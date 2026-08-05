---
description: Plan the implementation of the feature
contract:
  version: 1
  loops:
    - id: plan-review
      what: plan reviewer rejects -> update and re-review
      site: "<!-- loop:plan-review -->"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---
1. Read `System/Agents/06_planner_prompt.md` to understand the Planning phase.
2. Create or update `docs/PLAN.md` with the overall plan.
   - When re-planning the **SAME** task, overwrite `docs/PLAN.md` in place (no archive).
   - For a NEW task, the previous PLAN.md was already rotated to `docs/plans/` by `skill-archive-task` during the Analysis phase.
3. Create task files in `docs/tasks/*.md` for each actionable task, following the stub-first strategy.
    <!-- loop:plan-review -->
    - **Evidence before the spawn** — apply `skill-parallel-orchestration` §2.4, orchestrator half.
      The reviewer is declared without an execution tool, so anything its checklist requires to be
      RUN (its `Script Contract` — the register scan; the RTM-coverage validator) is yours to run
      **first**; the brief carries the OUTPUT as data (a file plus its path), never the command.
      Anything you did not run goes in as `NOT RUN (<reason>)`.
    - **Verification Loop**: Read `System/Agents/07_plan_reviewer_prompt.md`.
    - If the Reviewer requests changes:
        - Update `docs/PLAN.md` and task files.
        - **Retry (Max 2 attempts)**: Repeat the review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.
    - If approved: Proceed.
4. **Phase-boundary gate — run the checks before leaving this phase.** A phase that edits artifacts
   **read by checks** must end by running those checks. This phase writes `docs/PLAN.md` and
   `docs/tasks/*.md`, which in a repository with machine-checked documentation are read by gates just
   as source is (WI-41).
    - **Gate:** the **full regression suite passes**. Same gate as `vdd-enhanced` §3 step 2; the
      command belongs to the project, not to this file. Record the result in the phase-boundary
      `skill-session-state` update.
    - **IF RED**: fix here and re-run. Development must not start against a red baseline — once it
      does, regression cannot be told apart from inherited state.
    - This is the **orchestrator's** obligation and never a reviewer's — a role declared without a
      means of execution must not be handed an instruction that requires execution
      (`skill-parallel-orchestration` §2.4).
