---
description: Start a new feature development cycle (VDD Mode - High Integrity)
---
> [!IMPORTANT]
> **VDD MODE ACTIVE**: You are now operating under Verification-Driven Development. Precision and decomposition are paramount.

1. **Standard Analysis**: Read `System/Agents/02_analyst_prompt.md`.
2. **Context Check**: Read `docs/KNOWN_ISSUES.md`.
3. **Chainlink Decomposition (Part 1 - The Epics)**:
    - **Archiving (Important)**:
        - Check if `docs/TASK.md` exists.
        - If yes: Archive it to `docs/tasks/task-ID-slug.md`.
4. **Update `docs/TASK.md`**:
    - **Constraint**: You MUST structure the requirements into **Epics** and **Issues**.
    - **Constraint**: Do not accept vague requirements. If ambiguous, ask the user.
    - **Verification Loop**: Read `System/Agents/03_task_reviewer_prompt.md`.
    - If the Reviewer requests changes: Update `docs/TASK.md` and repeat the review.
    - If approved: Proceed.
5. **Architecture**: Read `System/Agents/04_architect_prompt.md` and update `docs/ARCHITECTURE.md`.
    - **Verification Loop**: Read `System/Agents/05_architecture_reviewer_prompt.md`.
    - If the Reviewer requests changes: Update `docs/ARCHITECTURE.md` and repeat the review.
    - If approved: Proceed.
