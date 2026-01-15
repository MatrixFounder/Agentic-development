<!--
## [Unreleased]

### 🇺🇸 English
#### Added
- ...

#### Changed
- ...

#### Fixed
- ...

### 🇷🇺 Русский
#### Добавлено
- ...

#### Изменено
- ...

#### Исправлено
- ...
-->

## 🇺🇸 English Version (Primary)

### **v3.1.1 — Plan & Structure Fixes**

#### **Fixed**
* **Agent Prompts**: Corrected `plan.md` file path references to `docs/PLAN.md` in Planner and Reviewer agents (both English and Russian versions).
* **Agent Prompts**: Corrected `open_questions.md` file path references to `docs/open_questions.md` in Planner agent.
* **Project Structure**: Removed the `verification/` directory to comply with `docs/ARCHITECTURE.md`.

---

### **v3.1.0 — Global "TZ" to "TASK" Refactor**

#### **Changed**
* **Terminology**: Global refactoring of "TZ" (Техническое Задание) to "TASK" (Task/Specification) to improve internationalization and consistency.
* **Artifacts**: Renamed `docs/TZ.md` to `docs/TASK.md`.
* **System Agents**: Updated all agent prompts (Analyst, Reviewer, Architect, etc.) to use "TASK" terminology.
* **Skills**: Renamed `skill-tz-review-checklist` to `skill-task-review-checklist`.
* **Documentation**: Updated `README.md`, `WORKFLOWS.md`, `SKILLS.md`, and `.gemini/GEMINI.md` to reflect the new standard.

#### **Fixed**
* **Consistency**: Eliminated mixed usage of "TZ" and "Task Specification" across the framework.
* **Localization**: Aligned Russian translations (`Translations/RU`) with the new global standard.
* **Workflows**: Fixed a critical bug in `01-start-feature` and `vdd-01-start-feature` where the previous `docs/TASK.md` was overwritten instead of archived. Added explicit archiving step.

#### **Migration Guide**
To upgrade from v3.0.x to v3.1.0:
1. **Rename**: `mv docs/TZ.md docs/TASK.md`
2. **Update Agents**: Replace `System/Agents/` with the new version (Note: `03_tz_reviewer_prompt.md` -> `03_task_reviewer_prompt.md`).
3. **Update Skills**: Replace `.agent/skills/` with the new version.

---

### **v3.0.3 — Documentation Sync & Artifacts**

#### **Fixed**
* **Documentation**: Replaced obsolete references to `UNKNOWN.md` with `docs/open_questions.md` in `README.md` and `README.ru.md` to align with actual Agent prompts.

#### **Added**
* **Artifacts**: Added missing `docs/open_questions.md` template for tracking unresolved issues.

---

### **v3.0.2 — Skills Doc & Examples**
  
#### **Added**
* **Examples**:
    * `examples/skill-testing/test_skill.py`: Python script for isolated skill testing.
    * `examples/skill-testing/n8n_skill_eval_workflow.json`: n8n workflow for skill evaluation (with Sticky Notes hints).
* **Skills Documentation**:
    * Added "Dynamic Loading", "Isolated Testing", and "Best Practices" sections to `docs/SKILLS.md`.
    * Added explicit links to example files.

---

### **v3.0.1 — Skills System Refinement**

#### **Improved**
* **Skills Documentation**:
    * Expanded `docs/SKILLS.md` with "How it Works", "Principles", and official documentation links.
    * Added explicit "Used By Workflows" and "Used By Agents" matrices.
    * Clarified **Adversarial Agent** as a "Virtual Persona" in VDD mode.
* **README**:
    * Restored missing "Agent Team" and "System Prompt" sections.
    * Fixed incomplete instructions for Skills System installation.

---

### **v3.0.0 — Skills System & Global Localization**

