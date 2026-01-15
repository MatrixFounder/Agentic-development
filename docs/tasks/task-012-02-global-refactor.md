# Task 012.2: Global Search & Replace (TZ -> TASK)

## Use Case Connection
- UC-02: Global Codebase Refactoring
- UC-03: Archive Management Update
- UC-04: Backward Compatibility Check

## Task Goal
Replace "TZ" with "TASK" across the entire codebase, including Skills, Workflows, and Documentation.

## Changes Description

### Global Search & Replace
- **Target:** "TZ.md" -> "TASK.md"
- **Target:** "TZ" -> "TASK" (context-aware)
- **Target:** "tz" -> "task" (context-aware)

### Affected Areas
- `.agent/skills/` (e.g. `requirements-analysis`, `artifact-management`)
- `.agent/roles/` (if any separate from System/Agents)
- `docs/WORKFLOWS.md`
- `README.md`
- `docs/ARCHITECTURE.md` (Verification)

### Exclusions
- `CHANGELOG.md`
- `docs/tasks/` (historic task files)

## Test Cases

### Verification Script
1. **TC-01:** Run grep for "TZ.md". Output should be empty (except exclusions).

## Acceptance Criteria
- [ ] No "TZ.md" references in active code/docs.
- [ ] Skills correctly reference `TASK.md`.
- [ ] Workflows correctly reference `TASK.md`.
