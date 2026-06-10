# Framework Audit: Retire the Politeness-Filter Rationale; Reposition vdd-sarcastic (Task 071)

**Date:** 2026-06-10
**Auditor:** Self-Improvement Verificator (`skill-self-improvement-verificator` v1.0)
**Target:** `docs/TASK.md` (Mode A — SPECIFICATION AUDIT) · `docs/PLAN.md` (Mode B — PLAN AUDIT, appended below)
**Status:** see per-mode verdicts

## 0. Emergency Bypass
- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

**Justification:** none required — no bypass used. All edited skills are Tier 2; the wrapper is a `.claude/agents/` thin file; no Tier 0 skill, no bootstrap file (`CLAUDE.md`/`AGENTS.md`/`GEMINI.md`), no `System/Agents/` prompt is modified.

---

## Mode A — SPECIFICATION AUDIT (`docs/TASK.md`, Task 071)

### 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | [x] Pass | ID 071, slug `retire-politeness-filter-rationale`, mode, type, workflow, source — all present. Old task 070 archived in lockstep (`task-070-…` + `plan-070-…`) before creation. |
| **Root Integrity** | [x] Pass | Atomicity: 10 RTM rows, each one file/concern. Traceability: every row carries its audit claim (C-01/C-03/K2) and a named verification gate (G1–G4). Stub-First: N/A — documentation-content change, zero scripts/code. Anti-hallucination: blast radius established by executed repo-wide greps (3 rationale locations, 2 mandatory-persona locations, 1 wrapper, 1 procedural mandate), not assumed from the roadmap — and the roadmap's own `vdd-adversarial/SKILL.md:24` line-number drift was caught (the "politeness" token actually sits at :59; :24 is the principle bullet). |
| **Skill Compatibility** | [x] Pass | No new agents or prompts are created; the 4 edited skills keep tier/structure/frontmatter contract (only `version:` and `description:` fields change). TIER 0 loading paths untouched. |
| **Documentation** | [x] Pass | R8 syncs `System/Docs/SKILLS.md` (3 rows); R9 covers CHANGELOG EN+RU v3.20.2, README header bump (release convention `3df62a2`/`c348928`), roadmap status flip. `WORKFLOWS.md` untouched — correct, since no workflow file changes. |
| **Migration** | [x] Pass | No session-state schema change; no consumer of the old wording exists outside the 6 edited files (G2 wrapper-drift grep proves it post-edit). The two `(supersedes "Forced Negativity")` notes preserve term traceability for readers of archived tasks/audits. |

### 2. Risk Analysis

- **Risk 1 — Acceptance-grep self-trip (lesson 070):** new retirement notes could reintroduce the token "politeness". Mitigated by an explicit TASK constraint (R2: "note's wording must NOT contain the token") and the hardened G1 grep covering bare "politeness" across `.agent/ System/ .claude/`.
- **Risk 2 — Defanging the critics (recall regression):** removing "be harsh" mandates could be over-rotated into "be lenient". Mitigated: every reworded line replaces tone-pressure with the *stronger* explicit instruction ("report every issue incl. low-confidence; never filter in your head") — the vendor-documented recall lever; Objective Convergence exit bars stay byte-untouched (K1 mechanics scored Current).
- **Risk 3 — Scope bleed into C-02 (item 8):** "relationship drift" wording lives in the same files and could get swept up. Mitigated by an explicit out-of-scope entry (§4.3) listing the exact lines to leave alone.
- **Risk 4 — Wrapper/SOT drift (Wave-1/2 class):** wrapper says "mandatory per SKILL §2" while SKILL §2 becomes optional. Mitigated: R5 syncs the wrapper in the same change; G2 greps the old wording to empty.

### 3. Verdict & Actions (Mode A)

**APPROVED** — specification is safe, evidence-grounded, atomic, and respects Constitutional (Tier 0) boundaries. No required actions.

---

## Mode B — PLAN AUDIT (`docs/PLAN.md`, Task 071)

*(appended after planning phase)*

### 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | [x] Pass | Phase T4 runs `validate_skill.py` on each of the 4 edited skills + full 43/43 sweep (G3), pytest 30/30 (G4), and the G1/G2 acceptance greps with expected-output assertions. |
| **Rollback** | [x] Pass | Phase T0 backs up every bootstrap file present (`CLAUDE.md`/`AGENTS.md`/`GEMINI.md` per workflow §3.1) **and** all 13 edit targets to `.agent/archive/` before any edit; fallback restore command documented in workflow §5. |
| **Atomic Updates** | [x] Pass | One phase per file-cluster (T1 K1, T2 K2, T3 security/perf critics + wrapper, T5 registry/release); each phase ends with its own file-level check before the global gates. |
| **Test Coverage** | [x] Pass | No code/scripts change → no new tests required; existing suite (30 tests) reused as regression evidence, consistent with 069/070 precedent. Example update (R7) doubles as living documentation of the new reporting contract. |

### 2. Verdict & Actions (Mode B)

**APPROVED** — plan contains explicit backup, per-phase verification, and measurable gates. No required actions.

---

## Post-Execution Evidence (2026-06-10, same session)

| Gate | Result |
| :--- | :--- |
| **G1** `grep -ri "politeness filter" .agent/ System/` | **empty** (exit 1). Hardened bare-token grep over `.agent/ System/ .claude/` also empty. Scope note: `--exclude-dir=archive --exclude-dir=sessions` — `.agent/archive/` holds the intentional pre-edit rollback copies (workflow §3.1) and `.agent/sessions/latest.yaml` contains the task *slug* `retire-politeness-filter-rationale` (a name, not a rationale). |
| **G2** mandate tokens (`mandatory per SKILL §2`, `Sarcasm breaks complacency`, `Meanness is the mechanism`, `frame ALL feedback sarcastically`, `State the problem sarcastically`) | **empty** (exit 1) across `.agent/ .claude/ System/`. One residue was caught by this very gate mid-execution (`vdd-sarcastic/SKILL.md` §3 "frame ALL feedback sarcastically") and fixed before sign-off — the gate worked as designed. |
| **G2b** "Forced Negativity" residue | exactly the 2 `(supersedes "Forced Negativity")` traceability notes (`vdd-adversarial/SKILL.md:24`, `references/vdd-methodology.md:44`). |
| **G3** skill quality gate | per-skill `validate_skill.py` pass (warning-first hints only); full sweep **43/43** (= pre-edit baseline). |
| **G4** regression evidence | `pytest .agent/skills/security-audit/tests/` **30/30** (= pre-edit baseline; no scripts touched). |
| **KNOWN_ISSUES Wave-1/2** | no SOT path renamed; `critic-security.md` wrapper wording synced in the same change; `sarcastic.md` asset path still valid (file kept as the optional persona). |

**Out-of-repo observation (reported, not acted on):** `~/.claude/skills/vdd-{sarcastic,adversarial}` symlink into the separate `Universal-skills` repo, whose `skills/vdd-*` directories are **independent stale copies** of these skills (consistent with the operator's repo-sync-topology note: agentic-development is canonical). Manual sync of Universal-skills recommended as operator follow-up.
