# Parallel Orchestration — Antigravity reference

**Status**: **STUB — contribute when adopting**. Framework's universal concepts (parent `SKILL.md` §2–§6) are runtime-agnostic and apply unchanged; this file needs to be filled in with Antigravity-specific primitives.

**Loads with**: `SKILL.md` (parent skill) when an Antigravity runtime marker is detected and no other vendor markers are active.

---

## What this reference must provide (checklist)

To match the completeness of [`claude-code.md`](claude-code.md), this file should document:

- [ ] **Runtime identification**: what file/env var/directory signals "this is Antigravity" (so the parent SKILL.md's §1 selection table can match).
- [ ] **Parallel-spawn primitive**: does Antigravity expose multi-agent spawn? If yes, syntax. If no, default to [`sequential-fallback.md`](sequential-fallback.md).
- [ ] **Teammate definition convention**: equivalent of `.claude/agents/<name>.md`.
- [ ] **Teammate type selector**: equivalent of `subagent_type`.
- [ ] **Tools whitelist mechanism**.
- [ ] **Layer B support** (peer messaging).
- [ ] **Verification pattern**.
- [ ] **Known gotchas**.
- [ ] **Reference consumer** (analog of `.agent/workflows/vdd-multi.md`).

---

## Minimum viable content to unblock

If a full reference is not yet feasible, at minimum state:

1. The detection marker that identifies Antigravity runtime.
2. Whether parallel primitive exists; if not, point users to [`sequential-fallback.md`](sequential-fallback.md).

---

## Universal fallback

Until this reference is complete, agents on Antigravity should use [`sequential-fallback.md`](sequential-fallback.md).

---

## Contribution guidance

Propose a PR after running an end-to-end task on Antigravity. Include vendor marker details, parallel-execution evidence (or lack thereof), and any known-issue entries.
