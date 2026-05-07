# Claude Plan Mode vs VDD Workflows — конспект для презентации

> Источник: рабочий диалог 2026-04-21. Материал структурирован как каркас слайдов: один раздел ≈ один слайд.

---

## 1. TL;DR

**Claude Plan Mode и `/vdd-*` — две разные системы планирования. Запустить одновременно технически можно, но получите degenerate mode (артефакты схлопнутся в один plan-file). Для production выбирайте одну.**

- **Plan Mode** — лёгкий встроенный режим Claude Code: «обсудить до кода».
- **`/vdd-start-feature`** — тяжёлый доменный workflow: сам заменяет плановую фазу и пишет полноценные артефакты в `docs/`.

Для серьёзной фичи: сначала `ExitPlanMode`, потом `/vdd-start-feature` (или сразу `/vdd`). Plan Mode — для предварительного обсуждения; запуск workflow **внутри** Plan Mode даёт degenerate mode, см. §3.

---

## 2. Две системы планирования — сравнение

| Характеристика | Claude Plan Mode | `/vdd-start-feature` |
|---|---|---|
| **Класс** | Встроенный режим IDE | Доменный workflow (`.agent/workflows/`) |
| **Активация** | `Shift+Tab` (toggle) | Slash-команда |
| **Что делает** | Read-only + правка одного plan-file | Analyst → Task Reviewer → Architect → Arch Reviewer |
| **Разрешённые правки** | Только `~/.claude/plans/*.md` | `docs/TASK.md`, `docs/ARCHITECTURE.md`, и любые нужные артефакты |
| **Выход** | `ExitPlanMode` (требует одобрения плана) | Завершается по шагам workflow |
| **Цель** | Согласовать намерение перед действием | Произвести структурированные требования + архитектуру |

---

## 3. Почему они конфликтуют

**Механика (уточнение)**: Plan Mode разрешает запись только в plan-file (`~/.claude/plans/*.md`). Когда внутри Plan Mode запускается [vdd-01-start-feature.md](../.agent/workflows/vdd-01-start-feature.md), агент **не падает** — он перенаправляет все записи (TASK, ARCHITECTURE, PLAN) в plan-file. Получается «VDD-как-один-документ»: вместо иерархии `docs/TASK.md` + `docs/ARCHITECTURE.md` + `docs/PLAN.md` — один длинный markdown.

