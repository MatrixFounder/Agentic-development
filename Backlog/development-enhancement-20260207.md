# Спецификация для доработки фреймворка Agentic-development: Улучшение workflows и добавление новых skills для предотвращения потери требований и достижения one-shot качества

## 0. Meta Information
- **ID:** SPEC-001
- **Slug:** framework-improvements-one-shot
- **Title:** Доработка workflows и добавление skills для детализации TASK/PLAN и минимизации итераций
- **Status:** Draft
- **Context:** На основе анализа артефактов TASK.md и PLAN.md из примера задачи "Task Manager MVP". Цель — интегрировать рекомендации из retrospective review (workflow changes и new skill ideas) для повышения качества первого прохода разработки. Используется в Antigravity с фокусом на Stub-First и VDD. Улучшения учитывают совместимость с существующими workflows, чтобы избежать путаницы (например, через режимы и флаги).
- **Version:** 1.1 (February 2026) — обновлено для совместимости с другими workflows и минимизации дублирования.

## 1. Problem Description
Текущий фреймворк генерирует полезные артефакты (TASK.md, PLAN.md), но страдает от проблем:
- Потеря или упрощение требований (например, subtasks, recurring tasks, tags/labels в исходном запросе не детализированы в Use Cases TASK.md).
- High-level планирование (PLAN.md группирует фичи, что приводит к defer в Developer phase).
- Open Questions в TASK.md (например, "one file strictness"), которые не разрешаются timely, вызывая итерации.
- Отсутствие жёстких checklists для verification, что позволяет "token-saving" поведение (скелет вместо polished кода).

**Цель доработки:** Сделать процесс более детализированным на early stages (Analysis/Planning), чтобы добиться production-ready результата с первого major цикла (one-shot, как в Claude Opus 4.6). Улучшения не должны "портить" core фреймворк — только добавления в .agent/skills/ и minor обновления prompts в System/Agents/ или workflows. Особый фокус на совместимости: новые элементы интегрируются в существующие workflows через режимы/флаги, чтобы избежать путаницы и дублирования команд.

**Ожидаемый эффект:** 
- TASK.md без Open Questions (все ambiguities resolved).
- PLAN.md с atomic checklists и edge cases.
- Минимизация итераций: 80–90% фич реализуется fully с первого Developer pass.
- Время на задачу: +5–10 мин на pre-planning, но -20–30 мин на fixes.
- Совместимость: новые режимы легко интегрируются в старые workflows без новых отдельных файлов.

## 2. Use Cases

### UC-01: Генерация улучшенного TASK.md в Analysis Phase
**Actors:** Analyst, Orchestrator
**Preconditions:** Исходный user prompt с требованиями.
**Main Scenario:**
1. Analyst парсит prompt.
2. Вызывает new skill-prompt-refinement для clarification.
3. Skill генерирует вопросы, классифицирует MVP/nice-to-have, удаляет Open Questions.
4. Обновляет TASK.md с refined Use Cases и без ambiguities.
**Alternative Scenarios:**
- Если Open Questions >0: skill паузит для user input (например, "Clarify: subtasks recursive or flat?").
**Postconditions:** TASK.md готов к Planning без пробелов.

### UC-02: Создание детализированного PLAN.md в Planning Phase
**Actors:** Planner
**Main Scenario:**
1. Planner читает TASK.md.
2. Вызывает skill-acceptance-criteria-parser для генерации checklists.
3. Интегрирует checklists в PLAN.md (atomic per phase/task).
4. Добавляет edge cases и verification steps.
**Postconditions:** PLAN.md с checkboxes, готов к VDD-pre-dev.

### UC-03: Verification во время/после Development
**Actors:** Developer, Reviewer
**Main Scenario:**
1. После phase в PLAN.md: вызывает skill-feature-completeness-check.
2. Skill сравнивает code vs checklists в TASK.md/PLAN.md.
3. Если coverage <95%: возвращает на Developer с list of gaps.
**Alternative Scenarios:**
- Post-full dev: блокирует commit до 100% coverage.
**Postconditions:** No "Done" без полной реализации.

## 3. Acceptance Criteria
- [ ] Новые skills созданы с помощью skill-creator и зарегистрированы в System/Docs/SKILLS.md.
- [ ] Workflow changes интегрированы в существующие prompts (System/Agents/) или workflows (.agent/workflows/) без удаления core логики и без создания дублирующих файлов (использовать режимы/флаги для совместимости).
- [ ] Тестирование: на примере "Task Manager" — TASK.md без Open Questions, PLAN.md с checklists для всех фич (включая subtasks), coverage check блокирует если drag&drop не persisted.
- [ ] Нет новых зависимостей; всё работает в Antigravity natively / совместимо с Cursor / Claude.
- [ ] Документация: обновить WORKFLOWS.md с новыми последовательностями (e.g., /vdd-enhanced теперь включает pre-dev skills) и таблицей сравнения режимов для избежания путаницы.
- [ ] Совместимость: новые режимы (pre-dev) работают как опции в существующих workflows; пользователь может переключаться ключевыми словами без новых команд.

