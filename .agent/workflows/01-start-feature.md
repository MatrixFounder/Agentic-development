---
description: Start a new feature development cycle (Analysis & Architecture)
contract:
  version: 1
  loops:
    - id: task-review
      what: TASK reviewer rejects -> update and re-review
      site: "<!-- loop:task-review -->"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
    - id: arch-review
      what: ARCHITECTURE reviewer rejects -> update and re-review
      site: "<!-- loop:arch-review -->"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---
1. Read `System/Agents/02_analyst_prompt.md` to understand the Analysis phase.
2. Read `docs/KNOWN_ISSUES.md` to be aware of past problems (skip if absent — created on the first filed issue).
3. **Archiving**: Apply `skill-archive-task` protocol if `docs/TASK.md` exists. This rotates **both** `docs/TASK.md` → `docs/tasks/` and `docs/PLAN.md` → `docs/plans/` in lockstep (same ID/slug).
4. Update `docs/TASK.md` with the new feature requirements.
    <!-- loop:task-review -->
    - **Verification Loop**: Read `System/Agents/03_task_reviewer_prompt.md`.
    - If the Reviewer requests changes:
        - Update `docs/TASK.md`.
        - **Retry (Max 2 attempts)**: Repeat the review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.
    - If approved: Proceed.
4. Read `System/Agents/04_architect_prompt.md` to understand the Architecture phase.
5. Update `docs/ARCHITECTURE.md` in place to reflect any architectural changes (living document — never per-task archived; if it exceeds 1500 lines, apply the Index-Mode split per `architecture-format-core`).
    <!-- loop:arch-review -->
    - **Verification Loop**: Read `System/Agents/05_architecture_reviewer_prompt.md`.
    - If the Reviewer requests changes:
        - Update `docs/ARCHITECTURE.md`.
        - **Retry (Max 2 attempts)**: Repeat the review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.
    - If approved: Proceed.
