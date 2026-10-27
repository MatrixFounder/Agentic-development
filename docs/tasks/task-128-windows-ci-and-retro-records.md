# TASK 128 — A CI job runs the session state on Windows, and the six records of the TASK 127 retro close

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 128 |
| Slug | windows-ci-and-retro-records |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | the retro of TASK 127 and the operator's answers of 2026-10-26 (D1, D2) |
| Base revision | `931d5b1c2ceaf8b33e8dca0e64aacdf7c1aaac1b` |
| Closes | ARC-13, SS-3, SS-4, SS-5, SS-6, TS-1 |
| Archive name | `task-128-windows-ci-and-retro-records.md` |
| Revision | 7 |

**Revision 7** records the close of stage 2 (D16). **Revision 6** applies fix round 2 of
stage 2 (D15). **Revision 5** applies fix round 1 of
stage 2 (D14). **Revision 4** extends TC-25 to a failed
removal (Mode B N11). **Revision 3** applies m1 to m4
and N1 to N7 of Mode A round 2, which passed, with no further round. **Revision 2** applied M1, m1 to m11 and N1 to N9 of round 1. It also took two findings
before the task into the task: an entry of another kind at the state (D13), and the race of the
scratch root (R6.4).

**Request.** At the retro of TASK 127 the operator filed six defects and chose to close them in
the next task. Asked for the order of the Windows series, they chose a CI job on Windows first,
with these records. The Windows port of the archive chain follows as TASK 129 (D1).

In this document `S/` stands for `.agent/skills/skill-session-state/`. A coordinate into a file
that this task edits carries the pin `@931d5b1`, the base revision.

<!-- contract:problem -->

## 1. Problem

1. **No run on Windows.** TASK 127 made `S/scripts/update_state.py` run on Windows, and no run on
   Windows has checked it. Every CI job of `.github/workflows/framework-gates.yml` runs on Ubuntu.
   TASK 127 §9 gave the CI job, and a run of its UC-1 on Windows, to this series.
2. **The tests assume POSIX in places.**
   - `.agent/skills/skill-session-state/scripts/update_state.py:63@931d5b1` `SESSION_DIR =
     ".agent/sessions"`. On Windows the script names `…\root\.agent/sessions\latest.yaml`.
   - TC-11 at `.agent/skills/skill-session-state/scripts/tests/test_update_state.py:479@931d5b1`
     expects backslashes only, so it fails on Windows.
   - `LockTestCase` skips TC-01 where `fcntl` is missing, though TC-01 holds no POSIX lock.
3. **ARC-13.** `.agent/tools/archive_move.py:36@931d5b1` and `.agent/tools/rebase_links.py:80@931d5b1`
   compare real paths as strings. A call through a path in other letter case, on a
   case-insensitive volume, keeps the script's directory on `sys.path`. A module planted beside
   the script then runs under the allow rule.
4. **SS-3.** `update_state.py` reads and writes `latest.yaml` by its path. A link planted at
   `latest.yaml`, at its lock file or at `.agent/sessions` sends the read or the write to the
   link's target.
5. **SS-4.** `tests/test_concurrent_state.py` deletes the live `latest.yaml` when run by hand.
6. **SS-5.** Two SS-1 tests write the state of an outer repository when `TMPDIR` lies inside a git
   work tree.
7. **SS-6.** The list-item pattern of the reader, `^\s+-\s+(.*?)\s*$`, backtracks over a run of
   spaces: 20,000 spaces cost about one second at each run.
8. **TS-1.** `python3 -m unittest discover -s tests` leaves `tests/.scratch/` and a session
   directory behind: only the pytest hook of `tests/conftest.py` removes them.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | The filter of the archive scripts (ARC-13) | yes | the rule of TASK 127 R6.1; both scripts; a run in other letter case; no shared module | A1 |
