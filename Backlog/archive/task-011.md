# Техническое Задание (ТЗ): Доработка документации docs/SKILLS.md

**Дата:** 14 января 2026  
**Версия ТЗ:** 1.0  
**Ответственный:** Контрибьютор / Maintainer фреймворка Agentic-development  
**Репозиторий:** https://github.com/MatrixFounder/Agentic-development  
**Цель релиза:** v3.0.2 (или следующий минорный релиз)

## Цель

Сделать файл `docs/SKILLS.md` полностью самодостаточным руководством по системе Skills. После доработки любой разработчик или контрибьютор сможет:
- Понять механизм динамической загрузки skills без изучения исходного кода Orchestrator.
- Быстро тестировать отдельные skills в изоляции (без запуска полного workflow).
- Соблюдать best practices при создании и поддержке skills.

Это повысит онбординг, упростит отладку и предотвратит регрессии в навыках.

## Задачи

1. **Добавить раздел «Динамическая загрузка skills»**  
   - Описать пошаговый процесс сборки промпта Orchestrator'ом.  
   - Привести реальный пример из текущей роли (например, `08_agent_developer.md`).  
   - Показать упрощённый вид финального промпта.

2. **Добавить раздел «Изолированное тестирование skills»**  
   - Объяснить назначение (быстрая итерация, отладка, CI-тесты).  
   - Предоставить два варианта:  
     - Основной — локальный Python-скрипт.  
     - Альтернативный — n8n workflow с Code node на JavaScript.  
   - Для каждого варианта дать готовый шаблон + пошаговую инструкцию по запуску и проверке.

3. **Добавить раздел «Best practices по работе со skills»**  
   - Рекомендации по размеру, избежанию дублирования, версионированию.  
   - Советы по написанию навыков для максимальной эффективности LLM.

