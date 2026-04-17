# TASK-059: Teams Mode Integration — Wave 2 (dev-pipeline wrappers)

**Status**: Done
**Task ID**: 059
**Slug**: teams-mode-wave-2
**Created**: 2026-04-17
**Mode**: Continuation of Wave 1 (TASK-058, committed in v3.10.0)

## Summary

Extend `.claude/agents/` with 9 thin Claude Code subagent wrappers for the dev-pipeline roles defined in `System/Agents/02–10`. Builds on Wave 1 (three critics for `/vdd-multi`). No workflow rewrites — existing sequential role-switching flows keep working unchanged.

Total subagent wrappers after Wave 2: **12** (3 critics + 9 dev-pipeline).

## Epic: Teams Mode Integration

### Completed Waves

| Wave | Scope | Release | Task |
|---|---|---|---|
| Wave 1 | 3 critics + parallel `/vdd-multi` | v3.10.0 | [docs/tasks/task-058-teams-mode-wave-1.md](tasks/task-058-teams-mode-wave-1.md) |
| **Wave 2** | **9 dev-pipeline wrappers** | **v3.11.0** | **[docs/tasks/task-059-teams-mode-wave-2.md](tasks/task-059-teams-mode-wave-2.md)** |

### Remaining Waves

| Wave | Scope | Status |
|---|---|---|
| Wave 3 | 4 product-pipeline wrappers (`strategic-analyst`, `product-analyst`, `product-director`, `solution-architect`) | Not started |
| Wave 4 | Layer B (native `TeamCreate` + `/teams-vdd-multi` workflow) | Not started |
| Wave 5 | Portable generator (if second vendor added) | Conditional |

## Issue I1 — Create 9 dev-pipeline wrappers

**Acceptance** (RTM):
- `[R1]` `.claude/agents/analyst.md` — builder (Read, Write, Edit, Grep, Glob, git read-only), SOT `System/Agents/02_analyst_prompt.md`.
- `[R2]` `.claude/agents/task-reviewer.md` — read-only, SOT `System/Agents/03_task_reviewer_prompt.md`.
- `[R3]` `.claude/agents/architect.md` — builder, SOT `System/Agents/04_architect_prompt.md`.
- `[R4]` `.claude/agents/architecture-reviewer.md` — read-only, SOT `System/Agents/05_architecture_reviewer_prompt.md`.
- `[R5]` `.claude/agents/planner.md` — builder + `task_id_tool` Bash, SOT `System/Agents/06_planner_prompt.md`.
- `[R6]` `.claude/agents/plan-reviewer.md` — read-only, SOT `System/Agents/07_plan_reviewer_prompt.md`.
- `[R7]` `.claude/agents/developer.md` — full Bash, SOT `System/Agents/08_developer_prompt.md`.
- `[R8]` `.claude/agents/code-reviewer.md` — read-only + git read-only, SOT `System/Agents/09_code_reviewer_prompt.md`.
- `[R9]` `.claude/agents/security-auditor.md` — read-only + scanner Bash, SOT `System/Agents/10_security_auditor.md`.

## Issue I2 — Docs update

**Acceptance**:
- `[R10]` `docs/ARCHITECTURE.md` §5.1 lists all 12 wrappers (Wave 1 + Wave 2) with SOT + tools + role per row.
- `[R11]` YAML frontmatter validation passes for all 12 wrappers.
- `[R12]` No regression — Wave 1 artifacts (`/vdd-multi.md`, critic wrappers) unchanged; verified by `git diff`.

## Design principle — wrapper pattern (Option D)

All 12 wrappers follow the same pattern:
- **Frontmatter**: Claude Code subagent spec (`name`, `description`, `tools`, `model=sonnet`).
- **Body**: ≤ ~30 lines — SOT reference, mandatory skill loads (per SOT §2), return contract, guardrails.
- **SOT is authoritative**: wrappers don't duplicate methodology; changes live in `System/Agents/` or `.agent/skills/`.
- **Reviewers return text reports**: no broad filesystem Write; the orchestrator persists `docs/reviews/…` if needed. This mirrors Wave 1 critic pattern.

## Out of scope (explicit)

- Workflow rewrites (dev-pipeline stays sequential role-switching through the Stage Cycle).
- Orchestrator prompts (`01_orchestrator.md`, `p00_product_orchestrator_prompt.md`) — native Teams don't support nested teams, so these must stay as main-agent role personas.
- `00_agent_development.md` — meta-doc, not an agent.

## References

- Wave 1 task: `docs/tasks/task-058-teams-mode-wave-1.md`.
- Wave 2 task: `docs/tasks/task-059-teams-mode-wave-2.md`.
- Architecture: `docs/ARCHITECTURE.md` §5.1.
