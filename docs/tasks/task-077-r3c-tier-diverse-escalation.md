# Technical Specification: R3c Tier-Diverse Escalation (C-08 remainder, roadmap item 7)

### 0. Meta Information
- **Task ID:** 077
- **Slug:** `r3c-tier-diverse-escalation`
- **Mode:** Framework Upgrade (1 workflow + 1 skill + 2 references/examples; lockstep rule edit across 4 locations; zero script change)
- **Type:** P1 modernization, roadmap item **7 R3c** — the last open slice of claim **C-08**. Adds the **tier-diverse** form (same vendor, different model tier — available in Claude Code today); the **cross-vendor** row stays ⏳ BLOCKED BY item 6.
- **Workflow:** `/framework-upgrade` (verificator Modes A+B).
- **Source:** User request (2026-06-10): "выполни R3c tier-diverse и затем мини-эксперимент" + roadmap item 7 R3c (gradation table, per-critic model config, env-override warning) + experiment-075 finding that same-model multi fails its cost bar (rule 2) → tier-diversity is the remaining lever.

## 1. General Description

Merge rule 3 (severity escalation) was redesigned in task 072 for the **same-model** case: agreement = corroboration, no auto-escalation (R3a); only different-mechanism overlap escalates (R3b); sequential never escalates (R3d). R3c adds the **model-independence axis**: when critics run on genuinely different models, same-location agreement carries more signal than persona variation alone, so *some* escalation is re-earned.

**The signal-strength gradation (roadmap-specified — wording authority):**

| Critic pair | Independence | Escalation on same-mechanism agreement |
|---|---|---|
| Same model, different persona | none (~60% shared-error, arXiv:2506.07962) | **no** — `corroborated` tag only (R3a) |
| Same vendor, different tier (haiku/sonnet/opus/fable) — **Claude Code today** | partial (correlated within family) | **+1 only for CRITICAL/HIGH** candidates; tag `tier-diverse` |
| Different vendors (Claude/Gemini/GPT) — **needs item 6 adapters** | quasi-independent | full +1 restored — ⏳ deferred |

**Config:** `/vdd-multi` gains an optional `--models=logic:<tier>,security:<tier>,performance:<tier>` flag (Phase 0 parse, Phase 1 per-critic spawn). When absent → all critics on the wrapper default (`opus`) → pure R3a, unchanged behavior.

**Env-override guard:** `CLAUDE_CODE_SUBAGENT_MODEL`, when set, silently overrides frontmatter/`--models` pins and **flattens** the heterogeneity. The workflow must detect this and **downgrade tier-diverse escalation back to R3a** (corroborated only) with a warning — escalating on a config that the env secretly collapsed would be false confidence.

**Empirical status:** the tier-diverse +1 is a **theory-grounded pilot**; its real-world payoff is validated by the mini-experiment that follows this task (separate task 078). The escalation rule ships marked as pilot; the gradation table is the independence model, not a proven recall claim.

## 2. RTM

| ID | Requirement | Target file(s) | Verification |
|----|-------------|----------------|--------------|
| R1 | Merge rule 3 gains the gradation table + a third bullet: same-mechanism agreement under a **tier-diverse** config (different model tiers, env not flattening) → escalate +1 **only for CRITICAL/HIGH**, tag `tier-diverse`; same-mechanism same-model stays R3a. Lockstep across vdd-multi Phase 2 + SKILL §6 (byte-identical modulo critics↔teammates noun split). | `.agent/workflows/vdd-multi.md`, `.agent/skills/skill-parallel-orchestration/SKILL.md` §6 | G1 grep; G2 normalized diff; validate_skill |
| R2 | Phase 0 parses `--models=logic:<t>,security:<t>,performance:<t>` (subset of `{haiku,sonnet,opus,fable}`; partial maps allowed, unset critics → default); Phase 1 spawns each critic with its assigned model; flags table documents `--models` | `.agent/workflows/vdd-multi.md` Phase 0/1 + params table | file read |
| R3 | Env-override guard: Phase 0 checks `CLAUDE_CODE_SUBAGENT_MODEL`; if set with a `--models` config present → warn + force escalation tier back to R3a (corroborated only) for the run | `.agent/workflows/vdd-multi.md` Phase 0 + rule 3 note | file read; G1 |
| R4 | Sequential fallback: tier-diverse is impossible (single instance) → merge step 3 explicitly states the gradation does not apply; stays never-escalate | `references/sequential-fallback.md` | G1 grep |
| R5 | Usage example merge walkthrough mentions the tier-diverse case (one line) | `examples/usage_example.md` | file read |
| R6 | `claude-code.md` Model-pin hygiene §: cross-ref the new `--models` flag as the consumer of the tier ladder; parent skill version 3.3→3.4; §9 History entry | `references/claude-code.md`, SKILL frontmatter + §9 | validate_skill |
| R7 | Bookkeeping: CHANGELOG EN+RU v3.20.7; README×2 header; roadmap item 7 → R3c tier-diverse ✅ (cross-vendor still ⏳ item 6); audit `framework-audit-077.md`; session-state | standard set | file reads |

## 3. Acceptance Criteria (Gates)
- **G1:** `grep -rn "tier-diverse" .agent/` → present in vdd-multi.md, SKILL.md, sequential-fallback.md, usage_example.md, claude-code.md (5 surfaces); env-guard phrase present in vdd-multi Phase 0.
- **G2:** rule-3 gradation text in vdd-multi.md Phase 2 and SKILL §6 byte-identical modulo the documented critics↔teammates noun split (normalized diff in audit).
- **G3:** skill gate 43/43; **G4:** pytest security-audit 30/30 (doc-only); **G5:** `.md`-only diff.
- **G6 (do-not-touch):** merge rules 1, 2, 4, 5; R3a corroborated text; R3b different-mechanism +1; R3d sequential-never; evidence contract (074); flags `--scope/--no-fix/--fail-on/--output/--diff-only`; iteration caps — byte-unchanged except where R1–R4 explicitly extend.

## 4. Out of Scope
1. **Cross-vendor row** — needs item 6 adapters; stays ⏳ in the gradation table and roadmap.
2. **Actually changing the wrapper default** from opus — R3c adds opt-in config, not a new default.
3. **The mini-experiment** — separate task 078 (validation), runs after this lands.
4. Merge rules 1/2/4/5, evidence contract, exit bars — do-not-touch.

## 5. Open Questions
None. Gradation table, config syntax, and env-guard semantics are roadmap-specified. Judgment calls: (a) tier-diverse +1 gated to CRITICAL/HIGH (roadmap-literal — conservative, avoids inflating MEDIUM noise); (b) env-flatten downgrades to R3a, not just warns (false-confidence avoidance); (c) escalation rule ships as "pilot" pending task-078 empirical validation.
