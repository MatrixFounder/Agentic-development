#!/usr/bin/env python3
"""Deterministic grader for the artifact-formalizer eval set (TASK 101).

It calls `scan_register.main()` and derives no finding and no threshold of its
own (ARCHITECTURE L4/L5, `skill-creator/references/advanced-eval-patterns.md`
sections 1 and 2). Grading costs no token and is a pure function of the
committed outputs plus the shipped rule files.

Exit codes
  0  graded
  2  the instrument is broken (a scan exited non-zero, a key is malformed)
  3  the invocation is wrong (a missing eval file, an unreadable run directory)
"""

import argparse
import contextlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SKILL, "scripts"))

import scan_register                                          # noqa: E402

# The share of non-blank lines that reached rule 1. Below this the per-line
# rates describe a document the scanner barely read, so the case is reported
# `measured: false` rather than as a value.
#
# Derivation: `references/measurement-baseline.md` section 10.1 E5 measured
# `task_md_template.md` at 27% under the masking defect and at 50% after the
# fix. A floor of 25 sits under both, so it names only a document measured less
# than the worst case that defect produced. It is NOT a register threshold, and
# no rule file declares it.
PROSE_FLOOR = 25

# A document shorter than this is not a specification. It is what a failed run
# leaves behind: `run_authoring.py` writes whatever the envelope returned, and
# a transport error returns one line of prose that scores perfectly on every
# register metric.
#
# Derivation: the shortest authored document this corpus holds is 87 lines; the
# error strings measured 1. Any floor between the two separates them, and 5
# sits far from both. It is NOT a register threshold, and no rule file
# declares it.
MIN_LINES = 5

# Every value below is read from the scanner's payload. `sentence_mean` and
# `prose_share_of_nonblank` are copied; the two rates are computed from counts
# the scanner reported. No threshold of the scanner's is restated here.
OUTCOME_KEYS = ("warn_per_100_lines", "marker_per_100_lines",
                "sentence_mean", "sentence_pressure")
GUARD_KEY = "prose_share_of_nonblank"


class ScanFailed(RuntimeError):
    """scan_register exited non-zero. Its findings are not a measurement."""


def scan(paths, terms=None):
    """Return scan_register's --json payload for *paths*.

    The scanner's own `main` is called, so a threshold or a rule changed in
    `data/register-*.json` reaches this grader with no edit here.
    """
    argv = [str(p) for p in paths] + ["--json"]
    for t in terms or ():
        argv += ["--terms", str(t)]
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = scan_register.main(argv)
    if rc != 0:
        raise ScanFailed(f"scan_register exited {rc}: "
                         f"{err.getvalue().strip()[:400]}")
    return json.loads(out.getvalue())


def _only_diag(payload):
    """Return the single per-file diagnostics block, or raise."""
    diags = payload.get("diagnostics") or {}
    if len(diags) != 1:
        raise ScanFailed(f"expected one file, scanned {len(diags)}")
    return next(iter(diags.values()))


def score_document(path, terms=None):
    """Return the five values TASK 101 R2 names, plus the counts behind them.

    `measured` is False when the document has no line to measure or when its
    prose share falls below PROSE_FLOOR. The values are still reported, so a
    reader sees what was rejected and why.
    """
    payload = scan([path], terms)
    diag = _only_diag(payload)
    findings = list(payload.get("warn") or ()) + list(payload.get("info") or ())
    lines = diag.get("lines") or 0
    warn_count = len(payload.get("warn") or ())
    marker_count = sum(1 for f in findings if f.get("kind") == "marker")
    guard = diag.get(GUARD_KEY, 0)

    if lines <= 0:
        reason = "the document holds no line"
    elif lines < MIN_LINES:
        reason = (f"{lines} line(s), under the {MIN_LINES}-line floor; "
                  f"this is a failed run, not a document")
    elif guard < PROSE_FLOOR:
        reason = (f"prose reaching rule 1 is {guard}%, "
                  f"under the {PROSE_FLOOR}% floor")
    else:
        reason = None

    return {
        "path": os.path.relpath(path, HERE),
        "measured": reason is None,
        "unmeasured_reason": reason,
        "warn_per_100_lines": round(warn_count / lines * 100, 2) if lines else None,
        "marker_per_100_lines": round(marker_count / lines * 100, 2) if lines else None,
        "sentence_mean": diag.get("sentence_mean"),
        "sentence_pressure": diag.get("sentence_pressure"),
        GUARD_KEY: guard,
        "counts": {
            "lines": lines,
            "nonblank_lines": diag.get("nonblank_lines"),
            "warn": warn_count,
            "marker": marker_count,
            "sentences": diag.get("sentences"),
            "sentence_max_observed": diag.get("sentence_max_observed"),
            "language": diag.get("language"),
            "findings_by_kind": diag.get("findings_by_kind") or {},
        },
    }


