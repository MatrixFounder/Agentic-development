# Framework Audit 079 — Demote Tier-Diverse Escalation to Tag-Only

- **Task:** 079 `demote-tier-diverse-escalation` · **Workflow:** `/framework-upgrade` · **Meta-skill:** `skill-self-improvement-verificator` (Modes A+B)
- **Date:** 2026-06-10 · **Release:** v3.20.8 · **Evidence:** `docs/reviews/tier-diverse-experiment-078.md` (T3: cross-tier agreement precision 0.66 < 0.73)

## Mode A — SPECIFICATION AUDIT — **PASS**
Root integrity ✅ (RTM R1–R6 atomic, lockstep); skill compat ✅ (no new agents, TIER 0 intact); documentation ✅ (R6); migration ✅ (subtractive — removes an escalation; `--models` behavior preserved; G1 grep).

## Mode B — PLAN AUDIT — **PASS**
Verification ✅ (G1–G4 incl. normalized lockstep diff + do-not-touch); rollback ✅ (5 file `.bak` + bootstrap + git at `01a657a`); atomic ✅; test coverage ✅ (doc-only, suites as regression).

## Gates
- **G1:** no positive `+1`/escalation attached to the tier-diverse case anywhere — stale phrases ("for CRITICAL/HIGH only, tag tier-diverse"; "R3c — pilot") survive **only** in the immutable v3.4 §9 History record and the new demotion text; 078 cited in `vdd-multi.md` + `SKILL.md`. The Positioning block (line 15) updated: tier-diversity tested-and-demoted, cross-vendor is the open lever.
- **G2:** rule-3 block in `vdd-multi.md` Phase 2 vs `SKILL.md` §6 → **IDENTICAL modulo critics↔teammates** (Python normalized-diff).
- **G3:** skill sweep **43/43**; pytest security-audit **30/30**; `.md`-only diff.
- **G4 (do-not-touch):** R3a `corroborated` bullet (×1 each file), R3b different-mechanism `escalate severity by one level` (×1 each — the only surviving escalation), evidence contract (`exit-bar condition` ×2), `--models` flag definition (×1), R3d sequential-never — all byte-unchanged.

## What changed (and what did not)

| Component | Before (v3.20.7) | After (v3.20.8) |
|---|---|---|
| tier-diverse same-mechanism overlap | `+1` for CRITICAL/HIGH, tag `tier-diverse` | **tag `tier-diverse` only, no `+1`** |
| `--models` config (flag/parse/spawn) | present | **unchanged** (recall tool) |
| Phase 0 step 5 | escalation-tier resolution | provenance-tag resolution |
| env-flatten guard | "never award the +1" | "downgrade tag to `corroborated`" |
| R3a / R3b / R3d / dedup / rules 2,4,5 / evidence / flags | — | **byte-unchanged** |

The only severity escalation remaining anywhere in the merge logic is **R3b** (different failure mechanisms at the same location) — mechanism-based, never in question.

## Design decisions
1. **Tag retained, escalation removed:** `tier-diverse` still records heterogeneous-model provenance (useful signal for a human reading the report), it just no longer changes severity.
2. **Config kept:** 078 validated `--models` as a recall/coverage tool (highest recall, 100% pooled) — demoting the escalation does not touch the spawn capability.
3. **Cross-vendor row preserved as the live question:** 078 tested *tiers within one vendor*; true cross-vendor independence is untested and stays ⏳ item 6, explicitly distinguished from the refuted tier bet.
4. **History is append-only:** the v3.4 entry (which shipped the +1) stays verbatim; v3.5 records the demotion. Auditors see the full pilot→validate→correct arc.

## Versions
`skill-parallel-orchestration` 3.4→**3.5**; framework v3.20.7→**v3.20.8**.

## Verdict
**APPROVED** — gates green, lockstep byte-verified, do-not-touch surfaces intact, rollback layers present. The 075→077→078→079 arc is now self-consistent: a pilot shipped, validated on a sealed corpus, and corrected by its own data. Uncommitted; operator to review and commit.
