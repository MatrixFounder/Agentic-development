# TASK 133 — `run-feedback` runs on Windows, `mine` finds the transcripts of its root, and the residuals of TASK 132 close

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 133 |
| Slug | run-feedback-windows |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | the defect report of 2026-10-26 (TASK 127 §1); TASK 127 D1; TASK 132 D12 and §9; D1 |
| Base revision | `6e3076314a1a1f57310c8cb5c9a97bd1a18e8b81` |
| Closes | none; TASK 132 D12 residuals (R6) |
| Archive name | `task-133-run-feedback-windows.md` |
| Revision | 12 |

**Request.** TASK 127 D1 set native Windows support for the critical path in one area per task:
the session state (TASK 127, 128), the archive chain (TASK 131, 132), then `run-feedback`. This
task is the third area. The operator added the residuals of TASK 132 D12 and §9 to the scope, and
moved WI-39 to TASK 134 (D1).

**Why `/framework-upgrade`.** `run-feedback` is a TIER 2 skill, but R6 edits two scripts of the
archive chain that `skill-archive-task` (TIER 1) runs, and the Retro of `run-feedback` is a Global
Protocol of every workflow.

**Revision 12** follows the narrow round 4 of stage 2 and the operator's narrow round 5 (D11).
Before its ledger write, `file` checks the file that its move writes, and each failure of the move
runs the recovery of V17. A11a gains TC-RF31 and TC-RF32, and TC-RF28 a dangling link at
`dismissed/`.

**Revision 11** follows round 3 of stage 2 and the operator's narrow round 4 (D10). `file`
checks `inbox/`, `filed/` and `dismissed/` before any read and any write, a refusal of the move
runs the recovery of V17, and each directory is checked before its `mkdir`. A11a gains TC-RF28
to TC-RF30, and §9 the races of a check before an open.

**Revision 10** follows round 2 of stage 2. R3.2 also refuses a link at a directory between
`.agent/feedback/` and the file (H1), a FIFO, and a link seen before the open where `os` has no
`O_NOFOLLOW`. R2.3 knows no identity before the open, R1.7 takes the refusal of R3.2 as best
effort, R5.4 opens a session file without blocking, and A11a gains TC-RF25 to TC-RF27 and TC-MN8.

**Revision 9** follows round 1 of stage 2. R3.2 refuses a link or a second hard link at a file
of the machine state, on POSIX too, by the operator's decision D9 on the finding B1. R2.3 names
the rollback after a failed index write. R5.4 compares paths as text. A11a lists the tests that
the round added, and TC-EN4 reads the category, since the feed holds no title.

**Revision 8** applies MINOR-1 to MINOR-3 and N1 to N8 of the narrow Mode A round on revisions 5
to 7, which passed, with no further round. It adds R5.6, the `projects_dir` of `mine()`, and the
f-string check of A10.

**Revision 7** follows Mode B round 2. TC-RF20 checks the alternative of UC-2 with the mine of the
hook on, and requires the journal's lock in the log (R2-M1). R8.1 states the form of a test that
the `unittest` rules run (R2-M2), and TC-WN4 requires `LockTimeout` (R2-m5).

**Revision 6** follows Mode B round 1 of the PLAN. TC-EN5 holds `é` and checks ASCII bytes (M5).
R8.3 names its tests TC-WN1 to TC-WN5 (M12). TC-RF20 and TC-MN5 cover two alternatives of the use
cases (m9), and §9 names the probe of `heal-issues` (n9).

**Revision 5** follows the read of R8.5, done during planning. It adds R2.5, the close of the
descriptor before a rollback, and R4.5, a rooted path in the config. R8.5a lists the edits of the
suite, and A10 states that this machine has no Python 3.11. TC-EN1 tests the human output of
`init`: on `→` the JSON form of R7.1a and that of `backslashreplace` are the same text.

**Revision 4** applies MINOR-A to MINOR-C and N-a to N-e of Mode A round 3, which passed, with no
further round, on the precedent of TASK 127 revision 3.

**Revision 3** applies Mode A round 2 (FAIL): MAJOR-1 (JSON output is ASCII, R7.1), MINOR-1 to
MINOR-9 and N1 to N8. The tests of the workflow and of the two documents move to
`tests/test_session_state_contract.py` (MINOR-9).

**Revision 2** applies Mode A round 1 (FAIL): M1 to M6, m1 to m17 and n1 to n5. It adds R7
(text encoding) and R5.4 (the `cwd` filter), rewrites UC-2 for the SessionEnd path, and renumbers
the old R7 and R8 as R8 and R9.

In this document `F/` stands for `.agent/skills/run-feedback/scripts/`, and `L/` for
`F/feedback_lib/`. A coordinate into a file that this task edits carries the pin `@6e30763`, the
base revision.

<!-- contract:problem -->

## 1. Problem

`run-feedback` captures failures, files them into the two ledgers, and owns the retro claim of
every workflow. The runs of §8 on the base, with the Windows conditions emulated on macOS, give
these defects:

1. **Import.** Four modules import `fcntl` at their top: `F/run_feedback.py:30@6e30763`,
   `L/claims.py:13@6e30763`, `L/inbox.py:9@6e30763` and `L/journal.py:18@6e30763`. On Windows
   every command of `run_feedback.py` exits 1 with `ModuleNotFoundError` (§8, run 1). The retro
   claim of each workflow then fails.
2. **Silent hooks.** Both hooks catch every error and exit 0. With `fcntl` absent they write
   nothing and print nothing (§8, run 2):
   - `F/hooks/session_end_marker.py` journals the end of a session and, with
     `RUN_FEEDBACK_MINE_ON_END=1`, mines it. HK-1 records that PostToolUse does not fire on a
     failed Bash call, so this is the primary live capture path;
   - `F/hooks/posttooluse_filter.py` captures a failure envelope from a call that succeeded.
3. **Locks.** Six calls take `fcntl.flock`: `F/run_feedback.py:539@6e30763`,
   `L/claims.py:56@6e30763`, `L/claims.py:78@6e30763`, `L/claims.py:98@6e30763`,
   `L/inbox.py:135@6e30763` and `L/journal.py:68@6e30763`. `msvcrt` has no shared lock.
4. **Create-only write.** `L/ledger_core.py:209@6e30763` reads `os.O_NOFOLLOW`, which Windows
   lacks. `run_feedback.py file` exits 1 with `AttributeError` and a traceback, after every check
   passed (§8, run 4).
5. **Text mode.** On Windows `os.open` opens a descriptor in text mode unless the call passes
   `os.O_BINARY`, and the C runtime then writes each LF as CR LF. No `os.open` of `F/` passes it.
   `L/ledger_core.py:210@6e30763` also opens its text layer with `newline=None`, which writes
   `os.linesep`.
