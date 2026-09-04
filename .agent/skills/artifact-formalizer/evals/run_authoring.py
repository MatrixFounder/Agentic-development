#!/usr/bin/env python3
"""Executor for the artifact-formalizer eval set (TASK 101).

Axis A — two arms per case. They differ in ONE input: the `with_contract` arm
is handed the text of `references/authoring-contract.md`; the `baseline` arm is
not. Same prompt, same model, same working directory shape, same tool denials.

Axis B — one run per fixture. The agent performs the SKILL.md step B4 reading
pass over the `--sections` worklist and returns findings as JSON.

This is the ONLY script here that spends tokens. `--dry-run` prints the command
and spawns nothing, which is how `selftest_evals.py` checks the command shape
for free.

Exit codes
  0  every requested run completed
  1  at least one run failed or returned an empty document
  2  the working directory is not isolated
  3  the invocation is wrong
"""

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
CONTRACT = os.path.join(SKILL, "references", "authoring-contract.md")
GUIDE = os.path.join(SKILL, "references", "formalization-guide.md")
SCANNER = os.path.join(SKILL, "scripts", "scan_register.py")

ARMS = ("baseline", "with_contract")
DEFAULT_MODEL = "claude-opus-5"

# The authoring task needs no tool. Denying them removes the second path to the
# contract and the agent's ability to write anywhere. `permission_denials` from
# the run envelope is recorded, so an attempted read is visible.
DENIED_TOOLS = ("Bash", "Read", "Write", "Edit", "MultiEdit", "NotebookEdit",
                "Glob", "Grep", "WebFetch", "WebSearch", "Task", "TodoWrite")

# A directory holding any of these teaches the baseline arm the contract that
# defines the arm.
LEAK_NAMES = ("CLAUDE.md", ".agent", ".claude", "AGENTS.md", "GEMINI.md")

CONTRACT_HEADER = (
    "You are writing a specification. Apply the authoring contract below to "
    "every sentence you write.\n\n"
    "=== BEGIN AUTHORING CONTRACT ===\n")
CONTRACT_FOOTER = "\n=== END AUTHORING CONTRACT ===\n\n"

AXIS_B_HEADER = (
    "You are auditing a specification for register defects. Apply the rules "
    "below.\n\n"
    "=== BEGIN FORMALIZATION GUIDE ===\n")
#: What each of the three partly-reachable rules asks the reader to find. Held
#: as one dict so the combined and the split pass are built from the SAME
#: sentences: a split arm phrased differently would measure the rewording, not
#: the split.
AXIS_B_RULES = {
    3: ("rule 3 — a requirement carrying its own justification, where the "
        "obligation\n  and the justification sit in SEPARATE sentences;"),
    4: ("rule 4 — a maxim or an aphorism standing where a norm belongs, "
        "including one\n  written today that matches no known template;"),
    6: ("rule 6 — a coined noun standing where a standard term belongs, "
        "including one\n  invented for this document."),
}

AXIS_B_MIDDLE = """
=== END FORMALIZATION GUIDE ===

A deterministic scanner has already run on this document and reported ZERO
findings. {preamble}

{rules}

Read EVERY section of the worklist below, not only the sections that look
suspicious.

=== BEGIN SECTION WORKLIST ===
{worklist}
=== END SECTION WORKLIST ===

=== BEGIN DOCUMENT (line-numbered) ===
{document}
=== END DOCUMENT ===

Output a JSON object and nothing else, in this exact shape:

{{"findings": [{{"line": <int>, "rule": <{allowed}>, "quote": "<the text>"}}]}}

Report a line only when you can name which rule it violates. An empty findings
list is a valid answer.
"""

FENCE = re.compile(r"\A\s*```[^\n]*\n(.*?)\n?```\s*\Z", re.S)


