# Development Plan: Task 076 — Post-Experiment Repositioning + Corpus Docs

> Mode B gates this plan. Architecture: untouched (positioning text + docs). Release: v3.20.6 (doc-level patch).

## Step 0 — Backup
```bash
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done
cp .agent/workflows/vdd-multi.md                .agent/archive/vdd-multi.md.bak
cp .agent/skills/vdd-adversarial/SKILL.md       .agent/archive/vdd-adversarial-SKILL.md.bak
cp .agent/skills/vdd-sarcastic/SKILL.md         .agent/archive/vdd-sarcastic-SKILL.md.bak
```
Rollback layer 2: git (рабочее дерево несёт только незакоммиченные артефакты 075/076; framework-файлы чисты на HEAD).

## Step 1 — Corpus docs (R1, R2; новые файлы, без gate-влияния)
1.1 `tests/fixtures/ab-corpus/README.md` (RU): зачем → как (seal → армы → frozen scorer) → mermaid-схема пайплайна → таблица результатов → unicode-бар-чарты (recall / FP / токены) → расшифровка по армам → 3 вердикта → нюансы → ограничения → ссылки (EN-отчёт, analysis.json, протокол Appendix A).
1.2 `tests/fixtures/ab-corpus/.AGENTS.md`: разделы Purpose / Python modules (files/f1–f8 + роли багов, c1–c2, build_ground_truth.py, analyze.py) / Data artifacts (ground_truth, seal, scan_floor, scan_summary, analysis, results-layout, wallclock.log) / Invariants (sealed corpus — re-seal + discard runs при любом изменении).

## Step 2 — Repositioning (R3–R5, atomic per file)
2.1 vdd-multi.md: вставить "## Positioning (evidence: ab-experiment-075)" между интро и ## Invocation. Механика/флаги/фазы не трогаются (G2).
2.2 vdd-adversarial SKILL §2: evidence-note (precision tool; цифры правила 3; ссылка на отчёт); version 1.4→1.5.
2.3 vdd-sarcastic :19 хвост дисклеймера → resolved-KEPT формулировка; version 1.4→1.5.

## Step 3 — Gates
G1 stale-grep → empty; G2 diff vdd-multi.md = только Positioning-блок; G3 sweep 43/43; G4 pytest 30/30; G5 git diff --stat = .md only.

## Step 4 — Finalization (R6, R7)
Roadmap (item 13 Follow-ups → done) → CHANGELOG EN+RU v3.20.6 → README×2 header → framework-audit-076.md → session-state.

## Rollback
| Failure | Action |
|---|---|
| Gate fail | restore `.bak` / `git checkout -- <file>`, re-run gates |
| Systemic | workflow §5 Fallback: restore all `.bak` |
