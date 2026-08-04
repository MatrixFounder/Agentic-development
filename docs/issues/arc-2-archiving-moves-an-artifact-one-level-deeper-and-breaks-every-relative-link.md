---
id: ARC-2
type: known-issue
status: fixed
opened_at: 2026-08-03
resolved_at: 2026-08-04
resolved_by: TASK 096 follow-up
category: archiving
severity: SEV-3
slug: arc-2-archiving-moves-an-artifact-one-level-deeper-and-breaks-every-relative-link
component: skill-archive-task
---

# ARC-2 — Archiving moves an artifact one level deeper and breaks every relative link

> **Resolved 2026-08-04.** New `.agent/tools/rebase_links.py`, invoked by `archive_protocol.py`
> after both moves and by `skill-archive-task` Steps 5.5 and 7.6.5. Corpus repaired: **45 broken
> links → 4**, and 19 silent mis-resolutions re-pointed. The 4 survivors are `PRE_BROKEN` — broken
> where they were authored, not by any move — and the tool refuses to guess at them:
> `task-047 → ./product_development_vision.md`, `task-061-02` and `task-062 → vdd-03-develop.md`.
> (`task-095 → docs/design/095_workflow_loop_contract.md` was a repo-root path written as a
> relative link; the file exists, so it was corrected by hand — the tool was right to refuse it.)
> Regression: `.agent/tools/test_rebase_links.py`, 36 cases, in CI.

> **Round-3 correction (2026-08-04): the tool's own verdict on the documented command was wrong.**
> Step 5.5 exited **1** — "a link regressed" — on the protocol's happy path. The conservation law
> filesystem-probed every rewritten target, including `SLOT_RESOLVED` ones. But a slot map is a
> **forward reference**: Step 5.5 names `docs/plans/plan-NNN-x.md`, which Step 7 creates
> afterwards. Read literally, the protocol told the agent to stop on success.
>
> `SLOT_RESOLVED` is now exempt from the conservation law — a declared identity is the caller's
> assertion, not a fact the tool should police mid-sequence — while a slot target that is not yet
> on disk is still printed as `[SLOT_PENDING]`, so a typo'd map stays visible. The closing
> validation of the protocol is where a wrong map is caught.
>
> This was reported by a critic in round 1 and **refuted in error**: the refutation ran
> `rebase_links.py` without `--slot`, which is not the documented command. It was found in round 3
> only because the stale `Example Flow` was rewritten and then executed. Pinned by
> `TestSlotTargetIsAForwardReference` (4 cases).

> **This record under-scoped the defect twice, and the second error was the dangerous one.**
>
> **1. The `../` signature was a minority shape.** The manual repair searched for `](../X)` and
> fixed 18. Measurement then found **45 more** broken links of the identical root cause carrying no
> `../` at all — `](TASK.md)`, `](tasks/task-063-01-installer-skeleton.md)`,
> `](ARCHITECTURE.md#9-…)`. The sentence below, *"Rewriting is mechanical because the depth delta
> is always exactly one"*, is wrong as a rule: a `../` → `../../` substitution fixes **zero** of
> those 45. The delta is an output of the rebase, never an input to it. The shipped rule is
> `relpath(normpath(join(old_dir, target)), new_dir)` — one expression covering every shape.
>
> **2. A mutable slot is not a file identity.** `docs/TASK.md` and `docs/PLAN.md` are slots that
> rotate. `**Parent**: [docs/PLAN.md](../PLAN.md)` inside `task-063-07` meant *task 063's* plan;
> it resolves today, to whatever plan is live. Preserving the **path** would have preserved the
> wrong thing and reported success. So the rewriter takes a slot map — the identity the slot held
> at that moment — and consults it **before** any filesystem probe, which is also what makes it
> work inside `archive_plan()`, where `docs/TASK.md` is already gone. 19 such references were
> re-pointed. Five were deliberately left: three name an epic TASK.md that was never archived, and
> two belong to task 061, which has no parent archive to point at.
>
> **3. Existence is the guard, not the trigger.** A link that resolved neither before nor after is
> never touched (`PRE_BROKEN`); one that resolves only from the new home is never touched
> (`ACCIDENTAL_RESOLVE`) — rewriting it would convert an accidentally-working link into a
> definitely-broken one. That row is also what makes a re-run a no-op.
>
> **4. Masking indented blocks as code hid 19% of the defect.** The first implementation blanked
> 4-space indents; in this corpus that is a lazy continuation of a `- [ ]` item, not a code block,
> and it silently skipped 8 of 42 links in one live plan. Only fenced blocks and inline spans are
> masked now, with a regression pin.

> Found when `check_positional_refs.py` went from green to 3 errors immediately after archiving
> TASK 095. A repo-wide sweep then found 18 broken links across 6 previously archived artifacts.

**Symptom.** `skill-archive-task` moves `docs/TASK.md` → `docs/tasks/task-NNN-slug.md` and
`docs/PLAN.md` → `docs/plans/plan-NNN-slug.md`. Both destinations are **one directory deeper** than
the source. Every relative link written as `](../X)` — correct from `docs/`, where it resolved to
repo root — now resolves to `docs/X` and points at nothing. The protocol's Step 6 and Step 7.7
validate only that the file arrived; nothing checks that its contents still resolve.

**Scale at time of filing.** 18 broken links in 6 files, every one carrying the same signature:

| File | Broken |
| :--- | ---: |
| `docs/tasks/task-062-vdd-develop-all.md` | 7 |
| `docs/plans/plan-063-framework-installer.md` | 4 |
| `docs/tasks/task-063-framework-installer.md` | 3 |
| `docs/plans/plan-061-vdd-develop-all.md` | 2 |
| `docs/tasks/task-048-product-migration-phase1.md` | 1 |
| `docs/tasks/task-049-phase-3-handoff.md` | 1 |

**Reproduction.**

```sh
grep -n '](\.\./' docs/TASK.md          # any link to repo root
mv docs/TASK.md docs/tasks/task-NNN-slug.md
python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py   # new errors
```

**Why it stayed invisible.** `check_positional_refs.py` only examines references carrying a line or
ordinal (`path:line`, `#L145`, `§4.4`). A plain `](../System/Agents/08_developer_prompt.md)` is not
checked by any gate, so 15 of the 18 had been broken for weeks with nothing reporting it.

**Fix applied 2026-08-03 (contents only, no protocol change yet).** All 18 rewritten `../` → `../../`
after confirming each corrected path resolves. No link was rewritten whose corrected form did not
exist. This restores what each document meant; it does not retro-fit anything new, so it does not
violate the archived-artifacts-are-immutable doctrine.

**Fix path (open).** Add a step to `skill-archive-task` between the `mv` and its validation: rewrite
relative links for the depth change, then assert every link in the moved file resolves. Rewriting is
mechanical because the depth delta is always exactly one. The alternative — requiring artifacts to
use repo-root-relative links — was not chosen: authors write `../` naturally while the document
still lives in `docs/`, and a rule against it would be violated silently.

**Related.** [[ARC-1]] (same component, ID generation); `documentation-standards` §4.1 (the gate that
caught it, and whose blind spot let 15 of 18 persist).

**Do-not.** Do not fix this by making `check_positional_refs.py` ignore archived directories. The
links are genuinely broken and the archive is the corpus most often read for precedent.
