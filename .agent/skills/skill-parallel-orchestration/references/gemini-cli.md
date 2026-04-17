# Parallel Orchestration — Gemini CLI reference

**Status**: **STUB — contribute when adopting**. Framework's universal concepts (parent `SKILL.md` §2–§6) are runtime-agnostic and apply unchanged; this file needs to be filled in with Gemini CLI–specific primitives.

**Loads with**: `SKILL.md` (parent skill) when `GEMINI.md` is present and no Claude Code markers are active.

---

## What this reference must provide (checklist)

To match the completeness of [`claude-code.md`](claude-code.md), this file should document:

- [ ] **Parallel-spawn primitive**: does Gemini CLI expose a single-invocation multi-agent spawn? If yes, its name + syntax. If no, explicitly note that and direct users to [`sequential-fallback.md`](sequential-fallback.md).
- [ ] **Teammate definition convention**: equivalent of `.claude/agents/<name>.md` — directory layout, frontmatter schema, body conventions.
- [ ] **Teammate type selector**: equivalent of `subagent_type` parameter.
- [ ] **Tools whitelist mechanism**: how per-teammate tool restrictions are declared and enforced.
- [ ] **Layer B support** (peer messaging): whether Gemini CLI has native teams / messaging between agents. If yes, how; if no, document that Layer B is unavailable and users must either use Layer A only or adopt a different runtime.
- [ ] **Verification pattern**: how to confirm the runtime actually ran teammates in parallel (Claude uses `requestId` check in JSONL). The equivalent here.
- [ ] **Known gotchas**: anything in [`docs/KNOWN_ISSUES.md`](../../../../docs/KNOWN_ISSUES.md) or vendor-specific equivalent.
- [ ] **Reference consumer**: link to a workflow that uses this reference (analogous to `.agent/workflows/vdd-multi.md` in the Claude Code case).

---

## Minimum viable content to unblock

If a full reference is not yet feasible, at minimum state:

1. Whether **any** parallel primitive exists; if not, note that all parallel-orchestration tasks should use [`sequential-fallback.md`](sequential-fallback.md).
2. The one-line summary of how teammate definitions are authored (file path + format) so that the framework's wrapper files (`.claude/agents/*`) can be ported or generated.

---

## Universal fallback

Until this reference is complete, agents on Gemini CLI should use [`sequential-fallback.md`](sequential-fallback.md) — all universal concepts apply, just slower wall-clock and with the single-session trade-offs documented there.

---

## Contribution guidance

Propose a PR to this file after running at least one concrete end-to-end task on Gemini CLI (analogous to the Claude Code smoke tests on `docs/tasks/task-dummy.md`). Include:

- JSONL/log evidence of parallel execution (or statement that it's sequential).
- Token-cost comparison vs the Claude Code reference implementation.
- Any new entries for [`docs/KNOWN_ISSUES.md`](../../../../docs/KNOWN_ISSUES.md).
