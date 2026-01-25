# Architecture: Agentic Development System

## Table of Contents
- [1. Core Concept](#1-core-concept)
- [2. Directory Structure](#2-directory-structure)
- [3. Workflow Logic (v3.1)](#3-workflow-logic-v31)
- [4. Tool Execution Subsystem [NEW]](#4-tool-execution-subsystem-new)
- [5. Key Principles](#5-key-principles)
- [6. Localization Strategy](#6-localization-strategy)
- [7. Skill Architecture & Optimization Standards](#7-skill-architecture--optimization-standards)

## 1. Core Concept
The system is built on a "Multi-Agent" architecture where different "Agents" (Personas defined by System Prompts) collaborate to solve tasks.
The Source of Truth for these agents is located in `System/Agents`.

## 2. Directory Structure
```text
project-root/
├── GEMINI.md                    # Orchestrator + core-principles
├── .cursor/rules/                 # Cursor Rules
├── AGENTS.md                      # References to rules + reading .AGENTS.md
├── .agent/
│   ├── skills/                  # Skills Library (Source of Capabilities)
│   │   ├── ...
│   │   └── skill-product-*      # [NEW] Product Skills (Strategy, Vision, Handoff)
│   └── tools/                   # Executable Tools Schemas (schemas.py)
├── .cursor/skills/                # [Symlink] Mirrors .agent/skills for Cursor
├── System/
│   ├── Agents/                  # Lightweight System Prompts (Personas)
│   │   ├── 00_agent_development.md
│   │   ├── 01_orchestrator.md
│   │   ├── ...
│   │   ├── p00_product_orchestrator.md #[NEW] Product Phase Agents
│   │   └── p04_solution_architect.md
│   ├── Docs/                    # Framework Documentation & Guides
│   │   ├── SKILLS.md            # Skills Catalog
│   │   ├── ORCHESTRATOR.md      # Tools Guide
│   │   ├── PRODUCT_DEVELOPMENT.md #[NEW] Product Playbook
│   │   └── ...
│   └── scripts/                 # [NEW] Framework Utilities (Tool Dispatcher)
│       └── tool_runner.py
├── Translations/                # Localizations (RU)
├── src/                         # Project Code
│   ├── services/
│   │   └── .AGENTS.md           # Local Context Artifact (Per-directory)
│   └── ...
├── docs/                        # Project Artifacts
│   ├── product/                 # [NEW] Product Artifacts (Strategy, Vision, BRD)
│   ├── TASK.md                  # Current Technical Task
│   ├── ARCHITECTURE.md          # System Architecture (This file)
│   └── ...
├── tests/                       # Tests & Test Reports
│   ├── tests-{ID}/              # Test Reports per Task (e.g. tests-016/)
│   └── ...
└── archives/
```

## 3. Workflow Logic (v3.1)
1. **Orchestrator** receives the user task and manages the **Tool Execution Loop**.
    - If the Model supports **Native Tool Calling**, the Orchestrator executes tools directly (structured) and feeds results back.
    - If not, it falls back to text-based parsing.
2. **Agent** (any role) starts by reading relevant local `.AGENTS.md` files...
3. **Agent** activates **Skills** (dynamically loaded from `.agent/skills`).
   - *Example:* Analyst loads `skill-requirements-analysis`.
4. **Analyst** (Agent 02) creates/updates a Technical Specification (TASK) in `docs/TASK.md`.
    - *Verification:* **Task Reviewer** (Agent 03) validates the TASK.
5. **Architect** (Agent 04) validates/updates Architecture in `docs/ARCHITECTURE.md`.
    - *Verification:* **Architecture Reviewer** (Agent 05) checks the design.
6. **Planner** (Agent 06) creates a Task Plan in `docs/PLAN.md` and detailed tasks.
    - *Verification:* **Plan Reviewer** (Agent 07) validates the plan.
7. **Developer** (Agent 08) executes the plan using Stub-First methodology.
    - **Crucial Step**: Updates code AND local `.AGENTS.md` (Documentation First).
    - *Verification:* **Code Reviewer** (Agent 09) checks the code.
8. **Security Auditor** (Agent 10) performs vulnerability analysis.

## 4. Tool Execution Subsystem [NEW]
The orchestration layer now supports **Structured Tool Calling**:
- **Definition**: Tools are defined in `.agent/tools/schemas.py` as `TOOLS_SCHEMAS`.
- **Execution**: The Orchestrator loads these schemas and passes them to the LLM.
- **Dispatch**: When the LLM requests a tool call, the Orchestrator intercepts it, executes the corresponding Python function (via `System/scripts/tool_runner.py`), and returns the result as a `tool` role message.
- **Security Check**: All tool arguments are validated; file operations are restricted to the project root (Anti-Path-Traversal).

### Available Tools
| Tool | Description |
|------|-------------|
| `run_tests` | Run pytest with custom commands |
| `read_file` | Read file contents |
| `write_file` | Create/overwrite files |
| `list_directory` | List directory contents |
| `git_status`, `git_add`, `git_commit` | Git operations |
| `generate_task_archive_filename` | Generate unique sequential ID for task archival |


## 5. Key Principles
- **Modular Skills**: Logic is decoupled from Personas. Agents load `skills` to perform specific tasks.
- **Local Artifacts**: `.AGENTS.md` provide distributed long-term memory per directory.
- **Session State**: `latest.yaml` provides volatile short-term memory (GPS coordinates).
- **Single Writer**: Only the Developer agent writes code and updates `.AGENTS.md` to prevent conflicts.
- **Stub-First**: Always create stubs/interfaces before implementation.
- **One Giant Column**: Keep context constraints in mind.
- **Source of Truth**: Documentation (`docs/`), `System/Agents`, `.agent/skills`, and `latest.yaml`.

## 6. Localization Strategy
- **Default**: English (`System/Agents`).
- **Alternative**: Russian (`System/Agents_ru` -> `Translations/RU`).
- Switching is done by swapping the source directory in the orchestrator config.

## 7. Skill Architecture & Optimization Standards

> **Critical Requirement:** All new skills MUST adhere to the **O6/O6a Optimization Standards** defined in [System/Docs/SKILLS.md](../System/Docs/SKILLS.md).

The system relies on a modular **Skills System** ([System/Docs/SKILLS.md](../System/Docs/SKILLS.md)) that separates "Who" (Agent) from "What" (Capabilities). To maintain performance and context limits, strict rules apply:

### Rule 1: Script-First Approach (O6a)
**Do NOT write complex logic in natural language.**
If a skill requires analyzing project structure, calculating metrics, or validating files:
- ❌ **Bad:** "Look at the file, count the lines, then if X..." (Bloats prompt, unreliable).
- ✅ **Good:** "Run `scripts/analyze_metrics.py`." (Zero-hallucination, deterministic).

### Rule 2: Example Separation (O6a)
**Do NOT inline large templates or examples.**
- ❌ **Bad:** Embedding 50 lines of JSON example in `SKILL.md`.
- ✅ **Good:** "Refer to `examples/template.json`."
*Why?* Skills are loaded into the context window. Static text wastes tokens.

### Rule 3: Tiered Loading Protocol (O5)
Every skill must be assigned a **TIER** in its YAML frontmatter to support Lazy Loading.
- **TIER 0 (System):** Always loaded (e.g., `safe-commands`). **Restriction:** Must be <500 tokens.
- **TIER 1 (Phase):** Loaded on phase entry (e.g., `requirements-analysis`).
- **TIER 2 (Extended):** Loaded only on demand (e.g., `adversarial-security`).

### Rule 4: Skill Creator Standard
All new skills must be generated using `skill-creator`.
- **Reason:** Enforces directory structure (`scripts/`, `examples/`, `tests/`) and runs validation checks (`validate_skill.py`).

**[>> Read Full Skills Documentation <<](../System/Docs/SKILLS.md)**
