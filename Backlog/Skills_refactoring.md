# Skills Refactoring Backlog

> **Status:** Draft
> **Created:** 2026-01-23
> **Purpose:** Align all skills with the `skill-creator` V2 standard (Script-First, Example-Separation) and expand capabilities.

---

## Executive Summary

Based on the analysis of `.agent/skills` and `Backlog/agentic_development_optimisations.md` (O6/O6a), several skills require refactoring to reduce token overhead, improve maintainability, and support new languages (Rust, Solidity).

**Core Principles for Refactoring:**
1.  **Script-First:** Replace complex natural language logic with Python scripts in `scripts/`.
2.  **Example-Separation:** Move inline code blocks and lengthy examples to `examples/`.
3.  **Resource-Extraction:** Move templates, checklists, and static assets to `resources/`.

---

## Refactoring Tasks

### 1. Refactor `developer-guidelines` (High Priority)
**Goal:** Expand language support and declutter core guidelines.

- [ ] **Decompose Structure:**
    - `SKILL.md`: Keep only universal principles (Strict Adherence, Input Handling, Anti-Loop).
    - Create `resources/languages/` directory.
- [ ] **Add Language Specifics:**
    - Create `resources/languages/rust.md`: Rust-specific guidelines (borrow checker, unwrap safety, clippy).
    - Create `resources/languages/solidity.md`: Smart contract security, gas optimization, checks-effects-interactions.
    - Create `resources/languages/python.md`: Type hinting, docstrings, testing.
    - Create `resources/languages/javascript.md`: Async/await, ecosystem standards.
- [ ] **Update `SKILL.md`:** Add dynamic loading instruction or reference to look up language guides based on current task.

### 2. Refactor `testing-best-practices` (Medium Priority)
**Goal:** Provide concrete, runnable examples and standard boilerplate.

- [ ] **Extract Examples:**
    - Move inline naming/structure examples to `examples/`.
    - Create `examples/pytest_structure.py`.
    - Create `examples/jest_structure.js`.
- [ ] **Create Templates:**
    - `resources/templates/test_boilerplate.py`.
- [ ] **Update `SKILL.md`:** Reference the new examples.

### 3. Refactor `security-audit` (Medium Priority)
**Goal:** Automate tooling and standardize checklists.

- [ ] **Scripting:**
    - Create `scripts/run_audit.py`: A wrapper script to detect language and run appropriate tools (`bandit`, `npm audit`, `semgrep`).
- [ ] **Resources:**
    - Create `resources/checklists/owasp_top_10.md`: Detailed breakdown for reference.
    - Create `resources/checklists/solidity_security.md`: Reentrancy, overflow, access control.
- [ ] **Update `SKILL.md`:** Instruct agent to run `scripts/run_audit.py` instead of generic "use tools".

### 4. Refactor `requirements-analysis` (Low Priority)
**Goal:** Streamline the prompt by removing the large TASK definition.

- [ ] **Extract Template:**
    - Move the "Technical Specification (TASK) Structure" section to `resources/templates/task_template.md`.
- [ ] **Update `SKILL.md`:**
    - Replace the inline template with a reference: "You MUST follow the structure defined in `resources/templates/task_template.md`."

### 5. Review `architecture-design` (Low Priority)
- [ ] **Analysis:** Check for inline patterns or diagrams that can be moved to `resources/patterns/`.

### 6. Refactor `skill-adversarial-security` (Medium Priority)
**Goal:** Enhance security checks and separate sarcasm resources.

- [ ] **Add Prompt Injection Checks:**
    - Update `SKILL.md` (or extracted resources) to include checks for:
        - Indirect Prompt Injection (data exfiltration via LLM).
        - Jailbreaking attempts detection.
        - System prompt leakage.
- [ ] **Decomposition (Optional but Recommended):**
    - Move sarcastic prompts to `resources/prompts/sarcastic.md` to reduce token load on the main skill.
    - Extract checklist to `resources/checklists/owasp_top_10.md` (shared with security-audit).

---

## Validation Protocol

For each refactored skill, run the validation script:
```bash
python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/<skill-name>
```

### 🛡️ Integrity & Regression Verification

> **Objective:** Ensure ZERO information loss and NO performance degradation.

| Check | Target | Method |
|-------|--------|--------|
| **Content Integrity** | Refactored Skills | `diff` comparison of semantic content (Core + Extended = Original) |
| **Logic Retention** | Agent Prompts | Verification that all 14 scenarios/logic branches remain executable |
| **Performance** | Token Usage | A/B Testing: New vs Old must show ≤ tokens for same task |
| **Safety** | TIER 0 Skills | Verify `core-principles` & `safe-commands` are NEVER dropped |

**Constraint:**
If **ANY** logic is lost or token usage increases (without justification), the optimization is **REJECTED**.

## Success Metrics
- **Token Reduction:** Target -20% size for `SKILL.md` files on average.
- **Maintainability:** Language specifics isolated in separate files.
- **Automation:** Security audit uses scripts instead of loose instructions.
