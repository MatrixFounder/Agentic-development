# Task 007.2: Implement Agent and Workflow Logic

## Use Case Connection
- UC-01: Execute Security Audit Workflow
- UC-03: Security Auditor Role Definition

## Task Goal
Fill the stub files with the actual content for the Security Auditor agent and workflow.

## Changes Description

### Modified Files
#### File: `System/Agents/10_security_auditor.md`
- Add "Security Auditor Role" header.
- Define "Core Principles".
- Define Input/Output format.

#### File: `.agent/workflows/security-audit.md`
- Add "Workflow: Security Audit" header.
- Define Steps (Gather Context, Static Analysis, Review).

## Implementation Details
- **Agent Prompt:** Use the content defined in `Backlog/task-007.md`.
- **Workflow:** Use the content defined in `Backlog/task-007.md`.

## Test Cases

### Manual Verification
1. **TC-MANUAL-01:** Read file content.
   - Command: `cat System/Agents/10_security_auditor.md`
   - Expected Result: Contains "Security Auditor Role".

## Acceptance Criteria
- [ ] Agent prompt contains full role definition.
- [ ] Workflow file contains full steps.