**Что теряется при таком запуске**:
- git-видимость отдельных артефактов (один файл вне репо вместо commit'ов в `docs/`)
- RTM привязанная к правильным файлам — в plan-file всё в одной куче
- отдельные ревью-границы между фазами (Task Reviewer / Arch Reviewer / Plan Reviewer теряют свои артефакты)
- долговечность: plan-file эфемерный, в `~/.claude/plans/` вне репо

**Вывод**: технически совместимо, но это **degenerate mode**. Для черновика и обсуждения направления — допустимо. Для долгоживущей фичи или фичи под PR — нет: вы получите VDD без структуры, ради которой VDD и существует.

---

## 4. Три варианта запуска

### Вариант A — прямой запуск (рекомендованный по умолчанию)

```
/vdd-start-feature <описание фичи>
```

Workflow сам выступает в роли «плановой фазы»: Analyst создаёт `docs/TASK.md`, Reviewer валидирует, Architect правит `docs/ARCHITECTURE.md`.

### Вариант B — обсуждение в Plan Mode, потом workflow

```
1. Shift+Tab       # Plan Mode ON
2. Обсуждаем намерение, формируем формулировку (без записи в docs/)
3. ExitPlanMode    # одобряете направление
4. /vdd-start-feature <финальное описание>
```

### Вариант C — полный цикл через супер-сет

```
/vdd <описание фичи>
```

По [vdd-enhanced.md](../.agent/workflows/vdd-enhanced.md) это Analysis + Spec-Validator + Planning + Development + Adversarial Review в одном вызове. Берёт, когда фича нетривиальна и нужен полный жизненный цикл.

---

## 5. Anti-patterns

**Не делать:**

- ⚠️ Вызов `/vdd-start-feature` внутри активного Plan Mode → **работает**, но артефакты схлопываются в plan-file. Не баг и не failure — degenerate mode. Используйте сознательно: черновик — ОК; production-фича — теряете структуру, ради которой VDD нужен.
- ❌ Попытка «запустить workflow из plan-file» → plan-file и VDD-артефакты живут в разных системах, plan-file не исполняется.
- ❌ Переключение в Plan Mode посреди исполнения `/vdd-*` → сломает петлю верификации внутри workflow.
- ❌ Копирование `~/.claude/plans/*.md` в `docs/TASK.md` вручную → обходит верификацию Analyst/Reviewer, теряется RTM.

---

## 6. Роль `/brainstorming`

[`.agent/skills/brainstorming/SKILL.md`](../.agent/skills/brainstorming/SKILL.md) — скилл для перехода «сырая идея → чёткий дизайн». Адаптируется к сложности:

| Уровень | Что делает | Совместимо с Plan Mode |
|---|---|---|
| **TRIVIAL** | Подтверждение в чате, без файлов | ✅ Полностью |
| **MEDIUM** | 1–2 уточняющих вопроса, краткое подтверждение | ✅ Если без Design Doc |
| **COMPLEX** | Пишет `docs/design/feature-name.md` | ⚠️ Перенаправит Design Doc в plan-file (или в чат, см. fallback ниже) |

**Обход для Complex в Plan Mode**: по той же SKILL.md (`No File Access? Output the full Markdown in chat`) скилл отдаёт Design Doc текстом, не записывая файл. Альтернатива — положить содержимое в plan-file (он писать разрешён).

---

## 7. Рекомендуемый pipeline для сложной фичи

```
Shift+Tab            →   Plan Mode ON
/brainstorming <...> →   Design Doc (в чат или в plan-file)
ExitPlanMode         →   одобряете дизайн
/vdd-start-feature   →   Analyst принимает на вход согласованный дизайн
                     →   docs/TASK.md (Epics + Issues + RTM)
                     →   Task Reviewer (верификация)
                     →   docs/ARCHITECTURE.md
                     →   Architecture Reviewer (верификация)
```

**Зачем так, а не сразу `/vdd-start-feature`:**

- `/vdd-start-feature` в фазе Analyst требует структурированных Epics/Issues. Если идея сырая, он потратит циклы на уточнение.
- `/brainstorming` специализирован на «сырая мысль → технический дизайн» — это его прямая задача.
- После брейншторма Analyst получает чёткую формулировку и не задаёт банальных вопросов.

---

## 8. Когда брейншторм НЕ нужен

- **Чёткие требования** → сразу `/vdd-start-feature`.
- **Тривиальный багфикс или typo** → `/light` (по правилу из CLAUDE.md: «если задача тривиальна — предложи `/light`»).
- **Исследовательский вопрос по коду** («как работает X?») → вообще без workflow, обычный диалог.
- **Продуктовое открытие с нуля** (TAM/SAM/SOM, целевая аудитория) → `/product-full-discovery`, а не `/brainstorming`.

---

## 9. Decision Tree — как выбрать entry point

```
┌─────────────────────────────────┐
│ Пользователь задаёт задачу      │
└───────────────┬─────────────────┘
                │
        Это тривиально?
                │
        ┌───────┴───────┐
        Yes             No
        │               │
    /light         Требования чёткие?
                        │
                ┌───────┴───────┐
                Yes             No
                │               │
         /vdd-start-feature   Нужен полный цикл
         (или /vdd для       с development + review?
          полного цикла)         │
                          ┌──────┴──────┐
                          Yes           No
                          │             │
                         /vdd      Plan Mode + /brainstorming
                                   → ExitPlanMode
                                   → /vdd-start-feature
```

---

## 10. Ссылки на источники

Ключевые файлы в репозитории, на которых построен конспект:

- [.agent/workflows/vdd-01-start-feature.md](../.agent/workflows/vdd-01-start-feature.md) — шаги VDD-Start-Feature workflow
- [.agent/workflows/vdd-enhanced.md](../.agent/workflows/vdd-enhanced.md) — супер-сет `/vdd` (Analysis + Planning + Development + Adversarial Review)
- [.agent/skills/brainstorming/SKILL.md](../.agent/skills/brainstorming/SKILL.md) — 3-уровневая модель Trivial/Medium/Complex
- [CLAUDE.md](../CLAUDE.md) — Orchestrator pipeline и правила переключения между workflow
