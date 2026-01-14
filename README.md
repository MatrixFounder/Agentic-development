**🇺🇸 English** | [🇷🇺 Русский](README.ru.md)

> [!NOTE]
> This is the primary version. Translations may lag behind.

# Multi-Agent Software Development System v3.0

This framework orchestrates a multi-agent system for structured software development. It transforms vague requirements into high-quality code through a strict pipeline of specialized agents (Analyst, Architect, Planner, Developer, Reviewer).

The methodology combines two key approaches (see [Comparison](docs/TDD_VS_VDD.md)):
- **TDD (Test-Driven Development)**: The "Stub-First" strategy ensures that tests are written and verified against stubs before actual implementation begins. [Read more](docs/TDD.md).
- **VDD (Verification-Driven Development)**: A high-integrity mode where an adversarial agent proactively challenges the plan and code to eliminate hallucinations and logic errors before they are committed. [Read more](docs/VDD.md).

![Framework architecture](/Attachments/Framework_architecture.png)

## 📁 Installation & Setup

### 1. Common Prerequisites
Regardless of your tool, you need the **Agent Personas** in your project root:
- Copy `/System/Agents` folder to your project root.

### 2. Choose Your AI Assistant

#### 🔵 Option A: Cursor IDE
To configure Cursor for this workflow:
1.  **Context Rules**: Copy `.cursorrules` to your project root.
2.  **Skills**: Copy the contents of `.agent/skills/` to `.cursor/skills/` (or `.cursor/rules/` depending on your version).
    *   *Note:* Cursor will index these files to understand agent capabilities.

#### 🟣 Option B: Antigravity (Native)
Antigravity supports this architecture out-of-the-box:
1.  **Configuration**: Ensure `.gemini/GEMINI.md` exists (it acts as the system prompt).
2.  **Skills**: Ensure `.agent/skills/` directory exists. Antigravity automatically loads skills from here.
3.  **Workflows**: (Optional) Use `.agent/workflows/` for automated sequences.

---

## 🏗 Directory Structure
```text
project-root/
├── .cursorrules                   # [Cursor] Context & Rules
├── .cursor/skills/                # [Cursor] Skills Library
├── .gemini/GEMINI.md              # [Antigravity] System Config
├── .agent/skills/                 # [Antigravity] Skills Library
├── System/Agents/                 # [Common] Agent Personas (00-10)
└── src/                           # Your Source Code
```

### 🔑 System Prompt (00_agent_development.md)
The file `00_agent_development.md` contains **fundamental principles** (Meta-System Prompt).
It **MUST** be added to the context for all other agents (01-10).

### 🤖 The Agent Team (Roles)

| Role | File | Responsibility |
|------|------|----------------|
| **Orchestrator** | `01_orchestrator.md` | Project Manager. Dispatches tasks, manages the pipeline. |
| **Analyst** | `02_analyst_prompt.md` | Requirements elicitation, TZ creation. |
| **TZ Reviewer** | `03_tz_reviewer_prompt.md` | Quality control for Technical Specifications. |
| **Architect** | `04_architect_prompt.md` | System design, database schema, API definition. |
| **Arch Reviewer** | `05_architecture_reviewer_prompt.md` | Validates verification of architectural decisions. |
| **Planner** | `06_agent_planner.md` | Breaks down implementation into atomic steps (Stub-First). |
| **Plan Reviewer** | `07_agent_plan_reviewer.md` | Ensures the plan is logical and testable. |
| **Developer** | `08_agent_developer.md` | Writes code (Stubs -> Tests -> Implementation). |
| **Code Reviewer** | `09_agent_code_reviewer.md` | Final code quality check. |
| **Security Auditor** | `10_security_auditor.md` | Security vulnerability assessment and reporting. |

### 📊 How the System Prompt is Loaded

| Tool | System Prompt | Loading Method |
|------|---------------|----------------|
| **Cursor IDE** | `00` + role (01-09) | Manually or via `.cursorrules` |
| **Antigravity** | `.gemini/GEMINI.md` (includes global principles) | **Automatically (Native)**. Manual concatenation of `00` is not required. |



---

## ⚡ Workspace Workflows

To simplify launching different development modes, the project provides special **Workflows**.
Detailed description of all workflows: [docs/WORKFLOWS.md](docs/WORKFLOWS.md).

### Quick Start
You can run a workflow simply by asking the agent:

- **Standard Mode (Stub-First):**
  - "Start feature X" -> runs `01-start-feature.md`
  - "Plan implementation" -> runs `02-plan-implementation.md`
  - "Develop task" -> runs `03-develop-task.md`

- **VDD Mode (Verification-Driven Development):**
  - "Start feature X in VDD mode" -> runs `vdd-01-start-feature.md`
  - "Develop task in VDD mode" -> runs `vdd-03-develop.md` (Adversarial Loop)

### Variants
1. **Standard**: Basic mode, focused on speed and structure (Stub-First).
2. **VDD (Verification-Driven)**: High-reliability mode using an "Adversarial Agent" (Sarcasmotron) that harshly criticizes code.
3. **Nested & Advanced**:
   - **VDD Enhanced** (`/vdd-enhanced`): Runs Stub-First then VDD Refinement.
   - **Full Robust** (`/full-robust`): Runs VDD Enhanced then Security Audit.

---

## 🚀 How to Start Development (Step-by-Step Plan)

This process will take you from an idea to finished code in the repository.

