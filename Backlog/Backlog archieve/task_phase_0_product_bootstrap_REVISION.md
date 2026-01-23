# Phase 0 Task Specification Review

## 1. Summary of Key Issues & Recommendations

1.  **Script Interaction Conflict**: The original task described `init_product.py` as an "Interactive CLI" for the user, but the Skill instructions told the Agent to call it. Agents struggle with interactive `input()` loops (requiring complex `send_command_input` flows).
    *   **Fix**: Mandate **Dual-Mode** scripts. They must support CLI arguments (`--problem "..."`) for atomic agent execution, falling back to interactive mode only if arguments are missing (for humans).
2.  **O6 Standardization Missing**: The task requested new agents (`p01`, `p02`) but didn't explicitly enforce the new **O6 Agent Prompt Standard** (Identity/Context/Loop patterns) or **Script-First** logic defined in `agentic_development_optimisations.md`.
    *   **Fix**: Explicitly require the O6 schema and `Tier 0` skill compliance for new agents.
3.  **Ambiguous Definition of Done**: The DoD was qualitative ("Runs correctly").
    *   **Fix**: Convert to specific file-based checks (e.g., "Artifacts exist," "WSJF calculation handles malformed tables," "Agent ignores interactive prompt").
4.  **Skill strictness**: The logic for WSJF calculation was correctly delegated to a script, but the skill description didn't explicitly forbid the LLM from trying to "help" by calculating it itself if the script fails.
    *   **Fix**: Add "Adversarial Check" to skill requirements — explicitly instructing the agent NOT to compute.

---

## 2. Revised Task Specification

### Task: Phase 0 - Product Bootstrap & Core Tooling

> **Status:** Ready for Dev
> **Parent Initiative:** [Product Development Vision](./product_development_vision.md)
> **Assignee:** Unassigned
> **Priority:** High (Blocker for Phase 1)

---

#### 1. Executive Summary
**Objective:** Establish the foundational infrastructure ("Bootstrap") required to generate and refine product artifacts (`PRODUCT_VISION.md`, `PRODUCT_BACKLOG.md`) utilizing a **Script-First** methodology.

**Core Philosophy:**
1.  **Strict Separation:** Logic (Templating, Math, Sorting) resides in Python. Semantic Reasoning resides in Prompts.
2.  **Dual-Mode Tooling:** Scripts must be usable by **Humans** (Interactive) and **Agents** (Atomic/Flag-based).
3.  **O6 Compliance:** All new agents must follow the v3.7+ Standardized Prompt Schema.

---

#### 2. User Stories
- **As a User**, I want to run `python3 scripts/init_product.py` interactively to scaffold a new project without remembering template formats.
- **As an Agent (p01)**, I want to call `python3 scripts/init_product.py --problem "..." --users "..."` to generate files atomically without getting stuck in `input()` loops.
- **As a User**, I want WSJF scores to be mathematically precise (calculated by script), avoiding LLM math hallucinations.
- **As a System Architect**, I want strict TIER 2 isolation for these new skills so they don't pollute the context of technical development sessions.

---

#### 3. Technical Specifications

##### 3.1. Infrastructure (Scripts)

> **Constraint:** All scripts must use standard library `argparse`. No heavy external dependencies (e.g., `pandas`) unless absolutely necessary.

**A. `scripts/init_product.py`**
**Type:** Dual-Mode CLI (Interactive + Headless)
**Purpose:** Scaffolds `docs/PRODUCT_VISION.md`.
**Requirements:**
1.  **Arguments:** Support flags for all fields (`--name`, `--problem`, `--audience`, `--metrics`).
2.  **Logic:**
    - If flags provided: **Headless Mode** (Generate file, exit 0).
    - If no flags: **Interactive Mode** (Prompt user via `input()`).
3.  **Idempotency:** If `docs/PRODUCT_VISION.md` exists, fail gracefully or ask to overwrite (require `--force` flag for agents).
4.  **Output:** Valid Markdown file based on `skill-product-analysis` templates.

**B. `scripts/calculate_wsjf.py`**
**Type:** Data Processing CLI
**Purpose:** Deterministic prioritization of the Backlog.
**Requirements:**
1.  **Input:** Path to `PRODUCT_BACKLOG.md` (via `--file`).
2.  **Parsing strategy:** Robust table parsing (regex or line-splitting) to handle minor markdown variances.
    - *Error Handling:* If table format is invalid, output specific error message for the Agent to read.
    - *Graceful Math:* Handle division by zero (JobSize=0) by erroring or creating a warning.
3.  **Logic:**
    - Parse columns: `User Value`, `Time Criticality`, `Risk Reduction`, `Job Size`.
    - Logic: `WSJF = (UV + TC + RR) / Job Size`.
    - Sort: Descending by `WSJF`.
