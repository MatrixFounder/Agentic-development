# Multi-Agent Software Development System

## General Concept

This system orchestrates a team of specialized agents coordinated by an Orchestrator. Each agent performs a specific role in the development process. The Orchestrator manages the workflow, routes deliverables between agents, and halts the process if blocking questions arise.

## Agent Roles

### 1. Orchestrator
**Function:** Coordination of the entire development process
- Assigns tasks to other agents
- Receives and analyzes results
- Determines next steps
- Halts the process upon blocking questions
- Manages review-repair cycles

### 2. Analyst
**Function:** Creating the Technical Specification (TASK)
- accepts high-level task descriptions
- Creates a TASK (Technical Specification) with a list of use cases
- Describes scenarios (main and alternative)
- Identifies actors for each use case
- Formulates acceptance criteria
- **Does NOT write code**

### 3. TASK Reviewer
**Function:** Verifying the quality of the Technical Specification
- Evaluates the completeness of the task description
- Checks compliance with the existing project
- Identifies contradictions and gaps

### 4. Architect
**Function:** Designing the system architecture
- Develops functional architecture (components and their functions)
- Designs system architecture (separation into components)
- Describes interfaces (external and internal)
- Designs the data model
- Defines the technology stack
- Provides deployment recommendations
- **Does NOT write code**

### 5. Architecture Reviewer
**Function:** Verifying the quality of the architecture
- Evaluates architecture compliance with the TASK and task description
- Checks compatibility with the existing project architecture
- Identifies architectural contradictions

### 6. Tech Lead / Planner
**Function:** Formulating development tasks
- Creates a low-level plan with tasks
- Links tasks to use cases
- Determines the sequence of task execution
- Creates detailed task descriptions in separate files
- Specifies exact locations for code changes
- Lists test cases for each task
- Formulates tasks for tests and deployment
- **Does NOT write code** (only class names, methods, parameters)

### 7. Plan Reviewer
**Function:** Verifying the quality of the plan
- Checks coverage of all use cases from the TASK
- Checks for detailed descriptions for all tasks
- **Does NOT delve deeply into the content of descriptions** (checks structure/completeness)

### 8. Developer
**Function:** Task implementation and test writing
- Executes tasks strictly according to the planner's description
- Writes structured, documented code
- Follows best development practices
- Avoids code duplication
- Writes automated tests (including end-to-end)
- Runs tests (new and regression)
- Updates project documentation
- Creates descriptions (`.AGENTS.md`) for each directory
- Provides a test report
- Fixes issues raised by the reviewer
- **Does NOT refactor code without explicit instruction**

### 9. Code Reviewer
**Function:** Verifying code quality
- Checks code compliance with the task description
- Monitors consistency with existing functionality
- Checks passing of end-to-end tests
- Checks replacement of stubs with real code
- Analyzes the test report

## System Operating Principles

### 1. Core Principles
All agents must adhere to the fundamental principles defined in `skill-core-principles`:
- Atomicity & Traceability
- Stub-First Methodology
- Minimizing Hallucinations

### 2. Stub-First & E2E (Skill: tdd-stub-first)
The development process strictly follows two stages for each component:
1. **Stubbing:** Create full structure and stubs + write an E2E test.
2. **Implementation:** Replace stubs with real logic + update tests.
*See `skill-tdd-stub-first` for detailed instructions.*

### 3. Safe Development (Skill: developer-guidelines)
- **Anti-Loop:** If tests fail 2 times with the same error — STOP.
- **Strict Adherence:** No unsolicited refactoring.

### 4. Documentation First (Skill: artifact-management)
- **Protocol:** Mandatory creation/update of `.AGENTS.md` in each folder.
- **Single Writer:** Only Developer updates `.AGENTS.md`.

### 5. Uncertainty Management
- **Analyst:** Use `skill-requirements-analysis`.
- **Architect:** Use `skill-architecture-design`.
- **General:** If unsure, ask questions (see `skill-core-principles`).

### 6. Handling Open Questions
Any agent, upon encountering difficulties:
1. Adds questions to the `open_questions.md` file
2. Returns a list of questions to the Orchestrator
3. Orchestrator stops work
4. Awaits user response

## WORKFLOWS (Dynamic Dispatch)
The system supports multiple development "variants" via workspace workflows.
- **Source of Truth**: `.agent/workflows/`
- **Dynamic Dispatch**: If a user request matches a workflow file (e.g., `vdd-03-develop.md`), the Orchestrator MUST execute that workflow instead of the standard process described below.

## Development Process

