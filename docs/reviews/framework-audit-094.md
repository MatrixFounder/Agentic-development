# Framework Audit: one ledger write path + the iteration-3 residue (TASK 094)

**Date:** 2026-07-30
**Auditor:** Self-Improvement Verificator (Mode A + Mode B)
**Target:** `docs/TASK.md` **and** `docs/PLAN.md` for TASK 094
**Status:** **BLOCKED → APPROVED** — two required changes applied before Step 1 (§3 disposition). Ran **before** execution.

## 0. Emergency Bypass
- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

**Justification:** none — no flag set. No TIER 0 skill is touched, no bootstrap file changes, and
`known-issues-format` is deliberately untouched (no contract change), so §4's "GEMINI.md without
System/Docs" blocker does not apply.

## 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | TASK ID `094`, slug `ledger-core-and-residue`, allocated via `task_id_tool.py`. No live TASK/PLAN on disk (093's were archived), so nothing to rotate — checked, not assumed. |
| **Tier Protection** | ✅ Pass | One TIER 2 skill (`run-feedback`). `core-principles`, `skill-safe-commands`, `artifact-management`, `skill-session-state` untouched. |
| **Skill Compatibility** | ✅ Pass | No new agent, prompt or workflow. `known-issues-format` unchanged by design — the strongest available signal that this is a refactor and not a contract change, since `check_contract_sync.py` must stay green with **no edits**. |
| **Documentation** | ✅ Pass | SKILL.md (the guard inventory and the two new refusals), CHANGELOG EN+RU, WI-8/WI-9 resolutions. `System/Docs/QUALITY_FEEDBACK_LOOP.md` needs no edit: the subsystem's described behaviour does not change, only where the code lives. |
| **Migration** | ✅ Pass | `config.v` stays `1`. No new config key. R2 freezes the public signatures **and result-dict keys**, so there is nothing for a consumer to migrate to. |
| **Verification Step** | ✅ Pass | Step 0 establishes the baseline before any edit, Step 8 re-runs the exploit probes by hand and mutation-sweeps the moved guards. |
| **Rollback** | ✅ Pass | Clean tree at `d2053e6`; per-path checkout or task-wide reset. |
| **Atomic Updates** | ✅ Pass | 10 steps; the extraction (1) is isolated from every behaviour change (3–7), which is what makes a bisect meaningful. |
| **Test Coverage** | ✅ Pass | The strongest part of this plan: **Step 0 forbids editing the 286 existing tests during the refactor.** A refactor whose tests change with it proves nothing, and this plan says so and enforces it with an ordering constraint rather than a good intention. |
| **Root Integrity** | ✅ Pass | Stub-First does not apply (no new production surface); the applicable discipline — RED-before-GREEN per guard — is carried over from audit 093 and inverted correctly for the refactor steps. |

## 2. Risk Analysis

- **Risk 1 — this is the largest single change to this skill, on code consumed by symlink in three
  repos.** Two registries, both live, no merge step. *Mitigation:* R2's frozen signatures and result
  keys mean the blast radius is confined to two function bodies; the 286-test baseline is a genuine
  net precisely because it is not allowed to change; and Step 1's `grep -c "O_EXCL" == 1` is a
  mechanical proof of the extraction rather than a reviewer's impression.
- **Risk 2 — a refactor can preserve every test and still lose a guard the tests never covered.**
  This is the real hazard: iteration 3 found guards that existed but were *untested on one path*.
  Moving such a guard into the core makes it universal, but moving it *wrongly* would silently drop
  it on both. *Mitigation:* Step 2's parameterized guard **inventory** is the right instrument, and
  Step 8's mutation sweep is what proves it bites. **Required Action 1** strengthens it.
