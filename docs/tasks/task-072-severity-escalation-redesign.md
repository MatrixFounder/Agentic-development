# Technical Specification: Severity-Escalation Redesign — R3a/R3b/R3d (C-08, partial item 7)

### 0. Meta Information
- **Task ID:** 072
- **Slug:** `severity-escalation-redesign`
- **Mode:** Framework Upgrade (meta-operation — modifies one Tier-2 skill, one workflow, one reference, one example)
- **Type:** P1 modernization, roadmap item 7 **partial** (sub-items R3a, R3b, R3d only). Closes the shippable-now portion of audit-067 claim **C-08** ("two critics flagging the same location → +1 severity" assumes critic independence that same-model personas do not have).
- **Workflow:** `/framework-upgrade` (with `skill-self-improvement-verificator` gate, Modes A + B).
- **Source:** User request (2026-06-10): "выполни R3a/R3b/R3d из docs/verification_roadmap.md" + `docs/verification_roadmap.md` item 7 + `docs/reviews/verification-stack-currency-audit-067.md` (claim C-08).

## 1. General Description

The merge rule "two critics independently flagging the same location → escalate severity by one level" double-counts one model's prior: all three critics are the same base model under different personas, and same-model pairs pick the *same wrong answer* ~60% of the time when erring (Correlated Errors, ICML 2025, arXiv:2506.07962; persona-differentiated same-model ensembles share priors and failure modes, arXiv:2601.12307). Same-model agreement is **corroboration** (the finding survived persona/prompt variation), not independent **confirmation**.

