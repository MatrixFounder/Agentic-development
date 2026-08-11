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
    - **Evidence before the spawn** — apply `skill-parallel-orchestration` §2.4, orchestrator half.
      The reviewer is declared without an execution tool, so anything its checklist requires to be
      RUN (its `Script Contract` — the register scan) is yours to run **first**; the brief carries
      the OUTPUT as data (a file plus its path), never the command. Anything you did not run goes in
      as `NOT RUN (<reason>)`. A brief naming a command instead of its result costs a silently
      unverified checklist section, or the whole turn.
    - **Freeze the artifact for the round** — `skill-parallel-orchestration` §2.4.1. Between the
      spawn and the reviewer's return you write nothing to what it is reading; a revision goes in
      after it returns. Put a `Tree fingerprint` line in the brief, recompute it on return, and
      compare. Differing values mean the review describes a document that no longer exists, so the
      round is re-taken rather than annotated. The reviewer **quotes** the value — computing one
      needs an execution tool its role does not have.
    - **Verification Loop**: Read `System/Agents/03_task_reviewer_prompt.md`.
    <!-- loop:task-review -->
    - If the Reviewer requests changes: Update `docs/TASK.md` and repeat the review.
    - **Bound: max 3 attempts.** Still rejected after the 3rd: **STOP** and escalate to the user
      with the Reviewer's outstanding objections — do not proceed to Architecture.
    - If approved: Proceed.
5. **Architecture**: Read `System/Agents/04_architect_prompt.md` and update `docs/ARCHITECTURE.md` in place (living document — never per-task archived; if it exceeds 1500 lines, apply the Index-Mode split per `architecture-format-core`).
    - **Evidence before the spawn** — apply `skill-parallel-orchestration` §2.4, orchestrator half.
      Same obligation as the TASK gate, plus the change set: this reviewer cannot produce a diff, so
      **write the diff to a file and pass the path**. "Review `git diff` on these files" is an
      instruction to execute, given to a role that cannot — measured at 600 s and a watchdog kill.
    - **Freeze the artifact for the round** — `skill-parallel-orchestration` §2.4.1. Between the
      spawn and the reviewer's return you write nothing to what it is reading; a revision goes in
      after it returns. Put a `Tree fingerprint` line in the brief, recompute it on return, and
      compare. Differing values mean the review describes a document that no longer exists, so the
      round is re-taken rather than annotated. The reviewer **quotes** the value — computing one
      needs an execution tool its role does not have.
    - **Verification Loop**: Read `System/Agents/05_architecture_reviewer_prompt.md`.
    <!-- loop:arch-review -->
    - If the Reviewer requests changes: Update `docs/ARCHITECTURE.md` and repeat the review.
    - **Bound: max 3 attempts.** Still rejected after the 3rd: **STOP** and escalate to the user
      with the Reviewer's outstanding objections.
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
