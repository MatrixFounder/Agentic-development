# TASK 127 — `update_state.py` runs on Windows, and a failed run of it reaches the operator

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 127 |
| Slug | session-state-windows |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | a defect report of 2026-10-26 from a team on Windows 10; the operator's answers of 2026-10-26 (D1, D2) |
| Base revision | `c6666c4a6cd251d7f0327ad0df57dd706a3104e3` |
| Closes | WI-39 for `update_state.py` only; the record stays open for nine scripts |
| Archive name | `task-127-session-state-windows.md` |
| Revision | 7 |

**Request.** A team runs the framework on Windows 10 with Python 3.13, Git Bash and PowerShell.
The ANSI code page there is cp1251. Their report lists framework scripts that fail on Windows.
The operator decided to support native Windows on the critical path, in four tasks (D1). This
task is the first: the session state of `skill-session-state`. The operator added the WI-39 fix
for this script to the scope (D2).

**Revision 2** applies M1, m1 to m5, N1 to N6 and N8 of Mode A round 1; N7 keeps the precedent
of TASK 124. **Revision 3** applies m1 and N1 to N6 of round 2, which passed, with no further
round, on the precedent of TASK 122 to TASK 124. **Revision 4** follows Mode B round 1 of the
PLAN (m2, N7, N8, N10) and a defect that B measured on the base script (R1.9, D16).
**Revision 5** adds TC-18 for R1.9, after Mode B round 2 (N4), which passed. **Revision 6**
records fix round 1 of stage 2 (D17). **Revision 7** records the close of stage 2 at round 2, and
its limits (D18).

In this document `S/` stands for `.agent/skills/skill-session-state/`. A coordinate into a file
that this task edits carries the pin `@c6666c4`, the base revision.

<!-- contract:problem -->

## 1. Problem

`S/scripts/update_state.py` writes `.agent/sessions/latest.yaml`. Every bootstrap file tells the
agent to run it at each phase boundary. The report, and the runs of §8 on the base script, give
these defects:

1. **Import.** `S/scripts/update_state.py:8@c6666c4` `import fcntl` raises
   `ModuleNotFoundError` on Windows. Every phase boundary fails there. In the report, the state
   file kept one task for three tasks.
2. **Encoding.** Four `open()` calls pass no `encoding`: lines 166, 207, 215 and 263 `@c6666c4`.
   Windows opens them in the ANSI code page. A summary with `→` exits 1 with
   `UnicodeEncodeError` (§8, run 2). A UTF-8 file read in cp1251 decodes to other text.
3. **Escaping.** `S/scripts/update_state.py:114@c6666c4` `name: "{data.get('task_name',
   'Unknown Task')}"` writes each value between quotes, with no escape. A `"` in `--task`, or a
   `\` in `--add_decision`, makes the file invalid YAML (§8, runs 3 and 4).
4. **No failure rule.** No rule says what an agent does when the script exits non-zero. In the
   report, agents continued the task. One agent wrote keys into `latest.yaml` by hand, and the
   script does not keep such keys.
5. **Stale state at boot.** The boot protocol announces the restored state and does not compare
   it with `docs/TASK.md`. In the report, a new session would restore a task three tasks old.
6. **Vendor tool in a TIER 0 skill.** `S/SKILL.md:40@c6666c4` `WHENEVER** you call the
   `task_boundary` tool` names its trigger by an Antigravity tool. Claude Code, Codex CLI and
   Cursor have no such tool. v3.20.11 removed the same framing from `00_agent_development.md` and
   `GEMINI.md`. `S/SKILL.md:89@c6666c4` `fcntl.lockf` states a lock that the script does not
   take: the script takes `fcntl.flock`, and no lock for a read.
7. **WI-39.** `.claude/settings.json:33` `update_state.py *` runs the script with no prompt.
   Python puts the script's directory first on `sys.path`. A `json.py` or `argparse.py` planted
   beside the script runs at the next phase boundary.
8. **Tests that run nowhere.** `S/scripts/tests/test_update_state.py` holds 6 tests of SS-1.
   No CI step names them. A bare `python3 -m pytest` from the root collects 725 tests and none
   under `.agent/`: pytest skips a directory whose name starts with a dot.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | The lock on POSIX and on Windows | yes | choice by import; one read inside the lock; `fcntl.flock`; `msvcrt.locking`; timeout exits 1 | A1, A2, A5 |
| R2 | UTF-8 on every platform | yes | `encoding` on each `open`; a BOM tolerated; LF line ends; messages never fail; a non-UTF-8 file exits 1 | A3, A4 |
| R3 | Escaped scalars and a stable round trip | yes | JSON scalars; YAML-printable escapes; `schema_version: 2`; old files read as before | A5, A6 |
| R4 | A failed run reaches the operator | yes | the failure rule; the disagreement step; the three bootstrap files; `S/SKILL.md`; the guide | A8 |
| R5 | `S/SKILL.md` names no vendor tool | yes | the phase boundary as trigger; the schema; §6 as the code locks; version 1.2 | A8, A12 |
| R6 | WI-39 for `update_state.py` | yes | the real directory leaves `sys.path`; no bytecode; a module import keeps the path; the record notes it | A7 |
| R7 | Tests and CI | yes | the staged test module; the Windows stand-in; the contract test; the CI step | A9, A10, A13 |
| R8 | Staging and records | yes | the four stages; the checks; the settings readings; the changelogs; the architecture; the restart | A11, A12, A13 |

## 3. Requirements

### R1 — the lock on POSIX and on Windows

- **R1.1** The script chooses its lock by import. When `import fcntl` succeeds, it uses `fcntl`.
  Otherwise it imports `msvcrt`. When neither imports, it prints a message that names both
  modules and exits 1, before it writes anything. `--help` works without either module.
- **R1.2** The script reads `latest.yaml` once, inside the lock, then merges and writes it. The
  read before the lock, at `S/scripts/update_state.py:162@c6666c4` `# 1. Read existing state`,
  is removed (D13). The lock file is `latest.yaml.lock` in the same directory.

  **Why.** The base merges the result of that read only into values that the read inside the
  lock computes again.
