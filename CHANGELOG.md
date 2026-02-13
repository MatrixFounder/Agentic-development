[Русская версия](CHANGELOG.ru.md) | [English version](CHANGELOG.md)

<!--
## [Unreleased]

### 🇺🇸 English
#### Added
- ...

#### Changed
- ...

#### Fixed
- ...
-->

## 🇺🇸 English Version (Primary)

### **v3.9.12 — Framework Consistency, Parallel Agents & Safety Fixes** (Feature / Bugfix)

#### **Added**
* **Parallel Agent Architecture (POC)**:
    * **New Skill: `skill-parallel-orchestration` (Tier 2)**: Protocol for decomposing tasks into parallel sub-tasks and spawning sub-agents (mock runner).
    * **Concurrent State Safety**: `update_state.py` now uses `fcntl` file locking for atomic read-modify-write on `latest.yaml`, preventing race conditions.
    * **Mock Agent Runner**: `spawn_agent_mock.py` simulates async agent execution with state updates.
    * **Documentation**: `docs/POC_PARALLEL_AGENTS.md` guide and `docs/ARCHITECTURE.md` updated with Parallel Execution Model.
* **Skill Validation Hook**:
    * **`.gemini/hooks/validate_skill_hook.sh`**: `AfterTool` hook that auto-validates skills via `validate_skill.py` on every write to `.agent/skills/`.
    * **`.gemini/settings.json`**: Hook configuration with `$GEMINI_PROJECT_DIR` fallback for cross-runner compatibility.
    * **Skill Creation Gate**: Added mandatory `init_skill.py` rule to `GEMINI.md` and `AGENTS.md` Development Phase. Manual skill creation is now prohibited.

#### **Fixed**
* **Data Loss Prevention**: Patched `trigger_technical.py` to abort if `docs/TASK.md` already exists, preventing accidental overwrites during product handoff.
* **Protocol Integrity**: Updated `light-02-develop-task` workflow to enforce mandatory `.AGENTS.md` updates, preventing memory drift in Light Mode.
* **Standardization**: Updated `vdd-01-start-feature` to use the authoritative `skill-archive-task` protocol instead of hardcoded manual steps.
* **Shell Injection (VDD)**: Replaced heredoc interpolation with `jq -n` in `validate_skill_hook.sh` to prevent malformed JSON from `validation_output`.
* **Invalid Mode (VDD)**: Fixed `spawn_agent_mock.py` using non-existent mode `"Wrapper"` → `"EXECUTION"`.

---



### **v3.9.11 — Hardened Pipeline & Self-Improvement System** (Feature)

#### **Added**
* **New Skill: `skill-spec-validator` (Tier 2)**:
    * **RTM Validation**: Mechanically enforces that `docs/TASK.md` contains a Requirements Traceability Matrix.
    * **Atomic Planning**: Mechanically enforces that `docs/PLAN.md` covers every RTM item with an ID-tagged task (e.g., `[R1]`).
* **New Skill: `skill-self-improvement-verificator` (Tier 3)**:
    * **Meta-Audit**: Acts as a "Guardian" for the framework itself. Audits specifications for `framework-upgrade` to prevent regression.
* **New Workflow: `/framework-upgrade`**:
    * Specialized pipeline for upgrading Prompts, Skills, and System Logic.
    * Integrates `skill-self-improvement-verificator` gates at Analysis and Planning stages.
* **Documentation**:
    * **Claude Code & Gemini CLI**: Added native integration guides (Options C & D) in READMEs.
    * **Concept Deep Dive**: Added "Blueprint vs Driver" explanation to clarify `00_agent_development.md` vs `AGENTS.md` roles.
    * **Usage Scenarios**: Added practical examples for Standard, Light Mode, and Session Restoration workflows.

#### **Improved**
* **Workflows**:
    * **`/vdd-enhanced`**: Upgraded to "Hardened Mode". Now includes `skill-spec-validator` checkpoints with auto-correction loops (Max 3 retries).
* **Agent Prompts**:
    * **Analyst**: Mandates RTM table generation (except for `[LIGHT]` tasks).
    * **Planner**: Mandates Atomic Checklists with Strict ID linking.
    * **Developer**: Enforces Strict Stub-First methodology (except for `[LIGHT]` tasks).
* **Reliability**:
    * **`skill-creator`**: now outputs mandatory cleanup instructions to prevent debris.
    * **`validate.py`**: robustness fix for parsing Markdown tables with escaped characters.

---


### **v3.9.10 — Skill Creator Cleanup & Brainstorming 2.1** (Optimization)

#### **Improved**
* **`skill-creator`**:
    * **Cleanup Protocol**: Added specific instructions to remove unused placeholder directories (`scripts/`, `assets/`, `references/`) after skill initialization.
    * **Validation**: Verified that `validate_skill.py` supports "lean" skills without empty folders.
* **`brainstorming`** (v2.1):
    * **Universal Gold Standard**: Upgraded to v2.1 with "Universal" compatibility (tool agnostic).
    * **3-Tier Assessment**: Implemented **Trivial/Medium/Complex** complexity classification with tailored protocols for each.
    * **Safety Guardrails**: Added strict "No Coding without Design" rules and Handover Templates.

---

### **v3.9.9 — Skill Resources Migration & Validation Hardening** (Optimization)

#### **Refactored**
* **Skill Standardization (Gold Standard)**:
    * **Directory Hygiene**: Migrated `resources/` folders to `assets/` (templates) and `references/` (knowledge) across all skills.
    * **Legacy Removal**: Deprecated `resources/` directory to strictly enforce Semantic Folder Structure.

#### **Fixed**
* **Validation**:
    * **Config Support**: Updated `validate_skill.py` to explicitly allow `config/` directories (restoring support for `skill-product-solution-blueprint`).
    * **CSO Violations**: Fixed description prefixes in 6 skills (`developer-guidelines`, `requirements-analysis`, etc.) to meet "Gold Standard" compliance (`Use when`, `Guidelines for`).

#### **Verified**
* **Global Audit**: Ran verification script on all migrated skills to ensure 0 broken links and 100% validation pass rate.

---