4. **Обновить оглавление и добавить якоря**  
   - Добавить ссылки на новые разделы в начало файла.  
   - Использовать якоря Markdown (#динамическая-загрузка-skills и т.д.).

## Требования к оформлению

- Формат: Markdown (.md).
- Использовать заголовки уровней ##, ###, ####.
- Кодовые блоки с указанием языка: ```markdown
- Все примеры должны быть рабочими «из коробки» (с минимальными правками путей/API).
- Добавить в конец новых разделов ссылку на папку `examples/skill-testing/` (создать её, если нет).
- Стиль: технически точный, лаконичный, с нумерованными/маркированными списками.

## Ожидаемый результат (полный текст новых/обновлённых разделов)

### Оглавление (добавить/обновить в начале файла)

```markdown
# Skills System

- [Каталог навыков](#каталог-навыков)
- [Матрица использования](#матрица-использования)
- [Динамическая загрузка skills](#динамическая-загрузка-skills)
- [Изолированное тестирование skills](#изолированное-тестирование-skills)
- [Best practices](#best-practices-по-работе-со-skills)
```

### Динамическая загрузка skills

```markdown
## Динамическая загрузка skills

Orchestrator собирает промпт агента в следующем порядке:

1. Читает базовую роль из `.agent/roles/<role>.md`.
2. Извлекает список `ACTIVE SKILLS` из раздела роли.
3. Для каждого skill последовательно загружает содержимое файла `.agent/skills/<skill-name>.md`.
4. Вставляет навыки после базовой роли в раздел `LOADED SKILLS`.
```
### Пример

В роли `08_agent_developer.md`:

```markdown
ACTIVE SKILLS:
- skill-core-principles
- skill-tdd-stub-first
- skill-artifact-management
- skill-testing-best-practices
```

Финальный промпт (упрощённо):

```markdown
You are the Developer Agent...
[Полный текст базовой роли]

### LOADED SKILLS
[Содержимое skill-core-principles.md]
[Содержимое skill-tdd-stub-first.md]
[Содержимое skill-artifact-management.md]
[Содержимое skill-testing-best-practices.md]

Current task: ...
```


### Изолированное тестирование skills

```markdown
## Изолированное тестирование skills

Изолированное тестирование позволяет проверять skill без полного workflow. Это ускоряет разработку, отладку и предотвращает регрессии.

#### Вариант 1: Python-скрипт (рекомендуемый)

Сохраните как `examples/skill-testing/test_skill.py` или `utils/test_skill.py`.

```python
import os
from pathlib import Path
import openai  # замените на клиент вашей модели (xai, groq и т.д.)

REPO_ROOT = Path(__file__).parent.parent
ROLES_DIR = REPO_ROOT / ".agent" / "roles"
SKILLS_DIR = REPO_ROOT / ".agent" / "skills"

def load_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def build_isolated_prompt(role_file: str, skill_names: list[str], task: str) -> str:
    role_content = load_file(ROLES_DIR / role_file)
    
    skills_content = ""
    for skill in skill_names:
        skill_path = SKILLS_DIR / f"{skill}.md"
        skills_content += f"\n### SKILL: {skill}\n{load_file(skill_path)}\n"
    
    prompt = f"""
{role_content}

### ACTIVE SKILLS (для теста)
{'\n'.join(f"- {s}" for s in skill_names)}

{skills_content}

### TEST TASK
{task}

Отвечай строго в соответствии с ролью и загруженными skills.
"""
    return prompt

def query_model(prompt: str, model: str = "grok-4"):
    client = openai.OpenAI(base_url="https://api.x.ai/v1", api_key=os.getenv("XAI_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=3000
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    role = "08_agent_developer.md"
    skills = ["skill-tdd-stub-first"]
    task = """
    Реализуй функцию calculate_tax(income: float) -> float:
    - 20% если income > 50000
    - 10% иначе
    Обязательно используй Stub-First подход.
    """
    
    prompt = build_isolated_prompt(role, skills, task)
    print("=== ПРОМПТ ===\n", prompt, "\n")
    print("=== ОТВЕТ МОДЕЛИ ===\n", query_model(prompt))
```

**Инструкция по запуску:**
1. Установите клиент: `pip install openai`.
2. Задайте переменную окружения с API-ключом.
3. Запустите: `python test_skill.py`.
4. Проверьте, что ответ строго следует skill (например, сначала stubs + тесты).

#### Вариант 2: n8n workflow (no-code/low-code)

Используйте **Code node** на JavaScript.

**Шаблон workflow (импортировать как JSON):**

```json
{
  "nodes": [
    {
      "parameters": {
        "jsCode": "const roleContent = $input.first().json.roleContent;\nconst skills = $input.first().json.skills;\nconst task = $input.first().json.task;\n\nlet prompt = roleContent + '\\n\\n### ACTIVE SKILLS\\n' + skills.map(s => '- ' + s).join('\\n') + '\\n\\n';\n\nfor (const skill of skills) {\n  const skillContent = $input.first().json.skillsContent[skill];\n  prompt += `### SKILL: ${skill}\\n${skillContent}\\n\\n`;\n}\n\nprompt += '### TEST TASK\\n' + task + '\\n\\nОтвечай строго в соответствии с ролью и загруженными skills.';\n\nreturn { prompt };"
      },
      "name": "Build Prompt",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [400, 300]
    },
    {
      "parameters": {
        "model": "grok-4",
        "prompt": "={{ $json.prompt }}",
        "options": {}
      },
      "name": "AI Agent",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [600, 300]
    }
  ],
  "connections": {
    "Build Prompt": {
      "main": [[{ "node": "AI Agent", "type": "main", "index": 0 }]]
    }
  }
}
```

**Инструкция:**
1. Добавьте Set node перед Code node с полями: `roleContent`, `skills` (массив), `skillsContent` (объект), `task`.
2. Настройте AI node на ваш провайдер.
3. Запустите и проверьте ответ.


### Best practices по работе со skills

```markdown
## Best practices по работе со skills

- Размер skill-файла: < 1500 токенов (избегайте prompt bloat).
- Избегайте дублирования: общие принципы выносите в core-skills.
- Пишите императивно и конкретно: «ТЫ ДОЛЖЕН...» вместо «Рекомендуется...».
- Тестируйте изолированно перед добавлением в ACTIVE SKILLS.
- Версионирование: при breaking changes создавайте skill-v2 и обновляйте роли.
```

## Приёмка

- PR с изменениями в `docs/SKILLS.md` и новыми файлами в `examples/skill-testing/`.
- Проверка: оба варианта тестирования работают с текущими skills.
- Ревью: минимум 1 approve от maintainer.
