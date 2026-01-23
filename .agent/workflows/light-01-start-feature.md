---
description: Start a feature using Light Mode (fast-track for trivial tasks)
---

# Light Mode: Start Feature

> **Purpose**: Fast-track analysis for trivial tasks (typos, UI tweaks, simple bugfixes).
> **Skips**: Architecture, Planning phases.
> **Use When**: Task is low-risk. No architecture changes. No new APIs.

## Prerequisites
- Load **Skill**: `light-mode` (Tier 2).

## Steps

### 1. Analysis Phase (Analyst)
// turbo
1. Read `System/Agents/02_analyst_prompt.md`.
2. Load skill: `.agent/skills/light-mode/SKILL.md`.
3. If `docs/TASK.md` exists: Apply `skill-archive-task`.
4. Create `docs/TASK.md` with **`[LIGHT]`** tag in the title.
   - Example: `# Task 048: [LIGHT] Fix typo in README`.
5. **Skip Task Reviewer** (task is trivial).

### 2. Transition to Development
// turbo
1. Inform user: "Analysis complete. Transitioning to `/light-02-develop-task`."
2. Call `/light-02-develop-task`.

## Escalation
If the Analyst discovers that the task requires:
- Database migrations
- API changes
- New dependencies
- Security-sensitive file modifications (`auth`, `payment`, `crypto`)

**STOP** and inform the user:
> "This task is more complex than expected. Switching to standard pipeline."

Then proceed with the standard `/01-start-feature` workflow.
