# Framework Audit 128 — A CI job runs the session state on Windows, and the six records of the TASK 127 retro close

- **Task:** 128 `windows-ci-and-retro-records`. It archives to
  `docs/tasks/task-128-windows-ci-and-retro-records.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1.
- **Date:** 2026-10-26. **Base revision:** `931d5b1c2ceaf8b33e8dca0e64aacdf7c1aaac1b`, clean tree
  at start (TASK 127, committed by the operator as `931d5b1`).
- **Source:** the retro of TASK 127, and the operator's answer on the order of the Windows series
  (TASK D1, D2).

## 0. Emergency Bypass

`[BYPASS_TIER_PROTECTION]`: `skill-session-state` is a TIER 0 skill. The change edits its
`SKILL.md` in place and its script and test module through the stage-3 patch (TASK R2, R3, R4). It
removes no TIER 0 skill and no load of one.

## Archive (§1)

TASK 127 and PLAN 127 archived under ID 127:
- `task_id_tool.py "session-state-windows" --proposed-id "127" --no-correction`: `generated`,
  `task-127-session-state-windows.md`;
- both moves `"ok": true`, method `link`;
- Step 5.5: `0 rewritten / 0 needing review`, exit 0; Step 7.6.5: one `SLOT_RESOLVED`, exit 0;
- Step 8 with `--since c6666c4a6cd251d7f0327ad0df57dd706a3104e3`: exit 3. It lists the two
  `INBOUND` records of old changelog entries that TASK 127 also listed, which carry no reason and
  stay. Step 8 rewrote no file.

## Research (§1)

The facts of TASK §8 come from reading the tree. The retro claim
`framework-upgrade-windows-ci-and-retro-records` was taken at the start of the run, and the base
was recorded in the session state before §1.

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

The reviewer, a `task-reviewer` agent with no shell, read the TASK at SHA-256 `9a3c1fa1c37a…` and
wrote nothing. The fingerprint of the tree was `0e0bbd5303a7`, this record included. Its blocking
finding:
- M1: the Windows job fails its first run. `S/scripts/update_state.py:63@931d5b1` joins
  `.agent/sessions` with a `/`, so on Windows TC-11 meets a path with both separators. A7 ran the
  steps of the job on macOS only, and no criterion covered its first run.

Its other findings:
- m1: TC-01 never runs on Windows, and no test makes two runs compete for `msvcrt.locking`;
- m2: a fixed `0o644` contradicts "the mode kept" of the RTM and loosens a file set to `0o600`.
  `os.fchmod` exists on Windows from 3.13 only, and the floor is 3.11;
- m3: `os.replace` fails on Windows while another process holds the file without
  `FILE_SHARE_DELETE`. The exclusive creation and the close before the move were not required;
- m4: the check by path leaves a window at `.agent/sessions`, at the lock file and at the read;
- m5: no test reaches the branch of the reparse point, and TC-19 and TC-20 lacked a skip where no
  link can be created;
- m6: TC-07 checks only the calls of `open` by name, and reads a mode `"x"` as a read;
- m7: the `grep` of A5 meets the changelogs, `.git/index` and `.agent/feedback/`;
- m8: TC-C4 pins version 1.2, and R8.2 and R8.3 had no criterion;
- m9: a link set on purpose at the state fails every phase boundary. No remedy was stated, and no
  check covered the other checkouts;
- m10: the WI-39 record still names both scripts as closed, and its recipe has the weakness of
  ARC-13;
- m11: R4 had no test of the skip, and TC-20 to TC-22 no mutation. The use cases lacked actors
  and alternatives, UC-3's postcondition was false beside a live session, and §9 dropped the run
  of TASK 127 UC-1 that TASK 127 §9 deferred;
- N1 to N9, notes:
  - every reparse point was refused, a cloud placeholder among them;
  - a coordinate in §1 had no pin, and R8.4 named four scripts where allow rules run three;
  - `_scratch` has a second module object, and TC-H1 needs a child process;
  - the checkout lacked `persist-credentials: false`. In PowerShell an early failure in a block
    does not fail its step;
  - §9 gave the two archive scripts to TASK 129. A deleted file has no staged copy at stage 3, and
    a failed stage 3 left the records `fixed`;
  - §0 of this record needs `[BYPASS_TIER_PROTECTION]`, which it holds;
  - the code page of the runner is cp1252.

Before the task, one line each:
- a FIFO at `latest.yaml` blocks the read while the lock is held;
- `tests/_scratch.py:61@931d5b1` `os.kill(pid, 0)` sends `CTRL_C_EVENT` on Windows;
- `sweep_session` removes the shared root with `rmdir`, which can race another session between
  `_ensure_root` and `mkdtemp`.

Its check of the staging: the eight pairs cover every edited file that an allow rule or
`tests/run_tests.py` runs or imports. No staged name is collected by a runner or named by a rule.

TASK revision 2 applies M1, m1 to m11 and N1 to N9:
- M1: R7.3 builds `.agent/sessions` with `os.path.join` (D8). R7.5 reads each test of the jobs
  for an assumption of POSIX, and R7.7 names who reads the first run and what a red job starts
  (D12);
- m1: TC-01 runs on every platform, and TC-24 holds the real lock on Windows;
- m2: the new file keeps the permission bits of the old one on POSIX (D10). The jobs run 3.11 and
  3.14 (D3);
- m3: R2.5 tries a move or a removal 10 times on `PermissionError` (D9). R2.4 creates the
  temporary file with mode `"x"` and closes it before the move;
- m4: `O_NOFOLLOW` on POSIX for the lock file, the read and the temporary file. D6 states the
  window left at `.agent/sessions` as accepted, with its reason;
- m5: TC-20 adds a junction on Windows, and TC-28 reaches the branch of the reparse point on
  every platform. TC-19 and TC-20 skip where no link can be made;
- m6: TC-07 treats `x`, `a` and `+` as a write, and fails on `os.fdopen`, `io.open` and
  `codecs.open`;
- m7: A5 uses `git grep` and leaves out `docs/` and both changelogs;
- m8: TC-C4 checks version 1.3 and the words of R8.3, and TC-C5 those of the guide; A11 covers
  R8.3 and R8.4;
- m9: the guide's §6 and the changelog state the remedy, and R8.9 searches the checkouts beside
  this repository;
- m10: R8.2 adds a progress blockquote to the WI-39 record;
- m11: TC-26 tests the helper of R4.1, and TC-20 to TC-22 name their mutation. The use cases gain
  actors and alternatives, UC-3's postcondition allows a live session, and UC-1 names the run of
  TASK 127 UC-1;
- N1: a reparse point is a link only when its tag is a name surrogate (D11);
- N2, N3, N6, N9: the pin of `rebase_links.py:80`, three scripts in the Why of R8.5, "the Windows
  port" in §9, and cp1252;
- N4: R6.1 counts once per module object, and TC-H1 runs in a child process;
- N5: each job sets `persist-credentials: false` and the shell bash;
- N7: the PLAN's stage 3 checks that the removed file is absent, and its Failure path restores
  the six records.

Two findings before the task enter the task: D13 refuses an entry of another kind, and R6.4 makes
the root again, since `atexit` adds sweeps. The stale sweep's `os.kill` on Windows stays a finding
before the task (§9).

The checks of revision 2, as their tools print them:
- `scan_register.py docs/TASK.md --sections --terms docs/ARCHITECTURE.md`: `0 warn / 1 info`;
  `sentences : 290, mean 11.6, max 31 (limit 35)`;
- `check_positional_refs.py --all docs/TASK.md`: `OK: 2 of 6 reference(s) in 1 document(s)
  resolve against the working tree (4 pinned, not checked).`;
- `bytescan.py` of the TASK and of this record: clean. The TASK hashes to `fdda6c043f8b…`.

### Round 2 — TASK revision 2: PASS

The reviewer, resumed, read the fingerprint `3a3e338d1704` and wrote nothing. It confirmed each
fix of round 1 and found no blocking finding. It confirmed:
- the order of the checks against the lock, the flags that `open` hands its opener, mode `"x"`
  with an opener on 3.11, and `PermissionError` for WinError 5 and 32;
- that no test or script that reads the workflow conflicts with the two jobs;
- that TC-24 can pass on `windows-latest`, and that TC-27 and TC-28 can fail on macOS as their
  mutations state.

Its findings to fix before planning:
- m1: a handler that reads the globals of `_scratch` at exit removes the real `tests/.scratch/`
  through the second module object of `tests/test_scratch_hygiene.py`, whose tearDown restores
  the real root;
- m2: R2.4 did not require the opener of the write to keep the flags of `open`. Without
  `O_BINARY`, the C runtime of Windows writes CRLF;
- m3: R2.2 invited a guard by `os.name`, under which TC-28 cannot pass on macOS. The FIFO case of
  TC-28 had no mutation;
- m4: no test failed when `O_NOFOLLOW` was removed. A2 depended on the run after the push, and
  R7.7 and R8.4 had no criterion;
- N1 to N7, notes:
  - D6 did not name the windows that Windows keeps at the lock file and at the read;
  - R2.1 said "Nothing is written", where a refusal at `latest.yaml` follows the creation of the
    lock file;
  - the close of the temporary file before its removal, and a FIFO swapped in after the check;
  - TC-24 unlocks before it closes, and TC-26 lacked a `.git` file;
  - `gates.py` and pip outside a virtual environment.

TASK revision 3 applies m1 to m4 and N1 to N7 with no further round, on the precedent of TASK 122
to TASK 127:
- m1: R6.1 binds the handler to its directory and its root, and TC-H1 checks that a second root
  stays;
- m2: R2.3 names one opener for the read and the write. It adds `O_NOFOLLOW` to the flags that it
  receives;
- m3: R2.2 reads both attributes with `getattr` on every platform, and TC-28 names the check of
  the kind;
- m4: TC-29. A2 drops TC-24, and A12 gives the run after the push to TASK 129. A13 checks the
  final report, and A11 the **Changed** part;
- N1 and N4: D6 and D13 name the windows they accept. N2 and N3: R2.1 and R2.6. N5 and N6: TC-24
  and TC-26. N7: A7.

The checks of revision 3, as their tools print them:
- `scan_register.py docs/TASK.md --sections --terms docs/ARCHITECTURE.md`: `0 warn / 1 info`;
  `sentences : 312, mean 11.8, max 31 (limit 35)`;
- `check_positional_refs.py --all docs/TASK.md`: `OK: 2 of 6 reference(s) in 1 document(s)
  resolve against the working tree (4 pinned, not checked).`;
- `bytescan.py`: clean. The TASK hashes to `63bfdefea4e0…`.

## Architecture (§2.1)

`docs/ARCHITECTURE.md` keeps its text. Its two statements of the session-state lock, lines 120 and
215, stay true: the lock file and `fcntl` or `msvcrt` do not change. The write through a temporary
file, the refusal of a link, the filter of the archive scripts and the CI jobs add no component,
no interface and no data model.

## Planning (§2.2)

PLAN revision 1 declares 32 paths. Each of the 23 tracked paths passes
`git ls-files --error-unmatch`, and each of the 9 new paths gives `git check-ignore -q` exit 1.

The reading of the settings at §2.2, `rules_check.py read`, saved as `rules_128.json` in the
scratchpad:
- `.claude/settings.local.json`: 50 allow rules, SHA-256 `48bbe25e64356acb…`;
- `~/.claude/settings.json`: 326 allow rules, SHA-256 `1abd385154c514ae…`.

Both files hash as at the reading of TASK 127. The rules of either file that run files of this
change, named by the SHA-256 prefix of the rule's text:

| Rule | File | What of the change it runs |
| :--- | :--- | :--- |
| `ca2c33383ded254c` | local | from the root: `tests/_scratch.py`, three test modules of `tests/`, the archive scripts |
| `ca2c33383ded254c` | local | from `S/scripts/`: the test module of `S/` and the script |
| `f42576bf00a2603c` | local | `tests/_scratch.py`, through `tests/conftest.py` |
| `7e089e2b18fca974` | local | `tests/_scratch.py`, through `tests/conftest.py` and `tests/test_tool_runner.py` |
| `9fa5cad71668c6f7` | user | from `S/`, the test module of `S/` and the script |
| 15 rules | user | `update_state.py`, by an absolute path in a sibling checkout whose skill directory links into this repository |

The 15 rules: `ed9b841f7a28c589`, `c9d9a3441dddbd5b`, `2ebfd9ef5b8ec4ac`, `f6edd29f20df2611`,
`9dacc267acf0870d`, `b5816440fd190330`, `9ef6002cd601ad92`, `4d7430ff38747bab`,
`16c51563e1e6f68c`, `9fcb20f312f9bc80`, `e6248792a91c56bf`, `89419a8af553ca90`,
`cafa3967b5c114ee`, `838a9db8fdcb691a` and `ad94d8ffaa294f28`.

The other rules that the search found run no file of the change:
- the local `6d2a76ee469828a5` names a path that does not exist;
- user rules run the unit tests of other repositories, or `discover -s` with a directory that
  this repository lacks; one runs `awk`.

The committed rules that run files of the change are `python -m pytest` and `python3 -m pytest`,
the rules of the three scripts, and `python3 tests/run_tests.py`. `python` and `python3` resolve
to one interpreter here, so the runs of `python3 -m pytest` stand for both, as in TASK 127.

A preview of PLAN H5 found 18 checkouts beside this repository that hold `.agent/sessions`, and no
link at the three entries of TASK R2.1 in any of them. H5 runs the search again before stage 3.

The checks of PLAN revision 1, as their tools print them:
- `scan_register.py docs/PLAN.md --sections --terms docs/ARCHITECTURE.md`: `0 warn / 0 info`;
  `sentences : 277, mean 11.9, max 29 (limit 35)`;
- `check_positional_refs.py --all docs/PLAN.md`: `OK: 11 of 12 reference(s) in 1 document(s)
  resolve against the working tree (1 pinned, not checked).`;
- `plan_gantt.py docs/PLAN.md --check docs/PLAN.md`: `docs/PLAN.md: plan chart is current`;
- `bytescan.py`: clean.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: PASS

The reviewer, a `plan-reviewer` agent with no shell, read the fingerprint `6f9a0c63af64` and wrote
nothing. It found Stub-First, atomicity and the dependencies in order, each requirement and
criterion decided by a step, the declared paths complete, and the claims of B1 right against the
base code. Its findings to fix before execution:
- m1: `git worktree list` names two prunable registrations, `head` and `clean`, which point into
  scratchpads of earlier sessions, so A1 failed on the current state;
- m2: the path of an `INCOMPLETE` audit as the only failure restored the six records, and no step
  closed them again before the patch landed;
- m3: Failure step 5 left out the WI-39 record;
- m4: no run of J3 reached the refusal of TASK R2.1;
- m5: the calls of the script in the test process lay outside the guard, B1 ran in the live tree,
  and the guard hashed two files only;
- m6: `tools-128/plan_128_draft.md`, a draft of the PLAN, lay in the scratchpad, and no step
  removed the copies that reviewers leave there;
- m7: H2 lacked the mutations of `io.open` and `codecs.open` for TC-07;
- N1 to N12, notes:
  - three cells of the coverage tables, and the wording of the guard for the two SS-1 tests;
  - the checkout in H4's read, and the caveats of B1 for TC-21, TC-25 and TC-23;
  - the bare pytest runs from other directories, and the shared name `staged_archive_move.py`;
  - the details of J3 item 4, the scope of H5, and the review rounds outside the guard;
  - `git worktree list` after `wt.sh remove`, and no test of the tries of a removal;
  - the wildcard of the two local rules.

Before the task: the two prunable registrations of worktrees, `head` and `clean`.

PLAN revision 2 and TASK revision 4 apply them with no further round, on the precedent of TASK 122
to TASK 127:
- m1: A1 names the two registrations as a finding before the task;
- m2, m3: the path of an `INCOMPLETE` audit skips step 5, and step 5 also restores the WI-39
  record. A change that returns to stage 3 runs C6 and D1 again, and H1 checks TASK A8;
- m4: J3 item 4 adds a run with a link at the stand-in, whose target `latest.yaml.target-128` is
  run state;
- m5: the guard lists `.agent/sessions/` with the SHA-256 of each file. Each call in the test
  process runs in a temporary root with `.git`, and B1 runs in the red tree, a worktree at the base;
- m6: A1 removes the draft, and I1 and J4 remove the copies that reviewers leave;
- m7: mutations 18 and 19;
- N1, N3, N6 to N8 and N10: in the PLAN;
- N4: TC-25 counts the calls of `os.replace`, so it fails at the base;
- N5: the precedent of TASK 124 to TASK 127 stays, and N9: the guard covers each round;
- N11: TC-25 adds a removal that fails twice (TASK revision 4);
- N12: neither local rule ends in a wildcard.

The checks, as their tools print them:
- PLAN revision 2: `0 warn / 0 info`; `sentences : 307, mean 12.2, max 29 (limit 35)`;
  `OK: 12 of 13 reference(s) in 1 document(s) resolve against the working tree (1 pinned, not
  checked).`; `docs/PLAN.md: plan chart is current`;
- TASK revision 4: `0 warn / 1 info`; `sentences : 314, mean 11.9, max 31 (limit 35)`;
  `OK: 2 of 6 reference(s) in 1 document(s) resolve against the working tree (4 pinned, not
  checked).`

## Execution (§3)

### A — base check and the rules of the settings

- A1: `HEAD` equals the base. Of the 32 declared paths, 23 pass `git ls-files --error-unmatch`
  and 9 give `git check-ignore -q` exit 1, and each matches `[A-Za-z0-9._/-]+`. `git worktree
  list` named the main worktree and the two prunable registrations `head` and `clean`, a finding
  before the task. The run removed from the scratchpad:
  - `tools-127/`, 26 files: the tools and drafts of TASK 127;
  - `logs-127/`, 238 files, and the empty `wt-127/`;
  - `tools-128/plan_128_draft.md`.
- A2: `rules_check.py compare` printed `local: file unchanged; 0 new rule(s)` and `user: file
  unchanged; 0 new rule(s)`.

At the operator's request during the run, the ignored `.venv` was made again on Python 3.14.8
from `requirements-dev.txt`. Its base, pyenv 3.14.2, no longer existed, and VS Code named it
broken. The listings of H3 hold the new `.venv`; no check ran while it was made.

### B — stage 1: the copies

- B1: the four staged test modules, written from their final files. The red tree ran them
  against the base code: `17 failed, 98 passed, 2 skipped, 85 subtests passed`.
  - failed: TC-19, the two links of TC-20, TC-22, TC-23, TC-25, TC-27, the four cases of TC-28
    and the two runs of TC-29; the runs in other letter case of TC-A20 and TC-G11; TC-H1, TC-H2;
  - skipped: TC-24 and the junction of TC-20;
  - passed: every other test, TC-07, TC-21 and TC-26 among them.

  TC-23 took 14.74 seconds against the base, under the umask `022`.
- B2: the stubs. In the dev tree, the six SS-1 tests, TC-01, TC-11 and TC-13 passed
  (`9 passed`), and `python3 -B scripts/update_state.py --help` exited 0 from `S/`.
- B3: the logic. In the dev tree:
  - pytest of the four modules: `111 passed, 2 skipped, 89 subtests passed`;
  - `python3 -m unittest discover -s scripts/tests` from `S/`: `Ran 38 tests`, `OK (skipped=2)`;
  - `python3 tests/run_tests.py`: `Ran 623 tests`, `OK`;
  - `python3 -m unittest discover -s tests -v`: `Ran 489 tests`, `OK`, and `tests/.scratch/` did
    not exist afterwards.

  Each staged file parses with `ast.parse(..., feature_version=(3, 11))` and compiles with
  warnings as errors. The red tree and each dev tree were removed after their step. The guard
  listed `.agent/sessions/` the same before and after B1, B2 and B3.

The calls that the change adds, against the documentation of Python 3.11:

| Call | Added in |
| :--- | :--- |
| `open(..., opener=...)`, the mode `"x"`, `os.replace` | 3.3 |
| `stat.FILE_ATTRIBUTE_REPARSE_POINT`, `st_file_attributes` | 3.5 |
| `st_reparse_tag` | 3.8 |
| `os.fchmod`, called on POSIX only | POSIX before 3.0; Windows 3.13 |
| `os.O_NOFOLLOW`, read through `getattr` | POSIX before 3.0 |
| `atexit.register` with arguments, `os.fsync`, `os.lstat`, `time.sleep` | before 3.0 |
| tests: `unittest.mock`; `contextlib.redirect_stdout` and `subTest` | 3.3; 3.4 |
| tests: `_winapi.CreateJunction`, on Windows | 3.5 |

### C — the documents, the workflow and the contract test in place

- C1: with TC-C4, TC-C5 and TC-C8, the contract test gave `3 failed, 5 passed` on the live tree:
  TC-C4, TC-C5 and TC-C8 failed.
- C2 to C4: `S/SKILL.md` 1.3, §1 and §6; the guide's item 7 of §1 and the note on links in §6;
  the jobs `session-state-windows-floor` and `session-state-windows-main`.
- C5: the contract test and the tests that read the workflow, `test_python_floor`,
  `test_ci_action_pins`, `test_reference_gate_scope`, `test_mermaid_wiring` and
  `test_committed_settings`: `122 passed, 597 subtests passed`. The contract test parses at 3.11.
- C6: the progress blockquote of TASK 128 in the WI-39 record.

### D — records in place

- D1: the six records hold `status: fixed`, `resolved_at`, `resolved_by: TASK 128` and a
  resolution blockquote after the banner. Their index lines name status `fixed`; H1 shortened
  five summaries for the register.
- D2: v3.48.0 in both changelogs. Its **Changed** part names the refusal of a link and the remedy.

### E — the patch

E1: `docs/reviews/framework-audit-128-stage3.diff`, SHA-256
`625df978eb51c85d8203a3df67d672c0e2b0f6d12f392b587368680e2283d8c9`. It holds nine diffs: the eight
final files and the removal of `tests/test_concurrent_state.py`. `git apply --check` passes. Each
file is `100644`, and the patch changes no mode.

| File | Before | After, the staged copy |
| :--- | :--- | :--- |
| `S/scripts/update_state.py` | `0e46785beb33cedb…` | `8f03ed9324c1b0c4…` |
| `S/scripts/tests/test_update_state.py` | `5bb50d7f20725829…` | `08d3b4fdd83687d8…` |
| `.agent/tools/archive_move.py` | `ca4d2b589876a462…` | `885e05e3a4f91e2b…` |
| `.agent/tools/rebase_links.py` | `667a1f6dc908106b…` | `234f5fbf9dc6cc38…` |
| `tests/_scratch.py` | `2d77e3e310cbec24…` | `58cc8c26cd828b1d…` |
| `tests/test_archive_move.py` | `e9f39ed6b9b0d22c…` | `d392f306a66c5396…` |
| `tests/test_script_guards.py` | `328419310e395ebd…` | `ae753f55a8dc8f34…` |
| `tests/test_scratch_hygiene.py` | `d0e31ea7a1747ee4…` | `2245845f0964c32f…` |
| `tests/test_concurrent_state.py` | `56e0b524c77bb789…` | removed |

### H — the checks before stage 3

- H1, on the live tree:
  - `gates.py`: `20 of 20 steps pass`. The test step of each Windows job gave `32 passed` with
    the base module;
  - `git diff --quiet <base> -- System/Docs/SKILLS.md System/Docs/WORKFLOWS.md`: exit 0;
  - `list_tests.py`: `staged: none` in each of the five listings, and no `tests/.scratch/` left;
  - `regcheck.py`: five warnings on the index lines of `docs/KNOWN_ISSUES.md`, a sentence of 36
    to 42 words each. D1 shortened the summaries, and the check then gave `0 warn`. Each other
    changed document gave `0 warn`;
  - `bytescan.py`: each changed and created file is clean;
  - the six records and their index lines name `fixed`, and the WI-39 record holds the progress;
  - each of the 28 paths of `git status` is declared.
- H2, in the patched tree:
  - `gates.py`: `20 of 20 steps pass`. The test step of each Windows job gave `44 passed, 2
    skipped, 4 subtests passed`;
  - the four modules: `111 passed, 2 skipped, 89 subtests passed`, the skips of B1 only;
  - TASK A4: with `TMPDIR` inside a temporary work tree, both SS-1 tests skipped and named it,
    and the work tree listed the same before and after;
  - TASK A5: `git grep -l test_concurrent_state -- . ':!docs' ':!CHANGELOG.md'
    ':!CHANGELOG.ru.md'` exited 1 and printed nothing;
  - `mutate.py`: each of the 22 mutations changed its file and made its named test fail, and each
    file hashed as before after the restore. The table below gives the first error line;
  - the patched tree was removed, and the guard listed `.agent/sessions/` the same.

| # | Mutation | Failure of the named test |
| :--- | :--- | :--- |
| 1, 2 | the check of device and inode removed | the planted module ran, and the copy exited 1 |
| 3, 5 | the check of `latest.yaml`, of the lock removed | `'is a link' not found` |
| 4 | the check of `.agent/sessions` removed | `0 != 1`: the state was written |
| 6, 8 | the reparse branch, the check of the kind removed | `StateError not raised` |
| 7 | the check of the name surrogate removed | the cloud placeholder was refused |
| 9, 10 | `O_NOFOLLOW` removed from the opener, from the lock | `0 != 1`: the run followed the link |
| 11 | `os.fchmod` removed | `420 != 384` |
| 12 | the removal of the temporary file removed | the temporary file stayed |
| 13 | the tries removed | `1 != 0`: `could not write` |
| 14, 15 | a pattern of the base restored | `6.9 not less than 4.0` |
| 16 | the literal `SESSION_DIR` restored | `'.agent/sessions' != '.agent\\sessions'` |
| 17 to 19 | the write through `os.fdopen`, `io.open`, `codecs.open` | `[322] != []` |
| 20, 21 | the registration removed; a handler that reads the globals | the session or its root stayed |
| 22 | the retry of R6.4 removed | `FileNotFoundError` |

- H3, `j3.py h3`, each command from the root unless a directory is named; the guard listed
  `.agent/sessions/` the same before and after:

| Command | Result |
| :--- | :--- |
| `python3 -m pytest` from the root | exit 0, `733 passed`, equal listings |
| `python3 -m pytest` from `S/` | exit 0, `24 passed`, equal listings |
| `python3 -m pytest` from `.agent/tools/` | exit 0, `257 passed`, equal listings |
| `python3 tests/run_tests.py` | exit 0, equal listings |
| the local rule `ca2c33383ded254c` | exit 0; `tests/.scratch/` and one session directory added |
| the user rule `9fa5cad71668c6f7`, from `S/` | exit 0, equal listings |
| the local rule `f42576bf00a2603c` | exit 0, `12 passed`, equal listings |
| the local rule `7e089e2b18fca974` | exit 0, `34 passed, 18 subtests passed`, equal listings |

  The base `tests/_scratch.py` wrote the two directories of the local rule: TS-1, a finding
  before the task, which this change closes. The run put them back with `rmdir`, the inner first.
- H4, the read of TASK R7.5, is the table below.
- H5: 18 checkouts beside this repository hold `.agent/sessions`, and none holds a link at the
  three entries of TASK R2.1. `Universal-skills`, the checkout of the 15 user rules, is among
  them.
- `wt.sh` left the diff of the live tree in the scratchpad after each build. The run removed the
  four files, and `wt.sh` now removes the diff after it applies it.

| Test or part | Assumption of POSIX | How the change meets it on Windows |
| :--- | :--- | :--- |
| the SS-1 tests | output read in the locale | the output is ASCII; `TEMP` is no work tree |
| TC-01 | a lock between two runs | the real `msvcrt.locking`, 10 tries |
| TC-02 to TC-05 | `fcntl`, or the stand-in on it | skipped where `fcntl` is missing |
| TC-24 | none | Windows only; it unlocks before it closes |
| TC-06 | `LC_ALL=C` makes the locale ASCII | no effect; the code page cp1252 is the test |
| TC-08 | a root in Cyrillic | `CreateProcessW` takes it; `backslashreplace` |
| TC-09, TC-14, TC-16, TC-17 | argv with CR, LF, quotes, a lone surrogate | the C runtime keeps them; UTF-16 |
| TC-11, TC-19 | the message names `str(path)` | R7.3 joins with backslashes |
| TC-12 | links, a `.pyc`, other letter case | links skip where they fail; `msvcrt` is built in |
| TC-18 | `os.path.exists` patched up to the root | `makedirs` ignores the error of `C:\` |
| TC-19, TC-20 | symbolic links | skipped where `os.symlink` fails |
| TC-20, junction | none | `_winapi.CreateJunction`; `os.rmdir` before the cleanup |
| TC-21 | no CR; the permission bits | the opener keeps `O_BINARY`; the bits on POSIX only |
| TC-22, TC-25, TC-29 | `main()` in the test process | it runs in the temporary root; TC-29 skips |
| TC-23 | a bound of 4 seconds | 0.1 seconds here; the base took 14.74 |
| TC-07, TC-13, TC-26 to TC-28 | none | none |
| the contract test | text of the documents | UTF-8, newlines read as text; PyYAML installed |
| the checkout | `core.autocrlf` on, no `.gitattributes` | Python and the tests read CRLF as text |
| `tests/conftest.py` | the stale sweep calls `os.kill` | `tests/.scratch/` is absent after a checkout |
| the file names | none | no reserved name and no character `:*?"<>\|` |

