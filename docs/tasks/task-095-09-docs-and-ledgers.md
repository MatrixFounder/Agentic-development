# Task 095.9 — System/Docs, CHANGELOG, ledgers

<!--
  Anchors below (`<!-- contract:* -->`) are how a MACHINE addresses a section:
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
-->

## Use Case Connection
- Covers `R13`

<!-- contract:goal -->

## Task Goal
Make the documentation describe what now exists, and close the three work-items against what
actually landed.

<!-- contract:changes -->

## Changes Description
### Changes in Existing Files
- **`System/Docs/SKILLS.md`** — rows for `documentation-standards`, `skill-spec-validator`,
  `known-issues-format`, `developer-guidelines`.
- **`System/Docs/WORKFLOWS.md`** — the VDD Enhanced row.
- **`CHANGELOG.md`** (+ `.ru`) — a new entry. Existing entries are historical records and are
  **not** edited.
- **`onchain-analytics`** — WI-30 / WI-31 / WI-32 closed with `resolved_by` naming this repo and
  the landed edit.

<!-- contract:tests -->

## Test Cases
Not applicable.

<!-- contract:acceptance -->

## Acceptance Criteria
- [ ] every changed skill's description matches its new content
- [ ] the changelog entry states what did NOT ship as well as what did
- [ ] each work-item's resolution is verified against the landed diff, not against intent

## Notes
`known-issues-format`: *"sent for review is not closed"* — verify with `git diff` in the target
repo before writing a resolution. This task's residual risk, recorded in the Mode B audit: that
verification is a human read, not a gate, because the reporting project's suite does not run here.
