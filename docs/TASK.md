# TASK-060: Teams Mode Integration — Wave 3 (product-pipeline wrappers)

**Status**: Done
**Task ID**: 060
**Slug**: teams-mode-wave-3
**Created**: 2026-04-17
**Mode**: Continuation of Wave 1 (TASK-058, v3.10.0) and Wave 2 (TASK-059, v3.11.0)

## Summary

Extend `.claude/agents/` with 4 thin Claude Code subagent wrappers for the product-pipeline roles defined in `System/Agents/p01–p04`. Total wrapper count after Wave 3: **16** (3 critics + 9 dev-pipeline + 4 product-pipeline). No workflow rewrites — existing product workflows keep working through sequential role-switching; wrappers enable `subagent_type`-based spawn when useful.

## Epic: Teams Mode Integration

### Completed Waves

| Wave | Scope | Release | Task |
|---|---|---|---|
| Wave 1 | 3 critics + parallel `/vdd-multi` | v3.10.0 | [docs/tasks/task-058-teams-mode-wave-1.md](tasks/task-058-teams-mode-wave-1.md) |
| Wave 2 | 9 dev-pipeline wrappers | v3.11.0 | [docs/tasks/task-059-teams-mode-wave-2.md](tasks/task-059-teams-mode-wave-2.md) |
| Hardening | Thin-wrapper refactor (842 → 160 lines) + adversarial-review fixes + `task_id_tool.py` CLI main | v3.11.1 | (CHANGELOG only) |
| Opus upgrade | 8 verifiers → `model: opus` | v3.11.2 | (CHANGELOG only; smoke-verified) |
| **Wave 3** | **4 product-pipeline wrappers** | **v3.12.0** | **[docs/tasks/task-060-teams-mode-wave-3.md](tasks/task-060-teams-mode-wave-3.md)** |

### Remaining Waves

| Wave | Scope | Status |
|---|---|---|
| Wave 4 | Layer B (native `TeamCreate` + `/teams-vdd-multi` workflow) | Not started |
| Wave 5 | Portable generator (if second vendor added) | Conditional |

## Issue I1 — Create 4 product-pipeline wrappers

**Acceptance** (RTM):
- `[R1]` `.claude/agents/strategic-analyst.md` — builder (Read, Write, Edit, Grep, Glob; `model: sonnet`), SOT `System/Agents/p01_strategic_analyst_prompt.md`. Produces `docs/product/MARKET_STRATEGY.md`.
- `[R2]` `.claude/agents/product-analyst.md` — builder (same tools, `model: sonnet`), SOT `System/Agents/p02_product_analyst_prompt.md`. Produces `docs/product/PRODUCT_VISION.md`.
- `[R3]` `.claude/agents/product-director.md` — verifier-that-writes (Read, Write, Edit, Grep, Glob, Bash; `model: opus`), SOT `System/Agents/p03_product_director_prompt.md`. Adversarial-VDD gatekeeper; produces `APPROVED_BACKLOG.md` or `REVIEW_COMMENTS.md` + runs WSJF + sign-off scripts.
- `[R4]` `.claude/agents/solution-architect.md` — builder with APPROVAL_HASH entry check (Read, Write, Edit, Grep, Glob; `model: sonnet`), SOT `System/Agents/p04_solution_architect_prompt.md`. Produces `docs/product/SOLUTION_BLUEPRINT.md`.

## Issue I2 — Docs update

**Acceptance**:
- `[R5]` `docs/ARCHITECTURE.md` §5.1 — new Wave 3 table (4 rows); Model policy block updated to cover 10 Opus + 6 Sonnet (including product-director on Opus per verifier pattern).
- `[R6]` YAML frontmatter valid for all 16 wrappers.
- `[R7]` No regression — Wave 1/2 artifacts unchanged.

## Model policy (post-Wave 3)

**10 Opus verifiers + rigor roles**:
- Dev-pipeline reviewers: `task-reviewer`, `architecture-reviewer`, `plan-reviewer`, `code-reviewer`
- Adversarial critics: `critic-logic`, `critic-security`, `critic-performance`
- `security-auditor`, `planner`
- **Product gatekeeper**: `product-director`

**6 Sonnet builders**:
- Dev-pipeline: `analyst`, `architect`, `developer`
- Product-pipeline: `strategic-analyst`, `product-analyst`, `solution-architect`

## Out of scope (explicit)

- Workflow rewrites (product workflows stay sequential role-switching).
- `p00_product_orchestrator_prompt.md` — orchestrator role, main-agent only (native Teams no nested teams).
- Wave 4 and Wave 5.

## References

- Wave 3 task: `docs/tasks/task-060-teams-mode-wave-3.md`.
- Architecture: `docs/ARCHITECTURE.md` §5.1.
- Prior waves: `docs/tasks/task-058-*.md`, `docs/tasks/task-059-*.md`.
