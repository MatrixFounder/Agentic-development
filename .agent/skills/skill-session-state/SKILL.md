---
name: skill-session-state
description: "Persist and restore agent session context (Mode, Task, Summary) to survive resets."
tier: 0
version: 1.0
---

# Session State Management

This skill provides the mechanism to persist your current working state to a file. This allows you to "reboot" from a seamless context state if the session window is reset.

## 1. The Session File
*   **Path**: `.agent/sessions/latest.yaml`
*   **Purpose**: Stores the exact arguments from your last `task_boundary` call, plus session metadata.
*   **Persistence**: surviving session clears, allowing you to pick up exactly where you left off.

## 2. Boot Protocol (Start of Session)
**IF** `.agent/sessions/latest.yaml` exists **AND** you are starting a new session (blank context):
1.  **READ** the file using `read_file` or `view_file`.
2.  **RESTORE** your state:
    *   Set your internal `Mode` to the file's `mode`.
    *   Set your `TaskName` and `TaskStatus` to the file's `current_task`.
    *   Read the `context_summary` to understand what you were doing.
    *   Check `active_blockers` to see if you were blocked.

## 3. Update Protocol (During Work)
**WHENEVER** you call the `task_boundary` tool, you **MUST** immediately follow it with a call to the `update_state.py` script.

### Command Syntax
```bash
python3 .agent/skills/skill-session-state/scripts/update_state.py \
  --mode "[Mode]" \
  --task "[TaskName]" \
  --status "[TaskStatus]" \
  --summary "[TaskSummary]" \
  --predicted_steps [PredictedTaskSize]
```

### Protocol Rules
1.  **Sync**: The arguments passed to the script MUST match the arguments you just passed to `task_boundary`.
2.  **Atomic**: Always call `task_boundary` first, then `update_state.py`.
3.  **No Hallucinations**: Do not invent values. Use the exact ones from your current context.

## 4. Task Switching Logic
If you finish one task and start another **in the same session**:
1.  **Archive History**: Ensure the old `docs/TASK.md` is archived (via `skill-archive-task`).
2.  **Update State**: Call `task_boundary` with the **NEW** Task Name.
3.  **Persist & Track**:
    *   Call `update_state.py` with the new task details.
    *   **CRITICAL**: Add the flag `--add_completed_task "[Old Task Name]"` to preserve history.
    *   Example: `...scripts/update_state.py ... --add_completed_task "Optimizing Database"`
    *   This ensures `latest.yaml` shows: *Current Task = UI Bug*, *Completed = [Database]*

## 5. Advanced Usage

### Adding Decisions
If you make a critical decision (e.g., "Chose Redux over Context API"), you can append it to the session log:
```bash
python3 ...scripts/update_state.py ... --add_decision "Chose Redux over Context API"
```

### Managing Blockers
*   **Add Blocker**: `--add_blocker "Waiting for API key"`
*   **Clear Blockers**: `--clear_blockers` (Use when unblocked)

## 6. Shared State Protocol (v2 - Concurrent)
> **For Parallel Agents**: When multiple agents run simultaneously, they must NOT overwrite each other's state in `latest.yaml`.

### Locking Mechanism
The `update_state.py` script now implements **Atomic File Locking** (`fcntl.lockf` on Unix).
- **Read**: Shared Lock (allow others to read).
- **Write**: Exclusive Lock (wait for others to finish).

### Safe Usage Pattern
1.  **Read State**:
    ```python
    # Pseudo-code
    with FileLock("latest.yaml", "r"):
        state = load()
    ```
2.  **Write State**:
    ```python
    # Pseudo-code
    with FileLock("latest.yaml", "w"):
        state = load() # Re-read to get latest
        state.update(my_changes)
        save(state)
    ```

