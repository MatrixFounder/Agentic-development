# Framework Audit 131 — The archive chain runs on Windows, and the file mode of `rebase_links.py` ends without a traceback

- **Task:** 131 `archive-chain-windows`. It archives to
  `docs/tasks/task-131-archive-chain-windows.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1.
- **Date:** 2026-10-27. **Base revision:** `6f3d65c8d085c48ae36e2e63a7f47fc9ac2b8dce`, clean tree
  at start (TASK 130, committed by the operator as `6f3d65c`).
- **Source:** the defect report of 2026-10-26 (TASK 127 §1), TASK 127 D1, and the operator's answers
  of 2026-10-27 (TASK D1 to D3).

## 0. Emergency Bypass

None. `skill-archive-task` is a TIER 1 skill; the change edits the scripts it runs and leaves its
text as it is (TASK D10). It touches no TIER 0 skill and removes no load of one.

## Archive (§1)

TASK 130 and PLAN 130 archived under ID 130:
- `task_id_tool.py "audit-the-copies-that-run" --proposed-id "130" --no-correction`: `generated`,
  `task-130-audit-the-copies-that-run.md`;
- both moves `"ok": true`, method `link`;
- Step 5.5: `0 rewritten / 0 needing review`, exit 0;
- Step 7.6.5: one `SLOT_RESOLVED`, exit 0;
- Step 8 with `--since e89753f706403a63026de3a66d7aee9999be598b`: exit 3. It lists the two
  `INBOUND` records of old changelog entries, `CHANGELOG.md:3618@6f3d65c` and
  `CHANGELOG.ru.md:3647@6f3d65c`, which carry no reason and stay. Step 8 rewrote no file.

## Research (§1)

The facts of TASK §8 come from reading the tree at the base, from runs in roots under the session's
scratchpad, and from the archived TASK 127 and TASK 128. The retro claim
`framework-upgrade-task-131-archive-chain-windows` was taken at the start of the run, and the base
was recorded in the session state before §1. The CI run 40511139061 of `6f3d65c` passed each of its
nine jobs. The operator answered three questions before the TASK was written (TASK D1 to D3).

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

The operator paused the run once while the first reviewer read the brief. That reviewer was stopped
before it reported, and a second reviewer ran the same brief on the same fingerprint. The reviewer, a
`task-reviewer` agent with no shell, read the TASK at SHA-256 `1a0a39a9387f…` and wrote nothing.
The fingerprint of the tree was `de67e211d76f` before and after the round. No failure condition of
the verificator's §4 applies, and root integrity holds. The committed, local and user rules reach
no file of the change that R9.1 does not stage. Its findings:
- M1: R1.5 removed the archive after a refusal at step 9, when the source is gone or replaced and
  the archive is the content's last name. The base keeps it there (TC-A21, TC-A22);
- M2: on Windows `rebase_document_links` writes the `denotes_old` of a `SLOT_RESOLVED` record with
  `\`, and `_adds_parts` splits on `/` only. Every slot link of Steps 5.5 and 7.6.5 then exits 2.
  The orchestrator reproduced it with `ntpath`: `_adds_parts` returns true;
- M3: TC-C8 asserts one pytest step per Windows job, and R7.1 adds a second;
- M4: the reparse-tag check, the read-only check, `O_BINARY` and the drive clauses of R5.2 had no
  test that fails on POSIX. No test reached the identity check of R1.4 step 3;
- M5: D7 stated a wrong outcome for a swap back inside step 7, missed the `docs` swaps at steps
  2–3 and 9–10, and R1.6 retried the unlink without step 9;
- m1 to m10:
  - other `OSError`s of R1.4;
  - the base flags `O_NOFOLLOW` and `O_NONBLOCK` of the source opens;
  - three tests that assert the refusal text of an `O_NOFOLLOW` open;
  - three runner conditions missing from R6.6;
  - the open of `task_id_tool.py:104@6f3d65c`;
  - a link written with `\`;
  - stale texts;
  - criteria for R1.8, R2.6, R3.1, R1.6 and R1.5;
  - register (T3, T1), and two unmeasured claims;
- N1 to N7, notes:
  - R4.2, R5.1 and R2.2 hold;
  - D7's bullet 3 assumes an unmeasured behaviour of `O_CREAT | O_EXCL` on Windows;
  - `FILE_SHARE_DELETE` protects steps 3 to 8;
  - the walk filter has a read-only window;
  - a volume with `st_ino` 0;
  - the change edits no settings;
  - TC-W16 runs in walk mode on POSIX.

Before the task:
- B1, LOW: `rebase_links.py:277@6f3d65c` and `:293@6f3d65c` compare slot paths with letter case.
  On a case-insensitive volume a link to `docs/task.md` is rewritten as an ordinary path;
- B2, LOW: the TASK examines no Windows behaviour of `archive_protocol.py` (`shutil.move`) or of
  `task_id_tool.py`; D3 runs their tests on Windows for the first time (R7.4).

The orchestrator applies every finding in revision 2 (TASK D18).

### Round 2 — TASK revision 2: FAIL

The same reviewer, resumed, read the TASK at SHA-256 `88fa5ffb5cbd…` and wrote nothing. The
fingerprint was `f39368905508` before and after the round. It found each fix of round 1 correct but
those named below. Its findings:
- M1: TC-W21 swapped a link in at the source between steps 2 and 3. With the base flag
  `O_NOFOLLOW` of step 3 the open refuses first, so the test could not reach the identity check;
- m1: a refusal at step 9 had three conflicting sources for its message;
- m2: the tries of the archive's removal checked the source once, so a removal of the source
  during them could leave no name;
- m3: R5.4, UC-1 alternative 2b and D16 claimed a refusal for every link written with `\`;
- m4: `.agent/tools/test_rebase_links.py:209@6f3d65c` compares `denotes_old` with a path of the
  platform, which R5.3 changes;
- m5: D7 bullet 5 named step 7 where step 6 refuses;
- m6: TC-W23 had no string to find for each window of D7;
- m7: D18 misplaced N1;
- N1: two rules of the user run `task_id_tool.py` by an absolute path in a sibling checkout. The
  orchestrator confirmed that its `.agent/tools` reaches this repository's through two links;
- N2, N3: when the opens of R2.2 run under TC-W24, and a stand-in of `ntpath` per module.

Before the task: `archive_protocol.py` has no Windows analysis (LOW); TASK §9 now names it.

The orchestrator applies every finding in revision 3 (TASK D19).

### Round 3 — TASK revision 3: PASS

The same reviewer, resumed, read the TASK at SHA-256 `170dfff5dde3…` and wrote nothing. The
fingerprint was `3bd00d30b183` before and after the round. Each fix of round 2 is correct, and a
read of the whole TASK found no new contradiction. Its findings, none blocking:
- m1: between steps 8 and 9 no descriptor held the source's inode, and a replacement made by an
  unlink and a create can receive the freed number on ext4 or FAT. TC-W6, TC-W7 and TC-W21 could
  then pass on macOS and fail on Ubuntu;
- m2: R1.4 step 9 named one message, and R1.5 four;
- N1: no message for tries of the archive's removal that a failed check of the source ends;
- N2: R5.4 left out `ACCIDENTAL_RESOLVE` and `ESCAPES_ROOT`;
- N3: the settings of the sibling checkout name no script of the chain;
- N4: the loop is at its bound, and the minor findings need no fourth round.

Revision 4 applies m1, m2, N1 and N2 without a further round (TASK D20), as TASK 127 revision 3 did.
The source's descriptor stays open through step 9, and each replacement of the three tests is made
by `os.replace`. D7 gains RW10.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: FAIL

The reviewer, a `plan-reviewer` agent with no shell, read the PLAN at SHA-256 `34f41acfb517…`
against the TASK at `36930e621c7a…`, and wrote nothing. The fingerprint was `653a4a9897aa` before
and after the round; the run's tools of `tools-131/` were written in the scratchpad meanwhile, and
the read of B1 ran as a read-only agent. Its findings:
- M1: no stub step and no green step for the staged scripts before the patch;
- M2: TC-W8, TC-W12, TC-W27 and the inbound case of TC-W13 had no mutation, and the case of R1.4 of
  TC-W24 had no module;
- M3: several mutations could not be killed by the test named, as each later check refused with the
  same outcome; two mutations held two edits; the kill criterion and a survivor's path were not
  stated;
- M4: the bare pytest from `.agent/` reaches the test modules of `.agent/tools/`, and no check ran
  it;
- M5: the live-state guard of TASK R9.3 was absent;
- M6: the read of TASK R6.7 missed the new tests;
- M7: J3 counted every non-zero exit as a failed gate, though three of its commands exit non-zero
  by design;
- m1 to m10:
  - the options that J3 covered;
  - the rules that reach any code, and the files that local and user rules run;
  - the red set of B2 and B3;
  - the class of the new tests of `tests/test_script_guards.py`;
  - the diff in the audit record;
  - the modes of the staged copies;
  - the check of the calls of Python 3.11;
  - a wrong citation in §4, and the checks of TASK A2 and R8.4;
  - the schedule status, the coverage anchor and the use-case table;
  - the full paths of the tools;
- N1 to N5, notes: `System/Docs/ORCHESTRATOR.md:327@6f3d65c`, the copy of F1, the branch `_move`
  under its rule, the estimates of B and C, and the conditional declaration.

Before the task:
- MEDIUM: three rules can run any code with no prompt: the local rule `881e39b164a5`, and the user
  rules `89216e2cf097` and `aa8ebef8166f`;
- LOW: rules of the user and the local settings let an agent discard or stage the run's edits
  through `git checkout`, `git restore` and `git add`. The committed deny rules cover `stash`,
  `reset --hard` and `clean`;
- LOW: `task_id_tool.py` keeps its own directory on `sys.path` (WI-39), and two user rules run it
  through the sibling checkout's links.

Revision 2 of the PLAN applies M1 to M7, m1 to m10 and N1 to N4. N5 needs no change.

### The read of PLAN B1, during the freeze of round 2

A read-only agent read each test of the step of TASK R7.1 for an assumption of POSIX, and wrote
nothing. TASK revision 5 states its results (R6.5, R6.6, R10, D21, D22). By module:
- `tests/test_archive_move.py`: nine tests patch the internals of `_move` (`os.link`, `os.unlink`
  and `os.stat` by name): TC-A11 of the racer, TC-A13, TC-A15 to TC-A17, TC-A19 and TC-A21 to
  TC-A23. They skip where `_supported()` returns false. Four need a symbolic link. TC-A14 meets
  another error class on Windows, which R1.7 refuses;
- `tests/test_script_guards.py`:
  - TC-G15 assumes a `..` resolved after the link;
  - TC-G16, TC-G17 and the swap case of TC-G19 assert the refusal text of `O_NOFOLLOW`;
  - TC-G21 replaces a file while a descriptor holds it, and TC-G22 reads `os.O_NOFOLLOW`;
  - TC-G30 and TC-G31 create names that NTFS refuses; TC-G25 to TC-G27 skip already;
  - TC-G11 plants built-in modules of Windows and not `fcntl`. Six tests need a symbolic link;
- `.agent/tools/test_rebase_links.py`: line 209 (TASK R6.6); TC-F5 skips on Windows, though it
  could run there;
- `.agent/tools/test_slot_links.py`:
  - TC-7 reads `§` in the locale encoding;
  - TC-21 writes hooks with CR LF and paths with `\`;
  - the test of the platform deletes `os.O_NOFOLLOW`; TC-26 and TC-45 need a FIFO;
  - TC-27 replaces a file while a descriptor holds it; TC-31 names a file with a line break;
  - TC-37 and TC-43 rely on permission bits. Five tests need a symbolic link;
- `.agent/tools/test_archive_protocol.py`: six tests write Cyrillic in the locale encoding, and
  `archive_protocol.py` reads and writes the TASK in it (lines 400, 440, 487 and 491);
- `.agent/tools/test_task_id_tool.py`: `_write` of `TestSubTaskByH1` writes dashes in the locale
  encoding, which fails six cases; two tests need a FIFO.

Cross-cutting: `write_text` writes CR LF on Windows, and `read_text` hides it; the runner's locale
encoding is cp1252; `test_slot_links.py` isolates its repositories from the runner's git
configuration. The identity of `os.stat` and of `os.fstat` should agree on NTFS; no run here
checks it.

### Round 2 — PLAN revision 2: FAIL

The same reviewer, resumed, read the PLAN at SHA-256 `418a738e0b2a…` and wrote nothing. The
fingerprint was `b55e4041fe9c` before and after the round. Each fix of round 1 holds. Its findings:
- M1: mutation 39 dropped one of two checks that give the same refusal, so no test could kill it;
- M2: a bare pytest from `.agent/` exits 2 at the base. The orchestrator measured it: 21 errors of
  collection, as packages of `scripts/tests` under `.agent/skills/` share the name `tests`. It
  still collects the 257 tests of `.agent/tools/`, and runs none;
- m1: the record of the tag case of TC-W19 at `_read` is `UNREADABLE`;
- m2: the local rule `ca2c33383ded` runs the scripts through test modules;
- m3: C4 did not run `tests/test_script_guards.py`, which runs `slot_links.py`;
- m4: D1 was missing from the live-state guard;
- m5: the copy of F1 outside version control;
- N1: one helper holds the checks of both opens of `slot_links.py`;
- N2: TC-W9 is red at the base.

Before the task: LOW, a bare pytest from `.agent/` fails its collection at the base. The
listing of `list_tests131.py` records 21 errors, list hash `603e9eeebec7`.

PLAN revision 3 applies M1, M2, m1 to m5, N1 and N2, and the read of B1.

### Round 3 — PLAN revision 3: PASS

The same reviewer, resumed, read the PLAN at SHA-256 `4478180c2b73…` and the TASK at
`e63b71c089ce…`, and wrote nothing. The fingerprint was `ca4bba349536` before and after the round.
Each fix of round 2 holds, and the additions of TASK revision 5 are consistent and testable: TC-W28
and its mutations 43 and 54 are killable on macOS. Its footer named three checks that the brief
did not carry. The orchestrator then ran them on revision 3: `plan_gantt.py --check` exit 0,
`scan_register.py` 0 warn on the PLAN and the TASK, `check_positional_refs.py --all` exit 0. Its
findings, none blocking:
- m1: C7 ran the in-place TC-W28 before D5, and no step recorded its red run;
- m2: two clauses of J3 met on an unexpected exit of other code;
- m3: the swaps of TC-W6 between steps 8 and 9 meet the open descriptor of the source on Windows,
  which grants no `FILE_SHARE_DELETE`;
- m4: D3 stated no content of v3.50.0 for R10;
- N1: the operator should hear of R10 before I1. The orchestrator named D21 to the operator in its
  message after round 2;
- N2: TC-W28 runs in a temporary root;
- N3 to N5: the reach of `ca2c33383ded`, the early tick of B1, and the wording of TASK A13.

TASK revision 6 applies m3 and N2 (TASK D23); PLAN revision 4 applies m1, m2, m4, N1 and N5, with
no further round, as TASK 127 and TASK 130 did after a pass.

## Execution (§3)

### A1, A2 — the base check and the settings

- `HEAD` equals the base. Each of the 17 edited paths passes `git ls-files --error-unmatch`; each
  of the 10 created paths gives `git check-ignore -q` exit 1 and does not exist; every path
  matches `[A-Za-z0-9._/-]+`, with no `.git` or `..` segment and no leading `/`.
- `git worktree list` names the main worktree and two prunable registrations of earlier sessions,
  a finding before the task.
- Removed from the scratchpad: `briefs-130/`, `logs-130/`, `tools-130/`, the empty `wt-130/`, and
  `m131/`, the roots of the measurements of TASK §8.
- `rules_check.py compare`: `local: file unchanged; 0 new rule(s)`, `user: file unchanged; 0 new
  rule(s)`.
- Files of the change that a local or a user rule runs:
  - `.agent/tools/task_id_tool.py`, by the local rules `bcddea47eb1b` and `20890709883a` and the
    user rules `f23abd494daf` and `0b6b1d85891c`;
  - the modules of `tests/` and, through them, the four scripts and `archive_protocol.py`, by the
    local rule `ca2c33383ded`.
- Before the task: the local rule `881e39b164a5` and the user rules `89216e2cf097` and
  `aa8ebef8166f` can reach any code; no finite check covers them.

### B2, B3 — the tests first

The live-state guard of the PLAN, `guard131.sh`, listed `.agent/sessions/` before and after each
run below: unchanged each time.
- B3, on the live tree: `tests/test_session_state_contract.py`, 1 failed and 8 passed. TC-C8 passes;
  TC-C9 fails, since the workflow holds no step of TASK R7.1 yet. A first run of the module had
  no guard listing; the run above repeats it.
- B2, on the live tree: `.agent/tools/test_archive_protocol.py`, 1 failed and 56 passed. TC-W28
  fails with `UnicodeDecodeError: 'ascii' codec can't decode byte 0xd0` in `archive_task`.
- B2, in the red tree of `wt131.sh red`: the five staged test modules under their final names,
  60 failed, 265 passed, 8 skipped. With `-rA`, each of the 48 new and changed tests is red: 44
  fail, and TC-W1, TC-W2 of the tags, TC-W18 and TC-W26 fail in their subtests. They include the
  changed TC-G22 and `test_platform_without_o_nofollow_refuses`, and TC-W9 and the file-mode case
  of TC-W13, since the base exits 2 on their branch. The 8 skipped tests are those of Windows
  only. Every test of the base passes. The red tree was removed.

### C1 to C7 — the staged scripts

Each step ran in a dev tree of `wt131.sh dev`, built anew and removed at its end, under the guard:
`.agent/sessions/` unchanged each time.
- C1, the stubs: `_move_by_path`, `_is_link`, `_open_nofollow`, `_leaves_tree` and `_emit` keep the
  base behaviour. The tests of the base pass. The TC-W tests of new behaviour fail, but TC-W10 and
  TC-W26, which test no new behaviour. `archive_move.py` with no operand exits 2.
- C2, `archive_move.py`: `tests/test_archive_move.py`, 53 passed and 3 skipped, the tests of
  Windows only.
- C3, `rebase_links.py`: the first run failed one test of the base. TC-F3 of TASK 116 pinned the
  traceback on an operand that is not UTF-8, which R3.3 replaces by a refusal. The staged module
  changes it to `test_f3_a_non_utf8_operand_is_refused`, and TASK revision 7 names it in R6.6. The
  second run: `tests/test_script_guards.py` and `.agent/tools/test_rebase_links.py`, 97 passed and 4
  skipped.
- C4, `slot_links.py` and `task_id_tool.py`: the first run failed TC-W24 of the inbound mode, which
  counted two opens of a sub-task. `task_id_tool._first_h1` opens it a third time, with `O_BINARY`.
  The test now asserts each open, a write among them. The second run: 260 passed, 5 skipped, and
  TC-W28 red until D5.
- C5: each staged file parses with `feature_version=(3, 11)`. The calls that the change adds:
  - `os.lstat`, `os.fstat`, `os.open`, `os.mkdir`, `os.rmdir`, `os.unlink`, `os.fsync`,
    `os.path.splitdrive` and `time.sleep`, in Python before 3.0;
  - `os.path.commonpath` and the `stat.FILE_ATTRIBUTE_*` constants, Python 3.5;
  - `st_file_attributes`, Python 3.5 on Windows; `st_reparse_tag`, Python 3.8 on Windows;
  - `sys.pycache_prefix` and the assignment expression, Python 3.8.

  None needs Python 3.12 or later.
