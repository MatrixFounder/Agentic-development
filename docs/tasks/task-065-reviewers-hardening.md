# Technical Specification: Reviewers Hardening — Provable Clean Code-Review Pass + Objective Sarcasmotron Exit (cross-vendor)

### 0. Meta Information
- **Task ID:** 065
- **Slug:** `reviewers-hardening`
- **Mode:** Framework Upgrade (meta-operation — modifies the framework's own review prompts, skills, workflows)
- **Type:** Hardening — make a clean Code-Review pass *provable*, align the reviewer output contract across all sources, and replace the subjective Sarcasmotron exit with an objective one.
- **Workflow:** `/framework-upgrade` (invoked via `/vdd-start-feature`)
- **Source:** `Backlog/reviewers_hardening.md` (refined & correctness-verified in the prior planning session) **+** an in-session user addition (Доработка 4 — see Epic D).

## 1. General Description

Three reviewer weaknesses, plus one cross-vendor backup gap, are addressed. Roles are **NOT merged or levelled** — Code Reviewer (quality gate) and Sarcasmotron (adversarial roast) keep distinct goals. Routing, phases, dispatch, loops, the 3-REJECT limit, and HITL are **not touched**.

1. **Code Reviewer — proof of checking.** When there are no critical issues, the report currently shows *nothing* about what was verified: an unchecked pass and a checked-and-clean pass are indistinguishable. Add a mandatory **"Verified" block** (plain markdown, report body) listing which TASK requirements were cross-checked and which edge cases were considered.
2. **Code Reviewer — output contract convergence.** The reviewer's output contract is defined in **four** drifting places. Converge them to one compatible structured superset; `comments` is the prose body, not a JSON key.
3. **Sarcasmotron — objective exit criterion.** The "Hallucination Convergence" exit triggers on *"the auditor is forced to invent nitpicks → approve"*, making fabrication the *trigger* for approval (a lazy/sycophantic model exits early; the signal is unobservable). Replace with an objective condition across **all four** authoritative definitions; refresh stale terminology in referencing files.
4. **(Added by user) framework-upgrade.md — vendor-aware backup/rollback.** The `/framework-upgrade` workflow backs up and restores only `GEMINI.md`; the repo now uses three bootstrap files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`). Backup (Step 3.1) and Fallback (Step 5) must cover all present bootstrap files.

### Orchestrator contract (strict invariants — MUST hold)
- The carrying control-flow field is **`has_critical_issues`**. Its **name, type, and semantics must not change**. The DECISION TABLE in `skill-orchestrator-patterns` is **not edited**.
- The prose report is passed to the developer for fixes; the "Verified" block lives **in the report body** and does not affect control-flow.
- All additions to structured output are **additive only** — must not break keys consumers expect (`has_critical_issues`, `e2e_tests_pass`, `stubs_replaced`).

## 2. Epics & Issues

### Epic A — Code Reviewer: proof-of-checking ("Verified" block)
**Issue A-1.** In `System/Agents/09_code_reviewer_prompt.md`, add a mandatory **"Verified"** block to the report format (Step 3 / Step 4 area), appearing when `has_critical_issues = false`: enumerates verified TASK requirements + edge cases considered. Plain markdown in the body, **not** in the JSON footer.
**Issue A-2.** Preserve tiers (🔴/🟡/🟢), the compliance focus, the three-pillar structure, and the quality-gate role — do **not** make the reviewer harsher.

### Epic B — Code Reviewer: output-contract convergence (four sources)
The four definitions today:
- **A — SOT** `System/Agents/09_code_reviewer_prompt.md` → `{review_status, has_critical_issues}` (2 fields).
- **B — orchestrator schema** `.agent/skills/skill-orchestrator-patterns/SKILL.md` Extended Schema (Code Reviewer) → `{comments, has_critical_issues, e2e_tests_pass, stubs_replaced}`.
- **C — wrapper** `.claude/agents/code-reviewer.md` → `{review_status, has_critical_issues, stubs_replaced, e2e_tests_pass}`.
- **D — orchestrator** `System/Agents/01_orchestrator.md` Step 11 → `Expected: { comments, has_critical_issues, e2e_tests_pass, stubs_replaced }`.

**Issue B-1.** Converge all four to one structured superset: **`has_critical_issues`, `e2e_tests_pass`, `stubs_replaced`, `review_status`**. SOT (A) and wrapper (C) emit this superset; B and D align to it.
**Issue B-2.** Reconcile `comments` as the **prose report body** (text passed to the developer), removed from the JSON-key lists in B and D — not a structured key.
**Issue B-3.** Additions additive; `has_critical_issues` semantics unchanged. `review_status` retained (used by wrapper/humans).

### Epic C — Sarcasmotron: objective exit criterion (all authoritative definitions)
The exit criterion is authoritatively defined in **four** places; changing only the overlay would re-create the very multi-source drift Epic B removes:
- `.agent/workflows/vdd-03-develop.md` (overlay, Exit Strategy + Refinement Strategy).
- `.agent/skills/vdd-adversarial/SKILL.md` (Convergence Signal).
- `.agent/skills/vdd-sarcastic/SKILL.md` (Convergence Signal).
- `.agent/skills/vdd-adversarial/references/vdd-methodology.md` ("Convergence and the Exit Strategy").

**Issue C-1.** Replace the subjective trigger with the **objective condition** in all four: approve **only when** (1) a full test run has been executed, (2) zero CRITICAL, (3) zero legitimate findings in logic / security / slop, (4) only bikeshedding/style remains. Skills edited via `skill-enhancer`.
**Issue C-2.** Preserve the hostile tone and the "assume broken until proven" stance in spirit. VDD-loop **mechanics** (3-REJECT, escalation, HITL) untouched.
**Issue C-3.** Refresh the now-stale **"Hallucination Convergence"** label in referencing files — `.agent/workflows/vdd-05-run-full-task.md` (HITL digest label) and `System/Docs/WORKFLOWS.md` (exit-rule description) — **terminology only, no loop-mechanic change**.
**Issue C-4 (found by the Phase-4 adversarial review).** Three further normative definitions still encoded the *old subjective exit* under different wording and must state the same objective criterion: `.agent/workflows/vdd-adversarial.md` (the `/vdd-adversarial` single-task workflow — "terminate when hallucinations dominate"), `System/Docs/VDD.md` ("Hallucination Exit"), `System/Docs/TDD_VS_VDD.md` (Exit Condition cell). The `/vdd-multi` + `skill-parallel-orchestration` `convergence: hallucinating` signal is a **distinct dedup noise-filter for parallel critics (not an approval gate)** and is deliberately **out of scope**; the `security-audit/docs/vdd-round*-critique.md` files are historical artifacts, left as-is.

### Epic D — framework-upgrade.md: vendor-aware backup/rollback (user addition)
**Issue D-1.** In `.agent/workflows/framework-upgrade.md`, Step 3.1 (Backup) and Step 5 (Fallback) must back up / restore **all present bootstrap files** (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`), not only `GEMINI.md`. Keep the `.agent/archive/` destination and the existing meta-operation structure.

