---
id: AT-3
type: known-issue
status: documented
opened_at: 2026-04-17
category: agent-teams
slug: at-3-one-team-per-session
---

# One team per session

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Constraint**: a lead session can manage only one team at a time.
- **Guidance**: Do not nest teams (e.g., a teammate spawning its own sub-team is not
  supported).
- **Related**: [No leadership transfer](at-4-no-leadership-transfer.md).