- C6, the read of the new and changed tests: one assumption of POSIX. TC-W24 of the inbound mode
  compared `os.path.abspath` of the open with `os.path.join` of the root and a path with `/`, which
  mixes separators on Windows. It now compares both through `os.path.abspath`. Each other test
  meets its platform: the symbolic links behind a probe, the junctions, held files and read-only
  sources of Windows only, the `\\?\` paths of TC-W16, and TC-W6 with the protection of TASK D23.
- C7, the whole step of TASK R7.1: 362 passed, 8 skipped, the tests of Windows only, and TC-W28 red
  until D5.

### D1 to D5 — in place

- D1: the step `Run the archive-chain tests` in both Windows jobs. Under the guard,
  `tests/test_session_state_contract.py`, `tests/test_ci_action_pins.py` and
  `tests/test_python_floor.py`: 35 passed, TC-C8 and TC-C9 among them.
- D2: the paragraph on archiving of `docs/ARCHITECTURE.md`. `regcheck.py`: 0 warn, and one info on
  the changed line.
- D3: v3.50.0 in `CHANGELOG.md` and `CHANGELOG.ru.md`; `regcheck.py` 0 warn, 0 info.
- D4: the progress note of the WI-39 record; `regcheck.py` 0 warn, 0 info.
- D5: the four calls of `archive_protocol.py`. Under the guard, `.agent/tools/test_archive_protocol.py`
  on the live tree: 57 passed, TC-W28 among them.

### E1 — the patch

`wt131.sh gen` wrote `docs/reviews/framework-audit-131-stage3.diff`: nine files, each final file of
TASK R9.1 with the bytes of its staged copy, no other path and no staged copy. `git apply --check`
passes on the live tree, and `git worktree list` names no worktree of the run. F1 changed TC-W7
after a first pass (below), so E1 ran again; the values here are those of the second run.

The patch: SHA-256 `a3ee95e85c1b7cedbdf5ec24b420a2e16e052653542be5df9b82bf336c013419`. Each
file that it edits, before the edit and after it, the second value the SHA-256 of its staged
copy; each file and each copy has the mode `644`:

| File | Before | After |
| :--- | :--- | :--- |
| `.agent/tools/archive_move.py` | `885e05e3a4f91e2b…` | `0fd37d0f2d32f179…` |
| `.agent/tools/rebase_links.py` | `234f5fbf9dc6cc38…` | `4876684b1484415c…` |
| `.agent/tools/slot_links.py` | `2e5ffe0ee7e64725…` | `5454c3ae5bd70a15…` |
| `.agent/tools/task_id_tool.py` | `567b040834405ad0…` | `7184d812b6b696a4…` |
| `.agent/tools/test_rebase_links.py` | `28c6f1a117743533…` | `44f2c0f6c9bfd82d…` |
| `.agent/tools/test_slot_links.py` | `783248ed6a5cdbb2…` | `9508d7e1d9b32f66…` |
| `.agent/tools/test_task_id_tool.py` | `85b5eb94145c625a…` | `9619663ce9201de9…` |
| `tests/test_archive_move.py` | `d392f306a66c5396…` | `87837f952401c8c6…` |
| `tests/test_script_guards.py` | `ae753f55a8dc8f34…` | `ad0af6e151ff752a…` |

### H1, H2 — the live and the patched tree

Each run below ran under the guard; `.agent/sessions/` was unchanged each time.
- H1, the live tree:
  - `gates.py`, 22 of 22 steps pass. The step of TASK R7.1 runs the base scripts and the base tests
    in place: 315 passed, TC-W28 among them;
  - the nine final files and the texts of `skill-archive-task` and `skill-safe-commands` equal the
    base;
  - `list_tests131.py`: no listing names a staged file. Each exits 0, but the one from `.agent/`. That
    one exits 2 with the 21 errors of the base, list hash `603e9eeebec7`, and names the tests of
    `.agent/tools/`;
  - `regcheck.py`: 0 warn on each changed document. `bytescan.py`: each changed and created file is
    clean. Each of the 23 paths of `git status` is declared.
- H2, the patched tree: `gates.py`, 22 of 22 steps pass. The curated suite and the tooling step run
  the new `tests/test_archive_move.py` and `tests/test_script_guards.py`: 602 passed, 3 skipped.
  The step of TASK R7.1: 363 passed and 8 skipped, the tests of Windows only, against 314 tests at
  the base. Each final file equals its staged copy, and `slot_links.py` holds no `or the platform`.
  The listings are those of H1, with 43 more tests.
- H2, the modes on the archive of TASK 130, with no stand-in and with the stand-in of Windows. The
  stand-in empties `os.supports_dir_fd` and deletes `os.O_NOFOLLOW`. The file mode with `--dry-run`
  exits 0, `0 rewritten`. The inbound mode with `--dry-run` exits 3 with the two `INBOUND` records
  of §1.
- H2, the chain end to end under the stand-in, in a temporary git repository: Steps 5, 5.5, 7.6,
  7.6.5 and 8 each exit 0. The moves report `"method": "copy"`, the archive keeps its CR LF and
  its byte `0x1A`, each slot link is rewritten, and Step 8 re-targets the sub-task's link.

### F1 — the mutations

`mutations131.json` holds 54 mutations, each edit an exact text that occurs once. A first pass in
the patched tree of H2 killed 49. Mutation 13 survived: TC-W7 held the unlink failing 10 times, so
a try with no check of step 9 ended as one with it. B2 then made the test fail twice only, red at
the base, and E1, H1 and H2 ran again. The pass of F1, in a new patched tree:
- 50 killed, mutations 1 to 49 and 54;
- mutations 50 to 53, marked `W`, not killed on macOS: each drops `O_BINARY`, which only Windows
  reads. TC-W24 kills the same edits on macOS as mutations 22, 23, 26 and 48; TC-W9 and TC-W13
  read the bytes on Windows, after the push (TASK A11);
- the fingerprint of the live tree, `9e27cc15c408`, is the same before and after the pass.

The table of the PLAN gives mutation 38 to `slot_links.py`: that module reads its link check from
`rebase_links` in the mutation, and TC-W26 kills it.

### G1 — the check of what runs

`check.py` listed the repository before and after each command, ignored files and `.git` included,
with `PYTHONDONTWRITEBYTECODE=1` and `PYTEST_ADDOPTS=-p no:cacheprovider`. Each pair of listings is
equal, 5749 entries, and the guard listed `.agent/sessions/` unchanged:
- `68c87931dedb` and `e97c6d7e4fe6` from the root and from `tests/`: exit 0, 745 passed each;
- the same two from `.agent/`: exit 2, `21 errors` of collection, the finding before the task of H1;
- the same two from `.agent/tools/`: exit 0, 258 passed each, TC-W28 among them;
- `ca2c33383ded` from the root: exit 0;
- `a8ddacaa1aa9` from the root: exit 0.

Until stage 3 the rules of the scripts run the base files; J3 runs them after it.

## Stage 2 (PLAN I1)

### Round 1, at the fingerprint `c846c559e729`: code review CHANGES REQUESTED, security audit PASS

Both reviewers read their brief, computed `c846c559e729` at their start and at their end, and ran
the new code in the patched tree `wt-131/i1`, which the orchestrator removed after the round. The
scratchpad held no file of a reviewer afterwards, and the fingerprint was unchanged.

The `code-reviewer`: CHANGES REQUESTED. It confirmed each hash of E1 and the 363 passed tests of
the step in the patched tree. Its findings:
- CR1-F1, HIGH: `ArchiveTestCase.write` writes `text` with `write_text` and no `newline`, so on
  Windows the fixtures hold CR LF. Twelve new tests compare bytes with `b"# task\n"` and fail on
  both Windows jobs. The read of C6 missed it; the read of B1 had named the cause;
- CR1-F2, MEDIUM: the Windows case of TC-W2 registers two removals of junctions, and the second
  meets a path whose parent the first removed;
- CR1-F3, MEDIUM: the masks of `rebase_links.py` close no fence on a line that ends in CR LF, and
  read no blank line of CR LF in a code span. A link after the first fence of a CR LF document is
  neither rebased at Steps 5.5 and 7.6.5 nor seen at Step 8, with exit 0. Base code, which the
  change makes run on Windows, where `core.autocrlf=true` is the default;
- CR1-F4, MEDIUM, measured: six mutations of `_move_by_path` survive every test:
  - the hard-link check of step 3, and the check of `docs` and of the destination at step 7;
  - the identity check of the undo, and its tries;
  - the four messages after a failed step 10;
- CR1-F5, LOW: the message when the archive's removal fails too differs from the base's;
- CR1-F6, LOW: the open of R2.2 drops `O_NONBLOCK`, and opens before it checks the kind of file;
- CR1-F7, CR1-F8, LOW: the wording of R6.6 for TC-G22, and of TC-W25 for Windows;
- CR1-F9, LOW: TC-G20 makes a hard link to a file that a descriptor holds;
- CR1-F10, LOW, style: a class after `if __name__`, the order of imports, blank lines, a redundant
  `except`;
- CR1-F11, LOW: on Windows `/proc/self/fd` names a path on the current drive.

The `security-auditor`: PASS. Its scan ran, `scan_status: findings`, with none at CRITICAL or HIGH
in the files of the change. The probes ran in its own temporary directories, since removed. Its
findings in scope, each LOW:
- SA1-F1: the undo removes the archive and the created directory by path, after their checks; a
  link swapped in at `docs` or the destination directory between the two reaches another file. No
  window of D7 names it;
- SA1-F2: as CR1-F6; under the stand-in a FIFO blocked the open of the file mode;
- SA1-F3: on Windows `_descriptor_path` imports `fcntl`, which Windows lacks, so the import searches
  every entry of `sys.path`;
- SA1-F4: an operand such as `docs/a.md:b.md` names an alternate stream of NTFS;
- SA1-F5: the copy of the move by path carries no DACL and no encryption of the source;
- SA1-F6: another process can write the source between steps 3 and 9;
- SA1-F7: the stated outcomes of RW1 and RW2;
- SA1-F8: `_dir_link` lets the walk enter a directory whose `lstat` fails;
- SA1-F9: the tests make a junction through `cmd.exe`.

Before the task:
- MEDIUM: `rebase_links.py --repo-root` and `task_id_tool.py --tasks-dir` open a UNC path that an
  argument names. On Windows that sends the user's NTLM credentials to the host;
- LOW: the file mode prints control characters unescaped; the letter case of slot paths; WI-39 for
  `task_id_tool.py`.

The operator chose to fix CR1-F3 and the UNC paths in this task: answers "Чинить в TASK 131
(Recommended)" to both (TASK D24, D25). The fix of round 1 applies every finding above (TASK D26).

### The fix of round 1

TASK revision 8 and PLAN revision 6 state the fix. Each run below ran under the guard, with
`.agent/sessions/` unchanged:
- the tests first. The staged test modules gained TC-W29 to TC-W42, the fixtures of LF bytes, the
  cleanup of TC-W2, the junctions through `_winapi.CreateJunction`, the order of the imports, and
  the class of TC-W24 of `task_id_tool` above `if __name__`. TC-W25, TC-G22 and the platform test
  of `slot_links` changed in their wording in the TASK only;
- against the staged scripts of round 1, in a dev tree, the tests of new behaviour failed: TC-W23,
  TC-W24 of `O_NONBLOCK`, TC-W30, the message of TC-W33, TC-W34 to TC-W42. TC-W29, TC-W31, TC-W32
  and the other cases of TC-W33 passed: they pin guards that round 1 already held, and kill the
  mutations that survived it (CR1-F4). A first run of that dev tree hung: TC-W37 opened a FIFO with
  no `O_NONBLOCK`, the defect of SA1-F2. The run was stopped, no process stayed, and the guard
  listed `.agent/sessions/` unchanged. TC-W37 then refuses the open in its spy, so it fails and
  never blocks;
- the staged scripts:
  - R1.4 steps 2 and 9, and the undo of R1.5 with its checks of the directories and the message of
    the base; RW11 in the docstring;
  - the open of R2.2 with its check of the kind and `O_NONBLOCK`; `_descriptor_path` on POSIX
    only; the walk of R2.5; R5.5, R11 and R12.

  The first run failed TC-W5, which expected the undo to remove a file through a link that the new R1.5
  keeps; TC-W5 and TC-W30 now state that the archive stays (RW2). The second run, in a new dev
  tree: 387 passed, 10 skipped;
- TASK §1 gained items 13 and 14; `docs/ARCHITECTURE.md` and both changelogs state R11, R12 and
  the access rules of the archive. `regcheck.py`: 0 warn on each changed document;
- the table of F1 gained mutations 55 to 76, and 69b, 73b and 74b, for the call sites of R5.5 and
  R12. Its edits of mutations 10, 14, 15, 19, 20, 26, 38, 44, 48, 52 and 53 follow the new code.
  TC-W39 gained a check of the call of `_names_stream` in `_refuse_operand`.
- F1 of the fix, first pass: 73 of 79 killed. Mutation 11 survived: the undo now checks the
  source before it removes the archive, so a refusal at step 9 that reached the undo kept the
  archive too, with a second clause in its message. TC-W6 then compares the whole message, and
  kills it.

The patch after the fix: SHA-256 `2aeb7f3be8674c10ea9aa690fa6cac15ff806f53626687ed7293f3e00a047e8b`.
Each file that it edits, before the edit and after it, the second value the SHA-256 of its staged
copy; each file and each copy has the mode `644`:

| File | Before | After |
| :--- | :--- | :--- |
| `.agent/tools/archive_move.py` | `885e05e3a4f91e2b…` | `4d9b163f8e3198c5…` |
| `.agent/tools/rebase_links.py` | `234f5fbf9dc6cc38…` | `e51670c21509e2cc…` |
| `.agent/tools/slot_links.py` | `2e5ffe0ee7e64725…` | `2bcd61a06aa1178a…` |
| `.agent/tools/task_id_tool.py` | `567b040834405ad0…` | `ba6977e7179aa81e…` |
| `.agent/tools/test_rebase_links.py` | `28c6f1a117743533…` | `44f2c0f6c9bfd82d…` |
| `.agent/tools/test_slot_links.py` | `783248ed6a5cdbb2…` | `bf61c79dcc668277…` |
| `.agent/tools/test_task_id_tool.py` | `85b5eb94145c625a…` | `c556d456ba1d2a06…` |
| `tests/test_archive_move.py` | `d392f306a66c5396…` | `cd1a77434b31c89a…` |
| `tests/test_script_guards.py` | `ae753f55a8dc8f34…` | `b41085017fdc0582…` |

The checks of the fix, each under the guard, with `.agent/sessions/` unchanged:
- H1: `gates.py` on the live tree, 22 of 22 steps pass. The nine final files and the two skills
  equal the base. `list_tests131.py` gives the listings of before, with the 21 errors from
  `.agent/` and no staged file. `regcheck.py` 0 warn; `bytescan.py` clean; 23 paths, each declared;
- H2: `gates.py` on the patched tree, 22 of 22 steps pass. The step of TASK R7.1: 383 passed and 10
  skipped. Each final file equals its staged copy. The modes on the archive of TASK 130, with no
  stand-in and with the stand-in of Windows: the file mode exits 0, the inbound mode 3 with the
  two records. The chain end to end under the stand-in, on CR LF documents with fences: Steps 5
  to 8 exit 0, and each link after a fence is rebased or re-targeted;
- F1, in a new patched tree: 74 of 79 killed. Mutations 50 to 53 and 74b are killed only by tests
  that run on Windows. The fingerprint of the live tree, `b0045fcf3777`, is the same before and
  after;
- G1: the ten commands of the check of what runs, each pair of listings equal, 5751 entries; the
  exit codes those of the first pass.

### Round 2, at the fingerprint `6a0fe9cc5490`: code review CHANGES REQUESTED, security audit PASS

Both reviewers read their brief, computed `6a0fe9cc5490` at their start and at their end, and ran
the new code in the patched tree `wt-131/i2`, which the orchestrator removed after the round. The
scratchpad held no file of a reviewer afterwards, and the fingerprint was unchanged.

The `code-reviewer`: CHANGES REQUESTED. It confirmed each hash of E1 and each fix of round 1. The
step of TASK R7.1 in `i2`: 383 passed and 10 skipped, also under its emulation of the line ends
that `write_text` gives on Windows. Its findings:
- R2-F1, HIGH: three assertions of TC-W39 and TC-W42 call `_names_stream` and `_unc` with the real
  `os`. On Windows `os.path` is `ntpath`, so each returns true, and the three tests fail on both
  Windows jobs;
- R2-F2, HIGH: TC-W31 renames the destination while the run's descriptor holds it. On Windows the
  rename fails with `PermissionError` out of the hook, and the test fails;
- R2-F3, MEDIUM: TC-W30 renames `docs` while the source's descriptor holds a file in it, with the
  same outcome on Windows;
- R2-F4, MEDIUM: `_unc` reads the drive that `splitdrive` gives, and it gives none for
  `\??\UNC\host\share`. It is R2-1 below;
- R2-F5, LOW: on Windows the time of the last write may lag while the writer's handle stays open,
  and FAT keeps it in steps of 2 seconds. D7 does not name it;
- R2-F6, LOW, measured: no test fails when the checks of the directories before the removal of the
  created directory are removed;
- R2-F7, LOW: the documents. Both changelogs name `RW1` to `RW10`. R6.4 names `mklink`.
  `docs/ARCHITECTURE.md` omits the encrypted source. The changelogs state no access rules of the
  archive, which the record of the fix of round 1 above says they do. R5.5 stands before R5.4;
- R2-F8, LOW: the inbound TC-W41 has no link before the fence and no code span;
- R2-F9, LOW, style: blank lines;
- carried from round 1, LOW, confidence 0.2: TC-G20 makes a hard link to a file that a descriptor
  holds. The reviewer expects `CreateHardLinkW` to succeed there; no change.

The `security-auditor`: PASS. Its scan ran, `scan_status: findings`, with none at CRITICAL or HIGH
in the files of the change. Its probes ran in its own temporary directories, since removed, and
confirmed each fix of round 1. Its findings:
- R2-1, MEDIUM: the refusal of R12 can be bypassed. `splitdrive` gives no drive for
  `\??\UNC\host\share` on any version; by the auditor's reading it gives none on 3.11 for
  `\\host\\share`, `\\\host\share` and `\\host` either. `task_id_tool.py` then reaches
  `os.path.exists` and `os.makedirs` with that value. The changelogs' claim that no UNC path reaches
  the file system does not hold;
- R2-2, LOW, reproduced: the tries of step 10 check no size and no time. A write between two tries
  is lost, and the move exits 0;
- R2-3, LOW: the undo checks the archive once, before its tries;
- R2-4, LOW: the undo keeps a file of step 6 with no word of it in the message. D7 names no link
  that stays in place through step 7;
- R2-5, LOW: `docs/ARCHITECTURE.md` and the changelogs do not name the encrypted source.

Before the task, each LOW: `task_id_tool.py --tasks-dir` creates its directory at any path that
the argument names; the control characters of round 1; the letter case of slot paths (TASK §9);
WI-39 for `task_id_tool.py`.

The fix of round 2 applies every finding of the round in the run (TASK D28).

### The fix of round 2

TASK revision 9 and PLAN revision 7 state the fix. Each run below ran under the guard, with
`.agent/sessions/` unchanged:
- the tests first. TC-W30 and TC-W31 assert on Windows the outcome of a rename that a descriptor
  of the run refuses (D28). TC-W31 asserts the whole message. TC-W39 and TC-W42 assert the result
  on POSIX with `posixpath`, and TC-W42 tests nine forms. The inbound TC-W41 gained a link before
  the fence and a code span over a CR LF line of a space and a tab. TC-W43 to TC-W46 are new, and
  TC-W23 asks for twelve labels;
- against the staged scripts of round 1, in a dev tree: TC-W23, TC-W31, TC-W42 of both modules
  (the forms with `\??\`) and TC-W43 to TC-W45 failed. TC-W46 and the cases on POSIX of TC-W39 and
  TC-W42 passed: they pin guards that round 1 already holds;
- the staged scripts: `_source_check` compares the size and `st_mtime_ns` of the `lstat` of step 2,
  and the comparison of `fstat` at step 9 is gone. Each try of the undo checks the archive again,
  and `_NotOurs` gives the message of R1.5. `_unc` of both scripts reads the text. In a new dev
  tree: 388 passed, 10 skipped;
- the Windows branch of TC-W30 and TC-W31, driven once on macOS: the test module read `os.name` as
  `nt`, and each rename raised `PermissionError`. Both tests passed: the move completed with exit
  0;
- TASK D7 and the docstring of `archive_move.py`: RW2, RW11 and RW12. `docs/ARCHITECTURE.md` and
  both changelogs name the encrypted source and the forms of R12.1, and both changelogs now state
  the access rules of the archive. `regcheck.py`: 0 warn on each changed document;
- the table of F1: the edits of mutations 58, 62, 64, 73b and 74 follow the new code, and 13b,
  64b, 71b, 72b and 77 to 83, 81b and 82b are new: 92 mutations.

The patch after the fix: SHA-256 `ccb9bda77c1b57e5defd7b91d5b029e43025c5e680adcc929141fef34f6f83d2`.
Each file that it edits, before the edit and after it, the second value the SHA-256 of its staged
copy; each file and each copy has the mode `644`:

| File | Before | After |
| :--- | :--- | :--- |
| `.agent/tools/archive_move.py` | `885e05e3a4f91e2b…` | `12c576f9b4140248…` |
| `.agent/tools/rebase_links.py` | `234f5fbf9dc6cc38…` | `fb1f9bdc3c10b5e2…` |
| `.agent/tools/slot_links.py` | `2e5ffe0ee7e64725…` | `2bcd61a06aa1178a…` |
| `.agent/tools/task_id_tool.py` | `567b040834405ad0…` | `b90bf66d18acbf6e…` |
| `.agent/tools/test_rebase_links.py` | `28c6f1a117743533…` | `44f2c0f6c9bfd82d…` |
| `.agent/tools/test_slot_links.py` | `783248ed6a5cdbb2…` | `be5c85d7fc46bd2b…` |
| `.agent/tools/test_task_id_tool.py` | `85b5eb94145c625a…` | `66f4f8cd01aaf5e3…` |
| `tests/test_archive_move.py` | `d392f306a66c5396…` | `ad5be687a0044930…` |
| `tests/test_script_guards.py` | `ae753f55a8dc8f34…` | `19917f9ed80d7f0d…` |

The checks of the fix, each under the guard, with `.agent/sessions/` unchanged:
- H1: `gates.py` on the live tree, 22 of 22 steps pass. The TASK changed during that run, so
  `gates.py` ran again on the final documents: 22 of 22 steps pass. The nine final files and the two skills
  equal the base. `list_tests131.py` gives the listings of before, with the 21 errors from
  `.agent/` and no staged file. `bytescan.py` clean; 23 paths, each declared;
- H2: `gates.py` on the patched tree, 22 of 22 steps pass. The step of TASK R7.1: 388 passed and 10
  skipped. Each final file equals its staged copy. The modes on the archive of TASK 130, with no
  stand-in and with the stand-in of Windows: the file mode exits 0, the inbound mode 3 with the
  two records. The chain end to end under the stand-in, on CR LF documents with fences: Steps 5
  to 8 exit 0, and each link after a fence is rebased or re-targeted. The archive keeps its CR LF
  and its byte `0x1A`;
- F1, in a new patched tree: 87 of 92 killed. Mutations 50 to 53 and 74b are killed only by
  tests that run on Windows. The fingerprint of the live tree, `2d5d5956a162`, is the same before
  and after;
- G1: the ten commands of the check of what runs, each pair of listings equal, 5751 entries; the
  exit codes those of the first pass.

### Round 3, at the fingerprint `6fbe789dce02`: code review APPROVED, security audit PASS

Round 3 is the last of the bound. Both reviewers read their brief, computed `6fbe789dce02` at their
start and at their end, and ran the new code in the patched tree `wt-131/i3`, which the
orchestrator removed after the round. The scratchpad held no file of a reviewer afterwards, and the
fingerprint was unchanged.

The `code-reviewer`: APPROVED. It confirmed each hash of E1 and each fix of round 2. The step of
TASK R7.1 in `i3`: 388 passed and 10 skipped, also under its emulation of the line ends of Windows.
It traced both branches of TC-W30 and TC-W31, and 13 mutations of its own in a temporary copy, since
removed, each failed a test. Its findings, each LOW:
- F1: R12.1 says that the check calls no `splitdrive`; it calls it to learn whether paths have
  drives;
- F2: an archive that another process removes between the undo's last check and its unlink ends
  with the message `…, and <archive> remains (…)`, inside window RW11;
- F3, style: two blank lines in a class body of `tests/staged_script_guards.py`;
- carried from rounds 1 and 2, confidence 0.2: TC-G20.

The `security-auditor`: PASS. Its scan ran, `scan_status: findings`, with none at CRITICAL or HIGH
in the files of the change. The UNC refusal held for each of 14 hostile forms, with the `ntpath`
of 3.14 and that of 3.9 for the `splitdrive` of 3.11, and refused none of 8 harmless forms. Its
probes of R2-2, R2-3 and R2-4 each gave the outcome of the fix. Its findings, each LOW:
- R3-1: the headline of R12 in both changelogs claims more than the check of two arguments;
- R3-2, before the task: on Python for Cygwin or MSYS2 `_unc` refuses no `//host/share`.

Stage 2 closes with this round (TASK D29). TASK revision 10 corrects R12.1, the heading of R12 and
both changelogs, names F2 in RW11 and R3-2 in §9. F3 and TC-G20 stay: a change of the reviewed bytes
would need a fourth round.

## §4.5, stage 3 and stage 4 (PLAN J)

### J1 — §4.5 and the settings

- `check_positional_refs.py --targets-changed`: 0 errors, 43 warnings across 724 references in 35
  documents. Each warning is `DRIFT_SUSPECT`: a coordinate in an archived document whose target
  this change edits. With `--fix`: the same counts, and `git status` and the diff unchanged, so no
  repair touched a file.
- `rules_check.py compare` against the reading of §2.2: the local and the user settings files are
  unchanged, with no new rule, exit 0.

### J2 — stage 3

Step 1: the patch hashes to `ccb9bda77c1b57e5defd7b91d5b029e43025c5e680adcc929141fef34f6f83d2`, and each staged copy to the value of
round 3. Step 3, before the apply: each file that the patch edits hashes to its value before the
edit in E1. Each file that the patch edits, before the edit, and its staged copy, with the SHA-256
and the mode of each:

| File | SHA-256 before | Mode | Staged copy | SHA-256 | Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `.agent/tools/archive_move.py` | `885e05e3a4f91e2b24cbfdff0c632ddcea2e8683cd503e27a32aeee4f34b0ae8` | `644` | `.agent/tools/staged_archive_move.py` | `12c576f9b4140248982089b51722cdfa69b5ed2558ee778266d4496303bbd644` | `644` |
| `.agent/tools/rebase_links.py` | `234f5fbf9dc6cc382426c084923dc5988c3eea40b5742e32da0cbfe8589173c4` | `644` | `.agent/tools/staged_rebase_links.py` | `fb1f9bdc3c10b5e263f8ea5a60f9445aa73a40ce3d96ebbc276b4eca4946c925` | `644` |
| `.agent/tools/slot_links.py` | `2e5ffe0ee7e64725a57fff27d2827eceeee8f7f9690bf922e028cdbc4dec6005` | `644` | `.agent/tools/staged_slot_links.py` | `2bcd61a06aa1178ae2ee6f79c8e93397099bcc6acefea8b204eae527fd18a146` | `644` |
| `.agent/tools/task_id_tool.py` | `567b040834405ad04253025c7981b09f62e6271b34480cc3895fe15ed86615f8` | `644` | `.agent/tools/staged_task_id_tool.py` | `b90bf66d18acbf6e3d6e87e06fb0c001343c21880bd01a7cb0e6c98ef2fa400f` | `644` |
| `.agent/tools/test_rebase_links.py` | `28c6f1a1177435330149be9d9e58a8dc905dd7ebe5b179b739e91ee03fb4d263` | `644` | `.agent/tools/staged_test_rebase_links.py` | `44f2c0f6c9bfd82d6ce1183707218d3710572c754a83c180f8930df30f8c3267` | `644` |
| `.agent/tools/test_slot_links.py` | `783248ed6a5cdbb2279f90a7404ad3d2a1bcdb346a375c9bde0ee9cbd89d4680` | `644` | `.agent/tools/staged_test_slot_links.py` | `be5c85d7fc46bd2bc087a51b94df90e68f05c83af2f7ae930c604c0526cae88e` | `644` |
| `.agent/tools/test_task_id_tool.py` | `85b5eb94145c625ab1965538da2a99390ea042f2095aafae6dc6f73eb5b8eec6` | `644` | `.agent/tools/staged_test_task_id_tool.py` | `66f4f8cd01aaf5e322894fe88501cab37b1931b1c184992e8ff96ba6373fc77d` | `644` |
| `tests/test_archive_move.py` | `d392f306a66c53960412820640912addfa2a154709732d6b6e87485f6bb7985d` | `644` | `tests/staged_archive_move.py` | `ad5be687a0044930a926cdf06d708d3774171f00bc987c1d050cf16fc1ab4743` | `644` |
| `tests/test_script_guards.py` | `ae753f55a8dc8f342def9fa31ad9b48a2c8bdb7898b79aa62fa762e7f7629e69` | `644` | `tests/staged_script_guards.py` | `19917f9ed80d7f0d13723c60e8a1ca5755867e3298567848c7011ada0c2a1757` | `644` |

The patch:

~~~~diff
diff --git a/.agent/tools/archive_move.py b/.agent/tools/archive_move.py
index 59c5557..ab111a1 100644
--- a/.agent/tools/archive_move.py
+++ b/.agent/tools/archive_move.py
@@ -14,17 +14,46 @@ It accepts exactly two operand pairs, compared as text:
 `<ID>` is three or more digits and `<slug>` is lowercase words joined by `-`, the shapes
 `task_id_tool.py` produces. Run it from the project root.
 
-It works through directory descriptors: `docs` and the destination directory are opened with
-`O_DIRECTORY | O_NOFOLLOW`, and every file is named relative to them, so a link swapped in for
-either directory is refused. It refuses a source that is a link or has a second hard link, and a
-destination that exists. It holds the source open from its open to the end of the move, so a file
-swapped in under its name meanwhile cannot take its inode number. It moves by a hard link and an
-unlink, and copies into an exclusively created file where the file system refuses the hard link.
-Any failure after the destination exists removes the destination; the source stays.
+Where the platform has `dir_fd`, `_move` works through directory descriptors: `docs` and the
+destination directory are opened with `O_DIRECTORY | O_NOFOLLOW`, and every file is named relative
+to them, so a link swapped in for either directory is refused. It refuses a source that is a link
+or has a second hard link, and a destination that exists. It holds the source open from its open
+to the end of the move, so a file swapped in under its name meanwhile cannot take its inode
+number. It moves by a hard link and an unlink, and copies into an exclusively created file where
+the file system refuses the hard link. Any failure after the destination exists removes the
+destination; the source stays.
+
+Where it has none, Windows among them, `_move_by_path` moves by path (TASK 131 R1). A link is a
+symbolic link or a junction: a reparse point whose tag is a name surrogate. It refuses each case
+of `_move`, a read-only source and an encrypted one, checks each entry before and after its open,
+copies into an exclusively created file with `O_BINARY`, and holds the source open through the
+check of its step 9. An unlink or a removal that fails with `PermissionError` is tried 10 times.
+The archive is a new file: it takes the access rules of the destination directory, and no
+alternate stream of the source. These windows of a race remain, as TASK 131 D7 states:
+
+- RW1: a link swapped in at `docs` or at the destination directory after its check, and swapped
+  back between the checks of step 7; the copy, or the move of a file at the link's target, is
+  then made there;
+- RW2: the same link swapped back before step 7, or still in place at it; an empty file stays at
+  the link's target, and the error says that it is kept; a directory that step 4 made through the
+  link stays there too;
+- RW3: a link swapped in at `docs` between step 9 and step 10 or a try; step 10 removes a file at
+  the link's target;
+- RW4: an entry swapped in at the source between step 9 and step 10 or a try; step 10 removes it;
+- RW5: the source removed between its check and a try of the archive's removal;
+- RW6: a link swapped in at the destination's name between steps 5 and 6;
+- RW7: a directory swapped for a link between an open and the check of its real path;
+- RW8: a junction swapped in between the walk filter and the walk's descent;
+- RW9: a volume that reports `st_ino` 0, where an identity compares the device only;
+- RW10: a replacement that receives the source's freed inode number;
+- RW11: a link swapped in at a directory, or another file put at the archive's name, between the
+  undo's checks and its removal of an entry;
+- RW12: a write to the source that keeps its size, which Windows may not date until the writer's
+  handle closes, or which falls within the 2-second steps of FAT; the archive misses it.
 
 Exit codes: 0 moved; 1 refused, nothing changed on disk, except when the error says the archive
