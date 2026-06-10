# Framework Audit 081 — Complete Item 6 In-Repo (Antigravity + 6d + 6e)

- **Task:** 081 `vendor-adapters-6d-6e-antigravity` · **Workflow:** `/framework-upgrade` · **Meta-skill:** `skill-self-improvement-verificator` (Modes A+B)
- **Date:** 2026-06-10 · **Release:** v3.20.10 · **Roadmap:** item 6 — 6a–6e in-repo ✅; operator validation ⏳

## Mode A / Mode B — **PASS**
A: root integrity ✅ (RTM R1–R7), skill compat ✅ (generator is a script not a skill; wrappers are vendor configs; TIER 0 intact), docs ✅, migration ✅ (additive + generated). B: verification ✅ (G1–G5), rollback ✅ (4 `.bak` + git, new files removable, generator idempotent), atomic ✅, coverage ✅ (doc/script-only).

## Antigravity — primary-source grounding
Primary docs render client-side (WebFetch returned empty); corroborated across antigravity.google/docs/agent-manager + Google-Cloud/Medium + DataCamp + github.com/google-gemini/gemini-cli #27305. Findings: **dynamic-first** (orchestrator spawns subagents on the fly, no files) + static **custom agents** (`agent.json` at `~/.gemini/antigravity-cli/agents/<name>/`, fields `name`/`description`/`hidden`/system-prompt); **async parallel ✅**; **detection ambiguous** (shares `AGENTS.md` w/ Codex, `~/.gemini/` w/ Gemini) — provisional `.antigravity/` marker, ambiguity documented. All recorded honestly, not papered over.

## Gates
- **G1:** `antigravity.md` carries ⚠️ SCAFFOLD + detection-ambiguity + parallel ✅ (5 markers).
- **G2:** positive "functionally equivalent" claim **removed** (only negations "NOT functionally equivalent" + the §9 History note remain); "Vendor dispatch" present in `vdd-multi` (×3) + SKILL (×2).
- **G3:** `generate_wrappers.py --check` idempotent OK; skill sweep **43/43**; **12/12** wrappers reference SOT + convergence enum; Codex TOML + Antigravity JSON parse.
- **G4:** pytest security-audit **30/30**; no scanner edits; doc/script-only diff.
- **G5 (honesty):** Antigravity dynamic-vs-static + detection ambiguity + Gemini Layer-A gap all stated; all 4 vendors ⚠️ unvalidated; **roadmap item 6 stays 🔜** (validation ⏳, not ✅).

## Deliverables
- `references/antigravity.md` (stub→full).
- `scripts/wrappers_manifest.json` + `scripts/generate_wrappers.py` → 12 wrappers (`.gemini/.codex/.cursor/.antigravity/agents/`), Claude excluded.
- `vdd-multi.md` "Vendor dispatch" rewrite + SKILL §7 demotion (C-07 claim removed); detection table Antigravity row; KNOWN_ISSUES drift-grep ×5 dirs; SKILL 3.6→3.7 + §9.

## Design decisions
1. **Generator owns the scaffold wrappers** — single manifest, `--check` drift gate; Claude stays hand-maintained donor (source-not-derived). 4 vendor formats (MD+YAML ×2, TOML, JSON) is exactly the hand-sync burden the generator removes.
2. **6d demotion shipped even though adapters are scaffold-status** (per user request) — the "Vendor dispatch" section honestly flags adapters as documented-not-validated and keeps sequential as the *proven* path until graduation, so no false "use the adapter" promise.
3. **Antigravity detection ambiguity documented, provisional marker** — resolved during validation, not guessed.
4. **Item 6 not closed** — all in-repo work done, but ✅ requires operator e2e runs.

## Verdict
**APPROVED** — gates green, vendor primitives sourced (Antigravity honestly from secondary), C-07 claim removed, generator idempotent + drift-gated, item 6 honestly left 🔜 pending validation. The in-repo half of item 6 is complete across 4 vendors. Uncommitted; operator to review, commit, and validate on real CLIs.
