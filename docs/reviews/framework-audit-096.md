# Framework Audit: Artifact register formalization (TASK 096)

**Date:** 2026-08-03
**Auditor:** Self-Improvement Verificator (Mode A — Specification Audit)
**Target:** `docs/TASK.md`
**Status:** **BLOCKED** (round 1) → **APPROVED** (round 2, after the actions below were applied)

## 0. Emergency Bypass

- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

No bypass used.

## 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | Pass | ID 096, slug `artifact-register-formalization`, archive name present. |
| **Tier Protection** | Pass | No TIER 0 skill is edited. `core-principles` and `skill-safe-commands` untouched. |
| **Documentation** | Pass | R11 covers `SKILLS.md` and `CHANGELOG.md`. |
| **Atomicity** | Pass | 12 requirements, each independently verifiable. |
| **Rollback Plan** | Deferred | Backup is a `/framework-upgrade` §3.1 step, audited in Mode B. |
| **Migration** | Pass | Archived artifacts are out of scope; rules apply on write. |
| **Skill creation gate** | Pass | R6 routes skill creation through `skill-creator`, per CLAUDE.md. |

## 2. Risk Analysis

**Risk 1 — a verification that cannot fail.** A3 verified "no language rule exists" with
`grep -rniE "in english|на английском"`. That grep proves one phrasing is absent. A rule worded
"artifacts follow the framework's language" would pass the grep and violate the requirement. The
check was a proxy for the property, not the property.

**Risk 2 — a bar tuned to the artifact it judges.** A8 required this TASK to pass its own scanner
at zero `warn`. The scanner's thresholds are set by this same task. Left as written, a failing
scan could be resolved by moving the threshold rather than the prose.

**Risk 3 — rules unreachable by the roles that need them.** R5 places the normative form in
`documentation-standards`, which the tier table loads in the Development phase. TASK and PLAN are
written by the Analyst and the Planner. Without R9, the rules would exist where their audience
never reads them. R9 is present, so the risk is covered, but the TASK did not say so.

**Risk 4 — an unresolved threshold entering implementation.** Q1 leaves the sentence-length bound
open. A plan that starts before it is closed will hard-code a guess.

**Risk 5 — new section conflicting with existing ones.** §5.5 is added beside §5.1 (table cells)
and §5.2 (prose structure). Overlap would create two rules for one property.

## 3. Verdict & Actions

**Round 1: BLOCKED.** Four actions required.

1. **A3** — replace the grep proxy with a review of every rule statement added by this task, plus
   the grep as a secondary check.
2. **A8** — state that the thresholds are fixed from the §1.1 measurement before the scanner is run
   against this TASK, and that a failing scan is resolved in the prose.
3. **R5** — record that §5.5 is reachable by the authoring roles only through R9, and that §5.5
   must cross-reference §5.1 and §5.2 rather than restate them.
4. **Q1** — mark the bound as a decision the PLAN must close before the scanner is implemented.

**Round 2: APPROVED.** All four actions were applied to `docs/TASK.md`. Re-checked:

- A3 now verifies by review of added rule statements, with grep as secondary.
- A8 now pins the thresholds to §1.1 and forbids threshold-tuning as the remedy.
- R5 sub-features name the cross-reference duty; A11 added for non-overlap with §5.1/§5.2.
- Q1 is marked as blocking the scanner step of the PLAN.

No failure condition from `skill-self-improvement-verificator` §4 is triggered.

---

# Mode B — Plan Audit

**Target:** `docs/PLAN.md`
**Status:** **BLOCKED** (round 1) → **APPROVED** (round 2)

## 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | Pass | §0.3 baseline, a per-stage command table, and a Stage 6 acceptance run. |
| **Rollback** | Pass | §0.1 backs up seven files; §0.2 is restore-and-remove, deleting nothing. |
| **Atomic Updates** | Pass | Seven tasks, each with its own description file and dependencies. |
| **Test Coverage** | Pass | Selftest battery written at Stage 2 against stubs, observed failing. |
| **Ordering** | Pass | Five constraints stated, each with the failure it prevents. |

## 2. Risk Analysis

**Risk 1 — a verification that greps for a word.** Stage 5 verified the authoring surfaces with
`grep -l "register"` over four files. That proves the token appears, not that the rules are stated
correctly. It is the defect Mode A found in A3, reproduced one document later.

**Risk 2 — the skill-creation gate is not invoked by name.** CLAUDE.md prohibits creating a file
under `.agent/skills/` by hand and requires `init_skill.py <name> --tier <N>`. Task 096.2 says the
skill is scaffolded through `skill-creator` but never writes the command, so the step can be
executed by hand while appearing compliant.

**Risk 3 — no skill validation gate.** Nothing runs the skill-structure validator on
`artifact-formalizer` before Stage 6 declares acceptance. The framework has a validation gate for
exactly this and the plan does not call it.

**Risk 4 — "expected to fail" without a reason check.** Stage 2 expects the selftest to fail. A
syntax error also fails. Without asserting *why* it failed, a broken file passes for a correct Red
state.

**Risk 5 — the architecture edit is unverified.** `docs/ARCHITECTURE.md` §7.3 was written during
the Architecture phase. No plan step re-reads it against the shipped rules, so a late change to a
threshold or a file location would leave §7.3 stating something untrue.

## 3. Verdict & Actions

**Round 1: BLOCKED.** Five actions required.

1. Replace the Stage 5 grep with a review of each authoring surface against the §5.5 rule list.
2. Write the literal `init_skill.py` invocation into Task 096.2 and the plan's verification table.
3. Add a skill-validation gate before Stage 6 acceptance.
4. Require the Stage 2 Red state to name the failing cases, and require the file to import cleanly.
5. Add a Stage 6 step that re-reads ARCHITECTURE.md §7.3 against what shipped.

**Round 2: APPROVED.** All five applied to `docs/PLAN.md`. Re-checked: Stage 5 verifies by review,
the scaffold command is literal, `validate_skill.py` runs before acceptance, the Red state asserts
its own reason, and §7.3 is re-read at Stage 6.
