#!/usr/bin/env python3
"""Fixture-repo harness for the run-feedback behavioural evals.

Builds a throwaway sandbox repo per (case, arm). Three properties make the eval
defensible rather than decorative:

1. SEEDED BY PRODUCTION CODE. The fixture ledger is created by running the real
   `collect` + `file` subcommands, never by hand-writing markdown. So the fixture is
   byte-identical to what production writes and the ground truth is objective by
   construction — zero author bias (advanced-eval-patterns.md §6). If the ledger format
   ever changes, the fixtures follow it automatically instead of silently rotting.

2. A LOGGING SHIM at the CLI path the skill tells agents to call. Every invocation is
   recorded with a content hash of docs/ and .agent/feedback/ taken immediately BEFORE
   and AFTER it. That hash chain is what lets the grader prove — with no LLM in the loop —
   that the ledger was mutated ONLY by the CLI and never by hand. A hand-edit shows up as
   a break between one call's post-hash and the next call's pre-hash (or after the last).

3. SINGLE-VARIABLE A/B (advanced-eval-patterns.md §7). with_skill keeps SKILL.md +
   references/ + examples/; without_skill deletes exactly those three and keeps everything
   else — same CLI, same assets, same fixture. Any delta is therefore attributable to the
   guidance layer, not to tool discovery.

No eval ever touches the real docs/KNOWN_ISSUES.md.

Usage:
    python3 harness.py build --case 1 --arm with_skill --dest /tmp/sbx-1-with
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVALS_DIR))
from _hashes import scope_hashes  # noqa: E402

SKILL_SRC = EVALS_DIR.parent
REAL_CLI = SKILL_SRC / "scripts" / "run_feedback.py"

# Scope definitions and the hash itself live in _hashes.py — imported by BOTH this harness
# and the instrumentation injected into the sandbox, so the before/after chain cannot drift.
# The agent's scratch files (body drafts, outputs/, .eval/) sit outside every scope, so
# drafting an issue body is never mistaken for a ledger edit.

# with_skill keeps these; without_skill does not. This is the ONLY difference between arms.
GUIDANCE_PATHS = ("SKILL.md", "references", "examples")

CONFIG = {
    "v": 1,
    "issues_dir": "docs/issues",
    "index_path": "docs/KNOWN_ISSUES.md",
    "backlog_path": "docs/BACKLOG.md",
    "backlog_anchor": "<!-- feedback:discovered-issues -->",
    "id_prefixes": {
        "_default": "FW",
        "transcript-fetcher": "TF",
        "agent-teams": "AT",
        "hooks": "HK",
        "skill-session-state": "SS",
        "skill-creator": "VAL",
        "vdd-multi": "VM",
        "docs": "DOC",
        "run-feedback": "RF",
        "session": "SES",
        # NOTE: `marp-slide` (case 16) is deliberately absent — it must fall back to the
        # _default prefix so the agent has to notice the missing prefix→category row.
    },
    "excerpt_max_chars": 2000,
    "feedback_dir": ".agent/feedback",
}

BACKLOG_MD = """# Backlog

Work items, ranked. Discovered issues from run retros land under the anchor below.

## Discovered Issues

<!-- feedback:discovered-issues -->
"""

# A live, human-ranked roadmap WITHOUT the feedback anchor — the fixture for the
# "repo already has a backlog under another name" case. The agent must point
# `backlog_path` here and seat the anchor, NOT create a second backlog file.
ROADMAP_MD = """# Roadmap

## Now
- [ ] Ship the importer rewrite (owner: @sergey)

## Next
- [ ] Consolidate the CLI flags across skills

## Discovered Issues

