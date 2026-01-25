# Доработка инструкции по работе с данным фреймворком

## Проверка инструкции / readme, readme.ru

1. Контекст:

```eng
### Stage 2: Analysis and Design
1. **Analyst (02_analyst_prompt.md):**
   - Provide the agent with the idea/task.
   - The agent studies the project structure (Reconnaissance).
   - Result: **Technical Specification (TZ)**.
2. **TZ Review (03_tz_reviewer_prompt.md):**
   - Check the TZ for completeness and consistency.
3. **Architect (04_architect_prompt.md):**
   - Based on the TZ, the agent designs the architecture.
   - Result: **Architecture Document** (classes, databases, APIs).
4. **Architecture Review (05_architecture_reviewer_prompt.md):**
   - Approve the architecture before planning.
```

```ru
### Этап 2: Анализ и Проектирование
1. **Аналитик (02_analyst_prompt.md):**
   - Подайте агенту идею/задачу.
   - Агент изучит структуру проекта (Reconnaissance).
   - Результат: **Техническое Задание (ТЗ)**.
2. **Ревью ТЗ (03_tz_reviewer_prompt.md):**
   - Проверьте ТЗ на полноту и непротиворечивость.
3. **Архитектор (04_architect_prompt.md):**
   - На основе ТЗ агент проектирует архитектуру.
   - Результат: **Архитектурный документ** (классы, базы данных, API).
4. **Ревью Архитектуры (05_architecture_reviewer_prompt.md):**
   - Утвердите архитектуру перед планированием.


```


## Что нужно сделать
1. Проверить, что указаны все deliverables (например, сейчас отсутствует описание, что будет создан файл ARCHITECTURE.md) и дополнить.
2. Описать, что делать с текущими файлами, которые создают агенты в конце всех изменений
3. Описать, какие файлы можно/нужно удалять, а какие нельзя после всех работ

