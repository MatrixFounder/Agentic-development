# Техническое Задание (ТЗ): Интеграция structured tool calling в фреймворк Agentic-development

**Дата:** 14 января 2026  
**Версия ТЗ:** 1.0  
**Ответственный:** Maintainer / Контрибьютор  
**Репозиторий:** https://github.com/MatrixFounder/Agentic-development  
**Цель релиза:** v3.1.0 (минорный релиз с backwards-compatibility)  
**Предпосылки:** Текущая версия v3.0.1 с модульной системой Skills. Orchestrator уже работает с LLM API (предположительно xAI/OpenAI-совместимый).

## Цель

Перейти от текстового описания внешних действий (например, «выведи команду `pytest ...`») к **structured tool calling** (function calling / tools) для executable skills.  

Это решит текущие проблемы:
- Ненадёжный парсинг текстового вывода агента.
- Ошибки в формате команд.
- Зависимость от дисциплины LLM.
- Сложность обработки ошибок выполнения.

После реализации:
- Надёжное выполнение внешних действий (тесты, git, файлы).
- Атомарность операций.
- Полная совместимость с моделями, поддерживающими tools (Grok-4, GPT-4o, Claude 3.5 Sonnet, Gemini 1.5).
- Минимальные изменения в существующих промптах и skills.

## Задачи

1. **Определить категорию executable skills**  
   - Выделить в `docs/SKILLS.md` новую категорию «Executable Skills» (те, что требуют tool calling).  
   - Обновить существующие skills (например, `skill-testing-best-practices.md`, `skill-git-ops.md` если есть) с явным указанием использовать tool вместо текста.

2. **Реализовать поддержку tool calling в Orchestrator**  
   - Добавить конфигурацию tools (JSON schema) в Orchestrator.  
   - В цикле агента: отправлять tools в API, обрабатывать tool_calls, выполнять инструменты, возвращать результаты в контекст.  
   - Обеспечить fallback на текстовый режим для моделей без tool calling.

3. **Определить базовый набор tools**  
   - Реализовать минимум 5–7 популярных tools (см. ниже).  
   - Добавить их схемы в новый файл `.agent/tools/schemas.json` или напрямую в код Orchestrator.

4. **Обновить документацию**  
   - Добавить раздел в `docs/SKILLS.md` и `docs/ORCHESTRATOR.md` (или новый `docs/TOOLS.md`).  
   - Описать, как добавлять новые tools.

5. **Тестирование и backwards-compatibility**  
   - Протестировать на существующих workflow (Stub-First, VDD).  
   - Сохранить совместимость: если модель не поддерживает tools — fallback на парсинг текста.

## Предлагаемые популярные Tools

В рамках современных агентных фреймворков (LangChain, CrewAI, Autogen, MCP-подобные подходы) стандартный набор tools для разработки включает операции с файловой системой, тестами и git. Предлагаю следующий минимальный viable набор (все реализуемы в Python без внешних зависимостей, кроме subprocess для shell-команд):

| Tool name              | Описание                                                                 | Параметры (JSON schema)                                                                 | Когда использовать (пример в skill) |
|-----------------------|--------------------------------------------------------------------------|------------------------------------------------------------------------------------------|-------------------------------------|
| `run_tests`           | Запуск тестов проекта (pytest)                                           | `command`: str (опционально, default: "pytest -q")<br>`cwd`: str (опционально)           | В Developer/Reviewer после изменений кода |
| `git_status`          | Получить статус репозитория                                              | Нет                                                                                     | Перед commit |
| `git_add`             | Добавить файлы в staging                                                 | `files`: array[str]                                                                     | После создания/изменения файлов |
| `git_commit`          | Создать commit                                                           | `message`: str (required)                                                               | После успешных тестов |
| `read_file`           | Прочитать содержимое файла                                               | `path`: str (required)                                                                  | Для анализа существующего кода |
| `write_file`          | Записать/перезаписать файл                                               | `path`: str (required)<br>`content`: str (required)                                     | Для создания нового кода/артефактов |
| `list_directory`      | Список файлов в директории                                               | `path`: str (default: ".")<br>`recursive`: bool (default: false)                         | Для ориентирования в проекте |

**Почему именно эти?**  
- Это стандартный набор в большинстве MCP-агентных систем (Multi-Agent Collaboration Protocol, как в Autogen или CrewAI).  
- Покрывают 90% нужд разработки: тесты, git, файлы.  
- Легко расширяемы (добавить `search_code` с ripgrep позже).

## Примеры встраивания в пайплайн разработки

### 1. Обновление skill-testing-best-practices.md

```markdown
### Запуск тестов

ТЫ ДОЛЖЕН использовать tool calling:

- Вызови tool `run_tests` с параметром command = "pytest -q --tb=short".
- ДОЖДИСЬ результата от Orchestrator.
- Если тесты фейлятся — анализируй ошибки и исправляй.

НЕ пиши команду текстом в выводе.
```