## Later
- [ ] Multi-vault sync
"""

# Seeded into EVERY case so the ledger is a realistic, non-empty index with real category
# sections — an agent filing into an empty repo is not the situation we mean to measure.
BASELINE_ISSUES = [
    {
        "id": "AT-1",
        "title": "No session resumption in agent teams",
        "category": "agent-teams",
        "severity": "SEV-3",
        "component": "agent-teams",
        "seed_spec": {
            "source": "workflow",
            "kind": "blocker",
            "component": "agent-teams",
            "message": "teams runtime does not resume a session after a reset",
        },
    },
    {
        "id": "HK-1",
        "title": "PostToolUse fires only on successful tool calls",
        "category": "hooks",
        "severity": "SEV-4",
        "component": "hooks",
        "seed_spec": {
            "source": "hook",
            "kind": "tool-error",
            "component": "hooks",
            "message": "posttooluse fires only on successful tool calls, so failures are never captured",
        },
    },
]

# Injected at the TOP of the sandbox's run_feedback.py — the file agents are told to call.
# Injection rather than a wrapper script on purpose: a wrapper has to keep the real
# implementation somewhere, and that file is then a bypass an inquisitive agent can call
# directly, escaping the log. Here there is exactly one CLI file and no way around it.
INSTRUMENT = '''# --- eval instrumentation (injected by evals/harness.py) ---
import atexit as _atexit, json as _j, os as _os, sys as _sys
from pathlib import Path as _P

_SBX = next(p for p in _P(__file__).resolve().parents if (p / ".eval").is_dir())
_sys.path.insert(0, str(_SBX / ".eval"))
import _hashes as _H   # the SAME module the grader imports — the chain cannot drift

_PRE = _H.scope_hashes(_SBX)
_ARGV = list(_sys.argv[1:])
_orig_exit = _sys.exit


def _tracked_exit(code=0):
    _sys._eval_code = code if isinstance(code, int) else (0 if code is None else 1)
    _orig_exit(code)


_sys.exit = _tracked_exit


@_atexit.register
def _eval_log():
    log = _SBX / ".eval" / "cli_log.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as fh:
        fh.write(_j.dumps({
            "argv": _ARGV,
            "cwd": _os.getcwd(),
            "exit": getattr(_sys, "_eval_code", 0),
            "pre": _PRE,
            "post": _H.scope_hashes(_SBX),
        }) + "\\n")
# --- end eval instrumentation ---
'''


def instrument(src: str) -> str:
    """Splice the logger into the CLI at a LEGAL insertion point.

    Not simply after the shebang: `from __future__ import annotations` must remain the first
    statement in the module, so code inserted above it is a SyntaxError and every CLI call
    dies. Insert after the last __future__ import (or, failing that, after the module
    docstring) and verify the result still compiles before handing it to an agent.
    """
    lines = src.splitlines(keepends=True)
    anchor = 0
    for i, line in enumerate(lines):
        if line.startswith("from __future__ import"):
            anchor = i + 1
    if anchor == 0:                                     # no __future__ import: clear the docstring
        tree = ast.parse(src)
        if (tree.body and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)):
            anchor = tree.body[0].end_lineno
        else:
            anchor = 1                                  # after the shebang
    out = "".join(lines[:anchor]) + "\n" + INSTRUMENT + "\n" + "".join(lines[anchor:])
    compile(out, "run_feedback.py", "exec")             # fail here, not inside an agent's session
    return out


def rf(dest: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run the REAL CLI against the sandbox (never the shim — seeding must not be logged)."""
    proc = subprocess.run(
        [sys.executable, str(REAL_CLI), "--repo-root", str(dest), *args],
        capture_output=True,
        text=True,
    )
    if check and proc.returncode != 0:
        raise SystemExit(
            f"harness: seeding command failed (exit {proc.returncode}): {' '.join(args)}\n"
            f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
        )
    return proc


def collect(dest: Path, spec: dict) -> dict:
    """Collect one finding via production code; return its {finding_id, fingerprint}."""
    args = [
        "collect",
        "--source", spec["source"],
        "--kind", spec["kind"],
        "--component", spec["component"],
        "--message", spec["message"],
        "--json",
    ]
    for flag, key in (
        ("--command", "command"),
        ("--workflow", "workflow"),
        ("--task-id", "task_id"),
        ("--phase", "phase"),
        ("--propose", "propose"),
        ("--severity", "severity"),
        ("--category", "category"),
    ):
        if spec.get(key):
            args += [flag, str(spec[key])]
    if spec.get("exit_code") is not None:
        args += ["--exit-code", str(spec["exit_code"])]

    out = json.loads(rf(dest, *args).stdout)
    finding = out.get("finding", out)
    return {"finding_id": finding["finding_id"], "fingerprint": finding["fingerprint"]}


