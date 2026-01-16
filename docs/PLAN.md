# Implementation Plan - Cleanup Skills & Rules

## Goal Description
Consolidate skills into `.agent/skills`, remove `.cursor/skills`, and fix legacy naming (`tz`) in configuration files.

## User Review Required
None.

## Proposed Changes

### Configuration
#### [MODIFY] .cursorrules
- Replace all instances of `.cursor/skills` with `.agent/skills`.
- Replace `03_tz_reviewer_prompt.md` with `03_task_reviewer_prompt.md`.
- Replace `skill-tz-review-checklist` with `skill-task-review-checklist`.

### File System
#### [DELETE] .cursor/skills
- Remove the directory after updating rules.

### Documentation
#### [MODIFY] README.md / README.ru.md
- Remove "Option A" special instructions for `.cursor/skills`.
- Standardize on `.agent/skills`.

#### [MODIFY] docs/ARCHITECTURE.md
- Update directory structure to reflect removal.

## Verification Plan
1. Checked `System/Agents` for `tz` files (done via `ls`).
2. Verify `.cursorrules` matches `grep` checks.
3. Verify deletion of `.cursor/skills`.
