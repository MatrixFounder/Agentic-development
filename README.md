**🇺🇸 English** | [🇷🇺 Русский](README.ru.md)

> [!NOTE]
> This is the primary version. Translations may lag behind.

# Multi-Agent Software Development System v3.9.5

This framework orchestrates a multi-agent system for structured software development. It transforms vague requirements into high-quality code through a strict pipeline of specialized agents (Analyst, Architect, Planner, Developer, Reviewer, Security Auditor).

The methodology combines two key approaches (see [Comparison](System/Docs/TDD_VS_VDD.md)):
- **TDD (Test-Driven Development)**: The "Stub-First" strategy ensures that tests are written and verified against stubs before actual implementation begins. [Read more](System/Docs/TDD.md).
- **VDD (Verification-Driven Development)**: A high-integrity mode where an adversarial agent proactively challenges the plan and code to eliminate hallucinations and logic errors before they are committed. [Read more](System/Docs/VDD.md).

![Framework architecture](/Attachments/Framework_architecture_v2.png)

## 📋 Table of Contents
- [Installation & Setup](#-installation--setup)
  - [1. Copy Framework Folders](#1-copy-framework-folders)
  - [2. Choose Your AI Assistant](#2-choose-your-ai-assistant)
  - [3. Installation Requirements (Python)](#3-installation-requirements-python)
- [System Overview](#-system-overview)
  - [Directory Structure](#directory-structure)
  - [Meta-System Prompt](#-meta-system-prompt-00_agent_developmentmd)
  - [The Agent Team (Roles)](#-the-agent-team-roles)
  - [The Product Team (Roles)](#-the-product-team-roles)
  - [Skills System](#-skills-system)
- [Workspace Workflows](#-workspace-workflows)
  - [Quick Start](#quick-start)
  - [Variants](#variants)
- [How to Start Development](#-how-to-start-development-step-by-step-plan)
  - [Phase 0: Product Discovery](#phase-0-product-discovery-optional)
  - [Stages 1-5](#stage-1-pre-flight-check)
- [Artifact Management](#-artifact-management)
- [What to do with .AGENTS.md files?](#-what-to-do-with-agentsmd-files)
- [How to prepare for future iterations?](#-how-to-prepare-for-future-iterations)
- [Reverse Engineering](#-reverse-engineering-if-documentation-is-outdated)
- [Starter Prompts](#-starter-prompt-templates)
- [Migration Guide](#-migration-from-older-versions)
- [Integration with Cursor IDE](#-integration-with-cursor-ide-agentic-mode)


## 📁 Installation & Setup

### 1. Copy Framework Folders

Copy these folders to your project root:

| Folder | Required | Description |
|--------|----------|-------------|
| `System/` | ✅ **Yes** | Agent Personas, Docs, and Tool Dispatcher |
| `.agent/` | ✅ **Yes** | Skills, Workflows, and Tool definitions |

```bash
# Installation
cp -r /path/to/framework/System ./
cp -r /path/to/framework/.agent ./
cp /path/to/framework/GEMINI.md ./ # (For Antigravity)
```

> [!NOTE]
> The Tool Execution Subsystem is included in `System/scripts/`:
> - `System/scripts/tool_runner.py` — Dispatcher (entry point)
> - `.agent/tools/` — Tool logic and schemas

### 2. Choose Your AI Assistant

#### 🔵 Option A: Cursor IDE
To configure Cursor for this workflow:
1.  **Context Rules**: Copy `AGENTS.md` to your project root.
2.  **Skills**: Create a symbolic link to enable native skill detection:
    ```bash
    ln -s .agent/skills .cursor/skills
    ```
    *   *Note:* This allows Cursor to index the skills while keeping `.agent/skills` as the single source of truth.

#### 🟣 Option B: Antigravity (Native)
Antigravity supports this architecture out-of-the-box:
1.  **Configuration**: Copy `GEMINI.md` to your project root (this is the system prompt).
2.  **Skills**: Ensure `.agent/skills/` directory exists. Antigravity automatically loads skills from here.
3.  **Workflows**: (Optional) Use `.agent/workflows/` for automated sequences.
4.  **Auto-Run Permissions**: To enable autonomous command execution, add the following to **Allow List Terminal Commands** in IDE Settings:
    ```text
    ls,cat,head,tail,find,grep,tree,wc,stat,file,du,df,git status,git log,git diff,git show,git branch,git remote,git tag,mv docs/TASK.md,mv docs/PLAN.md,mkdir -p docs,mkdir -p .agent,mkdir -p tests,python -m pytest,python3 -m pytest,npm test,npx jest,cargo test
    ```

### 3. Installation Requirements (Python)
If you plan to use the **Tool Execution Subsystem** (native tools), you need Python 3.9+ with the following packages:

```bash
# Required for tool execution
pip install pytest  # For run_tests tool

# Optional: for AI orchestration (if using custom scripts)
pip install openai  # OpenAI API client
pip install python-dotenv  # Environment variables
```

**Minimal Setup** (read-only tools work without dependencies):
```bash
# No installation needed for basic tools like:
# - generate_task_archive_filename
# - list_directory
# - read_file
# These use Python's standard library only.
```

---

## 🏗 System Overview

### Directory Structure
```text
project-root/
├── AGENTS.md                    # [Cursor] Context & Rules
├── GEMINI.md                    # [Antigravity] System Config
├── .agent/
│   │   ├── ...
│   │   └── skill-product-*      # [Product] Strategy, Vision, Handoff
│   ├── workflows/               # [Common] Workflow Library
│   └── tools/                   # [Common] Tool Logic & Schemas
├── System/
│   ├── Agents/                  # [Common] Agent Personas (00-10, p00-p04)
│   ├── Docs/                    # [Common] Framework Documentation
│   └── scripts/                 # [Common] Tool Dispatcher
│       └── tool_runner.py
└── src/                           # Your Source Code
```

### 🔑 Meta-System Prompt (00_agent_development.md)
The file `00_agent_development.md` serves as the **Meta-System Prompt** for Cursor.
It defines global principles (Skill Tiers, Task Boundaries) and **SHOULD** be included in the context for manual agent calls.
For Antigravity, this logic is handled natively via `GEMINI.md`.

### 🤖 The Agent Team (Roles)

| Role | File | Responsibility |
|------|------|----------------|
| **Orchestrator** | `01_orchestrator.md` | Project Manager. Dispatches tasks, manages the pipeline. |
| **Analyst** | `02_analyst_prompt.md` | Requirements elicitation, TASK creation. |
| **TASK Reviewer** | `03_task_reviewer_prompt.md` | Quality control for Technical Specifications. |
| **Architect** | `04_architect_prompt.md` | System design, database schema, API definition. |
| **Arch Reviewer** | `05_architecture_reviewer_prompt.md` | Validates verification of architectural decisions. |
| **Planner** | `06_agent_planner.md` | Breaks down implementation into atomic steps (Stub-First). |
| **Plan Reviewer** | `07_agent_plan_reviewer.md` | Ensures the plan is logical and testable. |
| **Developer** | `08_agent_developer.md` | Writes code (Stubs -> Tests -> Implementation). |
| **Code Reviewer** | `09_agent_code_reviewer.md` | Final code quality check. |
| **Security Auditor** | `10_security_auditor.md` | Security vulnerability assessment and reporting. |

### 🚀 The Product Team (Roles)

| Role | File | Responsibility |
|------|------|----------------|
| **Product Orch** | `p00_product_orchestrator.md` | Dispatches product tasks to Strategy/Vision/Director. |
| **Strategic Analyst** | `p01_strategic_analyst_prompt.md` | Market Research, TAM/SAM/SOM, Competitive Analysis. |
| **Product Analyst** | `p02_product_analyst_prompt.md` | Product Vision, User Stories, Backlog Prioritization (WSJF). |
| **Director** | `p03_product_director_prompt.md` | **Quality Gate**. Approves BRD with cryptographic hash. |
| **Solution Arch** | `p04_solution_architect_prompt.md` | Feasibility Check, ROI, Solution Blueprint. |

### 📊 How the System Prompt is Loaded

| Tool | System Prompt | Loading Method |
|------|---------------|----------------|
| **Cursor IDE** | `00` + role (01-10) | Manually or via `AGENTS.md` |
| **Antigravity** | `GEMINI.md` (includes global principles) | **Automatically (Native)**. Manual concatenation of `00` is not required. |


### 📚 Skills System
Version 3.0 introduces a modular **Skills System** that separates "Who" (Agent) from "What" (Capabilities).
- **Reduces Prompt Size**: Agents only load what they need.
- **Shared Logic**: Improvements in a skill benefit all agents.

**Structure:**
- `.agent/skills/` — Markdown instructions and templates.
- `.agent/tools/` — Native tool definitions and schemas.
- `System/scripts/` — Execution engine for tools.

**Capabilities**: Run tests, Git operations, File I/O, Archiving.

**[>> View Full Skills Catalog <<](System/Docs/SKILLS.md)**
**[>> Orchestrator & Tools Guide <<](System/Docs/ORCHESTRATOR.md)**

By default, the system uses English prompts. To use **Russian** context:
1.  Copy content from `Translations/RU/Agents` to `System/Agents`.
2.  Copy content from `Translations/RU/Skills` to `.agent/skills`.

---

## ⚡ Workspace Workflows

To simplify launching different development modes, the project provides special **Workflows**.
Detailed description of all workflows: [WORKFLOWS](System/Docs/WORKFLOWS.md).

### Quick Start
You can run a workflow simply by asking the agent:

- **Product Discovery (New):**
  - "Start Product Discovery" -> runs `/product-full-discovery` (Full pipeline)
  - "Just the vision" -> runs `/product-quick-vision` (Fast track)
  - "Analyze market" -> runs `/product-market-only` (Strategy only)

- **Standard Mode (Stub-First):**
  - "Start feature X" -> runs `01-start-feature.md`
  - "Plan implementation" -> runs `02-plan-implementation.md`
  - "Develop task" -> runs `03-develop-single-task.md` (for single) or `05-run-full-task.md` (for loop)

- **VDD Mode (Verification-Driven Development):**
  - "Start feature X in VDD mode" -> runs `vdd-01-start-feature.md`
  - "Develop task in VDD mode" -> runs `vdd-03-develop.md` (Adversarial Loop)

### Variants
1. **Standard**: Basic mode, focused on speed and structure (Stub-First).
2. **VDD (Verification-Driven)**: High-reliability mode using an "Adversarial Agent" (Sarcasmotron) that harshly criticizes code.
3. **Nested & Advanced**:
   - **VDD Enhanced** (`/vdd-enhanced`): Runs Stub-First then VDD Refinement.
   - **VDD Multi-Adversarial** (`/vdd-multi`): Sequential 3-critic verification (Logic → Security → Performance).
   - **Full Robust** (`/full-robust`): Runs VDD Enhanced then Security Audit.

---

## 🚀 How to Start Development (Step-by-Step Plan)

This process will take you from an idea to finished code in the repository.

### Phase 0: Product Discovery (Optional)
**Agents `p00`-`p04`** ensure you are building the *right* product before you build it *right*.

1. **Orchestrator (p00):** Decides if you need "Market Research" or just a "Quick Vision".
2. **Strategy (p01):** Calculates TAM/SAM/SOM and checks competitors.
3. **Vision (p02):** Defines the "Soul" of the product and User Stories.
4. **Director (p03):** **Adversarial Gatekeeper**. Rejects fluff. Signs off with a cryptographic hash.
5. **Solution (p04):** Converts Vision to `SOLUTION_BLUEPRINT.md` (ROI, UX Flows).
6. **Handoff:** Compiles `BRD.md` and triggers the Technical Phase.

**[>> Read the full Product Development Playbook <<](System/Docs/PRODUCT_DEVELOPMENT.md)**

### Stage 1: Pre-flight Check
1. **Initialization:** Ensure you are in the project root.
2. **Reconnaissance:** If the project already exists, ensure `.AGENTS.md` files exist in root folders. If not, create empty or basic ones so agents have somewhere to write.

### Stage 2: Analysis and Design
1. **Analyst (02_analyst_prompt.md):**
   - Provide the agent with the idea/task.
   - The agent studies the project structure (Reconnaissance).
   - Result: **Technical Specification (TASK)**.
2. **TASK Review (03_task_reviewer_prompt.md):**
   - Check the TASK for completeness and consistency.
3. **Architect (04_architect_prompt.md):**
   - Based on the TASK, the agent designs the architecture.
   - Result: **Architecture Document** (`docs/ARCHITECTURE.md`) - (classes, databases, APIs).
4. **Architecture Review (05_architecture_reviewer_prompt.md):**
   - Approve the architecture before planning.

### Stage 3: Planning (Stub-First)
1. **Planner (06_agent_planner.md):**
   - The agent creates a work plan.
   - **IMPORTANT:** The plan must follow the **Stub-First** strategy:
     - Task X.1 [STUB]: Create structure and stubs + E2E test on hardcode.
     - Task X.2 [IMPL]: Implement logic + update tests.
2. **Plan Review (07_agent_plan_reviewer.md):**
   - Check that Stub-First principle is observed. If not, send for revision.

### Stage 4: Development (Implementation Cycle)
For each pair of tasks in the plan (Stub -> Impl):

1. **Developer (08_agent_developer.md) — STUB Phase:**
   - Creates files, classes, and methods.
   - Methods return `None` or hardcode (e.g., `return True`).
   - Writes an E2E test that passes on this hardcode.
   - **Documentation First:** Creates/updates `.AGENTS.md` in affected folders.
2. **Code Review (09_agent_code_reviewer.md) — STUB Phase:**
   - Checks: "Are these really stubs? Does the test pass?".
3. **Developer (08_agent_developer.md) — IMPLEMENTATION Phase:**
   - Replaces hardcode with real logic.
   - Updates tests (removes hardcode asserts, adds real checks).
   - **Anti-Loop:** If tests fail 2 times in a row with the same error — stop and analyze.
4. **Code Review (09_agent_code_reviewer.md) — IMPLEMENTATION Phase:**
   - Checks: "No stubs left? Is code clean? Do tests pass?".

### Stage 5: Completion and Commit
1. **Final Check:** Run the full test suite (Regression Testing).
2. **Git Commit:**
   - If all tests are green, make a commit.
   - Recommended format: `feat(scope): description`.
3. **Artifacts:**
   - Ensure all created artifacts (TASK, Architecture, Plan) are saved in the project documentation.
   - **Archive TASK:** Copy the final Technical Specification to the archive: `cp docs/TASK.md docs/tasks/task-ID-name.md`.

---


## 🗂 Artifact Management

During the development process, agents create various artifacts. Here is how to handle them:

| Artifact | Path | Status | Recommendation |
|----------|------|--------|----------------|
| **Product Strategy** | `docs/product/MARKET_STRATEGY.md` | **Strategic** | TAM/SAM/SOM & Competitive Analysis. Update quarterly. |
| **Product Vision** | `docs/product/PRODUCT_VISION.md` | **Strategic** | "North Star". Defines User Stories and Values. |
| **Solution Blueprint** | `docs/product/SOLUTION_BLUEPRINT.md` | **Tactical** | ROI, Risk Register, UX Flows. |
| **BRD** | `docs/product/BRD.md` | **Quality Gate** | Business Requirements. Signed with hash. Triggers dev. |
| **Technical Specification** | `docs/TASK.md` | **Single Source of Truth (Technical)** | **STRICTLY for current active task**. Derived from BRD. |
| **Architecture** | `docs/ARCHITECTURE.md` | **Source of Truth (System)** | **NEVER DELETE**. Keep updated. This is the map of your system. |
| **Known Issues** | `docs/KNOWN_ISSUES.md` | **Living Document** | Keep. Document bugs, workarounds, and complex logic explanation. |
| **Task Archive** | `docs/tasks/task-ID-name.md` | **History / Immutable** | **Mandatory Archive**. All completed TASKs move here. Never edit after archiving. |
| **Subtask Description** | `docs/tasks/task-ID-SubID-slug.md` | **Granular Plan** | Created by Planner. detailed steps for Developer. |
| **Implementation Plan** | `docs/PLAN.md` (or `implementation_plan.md`) | **Transient** | Can be kept for history or deleted after task completion. |
| **Test Report** | `tests/tests-{TaskID}/...` | **Proof of Quality** | Created by Developer. Contains verification results. |
| **Walkthrough** | `walkthrough.md` | **Proof of Work** | Created after verification. Demonstrates changes and validation results. |
| **Task Checklist** | `task.md` | **Transient** | Task tracking. Reset/overwrite for new tasks. |
| **Agent Memory** | `.AGENTS.md` | **Long-term Memory** | **NEVER DELETE**. Commit to Git. |
| **Open Questions** | `docs/open_questions.md` | **Unresolved Issues** | Track unresolved architectural questions here. |

**Strict Artefact Rules (New v2.1):**
1. **One Task = One TASK**: `docs/TASK.md` always reflects *only* what is being built right now.
2. **Archive Strategy**:
   - **Before** starting a fundamentally new task: Archive `docs/TASK.md` -> `docs/tasks/task-00N-name.md`.
   - **During** the task: Only overwrite `docs/TASK.md`. Never append.
3. **Cleanup**:
   - **Keep**: All `docs/*` files that describe the *current* state of the system.
   - **Cleanup**: Intermediate scratchpads if you used them outside of `docs/`.

---

## 📂 What to do with `.AGENTS.md` files?

**DO NOT DELETE THEM!**

The `.AGENTS.md` files are the project's "long-term memory" for agents (and humans).
- **When development is complete:** Leave them in the repository. They should be committed along with the code.
- **Why they are needed:** When you return to the project in a month (or another agent comes), this file explains: "This folder is responsible for auth, main files here are X and Y".
- **Maintenance:** If you refactor code manually, do not forget to update `.AGENTS.md`.

---

## 🔄 How to prepare for future iterations?

To make the next iteration go smoothly:
1. **Green Tests:** Leave the project with passing tests. A broken test at the start of the next task will confuse agents.
2. **Actual Map:** Check that `.AGENTS.md` matches reality.
3. **Open Questions:** If unresolved architectural questions remain, record them in `docs/open_questions.md` so the Architect of the next iteration sees them.

---

## 🛠 Reverse Engineering (If documentation is outdated)

If the user made "free-form" fixes during development completion, the documentation (e.g., `docs/TASK.md`, `docs/ARCHITECTURE.md`) might have desynchronized with the actual code.

To prevent AI from breaking what you fixed when adding a feature next time, you need to update the documentation.

> [!TIP]
> Use `skill-reverse-engineering` for structured recovery of architecture docs from code.
> Use `skill-update-memory` for automatic `.AGENTS.md` updates based on git diff.

**Example prompt (Reverse Engineering):**

```text
@docs/ARCHITECTURE.md

You are an Architect and Technical Writer.
Apply skill-reverse-engineering.

SITUATION:
We completed active development. Many manual fixes were made.
Current documentation is outdated and does not reflect the actual code structure.

TASK:
1. Use the iterative analysis strategy from skill-reverse-engineering.
2. Update docs/ARCHITECTURE.md with the real technical solution.
3. Record hidden knowledge in docs/KNOWN_ISSUES.md (TODOs, HACKs, complex spots).
4. Generate missing .AGENTS.md files using skill-update-memory format.
```


---

## 📝 Starter Prompt Templates

**IMPORTANT:** To launch the process, use **Composer** (Cmd+I) or chat.
Copy this text to activate the Orchestrator via `AGENTS.md`.

### Template 1: Developing a New Feature (Feature)
```text
You are an Orchestrator.
Context: Our project - [PROJECT_NAME/DESCRIPTION].
TASK: Develop "[FEATURE_NAME]" module.
INPUT:
- [REQUIREMENT_1]
- [REQUIREMENT_2]
ACTION:
- Execute workflow `/base-stub-first` (Standard Pipeline).
```

### Template 2: Refactoring
```text
You are an Orchestrator.
TASK: Refactor "[MODULE_NAME]" module.
CONTEXT:
- Current code: `[PATH/TO/CODE]`.
- Problem: [DESCRIPTION_OF_PROBLEM].
- Goal: [DESCRIPTION_OF_GOAL].
ACTION:
- Execute workflow `/base-stub-first` (Analysis -> Arch -> Plan -> Refactor).
```

### Template 3: Complex Bugfix
```text
You are an Orchestrator.
TASK: Fix the "[ERROR_DESCRIPTION]" bug.
INPUT:
- Log file: [PATH_TO_LOGS].
ACTION:
- Execute workflow `/vdd-adversarial` to reproduce and fix.
```

### Template 4: Documentation Restore (Reverse Engineering)
```text
You are an Orchestrator.
TASK: Restore outdated documentation.
CONTEXT:
- Active development finished, but `docs/` are stale.
ACTION:
- Execute workflow `/04-update-docs` to reverse-engineer architecture and update memory.
```

### Template 5: Security Audit
```text
You are an Orchestrator.
TASK: Audit the "[MODULE_OR_SERVICE_NAME]" for vulnerabilities.
ACTION:
- Execute workflow `/security-audit`.
```

---

## 🔄 Migration from Older Versions

### Upgrading to v3.1.0 (Global Refactor)
**Goal:** Transition from "TZ" (Техническое Задание) to "TASK" to align with the new standard.

1. **Rename Artifact:**
   ```bash
   mv docs/TZ.md docs/TASK.md
   ```
2. **Update Prompts:**
   - Overwrite `System/Agents/` with the latest version from v3.1.0 release.
   - Key shift: `03_tz_reviewer_prompt.md` is now **`03_task_reviewer_prompt.md`**.
3. **Update Skills:**
   - Overwrite `.agent/skills/` with the latest version.

### Upgrading to v3.0.0 (Skills System)
**Goal:** Enable modular agents.

1. **Delete Legacy:** Remove `System/Agents` (if it contains monolithic prompts).
2. **Install New:** Copy `System/Agents` (v3.0+) and `.agent/` folder to root.
3. **Config:** Ensure `GEMINI.md` or `AGENTS.md` are updated.

---

## 🤖 Integration with Cursor IDE (Agentic Mode)

For maximum automation, you can use a mode where the Orchestrator independently calls sub-agents via CLI.

### 1. Utility Installation
You will need the `cursor-agent` utility (or equivalent) allowing LLM requests from the terminal.
```bash
# Example installation (hypothetical)
npm install -g cursor-agent
```

### 2. Universal "Super-Prompt" for Launch
Use this prompt in Cursor chat to run the full development chain on a task.

```text
Using the multi-agent development orchestration approach (System/Agents/01_orchestrator.md),
perform the modification: {LINK_TO_TASK_FILE_OR_DESCRIPTION}.

PROJECT DESCRIPTION:
{BRIEF DESCRIPTION OR LINK TO README}

AGENT LAUNCH INSTRUCTION:
Agent prompts are located in System/Agents (02*.md .. 09.md).
You must call agents by executing shell commands like:
`cursor-agent -f --model {MODEL} -p "{PROMPT_TEXT}"`

CALL FORMAT:
The prompt text must consist of:
1. Content of the role's system prompt (e.g., System/Agents/02_analyst_prompt.md).
2. Input data for this role (according to description in 01_orchestrator.md).

RECOMMENDED MODELS:
- Analyst, Architect, Planner — opus-4.5 (or high-accuracy equivalent)
- Reviewers, Developer — composer-1 (or claude-3.5-sonnet for code)

IMPORTANT:
- Wait for the command execution result before the next step.
- Follow the pipeline: Analysis -> Architecture -> Plan -> (Stub -> Test -> Impl).
```
