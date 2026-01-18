# Task: Внедрение надежного tool для генерации и проверки ID задач при архивации

## 0. Meta Information

| Field    | Value                                |
|----------|--------------------------------------|
| Task ID  | 032                                  |
| Slug     | task-archive-id-tool                 |
| Status   | Completed                            |
| Priority | Medium                               |

---

## 1. Цель

Создать и внедрить dedicated tool в директории `.agent/tools/`, который будет отвечать за генерацию уникального sequential ID для архивных задач (формат `task-{ID}-{Slug}.md`) и проверку предложенного ID на уникальность.

Tool должен:
- Автоматически генерировать следующий свободный ID (с leading zeros, начиная с 001).
- Поддерживать ручной ввод желаемого ID (когда пользователь явно указывает его в новой задаче).
- Если предложенный ID уже занят — автоматически скорректировать на следующий свободный или вернуть ошибку с предложением альтернативы.
- Возвращать готовое имя файла для архивации (включая slug).

Это устранит гэпы и ошибки в нумерации, сделает процесс полностью автономным для агентов и безопасным при ручном вмешательстве пользователя.

---

## 2. Текущая ситуация

- Нумерация задач происходит вручную или через reasoning агентов (Orchestrator/Planner/Reviewer) при архивации `docs/TASK.md` → `docs/tasks/task-{ID}-{Slug}.md`.
- Агенты имеют доступ к filesystem через существующие tools в `.agent/tools/schemas.py` (`list_directory`, `read_file` и т.д.).
- Уже наблюдаются гэпы в нумерации (например, пропуски 017–029), что указывает на ошибки в подсчете.
- Пользователь иногда вручную задает ID для «вдумчивых» новых задач (указывает желаемый номер в описании или заголовке TASK.md).
- Существует skill `artifact-management` с Archiving Protocol, который должен быть расширен.

---

## 3. Use Case

### UC-01: Автоматическая генерация ID при архивации

**Actors:**
- Orchestrator/Analyst Agent
- Tool `generate_task_archive_filename`
- File System

**Preconditions:**
- Существует `docs/TASK.md` с завершённой задачей
- Секция "0. Meta Information" содержит Task ID и Slug
- Директория `docs/tasks/` существует

**Main Scenario:**
1. Agent определяет необходимость архивации текущего TASK.md
2. Agent вызывает tool `generate_task_archive_filename` с `proposed_id=None` и `slug` из Meta Information
3. Tool сканирует директорию `docs/tasks/`
4. Tool собирает все существующие ID из имён файлов `task-{XXX}-*.md`
5. Tool находит максимальный ID и вычисляет следующий (`max + 1`)
6. Tool форматирует ID с leading zeros (`{:03d}`)
7. Tool возвращает filename: `task-{formatted_id}-{slug}.md` и `used_id`
8. **Agent обновляет Task ID внутри `docs/TASK.md`** (секция Meta Information) на полученный `used_id`
9. Agent перемещает обновлённый файл `docs/TASK.md` → `docs/tasks/{filename}`

**Alternative Scenarios:**

**A1: Директория `docs/tasks/` не существует (at step 3)**
1. Tool создаёт директорию `docs/tasks/`
2. Continue to step 4 with empty file list
3. Tool возвращает `task-001-{slug}.md`

**A2: Нет существующих task файлов (at step 4)**
1. Tool возвращает `task-001-{slug}.md`
2. Continue to step 8

**Postconditions:**
- Task ID внутри файла обновлён на финальный `used_id`
- Файл перемещён в `docs/tasks/` с уникальным sequential ID
- ID в имени файла и внутри документа совпадают

**Acceptance Criteria:**
- ✅ При пустой директории возвращается ID `001`
- ✅ При наличии `task-005-*.md` следующий ID = `006`
- ✅ Гэпы в нумерации игнорируются (max ID + 1, не заполнение гэпов)
- ✅ Slug приводится к lowercase с дефисами
- ✅ Task ID внутри архивированного файла соответствует `used_id` из tool

---

### UC-02: Ручное указание желаемого ID

**Actors:**
- User
- Orchestrator/Analyst Agent
- Tool `generate_task_archive_filename`