### 2. Пример цикла в Orchestrator (псевдокод Python)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Запустить тесты",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Команда pytest"}
                }
            }
        }
    },
    # ... другие tools
]

def execute_tool(tool_call):
    if tool_call.name == "run_tests":
        import subprocess
        result = subprocess.run(tool_call.args["command"], shell=True, capture_output=True)
        return {"output": result.stdout.decode(), "errors": result.stderr.decode(), "returncode": result.returncode}

# В основном цикле агента
response = client.chat.completions.create(
    model="grok-4",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = execute_tool(tool_call)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })
    # Повторный запрос к модели с результатами
```

### 3. Пример поведения агента (Developer в Stub-First)

Агент вместо текста:
```json
{
  "tool_calls": [
    {
      "name": "run_tests",
      "arguments": {"command": "pytest -q"}
    }
  ]
}
```

Orchestrator выполняет → возвращает результаты → агент анализирует и продолжает (исправляет код → write_file → run_tests снова).

### 4. В пайплайне VDD (adversarial)

Sarcasmotron может вызывать `read_file` для анализа кода, затем `run_tests` для поиска слабых мест.

## Приёмка

- PR с изменениями в Orchestrator, новыми tools, обновлёнными skills и документацией.
- End-to-end тесты: запуск простого workflow (создание функции + тесты + commit).
- Проверка на Grok-4 и fallback-режиме.
- Минимум 2 approve от контрибьюторов.

Это ТЗ доведёт фреймворк до уровня современных tool-enabled агентных систем. 

# Приложение к ТЗ: Примеры реализации Tools

**Приложение к Техническому Заданию "Интеграция structured tool calling в фреймворк Agentic-development" (v3.1.0)**  
**Дата:** 14 января 2026  
**Цель приложения:** Предоставить конкретные, готовые к копированию примеры JSON-схем tools и кода их выполнения в Orchestrator. Это позволит ускорить реализацию и обеспечить единообразие.

## 1. Полный список JSON-схем tools (рекомендуемый базовый набор)

Сохранить в отдельный файл `.agent/tools/schemas.py` (как список словарей) или напрямую в коде Orchestrator.

```python
TOOLS_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Запустить тесты проекта с помощью pytest. Возвращает stdout, stderr и код возврата.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Полная команда для запуска тестов. По умолчанию 'pytest -q --tb=short'.",
                        "default": "pytest -q --tb=short"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Рабочая директория для запуска (по умолчанию корень проекта).",
                        "default": "."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Прочитать содержимое файла из проекта.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Относительный путь к файлу."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Создать или перезаписать файл в проекте.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Относительный путь к файлу."},
                    "content": {"type": "string", "description": "Полное содержимое файла."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Получить список файлов и папок в директории.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": ".", "description": "Путь к директории."},
                    "recursive": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Получить текущий статус git-репозитория.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_add",
            "description": "Добавить файлы в staging area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {"type": "array", "items": {"type": "string"}, "description": "Список путей файлов."}
                },
                "required": ["files"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Создать commit с указанным сообщением.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Сообщение коммита."}
                },
                "required": ["message"]
            }
        }
    }
]
```

## 2. Пример реализации функции execute_tool в Orchestrator

```python
import subprocess
import json
import os
from pathlib import Path

def execute_tool(tool_call):
    """Выполняет tool_call и возвращает результат в формате, подходящем для сообщения 'tool'."""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)  # arguments приходят как строка JSON
    
    repo_root = Path.cwd()  # или явно задать корень проекта
    
    try:
        if name == "run_tests":
            command = args.get("command", "pytest -q --tb=short")
            cwd = args.get("cwd", ".")
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, cwd=cwd
            )
            return {
                "output": result.stdout,
                "errors": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
        
        elif name == "read_file":
            path = repo_root / args["path"]
            if not path.exists():
                raise FileNotFoundError(f"File {args['path']} not found")
            content = path.read_text(encoding="utf-8")
            return {"content": content, "path": args["path"]}
        
        elif name == "write_file":
            path = repo_root / args["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(args["content"], encoding="utf-8")
            return {"status": "written", "path": args["path"], "size_bytes": len(args["content"])}
        
        elif name == "list_directory":
            path = repo_root / args.get("path", ".")
            recursive = args.get("recursive", False)
            files = []
            if recursive:
                for p in path.rglob("*"):
                    files.append(str(p.relative_to(repo_root)))
            else:
                for p in path.iterdir():
                    files.append(str(p.relative_to(repo_root)))
            return {"files": sorted(files), "path": args.get("path", ".")}
        
        elif name == "git_status":
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True, check=False
            )
            return {"status": result.stdout.strip(), "returncode": result.returncode}
        
        elif name == "git_add":
            files = args["files"]
            result = subprocess.run(["git", "add"] + files, capture_output=True, text=True)
            return {"output": result.stdout, "errors": result.stderr, "returncode": result.returncode}
        
        elif name == "git_commit":
            message = args["message"]
            result = subprocess.run(
                ["git", "commit", "-m", message], capture_output=True, text=True
            )
            return {"output": result.stdout, "errors": result.stderr, "returncode": result.returncode}
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return {"error": str(e), "success": False}
```

## 3. Пример интеграции в цикл Orchestrator (упрощённо)

```python
# В основном цикле обработки ответа агента
response = client.chat.completions.create(
    model=current_model,
    messages=messages,
    tools=TOOLS_SCHEMAS,
    tool_choice="auto"  # или "required" для принудительного вызова
)

message = response.choices[0].message

if message.tool_calls:
    for tool_call in message.tool_calls:
        result = execute_tool(tool_call)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": json.dumps(result, ensure_ascii=False, indent=2)
        })
    # Повторный запрос к модели с результатами tools
    return continue_agent_loop(messages)