- **Risk 3 — R2's frozen result keys preserve a genuinely bad interface.** `issue_id`/`item_id`,
  `issue_path`/`record_path`, `index_path`/`backlog_path`, `seeded_index`/`seeded_backlog` are four
  gratuitous synonyms, and freezing them means the core carries a translation layer forever.
  *Assessment:* correct call anyway. Renaming is a separate change with its own callers, and doing it
  inside the refactor would destroy the one property that makes the refactor reviewable. Recorded so
  the translation layer reads as deliberate debt rather than confusion.
- **Risk 4 — the deliberate ordering change (TASK §4) alters which error a user sees.** Two
  invalid inputs at once now report the earlier one. *Mitigation:* stated in the spec rather than
  discovered; nothing is written in either order, so the zero-writes invariant is untouched. Any test
  that asserts a *specific* error for a doubly-invalid input will fail loudly and correctly.
- **Risk 5 — R12 (`feedback_dir` forbidden roots) can break the documented default.** `.agent/feedback`
  is *inside* `.agent`, which is a forbidden root. That is exactly why `ledger=False` exists. A naive
  "apply the guard" breaks every consumer immediately. *Mitigation:* the plan already says "a narrower
  exemption, not removing the guard" — **Required Action 2** makes the acceptance criterion explicit.
- **Risk 6 — R15 (dropping `fsync` for inbox writes) trades durability for latency.** A crash between
  write and `os.replace` can now lose a queued finding. *Assessment:* acceptable and correctly argued —
  inbox state is regenerable machine state under a gitignored dir, and the barrier sat inside the
  collect flock, serializing concurrent captures. The ledgers, which are the durable artifact, keep it.
  The acceptance test must assert the **asymmetry**, not just the absence.
- **Risk 7 — R10 (refusing duplicate frontmatter keys) tightens a READER on live hand-edited files.**
  The module's stated read discipline is tolerant. A duplicate key in a real ledger would now raise
  where it previously resolved. *Mitigation:* this is the "a human reads one value, a tool reads the
  other" primitive, so refusing is right — but it must fail as a `CliError`, never a traceback, and
  `list_issues` must keep skipping unparseable records rather than aborting a scan.
- **Risk 8 — scope.** 20 requirements across a refactor and 16 fixes is a lot for one task. *Mitigation:*
  the ordering isolates them (Steps 1–2 behaviour-preserving, 3–7 behaviour-changing), and WI-8's items
  are individually tiny. Splitting into two tasks would mean doing the choreography edits twice, which
  is the thing being fixed.

## 3. Verdict & Actions

**BLOCKED** on two points, both additions to the plan's own acceptance criteria. The plan is otherwise
the best-specified one in this series — Step 0 in particular is the control that was missing from 093.

**Required actions:**
1. **The guard inventory must assert per-registry, not just "some registry".** Step 2 as written could
   pass with a guard that fires for one registry and a coincidental failure for the other. Require the
   inventory to record *which* registry each guard fired for, and Step 8's mutation sweep to confirm
   **both** entries flip. Without this, Risk 2 — the hazard this whole task exists to close — is
   unpinned by the very test meant to pin it.
2. **State R12's acceptance criterion as a pair:** `.agent/feedback` (the documented default) must
   still load, **and** `.git/...` must be refused. One assertion without the other either breaks every
   consumer or changes nothing (Risk 5).

**Carried into execution as standing constraints:**
3. Do not edit an existing test during Steps 1–3 (the plan says this; the audit makes it a gate).
4. Freeze the tree while any critic runs against it — iteration 3's process failure, not to be repeated.
5. R7/R10's tightenings must raise `CliError`, never a traceback, and must not make a tolerant scan abort.
6. Any WI-8 row not implemented is named in the resolution with its reason. sec-L-10 is already known.

**Disposition — both applied before Step 1 began:**
1. `docs/PLAN.md` Step 2 and Step 8 now require the inventory to record the registry per guard and the
   mutation sweep to confirm both entries flip.
2. Step 6's R12 line now names both halves of the acceptance criterion.

**APPROVED for execution.**
