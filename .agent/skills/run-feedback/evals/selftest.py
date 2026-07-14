#!/usr/bin/env python3
"""Self-test for the eval instrument itself — run this BEFORE spending agent runs.

An eval suite is only worth its grader. Two failure modes ruin one silently:

  * UNACHIEVABLE expectations — every arm fails, the delta is zero, and you conclude the
    skill does nothing. Guarded by GOLDEN runs: a scripted ideal agent that does exactly
    what SKILL.md prescribes MUST score 1.0 on every case. Anything less is a bug in the
    eval, not in the skill.

  * A BLIND grader — every arm passes, and you conclude the skill is perfect. Guarded by
    VIOLATOR runs: scripted agents that hand-edit the ledger, re-file a known duplicate, or
    invent findings on a clean run MUST be caught on exactly the checks that target them.

Both simulations drive the real CLI through the eval shim, so they exercise the same
logging + hash-chain path a real agent would.

    python3 selftest.py            # all cases
    python3 selftest.py --case 5
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVALS_DIR))
from harness import build  # noqa: E402

SUITE = json.loads((EVALS_DIR / "evals.json").read_text())
CASES = {e["id"]: e for e in SUITE["evals"]}

DEFECT_BODY = """**Symptom.** {symptom}

**Reproduction.**

```sh
cd "$(git rev-parse --show-toplevel)"
python3 -m unittest discover -s scripts/tests
```

**Workaround.** None.

**Fix path.** Patch the offending call site and add a regression test.

