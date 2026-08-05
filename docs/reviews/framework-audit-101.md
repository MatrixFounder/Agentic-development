# Framework audit 101 — behavioural evals for artifact-formalizer

**Skill applied:** `skill-self-improvement-verificator` · **Artifacts:** [docs/TASK.md](../TASK.md),
[docs/PLAN.md](../PLAN.md) · **Date:** 2026-08-05 · **Verdict:** APPROVED

## Mode A — specification audit

| # | Check | Verdict | Evidence |
| :--- | :--- | :--- | :--- |
| 1 | Root integrity: Stub-First and atomicity | pass | PLAN cluster A, item A5 |
| 2 | Skill compatibility: new agents load TIER 0 | not applicable | the task adds no agent and no prompt |
| 3 | Documentation: `System/Docs/` updated | pass with an amendment | see Finding F1 |
| 4 | Migration of existing sessions | not applicable | the change is additive; no existing artifact changes shape |

**Check 1 in detail.** Cluster A creates every file as a stub, and item A5 requires the selftest to
exit non-zero before any implementation begins.

## Mode B — plan audit

| # | Check | Verdict | Evidence |
| :--- | :--- | :--- | :--- |
| 1 | Explicit verification step | pass | the Verification checkpoints table, plus G6 and G7 |
| 2 | Rollback | pass | PLAN Sequencing rule, "Rollback" |
| 3 | Atomic updates | pass | seven clusters, each item a single file operation with its own checkpoint |
| 4 | Test coverage | pass | cluster E, items E1 to E14 |

**Check 2 in detail.** The Sequencing rule states `rm -rf` on one new directory plus `git checkout`
on the files cluster G touches. No cluster deletes or moves an existing file.

**Check 4 in detail.** Cluster E declares the battery, and item E4 asserts the fixture invariant
that keeps axis B measuring a gap rather than a detector.

## Failure conditions (§4)

| Condition | Present |
| :--- | :--- |
| `core-principles` or `skill-safe-commands` removed from an agent | no |
| `CLAUDE.md` modified without a `System/Docs/` update | no; `CLAUDE.md` is not modified |
| A new workflow with no trigger declared | no; the task adds no workflow |

No bypass flag is claimed.

## Findings

**F1 — `System/Docs/SKILLS.md` describes `artifact-formalizer` and PLAN cluster G did not name it.**
`SKILLS.md:67` and `SKILLS.md:73` state the skill's two modes. The task adds a third instrument, so
that entry becomes incomplete on merge. **Action:** G3 is extended to cover `System/Docs/SKILLS.md`.

**F2 — `docs/ARCHITECTURE.md` carries 8 pre-existing `warn` findings.** Lines 91, 187, 210, 242 and
411 to 417. None falls in §7.6, which this task added. **Action at audit time:** none; TASK §7
excludes edits outside the task's surface. **Closed 2026-08-05 by operator instruction**, after the
task's own work was complete: one rule-2 marker, two long sentences, one wide cell and four
severity glyphs. The document now reports `0 warn`. Substance is unchanged in every case — the
justification of the model policy moved under a `**Why.**` block, and the four glyphs became
`Rejected:` and `Required:`.

**F3 — cluster F spends tokens and no earlier cluster does.** The plan states this, and `--dry-run`
plus the TC-EV-12 sentinel keep clusters A to E at zero. **Action:** none; recorded as the
property that makes the selftest safe to wire into CI.

## Verdict

APPROVED, conditional on F1. The plan respects Stub-First, carries a rollback, breaks the work into
verifiable clusters, and adds a test battery for the feature it introduces.