- **R1.3** On POSIX the script takes `fcntl.flock(fd, fcntl.LOCK_EX)` and releases it with
  `fcntl.LOCK_UN`. It waits with no time limit, as at the base.
- **R1.4** On Windows the script takes `msvcrt.locking(fd, msvcrt.LK_LOCK, 1)` at offset 0 of the
  lock file. It releases the same byte with `msvcrt.LK_UNLCK`.
- **R1.5** `LK_LOCK` tries 10 times, 1 second apart, and then raises `OSError`. The script then
  prints a message that names the lock file and exits 1. `latest.yaml` keeps its bytes.
- **R1.6** The script opens the lock file with `os.open(path, os.O_RDWR | os.O_CREAT, 0o644)`:
  for reading and writing, created when absent, never truncated, at position 0. It is not an
  `open()` call of TC-07.
- **R1.7** The lock code is part of `update_state.py`. The script imports no module of the
  repository (D3).
- **R1.8** The merge keeps its base rules. An empty value of an `--add_*` option records
  nothing. `recent_decisions` keeps its last 10 items. `--add_blocker` and
  `--add_completed_task` skip a value that the list already holds.
- **R1.9** Two runs that create `.agent/sessions/` at the same time both succeed: the script
  calls `os.makedirs(..., exist_ok=True)`, inside its error handling (D16).

### R2 — UTF-8 on every platform

- **R2.1** Each `open()` of the script passes an encoding. A read passes `encoding="utf-8-sig"`,
  which drops a leading byte-order mark (D14). The write passes `encoding="utf-8"` and
  `newline="\n"`, so the file has LF line ends and no byte-order mark on every platform.
- **R2.2** The script reconfigures `sys.stdout` and `sys.stderr` with `errors="backslashreplace"`.
  No message of the script raises an encoding error on a console or a pipe.
- **R2.3** An existing `latest.yaml` that is not valid UTF-8 stops the run. The script prints a
  message that names the file, says it is not UTF-8, and says to save it as UTF-8 or delete it.
  It exits 1, and the file keeps its bytes (D9).

### R3 — escaped scalars and a stable round trip

- **R3.1** The script writes each string value as a YAML double-quoted scalar:
  1. `json.dumps(value, ensure_ascii=False)` encodes the value;
  2. each character outside the YAML 1.2 printable set becomes its `\uXXXX` escape;
  3. U+0085, U+2028 and U+2029 become `\u0085`, `\u2028` and `\u2029`.
- **R3.2** `context_summary` is such a scalar too. The script no longer writes the block form `|`
  (D6). It strips the summary's outer whitespace, as at the base.
- **R3.3** The first line of the file is `schema_version: 2`. The reader takes the version from
  the first line only.
- **R3.4** With `schema_version: 2` in the file, the reader decodes each preserved value with
  `json.loads`: `session_id` and the items of `active_blockers`, `recent_decisions` and
  `completed_tasks`. An item that `json.loads` rejects is read as at the base.
- **R3.5** Without `schema_version: 2`, the reader reads the file as at the base. The next write
  stores the same strings in the encoding of R3.1. A revert to the base script reads a version 2
  file in the base way: each escape stays in the value as literal text.