## 4. Доработки Workflow Changes
На основе анализа: сделать PLAN.md более granular, VDD earlier, Stub-First stricter. Причины: high-level планы приводят к группам фич (как Phase 3 в примере), что defer polish; early VDD предотвратит это. Все изменения совместимы: интегрируются в существующие файлы через режимы/флаги, чтобы не плодить новые команды и избежать путаницы.

### 4.1 Изменение в Planning: от high-level file list к feature checklist с acceptance criteria
**Причина:** Текущий PLAN.md (e.g., "task-001.4-ux-enhancements" группирует theming/shortcuts/drag&drop) позволяет Developer упрощать; checklists force atomic breakdown и verification.
**Доработка:** В System/Agents/06_agent_planner.md добавить инструкцию в prompt. Совместимость: применяется во всех workflows без изменений.
**Пример обновлённого prompt snippet:**
```
Для PLAN.md:
- Для каждой фазы: генерируй нумерованный checklist с checkboxes из TASK.md Acceptance Criteria.
- Разбей групповые таски на sub-tasks (e.g., separate for theming, shortcuts, drag&drop).
- Включи edge cases (e.g., 'Drag&drop in filtered list persists after refresh').
- Verification steps: Пример: 'Run E2E test: open index.html, toggle theme, check localStorage'.
```
**Пример выходного PLAN.md (улучшенный для Task Manager):**
```
# Plan: Task Manager MVP
...
### Phase 3: Polish & UX
- [ ] **task-001.4.1-theming**
    - Goal: Implement light/dark toggle.
    - Checklist: - [ ] Toggle persists in localStorage; - [ ] CSS variables for colors; - [ ] Transition on switch.
    - Edge: Reload in dark mode.
    - Verification: Cmd+S saves, refresh keeps theme.
- [ ] **task-001.4.2-shortcuts**
    - Checklist: - [ ] Cmd+N adds task; - [ ] Cmd+D toggles complete; etc.
    - Edge: Shortcuts work on focused task.
...
```

### 4.2 Изменение в VDD: from post-implementation to after planning (pre-dev)
**Причина:** В примере Open Questions в TASK.md не решены timely; pre-dev VDD catches gaps early, предотвращая dev на incomplete плане.
**Доработка:** Обновить .agent/workflows/vdd-enhanced.md как "умный" workflow с режимами (по ключевым словам в запросе) для совместимости. Не создавать новые файлы — интегрировать в существующий, чтобы избежать путаницы. Orchestrator парсит запрос и ветвится (default — classic post-impl; pre-dev — новый режим).
**Пример workflow snippet (полный текст для .agent/workflows/vdd-enhanced.md):**
```
# Workflow: /vdd-enhanced (умный, с режимами для совместимости)

You are Orchestrator. Parse user command for mode to avoid confusion with other workflows.

Supported modes (detect from keywords in query, case-insensitive):
- default / enhanced → classic VDD-enhanced (Stub → Impl → VDD post-impl, как в оригинале)
- pre-dev / gated / plan-first / detailed-plan → new pre-dev mode (VDD after Planning, before Develop)
- adversarial / sarcastic → integrate adversarial loop (from /vdd-adversarial)
- multi → sequential multi-critic (from /vdd-multi)
- robust → full-robust (enhanced + security audit from /full-robust)

If no mode specified → default (classic) for backward compatibility.
If multiple modes → prioritize (e.g., pre-dev + adversarial → pre-dev with sarcastic review).

Execution flow:

IF mode includes pre-dev / gated / plan-first / detailed-plan:
1. Analysis → TASK.md (run prompt-refinement if ambiguities)
2. Planning → PLAN.md (with detailed checklists from 4.1)
3. VDD-pre-dev:
   - Run Sarcasmotron / Director (p03) on PLAN.md vs TASK.md + исходный prompt
   - Check: coverage of requirements? Open Questions? Edge cases covered?
   - If gaps (e.g., subtasks not in checklist) → return to Planner with specific feedback
   - If OK → proceed to Develop
4. Develop (strict Stub-First for ALL from 4.3)
5. Review + feature-completeness-check
6. Commit

ELSE IF mode == adversarial / sarcastic:
   - Fallback to /vdd-adversarial logic (adversarial loop during dev)

ELSE IF mode == multi:
   - Fallback to /vdd-multi logic (sequential critics)

ELSE IF mode == robust:
   - Fallback to /full-robust logic (enhanced + security)

ELSE (default):
   - Original VDD-enhanced logic: Analysis → Planning → Develop → VDD post-impl → Review

Alias integration: If user calls /vdd-enhanced-pre-dev or similar → treat as pre-dev mode.
This ensures compatibility: users can use old commands without changes, but add keywords for new behavior.
```
**Пример:** Для Task Manager — VDD выявит "recurring tasks not in PLAN" и force добавление sub-task. Вызов: "Start feature X in VDD enhanced pre-dev mode" → новый режим; "Start feature X in VDD enhanced" → classic.

