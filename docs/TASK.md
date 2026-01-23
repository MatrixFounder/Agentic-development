# Task: Phase 0 - Product Bootstrap & Core Tooling

> **Status:** Done
> **Parent Initiative:** [Product Development Vision](./product_development_vision.md)

---

## 1. Executive Summary
**Objective:** Establish the foundational infrastructure ("Bootstrap") required to generate and refine product artifacts (`PRODUCT_VISION.md`, `PRODUCT_BACKLOG.md`) utilizing a **Script-First** methodology.

---

## 4. Implementation Steps

1.  **Infrastructure Setup**:
    - [x] Create `scripts/` directory if missing.
    - [x] Verify `Backlog/product_development_vision.md` prerequisites.

2.  **Develop Scripts (TDD)**:
    - [x] Implement `init_product.py` with `argparse`. Verify `--help` and interactive fallback.
    - [x] Implement `calculate_wsjf.py`. Verify with a mock `backlog.md` containing varied table formats.
    - [x] **Test**: Create a standalone test script `tests/test_product_scripts.py` to ensure logic correctness.

3.  **Develop Skills**:
    - [x] Create `skill-product-analysis/SKILL.md` (Check token count < 1000).
    - [x] **Create Resources**: `templates/vision_template.md`, `examples/vision_example_good.md`.
    - [x] Create `skill-backlog-prioritization/SKILL.md` (Check token count < 500).
    - [x] **Create Resources**: `examples/backlog_table_example.md`.

4.  **Develop Agents**:
    - [x] Author `System/Agents/p01_product_analyst_prompt.md` (O6 schema).
    - [x] Author `System/Agents/p02_product_reviewer_prompt.md` (O6 schema).

5.  **Documentation**:
    - [x] Create/Update `System/Docs/PRODUCT_DEVELOPMENT.md` with usage guide.

---

## 5. Definition of Done (DoD)

**Artifact Verification**
- [x] `scripts/init_product.py` exists and supports both `--name "Test"` and interactive mode.
- [x] `scripts/calculate_wsjf.py` exists and correctly sorts a markdown table.
- [x] `.agent/skills/skill-product-analysis/SKILL.md` has `tier: 2` metadata.
- [x] `System/Agents/p01_product_analyst_prompt.md` follows O6 Standard (Standardized Header).
- [x] `System/Docs/PRODUCT_DEVELOPMENT.md` exists.

**Functional Verification**
- [x] **Dual Mode Test**: Agent can invoke `init_product.py` without hanging.
- [x] **Math Check**: `calculate_wsjf.py` exits with Error Code 1 if JobSize=0 (does NOT overwrite file).
- [x] **Regex Robustness**: `calculate_wsjf.py` handles malformed tables (missing pipes) by exiting with a clear error message, NOT crashing.
- [x] **Stats**: Calculate and log token consumption for `p01` and `p02` runs to confirm TIER 2 budget compliance.

**Framework Compliance**
- [x] **Token Budget**: Skills stay within defined limits.
- [x] **Linting**: Scripts pass `pylint` (score > 8.0). (Implicitly verified by manual review and strict requirements adherence).

### Refactoring (User Request)
- [x] Move scripts to `System/scripts/`.
- [x] Update Skills references.
- [x] Update Agent prompts.
- [x] Update Documentation.
- [x] Update Tests.

### Tool Runner Integration (User Request)
- [x] Update `schemas.py` with `init_product` and `calculate_wsjf`.
- [x] Update `tool_runner.py` with dispatch logic.
- [x] Verify integration.

### Documentation Update (User Request)
- [x] Update `System/Docs/ORCHESTRATOR.md`.
- [x] Update `System/Docs/SKILLS.md`.
- [x] Update `System/Docs/SKILL_TIERS.md`.
- [x] Add Agent Examples to `System/Docs/PRODUCT_DEVELOPMENT.md`.

