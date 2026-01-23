# Development Plan: Phase 0 Product Bootstrap & Core Tooling

## Goal
Establish the foundational infrastructure to generate and refine product artifacts (`PRODUCT_VISION.md`, `PRODUCT_BACKLOG.md`) utilizing a **Script-First** methodology and strictly separated logic.

## Task Execution Sequence

### Stage 1: Infrastructure (Scripts)
- **Task 0.1** — Implement `scripts/init_product.py`
  - **Use Cases:** Scaffolding `PRODUCT_VISION.md` (Interactive + Headless).
  - **Description:** Create dual-mode Python script using `argparse`.
  - **Priority:** Critical
  - **Verification:** Unit tests + Manual execution check.

- **Task 0.2** — Implement `scripts/calculate_wsjf.py`
  - **Use Cases:** WSJF Prioritization and Sorting.
  - **Description:** Implement regex-based markdown table parsing and WSJF math logic.
  - **Priority:** Critical
  - **Verification:** Unit tests with malformed/valid input tables.

- **Task 0.3** — Create Test Suite
  - **Use Cases:** Verification of scripts.
  - **Description:** `tests/test_product_scripts.py` covering all edge cases (job size=0, bad table, etc).
  - **Priority:** Critical

### Stage 2: Skills & Resources (TIER 2)
- **Task 0.4** — Implement `skill-product-analysis`
  - **Use Cases:** p01 Agent logic for vision creation.
  - **Description:** Create `SKILL.md` (Tier 2), `resources/templates/vision_template.md` (Gold Standard structure), and examples.
  - **Priority:** High

- **Task 0.5** — Implement `skill-backlog-prioritization`
  - **Use Cases:** p01/p02 Agent logic for backlog management.
  - **Description:** Create `SKILL.md` (Tier 2) with "Logic Locker" (forbidden math) and `examples/backlog_table_example.md`.
  - **Priority:** High

### Stage 3: Agents (O6 Standard)
- **Task 0.6** — Author `p01_product_analyst`
  - **Description:** Create System/Agents/p01_product_analyst_prompt.md following O6 schema.
  - **Priority:** High

- **Task 0.7** — Author `p02_product_reviewer`
  - **Description:** Create System/Agents/p02_product_reviewer_prompt.md following O6 schema (Adversarial Role).
  - **Priority:** High

### Stage 4: Documentation & Verification
- **Task 0.8** — Create Documentation
  - **Description:** `System/Docs/PRODUCT_DEVELOPMENT.md` with usage guides and architecture notes.
  - **Priority:** Medium

## Verification Plan

### Automated Tests
- **Scripts:** Run `pytest tests/test_product_scripts.py`.
- **Linting:** Run `pylint scripts/*.py` (Target > 8.0).

### Manual Verification
1. **Interactive Init:**
   - Run: `python3 scripts/init_product.py` (No args) -> Verify it prompts for input.
   - Run: `python3 scripts/init_product.py --name "Test" --problem "A" ...` -> Verify file creation.
2. **WSJF Calculation:**
   - Create dummy `docs/PRODUCT_BACKLOG.md`.
   - Run: `python3 scripts/calculate_wsjf.py --file docs/PRODUCT_BACKLOG.md`.
   - Verify: Lines resorted by WSJF score.
3. **Agent Simulation:**
   - (Optional) Use `skill-product-analysis` instructions in a new chat to verify the agent uses the script.
