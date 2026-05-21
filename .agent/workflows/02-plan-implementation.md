---
description: Plan the implementation of the feature
---
1. Read `System/Agents/06_planner_prompt.md` to understand the Planning phase.
2. Create or update `docs/PLAN.md` with the overall plan.
   - When re-planning the **SAME** task, overwrite `docs/PLAN.md` in place (no archive).
   - For a NEW task, the previous PLAN.md was already rotated to `docs/plans/` by `skill-archive-task` during the Analysis phase.
3. Create task files in `docs/tasks/*.md` for each actionable task, following the stub-first strategy.
    - **Verification Loop**: Read `System/Agents/07_plan_reviewer_prompt.md`.
    - If the Reviewer requests changes:
        - Update `docs/PLAN.md` and task files.
        - **Retry (Max 2 attempts)**: Repeat the review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.
    - If approved: Proceed.
