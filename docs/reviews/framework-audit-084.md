# Framework Audit: Workflow loop hardening & portability (`full-robust`, `vdd-enhanced`)

**Date:** 2026-07-07
**Auditor:** Self-Improvement Verificator
**Target:** `docs/TASK.md` (Mode A) — Mode B section appended below after planning.
**Status:** **APPROVED**

## 0. Emergency Bypass
- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

**Justification:**
> None set. No bypass needed: no Tier-0 skill, bootstrap file, or agent prompt is touched.

## Mode A — SPECIFICATION AUDIT (docs/TASK.md, task 084)

### 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | [x] Pass | ID `084`, slug `workflow-loops-portability`, Mode/Type/Workflow declared. |
| **Root Integrity** | [x] Pass | Atomicity: each finding F1–F12 maps to exactly one RTM sub-feature; traceability F→R→AC closed. Stub-First n/a (doc-only), structure-first honored (audit → RTM → edits). |
| **Tier Protection** | [x] Pass | No Tier-0 skill modified or de-referenced. Workflows keep pointing at SOT skills (`skill-parallel-orchestration`, `skill-spec-validator`) instead of duplicating them — anti-drift preserved. |
| **Skill Compatibility** | [x] Pass | No new agents/prompts introduced; no TIER-0 loading contract changed. R2b/R5b explicitly forbid duplicating vendor tables (SOT: `skill-parallel-orchestration` §1/§7). |
| **Documentation** | [x] Pass | R6 covers `System/Docs/WORKFLOWS.md`, CHANGELOG (EN+RU), and this audit artifact. |
| **Migration** | [x] Pass | §7: workflows are read fresh per invocation; no session-format or wrapper-manifest impact (no SOT path renamed → KNOWN_ISSUES drift-grep not triggered). |

### 2. Blocking-Condition Scan (skill §4)
- Removing `core-principles` / `skill-safe-commands` from any agent → **not present**.
- Modifying `GEMINI.md` without System/Docs update → **GEMINI.md untouched** (R7b).
- New workflow without trigger → **no new workflow created**; both files already have
  triggers (`/full`, `/vdd` in `.claude/commands/`; `run full-robust` / `run vdd-enhanced`
  in `System/Docs/WORKFLOWS.md`).

### 3. Risk Analysis
- **Risk 1 — Behavior drift for existing callers:** `/full` and `/vdd` gain explicit gates
  where behavior was previously undefined. Mitigation: gates codify the framework's existing
  canon (Stage Cycle bounds, objective convergence), they do not invent new policy; bounds
  chosen to match sibling workflows (max 2–3, escalate).
- **Risk 2 — Registry desync:** WORKFLOWS.md tables describe the two pipelines. Mitigation:
  R6a forces the row check in the same change.
- **Risk 3 — Cross-file contradiction:** adding an opt-in `/vdd-multi` step must not
  contradict its 075 positioning ("not the default review path"). Mitigation: R3 marks the
  step optional with the 075 rationale inline.

### 4. Verdict & Actions (Mode A)
**APPROVED** — proceed to Planning (Mode B audit required before execution).

---

## Mode B — PLAN AUDIT (docs/PLAN.md, task 084)

### 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | [x] Pass | Step 5.2: `validate_skill.py` sweep + three pytest suites (root `tests/`, `.agent/tools`, security-audit smoke). Step 5.1 greps mechanically cover AC1 (gate presence + loop bounds), AC2, AC3, AC4's "(future)" removal, and AC5; AC4's opt-in `/vdd-multi` step and AC6 are verified by inspection + the Step 5.3 review pass. |
| **Rollback** | [x] Pass | Step 0 backs up both target files, registry, CHANGELOG/README set, AND the bootstrap trio per `framework-upgrade` §3.1; restore loop = §5 Fallback. Git tree was clean at task start. |
| **Atomic Updates** | [x] Pass | One file per step; each step carries its RTM IDs and finding IDs ([R..]/[F..]). Steps 1 and 2 are independent; docs sync (3–4) follows content. |
| **Test Coverage** | [x] Pass | No new executable logic (workflow prose). Justified in "Test Coverage Note": regression gates + grep-verifiable acceptance + code-reviewer pass (Step 5.3) substitute for new unit tests. |

### 2. Risk Analysis (delta vs Mode A)
- **Caller-side bounds vs sub-workflow text:** Step 1 bounds security remediation (max 3)
  while `security-audit.md` itself says "re-run until clean". Not a contradiction — the
  caller's bound is stricter and the sub-workflow is unchanged; documented inline. Same
  pattern for Phase-3/Phase-4 caller-side gates in `vdd-enhanced.md`.
