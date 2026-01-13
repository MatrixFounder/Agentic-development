# Architecture: Agentic Development System

## 1. Core Concept
The system is built on a "Multi-Agent" architecture where different "Agents" (Personas defined by System Prompts) collaborate to solve tasks.
The Source of Truth for these agents is located in `System/Agents`.

## 2. Directory Structure
```text
.agent/                      # Agentic Workflows & Rules
├── workflows/               # Executable workflow definitions
└── rules/                   # Specific agent rules
docs/                        # Project Documentation (Source of Truth)
├── tasks/                   # Archived Tasks (History)
├── ARCHITECTURE.md          # This file
├── WORKFLOWS.md             # User Manual for Workflows
└── ...
System/
├── Agents/                  # Primary System Prompts (English)
│   ├── 00_agent_development.md  # Meta-prompt / Orchestrator guide
│   ├── 01_orchestrator.md       # Interaction handler
│   ├── 02_analyst_prompt.md     # Requirements analysis
│   ├── 04_architect_prompt.md   # System design
│   ├── 06_agent_planner.md      # Planning & Task breakdown
│   ├── 08_agent_developer.md    # Code implementation
│   ├── 10_security_auditor.md   # Security Vulnerability Assessment
│   └── ...
└── Agents_ru/               # Legacy/Backup System Prompts (Russian)
    └── ... (mirrors Agents/)
```

## 3. Workflow Logic
1. **Orchestrator** receives the user task.
2. **Analyst** (Agent 02) creates a Technical Specification (TZ).
    - *Verification:* **TZ Reviewer** (Agent 03) validates the TZ.
3. **Architect** (Agent 04) validates/updates Architecture.
    - *Verification:* **Architecture Reviewer** (Agent 05) checks the design.
4. **Planner** (Agent 06) creates a Task Plan.
    - *Verification:* **Plan Reviewer** (Agent 07) validates the plan.
5. **Developer** (Agent 08) executes the plan using Stub-First methodology.
    - *Verification:* **Code Reviewer** (Agent 09) checks the code (optional/workflow-dependent).
6. **Security Auditor** (Agent 10) performs vulnerability analysis (optional/workflow-dependent).

Workflows can be **nested**: A workflow can call another workflow (e.g., VDD invokes Base Stub-First), allowing for composable and reusable process definitions. Workflow definitions are stored in `.agent/workflows`.

## 4. Key Principles
- **Stub-First**: Always create stubs/interfaces before implementation.
- **One Giant Column**: (Metaphor for keeping context constraints in mind).
- **Source of Truth**: Documentation (`docs/`) and `System/Agents` are the sources of truth.

## 5. Localization Strategy
- **Default**: English (`System/Agents`).
- **Alternative**: Russian (`System/Agents_ru`).
- Switching is done by pointing the Agent Construction mechanism to the appropriate folder.