6. **Replace and unlink.** On Windows `os.replace` and `os.unlink` raise `PermissionError` while
   another process holds the file open without delete sharing. Each of these calls runs once:
   `L/atomic.py:97@6e30763`, `L/atomic.py:100@6e30763`, `L/inbox.py:159@6e30763` and
   `L/ledger_core.py:136@6e30763`.
   `L/atomic.py:78@6e30763` refuses a symbolic link at the target, and not a junction.
7. **Text encoding.** On Windows a pipe and a redirected stream use the ANSI code page:
   - `F/run_feedback.py:100@6e30763` prints JSON with `ensure_ascii=False`, and several messages
     hold `→`, which cp1251 and cp1252 cannot encode. Such a print raises `UnicodeEncodeError`;
   - both hooks read their JSON with `json.load(sys.stdin)`, which decodes UTF-8 bytes in the code
     page. A Cyrillic letter then raises `UnicodeDecodeError`, and the hook drops the event;
   - `_read_maybe_stdin` of `F/run_feedback.py:59@6e30763` reads `-` in the code page;
   - `L/config.py:100@6e30763` runs `git` with `text=True`, which decodes its output in the code
     page.
8. **`mine` matches no transcript directory.** `L/mine.py:39@6e30763` replaces `/` and `.` in the
   root's path with `-`. Claude Code 2.1.306 names a project's transcript directory by
   `replace(/[^a-zA-Z0-9]/g, "-")`, and cuts a name longer than 200 characters to 200, with `-`
   and a hash appended. `mine` then finds no directory and reports no transcript (§8, runs 5 and
   6):
   - on Windows for every root: `C:\Users\dev\app` stays `C:\Users\dev\app`;
   - on POSIX for a root whose path holds a character outside `[A-Za-z0-9/.]`, such as a space,
     `_` or a Cyrillic letter.
9. **`mine` reads other projects.** `L/mine.py:48-49@6e30763` also matches each directory whose
   name starts with the root's name and `-`. The root `/home/u/app` matches the transcripts of
   `/home/u/app-old` and `/home/u/app.bak`. The naming rule of item 8 cannot be reversed, so the
   name alone cannot tell a sub-directory of the root from a sibling.
10. **Tests that run nowhere.** `F/tests/` holds 333 tests (§8, run 7). No step of
    `.github/workflows/framework-gates.yml` names them, and `tests/run_tests.py` does not load
    them.
11. **TASK 132 residuals.** TASK 132 D12 and §9 leave three items:
    - no test pins that the check of TASK 132 R2.4 runs before any operand is read;
    - the module docstring of `.agent/tools/rebase_links.py` and the docstring of
      `_refuse_operand` name no path that names a device;
    - on Python 3.11 for Windows, `os.lstat` of a junction named after a device may report the
      device. `entered` of `.agent/tools/slot_links.py:186@6e30763` checks `_is_link` only, so
      the walk may enter the junction.
12. **A rooted path in the config.** `_contained` of `L/config.py:128@6e30763` refuses a path that
    `Path.is_absolute` gives as absolute. On Windows `/tmp/escaped` and `C:docs` are not absolute.
    The first then fails with another message; the second resolves to `<root>\docs` when the root
    lies on drive C:.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | One lock module for POSIX and Windows | yes | choice by import; `flock` as at the base; `msvcrt.locking` on byte 0; timeout exits 1 | A1, A2 |
| R2 | The create-only write without `O_NOFOLLOW` | yes | base call where the flag exists; identity check; LF text; close before rollback | A3, A5 |
| R3 | Binary descriptors, and no link at a file of the state | yes | `O_BINARY` on each `os.open`; `O_NOFOLLOW`; the identity check; one hard link | A4, A11a |
| R4 | Replace and unlink on Windows | yes | 10 tries; a junction is a link; a rooted config path | A5 |
| R5 | `mine` finds the transcripts of its root, and no other | yes | the naming rule; the cut; letter case; the `cwd` filter; `projects_dir` | A6 |
| R6 | The residuals of TASK 132 | yes | `S_ISDIR` in `entered`; the order test; two docstrings | A7 |
| R7 | Text encoding of the streams and of `git` | yes | `backslashreplace` output; ASCII JSON; UTF-8 input; UTF-8 `git` | A8 |
| R8 | Tests and CI | yes | the stand-in; tests on Windows; the read of the suite; the CI steps | A9, A10 |
| R9 | Staging and records | yes | the four stages; the settings readings; the changelogs; the docs | A11 |

## 3. Requirements

### R1 — one lock module for POSIX and Windows

- **R1.1** A new module `L/locks.py` holds `acquire(fd, path, shared=False)`, `release(fd)` and
  the constant `WINDOWS`. It chooses its lock by import. When `import fcntl` succeeds, it uses
  `fcntl`. Otherwise it imports `msvcrt`. `WINDOWS` is true exactly when `import fcntl` fails.
  When neither imports, `acquire` raises `CliError` with exit 1, and the message names both
  modules.
- **R1.2** No module of `F/` imports `fcntl` or `msvcrt` except `L/locks.py` and the test modules
  of `F/tests/`. `run_feedback.py --help` and each subcommand import on a platform without
  `fcntl`. The comment of `posttooluse_filter.py:120@6e30763` that names `fcntl` among the
  imports of `feedback_lib` names `locks` in its place.
- **R1.3** On POSIX, `acquire` calls `fcntl.flock(fd, fcntl.LOCK_EX)`, or `fcntl.LOCK_SH` when
  `shared` is true. It waits with no time limit, as at the base. `release` makes no call: the close
  of the descriptor releases the lock, as at the base.
- **R1.4** On Windows, `acquire` moves the descriptor to offset 0 and calls
  `msvcrt.locking(fd, msvcrt.LK_LOCK, 1)`. A shared lock is exclusive there: `msvcrt` has no shared
  lock. `release` moves the descriptor to offset 0 and calls `msvcrt.locking(fd,
  msvcrt.LK_UNLCK, 1)`. It ignores an `OSError` of that call, since the close releases the lock.
- **R1.5** `LK_LOCK` tries 10 times, 1 second apart, and then raises `OSError` with errno 36,
  `EDEADLOCK` of the Universal C Runtime. `L/locks.py` holds 36 as a constant. `acquire` then
  raises `CliError` with exit 1 and the error type `LockTimeout` (D3). The message names the lock
  file and says that another `run-feedback` process holds it. An `OSError` with another `errno`
  raises `CliError` with exit 1, the error type `LockError`, and the error's text.

  **Why.** `errno.EDEADLOCK` is 35 on Linux and absent on macOS, where the stand-in of R8.1 runs.
- **R1.6** The six calls of §1 item 3 call `acquire` with the descriptor and the file of the base,
  and call `release` before each close of that descriptor. Each lock file stays as at the base
  (D2). A caller that reads or writes after `acquire` sets its own offset, as at the base.
