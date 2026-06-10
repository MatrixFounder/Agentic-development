# Framework Audit 076 — Post-Experiment Repositioning + Corpus Documentation

- **Task:** 076 `post-experiment-repositioning` · **Workflow:** `/framework-upgrade` · **Meta-skill:** `skill-self-improvement-verificator` (Modes A+B)
- **Date:** 2026-06-10 · **Release:** v3.20.6 · **Evidence base:** `docs/reviews/ab-experiment-075.md` (pre-registered rules 1–3)

## Mode A — SPECIFICATION AUDIT — **PASS**
Root integrity ✅ (RTM R1–R7 atomic, doc-only); skill compatibility ✅ (no new agents, TIER 0 intact); documentation ✅ (R7; `.AGENTS.md` written under Developer single-writer rule); migration ✅ (G1 stale-disclaimer grep).

## Mode B — PLAN AUDIT — **PASS**
Verification ✅ (G1–G5); rollback ✅ (3 file `.bak` + bootstrap + git layer); atomic ✅ (per-file steps); test coverage ✅ (doc-only, suites as regression — precedent 070–074).

## Gates
- **G1:** `grep "awaits the pre-registered"` over `.agent/ .claude/ System/` (excl. archive/sessions) → **empty**.
- **G2:** `git diff vdd-multi.md` touches **0** lines of merge rules 1–5 / enum / flags / Phase 1.0 evidence step — only the new Positioning block (+8 lines).
- **G3:** skill sweep **43/43**. **G4:** pytest security-audit **30/30**. **G5:** framework diff = `vdd-multi.md`, `vdd-adversarial/SKILL.md`, `vdd-sarcastic/SKILL.md` only (.md).

## Deliverables
| # | Artifact | Note |
|---|---|---|
| 1 | `tests/fixtures/ab-corpus/README.md` (EN) + `README.ru.md` (RU) — cross-linked pair, repo convention | 10 глав: что за тест (seeded-bug бенчмарк + pre-registration) · зачем (2 убеждения, аудит 067, 3 зависевших решения) · принцип работы (4 механизма, таблица изоляции переменных, обоснование ±3/класс/N=3/+10pp) · mermaid-пайплайн · результаты + unicode-бар-чарты · вердикты · расшифровка · ограничения · **как повторить (6-шаговая процедура воспроизведения + бюджет)** · карта артефактов. Описательная часть расширена по запросу оператора через `/text-humanizer` (genre=science/technical, triple-pass verification) |
| 2 | `tests/fixtures/ab-corpus/.AGENTS.md` (NEW) | все python-модули (f1–f8 с ролями багов, c1–c2, build_ground_truth.py, analyze.py) + все артефакты данных + инварианты печати |
| 3 | `vdd-multi.md` Positioning block | rule 2: coverage/CI tool, не дефолт; single-strong-reviewer default; R3c как оставшийся рычаг |
| 4 | `vdd-adversarial` 1.4→**1.5** | rule 3: precision tool, not recall lever (−6.9pp recall / −16% FP / 3.9% vs 13.0% bikeshedding) |
| 5 | `vdd-sarcastic` 1.4→**1.5** | rule 1: disclaimer "awaits" → resolved **KEPT** (+4.2pp vs B at lower FP; plain baseline still above both skins) |
| 6 | Roadmap item 13 follow-ups → done; CHANGELOG EN+RU v3.20.6; README×2 headers | — |

## Judgment calls
1. README written in Russian (explicit operator request «доступным языком»; EN technical report exists at ab-experiment-075.md — cross-linked).
2. `System/Docs/WORKFLOWS.md:148/422` reviewed, **not edited**: rows describe mechanics/coverage ("Maximum code quality (3 parallel critics)" = max-coverage quick-pick), no recall claim contradicting rule 2; flagged here for operator awareness.
3. K1 note placed in §2 (VDD Methodology Context) after Key Principles — the positioning is methodology-level, not a Red-Flag/termination change; exit bars untouched.

## Verdict
**APPROVED** — gates green, mechanics byte-identical, rollback layers intact. Uncommitted; operator to review and commit (working tree now carries: experiment 075 artifacts + this v3.20.6 cycle).
