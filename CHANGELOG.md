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

### **v3.4.2 — Framework Documentation Consistency Fixes** (Task 034 Phase 3)

#### **Fixed**
* **Broken References**: Identified and fixed stale references to moved files (`System/Docs/` vs `docs/`) in `README.md`, `.cursorrules`, and agent prompts.
* **Path Error**: Fixed incorrect path in `Translations/RU/Agents/01_orchestrator.md` (`docs/ORCHESTRATOR.md`) to align with user project structure.
* **Typos**: Corrected formatting errors in Russian Orchestrator prompt.

#### **Improved**
* **Installation Instructions**: Clarified `README.md` and `README.ru.md` to explicitly instruct users to copy `System/Docs/ORCHESTRATOR.md` to their local `docs/` folder, preventing path conflicts for distributed agents.

---

### **v3.4.1 — Workflow Integrity & Artifact Fixes** (Task 034 Phase 2)

#### **Fixed**
* **Workflow "Phantom" References**: Fixed critical bugs in `base-stub-first.md` (and consequently `vdd-enhanced`) which referenced non-existent workflows (`/analyst-task`, etc.) instead of valid ones. This restored the mandatory Analysis/Architecture phases.
* **VDD Adversarial Loop**: Corrected `vdd-adversarial.md` to use valid workflow calls (`/03-develop-single-task`) instead of non-existent actions (`/developer-fix`).
* **Artifact Consistency**: Created missing `docs/KNOWN_ISSUES.md` placeholder to satisfy workflow requirements.
* **Security Audit**: Clarified `security-audit.md` instructions regarding `.AGENTS.md` updates to handle missing files gracefully.

#### **Verified**
* Performed a full audit of all 14 workflow definitions to ensure every cross-reference points to an existing file.

### **v3.4.0 — VDD Multi-Adversarial** (Task 034)

#### **Added**
* **New Skill: `skill-adversarial-security`**: OWASP security critic in adversarial/sarcastic style.
    * Injection attacks (SQLi, XSS, Command Injection, Path Traversal).
    * Authentication & Authorization flaws.
    * Secrets exposure (hardcoded keys, passwords, API tokens).
    * Input validation failures.
* **New Skill: `skill-adversarial-performance`**: Performance critic in adversarial/sarcastic style.
    * N+1 queries, missing indexes.
    * Memory leaks, unbounded allocations.
    * Blocking operations in async code.
    * Algorithm complexity issues.
* **New Workflow: `/vdd-multi`**: Sequential execution of multiple specialized adversarial critics.
    * Phase 1: General logic review (`skill-vdd-adversarial`).
    * Phase 2: Security review (`skill-adversarial-security`).
    * Phase 3: Performance review (`skill-adversarial-performance`).

#### **Documentation**
* Updated `docs/SKILLS.md` with new VDD skills.
* Updated `Backlog/potential_improvements-2.md` with v3.4 status.

---

### **v3.3.2 — Auto-Tests for Archiving Protocol** (Task 033 Phase 2)

#### **Added**
* **Archive Protocol Tests**: 15 new automated tests for the 8 archiving scenarios using VDD adversarial approach:
    * Core scenarios: new task with existing TASK.md, no TASK.md, refinement, ID conflict.
    * VDD adversarial: missing Meta Information, malformed Task ID, permission denied, tool error simulation.
* **Testable Protocol Module**: `archive_protocol.py` — Python implementation of the 6-step archiving protocol for unit testing.
* **Test Fixtures**: 3 TASK.md variants (`task_with_meta.md`, `task_without_meta.md`, `task_malformed_id.md`).

#### **Verification**
* 44 total tests pass (29 existing + 15 new).
* Run: `cd .agent/tools && python -m pytest test_archive_protocol.py -v`

---

### **v3.3.1 — Portability, VDD Audit & UX Improvements** (Task 033)

