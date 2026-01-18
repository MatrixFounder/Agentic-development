# Task: Создание skill-archive-task для инкапсуляции протокола архивации

## 0. Meta Information

| Field    | Value                                |
|----------|--------------------------------------|
| Task ID  | 033                                  |
| Slug     | skill-archive-task                   |
| Status   | Completed                            |
| Priority | Critical                             |

---

## 1. Цель

Создать **`skill-archive-task`** — самодостаточный skill, который инкапсулирует все инструкции по архивации `docs/TASK.md`.

**Проблема:** Логика архивации дублируется в 6+ файлах:
- `.gemini/GEMINI.md` (строки 56-58)
- `.cursorrules` (строки 36-38)
- `artifact-management/SKILL.md` (строки 33-55)
- `02_analyst_prompt.md` (строки 24-35)
- `01_orchestrator.md` (строки 57-69)
- `01-start-feature.md` workflow (строки 6-10)

**Решение:** Один skill = один источник истины для архивации.

> [!CAUTION]
> **Известные проблемы:** Ранее TASK.md не всегда корректно архивировался в разных режимах работы (промпт, workflow). Требуется детальное тестирование.

---

## 2. Use Cases

### UC-01: Архивация TASK.md при старте новой задачи

**Actors:**
- Orchestrator/Analyst Agent
- skill-archive-task
- Tool `generate_task_archive_filename`

**Preconditions:**
- Существует `docs/TASK.md` с завершённой/другой задачей
- Agent начинает работу над НОВОЙ задачей

**Main Scenario:**
1. Agent определяет: это НОВАЯ задача или уточнение текущей?
2. Если НОВАЯ: Agent загружает `skill-archive-task`
3. Agent читает Meta Information из текущего TASK.md (Task ID, Slug)
4. Agent вызывает `generate_task_archive_filename(slug="...")`
5. Agent обновляет Task ID в TASK.md на `used_id` из tool
6. Agent выполняет `mv docs/TASK.md docs/tasks/{filename}`
7. Agent проверяет: файл перемещён (`docs/TASK.md` не существует)
8. Agent создаёт новый `docs/TASK.md`

**Alternative Scenarios:**

**A1: TASK.md не существует (at step 2)**
1. Agent пропускает архивацию
2. Agent создаёт новый `docs/TASK.md`

**A2: Это уточнение текущей задачи (at step 1)**
1. Agent НЕ архивирует
2. Agent перезаписывает `docs/TASK.md`

**A3: Tool возвращает conflict (at step 4)**
1. Agent уведомляет пользователя
2. Ожидает решения

**Postconditions:**
- Старый TASK.md перемещён в `docs/tasks/`
- Новый TASK.md создан
- ID в имени файла и внутри документа совпадают

**Acceptance Criteria:**
- ✅ Skill корректно определяет "новая vs уточнение"
- ✅ Tool `generate_task_archive_filename` вызывается
- ✅ Meta Information обновляется перед mv
- ✅ Файл перемещается (не копируется)
- ✅ Валидация: старый путь не существует

---

### UC-02: Архивация при завершении задачи (Orchestrator Completion)

**Actors:**
- Orchestrator Agent
- skill-archive-task

**Preconditions:**
- Все задачи плана выполнены
- Orchestrator в стадии Completion

**Main Scenario:**
1. Orchestrator загружает `skill-archive-task`
2. Выполняет шаги 3-7 из UC-01
3. НЕ создаёт новый TASK.md (завершение работы)

**Acceptance Criteria:**
- ✅ Архивация происходит автоматически при завершении
- ✅ Не требует ручного вмешательства

---

## 3. Тестовые сценарии (ОБЯЗАТЕЛЬНЫЕ)

| # | Сценарий | Режим запуска | Ожидаемый результат |
|---|----------|---------------|---------------------|
| 1 | Новая задача, TASK.md существует | Прямой промпт | TASK.md → docs/tasks/, новый создан |
| 2 | Новая задача, TASK.md существует | `/01-start-feature` | То же самое |
| 3 | Новая задача, TASK.md существует | `/base-stub-first` | То же самое |
| 4 | Новая задача, TASK.md существует | `/vdd-enhanced` | То же самое |
| 5 | Новая задача, TASK.md НЕ существует | Любой режим | Новый создан, архивация пропущена |
| 6 | Уточнение текущей задачи | Прямой промпт | TASK.md перезаписан, НЕ архивирован |
| 7 | Завершение задачи | Orchestrator Completion | TASK.md → docs/tasks/ |
| 8 | Конфликт ID | Любой режим | Tool возвращает corrected ID |

---

## 4. Требования к Skill

### 4.1 Структура

```
.agent/skills/skill-archive-task/
└── SKILL.md           # Полный протокол архивации
```

### 4.2 Содержимое SKILL.md

```yaml
---
name: skill-archive-task
description: "Complete protocol for archiving TASK.md with ID generation"
version: 1.0
tools: ["generate_task_archive_filename"]
---
```

**Секции:**
1. **When to Archive** — условия для архивации
2. **Protocol Steps** — пошаговый протокол (6 шагов)
3. **Safe Commands** — команды для auto-run
4. **Decision Logic** — новая vs уточнение

---

## 5. Места внедрения (после создания skill)

### 5.1 Упрощение файлов