- **R3.6** A string that the command line can carry is read back unchanged after any number of
  runs. A lone surrogate of `surrogateescape` is such a string. The escapes of a high and a low
  surrogate, written by hand, read back as one character: `json.loads` joins them. The command
  line cannot carry such a pair.
- **R3.7** PyYAML `safe_load` parses each file that the script writes, and yields the values that
  the script wrote. The script itself does not import PyYAML (D5).

### R4 — a failed run reaches the operator

- **R4.1** The failure rule stands in the `ON PHASE BOUNDARY` list of `CLAUDE.md`, and in the
  `Session State Persistence` section of `AGENTS.md` and of `GEMINI.md`:
  1. on a non-zero exit of `update_state.py`, the agent tells the operator in the same reply;
  2. the message names the command, the exit code and the last line of the output;
  3. the agent does not write `.agent/sessions/latest.yaml` by hand in place of the run;
  4. the agent continues the task.

  The rule leaves each stop rule of a workflow in force, such as `framework-upgrade` §5 step 0.
- **R4.2** The `SESSION RESTORATION (BOOTSTRAP)` section of the same three files gains a
  disagreement step. When the state was restored and `docs/TASK.md` exists, the agent reads its
  H1 and its Task ID:
  1. Both `current_task.name` and `docs/TASK.md` carry a task ID, and the two differ. The
     announcement says `Session state and docs/TASK.md disagree` and names both IDs. The user's
     request decides which task continues; when it does not decide, the agent asks the operator.
  2. Either carries no task ID. The announcement names the H1 of `docs/TASK.md` beside the
     restored task, and the agent asks nothing.
  3. The two IDs are equal. The announcement stays as before.
- **R4.3** `S/SKILL.md` §2 states the disagreement step, and §3 states the failure rule. §3 keeps
  its paragraph for roles that cannot run a command.
- **R4.4** `System/Docs/SESSION_CONTEXT_GUIDE.md` changes in four places:
  - §1 states both rules, with the stop rules of a workflow and the case with no task ID;
  - §4, Risk A, names both rules as mitigations;
  - §5 names macOS, Linux and Windows;
  - §6 names `current_task.status`, states that the file is UTF-8, and states that the script
    drops a key that it does not write.

### R5 — `S/SKILL.md` names no vendor tool

- **R5.1** `S/SKILL.md` names its trigger as each phase boundary, the wording of the bootstrap
  files. It contains no `task_boundary`, no `read_file` and no `view_file` (D8).
- **R5.2** §1 states the file's format: UTF-8, LF, `schema_version: 2`, the keys, and JSON
  scalars. It states that the script owns the file and drops a key that it does not write.
- **R5.3** §6 states the lock as the script takes it:
  - one exclusive lock on `latest.yaml.lock` around the read, the merge and the write;
  - `fcntl.flock` on POSIX, with no time limit;
  - `msvcrt.locking` on Windows, which waits about 10 seconds and then exits 1.

  The pseudo-code of a read lock is removed.
- **R5.4** The frontmatter `version` of `S/SKILL.md` becomes `1.2`.
- **R5.5** `System/Docs/SKILLS.md` and `System/Docs/WORKFLOWS.md` stay unedited: no skill and no
  workflow is added, renamed or removed.

### R6 — WI-39 for `update_state.py`

- **R6.1** Run as `__main__`, before every import but `os` and `sys`, the script removes from
  `sys.path` each entry that is its own directory. Its own directory is the directory of
  `__file__` as called and of its real path. An entry is that directory when its real path,
  through `os.path.normcase`, or its device and inode, match one of them. The script sets no
  bytecode option (D15).
- **R6.2** A module import of the script, such as a test's
  `importlib.util.spec_from_file_location`, leaves `sys.path` unchanged.
- **R6.3** The WI-39 record gains a progress blockquote after its provenance banner, where ARC-8
  holds its resolution. It names TASK 127 and `update_state.py`, and says that nine scripts
  remain. Its status stays `open`, and its index line stays as it is.

### R7 — tests and CI

- **R7.1** `S/scripts/tests/test_update_state.py` keeps the 6 tests of SS-1 and gains the tests
  of §5. A test runs the script in a temporary root that holds its own `.git`. No test writes
  under the repository.
- **R7.2** A test runs the Windows branch on POSIX. At run time it writes, in a temporary
  directory, a `sitecustomize.py` that blocks `import fcntl` and provides a `msvcrt` stand-in. It
  starts the script with that directory on `PYTHONPATH`. The stand-in implements `locking` with
  `fcntl.lockf` on the same byte, and logs each call (D10). No such file is committed.