## 3. Non-functional Requirements
- **Cross-vendor (mandatory).** Framework runs on Claude Code, Codex, Gemini CLI, Cursor, Antigravity. All edits live in shared `System/` and `.agent/` (SOT, inherited by all vendors), plus the Claude-Code-only wrapper. No behavior may depend on a Claude-Code-only mechanism; the "Verified" block is plain markdown, read identically as text by every vendor.
- **Contract safety (meta-operation).** `has_critical_issues` name/type/semantics and the DECISION TABLE are invariant; orchestrator control-flow must be identical before and after on the same inputs.
- **Safety / rollback.** Back up every edited file to `.agent/archive/` before changes (per `/framework-upgrade` Step 3.1); `skill-self-improvement-verificator` gates both the TASK and the PLAN.
- **Skill edit protocol.** Skills are edited via `skill-enhancer`; no new skills/agents are created; edited skills must still pass `validate_skills.py` (43/43).
- **Validation is prompt-level.** There is no runtime unit test for prompt semantics; verification is prompt-level reasoning + the skill quality gate + a wrapper-drift grep.

## 4. Constraints & Assumptions
- **Backlog source of truth:** `Backlog/reviewers_hardening.md` (already correctness-verified). Epic D is the only item beyond that backlog, added in-session by the user.
- **Wrapper/SOT drift (KNOWN_ISSUES §Wave-1/2):** `.claude/agents/*.md` wrappers reference one SOT path each; we edit SOT *content* (no renames), so wrappers stay valid — but a post-edit `grep` confirms no stale references and that the `code-reviewer.md` footer matches the new SOT superset.
- **No-go list:** do not merge/level roles; do not change `has_critical_issues` or the DECISION TABLE; do not make Sarcasmotron softer or the reviewer harsher; do not touch the **mechanics** of phases/VDD-loops, dispatch, limits, or the HITL gate (editing the Sarcasmotron exit-criterion text in `vdd-03` and the stale label in `vdd-05` is text/terminology, not mechanics); no vendor-specific behavior branches; RU translations untouched (removed separately).

