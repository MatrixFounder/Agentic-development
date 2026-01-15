# TASK: Интеграция structured tool calling в фреймворк Agentic-development

**Дата:** 14 января 2026  
**Версия TASK:** 1.0  
**Ответственный:** Maintainer / Контрибьютор  
**Репозиторий:** https://github.com/MatrixFounder/Agentic-development  
**Цель релиза:** v3.1.2 (минорный релиз с backwards-compatibility)  
**Предпосылки:** Текущая версия v3.1.1 с модульной системой Skills. Orchestrator уже работает с LLM API (предположительно xAI/OpenAI-совместимый).

## 1. Обоснование и Цель

Переход к **structured tool calling** (function calling) — это качественный скачок зрелости фреймворка, обеспечивающий следующие преимущества:

### 1. Железная надёжность (Reliability)
Исключение ошибок парсинга. Агент отправляет типизированный JSON-объект, гарантированно понятный машине. Выполнение становится атомарным и предсказуемым, исключая итерации на исправление опечаток в командах.

### 2. Поддержка Native Tool Use
Современные модели (Grok-4, GPT-4o, Claude 3.5) оптимизированы для работы с инструментами. Фреймворк становится "родным" для передовых LLM, позволяя им использовать встроенные механизмы рассуждения (CoT) над инструментами.

### 3. Безопасность (Safety)
Переход от парсинга произвольных shell-команд к строгому "Белому списку" (Allowlist) функций. Аргументы валидируются до выполнения, что снижает риск инъекций.

### 4. Упрощение контекста (Simpler Prompts)
Снижение когнитивной нагрузки на модель за счёт удаления громоздких инструкций по форматированию текста. Агент сосредотачивается на бизнес-логике.

## 2. Сценарии Использования (Use Cases)

### UC-1: Выполнение инструмента Агентом
**Акторы:** Агент (Developer/Reviewer), Orchestrator.  
**Предусловия:** Агент находится в середине цикла выполнения задачи.  
**Основной сценарий:**
1. Агент решает выполнить внешнее действие (напр., прочитать файл).
2. Агент возвращает ответ с заполненным полем `tool_calls` (JSON), указывая имя инструмента и аргументы.
3. Orchestrator перехватывает `tool_calls`.
4. Orchestrator валидирует существование инструмента и аргументы.
5. Orchestrator выполняет инструмент (Python-функцию).
6. Orchestrator формирует сообщение с ролью `tool` (или `function`), содержащее output действия.
7. Orchestrator добавляет результат в контекст и вызывает модель снова.
**Постусловия:** Результат действия доступен Агенту для анализа.

### UC-2: Обработка ошибок выполнения
**Акторы:** Orchestrator, Агент.  
**Предусловия:** Агент вызвал инструмент с некорректными аргументами или инструмент вернул ошибку выполнения (non-zero exit code).
**Основной сценарий:**
1. Orchestrator пытается выполнить инструмент.
2. Возникает исключение или ошибка процесса (stderr).
3. Orchestrator перехватывает ошибку.
4. Orchestrator формирует JSON-ответ с полем `error` или `success: false`.
5. Агент получает сообщение с описанием ошибки.
6. Агент анализирует ошибку и повторяет вызов с исправленными аргументами.

### UC-3: Fallback на текстовый режим
**Акторы:** Агент, Orchestrator.  
**Предусловия:** Используемая модель не поддерживает native tool calling или API недоступно.
**Основной сценарий:**
1. Orchestrator определяет отсутствие поддержки tools.
2. Orchestrator инструктирует Агента использовать текстовый формат (как в v3.0.1).
3. Агент использует текстовый блок `>>> RUN COMMAND`.
4. Orchestrator использует regex-парсер для извлечения команды.
**Постусловия:** Система сохраняет работоспособность на старых моделях.

## 3. Спецификация Инструментов (Functional Requirements)