### **v3.9.8 — Meta-Skills Independence** (Refactoring)
#### **Decoupled**
* **Project-Agnostic Meta-Skills**: `skill-creator` and `skill-enhancer` are now fully portable and independent of the Antigravity project.
    * **Configurable**: Policies (Tiers, Banned Words, File Rules) are now loaded from `.agent/rules/skill_standards.yaml` instead of hardcoded Python dicts.
    * **Zero-Dependency**: Removed `PyYAML` dependency. Implemented a custom "Vanilla Python" parser (`skill_utils.py`) to ensure tools run on any environment without `pip install` or `venv`.
    * **Documentation**: Removed hardcoded references to `System/Docs/SKILLS.md` and "Gemini/Antigravity". Replaced with generic "Skill Catalog" concepts.

#### **Added**
* **New Manual**: `System/Docs/skill-writing.md` — A portable User Guide for using the meta-skills (Install, Config, Usage).
* **Resilience**: Scripts now include a **Bundled Default Config** (`skill_standards_default.yaml`) for instant drop-in usage if project config is missing.

#### **Refined**
* **Hybrid Folder Structure**: Refactored `skill-creator` and `skill-enhancer` to use a semantic folder standard:
    * `examples/` (Train): Few-shot examples for the agent.
    * `assets/` (Material): User-facing templates and output files.
    * `references/` (Knowledge): Heavy context, specs, and guidelines.
    * `scripts/` (Tools): Python automation.
    * *Deprecated `resources/` in favor of more specific `assets/` and `references/`.*

#### **Verified**
* **E2E Testing**: Validated proper functioning of dynamic tiers, parser correctness (including edge cases like inline dicts), and gap analysis on a test skill.
* **Migration**: Successfully migrated `skill-creator` and `skill-enhancer` to the new structure without data loss.

---

### **v3.9.7 — Skill Best Practices & AGI-Agnostic Hardening** (Optimization)

#### **Added**
* **Extended Best Practices Integration**:
    * **Checklist Workflows**: Added native support for the "Checklist Pattern" in `SKILL_TEMPLATE.md` and `skill_design_patterns.md`.
    * **Gerund Naming**: `init_skill.py` now advises users to use Action-Oriented naming (e.g., `processing-files`).
    * **POV Detection**: `analyze_gaps.py` now flags First/Second person POV ("I can...", "You can...") to enforce Third-Person objectivity.
    * **Anti-Patterns**: `analyze_gaps.py` now detects Windows-style paths (`back\slashes`) to ensure cross-platform compatibility.
* **Logic Hardening**:
    * **"Solve, Don't Punt"**: Explicitly banned "Try to..." language in favor of deterministic scripts.
    * **Rationalization Table**: Built-in to default templates to preemptively block agent excuses.

#### **Improved**
* **`analyze_gaps.py`**:
    * **False Positive Reduction**: Fixed regex to ignore quoted words (e.g., prohibiting "should" no longer flags the rule itself) and Markdown tables.
    * **Robust Parsing**: Enhanced Windows path detection to handle mixed text/code contexts.
* **`skill-creator`**:
    * **Self-Sufficiency**: Added `skill_design_patterns.md` resource to decouple the skill from external docs.
    * **TDD Integration**: Evaluation-Driven Development is now a core pattern.

#### **Verified**
* **VDD Round 3**: Created an adversarial `bad-skill-helper` with intentional violations. The system successfully detected and flagged all anti-patterns (Vague Name, POV, Windows Paths).

---

### **v3.9.7 — Iterative Design & VDD Robustness** (Feature)

#### **Added**
* **New Workflow: `/iterative-design`**:
    * **Concept Loop**: brain storm -> Spec Draft -> VDD Audit -> Human Review -> Refinement.
    * **Human-in-the-Loop**: Explicit checkpoints for user feedback before coding.
* **New Skill: `brainstorming` (Tier 2)**:
    * **Pre-Planning**: Specialized instructions for research and idea generation.
    * **Anti-Hallucination**: Strict "NO CODING" rules during brainstorming phase.

#### **Fixed**
* **VDD Artifact Consistency**:
    * **Logic Gap Closed**: Fixed issue where `iterative-design` requested a report but `vdd-adversarial` had no template.
    * **Templates**: Added `resources/template_critique.md` to `skill-vdd-adversarial` for standardized auditing.
    * **Rich Skill**: Refactored `vdd-adversarial` to meet `skill-enhancer` standards (Resources separation).

---

### **v3.9.6 — Evolved TDD & Strict Reliability** (Feature)

#### **Added**
* **New Skill: `tdd-strict` (Tier 3)**:
    * **High Assurance Mode**: Enforces "Mechanical Verification" (Failing test MUST match `EXPECTED_FAIL_REASON`).
    * **Law of Minimalism**: Explicitly bans speculative coding and dead code.
    * **Self-Contained**: Can be loaded independently of Tier 1 skills.
* **Bug Fixing Protocol (Universal)**:
    * Added to `developer-guidelines` (Section 6).
    * Mandates "Reproduce First" rule for ALL bug fixes (Tier 1).

#### **Improved**
* **Checklists**:
    * **`code-review-checklist`**: Added "High Assurance" section for verifying strict TDD compliance.
    * **`plan-review-checklist`**: Added check for planning Strict Mode usage.
* **Workflows**:
    * Updated `/full-robust` pipeline to automatically load `tdd-strict` for maximum reliability.
* **Documentation**:
    * Updated `System/Docs/SKILLS.md` with Tier 3 definitions.
    * Updated `System/Docs/WORKFLOWS.md` to reflect strict integration.

---

### **v3.9.5 — Skill Hardening & Gold Standard Refactoring** (Optimization)

#### **Refactored (Gold Standard)**
* **`documentation-standards`**:
    * **Token Optimization**: Extracted inline templates to `resources/templates/` (60%+ reduction).
    * **Richness**: Added `examples/good_documentation.py` (Gold Standard example).
    * **Resilience**: Added "Red Flags" and "Rationalization Table".
* **`skill-planning-format`**:
    * **Token Optimization**: Extracted massive templates (`PLAN.md`, `TASK.md`) to `resources/templates/`.
    * **Richness**: Added `examples/PLAN_EXAMPLE.md` and `examples/TASK_EXAMPLE.md`.
* **`skill-task-model`**:
    * **Richness**: Extracted inline Use Case examples (Good/Bad) to `examples/`.
    * **Resilience**: Added "Red Flags" and "Rationalization Table".

