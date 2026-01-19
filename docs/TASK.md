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

Реализовать **VDD Multi-Adversarial** (v3.4.0) и **Workflow Integrity Fixes** (v3.4.1).

## 2. Что создано

### 2.1 Новые Adversarial Skills (v3.4.0)

| Skill | Описание |
|-------|----------|
| `skill-adversarial-security` | OWASP-критик в саркастичном стиле: injections, auth, secrets |
| `skill-adversarial-performance` | Критик производительности: N+1, memory, async, complexity |

### 2.2 Новый Workflow (v3.4.0)

| Workflow | Описание |
|----------|----------|
| `vdd-multi.md` | Последовательный запуск 3 критиков: logic → security → performance |

### 2.3 Workflow Integrity Fixes (v3.4.1)

| Компонент | Исправление |
|-----------|-------------|
| `base-stub-first.md` | Исправлены ссылки на несуществующие сценарии (`/analyst-task` → `/01-start-feature`) |
| `vdd-enhanced.md` | Починен через фикс base-stub-first (восстановлен вызов Аналитика) |
| `vdd-adversarial.md` | Исправлен вызов (`/developer-fix` → `/03-develop-single-task`) |
| `docs/KNOWN_ISSUES.md` | Создан (требовался для работы сценариев) |

## 3. Файлы

### Созданные файлы
| Файл | Описание |
|------|----------|
| `.agent/skills/skill-adversarial-security/SKILL.md` | Критик безопасности |
| `.agent/skills/skill-adversarial-performance/SKILL.md` | Критик производительности |
| `.agent/workflows/vdd-multi.md` | Workflow мульти-критиков |
| `docs/KNOWN_ISSUES.md` | Реестр известных проблем (v3.4.1) |

### Изменённые файлы
| Файл | Изменения |
|------|-----------|
| `System/Docs/SKILLS.md` | Добавлены 2 новых скилла в VDD секцию |
| `Backlog/potential_improvements-2.md` | Обновлены статусы v3.4 → Done |
| `CHANGELOG.md` | Добавлены v3.4.0 и v3.4.1 releases |
| `.agent/workflows/base-stub-first.md` | Fix phantom references |
| `.agent/workflows/vdd-adversarial.md` | Fix loop calls |
| `.agent/workflows/security-audit.md` | Fix .AGENTS.md instructions |

## 4. Acceptance Criteria

- [x] `skill-adversarial-security` создан с OWASP checklist
- [x] `skill-adversarial-performance` создан с perf checklist  
- [x] `vdd-multi` workflow создан с 3 фазами
- [x] Документация обновлена (SKILLS, CHANGELOG)
- [x] **v3.4.1 Integrity**: Все 14 сценариев проверены и ссылаются на существующие файлы
- [x] **v3.4.1 Integrity**: `docs/KNOWN_ISSUES.md` существует
