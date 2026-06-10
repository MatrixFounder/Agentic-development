# Technical Specification: Verification Stack P2 "Aging" Batch — Items 8/9/10/12 (C-02, C-06, C-10, C-16)

### 0. Meta Information
- **Task ID:** 073
- **Slug:** `verification-p2-aging-batch`
- **Mode:** Framework Upgrade (meta-operation — doc-level edits to 4 Tier-2 skills, 1 skill reference, 3 critic wrappers, 1 workflow file; zero script/code changes)
- **Type:** P2 modernization batch, roadmap items **8, 9, 10, 12** — the roadmap's own suggested cycle (6) "items 8/9/10/12 batched". Closes audit-067 claims **C-02** (fresh-context rationale), **C-06** (model-pin hygiene), **C-10** (regex-as-floor positioning), **C-16** (perf-critic termination drift).
- **Workflow:** `/framework-upgrade` (with `skill-self-improvement-verificator` gate, Modes A + B).
- **Source:** User request (2026-06-10): "выполни 8, 9, 10, 12 — independent, small из docs/verification_roadmap.md" + `docs/verification_roadmap.md` items 8/9/10/12 + `docs/reviews/verification-stack-currency-audit-067.md` (claims C-02, C-06, C-10, C-16).

## 1. General Description

Four independent, small P2 items, each replacing aged or drifted framework text with current, evidence-grounded wording. **No practice changes** — in all four cases the *behavior* stays (fresh context stays mandatory, critics stay pinned, regex scanner stays, perf critic still terminates); only the *rationale/contract text* is modernized.

### Item 8 [C-02] — Re-ground the fresh-context rationale
The mandate "fresh context per adversarial review" is justified by the anthropomorphic "relationship drift / AI becoming too agreeable over time" story. Documented mechanisms replace it: **multi-turn context interference + assumption lock-in** (−39% multi-turn vs single-turn, arXiv:2505.06120), **context rot** (Chroma 2025), **pushback-driven sycophantic belief updates** (TRUTH DECAY / SYCON-Bench). Practice unchanged — fresh context per review stays mandatory (it scored Current in audit-067).
**Blast radius (grep, 2026-06-10):** 4 locations carry "relationship drift": `vdd-adversarial/SKILL.md:25`, `vdd-sarcastic/SKILL.md:28`, `vdd-adversarial/references/vdd-methodology.md:23`, **plus `.agent/workflows/vdd-adversarial.md:19`** (not in the roadmap's file list; required for the grep-clean gate). "Entropy Resistance" wording: `vdd-methodology.md:46` only. (Roadmap's `vdd-sarcastic/SKILL.md:24` drifted to `:28` after task 071 — same line, new number.)

### Item 9 [C-06] — Model-pin hygiene for critic agents
All three critic wrappers pin `model: opus` with zero rationale, and nothing documents that (a) a `fable` tier exists **above** opus in the Agent-tool model enum, (b) `CLAUDE_CODE_SUBAGENT_MODEL` env **silently overrides** frontmatter pins, (c) an `effort` frontmatter field is available (audit-067), (d) Opus 4.7+ follows severity-threshold instructions literally (recall hazard). Work: new "Model-pin hygiene" section in `references/claude-code.md` + a 2-line pin-rationale comment in each wrapper's frontmatter + literalism audit of critic prompt surfaces.
**Literalism audit result (grep, 2026-06-10):** threshold-instruction grep over `.claude/agents/` + the 4 critic SOT skills → **empty** (071 already fixed the only offender). To be re-verified and recorded in the audit artifact.

