# Technical Specification: Pre-registered A/B — Sarcasm & Multi-Critic Effectiveness (C-12, roadmap item 13)

### 0. Meta Information
- **Task ID:** 075
- **Slug:** `ab-experiment-sarcasm-multicritic`
- **Mode:** Experiment (🧪 — produces corpus fixtures + analysis script + report; **modifies no framework component**; framework edits, if any, follow as separate cycles driven by the decision rules)
- **Type:** P2-experiment, roadmap item **13** [C-12]. Protocol authority: audit-067 **Appendix A** — pre-registered, **do not redesign**.
- **Source:** User request (2026-06-10): "сделай item 13" (after explicit cost warning: ~240 agent runs — informed consent). Arm-D handicap removed by item 11 (Task 074) — pipeline measured at design intent.

## 1. Protocol (verbatim constraints from Appendix A)

- **Corpus:** 24 seeded bugs in 8 realistic files (~150–400 LoC): 8 logic / 8 security / 8 performance; severity-stratified 8 CRITICAL / 8 HIGH / 8 MEDIUM; + 2 clean controls (FP floor). Ground truth sealed in `tests/fixtures/ab-corpus/ground_truth.json` **before any arm runs** (sha256 seal manifest).
- **Arms** (same model+version for A–D = `opus` (matches critic wrapper pins), fresh context per run, N=3 runs/arm/file):
  - **A** plain baseline ("review thoroughly; report every issue incl. low-confidence, with confidence+severity; structured output", no persona)
  - **B** `vdd-adversarial` (neutral adversarial)
  - **C** `vdd-sarcastic` (full Sarcasmotron)
  - **D** `/vdd-multi --no-fix` (3 parallel opus critics + Phase-2 merge; evidence contract per v3.20.5)
  - **E** single `fable` reviewer with arm-A prompt (cost-matched "one strong reviewer")
- **Metrics:** seeded-bug recall (by class & severity); FP per file (controls + unmatched non-style findings); bikeshedding ratio; tokens (proxy, see limitations); wall-clock per arm.
- **Decision rules (fixed):** (1) sarcasm survives iff recall(C)−recall(B) > pooled run variance AND FP(C) ≤ FP(B), else deprecate K2; (2) multi survives iff recall(D)−recall(max(A,E)) ≥ +10pp at equal-or-lower FP, else single-strong-reviewer default; (3) B vs A judged as rule 1.

## 2. RTM

| ID | Requirement | Verification |
|----|-------------|--------------|
| R1 | Corpus: 8 seeded + 2 control files, 24 bugs per stratification; `ground_truth.json` (file, line, class, severity, description) + `seal.json` (sha256 of corpus+GT) created **before** runs | seal timestamps in report; line numbers grep-derived, not hand-counted |
| R2 | Scanner floor recorded: `run_audit.py` on corpus → `scan_floor.json` (attribution: which D-findings are scanner-derivable); scan summary injected into critic-security prompts per v3.20.5 contract | file exists pre-run |
| R3 | Runs: 5 arms × 10 files × 3 runs; arms A–C/E = single reviewer (A/B/C model=opus, E=fable), D = critic-{logic,security,performance} wrappers + deterministic Phase-2 merge (rules 1,2,4,5 in script; rule 3 = corroborated/no-escalation, cross-mechanism kept); per-run findings persisted as JSON under `results/<arm>/` | result-file count = 120 single + 30×3 critic |
| R4 | Evidence lines: B/C/D receive `Tests: NOT RUN (fixture corpus — no test suite)`; D-security additionally scan summary; A/E prompts stay verbatim-minimal per protocol | prompts in workflow scripts |
| R5 | `analyze.py` (~100 lines): matching = same file + \|Δline\|≤3 + class match; per-run recall mean±variance, pooled-union secondary; FP/file; bikeshedding ratio; decision rules 1–3 evaluated mechanically | script output in report |
| R6 | Report `docs/reviews/ab-experiment-075.md`: metrics tables, decision-rule verdicts, limitations (token proxy; same-model-family bug seeding; deterministic merge), consequences for items 5 (K2) and 7/R3c; roadmap item 13 status update; session-state | file read |

## 3. Out of Scope
Applying the decisions (deprecating K2, changing /vdd-multi defaults) — separate `/framework-upgrade` cycles after operator reviews the report. No framework files touched in this task.

## 4. Known limitations (declared pre-run)
(a) Token metric is a proxy (per-arm output-volume + agent counts; harness does not expose per-subagent token usage); (b) bug author = same model family as reviewers (CriticGPT-style seeded-bug methodology, arXiv:2407.00215; mitigations: sealed GT, reviewers see only the file); (c) D's Phase-2 merge implemented deterministically in the scorer (affects FP counting only marginally; recall uses post-dedup union either way); (d) N=3 → low statistical power; decision rules pre-registered to use pooled run variance, not significance tests.