| R2 | No read or write through a link (SS-3) | yes | a link refused; `O_NOFOLLOW` on POSIX; an exclusive temporary file; the move tried again; the mode kept | A2 |
| R3 | A linear item pattern (SS-6) | yes | `(.*)$` and `rstrip`; the session id too; a time bound | A3 |
| R4 | The SS-1 tests stay in their root (SS-5) | yes | a skip inside a git work tree; the walk-up unchanged; a test of the skip | A4 |
| R5 | No script that deletes the live state (SS-4) | yes | the module removed; no reference left; TC-01 and TC-02 cover it | A5 |
| R6 | Scratch removed at the end of a unittest run (TS-1) | yes | `atexit` bound to its directory; the runner keeps no hook; a child process; the root made again | A6 |
| R7 | CI jobs on Windows | yes | 3.11 and 3.14; bash; paths of the platform; TC-01 and TC-24 on Windows; each test read; the first run read | A7, A12, A13 |
| R8 | Records, documents, staging and checks | yes | the six records closed; WI-39; the documents; the changelogs; the four stages; the checks | A8, A9, A10, A11 |

## 3. Requirements

### R1 — the filter of the archive scripts (ARC-13)

- **R1.1** `.agent/tools/archive_move.py` and `.agent/tools/rebase_links.py`, run as `__main__`,
  remove from `sys.path` each entry that is their own directory, by the rule of TASK 127 R6.1:
  - their own directory is the directory of `__file__` as called and of its real path;
  - an entry matches by `os.path.normcase(os.path.realpath(...))` or by `(st_dev, st_ino)`.
- **R1.2** The code of the filter lives in each script; no module is shared (TASK 127 D3).
  `rebase_links.py` keeps its bytecode settings.
- **R1.3** TC-A20 of `tests/test_archive_move.py` and TC-G11 of `tests/test_script_guards.py` each
  add a run through a path in other letter case. The run is skipped where the volume tells letter
  case apart.

### R2 — no read or write through a link (SS-3)

- **R2.1** The script finds the session directory once, and checks three entries with
  `os.lstat`. It refuses each that is a link, or that is of another kind than expected:
  - `.agent/sessions`, before it creates or opens anything: a directory;
  - `latest.yaml.lock`, before it opens it: a regular file;
  - `latest.yaml`, after it takes the lock and before it reads: a regular file.

  An entry that does not exist passes. A refusal prints a message that names the path and says
  `is a link`, or names the kind it expected, and exits 1. For a link the message also says to
  remove it, or to replace it with a directory or a regular file of one's own. No state is
  written, and nothing is written through a link.
- **R2.2** A link is an entry for which `os.lstat` gives `stat.S_ISLNK`. It is also a reparse
  point whose tag is a name surrogate: `st_file_attributes` holds
  `stat.FILE_ATTRIBUTE_REPARSE_POINT`, and `st_reparse_tag & 0x20000000` is not 0. The check reads
  both attributes with `getattr` on every platform; only Windows sets them. A symbolic link and a
  junction are links; a cloud or deduplication placeholder is not (D11).
- **R2.3** On POSIX, the lock file opens with `os.O_NOFOLLOW`. The read and the write pass `open`
  one `opener`. It adds `os.O_NOFOLLOW` on POSIX to the flags that it receives, and creates a file
  with the bits `0o600`. The flags of `open` stay, `O_BINARY` on Windows among them.
- **R2.4** The script writes the new state to a temporary file named
  `latest.yaml.<32 hex digits>.tmp` in `.agent/sessions`:
  1. `open` with mode `"x"`, `encoding="utf-8"`, `newline="\n"` and the opener of R2.3 creates
     it exclusively, with the bits `0o600`, so no other user can open it before step 2;
  2. on POSIX, `os.fchmod` gives the file the permission bits of `latest.yaml` when that is a
     regular file, and else the bits `0o644` under the umask;
  3. the script writes the file, flushes it, syncs it with `os.fsync`, and closes it;
  4. `os.replace` moves it onto `latest.yaml`.
- **R2.5** A move or a removal that fails with `PermissionError` is tried again: at most 10 tries,
  0.1 seconds apart (D9).
