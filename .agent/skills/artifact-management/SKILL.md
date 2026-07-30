---
name: artifact-management
description: "Rules for managing local .AGENTS.md and global artifacts (TASK.md, PLAN.md, ARCHITECTURE.md, KNOWN_ISSUES.md, BACKLOG.md)."
tier: 0
version: 1.4
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
- **KNOWN_ISSUES.md:** Known-issues ledger. A **LIVING, hand-maintained thin index** (one file per issue under `docs/issues/`) — updated in place, **never per-task archived**. Its **format is defined in `known-issues-format`, not here** (the frontmatter schema, prefix→category table, status/severity vocab, index-line format, and per-issue recipe live there — parallel to how `ARCHITECTURE.md`'s structure lives in `architecture-format-core`). **Create-if-absent:** if the ledger is missing when you record an issue, first materialize it from `known-issues-format`'s `assets/templates/known_issues_md_template.md`, then file the issue.
- **BACKLOG.md:** Work-item ledger — enhancements, polish, and signals with no broken contract (defects go to `KNOWN_ISSUES.md`). Also a **LIVING, hand-maintained thin index** (one file per work-item under `docs/backlog/`), updated in place, **never per-task archived**, and **human-ranked** — no machine-imposed sort. Its **format is defined in `known-issues-format`** too (same skill, Registry B: `type: work-item`, `WI-<n>`, `open/done/dropped`, optional `effort/value/source`, index line after the `<!-- feedback:discovered-issues -->` anchor). **Create-if-absent** from that skill's `assets/templates/backlog_md_template.md` — unless the project already tracks work under another name (`docs/ROADMAP.md`, an iteration backlog), in which case seat the anchor in **that** file rather than starting a second ledger.

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
