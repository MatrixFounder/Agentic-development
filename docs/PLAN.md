# Development Plan: Task 073 — Verification Stack P2 "Aging" Batch (Items 8/9/10/12)

> **TASK:** `docs/TASK.md` (Task 073, slug `verification-p2-aging-batch`)
> **Workflow:** `/framework-upgrade` — Mode B PLAN AUDIT gates this plan before execution.
> **Architecture impact:** none — rationale/contract text inside existing skills, wrappers, one workflow line; no component/interface/data-model change → `docs/ARCHITECTURE.md` untouched (living document).
> **Release:** v3.20.4 (doc-level patch, follows v3.20.3 convention).

## Step 0 — Backup (rollback layer 1)

```bash
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done   # bootstrap files (workflow mandate; none are edited this cycle)
cp .agent/skills/vdd-adversarial/SKILL.md                                  .agent/archive/vdd-adversarial-SKILL.md.bak
cp .agent/skills/vdd-sarcastic/SKILL.md                                    .agent/archive/vdd-sarcastic-SKILL.md.bak
cp .agent/skills/vdd-adversarial/references/vdd-methodology.md             .agent/archive/vdd-methodology.md.bak
cp .agent/workflows/vdd-adversarial.md                                     .agent/archive/workflow-vdd-adversarial.md.bak
cp .agent/skills/skill-parallel-orchestration/references/claude-code.md    .agent/archive/claude-code.md.bak
cp .agent/skills/skill-parallel-orchestration/SKILL.md                     .agent/archive/parallel-orchestration-SKILL.md.bak
cp .claude/agents/critic-logic.md                                          .agent/archive/critic-logic.md.bak
cp .claude/agents/critic-security.md                                       .agent/archive/critic-security.md.bak
cp .claude/agents/critic-performance.md                                    .agent/archive/critic-performance.md.bak
cp .agent/skills/security-audit/SKILL.md                                   .agent/archive/security-audit-SKILL.md.bak
cp .agent/skills/skill-adversarial-performance/SKILL.md                    .agent/archive/adversarial-performance-SKILL.md.bak
```

Rollback layer 2: working tree was **git-clean** at cycle start (072 committed as `8296b04`) → `git checkout -- <file>` restores any file. Rollback procedure: restore `.bak` copies (workflow §5 Fallback) or `git checkout`; no session migration to undo.

## Step 1 — Item 8: re-ground fresh-context rationale (R1–R4)

Atomic edits, one file at a time; new wording cites the three documented mechanisms (assumption lock-in −39% arXiv:2505.06120 · context rot Chroma 2025 · pushback-driven sycophantic updates TRUTH DECAY/SYCON-Bench); the **mandate itself is byte-preserved in spirit: fresh context stays MUST**.

1.1 `vdd-adversarial/SKILL.md:25` — replace the Context Resetting bullet's "to prevent \"relationship drift.\"" tail with the mechanism list; frontmatter `version: 1.2` → `1.3`.
1.2 `vdd-sarcastic/SKILL.md:28` — same replacement, compact form + pointer to vdd-adversarial references; `version: 1.2` → `1.3`.
1.3 `vdd-methodology.md:23` (§II.3) — re-grounded long form + explicit retirement note ("pre-2026 anthropomorphic framing", **without** the literal old token — G1 must stay clean); `:46` (§V.4) — "Entropy Resistance" → "Context-Interference Resistance (formerly \"Entropy Resistance\")" + mechanism list.
1.4 `.agent/workflows/vdd-adversarial.md:19` — "(no relationship drift)" → "(avoids multi-turn assumption lock-in & context rot — audit-067 C-02)".

**Verify:** G1 greps (`relationship drift`, `too agreeable`) → empty in scope.

## Step 2 — Item 9: model-pin hygiene (R5–R7)

2.1 `references/claude-code.md` — insert section **"Model-pin hygiene (audit-067 C-06)"** (after "Tools whitelist note"): tier ladder (`haiku < sonnet < opus < fable` — fable **above** opus); why wrappers pin opus (cost/latency; recall lever = exhaustive-reporting instruction, not tier; revisit at R3c); `CLAUDE_CODE_SUBAGENT_MODEL` **silent override** warning (flattens tier-diverse configs); `effort` frontmatter field (audit-067); severity-threshold literalism hazard + the canonical pattern wording from item 5.1: *"report everything with confidence + severity attached; filter downstream"*.
2.2 `skill-parallel-orchestration/SKILL.md` — frontmatter `version: 3.1` → `3.2` (reference-file edit; no body change).
2.3 Each of `.claude/agents/critic-{logic,security,performance}.md` — add 2 comment lines above `model: opus` in frontmatter (pin rationale + env-override caveat + pointer); **no other wrapper change**.
2.4 Literalism audit re-run (G5 grep) — output recorded in audit artifact; any hit → fix immediately (expected: none).