- **R2.6** A failure of the write or of the move closes the temporary file and removes it, with
  the tries of R2.5: Windows removes no open file. The script prints a message that names
  `latest.yaml`, and exits 1. `latest.yaml` keeps its bytes.

### R3 — a linear item pattern (SS-6)

- **R3.1** The reader captures a list item with `(.*)$` and strips its trailing whitespace with
  `str.rstrip`. The session id of a version 2 file is read the same way.
- **R3.2** Each value reads back as at TASK 127; TC-09 and TC-10 keep their assertions.

### R4 — the SS-1 tests stay in their root (SS-5)

- **R4.1** `test_no_git_falls_back_to_claude_project_dir` and
  `test_no_git_no_env_keeps_legacy_cwd_behavior` skip when an ancestor of their temporary root
  holds `.git`. A helper of the test module finds that ancestor, and the skip message names it.
- **R4.2** The walk-up of the script stays as SS-1 fixed it.

### R5 — no script that deletes the live state (SS-4)

- **R5.1** `tests/test_concurrent_state.py` is removed. TC-01 and TC-02 of the test module test
  concurrent runs in a temporary root.
- **R5.2** After the change, no tracked file names the module outside `docs/`, `CHANGELOG.md` and
  `CHANGELOG.ru.md`.

### R6 — scratch removed at the end of a unittest run (TS-1)

- **R6.1** When `session_scratch()` of `tests/_scratch.py` creates a session directory, it
  registers an `atexit` handler with that directory and its root as arguments. At exit the handler
  removes that directory, and that root when the root is empty. It reads no global of the module.
  `tests/test_scratch_hygiene.py` loads a second module object and restores its root after each
  test. The handler of that object touches only the temporary root it was given.
- **R6.2** The pytest hook of `tests/conftest.py` stays. `tests/run_tests.py` gains no sweep hook,
  so `TestRunnerDoesNotSweep` of `tests/test_scratch_hygiene.py` stays true.
- **R6.3** A killed process runs no `atexit` handler. Its directory stays until the stale sweep
  of the next pytest session removes it. A unittest run removes no stale directory.
- **R6.4** When `_ensure_root` or `tempfile.mkdtemp` raises `FileNotFoundError` or
  `FileExistsError`, `session_scratch()` makes the root again and tries once more. A sweep of another process can
  remove the empty root during either call, and `atexit` adds such sweeps.

### R7 — CI jobs on Windows

- **R7.1** `.github/workflows/framework-gates.yml` gains two jobs on `windows-latest`:
  `session-state-windows-floor` with `python-version: "3.11"`, and `session-state-windows-main`
  with `python-version: "3.14"`. Each job:
  - sets `defaults.run.shell: bash`, so a failed command fails its step (D3);
  - checks out with `persist-credentials: false`, and sets up Python with the pinned actions of
    the other jobs;
  - runs `python -m pip install --upgrade pip` and `pip install -r requirements-dev.txt`;
  - runs `python -m pytest -p no:cacheprovider .agent/skills/skill-session-state/scripts/tests/
    tests/test_session_state_contract.py -q`.
- **R7.2** The jobs have no `python-version` list: `tests/test_python_floor.py` allows one version
  matrix in the workflow (D3).
- **R7.3** The script builds `.agent/sessions` with `os.path.join(".agent", "sessions")`, so each
  path that it prints has the form of the platform (D8).
- **R7.4** In the test module of `S/`:
  - TC-01 runs on every platform. Only the tests that hold a POSIX lock or use the stand-in skip
    where `fcntl` is missing;
  - TC-24 holds the real lock where `msvcrt` imports;
  - each test that names a path compares it in the form of the platform.
- **R7.5** Before stage 2, the run reads each test that the jobs run for an assumption of POSIX.
  The read covers path separators, line ends, links, locks, encodings, the temporary directory,
  and the removal of a file that is still open. The audit record lists each test, the assumption
  it meets, and how the change meets it.
- **R7.6** TC-C8 of `tests/test_session_state_contract.py` checks the two jobs of R7.1.
- **R7.7** The first run of the jobs follows the operator's push, after this run. The final report
  of this run names the two jobs. TASK 129 reads their result first, with `gh run list` and
  `gh run view`. A failed test is filed as a defect record and named to the operator, who decides
  whether TASK 129 closes it first (D12).

