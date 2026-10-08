# TASK 114 — [LIGHT] A sub-task is told from its parent by the H1 first, by the filename second

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 114 |
| Slug | subtask-classified-by-h1 |
| Mode | Light (two tools, their tests, two skills; no API, schema or dependency change) |
| Source | The operator's request of 2026-10-07: KI-089 of n8n-lazy-loading-skills |
| Base revision | `9983c84` |
| Archive name | `task-114-subtask-classified-by-h1.md` |

## 1. Problem

The planner splits a sub-task further with a letter suffix: `task-033-05a-sqltest-db.md`, `08b`,
`33b`. `task_id_tool.py` reads a sub-task from the filename only:

- `.agent/tools/task_id_tool.py:78` `SUBTASK_FILENAME_RE = re.compile(r'^task-(\d{3,})-(\d+)-.+\.md$')`

`get_parent_archive_ids()` therefore counts `task-033-05a-sqltest-db.md` as a parent archive.
`task_id_tool.py "admission-core-v1" --proposed-id 033 --no-correction` returns `conflict` and
suggests 034, with no parent archive present. Following the suggestion renumbers a task that its
sub-tasks, plan, commits and ledgers cite as 033 (ARC-1). Observed in n8n-lazy-loading-skills on
2026-10-07, filed there as KI-089.

A filename rule of `(\d+[a-z]?)` is not a fix. The docstring of `get_parent_archive_ids()` keeps
`task-012-3d-viewer.md` a parent archive, and that rule reads `3d` as a sub-task id.

## 2. Classification rule

A file named `task-<ID>-*.md` in `docs/tasks/` is classified in this order:

1. Its first H1 reads `# Task <ID>-<SubID>` or `# Task <ID>.<SubID>`, followed by `:`, `—`, `–`,
   `- ` or the line end → a sub-task.
2. Its first H1 reads `# Task <ID>`, followed by `:`, `—`, `–`, `- ` or the line end → a parent.
3. Otherwise → the filename rule of `SUBTASK_FILENAME_RE`, unchanged.

- `<SubID>` is `\d+[a-z]?`. `Task` matches in any case.
- The H1 counts only when its `<ID>` equals the filename's ID as a number.
- A UTF-8 BOM, HTML comments, a leading YAML front matter and fenced code blocks are skipped
  before the first H1 is taken. An unclosed comment runs to the end of the head.
- Only a regular file is read, opened with `O_NONBLOCK | O_NOCTTY`, at most 16 KiB of its head.
- `<SubID>` letters are lowercase; `# Task 033-05A` is outside the grammar.

## 3. Requirements

| ID | Requirement | Verify |
|----|-------------|--------|
| R1 | `task_id_tool.py` classifies a file by §2. `get_parent_archive_ids()` returns the IDs of the files that §2 classifies as parents. | TC-1 to TC-5 |
| R2 | `get_existing_task_ids()` counts parents and sub-tasks of either shape, as before. | TC-6 |
| R3 | `archive_protocol.archive_task()` and `archive_plan()` archive a TASK whose sub-tasks carry letter suffixes under its own ID. | TC-7 |
| R4 | `archive_move.py` refuses an existing destination shaped like a letter-suffixed sub-task. | TC-8 |
| R5 | `skill-planning-format` §3 states the `<SubID>` grammar and the sub-task H1. The sub-task template writes `# Task {ID}-{SubID}: …`. | Review |
| R6 | `skill-archive-task` Step 3, Option B step 2, Step 5 and the Example Flow state the §2 rule. | Review |
| R7 | The skill versions and both CHANGELOG files record the change. | Review |

## 4. Test obligations

Each test writes its fixture files with the H1 given. TC-1, TC-3 and TC-7 fail on base `9983c84`.

- TC-1 — no parent; `task-NNN-05-x.md` and `task-NNN-05a-y.md` carry sub-task H1s → `--proposed-id NNN` returns `generated`.
- TC-2 — `task-NNN-slug.md` with H1 `# Task NNN: …` → `conflict`.
- TC-3 — `task-NNN-2024-migration.md` with H1 `# Task NNN: …` → `conflict`.
- TC-4 — `task-012-3d-viewer.md` with H1 `# Task 012: …` → a parent.
- TC-5 — a file with no H1, or with an H1 of another ID, is classified by its name.
- TC-6 — only letter-suffixed sub-tasks of NNN, no `proposed_id` → an ID other than NNN.
- TC-7 — `archive_task` + `archive_plan` on a fixture with sub-tasks `01`, `05a`, `08b` → `task-NNN-*` and `plan-NNN-*`.
- TC-8 — `archive_move.py docs/TASK.md docs/tasks/task-NNN-05a-x.md` with that file present → exit 1; the file is unchanged.

## 5. Decisions

- D1, 2026-10-07, agent: `archive_move.py` keeps its code. It refuses every existing destination,
  a sub-task file of either shape included. Rejected: a refusal by name — it also refuses the new
  archive `task-012-3d-viewer.md`.
- D2, 2026-10-07, agent: the H1 rule reads both `-` and `.` between `<ID>` and `<SubID>`. Sub-tasks
  006 to 096 of this repository use `.`; the plan template enumerates `Task {ID}.1`.

- D3, 2026-10-07, agent: code review round 1 findings 1–6 and 8 are fixed: digit strings compared
  without `int()`, an unclosed comment, a BOM, fences, the scan limit and the separators pinned by
  tests, `O_NOCTTY`. Not changed: finding 7 — the H1 overrides the name in both directions, as §2
  states; finding 9 — the auto-generation path also reads the heads.

## 6. Out of scope

- Re-targeting links to `docs/TASK.md` and `docs/PLAN.md` in other documents after the move
  (part 2 of the request, marked optional).
- The H1s of archived files in this repository.

## 7. Verification

1. `python3 -m pytest` in `.agent/tools/` passes.
2. `python3 -m unittest tests.test_archive_move -v` passes.
3. `PYTHONPATH=. python3 tests/run_tests.py` passes.
4. `python3 .agent/skills/skill-creator/scripts/validate_skill.py` passes for both edited skills.
