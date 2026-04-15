[Русская версия](CHANGELOG.ru.md) | [English version](CHANGELOG.md)

<!--
## [Не реализовано]

### 🇷🇺 Русский
#### Добавлено
- ...

#### Изменено
- ...

#### Исправлено
- ...
-->

## 🇷🇺 Русская версия

### **v3.9.17 — Дисциплина разработки: интеграция Karpathy Guidelines**

#### **Добавлено**
* **§1.5 Think Before Implementing** (`developer-guidelines`): Градуированный протокол обработки неоднозначности — критическая неоднозначность фиксируется в TASK.md Open Questions, реализационные решения принимаются разработчиком с кратким документированием, тривиальные решения принимаются молча.
* **§1.6 Implementation Discipline** (`developer-guidelines`): Двухуровневая модель решений — архитектурные решения (новые модули, публичный API, модели данных) должны следовать из PLAN.md/ARCHITECTURE.md; детали реализации (внутренние паттерны, хелперы, абстракции) — профессиональное суждение разработчика. Спекулятивная сложность запрещена.
* **§6.2 Multi-Step Tasks** (`developer-guidelines`): Обобщённый Verification Protocol с паттерном `Step → verify: [check]`, расширяющий Bug Fixing Protocol на все многошаговые задачи.
* **Before/after примеры кода** (`developer-guidelines/examples/coding-anti-patterns.md`): 3 примера — drive-by рефакторинг, спекулятивные фичи vs. реализация по плану, молчаливая интерпретация vs. выявление неоднозначности. Адаптировано из Karpathy Guidelines для контекста комплексной продуктовой разработки.

#### **Улучшено**
* **Red Flags** (`developer-guidelines` §0): +2 записи — против молчаливых архитектурных изменений и спекулятивных фич.
* **Strict Adherence** (`developer-guidelines` §1): +2 записи — Task Traceability (каждое изменение должно служить задаче, профессиональные решения в рамках scope допустимы) и Style Matching (соответствие существующему стилю кода).
* **Rationalization Table** (`developer-guidelines` §9): +3 записи про спекулятивные добавления, молчаливое отклонение от плана и drive-by улучшения.
* **Atomicity & Traceability** (`core-principles` §1): Добавлены Verification Checkpoints для многошаговых задач.
* **Minimizing Hallucinations** (`core-principles` §3): Добавлен Ambiguity Protocol с перекрёстной ссылкой на developer-guidelines §1.5.
* **Бюджет токенов** (`skill-phase-context`): Обновлена оценка фазы Development с ~768 до ~1,100 для отражения расширенного developer-guidelines.

#### **Проектные решения**
* **"Implementation Discipline" вместо "Simplicity First"**: Принцип Karpathy "minimum code" адаптирован для комплексной продуктовой разработки — архитектурная сложность валидна когда следует из плана; запрещается только спекулятивная сложность.
* **Градуированная неоднозначность вместо "спрашивай всё"**: Трёхуровневый протокол предотвращает бомбардировку пользователя вопросами, при этом критические решения выносятся на обсуждение.
* **Новый отдельный скилл не создавался**: Все изменения интегрированы в существующие `developer-guidelines` (Tier 1) и `core-principles` (Tier 0) во избежание раздувания скиллов и конфликтов тиров.

---

### **v3.9.16 — Security Audit v3.2: Паттерны смарт-контрактов и модульная архитектура**

#### **Добавлено**
* **Паттерны Solidity/Smart Contract** (16 новых): Reentrancy (`.call{value:}`, `.send()`, `.transfer()`), произвольное выполнение (`delegatecall`, `selfdestruct` EIP-6780, `suicide()`), контроль доступа (`tx.origin`, public/external без модификатора), манипуляция оракулами (`getReserves()`, `latestRoundData()`), непроверенные возвращаемые значения, незащищённые инициализаторы, целочисленное переполнение (до 0.8.0), заблокированный ETH, inline assembly.
* **VDD Раунд 3 критика** с матрицей покрытия реальных взломов (Дек 2025 – Март 2026).
* **Валидация по реальным взломам**: Сканер протестирован на контрактах, симулирующих атаки SwapNet ($13.4M), Truebit ($26.4M), YieldBlox ($10.2M), Aperture ($4M) — 7/10 векторов обнаружены.

#### **Улучшено**
* **Модульная архитектура сканера**: Рефакторинг монолита `run_audit.py` (886 строк) в пакет из 7 файлов (`audit/config.py`, `audit/patterns.py`, `audit/helpers.py`, `audit/scanners.py`, `audit/external.py`, `audit/__init__.py`).
* **Единообразие MAX_FILE_SIZE**: Добавлена защита 5MB в `scan_configuration()` и `scan_iac()`.
* **Количество паттернов**: 105 → 121 (28 секреты + 62 опасные + 25 IaC + 6 конфиг).

#### **Исправлено**
* **VDD Раунд 2** (8 замечаний): Неверная классификация `os.popen()` CWE, отсутствующий `subprocess.run shell=True`, regex open redirect для Flask, обнаружение SQL `%` форматирования, ложные срабатывания IaC на не-IaC YAML, следование по символическим ссылкам, расширение паттерна SSRF.

---

### **v3.9.15 — Интеграция Claude Code**

#### **Добавлено**
* **Точка входа Claude Code**: Создан `CLAUDE.md` (136 строк), адаптированный из `GEMINI.md` с нативными инструментами Claude Code (Read, Write, Edit, Bash, Grep, Glob), bootstrap сессии и явным протоколом загрузки навыков по тирам.
* **Хуки Claude Code**: Добавлены `.claude/settings.json` с хуком `PostToolUse` и `.claude/hooks/validate_skill_hook.sh` для автоматической валидации навыков при модификации файлов.
* **Команды Claude Code**: Созданы 20 файлов слэш-команд в `.claude/commands/`, покрывающих все 21 workflow (паттерн делегатора — единый источник истины в `.agent/workflows/`).
  * Основные: `/start-feature`, `/plan`, `/develop`, `/develop-all`, `/light`
  * VDD: `/vdd`, `/vdd-start-feature`, `/vdd-plan`, `/vdd-develop`, `/vdd-adversarial`, `/vdd-multi`
  * Пайплайны: `/full`, `/security-audit`, `/base-stub-first`, `/framework-upgrade`, `/iterative-design`
  * Продуктовые: `/product-full-discovery`, `/product-market-only`, `/product-quick-vision`
  * Документация: `/update-docs`
* **Спецификация миграции**: Добавлен `docs/migration-to-claude.md` с полным сравнением платформ, маппингом инструментов, руководством по адаптации хуков и чеклистом валидации.

#### **Улучшено**
* **AGENTS.md**: Добавлена недостающая инструкция "Session State Persistence" (`update_state.py` на границах фаз) для паритета с `GEMINI.md`.
* **SESSION_CONTEXT_GUIDE.md**: Добавлена секция 5 "Platform Memory Integration" — документация о взаимодополняемости сессионного состояния фреймворка и платформенных систем памяти (Claude Code, Cursor, Gemini).
* **README.md / README.ru.md**: Обновлена секция "Вариант В: Claude Code" — ручные инструкции по настройке заменены на готовую конфигурацию и полный список команд.

---

### **v3.9.14 — Волна Enterprise Hardening (BI-001..009)** (Security / Reliability / Governance)

#### **Добавлено**
* **Governance-документы**:
    * Добавлен `System/Docs/SOURCE_OF_TRUTH.md` с авторитетной картой prompts, skills, workflows, tools и command conventions.
    * Добавлен `System/Docs/RELEASE_CHECKLIST.md` с релизными gate-проверками и обязательными командами валидации.
* **Скрипты валидации и guardrails**:
    * Добавлены `System/scripts/check_prompt_references.py`, `System/scripts/security_lint.py`, `System/scripts/smoke_workflows.py`, `System/scripts/validate_skills.py`, `System/scripts/doctor.py`.
* **CI gatekeeping**:
    * Добавлен `.github/workflows/framework-gates.yml` для принудительных проверок tooling-тестов, валидации skills, smoke-проверок workflows, целостности ссылок и security lint.
* **Регрессионное покрытие**:
    * Добавлены `tests/test_tool_runner_security_contract.py`, `tests/test_spec_validator.py`, `tests/test_product_handoff_scripts.py`.
* **skill-creator v1.3 (Anthropic Skill Standards Sync)**:
    * **Structured Evals Workflow**: Добавлена полноценная секция по написанию и запуску вендор-агностичных тестов (evals) для скиллов с использованием LLM-как-судья. Внедрен формат `evals/evals.json`.
    * **Agent Prompts**: В папку `agents/` перенесены 3 готовых промпта для автоматизированной оценки скиллов: `grader.md`, `comparator.md`, `analyzer.md`.
    * **Скрипты агрегации и отчетности**: В папке `scripts/` добавлена инфраструктура для работы с результатами эвалюаторов (`aggregate_benchmark.py`, `generate_report.py`, `generate_review.py`).
    * **JSON Schemas**: Добавлен файл `references/eval_schemas.md`, задающий единый Source of Truth для 8 различных JSON-форматов оценки.
* **skill-enhancer v1.2 (Anthropic Skill Standards Sync)**:
    * **Phase 1.7: Behavioral Analysis**: В жизненный цикл аудита добавлена новая фаза. Теперь enhancer проверяет логи использования старого скилла и рекомендует вынести FAQ в `references/`, а helper-код в `scripts/`.