### Item 10 [C-10] — Position regex layer as deterministic floor; name the LLM semantic pass
`security-audit/SKILL.md` presents §2 (script) and §3 (manual review) as siblings without an explicit model of *why both exist*. Add a compact two-layer methodology section: (1) **deterministic floor** — regex + external tools: reproducible, cheap, CI-gateable, categorically blind to semantic classes; (2) **LLM semantic pass** — long-context taint/logic review + semantic tool-description poisoning check (the class regex cannot catch — already honestly flagged in §3's MCP limitation note). Plus semgrep licensing footnote (Semgrep CE since Dec 2024; Opengrep fork as drop-in alternative) and frontier evidence as rationale (AIxCC, Big Sleep, Codex Security / Claude Code Security — full citations in audit-067 bibliography).
**Constraint:** existing §1–§7 numbering is referenced by other artifacts (roadmap, audit reports) — the new section is inserted as **§0** so no existing § number shifts.

### Item 12 [C-16] — Align skill-adversarial-performance termination with the objective bar
`skill-adversarial-performance/SKILL.md` "Termination Condition" (lines 75–80) still has the pre-065 subjective form ("all categories reviewed / remaining issues are micro-optimizations / developer addressed all real issues") while its own wrapper `critic-performance.md:13` already emits the 3-state convergence enum. Add the test-execution/evidence condition + the enum `clean-pass | issues-found | bikeshedding-only` so SKILL matches wrapper (and the vdd-multi convergence protocol). Evidence condition mirrors the 065 security pattern honestly: this critic has **no Bash** — evidence is supplied by the orchestrator or reported as `tests: NOT RUN`, never fabricated (full orchestrator-side contract is item 11, out of scope here).

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | Target file(s) | Roadmap | Verification |
|----|-------------|----------------|---------|--------------|
| R1 | Replace "relationship drift" rationale with the three documented mechanisms (lock-in −39% arXiv:2505.06120; context rot Chroma 2025; pushback-driven sycophantic updates TRUTH DECAY/SYCON); practice mandate unchanged. Version 1.2→1.3 | `.agent/skills/vdd-adversarial/SKILL.md` (§2 Context Resetting, line 25) | 8 | File read; grep G1; `validate_skill.py` |
| R2 | Same re-grounding, compact form pointing to vdd-adversarial references. Version 1.2→1.3 | `.agent/skills/vdd-sarcastic/SKILL.md` (§3 Process, line 28) | 8 | File read; grep G1; `validate_skill.py` |
| R3 | §II.3 Context Resetting re-grounded (with explicit retirement note for the pre-2026 anthropomorphic framing, no literal old token); §V.4 "Entropy Resistance" re-worded to name the documented mechanisms (old name kept in parens for traceability) | `.agent/skills/vdd-adversarial/references/vdd-methodology.md` (lines 23, 46) | 8 | File read; grep G1 |
| R4 | Workflow line "(no relationship drift)" → documented-mechanism wording (G1 completeness; outside roadmap's file list, found by blast-radius grep) | `.agent/workflows/vdd-adversarial.md` (line 19) | 8 | grep G1 |
| R5 | New section "Model-pin hygiene (audit-067 C-06)": fable tier above opus in the model enum; pin rationale (cost/latency; recall lever is reporting instruction, not tier); `CLAUDE_CODE_SUBAGENT_MODEL` silent override warning; `effort` field; severity-threshold literalism hazard + correct pattern ("report everything with confidence+severity, filter downstream" — same wording as item 5.1/071). Parent skill version 3.1→3.2 | `.agent/skills/skill-parallel-orchestration/references/claude-code.md` (+ `SKILL.md` frontmatter version only) | 9 | File read; `validate_skill.py` |
| R6 | 2-line frontmatter comment in each wrapper: why `model: opus` (not fable) + env-override caveat + pointer to claude-code.md section. No other wrapper changes | `.claude/agents/critic-logic.md`, `critic-security.md`, `critic-performance.md` | 9 | File reads; G4 |
| R7 | Literalism audit re-run and recorded: threshold-instruction grep over critic surfaces → expected empty; any hit = fix in this cycle | `.claude/agents/`, 4 critic SOT skills | 9 | G5 grep output in audit artifact |
| R8 | New §0 "Methodology — Two Layers": deterministic floor (reproducible/CI-gateable/semantically blind) vs LLM semantic pass (taint/logic/tool-description poisoning); frontier-evidence rationale (AIxCC, Big Sleep, Codex Security / Claude Code Security per audit-067 bibliography); semgrep CE (Dec 2024) + Opengrep footnote. §1–§7 numbering unshifted. Version 3.5→3.6 + title bump | `.agent/skills/security-audit/SKILL.md` | 10 | File read; `validate_skill.py`; G3 |
| R9 | Termination section → Objective Convergence: evidence condition (orchestrator-supplied or honest `tests: NOT RUN`, never fabricated — critic has no Bash) + 3-state enum `clean-pass \| issues-found \| bikeshedding-only`, byte-aligned with wrapper `critic-performance.md:13` enum semantics. Version 1.1→1.2 | `.agent/skills/skill-adversarial-performance/SKILL.md` (lines 75–80) | 12 | File read; G4; `validate_skill.py` |
| R10 | Release bookkeeping: CHANGELOG EN+RU **v3.20.4**; README EN+RU version-header bump (release convention per `3df62a2`); `System/Docs/SKILLS.md:87` security-audit row "v3.5"→"v3.6"; roadmap items 8/9/10/12 → ✅ DONE; audit artifact `docs/reviews/framework-audit-073.md`; session-state at phase boundaries | `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md`, `README.ru.md`, `System/Docs/SKILLS.md`, `docs/verification_roadmap.md`, `docs/reviews/framework-audit-073.md` | cold-session protocol | File reads |

## 3. Acceptance Criteria (Gates)

- **G1 (stale-rationale grep-clean):** `grep -rn "relationship drift" .agent/ .claude/ System/` and `grep -rni "too agreeable" .agent/ .claude/ System/` → **empty** (scope excludes `.agent/archive/` rollback copies + `.agent/sessions/` runtime state, per 071/072 precedent; `docs/` history/audit files immutable by design).
- **G2 (skill quality gate):** `validate_skill.py` pass on all 5 touched skills (vdd-adversarial, vdd-sarcastic, skill-parallel-orchestration, security-audit, skill-adversarial-performance); full sweep across `.agent/skills/*/` = **43/43** (baseline).
- **G3 (regression evidence):** `python3 -m pytest .agent/skills/security-audit/tests/ -q` = **30/30** (doc-only change; suite run as no-regression proof that §0 insertion broke nothing the scripts parse).
- **G4 (wrapper↔SKILL consistency):** the 3-state enum string in `skill-adversarial-performance/SKILL.md` matches `critic-performance.md:13` (`clean-pass | issues-found | bikeshedding-only`); all 3 wrappers carry the model-pin comment; wrapper bodies otherwise unchanged (diff inspection).
- **G5 (literalism audit recorded):** threshold-instruction grep (`only (report|flag) (high|critical)|report only|skip (low|minor)…`) over `.claude/agents/` + critic SOT skills → output (expected empty) pasted into `framework-audit-073.md`.
- **G6 (no behavior change):** zero edits under any `scripts/` directory; `git diff --stat` shows only `.md` files.

## 4. Out of Scope (considered and excluded — with reasons)

1. **Item 11** (orchestrator-supplies-evidence contract in vdd-multi Phase 1) — roadmap pairs it with item 7/R3c, not this batch; R9's evidence condition references the *critic-side* honesty rule only (already established by 065/P0-item-2 for security).
2. **Item 7/R3c** (tier-diverse per-critic model config) — claude-code.md's new section *mentions* tier-diversity as the revisit path but does not implement config parsing; R3c stays ⏳/🔜 per roadmap.
3. **`vdd-multi.md`, `sequential-fallback.md`, merge rules** — untouched (072 territory; do-not-touch discipline).
4. **`SKILLS.md:53` stale "Mock Runner for POC" row** — pre-existing drift flagged in 072, unrelated to items 8/9/10/12; re-flagged, not fixed (scope discipline).
5. **Scanner scripts/patterns** (`scripts/audit/*`) — item 10 is methodology-text only; the MCP limitation note in §3 already carries the honest-floor language (069).
6. **`docs/reviews/verification-stack-currency-audit-067.md`** — immutable audit history quoting old wording; excluded from G1 scope by design.

## 5. Open Questions
None. All four items pre-specify files, mechanisms, and citations in the roadmap; judgment calls recorded: (a) workflow file `vdd-adversarial.md:19` added to item-8 scope for G1 completeness; (b) security-audit insertion as §0 to keep §1–§7 stable; (c) "Entropy Resistance" renamed with old name in parens (traceability, not in any grep gate); (d) R9 keeps critic-side `NOT RUN` honesty form, deferring the orchestrator-side contract to item 11.