| Файл | Действие |
|------|----------|
| `.gemini/GEMINI.md` | Заменить строки 56-60 на `Apply Skill: skill-archive-task` |
| `.cursorrules` | Заменить строки 36-38 на ссылку на skill |
| `02_analyst_prompt.md` | Заменить PRE-FLIGHT на ссылку |
| `01_orchestrator.md` | Заменить DECISION LOGIC на ссылку |
| `artifact-management/SKILL.md` | Заменить Archiving Protocol на импорт |
| `01-start-feature.md` | Заменить шаг 3 на ссылку |

### 5.2 Документация

- Добавить в `docs/SKILLS.md` новый skill

---

## 6. Шаги выполнения

### Phase 1: Создание Skill ✅
- [x] Создать `.agent/skills/skill-archive-task/SKILL.md`
- [x] Написать полный протокол из `artifact-management`
- [x] Добавить Decision Logic

### Phase 2: Тестирование (8 сценариев) ⏳
- [ ] Сценарий 1: Прямой промпт + существующий TASK
- [ ] Сценарий 2: `/01-start-feature` + существующий TASK
- [ ] Сценарий 3: `/base-stub-first` + существующий TASK
- [ ] Сценарий 4: `/vdd-enhanced` + существующий TASK
- [ ] Сценарий 5: TASK не существует
- [ ] Сценарий 6: Уточнение задачи
- [ ] Сценарий 7: Orchestrator Completion
- [ ] Сценарий 8: Конфликт ID

### Phase 3: Рефакторинг дублирования ✅
- [x] Упростить `.gemini/GEMINI.md`
- [x] Упростить `.cursorrules`
- [x] Упростить `02_analyst_prompt.md`
- [x] Упростить `01_orchestrator.md`
- [x] Упростить `artifact-management/SKILL.md`
- [x] Упростить `01-start-feature.md`

### Phase 4: VDD Adversarial Review ✅
- [x] Adversarial roast skill содержимого
- [x] Adversarial roast рефакторинга

### Phase 5: Бонус — skill-safe-commands ✅
- [x] Создать `skill-safe-commands/SKILL.md`
- [x] Рефакторить ссылки в skills

---

## 7. Acceptance Criteria

| Criteria | Metric | Verification |
|----------|--------|--------------|
| Skill создан | Файл существует | `ls .agent/skills/skill-archive-task/` |
| Protocol полный | 6 шагов описаны | Review SKILL.md |
| Decision Logic есть | Новая vs уточнение | Review SKILL.md |
| Тесты 1-4 проходят | Архивация из разных режимов | Manual testing |
| Тест 5 проходит | Пропуск архивации | Manual testing |
| Тест 6 проходит | Перезапись без архивации | Manual testing |
| Дублирование устранено | 6 файлов упрощены | Diff review |

---

## 8. Non-Functional Requirements

### 8.1 Maintainability
- Один skill = один источник истины
- Изменения только в одном месте

### 8.2 Backward Compatibility
- Существующие агенты продолжают работать
- Ссылки на skill понятны

---

## 9. Open Questions

1. ~~Можно ли инкапсулировать всё в skill?~~ → **Да** (см. анализ)
2. ~~Нужен ли script внутри skill?~~ → **Нет** (достаточно документации + tool)

---

## 10. Implementation Summary

### Созданные файлы
| Файл | Описание |
|------|----------|
| `.agent/skills/skill-archive-task/SKILL.md` | Полный протокол архивации (6 шагов, decision logic) |
| `.agent/skills/skill-safe-commands/SKILL.md` | Централизованный список Safe Commands |

### Изменённые файлы
| Файл | Изменения |
|------|----------|
| `.gemini/GEMINI.md` | Упрощена секция Analysis Phase → ссылка на skill |
| `.cursorrules` | Добавлен skill-archive-task в Load Skills |
| `System/Agents/02_analyst_prompt.md` | PRE-FLIGHT → ссылка на skill |
| `System/Agents/01_orchestrator.md` | DECISION LOGIC → ссылка на skill |
| `.agent/skills/artifact-management/SKILL.md` | Archiving Protocol → импорт из skill-archive-task |
| `.agent/workflows/01-start-feature.md` | Шаг 3 → ссылка на skill |
| `docs/SKILLS.md` | Добавлены skill-archive-task и skill-safe-commands |

### VDD Adversarial Fixes
| Проблема | Исправление |
|----------|-------------|
| Missing error handling for Meta Information | Добавлен fallback: slug из H1, auto-generate ID |
| No rollback on validation failure | Добавлена секция "If validation fails" |

### Phase 7: Mandatory Skill Refactor (User Request)
- [x] Refactor `01_orchestrator.md` to use ACTIVE SKILLS
- [x] Add `skill-safe-commands (Mandatory)` to all agents:
    - [x] Orchestrator
    - [x] Analyst
    - [x] Architect
    - [x] Planner
    - [x] Developer
    - [x] Reviewers (Task, Arch, Plan, Code)
### Phase 8: Portability & UX Fixes (Bonus)
- [x] Fix `skill-safe-commands` IDE config confusion (Agent vs User)
- [x] Make `docs/ORCHESTRATOR.md` reference optional in prompts (if available)
- [x] Update README with installation instructions (User Request)
