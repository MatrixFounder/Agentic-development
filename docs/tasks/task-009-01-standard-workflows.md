# Task 009.1: Add verification to Standard Workflows

## Use Case Connection
- UC-01: Analyst Workflow with Verification
- UC-02: Architect Workflow with Verification
- UC-03: Planner Workflow with Verification

## Task Goal
Introduce mandatory review steps in `01-start-feature.md` and `02-plan-implementation.md`.

## Changes Description

### Changes in Existing Files

#### File: `.agent/workflows/01-start-feature.md`
- After **Analyst** step, add **TZ Reviewer** step.
- Implement loop: If Reviewer rejects -> Back to Analyst.
- After **Architect** step, add **Architecture Reviewer** step.
- Implement loop: If Reviewer rejects -> Back to Architect.

#### File: `.agent/workflows/02-plan-implementation.md`
- After **Planner** step, add **Plan Reviewer** step.
- Implement loop: If Reviewer rejects -> Back to Planner.

## Acceptance Criteria
- [ ] `01-start-feature.md` contains TZ and Arch review loops.
- [ ] `02-plan-implementation.md` contains Plan review loop.
- [ ] Loops use correct conditionals (if/else).