#### **Major Changes**
* **Skills System**: Introduced a modular `.agent/skills/` library. Agents now dynamically load capabilities (Skills) instead of having monolithic prompts. This reduces prompt size and increases maintainability.
* **Localization Architecture**: New `Translations/` directory structure. Full support for switching between English and Russian contexts by swapping agent/skill files.
* **Documentation**:
    * Added `docs/SKILLS.md`: Comprehensive catalog of all available skills.
    * Updated `README.md`, `README.ru.md`, `docs/ARCHITECTURE.md` to reflect the new structure.

#### **Removed**
* **Legacy directories**: Removed `/System/Agents_ru` (replaced by `Translations/RU`).

---

### **v2.1.3 — Documentation & Workflow Consistency**

#### **Fixed**
* **ARCHITECTURE.md**: Updated to reflect the actual project structure (added `.agent` and `docs` directories).
* **Workflows**: `full-robust.md` now explicitly calls `/security-audit` (Agent 10) instead of a placeholder.

### **v2.1.2 — Fix .AGENTS.md Generation Bug**

#### **Fixed**
* **Prompt Conflict**: Resolved a conflict where the Developer agent would skip creating `.AGENTS.md` files because the Planner didn't explicitly task them and the "no extra files" rule completely forbade them.
* **Planner Agent**: Now mandates `.AGENTS.md` creation for new directories.
* **Developer Agent**: Explicitly allowed to create `.AGENTS.md` as an exception, even if not listed in the task.

### **v2.1.1 — Workflow Verification & Safety**

#### **Added**
* **Mandatory Verification**: All core workflows (Standard & VDD) now include explicit verification loops (Analyst -> TZ Review, Architect -> Arch Review, etc.).
* **Safety Limits**: Implemented a **Max 2 Retries** mechanism to prevent infinite Doer-Reviewer loops.

---

### **v2.1.0 — Nested Workflows and Security Audit**

#### **Added**
* **Nested Workflows Support**: New ability to call workflows from within other workflows (e.g., `Call /base-stub-first`).
* **New Workflows**:
  * `/base-stub-first`: Foundational stub-first pipeline.
  * `/vdd-adversarial`: Isolated adversarial loop.
  * `/vdd-enhanced`: Nested combination of Stub-First + VDD.
  * `/full-robust`: Full pipeline including future Security Audit steps.
  * `/security-audit`: Standalone security vulnerability assessment workflow.
* **New Roles**:
  * **10_security_auditor**: Specialized agent for OWASP/Security scanning.
* **Documentation**: Updated `WORKFLOWS.md`, `README.md`, and `GEMINI.md` to reflect these changes.

---

### **v2.0.0 — Public Release: Multi-Agent Software Development System**

#### **Key Highlights**

* **9-Agent Ecosystem**: A comprehensive orchestration of **9 specialized agents** (Analyst, Architect, Planner, Developer, Reviewer, Orchestrator, and others) covering the full SDLC.
* **VDD (Verification-Driven Development)**: Built-in adversarial testing with the **Sarcasmotron** agent to ensure logic consistency and high reliability.
* **Stub-First Methodology**: Strict TDD-inspired flow where architecture, E2E tests, and stubs are defined before a single line of production code is written.
* **Long-Term Memory**: Advanced artifact management using `.AGENTS.md` and structured logs to maintain context across long development sessions.
* **Native IDE Integration**: Seamless support for **Antigravity** (`.gemini/GEMINI.md`) and **Cursor** (`.cursorrules`).

#### **🚀 Quick Start**

1. **Copy agents**: Move the `/System/Agents` folder into your project root.
2. **Configure IDE**: Copy `.gemini/GEMINI.md` (for Antigravity) or `.cursorrules` (for Cursor) to your project root to enable agent instructions.
3. **Initialize**: Use the `02_analyst_prompt.md` prompt to start the session.
4. **Follow Guidelines**: Refer to the **Pre-flight Check** in the README for the full workflow.

---

## 🇷🇺 Русская версия