## Stage 2 (PLAN I1)

### Round 1, at the fingerprint `4182f63c709d`: both pass

Each reviewer computed the fingerprint at its start and at its end, and found `4182f63c709d`. Each
ran its probes in the patched tree `wt-128/i1` or in its own temporary directories, and removed
them. After the round, the guard listed `.agent/sessions/` the same, the scratchpad held no file
of a reviewer, and the patched tree held only the change; the run removed it.

The `code-reviewer`: `APPROVED`, 11 findings in scope, each LOW:
- tests:
  - TC-H2 does not make the root vanish, so a retry without `_ensure_root` passes it;
  - no test pins `_TRIES` and `_PAUSE`, or a move that fails at every try;
  - TC-28 lacks the branch of the directory, and TC-29 asserts the exit only;
  - TC-23 has a margin of 1.7 against one pattern of the base;
  - `run_main` leaves `sys.stderr` reconfigured;
- code:
  - the bits of the old file come from a second `os.lstat`, which a link swapped in during the
    window of D6 answers;
  - a killed run leaves its temporary file;
  - `os.fchmod` and `os.fsync` can fail on a file system that the base wrote to;
- documents: the skill and the guide say that the message calls an entry of another kind a link;
  the changelogs give the time of both patterns as that of the item pattern alone.