#### **Улучшено**
* **Безопасность выполнения инструментов (BI-001)**:
    * Усилен `System/scripts/tool_runner.py` (политика `shell=False`, блок shell-операторов/символов, allowlist-команд, таймауты, нормализация и проверка `cwd`).
    * Расширены и синхронизированы схемы в `.agent/tools/schemas.py`; обновлена документация рантайма в `System/Docs/ORCHESTRATOR.md`.
* **Целостность workflow и путей (BI-002, BI-009)**:
    * Починены устаревшие ссылки на prompts/workflows в workflow-файлах и README.
    * Нормализованы command conventions: канонический формат `run <workflow-name>` + явные alias-заметки для slash-формы.
* **Стандартизация Python-окружения (BI-004)**:
    * Добавлен `requirements-dev.txt` с pinned-зависимостями и инструкции по setup в `README.md` и `README.ru.md`.
* **Стандартизация skills, технический контур (BI-007)**:
    * Добавлены недостающие `tier`/`version` в metadata.
    * Ослаблено строгое применение CSO-prefix для уже работающих legacy-skills (без принудительного переименования).
* **Усиление execution-policy в мета-скилах**:
    * Обновлены `.agent/skills/skill-creator/SKILL.md` и `.agent/skills/skill-creator/assets/SKILL_TEMPLATE.md`: добавлены обязательные секции `Execution Mode`, `Script Contract`, `Safety Boundaries`, `Validation Evidence`.
    * Расширен `.agent/skills/skill-creator/scripts/validate_skill.py`: warning-first проверки execution-policy + опциональный строгий режим (`--strict-exec-policy`).
    * Расширен `.agent/skills/skill-enhancer/scripts/analyze_gaps.py`: детектирование execution-policy gap-ов (отсутствующие секции контракта + сигналы по script/scope safety).
    * Обновлен `.agent/skills/skill-enhancer/references/refactoring_patterns.md`: паттерны миграции prompt-only -> hybrid, ad-hoc script -> governed script, unsafe mutation -> scoped mutation.

* **Операционное выравнивание skill-validator (BI-007 follow-up)**:
    * Добавлен `validation.inline_exempt_skills` в `.agent/rules/skill_standards.yaml` для legacy-скилов с обязательными большими inline-блоками.
    * Обновлен `.agent/skills/skill-creator/scripts/validate_skill.py`: проверка лимита inline-блоков пропускается только для явно исключенных скилов, при этом дефолтный лимит для новых скилов сохранен.
* **Повышена discoverability дефолтов skill-creator**:
    * Добавлен `.agent/skills/skill-creator/references/default_parameters.md` (порядок резолва конфигурации, bundled defaults, runtime fallback-правила, maintenance rule).
    * Обновлен `.agent/skills/skill-creator/SKILL.md`: добавлены ссылки на defaults map и `skill_utils.py` для просмотра эффективной merged-конфигурации.
* **Точная настройка release checklist**:
    * Обновлен `System/Docs/RELEASE_CHECKLIST.md`: проверки Product Handoff сделаны опциональными и обязательны только при изменениях в `skill-product-handoff`.
* **skill-creator v1.3 (Anthropic Skill Standards Sync)**:
    * **Graduated Instructions**: Вместо жесткого требования `MUST/ALWAYS` везде, внедрен двухуровневый подход: жесткий `MUST + explanation` для критичных шагов и `explain why + do` для поведенческих настроек.
    * **Description Pushiness Optimization (CSO)**: Расширено руководство по SEO-оптимизации описания скилла: рекомендуется писать более агрессивные триггеры для предотвращения under-triggering.
    * **Behavior Iteration Loop**: Добавлен шаг в алгоритм создания скилла: выявлять повторяющийся код или вопросы агента во время тестов и переносить их в `scripts/` или `references/`.
    * **Environment Adaptation**: Добавлены рекомендации по описанию Fallback-стратегий для скиллов, которые зависят от специфичных CLI или браузеров.
    * **Target Audience Selection**: Инструкция теперь требует явно определить целевую аудиторию перед написанием скилла.
* **skill-enhancer v1.2 (Anthropic Skill Standards Sync)**:
    * **Graduated Language Check**: Скрипт `analyze_gaps.py` и инструкции теперь проверяют текст по "Двухуровневой" системе мотивации. Обновлены VDD-чеклисты и паттерны рефакторинга.
    * **Description Pushiness Check**: Добавлено правило проверки описания оцениваемого скилла на достаточную "агрессивность" триггеров.
    * **Test Coverage Check**: Фаза финальной проверки принудительно проверяет, имеет ли скилл хотя бы 2-3 тестовых промпта (в `evals.json` или описанных текстом).
    * **Generalization Check**: Добавлен аудит на overfitting (переобучение) скилла под очень узкие примеры.
    * Обновлены локальные ссылки на SSoT агентов (`skill-creator/agents/`).

#### **Исправлено**
* **Корректность spec-validator (BI-003)**:
    * Исправлена логика сопоставления ID требований в `.agent/skills/skill-spec-validator/scripts/validate.py` (literal token matching + регрессионные тесты).
* **Усиление product handoff scripts (BI-008)**:
    * Усилены `.agent/skills/skill-product-handoff/scripts/sign_off.py`, `.agent/skills/skill-product-handoff/scripts/verify_gate.py`, `.agent/skills/skill-product-handoff/scripts/compile_brd.py` (argparse CLI, явные file-аргументы, safe path validation).
* **Усиление Artifact Memory, техническая часть (BI-006)**:
    * Расширен `.agent/skills/skill-update-memory/scripts/suggest_updates.py` с детерминированным bootstrap-контуром:
        * Добавлены `--mode bootstrap` + `--create-missing` для контролируемой инициализации memory-файлов.
        * Добавлен явный scope разработки через `--development-root` (по умолчанию: `src`).
        * Добавлены жёсткие исключения для `/.agent/skills/*` и `/.cursor/skills/*`, чтобы исключить нежелательное создание memory-файлов в каталогах skills.
        * Сохранено корректное поведение при отсутствии `.AGENTS.md` (без hard-fail).
    * Синхронизирован workflow/docs-контракт для миграционного запуска:
        * Обновлена bootstrap-команда в `.agent/workflows/04-update-docs.md` с `--development-root src`.
        * Обновлены `System/Docs/SOURCE_OF_TRUTH.md` и docs навыков (опциональность `.AGENTS.md` + scoped bootstrap policy).
* **skill-creator v1.3**:
    * Обновлен `validate_skill.py`: папки `agents/` и `evals/` теперь внесены в `allowed_dirs` во избежание false-positives при строгой проверке.
    * Опечатки в JSON ключах (`input_files` -> `files`, `expected_outcomes` -> `expectations`) в примерах `SKILL.md` исправлены для полного соответствия схемам.
* **skill-enhancer v1.2**:
    * `analyze_gaps.py`: Улучшен парсинг markdown-файлов. Скрипт больше не триггерит false-positives на отсутствие префикса `Phase/Step` внутри блоков JSON.
    * Отчищены фантомные ссылки на "(Coming in Iteration 2)" — вся заявленная архитектура теперь существует в реальности.

#### **Проверено**
* В target-репозитории проходят `System/scripts/check_prompt_references.py --root .` и `System/scripts/smoke_workflows.py --root .`.
* Статусы backlog синхронизированы: BI-001..006, BI-008 и BI-009 отмечены как `Done` в `Backlog/archive/framework_improvements_20260219.md`.

---

### **v3.9.13 — Усиление Аудита Безопасности & Синхронизация Workflow** (Feature / Maintenance)

#### **Добавлено**
* **Developer Guidelines**:
    * **Security Quick-References**: Добавлены сжатые руководства для 10 фреймворков (Flask, Django, FastAPI, Express, Next.js, React, Vue, jQuery, JS General, Go).
    * **Динамическая загрузка**: Обновлен `SKILL.md` (v1.1) для контекстной загрузки строгих правил безопасности.

#### **Рефакторинг**
* **`security-audit` Workflow**:
    * **Единый Скрипт**: Обновлен `.agent/workflows/security-audit.md` для использования унифицированного скрипта `run_audit.py`.
    * **Модернизация**: Удалены устаревшие ссылки на промпты, шаги ручного ревью синхронизированы с протоколом "Думай как хакер".
* **`skill-adversarial-security` (v1.1)**:
    * **Gold Standard**: Добавлены строгие "Red Flags" (Анти-Рационализация) и "Rationalization Table" (Оправдания разработчика).
    * **Очистка**: Удалены дублирующиеся секции, команды запуска скрипта обновлены до v2 стандартов.
    * **Верификация**: Проверена интеграция с воркфлоу `vdd-adversarial` и `vdd-multi`.

#### **Улучшено**
* **`security-audit` (v2.1)**:
    * **Единый Сканер**: `run_audit.py` теперь объединяет внутренний статический анализ (Секреты, Опасные паттерны) с запуском внешних инструментов (`slither`, `bandit`, `npm audit`).
    * **Gold Standard Compliance**: Добавлены "Red Flags" (Анти-Рационализация), стандарты отчетности и обязательные чек-листы "Думай как хакер".
    * **OWASP 2025**: Проверки обновлены до стандарта OWASP Top 10:2025 (Security Supply Chain, Exceptional Conditions).
    * **Восстановление Чек-листов**: Явно восстановлены и сделаны обязательными ссылки на `solana_security.md`, `solidity_security.md` и `fuzzing_invariants.md`.

