# Session Context Management (O7) - Authoritative Guide

> **Skill:** `skill-session-state` (TIER 0)
> **Status:** Active / System Foundation
> **File:** `.agent/sessions/latest.yaml`

This document explains the mechanism, rationale, and configuration of the Session Context system.

## 1. How It Works

1.  **Boot Protocol**: On session start, agents check `.agent/sessions/latest.yaml`. If found, they restore the last known state (`Mode`, `Task`, `Summary`).
2.  **Tracking**: Every time the `task_boundary` tool is called, the agent executes `update_state.py` to persist the new state atomically.
3.  **Conflict Resolution**: If the user's new prompt conflicts with the file (e.g., "Start task X"), the **User takes precedence**.
4.  **Multi-Task**: Completed tasks are tracked in the `completed_tasks` list to preserve history within a single session.

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

## 3. Degradation & Risk Analysis

I have adversarialy analyzed potential downsides:

### Risk A: "The Stale State Lie"
**Scenario:** Agent crashes *before* updating `latest.yaml`.
**Result:** On reboot, Agent restores a state that is 1 step behind reality.
**Mitigation:** `GEMINI.md` Conflict Resolution Rule (User > File). User says "No, we are done with that", Agent obeys.
**Verdict:** Manageable.

### Risk B: Confusion with IDE Features
**Scenario:** IDE has its own hidden prompting.
**Conflict:** Unlikely. `latest.yaml` is just a file. The Agent *reads* it voluntarily. It relies on the Agent Prompt (`01_orchestrator`), not the IDE binary.
**Verdict:** Low Risk.

### Risk C: Performance Overhead
**Cost:** Running `update_state.py` adds ~200ms to every `task_boundary` call.
**Verdict:** Negligible compared to LLM generation time (seconds).

## 4. Manual Override (Troubleshooting)

The session file is standard YAML. If the agent gets stuck or confused, you can edit it manually:

1.  Open `.agent/sessions/latest.yaml`.
2.  Change the `task_status` or `context_summary` to match reality.
3.  Save the file.
4.  Restart the chat window. The agent will read your "corrected" state.

**Tip:** You can also simply delete the file to force a "fresh start".

## 5. Deactivation Guide (How to Disable)

If you find this system conflicts with your workflow or IDE tools, you can disable it by downgrading the skill from **TIER 0** (Mandatory) to **TIER 2** (Optional).

### Step 1: Modifying Skill Metadata
1.  Open `.agent/skills/skill-session-state/SKILL.md`.
2.  Change `tier: 0` to `tier: 2`.

### Step 2: Removing Boot Instructions
1.  Open `GEMINI.md` and `AGENTS.md`.
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
