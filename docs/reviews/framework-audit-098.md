# Framework Audit: ARC-3…ARC-12 archiving identity batch

**Date:** 2026-08-04
**Auditor:** Self-Improvement Verificator
**Target:** `docs/TASK.md` (Mode A — SPECIFICATION AUDIT)
**Status:** **APPROVED** (round 2)

## 0. Emergency Bypass
- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

No bypass claimed.

## 1. Compliance Checklist — round 1

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | Pass | Task ID `098`, slug `arc-batch-archiving-identity-integrity`, allocated by `task_id_tool.py` (`status: generated`). |
| **Tier Protection** | Pass | No TIER 0 skill is edited. `core-principles`, `skill-safe-commands`, `artifact-management`, `skill-session-state` untouched. |
| **Documentation** | **Fail** | R1–R8 name no update to `System/Docs/`. Two statements there go stale. |
| **Atomicity** | Pass | Eight requirements, each mapped to named issue IDs and to acceptance criteria A1–A16. |
| **Rollback Plan** | Pass | Deferred to PLAN.md per the workflow; §3.1 of `/framework-upgrade` owns the backup step. |

### Round 1 finding — F1 (Documentation)

`System/Docs/ORCHESTRATOR.md:8` instructs the reader to run the tool with `--no-correction`. R1 makes
that value the default, so the instruction survives but stops describing the shortest correct
invocation. `System/Docs/ORCHESTRATOR.md:284` states `39 tests`, and R8 adds tests to that file.

Required action: add a requirement covering `System/Docs/ORCHESTRATOR.md` and the CHANGELOG pair.

## 2. Compliance Checklist — round 2

TASK.md was redrafted per `/framework-upgrade` §1.3 (GOTO §1.2). R9 and A17–A18 were added.

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | Pass | Unchanged. |
| **Tier Protection** | Pass | Unchanged. |
| **Documentation** | Pass | R9 names `ORCHESTRATOR.md:8`, `:284`, and both CHANGELOG files. A17–A18 verify them. |
| **Atomicity** | Pass | Nine requirements. |
| **Rollback Plan** | Pass | Unchanged. |

## 3. Risk Analysis

- **Risk R1 — a caller relies on the old `allow_correction=True` default.** Condition: a call site
  omits the keyword and expects renumbering → the call returns `conflict` after R1. Detected by:
  `python3 -m pytest .agent/tools/ -q`. Measured before drafting: three production call sites pass
  the argument explicitly (`tool_runner.py:292`, `archive_protocol.py:256`, `task_id_tool.py:298`).
  One test relies on the default (`test_task_id_tool.py:152`) and is named in the PLAN.

- **Risk R2 — the new STOP path in `archive_task` blocks a legitimate archive.** Condition: a meta
  block with no ID row is misread as a refusal → a new task cannot archive. Detected by: A7.
  Mitigated by D4 — refusal is reported as a distinct reason, not inferred from `task_id is None`.

- **Risk R3 — `--slot-must-exist` breaks the Step 5.5 forward reference.** Condition: the flag is
  passed at Step 5.5, where the plan archive does not exist yet → the protocol's own happy path
  exits 1. Detected by: A10. Mitigated by R6 — only Step 7.6.5 passes the flag.

- **Risk R4 — the ledger flip and the code fix diverge.** Condition: an issue file flips to `fixed`
  while its defect survives → the ledger misreports. Detected by: A16 plus the per-issue mapping in
  the PLAN's closing step.

## 4. Verdict & Actions

**APPROVED** (round 2 of a maximum of 3).

**Actions carried into Planning:**
1. PLAN.md must name the backup set (`/framework-upgrade` §3.1) — the edited files are Python
   modules and skills, not only bootstrap docs.
2. PLAN.md must sequence R1 after the `test_task_id_tool.py:152` amendment, or the suite goes red on
   an expected change rather than on a regression.
3. PLAN.md must run the ledger flip as the final step, after A14 passes.

---

# Mode B — PLAN AUDIT

**Target:** `docs/PLAN.md`
**Status:** **APPROVED** (round 1)

## 5. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | Pass | Seven gates. Gate 1, 2 and 2b run `pytest`; gates 3–5 run `grep` against named lines; gate 6 runs the register scanner; gate 7 reads `git status`. |
| **Rollback** | Pass | §0.1 backs up ten edited files plus three bootstrap files into gitignored `.agent/archive/`. §0.2 names `git checkout 5c9da31 -- <path>` as the second route. |
| **Atomic Updates** | Pass | Five stages, 22 numbered steps, each carrying an `[R<ID>]` prefix mapped 1:1 to the RTM. |
| **Test Coverage** | Pass | Stage 1 writes three new test classes before any fix and amends one existing test. Ordering constraint 1 forbids the reverse order. |

## 6. Plan-specific observations

- **The three actions from Mode A are discharged.** Action 1 → §0.1. Action 2 → step 1.4 plus
  ordering constraint 2. Action 3 → Stage 5 plus ordering constraint 3.
- **Gate 2b is a mutation check, not a self-assessment.** It reverts `tool_runner.py:292` and
  requires the four-surface test to turn red. That is the measurement ARC-9 showed was missing.
- **Baseline is recorded before the first edit.** §0.3 pins 110 passing tests and the three
  reachable exit codes, so every later claim is a delta rather than an assertion.

## 7. Verdict

**APPROVED.** Execution may enter `/framework-upgrade` §3.
