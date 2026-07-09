---
id: AT-9
type: known-issue
status: documented
opened_at: 2026-04-17
category: agent-teams
slug: at-9-runtime-sends-structured-json-despite-docs
---

# Runtime sends structured JSON despite docs

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Symptom**: docs say "Do NOT send structured JSON status messages like `{type: idle,...}`";
  the runtime itself auto-delivers `{"type":"idle_notification", ...}` and
  `{"type":"shutdown_approved", ...}` into the lead's inbox.
- **Guidance**: Parsers must handle both plain text and structured JSON.
- **Related**: [Async spawn ≠ sync return](at-7-async-spawn-not-sync-return.md),
  [`TeamDelete` does not clean up after protocol shutdown](at-6-teamdelete-does-not-clean-up-after-protocol-shutdown.md).
