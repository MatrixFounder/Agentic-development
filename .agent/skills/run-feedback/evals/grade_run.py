#!/usr/bin/env python3
"""Deterministic script-grader for the run-feedback behavioural evals.

A pure function of (sandbox final state, CLI log, evals.json) → grading.json. No LLM, no
network, no `eval`/`exec`/shell. The same inputs always produce the same report, which is
what makes the numbers pinnable (advanced-eval-patterns.md §1, §3) and costs zero grader
tokens.

Two rules keep it honest:

  * CALL THE GATE, DON'T COPY IT (§2). Whether the ledger is well-formed is decided by
    running the production feed — `run_feedback.py issues --json` and `doctor --json`, the
    same commands /heal-issues consumes — not by re-implementing their parsing here. A
    re-implementation would drift from production and go on lying green.

  * ALIGNMENT. checks[] must be 1:1 and same-order with expectations[] (likewise
    forbidden_*). A mismatch exits 2 rather than grading, so a human-readable expectation
    can never silently detach from the machine check that supposedly verifies it.

Forbidden checks invert: `passed: true` means the forbidden outcome did NOT happen. They
count toward the summary, so over-firing lowers the pass rate instead of being free.

Usage:
    python3 grade_run.py --sandbox /tmp/sbx-1-with --case 1 --out /path/grading.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _hashes import DEFAULT_SCOPES, scope_hashes  # noqa: E402
from harness import SKILL_SRC  # noqa: E402

EVALS_DIR = Path(__file__).resolve().parent
PROD_CLI = SKILL_SRC / "scripts" / "run_feedback.py"

SEVERITY_VOCAB = {"SEV-2", "SEV-3", "SEV-4", "LOW"}
ALL_SCOPES = DEFAULT_SCOPES

# The index seeded from the known-issues-format template carries a FORMAT EXAMPLE line
# (`- **<ID>** [<title>](issues/<slug>.md) — severity `<SEV>`...`). It is documentation, not
# an issue: excluded from every index-line count and vocabulary scan, or the placeholder
# `<SEV>` would read as a vocabulary violation and the counts would be off by one.
PLACEHOLDER = re.compile(r"<(ID|title|slug|SEV|status|YYYY-MM-DD)>")
INDEX_LINE = re.compile(r"(?m)^- \*\*")


SUBCOMMANDS = {"collect", "triage", "file", "journal", "issues",
               "claim", "release", "mine", "init", "doctor"}


def _norm_argv(argv: list[str]) -> list[str]:
    out = []
    for a in argv:
        if a.startswith("--") and "=" in a:
            flag, _, val = a.partition("=")
            out += [flag, val]
        else:
            out.append(a)
    return out


def _subcommand(argv: list[str]) -> str | None:
    """The real subcommand, not 'first non-dash token'. Global flags take values
    (`--config /tmp/x.json doctor`), and a naive positional parse reads the flag's VALUE as
    the subcommand — which once counted ten `--config <path>` calls as a runaway retry-loop
    of a subcommand named after a temp file."""
    return next((a for a in argv if a in SUBCOMMANDS), None)


class Ctx:
    """Everything a check can look at. Read-only; captured before any gate call."""

    def __init__(self, sandbox: Path):
        self.sandbox = sandbox
        self.state = json.loads((sandbox / ".eval" / "state.json").read_text())
        self.cfg = self.state["config"]
        self.baseline = self.state["baseline"]
        self.refs = self.state["refs"]

        log_path = sandbox / ".eval" / "cli_log.jsonl"
        self.log = [
            json.loads(ln) for ln in log_path.read_text().splitlines() if ln.strip()
        ] if log_path.exists() else []
        # `--finding=fnd-x` and `--finding fnd-x` are the same call; normalise so a check
        # cannot be dodged (or mis-scored) by the equals form.
        for call in self.log:
            call["argv"] = _norm_argv(call["argv"])

        # Snapshot hashes BEFORE running any production-gate command, so a gate call can
        # never be mistaken for a mutation.
        self.final_hashes = scope_hashes(sandbox)

        self.issues_dir = sandbox / self.cfg["issues_dir"]
        self.index_path = sandbox / self.cfg["index_path"]
        self.backlog_path = sandbox / self.cfg["backlog_path"]

        self.current_issue_files = sorted(
            p.name for p in self.issues_dir.glob("*.md")
        ) if self.issues_dir.is_dir() else []
        self.new_issue_files = [
            f for f in self.current_issue_files if f not in self.baseline["issue_ids"]
        ]

        self.report = ""
        report_path = sandbox / "outputs" / "report.md"
        if report_path.exists():
            self.report = report_path.read_text()

        self._gates: dict = {}

    # --- production gate (called, never re-implemented) -------------------------------
    def gate(self, *args: str):
        key = " ".join(args)
        if key not in self._gates:
            proc = subprocess.run(
                [sys.executable, str(PROD_CLI), "--repo-root", str(self.sandbox), *args],
                capture_output=True, text=True,
            )
            try:
                payload = json.loads(proc.stdout)
            except json.JSONDecodeError:
                payload = None
            self._gates[key] = (proc.returncode, payload)
        return self._gates[key]

    # --- helpers ----------------------------------------------------------------------
    def index_lines(self) -> list[str]:
        from _hashes import index_lines
        return index_lines(self.sandbox)

    def backlog_bullets(self) -> int:
        if not self.backlog_path.exists():
            return 0
        text = self.backlog_path.read_text()
        anchor = self.cfg["backlog_anchor"]
        if anchor not in text:
            return 0
        return len(re.findall(r"(?m)^- ", text.split(anchor, 1)[1]))

    def ledger_text(self, scope: str = "both") -> str:
        parts = []
        if scope in ("both", "issues"):
            parts += [p.read_text() for p in sorted(self.issues_dir.glob("*.md"))] \
                if self.issues_dir.is_dir() else []
        if scope in ("both", "index") and self.index_path.exists():
            parts.append(self.index_path.read_text())
        return "\n".join(parts)

    def frontmatter(self, issue_file: str) -> dict:
        text = (self.issues_dir / issue_file).read_text()
        m = re.match(r"(?s)\A---\n(.*?)\n---", text)
        if not m:
            return {}
        out = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
        return out

    def body(self, issue_file: str) -> str:
        text = (self.issues_dir / issue_file).read_text()
        return re.sub(r"(?s)\A---\n.*?\n---\n", "", text)

    def finding_record(self, ref: str) -> tuple[str | None, dict | None]:
        fid = self.refs.get(ref, {}).get("finding_id")
        if not fid:
            return None, None
        for status in ("filed", "dismissed", "inbox"):
            p = self.sandbox / ".agent" / "feedback" / status / f"{fid}.json"
            if p.exists():
                return status, json.loads(p.read_text())
        return None, None

    def calls(self, subcommand: str | None = None, args_all=None, not_args=None) -> list[dict]:
        out = []
        for c in self.log:
            argv = c["argv"]
            if subcommand and _subcommand(argv) != subcommand:
                continue
            if args_all and not all(a in argv for a in args_all):
                continue
            if not_args and any(a in argv for a in not_args):
                continue
            out.append(c)
        return out


# ---------------------------------------------------------------------------------------
# Checks. Each returns (bool, evidence). `bool` is the literal truth of the statement;
# forbidden checks are inverted by the caller.
# ---------------------------------------------------------------------------------------

def chk_cli_called(ctx, c):
    hits = ctx.calls(c["subcommand"], c.get("args_all"), c.get("not_args"))
    n = len(hits)
    return n >= c.get("min", 1), f"{n} matching `{c['subcommand']}` call(s)"


def chk_cli_not_called(ctx, c):
    hits = ctx.calls(c["subcommand"], c.get("args_all"), c.get("not_args"))
    return len(hits) == 0, f"{len(hits)} `{c['subcommand']}` call(s) (expected none)"


def chk_cli_exit(ctx, c):
    hits = [h for h in ctx.calls(c["subcommand"]) if h["exit"] == c["exit"]]
    return len(hits) >= c.get("min", 1), (
        f"{len(hits)} `{c['subcommand']}` call(s) exited {c['exit']}; "
        f"exits seen: {[h['exit'] for h in ctx.calls(c['subcommand'])]}"
    )


def chk_cli_call_count(ctx, c):
    n = len(ctx.calls(c["subcommand"]))
    return n <= c["max"], f"{n} `{c['subcommand']}` call(s), max {c['max']}"


def chk_max_calls_per_subcommand(ctx, c):
    counts: dict[str, int] = {}
    for call in ctx.log:
        sub = _subcommand(call["argv"])
        if sub:
            counts[sub] = counts.get(sub, 0) + 1
    worst = max(counts.values()) if counts else 0
    return worst <= c["max"], f"max calls of any one subcommand: {worst} ({counts})"


def _matches(call, spec) -> bool:
    argv = call["argv"]
    if spec.get("subcommand") and _subcommand(argv) != spec["subcommand"]:
        return False
    if spec.get("args_all") and not all(a in argv for a in spec["args_all"]):
        return False
    if spec.get("not_args") and any(a in argv for a in spec["not_args"]):
        return False
    return True


def chk_cli_order(ctx, c):
    first_i = next((i for i, call in enumerate(ctx.log) if _matches(call, c["first"])), None)
    if first_i is None:
        return False, f"no call matching {c['first']}"
    second_i = next(
        (i for i, call in enumerate(ctx.log) if i > first_i and _matches(call, c["second"])),
        None,
    )
    ok = second_i is not None
    return ok, (
        f"{c['first'].get('subcommand')} at #{first_i}, "
        f"{c['second'].get('subcommand')} after it: "
        f"{'#' + str(second_i) if ok else 'never'}"
    )


def chk_dry_run_precedes_file(ctx, c):
    """Every real `file --as defect|work-item` must be preceded by a dry-run of the SAME
    finding. A dry-run of some other finding proves nothing about this one.

    A real filing must actually name a finding and a ledger: `file --help` is a `file`
    invocation with neither, and counting it as an un-previewed filing failed agents who had
    in fact dry-run correctly and merely read the usage text first.
    """
    real = [
        call for call in ctx.log
        if _matches(call, {"subcommand": "file", "not_args": ["--dry-run", "--help", "-h"]})
        and "--finding" in call["argv"]
        and any(a in call["argv"] for a in ("defect", "work-item"))
    ]
    if not real:
        return False, "no real filing happened at all"
    for call in real:
        argv = call["argv"]
        finding = argv[argv.index("--finding") + 1] if "--finding" in argv else None
        idx = ctx.log.index(call)
        preceded = any(
            _matches(prev, {"subcommand": "file", "args_all": ["--dry-run"]})
            and finding is not None and finding in prev["argv"]
            for prev in ctx.log[:idx]
        )
        if not preceded:
            return False, f"real filing of {finding} had no preceding dry-run for it"
    return True, f"all {len(real)} real filing(s) were dry-run first"


def chk_no_cli_after_denied_claim(ctx, c):
    denied = next(
        (i for i, call in enumerate(ctx.log)
         if _matches(call, {"subcommand": "claim"}) and call["exit"] == 6),
        None,
    )
    if denied is None:
        return False, "claim was never denied (exit 6) — precondition absent"
    after = [
        call for call in ctx.log[denied + 1:]
        if any(_matches(call, {"subcommand": s}) for s in c["subcommands"])
    ]
    names = [[a for a in x["argv"] if not a.startswith("-")][:1] for x in after]
    return len(after) == 0, f"{len(after)} forbidden call(s) after the denied claim: {names}"


def chk_no_manual_mutation(ctx, c):
    """Replay the hash chain. A gap between one call's post-hash and the next call's
    pre-hash — or between the last call and the final state — is a mutation the CLI did not
    make, i.e. a hand-edit."""
    scopes = c.get("scopes", ALL_SCOPES)
    initial = ctx.state["initial_hashes"]
    violations = []
    for scope in scopes:
        expected = initial[scope]
        for i, call in enumerate(ctx.log):
            if call["pre"][scope] != expected:
                violations.append(f"{scope} changed outside the CLI before call #{i}")
                break
            expected = call["post"][scope]
        else:
            if ctx.final_hashes[scope] != expected:
                violations.append(f"{scope} changed after the last CLI call")
    return not violations, "; ".join(violations) if violations else \
        f"hash chain intact across {scopes} ({len(ctx.log)} CLI calls)"


def _delta_ok(c, actual):
    if "equals" in c:
        return actual == c["equals"]
    if "min" in c:
        return actual >= c["min"]
    if "max" in c:
        return actual <= c["max"]
    raise ValueError(f"delta check needs equals/min/max: {c}")


def chk_issue_count_delta(ctx, c):
    actual = len(ctx.current_issue_files) - ctx.baseline["issue_count"]
    return _delta_ok(c, actual), (
        f"issue count {ctx.baseline['issue_count']} → {len(ctx.current_issue_files)} "
        f"(delta {actual}); new: {ctx.new_issue_files}"
    )


def chk_index_line_delta(ctx, c):
    base = ctx.baseline["index_lines"]
    current = len(ctx.index_lines())
    actual = current - base
    return _delta_ok(c, actual), f"index lines {base} → {current} (delta {actual})"


def chk_backlog_bullet_delta(ctx, c):
    actual = ctx.backlog_bullets() - ctx.baseline["backlog_bullets"]
    return _delta_ok(c, actual), (
        f"backlog bullets {ctx.baseline['backlog_bullets']} → {ctx.backlog_bullets()} "
        f"(delta {actual})"
    )


def chk_issue_field(ctx, c):
    if c.get("scope", "new") == "new":
        files = ctx.new_issue_files
    else:
        files = ctx.current_issue_files
    if not files:
        return False, "no new issue file to inspect"
    results = []
    for f in files:
        fm = ctx.frontmatter(f)
        val = fm.get(c["field"])
        if "equals" in c:
            ok = str(val).lower() == str(c["equals"]).lower()
        else:
            ok = val in c["in"]
        results.append((ok, f"{f}: {c['field']}={val!r}"))
    passed = all(r[0] for r in results)
    return passed, "; ".join(r[1] for r in results)


def chk_index_severity_vocab(ctx, c):
    bad = []
    for line in ctx.index_lines():
        m = re.search(r"severity `([^`]+)`", line)
        if m and m.group(1) not in SEVERITY_VOCAB:
            bad.append(m.group(1))
    return not bad, f"out-of-vocabulary severities: {bad}" if bad else \
        f"all {len(ctx.index_lines())} index line(s) use the write vocabulary"


def chk_ledger_contains(ctx, c):
    expect = c.get("expect", True)
    text = ctx.ledger_text(c.get("scope", "both"))
    found = bool(re.search(c["regex"], text))
    return found == expect, f"pattern {'found' if found else 'not found'} (expected {expect})"


def _sections(body: str) -> dict[str, str]:
    """Split a markdown body into sections, FENCE-AWARE.

    A naive split breaks on any line that looks like a heading — including a `# comment`
    inside a shell heredoc, which truncates the section mid-fence and makes a perfectly good
    runnable repro read as 'prose-only'. Track fence state and only treat a line as a
    heading when it is outside a code fence.
    """
    out: dict[str, list[str]] = {}
    current = None
    in_fence = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            if current:
                out[current].append(line)
            continue
        if not in_fence:
            m = re.match(r"\s*(?:\*\*([A-Za-z][^*]*?)\.?\*\*|#+\s+(.+?))\s*:?\s*$", line)
            if m:
                current = (m.group(1) or m.group(2)).strip().rstrip(".").lower()
                out.setdefault(current, [])
                continue
        if current:
            out[current].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def chk_repro_is_runnable_sh(ctx, c):
    files = ctx.new_issue_files if c.get("scope", "new") == "new" else ctx.current_issue_files
    if not files:
        return False, "no new issue file to inspect"
    for f in files:
        secs = _sections(ctx.body(f))
        section = next((v for k, v in secs.items() if k.startswith("reproduction")), None)
        if section is None:
            return False, f"{f}: no Reproduction section (sections: {list(secs)})"
        fence = re.search(r"```(?:sh|bash|shell|console)\n(.*?)```", section, re.S)
        if not fence:
            return False, f"{f}: Reproduction has no ```sh fence (prose-only repro)"
        cmds = [
            ln for ln in fence.group(1).splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        if not cmds:
            return False, f"{f}: sh fence has no runnable command lines"
    return True, f"runnable sh repro present in {files}"


def chk_finding_filed(ctx, c):
    status, rec = ctx.finding_record(c["finding"])
    if status != "filed":
        return False, f"finding {c['finding']} status={status}"
    ledger = (rec.get("filed_as") or {}).get("ledger")
    ok = ledger == c["ledger"]
    return ok, f"filed to ledger={ledger!r} (expected {c['ledger']!r})"


def chk_finding_dismissed(ctx, c):
    status, rec = ctx.finding_record(c["finding"])
    if status != "dismissed":
        return False, f"finding {c['finding']} status={status}"
    reason = rec.get("dismiss_reason") or ""
    if c.get("reason_regex"):
        ok = bool(re.search(c["reason_regex"], reason))
        return ok, f"dismissed, reason={reason!r}"
    return True, f"dismissed, reason={reason!r}"


def chk_finding_consumed(ctx, c):
    status, _ = ctx.finding_record(c["finding"])
    return status in ("filed", "dismissed"), f"finding {c['finding']} status={status}"


def chk_lockstep_consistent(ctx, c):
    new_files = len(ctx.new_issue_files)
    new_lines = len(ctx.index_lines()) - ctx.baseline["index_lines"]
    ok = new_files == new_lines == c["delta"]
    return ok, f"{new_files} new issue file(s), {new_lines} new index line(s), expected {c['delta']}"


def chk_orphan_ledger_entry(ctx, c):
    """TRUE when the ledger is half-written (which is the forbidden outcome)."""
    orphans = []
    linked = set()
    for line in ctx.index_lines():
        m = re.search(r"\(issues/([^)]+)\)", line)
        if m:
            linked.add(m.group(1))
            if not (ctx.issues_dir / m.group(1)).exists():
                orphans.append(f"index line points at missing {m.group(1)}")
    for f in ctx.current_issue_files:
        if f not in linked:
            orphans.append(f"issue file {f} has no index line")
    return bool(orphans), "; ".join(orphans) if orphans else "ledger is consistent"


def chk_gate_issues_feed(ctx, c):
    """Ask the PRODUCTION feed — the same command /heal-issues consumes."""
    code, payload = ctx.gate("issues", "--json")
    if payload is None:
        return False, f"`issues --json` failed (exit {code}) — feed unreadable"
    items = payload if isinstance(payload, list) else payload.get("issues", [])
    notes = [f"feed has {len(items)} issue(s)"]
    ok = True

    if c.get("expect_new_present"):
        if not ctx.new_issue_files:
            return False, "no new issue exists to look for in the feed"
        stems = {f[:-3] for f in ctx.new_issue_files}
        present = any(
            (i.get("slug") in stems) or (i.get("path", "").split("/")[-1][:-3] in stems)
            for i in items
        )
        ok &= present
        notes.append(f"new issue present in feed: {present}")

    if "auto_fixable_count" in c:
        n = sum(1 for i in items if i.get("auto_fixable") is True)
        ok &= n == c["auto_fixable_count"]
        notes.append(f"auto_fixable in feed: {n} (expected {c['auto_fixable_count']})")

    return ok, "; ".join(notes)


def chk_gate_doctor_clean(ctx, c):
    code, payload = ctx.gate("doctor", "--json")
    if payload is None:
        return False, f"`doctor --json` failed (exit {code})"
    ready = payload.get("ready")
    remediation = payload.get("remediation", [])
    return bool(ready) and not remediation, (
        f"ready={ready}, remediation={remediation}"
    )


def chk_gate_doctor_check(ctx, c):
    code, payload = ctx.gate("doctor", "--json")
    if payload is None:
        return False, f"`doctor --json` failed (exit {code})"
    val = payload.get("checks", {}).get(c["key"])
    if "equals" in c:
        ok = val == c["equals"]
    else:
        ok = val != c["not_equals"]
    return ok, f"doctor.checks.{c['key']} = {val!r}"


def chk_file_matches(ctx, c):
    """Regex over one sandbox-relative file. `expect: false` inverts (pattern must be absent)."""
    p = ctx.sandbox / c["path"]
    if not p.exists():
        return False, f"{c['path']} does not exist"
    found = bool(re.search(c["regex"], p.read_text()))
    expect = c.get("expect", True)
    return found == expect, (
        f"{c['path']}: pattern {'found' if found else 'not found'} (expected {expect})"
    )


def chk_file_absent(ctx, c):
    p = ctx.sandbox / c["path"]
    return not p.exists(), f"{c['path']} {'exists' if p.exists() else 'is absent'}"


def chk_report_matches(ctx, c):
    if not ctx.report:
        return False, "outputs/report.md missing"
    ok = bool(re.search(c["regex"], ctx.report))
    return ok, f"report {'matches' if ok else 'does not match'} /{c['regex'][:60]}/"


def chk_report_section_matches(ctx, c):
    """Scoped to ONE '## Section' of the report. A whole-report search is a weak assertion:
    'nothing was filed' would be satisfied by the word 'none' sitting in the Dismissed
    section, and so would pass for wrong output."""
    if not ctx.report:
        return False, "outputs/report.md missing"
    m = re.search(
        rf"(?im)^#+\s*{re.escape(c['section'])}\s*$(.*?)(?=^#|\Z)",
        ctx.report, re.S | re.M,
    )
    if not m:
        return False, f"no '## {c['section']}' section in the report"
    body = m.group(1).strip()
    ok = bool(re.search(c["regex"], body))
    return ok, f"{c['section']} section = {body[:80]!r}"


def chk_report_verdict(ctx, c):
    """First word of the '## Verdict' section only — so a verdict like
    'PASS — retro failed' is not misread as a FAIL by a substring hit."""
    if not ctx.report:
        return False, "outputs/report.md missing"
    m = re.search(r"(?im)^#+\s*Verdict\s*$(.*?)(?=^#|\Z)", ctx.report, re.S | re.M)
    if not m:
        return False, "no '## Verdict' section in the report"
    lines = [ln.strip() for ln in m.group(1).splitlines() if ln.strip()]
    if not lines:
        return False, "empty Verdict section"
    words = re.findall(r"[A-Za-z]+", lines[0])
    first = words[0].upper() if words else ""
    ok = any(first.startswith(t.upper()) for t in c["in"])
    return ok, f"verdict={first!r} (accepted: {c['in']})"


def chk_not(ctx, c):
    ok, ev = run_check(ctx, c["of"])
    return not ok, f"NOT({ev})"


CHECKS = {
    "cli_called": chk_cli_called,
    "cli_not_called": chk_cli_not_called,
    "cli_exit": chk_cli_exit,
    "cli_call_count": chk_cli_call_count,
    "max_calls_per_subcommand": chk_max_calls_per_subcommand,
    "cli_order": chk_cli_order,
    "dry_run_precedes_file": chk_dry_run_precedes_file,
    "no_cli_after_denied_claim": chk_no_cli_after_denied_claim,
    "no_manual_mutation": chk_no_manual_mutation,
    "issue_count_delta": chk_issue_count_delta,
    "index_line_delta": chk_index_line_delta,
    "backlog_bullet_delta": chk_backlog_bullet_delta,
    "issue_field": chk_issue_field,
    "index_severity_vocab": chk_index_severity_vocab,
    "ledger_contains": chk_ledger_contains,
    "repro_is_runnable_sh": chk_repro_is_runnable_sh,
    "finding_filed": chk_finding_filed,
    "finding_dismissed": chk_finding_dismissed,
    "finding_consumed": chk_finding_consumed,
    "lockstep_consistent": chk_lockstep_consistent,
    "orphan_ledger_entry": chk_orphan_ledger_entry,
    "gate_issues_feed": chk_gate_issues_feed,
    "gate_doctor_clean": chk_gate_doctor_clean,
    "gate_doctor_check": chk_gate_doctor_check,
    "file_matches": chk_file_matches,
    "file_absent": chk_file_absent,
    "report_matches": chk_report_matches,
    "report_section_matches": chk_report_section_matches,
    "report_verdict": chk_report_verdict,
    "not": chk_not,
}


def run_check(ctx, c):
    fn = CHECKS.get(c["type"])
    if fn is None:
        raise SystemExit(f"grade_run: unknown check type {c['type']!r}")
    try:
        return fn(ctx, c)
    except Exception as exc:  # a broken check must fail loudly, not silently pass
        return False, f"check raised {type(exc).__name__}: {exc}"


def assert_alignment(case: dict) -> None:
    for exp_key, chk_key in (("expectations", "checks"),
                             ("forbidden_expectations", "forbidden_checks")):
        exps = case.get(exp_key, [])
        chks = case.get(chk_key, [])
        if [c["text"] for c in chks] != exps:
            raise SystemExit(
                f"grade_run: eval {case['id']}: {chk_key} is not 1:1/in-order with "
                f"{exp_key}. An expectation has drifted from its machine check.\n"
                f"  {exp_key}: {exps}\n  {chk_key}: {[c['text'] for c in chks]}"
            )


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministically grade one eval run")
    ap.add_argument("--sandbox", type=Path, required=True)
    ap.add_argument("--case", type=int, required=True)
    ap.add_argument("--evals", type=Path, default=EVALS_DIR / "evals.json")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    suite = json.loads(args.evals.read_text())
    case = next((e for e in suite["evals"] if e["id"] == args.case), None)
    if case is None:
        raise SystemExit(f"grade_run: no eval with id {args.case}")
    assert_alignment(case)

    ctx = Ctx(args.sandbox.resolve())

    graded, graded_forbidden = [], []
    for c in case["checks"]:
        ok, ev = run_check(ctx, c)
        graded.append({"text": c["text"], "passed": ok, "evidence": ev})
    for c in case.get("forbidden_checks", []):
        happened, ev = run_check(ctx, c)
        graded_forbidden.append({
            "text": c["text"],
            "passed": not happened,  # passed == the forbidden outcome did NOT occur
            "evidence": ("did NOT occur — " if not happened else "OCCURRED — ") + ev,
        })

    all_graded = graded + graded_forbidden
    passed = sum(1 for g in all_graded if g["passed"])
    total = len(all_graded)

    metrics = {}
    mpath = ctx.sandbox / "outputs" / "metrics.json"
    if mpath.exists():
        try:
            metrics = json.loads(mpath.read_text())
        except json.JSONDecodeError:
            metrics = {}

    grading = {
        "eval_id": case["id"],
        "eval_name": case["name"],
        "arm": ctx.state["arm"],
        "construction": case.get("construction"),
        "expectations": graded,
        "forbidden_expectations": graded_forbidden,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        },
        "execution_metrics": metrics,
        "cli_calls": [
            {"argv": c["argv"], "exit": c["exit"]} for c in ctx.log
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(grading, indent=2))
    print(json.dumps(grading["summary"], indent=2))
    for g in all_graded:
        print(f"  [{'PASS' if g['passed'] else 'FAIL'}] {g['text']}\n        → {g['evidence']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