Before the task: `docs/ARCHITECTURE.md:120` puts the lock on `latest.yaml`, not on its lock file.

The `security-auditor`: `PASS`, the scan complete, 8 findings in scope, each LOW:
- a link at `.agent` itself is followed, while the documents say that nothing is read or written
  through a link. The names stay fixed, so another checkout's state can be read and replaced;
- the temporary file holds the bits `0o644` under the umask until `os.fchmod`, so a state set to
  `0o600` is readable by others for a moment: a regression of this change;
- the bits come from a second `os.lstat` with no check of the kind, as the code review found;
- `get_session_dir()` walks up three times in `main()`;
- the remedy "replace it with the directory or the file that it names" suits no hostile link;
- `_ensure_root()` can raise `FileNotFoundError` outside the retry of R6.4, in a race with the
  `rmdir` of another process's handler;
- the CI jobs install `requirements-dev.txt` without hashes, as the other jobs do;
- R1 on a volume without inode numbers keeps the check by name alone, as PLAN H2 states.

Before the task, named to the operator when the round ended:
- MEDIUM: `pytest==9.0.2` of `requirements-dev.txt` has CVE-2025-71176, fixed in 9.0.3;
- CRITICAL and HIGH: `npm audit` of the lockfiles of the mermaid renderers, v10 to v12;
- CRITICAL by pattern: secret-shaped strings in test fixtures of `run-feedback` and
  `tests/fixtures/ab-corpus*`, not verified;
- MEDIUM, low confidence: the boot read of `latest.yaml` by the agent follows a committed link,
  which the script's refusal does not cover;
- LOW: the scanner's `pip-audit` reads its own environment; three hits of semgrep in older code.

Both reviews passed. Three findings break something real: the race of `_ensure_root`, which R6.4
was meant to close; the bits of the temporary file, a regression; and the wording of the
documents and changelogs. Under the operator's rule recorded at TASK 124, fix round 1 fixes these
and the cheap gaps of the tests in one round, and the TASK states the rest as limits (D14).

### Fix round 1 (TASK D14)

TASK revision 5 and PLAN revision 3 state the fixes and the mutations 23 to 28.

- B, the tests first. The staged test modules gained:
  - TC-21: the bits of the temporary file before `os.fchmod`, and a write onto a link;
  - TC-23: 100,000 spaces; TC-25: a move held at every try; TC-28: a regular file at
    `.agent/sessions`; TC-29: no `is a link` in the output;
  - TC-H2: the root removed before `mkdtemp`, and an `_ensure_root` that raises once;
  - `run_main` also captures `sys.stderr`.

  In a dev tree with the staged code of round 1: `2 failed, 49 passed, 2 skipped, 5 subtests
  passed`. TC-21 failed with `the temporary file had 0o644`, and the case of `_ensure_root` of
  TC-H2 failed.
- B, then the code:
  - the opener creates with `0o600`;
  - `_write_state` takes the bits of a regular file only, and else `0o644` under the umask;
  - `main` finds the session directory once;
  - `session_scratch()` holds `_ensure_root` inside its tries.

  In a new dev tree: the four modules `112 passed, 2 skipped, 90 subtests passed`; the module of
  `S/` under unittest `OK (skipped=2)`; `tests/run_tests.py` `OK`; the unittest discovery of
  `tests` `OK`, with no `tests/.scratch/` left. The guard listed `.agent/sessions/` the same.
- C and D: the skill, the guide, both changelogs and the SS-6 record:
  - the refusal names the three entries, and a link above them is followed;
  - the message names a link, or the kind that it expected;
  - the remedy: remove the link, or replace it with a directory or a regular file of one's own;
  - the guide names the temporary file that a killed run leaves;
  - the changelogs name both patterns of SS-6 and both values.
- E1: the patch, SHA-256 `5f0664776fffa2b17275139ece7bc33d721e58f00574ae0b5c4ce2f7b3e51b61`, nine
  diffs; `git apply --check` passes. Four staged copies changed; the other four hash as in
  round 1:

| File | After, the staged copy |
| :--- | :--- |
| `S/scripts/update_state.py` | `4a5fc65d0caeccae…` |
| `S/scripts/tests/test_update_state.py` | `30293d85fda5ce6f…` |
| `tests/_scratch.py` | `cc74afb2e6862999…` |
| `tests/test_scratch_hygiene.py` | `4d9199cfea7f5a0e…` |

- H1, on the live tree: `gates.py` `20 of 20 steps pass`; `list_tests.py` `staged: none` in each
  listing; `regcheck.py` `0 warn` on each of 15 documents; `bytescan.py` clean; the registries
  unchanged; the six records `fixed`; each of the 28 paths of `git status` declared.
- H4: the table above holds. The new parts of TC-21 run on POSIX only; the new case of TC-25
  replaces `os.replace` and `time.sleep`; TC-H2 runs in no Windows job.
- H5: 18 checkouts, and no link at the three entries in any of them.
- H2, in a new patched tree that hashes to the staged copies of the fix round:
  - `gates.py`: `20 of 20 steps pass`; the test step of each Windows job gave `44 passed, 2
    skipped, 5 subtests passed`;
  - the four modules: `112 passed, 2 skipped, 90 subtests passed`;
  - TASK A4 and A5 as at round 1;
  - `mutate.py`: each of the 28 mutations made its named test fail, and each file hashed as
    before after the restore. Mutations 14 and 15 took 27.5 seconds each against the bound of 4.

| # | Mutation of the fix round | Failure of the named test |
| :--- | :--- | :--- |
| 11 | `os.fchmod` removed | `384 != 420`: the bits of creation stayed |
| 23 | the opener creates with `0o644` | `the temporary file had 0o644` |
| 24 | the bits taken from an entry of any kind | `493 != 420`: the bits of the link |
| 25, 26 | `_TRIES` set to 3; `_PAUSE` set to 0.5 | `3 != 10`; nine pauses of 0.5 |
| 27 | the branch of the directory removed | `StateError not raised` |
| 22, 28 | the retry removed; the root made once before the tries | `FileNotFoundError` |

- H3, `j3.py h3`: each command as at round 1, with equal listings but the local rule
  `ca2c33383ded254c`, whose two directories the base `tests/_scratch.py` wrote again (TS-1). The
  run put them back. The guard listed `.agent/sessions/` the same.

### Round 2, at the fingerprint `31b3336c9275`: both pass

Each reviewer, resumed, computed `31b3336c9275` at its start and at its end, ran its probes in the
patched tree `wt-128/i2` or in its own directories, and removed them. After the round, the guard
listed `.agent/sessions/` the same, the scratchpad held no file of a reviewer, and the run removed
the patched tree.

The `code-reviewer`: `APPROVED`. It checked each fix of round 1 and found nothing broken. Three
findings, each LOW:
- the refusal message of `update_state.py` and its docstring keep the old remedy and the claim of
  no link at all; R8.3 of the TASK prescribes the old remedy;
- `REPO_SCRATCH.mkdir(parents=True, exist_ok=True)` raises `FileExistsError` when the empty root
  goes between its `os.mkdir` and its `is_dir()`, a race that R6.4 misses;
- the check of TC-21 on the bits of the temporary file holds under the umask `022` only.

The `security-auditor`: `PASS`, the scan complete. Fixes 2, 3, 4 and 6 of round 1 hold. Two
findings, each LOW:
- the message and the docstring of the script, as the code review found;
- `os.replace` keeps the mode bits of the old file, not its ACL, its extended attributes or its
  owner. The base wrote the file in place.

The message is the line that the operator reads under the failure rule, and it gives the remedy
that round 1 called wrong for a hostile link. Fix round 2 corrects it, closes the race of
`FileExistsError` and fixes the umask of TC-21. The ACL and the extended attributes become a
limit (D15). Round 3 is the last of the bound.

### Fix round 2 (TASK D15)

TASK revision 6 and PLAN revision 4 state the fixes and the mutations 29 and 30.

- B, the tests first:
  - TC-19 asserts that the message says to remove the link;
  - the check of TC-21 on the bits of the temporary file runs under the umask `022`;
  - TC-H2 adds an `_ensure_root` that raises `FileExistsError` once.

  In a dev tree with the staged code of round 2: `2 failed, 50
  passed, 2 skipped, 6 subtests passed`. TC-19 and the case of `FileExistsError` failed.
- B, then the code: the refusal message names the remedy of R2.1, and the docstring names the
  three entries and the link above them; `session_scratch()` catches `FileExistsError` too. In a
  new dev tree: the four modules `112 passed, 2 skipped, 92 subtests passed`; the module of `S/`
  under unittest, `tests/run_tests.py` and the unittest discovery of `tests` each `OK`, with no
  `tests/.scratch/` left. The guard listed `.agent/sessions/` the same.