class NotIsolated(RuntimeError):
    """The working directory would leak the contract into the baseline arm."""


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def leaks_above(path):
    """Return every context file at or above *path*, stopping at $HOME.

    `~/.claude` is the user-level configuration. It is loaded for every run of
    `claude` regardless of the directory, it is identical in both arms, and it
    does not hold this skill. Walking into it would report a leak that no
    directory choice can remove.
    """
    found = []
    home = os.path.realpath(os.path.expanduser("~"))
    cur = os.path.realpath(path)
    while cur != home:
        for name in LEAK_NAMES:
            candidate = os.path.join(cur, name)
            if os.path.exists(candidate):
                found.append(candidate)
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return found


def isolated_workdir(base=None):
    """Create a working directory and assert nothing above it leaks."""
    path = tempfile.mkdtemp(prefix="formalizer-eval-", dir=base)
    leaks = leaks_above(path)
    if leaks:
        shutil.rmtree(path, ignore_errors=True)
        raise NotIsolated("; ".join(leaks))
    return path


def build_prompt(case_prompt, arm, contract_text=None):
    """Return the prompt for *arm*. The arms differ by the contract block only."""
    if arm == "baseline":
        return case_prompt
    if arm != "with_contract":
        raise ValueError(f"unknown arm {arm!r}")
    text = _read(CONTRACT) if contract_text is None else contract_text
    return CONTRACT_HEADER + text + CONTRACT_FOOTER + case_prompt


def contract_block(contract_text=None):
    """Return the exact bytes `build_prompt` prepends for `with_contract`."""
    text = _read(CONTRACT) if contract_text is None else contract_text
    return CONTRACT_HEADER + text + CONTRACT_FOOTER


def build_command(prompt, model):
    """Return the argv for one `claude -p` run."""
    return ["claude", "-p", prompt,
            "--output-format", "json",
            "--model", model,
            "--disallowed-tools", *DENIED_TOOLS]


def spawn(prompt, model, workdir, timeout=900):
    """Run one agent and return its envelope. The only token-spending call."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    try:
        proc = subprocess.run(build_command(prompt, model), cwd=workdir,
                              env=env, capture_output=True, text=True,
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        # Recorded as a failed run rather than raised. One stalled case must
        # not discard the arms that already completed.
        return {"is_error": True, "result": "",
                "error": f"timed out after {timeout}s", "returncode": None}
    if proc.returncode != 0 and not proc.stdout.strip():
        return {"is_error": True, "result": "",
                "error": proc.stderr.strip()[:2000],
                "returncode": proc.returncode}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {"is_error": True, "result": "",
                "error": f"unparsable envelope: {exc}",
                "returncode": proc.returncode}


def unwrap(text):
    """Strip ONE enclosing fenced block. Returns (text, unwrapped)."""
    m = FENCE.match(text or "")
    return (m.group(1), True) if m else (text or "", False)


def sections_worklist(fixture_path):
    """Return the scanner's own `--sections` worklist for *fixture_path*."""
    proc = subprocess.run(
        [sys.executable, SCANNER, fixture_path, "--sections"],
        capture_output=True, text=True)
    out = proc.stdout
    marker = "READING-PASS WORKLIST"
    return out[out.index(marker):] if marker in out else out


def number_lines(text):
    return "\n".join(f"{i:>4}| {line}"
                     for i, line in enumerate(text.split("\n"), 1))


