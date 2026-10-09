# TASK 117 — [LIGHT] The file mode refuses a slot archive of another task, reordered parts and spliced links, and stage 2 of framework-upgrade has a bound

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 117 |
| Slug | slot-archive-bound-and-stage2-review-bound |
| Mode | Light (one script and its tests, one workflow; no API, schema or dependency change). The operator asked for a fast fix of two records |
| Source | [WI-47](../backlog/wi-47-rebase-links-py-can-still-write-a-chosen-slug-into-a-slot-link.md), [WI-48](../backlog/wi-48-stage-2-of-framework-upgrade-has-no-bound-on-its-review-rounds.md); the operator's request of 2026-10-09 |
| Base revision | `9e407e5` |
| Closes | WI-47, WI-48 |
| Archive name | `task-117-slot-archive-bound-and-stage2-review-bound.md` |

## 1. Problem

**WI-47.** The file mode of `.agent/tools/rebase_links.py` runs with no prompt under
`Bash(python3 .agent/tools/rebase_links.py *)`. After TASK 116 three routes still write chosen
text into a link:

- `--slot` admits any slug of the grammar `_SLUG`. `--slot docs/TASK.md=docs/tasks/task-116-marker-chosen-words-here.md`
  on `[t](../TASK.md)` writes `task-116-marker-chosen-words-here.md`, exit 0.
- `_adds_parts` is a set test. `[a](one/two/three.md)` with `--from docs/two/one` writes
  `../two/one/one/two/three.md`.
- Two overlapping link matches are spliced into one. `[r]: ](x` writes `[r]: ../](x../x`.

**WI-48.** Stage 2 of `/framework-upgrade` (§3 step 4) has no bound on its review rounds. The
spec and plan audits have one each (`default_max: 3`, `on_exhaust: escalate_user`).

## 2. Requirements

| ID | Requirement | Verify |
|----|-------------|--------|
| R1 | With a `--slot`, each operand's name is `task-<ID>-<slug>.md` or `plan-<ID>-<slug>.md`, and its `<ID>-<slug>` equals that of each slot archive. Otherwise the file mode exits 2 before it opens an operand. | TC-1, TC-4 |
| R2 | The path parts of a rewritten link, other than `.` and `..`, are a tail of the authored link's parts, or, for a slot link, of the archive's. Otherwise exit 2, no write. | TC-2 |
| R3 | The rewritten text's length equals the text's length plus each rewrite's change of length. Otherwise exit 2, no write. | TC-3 |
| R4 | The archive steps of `skill-archive-task` (5.5, 7.6.5, Option B) still exit 0. | TC-4, measurement |
| R5 | `framework-upgrade` declares the loop `stage2-review-retry` (`default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user`). Stage 2 states the bound at the loop's site. | `check_loop_contract.py --strict` |
| R6 | Stage 2 states: a round that finds only LOW routes of a class that an earlier round of the run fixed proposes their scope for the TASK's residuals and a backlog record; the operator decides. | Review |
| R7 | Both CHANGELOG files record the change; WI-47 and WI-48 are closed in `docs/BACKLOG.md` and in their records. | Review |

## 3. Test obligations

All in `tests/test_script_guards.py`, class `TestRebaseLinksGuard`. Each refused case asserts exit
2, the reason in stderr, and the operand's text unchanged.

- **TC-1** A slot archive whose `<ID>-<slug>` differs from the operand's, and an operand whose name
  has no `<ID>-<slug>`.
- **TC-2** `[a](one/two/three.md)` with `--from docs/two/one`, and a repeated part.
- **TC-3** `[r]: ](x` and `<a href="](x">` with the files of WI-47 on disk.
- **TC-4** The Step 5.5 and Step 7.6.5 shapes exit 0. The ARC-6 tests of
  `.agent/tools/test_rebase_links.py` keep exit 1 for an absent archive of the operand's own name.

## 4. Measurement (R4)

`rebase_document_links` over 317 files of `docs/` moved one directory deeper: 306 rewrites, none
refused by the tail test of R2.

## 5. Out of scope

The splice in `rebase_document_links()` itself: `archive_protocol.py` calls it with temporary
paths, and R3 refuses its result in the file mode.