-was kept; 2 usage error or a platform without `dir_fd` support. Any `OSError`, such as an overlong
-name, is a refusal. One JSON object goes to stdout on success, to stderr otherwise.
+was kept; 2 usage error. Any `OSError`, such as an overlong name, is a refusal. One JSON object
+goes to stdout on success, to stderr otherwise.
 """
 import os
 import sys
@@ -55,6 +84,7 @@ import errno  # noqa: E402
 import json  # noqa: E402
 import re  # noqa: E402
 import stat  # noqa: E402
+import time  # noqa: E402
 
 USAGE = ("usage: archive_move.py docs/TASK.md docs/tasks/task-<ID>-<slug>.md\n"
          "       archive_move.py docs/PLAN.md docs/plans/plan-<ID>-<slug>.md")
@@ -68,6 +98,13 @@ PAIRS = {
 NO_HARD_LINK = {errno.EPERM, errno.EXDEV, errno.EMLINK, errno.ENOSYS,
                 getattr(errno, "ENOTSUP", errno.EPERM), getattr(errno, "EOPNOTSUPP", errno.EPERM)}
 CHUNK = 1 << 16
+#: The bit of a reparse tag that marks a name surrogate: a symbolic link or a junction (TASK 128
+#: R2.2).
+NAME_SURROGATE = 0x20000000
+#: An unlink or a removal that fails with `PermissionError` is tried this often, this many seconds
+#: apart (TASK 128 D9, TASK 131 R1.6).
+TRIES = 10
+PAUSE = 0.1
 
 
 class Refused(Exception):
@@ -88,6 +125,278 @@ def _supported():
             and hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"))
 
 
+def _is_link(st):
+    """True for a symbolic link, or a reparse point whose tag is a name surrogate (TASK 131 R1.3).
+
+    Both attributes of Windows are read with `getattr`: only Windows sets them. A junction is a
+    link; a cloud placeholder is not.
+    """
+    return stat.S_ISLNK(st.st_mode) or bool(
+        getattr(st, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
+        and getattr(st, "st_reparse_tag", 0) & NAME_SURROGATE)
+
+
+def _flags(*names):
+    """The union of each `os.O_*` flag of `names` that this platform has."""
+    value = 0
+    for name in names:
+        value |= getattr(os, name, 0)
+    return value
+
+
+def _tried(call, path, check=None):
+    """`call(path)`, tried again on `PermissionError` (TASK 131 R1.6).
+
+    At most `TRIES` tries, `PAUSE` seconds apart. `check`, when given, runs before each try after
+    the first, and a check that raises ends the tries with its error.
+    """
+    for attempt in range(TRIES):
+        if attempt and check is not None:
+            check()
+        try:
+            return call(path)
+        except PermissionError:
+            if attempt == TRIES - 1:
+                raise
+            time.sleep(PAUSE)
+
+
+def _dir_lstat(path, label):
+    """The `lstat` of directory `path`; `label` names it in a refusal. A missing one raises
+    `FileNotFoundError`."""
+    try:
+        st = os.lstat(path)
+    except FileNotFoundError:
+        raise
+    except OSError as exc:
+        raise Refused(f"cannot open {label!r}: {exc.strerror}") from exc
+    return st
+
+
+def _same_dir(path, ref):
+    """True while `path` is a directory, no link, of the identity of `ref`."""
+    try:
+        st = os.lstat(path)
+    except OSError:
+        return False
+    return stat.S_ISDIR(st.st_mode) and not _is_link(st) and _same_file(st, ref)
+
+
+def _holds(path, ref):
+    """True while `path` is the file of `ref`, no link."""
+    try:
+        st = os.lstat(path)
+    except OSError:
+        return False
+    return not _is_link(st) and _same_file(st, ref)
+
+
+class _Kept(Refused):
+    """A refusal after which the archive stays: it may be the content's last name."""
+
+
+def _source_check(source, ref, target):
+    """Step 9: the source still holds the moved file, one hard link, with the size and the time of
+    the last write of step 2 (TASK 131 R1.4, R1.5).
+
+    Raises `_Kept` when the source is gone, holds another file or cannot be checked, and
+    `Refused` when it holds the moved file with a second hard link or a write since step 2.
+    """
+    try:
+        st = os.lstat(source)
+    except FileNotFoundError as exc:
+        raise _Kept(f"{source} is gone after the copy, so {target} is kept") from exc
+    except OSError as exc:
+        raise _Kept(f"cannot confirm what {source} holds ({exc.strerror}); both it and "
+                    f"{target} are kept") from exc
+    if _is_link(st) or not _same_file(st, ref):
+        raise _Kept(f"{source} no longer holds the moved file, so {target} is kept")
+    if st.st_nlink != 1 or (st.st_size, st.st_mtime_ns) != (ref.st_size, ref.st_mtime_ns):
+        raise Refused("the source changed during the move")
+
+
+class _UnlinkFailed(Refused):
+    """Step 10 failed while the source still holds the moved file; `strerror` is its error."""
+
+    def __init__(self, source, strerror):
+        super().__init__(f"cannot remove {source}: {strerror}")
+        self.strerror = strerror
+
+
+def _unlink_source(source, ref, target):
+    """Step 10, with the tries of R1.6; the message of `_undo_after_failed_unlink` on a failure."""
+    try:
+        _tried(os.unlink, source, lambda: _source_check(source, ref, target))
+    except Refused:
+        raise
+    except OSError as exc:
+        try:
+            st = os.lstat(source)
+        except FileNotFoundError:
+            raise _Kept(f"cannot remove {source} ({exc.strerror}); it is gone, so {target} is "
+                        "kept") from exc
+        except OSError as check:
+            raise _Kept(f"cannot remove {source} ({exc.strerror}) or confirm what it holds "
+                        f"({check.strerror}); both it and {target} are kept") from exc
+        if _is_link(st) or not _same_file(st, ref):
+            raise _Kept(f"cannot remove {source} ({exc.strerror}); it no longer holds the moved "
+                        f"file, so {target} is kept") from exc
+        raise _UnlinkFailed(source, exc.strerror) from exc
+
+
+class _DirsChanged(Exception):
+    """A directory of the undo is no longer the one that steps 1 and 4 checked."""
+
+
+class _NotOurs(Exception):
+    """The archive's name no longer holds the file that step 6 made."""
+
+
+def _remove_ours(target, made, dirs, check=None):
+    """Remove this run's archive, with the tries of R1.6, through unchanged directories (R1.5).
+
+    Before the first try and before each later one, the archive is checked and raises `_NotOurs`
+    unless it holds the file of `made`; then `dirs()` raises `_DirsChanged` unless `docs` and the
+    destination directory keep their identities; then `check` runs.
+    """
+    if made is None:
+        return
+
+    def checks():
+        if not _holds(target, made):
+            raise _NotOurs()
+        dirs()
+        if check is not None:
+            check()
+    checks()
+    _tried(os.unlink, target, checks)
+
+
+def _undo(exc, message, target, made, dirs, source, ref, checked):
+    """The message of a refusal after the undo of R1.5 removed what it may remove."""
+    def source_holds():
+        if not _holds(source, ref):
+            raise _Kept("")
+    try:
+        _remove_ours(target, made, dirs, source_holds if checked else None)
+    except _NotOurs:
+        return f"{message}; {target} no longer holds the file this run made, so that file is kept"
+    except _DirsChanged:
+        return f"{message}; the destination directory changed, so {target} is kept"
+    except _Kept:
+        return f"{message}; {source} changed before {target} was removed, so {target} is kept"
+    except OSError as cleanup:
+        if isinstance(exc, _UnlinkFailed):
+            return (f"cannot remove {source} ({exc.strerror}), and {target} remains "
+                    f"({cleanup.strerror})")
+        return f"{message}, and {target} remains ({cleanup.strerror})"
+    return message
+
+
+def _move_by_path(src, subdir, dst):
+    """Move `docs/<src>` to `docs/<subdir>/<dst>` by path, where `dir_fd` is missing (R1.4).
+
+    The steps are those of TASK 131 R1.4, and the undo that of R1.5: an archive made before step 9
+    is removed while it is this run's; one checked at step 9 or 10 stays when the source is gone
+    or holds another file. A directory this run created is removed again.
+    """
+    source, directory = f"docs/{src}", f"docs/{subdir}"
+    target = f"{directory}/{dst}"
+    try:                                                    # step 1
+        docs = _dir_lstat("docs", "docs")
+    except FileNotFoundError as exc:
+        raise Refused("docs does not exist") from exc
+    if _is_link(docs) or not stat.S_ISDIR(docs.st_mode):
+        raise Refused("'docs' is a symbolic link or not a directory")
+    src_fd = dst_fd = made = sub = ref = None
+    created, checked = False, False
+    try:
+        try:                                                # step 2
+            ref = os.lstat(source)
+        except FileNotFoundError as exc:
+            raise Refused(f"{source} does not exist") from exc
+        if _is_link(ref) or not stat.S_ISREG(ref.st_mode):
+            raise Refused(f"{source} is a symbolic link or not a regular file")
+        if ref.st_nlink != 1:
+            raise Refused(f"{source} has {ref.st_nlink} hard links")
+        if getattr(ref, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_READONLY:
+            raise Refused(f"{source} is read-only")
+        if getattr(ref, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_ENCRYPTED:
+            raise Refused(f"{source} is encrypted")
+        try:                                                # step 3
+            src_fd = os.open(source, _flags("O_RDONLY", "O_NOFOLLOW", "O_NONBLOCK", "O_BINARY"))
+        except OSError as exc:
+            raise Refused(f"cannot open {source}: {exc.strerror}") from exc
+        held = os.fstat(src_fd)
+        if not (stat.S_ISREG(held.st_mode) and _same_file(held, ref) and held.st_nlink == 1):
+            raise Refused("the source changed during the move")
+        try:                                                # step 4
+            sub = _dir_lstat(directory, subdir)
+        except FileNotFoundError:
+            os.mkdir(directory)
+            created = True
+            sub = _dir_lstat(directory, subdir)
+        if _is_link(sub) or not stat.S_ISDIR(sub.st_mode):
+            raise Refused(f"{subdir!r} is a symbolic link or not a directory")
+        try:                                                # step 5
+            os.lstat(target)
+        except FileNotFoundError:
+            pass
+        else:
+            raise Refused("the destination exists")
+        flags = _flags("O_WRONLY", "O_CREAT", "O_EXCL", "O_NOFOLLOW", "O_BINARY")
+        try:                                                # step 6
+            dst_fd = os.open(target, flags, stat.S_IMODE(ref.st_mode))
+        except FileExistsError as exc:
+            raise Refused("the destination exists") from exc
+        except OSError as exc:
+            raise Refused(f"cannot create the destination: {exc.strerror}") from exc
+        made = os.fstat(dst_fd)
+        if not (_same_dir("docs", docs) and _same_dir(directory, sub)       # step 7
+                and _holds(target, made)):
+            raise Refused("the destination directory changed during the move")
+        try:                                                # step 8
+            while chunk := os.read(src_fd, CHUNK):
+                view = memoryview(chunk)
+                while view:
+                    view = view[os.write(dst_fd, view):]
+            os.fsync(dst_fd)
+        except OSError as exc:
+            raise Refused(f"cannot copy the source: {exc.strerror}") from exc
+        _close(dst_fd)
+        dst_fd = None
+        checked = True                                      # step 9
+        _source_check(source, ref, target)
+        _close(src_fd)
+        src_fd = None
+        _unlink_source(source, ref, target)                 # step 10
+    except _Kept:
+        raise
+    except (Refused, OSError) as exc:
+        _close(dst_fd)
+        dst_fd = None
+        if isinstance(exc, Refused):
+            message = str(exc)
+        else:
+            message = f"{exc.strerror or exc}: {exc.filename or ''}".rstrip(": ")
+
+        def dirs():
+            if not (_same_dir("docs", docs) and (sub is None or _same_dir(directory, sub))):
+                raise _DirsChanged()
+        message = _undo(exc, message, target, made, dirs, source, ref, checked)
+        if created:
+            try:
+                dirs()
+                _tried(os.rmdir, directory, dirs)
+            except (_DirsChanged, OSError):
+                pass
+        raise Refused(message) from exc
+    finally:
+        _close(src_fd)
+        _close(dst_fd)
+    return {"method": "copy", "created_directory": created}
+
+
 def _parse(source, destination):
     """The source name in `docs`, the destination directory and the archive name, or Refused."""
     if source not in PAIRS:
@@ -298,11 +607,10 @@ def main(argv=None):
     argv = sys.argv[1:] if argv is None else list(argv)
     if len(argv) != 2 or any(arg.startswith("-") for arg in argv):
         return _fail(2, USAGE)
-    if not _supported():
-        return _fail(2, "this platform has no dir_fd support for open, mkdir, link and unlink")
     source, destination = argv
     try:
-        result = _move(*_parse(source, destination))
+        parsed = _parse(source, destination)
+        result = _move(*parsed) if _supported() else _move_by_path(*parsed)
     except Refused as exc:
         return _fail(1, str(exc))
     print(json.dumps({"ok": True, "source": source, "destination": destination, **result}))
diff --git a/.agent/tools/rebase_links.py b/.agent/tools/rebase_links.py
index 523b982..35393f2 100644
--- a/.agent/tools/rebase_links.py
+++ b/.agent/tools/rebase_links.py
@@ -76,7 +76,9 @@ import sys
 #   and inode, match the directory of the path as called or of the real path: a case-insensitive
 #   volume reaches the directory in other letter case (ARC-13, the rule of TASK 127 R6.1);
 # - no bytecode is written, and `.pyc` files are looked up under the null device, where none can
-#   exist, so a `.pyc` planted in `__pycache__/` is never read.
+#   exist, so a `.pyc` planted in `__pycache__/` is never read. Where `os.devnull` is a relative
+#   path, `nul` on Windows, they are looked up under the script's own real path instead: a regular
+#   file holds no directory, so no `.pyc` can exist there either (TASK 131 R4).
 # The module has no `from __future__` statement: at run time it imports `__future__`.
 if __name__ == "__main__":
     def _identity(path):
@@ -95,7 +97,10 @@ if __name__ == "__main__":
                    if os.path.normcase(os.path.realpath(entry or os.curdir)) not in _NAMES
                    and _identity(entry or os.curdir) not in _IDS]
     sys.dont_write_bytecode = True
-    sys.pycache_prefix = os.path.join(os.devnull, "rebase-links-pycache")
+    if os.path.isabs(os.devnull):
+        sys.pycache_prefix = os.path.join(os.devnull, "rebase-links-pycache")
+    else:
+        sys.pycache_prefix = os.path.join(os.path.realpath(__file__), "pycache")
 
 import posixpath  # noqa: E402
 import re  # noqa: E402
@@ -105,8 +110,9 @@ from typing import NamedTuple  # noqa: E402
 #: Schemes and forms that are never document-relative.
 _ABSOLUTE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|/|#)", re.IGNORECASE)
 
-#: Fenced blocks: ``` or ~~~, any info string, closed by a fence at least as long.
-_FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*?^[ \t]{0,3}\1[ \t]*$",
+#: Fenced blocks: ``` or ~~~, any info string, closed by a fence at least as long. The closing
+#: line may end in CR LF, as Git for Windows checks a file out (TASK 131 R11.1).
+_FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*?^[ \t]{0,3}\1[ \t]*\r?$",
                     re.S | re.M)
 #: An unterminated fence: everything from the opener to end of document.
 _FENCE_OPEN = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*\Z", re.S | re.M)
@@ -117,11 +123,12 @@ _FENCE_OPEN = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*\Z", re.S | re.M)
 #:      the mask desynchronized for the rest of the file.
 #:   2. A code span cannot contain a blank line -- a blank line ends the
 #:      paragraph. Without that bound an unbalanced backtick pairs with one
-#:      hundreds of lines later and blanks every real link in between.
+#:      hundreds of lines later and blanks every real link in between. A blank
+#:      line of CR LF counts too (TASK 131 R11.2).
 #: Measured on this corpus: (1)+(2) recover 3 real links in
 #: docs/design/095_workflow_loop_contract.md that were invisible to the tool,
 #: and keep masking all 13 links that are syntax examples inside code spans.
-_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(?:[^\n]|\n(?![ \t]*\n))*?(?<!`)\1(?!`)")
+_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(?:[^\n]|\n(?![ \t]*\r?\n))*?(?<!`)\1(?!`)")
 
 # NOTE: indented code blocks are deliberately NOT masked. In this corpus a
 # 4-or-more-space indent is overwhelmingly a lazy continuation of a list item,