def score_axis_b(reported, key):
    """Score one reading-pass answer against a key written before the run.

    *reported* is a list of `{"line": int, "rule": int}`. A planted defect is
    matched when a reported entry names its rule and falls in its line set.
    """
    planted = list(key.get("planted") or ())
    seen, matched, spurious = set(), [], []
    for r in reported:
        try:
            line, rule = int(r["line"]), int(r["rule"])
        except (KeyError, TypeError, ValueError):
            spurious.append(r)
            continue
        hit = next((p for p in planted
                    if int(p["rule"]) == rule and line in p["lines"]), None)
        if hit is None:
            spurious.append(r)
        else:
            seen.add(hit["id"])
            matched.append({"id": hit["id"], "line": line, "rule": rule})

    missed = [p["id"] for p in planted if p["id"] not in seen]
    recall = 1.0 if not planted else round(len(seen) / len(planted), 3)
    precision = (1.0 if not reported
                 else round((len(reported) - len(spurious)) / len(reported), 3))
    return {
        "recall": recall,
        "precision": precision,
        # A key with nothing planted cannot fail recall. Saying so stops a
        # control case from inflating an aggregate it never measured.
        "vacuous_recall": not planted,
        "planted": len(planted),
        "reported": len(reported),
        "matched": matched,
        "missed": missed,
        "spurious": spurious,
    }


def _mean(values):
    vals = [v for v in values if isinstance(v, (int, float))]
    return round(sum(vals) / len(vals), 2) if vals else None


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def grade(evals, run_dir, terms=None):
    """Grade a completed campaign. Pure in (evals, run_dir) and the rule files."""
    cases, empty, unmeasured = [], [], []
    # Both arms are seeded whenever the set holds an authoring case. An arm
    # whose every document was empty or unmeasured would otherwise vanish from
    # the summary, and a one-armed table reads as a comparison.
    per_arm = {arm: [] for arm in ("baseline", "with_contract")
               if any(c.get("axis") == "authoring"
                      for c in evals.get("cases", []))}

    for case in evals.get("cases", []):
        if case.get("axis") == "authoring":
            for arm in ("baseline", "with_contract"):
                arm_dir = os.path.join(run_dir, case["id"], arm)
                reps = sorted(f for f in os.listdir(arm_dir)
                              if f.startswith("rep-") and f.endswith(".md")
                              ) if os.path.isdir(arm_dir) else []
                if not reps:
                    empty.append(f"{case['id']}/{arm}: no rep-*.md")
                    continue
                for rep in reps:
                    path = os.path.join(arm_dir, rep)
                    if os.path.getsize(path) == 0:
                        empty.append(f"{case['id']}/{arm}/{rep}: empty output")
                        continue
                    # The executor already knows the run failed and records it.
                    # Reading the file without reading its metadata graded two
                    # 80-byte transport errors as conforming documents: a
                    # one-line error string scores zero on every register
                    # metric, which is the clean-looking zero this whole skill
                    # exists to catch.
                    meta_path = os.path.join(arm_dir, rep[:-3] + ".meta.json")
                    meta = (_load_json(meta_path)
                            if os.path.isfile(meta_path) else {})
                    if meta.get("is_error"):
                        empty.append(f"{case['id']}/{arm}/{rep}: the executor "
                                     f"recorded is_error for this run")
                        continue
                    row = score_document(path, terms)
                    row.update(case_id=case["id"], arm=arm, rep=rep,
                               axis="authoring", lang=case.get("lang"),
                               artifact_kind=case.get("artifact_kind"))
                    cases.append(row)
                    if not row["measured"]:
                        unmeasured.append(
                            f"{case['id']}/{arm}/{rep}: {row['unmeasured_reason']}")
                    else:
                        per_arm.setdefault(arm, []).append(row)
        elif case.get("axis") == "recall_gap":
            case_dir = os.path.join(run_dir, case["id"])
            # Repetitions live in rep-N/ directories. A single `answer.json`
            # directly under the case is the pre-repetition layout and is read
            # as rep-1, so an older corpus still grades.
            reps = []
            if os.path.isdir(case_dir):
                reps = sorted((d, os.path.join(case_dir, d, "answer.json"))
                              for d in os.listdir(case_dir)
                              if d.startswith("rep-")
                              and os.path.isfile(os.path.join(case_dir, d,
                                                              "answer.json")))
                if not reps and os.path.isfile(
                        os.path.join(case_dir, "answer.json")):
                    reps = [("rep-1", os.path.join(case_dir, "answer.json"))]
            if not reps:
                empty.append(f"{case['id']}: no answer.json")
                continue
            key = _load_json(os.path.join(HERE, case["key"]))
            for rep, answer in reps:
                payload = _load_json(answer)
                # The executor writes `{"findings": [...]}`; a hand-written
                # answer may be the bare list. An answer the model returned
                # unparsably is stored with an empty findings list, and it is
                # named here — a zero from a broken answer must not read as a
                # pass with no findings.
                if isinstance(payload, dict):
                    reported = payload.get("findings", [])
                    if "unparsable" in payload:
                        empty.append(f"{case['id']}/{rep}: the answer did not "
                                     f"parse as JSON")
                else:
                    reported = payload
                row = score_axis_b(reported, key)
                row.update(case_id=case["id"], axis="recall_gap", rep=rep,
                           rule=case.get("rule"),
                           control=bool(case.get("control")))
                cases.append(row)

    arms = {arm: {k: _mean([r[k] for r in rows]) for k in OUTCOME_KEYS
                  if k != "sentence_pressure"}
            for arm, rows in per_arm.items()}
    for arm, rows in per_arm.items():
        arms[arm]["documents"] = len(rows)
        arms[arm]["pressed_against_limit"] = sum(
            1 for r in rows if r.get("sentence_pressure"))
        arms[arm][GUARD_KEY] = _mean([r[GUARD_KEY] for r in rows])
        # The absolute counts ride beside the rates. Two arms can produce
        # documents of very different length, and a rate alone cannot say
        # whether a difference is fewer findings or a shorter document.
        arms[arm]["warn_total"] = sum(r["counts"]["warn"] for r in rows)
        arms[arm]["lines_total"] = sum(r["counts"]["lines"] for r in rows)
        arms[arm]["sentence_max_worst"] = max(
            (r["counts"]["sentence_max_observed"] or 0 for r in rows),
            default=0)
        by_kind = {}
        for r in rows:
            for kind, n in r["counts"]["findings_by_kind"].items():
                by_kind[kind] = by_kind.get(kind, 0) + n
        arms[arm]["findings_by_kind"] = dict(sorted(by_kind.items()))

    gaps = [c for c in cases if c.get("axis") == "recall_gap"]
    seeded = [c for c in gaps if not c.get("control")]
    controls = [c for c in gaps if c.get("control")]

    return {
        "schema": "formalizer-grading/v1",
        "prose_floor": PROSE_FLOOR,
        "arms": arms,
        "axis_b": {
            "seeded_cases": len(seeded),
            "recall_mean": _mean([c["recall"] for c in seeded]),
            "precision_mean": _mean([c["precision"] for c in seeded]),
            "control_spurious": sum(len(c["spurious"]) for c in controls),
        },
        "empty": empty,
        "unmeasured": unmeasured,
        "cases": cases,
    }


