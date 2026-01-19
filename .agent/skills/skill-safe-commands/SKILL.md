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
^(ls|cat|head|tail|find|grep|tree|wc|stat|file|du|df)(?:\s|$)

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

## Implementation Guidelines

### For Agents (Runtime Behavior)
When calling `run_command` in **ANY** environment:
1. Check if the command matches the patterns above or the table.
2. If match found → Set `SafeToAutoRun: true`.
3. If no match → Set `SafeToAutoRun: false` (require approval).

### For Users (Configuration)
> **Note for Agents:** Do NOT create configuration files (like `.cursorrules`) automatically. These are user-managed files.

**Cursor Users:**
- Add the patterns above to your `.cursorrules` file to enable auto-approval.

**Antigravity Users:**
- Add the command list below to "Allow List Terminal Commands" setting in IDE options:
  `ls,cat,head,tail,find,grep,tree,wc,stat,file,du,df,git status,git log,git diff,git show,git branch,git remote,git tag,mv docs/TASK.md,mv docs/PLAN.md,mkdir -p docs,mkdir -p .agent,mkdir -p tests,python -m pytest,python3 -m pytest,npm test,npx jest,cargo test`

### Troubleshooting
If the IDE still requests approval for commands listed here:
1. **Agent Behavior**: Ensure the Agent is actually setting `SafeToAutoRun: true` in the tool call. If the Agent sets it to `false`, the IDE *must* ask for approval regardless of the Allow List.
2. **Prefix Matching**: Some IDEs require exact matches. If `mv docs/TASK.md` works but `mv docs/TASK.md docs/tasks/foo.md` fails, check if the IDE supports regex/glob patterns or try shortening the allowed rule (e.g., `mv` only) if security policy permits.

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