#### **Fixed**
* **Circular Logic in Safe Commands**: Eliminated the documentation loop. Added explicit copy-paste list to `skill-safe-commands` for IDE configuration.
* **Agent Hallucinations**: Corrected `01_orchestrator.md` references to non-existent tools (`git_ops` -> `git_status`, etc.) revealed by VDD Audit.
* **IDE Configuration**: Fixed documentation for "Allow List" to address `mv` command token matching issues.
* **Portability**: Made `docs/ORCHESTRATOR.md` reference optional (`if available`) to prevent errors in lightweight projects or when transferring agents.

#### **Refactored**
* **Mandatory Skill Pattern**: Enforced `skill-safe-commands (Mandatory)` across all agents to ensure native tool safety.
* **Developer Guidelines**: Introduced explicit "Tooling Protocol" enforcing `native tools` (like `run_tests`) over shell commands.

### **v3.3.0 — Skill Encapsulation & Safe Commands Centralization** (Task 033)

#### **Added**
* **New Skill: `skill-archive-task`**: Complete, self-contained protocol for archiving `docs/TASK.md`. Single source of truth for archiving logic, eliminating duplication across 7+ files.
    * 6-step archiving protocol with decision logic (new vs refinement).
    * Error handling for missing Meta Information.
    * Validation and rollback guidance.
* **New Skill: `skill-safe-commands`**: Centralized list of commands safe for auto-execution without user approval.
    * 7 command categories: read-only, file info, git read, archiving, directory ops, tool calls, testing.
    * Pattern matching rules for IDE integration.
    * IDE-specific instructions (Antigravity/Gemini, Cursor).

#### **Refactored**
* **Duplication Eliminated**: Reduced archiving protocol duplication from 7 files to 1:
    * `.gemini/GEMINI.md` → skill reference
    * `.cursorrules` → skill reference
    * `System/Agents/02_analyst_prompt.md` → skill reference
    * `System/Agents/01_orchestrator.md` → skill reference
    * `System/Agents/00_agent_development.md` → skill reference (30 lines → 14)
    * `.agent/skills/artifact-management/SKILL.md` → skill import
    * `.agent/workflows/01-start-feature.md` → skill reference
* **Safe Commands Centralized**: All 4 files with duplicate Safe Commands now reference `skill-safe-commands`.

#### **Documentation**
* Updated `docs/SKILLS.md` with new skills.
* Added Implementation Summary to `docs/TASK.md` (Task 033).

---

### **v3.2.5, v3.2.6 — Task Archive ID Tool & Auto-Run Protocol**

#### **Added**
* **New Tool: `generate_task_archive_filename`**: Deterministic tool for generating unique sequential IDs when archiving tasks. Eliminates manual ID assignment errors and ID gaps.
    * Auto-generates next available ID (`max + 1` strategy).
    * Validates proposed IDs and handles conflicts (`allow_correction` flag).
    * Normalizes slugs (lowercase, dashes).
    * Future-proofed: supports IDs beyond 999 (regex `\d{3,}`).
* **Dispatcher Integration**: Tool registered in `scripts/tool_runner.py` for native execution.
* **Unit Tests**: 29 comprehensive tests covering all use cases.

#### **Improved**
* **Safe Commands Protocol**: Expanded list of auto-run commands in `skill-artifact-management` and Orchestrator prompt:
    * Read-only: `ls`, `cat`, `head`, `tail`, `find`, `grep`, `tree`, `wc`
    * Git read: `git status`, `git log`, `git diff`, `git show`, `git branch`
    * Archiving: `mv docs/TASK.md docs/tasks/...`
    * Tools: `generate_task_archive_filename`, `list_directory`, `read_file`
* **Agent Prompts**: Updated Orchestrator (`01`) and Analyst (`02`) with explicit tool usage for archiving.

#### **Documentation**
* Updated `docs/ARCHITECTURE.md`, `docs/ORCHESTRATOR.md`, and `docs/SKILLS.md`.
* Added Python installation requirements to README.
* Consolidated `docs/USER_TOOLS_GUIDE.md` into `docs/ORCHESTRATOR.md` (removed duplicate file).
* Synchronized `.gemini/GEMINI.md` and `.cursorrules` with v3.2.5+ protocol.

---