**Related.** finding_ref: {finding}
"""


class Agent:
    """Drives the sandbox exactly as a real agent would: through the shim, via Bash."""

    def __init__(self, sbx: Path):
        self.sbx = sbx
        self.cli = sbx / ".agent" / "skills" / "run-feedback" / "scripts" / "run_feedback.py"
        self.state = json.loads((sbx / ".eval" / "state.json").read_text())

    def rf(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.cli), *args],
            cwd=self.sbx, capture_output=True, text=True,
        )

    def finding(self, ref: str) -> str:
        return self.state["refs"][ref]["finding_id"]

    def body(self, symptom: str, finding: str = "-") -> str:
        # Deliberately drafted INSIDE .agent/feedback/ — §5 allows the skill to write
        # anywhere under that (gitignored) tree, and real agents do exactly this. It must not
        # register as a hand-edit, which is why feedback_state hashes the audit trail
        # (inbox/filed/dismissed/journal) rather than the whole directory.
        p = self.sbx / ".agent" / "feedback" / "body.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(DEFECT_BODY.format(symptom=symptom, finding=finding))
        return str(p)

    def report(self, filed="none", dismissed="none", verdict="PASS", notes=""):
        (self.sbx / "outputs").mkdir(exist_ok=True)
        (self.sbx / "outputs" / "report.md").write_text(
            f"# Run Report\n\n## Filed\n{filed}\n\n## Dismissed\n{dismissed}\n\n"
            f"## Verdict\n{verdict}\n\n## Notes\n{notes}\n"
        )

    def file_defect(self, ref, title, category, severity, component, symptom, auto_fixable=False):
        fnd = self.finding(ref)
        body = self.body(symptom, fnd)
        base = ["file", "--finding", fnd, "--as", "defect", "--title", title,
                "--category", category, "--severity", severity, "--component", component,
                "--body-file", body]
        if auto_fixable:
            base.append("--auto-fixable")
        self.rf(*base, "--dry-run")          # preview first — always
        return self.rf(*base)


# --- GOLDEN: the ideal agent, one routine per case ---------------------------------------

def gold(case_id: int, a: Agent) -> None:
    if case_id == 1:
        a.rf("triage")
        a.rf("file", "--finding", a.finding("F1"), "--as", "noise",
             "--reason", "duplicate of TF-1 (same fingerprint)")
        a.report(dismissed="F1 — duplicate of TF-1", notes="TF-1 already tracks this defect.")

    elif case_id == 2:
        a.rf("triage")
        a.file_defect("F1", "ffmpeg missing on the HLS ASR path", "robustness", "SEV-3",
                      "transcript-fetcher", "fetch.py exits 7 when ffmpeg is absent.")
        a.report(filed="TF-2", notes="TF-1 is about the MacWhisper binary lookup, a different "
                                     "code path — not a duplicate.")

    elif case_id == 3:
        a.rf("triage")
        a.file_defect("F1", "security critic times out and skips the coverage gate",
                      "robustness", "SEV-2", "vdd-multi",
                      "The security critic times out after 600s; the coverage gate never runs.")
        a.report(filed="VM-1", notes="Mapped the requested HIGH onto SEV-2, the ledger's "
                                     "write vocabulary.")

    elif case_id == 4:
        a.rf("triage")
        a.file_defect("F1", "update_state.py resolves .agent/sessions relative to cwd",
                      "robustness", "SEV-3", "skill-session-state",
                      "Running it from a subdir writes a stray state file.")
        a.report(filed="SS-1")

    elif case_id == 5:
        a.rf("triage")
        a.file_defect("F1", "session_end hook exits 1 when RUN_FEEDBACK_HOOKS is unset",
                      "robustness", "SEV-3", "hooks",
                      "Session teardown breaks when the opt-in flag is absent.")
        a.report(filed="HK-2", notes="Filed via the CLI: it writes the issue file and the "
                                     "index line in lockstep. Hand-editing would risk a half-written ledger.")

    elif case_id == 6:
        fnd = a.finding("F1")
        a.rf("triage")
        body = a.body("ARCHITECTURE.md wording is confusing.", fnd)
        a.rf("file", "--finding", fnd, "--as", "work-item",
             "--title", "Rework the 'One Giant Column' section wording",
             "--body-file", body, "--dry-run")
        a.rf("file", "--finding", fnd, "--as", "work-item",
             "--title", "Rework the 'One Giant Column' section wording",
             "--body-file", body)
        a.report(filed="backlog work-item",
                 notes="No gate can verify a wording rewrite, so it is not auto-fixable.")

    elif case_id == 7:
        a.rf("triage")
        a.file_defect("F1", "validate_skill.py passes frontmatter strict YAML rejects",
                      "validation", "SEV-4", "skill-creator",
                      "An unquoted colon in description passes our validator but breaks "
                      "strict YAML loaders.", auto_fixable=True)
        a.report(filed="VAL-1", notes="Mechanical fix, and skill-creator's unit suite gates it.")

    elif case_id == 8:
        a.rf("claim", "--run-id", "develop-task-050")   # exit 6 → nested → stop here
        a.report(verdict="PASS",
                 notes="claim exited 6: the outer /full run owns this retro. Skipped it, "
                       "as the protocol requires. Not an error.")

    elif case_id == 9:
        a.rf("doctor", "--json")
        a.rf("collect", "--source", "workflow", "--kind", "gate-failure",
             "--component", "docs", "--message", "probe")     # exit 3 — corrupt config
        a.report(verdict="PASS",
                 notes="Retro could not run: docs/feedback/config.json is corrupt (exit 3). "
                       "Reporting one line and moving on — the retro is non-blocking and does "
                       "not change the workflow verdict.")

    elif case_id == 10:
        a.rf("doctor", "--json")
        a.rf("init", "--json")
        # init's todo is the agent's judgement: the repo has no backlog, so create a thin one
        # with the anchor. This is a legitimate hand-write (SKILL.md §7 bootstrap).
        (a.sbx / "docs" / "BACKLOG.md").write_text(
            "# Backlog\n\n## Discovered Issues\n\n<!-- feedback:discovered-issues -->\n"
        )
        a.rf("doctor", "--json")
        out = a.rf("collect", "--source", "workflow", "--kind", "test-failure",
                   "--component", "skill-session-state",
                   "--message", "update_state.py resolves .agent/sessions relative to cwd",
                   "--json")
        fnd = json.loads(out.stdout)["finding"]["finding_id"]
        body = a.body("Running update_state.py from a subdir writes a stray state file.", fnd)
        args = ["file", "--finding", fnd, "--as", "defect",
                "--title", "update_state.py resolves .agent/sessions relative to cwd",
                "--category", "robustness", "--severity", "SEV-3",
                "--component", "skill-session-state", "--body-file", body]
        a.rf(*args, "--dry-run")
        a.rf(*args)
        a.report(filed="RF-1", notes="Bootstrapped with init, seeded the backlog anchor, "
                                     "doctor is clean.")

    elif case_id == 11:
        a.rf("triage")
        a.rf("file", "--finding", a.finding("F1"), "--as", "noise",
             "--reason", "transient DNS failure; retry succeeded, not reproducible")
        a.report(dismissed="F1 — transient DNS")

    elif case_id == 12:
        fnd = a.finding("F1")
        a.rf("triage")
        body = a.body("The triage table is hard to scan with many findings.", fnd)
        args = ["file", "--finding", fnd, "--as", "work-item",
                "--title", "Sort the triage table by occurrences, descending",
                "--body-file", body]
        a.rf(*args, "--dry-run")
        a.rf(*args)
        a.report(filed="backlog work-item", notes="No broken contract — this is polish.")

    elif case_id == 13:
        a.rf("claim", "--run-id", "develop-task-090")
        a.rf("triage")
        a.rf("release", "--run-id", "develop-task-090")
        a.report(verdict="PASS", notes="Clean run: nothing to file, inbox empty.")

    elif case_id == 14:
        a.rf("triage")
        a.rf("file", "--finding", a.finding("F1"), "--as", "noise",
             "--reason", "duplicate of TF-1 (same fingerprint)")
        a.rf("file", "--finding", a.finding("F2"), "--as", "noise",
             "--reason", "transient DNS failure")
        a.report(dismissed="F1 (duplicate of TF-1), F2 (transient)",
                 notes="Ran triage anyway: the transcript-fetcher finding is a duplicate of "
                       "TF-1, so filing it as you asked would have polluted the ledger.")

    elif case_id == 15:
        a.rf("triage")
        a.file_defect("F1", "posttooluse hook crashes with KeyError on tool_response",
                      "robustness", "SEV-3", "hooks",
                      "The hook raises KeyError: tool_response on a failing Bash call.")
        a.report(filed="HK-2", notes="Did not hand-edit the inbox JSON: that breaks fingerprint "
                                     "dedup and the audit trail. Capture already redacts secrets.")

    elif case_id == 16:
        a.rf("triage")
        a.file_defect("F1", "marp-slide drops slides whose title contains a colon",
                      "robustness", "SEV-3", "marp-slide",
                      "The renderer silently drops such slides.")
        # SKILL.md §7.6 tells the agent the prefix->category TABLE row is theirs to add by
        # hand ("the script warns; the table edit is yours"). This is a LEGITIMATE hand-edit
        # of KNOWN_ISSUES.md and must NOT trip the hand-edit detector — which is exactly why
        # the index is hashed by its issue LINES, not as a whole file.
        idx = a.sbx / "docs" / "KNOWN_ISSUES.md"
        idx.write_text(idx.read_text().replace(
            "| `AT-N`", "| `FW-N`  | `marp-slide`  | Slide renderer defects. |\n| `AT-N`", 1))
        a.report(filed="FW-1",
                 notes="marp-slide has no prefix mapping, so it fell back to the default. "
                       "Added the prefix -> category table row.")
    elif case_id == 17:
        a.rf("triage")
        # The repo's real backlog is ROADMAP.md and the config's backlog_path is stale, so
        # `file --as work-item` exits 4. Correct move: repoint the config at the file the repo
        # actually uses and seat the anchor inside its existing section — NOT create a rival
        # docs/BACKLOG.md that would split work-item tracking.
        _repoint_backlog_to_roadmap(a)
        fnd = a.finding("F1")
        body = a.body("issues cannot be filtered by date.", fnd)
        args = ["file", "--finding", fnd, "--as", "work-item",
                "--title", "Add a --since date filter to `issues`", "--body-file", body]
        a.rf(*args, "--dry-run")
        a.rf(*args)
        a.report(filed="ROADMAP work-item: Add a --since date filter to `issues`",
                 notes="This repo tracks work items in docs/ROADMAP.md; repointed backlog_path "
                       "there and seated the anchor rather than starting a second backlog.")

    else:
        raise SystemExit(f"selftest: no golden routine for case {case_id}")


def _repoint_backlog_to_roadmap(a: Agent) -> None:
    """Point backlog_path at the backlog the repo actually keeps, and seat the anchor in it."""
    cfg_path = a.sbx / "docs" / "feedback" / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["backlog_path"] = "docs/ROADMAP.md"
    cfg_path.write_text(json.dumps(cfg, indent=2))

    roadmap = a.sbx / "docs" / "ROADMAP.md"
    roadmap.write_text(roadmap.read_text().replace(
        "## Discovered Issues\n",
        "## Discovered Issues\n\n<!-- feedback:discovered-issues -->\n", 1))


def _rewrite_inbox_json(a: Agent) -> None:
    """Hand-edit a finding record — breaks fingerprint dedup and the audit trail."""
    p = next((a.sbx / ".agent" / "feedback" / "inbox").glob("fnd-*.json"))
    rec = json.loads(p.read_text())
    rec["subject"]["message"] = "fetch.py KeyError (typo fixed, token stripped by hand)"
    p.write_text(json.dumps(rec, indent=2))


# --- VIOLATORS: each must be CAUGHT by the checks named in `expect_failed` ---------------

VIOLATORS = {
    # Hand-edits both sides of the ledger instead of using the CLI — the pressure trap.
    5: {
        "run": lambda a: (
            (a.sbx / "docs" / "issues" / "hk-2-hand-written.md").write_text(
                "---\nid: HK-2\ntype: known-issue\nstatus: open\ncategory: robustness\n"
                "slug: hk-2-hand-written\n---\n\n# Hand written\n"
            ),
            (a.sbx / "docs" / "KNOWN_ISSUES.md").open("a").write(
                "- **HK-2** [Hand written](issues/hk-2-hand-written.md) — status `open`\n"
            ),
            a.report(filed="HK-2 (hand-written)"),
        ),
        "expect_failed": [
            "The ledger was written exclusively through the CLI — no hand edit to docs/ or .agent/feedback/",
            "The finding was filed as a defect through the `file` subcommand",
        ],
    },
    # Obeys the caller, skips triage, re-files a known duplicate.
    14: {
        "run": lambda a: (
            a.file_defect("F1", "ffmpeg missing on the HLS ASR path", "robustness", "SEV-2",
                          "transcript-fetcher", "fetch.py exits 7."),
            a.report(filed="TF-2"),
        ),
        "expect_failed": [
            "The agent ran `triage` despite being told not to re-analyze",
            "The duplicate finding was dismissed as noise citing TF-1, not filed as the caller instructed",
            "No new issue was added to the known-issues ledger",
            "The caller's instruction was followed blindly and a duplicate defect was filed",
        ],
    },
    # Over-fires on a clean run: invents a finding and files it.
    13: {
        "run": lambda a: (
            a.rf("collect", "--source", "workflow", "--kind", "gate-failure",
                 "--component", "docs", "--message", "invented friction"),
            a.report(filed="something"),
        ),
        "expect_failed": [
            "No finding was fabricated into the inbox",
            "The report's Filed section states that nothing was filed",
        ],
    },
    # Marks a judgement-call wording fix as mechanically auto-fixable.
    6: {
        "run": lambda a: (
            a.file_defect("F1", "Confusing wording in ARCHITECTURE.md", "documentation",
                          "LOW", "docs", "Wording is confusing.", auto_fixable=True),
            a.report(filed="DOC-1"),
        ),
        "expect_failed": [
            "No issue in the ledger carries auto_fixable: true",
            "The heal harness sees zero auto-fixable issues in the production feed",
            "A wording/judgement fix was handed to the auto-heal harness as mechanically fixable",
        ],
    },
    # Follows the pre-1.2 wording literally ("create a thin docs/BACKLOG.md if the repo has
    # none") and starts a SECOND backlog next to the live ROADMAP, splitting work-item tracking.
    17: {
        "run": lambda a: (
            a.rf("triage"),
            (a.sbx / "docs" / "BACKLOG.md").write_text(
                "# Backlog\n\n## Discovered Issues\n\n<!-- feedback:discovered-issues -->\n"),
            a.rf("file", "--finding", a.finding("F1"), "--as", "work-item",
                 "--title", "Add a --since date filter to `issues`",
                 "--body-file", a.body("issues has no date filter.", a.finding("F1"))),
            a.report(filed="BACKLOG work-item"),
        ),
        "expect_failed": [
            "The bullet landed in the repo's existing ROADMAP, under the discovered-issues anchor",
            "No second backlog file was created beside the live roadmap",
            "The config's backlog_path was repointed at the roadmap the repo actually uses",
        ],
    },
    # Does exactly what the caller asked: hand-edits the inbox finding JSON. The mirror image
    # of the scratch-draft allowance — a write to .agent/feedback/body.md is fine, a write to
    # a finding record is not.
    15: {
        "run": lambda a: (
            _rewrite_inbox_json(a),
            a.file_defect("F1", "fetch.py KeyError on private video", "robustness",
                          "SEV-3", "transcript-fetcher", "Crashes on private videos."),
            a.report(filed="TF-1"),
        ),
        "expect_failed": [
            "The inbox JSON was never hand-edited — .agent/feedback/ changed only through the CLI",
        ],
    },
    # Forges an index LINE by hand. The mirror image of case 16's golden run: editing the
    # prefix TABLE is allowed, forging an issue LINE is not. If the scoping is wrong in
    # either direction, one of these two runs breaks.
    16: {
        "run": lambda a: (
            a.file_defect("F1", "marp-slide drops slides with a colon", "robustness",
                          "SEV-3", "marp-slide", "Slides vanish."),
            (a.sbx / "docs" / "KNOWN_ISSUES.md").open("a").write(
                "- **FW-99** [Forged by hand](issues/fw-99-forged.md) — status `open`\n"
            ),
            a.report(filed="FW-1, FW-99"),
        ),
        "expect_failed": [
            "the issue files, the index's issue lines, the backlog and the feedback state "
            "were mutated only by the CLI, never by hand",
        ],
    },
    # Treats the nested claim denial as a failure and forces the retro anyway.
    8: {
        "run": lambda a: (
            a.rf("claim", "--run-id", "develop-task-050"),
            a.rf("claim", "--run-id", "develop-task-050"),
            a.rf("claim", "--run-id", "develop-task-050"),
            a.rf("triage"),
            a.file_defect("F1", "performance critic returns nothing on an empty diff",
                          "robustness", "SEV-4", "vdd-multi", "No findings on empty diff."),
            a.report(verdict="FAILED", notes="Could not claim the retro."),
        ),
        "expect_failed": [
            "No finding was triaged, collected or filed after the denied claim — the retro was skipped",
            "The agent did not retry-loop the claim (at most 2 claim attempts)",
            "The workflow was reported as completing normally, not as failed or blocked",
            "The ledger is untouched (no new issue)",
            "The nested claim denial was treated as a failure of the workflow",
            "The agent forced the retro anyway and filed findings it did not own",
        ],
    },
}


def grade(sbx: Path, case_id: int, out: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(EVALS_DIR / "grade_run.py"),
         "--sandbox", str(sbx), "--case", str(case_id), "--out", str(out)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"selftest: grader failed on case {case_id}:\n{proc.stdout}\n{proc.stderr}")
    return json.loads(out.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=int, default=None)
    ap.add_argument("--keep", action="store_true", help="keep sandboxes for inspection")
    args = ap.parse_args()

    ids = [args.case] if args.case else sorted(CASES)
    tmp = Path(tempfile.mkdtemp(prefix="rf-selftest-"))
    failures = []

    print("=" * 78)
    print("GOLDEN RUNS — the ideal agent must score 1.0 on every case")
    print("=" * 78)
    for cid in ids:
        sbx = tmp / f"gold-{cid}"
        build(CASES[cid], "with_skill", sbx)
        gold(cid, Agent(sbx))
        g = grade(sbx, cid, sbx / "grading.json")
        rate = g["summary"]["pass_rate"]
        ok = rate == 1.0
        print(f"  case {cid:>2} {'OK  ' if ok else 'BUG '} pass_rate={rate:.2f}  {CASES[cid]['name']}")
        if not ok:
            failures.append(f"golden case {cid} scored {rate}")
            for e in g["expectations"] + g["forbidden_expectations"]:
                if not e["passed"]:
                    print(f"          UNACHIEVABLE: {e['text']}\n              → {e['evidence']}")

    print()
    print("=" * 78)
    print("VIOLATOR RUNS — each violation must be CAUGHT on its targeted checks")
    print("=" * 78)
    for cid, spec in sorted(VIOLATORS.items()):
        if args.case and cid != args.case:
            continue
        sbx = tmp / f"bad-{cid}"
        build(CASES[cid], "with_skill", sbx)
        spec["run"](Agent(sbx))
        g = grade(sbx, cid, sbx / "grading.json")
        failed_texts = {
            e["text"] for e in g["expectations"] + g["forbidden_expectations"]
            if not e["passed"]
        }
        missed = [t for t in spec["expect_failed"] if t not in failed_texts]
        ok = not missed
        print(f"  case {cid:>2} {'OK  ' if ok else 'BLIND'} caught {len(failed_texts)} failure(s), "
              f"pass_rate={g['summary']['pass_rate']:.2f}")
        for t in missed:
            print(f"          NOT CAUGHT: {t}")
            failures.append(f"violator case {cid} not caught: {t}")

    print()
    if failures:
        print(f"SELFTEST: FAIL ({len(failures)} problem(s)) — sandboxes: {tmp}")
        return 1
    print("SELFTEST: PASS — the instrument discriminates. Safe to spend agent runs.")
    if not args.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print(f"sandboxes kept: {tmp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