### R8 — records, documents, staging and checks

- **R8.1** Each of the six records gains `status: fixed`, `resolved_at: 2026-10-26`,
  `resolved_by: TASK 128` and a resolution blockquote after its provenance banner, as ARC-8 holds.
  Its index line in `docs/KNOWN_ISSUES.md` names status `fixed`.
- **R8.2** The WI-39 record gains a progress blockquote after its last one. It states that the two
  archive scripts match their directory by the rule of TASK 127 R6.1. That rule replaces the check
  by name of its table. Its index line in `docs/BACKLOG.md` stays.
- **R8.3** `S/SKILL.md` becomes version `1.3`. Its §1 and §6, and §1 and §6 of
  `System/Docs/SESSION_CONTEXT_GUIDE.md`, state the refusal of a link and the write through a
  temporary file. The guide's §6 states the remedy: remove the link, or replace it with a
  directory or a regular file of one's own. It also states that a link above the three entries
  is followed.
- **R8.4** `CHANGELOG.md` and `CHANGELOG.ru.md` hold v3.48.0. Its **Changed** part states the
  refusal of a link and the remedy.
- **R8.5** The change runs the four stages of `framework-upgrade` §3 step 4. Stage 1 writes these
  copies under new names, and the stage-3 patch gives each final file their bytes:
  - `S/scripts/staged_update_state.py` → `S/scripts/update_state.py`;
  - `S/scripts/tests/staged_test_update_state.py` → `S/scripts/tests/test_update_state.py`;
  - `.agent/tools/staged_archive_move.py` → `.agent/tools/archive_move.py`;
  - `.agent/tools/staged_rebase_links.py` → `.agent/tools/rebase_links.py`;
  - `tests/staged_scratch.py` → `tests/_scratch.py`;
  - `tests/staged_archive_move.py` → `tests/test_archive_move.py`;
  - `tests/staged_script_guards.py` → `tests/test_script_guards.py`;
  - `tests/staged_scratch_hygiene.py` → `tests/test_scratch_hygiene.py`.

  The patch also removes `tests/test_concurrent_state.py`. It touches no other path.

  **Why.** Allow rules run the three scripts. `tests/run_tests.py`, which an allow rule runs, runs
  the three test modules of `tests/`, and `tests/test_scratch_hygiene.py` loads `tests/_scratch.py`.
  The test module of `S/` tests the script by its final name.
- **R8.6** The documents, the changelogs, the records, the CI workflow and the contract test land
  in place before stage 3.
- **R8.7** The checks of TASK 127 apply, with the commands of this change:
  - the behaviour check in a worktree, the mutations and the byte scan;
  - the live-state guard;
  - the check of §3 step 4 for each allowed command that reaches the change, which the PLAN lists.
- **R8.8** The run reads `.claude/settings.local.json` and the user's `~/.claude/settings.json` at
  §2.2, at §4.5 and after the gates of stage 3.
- **R8.9** Before stage 3, the run looks for a link at the three entries of R2.1 in each checkout
  beside this repository that holds `.agent/sessions`. The script runs there under the user's
  rules. The audit record names each link found, and the run names it to the operator.

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — The operator pushes, and CI runs the session state on Windows

- **Actors.** The operator; GitHub Actions; the orchestrator of TASK 129.
- **Precondition.** The operator has committed and pushed this task.
1. Each Windows job checks out the tree on `windows-latest` and sets up Python 3.11 or 3.14.
2. It installs `requirements-dev.txt`, and runs the test module of `S/` and the contract test with
   pytest under bash.
3. The tests that hold a POSIX lock or use the stand-in skip. The others run the script with the
   real `msvcrt`, the runner's code page cp1252, NTFS and paths in the Windows form.
4. The orchestrator of TASK 129 reads both results (R7.7).
- **Alternative 3a.** A test fails, and its job is red. Step 4 files the failure as a defect
  record, and the operator decides.