**Preconditions:**
- Пользователь указал желаемый ID в TASK.md (секция Meta Information или заголовок)
- Директория `docs/tasks/` существует

**Main Scenario:**
1. Agent парсит TASK.md и находит явно указанный `Task ID`
2. Agent вызывает tool с `proposed_id="XXX"` и `slug`
3. Tool приводит `proposed_id` к формату `{:03d}`
4. Tool проверяет, существует ли файл `task-{proposed_id}-*.md`
5. Файл не найден → Tool возвращает `task-{proposed_id}-{slug}.md`
6. Agent перемещает файл

**Alternative Scenarios:**

**A1: Указанный ID уже занят, `allow_correction=True` (at step 4)**
1. Tool находит следующий свободный ID
2. Tool возвращает filename со скорректированным ID
3. Tool добавляет в response `"status": "corrected"` и `"message": "ID 031 занят, использован 033"`
4. Agent логирует предупреждение и продолжает

**A2: Указанный ID уже занят, `allow_correction=False` (at step 4)**
1. Tool возвращает `"status": "conflict"`
2. Tool добавляет `"message": "ID 031 занят. Предложенная альтернатива: 033"`
3. Agent сообщает пользователю о конфликте
4. Use case завершается без перемещения файла

**A3: Некорректный proposed_id (не число) (at step 3)**
1. Tool возвращает ошибку: `"status": "error"`, `"message": "Invalid ID format"`
2. Use case завершается

**Postconditions:**
- При успехе: файл перемещён с указанным или скорректированным ID
- При конфликте: пользователь уведомлён

**Acceptance Criteria:**
- ✅ `proposed_id="31"` корректно форматируется как `"031"`
- ✅ `proposed_id="001"` при занятом ID возвращает следующий свободный
- ✅ Некорректный ввод (`"abc"`) возвращает понятную ошибку
- ✅ При `allow_correction=False` возвращается конфликт, а не автокоррекция

---

### UC-03: Присвоение ID новой задаче при создании TASK.md

**Actors:**
- Orchestrator/Analyst Agent
- Tool `generate_task_archive_filename`
- User (опционально)

**Preconditions:**
- Предыдущая задача заархивирована (UC-01 или UC-02 завершён)
- Agent готов создать новый `docs/TASK.md`

**Main Scenario:**
1. Agent определяет, что нужно создать новую задачу
2. Agent вызывает tool `generate_task_archive_filename` с `proposed_id=None` и временным `slug` (например, "new-task")
3. Tool возвращает следующий свободный ID (например, `"033"`)
4. Agent создаёт новый `docs/TASK.md` с секцией Meta Information:
   ```markdown
   ## 0. Meta Information
   | Field    | Value       |
   |----------|-------------|
   | Task ID  | 033         |
   | Slug     | TBD         |
   ```
5. Agent/User наполняет TASK.md содержанием
6. После финализации Slug обновляется на реальное значение

**Alternative Scenarios:**

**A1: Пользователь хочет конкретный ID для новой задачи**
1. Пользователь указывает желаемый ID (например, "050")
2. Agent вызывает tool с `proposed_id="050"`
3. Tool проверяет доступность и возвращает результат
4. Continue to step 4 with returned ID

**Postconditions:**
- Новый TASK.md создан с зарезервированным уникальным ID
- ID гарантированно не конфликтует с существующими архивами

**Acceptance Criteria:**
- ✅ После архивации task-032 новая задача получает ID `033`
- ✅ ID присваивается ДО наполнения TASK.md содержанием
- ✅ Sequential нумерация сохраняется

---

## 4. Требования к Tool

### 4.1 Название

`generate_task_archive_filename`

### 4.2 Интерфейс (Python)

```python
def generate_task_archive_filename(
    slug: str,                          # Краткое название задачи, латиницей с дефисами
    proposed_id: Optional[str] = None,  # Например "031" или "31"
    allow_correction: bool = True       # Если True — автоматически взять следующий при конфликте
) -> dict:
    """
    Возвращает:
    {
        "filename": "task-031-new-feature.md",
        "used_id": "031",
        "status": "generated" | "corrected" | "conflict" | "error",
        "message": Optional[str]  # Для логов/отчета
    }
    """
```

