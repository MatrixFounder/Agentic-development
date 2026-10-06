# TASK 113 — [LIGHT] The archive script pins the source inode during the move

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 113 |
| Slug | archive-move-pins-the-source-inode |
| Mode | Light (one-file bugfix; no API, schema or dependency change) |
| Source | The operator's request of 2026-10-06: fix the failing CI workflow |
| Base revision | `d40eff8` |
| Archive name | `task-113-archive-move-pins-the-source-inode.md` |

## 1. Problem

Run 37480167366 of `Framework Gates` on `main` (commit `d40eff8`) failed in the step "Run curated
unittest suite (incl. installer)" of the jobs `Tooling tests (3.11)` and `Tooling tests (3.14)`.
Two cases failed with `AssertionError: 0 != 1`:

- `test_archive_move.TestSwappedSource.test_a15_link_path_refuses_a_swapped_source`
- `test_archive_move.TestSwappedSource.test_a16_copy_path_refuses_a_swapped_regular_file`

Both cases pass on macOS.

**Cause.** `.agent/tools/archive_move.py` identifies the source by `(st_dev, st_ino)` only
(`_same_file`). It reads that pair with `os.stat` and holds no descriptor of the source. The test
unlinks `docs/TASK.md` and creates a new file under the same name. On the ext4 file system of the
GitHub runner, the new file receives the inode number that the unlink freed. The swapped file then
matches the recorded pair, and the script moves it with exit 0. APFS does not reuse a freed inode
number at once, so the defect does not appear on macOS.

The defect is in the script, not in the test: R1.3 of TASK 112 requires a refusal when the source
changes during the move, and on Linux an unlink-and-create swap passes the check.

## 2. Requirements

| ID | Requirement | Verify |
|----|-------------|--------|
| R1 | `_check_source` opens the source with `O_RDONLY \| O_NOFOLLOW \| O_NONBLOCK` relative to the `docs` descriptor, after the `lstat` checks, and refuses it when `fstat` of the descriptor does not match the `lstat` result. | TC-A15 to TC-A17 pass. |
| R2 | `_move` keeps that descriptor open until the move ends and closes it on every path. While the descriptor is open, the file system cannot assign the source's inode number to another file, so `(st_dev, st_ino)` identifies the source. | CI jobs `Tooling tests (3.11)` and `Tooling tests (3.14)` pass on Ubuntu. |
| R3 | A source that cannot be opened is refused with exit 1 and an error that names `docs/<name>`. | Full `tests/test_archive_move.py` passes. |
| R4 | The module docstring states that the source is held open from its open to the end of the move. | Review. |
| R5 | `_copy` opens the source with `O_NONBLOCK`, so a FIFO swapped in on the copy path does not block the script (code review, finding 1). | Review. |

## 3. Out of scope

- The tests of `tests/test_archive_move.py`. They state the required behaviour and stay unchanged.
- Other users of `(st_dev, st_ino)` in the repository.

## 4. Verification

1. `python3 -m unittest tests.test_archive_move -v` passes on macOS.
2. `PYTHONPATH=. python3 tests/run_tests.py` (the curated suite of the CI step) passes on macOS.
3. After the push, the `Framework Gates` run on `main` passes, including the Ubuntu jobs that
   reproduce the inode reuse.
