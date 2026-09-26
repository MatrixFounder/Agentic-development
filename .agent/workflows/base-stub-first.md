---
description: Start a feature using the standard Stub-First pipeline
contract:
  version: 1
  loops: []
  calls:
    - workflow: 01-start-feature
      kind: invoke
    - workflow: 02-plan-implementation
      kind: invoke
    - workflow: 05-run-full-task
      kind: invoke
---
# Workflow: Base Stub-First Development

**Description:**  
Core pipeline with Stub-First and TDD. Used as foundation for others.

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "base-stub-first-<task-slug>"` (non-blocking; exit 6 = an outer workflow of this task owns this run's retro — fine, continue; an owner from another task is a stale claim — run-feedback §7 Retro step 1).

**Steps:**

1. **Analysis & Architecture Phase**:
    - Execute `.agent/workflows/01-start-feature.md` (Claude Code alias: `/start-feature`).
    - This handles:
        - Archiving old TASK.md
        - Creating new TASK.md (Analysis)
        - Updating ARCHITECTURE.md (Architecture)

2. **Planning Phase**:
    - Execute `.agent/workflows/02-plan-implementation.md` (alias: `/plan`).
    - Creates PLAN.md and tasks/*.md using Stub-First strategy.

3. **Development Loop** (Automated):
    - Execute `.agent/workflows/05-run-full-task.md` (alias: `/develop-all`).
    - Executes tasks, creating stubs first, then implementing logic.

4. Final validation and commit preparation.

5. **Retro (Global Protocol)** — apply `run-feedback` SKILL.md §7 "Retro protocol":
   `claim --run-id "base-stub-first-<task-slug>"` → exit 6 = nested, SKIP this step (unless the owner is another task's run — a stale claim, run-feedback §7 Retro step 1);
   exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
   from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
   collect → triage → file per the skill, and `release`. **Non-blocking**: failures
   here are reported in one line and never change this workflow's outcome.