- **Postcondition.** The results show whether TASK 127 and this task hold on Windows. The jobs
  are the run of TASK 127 UC-1 on Windows: TC-09 runs its values, TC-01 its alternative 2a, and
  TC-24 its alternative 2b.

### UC-2 — A link stands at `latest.yaml`

- **Actors.** An agent at a phase boundary; a link that another process planted, or that a cloned
  repository holds.
- **Precondition.** `.agent/sessions/latest.yaml` is a link to another file.
1. The agent runs `update_state.py`.
2. The script exits 1, and its message names the path and says `is a link`. The target keeps its
   bytes.
3. The failure rule of TASK 127 follows: the agent tells the operator.
- **Alternative 1a.** `.agent/sessions` is a symbolic link or, on Windows, a junction. The script
  refuses it before it creates anything.
- **Alternative 1b.** No link stands, and the move of the temporary file fails at each of its 10
  tries: on Windows another process holds `latest.yaml` open. The script removes the temporary
  file and exits 1, `latest.yaml` keeps its bytes, and step 3 follows.
- **Postcondition.** No byte is written through a link.

### UC-3 — A full unittest discovery of `tests/`

- **Actors.** The operator, or an agent under the local rule.
1. The local rule runs `python3 -m unittest discover -s tests -v`.
2. A test creates its in-repo scratch. At the end of the process, `atexit` removes the session
   directory, and `tests/.scratch/` when it is empty.
- **Alternative 2a.** The process is killed. No `atexit` handler runs, and the directory stays
  until the next pytest session (R6.3).
- **Postcondition.** The session directory of the run does not exist. `tests/.scratch/` exists only
  while another live session holds a directory in it.

<!-- contract:acceptance -->

## 5. Acceptance criteria

New and changed tests of `S/scripts/tests/test_update_state.py`:

- **TC-01** — runs on every platform; two runs at once keep both tasks.
- **TC-07** — checks every call of `open` by name, and treats a mode with `w`, `x`, `a` or `+` as
  a write. It fails on a call of `os.fdopen`, `io.open` or `codecs.open`.
- **TC-19** — a link at `latest.yaml` → exit 1, the message names the path, says `is a link` and
  says to remove it, and the target keeps its bytes. Fails when the check of `latest.yaml` is removed; skipped where
  no link can be created.
- **TC-20** — a link at `.agent/sessions`, a link at `latest.yaml.lock`, and on Windows a junction
  at `.agent/sessions` → exit 1 with `is a link`, and nothing is written through any of them. Fails
  when the check of either entry is removed; each case is skipped where its link cannot be made.
- **TC-21** — a run → `.agent/sessions` holds `latest.yaml` and its lock only, and the file holds
  no CR byte. On POSIX:
  - a new file has the bits `0o644` under the umask, and a file with the bits `0o600` keeps them;
  - under the umask `022`, the temporary file holds no bit for group or others until
    `os.fchmod`;
  - a write onto a link gives the new file the bits `0o644` under the umask, not the link's.

  Fails when `os.fchmod` is removed, when the opener creates with `0o644`, or when the bits come
  from an entry of any kind.
- **TC-22** — `os.replace` made to fail with `OSError` in an imported script → exit 1, the message
  names `latest.yaml`, `latest.yaml` keeps its bytes, and no temporary file stays. Fails when the
  removal of the temporary file is removed.
- **TC-23** — a version 2 file whose session id and decision each hold 100,000 spaces between
  two letters → the run exits 0 within 4 seconds, and both read back unchanged. Fails with either
  pattern of the base.
- **TC-24** — on Windows the test holds byte 0 of `latest.yaml.lock` with `msvcrt.locking` → exit 1
  after the tries of `LK_LOCK`, the message names `latest.yaml.lock`, and `latest.yaml` keeps its
  bytes. The test unlocks the byte before it closes the descriptor. Skipped where `msvcrt` does not
  import.
