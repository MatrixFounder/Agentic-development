# Technical Specification: Post-Experiment Repositioning + Corpus Documentation (rules 2/3 of ab-experiment-075)

### 0. Meta Information
- **Task ID:** 076
- **Slug:** `post-experiment-repositioning`
- **Mode:** Framework Upgrade (meta-operation — 1 workflow file, 2 Tier-2 skills, roadmap; plus 2 new documentation artifacts in `tests/fixtures/ab-corpus/`)
- **Type:** Follow-up cycle mandated by experiment 075's pre-registered decision rules 2/3 (`docs/reviews/ab-experiment-075.md`) + corpus documentation (README with infographics + `.AGENTS.md`).
- **Workflow:** `/framework-upgrade` (verificator Modes A+B).
- **Source:** User request (2026-06-10): (1) README с инфографикой в tests/fixtures/ab-corpus — методология, принципы, расшифровка результатов, вердикт, доступным языком; (1b, добавлено сообщением пользователя) `.AGENTS.md` рядом — описание всех python-модулей и артефактов; (2) репозиционирование vdd-multi + K1 по правилам 2/3; (3) обновить roadmap.

## 1. General Description

Experiment 075 produced three mechanical verdicts. Rule 1 (sarcasm survives → K2 kept) needs only a disclaimer refresh — the old text still says the decision "awaits" the A/B. Rules 2/3 mandate repositioning text: **vdd-multi** is не дефолт, а инструмент покрытия/CI (D: +5.6pp < +10pp bar, FP хуже, 3.25× токенов — но единственный 100% pooled recall); **K1 (vdd-adversarial)** — инструмент точности, не полноты (B−A = −6.9pp recall, FP −16%, bikeshedding 3.9% vs 13.0%). Никакие механики не меняются — только позиционирующий текст с цитатой на отчёт. Плюс два документационных артефакта в корпусе эксперимента.

## 2. RTM

| ID | Requirement | Target file(s) | Verification |
|----|-------------|----------------|--------------|
| R1 | README (RU, доступный язык) в корпусе: зачем эксперимент, методология (seal-before-run, 5 армов, N=3, frozen scorer), инфографика (mermaid-пайплайн + unicode-бар-чарты recall/FP/токены), детальная расшифровка таблиц, три вердикта + честные нюансы, ссылки на EN-отчёт/analysis.json | NEW `tests/fixtures/ab-corpus/README.md` | file read; renders in VSCode preview |
| R2 | `.AGENTS.md` в корпусе: назначение каталога; каждый python-модуль (build_ground_truth.py, analyze.py, files/f1–f8 с ролью посеянных багов, files/c1–c2 контроли) и каждый артефакт (ground_truth.json, seal.json, scan_floor.json, scan_summary.txt, analysis.json, results/-layout, wallclock.log) с однострочным описанием + предупреждение «корпус запечатан — не редактировать без re-seal» | NEW `tests/fixtures/ab-corpus/.AGENTS.md` | file read |
| R3 | vdd-multi repositioning (rule 2): новый блок "Positioning (evidence: ab-experiment-075)" после интро — когда vdd-multi (CI `--fail-on`, coverage-critical: единственный арм 100% pooled, единственный f4-PER catch), когда single strong reviewer (дефолт для recall-задач: A=0.931 при 1/3.25 цены); существующие механики/флаги не тронуты | `.agent/workflows/vdd-multi.md` | file read; G2 |
| R4 | K1 repositioning (rule 3): evidence-note в §2 — precision tool, not recall lever (−6.9pp recall vs plain exhaustive; FP −16%; bikeshedding 3.9% vs 13.0%; N=3); для recall-critical pass — plain exhaustive baseline. Version 1.4→1.5 | `.agent/skills/vdd-adversarial/SKILL.md` | file read; validate_skill |
| R5 | K2 disclaimer refresh (rule 1): "awaits the pre-registered A/B" → resolved KEPT (rule 1: C−B=+4.2pp at lower FP; полный порядок recall всё же ставит plain baseline выше обоих скинов). Version 1.4→1.5 | `.agent/skills/vdd-sarcastic/SKILL.md:19` | G1 stale-grep empty |
| R6 | Roadmap: item 13 Follow-ups строка → repositioning DONE (Task 076); item 5/13 строки согласованы | `docs/verification_roadmap.md` | file read |
| R7 | Bookkeeping: CHANGELOG EN+RU v3.20.6, README EN+RU header, audit artifact `framework-audit-076.md`, session-state | стандартный набор | file reads |

## 3. Acceptance Criteria (Gates)
- **G1:** `grep -rn "awaits the pre-registered" .agent/ .claude/ System/` (excl. archive/sessions) → empty.
- **G2:** vdd-multi.md: merge rules 1–5, enum, флаги, Phase 1.0 evidence contract — byte-неизменны (diff inspection); добавлен только Positioning-блок.
- **G3:** skill gate 43/43; **G4:** pytest security-audit 30/30; **G5:** doc-only diff (.md only).

## 4. Out of Scope
WORKFLOWS.md:148/422 quick-pick rows («Maximum code quality (3 parallel critics)») — проверены: описывают coverage-механику, не recall-claim; не редактируются (флаг в аудит-артефакте). R3c pilot, vendor adapters (6) — отдельные циклы. Механики vdd-multi/K1 — не тронуты.

## 5. Open Questions
None. Формулировки позиционирования предписаны отчётом 075 (§Consequences); README/.AGENTS.md — документация без влияния на пайплайны.
