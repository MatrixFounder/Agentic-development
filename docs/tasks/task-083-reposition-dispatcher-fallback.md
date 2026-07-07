# Technical Specification: Reposition the Tool Dispatcher as a FALLBACK (correct 082's "legacy")

### 0. Meta Information
- **Task ID:** 083
- **Slug:** `reposition-dispatcher-fallback`
- **Mode:** Framework Upgrade (docs-only; corrects wording from task 082; **no archiving, no new code**)
- **Type:** Maintenance / framing correction. Discharges 082's `[BYPASS_DOCS_CHECK]` *with corrected framing* (fallback, not legacy).
- **Workflow:** `/framework-upgrade` (verificator Modes A+B).

### 1. Problem Description
Task 082 branded the `schemas.py`/`tool_runner.execute_tool` dispatcher **"legacy / not used by any vendor harness"** in `AGENTS.md`, `GEMINI.md`, and (as a doc-debt) across `System/Docs/`. The operator clarified the **real intent**: the dispatcher is a **fallback** for harnesses that can't execute tools natively — not abandoned legacy. A read-only verification established the honest status: the dispatch primitive (`execute_tool`) is implemented and tested, but `TOOLS_SCHEMAS` is imported by nothing, there is no LLM loop and no entrypoint — so the fallback is **not yet wired**. Correct framing across the docs is therefore **"fallback — dispatch primitive implemented + tested; orchestrator loop not yet wired"** (neither "legacy" nor "working fallback").

### 2. Requirements Traceability Matrix (RTM)
> **Scope expansion (operator, mid-execution):** the dispatcher isn't just a fallback — its tools are **additional tools on top of the harness's built-in ones**. `generate_task_archive_filename` is **framework-unique** (no native equivalent, always usable via `task_id_tool.py` CLI); the rest (`run_tests`/`git_*`/file ops) **mirror native tools** → fallback. Re-establish them in `AGENTS.md`/`GEMINI.md` (deleted in 082), **grounded in official vendor docs**. **`CLAUDE.md` stays untouched** (already correct). **`GEMINI.md` also serves Antigravity.**

| ID | Requirement | MVP? | Sub-features |
|----|-------------|------|--------------|
| R1 | Reframe `ORCHESTRATOR.md` as the fallback + additional-tools doc (keep LIVE, do not archive) | Yes | (a) Status Active→Fallback/not-wired; (b) `[!NOTE]` banner; (c) full tool list framing (unique vs fallback); (d) `generate_task_archive_filename`/`task_id_tool.py` example; (e) per-vendor wiring paths (MCP / Gemini `tools.discoveryCommand`) |
| R2 | Re-establish framework **additional tools** in bootstrap files, doc-grounded; flip legacy→fallback | Yes | (a) `AGENTS.md` (Cursor+Codex: built-in + MCP); (b) `GEMINI.md` (Gemini CLI `run_shell_command`/`discoveryCommand`/MCP **+ Antigravity**); (c) **`CLAUDE.md` UNTOUCHED** |
| R3 | Reframe `System/Docs` references legacy→additional/fallback (in place) | Yes | (a) `SOURCE_OF_TRUTH.md`; (b) `SKILLS.md`; (c) `RELEASE_CHECKLIST.md`; (d) `SESSION_CONTEXT_GUIDE.md` `task_boundary`→phase boundary |
| R4 | README accuracy + forward-correcting CHANGELOG | Yes | (a) README/README.ru tree note + nav relabel; (b) CHANGELOG EN+RU v3.20.12 stating 082 overshot "legacy"; (c) vendor-doc provenance in audit |
| R5 | Preserve behavior; no archiving; no code change; gates green | Yes | (a) no `System/Docs/archive/`; (b) ORCHESTRATOR.md at original path; (c) dispatcher code untouched; (d) validate_skill 43/43, pytest 30/30 |

### 3. Use Cases
- **UC1 (Codex/Cursor/Gemini orchestrator):** reads `AGENTS.md`/`GEMINI.md` → learns the dispatcher is the **fallback** for tool-less harnesses (not "dead"), with native tools as the primary path.
- **UC2 (maintainer):** opens `ORCHESTRATOR.md` → sees honest status (fallback, dispatch primitive only, loop not yet wired) instead of "Active" or "legacy".
- **UC3 (future):** the "wire the fallback" feature has a clearly-scoped, correctly-framed doc to build against.

### 4. Acceptance Criteria
- [ ] AC1: `AGENTS.md`/`GEMINI.md` no longer call the dispatcher "legacy"; both say **fallback**. `ORCHESTRATOR.md` Status line = "Fallback …".
- [ ] AC2: `grep "fallback"` present in `ORCHESTRATOR.md`, `AGENTS.md`, `GEMINI.md`, `SOURCE_OF_TRUTH.md`.
- [ ] AC3: **No archiving** — `System/Docs/ORCHESTRATOR.md` at its original path; no `System/Docs/archive/` dir.
- [ ] AC4: `task_boundary` no longer a live tool in `System/Docs/SESSION_CONTEXT_GUIDE.md`.
- [ ] AC5: dispatcher code untouched (`schemas.py`/`tool_runner.py`/`archive_protocol.py`/`task_id_tool.py`) and no `System/Agents/*` prompt changed; `validate_skill` 43/43, `pytest` security-audit 30/30.

### 5. Open Questions
None — scope (docs-only fallback reposition) + version (v3.20.12) locked by operator.
