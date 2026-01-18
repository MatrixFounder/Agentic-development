---
name: skill-archive-task
description: "Complete protocol for archiving TASK.md with ID generation. Single source of truth for archiving."
version: 1.0
tools: ["generate_task_archive_filename"]
---
# Task Archiving Protocol

This skill encapsulates the complete protocol for archiving `docs/TASK.md` to `docs/tasks/`.

## When to Archive

Archive `docs/TASK.md` **ONLY** when:
1. Starting a **NEW** task AND `docs/TASK.md` exists with **DIFFERENT** content
2. **Completing** a task (Orchestrator Completion stage)

**DO NOT** archive when:
- Refining/clarifying the **CURRENT** task (overwrite instead)
- `docs/TASK.md` does not exist

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
- Generate ID via tool with `proposed_id=None`

### Step 3: Generate Filename
Call tool:
```python
result = generate_task_archive_filename(slug="task-slug")
```

Handle response:
| Status | Action |
|--------|--------|
| `generated` | Use `result["filename"]` |
| `corrected` | Use `result["filename"]`, log warning |
| `conflict` | Notify user, STOP |
| `error` | Handle error, STOP |

### Step 4: Update Task ID
**BEFORE** moving file, update `docs/TASK.md`:
- Set Task ID to `result["used_id"]`
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

## Safe Commands (AUTO-RUN)

> See **`skill-safe-commands`** for the authoritative list of commands safe for auto-execution.

Key commands for this skill:
- `mv docs/TASK.md docs/tasks/...` — archiving
- `generate_task_archive_filename` — tool call
- `ls`, `cat` — validation

## Integration

### Required by Agents
- **Analyst** (`02_analyst_prompt.md`): Before creating new TASK.md
- **Orchestrator** (`01_orchestrator.md`): At Completion stage

### Required Tools
- `generate_task_archive_filename` — Call via native tool mechanism

## Example Flow

```
User: "Create new task for implementing login feature"

1. Agent loads skill-archive-task
2. Agent checks: docs/TASK.md exists? → YES (contains "Task 032: Archive Tool")
3. Decision: This is NEW task (different feature) → Archive
4. Extract: Task ID = 032, Slug = "task-archive-id-tool"
5. Call: generate_task_archive_filename(slug="task-archive-id-tool")
   → Returns: {filename: "task-032-task-archive-id-tool.md", used_id: "032"}
6. Verify Task ID in file = "032" (matches)
7. Execute: mv docs/TASK.md docs/tasks/task-032-task-archive-id-tool.md
8. Validate: docs/TASK.md does NOT exist ✓
9. Create new TASK.md for login feature with ID 033
```