## 5. Open Questions
- **Q1 (resolved):** "Verified" lives **markdown-body only** (zero contract risk, additive, plain-text cross-vendor — consistent with C1/A3). No structured flag introduced.
- **Q2 (resolved):** `review_status` **retained** in the superset (wrapper/human compatibility).
- **Q3 (author discretion):** exact prose wording of the "Verified" block and of the objective exit condition — wording is free, role tone unchanged.
- **Q4 (Epic D, decided):** back up all three bootstrap files that exist (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`); use a glob/loop over present files rather than a fixed `GEMINI.md` line, so the step degrades gracefully if a vendor file is absent.

## 6. Acceptance Criteria (Requirements Traceability Matrix)

| ID | Requirement | Source file(s) | Issue |
|----|-------------|----------------|-------|
| **A1** | At `has_critical_issues = false`, the reviewer report contains a non-empty "Verified" block (verified requirements + edge cases). With issues present, behavior is unchanged. | `09_code_reviewer_prompt.md` | A-1 |
| **A2** | `has_critical_issues` (name/type/semantics) and the DECISION TABLE are unchanged; orchestrator control-flow is identical before/after on the same inputs. | `09_…`, `skill-orchestrator-patterns`, `01_orchestrator.md` | invariant |
| **A3** | Reviewer output is consistent across all **four** definitions (SOT, orchestrator schema, wrapper, `01_orchestrator.md`): one structured superset; all consumer-expected keys present; `comments` described as prose (not a key); additions additive. | A/B/C/D files | B-1,B-2,B-3 |
| **A4** | Tiers and the compliance frame of the reviewer are unchanged. | `09_…` | A-2 |
| **B1** | Sarcasmotron approval is bound to the objective condition (tests run, 0 CRITICAL, 0 legitimate findings), not to "forced to invent nitpicks". | `vdd-03`, `vdd-adversarial`, `vdd-sarcastic`, `vdd-methodology.md` | C-1 |
| **B2** | Sarcasmotron tone/stance preserved in spirit; 3-REJECT and escalation untouched. | same as B1 | C-2 |
| **B3** | The objective exit criterion is identical across all four Sarcasmotron definitions (overlay + two skills + methodology ref); no skill/workflow divergence. | same as B1 | C-1 |
| **C1** | Edits only in `System/`/`.agent/` (+ the Claude-Code wrapper); no vendor-specific dependency in behavior; output reads as plain text for all vendors. | all | NFR |
| **C2** | No remaining wording (any label: "Hallucination Convergence", "Hallucination Exit", "runs out of critiques", "hallucinations dominate") implies the old subjective rule in any normative definition; loop mechanics (3-REJECT/escalation/HITL) provably unchanged. | `vdd-05`, `WORKFLOWS.md`, `vdd-adversarial.md`, `VDD.md`, `TDD_VS_VDD.md` | C-3, C-4 |
| **D1** | `/framework-upgrade` backup (Step 3.1) and fallback (Step 5) cover all present bootstrap files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`); degrades gracefully if one is absent; `.agent/archive/` destination retained. | `framework-upgrade.md` | D-1 |

## 7. Validation (prompt-level)
- **Reviewer:** an under-checked "clean" pass must now produce a non-empty "Verified"; a seeded defect still yields `has_critical_issues = true`.
- **Contract:** walking the Code-Review stage, the orchestrator receives `has_critical_issues` (+ `e2e_tests_pass`, `stubs_replaced`) and branches as before; the wrapper emits the same set; all four definitions list the same structured superset; `comments` is described as prose everywhere.
- **Sarcasmotron:** seeded slop is rejected; clean code is approved without invented nitpicks; the VDD loop terminates normally; the four definitions state the same objective criterion.
- **Cross-vendor smoke:** the reviewer report and Sarcasmotron output render and are consumed under Cursor / Gemini CLI / Codex (role-switching) without vendor-specific assumptions.
- **framework-upgrade:** Step 3.1 / Step 5 reference all three bootstrap files; the snippet is shell-correct and skips absent files.
- **Gate:** `python System/scripts/validate_skills.py --root . --quiet` → green (edited skills `vdd-adversarial`, `vdd-sarcastic` still pass); wrapper-drift grep returns no stale references.
