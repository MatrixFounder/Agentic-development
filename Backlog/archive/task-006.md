# Создание nested workflows

Nested workflows полностью поддерживаются в Google Antigravity (подтверждено официальной документацией: "You can call other Workflows from within a workflow! For example, /workflow-1 can include instructions like “Call /workflow-2” and “Call /workflow-3”").

Их необходимо добавить для большей масштабируемости: это позволит комбинировать вариации (base + VDD + future Security), избегать дублирования шагов и делать систему более composable. Поскольку фреймворк интегрирован с Antigravity (через .gemini/GEMINI.md), nested calls будут работать нативно, если workflows созданы/подхвачены в UI или правильно размещены в .agent/.

## Рабочие примеры nested workflows

Эти примеры нужно адаптировать под стиль репозитория (markdown в .agent/workflows). Их стоит добавить как отдельные файлы. Nesting реализуется через шаг "Call /other-workflow-name" (Antigravity выполнит его автоматически).

### 1. /base-stub-first.md (базовый, без nesting — для основания)

```Markdown
# Workflow: Base Stub-First Development

**Description:**  
Core pipeline with Stub-First and TDD. Used as foundation for others.

**Steps:**

1. Call /analyst-tz               # Technical Specification
2. Call /tz-review
3. Call /architect-design
4. Call /architecture-review
5. Call /planner-stub-first      # Enforce Stub → Impl pairs
6. Call /plan-review
7. For each task pair:
   - Call /developer-stub
   - Call /code-review-stub
   - Call /developer-impl
   - Call /code-review-final
8. Final validation and commit preparation
```

### 2. /vdd-adversarial.md (адверсариальная часть — для nesting)
```Markdown
# Workflow: VDD Adversarial Refinement

**Description:**  
Post-implementation adversarial cycle for zero-slop robustness.

**Steps:**

1. For each implemented module:
   a. Activate Adversary (Sarcasmotron)
      - Prompt: [Full Sarcasmotron prompt with cynicism, fresh context, hallucination termination]
      - Review all code + tests
   b. If real issues found:
      - Call /developer-fix + add tests
      - Call /code-review-final
      - Repeat this workflow (recursive call if needed)
   c. Terminate when adversary hallucinations dominate
2. Announce: "VDD cycle complete: zero-slop achieved"
```

### 3. /vdd-enhanced.md (nested: base + VDD)
```Markdown
# Workflow: VDD-Enhanced Development

**Description:**  
Full robust mode: Standard Stub-First + adversarial refinement.

**Steps:**

1. Call /base-stub-first          # Run core pipeline first
2. After completion:
   Call /vdd-adversarial          # Add adversarial roast on top
3. Final regression tests and commit
```

### 4. /full-robust.md (пример сложного nesting с будущей вариацией)

```Markdown
# Workflow: Full Robust Development

**Description:**  
Maximum reliability: Base + VDD + (future) Security audit.

**Steps:**

1. Call /vdd-enhanced              # Already nested: base + adversarial
2. (Optional future) Call /security-audit
3. Final documentation update
```

## Что нужно сделать?

1. Добавить файлы в .agent/workflows.
2. В .gemini/GEMINI.md добавить: "Available workflows: /base-stub-first, /vdd-enhanced etc. Use Call /workflow-name in steps."
3. Запуск: В Antigravity — "/vdd-enhanced" или "Start feature X in VDD mode" (оркестратор направит).
4. Обновить readme, workflows.md 

Это сделает фреймворк ещё мощнее — nested позволит бесконечно комбинировать вариации без дублирования. 