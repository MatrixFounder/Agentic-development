# Task 058 — Teams Mode Integration (Wave 1)

**Parent**: [docs/TASK.md](../TASK.md) (Epic E1)
**Plan**: `/Users/sergey/.claude/plans/swirling-drifting-feigenbaum.md`

## Goal

Implement Layer A (parallel `Agent` tool spawn) of the two-layer teams model for the VDD Multi-Adversarial pipeline. Three critic subagents (`critic-logic`, `critic-security`, `critic-performance`) spawned in parallel replace the current sequential role-switching in `/vdd-multi`.

## Context — files to read/edit

**Source of truth (read, do not modify)**:
- `.agent/skills/vdd-adversarial/SKILL.md` + `assets/template_critique.md`
- `.agent/skills/skill-adversarial-security/SKILL.md` + `references/prompts/sarcastic.md`
- `.agent/skills/skill-adversarial-performance/SKILL.md`

**Create**:
- `.claude/agents/critic-logic.md`
- `.claude/agents/critic-security.md`
- `.claude/agents/critic-performance.md`
- `docs/archives/POC_PARALLEL_AGENTS.md` (via `git mv`)

**Edit**:
- `.agent/workflows/vdd-multi.md` — parallel spawn + merge
- `.agent/skills/skill-parallel-orchestration/SKILL.md` — v2.0 rewrite (Layer A + Layer B stub)
- `System/Agents/01_orchestrator.md` — §5.1 Teams Dispatch section
- `docs/ARCHITECTURE.md` — §5 SUPERSEDED, §5.1 new
- `docs/KNOWN_ISSUES.md` — Native Teams gotchas
- `.agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py` — DEPRECATED docstring
- `tests/test_mock_agent.py` — DEPRECATED docstring
- `CLAUDE.md` — note about parallel `/vdd-multi`

## Steps

1. Create three critic wrappers with full frontmatter + body per plan templates.
2. Rewrite `/vdd-multi` workflow for parallel spawn (Phase 1: parallel `Agent` tool-uses; Phase 2: merge/dedup by location; Phase 3: iterative single-critic re-spawn).
3. Update `skill-parallel-orchestration` to v2.0 — replace mock-agent with native Agent, add Layer B stub.
4. Insert Teams Dispatch §5.1 into orchestrator prompt.
5. `git mv` POC doc to archives, add SUPERSEDED header.
6. Mark mock scripts DEPRECATED in docstrings.
7. Update ARCHITECTURE.md §5 (SUPERSEDED) and add §5.1 with ASCII diagram.
8. Populate KNOWN_ISSUES.md with Native Teams gotchas.
9. Create TASK.md (this task's parent).
10. Add CLAUDE.md note.

## Verification

- **Structural**: `ls .claude/agents/critic-*.md` → 3 files; YAML frontmatter parseable; required fields (`name`, `description`, `tools`, `model`) present.
- **Coherence**: `grep -rn 'spawn_agent_mock\|POC_PARALLEL_AGENTS'` — all hits are in `docs/archives/`, DEPRECATED docstrings, or version history in `SKILL.md`.
- **Workflow**: `.agent/workflows/vdd-multi.md` contains exactly 3 `subagent_type: critic-…` references.
- **Smoke (manual, IDE)**: `/vdd-multi` on a small module → one message with three parallel `Agent` tool-uses; merged report dedup'd by location.
- **Regression (manual, IDE)**: `/vdd` (non-multi) works unchanged — role-switching intact.
- **Discovery (manual, IDE)**: `/agents` lists three critic entries with the descriptions from their frontmatter.
- **Tools whitelist (manual)**: attempting `Write` inside a spawned critic subagent fails with a permission error.
