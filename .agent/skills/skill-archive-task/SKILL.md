---
name: skill-archive-task
description: "Complete protocol for archiving TASK.md and PLAN.md (lockstep) with ID generation. Single source of truth for archiving."
tier: 1
version: 1.2
---
# Task Archiving Protocol

This skill encapsulates the complete protocol for archiving `docs/TASK.md` to `docs/tasks/`
and `docs/PLAN.md` to `docs/plans/` (in lockstep with TASK.md).

## When to Archive

Archive `docs/TASK.md` **ONLY** when:
1. Starting a **NEW** task AND `docs/TASK.md` exists with **DIFFERENT** content
2. **Completing** a task (Orchestrator Completion stage)

**DO NOT** archive when:
- Refining/clarifying the **CURRENT** task (overwrite instead)
- `docs/TASK.md` does not exist

> [!IMPORTANT]
> **PLAN.md rotates in lockstep with TASK.md.** Whenever TASK.md is archived for a
> NEW task, the old `docs/PLAN.md` (if present) is archived too — see
> **"PLAN.md Archiving (Lockstep)"** below. On task refinement, PLAN.md is overwritten
> in place, never archived. `docs/ARCHITECTURE.md` is a LIVING document and is **never**
> touched by this skill.

## Decision Logic: New vs Refinement

```
IF user request implies a NEW SEPARATE feature/refactor:
    → Archive existing TASK.md, then create new
    
IF user request is a clarification/refinement of CURRENT task:
    → Overwrite TASK.md, do NOT archive
```

**Indicators of NEW task:**
- Different feature/component mentioned
- "Create new task for...", "Start working on..."
- Completed previous task

**Indicators of REFINEMENT:**
- "Clarify requirement X", "Add detail to..."
- Same feature context as current TASK.md

## Protocol Steps

### Step 1: Check Condition
```
IF NOT exists("docs/TASK.md"):
    SKIP archiving → Create new TASK.md
```

### Step 2: Extract Metadata
Read from current `docs/TASK.md`:
- **Task ID** from "0. Meta Information" section
- **Slug** from "0. Meta Information" section

**If Meta Information is missing or malformed:**
- Use slug from task title (H1 header)
- Generate ID via tool if available, otherwise use `000` or increment last known ID manually.

### Step 3: Generate Filename

**Option A: Use Tool (Preferred)**
If `generate_task_archive_filename` tool is available:
```python
result = generate_task_archive_filename(slug="task-slug")
filename = result["filename"]
```

**Option B: Manual Generation (Fallback)**
If tool is NOT available:
1. Construct filename: `task-[ID]-[slug].md` (e.g. `task-033-login-flow.md`)
2. Ensure no conflict in `docs/tasks/` (check via `ls`).


### Step 4: Update Task ID
**BEFORE** moving file, update `docs/TASK.md`:
- Set Task ID to the ID used in filename
- Ensure ID in file matches ID in filename

### Step 5: Archive (Move File)
```bash
mv docs/TASK.md docs/tasks/{filename}
```

> [!IMPORTANT]
> This command is **SAFE TO AUTO-RUN**. Do NOT wait for user approval.

### Step 6: Validate
Verify:
- [ ] `docs/TASK.md` does NOT exist
- [ ] `docs/tasks/{filename}` exists

**If validation fails:**
- Check if mv command returned error
- If `docs/TASK.md` still exists: retry mv or notify user
- DO NOT create new TASK.md until validation passes

## PLAN.md Archiving (Lockstep)

`docs/PLAN.md` has no Meta block or identity of its own, and there is always exactly
one PLAN per TASK. Therefore PLAN.md is **never archived independently** — it rotates
**in lockstep** with TASK.md, reusing the **same ID and slug** TASK.md was just archived
under.

> Result: `docs/tasks/task-NNN-slug.md` ↔ `docs/plans/plan-NNN-slug.md` always pair up.

> [!IMPORTANT]
> `docs/tasks/` is shared — it also holds planner sub-task files
> (`task-NNN-SubID-slug.md`). PLAN.md therefore archives to a **separate** `docs/plans/`
> directory, **never** to `docs/tasks/`.

### Step 7: Archive PLAN.md (Lockstep)

