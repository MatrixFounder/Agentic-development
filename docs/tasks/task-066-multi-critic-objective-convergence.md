# Technical Specification: Multi-Critic Objective Convergence (parallel adversarial pipeline)

### 0. Meta Information
- **Task ID:** 066
- **Slug:** `multi-critic-objective-convergence`
- **Mode:** Framework Upgrade (meta-operation — modifies the parallel multi-critic convergence contract)
- **Type:** Hardening / consistency — extend Task 065's "Objective Convergence" philosophy to the `/vdd-multi` parallel-critic subsystem.
- **Workflow:** `/framework-upgrade`
- **Source:** Follow-up flagged at the end of Task 065. The parallel critics (`critic-logic`/`security`/`performance`) still self-certify convergence via a subjective `hallucinating` state — the exact gameable pattern Task 065 removed from Sarcasmotron.

## 1. General Description

Each parallel critic emits `Convergence signal: clean-pass | issues-found | hallucinating` (`.claude/agents/critic-*.md:13`). That `hallucinating` state feeds two consumers:
1. **Termination gate** (`vdd-multi.md` Phase 3): *"Hallucinating: critic inventing problems → category ✓"* — an **approval gate** driven by the critic self-reporting fabrication. Same subjective, gameable flaw Task 065 fixed in Sarcasmotron.
2. **Merge noise-filter** (`vdd-multi.md` rule 4, `skill-parallel-orchestration` rule 4): a critic reporting `hallucinating` → drop its low-severity items this iteration. A defensible filter, but keyed on the same subjective self-report.

This task replaces the subjective `hallucinating` state with an **objective** `bikeshedding-only` state — "no legitimate findings remain in this category; only style/nits" — so both the termination gate and the noise-filter become objective, mirroring Task 065's Objective Convergence. **Merge mechanics are not otherwise touched.**

### Invariants (MUST hold)
- Parallel-critique merge mechanics — location dedup (±3 lines), cross-category re-attribution, severity escalation on independent overlap, optional `--severity` filter, iteration cap — are **unchanged**.
- The Layer A / Layer B decision rule and the single-atomic-spawn invariant are **untouched**.
- The critic enum stays a 3-state contract (only the third state is renamed + redefined); `clean-pass` and `issues-found` are unchanged.

## 2. Epic & Issues

### Epic E — Objective convergence for parallel critics
**Issue E-1.** In the 3 critic agents (`.claude/agents/critic-logic.md`, `critic-security.md`, `critic-performance.md`, line 13), rename the emitted state `hallucinating` → **`bikeshedding-only`**, defined objectively ("no legitimate findings remain — only style/nits; NOT 'I was forced to invent problems'").
**Issue E-2.** In `vdd-multi.md` Phase 3 termination, change *"Hallucinating: critic inventing problems → category ✓"* to the objective state ("Bikeshedding-only: no legitimate findings remain, only style/nits → category ✓").
**Issue E-3.** Re-key the merge noise-filter (`vdd-multi.md` rule 4, `skill-parallel-orchestration/SKILL.md` rule 4) off `bikeshedding-only`; keep the mechanic (drop low-severity items this iteration).
**Issue E-4.** Refresh satellite references — `skill-parallel-orchestration/SKILL.md` §2.3 step-3 "filter hallucinations", `examples/usage_example.md` step 4, `references/sequential-fallback.md` merge step 4 — to the objective terminology. No live "hallucinat\*"-as-exit wording remains in this subsystem.

## 3. Non-functional Requirements
- **Cross-vendor.** Convergence *semantics* live in shared `.agent/` (`vdd-multi.md`, `skill-parallel-orchestration`); the Claude-Code critic wrappers (`.claude/agents/critic-*.md`) are updated in lockstep so their emitted enum matches. No vendor-specific behavior branch.
- **Safety (meta-operation).** Back up edited files to `.agent/archive/`; `skill-self-improvement-verificator` gates TASK and PLAN.
- **Gate.** Edited skill (`skill-parallel-orchestration`) must still pass `validate_skills.py` (43/43). Critic agents are wrappers (not skills) — verified by grep.
- **Scope discipline.** Only the convergence state and its two consumers change. No change to dedup/escalation/severity-filter/iteration-cap logic, or to the Sarcasmotron (single-roast) path already fixed in Task 065.

## 4. Constraints & Assumptions
- The `convergence` state is defined in the `.claude/agents/critic-*.md` wrappers (line 13) and consumed in `vdd-multi.md` + `skill-parallel-orchestration`. There is no separate System/ SOT for the enum; shared semantics live in the workflow/skill.
- Historical artifacts (`security-audit/docs/vdd-round*-critique.md`) and unrelated "anti-hallucination" mentions are out of scope.
- Builds on Task 065's "Objective Convergence" terminology (this branch is stacked on `feat/reviewers-hardening`).

## 5. Acceptance Criteria (RTM)

| ID | Requirement | Source file(s) | Issue |
|----|-------------|----------------|-------|
| **E1** | All 3 critic agents emit `clean-pass \| issues-found \| bikeshedding-only`; `hallucinating` removed; `bikeshedding-only` defined objectively. | `critic-logic.md`, `critic-security.md`, `critic-performance.md` | E-1 |
| **E2** | Phase-3 termination marks a category ✓ on the objective state (no legitimate findings, only style), not on "critic inventing problems". | `vdd-multi.md` | E-2 |
| **E3** | Merge noise-filter keys off `bikeshedding-only`; the drop-low-severity-this-iteration mechanic is unchanged. | `vdd-multi.md`, `skill-parallel-orchestration/SKILL.md` | E-3 |
| **E4** | No live "hallucinat\*"-as-exit wording remains in the parallel-critic subsystem; satellites use objective terms. | `skill-parallel-orchestration/SKILL.md`, `examples/usage_example.md`, `references/sequential-fallback.md` | E-4 |
| **INV** | Dedup / cross-category / severity escalation / `--severity` filter / iteration cap / Layer A·B rule unchanged. | all | invariant |
| **GATE** | `validate_skills.py --root . --quiet` green; no stale convergence terminology in the subsystem. | — | NFR |

## 6. Validation (prompt-level)
- A critic that finds only style nits reports `bikeshedding-only`; the category terminates ✓ on that objective state, and its low-severity items are dropped from the iteration.
- A critic that finds a real CRITICAL still reports `issues-found` and the loop continues — no early exit via self-certified fabrication.
- `grep` confirms `hallucinating` survives only in historical artifacts; the 3 critic enums + the 2 consumers + 3 satellites all use the objective term.
- `validate_skills.py` green; Layer A/B rule and the other merge rules are byte-unchanged.
