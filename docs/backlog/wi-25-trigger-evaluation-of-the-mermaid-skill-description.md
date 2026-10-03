---
id: WI-25
type: work-item
status: dropped
opened_at: 2026-10-02
slug: wi-25-trigger-evaluation-of-the-mermaid-skill-description
effort: S
value: 'a measured trigger rate for the description, on the model that runs the skill'
source: 'TASK 108 (mermaid-authoring-guidelines)'
resolved_at: 2026-10-04
resolved_by: 'operator decision of 2026-10-04, after the skill-creator 2.4 guidance'
---

# WI-25 — Trigger evaluation of the mermaid skill description

> **Dropped 2026-10-04, by the operator's decision, without a paid run.** The description already
> follows the pattern that `skill-creator` 2.4 measured at 9 of 10 triggers: it quotes the user's
> own words («нарисуй схему», «добавь диаграмму», "draw a diagram", "mermaid"). In the framework
> the skill loads by rule, before the first figure of any output (`skill-phase-context`), so the
> description is the second way in, not the first. A run could only confirm the pattern.
>
> - **Not measured:** false triggers on near misses: charts of data, slides, a diagram in a
>   terminal reply.
> - **If the measurement is needed later:** the Option below names `run_eval.py`, whose log scan
>   cannot tell a skill that was not chosen from one chosen and not applied. Use the method of
>   `skill-creator/references/advanced-eval-patterns.md`, "Measuring a trigger by its effect":
>   four sets, with the rig check first, on the model that runs the skill.

**Signal.** The TASK 108 campaign loads the skill into the `with_skill` arm by construction, so
it measures guidance under perfect loading. Whether an agent loads the skill on its own is
untested. `skill-creator` measured description phrasing at 9 of 10 triggers for the user's own
words against 1 of 10 for a capability description.

**Option.** About 20 queries, mixed should-trigger and should-not-trigger, run with
`skill-creator/scripts/run_eval.py` on the model that runs the skill. Near misses: requests for
charts of data (the `dataviz` skill), slides, and diagrams in a terminal reply.
