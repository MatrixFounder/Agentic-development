---
id: WI-22
type: work-item
status: open
opened_at: 2026-10-02
slug: wi-22-plan-status-tokens-for-the-generated-plan-chart
effort: M
value: 'the generated plan chart shows which tasks are done and which are ready'
source: 'TASK 108 (mermaid-authoring-guidelines)'
---

# WI-22 — Plan status tokens for the generated plan chart

**Signal.** TASK 108 D11 deferred task status. The framework's plan chart therefore draws every
bar as waiting; completion lives in `.agent/sessions/latest.yaml`, which the chart does not read.
`plan_gantt.py` already accepts `status` in a JSON schedule (`done`, `in-progress`,
`not-started`).

**Option.** Add `status` to the schedule block of the plan template. The develop workflows set it
after an approved task and run `plan_gantt.py --write`. Four workflows change:
`03-develop-single-task.md`, `05-run-full-task.md`, `vdd-03-develop.md`, `vdd-05-run-full-task.md`.
`plan-review-checklist` gains the stale-status check.
