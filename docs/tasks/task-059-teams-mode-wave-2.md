# Task 059 — Teams Mode Integration (Wave 2: dev-pipeline wrappers)

**Parent**: [docs/TASK.md](../TASK.md) history (Wave 2 follows Wave 1 / TASK-058)

## Goal

Extend `.claude/agents/` with thin Claude Code subagent wrappers for the 9 dev-pipeline roles defined in `System/Agents/02–10`. Wrappers expose each role for native `Agent` tool spawn + `/agents` discovery, with correct tools whitelist per role (builders get Write/Edit, reviewers stay read-only). No workflow rewrites — existing role-switching flows keep working unchanged.

## Scope

**Created (9 wrappers)**:
- `.claude/agents/analyst.md` → `System/Agents/02_analyst_prompt.md`
- `.claude/agents/task-reviewer.md` → `System/Agents/03_task_reviewer_prompt.md`
- `.claude/agents/architect.md` → `System/Agents/04_architect_prompt.md`
- `.claude/agents/architecture-reviewer.md` → `System/Agents/05_architecture_reviewer_prompt.md`
- `.claude/agents/planner.md` → `System/Agents/06_planner_prompt.md`
- `.claude/agents/plan-reviewer.md` → `System/Agents/07_plan_reviewer_prompt.md`
- `.claude/agents/developer.md` → `System/Agents/08_developer_prompt.md`
- `.claude/agents/code-reviewer.md` → `System/Agents/09_code_reviewer_prompt.md`
- `.claude/agents/security-auditor.md` → `System/Agents/10_security_auditor.md`

**Updated**:
- `docs/ARCHITECTURE.md` §5.1 — extended Layer A wrapper catalog (12 total with Wave 1 critics).

**Not in scope**:
- Workflow rewrites (unlike Wave 1 which rewrote `/vdd-multi`). Dev-pipeline remains sequential role-switching through the Stage Cycle; these wrappers are additionally available for parallel spawn when the orchestrator chooses.
- Wave 3 (product pipeline `p01–p04`) and Wave 4 (Layer B / native `TeamCreate`).

## Design decisions

### Tools whitelist per role

Strict principle: **builders write to their own artifact path; reviewers are read-only**.

- **Builders** (analyst, architect, planner): `Read, Write, Edit, Grep, Glob` + scoped git/tool Bash where SOT requires it (e.g. `task_id_tool` for planner).
- **Developer**: full `Bash` — needs to run tests, build, git ops, scripts. This is the one role with broad write authority.
- **Reviewers and critics** (task/arch/plan/code + Wave 1 critics): read-only (`Read, Grep, Glob` [+ `git` read-only for code-reviewer and security-auditor]). They **return text reports** to the orchestrator — the orchestrator persists to `docs/reviews/…` if needed. This mirrors Wave 1 critic pattern and prevents teammates from mutating each other's files.
- **Security-auditor**: read-only + scoped Bash for scanners (`run_audit.py`, `bandit`). Distinct from the Wave 1 `critic-security` which is a lighter parallel-critique version.

### No workflow changes

Dev-pipeline workflows (standard `01–04`, `vdd-*`, `develop-all`) continue to work as role-switching through the orchestrator. These Wave 2 wrappers **enable** parallel spawn when useful (e.g., parallel reviewer pairs, parallel developers for independent tasks via `/develop-all`) without mandating it. The orchestrator decides per-scenario.

## RTM (acceptance criteria)

- `[R1]` — `[R9]`: each wrapper exists with valid YAML frontmatter, correct `name` matching filename, tools whitelist per role, pointer to its SOT.
- `[R10]`: `docs/ARCHITECTURE.md` §5.1 lists all 12 wrappers with SOT and tools.
- `[R11]`: YAML validation passes for all 12 wrappers (Wave 1 + Wave 2).
- `[R12]`: existing `/vdd-multi` workflow still works (no regression — Wave 2 adds files, doesn't change vdd-multi.md).

## Verification

- **Frontmatter validation**: Python yaml-parse on all 12 wrappers → name matches filename, required fields present. ✅ Passed pre-commit.
- **Discovery** (manual, IDE): `/agents` shows all 12 wrappers with descriptions from frontmatter.
- **Tools whitelist** (manual, IDE): attempting Write inside a reviewer subagent fails with permission error.
- **Regression**: `/vdd-multi` workflow unchanged (verified by git diff: no files in `.agent/workflows/` modified).

## Out of scope reminder

- **Wave 3**: 4 product-pipeline wrappers (`strategic-analyst`, `product-analyst`, `product-director`, `solution-architect`).
- **Wave 4**: Layer B (`/teams-vdd-multi` with native `TeamCreate`/`SendMessage`).
- **Wave 5**: portable generator `.agent/agents/` → per-vendor.
- Orchestrator (`01_orchestrator.md`) and product-orchestrator (`p00`) remain role-switching — native Teams don't support nested teams, these must stay as main-agent roles.
