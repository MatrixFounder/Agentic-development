---
description: Automatically execute all tasks in the current PLAN.md
---
# Workflow: Run Full Task

**Description:**
Iterates through all defined tasks in `docs/PLAN.md` and executes them using the standard Developer -> Reviewer loop.

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "05-run-full-task-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

**Steps:**

1. **Read Plan**:
   - Read `docs/PLAN.md` to identify the list of tasks (Task X.1, Task X.2, etc.).

2. **Execution Loop** (For each Task):
   
   **A. Developer Phase**:
   - Call `/03-develop-single-task`.
     > Input: The specific task file (e.g. `docs/tasks/task-X-Y.md`).
     > Note: This atomic workflow includes Developer -> Reviewer loop.


3. **Finalization**:
   - Run Full Regression Suite (`pytest`).
   - **Gate**:
     - **If Pass**: Commit changes.
     - **If Fail**: re-enter `.agent/workflows/03-develop-single-task.md` (alias: `/develop`)
       for the failing task(s) — **max 2 attempts** — then re-run the suite.
       Still failing → **STOP** and ask the user. **Never commit on a red suite.**

4. **Retro (Global Protocol)** — apply `run-feedback` SKILL.md §7 "Retro protocol":
   `claim --run-id "05-run-full-task-<task-slug>"` → exit 6 = nested, SKIP this step;
   exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
   from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
   collect → triage → file per the skill, and `release`. **Non-blocking**: failures
   here are reported in one line and never change this workflow's outcome.
