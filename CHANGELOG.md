<!--
## [Unreleased]

### 🇺🇸 English
#### Added
- ...

#### Changed
- ...

#### Fixed
- ...

### 🇷🇺 Русский
#### Добавлено
- ...

#### Изменено
- ...

#### Исправлено
- ...
-->

## 🇺🇸 English Version (Primary)

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
* **Documentation:** Updated `README.md`, `README.ru.md`, and `docs/ARCHITECTURE.md` to reflect the new configuration structure.

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
* **New Skill: `skill-reverse-engineering`**: Regenerate architecture documentation from codebase.
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
* **Skills**: Audited and fixed YAML frontmatter in `code-review-checklist`, `developer-guidelines`, `security-audit`, and `artifact-management`.
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
* **Artifacts**: Renamed `docs/TZ.md` to `docs/TASK.md`.
* **System Agents**: Updated all agent prompts (Analyst, Reviewer, Architect, etc.) to use "TASK" terminology.
* **Skills**: Renamed `skill-tz-review-checklist` to `skill-task-review-checklist`.
* **Documentation**: Updated `README.md`, `WORKFLOWS.md`, `SKILLS.md`, and `.gemini/GEMINI.md` to reflect the new standard.

#### **Fixed**
* **Consistency**: Eliminated mixed usage of "TZ" and "Task Specification" across the framework.
* **Localization**: Aligned Russian translations (`Translations/RU`) with the new global standard.
* **Workflows**: Fixed a critical bug in `01-start-feature` and `vdd-01-start-feature` where the previous `docs/TASK.md` was overwritten instead of archived. Added explicit archiving step.

#### **Migration Guide**
To upgrade from v3.0.x to v3.1.0:
1. **Rename**: `mv docs/TZ.md docs/TASK.md`
2. **Update Agents**: Replace `System/Agents/` with the new version (Note: `03_tz_reviewer_prompt.md` -> `03_task_reviewer_prompt.md`).
3. **Update Skills**: Replace `.agent/skills/` with the new version.

---

### **v3.0.3 — Documentation Sync & Artifacts**

#### **Fixed**
* **Documentation**: Replaced obsolete references to `UNKNOWN.md` with `docs/open_questions.md` in `README.md` and `README.ru.md` to align with actual Agent prompts.

#### **Added**
* **Artifacts**: Added missing `docs/open_questions.md` template for tracking unresolved issues.

---

### **v3.0.2 — Skills Doc & Examples**
  
#### **Added**
* **Examples**:
    * `examples/skill-testing/test_skill.py`: Python script for isolated skill testing.
    * `examples/skill-testing/n8n_skill_eval_workflow.json`: n8n workflow for skill evaluation (with Sticky Notes hints).
* **Skills Documentation**:
    * Added "Dynamic Loading", "Isolated Testing", and "Best Practices" sections to `docs/SKILLS.md`.
    * Added explicit links to example files.

---

### **v3.0.1 — Skills System Refinement**

#### **Improved**
* **Skills Documentation**:
    * Expanded `docs/SKILLS.md` with "How it Works", "Principles", and official documentation links.
    * Added explicit "Used By Workflows" and "Used By Agents" matrices.
    * Clarified **Adversarial Agent** as a "Virtual Persona" in VDD mode.
* **README**:
    * Restored missing "Agent Team" and "System Prompt" sections.
    * Fixed incomplete instructions for Skills System installation.

---

### **v3.0.0 — Skills System & Global Localization**

#### **Major Changes**
* **Skills System**: Introduced a modular `.agent/skills/` library. Agents now dynamically load capabilities (Skills) instead of having monolithic prompts. This reduces prompt size and increases maintainability.
* **Localization Architecture**: New `Translations/` directory structure. Full support for switching between English and Russian contexts by swapping agent/skill files.
* **Documentation**:
    * Added `docs/SKILLS.md`: Comprehensive catalog of all available skills.
    * Updated `README.md`, `README.ru.md`, `docs/ARCHITECTURE.md` to reflect the new structure.

#### **Removed**
* **Legacy directories**: Removed `/System/Agents_ru` (replaced by `Translations/RU`).

---

### **v2.1.3 — Documentation & Workflow Consistency**

#### **Fixed**
* **ARCHITECTURE.md**: Updated to reflect the actual project structure (added `.agent` and `docs` directories).
* **Workflows**: `full-robust.md` now explicitly calls `/security-audit` (Agent 10) instead of a placeholder.

### **v2.1.2 — Fix .AGENTS.md Generation Bug**

#### **Fixed**
* **Prompt Conflict**: Resolved a conflict where the Developer agent would skip creating `.AGENTS.md` files because the Planner didn't explicitly task them and the "no extra files" rule completely forbade them.
* **Planner Agent**: Now mandates `.AGENTS.md` creation for new directories.
* **Developer Agent**: Explicitly allowed to create `.AGENTS.md` as an exception, even if not listed in the task.

### **v2.1.1 — Workflow Verification & Safety**

#### **Added**
* **Mandatory Verification**: All core workflows (Standard & VDD) now include explicit verification loops (Analyst -> TZ Review, Architect -> Arch Review, etc.).
* **Safety Limits**: Implemented a **Max 2 Retries** mechanism to prevent infinite Doer-Reviewer loops.

---

### **v2.1.0 — Nested Workflows and Security Audit**

#### **Added**
* **Nested Workflows Support**: New ability to call workflows from within other workflows (e.g., `Call /base-stub-first`).
* **New Workflows**:
  * `/base-stub-first`: Foundational stub-first pipeline.
  * `/vdd-adversarial`: Isolated adversarial loop.
  * `/vdd-enhanced`: Nested combination of Stub-First + VDD.
  * `/full-robust`: Full pipeline including future Security Audit steps.
  * `/security-audit`: Standalone security vulnerability assessment workflow.
* **New Roles**:
  * **10_security_auditor**: Specialized agent for OWASP/Security scanning.
* **Documentation**: Updated `WORKFLOWS.md`, `README.md`, and `GEMINI.md` to reflect these changes.

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

---

## 🇷🇺 Русская версия

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

1. **Копирование агентов**: Перенесите папку `/System/Agents` в корень вашего проекта.
2. **Настройка IDE**: Скопируйте `.gemini/GEMINI.md` (для Antigravity) или `.cursorrules` (для Cursor) в корень проекта.
3. **Инициализация**: Используйте промпт `02_analyst_prompt.md` для запуска процесса.
4. **Инструкции**: Следуйте разделу **Pre-flight Check** в README.