- **TC-25** — `os.replace` made to fail with `PermissionError` twice in an imported script → exit
  0, the state is written, and no temporary file stays. A second case: `os.replace` fails with
  `OSError`, and `os.remove` with `PermissionError` twice → exit 1, and no temporary file stays. A
  third case: `os.replace` fails with `PermissionError` at each try → exit 1 after 10 tries and 9
  pauses of 0.1 seconds, `latest.yaml` keeps its bytes, and no temporary file stays. Fails when
  the tries of R2.5 are removed, or their count or their pause changes.
- **TC-26** — the helper of R4.1 names an ancestor that holds `.git` as a directory, and one that
  holds `.git` as a file, as a linked worktree does. For a directory with no such ancestor of its
  own, it answers as for the directory's parent.
- **TC-27** — the script loaded while `os.path` is `ntpath` names the session directory
  `.agent\sessions`. Fails with the literal of the base.
- **TC-28** — `os.lstat` patched in an imported script: a directory whose reparse tag is
  `0xA0000003` or `0xA000000C` is refused as a link, and one whose tag is `0x9000001A` is not. A
  FIFO at `latest.yaml` is refused as no regular file, and a regular file at `.agent/sessions` as
  no directory. Runs on every platform. Fails when the tag check, the branch of the reparse point,
  or either check of the kind is removed.
- **TC-29** — on POSIX, `os.lstat` is patched in an imported script. It reports a regular file over
  a link to an existing file at `latest.yaml`, and over a dangling link at `latest.yaml.lock`.
  Each run exits 1 with no `is a link` in its output, the linked file keeps its bytes, and the
  target of the dangling link is not created. Fails when `O_NOFOLLOW` is removed from the opener or from the open of the lock file.
  Skipped where `os.O_NOFOLLOW` is missing or no link can be made.

Changed tests of other modules:

- **TC-12 of `S/`**, TC-A20 of `tests/test_archive_move.py` and TC-G11 of
  `tests/test_script_guards.py` → no planted module runs through a path in other letter case.
- **TC-H1** of `tests/test_scratch_hygiene.py` — a child process creates a session directory under
  a redirected root, names a second empty directory as its root, and exits. The first root holds
  nothing, and the second stays. Fails when the registration of R6.1 is removed, or when the
  handler reads the globals of the module at exit. The test never calls `atexit._run_exitfuncs()`.
- **TC-H2** of `tests/test_scratch_hygiene.py` — the root removed before the first
  `tempfile.mkdtemp`, and in two more cases `_ensure_root` made to raise `FileNotFoundError` or
  `FileExistsError` once → `session_scratch()` returns a directory each time. Fails when R6.4 is removed, or when the root
  is made once before the tries.
- **TC-C4** — `S/SKILL.md` has version 1.3. Its §1 holds `is a link` and `temporary file`, and its
  §6 holds `os.replace`.
- **TC-C5** — the guide's §1 holds `temporary file`, and its §6 holds `is a link`.
- **TC-C8** — the workflow holds two jobs on `windows-latest`, with Python 3.11 and 3.14 and the
  shell bash, and a pytest step in each runs both paths of R7.1.

The criteria of the task:

- **A1** — R1: the runs in other letter case pass, and fail when the check of device and inode is
  removed from either script.
- **A2** — TC-19 to TC-22, TC-25, TC-28 and TC-29 pass.
- **A3** — TC-23, TC-09 and TC-10 pass.
- **A4** — TC-26 passes. Under a `TMPDIR` inside a git work tree, the two SS-1 tests skip and
  write nothing.
- **A5** — `tests/test_concurrent_state.py` does not exist, and
  `git grep -l test_concurrent_state -- . ':!docs' ':!CHANGELOG.md' ':!CHANGELOG.ru.md'` prints
  nothing.
- **A6** — TC-H1 and TC-H2 pass. The check of §3 step 4 for the local unittest discovery of
  `tests` finds no difference after stage 3.
- **A7** — TC-01, TC-11, TC-27 and TC-C8 pass. The test steps of the new jobs pass when `gates.py`
  runs them on macOS. `gates.py` skips the install steps, so pip installs nothing outside a
  virtual environment. The audit record holds the read of R7.5.
