# Technical Specification: Vendor Adapter Scaffolds 6a–6c (C-07, roadmap item 6 — in-repo portion)

### 0. Meta Information
- **Task ID:** 080
- **Slug:** `vendor-adapter-scaffolds`
- **Mode:** Framework Upgrade (3 references stub→full, 1 detection-table row, 9 critic wrappers, 1 skill version; zero script change)
- **Type:** P1 modernization, roadmap item **6 sub-tasks 6a/6b/6c — in-repo documentation portion only**. The e2e validation (⚠️→✅ graduation) is **operator action on real CLIs, explicitly deferred** (user 2026-06-10: "я их проверить не смогу в данный момент … это только заготовки на будущее").
- **Workflow:** `/framework-upgrade` (verificator Modes A+B).
- **Source:** User request (2026-06-10): "Сделать базовые работы по (6a–6c референсы + обёртки)". Vendor primitives verified against PRIMARY docs in-session (geminicli.com/docs, developers.openai.com/codex, cursor.com/docs) — see §1 findings.

## 1. Primary-source findings (verified 2026-06-10, NOT from memory)

| Vendor | Def format + location | Key fields | Parallel multi-spawn? | Detection marker |
|---|---|---|---|---|
| **Gemini CLI** | Markdown+YAML — `.gemini/agents/*.md` (proj), `~/.gemini/agents/*.md` (user) | `name`, `description` (req); `tools` (array, wildcards `*`/`mcp_*`), `model`, `kind`, `temperature`, `max_turns`, `timeout_mins` | **⚠️ NOT documented** — only auto-delegation + explicit `@subagent-name`; concurrent spawn unconfirmed in primary docs | `GEMINI.md` (+ `.gemini/agents/`) |
| **Codex CLI** | TOML — `.codex/agents/` (proj), `~/.codex/agents/` (user) | `name`, `description`, `developer_instructions` (req); `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`, `nickname_candidates` | **✅ YES** — "spawns in parallel, waits for all, returns consolidated response" | `.codex/agents/` directory |
| **Cursor 2.4** | Markdown+YAML — `.cursor/agents/` (proj), `~/.cursor/agents/` (user) | `description`, `model` (inherit/fast/id), `readonly` (bool), `is_background` (bool) | **✅ YES** — main agent orchestrates, subagents run in parallel, **max 10**; `is_background:true` = async (Layer B-ish) | `.cursor/` directory |

**Material correction to roadmap item 6:** the roadmap's optimistic "Gemini concurrent subagents/instances" is **not confirmed** by primary docs — Gemini subagents exist but parallel single-invocation multi-spawn is undocumented. The Gemini scaffold records this gap honestly (Layer A unconfirmed → may stay sequential-delegation). Codex and Cursor genuinely support Layer A parallelism. `readonly:true` (Cursor) / `sandbox_mode:"read-only"` (Codex) map cleanly to the read-only critic guarantee.

## 2. Scope discipline

- **IN:** references at `claude-code.md` depth (concept→primitive mapping), the Codex detection-table row, 9 thin critic wrappers (3 vendors × logic/security/performance) referencing the **same SOT skills** (`vdd-adversarial`, `skill-adversarial-security`, `skill-adversarial-performance`) with the same convergence enum, each carrying the ⚠️ **scaffold/unvalidated** banner.
- **OUT (deferred):** 6d (sequential-fallback demotion + vdd-multi "Vendor dispatch" rewrite), 6e (drift-grep extension + Wave-5 generator), and ALL e2e validation. Roadmap item 6 stays **🔜 (scaffolds authored, validation + 6d/6e pending)** — **NOT** ✅.

## 3. RTM

| ID | Requirement | Target | Verification |
|----|-------------|--------|--------------|
| R1 | `references/gemini-cli.md` stub→full: §1 findings, concept-map table, **honest Layer-A-unconfirmed gap**, 3 wrapper pointers, ⚠️ scaffold banner | `references/gemini-cli.md` | file read; G1 |
| R2 | NEW `references/codex-cli.md`: TOML format, parallel-confirmed, sandbox=read-only critics, concept-map, ⚠️ banner | `references/codex-cli.md` | file read |
| R3 | `references/cursor.md` stub→full: Markdown+YAML, parallel max-10, `readonly` critics, in-session vs background (Layer B deferred), ⚠️ banner | `references/cursor.md` | file read; G1 |
| R4 | SKILL §1.1 detection table: add Codex row (`.codex/agents/`); restate Gemini/Cursor statuses as "scaffold — documented, not validated"; note Gemini Layer-A caveat. Tie-break §1.2 unaffected (AGENTS.md note already there) | `SKILL.md` §1.1 | file read; G2 |
| R5 | 9 critic wrappers at real runtime paths (`.gemini/agents/`, `.codex/agents/`, `.cursor/agents/`), thin, SOT-pointing, vendor-format-correct (Gemini/Cursor MD+YAML, Codex TOML), read-only enforced where the vendor supports it (`readonly`/`sandbox_mode`), ⚠️ scaffold note in each body | `.gemini/agents/critic-*.md` ×3, `.codex/agents/critic-*.toml` ×3, `.cursor/agents/critic-*.md` ×3 | file reads; G3 |
| R6 | SKILL version 3.5→3.6 + §9 History entry (6a–6c scaffolds authored from primary sources; validation pending) | `SKILL.md` | validate_skill |
| R7 | Bookkeeping: CHANGELOG EN+RU v3.20.9; README×2 header; roadmap item 6 (6a–6c scaffolds ✅ authored, validation/6d/6e 🔜); audit `framework-audit-080.md`; session-state | standard set | file reads |

## 4. Acceptance Criteria (Gates)
- **G1:** every non-complete reference carries the ⚠️ scaffold/unvalidated banner; `grep -rn "not.*validated\|scaffold" references/` covers gemini/codex/cursor.
- **G2:** SKILL §1.1 table has a Codex row; detection markers match §1 findings (`.codex/agents/`, `GEMINI.md`, `.cursor/`).
- **G3:** skill gate **43/43** (the parent skill still validates; wrappers are not skills); each wrapper references its SOT skill path + the 3-state enum; Codex wrappers are valid TOML (parse check).
- **G4:** pytest security-audit 30/30 (doc-only); `.md`/`.toml`-only diff, no `scripts/`.
- **G5 (honesty gate):** the Gemini Layer-A gap is stated, not papered over; roadmap item 6 NOT marked ✅ done; banners present.

## 5. Out of Scope
6d, 6e, e2e validation (operator + hardware), antigravity (unchanged), Wave-5 generator. Detection of `.codex/agents/` must not break Claude Code precedence (first-match-wins, CLAUDE.md row is first) — verified by ordering.

## 6. Open Questions
None blocking. Judgment calls: (a) wrappers placed at real runtime paths (ready to validate) not staged templates — they carry scaffold banners and point at SOT, so a real CLI reading them gets correct behavior once validated; (b) Gemini Layer-A unconfirmed → reference documents the gap rather than claiming parallelism; (c) item 6 stays open (scaffolds ≠ validated adapters).