def build_axis_b_prompt(fixture_path, rules=(3, 4, 6)):
    """Build one reading pass over *fixture_path* for *rules*.

    `rules` is the whole difference between the two arms R10 compares. The
    combined arm passes all three in one call, which is what step B4 of
    `SKILL.md` currently prescribes. The split arm calls this three times, once
    per rule, and unions the answers. Everything else -- the guide, the
    worklist, the document, the output shape -- is identical, so a difference
    in the result is a difference in the split.
    """
    rules = tuple(rules)
    unknown = set(rules) - set(AXIS_B_RULES)
    if unknown:
        raise ValueError(f"unknown axis-B rule(s) {sorted(unknown)}")
    # The full-set wording is byte-identical to what step B4 has always emitted.
    # A combined arm phrased even slightly differently would make this a
    # measurement of the rewording rather than of the split.
    if rules == (3, 4, 6):
        preamble = ("Three rules are only partly reachable by any detector, so "
                    "the\nremainder is yours:")
    elif len(rules) == 1:
        preamble = ("One rule is only partly reachable by any detector, so the\n"
                    "remainder is yours:")
    else:
        preamble = (f"{len(rules)} rules are only partly reachable by any "
                    f"detector, so the\nremainder is yours:")
    return (AXIS_B_HEADER + _read(GUIDE)
            + AXIS_B_MIDDLE.format(
                preamble=preamble,
                rules="\n".join(f"- {AXIS_B_RULES[r]}" for r in rules),
                allowed="|".join(str(r) for r in rules),
                worklist=sections_worklist(fixture_path),
                document=number_lines(_read(fixture_path))))


def _write_meta(path, payload):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)


def run_authoring_case(case, arm, rep, model, out_root, dry_run=False):
    """Execute one arm of one Axis A case and write the corpus entry."""
    case_prompt = _read(os.path.join(HERE, case["prompt_file"]))
    contract_text = _read(CONTRACT)
    prompt = build_prompt(case_prompt, arm, contract_text)
    if dry_run:
        print(f"[dry-run] {case['id']}/{arm}/rep-{rep}: "
              f"{' '.join(build_command('<prompt>', model))}")
        return {"dry_run": True}

    workdir = isolated_workdir()
    try:
        env = spawn(prompt, model, workdir)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    body, unwrapped = unwrap(env.get("result", ""))
    arm_dir = os.path.join(out_root, case["id"], arm)
    os.makedirs(arm_dir, exist_ok=True)
    with open(os.path.join(arm_dir, f"rep-{rep}.md"), "w",
              encoding="utf-8") as fh:
        fh.write(body)
    _write_meta(os.path.join(arm_dir, f"rep-{rep}.meta.json"), {
        "case": case["id"], "arm": arm, "rep": rep, "model": model,
        "prompt_sha256_16": _sha(case_prompt),
        "contract_sha256_16": _sha(contract_text),
        "contract_applied": arm == "with_contract",
        "unwrapped_fence": unwrapped,
        "is_error": bool(env.get("is_error")),
        "error": env.get("error"),
        "permission_denials": env.get("permission_denials", []),
        "models_used": sorted(env.get("modelUsage", {})),
        "total_cost_usd": env.get("total_cost_usd"),
        "duration_ms": env.get("duration_ms"),
        "session_id": env.get("session_id"),
        "output_chars": len(body),
    })
    return {"ok": bool(body.strip()) and not env.get("is_error"),
            "chars": len(body), "cost": env.get("total_cost_usd") or 0.0}


#: The two reading-pass arms R10 compares. `combined` is what step B4 of
#: SKILL.md prescribes today: one call naming all three partly-reachable rules.
#: `split` is the proposal: three calls, one rule each, answers unioned.
PASS_MODES = {"combined": ((3, 4, 6),), "split": ((3,), (4,), (6,))}


def _one_gap_pass(fixture, rules, model, dry_run, label):
    """Run a single reading pass and return (answer, envelope, prompt)."""
    prompt = build_axis_b_prompt(fixture, rules)
    if dry_run:
        print(f"[dry-run] {label}: "
              f"{' '.join(build_command('<prompt>', model))}"
              f"  (rules {'+'.join(str(r) for r in rules)}, "
              f"prompt {len(prompt)} chars)")
        return None, None, prompt

    workdir = isolated_workdir()
    try:
        env = spawn(prompt, model, workdir)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    body, _ = unwrap(env.get("result", ""))
    try:
        answer = json.loads(body)
    except json.JSONDecodeError:
        answer = {"findings": [], "unparsable": body[:4000]}
    return answer, env, prompt


