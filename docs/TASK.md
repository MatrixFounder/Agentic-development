# Task: v3.4 VDD Multi-Adversarial

## 0. Meta Information

| Field    | Value                                |
|----------|--------------------------------------|
| Task ID  | 034                                  |
| Slug     | vdd-multi-adversarial                |
| Status   | Completed                            |
| Priority | High                                 |

---

## 1. Цель

Реализовать **VDD Multi-Adversarial** — расширение VDD последовательным запуском нескольких специализированных критиков.

## 2. Что создано

### 2.1 Новые Adversarial Skills

| Skill | Описание |
|-------|----------|
| `skill-adversarial-security` | OWASP-критик в саркастичном стиле: injections, auth, secrets |
| `skill-adversarial-performance` | Критик производительности: N+1, memory, async, complexity |

### 2.2 Новый Workflow

| Workflow | Описание |
|----------|----------|
| `vdd-multi.md` | Последовательный запуск 3 критиков: logic → security → performance |

## 3. Файлы

### Созданные файлы
| Файл | Описание |
|------|----------|
| `.agent/skills/skill-adversarial-security/SKILL.md` | Критик безопасности |
| `.agent/skills/skill-adversarial-performance/SKILL.md` | Критик производительности |
| `.agent/workflows/vdd-multi.md` | Workflow мульти-критиков |

### Изменённые файлы
| Файл | Изменения |
|------|-----------|
| `docs/SKILLS.md` | Добавлены 2 новых скилла в VDD секцию |
| `Backlog/potential_improvements-2.md` | Обновлены статусы v3.4 → Done |
| `CHANGELOG.md` | Добавлен v3.4.0 release |

## 4. Acceptance Criteria

- [x] `skill-adversarial-security` создан с OWASP checklist
- [x] `skill-adversarial-performance` создан с perf checklist  
- [x] `vdd-multi` workflow создан с 3 фазами
- [x] Документация обновлена
- [x] CHANGELOG обновлён
