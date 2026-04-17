# Parallel Orchestration — Cursor reference

**Status**: **STUB — contribute when adopting**. Framework's universal concepts (parent `SKILL.md` §2–§6) are runtime-agnostic and apply unchanged; this file needs to be filled in with Cursor-specific primitives.

**Loads with**: `SKILL.md` (parent skill) when a `.cursor/` directory is present and no Claude Code markers are active.

---

## What this reference must provide (checklist)

To match the completeness of [`claude-code.md`](claude-code.md), this file should document:

- [ ] **Parallel-spawn primitive**: does Cursor Composer / agent-mode support a single-invocation multi-agent spawn? If yes, its name + syntax. If no, explicitly note that and direct users to [`sequential-fallback.md`](sequential-fallback.md).
- [ ] **Teammate definition convention**: equivalent of `.claude/agents/<name>.md` — Cursor uses `.cursor/rules/` for related concepts; clarify whether rules, composer modes, or something else is the teammate analog.
- [ ] **Teammate type selector**: equivalent of `subagent_type` parameter.
- [ ] **Tools whitelist mechanism**: how per-teammate tool restrictions are declared.
- [ ] **Layer B support** (peer messaging): whether Cursor agents can message each other mid-work. If no, document Layer B unavailability.
- [ ] **Verification pattern**: how to confirm parallel execution.
- [ ] **Known gotchas**.
- [ ] **Reference consumer**: link to a workflow that uses this reference.

---

## Minimum viable content to unblock

If a full reference is not yet feasible, at minimum state:

1. Whether **any** parallel primitive exists in Cursor Composer or agent-mode; if not, default to [`sequential-fallback.md`](sequential-fallback.md).
2. The file convention for per-teammate prompts (is it `.cursor/rules/*.mdc`? Composer system-prompt files? Something else?).

---

## Universal fallback

Until this reference is complete, agents on Cursor should use [`sequential-fallback.md`](sequential-fallback.md).

---

## Contribution guidance

Propose a PR to this file after running at least one concrete end-to-end task on Cursor (analogous to the Claude Code smoke tests on `docs/tasks/task-dummy.md`). Include:

- Evidence of parallel execution (or statement that it's sequential / per-chat).
- Token-cost comparison vs the Claude Code reference.
- Any known-issue entries.
