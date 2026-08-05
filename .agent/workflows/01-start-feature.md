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
    - **Evidence before the spawn** — apply `skill-parallel-orchestration` §2.4, orchestrator half.
      The reviewer is declared without an execution tool, so anything its checklist requires to be
      RUN (its `Script Contract` — the register scan) is yours to run **first**; the brief carries
      the OUTPUT as data (a file plus its path), never the command. Anything you did not run goes in
      as `NOT RUN (<reason>)`. A brief naming a command instead of its result costs a silently
      unverified checklist section, or the whole turn.
    - **Verification Loop**: Read `System/Agents/03_task_reviewer_prompt.md`.
    - If the Reviewer requests changes:
        - Update `docs/TASK.md`.
        - **Retry (Max 2 attempts)**: Repeat the review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.
    - If approved: Proceed.
4. Read `System/Agents/04_architect_prompt.md` to understand the Architecture phase.
5. Update `docs/ARCHITECTURE.md` in place to reflect any architectural changes (living document — never per-task archived; if it exceeds 1500 lines, apply the Index-Mode split per `architecture-format-core`).
    <!-- loop:arch-review -->
    - **Evidence before the spawn** — apply `skill-parallel-orchestration` §2.4, orchestrator half.
      Same obligation as the TASK gate, plus the change set: this reviewer cannot produce a diff, so
      **write the diff to a file and pass the path**. "Review `git diff` on these files" is an
      instruction to execute, given to a role that cannot — measured at 600 s and a watchdog kill.
    - **Verification Loop**: Read `System/Agents/05_architecture_reviewer_prompt.md`.
    - If the Reviewer requests changes:
        - Update `docs/ARCHITECTURE.md`.
        - **Retry (Max 2 attempts)**: Repeat the review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.
    - If approved: Proceed.
6. **Phase-boundary gate — run the checks before leaving this phase.** A phase that edits artifacts
   **read by checks** must end by running those checks. Where documentation is machine-checked, a
   document edit breaks the build exactly as a code edit does: measured, one Architecture phase wrote
   no source line and left the suite red **twice**, both times from document edits alone, and neither
   was found by review (WI-41).
    - **Gate:** the **full regression suite passes**. Same gate as `vdd-enhanced` §3 step 2; the
      command belongs to the project, not to this file. Record the result in the phase-boundary
      `skill-session-state` update — "the build was green at the end of the task" is not this
      criterion, the question is *when* it became known.
    - **IF RED**: fix here and re-run. A red suite carried into Planning becomes that phase's
      baseline, and from then on regression cannot be told apart from inherited state.
    - This is the **orchestrator's** obligation and never a reviewer's — a role declared without a
      means of execution must not be handed an instruction that requires execution
      (`skill-parallel-orchestration` §2.4).