- **R7.3** A test runs the script under `LC_ALL=C`, `PYTHONUTF8=0` and `PYTHONCOERCECLOCALE=0`.
  There, Python's locale encoding is US-ASCII on macOS (§8, run 5) and ASCII on Linux (PEP 538
  and PEP 540 then leave the C locale in force). On Linux the command line is decoded in ASCII
  too, so the test passes non-ASCII text through an existing state file.
- **R7.4** `tests/test_session_state_contract.py` is a new test module of `unittest.TestCase`
  classes. It checks the documents of R4 and R5, `docs/ARCHITECTURE.md` and the CI step of R7.5.
- **R7.5** The pytest step of `.github/workflows/framework-gates.yml` names
  `.agent/skills/skill-session-state/scripts/tests/` and `tests/test_session_state_contract.py`.

### R8 — staging and records

- **R8.1** The change runs the four stages of `framework-upgrade` §3 step 4 (D11). Stage 1 writes
  two copies under new names:
  - `S/scripts/staged_update_state.py`, the new script;
  - `S/scripts/tests/staged_test_update_state.py`, the new test module. It runs
    `update_state.py`, the final name.

  No rule runs the copies, and no test runner collects them (A13).
- **R8.2** The edits of R4, R5, R6.3, R7.4, R7.5 and the records land in place before stage 3.
- **R8.3** The stage-3 patch gives `update_state.py` and `test_update_state.py` the bytes of their
  staged copies. It touches no other path and holds no staged copy. Stage 3 removes each copy
  once its file hashes to it. Stage 3 adds no settings test.

  **Why.** `tests/test_committed_settings.py:74` already pins the allow rule, and no
  registration changes.
- **R8.4** On a failure of stage 3 or stage 4, the run writes back each removed copy from its
  file and runs `git apply -R` of the patch. A file that hashes otherwise, or a failed
  `git apply -R`, stops the run for the operator.
- **R8.5** The behaviour check runs in a throwaway worktree outside the repository. The worktree
  holds the live tree's files and the stage-3 patch. There, the gates of
  `.github/workflows/framework-gates.yml` and the new test module pass.
- **R8.6** The check of `framework-upgrade` §3 step 4 runs each command below, from the
  repository root unless a directory is named:
  - before and after stage 3:
    - `python3 -m pytest` from the root and from `S/`;
    - `python3 tests/run_tests.py`;
    - the local rule's `python3 -m unittest discover -s tests -v`, which runs the contract test;
    - the user rule's `python3 -m unittest discover -s scripts/tests`, from `S/`;
  - after stage 3, from `S/scripts/`: `python3 -m pytest`, and the local rule's
    `python3 -m unittest discover -s tests -v`, which there runs `scripts/tests`;
  - after stage 3, the committed rule of `update_state.py`, on the live state file, with the
    four required options and no `--add_*` option:
    - one run with the live base-format file, then one run with the version 2 file it becomes;
  - after stage 3, on a stand-in state file (R8.10), in this order:
    1. one run with no state file; it writes the stand-in;
    2. one run with each of `--add_decision`, `--add_blocker`, `--add_completed_task`,
       `--clear_blockers` and `--predicted_steps 3`. A string value has the form
       `TASK 127 check: <option>`;
    3. one run with `--help`;
    4. one run with the stand-in written again with a byte-order mark in front;
    5. the 15 rules of the user's settings that run the script by an absolute path. That path
       lies in a sibling checkout whose skill directory links into this repository;
    6. last, one run with a stand-in that is not UTF-8, which exits 1 and writes nothing.
- **R8.10** For the runs on a stand-in, the run renames the live `latest.yaml` to
  `latest.yaml.keep-127` in the same directory. After the last run it removes the stand-in and
  renames the file back. Then it records the session state again through `update_state.py`. The
  check values stay out of the live history. On any other exit after the rename, the run first
  removes the stand-in and renames the file back. Under the stop rule of `framework-upgrade` §3
  step 4, it moves neither file and names both to the operator.
- **R8.7** The run reads `.claude/settings.local.json` and the user's `~/.claude/settings.json` at
  §2.2, at §4.5 and after the gates of stage 3. The audit record names each file of the change
  that a rule of either file runs, and quotes no rule.
- **R8.8** `CHANGELOG.md` and `CHANGELOG.ru.md` hold v3.47.0. `docs/ARCHITECTURE.md` names
  `msvcrt` beside `fcntl` at its two statements of the session-state lock.
- **R8.9** The run tells the operator to restart the session: the change edits `CLAUDE.md`,
  `AGENTS.md` and `GEMINI.md` (`framework-upgrade` §4 step 3).

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — An agent on Windows records a phase boundary

- **Actors.** An agent in Claude Code on Windows 10; Python 3.13; the ANSI code page cp1251.
- **Precondition.** TASK 127 has landed.
1. The agent runs `update_state.py --mode M --task "TASK-031 «тест» → ok" --status S --summary
   "line one"`.
