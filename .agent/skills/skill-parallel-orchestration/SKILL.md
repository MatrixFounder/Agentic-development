---
name: skill-parallel-orchestration
description: "Use when decomposing tasks into parallel sub-tasks or spawning sub-agents."
tier: 2
version: 1.0
---

# Parallel Orchestration Skill

**Purpose**: Defines the protocol and tools for the **Orchestrator Role**, enabling the decomposition of large tasks into independent sub-tasks and their parallel execution via sub-agents (or mock agents).

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I can just run `python agent.py` directly." -> **WRONG**. You must use the `spawn_agent_mock.py` script to ensure shared state updates.
- "I don't need file locking." -> **WRONG**. Multiple agents writing to `latest.yaml` will corrupt the session state.
- "I'll just wait for all agents sequentially." -> **WRONG**. This defeats the purpose of parallelism. Spawn them in the background (`&`).

## 2. Capabilities
- **Decompose**: Split complex tasks into atomic `docs/tasks/subtask-*.md` files.
- **Spawn**: Launch independent agent processes that execute asynchronously.
- **Synchronize**: Read shared session state to track progress of all spawned agents.

## 3. Instructions

### Phase 1: Task Decomposition
1.  **Analyze** the user request.
2.  **Create** individual task files in `docs/tasks/` for each parallel unit of work.
3.  **Ensure** tasks are truly independent (no shared memory requirements other than final artifacts).

### Phase 2: Agent Spawning
1.  **Call** the Agent Runner script using `run_command`.
2.  **Use** the `&` operator to run in background.
    ```bash
    python3 .agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py \
      --task_name "subtask-A" \
      --goal "Implement Logic" \
      --output_dir "docs/tasks/results" &
    ```
3.  **Repeat** for all sub-tasks.

### Phase 3: Monitoring & Merging
1.  **Poll** `.agent/sessions/latest.yaml` (read only).
2.  **Wait** until all sub-tasks show status "Completed".
3.  **Read** result files from `docs/tasks/results/`.
4.  **Synthesize** final answer for the user.

## 4. Best Practices & Anti-Patterns

| DO THIS | DO NOT DO THIS |
| :--- | :--- |
| **Use Background Jobs** (`&`) | Run agents sequentially |
| **Check Session State** | Assume agents finished after X seconds |
| **Use Unique IDs** | Reuse task names (causes overwrite) |

## 5. Scripts and Resources
- `scripts/spawn_agent_mock.py`: **Mock Agent Runner**. Simulates LLM agent behavior (delay + file write) and updates session state.
