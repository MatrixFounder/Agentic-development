# Framework Audit 080 — Vendor Adapter Scaffolds 6a–6c

- **Task:** 080 `vendor-adapter-scaffolds` · **Workflow:** `/framework-upgrade` · **Meta-skill:** `skill-self-improvement-verificator` (Modes A+B)
- **Date:** 2026-06-10 · **Release:** v3.20.9 · **Roadmap:** item 6 sub-tasks 6a–6c (in-repo portion); validation + 6d/6e stay ⏳

## Mode A — SPECIFICATION AUDIT — **PASS**
Root integrity ✅ (RTM R1–R7 atomic); skill compat ✅ (parent skill validates; wrappers are vendor configs, not skills; TIER 0 intact); documentation ✅ (R7); migration ✅ (additive — new references/wrappers, detection precedence preserved).

## Mode B — PLAN AUDIT — **PASS**
Verification ✅ (G1–G5 incl. TOML parse + honesty gate); rollback ✅ (3 `.bak` + git `7d09d86`; new files removable); atomic ✅; test coverage ✅ (doc-only).

## Primary-source grounding (the key risk this task faced)
Knowledge cutoff (Jan 2026) predates these CLIs' subagent features (Jan–Apr 2026), so vendor primitives were **fetched from primary docs in-session**, not recalled:

| Vendor | Source | Parallel Layer A? | Read-only critic |
|---|---|---|---|
| Codex CLI | developers.openai.com/codex/subagents | ✅ confirmed (spawns parallel, consolidates) | `sandbox_mode="read-only"` |
| Cursor 2.4 | cursor.com/docs/subagents + changelog/2-4 | ✅ confirmed (max 10) | `readonly: true` |
| Gemini CLI | geminicli.com/docs/core/subagents | ⚠️ **NOT documented** (auto-delegation + `@name` only) | read-only `tools` whitelist |

**Honesty gate (G5):** the Gemini Layer-A gap is stated explicitly in `gemini-cli.md` (3×) and the detection table, correcting the roadmap's optimistic "concurrent subagents" note. Roadmap item 6 is **not** marked ✅ — scaffolds ≠ validated adapters.

## Gates
- **G1:** all 3 references carry the ⚠️ SCAFFOLD banner (×3 each).
- **G2:** `SKILL.md §1.1` has a Codex row (`.codex/agents/`); markers match primary findings; CLAUDE.md row remains first (Claude precedence preserved in this repo).
- **G3:** skill sweep **43/43**; all 3 Codex TOML parse with required fields + `sandbox_mode="read-only"`; all 9 wrappers reference their SOT skill + the convergence enum.
- **G4:** pytest security-audit **30/30**; no code files touched (`.md`/`.toml` + new vendor dirs only).
- **G5:** Gemini gap stated; item 6 not ✅; banners present.

## Deliverables
- `references/codex-cli.md` (NEW), `references/gemini-cli.md` + `references/cursor.md` (stub→full).
- `.codex/agents/critic-{logic,security,performance}.toml`, `.gemini/agents/critic-*.md`, `.cursor/agents/critic-*.md` (9 wrappers).
- `SKILL.md` §1.1 Codex row + scaffold-status note; version 3.5→3.6 + §9 History.

## Design decisions
1. **Wrappers at real runtime paths** (not staged templates) — ready to validate; each carries a scaffold banner and points at SOT, so a real CLI reading them behaves correctly once validated. First-match-wins detection keeps Claude precedence in this (Claude) repo.
2. **Gemini gap documented, not papered over** — the multi-critic flow stays sequential-delegation on Gemini until a real run proves parallel.
3. **Read-only critic guarantee mapped per vendor** — `sandbox_mode`/`readonly`/`tools` are the runtime-enforced analogues of withholding Bash/Write from a Claude critic.
4. **Item 6 stays open** — this is the in-repo half; validation (operator hardware) + 6d/6e remain.

## Verdict
**APPROVED** — gates green, primitives primary-source-verified, honest about the Gemini gap, rollback intact. Scaffolds are ready for operator validation; **item 6 remains 🔜** until an e2e `/vdd-multi --no-fix` graduates each runtime. Uncommitted; operator to review and commit.
