# Enterprise Agentic Development Framework

> **Status:** CRITICAL REVIEW v2 — 2026-01-21
> **Reviewer:** Adversarial Architect (VDD-style)
> **Previous Version:** Comprehensive but over-engineered, critical gaps identified

---

## Executive Summary

Данный документ описывает инициативы по расширению фреймворка Agentic-Development для enterprise-уровня. **После глубокого VDD-review выявлены критические проблемы**, которые могут привести к:

1. **Context Overflow** — перегрузка LLM-контекста при попытке загрузить всю иерархию
2. **Hallucination Multiplication** — больше агентов = больше точек галлюцинаций
3. **Over-Engineering** — SAFe-подобная иерархия противоречит принципам LLM-агентов
4. **Session Isolation Gap** — игнорирование критического ограничения: каждый агент = 1 сессия

---

## Table of Contents

- [Critical Review (VDD Adversarial)](#critical-review-vdd-adversarial)
- [Revised Vision](#revised-vision)
- [Implementation Plan](#implementation-plan)
- [Appendix: Original Initiatives (Archived)](#appendix-original-initiatives-archived)

---

## Critical Review (VDD Adversarial)

### 🔴 CRITICAL: Session Isolation Not Addressed

> [!CAUTION]
> **Fundamental Flaw:** Документ описывает "параллельные пайплайны" и "иерархию агентов", но **полностью игнорирует факт, что каждый LLM-агент = 1 сессия IDE**.

**Реальность:**
- В Cursor/Antigravity нет "оркестратора", который spawn'ит sub-агентов
- Каждый агент выполняется последовательно в одном контексте
- "Параллелизм" возможен только через **файлы-артефакты как интерфейс**

**Вердикт:** Вся концепция "dispatch_parallel_tasks" и "Module Coordinator" требует фундаментального переосмысления.

---

### 🔴 CRITICAL: Context Overflow Risk

> [!WARNING]
> **Оценка:** Product Owner + Orchestrator + Module Coordinator + Analyst = 4+ системных промпта = **50K+ токенов только на контекст агентов**.

**Расчёт:**
| Компонент | Токены (приблизительно) |
|-----------|-------------------------|
| GEMINI.md/AGENTS.md | 3-5K |
| 00_product_owner.md | 3-5K (прогноз) |
| 01_orchestrator.md | 2-3K |
| 01_module_coordinator.md | 3-4K (прогноз) |
| Skills (5-10 штук) | 5-10K |
| PRODUCT_BACKLOG.md | 5-20K (зависит от проекта) |
| ARCHITECTURE.md (domain-specific × N) | 10-50K |
| **ИТОГО** | **30-100K+ токенов** |

**Проблема:** При лимите контекста 128K-200K, остаётся мало места для:
- Исходного кода
- Истории чата
- Thinking LLM

**Вердикт:** Нужна **агрессивная декомпозиция** и **lazy loading** артефактов.

---

### 🟡 WARNING: Hallucination Multiplication

> [!IMPORTANT]
> **Закон:** Каждый дополнительный агент — это точка потенциальной галлюцинации.

**Анализ:**
- Product Owner "галлюцинирует" ROI → Orchestrator принимает за факт
- Module Coordinator "галлюцинирует" зависимости → Deadlock в реальности
- Бизнес-контекст труднее верифицировать чем код (нет компилятора для ROI)

**Вердикт:** Нужен **VDD на каждом уровне** с конкретными критериями приёмки.

---

### 🟡 WARNING: Over-Engineering (SAFe Trap)

> [!WARNING]
> **Критика:** Предложенная иерархия "Top → Mid → Bottom" копирует SAFe (Scaled Agile), но SAFe — это фреймворк для **людей**, не для LLM.

**Различия LLM vs Human teams:**

| Аспект | Human Teams (SAFe) | LLM Agents |
|--------|-------------------|------------|
| Коммуникация | Rich, async, multi-channel | Text artifacts only |
| Context | Unlimited (brain) | 128K tokens |
| Parallelism | Native (multiple brains) | Sequential (1 session) |
| Memory | Persistent | Session-scoped |
| Verification | Meetings, reviews | Artifacts, tests |

**Вердикт:** Нужна **artifact-centric architecture**, а не role-centric.

---

### 🟢 POSITIVE: Domain Isolation

**Что хорошо:**
- Структура `docs/domains/{domain}/` — правильное направление
- Изоляция артефактов по доменам снижает конфликты
- ID-based задачи (`task-001-arbitrage-scanner/`) — хорошая практика

**Но:** Нужно упростить — убрать лишние уровни вложенности.

---

### 🟢 POSITIVE: Skills Extension

**Что хорошо:**
- Новые skills (`skill-backlog-prioritization`, `skill-epic-breakdown`) — верный подход
- Skills = документация для LLM, не код
- Модульность позволяет lazy loading

---

## Revised Vision

### Философия: Artifact-Centric Architecture

> [!IMPORTANT]
> **Ключевой инсайт:** Агенты не общаются напрямую. Они общаются через **артефакты**.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARTIFACT-CENTRIC MODEL                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User ──> [PRODUCT_VISION.md] ──> Product Analyst (Session 1)  │
│                    │                                            │
│                    ▼                                            │
│           [PRODUCT_BACKLOG.md] ──> Orchestrator (Session 2)     │
│                    │                                            │
│                    ▼                                            │
│           [domains/trading/TASK.md] ──> Developer (Session N)   │
│                    │                                            │
│                    ▼                                            │
│           [Code + .AGENTS.md] ──> Reviewer (Session N+1)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Принципы:**
1. **Sequential Sessions** — Один агент = Одна сессия = Один артефакт на выходе
2. **Artifacts as Contracts** — Каждый артефакт имеет схему и критерии валидации
3. **Lazy Context Loading** — Загружать только необходимый домен
4. **VDD at Every Stage** — Adversarial review каждого артефакта

---

### Revised Agent Model

**БЫЛО (Over-engineered):**
```
PO → Orchestrator → Module Coordinator → Analyst → Architect → ...
```

**СТАЛО (Pragmatic):**

| Phase | Agent (Session) | Input Artifact | Output Artifact |
|-------|-----------------|----------------|-----------------|
| 1. Vision | Product Analyst | User Request + VISION.md | PRODUCT_BACKLOG.md |
| 2. Review | Product Reviewer (VDD) | PRODUCT_BACKLOG.md | APPROVED_BACKLOG.md |
| 3. Domain | Orchestrator | APPROVED_BACKLOG.md | Domain TASK.md files |
| 4. Execute | Standard Pipeline | Domain TASK.md | Code + Tests |

**Ключевые изменения:**
- Убран "Module Coordinator" (его функции в artifacts)
- "Product Owner" переименован в "Product Analyst" (уточнение роли)
- Добавлен явный VDD-review на уровне продукта
- Reduced depth: 4 фазы вместо 7+ в цепочке

---

### Revised Folder Structure

```
project-root/
├── GEMINI.md                    # Orchestrator bootstrap
├── .agent/
│   ├── skills/
│   │   ├── skill-product-analysis/       # NEW: Vision → Backlog
│   │   ├── skill-backlog-prioritization/ # NEW: WSJF/MoSCoW
│   │   ├── skill-domain-decomposition/   # NEW: Split by domain
│   │   └── ... (existing skills)
│   └── workflows/
│       ├── product-vision.md             # NEW: Phase 1
│       ├── product-review.md             # NEW: Phase 2 (VDD)
│       └── domain-start.md               # NEW: Phase 3
├── System/
│   └── Agents/
│       ├── p01_product_analyst.md        # NEW (NOT p00 - no meta-prompt needed)
│       ├── p02_product_reviewer.md       # NEW (VDD-adversarial)
│       └── ... (existing agents)
├── docs/
│   ├── PRODUCT_VISION.md                 # NEW: High-level vision
│   ├── PRODUCT_BACKLOG.md                # NEW: Prioritized backlog
│   └── domains/
│       ├── {domain}/
│       │   ├── ARCHITECTURE.md           # Domain-specific
│       │   ├── KNOWN_ISSUES.md
│       │   └── current/                  # Active task (singular!)
│       │       ├── TASK.md
│       │       └── PLAN.md
│       └── archive/                      # Completed tasks
└── src/{domain}/                          # Code by domain
```

**Упрощения:**
- `current/` вместо `tasks/task-XXX/` — принудительный single-tasking
- Один активный TASK per domain — меньше конфликтов
- Archive на уровне docs, не per-domain

---

## Implementation Plan

### Phase 0: Foundation (No Code, Documentation Only)

> [!NOTE]
> Эта фаза НЕ требует разработки. Только документы и верификация.

| # | Deliverable | Description | DoD |
|---|-------------|-------------|-----|
| 0.1 | `skill-product-analysis/SKILL.md` | Skill для анализа vision и breakdown в backlog items | VDD-review passed |
| 0.2 | `skill-backlog-prioritization/SKILL.md` | WSJF/MoSCoW prioritization logic | VDD-review passed |
| 0.3 | `p01_product_analyst.md` | Agent prompt for vision analysis | Not over 3K tokens |
| 0.4 | `p02_product_reviewer.md` | Adversarial reviewer for product artifacts | Uses vdd-sarcastic |
| 0.5 | `workflow product-vision.md` | End-to-end workflow for phase 1 | Tested manually |

**Estimated Effort:** 1-2 sessions of framework development

---

### Phase 1: Domain Decomposition (Low Risk)

| # | Deliverable | Description | DoD |
|---|-------------|-------------|-----|
| 1.1 | `skill-domain-decomposition/SKILL.md` | Rules for splitting product into domains | VDD-review passed |
| 1.2 | Updated `01_orchestrator.md` | Read PRODUCT_BACKLOG.md, dispatch to domains | Backward-compatible |
| 1.3 | Folder structure migration guide | How to reorganize existing projects | Documented |

**Estimated Effort:** 1 session

---

### Phase 2: Integration Testing (Validation)

| # | Deliverable | Description | DoD |
|---|-------------|-------------|-----|
| 2.1 | Example project: "Trading Platform" | Test new workflows on non-trivial example | All phases pass |
| 2.2 | `skill-integration-testing/SKILL.md` | Cross-domain E2E testing guidance | Applied to example |
| 2.3 | Metrics collection | Token usage, hallucination rate | Baseline established |

**Estimated Effort:** 2-3 sessions

---

### Phase 3: Enterprise Extensions (Optional, After Validation)

> [!WARNING]
> Приступать только после успешной валидации Phase 0-2 на реальном проекте.

| # | Deliverable | Risk Level |
|---|-------------|------------|
| 3.1 | External API integration (market data) | HIGH — Requires real services |
| 3.2 | Compliance checking skill | MEDIUM — Needs legal review |
| 3.3 | Multi-agent parallelism research | HIGH — Requires IDE support |

---

## Revised Skills List

### New Skills (Phase 0-1)

| Skill | Purpose | Token Budget |
|-------|---------|--------------|
| `skill-product-analysis` | Vision → Structured Backlog | 1-2K |
| `skill-backlog-prioritization` | WSJF/MoSCoW/RICE ranking | 1K |
| `skill-domain-decomposition` | Split by bounded contexts | 1-2K |

### Existing Skills to Update

| Skill | Change |
|-------|--------|
| `skill-architecture-design` | Add domain-level architecture section |
| `skill-reverse-engineering` | Support domain-scoped analysis |

### Rejected Skills (Over-Engineering)

| Original Proposal | Reason for Rejection |
|-------------------|---------------------|
| `skill-parallel-dispatch` | No real parallelism in current IDE |
| `skill-stakeholder-elicitation` | Too vague, prone to hallucinations |
| `skill-roadmap-planning` | LLM not reliable for long-term planning |

---

## Revised Tools List

### New Tools: NONE in Phase 0-1

> [!IMPORTANT]
> **Философия:** "No new tools until proven necessary."
> Существующих tools (read_file, write_file, run_tests, git_*) достаточно для Phase 0-2.

### Deferred Tools (Phase 3)

| Tool | Reason |
|------|--------|
| `create_domain_structure` | Can be done with existing mkdir/touch |
| `fetch_market_data` | External API — high risk |
| `compliance_check` | Needs legal review first |

---

## Revised Agent List

### New Agents (Minimal Set)

| ID | Agent | Purpose | Max Tokens |
|----|-------|---------|------------|
| p01 | `p01_product_analyst.md` | Analyze vision, create backlog | 3K |
| p02 | `p02_product_reviewer.md` | VDD-review of product artifacts | 2K |

### Rejected Agents (Over-Engineering)

| Original | Reason |
|----------|--------|
| `p00_product_development.md` | Meta-prompt unnecessary — already have GEMINI.md |
| `01_module_coordinator.md` | Function covered by artifacts, not agent |
| `11_integration_tester.md` | Role for developer + skill, not separate agent |

---

## Open Questions (Revisited)

### Resolved

| Question | Resolution |
|----------|------------|
| "Как handling hallucinations в PO?" | VDD-review mandatory (p02_product_reviewer) |
| "Нужен ли queuing system?" | No — sequential sessions are feature, not bug |
| "Тестирование на реальных примерах?" | Phase 2 includes example project |

### Still Open

| Question | Owner | Deadline |
|----------|-------|----------|
| "Как передавать context между sessions эффективно?" | To be researched | Before Phase 1 |
| "Как валидировать бизнес-метрики (ROI)?" | Needs stakeholder input | Before Phase 3 |
| "IDE parallelism support (Cursor/Antigravity)?" | Depends on IDE roadmap | External blocker |

---

## Альтернатива: Отдельный Фреймворк

> [!TIP]
> Рассмотреть создание **Product Management Framework** как отдельного проекта, интегрируемого с Agentic-Development.

**Аргументы ЗА:**
- Separation of Concerns — разные lifecycle
- Разная аудитория — PO vs Developers
- Независимое версионирование

**Аргументы ПРОТИВ:**
- Дублирование skills infrastructure
- Сложность интеграции
- Maintenance burden

**Рекомендация:** Начать как extension к текущему фреймворку (Phase 0-2). Если complexity превысит threshold — extract в отдельный проект.

---

## Appendix: Original Initiatives (Archived)

<details>
<summary>Показать оригинальный документ (до ревью)</summary>

### 1. Описание Идеи / Глобального Изменения

Идея заключается в эволюции текущего фреймворка от фокуса на отдельных фичах к полноценной enterprise-разработке. Текущая структура (линейный пайплайн: Orchestrator → Analyst → Architect → Planner → Developer → Reviewers) хорошо работает для средних проектов, но для enterprise (например, торговая система с арбитражем, лояльностью, платежами и аналитикой) требуется:

- **Вертикальная иерархия агентов**: Слои для стратегического планирования (Product Owner), тактической координации (Orchestrator + Module Coordinators) и операционной реализации (существующие исполнители). Это вдохновлено Scaled Agile (SAFe), но адаптировано для LLM-агентов.
- **Параллельная разработка**: Изоляция задач по доменам и ID для одновременного выполнения нескольких пайплайнов без конфликтов (перезапись артефактов, кодовые коллизии).
- **Бизнес-ориентация**: Добавление Product Owner для приоритизации backlog, breakdown epics в stories, интеграции с ROI и stakeholder feedback.
- **Масштабируемость**: Расширение skills, tools и workflows для handling зависимостей, compliance и E2E-интеграций.
- **Совместимость**: Минимальные изменения в core (Stub-First, VDD), но с новыми артефактами (PRODUCT_BACKLOG.md, ROADMAP.md) и структурами папок.

### 2. Оригинальные Эпики

- **Эпик 1: Введение Роли Product Owner** (Приоритет: High)
- **Эпик 2: Реализация Вертикальной Иерархии Агентов** (Приоритет: High)
- **Эпик 3: Обновление Структуры Папок для Параллелизма** (Приоритет: High)
- **Эпик 4: Расширение Skills System** (Приоритет: Medium)
- **Эпик 5: Расширение Tools и Workflows** (Приоритет: Medium)
- **Эпик 6: Улучшение VDD и Security для Enterprise** (Приоритет: Low)
- **Эпик 7: Тестирование и Миграция** (Приоритет: Low)

### 3. Оригинальная Иерархия Агентов

- **Top-Level (Стратегический слой)**: Product Owner
- **Mid-Level (Тактический слой)**: Orchestrator + Module Coordinators
- **Bottom-Level (Операционный слой)**: Analyst, Architect, Planner, Developer, Reviewers

### 4. Дополнение - Альтернативная нумерация (p00-p05)

- p00_product_development - мета-промпт
- p01_product_orchestrator
- p02_product_owner
- p03_product_reviewer
- p04_product_architect
- p05_product_architecture_review

</details>

---

---

## Appendix B: Token Consumption Analysis (Current Framework)

> **Analysis Date:** 2026-01-21
> **Method:** Direct file measurement + emulated development cycle
> **Token Estimation:** 1 token ≈ 4 bytes (approximate for mixed EN/RU content)

### 1. Framework Component Sizes

#### 1.1 Agent Prompts (System/Agents/)

| File | Size (bytes) | Est. Tokens |
|------|--------------|-------------|
| `01_orchestrator.md` | 11,195 | ~2,799 |
| `00_agent_development.md` | 8,544 | ~2,136 |
| `06_agent_planner.md` | 4,173 | ~1,043 |
| `02_analyst_prompt.md` | 4,041 | ~1,010 |
| `08_agent_developer.md` | 4,039 | ~1,010 |
| `04_architect_prompt.md` | 3,856 | ~964 |
| `03_task_reviewer_prompt.md` | 3,225 | ~806 |
| `05_architecture_reviewer_prompt.md` | 3,061 | ~765 |
| `07_agent_plan_reviewer.md` | 2,027 | ~507 |
| `09_agent_code_reviewer.md` | 2,013 | ~503 |
| `10_security_auditor.md` | 500 | ~125 |
| **TOTAL Agents** | **46,674** | **~11,669** |

#### 1.2 Skills (.agent/skills/)

| Skill | Size (bytes) | Est. Tokens | Load Frequency |
|-------|--------------|-------------|----------------|
| `architecture-format` | 10,138 | ~2,535 | Low |
| `skill-reverse-engineering` | 5,287 | ~1,322 | Low |
| `skill-update-memory` | 4,402 | ~1,101 | Medium |
| `skill-adversarial-performance` | 3,784 | ~946 | VDD only |
| `skill-safe-commands` | 3,708 | ~927 | **Every session** |
| `skill-archive-task` | 3,666 | ~917 | New tasks |
| `requirements-analysis` | 3,614 | ~904 | Analysis phase |
| `skill-adversarial-security` | 3,350 | ~838 | VDD only |
| `skill-planning-format` | 3,025 | ~756 | Planning phase |
| `artifact-management` | 2,542 | ~636 | **Every session** |
| `skill-task-model` | 2,361 | ~590 | Analysis phase |
| `architecture-design` | 2,204 | ~551 | Architecture phase |
| `core-principles` | 2,077 | ~519 | **Every session** |
| `planning-decision-tree` | 1,690 | ~423 | Planning phase |
| `documentation-standards` | 1,699 | ~425 | Development phase |
| `code-review-checklist` | 1,543 | ~386 | Review phase |
| `architecture-review-checklist` | 1,383 | ~346 | Architecture phase |
| `developer-guidelines` | 1,371 | ~343 | Development phase |
| `task-review-checklist` | 1,333 | ~333 | Analysis phase |
| `testing-best-practices` | 1,139 | ~285 | Development phase |
| `plan-review-checklist` | 1,021 | ~255 | Planning phase |
| `tdd-stub-first` | 982 | ~246 | Development phase |
| `vdd-adversarial` | 743 | ~186 | VDD only |
| `vdd-sarcastic` | 578 | ~145 | VDD only |
| `security-audit` | 539 | ~135 | Security phase |
| **TOTAL Skills** | **64,179** | **~16,045** |

#### 1.3 Configuration Files

| File | Size (bytes) | Est. Tokens | Load Frequency |
|------|--------------|-------------|----------------|
| `GEMINI.md` | 5,576 | ~1,394 | **Session start** |
| `AGENTS.md` | 3,467 | ~867 | **Session start** |
| **TOTAL Config** | **9,043** | **~2,261** |

#### 1.4 Workflows (.agent/workflows/)

| Category | Total Size | Est. Tokens |
|----------|------------|-------------|
| Standard (01-05) | 3,622 | ~906 |
| VDD variants | 5,914 | ~1,479 |
| Other | 3,041 | ~760 |
| **TOTAL Workflows** | **12,577** | **~3,144** |

---

### 2. Emulated Development Cycle: Token Consumption

> [!NOTE]
> **Scenario:** Разработка средней сложности feature (например, "добавить новый API endpoint")
> **Context Limit:** 128K tokens (Gemini Pro 1.5) / 200K tokens (Claude 3.5)

#### 2.1 Phase-by-Phase Breakdown

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EMULATED DEVELOPMENT CYCLE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SESSION START                                                              │
│  ├── GEMINI.md/AGENTS.md loaded ........................ ~1,400 tokens    │
│  ├── IDE system prompt (Antigravity internal) ............ ~5,000 tokens*  │
│  └── User request + conversation history ................. ~500 tokens     │
│                                                    SUBTOTAL: ~6,900 tokens  │
│                                                                             │
│  PHASE 1: ANALYSIS                                                          │
│  ├── 02_analyst_prompt.md ................................ ~1,010 tokens   │
│  ├── skill-requirements-analysis ......................... ~904 tokens     │
│  ├── skill-archive-task .................................. ~917 tokens     │
│  ├── skill-task-review-checklist ......................... ~333 tokens     │
│  ├── skill-core-principles ............................... ~519 tokens     │
│  ├── docs/KNOWN_ISSUES.md (assumed) ...................... ~500 tokens     │
│  ├── docs/ARCHITECTURE.md (read) ......................... ~1,200 tokens   │
│  └── Generated TASK.md output ............................ ~1,000 tokens   │
│                                                    SUBTOTAL: ~6,383 tokens  │
│                                                                             │
│  PHASE 2: TASK REVIEW (Self-Correction)                                     │
│  ├── 03_task_reviewer_prompt.md .......................... ~806 tokens     │
│  └── Review iteration .................................... ~500 tokens     │
│                                                    SUBTOTAL: ~1,306 tokens  │
│                                                                             │
│  PHASE 3: ARCHITECTURE                                                      │
│  ├── 04_architect_prompt.md .............................. ~964 tokens     │
│  ├── skill-architecture-design ........................... ~551 tokens     │
│  ├── skill-architecture-format (if used) ................. ~2,535 tokens   │
│  └── Architecture update ................................. ~800 tokens     │
│                                                    SUBTOTAL: ~4,850 tokens  │
│                                                                             │
│  PHASE 4: ARCHITECTURE REVIEW                                               │
│  ├── 05_architecture_reviewer_prompt.md .................. ~765 tokens     │
│  └── skill-architecture-review-checklist ................. ~346 tokens     │
│                                                    SUBTOTAL: ~1,111 tokens  │
│                                                                             │
│  PHASE 5: PLANNING                                                          │
│  ├── 06_agent_planner.md ................................. ~1,043 tokens   │
│  ├── skill-planning-decision-tree ........................ ~423 tokens     │
│  ├── skill-planning-format ............................... ~756 tokens     │
│  ├── skill-tdd-stub-first ................................ ~246 tokens     │
│  └── Generated PLAN.md ................................... ~1,500 tokens   │
│                                                    SUBTOTAL: ~3,968 tokens  │
│                                                                             │
│  PHASE 6: PLAN REVIEW                                                       │
│  ├── 07_agent_plan_reviewer.md ........................... ~507 tokens     │
│  └── skill-plan-review-checklist ......................... ~255 tokens     │
│                                                    SUBTOTAL: ~762 tokens    │
│                                                                             │
│  PHASE 7: DEVELOPMENT (per task, assume 3 tasks)                            │
│  ├── 08_agent_developer.md ............................... ~1,010 tokens   │
│  ├── skill-developer-guidelines .......................... ~343 tokens     │
│  ├── skill-documentation-standards ....................... ~425 tokens     │
│  ├── Source code read (per task) ......................... ~3,000 tokens   │
│  └── Code generation (per task) .......................... ~2,000 tokens   │
│                                                SUBTOTAL (×3): ~20,334 tokens│
│                                                                             │
│  PHASE 8: CODE REVIEW (per task)                                            │
│  ├── 09_agent_code_reviewer.md ........................... ~503 tokens     │
│  ├── skill-code-review-checklist ......................... ~386 tokens     │
│  └── Review comments ..................................... ~500 tokens     │
│                                                SUBTOTAL (×3): ~4,167 tokens │
│                                                                             │
│  PHASE 9: SECURITY (optional)                                               │
│  ├── 10_security_auditor.md .............................. ~125 tokens     │
│  └── skill-security-audit ................................ ~135 tokens     │
│                                                    SUBTOTAL: ~260 tokens    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  GRAND TOTAL (Standard Pipeline): ~50,041 tokens                            │
│  + VDD Multi-Adversarial (if used): +5,000 tokens                           │
│  + Conversation history growth: +10,000-30,000 tokens                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ESTIMATED PEAK USAGE: 65,000-85,000 tokens                                 │
│  REMAINING CONTEXT (128K): 43,000-63,000 tokens for CODE                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

*IDE system prompt estimated based on typical agentic mode overhead

#### 2.2 Critical Observations

> [!WARNING]
> **Observation 1: Mandatory Skills Overhead**
> 
> Skills, загружаемые КАЖДУЮ сессию независимо от фазы:
> - `skill-core-principles` (~519 tokens)
> - `skill-artifact-management` (~636 tokens)
> - `skill-safe-commands` (~927 tokens)
> 
> **Total mandatory overhead: ~2,082 tokens per session**

> [!WARNING]
> **Observation 2: Orchestrator Dominance**
> 
> `01_orchestrator.md` (~2,799 tokens) — самый большой агентский промпт.
> Содержит 14 сценариев с дублированием структур. 
> **Возможное сокращение: 40-50% при рефакторинге.**

> [!CAUTION]
> **Observation 3: architecture-format Anomaly**
> 
> `skill-architecture-format` (~2,535 tokens) — непропорционально большой skill.
> Если загружается при каждом architecture phase → **+2.5K tokens overhead**.

---

### 3. Optimization Recommendations

#### 3.1 IMMEDIATE (No Code Changes)

| # | Recommendation | Savings | Effort |
|---|----------------|---------|--------|
| O1 | **Lazy Loading**: Не загружать все skills в начале сессии, только по требованию | 3-5K | Low |
| O2 | **Truncate Orchestrator**: Убрать дублирующиеся сценарии из `01_orchestrator.md` | 1-1.5K | Medium |
| O3 | **Split architecture-format**: Разбить на базовый и extended варианты | 1.5-2K | Low |
| O4 | **Archive Conversation**: Периодически summarize conversation history | 5-15K | Medium |

#### 3.2 MEDIUM-TERM (Minor Refactoring)

| # | Recommendation | Savings | Risk |
|---|----------------|---------|------|
| O5 | **Skill Tiers**: Разделить skills на `core` (always load) и `extended` (on-demand) | 4-6K | Low |
| O6 | **Agent Prompt Compression**: Использовать более компактный синтаксис | 2-3K | Medium |
| O7 | **Context Checkpointing**: Сохранять state между фазами в артефакты, не в контекст | 10-20K | Medium |

#### 3.3 STRATEGIC (For Enterprise Extension)

| # | Recommendation | Impact | Complexity |
|---|----------------|--------|------------|
| O8 | **Domain Isolation**: Загружать только domain-specific артефакты | Critical | High |
| O9 | **Multi-Session Pipeline**: Каждая фаза = отдельная сессия с artifact handoff | Critical | High |
| O10 | **Hierarchical Context**: Summarized parent context + full current phase | High | High |

---

### 4. Optimized Token Budget (Target)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPTIMIZED TOKEN BUDGET (PROPOSED)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Category                          Current        Target         Δ         │
│  ─────────────────────────────────────────────────────────────────────────  │
│  IDE System Prompt                 ~5,000         ~5,000        0%         │
│  Framework Bootstrap               ~2,400         ~1,200       -50%        │
│  Mandatory Skills                  ~2,100         ~1,000       -52%        │
│  Active Agent Prompt (1 at a time) ~1,500         ~1,000       -33%        │
│  Phase-Specific Skills             ~2,500         ~1,500       -40%        │
│  Project Artifacts (TASK, ARCH)    ~2,500         ~2,000       -20%        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Framework Overhead (Total)        ~16,000        ~11,700      -27%        │
│                                                                             │
│  Available for Code + History      ~112,000       ~116,300     +4%         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 5. VDD Review of Optimizations

> **Sarcasmotron:** "Oh, you want to *optimize* the framework that *already works*? What could go wrong?"

#### Challenge 1: Lazy Loading Failure Mode

**Risk:** Agent forgets to load required skill → hallucination
**Mitigation:** Explicit `REQUIRED_SKILLS` header in each agent prompt, validated at start

#### Challenge 2: Compression = Ambiguity

**Risk:** Shorter prompts → less precise instructions → more interpretation errors
**Mitigation:** A/B testing: run same task with original vs compressed prompts, measure hallucination rate

#### Challenge 3: Multi-Session State Loss

**Risk:** Artifact-based handoff loses nuanced context
**Mitigation:** Structured artifact schemas with explicit "context carryover" sections

---

### 6. Recommended Next Steps

1. **[ ] Measure Baseline:** Run 5 standard development tasks, collect actual token usage via IDE logs
2. **[ ] Implement O1-O4:** Low-risk optimizations, measure improvement
3. **[ ] Create `skill-context-management`:** Formalize lazy loading and checkpointing protocols
4. **[ ] Test Enterprise Scenario:** Run domain-isolated task to validate O8 approach

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-21 | Adversarial Architect | Added Token Consumption Analysis appendix |
| 2026-01-21 | Adversarial Architect | Critical VDD Review, restructured document |
| 2026-01-XX | Original Author | Initial vision document |