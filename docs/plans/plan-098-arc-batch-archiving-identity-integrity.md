# Development Plan: TASK 098 — Archiving identity, ARC-3…ARC-12

**Target:** `docs/TASK.md` (TASK 098), 9 requirements, audit `docs/reviews/framework-audit-098.md`.
**Mode:** Framework Upgrade (Self-Improvement). Stub-First per `tdd-stub-first`.
**Primary files:** `.agent/tools/task_id_tool.py`, `.agent/tools/archive_protocol.py`,
`.agent/tools/rebase_links.py`, `.agent/skills/skill-archive-task/SKILL.md`.

## 0. Safety

**0.1 Backup** (before the first edit in Stage 2):

```sh
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done
for f in .agent/tools/task_id_tool.py \
         .agent/tools/archive_protocol.py \
         .agent/tools/rebase_links.py \
         .agent/tools/test_task_id_tool.py \
         .agent/tools/test_archive_protocol.py \
         .agent/tools/test_rebase_links.py \
         .agent/skills/skill-archive-task/SKILL.md \
         .claude/agents/planner.md \
         System/Docs/ORCHESTRATOR.md \
         docs/ARCHITECTURE.md; do
  cp "$f" ".agent/archive/$(basename $f).bak"
done
```

`.agent/archive/` is gitignored, so the backups leave `git status` clean.

**0.2 Rollback.** Restore any file from `.agent/archive/<basename>.bak`. The tracked copy is also in
git history at `5c9da31`, so `git checkout 5c9da31 -- <path>` is the second route.

**0.3 Baseline** (measured 2026-08-04, before any edit):

| Measure | Value |
| :--- | :--- |
| `python3 -m pytest .agent/tools/ -q` | 110 passed |
| `ORCHESTRATOR.md:284` states | `39 tests` |
| `rebase_links.py` reachable exit codes | 0, 2, 3 |
| Open `ARC-*` records | 10 |

<!-- contract:sequence -->

## Task Execution Sequence

### Stage 1 — Red: pin every defect before fixing it

**[R8] 1.1** Add `TestAllowCorrectionPolarity` to `.agent/tools/test_task_id_tool.py`. Four
behavioural cases against a temp `tasks_dir` holding one real parent archive:

- schema literal is `False`;
- `tool_runner.execute_tool` with `allow_correction` omitted returns `conflict`;
- `generate_task_archive_filename` called without the keyword returns `conflict`;
- the CLI run as a subprocess with no flag exits 1 and prints `conflict`.

Expected at this stage: cases 3 and 4 fail. Docstring names the revert that turns each red.

**[R8] 1.2** Add `TestMetaRefusalStopsTheArchive` to `.agent/tools/test_archive_protocol.py`:

- an ambiguous meta table (two 3-digit values) makes `archive_task` return `status: error`;
- `docs/TASK.md` still exists after that call;
- a meta block with an empty ID row archives and writes the ID back under a Russian label.

Expected at this stage: all three fail.

**[R8] 1.3** Add `TestSlotTargetMustExist` to `.agent/tools/test_rebase_links.py`:

- with the existence assertion on, a slot map naming an absent target exits 1;
- with it off, the same input exits 0 or 3.

Expected at this stage: the first fails.

**[R8] 1.4** Amend `test_task_id_tool.py:152` (`test_proposed_id_still_conflicts_with_a_real_parent`)
to pass `allow_correction=True` explicitly. Its intent is the correction path, and after R1 the
default no longer supplies it. This runs BEFORE Stage 2 so the suite goes red only on the new tests.

**Gate 1:** `python3 -m pytest .agent/tools/ -q` reports the new tests failing and no other test
newly failing.

### Stage 2 — Green: the four groups

**[R1] 2.1** `.agent/tools/task_id_tool.py:165` — `allow_correction: bool = False`. Update the
docstring line for the argument.

**[R1] 2.2** `.agent/tools/task_id_tool.py:291-301` — add `--allow-correction` (`store_true`). Keep
`--no-correction` accepting its now-default value per D1. Compute
`allow_correction = args.allow_correction and not args.no_correction`.

**[R3] 2.3** `.agent/tools/archive_protocol.py` `parse_task_meta` — return a refusal reason.
Add `id_ambiguous: bool` set when the structural read finds more than one 3-digit value, and
`slug_unreadable: bool` set when a meta block is present and no slug row is readable.

**[R3] 2.4** `.agent/tools/archive_protocol.py:244-249` — add the STOP branch the comment at
`:116-119` promises. On a refusal return `{"status": "error", "reason": "meta_unreadable", ...}` and
move no file. A meta block with no ID row is not a refusal and still auto-generates.

**[R4] 2.5** `.agent/tools/archive_protocol.py:286-291` — locate the write-back row inside the meta
region rather than by the English label `Task ID`. Write only when the region offers exactly one
empty value cell. Report the outcome in the result dict as `meta_id_written`.

**[R5] 2.6** `.agent/tools/rebase_links.py` — add `--slot-must-exist`. When set, a `SLOT_RESOLVED`
record whose target is absent sets `failed`. Retain the conservation probe per D3.

**[R5] 2.7** `.agent/tools/rebase_links.py:43-44` — rewrite the docstring exit table so every listed
code is reachable, naming the declared-present slot target as the exit-1 condition.

