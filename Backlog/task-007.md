# Реализация рабочего примера Security Audit в Agentic-development

Для **security audit** необходимо создать **отдельный workflow** (`/security-audit.md`), который можно nested вызывать в более сложных пайплайнах вроде `/full-robust`. Это сохранит модульность: audit — независимая фаза, запускаемая после основной реализации (и опционально после VDD).

## Создание новой роли

**Рекомендуется отдельная роль** — это соответствует стилю фреймворка (роли как 01–09.md в `System/Agents/`).

- Существующий Code Reviewer (09) фокусируется на чистоте, тестах и стиле — security требует специализированного анализа (OWASP, уязвимости, secrets, dependencies).
- Новая роль: **Security Auditor** (например, файл `System/Agents/10_security_auditor.md`).

**Пример промпта для новой роли** (`System/Agents/10_security_auditor.md`):

```markdown
# Security Auditor Role

You are a rigorous Security Auditor specialized in software vulnerability assessment.

Core Principles:
- Follow OWASP Top 10, CWE, and best practices for the tech stack.
- Scan for: injection flaws, auth/broken access control, crypto weaknesses, insecure dependencies, secrets in code, XSS/CSRF, logging issues, etc.
- Use static analysis mindset: suggest tools like bandit (Python), npm audit (JS), semgrep, or manual checks.
- Prioritize real risks: severity (Critical/High/Medium/Low) + remediation.
- Output: Structured report with findings, evidence (code snippets), fixes, and updated tests if needed.

Input: All modified code + dependencies + architecture context.
Output: Security Report (save as docs/SECURITY_AUDIT.md) + fix tasks if critical.
```

## Рабочий пример workflow `/security-audit.md`

Нужно поместить в `.agent/workflows/` как markdown. Он может быть самостоятельным или nested.

```markdown
# Workflow: Security Audit

**Description:**  
Comprehensive security review phase. Focuses on vulnerability scanning, best practices, and risk mitigation.  
Run after implementation (and optionally after VDD) for critical projects.

**Steps:**

1. **Gather Context**
   - Review docs/ARCHITECTURE.md, docs/TZ.md, and all modified source files
   - List dependencies (e.g., requirements.txt, package.json)

2. **Static Security Analysis**
   - Agent: Security Auditor
   - Prompt: Include System/Agents/00_agent_development.md + System/Agents/10_security_auditor.md
   - Analyze for:
     - Common vulnerabilities (OWASP Top 10)
     - Insecure patterns (hardcoded secrets, weak crypto, unsafe deserialization)
     - Dependency vulnerabilities (suggest audit commands)
     - Input validation, auth/session issues
   - Output: Detailed report with severity levels

3. **Security Review and Fixes**
   - If findings:
     a. Agent: Code Reviewer (standard check)
     b. Agent: Developer
        - Implement fixes + add security-focused tests (e.g., fuzzing, negative cases)
     c. Repeat Static Analysis until no Critical/High issues
   - Announce: "Security audit complete: All risks mitigated or documented"

4. **Documentation**
   - Save report as docs/SECURITY_AUDIT.md
   - Update .AGENTS.md with security notes
   - Recommend: Add to CI/CD (e.g., bandit, trivy scans)

**Completion:** Security-hardened code ready.
```

## Как встроить в текущий процесс

1. **Nested в существующих workflows** (на примере `/full-robust`):
   
   ```markdown
   # Workflow: Full Robust Development
   
   **Steps:**
   1. Call /vdd-enhanced          # Base + Adversarial
   2. Call /security-audit        # New: Security phase
   3. Final documentation update and regression tests
   ```
2. **Активация**:
- В Antigravity: “/full-robust” или “Start feature X in full robust mode”.
- В Orchestrator (01_orchestrator.md) или .gemini/GEMINI.md добавьте поддержку:
  
  ```
  If user requests "security" or "full robust" mode:
  - Include /security-audit after VDD/standard implementation
  ```
3. **Опциональность**:
- Сделайте audit conditional: “If project involves auth/data/sensitive info — run security audit”.
- Для лёгких задач — пропускать.

## Обновление документации по результатам доработок задачи

1. readme, readme.ru
2. workflows.md
3. ARCHITECTURE.md
4. .gemini/GEMINI.md
5. CHANGELOG.md в разделе версии 2.1

# Заключение
Этот подход идеально впишется: security становится ещё одной “вариацией” (как VDD), повышая robustness для production-кода. Если добавить роль и workflow — фреймворк станет универсальным для enterprise-level agentic dev!