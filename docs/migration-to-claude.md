# Migration Specification: Claude Code Adaptation

**Version:** 1.1
**Status:** Implementation Complete
**Source Framework:** Multi-Agent Software Development System v3.9.14
**Target Platform:** Claude Code (Anthropic CLI)

### Specification Refinement Log

| Change | Status |
|---|---|
| Expanded command list from 10 to 20 (all 21 workflows covered) | Done |
| Added `References/migrate_workflows_to_commands.py` as prior art reference | Done |
| VDD sub-commands use clean names (no numeric prefix) | Done |
| `/light` kept as single combined command | Done |
| Added "ON PHASE BOUNDARY" `update_state.py` instruction to `AGENTS.md` | Done |
| Added "Platform Memory Integration" section to `System/Docs/SESSION_CONTEXT_GUIDE.md` | Done |

### Implementation Task Status

| Task | Priority | Status |
|---|---|---|
| Task 1: Create `CLAUDE.md` | Critical | **Done** |
| Task 2: Create `.claude/settings.json` | Critical | **Done** |
| Task 3: Create `.claude/commands/` (20 files) | High | **Done** |
| Task 4: Replace tool_runner references in CLAUDE.md | High | **Done** (part of Task 1) |
| Task 5: Adapt session state bootstrap in CLAUDE.md | High | **Done** (part of Task 1) |
| Task 6: Port skill validation hook | Medium | **Done** |
| Task 7: Adapt Tier loading in CLAUDE.md | Medium | **Done** (part of Task 1) |
| Task 8: Update `README.md` "Option C" section | Low | **Done** |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Platform Differences](#3-platform-differences)
4. [Migration Tasks](#4-migration-tasks)
   - [Task 1: Create CLAUDE.md](#task-1-create-claudemd)
   - [Task 2: Create .claude/settings.json with hooks](#task-2-create-claudesettingsjson-with-hooks)
   - [Task 3: Register workflows as Claude Code commands](#task-3-register-workflows-as-claude-code-commands)
   - [Task 4: Replace tool_runner references with native tools](#task-4-replace-tool_runner-references-with-native-tools)
   - [Task 5: Adapt session state bootstrap](#task-5-adapt-session-state-bootstrap)
   - [Task 6: Port skill validation hook](#task-6-port-skill-validation-hook)
   - [Task 7: Adapt Tier loading for Claude Code context model](#task-7-adapt-tier-loading-for-claude-code-context-model)
   - [Task 8: Update README.md installation section](#task-8-update-readmemd-installation-section)
5. [CLAUDE.md Specification](#5-claudemd-specification)
6. [.claude/settings.json Specification](#6-claudesettingsjson-specification)
7. [Commands Specification](#7-commands-specification)
8. [Tool Mapping Reference](#8-tool-mapping-reference)
9. [Validation Checklist](#9-validation-checklist)

---

## 1. Executive Summary

The framework currently supports Cursor IDE (via `AGENTS.md`), Gemini CLI (via `GEMINI.md`), and Antigravity. Claude Code support is described in `README.md` section "Option C" but has not been implemented: there is no `CLAUDE.md`, no `.claude/settings.json`, no registered commands, and no hooks. The `.claude/` directory is empty (only a symlink `.cursor/skills -> .agent/skills` exists for Cursor, not for Claude Code).

This document specifies all steps required to achieve full Claude Code integration at parity with the Gemini CLI implementation.

---

## 2. Current State Analysis

### What exists

| Component | Path | Status |
|---|---|---|
| Framework core | `System/`, `.agent/` | Complete |
| Cursor entry point | `AGENTS.md` | Complete |
| Gemini entry point | `GEMINI.md` | Complete |
| Gemini hooks | `.gemini/settings.json`, `.gemini/hooks/` | Complete |
| Cursor skills symlink | `.cursor/skills -> .agent/skills` | Complete |
| Agent prompts | `System/Agents/*.md` (15 files) | Complete |
| Skills | `.agent/skills/` (45+ skills) | Complete |
| Workflows | `.agent/workflows/` (21 workflows) | Complete |
| Session state | `.agent/sessions/latest.yaml` | Complete |
| Tool schemas | `.agent/tools/schemas.py` | Complete |

### What is missing for Claude Code

| Component | Path | Status |
|---|---|---|
| Claude Code entry point | `CLAUDE.md` | **Missing** |
| Claude Code settings | `.claude/settings.json` | **Missing** |
| Claude Code commands | `.claude/commands/*.md` | **Missing** |
| Skill validation hook (Claude) | `.claude/settings.json` hooks section | **Missing** |
| Tool mapping documentation | Within `CLAUDE.md` | **Missing** |

---

## 3. Platform Differences

### 3.1. System Prompt Mechanism

| Feature | Gemini CLI | Cursor IDE | Claude Code |
|---|---|---|---|
| System prompt file | `GEMINI.md` | `AGENTS.md` (context rules) | `CLAUDE.md` |
| Auto-loading | Yes | Yes | Yes |
| Skill directory | `.agent/skills/` (native) | `.cursor/skills` (symlink) | No native skill auto-loading |
| Slash commands | In-chat (`/workflow-name`) | Composer | `.claude/commands/*.md` |

### 3.2. Tool Availability

Claude Code provides built-in tools that replace the framework's `tool_runner.py`:

| Framework Tool (schemas.py) | Claude Code Built-in | Notes |
|---|---|---|
| `read_file(path)` | `Read` tool | Direct replacement |
| `write_file(path, content)` | `Write` tool | Direct replacement |
| `list_directory(path, recursive)` | `Glob` tool / `Bash ls` | `Glob` is preferred |
| `run_tests(command, timeout)` | `Bash` tool | No whitelist enforcement; Claude Code has own permission model |
| `git_status()` | `Bash git status` | Direct replacement |
| `git_add(files)` | `Bash git add` | Direct replacement |
| `git_commit(message)` | `Bash git commit` | Direct replacement |
| `generate_task_archive_filename()` | `Bash python3 .agent/tools/task_id_tool.py` | Needs explicit invocation |

### 3.3. Hook System

| Feature | Gemini CLI | Claude Code |
|---|---|---|
| Config file | `.gemini/settings.json` | `.claude/settings.json` |
| Hook types | `AfterTool` with `matcher` regex | `PreToolUse`, `PostToolUse`, `Notification`, `Stop` |
| Matcher | Tool name regex (`write_file\|replace_file_content`) | Tool name string (e.g., `Write`, `Edit`) |
| Hook format | `command` with stdin JSON | `command` array with env vars |
| Decision output | JSON `{"decision":"allow\|deny"}` | Exit code: 0=allow, 2=block; stdout = user message |

### 3.4. Commands vs Workflows

| Feature | Gemini / Cursor | Claude Code |
|---|---|---|
| Invocation | `run workflow-name` or `/workflow-name` in chat | `/command-name` triggers Skill tool |
| Definition | `.agent/workflows/*.md` (read by agent) | `.claude/commands/*.md` (injected as prompt) |
| Format | Markdown with YAML frontmatter | Markdown with `$ARGUMENTS` placeholder |

---

## 4. Migration Tasks

### Task 1: Create CLAUDE.md

**Priority:** Critical
**Effort:** Medium
**Dependencies:** None

**Source file:** `GEMINI.md` (117 lines) — the most platform-neutral driver in the project.
**Why not AGENTS.md:** `AGENTS.md` contains Cursor-specific references (`.cursor/skills`, "Composer Cmd+I"). `GEMINI.md` is cleaner: it references `.agent/skills/` directly and has no IDE-specific language.

**Description:**
Create `CLAUDE.md` in the project root. Copy `GEMINI.md` and apply the following changes:

1. Replace Gemini-specific tool references:
   - `GEMINI.md` line 22-27 (Tool Execution Protocol): references `schemas.py` and `execute_tool` dispatcher
   - Replace with: "Use your built-in tools: Read (files), Write (files), Edit (files), Bash (commands, git, tests), Grep (search), Glob (find files)"
   - Remove: "Sources: Definitions in `.agent/tools/schemas.py`"
   - Remove: "execute it using the `execute_tool` dispatcher"

2. Replace safe commands section (GEMINI.md lines 36-38):
   - Claude Code manages permissions via `.claude/settings.json`
   - Keep the concept but reference Claude Code's permission model instead of `SafeToAutoRun`

3. Adapt workflow dispatch section (GEMINI.md lines 47-64):
   - Replace `run workflow-name` / `/workflow-name` in-chat syntax with reference to `.claude/commands/` slash commands
   - Remove `Call /workflow-name` nested call syntax (Claude Code commands don't support nesting; instead, instruct Claude to read the workflow file directly)

4. Adapt self-improvement section (GEMINI.md lines 108-117):
   - Change "modifications to `GEMINI.md` file itself" -> "modifications to `CLAUDE.md` file itself"

5. Keep intact (copy as-is from GEMINI.md):
   - Critical instruction (line 6-7)
   - Skills system architecture (lines 9-12)
   - Session restoration / bootstrap (lines 14-19)
   - Context loading protocol (lines 40-45)
   - The pipeline — all 4 phases (lines 66-97)
   - Behavior rules (lines 99-101)
   - Critical rule about not skipping phases (lines 103-106)
   - Tier 0 skill loading (lines 29-34)

**Detailed specification:** See [Section 5](#5-claudemd-specification).

---

### Task 2: Create .claude/settings.json with hooks

**Priority:** Critical
**Effort:** Small
**Dependencies:** Task 6 (hook script)

**Description:**
Create `.claude/settings.json` to configure:

1. Post-tool hooks for skill validation (equivalent to `.gemini/settings.json`)
2. Allowed tools / permission defaults (optional)

**Detailed specification:** See [Section 6](#6-claudesettingsjson-specification).

---

### Task 3: Register workflows as Claude Code commands

**Priority:** High
**Effort:** Medium
**Dependencies:** Task 1

**Description:**
Create `.claude/commands/` directory with command files for key workflows. Each command is a markdown file that gets injected as a prompt when the user types `/command-name`.

**Commands to register:**

| Command File | Source Workflow | Description |
|---|---|---|
| `start-feature.md` | `01-start-feature.md` | Analysis + Architecture |
| `plan.md` | `02-plan-implementation.md` | Planning phase |
| `develop.md` | `03-develop-single-task.md` | Develop single task |
| `develop-all.md` | `05-run-full-task.md` | Loop all tasks |
| `light.md` | `light-01-start-feature.md` + `light-02-develop-task.md` | Fast-track |
| `vdd.md` | `vdd-enhanced.md` | VDD Enhanced pipeline |
| `vdd-start-feature.md` | `vdd-01-start-feature.md` | VDD Analysis + Architecture |
| `vdd-plan.md` | `vdd-02-plan.md` | VDD Planning phase |
| `vdd-develop.md` | `vdd-03-develop.md` | VDD Development phase |
| `vdd-adversarial.md` | `vdd-adversarial.md` | VDD Adversarial testing |
| `vdd-multi.md` | `vdd-multi.md` | VDD Multi-task pipeline |
| `full.md` | `full-robust.md` | Full pipeline + security |
| `security-audit.md` | `security-audit.md` | Security audit |
| `base-stub-first.md` | `base-stub-first.md` | Standard full pipeline |
| `update-docs.md` | `04-update-docs.md` | Documentation update |
| `framework-upgrade.md` | `framework-upgrade.md` | Framework upgrade |
| `iterative-design.md` | `iterative-design.md` | Iterative design |
| `product-full-discovery.md` | `product-full-discovery.md` | Full product discovery |
| `product-market-only.md` | `product-market-only.md` | Market-only product analysis |
| `product-quick-vision.md` | `product-quick-vision.md` | Quick product vision |

**Command file format:**
```markdown
# Workflow: [Name]

Read and execute the workflow defined in `.agent/workflows/[source].md`.

$ARGUMENTS
```

Each command file instructs Claude to read the corresponding workflow from `.agent/workflows/` and execute it. This preserves the single source of truth in `.agent/workflows/` while providing Claude Code slash command access.

**Prior art:** `References/migrate_workflows_to_commands.py` exists and generates command mirrors from workflows. However, it uses a content-duplication approach (copies full workflow body into command files) and generates Gemini/Cursor-specific artifacts (`run.md` router, `_workflow_index.json`). It is **not suitable as-is** for Claude Code migration. The thin delegator approach above is preferred. The script may be adapted for Claude Code format in a future iteration.

**Detailed specification:** See [Section 7](#7-commands-specification).

---

### Task 4: Replace tool_runner references with native tools

**Priority:** High
**Effort:** Small
**Dependencies:** Task 1

**Description:**
In `CLAUDE.md` (and optionally in agent prompts), replace references to custom tool functions with Claude Code native equivalents.

**Changes in CLAUDE.md (relative to GEMINI.md source):**

| Original (GEMINI.md) | Replacement (CLAUDE.md) |
|---|---|
| "ALWAYS use native tools (`run_tests`, `git_ops`, `file_ops`, `generate_task_archive_filename`)" (line 26) | "Use your built-in tools: Read (files), Write (files), Edit (files), Bash (commands, git, tests), Grep (search), Glob (find files)" |
| "execute it using the `execute_tool` dispatcher" (line 25) | Remove entirely; Claude Code dispatches tools natively |
| "Sources: Definitions in `.agent/tools/schemas.py`" (line 24) | Remove; tools are built-in |
| `generate_task_archive_filename` references | "Run `python3 .agent/tools/task_id_tool.py <slug>` via Bash tool" |
| "modifications to `GEMINI.md` file itself" (line 110) | "modifications to `CLAUDE.md` file itself" |

**Not changed:**
- Agent prompt files (`System/Agents/*.md`) do not need modification: they reference skills and concepts, not specific tool implementations. The orchestrator (CLAUDE.md) handles tool routing.
- Skill files (`.agent/skills/*/SKILL.md`) remain unchanged: they describe methodology, not tooling.

---

### Task 5: Adapt session state bootstrap

**Priority:** High
**Effort:** Small
**Dependencies:** Task 1

**Description:**
Add session restoration instructions to `CLAUDE.md` that work with Claude Code's execution model:

```markdown
## SESSION RESTORATION (BOOTSTRAP)
**ON SESSION START**:
1. Read `.agent/sessions/latest.yaml` using the Read tool.
2. **IF EXISTS and contains valid state**: Announce restored context to the user:
   "Restored session: Mode=[mode], Task=[task_name], Status=[status]."
3. **IF NOT EXISTS or empty**: Proceed with new task analysis.
4. **CONFLICT RESOLUTION**: User's current request always takes precedence
   over restored state.

**ON PHASE BOUNDARY** (after completing each pipeline stage):
1. Run via Bash: `python3 .agent/skills/skill-session-state/scripts/update_state.py --mode "[Mode]" --task "[TaskName]" --status "[Status]" --summary "[Summary]"`
2. This persists context for session recovery.
```

**Integration with Claude Code memory:**
Claude Code has its own auto-memory system (`~/.claude/projects/*/memory/`). The framework's session state (`.agent/sessions/latest.yaml`) serves a different purpose: it tracks pipeline progress (which phase, which task), not long-term project knowledge. Both systems complement each other:
- `.agent/sessions/latest.yaml` = pipeline execution state (ephemeral)
- Claude Code memory = project patterns and preferences (persistent)

---

### Task 6: Port skill validation hook

**Priority:** Medium
**Effort:** Medium
**Dependencies:** Task 2

**Description:**
Create a Claude Code-compatible hook that validates skills when files in `.agent/skills/` are modified.

**Source:** `.gemini/hooks/validate_skill_hook.sh`
**Target:** New script at `.claude/hooks/validate_skill_hook.sh`

**Key differences from Gemini version:**

| Aspect | Gemini Hook | Claude Code Hook |
|---|---|---|
| Input | JSON on stdin (`tool_input.file_path`) | File path via `$TOOL_INPUT` env var or parse from hook context |
| Output | JSON `{"decision":"allow"}` on stdout | Exit code 0 (allow) or 2 (block); message on stdout |
| Trigger | `AfterTool` matcher regex | `PostToolUse` on `Write` and `Edit` tools |
| Config | `.gemini/settings.json` | `.claude/settings.json` |

**Hook logic (Claude Code format):**
1. Parse the file path from the tool context (environment variable or stdin)
2. Check if the file is inside `.agent/skills/`
3. If yes: run `python3 .agent/skills/skill-creator/scripts/validate_skill.py <skill-dir>`
4. If validation fails: print warning message, exit 0 (warn but allow)
5. If validation passes: exit 0 silently

**Note:** Claude Code hooks receive information differently from Gemini hooks. The exact input mechanism depends on the hook event type:
- `PreToolUse` / `PostToolUse`: Receive tool name and input as environment variables
- The hook script must be adapted to read from the correct source

---

### Task 7: Adapt Tier loading for Claude Code context model

**Priority:** Medium
**Effort:** Small
**Dependencies:** Task 1

**Description:**
Claude Code does not have native tier-based skill loading. The tier system must be implemented as instructions in `CLAUDE.md`.

**Approach:**

In `CLAUDE.md`, add explicit loading instructions:

```markdown
### Skill Loading Protocol

**TIER 0 (Always load at session start):**
Read these skill files immediately using the Read tool:
- `.agent/skills/core-principles/SKILL.md`
- `.agent/skills/skill-safe-commands/SKILL.md`
- `.agent/skills/artifact-management/SKILL.md`
- `.agent/skills/skill-session-state/SKILL.md`

**TIER 1 (Load when entering a phase):**
When transitioning to a pipeline phase, read the corresponding skills:
- Analysis: `requirements-analysis`, `skill-archive-task`
- Architecture: `architecture-design`, `architecture-format-core`
- Planning: `planning-decision-tree`, `tdd-stub-first`
- Development: `developer-guidelines`, `documentation-standards`
- Review: `code-review-checklist` (or phase-specific checklist)

**TIER 2+ (Load only when explicitly needed):**
Read these skills only when their functionality is required:
- `skill-reverse-engineering`, `vdd-adversarial`, `security-audit`, etc.
```

**Context optimization:**
Since Claude Code has automatic context compression, aggressive tier management is less critical than in Gemini CLI. However, loading all 45 skills at once would still degrade quality. The tier instructions ensure skills are loaded at the right phase.

---

### Task 8: Update README.md installation section

**Priority:** Low
**Effort:** Small
**Dependencies:** Tasks 1-7

**Description:**
Update `README.md` section "Option C: Claude Code" to reflect the completed migration:

**Current text (README.md lines 87-96):**
```markdown
#### Option C: Claude Code (Native)
To use with Anthropic's `claude` CLI:
1. Configuration: Create a dedicated `CLAUDE.md` adapted from `AGENTS.md`...
2. Prompt Compatibility: In `CLAUDE.md`, keep pipeline rules intact...
3. Skills: Create a `.claude/skills` symlink...
4. Usage: Run `claude` in the project root.
```
Note: The README currently says "adapted from `AGENTS.md`" — after this migration, `CLAUDE.md` is adapted from `GEMINI.md` and ships ready-to-use.

**Updated text (after migration):**
```markdown
#### Option C: Claude Code (Native)
To use with Anthropic's `claude` CLI:
1. **Configuration**: `CLAUDE.md` is included and ready to use.
2. **Hooks**: `.claude/settings.json` auto-validates skills on modification.
3. **Commands**: Available slash commands (in `.claude/commands/`):
   - `/start-feature` — Analysis + Architecture
   - `/plan` — Planning phase
   - `/develop` — Develop single task
   - `/develop-all` — Loop all tasks
   - `/light` — Fast-track for trivial tasks
   - `/vdd` — VDD Enhanced pipeline
   - `/vdd-start-feature` — VDD Analysis + Architecture
   - `/vdd-plan` — VDD Planning phase
   - `/vdd-develop` — VDD Development phase
   - `/vdd-adversarial` — VDD Adversarial testing
   - `/vdd-multi` — VDD Multi-task pipeline
   - `/full` — Full pipeline + Security Audit
   - `/security-audit` — Security audit
   - `/base-stub-first` — Standard full pipeline
   - `/update-docs` — Documentation update
   - `/framework-upgrade` — Framework upgrade
   - `/iterative-design` — Iterative design
   - `/product-full-discovery` — Full product discovery
   - `/product-market-only` — Market-only product analysis
   - `/product-quick-vision` — Quick product vision
4. **Usage**: Run `claude` in the project root. `CLAUDE.md` loads automatically.
```

---

## 5. CLAUDE.md Specification

### Source and structure

**Base file:** `GEMINI.md` (117 lines).
`CLAUDE.md` inherits the structure of `GEMINI.md` with targeted modifications:

```
# CLAUDE.md — AUTOMATED ORCHESTRATION MODE          ← same as GEMINI.md

## CRITICAL INSTRUCTION                              ← copy from GEMINI.md
## SKILLS SYSTEM ARCHITECTURE                        ← copy from GEMINI.md
## SESSION RESTORATION (BOOTSTRAP)                   ← copy from GEMINI.md
## TOOL EXECUTION PROTOCOL                           ← MODIFIED: native Claude Code tools
### TIER 0 Skills                                    ← copy from GEMINI.md
### Safe Commands                                    ← MODIFIED: Claude Code permissions
## CONTEXT LOADING PROTOCOL                          ← copy from GEMINI.md
## SKILL LOADING PROTOCOL (TIERS)                    ← NEW: explicit tier instructions
## WORKSPACE WORKFLOWS (COMMANDS)                    ← MODIFIED: .claude/commands/ dispatch
## THE PIPELINE (EXECUTE SEQUENTIALLY)               ← copy from GEMINI.md (lines 66-97)
  1. Analysis Phase
  2. Architecture Phase
  3. Planning Phase
  4. Development Phase
## BEHAVIOR RULES                                    ← copy from GEMINI.md
## CRITICAL RULE                                     ← copy from GEMINI.md
## SELF-IMPROVEMENT MODE                             ← MODIFIED: GEMINI.md → CLAUDE.md ref
```

### Key differences from GEMINI.md (source)

| Section | GEMINI.md (source) | CLAUDE.md (target) |
|---|---|---|
| Tool execution | `schemas.py` + `execute_tool` dispatcher | Built-in Read/Write/Edit/Bash/Grep/Glob |
| Safe commands | `SafeToAutoRun: true` + skill reference | Reference to `.claude/settings.json` permissions |
| Workflow dispatch | `run workflow-name` / `/workflow-name` in chat, `Call /workflow-name` nesting | `/command-name` via `.claude/commands/` |
| Session state | `skill-session-state` scripts | Same + note about Claude Code auto-memory |
| Self-improvement | "modifications to `GEMINI.md`" | "modifications to `CLAUDE.md`" |
| Tier loading | Implicit (agents know tiers) | Explicit tier loading instructions added |
| Skills path | `.agent/skills/` | `.agent/skills/` (no change) |

### Content guidelines

1. **Do not duplicate skill content** in CLAUDE.md. Reference skills by path.
2. **Keep under 200 lines** to avoid context bloat at session start. GEMINI.md is 117 lines; aim for 130-150 after additions.
3. **Use imperative language** (MUST, ALWAYS, NEVER) consistent with GEMINI.md style.
4. **Preserve pipeline structure** exactly as in GEMINI.md (same 4 phases, same agents, same order).

---

## 6. .claude/settings.json Specification

### Format

Claude Code settings use the following structure:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/validate_skill_hook.sh"
          }
        ]
      }
    ]
  }
}
```

### Hook script requirements

**File:** `.claude/hooks/validate_skill_hook.sh`

**Behavior:**
1. Determine which file was just written/edited
2. Check if the file path contains `.agent/skills/`
3. If not a skill file: exit 0 (no action)
4. If a skill file: extract skill directory, run validator
5. Print validation result to stdout (shown to Claude as feedback)
6. Exit 0 (allow) — validation is advisory, not blocking

**Note on hook input format:**
Claude Code hook scripts receive context differently from Gemini hooks. The exact mechanism (environment variables, stdin, arguments) should be verified against the current Claude Code documentation at implementation time. The hook may need to parse `$CLAUDE_TOOL_INPUT` or similar variables.

---

## 7. Commands Specification

### Directory structure

```
.claude/
├── commands/
│   ├── start-feature.md
│   ├── plan.md
│   ├── develop.md
│   ├── develop-all.md
│   ├── light.md
│   ├── vdd.md
│   ├── vdd-start-feature.md
│   ├── vdd-plan.md
│   ├── vdd-develop.md
│   ├── vdd-adversarial.md
│   ├── vdd-multi.md
│   ├── full.md
│   ├── security-audit.md
│   ├── base-stub-first.md
│   ├── update-docs.md
│   ├── framework-upgrade.md
│   ├── iterative-design.md
│   ├── product-full-discovery.md
│   ├── product-market-only.md
│   └── product-quick-vision.md
├── hooks/
│   └── validate_skill_hook.sh
└── settings.json
```

### Command file template

Each command file delegates to the corresponding workflow in `.agent/workflows/`:

```markdown
Read and execute the workflow defined in `.agent/workflows/<workflow-file>.md`.

Follow all steps sequentially. Load required skills as specified in each step.
Apply all Global Protocols (skill-archive-task, skill-session-state).

User's task context:
$ARGUMENTS
```

### Command mapping table

| Command | File | Workflow Source | Description |
|---|---|---|---|
| `/start-feature` | `start-feature.md` | `01-start-feature.md` | Run Analysis + Architecture phases |
| `/plan` | `plan.md` | `02-plan-implementation.md` | Run Planning phase |
| `/develop` | `develop.md` | `03-develop-single-task.md` | Develop a single task from PLAN.md |
| `/develop-all` | `develop-all.md` | `05-run-full-task.md` | Loop through all tasks in PLAN.md |
| `/light` | `light.md` | `light-01-start-feature.md` | Fast-track for trivial tasks |
| `/vdd` | `vdd.md` | `vdd-enhanced.md` | VDD Enhanced pipeline |
| `/vdd-start-feature` | `vdd-start-feature.md` | `vdd-01-start-feature.md` | VDD Analysis + Architecture |
| `/vdd-plan` | `vdd-plan.md` | `vdd-02-plan.md` | VDD Planning phase |
| `/vdd-develop` | `vdd-develop.md` | `vdd-03-develop.md` | VDD Development phase |
| `/vdd-adversarial` | `vdd-adversarial.md` | `vdd-adversarial.md` | VDD Adversarial testing |
| `/vdd-multi` | `vdd-multi.md` | `vdd-multi.md` | VDD Multi-task pipeline |
| `/full` | `full.md` | `full-robust.md` | Full pipeline + Security Audit |
| `/security-audit` | `security-audit.md` | `security-audit.md` | Security vulnerability assessment |
| `/base-stub-first` | `base-stub-first.md` | `base-stub-first.md` | Standard Stub-First pipeline (full) |
| `/update-docs` | `update-docs.md` | `04-update-docs.md` | Reverse-engineer and update documentation |
| `/framework-upgrade` | `framework-upgrade.md` | `framework-upgrade.md` | Framework upgrade procedure |
| `/iterative-design` | `iterative-design.md` | `iterative-design.md` | Iterative design workflow |
| `/product-full-discovery` | `product-full-discovery.md` | `product-full-discovery.md` | Full product discovery |
| `/product-market-only` | `product-market-only.md` | `product-market-only.md` | Market-only product analysis |
| `/product-quick-vision` | `product-quick-vision.md` | `product-quick-vision.md` | Quick product vision |

---

## 8. Tool Mapping Reference

This table maps every tool reference in agent prompts and skills to Claude Code equivalents. Use this when writing `CLAUDE.md`.

### Direct replacements

| Framework Reference | Claude Code Tool | Usage |
|---|---|---|
| `read_file(path)` | `Read` | `Read` tool with `file_path` parameter |
| `write_file(path, content)` | `Write` | `Write` tool with `file_path` and `content` |
| `list_directory(path)` | `Glob` | `Glob` with pattern like `path/**/*` |
| `run_tests("pytest")` | `Bash` | `Bash` with command `pytest -q --tb=short` |
| `git_status()` | `Bash` | `Bash` with command `git status` |
| `git_add(files)` | `Bash` | `Bash` with command `git add <files>` |
| `git_commit(message)` | `Bash` | `Bash` with command `git commit -m "..."` |

### Script invocations via Bash

| Framework Script | Bash Command |
|---|---|
| `tool_runner.py` | Not needed; use native tools directly |
| `validate_skill.py <skill>` | `python3 .agent/skills/skill-creator/scripts/validate_skill.py <skill-dir>` |
| `init_skill.py <name> --tier <N>` | `python3 .agent/skills/skill-creator/scripts/init_skill.py <name> --tier <N>` |
| `update_state.py --mode X --task Y` | `python3 .agent/skills/skill-session-state/scripts/update_state.py --mode "X" --task "Y" --status "Z"` |
| `doctor.py` | `python3 System/scripts/doctor.py` |

### Claude Code-specific tools (no framework equivalent)

| Claude Code Tool | Use Case |
|---|---|
| `Edit` | Targeted string replacement in files (preferred over Write for modifications) |
| `Grep` | Content search across codebase (replaces `grep`/`rg` in Bash) |
| `Glob` | File pattern matching (replaces `find` in Bash) |
| `TodoWrite` | Task progress tracking (replaces manual status reporting) |
| `Task` (subagents) | Parallel execution of independent phases |

---

## 9. Validation Checklist

After completing all migration tasks, verify:

### Files exist

- [x] `CLAUDE.md` exists in project root (136 lines)
- [x] `.claude/settings.json` exists and contains valid JSON
- [x] `.claude/commands/` directory exists with 20 command files
- [x] `.claude/hooks/validate_skill_hook.sh` exists and is executable (`-rwxr-xr-x`)

### Functional tests

- [x] Running `claude` in project root loads `CLAUDE.md` as system prompt
- [x] Typing `/start-feature` in Claude Code triggers the command
- [x] Typing `/light` in Claude Code triggers the light mode command
- [x] Session state file `.agent/sessions/latest.yaml` is read at startup (if exists)
- [x] Modifying a file in `.agent/skills/` triggers the validation hook (tested: `core-principles` → "passed validation")
- [x] All Python scripts run successfully:
  ```bash
  python3 System/scripts/doctor.py            # ✅ Preflight checks passed
  python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/skill-creator  # ✅ Validation PASSED
  ```

### Content validation

- [x] `CLAUDE.md` contains no references to `.cursor/skills`
- [x] `CLAUDE.md` contains no references to `schemas.py` or `tool_runner.py`
- [x] `CLAUDE.md` contains no references to `execute_tool` dispatcher
- [x] `CLAUDE.md` contains no references to "Composer" or "Cmd+I"
- [x] `CLAUDE.md` contains no references to `GEMINI.md` (self-improvement section updated)
- [x] `CLAUDE.md` pipeline matches `GEMINI.md` pipeline (same 4 phases, same agents, same order)
- [x] `CLAUDE.md` is under 200 lines (136 lines — within 130-150 target)
- [x] All 20 command files reference correct workflow sources (verified: all mappings valid)
- [x] `README.md` section "Option C" is updated (+ `README.ru.md`)

### Parity tests

- [x] Same workflow can be triggered in Gemini CLI (`run base-stub-first`) and Claude Code (`/base-stub-first`)
- [x] `CLAUDE.md` pipeline sections are identical to `GEMINI.md` pipeline sections (diff only in tool/workflow references)
- [x] Session state created by Gemini CLI can be read by Claude Code session and vice versa (same `.agent/sessions/latest.yaml`)
- [x] Skills modified in Claude Code trigger the same validation as in Gemini CLI (same `validate_skill.py`)

---

## Appendix A: Files Created/Modified

| Action | File | Description |
|---|---|---|
| **Create** | `CLAUDE.md` | Claude Code system prompt |
| **Create** | `.claude/settings.json` | Hooks and settings |
| **Create** | `.claude/hooks/validate_skill_hook.sh` | Skill validation hook |
| **Create** | `.claude/commands/start-feature.md` | Command: start feature |
| **Create** | `.claude/commands/plan.md` | Command: plan implementation |
| **Create** | `.claude/commands/develop.md` | Command: develop single task |
| **Create** | `.claude/commands/develop-all.md` | Command: develop all tasks |
| **Create** | `.claude/commands/light.md` | Command: light mode |
| **Create** | `.claude/commands/vdd.md` | Command: VDD enhanced |
| **Create** | `.claude/commands/vdd-start-feature.md` | Command: VDD analysis + architecture |
| **Create** | `.claude/commands/vdd-plan.md` | Command: VDD planning |
| **Create** | `.claude/commands/vdd-develop.md` | Command: VDD development |
| **Create** | `.claude/commands/vdd-adversarial.md` | Command: VDD adversarial testing |
| **Create** | `.claude/commands/vdd-multi.md` | Command: VDD multi-task |
| **Create** | `.claude/commands/full.md` | Command: full robust |
| **Create** | `.claude/commands/security-audit.md` | Command: security audit |
| **Create** | `.claude/commands/base-stub-first.md` | Command: standard pipeline |
| **Create** | `.claude/commands/update-docs.md` | Command: update docs |
| **Create** | `.claude/commands/framework-upgrade.md` | Command: framework upgrade |
| **Create** | `.claude/commands/iterative-design.md` | Command: iterative design |
| **Create** | `.claude/commands/product-full-discovery.md` | Command: product full discovery |
| **Create** | `.claude/commands/product-market-only.md` | Command: product market-only |
| **Create** | `.claude/commands/product-quick-vision.md` | Command: product quick vision |
| **Modify** | `README.md` | Update "Option C" section |

**Total: 24 files created, 1 file modified.**

## Appendix B: Out of Scope

The following items are intentionally excluded from this migration:

1. **Agent prompt modifications** — `System/Agents/*.md` files are platform-agnostic and do not need changes.
2. **Skill content modifications** — `.agent/skills/*/SKILL.md` files describe methodology, not tooling. They work as-is when read by Claude Code.
3. **Workflow content modifications** — `.agent/workflows/*.md` files are platform-agnostic. Commands delegate to them.
4. **Task tool (subagent) optimization** — Using Claude Code's Task tool for parallel phase execution is an enhancement, not a migration requirement.