#### **Исправлено** *(VDD Adversarial Hardening)*
* **Security References**:
    * Исправлены фактические неточности во `flask.md` (устаревший `FLASK_ENV`, `safe_join` CVE) и `django.md` (порядок middleware) через VDD Adversarial Review.
* **`run_audit.py`**:
    * Молчаливое `except: pass` → логирование в stderr + счётчик `skipped_files` в отчёте.
    * Ложные срабатывания на себя → самоисключение через `_is_self_path()`.
    * Строковое совпадение `SKIP_DIRS` → проверка по basename (`dirs[:]` pruning).
    * `run_command` теперь отслеживает и выводит exit-коды внешних инструментов.
    * Добавлен таймаут 120с на все вызовы `subprocess.run`.
    * `SKIP_DIRS` расширен: `.cache`, `.idea`, `.vscode`, `vendor`, `tmp`, `coverage`.
* **`SKILL.md`**: Исправлены маппинги OWASP (Secrets→A02, Deps→A06, Patterns→A03, Config→A05). Добавлена Rationalization Table (Section 6).
* **`owasp_top_10.md`**: Устранён дубликат A10 (SSRF объединён в единый A10). A08 слит с A03.

---

### **v3.9.12 — Целостность фреймворка, Параллельные Агенты и Безопасность** (Feature / Bugfix)

#### **Добавлено**
* **Архитектура Параллельных Агентов (POC)**:
    * **Новый навык: `skill-parallel-orchestration` (Tier 2)**: Протокол декомпозиции задач на параллельные подзадачи и запуск суб-агентов (мок-раннер).
    * **Конкурентная безопасность состояния**: `update_state.py` теперь использует `fcntl` файловую блокировку для атомарных операций чтения-записи `latest.yaml`, предотвращая гонки.
    * **Мок-раннер агентов**: `spawn_agent_mock.py` эмулирует асинхронное выполнение агентов с обновлением состояния.
    * **Документация**: Гайд `docs/POC_PARALLEL_AGENTS.md` и обновлена `docs/ARCHITECTURE.md` (Модель параллельного выполнения).
* **Хук автовалидации навыков**:
    * **`.gemini/hooks/validate_skill_hook.sh`**: `AfterTool` хук, автоматически запускающий `validate_skill.py` при каждой записи в `.agent/skills/`.
    * **`.gemini/settings.json`**: Конфигурация хука с фоллбеком `$GEMINI_PROJECT_DIR` для кросс-раннер совместимости.
    * **Skill Creation Gate**: Добавлено обязательное правило `init_skill.py` в `GEMINI.md` и `AGENTS.md` (фаза разработки). Ручное создание навыков запрещено.

#### **Улучшено**
* **Навыки VDD (v1.1)**:
    * **`vdd-adversarial`**: Добавлены **Red Flags** (Анти-Рационализация), **Rationalization Table** и явная ссылка на `examples/`.
    * **`vdd-sarcastic`**: Добавлены **Red Flags** (Анти-Рационализация), **Rationalization Table** и явная ссылка на `examples/`.

#### **Исправлено**
* **Предотвращение потери данных**: Пропатчен `trigger_technical.py`, теперь он прерывает выполнение, если `docs/TASK.md` уже существует, предотвращая случайную перезапись при передаче продукта.
* **Целостность протокола**: Обновлен сценарий `light-02-develop-task`, теперь он требует обязательного обновления `.AGENTS.md`, предотвращая дрейф памяти в Light Mode.
* **Стандартизация**: Обновлен `vdd-01-start-feature` для использования авторитетного протокола `skill-archive-task` вместо хардкодных ручных шагов.
* **Shell Injection (VDD)**: В `validate_skill_hook.sh` заменена heredoc-интерполяция на `jq -n` для защиты от некорректного JSON в `validation_output`.
* **Невалидный Mode (VDD)**: Исправлен `spawn_agent_mock.py` — использовал несуществующий режим `"Wrapper"` → `"EXECUTION"`.

---



### **v3.9.11 — Hardened Pipeline & Система Самосовершенствования** (Feature)

#### **Добавлено**
* **Новый навык: `skill-spec-validator` (Tier 2)**:
    * **RTM Валидация**: Механически требует, чтобы `docs/TASK.md` содержал Матрицу Трассируемости Требований (RTM).
    * **Атомарное Планирование**: Механически требует, чтобы `docs/PLAN.md` покрывал каждый пункт RTM задачей с ID-тегом (например, `[R1]`).
* **Новый навык: `skill-self-improvement-verificator` (Tier 3)**:
    * **Meta-Audit**: Действует как "Страж" самого фреймворка. Аудирует спецификации для `framework-upgrade`, чтобы предотвратить регрессию.
* **Новый сценарий (Workflow): `/framework-upgrade`**:
    * Специализированный пайплайн для обновления Промптов, Навыков и Системной Логики.
    * Интегрирует проверки `skill-self-improvement-verificator` на этапах Анализа и Планирования.
* **Документация**:
    * **Claude Code & Gemini CLI**: Добавлены руководства по нативной интеграции (Варианты В и Г) в README.
    * **Deep Dive**: Добавлен раздел "Чертеж против Драйвера" (Blueprint vs Driver) для разъяснения ролей `00_agent_development.md` и `AGENTS.md`.
    * **Сценарии использования**: Добавлены практические примеры для Стандартного режима, Light Mode и Восстановления сессии.

#### **Улучшено**
* **Сценарии (Workflows)**:
    * **`/vdd-enhanced`**: Обновлен до "Hardened Mode". Теперь включает контрольные точки `skill-spec-validator` с циклами авто-коррекции (макс. 3 попытки).
* **Промпты Агентов**:
    * **Analyst**: Обязательная генерация RTM таблицы (кроме задач `[LIGHT]`).
    * **Planner**: Обязательные Атомарные Чек-листы со строгой ID-привязкой.
    * **Developer**: Принудительная методология Strict Stub-First (кроме задач `[LIGHT]`).
* **Надежность**:
    * **`skill-creator`**: теперь выводит обязательные инструкции по очистке для предотвращения мусора.
    * **`validate.py`**: исправлена устойчивость парсинга Markdown таблиц с экранированными символами.

---


### **v3.9.10 — Чистка Skill Creator и Brainstorming 2.1** (Оптимизация)

#### **Улучшено**
* **`skill-creator`**:
    * **Протокол очистки**: Добавлены конкретные инструкции по удалению неиспользуемых папок-заполнителей (`scripts/`, `assets/`, `references/`) после инициализации навыка.
    * **Валидация**: Проверено, что `validate_skill.py` поддерживает "легкие" навыки без пустых папок.
* **`brainstorming`** (v2.1):
    * **Универсальный Стандарт**: Обновлен до v2.1 с поддержкой "Универсальной" совместимости (агностицизм к инструментам).
    * **3-Уровневая Оценка**: Внедрена классификация сложности **Тривиально/Средне/Сложно** с адаптированными протоколами.
    * **Барьеры Безопасности**: Добавлены строгие правила "Никакого Кода без Дизайна" и шаблоны передачи задач.

---

### **v3.9.9 — Миграция Ресурсов Навыков и Усиление Валидации** (Оптимизация)

#### **Рефакторинг**
* **Стандартизация Навыков (Gold Standard)**:
    * **Гигиена Папок**: Папки `resources/` мигрированы в `assets/` (шаблоны) и `references/` (знания) во всех навыках.
    * **Удаление Legacy**: Директория `resources/` объявлена устаревшей для строгого соблюдения семантической структуры папок.

#### **Исправлено**
* **Валидация**:
    * **Поддержка Config**: Обновлен `validate_skill.py`, теперь явно разрешена папка `config/` (восстановлена поддержка `skill-product-solution-blueprint`).
    * **Нарушения CSO**: Исправлены префиксы описаний в 6 навыках (`developer-guidelines`, `requirements-analysis` и др.) для соответствия "Gold Standard" (`Use when`, `Guidelines for`).

#### **Верифицировано**
* **Глобальный Аудит**: Запущен скрипт верификации всех мигрированных навыков: 0 битых ссылок, 100% прохождение валидации.

---

### **v3.9.8 — Независимость Мета-Навыков** (Рефакторинг)
#### **Развязка (Decoupling)**
* **Проектно-Агностичные Мета-Навыки**: `skill-creator` и `skill-enhancer` теперь полностью портативны и независимы от проекта Antigravity.
    * **Конфигурируемость**: Политики (Уровни, Запрещенные слова, Правила файлов) теперь загружаются из `.agent/rules/skill_standards.yaml` вместо хардкода в Python словарях.
    * **Без Зависимостей**: Удалена зависимость `PyYAML`. Реализован кастомный "Vanilla Python" парсер (`skill_utils.py`), чтобы инструменты работали в любом окружении без `pip install` или `venv`.
    * **Документация**: Удалены хардкод-ссылки на `System/Docs/SKILLS.md` и "Gemini/Antigravity". Заменены на универсальные концепции "Каталога Навыков".

#### **Добавлено**
* **Новое Руководство**: `System/Docs/skill-writing.md` — Портативный гайд пользователя для мета-навыков (Установка, Конфиг, Использование).
* **Устойчивость**: Скрипты теперь включают **Встроенный Дефолтный Конфиг** (`skill_standards_default.yaml`) для мгновенного запуска "из коробки".

