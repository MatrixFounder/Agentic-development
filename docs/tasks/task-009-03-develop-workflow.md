# Task 009.3: Add verification to Develop Task Workflow

## Use Case Connection
- UC-04: Developer Workflow with Verification

## Task Goal
Introduce mandatory code review step in `03-develop-task.md`.

## Changes Description

### Changes in Existing Files

#### File: `.agent/workflows/03-develop-task.md`
- After **Developer** step, add **Code Reviewer** step.
- Implement loop: If Reviewer rejects -> Back to Developer.

## Acceptance Criteria
- [ ] `03-develop-task.md` contains Code Reviewer loop.
- [ ] Loop uses correct conditionals (if/else).
