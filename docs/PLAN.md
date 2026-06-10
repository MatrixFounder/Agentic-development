# Development Plan: Task 083 — Reposition Dispatcher as Fallback (docs-only)

> Mode B gates. **Architecture untouched** (framing-only). Release v3.20.12. No archiving, no code change. Corrects task 082's "legacy" → "fallback (not yet wired)".

## Step 0 — Backup (rollback safety)
```
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md README.md README.ru.md; do cp "$f" ".agent/archive/$f.bak"; done
for f in ORCHESTRATOR SOURCE_OF_TRUTH SKILLS RELEASE_CHECKLIST SESSION_CONTEXT_GUIDE; do cp "System/Docs/$f.md" ".agent/archive/$f.md.bak"; done
```

## Step 1 — [R1] ORCHESTRATOR.md → fallback + additional-tools doc (keep live)
- Header line 4 `**Status:** Active` → `**Status:** Fallback / additional-tools subsystem — dispatch primitive implemented & tested; orchestrator loop not yet wired`.
- Insert `> [!NOTE]` banner: two tool classes — **framework-unique** (`generate_task_archive_filename`, no native equivalent, always usable via `task_id_tool.py`) and **overlap/fallback** (`run_tests`/`git_*`/file ops, native preferred); dispatch primitive tested, loop not yet wired; per-vendor native wiring exists (MCP everywhere; Gemini `tools.discoveryCommand`).
- Overview line 7: drop present-tense "introduces … replaces" → fallback/additional-tools framing.

## Step 2 — [R2] Re-establish framework additional tools in bootstrap files (doc-grounded)
- **`CLAUDE.md`: NO CHANGE** (operator: already correct).
- `AGENTS.md` TOOL EXECUTION PROTOCOL (replaces 082 block): built-in tools (Cursor/Codex: file/shell/search, per docs) + repo helpers (`task_id_tool.py`, `update_state.py`) + **additional/fallback tools** (`schemas.py` set; unique `generate_task_archive_filename` vs overlap-fallback; dispatcher = fallback **if available**; expose via **MCP** `mcp.json`/`config.toml`) + ORCHESTRATOR.md reference.
- `GEMINI.md` TOOL EXECUTION PROTOCOL (replaces 082 block): **Gemini CLI** (`run_shell_command`/file tools/`read_many_files`) **+ Antigravity** (file/shell) built-ins; same additional/fallback tool framing; native registration via **`tools.discoveryCommand`** / MCP `mcpServers` (Gemini) and MCP/`agent.json` (Antigravity).

## Step 3 — [R3] System/Docs reframe (in place)
- `SOURCE_OF_TRUTH.md` (16–18, 49–51, 58): `schemas.py`/`tool_runner.py`/`ORCHESTRATOR.md` → **fallback dispatcher** (paths unchanged).
- `SKILLS.md` (~92): "natively executed by the Orchestrator" → "**fallback dispatcher** tool set (used when the harness can't execute tools natively)".
- `RELEASE_CHECKLIST.md` (19, 31): frame as fallback-dispatcher verification.
- `SESSION_CONTEXT_GUIDE.md` (12, 75): `task_boundary` → "phase boundary".

## Step 4 — [R4] README + CHANGELOG
- `README.md:93`/`README.ru.md:93`: `Dispatcher (entry point)` → `(fallback tool dispatcher)`; `README.md:318` nav relabel "… Fallback Guide" (path unchanged).
- CHANGELOG EN+RU **v3.20.12**: states 082 over-labeled it "legacy"; repositioned to **fallback (not yet wired)**; nothing archived. README header bump ×2.

## Step 5 — [R5] Verification gates
1. `grep -rn "legacy" AGENTS.md GEMINI.md` → dispatcher no longer "legacy"; `grep -rn "fallback"` present in ORCHESTRATOR/AGENTS/GEMINI/SOURCE_OF_TRUTH.
2. No `System/Docs/archive/`; `System/Docs/ORCHESTRATOR.md` at original path.
3. `grep -rn "task_boundary" System/Docs/` → none as a live tool.
4. `validate_skill` sweep 43/43; `pytest .agent/skills/security-audit/tests/` 30/30; dispatcher tests (`tool_runner`/`archive_protocol`/`task_id_tool`) still green.
5. `git diff` → no change to `schemas.py`/`tool_runner.py`/`archive_protocol.py`/`task_id_tool.py`/`System/Agents/*`.

## Step 6 — Finalization
- Audit `docs/reviews/framework-audit-083.md` (Mode A+B, honest fallback status, Universal-skills divergence flag).
- `update_state.py` session-state.
- Flag operator: restart session (bootstrap files changed) + manual-sync the `Universal-skills` ORCHESTRATOR.md copy.

## Test Coverage Note (Mode B item 4)
No new logic (pure prose reframe) → no new unit tests. Regression covered by validate_skill sweep + security-audit pytest + the untouched dispatcher tests (Step 5.4). Acceptance is grep-verifiable (Step 5.1–5.3, 5.5).

## Rollback
Step 0 `.bak` set + git. New file: only `docs/reviews/framework-audit-083.md` (removable). Edits confined to text docs + changelog/readme.