### **v3.1.1 — Исправление путей Плана и Структуры**

#### **Исправлено**
* **Промпты Агентов**: Исправлены ссылки на файл плана (`plan.md` -> `docs/PLAN.md`) в промптах Planner и Reviewer (в английской и русской версиях).
* **Промпты Агентов**: Исправлены ссылки на файл вопросов (`open_questions.md` -> `docs/open_questions.md`) в промпте Planner.
* **Структура Проекта**: Удалена папка `verification/` для соответствия `docs/ARCHITECTURE.md`.

---

### **v3.1.0 — Глобальный Рефакторинг "ТЗ" в "TASK"**

#### **Изменено**
* **Терминология**: Глобальный рефакторинг "ТЗ" (Техническое Задание) в "TASK" (Task/Specification) для улучшения интернационализации и согласованности.
* **Артефакты**: Переименован `docs/TZ.md` в `docs/TASK.md`.
* **Системные Агенты**: Обновлены все промпты агентов (Analyst, Reviewer, Architect и др.) для использования терминологии "TASK".
* **Навыки**: Переименован `skill-tz-review-checklist` в `skill-task-review-checklist`.
* **Документация**: Обновлены `README.ru.md`, `WORKFLOWS.md`, `SKILLS.md` и `.gemini/GEMINI.md` для соответствия новому стандарту.

#### **Исправлено**
* **Согласованность**: Устранено смешанное использование "ТЗ" и "Task Specification" во всем фреймворке.
* **Сценарии (Workflows)**: Исправлена критическая ошибка в `01-start-feature` и `vdd-01-start-feature`, из-за которой старое ТЗ перезаписывалось без архивации. Добавлен явный шаг архивирования.

#### **Инструкция по миграции**
Для обновления с v3.0.x до v3.1.0:
1. **Переименование**: `mv docs/TZ.md docs/TASK.md`
2. **Обновление Агентов**: Замените `System/Agents/` на новую версию (Важно: `03_tz_reviewer_prompt.md` -> `03_task_reviewer_prompt.md`).
3. **Обновление Навыков**: Замените `.agent/skills/` на новую версию.

---

### **v3.0.3 — Синхронизация документации и артефакты**

#### **Исправлено**
* **Документация**: Заменены устаревшие ссылки на `UNKNOWN.md` на `docs/open_questions.md` в `README.md` и `README.ru.md` для соответствия реальным промптам Агентов.

#### **Добавлено**
* **Артефакты**: Добавлен отсутствующий шаблон `docs/open_questions.md` для отслеживания нерешенных вопросов.

---

### **v3.0.2 — Примеры и Доработка Документации**
  
#### **Добавлено**
* **Примеры (Examples)**:
    * `examples/skill-testing/test_skill.py`: Python скрипт для изолированного тестирования навыков.
    * `examples/skill-testing/n8n_skill_eval_workflow.json`: n8n workflow с подсказками (Sticky Notes) для проверки промптов.
* **Документация (Skills)**:
    * В `docs/SKILLS.md` добавлены разделы "Dynamc Loading", "Isolated Testing" и "Best Practices".
    * Добавлены прямые ссылки на файлы примеров.

---

### **v3.0.1 — Улучшение Системы Навыков**

#### **Улучшено**
* **Документация Навыков**:
    * Расширен `docs/SKILLS.md`: добавлено "Как это работает", принципы и ссылки на официальную документацию.
    * Добавлены матрицы "Используется в сценариях" и "Используется агентами".
    * Уточнено понятие **Adversarial Agent** как "Virtual Persona" (Виртуальная Персона) в режиме VDD.
* **README**:
    * Восстановлены пропущенные разделы "Команда Агентов" и "Системный Промпт".
    * Исправлены инструкции по установке Системы Навыков.

---

### **v3.0.0 — Система Навыков и Глобальная Локализация**

