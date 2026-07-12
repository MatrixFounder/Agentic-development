---
description: Ensure documentation is up to date
---
> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "04-update-docs-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

1. **Task Rotation Check**:
   - If `docs/TASK.md` exists and contains a *different* completed task:
     - Apply `skill-archive-task` to rotate it to `docs/tasks/` (and `docs/PLAN.md` → `docs/plans/` in lockstep, if present).
     - Create a fresh `docs/TASK.md` for this workflow.
2. Check if `docs/TASK.md` matches the current codebase state.
3. Check if `docs/ARCHITECTURE.md` matches the current codebase state.
   - If outdated, apply `skill-reverse-engineering` to regenerate from code.
   - `docs/ARCHITECTURE.md` is a living document — update in place, never per-task archive. If it exceeds 1500 lines, apply the Index-Mode split per `architecture-format-core` (`wc -l docs/ARCHITECTURE.md` → split into `docs/architectures/` chunks + short index).
4. Check if `.AGENTS.md` files are up to date.
   - Apply `skill-update-memory` to analyze recent changes and propose updates.
   - For external project onboarding/migration, run:
     - `python3 .agent/skills/skill-update-memory/scripts/suggest_updates.py --mode bootstrap --create-missing --development-root src`
5. Update any outdated documentation.
6. **Retro (Global Protocol)** — apply `run-feedback` SKILL.md §7 "Retro protocol":
   `claim --run-id "04-update-docs-<task-slug>"` → exit 6 = nested, SKIP this step;
   exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
   from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
   collect → triage → file per the skill, and `release`. **Non-blocking**: failures
   here are reported in one line and never change this workflow's outcome.
