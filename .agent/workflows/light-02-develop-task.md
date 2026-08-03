---
description: Develop a task using Light Mode (Dev + Review loop)
---

# Light Mode: Develop Task

> **Purpose**: Streamlined development loop for trivial tasks.
> **Skips**: Planner, Plan Reviewer, Security Audit.
> **Assumes**: `docs/TASK.md` exists with `[LIGHT]` tag.

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "light-02-develop-task-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

## Prerequisites
- `docs/TASK.md` must have `[LIGHT]` tag.
- **Skill**: `light-mode` must be loaded.

## Steps

### 1. Development (Developer)
// turbo
1. Read `System/Agents/08_developer_prompt.md`.
2. Load skill: `.agent/skills/light-mode/SKILL.md` (if not already loaded).
3. Implement the fix directly. **Do not overengineer.**
4. Run tests: `pytest` / `npm test` / relevant test command.
   <!-- loop:light-fix-loop -->
5. If tests fail: fix and re-run — **max 3 fix-and-rerun attempts**. Still red after the
   3rd attempt → **STOP**: the task is not trivial; follow the **Escalation** section below.
6. **Memory Update**: Update `.AGENTS.md` to reflect changes.

### 2. Code Review (Code Reviewer)
// turbo
1. Read `System/Agents/09_code_reviewer_prompt.md`.
2. Load skill: `.agent/skills/code-review-checklist/SKILL.md`.
3. **Security Sanity Check**: Verify no credentials leaked, no new dependencies added without approval.
   <!-- loop:light-review-loop -->
4. If issues found: Return to Step 1 (Developer) — **max 2 review cycles**. Issues still
   open after the 2nd cycle → **STOP** and follow the **Escalation** section below.
5. If approved: Proceed to Commit.

### 3. Commit & Archive (Orchestrator)
// turbo
1. Stage changes: `git add -A`.
2. Commit with message: `fix: [LIGHT] <short description>`.
3. Archive `docs/TASK.md` using `skill-archive-task` (also rotates `docs/PLAN.md` → `docs/plans/` in lockstep, if present).
4. Inform user: "Light Mode task complete."

### 4. Retro (Global Protocol)
Apply `run-feedback` SKILL.md §7 "Retro protocol":
`claim --run-id "light-02-develop-task-<task-slug>"` → exit 6 = nested, SKIP this step;
exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
collect → triage → file per the skill, and `release`. **Non-blocking**: failures
here are reported in one line and never change this workflow's outcome.

## Escalation
If the Developer or Reviewer discovers complexity (e.g., needs architecture change), **or a
loop bound above is exhausted** (repeated failures = the task is not trivial):
1. **STOP** development.
2. Inform user: "Escalating to standard pipeline."
3. Switch to the `.agent/workflows/01-start-feature.md` workflow (alias: `/start-feature`).
