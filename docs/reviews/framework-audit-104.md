# Framework Audit: TASK 104 — resolver wiring

**Date:** 2026-08-07
**Auditor:** Self-Improvement Verificator (Mode A — SPECIFICATION AUDIT)
**Target:** `docs/TASK.md`
**Status (round 1):** **BLOCKED** · **Status (round 2):** **APPROVED**

## 0. Emergency Bypass

No flag set. No bypass claimed.

## 1. Compliance Checklist — round 1

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | Pass | ID 104, slug `resolver-wiring`, archive name, dependency pinned to `ed2af74` |
| **Tier Protection** | Pass | No TIER 0 skill modified. Four TIER 1 checklists gain a section; none loses one |
| **Root Integrity** | Pass | Eight atomic requirements, each bound to an acceptance criterion; every figure states its measurement |
| **Skill Compatibility** | N/A | No agent or prompt is created. The four reviewer prompts already declare `documentation-standards` |
| **Documentation** | **Fail** | See F-1 |
| **Migration** | **Fail** | See F-2 |

### F-1 — `System/Docs/` is not addressed, and the same omission blocked TASK 103

`R8` requires both changelogs and the ledger. Nothing requires the registry, and
`framework-upgrade` §4.2 names `System/Docs/SKILLS.md` **and** `WORKFLOWS.md` as a finalization step.

Measured: `WORKFLOWS.md` describes workflows at summary granularity — a mermaid graph plus a
one-row-per-workflow table (`framework-upgrade` at `:156`) — not step by step. So an edit is
plausibly unnecessary here, unlike TASK 103 where a skill gained a whole CLI surface. But "plausibly
unnecessary" is a judgement the task must **record**, not one a reader should have to reconstruct.

**Required action:** state the decision explicitly — either a requirement covering the registry, or
a decision recording why seven added steps do not change what `SKILLS.md` and `WORKFLOWS.md`
describe.

### F-2 — the two halves of this task reach consumers by different routes, and the task does not say so

Measured in onchain-analytics: `.agent/skills/` holds **47 per-skill symlinks** into
`.agentic-development`, `code-review-checklist` and `task-review-checklist` among them.
`.agent/workflows/` is a **real directory**, per-repo, and WI-16 §8 states the same.

Consequence, unstated in the TASK:

| Half | Reaches five consumer repositories | When |
| :--- | :--- | :--- |
| Four checklist edits (T2) | **yes**, by symlink | at commit time, no adoption step |
| Seven workflow steps (T1) | **no** | never, unless each repo edits its own copy |

The task therefore delivers T2 coverage fleet-wide and T1 coverage **in this repository only**. That
is defensible — the checklist half is advisory and costs an unadopting project nothing (103-D1) —
but a reader of the RTM would conclude both halves land everywhere.

**Required action:** state the asymmetry, and state which half a consumer actually gets.

## 2. Risk Analysis

- **R-1 — the checklist half is live in five repositories the moment this commits.** Mitigated by
  R2's not-a-defect clause, which is the single item preventing a fleet-wide migration demand. A1
  must not be weakened to allow its omission.
- **R-2 — collision with the open WI-16.** Six of seven workflows are in its pinned table and its
  acceptance fails on a displaced site. Mitigated by §2.1's site rule; A2 pins it.
- **R-3 — a double-run.** `03-develop-single-task` and `light-02-develop-task` invoke the code
  reviewer whose checklist now carries the item; a step there would run the resolver twice. A4 is
  the assertion, and it is written as a prohibition on nine named workflows rather than as an
  absence, which is the only form a test can check.
- **R-4 — the derived test is the whole value of R6 and the easiest thing to weaken.** A literal
  list of eleven paths passes forever and answers nothing about a workflow added tomorrow. A3 states
  the failure condition in exactly those terms.

## 3. Verdict — round 1

**BLOCKED.** Two required actions: F-1, F-2.

## 4. Round 2 — re-audit after redraft

| Action | Evidence in the redraft |
| :--- | :--- |
| F-1 | 104-D5 records the registry decision with the measurement that supports it |
| F-2 | 104-D6 states the propagation asymmetry and which half a consumer receives; §7 repeats it as a scope boundary |

| Check | Status |
| :--- | :--- |
| Meta-Information · Tier Protection · Root Integrity | Pass |
| Skill Compatibility | N/A |
| **Documentation** | **Pass** |
| **Migration** | **Pass** |

**APPROVED for §2 Planning.** Two obligations carry into the Mode B audit, which gates them:

1. **Stub-First.** The test of R6 is the structure; it is written and failing before any checklist or
   workflow is edited, so the red list is the specification.
2. **Backup set.** `framework-upgrade` §3.1 covers bootstrap files only. This task edits four skills,
   seven workflows, two changelogs and the ledger, and creates one test — the PLAN names its own set.

## 5. Mode B — PLAN AUDIT

**Target:** `docs/PLAN.md` · **Status (round 1):** **BLOCKED** · **Status (round 2):** **APPROVED**

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | Pass | A8, B6, B7, C4, D3 — every cluster ends in an executed gate, and A8 records its red list |
| **Rollback** | Pass | 13 tracked files plus 2 creations, each named; states what a partial revert leaves behind |
| **Atomic Updates** | Pass | Four clusters, independently revertible |
| **Test Coverage** | Pass | Cluster A precedes every edit; baselines measured (413 + 74 subtests, 46/46, 23 workflow files) |
| **Stub-First** | Pass | The test is the structure, written and failing first — the carried obligation from §4 |
| **Executability** | **Fail** | See F-3 |
| **Ordering against an unlanded record** | **Fail** | See F-4 |

### F-3 — A7 asserts a clause without naming the string it asserts

A7 requires the test to check that each checklist "contains the not-a-defect clause of R2". No
string is named. Two failure modes follow and both are silent: a loose substring passes on a
checklist that says the opposite, and a strict one breaks on a wording change that preserves the
meaning — after which someone relaxes the assertion and the guarantee is gone.

This assertion is the blast-radius mitigation for five consumer repositories. It is the last item in
this task that should be approximate.

**Required action:** name the exact token the test asserts, and make it a token chosen to be stable —
a section heading plus a marker phrase — rather than a sentence someone will reword.

### F-4 — Cluster C orders the step against a site that does not exist

C2 places the resolver step "after the WI-16 State-Claim Sweep site named in that record's §5.1
table". **WI-16 is open**: its sites are proposed and none is in any workflow file today. As written
the instruction cannot be followed — there is nothing to sit after.

The intent is sound and needs restating as a forward-compatible rule: place the step where WI-16's
site is *specified* to go, positioned so that WI-16 can later insert **before** it without moving it.
Otherwise the two records collide on landing and WI-16's acceptance — which fails on a displaced
site — fails because of this task.

**Required action:** restate C2 as a placement that reserves WI-16's position rather than following
it.

## 6. Verdict & Actions — Mode B

**BLOCKED**: F-3, F-4.

### Round 2 — re-audit after redraft

| Action | Evidence in the redraft |
| :--- | :--- |
| F-3 | A7 names the asserted tokens: the `## N. References` heading and the marker `not a defect`, both stated in Cluster B as the text to write |
| F-4 | C2 restated — the step takes the position WI-16's table specifies **for its own site**, placed so WI-16 inserts above it on landing; nothing is ordered against an absent line |

**APPROVED for §3 Execution.** No bypass flag; no TIER 0 skill modified; acceptance set A1–A6
unchanged by this round.