@@ -261,7 +268,7 @@ def rebase_document_links(text: str, from_dir: str, to_dir: str,
         denote_old = os.path.normpath(os.path.join(old_base, path))
         denote_new = os.path.normpath(os.path.join(new_base, path))
 
-        if os.path.commonpath([root, denote_old]) != root:
+        if not _inside(denote_old, root):
             records.append(LinkRecord(line, authored, denote_old,
                                       "ESCAPES_ROOT", authored))
             continue
@@ -283,7 +290,7 @@ def rebase_document_links(text: str, from_dir: str, to_dir: str,
             if raw.startswith("<"):
                 new_target = f"<{new_target}>"
             records.append(LinkRecord(line, authored,
-                                      os.path.relpath(identity, root),
+                                      os.path.relpath(identity, root).replace(os.sep, "/"),
                                       "SLOT_RESOLVED", new_target))
             edits.append((start, end, new_target))
             continue
@@ -292,13 +299,13 @@ def rebase_document_links(text: str, from_dir: str, to_dir: str,
         # the path here is what converts "dead" into "silently wrong".
         if os.path.relpath(denote_old, root) in known_slots:
             records.append(LinkRecord(line, authored,
-                                      os.path.relpath(denote_old, root),
+                                      os.path.relpath(denote_old, root).replace(os.sep, "/"),
                                       "UNMAPPED_SLOT", authored))
             continue
 
         resolved_old = os.path.exists(denote_old)
         resolved_new = os.path.exists(denote_new)
-        rel_old = os.path.relpath(denote_old, root)
+        rel_old = os.path.relpath(denote_old, root).replace(os.sep, "/")  # TASK 131 R5.3
 
         if not resolved_old:
             action = "ACCIDENTAL_RESOLVE" if resolved_new else "PRE_BROKEN"
@@ -495,8 +502,10 @@ def _refuse_operand(path):
     """
     cwd = os.getcwd()
     absolute = os.path.normpath(os.path.join(cwd, path))
-    if os.path.commonpath([absolute, cwd]) != cwd or absolute == cwd:
+    if not _inside(absolute, cwd) or absolute == cwd:
         return "lies outside the working directory"
+    if _names_stream(path):
+        return "names an alternate stream of a file"
     if _under_git(path, cwd):
         return "lies under .git/"
     if os.path.islink(path):
@@ -505,7 +514,7 @@ def _refuse_operand(path):
         return "has a second hard link"
     real_cwd = os.path.realpath(cwd)
     directory = os.path.realpath(os.path.dirname(os.path.join(cwd, path)))
-    if os.path.commonpath([directory, real_cwd]) != real_cwd:
+    if not _inside(directory, real_cwd):
         return "its directory resolves outside the working directory"
     if os.path.relpath(absolute, cwd).split(os.sep)[0] != "docs":
         return "does not lie under docs/"
@@ -518,6 +527,95 @@ class _Unsafe(Exception):
     """An operand that the file mode refuses to read or to write (TASK 116 R7)."""
 
 
+#: The bit of a reparse tag that marks a name surrogate: a symbolic link or a junction (TASK 128
+#: R2.2). Held here, not read from a sibling (TASK 131 R2.6).
+_NAME_SURROGATE = 0x20000000
+
+
+def _is_link(st):
+    """True for a symbolic link, or a reparse point whose tag is a name surrogate (TASK 131 R1.3).
+
+    Both attributes of Windows are read with `getattr`: only Windows sets them. A junction is a
+    link; a cloud placeholder is not.
+    """
+    return stat.S_ISLNK(st.st_mode) or bool(
+        getattr(st, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
+        and getattr(st, "st_reparse_tag", 0) & _NAME_SURROGATE)
+
+
+def _open_nofollow(path, flags):
+    """A descriptor of `path` opened with `flags` and no link followed (TASK 131 R2.1, R2.2).
+
+    Where `O_NOFOLLOW` exists, the open of the base. Elsewhere, Windows among them: `os.lstat`, a
+    refusal of a link or of any entry that is not a regular file, `os.open` with `O_NONBLOCK` and
+    `O_BINARY` where they exist, and `os.fstat`, which must give the identity of the `lstat`. An
+    `OSError` of the calls passes to the caller.
+    """
+    nofollow = getattr(os, "O_NOFOLLOW", None)
+    if nofollow is not None:
+        return os.open(path, flags | nofollow | getattr(os, "O_NONBLOCK", 0))
+    before = os.lstat(path)
+    if _is_link(before):
+        raise _Unsafe("is a link")
+    if not stat.S_ISREG(before.st_mode):
+        raise _Unsafe("is not a regular file")
+    fd = os.open(path, flags | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
+    try:
+        st = os.fstat(fd)
+    except BaseException:
+        os.close(fd)
+        raise
+    if (st.st_dev, st.st_ino) != (before.st_dev, before.st_ino):
+        os.close(fd)
+        raise _Unsafe("changed during the run")
+    return fd
+
+
+def _inside(path, root):
+    """True when `path` lies inside `root`; paths on two drives lie outside (TASK 131 R5.1)."""
+    try:
+        return os.path.commonpath([path, root]) == root
+    except ValueError:
+        return False
+
+
+def _leaves_tree(value):
+    """True when `--from` or `--to` leaves the working directory (TASK 116 R8.6, TASK 131 R5.2).
+
+    A value leaves it when it is absolute, has a drive, starts with a separator, or starts with
+    `..` once normalised.
+    """
+    return (os.path.isabs(value) or bool(os.path.splitdrive(value)[0])
+            or value.startswith(("/", os.sep))
+            or os.path.normpath(value).split(os.sep)[0] == "..")
+
+
+def _names_stream(path):
+    """True where paths have drives and `path` holds `:` after its drive (TASK 131 R5.5).
+
+    On NTFS such a colon names an alternate data stream of the file before it.
+    """
+    return bool(os.path.splitdrive("c:")[0]) and ":" in os.path.splitdrive(path)[1]
+
+
+def _unc(value):
+    """True where paths have drives and `value` is a UNC or device path (TASK 131 R12.1).
+
+    Such a path starts with two separators, as `\\\\host\\share`, `\\\\?\\` and `\\\\.\\` do, or
+    with `\\??\\`, as `\\??\\UNC\\host\\share` does. The check reads the text, each `/` as `\\`,
+    so it reaches no file system. It reads no drive of `value`: `splitdrive` gives none for
+    `\\??\\`.
+    """
+    text = value.replace("/", "\\")
+    return bool(os.path.splitdrive("c:")[0]) and text.startswith(("\\\\", "\\??\\"))
+
+
+def _emit(stream, line):
+    """Write `line` and a newline; text the stream cannot encode becomes backslash escapes."""
+    encoding = getattr(stream, "encoding", None) or "utf-8"
+    stream.write(line.encode(encoding, "backslashreplace").decode(encoding, "replace") + "\n")
+
+
 def _check_descriptor(fd, path, cwd):
     """The `fstat` of `fd`, if it is the regular file at `path`'s real path (TASK 116 R7.2).
 
@@ -543,7 +641,7 @@ def _check_descriptor(fd, path, cwd):
     except OSError:
         raise _Unsafe("is not the file at its real path") from None
     real_cwd = os.path.realpath(cwd)
-    if os.path.commonpath([os.path.dirname(where), real_cwd]) != real_cwd:
+    if not _inside(os.path.dirname(where), real_cwd):
         raise _Unsafe("its directory resolves outside the working directory")
     return st
 
@@ -553,8 +651,11 @@ def _descriptor_path(fd):
 
     `fcntl.F_GETPATH` gives it on darwin, and the link `/proc/self/fd/<fd>` on Linux. It is one
     lookup, so no swap of a directory between two lookups by name can change it, as one can
-    between `realpath` and `stat`. A failed lookup raises `OSError`.
+    between `realpath` and `stat`. A failed lookup raises `OSError`. Where `os.name` is not
+    `posix` it gives none: it imports no `fcntl` and reads no `/proc` (TASK 131 R2.3).
     """
+    if os.name != "posix":
+        return None
     try:
         import fcntl
     except ImportError:
@@ -568,11 +669,8 @@ def _descriptor_path(fd):
 
 def _open_checked(path, cwd, flags):
     """`(descriptor, fstat)` of `path` opened with `flags` and no link followed (TASK 116 R7.1)."""
-    nofollow = getattr(os, "O_NOFOLLOW", None)
-    if nofollow is None:
-        raise _Unsafe("this platform has no O_NOFOLLOW")
     try:
-        fd = os.open(path, flags | nofollow | getattr(os, "O_NONBLOCK", 0))
+        fd = _open_nofollow(path, flags)
     except OSError as exc:
         raise _Unsafe(f"cannot open it: {exc.strerror or exc}") from None
     try:
@@ -678,23 +776,24 @@ def _main(argv=None):
     args = ap.parse_args(argv)
 
     # TASK 116 R8.6: a rewritten link is built from these paths, so each stays in the tree.
-    if os.path.realpath(args.repo_root) != os.path.realpath(os.getcwd()):
+    # TASK 131 R12: a UNC path is refused before any call reaches the file system.
+    if _unc(args.repo_root):
+        problem = "--repo-root is a UNC or device path"
+    elif os.path.realpath(args.repo_root) != os.path.realpath(os.getcwd()):
         problem = "--repo-root is not the working directory"
     else:
         problem = next((f"{name} does not lie inside the working directory"
                         for name, value in (("--from", args.from_dir), ("--to", args.to_dir))
-                        if os.path.isabs(value)
-                        or os.path.normpath(value).split(os.sep)[0] == ".."), None)
+                        if _leaves_tree(value)), None)
     if problem:
-        print(json.dumps({"ok": False, "error": problem}), file=sys.stderr)
+        _emit(sys.stderr, json.dumps({"ok": False, "error": problem}))
         return 2
 
     slot_map = {}
     for pair in args.slot:
         if "=" not in pair:
-            print(json.dumps({"ok": False,
-                              "error": f"--slot expects SLOT=ARCHIVE, got {pair!r}"}),
-                  file=sys.stderr)
+            _emit(sys.stderr, json.dumps({"ok": False,
+                                          "error": f"--slot expects SLOT=ARCHIVE, got {pair!r}"}))
             return 2
         slot, archive = (part.strip() for part in pair.split("=", 1))
         # TASK 116 R8.1: the allow rule approves any argument, and ARCHIVE is written as a link.
@@ -706,7 +805,7 @@ def _main(argv=None):
         else:
             slot_map[slot] = archive
             continue
-        print(json.dumps({"ok": False, "error": f"--slot {pair!r}: {problem}"}), file=sys.stderr)
+        _emit(sys.stderr, json.dumps({"ok": False, "error": f"--slot {pair!r}: {problem}"}))
         return 2
 
     opened = []
@@ -724,7 +823,7 @@ def _file_mode(args, slot_map, opened):
     for path in args.files:
         reason = _refuse_operand(path) or _refuse_slot(path, slot_map)
         if reason:
-            print(json.dumps({"ok": False, "error": f"{path}: {reason}"}), file=sys.stderr)
+            _emit(sys.stderr, json.dumps({"ok": False, "error": f"{path}: {reason}"}))
             return 2
 
     # TASK 116 R7.1: every operand is open and checked before any of them is read.
@@ -733,14 +832,18 @@ def _file_mode(args, slot_map, opened):
         try:
             fd, st = _open_checked(path, cwd, os.O_RDONLY)
         except _Unsafe as exc:
-            print(json.dumps({"ok": False, "error": f"{path}: {exc}"}), file=sys.stderr)
+            _emit(sys.stderr, json.dumps({"ok": False, "error": f"{path}: {exc}"}))
             return 2
         opened.append((path, fd, st))
 
     report, warned, failed, pending = [], False, False, []
     for path, fd, st in opened:
         try:
-            text = _read_descriptor(fd).decode("utf-8")
+            try:
+                text = _read_descriptor(fd).decode("utf-8")
+            except UnicodeDecodeError:
+                _emit(sys.stderr, json.dumps({"ok": False, "error": f"{path}: is not UTF-8"}))
+                return 2
             new_text, records = rebase_document_links(text, args.from_dir, args.to_dir,
                                                       args.repo_root, slot_map)
             changed = new_text != text
@@ -748,32 +851,32 @@ def _file_mode(args, slot_map, opened):
             added = [r.line for r in records if r.action in _WROTE
                      and _adds_characters(r.authored, r.new_target)]
             if added:
-                print(json.dumps({"ok": False, "error": f"{path}:{added[0]}: a rewritten link "
-                                  "holds text that its authored link does not"}),
-                      file=sys.stderr)
+                _emit(sys.stderr, json.dumps({"ok": False, "error": f"{path}:{added[0]}: a "
+                                              "rewritten link holds text that its authored "
+                                              "link does not"}))
                 return 2
             parts = [r.line for r in records if r.action in _WROTE and _adds_parts(r)]
             if parts:
-                print(json.dumps({"ok": False, "error": f"{path}:{parts[0]}: the path of a "
-                                  "rewritten link is not a tail of its authored link's"}),
-                      file=sys.stderr)
+                _emit(sys.stderr, json.dumps({"ok": False, "error": f"{path}:{parts[0]}: the "
+                                              "path of a rewritten link is not a tail of its "
+                                              "authored link's"}))
                 return 2
             # Overlapping links are spliced one into the other: the text gains no character either.
             if _adds_characters(text, new_text):
-                print(json.dumps({"ok": False, "error": f"{path}: the rewritten text holds a "
-                                  "character that the text did not"}), file=sys.stderr)
+                _emit(sys.stderr, json.dumps({"ok": False, "error": f"{path}: the rewritten "
+                                              "text holds a character that the text did not"}))
                 return 2
             # TASK 117 R3: a splice that adds no new character still changes the length.
             if len(new_text) != len(text) + sum(len(r.new_target) - len(r.authored)
                                                 for r in records if r.action in _WROTE):
-                print(json.dumps({"ok": False, "error": f"{path}: the rewritten text is not the "
-                                  "text with each rewritten link replaced"}), file=sys.stderr)
+                _emit(sys.stderr, json.dumps({"ok": False, "error": f"{path}: the rewritten "
+                                              "text is not the text with each rewritten link "
+                                              "replaced"}))
                 return 2
             if changed and not args.dry_run:
                 _write_checked(path, cwd, st, new_text.encode("utf-8"))
         except (OSError, _Unsafe) as exc:
-            print(json.dumps({"ok": False, "error": f"{path}: {exc}"}),
-                  file=sys.stderr)
+            _emit(sys.stderr, json.dumps({"ok": False, "error": f"{path}: {exc}"}))
             return 2
 
         # Conservation law: every file denoted before the move is denoted after.
@@ -815,23 +918,23 @@ def _file_mode(args, slot_map, opened):
             warned = True
 
     if args.json:
-        print(json.dumps({"ok": not failed, "files": report,
-                          "slot_targets_pending": pending},
-                         ensure_ascii=False, indent=1))
+        _emit(sys.stdout, json.dumps({"ok": not failed, "files": report,
+                                      "slot_targets_pending": pending},
+                                     ensure_ascii=True, indent=1))
     else:
         for entry in report:
             for r in entry["links"]:
                 if r["action"] == "UNCHANGED":
                     continue
-                print(f"[{r['action']}] {entry['file']}:{r['line']}  "
+                _emit(sys.stdout, f"[{r['action']}] {entry['file']}:{r['line']}  "
                       f"{r['authored']}"
                       + (f"  ->  {r['new_target']}" if r["action"] in _WROTE
                          else ""))
         n = sum(1 for e in report for r in e["links"] if r["action"] in _WROTE)
         w = sum(1 for e in report for r in e["links"] if r["action"] in ACTIONS_WARN)
         for p in pending:
-            print(f"[SLOT_PENDING] {p}  (declared identity, not yet on disk)")
-        print(f"{n} rewritten / {w} needing review"
+            _emit(sys.stdout, f"[SLOT_PENDING] {p}  (declared identity, not yet on disk)")
+        _emit(sys.stdout, f"{n} rewritten / {w} needing review"
               + (" (dry run)" if args.dry_run else ""))
 
     if failed:
diff --git a/.agent/tools/slot_links.py b/.agent/tools/slot_links.py
index 1a4e8b4..a0e9e37 100644
--- a/.agent/tools/slot_links.py
+++ b/.agent/tools/slot_links.py
@@ -18,8 +18,11 @@ Added lines are computed here, from `git cat-file blob`, with `difflib`. No `git
 diff driver, textconv driver or clean filter runs (TASK 115 D3).
 
 Exit codes of `main`: 0 nothing listed; 1 a rewritten link does not resolve, a write failed after
-its first byte, or an unexpected error; 2 an operand, git, `<rev>` or the platform; 3 completed with
-`INBOUND`, `REFUSED`, `UNREADABLE` or `SKIPPED` records.
+its first byte, or an unexpected error; 2 an operand, git or `<rev>`; 3 completed with `INBOUND`,
+`REFUSED`, `UNREADABLE` or `SKIPPED` records.
+
+Where the platform has no `O_NOFOLLOW`, Windows among them, each open checks the path with `lstat`
+before it and the descriptor with `fstat` after it, and the walk enters no junction (TASK 131 R2).
 """
 from __future__ import annotations
 
@@ -63,7 +66,7 @@ LISTED = ("INBOUND", "REFUSED", "UNREADABLE", "SKIPPED")
 
 
 class InboundError(Exception):
-    """An operand, git, `<rev>` or the platform: nothing was written (exit 2)."""
+    """An operand, git or `<rev>`: nothing was written (exit 2)."""
 
 
 class InboundRecord(NamedTuple):
@@ -168,9 +171,22 @@ def _walk(root, unreadable):
         rel = os.path.relpath(exc.filename or root, root).replace(os.sep, "/")
         unreadable.append(InboundRecord(rel, None, "UNREADABLE", "", "", exc.strerror or str(exc)))
 
+    def entered(dirpath, name):
+        """TASK 131 R2.5: `os.walk` enters a junction; the walk enters no directory link, and no
+        directory whose `lstat` fails, which it records as unreadable."""
+        path = os.path.join(dirpath, name)
+        try:
+            return not _is_link(os.lstat(path))
+        except OSError as exc:
+            rel = os.path.relpath(path, root).replace(os.sep, "/")
+            unreadable.append(InboundRecord(rel, None, "UNREADABLE", "", "",
+                                            exc.strerror or str(exc)))
+            return False
+
     found = []
     for dirpath, dirnames, filenames in os.walk(root, onerror=failed):
         dirnames[:] = sorted(d for d in dirnames if d not in WALK_SKIPS
+                             and entered(dirpath, d)
                              and not os.path.isfile(os.path.join(dirpath, d, "pyvenv.cfg")))
         for name in filenames:
             rel = os.path.relpath(os.path.join(dirpath, name), root)
@@ -178,10 +194,68 @@ def _walk(root, unreadable):
     return sorted(found)
 
 
+#: The bit of a reparse tag that marks a name surrogate: a symbolic link or a junction (TASK 128
+#: R2.2). Held here, not read from a sibling (TASK 131 R2.6).
+_NAME_SURROGATE = 0x20000000
+
+
+class _LinkRefused(Exception):
+    """An open of TASK 131 R2.2 met a link or a swap; the text is the refusal."""
+
+
+def _is_link(st):
+    """True for a symbolic link, or a reparse point whose tag is a name surrogate (TASK 131 R1.3).
+
+    Both attributes of Windows are read with `getattr`: only Windows sets them. A junction is a
+    link; a cloud placeholder is not.
+    """
+    return stat.S_ISLNK(st.st_mode) or bool(
+        getattr(st, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
+        and getattr(st, "st_reparse_tag", 0) & _NAME_SURROGATE)
+
+
+def _open_nofollow(path, flags):
+    """A descriptor of `path` opened with `flags` and no link followed (TASK 131 R2.1, R2.2).
+
+    Where `O_NOFOLLOW` exists, the open of the base. Elsewhere, Windows among them: `os.lstat`, a
+    refusal of a link or of any entry that is not a regular file, `os.open` with `O_NONBLOCK` and
+    `O_BINARY` where they exist, and `os.fstat`, which must give the identity of the `lstat`. A
+    refusal raises `_LinkRefused`; an `OSError` of the calls passes to the caller.
+    """
+    nofollow = getattr(os, "O_NOFOLLOW", None)
+    if nofollow is not None:
+        return os.open(path, flags | nofollow | getattr(os, "O_NONBLOCK", 0))
+    before = os.lstat(path)
+    if _is_link(before):
+        raise _LinkRefused("is a link")
+    if not stat.S_ISREG(before.st_mode):
+        raise _LinkRefused("is not a regular file")
+    fd = os.open(path, flags | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
+    try:
+        st = os.fstat(fd)
+    except BaseException:
+        os.close(fd)
+        raise
+    if (st.st_dev, st.st_ino) != (before.st_dev, before.st_ino):
+        os.close(fd)
+        raise _LinkRefused("changed during the run")
+    return fd
+
+
+def _inside(path, root):
+    """True when `path` lies inside `root`; paths on two drives lie outside (TASK 131 R5.1)."""
+    try:
+        return os.path.commonpath([path, root]) == root
+    except ValueError:
+        return False
+
+
 def _read(path):
     """`(bytes, (st_dev, st_ino))` of a regular file, through a descriptor that follows no link."""
     try:
-        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0))
+        fd = _open_nofollow(path, os.O_RDONLY)
+    except _LinkRefused as exc:
+        raise _Unreadable(str(exc)) from exc
     except OSError as exc:
         raise _Unreadable(exc.strerror or str(exc)) from exc
     try:
@@ -328,8 +402,11 @@ def _descriptor_path(fd):
     lookup, so no swap of a directory between two lookups by name can change it, as one can
     between `realpath` and `stat`. A failed lookup raises `OSError`. The same lookup as
     `rebase_links._descriptor_path`, held here since a copy of one module may run beside
-    the base of the other.
+    the base of the other. Where `os.name` is not `posix` it gives none: it imports no `fcntl`
+    and reads no `/proc` (TASK 131 R2.3).
     """
+    if os.name != "posix":
+        return None
     try:
         import fcntl
     except ImportError:
@@ -352,12 +429,14 @@ def _write_file(root, rel, original, ident, data, dry_run=False):
     path = os.path.join(root, rel)
     real_root = os.path.realpath(root)
     parent = os.path.realpath(os.path.dirname(path))
-    if os.path.commonpath([parent, real_root]) != real_root:
+    if not _inside(parent, real_root):
         return _Refusal("its directory resolves outside the working directory", False)
     if _rl._under_git(rel, root):
         return _Refusal("lies under .git/", False)
     try:
-        fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0))
+        fd = _open_nofollow(path, os.O_RDWR)
+    except _LinkRefused as exc:
+        return _Refusal(str(exc), False)
     except OSError as exc:
         return _Refusal(f"cannot open it: {exc.strerror or exc}", False)
     written = 0
@@ -376,7 +455,7 @@ def _write_file(root, rel, original, ident, data, dry_run=False):
             return _Refusal("is not the file at its real path", False)
         if (now.st_dev, now.st_ino) != (st.st_dev, st.st_ino):
             return _Refusal("is not the file at its real path", False)
-        if os.path.commonpath([os.path.dirname(where), real_root]) != real_root:
+        if not _inside(os.path.dirname(where), real_root):
             return _Refusal("its directory resolves outside the working directory", False)
         if (st.st_dev, st.st_ino) != ident:
             return _Refusal("changed during the run", False)
@@ -456,7 +535,7 @@ def _scan_set(root, unreadable):
     if toplevel is None:
         return "walk", [p for p in _walk(root, unreadable) if p.endswith(".md")], ""
     real_root, real_top = os.path.realpath(root), os.path.realpath(toplevel)
-    if os.path.commonpath([real_root, real_top]) != real_top:
+    if not _inside(real_root, real_top):
         raise InboundError(f"{root} does not lie inside its git top level {toplevel}")
     paths = {unicodedata.normalize("NFC", p): p for p in _ls_files(root) if p.endswith(".md")}
     try:
@@ -488,10 +567,8 @@ def retarget_inbound(repo_root, task_archive, plan_archive=None, since=None, dry
         InboundResult(records, archived_slot_links, scan, since, exit_code).
 
     Raises:
-        InboundError: an operand, git, `<rev>` or the platform (exit 2); nothing was written.
+        InboundError: an operand, git or `<rev>` (exit 2); nothing was written.
     """
-    if not hasattr(os, "O_NOFOLLOW"):
-        raise InboundError("this platform has no O_NOFOLLOW")
     root = os.path.abspath(repo_root)
     digits, archives = _check_archives(root, task_archive, plan_archive)
     task_id = int(digits)
diff --git a/.agent/tools/task_id_tool.py b/.agent/tools/task_id_tool.py
index e229cf1..294fe23 100644
--- a/.agent/tools/task_id_tool.py
+++ b/.agent/tools/task_id_tool.py
@@ -97,9 +97,11 @@ def _first_h1(path: str) -> Optional[str]:
     head), a leading YAML front matter and fenced code blocks are skipped: the sub-task template
     puts a comment block above its H1, and a YAML or shell comment line starts with `# `.
     The file is opened with `O_NONBLOCK | O_NOCTTY` and read only when `fstat` shows a regular
-    file, so a FIFO or a device named `task-*.md` does not block the scan.
+    file, so a FIFO or a device named `task-*.md` does not block the scan. Where `O_BINARY` exists,
+    Windows among them, the open passes it, so the read stops at no byte `0x1A` (TASK 131 R2.7).
     """
-    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOCTTY', 0)
+    flags = (os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOCTTY', 0)
+             | getattr(os, 'O_BINARY', 0))
     try:
         fd = os.open(path, flags)
     except OSError:
@@ -133,6 +135,18 @@ def _first_h1(path: str) -> Optional[str]:
     return None
 
 
+def _unc(value: str) -> bool:
+    """True where paths have drives and `value` is a UNC or device path (TASK 131 R12.1).
+
+    Such a path starts with two separators, or with the NT prefix `\\??\\`. The check reads the
+    text, each `/` as `\\`, so it reaches no file system: on Windows an open of a UNC path sends
+    the user's credentials to its host. It reads no drive of `value`: `splitdrive` gives none for
+    `\\??\\`.
+    """
+    text = value.replace('/', '\\')
+    return bool(os.path.splitdrive('c:')[0]) and text.startswith(('\\\\', '\\??\\'))
+
+
 def classify_task_file(tasks_dir: str, filename: str) -> Optional[tuple[int, bool]]:
     """`(task id, is_subtask)` of a file in `tasks_dir`, or None when its name is not `task-<id>-*.md`.
 
@@ -396,6 +410,12 @@ if __name__ == "__main__":
     # `--no-correction` now states the default, so passing both is consistent.
     allow_correction = args.allow_correction and not args.no_correction
 
+    # TASK 131 R12: a UNC `--tasks-dir` is refused before any call reaches the file system.
+    if _unc(args.tasks_dir):
+        print(json.dumps({"filename": None, "used_id": None, "status": "error",
+                          "message": "--tasks-dir is a UNC or device path"}, indent=2))
+        sys.exit(1)
+
     result = generate_task_archive_filename(
         slug=args.slug,
         proposed_id=args.proposed_id,
diff --git a/.agent/tools/test_rebase_links.py b/.agent/tools/test_rebase_links.py
index 57d5258..e03740c 100644
--- a/.agent/tools/test_rebase_links.py
+++ b/.agent/tools/test_rebase_links.py
@@ -3,17 +3,22 @@
 One test per row of the decision table, one per markdown construct that can
 carry a path, and regression pins for the two defects an adversarial review
 found in the first design: the mutable-slot case and the indented-continuation
-masking rule.
+masking rule. TC-W25 (TASK 131 R5.3): a record writes its `denotes_old` with `/` on every
+platform, so the check of TASK 117 R2 reads a slot archive in parts on Windows too.
 """
 
 import json
+import ntpath
 import os
 import sys
+import types
+from unittest import mock
 
 import pytest
 
 sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
+import rebase_links  # noqa: E402
 from rebase_links import rebase_document_links, rebase_file  # noqa: E402
 
 
@@ -206,7 +211,7 @@ class TestReporting:
         _, rec = rb(repo, "[a](ARCHITECTURE.md)\n")
         assert rec[0].authored == "ARCHITECTURE.md"
         assert rec[0].new_target == "../ARCHITECTURE.md"
-        assert rec[0].denotes_old == os.path.join("docs", "ARCHITECTURE.md")
+        assert rec[0].denotes_old == "docs/ARCHITECTURE.md"     # TASK 131 R5.3
 
 
 class TestUnmappedSlot:
@@ -492,11 +497,12 @@ class TestFileModeCommandLine:
         assert self.run("docs/tasks/t.md") == 0
         assert moved.read_bytes() == "# é\n[a](../ARCHITECTURE.md)\n".encode("utf-8")
 
-    def test_f3_a_non_utf8_operand_raises_as_at_the_base(self, tmp_path):
+    def test_f3_a_non_utf8_operand_is_refused(self, tmp_path, capsys):
+        # TASK 131 R3.3 replaces the traceback of the base by a refusal, exit 2.
         moved = tmp_path / "docs" / "tasks" / "t.md"
         moved.write_bytes(b"\xff\xfe[a](ARCHITECTURE.md)\n")
-        with pytest.raises(UnicodeDecodeError):
-            self.run("docs/tasks/t.md")
+        assert self.run("docs/tasks/t.md") == 2
+        assert json.loads(capsys.readouterr().err)["error"] == "docs/tasks/t.md: is not UTF-8"
         assert moved.read_bytes() == b"\xff\xfe[a](ARCHITECTURE.md)\n"
 
     def test_f4_a_dry_run_writes_nothing(self, tmp_path):
@@ -531,3 +537,20 @@ class TestFileModeCommandLine:
         moved.write_bytes(b"[a](../ARCHITECTURE.md)\n")
         assert self.run("docs/t.md", from_dir="docs/tasks", to_dir="docs") == 0
         assert moved.read_bytes() == b"[a](ARCHITECTURE.md)\n"
+
+
+class TestWindowsSeparators:
+    """TC-W25 (TASK 131 R5.3), with the paths of Windows on any platform."""
+
+    def test_w25_a_slot_record_holds_slashes(self):
+        # base-fail: `denotes_old` holds `\\` under `ntpath`, so `_adds_parts` reads one part.
+        windows = types.SimpleNamespace(path=ntpath, sep="\\")
+        with mock.patch.object(rebase_links, "os", windows):
+            new_text, records = rebase_document_links(
+                "[t](TASK.md)\n", "docs", "docs/plans", "C:\\repo",
+                {"docs/TASK.md": "docs/tasks/task-001-x.md"})
+        assert [r.action for r in records] == ["SLOT_RESOLVED"]
+        assert records[0].denotes_old == "docs/tasks/task-001-x.md"
+        assert records[0].new_target == "../tasks/task-001-x.md"
+        assert not rebase_links._adds_parts(records[0])
+        assert new_text == "[t](../tasks/task-001-x.md)\n"
diff --git a/.agent/tools/test_slot_links.py b/.agent/tools/test_slot_links.py
index 266c8ff..24af90e 100644
--- a/.agent/tools/test_slot_links.py
+++ b/.agent/tools/test_slot_links.py
@@ -14,15 +14,24 @@ next task's TASK and PLAN filled it (WI-38). This module pins TC-0 to TC-46 of T
 
 Git fixtures run with `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1` and a fixed identity,
 set for the test process so that the module's own git calls read no operator configuration.
+
+TC-W13, TC-W17, TC-W19, TC-W20 and TC-W24 (TASK 131) pin the inbound mode on a platform without
+`O_NOFOLLOW`, Windows among them. A test that makes a symbolic link or a FIFO skips where the
+platform cannot, and a test whose premise is a behaviour of POSIX skips on Windows (TASK 131 R6.5).
 """
 
+import contextlib
 import errno
 import json
 import os
 import shutil
+import stat
 import subprocess
 import sys
+import tempfile
+import types
 from pathlib import Path
+from unittest import mock
 
 import pytest
 
@@ -48,6 +57,71 @@ def isolated_git(monkeypatch, tmp_path):
         monkeypatch.setenv(key, value)
 
 
+def _can_symlink():
+    """True where this process can make a symbolic link; Windows asks for a privilege."""
+    probe = Path(tempfile.mkdtemp())
+    try:
+        (probe / "link").symlink_to(probe / "target")
+        return True
+    except OSError:
+        return False
+    finally:
+        shutil.rmtree(probe, ignore_errors=True)
+
+
+needs_symlink = pytest.mark.skipif(not _can_symlink(), reason="this process cannot make a link")
+needs_fifo = pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="no os.mkfifo")
+#: TASK 131 R6.5: a premise of POSIX that Windows does not hold.
+posix_premise = pytest.mark.skipif(os.name == "nt", reason="a premise of POSIX (TASK 131 D22)")
+windows_only = pytest.mark.skipif(os.name != "nt", reason="a behaviour of Windows")
+#: The reparse tag of a junction (TASK 128 R2.2).
+JUNCTION = 0xA0000003
+
+
+@contextlib.contextmanager
+def no_o_nofollow():
+    """`os.O_NOFOLLOW` deleted, as on Windows, for the time of the block."""
+    saved = getattr(os, "O_NOFOLLOW", None)
+    if saved is not None:
+        del os.O_NOFOLLOW
+    try:
+        yield
+    finally:
+        if saved is not None:
+            os.O_NOFOLLOW = saved
+
+
+def lstat_reporting(paths, **extra):
+    """A patch of `os.lstat` that reports the attributes of Windows of `extra` for `paths`."""
+    real = os.lstat
+
+    def lstat(path, *args, **kwargs):
+        st = real(path, *args, **kwargs)
+        if os.fspath(path) not in paths:
+            return st
+        fields = {name: getattr(st, name) for name in dir(st) if name.startswith("st_")}
+        fields.setdefault("st_file_attributes", 0)
+        fields.setdefault("st_reparse_tag", 0)
+        fields.update(extra)
+        return types.SimpleNamespace(**fields)
+    return mock.patch("os.lstat", side_effect=lstat)
+
+
+def unused_open_bit():
+    """A bit that no `os.O_*` flag of this platform uses."""
+    used = 0
+    for name in dir(os):
+        if name.startswith("O_"):
+            used |= getattr(os, name)
+    return next(1 << bit for bit in range(30, 15, -1) if not used & (1 << bit))
+
+
+def junction(link, target):
+    """A junction at `link` to the directory `target` (Windows only), as CPython's tests make it."""
+    import _winapi
+    _winapi.CreateJunction(str(target), str(link))
+
+
 def write(root, rel, text, newline="\n"):
     path = Path(root) / rel
     path.parent.mkdir(parents=True, exist_ok=True)
@@ -213,7 +287,7 @@ def test_tc6_fences_and_code_spans_are_not_links(project):
 def test_tc7_link_text(project, before, after):
     sub = write(project, "docs/tasks/task-033-03-x.md", f"# Task 033-03: x\n\n{before}\n")
     retarget_inbound(str(project), TASK, PLAN)
-    assert sub.read_text() == f"# Task 033-03: x\n\n{after}\n"
+    assert sub.read_text(encoding="utf-8") == f"# Task 033-03: x\n\n{after}\n"
 
 
 @pytest.mark.parametrize("before, after", [
@@ -240,6 +314,7 @@ def test_tc8_fragment_brackets_and_reference_definitions(project, before, after)
     ("--task", "docs/tasks/task-033-linked.md"),
     ("--plan", PLAN),
 ])
+@needs_symlink
 def test_tc9_operands_exit_2_and_write_nothing(project, args):
     write(project, "docs/tasks/task-033-01-guards.md", "# Task 033-01: Guards\n\n[x](../TASK.md)\n")
     (project / "docs/tasks/task-033-linked.md").symlink_to(project / TASK)
@@ -269,6 +344,7 @@ def test_tc10_since_errors_exit_2(project):
     assert {k: v for k, v in after.items() if k in before} == before
 
 
+@needs_symlink
 def test_tc11_links_and_hard_links_are_not_written(project, tmp_path):
     outside = Path(os.path.realpath(tmp_path)) / "outside.md"
     outside.write_text("[x](../TASK.md)\n")
@@ -352,6 +428,7 @@ def test_tc18_an_unresolved_rewrite_exits_1(project, monkeypatch):
     assert retarget_inbound(str(project), TASK).exit_code == 1
 
 
+@needs_symlink
 def test_tc19_walk_mode_skips_git_node_modules_and_directory_links(project, tmp_path):
     outside = Path(os.path.realpath(tmp_path)) / "elsewhere"
     write(outside, "x.md", "[x](../docs/TASK.md)\n")
@@ -396,14 +473,15 @@ def test_tc21_no_driver_filter_or_hook_runs(project, tmp_path):
         hook = scratch / f"{name}.sh"
         body = ('cat "$1"' if name == "textconv"
                 else "cat" if name in ("clean", "smudge") else "exit 0")
-        hook.write_text(f"#!/bin/sh\ntouch '{sentinels[name]}'\n{body}\n")
+        # TASK 131 R6.6: LF bytes and paths of POSIX, which the shell of git reads on Windows too.
+        hook.write_bytes(f"#!/bin/sh\ntouch '{sentinels[name].as_posix()}'\n{body}\n".encode())
         hook.chmod(0o755)
     for key, value in (("diff.external", scratch / "external.sh"),
                        ("diff.md.textconv", scratch / "textconv.sh"),
                        ("filter.sentinel.clean", scratch / "clean.sh"),
                        ("filter.sentinel.smudge", scratch / "smudge.sh"),
                        ("core.fsmonitor", scratch / "fsmonitor.sh")):
-        git(project, "config", key, str(value))
+        git(project, "config", key, value.as_posix())
     write(project, ".gitattributes", "*.md diff=md filter=sentinel\n")
     design.write_text("Old [s](../TASK.md).\n\nNew [s](../TASK.md).\n")
 
@@ -419,7 +497,7 @@ def test_tc21_no_driver_filter_or_hook_runs(project, tmp_path):
         path.unlink()
     # A tracked file changed at the same size: `git status` must read it through the clean
     # filter, since its size no longer tells it apart from the index.
-    same.write_text("bbbb\n")
+    same.write_bytes(b"bbbb\n")
     stamp = same.stat()
     os.utime(same, (stamp.st_atime + 5, stamp.st_mtime + 5))
 
@@ -444,6 +522,7 @@ def test_tc22_inherited_git_variables_change_nothing(project, tmp_path, monkeypa
     assert retarget_inbound(str(project), TASK, PLAN, since=base, dry_run=True) == expected
 
 
+@needs_symlink
 def test_tc23_a_root_below_the_top_level_through_a_link(tmp_path):
     real = Path(os.path.realpath(tmp_path))
     top = real / "mono"
@@ -475,10 +554,13 @@ def test_tc24_only_the_added_copy_of_a_duplicated_line_is_own(project):
                                ("docs/design/core.md", 4, "RETARGETED")]
 
 
-def test_platform_without_o_nofollow_refuses(project, monkeypatch):
-    monkeypatch.delattr(os, "O_NOFOLLOW")
-    with pytest.raises(InboundError):
-        retarget_inbound(str(project), TASK, PLAN)
+def test_platform_without_o_nofollow_refuses(project):
+    # base-fail: the base refuses the platform (TASK 131 R2.4). The name stays from TASK 116.
+    sub = write(project, "docs/tasks/task-033-30-x.md", "# Task 033-30: x\n\n[a](../TASK.md)\n")
+    with no_o_nofollow():
+        result = retarget_inbound(str(project), TASK, PLAN)
+    assert records(result) == [("docs/tasks/task-033-30-x.md", 3, "RETARGETED")]
+    assert "[a](task-033-admission-core-v1.md)" in sub.read_text(encoding="utf-8")
 
 
 # --- stage-2 round 1 ---------------------------------------------------------------------------
@@ -500,6 +582,7 @@ def _after_read(monkeypatch, rel, change):
     monkeypatch.setattr(slot_links, "_read", hooked)
 
 
+@needs_symlink
 def test_tc26_a_parent_linked_outside_is_refused(project, tmp_path):
     write(project, "docs/design/x.md", "Old.\n")
     init_repo(project)
@@ -517,7 +600,8 @@ def test_tc26_a_parent_linked_outside_is_refused(project, tmp_path):
     assert (outside / "x.md").read_text() == "Old.\nNew [s](../TASK.md).\n"
 
 
-@pytest.mark.parametrize("how", ["replaced", "changed", "fifo"])
+@pytest.mark.parametrize("how", ["replaced", "changed",
+                                 pytest.param("fifo", marks=needs_fifo)])
 def test_tc26_a_file_changed_after_the_read_is_refused(project, monkeypatch, how):
     rel = "docs/tasks/task-033-20-x.md"
     sub = write(project, rel, "# Task 033-20: x\n\n[a](../TASK.md)\n")
@@ -543,6 +627,8 @@ def test_tc26_a_file_changed_after_the_read_is_refused(project, monkeypatch, how
         assert "[a](../TASK.md)" in sub.read_text()
 
 
+@pytest.mark.skipif(os.name == "nt", reason="Windows refuses to replace a file that a descriptor "
+                    "holds (TASK 131 D22)")
 def test_tc27_a_file_replaced_after_the_write_is_refused(project, monkeypatch):
     rel = "docs/tasks/task-033-21-x.md"
     sub = write(project, rel, "# Task 033-21: x\n\n[a](../TASK.md)\n")
@@ -604,6 +690,8 @@ def test_tc30_a_write_that_fails_after_its_first_byte_exits_1(project, monkeypat
     assert result.exit_code == 1
 
 
+@needs_symlink
+@pytest.mark.skipif(os.name == "nt", reason="NTFS refuses a line break in a name (TASK 131 D22)")
 def test_tc31_the_text_output_escapes_and_json_is_ascii(project):
     (project / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
     (project / "docs" / "x\n[RETARGETED] forged.md").symlink_to(project / TASK)
@@ -686,6 +774,7 @@ def test_tc36_an_ignored_subtask_is_still_read(project):
 
 
 @pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root reads any directory")
+@posix_premise
 def test_tc37_an_unreadable_directory_is_listed(project):
     secret = project / "docs" / "secret"
     secret.mkdir()
@@ -761,6 +850,7 @@ def test_tc42_autojunk_stays_off(project):
 
 
 @pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root reads any directory")
+@posix_premise
 def test_tc43_an_unreadable_tasks_directory_is_listed_in_git_mode(project):
     init_repo(project)
     commit(project)
@@ -792,6 +882,7 @@ def test_tc44_a_closed_stdout_exits_1_with_the_error_object(monkeypatch, capsys)
     assert json.loads(capsys.readouterr().err)["ok"] is False
 
 
+@needs_fifo
 def test_tc45_the_tasks_listing_reads_regular_files_only(project):
     init_repo(project)
     commit(project)
@@ -817,3 +908,234 @@ def test_tc46_a_file_without_a_slot_name_is_not_masked(project, monkeypatch):
     assert "No slot name here.\n" not in masked
     assert "[a](TASK.md)\n" in masked
 
+
+# --- TASK 131: a platform without O_NOFOLLOW, Windows among them -------------------------------
+
+def _hook_open(monkeypatch, path, when, change):
+    """Run `change()` once, right before the first `os.open` of `path` whose flags pass `when`."""
+    real_open, done = os.open, []
+
+    def opener(name, flags, *args, **kwargs):
+        if os.path.abspath(name) == str(path) and when(flags) and not done:
+            done.append(True)
+            change()
+        return real_open(name, flags, *args, **kwargs)
+    monkeypatch.setattr(os, "open", opener)
+    return done
+
+
+@needs_symlink
+def test_w19_a_file_swapped_for_a_link_after_the_read_lstat(project, monkeypatch, tmp_path):
+    # base-fail: the base refuses the platform before it reads.
+    outside = Path(os.path.realpath(tmp_path)) / "outside.md"
+    outside.write_text("Outside.\n[x](../TASK.md)\n", encoding="utf-8")
+    rel = "docs/design/x.md"
+    design = write(project, rel, "Inside, with no link.\nTASK.md\n")
+
+    def swap():
+        design.unlink()
+        design.symlink_to(outside)
+    done = _hook_open(monkeypatch, project / rel, lambda flags: not flags & os.O_RDWR, swap)
+    with no_o_nofollow():
+        result = retarget_inbound(str(project), TASK, PLAN)
+    assert done, "the hook never swapped"
+    assert [(r.file, r.action, r.reason) for r in result.records if r.file == rel] == [
+        (rel, "UNREADABLE", "changed during the run")]
+    assert outside.read_text(encoding="utf-8") == "Outside.\n[x](../TASK.md)\n"
+
+
+@needs_symlink
+def test_w19_a_file_swapped_for_a_link_after_the_write_lstat(project, monkeypatch, tmp_path):
+    outside = Path(os.path.realpath(tmp_path)) / "victim.md"
+    rel = "docs/tasks/task-033-31-x.md"
+    text = "# Task 033-31: x\n\n[a](../TASK.md)\n"
+    outside.write_text(text, encoding="utf-8")
+    sub = write(project, rel, text)
+
+    def swap():
+        sub.unlink()
+        sub.symlink_to(outside)
+    _hook_open(monkeypatch, project / rel, lambda flags: flags & os.O_RDWR, swap)
+    with no_o_nofollow():
+        result = retarget_inbound(str(project), TASK, PLAN)
+    assert _reason(result, rel, "REFUSED") == ["changed during the run"]
+    assert outside.read_text(encoding="utf-8") == text
+
+
+def test_w19_a_reparse_tag_at_the_read_or_at_the_write(project, monkeypatch):
+    rel = "docs/tasks/task-033-32-x.md"
+    text = "# Task 033-32: x\n\n[a](../TASK.md)\n"
+    sub = write(project, rel, text)
+    path = os.path.join(str(project), rel)
+    tag = dict(st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT, st_reparse_tag=JUNCTION)
+    with no_o_nofollow(), lstat_reporting({path}, **tag):
+        result = retarget_inbound(str(project), TASK, PLAN)
+    assert [(r.action, r.reason) for r in result.records if r.file == rel] == [
+        ("UNREADABLE", "is a link")]
+
+    original = slot_links._read
+    read = []
+
+    def reading(name):
+        value = original(name)
+        if name == path:
+            read.append(True)
+        return value
+    monkeypatch.setattr(slot_links, "_read", reading)
+    real_lstat = os.lstat
+
+    def lstat(name, *args, **kwargs):
+        st = real_lstat(name, *args, **kwargs)
+        if os.fspath(name) != path or not read:
+            return st
+        fields = {key: getattr(st, key) for key in dir(st) if key.startswith("st_")}
+        fields.update(tag)
+        return types.SimpleNamespace(**fields)
+    with no_o_nofollow(), mock.patch("os.lstat", side_effect=lstat):
+        result = retarget_inbound(str(project), TASK, PLAN)
+    assert _reason(result, rel, "REFUSED") == ["is a link"]
+    assert sub.read_text(encoding="utf-8") == text
+
+
+def test_w20_the_walk_enters_no_directory_with_a_name_surrogate_tag(project):
+    # base-fail: `os.walk` enters a junction on Windows; the base has no filter (TASK 131 R2.5).
+    hidden = project / "docs" / "junction-like"
+    write(hidden, "x.md", "[x](../TASK.md)\n")
+    tag = dict(st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT, st_reparse_tag=JUNCTION)
+    with lstat_reporting({str(hidden)}, **tag):
+        result = retarget_inbound(str(project), TASK, PLAN)
+    assert result.scan == "walk"
+    assert [r.file for r in result.records if r.file.startswith("docs/junction-like")] == []
+
+
+@windows_only
+def test_w20_the_walk_enters_no_junction(project, tmp_path):
+    outside = Path(os.path.realpath(tmp_path)) / "elsewhere"
+    write(outside, "x.md", "[x](../docs/TASK.md)\n")
+    junction(project / "linked", outside)
+    try:
+        result = retarget_inbound(str(project), TASK, PLAN)
+    finally:
+        os.rmdir(project / "linked")
+    assert [r.file for r in result.records if r.file.startswith("linked")] == []
+
+
+@pytest.mark.parametrize("o_nofollow", [True, False])
+def test_w13_the_inbound_mode_keeps_every_byte(project, o_nofollow):
+    rel = "docs/tasks/task-033-33-x.md"
+    data = b"# Task 033-33: x\r\n\r\n[a](../TASK.md)\r\nline\x1a after the byte\r\n"
+    path = project / rel
+    path.parent.mkdir(parents=True, exist_ok=True)
+    path.write_bytes(data)
+    with (contextlib.nullcontext() if o_nofollow else no_o_nofollow()):
+        result = retarget_inbound(str(project), TASK, PLAN)
+    assert records(result) == [(rel, 3, "RETARGETED")]
+    assert path.read_bytes() == data.replace(b"(../TASK.md)", b"(task-033-admission-core-v1.md)")
+
+
+@pytest.mark.parametrize("call", [1, 2])
+def test_w17_two_drives_are_outside_at_the_write(project, call):
+    # base-fail: a ValueError of `commonpath` ends the base in a traceback (TASK 131 R5.1).
+    rel = "docs/tasks/task-033-34-x.md"
+    sub = write(project, rel, "# Task 033-34: x\n\n[a](../TASK.md)\n")
+    original, st = sub.read_bytes(), sub.stat()
+    calls, real = [], os.path.commonpath
+
+    def commonpath(paths):
+        calls.append(paths)
+        if len(calls) == call:
+            raise ValueError("Paths don't have the same drive")
+        return real(paths)
+    with mock.patch("os.path.commonpath", side_effect=commonpath):
+        refusal = slot_links._write_file(str(project), rel, original, (st.st_dev, st.st_ino),
+                                         b"rewritten\n")
+    assert refusal is not None
+    assert refusal.reason == "its directory resolves outside the working directory"
+    assert sub.read_bytes() == original
+
+
+def test_w17_two_drives_are_outside_at_the_scan(project):
+    init_repo(project)
+    commit(project)
+    with mock.patch("os.path.commonpath",
+                    side_effect=ValueError("Paths don't have the same drive")):
+        with pytest.raises(InboundError, match="does not lie inside its git top level"):
+            retarget_inbound(str(project), TASK, PLAN)
+
+
+def test_w24_each_open_of_the_inbound_mode_passes_o_binary(project, monkeypatch):
+    rel = "docs/tasks/task-033-35-x.md"
+    write(project, rel, "# Task 033-35: x\n\n[a](../TASK.md)\n")
+    bit, seen, real_open = unused_open_bit(), [], os.open
+
+    def spy(name, flags, *args, **kwargs):
+        if os.path.abspath(name) == os.path.abspath(os.path.join(str(project), rel)):
+            seen.append(flags)
+        return real_open(name, flags & ~bit, *args, **kwargs)
+    monkeypatch.setattr(os, "O_BINARY", bit, raising=False)
+    monkeypatch.setattr(os, "open", spy)
+    with no_o_nofollow():
+        result = retarget_inbound(str(project), TASK, PLAN)
+    assert records(result) == [(rel, 3, "RETARGETED")]
+    # The H1 scan of `task_id_tool._first_h1` opens the sub-task too (TASK 131 R2.7).
+    assert len(seen) >= 2 and any(flags & os.O_RDWR for flags in seen), seen
+    assert all(flags & bit for flags in seen), "an open drops O_BINARY"
+    nonblock = getattr(os, "O_NONBLOCK", 0)
+    assert all(flags & nonblock == nonblock for flags in seen), "an open drops O_NONBLOCK"
+
+
+# --- the fix of round 1 of stage 2 (TASK 131 D24 to D26) ---------------------------------------
+
+@needs_fifo
+def test_w37_without_o_nofollow_a_fifo_is_never_opened(project, monkeypatch):
+    fifo = project / "docs" / "design" / "f.md"
+    fifo.parent.mkdir(parents=True)
+    os.mkfifo(fifo)
+    opened, real_open = [], os.open
+
+    def opener(name, flags, *args, **kwargs):
+        if os.path.abspath(name) == str(fifo):
+            opened.append(flags)                    # the open would block: fail it instead
+            raise OSError(errno.EAGAIN, "the test refuses to open the FIFO")
+        return real_open(name, flags, *args, **kwargs)
+    monkeypatch.setattr(os, "open", opener)
+    with no_o_nofollow():
+        result = retarget_inbound(str(project), TASK, PLAN)
+    assert [(r.action, r.reason) for r in result.records if r.file == "docs/design/f.md"] == [
+        ("UNREADABLE", "is not a regular file")]
+    assert opened == [], "the FIFO was opened"
+
+
+def test_w40_a_directory_whose_lstat_fails_is_not_entered(project):
+    hidden = project / "docs" / "locked"
+    write(hidden, "x.md", "[x](../TASK.md)\n")
+    real_lstat = os.lstat
+
+    def lstat(path, *args, **kwargs):
+        if os.fspath(path) == str(hidden):
+            raise PermissionError(13, "Permission denied")
+        return real_lstat(path, *args, **kwargs)
+    with mock.patch("os.lstat", side_effect=lstat):
+        result = retarget_inbound(str(project), TASK, PLAN)
+    assert result.scan == "walk"
+    assert [(r.file, r.action) for r in result.records if r.file.startswith("docs/locked")] == [
+        ("docs/locked", "UNREADABLE")]
+
+
+def test_w41_a_crlf_subtask_with_a_fence(project):
+    # base-fail: at the base no fence closes on CR LF, so the link after it is never seen.
+    rel = "docs/tasks/task-033-36-x.md"
+    path = project / rel
+    path.parent.mkdir(parents=True, exist_ok=True)
+    data = (b"# Task 033-36: x\r\n\r\n[b](../TASK.md)\r\n\r\n```\r\n[c](../TASK.md)\r\n```\r\n"
+            b"\r\n[a](../TASK.md)\r\n\r\n`span\r\n \t\r\n[d](../TASK.md) and `x`\r\n")
+    path.write_bytes(data)
+    result = retarget_inbound(str(project), TASK, PLAN)
+    assert sorted(records(result)) == [(rel, 3, "RETARGETED"), (rel, 9, "RETARGETED"),
+                                       (rel, 13, "RETARGETED")]
+    expected = data
+    for label in (b"a", b"b", b"d"):
+        expected = expected.replace(b"[" + label + b"](../TASK.md)",
+                                    b"[" + label + b"](task-033-admission-core-v1.md)")
+    assert path.read_bytes() == expected
+
diff --git a/.agent/tools/test_task_id_tool.py b/.agent/tools/test_task_id_tool.py
index 5b3807f..dcb7b52 100644
--- a/.agent/tools/test_task_id_tool.py
+++ b/.agent/tools/test_task_id_tool.py
@@ -204,7 +204,9 @@ class TestSubTaskByH1:
     @staticmethod
     def _write(tasks_dir, name, h1):
         tasks_dir.mkdir(exist_ok=True)
-        (tasks_dir / name).write_text(f"{h1}\n\nBody.\n" if h1 else "No heading.\n")
+        # TASK 131 R6.6: the dashes of an H1 are not ASCII.
+        (tasks_dir / name).write_text(f"{h1}\n\nBody.\n" if h1 else "No heading.\n",
+                                      encoding="utf-8")
 
     def test_tc1_letter_suffixed_subtasks_are_not_a_parent(self, tmp_path):
         tasks_dir = tmp_path / "tasks"
@@ -329,6 +331,7 @@ class TestSubTaskByH1:
         assert not worker.is_alive(), "the scan blocked on a special file"
         return result[0]
 
+    @pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="no os.mkfifo")
     def test_a_fifo_is_not_read(self, tmp_path):
         """A FIFO named like a task file does not block the scan; its name decides."""
         tasks_dir = tmp_path / "tasks"
@@ -336,6 +339,7 @@ class TestSubTaskByH1:
         os.mkfifo(tasks_dir / "task-033-05a-x.md")
         assert self._scan_with_timeout(tasks_dir) == [33]
 
+    @pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="no os.mkfifo")
     def test_a_fifo_with_data_is_not_read(self, tmp_path):
         """Only a regular file is read: a FIFO holding a sub-task H1 is classified by its name."""
         tasks_dir = tmp_path / "tasks"
@@ -705,5 +709,59 @@ class TestAllowCorrectionPolarity:
         assert proc.returncode == 0
 
 
+class TestFirstH1Binary:
+    """TC-W24 (TASK 131 R2.7): the H1 scan opens its file with `O_BINARY` where it exists."""
+
+    def test_w24_the_h1_scan_passes_o_binary(self, tmp_path, monkeypatch):
+        import task_id_tool
+        used = 0
+        for name in dir(os):
+            if name.startswith("O_"):
+                used |= getattr(os, name)
+        bit = next(1 << b for b in range(30, 15, -1) if not used & (1 << b))
+        path = tmp_path / "task-033-05a-x.md"
+        path.write_bytes(b"# Task 033-05a: x\r\n\r\nBody.\r\n")
+        seen, real_open = [], os.open
+
+        def spy(name, flags, *args, **kwargs):
+            seen.append(flags)
+            return real_open(name, flags & ~bit, *args, **kwargs)
+        monkeypatch.setattr(os, "O_BINARY", bit, raising=False)
+        monkeypatch.setattr(os, "open", spy)
+        assert task_id_tool._first_h1(str(path)) == "# Task 033-05a: x"
+        assert seen and all(flags & bit for flags in seen), "the open drops O_BINARY"
+
+    def test_w42_a_unc_tasks_dir_is_refused(self):
+        # base-fail: the base lists any `--tasks-dir` (TASK 131 R12).
+        import ntpath
+        import posixpath
+        import types
+        from unittest import mock
+        import task_id_tool
+        unc = ("\\\\host\\share", "//host/share", "\\\\?\\C:\\x", "\\\\.\\pipe\\x",
+               "\\??\\UNC\\host\\share", "/??/UNC/host/share", "\\\\host\\\\share",
+               "\\\\\\host\\share", "\\\\host")
+        windows = types.SimpleNamespace(path=ntpath, sep="\\")
+        with mock.patch.object(task_id_tool, "os", windows):
+            for value in unc:
+                assert task_id_tool._unc(value), value
+            for value in ("C:\\repo\\docs\\tasks", "docs/tasks", "\\x"):
+                assert not task_id_tool._unc(value), value
+        with mock.patch.object(task_id_tool, "os", types.SimpleNamespace(path=posixpath, sep="/")):
+            for value in unc:
+                assert not task_id_tool._unc(value), f"no drives, no UNC path, on POSIX: {value}"
+
+    @pytest.mark.skipif(os.name != "nt", reason="a behaviour of Windows")
+    def test_w42_a_unc_tasks_dir_on_windows(self, tmp_path):
+        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task_id_tool.py")
+        result = subprocess.run([sys.executable, script, "x", "--tasks-dir",
+                                 "\\\\localhost\\nowhere"], capture_output=True, text=True,
+                                cwd=tmp_path, timeout=60)
+        assert result.returncode == 1, result.stderr
+        report = json.loads(result.stdout)
+        assert report["status"] == "error"
+        assert "UNC or device path" in report["message"]
+
+
 if __name__ == "__main__":
     pytest.main([__file__, "-v"])
diff --git a/tests/test_archive_move.py b/tests/test_archive_move.py
index 96a1c13..3eb951b 100644
--- a/tests/test_archive_move.py
+++ b/tests/test_archive_move.py
@@ -25,11 +25,18 @@ Before TASK 112 two allow rules, `Bash(mv docs/TASK.md docs/tasks/*)` and
   its unlink, holds another file then, or cannot be checked, leaves the archive in place
   (``TC-A19`` to ``TC-A23``);
 * an existing letter-suffixed sub-task file in the destination's place is refused (``TC-A24``,
-  TASK 114).
+  TASK 114);
+* on a platform without `dir_fd`, Windows among them, the move copies by path: it refuses a link,
+  a junction, a read-only source and a source with a second hard link; it keeps the archive when
+  the source changed after the copy; it tries an unlink 10 times; it keeps every byte; and each of
+  its opens passes `O_BINARY` (``TC-W1`` to ``TC-W10``, ``TC-W21`` to ``TC-W24``, TASK 131 R1).
+
+A test that patches the descriptors of `_move` skips where `_supported()` is false, and a test
+that makes a symbolic link skips where this process cannot make one (TASK 131 R6.5).
 
 Each case runs the script with the `realpath` of a temporary root as its working directory;
 TC-A11, TC-A13 and TC-A15 to TC-A18 call `main(argv)` in-process to replace `os.link`, `os.unlink`
-or `os.write`.
+or `os.write`; the TC-W tests call it in-process with `_supported` patched to return false.
 """
 import contextlib
 import importlib.util
@@ -37,9 +44,11 @@ import io
 import json
 import os
 import shutil
+import stat
 import subprocess
 import sys
 import tempfile
+import types
 import unittest
 from pathlib import Path
 from unittest import mock
@@ -59,6 +68,73 @@ def _load():
     return module
 
 
+def _can_symlink():
+    """True where this process can make a symbolic link; Windows asks for a privilege."""
+    probe = Path(tempfile.mkdtemp())
+    try:
+        (probe / "link").symlink_to(probe / "target")
+        return True
+    except OSError:
+        return False
+    finally:
+        shutil.rmtree(probe, ignore_errors=True)
+
+
+NEEDS_SYMLINK = unittest.skipUnless(_can_symlink(), "this process cannot make a symbolic link")
+NEEDS_DIR_FD = unittest.skipUnless(_load()._supported(),
+                                   "it patches the descriptors of `_move`, which need `dir_fd`")
+WINDOWS_ONLY = unittest.skipUnless(os.name == "nt", "a behaviour of Windows")
+#: The reparse tags of a junction, of a symbolic link and of a cloud placeholder (TASK 128 R2.2).
+JUNCTION, SYMLINK, CLOUD = 0xA0000003, 0xA000000C, 0x9000001A
+
+
+def _fake_stat(real, **extra):
+    """The fields of `real`, with the attributes of Windows that `extra` names."""
+    fields = {name: getattr(real, name) for name in dir(real) if name.startswith("st_")}
+    fields.setdefault("st_file_attributes", 0)
+    fields.setdefault("st_reparse_tag", 0)
+    fields.update(extra)
+    return types.SimpleNamespace(**fields)
+
+
+def _lstat_reporting(paths, **extra):
+    """A patch of `os.lstat` that reports `extra` for each path of `paths`."""
+    real = os.lstat
+
+    def lstat(path, *args, **kwargs):
+        st = real(path, *args, **kwargs)
+        return _fake_stat(st, **extra) if os.fspath(path) in paths else st
+    return mock.patch("os.lstat", side_effect=lstat)
+
+
+def _unused_open_bit():
+    """A bit that no `os.O_*` flag of this platform uses."""
+    used = 0
+    for name in dir(os):
+        if name.startswith("O_"):
+            used |= getattr(os, name)
+    return next(1 << bit for bit in range(30, 15, -1) if not used & (1 << bit))
+
+
+@contextlib.contextmanager
+def _no_o_nofollow():
+    """`os.O_NOFOLLOW` deleted, as on Windows, for the time of the block."""
+    saved = getattr(os, "O_NOFOLLOW", None)
+    if saved is not None:
+        del os.O_NOFOLLOW
+    try:
+        yield
+    finally:
+        if saved is not None:
+            os.O_NOFOLLOW = saved
+
+
+def _junction(link, target):
+    """A junction at `link` to the directory `target` (Windows only), as CPython's tests make it."""
+    import _winapi
+    _winapi.CreateJunction(str(target), str(link))
+
+
 class ArchiveTestCase(unittest.TestCase):
 
     def setUp(self):
@@ -71,7 +147,8 @@ class ArchiveTestCase(unittest.TestCase):
     def write(self, rel, text):
         path = self.root / rel
         path.parent.mkdir(parents=True, exist_ok=True)
-        path.write_text(text, encoding="utf-8")
+        # TASK 131 D26: LF on every platform, so a test may compare the bytes.
+        path.write_text(text, encoding="utf-8", newline="\n")
         return path
 
     def run_script(self, *args):
@@ -147,6 +224,7 @@ class TestRefusals(ArchiveTestCase):
         self.write(TASK_DEST, "# older\n")
         self.assertRefused((TASK, TASK_DEST))
 
+    @NEEDS_SYMLINK
     def test_a4_a_link_in_place_of_the_destination(self):
         outside = Path(os.path.realpath(tempfile.mkdtemp()))
         self.addCleanup(shutil.rmtree, outside)
@@ -163,6 +241,7 @@ class TestRefusals(ArchiveTestCase):
                 self.assertEqual(target.read_text(encoding="utf-8"), "victim\n")
                 self.assertFalse((outside / "absent.md").exists())
 
+    @NEEDS_SYMLINK
     def test_a5_a_linked_tasks_directory(self):
         outside = Path(os.path.realpath(tempfile.mkdtemp()))
         self.addCleanup(shutil.rmtree, outside)
@@ -170,6 +249,7 @@ class TestRefusals(ArchiveTestCase):
         self.assertRefused((TASK, TASK_DEST))
         self.assertEqual(os.listdir(outside), [])
 
+    @NEEDS_SYMLINK
     def test_a6_a_linked_source(self):
         real = self.write("elsewhere.md", "# elsewhere\n")
         (self.root / TASK).unlink()
@@ -201,6 +281,7 @@ class TestRefusals(ArchiveTestCase):
             with self.subTest(args=args):
                 self.assertRefused(args, code=2)
 
+    @NEEDS_SYMLINK
     def test_a9_a_linked_docs_directory(self):
         real = self.root / "real-docs"
         (self.root / "docs").rename(real)
@@ -240,6 +321,7 @@ class TestFallbacks(ArchiveTestCase):
         self.assertFalse((self.root / TASK).exists())
         self.assertEqual((self.root / TASK_DEST).read_text(encoding="utf-8"), "# task\n")
 
+    @NEEDS_DIR_FD
     def test_a11_copy_path_refuses_a_destination_that_appeared(self):
         racer = self.root / TASK_DEST
 
@@ -254,6 +336,7 @@ class TestFallbacks(ArchiveTestCase):
         self.assertEqual((self.root / TASK).read_text(encoding="utf-8"), "# task\n")
         self.assertEqual(racer.read_text(encoding="utf-8"), "# racer\n")
 
+    @NEEDS_DIR_FD
     def test_a13_a_source_that_cannot_be_removed_leaves_no_destination(self):
         real_unlink = os.unlink
 
@@ -286,6 +369,7 @@ class TestSwappedSource(ArchiveTestCase):
             (outside / "secret.md").write_text("secret\n", encoding="utf-8")
             source.symlink_to(outside / "secret.md")
 
+    @NEEDS_DIR_FD
     def test_a15_link_path_refuses_a_swapped_source(self):
         real_link = os.link
 
@@ -300,6 +384,7 @@ class TestSwappedSource(ArchiveTestCase):
         self.assertFalse((self.root / TASK_DEST).exists())
         self.assertEqual((self.root / TASK).read_text(encoding="utf-8"), "# swapped\n")
 
+    @NEEDS_DIR_FD
     def test_a16_copy_path_refuses_a_swapped_regular_file(self):
         def swap_then_fail(*_args, **_kwargs):
             self.swap("file")
@@ -311,6 +396,7 @@ class TestSwappedSource(ArchiveTestCase):
         self.assertIn("changed", report["error"])
         self.assertFalse((self.root / TASK_DEST).exists())
 
+    @NEEDS_DIR_FD
     def test_a17_copy_path_never_opens_a_link(self):
         def swap_then_fail(*_args, **_kwargs):
             self.swap("link")
@@ -336,6 +422,7 @@ class TestSwappedSource(ArchiveTestCase):
 class TestLastSteps(ArchiveTestCase):
     """TC-A19 to TC-A21 (TASK 112 fix round 2)."""
 
+    @NEEDS_DIR_FD
     def test_a19_a_failed_check_after_the_link_leaves_no_destination(self):
         real_link, real_stat, linked = os.link, os.stat, []
 
@@ -391,6 +478,7 @@ class TestLastSteps(ArchiveTestCase):
         finally:
             sys.path[:] = before
 
+    @NEEDS_DIR_FD
     def test_a21_a_vanished_source_keeps_the_archive(self):
         real_unlink = os.unlink
 
@@ -406,6 +494,7 @@ class TestLastSteps(ArchiveTestCase):
         self.assertIn("kept", report["error"])
         self.assertEqual((self.root / TASK_DEST).read_text(encoding="utf-8"), "# task\n")
 
+    @NEEDS_DIR_FD
     def test_a22_a_source_swapped_before_its_unlink_keeps_the_archive(self):
         real_unlink = os.unlink
 
@@ -424,6 +513,7 @@ class TestLastSteps(ArchiveTestCase):
         self.assertEqual((self.root / TASK_DEST).read_text(encoding="utf-8"), "# task\n")
         self.assertEqual((self.root / TASK).read_text(encoding="utf-8"), "# another\n")
 
+    @NEEDS_DIR_FD
     def test_a23_an_unconfirmed_source_keeps_both_names(self):
         real_unlink, real_stat, failed = os.unlink, os.stat, []
 
@@ -446,5 +536,714 @@ class TestLastSteps(ArchiveTestCase):
         self.assertEqual((self.root / TASK_DEST).read_text(encoding="utf-8"), "# task\n")
 
 
+class TestMoveByPath(ArchiveTestCase):
+    """TC-W1 to TC-W10, TC-W21 to TC-W24 (TASK 131 R1): the move on a platform without `dir_fd`.
+
+    Each test calls `main` in the test process with `_supported` patched to return false, the
+    branch that Windows takes (TASK 131 R6.2), and with `time.sleep` patched out of the tries.
+    """
+
+    def by_path(self, *args, patches=(), module=None):
+        """`(exit code, the JSON object printed)` of `main` with `_supported` false."""
+        module = module or _load()
+        out, err = io.StringIO(), io.StringIO()
+        cwd = os.getcwd()
+        os.chdir(self.root)
+        try:
+            with contextlib.ExitStack() as stack:
+                stack.enter_context(mock.patch.object(module, "_supported", return_value=False))
+                stack.enter_context(mock.patch("time.sleep"))
+                for patch in patches:
+                    stack.enter_context(patch)
+                stack.enter_context(contextlib.redirect_stdout(out))
+                stack.enter_context(contextlib.redirect_stderr(err))
+                code = module.main(list(args))
+        finally:
+            os.chdir(cwd)
+        return code, json.loads(out.getvalue() or err.getvalue())
+
+    def refused_by_path(self, args, message, patches=()):
+        before = self.tree()
+        code, report = self.by_path(*args, patches=patches)
+        self.assertEqual(code, 1, report)
+        self.assertFalse(report["ok"])
+        self.assertIn(message, report["error"])
+        self.assertEqual(self.tree(), before, "a refusal changed the disk")
+        return report
+
+    def outside(self):
+        path = Path(os.path.realpath(tempfile.mkdtemp()))
+        self.addCleanup(shutil.rmtree, path)
+        return path
+
+    def test_w1_the_move_by_path_copies(self):
+        for source, destination, text in ((TASK, TASK_DEST, b"# task\n"),
+                                          (PLAN, PLAN_DEST, b"# plan\n")):
+            with self.subTest(source=source):
+                code, report = self.by_path(source, destination)
+                self.assertEqual(code, 0, report)
+                self.assertEqual(report["method"], "copy")
+                self.assertTrue(report["created_directory"])
+                self.assertFalse((self.root / source).exists())
+                self.assertEqual((self.root / destination).read_bytes(), text)
+
+    def test_w1_the_script_moves_by_path_where_dir_fd_is_missing(self):
+        site = self.outside()
+        (site / "sitecustomize.py").write_text("import os\nos.supports_dir_fd = set()\n",
+                                               encoding="utf-8")
+        env = dict(os.environ, PYTHONPATH=str(site))
+        result = subprocess.run([sys.executable, str(SCRIPT), TASK, TASK_DEST], cwd=self.root,
+                                env=env, capture_output=True, text=True, timeout=60)
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertEqual(json.loads(result.stdout)["method"], "copy")
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
+
+    @NEEDS_SYMLINK
+    def test_w2_a_link_at_docs(self):
+        real = self.root / "real-docs"
+        (self.root / "docs").rename(real)
+        (self.root / "docs").symlink_to(real, target_is_directory=True)
+        self.refused_by_path((TASK, TASK_DEST), "'docs' is a symbolic link or not a directory")
+
+    @NEEDS_SYMLINK
+    def test_w2_a_link_at_the_destination_directory(self):
+        (self.root / "docs" / "tasks").symlink_to(self.outside(), target_is_directory=True)
+        self.refused_by_path((TASK, TASK_DEST), "'tasks' is a symbolic link or not a directory")
+
+    @NEEDS_SYMLINK
+    def test_w2_a_link_at_the_source(self):
+        real = self.write("elsewhere.md", "# elsewhere\n")
+        (self.root / TASK).unlink()
+        (self.root / TASK).symlink_to(real)
+        self.refused_by_path((TASK, TASK_DEST),
+                             "docs/TASK.md is a symbolic link or not a regular file")
+
+    def test_w2_a_reparse_tag_of_a_name_surrogate_is_a_link(self):
+        (self.root / "docs" / "tasks").mkdir()
+        for path, label in (("docs", "'docs'"), ("docs/tasks", "'tasks'")):
+            for tag in (JUNCTION, SYMLINK):
+                with self.subTest(path=path, tag=hex(tag)):
+                    patch = _lstat_reporting(
+                        {path}, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT,
+                        st_reparse_tag=tag)
+                    self.refused_by_path((TASK, TASK_DEST),
+                                         f"{label} is a symbolic link or not a directory",
+                                         patches=(patch,))
+
+    def test_w2_a_reparse_tag_that_is_no_name_surrogate_is_no_link(self):
+        patch = _lstat_reporting({"docs"}, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT,
+                                 st_reparse_tag=CLOUD)
+        code, report = self.by_path(TASK, TASK_DEST, patches=(patch,))
+        self.assertEqual(code, 0, report)
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
+
+    @WINDOWS_ONLY
+    def test_w2_a_junction_at_docs_or_at_the_destination_directory(self):
+        outside = self.outside()
+        tasks = self.root / "docs" / "tasks"
+        _junction(tasks, outside)
+        try:
+            self.refused_by_path((TASK, TASK_DEST),
+                                 "'tasks' is a symbolic link or not a directory")
+        finally:
+            os.rmdir(tasks)                     # removes the junction, not its target
+        real = self.root / "real-docs"
+        (self.root / "docs").rename(real)
+        _junction(self.root / "docs", real)
+        self.addCleanup(os.rmdir, self.root / "docs")
+        self.refused_by_path((TASK, TASK_DEST), "'docs' is a symbolic link or not a directory")
+
+    def test_w3_an_entry_at_the_destination(self):
+        tasks = self.root / "docs" / "tasks"
+        tasks.mkdir()
+        target = self.root / TASK_DEST
+        target.write_text("# older\n", encoding="utf-8")
+        self.refused_by_path((TASK, TASK_DEST), "the destination exists")
+        target.unlink()
+        target.mkdir()
+        self.refused_by_path((TASK, TASK_DEST), "the destination exists")
+        target.rmdir()
+        if _can_symlink():
+            target.symlink_to(self.outside() / "absent.md")
+            self.refused_by_path((TASK, TASK_DEST), "the destination exists")
+
+    def test_w4_a_second_hard_link_is_refused_at_its_lstat(self):
+        os.link(self.root / TASK, self.root / "alias.md")
+        self.refused_by_path((TASK, TASK_DEST), "docs/TASK.md has 2 hard links")
+
+    def test_w4_a_read_only_source_is_refused(self):
+        patch = _lstat_reporting({TASK}, st_file_attributes=stat.FILE_ATTRIBUTE_READONLY)
+        self.refused_by_path((TASK, TASK_DEST), "docs/TASK.md is read-only", patches=(patch,))
+
+    @WINDOWS_ONLY
+    def test_w4_a_read_only_source_on_windows(self):
+        source = self.root / TASK
+        os.chmod(source, stat.S_IREAD)
+        self.addCleanup(os.chmod, source, stat.S_IREAD | stat.S_IWRITE)
+        self.refused_by_path((TASK, TASK_DEST), "docs/TASK.md is read-only")
+
+    @NEEDS_SYMLINK
+    def test_w5_a_directory_swapped_for_a_link_before_the_create(self):
+        tasks = self.root / "docs" / "tasks"
+        tasks.mkdir()
+        outside = self.outside()
+        real_open = os.open
+
+        def open_(path, flags, *args, **kwargs):
+            if os.fspath(path) == TASK_DEST and flags & os.O_CREAT and not tasks.is_symlink():
+                tasks.rename(self.root / "docs" / "tasks-aside")
+                tasks.symlink_to(outside, target_is_directory=True)
+            return real_open(path, flags, *args, **kwargs)
+
+        code, report = self.by_path(TASK, TASK_DEST,
+                                    patches=(mock.patch("os.open", side_effect=open_),))
+        self.assertEqual(code, 1, report)
+        self.assertIn("the destination directory changed during the move", report["error"])
+        # R1.5: the undo removes nothing through the link; the empty file stays there (RW2).
+        self.assertIn("so docs/tasks/task-112-x.md is kept", report["error"])
+        self.assertEqual((outside / "task-112-x.md").read_bytes(), b"")
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")
+
+    def changed_after_the_copy(self, change):
+        """`(exit code, report, whether the change was refused)`; `change` runs after the copy."""
+        real_fsync, refused = os.fsync, []
+
+        def fsync(fd):
+            real_fsync(fd)
+            try:
+                change(self.root / TASK)
+            except PermissionError:
+                refused.append(True)            # Windows: the source's descriptor is open
+
+        code, report = self.by_path(TASK, TASK_DEST,
+                                    patches=(mock.patch("os.fsync", side_effect=fsync),))
+        return code, report, bool(refused)
+
+    def assertMovedDespite(self, code, report):
+        """TASK 131 D23, D28: a descriptor of the run refused the change, and the move ends."""
+        self.assertEqual(code, 0, report)
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
+        self.assertFalse((self.root / TASK).exists())
+
+    def test_w6_a_source_replaced_after_the_copy_keeps_the_archive(self):
+        def replace(source):
+            new = source.with_name("TASK.md.new")
+            new.write_bytes(b"# replaced\n")
+            os.replace(new, source)
+
+        code, report, refused = self.changed_after_the_copy(replace)
+        if refused:
+            return self.assertMovedDespite(code, report)
+        self.assertEqual(code, 1, report)
+        self.assertEqual(report["error"], "docs/TASK.md no longer holds the moved file, so "
+                                          "docs/tasks/task-112-x.md is kept")
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
+        self.assertEqual((self.root / TASK).read_bytes(), b"# replaced\n")
+
+    def test_w6_a_source_removed_after_the_copy_keeps_the_archive(self):
+        code, report, refused = self.changed_after_the_copy(os.unlink)
+        if refused:
+            return self.assertMovedDespite(code, report)
+        self.assertEqual(code, 1, report)
+        self.assertIn("is gone after the copy", report["error"])
+        self.assertIn("is kept", report["error"])
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
+
+    def test_w6_a_second_hard_link_after_the_copy_removes_the_archive(self):
+        code, report, refused = self.changed_after_the_copy(
+            lambda source: os.link(source, self.root / "alias.md"))
+        if refused:
+            return self.assertMovedDespite(code, report)
+        self.assertEqual(code, 1, report)
+        self.assertIn("the source changed during the move", report["error"])
+        self.assertFalse((self.root / TASK_DEST).exists())
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")
+
+    def unlink_failing(self, times, on_failure=None):
+        """A patch of `os.unlink` that fails `times` times on the source, then removes it."""
+        real_unlink, failures = os.unlink, []
+
+        def unlink(path, *args, **kwargs):
+            if os.fspath(path) == TASK and len(failures) < times:
+                failures.append(True)
+                if on_failure is not None:
+                    on_failure(len(failures))
+                raise PermissionError(13, "Permission denied")
+            return real_unlink(path, *args, **kwargs)
+        return mock.patch("os.unlink", side_effect=unlink)
+
+    def test_w7_the_unlink_of_the_source_is_tried_ten_times(self):
+        code, report = self.by_path(TASK, TASK_DEST, patches=(self.unlink_failing(10),))
+        self.assertEqual(code, 1, report)
+        self.assertIn("cannot remove docs/TASK.md", report["error"])
+        self.assertFalse((self.root / TASK_DEST).exists())
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")
+
+    def test_w7_the_tenth_try_moves_the_file(self):
+        code, report = self.by_path(TASK, TASK_DEST, patches=(self.unlink_failing(9),))
+        self.assertEqual(code, 0, report)
+        self.assertFalse((self.root / TASK).exists())
+
+    def test_w7_a_source_replaced_between_two_tries_keeps_both(self):
+        def replace(count):
+            if count == 2:
+                new = self.root / "docs" / "TASK.md.new"
+                new.write_bytes(b"# replaced\n")
+                os.replace(new, self.root / TASK)
+
+        # Two failures, so that a third try with no check of step 9 removes the replacement.
+        code, report = self.by_path(TASK, TASK_DEST,
+                                    patches=(self.unlink_failing(2, on_failure=replace),))
+        self.assertEqual(code, 1, report)
+        self.assertIn("no longer holds the moved file", report["error"])
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
+        self.assertEqual((self.root / TASK).read_bytes(), b"# replaced\n")
+
+    def test_w7_a_source_removed_before_a_try_of_the_archives_removal(self):
+        real_unlink, failed = os.unlink, []
+
+        def unlink(path, *args, **kwargs):
+            name = os.fspath(path)
+            if name == TASK:
+                raise PermissionError(13, "Permission denied")
+            if name == TASK_DEST and not failed:
+                failed.append(True)
+                real_unlink(self.root / TASK)       # another process removes the source
+                raise PermissionError(13, "Permission denied")
+            return real_unlink(path, *args, **kwargs)
+
+        code, report = self.by_path(TASK, TASK_DEST,
+                                    patches=(mock.patch("os.unlink", side_effect=unlink),))
+        self.assertEqual(code, 1, report)
+        self.assertIn("was removed, so", report["error"])
+        self.assertIn("is kept", report["error"])
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
+
+    @WINDOWS_ONLY
+    def test_w8_a_source_held_open_by_another_handle(self):
+        with open(self.root / TASK, "rb"):
+            code, report = self.by_path(TASK, TASK_DEST)
+        self.assertEqual(code, 1, report)
+        self.assertIn("cannot remove docs/TASK.md", report["error"])
+        self.assertFalse((self.root / TASK_DEST).exists())
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")
+
+    def test_w9_the_archive_keeps_every_byte(self):
+        data = b"# task\r\nline\x1a after the byte\r\nlast\n"
+        (self.root / TASK).write_bytes(data)
+        code, report = self.by_path(TASK, TASK_DEST)
+        self.assertEqual(code, 0, report)
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), data)
+
+    @NEEDS_DIR_FD
+    def test_w10_a_platform_with_dir_fd_never_moves_by_path(self):
+        module = _load()
+        out = io.StringIO()
+        cwd = os.getcwd()
+        os.chdir(self.root)
+        try:
+            with mock.patch.object(module, "_move_by_path",
+                                   side_effect=AssertionError("moved by path")), \
+                    contextlib.redirect_stdout(out):
+                code = module.main([TASK, TASK_DEST])
+        finally:
+            os.chdir(cwd)
+        self.assertEqual(code, 0)
+        self.assertTrue(json.loads(out.getvalue())["ok"])
+
+    def test_w21_a_regular_file_swapped_in_before_the_open(self):
+        real_open = os.open
+
+        def open_(path, flags, *args, **kwargs):
+            if os.fspath(path) == TASK and not flags & os.O_CREAT:
+                new = self.root / "docs" / "TASK.md.new"
+                new.write_bytes(b"# swapped\n")
+                os.replace(new, self.root / TASK)
+            return real_open(path, flags, *args, **kwargs)
+
+        code, report = self.by_path(TASK, TASK_DEST,
+                                    patches=(mock.patch("os.open", side_effect=open_),))
+        self.assertEqual(code, 1, report)
+        self.assertIn("the source changed during the move", report["error"])
+        self.assertFalse((self.root / "docs" / "tasks").exists())
+        self.assertEqual((self.root / TASK).read_bytes(), b"# swapped\n")
+
+    @NEEDS_SYMLINK
+    def test_w21_a_link_swapped_in_where_o_nofollow_is_missing(self):
+        secret = self.outside() / "secret.md"
+        secret.write_bytes(b"secret\n")
+        real_open = os.open
+
+        def open_(path, flags, *args, **kwargs):
+            if os.fspath(path) == TASK and not flags & os.O_CREAT:
+                link = self.root / "docs" / "TASK.md.link"
+                link.symlink_to(secret)
+                os.replace(link, self.root / TASK)
+            return real_open(path, flags, *args, **kwargs)
+
+        with _no_o_nofollow():
+            code, report = self.by_path(TASK, TASK_DEST,
+                                        patches=(mock.patch("os.open", side_effect=open_),))
+        self.assertEqual(code, 1, report)
+        self.assertIn("the source changed during the move", report["error"])
+        self.assertFalse((self.root / "docs" / "tasks").exists())
+
+    def test_w22_an_overlong_name_is_a_json_refusal(self):
+        code, report = self.by_path(TASK, "docs/tasks/task-112-" + "a" * 300 + ".md")
+        self.assertEqual(code, 1, report)
+        self.assertFalse(report["ok"])
+        self.assertFalse((self.root / "docs" / "tasks").exists())
+
+    def test_w22_a_created_directory_is_removed_after_a_failed_rmdir(self):
+        real_rmdir, failed = os.rmdir, []
+
+        def rmdir(path, *args, **kwargs):
+            if os.fspath(path) == "docs/plans" and not failed:
+                failed.append(True)
+                raise PermissionError(13, "Permission denied")
+            return real_rmdir(path, *args, **kwargs)
+
+        code, report = self.by_path(PLAN, "docs/plans/plan-112-" + "a" * 300 + ".md",
+                                    patches=(mock.patch("os.rmdir", side_effect=rmdir),))
+        self.assertEqual(code, 1, report)
+        self.assertTrue(failed, "the refusal removed no directory")
+        self.assertFalse((self.root / "docs" / "plans").exists())
+
+    def test_w23_the_docstring_names_both_branches_and_the_windows(self):
+        doc = _load().__doc__
+        self.assertIn("_move_by_path", doc)
+        self.assertIn("2 usage error.", doc)
+        self.assertIn("access rules", doc)
+        for label in range(1, 13):
+            with self.subTest(label=label):
+                self.assertRegex(doc, rf"\bRW{label}\b")
+
+    def test_w24_each_open_of_the_move_passes_o_binary(self):
+        bit, calls, real_open = _unused_open_bit(), [], os.open
+
+        def spy(path, flags, *args, **kwargs):
+            calls.append((os.fspath(path), flags))
+            return real_open(path, flags & ~bit, *args, **kwargs)
+
+        code, report = self.by_path(TASK, TASK_DEST, patches=(
+            mock.patch.object(os, "O_BINARY", bit, create=True),
+            mock.patch("os.open", side_effect=spy)))
+        self.assertEqual(code, 0, report)
+        self.assertEqual(sorted(path for path, _flags in calls), [TASK, TASK_DEST])
+        for path, flags in calls:
+            with self.subTest(path=path):
+                self.assertTrue(flags & bit, f"the open of {path} drops O_BINARY")
+
+    # --- the fix of round 1 of stage 2 (TASK 131 D26) ------------------------------------------
+
+    def open_hook(self, path, when, change):
+        """A patch of `os.open` that runs `change()` once, before the first open of `path` that
+        `when(flags)` accepts; the list it returns names each open of `path`."""
+        real_open, seen = os.open, []
+
+        def opener(name, flags, *args, **kwargs):
+            if os.fspath(name) == path:
+                seen.append(flags)
+                if when(flags) and len([f for f in seen if when(f)]) == 1:
+                    change()
+            return real_open(name, flags, *args, **kwargs)
+        return mock.patch("os.open", side_effect=opener), seen
+
+    def test_w29_a_second_hard_link_before_the_open_of_the_source(self):
+        real_open, opened = os.open, []
+
+        def opener(name, flags, *args, **kwargs):
+            opened.append(os.fspath(name))
+            if os.fspath(name) == TASK and opened.count(TASK) == 1:
+                os.link(self.root / TASK, self.root / "alias.md")
+            return real_open(name, flags, *args, **kwargs)
+        code, report = self.by_path(TASK, TASK_DEST,
+                                    patches=(mock.patch("os.open", side_effect=opener),))
+        self.assertEqual(code, 1, report)
+        self.assertIn("the source changed during the move", report["error"])
+        self.assertNotIn(TASK_DEST, opened, "step 6 opened the destination")
+        self.assertFalse((self.root / "docs" / "tasks").exists(), "step 4 ran")
+
+    def refused_on_windows(self, change, refused):
+        """`change()`; on Windows its `PermissionError` is noted in `refused` (TASK 131 D28)."""
+        try:
+            change()
+        except PermissionError:
+            if os.name != "nt":
+                raise
+            refused.append(True)                # a descriptor of the run holds the file
+
+    @NEEDS_SYMLINK
+    def test_w30_docs_moved_out_and_linked_back_before_the_create(self):
+        (self.root / "docs" / "tasks").mkdir()
+        away = self.outside() / "docs-moved"
+        refused = []
+
+        def move_docs():
+            (self.root / "docs").rename(away)
+            (self.root / "docs").symlink_to(away, target_is_directory=True)
+        patch, _seen = self.open_hook(TASK_DEST, lambda flags: flags & os.O_CREAT,
+                                      lambda: self.refused_on_windows(move_docs, refused))
+        code, report = self.by_path(TASK, TASK_DEST, patches=(patch,))
+        if refused:
+            return self.assertMovedDespite(code, report)
+        self.assertEqual(code, 1, report)
+        self.assertIn("the destination directory changed during the move", report["error"])
+        # R1.5: the undo removes nothing through a changed directory (RW2).
+        self.assertIn("so docs/tasks/task-112-x.md is kept", report["error"])
+        self.assertEqual((away / "tasks" / "task-112-x.md").read_bytes(), b"")
+        self.assertEqual((away / "TASK.md").read_bytes(), b"# task\n")
+
+    def test_w31_another_file_at_the_destination_after_the_create(self):
+        (self.root / "docs" / "tasks").mkdir()
+        target, aside = self.root / TASK_DEST, self.root / "docs" / "made-aside.md"
+        real_open, refused = os.open, []
+
+        def put_another():
+            target.rename(aside)
+            target.write_bytes(b"# impostor\n")
+
+        def opener(name, flags, *args, **kwargs):
+            fd = real_open(name, flags, *args, **kwargs)
+            if os.fspath(name) == TASK_DEST and flags & os.O_CREAT:
+                self.refused_on_windows(put_another, refused)
+            return fd
+        code, report = self.by_path(TASK, TASK_DEST,
+                                    patches=(mock.patch("os.open", side_effect=opener),))
+        if refused:
+            return self.assertMovedDespite(code, report)
+        self.assertEqual(code, 1, report)
+        self.assertEqual(report["error"], "the destination directory changed during the move; "
+                                          "docs/tasks/task-112-x.md no longer holds the file "
+                                          "this run made, so that file is kept")
+        self.assertEqual(target.read_bytes(), b"# impostor\n")
+        self.assertEqual(aside.read_bytes(), b"")
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")
+
+    def test_w32_the_undo_tries_the_removal_of_the_archive(self):
+        real_unlink, failed = os.unlink, []
+
+        def unlink(name, *args, **kwargs):
+            if os.fspath(name) == TASK_DEST and not failed:
+                failed.append(True)
+                raise PermissionError(13, "Permission denied")
+            return real_unlink(name, *args, **kwargs)
+        code, report = self.by_path(TASK, TASK_DEST, patches=(
+            mock.patch("os.write", side_effect=OSError(28, "No space left on device")),
+            mock.patch("os.unlink", side_effect=unlink)))
+        self.assertEqual(code, 1, report)
+        self.assertIn("cannot copy the source", report["error"])
+        self.assertTrue(failed)
+        self.assertFalse((self.root / TASK_DEST).exists())
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")
+
+    def failed_step_10(self, error, before=None):
+        """`main` with the unlink of the source failing with `error`; `before` runs first."""
+        real_unlink = os.unlink
+
+        def unlink(name, *args, **kwargs):
+            if os.fspath(name) == TASK:
+                if before is not None:
+                    before()
+                raise error
+            return real_unlink(name, *args, **kwargs)
+        return self.by_path(TASK, TASK_DEST, patches=(mock.patch("os.unlink", side_effect=unlink),))
+
+    def test_w33_a_vanished_source_keeps_the_archive(self):
+        code, report = self.failed_step_10(FileNotFoundError(2, "No such file or directory"),
+                                           before=lambda: os.remove(self.root / TASK))
+        self.assertEqual(code, 1, report)
+        self.assertIn("it is gone, so docs/tasks/task-112-x.md is kept", report["error"])
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
+
+    def test_w33_a_source_that_holds_another_file_keeps_the_archive(self):
+        def swap():
+            new = self.root / "docs" / "TASK.md.new"
+            new.write_bytes(b"# another\n")
+            os.replace(new, self.root / TASK)
+        code, report = self.failed_step_10(OSError(5, "Input/output error"), before=swap)
+        self.assertEqual(code, 1, report)
+        self.assertIn("it no longer holds the moved file, so", report["error"])
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
+        self.assertEqual((self.root / TASK).read_bytes(), b"# another\n")
+
+    def test_w33_an_unconfirmed_source_keeps_both_names(self):
+        real_lstat, real_unlink, failed = os.lstat, os.unlink, []
+
+        def unlink(name, *args, **kwargs):
+            if os.fspath(name) == TASK:
+                failed.append(True)
+                raise OSError(5, "Input/output error")
+            return real_unlink(name, *args, **kwargs)
+
+        def lstat(name, *args, **kwargs):
+            if failed and os.fspath(name) == TASK:
+                raise OSError(5, "Input/output error")
+            return real_lstat(name, *args, **kwargs)
+        code, report = self.by_path(TASK, TASK_DEST, patches=(
+            mock.patch("os.unlink", side_effect=unlink),
+            mock.patch("os.lstat", side_effect=lstat)))
+        self.assertEqual(code, 1, report)
+        self.assertIn("or confirm what it holds", report["error"])
+        self.assertIn("both it and docs/tasks/task-112-x.md are kept", report["error"])
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
+
+    def test_w33_a_failed_removal_of_the_archive_keeps_the_base_message(self):
+        def unlink(name, *args, **kwargs):
+            raise PermissionError(13, "Permission denied")
+        code, report = self.by_path(TASK, TASK_DEST,
+                                    patches=(mock.patch("os.unlink", side_effect=unlink),))
+        self.assertEqual(code, 1, report)
+        self.assertEqual(report["error"],
+                         "cannot remove docs/TASK.md (Permission denied), and "
+                         "docs/tasks/task-112-x.md remains (Permission denied)")
+
+    @NEEDS_SYMLINK
+    def test_w34_a_directory_swapped_before_the_removal_of_the_archive(self):
+        tasks = self.root / "docs" / "tasks"
+        tasks.mkdir()
+        outside = self.outside()
+        decoy = outside / "task-112-x.md"
+        decoy.write_bytes(b"# decoy\n")
+        real_lstat, swapped = os.lstat, []
+
+        def lstat(name, *args, **kwargs):
+            st = real_lstat(name, *args, **kwargs)
+            if os.fspath(name) == TASK_DEST and copied and not swapped:
+                swapped.append(True)                # the check of the archive passed
+                tasks.rename(self.root / "docs" / "tasks-aside")
+                tasks.symlink_to(outside, target_is_directory=True)
+            return st
+        copied = []
+
+        def failing_write(fd, data):
+            copied.append(True)
+            raise OSError(28, "No space left on device")
+        code, report = self.by_path(TASK, TASK_DEST, patches=(
+            mock.patch("os.write", side_effect=failing_write),
+            mock.patch("os.lstat", side_effect=lstat)))
+        self.assertEqual(code, 1, report)
+        self.assertTrue(swapped, "the hook never swapped")
+        self.assertIn("so docs/tasks/task-112-x.md is kept", report["error"])
+        self.assertEqual(decoy.read_bytes(), b"# decoy\n")
+
+    def test_w35_an_encrypted_source_is_refused(self):
+        patch = _lstat_reporting({TASK}, st_file_attributes=stat.FILE_ATTRIBUTE_ENCRYPTED)
+        self.refused_by_path((TASK, TASK_DEST), "docs/TASK.md is encrypted", patches=(patch,))
+
+    def test_w36_a_write_to_the_source_after_the_copy(self):
+        real_fsync = os.fsync
+
+        def fsync(fd):
+            real_fsync(fd)
+            with open(self.root / TASK, "ab") as handle:
+                handle.write(b"written later\n")
+            # a later time of the last write than that of step 3
+            st = os.stat(self.root / TASK)
+            os.utime(self.root / TASK, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))
+        code, report = self.by_path(TASK, TASK_DEST,
+                                    patches=(mock.patch("os.fsync", side_effect=fsync),))
+        self.assertEqual(code, 1, report)
+        self.assertIn("the source changed during the move", report["error"])
+        self.assertFalse((self.root / TASK_DEST).exists())
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\nwritten later\n")
+
+    # --- the fix of round 2 of stage 2 (TASK 131 D28) ------------------------------------------
+
+    def test_w43_a_write_to_the_source_between_two_tries_of_step_10(self):
+        def write(_count):
+            with open(self.root / TASK, "ab") as handle:
+                handle.write(b"written later\n")
+
+        code, report = self.by_path(TASK, TASK_DEST,
+                                    patches=(self.unlink_failing(1, on_failure=write),))
+        self.assertEqual(code, 1, report)
+        self.assertEqual(report["error"], "the source changed during the move")
+        self.assertFalse((self.root / TASK_DEST).exists())
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\nwritten later\n")
+
+    def test_w44_another_file_at_the_archives_name_between_two_tries_of_the_undo(self):
+        real_unlink, failed = os.unlink, []
+
+        def unlink(name, *args, **kwargs):
+            if os.fspath(name) == TASK_DEST and not failed:
+                failed.append(True)
+                another = self.root / "docs" / "tasks" / "another.md"
+                another.write_bytes(b"# another\n")
+                os.replace(another, self.root / TASK_DEST)
+                raise PermissionError(13, "Permission denied")
+            return real_unlink(name, *args, **kwargs)
+        code, report = self.by_path(TASK, TASK_DEST, patches=(
+            mock.patch("os.write", side_effect=OSError(28, "No space left on device")),
+            mock.patch("os.unlink", side_effect=unlink)))
+        self.assertEqual(code, 1, report)
+        self.assertTrue(failed, "the undo tried no removal")
+        self.assertTrue(report["error"].endswith("so that file is kept"), report["error"])
+        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# another\n")
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")
+
+    def copy_failing(self, path, change):
+        """Patches: the copy fails, and `change()` runs at the first `lstat` of `path` after it."""
+        real_lstat, copied, changed = os.lstat, [], []
+
+        def lstat(name, *args, **kwargs):
+            if os.fspath(name) == path and copied and not changed:
+                changed.append(True)
+                change()
+            return real_lstat(name, *args, **kwargs)
+
+        def failing_write(fd, data):
+            copied.append(True)
+            raise OSError(28, "No space left on device")
+        return (mock.patch("os.write", side_effect=failing_write),
+                mock.patch("os.lstat", side_effect=lstat)), changed
+
+    def test_w45_a_renamed_destination_directory_keeps_the_archive(self):
+        tasks = self.root / "docs" / "tasks"
+        tasks.mkdir()
+        aside = self.root / "docs" / "tasks-aside"
+        patches, changed = self.copy_failing(TASK_DEST, lambda: tasks.rename(aside))
+        code, report = self.by_path(TASK, TASK_DEST, patches=patches)
+        self.assertEqual(code, 1, report)
+        self.assertTrue(changed, "the undo never checked the archive")
+        self.assertEqual(report["error"], "cannot copy the source: No space left on device; "
+                                          "docs/tasks/task-112-x.md no longer holds the file "
+                                          "this run made, so that file is kept")
+        self.assertEqual((aside / "task-112-x.md").read_bytes(), b"")
+        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")
+
+    def test_w46_a_created_directory_replaced_before_the_undo_stays(self):
+        plans = self.root / "docs" / "plans"
+
+        def replace():
+            plans.rename(self.root / "docs" / "plans-aside")
+            plans.mkdir()                       # another, empty directory at its name
+        patches, changed = self.copy_failing(PLAN_DEST, replace)
+        code, report = self.by_path(PLAN, PLAN_DEST, patches=patches)
+        self.assertEqual(code, 1, report)
+        self.assertTrue(changed, "the undo never checked the archive")
+        self.assertTrue(plans.is_dir(), "the undo removed a directory that it did not create")
+        self.assertEqual((self.root / "docs" / "plans-aside" / "plan-112-x.md").read_bytes(), b"")
+
+    def test_w46_a_created_directory_replaced_between_two_tries_stays(self):
+        plans = self.root / "docs" / "plans"
+        real_rmdir, failed = os.rmdir, []
+
+        def rmdir(path, *args, **kwargs):
+            if os.fspath(path) == "docs/plans" and not failed:
+                failed.append(True)
+                plans.rename(self.root / "docs" / "plans-aside")
+                plans.mkdir()                   # another, empty directory at its name
+                raise PermissionError(13, "Permission denied")
+            return real_rmdir(path, *args, **kwargs)
+
+        code, report = self.by_path(PLAN, "docs/plans/plan-112-" + "a" * 300 + ".md",
+                                    patches=(mock.patch("os.rmdir", side_effect=rmdir),))
+        self.assertEqual(code, 1, report)
+        self.assertTrue(failed, "the refusal removed no directory")
+        self.assertTrue(plans.is_dir(), "the undo removed a directory that it did not create")
+
+
 if __name__ == "__main__":
     unittest.main()
