# Development Plan: Task 077 — R3c Tier-Diverse Escalation

> Mode B gates this plan. Architecture: untouched (rule text + config parsing in existing workflow). Release: v3.20.7.

## Step 0 — Backup
```bash
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done
cp .agent/workflows/vdd-multi.md                                              .agent/archive/vdd-multi.md.bak
cp .agent/skills/skill-parallel-orchestration/SKILL.md                        .agent/archive/parallel-orchestration-SKILL.md.bak
cp .agent/skills/skill-parallel-orchestration/references/sequential-fallback.md .agent/archive/sequential-fallback.md.bak
cp .agent/skills/skill-parallel-orchestration/references/claude-code.md       .agent/archive/claude-code.md.bak
cp .agent/skills/skill-parallel-orchestration/examples/usage_example.md       .agent/archive/usage_example.md.bak
```
Rollback layer 2: git (tree clean at `1918af6` for framework files).

## Step 1 — Gradation table + rule-3 third bullet (R1, lockstep)
The gradation table goes into **SKILL §6** (canonical) and is referenced from **vdd-multi Phase 2**. Rule 3 gains a third bullet (tier-diverse +1 for CRITICAL/HIGH, tag `tier-diverse`) inserted between the same-mechanism (R3a) and different-mechanism (R3b) bullets. Existing R3a/R3b bullets byte-unchanged. Lockstep: the new bullet + table identical in both files modulo critics↔teammates.

## Step 2 — Config parsing (R2, R3)
- Phase 0 step 5: parse `--models=logic:<t>,security:<t>,performance:<t>` (validate tiers ⊂ {haiku,sonnet,opus,fable}; partial OK; unset → default opus). Step 6: env-guard — if `CLAUDE_CODE_SUBAGENT_MODEL` set AND `--models` present → warn + set run flag `escalation_tier=R3a` (flattened).
- Phase 1 Step 1.1: spawn each critic with its `--models` tier (or default); note env-flatten caveat.
- Params table: add `--models` row.

## Step 3 — Lockstep tails + version (R4, R5, R6)
- `sequential-fallback.md` merge step 3: append sentence — tier-diverse impossible in single-instance sequential mode, gradation N/A, stays never-escalate.
- `usage_example.md`: one line on the tier-diverse escalation case.
- `claude-code.md` Model-pin hygiene: cross-ref `--models` as the tier-ladder consumer.
- SKILL frontmatter 3.3→3.4 + §9 History entry (R3c tier-diverse done; cross-vendor still item 6).

## Step 4 — Gates
G1 `grep "tier-diverse"` = 5 surfaces + env-guard phrase; G2 normalized diff of rule-3 table (vdd-multi vs SKILL) → identical mod noun; G3 sweep 43/43; G4 pytest 30/30; G5 .md-only; G6 do-not-touch diff inspection (rules 1/2/4/5, R3a/R3b/R3d text, evidence block, flags).

## Step 5 — Finalization (R7)
CHANGELOG EN+RU v3.20.7 → README×2 → roadmap (item 7: R3c tier-diverse ✅, cross-vendor ⏳ item 6; Dependencies line) → framework-audit-077.md → session-state.

## Rollback
| Failure | Action |
|---|---|
| Gate fail | restore `.bak` / `git checkout`, re-run |
| Lockstep diff mismatch | re-derive the shared block, re-apply both copies from one source |
