#!/usr/bin/env python3
"""Per-RULE verdict: which SKILL.md instructions earn their tokens?

Aggregates per-check pass rates across arms and maps every check onto the SKILL.md rule it
exercises. The output classifies each rule:

  LOAD-BEARING  baseline fails it, skill passes it — the rule encodes something the model
                does not do on its own. Keep.
  DEAD-WEIGHT   both arms pass — the CLI + ledger format already force this behaviour, or
                the model does it unprompted. The instruction buys nothing; candidates for
                deletion (context cost with zero behavioural delta).
  HARMFUL       skill arm fails where baseline passes — the instruction actively degrades
                behaviour. Delete immediately.
  BROKEN-BOTH   both arms fail — either the rule is unteachable by prompt, or the CASE is
                measuring something else (inspect before concluding).

Caveat printed with the table: a DEAD-WEIGHT verdict is relative to THIS baseline, which
already ships the CLI (--help) and the known-issues-format skill. It answers "does this line
change behaviour for a strong model with the tooling present", not "would a weak model with
no tooling need it".

    python3 analyze_rules.py --workspace <ws>/iteration-3
"""
from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict
from pathlib import Path

# check-text keywords -> the SKILL.md rule under test. Keyed by (case, salient substring).
RULES = [
    ("§7.1 'MUST run triage first' + RF#3 'classify straight from inbox'",
     ["ran the `triage` subcommand", "ran `triage` despite"]),
    ("§7.2 duplicate -> dismiss with original's ID + RF#2 'file it anyway'",
     ["dismissed as noise with a reason naming", "duplicate", "gained no new issue",
      "second issue was filed"]),
    ("§7.2 counterpart: title-overlap that is NOT a dup must still be filed",
     ["citing the MacWhisper detail", "rather than suppressed", "suppressed as a duplicate"]),
    ("§7.4 severity strictly from SEV-2/3/4/LOW + RF#4 invented vocab",
     ["severity is one of", "severity token", "status is from the write vocabulary"]),
    ("§7.5 'MUST dry-run, read the preview, then run for real' + RF#5",
     ["dry-run"]),
    ("RF#1 lockstep / never hand-edit the ledger; §5 create-only",
     ["mutated only by the CLI", "hand edit", "hand-edit", "lockstep", "half-written",
      "hand-editing the ledger"]),
    ("§7.4 auto-fixable ONLY with a real gate + table row 'mark only mechanical'",
     ["auto_fixable", "auto-fixable", "heal harness"]),
    ("§7.4 'MUST make Reproduction a fenced sh block'",
     ["Reproduction section is a fenced"]),
    ("Retro §1 claim exit 6 = nested -> SKIP + table row 'exit 6 is an error I should fix'",
     ["exit 6", "denied claim", "retry-loop the claim", "forced the retro"]),
    ("Retro §5 non-blocking guarantee + RF#7 'retry it / fail the workflow'",
     ["verdict as passing despite the retro", "green workflow into a failed",
      "retry-loop the failing", "surfaced in the report"]),
    ("§7 Bootstrap: init -> finish todo -> doctor clean -> resume",
     ["init` subcommand", "re-ran `doctor`", "real config file", "EMPTY remediation",
      "backlog anchor now exists", "before the repo was bootstrapped"]),
    ("§7.3 noise = transient env -> dismiss with reason",
     ["dismissed as noise with a reason", "transient", "curl finding"]),
    ("§7.3 work-item = no broken contract -> backlog",
     ["work-item into the backlog", "bullet was appended", "polish request"]),
    ("Retro §2/§13 clean run -> file NOTHING (over-firing guard)",
     ["fabricated into the inbox", "nothing was filed", "invented a defect"]),
    ("RF#6 / table 'inbox item is obviously noise, delete the JSON' — CLI-only inbox",
     ["inbox JSON was never hand-edited", "token was re-introduced"]),
    ("§7.6 report the missing prefix→category row (edit is the human's)",
     ["prefix→category table row", "prefix->category"]),
    ("(cross-cutting) filing lands in the production feed (gate parity)",
     ["issues feed", "parses the new issue", "ledger once the repo", "reached the issues ledger",
      "filed as a defect", "filed through the `file`", "Exactly one new issue",
      "recorded rather than silently dropped"]),
]


def rule_for(text: str) -> str:
    for rule, keys in RULES:
        if any(k.lower() in text.lower() for k in keys):
            return rule
    return "(unmapped)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    args = ap.parse_args()

    # (rule, arm) -> [passed…]
    tally = defaultdict(list)
    detail = defaultdict(lambda: defaultdict(list))  # rule -> case -> [(arm, passed)]

    for p in sorted(glob.glob(str(args.workspace / "runs/eval-*/*/run-*/grading.json"))):
        g = json.loads(Path(p).read_text())
        for e in g["expectations"] + g["forbidden_expectations"]:
            rule = rule_for(e["text"])
            tally[(rule, g["arm"])].append(e["passed"])
            detail[rule][g["eval_id"]].append((g["arm"], e["passed"]))

    rows = []
    for rule in {r for (r, _) in tally}:
        w = tally.get((rule, "with_skill"), [])
        b = tally.get((rule, "without_skill"), [])
        wr = sum(w) / len(w) if w else None
        br = sum(b) / len(b) if b else None
        if wr is None or br is None:
            verdict = "NO-DATA"
        elif wr >= 0.99 and br >= 0.99:
            verdict = "DEAD-WEIGHT"
        elif wr - br >= 0.15:
            verdict = "LOAD-BEARING"
        elif br - wr >= 0.15:
            verdict = "HARMFUL"
        elif wr < 0.99 and br < 0.99:
            verdict = "BROKEN-BOTH"
        else:
            verdict = "MARGINAL"
        rows.append((verdict, rule, wr, br, len(w), len(b)))

    order = {"HARMFUL": 0, "LOAD-BEARING": 1, "BROKEN-BOTH": 2, "MARGINAL": 3,
             "DEAD-WEIGHT": 4, "NO-DATA": 5}
    rows.sort(key=lambda r: (order[r[0]], r[1]))

    print(f"{'verdict':<13} {'with':>6} {'base':>6} {'n':>5}  rule")
    print("-" * 110)
    for verdict, rule, wr, br, nw, nb in rows:
        print(f"{verdict:<13} {wr:>6.2f} {br:>6.2f} {nw:>2}/{nb:<2}  {rule[:80]}")

    print("\nCaveat: DEAD-WEIGHT is relative to THIS baseline (CLI --help + known-issues-format"
          "\npresent, current-generation model). It licenses trimming the SKILL.md text, not"
          "\ndeleting the underlying CLI checks.")
    return 0


if __name__ == "__main__":
    main()