def run_gap_case(case, model, out_root, rep=1, dry_run=False,
                 pass_mode="combined"):
    """Execute one Axis B reading pass and write its answer.

    Repetitions live in their own directory, mirroring axis A. A reading pass
    is as non-deterministic as an authoring run, and one draw of `6 of 6` says
    less than three do.

    `pass_mode` selects the arm. Under `split` the case costs three calls
    instead of one and their findings are unioned -- the cost R10 names as its
    own risk, made visible in the recorded `total_cost_usd`.
    """
    if pass_mode not in PASS_MODES:
        raise ValueError(f"unknown pass mode {pass_mode!r}; "
                         f"known: {sorted(PASS_MODES)}")
    fixture = os.path.join(HERE, case["fixture"])
    groups = PASS_MODES[pass_mode]

    if dry_run:
        for rules in groups:
            _one_gap_pass(fixture, rules, model, True,
                          f"{case['id']}/{pass_mode}/rep-{rep}")
        return {"dry_run": True}

    findings, passes, cost, errors, unparsable = [], [], 0.0, [], False
    for rules in groups:
        answer, env, prompt = _one_gap_pass(fixture, rules, model, False, "")
        got = answer.get("findings") or []
        # A split pass may only report the rule it was asked about. A finding
        # naming another rule is a leak between passes, and dropping it
        # silently would flatter the arm.
        kept = [f for f in got if _rule_of(f) in rules]
        leaked = [f for f in got if _rule_of(f) not in rules]
        findings.extend(kept)
        if "unparsable" in answer:
            unparsable = True
        if env.get("is_error"):
            errors.append(env.get("error"))
        cost += env.get("total_cost_usd") or 0.0
        passes.append({
            "rules": list(rules),
            "prompt_sha256_16": _sha(prompt),
            "reported": len(got),
            "kept": len(kept),
            "leaked_to_other_rules": leaked,
            "parsed": "unparsable" not in answer,
            "is_error": bool(env.get("is_error")),
            "total_cost_usd": env.get("total_cost_usd"),
            "duration_ms": env.get("duration_ms"),
            "session_id": env.get("session_id"),
        })

    answer = {"findings": findings}
    if unparsable:
        answer["unparsable"] = True
    case_dir = os.path.join(out_root, case["id"], f"rep-{rep}")
    os.makedirs(case_dir, exist_ok=True)
    _write_meta(os.path.join(case_dir, "answer.json"), answer)
    _write_meta(os.path.join(case_dir, "meta.json"), {
        "case": case["id"], "rep": rep, "model": model,
        "fixture": case["fixture"],
        "pass_mode": pass_mode,
        "passes": passes,
        "calls": len(groups),
        "prompt_sha256_16": passes[0]["prompt_sha256_16"],
        "is_error": bool(errors),
        "error": errors or None,
        "permission_denials": [],
        "parsed": not unparsable,
        "total_cost_usd": cost,
        "duration_ms": sum(p["duration_ms"] or 0 for p in passes),
        "session_id": passes[0]["session_id"],
    })
    return {"ok": not unparsable and not errors,
            "findings": len(findings), "cost": cost}


def _rule_of(finding):
    """The rule a reported finding names, or None when it names none."""
    try:
        return int(finding["rule"])
    except (KeyError, TypeError, ValueError):
        return None


