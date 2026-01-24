# Task: Phase 0 - Product Bootstrap & Core Tooling

> **Status:** Ready for Dev
> **Parent Initiative:** [Product Development Vision](./product_development_vision.md)
> **Assignee:** Unassigned
> **Priority:** High (Blocker for Phase 1)

---

## 1. Executive Summary
**Objective:** Establish the foundational infrastructure ("Bootstrap") required to generate and refine product artifacts (`PRODUCT_VISION.md`, `PRODUCT_BACKLOG.md`) utilizing a **Script-First** methodology.

**Core Philosophy:**
1.  **Strict Separation:** Logic (Templating, Math, Sorting) resides in Python. Semantic Reasoning resides in Prompts.
2.  **Dual-Mode Tooling:** Scripts must be usable by **Humans** (Interactive) and **Agents** (Atomic/Flag-based).
3.  **O6 Compliance:** All new agents must follow the v3.7+ Standardized Prompt Schema.

---

## 2. User Stories
- **As a User**, I want to run `python3 System/scripts/init_product.py` interactively to scaffold a new project without remembering template formats.
- **As an Agent (p01)**, I want to call `init_product` via native Tool Runner (or `python3 System/scripts/init_product.py`) to generate files atomically.
- **As a User**, I want WSJF scores to be mathematically precise (calculated by script), avoiding LLM math hallucinations.
- **As a System Architect**, I want strict TIER 2 isolation for these new skills so they don't pollute the context of technical development sessions.

---

## 3. Technical Specifications

### 3.1. Infrastructure (Scripts)

> **Constraint:** All scripts must use standard library `argparse`. No heavy external dependencies (e.g., `pandas`) unless absolutely necessary.

**A. `System/scripts/init_product.py`**
**Type:** Dual-Mode CLI (Interactive + Headless)
**Purpose:** Scaffolds `docs/PRODUCT_VISION.md`.
**Requirements:**
1.  **Arguments:** Support flags for all fields (`--name`, `--problem`, `--audience`, `--metrics`).
2.  **Logic:**
    - If flags provided: **Headless Mode** (Generate file, exit 0).
    - If no flags: **Interactive Mode** (Prompt user via `input()`).
3.  **Idempotency:** If `docs/PRODUCT_VISION.md` exists, fail gracefully or ask to overwrite (require `--force` flag for agents).
4.  **Output:** Valid Markdown file at `docs/PRODUCT_VISION.md` based on `skill-product-analysis` templates.

**B. `System/scripts/calculate_wsjf.py`**
**Type:** Data Processing CLI
**Purpose:** Deterministic prioritization of the Backlog.
**Requirements:**
1.  **Input:** Path to `PRODUCT_BACKLOG.md` (via `--file`).
2.  **Parsing strategy:** **Regex-First Approach**.
    - DO NOT use simple string splitting (e.g., `line.split("|")`).
    - MUST use regex patterns that handle:
        - Optional surrounding pipes.
        - Whitespace padding.
        - Escaped pipe characters `\|` (optional but good practice).
    - *Validation:* If the table structure is invalid:
        -   **Exit Code 1**.
        -   Print a friendly correction guide (e.g., "Row 5 is missing a column 'Job Size'").
3.  **Logic:**
    - Parse columns: `User Value`, `Time Criticality`, `Risk Reduction`, `Job Size`.
    - Logic: `WSJF = (UV + TC + RR) / Job Size`.
    - **Division by Zero Protection**: If `Job Size` is 0:
        -   **Exit Code 1**.
        -   Print specific error: "Job Size cannot be 0 for item '...'. Please set to at least 1."
        -   **DO NOT** overwrite the file.
    - Sort: Descending by `WSJF`.
4.  **Output:** Overwrite file with updated values (formatting preserved).

**C. Tool Runner Integration (New)**
**Type:** Native System Architecture
**Purpose:** Enable Agents to call these scripts as native tools, not just shell commands.
**Requirements:**
1.  **UPDATE** `System/scripts/tool_runner.py`: Add dispatch logic for `init_product` and `calculate_wsjf`.
2.  **UPDATE** `.agent/tools/schemas.py`: Add JSON schemas for these tools.
3.  **Mechanism:** `tool_runner` should spawn a subprocess to call the python scripts in `System/scripts/`, ensuring isolation.

### 3.2. Skills (TIER 2)

> **Standard:** Must follow `skill-creator` guidelines and `O5 Skill Tiers` format.
> **Constraint:** All skills MUST include `resources/templates` and `examples/` to minimize hallucinations.

**A. `skill-product-analysis`**
- **Location:** `.agent/skills/skill-product-analysis/SKILL.md`
- **Tier:** `2` (Lazy Loaded)
- **Token Budget:** < 1,000 tokens
- **Content:**
  - **YAML Frontmatter:** `name`, `description`, `tier: 2`.
  - **Structure Rules:** Definitions of "Problem Statement", "Success Metrics" (SMART).
  - **Tool Usage:** "To create vision, use `init_product.py` with flags. DO NOT write markdown manually."
  - **INVEST Criteria:** Reference for User Stories.
