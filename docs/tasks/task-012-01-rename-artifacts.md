# Task 012.1: Rename artifacts and update System Prompts

## Use Case Connection
- UC-01: Renaming Artifacts

## Task Goal
Rename `docs/TZ.md` to `docs/TASK.md` and `03_tz_reviewer_prompt.md` to `03_task_reviewer_prompt.md`. Update the content of the reviewer prompt to reflect the new terminology.

## Changes Description

### New Files
- `docs/TASK.md` (Moved from `docs/TZ.md`)
- `System/Agents/03_task_reviewer_prompt.md` (Moved from `System/Agents/03_tz_reviewer_prompt.md`)

### Changes in Existing Files

#### File: `System/Agents/03_task_reviewer_prompt.md`
- **Content:** Replace all occurrences of "TZ" with "TASK" / "Task Specification".
- **Logic:** Ensure it references `docs/TASK.md`.

#### File: `System/Agents/02_analyst_prompt.md`
- **Output Format:** Change `docs/TZ.md` to `docs/TASK.md`.
- **References:** Replace "TZ" with "TASK".

#### File: `System/Agents/04_architect_prompt.md`
- **Input Data:** Change `Technical Specification (TZ)` to `Technical Specification (TASK)`.

## Acceptance Criteria
- [ ] `docs/TASK.md` exists.
- [ ] `docs/TZ.md` does not exist.
- [ ] `System/Agents/03_task_reviewer_prompt.md` exists and uses "TASK".
- [ ] Analyst and Architect prompts refer to `TASK.md`.
