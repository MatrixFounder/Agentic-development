---
description: VDD-Enhanced Development (Hardened Pipeline)
contract:
  version: 1
  loops:
    - id: task-validate-retry
      what: RTM validation fails -> re-run the analyst role
      site: "<!-- loop:task-validate-retry -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
    - id: plan-validate-retry
      what: plan validation fails -> re-run the planner role
      site: "<!-- loop:plan-validate-retry -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
      window: 2
    - id: regression-retry
      what: red regression suite -> fix and re-run, total not per task
      site: "<!-- loop:regression-retry -->"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
      scope: per_run
  calls:
    - workflow: 01-start-feature
      kind: invoke
    - workflow: 02-plan-implementation
      kind: invoke
    - workflow: 05-run-full-task
      kind: invoke
    - workflow: 03-develop-single-task
      kind: invoke
    - workflow: vdd-adversarial
      kind: invoke
      binds:
        adversarial-cycle:
          max: 3
---

# Workflow: VDD-Enhanced (Hardened)

> [!IMPORTANT]
> **Constraint**: This workflow enforces "Requirements Hardening" and "Atomic Planning".
> **Tools**: Uses `skill-spec-validator` to mechanically verify artifacts.

> [!NOTE]
> **Loop protocol (all phases):** gates are **externally checkable** — script exit codes and
> test runs are deterministic; review gates return a structured verdict against a written
> objective bar, never the authoring model's free-form self-assessment — so any LLM can drive
> this pipeline. On failure, feed the gate's error output **verbatim** into the retry. Every loop
> is **bounded**, and exhaustion **escalates to the user** — never proceed silently. After
> each phase, persist state (global protocol):
> `python3 .agent/skills/skill-session-state/scripts/update_state.py ...` — a fresh session
> resumes mid-pipeline from `.agent/sessions/latest.yaml`.

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "vdd-enhanced-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

## 1. Analysis & Validation
1.  **Execute**: `.agent/workflows/01-start-feature.md` (Claude Code alias: `/start-feature`) — Analysis Phase.
2.  **Validate**: Run `python3 .agent/skills/skill-spec-validator/scripts/validate.py --mode task docs/TASK.md`
3.  **Self-Correction**:
    -   **IF PASS**: Proceed to Step 2.
    -   **IF FAIL**:
        -   Read the error message.
        -   Re-run the Analyst role (`System/Agents/02_analyst_prompt.md`; subagent `analyst`
            on Claude Code, role-switch elsewhere) with instruction: "Fix RTM gaps: [Error
            Message]. Ensure strict RTM table."
        <!-- loop:task-validate-retry -->
        -   **Loop**: Repeat Validation (Max 3 retries).
        -   **Escalation**: If still failing, STOP and ask User.

## 2. Planning & Validation
1.  **Execute**: `.agent/workflows/02-plan-implementation.md` (alias: `/plan`) — Planning Phase.
2.  **Validate**: Run `python3 .agent/skills/skill-spec-validator/scripts/validate.py --mode plan docs/PLAN.md docs/TASK.md`
3.  **Self-Correction**:
    -   **IF PASS**: Proceed to Step 3.
    -   **IF FAIL**:
        -   Read the error message (missing IDs workflow).
        -   Re-run the Planner role (`System/Agents/06_planner_prompt.md`; subagent `planner`
            on Claude Code, role-switch elsewhere) with instruction: "Fix missing RTM IDs in
            Plan: [Error Message]. Ensure every task starts with `[ID]`."
        <!-- loop:plan-validate-retry -->
        -   **Loop**: Repeat Validation (Max 3 retries).
        -   **Escalation**: If still failing, STOP and ask User.

## 3. Development (Stub-First)
1.  **Execute**: `.agent/workflows/05-run-full-task.md` (alias: `/develop-all`) — Standard Development Loop.
    -   *Note*: Each task inside runs the Developer → Reviewer loop of
        `.agent/workflows/03-develop-single-task.md` (max 2 review attempts, then escalate);
        the standard Developer prompt enforces Stub-First.
2.  **Gate (caller-side)**: the **full regression suite passes**.
    <!-- loop:regression-retry -->
    -   **IF FAIL**: re-enter `.agent/workflows/03-develop-single-task.md` (alias: `/develop`)
        for each failing task, then re-run the full regression suite — **max 2 fix-and-rerun
        rounds total** (not per task; `/develop`'s internal max-2 review loop counts
        separately). Suite still red after the 2nd round → STOP and ask User.
        Do not enter Phase 4 with a red suite.

## 4. Adversarial Review
1.  **Execute**: `.agent/workflows/vdd-adversarial.md` (alias: `/vdd-adversarial`) — Final Polish.
2.  **Termination bar**: **Objective Convergence** — full test run executed, 0 CRITICAL, no
    legitimate logic/security/slop findings, only bikeshedding remains (see the
    `vdd-adversarial` skill). Never approve because the adversary was forced to invent
    nitpicks.
3.  **Outer cap**: **max 3 adversarial cycles** (critique → fix → re-critique). Cap reached
    without convergence → STOP and report the remaining findings to the User.
4.  **Orchestrator-applied fixes are re-reviewed, and named as such.** A fix the orchestrator
    writes itself — instead of dispatching it through the Developer → Reviewer loop — has had
    **no review pass at all**. Carry every such fix into the NEXT cycle's brief, listed
    explicitly as "applied outside the dev→review loop", so the critics know to attack the fix
    and not only the original code. A fix is not exempt from review for having been written by the
    orchestrator; a fix can be worse than the defect it replaced.
