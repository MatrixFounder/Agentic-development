# Tier-Diverse Mini-Experiment 078 — does model heterogeneity earn the committee its cost?

- **Task:** 078 `tier-diverse-mini-experiment` · validates the R3c tier-diverse escalation pilot shipped in task 077 (v3.20.7)
- **Date:** 2026-06-10 · **Corpus:** `tests/fixtures/ab-corpus-2/` (NEW — the 075 corpus is burned) · sealed `seal.json` @ 2026-06-10T12:53:58Z before any run
- **Scale:** 3 arms, 7 files (6 seeded + 1 control), 18 bugs (6/6/6 class, 6/6/6 severity), N=3 → 147 agents, ~2.35M tokens, ~17 min
- **Scorer:** `analyze.py`, frozen pre-data. Match = file + |Δline|≤3 + class. Full output: `analysis.json`.

## Arms
- **A** — single reviewer, plain exhaustive prompt, `opus`.
- **D-same** — `/vdd-multi` committee, all 3 critics `opus` (reproduces 075 arm D on the new corpus).
- **D-tier** — `/vdd-multi --models=logic:sonnet,security:opus,performance:fable` — three distinct tiers (the R3c config).

## Results

| Arm | recall μ (N=3) | var | pooled | FP/file | FP on controls (Σ3) | bikeshed % | overlap precision | tokens |
|---|---|---|---|---|---|---|---|---|
| **A** | 0.870 | 0.0048 | 0.944 | **5.14** | 14 | 17.6% | — | 464k |
| **D-same** | 0.963 | 0.0007 | **1.000** | 7.95 | 18 | 7.2% | **0.726** (122/168) | 888k |
| **D-tier** | **0.981** | 0.0007 | **1.000** | 10.05 | 27 | 7.3% | 0.664 (154/232) | 996k |

Per-run recall: A .944/.778/.889 · D-same 1.0/.944/.944 · D-tier 1.0/.944/1.0. Both committees found all 18 bugs pooled; A missed only `g5-SEC` (log injection — the subtlest security bug).

## Pre-registered verdicts (mechanical, `analysis.json`)

**T1 — does the tier-diverse committee earn its cost vs the single reviewer?** *(recall ≥ +10pp AND FP no worse)*
→ **FAILS the conjunction.** recall(D-tier) − recall(A) = **+11.1pp** (clears the +10pp bar that same-model failed in 075 at +5.6pp!) — **but** FP/file nearly doubled (10.05 vs 5.14), so the "FP no worse" condition fails. The committee wins recall by **reporting more, not aiming better**.

**T2 — does heterogeneity add over a same-model committee?** *(Δrecall > pooled run variance)*
→ **Technically yes, trivially.** D-tier − D-same = **+1.9pp** (> variance 0.0007). But both already hit 100% pooled; the gap is ~0.3 bugs/18 in mean recall, bought at +2.1 FP/file and +108k tokens. Heterogeneity adds a sliver of per-run stability, not new coverage.

**T3 — is cross-tier agreement more *truthful* than same-tier agreement?** *(the premise R3c's escalation bets on)*
→ **NO — the decisive negative.** D-tier overlap precision **0.664 < 0.726** D-same. Tier-diverse critics produced **more** same-location overlaps (232 vs 168) but a **smaller fraction were real bugs**. Cross-tier agreement was *lower* quality, not higher.

## What this means for the R3c pilot

R3c's tier-diverse `+1` escalation rests on one assumption: critics on different tiers are more independent, so their **agreement** is stronger confirmation and deserves a severity bump. **T3 directly contradicts that on this corpus** — tier-diverse agreement was *less* precise than same-tier agreement (0.66 vs 0.73). Escalating on it would amplify false positives, not catch more real criticals.

Meanwhile the **`--models` capability itself has value**: D-tier reached the highest recall (0.981, 100% pooled) and cleared the +10pp recall bar same-model couldn't. The split verdict:

| R3c component | Verdict | Recommendation (operator decision, separate cycle) |
|---|---|---|
| `--models` config (tier-diverse spawn) | **useful** — highest recall, 100% pooled coverage | keep as a coverage/recall opt-in |
| tier-diverse **+1 escalation** on agreement | **not supported** (T3 failed; agreement precision dropped) | **demote** — treat tier-diverse same-mechanism overlaps as `corroborated`, not escalated, until stronger (ideally cross-vendor) evidence. Keep the gradation table's cross-vendor row as the real open question (item 6). |

This is the VDD discipline working as designed: R3c shipped explicitly as a **pilot**, the validation ran, and the data says the escalation premise doesn't hold for *tier* diversity (same vendor family). The framework should now caveat or demote the tier-diverse +1 — a follow-up `/framework-upgrade` cycle, not auto-applied here (experiment = evidence, not edits).

## Honest limitations

1. **Tier↔domain confound:** logic=sonnet (lowest tier), security=opus, performance=fable (highest) — recall blends tier and which domain got which model. The T3 overlap-precision result is more robust to this (it measures agreement quality across all overlaps), but the recall deltas are confounded.
2. **Same-vendor family only:** these are Claude tiers (partial independence by design). The gradation table's *cross-vendor* row (quasi-independent) is **untested** — needs item 6 adapters. T3's negative is evidence against the *tier* bet, not necessarily the *vendor* bet.
3. **Corpus-dependent committee lift:** corpus-2's bugs are more semantic (regex floor ≈ 0 vs corpus-1's 4/8 security), which is *why* even same-model committee did better here (+9.3pp) than in 075 (+5.6pp). Committee value scales with how non-pattern the bugs are.
4. **N=3, one corpus, deterministic merge in scorer.** Low power; verdicts use pooled run variance, not significance tests (pre-registered).

## Consequences for the roadmap

- **Item 7 R3c tier-diverse:** config validated as a recall tool; **escalation premise not confirmed** → recommend demote-to-`corroborated` in a follow-up cycle. The cross-vendor row stays the genuine open question (⏳ item 6).
- **Item 7 overall:** R3a/R3b/R3d ✅ (072), R3c tier-diverse config ✅ (077) + escalation flagged for demotion (078), R3c cross-vendor ⏳ (item 6). Item 7 effectively closed pending the operator's demote decision and the cross-vendor work.

**Publishable note:** combined with experiment 075, this is now a two-corpus, pre-registered look at multi-critic LLM review: same-model committees don't earn their cost (075 rule 2), tier-diverse committees reach higher recall but with worse precision and no agreement-quality gain (078 T1/T3). No comparable study exists as of 2026-06-10.
