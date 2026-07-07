---
description: Start a feature using the standard Stub-First pipeline
---
# Workflow: Base Stub-First Development

**Description:**  
Core pipeline with Stub-First and TDD. Used as foundation for others.

**Steps:**

1. **Analysis & Architecture Phase**:
    - Call `/01-start-feature`.
    - This handles:
        - Archiving old TASK.md
        - Creating new TASK.md (Analysis)
        - Updating ARCHITECTURE.md (Architecture)

2. **Planning Phase**:
    - Call `/02-plan-implementation`.
    - Creates PLAN.md and tasks/*.md using Stub-First strategy.

3. **Development Loop** (Automated):
    - Call `/05-run-full-task`.
    - Executes tasks, creating stubs first, then implementing logic.

4. Final validation and commit preparation.
