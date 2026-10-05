---
id: WI-22
type: work-item
status: done
opened_at: 2026-10-02
slug: wi-22-plan-status-tokens-for-the-generated-plan-chart
effort: M
value: 'the generated plan chart shows which tasks are done and which are ready'
source: 'TASK 108 (mermaid-authoring-guidelines)'
resolved_at: 2026-10-05
resolved_by: 'TASK 110'
---

# WI-22 — Plan status tokens for the generated plan chart

> **Done 2026-10-05 (TASK 110).** The plan template writes `not-started`. `03-develop-single-task`,
> `vdd-03-develop` and `vdd-05-run-full-task` set `in-progress` and `done` and rewrite the chart by
> `skill-planning-format` §2.2. `05-run-full-task` gets the step through 03 (TASK 110 D7).
> `plan-review-checklist` checks the status of a new plan only (D11).

**Signal.** TASK 108 D11 deferred task status. The framework's plan chart therefore draws every
bar as waiting; completion lives in `.agent/sessions/latest.yaml`, which the chart does not read.
`plan_gantt.py` already accepts `status` in a JSON schedule (`done`, `in-progress`,
`not-started`).

**Option.** Add `status` to the schedule block of the plan template. The develop workflows set it
after an approved task and run `plan_gantt.py --write`. Four workflows change:
`03-develop-single-task.md`, `05-run-full-task.md`, `vdd-03-develop.md`, `vdd-05-run-full-task.md`.
`plan-review-checklist` gains the stale-status check.
