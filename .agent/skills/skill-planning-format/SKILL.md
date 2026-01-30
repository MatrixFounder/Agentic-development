---
name: skill-planning-format
description: Standards for Development Plans (PLAN.md) and Detailed Task Descriptions (TASK.md).
tier: 1
version: 1.1
---

# Planning Output Format

**Purpose**: Defines the rigid structure for planning documents effectively.

## 1. Red Flags (Anti-Rationalization)
**STOP if you are thinking:**
- "I'll plan the details later" -> **WRONG**. "Later" means "Never". Breakdown must happen NOW.
- "This task is too simple for a file" -> **WRONG**. Every unit of work needs a `task-*.md` file for tracking.
- "I'll use my own format" -> **WRONG**. The Orchestrator relies on this specific structure.

## 2. Development Plan Structure (`docs/PLAN.md`)
The Main Plan acts as the "Table of Contents" for the feature.

> [!TIP]
> Use the template at `assets/templates/plan_md_template.md`.

## 3. Detailed Task Description Structure
For **each** task in the plan, you must create a separate file: `docs/tasks/task-{ID}-{SubID}-{slug}.md`.

> [!TIP]
> Use the template at `assets/templates/task_md_template.md`.

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "I don't know the implementation details yet" | That is why you are in PLANNING mode. Research until you know. |
| "Writing 5 files takes too long" | Fixing a disorganized codebase takes 10x longer. |

## 4. Result Structure Rules
1. **`docs/PLAN.md` file** — general development plan with task sequence.
2. **`docs/tasks/task-{ID}-{SubID}-{Slug}.md` files** — detailed descriptions of each task.
3. **CRITICAL:** Use only RELATIVE paths for file links (e.g., `[Link](docs/tasks/file.md)`), never absolute.

## 5. Resources
- `assets/templates/`: Standard markdown templates.
- `examples/`: Real-world planning examples.