else:
    # Обычная обработка текстового ответа
    ...
```

Эти примеры полностью рабочие (при минимальной адаптации под текущую структуру Orchestrator). Они покрывают все предложенные tools и могут быть расширены. Рекомендуется начать реализацию с `run_tests`, `read_file` и `write_file` — они дадут максимальный эффект сразу.


# Приложение к ТЗ: Пояснения по работе агента с tool calling

**Приложение к Техническому Заданию "Интеграция structured tool calling в фреймворк Agentic-development" (v3.1.0)**  
**Дата:** 14 января 2026  

## Общий принцип

Агент (LLM) в фреймворке **Agentic-development** не выполняет Python-скрипты или внешние команды напрямую и самостоятельно. Все внешние действия происходят под строгим контролем **Orchestrator** — центрального управляющего компонента фреймворка. Это обеспечивает безопасность, предсказуемость и возможность валидации операций.

## Текущая реализация (v3.0.1) — текстовый режим

- Агент получает задачу, промпт и загруженные skills.
- При необходимости внешнего действия (запуск тестов, чтение/запись файлов, git-операции) агент описывает его текстом в строго заданном формате, например:
  ```markdown
  >>> RUN COMMAND
  pytest -q --tb=short
  ```
  или
  ```markdown
  >>> WRITE FILE: src/utils.py
  ```python
  def hello():
      return "world"
  ```
  ```
- Orchestrator парсит текстовый вывод, выполняет проверку безопасности и запускает соответствующую операцию (subprocess, pathlib, git-операции).
- Результат возвращается агенту в следующем сообщении, цикл продолжается.

**Преимущества:** совместимость с моделями без поддержки tool calling.  
**Недостатки:** зависимость от точного формата вывода, риск ошибок парсинга.

## Предлагаемая реализация (v3.1.0) — structured tool calling

Реализация использует нативный механизм function/tool calling современных моделей (Grok-4, GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 и др.).

- Агент получает в промпте описание доступных tools (JSON-схемы: `run_tests`, `read_file`, `write_file`, `git_commit` и т.д.).
- При необходимости действия агент генерирует structured tool_call в формате JSON:
  ```json
  {
    "tool_calls": [
      {
        "name": "run_tests",
        "arguments": {
          "command": "pytest -q --tb=short"
        }
      }
    ]
  }
  ```
- Orchestrator получает tool_call напрямую от API модели (без текстового парсинга).
- Orchestrator выполняет соответствующий код (subprocess, pathlib, git).
- Результат возвращается агенту как сообщение роли "tool":
  ```json
  {
    "role": "tool",
    "content": "{\"output\": \"...\", \"errors\": \"\", \"success\": true}"
  }
  ```
- Агент анализирует результат и продолжает работу (исправление кода, следующий tool_call и т.д.).

## Ключевые аспекты безопасности и автономности

- Агент самостоятельно принимает решение о вызове tool (на основе промпта, skills и контекста).
- Выполнение осуществляется исключительно через Orchestrator: агент не имеет прямого доступа к файловой системе, shell или интерпретатору Python.
- Доступны только заранее определённые tools с фиксированными схемами — произвольное выполнение кода, придуманного агентом, невозможно.
- Возможен fallback на текстовый режим для моделей без поддержки tool calling.
- Orchestrator может дополнительно реализовать сандбоксинг, валидацию путей и ограничения команд.

## Пример полного цикла (Developer реализует функцию)

1. Агент генерирует код → вызывает tool `write_file`.
2. Orchestrator записывает файл.
3. Агент вызывает tool `run_tests`.
4. Orchestrator запускает pytest → возвращает результат.
5. При неудачных тестах: агент анализирует ошибки → повторный `write_file` → `run_tests`.
6. При успехе: `git_add` → `git_commit`.

**Эффект внедрения:** повышение надёжности и скорости работы агентов за счёт устранения ошибок парсинга и сокращения лишних итераций. Фреймворк достигает уровня современных tool-enabled систем (CrewAI, Autogen, LangGraph) при сохранении уникальных особенностей (Stub-First, VDD, verification loops).