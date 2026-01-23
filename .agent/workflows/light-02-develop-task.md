---
description: Develop a task using Light Mode (Dev + Review loop)
---

# Light Mode: Develop Task

> **Purpose**: Streamlined development loop for trivial tasks.
> **Skips**: Planner, Plan Reviewer, Security Audit.
> **Assumes**: `docs/TASK.md` exists with `[LIGHT]` tag.

## Prerequisites
- `docs/TASK.md` must have `[LIGHT]` tag.
- **Skill**: `light-mode` must be loaded.

## Steps

### 1. Development (Developer)
// turbo
1. Read `System/Agents/08_agent_developer.md`.
2. Load skill: `.agent/skills/light-mode/SKILL.md` (if not already loaded).
3. Implement the fix directly. **Do not overengineer.**
4. Run tests: `pytest` / `npm test` / relevant test command.
5. If tests fail: Fix and re-run (loop).

### 2. Code Review (Code Reviewer)
// turbo
1. Read `System/Agents/09_agent_code_reviewer.md`.
2. Load skill: `.agent/skills/code-review-checklist/SKILL.md`.
3. **Security Sanity Check**: Verify no credentials leaked, no new dependencies added without approval.
4. If issues found: Return to Step 1 (Developer).
5. If approved: Proceed to Commit.

### 3. Commit & Archive (Orchestrator)
// turbo
1. Stage changes: `git add -A`.
2. Commit with message: `fix: [LIGHT] <short description>`.
3. Archive `docs/TASK.md` using `skill-archive-task`.
4. Inform user: "Light Mode task complete."

## Escalation
If the Developer or Reviewer discovers complexity (e.g., needs architecture change):
1. **STOP** development.
2. Inform user: "Escalating to standard pipeline."
3. Switch to `/01-start-feature` workflow.
