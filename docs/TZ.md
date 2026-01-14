# Technical Specification: Skills System Integration & Local Artifacts Optimization

## 0. Meta Information
- **Task ID:** 010
- **Slug:** skills-and-artifacts

## 1. General Description
The goal is to transform the Agentic-development framework into an enterprise-ready solution for multi-agent software development. This involves introducing modular "skills" to encapsulate repetitive processes, reinforcing the system of local artifacts (`.AGENTS.md`) as distributed long-term memory, and ensuring cross-platform compatibility (Antigravity + Cursor). The key focus is on preserving the unique behavior of agents while simplifying their prompts and establishing a "single writer" protocol for code and documentation to minimize conflicts.

## 2. List of Use Cases

### UC-01: Agent Executes Task with Skills
**Actors:** Orchestrator, Agent (Developer/Reviewer/etc.)
**Preconditions:** Task assigned to agent.
**Main Scenario:**
1. Orchestrator assigns a task to an Agent.
2. Agent reads relevant local `.AGENTS.md` files in the target directories.
3. Agent activates necessary skills (starting with `core-principles`).
4. Agent executes the task using the logic defined in the skills (e.g., TDD, verification).
5. Agent completes the task.

### UC-02: Developer Updates Code and Artifacts
**Actors:** Developer Agent
**Preconditions:** Code changes are required.
**Main Scenario:**
1. Developer modifies code in a specific directory (e.g., `src/services/`).
2. Developer checks for existing `.AGENTS.md` in that directory.
3. Developer creates or updates `.AGENTS.md` to reflect the changes (new files, methods, dependencies), following the "Documentation First" protocol.
4. Developer saves both code and artifact changes.

### UC-03: New Skill Integration
**Actors:** System Maintainer (User/Agent)
**Preconditions:** A new recurring process is identified.
**Main Scenario:**
1. Maintainer creates a new skill directory in `.agent/skills/` (and duplicates to `.cursor/skills/`).
2. Maintainer adds `SKILL.md` with YAML frontmatter and instructions.
3. Maintainer optionally updates agent prompts to reference user the new skill if needed.

## 3. Non-functional Requirements
- **Consistency:** `.AGENTS.md` must strictly follow the defined template.
- **Traceability:** All changes to code must be reflected in local artifacts.
- **Compatibility:** Skills must work in both Antigravity and Cursor environments.
- **Preservation:** Original agent behaviors (e.g., Anti-Loop, Stub-First) must be preserved during refactoring.

## 4. Constraints and Assumptions
- **Single Writer:** Only the Developer agent is allowed to write/update `.AGENTS.md` files in code directories. Other agents only read.
- **Filesystem:** The system assumes a standard filesystem structure accessible by the agents.

## 5. Open Questions
- Are there any specific specific naming conventions for the skills beyond kebab-case? (Assumed kebab-case based on examples).
- Should existing `.AGENTS.md` files (if any) be migrated automatically? (Assumed manual migration or "as touched" basis).

