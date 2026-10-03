---
id: WI-25
type: work-item
status: open
opened_at: 2026-10-02
slug: wi-25-trigger-evaluation-of-the-mermaid-skill-description
effort: S
value: 'a measured trigger rate for the description, on the model that runs the skill'
source: 'TASK 108 (mermaid-authoring-guidelines)'
---

# WI-25 — Trigger evaluation of the mermaid skill description

**Signal.** The TASK 108 campaign loads the skill into the `with_skill` arm by construction, so
it measures guidance under perfect loading. Whether an agent loads the skill on its own is
untested. `skill-creator` measured description phrasing at 9 of 10 triggers for the user's own
words against 1 of 10 for a capability description.

**Option.** About 20 queries, mixed should-trigger and should-not-trigger, run with
`skill-creator/scripts/run_eval.py` on the model that runs the skill. Near misses: requests for
charts of data (the `dataviz` skill), slides, and diagrams in a terminal reply.
