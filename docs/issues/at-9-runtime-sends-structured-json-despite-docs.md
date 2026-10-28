---
id: AT-9
type: known-issue
status: wontfix
opened_at: 2026-04-17
category: agent-teams
slug: at-9-runtime-sends-structured-json-despite-docs
---

# Runtime sends structured JSON despite docs

> **Closed 2026-10-28** (`wontfix`: superseded by the runtime). The record describes the runtime of the probe of 2026-04-17, with `TeamCreate`, `TeamDelete` and named teams under `~/.claude/teams/`. Claude Code 2.1.306 retired `TeamCreate` and `TeamDelete`: its binary lists both among retired tool names, and with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` neither is offered as a tool. A session has one implicit team, and `Agent` ignores its `team_name` parameter. The constraint below was not probed again on 2.1.306. A Layer B workflow starts with a new probe, and files each constraint that still holds as a new record.

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Symptom**: docs say "Do NOT send structured JSON status messages like `{type: idle,...}`";
  the runtime itself auto-delivers `{"type":"idle_notification", ...}` and
  `{"type":"shutdown_approved", ...}` into the lead's inbox.
- **Guidance**: Parsers must handle both plain text and structured JSON.
- **Related**: [Async spawn ≠ sync return](at-7-async-spawn-not-sync-return.md),
  [`TeamDelete` does not clean up after protocol shutdown](at-6-teamdelete-does-not-clean-up-after-protocol-shutdown.md).