**Verify:** file reads; G4 wrapper diff = comments only; G5 output captured.

## Step 3 — Item 10: two-layer methodology section (R8)

3.1 `security-audit/SKILL.md` — insert **"## 0. Methodology — Two Layers (audit-067 C-10)"** between the H1 title and §1 (keeps §1–§7 numbering stable): deterministic floor (regex+external: reproducible, cheap, CI-gateable, categorically blind to semantic classes — clean scan ≠ clearance) vs LLM semantic pass (long-context taint/logic review, business-logic authz, semantic tool-description poisoning per §3 limitation note); frontier evidence line (AIxCC finals 2025, Big Sleep, Codex Security / Claude Code Security — citations live in audit-067 bibliography); semgrep licensing footnote (Semgrep CE since Dec 2024; Opengrep fork = drop-in alternative).
3.2 Same file — title `# Security Audit v3.5` → `v3.6`; frontmatter `version: 3.5` → `3.6`.

**Verify:** §1–§7 headings byte-unchanged (diff); G3 pytest 30/30.

## Step 4 — Item 12: perf-critic termination alignment (R9)

4.1 `skill-adversarial-performance/SKILL.md:75–80` — replace "## Termination Condition" body with **Objective Convergence** form: (1) evidence condition — execution evidence supplied by orchestrator or honest `tests: NOT RUN` (critic has no Bash; never fabricate); (2) all 6 categories reviewed; (3) zero legitimate Critical/High findings; (4) only micro-optimizations/style remain. Append the 3-state signal line with enum `clean-pass | issues-found | bikeshedding-only` matching `critic-performance.md:13` semantics (incl. "NOT \"forced to invent problems\"" clause).
4.2 Frontmatter `version: 1.1` → `1.2`.

**Verify:** G4 — enum string identical to wrapper's; SKILL still passes `validate_skill.py`.

## Step 5 — Verification gates (all)

```bash
# G1 stale-rationale greps (expect empty)
grep -rn "relationship drift" .agent/ .claude/ System/ | grep -v ".agent/archive/" | grep -v ".agent/sessions/"
grep -rni "too agreeable"     .agent/ .claude/ System/ | grep -v ".agent/archive/" | grep -v ".agent/sessions/"
# G2 skill gate — 5 touched skills + full 43/43 sweep
python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/{vdd-adversarial,vdd-sarcastic,skill-parallel-orchestration,security-audit,skill-adversarial-performance}
for d in .agent/skills/*/; do python3 .agent/skills/skill-creator/scripts/validate_skill.py "$d"; done  # count PASS = 43
# G3 regression
python3 -m pytest .agent/skills/security-audit/tests/ -q   # 30/30
# G5 literalism grep (expect empty; paste into audit artifact)
grep -rniE "only (report|flag) (high|critical)|report only|skip (low|minor|medium)|ignore (low|minor)" .claude/agents/ .agent/skills/vdd-adversarial/ .agent/skills/vdd-sarcastic/ .agent/skills/skill-adversarial-performance/ .agent/skills/skill-adversarial-security/
# G6 doc-only proof
git diff --stat   # only .md files
```

No new tests: zero script changes (G6 enforces); existing suites run as regression evidence — same justification accepted in 070/071/072 (doc-only cycles).

## Step 6 — Documentation & finalization (R10)

6.1 `CHANGELOG.md` + `CHANGELOG.ru.md` — v3.20.4 entry (4 items, claims closed, versions bumped).
6.2 `README.md` + `README.ru.md` — version header bump (release convention per `3df62a2`).
6.3 `System/Docs/SKILLS.md:87` — security-audit row "v3.5:" → "v3.6:" (re-flag, not fix, the stale `:53` Mock-Runner row).
6.4 `docs/verification_roadmap.md` — items 8/9/10/12 → ✅ DONE with task/version/artifact refs; Dependencies block updated.
6.5 `docs/reviews/framework-audit-073.md` — audit artifact: Mode A + Mode B results, G1–G6 outputs, literalism-audit record, flagged-not-fixed list.
6.6 Session state update (phase boundary) — task completed status.

## Rollback plan

| Failure | Action |
|---|---|
| Any gate fails mid-execution | Fix forward if trivial (wording); else restore the affected file from `.agent/archive/*.bak` and re-run gates |
| Systemic instability | Workflow §5 Fallback: restore all `.bak` files; `git checkout -- .` as final layer (tree was clean at start) |
| validate_skill.py regression on a touched skill | Restore that skill's `.bak`, re-apply edit in smaller chunks |
