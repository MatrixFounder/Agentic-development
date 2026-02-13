# Proof of Concept: Parallel Agent Architecture

## Overview
This POC demonstrates the **Parallel Orchestration Protocol**. While we cannot yet spawn "Smart" agents due to missing LLM infrastructure in the base environment, we have implemented the full **Control Flow** and **State Management** required for parallel execution.

## Components
1.  **Orchestrator Skill**: `.agent/skills/skill-parallel-orchestration`
2.  **Shared State**: `.agent/skills/skill-session-state` (with `fcntl` locking)
3.  **Mock Runner**: `scripts/spawn_agent_mock.py`

## How to Run the POC
You can verify the system by running the included test script, which simulates an Orchestrator spawning an agent:

```bash
python3 tests/test_mock_agent.py
```

### Expected Output
```text
Spawning Mock Agent...
[test-task-123] Starting... Goal: Verify infrastructure
[test-task-123] Finished. Result saved to docs/tasks/mock_results/test-task-123.result.md
Agent finished in 5.13s
SUCCESS: Result file created...
SUCCESS: Content valid.
```

## Manual Usage (Orchestrator Mode)
If you want to manually "Orchestrate" a parallel task:

1.  **Define Subtasks**: Create task files in `docs/tasks/`.
2.  **Spawn Agent 1**:
    ```bash
    python3 .agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py \
      --task_name "frontend-01" \
      --goal "Build Login Form" \
      --output_dir "docs/tasks/results" &
    ```
3.  **Spawn Agent 2**:
    ```bash
    python3 .agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py \
      --task_name "backend-01" \
      --goal "Build Auth API" \
      --output_dir "docs/tasks/results" &
    ```
4.  **Monitor**: Watch `.agent/sessions/latest.yaml` for status updates.

## Next Steps to "Real" Parallelism
To turn this POC into a real feature:
1.  **Install Libraries**: `pip install openai langchain`
2.  **API Keys**: Add `.env` with `OPENAI_API_KEY`.
3.  **Replace Mock**: Update `spawn_agent_mock.py` to import `skill-developer` and execute the goal using an LLM.

## Future Improvements

### Windows Compatibility
The current `fcntl`-based locking in `update_state.py` is POSIX-only (macOS/Linux). For Windows support:

```python
import platform

if platform.system() == "Windows":
    import msvcrt
    def lock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
    def unlock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl
    def lock_file(f):
        fcntl.flock(f, fcntl.LOCK_EX)
    def unlock_file(f):
        fcntl.flock(f, fcntl.LOCK_UN)
```

**Priority**: Low — the project currently targets macOS/Linux only.

### Additional Improvements
| Area | Description | Priority |
|------|-------------|----------|
| **LLM Agent Runner** | Replace `spawn_agent_mock.py` with actual LLM calls (`openai` / `langchain`) | High |
| **Resource Limits** | Max concurrent agents, token budget per sub-agent, recursion depth | Medium |
| **Result Merging** | Intelligent conflict resolution when agents modify shared files | Medium |
| **Error Recovery** | Retry logic, timeout handling, graceful degradation on sub-agent failure | Medium |
| **SQLite State** | Migrate from YAML+fcntl to SQLite for more robust concurrent state | Low |
| **Agent Output Viewing** | Structured log files or shared buffer for monitoring sub-agent progress | Low |

## Open Questions

> These are unresolved questions from the original task specification and VDD analysis.

1. **Platform CLI Availability**: Does the underlying IDE platform (`gemini`, `cursor`, `claude`) expose a CLI command to spawn a new agent instance programmatically? Without this, "real" parallelism requires an external LLM API call, not another agent session.

2. **Sub-Agent Output Visibility**: How should the Orchestrator view sub-agent outputs? Options:
   - Log files per agent (current approach: `docs/tasks/results/`)
   - Shared scrollback buffer
   - Structured JSON reports

3. **Hook Performance**: The skill validation hook fires on **every** file write operation (not just `.agent/skills/`). The early-exit adds ~100ms latency per call. If this becomes a bottleneck, consider a more selective matcher or async execution.

4. **Tool Schema Stability**: The hook relies on `.tool_input.TargetFile` field name. If future tool versions change the schema (e.g., `file_path`, `path`), validation will be silently skipped. Monitor for schema changes when upgrading the CLI.
