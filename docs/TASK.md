# Task: v3.5 Memory Automation

## 0. Meta Information

| Field    | Value                   |
|----------|-------------------------|
| Task ID  | 035                     |
| Slug     | memory-automation       |
| Status   | Completed               |
| Priority | Medium                  |

---

## 1. Цель

Реализовать **v3.5 — Автоматизация памяти**: создать скиллы для автоматического обновления `.AGENTS.md` и восстановления архитектурной документации из кода.

## 2. Проблема

1. **Амнезия агентов**: Разработчики забывают обновлять `.AGENTS.md` после изменения кода. Следующие сессии не имеют актуального контекста.
2. **Рассинхронизация документации**: После "быстрых правок" или серии багфиксов, `ARCHITECTURE.md` и `KNOWN_ISSUES.md` не отражают реальное состояние кода.

## 3. Решение

### 3.1 `skill-update-memory`

Навык анализа изменений в коде и предложения обновлений для `.AGENTS.md`.

**Вход:** `git diff --staged` или список изменённых файлов.

**Логика:**
1. **Фильтрация:** Игнорировать `*.lock`, `*.min.js`, `dist/`, `migrations/`, конфиги, документацию.
2. Для каждого изменённого исходного файла определить целевой `.AGENTS.md`.
3. Если файл новый — добавить запись.
4. Если файл удалён — пометить `(Deleted)`.
5. Если изменилась логика — обновить описание.

**Интеграция:** Шаг в `09_agent_code_reviewer` или `04-update-docs`.

### 3.2 `skill-reverse-engineering`

Навык восстановления ментальной модели проекта из кода.

**Функции:**
- Генерация/обновление `docs/ARCHITECTURE.md` по текущему коду.
- Выявление "скрытых знаний" для записи в `docs/KNOWN_ISSUES.md`.

**Стратегия (Mitigation: Context Overflow):**
- Итеративный анализ: папка-за-папкой → локальные summaries → глобальная Architecture.

## 4. Файлы

### Создаваемые файлы
| Файл | Описание |
|------|----------|
| `.agent/skills/skill-update-memory/SKILL.md` | Навык обновления .AGENTS.md |
| `.agent/skills/skill-reverse-engineering/SKILL.md` | Навык reverse engineering |

### Изменяемые файлы
| Файл | Изменения |
|------|-----------|
| `System/Docs/SKILLS.md` | Добавление 2 новых скиллов |
| `Backlog/potential_improvements-2.md` | Обновление статуса v3.5 → Done |
| `CHANGELOG.md` | Добавление v3.5.0 release |
| `README.md` / `README.ru.md` | Обновление версии |

## 5. Acceptance Criteria

- [x] `skill-update-memory/SKILL.md` создан с filtering logic и integration steps
- [x] `skill-reverse-engineering/SKILL.md` создан с iterative strategy
- [x] Документация `System/Docs/SKILLS.md` обновлена
- [x] VDD adversarial проверка пройдена
- [x] `CHANGELOG.md` обновлён

## 6. VDD Risk Assessment (Pre-Verified)

| Risk | Critique | Mitigation |
|------|----------|------------|
| Context Overflow | "50k lines в контекст для Architecture? Удачи." | Iterative Strategy: folder-by-folder summaries |
| Hallucination & Noise | "1000 строк в package-lock.json = 'Dependencies Logic'?" | Strict Filtering: `*.lock`, `dist/`, `migrations/` |
| Overwriting Human Wisdom | "Агент удалит мой костыльный комментарий?" | Append/Refine Mode: `[Human Knowledge]` sections protected |