### **v3.2.4 — Workflow Documentation Enhancement**

#### **Added**
* **Workflow Call Sequences**: Added comprehensive "Getting Started" section to `docs/WORKFLOWS.md` with:
    * One-Step vs Multi-Step approach comparison table.
    * TDD pipeline examples (`base-stub-first`, `01`→`02`→`03/05`→`04`) with pros/cons.
    * VDD pipeline examples (`vdd-enhanced`, `full-robust`, VDD atomic steps) with pros/cons.
    * Decision flowchart (Mermaid diagram) for choosing the right approach.
    * Quick reference summary table for common scenarios.

---

### **v3.2.3 — Archiving Protocol Refinement**

#### **Changed**
* **Archiving Scope**: Removed mandatory archiving of `docs/PLAN.md`. Only `docs/TASK.md` requires archiving before new tasks.
* **Documentation**: Updated version references in `README.md` (v3.1→v3.2) and `docs/ORCHESTRATOR.md` (v3.1.2→v3.2.2).

#### **Improved**
* **Auto-Run Protocol**: Added explicit `SAFE TO AUTO-RUN` instruction to Analyst prompt and `skill-artifact-management`. The archive command for `docs/TASK.md` no longer requires user approval.

---

### **v3.2.2 — System Integrity & Archiving Protocols**

#### **Fixed**
* **Critical Restoration**: Restored missing (empty) Russian agent prompts (`Translations/RU/Agents/01, 02, 04, 06`) using v3.2.0 logic.
* **Data Loss Prevention**: Fixed a critical gap in `skill-artifact-management` where the "Archiving Protocol" was missing.
* **Protocol Enforcement**: Updated Orchestrator (`01`), Analyst (`02`), and Planner (`06`) to strictly enforce archiving of `docs/TASK.md` and `docs/PLAN.md` before overwriting.

#### **Improved**
* **System Prompts**: Synchronized `.gemini/GEMINI.md` and `.cursorrules` with the Tool Execution Protocol (v3.2.0), explicitly enabling native tool calling.
* **Consistency**: Completed a full audit of the prompt system to ensure zero contradictions between System and Agent prompts.

---

### **v3.2.1 — Skills System Optimization**

#### **Added**
* **Skills**:
    * `skill-task-model`: Standardized examples and rules for `docs/TASK.md`.
    * `skill-planning-format`: Standardized templates for `docs/PLAN.md` and Task Descriptions.
* **Rules**: Added `.agent/rules/localization-sync.md` to enforce bilingual documentation updates.

#### **Improved**
* **Prompt Engineering**: Significantly reduced the size of Analyst (`02`), Architect (`04`), and Planner (`06`) agents by extracting static templates into the Skills System.
* **Localization**: Synced `README.ru.md` with English version (added Tool Calling section).
* **Russian Agents**: Updated `Translations/RU/Agents/*.md` to match v3.2.0 optimizations (Tool Calling logic, Skills extraction, Path Hygiene).

---

### **v3.2.0 — Structured Tool Calling & Path Hygiene**

#### **Added**
* **Tool Execution Subsystem**: The Orchestrator now natively supports structured tool calling (Function Calling).
* **New Skills**:
    * `skill-task-model`: Standardized examples and rules for `docs/TASK.md`.
    * `skill-planning-format`: Standardized templates for `docs/PLAN.md` and Task Descriptions.
    * `skill-architecture-format`: Consolidated architecture document templates.
* **Standard Tools**: Added `run_tests`, `git_ops`, `file_ops` to `.agent/tools/schemas.py`.
* **Documentation**: Added `docs/ORCHESTRATOR.md`.

#### **Improved**
* **Prompt Engineering**: Significantly reduced the size of Analyst (`02`), Architect (`04`), and Planner (`06`) agents by extracting static templates into the Skills System.
* **Maintenance**: Centralized critical document templates (TASK, PLAN, Architecture) in `.agent/skills/` to ensure consistency and easier updates.
* **Workflows**: Refactored `03-develop-task` -> `03-develop-single-task` and updated `base-stub-first`.

