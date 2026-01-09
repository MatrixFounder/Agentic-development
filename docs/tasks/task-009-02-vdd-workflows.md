# Task 009.2: Add verification to VDD Workflows

## Use Case Connection
- UC-01: Analyst Workflow with Verification
- UC-02: Architect Workflow with Verification
- UC-03: Planner Workflow with Verification

## Task Goal
Introduce mandatory review steps in `vdd-01-start-feature.md` and `vdd-02-plan.md`.

## Changes Description

### Changes in Existing Files

#### File: `.agent/workflows/vdd-01-start-feature.md`
- After **Analyst** step, add **TZ Reviewer** step.
- Implement loop: If Reviewer rejects -> Back to Analyst.
- After **Architect** step, add **Architecture Reviewer** step.
- Implement loop: If Reviewer rejects -> Back to Architect.

#### File: `.agent/workflows/vdd-02-plan.md`
- After **Planner** step, add **Plan Reviewer** step.
- Implement loop: If Reviewer rejects -> Back to Planner.

## Acceptance Criteria
- [ ] `vdd-01-start-feature.md` contains TZ and Arch review loops.
- [ ] `vdd-02-plan.md` contains Plan review loop.