- E1: the patch, SHA-256 `dd655ff565cbd45fae0e9f7cd8ac49b19541beb1eadf1894a4fdd15f1f0a8a28`, nine
  diffs; `git apply --check` passes. Four staged copies changed in this round:

| File | After, the staged copy |
| :--- | :--- |
| `S/scripts/update_state.py` | `531e2c46e723d395…` |
| `S/scripts/tests/test_update_state.py` | `5922108dfe575ffc…` |
| `tests/_scratch.py` | `ea8e7534e6905000…` |
| `tests/test_scratch_hygiene.py` | `ddcd5c75eae08f8f…` |

- H1, on the live tree: `gates.py` `20 of 20 steps pass`; `list_tests.py` `staged: none` in each
  of the five listings; `regcheck.py` `0 warn` on each of 15 documents; `bytescan.py` clean; each
  of the 28 paths of `git status` declared. The guard listed `.agent/sessions/` the same.
- H2, in a new patched tree that hashes to the staged copies of fix round 2: `gates.py` `20 of
  20 steps pass`; the four modules `112 passed, 2 skipped, 92 subtests passed`; TASK A4 and A5 as
  before. Each of the 30 mutations made its named test fail, and each file hashed as before after
  the restore. Mutation 29 failed with `'remove it' not found`, and mutation 30 with
  `FileExistsError`.
- H3, `j3.py h3`: as at round 1. The base `tests/_scratch.py` wrote the two directories of TS-1
  again under the local rule `ca2c33383ded254c`, and the run put them back.
- H5: 18 checkouts, and no link at the three entries in any of them.

### Round 3, at the fingerprint `1c8422238af5`: both pass, and stage 2 closes (TASK D16)

Each reviewer, resumed, computed `1c8422238af5` at its start and at its end, ran its probes in the
patched tree `wt-128/i3` or in its own directories, and removed them. After the round, the guard
listed `.agent/sessions/` the same, the scratchpad held no file of a reviewer, and the run removed
the patched tree.

- The `code-reviewer`: `APPROVED`. Its three findings of round 2 are fixed, the round broke
  nothing, and it has no new finding. Before the task: `docs/ARCHITECTURE.md:120`, as before.
- The `security-auditor`: `PASS`, the scan complete. R2-1 is fixed and R2-2 is a limit. The catch
  of `FileExistsError` can hide no error, cannot loop and deletes nothing new. Nothing breaks
  something real. The limits of D6, D13, D14 and D15 stand, each recorded.

The findings before the task of round 1 were named to the operator when stage 2 closed:
- `npm audit` of the lockfiles of the mermaid renderers, CRITICAL and HIGH;
- secret-shaped strings in test fixtures, CRITICAL by pattern;
- CVE-2025-71176 of `pytest==9.0.2`, MEDIUM;
- the boot read of `latest.yaml` by the agent, MEDIUM with low confidence.

## Stage 3 (PLAN J1 and J2)

- J1, §4.5: `check_positional_refs.py --targets-changed` reported `0 error(s), 17 warning(s)
  across 566 reference(s)`. Each warning is a `DRIFT_SUSPECT` in an archived or older document
  whose coordinate points into a file this change edits. The changelogs grew at their top, and
  the workflow at its end. `--fix` touched no file. `rules_check.py compare`: both settings
  files unchanged, and no new rule.
- J2 step 1: the patch hashes to
  `dd655ff565cbd45fae0e9f7cd8ac49b19541beb1eadf1894a4fdd15f1f0a8a28`, the value that round 3
  reviewed, and each staged copy to its value of E1 of fix round 2.
- J2 step 2: the staged copies, and each file that the patch edits or removes before it:

| Staged copy | SHA-256 |
| :--- | :--- |
| `.agent/skills/skill-session-state/scripts/staged_update_state.py` | `531e2c46e723d395a930054374fa2cdb71c69a3d5ff78b56b645bda66cb1eec8` |
| `.agent/skills/skill-session-state/scripts/tests/staged_test_update_state.py` | `5922108dfe575ffc3d35669e84639e45d17f7e2e41cf7d7a0833de1f4de37922` |
| `.agent/tools/staged_archive_move.py` | `885e05e3a4f91e2b24cbfdff0c632ddcea2e8683cd503e27a32aeee4f34b0ae8` |
| `.agent/tools/staged_rebase_links.py` | `234f5fbf9dc6cc382426c084923dc5988c3eea40b5742e32da0cbfe8589173c4` |
| `tests/staged_scratch.py` | `ea8e7534e690500071bca4f973a4c442b09c1e49f2d772bd17b31aeff0da601d` |
| `tests/staged_archive_move.py` | `d392f306a66c53960412820640912addfa2a154709732d6b6e87485f6bb7985d` |
| `tests/staged_script_guards.py` | `ae753f55a8dc8f342def9fa31ad9b48a2c8bdb7898b79aa62fa762e7f7629e69` |
| `tests/staged_scratch_hygiene.py` | `ddcd5c75eae08f8f5ab68dc307679307a7476db74d972c21dd942b89e2bab2c2` |

| File before the patch | SHA-256 | Mode |
| :--- | :--- | :--- |
| `.agent/skills/skill-session-state/scripts/update_state.py` | `0e46785beb33cedb…` | `644` |
| `.agent/skills/skill-session-state/scripts/tests/test_update_state.py` | `5bb50d7f20725829…` | `644` |
| `.agent/tools/archive_move.py` | `ca4d2b589876a462…` | `644` |
| `.agent/tools/rebase_links.py` | `667a1f6dc908106b…` | `644` |
| `tests/_scratch.py` | `2d77e3e310cbec24…` | `644` |
| `tests/test_archive_move.py` | `e9f39ed6b9b0d22c…` | `644` |
| `tests/test_script_guards.py` | `328419310e395ebd…` | `644` |
| `tests/test_scratch_hygiene.py` | `d0e31ea7a1747ee4…` | `644` |
| `tests/test_concurrent_state.py` | `56e0b524c77bb789…` | `644` |

The patch:

~~~~diff
diff --git a/.agent/skills/skill-session-state/scripts/tests/test_update_state.py b/.agent/skills/skill-session-state/scripts/tests/test_update_state.py
index b8531db..b3c0c71 100644
--- a/.agent/skills/skill-session-state/scripts/tests/test_update_state.py
+++ b/.agent/skills/skill-session-state/scripts/tests/test_update_state.py
@@ -3,18 +3,26 @@
 SS-1 regression: update_state.py must anchor .agent/sessions at the repo root regardless of the
 invocation CWD (docs/issues/ss-1-*.md). TASK 127: the lock on POSIX and on Windows, UTF-8, the
 escaped scalars and their round trip, and the import path (WI-39); TC-01 to TC-18 of its §5.
+TASK 128: no read or write through a link (SS-3), the write through a temporary file, a linear
+reader (SS-6), the SS-1 tests inside a git work tree (SS-5), and the paths of Windows; TC-19 to
+TC-29 of its §5.
 
 Each test runs the script in a temporary root that holds its own `.git`, and no test writes
