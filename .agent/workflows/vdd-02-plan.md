---
description: Plan the implementation using Chainlink Decomposition
contract:
  version: 1
  loops:
    - id: plan-review
      what: plan reviewer rejects -> update and re-review
      site: "<!-- loop:plan-review -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
  calls: []
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
    - **Evidence before the spawn** — apply `skill-parallel-orchestration` §2.4, orchestrator half.
      The reviewer is declared without an execution tool, so anything its checklist requires to be
      RUN (its `Script Contract` — the register scan; the RTM-coverage validator) is yours to run
      **first**; the brief carries the OUTPUT as data (a file plus its path), never the command.
      Anything you did not run goes in as `NOT RUN (<reason>)`.
    - **Freeze the artifact for the round** — `skill-parallel-orchestration` §2.4.1. Between the
      spawn and the reviewer's return you write nothing to what it is reading; a revision goes in
      after it returns. Put a `Tree fingerprint` line in the brief, recompute it on return, and
      compare. Differing values mean the review describes a document that no longer exists, so the
      round is re-taken rather than annotated. The reviewer **quotes** the value — computing one
      needs an execution tool its role does not have.
    - **Verification Loop**: Read `System/Agents/07_plan_reviewer_prompt.md`.
    <!-- loop:plan-review -->
    - If the Reviewer requests changes: Update `docs/PLAN.md` and task files, then repeat the review.
    - **Bound: max 3 attempts.** Still rejected after the 3rd: **STOP** and escalate to the user
      with the Reviewer's outstanding objections — do not enter Development.
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