#### **Верифицировано**
* **E2E Тестирование**: Подтверждена работа динамических уровней (tiers), корректность парсера (включая сложные случаи инлайн-словарей) и gap-анализа на тестовом навыке.

---

### **v3.9.7 — Усиление навыков и Рефакторинг (Gold Standard)** (Оптимизация)

#### **Рефакторинг (Gold Standard)**
* **`documentation-standards`**:
    * **Оптимизация токенов**: Шаблоны вынесены в `resources/templates/` (>60% экономии).
    * **Полнота**: Добавлен пример `examples/good_documentation.py`.
    * **Устойчивость**: Добавлены разделы "Red Flags" (Красные флаги) и "Rationalization Table" (Таблица оправданий).
* **`skill-planning-format`**:
    * **Оптимизация**: Массивные шаблоны (`PLAN.md`, `TASK.md`) вынесены в `resources/templates/`.
    * **Примеры**: Добавлены реалистичные `examples/PLAN_EXAMPLE.md` и `examples/TASK_EXAMPLE.md`.
* **`skill-task-model`**:
    * **Полнота**: Примеры Use Case (Good/Bad) вынесены в файлы `examples/`.
    * **Устойчивость**: Добавлены "Red Flags" и "Rationalization Table".

#### **Исправлено**
* **`light-mode`**: Исправлена ошибка YAML-синтаксиса (тег `[LIGHT]` теперь в кавычках) и нарушение CSO в описании.
* **`skill-safe-commands`**: Обновлена документация (добавлено упоминание `AGENTS.md`).

#### **Улучшено**
* **Системная устойчивость**:
    * **Без зависимостей**: Удалена зависимость `PyYAML` из `validate_skill.py` и `analyze_gaps.py`.
    * **Надежный парсер**: Реализован ручной YAML-парсер, корректно обрабатывающий кавычки, списки и комментарии.
* **CSO Схемы**: Обновлены `skill-creator` и `skill-enhancer`, добавлены разрешенные префиксы: `Use when`, `Guidelines for`, `Standards for`, `Defines`, `Helps with`.

---

### **v3.9.4 — Глубокий рефакторинг продуктовых навыков** (Оптимизация)

#### **Рефакторинг**
* **Strategic Analyst (`p01`):**
    * Промпт: Удален встроенный шаблон, добавлен `Execution Loop` с шагами Deconstruct/Timing/Moat.
    * Навык `skill-product-strategic-analysis`:
        * Добавлен `market_strategy_template.md` (Core Thesis, Moat Score, Risks).
        * Добавлен пример `01_strong_ai_assistant.md` (Strong Go).
        * Добавлен пример `02_nogo_vertical_video.md` (No-Go).
* **Product Analyst (`p02`):**
    * Промпт: Добавлен вход `User Refinements`, делегирование Vision навыку.
    * Навык `skill-product-analysis`:
        * Обновлен `vision_template.md` (Pillars, Moat Score, Emotional Logic).
        * Добавлены примеры: `01_strong_go_devboost`, `02_consider_talentflow`, `03_nogo_quickbites`.
* **Solution Architect (`p04`):**
    * Промпт: Удален дублирующийся шаблон.
    * Навык `skill-product-solution-blueprint`:
        * Обновлен `solution_blueprint_template.md` (Unit Economics, Verdict).
        * Обновлен `calculate_roi.py`: вывод ARPU, CAC, LTV/CAC.
        * Добавлены примеры: `01_simple_flexarb` и `02_advanced_loyaltyhub`.
* **Director (`p03`):**
    * Промпт: Интегрирован навык `skill-product-backlog-prioritization`.
    * Добавлен шаг "Auto-Prioritization" (WSJF) перед подписью.
    * Добавлен шаг "Auto-Hash" через `sign_off.py`.

#### **Улучшено**
* **Консистентность:** Все продуктовые агенты (`p01`, `p02`, `p04`) теперь используют единую архитектуру "Промпт → Навык → Внешний Шаблон".
* **Скоринг:** Внедрен количественный скоринг (10-факторная матрица) и логика "Вердикта" во все продуктовые артефакты.

---

### **v3.9.3 — Гигиена Документации и JSON Стандарт** (Maintenance)

#### **Изменено**
* **Стандартизация Документации:**
    * **JSON Only:** В `skill-product-solution-blueprint` убраны упоминания YAML. Строгий стандарт `.json` для `calculate_roi.py`.
    * **Гигиена Путей:** Рекомендованная папка для временных артефактов — `docs/product/`.
* **Структура Ресурсов:**
    * Упрощена структура шаблонов (удалена подпапка `templates/`, файлы перенесены в корень `resources/`).
    * Обновлены ссылки в `SKILL.md`.

---

### **v3.9.2 — Рефакторинг Продуктовых Навыков и Усиление Математики** (Оптимизация)

#### **Добавлено**
* **Продвинутые Финансы:** `calculate_roi.py` теперь поддерживает:
    * **Гранулярная Оценка:** T-Shirt размеры (XS-XXL) с конфигом в `sizing_config.json`.
    * **LLM Акселерация:** Скидка на часы разработки на основе "Friendliness" (дружелюбности к ИИ).
    * **Метрики:** NPV (3 года), LTV, CAC и срок окупаемости.
* **Скоринг Продукта:** Новый `score_product.py` с 10-факторной матрицей (Интенсивность проблемы, Ров и т.д.).
* **Документация:**
    * `System/Docs/PRODUCT_CALCULATIONS_MANUAL.md`: Подробное руководство "Magic Math".
    * Обновлен `System/Docs/PRODUCT_DEVELOPMENT.md`.

#### **Оптимизировано**
* **Приоритизация:** `calculate_wsjf.py` поддерживает T-Shirt размеры (S, M, L) с маппингом в Фибоначчи.
* **Безопасность (VDD):**
    * Исправлен баг "Путешествия во времени" (отрицательная длительность) в `calculate_roi.py`.
    * Ограничены инпуты `score_product.py` (1-10).
    * Удалена зависимость `PyYAML`.

---

### **v3.9.1 — Синхронизация Документации и Очистка** (Maintenance)

#### **Оптимизировано**
* **Синхронизация Документации:**
    * Обновлены `README.md` и `README.ru.md` для полного отражения возможностей Product Development (Агенты, Воркфлоу, Артефакты).
    * Описание `00_agent_development.md` уточнено как "Мета-Системный Промпт".
* **Стандартизация (O6a):**
    * Обновлены `System/Docs/SKILLS.md` и `SKILL_TIERS.md` для строгого соблюдения паттернов "Script-First" и "Example Separation".
    * Удалены устаревшие ссылки на `Backlog/agentic_development_optimisations.md`.
* **Очистка:**
    * Архивирован `Backlog/agentic_development_optimisations.md`, так как все вехи оптимизации (O1-O7) завершены и задокументированы в System Docs.

---

### **v3.9.0 — Product Discovery & Handoff** (Feature)

#### **Добавлено**
* **Завершена Продуктовая Фаза:** Полный пайплайн "Venture Builder" с 5 новыми агентами (`p00`-`p04`).
    * **Strategy:** `skill-product-strategic-analysis` (TAM/SAM/SOM).
    * **Vision:** `skill-product-analysis` (Crossing the Chasm).
    * **Solution:** `skill-product-solution-blueprint` (ROI, Risk, Text-UX).
* **Ворота Качества (Quality Gate - VDD):**
    * **Adversarial Director (`p03`):** Блокирует передачу в разработку, если "Рыночный ров" слаб.
    * **Криптографический Handoff:** Цепочка `sign_off.py` -> `verify_gate.py` гарантирует, что только утвержденные бэклоги попадают к разработчикам.
* **Сценарии (Workflows):**
    * `/product-full-discovery`: Полный цикл Venture Building.
    * `/product-quick-vision`: Для внутренних инструментов.
    * `/product-market-only`: Для быстрой валидации идей.
* **Документация:**
    * `System/Docs/PRODUCT_DEVELOPMENT.md`: Полный плейбук.
    * `System/Docs/WORKFLOWS.md`: Обновлен продуктовыми сценариями.

---

### **v3.8.0 — Фаза 0: Product Bootstrap** (Feature)

#### **Добавлено**
* **Модуль Управления Продуктом:**
    * **Новые Навыки:** `skill-product-analysis` (Видение) и `skill-product-backlog-prioritization` (WSJF).
    * **Новые Агенты:** `p01_product_analyst` (Создатель) и `p02_product_reviewer` (VDD Критик).
    * **Новая Документация:** [`System/Docs/PRODUCT_DEVELOPMENT.md`](System/Docs/PRODUCT_DEVELOPMENT.md) со сценариями использования.
* **Нативная Интеграция Инструментов:**
    * **Инструменты:** `init_product` и `calculate_wsjf` зарегистрированы в `schemas.py`.
    * **Tool Runner:** Обновлен `System/scripts/tool_runner.py` для диспетчеризации этих инструментов.
    * **Архитектура:** Скрипты перемещены из `scripts/` в `System/scripts/` для соответствия стандартам.

#### **Изменено**
* **Документация:**
    * Обновлен `ORCHESTRATOR.md` (новые поддерживаемые инструменты).
    * Обновлен `SKILLS.md` (секция Управления Продуктом).
    * Обновлен `SKILL_TIERS.md` (новые навыки Tier 2).

---

### **v3.7.1 — Light Mode** (Feature)