#### **Fixed**
* **`light-mode`**: Fixed YAML syntax error (`[LIGHT]` tag unquoted) and CSO violation in description.
* **`skill-safe-commands`**: Updated documentation to allow `AGENTS.md` configuration.

#### **Improved**
* **System Resilience**:
    * **No-Dependency Parsing**: Removed `PyYAML` dependency from `validate_skill.py` and `analyze_gaps.py`.
    * **Robust Parsing**: Implemented manual YAML parser handling quotes, lists, and comments gracefully.
* **CSO Schemas**: Updated `skill-creator` and `skill-enhancer` to allow richer description prefixes: `Use when`, `Guidelines for`, `Standards for`, `Defines`, `Helps with`.

---

### **v3.9.4 — Product Skills Deepening & Refactoring** (Optimization)

#### **Refactored**
* **Strategic Analyst (`p01`):**
    * Refactored Prompt: Removed inline template, added `Execution Loop` with Deconstruct/Timing/Moat steps.
    * Updated Skill `skill-product-strategic-analysis`:
        * Added `market_strategy_template.md` (Core Thesis, Moat Score, Risks).
        * Added Example `01_strong_ai_assistant.md` (Strong Go).
        * Added Example `02_nogo_vertical_video.md` (No-Go).
* **Product Analyst (`p02`):**
    * Refactored Prompt: Added `User Refinements` input, delegated Vision generation to Skill.
    * Updated Skill `skill-product-analysis`:
        * Updated `vision_template.md` (Core Pillars, Moat Score, Emotional Logic).
        * Added rigorous examples: `01_strong_go_devboost`, `02_consider_talentflow`, `03_nogo_quickbites`.
* **Solution Architect (`p04`):**
    * Refactored Prompt: Removed duplicated template.
    * Updated Skill `skill-product-solution-blueprint`:
        * Updated `solution_blueprint_template.md` (Unit Economics, Verdict).
        * Updated `calculate_roi.py` to output ARPU, CAC, LTV/CAC.
        * Added examples: `01_simple_flexarb` and `02_advanced_loyaltyhub`.
* **Director (`p03`):**
    * Refactored Prompt: Integrated `skill-product-backlog-prioritization`.
    * Added Step 3: Auto-Prioritization (WSJF) before sign-off.
    * Added Step 4: Auto-Hash generation via `sign_off.py`.

#### **Improved**
* **Consistency:** All Product Agents (`p01`, `p02`, `p04`) now use a unified "Prompt → Skill → External Template" architecture.
* **Scoring:** Implemented quantitative scoring (10-factor matrix) and "Verdict" logic across all product artifacts.

---

### **v3.9.3 — Documentation Hygiene & JSON Enforcement** (Maintenance)

#### **Changed**
* **Documentation Standardization:**
    * **JSON Enforcement:** Updated `skill-product-solution-blueprint` to strictly enforce `.json` for `calculate_roi.py` inputs (removed ambiguous YAML references).
    * **Path Hygiene:** Standardized temporary artifact location to `docs/product/` (e.g., `docs/product/stories.json`).
* **Resource Structure:**
    * Flattened template structure in `skill-product-solution-blueprint` (moved `resources/templates/` -> `resources/`).
    * Updated `SKILL.md` to reference the canonical `solution_blueprint_template.md`.

---

### **v3.9.2 — Product Skills Refactoring & Math Hardening** (Optimization)

#### **Added**
* **Advanced Financials:** `calculate_roi.py` now supports:
    * **Granular Sizing:** T-Shirt sizes (XS-XXL) mapped to hours via `sizing_config.json`.
    * **LLM Acceleration:** "Friendliness" score discounting based on global factors.
    * **Metrics:** NPV (3yr), LTV, CAC, and Payback estimations.
* **Product Scoring:** New `score_product.py` implementing 10-Factor Matrix (Problem Intensity, Moat, etc.).
* **Documentation:**
    * `System/Docs/PRODUCT_CALCULATIONS_MANUAL.md`: Detailed "Magic Math" FAQ.
    * Updated `System/Docs/PRODUCT_DEVELOPMENT.md` with Calculation Manual reference.

#### **Optimized**
* **Prioritization:** `calculate_wsjf.py` now natively supports T-Shirt sizes (S, M, L) mapped to Fibonacci.
* **Security (VDD):**
    * Hardened `calculate_roi.py` against "Time Travel" bugs (negative duration).
    * Clamped `score_product.py` inputs (1-10) to prevent overflow.
    * Removed `PyYAML` dependency for lighter execution.

---

### **v3.9.1 — Documentation Sync & Cleanup** (Maintenance)

#### **Optimized**
* **Documentation Synchronization:**
    * Updated `README.md` and `README.ru.md` to fully reflect Product Development capabilities (Agents, Workflows, Artifacts).
    * Refactored `00_agent_development.md` description to "Meta-System Prompt".
* **Standards Enforcement (O6a):**
    * Updated `System/Docs/SKILLS.md` and `SKILL_TIERS.md` to strictly enforce "Script-First" and "Example Separation" patterns.
    * Removed legacy references to `Backlog/agentic_development_optimisations.md`.
* **Cleanup:**
    * Archived `Backlog/agentic_development_optimisations.md` as all optimization milestones (O1-O7) are complete and documented in System Docs.

---

### **v3.9.0 — Product Discovery & Handoff** (Feature)

#### **Added**
* **Completed Product Phase:** Full "Venture Builder" pipeline with 5 new agents (`p00`-`p04`).
    * **Strategy:** `skill-product-strategic-analysis` (TAM/SAM/SOM).
    * **Vision:** `skill-product-analysis` (Crossing the Chasm).
    * **Solution:** `skill-product-solution-blueprint` (ROI, Risk, Text-UX).
* **Quality Gate (VDD):**
    * **Adversarial Director (`p03`):** Blocks handoff if "Moat" is weak.
    * **Cryptographic Handoff:** `sign_off.py` -> `verify_gate.py` chain ensures only approved backlogs reach developers.
* **Workflows:**
    * `/product-full-discovery`: End-to-end Venture Building.
    * `/product-quick-vision`: For internal tools.
    * `/product-market-only`: For rapid idea validation.
