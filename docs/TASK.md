# Technical Specification: Orchestrator-Supplies-Evidence Contract (C-13, roadmap item 11)

### 0. Meta Information
- **Task ID:** 074
- **Slug:** `orchestrator-supplies-evidence`
- **Mode:** Framework Upgrade (meta-operation — 1 workflow, 4 Tier-2 skill files, 1 reference; zero script/code changes)
- **Type:** P2 modernization, roadmap item **11**. Closes audit-067 claim **C-13** (critic capability asymmetry) and the **P0 item 2 residual** ("until item 11 lands, critic-security legitimately reports `scan: NOT RUN` on every `/vdd-multi` run"). Pre-requisite hardening for experiment 13 (removes arm D's known handicap).
- **Workflow:** `/framework-upgrade` (with `skill-self-improvement-verificator` gate, Modes A + B).
- **Source:** User request (2026-06-10): "выполни item 11 из docs/verification_roadmap.md" + roadmap item 11 + audit-067 claim C-13.

## 1. General Description

Critics (`tools: Read, Grep, Glob`) physically cannot execute tests or scanners, yet their shared exit bar requires "the full test run has actually been executed". Chosen direction (pre-specified in roadmap, consistent with P0 item 2): **the orchestrator supplies execution evidence** — it has Bash, runs the evidence commands *before* Phase-1 spawn, and injects results into every critic prompt. Critics treat supplied evidence as **input**; total absence of an evidence block → finding **"exit-bar condition unverifiable"**, never approval. Rejected alternative (per roadmap): granting critics Bash — widens attack/cost surface, breaks the read-only critic guarantee.

**Blast radius (greps, 2026-06-10):**
- Phase-1 prompt skeleton exists **only** in `vdd-multi.md:85-93` — no lockstep duplicates.
- Exit-bar condition "(1) the full test run has actually been executed" is a **3-location lockstep family** (065/066 discipline): `vdd-adversarial/SKILL.md:29`, `vdd-sarcastic/SKILL.md:32`, `vdd-methodology.md:38` — the critic-side parenthetical must land byte-identically in all three.
- Critic-side groundwork already present: `skill-adversarial-security` §3/§5/§7 (NOT RUN honesty + "orchestrator is responsible…", from 068) and `skill-adversarial-performance` Termination cond 1 (from 073). Each needs only the **absence-rule** clause.
- `sequential-fallback.md` "Concrete pattern" (3-critic VDD run, lines 67-89) has no evidence step — sequential path must stay flag/contract-equivalent.

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | Target file(s) | Verification |
|----|-------------|----------------|--------------|
| R1 | Phase 1 gains an **evidence-gathering step before spawn**: orchestrator runs the test suite (capture command + pass/fail summary; else `tests: NOT RUN (<reason>)`) and `run_audit.py` (JSON/summary; else `scan: NOT RUN (<reason>)`). Prompt skeleton extended with an `Execution evidence` block — tests evidence for **all** critics, scan evidence additionally for critic-security — plus the critic-side instruction: evidence is input, never re-run/fabricate; absent block → finding "exit-bar condition unverifiable", not approval | `.agent/workflows/vdd-multi.md` Phase 1 | File read; G1 |
| R2 | Phase 2 merged-report Summary records evidence state (`Evidence: tests=<…> · scan=<…>`); merge rules 1–5 untouched | `.agent/workflows/vdd-multi.md` Phase 2 | File read; diff |
| R3 | Fallback (Sequential) section: evidence gathered **once** before role-switching, injected into every persona pass; same absence rule. Flag-parity statement extended to the evidence contract | `.agent/workflows/vdd-multi.md` Fallback | File read; G1 |
| R4 | Exit-bar condition (1) extended with one **byte-identical** parenthetical in all 3 lockstep locations: executed by you, or via orchestrator-supplied execution evidence (critic/subagent mode); if neither — condition unverifiable → report as finding, never approve. Versions: vdd-adversarial 1.3→1.4, vdd-sarcastic 1.3→1.4 | `vdd-adversarial/SKILL.md:29`, `vdd-sarcastic/SKILL.md:32`, `references/vdd-methodology.md:38` | G2 normalized diff; `validate_skill.py` |
| R5 | Absence-rule clause added to existing critic-side groundwork: `skill-adversarial-security` §3 (one sentence; 1.3→1.4) and `skill-adversarial-performance` Termination cond 1 (one clause; 1.2→1.3) | both SKILL.md | File reads; G1 |
| R6 | Sequential-fallback concrete pattern gains evidence step 0 (orchestrator runs evidence commands first; injects into steps 1/3/5). Parent `skill-parallel-orchestration` 3.2→3.3 | `references/sequential-fallback.md`, parent SKILL.md frontmatter | File read; `validate_skill.py` |
| R7 | Bookkeeping: CHANGELOG EN+RU **v3.20.5**; README EN+RU header bump; roadmap item 11 → ✅ + P0 item 2 residual marked resolved + Dependencies line; audit artifact `docs/reviews/framework-audit-074.md`; session-state at boundaries | CHANGELOG×2, README×2, `docs/verification_roadmap.md`, audit artifact | File reads |

## 3. Acceptance Criteria (Gates)

- **G1 (contract grep):** `grep -rn "exit-bar condition unverifiable" .agent/` → present in exactly the contract surface (vdd-multi.md, 3 exit-bar locations, skill-adversarial-security, skill-adversarial-performance, sequential-fallback.md); `grep -n "Execution evidence" .agent/workflows/vdd-multi.md` → Phase 1 block present.
- **G2 (lockstep byte-consistency):** the new parenthetical in the 3 exit-bar locations is byte-identical (normalized diff in audit artifact).
- **G3 (skill gate):** `validate_skill.py` pass on the 4 touched skills; full sweep **43/43**.
- **G4 (regression):** pytest security-audit **30/30** (doc-only change).
- **G5 (doc-only):** `git diff --stat` — `.md` only, no `scripts/` paths.
- **G6 (do-not-touch):** merge rules 1–5, iteration caps, convergence enum, flags table — byte-unchanged (diff inspection).

## 4. Out of Scope

1. **Granting critics Bash** — rejected by roadmap (attack/cost surface, read-only guarantee).
2. **Critic wrappers `.claude/agents/critic-*.md`** — stay thin; the critic-side rule lives in SOT skills + the Phase-1 prompt the orchestrator composes (Wave-1/2 anti-drift discipline).
3. **R3c / per-critic model config** — separate item (blocked by 6).
4. **"Functionally equivalent" claim in the Fallback section** — item 6 (C-07) territory; not touched beyond the evidence sentence.
5. **`security-audit` workflow / `10_security_auditor.md`** — the full-audit path runs its own automation (auditor has Bash); contract unchanged there.

## 5. Open Questions
None. Direction, evidence items, and absence semantics are pre-specified in roadmap item 11. Judgment calls: (a) exit-bar parenthetical applied to all 3 lockstep copies (065/066 discipline), not just the critic SOT; (b) Phase-2 Summary evidence line added for report traceability (minimal, merge rules untouched); (c) sequential path gets the same contract to preserve path parity.
