# TASK 134 — Allow-listed scripts import no module planted beside them (WI-39)

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 134 |
| Slug | allow-listed-script-imports |
| Type | Framework Upgrade, reduced process (D1) |
| Source | WI-39; TASK 133 D1; the operator's request of 2026-10-28 |
| Base revision | `48e10ea` |
| Closes | WI-39 |
| Archive name | `task-134-allow-listed-script-imports.md` |
| Revision | 2 |

**Request.** WI-39: a module planted beside a Python script that an allow rule runs is imported
before the script's own code, at the next approved call, with no prompt. TASK 115, 127 and 128
closed it for `rebase_links.py`, `archive_move.py` and `update_state.py`. TASK 133 D1 set the rest
as this task: the 13 scripts that the committed rules run, and `run_audit.py` of the local rules.

**Revision 2** follows the code review (CHANGES REQUESTED: one MAJOR, seven MINOR, eleven NIT)
and the security audit (PASS: four MEDIUM, six LOW, all before the task but for M1a). The fix
pass:
- `run_tests.py` loads the installer tests' `_base` by its path: with `tests/` before
  `tests/installer/` on the path, a `_base.py` planted in `tests/` stood in for it (M1a, a
  regression of revision 1). It imports `platform` before the discovery, whose probe for `_wmi`
  read `tests/` on POSIX (MAJOR-1, L1). Its comment names no `_load` (MINOR-2);
- TC-AL1 pins each script's exit code, and two fixtures reach the work (MINOR-1). TC-AL3 runs the
  runner too (MINOR-3). TC-AL4 plants in `tests/installer/` and plants `_base` and `_wmi`. TC-AL5
  finds each change of `sys.path` outside the guard, and checks the runner's early imports (N2, N6);
- R5 and §5 state the runner's residual (D8), and the documents name the scripts that a committed
  rule runs (MINOR-5, MINOR-6, L2, N1, N3, N9); one positional reference is repaired (MINOR-4);
- the three findings outside WI-39 go to one backlog record, WI-59 (D9).

Not taken: the Windows jobs (MINOR-7, L5). The guard's code is pinned to that of
`rebase_links.py`, which TC-W16 runs on Windows, and a failure of an unrelated script there would
block the jobs. N4 and N5, a split of TC-AL2 and a cache of the clean runs, change no result.

**Measured at the base** (2026-10-28, Python 3.14.8, macOS):
- none of the 14 scripts removes its own directory from `sys.path`. Five insert it again at module
  level: `selftest_scan.py`, `lint_mermaid.py` and `plan_gantt.py` at the front, `init_skill.py`
  and `validate_skill.py` at the end;
- a `__future__.py` planted beside a script that starts with `from __future__ import annotations`
  runs before the script's first line of code. Nine of the 14 scripts start so. The statement must
  be the first of its module, so no guard can precede it;
- a static check of the nine scripts finds no annotation that Python 3.11 evaluates at definition
  time and that names a value not yet bound.

## 1. Decisions

- D1, 2026-10-28, operator: a reduced process. The run has a TASK and a PLAN, edits in place, the
  tests first and red, and the gates. At the end, one code reviewer with the exhaustive prompt and
  one security auditor review the change, and one fix pass follows. Rejected: the full
  `/framework-upgrade`, for its cost, and Light Mode, which has no security audit for a change of
  security. Skipped: the meta-audits of Mode A and Mode B, the staged copies and stages 1 to 4 of
  `framework-upgrade` §3 step 4, and the check of each allowed command.
- D2, 2026-10-28, operator: the guard works at the level of the script. A sibling module or
  package loads by explicit path. The submodules of a package load by the path search inside the
  package's own directory, as at the base (§5, residual 1).
- D3, orchestrator: the nine scripts lose `from __future__ import annotations`. The base needs no
  annotation quoted for Python 3.11.
- D4, orchestrator: one test module checks all 14 scripts from one table, as TC-G11 of TASK 115
  checks `rebase_links.py`.