-under the repository. The Windows branch runs on POSIX: a test writes, into a temporary
-directory, a `sitecustomize.py` that blocks `import fcntl` and provides a `msvcrt` stand-in on
-`fcntl.lockf`, and puts that directory on `PYTHONPATH`. PyYAML checks each written file as a
-second reader; where it does not import, each test that reaches such a check reports a skip.
+under the repository. A call of the script in this process changes into such a root first. The
+two SS-1 tests of the fallback without `.git` skip when an ancestor holds one. The Windows branch
+runs on POSIX: a test writes, into a temporary directory, a `sitecustomize.py` that blocks
+`import fcntl` and provides a `msvcrt` stand-in on `fcntl.lockf`, and puts that directory on
+`PYTHONPATH`. PyYAML checks each written file as a second reader; where it does not import, each
+test that reaches such a check reports a skip.
 """
 import ast
+import contextlib
+import io
 import json
 import os
 import py_compile
 import re
+import stat
 import subprocess
 import sys
 import tempfile
@@ -22,11 +30,20 @@ import time
 import types
 import unittest
 from pathlib import Path
+from unittest import mock
 
 try:
     import fcntl
 except ImportError:  # Windows: the tests that hold a POSIX lock skip
     fcntl = None
+try:
+    import msvcrt
+except ImportError:  # POSIX: the test of the real lock of Windows skips
+    msvcrt = None
+try:
+    import _winapi
+except ImportError:  # POSIX: the junction of TC-20 skips
+    _winapi = None
 try:
     import yaml
 except ImportError:  # PyYAML is a second reader only
@@ -215,6 +232,24 @@ def json_lists(text):
     return lists, scalars
 
 
+def outer_git(path):
+    """`path` or its nearest ancestor that holds `.git`, a directory or a file, or `None`.
+
+    The script's walk-up stops at such a directory (SS-1), so a test that expects no `.git` above
+    its root skips when one is found (TASK 128 R4.1).
+    """
+    path = Path(path).resolve()
+    for directory in (path, *path.parents):
+        if (directory / ".git").exists():
+            return directory
+    return None
+
+
+def fake_stat(mode, attributes=0, tag=0):
+    """A result of `os.lstat` with the attributes that the check of the script reads."""
+    return types.SimpleNamespace(st_mode=mode, st_file_attributes=attributes, st_reparse_tag=tag)
+
+
 class _RootCase(unittest.TestCase):
     """A temporary root that holds its own `.git`; the script writes its state there."""
 
@@ -232,6 +267,37 @@ class _RootCase(unittest.TestCase):
         self.assertEqual(proc.returncode, 0, output(proc))
         return proc
 
+    def run_main(self, module, args):
+        """`module.main()` in this process with `args`, in the root and without
+        `CLAUDE_PROJECT_DIR`; the exit code and the output."""
+        out = io.StringIO()
+        cwd = os.getcwd()
+        os.chdir(self.root)
+        try:
+            with mock.patch.dict(os.environ), \
+                    mock.patch.object(sys, "argv", ["update_state.py"] + list(args)), \
+                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
+                os.environ.pop("CLAUDE_PROJECT_DIR", None)
+                try:
+                    module.main()
+                    code = 0
+                except SystemExit as exc:
+                    code = exc.code
+        finally:
+            os.chdir(cwd)
+        return code, out.getvalue()
+
+    def make_link(self, link, target, directory=False):
+        """A symbolic link at `link`; the test skips where none can be made."""
+        try:
+            os.symlink(target, link, target_is_directory=directory)
+        except (OSError, NotImplementedError):
+            self.skipTest("no symbolic link can be made on this host")
+
+    def names(self):
+        """The entries of the session directory, sorted."""
+        return sorted(p.name for p in self.sessions.iterdir())
+
     def text(self):
         return self.state.read_bytes().decode("utf-8")
 
@@ -304,7 +370,15 @@ class UpdateStateAnchorTestCase(unittest.TestCase):
         self.assertEqual(proc.returncode, 0, proc.stderr)
         self.assertTrue(self._state(self.root).is_file())
 
+    def skip_inside_a_work_tree(self):
+        """The fallback without `.git` is tested only where no ancestor of the root holds one;
+        elsewhere the script would write the state of that outer tree (SS-5)."""
+        outer = outer_git(self.root)
+        if outer is not None:
+            self.skipTest(f"{outer} holds .git, and the script would write its state there (SS-5)")
+
     def test_no_git_falls_back_to_claude_project_dir(self):
+        self.skip_inside_a_work_tree()
         target = self.root / "proj"
         (target / ".agent").mkdir(parents=True)
         lone = self.root / "lone"
@@ -316,6 +390,7 @@ class UpdateStateAnchorTestCase(unittest.TestCase):
         self.assertFalse((lone / ".agent").exists())
 
     def test_no_git_no_env_keeps_legacy_cwd_behavior(self):
+        self.skip_inside_a_work_tree()
         lone = self.root / "lone"
         lone.mkdir()
         proc = self._run(lone)
@@ -339,9 +414,8 @@ class UpdateStateAnchorTestCase(unittest.TestCase):
                          "same session_id — subdir run updates, not forks")
 
 
-@unittest.skipIf(fcntl is None, "holds a POSIX lock, or runs the Windows branch on POSIX")
-class LockTestCase(_RootCase):
-    """TASK 127 R1: the lock on POSIX and on Windows (TC-01 to TC-05)."""
+class ConcurrentRunsTestCase(_RootCase):
+    """TASK 127 R1 on every platform (TASK 128 R7.4): two runs at once (TC-01)."""
 
     def test_tc01_two_runs_at_once_keep_both_tasks(self):
         procs = [subprocess.Popen([sys.executable, str(SCRIPT)] + ARGS
@@ -355,6 +429,33 @@ class LockTestCase(_RootCase):
         lists, _ = json_lists(self.text())
         self.assertEqual(sorted(lists["completed_tasks"]), ["Task A", "Task B"])
 
+
+@unittest.skipIf(msvcrt is None, "holds the lock of Windows")
+class WindowsLockTestCase(_RootCase):
+    """TASK 128 R7.4: the real `msvcrt` lock (TC-24)."""
+
+    def test_tc24_a_held_lock_ends_the_run_after_its_tries(self):
+        self.write_state(V2_STATE.format(decision='"kept"'))
+        before = self.state.read_bytes()
+        fd = os.open(self.lock, os.O_RDWR | os.O_CREAT, 0o644)
+        try:
+            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
+            try:
+                proc = run_script(self.root, ARGS)
+            finally:
+                os.lseek(fd, 0, os.SEEK_SET)
+                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
+        finally:
+            os.close(fd)
+        self.assertEqual(proc.returncode, 1, output(proc))
+        self.assertIn("latest.yaml.lock", output(proc))
+        self.assertEqual(self.state.read_bytes(), before)
+
+
+@unittest.skipIf(fcntl is None, "holds a POSIX lock, or runs the Windows branch on POSIX")
+class LockTestCase(_RootCase):
+    """TASK 127 R1: the lock on POSIX and on Windows (TC-02 to TC-05)."""
+
     def test_tc02_a_held_flock_makes_the_run_wait(self):
         self.sessions.mkdir(parents=True)
         fd = os.open(self.lock, os.O_RDWR | os.O_CREAT, 0o644)
@@ -446,8 +547,15 @@ class EncodingTestCase(_RootCase):
 
     def test_tc07_each_open_names_its_encoding(self):
         tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
-        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
-                 and isinstance(node.func, ast.Name) and node.func.id == "open"]
+        every = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
+        # A file of the state is read and written through `open` only (TASK 128 TC-07).
+        others = [call.lineno for call in every if isinstance(call.func, ast.Attribute)
+                  and (call.func.attr == "fdopen"
+                       or call.func.attr == "open" and isinstance(call.func.value, ast.Name)
+                       and call.func.value.id in ("io", "codecs"))]
+        self.assertEqual(others, [], "a file opened outside `open`")
+        calls = [call for call in every
+                 if isinstance(call.func, ast.Name) and call.func.id == "open"]
         self.assertTrue(calls)
         for call in calls:
             keywords = {kw.arg: kw.value for kw in call.keywords}
@@ -455,7 +563,7 @@ class EncodingTestCase(_RootCase):
             mode = mode.value if isinstance(mode, ast.Constant) else "r"
             encoding = keywords.get("encoding")
             self.assertIsInstance(encoding, ast.Constant, f"line {call.lineno}: no encoding")
-            if "w" in mode:
+            if any(flag in mode for flag in "wxa+"):
                 self.assertEqual(encoding.value, "utf-8", f"line {call.lineno}")
                 newline = keywords.get("newline")
                 self.assertIsInstance(newline, ast.Constant, f"line {call.lineno}: no newline")
@@ -629,5 +737,272 @@ class ImportPathTestCase(_RootCase):
         self.assertTrue(callable(module.parse_simple_yaml))
 
 
+class LinkTestCase(_RootCase):
+    """TASK 128 R2.1 to R2.3, SS-3: no read or write through a link (TC-19, TC-20, TC-29)."""
+
+    def test_tc19_a_link_at_the_state_is_refused(self):
+        outside = Path(self._tmp.name).resolve() / "outside.txt"
+        outside.write_bytes(b"keep\n")
+        self.sessions.mkdir(parents=True)
+        self.make_link(self.state, outside)
+        proc = run_script(self.root, ARGS)
+        self.assertEqual(proc.returncode, 1, output(proc))
+        self.assertIn(str(self.state), output(proc))
+        self.assertIn("is a link", output(proc))
+        self.assertIn("remove it", output(proc))
+        self.assertEqual(outside.read_bytes(), b"keep\n")
+
+    def test_tc20_a_link_at_the_directory_is_refused(self):
+        outside = Path(self._tmp.name).resolve() / "outside-dir"
+        outside.mkdir()
+        (self.root / ".agent").mkdir()
+        self.make_link(self.sessions, outside, directory=True)
+        proc = run_script(self.root, ARGS)
+        self.assertEqual(proc.returncode, 1, output(proc))
+        self.assertIn("is a link", output(proc))
+        self.assertEqual(list(outside.iterdir()), [])
+
+    def test_tc20_a_link_at_the_lock_is_refused(self):
+        outside = Path(self._tmp.name).resolve() / "outside.txt"
+        outside.write_bytes(b"keep\n")
+        self.sessions.mkdir(parents=True)
+        self.make_link(self.lock, outside)
+        proc = run_script(self.root, ARGS)
+        self.assertEqual(proc.returncode, 1, output(proc))
+        self.assertIn("is a link", output(proc))
+        self.assertEqual(outside.read_bytes(), b"keep\n")
+        self.assertFalse(self.state.exists())
+
+    @unittest.skipIf(_winapi is None, "makes a junction of Windows")
+    def test_tc20_a_junction_at_the_directory_is_refused(self):
+        outside = Path(self._tmp.name).resolve() / "outside-dir"
+        outside.mkdir()
+        (self.root / ".agent").mkdir()
+        try:
+            _winapi.CreateJunction(str(outside), str(self.sessions))
+        except OSError:
+            self.skipTest("no junction can be made on this host")
+        self.addCleanup(os.rmdir, str(self.sessions))
+        proc = run_script(self.root, ARGS)
+        self.assertEqual(proc.returncode, 1, output(proc))
+        self.assertIn("is a link", output(proc))
+        self.assertEqual(list(outside.iterdir()), [])
+
+    def regular_at(self, *entries):
+        """An `os.lstat` that reports a regular file at `entries`: a link swapped in after the
+        check of R2.1 (TC-29)."""
+        real = os.lstat
+        names = {str(entry) for entry in entries}
+
+        def lstat(path, *args, **kwargs):
+            if os.fspath(path) in names:
+                return fake_stat(stat.S_IFREG | 0o644)
+            return real(path, *args, **kwargs)
+        return lstat
+
+    @unittest.skipIf(not hasattr(os, "O_NOFOLLOW"), "no O_NOFOLLOW on this platform")
+    def test_tc29_a_link_swapped_in_at_the_state_is_not_read(self):
+        target = Path(self._tmp.name).resolve() / "target.txt"
+        target.write_bytes(b"keep\n")
+        self.sessions.mkdir(parents=True)
+        self.make_link(self.state, target)
+        module = load_script("update_state_tc29_state")
+        with mock.patch.object(module.os, "lstat", side_effect=self.regular_at(self.state)):
+            code, out = self.run_main(module, ARGS)
+        self.assertEqual(code, 1, out)
+        self.assertNotIn("is a link", out, "the check of R2.1 refused, not O_NOFOLLOW")
+        self.assertEqual(target.read_bytes(), b"keep\n")
+        self.assertTrue(self.state.is_symlink())
+
+    @unittest.skipIf(not hasattr(os, "O_NOFOLLOW"), "no O_NOFOLLOW on this platform")
+    def test_tc29_a_link_swapped_in_at_the_lock_is_not_followed(self):
+        target = Path(self._tmp.name).resolve() / "made-through-the-lock"
+        self.sessions.mkdir(parents=True)
+        self.make_link(self.lock, target)
+        module = load_script("update_state_tc29_lock")
+        with mock.patch.object(module.os, "lstat", side_effect=self.regular_at(self.lock)):
+            code, out = self.run_main(module, ARGS)
+        self.assertEqual(code, 1, out)
+        self.assertNotIn("is a link", out, "the check of R2.1 refused, not O_NOFOLLOW")
+        self.assertFalse(os.path.lexists(target), "the link at the lock file was followed")
+
+
+class WriteTestCase(_RootCase):
+    """TASK 128 R2.4 to R2.6: the write through a temporary file (TC-21, TC-22, TC-25)."""
+
+    def test_tc21_the_write_leaves_no_temporary_file_and_keeps_the_bits(self):
+        self.run_ok(ARGS)
+        self.assertEqual(self.names(), ["latest.yaml", "latest.yaml.lock"])
+        self.assertNotIn(bytes([13]), self.state.read_bytes())
+        if os.name == "posix":
+            umask = os.umask(0)
+            os.umask(umask)
+            self.assertEqual(stat.S_IMODE(self.state.stat().st_mode), 0o644 & ~umask)
+            os.chmod(self.state, 0o600)
+            self.run_ok(ARGS)
+            self.assertEqual(stat.S_IMODE(self.state.stat().st_mode), 0o600)
+            self.assertEqual(self.names(), ["latest.yaml", "latest.yaml.lock"])
+
+            # The temporary file holds no bit for group or others until `os.fchmod` (R2.4). The
+            # umask `022` leaves group and others readable, so creation bits of `0o644` show.
+            module = load_script("update_state_tc21")
+            seen, real_fchmod = [], os.fchmod
+
+            def fchmod(fd, mode):
+                seen.append(stat.S_IMODE(os.fstat(fd).st_mode))
+                return real_fchmod(fd, mode)
+
+            ambient = os.umask(0o022)
+            try:
+                with mock.patch.object(module.os, "fchmod", side_effect=fchmod):
+                    code, out = self.run_main(module, ARGS)
+            finally:
+                os.umask(ambient)
+            self.assertEqual(code, 0, out)
+            self.assertEqual(len(seen), 1)
+            self.assertEqual(seen[0] & 0o077, 0, f"the temporary file had {oct(seen[0])}")
+
+            # A write onto a link gives the new file the bits of no link (R2.4 step 2).
+            target = Path(self._tmp.name).resolve() / "target.txt"
+            target.write_bytes(b"keep\n")
+            os.remove(self.state)
+            self.make_link(self.state, target)
+            module._write_state(str(self.state), "schema_version: 2")
+            self.assertFalse(self.state.is_symlink())
+            self.assertEqual(stat.S_IMODE(self.state.stat().st_mode), 0o644 & ~umask)
+            self.assertEqual(target.read_bytes(), b"keep\n")
+
+    def test_tc22_a_failed_move_keeps_the_state(self):
+        self.write_state(V2_STATE.format(decision='"kept"'))
+        before = self.state.read_bytes()
+        module = load_script("update_state_tc22")
+        with mock.patch.object(module.os, "replace", side_effect=OSError(5, "Input/output error")):
+            code, out = self.run_main(module, ARGS)
+        self.assertEqual(code, 1, out)
+        self.assertIn(str(self.state), out)
+        self.assertEqual(self.state.read_bytes(), before)
+        self.assertEqual(self.names(), ["latest.yaml", "latest.yaml.lock"])
+
+    def test_tc25_a_move_or_a_removal_held_for_a_moment_is_tried_again(self):
+        module = load_script("update_state_tc25")
+        real_replace, real_remove = os.replace, os.remove
+        moves, removals = [], []
+
+        def move_held_twice(src, dst):
+            moves.append(src)
+            if len(moves) <= 2:
+                raise PermissionError(13, "held by another process")
+            return real_replace(src, dst)
+
+        def removal_held_twice(path):
+            removals.append(path)
+            if len(removals) <= 2:
+                raise PermissionError(13, "held by another process")
+            return real_remove(path)
+
+        with mock.patch.object(module.os, "replace", side_effect=move_held_twice), \
+                mock.patch("time.sleep"):
+            code, out = self.run_main(module, ARGS)
+        self.assertEqual(code, 0, out)
+        self.assertEqual(len(moves), 3)
+        self.assertEqual(self.text().splitlines()[0], "schema_version: 2")
+        self.assertEqual(self.names(), ["latest.yaml", "latest.yaml.lock"])
+
+        before = self.state.read_bytes()
+        with mock.patch.object(module.os, "replace", side_effect=OSError(5, "Input/output error")), \
+                mock.patch.object(module.os, "remove", side_effect=removal_held_twice), \
+                mock.patch("time.sleep"):
+            code, out = self.run_main(module, ARGS)
+        self.assertEqual(code, 1, out)
+        self.assertEqual(len(removals), 3)
+        self.assertEqual(self.state.read_bytes(), before)
+        self.assertEqual(self.names(), ["latest.yaml", "latest.yaml.lock"])
+
+        # A move held at every try: 10 tries, 9 pauses of 0.1 seconds, then exit 1 (UC-2 1b).
+        with mock.patch.object(module.os, "replace",
+                               side_effect=PermissionError(13, "held by another process")) as held, \
+                mock.patch("time.sleep") as pause:
+            code, out = self.run_main(module, ARGS)
+        self.assertEqual(code, 1, out)
+        self.assertEqual(held.call_count, 10)
+        self.assertEqual([call.args for call in pause.call_args_list], [(0.1,)] * 9)
+        self.assertEqual(self.state.read_bytes(), before)
+        self.assertEqual(self.names(), ["latest.yaml", "latest.yaml.lock"])
+
+
+class PatternTestCase(_RootCase):
+    """TASK 128 R3, SS-6: the reader is linear in a run of spaces (TC-23)."""
+
+    def test_tc23_a_run_of_spaces_is_read_in_linear_time(self):
+        spaces = " " * 100000
+        session, decision = "a" + spaces + "b", "c" + spaces + "d"
+        text = V2_STATE.format(decision=json.dumps(decision)).replace(
+            'session_id: "sid-127"', "session_id: " + json.dumps(session))
+        self.write_state(text)
+        start = time.monotonic()
+        proc = run_script(self.root, ARGS)
+        elapsed = time.monotonic() - start
+        self.assertEqual(proc.returncode, 0, output(proc))
+        self.assertLess(elapsed, 4.0, f"the run took {elapsed:.1f} s")
+        lists, _ = json_lists(self.text())
+        self.assertEqual(lists["recent_decisions"], [decision])
+        ids = [line for line in self.text().splitlines() if line.startswith("session_id: ")]
+        self.assertEqual([json.loads(line[len("session_id: "):]) for line in ids], [session])
+
+
+class HelperTestCase(unittest.TestCase):
+    """TASK 128 R4.1: the helper that decides the skip of the two SS-1 tests (TC-26)."""
+
+    def test_tc26_outer_git_names_the_nearest_root(self):
+        with tempfile.TemporaryDirectory() as tmp:
+            base = Path(tmp).resolve()
+            (base / "a" / ".git").mkdir(parents=True)
+            (base / "a" / "b" / "c").mkdir(parents=True)
+            self.assertEqual(outer_git(base / "a" / "b" / "c"), base / "a")
+            (base / "w" / "x").mkdir(parents=True)
+            (base / "w" / ".git").write_text("gitdir: /elsewhere", encoding="utf-8")
+            self.assertEqual(outer_git(base / "w" / "x"), base / "w")
+            (base / "n" / "m").mkdir(parents=True)
+            self.assertEqual(outer_git(base / "n" / "m"), outer_git(base))
+
+
+class PathFormTestCase(unittest.TestCase):
+    """TASK 128 R7.3: the session directory in the form of the platform (TC-27)."""
+
+    def test_tc27_the_session_directory_is_joined_by_the_platform(self):
+        import ntpath
+        source = SCRIPT.read_bytes()
+        module = types.ModuleType("update_state_tc27")
+        module.__file__ = str(SCRIPT)
+        with mock.patch("os.path", ntpath):
+            exec(compile(source, str(SCRIPT), "exec"), module.__dict__)
+        self.assertEqual(module.SESSION_DIR, ntpath.join(".agent", "sessions"))
+
+
+class EntryKindTestCase(unittest.TestCase):
+    """TASK 128 R2.1, R2.2: what the check counts as a link, or as another kind (TC-28)."""
+
+    def test_tc28_a_link_is_a_symbolic_link_or_a_name_surrogate(self):
+        module = load_script("update_state_tc28")
+        reparse = stat.FILE_ATTRIBUTE_REPARSE_POINT
+        directory = stat.S_IFDIR | 0o755
+        cases = [
+            ("a junction", fake_stat(directory, reparse, 0xA0000003), True, "is a link"),
+            ("a symbolic link", fake_stat(directory, reparse, 0xA000000C), True, "is a link"),
+            ("a cloud placeholder", fake_stat(directory, reparse, 0x9000001A), True, None),
+            ("a FIFO", fake_stat(stat.S_IFIFO | 0o644), False, "not a regular file"),
+            ("a file for the directory", fake_stat(stat.S_IFREG | 0o644), True, "not a directory"),
+        ]
+        for name, result, is_dir, message in cases:
+            with self.subTest(case=name), \
+                    mock.patch.object(module.os, "lstat", return_value=result):
+                if message is None:
+                    module._check_entry("entry", is_dir)
+                    continue
+                with self.assertRaises(module.StateError) as caught:
+                    module._check_entry("entry", is_dir)
+                self.assertIn(message, str(caught.exception))
+
+
 if __name__ == "__main__":
     unittest.main()
diff --git a/.agent/skills/skill-session-state/scripts/update_state.py b/.agent/skills/skill-session-state/scripts/update_state.py
index 0a6c27f..ebc187a 100644
--- a/.agent/skills/skill-session-state/scripts/update_state.py
+++ b/.agent/skills/skill-session-state/scripts/update_state.py
@@ -12,9 +12,14 @@ The bootstrap files run this script at each phase boundary. It takes an exclusiv
 - a file without `schema_version: 2` is read as the script before TASK 127 wrote it, and the
   next write stores the same strings in the new form.
 
+The script refuses a link, or an entry of another kind, at `.agent/sessions`, at the lock file
+and at `latest.yaml` (SS-3, TASK 128); a link above them, at `.agent` or a parent directory, is
+followed (TASK 128 D14). It writes a temporary file beside the state and moves it onto
+`latest.yaml` with `os.replace`, which replaces a link there and writes nothing through it.
+
 Exit codes: 0 the state was written; 1 no lock module, a lock that stayed held, a state file that
-is not UTF-8, or another error; 2 a usage error. In the first three cases of exit 1 the script
-writes nothing.
+is not UTF-8, a link or an entry of another kind, a failed write, or another error; 2 a usage
+error. In each case of exit 1 the script writes no state.
 """
 import os
 import sys