#### **Changed**
* **Test Reports**: Standardized storage location. Reports moved from `docs/test_reports` to `tests/tests-{Task ID}/`.
* **Path Enforcement**: Updated all Agent prompts to use strictly project-relative path examples.
* **Agents**: Updated Orchestrator, Developer, and Reviewers to enforce new protocols.

#### **Fixed**
* **Cleanup**: Removed legacy `docs/test_reports` directory.

---

### **v3.1.3 — Skills Cleanup & Cursor Integration Fix**

#### **Changed**
* **Project Structure**: Removed redundant `.cursor/skills` directory to eliminate duplication.
* **Cursor Integration**: Updated `README.md` to instruct users to simply symlink `.cursor/skills` -> `.agent/skills`, ensuring a single source of truth.
* **Orchestrator**: Updated `.cursorrules` to reference the correct symlinked path and fixed legacy "tz" terminology in comments.
* **Workflows**: Archived `docs/TASK.md` to `docs/tasks/task-014-cleanup-skills.md`.

---

### **v3.1.2 — Analyst Protocol & YAML Fixes**

#### **Fixed**
* **Skills**: Fixed YAML syntax error in `core-principles` skill (quoted description).

#### **Improved**
* **Analyst Agent**: Added "CRITICAL PRE-FLIGHT CHECKLIST" to `02_analyst_prompt.md` to strictly enforce:
    * Archiving of existing `docs/TASK.md` before starting new work.
    * Mandatory inclusion of Section 0 (Meta Information: Task ID, Slug).
* **Skills**: Updated `skill-requirements-analysis` to mark Meta Information as **MANDATORY**.
* **Documentation**: Enforced "Relative Paths Only" rule for Artifacts in `skill-documentation-standards` and `06_agent_planner.md`.

#### **Refactored**
* **Skills**: Audited and fixed YAML frontmatter in `code-review-checklist`, `developer-guidelines`, `security-audit`, and `artifact-management`.
* **PLAN.md**: Converted absolute paths to relative paths.

---

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

### **v3.4.1 — Целостность сценариев и фиксы артефактов** (Task 034 Phase 2)

#### **Исправлено**
* **"Фантомные" ссылки в сценариях**: Исправлены критические ссылки в `base-stub-first.md` (и, как следствие, в `vdd-enhanced`), которые вели на несуществующие сценарии (`/analyst-task` и др.). Это восстановило обязательные фазы Анализа и Архитектуры.
* **Цикл VDD Adversarial**: В `vdd-adversarial.md` исправлены вызовы на валидные сценарии (`/03-develop-single-task`) вместо несуществующих действий.
* **Целостность Артефактов**: Добавлен отсутствующий файл `docs/KNOWN_ISSUES.md`, необходимый для корректной работы сценариев.
* **Аудит Безопасности**: В `security-audit.md` уточнена инструкция по обновлению `.AGENTS.md` (теперь корректно отрабатывает отсутствие файлов).

#### **Верифицировано**
* Проведен полный аудит всех 14 файлов сценариев на предмет корректности перекрестных ссылок.

### **v3.4.0 — VDD Multi-Adversarial** (Task 034)

#### **Добавлено**
* **Новый навык: `skill-adversarial-security`**: OWASP-критик в саркастичном стиле.
    * Атаки инъекций (SQLi, XSS, Command Injection, Path Traversal).
    * Уязвимости аутентификации и авторизации.
    * Утечка секретов (хардкод ключей, паролей, токенов).
    * Ошибки валидации ввода.
* **Новый навык: `skill-adversarial-performance`**: Критик производительности в саркастичном стиле.
    * N+1 запросы, отсутствие индексов.
    * Утечки памяти, unbounded аллокации.
    * Блокирующие операции в async коде.
    * Проблемы сложности алгоритмов.
* **Новый workflow: `/vdd-multi`**: Последовательный запуск нескольких adversarial критиков.
    * Фаза 1: Ревью логики (`skill-vdd-adversarial`).
    * Фаза 2: Ревью безопасности (`skill-adversarial-security`).
    * Фаза 3: Ревью производительности (`skill-adversarial-performance`).

