# Architecture: Agentic Development System

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
│   └── tools/                   # [NEW] Executable Tools Schemas (schemas.py)
├── .cursor/skills/                # [Symlink] Mirrors .agent/skills for Cursor
├── System/
│   ├── Agents/                  # Lightweight System Prompts (Personas)
│   │   ├── 00_agent_development.md
│   │   ├── 01_orchestrator.md
│   │   └── ...
│   ├── Docs/                    # Framework Documentation & Guides
│   │   ├── SKILLS.md            # Skills Catalog
│   │   ├── ORCHESTRATOR.md      # Tools Guide
│   │   └── ...
│   └── scripts/                 # [NEW] Framework Utilities (Tool Dispatcher)
│       └── tool_runner.py
├── Translations/                # Localizations (RU)
├── src/                         # Project Code
│   ├── services/
│   │   └── .AGENTS.md           # Local Context Artifact (Per-directory)
│   └── ...
├── docs/                        # Project Artifacts
│   ├── TASK.md                  # Current Task
│   ├── ARCHITECTURE.md          # System Architecture (This file)
│   └── ...
├── tests/                       # Tests & Test Reports
│   ├── tests-{ID}/              # Test Reports per Task (e.g. tests-016/)
│   └── reports/                 # Validation Reports (e.g. o1-o3-validation.md)
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
- **Single Writer**: Only the Developer agent writes code and updates `.AGENTS.md` to prevent conflicts.
- **Stub-First**: Always create stubs/interfaces before implementation.
- **One Giant Column**: Keep context constraints in mind.
- **Source of Truth**: Documentation (`docs/`), `System/Agents`, and local `.AGENTS.md`.

## 6. Localization Strategy
- **Default**: English (`System/Agents`).
- **Alternative**: Russian (`System/Agents_ru`).
- Switching is done by pointing the Agent Construction mechanism to the appropriate folder.