**Gate 2:** `python3 -m pytest .agent/tools/ -q` — all green, count ≥ 110 plus the new tests.

### Stage 3 — Protocol and cards

**[R6] 3.1** `.agent/skills/skill-archive-task/SKILL.md:149-152` — state the PLAN-slot condition:
the pairing is passed only when `docs/PLAN.md` exists. Cite `archive_protocol.py:363-366`.

**[R6] 3.2** `.agent/skills/skill-archive-task/SKILL.md:325-327` (Example Flow) — repeat the same
condition, so the copyable command and the rule agree.

**[R6] 3.3** `.agent/skills/skill-archive-task/SKILL.md:235-246` (Step 7.6.5) — add
`--slot-must-exist` to the command. By this point the TASK archive is on disk, so the assertion is
satisfiable and a mistyped slug is caught.

**[R6] 3.4** `.agent/skills/skill-archive-task/SKILL.md:216-219` (Step 7.4) — replace the
post-correction rule with the Meta-block rule that Steps 3 and 4 enforce. Name
`archive_protocol.archive_task(allow_renumber=True)` as the one path where a corrected ID survives.

**[R6] 3.5** `.agent/skills/skill-archive-task/SKILL.md:264` (Edge Cases) — rewrite the
`Corrected used_id` row to match 3.4.

**[R7] 3.6** `.claude/agents/planner.md:12` — replace the ID-generation instruction. The planner
reuses the parent TASK Meta ID for every sub-task filename, per `06_planner_prompt.md:40`.

**[R7] 3.7** `docs/ARCHITECTURE.md:169` — remove `(uses task_id_tool.py)` from the `planner` row.
After 3.6 the planner does not invoke it. `ARCHITECTURE.md` is a LIVING document, edited in place.

**Gate 3:** `grep -n "task_id_tool" .claude/agents/planner.md` returns no generate-an-ID instruction;
each SKILL.md line cited in A12 reads as specified.

### Stage 4 — Documentation

**[R9] 4.1** `System/Docs/ORCHESTRATOR.md:8` — state the shortest correct invocation. After R1 the
default refuses a conflict, so `--no-correction` is no longer required to obtain that behaviour.

**[R9] 4.2** `System/Docs/ORCHESTRATOR.md:284` — replace `39 tests` with the count Gate 2 reported.

**[R9] 4.3** `CHANGELOG.md` and `CHANGELOG.ru.md` — one paired entry naming the ten issue IDs.

**Gate 4:** A17 and A18 pass.

### Stage 5 — Ledger flip (last, after Gate 2 passed)

**[R8] 5.1** For each of ARC-3 … ARC-12: set `status: fixed`, add `resolved_at: 2026-08-04` and
`resolved_by: TASK 098`, and append a resolution blockquote. Existing body text is preserved
verbatim.

**[R8] 5.2** Update the ten matching index lines in `docs/KNOWN_ISSUES.md` in lockstep.

**Gate 5:** A16 passes; no `ARC-*` line reads `status: open`.

<!-- contract:coverage -->

## Use Case Coverage

| Use Case | Stage | Verified by |
| :--- | :--- | :--- |
| UC-1 archive against a taken ID | 2.1, 2.2 | A1, A2, A3 |
| UC-2 ambiguous non-English meta | 2.3, 2.4 | A6 |
| UC-3 empty ID row, non-English | 2.5 | A7, A8 |
| UC-4 mistyped slug in the slot map | 2.6, 3.3 | A9 |
| UC-5 task without a plan | 3.1, 3.2 | A10, A12 |
| UC-6 planner writes sub-task files | 3.6, 3.7 | A13 |

## Requirements Coverage (RTM)

| Req | Stages | Acceptance |
| :--- | :--- | :--- |
| R1 | 2.1, 2.2 | A1, A2, A3, A4 |
| R2 | 1.1 | A5 |
| R3 | 2.3, 2.4 | A6, A7 |
| R4 | 2.5 | A7, A8 |
| R5 | 2.6, 2.7 | A9, A10, A11 |
| R6 | 3.1–3.5 | A12 |
| R7 | 3.6, 3.7 | A13 |
| R8 | 1.1–1.4, 5.1, 5.2 | A14, A16 |
| R9 | 4.1–4.3 | A17, A18 |

## Ordering constraints

1. Stage 1 precedes Stage 2. A test written after its fix cannot show that the fix was needed.
2. Step 1.4 precedes 2.1. Without it the suite goes red on an expected change.
3. Stage 5 follows Gate 2. A ledger row that reads `fixed` before the gate passes misreports.
4. Step 4.2 follows Gate 2. The count it writes is the count Gate 2 reported.

## Verification per stage

| Gate | Command | Pass condition |
| :--- | :--- | :--- |
| 1 | `python3 -m pytest .agent/tools/ -q` | new tests fail, no other test newly fails |
| 2 | `python3 -m pytest .agent/tools/ -q` | all pass |
| 2b | manual revert of `tool_runner.py:292` default | the four-surface test turns red |
| 3 | `grep` per A12, A13 | cited lines read as specified |
| 4 | `grep` per A17, A18 | both present |
| 5 | `grep` per A16 | ten records and ten index lines agree |
| 6 | `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py docs/TASK.md docs/PLAN.md` | exit 0 |
| 7 | `git status --porcelain` | only intended paths listed |
