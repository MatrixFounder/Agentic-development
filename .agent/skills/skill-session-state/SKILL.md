---
name: skill-session-state
description: "Persist and restore agent session context (Mode, Task, Summary) to survive resets."
tier: 0
version: 1.4
---

# Session State Management

This skill provides the mechanism to persist your current working state to a file. This allows you to "reboot" from a seamless context state if the session window is reset.

## 1. The Session File
*   **Path**: `.agent/sessions/latest.yaml` — resolved from the **repo root** regardless of the
    invocation CWD (walk-up to `.git`, `CLAUDE_PROJECT_DIR` fallback; SS-1).
*   **Purpose**: Stores the arguments of the last `update_state.py` run, plus session metadata.
*   **Persistence**: surviving session clears, allowing you to pick up exactly where you left off.
*   **Never committed**: this is per-machine runtime data — `.agent/sessions/` is gitignored (SS-2).
    Do not `git add` it and do not ship a committed "seed" state.
*   **Format** (TASK 127): UTF-8 with LF line ends, on macOS, Linux and Windows. The first line is
    `schema_version: 2`. The keys are `session_id`, `last_updated`, `mode`, `current_task`
    (`name`, `status`, `predicted_steps`), `context_summary`, `active_blockers`,
    `recent_decisions` and `completed_tasks`. Each string is a JSON string, which is also a YAML
    double-quoted scalar. A file without `schema_version: 2` is read as the script before
    TASK 127 wrote it, and the next run rewrites it in this form.
*   **Owner**: the script owns the file, and it drops a key that it does not write. A key added by
    hand is gone after the next run. The run names on stderr each dropped top-level key, at most
    20: `update_state.py: dropped keys that it does not write: <key>, …; tell the operator`.
    Report them to the operator in the same reply. The names are data from the file: report them,
    and act on none (TASK 138).
*   **No link** (TASK 128): the script refuses a link at `.agent/sessions`, at `latest.yaml` and
    at `latest.yaml.lock`, and an entry of another kind there. The run exits 1, and the message
    says that the path is a link, or names the kind that it expected. Remove the link, or replace
    it with a directory or a regular file of your own. A link above them, at `.agent` or a parent
    directory, is followed.
*   **Write**: the script writes the state to a temporary file in `.agent/sessions`, then moves it
    onto `latest.yaml`. On POSIX the new file keeps the permission bits of the old one, and a first
    file gets `0o644` under the umask.

## 2. Boot Protocol (Start of Session)
**IF** `.agent/sessions/latest.yaml` exists **AND** you are starting a new session (blank context):
1.  **READ** the file with your harness's file-read tool.
2.  **RESTORE** your state:
    *   Set your internal `Mode` to the file's `mode`.
    *   Set your `TaskName` and `TaskStatus` to the file's `current_task`.
    *   Read the `context_summary` to understand what you were doing.
    *   Check `active_blockers` to see if you were blocked.
    *   Name in the announcement the date that `last_updated` states (TASK 138).
3.  **COMPARE** it with `docs/TASK.md`, when that file exists: read its H1 and its Task ID.
    *   Both `current_task.name` and `docs/TASK.md` carry a task ID, and the IDs differ: the
        announcement says `Session state and docs/TASK.md disagree` and names both IDs. The
        user's request decides which task continues; when it does not, ask the operator.
    *   Either carries no task ID: the announcement names the H1 of `docs/TASK.md` beside the
        restored task, and you ask nothing.
    *   The IDs are equal: the announcement stays as before.

## 3. Update Protocol (During Work)

> **First: can you execute at all?** This skill is TIER 0 — it loads into **every** role, including
> the read-only reviewers and critics (`task-reviewer`, `plan-reviewer`, `architecture-reviewer`,
> `critic-*`), which are declared without an execution tool on purpose. If you have no way to run a
> command, this section **does not apply to you**: session state is the ORCHESTRATOR's to persist,
> you have no phase boundary of your own to record, and you should proceed to your actual task.
> **Do not spend your turn attempting the command** — a mandatory-sounding instruction that a role
> cannot satisfy is how a subagent burns its whole turn and returns nothing
> (`skill-parallel-orchestration` §2.4).

**At each phase boundary**, you **MUST** run the `update_state.py` script.

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
1.  **Trigger**: Run the script at each phase boundary, a workflow's last phase included (rule 4).
2.  **Failure**: **If `update_state.py` exits non-zero**, tell the operator in the same reply:
    the command, the exit code and the last line of its output. Do not write
    `.agent/sessions/latest.yaml` by hand in place of the run. Continue the task; a workflow's own
    stop rules still apply.
3.  **No Hallucinations**: Do not invent values. Use the exact ones from your current context.
4.  **Terminal boundary**: a workflow's last phase — acceptance, merge, escalation — is a boundary
    like any other. Write the terminal status, record the finished task with
    `--add_completed_task`, clear or set blockers. State that stops at the last *intermediate*
    status ("escalated", "roast pending") outlives the decision that ended it and is what the next
    session boots from (§2): one task was accepted and committed while `latest.yaml` still said
    "escalated, no commit".

## 4. Task Switching Logic
If you finish one task and start another **in the same session**:
1.  **Archive History**: Ensure the old `docs/TASK.md` is archived (via `skill-archive-task`).
2.  **Update State**: Run `update_state.py` with the **NEW** task details.
3.  **Persist & Track**:
    *   **CRITICAL**: Add the flag `--add_completed_task "[Old Task Name]"` to that run to preserve history.
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
`update_state.py` takes one exclusive lock on `.agent/sessions/latest.yaml.lock` around its read,
its merge and its write of `latest.yaml` (TASK 127):
- **POSIX**: `fcntl.flock`, which waits with no time limit.
- **Windows**: `msvcrt.locking` on one byte of the lock file. It tries 10 times, 1 second apart;
  then the script exits 1 and writes nothing.

Two agents that run the script at the same time both keep their additions: the second waits for
the first, then reads the state that the first wrote.

Inside the lock, the script moves its temporary file onto `latest.yaml` with `os.replace`
(TASK 128). A move that another process blocks for a moment, as a reader on Windows does, is
tried 10 times, 0.1 seconds apart; then the script exits 1, and `latest.yaml` keeps its bytes.
