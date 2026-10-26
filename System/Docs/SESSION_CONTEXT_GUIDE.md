# Session Context Management (O7) - Authoritative Guide

> **Skill:** `skill-session-state` (TIER 0)
> **Status:** Active / System Foundation
> **File:** `.agent/sessions/latest.yaml`

This document explains the mechanism, rationale, and configuration of the Session Context system.

## 1. How It Works

1.  **Boot Protocol**: On session start, agents check `.agent/sessions/latest.yaml`. If found, they restore the last known state (`Mode`, `Task`, `Summary`).
2.  **Tracking**: At every phase boundary, the agent executes `update_state.py` to persist the new state atomically.
3.  **Conflict Resolution**: If the user's new prompt conflicts with the file (e.g., "Start task X"), the **User takes precedence**.
4.  **Multi-Task**: Completed tasks are tracked in the `completed_tasks` list to preserve history within a single session.
5.  **Failure Rule**: If `update_state.py` exits non-zero, the agent tells the operator in the same reply: the command, the exit code and the last line of its output. It does not write `latest.yaml` by hand in place of the run, and it continues the task;
    a workflow's own stop rules still apply.
6.  **Disagreement Check**: At boot, when `current_task.name` and `docs/TASK.md` both carry a task ID and the IDs differ, the announcement says `Session state and docs/TASK.md disagree` and names both IDs. The user's request decides which task continues; otherwise the agent asks the operator. When either carries no task ID, the announcement names the H1 of `docs/TASK.md` beside the restored task.

## 2. Adversarial Analysis (The "Why")

*The following analysis was conducted to verify the necessity of this optimization.*

### The Core Problem: Context Truncation

| Scenario | Behavior WITHOUT O7 | Behavior WITH O7 |
|:---|:---|:---|
| **User clears chat** | Agent wakes up with **Amnesia**. "Hello. I see files, but I don't know what I was doing." | Agent reads `latest.yaml`. "Restoring state: I was midway through Task-123 in EXECUTION mode." |
| **Context Overflow** | LLM starts forgetting earliest instructions (the Task definition). | Agent has the Task Summary persisted in `latest.yaml` as a "cheat sheet". |
| **Crash/Restart** | User must re-explain: "We were debugging the login API." | Agent self-repairs: "Resuming debugging of login API." |

### Why .AGENTS.md is not enough

| Layer | File | Content | Volatility | Problem it Solves |
|:---|:---|:---|:---|:---|
| **Long-Term Memory** | `.AGENTS.md` | "This folder contains the Auth Logic." | **Static**. Rarely changes. | "What is this code?" |
| **Project Goal** | `docs/TASK.md` | "We need to build a Login Page." | **Stable**. Changes on edit. | "What are the requirements?" |
| **Session State (O7)** | `latest.yaml` | "I am currently editing `login.ts` and just ran a failed test." | **Volatile**. Changes every turn. | **"Where did I leave off?"** |

**Conclusion:** `.AGENTS.md` tells the agent *what the project is*. `latest.yaml` tells the agent *what it is doing right now*.

## 3. Conceptual Examples & Analogies

### The "Map vs GPS" Analogy
*   **`docs/TASK.md` is the Map**: It spans the entire region and shows where we want to go eventually.
*   **`latest.yaml` is the GPS Coordinates**: It tracks exactly where we are standing *right now* (e.g., "Lat/Long: 42.123, -71.456, Speed: 0").

### The "Bookmark" Analogy
Without O7, clearing the chat window is like closing a book and losing your page. You have to start reading from the Chapter 1 Index (`TASK.md`).
With O7, `latest.yaml` acts as a physical bookmark. You open the book and immediately know: *"I'm on Page 42, paragraph 3."*

### What Accumulates vs. What Updates
In long-running complex sessions, data behaves differently:

1.  **Accumulating History**:
    *   `completed_tasks`: "I already finished the DB, the API, and the Tests." (Prevents loops).
    *   `recent_decisions`: "We decided to use Postgres." (Prevents flip-flopping).
    *   `active_blockers`: "Still waiting for API key." (Persistent memory).