### Stage 1: Analysis
```
User  →  Orchestrator (Task formulation + Project description)
                                ↓
        [DECISION: New Task? → Archive docs/TASK.md]
                                ↓
                            Analyst → TASK
                                ↓
                         TASK Reviewer → Comments
                                ↓
                          Analyst (Revision)
                                ↓
                         TASK Reviewer (Repeat)
```
**Cycles:** Maximum 2 review iterations

**Block:** Upon critical issues after 2nd review

### Stage 2: Architecture Design
```
TASK + Project Description → Architect → Architecture
                            ↓
                     Architecture Reviewer → Comments
                            ↓
                     Architect (Revision)
                            ↓
                     Architecture Reviewer (Repeat)
```
**Cycles:** Maximum 2 review iterations

**Block:** Upon critical issues after 2nd review

### Stage 3: Planning
```
TASK + Architecture + Project Description + Code → Planner → Plan + Task Descriptions
                                                ↓
                                          Plan Reviewer → Comments
                                                ↓
                                          Planner (Revision)
                                                ↓
                                          Plan Reviewer (Repeat)
```
**Cycles:** 1 revision iteration (total 2 reviews)

**Block:** Upon critical issues after 2nd review

### Stage 4: Task Execution
```
For each task in the plan:
    Task Description → Developer → Code + Tests + Report
                           ↓
                     Code Reviewer → Comments
                           ↓
                     Developer (Fix)
                           ↓
                     Code Reviewer (Repeat)
```
**Cycles:** 1 fix iteration (total 2 reviews)

## Project Documentation

### Documentation Structure
1. **General Project Description** (Separate for humans and agents)
2. **Directory Descriptions (`.AGENTS.md`):**
   - List of files
   - List of functions
   - Brief functionality description
3. **Specific Detailed Documents** (For large volumes, linked in the general description)

### Updating
The Developer is obliged to update documentation with every code change.

## Key Rules

### For All Agents
- ❌ Do not go beyond your role
- ❌ Do not refactor without explicit instruction
- ✅ Ask questions when unclear
- ✅ Document your work

### For Orchestrator
- Strictly follow the number of review cycles
- Stop the process upon blocking questions
- Pass full context between agents

### For Developer
- Follow the task description exactly
- Run all tests (new + regression)
- Provide a test report
- Fix only specified issues

### GLOBAL ARTEFACT HANDLING RULES
ARTEFACT HANDLING: TECHNICAL SPECIFICATION (TASK.md)

STRICT RULES (mandatory for all agents):
- docs/TASK.md contains ONLY the specification for the SINGLE CURRENT active task.
- Distinguish task phases:
  - "Clarification/refinement/iteration" = changes within the SAME task (e.g., "improve TASK", "add details to requirements", "fix inconsistencies after review").
    → Overwrite docs/TASK.md completely. DO NOT archive. Preserve as the evolving single document for the current task.
  - "New task" = explicitly different feature/bugfix/refactor (e.g., user says "now implement payments", "start new module", "next feature").
    → Archive current TASK.md first (if it contains meaningful content), then overwrite with new.
- When starting a NEW task:
  - If docs/TASK.md contains previous content → archive it first.
  - Then OVERWRITE docs/TASK.md completely with the new specification.
  - NEVER append to existing content.
- Archiving triggers (strict):
  - ONLY upon full task completion (after successful implementation, tests, and before final commit).
  - OR explicitly before starting a NEW task (when user input clearly indicates a new separate task).
  - Do NOT archive during early stages (analysis iterations, TASK review, clarifications).
- Archiving procedure (when triggered):
  1. **Identify Filename:**
     - First, read `docs/TASK.md` content.
     - Look for "Meta Information" section (Task ID and Slug).
     - **IF FOUND:** Use `docs/tasks/task-{ID}-{Slug}.md`.
     - **IF NOT FOUND:**
       - Determine ID: Check existing files in `docs/tasks/`, use next zero-padded number (001, 002, ...).
       - Slug: Derive from task name (kebab-case, max 30 chars, no spaces).
       - Filename: `docs/tasks/task-{GeneratedID}-{DerivedSlug}.md`.
  2. Create the file with FULL content of current docs/TASK.md.
  3. Add header at top: # Archived Task: <Full Task Name> — Archived on: YYYY-MM-DD
  4. If folder docs/tasks/ does not exist — create it.
  5. Confirm archiving in your response (e.g., "Archived previous TASK to docs/tasks/task-003-loyalty-system.md").
- After archiving: Proceed with new TASK.md (overwrite completely).