2. The script imports `msvcrt`, locks byte 0 of `latest.yaml.lock`, reads, merges and writes the
   file.
3. The script prints `Session state updated` and exits 0.
- **Alternative 2a.** Another agent holds the lock. `LK_LOCK` waits and then succeeds.
- **Alternative 2b.** The lock stays held for 10 tries. The script exits 1; UC-3 follows.
- **Postcondition.** `latest.yaml` is UTF-8 with LF line ends, and its first line is
  `schema_version: 2`. PyYAML reads `TASK-031 «тест» → ok` back from `current_task.name`.

### UC-2 — Two agents record a boundary at the same time

- **Actors.** Two agents of one team; one host, POSIX or Windows.
1. Both run the script with `--add_completed_task`, each with its own task.
2. One takes the lock; the other waits.
- **Postcondition.** `completed_tasks` holds both tasks.

### UC-3 — The script exits non-zero

- **Actors.** Any agent with a shell tool.
1. The agent sees a non-zero exit of `update_state.py`.
2. In the same reply, it tells the operator the command, the exit code and the last output line.
3. It continues the task. It does not edit `latest.yaml`.
- **Alternative 3a.** A workflow step needs the record, such as `framework-upgrade` §0 step 3.
  That workflow's own stop rules apply.
- **Postcondition.** The operator knows that the state did not change.

### UC-4 — A session starts on a state that disagrees with `docs/TASK.md`

- **Actors.** An agent at session start.
- **Precondition.** `latest.yaml` names TASK-028, and `docs/TASK.md` is TASK-031.
1. The agent reads `latest.yaml`, then the H1 and the Task ID of `docs/TASK.md`.
2. Its announcement says `Session state and docs/TASK.md disagree` and names TASK-028 and
   TASK-031.
3. The user's request decides which task continues. When it does not, the agent asks.
- **Alternative 1a.** `docs/TASK.md` does not exist. The agent announces the state as before.
- **Alternative 1b.** `current_task.name` is `Optimizing Database`, with no task ID. The
  announcement names the H1 of `docs/TASK.md` beside it. It states no disagreement, and the
  agent asks nothing.
- **Alternative 1c.** `docs/TASK.md` has no Task ID. The announcement names its H1, as in 1b.
- **Alternative 1e.** Both IDs are TASK-031. The announcement stays as before.
- **Alternative 1d.** The state names a later task than `docs/TASK.md`. A run stopped between
  `framework-upgrade` §0 and §1 leaves this state. The announcement states the disagreement, as
  in step 2.

### UC-5 — The first run after the upgrade meets an old file

- **Precondition.** `latest.yaml` has no `schema_version`. One decision holds `C:\new\dir`.
1. The script reads the file as at the base.
2. It writes the same strings in the encoding of R3.1, under `schema_version: 2`.
- **Postcondition.** The decision reads back as `C:\new\dir`. Keys that the script does not write
  are gone.

<!-- contract:acceptance -->

## 5. Acceptance criteria

The tests of the test module after stage 3 (R7.1):

- **TC-01** — two runs started together, with distinct `--add_completed_task` → `completed_tasks`
  holds both.
- **TC-02** — the test holds `flock` on the lock file, then starts a run → the run has not exited
  after 2 seconds. While it waits, the test writes a version 2 state whose `completed_tasks`
  holds a marker. After the release the run exits 0, and the marker survives; fails when the
  lock is removed, or when the read moves before the lock.
- **TC-03** — the Windows branch of R7.2 → exit 0; the stand-in logs `LK_LOCK` and then
  `LK_UNLCK`, each on 1 byte at offset 0.
- **TC-04** — the Windows branch, with the stand-in's lock held for its 10 tries → exit 1; the
  message names `latest.yaml.lock`; `latest.yaml` keeps its bytes.
- **TC-05** — `fcntl` blocked and no `msvcrt` → exit 1, the message names both modules, and no
  file is written. `--help` under the same block exits 0.
- **TC-06** — a version 2 `latest.yaml` whose `recent_decisions` holds Cyrillic and `→`, the
  locale of R7.3, and arguments in ASCII → exit 0. The file decodes as UTF-8 and still holds both
  strings; fails when the read or the write of `latest.yaml` loses its encoding.
- **TC-07** — the AST of `update_state.py` → each `open()` call passes an encoding. A read
  passes `"utf-8-sig"`; the write passes `"utf-8"` and `newline="\n"`.
- **TC-08** — `PYTHONIOENCODING=ascii` and a temporary root whose name holds Cyrillic → exit 0,
  and no traceback.
