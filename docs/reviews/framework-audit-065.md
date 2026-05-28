# Framework Audit: Reviewers Hardening (Task 065)

**Date:** 2026-05-29
**Auditor:** Self-Improvement Verificator
**Target:** `docs/TASK.md`
**Status:** **APPROVED** (Mode A — Specification Audit)

## 0. Emergency Bypass
- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

**Justification:** None — no bypass needed.

## 1. Compliance Checklist (Mode A)

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | ID 065, slug `reviewers-hardening`, Mode = Framework Upgrade present in §0. |
| **Root Integrity (Tier 0 / Stub-First / Atomicity)** | ✅ Pass | Edits are additive prompt/markdown changes; §2 decomposes into Epics A–D with atomic issues; no Tier-0 skill is weakened. |
| **Skill Compatibility (Tier 0 load)** | ✅ Pass | No new agents/prompts created. The edited `09_code_reviewer_prompt.md` already declares TIER 0 (`core-principles`, `safe-commands`, `artifact-management`, `session-state`); edits do not remove them. |
| **Documentation** | ✅ Pass | Task explicitly updates `System/Docs/WORKFLOWS.md` (C-3) and mandates finalization docs; CHANGELOG entry to be added at finalization. |
| **Migration** | ✅ Pass (N/A) | Control-flow field `has_critical_issues` is invariant; no state/schema change → existing sessions and `latest.yaml` remain valid. Additive output keys do not break consumers. |
| **Rollback strategy present** | ✅ Pass | NFR §3 mandates `.agent/archive/` backup before edits (handled in PLAN Mode B). |

## 2. Failure-Condition Scan (blocking gates)
- **Removing `core-principles`/`safe-commands` from any Agent?** ❌ Not present → safe.
- **Modifying a bootstrap file (`GEMINI.md`/`CLAUDE.md`/`AGENTS.md`) without a `System/Docs` update?** ❌ Not triggered — Epic D edits the *workflow file's reference* to bootstrap files, not the bootstrap files themselves; WORKFLOWS.md is updated regardless.
- **New Workflow without a Trigger defined?** ❌ No new workflow created.

→ **No blocking conditions.**

## 3. Risk Analysis
- **R1 — Contract drift re-introduced.** If only some of the four reviewer-contract sources are aligned, drift persists. *Mitigation:* A3 enumerates all four; PLAN must touch A/B/C/D atomically and a verification step greps all four.
- **R2 — Sarcasmotron divergence.** Editing the overlay but not the three skill/methodology definitions recreates multi-source drift. *Mitigation:* C-1/B3 require all four definitions to state the identical objective criterion; verification greps for residual subjective wording.
- **R3 — Accidental control-flow change.** Touching `has_critical_issues` semantics or the DECISION TABLE would change routing. *Mitigation:* hard invariant in §1 + A2; DECISION TABLE explicitly out of edit scope.
- **R4 — Tone regression.** Making the reviewer harsher or Sarcasmotron softer violates intent. *Mitigation:* A2/C2 preserve tiers, compliance frame, hostile stance.
- **R5 — Skill gate failure.** Editing `vdd-adversarial`/`vdd-sarcastic` SKILL.md could trip `validate_skills.py`. *Mitigation:* edits via `skill-enhancer`; PLAN includes a 43/43 gate run.
- **R6 — Wrapper drift.** `code-reviewer.md` footer could diverge from the new SOT superset. *Mitigation:* wrapper updated in same task; post-edit grep per KNOWN_ISSUES §Wave-1/2.

## 4. Verdict & Actions
**APPROVED.** The specification is safe, consistent, documented, and respects all constitutional (Tier 0) rules and contract invariants. Proceed to Architecture assessment and Planning (Mode B audit will gate the PLAN for explicit backup + verification steps).

**Carry-forward requirements for the PLAN:**
1. Phase 0 backup of all edited files to `.agent/archive/`.
2. Atomic tasks per Epic; A/B/C/D contract/criterion changes each paired with a consistency-grep verification.
3. Explicit gate: `validate_skills.py --root . --quiet` green + wrapper-drift grep.

---

# Mode B — Plan Audit (Task 065)

**Target:** `docs/PLAN.md`
**Status:** **APPROVED**

## Compliance Checklist (Mode B)

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | ✅ Pass | T11 runs `validate_skills.py --root . --quiet` + contract/criterion/wrapper-drift greps + an adversarial review of the diff. |
| **Rollback** | ✅ Pass | Phase 0 / T0 backs up all 11 targets to `.agent/archive/`; explicit Rollback Plan (`cp .agent/archive/<file>.bak <orig>`). |
| **Atomic Updates** | ✅ Pass | T0–T11 are atomic, each scoped to one file/concern with a per-task RTM mapping and a verification clause. |
| **Test Coverage** | ✅ Pass (prompt-level) | No runtime unit test applies to prompt semantics; coverage = the skill quality gate over edited skills + consistency greps acting as executable assertions + TASK §7 prompt-level scenarios. Carry-forward #1–#3 all satisfied. |

## Carry-forward verification
1. ✅ Phase 0 backup present.
2. ✅ Atomic per-Epic tasks with consistency-grep verification each.
3. ✅ Explicit `validate_skills.py` gate + wrapper-drift grep in T11.

## Verdict
**APPROVED.** Plan has explicit backup, rollback, atomic chunks, and a concrete verification phase. Proceed to Execution (Phase 0 backup first).

---

# Post-Execution Verification (Task 065)

**Status:** **PASS** — implemented & verified.

| Gate | Result |
| :--- | :--- |
| Skill quality gate | `validate_skills.py --root . --quiet` → **43/43** (edited `vdd-adversarial`, `vdd-sarcastic` green). |
| Contract convergence (A3) | All 4 definitions list `{review_status, has_critical_issues, e2e_tests_pass, stubs_replaced}`; `comments` = prose everywhere. |
| Control-flow invariant (A2) | DECISION TABLE byte-identical (diff vs backup); `has_critical_issues` unchanged; e2e/stubs not promoted to routing. |
| Objective Convergence (B1/B3) | Identical objective bar across all 4 Sarcasmotron defs; no subjective approval trigger remains. |
| Terminology (C2) | "Hallucination Convergence/Exit/runs-out-of-critiques" gone from all normative defs; survives only in historical artifacts (CHANGELOG, docs/tasks, latest.yaml). |
| Vendor-aware backup (D1) | `framework-upgrade.md` Step 3.1/Step 5 loop over CLAUDE.md/AGENTS.md/GEMINI.md; shell validated (`bash -n`). |
| Wrapper drift | No stale SOT refs; `code-reviewer.md` footer matches the new superset. |
| Adversarial review (VDD dogfood) | code-reviewer subagent applied the **new** Objective-Convergence bar to the diff → APPROVED (0 CRITICAL, 0 MAJOR). |

**VDD loop catch:** the Phase-4 adversarial review surfaced 3 normative residuals of the old subjective rule (`VDD.md`, `TDD_VS_VDD.md`, `/vdd-adversarial` workflow) under different labels; these were folded in as RTM Issue **C-4** and re-verified clean. The `/vdd-multi` `convergence: hallucinating` dedup noise-filter is a distinct mechanism, deliberately out of scope.

**Not committed** — awaiting user. **Core prompts changed** (`09_…`, `01_orchestrator.md`) → recommend a session restart before relying on the updated reviewer behavior.
