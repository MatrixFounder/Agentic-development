---
description: VDD-Enhanced Development (Hardened Pipeline)
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
        -   **Loop**: Repeat Validation (Max 3 retries).
        -   **Escalation**: If still failing, STOP and ask User.

## 3. Development (Stub-First)
1.  **Execute**: `.agent/workflows/05-run-full-task.md` (alias: `/develop-all`) — Standard Development Loop.
    -   *Note*: Each task inside runs the Developer → Reviewer loop of
        `.agent/workflows/03-develop-single-task.md` (max 2 review attempts, then escalate);
        the standard Developer prompt enforces Stub-First.
2.  **Gate (caller-side)**: the **full regression suite passes**.
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