- **R1.7** A journal append that follows a completed write of the same command is best effort on
  a lock error. Such appends: `file` after the ledger write and the move out of the inbox,
  `claim` after the claim, `release` after the release, `collect` after the inbox write, and
  `mine` after its collects. There a `LockTimeout`, a `LockError` or a `StateRefused` of the
  journal prints
  one warning line to stderr, names the event that was not journaled, and leaves the command's
  exit code as it would be.
- **R1.8** The hooks stay silent: a `CliError` in `posttooluse_filter.py` or
  `session_end_marker.py` ends the hook with exit 0, as every other error there does.

### R2 — the create-only write without `O_NOFOLLOW`

- **R2.1** Where `os` has `O_NOFOLLOW`, `file_record` of `L/ledger_core.py` keeps the flags of
  the base call.
- **R2.2** Elsewhere, the flags are `os.O_WRONLY | os.O_CREAT | os.O_EXCL` with `os.O_BINARY`.
  After the open, these hold, or the write is refused:
  - `os.fstat` of the descriptor gives a regular file with one hard link;
  - `os.lstat` of the record path gives the `(st_dev, st_ino)` of the descriptor;
  - the record path is no link by the rule of TASK 131 R1.3: `stat.S_ISLNK`, or a reparse point
    whose tag is a name surrogate.

  A refusal closes the descriptor and raises `CliError` with exit 4, `FilingConflict` and the
  message `the record path changed during the write: <path>`.
- **R2.3** On the branch of R2.2, a removal of the record path needs the identity of the
  descriptor at the path, by `os.lstat`. Such removals are the refusal of R2.2, the rollback of a
  failed text write, and the rollback after a failed write of the index. An error before the
  identity is known, the open of the record included, removes nothing. Otherwise the path stays,
  and the message says so. On the branch of R2.1 `_rollback` stays as at the base.
- **R2.4** The text layer of the write passes `newline="\n"`. The record has LF line ends on every
  platform. On POSIX the bytes equal those of the base.
- **R2.5** When `os.fdopen` raises, `file_record` closes the descriptor before the rollback, and
  ignores an `OSError` of `EBADF` from that close. When the text layer was made, its own close
  closes the descriptor, as at the base. On the branch of R2.2 it takes
  the identity of the descriptor with `os.fstat` right after `os.open`. **Why.** At the base the
  descriptor leaks when `os.fdopen` raises, and Windows refuses to remove a file that is open,
  so the rollback leaves the record.

### R3 — binary descriptors

- **R3.1** Each `os.open` of `F/` passes `getattr(os, "O_BINARY", 0)`: the lock file of
  `cmd_file`, `_locked` of `L/claims.py`, the collect lock of `L/inbox.py`, the append of
  `L/journal.py` and the write of R2. Each call reads the flag when it runs. CR LF and a byte
  `0x1A` stay as written. On POSIX the flag is 0, and each call equals the base.
- **R3.2** The four opens of the machine state, `_locked` of `L/claims.py`, the append of
  `L/journal.py`, the collect lock of `L/inbox.py` and the filing lock of `cmd_file`, go through
  one function, `open_state` of `L/atomic.py`. It refuses, with exit 4 and the error type
  `StateRefused`, and writes nothing:
  - a directory of the file that is a link or a junction, by the rule of R2.2 on `os.lstat` of the
    file's own directory. A file of the state lies in `.agent/feedback/`, which the config
    resolves, or in one directory under it. The same check runs before each `mkdir` of such a
    directory, on the directory of `consume` before it writes, and in `file` on `inbox/`, `filed/`
    and `dismissed/` before it reads or writes. Before its ledger write, `file` also refuses the
    file that its move writes, `filed/<finding_id>.json` or `dismissed/<finding_id>.json`, when
    `os.lstat` gives it as no regular file. Each failure of the move after the ledger write, a
    `CliError` included, runs the recovery of `_consume_or_explain`. When the write of the recovery
    fails too, the finding stays `new`, and the error names both halves;
  - a link at the file's name. Where `os` has `O_NOFOLLOW`, the open passes it, and an `ELOOP`,
    `EMLINK` or `EFTYPE` of the open is the refusal. Elsewhere `os.lstat` of the name, before the
    open and after it, must give no link by the rule of R2.2, and after it the identity of the
    descriptor;
  - a file that is no regular file: the open passes `O_NONBLOCK`, an `ENXIO` of the open is the
    refusal, and `os.fstat` of the descriptor must give a regular file;
  - a file with a second hard link.

  **Why.** Before the task a link planted at `.agent/feedback/retro_owner` made `claim` write a
  file outside the repository, and `release` truncate it (B1, D9). A link at
  `.agent/feedback/inbox/` made `collect` write a finding outside, and a FIFO made it wait.

### R4 — replace and unlink on Windows

- **R4.1** When `locks.WINDOWS` is true, `write_atomic` of `L/atomic.py` tries `os.replace` up to
  10 times, 0.1 seconds apart, while it raises `PermissionError`. The last error propagates as at
  the base. This is the rule of TASK 128 for `update_state.py`.
- **R4.2** The same 10 tries apply to three unlinks:
  - `os.unlink` in `consume` of `L/inbox.py`: after the 10th `PermissionError` the error
    propagates. A `FileNotFoundError` returns, as at the base;
  - the unlink of the temporary file in `write_atomic`, and `os.unlink` in `_rollback` of
    `L/ledger_core.py`: after the 10th `PermissionError` each ignores the error, as at the base,
    and the exception that started the cleanup propagates.
- **R4.3** `write_atomic` refuses a target that is a link by the rule of R2.2, with the message of
  the base. On POSIX the check equals the base's `stat.S_ISLNK`.
- **R4.4** When `locks.WINDOWS` is false, each call runs once, as at the base. Each function reads
  `locks.WINDOWS` when it runs, so a test sets it.
