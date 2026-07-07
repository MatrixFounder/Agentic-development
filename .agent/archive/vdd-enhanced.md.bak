---
description: VDD-Enhanced Development (Hardened Pipeline)
---

# Workflow: VDD-Enhanced (Hardened)

> [!IMPORTANT]
> **Constraint**: This workflow enforces "Requirements Hardening" and "Atomic Planning".
> **Tools**: Uses `skill-spec-validator` to mechanically verify artifacts.

## 1. Analysis & Validation
1.  **Execute**: Call `/01-start-feature` (Analysis Phase).
2.  **Validate**: Run `python3 .agent/skills/skill-spec-validator/scripts/validate.py --mode task docs/TASK.md`
3.  **Self-Correction**:
    -   **IF PASS**: Proceed to Step 2.
    -   **IF FAIL**:
        -   Read the error message.
        -   Call `02_analyst` again with instruction: "Fix RTM gaps: [Error Message]. Ensure strict RTM table."
        -   **Loop**: Repeat Validation (Max 3 retries).
        -   **Escalation**: If still failing, stop and ask User.

## 2. Planning & Validation
1.  **Execute**: Call `/02-plan-implementation` (Planning Phase).
2.  **Validate**: Run `python3 .agent/skills/skill-spec-validator/scripts/validate.py --mode plan docs/PLAN.md docs/TASK.md`
3.  **Self-Correction**:
    -   **IF PASS**: Proceed to Step 3.
    -   **IF FAIL**:
        -   Read the error message (missing IDs workflow).
        -   Call `06_planner` again with instruction: "Fix missing RTM IDs in Plan: [Error Message]. Ensure every task starts with `[ID]`."
        -   **Loop**: Repeat Validation (Max 3 retries).

## 3. Development (Stub-First)
1.  **Execute**: Call `/05-run-full-task` (Standard Development Loop).
    -   *Note*: This uses the standard Developer prompt which enforces Stub-First.

## 4. Adversarial Review
1.  **Execute**: Call `/vdd-adversarial` (Final Polish).