5.  **Cap reached with an orchestrator-applied fix still un-reviewed** → the verdict is
    **WARNING, never PASS**. Name the unreviewed change in the report to the User; do not let
    "the cycle found nothing new" stand in for "this change was reviewed".
6.  **Fixing an assertion: find every site FIRST, then fix, then report the ratio.** A fact is
    usually written in several places — a docstring, a README, a test name, a prompt. The critic
    points at one. Fixing only that one *looks* like completed work, which makes it more dangerous
    than the untouched defect: it removes the alarm without removing the cause. Order is fixed:
    -   **Search before editing.** Grep the distinctive wording, the number, the name — whatever
        form the assertion takes — across the repository. Searching costs less than one review
        cycle; discovering the other three sites next cycle costs a full critic pass.
    -   **Report "fixed N of M found"** in the cycle report. "Fixed" without a denominator is an
        assertion with no guard — precisely the genre these cycles exist to catch.
    -   **N < M is a legitimate outcome, silence is not.** Archived documents must not be edited,
        and a translated copy may lag. Name what was left and why.
    -   **Repeated verbatim in several files → prefer one declaration with readers** over synchronized
        copies. A synchronized copy must be re-synchronized on every future change; a declaration
        need not. This is a preference, not a rule: it loses to the archive doctrine.
    Carry the ratio into the **Cycle Brief** (§4.7), so the next cycle verifies the *ratio* and not
    only the fix it was shown.
7.  **The Cycle Brief is a real input, not an implied one.** Items 4 and 6 both hand something to
    the next cycle, so the next cycle must have somewhere to receive it. When re-entering
    `.agent/workflows/vdd-adversarial.md`, pass the **Cycle Brief block** defined in its step 2a
    — `Applied outside the dev→review loop` and `Assertion fixes (N of M)`. An empty brief is
    written as empty; **omitting the block entirely** is what the adversary reports as
    "cycle brief missing", exactly as it treats missing execution evidence.
8.  **Gather the execution evidence before spawning — on EVERY cycle, the first included.** The
    adversary is read-only (no `Bash`), so a test run or a scanner is *your* job, not its. Run them
    first, then pass the `Execution evidence` block defined in `vdd-adversarial.md` step 2a — with an
    honest `NOT RUN (<reason>)` line for anything you did not run. This is the same contract
    `vdd-multi` Step 1.0 states for the parallel path and `skill-parallel-orchestration` §2.4 states
    for every path. Omitting it does not merely lose a fact: a teammate whose skill tells it to run
    something it cannot run will spend the whole turn trying. Measured — two subagents stalled 600 s
    each in one run of this workflow; for one of them the truncated output shows the turn spent
    trying to launch a scanner its role cannot execute, and both worked normally on a relaunch that
    only told them not to attempt it. The second stall is recorded as observed, not as explained.
9.  **The tree is frozen while the round reads it, and the brief carries its fingerprint.** Item 8
    puts you at the keyboard during the cycle; this item bounds what you may do there. Between the
    spawn and the return of the round's last role you write **nothing** to the reviewed files — no
    fix, no mutation run to prove test strength, no reformat. Those run before the spawn, or after
    the last return. Compute a `Tree fingerprint` before spawning, pass it in the evidence block,
    and recompute it on return. A role **quotes** the value rather than computing one: computing
    needs an execution tool it does not have. Full rule and the `git` form —
    `skill-parallel-orchestration` §2.4.1.
    -   **A mismatch invalidates the cycle rather than annotating it.** Re-take the critique against
        the frozen tree, or report the mismatch and record no pass. Findings about a state that no
        longer exists are not findings about this one.
    -   **Measured (RF-7).** The mutation protocol and a read-only roast ran over one tree with no
        order between them. The reviewer read `1 failed | 336 passed` and a `git diff --stat` of
        `35 ++++` where the same command had printed `38 +` ninety seconds earlier. Both came from
        the caller's own mutation. Cost of the catch: seven extra full suite runs and one HIGH
        finding. Cost of the miss: a verdict on a tree that was never committed.

## 5. Retro (Global Protocol)
Apply `run-feedback` SKILL.md §7 "Retro protocol":
`claim --run-id "vdd-enhanced-<task-slug>"` → exit 6 = nested, SKIP this step;
exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
collect → triage → file per the skill, and `release`. **Non-blocking**: failures
here are reported in one line and never change this workflow's outcome.

## Vendor dispatch & model portability

- **Invocation:** on any harness, "execute" a referenced workflow = **read that
  `.agent/workflows/*.md` file and follow its steps**; slash commands in parentheses are
  Claude-Code-only aliases (`.claude/commands/`). Codex/Cursor bootstrap via `AGENTS.md`,
  Gemini CLI / Antigravity via `GEMINI.md`.
- **Role calls** (the Analyst/Planner re-runs above) resolve per
  `skill-parallel-orchestration` §1.1: native subagent wrappers where the runtime has them,
  sequential role-switching (§7) as the last resort. Loop bounds, gates, and escalation
  paths are identical on every path — only the spawn mechanism changes.
- **Model-agnostic by construction:** Phases 1–3 gate on mechanical checks (`validate.py`
  exit status, regression suite); Phase 4 gates on a structured adversarial verdict against
  the written convergence bar — no phase depends on a vendor-specific model capability; the
  phase-boundary checkpoints let small-context models resume mid-pipeline.
