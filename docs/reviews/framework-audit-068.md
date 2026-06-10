# Framework Audit: Adversarial-Security Skill P0 Fixes (Task 068)

**Date:** 2026-06-10
**Auditor:** Self-Improvement Verificator
**Target:** `docs/TASK.md`
**Status:** **APPROVED** (Mode A — Specification Audit)

## 1. Compliance Checklist (Mode A)

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | ID 068, slug `adversarial-security-p0-fixes`, Mode = Framework Upgrade, source traced to audit 067 P0 items + user request. |
| **Root Integrity** | ✅ Pass | Two atomic, anchor-traced edits in one Tier-2 skill. The change *strengthens* `core-principles` §3 (anti-hallucination): it deletes an instruction to fabricate scanner evidence. No Tier-0 skill weakened. Stub-First N/A (prompt-content edit). |
| **Skill Compatibility** | ✅ Pass | No new agents/prompts/workflows. Edits an existing Tier-2 skill consumed by `critic-security.md` (which already states the objective-bar contract — the edit converges the skill *toward* its consumer, not away). TIER 0 untouched. |
| **Documentation** | ✅ Pass | R4 covers CHANGELOG (EN+RU) + version bump 1.1→1.2; registry entries (`System/Docs/SKILLS.md:107`, `SKILL_TIERS.md:54`) pre-checked generic — no staleness introduced. |
| **Migration** | ✅ Pass (N/A) | Critic termination/recon behavior is per-run, not persisted state; existing sessions unaffected. |

## 2. Failure-Condition Scan
- Removing `core-principles`/`skill-safe-commands` from any agent? ❌ No.
- Modifying a bootstrap file (`CLAUDE.md`/`AGENTS.md`/`GEMINI.md`) without `System/Docs` update? ❌ No bootstrap file touched.
- Creating a new Workflow without defining its Trigger? ❌ No new workflow.
→ **No blocking conditions.**

## 3. Risk Analysis
- **R1 — Persona over-removal.** Deleting the snarky-comment *termination condition* could drift into deleting the sarcastic *persona* (§2), which is out of scope and load-bearing for `/vdd-multi`. *Mitigation:* TASK NFR "minimal-diff invariant" restricts edits to §3/§5-consistency/§7 + version header; R3(d) diff review enforces it.
- **R2 — Internal §3↔§5 contradiction.** §5 Process step 1 says "Run Automation (`run_audit.py`)"; after the C-15 fix, §3 says the critic may be unable to run it and must report `scan: NOT RUN`. *Mitigation:* R2(c) explicitly checks §5 for consistency with the new §3 protocol.
- **R3 — Doctrine wording drift.** The new §7 objective bar could paraphrase `vdd-sarcastic` §4 into something subtly weaker (e.g., dropping "automation executed"). *Mitigation:* R1(b) requires verbatim-compatible alignment with §4 + the `critic-security.md` convergence enum; acceptance grep in UC-1.
- **R4 — Stale copies elsewhere.** A satellite could still carry the old instruction. *Mitigation:* pre-checked this session (greps over `.claude/agents/`, `vdd-multi.md`, `skill-adversarial-performance`, `System/Agents/` → both strings exist **only** in the target SKILL.md); R3(b–c) re-verifies post-edit.

## 4. Verdict
**APPROVED.** The specification is safe, minimal, anchor-traced, and doctrine-convergent. Proceed to Planning (Mode B gates backup + verification steps).

**Carry-forward for the PLAN:** backup step before edits (workflow §3.1); atomic per-edit steps mapped to RTM; explicit `validate_skill.py` run; post-edit grep assertions; rollback instructions.

---

# Mode B — Plan Audit (Task 068)

**Target:** `docs/PLAN.md` · **Status:** **APPROVED**

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | ✅ Pass | T3 is a dedicated gate: `validate_skill.py` + stale-reference grep + satellite re-read + minimal-diff check vs backup. Per-phase atomic greps in T1/T2. |
| **Rollback** | ✅ Pass | T0 backs up all present bootstrap files + the edit target to `.agent/archive/`; explicit restore path (workflow §5). |
| **Atomic Updates** | ✅ Pass | T1 (C-05) and T2 (C-15) are separate, RTM-mapped, each with its own verify assertion; scope fenced by the minimal-diff invariant. |
| **Test Coverage** | ✅ Pass (prompt-level) | No runtime code touched; skill-gate validator + grep assertions + diff-scope check, matching the 065/066 precedent. |

**Carry-forward checks honored:** all four items from Mode A's carry-forward appear as concrete PLAN steps (T0, T1/T2 atomicity, T3.1, Phase 0 rollback note).

**Verdict: APPROVED.** Proceed to Execution (T0 backup first).
