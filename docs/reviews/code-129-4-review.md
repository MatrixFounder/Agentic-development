# Code Review: Task 129.4 — the records and the check of the architecture

- **Date:** 2026-10-27
- **Reviewer:** `code-reviewer` (subagent), `03-develop-single-task` step 4.
- **Status:** APPROVED, MERGE. 0 BLOCKING, 0 MAJOR, 6 MINOR.
- **Reviewed:** the diff of `CHANGELOG.md`, `CHANGELOG.ru.md`, RF-22 of
  `.agent/skills/mermaid-authoring-guidelines/references/renderer-facts.md`, the WI-41 record,
  `docs/BACKLOG.md`, `docs/ARCHITECTURE.md` and `tests/test_session_state_contract.py`, at tree
  fingerprint `f396d3e711c0`. The reviewer quoted it; the orchestrator recomputed the same value at
  the return. The reviewer planted in copies outside the repository and removed them.
- **Kept by:** the orchestrator, from the reviewer's hand-back.

## Assessment

The diff matches the task file. `docs/ARCHITECTURE.md` changes in three places only: lines 120 and
215, and §10.7 (R4.3). Every number, version, date and name of the records matches TASK §8, D4 and
D9 and the evidence of Task 129.3. WI-41 stays `open`, with its front matter and its earlier body
unchanged. RF-21 and the WI-30 record are byte-identical to the base, and the disclosure test
passes. The two changelogs state the same versions, IDs and numbers.

## Comments

### BLOCKING

None.

### MAJOR

None.

### MINOR

| ID | Pillar | Finding | Answer |
| :--- | :--- | :--- | :--- |
| 1 | Compliance | The WI-41 progress said that TASK §8 "lists the rest"; §8 counts them | it states the counts: 13, 5 and 21 |
| 2 | Compliance | The changelog heading says the advisories close; the critical GHSA-cg2g-xh64-v4q7 still covers the copies of DOMPurify 3.4.12 | the Notes of both changelogs name it |
| 3 | Compliance | The index line of WI-41 said "the copies" with nothing to refer back to | "the lockfiles audit clean; the bundled DOMPurify and KaTeX copies still run" |
| 4 | Quality | The first observation of RF-22 kept the present tense of 2026-10-05 | it carries its date and TASK 110 |
| 5 | Quality | RF-22 named the base by its puppeteer alone | "of the base lockfiles" |
| 6 | Testing | The module docstring of TC-C7 did not name the lock file | it names the lock file and TASK 129 R4.1 |

**Before the task:** `docs/PLAN.md` cited TASK revision 5; the TASK is at revision 6. Corrected.

**Measured after the fixes:** byte scans clean; the register scan finds no warning on an added line;
`tests/test_session_state_contract.py` and `tests/test_disclosure_rule.py`, `23 passed`.

## Verified (clean pass)

- **Requirements checked:** R4.1–R4.3, R6.1, R6.2, R6.4, R6.5; A6, A8; D4, D9, §8.
- **Edge cases considered:** the entry counts with the root key; a release of a plugin newer than
  DOMPurify 3.4.17 (none: zenuml 1.0.1 and layout-elk 1.0.1 predate it); the position of the
  index line between the anchor and `## Closed`; living citations of the architecture above each
  hunk that changes the line count.
- **Tests observed:** TC-C7 on copies: the control passes, and the base text of line 120 or of line
  215 fails; no other test reads these lines. The local gates: `20 of 20 steps pass`.

`{"review_status": "APPROVED", "has_critical_issues": false, "e2e_tests_pass": true, "stubs_replaced": true}`