* **Documentation:**
    * `System/Docs/PRODUCT_DEVELOPMENT.md`: Comprehensive playbook.
    * `System/Docs/WORKFLOWS.md`: Updated with Product workflows.

---

### **v3.8.0 — Phase 0: Product Bootstrap** (Feature)

#### **Added**
* **Product Management Module:**
    * **New Skills:** `skill-product-analysis` (Vision) and `skill-product-backlog-prioritization` (WSJF).
    * **New Agents:** `p01_product_analyst` (Creator) and `p02_product_reviewer` (VDD Critic).
    * **New Documentation:** [`System/Docs/PRODUCT_DEVELOPMENT.md`](System/Docs/PRODUCT_DEVELOPMENT.md) with usage scenarios.
* **Native Tool Integration:**
    * **Product Tools:** `init_product` and `calculate_wsjf` registered in `schemas.py`.
    * **Tool Runner:** Updated `System/scripts/tool_runner.py` to dispatch these tools via native subprocess calls.
    * **Scripts Root:** Moved scripts from `scripts/` to `System/scripts/` to align with framework standards.

#### **Changed**
* **Documentation:**
    * Updated `ORCHESTRATOR.md` with new supported tools.
    * Updated `SKILLS.md` with Product Management section.
    * Updated `SKILL_TIERS.md` with new Tier 2 skills.

---

### **v3.7.2 — O7: Session Context Persistence** (Optimization)

#### **Added**
* **New Skill: `skill-session-state`**: TIER 0 capability to persist/restore session context.
    * **Script-First**: `update_state.py` handles atomic YAML updates.
    * **Protocol**: Defines Boot (Read) and Boundary (Write) triggers.
* **Boot Protocol**: Updated `GEMINI.md` and `AGENTS.md` to restore state from `.agent/sessions/latest.yaml` on session start.
* **Agent Updates**: All 10 Agent Prompts updated to include `skill-session-state` in TIER 0 list.


### **v3.7.1 — Light Mode** (Feature)

#### **Added**
* **Light Mode:** New fast-track workflow for trivial tasks (typos, UI tweaks, simple bugfixes).
    * Skips Architecture and Planning phases (~50% token savings).
    * Workflows: `light-01-start-feature.md`, `light-02-develop-task.md`.
    * Skill: `light-mode` (Tier 2) with escalation protocol and security sanity checks.
    * Updated `GEMINI.md`, `AGENTS.md`, `WORKFLOWS.md`, `SKILLS.md`.

---

### **v3.7.0 — Skills Refactoring & Security Hardening** (Optimization)

#### **Added**
* **Security Automation:** Added `run_audit.py` to `security-audit` skill. Auto-detects project type (Solidity/Rust/Python/JS) and runs relevant tools (`slither`, `bandit`, `cargo audit`).
* **High-Grade Checklists:**
    * `solidity_security.md`: DeFi patterns, Flash Loans, Upgradability.
    * `solana_security.md`: Anchor validation, PDAs, Arithmetic.
* **Architecture Patterns:** Added `clean_architecture.md` and `event_driven.md` to `architecture-design` resources.
* **LLM Security:** Added Prompt Injection, Jailbreaking, and System Prompt Leakage checks to `skill-adversarial-security`.

#### **Optimized**
* **Skills Refactoring (O6):**
    * **Example Separation:** Extracted inline templates from `requirements-analysis`, `testing-best-practices` to `resources/`.
    * **Script-First:** Replaced manual instructions with script mandates.
    * **Sarcastic Persona:** Extracted prompt examples to `resources/prompts/sarcastic.md`.
* **Documentation:** Updated `System/Docs/SKILLS.md` to mandate V2 standards (Script-First, Example-Separation).

#### **Verified**
* **Global Validation:** All 6 refactored skills passed `validate_skill.py`.
* **Safety:** TIER 0 skills (`core-principles`) verified intact.

---

### **v3.6.5 — Configuration Standardization** (Refactoring)

#### **Changed**
* **Project Structure:**
    * Moved `.gemini/GEMINI.md` to `./GEMINI.md` (Project Root).
    * Renamed `.cursorrules` to `AGENTS.md` (Project Root) for clarity.
* **Documentation:** Updated `README.md`, `README.ru.md` and `docs/ARCHITECTURE.md` to reflect the new configuration structure.

---

### **v3.6.4 — O7 Prep & System Manifesto** (Documentation)

#### **Optimized**
* **System Manifesto (O11):** Rewritten `System/Agents/00_agent_development.md` to be the single source of truth for v3.6+ architecture.
    * Aligned with O1 (Skill Tiers) and O2 (Orchestrator Patterns).
    * Added section on **Agentic Mode** and `task_boundary` usage.
    * Included `10. Security Auditor` role.
* **O7 Specification:** Refined Session Context Management optimization.
    * Added alignment with `task_boundary` tool.
    * Added "Start Prompt" for O7 implementation.
* **README:** Updated Installation section to explicitly mention `.gemini/` folder copy.

---

### **v3.6.3 — O6a: Skill Structure Optimization** (Optimization)

#### **Changed**
* **Large Skills Refactoring:** Transformed 4 "heavy" skills (>4KB) to use `scripts/` + `examples/` pattern:
    * `architecture-format-extended`: Extracted inline templates to `examples/` (-65% size).
    * `skill-reverse-engineering`: Replaced NL traversal valid with `scan_structure.py` (-64% size).
    * `skill-update-memory`: Replaced NL git logic with `suggest_updates.py` (-63% size).
    * `skill-phase-context`: Removed redundant ASCII art layers (-49% size).

#### **Added**
* **Automation Scripts**: Added python automation for deterministic skill execution.
* **Infographic Update**: Added *Model Impact Analysis* and *References* to [O6_OPTIMIZATION_INFOGRAPHIC.md](archives/Infographics/O6_OPTIMIZATION_INFOGRAPHIC.md).

### **v3.6.2 — Skill Creator & Automation** (Feature)

#### **Added**
* **New Skill: `skill-creator`**: Meta-skill for creating new skills containing Anthropic standards + Project Tiers (verified structure).
    *   **Automation:** Includes `scripts/init_skill.py` for compliant scaffolding.
    *   **Validation:** Includes `scripts/validate_skill.py` for ensuring frontmatter and strict folder hygiene.

