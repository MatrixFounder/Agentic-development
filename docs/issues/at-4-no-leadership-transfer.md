---
id: AT-4
type: known-issue
status: documented
opened_at: 2026-04-17
category: agent-teams
slug: at-4-no-leadership-transfer
---

# No leadership transfer

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Constraint**: cannot promote a teammate to lead or hand off the team.
- **Guidance**: The lead session that created the team must orchestrate cleanup via
  `TeamDelete`.
- **Related**: [One team per session](at-3-one-team-per-session.md),
  [`TeamDelete` does not clean up after protocol shutdown](at-6-teamdelete-does-not-clean-up-after-protocol-shutdown.md).
