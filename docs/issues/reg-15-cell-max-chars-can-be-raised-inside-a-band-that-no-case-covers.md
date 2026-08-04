---
id: REG-15
type: known-issue
status: fixed
opened_at: 2026-08-04
category: register
severity: SEV-3
slug: reg-15-cell-max-chars-can-be-raised-inside-a-band-that-no-case-covers
component: '.agent/skills/artifact-formalizer/data/register-en.json'
resolved_at: 2026-08-04
resolved_by: TASK 100
---

# REG-15 — `cell_max_chars` can be raised inside a band that no case covers

> **Resolved 2026-08-04 by TASK 100.** `SHIPPED_THRESHOLDS` pins all four keys each rule file
> declares, and `SHIPPED_DEFAULTS` pins the six the scanner falls back to — including
> `sentence_pressure_band` and `cell_prose_chars`, which no rule file states. This record's own
> reproduction fails `TC-100-04` in both languages, and moving a default fails `TC-100-05`.

**Component:** `.agent/skills/artifact-formalizer/data/register-en.json`

## Symptom

`TC-SHIP-02` pins `sentence_max_words` only, and `_structural_probes` builds the `cell_width`
fixture from `cell_max_chars` itself, so the roster fixture moves with the threshold and cannot
notice a change. Values above roughly 200 are caught incidentally by `TC-PREC-01`/`TC-PREC-02`;
the band between is uncovered.

## Reproduction

Set `thresholds.cell_max_chars` to 150 in both `data/register-en.json` and `data/register-ru.json`.
Measured over the 631 tracked `.md` files: `cell_width` findings fall from 811 to 613, a loss of
198, while `selftest_scan.py` reports `174/174 passed` exit 0 and `scan_register.py --probe`
reports `18/18 detectors live` exit 0.

## Provenance

Found by the adversarial verification of TASK 099, 2026-08-04, and independently reproduced by the
orchestrator before filing. Each is the class TASK 099 closed elsewhere: a gate that reports a clean
instrument while a detector is gone. None is the symptom any `REG-2`…`REG-13` record states, so
TASK 099 recorded them here rather than widening its own scope (TASK 099 OQ-2).
