# Доработка workflow по части верификации

Роль: Ты — Senior AI Architect, специализирующийся на проектировании надежных агентных систем (Agentic Workflow Design). Твоя задача — улучшить качество процессов разработки, внедрив обязательные этапы верификации (Review) и циклы обратной связи.

Контекст: В проекте используются Markdown-файлы для описания рабочих процессов (Workflows). Мы обнаружили архитектурную ошибку: агенты-исполнители генерируют артефакты, но агенты-валидаторы (Reviewers) не задействованы, что нарушает принцип Quality Assurance.

Задача: Проанализируй и обнови указанные ниже файлы workflow. Тебе необходимо найти вызовы "агентов-исполнителей" и добавить сразу после них вызов соответствующих "агентов-верификаторов".

Правила связывания (Doer -> Reviewer):

Если работает Analyst (System/Agents/02_analyst_prompt.md), его результат ОБЯЗАН проверить TZ Reviewer (System/Agents/03_tz_reviewer_prompt.md).

Если работает Architect (System/Agents/04_architect_prompt.md), его результат ОБЯЗАН проверить Architecture Reviewer (System/Agents/05_architecture_reviewer_prompt.md).

Если работает Planner (System/Agents/06_agent_planner.md), его результат ОБЯЗАН проверить Plan Reviewer (System/Agents/07_agent_plan_reviewer.md).

Логика выполнения (Loop Logic): Для каждой пары внедрить следующую логику (адаптируй под существующий стиль/синтаксис файла):

Generate: Исполнитель создает артефакт.

Review: Верификатор проверяет артефакт на соответствие требованиям и стандартам.

Iterate:

Если верификатор находит ошибки -> Исполнитель переделывает работу с учетом замечаний -> Снова к шагу Review.

Если верификатор одобряет ("LGTM") -> Переход к следующему шагу workflow.

Целевые файлы для исправления:

01-start-feature.md (Проверить Analyst и Architect)

02-plan-implementation.md (Проверить Planner)

vdd-01-start-feature.md (Проверить Analyst и Architect)

vdd-02-plan.md (Проверить Planner)


