# Framework Audit 109 — Python 3.11 is the floor and 3.14 the main version

- **Task:** 109 `python-floor-3-11-main-3-14`. It archives to
  `docs/tasks/task-109-python-floor-3-11-main-3-14.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1,
  Modes A and B.
- **Date:** 2026-10-03. **Base revision:** `cd9a45547f69460b7630e5966a54c9ec6b94a6de`, clean tree
  at start.
- **Source:** WI-33, with the operator's choice of 2026-10-03: minimum 3.11, main version 3.14.

## 0. Emergency Bypass

None set.

## Mode A — SPECIFICATION AUDIT — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Root Integrity | PASS — R1–R7 each name an acceptance id; R6's pin is written before the edits |
| 2 | Skill Compatibility | PASS — no new agent, prompt or workflow; TIER 0 skills untouched |
| 3 | Documentation | PASS — R1 edits the README pair and `System/Docs/ORCHESTRATOR.md`; R7 covers both changelogs |
| 4 | Migration | PASS — consumer projects receive the change through `install.sh update`; no session state changes |
| — | Blocking conditions | None triggered |

**Blocking conditions.** `core-principles` and `skill-safe-commands` are unmodified. `CLAUDE.md`,
`AGENTS.md` and `GEMINI.md` are unmodified. No workflow is added.

**Check 4.** No version below 3.11 was tested before this task. On 3.9, five `skill-creator`
scripts and `verify_pin.py` fail at import. After this task, the installer, the preflight and the
benchmark stop below 3.11 with a message that names the versions. A project whose installer ran
on 3.9 or 3.10 gets that message from now on (TASK D1).

## Mode B — PLAN AUDIT — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Verification step | PASS — A3 and D3 run the pin; E1, E2 and E6 run the mutations, the old interpreter and every CI gate |
| 2 | Rollback | PASS — base `cd9a455` recorded at a clean tree; 18 edited and 2 created paths declared |
| 3 | Atomic updates | PASS — five clusters, one requirement group each |
| 4 | Test coverage | PASS — a new unittest module, written first and failing on the base tree |

## Execution (§3)

- **Base check:** HEAD equals the base; the edited paths are tracked, the created paths are not
  ignored, and every path has a safe form.
- **Cluster A:** the pin failed on the base tree, 8 of its first 9 tests red.
- **Deviation, TASK D6:** the first guard in `grade_figures.py` failed the eval selftest row
  TC-ME-22. Every committed campaign report records the grader's sha256, and the row re-derives
  the stored report. The guard was removed; the grader stops through its import of `run_evals`.
  `grade_figures.py` is identical to the base.

## Review round 1 (E7)

Two reviewers read the frozen tree (fingerprint `4f7a0a6821f1`): one code reviewer with the plain
exhaustive prompt, and one security auditor. Both left the tree byte-identical. Same-model
agreement is corroboration, not independent confirmation.

- **Code review:** approved; 0 BLOCKING, 2 MAJOR, 19 MINOR and nits.
- **Security audit:** PASS; 0 critical, 0 high, 3 MINOR, 5 INFO. External scanners (semgrep,
  gitleaks, bandit, pip-audit) are not installed, so only its pattern layer ran.

| Finding | Severity | Resolution |
| :--- | :--- | :--- |
| CR-1, SEC-3: exit 1 reads as a verdict in `verify_pin.py` and `run_evals.py` | MAJOR | guards exit 2 (TASK D7); exit-code descriptions name the case |
| CR-2: a guard is proven against a faked version only | MAJOR | TC-03 parses under the 3.9 grammar, allows only 3.9 standard-library imports, and walks the grader's imports |
| SEC-1: the PyYAML probe imports `yaml.py` from the target project | MINOR | `-P` (TASK D8); TC-07 plants decoys |
| SEC-2: `install.py` has no guard | MINOR | guard, exit 2 |
| SEC-4: the tests do not watch the skills for a write | MINOR | TC-04 runs with `-B` and compares the skill directories before and after |
| CR-3, CR-17: `doctor.py` overstated, and its wording differs | MINOR | both messages name both versions; the changelogs say what it does |
| CR-4: the mutation claim has no record | MINOR | the table below |
| CR-5, CR-6, CR-16: stale or inexact wording; a patch version | MINOR | TASK revision 2; v3.34.0 (TASK D10); a longer Migration note |
| CR-7: README covers less than it says | MINOR | `render_corpus.py` guarded; README names the guarded group |
| CR-8: the grader's message names `run_evals.py` | MINOR | each guard names the script that was run |
| CR-9, CR-10, CR-11: TC-06 and TC-02 gaps | MINOR | broader patterns across line breaks, a wider scope, one fact file exempt; no CI job below the minimum |
| CR-12, SEC-7: the TC-05 shim depends on the caller | MINOR | a `/bin/sh` wrapper, a minimal environment, a skip on a no-exec directory |
| CR-13: ARCHITECTURE §9.2 is stale | MINOR | the wrapper line lists its checks |
| CR-14: `uninstall` stops below 3.11 | MINOR | accepted (TASK D9); the Migration note says so |
| CR-15: README pointers resolve to the project's own README | MINOR | `ORCHESTRATOR.md` states the pair itself (TASK D2) |
| CR-18: the wrapper test's stub misses `-P` | MINOR | the stub matches the import |
| CR-19: a dead branch in the grader | INFO | TASK §7; the next grader revision removes it |
| CR-20: no 3.11 interpreter here; CI has not run 3.14 on Linux | INFO | open: the first CI run on the commit is that check |
| CR-21: nits | INFO | fixed, except the rebased TASK link of the PLAN 108 archive, which the archive protocol writes |
| SEC-5, SEC-6, SEC-8: heredoc temp file, trusted `python3`, CI coverage | INFO | no action; supply chain stays with WI-31 |

## Review round 2 (verification)

The same two reviewers checked the fixes on the frozen tree (fingerprint `e58c996912f8`) and left
it byte-identical.

- **Code review:** merge. 15 findings resolved; F2, F9, F18 and F21 partial; F11 resolved with a
  gap; F20 open by nature; 5 new MINOR items and one note on SEC-1.
- **Security audit:** PASS. F1–F8 resolved or accepted as stated, and 6 new INFO items.

The fixes below came after round 2. No third review ran; the mutations below cover them.

| Item | Resolution |
| :--- | :--- |
| CR F2 partial: a 3.11 name in a `from` import (`typing.Self`, `datetime.UTC`, `enum.StrEnum`) passes TC-03 | `FROM_3_9`, a list of names 3.9 has, checked above each guard and in the grader's imports |
| CR F2 rest: `dataclass(slots=True)` in an imported module | out of reach of a static check; TASK §7 and the test docstring state it |
| CR F9 partial: "or greater", "или новее", `.claude/agents`, other top-level `docs/` files | in the patterns and the scope; the current TASK and PLAN stay out, since they quote the old claims |
| CR F11 gap: an unquoted `python-version: 3.10` | the single-job pattern accepts either form |
| CR F18 partial: wrapper case 1 below the minimum | it reports SKIP with the wrapper's own message |
| CR ND1: `render_corpus.py` exit 2 without `not rendered:` | the guard message starts with it (ARCHITECTURE §10.5, L6) |
| CR ND2: under `python -m <package>` a guard names `__main__.py` | falls back to the module's own name; a TC-04 case imports each guarded module with that `argv[0]` |
| CR ND3, SEC N4: TC-07 lacks the no-exec skip; TC-05 skips on any `OSError` | both probe their shim and skip on `PermissionError` only |
| CR ND4: TC-02 rejects the stricter `-I` | it accepts `-P` or `-I` |
| CR ND5: TC-04 snapshots the corpus as well | accepted: CI runs the suite alone |
| CR SEC-1 note, `-P` keeps `PYTHONPATH` entries | accepted and stated (TASK D8) |
| SEC N1: `doctor.py` runs `-m pytest` from the current directory | `-P` on 3.11 or newer |
| SEC N2: pip requirements without hashes have no record | not filed: the operator named no retro item (2026-10-04); this line is its only record |
| SEC N3, N6: TC-04's scope; an interpreter without `-P` | accepted |
| SEC N5: TC-07 writes bytecode into `System/scripts` | `PYTHONDONTWRITEBYTECODE=1` in the minimal environment |
| CR F21: test methods without docstrings | accepted: each class name states the case |

## Mutations (E1)

Each mutation was applied alone, the module run, and the file restored. All 32 fail it. One
legitimate variant passes, and so does the module after the restores: 14 tests, 37 subtests.

| Group | Mutations |
| :--- | :--- |
| Statement | README names another minimum; `ORCHESTRATOR.md` another pair |
| Preflight | `doctor.py` requires 3.10; its FAIL message drops the main version |
| Installer | `install.sh` checks 3.10; loses its check; probes PyYAML without `-P` |
| Guards | one checks 3.10; one exits 1; one deleted; the `install.py` guard deleted; one names `__main__.py` |
| Reachability | a guard below a statement; `tomllib`, `Self` or `UTC` above a guard; `match` in two files; `StrEnum` in `stats.py` |
| CI | the matrix loses 3.14; gains 3.10; a single job runs 3.10, quoted or not |
| Claims | "Python 3.9+"; "or higher"; "or greater"; a line break; "и выше"; "или новее"; `docs/BACKLOG.md`; `.claude/agents` |
| Grader | `grade_figures.py` stops importing `run_evals` |
| Legitimate variant, passes | the PyYAML probe runs with the stricter `-I` |

## Old interpreter (E2, A3)

Under `/usr/bin/python3` 3.9.6, in an empty directory:

- `install.sh --help` exits 2: "Python 3.9 found. The framework needs Python 3.11 or newer (3.14
  is the main version)."
- `install.py`, `aggregate_benchmark.py`, `verify_pin.py`, `run_evals.py`, `render_corpus.py`,
  `selftest_figure_evals.py` and `grade_figures.py` exit 2. Each message names the script that was
  run; `render_corpus.py` starts its message with `not rendered:`. No file was written.
- `doctor.py`: "[FAIL] Python 3.9.6 is below the minimum 3.11; 3.14 is the main version".

## Gates (E6)

Every step of `framework-gates.yml` passes locally on Python 3.14.4:

- the tooling pytest list: 397 passed;
- `run_tests.py`: 422 tests OK, with the new module;
- the `skill-creator` tests: 90 passed, 4 skipped;
- the `mermaid-authoring-guidelines` tests: 608 passed;
- the lint probe: 97 of 97; the eval selftest: 223 of 223, TC-ME-22 included;
- the formalizer checks: 192 of 192 and 78 of 78; the register probe: 18 of 18;
- the skills: 47 of 47; references, security lint, workflow smoke and the loop contract: clean;
- `tests/installer/test_wrapper.sh`: OK.

More checks:

- The living-corpus reference check reports 0 errors.
- The advisory archive step reports the 8 errors present at the base.
- `--targets-changed --fix` repaired nothing. Its 11 errors were present at the base: links in old
  changelog entries to files of another repository, and the known `review-095` one.
- `scan_register.py` reports no warn on a changed line of the edited markdown files.
- `git status` lists 28 paths: the 24 declared and the run's own four.
- Not run here: the 3.11 job of the CI matrix and Linux with 3.14. The first CI run on the commit
  is that check.

## Retro (§6)

On 2026-10-04 the operator answered the retro question with "nothing". No finding was collected
or filed.
