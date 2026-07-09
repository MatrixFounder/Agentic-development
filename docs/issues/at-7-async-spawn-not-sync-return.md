---
id: AT-7
type: known-issue
status: documented
opened_at: 2026-04-17
category: agent-teams
slug: at-7-async-spawn-not-sync-return
---

# Async spawn ≠ sync return

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Constraint**: `Agent(team_name, name, ...)` returns `"Spawned successfully. agent_id: ..."`
  immediately; teammate runs in background. Lead must poll the inbox file
  (`~/.claude/teams/<name>/inboxes/<recipient>.json`) or await an auto-delivered message turn.
- **Contrast**: Different contract from Layer A where `Agent` returns the subagent's result
  synchronously.
- **Related**: [Task status lag](at-2-task-status-lag.md),
  [Runtime sends structured JSON despite docs](at-9-runtime-sends-structured-json-despite-docs.md).