### 4.3 Логика работы

1. Сканировать директорию `docs/tasks/` (использовать `os.listdir` или вызвать `list_directory` tool).
2. Собрать все существующие ID: парсить имена файлов вида `task-XXX-*`, брать числовую часть XXX.
3. Если `proposed_id is None`:
   - Найти максимальный ID → +1 → формат `{:03d}`.
4. Если `proposed_id` задан:
   - Привести к int, отформатировать `{:03d}`.
   - Проверить, существует ли файл с этим ID (`task-{proposed_id}-*.md`).
   - Если НЕ существует — использовать его.
   - Если существует и `allow_correction=True` — найти следующий свободный ID.
   - Если `allow_correction=False` — вернуть ошибку с предложением альтернативы.
5. Валидировать и нормализовать slug (lowercase, дефисы вместо пробелов, без спецсимволов).
6. Сформировать полное имя файла: `task-{formatted_id}-{slug}.md`.

### 4.4 Дополнительные требования

- Tool должен быть детерминированным и не зависеть от промптов — чистая логика.
- Добавить в `.agent/tools/schemas.py` как новый tool schema.
- Добавить функцию-исполнитель в соответствующий dispatcher (если есть).

---

## 5. Места внедрения

После создания tool необходимо обновить:

### 5.1 Skills

- **`artifact-management`** (`/.agent/skills/artifact-management/SKILL.md`):
  - Добавить секцию про использование `generate_task_archive_filename` tool
  - Обновить Archiving Protocol с явной инструкцией вызова tool

### 5.2 System Prompts (Agents)

- **Orchestrator** (`System/Agents/01_orchestrator.md`):
  - Добавить инструкцию: "При архивации TASK.md всегда используй tool `generate_task_archive_filename`"

- **Analyst** (`System/Agents/02_analyst_prompt.md`):
  - Добавить проверку на наличие желаемого ID в Meta Information

### 5.3 Документация

- **`docs/ARCHITECTURE.md`**:
  - Добавить `generate_task_archive_filename` в секцию "4. Tool Execution Subsystem"

- **`docs/ORCHESTRATOR.md`** (если существует):
  - Описать новый tool

---

## 6. Шаги выполнения

### Phase 1: Создание Tool ✅

1. **Анализ текущего кода**
   - [x] Просмотреть `.agent/tools/schemas.py` — добавить новую schema
   - [x] Проверить, есть ли dispatcher/executor для tools → Найден `scripts/tool_runner.py`

2. **Реализация**
   - [x] Создать функцию `generate_task_archive_filename` в `.agent/tools/task_id_tool.py`
   - [x] Добавить schema в `TOOLS_SCHEMAS`
   - [x] Интегрировать с dispatcher (`scripts/tool_runner.py`)

### Phase 2: Тестирование ✅

3. **Unit тесты** (29 тестов)
   - [x] proposed_id=None → следующий ID
   - [x] proposed_id свободен → использовать его
   - [x] proposed_id занят + allow_correction=True → скорректировать
   - [x] proposed_id занят + allow_correction=False → conflict
   - [x] Некорректный proposed_id → error
   - [x] Slug нормализация
   - [x] **Добавлено:** Поддержка 4+ значных ID (`\d{3,}`)

### Phase 3: Интеграция ✅

4. **Обновление skills и prompts**
   - [x] Обновить `artifact-management` skill
   - [x] Обновить промпты Orchestrator, Analyst

5. **Обновление документации**
   - [x] Обновить `docs/ARCHITECTURE.md`
   - [x] Обновить `docs/ORCHESTRATOR.md`
   - [x] Обновить `docs/SKILLS.md`

### Phase 4: VDD Adversarial Review ✅ (Дополнительная фаза)

6. **Sarcasmotron Roast**
   - [x] Round 1: Найдены 2 проблемы (race condition, 3-digit limit)
   - [x] Исправлены обе проблемы
   - [x] Round 2: APPROVED (Hallucination Convergence)