def summarize(doc):
    """Return the printed summary. It names what was NOT measured."""
    out = [f"cases graded        : {len(doc['cases'])}"]
    for arm in sorted(doc["arms"]):
        a = doc["arms"][arm]
        if not a["documents"]:
            out.append(f"  {arm:<14}: 0 docs — NOT MEASURED, this arm has no "
                       f"document the grader accepted")
            continue
        out.append(
            f"  {arm:<14}: {a['documents']} docs  "
            f"warn/100L {a['warn_per_100_lines']}  "
            f"marker/100L {a['marker_per_100_lines']}  "
            f"sent.mean {a['sentence_mean']}  "
            f"prose {a[GUARD_KEY]}%  "
            f"pressed {a['pressed_against_limit']}")
        out.append(
            f"  {'':<14}  {a['warn_total']} warn over {a['lines_total']} "
            f"lines, longest sentence {a['sentence_max_worst']} words, "
            f"{a['findings_by_kind']}")
    b = doc["axis_b"]
    out.append(f"  recall gaps   : {b['seeded_cases']} seeded  "
               f"recall {b['recall_mean']}  precision {b['precision_mean']}  "
               f"control false positives {b['control_spurious']}")
    out.append(f"empty outputs       : {len(doc['empty'])}")
    out.extend(f"  {e}" for e in doc["empty"])
    out.append(f"unmeasured cases    : {len(doc['unmeasured'])}")
    out.extend(f"  {u}" for u in doc["unmeasured"])
    if not doc["arms"]:
        out.append("NO ARM HAS A MEASURED DOCUMENT — this is not a measurement")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Grade an artifact-formalizer eval campaign "
                    "(deterministic; spawns no agent)")
    ap.add_argument("--evals", default=os.path.join(HERE, "evals.json"))
    ap.add_argument("--run-dir", default=os.path.join(HERE, "corpus"))
    ap.add_argument("--terms", action="append", dest="terms")
    ap.add_argument("--out", default=None, help="write grading.json here")
    ap.exit_on_error = False
    try:
        args = ap.parse_args(argv)
    except (argparse.ArgumentError, SystemExit) as exc:
        code = getattr(exc, "code", 1)
        return 0 if code == 0 else 3

    if not os.path.isfile(args.evals):
        print(f"usage error: no eval file at {args.evals}", file=sys.stderr)
        return 3
    if not os.path.isdir(args.run_dir):
        print(f"usage error: no run directory at {args.run_dir}",
              file=sys.stderr)
        return 3

    try:
        doc = grade(_load_json(args.evals), args.run_dir, args.terms)
    except ScanFailed as exc:
        print(f"broken instrument: {exc}", file=sys.stderr)
        return 2
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"broken instrument: malformed key or answer: {exc}",
              file=sys.stderr)
        return 2

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh_note = f"\nwritten: {args.out}"
    else:
        fh_note = ""
    print(summarize(doc) + fh_note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