- D5, orchestrator: the other scripts of the local rules stay out: `analyze_gaps.py`, the test
  modules that a rule runs by path, and the paths into other checkouts. The local settings are the
  operator's; TASK 133 D1 named `run_audit.py` only.
- D6, orchestrator: `Universal-skills/skills/skill-creator` is a copy. The run copies the two
  changed scripts there, and the operator commits that repository.
- D8, 2026-10-29, operator: `run_tests.py` guards its own imports and the two probes; the test
  modules that it runs, and what they import and start, stay a residual (§5, residual 2).
- D9, 2026-10-29, operator: three findings of the security audit outside WI-39 go to one backlog
  record: the scanners of `run_audit.py`, the `pytest` rules, and the start files of `.venv`.
- D7, 2026-10-29, operator: each script keeps its own copy of the guard. A shared module would be
  found by the path search that the guard closes, and a skill imports nothing from outside its
  directory. A test pins the 17 copies, the three older ones among them, to one code, and the
  comment and `_load` to one text in each group. Each copy's comment has two or three lines.

## 2. Requirements

<!-- contract:requirements -->

The 14 scripts, by group; `S/` stands for `.agent/skills/`:
- A, no sibling: `S/artifact-formalizer/scripts/scan_register.py`, `.agent/tools/task_id_tool.py`,
  and `check_prompt_references.py`, `doctor.py`, `security_lint.py`, `smoke_workflows.py` and
  `validate_skills.py` of `System/scripts/`;
- B, siblings, named in brackets:
  - `S/artifact-formalizer/scripts/selftest_scan.py` (`scan_register`);
  - `S/mermaid-authoring-guidelines/scripts/lint_mermaid.py` (`mermaid_model`, `planarity`,
    `lint_mermaid_parts`) and `plan_gantt.py` (`mermaid_model`);
  - `S/skill-creator/scripts/init_skill.py` and `validate_skill.py` (`skill_utils`);
  - `S/security-audit/scripts/run_audit.py` (`audit`);
- C, a test runner: `tests/run_tests.py`.

- **R1** Each of the 14 scripts runs, under `if __name__ == "__main__":` and before any import but
  `os` and `sys`, the guard of TASK 127 R6.1. An entry of `sys.path` leaves when its real path, in
  `os.path.normcase`, or its `(st_dev, st_ino)` matches the directory of `__file__` as called or of
  its real path.
- **R2** Each script of groups B and C also sets `sys.dont_write_bytecode` and a
  `sys.pycache_prefix` under `os.devnull`. Where `os.devnull` is a relative path, the prefix lies
  under the script's own real path (TASK 131 R4).
- **R3** Each script of group B loads its siblings by explicit path, with
  `importlib.util.spec_from_file_location`, a package with `submodule_search_locations`. It loads
  them in the order of their imports, and reuses a module that `sys.modules` already holds. No
  script inserts its own directory into `sys.path` at module level. A test that imports the module
  keeps its own path.
- **R4** The nine scripts that start with `from __future__ import annotations` no longer hold the
  statement: `scan_register.py`, `selftest_scan.py`, `lint_mermaid.py`, `plan_gantt.py`, and the
  five of `System/scripts/`.
- **R5** `tests/run_tests.py` appends `tests/` and `tests/installer/` to the end of `sys.path`
  before its discovery, so `unittest` does not insert them at the front. It loads the installer
  tests' `_base` by its path. It imports `subprocess` and `platform` before the discovery: on
  import, `subprocess` probes for `msvcrt` or `fcntl`, and `platform` for `_wmi`, which one platform
  or another lacks.
- **R6** The exit codes, the output and the files written of each script stay as at the base.
- **R7** WI-39 closes in its record and in `docs/BACKLOG.md`; both changelogs carry the release.
  `Universal-skills/skills/skill-creator/scripts/` receives the two changed scripts (D6).