- **TC-09** — 16 runs; run k passes value k of the list below to `--add_blocker`,
  `--add_decision`, `--add_completed_task`, `--task` and `--status`:
  - `"`, `\` and a literal `\n`;
  - LF, CR, TAB, U+007F, U+0085, U+0093 and U+2028;
  - Cyrillic and an emoji;
  - `: `, `#` and a leading space;
  - a lone surrogate.

  After the 16th run, `active_blockers` and `completed_tasks` hold the 16 values in order, and
  `recent_decisions` holds the last 10. PyYAML yields the same lists, and the 16th value from
  `current_task.name` and `current_task.status`.
- **TC-10** — an old file of UC-5, with a decision `C:\new\tab` and a line
  `schema_version: 2` below its first line → the strings survive. The first line of the new
  file is `schema_version: 2`, and PyYAML parses it; fails when the reader takes the version
  from any line.
- **TC-11** — a `latest.yaml` with bytes that are not UTF-8 → exit 1; the message names the file
  and `UTF-8`; the file keeps its bytes.
- **TC-12** — copies of the script beside planted modules → exit 0, and no planted module writes
  its marker; fails when the `sys.path` filter is removed:
  - planted as sources: each module that the script imports, found from its AST, and `msvcrt`
    and `_winapi`, but `datetime`;
  - planted as a sourceless `.pyc` with no source beside it: `datetime`;
  - one run calls the copy by its path, one through a symbolic link to its directory, and one
    through a path in other letter case where the volume ignores case;
  - one run calls a symbolic link to the copy, from a directory that holds planted modules too.
- **TC-13** — a module import of the script → `sys.path` is unchanged. TC-13 and TC-18 compile
  the script in memory, so neither reads nor writes `__pycache__/` beside it.
- **TC-14** — a summary of two lines → `context_summary` is one JSON scalar that decodes to both
  lines. A summary with outer spaces is stored without them; fails when the strip is removed.
- **TC-15** — a version 2 file that starts with a byte-order mark → its values are decoded as
  version 2, and the new file has no byte-order mark.
- **TC-16** — `--task ""` → exit 0, and PyYAML reads `""` from `current_task.name`.
- **TC-17** — the merge rules of R1.8 → an empty `--add_blocker` and an empty `--add_decision`
  record nothing. A second `--add_blocker` and a second `--add_completed_task` of one value keep
  one item each.
- **TC-18** — the race of R1.9, every time: `ensure_session_dir` of the imported script, with
  `.agent/sessions` present and `os.path.exists` reporting it absent → no exception; fails when
  `exist_ok=True` is removed.

The tests of `tests/test_session_state_contract.py` (R7.4):

- **TC-C1** — the failure rule of R4.1 stands in the three named sections, in `S/SKILL.md` §3, and
  in the guide's §1 and its Risk A, with "the operator in the same reply".
- **TC-C2** — `Session state and docs/TASK.md disagree` stands in the three `SESSION RESTORATION`
  sections, in `S/SKILL.md` §2, and in the guide's §1 and its Risk A.
- **TC-C3** — `S/SKILL.md` holds no `task_boundary`, `read_file`, `view_file`, `lockf` or
  `Shared Lock`, and §3 keeps the paragraph for roles that cannot run a command.
- **TC-C4** — `S/SKILL.md` §1 names `schema_version: 2`, `UTF-8` and the dropped key; §6 names
  `fcntl.flock` and `msvcrt.locking`; the frontmatter has `version: 1.2`.
- **TC-C5** — the guide names `current_task.status` and not `task_status`; its §5 names macOS,
  Linux and Windows; its §6 names `UTF-8` and the dropped key.
- **TC-C6** — the pytest step of the CI workflow names both paths of R7.5.
- **TC-C7** — `docs/ARCHITECTURE.md` names `msvcrt` at both statements of the session-state lock.

The criteria of the task:

- **A1** — TC-01, TC-02, TC-18 and the 6 SS-1 tests pass on POSIX.
- **A2** — TC-03, TC-04 and TC-05 pass.
- **A3** — TC-06, TC-07, TC-08 and TC-15 pass.
- **A4** — TC-11 passes.
- **A5** — TC-09, TC-14, TC-16 and TC-17 pass.
- **A6** — TC-10 passes.
- **A7** — TC-12 and TC-13 pass, and the WI-39 record holds the note of R6.3.
- **A8** — TC-C1 to TC-C5 pass.
- **A9** — `tests/test_mock_agent.py` passes after stage 3.
- **A10** — TC-C6 passes, and the gates pass on the patched worktree and, after stage 3, on the
  tree.
