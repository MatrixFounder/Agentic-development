# Architecture: Agentic Development System

## 1. Core Concept
The system is built on a "Multi-Agent" architecture where different "Agents" (Personas defined by System Prompts) collaborate to solve tasks.
The Source of Truth for these agents is located in `System/Agents`.

## 2. Directory Structure
```text
project-root/
├── .gemini/GEMINI.md              # Orchestrator + core-principles
├── .cursor/rules/                 # Cursor Rules
├── .cursorrules                   # References to skills + reading .AGENTS.md
├── .agent/
│   ├── skills/                  # Skills Library (Source of Capabilities)
│   └── tools/                   # [NEW] Executable Tools Schemas (schemas.py)
├── .cursor/skills/                # [Symlink] Mirrors .agent/skills for Cursor
├── System/Agents/                 # Lightweight System Prompts (Personas)
│   ├── 00_agent_development.md  # Meta-prompt / Orchestrator guide
│   ├── 01_orchestrator.md       # Interaction handler
│   ├── 02_analyst_prompt.md     # Requirements analysis
│   └── ...
├── Translations/                  # Localizations (RU)
├── src/                           # Project Code
│   ├── services/
│   │   └── .AGENTS.md             # Local Context Artifact (Per-directory)
│   └── ...
├── docs/                          # Global Artifacts
│   ├── SKILLS.md                # Skills Catalog
│   ├── ARCHITECTURE.md          # This file
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
- **Dispatch**: When the LLM requests a tool call, the Orchestrator intercepts it, executes the corresponding Python function (via `execute_tool` dispatcher), and returns the result as a `tool` role message.
- **Security Check**: All tool arguments are validated; file operations are restricted to the project root (Anti-Path-Traversal).

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