## 3. Files

- the 14 scripts of §2;
- `tests/test_allow_listed_imports.py` (new), and `.github/workflows/framework-gates.yml`, whose
  tooling step runs it;
- `S/mermaid-authoring-guidelines/scripts/tests/test_lint_mermaid_package.py`: `_load` is a name
  of the thin file;
- `docs/ARCHITECTURE.md`: the rule of the guard;
- `docs/backlog/wi-39-allow-listed-scripts-import-a-module-planted-beside-them.md`,
  `docs/BACKLOG.md`;
- `CHANGELOG.md`, `CHANGELOG.ru.md`;
- `docs/TASK.md`, `docs/PLAN.md`; the archive of TASK 135;
- revision 2: `docs/backlog/wi-59-*.md` and its index line (D9), and the line of
  `.agent/tools/task_id_tool.py` that `docs/tasks/task-114-subtask-classified-by-h1.md` cites,
  which `check_positional_refs.py --fix` repaired.

## 4. Acceptance

<!-- contract:acceptance -->

In `tests/test_allow_listed_imports.py`, each test copies a script and the files it loads into a
temporary directory and plants modules beside the copy. A planted module creates a sentinel file
when it runs. The planted names are each top-level module that the script and its siblings import,
`__future__`, `msvcrt`, `_winapi` and `fcntl`.

- TC-AL1: each of the 14 scripts, run as an allow rule runs it, with arguments that reach its
  work. Its exit code equals that of a run with nothing planted, which ends without a traceback,
  and no sentinel exists.
- TC-AL2: each script of group B, with a package and an extension module planted under the name
  of each sibling module. A `.pyc` is planted in `__pycache__/` for each sibling module and for a
  submodule of each sibling package. The exit code is as in TC-AL1, and no sentinel exists.
- TC-AL3: TC-AL1 for one script of each group, through a path in other letter case, where the
  volume ignores letter case.
- TC-AL4: `run_tests.py` with stub test modules that import `subprocess`, `platform` and
  `colorsys`, which nothing imports before the discovery. Those names, `_wmi`, `msvcrt` and
  `_winapi` are planted in the stub `tests/` and `tests/installer/`, and `_base` in `tests/`: exit
  0, and no sentinel.
- TC-AL5: none of the 14 scripts holds `from __future__` or inserts a directory into `sys.path` at
  module level, and each runs its guard before any import but `os` and `sys`. The copies of the
  guard are as D7 states.
- TC-AL6: the gates of `framework-gates.yml` pass, on this machine with Python 3.14 and in CI with
  Python 3.11 and 3.14.

Each of TC-AL1 to TC-AL5 fails on the base.

<!-- contract:out-of-scope -->

## 5. Out of scope and residuals

1. A directory or an extension module planted inside the directory of a sibling package, under
   the name of a submodule, wins the path search of that package: `mermaid_model/`,
   `lint_mermaid_parts/`, `audit/` (D2). A `.pyc` there wins only under a name with no source;
   the prefix keeps `__pycache__/` from being read.
2. `run_tests.py` runs the test modules of `tests/` and `tests/installer/` (D8). Such a module
   imports from those directories, `_base.py` puts `System/scripts/` first on the path, and some
   start scripts of `System/scripts/` that carry no guard. The discovery of `tests/installer/` also
   imports a planted `test*.py` and a planted package. So a file planted there can run under the
   rule of `run_tests.py`, as one in the working directory can under the `pytest` rules.
3. An executable on `PATH` that a script runs, such as the scanners of `run_audit.py`.
4. The scripts of the local rules that D5 leaves out, `analyze_gaps.py` among them.
5. The findings that D9 records in WI-59:
   - the scanners of `run_audit.py --scan-type all` run in the scanned tree;
   - the `python3 -m pytest` rules import a planted `pytest.py`;
   - a `.pth` file or `sitecustomize.py` in the `.venv` of the work tree runs at the start of each
     `python3`.
