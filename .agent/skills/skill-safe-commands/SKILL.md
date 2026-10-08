---
name: skill-safe-commands
description: "Centralized list of commands safe for auto-execution without user approval. Single source of truth."
tier: 0
version: 1.5
---
# Safe Commands Protocol

This skill defines **all commands that are SAFE TO AUTO-RUN** without user approval.

> [!IMPORTANT]
> **This is the single source of truth for Safe Commands.**
> All other skills and prompts should reference this skill instead of duplicating the list.

## Auto-Run Command Categories

| Category | Commands | Reason |
|----------|----------|--------|
| **Read-only** | `ls`, `cat`, `head`, `tail`, `grep`, `rg`, `fd`, `wc`, `echo` | Do not modify state; `rg` and `fd` without the options that run a program |
| **Symlink-aware** | `ls -L`, `rg --follow` / `rg -L`, `fd -L` | Read-only, but follow symlinks into framework dirs (`.agent/`, `.agents/`, `.cursor/skills/`, `System/`, `.agentic-development/`). Plain `find`/`ls`/`rg` do **not** descend into symlinked directories |
| **File info** | `stat`, `du`, `df` | Informational only |
| **Git read** | `git status`; `git log`, `git diff`, `git show` without `--output`; `git branch`, `git remote`, `git tag` with no argument | Read-only git operations |
| **Archiving** | `python3 .agent/tools/archive_move.py` | Moves `docs/TASK.md` and `docs/PLAN.md` into `docs/tasks/` and `docs/plans/`; refuses every other operand (TASK 112) |
| **Directory** | `mkdir -p docs/tasks`, `mkdir -p docs/plans`, `mkdir -p docs/architectures` | Idempotent; three fixed directories |
| **Tool calls** | `generate_task_archive_filename`, `list_directory`, `read_file` | Native tools |
| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py`, `python3 .agent/skills/artifact-formalizer/evals/grade_run.py`, `python3 System/scripts/doctor.py` | Framework automation; `rebase_links.py` writes markdown in the working directory by real path, `init_skill.py` by path |
| **Testing** | `python -m pytest`, `python3 -m pytest`, `npm test`, `cargo test`, with no argument | Their options can run a program, delete a directory or overwrite a file (TASK 111 D14) |

> [!IMPORTANT]
> **`artifact-formalizer/evals/run_authoring.py` is deliberately NOT on this list.** The other two
> eval scripts read files and spawn nothing. `run_authoring.py` spawns `claude -p` once per arm per
> case and spends tokens, so it requires approval on every invocation.

## Pattern Matching Rules

Commands are safe if they match these patterns:

- **From the project root only.** The framework-script patterns name paths relative to the project
  root. Run from another directory, the same text names another file, such as a nested checkout's
  script of the same path.
- **In the project's own work tree only.** The test-runner patterns run the code of the directory
  they start in: a nested checkout's `conftest.py` or `package.json` scripts.
- **Enforcement.** No hook enforces these two conditions yet: an allow list cannot see the
  working directory, so the agent runs these commands from the project root. A PreToolUse hook to
  make a relative-path command ask inside a nested checkout is deferred to WI-34.
- **`find` is not on this list.** `-exec`, `-execdir`, `-ok` and `-delete` run a command or
  delete files, and a pattern cannot tell them apart; `find` asks for approval.
- **Options that run a program.** `rg --pre` and `rg --hostname-bin` run a program, and so do
  `fd -x`, `fd -X`, `--exec` and `--exec-batch`. The `rg` and `fd` patterns exclude these options
  wherever they stand. ripgrep 14.1.1 rejects an abbreviated long option; the `fd` pattern excludes
  every long option that starts with `--exe`, and `x` or `X` anywhere in a short-option cluster,
  digits included (`fd -1x`).
- **Archiving runs through a script.** `archive_move.py` accepts `docs/TASK.md` with
  `docs/tasks/task-<ID>-<slug>.md` and `docs/PLAN.md` with `docs/plans/plan-<ID>-<slug>.md`, and
  refuses every other operand, a link and an existing file. The pattern admits any operand
  because the script is the guard (TASK 112 R1).
- **No `file`.** `file` is off this list: `-C`, and its abbreviation `--co`, write a compiled
  magic file (TASK 112 D2).
- **An allow rule names its command whole.** `X *` matches `X` with arguments; `X*` also matches
  every command whose name starts with `X`, such as `git difftool` for `git diff*`. Each pattern
  ends at its command or its script's name for the same reason.
- **Read forms only.** `--output` makes `git log`, `git diff` and `git show` write a file. With an
  argument, `git branch`, `git tag` and `git remote` create or delete a ref or change a remote.
  `tree -o` writes a file, so `tree` is off this list. Claude Code's built-in check approves the
  read forms of `git` with no rule, and the committed settings name only the bare forms of these
  commands (TASK 111 D13).
- **Test runners with no argument.** An option of `pytest`, `npm test`, `jest` or `cargo test` can
  run a program, delete a directory or overwrite a file. The patterns match the bare commands
  only. `npx jest` is off this list: it downloads jest when the project has none (TASK 111 D14).
- **Each simple command, after quote removal.** A pattern applies to each simple command of a
  compound command, after the shell removes its quotes. A simple command with an output
  redirection to a file other than `/dev/null`, a command substitution or a process substitution
  is not safe. Neither is a command with a line continuation, `$'…'` or `$"…"` quoting, a
  parameter or brace expansion, or, for `rg`, `fd` and `git`, an unquoted glob: the shell can turn
  each into an option the patterns never see. Neither is a command the agent cannot reduce that
  way.

```
# Read-only filesystem
^(ls|cat|head|tail|grep|wc|stat|du|df|echo)(?:\s|$)