- **R4.5** `_contained` of `L/config.py` refuses a configured path whose `Path.anchor` is not
  empty, with the message of an absolute path: `must be RELATIVE to the repo root`. On POSIX a
  path has an anchor exactly when it is absolute, so the check equals the base. **Why.** On
  Windows `/tmp/escaped` has the anchor `\` and is not absolute, and `C:docs` has the anchor
  `C:` (§1 item 12). The check tightens the base: on a root of drive C: the base accepted
  `C:docs` as `<root>\docs`.

### R5 — `mine` finds the transcripts of its root, and no other

- **R5.1** `encode_project_dir` of `L/mine.py` replaces each UTF-16 code unit outside
  `[A-Za-z0-9]` with `-`, the rule of Claude Code 2.1.306. A character outside the Basic
  Multilingual Plane gives two `-`.
- **R5.2** When the encoded name is longer than 200 characters, `default_transcript_dirs` matches
  on its first 200 characters. The base rule then applies: a directory named as the prefix, or
  starting with the prefix and `-`.
- **R5.3** `default_transcript_dirs` resolves the root, then calls a new function
  `match_transcript_dirs(root_text, projects)`, which takes the resolved root as text and holds
  the match of R5.1 to R5.3. When `locks.WINDOWS` is true, the match compares both names after
  `str.casefold`: NTFS ignores letter case, and the drive letter of the root may differ in case
  from the one that Claude Code read.
- **R5.4** With the default directories, `mine` reads a session file only when the first line of
  it that carries `cwd` names the root or a path under it. The comparison uses the text of both
  paths after `os.path.normpath` and `os.path.normcase`, and `str.casefold` when `locks.WINDOWS`
  is true; it resolves no link. `mine` skips a file that is no regular file, and a file whose
  saved offset equals its size, before it reads the `cwd`. It opens a session file with
  `O_NONBLOCK` and reads it only when `os.fstat` gives a regular file. A file with no
  such line, or with a `cwd` elsewhere, is not read, and the statistics count it as
  `files_skipped_foreign`. With `--transcripts-dir`, `mine` reads each file, as at the base.
- **R5.5** The `mine` section of `.agent/skills/run-feedback/references/cli_reference.md`, §C of
  `.agent/skills/run-feedback/references/capture_surfaces.md` and the module docstring of
  `L/mine.py` state R5.1 to R5.4. They no longer say that the directory name is decoded.
- **R5.6** `mine()` takes `projects_dir` and passes it to `default_transcript_dirs`. The command
  `mine` passes none, so its default stays `~/.claude/projects`. No test reads the real
  `~/.claude/projects`: each test of R5 passes a temporary `projects_dir`.

### R6 — the residuals of TASK 132

- **R6.1** `entered` of `.agent/tools/slot_links.py` decides by the `os.lstat` of the entry:
  - a failed `os.lstat` is recorded as `UNREADABLE`, as at the base;
  - a link by TASK 131 R1.3 is not entered and not recorded, as at the base;
  - a directory by `stat.S_ISDIR` that is no link is entered, as at the base;
  - any other entry is not entered, and is recorded as `UNREADABLE` with the reason
    `not a directory`. This case is new.
- **R6.2** A test runs `_main` of `rebase_links.py` with a `--from` that the stand-in of TASK 132
  R3.1 makes a device, and the operand `README.md`, which `_refuse_operand` refuses. The run exits
  2 with the reason of TASK 132 R2.4, `--from does not lie inside the working directory`, and not
  with the operand's.
- **R6.3** The module docstring of `rebase_links.py` and the docstring of `_refuse_operand` name a
  path that names a device among the refused operands and options (TASK 132 R2.3, R2.4).

### R7 — text encoding of the streams and of `git`

- **R7.1** `main` of `run_feedback.py` and both hooks reconfigure `sys.stdout` and `sys.stderr`
  with `errors="backslashreplace"`, before any output. A stream that has no `reconfigure`, such
  as the `io.StringIO` of `run_cli` in `F/tests/_fixtures.py`, stays as it is. No message raises
  an encoding error. This is the rule of TASK 127 R2.2.
- **R7.1a** Each JSON output to a stream is ASCII: `json.dumps` with `ensure_ascii=True`. This
  covers `_emit` with `--json`, `triage --json`, `issues --json` and `emit_json_error` of
  `L/envelope.py`. The output then holds `\uXXXX` escapes and parses to the same values on every
  platform. **Why.** `backslashreplace` writes `\xNN` and `\UNNNNNNNN`, which JSON does not
  allow. TASK 131 made the `--json` output of `rebase_links.py` ASCII for the same reason. The JSON
  files that `F/` writes keep `ensure_ascii=False`.
- **R7.2** Both hooks read their payload from `sys.stdin.buffer` and decode it as `utf-8-sig`,
  which drops a leading byte-order mark. A payload that is not UTF-8 is treated as at the base:
  `{}` in `session_end_marker.py`, exit 0 in `posttooluse_filter.py`.
- **R7.3** `_read_maybe_stdin` reads `-` from `sys.stdin.buffer` and decodes it as `utf-8-sig`.
  It reads a file given with `@`, the form of `--body-file <path>`, as `utf-8-sig` too, so a body
  keeps the same text by either route. Bytes that are not UTF-8 raise `CliError` with exit 2, as at
  the base for a file.
- **R7.4** The `git` call of `L/config.py` passes `encoding="utf-8"` and
  `errors="surrogateescape"` in place of `text=True`. On POSIX a path that is not UTF-8 then
  round-trips through `Path`; Git for Windows prints UTF-8.

### R8 — tests and CI

- **R8.1** A new test module `F/tests/test_windows_branch.py` runs the Windows branches on POSIX.
  At run time it writes, in a temporary directory, a `sitecustomize.py` that blocks `import fcntl`,
  provides a `msvcrt` stand-in, and removes `os.O_NOFOLLOW`. The stand-in implements `locking`
  with `fcntl.lockf` on the same byte, and logs each call with its offset and its time. It starts
  `run_feedback.py` or a hook with that directory on `PYTHONPATH`. No such file is committed. This
  is the method of TASK 127 R7.2. The module skips these tests where `fcntl` does not import.
  Each new test of `F/tests/` is a method of a `unittest.TestCase`, and each skip there is
  `unittest.skipIf` or `unittest.skipUnless`. **Why.** The `unittest` rules of R9.1 load
  `F/tests/` and run no mark of pytest.
- **R8.2** A stand-in value of `os.O_BINARY` is an unused bit. A spy on `os.open` records the flags
  and strips that bit before the real call (TASK 131 R6.3).
- **R8.3** Tests that run on Windows only, in `F/tests/test_windows_branch.py`:
  - TC-WN1: a target of `write_atomic` held open by `open()` in a thread that closes it after 0.3
    seconds;
  - TC-WN2: a junction at the target of `write_atomic`, made with `_winapi.CreateJunction`;
  - TC-WN3: the bytes of a journal entry and of a filed record hold no CR;
  - TC-WN4: the real `msvcrt` lock: a second process meets the held lock and exits 1 with
    `LockTimeout` after the 10 tries;
  - TC-WN5: `default_transcript_dirs` of a root with a lower-case drive letter.
- **R8.4** Each test of §5 names its module. Each new test names one mutation of the code that
  turns it red, and the audit records the run of each mutation (TASK 132 R3.4).
- **R8.5** The run reads each test module of `F/tests/` for assumptions that do not hold on
  Windows. Such an assumption is a separator, a line end, a locale encoding, a link, `st_mode`
  bits, the removal of an open file or a shell script. The audit records, per module, each
  assumption found and its skip or fix. A test that needs POSIX skips on Windows with a reason
  that names the need.
- **R8.5a** The read of R8.5, made during planning, gives these edits of `F/tests/`:
  - skips: `test_iteration3.py` of a file's permission bits, on Windows; `test_ledger_core.py` and
    `test_ledger_hardening.py` of the `O_EXCL|O_NOFOLLOW` refusal, where `os` has no
    `O_NOFOLLOW` (§9, TC-RF10);
  - a path compared with `/` becomes a `Path` or an `os.path.join` in `test_backlog_append.py`,
    `test_dry_run.py`, `test_iteration3.py`, `test_work_item_cli.py` and `test_wi_tail.py`;
  - the `StringIOish` stand-in of stdin in `test_wi_tail.py` gains a `buffer` (R7.2);
  - each test that creates a symbolic link skips where the process cannot create one. The probe
    has the form of `_can_symlink` of `.agent/tools/test_slot_links.py`, copied into each module
    that creates a link, behind `unittest.skipUnless`; the module imports nothing of
    `.agent/tools/`.

  The modules not named here need no edit.
- **R8.6** The job `tooling-tests` of `.github/workflows/framework-gates.yml` gains a step named
  `Run the run-feedback tests`, which runs
  `python -m pytest -p no:cacheprovider .agent/skills/run-feedback/scripts/tests -q`.
- **R8.7** Both Windows jobs gain the same step, after `Run the archive-chain tests`. TC-C9 of
  TASK 131 R7.3 keeps its order of the two existing steps. `F/tests/test_e2e.sh` stays out
  of CI.
- **R8.7a** The tests of the workflow file and of the documents of R9.7, TC-CI1 and TC-CI2, stand
  in `tests/test_session_state_contract.py`, beside TC-C9. **Why.** A copy install of the skill
  holds no `.github/` and no `System/Docs/`, and `tests/` runs in the tooling step and in both
  Windows steps.
- **R8.8** The first Windows run follows the push. A failure there is read by the next task with
  `gh run list` and `gh run view`, filed as a defect, and named to the operator, as TASK 132 R4.2
  states.

### R9 — staging and records

- **R9.1** The change runs the four stages of `framework-upgrade` §3 step 4. These rules reach the
  changed code, each from the directory named:
  - the committed `python3 .agent/tools/rebase_links.py *`, from the root, runs `slot_links.py`
    and `rebase_links.py`;
  - the committed `python3 tests/run_tests.py`, from the root, runs `tests/test_script_guards.py`,
    which loads both scripts by path;
  - the committed `python3 -m pytest` and `python -m pytest`:
    - from the root, they collect `tests/test_script_guards.py` and
      `tests/test_session_state_contract.py`;
    - from `.agent/tools/`, they collect `test_slot_links.py`, `test_rebase_links.py` and
      `test_archive_protocol.py`, which import both scripts;
    - from `.agent/`, they collect `F/tests/` and the tests of `.agent/tools/`;
    - from `.agent/skills/`, `.agent/skills/run-feedback/`, `F/` or `F/tests/`, they collect
      `F/tests/`;
    - from `.claude/`, and from each directory above through a link, they collect the same.
      The links are `.claude/skills`, which points at `.agent/skills`, and the per-skill link
      `.agent/skills/run-feedback` of the sibling checkout `Universal-skills`;
  - the local `python3 -m unittest discover -s tests -v`, from the root, loads
    `tests/test_script_guards.py` and `tests/test_session_state_contract.py`, and from `F/` it
    loads `F/tests/`;
  - the user's `python3 -m unittest discover -s scripts/tests`, from `.agent/skills/run-feedback/`,
    loads `F/tests/`;
  - both `unittest` rules do the same from a directory reached through one of the links above.
- **R9.2** Stage 1 writes each edited code file, each new module and each edited test module that
  a rule above runs, under a new name. The PLAN names each copy. No rule runs a copy, and no test
  runner collects one. A test module that no rule names by path, such as a new module under
  `F/tests/`, is not exempt here: the rules of R9.1 collect `F/tests/`.
- **R9.3** The behaviour check runs in a throwaway worktree outside the repository, which holds
  the live tree and the stage-3 patch. There the gates of the workflow file, the suite of `F/tests/`
  and the tests of the archive chain pass (TASK 127 R8.5).
- **R9.4** The run reads `.claude/settings.local.json` and the user's `~/.claude/settings.json` at
  §2.2, at §4.5 and after the gates of stage 3. The audit names each file of the change that a rule
  of either file runs, and quotes no rule.
- **R9.5** The change edits no permission rule, no hook and no settings key, so stage 3 adds no
  settings test.
- **R9.6** `CHANGELOG.md` and `CHANGELOG.ru.md` hold v3.51.0. Its notes state the migration of
  R5: a root that matched no directory before reads its whole transcript history at its first
  `mine`, and `--since` bounds it.
- **R9.7** `.agent/skills/run-feedback/references/cli_reference.md:89@6e30763` and
  `System/Docs/QUALITY_FEEDBACK_LOOP.md:69@6e30763` name the lock of the journal as `fcntl.flock`
  on POSIX and `msvcrt.locking` on Windows, in place of `flock`.
- **R9.8** `docs/ARCHITECTURE.md` states no lock of `run-feedback` and stays unedited. The
  SKILL.md of `run-feedback` names no lock and no platform, and its exit codes keep their meaning
  (D3), so it stays unedited.

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — A workflow on Windows claims its retro

- **Actors.** An agent in Claude Code on Windows 10; Python 3.13; Git Bash; the ANSI code page
  cp1251.
- **Preconditions.** TASK 133 has landed. No other process holds the claim file.
- **Main scenario.**
  1. The agent runs `run_feedback.py claim --run-id "framework-upgrade-x"`.
  2. The script takes the lock of `retro_owner_path` with `msvcrt.locking`, writes the claim,
     releases the lock, and journals `retro_claimed`.
  3. It exits 0.
- **Alternative.** Another process holds the lock for more than about 10 seconds. The script
  exits 1 with `LockTimeout`, and the message names the lock file. The workflow continues: the
  retro claim is non-blocking.
- **Postconditions.** The claim file holds the run's claim, with no CR.

### UC-2 — A session on Windows ends, and its failures are mined

- **Actors.** Claude Code on Windows; the SessionEnd hook of `run-feedback`.
- **Preconditions.** `RUN_FEEDBACK_HOOKS=1` and `RUN_FEEDBACK_MINE_ON_END=1`. The session ran a
  Bash call that failed. The root's path holds a Cyrillic letter.
- **Main scenario.**
  1. The session ends. Claude Code runs `session_end.sh` with a JSON payload on stdin.
  2. The hook decodes the payload as UTF-8, journals `session_end` with the session id, and mines
     the session's transcript.
  3. `mine` reads the directory of `transcript_path` from the payload, for that session id only.
     The rule of R5.1 serves the hook only when the payload carries no `transcript_path`.
  4. The failure becomes a finding in `.agent/feedback/inbox/`. The hook exits 0.
- **Alternative.** The journal lock times out. The hook exits 0 and writes no finding.
- **Postconditions.** The journal holds `session_end` and `mine_run`, and the inbox one finding.

### UC-3 — The operator files a defect on Windows

- **Actors.** An agent on Windows; the operator.
- **Preconditions.** A finding stands in the inbox.
- **Main scenario.**
  1. The agent runs `run_feedback.py file --finding <id> --as defect ...`.
  2. The record is created with `O_EXCL` and `O_BINARY`, and has LF line ends. The index line is
     inserted, and the finding moves to `filed/`.
  3. It exits 0.
- **Alternatives.**
  - The record path is swapped for a link after the open. The run exits 4 with
    `FilingConflict`, and the file at the path stays.
  - The journal lock times out after the filing. The run prints a warning that names
    `finding_filed`, and exits 0.
- **Postconditions.** The record and its index line exist; the inbox no longer holds the finding.

### UC-4 — `mine` runs in a root whose path holds a space

- **Actors.** An agent on Linux.
- **Preconditions.** The root is `/home/u/My Project_1`. A sibling `/home/u/My Project_1-old`
  has transcripts too.
- **Main scenario.**
  1. The agent runs `run_feedback.py mine --dry-run`.
  2. `mine` reads `~/.claude/projects/-home-u-My-Project-1/`. It skips each session file of
     `-home-u-My-Project-1-old/`, whose first `cwd` is the sibling.
- **Alternative.** A session file of the root's directory holds no line with `cwd`. `mine` skips
  it and counts it, and the operator passes `--transcripts-dir` to read it.
- **Postconditions.** The candidates come from the root's sessions only; the statistics count the
  skipped files.

<!-- contract:acceptance -->

## 5. Acceptance criteria

The module of each test: `W` is `F/tests/test_windows_branch.py`, `M` is `F/tests/test_mine.py`,
`S` is `.agent/tools/test_slot_links.py`, `G` is `tests/test_script_guards.py`, `C` is
`tests/test_session_state_contract.py` (R8.7a).

- **A1** (R1.1, R1.2) With `fcntl` blocked and the stand-in present, each subcommand of
  `run_feedback.py` and both hooks exit as with `fcntl`. Each lock call in the stand-in's log is
  `LK_LOCK` or `LK_UNLCK` at offset 0 (TC-RF1, TC-RF2, W). With neither module, a command that
  takes a lock exits 1 and names both (TC-RF3, W).
- **A2** (R1.4 to R1.8) The stand-in's `locking` raises `OSError` with errno 36 from its N-th
  `LK_LOCK` call on, N set by the test:
  - with N = 1, `claim` exits 1 with `LockTimeout` (TC-RF4, W);
  - with N = 1, the PostToolUse hook exits 0 and writes no finding and no journal entry (TC-RF5,
    W);
  - with N past the locks of the filing, `file` files the record, prints a warning that names
    `finding_filed`, and exits 0 (TC-RF6, W).

  With N = 1, `RUN_FEEDBACK_MINE_ON_END=1` and a transcript that holds a failed call,
  `session_end_marker.py` exits 0 and writes no finding, and the stand-in's log holds the
  journal's `LK_LOCK` (TC-RF20, W). With another
  `errno`, `claim` exits 1 with `LockError` (TC-RF7, W). Two processes that append to
  the journal at once leave lock intervals in the stand-in's log that never overlap (TC-RF8, W).
- **A3** (R2) With `os.O_NOFOLLOW` removed:
  - `file` creates the record with LF line ends and exits 0 (TC-RF9, W);
  - a record path swapped for a symbolic link between the open and the check exits 4 and leaves
    the link (TC-RF10, W).

  On POSIX with the flag, the record's bytes equal `record_text.encode("utf-8")` with LF line ends
  (TC-RF11, W).
- **A4** (R3) The spy of R8.2 records `O_BINARY` in the flags of each of the five calls (TC-RF12,
  W).
- **A5** (R4) With `locks.WINDOWS` set:
  - `os.replace` that raises `PermissionError` twice and then succeeds: `write_atomic` writes the
    file (TC-RF13, W);
  - raising 10 times: the error propagates and no temporary file stays (TC-RF14, W);
  - `consume`: it succeeds after two failures, and after ten the error propagates (TC-RF15, W);
  - the temporary file's unlink and `_rollback`: each succeeds after two failures. After ten, the
    cleanup error is ignored, the exception that started the cleanup propagates, and the path
    stays (TC-RF17, W);
  - a stand-in of a junction at the target is refused (TC-RF16, W);
  - an `os.fdopen` that raises closes the descriptor before the rollback, and the record is
    removed (TC-RF18, W);
  - `_contained` with `Path` bound to `PureWindowsPath` for its own call only, given
    `/tmp/escaped` and `C:docs`, raises `CliError` with code 3 and `RELATIVE` (TC-RF19, W).
- **A6** (R5) `encode_project_dir` gives these literal names (TC-MN1, M):
  - `C:\Users\dev\loyalty-api-java` → `C--Users-dev-loyalty-api-java`;
  - `/home/u/My Project_1` → `-home-u-My-Project-1`;
  - a path with a Cyrillic word of 12 letters → 12 `-` in its place, as
    `-Users-sergey-Documents-Work-data-------------` shows;
  - a path with one emoji → two `-`;
  - `/home/u/app` → `-home-u-app`, as at the base.

  A root of 210 characters matches a directory named as Claude Code names it (TC-MN2, M). With
  `locks.WINDOWS` set, `match_transcript_dirs` with the root text `c:\Users\dev\app` matches a
  projects directory that holds `C--Users-dev-app` (TC-MN3, M). For the root `<r>`, a session
  file whose first `cwd` is `<r>-old` is skipped and counted, and one whose first `cwd` is
  `<r>/sub` is read (TC-MN4, M). A session file of the root's directory with no line that carries
  `cwd` is skipped and counted (TC-MN5, M).
- **A7** (R6) With an `os.lstat` stand-in that gives a character device for a directory entry,
  `entered` records `UNREADABLE` `not a directory` and does not enter it (TC-AR1, S). The tests of
  a directory link at the base, `test_slot_links.py` TC-19 and TC-W20, still pass. The test of
  R6.2 passes, and fails when the check of TASK 132 R2.4 moves after `_refuse_operand` (TC-AR2,
  G). Both docstrings name a device (TC-AR3, G).
- **A8** (R7) Each output below parses with `json.loads` to the values written:
  - under `PYTHONIOENCODING=cp1251`, `issues --json` with a record whose category holds `é`
    (TC-EN4, W);
  - under `PYTHONIOENCODING=cp1252`, `triage --json` with a finding that holds one emoji, and the
    `--json-errors` envelope of a failed command whose path holds `é`; the bytes of both outputs
    are ASCII (TC-EN5, W).

  Under `PYTHONIOENCODING=cp1252`:
  - `init` exits 0 in a new root, and its human output holds `prefix\u2192category`, the escape of
    `→` (TC-EN1, W);
  - `session_end_marker.py` with a payload that holds a Cyrillic session id and a leading
    byte-order mark journals that id (TC-EN2, W);
  - `collect --error-envelope -` with a Cyrillic `error` keeps the text (TC-EN3, W).
- **A9** (R8.6, R8.7) The workflow file holds the step `Run the run-feedback tests` with the
  command of R8.6 in `tooling-tests` and in both Windows jobs, after `Run the archive-chain tests`
  there (TC-CI1, C).
- **A10** (R8) The suite of `F/tests/` passes on macOS with Python 3.14. Each new or edited Python
  file parses with `ast.parse(..., feature_version=(3, 11))`. The run reads each call that the
  change adds against the documentation of Python 3.11. No f-string of a new or edited file holds,
  inside a replacement field, a quote of its own kind, a backslash or a `#`. PEP 701 allows these
  from Python 3.12, and `feature_version` does not refuse them. This machine has no Python 3.11;
  the floor job of CI runs it after the push. The audit holds the read of R8.5 and the mutation runs
  of R8.4. `tests/run_tests.py` and the gates of the
  workflow pass.