diff --git a/tests/test_script_guards.py b/tests/test_script_guards.py
index dd8393c..2450770 100644
--- a/tests/test_script_guards.py
+++ b/tests/test_script_guards.py
@@ -13,10 +13,10 @@ skill directory at any `--path` or path-shaped name. This file pins:
   exit 2 and no write, also through a `..` after a link; a file whose directory link resolves
   inside is rewritten (``TC-G13`` to ``TC-G15``, TASK 116 R1.1);
 * both modes write through the descriptor they checked: a directory swapped around the open or
-  moved out, a file swapped for a link, a second hard link, a file replaced after the read, a FIFO
-  and a platform with no `O_NOFOLLOW` are refused with no write, and so are three swaps around the
-  identity check; a failed write leaves a prefix of the new text, and no descriptor stays open
-  (``TC-G16`` to ``TC-G27``, TASK 116 R7);
+  moved out, a file swapped for a link, a second hard link, a file replaced after the read and a
+  FIFO are refused with no write, and so are three swaps around the identity check; a failed
+  write leaves a prefix of the new text, and no descriptor stays open (``TC-G16`` to ``TC-G27``,
+  TASK 116 R7). A platform with no `O_NOFOLLOW` opens through the check of TASK 131 R2.2;
 * `rebase_links.py` takes a slot map only for `docs/TASK.md` and `docs/PLAN.md`, each with an
   archive of its form, and only a markdown operand under `docs/`. Its `--repo-root`, `--from` and
   `--to` stay in the tree. A rewrite adds to a link no character outside letters, digits and
