# A/B Experiment 075 — Sarcasm & Multi-Critic Effectiveness (C-12, roadmap item 13)

- **Task:** 075 `ab-experiment-sarcasm-multicritic` · **Protocol:** audit-067 **Appendix A**, pre-registered (not redesigned) · **Date:** 2026-06-10
- **Corpus:** `tests/fixtures/ab-corpus/` — 8 seeded files + 2 clean controls, 24 bugs (8 logic / 8 security / 8 performance; 8 CRITICAL / 8 HIGH / 8 MEDIUM). Ground truth + corpus **sealed before any run**: `seal.json` @ 2026-06-10T10:50:01Z (11 sha256 hashes). Stratification machine-asserted.
- **Scorer:** `analyze.py`, frozen pre-data. Match = same file + |Δline| ≤ 3 + class equal. Full machine output: `analysis.json`.
- **Models:** arms A–D on `opus` (= critic-wrapper pin; harness alias claude-opus-4-8), arm E on `fable` (claude-fable-5). `CLAUDE_CODE_SUBAGENT_MODEL` verified **unset** pre-run. Evidence contract per v3.20.5 (`Tests: NOT RUN` line to B/C/D; per-file `run_audit.py` slice to D-security).
- **Scale:** 240 agents, 5,493,129 subagent tokens, ~37 min wall-clock total (sequential arms for per-arm accounting).

## Results

| Arm | recall μ (N=3) | var | pooled | FP/file | FP on controls (Σ6 reviews) | bikeshed % | tokens | wall-clock |
|---|---|---|---|---|---|---|---|---|
| **A** plain exhaustive (opus) | **0.931** | 0.0004 | 0.958 | 7.37 | 44 | 13.0% | 690,818 | 3.3 min |
| **B** vdd-adversarial 1.4 | 0.861 | 0.0004 | 0.917 | **6.20** | 39 | **3.9%** | 750,369 | 3.9 min |
| **C** vdd-sarcastic 1.4 | 0.903 | 0.0027 | 0.958 | **5.03** | **35** | 7.0% | 818,433 | 3.0 min |
| **D** /vdd-multi --no-fix (3×opus) | **0.986** | 0.0004 | **1.000** | 9.63 | 47 | 6.9% | 2,243,187 (3.25×A) | 15.9 min |
| **E** fable, arm-A prompt | 0.917 | **0.0000** | 0.917 | 10.33 | 58 | 19.5% | 990,322 | 10.8 min |

Per-run recalls: A .917/.917/.958 · B .875/.833/.875 · C .917/.833/.958 · D **1.0/.958/1.0** · E .917/.917/.917 (perfectly stable).
Missed bugs (pooled): A → f4-PER · B → f4-PER, f6-PER · C → f4-PER · D → **none** · E → f4-PER, f6-PER.
**Security class saturated:** every arm found 8/8 security and 8/8 CRITICAL — all differentiation lives in the performance class (f4-PER "unbounded L1 cache, no eviction" was caught **only** by arm D's dedicated perf critic).

## Pre-registered decision rules — verdicts (mechanical, `analysis.json`)

1. **Rule 1 — sarcasm: SURVIVES.** recall(C)−recall(B) = **+4.2pp** > pooled run variance (0.0015), and FP(C)=5.03 ≤ FP(B)=6.20. → Per pre-registration, **vdd-sarcastic (K2) is NOT deprecated** — item 5's final form resolves to: keep as opt-in stylistic skin with the existing no-evidence-base disclaimer.
2. **Rule 2 — multi-critic: FAILS.** recall(D)−recall(best single = A) = **+5.6pp < +10pp**, and FP(D)=9.63 > FP(A)=7.37 (both conditions fail) at **3.25×** token cost. → Per pre-registration: **default to a single strong reviewer; keep `/vdd-multi` for latency-critical CI** (it is the only arm that found all 24 bugs and the only one to catch f4-PER, but it does not clear its pre-registered cost bar).
3. **Rule 3 — forced negativity / adversarial framing: FAILS.** recall(B)−recall(A) = **−6.9pp** (FP condition passed, recall condition decisively failed). The adversarial scaffolding *costs recall* and *buys precision*: FP −16%, bikeshedding 3.9% vs 13.0%. Empirically confirms audit-067 C-01 (tone/persona is not a recall lever — here it is a recall **tax**).

## Honest nuances (outside the pre-registered gates)

- Full ordering on recall: **D > A > E > C > B**. Rule 1 only compares C vs B; both adversarial skins sit **below the plain exhaustive baseline**. "Sarcasm survives" means "sarcasm beats neutral-adversarial", not "use sarcasm for recall".
- Arm E (fable) was the most stable (zero variance) but noisiest (FP 10.33/file, 19.5% bikeshedding) and 3.2× slower than opus-A — on this corpus the bigger model did **not** out-recall opus given the same prompt.
- Scanner attribution: 4/8 security bugs appeared in D-security's evidence slice, but **every arm — including no-scan singles — found all 8 security bugs anyway**; D's edge came from the perf critic, not the scan injection.
- FP floor on *clean* controls: ~6–10 findings per clean-file review across all arms — "FP" here means "not in ground truth", not necessarily "wrong" (reviewers flag real-but-unseeded improvements). This floor is the empirical argument for the framework's bikeshedding filter and severity gates.

## Limitations (declared pre-run, TASK 075 §4)

(a) per-arm token totals are exact (harness usage counters), per-run splits are not; (b) bug author = same model family as reviewers (CriticGPT-style seeded-bug methodology, arXiv:2407.00215; sealed GT, reviewers saw only the file); (c) arm-D Phase-2 merge implemented deterministically in the scorer (rules 1/4; rule 3 tag-only — affects no recall/FP materially); (d) N=3 → low power; rules use pooled run variance per pre-registration, not significance tests; (e) corpus security bugs skew classic/pattern-shaped — security saturation limits what this corpus can say about security-review deltas.

## Consequences for the roadmap

| Item | Outcome |
|---|---|
| **5 (K2 keep-vs-deprecate)** | **RESOLVED — KEEP** as opt-in skin (rule 1). No further action; disclaimers already in place since 071. |
| **7/R3c** | Same-model multi fails its cost bar (rule 2) → R3c's model-heterogeneity is the **remaining lever** that could re-earn multi-critic escalation/cost; tier-diverse pilot (fable/opus/sonnet critics) is the natural follow-up experiment. |
| **vdd-multi positioning** | Recommendation (operator decision, separate `/framework-upgrade` cycle): document "default = single strong reviewer (plain exhaustive prompt); `/vdd-multi` for CI `--fail-on` gates and when class-complete coverage matters (only arm at 100% pooled)". |
| **K1 (vdd-adversarial)** | Value proposition shifts: **precision tool, not recall tool** (lowest bikeshedding 3.9%, FP −16% vs plain; recall −6.9pp). Candidate doc note for the skill, same follow-up cycle. |

**Publishable:** as of 2026-06-10 no comparable pre-registered study of adversarial-persona / multi-critic LLM code review exists (audit-067 finding); this run is small-N but fully sealed, scripted, and reproducible from `tests/fixtures/ab-corpus/`.

## Verdict

Experiment executed per pre-registration, 240/240 runs returned, zero malformed results, gates of TASK 075 met (seal-before-run ✓, frozen scorer ✓, mechanical rules ✓). Framework changes implied by rules 2/3 are **recommendations pending operator review** — nothing in `.agent/` / `System/` was modified by this task.