- **A8** — the six records are `fixed`, with their index lines, and the WI-39 record holds the
  progress of R8.2.
- **A9** — the gates pass on the patched worktree and, after stage 3, on the tree. Each mutation
  of the PLAN makes its test fail.
- **A10** — the checks of R8.7 pass. The audit record holds the readings of R8.8 and the search of
  R8.9.
- **A11** — TC-C4 and TC-C5 pass. The **Changed** part of v3.48.0 in each changelog names the
  refusal of a link and the remedy. `regcheck.py` finds no warning on an added line of the
  documents, the changelogs and the records.
- **A12** — after the push, owned by TASK 129: both Windows jobs pass, TC-24 among their tests
  (R7.7). This run cannot decide it.
- **A13** — the final report of this run names `session-state-windows-floor` and
  `session-state-windows-main`, and asks the operator to push (R7.7).

<!-- contract:open-questions -->

## 6. Open questions

None. The operator chose the order (D1) and the records (D2).

## 7. Decisions

- **D1**, 2026-10-26, operator: this task runs the session state on Windows in CI and closes the
  six records; TASK 129 ports the archive chain to Windows. Answer "Сначала CI и записи".
  Rejected: the archive chain first, which a run on macOS can check only by emulation.
- **D2**, 2026-10-26, operator, at the retro of TASK 127: the six records close in the next task.
- **D3**, 2026-10-26, orchestrator: the Windows jobs run Python 3.11 and 3.14, the floor and the
  main version of README §3, as the tooling job does. The 3.13 of the report lies between them.
  Two jobs of one version each, since `tests/test_python_floor.py` allows one `python-version`
  list. Each job sets the shell bash. Rejected:
  - 3.13 alone, which leaves unchecked an API that 3.11 lacks on Windows;
  - a second matrix, which fails that test;
  - one job with both versions, where a failure on 3.11 hides the result of 3.14;
  - PowerShell, the default shell, where a failed command early in a block does not fail its
    step.
- **D4**, 2026-10-26, orchestrator: TS-1 is closed by `atexit` in `tests/_scratch.py`. Rejected: a
  sweep hook in `tests/run_tests.py`, which `TestRunnerDoesNotSweep` forbids, and which a full
  discovery of `tests/` would not run.
- **D5**, 2026-10-26, orchestrator: `tests/test_concurrent_state.py` is removed. Rejected: a
  rewrite in a temporary root; TC-01 and TC-02 already test concurrent runs.
- **D6**, 2026-10-26, orchestrator: the script refuses a link at the three entries, and writes
  through a temporary file that `os.replace` moves. A move replaces a link at `latest.yaml` and
  writes nothing through it. On POSIX, `O_NOFOLLOW` closes the window of the lock file and of the
  read. Accepted, for a process that can swap entries in `.agent/sessions` during a run can
  already write the scripts of the repository:
  - a link swapped in at `.agent/sessions` between its check and the move;
  - on Windows, which has no `O_NOFOLLOW`, a link swapped in at the lock file or at `latest.yaml`
    between its check and its open.
  Rejected: descriptors of the directory (`dir_fd`). Windows lacks them, so the script would keep a
  second path for one platform.
- **D7**, 2026-10-26, orchestrator: SS-5 is closed in the tests. Rejected: a change of the
  walk-up, which SS-1 fixed on purpose.
- **D8**, 2026-10-26, orchestrator: the script builds `.agent/sessions` with `os.path.join` (Mode A
  M1). Rejected: a test that accepts both separators, which keeps the mixed form in every message
  on Windows.
- **D9**, 2026-10-26, orchestrator: a move or a removal that fails with `PermissionError` is tried
  10 times, 0.1 seconds apart, on every platform. On Windows a reader or a virus scan can hold the
  file without `FILE_SHARE_DELETE` for a moment. Rejected: one try, which fails a phase boundary
  for a moment's hold; tries on Windows only, which no test on POSIX reaches.