#### **Добавлено**
* **Light Mode:** Новый быстрый режим для тривиальных задач (опечатки, UI-правки, простые баги).
    * Пропускает фазы Architecture и Planning (~50% экономия токенов).
    * Workflows: `light-01-start-feature.md`, `light-02-develop-task.md`.
    * Навык: `light-mode` (Tier 2) с протоколом эскалации и проверками безопасности.
    * Обновлены `GEMINI.md`, `AGENTS.md`, `WORKFLOWS.md`, `SKILLS.md`.

---

### **v3.7.0 — Рефакторинг Навыков и Усиление Безопасности** (Оптимизация)

#### **Добавлено**
* **Автоматизация Безопасности:** Добавлен `run_audit.py` в навык `security-audit`. Авто-детект типа проекта (Solidity/Rust/Python/JS) и запуск инструментов (`slither`, `bandit`, `cargo audit`).
* **Чек-листы Высокого Уровня:**
    * `solidity_security.md`: Паттерны DeFi, Flash Loans, Upgradability.
    * `solana_security.md`: Валидация Anchor, PDA, Арифметика.
* **Архитектурные Паттерны:** Добавлены `clean_architecture.md` и `event_driven.md` в ресурсы `architecture-design`.
* **Безопасность LLM:** Добавлены проверки на Prompt Injection, Jailbreaking и утечку системного промпта в `skill-adversarial-security`.

#### **Оптимизировано**
* **Рефакторинг Навыков (O6):**
    * **Выделение Примеров:** Инлайн-шаблоны вынесены в `resources/` (`requirements-analysis`, `testing-best-practices`).
    * **Script-First:** Ручные инструкции заменены на обязательный запуск скриптов.
    * **Саркастичная Персона:** Примеры промптов вынесены в `resources/prompts/sarcastic.md`.
* **Документация:** В `System/Docs/SKILLS.md` закреплены стандарты V2 (Script-First, Example-Separation).

#### **Верифицировано**
* **Глобальная Валидация:** Все 6 навыков прошли `validate_skill.py`.
* **Безопасность:** TIER 0 навыки (`core-principles`) не затронуты.

---

### **v3.6.5 — Стандартизация Конфигурации** (Рефакторинг)

#### **Изменено**
* **Структура Проекта:**
    * Перемещен `.gemini/GEMINI.md` в `./GEMINI.md` (Корень проекта).
    * Переименован `.cursorrules` в `AGENTS.md` (Корень проекта) для ясности.
* **Документация:** Обновлены `README.md`, `README.ru.md` и `docs/ARCHITECTURE.md` для отражения новой структуры конфигурации.

---

### **v3.6.4 — O7 Prep & System Manifesto** (Documentation)

#### **Оптимизировано**
* **Системный Манифест (O11):** Полностью переписан `System/Agents/00_agent_development.md` как единый источник правды для v3.6+.
    * Синхронизирован с O1 (Skill Tiers) и O2 (Orchestrator Patterns).
    * Добавлена секция про **Agentic Mode** и `task_boundary`.
    * Включена роль `10. Security Auditor`.
* **Спецификация O7:** Уточнена оптимизация Session Context Management.
    * Добавлена интеграция с инструментом `task_boundary`.
    * Добавлен "Стартовый Промпт" для реализации O7.
* **README:** Обновлен раздел Установки, добавлено явное упоминание копирования папки `.gemini/`.

---

### **v3.6.3 — O6a: Оптимизация Структуры Навыков** (Оптимизация)

#### **Изменено**
* **Рефакторинг Крупных Навыков:** Трансформированы 4 "тяжелых" навыка (>4KB) с использованием паттерна `scripts/` + `examples/`:
    * `architecture-format-extended`: Шаблоны вынесены в `examples/` (-65% размера).
    * `skill-reverse-engineering`: NL-обход заменен на `scan_structure.py` (-64% размера).
    * `skill-update-memory`: NL-логика git заменена на `suggest_updates.py` (-63% размера).
    * `skill-phase-context`: Удалена избыточная ASCII-графика (-49% размера).

#### **Добавлено**
* **Скрипты Автоматизации:** Добавлена python-автоматизация для детерминированного выполнения навыков.
* **Обновление Инфографики:** Добавлен *Анализ Влияния на Модель* и *Ссылки* в [O6 Optimization Infographic](archives/Infographics/O6_OPTIMIZATION_INFOGRAPHIC.md).

### **v3.6.2 — Skill Creator & Automation** (Feature)

#### **Добавлено**
* **Новый навык: `skill-creator`**: Мета-навык для создания новых навыков, включающий стандарты Anthropic + Project Tiers (верифицированная структура).
    *   **Автоматизация:** Включает `scripts/init_skill.py` для генерации скелета навыка.
    *   **Валидация:** Включает `scripts/validate_skill.py` для проверки гигиены папок и метаданных.

---

---

### **v3.6.1 — O6: Целостность Логики & Документация** (Post-Release Fix)

#### **Оптимизировано**
* **Системный Манифест (O11):** Полностью переписан `System/Agents/00_agent_development.md` как единый источник правды для v3.6+.
    * Синхронизирован с O1 (Skill Tiers) и O2 (Orchestrator Patterns).
    * Добавлена секция про **Agentic Mode** и `task_boundary`.
    * Включена роль `10. Security Auditor`.
* **Спецификация O7:** Уточнена оптимизация Session Context Management.
    * Добавлена интеграция с инструментом `task_boundary`.
    * Добавлен "Стартовый Промпт" для реализации O7.

#### **Исправлено**
* **Целостность Оркестратора:** Восстановлены пропущенные этапы 11-14 (Review/Fix цикл) и секция Workflows в `01_orchestrator.md` для гарантии 100% паритета логики с v3.2.
* **Документация:** Консолидирована запись `CHANGELOG.md` для версии v3.6.0.

#### **Обновлено**
* **Инфографика:** Обновлены [Token Optimization Infographic](archives/Infographics/TOKEN_OPTIMIZATION_INFOGRAPHIC.md) и [O6 Optimization Infographic](archives/Infographics/O6_OPTIMIZATION_INFOGRAPHIC.md) с финальной статистикой (-20% сжатие Оркестратора против -36% изначальной оценки).

---

### **v3.6.0 — O5: Формализация Уровней Навыков & O6: Стандартизация (Оптимизация)** (Стабильность)

#### **Добавлено**
* **O6 Стандарт:** Все 10 промптов агентов (`01`–`10`) используют унифицированную схему с принудительным TIER 0 и структурированным Workflow.
    * Имена файлов стандартизированы (`_prompt.md`).
* **O5 Уровни Навыков:** Новый документ `System/Docs/SKILL_TIERS.md` — авторитетный источник правил загрузки (TIER 0, 1, 2).

#### **Изменено**
* **Метаданные Навыков:** Все 28 навыков теперь имеют свойство `tier: [0|1|2]`.
* **Эффективность Агентов (O6):**
    * `04 Architect`: **-29%** токенов.
    * `06 Planner`: **-33%** токенов.
    * `08 Developer`: **-31%** токенов.
    * `01 Orchestrator`: **-20%** токенов (с учетом восстановления логики).
* **Безопасность (O6):**
    * Ревьюеры (`07`, `09`) и Аудитор (`10`) получили обязательные навыки TIER 0 (+43% размер), что устраняет галлюцинации и повышает надежность.

#### **Верифицировано**
* **VDD Audit:** Все 10 агентов прошли проверку на сохранение логики (Logic Retention) относительно версии v3.2.
* **Локализация:** Все русские промпты синхронизированы.

---


### **v3.5.5 — O2: Сжатие Оркестратора (Оптимизация)** (Token Savings)

#### **Добавлено**
* **Новый навык: `skill-orchestrator-patterns`**: Паттерн Stage Cycle и dispatch table для Оркестратора.
    * Переиспользуемый поток Init → Review → Revision.
    * Таблица диспетчеризации этапов с агентами, ревьюерами и лимитами итераций.
    * Таблицы логики решений для общих ветвлений.
    * Схемы ожидаемых результатов для всех типов агентов.
    * Документация исключений (Завершение, Блокировка).

#### **Изменено**
* **`01_orchestrator.md`**: Сжат с 492 строк до 170 строк с использованием паттернов + dispatch table.
* **`Translations/RU/Agents/01_orchestrator.md`**: Обновлён с той же логикой сжатия.
* **`System/Docs/SKILLS.md`**: Добавлена запись `skill-orchestrator-patterns`.

#### **Результат оптимизации**
| Метрика | До | После | Экономия |
|---------|-----|-------|----------|
| Размер файла | 11,195 байт | 4,522 байт | **-60%** |
| Строки | 492 | 170 | **-65%** |
| Токены (~) | ~2,799 | ~1,130 | **-60%** |

> **Примечание:** Все 14 сценариев сохранены. Бекап: `01_orchestrator_full.md.bak`.
>
> 📊 **См. также:** [Инфографика оптимизации токенов](archives/Infographics/TOKEN_OPTIMIZATION_INFOGRAPHIC.md) для визуального разбора экономии.

---

### **v3.5.4 — O1: Skill Phase Context (Оптимизация)** (Token Savings)

