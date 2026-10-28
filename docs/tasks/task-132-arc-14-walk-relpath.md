# TASK 132 — The inbound walk and the file mode of `rebase_links.py` end without a traceback on a path that names a device

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 132 |
| Slug | arc-14-walk-relpath |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | ARC-14; CI run 40637795256 of `30616d2`; the operator's answer of 2026-10-28 (D1) |
| Base revision | `6aedb2203c26e6f6c745a362f950008e63e5a291` |
| Closes | ARC-14 |
| Archive name | `task-132-arc-14-walk-relpath.md` |
| Revision | 4 |

**Revision 4** records round 1 of stage 2, which passed, and the LOW findings that stay (D12).
**Revision 3** applies m1, m2 and N1 to N3 of Mode A round 2, which passed, with no further round
(D11).
**Revision 2** applies M1 to M3, m1 to m5, N1, N3 and N4 of Mode A round 1 (D10).

**Request.** TASK 131 added a step `Run the archive-chain tests` to both Windows jobs of
`.github/workflows/framework-gates.yml`. Its first run, CI run 40637795256 of `30616d2`, failed one
test in the job on Python 3.14. TASK 131 R7.4 filed the failure as ARC-14. The operator asked to fix
it, and chose the scope (D1).

A coordinate into a file that this task edits carries the pin `@6aedb22`, the base revision.

<!-- contract:problem -->

## 1. Problem

