---
id: AT-8
type: known-issue
status: documented
opened_at: 2026-04-17
category: agent-teams
slug: at-8-model-inheritance-inconsistent-across-agent-types
---

# Model inheritance inconsistent across agent types

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Symptom**: spawning `subagent_type: "Explore"` as a teammate defaults to `model: "haiku"`
  regardless of lead's model.
- **Guidance**: If Opus is required for a teammate, pass `model` explicitly at spawn time.