#### **Добавлено**
* **Новый навык: `skill-phase-context`**: Протокол уровней загрузки навыков для оптимизации потребления токенов.
    * **TIER 0** (Всегда загружать): `core-principles`, `skill-safe-commands`, `artifact-management` (~2,082 токена).
    * **TIER 1** (По фазе): Таблица соответствия фаза→навыки для загрузки по требованию.
    * **TIER 2** (Расширенные): Специализированные навыки, загружаемые только по явному запросу.
    * Правила загрузки и диаграмма потока для агентов.

#### **Изменено**
* **`.gemini/GEMINI.md`**: Добавлена явная секция TIER 0 Skills с инструкциями bootstrap-загрузки.
* **`.cursorrules`**: Добавлена явная секция TIER 0 Skills с инструкциями bootstrap-загрузки.
* **`System/Docs/SKILLS.md`**: Добавлена запись `skill-phase-context` в секцию Core & Process.

#### **Результат оптимизации**
| Метрика | До | После | Экономия |
|---------|-----|-------|----------|
| Базовая загрузка сессии | ~9,772 токена | ~2,082 токена | **-79%** |
| TIER 1 навыки | Все сразу | По требованию | -3,000 — -5,000 токенов |

> **Примечание:** Автоматизация (safe-commands) сохранена — `mv`, `git`, тесты выполняются автоматически.

---

### **v3.5.3 — O3: Разделение architecture-format (Оптимизация)** (Token Savings)

#### **Добавлено**
* **Новый навык: `architecture-format-core`**: Минимальный шаблон для архитектурных документов (~150 строк, TIER 1).
    * Базовые секции: Описание задачи, Функциональная архитектура, Системная архитектура, Модель данных (концептуальная), Открытые вопросы.
    * Навык по умолчанию для большинства обновлений архитектуры.
    * Таблица условий загрузки для принятия решений.
* **Новый навык: `architecture-format-extended`**: Полные шаблоны с примерами (~400 строк, TIER 2).
    * Полные секции 3-10 с JSON примерами, диаграммами и детальными шаблонами.
    * Загружается только для: новых систем, крупного рефакторинга, сложных требований.
    * Перекрёстная ссылка на core-навык.

#### **Изменено**
* **`04_architect_prompt.md`**: Обновлён с таблицей условной загрузки для core/extended навыков.
* **`Translations/RU/Agents/04_architect_prompt.md`**: Обновлён с той же логикой условной загрузки.
* **`System/Docs/SKILLS.md`**: Заменена единственная запись `architecture-format` на две записи с указанием уровней.

#### **Экономия токенов**
| Сценарий | До | После | Экономия |
|----------|-----|-------|----------|
| Минорное обновление архитектуры | ~2,535 | ~996 | **-60%** |
| Новая система / крупный рефакторинг | ~2,535 | ~3,357 | +32% (больше примеров) |

---

### **v3.5.2 — Консолидация скриптов и упрощение установки** (Рефакторинг)

#### **Изменено**
* **Перемещён `scripts/` → `System/scripts/`**: Диспатчер инструментов теперь часть папки System.
    * **Установка упрощена**: Только 2 папки для копирования (`System/` + `.agent/`) вместо 3.
    * **Чёткое разделение**: Файлы фреймворка (`System/`) vs файлы проекта.

#### **Обновлено**
* **README.md / README.ru.md**: Упрощены инструкции установки и диаграммы структуры.
* **System/Docs/ORCHESTRATOR.md**: Все пути импорта обновлены до `System.scripts.tool_runner`.
* **tests/test_tool_runner.py**: Обновлён путь импорта.

---

### **v3.5.1 — Исправление конфликтов протоколов и IDE-агностичные фиксы** (Framework Bugfix)

#### **Исправлено**
* **`skill-archive-task`**: Удалена жёсткая зависимость от инструмента `generate_task_archive_filename`. Добавлен ручной fallback для генерации имени файла.
* **`skill-archive-task`**: Заменены хардкод-примеры ID (`032`, `033`) на универсальные плейсхолдеры (`{OLD_ID}`, `{NEW_ID}`).
* **`artifact-management`**: Удалён хардкод абсолютного пути. Исправлена устаревшая ссылка на инструмент.
* **`artifact-management`**: Добавлена секция "Dual State Tracking" для разрешения конфликта между внутренним `task.md` Agentic Mode и проектным `docs/TASK.md`.
* **`core-principles`**: Добавлен IDE-агностичный "Bootstrap Protocol" (Секция 0), объясняющий агентам, что `<user_rules>`, инжектируемые IDE, **переопределяют** внутренние настройки.

#### **Устранённые первопричины**
| Проблема | Решение |
|----------|---------|
| Контекстная слепота | Bootstrap Protocol разъясняет приоритеты |
| Внутренний vs проектный `task.md` | Добавлена секция Dual State Tracking |
| Блокировка из-за инструмента | Ручной fallback в skill-archive-task |
| Хардкод в примерах | Заменены на `{PLACEHOLDER}` |

---

### **v3.5.0 — Автоматизация памяти** (Task 035)


#### **Добавлено**
* **Новый навык: `skill-update-memory`**: Автообновление `.AGENTS.md` на основе изменений кода.
    * Анализирует `git diff --staged` для обнаружения новых, изменённых и удалённых файлов.
    * Строгая фильтрация: игнорирует `*.lock`, `dist/`, `migrations/`, конфиги.
    * Сохранение человеческих знаний: защищает секции `[Human Knowledge]`.
    * Точки интеграции: `09_agent_code_reviewer`, `04-update-docs`.
* **Новый навык: `skill-reverse-engineering`**: Восстановление архитектурной документации из кода.
    * Итеративная стратегия: анализ папка-за-папкой → локальные summaries → глобальный синтез.
    * Обновляет `ARCHITECTURE.md` и выявляет скрытые знания для `KNOWN_ISSUES.md`.
    * Защита от overflow контекста: никогда не загружает весь код сразу.

#### **Документация**
* Обновлён `System/Docs/SKILLS.md` с новыми навыками в секции Core & Process.
* Обновлена дорожная карта в `Backlog/potential_improvements-2.md`.

#### **Интеграция**
* `09_agent_code_reviewer.md`: Добавлен `skill-update-memory` для проверки обновления `.AGENTS.md`.
* Workflow `04-update-docs.md`: Добавлены ссылки на оба навыка.
* `README.md` / `README.ru.md`: Обновлён раздел "Reverse Engineering" с промптами на основе навыков.

---

### **v3.4.1 — Целостность сценариев и фиксы артефактов** (Task 034 Phase 2)

#### **Исправлено**
* **"Фантомные" ссылки в сценариях**: Исправлены критические ссылки в `base-stub-first.md` (и, как следствие, в `vdd-enhanced`), которые вели на несуществующие сценарии (`/analyst-task` и др.). Это восстановило обязательные фазы Анализа и Архитектуры.
* **Цикл VDD Adversarial**: В `vdd-adversarial.md` исправлены вызовы на валидные сценарии (`/03-develop-single-task`) вместо несуществующих действий.
* **Целостность Артефактов**: Добавлен отсутствующий файл `docs/KNOWN_ISSUES.md`, необходимый для корректной работы сценариев.
* **Аудит Безопасности**: В `security-audit.md` уточнена инструкция по обновлению `.AGENTS.md` (теперь корректно отрабатывает отсутствие файлов).

#### **Верифицировано**
* Проведен полный аудит всех 14 файлов сценариев на предмет корректности перекрестных ссылок.

### **v3.4.0 — VDD Multi-Adversarial** (Task 034)

#### **Добавлено**
* **Новый навык: `skill-adversarial-security`**: OWASP-критик в саркастичном стиле.
    * Атаки инъекций (SQLi, XSS, Command Injection, Path Traversal).
    * Уязвимости аутентификации и авторизации.
    * Утечка секретов (хардкод ключей, паролей, токенов).
    * Ошибки валидации ввода.
* **Новый навык: `skill-adversarial-performance`**: Критик производительности в саркастичном стиле.
    * N+1 запросы, отсутствие индексов.
    * Утечки памяти, unbounded аллокации.
    * Блокирующие операции в async коде.
    * Проблемы сложности алгоритмов.
* **Новый workflow: `/vdd-multi`**: Последовательный запуск нескольких adversarial критиков.
    * Фаза 1: Ревью логики (`skill-vdd-adversarial`).
    * Фаза 2: Ревью безопасности (`skill-adversarial-security`).
    * Фаза 3: Ревью производительности (`skill-adversarial-performance`).

#### **Документация**
* Обновлён `docs/SKILLS.md` с новыми VDD скиллами.
* Обновлён `Backlog/potential_improvements-2.md` статусы v3.4.

---

### **v3.3.2 — Авто-тесты для Протокола Архивации** (Task 033 Phase 2)

#### **Добавлено**
* **Тесты протокола архивации**: 15 новых автоматизированных тестов для 8 сценариев архивации с VDD adversarial подходом:
    * Основные сценарии: новая задача с существующим TASK.md, без TASK.md, уточнение, конфликт ID.
    * VDD adversarial: отсутствие Meta Information, некорректный Task ID, ошибка прав доступа, ошибка инструмента.
* **Тестируемый модуль протокола**: `archive_protocol.py` — Python реализация 6-шагового протокола для unit-тестирования.
* **Test Fixtures**: 3 варианта TASK.md (`task_with_meta.md`, `task_without_meta.md`, `task_malformed_id.md`).

#### **Верификация**
* 44 теста проходят (29 существующих + 15 новых).
* Запуск: `cd .agent/tools && python -m pytest test_archive_protocol.py -v`

---