### Phase 5: Safe Commands Protocol ✅ (Дополнительная фаза)

7. **Расширение протокола Auto-Run**
   - [x] Добавлен список безопасных команд для автозапуска:
     - Read-only: `ls`, `cat`, `head`, `tail`, `find`, `grep`, `tree`, `wc`
     - Git read: `git status`, `git log`, `git diff`, `git show`, `git branch`
     - Archiving: `mv docs/TASK.md docs/tasks/...`
     - Tools: `generate_task_archive_filename`, `list_directory`, `read_file`

### Phase 6: Финализация ✅

8. **Dogfooding**
   - [x] Протестирован tool на реальном `docs/TASK.md` (task-031)
   - [x] Заархивирован task-031 → `docs/tasks/task-031-verify-docs-v322.md`
   - [x] Создан новый `docs/TASK.md` для task-032

9. **Обновление версии и документации**
   - [x] CHANGELOG.md: v3.2.5 (EN + RU)
   - [x] README.md: bump to v3.2.5 + Python installation requirements
   - [x] README.ru.md: bump to v3.2.5 + Python installation requirements

---

## 7. Acceptance Criteria

| Criteria | Metric | Verification |
|----------|--------|--------------|
| Tool создан | Файл `.agent/tools/task_id_tool.py` существует | `ls .agent/tools/` |
| Schema добавлена | `generate_task_archive_filename` в `TOOLS_SCHEMAS` | Grep `schemas.py` |
| Авто-генерация | При пустой директории → `001` | Unit test |
| Sequential ID | max ID + 1, не заполнение гэпов | Unit test |
| Conflict handling | `allow_correction=False` возвращает conflict | Unit test |
| Slug normalization | "New Feature" → "new-feature" | Unit test |
| Integration | `artifact-management` skill обновлён | Review |
| Docs updated | ARCHITECTURE.md содержит описание tool | Review |

---

## 8. Non-Functional Requirements

### 8.1 Performance
- Tool должен выполняться < 100ms даже при 1000 файлов в `docs/tasks/`

### 8.2 Security
- Tool НЕ выполняет операции с файлами (только генерирует имя)
- Фактическое перемещение файла остаётся за агентом (через `mv` или соответствующий tool)

### 8.3 Compatibility
- Совместимость с существующим форматом именования `task-{ID}-{Slug}.md`
- Не нарушать работу существующих tools в `schemas.py`

---

## 9. Open Questions

1. ~~Где хранится dispatcher/executor для tools?~~ → **Решено:** `scripts/tool_runner.py`
2. ~~Нужен ли отдельный tool для полного цикла архивации (generate + move + git commit)?~~ → **Решение:** Нет, разделение ответственности лучше (tool генерирует имя, агент выполняет mv)
3. ~~Должны ли гэпы в нумерации заполняться или игнорироваться?~~ → **Решение:** Игнорировать (max + 1)

---

## 10. Implementation Summary (Добавлено по результатам)

### Созданные файлы
| Файл | Описание |
|------|----------|
| `.agent/tools/task_id_tool.py` | Основная реализация tool |
| `.agent/tools/test_task_id_tool.py` | 29 unit-тестов |

### Изменённые файлы
| Файл | Изменения |
|------|----------|
| `.agent/tools/schemas.py` | Добавлена schema |
| `scripts/tool_runner.py` | Зарегистрирован tool в dispatcher |
| `.agent/skills/artifact-management/SKILL.md` | Обновлён Archiving Protocol + Safe Commands |
| `System/Agents/01_orchestrator.md` | Safe Commands section + tool usage |
| `System/Agents/02_analyst_prompt.md` | Tool usage for ID reservation |
| `docs/ARCHITECTURE.md` | Добавлен tool в таблицу Available Tools |
| `docs/ORCHESTRATOR.md` | Добавлен tool в таблицу Supported Tools |
| `docs/SKILLS.md` | Добавлен tool в секцию Executable Skills |
| `CHANGELOG.md` | v3.2.5 entry (EN + RU) |
| `README.md` | v3.2.5 + Python requirements |
| `README.ru.md` | v3.2.5 + Python requirements |
