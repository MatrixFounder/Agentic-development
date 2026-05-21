---
description: Plan the implementation using Chainlink Decomposition
---
> [!IMPORTANT]
> **VDD MODE ACTIVE**: Ensure every atomic unit of work ("Bead") is documented.

1. **Planner Prompt**: Read `System/Agents/06_planner_prompt.md`.
2. **Chainlink Decomposition (Part 2 - The Beads)**:
    - Create/Update `docs/PLAN.md`. (Re-planning the SAME task → overwrite in place; for a NEW task the old PLAN.md was already rotated to `docs/plans/` by `skill-archive-task` in Analysis.)
    - **Requirement**: Break down every "Issue" into "Sub-issues" (The Beads).
    - **Format**: Nested Markdown list (Epic -> Issue -> **Sub-issue**).
    - **Rule**: A "Bead" must be small enough to be Verified via a single test case.
3. **Task Creation**: Create `docs/tasks/*.md` corresponding to these atomic units.
    - **Verification Loop**: Read `System/Agents/07_plan_reviewer_prompt.md`.
    - If the Reviewer requests changes: Update `docs/PLAN.md` and task files, then repeat the review.
    - If approved: Proceed.
