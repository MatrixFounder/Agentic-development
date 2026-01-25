# Task: Внедрение "Light" режима (Workflow-Based) [Completed]

## Цель

Добавить в фреймворк (v3.7.0) режим **Light Mode** для быстрых низкорисковых задач, используя нативные механизмы оптимизации (Workflows + Skill Tiers).

Это позволит сократить цикл разработки на 40–60% для тривиальных задач (bugfix, UI tweaks, minor refactor) за счет пропуска фаз Architecture и тяжелого Planning, сохраняя при этом обязательные проверки качества (Tests + Code Review).

## Контекст (Совместимость с O1-O6)

В отличие от ранних планов, реализация будет опираться на новые возможности фреймворка:
1.  **Workflows (O2/O6):** Вместо усложнения промпта Оркестратора (`IF/ELSE`) мы используем файлы `.agent/workflows/`, которые автоматически переопределяют стандартный pipeline.
2.  **Skill Tiers (O1/O5):** `skill-light-mode` будет реализован как **TIER 2** (загрузка по требованию) и будет содержать инструкции для Analyst и Developer, специфичные для этого режима.
3.  **Lazy Loading:** Пропуск агента Architect автоматически предотвратит загрузку тяжелых архитектурных скиллов — специальная логика выгрузки не требуется.

## Use Case: Запуск Light Mode

### Актёры
*   **User:** Разработчик.
*   **Orchestrator:** Исполнитель workflows.

### Основной сценарий
1.  User вводит команду `/light` или запускает workflow `run light-start`.
    *   *Alternately:* User пишет "Fix typo in button label" -> Orchestrator распознает паттерн и предлагает workflow.
2.  Orchestrator находит `.agent/workflows/light-01-start-feature.md`.
3.  Выполняется упрощенный pipeline, описанный в workflow.
4.  Результат: быстрый PR (commit) с зелеными тестами.

## Требования к реализации

### 1. Pipeline (определяется в Workflows)

| Шаг | Агент | Описание | Отличие от Standard |
| :--- | :--- | :--- | :--- |
| **1** | Analyst | Создание `TASK.md` с тегом `[LIGHT]` | Обязательно |
| **2** | Developer | Реализация + Тесты (Cycle) | Совмещает Plan+Exec |
| **3** | Code Reviewer | Финальная проверка + Sanity Security | SPoF Mitigation |
| **4** | Orchestrator | Commit + Archive | Автоматически |

**Пропущенные фазы:**
*   **Architect:** Пропускается (архитектура не меняется).
*   **Task Reviewer:** Пропускается (задача тривиальна).
*   **Planner:** Пропускается (Developer планирует "на лету" или использует `Implementation Steps` из TASK).
*   **Plan Reviewer:** Пропускается.
*   **Security:** Пропускается (если не затронуты sensitive файлы).

### 2. Исключения (Critical Rules)

В `GEMINI.md` и `AGENTS.md` необходимо внести исключение в CRITICAL RULE, разрешающее пропускать фазу Architecture **только** в режиме Light Mode.

### 3. Skill: `light-mode` (Tier 2)

Создать `.agent/skills/light-mode/SKILL.md`:
*   **Tier:** 2 (Load on specific trigger).
*   **Content:**
    *   Критерии режима (Low Risk).
    *   Инструкция для Developer: "Do not overengineer. Fix the issue directly. Run tests."
    *   Инструкция для Reviewer: "Focus on correctness and tests. Skip architectural nitpicks unless critical. Perform basic security sanity check."
    *   **Escalation Policy:** "If you discover complexity (DB migration, API change), STOP and request workflow switch."
    *   **Safety:** Запрет на использование в файлах `auth`, `payment`, `crypto` (эскалация в Standard).

## План работ

1.  **Documentation Updates:**
    *   [ ] Обновить `GEMINI.md`:
        *   Добавить исключение в CRITICAL RULE.
        *   Обновить Dispatch Logic: предлагать `/light` для простых задач.
    *   [ ] Обновить `AGENTS.md`: Добавить исключение.
    *   [ ] Обновить `docs/WORKFLOWS.md`: Описать режим.

2.  **Creation of Workflows:**
    *   [ ] Создать `.agent/workflows/light-01-start-feature.md`:
        *   Step 1: Analyisis (Load `light-mode` skill).
        *   Step 2: Transition to Develop workflow.
    *   [ ] Создать `.agent/workflows/light-02-develop-task.md`:
        *   Step 1: Developer (Implement + Test).
        *   Step 2: Code Reviewer.
        *   Step 3: Loop or Checkpoint.

3.  **Skill Creation:**
    *   [ ] Создать `.agent/skills/light-mode/SKILL.md` (шаблон Tier 2).

4.  **Verification (Dogfooding):**
    *   [ ] Запустить тестовую задачу через `/light`.

## Definition of Done
*   Режим запускается через workflow.
*   Оркестратор **НЕ ИЗМЕНЯЛСЯ** (промпт `01_orchestrator.md` остался чистым).
*   Токенов тратится на ~50% меньше на старте (нет Architect/Planner overhead).
*   Тесты проходят.