Система должна поддерживать следующий минимальный набор инструментов. Схемы приведены в Приложении.

| Tool name | Описание | Обязательные аргументы |
|-----------|----------|------------------------|
| `run_tests` | Запуск тестов проекта (pytest) | - |
| `git_status` | Получить статус репозитория | - |
| `git_add` | Добавить файлы в staging | `files` (list) |
| `git_commit` | Создать commit | `message` |
| `read_file` | Прочитать содержимое файла | `path` |
| `write_file` | Записать/перезаписать файл | `path`, `content` |
| `list_directory` | Просмотр содержимого папки | - |

## 4. Объем работ (Scope & Tasks)

1. **Определить категорию executable skills**
   - Выделить в `docs/SKILLS.md` новую категорию «Executable Skills».
   - Обновить `skill-testing-best-practices.md`, `skill-git-ops.md`.

2. **Реализовать поддержку tool calling в Orchestrator**
   - Добавить загрузку схем из `.agent/tools/schemas.py`.
   - Реализовать обработку `tool_calls` в основном цикле.
   - Реализовать функцию `execute_tool` (диспетчер).

3. **Обновить документацию**
   - Создать `docs/ORCHESTRATOR.md` (новое техническое описание работы диспетчера tools).
   - Создать руководство по добавлению новых tools.

4. **Тестирование**
   - Проверить работу на Grok-4 (Tools) и модели без Tools (Fallback).

## 5. Нефункциональные Требования

1. **Безопасность:**
   - Tools не должны позволять выход за пределы директории проекта (path traversal check).
   - Shell-команды в `run_tests` должны быть ограничены белым списком или запускаться в изолированном окружении (по возможности).
2. **Совместимость:**
   - Полная обратная совместимость со старыми промптами (через fallback).
3. **Производительность:**
   - Оверхед на обработку JSON tools не должен превышать 100мс.

## 6. Критерии Приёмки

- [ ] PR включает изменения в Orchestrator (поддержка `tool_calls`, диспетчер `execute_tool`).
- [ ] PR включает файл схем `.agent/tools/schemas.py`.
- [ ] Обновлены скиллы (как минимум Testing и Git-ops).
- [ ] End-to-end тест: Агент пишет тест -> падает -> чинит -> коммитит (используя tools).
- [ ] Протестирован fallback режим.

## 7. Следующие шаги (Future Work)

После стабилизации базового функционала tools (Post-v3.1.0):

1. **Чистка системных Промптов (Dynamic Prompt Assembly):**
   - Базовые промпты очищаются от инструкций по текстовому форматированию (`>>> RUN COMMAND`).
   - Orchestrator динамически добавляет блок "Legacy Formatting Instructions" ТОЛЬКО если модель не поддерживает native tools.
   - Это сохраняет чистоту промптов для умных моделей и совместимость для старых.
2. **Advanced Safety:**
   - Внедрение песочницы (Sandbox) для выполнения кода и команд.
   - Granular permissions (разные права для разных агентов).
3. **Расширение набора Tools:**
   - Добавление `search_code` (ripgrep / grep).
   - Интеграция с внешними API.

---

# Приложение: Примеры реализации Tools

**Цель:** Готовые к внедрению JSON-схемы и код.

## 1. JSON-схемы (Draft)

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

## 2. Реализация execute_tool (Reference)

```python
import subprocess
import json
import os
from pathlib import Path

def execute_tool(tool_call):
    """Выполняет tool_call и возвращает результат в формате, подходящем для сообщения 'tool'."""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    
    repo_root = Path.cwd()
    
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
        
        # ... остальные implementation ...
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return {"error": str(e), "success": False}
```

## 3. Пример цикла в Orchestrator

```python
if message.tool_calls:
    for tool_call in message.tool_calls:
        result = execute_tool(tool_call)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": json.dumps(result, ensure_ascii=False)
        })
    # Рекурсивный вызов или продолжение цикла
```