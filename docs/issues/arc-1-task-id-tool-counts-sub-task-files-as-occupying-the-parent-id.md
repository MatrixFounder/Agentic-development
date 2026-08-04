---
id: ARC-1
type: known-issue
status: fixed
opened_at: 2026-08-03
resolved_at: 2026-08-04
resolved_by: TASK 096 follow-up
category: archiving
severity: SEV-3
slug: arc-1-task-id-tool-counts-sub-task-files-as-occupying-the-parent-id
component: task_id_tool
---

# ARC-1 — task_id_tool counts sub-task files as occupying the parent ID

> **Resolved 2026-08-04.** `skill-archive-task` Step 3 now passes the Meta-block id as
> `--proposed-id` with correction off; Step 4 asserts the id instead of assigning it;
> `archive_protocol.archive_task()` takes `allow_renumber=False` by default and parses the meta
> block whenever *either* field is missing; `tool_runner.py` defaults `allow_correction` to
> `False`. Reproduction re-run: sub-tasks `task-095-01..03` present, no parent — archived as
> **task-095**, not task-096. Regression: `.agent/tools/test_archive_protocol.py` +3 cases, and
> the file now runs in CI (see below).

> **This record's diagnosis was wrong, and the correction matters.** The title says the tool counts
> sub-task files as occupying the parent id. The tool has distinguished them since v3.21.2:
> `get_parent_archive_ids()` and `SUBTASK_FILENAME_RE` exist and are correct. That machinery is
> only reachable on the `--proposed-id` path, and **every documented way of calling the tool
> omitted it** — `skill-archive-task` Step 3 Option A literally showed
> `generate_task_archive_filename(slug="task-slug")`. So the "Fix path" proposed below is work
> already shipped; the real defect was in the protocol prose and in two policy defaults.
>
> Two further defects were found while fixing it, both now closed:
> - `archive_task()` parsed the meta block only `if current_task_slug is None`, so a caller
>   supplying a slug but no id fell through to auto-generation — ARC-1 reached through the
>   *automated* path, which this record called "already correct".
> - `parse_task_meta()` keyed on the English literals `Task ID` and `Slug`, so a non-English
>   TASK.md yielded no id and no slug and archived as `untitled` with an auto id. It now falls back
>   to a structural read of the `<!-- contract:meta -->` region, identifying rows by the shape of
>   their value rather than by their label. Latin behaviour is byte-identical.
>
> **Step 5 had no collision guard** while `SKILL.md` claimed one existed: `shutil.move` overwrites,
> and the tool's conflict check sees parent archives only, so a document whose meta read id 096 /
> slug `01-x` silently overwrote the planner sub-task `task-096-01-x.md`. Guard added; the claim in
> `SKILL.md` is now true.
>
> **The 86 tests protecting all of this ran nowhere.** `.github/workflows/framework-gates.yml`
> lists test files explicitly and named neither `test_task_id_tool.py` nor
> `test_archive_protocol.py`; `tests/run_tests.py` excluded them too. Both are now in the CI list.
>
> **Second-round finding (2026-08-04): this record was closed while four of five documented call
> sites still taught the defect.** The fix landed in `skill-archive-task` Step 3 and in
> `tool_runner.py`. But `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` and `System/Docs/ORCHESTRATOR.md`
> all still showed the bare `task_id_tool.py <slug>` form — and three of those are bootstrap files
> read at session start, before `skill-archive-task` is ever loaded. Re-measured by execution, not
> by reading: with `task-095-01..03` present and no parent, the bare form returns **096** and the
> protocol form returns **095**. That is ARC-1 unchanged, still reachable. All four now show
> `--proposed-id "<id>" --no-correction` and say why. Separately, `schemas.py` advertised
> `allow_correction` `"default": true` to the model while `tool_runner.py` used `False`, so an
> agent could omit the argument believing it had enabled the renumbering this issue forbids;
> the schema now reads `false`. Pinned by `TestBareInvocationShadowsTheParentId` (2 cases, one per
> form) and `TestSchemaMatchesTheDispatcher`.
>
> The lesson generalises past this issue: **a fix verified only where it was written is not
> verified.** The first pass measured the code path it had just changed and did not enumerate the
> other ways the tool is invoked.

> Observed while archiving TASK 095 at the start of TASK 096. The tool returned `096` for a
> document whose own Meta block, plan, and nine sub-task files all read `095`.

**Symptom.** `docs/tasks/` is shared between two kinds of file: the archived parent
(`task-NNN-slug.md`) and the Planner's sub-task files (`task-NNN-SubID-slug.md`). Both match the
`task-NNN` prefix. When a task has sub-task files, the ID scan sees `NNN` as taken and hands the
parent the next free ID.

The parent is then archived under an ID that contradicts its own Meta block, breaks the
`task-NNN` ↔ `plan-NNN` pairing that `skill-archive-task` guarantees, orphans the sub-task files
from their parent, and consumes the ID the next task is about to claim.

**Reproduction.**

```sh
cd <agentic-development-checkout>
ls docs/tasks/task-095*            # nine sub-task files, no parent
python3 .agent/tools/task_id_tool.py structural-anchors-and-gate-honesty
# {"used_id": "096", ...}  — expected 095, the ID this task already owns
```

**Impact.** Silent. The tool reports `"status": "generated"`, not a conflict, so an operator
following `skill-archive-task` Step 3 Option A archives under the wrong ID without a warning. It
is the same failure shape as the `untitled` slug degradation closed in TASK 095 R7: a wrong answer
returned confidently instead of an error.

**Workaround (used for TASK 095).** `skill-archive-task` Step 3 Option B — construct
`task-<meta-id>-<slug>.md` by hand, run the Step 5 / Step 7.5 collision guards, then `mv`.

**Fix path.** The ID scan must distinguish the two filename shapes. A parent is
`task-(\d{3})-(?!\d)`; a sub-task is `task-(\d{3})-(\d+)-`. Only parents and `docs/plans/plan-NNN-`
occupy an ID. Archiving should also prefer the ID already written in the document's Meta block and
report a conflict when it is taken, rather than silently renumbering a task whose ID is cited in
commits, CHANGELOG entries, and downstream ledgers.

**Related.** `skill-archive-task` Steps 3, 7.4 (the corrected-`used_id` rule assumes the tool's ID
is the trustworthy one); TASK 095 R7 (sibling silent-degradation defects in the same tool).

**Do-not.** Do not resolve this by forbidding sub-task files in `docs/tasks/` — the split is
deliberate and `skill-archive-task` documents it. Do not renumber already-archived tasks.