---

---

### **v3.6.1 — O6: Logic Integrity & Documentation Polish** (Post-Release Fix)

#### **Fixed**
* **Orchestrator Logic Integrity:** Restored missing stages 11-14 (Review/Fix cycle) and Workflows section in `01_orchestrator.md` to guarantee 100% logic parity with v3.2.
* **Documentation:** Consolidated `CHANGELOG.md` entry for v3.6.0 logic clarity.

#### **Updated**
* **Infographics:** Updated [Token Optimization Infographic](archives/Infographics/TOKEN_OPTIMIZATION_INFOGRAPHIC.md) and [O6 Optimization Infographic](archives/Infographics/O6_OPTIMIZATION_INFOGRAPHIC.md) with final v3.6.1 verification stats (-20% Orchestrator compression vs -36% initial estimate).

---

### **v3.6.0 — O5: Skill Tiers & O6: Standardization (Optimization)** (Stability)

#### **Added**
* **O6 Standard:** All 10 Agent Prompts (`01`–`10`) now use a unified 4-section schema with mandatory TIER 0 skills validation.
    * **New Names:** Standardized filenames to `_prompt.md`.
* **O5 Skill Tiers:** New document `System/Docs/SKILL_TIERS.md` — authoritative source for loading rules (TIER 0, 1, 2).

#### **Changed**
* **Skills Metadata:** All 28 skills now explicitly declare `tier: [0|1|2]`.
* **Agent Efficiency (O6):**
    * `04 Architect`: **-29%** tokens.
    * `06 Planner`: **-33%** tokens.
    * `08 Developer`: **-31%** tokens.
    * `01 Orchestrator`: **-20%** tokens (adjusted for guaranteed logic retention).
* **Safety (O6):**
    * Reviewers (`07`, `09`) and Auditor (`10`) now strictly enforce TIER 0 safety skills (+43% size for zero hallucinations).

#### **Verified**
* **VDD Audit:** All 10 standardized agents passed Logic Retention checks against v3.2 backups.
* **Localization:** All Russian prompts synchronized.

---


### **v3.5.5 — O2: Orchestrator Compression (Optimization)** (Token Savings)

#### **Added**
* **New Skill: `skill-orchestrator-patterns`**: Stage Cycle pattern and dispatch table for Orchestrator.
    * Reusable Init → Review → Revision flow pattern.
    * Stage Dispatch Table with agents, reviewers, and iteration limits.
    * Decision logic tables for common branching.
    * Expected result schemas for all agent types.
    * Exception documentation (Completion, Blocking).

#### **Changed**
* **`01_orchestrator.md`**: Compressed from 492 lines to 170 lines using patterns + dispatch table.
* **`Translations/RU/Agents/01_orchestrator.md`**: Updated with same compression logic.
* **`System/Docs/SKILLS.md`**: Added `skill-orchestrator-patterns` entry.

#### **Optimization Impact**
| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| File size | 11,195 bytes | 4,522 bytes | **-60%** |
| Lines | 492 | 170 | **-65%** |
| Tokens (~) | ~2,799 | ~1,130 | **-60%** |

> **Note:** All 14 scenarios preserved. Backup at `01_orchestrator_full.md.bak`.
>
> 📊 **See:** [Token Optimization Infographic](archives/Infographics/TOKEN_OPTIMIZATION_INFOGRAPHIC.md) for a visual breakdown of savings.

---

### **v3.5.4 — O1: Skill Phase Context (Optimization)** (Token Savings)

#### **Added**
* **New Skill: `skill-phase-context`**: Skill loading tiers protocol for optimized token consumption.
    * **TIER 0** (Always Load): `core-principles`, `skill-safe-commands`, `artifact-management` (~2,082 tokens).
    * **TIER 1** (Phase-Triggered): Phase→Skills mapping table for on-demand loading.
    * **TIER 2** (Extended): Specialized skills loaded only when explicitly requested.
    * Loading rules and flow diagram for agent reference.

#### **Changed**
* **`.gemini/GEMINI.md`**: Added explicit TIER 0 Skills section with bootstrap loading instructions.
* **`.cursorrules`**: Added explicit TIER 0 Skills section with bootstrap loading instructions.
* **`System/Docs/SKILLS.md`**: Added `skill-phase-context` entry in Core & Process section.

#### **Optimization Impact**
| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Baseline session load | ~9,772 tokens | ~2,082 tokens | **-79%** |
| TIER 1 skills | All loaded upfront | On-demand per phase | -3,000 to -5,000 tokens |

> **Note:** Automation (safe-commands) preserved — `mv`, `git`, tests still auto-run.

---

### **v3.5.3 — O3: architecture-format Split (Optimization)** (Token Savings)

#### **Added**
* **New Skill: `architecture-format-core`**: Minimal template for architecture documents (~150 lines, TIER 1).
    * Core sections: Task Description, Functional Architecture, System Architecture, Data Model (conceptual), Open Questions.
    * Default skill for most architecture updates.
    * Loading conditions table for decision-making.
* **New Skill: `architecture-format-extended`**: Full templates with examples (~400 lines, TIER 2).
    * Complete sections 3-10 with JSON samples, diagrams, and detailed templates.
    * Loaded only for: new systems, major refactors, complex requirements.
    * Cross-reference to core skill.

#### **Changed**
* **`04_architect_prompt.md`**: Updated with conditional loading table for core/extended skills.
* **`Translations/RU/Agents/04_architect_prompt.md`**: Updated with same conditional loading logic.
* **`System/Docs/SKILLS.md`**: Replaced single `architecture-format` entry with two tier-based entries.

#### **Token Savings**
| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Minor architecture update | ~2,535 | ~996 | **-60%** |
| New system / major refactor | ~2,535 | ~3,357 | +32% (more examples) |

---

### **v3.5.2 — Scripts Consolidation & Installation Simplification** (Refactoring)

#### **Changed**
* **Moved `scripts/` → `System/scripts/`**: Tool Dispatcher is now part of System folder.
    * **Installation simplified**: Only 2 folders to copy (`System/` + `.agent/`) instead of 3.
    * **Clear separation**: Framework files (`System/`) vs project files.