### 4.3 Изменение в Developer: force stub-first for ALL features
**Причина:** В примере Phase 3 без stubs приводит к defer; strict Stub-First ensures polish не skipped.
**Доработка:** В System/Agents/08_agent_developer.md добавить правило в prompt. Совместимость: применяется во всех workflows.
**Пример prompt snippet:**
```
Для КАЖДОЙ фичи в PLAN.md checklist:
1. Stub + E2E test (even for UX: stub drag event with log).
2. Impl + polish (CSS transitions, edge handling).
NO skipping "because simple". Reference TASK.md Use Cases.
```
**Пример:** Для drag&drop — stub: "Log 'dragged'", test: "Console shows log"; impl: full HTML5 Drag API.

## 5. Добавление New Skills
На основе анализа: skills для parsing/resolution в TASK.md. Причины: automate clarification, enforce completeness. Добавлять как папки в .agent/skills/ — Antigravity подхватит. Совместимость: skills вызываются в любом workflow без конфликтов.

### 5.1 skill-acceptance-criteria-parser
**Причина:** Текущий Acceptance Criteria в TASK.md базовый; skill генерирует detailed checkboxes из Use Cases, resolving gaps (e.g., add for subtasks).
**Файл:** .agent/skills/acceptance-criteria-parser/SKILL.md
```
---
name: acceptance-criteria-parser
description: Extracts testable checkboxes from user prompt, BRD/TASK.md Use Cases. Resolves Open Questions by generating clarifications. Injects into docs/ACCEPTANCE.md or appends to TASK.md as verification checklist. Developer MUST reference this.
---
You are an Acceptance Criteria Extractor.
Steps:
1. Parse TASK.md Use Cases and requirements.
2. Generate checkboxes for each scenario/alt (e.g., from UC-01: "- [ ] Inline edit saves on Enter").
3. If Open Questions exist: auto-propose resolutions (e.g., for single-file: "Bundle CSS/JS inline in index.html").
4. Include edge cases (e.g., "Drag&drop persists after refresh").
5. Save to docs/ACCEPTANCE.md.
6. Instruct: "Block Developer if checklist not 100% covered."
```
**Пример использования:** "Run acceptance-criteria-parser on TASK.md" → Выход: docs/ACCEPTANCE.md с 20+ checkboxes для Task Manager.

### 5.2 skill-feature-completeness-check
**Причина:** Нет post-phase verification; skill блокирует incomplete code (e.g., if tags missing — flag).
**Файл:** .agent/skills/feature-completeness-check/SKILL.md
```
---
name: feature-completeness-check
description: After development phases, compare code vs TASK.md Acceptance Criteria and PLAN.md checklists. Block "Done" if <95% coverage (account for MVP). Report missing from Use Cases.
---
You are a Completeness Auditor.
Steps:
1. Read TASK.md (Criteria/Use Cases) and PLAN.md (phases/tasks).
2. Analyze code (tools: read_file, grep_search, run tests).
3. For each checkbox/phase: verified? (e.g., "UC-05 Drag&drop: test reorder in sidebar").
4. Coverage %: flag if subtasks/recurring missing.
5. If <95%: list gaps → force back to Developer.
6. Output report to docs/COMPLETENESS.md.
```
**Пример:** После Phase 3 — report: "Coverage 85%: Missing recurring tasks logic — add to task-001.2".

### 5.3 skill-prompt-refinement
**Причина:** Open Questions и vague фичи (e.g., "polished UI") вызывают потери; skill forces clarification early.
**Файл:** .agent/skills/prompt-refinement/SKILL.md
```
---
name: prompt-refinement
description: In Analysis, ask clarifying questions if requirements vague or Open Questions in TASK.md. Force MVP/nice-to-have split (e.g., subtasks as nice-to-have). Generate criteria if missing.
---
You are a Requirements Clarifier.
Steps:
1. Scan prompt/TASK.md for ambiguities (e.g., "polished UI" → ask "Specific CSS examples?").
2. Classify: MVP (core CRUD), Nice-to-have (recurring tasks).
3. Resolve Open Questions (e.g., single-file: propose inline <style>/<script>).
4. Update TASK.md: remove Open Questions, add refined Use Cases.
5. If needed, pause for user input.
```
**Пример:** Для Task Manager — questions: "Subtasks: nested or flat? Recurring: daily/weekly?" → Updated TASK.md без Open.

## 6. Implementation Plan
1. **Добавь skills:** Создай 3 папки в .agent/skills/ с SKILL.md; зарегистрируй в System/Docs/SKILLS.md.
2. **Обнови prompts:** В System/Agents/ добавь snippets (без overwrite core).
3. **Обнови workflows:** В .agent/workflows/vdd-enhanced.md внедри умные режимы (как в 4.2) для совместимости; обнови WORKFLOWS.md с таблицей сравнения.
4. **Test:** Запусти на example TASK.md — check артефакты и совместимость (e.g., вызов с pre-dev mode не ломает classic).
5. **Archive:** После — archive spec в docs/specs/.

## 7. Open Questions
- Нет (все resolved в spec). Если нужны уточнения — добавить в refinement skill.