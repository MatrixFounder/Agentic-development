# TASK-059: Teams Mode Integration — Wave 2 (dev-pipeline wrappers)

**Status**: Done (smoke-verified against v3.11.1 thin wrappers)
**Task ID**: 059
**Slug**: teams-mode-wave-2
**Created**: 2026-04-17
**Mode**: Continuation of Wave 1 (TASK-058, committed in v3.10.0)
**Post-release**: v3.11.1 thin-wrapper refactor (842 → 160 lines) — see CHANGELOG and smoke test verification below.

## Summary

Extend `.claude/agents/` with 9 thin Claude Code subagent wrappers for the dev-pipeline roles defined in `System/Agents/02–10`. Builds on Wave 1 (three critics for `/vdd-multi`). No workflow rewrites — existing sequential role-switching flows keep working unchanged.

Total subagent wrappers after Wave 2: **12** (3 critics + 9 dev-pipeline).

## Epic: Teams Mode Integration

### Completed Waves

| Wave | Scope | Release | Task |
|---|---|---|---|
| Wave 1 | 3 critics + parallel `/vdd-multi` | v3.10.0 | [docs/tasks/task-058-teams-mode-wave-1.md](tasks/task-058-teams-mode-wave-1.md) |
| **Wave 2** | **9 dev-pipeline wrappers** | **v3.11.0** | **[docs/tasks/task-059-teams-mode-wave-2.md](tasks/task-059-teams-mode-wave-2.md)** |
| Hardening | Thin-wrapper refactor + adversarial-review fixes; `task_id_tool.py` CLI main; removed bandit/colon Bash patterns | v3.11.1 | (CHANGELOG only) |

### Remaining Waves

| Wave | Scope | Status |
|---|---|---|
| Wave 3 | 4 product-pipeline wrappers (`strategic-analyst`, `product-analyst`, `product-director`, `solution-architect`) | Not started |
| Wave 4 | Layer B (native `TeamCreate` + `/teams-vdd-multi` workflow) | Not started |
| Wave 5 | Portable generator (if second vendor added) | Conditional |

## Issue I1 — Create 9 dev-pipeline wrappers

**Acceptance** (RTM; tools reflect post-v3.11.1 thin frontmatter — simple tool names; sub-command restrictions live in `.claude/settings.json` `permissions.allow`):
- `[R1]` `.claude/agents/analyst.md` — builder (Read, Write, Edit, Grep, Glob), SOT `System/Agents/02_analyst_prompt.md`.
- `[R2]` `.claude/agents/task-reviewer.md` — read-only (Read, Grep, Glob), SOT `System/Agents/03_task_reviewer_prompt.md`.
- `[R3]` `.claude/agents/architect.md` — builder (Read, Write, Edit, Grep, Glob), SOT `System/Agents/04_architect_prompt.md`.
- `[R4]` `.claude/agents/architecture-reviewer.md` — read-only, SOT `System/Agents/05_architecture_reviewer_prompt.md`.
- `[R5]` `.claude/agents/planner.md` — builder + Bash (uses `python3 .agent/tools/task_id_tool.py`), SOT `System/Agents/06_planner_prompt.md`.
- `[R6]` `.claude/agents/plan-reviewer.md` — read-only, SOT `System/Agents/07_plan_reviewer_prompt.md`.
- `[R7]` `.claude/agents/developer.md` — full access (Read, Write, Edit, Grep, Glob, Bash), SOT `System/Agents/08_developer_prompt.md`.
- `[R8]` `.claude/agents/code-reviewer.md` — read-only + Bash (for `git diff/log/show`), SOT `System/Agents/09_code_reviewer_prompt.md`.
- `[R9]` `.claude/agents/security-auditor.md` — read-only + Bash (for `run_audit.py`), SOT `System/Agents/10_security_auditor.md`.

## Issue I2 — Docs update

**Acceptance**:
- `[R10]` `docs/ARCHITECTURE.md` §5.1 lists all 12 wrappers (Wave 1 + Wave 2) with SOT + tools + role per row.
- `[R11]` YAML frontmatter validation passes for all 12 wrappers.
- `[R12]` No regression — Wave 1 artifacts (`/vdd-multi.md`, critic wrappers) unchanged; verified by `git diff`.

## Design principle — wrapper pattern (Option D, post-v3.11.1)

All 12 wrappers follow the **thin-adapter** pattern (current state after v3.11.1):
- **Frontmatter**: Claude Code subagent spec (`name`, `description`, `tools`, `model=sonnet`). Description starts with an infinitive action verb (`Transform`, `Review`, `Design`, `Decompose`, `Implement`, `Perform`) for predictable auto-routing.
- **Body**: **≤ 15 lines** (actual: 7–8 lines body) containing **only**:
  1. One-line SOT pointer: `You are the <Role> teammate. Full system prompt ... lives in [SOT path] — read and follow strictly.`
  2. `## Subagent adaptations`: 1–3 bullets covering **only what differs** from SOT when running as subagent vs main-agent role (primarily "return text report to orchestrator instead of writing `docs/reviews/…`").
- **SOT is authoritative**: wrappers do NOT duplicate skill lists, guardrails, Prime Directives, or return-format blocks. Edits to SOT propagate automatically on next subagent spawn.
- **Reviewers return text reports**: read-only tools (no `Bash` in frontmatter → cannot invoke shell at all). The orchestrator persists to `docs/reviews/…` or `docs/audit/…` if needed.

## Smoke test verification (post-v3.11.1, 2026-04-17)

v3.11.1 thin-wrapper refactor validated by in-session smoke test against [docs/tasks/task-dummy.md](tasks/task-dummy.md):
- Parallel spawn: single `requestId` across three critic `Agent` tool_uses (log `2babc138-…jsonl` → `req_011Ca9FA2hNt4PVJGVTYajEX`). ✅
- Seeded flaw coverage: critic-logic 2/2, critic-security 4/4, critic-performance 5/5. ✅
- Both expected overlaps detected (line 20 flaw #5, line 51/57 flaw #9); severity escalation applied per dedup rule 3. ✅
- Hallucinations: none. Bonus findings (path-traversal, missing input validation, conn pooling, returncode check, second-order SQLi, ambiguous types) legitimate and exceed Wave 1 baseline — evidence that thin wrappers do not lose SOT access.
- Fixture integrity: `git diff docs/tasks/task-dummy.md` empty. ✅

## Out of scope (explicit)

- Workflow rewrites (dev-pipeline stays sequential role-switching through the Stage Cycle).
- Orchestrator prompts (`01_orchestrator.md`, `p00_product_orchestrator_prompt.md`) — native Teams don't support nested teams, so these must stay as main-agent role personas.
- `00_agent_development.md` — meta-doc, not an agent.

## References

- Wave 1 task: `docs/tasks/task-058-teams-mode-wave-1.md`.
- Wave 2 task: `docs/tasks/task-059-teams-mode-wave-2.md`.
- Architecture: `docs/ARCHITECTURE.md` §5.1.
