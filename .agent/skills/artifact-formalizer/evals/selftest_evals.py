#!/usr/bin/env python3
"""Instrument selftest for the artifact-formalizer eval set (TASK 101).

It spawns no agent and costs no token. It verifies the INSTRUMENT, never the
skill: nothing here proves that the authoring contract improves what a model
writes. Only a campaign does, and only `run_authoring.py` runs one.

Exit 0 when every case passes, 1 otherwise.
"""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(SKILL, "scripts"))

import grade_run                                              # noqa: E402
import run_authoring                                          # noqa: E402
import scan_register                                          # noqa: E402

#: Total rows this battery prints, PINNED as a literal. Deriving it from the
#: run would make the assertion agree with itself after any deletion — the
#: defect `selftest_scan.py` records as REG-2. `README.md` states the same
#: number, and TC-EV-13b reads it from there.
EXPECTED_CASES = 59

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


class Sentinel:
    """Stands in for the one call that spends tokens."""

    def __init__(self):
        self.calls = 0

    def __call__(self, *a, **kw):
        self.calls += 1
        raise AssertionError("selftest_evals spawned an agent")


SPAWN_SENTINEL = Sentinel()
run_authoring.spawn = SPAWN_SENTINEL


def _evals():
    with open(os.path.join(HERE, "evals.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


# --------------------------------------------------------------------------
# The two documents TC-EV-02 compares. Both are declared here, never derived
# from a fixture, so a fixture edit cannot move both sides of the comparison.
# --------------------------------------------------------------------------
GOLDEN_DOC = """# Cache eviction

## 1. Scope

In scope: the eviction policy. Out of scope: the write path.

## 2. Requirements

**R1.** The cache evicts the least recently used entry when it reaches 10,000 entries.

**Why.** The process budget is 200 MB and one entry averages 18 KB.

**R2.** An evicted key is counted in the `evictions_total` metric.

**Why.** The on-call runbook reads that counter before it raises the limit.
"""

VIOLATOR_DOC = """# Cache eviction

## 1. Scope

Obviously the elegant approach here is the naive one, and it is crucial that we leverage a robust
seamless policy, because the cache must not become the seam where the whole request path goes red
and the on-call engineer is punished for a design decision that outlived its reason and was never
written down anywhere a reader could find it without asking three people first.

## 2. Requirements

**R1.** The cache must evict the least recently used entry because the process budget is 200 MB and
one entry averages 18 KB, which is why the limit sits at 10,000 entries and not somewhere else.

A gate that blesses everything checks nothing. 🔴 Critical: the metric silently disappears.
"""

LOW_PROSE_DOC = "# Generated\n\nOne line of prose.\n\n```text\n" + \
    "\n".join(f"row {i} value {i * 7}" for i in range(40)) + "\n```\n"


def t_set_shape():
    ev = _evals()
    cases = ev.get("cases", [])
    authoring = [c for c in cases if c["axis"] == "authoring"]
    gaps = [c for c in cases if c["axis"] == "recall_gap"]
    check("TC-EV-01a the set holds 10 cases", len(cases) == 10,
          f"n={len(cases)}")
    check("TC-EV-01b 6 authoring and 4 recall-gap",
          len(authoring) == 6 and len(gaps) == 4,
          f"authoring={len(authoring)} gaps={len(gaps)}")
    check("TC-EV-01c both shipped languages appear on axis A",
          {c["lang"] for c in authoring} == {"en", "ru"},
          f"langs={sorted({c['lang'] for c in authoring})}")
    check("TC-EV-01d axis A spans at least four artifact kinds",
          len({c["artifact_kind"] for c in authoring}) >= 4,
          f"kinds={sorted({c['artifact_kind'] for c in authoring})}")
    check("TC-EV-01e exactly one recall-gap case is the control",
          sum(1 for c in gaps if c.get("control")) == 1,
          f"controls={[c['id'] for c in gaps if c.get('control')]}")
    missing = [c["prompt_file"] for c in authoring
               if not os.path.isfile(os.path.join(HERE, c["prompt_file"]))]
    check("TC-EV-01f every declared prompt file exists", not missing,
          f"missing={missing}")


def t_grader_direction():
    tmp = tempfile.mkdtemp(prefix="ev-grade-")
    try:
        g = grade_run.score_document(_write(os.path.join(tmp, "g.md"),
                                            GOLDEN_DOC))
        v = grade_run.score_document(_write(os.path.join(tmp, "v.md"),
                                            VIOLATOR_DOC))
        check("TC-EV-02a the violator scores higher on warn/100 lines",
              v["warn_per_100_lines"] > g["warn_per_100_lines"],
              f"golden={g['warn_per_100_lines']} violator={v['warn_per_100_lines']}")
        check("TC-EV-02b the violator scores higher on marker/100 lines",
              v["marker_per_100_lines"] > g["marker_per_100_lines"],
              f"golden={g['marker_per_100_lines']} violator={v['marker_per_100_lines']}")
        check("TC-EV-02c the violator has the longer mean sentence",
              v["sentence_mean"] > g["sentence_mean"],
              f"golden={g['sentence_mean']} violator={v['sentence_mean']}")
        check("TC-EV-02d the golden document scores zero warn",
              g["warn_per_100_lines"] == 0.0,
              f"golden={g['counts']}")
        check("TC-EV-02e both documents are measured",
              g["measured"] and v["measured"],
              f"golden={g['unmeasured_reason']} violator={v['unmeasured_reason']}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_axis_b_scorer():
    key = {"planted": [{"id": "P1", "lines": [10, 11], "rule": 3, "quote": "a"},
                       {"id": "P2", "lines": [20], "rule": 4, "quote": "b"}]}
    gold = grade_run.score_axis_b(
        [{"line": 11, "rule": 3}, {"line": 20, "rule": 4}], key)
    bad = grade_run.score_axis_b(
        [{"line": 10, "rule": 3}, {"line": 99, "rule": 6}], key)
    empty = grade_run.score_axis_b([], {"planted": []})
    noisy = grade_run.score_axis_b([{"line": 5, "rule": 4}], {"planted": []})
    check("TC-EV-03a a golden answer scores recall 1.0 and precision 1.0",
          gold["recall"] == 1.0 and gold["precision"] == 1.0, f"{gold}")
    check("TC-EV-03b an answer that misses one and invents one scores below 1.0",
          bad["recall"] < 1.0 and bad["precision"] < 1.0,
          f"recall={bad['recall']} precision={bad['precision']}")
    check("TC-EV-03c the missed defect is named", bad["missed"] == ["P2"],
          f"missed={bad['missed']}")
    check("TC-EV-03d a wrong rule on a planted line is spurious",
          grade_run.score_axis_b([{"line": 20, "rule": 6}], key)["recall"] == 0.0,
          "rule 6 reported on a rule-4 line")
    check("TC-EV-03e an empty control answer is marked vacuous",
          empty["vacuous_recall"] and empty["precision"] == 1.0, f"{empty}")
    check("TC-EV-03f a finding on the control is a false positive",
          noisy["precision"] == 0.0 and len(noisy["spurious"]) == 1,
          f"{noisy}")


def t_fixture_invariant():
    """A fixture the scanner reports on measures the detector, not the gap."""
    for case in [c for c in _evals()["cases"] if c["axis"] == "recall_gap"]:
        fixture = os.path.join(HERE, case["fixture"])
        key = json.load(open(os.path.join(HERE, case["key"]), encoding="utf-8"))
        payload = grade_run.scan([fixture])
        warns = payload.get("warn") or []
        planted_lines = {n for p in key["planted"] for n in p["lines"]}
        on_planted = [w for w in warns
                      if int(w["where"].rsplit(":", 1)[1]) in planted_lines]
        check(f"TC-EV-04 {case['id']} no warn on a planted line",
              not on_planted, f"{[w['where'] for w in on_planted]}")
        check(f"TC-EV-04 {case['id']} the fixture reports zero warn",
              not warns,
              f"{[w['where'] + ' ' + w['kind'] for w in warns]} — "
              f"re-word the fixture or re-plant it; a finding the scanner "
              f"already makes is not evidence about the gap")


def t_key_integrity():
    """A quote that no longer occurs on its declared line is a stale key."""
    stale = []
    for case in [c for c in _evals()["cases"] if c["axis"] == "recall_gap"]:
        text = open(os.path.join(HERE, case["fixture"]),
                    encoding="utf-8").read().split("\n")
        key = json.load(open(os.path.join(HERE, case["key"]), encoding="utf-8"))
        for p in key["planted"]:
            block = " ".join(text[n - 1] for n in p["lines"])
            block = " ".join(block.split())
            quote = " ".join(p["quote"].split())
            if quote not in block:
                stale.append(f"{case['id']}/{p['id']}")
            if int(p["rule"]) != int(key["rule"]):
                stale.append(f"{case['id']}/{p['id']} rule mismatch")
    check("TC-EV-05 every planted quote occurs on its declared lines",
          not stale, f"stale={stale}")


def t_prompt_identity():
    """The two arms differ by the contract block and by nothing else."""
    block = run_authoring.contract_block()
    bad = []
    for case in [c for c in _evals()["cases"] if c["axis"] == "authoring"]:
        body = open(os.path.join(HERE, case["prompt_file"]),
                    encoding="utf-8").read()
        base = run_authoring.build_prompt(body, "baseline")
        with_c = run_authoring.build_prompt(body, "with_contract")
        if not with_c.startswith(block) or with_c[len(block):] != base:
            bad.append(case["id"])
    check("TC-EV-06a removing the contract block yields the baseline prompt",
          not bad, f"differing={bad}")
    check("TC-EV-06b the contract block is the shipped contract",
          open(os.path.join(SKILL, "references", "authoring-contract.md"),
               encoding="utf-8").read() in block,
          "the block does not carry references/authoring-contract.md")
    named = [c["id"] for c in _evals()["cases"] if c["axis"] == "authoring"
             and any(w in open(os.path.join(HERE, c["prompt_file"]),
                               encoding="utf-8").read().lower()
                     for w in ("register", "формализ", "maxim", "metaphor",
                               "authoring contract"))]
    check("TC-EV-06c no prompt names a register rule", not named,
          f"prompts teaching the contract to both arms: {named}")


def t_isolation():
    base = tempfile.mkdtemp(prefix="ev-iso-")
    try:
        for name, maker in (("CLAUDE.md", lambda p: _write(p, "x")),
                            (".agent", os.makedirs),
                            (".claude", os.makedirs)):
            room = tempfile.mkdtemp(dir=base)
            maker(os.path.join(room, name))
            raised = False
            try:
                run_authoring.isolated_workdir(base=room)
            except run_authoring.NotIsolated:
                raised = True
            check(f"TC-EV-07 a directory holding {name} is refused", raised,
                  "isolated_workdir returned instead of raising")
        clean = run_authoring.isolated_workdir(base=base)
        check("TC-EV-07 a clean directory is accepted",
              os.path.isdir(clean) and not run_authoring.leaks_above(clean),
              f"leaks={run_authoring.leaks_above(clean)}")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_command_shape():
    cmd = run_authoring.build_command("PROMPT", "claude-opus-5")
    joined = " ".join(cmd)
    check("TC-EV-08a the command pins the model and the envelope format",
          "--model" in cmd and "claude-opus-5" in cmd
          and "--output-format" in cmd and "json" in cmd, joined)
    check("TC-EV-08b the command denies the file and command tools",
          "--disallowed-tools" in cmd
          and all(t in cmd for t in ("Bash", "Read", "Write", "Edit",
                                     "WebFetch", "Task")),
          joined)
    check("TC-EV-08c the prompt is passed as one argument",
          cmd[cmd.index("-p") + 1] == "PROMPT", joined)
    # stderr is captured: the refusal PRINTS a usage error, and a battery that
    # emits one reads as a failing run.
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = run_authoring.main(["--reps", "2", "--dry-run"])
    check("TC-EV-08d an even --reps is refused",
          rc == 3 and "must be odd" in err.getvalue(),
          f"exit={rc} stderr={err.getvalue().strip()!r}")

    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = run_authoring.main(["--jobs", "0", "--dry-run"])
    check("TC-EV-08e --jobs below 1 is refused",
          rc == 3 and "at least 1" in err.getvalue(),
          f"exit={rc} stderr={err.getvalue().strip()!r}")

    # Repetitions apply to BOTH axes. A reading pass is as non-deterministic as
    # an authoring run, and axis B carried the campaign's weakest number.
    ev = _evals()
    runs = run_authoring.plan_runs(ev, "both", 3)
    gap_runs = [r for r in runs if r[1] == "recall_gap"]
    check("TC-EV-08f the run plan covers both axes at every repetition",
          len(runs) == 6 * 2 * 3 + 4 * 3 and len(gap_runs) == 12,
          f"total={len(runs)} gaps={len(gap_runs)}")
    check("TC-EV-08g concurrency changes ordering and nothing else",
          run_authoring.plan_runs(ev, "both", 1)
          == run_authoring.plan_runs(ev, "both", 1),
          "the plan is not a pure function of its arguments")


def t_no_reimplementation():
    """The grader calls the production gate; it declares no threshold of it."""
    src = open(os.path.join(HERE, "grade_run.py"), encoding="utf-8").read()
    check("TC-EV-09a the grader imports scan_register",
          "import scan_register" in src
          and grade_run.scan_register is scan_register,
          "the grader does not hold the production module")
    restated = [k for k in scan_register.DEFAULTS
                if f"\n{k.upper()} =" in src or f"\n{k} =" in src]
    check("TC-EV-09b the grader restates no scanner threshold", not restated,
          f"restated={restated}; a copy grades against the previous value")
    check("TC-EV-09c the grader's own floor is not a scanner key",
          "prose_floor" not in scan_register.DEFAULTS
          and grade_run.PROSE_FLOOR == 25,
          f"floor={grade_run.PROSE_FLOOR}")
    payload = grade_run.scan([os.path.join(HERE, "fixtures",
                                           "control-conforming.md")])
    check("TC-EV-09d the grader reads the scanner's own thresholds",
          payload["thresholds"]["sentence_max_words"]
          == scan_register.DEFAULTS["sentence_max_words"],
          f"{payload['thresholds']}")


def t_report_shape():
    """A run that measured nothing must say so, not print a mean."""
    tmp = tempfile.mkdtemp(prefix="ev-report-")
    try:
        ev = {"cases": [{"id": "A1", "axis": "authoring", "lang": "en",
                         "artifact_kind": "task-spec"},
                        {"id": "A2", "axis": "authoring", "lang": "en",
                         "artifact_kind": "task-spec"},
                        {"id": "A3", "axis": "authoring", "lang": "en",
                         "artifact_kind": "task-spec"}]}
        for cid, arm, body in (("A1", "baseline", GOLDEN_DOC),
                               ("A1", "with_contract", VIOLATOR_DOC),
                               ("A2", "baseline", ""),
                               ("A2", "with_contract", GOLDEN_DOC),
                               ("A3", "baseline", LOW_PROSE_DOC),
                               ("A3", "with_contract", GOLDEN_DOC)):
            d = os.path.join(tmp, cid, arm)
            os.makedirs(d, exist_ok=True)
            _write(os.path.join(d, "rep-1.md"), body)
        doc = grade_run.grade(ev, tmp)
        text = grade_run.summarize(doc)
        check("TC-EV-10a an empty output is named, not dropped",
              any("A2/baseline" in e for e in doc["empty"]),
              f"empty={doc['empty']}")
        check("TC-EV-10b a case under the prose floor is unmeasured",
              any("A3/baseline" in u for u in doc["unmeasured"]),
              f"unmeasured={doc['unmeasured']}")
        check("TC-EV-10c an unmeasured case is excluded from the arm mean",
              doc["arms"]["baseline"]["documents"] == 1,
              f"baseline={doc['arms']['baseline']}")
        # A rate with no count behind it cannot separate "fewer findings" from
        # "a shorter document", and the two arms do not produce documents of
        # the same length.
        check("TC-EV-10c2 each arm reports its absolute counts beside the rates",
              all(k in doc["arms"]["with_contract"]
                  for k in ("warn_total", "lines_total", "sentence_max_worst",
                            "findings_by_kind"))
              and "warn over" in grade_run.summarize(doc),
              f"arm keys={sorted(doc['arms']['with_contract'])}")
        check("TC-EV-10d the summary prints both counts",
              "empty outputs       : 1" in text
              and "unmeasured cases    : 1" in text, text)
        # Found by the campaign, not by design. Two runs died on a transport
        # error and `run_authoring.py` wrote the 80-byte error string it got
        # back. The grader read the file and not its metadata, so both scored
        # `0 warn`, `measured: true`, and entered the arm mean.
        err_dir = os.path.join(tmp, "A9", "baseline")
        os.makedirs(err_dir, exist_ok=True)
        _write(os.path.join(err_dir, "rep-1.md"),
               "API Error: Connection closed mid-response.\n")
        _write(os.path.join(err_dir, "rep-1.meta.json"),
               json.dumps({"is_error": True, "model": "m",
                           "contract_sha256_16": "x"}))
        errdoc = grade_run.grade(
            {"cases": [{"id": "A9", "axis": "authoring", "lang": "en",
                        "artifact_kind": "task-spec"}]}, tmp)
        check("TC-EV-10g a run the executor marked is_error is not graded",
              any("A9/baseline" in e and "is_error" in e
                  for e in errdoc["empty"])
              and errdoc["arms"]["baseline"]["documents"] == 0,
              f"empty={errdoc['empty']} "
              f"docs={errdoc['arms']['baseline']['documents']}")
        # The metadata is the primary evidence; the line floor is the backstop
        # for a corpus placed by hand, where no meta.json exists.
        short = grade_run.score_document(
            _write(os.path.join(tmp, "short.md"), "API Error: closed.\n"))
        check("TC-EV-10h a document under the line floor is unmeasured",
              not short["measured"] and "line floor" in short["unmeasured_reason"],
              f"{short['unmeasured_reason']}")
        check("TC-EV-10e a campaign with no measured document says so",
              "NO ARM HAS A MEASURED DOCUMENT"
              in grade_run.summarize(grade_run.grade({"cases": []}, tmp)),
              "an empty campaign printed a summary that reads as a result")
        # An arm whose every document was rejected must stay in the table. A
        # one-armed table reads as a comparison and there is nothing to compare.
        only_bad = {"cases": [{"id": "A3", "axis": "authoring", "lang": "en",
                               "artifact_kind": "task-spec"}]}
        doc2 = grade_run.grade(only_bad, tmp)
        check("TC-EV-10f an arm with no accepted document is still named",
              set(doc2["arms"]) == {"baseline", "with_contract"}
              and doc2["arms"]["baseline"]["documents"] == 0
              and "NOT MEASURED" in grade_run.summarize(doc2),
              f"arms={ {k: v['documents'] for k, v in doc2['arms'].items()} }")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_corpus_shape():
    """Every authored document ships with the metadata that produced it."""
    root = os.path.join(HERE, "corpus")
    orphans, docs = [], 0
    for dirpath, _, files in os.walk(root):
        for name in files:
            if name.startswith("rep-") and name.endswith(".md"):
                docs += 1
                meta = name[:-3] + ".meta.json"
                if meta not in files:
                    orphans.append(os.path.join(dirpath, name))
    check("TC-EV-11a every rep-*.md has its meta.json", not orphans,
          f"orphans={orphans}")
    if docs == 0:
        check("TC-EV-11b the corpus is empty (no campaign has run here)", True,
              "0 documents — this is a statement, not a pass of the campaign")
    else:
        recorded = []
        for dirpath, _, files in os.walk(root):
            for name in files:
                if name.endswith(".meta.json"):
                    m = json.load(open(os.path.join(dirpath, name),
                                       encoding="utf-8"))
                    if not m.get("contract_sha256_16") or not m.get("model"):
                        recorded.append(os.path.join(dirpath, name))
        check("TC-EV-11b every meta.json records the model and the contract "
              "hash", not recorded, f"incomplete={recorded}")


def t_zero_tokens():
    check("TC-EV-12 the battery spawned no agent", SPAWN_SENTINEL.calls == 0,
          f"spawn called {SPAWN_SENTINEL.calls} time(s)")


def t_report_pin():
    """The committed numbers are re-derived, never trusted.

    `advanced-eval-patterns.md` §3: commit the raw run outputs and assert that
    grading them reproduces the committed report. Any accidental change to the
    grader then flips this case instead of silently moving the headline
    figures in `measurement-baseline.md` §12.
    """
    pinned_path = os.path.join(HERE, "report.json")
    if not os.path.isfile(pinned_path):
        check("TC-EV-14 the committed report re-derives from the corpus", False,
              "report.json is absent; a campaign's numbers are unpinned")
        return
    with open(pinned_path, encoding="utf-8") as fh:
        pinned = json.load(fh)
    fresh = grade_run.grade(_evals(), os.path.join(HERE, "corpus"))
    drift = [k for k in ("arms", "axis_b", "prose_floor", "unmeasured", "empty")
             if pinned.get(k) != fresh.get(k)]
    check("TC-EV-14 the committed report re-derives from the corpus",
          not drift,
          f"drifted={drift}; the grader or the corpus changed. Re-run "
          f"`grade_run.py --out report.json`, read the diff, and only then "
          f"accept it — measurement-baseline.md §12 quotes these values")


def t_count_pin():
    readme = os.path.join(HERE, "README.md")
    if not os.path.isfile(readme):
        check("TC-EV-13b README.md states the case count", False,
              "README.md is absent")
        return
    text = open(readme, encoding="utf-8").read()
    check("TC-EV-13b README.md states the case count",
          str(EXPECTED_CASES) in text,
          f"README does not carry {EXPECTED_CASES}")


def main():
    for fn in (t_set_shape, t_grader_direction, t_axis_b_scorer,
               t_fixture_invariant, t_key_integrity, t_prompt_identity,
               t_isolation, t_command_shape, t_no_reimplementation,
               t_report_shape, t_corpus_shape, t_report_pin, t_count_pin,
               t_zero_tokens):
        try:
            fn()
        except Exception as exc:                              # noqa: BLE001
            check(f"{fn.__name__} raised", False,
                  f"{type(exc).__name__}: {exc}")

    # `+ 1` counts this row: `check` has not appended it yet, and the number
    # under test is the one the run PRINTS.
    total = len(RESULTS) + 1
    check("TC-EV-13a the battery ran every case it declares",
          total == EXPECTED_CASES, f"ran={total} declared={EXPECTED_CASES}")

    failed = [r for r in RESULTS if not r[1]]
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL  {name}  — {detail}")
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed  "
          f"(0 agents spawned, 0 tokens)")
    if failed:
        print(f"{len(failed)} FAILING CASES:")
        for name, _, _ in failed:
            print(f"  · {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
