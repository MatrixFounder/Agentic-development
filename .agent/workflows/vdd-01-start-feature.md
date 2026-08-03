---
description: Start a new feature development cycle (VDD Mode - High Integrity)
contract:
  version: 1
  loops:
    - id: task-review
      what: TASK reviewer rejects -> update and re-review
      site: "<!-- loop:task-review -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
    - id: arch-review
      what: ARCHITECTURE reviewer rejects -> update and re-review
      site: "<!-- loop:arch-review -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---
> [!IMPORTANT]
> **VDD MODE ACTIVE**: You are now operating under Verification-Driven Development. Precision and decomposition are paramount.

1. **Standard Analysis**: Read `System/Agents/02_analyst_prompt.md`.
2. **Context Check**: Read `docs/KNOWN_ISSUES.md` (skip if absent — created on the first filed issue).
3. **Chainlink Decomposition (Part 1 - The Epics)**:
    - **Archiving**: Apply `skill-archive-task` protocol if `docs/TASK.md` exists. This rotates **both** `docs/TASK.md` → `docs/tasks/` and `docs/PLAN.md` → `docs/plans/` in lockstep (same ID/slug).
4. **Update `docs/TASK.md`**:
    - **Constraint**: You MUST structure the requirements into **Epics** and **Issues**.
    - **Constraint**: Do not accept vague requirements. If ambiguous, ask the user.
    - **Verification Loop**: Read `System/Agents/03_task_reviewer_prompt.md`.
    <!-- loop:task-review -->
    - If the Reviewer requests changes: Update `docs/TASK.md` and repeat the review.
    - **Bound: max 3 attempts.** Still rejected after the 3rd: **STOP** and escalate to the user
      with the Reviewer's outstanding objections — do not proceed to Architecture.
    - If approved: Proceed.
5. **Architecture**: Read `System/Agents/04_architect_prompt.md` and update `docs/ARCHITECTURE.md` in place (living document — never per-task archived; if it exceeds 1500 lines, apply the Index-Mode split per `architecture-format-core`).
    - **Verification Loop**: Read `System/Agents/05_architecture_reviewer_prompt.md`.
    <!-- loop:arch-review -->
    - If the Reviewer requests changes: Update `docs/ARCHITECTURE.md` and repeat the review.
    - **Bound: max 3 attempts.** Still rejected after the 3rd: **STOP** and escalate to the user
      with the Reviewer's outstanding objections.
    - If approved: Proceed.
