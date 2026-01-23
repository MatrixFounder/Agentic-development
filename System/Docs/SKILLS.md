# System Skills Catalog

The Agentic System v3.0 relies on a modular **Skills System**. Skills are reusable packages of instructions that extend agent capabilities.

## Table of Contents
- [Library Layout](#-library-layout)
- [How it Works](#️-how-it-works)
- [Available Skills](#-available-skills)
- [Dynamic Loading](#-dynamic-loading)
- [Skill Tiers](#-skill-tiers)
- [Isolated Testing](#-isolated-testing-skills)
- [Best Practices](#-best-practices)

## 📁 Library Layout
Skills are located in `.agent/skills/`.

## ⚙️ How it Works

The Skills System separates **"Who"** (Agent Persona) from **"What"** (Capabilities).
- **Persona (`System/Agents/`)**: Defines the role, tone, and high-level responsibilities (e.g., "You are an Architect").
- **Skill (`.agent/skills/`)**: Defines specific procedures, checklists, or technical standards (e.g., "How to design a DB").

### Principles
1.  **Dynamic Loading**: Agents load only the skills they need for a specific task.
2.  **Modularity**: Improvements to `skill-tdd-stub-first` automatically benefit all agents using it.
3.  **Cross-Platform**: The same skill definitions work in both Cursor and Antigravity.

### 🔗 Documentation
- **For Cursor**: [Cursor Skills Documentation](https://cursor.com/ru/docs/context/skills)
- **For Antigravity**: [Antigravity Skills Documentation](https://antigravity.google/docs/skills)

## 📚 Available Skills

### Core & Process
| Skill | Description | Used By in Workflows | Used By Agents |
|-------|-------------|----------------------|----------------|
| **`core-principles`** | Fundamental principles: Atomicity, Traceability, Stub-First, Minimizing Hallucinations. | All (`01-03`, `vdd-*`) | All Agents |
| **`artifact-management`** | Rules for managing `.AGENTS.md` (local memory) and global artifacts (`TASK.md`, `ARCHITECTURE.md`). | All Workflows | All Agents |
| **`skill-archive-task`** | Complete protocol for archiving TASK.md with ID generation. Single source of truth for archiving. | `01-start-feature`, All | Analyst, Orchestrator |
| **`skill-safe-commands`** | Centralized list of commands safe for auto-execution without user approval. | All | All Agents |
| **`skill-session-state`** | Persist and restore session state (Mode, Task, Summary) to recovery from checks/resets. <br> **[Guide: Session Context Management](SESSION_CONTEXT_GUIDE.md)** | All | All Agents |
| **`skill-phase-context`** | Skill loading tiers: TIER 0 (always), TIER 1 (phase-triggered), TIER 2 (extended). Defines when to load which skills. | All | Orchestrator |
| **`skill-orchestrator-patterns`** | Stage Cycle pattern and dispatch table for Orchestrator compression. Defines Init→Review→Revision flow. | All | Orchestrator |
| **`skill-update-memory`** | Auto-update `.AGENTS.md` files based on code changes from git diff. | `04-update-docs`, Code Review | Developer, Code Reviewer |
| **`skill-reverse-engineering`** | Regenerate architecture documentation from codebase analysis. | `04-update-docs`, Manual | Architect, Analyst |
| **`planning-decision-tree`** | Decision logic for breaking down tasks and prioritizing work (Stub-First & E2E). | `02-plan-implementation`, `vdd-02-plan` | Planner, Architect |
| **`requirements-analysis`** | Process for gathering and refining requirements into a structured Technical Specification (TASK). | `01-start-feature`, `vdd-01-start-feature` | Analyst, TASK Reviewer |
| **`skill-task-model`** | Standard models, examples (Good/Bad), and structure rules for TASK documents. | `01-start-feature` | Analyst, TASK Reviewer |
| **`skill-creator`** | Guidelines for creating new Agent Skills. Based on [Anthropic](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) & [Antigravity](https://antigravity.google/docs/skills) standards. | Manual, `04-update-docs` | Developer, Architect |
| **`light-mode`** | Fast-track guidelines for trivial tasks (typos, UI tweaks). Skips Architect/Planner. (Tier 2) | `/light`, `light-01-start-feature` | Analyst, Developer, Code Reviewer |

### Engineering Standards
| Skill | Description | Used By in Workflows | Used By Agents |
|-------|-------------|----------------------|----------------|
| **`architecture-design`** | Guidelines for designing scalable and modular system architecture and data models. | `01-start-feature`, `/base-stub-first` | Architect, Arch Reviewer |
| **`skill-planning-format`** | Standard templates for `PLAN.md` and Task Descriptions. | `02-plan-implementation` | Planner |
| **`architecture-format-core`** | Core template for Architecture documents. For quick updates. (~150 lines, TIER 1) | `01-start-feature`, Most updates | Architect |
| **`architecture-format-extended`** | Full templates with examples, diagrams, JSON samples. For new systems. (~400 lines, TIER 2) | New systems, Major refactors | Architect |
| **`tdd-stub-first`** | Test-Driven Development strategy: "Structure & Stubs" first, then "Implementation". | `03-develop-task`, `vdd-enhanced` | Planner, Developer |
| **`developer-guidelines`** | Behavioral rules for Developers: adherence to tasks, "Documentation First", Anti-Loop Protocol. | `03-develop-task`, `/base-stub-first` | Developer |
| **`documentation-standards`** | Standards for docstrings (Google/JSDoc) and "The Why" comments. | All Development Workflows | Developer, Code Reviewer |
| **`testing-best-practices`** | Best practices: E2E/Unit hierarchy, no LLM mocking, realism. | `03-develop-task`, `vdd-03-develop` | Developer, Code Reviewer |

### Product Management
| Skill | Description | Used By in Workflows | Used By Agents |
|-------|-------------|----------------------|----------------|
| **`skill-product-analysis`** | Creation of Product Vision and Strategy. (Tier 2) | Manual / Product Bootstrap | Product Analyst (p01) |
| **`skill-backlog-prioritization`** | Backlog management logic containing WSJF rules. (Tier 2) | Manual / Product Bootstrap | Product Analyst (p01) |

### Review & Quality Assurance
| Skill | Description | Used By in Workflows | Used By Agents |
|-------|-------------|----------------------|----------------|
| **`checklists/*`** | Specialized checklists for each review stage: | All relevant stages | Reviewers (TASK, Arch, Plan, Code) |
| - `task-review-checklist` | For checking Technical Specifications. | `01-start-feature` | TASK Reviewer |
| - `architecture-review-checklist` | For checking System Architecture. | `01-start-feature` | Arch Reviewer |
| - `plan-review-checklist` | For checking Development Plans. | `02-plan-implementation` | Plan Reviewer |
| - `code-review-checklist` | For checking Code implementation. | `03-develop-task` | Code Reviewer |
| **`security-audit`** | Vulnerability assessment (OWASP, secrets) and reporting. | `/security-audit`, `/full-robust` | Security Auditor |

### Executable Skills (Tools)
| Skill | Description | Used By in Workflows | Used By Agents |
|-------|-------------|----------------------|----------------|
| **`tools/*`** | Core system tools defined in `.agent/tools/schemas.py`. These are natively executed by the Orchestrator. | `01-start-feature`, `03-develop-task` | All Agents |
| - `run_tests` | Runs pytest validation. | `03-develop-task` | Developer |
| - `git_ops` | Git operations (status, add, commit). | `03-develop-task` | Developer |
| - `generate_task_archive_filename` | Generates unique sequential ID for task archival. Handles conflicts. | `01-start-feature`, `04-update-docs` | Analyst, Orchestrator |

### Verification Driven Development (VDD)
| Skill | Description | Used By in Workflows | Used By Agents |
|-------|-------------|----------------------|----------------|
| **`skill-vdd-adversarial`** | Adversarial verification: challenging assumptions and finding weak spots. <br> **[Read Full Role Description](VDD.md#core-philosophy)** | `vdd-03-develop`, `/vdd-adversarial`, `/vdd-multi` | **Virtual Persona** <br> (Adversarial Agent) |
| **`vdd-sarcastic`** | Adversarial verification with a sarcastic/provocative tone. (Variant of `vdd-adversarial`) | `/vdd-sarcastic` | **Virtual Persona** <br> (Adversarial Agent) |
| **`skill-adversarial-security`** | OWASP security critic in adversarial/sarcastic style. Checks injections, auth, secrets. | `/vdd-multi` | **Virtual Persona** <br> (Security Critic) |
| **`skill-adversarial-performance`** | Performance critic in adversarial/sarcastic style. Checks N+1, memory, async issues. | `/vdd-multi` | **Virtual Persona** <br> (Performance Critic) |

## 🚀 Dynamic Loading

The Orchestrator dynamically dynamically constructs the Agent's prompt by combining three elements:

1.  **Base Role** (`System/Agents/<agent_name>.md`): The core persona (e.g., "You are a Developer").
2.  **Active Skills** (`ACTIVE SKILLS` list in Role): The specific capabilities required for the task.
3.  **Task Context**: The user's request and project context.

### Prompt Assembly Process
When an Agent is initialized:
1.  The system reads the **Base Role** file.
2.  It parses the `ACTIVE SKILLS` section (YAML or list mechanism).
3.  It loads the content of each referenced skill from `.agent/skills/`.
4.  It appends a `### LOADED SKILLS` section to the system prompt containing the full text of these skills.

**Simplified Prompt Structure:**

```markdown
[Base Role Content: "You are the Developer..."]

### LOADED SKILLS

#### SKILL: skill-tdd-stub-first
[Content of skill-tdd-stub-first.md]

#### SKILL: skill-core-principles
[Content of skill-core-principles.md]

[Task Description]
```

## 🏷️ Skill Tiers

To optimize token usage, skills are classified into three tiers (Lazy Loading Protocol).
**Authoritative Source:** [System/Docs/SKILL_TIERS.md](SKILL_TIERS.md)

1.  **TIER 0 (System Foundation)**: Always loaded at bootstrap. Mandatory for basic operation (e.g., `skill-safe-commands`).
2.  **TIER 1 (Phase-Triggered)**: Loaded automatically when entering a specific phase (Analysis, Planning, etc.).
3.  **TIER 2 (Extended)**: Loaded only on explicit request or for specialized workflows.

## 🧪 Isolated Testing Skills

Testing skills in isolation allows you to verify prompts, check compliance with instructions, and iterate quickly without running the full Orchestrator pipeline.

### Option 1: Python Script (Recommended)
We provide a helper script to test skills with any OpenAI-compatible API (OpenAI, xAI, OpenRouter, etc.).

1.  **Locate the script**: [`examples/skill-testing/test_skill.py`](examples/skill-testing/test_skill.py).
2.  **Configure**: Edit the `ROLE_FILE`, `TARGET_SKILLS`, and `TEST_TASK` variables in the `__main__` block.
3.  **Run**:
    ```bash
    export OPENAI_API_KEY="your-key"
    # Optional: export OPENAI_BASE_URL="https://api.other-provider.com/v1"
    python3 examples/skill-testing/test_skill.py
    ```

### Option 2: n8n / Low-Code
You can use n8n or any flow-based tool. We provide a ready-to-import workflow with **Sticky Notes (Stickers)** acting as hints for configuration.

1.  **Download the Workflow**: [`examples/skill-testing/n8n_skill_eval_workflow.json`](examples/skill-testing/n8n_skill_eval_workflow.json).
2.  **Import to n8n**: Go to Workflow -> Import from File.
3.  **Follow the Stickers**: The workflow canvas contains Sticky Notes explaining where to paste your Role content and where the Prompt Assembly logic lives.
4.  **Execute**: Run the workflow to see the assembled prompt and the AI's response.

## ✅ Best Practices

When creating or modifying skills, follow these guidelines to ensure effectiveness and maintainability.

### 0. Creation Standard (V2)
**ALWAYS** start your skill implementation using the **Skill Creator standard**:
- Path: [`.agent/skills/skill-creator`](../.agent/skills/skill-creator)
- Reasoning: Ensures compliance with structure, testing, and validation scripts from Day 1.

### 1. Granularity & Size
- **Keep it Focused**: A skill should do *one* thing well.
- **Token Limit**: Keep `SKILL.md` under **1000 tokens**. Move heavy content to resources.
- **Script-First (Optimization O6a)**: If a skill contains complex logic (e.g., "scan this project structure"), **DO NOT** write 5 pages of instructions.
    - ✅ **Correct:** Write a Python script (`scripts/scan.py`) and instruct the agent to run it.
    - ❌ **Incorrect:** "Look at file X, then check Y, then if Z..." (Unreliable & expensive).

### 2. Instruction Style
- **Imperative**: Use "You MUST", "DO NOT".
- **Example Separation**: **NEVER** put large examples inline in `SKILL.md`.
    - ✅ **Correct:** "See `examples/auth_flow.py`".
    - ❌ **Incorrect:** Large code blocks inside the prompt (wastes tokens).
- **Resource Extraction**: Move checklists, templates, and patterns to `resources/` directory.

### 3. Versioning & Updates
- **Breaking Changes**: Check usage via `grep -r "skill-name" System/Agents`.
- **Validation**: ALWAYS run `validate_skill.py` before committing.

### 4. Anti-Patterns
- ❌ **Inline Bloat**: Large ASCII art, huge tables, or inline templates.
- ❌ **Duplication**: Re-listing OWASP rules instead of linking to `security-audit`.
- ❌ **Hardcoded Paths**: Use relative structure or standard vars.

> **Note:** These standards are derived from the [Agentic Development Optimizations](../Backlog/agentic_development_optimisations.md) (O6/O6a) to ensure scalability.
