# Framework Audit 083 — Reposition Dispatcher as Fallback + Additional Tools (correct 082's "legacy")

- **Task:** 083 `reposition-dispatcher-fallback` · **Workflow:** `/framework-upgrade` · **Meta-skill:** `skill-self-improvement-verificator` (Modes A+B)
- **Date:** 2026-06-10 · **Release:** v3.20.12 · **Type:** docs-only correction of task 082; **no archiving, no code change.**
- **Discharges** 082's `[BYPASS_DOCS_CHECK]` — *with corrected framing* (dispatcher = additional-tools + fallback, not "legacy").

## Why this task exists (correcting 082)
Task 082 branded the `schemas.py`/`tool_runner.execute_tool` dispatcher **"legacy / not used by any vendor harness."** Operator corrected: it's a **fallback** for harnesses without native tool execution **and** the home of **additional** framework tools. Read-only verification confirmed the honest status (below), so the docs were repositioned rather than archived.

## Honest status (verified read-only)
- **`generate_task_archive_filename`** lives in `task_id_tool.py` as **both** a CLI (`__main__`+argparse — the live path; what CLAUDE.md calls, what `skill-archive-task` Step 3 Option A uses) **and** an importable function the dispatcher wraps (`tool_runner.py:279`, `schemas.py:115`). → **framework-unique, live, no native equivalent.**
- **Overlap tools** (`run_tests`, `git_status`/`git_add`/`git_commit`, `read_file`/`write_file`/`list_directory`) mirror native harness capabilities → **fallback**.
- **`execute_tool`** dispatch primitive is implemented + tested (63 dispatcher tests green), but **`TOOLS_SCHEMAS` is imported by nothing**, there's **no LLM client / entrypoint** → the orchestrator loop that would drive the fallback is **not yet wired**. Stated honestly in `ORCHESTRATOR.md`. (082's "imported only by its own tests" was imprecise — `tool_runner` wraps the live `generate_task_archive_filename`.)

## Vendor-doc provenance (official sources, fetched 2026-06-10)
Bootstrap tool sections were re-established **grounded in official docs**, not memory:
- **Cursor** (`cursor.com/docs/cli/using`, `/agent/tools/terminal`, `/cli/mcp`): built-in file/search/terminal (sandboxed, approval-gated) + **MCP** (`mcp.json`) + ACP.
- **Codex CLI** (`developers.openai.com/codex/cli`, `/concepts/sandboxing`, `/codex/mcp`): edit/run in sandbox (`workspace-write`) + **MCP** (`~/.codex/config.toml`) + `codex-shell-tool-mcp`.
- **Gemini CLI** (`github.com/google-gemini/gemini-cli` docs/tools/shell.md, reference/tools.md, core/tools-api.md): `run_shell_command`, file tools, `read_many_files`, **`tools.discoveryCommand`** (registers custom tools from JSON), **MCP** (`mcpServers`).
- **Antigravity** (shares `GEMINI.md`): built-in file/shell, MCP / `agent.json` (per task-081 reference).

## Gates
- **G1 (wording):** `AGENTS.md`/`GEMINI.md` no longer call the dispatcher "legacy"; "fallback" present in `ORCHESTRATOR.md`/`AGENTS.md`/`GEMINI.md`/`SOURCE_OF_TRUTH.md`; "additional"-tools framing + `generate_task_archive_filename` present.
- **G2 (no archiving):** no `System/Docs/archive/`; `ORCHESTRATOR.md` at its original path.
- **G3 (task_boundary):** none in `System/Docs/` (SESSION_CONTEXT_GUIDE reframed to "phase boundary").
- **G4:** `validate_skill` sweep **43/43**.
- **G5:** `pytest` security-audit **30/30**; dispatcher tests (`tool_runner` + `archive_protocol` + `task_id_tool`) **63/63** — code intact.
- **G6 (untouched):** `git diff` shows **no** change to `schemas.py`, `tool_runner.py`, `archive_protocol.py`, `task_id_tool.py`, **`CLAUDE.md`** (operator: leave as-is), or any `System/Agents/*` prompt.

## Deliverables
- `System/Docs/ORCHESTRATOR.md` — Status Active→Fallback subsystem; `[!NOTE]` banner (two tool classes + not-yet-wired status + per-vendor wiring); Overview reframed. **Kept live, not archived.**
- `AGENTS.md` (Cursor+Codex) + `GEMINI.md` (Gemini CLI **+ Antigravity**) — TOOL EXECUTION PROTOCOL re-establishes the framework additional tools (built-in primary, `generate_task_archive_filename` always, overlap=fallback, MCP/`discoveryCommand` native paths). `CLAUDE.md` untouched.
- `SOURCE_OF_TRUTH.md` / `SKILLS.md` / `RELEASE_CHECKLIST.md` — legacy→additional/fallback. `SESSION_CONTEXT_GUIDE.md` — `task_boundary`→phase boundary.
- `README.md`/`README.ru.md` — tree note + nav relabel + header v3.20.12. `CHANGELOG.md`/`CHANGELOG.ru.md` — v3.20.12 (corrects 082 forward; 082's committed entry left as history).

## Design decisions
1. **Reposition, not archive.** The dispatcher is intended infrastructure (fallback + additional tools), so its doc stays live and honestly labelled — burying it would have repeated 082's mistake in the other direction.
2. **Two tool classes named explicitly** so readers don't conflate the framework-unique `generate_task_archive_filename` (always use) with the overlap/fallback tools (native preferred).
3. **`CLAUDE.md` untouched** per operator — it already carries the correct, working block.
4. **Honest "not yet wired"** kept front-and-center — the fallback isn't a working orchestrator loop yet; that's a separate feature (out of scope).

## Flags for operator
- **Restart session** (bootstrap files changed).
- **Manual-sync** the independent `Universal-skills/System/Docs/ORCHESTRATOR.md` copy (diverged; separate repo, not touched here).
- **Wiring the fallback** (LLM loop over `TOOLS_SCHEMAS` → `execute_tool` + entrypoint + capability detection) remains a future feature TASK.

## Verdict
**APPROVED** — gates green, dispatcher repositioned as additional-tools + fallback with an honest not-yet-wired status, framework tools re-established in `AGENTS.md`/`GEMINI.md` grounded in official vendor docs, `CLAUDE.md` + all dispatcher code untouched, nothing archived. Uncommitted; operator to review + commit (v3.20.12).
