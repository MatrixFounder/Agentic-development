# Task 095.2 — Validator: anchor lookup and positional columns

<!--
  Anchors below (`<!-- contract:* -->`) are how a MACHINE addresses a section:
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
-->

## Use Case Connection
- UC-1 + Alt A + Alt B
- Covers `R2`, `R3`, `R6`

<!-- contract:goal -->

## Task Goal
Make `skill-spec-validator` pass on a non-English RTM **in both modes**, without changing the
verdict on a single document that exists today.

<!-- contract:changes -->

## Changes Description
### Phase 1 — `[STUB CREATION]` (Red)
- `scripts/tests/test_anchor.py` — non-English fixture asserted in `--mode task` AND `--mode plan`,
  anchor-beats-prose, duplicate anchor, anchor-without-table, single-column table, and two
  compatibility guards. Observed FAILING before any logic (7 of 9).

### Phase 2 — `[LOGIC IMPLEMENTATION]` (Green)
**`scripts/validate.py`**
- `ANCHOR_RTM`, `_anchor_block()`, `_table_columns()`, `locate_rtm()`.
- `validate_task` and `validate_plan` both delegate to `locate_rtm()` — they held two copies of
  the same logic and each fix landed in only one of them.
- Anchor path reads the table POSITIONALLY (first column = id). Anchorless path keeps the
  `['ID','Requirement']` contract byte-for-byte.
- Both fallback errors now name the anchor as the remedy.

<!-- contract:tests -->

## Test Cases
### End-to-end
1. **TC-E2E-01** Russian RTM + anchor → `--mode task` exit 0.
2. **TC-E2E-02** same document → `--mode plan` exit 0. *Separate test on purpose: this path fails
   independently of the column check, so one test could not have caught both.*
3. **TC-E2E-03** plan missing an id → still exit 1 (positional reading is not a rubber stamp).

### Regression
- The 38 pre-existing tests, unchanged.
- `tests/test_corpus.py` liveness floors, unchanged.
- Corpus pass counts re-measured in both repositories.

<!-- contract:acceptance -->

## Acceptance Criteria
- [ ] 47 skill tests + 4 root tests green
- [ ] framework `docs/tasks/` pass count ≥ 30/113 (measured before: 30)
- [ ] onchain-analytics `docs/tasks/` pass count ≥ 10/50 (measured before: 10)
- [ ] the reported document passes with ONE anchor line added
- [ ] `RTM_HEADER` byte-identical; `test_split_on_the_heading_is_non_capturing` green

## Notes
The anchor is deliberately a SEPARATE pattern, never an alternation inside `RTM_HEADER`:
`test_validate.py` pins `RTM_HEADER.split()` at exactly two parts, and `test_corpus.py` pins that
the matcher is never narrowed. Additive in both senses.