@@ -27,11 +27,20 @@ skill directory at any `--path` or path-shaped name. This file pins:
   planted beside the script runs (``TC-G8`` to ``TC-G12``, TASK 115), through a path in other
   letter case either (ARC-13, TASK 128);
 * `init_skill.py` refuses a skill directory outside the working directory or under `.git/`, with
-  exit 1 and nothing created (``TC-G4``, ``TC-G5``); a directory inside is created (``TC-G6``).
+  exit 1 and nothing created (``TC-G4``, ``TC-G5``); a directory inside is created (``TC-G6``);
+* on a platform without `O_NOFOLLOW`, Windows among them, the file mode opens with a check before
+  and after the open, refuses a junction, keeps every byte, writes any text in any stream
+  encoding, refuses an operand that is not UTF-8, finds no `.pyc` under a relative null device,
+  treats paths on two drives as outside, and keeps its own helpers (``TC-W11`` to ``TC-W18``,
+  ``TC-W24``, ``TC-W26``, ``TC-W27``, TASK 131).
+
+A test that makes a symbolic link skips where this process cannot make one, and a test whose
+premise is a behaviour of POSIX skips on Windows (TASK 131 R6.5, D22).
 
 The working directory is the `realpath` of a temporary root: `os.getcwd()` returns the resolved
 path on darwin, where `tempfile` returns `/var/...`.
 """
+import ast
 import builtins
 import contextlib
 import errno
@@ -39,12 +48,17 @@ import gc
 import importlib.util
 import io
 import json
+import ntpath
 import os
+import posixpath
+import py_compile
 import re
 import shutil
+import stat
 import subprocess
 import sys
 import tempfile
+import types
 import unittest
 from pathlib import Path
 from unittest import mock
@@ -61,6 +75,9 @@ LINKED = "[a](ARCHITECTURE.md)\n"
 REBASED = "[a](../ARCHITECTURE.md)\n"
 SUBTASK = "# Task 112-01: a\n\n[docs/TASK.md](../TASK.md)\n"
 RETARGETED = "# Task 112-01: a\n\n[task-112](task-112-x.md)\n"
+UNC_PATHS = ("\\\\host\\share", "//host/share", "\\\\?\\C:\\x", "\\\\.\\pipe\\x",
+             "\\??\\UNC\\host\\share", "/??/UNC/host/share", "\\\\host\\\\share",
+             "\\\\\\host\\share", "\\\\host")  # TASK 131 R12.1, TC-W42
 
 
 def _tmp(case):
@@ -123,6 +140,80 @@ def _descriptor_path_known():
     return hasattr(fcntl, "F_GETPATH") or os.path.isdir("/proc/self/fd")
 
 
+def _can_symlink():
+    """True where this process can make a symbolic link; Windows asks for a privilege."""
+    probe = Path(tempfile.mkdtemp())
+    try:
+        (probe / "link").symlink_to(probe / "target")
+        return True
+    except OSError:
+        return False
+    finally:
+        shutil.rmtree(probe, ignore_errors=True)
+
+
+NEEDS_SYMLINK = unittest.skipUnless(_can_symlink(), "this process cannot make a symbolic link")
+WINDOWS_ONLY = unittest.skipUnless(os.name == "nt", "a behaviour of Windows")
+#: TASK 131 R6.5: a premise of POSIX that Windows does not hold.
+POSIX_PREMISE = os.name == "nt"
+#: The characters that a name on NTFS cannot hold.
+NTFS_REFUSES = set('<>:"|?*') if os.name == "nt" else set()
+#: The reparse tag of a junction (TASK 128 R2.2).
+JUNCTION = 0xA0000003
+
+
+def _o_nofollow_refusal(posix):
+    """The refusal of an open that meets a swap: `posix`, or that of TASK 131 R2.2."""
+    return posix if hasattr(os, "O_NOFOLLOW") else "changed during the run"
+
+
+@contextlib.contextmanager
+def _no_o_nofollow():
+    """`os.O_NOFOLLOW` deleted, as on Windows, for the time of the block."""
+    saved = getattr(os, "O_NOFOLLOW", None)
+    if saved is not None:
+        del os.O_NOFOLLOW
+    try:
+        yield
+    finally:
+        if saved is not None:
+            os.O_NOFOLLOW = saved
+
+
+def _fake_stat(real, **extra):
+    """The fields of `real`, with the attributes of Windows that `extra` names."""
+    fields = {name: getattr(real, name) for name in dir(real) if name.startswith("st_")}
+    fields.setdefault("st_file_attributes", 0)
+    fields.setdefault("st_reparse_tag", 0)
+    fields.update(extra)
+    return types.SimpleNamespace(**fields)
+
+
+def _lstat_reporting(paths, **extra):
+    """A patch of `os.lstat` that reports `extra` for each path of `paths`."""
+    real = os.lstat
+
+    def lstat(path, *args, **kwargs):
+        st = real(path, *args, **kwargs)
+        return _fake_stat(st, **extra) if os.fspath(path) in paths else st
+    return mock.patch("os.lstat", side_effect=lstat)
+
+
+def _unused_open_bit():
+    """A bit that no `os.O_*` flag of this platform uses."""
+    used = 0
+    for name in dir(os):
+        if name.startswith("O_"):
+            used |= getattr(os, name)
+    return next(1 << bit for bit in range(30, 15, -1) if not used & (1 << bit))
+
+
+def _junction(link, target):
+    """A junction at `link` to the directory `target` (Windows only), as CPython's tests make it."""
+    import _winapi
+    _winapi.CreateJunction(str(target), str(link))
+
+
 class TestRebaseLinksGuard(unittest.TestCase):
     """TC-G1 to TC-G3, TC-G7, TC-G13 to TC-G18, TC-G20 to TC-G30 (TASK 116), TC-G31 (TASK 117)."""
 