def seed_issue(dest: Path, issue: dict, collect_specs: dict[str, dict]) -> None:
    """Create one ledger issue by collecting its source failure and filing it for real."""
    spec = issue.get("seed_spec") or collect_specs[issue["from_finding"]]
    ref = collect(dest, spec)

    body = (
        f"**Symptom.** {issue['title']}. "
        f"{issue.get('body_discriminator', 'Observed during a workflow run.')}\n\n"
        "**Reproduction.**\n\n"
        "```sh\n"
        "# seeded fixture issue\n"
        "python3 scripts/repro.py\n"
        "```\n\n"
        "**Workaround.** None.\n\n"
        "**Fix path.** See the owning component.\n"
    )
    body_file = dest / ".eval" / f"seed-{issue['id']}.md"
    body_file.parent.mkdir(parents=True, exist_ok=True)
    body_file.write_text(body)

    out = json.loads(rf(
        dest, "file",
        "--finding", ref["finding_id"],
        "--as", "defect",
        "--title", issue["title"],
        "--category", issue["category"],
        "--severity", issue["severity"],
        "--component", issue["component"],
        "--body-file", str(body_file),
        "--json",
    ).stdout)

    allocated = (out.get("result") or {}).get("issue_id")
    if allocated != issue["id"]:
        raise SystemExit(
            f"harness: fixture integrity failure — expected issue id {issue['id']}, "
            f"production allocated {allocated}. Fix CONFIG['id_prefixes'] or the seed."
        )


def count_index_lines(dest: Path) -> int:
    from _hashes import index_lines
    return len(index_lines(dest))


def count_backlog_bullets(dest: Path) -> int:
    path = dest / CONFIG["backlog_path"]
    if not path.exists():
        return 0
    text = path.read_text()
    anchor = CONFIG["backlog_anchor"]
    if anchor not in text:
        return 0
    return len(re.findall(r"(?m)^- ", text.split(anchor, 1)[1]))


