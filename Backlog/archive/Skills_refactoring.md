# Skills Refactoring Backlog

> **Status:** Completed
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

- [x] **Decompose Structure:**
    - [x] `SKILL.md`: Keep only universal principles (Strict Adherence, Input Handling, Anti-Loop).
    - [x] Create `resources/languages/` directory.
- [x] **Add Language Specifics:**
    - [x] Create `resources/languages/rust.md`: Rust-specific guidelines (borrow checker, unwrap safety, clippy).
    - [x] Create `resources/languages/solidity.md`: Smart contract security, gas optimization, checks-effects-interactions.
    - [x] Create `resources/languages/python.md`: Type hinting, docstrings, testing.
    - [x] Create `resources/languages/javascript.md`: Async/await, ecosystem standards.
- [x] **Update `SKILL.md`:** Add dynamic loading instruction or reference to look up language guides based on current task.

### 2. Refactor `testing-best-practices` (Medium Priority)
**Goal:** Provide concrete, runnable examples and standard boilerplate.

- [x] **Extract Examples:**
    - [x] Move inline naming/structure examples to `examples/`.
    - [x] Create `examples/pytest_structure.py`.
    - [x] Create `examples/jest_structure.js`.
- [x] **Create Templates:**
    - [x] `resources/templates/test_boilerplate.py`.
- [x] **Update `SKILL.md`:** Reference the new examples.

### 3. Refactor `security-audit` (Medium Priority)
**Goal:** Automate tooling and standardize checklists.

- [x] **Scripting:**
    - [x] Create `scripts/run_audit.py`: A unified wrapper to detect project type and run:
        - **Solidity:** `slither` (Static analysis), `aderyn` (if available).
        - **Python:** `bandit` (Security linter), `safety` (Dependencies).
        - **JS/TS:** `npm audit` / `yarn audit`.
        - **Rust:** `cargo audit` (Dependencies), `cargo clippy` (Lints).
        - **General:** Simple regex-based secrets detection (API keys, private keys).
- [x] **Resources:**
    - [x] Create `resources/checklists/owasp_top_10.md`: Web2 security standard (Injection, Auth, SSRF).
    - [x] Create `resources/checklists/solidity_security.md`: **High-Grade Smart Contract Security**:
        - **Standards:** Mapping to SCSVS (Smart Contract Security Verification Standard) and SWC Registry.
        - **DeFi Patterns:** Flash loans, Price Oracle manipulation, Slippage protection.
        - **Upgradability:** Storage collisions, Proxy patterns, Initializers.
        - **Cryptography:** Signature replay, Malleability, Randomness (Chainlink VRF).
        - **Access Control:** Timelocks, Multi-sig requirements, Role-based access.
    - [x] Create `resources/checklists/solana_security.md`: **High-Grade Solana**:
        - **Account Validation:** Ownership, Signer checks, Executable.
        - **PDA:** Bump validation, Seed uniqueness.
        - **Anchor:** `init` protection, correct types, `close` constraint.
    - [x] Create `resources/checklists/fuzzing_invariants.md`: Guidelines for writing Invariant Tests (Foundry/Echidna).
- [x] **Update `SKILL.md`:** 
    - [x] Instruct agent to use `scripts/run_audit.py`.
    - [x] **CRITICAL:** Mandate "Think like a Hacker" step using the checklists before any deployment.

### 4. Refactor `requirements-analysis` (Low Priority)
**Goal:** Streamline the prompt by removing the large TASK definition.

- [x] **Extract Template:**
    - [x] Move the "Technical Specification (TASK) Structure" section to `resources/templates/task_template.md`.
- [x] **Update `SKILL.md`:**
    - [x] Replace the inline template with a reference: "You MUST follow the structure defined in `resources/templates/task_template.md`."

### 5. Enrich `architecture-design` (Low Priority)
- [x] **Create Resources:**
    - [x] Create `resources/patterns/clean_architecture.md`: Reference for Layers (Entities, Use Cases, Adapters).
    - [x] Create `resources/patterns/event_driven.md`: Reference for Pub/Sub, Brokers, and Async flows.
- [x] **Update `SKILL.md`:**
    - [x] Reference the new patterns in the "Modularity" or "Core Principles" section.

### 6. Refactor `skill-adversarial-security` (Medium Priority)
**Goal:** Enhance security checks, separate sarcasm, and leverage `security-audit` tools.

- [x] **Integration with `security-audit`:**
    - [x] **Reconnaissance:** Mandate running `.agent/skills/security-audit/scripts/run_audit.py` to find low-hanging fruit before deep adversarial thought.
    - [x] **Shared Knowledge:** Link to `security-audit/resources/checklists/`:
        - Use `solidity_security.md` for drilling into DeFi logic (Flash loans, Oracles).
        - Use `solana_security.md` for attacking Account Validation and PDAs.
- [x] **Add Prompt Injection Checks:**
    - [x] Update `SKILL.md` (or extracted resources) to include checks for:
        - [x] Indirect Prompt Injection (data exfiltration via LLM).
        - [x] Jailbreaking attempts detection.
        - [x] System prompt leakage.
- [x] **Decomposition:**
    - [x] Move sarcastic prompts to `resources/prompts/sarcastic.md` to reduce token load.
    - [x] **Remove duplication:** Do NOT maintain separate OWASP lists. Reference `security-audit/resources/checklists/owasp_top_10.md`.

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
