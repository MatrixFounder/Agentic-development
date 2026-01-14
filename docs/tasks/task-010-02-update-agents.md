# Task 010.2: Update Agent System Prompts

## Use Case Connection
- UC-01: Agent Executes Task with Skills
- UC-02: Developer Updates Code and Artifacts

## Task Goal
Update system prompts to reference the new skills and remove duplicated logic, enforcing the "Single Writer" and "Documentation First" protocols.

## Changes Description

### Changes in Existing Files

#### File: `System/Agents/00_agent_development.md`
- Updates to reference `.agent/skills`.

#### File: `System/Agents/01_orchestrator.md`
- General updates to align with new structure.

#### File: `System/Agents/02_analyst_prompt.md`
- Integrate `requirements-analysis` skill.

#### File: `System/Agents/04_architect_prompt.md`
- Integrate `architecture-design` skill.

#### File: `System/Agents/06_agent_planner.md`
- Integrate `planning-decision-tree` and `tdd-stub-first` skills.

#### File: `System/Agents/08_agent_developer.md`
- Integrate `developer-guidelines`, `tdd-stub-first`, `docs-standards`.
- **Enforce**: Single Writer protocol for `.AGENTS.md`.

#### File: `System/Agents/10_security_auditor.md`
- Integrate `security-audit` skill.

## Test Cases

### Manual Verification
1. **TC-MAN-01:** Read updated prompts and verify skill references.

## Acceptance Criteria
- [ ] All listed prompts updated to use skills.
- [ ] Logic de-duplicated (moved to skills).
- [ ] Single Writer protocol explicitly stated.