1. **The job `Session state on Windows (3.14)` fails.** Its step `Run the archive-chain tests`
   reports 1 failed, 371 passed and 27 skipped. The job on 3.11 passes the same step: 372 passed and
   27 skipped (§8). The failed test is TC-W16 of the inbound mode,
   `tests/test_script_guards.py::TestInboundGuard::test_w16_no_pyc_under_a_relative_null_device`.
   It makes a directory named `nul` in the work tree through a `\\?\` path, and runs the inbound
   mode in walk mode. The run exits 1 with
   `unexpected: ValueError: path is on mount '\\.\nul', start on mount 'C:'`.
2. **The cause.** `ntpath.relpath` calls `abspath` on both of its paths, then raises `ValueError`
   when their drives differ (§8). On Windows `abspath` resolves a path whose last part names a
   reserved device, such as `C:\r\nul`, to the device `\\.\nul`. The walk of the inbound mode
   calls `os.path.relpath` at three sites:
   - `.agent/tools/slot_links.py:171@6aedb22` `rel = os.path.relpath(exc.filename or root, root)`;
   - `.agent/tools/slot_links.py:181@6aedb22` `rel = os.path.relpath(path, root)`;
   - `.agent/tools/slot_links.py:192@6aedb22` `rel = os.path.relpath(os.path.join(dirpath, name), root)`.

   The second is the record of a directory whose `os.lstat` fails, which TASK 131 R2.5 added. It
   is the likely site (ARC-14): the message of the run names no line. By that reading, on 3.14 the
   `os.lstat` of the directory `nul` fails, and that record raises; on 3.11 it succeeds, and the
   record is never built.
3. **The file mode raises the same error.** `rebase_document_links` computes the path of a link
   target from the root with `os.path.relpath`. A link such as `[x](nul)` raises there, and the
   file mode has no handler for it: Steps 5.5 and 7.6.5 end in a traceback with exit 1. The title of
   TASK 131 states that the file mode ends without a traceback. The first site is:
   - `.agent/tools/rebase_links.py:300@6aedb22` `if os.path.relpath(denote_old, root) in known_slots:`.
4. **An operand that names a device raises too.** `_refuse_operand` passes the operand to
   `_under_git`, which computes its path with `os.path.relpath`. An operand such as
   `docs/tasks/nul` raises there, before any refusal:
   - `.agent/tools/rebase_links.py:407@6aedb22` `segments = os.path.relpath(absolute, cwd).split(os.sep)`.
5. **A `--to` that names a device raises too.** `rebase_document_links` computes each rewritten
   target with `os.path.relpath` from `new_base`, the path of `--to`. `ntpath.relpath` resolves
   that start as well. `--to nul` and `--to docs/nul` pass `_leaves_tree`, and then raise at each
   rewrite, before any write:
   - `.agent/tools/rebase_links.py:286@6aedb22` `new_path = os.path.relpath(identity, new_base)`;
   - `.agent/tools/rebase_links.py:320@6aedb22` `new_path = os.path.relpath(denote_old, new_base)`.
6. **TASK 131 R5.1** counts a `ValueError` of `os.path.commonpath` as a path outside, at seven
   checks. It names no `ValueError` of `os.path.relpath`.

An emulation on macOS measured items 2 to 5 (§8). No run before the push can reach Windows; the
Windows jobs confirm the fix after the operator's push (R4).

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | The walk of the inbound mode reads its paths as text | yes | three sites; the records of the base | A1 |
| R2 | The file mode counts a `ValueError` of `relpath` as a path outside | yes | a link target; an operand; `--from` and `--to` | A2 |
| R3 | Tests | yes | TC-D1 to TC-D6; mutations | A3, A4 |
| R4 | CI on Windows | yes | TC-W16 on both jobs after the push | A5 |
| R5 | Documents and records | yes | v3.50.1; ARC-14 | A6 |
| R6 | Staging and checks | yes | four copies under new names; the check of what runs; the settings | A7 |

## 3. Requirements

### R1 — the walk of the inbound mode reads its paths as text

- **R1.1** `_walk` of `.agent/tools/slot_links.py` derives each repo-relative path from the text
  of the path: the part after `os.path.join(root, "")`, with each `os.sep` written as `/`. The
  path `root` itself is `.`. The walk calls no `os.path.relpath`.

  **Why.** `os.walk` builds each path by joining onto `root`, and so does each record of an error
  that it passes to `onerror`. On POSIX the text gives the path that `relpath` gives. On Windows
  `relpath` also drops the dots and spaces that end the last part of a path, and the single dot
  that ends an inner part. The text keeps them.
- **R1.2** R1.1 holds at the three sites of §1 item 2: the record of an error of `os.walk`, the
  record of a directory whose `os.lstat` fails, and the list of files.
- **R1.3** For every other entry, the walk gives the paths and the records of the base. On Windows
  this holds for an entry no part of whose path ends in a dot or a space (§9).

### R2 — the file mode counts a `ValueError` of `relpath` as a path outside

- **R2.1** A helper `_relative(path, start)` of `.agent/tools/rebase_links.py` returns
  `os.path.relpath(path, start)`, or `None` when that call raises `ValueError`.
- **R2.2** In `rebase_document_links`, a link target whose `_relative` from the root is `None` is
  `ESCAPES_ROOT`, and stays as written. The check runs after the check of `_inside`, before any
  other check of the target. The later checks reuse the path that `_relative` returned.
- **R2.3** `_refuse_operand` refuses an operand whose `_relative` from the working directory is
  `None`, with the reason `lies outside the working directory`, before `_under_git`. The file mode
  then exits 2 and writes nothing.
- **R2.4** `_main` refuses a `--from` or a `--to` whose
  `_relative(os.path.join(os.getcwd(), value), os.getcwd())` is `None`, with the reason
  `<option> does not lie inside the working directory`. It exits 2 before it reads any operand, as
  TASK 131 R5.2 refuses a drive or a root. The check runs in `_main`, after `_leaves_tree`, which
  calls no `os.getcwd` (TC-W18 binds its `os` to a namespace).
- **R2.5** In the file mode, each other call of `os.path.relpath` of `rebase_links.py` takes as
  each of its two arguments one of these:
  - the root;
  - a path that R2.2, R2.3 or R2.4 checked;
  - a slot archive that matches the pattern of TASK 116 R8.1.
- **R2.6** Two other callers reach those calls without `_main`:
  - `slot_links._write_file` calls `_under_git` with a path of the scan set. Such a path is a
    `.md` file that `_read` opened as a regular file, and no device is one;
  - `archive_protocol._rebase_moved_document` calls `rebase_file` with the `to_dir` `docs/tasks`
    or `docs/plans`, and catches `ValueError`:
    `.agent/tools/archive_protocol.py:324@6aedb22` `except (OSError, ValueError):`.

### R3 — tests

- **R3.1** New tests TC-D1 to TC-D6 (§5). On POSIX a test reaches each site with a stand-in for the
  Windows behaviour: `os.path.relpath` patched to raise `ValueError` when the last part of its path
  or of its start is `nul`.
- **R3.2** TC-W16 keeps its text, and runs on both Windows jobs. No test of the base gains a skip.
- **R3.3** TC-D1 to TC-D3 skip on Windows, with the reason in their marker: a plain path there
  names the device, not an entry `nul` (D8).
- **R3.4** Each new test fails under a mutation that the PLAN names. Each new test but TC-D6 fails at
  the base, red first.

### R4 — CI on Windows

- **R4.1** The step `Run the archive-chain tests` of both Windows jobs stays as TASK 131 R7.1 wrote
  it. It runs the two test modules that this task changes.
- **R4.2** The first run of the step follows the operator's push, after this run. The next task
  reads its result first, with `gh run list` and `gh run view`. A failed test is filed as a defect
  record and named to the operator, as TASK 131 R7.4 states.

### R5 — documents and records

- **R5.1** `CHANGELOG.md` and `CHANGELOG.ru.md` hold v3.50.1, with the fix under Fixed.
- **R5.2** The record of ARC-14 takes the status `fixed`, with the date and TASK 132. Its index line
  in `docs/KNOWN_ISSUES.md` takes the same status and a summary of the fix (`known-issues-format`).
- **R5.3** `docs/ARCHITECTURE.md`, `skill-archive-task` and `skill-safe-commands` stay as they are
  (D5).

### R6 — staging and checks

- **R6.1** The change runs the four stages of `framework-upgrade` §3 step 4. Stage 1 writes these
  copies under new names, and the stage-3 patch gives each final file their bytes:
  - `.agent/tools/staged_rebase_links.py` → `.agent/tools/rebase_links.py`;
  - `.agent/tools/staged_slot_links.py` → `.agent/tools/slot_links.py`;
  - `tests/staged_script_guards.py` → `tests/test_script_guards.py`;
  - `.agent/tools/staged_test_slot_links.py` → `.agent/tools/test_slot_links.py`.

  The patch touches no other path.

  **Why.** An allow rule runs `rebase_links.py`, and `rebase_links.py` loads `slot_links.py`.
  `tests/run_tests.py`, which an allow rule runs, runs `tests/test_script_guards.py`. The two test
  modules load the scripts by their final names ⇒ landed in place, their new tests fail the gates
  before stage 3.
- **R6.2** The changelogs, the record of ARC-14 and its index line land in place before stage 3.
- **R6.3** The checks of TASK 131 R9.3 apply. The PLAN lists their commands:
  - the gates, on a worktree that holds the stage-3 patch;
  - the mutations, and a scan of each changed file for bytes outside its encoding;
  - the listing of `.agent/sessions/` before and after each check;
  - the check of §3 step 4 for each allowed command that reaches the change.
- **R6.4** The run reads `.claude/settings.local.json` and the user's `~/.claude/settings.json` at
  §2.2, at §4.5 and after the gates of stage 3. The audit record names each file of the change that
  a rule of either file runs, and quotes no rule.
- **R6.5** The change edits no permission rule, hook or settings key.

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — An agent on Windows archives a task in a tree with a device name

- **Actors.** An agent on Windows with Python 3.14, running `skill-archive-task`.
- **Preconditions.** The work tree holds a directory or a file whose name is a reserved device
  name, such as `nul`, or a document links to one.
- **Main flow.**
  1. Steps 5.5 and 7.6.5 rebase the moved documents. A link to a device is `ESCAPES_ROOT` and
     stays as written; the step exits 3.
  2. Step 8 walks the tree where no git work tree exists. A directory named after a device whose
     `os.lstat` fails is `UNREADABLE`; the step exits 3 and lists it.
- **Alternative 1a.** An operand of the file mode names a device: exit 2, and nothing is written.
- **Alternative 1b.** `--from` or `--to` names a device: exit 2, before any operand is read.
- **Postconditions.** No run ends in a traceback or in `unexpected`.

<!-- contract:acceptance -->

## 5. Acceptance criteria

Tests of the walk, in `.agent/tools/test_slot_links.py`:

- **TC-D1** — a directory `nul` whose `os.lstat` fails, with `os.path.relpath` raising for `nul` →
  the walk records `nul` as `UNREADABLE`, and lists the files of the other directories.
- **TC-D2** — a directory `nul` whose `os.scandir` fails, with the same stand-in → the record of
  the error names `nul` as `UNREADABLE`. An `os.scandir` that fails for the root → the record
  names `.`.
- **TC-D3** — a file named `nul`, with the same stand-in → the walk lists it under its path.
- **TC-D4** — a tree of directories and files with no device name. The expected paths come from
  the real `os.path.relpath`. Then `_walk` runs with `os.path.relpath` patched to raise on every
  call → it gives the same paths, and calls no `relpath`.

Tests of the file mode, in `tests/test_script_guards.py`, class `TestRebaseLinksGuard`:

- **TC-D5** — with the same stand-in:
  - a document with `[a](ARCHITECTURE.md)` and `[n](nul)` → `rebase_document_links` gives
    `ESCAPES_ROOT` for the link to `nul` and rewrites the other. `_main` on that document exits 3,
    and the link to `nul` stays as written;
  - the operand `docs/tasks/nul` → `_refuse_operand` gives `lies outside the working directory`,
    and `_main` exits 2;
  - `--to nul`, and `--from nul` → `_main` exits 2 with `does not lie inside the working
    directory`, and the document keeps its bytes.
- **TC-D6** — on Windows only, with no stand-in: the link to `nul` is `ESCAPES_ROOT`; the operand
  `docs/tasks/nul` exits 2 with `lies outside the working directory`; `--to nul` exits 2.

The criteria of the task:

- **A1** — R1: TC-D1 to TC-D4 pass, and so do the tests of the walk of TASK 131, TC-W20 and TC-W40
  among them.
- **A2** — R2: TC-D5 passes, and so do TC-W17, TC-W18 and the other tests of `rebase_links.py`.
- **A3** — R3: each new test but TC-D6 fails at the base. TC-W16 keeps its text.
- **A4** — each mutation of the PLAN makes its test fail on macOS, except those that the PLAN marks
  as killed on Windows only.
- **A5** — after the push, owned by the next task: both Windows jobs pass the step of R4.1, with
  TC-W16 and TC-D6 among its tests. TC-D6 passes there. This run cannot decide it.
- **A6** — R5: both changelogs hold v3.50.1, and the record of ARC-14 and its index line say
  `fixed`. The texts of R5.3 equal the base. `scan_register.py` finds no warning on a line that the
  change adds.
- **A7** — R6: the gates pass on the patched worktree and, after stage 3, on the tree. The checks of
  R6.3 and R6.4 pass. No settings file of the repository changes (R6.5).

<!-- contract:open-questions -->

## 6. Open questions

None. The operator chose the scope (D1).

## 7. Decisions

- **D1**, 2026-10-28, operator: the task fixes the walk of the inbound mode and the file mode of
  `rebase_links.py`, each call of `relpath` that can meet a device. Answer "Обход и файловый режим
  (Recommended)". Rejected: the walk alone, which leaves a traceback in Steps 5.5 and 7.6.5.
- **D2**, 2026-10-28, orchestrator: the walk reads each path as text (R1.1). The entry stays in
  the records under its name. Rejected: a `ValueError` caught at each site with the entry dropped,
  which loses a file of the walk.
- **D3**, 2026-10-28, orchestrator: the file mode counts a `ValueError` of `relpath` as a path
  outside, as TASK 131 R5.1 does for `commonpath`. Rejected:
  - `ntpath.isreserved`, which Python 3.11, the floor of the Windows jobs, lacks;
  - a list of device names, whose set differs between versions of Windows.
- **D4**, 2026-10-28, orchestrator: TC-W16 keeps its text (R3.2). It is the only test that runs the
  bytecode prefix of TASK 131 R4 where `os.devnull` is `nul`.
- **D5**, 2026-10-28, orchestrator: `docs/ARCHITECTURE.md` stays. The change adds no component and
  no interface; the paragraph on archiving names no call of `relpath`.
- **D6**, 2026-10-28, orchestrator: the record of ARC-14 closes with this task. The Windows jobs
  confirm the fix after the push; a failure there reopens the record (R4.2).
- **D7**, 2026-10-28, orchestrator: the windows of a race of TASK 131 D7 stay as they are. The
  change adds no file-system call.
- **D8**, 2026-10-28, orchestrator: TC-D1 to TC-D3 skip on Windows (R3.3). Their premise is an entry
  `nul` that a plain path makes, which POSIX gives and Windows does not. On Windows TC-W16 runs the
  walk on a real directory `nul`, and TC-D6 runs the file mode. Rejected: tests that make and
  remove each `nul` through a `\\?\` path, which no run before the push can check.
- **D9**, 2026-10-28, orchestrator: `--from` and `--to` are refused as TASK 131 R5.2 refuses a drive
  (R2.4). The refusal comes before any operand is read. Rejected: a check at each call of
  `relpath` from `new_base`, which lets the run read every operand first.
- **D10**, 2026-10-28, orchestrator: revision 2 applies M1 to M3, m1 to m5, N1, N3 and N4 of Mode A
  round 1. N2 needs no change: the first run of the step after the push measures 3.11 (A5).
- **D11**, 2026-10-28, orchestrator: revision 3 applies m1, m2 and N1 to N3 of Mode A round 2, which
  passed. The reviewer stated that they need no further round.
- **D12**, 2026-10-28, operator: round 1 of stage 2 passed: the code review approved, and the
  security audit passed. The run closes with no further round. The operator's rule, recorded at
  TASK 124 D17: once both reviews pass and only narrow LOW routes remain, the run closes. Stage 4
  noted that two findings below are fixes rather than narrow routes: the test of the order of R2.4
  and the module docstring. Asked, the operator answered "Закрыть как есть (Recommended)". A change
  of the reviewed bytes would need another round. The LOW findings of the round stay:
  - no test pins that the check of R2.4 runs before any operand is read;
  - the stand-in of R3.1 raises for `nul` alone, also when the path and the start name the same
    device; `ntpath.relpath` returns `.` there, and its set of device names depends on the version
    of Windows;
  - the helper of the stand-in in `tests/test_script_guards.py` sits among the module's
    constants, and `test_slot_links.py` adds a marker with the condition of `posix_premise`;
  - the module docstring of `rebase_links.py` and the docstring of `_refuse_operand` name no
    device;
  - on Windows an operand such as `docs/tasks/nul:x` may meet R2.3 before the check of R5.5 of
    TASK 131, with the same exit 2;
  - on Windows, a record of the walk names `x./y.md` where the read opens `x\y.md` (§9);
  - a device-named `.md` file of the walk, such as `docs\con.md` before Windows 11, is probed
    before `_open_nofollow` refuses it;
  - `relative` of the walk slices with no check of the prefix, which `os.walk` of 3.11 to 3.14
    always gives;
  - the record of ARC-14 is `fixed` before the Windows jobs confirm the fix (D6).

## 8. Measurements of this run

- CI run 40637795256 of `30616d2`: the job `Session state on Windows (3.14)`, on Python 3.14.9, ran
  the step `Run the archive-chain tests` with 1 failed, 371 passed and 27 skipped. The job on 3.11
  ran it with 372 passed and 27 skipped. Every other job of the run passed.
- `inspect.getsource(ntpath.relpath)` of Python 3.14.8: the function calls `abspath(start)` and
  `abspath(path)`, then raises `ValueError("path is on mount %r, start on mount %r")`.
- An emulation on macOS with Python 3.14.8, at the base, in a temporary root:
  `os.path.relpath` patched to raise that `ValueError` for a path whose last part is `nul`.
  - The file mode on a document that links to `nul`: `rebase_document_links` raises `ValueError`.
  - `_walk` with a directory `nul` whose `os.lstat` fails: `_walk` raises `ValueError`.
  - With the stand-in also raising for a start whose last part is `nul`: `_refuse_operand` of
    `docs/tasks/nul` raises `ValueError`, and so does `_main` with `--to nul` or `--to docs/nul` on
    a document with a link to rewrite.
- `ntpath.isreserved` exists in Python 3.14.8; Python 3.13 added it.

<!-- contract:out-of-scope -->

## 9. Out of scope

- The reserved device names themselves: which names Windows treats as devices, and in which
  versions. The task handles the `ValueError`, whatever the name.
- A file named after a device that a git work tree lists. Git for Windows refuses to check out such
  a name by default (`core.protectNTFS`).
- The findings before TASK 131 that its §9 lists.
- An entry whose name ends in a dot or a space, on Windows. `relpath` drops those characters, so
  the base listed `a.md.` as `a.md`; the text of R1.1 keeps them. Such a name reaches a file only
  through a `\\?\` path. A walk entry under a directory `x.` is read at `x\y.md`, at the base and
  after the change, and written there at the base only: a finding before the task.
- The locks of `run-feedback` — the third area of the Windows series.
- Findings before the task, from the security audit of stage 2, each LOW:
  - on Python 3.11 for Windows, `os.lstat` of a junction named after a device may give the device.
    The walk of TASK 131 R2.5 may then follow the junction and read `.md` files outside the tree.
    The check of the real path refuses each write. The audit inferred this from the code; no run
    on Windows measured it. A check of `stat.S_ISDIR` in `entered` would close it;
  - `os.path.exists(denote_new)` of the file mode probes a path that no check keeps inside the
    root;
  - the text report of the file mode prints the control characters of a link target unescaped
    (TASK 131 §9).
