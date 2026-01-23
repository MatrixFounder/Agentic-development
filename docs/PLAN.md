# Implementation Plan - Light Mode

> **User Review Required:**
> - None. (Approved in Planning phase).

## Proposed Changes

### 1. Documentation Updates
#### [MODIFY] [GEMINI.md](file:///Users/sergey/Antigravity/agentic-development/GEMINI.md)
- Update **CRITICAL RULE**: "Even for small tasks, NEVER skip the Analysis and Architecture phases *UNLESS running in Light Mode (via `/light` workflow)*".
- Update **Dispatch**: Add instruction to propose `/light` for trivial tasks.

#### [MODIFY] [AGENTS.md](file:///Users/sergey/Antigravity/agentic-development/AGENTS.md)
- Update rules to reflect Light Mode existence.

#### [MODIFY] [WORKFLOWS.md](file:///Users/sergey/Antigravity/agentic-development/docs/WORKFLOWS.md)
- Add documentation for `/light` workflow.

### 2. Workflows
#### [NEW] [.agent/workflows/light-01-start-feature.md](file:///Users/sergey/Antigravity/agentic-development/.agent/workflows/light-01-start-feature.md)
- Steps:
    1. Analyst: Create TASK with `[LIGHT]` tag. Load `skill-light-mode`.
    2. Suggest transition to `light-02-develop-task`.

#### [NEW] [.agent/workflows/light-02-develop-task.md](file:///Users/sergey/Antigravity/agentic-development/.agent/workflows/light-02-develop-task.md)
- Steps:
    1. Developer (Loop): Implement + Test. (Verify `skill-light-mode` instructions).
    2. Code Reviewer: Sanity check.
    3. Orchestrator: Commit.

### 3. Skills
#### [NEW] [.agent/skills/light-mode/SKILL.md](file:///Users/sergey/Antigravity/agentic-development/.agent/skills/light-mode/SKILL.md)
- YAML: `tier: 2`
- Content:
    - Definition of Low Risk.
    - Developer Rules: "No overengineering", "Escalate if complex".
    - Reviewer Rules: "Security Sanity Check", "No architecture nitpicks".

## Verification Plan
### Manual Verification
- Run: `Call /light-01-start-feature` with a prompt "Fix typo in README".
- Validate:
    - Analyst runs.
    - Architect IS SKIPPED.
    - Planner IS SKIPPED.
    - Developer runs.
    - Code Reviewer runs.