4.  **Output:** Overwrite file with updated values (formatting preserved).

##### 3.2. Skills (TIER 2)

> **Standard:** Must follow `skill-creator` guidelines and `O5 Skill Tiers` format.

**A. `skill-product-analysis`**
- **Location:** `.agent/skills/skill-product-analysis/SKILL.md`
- **Tier:** `2` (Lazy Loaded)
- **Token Budget:** < 1,000 tokens
- **Content:**
  - **YAML Frontmatter:** `name`, `description`, `tier: 2`.
  - **Structure Rules:** Definitions of "Problem Statement", "Success Metrics" (SMART).
  - **Tool Usage:** "To create vision, use `init_product.py` with flags. DO NOT write markdown manually."
  - **INVEST Criteria:** Reference for User Stories.

**B. `skill-backlog-prioritization`**
- **Location:** `.agent/skills/skill-backlog-prioritization/SKILL.md`
- **Tier:** `2` (Lazy Loaded)
- **Token Budget:** < 500 tokens
- **Content:**
  - **Constraint:** "You are FORBIDDEN from calculating WSJF scores yourself."
  - **Instruction:** "Run `python3 scripts/calculate_wsjf.py --file docs/PRODUCT_BACKLOG.md`."
  - **Scoring Guide:** Reference table for Business Value (e.g., "1 = Nice to have", "10 = Critical path").

##### 3.3. Agents (O6 Standardized)

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

#### 4. Implementation Steps

1.  **Infrastructure Setup**:
    - [ ] Create `scripts/` directory if missing.
    - [ ] Verify `Backlog/product_development_vision.md` prerequisites.

2.  **Develop Scripts (TDD)**:
    - [ ] Implement `init_product.py` with `argparse`. Verify `--help` and interactive fallback.
    - [ ] Implement `calculate_wsjf.py`. Verify with a mock `backlog.md` containing varied table formats.
    - [ ] **Test**: Create a standalone test script `tests/test_product_scripts.py` to ensure logic correctness.

3.  **Develop Skills**:
    - [ ] Create `skill-product-analysis/SKILL.md` (Check token count < 1000).
    - [ ] Create `skill-backlog-prioritization/SKILL.md` (Check token count < 500).

4.  **Develop Agents**:
    - [ ] Author `System/Agents/p01_product_analyst_prompt.md` (O6 schema).
    - [ ] Author `System/Agents/p02_product_reviewer_prompt.md` (O6 schema).

5.  **Documentation**:
    - [ ] Create/Update `System/Docs/PRODUCT_DEVELOPMENT.md` with usage guide.

---

#### 5. Definition of Done (DoD)

**Artifact Verification**
- [ ] `scripts/init_product.py` exists and supports both `--name "Test"` and interactive mode.
- [ ] `scripts/calculate_wsjf.py` exists and correctly sorts a markdown table.
- [ ] `.agent/skills/skill-product-analysis/SKILL.md` has `tier: 2` metadata.
- [ ] `System/Agents/p01_product_analyst_prompt.md` follows O6 Standard (Standardized Header).
- [ ] `System/Docs/PRODUCT_DEVELOPMENT.md` exists.

**Functional Verification**
- [ ] **Dual Mode Test**: Agent can invoke `init_product.py` without hanging.
- [ ] **Math Check**: `calculate_wsjf.py` handles division by zero (JobSize=0) gracefully (sets score to 0 or errors).
- [ ] **Parsing Check**: `calculate_wsjf.py` preserves other markdown content (headers, footers) outside the table.

**Framework Compliance**
- [ ] **Token Budget**: Skills stay within defined limits (<1000 and <500).
- [ ] **Linting**: Scripts pass `pylint` (score > 8.0).

---

#### 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Script Parsing Fragility** | High | Use regex for table parsing instead of generic split. Support standard GFM table syntax. |
| **Agent Loops** | Medium | Agents might try to "fix" the script output manually. **Mitigation:** Explicit "Forbidden" rule in Skill. |
| **Token Overflow** | Low | New skills are Tier 2 (Lazy). |

---

## 3. Rationale for Major Changes

*   **Dual-Mode Scripts**: Agents cannot operate a `wait-for-user-input` loop effectively without complex plumbing. Supporting CLI arguments (`--flag value`) is the standard "Script-First" pattern for agent tools.
*   **O6 Standardization**: The original task predated the strict "O6" requirement. Updating the agent specs prevents creating "Legacy" agents that would need immediate refactoring.
*   **Explicit Token Tiers**: Added `Tier: 2` requirements to the SKILL descriptions to align with the O5 optimization (Skill Tiers).
*   **Robust parsing requirement**: `calculate_wsjf.py` is a risk point. Markdown tables can vary (alignment colons, spacing). Specifying robust parsing prevents immediate bugs.
