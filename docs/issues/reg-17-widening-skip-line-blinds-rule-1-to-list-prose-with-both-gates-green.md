---
id: REG-17
type: known-issue
status: fixed
opened_at: 2026-08-04
category: register
severity: SEV-3
slug: reg-17-widening-skip-line-blinds-rule-1-to-list-prose-with-both-gates-green
component: '.agent/skills/artifact-formalizer/scripts/scan_register.py'
resolved_at: 2026-08-04
resolved_by: TASK 100
---

# REG-17 — Widening `SKIP_LINE` blinds rule 1 to list prose with both gates green

> **Resolved 2026-08-04 by TASK 100.** Every rule-1 and rule-3 fixture runs in two line forms, a
> bare line and a `- ` list item, and a kind is live only when both fire. This record's own
> reproduction now exits 2 at `12/18 detectors live` with `sentence_length`, `sentence_near_limit`
> and `reasoning` DEAD in both languages, and fails `TC-100-11`. The roster stays at 18 rows: the
> forms are per row, not rows of their own (TASK 100 D3).

**Component:** `.agent/skills/artifact-formalizer/scripts/scan_register.py`

## Symptom

The structural probe fixtures are bare sentences, never list items, so the roster cannot observe a
`SKIP_LINE` that swallows list markers. Most prose in this repository's documents is written as
list items.

## Reproduction

Add `[-*+]\s|` to the `SKIP_LINE` alternation at `scan_register.py:525@23827c1`. Measured over the 631
tracked `.md` files: total findings fall from 4,831 to 4,352 — `sentence_length` 824 -> 546,
`sentence_near_limit` 714 -> 519, `reasoning` 22 -> 16 — while `selftest_scan.py` reports
`174/174 passed` exit 0 and `scan_register.py --probe` reports `18/18 detectors live` exit 0.

## Provenance

Found by the adversarial verification of TASK 099, 2026-08-04, and independently reproduced by the
orchestrator before filing. Each is the class TASK 099 closed elsewhere: a gate that reports a clean
instrument while a detector is gone. None is the symptom any `REG-2`…`REG-13` record states, so
TASK 099 recorded them here rather than widening its own scope (TASK 099 OQ-2).
