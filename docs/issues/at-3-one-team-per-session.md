---
id: AT-3
type: known-issue
status: wontfix
opened_at: 2026-04-17
category: agent-teams
slug: at-3-one-team-per-session
---

# One team per session

> **Closed 2026-10-28** (`wontfix`: superseded by the runtime). The record describes the runtime of the probe of 2026-04-17, with `TeamCreate`, `TeamDelete` and named teams under `~/.claude/teams/`. Claude Code 2.1.306 retired `TeamCreate` and `TeamDelete`: its binary lists both among retired tool names, and with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` neither is offered as a tool. A session has one implicit team, and `Agent` ignores its `team_name` parameter. One team per session is now the declared design of the runtime. The constraint below was not probed again on 2.1.306. A Layer B workflow starts with a new probe, and files each constraint that still holds as a new record.

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Constraint**: a lead session can manage only one team at a time.
- **Guidance**: Do not nest teams (e.g., a teammate spawning its own sub-team is not
  supported).
- **Related**: [No leadership transfer](at-4-no-leadership-transfer.md).
