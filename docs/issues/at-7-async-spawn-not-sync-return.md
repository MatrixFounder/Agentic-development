---
id: AT-7
type: known-issue
status: wontfix
opened_at: 2026-04-17
category: agent-teams
slug: at-7-async-spawn-not-sync-return
---

# Async spawn ≠ sync return

> **Closed 2026-10-28** (`wontfix`: superseded by the runtime). The record describes the runtime of the probe of 2026-04-17, with `TeamCreate`, `TeamDelete` and named teams under `~/.claude/teams/`. Claude Code 2.1.306 retired `TeamCreate` and `TeamDelete`: its binary lists both among retired tool names, and with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` neither is offered as a tool. A session has one implicit team, and `Agent` ignores its `team_name` parameter. In 2.1.306 the `Agent` tool runs each subagent in the background and notifies the lead when it completes. The constraint below was not probed again on 2.1.306. A Layer B workflow starts with a new probe, and files each constraint that still holds as a new record.

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Constraint**: `Agent(team_name, name, ...)` returns `"Spawned successfully. agent_id: ..."`
  immediately; teammate runs in background. Lead must poll the inbox file
  (`~/.claude/teams/<name>/inboxes/<recipient>.json`) or await an auto-delivered message turn.
- **Contrast**: Different contract from Layer A where `Agent` returns the subagent's result
  synchronously.
- **Related**: [Task status lag](at-2-task-status-lag.md),
  [Runtime sends structured JSON despite docs](at-9-runtime-sends-structured-json-despite-docs.md).
