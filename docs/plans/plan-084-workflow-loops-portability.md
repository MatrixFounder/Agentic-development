# Development Plan: Task 084 — Workflow loop hardening & portability (`full-robust`, `vdd-enhanced`)

> Mode B gates. **Architecture untouched** (workflow prose only — no system-structure change).
> Release v3.20.13. No archiving of living docs, no code change, no skill change.
> Scope fixed by operator: `.agent/workflows/full-robust.md`, `.agent/workflows/vdd-enhanced.md`
> (+ registry/CHANGELOG sync per R6).

## Step 0 — Backup (rollback safety)
```
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done   # framework-upgrade §3.1 mandate (untouched but backed up)
cp .agent/workflows/full-robust.md   .agent/archive/full-robust.md.bak
cp .agent/workflows/vdd-enhanced.md  .agent/archive/vdd-enhanced.md.bak
cp System/Docs/WORKFLOWS.md          .agent/archive/WORKFLOWS.md.bak
cp CHANGELOG.md CHANGELOG.ru.md README.md README.ru.md .agent/archive/   # version-bump set
```

## Step 1 — [R1,R2,R3] Rewrite `full-robust.md` as a gated pipeline
Atomic edit of one file. Content contract:
- **Loop protocol note** (top): gates are deterministic (script exit codes / structured
  verdicts) ⇒ any LLM can drive them; feed gate errors verbatim into retries; persist state
  via `update_state.py` at every phase boundary (global protocol reminder).
- **Step 1**: Execute `.agent/workflows/vdd-enhanced.md` (Claude Code alias `/vdd`) with
  `tdd-strict` context. **Gate:** completed without escalation; if it escalated to the user,
  this pipeline is already stopped — do not proceed. [F1]
- **Step 2 (opt-in)**: `/vdd-multi --no-fix --fail-on=high` coverage gate, marked optional
  with the ab-experiment-075 rationale (coverage/CI tool, not default). **Gate:** verdict
  PASS; on FAIL → fix via `.agent/workflows/03-develop-single-task.md`, re-run **once**;
  still FAIL → STOP, escalate. [F6]
- **Step 3**: Execute `.agent/workflows/security-audit.md` (alias `/security-audit`).
  **Gate:** scan + manual review clean of CRITICAL/HIGH. **Bounded remediation:** max 3
  fix→re-scan iterations (the sub-workflow's own "re-run until clean" is unbounded — the
  bound lives here at the caller); on exhaustion → STOP, escalate with open findings. [F1]
- **Step 4**: Execute `.agent/workflows/04-update-docs.md` (alias `/update-docs`) — replaces
  the vague "Final documentation update"; remove "(future) Security audit" staleness. [F2]
- **`## Vendor dispatch & model portability`** section: invocation = read the workflow file
  (slash commands are Claude-Code aliases); role/subagent calls resolve per
  `skill-parallel-orchestration` §1.1 (native adapter) / §7 (sequential last resort); no
  duplicated vendor tables. [F3, F4, F5]
- **Completion line** stating the pipeline's terminal verdict.

## Step 2 — [R4,R5] Complete the loops in `vdd-enhanced.md`
Atomic edit of one file. Content contract:
- **Loop protocol note** (top): same three-point note as Step 1 (deterministic gates ⇒
  model-agnostic; error feedback; phase-boundary checkpoints). [F11, F12]
- **Phase 1**: portable reference `.agent/workflows/01-start-feature.md` (alias
  `/start-feature`); role call = "Analyst role (`System/Agents/02_analyst_prompt.md`) —
  subagent on Claude Code, role-switch otherwise". Loop semantics unchanged (already
  canonical). [F10]
- **Phase 2**: portable reference `.agent/workflows/02-plan-implementation.md` (alias
  `/plan`); add missing **Escalation** clause (parity with Phase 1: after 3 failed retries →
  STOP, ask user). [F7, F10]
- **Phase 3**: portable reference `.agent/workflows/05-run-full-task.md` (alias
  `/develop-all`); add caller-side **Gate**: full regression suite passes; IF FAIL → re-enter
  `.agent/workflows/03-develop-single-task.md` for the failing task (max 2 attempts) →
  still failing → STOP, ask user. [F8]