### **v3.3.1 — Портативность, VDD Аудит и UX** (Task 033)

#### **Исправлено**
* **Круговая зависимость в Safe Commands**: Устранена петля в документации. Добавлен явный список команд в `skill-safe-commands` для быстрой настройки IDE.
* **Галлюцинации Агентов**: Исправлены ссылки на несуществующие инструменты в `01_orchestrator.md` (`git_ops` -> `git_status`), выявленные в ходе VDD Аудита.
* **Конфигурация IDE**: Исправлена документация для "Allow List" (решена проблема токенизации команды `mv`).
* **Портативность**: Ссылка на `docs/ORCHESTRATOR.md` сделана опциональной (`if available`), чтобы агенты работали корректно при переносе.

#### **Рефакторинг**
* **Mandatory Skill Pattern**: Принудительное использование `skill-safe-commands` всеми агентами.
* **Гайдлайны Разработчика**: Явный "Tooling Protocol", требующий использования нативных инструментов (`run_tests`) вместо shell.

### **v3.3.0 — Инкапсуляция Skills и Централизация Safe Commands** (Task 033)

#### **Добавлено**
* **Новый навык: `skill-archive-task`**: Полный, самодостаточный протокол архивации `docs/TASK.md`. Единый источник истины для логики архивации, устраняет дублирование в 7+ файлах.
    * 6-шаговый протокол архивации с логикой принятия решений (новая задача vs уточнение).
    * Обработка ошибок при отсутствии Meta Information.
    * Руководство по валидации и откату.
* **Новый навык: `skill-safe-commands`**: Централизованный список команд для автоматического выполнения без подтверждения пользователя.
    * 7 категорий команд: только чтение, информация о файлах, git чтение, архивация, директории, инструменты, тестирование.
    * Правила pattern matching для интеграции с IDE.
    * Инструкции для IDE (Antigravity/Gemini, Cursor).

#### **Рефакторинг**
* **Устранено дублирование**: Сокращён протокол архивации с 7 файлов до 1:
    * `.gemini/GEMINI.md` → ссылка на skill
    * `.cursorrules` → ссылка на skill
    * `System/Agents/02_analyst_prompt.md` → ссылка на skill
    * `System/Agents/01_orchestrator.md` → ссылка на skill
    * `System/Agents/00_agent_development.md` → ссылка на skill (30 строк → 14)
    * `.agent/skills/artifact-management/SKILL.md` → импорт из skill
    * `.agent/workflows/01-start-feature.md` → ссылка на skill
* **Safe Commands централизованы**: Все 4 файла с дублированными Safe Commands теперь ссылаются на `skill-safe-commands`.

#### **Документация**
* Обновлён `docs/SKILLS.md` с новыми навыками.
* Добавлено Implementation Summary в `docs/TASK.md` (Task 033).

---

### **v3.2.5, v3.2.6 — Инструмент генерации ID задач и Протокол Auto-Run**

#### **Добавлено**
* **Новый инструмент: `generate_task_archive_filename`**: Детерминированный инструмент для генерации уникальных последовательных ID при архивации задач. Устраняет ошибки ручного назначения ID и пробелы в нумерации.
    * Автоматически генерирует следующий доступный ID (стратегия `max + 1`).
    * Проверяет предложенные ID и обрабатывает конфликты (флаг `allow_correction`).
    * Нормализует slug (нижний регистр, дефисы).
    * Поддержка ID > 999 (регулярка `\d{3,}`).
* **Интеграция с Dispatcher**: Инструмент зарегистрирован в `scripts/tool_runner.py`.
* **Unit-тесты**: 29 тестов, покрывающих все сценарии использования.

#### **Улучшено**
* **Протокол Safe Commands**: Расширен список команд для автозапуска в `skill-artifact-management` и промпте Orchestrator:
    * Только чтение: `ls`, `cat`, `head`, `tail`, `find`, `grep`, `tree`, `wc`
    * Git чтение: `git status`, `git log`, `git diff`, `git show`, `git branch`
    * Архивация: `mv docs/TASK.md docs/tasks/...`
    * Инструменты: `generate_task_archive_filename`, `list_directory`, `read_file`
* **Промпты агентов**: Обновлены Orchestrator (`01`) и Analyst (`02`) с явными инструкциями использования инструмента.

#### **Документация**
* Обновлены `docs/ARCHITECTURE.md`, `docs/ORCHESTRATOR.md`, `docs/SKILLS.md`.
* Добавлены требования к установке Python в README.
* Консолидирован `docs/USER_TOOLS_GUIDE.md` в `docs/ORCHESTRATOR.md` (удален дубликат).
* Синхронизированы `.gemini/GEMINI.md` и `.cursorrules` с протоколом v3.2.5+.

---

### **v3.2.4 — Улучшение Документации Сценариев**

#### **Добавлено**
* **Последовательности вызовов Workflow**: Добавлен раздел "Getting Started" в `docs/WORKFLOWS.md`:
    * Сравнительная таблица подходов One-Step vs Multi-Step.
    * Примеры TDD пайплайна (`base-stub-first`, `01`→`02`→`03/05`→`04`) с плюсами и минусами.
    * Примеры VDD пайплайна (`vdd-enhanced`, `full-robust`, атомарные VDD шаги) с плюсами и минусами.
    * Диаграмма принятия решений (Mermaid) для выбора подхода.
    * Сводная таблица рекомендаций для типичных сценариев.

---

### **v3.2.3 — Уточнение Протокола Архивации**

#### **Изменено**
* **Область архивации**: Удалена обязательная архивация `docs/PLAN.md`. Только `docs/TASK.md` требует архивации перед новыми задачами.
* **Документация**: Обновлены ссылки на версии в `README.md` (v3.1→v3.2) и `docs/ORCHESTRATOR.md` (v3.1.2→v3.2.2).

#### **Улучшено**
* **Протокол Auto-Run**: Добавлена явная инструкция `SAFE TO AUTO-RUN` в промпт Аналитика и `skill-artifact-management`. Команда архивации `docs/TASK.md` больше не требует одобрения пользователя.

---

### **v3.2.2 — Целостность системы и Протоколы архивации**

#### **Исправлено**
* **Критическое восстановление**: Восстановлены отсутствующие (пустые) промпты русских агентов (`Translations/RU/Agents/01, 02, 04, 06`) с логикой v3.2.0.
* **Предотвращение потери данных**: Исправлен критический пробел в `skill-artifact-management`, где отсутствовал "Протокол Архивации".
* **Принудительные протоколы**: Обновлены Оркестратор (`01`), Аналитик (`02`) и Планировщик (`06`) для строгого требования архивации `docs/TASK.md` и `docs/PLAN.md` перед перезаписью.

#### **Улучшено**
* **Системные промпты**: Синхронизированы `.gemini/GEMINI.md` и `.cursorrules` с Протоколом Выполнения Инструментов (v3.2.0), явно разрешающим нативный вызов инструментов.
* **Согласованность**: Проведен полный аудит системы промптов для исключения противоречий.

---

### **v3.2.1 — Оптимизация Системы Навыков**

#### **Добавлено**
* **Навыки**:
    * `skill-task-model`: Стандартизированные примеры и правила для `docs/TASK.md`.
    * `skill-planning-format`: Шаблоны для `docs/PLAN.md` и описаний задач.
* **Правила**: Добавлен файл `.agent/rules/localization-sync.md` для автоматического контроля синхронизации документации.

#### **Улучшено**
* **Промпт-инжиниринг**: Значительно уменьшен размер агентов-Аналитика (`02`), Архитектора (`04`) и Планировщика (`06`) за счет выноса статических шаблонов в Систему Навыков.
* **Локализация**: `README.ru.md` синхронизирован с английской версией (добавлен раздел Инструментов).
* **Русские Агенты**: Обновлены `Translations/RU/Agents/*.md` до стандартов v3.2.0 (логика Инструментов, Навыки, относительные пути).

---

### **v3.2.0 — Структурированные инструменты и Гигиена путей**

#### **Добавлено**
* **Подсистема выполнения инструментов**: Оркестратор теперь нативно поддерживает структурированный вызов инструментов.
* **Новые навыки**:
    * `skill-task-model`: Стандартизированные примеры и правила для `docs/TASK.md`.
    * `skill-planning-format`: Шаблоны для `docs/PLAN.md` и описаний задач.
    * `skill-architecture-format`: Консолидированные шаблоны архитектурной документации.
* **Стандартные инструменты**: Добавлены `run_tests`, `git_ops`, `file_ops`.
* **Документация**: Добавлены `docs/ORCHESTRATOR.md`.

#### **Улучшено**
* **Промпт-инжиниринг**: Значительно уменьшен размер агентов-Аналитика (`02`), Архитектора (`04`) и Планировщика (`06`) за счет выноса статических шаблонов в Систему Навыков.
* **Поддержка**: Критические шаблоны документов централизованы в `.agent/skills/`.

#### **Изменено**
* **Протоколы тестирования**: Стандартизировано место хранения отчетов (`tests/tests-{Task ID}/`).
* **Гигиена путей**: В промптах агентов теперь используются строго относительные пути проекта.
* **Агенты**: Обновлены промпты Оркестратора, Разработчика и Ревьюеров.

#### **Исправлено**
* **Очистка**: Удалена устаревшая директория `docs/test_reports`.

---

### **v3.1.3 — Очистка Skills и исправление интеграции Cursor**