- **Alias accuracy:** every parenthetical alias verified against `.claude/commands/`
  (`/full`, `/vdd`, `/start-feature`, `/plan`, `/develop`, `/develop-all`,
  `/vdd-adversarial`, `/security-audit`, `/update-docs`, `/vdd-multi`).

### 3. Verdict & Actions (Mode B)
**APPROVED** — proceed to Execution (Step 0 backup first; no bypass flags in use).

---

## Execution Verification (post-implementation, 2026-07-08)

### 1. Scope expansion (operator-approved, R8)
Mid-execution the operator requested: *"fix follow ups that you've marked."* Three marked
follow-ups were fixed under R8 (TASK.md updated, PLAN.md Step 7):
- `tests/test_product_scripts.py` — stale `System/scripts` import → `load_module_from_path`
  (collection `ImportError` resolved; 5 tests now run).
- `tests/test_product_skills.py::test_wsjf_calculation_logic` — fixture aligned with
  `calculate_wsjf`'s actual `(line, cells)` contract.
- `.agent/workflows/05-run-full-task.md` — Finalization gained the missing If-Fail gate
  (max 2 fix-and-rerun, escalate, never commit on red) + WORKFLOWS.md row sync.

### 2. Review pipeline (Step 5.3) — multi-critic workflow `wf_517d83ab-2f3`
4 dimension critics (xref / loops / portability / docs-sync) + per-finding adversarial
verification; 21 agents, 17 raw findings → **12 confirmed** (5 refuted, xref clean).
All 12 confirmed findings **fixed**:
1. full-robust Step 3: exit condition re-scoped at caller ("clean" = no CRITICAL/HIGH;
   MEDIUM/LOW recorded, no extra iterations).
2. full-robust Step 4: gate + bounded retry + escalation added (AC1 now literally true).
3. full-robust Step 2 FAIL path: findings → persisted report + materialized fix-task file →
   `/develop` input defined.
4. Both files + WORKFLOWS.md rows: "deterministic / never model self-assessment /
   mechanical" overclaim reworded — script gates are deterministic; review gates are
   structured verdicts against written objective bars.
5. vdd-enhanced Phase 3: bound unit disambiguated ("max 2 fix-and-rerun rounds total").
6. WORKFLOWS.md mermaid: Robust edges now 1. VDDE → 2. opt-in VDDMulti → 3. SecAudit.
7. PLAN 5.1 greps made precise + PLAN 5.4 allowlist completed; this audit's alias list
   (+`/develop`) and Verification-Step wording corrected.

### 3. Final gates
- Grep acceptance (precise forms): PASS — 4 `Gate:` in full-robust (one per step); 7 gate
  constructs across vdd-enhanced phases; no phantom slash-commands in either target file.
- `validate_skill.py`: **43/43**. Pytest: root `tests/` **227 passed** (both pre-existing
  failures fixed under R8), `.agent/tools` **52 passed**, security-audit **30 passed**.
- Diff confinement: matches the (updated) PLAN 5.4 allowlist exactly.

### 4. Recorded follow-ups → FIXED under R9 (operator: "почини их", scope expansion 2)
- ~~Phantom slash-command references in `base-stub-first.md`, `light-01-start-feature.md`,
  `light-02-develop-task.md`~~ — all converted to the portable
  `.agent/workflows/*.md` + real-alias form; also fixed the transition to the nonexistent
  `/light-02-develop-task` command inside `light-01` (no `.claude/commands/` entry exists —
  it is the second half of `/light`).
- ~~`calculate_wsjf` docstring mismatch~~ — now documents the `(line, cells)` input pairs,
  the dict-list return, and the exit-1 behavior.
- ~~`tests/test_mock_agent.py` dirties the tree~~ — output moved to pytest `tmp_path`
  (`TemporaryDirectory` for the `__main__` path); asserts instead of `sys.exit`; the tracked
  test artifact `docs/tasks/mock_results/` was `git rm`-ed (referenced only by the
  historical POC archive doc; recoverable from git history).

### 5. ~~New observation~~ → FIXED under R10 (operator: "это тоже исправь", scope expansion 3)
`light-02-develop-task.md` Steps 1.5 and 2.4 were unbounded loops. Now: test-fix loop
bounded at **max 3 fix-and-rerun attempts**; review loop at **max 2 review cycles** (family
conventions: validator-retry max 3 / reviewer max 2); the Escalation trigger explicitly
covers bound exhaustion (repeated failures ⇒ task not trivial ⇒ standard pipeline).
WORKFLOWS.md Light Mode row synced.

### Final Verdict
**APPROVED — task 084 complete** (v3.20.13, incl. R8+R9+R10 scope expansions). No bypass
flags used. Restart not required (no bootstrap/prompt files changed).