# Symlink-aware listing — framework dirs (.agent/, .agents/, System/, .agentic-development/) may be symlinks
^ls\s+-[a-zA-Z]*L

# rg and fd, except the options that run a program; -L and --follow follow symlinks
^rg(?![\s\S]*\s--(?:pre|hostname-bin)(?:[=\s]|$))(?:\s|$)
^fd(?![\s\S]*\s(?:-[^-\s]*[xX]|--exe))(?:\s|$)

# Git read operations (the boundary keeps `git difftool -x <program>` out; `--output` writes a file)
^git\s+(status|log|diff|show)(?![\s\S]*\s--output)(\s|$)
^git\s+(branch|remote|tag)$

# Archiving: the script refuses every operand but the two archive pairs
^python3\s+\.agent/tools/archive_move\.py(\s|$)

# Directory creation (three fixed directories)
^mkdir\s+-p\s+docs/(tasks|plans|architectures)$

# Python testing (bare forms only)
^(python|python3)\s+-m\s+pytest$

# Node and Rust testing (bare forms only)
^npm\s+test$
^cargo\s+test$

# Framework scripts (each pattern ends at the script's name)
^python3\s+\.agent/skills/skill-session-state/scripts/update_state\.py(\s|$)
^python3\s+\.agent/tools/task_id_tool\.py(\s|$)
^python3\s+\.agent/tools/rebase_links\.py(\s|$)
^python3\s+\.agent/skills/skill-creator/scripts/(validate_skill|init_skill)\.py(\s|$)
^python3\s+\.agent/skills/artifact-formalizer/scripts/(scan_register|selftest_scan)\.py(\s|$)
^python3\s+\.agent/skills/artifact-formalizer/evals/(selftest_evals|grade_run)\.py(\s|$)
^python3\s+System/scripts/doctor\.py(\s|$)
```

## Implementation Guidelines

### For Agents (Runtime Behavior)
When calling `run_command` in **ANY** environment:
1. Check whether the command matches a pattern above. The table names the same commands; it
   approves no command that no pattern matches.
2. If match found → Set `SafeToAutoRun: true`.
3. If no match → Set `SafeToAutoRun: false` (require approval).

> [!IMPORTANT]
> **Symlink-following is the default for framework paths.** When listing or
> searching `.agent/`, `.agents/`, `.cursor/skills/`, `System/`, or
> `.agentic-development/`, prefer the symlink-aware variants (`ls -L`,
> `rg --follow`, `fd -L`) — a plain `ls`/`rg`/`fd` silently skips symlinked
> directories. If a read-only probe returns **nothing** under a known
> framework directory, retry it **once** with symlink-following enabled before
> treating the path as empty or missing.

### For Users (Configuration)
> **Note for Agents:** Do NOT create configuration files (like `.cursorrules` or `AGENTS.md`) automatically. These are user-managed files.

**Cursor Users:**
- Add the patterns above to your `.cursorrules` or `AGENTS.md` file to enable auto-approval.

**Antigravity Users:**
- Add the command list below to "Allow List Terminal Commands" setting in IDE options:
  `ls,cat,head,tail,grep,wc,stat,du,df,git status,python3 .agent/tools/archive_move.py`
- Antigravity matches an entry as an exact word or token prefix, so `ls` does not admit `lsof`
  (antigravity.google/docs/permissions, read 2026-10-06). A chain or a pipeline of listed
  commands still matches, and so does a simple file redirect, which writes. A command or process
  substitution turns prefix matching off for the whole line.
- An entry cannot exclude an option, so the list names only commands with no option that writes
  or runs a program. `rg`, `fd`, `mkdir` and the test runners ask; from `git`, only `git status`
  is listed. The agent's `SafeToAutoRun` still rejects a redirect (Troubleshooting item 1).
  `python3 .agent/tools/archive_move.py` admits any operand as a prefix entry; the script refuses
  every operand but the two archive pairs. Its path is relative, like every framework-script
  pattern, so the agent runs it from the project root (WI-34).

### Troubleshooting
If the IDE still requests approval for commands listed here:
1. **Agent Behavior**: Ensure the Agent is actually setting `SafeToAutoRun: true` in the tool call. If the Agent sets it to `false`, the IDE *must* ask for approval regardless of the Allow List.
2. **Prefix Matching**: Antigravity matches a word or token prefix. If `git status` runs unasked
   but a longer command asks, check whether the command carries a construct that turns prefix
   matching off, such as a command substitution. Do not shorten an entry to a bare command such
   as `mv` or `git`: it then admits every form of that command.

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