#### **Документация**
* Обновлён `docs/SKILLS.md` с новыми VDD скиллами.
* Обновлён `Backlog/potential_improvements-2.md` статусы v3.4.

---

### **v3.3.2 — Авто-тесты для Протокола Архивации** (Task 033 Phase 2)

#### **Добавлено**
* **Тесты протокола архивации**: 15 новых автоматизированных тестов для 8 сценариев архивации с VDD adversarial подходом:
    * Основные сценарии: новая задача с существующим TASK.md, без TASK.md, уточнение, конфликт ID.
    * VDD adversarial: отсутствие Meta Information, некорректный Task ID, ошибка прав доступа, ошибка инструмента.
* **Тестируемый модуль протокола**: `archive_protocol.py` — Python реализация 6-шагового протокола для unit-тестирования.
* **Test Fixtures**: 3 варианта TASK.md (`task_with_meta.md`, `task_without_meta.md`, `task_malformed_id.md`).

#### **Верификация**
* 44 теста проходят (29 существующих + 15 новых).
* Запуск: `cd .agent/tools && python -m pytest test_archive_protocol.py -v`

---

### **v3.3.1 — Портативность, VDD Аудит и UX** (Task 033)

#### **Исправлено**
* **Круговая зависимость в Safe Commands**: Устранена петля в документации. Добавлен явный список команд в `skill-safe-commands` для быстрой настройки IDE.
* **Галлюцинации Агентов**: Исправлены ссылки на несуществующие инструменты в `01_orchestrator.md` (`git_ops` -> `git_status`), выявленные в ходе VDD Аудита.
* **Конфигурация IDE**: Исправлена документация для "Allow List" (решена проблема токенизации команды `mv`).
* **Портативность**: Ссылка на `docs/ORCHESTRATOR.md` сделана опциональной (`if available`), чтобы агенты работали корректно при переносе.

#### **Рефакторинг**
* **Mandatory Skill Pattern**: Принудительное использование `skill-safe-commands` всеми агентами.
* **Гайдлайны Разработчика**: Явный "Tooling Protocol", требующий использования нативных инструментов (`run_tests`) вместо shell.

### **v3.3.0 — Инкапсуляция Skills и Централизация Safe Commands** (Task 033)

#### **Добавлено**
* **Новый навык: `skill-archive-task`**: Полный, самодостаточный протокол архивации `docs/TASK.md`. Единый источник истины для логики архивации, устраняет дублирование в 7+ файлах.
    * 6-шаговый протокол архивации с логикой принятия решений (новая задача vs уточнение).
    * Обработка ошибок при отсутствии Meta Information.
    * Руководство по валидации и откату.
* **Новый навык: `skill-safe-commands`**: Централизованный список команд для автоматического выполнения без подтверждения пользователя.
    * 7 категорий команд: только чтение, информация о файлах, git чтение, архивация, директории, инструменты, тестирование.
    * Правила pattern matching для интеграции с IDE.
    * Инструкции для IDE (Antigravity/Gemini, Cursor).

#### **Рефакторинг**
* **Устранено дублирование**: Сокращён протокол архивации с 7 файлов до 1:
    * `.gemini/GEMINI.md` → ссылка на skill
    * `.cursorrules` → ссылка на skill
    * `System/Agents/02_analyst_prompt.md` → ссылка на skill
    * `System/Agents/01_orchestrator.md` → ссылка на skill
    * `System/Agents/00_agent_development.md` → ссылка на skill (30 строк → 14)
    * `.agent/skills/artifact-management/SKILL.md` → импорт из skill
    * `.agent/workflows/01-start-feature.md` → ссылка на skill
* **Safe Commands централизованы**: Все 4 файла с дублированными Safe Commands теперь ссылаются на `skill-safe-commands`.

#### **Документация**
* Обновлён `docs/SKILLS.md` с новыми навыками.
* Добавлено Implementation Summary в `docs/TASK.md` (Task 033).

---

