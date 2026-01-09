# Task 009.4: Add verification to Base Stub-First Workflow

## Use Case Connection
- UC-05: Base Stub-First Workflow with Verification

## Task Goal
Introduce mandatory review loops in `base-stub-first.md`.

## Changes Description

### Changes in Existing Files

#### File: `.agent/workflows/base-stub-first.md`
- Identify all "Doer" steps (Analyst, Architect, Planner, Developer).
- Add corresponding "Reviewer" steps with explicit loops.
- Ensure the logic flows: Do -> Review -> Fix (if needed) -> Proceed.

## Acceptance Criteria
- [ ] `base-stub-first.md` contains Analyst -> TZ Reviewer loop.
- [ ] `base-stub-first.md` contains Architect -> Architecture Reviewer loop.
- [ ] `base-stub-first.md` contains Planner -> Plan Reviewer loop.
- [ ] `base-stub-first.md` contains Developer -> Code Reviewer loop.