- **Phase 4**: portable reference `.agent/workflows/vdd-adversarial.md` (alias
  `/vdd-adversarial`); add **outer cap**: max 3 adversarial cycles; termination bar =
  objective convergence (0 CRITICAL, only bikeshedding left — per `vdd-adversarial` skill);
  cap hit without convergence → STOP, report remaining findings. [F9]
- **`## Vendor dispatch & model portability`** section (same shape as Step 1). [F11]

## Step 3 — [R6a] `System/Docs/WORKFLOWS.md` row sync
- Check rows 146–147 (Full Robust / VDD Enhanced): update descriptions to mention bounded
  gated loops + vendor dispatch if wording drifted; keep `run full-robust` / `run
  vdd-enhanced` triggers unchanged (no new workflow ⇒ no new trigger).

## Step 4 — [R6b] CHANGELOG + version bump
- CHANGELOG EN+RU **v3.20.13**: the two pipelines gained explicit bounded loops
  (gate/retry/escalation), portable invocation references, and vendor-dispatch sections;
  no behavior of other workflows changed.
- README.md / README.ru.md header `v3.20.12` → `v3.20.13` (×2).

## Step 5 — [R7, R6c] Verification gates
1. **Grep acceptance** (AC1–AC5):
   - `grep -n "future" .agent/workflows/full-robust.md` → none;
   - `grep -n "01-start-feature\|02-plan-implementation\|05-run-full-task" .agent/workflows/vdd-enhanced.md`
     → every hit is a `.agent/workflows/…` file path;
   - `grep -n "Escalation" .agent/workflows/vdd-enhanced.md` → present in Phases 1 AND 2;
   - `grep -n "Vendor dispatch" .agent/workflows/*.md` → both target files listed;
   - no reference to a non-existent slash command:
     `grep -nE '\`/(vdd-enhanced|01-start-feature|02-plan-implementation|05-run-full-task)\`' <the two target files>`
     → none (note: three OTHER workflows — `base-stub-first.md`, `light-01/02-*` — still carry
     the pattern; pre-existing, recorded as follow-up, out of 084 scope);
   - `grep -c "Gate:" .agent/workflows/full-robust.md` → 4 (one per step, AC1);
     `grep -cE "Validate|Self-Correction|Gate \(caller-side\)|Termination bar|Outer cap" .agent/workflows/vdd-enhanced.md`
     → ≥4 (every phase gated, AC1);
   - `grep -n "max 3 iterations\|max 2 fix-and-rerun\|max 3 adversarial\|Max 3 retries" .agent/workflows/full-robust.md .agent/workflows/vdd-enhanced.md`
     → all loop bounds present (AC1, AC5b/c).
2. **Regression**: `validate_skill.py` sweep over `.agent/skills/` (expect 43/43 — no skill
   touched); root `python3 -m pytest tests/ -q`; `cd .agent/tools && python3 -m pytest -q`;
   `python3 -m pytest .agent/skills/security-audit/tests/ -q`.
3. **Review pipeline** (Self-Improvement Mode mandate): spawn `code-reviewer` on the diff of
   the two workflow files; security check of added shell snippets (static, no interpolation
   of untrusted input — confirm by inspection; run_audit.py not applicable to prose).
4. **Diff confinement**: `git status --porcelain` touches only: 2 workflow files,
   WORKFLOWS.md, CHANGELOG×2, README×2, docs/TASK.md, docs/PLAN.md,
   docs/reviews/framework-audit-084.md, session state, archived 083 pair (renames),
   `.agent/archive/` backups created by Steps 0 and 7, and the R8 scope-expansion files
   (`.agent/workflows/05-run-full-task.md`, `tests/test_product_scripts.py`,
   `tests/test_product_skills.py`).

## Step 6 — Finalization
- Append Mode B verdict + execution-verify section to `docs/reviews/framework-audit-084.md`.
- `update_state.py` at each phase boundary (Planning done → Execution → Completion).
- Report to operator (RU): findings F1–F12, what changed per file, gates, follow-up
  recommendation (`05-run-full-task.md` Finalization lacks an If-Fail branch — out of scope).

