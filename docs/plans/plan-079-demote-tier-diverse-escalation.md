# Development Plan: Task 079 — Demote Tier-Diverse Escalation

> Mode B gates this plan. Architecture: untouched. Release: v3.20.8 (doc-level correction).

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
Rollback layer 2: git (tree clean at `01a657a` for framework files).

## Step 1 — Demote rule 3 (R1, R2, lockstep)
Canonical edit in SKILL §6, mirrored byte-identically (mod critics↔teammates) into vdd-multi Phase 2:
- **Gradation table middle row:** `+1 for CRITICAL/HIGH only, tag tier-diverse (R3c — pilot)` → `no escalation — tier-diverse tag only (R3c escalation refuted by mini-exp 078: agreement precision 0.73→0.66; config kept for recall)`.
- **Third bullet:** tier-diverse same-mechanism → tag `tier-diverse`, severity = max (rule 1), **no +1**; replace the pilot/escalation wording with the 078-refutation note. Bullet remains (documents the config) but is now a tag, not an escalation.
- R3a bullet and R3b bullet byte-unchanged.

## Step 2 — Config retained, tier resolution simplified (R3)
- `--models` flag row, Phase 0 parse, Phase 1 per-critic spawn: **unchanged**.
- Phase 0 step 5 escalation-tier resolution: `tier-diverse` now resolves to tag-only; reword so it no longer promises a CRITICAL/HIGH bump. Env-flatten guard: keep the warning (model-identity correctness) but drop the "never award the +1" framing (no +1 to award) → reword to "downgrade tag to same-model `corroborated`".

## Step 3 — Cross-refs + version (R4, R5)
- `usage_example.md`: drop "tier-diverse escalation" from the merge walkthrough; keep the different-mechanism +1; note tier-diverse is a tag (078).
- `claude-code.md` Model-pin hygiene: reword the `--models` consumer note — recall tool, escalation demoted (078).
- `sequential-fallback.md`: the tier-diverse-impossible note stays (still true); no escalation change needed there.
- SKILL 3.4→3.5 + §9 History entry.

## Step 4 — Gates
- G1: `grep -rn "tier-diverse" .agent/` present; `grep -rniE "escalat.*tier-diverse|tier-diverse.*(\+1|escalat)" .agent/` → empty; 078 citation in vdd-multi + SKILL.
- G2: normalized rule-3 diff (vdd-multi vs SKILL) identical mod noun.
- G3: sweep 43/43; pytest 30/30; `.md`-only.
- G4: R3a/R3b/R3d, dedup, rules 2/4/5, evidence contract, `--models` definition byte-unchanged (diff inspection).

## Step 5 — Finalization (R6)
CHANGELOG EN+RU v3.20.8 → README×2 → roadmap (item 7 R3c tier-escalation resolved/demoted, cross-vendor ⏳ item 6) → framework-audit-079.md → session-state.

## Rollback
| Failure | Action |
|---|---|
| Gate fail | restore `.bak` / `git checkout`, re-run |
| Lockstep mismatch | re-derive shared block, re-apply both copies from one source |
