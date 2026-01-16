---
description: Start a feature using the standard Stub-First pipeline
---
# Workflow: Base Stub-First Development

**Description:**  
Core pipeline with Stub-First and TDD. Used as foundation for others.

**Steps:**

1. **Analyst Phase**:
    - Call `/analyst-task`.
    - **Verification Loop**: Call `/task-review`.
    - If Rejection:
        - Re-run `/analyst-task` (revision mode).
        - **Retry (Max 2 attempts)**: Repeat Review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.

2. **Architecture Phase**:
    - Call `/architect-design`.
    - **Verification Loop**: Call `/architecture-review`.
    - If Rejection:
        - Re-run `/architect-design` (revision mode).
        - **Retry (Max 2 attempts)**: Repeat Review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.

3. **Planning Phase**:
    - Call `/planner-stub-first`.
    - **Verification Loop**: Call `/plan-review`.
    - If Rejection:
        - Re-run `/planner-stub-first` (revision mode).
        - **Retry (Max 2 attempts)**: Repeat Review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.

4. **Development Loop** (Automated):
    - Call `/05-run-full-task`.

5. Final validation and commit preparation.