@@ -45,6 +50,8 @@ import argparse  # noqa: E402
 import datetime  # noqa: E402
 import json  # noqa: E402
 import re  # noqa: E402
+import stat  # noqa: E402
+import time  # noqa: E402
 import uuid  # noqa: E402
 
 # The lock module: `fcntl` where it imports, else `msvcrt` (TASK 127 D10).
@@ -59,8 +66,9 @@ except ImportError:
 else:
     msvcrt = None
 
-# Constants
-SESSION_DIR = ".agent/sessions"
+# Constants. The session directory is joined by the platform, so each path that the script
+# prints has one form of separator on Windows (TASK 128 R7.3).
+SESSION_DIR = os.path.join(".agent", "sessions")
 SESSION_FILE = "latest.yaml"
 SCHEMA_VERSION = 2
 #: Characters that `json.dumps(ensure_ascii=False)` leaves raw and a YAML double-quoted scalar
@@ -71,6 +79,15 @@ _YAML_UNSAFE = re.compile("[%s]" % "".join(
     for low, high in ((0x7F, 0x9F), (0x2028, 0x2029), (0xD800, 0xDFFF), (0xFFFE, 0xFFFF))))
 #: The version line; the reader takes it from the first line only (TASK 127 R3.3).
 _VERSION_LINE = re.compile(r"schema_version:\s*(\d+)\s*")
+#: `os.O_NOFOLLOW` where the platform has it; Windows has none (TASK 128 R2.3).
+_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
+#: The bit of a reparse tag that marks a name surrogate: a symbolic link or a junction
+#: (TASK 128 R2.2).
+_NAME_SURROGATE = 0x20000000
+#: A move or a removal that fails with `PermissionError` is tried this often, this many seconds
+#: apart (TASK 128 R2.5).
+_TRIES = 10
+_PAUSE = 0.1
 
 
 class StateError(Exception):
@@ -108,9 +125,11 @@ def get_session_path():
     """Get absolute path to session file."""
     return os.path.join(get_session_dir(), SESSION_FILE)
 
-def ensure_session_dir():
-    """Create the session dir; a second run that creates it at the same time is no error."""
-    os.makedirs(get_session_dir(), exist_ok=True)
+def ensure_session_dir(session_dir=None):
+    """Create the session dir; a second run that creates it at the same time is no error.
+
+    `main` passes the directory that it found once (TASK 128 R2.1)."""
+    os.makedirs(session_dir or get_session_dir(), exist_ok=True)
 
 # --- Minimal YAML reader (specific to our schema) ---
 # We ONLY need to preserve: session_id, active_blockers, recent_decisions, completed_tasks.
@@ -134,12 +153,17 @@ def _decode(raw, version):
 
 
 def _list_items(content, key, version):
-    """The items of the list `key`, each decoded by `_decode`."""
+    """The items of the list `key`, each decoded by `_decode`.
+
+    An item is taken to the end of its line, and its trailing whitespace is stripped. A lazy
+    capture before a pattern of trailing whitespace backtracks over a run of spaces in a quadratic
+    number of steps (SS-6, TASK 128 R3.1).
+    """
     section = re.search(r'^' + key + r':\s*\n((?:\s+-\s+.*(?:\n|$))*)', content, re.MULTILINE)
     if not section:
         return []
-    return [_decode(raw, version)
-            for raw in re.findall(r'^\s+-\s+(.*?)\s*$', section.group(1), re.MULTILINE)]
+    return [_decode(raw.rstrip(), version)
+            for raw in re.findall(r'^\s+-\s+(.*)$', section.group(1), re.MULTILINE)]
 
 
 def parse_simple_yaml(content):
@@ -156,9 +180,9 @@ def parse_simple_yaml(content):
         "completed_tasks": _list_items(content, "completed_tasks", version),
     }
     if version >= SCHEMA_VERSION:
-        sid = re.search(r'^session_id:\s*(.*?)\s*$', content, re.MULTILINE)
+        sid = re.search(r'^session_id:\s*(.*)$', content, re.MULTILINE)
         if sid:
-            data["session_id"] = _decode(sid.group(1), version) or None
+            data["session_id"] = _decode(sid.group(1).rstrip(), version) or None
     else:
         sid = re.search(r'^session_id:\s*[\'"]?([^\'"\n]+)[\'"]?', content, re.MULTILINE)
         if sid:
@@ -207,7 +231,7 @@ def read_state(fpath):
     if not os.path.exists(fpath):
         return {}
     try:
-        with open(fpath, "r", encoding="utf-8-sig") as f:
+        with open(fpath, "r", encoding="utf-8-sig", opener=_opener) as f:
             content = f.read()
     except UnicodeDecodeError as exc:
         raise StateError(f"{fpath} is not UTF-8 (byte {exc.start}: {exc.reason}); "
@@ -237,6 +261,91 @@ def _unlock(fd):
         msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
 
 
+def _check_entry(path, directory):
+    """Refuse `path` when it is a link, or when it exists and is not a directory (`directory`) or
+    a regular file (TASK 128 R2.1, R2.2).
+
+    A link is a symbolic link, or a reparse point whose tag is a name surrogate: a symbolic link
+    or a junction of Windows. A cloud or deduplication placeholder is no link. The attributes of
+    Windows are read with `getattr` on every platform; only Windows sets them.
+
+    Raises:
+        StateError: the message names the path.
+    """
+    try:
+        st = os.lstat(path)
+    except FileNotFoundError:
+        return
+    if stat.S_ISLNK(st.st_mode) or (
+            getattr(st, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
+            and getattr(st, "st_reparse_tag", 0) & _NAME_SURROGATE):
+        raise StateError(f"{path} is a link; remove it, or replace it with a directory or a "
+                         f"regular file of your own")
+    if directory and not stat.S_ISDIR(st.st_mode):
+        raise StateError(f"{path} is not a directory")
+    if not directory and not stat.S_ISREG(st.st_mode):
+        raise StateError(f"{path} is not a regular file")
+
+
+def _opener(path, flags):
+    """The opener of the read and of the write of the state (TASK 128 R2.3): the flags that `open`
+    hands it, `O_BINARY` on Windows among them, with `O_NOFOLLOW` on POSIX, and the permission
+    bits `0o600` for a file that it creates, so no other user opens it before `os.fchmod`."""
+    return os.open(path, flags | _NOFOLLOW, 0o600)
+
+
+def _retry(call, *args):
+    """`call(*args)`, tried again on `PermissionError`: at most `_TRIES` tries, `_PAUSE` seconds
+    apart (TASK 128 R2.5). On Windows a reader or a scan can hold a file for a moment."""
+    for attempt in range(_TRIES):
+        try:
+            return call(*args)
+        except PermissionError:
+            if attempt == _TRIES - 1:
+                raise
+            time.sleep(_PAUSE)
+
+
+def _write_state(fpath, text):
+    """Write `text` to a temporary file beside `fpath`, and move it onto `fpath` (TASK 128 R2.4 to
+    R2.6).
+
+    The temporary file is created exclusively, with the bits `0o600`. On POSIX it then takes the
+    bits of `fpath` when that is a regular file, and else `0o644` under the umask; a link swapped
+    in at `fpath` gives it no bits. It is synced and closed before the move. A failed write or
+    move closes the temporary file, removes it, and raises `StateError`.
+    """
+    tmp = os.path.join(os.path.dirname(fpath), f"{SESSION_FILE}.{uuid.uuid4().hex}.tmp")
+    try:
+        st = os.lstat(fpath)
+    except FileNotFoundError:
+        st = None
+    if st is not None and stat.S_ISREG(st.st_mode):
+        bits = stat.S_IMODE(st.st_mode)
+    else:
+        umask = os.umask(0)
+        os.umask(umask)
+        bits = 0o644 & ~umask
+    made = False
+    try:
+        with open(tmp, "x", encoding="utf-8", newline="\n", opener=_opener) as f:
+            made = True
+            if os.name == "posix":
+                os.fchmod(f.fileno(), bits)
+            f.write(text)
+            f.flush()
+            os.fsync(f.fileno())
+        _retry(os.replace, tmp, fpath)
+    except Exception as exc:
+        stays = ""
+        if made:
+            try:
+                _retry(os.remove, tmp)
+            except OSError as left:
+                stays = f"; the temporary file {tmp} stays: {left}"
+        raise StateError(f"could not write {fpath}: {exc}{stays}") from None
+
+
 def main():
     # The script's own messages never raise an encoding error on a console or a pipe whose
     # encoding cannot hold a path or a value (TASK 127 R2.2).
@@ -263,17 +372,24 @@ def main():
         sys.exit(1)
 
     try:
-        ensure_session_dir()
-        fpath = get_session_path()
+        # No entry of the state is a link, or of another kind (TASK 128 R2.1): the directory
+        # before anything is made, the lock file before its open, the state inside the lock.
+        # The directory is found once, so the one checked is the one used.
+        session_dir = get_session_dir()
+        _check_entry(session_dir, directory=True)
+        ensure_session_dir(session_dir)
+        fpath = os.path.join(session_dir, SESSION_FILE)
         # A separate lock file, opened with no truncation and at position 0 (TASK 127 R1.6).
         lock_path = fpath + ".lock"
-        fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
+        _check_entry(lock_path, directory=False)
+        fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | _NOFOLLOW, 0o644)
         try:
             try:
                 _lock(fd)
             except OSError as exc:
                 raise StateError(f"could not lock {lock_path}: {exc}") from None
             try:
+                _check_entry(fpath, directory=False)
                 # The one read of the state, inside the lock (TASK 127 R1.2).
                 latest_data = read_state(fpath)
 
@@ -311,9 +427,7 @@ def main():
                     "completed_tasks": final_completed,
                 }
                 yaml_content = generate_yaml(final_state)
