# Task 095.6 — Adversarial cycle: find-all-sites and a real brief

<!--
  Anchors below (`<!-- contract:* -->`) are how a MACHINE addresses a section:
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
-->

## Use Case Connection
- UC-3: Orchestrator fixes an assertion mid-cycle
- Covers `R9`, `R10` — WI-32

<!-- contract:goal -->

## Task Goal
Stop the cycle from paying a full critic pass to discover that a fix landed in one site of four,
and give the thing §4.4 already hands to the next cycle somewhere to land.

<!-- contract:changes -->

## Changes Description
### Changes in Existing Files
- **`.agent/workflows/vdd-enhanced.md` §4** — items **6** and **7**, APPENDED.
  Item 6: search before editing; report `fixed N of M found`; `N < M` is legitimate, silence is
  not; repeated wording prefers one declaration with readers.
  Item 7: the Cycle Brief is a real input; omitting the block is itself a finding.
- **`.agent/workflows/vdd-adversarial.md` step 2a** — the **Cycle Brief** block, modelled on
  `vdd-multi`'s execution-evidence skeleton, with the instruction to verify the RATIO by re-running
  the search rather than trusting the claim.

<!-- contract:tests -->

## Test Cases
No automated test — `smoke_workflows.py` asserts existence and call targets, not §4's content.
Verification is the ordinal check plus `check_positional_refs.py` in T-095-10.

<!-- contract:acceptance -->

## Acceptance Criteria
- [ ] §4 items 1–5 keep their ordinals (verified: 4 and 5 unmoved)
- [ ] the brief block names both carried-over kinds
- [ ] a missing block is a finding, and an explicit `NONE` is not
- [ ] `smoke_workflows.py --root .` exit 0

## Notes
**Appended, never inserted.** `docs/design/095_workflow_loop_contract.md` and three ledger lines
in the reporting project cite §4.4/§4.5 by ordinal. Inserting a new item fourth would shift five
references across two repositories — reproducing WI-32's exact failure mode inside WI-32's own fix.

M for this task was established by grep before editing: the rule text lives in exactly **one** live
file. The other three hits are a changelog entry, an archived audit, and a design spec quoting it —
records, not instructions. **Fixed 1 of 1 found.**
