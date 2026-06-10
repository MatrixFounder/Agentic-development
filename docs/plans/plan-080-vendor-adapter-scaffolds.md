# Development Plan: Task 080 — Vendor Adapter Scaffolds 6a–6c

> Mode B gates. Architecture: untouched. Release: v3.20.9. Vendor primitives verified vs primary docs (TASK §1).

## Step 0 — Backup
```bash
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done
cp .agent/skills/skill-parallel-orchestration/SKILL.md                   .agent/archive/parallel-orchestration-SKILL.md.bak
cp .agent/skills/skill-parallel-orchestration/references/gemini-cli.md   .agent/archive/gemini-cli.md.bak
cp .agent/skills/skill-parallel-orchestration/references/cursor.md       .agent/archive/cursor.md.bak
```
New files (codex-cli.md, 9 wrappers) need no backup. Rollback: git (clean at `7d09d86`).

## Step 1 — References (R1–R3)
Each structured like `claude-code.md`: header + ⚠️ scaffold banner → "Loads with" → Runtime primitives table (concept→vendor primitive) → Layer A pattern (or honest gap) → Layer B note → tools/read-only mechanism → wrapper catalog → validation-gate reminder → See also. Content from TASK §1 (primary-source verified). Gemini: explicit Layer-A-unconfirmed gap. Codex/Cursor: parallel confirmed.

## Step 2 — Detection table (R4)
SKILL §1.1: add row `.codex/ directory present | references/codex-cli.md | Scaffold — documented (primary), not yet validated`. Reword Gemini/Cursor status cells to "Scaffold — documented, not validated" (+ Gemini "Layer A unconfirmed"). Keep first-match-wins ordering (CLAUDE.md first → Claude precedence preserved).

## Step 3 — Wrappers (R5) — 9 thin files at real paths
Model on `.claude/agents/critic-logic.md` (~14 lines): point to SOT skill, scope note, structured-return + convergence enum. Per vendor format:
- `.gemini/agents/critic-{logic,security,performance}.md` — MD+YAML frontmatter `name/description/tools:[read,grep,glob]/model`.
- `.codex/agents/critic-{logic,security,performance}.toml` — TOML `name/description/developer_instructions/sandbox_mode="read-only"`.
- `.cursor/agents/critic-{logic,security,performance}.md` — MD+YAML `description/model/readonly:true`.
Each body: SOT skill path + 3-state enum + ⚠️ scaffold line.

## Step 4 — Version + gates (R6, then G1–G5)
SKILL 3.5→3.6 + §9 entry. Gates: scaffold-banner grep; detection-table Codex row; validate_skill 43/43; Codex TOML parse; pytest 30/30; diff scope; honesty checks (Gemini gap stated, item 6 not ✅).

## Step 5 — Finalization (R7)
CHANGELOG EN+RU v3.20.9 → README×2 → roadmap item 6 (6a–6c scaffolds authored ✅, validation+6d+6e 🔜) → framework-audit-080.md → session-state.

## Rollback
| Failure | Action |
|---|---|
| Gate fail | fix forward / restore `.bak` / `rm` new files / `git checkout` |
| TOML parse fail | fix wrapper syntax, re-check |
