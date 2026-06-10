# Framework Audit 082 — Reword Dead Tool-Layer Framing + Re-sync GEMINI.md (Vendor Currency)

- **Task:** 082 `reword-tool-framing-vendor-sync` · **Workflow:** `/framework-upgrade` · **Meta-skill:** `skill-self-improvement-verificator` (Modes A+B)
- **Date:** 2026-06-10 · **Release:** v3.20.11 · **Source:** follow-up to the `System/Agents` cross-vendor audit (this session) — implements audit **items 1, 2, 4**; item **3** (version-header re-stamp) intentionally **not** done.
- **Scope decision (operator):** "Reword prompts only" — `schemas.py`, `tool_runner.py`, `System/Docs/ORCHESTRATOR.md` left in place.

## Mode A / Mode B — **PASS**
**A (Specification):** Root integrity ✅ (framing-only, atomic, anti-hallucination — schemas.py orphan + GEMINI staleness both verified by evidence: `grep` of importers = self-tests only; `git log` dates AGENTS v3.19.1 Jun-2 vs GEMINI May-7). Skill compatibility ✅ (no agent loses a TIER 0 skill; only tool-framing/symlink text changes). Documentation ⚠️ **`[BYPASS_DOCS_CHECK]`** — see justification below. Migration ✅ N/A (no format change; "restart session" flagged per workflow Step 4.3).
**B (Plan):** Verification step ✅ (validate_skill sweep + pytest). Rollback ✅ (5-file `.bak` + git). Atomic ✅ (R1/R2/R3 per-file). Test coverage ✅ (no new logic → existing gates are the regression; acceptance is grep-verifiable).

### `[BYPASS_DOCS_CHECK]` justification (Mode-A failure-condition: "modify GEMINI.md without a System/Docs update")
The reword aligns the bootstrap files to **reality** and to `CLAUDE.md` (already the de-facto truth) and `System/Docs/SESSION_CONTEXT_GUIDE.md` (already documents the real `update_state.py` mechanism). The only doc still describing the dead dispatcher as live is `ORCHESTRATOR.md`, which the operator **explicitly chose to leave in place**. The bootstrap files now label it **legacy**, so no reader is misled. Fully reconciling/retiring `ORCHESTRATOR.md` + `schemas.py` is the deferred "delete dead code" option the operator declined for this pass.

## Gates
- **G1 (validate_skill sweep):** 43/43 PASS (by exit code over every `.agent/skills/*/`) — unchanged vs baseline. No skill was touched.
- **G2 (security-audit pytest):** 30/30 — unchanged. No scanner/skill edit.
- **G3 (AC1/AC2 — no live dead-tool wording):** residual `grep` hits = exactly the 3 permitted survivors: `00:73` negation ("no special `task_boundary` tool is required"), `AGENTS:42` + `GEMINI:43` legacy `execute_tool`/`schemas.py` reference labelled "**legacy** … **not** used". Caught + fixed one straggler at `00:5` (had called `task_boundary` a live "protocol for state management").
- **G4 (AC3 — GEMINI symlink protocol):** 2 section headers present (`SYMLINK RESOLUTION`, `SYMLINK-AWARE COMMAND DEFAULTS`).
- **G5 (AC5 — untouched files):** `git diff` shows **no** change to `CLAUDE.md`, `.agent/tools/schemas.py`, `System/scripts/tool_runner.py`, `System/Docs/ORCHESTRATOR.md`.

## Deliverables (diff)
- `System/Agents/00_agent_development.md` — General Concept line, §2 retitled "Agentic Mode & Session State", anti-patterns line, Orchestrator "Tooling" line (4 edits: #1 + #4).
- `System/Agents/01_orchestrator.md` — §1.3 Tool Priority (#1).
- `AGENTS.md` — §TOOL EXECUTION PROTOCOL rewrite (#1).
- `GEMINI.md` — §TOOL EXECUTION PROTOCOL rewrite (#1), workflow-dispatch `task_boundary`→"phase boundary" (#4), inserted SYMLINK RESOLUTION + SYMLINK-AWARE COMMAND DEFAULTS (#2).
- `CHANGELOG.md` / `CHANGELOG.ru.md` v3.20.11; `README.md` / `README.ru.md` header bump.

## Design decisions
1. **`CLAUDE.md` is the donor, untouched.** It already says "use your built-in tools"; the other three bootstrap files were brought up to it (vendor-neutral phrasing, not Claude-specific tool names).
2. **Reword, not delete.** Per operator scope, the inert `schemas.py`/`tool_runner.py`/`ORCHESTRATOR.md` stay (test-backed, harmless); the bootstrap files just relabel them **legacy** so the misdirection stops at the read surface.
3. **Item 3 deliberately skipped.** Re-stamping 16 prompt headers (v3.6.0/v3.7.0 → current) is high-churn / zero-behavior; not worth a 16-file diff on its own.
4. **GEMINI was the real bug, not just stale wording.** Missing symlink protocol = silent skill-load failure on the weakest instruction-follower; the port is the functional half of this release.

## Verdict
**APPROVED** — gates green, dead tool-dispatch + `task_boundary` framing retired across the 4 files, GEMINI.md symlink protocol restored, `CLAUDE.md`/dead-code untouched, item 3 honestly skipped. Framing-only; **operator should restart the session** so re-read bootstrap files take effect. Uncommitted — operator to review + commit (v3.20.11).
