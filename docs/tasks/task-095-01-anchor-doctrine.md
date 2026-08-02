# Task 095.1 — Anchor doctrine and registry

<!--
  Anchors below (`<!-- contract:* -->`) are how a MACHINE addresses a section:
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
-->

## Use Case Connection
- UC-2: Author writes a new TASK
- Covers `R1`, registry half of `R4`

<!-- contract:goal -->

## Task Goal
State the rule that makes every later step legible, and reserve the anchor names, BEFORE any
script reads one. Implementing a reader first is how the second one-off gets created — which is
exactly how this defect reached three files.

<!-- contract:changes -->

## Changes Description
### Changes in Existing Files

**`.agent/skills/documentation-standards/SKILL.md`** (TIER 1)
- Add §4.3 — the third rung of the §4.1 addressing ladder: a reference can be nominal and still
  break, because it names its target in a LANGUAGE. Syntax, lookup semantics, compatibility rule.
- Add §4.4 — the reserved-anchor registry (14 rows, `Consumer` column, `—` = reserved, no reader).
- Bump `version` 1.6 → 1.7.

**`.agent/skills/known-issues-format/SKILL.md`** (TIER 2)
- Note under the backlog grouping rule: its own "a comment, not a heading" reasoning is now
  framework-wide doctrine; it owns 3 registry rows. Bump `version` 2.0 → 2.1.

**`docs/ARCHITECTURE.md`**
- §7 split into §7.1 (framework language) and §7.2 (project language ≠ framework language),
  carrying invariant **L1**: a machine gate never depends on the natural language of the document
  it judges. §7 previously modelled localization as *translating the framework*, which is a
  different problem from *the project's own artifacts being in another language*.

<!-- contract:tests -->

## Test Cases
No new automated test: this task adds no executable behaviour. Its verification is that
`check_contract_sync.py` and `validate_skills.py` stay green, and that every anchor emitted by
T-095-03 resolves to a registry row.

<!-- contract:acceptance -->

## Acceptance Criteria
- [ ] §4.3 states the rule as a RULE, with the failure mode, not as a tip
- [ ] §4.4 lists every anchor any later task emits
- [ ] `check_contract_sync.py` exit 0
- [ ] `validate_skills.py --root . --quiet` exit 0

## Notes
Ordering: strictly before T-095-02. The anchor's spelling is a contract, and a reader written
against an unregistered name is the defect this task exists to stop.
