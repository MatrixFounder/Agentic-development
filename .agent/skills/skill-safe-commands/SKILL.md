---
name: skill-safe-commands
description: "Centralized list of commands safe for auto-execution without user approval. Single source of truth."
version: 1.0
---
# Safe Commands Protocol

This skill defines **all commands that are SAFE TO AUTO-RUN** without user approval.

> [!IMPORTANT]
> **This is the single source of truth for Safe Commands.**
> All other skills and prompts should reference this skill instead of duplicating the list.

## Auto-Run Command Categories

| Category | Commands | Reason |
|----------|----------|--------|
| **Read-only** | `ls`, `cat`, `head`, `tail`, `find`, `grep`, `tree`, `wc` | Do not modify state |
| **File info** | `stat`, `file`, `du`, `df` | Informational only |
| **Git read** | `git status`, `git log`, `git diff`, `git show`, `git branch` | Read-only git operations |
| **Archiving** | `mv docs/TASK.md docs/tasks/...`, `mv docs/PLAN.md docs/plans/...` | Documented, non-destructive moves |
| **Directory** | `mkdir -p docs/tasks`, `mkdir -p .agent/skills/*` | Idempotent operations |
| **Tool calls** | `generate_task_archive_filename`, `list_directory`, `read_file` | Native tools |
| **Testing** | `python -m pytest ...`, `npm test`, `cargo test` | Tests don't modify source code |

## Pattern Matching Rules

Commands are safe if they match these patterns:

```
# Read-only filesystem
^(ls|cat|head|tail|find|grep|tree|wc|stat|file|du|df)\s

# Git read operations
^git\s+(status|log|diff|show|branch|remote|tag)

# Archiving (specific paths only)
^mv\s+docs/(TASK|PLAN)\.md\s+docs/(tasks|plans)/

# Directory creation (safe paths)
^mkdir\s+-p\s+(docs|\.agent|tests)/

# Python testing
^(python|python3)\s+-m\s+pytest
^cd\s+\.agent/tools\s+&&\s+python

# Node testing
^npm\s+test
^npx\s+jest

# Tool execution
^python3?\s+-c\s+'from\s+scripts\.tool_runner
```

## IDE-Specific Instructions

### Antigravity / Gemini
When calling `run_command`, set `SafeToAutoRun: true` for:
- Any command matching patterns above
- Any command explicitly listed in the table

### Cursor
Add these patterns to auto-approve settings.

## Integration

### How Other Skills Should Reference This

Instead of duplicating Safe Commands lists, use:

```markdown
## Safe Commands
See `skill-safe-commands` for the authoritative list of commands safe for auto-execution.
```

### Required by
- `skill-archive-task` — archiving commands
- `artifact-management` — file operations
- `developer-guidelines` — test commands
- All agent prompts — general command execution
