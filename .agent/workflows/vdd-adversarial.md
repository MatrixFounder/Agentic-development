---
description: VDD Adversarial Refinement
---

# Workflow: VDD Adversarial Refinement

**Description:**  
Post-implementation adversarial cycle for zero-slop robustness.

**Required Skills:** `vdd-adversarial` (Tier 2), `vdd-sarcastic` (Tier 2)

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "vdd-adversarial-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

**Steps:**

1. **Load Skills**: Read `.agent/skills/vdd-adversarial/SKILL.md` and `.agent/skills/vdd-sarcastic/SKILL.md`.
2. For each implemented module:
   a. Activate Adversary (Sarcasmotron)
      - Apply the `vdd-adversarial` skill: Red Flags, Challenge Assumptions, Failure Simulation.
      - Use critique template from `.agent/skills/vdd-adversarial/assets/template_critique.md`.
      - Review all code + tests with fresh context (avoids multi-turn assumption lock-in and context rot — audit-067 C-02).
   b. If real issues found:
      - Call workflow `03-develop-single-task` to fix issues.
      - Repeat this workflow (recursive call if needed).
   c. Terminate on **Objective Convergence** — the full test run has executed, 0 CRITICAL, 0 legitimate logic/security/slop findings, only bikeshedding remains (see `vdd-adversarial` / `vdd-sarcastic` skills). Never approve because the adversary was forced to invent nitpicks.
3. **Retro (Global Protocol)** — apply `run-feedback` SKILL.md §7 "Retro protocol":
   `claim --run-id "vdd-adversarial-<task-slug>"` → exit 6 = nested, SKIP this step;
   exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
   from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
   collect → triage → file per the skill, and `release`. **Non-blocking**: failures
   here are reported in one line and never change this workflow's outcome.
4. Announce: "VDD cycle complete: zero-slop achieved"