## Step 7 — [R8] Scope expansion (operator, mid-execution): fix the marked follow-ups
Backups first (`.agent/archive/05-run-full-task.md.bak`, `test_product_scripts.py.bak`,
`test_product_skills.py.bak`).
- **7.1 [R8a]** `tests/test_product_scripts.py`: replace the stale
  `sys.path.append(../System/scripts)` + top-level imports (scripts moved into skills long
  ago → collection `ImportError`) with the repo's `load_module_from_path` pattern pointing at
  `.agent/skills/skill-product-analysis/scripts/init_product.py` and
  `.agent/skills/skill-product-backlog-prioritization/scripts/calculate_wsjf.py`.
- **7.2 [R8b]** `tests/test_product_skills.py::test_wsjf_calculation_logic`: the script is
  SOT (`main()` passes `(line, cells)` pairs); drop the stale leading row-index from the
  test fixture.
- **7.3 [R8c]** `.agent/workflows/05-run-full-task.md` Finalization: add the If-Fail gate
  (re-enter `03-develop-single-task`, max 2, re-run suite, escalate on exhaustion; never
  commit on red) — consistent with the caller-side gate added to `vdd-enhanced.md` Phase 3.
  Sync the "Run Full Task" row in `System/Docs/WORKFLOWS.md`.
- **Gate**: full root suite green (`python3 -m pytest tests/ -q`); CHANGELOG v3.20.13
  extended (EN+RU) to cover R8.

## Step 8 — [R9] Scope expansion 2 (operator: "почини их"): second-round follow-ups
Backups first (`.agent/archive/`: `base-stub-first.md`, `light-01-start-feature.md`,
`light-02-develop-task.md`, `test_mock_agent.py`, `calculate_wsjf.py`).
- **8.1 [R9a]** Phantom slash-commands → `Execute \`.agent/workflows/…\` (alias: …)` form in
  `base-stub-first.md` (3 refs), `light-01-start-feature.md` (standard-pipeline escalation
  ref + the nonexistent `/light-02-develop-task` self-transition), `light-02-develop-task.md`
  (escalation ref).
- **8.2 [R9b]** `tests/test_mock_agent.py`: output to pytest `tmp_path` (spawn script does
  its own `os.makedirs`); assert-based checks; `__main__` path uses `TemporaryDirectory`;
  `git rm docs/tasks/mock_results/` (test junk, recoverable from history; referenced nowhere
  live — only the historical POC archive doc).
- **8.3 [R9c]** `calculate_wsjf.calculate_wsjf` docstring: document `(line, cells)` input,
  dict-list return, exit-1 on bad critical column.
- **Gate**: affected tests green; full suite green; `git status` clean of `docs/tasks/`
  side-effects after a test run; CHANGELOG v3.20.13 extended (EN+RU) to cover R9.

## Step 9 — [R10] Scope expansion 3 (operator: "это тоже исправь"): bound the light-mode loops
Fixes the audit §5 observation (same defect class as F1/F8/F9, in light mode). Rollback via
git (R9 backup of `light-02-develop-task.md` in `.agent/archive/` predates R9's own edit;
git HEAD holds the original).
- **9.1 [R10a]** `light-02-develop-task.md` Step 1.5: test-fix loop bounded at **max 3
  fix-and-rerun attempts** → STOP + Escalation section.
- **9.2 [R10b]** Step 2.4: review loop bounded at **max 2 review cycles** → STOP +
  Escalation section.
- **9.3 [R10c]** Escalation trigger extended: "…or a loop bound above is exhausted".
- **9.4 [R10d]** WORKFLOWS.md Light Mode row: bounds + escalation mentioned.
- **Gate**: grep both bounds present in `light-02-develop-task.md`; no unbounded "(loop)"
  wording remains; suites stay green (no code touched).

## Test Coverage Note (Mode B item 4)
No new executable logic (markdown workflow prose only) → no new unit tests. Regression =
full existing gate set (Step 5.2); acceptance is grep-verifiable (Step 5.1); human-logic
review via code-reviewer (Step 5.3).

## Rollback
Step 0 `.bak` set + git (clean tree at start). New files: `docs/reviews/framework-audit-084.md`,
new TASK/PLAN (removable). Restore per `framework-upgrade` §5 Fallback loop.