#### **Изменено**
* **Структура проекта**: Удалена дублирующая директория `.cursor/skills`.
* **Интеграция с Cursor**: В `README.md` и `README.ru.md` добавлена инструкция по созданию симлинка `.cursor/skills` -> `.agent/skills`, что гарантирует единый источник правды.
* **Оркестратор**: Обновлен `.cursorrules`, исправлены пути к навыкам и легаси-терминология "tz".
* **Документация**: В `docs/ARCHITECTURE.md` отражена связь через симлинк.

---

### **v3.1.2 — Протокол Аналитика и Fix YAML**

#### **Исправлено**
* **Навыки**: Исправлена синтаксическая ошибка YAML в навыке `core-principles` (добавлены кавычки в описание).

#### **Улучшено**
* **Агент-Аналитик**: Добавлен "CRITICAL PRE-FLIGHT CHECKLIST" в `02_analyst_prompt.md`, строго требующий:
    * Архивирования существующего `docs/TASK.md` перед началом работы.
    * Обязательного включения Секции 0 (Meta Information: Task ID, Slug).
* **Навыки**: Обновлен `skill-requirements-analysis`, помечающий Meta Information как **ОБЯЗАТЕЛЬНУЮ**.
* **Документация**: Внедрено правило "Только относительные пути" (Relative Paths Only) для Артефактов в `skill-documentation-standards` и `06_agent_planner.md`.

#### **Рефакторинг**
* **Навыки**: Проведен аудит и исправление YAML-заголовков в `code-review-checklist`, `developer-guidelines`, `security-audit` и `artifact-management`.
* **PLAN.md**: Абсолютные пути заменены на относительные.

---

### **v3.1.1 — Исправление путей Плана и Структуры**

#### **Исправлено**
* **Промпты Агентов**: Исправлены ссылки на файл плана (`plan.md` -> `docs/PLAN.md`) в промптах Planner и Reviewer (в английской и русской версиях).
* **Промпты Агентов**: Исправлены ссылки на файл вопросов (`open_questions.md` -> `docs/open_questions.md`) в промпте Planner.
* **Структура Проекта**: Удалена папка `verification/` для соответствия `docs/ARCHITECTURE.md`.

---

### **v3.1.0 — Глобальный Рефакторинг "ТЗ" в "TASK"**

#### **Изменено**
* **Терминология**: Глобальный рефакторинг "ТЗ" (Техническое Задание) в "TASK" (Task/Specification) для улучшения интернационализации и согласованности.
* **Артефакты**: Переименован `docs/TZ.md` в `docs/TASK.md`.
* **Системные Агенты**: Обновлены все промпты агентов (Analyst, Reviewer, Architect и др.) для использования терминологии "TASK".
* **Навыки**: Переименован `skill-tz-review-checklist` в `skill-task-review-checklist`.
* **Документация**: Обновлены `README.ru.md`, `WORKFLOWS.md`, `SKILLS.md` и `.gemini/GEMINI.md` для соответствия новому стандарту.

#### **Исправлено**
* **Согласованность**: Устранено смешанное использование "ТЗ" и "Task Specification" во всем фреймворке.
* **Сценарии (Workflows)**: Исправлена критическая ошибка в `01-start-feature` и `vdd-01-start-feature`, из-за которой старое ТЗ перезаписывалось без архивации. Добавлен явный шаг архивирования.

#### **Инструкция по миграции**
Для обновления с v3.0.x до v3.1.0:
1. **Переименование**: `mv docs/TZ.md docs/TASK.md`
2. **Обновление Агентов**: Замените `System/Agents/` на новую версию (Важно: `03_tz_reviewer_prompt.md` -> `03_task_reviewer_prompt.md`).
3. **Обновление Навыков**: Замените `.agent/skills/` на новую версию.

---

### **v3.0.3 — Синхронизация документации и артефакты**

#### **Исправлено**
* **Документация**: Заменены устаревшие ссылки на `UNKNOWN.md` на `docs/open_questions.md` в `README.md` и `README.ru.md` для соответствия реальным промптам Агентов.

#### **Добавлено**
* **Артефакты**: Добавлен отсутствующий шаблон `docs/open_questions.md` для отслеживания нерешенных вопросов.

---

### **v3.0.2 — Примеры и Доработка Документации**
  
#### **Добавлено**
* **Примеры (Examples)**:
    * `examples/skill-testing/test_skill.py`: Python скрипт для изолированного тестирования навыков.
    * `examples/skill-testing/n8n_skill_eval_workflow.json`: n8n workflow с подсказками (Sticky Notes) для проверки промптов.
* **Документация (Skills)**:
    * В `docs/SKILLS.md` добавлены разделы "Dynamc Loading", "Isolated Testing" и "Best Practices".
    * Добавлены прямые ссылки на файлы примеров.

---

### **v3.0.1 — Улучшение Системы Навыков**

#### **Улучшено**
* **Документация Навыков**:
    * Расширен `docs/SKILLS.md`: добавлено "Как это работает", принципы и ссылки на официальную документацию.
    * Добавлены матрицы "Используется в сценариях" и "Используется агентами".
    * Уточнено понятие **Adversarial Agent** как "Virtual Persona" (Виртуальная Персона) в режиме VDD.
* **README**:
    * Восстановлены пропущенные разделы "Команда Агентов" и "Системный Промпт".
    * Исправлены инструкции по установке Системы Навыков.

---

### **v3.0.0 — Система Навыков и Глобальная Локализация**

#### **Ключевые изменения**
* **Система Навыков**: Внедрена модульная библиотека `.agent/skills/`. Агенты теперь динамически загружают "навыки" вместо использования монолитных промптов.
* **Архитектура Локализации**: Новая структура директории `Translations/`. Полная поддержка переключения между Английским и Русским контекстами.
* **Документация**:
    * Добавлен `docs/SKILLS.md`: Полный каталог доступных навыков.
    * Обновлены `README.md`, `README.ru.md`, `docs/ARCHITECTURE.md`.

#### **Удалено**
* **Legacy**: Удалена директория `/System/Agents_ru` (заменена на `Translations/RU`).

---

### **v2.1.3 — Документация и согласованность сценариев**

#### **Исправлено**
* **ARCHITECTURE.md**: Обновлен для соответствия реальной структуре проекта (добавлены папки `.agent` и `docs`).
* **Workflows**: `full-robust.md` теперь явно вызывает `/security-audit` (Агент 10) вместо заглушки.

### **v2.1.2 — Исправление генерации .AGENTS.md**

#### **Исправлено**
* **Конфликт промптов**: Устранен конфликт, из-за которого Developer пропускал создание `.AGENTS.md`, так как Planner не ставил это в задачу, а правило "без лишних файлов" запрещало самодеятельность.
* **Planner Agent**: Теперь явно требует создания `.AGENTS.md` для новых папок.
* **Developer Agent**: Получил явное разрешение (исключение) на создание `.AGENTS.md`, даже если этого нет в task-файле.

### **v2.1.1 — Верификация процессов и безопасность**

#### **Добавлено**
* **Обязательная верификация**: Все основные сценарии (Standard и VDD) теперь включают явные циклы проверки (Analyst -> TZ Review и т.д.).
* **Лимиты безопасности**: Внедрен механизм **Max 2 Retries** для предотвращения бесконечных циклов "Исполнитель-Ревьюер".

---

### **v2.1.0 — Вложенные сценарии (Nested Workflows) и аудит безопасности (Security Audit)**

#### **Добавлено**
* **Поддержка вложенных сценариев**: Возможность вызывать одни workflows из других (например, `Call /base-stub-first`).
* **Новые сценарии**:
  * `/base-stub-first`: Базовый пайплайн Stub-First.
  * `/vdd-adversarial`: Изолированный цикл адверсариальной проверки.
  * `/vdd-enhanced`: Комбинация Stub-First + VDD.
  * `/full-robust`: Полный пайплайн с будущим аудитом безопасности.
  * `/security-audit`: Standalone security vulnerability assessment workflow.
* **Документация**: Обновлены `WORKFLOWS.md`, `README.md` и `GEMINI.md`.

---

### **v2.0.0 — Публичный релиз: Система мультиагентной разработки**

#### **Основные возможности**

* **Экосистема из 9 агентов**: Полная оркестрация **9 специализированных ролей** (Analyst, Architect, Planner, Developer, Reviewer, Orchestrator и др.), обеспечивающая контроль на всех этапах SDLC.
* **VDD (Verification-Driven Development)**: Состязательное тестирование с помощью агента **Sarcasmotron** для проверки логики и минимизации ошибок.
* **Методология Stub-First**: Методика, при которой тесты и заглушки создаются до реализации основной логики.
* **Управление контекстом**: Система артефактов и `.AGENTS.md` для поддержания "длинной памяти" проекта.
* **Поддержка IDE**: Нативная интеграция с **Antigravity** и **Cursor**.

#### **🚀 Быстрый старт**

1. **Скопируйте агентов**: Переместите папку `/System/Agents` в корень вашего проекта.
2. **Настройте IDE**: Скопируйте `.gemini/GEMINI.md` (для Antigravity) или `.cursorrules` (для Cursor) в корень вашего проекта, чтобы активировать инструкции агентов.
3. **Инициализация**: Используйте промпт `02_analyst_prompt.md`, чтобы начать сессию.
4. **Следуйте инструкциям**: Ознакомьтесь с **Pre-flight Check** в README для полного понимания рабочего процесса.
