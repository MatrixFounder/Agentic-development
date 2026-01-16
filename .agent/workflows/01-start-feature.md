---
description: Start a new feature development cycle (Analysis & Architecture)
---
1. Read `System/Agents/02_analyst_prompt.md` to understand the Analysis phase.
2. Read `docs/KNOWN_ISSUES.md` to be aware of past problems.
3. **Archiving (Important)**:
   - Check if `docs/TASK.md` exists and contains content from a previous task.
   - If yes: Archive it to `docs/tasks/task-ID-slug.md` (use `skill-artifact-management`).
   - If no (or first run): Skip archiving.
4. Update `docs/TASK.md` with the new feature requirements.
    - **Verification Loop**: Read `System/Agents/03_task_reviewer_prompt.md`.
    - If the Reviewer requests changes:
        - Update `docs/TASK.md`.
        - **Retry (Max 2 attempts)**: Repeat the review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.
    - If approved: Proceed.
4. Read `System/Agents/04_architect_prompt.md` to understand the Architecture phase.
5. Update `docs/ARCHITECTURE.md` to reflect any architectural changes.
    - **Verification Loop**: Read `System/Agents/05_architecture_reviewer_prompt.md`.
    - If the Reviewer requests changes:
        - Update `docs/ARCHITECTURE.md`.
        - **Retry (Max 2 attempts)**: Repeat the review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.
    - If approved: Proceed.
