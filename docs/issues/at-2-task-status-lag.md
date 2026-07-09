---
id: AT-2
type: known-issue
status: documented
opened_at: 2026-04-17
category: agent-teams
severity: SEV-3
slug: at-2-task-status-lag
---

# Task status lag

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Symptom**: teammates sometimes fail to mark tasks complete in the shared task list,
  blocking dependent tasks.
- **Guidance**: Include a timeout + lead-side status audit when designing long-running teams.
- **Related**: [Async spawn ≠ sync return](at-7-async-spawn-not-sync-return.md).