#### **Updated**
* **README.md / README.ru.md**: Simplified installation instructions and directory structure diagrams.
* **System/Docs/ORCHESTRATOR.md**: All import paths updated to `System.scripts.tool_runner`.
* **tests/test_tool_runner.py**: Updated import path.

---

### **v3.5.1 — Protocol Conflict Resolution & IDE-Agnostic Fixes** (Framework Bugfix)

#### **Fixed**
* **`skill-archive-task`**: Removed strict dependency on `generate_task_archive_filename` tool. Added manual fallback for filename generation using shell commands.
* **`skill-archive-task`**: Replaced hardcoded example IDs (`032`, `033`) with generic placeholders (`{OLD_ID}`, `{NEW_ID}`) to prevent agent confusion.
* **`artifact-management`**: Removed hardcoded absolute path in skill reference. Fixed outdated tool reference.
* **`artifact-management`**: Added "Dual State Tracking" section to resolve conflict between Agentic Mode internal `task.md` and project `docs/TASK.md`.
* **`core-principles`**: Added IDE-agnostic "Bootstrap Protocol" (Section 0) instructing agents that `<user_rules>` injected by IDE **override** internal defaults.

#### **Root Causes Addressed**
| Issue | Solution |
|-------|----------|
| Context Blindness | Bootstrap Protocol now clarifies priority |
| Internal vs Project `task.md` | Dual State Tracking section added |
| Missing Tool Blocker | Manual fallback in skill-archive-task |
| Hardcoded Examples | Replaced with `{PLACEHOLDER}` syntax |

---

### **v3.5.0 — Memory Automation** (Task 035)


#### **Added**
* **New Skill: `skill-update-memory`**: Auto-update `.AGENTS.md` files based on code changes.
    * Analyzes `git diff --staged` to detect new, modified, and deleted files.
    * Strict filtering: ignores `*.lock`, `dist/`, `migrations/`, config files.
    * Human knowledge preservation: protects `[Human Knowledge]` sections.
    * Integration points: `09_agent_code_reviewer`, `04-update-docs`.
* **New Skill: `skill-reverse-engineering`**: Regenerate architecture documentation from codebase analysis.
    * Iterative strategy: folder-by-folder analysis → local summaries → global synthesis.
    * Updates `ARCHITECTURE.md` and discovers hidden knowledge for `KNOWN_ISSUES.md`.
    * Context overflow mitigation: never loads entire codebase at once.

#### **Documentation**
* Updated `System/Docs/SKILLS.md` with new skills in Core & Process section.
* Updated roadmap in `Backlog/potential_improvements-2.md`.

#### **Integration**
* `09_agent_code_reviewer.md`: Added `skill-update-memory` to verify `.AGENTS.md` updates.
* `04-update-docs.md` workflow: Added references to both skills for structured docs maintenance.
* `README.md` / `README.ru.md`: Updated "Reverse Engineering" section with skill-based prompts.

---

### **v3.4.2 — Framework Documentation Consistency Fixes** (Task 034 Phase 3)

#### **Fixed**
* **Broken References**: Identified and fixed stale references to moved files (`System/Docs/` vs `docs/`) in `README.md`, `.cursorrules`, and agent prompts.
* **Path Error**: Fixed incorrect path in `Translations/RU/Agents/01_orchestrator.md` (`docs/ORCHESTRATOR.md`) to align with user project structure.
* **Typos**: Corrected formatting errors in Russian Orchestrator prompt.

#### **Improved**
* **Installation Instructions**: Clarified `README.md` and `README.ru.md` to explicitly instruct users to copy `System/Docs/ORCHESTRATOR.md` to their local `docs/` folder, preventing path conflicts for distributed agents.

---

### **v3.4.1 — Workflow Integrity & Artifact Fixes** (Task 034 Phase 2)

#### **Fixed**
* **Workflow "Phantom" References**: Fixed critical bugs in `base-stub-first.md` (and consequently `vdd-enhanced`) which referenced non-existent workflows (`/analyst-task`, etc.) instead of valid ones. This restored the mandatory Analysis/Architecture phases.
* **VDD Adversarial Loop**: Corrected `vdd-adversarial.md` to use valid workflow calls (`/03-develop-single-task`) instead of non-existent actions (`/developer-fix`).
* **Artifact Consistency**: Created missing `docs/KNOWN_ISSUES.md` placeholder to satisfy workflow requirements.
* **Security Audit**: Clarified `security-audit.md` instructions regarding `.AGENTS.md` updates to handle missing files gracefully.

#### **Verified**
* Performed a full audit of all 14 workflow definitions to ensure every cross-reference points to an existing file.

### **v3.4.0 — VDD Multi-Adversarial** (Task 034)

#### **Added**
* **New Skill: `skill-adversarial-security`**: OWASP security critic in adversarial/sarcastic style.
    * Injection attacks (SQLi, XSS, Command Injection, Path Traversal).
    * Authentication & Authorization flaws.
    * Secrets exposure (hardcoded keys, passwords, API tokens).
    * Input validation failures.
* **New Skill: `skill-adversarial-performance`**: Performance critic in adversarial/sarcastic style.
    * N+1 queries, missing indexes.
    * Memory leaks, unbounded allocations.
    * Blocking operations in async code.
    * Algorithm complexity issues.
* **New Workflow: `/vdd-multi`**: Sequential execution of multiple specialized adversarial critics.
    * Phase 1: General logic review (`skill-vdd-adversarial`).
    * Phase 2: Security review (`skill-adversarial-security`).
    * Phase 3: Performance review (`skill-adversarial-performance`).

#### **Documentation**
* Updated `docs/SKILLS.md` with new VDD skills.
* Updated `Backlog/potential_improvements-2.md` with v3.4 status.

---

### **v3.3.2 — Auto-Tests for Archiving Protocol** (Task 033 Phase 2)

#### **Added**
* **Archive Protocol Tests**: 15 new automated tests for the 8 archiving scenarios using VDD adversarial approach:
    * Core scenarios: new task with existing TASK.md, no TASK.md, refinement, ID conflict.
    * VDD adversarial: missing Meta Information, malformed Task ID, permission denied, tool error simulation.
* **Testable Protocol Module**: `archive_protocol.py` — Python implementation of the 6-step archiving protocol for unit testing.
* **Test Fixtures**: 3 TASK.md variants (`task_with_meta.md`, `task_without_meta.md`, `task_malformed_id.md`).