**New rule design (pre-specified in roadmap item 7 — wording authority):**
- **R3a — Same-model agreement: no auto-escalation.** Replace "+1 severity" with a `corroborated` tag on the merged finding; severity = max of the duplicates (dedup rule 1 unchanged). The "Overlaps" report section stays, listing corroborated findings.
- **R3b — Cross-category, different-mechanism exception.** Two critics flagging the same location with **different failure mechanisms** (e.g., unhandled edge case + exploitable injection at the same line) = two distinct analyses, not duplicate detection → +1 escalation remains legitimate. Mechanism-difference test: the exploit/failure scenarios are not paraphrases of each other — orchestrator judgment, documented in the merged report.
- **R3d — Sequential mode: explicit no-escalation.** In role-switching mode independence is weakest (same session window, same instance): agreement between sequential personas **never** escalates — tag only. Cross-mechanism findings in sequential mode get at most a `priority` flag (R3b's documented minimum form), never +1.

**What this task is NOT:**
- **R3c is out of scope** (user request names R3a/R3b/R3d only). No per-critic model config, no signal-strength gradation table, no `CLAUDE_CODE_SUBAGENT_MODEL` warning. Its cross-vendor form is BLOCKED BY item 6; its tier-diverse form stays 🔜 in the roadmap.
- **Do NOT touch** (roadmap discipline list): dedup rule 1 (±3 lines), cross-category re-attribution rule 2, bikeshedding filter rule 4, `--severity` filter rule 5, iteration caps.
- Item 11 (orchestrator-supplies-evidence contract) also edits vdd-multi Phase 1/2 and "pairs naturally" with item 7 per the roadmap — but the user scoped this cycle to R3a/R3b/R3d; item 11 stays 🔜.

**Blast radius (established by repo-wide grep, 2026-06-10):** the rule appears in exactly the 4 locations the roadmap names — `vdd-multi.md:106` (+ Overlaps placeholder `:131`), `skill-parallel-orchestration/SKILL.md:107` (+ §2.3 merge-summary echo `:60`), `references/sequential-fallback.md:47` (+ adjacent independence claim `:97`), `examples/usage_example.md:45-46`. `System/Agents/`, `.claude/agents/`, and `System/Docs/` carry no copy of the rule.

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | Target file(s) | Roadmap | Verification |
|----|-------------|----------------|---------|--------------|
| R1 | Replace Phase-2 merge rule 3 with the mechanism-aware rule: same-mechanism agreement → `corroborated` tag, severity = max, NO escalation (R3a); same location + different failure mechanisms → +1 escalation survives, mechanism-difference test documented (R3b). Update the Overlaps section placeholder (`:131`) to list corroborated findings + cross-mechanism escalations | `.agent/workflows/vdd-multi.md` (Phase 2 rule 3, report structure) | R3a, R3b | File read; grep G1; byte-consistency check G2 |
| R2 | Same rule-3 replacement in §6 (wording identical to R1 modulo the actor noun "teammates" vs "critics" — documented deviation, both files predate this task with that same noun split); sync the §2.3 step-3 merge summary echo | `.agent/skills/skill-parallel-orchestration/SKILL.md` (§6 rule 3, §2.3; version 3.0→3.1) | R3a, R3b | File read; greps G1/G2; `validate_skill.py` |
| R3 | Sequential merge step 3 → explicit no-escalation sentence: agreement between sequential personas never escalates (weakest independence — same session window, same instance); tag `corroborated` only; cross-mechanism → `priority` flag at most. Align the §Anti-patterns "stronger signal" line (`:97`) so it stops implying independent confirmation | `.agent/skills/skill-parallel-orchestration/references/sequential-fallback.md` | R3d | File read; grep G1 |
| R4 | Merge walkthrough (Step 3) updated to demonstrate the new rule: corroborated tag for same-mechanism agreement, escalation only for cross-mechanism overlap | `.agent/skills/skill-parallel-orchestration/examples/usage_example.md` | R3a, R3b | File read; grep G1 |
| R5 | Release bookkeeping: CHANGELOG EN+RU **v3.20.3**; README version-header bump (release convention per `3df62a2`); roadmap item 7 status → R3a/R3b/R3d ✅ done, R3c remains ⏳/🔜; session-state at phase boundaries | `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md`, `README.ru.md`, `docs/verification_roadmap.md` | migration list | File reads |
| R6 | Acceptance gates pass (G1–G4 below) | — | item 7 acceptance (R3a/b/d slice) | Bash outputs in audit artifact |

## 3. Acceptance Criteria (Gates)

- **G1 (old wording grep-clean, roadmap migration grep verbatim):** `grep -rn "escalate severity by one level" .agent/ .claude/ System/` → only the new R3b cross-mechanism wording remains (the phrase is legitimate there); zero hits in the old "same location → +1" sense. Hardened form: `grep -rn "independently flagging the same location\|independently flag the same location\|escalation on independent overlap\|escalate severity on cross-category overlap" .agent/ .claude/ System/` → empty.
- **G2 (lockstep byte-consistency):** the rule-3 text in `vdd-multi.md` and `SKILL.md §6` is identical modulo the single documented noun substitution (critics ↔ teammates) — verified by normalized diff in the audit artifact.
- **G3 (skill quality gate):** `validate_skill.py .agent/skills/skill-parallel-orchestration` pass; full sweep across `.agent/skills/*/` = **43/43** (baseline).
- **G4 (regression evidence):** `python3 -m pytest .agent/skills/security-audit/tests/ -q` = 30/30 and `python3 -m pytest .agent/skills/skill-parallel-orchestration/tests/ -q` green (pure-docs change; suites run as no-regression proof).

## 4. Out of Scope (considered and excluded — with reasons)

1. **R3c** (per-critic model config, gradation table, env-override warning) — excluded by user request; cross-vendor form BLOCKED BY item 6. Roadmap item 7 therefore stays partially open.
2. **Item 11** (orchestrator-supplies-evidence in vdd-multi Phase 1) — roadmap suggests pairing with 7, but user scoped this cycle explicitly; deferred.
3. Merge rules 1, 2, 4, 5 and iteration caps — roadmap "Do NOT touch" list; scored Current in audit 067.
4. `references/claude-code.md`, critic wrappers `.claude/agents/critic-*.md`, `System/Docs/WORKFLOWS.md` — grep-verified to carry no copy of the escalation rule; no edit needed (WORKFLOWS.md "escalation" hits are the unrelated REJECTED-iteration escalation).
5. `docs/reviews/verification-stack-currency-audit-067.md` — immutable audit history quoting the old rule; excluded by design (G1 scope is `.agent/ .claude/ System/`).

## 5. Open Questions
None. Roadmap item 7 pre-specifies wording, the 4 locations, the do-not-touch list, and the migration greps. Judgment calls recorded above: (a) critics/teammates noun split preserved (pre-existing); (b) sequential cross-mechanism findings get `priority` flag, not +1 (R3b's "at minimum" form, consistent with R3d's "never escalates"); (c) sequential-fallback `:97` "stronger signal" line aligned as R3d-adjacent consistency edit.
