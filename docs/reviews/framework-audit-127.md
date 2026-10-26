# Framework Audit 127 — `update_state.py` runs on Windows, and a failed run of it reaches the operator

- **Task:** 127 `session-state-windows`. It archives to
  `docs/tasks/task-127-session-state-windows.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1.
- **Date:** 2026-10-26. **Base revision:** `c6666c4a6cd251d7f0327ad0df57dd706a3104e3`, clean tree
  at start (TASK 126, committed by the operator as `c6666c4`).
- **Source:** a defect report of 2026-10-26 from a team that runs the framework on Windows 10, and
  the operator's answers of 2026-10-26 (TASK D1, D2).

## 0. Emergency Bypass

`[BYPASS_TIER_PROTECTION]`: `skill-session-state` is a TIER 0 skill. The change edits its
`SKILL.md` in place (TASK R4.3, R5) and its script and test module through the stage-3 patch
(TASK R1 to R3, R6). It removes no TIER 0 skill and no load of one. Mode B round 1 of the PLAN
found the record missing (m3); it was added then.

## Archive (§1)

TASK 126 archived under ID 126; it had no PLAN:
- `task_id_tool.py "lint-mermaid-package" --proposed-id "126" --no-correction`: `generated`,
  `task-126-lint-mermaid-package.md`;
- the move `"ok": true`, method `link`;
- Step 5.5: `0 rewritten / 0 needing review`, exit 0; Step 7 skipped at 7.1, no `docs/PLAN.md`;
- Step 8 with `--since ee278ca0b1340af8e53a09d6e9534a8fc1a42328`: exit 3. It lists two `INBOUND`
  records of old changelog entries (`CHANGELOG.md:3454`, `CHANGELOG.ru.md:3474`), which carry no
  reason and stay. Step 8 rewrote no file.

## Research (§1)

The runs of TASK §8 used a temporary root with its own `.git` in the session's scratchpad, and
wrote nothing in the tree. The base script ran from its tracked path; the scratchpad held the
`sitecustomize.py` that blocks `import fcntl`.

The retro claim `framework-upgrade-session-state-windows` was taken at the start of the run, and
the base was recorded in the session state before §1.

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

The reviewer, a `task-reviewer` agent with no shell, read the fingerprint `14f955c6dcbd` and wrote
nothing. It confirmed the claims of the TASK on `msvcrt.locking`, the YAML printable set, the
escapes of `json.dumps`, `surrogateescape`, the staged names, the line and version facts, and the
Python 3.11 floor. Its blocking finding:
- M1: TC-06 cannot pass on the CI platform. Under the locale of R7.3, Linux decodes the command
  line in ASCII with `surrogateescape`, so Cyrillic arrives as lone surrogates and the file stays
  ASCII. §8 measured macOS only.

Its other findings:
- m1: TC-09 contradicts the kept merge rules: an empty `--add_*` value records nothing,
  `recent_decisions` keeps 10 items, and each option takes one value per run;
- m2: R4.4, R5.2 and R5.3 had no criterion; `newline="\n"` and the uncollected staged copies had
  no check;
- m3: R8.6 lacked one command per option and input of the wildcard rule, the runs from `S/`
  before stage 3, and the count of the user's rules that run the script through a linked checkout;
- m4: R6.1 had to name the real directory, TC-12 lacked a run through a linked directory, and
  `fcntl`, `msvcrt` and `_winapi` were not planted;
- m5: R4.1 and R4.2 named no target section, and UC-4 lacked the cases with no task ID and the
  state ahead of `docs/TASK.md`;
- N1 to N8, notes:
  - the read before the lock, a byte-order mark, and the stand-in written at run time;
  - the effect of a revert, the read-only paragraph, the unedited registries and the restart;
  - a missing pin;
  - other directories of a bare pytest run, where the precedent of the root and `S/` was kept;
  - a workflow's own stop rules.

Before the task, one line each:
- a rule of the local settings runs Python code from its standard input (TASK 123 §9);
- the POSIX lock waits with no time limit;
- `tests/test_concurrent_state.py` rewrites the live state when run by hand.

TASK revision 2 applies M1, m1 to m5, N1 to N6 and N8; N7 keeps the precedent of TASK 124 (the
root and `S/`). It adds D13 (one read, inside the lock), D14
(`utf-8-sig`), TC-15, TC-16, TC-C1 to TC-C7 and A13. After it, the register scan finds no
warning and no note, and `check_positional_refs.py --all docs/TASK.md` reports `OK: 13 of 18
reference(s) in 1 document(s) resolve against the working tree (5 pinned, not checked).`

### Round 2 — TASK revision 2: PASS

The reviewer, resumed, read the fingerprint `8ec673d7fe8a`. It confirmed each fix of round 1 and
found no blocking finding. It corrected its own reasoning of m4. On POSIX, CPython applies
`realpath` to the script's path when it sets `sys.path[0]`, so only Windows leaves a linked path
unresolved there. A run through a linked directory still fails a filter that compares with an
`abspath` of the script's directory. Its findings to fix before planning:
- m1: R4.2 item 3 had no scope, so every session start whose first message names no task would
  ask the operator;
- N1: the open of the lock file was not named, and an `open(..., "a+")` starts at the file's end;
- N2: the option runs of R8.6 leave check values in the live state, which the script cannot
  remove;
- N3: `sys.pycache_prefix` guards nothing in a script that loads no sibling, and sends every
  standard-library import to its source;
- N4: the runs of R8.6 lacked a file that is not UTF-8 and a file with a byte-order mark;
- N5: no contract test checked Risk A of the guide;
- N6: two gaps of the RTM.

TASK revision 3 applies m1 and N1 to N6 with no further round, on the precedent of TASK 122 to
TASK 124. It adds D15 and R8.10. The checks of revision 3, as their tools print them:
- `scan_register.py docs/TASK.md --sections --terms docs/ARCHITECTURE.md`: `0 warn / 0 info`;
  `sentences : 394, mean 10.4, max 28 (limit 35)`;
- `check_positional_refs.py --all docs/TASK.md`: `OK: 13 of 18 reference(s) in 1 document(s)
  resolve against the working tree (5 pinned, not checked).`

The fingerprint of revision 3 is `6e59021bc198`.

## Architecture (§2.1)

`docs/ARCHITECTURE.md` names `msvcrt` beside `fcntl` at its two statements of the session-state
lock, lines 120 and 215 (TASK R8.8). No other structure changes: the script keeps its path, its
command line and its file. The register scan of `docs/ARCHITECTURE.md` reports no finding on
either line. The change is two lines of one existing statement each; no
`architecture-reviewer` round was run for it, and Mode B reviews it with the PLAN.

## The rules of the settings, read at §2.2 (TASK R8.7)

Read when §2.2 wrote PLAN revision 1. The record quotes no rule. The scratchpad's
`rules_127.json` holds the SHA-256 of each rule of both files, for J1 and J3 to find a new one.
- `.claude/settings.local.json`: 50 allow rules, SHA-256
  `48bbe25e64356acb4413474d0f1abf0212a13b32346206f44ae76345ca7c5f41`.
- The user's `~/.claude/settings.json`: 326 allow rules, SHA-256
  `1abd385154c514ae50ebbb05e18bc644d68bf0931d0843b344b23c4d59c313e6`.

Both files hash as at the reading of TASK 124. The rules of them that run files of the change,
named by the first 16 hex digits of the SHA-256 of each rule's text:
- local `ca2c33383ded254c`, unittest discovery over `tests/`, runs
  `tests/test_session_state_contract.py`;
- user `9fa5cad71668c6f7`, unittest discovery over the `scripts/tests` of the directory it runs
  in. Run from `.agent/skills/skill-session-state/`, it runs `test_update_state.py`, and through
  it `update_state.py`;
- 15 user rules run `update_state.py` by an absolute path in a sibling checkout, whose skill
  directory links into this repository: `ed9b841f7a28c589`, `c9d9a3441dddbd5b`,
  `2ebfd9ef5b8ec4ac`, `f6edd29f20df2611`, `9dacc267acf0870d`, `b5816440fd190330`,
  `9ef6002cd601ad92`, `4d7430ff38747bab`, `16c51563e1e6f68c`, `9fcb20f312f9bc80`,
  `e6248792a91c56bf`, `89419a8af553ca90`, `cafa3967b5c114ee`, `838a9db8fdcb691a`,
  `ad94d8ffaa294f28`;
- local `6d2a76ee469828a5` names `update_state.py` under a path that does not exist, and runs
  nothing.

The rules that run whatever code their command line or standard input holds stay as TASK 123 §9
names them.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: FAIL

The reviewer, a `plan-reviewer` agent with no shell, read the fingerprint `abb9360ade7a` and wrote
nothing. Coverage, stub-first, atomicity and the order of the clusters passed. Its blocking
finding:
- M1: J3 exempted the state file for every command of the check, the test runs of item 1 among
  them. A test that rewrote the live `latest.yaml` would then pass; TASK 122 recorded that case.

Its other findings:
- m1: an exit inside J3 item 3 left the live state aside, and the Failure path kept the stand-in;
- m2: the stand-in before each run of item 3 was not stated, and the file that is not UTF-8 came
  before the 15 user rules;
- m3: the audit's §0 lacked `[BYPASS_TIER_PROTECTION]`, as TASK 111, 112, 115 and 116 recorded;
- m4: J1 and J3 did not handle a changed settings file with no new allow rule;
- m5: nothing checked the test modules under Python 3.11, the lower version of the CI matrix;
- m6: the live state was unguarded during the runs that no listing checks;
- N1 to N10, notes:
  - the stale reference line, three coverage gaps, and the proofs of `mutate.py`;
  - the refresh and removal of the mirror, the filter in B2, and the first live run;
  - the arguments and value forms of the checks, and the place of the WI-39 note;
  - the task files, and three gaps at the TASK level.

Before the task: nothing beyond the three lines of Mode A round 1.

PLAN revision 2 applies M1, m1 to m6 and N1 to N10. It adds the live-state guard, the byte scan,
K2, and the steps of J3 for the stand-in. TASK revision 4 follows it:
- m2 and N7: the order of the stand-in runs, the arguments of the live runs, and the value forms;
- N8: the WI-39 note after the provenance banner;
- N10: the two runs from `S/scripts/`, the planted list from the script's imports, and TC-17;
- R1.9 and D16: a defect that the dev mirror measured before B1. TC-01 of the new test module
  failed in 3 of 25 runs against the base script, with `FileExistsError` on `.agent/sessions`.

`rules_check.py` now records one SHA-256 per top-level key, and its `compare` exits 2 on a changed
file with no new allow rule (m4). The reading was taken again for PLAN revision 2: both files
hash as at the reading of §2.2.

The byte scan of PLAN revision 2 has a cause in this run. A tool input that held a backslash, `u`
and four hex digits was decoded into the character it names. Four such characters reached a draft
of the script in the scratchpad, U+2028 and U+2029 among them, and a test value lost its
escapes. Both drafts were
rewritten without such escapes before B1, and the scan of TASK, PLAN, ARCHITECTURE and this
record finds nothing.

The checks of revision 2, as their tools print them:
- `scan_register.py docs/PLAN.md --sections --terms docs/ARCHITECTURE.md`: `0 warn / 1 info`;
  the note is one 32-word list item of J3 with one claim;
- `check_positional_refs.py --all docs/PLAN.md`: `OK: 11 of 12 reference(s) in 1 document(s)
  resolve against the working tree (1 pinned, not checked).`;
- `plan_gantt.py docs/PLAN.md --check docs/PLAN.md`: `docs/PLAN.md: plan chart is current`;
- TASK revision 4: `0 warn / 0 info`; `OK: 14 of 19 reference(s) in 1 document(s) resolve against
  the working tree (5 pinned, not checked).`

### Round 2 — PLAN revision 2: PASS

The reviewer, resumed, read the fingerprint `e529a25d6740` of the PLAN and `6179aed2b9d8` of the
TASK. It confirmed each fix of round 1 and found no blocking finding and no finding to fix before
execution. Its notes:
- N1: the live-state guard missed the runs of B2 and the gates and tests of H2;
- N2: the system Python 3.9 has no PyYAML, so its run cannot check R3.7, and the draft returned
  silently where PyYAML was missing;
- N3: B3 parsed the contract test, which C1 writes;
- N4: R1.9 had no test that fails every time;
- N5: the scratchpad held probes that the PLAN did not name;
- N6: a full draft of the script predates B1;
- N7: the committed `python -m pytest` rule was outside R8.6;
- N8: Failure step 1 could fail on a stand-in that J3 had removed.

PLAN revision 3 and TASK revision 5 apply them with no further round, on the precedent of TASK 122
to TASK 124:
- N1, N3, N8: the guard covers every run of the staged or new test module outside a check; B3
  parses the script and the staged test module; Failure step 1 removes the stand-in when present;
- N2: each test that reaches a PyYAML check reports a skip where PyYAML is missing, and H2
  records that its run reported none;
- N4: TC-18 and the mutation `exist_ok=True` removed;
- N5: the probes that held copies were removed before B1:
  - `dryrun-127/`, the copies of the eight documents of C for a dry run of `apply_c.py`;
  - `mirror-127-base/`, a copy of the base script and of the draft test module, for TASK §8
    run 6;
  - `mirror-127-mut/`, one mutation of the draft.
  `probe-127/` holds the temporary roots of TASK §8 and no copy of a repository file;
- N6: the dev mirror held a full draft of the script and the test module before B1, and TASK §8
  run 6 measured them. B1 writes the staged test module from that draft. B2 writes a stub, not
  the draft, and B3 the logic;
- N7: `python` and `python3` resolve to one interpreter here,
  `~/.pyenv/versions/3.14.8/bin/python` and `.../python3`, so the runs of `python3 -m
  pytest` stand for both spellings of the committed rule.

The checks of the revisions, as their tools print them:
- PLAN revision 3: `0 warn / 1 info` (a 31-word list item); `OK: 11 of 12 reference(s) in 1
  document(s) resolve against the working tree (1 pinned, not checked).`; `plan chart is current`;
  fingerprint `d24ac8908ddc`;
- TASK revision 5: `0 warn / 0 info`; `OK: 14 of 19 reference(s) in 1 document(s) resolve against
  the working tree (5 pinned, not checked).`; fingerprint `4c3fb3068d20`.

## Execution (§3)

### A — base check and the rules of the settings

- A1: `HEAD` equals the base, and each of the 16 declared paths passes the checks of
  `framework-upgrade` §3.1. No created path existed before its step.
- A2: `rules_check.py compare`: both settings files hash as at the reading of §2.2, with no new
  rule.

### B — stage 1: the copies

- B1: `S/scripts/tests/staged_test_update_state.py`, from the draft of the dev mirror, SHA-256
  `7e07dd15362bd451…`. Run by its path with pytest from the root, against the base script, 14
  fail and 10 pass, as the PLAN states:
  - fail: TC-01, TC-03 to TC-12, TC-14, TC-15 and TC-18. TC-01 failed with `FileExistsError` on
    `.agent/sessions`, the race of R1.9; on a second run it passed. TC-18 fails every time;
  - pass: the 6 SS-1 tests, TC-02, TC-13, TC-16 and TC-17.
- B2: the stub, from the draft with four marked stubs: no `sys.path` filter, the base form of the
  encoder, and `fcntl` only in both lock helpers. In the dev mirror, the 6 SS-1 tests and TC-13
  pass, and `--help` exits 0.
- B3: `S/scripts/staged_update_state.py`, SHA-256 `b3f232f5dfb074d3…`, with the logic and the
  filter. In the dev mirror, the staged test module passes 24 of 24. The script and the staged
  test module parse with `feature_version=(3, 11)`. Under the system Python 3.9.6 with `unittest`,
  24 tests run and pass, 5 of them reported as skipped at their PyYAML check: 3.9 has no PyYAML.
  The mirror was then removed.
- The live-state guard held around each run of B: `latest.yaml` and `latest.yaml.lock` hashed as
  before.

### C — the documents in place

- C1: `tests/test_session_state_contract.py`. Against the live tree, TC-C1 to TC-C6 failed, each
  with one line that names the missing text, and TC-C7 passed. The first version of its failures
  printed whole files; the assertions were rewritten before C2.
- C2 to C5 and C7: `apply_c.py`, one exact replacement per edit. A dry run on copies of the eight
  documents had passed the contract test before the step; the copies were then removed.
- C6: the contract test passes 7 of 7 on the live tree, and parses with `feature_version=(3, 11)`.
- `regcheck.py` finds no warning on an added line of the eight documents, and `bytescan.py` finds
  nothing in them.

### D — records in place

- D1: v3.47.0 in `CHANGELOG.md` and `CHANGELOG.ru.md`. `regcheck.py`: no warning, one note of
  33 words on one claim. `check_positional_refs.py --all` on both: 0 errors; its 2 warnings name
  old entries of `CHANGELOG.ru.md`.

### E — the patch

- E1: `wt.sh gen` wrote `docs/reviews/framework-audit-127-stage3.diff`, 974 lines, two file
  sections and no staged path; `git apply --check` passes. The SHA-256 values:
  - the patch: `b0ad96c39aac1d133111b39364e65f8c46ee4347b31c5993963a0c192ac6c649`;
  - staged copy `S/scripts/staged_update_state.py`:
    `b3f232f5dfb074d31b20ff54dd6e5a24ee83b0bc7ff5cf0516a90af1f722f37e`;
  - staged copy `S/scripts/tests/staged_test_update_state.py`:
    `7e07dd15362bd451c7dafcf78388cf8664375d3f008bf37fda09854f634d93a5`;
  - before the patch, `S/scripts/update_state.py`:
    `4fb99b553f8b2dda74c69b7edd115e5e442259ab648c093e461e0609b52bb3aa`;
  - before the patch, `S/scripts/tests/test_update_state.py`:
    `46d8599fb37a9c3ba40c00e0afe2c6b6fe96ba97c659b3d56bafb92a0aff4b3c`;
  - after the patch, each final file hashes to its staged copy (H2).

### H — the checks before stage 3

- H1, on the live tree:
  - `gates.py`: 18 of 18. The pytest step passes 548 tests, 13 more than at the base: the 6 SS-1
    tests that the step now names and the 7 of the contract test;
  - `git diff --quiet <base>` exits 0 for `System/Docs/SKILLS.md` and `System/Docs/WORKFLOWS.md`;
  - `list_tests.py`: pytest's `--co` from the root and from `S/`, and the unittest discoveries of
    `tests` and of `scripts/tests`, list no staged file; no `tests/.scratch/` was left;
  - `regcheck.py`: no warning on an added line of TASK, PLAN, the eight documents and the
    changelogs. Six warnings of this record were rewritten first;
  - `bytescan.py` of the 18 changed and created files finds nothing;
  - each of the 18 paths of `git status` is declared.
- H2, in the worktree `patched/` that `wt.sh make` built:
  - `gates.py`: 18 of 18; the pytest step passes 566 tests, the new module and the contract test
    among them;
  - `S/scripts/tests/test_update_state.py` passes 24 of 24 with no skip, so PyYAML imported there;
  - `tests/test_mock_agent.py` passes;
  - `mutate.py`: each of the 8 mutations of the PLAN made its test fail, and the worktree's
    script hashed as before at the end;
  - `wt.sh remove` removed the worktree, and `git worktree list` names it no more. The run wrote
    nothing in the tree from `wt.sh make` to the end of H2, and the live-state guard held.
- H3, the check of `framework-upgrade` §3 step 4 before stage 3, with `check.py`, 4714 entries:
  - `python3 -m pytest` from the root: equal listings, 732 passed;
  - `python3 -m pytest` from `S/`: equal listings, 6 passed;
  - `python3 tests/run_tests.py`: equal listings;
  - `python3 -m unittest discover -s tests -v`: two empty directories added, `tests/.scratch/` and
    a session directory in it. `session_scratch()` of `tests/_scratch.py` creates both, as TASK
    123 and TASK 124 recorded; no file of the change imports that module. It is a finding before
    the task, and no difference of the stop rule. The put-back removed both with `rmdir --`, the
    inner one first;
  - `python3 -m unittest discover -s scripts/tests` from `S/`: equal listings, 6 tests.

Before the task, one line: `git worktree list` names two worktrees of earlier sessions under
other scratchpads, both `prunable`. The run leaves them.

## Stage 2 — reviews

### Round 1, at the fingerprint `b4b5fdfe49bc`: both PASS

Each reviewer computed the fingerprint at its start and at its end, and found `b4b5fdfe49bc`
both times; neither wrote in the tree.

The security audit passed. `run_audit.py . --scan-type all` ran to completion, `scan_complete`
`true`, with no tool error. Its hits in the change are two `SQL f-string` hits of the regex
scanner at lines 167 and 303 of the staged script, checked by hand as false: the word `updated`
in an f-string. Bandit reports B404 and B603 at LOW in the test module. Its findings in scope:
- S-1, MEDIUM: on a case-insensitive volume, the `sys.path` filter misses a script path whose
  letter case differs from the case on disk. CPython builds `sys.path[0]` with `realpath(3)`,
  which returns the case on disk, while `posixpath.realpath` keeps the case as typed. Reproduced
  on macOS with a planted `json.py`. Not a regression: the base imported a planted module on every
  run;
- S-2, LOW: TC-13 and TC-18 load the script with `importlib`, which reads and writes
  `scripts/__pycache__/` beside it;
- S-3, LOW: this record named a path under the operator's home directory;
- S-4, LOW: `json.loads` joins the escapes of a high and a low surrogate into one character, so the
  reader and PyYAML disagree on such a pair. The command line cannot produce one.

The code review passed: "MERGE". It reproduced S-1 as CR-1, and checked R1.1 to R8.8 and A1 to
A12 on a patched copy. Its findings in scope:
- CR-1, MEDIUM: S-1;
- CR-2, MEDIUM: only TC-01 catches a read before the lock, and only when its runs race. A mutant
  that reads before `_lock` failed TC-01 in 11 of 20 runs;
- CR-3, LOW: S-2;
- CR-4, LOW: no test fails when `.strip()` of the summary is removed;
- CR-5, LOW: TC-C1 pins the trigger of the failure rule and "by hand", not the duty to tell the
  operator;
- CR-6, LOW: the disagreement step of the bootstrap files does not say that it follows a
  restored state, and the guide's items 5 and 6 omit parts of the rules;
- CR-7, LOW: the version line matches any line of the file, not the first;
- CR-8, LOW: the script's docstring says that exit 1 writes nothing, and one line of
  `SKILL.md` is not wrapped.

Before the task, one line each:
- MEDIUM: the write of `latest.yaml` follows a link planted at that name, as at the base; the
  change keeps the lock file's target intact, where the base truncated it. A Windows host now
  reaches the write, since the script now runs there;
- LOW: the item regex of the reader is quadratic in a run of spaces, as at the base;
- LOW: a `PYTHONPATH` that names the script's directory runs a planted module at interpreter
  start, before any filter (WI-39 option 2);
- LOW: the SS-1 tests `test_no_git_*` write the state of an ancestor repository when `TMPDIR`
  lies inside a git work tree;
- LOW: the committed allow rule names the script by a relative path (WI-34);
- LOW: the guide calls the write atomic; the lock serialises writers, and the write is in place.

The reviewers' probes in the scratchpad held copies of repository files: `focus/`, `patchcheck/`,
`cr127/` and `probes/`. The run removed them with the other probes when the round ended.

### Fix round 1 (TASK D17)

Both reviews passed; the run fixes their findings in scope before registration, and a second
round reviews the fix. S-1 and CR-1 are one finding.

Red first. The edits of the staged test module (TC-02, TC-10, TC-12, TC-13, TC-14, TC-18), run
against the staged script of round 1 in the dev mirror: TC-10 and TC-12 fail, and 22 pass.
TC-10 fails on the escape `C:` backslash `new` backslash `tab`, which a version 2 read decodes;
TC-12 fails on its run in other letter case. TC-02 and TC-14 pass there, and their mutations
below make them fail.

The fixes:
- `staged_update_state.py`:
  - the filter matches the directory as called and as resolved, by real path and by device and
    inode (S-1, CR-1);
  - the version line is read from the first line only (CR-7);
  - the docstring names the exits of code 1 that write nothing (CR-8);
- `staged_test_update_state.py`:
  - `load_script` compiles the script in memory for TC-13 and TC-18, so no `__pycache__/` appears
    beside it (S-2, CR-3);
  - TC-02 writes a marker while the run waits (CR-2), and TC-14 checks the strip (CR-4);
  - TC-12 runs through a path in other letter case and through a linked file;
- `tests/test_session_state_contract.py`: TC-C1 pins "the operator in the same reply" (CR-5);
- the three bootstrap files, the guide and `S/SKILL.md`: the wording of CR-6 and CR-8;
- the changelogs: the WI-39 line names how the directory is matched;
- this record: the path under the operator's home directory became `~/...` (S-3).

The checks after the fixes:
- the dev mirror: 24 of 24 on Python 3.14.8; under the system Python 3.9.6, 24 run and pass, 5
  of them skipped at their PyYAML check; no `__pycache__/` beside the script; both modules parse
  with `feature_version=(3, 11)`;
- `mutate.py`: 11 mutations, each caught. "The check of device and inode removed" took the place
  of "`realpath` replaced by `abspath`". After the fix the two checks cover each other, and the
  check by device and inode covers every run of TC-12 alone;
- the contract test passes 7 of 7; `regcheck.py` finds no warning on an added line; `bytescan.py`
  finds nothing;
- E1, again: the patch `25a5bd8ea85fb59e5ac02204e8520f69520b22a8b466d9652cb6b8c5751318cf`, 1026
  lines, two sections, `git apply --check` passes. Staged copies:
  `staged_update_state.py` `0e46785beb33cedb10547380d1990e8d065f0ec14a1d8bcfb32c3eb456f706c8`,
  `staged_test_update_state.py` `5bb50d7f20725829444cee1341cfa6debeffeb2bba1204b9e41a3933adfbc316`.
  The final files before the patch hash as at E1 of round 1;
- H1, again: `gates.py` 18 of 18; `list_tests.py` lists no staged file;
- H2, again: in the patched worktree, `gates.py` 18 of 18, the test module 24 of 24 with no skip,
  `tests/test_mock_agent.py` passes, and the 11 mutations are caught; the worktree was removed;
- H3, again: the five commands give the results of round 1. The local unittest discovery of
  `tests` again added the two empty directories of `tests/_scratch.py`, and the put-back removed
  them.

The live-state guard held around each run of the round.

### Round 2, at the fingerprint `01e3a44fb48d`: both PASS, and stage 2 closes (TASK D18)

Each reviewer computed `01e3a44fb48d` at its start and at its end, wrote nothing in the tree, and
removed its own scratch directory.

The security audit confirmed S-1 to S-3 as fixed and S-4 as stated. Its probes of round 1, run
against the new script, ran no planted module: 81 module names, seven ways to call the script,
three case-only renames, and an emulation of a linked file on Windows. Its scan ran in full; its
new hit, `exec()` in `load_script`, and the two `SQL f-string` hits are false. Its findings:
- N-1, LOW: a volume with no inode numbers leaves the check by name alone;
- N-2, LOW: on POSIX the run of TC-12 through a linked file passes with or without the check
  of the directory as called.

The code review confirmed CR-1 to CR-8 as fixed, each by a run or a mutation, and found no
regression in the fix. The new filter keeps a zip, a missing entry, a file and an unrelated
directory. It removes the script's directory under each spelling. Its findings:
- N-1, LOW: TC-13 fails on a removed `__main__` guard only from `S/scripts/`;
- N-2 to N-4, notes:
  - the check by name has no test where inode numbers are missing;
  - the check by device and inode assumes a unique pair;
  - the positional references of the bootstrap files moved, which J1 repairs.

No finding breaks a requirement or a run. Under the operator's rule recorded at TASK 124 D17, the
run states each as a limit in TASK D18 and closes stage 2 at round 2, with no backlog record.

## Stage 3 (PLAN J2)

J1, §4.5: `check_positional_refs.py --targets-changed` reports 0 errors and 30 `DRIFT_SUSPECT`
warnings, each in an archived document that cites a line of a file this change edits. `--fix`
repaired nothing: no reference was `REFERENT_MOVED`. `rules_check.py compare`: both settings files
hash as at the reading of §2.2, with no new rule.

Before the patch, as I1 quoted them:
- the patch `docs/reviews/framework-audit-127-stage3.diff`:
  `25a5bd8ea85fb59e5ac02204e8520f69520b22a8b466d9652cb6b8c5751318cf`;
- staged copy `S/scripts/staged_update_state.py`:
  `0e46785beb33cedb10547380d1990e8d065f0ec14a1d8bcfb32c3eb456f706c8`;
- staged copy `S/scripts/tests/staged_test_update_state.py`:
  `5bb50d7f20725829444cee1341cfa6debeffeb2bba1204b9e41a3933adfbc316`;
- `S/scripts/update_state.py`, mode `100644`:
  `4fb99b553f8b2dda74c69b7edd115e5e442259ab648c093e461e0609b52bb3aa`;
- `S/scripts/tests/test_update_state.py`, mode `100644`:
  `46d8599fb37a9c3ba40c00e0afe2c6b6fe96ba97c659b3d56bafb92a0aff4b3c`.

The patch:

~~~~diff
diff --git a/.agent/skills/skill-session-state/scripts/tests/test_update_state.py b/.agent/skills/skill-session-state/scripts/tests/test_update_state.py
index ba98fa5..b8531db 100644
--- a/.agent/skills/skill-session-state/scripts/tests/test_update_state.py
+++ b/.agent/skills/skill-session-state/scripts/tests/test_update_state.py
@@ -1,15 +1,264 @@
-"""SS-1 regression: update_state.py must anchor .agent/sessions at the repo
-root regardless of the invocation CWD (docs/issues/ss-1-*.md)."""
+"""Tests of `update_state.py`.
+
+SS-1 regression: update_state.py must anchor .agent/sessions at the repo root regardless of the
+invocation CWD (docs/issues/ss-1-*.md). TASK 127: the lock on POSIX and on Windows, UTF-8, the
+escaped scalars and their round trip, and the import path (WI-39); TC-01 to TC-18 of its §5.
+
+Each test runs the script in a temporary root that holds its own `.git`, and no test writes
+under the repository. The Windows branch runs on POSIX: a test writes, into a temporary
+directory, a `sitecustomize.py` that blocks `import fcntl` and provides a `msvcrt` stand-in on
+`fcntl.lockf`, and puts that directory on `PYTHONPATH`. PyYAML checks each written file as a
+second reader; where it does not import, each test that reaches such a check reports a skip.
+"""
+import ast
+import json
 import os
+import py_compile
+import re
 import subprocess
 import sys
 import tempfile
+import time
+import types
 import unittest
 from pathlib import Path
 
+try:
+    import fcntl
+except ImportError:  # Windows: the tests that hold a POSIX lock skip
+    fcntl = None
+try:
+    import yaml
+except ImportError:  # PyYAML is a second reader only
+    yaml = None
+
 SCRIPT = Path(__file__).resolve().parents[1] / "update_state.py"
 ARGS = ["--mode", "Test", "--task", "t", "--status", "s", "--summary", "x"]
 
+#: The `sitecustomize.py` of the Windows branch (TASK 127 R7.2). `MSVCRT_STANDIN=1` blocks
+#: `import fcntl` and provides `msvcrt`, whose `locking` logs `<mode> <offset> <nbytes>` to
+#: `MSVCRT_STANDIN_LOG` and takes `fcntl.lockf` on the same bytes. `LK_LOCK` tries
+#: `MSVCRT_STANDIN_TRIES` times, like the 10 tries of the real one, and then raises `OSError`.
+#: `MSVCRT_STANDIN_BLOCK` names more modules to block.
+SITECUSTOMIZE = r'''
+import errno
+import os
+import sys
+import time
+import types
+
+_BLOCKED = {"fcntl"} | set(filter(None, os.environ.get("MSVCRT_STANDIN_BLOCK", "").split(",")))
+for _name in _BLOCKED - {"fcntl"}:
+    sys.modules.pop(_name, None)
+
+if os.environ.get("MSVCRT_STANDIN") == "1":
+    import fcntl as _real
+    del sys.modules["fcntl"]
+    _LOG = os.environ.get("MSVCRT_STANDIN_LOG")
+    _TRIES = int(os.environ.get("MSVCRT_STANDIN_TRIES", "10"))
+    msvcrt = types.ModuleType("msvcrt")
+    msvcrt.LK_UNLCK, msvcrt.LK_LOCK, msvcrt.LK_NBLCK, msvcrt.LK_RLCK, msvcrt.LK_NBRLCK = range(5)
+
+    def locking(fd, mode, nbytes):
+        offset = os.lseek(fd, 0, os.SEEK_CUR)
+        if _LOG:
+            with open(_LOG, "a", encoding="utf-8") as fh:
+                fh.write(f"{mode} {offset} {nbytes}\n")
+        if mode == msvcrt.LK_UNLCK:
+            _real.lockf(fd, _real.LOCK_UN, nbytes, offset, os.SEEK_SET)
+            return
+        for _ in range(_TRIES):
+            try:
+                _real.lockf(fd, _real.LOCK_EX | _real.LOCK_NB, nbytes, offset, os.SEEK_SET)
+                return
+            except OSError:
+                time.sleep(0.05)
+        raise OSError(errno.EDEADLK, "Resource deadlock avoided")
+
+    msvcrt.locking = locking
+    sys.modules["msvcrt"] = msvcrt
+else:
+    sys.modules.pop("fcntl", None)
+
+
+class _Block:
+    def find_spec(self, name, path=None, target=None):
+        if name in _BLOCKED:
+            raise ModuleNotFoundError(f"No module named {name!r}", name=name)
+        return None
+
+
+sys.meta_path.insert(0, _Block())
+'''
+
+#: TC-09: one value per run, each a case of TASK 127 §5.
+ROUND_TRIP_VALUES = [
+    'q"q', "b\\b", "n\\nn",
+    "l\nl", "c\rc", "t\tt", "d\x7fd", "x\x85x", "y\x93y", "z\u2028z",
+    "Тест", "e\U0001F600e",
+    "k: v", "# h", " lead",
+    "s\udcffs",
+]
+
+#: A version 2 state file whose decision holds Cyrillic and an arrow (TC-06), and one whose
+#: decision holds escaped quotes (TC-15).
+V2_STATE = """schema_version: 2
+session_id: "sid-127"
+last_updated: "2026-10-26T00:00:00"
+mode: "M"
+
+current_task:
+  name: "t"
+  status: "s"
+  predicted_steps: 0
+
+context_summary: "x"
+
+active_blockers:
+  []
+
+recent_decisions:
+  - {decision}
+
+completed_tasks:
+  []
+"""
+
+#: A state file as the script before TASK 127 wrote it, with a key that a hand edit added
+#: (TC-10, UC-5).
+V1_STATE = r"""session_id: "old-sid"
+last_updated: "2026-09-17T00:00:00"
+mode: "M"
+
+current_task:
+  name: "t"
+  status: "s"
+  predicted_steps: 0
+
+context_summary: "x"
+
+current_task_2026_09_17:
+  name: "TASK-029 by hand"
+
+active_blockers:
+  []
+
+recent_decisions:
+  - "say "hi""
+  - "C:\new\dir"
+  - "C:\new\tab"
+
+schema_version: 2
+
+completed_tasks:
+  - "done one"
+"""
+
+
+def clean_env():
+    """The environment of a run: no `CLAUDE_PROJECT_DIR`, which could point the script at a live
+    repository, no `PYTHONPATH`, and no bytecode written."""
+    env = dict(os.environ)
+    for key in ("CLAUDE_PROJECT_DIR", "PYTHONPATH"):
+        env.pop(key, None)
+    env["PYTHONDONTWRITEBYTECODE"] = "1"
+    return env
+
+
+def run_script(cwd, args, env_extra=None, script=SCRIPT, pythonpath=None):
+    """Run the script with `args` in `cwd`; bytes out."""
+    env = clean_env()
+    if pythonpath is not None:
+        env["PYTHONPATH"] = str(pythonpath)
+    env.update(env_extra or {})
+    return subprocess.run([sys.executable, str(script)] + list(args), cwd=str(cwd), env=env,
+                          capture_output=True, timeout=120)
+
+
+def output(proc):
+    """stdout and stderr of `proc` as text, for messages and assertions."""
+    return (proc.stdout + proc.stderr).decode("utf-8", "backslashreplace")
+
+
+def load_script(name):
+    """The script as a module named `name`, compiled from its source in memory.
+
+    `importlib`'s loader reads and writes `__pycache__/` beside the script; this neither reads
+    nor writes bytecode there.
+    """
+    module = types.ModuleType(name)
+    module.__file__ = str(SCRIPT)
+    exec(compile(SCRIPT.read_bytes(), str(SCRIPT), "exec"), module.__dict__)
+    return module
+
+
+def json_lists(text):
+    """Each list of the state file and the scalars of `current_task`, read as JSON lines.
+
+    A reader of its own, independent of the script's parser: a list item is `  - <JSON string>`.
+    """
+    lists, key = {}, None
+    scalars = {}
+    for line in text.split("\n"):
+        head = re.match(r"^(\w+):\s*$", line)
+        if head:
+            key = head.group(1)
+            lists.setdefault(key, [])
+            continue
+        item = re.match(r"^  - (.*)$", line)
+        if item and key:
+            lists[key].append(json.loads(item.group(1)))
+            continue
+        field = re.match(r"^  (name|status): (.*)$", line)
+        if field and key == "current_task":
+            scalars[field.group(1)] = json.loads(field.group(2))
+    return lists, scalars
+
+
+class _RootCase(unittest.TestCase):
+    """A temporary root that holds its own `.git`; the script writes its state there."""
+
+    def setUp(self):
+        self._tmp = tempfile.TemporaryDirectory()
+        self.addCleanup(self._tmp.cleanup)
+        self.root = Path(self._tmp.name).resolve() / "root"
+        (self.root / ".git").mkdir(parents=True)
+        self.sessions = self.root / ".agent" / "sessions"
+        self.state = self.sessions / "latest.yaml"
+        self.lock = self.sessions / "latest.yaml.lock"
+
+    def run_ok(self, args, **kwargs):
+        proc = run_script(self.root, args, **kwargs)
+        self.assertEqual(proc.returncode, 0, output(proc))
+        return proc
+
+    def text(self):
+        return self.state.read_bytes().decode("utf-8")
+
+    def write_state(self, text, prefix=b""):
+        self.sessions.mkdir(parents=True, exist_ok=True)
+        self.state.write_bytes(prefix + text.encode("utf-8"))
+
+    def standin(self, **env):
+        """The `PYTHONPATH` directory and the environment of the Windows branch."""
+        site = Path(self._tmp.name) / "site"
+        site.mkdir(exist_ok=True)
+        (site / "sitecustomize.py").write_text(SITECUSTOMIZE, encoding="utf-8")
+        values = {"MSVCRT_STANDIN": "1",
+                  "MSVCRT_STANDIN_LOG": str(Path(self._tmp.name) / "msvcrt.log")}
+        values.update(env)
+        return site, values
+
+    def assert_yaml_equal(self, text, key, expected):
+        """PyYAML yields `expected` for `key`, a dotted path. Each test calls this after its own
+        checks; without PyYAML the test reports a skip, so R3.7 is not shown as checked."""
+        if yaml is None:
+            self.skipTest("PyYAML does not import: TASK 127 R3.7 is not checked")
+        node = yaml.safe_load(text)
+        for part in key.split("."):
+            node = node[part]
+        self.assertEqual(node, expected)
+
 
 class UpdateStateAnchorTestCase(unittest.TestCase):
     def setUp(self):
@@ -90,5 +339,295 @@ class UpdateStateAnchorTestCase(unittest.TestCase):
                          "same session_id — subdir run updates, not forks")
 
 
+@unittest.skipIf(fcntl is None, "holds a POSIX lock, or runs the Windows branch on POSIX")
+class LockTestCase(_RootCase):
+    """TASK 127 R1: the lock on POSIX and on Windows (TC-01 to TC-05)."""
+
+    def test_tc01_two_runs_at_once_keep_both_tasks(self):
+        procs = [subprocess.Popen([sys.executable, str(SCRIPT)] + ARGS
+                                  + ["--add_completed_task", name], cwd=str(self.root),
+                                  env=clean_env(), stdout=subprocess.PIPE,
+                                  stderr=subprocess.PIPE)
+                 for name in ("Task A", "Task B")]
+        for proc in procs:
+            out, err = proc.communicate(timeout=120)
+            self.assertEqual(proc.returncode, 0, (out + err).decode("utf-8", "replace"))
+        lists, _ = json_lists(self.text())
+        self.assertEqual(sorted(lists["completed_tasks"]), ["Task A", "Task B"])
+
+    def test_tc02_a_held_flock_makes_the_run_wait(self):
+        self.sessions.mkdir(parents=True)
+        fd = os.open(self.lock, os.O_RDWR | os.O_CREAT, 0o644)
+        try:
+            fcntl.flock(fd, fcntl.LOCK_EX)
+            proc = subprocess.Popen([sys.executable, str(SCRIPT)] + ARGS, cwd=str(self.root),
+                                    env=clean_env(), stdout=subprocess.PIPE,
+                                    stderr=subprocess.PIPE)
+            time.sleep(2)
+            waiting = proc.poll() is None
+            # A state that another run wrote while this one waited: the read must come after it.
+            self.write_state(V2_STATE.format(decision='"kept"').replace(
+                "completed_tasks:\n  []", 'completed_tasks:\n  - "written while waiting"'))
+            fcntl.flock(fd, fcntl.LOCK_UN)
+            out, err = proc.communicate(timeout=120)
+        finally:
+            os.close(fd)
+        self.assertTrue(waiting, "the run did not wait for the held lock")
+        self.assertEqual(proc.returncode, 0, (out + err).decode("utf-8", "replace"))
+        lists, _ = json_lists(self.text())
+        self.assertEqual(lists["completed_tasks"], ["written while waiting"],
+                         "the run read the state before it took the lock")
+
+    def test_tc03_windows_branch_locks_and_unlocks_byte_zero(self):
+        site, env = self.standin()
+        self.run_ok(ARGS, env_extra=env, pythonpath=site)
+        log = Path(env["MSVCRT_STANDIN_LOG"]).read_text(encoding="utf-8").split()
+        self.assertEqual(log, ["1", "0", "1", "0", "0", "1"],
+                         "LK_LOCK, then LK_UNLCK, each on 1 byte at offset 0")
+        self.assertTrue(self.text().startswith("schema_version: 2\n"))
+
+    def test_tc04_windows_branch_exits_1_when_the_lock_stays_held(self):
+        self.write_state(V2_STATE.format(decision='"kept"'))
+        before = self.state.read_bytes()
+        fd = os.open(self.lock, os.O_RDWR | os.O_CREAT, 0o644)
+        try:
+            fcntl.lockf(fd, fcntl.LOCK_EX, 1, 0, os.SEEK_SET)
+            site, env = self.standin()
+            proc = run_script(self.root, ARGS, env_extra=env, pythonpath=site)
+        finally:
+            os.close(fd)
+        self.assertEqual(proc.returncode, 1, output(proc))
+        self.assertIn("latest.yaml.lock", output(proc))
+        self.assertEqual(self.state.read_bytes(), before)
+
+    def test_tc05_no_lock_module_exits_1_and_writes_nothing(self):
+        site, env = self.standin(MSVCRT_STANDIN="0", MSVCRT_STANDIN_BLOCK="msvcrt")
+        proc = run_script(self.root, ARGS, env_extra=env, pythonpath=site)
+        self.assertEqual(proc.returncode, 1, output(proc))
+        self.assertIn("fcntl", output(proc))
+        self.assertIn("msvcrt", output(proc))
+        self.assertFalse((self.root / ".agent").exists(), "a file was written")
+        proc = run_script(self.root, ["--help"], env_extra=env, pythonpath=site)
+        self.assertEqual(proc.returncode, 0, output(proc))
+
+
+class DirectoryTestCase(_RootCase):
+    """TASK 127 R1.9: a session directory that another run made meanwhile (TC-18)."""
+
+    def test_tc18_a_directory_made_meanwhile_is_no_error(self):
+        # The race of R1.9 every time: the directory exists, and `os.path.exists` says it does
+        # not, as when a second run creates it between the check and the creation.
+        from unittest import mock
+        module = load_script("update_state_tc18")
+        self.sessions.mkdir(parents=True)
+        cwd = os.getcwd()
+        os.chdir(self.root)
+        try:
+            with mock.patch.dict(os.environ), mock.patch("os.path.exists", return_value=False):
+                os.environ.pop("CLAUDE_PROJECT_DIR", None)
+                module.ensure_session_dir()
+        finally:
+            os.chdir(cwd)
+        self.assertTrue(self.sessions.is_dir())
+
+
+class EncodingTestCase(_RootCase):
+    """TASK 127 R2: UTF-8 on every platform (TC-06 to TC-08, TC-11, TC-15)."""
+
+    #: A locale whose encoding is ASCII on Linux and macOS (TASK 127 R7.3).
+    ASCII_LOCALE = {"LC_ALL": "C", "LANG": "C", "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0"}
+
+    def test_tc06_cyrillic_state_survives_an_ascii_locale(self):
+        self.write_state(V2_STATE.format(decision='"решение → ok"'))
+        self.run_ok(ARGS, env_extra=self.ASCII_LOCALE)
+        lists, _ = json_lists(self.text())
+        self.assertEqual(lists["recent_decisions"], ["решение → ok"])
+        self.assert_yaml_equal(self.text(), "recent_decisions", ["решение → ok"])
+
+    def test_tc07_each_open_names_its_encoding(self):
+        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
+        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
+                 and isinstance(node.func, ast.Name) and node.func.id == "open"]
+        self.assertTrue(calls)
+        for call in calls:
+            keywords = {kw.arg: kw.value for kw in call.keywords}
+            mode = call.args[1] if len(call.args) > 1 else keywords.get("mode")
+            mode = mode.value if isinstance(mode, ast.Constant) else "r"
+            encoding = keywords.get("encoding")
+            self.assertIsInstance(encoding, ast.Constant, f"line {call.lineno}: no encoding")
+            if "w" in mode:
+                self.assertEqual(encoding.value, "utf-8", f"line {call.lineno}")
+                newline = keywords.get("newline")
+                self.assertIsInstance(newline, ast.Constant, f"line {call.lineno}: no newline")
+                self.assertEqual(newline.value, "\n", f"line {call.lineno}")
+            else:
+                self.assertEqual(encoding.value, "utf-8-sig", f"line {call.lineno}")
+
+    def test_tc08_messages_survive_an_ascii_pipe(self):
+        root = Path(self._tmp.name).resolve() / "корень"
+        (root / ".git").mkdir(parents=True)
+        proc = run_script(root, ARGS, env_extra={"PYTHONIOENCODING": "ascii"})
+        self.assertEqual(proc.returncode, 0, output(proc))
+        self.assertNotIn("Traceback", output(proc))
+
+    def test_tc11_a_state_file_that_is_not_utf8_stops_the_run(self):
+        self.sessions.mkdir(parents=True)
+        before = b'session_id: "x"\nmode: "\xff\xfe"\n'
+        self.state.write_bytes(before)
+        proc = run_script(self.root, ARGS)
+        self.assertEqual(proc.returncode, 1, output(proc))
+        self.assertIn(str(self.state), output(proc))
+        self.assertIn("UTF-8", output(proc))
+        self.assertEqual(self.state.read_bytes(), before)
+
+    def test_tc15_a_byte_order_mark_does_not_hide_version_2(self):
+        # An ASCII-only JSON string escapes `é` and `→`. A version 2 read decodes the
+        # escapes, and the write stores the characters; a version 1 read keeps them as text.
+        self.write_state(V2_STATE.format(decision=json.dumps("café → ok")),
+                         prefix=b"\xef\xbb\xbf")
+        self.run_ok(ARGS)
+        raw = self.state.read_bytes()
+        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
+        self.assertIn('  - "café → ok"\n', raw.decode("utf-8"))
+
+
+class ScalarTestCase(_RootCase):
+    """TASK 127 R3: escaped scalars and a stable round trip (TC-09, TC-10, TC-14, TC-16)."""
+
+    def test_tc09_sixteen_runs_keep_every_value(self):
+        for value in ROUND_TRIP_VALUES:
+            self.run_ok(["--mode", "M", "--task", value, "--status", value, "--summary", "x",
+                         "--add_blocker", value, "--add_decision", value,
+                         "--add_completed_task", value])
+        text = self.text()
+        lists, scalars = json_lists(text)
+        self.assertEqual(lists["active_blockers"], ROUND_TRIP_VALUES)
+        self.assertEqual(lists["completed_tasks"], ROUND_TRIP_VALUES)
+        self.assertEqual(lists["recent_decisions"], ROUND_TRIP_VALUES[-10:])
+        self.assertEqual(scalars, {"name": ROUND_TRIP_VALUES[-1],
+                                   "status": ROUND_TRIP_VALUES[-1]})
+        self.assert_yaml_equal(text, "active_blockers", ROUND_TRIP_VALUES)
+        self.assert_yaml_equal(text, "completed_tasks", ROUND_TRIP_VALUES)
+        self.assert_yaml_equal(text, "recent_decisions", ROUND_TRIP_VALUES[-10:])
+        self.assert_yaml_equal(text, "current_task.name", ROUND_TRIP_VALUES[-1])
+        self.assert_yaml_equal(text, "current_task.status", ROUND_TRIP_VALUES[-1])
+
+    def test_tc10_an_old_file_keeps_its_strings(self):
+        self.write_state(V1_STATE)
+        self.run_ok(ARGS)
+        text = self.text()
+        self.assertTrue(text.startswith("schema_version: 2\n"))
+        lists, _ = json_lists(text)
+        self.assertEqual(lists["recent_decisions"],
+                         ['say "hi"', "C:\\new\\dir", "C:\\new\\tab"])
+        self.assertEqual(lists["completed_tasks"], ["done one"])
+        self.assertIn('session_id: "old-sid"', text)
+        self.assertNotIn("current_task_2026_09_17", text)
+        self.assert_yaml_equal(text, "recent_decisions",
+                               ['say "hi"', "C:\\new\\dir", "C:\\new\\tab"])
+
+    def test_tc14_a_summary_of_two_lines_is_one_scalar(self):
+        self.run_ok(["--mode", "M", "--task", "t", "--status", "s",
+                     "--summary", "line one\nline two"])
+        text = self.text()
+        line = [l for l in text.split("\n") if l.startswith("context_summary: ")]
+        self.assertEqual(len(line), 1)
+        self.assertEqual(json.loads(line[0][len("context_summary: "):]), "line one\nline two")
+        self.run_ok(["--mode", "M", "--task", "t", "--status", "s", "--summary", "  padded  "])
+        self.assertIn('context_summary: "padded"\n', self.text())
+        self.assert_yaml_equal(text, "context_summary", "line one\nline two")
+
+    def test_tc17_the_merge_rules(self):
+        self.run_ok(ARGS + ["--add_blocker", "", "--add_decision", ""])
+        lists, _ = json_lists(self.text())
+        self.assertEqual((lists["active_blockers"], lists["recent_decisions"]), ([], []))
+        for _ in range(2):
+            self.run_ok(ARGS + ["--add_blocker", "B", "--add_completed_task", "T"])
+        lists, _ = json_lists(self.text())
+        self.assertEqual(lists["active_blockers"], ["B"])
+        self.assertEqual(lists["completed_tasks"], ["T"])
+
+    def test_tc16_an_empty_task_name(self):
+        self.run_ok(["--mode", "M", "--task", "", "--status", "s", "--summary", "x"])
+        _, scalars = json_lists(self.text())
+        self.assertEqual(scalars["name"], "")
+        self.assert_yaml_equal(self.text(), "current_task.name", "")
+
+
+class ImportPathTestCase(_RootCase):
+    """TASK 127 R6, WI-39: no module planted beside the script runs (TC-12, TC-13)."""
+
+    #: Modules that a planted file cannot shadow: built into the interpreter, or imported
+    #: before the script runs.
+    PRELOADED = ("os", "sys")
+
+    def planted_names(self):
+        """Each module that the script imports, by its AST, and `msvcrt` and `_winapi`."""
+        names = {"msvcrt", "_winapi"}
+        for node in ast.walk(ast.parse(SCRIPT.read_text(encoding="utf-8"))):
+            if isinstance(node, ast.Import):
+                names.update(alias.name.split(".")[0] for alias in node.names)
+            elif isinstance(node, ast.ImportFrom) and node.level == 0:
+                names.add(node.module.split(".")[0])
+        return sorted(names - set(self.PRELOADED))
+
+    def test_tc12_a_planted_module_is_not_imported(self):
+        base = Path(self._tmp.name).resolve()
+        scripts = base / "copy" / "scripts"
+        scripts.mkdir(parents=True)
+        (scripts / "update_state.py").write_bytes(SCRIPT.read_bytes())
+        markers = base / "markers"
+        markers.mkdir()
+        planted = self.planted_names()
+        self.assertIn("datetime", planted)
+        self.assertIn("json", planted)
+        for name in planted:
+            if name == "datetime":
+                continue
+            (scripts / f"{name}.py").write_text(
+                f"open({str(markers / name)!r}, 'w').close()\n", encoding="utf-8")
+        source = base / "datetime_source.py"
+        source.write_text(f"open({str(markers / 'datetime')!r}, 'w').close()\n",
+                          encoding="utf-8")
+        py_compile.compile(str(source), cfile=str(scripts / "datetime.pyc"), doraise=True)
+        source.unlink()
+        runs = [scripts / "update_state.py"]
+        link = base / "link"
+        try:
+            os.symlink(scripts, link, target_is_directory=True)
+            runs.append(link / "update_state.py")
+        except (OSError, NotImplementedError):  # no symbolic link on this host
+            pass
+        # A case-insensitive volume reaches the copy through other letter case, and the path as
+        # called then differs from the real one (security audit S-1).
+        variant = base / "COPY" / "scripts" / "update_state.py"
+        if variant.exists():
+            runs.append(variant)
+        # A linked file leaves the link's own directory on `sys.path` on Windows; the modules
+        # planted there must not run either.
+        linked = base / "linked"
+        linked.mkdir()
+        for name in planted:
+            if name != "datetime":
+                (linked / f"{name}.py").write_text(
+                    f"open({str(markers / name)!r}, 'w').close()\n", encoding="utf-8")
+        try:
+            os.symlink(scripts / "update_state.py", linked / "update_state.py")
+            runs.append(linked / "update_state.py")
+        except (OSError, NotImplementedError):
+            pass
+        for script in runs:
+            proc = run_script(self.root, ARGS, script=script)
+            self.assertEqual(proc.returncode, 0, output(proc))
+            self.assertEqual(sorted(p.name for p in markers.iterdir()), [],
+                             f"a module planted beside {script} was imported")
+
+    def test_tc13_a_module_import_keeps_sys_path(self):
+        before = list(sys.path)
+        module = load_script("update_state_under_test")
+        self.assertEqual(sys.path, before)
+        self.assertTrue(callable(module.parse_simple_yaml))
+
+
 if __name__ == "__main__":
     unittest.main()
diff --git a/.agent/skills/skill-session-state/scripts/update_state.py b/.agent/skills/skill-session-state/scripts/update_state.py
index 3bd5970..0a6c27f 100644
--- a/.agent/skills/skill-session-state/scripts/update_state.py
+++ b/.agent/skills/skill-session-state/scripts/update_state.py
@@ -1,15 +1,81 @@
 #!/usr/bin/env python3
-import sys
+"""Persist the session state of `skill-session-state` in `.agent/sessions/latest.yaml`.
+
+The bootstrap files run this script at each phase boundary. It takes an exclusive lock on
+`latest.yaml.lock`, reads the state once, merges the arguments into it and writes it back
+(TASK 127):
+
+- the lock is `fcntl.flock` on POSIX and `msvcrt.locking` on Windows, chosen by which of the two
+  imports;
+- the file is UTF-8 with LF line ends. Its first line is `schema_version: 2`, and each string is
+  a JSON string, which is also a YAML double-quoted scalar;
+- a file without `schema_version: 2` is read as the script before TASK 127 wrote it, and the
+  next write stores the same strings in the new form.
+
+Exit codes: 0 the state was written; 1 no lock module, a lock that stayed held, a state file that
+is not UTF-8, or another error; 2 a usage error. In the first three cases of exit 1 the script
+writes nothing.
+"""
 import os
-import uuid
-import datetime
-import argparse
-import re
-import fcntl
+import sys
+
+# Run as a script, its own directory leaves the import path before any other import, so a module
+# planted beside the script is never imported under the allow rule (WI-39, TASK 127 R6). An entry
+# is that directory when its real path, or its device and inode, match the directory of the path
+# as called or of the real path. A case-insensitive volume, a linked directory and a linked file
+# reach the directory under other spellings. A test that loads the module keeps its own path.
+if __name__ == "__main__":
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
+
+import argparse  # noqa: E402
+import datetime  # noqa: E402
+import json  # noqa: E402
+import re  # noqa: E402
+import uuid  # noqa: E402
+
+# The lock module: `fcntl` where it imports, else `msvcrt` (TASK 127 D10).
+try:
+    import fcntl  # noqa: E402
+except ImportError:
+    fcntl = None
+    try:
+        import msvcrt  # noqa: E402
+    except ImportError:
+        msvcrt = None
+else:
+    msvcrt = None
 
 # Constants
 SESSION_DIR = ".agent/sessions"
 SESSION_FILE = "latest.yaml"
+SCHEMA_VERSION = 2
+#: Characters that `json.dumps(ensure_ascii=False)` leaves raw and a YAML double-quoted scalar
+#: must not hold raw: those outside the YAML 1.2 printable set, and the line breaks U+0085,
+#: U+2028 and U+2029 (TASK 127 R3.1).
+_YAML_UNSAFE = re.compile("[%s]" % "".join(
+    "%s-%s" % (chr(low), chr(high))
+    for low, high in ((0x7F, 0x9F), (0x2028, 0x2029), (0xD800, 0xDFFF), (0xFFFE, 0xFFFF))))
+#: The version line; the reader takes it from the first line only (TASK 127 R3.3).
+_VERSION_LINE = re.compile(r"schema_version:\s*(\d+)\s*")
+
+
+class StateError(Exception):
+    """A state that the script will not read or lock; the message names the file."""
+
 
 def find_repo_root():
     """Anchor for SESSION_DIR (SS-1): the state file must land at the repo
@@ -43,106 +109,141 @@ def get_session_path():
     return os.path.join(get_session_dir(), SESSION_FILE)
 
 def ensure_session_dir():
-    session_dir = get_session_dir()
-    if not os.path.exists(session_dir):
-        os.makedirs(session_dir)
+    """Create the session dir; a second run that creates it at the same time is no error."""
+    os.makedirs(get_session_dir(), exist_ok=True)
 
-# --- Minimal YAML Parser (Read-Only specific to our schema) ---
-# We ONLY need to preserve: session_id, active_blockers, recent_decisions.
+# --- Minimal YAML reader (specific to our schema) ---
+# We ONLY need to preserve: session_id, active_blockers, recent_decisions, completed_tasks.
 # Everything else (task, mode, summary) is overwritten by the Agent's update.
 
+def _decode(raw, version):
+    """One preserved value from its text in the file.
+
+    A version 2 file holds a JSON string, which `json.loads` decodes. A version 1 file, or an item
+    that is not a JSON string, is read as the script before TASK 127 read it: one optional quote
+    is stripped from each end, then the outer whitespace.
+    """
+    if version >= SCHEMA_VERSION:
+        try:
+            value = json.loads(raw)
+        except ValueError:
+            value = None
+        if isinstance(value, str):
+            return value
+    return re.fullmatch(r"""['"]?(.*?)['"]?""", raw, re.DOTALL).group(1).strip()
+
+
+def _list_items(content, key, version):
+    """The items of the list `key`, each decoded by `_decode`."""
+    section = re.search(r'^' + key + r':\s*\n((?:\s+-\s+.*(?:\n|$))*)', content, re.MULTILINE)
+    if not section:
+        return []
+    return [_decode(raw, version)
+            for raw in re.findall(r'^\s+-\s+(.*?)\s*$', section.group(1), re.MULTILINE)]
+
+
 def parse_simple_yaml(content):
     """
     Robustly extract specific fields from our generated YAML.
     Does NOT aim to be a full YAML parser.
     """
+    match = _VERSION_LINE.fullmatch(content.split("\n", 1)[0])
+    version = int(match.group(1)) if match else 1
     data = {
         "session_id": None,
-        "active_blockers": [],
-        "recent_decisions": [],
-        "completed_tasks": []
+        "active_blockers": _list_items(content, "active_blockers", version),
+        "recent_decisions": _list_items(content, "recent_decisions", version),
+        "completed_tasks": _list_items(content, "completed_tasks", version),
     }
-    
-    # Extract session_id
-    sid_match = re.search(r'^session_id:\s*[\'"]?([^\'"\n]+)[\'"]?', content, re.MULTILINE)
-    if sid_match:
-        data["session_id"] = sid_match.group(1).strip()
-        
-    # Extract active_blockers (List of strings)
-    # Assumes format:
-    # active_blockers:
-    #   - "Blocker 1"
-    #   - "Blocker 2"
-    blockers_section = re.search(r'^active_blockers:\s*\n((?:\s+-\s+.*(?:\n|$))*)', content, re.MULTILINE)
-    if blockers_section:
-        items = re.findall(r'^\s+-\s+[\'"]?(.*?)[\'"]?\s*$', blockers_section.group(1), re.MULTILINE)
-        data["active_blockers"] = [item.strip() for item in items]
-
-    # Extract recent_decisions
-    decisions_section = re.search(r'^recent_decisions:\s*\n((?:\s+-\s+.*(?:\n|$))*)', content, re.MULTILINE)
-    if decisions_section:
-        items = re.findall(r'^\s+-\s+[\'"]?(.*?)[\'"]?\s*$', decisions_section.group(1), re.MULTILINE)
-        data["recent_decisions"] = [item.strip() for item in items]
-
-    # Extract completed_tasks
-    completed_section = re.search(r'^completed_tasks:\s*\n((?:\s+-\s+.*(?:\n|$))*)', content, re.MULTILINE)
-    if completed_section:
-        items = re.findall(r'^\s+-\s+[\'"]?(.*?)[\'"]?\s*$', completed_section.group(1), re.MULTILINE)
-        data["completed_tasks"] = [item.strip() for item in items]
-        
+    if version >= SCHEMA_VERSION:
+        sid = re.search(r'^session_id:\s*(.*?)\s*$', content, re.MULTILINE)
+        if sid:
+            data["session_id"] = _decode(sid.group(1), version) or None
+    else:
+        sid = re.search(r'^session_id:\s*[\'"]?([^\'"\n]+)[\'"]?', content, re.MULTILINE)
+        if sid:
+            data["session_id"] = sid.group(1).strip()
     return data
 
+
+def _scalar(value):
+    """`value` as a YAML double-quoted scalar: a JSON string with `_YAML_UNSAFE` escaped."""
+    text = json.dumps(str(value), ensure_ascii=False)
+    return _YAML_UNSAFE.sub(lambda m: "\\u%04x" % ord(m.group()), text)
+
+
 def generate_yaml(data):
     """
     Generate clean, valid YAML string.
     """
-    iso_time = datetime.datetime.now().isoformat()
-    
-    # Handle multiline summary
-    summary = data.get('context_summary', '').strip()
-    formatted_summary = ""
-    if '\n' in summary or len(summary) > 80:
-        formatted_summary = "|\n" + "\n".join([f"  {line}" for line in summary.splitlines()])
-    else:
-        formatted_summary = f'"{summary}"'
+    lines = [
+        f"schema_version: {SCHEMA_VERSION}",
+        f"session_id: {_scalar(data.get('session_id'))}",
+        f"last_updated: {_scalar(datetime.datetime.now().isoformat())}",
+        f"mode: {_scalar(data.get('mode', 'UNKNOWN'))}",
+        "",
+        "current_task:",
+        f"  name: {_scalar(data.get('task_name', 'Unknown Task'))}",
+        f"  status: {_scalar(data.get('task_status', 'Initializing'))}",
+        f"  predicted_steps: {int(data.get('predicted_steps', 0))}",
+        "",
+        f"context_summary: {_scalar(data.get('context_summary', '').strip())}",
+    ]
+    for key in ("active_blockers", "recent_decisions", "completed_tasks"):
+        items = data.get(key) or []
+        lines += ["", f"{key}:"]
+        lines += [f"  - {_scalar(item)}" for item in items] or ["  []"]
+    return "\n".join(lines) + "\n"
 
-    yaml = f"""session_id: "{data.get('session_id')}"
-last_updated: "{iso_time}"
-mode: "{data.get('mode', 'UNKNOWN')}"
 
-current_task:
-  name: "{data.get('task_name', 'Unknown Task')}"
-  status: "{data.get('task_status', 'Initializing')}"
-  predicted_steps: {data.get('predicted_steps', 0)}
+def read_state(fpath):
+    """The preserved fields of the state file `fpath`, or `{}` when it does not exist.
 
-context_summary: {formatted_summary}
+    The read drops a leading byte-order mark (TASK 127 D14).
+
+    Raises:
+        StateError: the file is not UTF-8 (TASK 127 R2.3).
+    """
+    if not os.path.exists(fpath):
+        return {}
+    try:
+        with open(fpath, "r", encoding="utf-8-sig") as f:
+            content = f.read()
+    except UnicodeDecodeError as exc:
+        raise StateError(f"{fpath} is not UTF-8 (byte {exc.start}: {exc.reason}); "
+                         f"save it as UTF-8 or delete it") from None
+    return parse_simple_yaml(content)
+
+
+def _lock(fd):
+    """Take the exclusive lock of the state on the lock file `fd`.
+
+    `msvcrt.LK_LOCK` tries 10 times, 1 second apart, and then raises `OSError`; `fcntl.flock`
+    waits with no time limit.
+    """
+    if fcntl is not None:
+        fcntl.flock(fd, fcntl.LOCK_EX)
+    else:
+        os.lseek(fd, 0, os.SEEK_SET)
+        msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
+
+
+def _unlock(fd):
+    """Release the lock that `_lock` took."""
+    if fcntl is not None:
+        fcntl.flock(fd, fcntl.LOCK_UN)
+    else:
+        os.lseek(fd, 0, os.SEEK_SET)
+        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
 
-active_blockers:
-"""
-    # Add lists
-    for blocker in data.get('active_blockers', []):
-        yaml += f'  - "{blocker}"\n'
-    
-    if not data.get('active_blockers'):
-        yaml += "  []\n"
-        
-    yaml += "\nrecent_decisions:\n"
-    for decision in data.get('recent_decisions', []):
-        yaml += f'  - "{decision}"\n'
-        
-    if not data.get('recent_decisions'):
-        yaml += "  []\n"
-        
-    yaml += "\ncompleted_tasks:\n"
-    for task in data.get('completed_tasks', []):
-        yaml += f'  - "{task}"\n'
-        
-    if not data.get('completed_tasks'):
-        yaml += "  []\n"
-        
-    return yaml
 
 def main():
+    # The script's own messages never raise an encoding error on a console or a pipe whose
+    # encoding cannot hold a path or a value (TASK 127 R2.2).
+    for stream in (sys.stdout, sys.stderr):
+        if hasattr(stream, "reconfigure"):
+            stream.reconfigure(errors="backslashreplace")
+
     parser = argparse.ArgumentParser(description="Update Session State YAML")
     parser.add_argument("--mode", required=True, help="Current Agent Mode")
     parser.add_argument("--task", required=True, help="Current Task Name")
@@ -153,85 +254,40 @@ def main():
     parser.add_argument("--add_blocker", help="Add a blocker item")
     parser.add_argument("--clear_blockers", action="store_true", help="Clear all blockers")
     parser.add_argument("--add_completed_task", help="Add a completed task to history")
-    
+
     args = parser.parse_args()
-    
-    ensure_session_dir()
-    fpath = get_session_path()
-    
-    # 1. Read existing state to preserve ID and lists
-    existing_data = {}
-    if os.path.exists(fpath):
-        try:
-            with open(fpath, 'r') as f:
-                content = f.read()
-                existing_data = parse_simple_yaml(content)
-        except Exception as e:
-            print(f"Warning: Could not read existing session file: {e}")
-            existing_data = {}
-            
-    # 2. Merge Data
-    session_id = existing_data.get("session_id") or str(uuid.uuid4())
-    active_blockers = existing_data.get("active_blockers", [])
-    recent_decisions = existing_data.get("recent_decisions", [])
-    
-    if args.clear_blockers:
-        active_blockers = []
-    
-    if args.add_blocker:
-        if args.add_blocker not in active_blockers:
-            active_blockers.append(args.add_blocker)
-            
-            
-    if args.add_decision:
-        # Keep only last 10 decisions
-        recent_decisions.append(args.add_decision)
-        if len(recent_decisions) > 10:
-            recent_decisions = recent_decisions[-10:]
-
-    completed_tasks = existing_data.get("completed_tasks", [])
-    if args.add_completed_task:
-        if args.add_completed_task not in completed_tasks:
-            completed_tasks.append(args.add_completed_task)
-            
-    
-    # 3. Construct New State
-    # Note: We construct it BEFORE locking to minimize lock time, 
-    # but we must re-read inside the lock to get the TRUE latest state.
-    
-    # --- CRITICAL SECTION START ---
-    # We use a separate lock file to avoid truncation issues with open(..., 'w')
-    lock_path = fpath + ".lock"
-    
+
+    if fcntl is None and msvcrt is None:
+        print("Error updating session state: neither fcntl nor msvcrt imports, "
+              "and the state needs one of them for its lock")
+        sys.exit(1)
+
     try:
-        with open(lock_path, 'w') as lockfile:
-            # Acquire Exclusive Lock
-            fcntl.flock(lockfile, fcntl.LOCK_EX)
-            
+        ensure_session_dir()
+        fpath = get_session_path()
+        # A separate lock file, opened with no truncation and at position 0 (TASK 127 R1.6).
+        lock_path = fpath + ".lock"
+        fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
+        try:
             try:
-                # RE-READ existing state inside the lock to ensure we have the absolute latest
-                # (Another agent might have updated it while we were parsing args)
-                if os.path.exists(fpath):
-                    with open(fpath, 'r') as f:
-                        current_content = f.read()
-                        latest_data = parse_simple_yaml(current_content)
-                else:
-                    latest_data = {}
-
-                # Merge Logic (Re-apply on top of latest_data)
-                # We prioritize the LATEST data for lists, but the ARGS for current status
-                
+                _lock(fd)
+            except OSError as exc:
+                raise StateError(f"could not lock {lock_path}: {exc}") from None
+            try:
+                # The one read of the state, inside the lock (TASK 127 R1.2).
+                latest_data = read_state(fpath)
+
                 # Session ID: Persist if exists
-                final_session_id = latest_data.get("session_id") or session_id
-                
+                final_session_id = latest_data.get("session_id") or str(uuid.uuid4())
+
                 # Active Blockers: Merge (Union)
                 final_blockers = latest_data.get("active_blockers", [])
                 if args.clear_blockers:
                     final_blockers = []
                 elif args.add_blocker and args.add_blocker not in final_blockers:
                     final_blockers.append(args.add_blocker)
-                    
-                # Recent Decisions: Append
+
+                # Recent Decisions: Append, keep the last 10
                 final_decisions = latest_data.get("recent_decisions", [])
                 if args.add_decision:
                     final_decisions.append(args.add_decision)
@@ -243,7 +299,6 @@ def main():
                 if args.add_completed_task and args.add_completed_task not in final_completed:
                     final_completed.append(args.add_completed_task)
 
-                # Construct Final State Object
                 final_state = {
                     "session_id": final_session_id,
                     "mode": args.mode,
@@ -253,22 +308,18 @@ def main():
                     "context_summary": args.summary,
                     "active_blockers": final_blockers,
                     "recent_decisions": final_decisions,
-                    "completed_tasks": final_completed
+                    "completed_tasks": final_completed,
                 }
-                
-                # Generate YAML
                 yaml_content = generate_yaml(final_state)
-                
-                # Write to actual file
-                with open(fpath, 'w') as f:
+
+                with open(fpath, "w", encoding="utf-8", newline="\n") as f:
                     f.write(yaml_content)
-                    
+
                 print(f"Session state updated: {fpath} (Locked)")
-                
             finally:
-                # Release Lock
-                fcntl.flock(lockfile, fcntl.LOCK_UN)
-                
+                _unlock(fd)
+        finally:
+            os.close(fd)
     except Exception as e:
         print(f"Error updating session state: {e}")
         sys.exit(1)
~~~~

J2, after the patch was recorded above:
- `git apply --whitespace=nowarn` of the patch exited 0;
- postconditions: `S/scripts/update_state.py` hashes to its staged copy, `0e46785b…`, and
  `S/scripts/tests/test_update_state.py` to its staged copy, `5bb50d7f…`; both keep mode
  `100644`; `git apply --check -R` of the patch passes;
- `rm --` of `S/scripts/staged_update_state.py`, then of
  `S/scripts/tests/staged_test_update_state.py`; both succeeded;
- step 6, for the guard of J3: `latest.yaml`
  `bffab37142d9fa792901b6d03e6dd3ebb9951e169407daf7f87cc55b98099d29`, `latest.yaml.lock`
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## The gates after stage 3 (PLAN J3)

- `gates.py`: 18 of 18; the pytest step passes 566 tests. The guard of J2 step 6 held before and
  after the gates.
- `bytescan.py` of the two final files finds nothing.
- The check of `framework-upgrade` §3 step 4, `j3.py`, exit 0:
  - item 1, seven commands: `python3 -m pytest` from the root (732 passed), from `S/` (24) and
    from `S/scripts/` (24); `python3 tests/run_tests.py`; `python3 -m unittest discover -s tests
    -v` from the root and from `S/scripts/`; `python3 -m unittest discover -s scripts/tests` from
    `S/`. No command changed `latest.yaml` or its lock. The discovery of `tests` from the root
    again added the two empty directories of `tests/_scratch.py`, which the put-back removed;
  - item 2, the committed rule on the live state: the base-format file, then the version 2 file
    that the first run wrote. Each changed `latest.yaml` only;
  - item 3: `latest.yaml` renamed to `latest.yaml.keep-127`, then the runs on the stand-in in the
    order of TASK R8.6. The run with no state file added the stand-in. Each option and each of the
    15 user rules changed the stand-in only; `--help` changed nothing. The stand-in with a
    byte-order mark was read and rewritten. The stand-in that is not UTF-8 exited 1, named the
    file, and changed nothing;
  - item 4: the stand-in removed, `latest.yaml.keep-127` renamed back.
- The live state after J3: `schema_version: 2` on its first line, the same `session_id`, 54
  completed tasks and 10 decisions, and PyYAML parses it. The run recorded it again through
  `update_state.py`.
- `rules_check.py compare`: both settings files hash as at the reading of §2.2, with no new rule.
- Each of the 18 paths of `git status` is declared.

## Stage 4 (PLAN J4), at the fingerprint `05097f0cdbea`: both PASS

Each reviewer computed `05097f0cdbea` at its start and at its end, wrote nothing in the tree, and
removed its own scratch directory.

The code review found the live diff of `S/scripts/` byte-identical to the reviewed patch, and each
other file of the change byte-identical to round 2, but the three records: TASK, PLAN and this
record. The final test module, the contract test and `tests/test_mock_agent.py` pass from the
root; the test module passes with pytest and with unittest from `S/` and from `S/scripts/`. No
regression; nothing new.

The security audit found the final files equal to the audited copies, with mode `100644`, and the
committed allow rule resolving to the new script. Its plant probe on a copy, with 79 module
names, ran no planted module in seven ways of calling the script, the rule's exact command after a
case-only rename among them. It found no file that a later allowed run could pick up: no
`__pycache__/` beside the script, no stand-in, no `latest.yaml.keep-127`. Its note: the
`__pycache__/` of `scripts/tests/` holds a bytecode file of the base test module from before the
task, which the import system rejects, since its recorded source size differs. Nothing new.

## Retro (§6)

The retro claim `framework-upgrade-session-state-windows` was taken at the start of the run and
released at its end. The question of the retro listed four candidates. The operator chose to file
the bypass in the archive scripts, the findings before the task, and B-1, and to close them in the
next task, the archive chain on Windows. Before filing, the run reproduced the bypass on copies of
`archive_move.py` and `rebase_links.py`: a call through a path in other letter case ran the planted
`json.py`, and a call in the exact case ran nothing. It also ran the `sh` block of each record from
the repository root, and each printed its defect line.

Filed, as defects:
- ARC-13, SEV-3: `archive_move.py` and `rebase_links.py` import a module planted beside them
  through a path in other letter case;
- SS-3, SEV-3: `update_state.py` writes `latest.yaml` through a link planted at that name (B-1);
- SS-4, SEV-4: `tests/test_concurrent_state.py` deletes the live `latest.yaml` when run by hand;
- SS-5, LOW: two SS-1 tests write the state of an outer repository when `TMPDIR` lies inside a git
  work tree;
- SS-6, LOW: the list-item pattern of the reader is quadratic in a run of spaces;
- TS-1, LOW: unittest discovery of `tests/` leaves an empty `tests/.scratch/` session directory
  behind. TS is a new prefix; `docs/KNOWN_ISSUES.md` gains its row, category `test-suite`.

Not filed, by the operator's choice: the decoding of escapes in tool inputs, which this record
describes under Mode B round 1. The inbox still holds five findings from earlier sessions, two of
them on `archive_move.py`; this retro did not triage them.

The retro wrote `docs/KNOWN_ISSUES.md` and the six records under `docs/issues/`. They are no
declared path, so a fallback after the retro stops at §5 step 1 and asks the operator.