@@ -146,6 +237,7 @@ class TestRebaseLinksGuard(unittest.TestCase):
         self.assertIn("lies outside the working directory", result.stderr)
         self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
 
+    @NEEDS_SYMLINK
     def test_g2_a_link_a_second_hard_link_or_git(self):
         victim = self.outside / "victim.md"
         victim.write_text(LINKED, encoding="utf-8")
@@ -171,6 +263,7 @@ class TestRebaseLinksGuard(unittest.TestCase):
         self.assertEqual(git.read_text(encoding="utf-8"), LINKED)
         self.assertEqual(hook.read_text(encoding="utf-8"), LINKED)
 
+    @NEEDS_SYMLINK
     def test_g2_from_a_subdirectory_and_through_a_firmlink(self):
         (self.root / ".git" / "hooks").mkdir(parents=True)
         hook = self.root / ".git" / "hooks" / "y.md"
@@ -207,6 +300,7 @@ class TestRebaseLinksGuard(unittest.TestCase):
         self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
         self.assertEqual(moved.read_text(encoding="utf-8"), REBASED)
 
+    @NEEDS_SYMLINK
     def test_g13_a_directory_that_resolves_outside(self):
         # base-fail: the base writes through the directory link.
         victim = self.outside / "victim.md"
@@ -217,6 +311,7 @@ class TestRebaseLinksGuard(unittest.TestCase):
         self.assertIn("resolves outside", result.stderr)
         self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
 
+    @NEEDS_SYMLINK
     def test_g14_a_directory_link_that_resolves_inside(self):
         moved = self.root / "docs" / "tasks" / "t.md"
         moved.write_text(LINKED, encoding="utf-8")
@@ -226,6 +321,8 @@ class TestRebaseLinksGuard(unittest.TestCase):
         self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
         self.assertEqual(moved.read_text(encoding="utf-8"), REBASED)
 
+    @NEEDS_SYMLINK
+    @unittest.skipIf(POSIX_PREMISE, "Windows resolves the `..` before the link (TASK 131 D22)")
     def test_g15_a_parent_segment_after_a_directory_link(self):
         # base-fail: the kernel resolves the link before the `..`; a lexical check does not.
         victim = self.outside / "victim.md"
@@ -261,6 +358,7 @@ class TestRebaseLinksGuard(unittest.TestCase):
             os.chdir(cwd)
         return code, err.getvalue()
 
+    @NEEDS_SYMLINK
     def test_g16_a_directory_swapped_around_the_open(self):
         # base-fail: the base reads and writes the outside file through the swapped directory.
         inside = self.root / "docs" / "x"
@@ -282,10 +380,11 @@ class TestRebaseLinksGuard(unittest.TestCase):
             return opener
         code, err = self.inprocess("docs/x/t.md", hooks)
         self.assertEqual(code, 2, err)
-        self.assertIn("is not the file at its real path", err)
+        self.assertIn(_o_nofollow_refusal("is not the file at its real path"), err)
         self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
         self.assertEqual((inside / "t.md").read_text(encoding="utf-8"), LINKED)
 
+    @NEEDS_SYMLINK
     def test_g17_a_file_swapped_for_a_link(self):
         # base-fail: the base follows the planted link. The inside link needs O_NOFOLLOW itself.
         other = self.root / "docs" / "other.md"
@@ -304,7 +403,7 @@ class TestRebaseLinksGuard(unittest.TestCase):
                     return opener
                 code, err = self.inprocess(f"docs/tasks/{name}.md", hooks)
                 self.assertEqual(code, 2, err)
-                self.assertIn("cannot open it", err)
+                self.assertIn(_o_nofollow_refusal("cannot open it"), err)
                 self.assertEqual(target.read_text(encoding="utf-8"), LINKED)
 
     def test_g18_a_second_hard_link_before_the_open(self):
@@ -343,6 +442,7 @@ class TestRebaseLinksGuard(unittest.TestCase):
         self.assertEqual(alias.read_text(encoding="utf-8"), LINKED)
         self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)
 
+    @unittest.skipIf(POSIX_PREMISE, "Windows refuses to replace a file that a descriptor holds")
     def test_g21_a_file_replaced_after_the_read(self):
         # base-fail: the base writes the rebased old text over the new file.
         moved = self.root / "docs" / "tasks" / "t.md"
@@ -366,23 +466,14 @@ class TestRebaseLinksGuard(unittest.TestCase):
         self.assertEqual(moved.read_text(encoding="utf-8"), fresh)
 
     def test_g22_a_platform_with_no_o_nofollow(self):
-        # base-fail: the base file mode needs no O_NOFOLLOW, so it rewrites the file.
+        # base-fail: the base refuses the platform (TASK 131 R2.4).
         moved = self.root / "docs" / "tasks" / "t.md"
         moved.write_text(LINKED, encoding="utf-8")
+        code, err = self.inprocess("docs/tasks/t.md", lambda real: real, before=_no_o_nofollow)
+        self.assertEqual(code, 0, err)
+        self.assertEqual(moved.read_text(encoding="utf-8"), REBASED)
 
-        @contextlib.contextmanager
-        def no_o_nofollow():
-            saved = os.O_NOFOLLOW
-            del os.O_NOFOLLOW
-            try:
-                yield
-            finally:
-                os.O_NOFOLLOW = saved
-        code, err = self.inprocess("docs/tasks/t.md", lambda real: real, before=no_o_nofollow)
-        self.assertEqual(code, 2, err)
-        self.assertIn("this platform has no O_NOFOLLOW", err)
-        self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)
-
+    @NEEDS_SYMLINK
     def test_g23_a_directory_moved_out_and_linked_back(self):
         # base-fail: the file keeps its inode, so only the directory check refuses it.
         inside = self.root / "docs" / "x"
@@ -563,9 +654,13 @@ class TestRebaseLinksGuard(unittest.TestCase):
         slot = ["--slot", "docs/TASK.md=docs/tasks/task-116-x.md"]
         with_slot = LINKED + "[t](TASK.md)\n"
         for name in ("x y", "a:b", "a)b", "plain-words"):
+            if NTFS_REFUSES & set(name):
+                continue                        # TASK 131 R6.5: a name that NTFS refuses
             (docs / name).mkdir()
             (docs / name / "ARCHITECTURE.md").write_text("# a\n", encoding="utf-8")
         for name in ("a b/x y.md", "m n/a.md", 'href="x.md"', "x.md"):
+            if NTFS_REFUSES & set(name):
+                continue
             (docs / name).parent.mkdir(exist_ok=True)
             (docs / name).write_text("# a\n", encoding="utf-8")
         text_held = "holds text that its authored link does not"
@@ -601,6 +696,8 @@ class TestRebaseLinksGuard(unittest.TestCase):
             ("docs", "docs/tasks", ["--dry-run"], '[a](href="x.md")\n',
              "the rewritten text holds a character that the text did not"))
         for from_dir, to_dir, extra, text, reason in refused:
+            if NTFS_REFUSES & set(from_dir) or (NTFS_REFUSES and 'href="' in text):
+                continue                        # its name, or the file it splices, NTFS refuses
             with self.subTest(from_dir=from_dir, to_dir=to_dir, extra=extra, text=text):
                 moved.write_text(text, encoding="utf-8")
                 result = _run(REBASE, ["docs/tasks/t.md", "--from", from_dir, "--to", to_dir,
@@ -634,6 +731,8 @@ class TestRebaseLinksGuard(unittest.TestCase):
         (docs / "plans").mkdir()
         (docs / "tasks" / "task-116-x.md").write_text("# Task 116: x\n", encoding="utf-8")
         for name in ("two/one/one/two/three.md", "one/one/a.md", "](x", "x", 'x">', "a/c.md"):
+            if NTFS_REFUSES & set(name):
+                continue                        # TASK 131 R6.5: a name that NTFS refuses
             (docs / name).parent.mkdir(parents=True, exist_ok=True)
             (docs / name).write_text("# a\n", encoding="utf-8")
         other = "names another <ID>-<slug> than its name"
@@ -660,6 +759,8 @@ class TestRebaseLinksGuard(unittest.TestCase):
             ("tasks/t.md", "docs", "docs/tasks", [], '<a href="](x">\n', splice),
             ("tasks/t.md", "docs", "docs/tasks", ["--dry-run"], "[r]: ](x\n", splice))
         for operand, from_dir, to_dir, extra, text, reason in refused:
+            if NTFS_REFUSES and text.startswith("<a href="):
+                continue                        # the spliced file's name NTFS refuses
             with self.subTest(operand=operand, from_dir=from_dir, extra=extra, text=text):
                 moved = docs / operand
                 moved.write_text(text, encoding="utf-8")
@@ -687,6 +788,342 @@ class TestRebaseLinksGuard(unittest.TestCase):
                 self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                 self.assertEqual(moved.read_text(encoding="utf-8"), rebased)
 
+    # --- TASK 131: a platform without O_NOFOLLOW, Windows among them ---------------------------
+
+    def test_w11_without_o_nofollow_a_swapped_link_is_refused(self):
+        # base-fail: the base refuses the platform before it opens the operand.
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+        victim = self.outside / "victim.md"
+        victim.write_text(LINKED, encoding="utf-8")
+
+        def hooks(real):
+            def opener(path, *args, **kwargs):
+                if os.path.abspath(path) == str(moved) and not moved.is_symlink():
+                    moved.unlink()
+                    moved.symlink_to(victim)
+                return real(path, *args, **kwargs)
+            return opener
+        if not _can_symlink():
+            self.skipTest("this process cannot make a symbolic link")
+        code, err = self.inprocess("docs/tasks/t.md", hooks, before=_no_o_nofollow)
+        self.assertEqual(code, 2, err)
+        self.assertIn("changed during the run", err)
+        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
+
+    def test_w11_without_o_nofollow_a_reparse_tag_is_a_link(self):
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+
+        @contextlib.contextmanager
+        def tagged():
+            with _no_o_nofollow(), _lstat_reporting(
+                    {"docs/tasks/t.md"}, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT,
+                    st_reparse_tag=JUNCTION):
+                yield
+        code, err = self.inprocess("docs/tasks/t.md", lambda real: real, before=tagged)
+        self.assertEqual(code, 2, err)
+        self.assertIn("is a link", err)
+        self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)
+
+    @WINDOWS_ONLY
+    def test_w12_a_junction_at_the_operands_directory(self):
+        victim = self.outside / "victim.md"
+        victim.write_text(LINKED, encoding="utf-8")
+        _junction(self.root / "docs" / "out", self.outside)
+        self.addCleanup(os.rmdir, self.root / "docs" / "out")
+        result = self.rebase("docs/out/victim.md")
+        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        self.assertIn("resolves outside", result.stderr)
+        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
+
+    def test_w13_the_file_mode_keeps_every_byte(self):
+        moved = self.root / "docs" / "tasks" / "t.md"
+        text = b"[a](ARCHITECTURE.md)\r\nline\x1a after the byte\r\nlast\n"
+        rebased = text.replace(b"(ARCHITECTURE.md)", b"(../ARCHITECTURE.md)")
+        moved.write_bytes(text)
+        result = self.rebase("docs/tasks/t.md")
+        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
+        self.assertEqual(moved.read_bytes(), rebased)
+        moved.write_bytes(text)
+        code, err = self.inprocess("docs/tasks/t.md", lambda real: real, before=_no_o_nofollow)
+        self.assertEqual(code, 0, err)
+        self.assertEqual(moved.read_bytes(), rebased)
+
+    def rebase_env(self, args, **env):
+        return subprocess.run([sys.executable, str(REBASE), *args], cwd=self.root,
+                              capture_output=True, timeout=60, env=dict(os.environ, **env))
+
+    def test_w14_any_stream_encoding_and_ascii_json(self):
+        # base-fail: the base prints the target with `print`, after the write, and its JSON is not
+        # ASCII (TASK 131 R3).
+        notes = self.root / "docs" / "notes"
+        notes.mkdir()
+        (notes / "n\u2192.md").write_text("# n\n", encoding="utf-8")
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text("[a](notes/n\u2192.md)\n", encoding="utf-8")
+        result = self.rebase_env(["docs/tasks/t.md", "--from", "docs", "--to", "docs/tasks"],
+                                 PYTHONIOENCODING="ascii")
+        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
+        self.assertIn(b"\\u2192", result.stdout)
+        result.stdout.decode("ascii")
+        result.stderr.decode("ascii")
+        moved.write_text("[a](notes/n\u2192.md)\n", encoding="utf-8")
+        result = self.rebase_env(["docs/tasks/t.md", "--from", "docs", "--to", "docs/tasks",
+                                  "--json"], PYTHONIOENCODING="utf-8")
+        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
+        self.assertTrue(all(byte < 128 for byte in result.stdout), "the JSON is not ASCII")
+        report = json.loads(result.stdout)
+        self.assertEqual(report["files"][0]["links"][0]["authored"], "notes/n\u2192.md")
+
+    def test_w15_an_operand_that_is_not_utf_8(self):
+        # base-fail: the base ends in a traceback, exit 1.
+        moved = self.root / "docs" / "tasks" / "t.md"
+        data = "[a](ARCHITECTURE.md)\n# \u0422\u0417\n".encode("cp1251")
+        moved.write_bytes(data)
+        result = self.rebase("docs/tasks/t.md")
+        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        self.assertEqual(json.loads(result.stderr.strip().splitlines()[-1])["error"],
+                         "docs/tasks/t.md: is not UTF-8")
+        self.assertEqual(moved.read_bytes(), data)
+
+    def test_w17_two_drives_are_outside(self):
+        # base-fail: a ValueError of `commonpath` ends the base in a traceback (TASK 131 R5.1).
+        module = _module(REBASE, "rebase_links_under_test")
+        same_drive = ValueError("Paths don't have the same drive")
+        with mock.patch("os.path.commonpath", side_effect=same_drive):
+            _text, records = module.rebase_document_links("[a](x.md)\n", "docs", "docs/tasks",
+                                                          str(self.root))
+        self.assertEqual([r.action for r in records], ["ESCAPES_ROOT"])
+        cwd = os.getcwd()
+        os.chdir(self.root)
+        self.addCleanup(os.chdir, cwd)
+        (self.root / "docs" / "tasks" / "t.md").write_text(LINKED, encoding="utf-8")
+        for call, reason in ((1, "lies outside the working directory"),
+                             (2, "its directory resolves outside the working directory")):
+            with self.subTest(call=call):
+                calls, real = [], os.path.commonpath
+
+                def commonpath(paths, call=call, calls=calls, real=real):
+                    calls.append(paths)
+                    if len(calls) == call:
+                        raise same_drive
+                    return real(paths)
+                with mock.patch("os.path.commonpath", side_effect=commonpath):
+                    self.assertEqual(module._refuse_operand("docs/tasks/t.md"), reason)
+        fd = os.open("docs/tasks/t.md", os.O_RDONLY)
+        self.addCleanup(os.close, fd)
+        with mock.patch("os.path.commonpath", side_effect=same_drive):
+            with self.assertRaises(module._Unsafe) as caught:
+                module._check_descriptor(fd, "docs/tasks/t.md", str(self.root))
+        self.assertEqual(str(caught.exception),
+                         "its directory resolves outside the working directory")
+
+    @WINDOWS_ONLY
+    def test_w17_an_operand_and_a_link_on_another_drive(self):
+        drive = os.path.splitdrive(str(self.root))[0].upper()
+        other = "Y:" if drive == "Z:" else "Z:"
+        result = self.rebase(f"{other}/docs/x.md")
+        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        self.assertIn("lies outside the working directory", result.stderr)
+        module = _module(REBASE, "rebase_links_under_test")
+        _text, records = module.rebase_document_links("[a](\\\\server\\share\\x.md)\n", "docs",
+                                                      "docs/tasks", str(self.root))
+        self.assertEqual([r.action for r in records], ["ESCAPES_ROOT"])
+
+    def test_w18_from_and_to_with_a_drive_or_a_root(self):
+        # base-fail: the base passes a drive with no root, and from Python 3.13 a root with no
+        # drive (TASK 131 R5.2).
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+        for option in ("--from", "--to"):
+            with self.subTest(option=option):
+                args = {"--from": "docs", "--to": "docs/tasks"}
+                args[option] = "/x"
+                result = _run(REBASE, ["docs/tasks/t.md", "--from", args["--from"], "--to",
+                                       args["--to"]], self.root)
+                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+                self.assertIn(f"{option} does not lie inside the working directory",
+                              result.stderr)
+        module = _module(REBASE, "rebase_links_under_test")
+        windows = types.SimpleNamespace(path=ntpath, sep="\\")
+        with mock.patch.object(module, "os", windows):
+            for value, leaves in (("\\x", True), ("/x", True), ("D:x", True), ("D:\\x", True),
+                                  ("docs", False), ("docs\\tasks", False)):
+                with self.subTest(value=value):
+                    self.assertEqual(module._leaves_tree(value), leaves)
+        self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)
+
+    @WINDOWS_ONLY
+    def test_w18_a_drive_or_a_root_on_windows(self):
+        for value in ("\\x", "D:x"):
+            with self.subTest(value=value):
+                result = _run(REBASE, ["docs/tasks/t.md", "--from", value, "--to", "docs/tasks"],
+                              self.root)
+                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+                self.assertIn("--from does not lie inside the working directory", result.stderr)
+
+    def test_w24_each_open_of_the_file_mode_passes_o_binary(self):
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+        bit, flags_seen = _unused_open_bit(), []
+
+        def hooks(real):
+            if real is not os.open:
+                return real
+
+            def opener(path, flags, *args, **kwargs):
+                if os.path.abspath(path) == str(moved):
+                    flags_seen.append(flags)
+                return real(path, flags & ~bit, *args, **kwargs)
+            return opener
+
+        @contextlib.contextmanager
+        def binary():
+            with _no_o_nofollow(), mock.patch.object(os, "O_BINARY", bit, create=True):
+                yield
+        code, err = self.inprocess("docs/tasks/t.md", hooks, before=binary)
+        self.assertEqual(code, 0, err)
+        self.assertEqual(len(flags_seen), 2, "the read and the write each open the file")
+        self.assertTrue(all(flags & bit for flags in flags_seen), "an open drops O_BINARY")
+        nonblock = getattr(os, "O_NONBLOCK", 0)
+        self.assertTrue(all(flags & nonblock == nonblock for flags in flags_seen),
+                        "an open drops O_NONBLOCK")
+
+    def test_w26_each_module_keeps_its_own_helpers(self):
+        # TASK 131 R2.6: a staged copy of one module runs beside the base of another (D12).
+        for path, names in ((ARCHIVE_MOVE, {"_is_link"}),
+                            (REBASE, {"_is_link", "_open_nofollow"}),
+                            (SLOT, {"_is_link", "_open_nofollow"})):
+            with self.subTest(module=path.name):
+                tree = ast.parse(path.read_text(encoding="utf-8"))
+                defined = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
+                self.assertLessEqual(names, defined)
+                borrowed = [node.attr for node in ast.walk(tree)
+                            if isinstance(node, ast.Attribute) and node.attr in names]
+                self.assertEqual(borrowed, [], "a helper read from another module")
+
+    @WINDOWS_ONLY
+    def test_w27_a_link_written_with_a_backslash(self):
+        (self.root / "x.md").write_text("# x\n", encoding="utf-8")
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text("[a](..\\x.md)\n", encoding="utf-8")
+        result = self.rebase("docs/tasks/t.md")
+        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        self.assertIn("docs/tasks/t.md:1", result.stderr)
+        self.assertEqual(moved.read_text(encoding="utf-8"), "[a](..\\x.md)\n")
+
+    # --- the fix of round 1 of stage 2 (TASK 131 D24 to D26) -----------------------------------
+
+    @unittest.skipUnless(hasattr(os, "mkfifo"), "no os.mkfifo")
+    def test_w37_without_o_nofollow_a_fifo_is_never_opened(self):
+        fifo = self.root / "docs" / "tasks" / "f.md"
+        os.mkfifo(fifo)
+        opened = []
+
+        def hooks(real):
+            if real is not os.open:
+                return real
+
+            def opener(path, *args, **kwargs):
+                if os.path.abspath(path) == str(fifo):
+                    opened.append(path)             # the open would block: fail it instead
+                    raise OSError(errno.EAGAIN, "the test refuses to open the FIFO")
+                return real(path, *args, **kwargs)
+            return opener
+        code, err = self.inprocess("docs/tasks/f.md", hooks, before=_no_o_nofollow)
+        self.assertEqual(code, 2, err)
+        self.assertIn("is not a regular file", err)
+        self.assertEqual(opened, [], "the FIFO was opened")
+
+    def test_w38_no_descriptor_path_and_no_fcntl_off_posix(self):
+        imported, real_import = [], builtins.__import__
+
+        def spy(name, *args, **kwargs):
+            imported.append(name)
+            return real_import(name, *args, **kwargs)
+        for path, name in ((REBASE, "rebase_links_under_test"), (SLOT, "slot_links_under_test")):
+            with self.subTest(module=path.name):
+                module = _module(path, name)
+                imported.clear()
+                with mock.patch.object(os, "name", "nt"), \
+                        mock.patch("builtins.__import__", side_effect=spy):
+                    self.assertIsNone(module._descriptor_path(0))
+                self.assertNotIn("fcntl", imported)
+
+    def test_w39_an_operand_that_names_a_stream(self):
+        module = _module(REBASE, "rebase_links_under_test")
+        windows = types.SimpleNamespace(path=ntpath, sep="\\")
+        with mock.patch.object(module, "os", windows):
+            self.assertTrue(module._names_stream("docs/a.md:b.md"))
+            self.assertTrue(module._names_stream("docs/tasks:b.md"))
+            self.assertFalse(module._names_stream("C:\\repo\\docs\\a.md"))
+            self.assertFalse(module._names_stream("docs/tasks/t.md"))
+        with mock.patch.object(module, "os", types.SimpleNamespace(path=posixpath, sep="/")):
+            self.assertFalse(module._names_stream("docs/a.md:b.md"),
+                             "a colon names no stream where paths have no drives")
+        # The file mode asks the check of each operand.
+        (self.root / "docs" / "tasks" / "t.md").write_text(LINKED, encoding="utf-8")
+        cwd = os.getcwd()
+        os.chdir(self.root)
+        self.addCleanup(os.chdir, cwd)
+        with mock.patch.object(module, "_names_stream", return_value=True):
+            self.assertEqual(module._refuse_operand("docs/tasks/t.md"),
+                             "names an alternate stream of a file")
+
+    def test_w41_a_crlf_document_with_a_fence_and_a_code_span(self):
+        # base-fail: at the base no fence closes on CR LF, so the links after it stay.
+        moved = self.root / "docs" / "tasks" / "t.md"
+        text = (b"[a](ARCHITECTURE.md)\r\n\r\n```\r\n[x](ARCHITECTURE.md)\r\n```\r\n\r\n"
+                b"[b](ARCHITECTURE.md)\r\n\r\n`span\r\n\r\n[c](ARCHITECTURE.md) and `x`\r\n")
+        moved.write_bytes(text)
+        result = self.rebase("docs/tasks/t.md")
+        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
+        rebased = moved.read_bytes()
+        self.assertEqual(rebased.count(b"(../ARCHITECTURE.md)"), 3, rebased)
+        self.assertIn(b"```\r\n[x](ARCHITECTURE.md)\r\n```", rebased)
+
+    def test_w42_a_unc_repo_root_is_refused_before_any_call(self):
+        # base-fail: the base resolves `--repo-root` with `os.path.realpath` first (TASK 131 R12).
+        module = _module(REBASE, "rebase_links_under_test")
+        windows = types.SimpleNamespace(path=ntpath, sep="\\")
+        with mock.patch.object(module, "os", windows):
+            for value in UNC_PATHS:
+                with self.subTest(value=value):
+                    self.assertTrue(module._unc(value))
+            for value in ("C:\\repo", "docs", "\\x", "."):
+                with self.subTest(value=value):
+                    self.assertFalse(module._unc(value))
+        with mock.patch.object(module, "os", types.SimpleNamespace(path=posixpath, sep="/")):
+            for value in UNC_PATHS:
+                with self.subTest(value=value, path="posixpath"):
+                    self.assertFalse(module._unc(value), "no drives, no UNC path, on POSIX")
+        (self.root / "docs" / "tasks" / "t.md").write_text(LINKED, encoding="utf-8")
+        resolved = []
+        real_realpath = os.path.realpath
+        cwd = os.getcwd()
+        os.chdir(self.root)
+        self.addCleanup(os.chdir, cwd)
+        err = io.StringIO()
+        with mock.patch.object(module, "_unc", return_value=True), \
+                mock.patch("os.path.realpath",
+                           side_effect=lambda p, *a, **k: (resolved.append(p),
+                                                          real_realpath(p, *a, **k))[1]), \
+                contextlib.redirect_stderr(err):
+            code = module._main(["docs/tasks/t.md", "--from", "docs", "--to", "docs/tasks",
+                                 "--repo-root", "//host/share"])
+        self.assertEqual(code, 2, err.getvalue())
+        self.assertIn("--repo-root is a UNC or device path", err.getvalue())
+        self.assertEqual(resolved, [], "a path was resolved before the refusal")
+
+    @WINDOWS_ONLY
+    def test_w42_a_unc_repo_root_on_windows(self):
+        (self.root / "docs" / "tasks" / "t.md").write_text(LINKED, encoding="utf-8")
+        result = _run(REBASE, ["docs/tasks/t.md", "--from", "docs", "--to", "docs/tasks",
+                               "--repo-root", "\\\\localhost\\nowhere"], self.root)
+        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        self.assertIn("--repo-root is a UNC or device path", result.stderr)
+
 
 class TestInboundGuard(unittest.TestCase):
     """TC-G8 to TC-G12 (TASK 115) and TC-G19 (TASK 116 R7.4): `--inbound` writes only regular
@@ -718,6 +1155,7 @@ class TestInboundGuard(unittest.TestCase):
         self.assertEqual(sub.read_text(encoding="utf-8"), SUBTASK)
         self.assertEqual((self.root / "alias.md").read_text(encoding="utf-8"), SUBTASK)
 
+    @NEEDS_SYMLINK
     def test_g9_a_symbolic_link_to_a_file_outside(self):
         victim = self.outside / "victim.md"
         victim.write_text(SUBTASK, encoding="utf-8")
@@ -751,7 +1189,7 @@ class TestInboundGuard(unittest.TestCase):
         import importlib.machinery
         tools = self._tools_copy()
         planted = ("__future__", "re", "typing", "argparse", "json", "difflib", "subprocess",
-                   "msvcrt", "_winapi")
+                   "msvcrt", "_winapi", "fcntl")
         for name in planted:
             sentinel = self.outside / f"sentinel-{name}"
             (tools / f"{name}.py").write_text(f"open({str(sentinel)!r}, 'w').close()\n",
@@ -777,7 +1215,7 @@ class TestInboundGuard(unittest.TestCase):
         # and the path as called then differs from the real one (TASK 128 R1.3).
         tools = self._tools_copy()
         planted = ("__future__", "re", "typing", "argparse", "json", "difflib", "subprocess",
-                   "msvcrt", "_winapi")
+                   "msvcrt", "_winapi", "fcntl")
         for name in planted:
             sentinel = self.outside / f"sentinel-{name}"
             (tools / f"{name}.py").write_text(f"open({str(sentinel)!r}, 'w').close()\n",
@@ -857,10 +1295,11 @@ class TestInboundGuard(unittest.TestCase):
                 state.pop("back")()
         return refusal, away / "t.md", original, state["swaps"]
 
+    @NEEDS_SYMLINK
     def test_g19_a_directory_swapped_around_the_inbound_open(self):
         # base-fail: the base writes the outside file; its post-write check refuses only a swap.
         module = _module(SLOT, "slot_links_under_test")
-        reasons = {"swap": "is not the file at its real path",
+        reasons = {"swap": _o_nofollow_refusal("is not the file at its real path"),
                    "move": "its directory resolves outside the working directory",
                    "three": "its directory resolves outside the working directory"}
         for case, reason in reasons.items():
@@ -875,6 +1314,39 @@ class TestInboundGuard(unittest.TestCase):
                     self.assertGreaterEqual(swaps, 1, "the realpath hook never swapped")
 
 
+    def test_w16_no_pyc_under_a_relative_null_device(self):
+        # base-fail: the base looks a sibling's `.pyc` up under `nul/rebase-links-pycache/`, a path
+        # relative to the working directory where `os.devnull` is `nul` (TASK 131 R4).
+        tools = self._tools_copy()
+        site = self.outside / "site"
+        site.mkdir()
+        report = self.outside / "prefix.txt"
+        (site / "sitecustomize.py").write_text(
+            "import atexit, os, sys\n"
+            "os.devnull = 'nul'\n"
+            f"atexit.register(lambda: open({str(report)!r}, 'w', encoding='utf-8')"
+            ".write(str(sys.pycache_prefix)))\n", encoding="utf-8")
+        sentinel = self.outside / "sentinel-nul-pyc"
+        evil = self.outside / "evil.py"
+        evil.write_text(f"open({str(sentinel)!r}, 'w').close()\n", encoding="utf-8")
+        head = os.path.splitdrive(str(tools))[1].lstrip("\\/")
+        cache = os.path.join(str(self.root), "nul", "rebase-links-pycache", head)
+        if os.name == "nt":
+            cache = "\\\\?\\" + cache
+            self.addCleanup(shutil.rmtree, "\\\\?\\" + str(self.root / "nul"))
+        os.makedirs(cache)
+        py_compile.compile(str(evil), cfile=os.path.join(
+            cache, f"slot_links.{sys.implementation.cache_tag}.pyc"),
+            invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
+        result = subprocess.run([sys.executable, str(tools / REBASE.name), "--inbound", "--task",
+                                 "docs/tasks/task-112-x.md"], cwd=self.root, capture_output=True,
+                                text=True, timeout=60, env=dict(os.environ, PYTHONPATH=str(site)))
+        self.assertIn(result.returncode, (0, 3), result.stdout + result.stderr)
+        self.assertFalse(sentinel.exists(), "a .pyc under the relative null device was read")
+        prefix = report.read_text(encoding="utf-8")
+        self.assertTrue(prefix.startswith(os.path.realpath(tools / REBASE.name)), prefix)
+
+
 class TestInitSkillGuard(unittest.TestCase):
     """TC-G4 to TC-G6."""
 
~~~~

`git apply --whitespace=nowarn` of the patch exited 0. Step 4: each final file hashes to its staged
copy and keeps the mode `644`, and `git apply --check -R` passes. Step 5: `rm --` of each staged
copy, each exit 0:
- `.agent/tools/staged_archive_move.py`, `.agent/tools/staged_rebase_links.py`,
  `.agent/tools/staged_slot_links.py`, `.agent/tools/staged_task_id_tool.py`;
- `.agent/tools/staged_test_rebase_links.py`, `.agent/tools/staged_test_slot_links.py`,
  `.agent/tools/staged_test_task_id_tool.py`;
- `tests/staged_archive_move.py`, `tests/staged_script_guards.py`.

### J3 — the gates after stage 3

Each run below ran under the guard, with `.agent/sessions/` unchanged:
- `gates.py` from the repository root: 22 of 22 steps pass. The step of TASK R7.1 in both Windows
  jobs: 388 passed and 10 skipped. The tooling step: 606 passed and 4 skipped;
- `regcheck.py`: 0 warn on each changed document, this record and the WI-39 record among them.
  `bytescan.py`: each of the 23 paths of `git status` is clean, and each is declared;
- `check.py` for each command below, each pair of listings equal, each exit code the one the PLAN
  names:
  - the ten commands of G1: `68c87931dedb` and `e97c6d7e4fe6` exit 0 from the root and from
    `tests/`, 802 passed and 8 skipped, and from `.agent/tools/`, 274 passed and 2 skipped. From
    `.agent/` both exit 2 with the 21 errors of the base. `ca2c33383ded` and `a8ddacaa1aa9` exit 0;
  - the committed rule `4e5ef4a6bcd5`: no operand, exit 2; the two pairs that `_parse` refuses,
    exit 1 each;
  - the committed rule `ce6cfae3843d`: `--help`, exit 0. The file mode with `--dry-run` on the
    archive of TASK 130, exit 0, and with `--json`, exit 0. The operand `README.md`, exit 2, and
    `--from /x`, exit 2. The inbound mode of §1 with `--dry-run`, exit 3, and with `--json`,
    exit 3;
  - the committed rule `274abb280e58`: the slug of TASK 131 with `--proposed-id 131` and
    `--no-correction`, exit 0;
  - the local rules `bcddea47eb1b` and `20890709883a` from this root, and the user rules
    `f23abd494daf` and `0b6b1d85891c` from the root of the sibling checkout, each with the
    command that it approves: exit 0 each;
- `rules_check.py compare`: the local and the user settings files are unchanged, with no new rule.

### J4 — stage 4, at the fingerprint `329cf8088974`: code review APPROVED, security audit PASS

Both reviewers read the brief of stage 4, computed `329cf8088974` at their start and at their end,
and ran the tests in the repository with `-B` and `-p no:cacheprovider`. The scratchpad held no
file of a reviewer afterwards, and the fingerprint was unchanged. Each confirmed that the nine final
files hash to the staged copies of round 3 with the mode `644`, that `git diff` of them from the
base equals the patch, and that `git apply --check -R` passes. Neither found a staged module that a
file of code, test, workflow or settings names. The step of TASK R7.1: 388 passed and 10 skipped.
Each committed rule runs its final file, in forms that write nothing. The security scan ran,
`scan_status: findings`, with none at CRITICAL or HIGH in the files of the change.

Their findings, each LOW:
- F1 and S4-1: two ignored files of bytecode, `.agent/tools/__pycache__/staged_rebase_links.cpython-314.pyc`
  and `staged_task_id_tool.cpython-314.pyc`, written at 21:44 during the fix of round 1 by a check
  that imported a staged copy without `-B`. Python reads neither without its source. The run removed
  both with `rm --` after the review;
- F2: D29 named the double blank line by the staged name of its file;
- F3: §9 said that `os.path` is `posixpath` on any Python of MSYS2; that holds for the Python of the
  MSYS2 runtime only;
- S4-2: an archive that another process removes after a failed try of the undo ends with the
  message `… no longer holds the file this run made, so that file is kept`, which RW11 did not
  name.

TASK revision 10 corrects D29, §9 and RW11 in place. Stage 4 passed.

## Retro (§6, PLAN K1)

The run id `framework-upgrade-task-131-archive-chain-windows` was claimed at the start of the run.
The retro question listed four observed candidates. They were the hang of a red run on a FIFO,
the read of R6.7 that missed premises of Windows twice, an unquoted heredoc of zsh, and records
behind the facts. The operator answered "ничего". The retro filed no record, and the claim was released, exit
0.