- **A11** — the checks of R8.6 pass, and the audit record holds the readings of R8.7.
- **A12** — TC-C7 passes, the changelogs hold v3.47.0, and `git diff --quiet <base> --` exits 0
  for `System/Docs/SKILLS.md` and `System/Docs/WORKFLOWS.md`.
- **A13** — before stage 3, these list no staged file: `python3 -m pytest --co -q` from the root
  and from `S/`, and `python3 -m unittest discover -s scripts/tests -v` from `S/`.

<!-- contract:open-questions -->

## 6. Open questions

None. The operator answered the scope (D1) and WI-39 (D2).

## 7. Decisions

- **D1**, 2026-10-26, operator: native Windows is supported on the critical path, in four tasks.
  Answers "Да с твоими рекомендациями" and "согласен с рекомендацией". This task is the first;
  §9 names the other three.
- **D2**, 2026-10-26, operator: this task removes the script's directory from `sys.path` (WI-39).
  Answer "Включить в TASK 127". The decision D10 of 2026-10-08 required the operator's review of
  such a change. Rejected: WI-39 left as it is, with the gap named in the audit record.
- **D3**, 2026-10-26, orchestrator: the lock code stays inside `update_state.py`. Rejected: one
  module `.agent/tools/_lock.py` shared by the skills. A skill installs alone, by its own link or
  copy, and cannot import from `.agent/tools/`. An added import path also widens WI-39.
- **D4**, 2026-10-26, orchestrator: `msvcrt.locking` on one byte of the lock file. Windows
  releases it when the process exits. Rejected: a lock file created with `O_CREAT | O_EXCL`. A
  process that dies holds it, and every later run fails until someone removes the file.
- **D5**, 2026-10-26, orchestrator: JSON scalars from the standard library, with
  `schema_version: 2`. Rejected: PyYAML, which needs a virtual environment; the bootstrap files
  run the script with the bare `python3`. Rejected: single-quoted YAML, which has no escape for a
  line break.
- **D6**, 2026-10-26, orchestrator: `context_summary` is a JSON scalar. Rejected: the block form
  `|`. A first line that starts with a space, a CR or a character outside the printable set makes
  the file invalid or changes the value.
- **D7**, 2026-10-26, orchestrator: the disagreement step is an instruction to the agent, and it
  compares task IDs only where both sides carry one. Rejected: a `--check` option of the script.
  A task in `current_task.name` is free text, and projects write its ID in different forms, such
  as `TASK 127` and `TASK-031`.
- **D8**, 2026-10-26, orchestrator: `S/SKILL.md` drops `task_boundary`, `read_file` and
  `view_file`. Rejected: an Antigravity note. v3.20.11 removed that framing from `GEMINI.md`,
  which Antigravity also reads.
- **D9**, 2026-10-26, orchestrator: a state file that is not UTF-8 stops the run. Rejected: a
  fallback to the locale encoding. cp1251 decodes almost every byte sequence, so a wrong guess
  gives other text and no error.
- **D10**, 2026-10-26, orchestrator: the script chooses the lock by the import of `fcntl`.
  Rejected: `os.name == "nt"`. A test on POSIX could reach that branch only by patching `os` for
  the whole interpreter.
- **D11**, 2026-10-26, orchestrator: the script and its test module are staged; the documents
  are edited in place. An allow rule names the script. The test module runs it, and until stage 3
  the old tests stay green on the live tree.
- **D12**, 2026-10-26, orchestrator: the skill's tests join the existing CI step on Ubuntu. A
  Windows job is the fourth task of D1.
- **D13**, 2026-10-26, orchestrator: the read before the lock is removed. Rejected: kept with an
  `encoding`. Its result changes no output, and it would print a second message for a file that
  is not UTF-8.
- **D14**, 2026-10-26, orchestrator: a read uses `utf-8-sig`. PowerShell 5.1 and some editors
  write a byte-order mark. With `utf-8`, the mark hides `schema_version: 2` from the reader, and
  a version 2 file is read in the base way.
- **D15**, 2026-10-26, orchestrator: the script sets neither `sys.dont_write_bytecode` nor
  `sys.pycache_prefix`. Those settings of `rebase_links.py` guard siblings that it loads by
  explicit path; this script loads none. Rejected: both settings, as the WI-39 record lists them.
  The prefix also sends every standard-library import to its source, at every phase boundary.
- **D16**, 2026-10-26, orchestrator: `ensure_session_dir` creates the directory with
  `exist_ok=True`, inside the script's error handling. At the base, TC-01 failed in 3 of 25 runs
  with `FileExistsError` on `.agent/sessions` (§8). Rejected: leaving it, since UC-2 is two agents
  at the same time.