### **v3.2.5, v3.2.6 — Инструмент генерации ID задач и Протокол Auto-Run**

#### **Добавлено**
* **Новый инструмент: `generate_task_archive_filename`**: Детерминированный инструмент для генерации уникальных последовательных ID при архивации задач. Устраняет ошибки ручного назначения ID и пробелы в нумерации.
    * Автоматически генерирует следующий доступный ID (стратегия `max + 1`).
    * Проверяет предложенные ID и обрабатывает конфликты (флаг `allow_correction`).
    * Нормализует slug (нижний регистр, дефисы).
    * Поддержка ID > 999 (регулярка `\d{3,}`).
* **Интеграция с Dispatcher**: Инструмент зарегистрирован в `scripts/tool_runner.py`.
* **Unit-тесты**: 29 тестов, покрывающих все сценарии использования.

#### **Улучшено**
* **Протокол Safe Commands**: Расширен список команд для автозапуска в `skill-artifact-management` и промпте Orchestrator:
    * Только чтение: `ls`, `cat`, `head`, `tail`, `find`, `grep`, `tree`, `wc`
    * Git чтение: `git status`, `git log`, `git diff`, `git show`, `git branch`
    * Архивация: `mv docs/TASK.md docs/tasks/...`
    * Инструменты: `generate_task_archive_filename`, `list_directory`, `read_file`
* **Промпты агентов**: Обновлены Orchestrator (`01`) и Analyst (`02`) с явными инструкциями использования инструмента.

#### **Документация**
* Обновлены `docs/ARCHITECTURE.md`, `docs/ORCHESTRATOR.md`, `docs/SKILLS.md`.
* Добавлены требования к установке Python в README.

---

### **v3.2.4 — Улучшение Документации Сценариев**

#### **Добавлено**
* **Последовательности вызовов Workflow**: Добавлен раздел "Getting Started" в `docs/WORKFLOWS.md`:
    * Сравнительная таблица подходов One-Step vs Multi-Step.
    * Примеры TDD пайплайна (`base-stub-first`, `01`→`02`→`03/05`→`04`) с плюсами и минусами.
    * Примеры VDD пайплайна (`vdd-enhanced`, `full-robust`, атомарные VDD шаги) с плюсами и минусами.
    * Диаграмма принятия решений (Mermaid) для выбора подхода.
    * Сводная таблица рекомендаций для типичных сценариев.

---

### **v3.2.3 — Уточнение Протокола Архивации**

#### **Изменено**
* **Область архивации**: Удалена обязательная архивация `docs/PLAN.md`. Только `docs/TASK.md` требует архивации перед новыми задачами.
* **Документация**: Обновлены ссылки на версии в `README.md` (v3.1→v3.2) и `docs/ORCHESTRATOR.md` (v3.1.2→v3.2.2).

#### **Улучшено**
* **Протокол Auto-Run**: Добавлена явная инструкция `SAFE TO AUTO-RUN` в промпт Аналитика и `skill-artifact-management`. Команда архивации `docs/TASK.md` больше не требует одобрения пользователя.

---

### **v3.2.2 — Целостность системы и Протоколы архивации**

#### **Исправлено**
* **Критическое восстановление**: Восстановлены отсутствующие (пустые) промпты русских агентов (`Translations/RU/Agents/01, 02, 04, 06`) с логикой v3.2.0.
* **Предотвращение потери данных**: Исправлен критический пробел в `skill-artifact-management`, где отсутствовал "Протокол Архивации".
* **Принудительные протоколы**: Обновлены Оркестратор (`01`), Аналитик (`02`) и Планировщик (`06`) для строгого требования архивации `docs/TASK.md` и `docs/PLAN.md` перед перезаписью.

#### **Улучшено**
* **Системные промпты**: Синхронизированы `.gemini/GEMINI.md` и `.cursorrules` с Протоколом Выполнения Инструментов (v3.2.0), явно разрешающим нативный вызов инструментов.
* **Согласованность**: Проведен полный аудит системы промптов для исключения противоречий.

---

### **v3.2.1 — Оптимизация Системы Навыков**

