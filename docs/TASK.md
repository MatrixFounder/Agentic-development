# TASK-058: Teams Mode Integration — Wave 1

**Status**: Done (smoke test passed 2026-04-17)
**Task ID**: 058
**Slug**: teams-mode-wave-1
**Created**: 2026-04-17
**Mode**: VDD (Verification-Driven Development)

## Summary

Parallelize the VDD Multi-Adversarial pipeline (`/vdd-multi`) by introducing thin Claude Code subagent wrappers (Option D) over existing adversarial skills. Preserve existing role-switching (Stage Cycle) and skills ecosystem. First iteration (Wave 1) covers three critics only; full agent-teams rollout is staged across Waves 2–5.

## Context

Framework currently has three disjoint approaches to "multi-agent":
1. **Role-switching personas** (`System/Agents/*.md`) — production, single Claude swaps prompts via Stage Cycle.
2. **POC parallel orchestration** (`spawn_agent_mock.py`) — mock agents, no real LLM spawn.
3. **Native Claude Code Agent Teams** — flag `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` enabled but unused.

Wave 1 closes the gap minimally: wraps three adversarial skills as `.claude/agents/critic-*` subagents, rewrites `/vdd-multi` to spawn them in parallel via native `Agent` tool, and stubs Layer B (native TeamCreate) for future Wave 4.

## Epic E1: Teams Mode Integration — Wave 1

### Issue I1: Create Critic Subagents (Layer A foundation)

**Acceptance**:
- `[R1]` `.claude/agents/critic-logic.md` — valid frontmatter, tools `Read,Grep,Glob`, body points to `.agent/skills/vdd-adversarial/SKILL.md` + mandatory template.
- `[R2]` `.claude/agents/critic-security.md` — valid frontmatter, tools `Read,Grep,Glob,Bash(git log:*),Bash(git diff:*),Bash(git show:*)`, body points to `.agent/skills/skill-adversarial-security/SKILL.md` + mandatory persona.
- `[R3]` `.claude/agents/critic-performance.md` — valid frontmatter, read-only tools, body points to `.agent/skills/skill-adversarial-performance/SKILL.md`.

### Issue I2: Parallel `/vdd-multi` workflow

**Acceptance**:
- `[R4]` `.agent/workflows/vdd-multi.md` Phase 1 instructs a single message with three parallel `Agent` tool-uses via `subagent_type: critic-logic|critic-security|critic-performance`. Phase 2 defines merge/dedup rules (location-based, severity escalation on cross-category overlap). Sequential fallback documented for non-Claude-Code vendors.

### Issue I3: Update skill-parallel-orchestration

**Acceptance**:
- `[R5]` `.agent/skills/skill-parallel-orchestration/SKILL.md` v2.0 — Phase 2 references native `Agent` tool (no mock); Layer B section present and marked `NOT IMPLEMENTED in Wave 1` with decision-rule criterion; `spawn_agent_mock.py` referenced as DEPRECATED.

### Issue I4: Orchestrator Teams Dispatch section

**Acceptance**:
- `[R6]` `System/Agents/01_orchestrator.md` §5.1 present with scenario→layer dispatch table; role-switching explicitly retained as primary mode.

### Issue I5: Archive POC

**Acceptance**:
- `[R7]` `docs/POC_PARALLEL_AGENTS.md` moved to `docs/archives/POC_PARALLEL_AGENTS.md` with SUPERSEDED header; `spawn_agent_mock.py` and `tests/test_mock_agent.py` have DEPRECATED module docstrings.

### Issue I6: Update ARCHITECTURE + KNOWN_ISSUES

**Acceptance**:
- `[R8]` `docs/ARCHITECTURE.md` §5 marked SUPERSEDED; §5.1 "Two-Layer Teams Model (Wave 1)" added with ASCII diagram and scope description.
- `[R9]` `docs/KNOWN_ISSUES.md` lists Native Teams gotchas (no session resume, task status lag, one team per session, no leadership transfer, higher token costs) + Wave 1 wrapper/SOT drift risk.

### Issue I7: TASK.md + CLAUDE.md

**Acceptance**:
- `[R10]` `docs/TASK.md` (this file) contains Epic E1 with all Issues and RTM acceptance criteria; `CLAUDE.md` has a note about parallel `/vdd-multi` in Claude Code vs. sequential fallback elsewhere.

### Issue I8: Verification

**Acceptance**:
- `[R11]` Smoke test (manual, in IDE): `/vdd-multi` on a fixture produces a single Agent-tool-use with three parallel subagents; each returns a structured report; orchestrator merges without duplicates.
- `[R12]` Regression: standard `/vdd` (sequential) still works — role-switching untouched.
- Docs coherence: all references to `spawn_agent_mock` / `POC_PARALLEL_AGENTS` either live in `docs/archives/` or are marked DEPRECATED.

## Out of Scope

- Wave 2: 9 dev-pipeline wrappers (analyst..security-auditor).
- Wave 3: 4 product-pipeline wrappers.
- Wave 4: Layer B (`TeamCreate`/`SendMessage` + `/teams-vdd-multi` workflow).
- Wave 5: portable generator `.agent/agents/ → per-vendor`.
- Changes to `01_orchestrator.md` beyond the Teams Dispatch section.
- Changes to `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` flag.

## References

- Detailed execution plan: `/Users/sergey/.claude/plans/swirling-drifting-feigenbaum.md`.
- Per-Bead task summary: `docs/tasks/task-058-teams-mode-wave-1.md`.
- Archived POC: `docs/archives/POC_PARALLEL_AGENTS.md`.
