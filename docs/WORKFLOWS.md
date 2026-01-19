# Antigravity Workflows Manual

This document is the **Single Source of Truth** for all automation workflows in the Antigravity system. Workflows are defined in `.agent/workflows/` and can be executed by the Orchestrator to automate development processes.

## � Table of Contents

- [🚀 Workflow Categorization](#-workflow-categorization)
- [1. Pipelines (Meta-Workflows)](#1-pipelines-meta-workflows)
- [2. Automation Loops](#2-automation-loops)
- [3. Atomic Actions](#3-atomic-actions)
- [❓ FAQ](#-faq)
- [🛡 Safety & Verification](#-safety--verification)
- [📋 Getting Started: Workflow Call Sequences](#-getting-started-workflow-call-sequences)
  - [Approaches Overview](#approaches-overview)
  - [TDD (Test-Driven Development) Examples](#tdd-test-driven-development-examples)
  - [VDD (Verification-Driven Development) Examples](#vdd-verification-driven-development-examples)
  - [Quick Reference: Choosing Your Approach](#quick-reference-choosing-your-approach)
  - [Summary Table](#summary-table)

---

## �🚀 Workflow Categorization

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
| **VDD Multi-Adversarial** | Sequential execution of 3 specialized critics: Logic → Security → Performance. | `run vdd-multi` |

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

---

## 📋 Getting Started: Workflow Call Sequences

This section provides practical examples of how to execute workflows from start to finish.

### Approaches Overview

| Approach | Description | Best For |
| :--- | :--- | :--- |
| **One-Step (Pipeline)** | Single command runs entire lifecycle | Quick starts, trusted automation |
| **Multi-Step (Manual)** | Step-by-step execution with full control | Learning, debugging, critical projects |

---

### TDD (Test-Driven Development) Examples

#### One-Step Approach (Pipeline)

```bash
# Single command to run the entire Stub-First pipeline
run base-stub-first
```

**What happens automatically**:
1. Analysis → TASK created and reviewed
2. Architecture → ARCHITECTURE.md updated and reviewed
3. Planning → PLAN.md created and reviewed
4. Development Loop → All tasks executed with Developer ↔ Reviewer cycles

✅ **Pros**:
- Minimal user intervention required
- Fast for well-defined tasks
- Consistent execution every time

❌ **Cons**:
- Less visibility into intermediate steps
- Harder to pause and adjust mid-process
- May waste cycles if initial analysis is wrong

---

#### Multi-Step Approach (Manual Control)

```bash
# Step 1: Analysis Phase
run 01-start-feature
# → Review docs/TASK.md before proceeding

# Step 2: Architecture Phase (if needed)
# → Manually update docs/ARCHITECTURE.md or verify it's current

# Step 3: Planning Phase
run 02-plan-implementation
# → Review docs/PLAN.md before proceeding

# Step 4: Execute a single task
run 03-develop-single-task
# → Repeat for each task, or use the loop:

# Step 4 (Alternative): Execute all tasks automatically
run 05-run-full-task

# Step 5: Update documentation
run 04-update-docs
```

✅ **Pros**:
- Full control at every stage
- Can pause, review, and adjust between phases
- Better for learning the system
- Easier to debug failures

❌ **Cons**:
- More commands to remember
- Requires more user attention
- Slower overall execution

---

### VDD (Verification-Driven Development) Examples

#### One-Step Approach (Pipeline)

```bash
# Option A: VDD-Enhanced (Stub-First + Adversarial)
run vdd-enhanced

# Option B: Full Robust (VDD-Enhanced + Security Audit)
run full-robust
```

**What happens automatically**:
1. Full `base-stub-first` pipeline executes
2. Adversarial "Sarcasmotron" reviews all code
3. (Full Robust only) Security audit runs
4. Final documentation update

✅ **Pros**:
- Maximum code quality assurance
- Adversarial review catches hidden issues
- Security audit for production-ready code

❌ **Cons**:
- Takes longer due to multiple review cycles
- May be overkill for simple changes
- Sarcasmotron can be overly critical

---

#### Multi-Step Approach (Manual Control)

```bash
# Step 1: VDD Analysis Phase (with Chainlink Decomposition)
run vdd-01-start-feature
# → Review docs/TASK.md (structured as Epics → Issues)

# Step 2: VDD Planning Phase (Beads Decomposition)
run vdd-02-plan
# → Review docs/PLAN.md (structured as Epics → Issues → Sub-issues)

# Step 3: VDD Development with Adversarial Loop
run vdd-03-develop
# → Each task goes through Builder → Verification → Sarcasmotron Roast

# Step 4 (Optional): Run adversarial refinement on entire codebase
run vdd-adversarial

# Step 5 (Optional): Security audit
run security-audit

# Step 6: Update documentation
run 04-update-docs
```

✅ **Pros**:
- Granular control over VDD phases
- Can skip adversarial/security for low-risk changes
- Better understanding of what each phase does

❌ **Cons**:
- More complex than TDD multi-step
- Requires understanding of VDD concepts
- Easy to skip important verification steps

---

### Quick Reference: Choosing Your Approach

```mermaid
graph TD
    A[New Task] --> B{Task Complexity?}
    B -->|Simple/Well-defined| C{Trust Automation?}
    B -->|Complex/Ambiguous| D[Multi-Step Approach]
    C -->|Yes| E[run base-stub-first]
    C -->|No| D
    D --> F{Need Adversarial Review?}
    F -->|Yes| G[VDD Multi-Step]
    F -->|No| H[TDD Multi-Step]
    
    E --> I{Production-Critical?}
    I -->|Yes| J[run full-robust]
    I -->|No| E
```

### Summary Table

| Scenario | Recommended Command |
| :--- | :--- |
| Quick feature, trusted automation | `run base-stub-first` |
| Learning the system | TDD Multi-Step (`01` → `02` → `03/05` → `04`) |
| High-quality production code | `run vdd-enhanced` |
| Maximum code quality (3 critics) | `run vdd-multi` |
| Security-critical feature | `run full-robust` |
| Debugging a specific phase | Run that phase's atomic workflow |
| Just need analysis | `run 01-start-feature` or `run vdd-01-start-feature` |