#### **Добавлено**
* **Навыки**:
    * `skill-task-model`: Стандартизированные примеры и правила для `docs/TASK.md`.
    * `skill-planning-format`: Шаблоны для `docs/PLAN.md` и описаний задач.
* **Правила**: Добавлен файл `.agent/rules/localization-sync.md` для автоматического контроля синхронизации документации.

#### **Улучшено**
* **Промпт-инжиниринг**: Значительно уменьшен размер агентов-Аналитика (`02`), Архитектора (`04`) и Планировщика (`06`) за счет выноса статических шаблонов в Систему Навыков.
* **Локализация**: `README.ru.md` синхронизирован с английской версией (добавлен раздел Инструментов).
* **Русские Агенты**: Обновлены `Translations/RU/Agents/*.md` до стандартов v3.2.0 (логика Инструментов, Навыки, относительные пути).

---

### **v3.2.0 — Структурированные инструменты и Гигиена путей**

#### **Добавлено**
* **Подсистема выполнения инструментов**: Оркестратор теперь нативно поддерживает структурированный вызов инструментов.
* **Новые навыки**:
    * `skill-task-model`: Стандартизированные примеры и правила для `docs/TASK.md`.
    * `skill-planning-format`: Шаблоны для `docs/PLAN.md` и описаний задач.
    * `skill-architecture-format`: Консолидированные шаблоны архитектурной документации.
* **Стандартные инструменты**: Добавлены `run_tests`, `git_ops`, `file_ops`.
* **Документация**: Добавлены `docs/ORCHESTRATOR.md`.

#### **Улучшено**
* **Промпт-инжиниринг**: Значительно уменьшен размер агентов-Аналитика (`02`), Архитектора (`04`) и Планировщика (`06`) за счет выноса статических шаблонов в Систему Навыков.
* **Поддержка**: Критические шаблоны документов централизованы в `.agent/skills/`.

#### **Изменено**
* **Протоколы тестирования**: Стандартизировано место хранения отчетов (`tests/tests-{Task ID}/`).
* **Гигиена путей**: В промптах агентов теперь используются строго относительные пути проекта.
* **Агенты**: Обновлены промпты Оркестратора, Разработчика и Ревьюеров.

#### **Исправлено**
* **Очистка**: Удалена устаревшая директория `docs/test_reports`.

---


### **v3.1.3 — Очистка Skills и исправление интеграции Cursor**

#### **Изменено**
* **Структура проекта**: Удалена дублирующая директория `.cursor/skills`.
* **Интеграция с Cursor**: В `README.md` и `README.ru.md` добавлена инструкция по созданию симлинка `.cursor/skills` -> `.agent/skills`, что гарантирует единый источник правды.
* **Оркестратор**: Обновлен `.cursorrules`, исправлены пути к навыкам и легаси-терминология "tz".
* **Документация**: В `docs/ARCHITECTURE.md` отражена связь через симлинк.

---

### **v3.1.2 — Протокол Аналитика и Fix YAML**

#### **Исправлено**
* **Навыки**: Исправлена синтаксическая ошибка YAML в навыке `core-principles` (добавлены кавычки в описание).

#### **Улучшено**
* **Агент-Аналитик**: Добавлен "CRITICAL PRE-FLIGHT CHECKLIST" в `02_analyst_prompt.md`, строго требующий:
    * Архивирования существующего `docs/TASK.md` перед началом работы.
    * Обязательного включения Секции 0 (Meta Information: Task ID, Slug).
* **Навыки**: Обновлен `skill-requirements-analysis`, помечающий Meta Information как **ОБЯЗАТЕЛЬНУЮ**.
* **Документация**: Внедрено правило "Только относительные пути" (Relative Paths Only) для Артефактов в `skill-documentation-standards` и `06_agent_planner.md`.

#### **Рефакторинг**
* **Навыки**: Проведен аудит и исправление YAML-заголовков в `code-review-checklist`, `developer-guidelines`, `security-audit` и `artifact-management`.
* **PLAN.md**: Абсолютные пути заменены на относительные.

---

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