- **D10**, 2026-10-26, orchestrator: on POSIX the new file keeps the permission bits of the old
  one, and a first file gets `0o644` under the umask (Mode A m2). Rejected: a fixed `0o644`, which
  loosens a file that the user set to `0o600`.
- **D11**, 2026-10-26, orchestrator: a reparse point counts as a link only when its tag is a name
  surrogate, a symbolic link or a junction (Mode A N1). Rejected: every reparse point, which
  refuses a project in a cloud folder whose files are placeholders.
- **D12**, 2026-10-26, orchestrator: TASK 129 reads the first run of the Windows jobs (R7.7). The
  run never pushes; the operator commits and pushes.
- **D13**, 2026-10-26, orchestrator: the check of R2.1 also refuses an entry of another kind. A
  FIFO at `latest.yaml` blocks the read while the lock is held. Mode A named it a finding before
  the task; the same `os.lstat` serves both checks. Accepted, as in D6: a FIFO swapped in between
  the check and the read. Rejected: `O_NONBLOCK` and a check of `fstat` after the open, a second
  check for the window that D6 accepts.
- **D14**, 2026-10-26, orchestrator, under the operator's rule recorded at TASK 124: fix round 1
  of stage 2 fixes the findings of both reviews that break something real. It fixes the race of
  `_ensure_root`, the bits of the temporary file, and the wording of the documents and the
  changelogs. It also closes the gaps of the tests. Each other finding stands as a limit of this
  task:
  - the script follows a link above the three entries, at `.agent` or a parent. The names under
    it stay fixed, so another checkout's state can be read and replaced, nothing else;
  - a run killed between the creation and the move leaves its temporary file, which no run reads;
  - a file system that refuses `os.fchmod` or `os.fsync` makes the write exit 1;
  - the Windows jobs install `requirements-dev.txt` without hashes, as the other jobs do;
  - R1 keeps the check by name alone on a volume without inode numbers (PLAN H2).

  Rejected: a refusal of a link at `.agent`, which an installation that links `.agent` whole
  would meet at each phase boundary.
- **D15**, 2026-10-26, orchestrator: round 2 of stage 2 passed. Fix round 2 corrects the message
  and the docstring of the script to the remedy of R2.1, catches `FileExistsError` in R6.4, and
  sets the umask of the bits check of TC-21. A limit joins D14: the new state keeps the mode bits
  of the old file, not its ACL, its extended attributes or its owner. Round 3 is the last of the
  bound of `framework-upgrade` §3 step 4.
- **D16**, 2026-10-26, orchestrator: stage 2 closes at round 3. Both reviews passed with no new
  finding, and the limits of D6, D13, D14 and D15 stand.

## 8. Measurements of this run

- The six records reproduced at the retro of TASK 127; each `sh` block printed its defect line.
- `tests/test_python_floor.py:429` `matrix = re.findall(r"python-version:\s*\[([^\]]*)\]", text)`
  requires one version list.
- `tests/run_tests.py` runs `test_archive_move`, `test_script_guards` and `test_scratch_hygiene`,
  and `test_scratch_hygiene` loads `tests/_scratch.py`.
- `ntpath.join("C:\\root", ".agent/sessions")` keeps the `/`, so the base names the state with
  both separators on Windows.

<!-- contract:out-of-scope -->

## 9. Out of scope

- The Windows port of the archive chain: `archive_move.py`, `rebase_links.py` and `slot_links.py`
  — TASK 129. This task edits the first two for ARC-13 only.
- The locks and `O_NOFOLLOW` of `run-feedback` — the third task of the Windows series.
- WI-39 for the nine scripts without a filter — the WI-39 record.
- A statement of supported platforms in `README.md` — after TASK 129. TASK 127 §9 gave it to the
  last task of the series.
- The `python3` launcher on Windows — the reporter's answer is still open. TASK 127 §9 gave the
  question to this series.
- The stale sweep of `tests/_scratch.py` on Windows, where `os.kill(pid, 0)` sends
  `CTRL_C_EVENT` — a finding before the task.
- The five findings in the inbox of `run-feedback` from earlier sessions.
