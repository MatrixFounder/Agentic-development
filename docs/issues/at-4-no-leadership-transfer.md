---
id: AT-4
type: known-issue
status: wontfix
opened_at: 2026-04-17
category: agent-teams
slug: at-4-no-leadership-transfer
---

# No leadership transfer

> **Closed 2026-10-28** (`wontfix`: superseded by the runtime). The record describes the runtime of the probe of 2026-04-17, with `TeamCreate`, `TeamDelete` and named teams under `~/.claude/teams/`. Claude Code 2.1.306 retired `TeamCreate` and `TeamDelete`: its binary lists both among retired tool names, and with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` neither is offered as a tool. A session has one implicit team, and `Agent` ignores its `team_name` parameter. The guidance on `TeamDelete` below has no tool to call. The constraint below was not probed again on 2.1.306. A Layer B workflow starts with a new probe, and files each constraint that still holds as a new record.

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Constraint**: cannot promote a teammate to lead or hand off the team.
- **Guidance**: The lead session that created the team must orchestrate cleanup via
  `TeamDelete`.
- **Related**: [One team per session](at-3-one-team-per-session.md),
  [`TeamDelete` does not clean up after protocol shutdown](at-6-teamdelete-does-not-clean-up-after-protocol-shutdown.md).