#### **Verification**
* 44 total tests pass (29 existing + 15 new).
* Run: `cd .agent/tools && python -m pytest test_archive_protocol.py -v`

---

### **v3.3.1 — Portability, VDD Audit & UX Improvements** (Task 033)

#### **Fixed**
* **Circular Logic in Safe Commands**: Eliminated the documentation loop. Added explicit copy-paste list to `skill-safe-commands` for IDE configuration.
* **Agent Hallucinations**: Corrected `01_orchestrator.md` references to non-existent tools (`git_ops` -> `git_status`, etc.) revealed by VDD Audit.
* **IDE Configuration**: Fixed documentation for "Allow List" to address `mv` command token matching issues.
* **Portability**: Made `docs/ORCHESTRATOR.md` reference optional (`if available`) to prevent errors in lightweight projects or when transferring agents.

#### **Refactored**
* **Mandatory Skill Pattern**: Enforced `skill-safe-commands (Mandatory)` across all agents to ensure native tool safety.
* **Developer Guidelines**: Introduced explicit "Tooling Protocol" enforcing `native tools` (like `run_tests`) over shell commands.

### **v3.3.0 — Skill Encapsulation & Safe Commands Centralization** (Task 033)

#### **Added**
* **New Skill: `skill-archive-task`**: Complete, self-contained protocol for archiving `docs/TASK.md`. Single source of truth for archiving logic, eliminating duplication across 7+ files.
    * 6-step archiving protocol with decision logic (new vs refinement).
    * Error handling for missing Meta Information.
    * Validation and rollback guidance.
* **New Skill: `skill-safe-commands`**: Centralized list of commands safe for auto-execution without user approval.
    * 7 command categories: read-only, file info, git read, archiving, directory ops, tool calls, testing.
    * Pattern matching rules for IDE integration.
    * IDE-specific instructions (Antigravity/Gemini, Cursor).

#### **Refactored**
* **Duplication Eliminated**: Reduced archiving protocol duplication from 7 files to 1:
    * `.gemini/GEMINI.md` → skill reference
    * `.cursorrules` → skill reference
    * `System/Agents/02_analyst_prompt.md` → skill reference
    * `System/Agents/01_orchestrator.md` → skill reference
    * `System/Agents/00_agent_development.md` → skill reference (30 lines → 14)
    * `.agent/skills/artifact-management/SKILL.md` → skill import
    * `.agent/workflows/01-start-feature.md` → skill reference
* **Safe Commands Centralized**: All 4 files with duplicate Safe Commands now reference `skill-safe-commands`.

#### **Documentation**
* Updated `docs/SKILLS.md` with new skills.
* Added Implementation Summary to `docs/TASK.md` (Task 033).

---

### **v3.2.5, v3.2.6 — Task Archive ID Tool & Auto-Run Protocol**

#### **Added**
* **New Tool: `generate_task_archive_filename`**: Deterministic tool for generating unique sequential IDs when archiving tasks. Eliminates manual ID assignment errors and ID gaps.
    * Auto-generates next available ID (`max + 1` strategy).
    * Validates proposed IDs and handles conflicts (`allow_correction` flag).
    * Normalizes slugs (lowercase, dashes).
    * Future-proofed: supports IDs beyond 999 (regex `\d{3,}`).
* **Dispatcher Integration**: Tool registered in `scripts/tool_runner.py` for native execution.
* **Unit Tests**: 29 comprehensive tests covering all use cases.

#### **Improved**
* **Safe Commands Protocol**: Expanded list of auto-run commands in `skill-artifact-management` and Orchestrator prompt:
    * Read-only: `ls`, `cat`, `head`, `tail`, `find`, `grep`, `tree`, `wc`
    * Git read: `git status`, `git log`, `git diff`, `git show`, `git branch`
    * Archiving: `mv docs/TASK.md docs/tasks/...`
    * Tools: `generate_task_archive_filename`, `list_directory`, `read_file`
* **Agent Prompts**: Updated Orchestrator (`01`) and Analyst (`02`) with explicit tool usage for archiving.

#### **Documentation**
* Updated `docs/ARCHITECTURE.md`, `docs/ORCHESTRATOR.md`, and `docs/SKILLS.md`.
* Added Python installation requirements to README.
* Consolidated `docs/USER_TOOLS_GUIDE.md` into `docs/ORCHESTRATOR.md` (removed duplicate file).
* Synchronized `.gemini/GEMINI.md` and `.cursorrules` with v3.2.5+ protocol.

---

### **v3.2.4 — Workflow Documentation Enhancement**

#### **Added**
* **Workflow Call Sequences**: Added comprehensive "Getting Started" section to `docs/WORKFLOWS.md` with:
    * One-Step vs Multi-Step approach comparison table.
    * TDD pipeline examples (`base-stub-first`, `01`→`02`→`03/05`→`04`) with pros/cons.
    * VDD pipeline examples (`vdd-enhanced`, `full-robust`, VDD atomic steps) with pros/cons.
    * Decision flowchart (Mermaid diagram) for choosing the right approach.
    * Quick reference summary table for common scenarios.

---

### **v3.2.3 — Archiving Protocol Refinement**

#### **Changed**
* **Archiving Scope**: Removed mandatory archiving of `docs/PLAN.md`. Only `docs/TASK.md` requires archiving before new tasks.
* **Documentation**: Updated version references in `README.md` (v3.1→v3.2) and `docs/ORCHESTRATOR.md` (v3.1.2→v3.2.2).

#### **Improved**
* **Auto-Run Protocol**: Added explicit `SAFE TO AUTO-RUN` instruction to Analyst prompt and `skill-artifact-management`. The archive command for `docs/TASK.md` no longer requires user approval.

---

### **v3.2.2 — System Integrity & Archiving Protocols**

#### **Fixed**
* **Critical Restoration**: Restored missing (empty) Russian agent prompts (`Translations/RU/Agents/01, 02, 04, 06`) using v3.2.0 logic.
* **Data Loss Prevention**: Fixed a critical gap in `skill-artifact-management` where the "Archiving Protocol" was missing.
* **Protocol Enforcement**: Updated Orchestrator (`01`), Analyst (`02`), and Planner (`06`) to strictly enforce archiving of `docs/TASK.md` and `docs/PLAN.md` before overwriting.

