---
description: Automatically execute all tasks in the current PLAN.md
---
# Workflow: Run Full Task

**Description:**
Iterates through all defined tasks in `docs/PLAN.md` and executes them using the standard Developer -> Reviewer loop.

**Steps:**

1. **Read Plan**:
   - Read `docs/PLAN.md` to identify the list of tasks (Task X.1, Task X.2, etc.).

2. **Execution Loop** (For each Task):
   
   **A. Developer Phase**:
   - Call `/03-develop-single-task`.
     > Input: The specific task file (e.g. `docs/tasks/task-X-Y.md`).
     > Note: This atomic workflow includes Developer -> Reviewer loop.


3. **Finalization**:
   - Run Full Regression Suite (`pytest`).
   - If Pass: Commit changes.
