---
id: AT-1
type: known-issue
status: documented
opened_at: 2026-04-17
category: agent-teams
slug: at-1-no-session-resumption
---

# No session resumption

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Constraint**: `/resume` does not restore in-process teammates. After a session restart
  you must respawn the team from scratch.
- **Guidance**: Do not design workflows that assume teammate persistence across `/resume`.
- **Related**: [No leadership transfer](at-4-no-leadership-transfer.md),
  [`TeamDelete` does not clean up after protocol shutdown](at-6-teamdelete-does-not-clean-up-after-protocol-shutdown.md).
