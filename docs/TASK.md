# Technical Specification: Reword Dead Tool-Layer Framing + Re-sync GEMINI.md (Vendor Currency)

### 0. Meta Information
- **Task ID:** 082
- **Slug:** `reword-tool-framing-vendor-sync`
- **Mode:** Framework Upgrade (4 files, framing-only, zero behavior change to the pipeline)
- **Type:** Maintenance — follow-up to the `System/Agents` cross-vendor audit (this session). Implements audit items **1, 2, 4**; item **3** (version-header re-stamp) is **explicitly out of scope** per operator decision.
- **Workflow:** `/framework-upgrade` (verificator Modes A+B). Scope decision: **"Reword prompts only"** — `schemas.py`, `tool_runner.py`, and `System/Docs/ORCHESTRATOR.md` are **left in place** (inert, test-backed).

### 1. Problem Description
The three vendor bootstrap files and two core role-prompts still describe a **standalone-Python-orchestrator tool layer** (`run_tests` / `git_status` / `git_ops` / `file_ops` / `execute_tool` via `.agent/tools/schemas.py` "Function Calling", plus a `task_boundary` tool). That dispatcher is imported only by its own tests — **no current vendor harness (Claude Code, Cursor, Codex CLI, Gemini CLI, Antigravity) uses it.** `CLAUDE.md` was already modernized to "use your built-in tools"; `00_agent_development.md`, `01_orchestrator.md`, `AGENTS.md`, and `GEMINI.md` were not. Separately, `GEMINI.md` is a stale fork (~v3.15) missing the **symlink-resolution protocol** that `AGENTS.md` received in v3.19.1 — which risks silent skill-load failure on Gemini CLI (its `find`/`rg` skip symlinks by default).

This misleads the orchestrator on every non-Claude vendor and bites Gemini hardest (weakest instruction-follower + missing symlink fix).

### 2. Requirements Traceability Matrix (RTM)
| ID | Requirement | MVP? | Sub-features |
|----|-------------|------|--------------|
| R1 | Replace dead tool-dispatch framing with vendor-neutral "use your harness's built-in tools" language | Yes | (a) `01_orchestrator.md` §1.3 Tool Priority; (b) `00_agent_development.md` Orchestrator "Tooling" line; (c) `AGENTS.md` §TOOL EXECUTION PROTOCOL; (d) `GEMINI.md` §TOOL EXECUTION PROTOCOL |
| R2 | Remove `task_boundary` as a fictional callable tool; route state to `skill-session-state`/`update_state.py` | Yes | (a) `00` §2 header+body; (b) `00` anti-patterns line; (c) `GEMINI.md` workflow-dispatch "after every task_boundary call" line |
| R3 | Re-sync `GEMINI.md` with `AGENTS.md` symlink protocol | Yes | (a) insert "SYMLINK RESOLUTION (MANDATORY)"; (b) insert "SYMLINK-AWARE COMMAND DEFAULTS"; (c) keep wording aligned with AGENTS.md |
| R4 | Preserve behavior; no edits to `schemas.py`/`tool_runner.py`/`ORCHESTRATOR.md`; gates green | Yes | (a) `.agent/archive/*.bak` backups; (b) validate_skill sweep unchanged; (c) pytest security-audit 30/30; (d) grep old-wording + symlink-present checks |

### 3. Use Cases
- **UC1 (Gemini CLI orchestrator, deployed via symlinks):** reads `GEMINI.md` → now follows symlinks when enumerating `.agent/skills/` → loads skills successfully instead of treating symlinked dirs as empty.
- **UC2 (Codex/Cursor orchestrator):** reads `AGENTS.md` → is told to use its own built-in file/shell/search tools, not to look for a nonexistent `run_tests`/`execute_tool` function.
- **UC3 (any vendor, role assumption):** reads `00`/`01` → tracks progress via session-state persistence + native task/todo state, not a phantom `task_boundary` tool.

### 4. Acceptance Criteria
- [ ] AC1: No occurrence of `run_tests` / `git_status` / `git_ops` / `file_ops` / `execute_tool` **presented as a callable native tool** in `00`/`01`/`AGENTS.md`/`GEMINI.md`. (A neutral reference to `ORCHESTRATOR.md` labelled *legacy* is permitted.)
- [ ] AC2: No `task_boundary` appears as a live tool/call in `00`/`01`/`GEMINI.md`.
- [ ] AC3: `GEMINI.md` contains a "SYMLINK RESOLUTION" section and a "SYMLINK-AWARE COMMAND DEFAULTS" section consistent with `AGENTS.md`.
- [ ] AC4: `validate_skill.py` sweep result unchanged vs baseline; `pytest .agent/skills/security-audit/tests/` stays green.
- [ ] AC5: `CLAUDE.md` is **unchanged** (it is the correct donor template) and `schemas.py`/`tool_runner.py`/`ORCHESTRATOR.md` are **unmodified**.
- [ ] AC6: Version-header re-stamp (audit item 3) is **NOT** performed.

### 5. Open Questions
None — scope locked by operator ("сделай 1,2 и 4", "#3 точно не надо", "Reword prompts only").