#### **Ключевые изменения**
* **Система Навыков**: Внедрена модульная библиотека `.agent/skills/`. Агенты теперь динамически загружают "навыки" вместо использования монолитных промптов.
* **Архитектура Локализации**: Новая структура директории `Translations/`. Полная поддержка переключения между Английским и Русским контекстами.
* **Документация**:
    * Добавлен `docs/SKILLS.md`: Полный каталог доступных навыков.
    * Обновлены `README.md`, `README.ru.md`, `docs/ARCHITECTURE.md`.

#### **Удалено**
* **Legacy**: Удалена директория `/System/Agents_ru` (заменена на `Translations/RU`).

---

### **v2.1.3 — Документация и согласованность сценариев**

#### **Исправлено**
* **ARCHITECTURE.md**: Обновлен для соответствия реальной структуре проекта (добавлены папки `.agent` и `docs`).
* **Workflows**: `full-robust.md` теперь явно вызывает `/security-audit` (Агент 10) вместо заглушки.

### **v2.1.2 — Исправление генерации .AGENTS.md**

#### **Исправлено**
* **Конфликт промптов**: Устранен конфликт, из-за которого Developer пропускал создание `.AGENTS.md`, так как Planner не ставил это в задачу, а правило "без лишних файлов" запрещало самодеятельность.
* **Planner Agent**: Теперь явно требует создания `.AGENTS.md` для новых папок.
* **Developer Agent**: Получил явное разрешение (исключение) на создание `.AGENTS.md`, даже если этого нет в task-файле.

### **v2.1.1 — Верификация процессов и безопасность**

#### **Добавлено**
* **Обязательная верификация**: Все основные сценарии (Standard и VDD) теперь включают явные циклы проверки (Analyst -> TZ Review и т.д.).
* **Лимиты безопасности**: Внедрен механизм **Max 2 Retries** для предотвращения бесконечных циклов "Исполнитель-Ревьюер".

---

### **v2.1.0 — Вложенные сценарии (Nested Workflows) и аудит безопасности (Security Audit)**

#### **Добавлено**
* **Поддержка вложенных сценариев**: Возможность вызывать одни workflows из других (например, `Call /base-stub-first`).
* **Новые сценарии**:
  * `/base-stub-first`: Базовый пайплайн Stub-First.
  * `/vdd-adversarial`: Изолированный цикл адверсариальной проверки.
  * `/vdd-enhanced`: Комбинация Stub-First + VDD.
  * `/full-robust`: Полный пайплайн с будущим аудитом безопасности.
  * `/security-audit`: Standalone security vulnerability assessment workflow.
* **Документация**: Обновлены `WORKFLOWS.md`, `README.md` и `GEMINI.md`.

---

### **v2.0.0 — Публичный релиз: Система мультиагентной разработки**

#### **Основные возможности**

* **Экосистема из 9 агентов**: Полная оркестрация **9 специализированных ролей** (Analyst, Architect, Planner, Developer, Reviewer, Orchestrator и др.), обеспечивающая контроль на всех этапах SDLC.
* **VDD (Verification-Driven Development)**: Состязательное тестирование с помощью агента **Sarcasmotron** для проверки логики и минимизации ошибок.
* **Методология Stub-First**: Методика, при которой тесты и заглушки создаются до реализации основной логики.
* **Управление контекстом**: Система артефактов и `.AGENTS.md` для поддержания "длинной памяти" проекта.
* **Поддержка IDE**: Нативная интеграция с **Antigravity** и **Cursor**.

#### **🚀 Быстрый старт**

1. **Копирование агентов**: Перенесите папку `/System/Agents` в корень вашего проекта.
2. **Настройка IDE**: Скопируйте `.gemini/GEMINI.md` (для Antigravity) или `.cursorrules` (для Cursor) в корень проекта.
3. **Инициализация**: Используйте промпт `02_analyst_prompt.md` для запуска процесса.
4. **Инструкции**: Следуйте разделу **Pre-flight Check** в README.
