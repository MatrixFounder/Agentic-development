# Technical Specification: Tier-Diverse Mini-Experiment (validates R3c, item 7 / C-12 follow-up)

### 0. Meta Information
- **Task ID:** 078
- **Slug:** `tier-diverse-mini-experiment`
- **Mode:** Experiment (🧪 — new sealed corpus + scorer + report; validates task 077's R3c pilot; **modifies no framework component**; any rule adjustment is a separate follow-up cycle)
- **Type:** Empirical validation of roadmap item 7 R3c (tier-diverse escalation), follow-up to experiment 075. Protocol: a focused 3-arm A/B in the same pre-registered spirit as Appendix A.
- **Source:** User request (2026-06-10): "выполни R3c tier-diverse и затем мини-эксперимент". Answers the question experiment 075 left open: does model-tier heterogeneity restore the +10pp committee cost-bar that the same-model committee failed (rule 2: D−A was only +5.6pp)?

## 1. Question & pre-registered rules

Experiment 075 found a same-model 3-critic committee (arm D) beat the best single reviewer by only +5.6pp — below the +10pp bar that justifies its 3.25× cost (rule 2 FAILED). R3c's thesis: critics on **different model tiers** are partially independent, so a tier-diverse committee should find more than a same-model one. This experiment tests that on a **fresh sealed corpus** (the 075 corpus is burned — its arms have seen it).

**Arms** (fresh context per run, N=3):
- **A** — single reviewer, plain exhaustive prompt, `opus` (the 075 best-value baseline).
- **D-same** — `/vdd-multi` committee, all 3 critics on `opus` (reproduces 075 arm D on the new corpus).
- **D-tier** — `/vdd-multi --models=logic:sonnet,security:opus,performance:fable` — 3 distinct tiers.

**Pre-registered decision rules (fixed before any run):**
- **T1 (tier-diversity earns the committee cost):** recall(D-tier) − recall(A) ≥ **+10pp** at FP/file no worse than A. If yes → R3c tier-diverse +1 is empirically justified; if no → committee still doesn't beat the single reviewer even with heterogeneity.
- **T2 (heterogeneity adds over same-model committee):** recall(D-tier) − recall(D-same) > pooled run variance of the two. If yes → tier-diversity adds signal; if no → the diversity buys nothing measurable here.
- **T3 (corroboration-quality, secondary):** on same-mechanism overlaps, report how often D-tier's agreeing critics were CORRECT vs D-same's — the mechanism R3c's escalation bets on (does cross-tier agreement track truth better than same-tier?).

## 2. RTM
| ID | Requirement | Verification |
|----|-------------|--------------|
| R1 | NEW corpus: 6 seeded files + 1 control, **18 bugs** (6 logic/6 security/6 performance; 6 CRITICAL/6 HIGH/6 MEDIUM); different domain from 075 (ETL/data-pipeline) to avoid any overlap. `ground_truth.json` + `seal.json` sealed before runs | seal predates results; anchors grep-derived |
| R2 | `analyze2.py` frozen pre-data: match = file + \|Δline\|≤3 + class; per-arm recall mean±var, pooled, FP/file, bikeshedding; rules T1/T2/T3 mechanical; tier-diverse merge = deterministic (same as 075 D) | script exists pre-run |
| R3 | Runs: A (21 single opus), D-same (21×3 opus critics), D-tier (21×3 mixed-tier critics); findings persisted per (arm,file,run); evidence line `tests: NOT RUN` per v3.20.5; D-security gets scan slice | result-file completeness |
| R4 | Report `docs/reviews/tier-diverse-experiment-078.md`: tables, T1/T2/T3 verdicts, limitations (tier↔domain confound, N=3, same-vendor family), consequence for R3c pilot status (confirm / keep-as-pilot / flag); roadmap item 7 update; session-state | file read |

## 3. Out of Scope
Changing the R3c rule text based on results — separate cycle if T1/T2 fail. Cross-vendor arms (need item 6). Corpus reuse from 075.

## 4. Known limitations (declared pre-run)
(a) **Tier↔domain confound:** each domain gets a fixed tier (logic:sonnet/security:opus/performance:fable), so a per-class recall delta blends tier and domain — overall recall is the pre-registered metric, the confound is noted; (b) same-vendor family (Claude tiers) — partial independence by design, not the cross-vendor quasi-independence; (c) N=3 low power, rules use pooled variance not significance; (d) deterministic merge in scorer; (e) fable/sonnet availability assumed (harness aliases).