- **D17**, 2026-10-26, orchestrator: fix round 1 of stage 2. Both reviews of round 1 passed; the
  run fixes their findings in scope before registration:
  - S-1 and CR-1: R6.1 matches the directory by device and inode too, and TC-12 adds its runs;
  - CR-2: TC-02 writes a marker while the run waits; S-2 and CR-3: TC-13 and TC-18 compile the
    script in memory;
  - CR-4, CR-5 and CR-7: TC-14, TC-C1 and TC-10 gain their cases, and R3.3 its first line;
  - CR-6 and CR-8: the wording of R4.2, of the guide, of the docstring and of `S/SKILL.md`;
  - S-4: the limit of R3.6. Rejected: an escape form of JSON for a lone surrogate pair; JSON has
    none.
  The findings before the task stay as one line each in the audit record.
- **D18**, 2026-10-26, orchestrator, under the operator's rule recorded at TASK 124 D17: stage 2
  closes at round 2. Both reviews passed, and the findings left are LOW or notes. Each stands as
  a limit of this task:
  - a volume that reports no inode number leaves the check by name alone, which is
    case-sensitive on POSIX; APFS, ext4, NTFS, SMB and FAT report inode numbers;
  - the run of TC-12 through a linked file fails only on Windows, where `sys.path[0]` is the
    link's directory; the CI job on Windows of the fourth task of D1 runs it there;
  - TC-13 fails on a removed `__main__` guard only when `S/scripts/` is on `sys.path`, as in a
    run from that directory;
  - the check by device and inode assumes that the pair names one directory. Where it repeats,
    the script loses a standard-library entry and exits 1.
  Rejected: a third round. The operator's rule closes a task once both reviews pass and only
  narrow LOW routes remain.

## 8. Measurements of this run

Measured at the base revision. The runs used a temporary root with its own `.git`, under the
session's scratchpad.

- `S/scripts/update_state.py` has 277 lines. `open(` occurs on lines 166, 203, 207, 215 and 263;
  line 203 is a comment, so four calls pass no `encoding`.
- Run 1: `fcntl` blocked by a meta-path finder → `ModuleNotFoundError: No module named 'fcntl'`,
  exit 1.
- Run 2: `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`, `--summary "TASK-031 → ok"` → `Error
  updating session state: 'ascii' codec can't encode character '\u2192'`, exit 1.
- Run 3: `--task 'say "hi"'` → exit 0; PyYAML `safe_load` raises `ParserError`.
- Run 4: `--add_decision 'C:\new\dir'` → exit 0; PyYAML `safe_load` raises an error at line 16,
  column 13.
- Run 5: under the locale of run 2, `locale.getpreferredencoding(False)` is `US-ASCII` on macOS
  with Python 3.14.8.
- `python3 -m pytest --co -q` from the root collects 725 tests. None lies under `.agent/`.
- Run 6: TC-01 of the new test module against the base script, 25 times in a new root each →
  3 failures, each `FileExistsError: [Errno 17] File exists: '<root>/.agent/sessions'`. Against
  the new script → 0 failures in 25.
- Callers of the script: the bootstrap files, the workflows, and
  `.agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py`.
  `tests/test_mock_agent.py` runs that mock against a sandbox copy of the script.
- `S/SKILL.md` names `task_boundary` on lines 15, 40, 53, 54 and 66, and `read_file` and
  `view_file` on line 22.
- `docs/ARCHITECTURE.md` names `fcntl` as the lock of the session state on lines 120 and 215.
- The user's settings hold 15 allow rules that run the script by an absolute path with fixed
  arguments. The path lies in a sibling checkout whose skill directory links into this
  repository. One rule of the local settings names a path that does not exist.
- `tests/test_concurrent_state.py` deletes and rewrites the live `latest.yaml` when run by hand.
  No runner collects it: it defines no test function. This is a finding before the task.

<!-- contract:out-of-scope -->

## 9. Out of scope

- The archive chain on Windows: `archive_move.py`, `rebase_links.py` and `slot_links.py` — the
  second task of D1.
- The locks and `O_NOFOLLOW` of `run-feedback` — the third task of D1.
- A CI job on `windows-latest`, and a run of UC-1 on Windows — the fourth task of D1.
- WI-39 for the other nine scripts — the WI-39 record.
- `os.killpg` and `signal.SIGKILL` of `render_check.py` — a `/light` task, if the operator asks.
- The `python3` launcher on Windows. The allow rules name `python3`, which the python.org
  installer of Python 3.13 does not create. The fourth task of D1 asks the reporter.
- A statement of supported platforms in `README.md` — the fourth task of D1.
- A time limit for the POSIX lock, which waits with no limit at the base.
- `tests/test_concurrent_state.py` — §8; a record needs the operator's decision.
- `docs/migration-to-claude.md`, which records the migration as it was done.
