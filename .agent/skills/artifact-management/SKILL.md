---
name: artifact-management
description: "Rules for managing local .AGENTS.md and global artifacts (TASK.md, ARCHITECTURE.md)."
version: 1.0
---
# Artifact Management

## Local .AGENTS.md (Per-Directory)
- **Purpose:** Distributed long-term memory for specific directories.
- **Location:** In every source code directory (e.g., `src/services/.AGENTS.md`).
- **Single Writer:** ONLY the **Developer** agent is allowed to create or update these files. All other agents (Analyst, Reviewer, etc.) must only READ them.
- **Format:**
  ```markdown
  # Directory: src/services/

  ## Purpose
  [Brief description of the directory's purpose]

  ## Files

  ### [filename.py]
  **Classes/Functions:**
  - `[ClassName]` — [Description]
    - `[method_name]` — [Description]
  ```

## Global Artifacts
- **TASK.md:** Technical Specification. Managed by Analyst.
- **ARCHITECTURE.md:** System Architecture. Managed by Architect.
- **PLAN.md:** Development Plan. Managed by Planner.


## Archiving Protocol (CRITICAL)

> [!IMPORTANT]
> **Complete protocol is in `skill-archive-task`.**
> This skill depends on `skill-archive-task` for archiving `docs/TASK.md`.

Before creating a NEW `docs/TASK.md`:
1. **Apply Skill**: `skill-archive-task`
2. Follow the 6-step protocol defined there

See [skill-archive-task](file:///Users/sergey/Antigravity/agentic-development/.agent/skills/skill-archive-task/SKILL.md) for:
- When to Archive (conditions)
- Decision Logic (new vs refinement)
- Protocol Steps (6 steps)
- Tool usage (`generate_task_archive_filename`)

### Safe Commands (Auto-Run without Approval)

> See **`skill-safe-commands`** for the complete list of commands safe for auto-execution.

Key commands: `mv docs/TASK.md docs/tasks/...`, `generate_task_archive_filename`, read-only commands.

## Protocol
1. **Read First:** Before starting work, read relevant artifacts.
2. **Update Immediately:** Update artifacts corresponding to your changes (Developer updates `.AGENTS.md`, Analyst updates `TASK.md`).
3. **Consistency:** Ensure artifacts match the actual code state.
