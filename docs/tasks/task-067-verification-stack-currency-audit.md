# Technical Specification: Verification Stack Currency Audit (VDD adversarial + security components vs mid-2026 LLM capabilities)

### 0. Meta Information
- **Task ID:** 067
- **Slug:** `verification-stack-currency-audit`
- **Mode:** Framework Audit (research/meta-operation — **read-only** with respect to all audited components)
- **Type:** Obsolescence & effectiveness audit. No framework component is modified in this cycle; remediation is a follow-up backlog.
- **Workflow:** `/vdd-start-feature` (Analysis + Architecture) + in-session audit execution (user-approved scope extension).
- **Source:** User request (2026-06-10): analyze `vdd-adversarial`, `vdd-sarcastic`, `vdd-multi`, `System/Agents/10_security_auditor.md`, `.agent/skills/security-audit` — how outdated are they relative to current LLM capabilities (Claude, Gemini, ChatGPT, etc.)? Do they perform at a top-notch level and do they actually deliver better results?

## 1. General Description

The framework's verification stack encodes falsifiable claims about LLM behavior (sycophancy, politeness filters, "relationship drift"), about the threat landscape (OWASP versions, MCP/agentic threats), and about its own effectiveness ("the Roast catches more bugs"). These claims were written across Dec 2025 – May 2026 against the model generation available then. This audit treats the five components **as claims, not files**: every load-bearing claim is extracted, anchored (file:line), graded against current (mid-2026) external evidence, and rolled up into per-component verdicts plus a prioritized modernization backlog.

**Audited components (K1–K5):**

| ID | Component | Canonical sources | Version |
|----|-----------|-------------------|---------|
| K1 | vdd-adversarial | `.agent/skills/vdd-adversarial/` (SKILL.md + references/vdd-methodology.md + assets) + `.agent/workflows/vdd-adversarial.md` | v1.1 |
| K2 | vdd-sarcastic | `.agent/skills/vdd-sarcastic/SKILL.md` | v1.1 |
| K3 | vdd-multi | `.agent/workflows/vdd-multi.md` + `.claude/agents/critic-{logic,security,performance}.md` + `.agent/skills/skill-adversarial-{security,performance}/` + `skill-parallel-orchestration` | v3.19.0 |
| K4 | Security Auditor role | `System/Agents/10_security_auditor.md` | v3.6.0 |
| K5 | security-audit skill | `.agent/skills/security-audit/` (SKILL.md + scripts/run_audit.py + references/checklists/) | v3.3 |

**Explicitly out of scope:** the Objective Convergence exit-bar design itself (hardened 2026-05-29 in v3.18.0/v3.19.0; audited then via `docs/reviews/framework-audit-065/066.md`). Only **residuals contradicting** that hardening are in scope. Live cross-vendor runs (Gemini CLI / Cursor / Codex) and executing the A/B experiment are out of scope (user decision 2026-06-10).

## Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features |
|----|-------------|------|--------------|
| R1 | **Claims Register**: extract all load-bearing claims from K1–K5 with file:line anchors | Yes | (a) seed register C-01…C-14 from exploration; (b) re-grep every anchor at v3.19.1 to confirm validity; (c) extend to completeness (~15–20 claims) by re-reading the 5 components; (d) classify each claim by dimension (D1 behavioral-assumption, D2 capability-leverage, D3 threat-currency, D4 cross-vendor, D5 effectiveness-evidence, D6 internal-consistency) |
| R2 | **External research** answering RQ1–RQ7 with dated sources | Yes | (a) RQ1 rude/persona prompting effectiveness 2025–26; (b) RQ2 sycophancy in current frontier models + whether tone-fixable; (c) RQ3 "relationship drift" vs context-rot literature; (d) RQ4 multi-critic ensembles vs single strong reviewer, correlated-error problem; (e) RQ5 model/runtime currency (`model: opus` alias; Gemini/Codex/Cursor parallel-agent support); (f) RQ6 threat landscape — OWASP API successor, OWASP GenAI/agentic taxonomy, MCP security, tool-poisoning, slopsquatting; (g) RQ7 published evidence for adversarial-review pipelines. Evidence bar: peer-reviewed / vendor system cards / standards bodies primary; blogs secondary; access dates recorded |
| R3 | **Desk checks** (repo-only) | Yes | (a) tone-as-success-criterion residual grep across all 5 components; (b) capability-leverage gap map (tools whitelists vs the objective bar's "tests executed" requirement); (c) scanner coverage matrix: threat × {pattern / checklist-only / absent}; (d) vdd-multi cost model from design properties (3× opus + re-spawns) |
| R4 | **Scoring & report**: rubric-based verdicts, report in `docs/reviews/` | Yes | (a) per-claim verdict ∈ {Current, Aging, Outdated, Harmful} + orthogonal **Unsubstantiated** tag; (b) evidence grade per verdict ∈ {[R]epo, [W]eb, [I]nference}, no verdict on [I] alone, Harmful requires [R]+[W]; (c) component verdict = worst load-bearing claim, distribution shown; (d) report `docs/reviews/verification-stack-currency-audit-067.md` in framework-audit header format; (e) modernization backlog: Harmful→P0, Outdated→P1, Aging→P2, Unsubstantiated→P2-experiment, every item traceable to a claim ID |
| R5 | **Effectiveness answer + A/B experiment design** (design only — no execution) | Yes | (a) decompose stack into 5 separable layers (fresh context / second pass / role-specialized critics / forced negativity / sarcastic tone) and state evidence status per layer; (b) explicit "can conclude / cannot conclude" honesty section; (c) pre-registered experiment protocol: seeded-bug corpus (20–30 bugs, 6–8 files), 4 arms (plain / adversarial / sarcastic / vdd-multi `--no-fix`), metrics (recall, FP count, bikeshedding ratio, tokens, wall-clock), decision rules fixed before any run |

## 2. Use Cases

### 2.1 UC-1: Maintainer assesses verification-stack currency (main)
**Actors:** Framework maintainer (user); Orchestrator agent (auditor).
**Preconditions:** Framework at v3.19.1, clean working tree; web research tools available.
**Main scenario:**
1. Auditor builds the Claims Register (R1) and validates anchors against the working tree.
2. Auditor runs the research sweep (R2), recording sources + access dates.
3. Auditor runs desk checks (R3).
4. Auditor scores claims per rubric (R4a–c), writes the report (R4d) with the backlog (R4e) and effectiveness section (R5).
5. Maintainer reads per-component verdicts K1–K5 and the direct answers to the three original questions.
**Alternative A1 — contradictory evidence:** sources conflict on a claim → verdict records both sides, grade capped at the weaker class, claim flagged for the experiment backlog instead of forcing a verdict.
**Alternative A2 — research tool unavailable/poor results:** claim scored on [R] facts only, tagged Unsubstantiated where [W] was required; never silently downgraded to [I]-only.
**Postconditions:** Report exists in `docs/reviews/`; TASK.md acceptance boxes checked; session state = `audit-complete`; zero framework components modified.
**Acceptance criteria:**
- ✅ Every claim in the register has a valid file:line anchor at v3.19.1.
- ✅ Every RQ has ≥1 primary-class source with access date, or an explicit "no evidence found" note (which is itself a finding for RQ7).
- ✅ No verdict rests on [I] alone; every Harmful verdict cites [R]+[W].
- ✅ Report sections: Meta / Methodology / Claims Register / Scorecards K1–K5 / Effectiveness / Experiment protocol / Backlog / Bibliography.
- ✅ Backlog items each trace to ≥1 claim ID with priority mapped from verdict.

### 2.2 UC-2: Follow-up modernization (out of scope, enabled by this task)
**Actors:** Maintainer; future `/vdd-start-feature` cycle.
**Scenario sketch:** Maintainer picks P0/P1 backlog items → new TASK cycle (subject to `skill-self-improvement-verificator` gate, since those edits touch framework components). This task must leave the backlog precise enough that each P0/P1 item is directly convertible into an Epic/Issue.

## Epics & Issues (audit execution plan)

### Epic E1 — Claims Register (→ R1)
- **E1-1.** Validate seed claims C-01…C-14 anchors by grep at HEAD.
- **E1-2.** Re-read K1–K5 sources; extend register to completeness (~15–20 claims); assign dimensions D1–D6.

### Epic E2 — External research sweep (→ R2)
- **E2-1.** RQ1+RQ2 (deep): sarcasm/forced-negativity justification vs 2025–26 politeness/sycophancy research and vendor system cards.
- **E2-2.** RQ3+RQ4 (medium): context-degradation mechanism; ensemble-vs-single-reviewer and correlated errors.
- **E2-3.** RQ5 (medium): model alias currency, per-vendor parallel-agent support status.
- **E2-4.** RQ6 (deep): OWASP API successor status, OWASP GenAI agentic taxonomy, MCP security guidance, tool-poisoning/slopsquatting.
- **E2-5.** RQ7 (quick): published A/B evidence for adversarial-persona review; absence is a finding.

### Epic E3 — Desk checks (→ R3)
- **E3-1.** Tone-as-criterion residuals grep (known instance: `skill-adversarial-security/SKILL.md` §7 "snarky comment" termination).
- **E3-2.** Capability-leverage map: critic tool whitelists vs objective-bar obligations; no-Bash asymmetry.
- **E3-3.** Scanner coverage matrix (MCP / tool-poisoning / context-poisoning / slopsquatting / sandbox-escape × pattern/checklist/absent).
- **E3-4.** vdd-multi token/cost model (design-property estimate, no execution).

### Epic E4 — Scoring & deliverable (→ R4)
- **E4-1.** Score all claims per rubric; roll up K1–K5 scorecards.
- **E4-2.** Write `docs/reviews/verification-stack-currency-audit-067.md`.
- **E4-3.** Modernization backlog with claim-ID traceability and P0–P2 priorities.

### Epic E5 — Effectiveness & experiment (→ R5)
- **E5-1.** Five-layer decomposition with per-layer evidence status.
- **E5-2.** Can/cannot-conclude section (incl. why "3 real bugs caught" anecdotes are confounded).
- **E5-3.** Pre-registered A/B protocol appendix (design only).

### Pre-registered hypotheses (falsifiable; the audit may refute them)
- **H1:** "Sarcasm bypasses politeness filters" (C-01/C-03) is Outdated; "≥1 snarky comment" termination (C-05) is Harmful (contradicts v3.19 objective-bar doctrine).
- **H2:** Fresh-context practice (C-02) is Current in practice, Aging in stated mechanism (drift mis-attributed vs context interference).
- **H3:** Parallel role-scoped critique is Current; bare `model: opus` pin (C-06) is Aging; severity-escalation-on-agreement independence assumption (C-08) is Outdated reasoning.
- **H4:** K5 is most outdated in substance: methodology shape (regex+checklist-walking vs long-context agentic analysis) and coverage absences (C-11), even with Current OWASP web refs.
- **H5:** "Does it give better results?" = Unsubstantiated either way; the experiment protocol is the honest deliverable.

## 3. Non-functional Requirements
- **Read-only invariant:** zero edits to K1–K5 sources, `System/`, `.claude/agents/`, or any skill. Verified post-audit via `git status` (only `docs/TASK.md`, `docs/reviews/…-067.md`, `.agent/sessions/latest.yaml` and archive rotations may appear).
- **Reproducibility:** every web claim carries source + access date; every repo claim carries file:line.
- **Framework conventions:** report header format matches `docs/reviews/framework-audit-066.md`; session state persisted at each phase boundary.

## 4. Constraints & Assumptions
- Exploration findings from the planning phase (component inventories, version history, v3.18/v3.19 hardening scope) are trusted inputs; anchors are still re-verified (E1-1).
- Cross-vendor fallback verdict is capped at **Unvalidated** — no live non-Claude runs in this cycle.
- The A/B experiment is designed, not executed (user decision 2026-06-10).
- Knowledge-cutoff discipline: statements about "current" models/standards must come from live web sources, not model memory, wherever a [W] grade is claimed.

## 5. Open Questions
- None blocking. Scope questions (full audit now vs workflow-only; experiment design vs run) were resolved by the user on 2026-06-10: **full audit now; experiment design only**.

## 6. Status
- [x] E1 Claims Register complete, anchors valid (16 claims, all verified at v3.19.1 HEAD; 2 new claims C-15/C-16 found during validation)
- [x] E2 Research sweep complete (RQ1–RQ7, 3 parallel research agents, ~50 dated sources, access date 2026-06-10)
- [x] E3 Desk checks complete (1 tone residual; capability map; coverage matrix; cost model)
- [x] E4 Report + backlog written — `docs/reviews/verification-stack-currency-audit-067.md` (13 backlog items: 2×P0, 5×P1, 5×P2, 1×P2-experiment)
- [x] E5 Effectiveness section + pre-registered A/B protocol written (Appendix A; design only per user decision)
