<!-- id: task-053-parallel-agent-architecture -->
# Task: Design Parallel Agent Architecture


## 0. Meta Information
- **ID**: task-053-parallel-agent-architecture
- **Status**: DONE
- **Date**: 2026-02-13
- **Context**: User Request for Claude Code-like Orchestrator Pattern.

## 1. Problem Description
The current Agentic Framework operates on a **Single-Threaded Sequential** model. The user wants to enable **Parallel Execution** where an Orchestrator Agent can spawn multiple sub-agents to handle independent tasks (e.g., Frontend vs Backend) simultaneously.

**Current Limitations:**
- Execution is serial (Analyst -> Architect -> Developer).
- Session state (`latest.yaml`) assumes a single active write lock.
- No native `spawn_agent` tool exposed (relies on `browser_subagent` or simulation).

## 2. Goals
- **Analyze** the gap between current generic tools and required parallel structure.
- **Design** a "Recursive Agent Spawning" architecture.
- **Propose** changes to `skill-session-state` to handle concurrency (e.g. file locking or SQLite).
- **Define** the interface for a `spawn_agent` mechanism using `run_command` or similar.

## 3. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features |
|----|-------------|------|--------------|
| **REQ-1** | **Shared State Management** | YES | 1.1 Concurrency-safe State (Locking/DB)<br>1.2 Multiple Active Sessions support<br>1.3 Shared Artifact Access (TASK.md) |
| **REQ-2** | **Agent Spawning Mechanism** | YES | 2.1 Standardized `spawn_agent` tool interface<br>2.2 CLI-based subprocess instruction<br>2.3 Context Injection (passing state to child) |
| **REQ-3** | **Orchestrator Logic** | YES | 3.1 Task Decomposition Strategy<br>3.2 Sub-agent Monitoring/Polling<br>3.3 Result Aggregation |
| **REQ-4** | **Safety & Limits** | NO | 4.1 Max concurrent agents<br>4.2 Resource limits (Token usage)<br>4.3 Recursion depth limits |

## 4. Use Cases

### UC-1: Orchestrator Spawns Two Agents
1. **User** asks for "Create Frontend and Backend".
2. **Orchestrator** creates `task-A-frontend.md` and `task-B-backend.md`.
3. **Orchestrator** calls `spawn_agent(task="task-A")` and `spawn_agent(task="task-B")`.
4. **Agents** run in parallel (via background process or sub-agent tool).
5. **Orchestrator** polls for completion.
6. **Orchestrator** merges results.

### UC-2: Shared State Locking
1. **Agent A** tries to write to `docs/TASK.md`.
2. **Agent B** tries to write to `docs/TASK.md`.
3. **System** enforces a lock or merge strategy to prevent data loss.

## 5. Acceptance Criteria
- [x] **Architecture Doc**: `docs/ARCHITECTURE.md` updated with "Parallel Agent Pattern".
- [x] **Skill Upgrade**: `skill-session-state` design for concurrency.
- [x] **Prototype Plan**: A concrete plan to implement the `spawn_agent` simulation using `run_command`.

## 6. Open Questions
- Does the underlying platform allow `run_command` to start a new Agent instance (is there a CLI for 'me')?
- How do we view the output of sub-agents? (Log files? shared buffer?)