- **A11** (R5.5, R9) The four stages run, and the audit record holds their checks and the settings
  readings. The changelogs hold v3.51.0 with the migration note. Both documents of R9.7 name both
  locks, and the reference states R5 (TC-CI2, C).

- **A11a** (R2.3, R3.2, R5.4, R7, round 1 of stage 2) The tests that round 1 of stage 2 added:
  - a failed write of the index, on the branch of R2.2, leaves a foreign file at the record path
    (TC-RF21, W);
  - a symbolic link at `retro_owner` and at the journal file: `claim` and `journal` exit 4 and the
    link's target keeps its bytes, with `O_NOFOLLOW` and without it (TC-RF22, W);
  - a second hard link made right after the open of a record, without `O_NOFOLLOW`: exit 4, and
    the other link keeps the file (TC-RF23, W);
  - a hard link at `retro_owner`: `claim` exits 4 (TC-RF24, W);
  - under `PYTHONIOENCODING=cp1252`, `collect --json` with an emoji in the message and a
    byte-order mark on stdin prints ASCII that parses (TC-EN3);
  - a `--body-file` that starts with a byte-order mark files a body without it (TC-EN6, W);
  - the PostToolUse hook with a byte-order mark on stdin collects its finding (TC-EN7, W);
  - TC-RF6 also with errno 13, a `LockError`;
  - a FIFO and a directory named `*.jsonl` among the session files: `mine` returns within 10
    seconds and counts neither (TC-MN6, M);
  - with `locks.WINDOWS` set, a session whose first `cwd` differs from the root in letter case is
    read (TC-MN7, M);
  - an error of the open of a record, or of its `os.fstat`, without `O_NOFOLLOW`, leaves a file
    that took the record path (TC-RF25, W);
  - a link at `journal/`, at `inbox/` and at `dismissed/` of `.agent/feedback/`: `claim` warns,
    `collect` and `file --as noise` exit 4, and the link's target stays empty, with `O_NOFOLLOW`
    and without it (TC-RF26, W). TC-RF22 also covers both lock files, a dangling link that creates
    no target without `O_NOFOLLOW`, and a swap right after the open, which the identity check sees;
  - a FIFO at `retro_owner`, at the journal file and at `.collect.lock`: each command exits 4
    within 10 seconds (TC-RF27, W);
  - a session file of another root whose saved offset equals its size is not counted
    (TC-MN8, M);
  - a link at `filed/`: `file --as defect` exits 4, files no record and leaves the finding `new`;
    a link at `inbox/`: `file --as noise` exits 4 and the finding outside stays. A direct
    `consume` with a dangling link at `dismissed/` raises a `CliError` and makes no target
    (TC-RF28, W);
  - a dangling link at `journal/`: `claim` warns and exits 0; at `inbox/`: `collect` exits 4; no
    traceback, and no target is made (TC-RF29, W);
  - a `StateRefused` of the move after the ledger write: exit 4, both halves named, and the
    finding marked `filed` in place (TC-RF30, W);
  - a link at `filed/<finding_id>.json`: `file --as defect` exits 4, files no record and leaves
    the finding `new`; a link at `dismissed/<finding_id>.json`: `file --as noise` exits 4; no
    target is made (TC-RF31, W);
  - a `FilingConflict` of the move after the ledger write: the finding is marked `filed` in place.
    When the write of that mark raises a `CliError` too, the error names both halves, and the
    finding stays `new` (TC-RF32, W).

