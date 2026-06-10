# Development Plan: Task 075 — A/B Experiment Execution (item 13, C-12)

> Protocol = audit-067 Appendix A (pre-registered). Mode A/B verificator gate: **light** — no framework component modified (new fixtures + script + report only); rollback = delete `tests/fixtures/ab-corpus/` + report (tree was git-clean at `e9a2360`).

## Step 0 — Corpus & seal (NO agent runs until sealed)
1. Author `tests/fixtures/ab-corpus/files/`: f1_auth_service.py … f8_config_loader.py (3 bugs each: 1 logic + 1 security + 1 perf) + c1/c2 controls. Totals: 8L/8S/8P, 8C/8H/8M.
2. Derive bug line numbers by grep (not hand-counting) → `ground_truth.json`.
3. `seal.json` = sha256 of every corpus file + ground_truth + UTC timestamp.
4. `run_audit.py files/ → scan_floor.json` + extract summary string for D-security prompts.
5. `analyze.py` written **before** runs (scoring rules frozen pre-data).

## Step 1 — Runs (5 sequential Workflow invocations, Bash `date` around each for wall-clock)
- Arm A: 30 agents (`claude` type, model=opus) — review one file each, write `results/A/<file>__r<k>.json`, return "done N".
- Arm B: same, prompt = read & apply `vdd-adversarial` SKILL (+ evidence line `Tests: NOT RUN`).
- Arm C: same, prompt = read & apply `vdd-sarcastic` (+`vdd-adversarial`) (+ evidence line).
- Arm D: per (file,run): 3 parallel critic agents (agentType critic-logic/security/performance, schema-validated findings) → writer agent persists 3 raw JSONs to `results/D/<file>__r<k>/`. 30 runs = 90 critics + 30 writers.
- Arm E: 30 agents, arm-A prompt, model=fable.
- Fresh context per run is inherent (each agent = new context). No cross-run information flow.

## Step 2 — Score & report
1. `python3 analyze.py` → metrics + decision rules 1–3.
2. Report `docs/reviews/ab-experiment-075.md` (tables, verdicts, limitations, consequences for items 5 / 7-R3c).
3. Roadmap item 13 → status per outcome; session-state final update. CHANGELOG: experiment is not a release — recorded in roadmap+report only (no version bump).

## Rollback / failure
| Failure | Action |
|---|---|
| Workflow dies mid-arm | Re-run that arm's workflow; result files are idempotent per (arm,file,run) — completed tuples skipped by filename check in prompts? (simpler: re-run overwrites; scorer reads what exists and reports completeness) |
| Corpus flaw found mid-run | STOP, fix corpus, re-seal with new hashes, **discard all prior runs** (pre-registration: no per-arm corpus drift) |
| Budget concern | Arms are independent — operator may stop between workflow invocations; partial-arm data excluded from decision rules |
