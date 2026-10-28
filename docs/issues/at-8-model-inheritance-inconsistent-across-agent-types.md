---
id: AT-8
type: known-issue
status: wontfix
opened_at: 2026-04-17
category: agent-teams
slug: at-8-model-inheritance-inconsistent-across-agent-types
---

# Model inheritance inconsistent across agent types

> **Closed 2026-10-28** (`wontfix`: superseded by the runtime). The record describes the runtime of the probe of 2026-04-17, with `TeamCreate`, `TeamDelete` and named teams under `~/.claude/teams/`. Claude Code 2.1.306 retired `TeamCreate` and `TeamDelete`: its binary lists both among retired tool names, and with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` neither is offered as a tool. A session has one implicit team, and `Agent` ignores its `team_name` parameter. In 2.1.306 an `Agent` call without `model` takes the model of the agent definition, else the parent's model unless a default subagent model is set. The constraint below was not probed again on 2.1.306. A Layer B workflow starts with a new probe, and files each constraint that still holds as a new record.

> **Scope:** applies to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **Symptom**: spawning `subagent_type: "Explore"` as a teammate defaults to `model: "haiku"`
  regardless of lead's model.
- **Guidance**: If Opus is required for a teammate, pass `model` explicitly at spawn time.