<!-- contract:open-questions -->

## 6. Open questions

None. D2 to D8 are the analyst's choices, open to the operator's change.

## 7. Decisions

- **D1**, 2026-10-28, operator: two tasks. TASK 133 holds `run-feedback` on Windows and the
  residuals of TASK 132. TASK 134 holds WI-39 for the 13 scripts that committed allow rules run and
  `run_audit.py` of the local rules.
- **D2**, analyst: the Windows lock covers byte 0 of the file that the POSIX lock covers. No
  sidecar file is added. A lock of `msvcrt` is mandatory: while it is held, a read of byte 0 by
  another process fails. The readers of `run-feedback` take the lock first; a `grep` of the
  journal, as `heal-issues` runs it, may fail during an append. **Why.** TASK 127 locks byte 0 and
  passed the Windows jobs. **Rejected:** a lock past the end of the file, such as at 2^30, which
  no read reaches. No Windows run of this framework has measured `msvcrt.locking` at such an
  offset, and the readers of `run-feedback` take the lock anyway. The task keeps the one form that
  CI measured. **Rejected:** a sidecar lock file per locked file, which adds files to
  `.agent/feedback/` for one platform.
- **D3**, analyst: a lock timeout exits 1. **Why.** TASK 127 R1.5 exits 1 on a lock timeout, and
  exit 1 of `L/envelope.py` is an unexpected failure. **Rejected:** exit 4. The SKILL.md of
  `run-feedback` defines exit 4 as a filing conflict: a slug that exists, a vocabulary violation or
  a missing backlog anchor.