### Stage 1: Pre-flight Check
1. **Initialization:** Ensure you are in the project root.
2. **Reconnaissance:** If the project already exists, ensure `.AGENTS.md` files exist in root folders. If not, create empty or basic ones so agents have somewhere to write.

### Stage 2: Analysis and Design
1. **Analyst (02_analyst_prompt.md):**
   - Provide the agent with the idea/task.
   - The agent studies the project structure (Reconnaissance).
   - Result: **Technical Specification (TZ)**.
2. **TZ Review (03_tz_reviewer_prompt.md):**
   - Check the TZ for completeness and consistency.
3. **Architect (04_architect_prompt.md):**
   - Based on the TZ, the agent designs the architecture.
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
   - Ensure all created artifacts (TZ, Architecture, Plan) are saved in the project documentation.
   - **Archive TZ:** Copy the final Technical Specification to the archive: `cp docs/TZ.md docs/tasks/task-ID-name.md`.

---


## 🗂 Artifact Management

During the development process, agents create various artifacts. Here is how to handle them:

| Artifact | Path | Status | Recommendation |
|----------|------|--------|----------------|
| **Technical Specification** | `docs/TZ.md` | **Single Source of Truth (Current Task)** | **STRICTLY for current active task**. Overwrite for updates. Archive before new task. |
| **Architecture** | `docs/ARCHITECTURE.md` | **Source of Truth (System)** | **NEVER DELETE**. Keep updated. This is the map of your system. |
| **Known Issues** | `docs/KNOWN_ISSUES.md` | **Living Document** | Keep. Document bugs, workarounds, and complex logic explanation. |
| **Task Archive** | `docs/tasks/task-ID-name.md` | **History / Immutable** | **Mandatory Archive**. All completed TZs move here. Never edit after archiving. |
| **Subtask Description** | `docs/tasks/task-ID-SubID-slug.md` | **Granular Plan** | Created by Planner. detailed steps for Developer. |
| **Implementation Plan** | `docs/PLAN.md` (or `implementation_plan.md`) | **Transient** | Can be kept for history or deleted after task completion. |
| **Task Checklist** | `task.md` | **Transient** | Task tracking. Reset/overwrite for new tasks. |
| **Agent Memory** | `.AGENTS.md` | **Long-term Memory** | **NEVER DELETE**. Commit to Git. |

**Strict Artefact Rules (New v2.1):**
1. **One Task = One TZ**: `docs/TZ.md` always reflects *only* what is being built right now.
2. **Archive Strategy**:
   - **Before** starting a fundamentally new task: Archive `docs/TZ.md` -> `docs/tasks/task-00N-name.md`.
   - **During** the task: Only overwrite `docs/TZ.md`. Never append.
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
3. **Open Questions:** If unresolved architectural questions remain, record them in `UNKNOWN.md` or a similar file in `docs/` so the Architect of the next iteration sees them.

---

## 🛠 Reverse Engineering (If documentation is outdated)

If the user made "free-form" fixes during development completion, the documentation (e.g., `docs/TZ.md`, `docs/ARCHITECTURE.md`) might have desynchronized with the actual code.

To prevent AI from breaking what you fixed when adding a feature next time (e.g., "color-code tasks by status"), you need to update the documentation.

Use this prompt (Reverse Engineering):

```text
@docs/TZ.md

You are an Architect and Technical Writer.

SITUATION:
We completed the active development and debugging phase of the Gantt widget prototype.
Many manual fixes were made to the code to fix bugs (scroll, Drag&Drop).
Current documentation (TZ.md) is outdated and does not reflect the actual code structure.

TASK:
1. Study ALL current widget code files (HTML, CSS, TS).
2. Update the `docs/ARCHITECTURE.md` file (or create it), describing the real technical solution that is currently working.
3. Record in `docs/KNOWN_ISSUES.md` (create file) what complex spots we resolved (how Drag&Drop is implemented, how scroll works) to avoid breaking this in the future.

This is needed so that you understand the actual context during future modifications.
```

---

## 📝 Starter Prompt Templates

**IMPORTANT:** To launch the process, use **Composer** (Cmd+I) or chat.
Copy this text to activate the Orchestrator via `.cursorrules`.

### Template 1: Developing a New Feature (Feature)
```text
You are an Orchestrator.
Context: Our project - [Online Store on Django].
TASK: Organize development of a new "Loyalty System" module.
INPUT:
- Users should receive 1 point for every 100 rubles.
- It should be possible to pay with points up to 30% of the order.
ACTIVE SKILLS:
- skill-core-principles
- skill-planning-decision-tree
ACTIONS:
- Run the full pipeline (Analysis -> Architecture -> Plan -> Code).
- Ensure Stub-First strategy (skill-tdd-stub-first).
```

### Template 2: Refactoring
```text
You are an Orchestrator.
TASK: Organize refactoring of the "Notification Sending" module.
CONTEXT:
- Current code: `src/notifications`.
- Problem: Synchronous sending.
- Goal: Move to Celery.
ACTIVE SKILLS:
- skill-architecture-design
ACTIONS:
- Guide through all stages (Analyst -> Architect -> Plan...).
```

### Template 3: Complex Bugfix
```text
You are an Orchestrator.
TASK: Fix the "Double Charigng" error.
INPUT:
- Log file: error_logs.txt.
ACTIVE SKILLS:
- skill-tdd-stub-first
- skill-vdd-adversarial
ACTIONS:
- Analyst must create a scenario (E2E test) to reproduce.
- Fix via Stub-First (test first, then fix).
```

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