-
-                with open(fpath, "w", encoding="utf-8", newline="\n") as f:
-                    f.write(yaml_content)
+                _write_state(fpath, yaml_content)
 
                 print(f"Session state updated: {fpath} (Locked)")
             finally:
diff --git a/.agent/tools/archive_move.py b/.agent/tools/archive_move.py
index bb51449..59c5557 100644
--- a/.agent/tools/archive_move.py
+++ b/.agent/tools/archive_move.py
@@ -31,10 +31,25 @@ import sys
 
 # Run as a script, its own directory leaves the import path before any other import, so a module
 # planted beside the script is never imported under the allow rule. A test that loads the module
-# keeps its own path (TASK 112 R1.8).
+# keeps its own path (TASK 112 R1.8). An entry is that directory when its real path, or its device
+# and inode, match the directory of the path as called or of the real path: a case-insensitive
+# volume reaches the directory in other letter case (ARC-13, the rule of TASK 127 R6.1).
 if __name__ == "__main__":
-    _HERE = os.path.dirname(os.path.realpath(__file__))
-    sys.path[:] = [entry for entry in sys.path if os.path.realpath(entry or os.curdir) != _HERE]
+    def _identity(path):
+        """`(st_dev, st_ino)` of `path`, or None where it cannot be read or has no inode."""
+        try:
+            st = os.stat(path)
+        except OSError:
+            return None
+        return (st.st_dev, st.st_ino) if st.st_ino else None
+
+    _DIRS = {os.path.dirname(os.path.abspath(__file__)),
+             os.path.dirname(os.path.realpath(__file__))}
+    _NAMES = {os.path.normcase(os.path.realpath(path)) for path in _DIRS}
+    _IDS = {_identity(path) for path in _DIRS} - {None}
+    sys.path[:] = [entry for entry in sys.path
+                   if os.path.normcase(os.path.realpath(entry or os.curdir)) not in _NAMES
+                   and _identity(entry or os.curdir) not in _IDS]
 
 import errno  # noqa: E402
 import json  # noqa: E402
diff --git a/.agent/tools/rebase_links.py b/.agent/tools/rebase_links.py
index 353b9b9..523b982 100644
--- a/.agent/tools/rebase_links.py
+++ b/.agent/tools/rebase_links.py
@@ -72,13 +72,28 @@ import sys
 # - its own directory leaves `sys.path`, so no file planted beside the script answers an import:
 #   not a standard-library name, not one the standard library lacks on this platform (`subprocess`
 #   imports `msvcrt` on POSIX), and not a sibling's name; the inbound mode loads its siblings by
-#   explicit path (`_load_siblings`);
+#   explicit path (`_load_siblings`). An entry is that directory when its real path, or its device
+#   and inode, match the directory of the path as called or of the real path: a case-insensitive
+#   volume reaches the directory in other letter case (ARC-13, the rule of TASK 127 R6.1);
 # - no bytecode is written, and `.pyc` files are looked up under the null device, where none can
 #   exist, so a `.pyc` planted in `__pycache__/` is never read.
 # The module has no `from __future__` statement: at run time it imports `__future__`.
 if __name__ == "__main__":
-    _HERE = os.path.dirname(os.path.realpath(__file__))
-    sys.path[:] = [entry for entry in sys.path if os.path.realpath(entry or os.curdir) != _HERE]
+    def _identity(path):
+        """`(st_dev, st_ino)` of `path`, or None where it cannot be read or has no inode."""
+        try:
+            st = os.stat(path)
+        except OSError:
+            return None
+        return (st.st_dev, st.st_ino) if st.st_ino else None
+
+    _DIRS = {os.path.dirname(os.path.abspath(__file__)),
+             os.path.dirname(os.path.realpath(__file__))}
+    _NAMES = {os.path.normcase(os.path.realpath(path)) for path in _DIRS}
+    _IDS = {_identity(path) for path in _DIRS} - {None}
+    sys.path[:] = [entry for entry in sys.path
+                   if os.path.normcase(os.path.realpath(entry or os.curdir)) not in _NAMES
+                   and _identity(entry or os.curdir) not in _IDS]
     sys.dont_write_bytecode = True
     sys.pycache_prefix = os.path.join(os.devnull, "rebase-links-pycache")
 
diff --git a/tests/_scratch.py b/tests/_scratch.py
index 408e010..0cf5933 100644
--- a/tests/_scratch.py
+++ b/tests/_scratch.py
@@ -22,10 +22,18 @@ timeout cannot execute its own teardown. The next session therefore removes subd
 whose owning process is **gone**, which recovers the debris without ever reaching into a
 live session. Keeping the tree out of `git status` is not this sweep's job — `.gitignore`
 already covers `tests/.scratch/`.
+
+**Why a session is also swept at exit.** Only pytest runs the hook of `tests/conftest.py`, so
+a unittest run left its session directory behind (TS-1). A session directory therefore
+registers an `atexit` handler when it is made. The handler holds that directory and its root
+as arguments and reads no global, so a second copy of this module that a test redirects
+touches only the root it was given (TASK 128 R6.1). A killed process runs no handler; the
+start-up sweep of the next pytest session collects what it leaves.
 """
 
 from __future__ import annotations
 
+import atexit
 import os
 import shutil
 import tempfile
@@ -96,14 +104,42 @@ def _remove(path: Path) -> None:
         pass
 
 
+def _sweep(session_dir: Path | None, root: Path) -> None:
+    """Remove `session_dir`, and `root` when it is then empty.
+
+    Both are arguments, so the `atexit` handler of a session removes the directory it was made
+    for, whatever this module names as its root at exit (TASK 128 R6.1).
+    """
+    if session_dir is not None:
+        _remove(session_dir)
+    try:
+        if root.is_dir() and not any(root.iterdir()):
+            root.rmdir()
+    except OSError:
+        pass
+
+
 def session_scratch() -> Path:
-    """Return this session's private scratch directory, creating it on first use."""
+    """Return this session's private scratch directory, creating it on first use.
+
+    A directory made here is removed at the exit of the process (TS-1). When `_ensure_root` or
+    `mkdtemp` raises `FileNotFoundError` or `FileExistsError`, a sweep of another process removed
+    the empty root meanwhile; the root is made again for one more try (TASK 128 R6.4). `mkdtemp`
+    raises `FileExistsError` itself only after it runs out of names, so one more try is safe.
+    """
     global _session_dir
     if _session_dir is None or not _session_dir.is_dir():
-        _ensure_root()
-        _session_dir = Path(
-            tempfile.mkdtemp(prefix=f"{SESSION_PREFIX}{os.getpid()}_", dir=REPO_SCRATCH)
-        )
+        for attempt in range(2):
+            try:
+                _ensure_root()
+                _session_dir = Path(
+                    tempfile.mkdtemp(prefix=f"{SESSION_PREFIX}{os.getpid()}_", dir=REPO_SCRATCH)
+                )
+                break
+            except (FileNotFoundError, FileExistsError):
+                if attempt:
+                    raise
+        atexit.register(_sweep, _session_dir, REPO_SCRATCH)
     return _session_dir
 
 
@@ -154,11 +190,5 @@ def sweep_stale_sessions() -> int:
 def sweep_session() -> None:
     """Remove only this session's scratch directory, and the root if it is now empty."""
     global _session_dir
-    if _session_dir is not None:
-        _remove(_session_dir)
-        _session_dir = None
-    try:
-        if REPO_SCRATCH.is_dir() and not any(REPO_SCRATCH.iterdir()):
-            REPO_SCRATCH.rmdir()
-    except OSError:
-        pass
+    _sweep(_session_dir, REPO_SCRATCH)
+    _session_dir = None
diff --git a/tests/test_archive_move.py b/tests/test_archive_move.py
index d314b42..96a1c13 100644
--- a/tests/test_archive_move.py
+++ b/tests/test_archive_move.py
@@ -20,7 +20,8 @@ Before TASK 112 two allow rules, `Bash(mv docs/TASK.md docs/tasks/*)` and
 * a source swapped during the move is refused on the link path and on the copy path, and a failed
   copy leaves no destination (``TC-A15`` to ``TC-A18``);
 * a failed check after the link leaves no destination; a module planted beside the script is not
-  imported, and loading the script keeps the caller's `sys.path`; a source that vanishes before
+  imported, through a path in other letter case either (ARC-13, TASK 128), and loading the script
+  keeps the caller's `sys.path`; a source that vanishes before
   its unlink, holds another file then, or cannot be checked, leaves the archive in place
   (``TC-A19`` to ``TC-A23``);
 * an existing letter-suffixed sub-task file in the destination's place is refused (``TC-A24``,
@@ -365,6 +366,22 @@ class TestLastSteps(ArchiveTestCase):
         self.assertEqual(result.returncode, 0, result.stderr)
         self.assertFalse(marker.exists(), "the planted json.py ran")
 
+    def test_a20_a_module_beside_the_script_through_other_letter_case(self):
+        # ARC-13: a volume that ignores letter case reaches the copy through a path in other case,
+        # and the path as called then differs from the real one (TASK 128 R1.3).
+        tools = Path(os.path.realpath(tempfile.mkdtemp()))
+        self.addCleanup(shutil.rmtree, tools)
+        shutil.copyfile(SCRIPT, tools / "archive_move.py")
+        marker = self.root / "planted-module-ran"
+        (tools / "json.py").write_text(f"open({str(marker)!r}, 'w').close()\n", encoding="utf-8")
+        variant = tools.parent / tools.name.swapcase() / "archive_move.py"
+        if not variant.exists():
+            self.skipTest("the volume tells letter case apart")
+        result = subprocess.run([sys.executable, str(variant), TASK, TASK_DEST],
+                                cwd=self.root, capture_output=True, text=True, timeout=60)
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertFalse(marker.exists(), "the planted json.py ran through other letter case")
+
     def test_a20_loading_the_script_keeps_the_callers_path(self):
         before = list(sys.path)
         sys.path.insert(0, str(SCRIPT.parent))
diff --git a/tests/test_concurrent_state.py b/tests/test_concurrent_state.py
deleted file mode 100644
index e84b789..0000000
--- a/tests/test_concurrent_state.py
+++ /dev/null
@@ -1,69 +0,0 @@
-
-import subprocess
-import time
-import os
-import sys
-
-# Path to update_state.py
-UPDATE_SCRIPT = ".agent/skills/skill-session-state/scripts/update_state.py"
-SESSION_FILE = ".agent/sessions/latest.yaml"
-
-def reset_session():
-    if os.path.exists(SESSION_FILE):
-        os.remove(SESSION_FILE)
-    if os.path.exists(SESSION_FILE + ".lock"):
-        os.remove(SESSION_FILE + ".lock")
-    
-    # Initialize
-    subprocess.run([
-        "python3", UPDATE_SCRIPT,
-        "--mode", "TEST",
-        "--task", "Init",
-        "--status", "Running",
-        "--summary", "Init"
-    ], check=True)
-
-def run_concurrent_updates():
-    print("Starting concurrent updates...")
-    
-    # Process A
-    p1 = subprocess.Popen([
-        "python3", UPDATE_SCRIPT,
-        "--mode", "TEST",
-        "--task", "Task A",
-        "--status", "Done",
-        "--summary", "Summary A",
-        "--add_completed_task", "Task A"
-    ])
-    
-    # Process B
-    p2 = subprocess.Popen([
-        "python3", UPDATE_SCRIPT,
-        "--mode", "TEST",
-        "--task", "Task B",
-        "--status", "Done",
-        "--summary", "Summary B",
-        "--add_completed_task", "Task B"
-    ])
-    
-    p1.wait()
-    p2.wait()
-    
-    print("Concurrent updates finished.")
-
-def verify():
-    with open(SESSION_FILE, 'r') as f:
-        content = f.read()
-        
-    print(f"Final Content:\n{content}")
-    
-    if "Task A" in content and "Task B" in content:
-        print("SUCCESS: Both tasks recorded.")
-    else:
-        print("FAILURE: Lost data.")
-        sys.exit(1)
-
-if __name__ == "__main__":
-    reset_session()
-    run_concurrent_updates()
-    verify()
diff --git a/tests/test_scratch_hygiene.py b/tests/test_scratch_hygiene.py
index 2a79760..82270d1 100644
--- a/tests/test_scratch_hygiene.py
+++ b/tests/test_scratch_hygiene.py
@@ -6,22 +6,24 @@ session start and corrupted concurrent runs; these tests exist so that cannot re
 unnoticed.
 
 Every test redirects the module's paths at a temporary location — nothing here touches the