- **D4**, analyst: R5 joins the scope with the `cwd` filter of R5.4. **Why.** The analysis of §1
  found the naming defect. On Windows `mine` matches no root, so the Windows area is not complete
  without it. R5.1 widens the over-match of §1 item 9, so R5.4 bounds it. **Rejected:** stating the
  over-match in §9 only, since `mine` would then read more foreign transcripts than at the base.
- **D5**, analyst: the run-feedback tests run on Linux and on both Windows jobs. **Why.** No CI
  step ran them before (§1 item 10). **Rejected:** Linux only, which leaves the Windows branches
  untested on Windows.
- **D6**, analyst: R7 joins the scope. **Why.** TASK 127 R2.2 and TASK 131 R6.7 cover the same
  class for the other two areas, and without R7 the tests of `init` and the hooks fail on Windows.
  **Rejected:** a later task for the encoding, which would leave the Windows step of R8.7 red.
- **D7**, analyst: the read of R8.5 precedes the push. **Why.** TASK 131 met ARC-14 in its first
  Windows run; a read of the suite lowers the number of such failures. **Rejected:** a push with no
  read, which leaves each failure to a follow-up task.
- **D12**, 2026-10-28, operator: the code review of stage 4 approved the code and rejected one
  sentence of `cli_reference.md`, a document outside the diff of stage 3. The operator chose a
  correction of the documents in place over the restore of stage 3. The code reviewer reads the
  corrected sentences.