def build(case: dict, arm: str, dest: Path) -> dict:
    seed = case.get("seed", {})
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
    (dest / "docs" / "issues").mkdir(parents=True)
    (dest / "outputs").mkdir()
    (dest / ".eval").mkdir()

    # Always seed a valid config first — the fixture ledger has to be written by production
    # code even for the cases whose *final* state is unconfigured or corrupt.
    (dest / "docs" / "feedback").mkdir(parents=True)
    (dest / "docs" / "feedback" / "config.json").write_text(json.dumps(CONFIG, indent=2))
    backlog = seed.get("backlog", True)
    if backlog == "roadmap":
        (dest / "docs" / "ROADMAP.md").write_text(ROADMAP_MD)
    elif backlog:
        (dest / "docs" / "BACKLOG.md").write_text(BACKLOG_MD)

    # Arbitrary fixture files a case needs in the sandbox (e.g. a build log the
    # agent is told to quote). Kept a plain {relpath: text} map so a case declares
    # its own fixtures instead of the harness growing a special case per scenario.
    for rel, text in (seed.get("files") or {}).items():
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    # --- skill copy, with the arm's single isolated variable applied -------------------
    skill_dst = dest / ".agent" / "skills" / "run-feedback"
    skill_dst.parent.mkdir(parents=True)
    shutil.copytree(
        SKILL_SRC, skill_dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "evals"),
    )
    # The CLI resolves the index seed template from its sibling skill; without it the
    # sandbox would report a spurious `seed_template_reachable: false`. Copied in BOTH arms,
    # so it is not part of the isolated variable.
    sibling = SKILL_SRC.parent / "known-issues-format"
    if sibling.is_dir():
        shutil.copytree(
            sibling, dest / ".agent" / "skills" / "known-issues-format",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "evals"),
        )
    if arm == "without_skill":
        for rel in GUIDANCE_PATHS:
            target = skill_dst / rel
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()

    # --- seed the ledger and the inbox (production code, in order) --------------------
    collect_specs = {c["ref"]: c for c in seed.get("collect", [])}

    for issue in BASELINE_ISSUES + seed.get("issues", []):
        seed_issue(dest, issue, collect_specs)

    # Live inbox findings come AFTER the issues. For a duplicate fixture the same failure
    # spec is collected again here: its first capture was consumed into the ledger, so this
    # one lands fresh in the inbox carrying an identical fingerprint — a genuine recurrence
    # of an already-filed issue, which is exactly the situation triage must catch.
    #
    # finding_id is `fnd-<UTC-second>-<fingerprint[:8]>`, so a recurrence collected within
    # the same second as its seed would be handed an IDENTICAL id — and the grader could no
    # longer tell the live finding from the consumed one. Wait out the second, then assert
    # the live ids really are distinct from everything already consumed.
    if any(i.get("from_finding") for i in seed.get("issues", [])):
        time.sleep(1.1)

    refs: dict[str, dict] = {}
    for spec in seed.get("collect", []):
        refs[spec["ref"]] = collect(dest, spec)

    consumed = {
        p.stem
        for sub in ("filed", "dismissed")
        for p in (dest / ".agent" / "feedback" / sub).glob("*.json")
    }
    for ref, info in refs.items():
        if info["finding_id"] in consumed:
            raise SystemExit(
                f"harness: fixture integrity failure — live finding {ref} "
                f"({info['finding_id']}) collides with an already-consumed finding of the "
                f"same id. The grader could not distinguish them."
            )

    if seed.get("claim_held_by"):
        rf(dest, "claim", "--run-id", seed["claim_held_by"])

    # --- final config state -----------------------------------------------------------
    cfg_mode = seed.get("config", "valid")
    if cfg_mode == "absent":
        # A repo that has an existing hand-maintained ledger but has never run the loop.
        shutil.rmtree(dest / "docs" / "feedback")
        shutil.rmtree(dest / ".agent" / "feedback", ignore_errors=True)
    elif cfg_mode == "broken":
        # Corrupt, not missing: `init` is create-only and will refuse to overwrite it, so
        # the agent cannot self-heal and must fall back on the non-blocking guarantee.
        (dest / "docs" / "feedback" / "config.json").write_text(
            '{"v": 1, "issues_dir": "docs/issues",,,\n  BROKEN — not valid JSON\n'
        )

    # --- instrument the CLI (after seeding, so seeding itself is not logged) -----------
    shutil.copy(EVALS_DIR / "_hashes.py", dest / ".eval" / "_hashes.py")
    cli = skill_dst / "scripts" / "run_feedback.py"
    cli.write_text(instrument(cli.read_text()))
    cli.chmod(0o755)
    (dest / ".eval" / "cli_log.jsonl").write_text("")

    state = {
        "case_id": case["id"],
        "case_name": case["name"],
        "arm": arm,
        "refs": refs,
        "initial_hashes": scope_hashes(dest),
        "baseline": {
            "issue_count": len(list((dest / "docs" / "issues").glob("*.md"))),
            "issue_ids": sorted(p.name for p in (dest / "docs" / "issues").glob("*.md")),
            "index_lines": count_index_lines(dest),
            "backlog_bullets": count_backlog_bullets(dest),
        },
        "config": CONFIG,
    }
    (dest / ".eval" / "state.json").write_text(json.dumps(state, indent=2))
    return state


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a run-feedback eval sandbox")
    ap.add_argument("action", choices=["build"])
    ap.add_argument("--case", type=int, required=True)
    ap.add_argument("--arm", choices=["with_skill", "without_skill"], required=True)
    ap.add_argument("--dest", type=Path, required=True)
    ap.add_argument("--evals", type=Path, default=EVALS_DIR / "evals.json")
    args = ap.parse_args()

    suite = json.loads(args.evals.read_text())
    case = next((e for e in suite["evals"] if e["id"] == args.case), None)
    if case is None:
        raise SystemExit(f"harness: no eval with id {args.case}")

    state = build(case, args.arm, args.dest.resolve())
    print(json.dumps(state, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
