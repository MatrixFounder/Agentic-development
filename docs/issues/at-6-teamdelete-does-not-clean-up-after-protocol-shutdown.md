---
id: AT-6
type: known-issue
status: fixed
opened_at: 2026-04-17
resolved_at: 2026-10-28
resolved_by: 'Claude Code 2.1.306'
category: agent-teams
severity: SEV-2
slug: at-6-teamdelete-does-not-clean-up-after-protocol-shutdown
---

# `TeamDelete` does NOT clean up after protocol shutdown

> **Resolved 2026-10-28** (Claude Code 2.1.306). The record describes the runtime of the probe of 2026-04-17, with `TeamCreate`, `TeamDelete` and named teams under `~/.claude/teams/`. Claude Code 2.1.306 retired `TeamCreate` and `TeamDelete`: its binary lists both among retired tool names, and with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` neither is offered as a tool. A session has one implicit team, and `Agent` ignores its `team_name` parameter. The step that failed no longer exists, and the workaround below is not needed.

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Symptom** (verified Wave-4 probe, 2026-04-17): the shutdown round-trip works
  (`SendMessage({type: "shutdown_request"})` → teammate replies `shutdown_approved`), but
  `config.json` members array is NOT updated. `TeamDelete` then fails with
  `Cannot cleanup team with N active member(s)`. The error references `requestShutdown`
  which is not an available tool.
- **Impact**: This blocks any workflow that expects idempotent team lifecycle via
  `TeamDelete`.
- **Workaround**: manual `rm -rf ~/.claude/teams/<name>/ ~/.claude/tasks/<name>/`.
- **Related**: [No leadership transfer](at-4-no-leadership-transfer.md),
  [No session resumption](at-1-no-session-resumption.md).
