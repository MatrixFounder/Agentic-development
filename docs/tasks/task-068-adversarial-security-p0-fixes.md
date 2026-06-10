# Technical Specification: Adversarial-Security Skill P0 Fixes (C-05 / C-15 Harmful-claim remediation)

### 0. Meta Information
- **Task ID:** 068
- **Slug:** `adversarial-security-p0-fixes`
- **Mode:** Framework Upgrade (meta-operation — modifies a framework skill)
- **Type:** P0 remediation of 2 HARMFUL claims found by audit 067. One skill file edited; satellites verified, not edited (pre-checked clean).
- **Workflow:** `/framework-upgrade` (with `skill-self-improvement-verificator` gate, Modes A + B).
- **Source:** User request (2026-06-10) + `docs/reviews/verification-stack-currency-audit-067.md` backlog items P0-1 [C-05] and P0-2 [C-15]; pre-authorized by session decision "067: P0 fixes (C-05, C-15) … require follow-up /framework-upgrade cycle with skill-self-improvement-verificator gate".

## 1. General Description

Audit 067 graded two claims in `.agent/skills/skill-adversarial-security/SKILL.md` (v1.1) **HARMFUL** — both are residuals that contradict the framework's own v3.18/v3.19 Objective Convergence doctrine and `core-principles` §3 (anti-hallucination):

- **C-05** (`SKILL.md:68`, §7 Termination): termination requires "at least one snarky comment" — tone-as-success-criterion forces noise on clean code and directly contradicts `vdd-sarcastic/SKILL.md` §4 ("Approval is bound to the objective bar — NOT to 'I was forced to invent a flaw'").
- **C-15** (`SKILL.md:29`, §3 Reconnaissance): "Mock the results if you cannot run it directly, but assume standard tool outputs (slither/bandit)" — instructs a security critic to **fabricate scanner evidence**. Compounding: the `critic-security` subagent has no Bash tool (C-13), so in every `/vdd-multi` run the fabrication branch is the *default* path, not the exception.

This task deletes both harmful instructions and replaces C-15's with an honest no-fabrication protocol (`scan: NOT RUN` + manual-review-only + orchestrator-supplied scan results).

## Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features |
|----|-------------|------|--------------|
| R1 | **[C-05] §7 Termination fix**: delete the condition "You have made at least one snarky comment about a questionable design choice" | Yes | (a) termination binds to the objective bar **only**: automation executed + no Critical/High findings + bikeshedding-only remains; (b) wording aligned with `vdd-sarcastic/SKILL.md` §4 Objective Convergence doctrine and `critic-security.md` convergence-signal contract (`clean-pass \| issues-found \| bikeshedding-only`); (c) no other §7 semantics changed |
| R2 | **[C-15] §3 Reconnaissance fix**: delete "Mock the results if you cannot run it directly, but assume standard tool outputs (slither/bandit)" | Yes | (a) replace with: if the script cannot be executed in your context, report `scan: NOT RUN` and proceed with manual review only — **never fabricate scanner output**; (b) note that the orchestrator runs `run_audit.py` and passes results into the critic prompt (the `critic-security` agent has no Bash tool); (c) §5 Process step 1 ("Run Automation") checked for consistency with the new §3 wording |
| R3 | **Verification gate** | Yes | (a) `python3 .agent/skills/skill-creator/scripts/validate_skill.py` green on the edited skill; (b) grep `.claude/agents/` for stale references to the deleted instructions (expected: none — pre-checked); (c) satellite consistency check: `critic-security.md`, `.agent/workflows/vdd-multi.md`, `skill-adversarial-performance/SKILL.md` contain no copy of either harmful claim; (d) diff review confirms only §3 + §7 (+ version header) changed |
| R4 | **Documentation & hygiene** | Yes | (a) skill version bump 1.1 → 1.2; (b) CHANGELOG entry (EN + RU) tracing to C-05/C-15; (c) registry check: `System/Docs/SKILLS.md` + `SKILL_TIERS.md` entries are generic — verified no update needed; (d) backup of every edited file to `.agent/archive/` before edits (workflow §3.1) |

## 2. Use Cases

### 2.1 UC-1: Maintainer remediates the two HARMFUL audit findings (main)
**Actors:** Framework maintainer (user); Orchestrator agent.
**Preconditions:** Audit 067 report exists; framework at v3.19.1; `skill-adversarial-security` v1.1.
**Main scenario:**
1. Agent backs up target files to `.agent/archive/`.
2. Agent applies R1 and R2 edits to `.agent/skills/skill-adversarial-security/SKILL.md`.
3. Agent runs the verification gate (R3): skill validator + stale-reference greps + satellite checks.
4. Agent updates CHANGELOG (R4) and persists session state.
**Postconditions:** Both HARMFUL claims gone; termination is objective-bar-only; no fabrication instruction anywhere in the verification stack; skill gate green; satellites consistent.
**Acceptance criteria:**
- ✅ `grep -n "snarky" .agent/skills/skill-adversarial-security/SKILL.md` → no termination-condition hit.
- ✅ `grep -rn "Mock the results" .agent/` → zero hits outside historical archives/reviews.
- ✅ §3 contains `scan: NOT RUN` protocol + orchestrator-supplies-results note.
- ✅ §7 termination = automation executed + no Critical/High + bikeshedding-only (objective bar verbatim-compatible with `vdd-sarcastic` §4).
- ✅ `validate_skill.py` passes for the edited skill.
- ✅ Only `skill-adversarial-security/SKILL.md` modified among framework components (CHANGELOG/docs/session-state aside).

## 3. Non-functional Requirements
- **Minimal-diff invariant:** no edits outside §3, §5 (only if needed for consistency), §7, and the version header of the one skill file.
- **Doctrine consistency:** post-edit wording must not contradict `vdd-sarcastic` §4, `critic-security.md`, or `vdd-multi.md` convergence semantics.
- **Rollback:** backups in `.agent/archive/`; restore per workflow §5 Fallback.
- **Conventions:** session state persisted at each phase boundary; TASK/PLAN archived per `skill-archive-task` at next task rotation.

## 4. Constraints & Assumptions
- Audit 067's claim anchors (lines 29, 68) and its P0 fix wording are trusted inputs (verified against the working tree this session).
- Out of scope: all P1/P2 backlog items from audit 067 — including C-13 capability-asymmetry restructuring (item 11) — except that R2(b)'s orchestrator note is the C-15-side half explicitly required by P0 item 2 ("Pairs with item 11").
- Out of scope: changes to `references/prompts/sarcastic.md`, checklists, or any other K1–K5 component.

## 5. Open Questions
- None. Scope is fixed by the audit backlog P0 items and the user's request.

## 6. Status
- [x] Phase 1: TASK drafted + Meta-Audit Mode A APPROVED (`docs/reviews/framework-audit-068.md`)
- [x] Phase 2: PLAN drafted + Meta-Audit Mode B APPROVED
- [x] Phase 3: Backup → Edits (§7 C-05, §3+§5 C-15, v1.1→1.2) → Verification gate green (validator pass; stale-grep zero hits repo-wide; minimal-diff confirmed; skill gate 43/43)
- [x] Phase 4: CHANGELOG v3.19.2 (EN+RU) + README headers bumped; full review pipeline green (Code Reviewer APPROVED · Security Auditor PASS, 0 findings)