Run this **only after Step 6 validation passed** (TASK.md successfully archived for a
NEW task).

```
# 7.1 — Condition check
IF NOT exists("docs/PLAN.md"):
    SKIP plan archiving (no PLAN.md to rotate — task never reached planning)
    DONE

# 7.2 — Refinement guard
IF the Step 1 decision was REFINEMENT (not a NEW task):
    DO NOT archive PLAN.md — it is overwritten in place by the Planner.
    DONE
# (Step 7 is normally only reached on the NEW-task path; this guard is stated
#  explicitly so re-planning the SAME task overwrites docs/PLAN.md.)

# 7.3 — Ensure destination
mkdir -p docs/plans          # idempotent, SAFE TO AUTO-RUN

# 7.4 — Derive filename (NO new ID generation)
plan_filename = "plan-{used_id}-{slug}.md"
# CRITICAL: {used_id} and {slug} are REUSED VERBATIM from the TASK.md archive just
# completed — specifically the post-correction `used_id` returned by
# generate_task_archive_filename (Step 3), NOT the ID read from TASK.md's Meta block.
# If the tool corrected a conflicting ID (e.g. 100 -> 101), TASK and PLAN must both
# use the corrected ID to stay paired.

# 7.5 — Collision guard
IF exists("docs/plans/{plan_filename}"):
    STOP. Do NOT overwrite. Report to user:
      "Plan archive collision: docs/plans/{plan_filename} already exists."

# 7.6 — Archive (move)
mv docs/PLAN.md docs/plans/{plan_filename}

# 7.7 — Validate
ASSERT NOT exists("docs/PLAN.md")
ASSERT exists("docs/plans/{plan_filename}")
IF validation fails: retry mv once, else notify user.
```

### Edge Cases

| Case | Behavior |
|------|----------|
| `docs/PLAN.md` absent | Skip silently (7.1). Not an error — many tasks reach analysis but not planning. |
| Task refinement (same task) | Step 7.2 returns early. PLAN.md is overwritten in place by the Planner. |
| `docs/plans/` missing | `mkdir -p` in 7.3 creates it. |
| Corrected `used_id` | 7.4 uses the corrected ID, so TASK and PLAN stay paired. |
| **Orphan PLAN.md** (PLAN.md exists, no TASK.md) | Step 1 skipped archiving (no TASK.md) → Step 7 is never reached. The orphan PLAN.md is **left in place**. Warn the user it may be stale. PLAN.md has no independent ID, so it cannot be safely archived alone — this is a deliberate limitation. |

## Safe Commands (AUTO-RUN)

> See **`skill-safe-commands`** for the authoritative list of commands safe for auto-execution.

Key commands for this skill:
- `mv docs/TASK.md docs/tasks/...` — archiving TASK.md
- `mv docs/PLAN.md docs/plans/...` — archiving PLAN.md (lockstep)
- `mkdir -p docs/plans` — ensure PLAN archive destination exists
- `ls`, `cat` — validation


## Integration

### Required by Agents
- **Analyst** (`02_analyst_prompt.md`): Before creating new TASK.md
- **Orchestrator** (`01_orchestrator.md`): At Completion stage

## Example Flow

```
User: "Create new task for implementing login feature"

1. Agent loads skill-archive-task
2. Agent checks: docs/TASK.md exists? → YES (contains "Task {OLD_ID}: {Old Feature}")
3. Decision: This is NEW task (different feature) → Archive
4. Extract: Task ID = {OLD_ID}, Slug = "{old-slug}"
5. Generate Filename:
   - Try tool → If tool not found, use manual fallback
   - Fallback: Construct filename "task-{OLD_ID}-{old-slug}.md"
6. Execute: mv docs/TASK.md docs/tasks/task-{OLD_ID}-{old-slug}.md
7. Validate: docs/TASK.md does NOT exist ✓
8. PLAN Lockstep (Step 7): docs/PLAN.md exists? → YES
   - mkdir -p docs/plans
   - Reuse {OLD_ID} + {old-slug} from the TASK archive above
   - Execute: mv docs/PLAN.md docs/plans/plan-{OLD_ID}-{old-slug}.md
   - Validate: docs/PLAN.md does NOT exist ✓
9. Create new TASK.md for login feature with ID {NEW_ID}
```