def plan_runs(evals, axis="both", reps=1, cases=None, arms=None):
    """Return every (label, thunk-arguments) this invocation will execute.

    The plan is built before anything spawns, so `--dry-run` prints exactly the
    set a real run would execute and `--jobs` has a list to distribute.
    """
    wanted = set(cases or ())
    runs = []
    for case in evals["cases"]:
        if wanted and case["id"] not in wanted:
            continue
        if case["axis"] == "authoring" and axis in ("a", "both"):
            for arm in (arms or ARMS):
                for rep in range(1, reps + 1):
                    runs.append((f"{case['id']}/{arm}/rep-{rep}",
                                 "authoring", case, arm, rep))
        elif case["axis"] == "recall_gap" and axis in ("b", "both"):
            for rep in range(1, reps + 1):
                runs.append((f"{case['id']}/rep-{rep}",
                             "recall_gap", case, None, rep))
    return runs


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Run the artifact-formalizer eval campaign "
                    "(this is the script that spends tokens)")
    ap.add_argument("--evals", default=os.path.join(HERE, "evals.json"))
    ap.add_argument("--out-root", default=os.path.join(HERE, "corpus"))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--axis", choices=("a", "b", "both"), default="both")
    ap.add_argument("--pass-mode", choices=sorted(PASS_MODES), default="combined",
                    help="axis B only. `combined` is what SKILL.md step B4 "
                         "prescribes: one reading pass naming all three "
                         "partly-reachable rules. `split` is registry item "
                         "R10's proposal: three passes, one rule each, unioned. "
                         "R10 ships only if `split` measures a recall gain, so "
                         "these are the two arms of that comparison")
    ap.add_argument("--cases", action="append", dest="cases",
                    help="run only these case ids")
    ap.add_argument("--arm", action="append", dest="arms", choices=ARMS,
                    help="run only these arms. A contract change moves one arm "
                         "only, so re-drawing the other spends tokens to "
                         "reproduce a number the committed corpus already holds")
    ap.add_argument("--jobs", type=int, default=1,
                    help="concurrent agents; each run is an independent "
                         "process writing its own file, so ordering is the "
                         "only thing concurrency changes")
    ap.add_argument("--dry-run", action="store_true",
                    help="print each command and spawn nothing")
    ap.exit_on_error = False
    try:
        args = ap.parse_args(argv)
    # `exit_on_error = False` keeps a usage error from killing the process,
    # and it also routes argparse's own message into the exception instead
    # of stderr. Print it: an exit 3 that says nothing sends the caller to
    # read the source to find out which flag was wrong. Measured: a run
    # with `--corpus` instead of `--run-dir` exited 3 in silence.
    except argparse.ArgumentError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        ap.print_usage(sys.stderr)
        return 3
    except SystemExit as exc:
        code = getattr(exc, "code", 1)
        return 0 if code == 0 else 3
        return 0 if code == 0 else 3

    if args.reps % 2 == 0:
        print("usage error: --reps must be odd; an even count lets an exact "
              "split decide by comparison order", file=sys.stderr)
        return 3
    if args.jobs < 1:
        print("usage error: --jobs must be at least 1", file=sys.stderr)
        return 3
    if not os.path.isfile(args.evals):
        print(f"usage error: no eval file at {args.evals}", file=sys.stderr)
        return 3

    with open(args.evals, encoding="utf-8") as fh:
        evals = json.load(fh)
    runs = plan_runs(evals, args.axis, args.reps, args.cases, args.arms)
    failures, cost = [], 0.0

    def execute(entry):
        label, kind, case, arm, rep = entry
        if kind == "authoring":
            return label, run_authoring_case(case, arm, rep, args.model,
                                             args.out_root, args.dry_run)
        return label, run_gap_case(case, args.model, args.out_root, rep,
                                   args.dry_run, args.pass_mode)

    def record(label, res):
        nonlocal cost
        cost += res.get("cost", 0.0)
        if args.dry_run:
            return
        if not res.get("ok"):
            failures.append(label)
            print(f"  {label}: FAILED")
        elif "chars" in res:
            print(f"  {label}: {res['chars']} chars")
        else:
            print(f"  {label}: {res['findings']} findings")

    try:
        if args.jobs == 1 or args.dry_run:
            for entry in runs:
                record(*execute(entry))
        else:
            with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
                for future in concurrent.futures.as_completed(
                        [pool.submit(execute, e) for e in runs]):
                    record(*future.result())
    except NotIsolated as exc:
        print(f"not isolated: {exc}", file=sys.stderr)
        return 2

    if not args.dry_run:
        print(f"\n{len(runs)} runs   cost: ${cost:.2f}   "
              f"failures: {len(failures)}")
        for f in failures:
            print(f"  {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
