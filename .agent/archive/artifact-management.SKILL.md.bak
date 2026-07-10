---
name: artifact-management
description: "Rules for managing local .AGENTS.md and global artifacts (TASK.md, PLAN.md, ARCHITECTURE.md)."
tier: 0
version: 1.1
---
# Artifact Management

## Local .AGENTS.md (Per-Directory)
- **Purpose:** Distributed long-term memory for specific directories.
- **Location:** In source-code directories covered by project memory policy (e.g., `src/services/.AGENTS.md`).
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
- **TASK.md:** Technical Specification. Managed by Analyst. Archived to `docs/tasks/task-NNN-slug.md`.
- **PLAN.md:** Development Plan. Managed by Planner. Rotated **in lockstep with TASK.md** to `docs/plans/plan-NNN-slug.md` (reuses the same ID/slug).
- **ARCHITECTURE.md:** System Architecture. Managed by Architect. A **LIVING document** — updated in place, **never per-task archived**. Only restructured (split into `docs/architectures/` section chunks + a short index) when it exceeds 1500 lines.

## Dual State Tracking (CRITICAL)

You serve TWO masters:
1. **Agentic Mode (Internal):** You have an internal `<appDataDir>/brain/.../task.md` for YOUR mental state. This is ephemeral and for your eyes only.
2. **Project Protocol (External):** You MUST maintain `docs/TASK.md` as the persistent Source of Truth for the TEAM.

**Resolution Rule:**
> **NEVER** let your internal `task.md` replace or obsolete the Project `docs/TASK.md`.
> You must keep `docs/TASK.md` up-to-date even if you are tracking granular steps internally.
> When "Creating a TASK", you create `docs/TASK.md`.


## Archiving Protocol (CRITICAL)

> [!IMPORTANT]
> **Complete protocol is in `skill-archive-task`.**
> This skill depends on `skill-archive-task` for archiving `docs/TASK.md` **and**
> `docs/PLAN.md` (PLAN.md rotates in lockstep with TASK.md, reusing the same ID/slug).

Before creating a NEW `docs/TASK.md`:
1. **Apply Skill**: `skill-archive-task`
2. Follow the protocol defined there (Steps 1-6 archive TASK.md → `docs/tasks/`; Step 7 archives PLAN.md → `docs/plans/` in lockstep)

See `skill-archive-task` for:
- When to Archive (conditions)
- Decision Logic (new vs refinement)
- Protocol Steps (Steps 1-6 = TASK.md; Step 7 = PLAN.md lockstep)
- Filename generation (tool or manual fallback)

> [!NOTE]
> **ARCHITECTURE.md is NOT archived.** It is a single LIVING document, updated in place
> across tasks. Its only structural operation — splitting into `docs/architectures/`
> section chunks with a short index when it exceeds 1500 lines — is defined in
> `architecture-format-core` ("Living Document & Index-Mode"), not here.

### Safe Commands (Auto-Run without Approval)

> See **`skill-safe-commands`** for the complete list of commands safe for auto-execution.

Key commands: `mv docs/TASK.md docs/tasks/...`, `mv docs/PLAN.md docs/plans/...`, `ls`, `cat` — read-only validation.

## Protocol
1. **Read First:** Before starting work, read relevant artifacts.
2. **Update Immediately:** Update artifacts corresponding to your changes (Developer updates relevant `.AGENTS.md` scopes, Analyst updates `TASK.md`).
3. **Consistency:** Ensure artifacts match the actual code state.