- **Required Resources:**
  - `resources/templates/vision_template.md`: The exact markdown structure the script generates. (Reference this in SKILL.md).
  - `examples/vision_example_good.md`: A "Gold Standard" example of a filled-out vision doc.
  - `examples/vision_example_bad.md`: An example of "Fluff" (Vague metrics, solution-first thinking) to train the critic.

**B. `skill-product-backlog-prioritization`**
- **Location:** `.agent/skills/skill-product-backlog-prioritization/SKILL.md`
- **Tier:** `2` (Lazy Loaded)
- **Token Budget:** < 500 tokens
- **Content:**
  - **Constraint:** "You are FORBIDDEN from calculating WSJF scores yourself."
  - **Instruction:** "Run `python3 scripts/calculate_wsjf.py --file docs/PRODUCT_BACKLOG.md`."
  - **Scoring Guide:** Reference table for Business Value (e.g., "1 = Nice to have", "10 = Critical path").
- **Required Resources:**
  - `examples/backlog_table_example.md`: Correctly formatted Markdown table with WSJF columns for the agent to emulate if creating new rows manually.

### 3.3. Agents (O6 Standardized)

**A. `System/Agents/p01_product_analyst_prompt.md`**
- **Role:** Product Owner / Analyst
- **Structure (O6):**
  1.  **Identity:** "You are the Product Analyst..."
  2.  **Context Loading:** Mandate `Tier 0` (Core, Safe-Cmds, Artifacts, Session State) + `Tier 2` (Product Analysis).
  3.  **Execution Loop:** Read Request → Refine Spec → Call Script → Verify.
- **Key Behavior:**
  - Uses `init_product.py` to create initial files.
  - Uses `calculate_wsjf.py` after creating stories.

**B. `System/Agents/p02_product_reviewer_prompt.md`**
- **Role:** VDD Adversarial Critic
- **Structure (O6):**
  1.  **Identity:** "You are the Design Critic..."
  2.  **Context Loading:** `Tier 0` + `Tier 2` (Adversarial, Product Analysis).
  3.  **Review Loop:** Read Artifact → Apply Checklist → Report.
- **Key Behavior:**
  - Check for "Fluff" words ("synergy", "world-class", "seamless").
  - Verification: "Do stories meet INVEST?"

---

## 4. Implementation Steps

1.  **Infrastructure Setup**:
    - [x] Create `scripts/` directory if missing.
    - [x] Verify `Backlog/product_development_vision.md` prerequisites.

2.  **Develop Scripts (TDD)**:
    - [x] Implement `init_product.py`. Verify `--help` and interactive fallback.
    - [x] Move to `System/scripts/` (Refactoring).
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
- [x] `System/scripts/init_product.py` exists and supports both `--name "Test"` and interactive mode.
- [x] `System/scripts/calculate_wsjf.py` exists and correctly sorts a markdown table.
- [x] **Tool Integration:** Tools registered in `schemas.py` and executable via `tool_runner`.
- [ ] `.agent/skills/skill-product-analysis/SKILL.md` has `tier: 2` metadata.
- [ ] `System/Agents/p01_product_analyst_prompt.md` follows O6 Standard (Standardized Header).
- [ ] `System/Docs/PRODUCT_DEVELOPMENT.md` exists.

**Functional Verification**
- [x] **Dual Mode Test**: Agent can invoke `init_product.py` without hanging.
- [x] **Math Check**: `calculate_wsjf.py` exits with Error Code 1 if JobSize=0 (does NOT overwrite file).
- [x] **Manual Verification (P02)**: Verify that `p02_product_reviewer` correctly identifies issues in `vision_example_bad.md` (Adversarial check).
- [x] **Regex Robustness**: `calculate_wsjf.py` handles malformed tables (missing pipes) by exiting with a clear error message, NOT crashing.
- [x] **Docs Verification**: `System/Docs/PRODUCT_DEVELOPMENT.md` contains:
    - Usage Guide (CLI + Agent)
    - Architecture Diagram
    - Troubleshooting (Exit codes explanation)
- [x] **Stats**: Calculate and log token consumption for `p01` and `p02` runs to confirm TIER 2 budget compliance.
**Framework Compliance**
- [x] **Token Budget**: Skills stay within defined limits (<1000 and <500).
- [x] **Linting**: Scripts pass `pylint` (score > 8.0).

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Script Parsing Fragility** | High | **Solution**: Implement `Regex-First` parsing. Do NOT rely on `.split('|')`. Create a `tests/fixtures/malformed_table.md` to verify the script rejects bad input gracefully with a helpful error message for the Agent. |
| **Agent Loops** | Medium | **Solution**: Implement **Logic Lockers** in Skills. <br>1. *Forbidden Action*: "Do not calculate WSJF." <br>2. *Stop Sequence*: If script fails X times, Agent MUST call `notify_user` instead of retrying blindly. |
| **Token Overflow** | Low | New skills are Tier 2 (Lazy). |