- **D11**, 2026-10-28, operator: the narrow round 4 of stage 2 passed, with R4-1 of the security
  audit open: a link at the file `filed/<finding_id>.json` left the half-state of R3-1. The
  operator chose its fix and a narrow round 5, which checks the fix and the lines it touches. The
  fix also takes R4-2, R4-3 and the NITs of round 4.
- **D10**, 2026-10-28, operator: round 3 of stage 2, the last that the bound allows, ended with
  MAJOR-1 of the code review open. The operator chose a narrow round 4: the fix of MAJOR-1,
  MINOR-1 and MINOR-2, and a review of the fix and of the lines it touches.
- **D9**, 2026-10-28, operator: the fix of M1 of stage 2 covers B1, a HIGH finding before the
  task, on POSIX too (R3.2). L4, the empty file that `CREATE_NEW` may leave at the target of a link
  planted after the check of `lexists`, stays in §9. **Why.** One function closes both platforms.
  The fix of L4 needs `_winapi.CreateFile`, a private API that only the Windows jobs can test.
- **D8**, analyst: the JSON output of R7.1a is ASCII on every platform. On POSIX a non-ASCII
  character of `--json` output then prints as `\uXXXX`. **Why.** One form on every platform lets a
  test on POSIX check the bytes that Windows prints. **Rejected:** ASCII only when the stream's
  encoding is not UTF-8, which makes the output depend on the environment of the caller.

<!-- contract:measurements -->

## 8. Measurements of this run

Each run is on macOS, Python 3.14.8, at the base, in a temporary root under the session's
scratchpad with its own `.git`. A `sitecustomize.py` on `PYTHONPATH` blocks `import fcntl`.

1. `run_feedback.py claim --run-id m133` with `fcntl` blocked: exit 1,
   `ModuleNotFoundError: No module named 'fcntl'`.
2. `posttooluse_filter.py` with a failure event on stdin and `fcntl` blocked: exit 0, and no
   `.agent/feedback/` directory is created.
3. The same event with `fcntl` present: exit 0, and the inbox holds one finding, the journal one
   entry.
4. `run_feedback.py file --finding <id> --as defect` with `os.O_NOFOLLOW` deleted: exit 1, a
   traceback that ends `AttributeError: module 'os' has no attribute 'O_NOFOLLOW'`, at
   `ledger_core.py` line 209.
5. `encode_project_dir(r"C:\Users\dev\loyalty-api-java")` returns the path unchanged; the rule of
   Claude Code gives `C--Users-dev-loyalty-api-java`.
6. A root `.../m133/My Project_1` and a projects directory that holds the name Claude Code gives
   it: `default_transcript_dirs` returns `[]`.
7. `python3 -m pytest -q -p no:cacheprovider tests` from `F/`: 333 passed.
8. CI run 40663257271 at `155441a`, the last pushed commit: all jobs passed, both Windows jobs
   among them. The commit of v3.50.2, `6e30763`, is not pushed, so it has no run.

The rule of Claude Code 2.1.306 comes from its binary,
`~/.local/share/claude/versions/2.1.306`: `function k(e){return
e.replace(/[^a-zA-Z0-9]/g,"-")}` and a cut at 200 characters with `-` and a base-36 hash. The
directory `~/.claude/projects/-Users-sergey-Documents-Work-data-------------` shows the rule on
a path with Cyrillic letters. A transcript line carries `cwd`, and the value changes when the
session changes its directory; the first such line names the directory of the start.

## 9. Out of scope

- WI-39 for every allow-listed script (TASK 134, D1).
- `python3` in `F/hooks/posttooluse.sh` and `F/hooks/session_end.sh`: on Windows the command may
  name the Microsoft Store stub. Every command of the framework uses `python3`.
- The debug dump of `posttooluse_filter.py`, which writes with `Path.write_text` and no `newline`.
- Two unlinks that ignore their failure at the base: `release` of `L/claims.py` and the probe of
  `doctor` in `F/run_feedback.py`.
- On the branch of R2.2, an `O_EXCL` open that met a link planted after the check of `lexists` may
  create an empty file at the link's target. A window remains between the `lstat` and the removal
  of a refusal.
- `mine` saves its new offsets before the caller collects the candidates. On Windows a collect
  that times out after 10 seconds ends the loop, and the candidates not yet collected are not read
  again. On POSIX `flock` waits with no limit, so the loss needs Windows and a held lock.
- `Path.resolve()` on Windows resolves a `subst` drive, a mapped drive and a junction, and the
  directory that Claude Code read may not. A path in NFD and one in NFC give different names. R5.4
  reads the `cwd` that Claude Code wrote, so a session found keeps its root.
- `mine` reads `~/.claude/projects/` and ignores `CLAUDE_CONFIG_DIR`, as at the base.
- R3.2 checks a name or a directory and then opens it. A process that races in between can swap in
  a link: a write may then leave the directory, and on Windows an open may make an empty target.
  POSIX could open the directory with `O_DIRECTORY | O_NOFOLLOW` and the file through `dir_fd`;
  the task keeps the check of a planted entry, as the record write of R2.2 does.
- A FIFO named after a finding, or at `mine_state.json`, blocks `collect`, `triage` and `mine`, as
  at the base (round 3 of stage 2, R3-5).
- TC-RF31 plants links only. No test pins the refusal of a directory or a FIFO at the file that the
  move writes (round 5 of stage 2, NIT-1). Without that refusal, a directory there makes the move
  fail after the ledger write, and the recovery of V17 marks the finding in place; the move
  replaces a FIFO.
- When the move and the write of the recovery both fail, as with `filed/` and `inbox/` read-only,
  the finding stays `new`, and a retry files another record. The error names the record and warns
  against a re-run with the same `--slug` (round 5 of stage 2, R5-1).
- For `--as noise`, the message of the recovery names a ledger write, which noise does not make, as
  at the base.
- `.agent/workflows/heal-issues.md` probes its lock with `import fcntl`. On Windows the import
  fails, and the workflow reads the failure as a lock that another run holds, so it stops on each
  run. It is a workflow of its own.
- A run of Windows on this machine: the Windows jobs of CI measure it after the push.
- The other findings of TASK 132 §9.
