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
Before creating a NEW `docs/TASK.md` (Analyst) or starting a new major phase:
1.  **Check Condition**: Does `docs/TASK.md` exist and contain a different/completed task?
2.  **Extract Formatting**: Read `Task ID` and `Slug` from "0. Meta Information".
3.  **Archive**: Move the file to `docs/tasks/task-{ID}-{Slug}.md`.
    -   Command: `mv docs/TASK.md docs/tasks/task-{ID}-{Slug}.md`
4.  **Validation**: Verify the file was moved before creating the new one.

## Protocol
1. **Read First:** Before starting work, read relevant artifacts.
2. **Update Immediately:** Update artifacts corresponding to your changes (Developer updates `.AGENTS.md`, Analyst updates `TASK.md`).
3. **Consistency:** Ensure artifacts match the actual code state.
