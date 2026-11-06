---
id: WI-62
type: work-item
status: open
opened_at: 2026-11-06
slug: wi-62-an-orchestrator-that-dispatches-a-plan-s-tasks-itself-leaves-docs-plan-md-stale
effort: S
value: 'docs/PLAN.md shows the state of the work while the work runs, whoever dispatches its tasks'
source: 'whip-insight task-045 and task-046 (operator, 2026-11-05 and 2026-11-06)'
---

# WI-62 — An orchestrator that dispatches a plan's tasks itself leaves docs/PLAN.md stale

> Filed on the operator's request of 2026-11-06 (whip-insight, task-046: «правило по обновлению плана в процессе
> закрытия подзадач надо как-то добавить в сам framework Agentic development»). Behaviour change of the planning
> format and the orchestrator prompt, for the framework owner's review, not a landed fix.

**Signal.** In whip-insight the operator asked twice for `docs/PLAN.md` to be kept current during development:
- task-045 (2026-11-05): "update docs/PLAN.md also. It's outdated", the Gantt chart stale after several tasks had
  closed;
- task-046 (2026-11-06): «не забывай обновлять docs/PLAN.md по ходу работы».

In both tasks the orchestrator ran the plan itself: it started developer and reviewer agents through the Agent tool,
task by task and several chains in parallel, as the plan's own § Strategy and review gates prescribed. It did not run
`/03-develop-single-task` or `/05-run-full-task`. The plan's statuses, checklists and chart stayed at their planning
values until the operator asked.

**What the framework says at `db09229`.**
- `skill-planning-format` § 2.2 (TASK 110 R8) binds "a develop workflow": a task turns `in-progress` when it starts
  and `done` when its review approves it; after each status edit `plan_gantt.py --write`, then `--check`.
- The workflows that apply it: `03-develop-single-task.md` (steps 2 and the approval), `vdd-03-develop.md`
  (step 2.1), `vdd-05-run-full-task.md` (after a merge). `05-run-full-task.md` reaches it through `03`.
- `System/Agents/01_orchestrator.md` names no plan status and no chart. An orchestrator that dispatches the tasks
  itself is not "a develop workflow", so § 2.2 does not bind it.
- No rule ticks a task's checklist items (`- [ ]` → `- [x]`). `skill-spec-validator` reads the "Atomic Checklists"
  for RTM coverage only; `skill-planning-format` does not mention them after planning.
- `light-02-develop-task.md` names no plan status (a light task usually has no schedule block; § 2.2 step 4 skips
  it).

**Why it matters.** `docs/PLAN.md` is the one artifact the operator reads to see where a multi-task run stands. A
plan that shows every task `not-started` while half of them are reviewed misleads the operator, and a resumed session
that reads it misjudges what is left (the session state names the current task only). The cost of the rule is one
edit and two script runs per task boundary.

**Generalized.** Whoever starts a plan's task, a workflow or an orchestrator, keeps the plan's record of that task
current at each of the task's boundaries: start, hand-back, review verdict.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | § 2.2 binds every executor of a plan's task, the orchestrator included; `01_orchestrator.md` gains one rule that points to § 2.2 | S: two files | statuses and chart only; the checklists stay unticked |
| 2 | Option 1, plus § 2.2 ticks a task's checklist items when the task's deliverables are in place (at the hand-back that reports them, before the review), and keeps them ticked through a fix round | S: the same two files | one more edit per task; a reviewer that rejects a deliverable unticks its item |
| 3 | Option 2, plus an optional `## Progress` table (stage, state, evidence) that the planner may emit and § 2.2 keeps current | M: the planner prompt, the format, `plan_gantt.py` untouched | a third place that states progress; worth it only for plans of 8 or more tasks |
| 4 | Do nothing; the operator asks | — | the case above, recurring |

**Recommendation.** Option 2. It closes the observed gap at its cause (the rule's subject is "a develop workflow")
and covers the checklists the operator reads first. Option 3's table is what whip-insight's plans carried
(`docs/plans/plan-045-company-budget.md`, plan-046 § Progress); adopt it only if another project asks for it.

**Touch points.**
- `.agent/skills/skill-planning-format/SKILL.md` § 2.2: the subject becomes "whoever starts a plan's task"; a new
  item for the checklist ticks; the moments (start, hand-back, verdict).
- `System/Agents/01_orchestrator.md`: one rule beside its task-dispatch section that points to § 2.2.
- The workflows `03`, `vdd-03`, `vdd-05` keep their references; `05-run-full-task.md` may name § 2.2 directly when its
  loop dispatches without `03`.
- A contract test, if the framework pins § 2.2's text (TASK 110's tests), follows the new wording.
