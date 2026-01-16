# Antigravity Workflows Manual

This document is the **Single Source of Truth** for all automation workflows in the Antigravity system. Workflows are defined in `.agent/workflows/` and can be executed by the Orchestrator to automate development processes.

## 🚀 Workflow Categorization

The workflows are organized into three categories:

1.  **Pipelines (Meta-Workflows)**: High-level strategies that manage the entire lifecycle of a feature (Analysis -> Arch -> Plan -> Execution). **Start here.**
2.  **Automation Loops**: Engines that iterate through lists of tasks.
3.  **Atomic Actions**: Granular steps that perform a single phase.

---

## 1. Pipelines (Meta-Workflows)
*Use these to start a big chunk of work.*

| Workflow Name | Description | Command |
| :--- | :--- | :--- |
| **Standard Feature** | **Default Choice.** Runs the full "Stub-First" pipeline: Analysis, Architecture, Planning, and then Auto-Execution loop. | `run base-stub-first` |
| **Full Robust** | The Ultimate Pipeline: Runs `VDD Enhanced` strategy (Adversarial) followed by a Security Audit. | `run full-robust` |
| **VDD Enhanced** | Combines Stub-First planning with VDD Adversarial execution. | `run vdd-enhanced` |

---

## 2. Automation Loops
*Use these to execute a ready-made plan.*

| Workflow Name | Description | Command |
| :--- | :--- | :--- |
| **Run Full Task** | **The Loop Engine.** Reads `docs/PLAN.md`, iterates through all tasks, and executes `03-develop-single-task` for each one. Stops on error. | `run 05-run-full-task` |
| **VDD Develop** | The VDD Loop Engine. Runs the Adversarial "Sarcasmotron" loop for tasks. | `run vdd-03-develop` |

---

## 3. Atomic Actions
*Use these for granular control or manual overrides.*

| Workflow Name | Description | Command |
| :--- | :--- | :--- |
| **Start Feature** | Analysis Phase only (creates TASK). | `run 01-start-feature` |
| **Plan Impl** | Planning Phase only (creates PLAN). | `run 02-plan-implementation` |
| **Develop Task** | Executes a **single** task from the plan (No loop). | `run 03-develop-single-task` |
| **Update Docs** | Updates documentation artifacts. | `run 04-update-docs` |
| **Security Audit** | runs the security auditor agent. | `run security-audit` |

---

## ❓ FAQ

### Q: Why did `01-04` not loop through all tasks?
A: Because `03-develop-single-task` (formerly `03-develop-task`) is designed to be **atomic**. It performs one cycle of "Code -> Review -> Fix". It does **not** contain logic to read a list and iterate. To run the full list, you must use a **Pipeline** (like `base-stub-first`) which calls the **Automation Loop** (`05-run-full-task`).

### Q: How does `Run Full Task` work?
A: It parses `docs/PLAN.md`. For each entry (e.g., "Task 1.1"), it:
1.  Calls `03-develop-single-task` with that specific task ID.
2.  Waits for success.
3.  Moves to the next task.
4.  Verification is handled inside `03` (Developer <-> Reviewer loop).

---

## 🛡 Safety & Verification

All **Standard** automation workflows include **Mandatory Verification Loops** and **Safety Limits**:
1.  **Verification**: Every artifact (TASK, Architecture, Plan, Code) is checked by a specialized Reviewer Agent.
2.  **Retry Limit**: If a Reviewer rejects an artifact, the Doer gets **2 attempts** to fix it. If it fails a 3rd time, the workflow stops to request User intervention.
