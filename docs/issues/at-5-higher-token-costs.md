---
id: AT-5
type: known-issue
status: by-design
opened_at: 2026-04-17
category: agent-teams
slug: at-5-higher-token-costs
---

# Higher token costs

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Constraint**: each teammate is an independent Claude session — costs scale ~linearly
  with team size.
- **Guidance**: Prefer Layer A for orthogonal critique where a peer mailbox is not required
  (see `skill-parallel-orchestration` §4 decision rule).
- **Related**: [Async spawn ≠ sync return](at-7-async-spawn-not-sync-return.md).