2.  **Snapshot State (Overwritten)**:
    *   `TaskStatus`: Always reflects the *current* moment. "Debugging login" overwrites "Writing login".

## 4. Degradation & Risk Analysis

I have adversarialy analyzed potential downsides:

### Risk A: "The Stale State Lie"
**Scenario:** Agent crashes *before* updating `latest.yaml`.
**Result:** On reboot, Agent restores a state that is 1 step behind reality.
**Mitigation:** `GEMINI.md` Conflict Resolution Rule (User > File). User says "No, we are done with that", Agent obeys.
**Mitigation (TASK 127):** two rules of §1. The failure rule: If `update_state.py` exits non-zero, the agent tells the operator in the same reply, and does not write the file by hand. The disagreement check: when the task IDs differ, the announcement says `Session state and docs/TASK.md disagree`. A team on Windows reported the case they close: the script failed at every phase boundary, and the state stayed three tasks old with no one told.
**Verdict:** Manageable.

### Risk B: Confusion with IDE Features
**Scenario:** IDE has its own hidden prompting.
**Conflict:** Unlikely. `latest.yaml` is just a file. The Agent *reads* it voluntarily. It relies on the Agent Prompt (`01_orchestrator`), not the IDE binary.
**Verdict:** Low Risk.

### Risk C: Performance Overhead
**Cost:** Running `update_state.py` adds ~200ms per phase-boundary persist.
**Verdict:** Negligible compared to LLM generation time (seconds).

## 5. Platform Memory Integration

Different AI coding platforms have their own memory/context systems. The framework's session state complements (not replaces) these:

| Layer | Mechanism | Purpose | Volatility |
|:---|:---|:---|:---|
| **Platform Memory** | Claude Code: `~/.claude/projects/*/memory/`, Cursor: composer history, Gemini: conversation context | Project patterns, preferences, long-term knowledge | Persistent across sessions |
| **Session State (O7)** | `.agent/sessions/latest.yaml` | Pipeline execution state: current phase, task, status | Ephemeral, updated every phase boundary |

**Key principle**: Platform memory answers "What do I know about this project?" Session state answers "What was I doing right now?"

Both systems are independent and complementary. Session state works identically across all supported platforms (Claude Code, Gemini CLI, Cursor IDE), on macOS, Linux and Windows.

## 6. Manual Override (Troubleshooting)

The session file is UTF-8 YAML, and its first line is `schema_version: 2`. If the agent gets stuck or confused, you can edit it manually:

1.  Open `.agent/sessions/latest.yaml`.
2.  Change `current_task.status` or `context_summary` to match reality.
3.  Save the file as UTF-8.
4.  Restart the chat window. The agent will read your "corrected" state.

**Tip:** You can also simply delete the file to force a "fresh start".

**Note:** the script drops a key that it does not write, so a key added by hand is gone after the next run. An agent never edits the file in place of a failed run of the script (§1, Failure Rule).

## 7. Deactivation Guide (How to Disable)

If you find this system conflicts with your workflow or IDE tools, you can disable it by downgrading the skill from **TIER 0** (Mandatory) to **TIER 2** (Optional).

### Step 1: Modifying Skill Metadata
1.  Open `.agent/skills/skill-session-state/SKILL.md`.
2.  Change `tier: 0` to `tier: 2`.

### Step 2: Removing Boot Instructions
1.  Open `GEMINI.md`, `AGENTS.md`, and `CLAUDE.md`.
2.  Delete the **"SESSION RESTORATION (BOOTSTRAP)"** section.
3.  Remove `skill-session-state` from the "Tier 0 Skills" list.

### Step 3: Reverting Agent Prompts
You must remove the reference from all 10 agent prompts:
1.  Run the following command (or edit manually):
    ```bash
    # Removes the line containing skill-session-state from all agent prompts
    sed -i '' '/skill-session-state/d' System/Agents/*.md
    ```

### Step 4: Cleanup
1.  Delete the session file: `rm .agent/sessions/latest.yaml`.

Once displayed, the agent will no longer attempt to read or write session state automatically.
