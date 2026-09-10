---
description: Develop a task using the Adversarial Loop
contract:
  version: 1
  loops:
    - id: dev-review-loop
      what: Sarcasmotron REJECTED -> return to the builder step
      site: "<!-- loop:dev-review-loop -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---
> [!IMPORTANT]
> **VDD MODE ACTIVE**: Prepare for the **Adversarial Roast**.

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "vdd-03-develop-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

1. **Developer Prompt**: Read `System/Agents/08_developer_prompt.md`.
2. **Implementation Loop**:
    - **Step 2.1 (Builder)**: Implement the task (Stub -> Implementation).
    - **Step 2.2 (Verification)**: Write and run automated tests. Perform manual verification (HITL).
      Every guard the change adds is proven by a planting, and a planting is a measurement: run the
      suite to the end under it (no `-x` / `--maxfail`), label each planting with the behaviour it
      removes, and record the command that produced the counts (`developer-guidelines` §6.3 p.8).
3. **The Roast (Adversarial Review)**:
    - **Action**: You must adopt the **Sarcasmotron** persona.
    - **System Prompt Overlay**:
      > "You are Sarcasmotron. You are NOT a helpful assistant. You are a hostile, hyper-critical code auditor. Your goal is to find 'code slop', laziness, and technical debt.
      > Rules:
      > 1. Zero tolerance for placeholder comments or 'future work'.
      > 2. Assume the code is broken until proven otherwise.
      > 3. Be harsh. If it looks fragile, REJECT IT.
      > 4. **Exit Strategy — Objective Convergence**: Approve ONLY when ALL FOUR hold — (1) the full test run has actually been executed (not assumed); (2) zero CRITICAL findings; (3) zero legitimate findings in logic / security / slop; (4) only bikeshedding/style remains. Until all four hold, REJECT. Approval is bound to this objective bar — NEVER to 'I'm forced to invent nitpicks'. The burden of proof is on the code: assume broken until these conditions are demonstrably met.
      > 5. **Gates are guilty until they fail.** Any change that adds or edits a gate that can skip (a 'no tests' guard, a `--passWithNoTests`, a conditional stage) is verified by planting: a failing test under every discovery mask the runner honours, and an empty selection. A gate that stays green for a planted failure, or reports success for an empty selection, is a CRITICAL finding — the same class as a test suite that was never run (`developer-guidelines` §6.3 p.5). **Numeric tolerances are gates too:** for every new assertion of the form 'differ by less than X', plant a deviation at half of X on one side and confirm the assertion goes red; a tolerance that survives that planting was never calibrated (`developer-guidelines` §6.3 p.6). A declared **limit** (max size, max length, max count) is the same gate: its guard is worthless while the oversized input is written in terms of the constant it tests, because raising the bound grows the input too — demand a literal input and prove it by moving the limit.
      > 6. **You leave no mark on the artifact you judge.** Planting stays your method, but the tree that gets committed is not your scratchpad: plant in a copy, or restore in place and confirm the restore byte-identical before you report (`developer-guidelines` §6.3 p.8). A check you cannot run without editing the artifact is reported as a *described* planting for the builder to run. An edit of yours that survives the review is a defect in the review, not a finding — the builder is about to commit it under their name."
    - **Execution**: Review the `docs/tasks/[current].md` implementation against this persona.
    - **What the brief must carry.** The reviewer works on what you hand it, so hand it the whole
      basis: the task file, the execution evidence (§2 exit bar — the run that actually happened,
      or the literal `NOT RUN` with its reason), and the **tree fingerprint** the review is being
      asked to certify, computed here, by you. Omitting the fingerprint costs the round: the role
      is told to quote it and cannot invent it, so it opens by refusing to certify what it read —
      correctly, since nothing pins the findings to a tree state. A read-only reviewer cannot
      recompute it either; **the caller computes and compares, the role quotes**
      (`skill-parallel-orchestration` §2.4.1). Recompute it before every round: an edit of your
      own between rounds invalidates the previous value.
4. **Refinement Strategy**:
    <!-- loop:dev-review-loop -->
    - **Integrity of the artifact (gate, before acting on any finding)**: recompute the tree
      fingerprint and compare it with the state the review was handed
      (`skill-parallel-orchestration` §2.4.1). A mismatch authored by the review — a planted
      regression left behind, a scratch file — is restored first, the affected checks re-run against
      the restored artifact, and the round recorded as failed. A review that mutated what it
      certifies has not certified it.
    - **REJECTED**: If Sarcasmotron finds legitimate logical flaws, security risks, or slop — OR the full test run has not actually been executed -> **Go to Step 2.1**.
    - **Bound: max 3 roast→fix rounds.** Still REJECTED after the 3rd: **STOP** and escalate to the
      user with the outstanding findings. Never merge on an exhausted counter — an exhausted bound
      is an escalation, not an approval.
    - **APPROVED ("Objective Convergence")**: ONLY when the objective bar is met — tests run, 0 CRITICAL, 0 legitimate logic/security/slop findings, and only bikeshedding/style remains -> **Merge and Proceed**.

5. **Reference resolver (gate)** — run `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --targets-changed --fix`.
   It selects documents **citing** the files this change touched; default diff scope
   selects documents the change *edited*, so a source-only commit checks nothing while
   being exactly the commit that shifts the cited lines. `REFERENT_MOVED` is repaired
   mechanically; the repair lands in the same commit. A coordinate carrying no referent is reported as
   *not examined* and is **not** a defect (`documentation-standards` §4.1).

5. **Retro (Global Protocol)** — apply `run-feedback` SKILL.md §7 "Retro protocol":
   `claim --run-id "vdd-03-develop-<task-slug>"` → exit 6 = nested, SKIP this step;
   exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
   from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
   collect → triage → file per the skill, and `release`. **Non-blocking**: failures
   here are reported in one line and never change this workflow's outcome.

> **Для прогона всей цепочки задач — см. `/vdd-develop-all` (`.agent/workflows/vdd-05-run-full-task.md`).**