#### **Improved**
* **System Prompts**: Synchronized `.gemini/GEMINI.md` and `.cursorrules` with the Tool Execution Protocol (v3.2.0), explicitly enabling native tool calling.
* **Consistency**: Completed a full audit of the prompt system to ensure zero contradictions between System and Agent prompts.

---

### **v3.2.1 — Skills System Optimization**

#### **Added**
* **Skills**:
    * `skill-task-model`: Standardized examples and rules for `docs/TASK.md`.
    * `skill-planning-format`: Standardized templates for `docs/PLAN.md` and Task Descriptions.
* **Rules**: Added `.agent/rules/localization-sync.md` to enforce bilingual documentation updates.

#### **Improved**
* **Prompt Engineering**: Significantly reduced the size of Analyst (`02`), Architect (`04`), and Planner (`06`) agents by extracting static templates into the Skills System.
* **Localization**: Synced `README.ru.md` with English version (added Tool Calling section).
* **Russian Agents**: Updated `Translations/RU/Agents/*.md` to match v3.2.0 optimizations (Tool Calling logic, Skills extraction, Path Hygiene).

---

### **v3.2.0 — Structured Tool Calling & Path Hygiene**

#### **Added**
* **Tool Execution Subsystem**: The Orchestrator now natively supports structured tool calling (Function Calling).
* **New Skills**:
    * `skill-task-model`: Standardized examples and rules for `docs/TASK.md`.
    * `skill-planning-format`: Standardized templates for `docs/PLAN.md` and Task Descriptions.
    * `skill-architecture-format`: Consolidated architecture document templates.
* **Standard Tools**: Added `run_tests`, `git_ops`, `file_ops` to `.agent/tools/schemas.py`.
* **Documentation**: Added `docs/ORCHESTRATOR.md`.

#### **Improved**
* **Prompt Engineering**: Significantly reduced the size of Analyst (`02`), Architect (`04`), and Planner (`06`) agents by extracting static templates into the Skills System.
* **Maintenance**: Centralized critical document templates (TASK, PLAN, Architecture) in `.agent/skills/` to ensure consistency and easier updates.
* **Workflows**: Refactored `03-develop-task` -> `03-develop-single-task` and updated `base-stub-first`.

#### **Changed**
* **Test Reports**: Standardized storage location. Reports moved from `docs/test_reports` to `tests/tests-{Task ID}/`.
* **Path Enforcement**: Updated all Agent prompts to use strictly project-relative path examples.
* **Agents**: Updated Orchestrator, Developer, and Reviewers to enforce new protocols.

#### **Fixed**
* **Cleanup**: Removed legacy `docs/test_reports` directory.

---

### **v3.1.3 — Skills Cleanup & Cursor Integration Fix**

#### **Changed**
* **Project Structure**: Removed redundant `.cursor/skills` directory to eliminate duplication.
* **Cursor Integration**: Updated `README.md` to instruct users to simply symlink `.cursor/skills` -> `.agent/skills`, ensuring a single source of truth.
* **Orchestrator**: Updated `.cursorrules` to reference the correct symlinked path and fixed legacy "tz" terminology in comments.
* **Workflows**: Archived `docs/TASK.md` to `docs/tasks/task-014-cleanup-skills.md`.

---

### **v3.1.2 — Analyst Protocol & YAML Fixes**

#### **Fixed**
* **Skills**: Fixed YAML syntax error in `core-principles` skill (quoted description).

#### **Improved**
* **Analyst Agent**: Added "CRITICAL PRE-FLIGHT CHECKLIST" to `02_analyst_prompt.md` to strictly enforce:
    * Archiving of existing `docs/TASK.md` before starting new work.
    * Mandatory inclusion of Section 0 (Meta Information: Task ID, Slug).
* **Skills**: Updated `skill-requirements-analysis` to mark Meta Information as **MANDATORY**.
* **Documentation**: Enforced "Relative Paths Only" rule for Artifacts in `skill-documentation-standards` and `06_agent_planner.md`.

#### **Refactored**
* **Skills**: Audited and fixed YAML frontmatter in `code-review-checklist`, `developer-guidelines`, `security-audit` and `artifact-management`.
* **PLAN.md**: Converted absolute paths to relative paths.

---

### **v3.1.1 — Plan & Structure Fixes**

#### **Fixed**
* **Agent Prompts**: Corrected `plan.md` file path references to `docs/PLAN.md` in Planner and Reviewer agents (both English and Russian versions).
* **Agent Prompts**: Corrected `open_questions.md` file path references to `docs/open_questions.md` in Planner agent.
* **Project Structure**: Removed the `verification/` directory to comply with `docs/ARCHITECTURE.md`.

---

### **v3.1.0 — Global "TZ" to "TASK" Refactor**

#### **Changed**
* **Terminology**: Global refactoring of "TZ" (Техническое Задание) to "TASK" (Task/Specification) to improve internationalization and consistency.
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

### **v2.0.0 — Public Release: Multi-Agent Software Development System**

#### **Key Highlights**

* **9-Agent Ecosystem**: A comprehensive orchestration of **9 specialized agents** (Analyst, Architect, Planner, Developer, Reviewer, Orchestrator, and others) covering the full SDLC.
* **VDD (Verification-Driven Development)**: Built-in adversarial testing with the **Sarcasmotron** agent to ensure logic consistency and high reliability.
* **Stub-First Methodology**: Strict TDD-inspired flow where architecture, E2E tests, and stubs are defined before a single line of production code is written.
* **Long-Term Memory**: Advanced artifact management using `.AGENTS.md` and structured logs to maintain context across long development sessions.
* **Native IDE Integration**: Seamless support for **Antigravity** (`.gemini/GEMINI.md`) and **Cursor** (`.cursorrules`).

#### **🚀 Quick Start**

1. **Copy agents**: Move the `/System/Agents` folder into your project root.
2. **Configure IDE**: Copy `.gemini/GEMINI.md` (for Antigravity) or `.cursorrules` (for Cursor) to your project root to enable agent instructions.
3. **Initialize**: Use the `02_analyst_prompt.md` prompt to start the session.
4. **Follow Guidelines**: Refer to the **Pre-flight Check** in the README for the full workflow.
