# Development Plan: Task 082 — Reword Tool-Layer Framing + Re-sync GEMINI.md

> Mode B gates. **Architecture untouched** (reviewed: framing-only, no data model / component / interface change → no `ARCHITECTURE.md` edit). Release v3.20.11. Donor template = `CLAUDE.md` (already correct).

## Step 0 — Backup (rollback safety)
```
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do cp "$f" ".agent/archive/$f.bak"; done
cp System/Agents/00_agent_development.md .agent/archive/00_agent_development.md.bak
cp System/Agents/01_orchestrator.md     .agent/archive/01_orchestrator.md.bak
```
Rollback = copy any `.bak` back over its source.

## Step 1 — [R1] Tool-framing reword (vendor-neutral)
- **1a `01_orchestrator.md` §1.3:** `ALWAYS use native tools (run_tests, git_status)` → `ALWAYS use your harness's built-in tools (shell/terminal for tests & git, file read/write/edit, search) to act yourself before asking the user.`
- **1b `00_agent_development.md` Orchestrator "Tooling" line:** drop `task_boundary`; describe progress as session-state-persisted (overlaps R2).
- **1c `AGENTS.md` §TOOL EXECUTION PROTOCOL (v3.2.5+):** rewrite to "use your environment's built-in file/shell/search tools"; helper scripts via shell; `ORCHESTRATOR.md` referenced as **legacy** (not used inside vendor harnesses).
- **1d `GEMINI.md` §TOOL EXECUTION PROTOCOL (v3.2.5+):** same rewrite as 1c.

## Step 2 — [R2] Remove `task_boundary` fiction
- **2a `00` §"Agentic Mode & Task Boundaries":** retitle → "Agentic Mode & Session State"; body: no special `task_boundary` tool required; track via harness task/todo state + persist with `update_state.py`.
- **2b `00` anti-patterns line** `ALWAYS use task_boundary to report status` → `ALWAYS persist status via skill-session-state at phase boundaries`.
- **2c `GEMINI.md` workflow-dispatch line** `After every task_boundary call, you MUST … update_state.py` → `After every phase boundary, you MUST … update_state.py`.

## Step 3 — [R3] GEMINI.md symlink re-sync
- Insert "SYMLINK RESOLUTION (MANDATORY)" + "SYMLINK-AWARE COMMAND DEFAULTS" sections (ported from `AGENTS.md` lines 14–29, wording aligned) after the SKILLS-SYSTEM section.

## Step 4 — [R4] Verification gates
1. `python3 .agent/skills/skill-creator/scripts/validate_skill.py` sweep → unchanged vs baseline.
2. `pytest .agent/skills/security-audit/tests/ -q` → green (regression; no scanner touched).
3. Grep AC1/AC2: no `run_tests|git_status|git_ops|file_ops|execute_tool|task_boundary` as a live tool in the 4 edited files (legacy `ORCHESTRATOR.md` reference allowed).
4. Grep AC3: `SYMLINK RESOLUTION` + `SYMLINK-AWARE` present in `GEMINI.md`.
5. Confirm AC5: `git diff --stat` shows **no** change to `CLAUDE.md`, `schemas.py`, `tool_runner.py`, `ORCHESTRATOR.md`.

## Step 5 — Finalization
- CHANGELOG.md + CHANGELOG.ru.md: **v3.20.11** entry.
- README.md + README.ru.md: version header bump.
- Audit artifact `docs/reviews/framework-audit-082.md` (Mode A+B, `[BYPASS_DOCS_CHECK]` justification).
- `update_state.py` session-state at finalization boundary.
- Flag operator: **restart session** so re-read bootstrap files take effect (core prompts changed).

## Test Coverage Note (Mode B item 4)
No new framework *logic* is introduced (pure prompt-text reword) → no new unit tests warranted. Regression is covered by the existing validate_skill sweep + security-audit pytest (Step 4.1–4.2). Acceptance is grep-verifiable (Step 4.3–4.5).

## Rollback
Per Step 0 `.bak` set + git. New files: only `docs/reviews/framework-audit-082.md` (removable). Edits are confined to 4 text files + changelogs/readme.
