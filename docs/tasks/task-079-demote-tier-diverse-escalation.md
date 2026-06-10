# Technical Specification: Demote Tier-Diverse Escalation to Corroborated (C-08, item 7 R3c — data-driven correction)

### 0. Meta Information
- **Task ID:** 079
- **Slug:** `demote-tier-diverse-escalation`
- **Mode:** Framework Upgrade (lockstep rule edit across the same 5 R3c surfaces from task 077; zero script change)
- **Type:** Evidence-driven correction of roadmap item 7 R3c. Mini-experiment 078 (`docs/reviews/tier-diverse-experiment-078.md`) **refuted** the tier-diverse `+1` escalation premise (T3: cross-tier agreement precision 0.66 < same-tier 0.73). This task translates that finding from a report recommendation into the rule text.
- **Workflow:** `/framework-upgrade` (verificator Modes A+B).
- **Source:** User request (2026-06-10): "да, запускай" — approving the demotion cycle proposed after experiment 078.

## 1. General Description

Task 077 shipped the R3c tier-diverse escalation as an explicit **pilot**: same-mechanism agreement under a tier-diverse `--models` config earned `+1` for CRITICAL/HIGH (tag `tier-diverse`). The pilot's sole premise — that cross-tier agreement is *stronger evidence* than same-tier — was tested in experiment 078 and **failed**: tier-diverse critics produced more same-location overlaps (232 vs 168) but a *smaller* fraction were real bugs (66% vs 73%). Escalating severity on lower-precision agreement manufactures false positives. So the escalation is demoted to a **tag only** (`tier-diverse`, no `+1`), matching the same-model R3a treatment.

**What stays:** the `--models` config itself (validated by 078 as a recall/coverage tool — D-tier reached 0.981 recall, 100% pooled). Only the *severity bump* is removed.

**What stays untouched:** R3a (same-model corroborated), R3b (different-mechanism `+1` — mechanism-based, never in question), R3d (sequential never-escalate), dedup rule 1, rules 2/4/5, evidence contract (074), flags, env-flatten guard (its R3a downgrade is now moot for tiers but kept as a correctness note).

**Cross-vendor row:** stays ⏳ BLOCKED BY item 6 — 078 tested *tiers within one vendor*, not *true cross-vendor independence*. The quasi-independent escalation remains an open question, explicitly distinguished from the refuted tier bet.

## 2. RTM

| ID | Requirement | Target file(s) | Verification |
|----|-------------|----------------|--------------|
| R1 | Gradation table middle row: "Same vendor, different tier → +1 for CRITICAL/HIGH, tag `tier-diverse`" → "→ **no escalation — `tier-diverse` tag only**" with an inline 078 citation (agreement precision 0.73→0.66). Lockstep across vdd-multi Phase 2 + SKILL §6 (byte-identical mod critics↔teammates) | `.agent/workflows/vdd-multi.md`, `.agent/skills/skill-parallel-orchestration/SKILL.md` §6 | G1 grep; G2 normalized diff; validate_skill |
| R2 | Rule-3 third bullet: tier-diverse same-mechanism → tag `tier-diverse`, severity = max (rule 1), **NO +1**; cite 078. The bullet stays (documents the config exists) but no longer escalates | same two files | G1; G2 |
| R3 | `--models` flag + Phase 0 parse + Phase 1 spawn **unchanged** (config kept); Phase 0 escalation-tier resolution simplified: `tier-diverse` resolves to tag-only (no CRITICAL/HIGH bump); env-flatten guard note kept but reworded (moot for escalation, still correct re: model identity) | `.agent/workflows/vdd-multi.md` Phase 0/1 | file read; G3 do-not-touch on flags |
| R4 | `usage_example.md` + `claude-code.md` cross-refs: drop the tier-diverse escalation mention, keep the config-as-recall-tool framing; cite 078 | `references/sequential-fallback.md` (tier-diverse-impossible note stays), `examples/usage_example.md`, `references/claude-code.md` | G1 |
| R5 | Version skill-parallel-orchestration 3.4→3.5 + §9 History entry (R3c escalation demoted per 078; config retained) | SKILL frontmatter + §9 | validate_skill |
| R6 | Bookkeeping: CHANGELOG EN+RU v3.20.8; README×2 header; roadmap item 7 (R3c tier-escalation → resolved/demoted; cross-vendor still ⏳ item 6); audit `framework-audit-079.md`; session-state | standard set | file reads |

## 3. Acceptance Criteria (Gates)
- **G1:** `grep -rn "tier-diverse" .agent/` still on its surfaces, but **no `+1`/escalate wording attached to the tier-diverse case** — grep `escalate.*tier-diverse|tier-diverse.*\+1` → empty; the 078 citation present in vdd-multi + SKILL.
- **G2:** rule-3 block in vdd-multi Phase 2 vs SKILL §6 → identical modulo critics↔teammates (normalized diff).
- **G3:** skill gate 43/43; pytest security-audit 30/30; `.md`-only diff.
- **G4 (do-not-touch):** R3a corroborated bullet, R3b different-mechanism `+1`, R3d sequential-never, dedup rule 1, rules 2/4/5, evidence contract, `--models` flag definition + Phase 0/1 parse/spawn — byte-unchanged except R1/R2/R3's explicit edits.

## 4. Out of Scope
1. Removing the `--models` config — it is validated; only the escalation is demoted.
2. The cross-vendor escalation row — stays ⏳ item 6 (distinct, untested question).
3. Re-running any experiment — 078 is the evidence; this is the code-side correction.
4. Touching R3a/R3b/R3d, evidence contract, flags, merge rules 1/2/4/5.

## 5. Open Questions
None. 078's verdict is unambiguous for the tier case. Judgment calls: (a) keep the tier-diverse *tag* (it still records "found under heterogeneous models" provenance, just without severity consequence); (b) keep the gradation table's cross-vendor row as the live open question, explicitly separated from the refuted tier row; (c) retain `--models` + env-guard mechanics (recall tool + correctness), demote only the escalation.
