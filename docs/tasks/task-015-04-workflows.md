# Task 015.4: Workflow Refactoring & Automation

## Use Case Connection
- New Requirement: Full Automation

## Task Goal
Modernize the workflow system by removing legacy "tz" terminology and introducing a new workflow for end-to-end task automation.

## Changes Description

### New Files
- `.agent/workflows/05-run-full-task.md`
  - **Logic:** Iterate through all listed subtasks in the Plan, executing Developer -> Reviewer loop for each.
  - **Format:** Standard workflow markdown.

### Changes in Existing Files

#### Directory: `.agent/workflows/`
- **Action:** Find and replace `tz` -> `task` in all files.
- **Specific Targets:**
  - `01-start-feature.md` (`03_tz_reviewer_prompt.md` -> `03_task_reviewer_prompt.md`)
  - `base-stub-first.md` (`/analyst-tz` -> `/analyst-task`)

## Test Cases

### Manual Verification
1. **TC-MAN-01:** Run `/01-start-feature` and verify it calls the Task Reviewer correctly (no file not found errors).
2. **TC-MAN-02:** Run `/05-run-full-task` (dry run or on a dummy task) to verify loop logic.

## Acceptance Criteria
- [ ] No `tz` terms in `.agent/workflows/`.
- [ ] `/05-run-full-task` exists and logic is sound.
