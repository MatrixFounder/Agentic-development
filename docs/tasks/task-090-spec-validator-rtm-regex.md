# Technical Specification: [LIGHT] Make skill-spec-validator RTM gate match the real heading/ID conventions

### 0. Meta Information
- **Task ID:** 090
- **Slug:** `spec-validator-rtm-regex`
- **Mode:** Light (single-file, low-risk bugfix; no API/schema/deps changes)

### 1. Problem Description
`.agent/skills/skill-spec-validator/scripts/validate.py` gates Step-1/Planning validation on
an RTM heading + per-requirement PLAN coverage. Both matchers were written for a format that
**no shipped artifact uses**, so the gate fails on 100% of current TASK/PLAN files and is, in
practice, dead. The house writes the RTM heading in ≥6 shapes — two-hash and three-hash, with a
section number, with a trailing `(RTM)`, and the newest form `### N. Requirements (RTM)` (no word
"Traceability" at all). The prior working-tree patch relaxed the regex but its `$` anchor + fixed
`##` still matched none of them. Fix the matcher to the shapes actually in the repo.

### 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | Verify |
|----|-------------|--------|
| R1 | RTM heading matcher accepts h2–h4 (`##`–`####`), an optional section number (`2.` / `3)`), a trailing `(RTM)`, and both `Requirements Traceability [Matrix]` and the bare `Requirements (RTM)` form. | Validator passes in `task` mode on task-085, task-088 and `docs/TASK.md`. |
| R2 | Section extraction (`RTM_HEADER.split`) stays consistent with the matcher — no capturing groups leak into the split, table checks (non-empty, `ID`+`Requirement` cols) unchanged. | task-mode `Success: Found N requirements` on the real files. |
| R3 | PLAN coverage check matches each RTM ID as a whole token anywhere in the plan body — the corpus references IDs in both `- [ ]` bullets and `## Step N (R1, R2)` headings — with no `R1`⊂`R10` false positives, IDs normalised of markdown emphasis. A genuinely un-referenced ID is reported as a real gap. | Validator passes in `plan` mode on conformant pairs (e.g. 087→after fix); `R1` does not spuriously match `R10`; a plan omitting an ID is flagged. |
| R4 | No behavioural regression to the bypass escape, empty-table error, or CLI surface. | Bypass flag still exits 0; empty/invalid table still exits 1. |

### 3. Out of scope
Redesigning the RTM/ID authoring convention itself, or adding a unit-test harness/CI. Changes are
confined to `validate.py` plus a doc-sync of the skill's own `SKILL.md` (Checks descriptions) so the
documentation matches the corrected behaviour — no other files.

### 4. Constraints
- stdlib-only Python 3.9+ (`re`, `sys`, `os`, `argparse`) — no new dependencies.
- Single file changed: `.agent/skills/skill-spec-validator/scripts/validate.py`.
