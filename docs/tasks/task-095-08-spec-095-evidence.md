# Task 095.8 — Spec 095: field evidence and independent review

<!--
  Anchors below (`<!-- contract:* -->`) are how a MACHINE addresses a section:
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
-->

## Use Case Connection
- Covers `R11`, `R12`

<!-- contract:goal -->

## Task Goal
Give design spec 095 what its own Phase-5 entry gate asks for — field evidence — and an
independent adversarial read, WITHOUT committing to build any of its components here.

<!-- contract:changes -->

## Changes Description
### Changes in Existing Files
- **`docs/design/095_workflow_loop_contract.md`** — a field-evidence section appended, answering
  the §7.1 entry-gate questions from WI-30 and WI-31 rather than from argument.

### New Files
- **`docs/reviews/review-095-independent.md`** — multi-lens critique (fact-check of the spec's
  claims about the repo, contract-grammar design, YAGNI/scope, ops+portability), each CRITICAL and
  HIGH finding put through an adversarial refutation pass before being reported.

<!-- contract:tests -->

## Test Cases
Not applicable — no executable behaviour. The check is `git status`: **no `run_stack.py` and no
`check_loop_contract.py` may appear.**

<!-- contract:acceptance -->

## Acceptance Criteria
- [ ] evidence recorded against the §7.1 questions it answers
- [ ] the review names blocking findings, factual corrections, and the strongest scope challenge
- [ ] neither Component B nor C is implemented by this task

## Notes
**Why evidence and not implementation.** WI-30's journaling half and WI-31's modes 1 and 3 both
need one mechanism: a wrapper that RUNS the command, so it owns the true exit code, records the
invocation verbatim, and makes "did not run" a distinguishable state. That is `run_stack.py gate`,
already designed in 095 Component C. Building a second one beside it would be waste — and 095 is
under review precisely because it is not ready to be built from.