-real `tests/.scratch`.
+real `tests/.scratch`. A process removes its own session directory at exit, by a handler bound to
+that directory and its root, so a unittest run leaves no scratch behind (TS-1, TASK 128).
 """
 
 import importlib.util
 import os
+import shutil
 import subprocess
 import sys
 import tempfile
 import unittest
 from pathlib import Path
+from unittest import mock
 
 PROJECT_ROOT = Path(__file__).parent.parent.resolve()
+SCRATCH = PROJECT_ROOT / "tests" / "_scratch.py"
 
-spec = importlib.util.spec_from_file_location(
-    "_scratch_uut", PROJECT_ROOT / "tests" / "_scratch.py"
-)
+spec = importlib.util.spec_from_file_location("_scratch_uut", SCRATCH)
 scratch = importlib.util.module_from_spec(spec)
 sys.modules["_scratch_uut"] = scratch
 spec.loader.exec_module(scratch)
@@ -140,6 +142,72 @@ class TestLegacyAndFailures(_Redirected):
         scratch._remove(self.root / "never-existed")
 
 
+class TestExitSweep(_Redirected):
+    """TC-H1 and TC-H2 (TASK 128 R6): a process sweeps its own session at exit, and a root that
+    another process swept meanwhile is made again."""
+
+    def test_h1_a_process_removes_its_session_at_exit(self):
+        # In a child process: `atexit` runs at its exit, and this process never calls
+        # `atexit._run_exitfuncs()`. The child names a second root before it exits; the handler
+        # of the first session must leave that root alone (R6.1).
+        base = Path(tempfile.mkdtemp())
+        self.addCleanup(shutil.rmtree, base, True)
+        first, second = base / "first", base / "second"
+        second.mkdir()
+        code = "\n".join([
+            "import importlib.util",
+            "from pathlib import Path",
+            f"spec = importlib.util.spec_from_file_location('scratch_child', {str(SCRATCH)!r})",
+            "mod = importlib.util.module_from_spec(spec)",
+            "spec.loader.exec_module(mod)",
+            f"mod.REPO_SCRATCH = Path({str(first)!r})",
+            "mod.LEGACY_SCRATCH = ()",
+            "mod.session_scratch()",
+            f"mod.REPO_SCRATCH = Path({str(second)!r})",
+        ])
+        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
+        proc = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True,
+                              text=True, timeout=60)
+        self.assertEqual(proc.returncode, 0, proc.stderr)
+        self.assertFalse(first.exists(), "the session directory or its root stayed")
+        self.assertTrue(second.is_dir(), "the handler removed the root named at exit")
+
+    def test_h2_a_root_swept_meanwhile_is_made_again(self):
+        # Another process removed the empty root between `_ensure_root` and `mkdtemp` (R6.4).
+        real, calls = tempfile.mkdtemp, []
+
+        def mkdtemp(*args, **kwargs):
+            calls.append(kwargs.get("dir"))
+            if len(calls) == 1:
+                scratch.REPO_SCRATCH.rmdir()
+            return real(*args, **kwargs)
+
+        with mock.patch.object(scratch.tempfile, "mkdtemp", side_effect=mkdtemp):
+            workspace = scratch.session_scratch()
+        self.assertTrue(workspace.is_dir())
+        self.assertEqual(len(calls), 2)
+
+    def test_h2_a_root_swept_inside_ensure_root_is_made_again(self):
+        # The sweep of another process can also land inside `_ensure_root`, which then raises
+        # `FileNotFoundError`, or `FileExistsError` from its `mkdir(exist_ok=True)` (R6.4).
+        for error in (FileNotFoundError(2, "No such file or directory"),
+                      FileExistsError(17, "File exists")):
+            with self.subTest(error=type(error).__name__):
+                scratch._session_dir = None
+                real, calls = scratch._ensure_root, []
+
+                def ensure_root():
+                    calls.append(True)
+                    if len(calls) == 1:
+                        raise error
+                    return real()
+
+                with mock.patch.object(scratch, "_ensure_root", side_effect=ensure_root):
+                    workspace = scratch.session_scratch()
+                self.assertTrue(workspace.is_dir())
+                self.assertEqual(len(calls), 2)
+
+
 class TestRunnerDoesNotSweep(unittest.TestCase):
     """The unittest runner must not touch in-repo scratch — it never creates any."""
 
diff --git a/tests/test_script_guards.py b/tests/test_script_guards.py
index 3ca9847..dd8393c 100644
--- a/tests/test_script_guards.py
+++ b/tests/test_script_guards.py
@@ -24,7 +24,8 @@ skill directory at any `--path` or path-shaped name. This file pins:
   (``TC-G28`` to ``TC-G30``, TASK 116 R8);
 * `rebase_links.py --inbound` refuses a file with a second hard link and skips a symbolic link,
   with exit 3 and no write; it rewrites a sub-task inside; neither a module nor a `.pyc`
-  planted beside the script runs (``TC-G8`` to ``TC-G12``, TASK 115);
+  planted beside the script runs (``TC-G8`` to ``TC-G12``, TASK 115), through a path in other
+  letter case either (ARC-13, TASK 128);
 * `init_skill.py` refuses a skill directory outside the working directory or under `.git/`, with
   exit 1 and nothing created (``TC-G4``, ``TC-G5``); a directory inside is created (``TC-G6``).
 
@@ -771,6 +772,24 @@ class TestInboundGuard(unittest.TestCase):
                 if (self.outside / f"sentinel-package-{name}").exists()]
         self.assertEqual(ran, [], "a module planted beside the script was imported")
 
+    def test_g11_a_planted_module_through_other_letter_case(self):
+        # ARC-13: a volume that ignores letter case reaches the copy through a path in other case,
+        # and the path as called then differs from the real one (TASK 128 R1.3).
+        tools = self._tools_copy()
+        planted = ("__future__", "re", "typing", "argparse", "json", "difflib", "subprocess",
+                   "msvcrt", "_winapi")
+        for name in planted:
+            sentinel = self.outside / f"sentinel-{name}"
+            (tools / f"{name}.py").write_text(f"open({str(sentinel)!r}, 'w').close()\n",
+                                              encoding="utf-8")
+        variant = tools.parent / tools.name.swapcase() / REBASE.name
+        if not variant.exists():
+            self.skipTest("the volume tells letter case apart")
+        result = self.inbound(variant)
+        self.assertIn(result.returncode, (0, 3), result.stdout + result.stderr)
+        ran = [name for name in planted if (self.outside / f"sentinel-{name}").exists()]
+        self.assertEqual(ran, [], "a module planted beside the script ran through other case")
+
     def test_g12_a_planted_pyc_is_never_read(self):
         import py_compile
         tools = self._tools_copy()
~~~~

- J2 step 3: each file that the patch edits or removes hashed to its value before the patch, the
  base. `git apply --whitespace=nowarn` of the patch exited 0.
- J2 step 4: each final file hashes to its staged copy and keeps the mode `644`;
  `tests/test_concurrent_state.py` does not exist; `git apply --check -R` passes.
- J2 step 5: `rm --` of each of the eight staged copies succeeded.
- J2 step 6, for the guard of J3: `latest.yaml`
  `6349a1bfc020ae7f203cfc73d6592382b5fb0ff1b7e8e77365e5b20790e7ed69`, `latest.yaml.lock`
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## The gates after stage 3 (PLAN J3)

- `gates.py`: `20 of 20 steps pass`; the test step of each Windows job gave `44 passed, 2 skipped,
  5 subtests passed`. The guard of J2 step 6 held after the gates.
- `regcheck.py`: `0 warn` on each of 15 documents. `bytescan.py`: each changed and created file is
  clean.
- The check of `framework-upgrade` §3 step 4, `j3.py j3`, exit 0:
  - item 1, eleven commands, each with equal listings:
    - `python3 -m pytest` from the root (`738 passed`), from `S/` (`36 passed, 2 skipped`), from
      `.agent/tools/` (`257 passed`), from `tests/` and from `S/scripts/`;
    - `python3 tests/run_tests.py`;
    - the local rule `ca2c33383ded254c` from the root and from `S/scripts/`;
    - the user rule `9fa5cad71668c6f7`, and the local rules `f42576bf00a2603c` and
      `7e089e2b18fca974`.

    The local discovery of `tests` left no `tests/.scratch/`, so TASK A6 holds;
  - `python3 -m pytest` from `tests/` exited 2: `tests/test_tool_runner.py` imports
    `System.scripts`, which only a run from the root with `PYTHONPATH=.` finds. The change does
    not touch that module, so this is a finding before the task, LOW;
  - item 2, each with equal listings:
    - `archive_move.py` with no operand (exit 2), and with refused operands (exit 1);
    - `rebase_links.py --help`, and its slot mode with `--dry-run` (`0 rewritten`);
    - its `--inbound` mode with `--dry-run`: exit 3, two records listed, as at Step 8 of §1;
  - item 3: the committed rule on the live state changed `latest.yaml` only;
  - item 4: `latest.yaml` renamed to `latest.yaml.keep-128`. Each run on the stand-in changed the
    stand-in only, each of the 15 user rules among them, and `--help` changed nothing. The
    stand-in with a byte-order mark was read and rewritten. The run with a link at the stand-in
    exited 1 with `is a link; remove it, or replace it with a directory or a regular file of your
    own`, and changed nothing. The stand-in that is not UTF-8 exited 1 and changed nothing;
  - item 5: the stand-in removed, `latest.yaml.keep-128` renamed back, and the session state
    recorded again through `update_state.py`.
- The live state after J3: `schema_version: 2` on its first line, the same `session_id`, 56
  completed tasks and 10 decisions, mode `644`; PyYAML parses it.
- `rules_check.py compare`: both settings files unchanged, and no new rule.
- Each of the 29 paths of `git status` is declared.

## Stage 4 (PLAN J4), at the fingerprint `450529b0abd5`: both pass

Each reviewer, resumed, computed `450529b0abd5` at its start and at its end, and ran its probes in
`wt-128/j4`, a copy of the live tree after stage 3, or in its own directories. After the round,
the guard listed `.agent/sessions/` the same, the scratchpad held no file of a reviewer, and the
run removed `wt-128/j4`.

- The `code-reviewer`: `APPROVED`, nothing in scope. `git diff 931d5b1 --binary` of the nine
  paths equals the patch byte for byte, each final file hashes to its staged copy, and nothing
  changed beyond the patch. It re-ran the gates of J3 in `j4`, and replayed items 2 to 4 of J3 on
  the final script in a scratch root. It confirmed that the exit 2 of a pytest run from `tests/`
  is a finding before the task. Five more tests fail there for the same reason:
  `tests/test_tool_runner_security_contract.py` reads its paths from the working directory, and
  so does `tests/test_schemas_stub.py`. A command of the reviewer printed the patch, and the
  harness kept that output in its session folder; the reviewer removed the file at once.
- The `security-auditor`: `PASS`, the scan complete, nothing in scope. What the allow rules run
  is the code of round 3 byte for byte, and the 15 user rules reach the same `update_state.py`
  through the link of `Universal-skills`. The runs of J3 on the live state and on the stand-in
  match the logs. The live state holds only `latest.yaml` and its lock, with no file of the
  stand-in left. The limits of D6, D13, D14 and D15 stand.

Neither reviewer could confirm the same `session_id` from the logs, which hold hashes only. The
run renamed `latest.yaml.keep-128`, the file of J3 item 3, back in place, and `update_state.py`
keeps the `session_id` of the file that it reads.

## Retro (PLAN K1)

`framework-upgrade` §6 with the run id `framework-upgrade-windows-ci-and-retro-records`, claimed at
the start of the run. The one question of `run-feedback` §7 listed four observed candidates. The
operator chose three and answered "это можно все сразу починить": fix them at once in the next
task, and file no record.

- `fnd-20261026-202627-0b47287a`: a pytest run from `tests/` fails to collect
  `tests/test_tool_runner.py`, and fails five tests that read their paths from the working
  directory;
- `fnd-20261026-202627-71891fc7`: the dependency advisories of stage 2, `npm audit` of the
  lockfiles of the mermaid renderers and CVE-2025-71176 of `pytest==9.0.2`;
- `fnd-20261026-202627-1c42d508`: `docs/ARCHITECTURE.md:120`, and `os.kill(pid, 0)` of
  `tests/_scratch.py` on Windows.

Each was collected into the inbox and dismissed with the reason "the operator chose at the retro of
TASK 128 (2026-10-26) to fix it at once in the next task, not to file it". The retro filed no
record and released its claim. The candidate that the operator did not choose, the boot read of
`latest.yaml` through a committed link, stays in this record only.
