# Implementation Plan - O7 Session Context

## Goal
Implement a robust Session State mechanism that survives context resets.

## Architecture

### 1. Schema: `.agent/sessions/latest.yaml`
```yaml
session_id: "uuid"
last_updated: "ISO-8601"
mode: "PLANNING | EXECUTION | VERIFICATION"
current_task:
  name: "String"
  status: "String"
  predicted_steps: Int
context_summary: "String"
active_blockers: []
recent_decisions: []
completed_tasks: []  # NEW: Tracks history within session
```

### 2. Skill: `skill-session-state` (TIER 0)
- **Role**: Provide the mechanism (script) and the protocol (instructions).
- **Script**: `.agent/skills/skill-session-state/scripts/update_state.py`
  - Arguments: `--mode`, `--task_name`, `--task_status`, `--task_summary`, `--predicted_steps`
  - Logic: Load existing YAML -> Update fields -> Save (Atomic write).

### 3. Integration
- **Boot**: `GEMINI.md` and `AGENTS.md` must have a "Start Specific" instruction to read `.agent/sessions/latest.yaml`.
- **Runtime**: `task_boundary` calls should be followed by `run_command(python update_state.py ...)` (managed by the Agent).

## Steps

1. **Scaffold**: Create skill directory.
2. **Script**: Develop `update_state.py` using standard Python libraries (`yaml`, `argparse`, `pathlib`).
3. **Skill Doc**: Write `SKILL.md` defining the usage and TIER 0 status.
4. **Docs Update**: Register in `SKILL_TIERS.md`.
5. **Boot Update**: Modify `GEMINI.md` and `AGENTS.md`.
6. **Verify**: Test run.
