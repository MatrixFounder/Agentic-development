# Framework Audit 123 — `framework-upgrade` counts local allow rules and checks what a change runs; the findings that TASK 122 left open are fixed

- **Task:** 123 `staging-rules-and-loose-ends`. It archives to
  `docs/tasks/task-123-staging-rules-and-loose-ends.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1.
- **Date:** 2026-10-15. **Base revision:** `09765e1d1379bd70eae996fe87e483ce73cf96fa`, clean tree
  at start (TASK 122, committed and pushed by the operator as `09765e1`; CI passed).
- **Source:** TASK 122 D13 and the findings before the task that TASK 122 recorded; the operator's
  request "запускай TASK-123 и добавь еще эти 4 пункта в работу".

## 0. Emergency Bypass

None.

## Archive (§1)

TASK 122 and PLAN 122 archived under ID 122:
- `task_id_tool.py "render-output-pytest-figure" --proposed-id "122" --no-correction`:
  `generated`, `task-122-render-output-pytest-figure.md`;
- both moves `"ok": true`;
- Step 5.5: 0 rewritten, exit 0; Step 7.6.5: one `SLOT_RESOLVED`, exit 0;
- Step 8 with `--since b6362e3…`: exit 3. It lists the two `INBOUND` records of the v3.13.0
  changelog entries (`CHANGELOG.md:3347@09765e1`, `CHANGELOG.ru.md:3364@09765e1`), which carry no
  reason and stay. Step 8 rewrote no file.

## Research (§1)

The measurements of TASK §8 ran in the session's scratchpad and in temporary directories outside
the repository. The repository `onchain-analytics` was read, not written, to check the revisions of
the pins of R8.1. No repository file was written by the research.

The retro claim `framework-upgrade-staging-rules-and-loose-ends` was taken at the start of the run.

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

The brief carried no fingerprint; the tree held the archive pair and TASK revision 1. The reviewer
had no shell, so the register scan and the reference resolver did not run in its audit.

Must-fix, all MEDIUM:
- M1: a listing shows which file changed, not which code wrote it, and the checked run's own write
  could not be restored.
- M2: the definition of the allow rules dropped the `allowed-tools` of skills and commands.
- M3: Claude Code writes a permanent approval into the local file during the run; the file was read
  once, and §8 did not list the files that the local `unittest discover` rule runs.
- M4: D9 did not say how the patched `render_check.py` and the hash after stage 3 exist without a
  copy outside version control.
- M5: "loaded" had no mechanism, and the top of `run_evals.py` does run.

Minor m1 to m13:
- wildcard rules and `python -m pytest`, and how no cache is written;
- R9.6 against R1.1, and "two lines" in R4.3;
- the pins and the prose of R8;
- two escape residuals, and the residual of the stubs;
- traceability, and the wording of R6.3;
- the comment of line 111 and `EXPECTED_CASES`;
- the Migration paragraph, R9.7 and §9, and three metaphors.

Notes: N1, the local rule that runs standard input as Python; N2, the Mode A checklist holds.

TASK revision 2 applies them: D4, D13, D14 and D15 are new, D5, D6, D8 and D9 state their
residuals or their method, and R8 pins the coordinates of the other repository.

### Round 2 — TASK revision 2: FAIL

The reviewer read the fingerprint `89a1349775a4`; it had no shell.

Must-fix, all MEDIUM:
- M6: the list of files that a local rule runs left out `render_corpus.py` and
  `selftest_figure_evals.py`, which TC-04 runs up to their guards.
- M7: the closing paragraph of the check restored every tracked file outside the change, the
  run's own records among them.
- M8: the audit record would quote a command picked under a local rule, absolute paths included.

Minor m14 to m20:
- a variable prefix makes another command text;
- options and inputs rather than outputs;
- the stop sentence, and a failed check at stage 3;
- the user's settings excluded without a reason;
- the width of two pinned record lines, the red run of TC-04, and one figurative verb.

The operator answered m17: "Да, и пользовательские" (TASK D16). The rules of the user's
`~/.claude/settings.json` count as those of the local file do.

TASK revision 3 applies them. D16 and D17 are new: D17 keeps the deletions of the staged copies
out of the stage-3 patch.

### Round 3 — TASK revision 3: PASS

The reviewer read the fingerprint `8a1c830e77a1`; it had no shell. Verdict: approved with
comments. No finding was CRITICAL, HIGH or MEDIUM. The LOW findings:
- L1: three coordinates of another repository in R8.1 of the TASK itself had no pin, and the
  living-corpus step of CI checks `docs/*.md`;
- L2: a rule whose command depends on its directory, such as `python3 -m pytest`, also gives one
  command for each directory;
- L3: stage 3 starts the check's process after §4.5, so the two files are read again after the
  gates of stage 3;
- L4: A10 asked for equal listings, where R1.1 makes a difference from other code a finding;
- L5: the failure path of D17 writes back only the removed copies, and only from a file that still
  hashes to its copy;
- L6: of `.git`, the listing takes `config`, `hooks` and `info`;
- L7: `--probe` with a path, and the internal-error line, which the tests reach in the process;
- L8: four wordings, and the user's rule `aa8ebef8166f2dac`, which runs any code with the
  repository's `.venv`.

INFO I1: the user's two git rules, `1906407db7c8843f` and `9b7c28a93551887e`, are the operator's
call, as the §9 rules are.

TASK revision 4 applies L1 to L8 and I1 with no further round, on the precedent of TASK 122. After
it, `check_positional_refs.py --all docs/TASK.md` resolves 14 of 17 references and pins 3, and the
register scan finds no warning.

## Architecture (§2.1)

`docs/ARCHITECTURE.md` §10.7: the bullet of TASK 122 on the escapes of the render check names the
lint and `render_corpus.py` as well, and states the ASCII JSON of the debug command line of
`svg_geometry.py` (TASK R9.7).

## The rules of the settings, read at §2.2 (TASK R1.5)

Read when §2.2 wrote PLAN revision 2. The record quotes no rule (TASK D3).
- `.claude/settings.local.json`: 50 allow rules, SHA-256
  `48bbe25e64356acb4413474d0f1abf0212a13b32346206f44ae76345ca7c5f41`.
- The user's `~/.claude/settings.json`: 326 allow rules, SHA-256
  `1abd385154c514ae50ebbb05e18bc644d68bf0931d0843b344b23c4d59c313e6`.

Four rules run files of the change. The record names each by the first 16 hex digits of the
SHA-256 of its text; none of the four texts holds an absolute path. The scratchpad's
`rules_22.json` holds the SHA-256 of every rule of both files, for J1 to find a new one.
- local `ca2c33383ded254c`: unittest discovery over `tests/`;
- user `fcf7ae83aa61d9ee` and `3c013025af0d911c`: the E2E script of `run-feedback`, run from its
  `tests/` and from its `scripts/` directory;
- user `9fa5cad71668c6f7`: unittest discovery over the `scripts/tests` of the directory it runs in.

The files of the change that their rules run, directly or through other code:
- through the local rule `ca2c33383ded254c`: `tests/test_run_safety_rules.py`,
  `tests/test_python_floor.py` and `tests/test_bare_pytest.py`; the example; `lint_mermaid.py`;
  `render_corpus.py` and `selftest_figure_evals.py` up to their guards; at the base,
  `svg_geometry.py`;
- through the user's rules `fcf7ae83aa61d9ee` and `3c013025af0d911c`:
  `test_ledger_hardening.py` and `test_wi_tail.py`;
- through the user's rule `9fa5cad71668c6f7`, run from the skill's directory: `test_lint_mermaid.py`, after stage 3 `test_printed_output.py`, and through them
  `lint_mermaid.py`, `svg_geometry.py` and `render_check.py`.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: FAIL

The reviewer read the fingerprint `996642e496ed`; it had no shell.

Must-fix, all MEDIUM:
- M1: `stage_driver.py regress` loaded the staged modules in the pytest process only; the child
  of `TestWritesNoFile` imported the base lint, and `GUARD_PRELUDE` stayed empty.
- M2: after a §6.2 re-run, the failure path skipped J3 and its gates.
- M3: `listing.py` left out all of `.git`, where TASK R1.1 lists `config`, `hooks` and `info`.
- M4: the first reading of the settings belongs at §2.2, and J1 could not tell a new rule from a
  hash alone.

Minor m1 to m13:
- three drafts in the scratchpad held text of the TASK or the PLAN, and G3's script had no name;
- `Pending after restore` left out R9.5 and R9.7;
- the put-back steps, a second check after a fix, the directory of the lint runs, and D4's rule on
  the local rule that runs standard input as Python;
- the file modes and a failed `rm` at J2;
- the coverage of the steps that land through the patch, and R9.7;
- a line diff for R4.2, and no import of `render_check.py` by the lint;
- the stub function by name, and one test that passed on the base;
- the R1.1 text as prose before J3, and the files of J3's register check;
- raw characters in the new module and the patch, and `str.splitlines`;
- the records of the run after stage 3, the advisory steps of `run_gates.sh`, and the register.

Notes N1 to N3: the coordinates that §4.5 cannot see before the patch, a clause of J2 that never
applies, and the docstring of `rerender.py`.

PLAN revision 2 applies them. The tools changed with it:
- `stage_driver.py` sets `GUARD_PRELUDE`, and gains `probe` and `svgdiff`;
- `listing.py` lists `config`, `hooks` and `info` of `.git`;
- `gen_stage3_patch.py` splits at newlines only, and refuses a raw character;
- `run_gates.sh` fails the living register scan on a non-zero exit, as CI does.

The scratchpad drafts of the TASK and the PLAN were deleted.

### Round 2 — PLAN revision 2: FAIL

The reviewer read the fingerprint `f8adf8fb1d99`; it had no shell. M1 to M3 were fixed, M4 in part.

Must-fix, MEDIUM:
- F1: J1 stopped only on a file that the first list lacked. Nearly every code file of the change
  is on that list, so a new rule, such as a permanent approval of the eval selftest by its path,
  would pass. The rules are to be compared, not the files.

Minor, LOW and INFO:
- F2: the clause of A9 at §4.5 was not in J1;
- F3: the label of the new tests held no newline;
- F4: the command of G8's pipe and the lines of the span were not named;
- F5: E3 said "in both" of a prelude that only `regress` uses, and the module check was no proof;
- F6: two tools allowed a raw tab, against "no non-printable character but newlines";
- F7: the restore had no check that the new test module is gone;
- F8: bytecode of an earlier run in the scratchpad.

PLAN revision 3 applies them. `rules_check.py` records the SHA-256 of every rule and compares by
rule; the reading of the settings above gains the four rules. The tools changed with it:
- `staging.py scan` pipes the patched workflow through the scanner; the span is lines 111 to 161,
  with no `WARN` in it;
- `stage_driver.py regress` proves by a collection hook which module pytest collected;
- `gen_stage3_patch.py` and `make_inplace.py r7` allow no raw tab;
- the new tests gain a finding whose quoted label holds a newline.

The scratchpad bytecode was deleted, and every Python run passes `-B`.

### Round 3 — PLAN revision 3: PASS

The reviewer read the fingerprint `afb4b4a7f9cc`; it had no shell. Verdict: approved with
comments. No finding was CRITICAL, HIGH or MEDIUM. Both examples of F1 are caught: a permanent
approval of the eval selftest by its path, or of a pytest run of `tests/test_bare_pytest.py`,
adds a rule that the recording lacks.

The LOW findings:
- L1: a new rule that runs only a file of the patch joins neither J1's stop nor J3's check;
- L2: exit 2 of `rules_check.py` had no action, and a changed hook or deny rule showed only as a
  changed file;
- L3: A2 said "the SHA-256" of each rule, where the record holds 16 hex digits of it;
- L4: the collection proof of `regress` printed its result without setting the exit code.

INFO: the `allowed-tools` of plugin commands under `~/.claude/plugins` lie outside the two
readings, which is the operator's call; `rules_22.json` is to be named by its full path.

PLAN revision 4 applies L1 to L4 and the path with no further round, on the precedent of TASK 122.
`rules_check.py` now also hashes each other key of `permissions` and of `hooks`, and names each that
changed. `stage_driver.py regress` exits 3 when the proof is false. The two files still hash to the
reading at §2.2, so the new recording holds the same content.

## Execution (§3)

### A — base check and the rules of the settings

- A1: `HEAD` equals the base. All 34 declared paths pass §3.1: the 25 edited paths are tracked,
  and `git check-ignore` gives exit 1 for each of the 9 created paths.
- A2: `rules_check.py compare` finds both settings files unchanged since the reading at §2.2.

### B — stage 1: the copies

- B1: the four staged code files are byte copies of their base files, as `cmp` shows.
  `stage_driver.py pin base` passes all 6 cases on the copy.

### C — the pin and the workflow text

- C2, red: `pin base` fails `test_step_4_is_the_reviewed_text_to_the_end_of_section_3`, and the
  other 5 cases pass.
- C2, green: `pin patched` passes all 6 cases.
- C2, old pin: `pin old-pin` fails the same case, and the other 5 cases pass.

### D — TC-04

- D1, red: `floor nostub` fails TC-04 at `grade_figures.py`. Its child holds six files of
  `GRADER_PATH`: `evals/fidelity.py`, `evals/stats.py`, `scripts/lint_mermaid.py`,
  `scripts/mermaid_model.py`, `scripts/planarity.py` and `scripts/svg_geometry.py`.
- D2, green: `floor staged` passes all 14 cases of the staged module.

### E — the lint and `svg_geometry.py`

- E1: `staged_printed_output.py` was written from the draft, which was then deleted. It holds no
  raw non-printable character but newlines.
- E1, red: `printed base` fails all 14 tests against the base code:
  - the outputs of the lint hold ESC, U+2028, U+202E and U+009B raw;
  - the base lint has no `_shown` and no `_json_text`, and `main` prints nine times;
  - the debug JSON is not ASCII, and its error line holds ESC raw.
- E2: `svgdiff` shows four changed lines, all in `main`, which spans base lines 2234 to 2270.
  Both staged files parse and hold no raw character.
- E3, green:
  - `printed staged` passes 14 of 14;
  - `probe` shows the child of the GUARD holding `scripts/staged_lint_mermaid.py` and writing
    nothing;
  - `regress` passes 716, with 1 skip, the APFS test known before the task. The collection hook
    prints that the collected `test_lint_mermaid` holds the staged prelude.
  - the staged lint by its own path: `--probe` gives "99/99 rules live", and the references of
    the skill give "0 error / 0 warn / 62 expected", as the base lint does.
- A first `regress` named the directory and the staged file together. pytest dropped the file as
  a duplicate and ran 702 tests. The driver now names each test module, so the 14 new tests run.

### F — the fixtures

- F1: `rerender.py`, from the skill's directory, rendered `references/paired-examples.md` into the
  staged paired fixture: 14 figures, 6 pass and 8 negative as expected, exit 0. The ten other
  references went into the staged references fixture: exit 2 for `ascii.md` and `eval-results.md`,
  which hold no fence, and exit 0 for the eight others.
- F2: `replay.py` of each staged fixture against its base: 14 and 37 figure entries, 0 moved, and
  per file only `instruments` and `generated` differ. Every `instruments` value is
  `7b29e01af879…`, the value of `rerender.py --hash`. Neither file holds a raw character.

### G — edits in place

- G1, red: with TC-ME-49 added, the selftest gives 225 passed and 1 failed of 226; TC-ME-49
  fails against the base write. Green: after `rc.json_text`, 226 of 226 pass.
- G2, red: the two new tests of `tests/test_bare_pytest.py` fail against the base example. An xAI
  key alone led to the import of `openai` and exit 1, and the script stopped at the missing role
  file. Green: 6 of 6 pass after R6.1 and R6.2. The example run as a script loads the role file and
  both skill files, prints "Dry run complete." and exits 0.
- G3: `ast.dump` of each of the four files of R7 equals that of its base text, and none holds a raw
  character. Their suites pass: 106 for the two files of `run-feedback`, 78 for
  `test_task_id_tool.py` and 223 for `test_lint_mermaid.py`.
- G4: no file of R8 changed its line count. `check_positional_refs.py --all docs .` reports 4
  errors, all in the examples of two skills (TASK §9), and none of the 16 of R8.
- G5 to G7: item 6 of `System/Docs/WORKFLOWS.md` from the fence of R1.4; v3.43.0 in both
  changelogs; `System/Docs/SKILLS.md` unchanged.
- G8: the register check found one sentence of 36 words, the English prose of R8.2 in the
  changelog. It became two sentences in the same three lines, and the fence of TASK R8.2 took the
  same text (TASK revision 5). `regcheck.py` now sets apart a warning that the base text holds on
  the same line. Ten such warnings remain, all on table rows of the three records that R8 pins:
  cell width, sentences per cell and one marker. They are findings before the task. No new
  warning remains. `staging.py scan` finds no warning in lines 111 to 161 of the patched workflow.

### H — the patch, the gates and the check

- H1: `gen_stage3_patch.py` wrote the patch: 805 lines, 9 file sections, one of them the new test
  module. The staged copies stay out of it (TASK D17), and it holds no raw character.
  `git apply --check` passes. The SHA-256 values, with `S/` for the skill's directory:
- the patch `docs/reviews/framework-audit-123-stage3.diff`: `71399c1f8218163380ae0170dedd72daadfcf8436341317836926cf10ab40c15`;
- staged copy `S/scripts/staged_lint_mermaid.py`: `2ea626f012c577b2b3b752dbe0d82c346546d75d89dfec5660f98d7cb1462a79`;
- staged copy `S/scripts/staged_svg_geometry.py`: `b7f77dc99b77b5a3197297d640163ab5a6f30475e0f9e3582b503158329b4b5c`;
- staged copy `S/scripts/tests/fixtures/staged_paired-examples-geometry.json`: `4f5c8b92c093cddf1f00e87aa328b818a74db5dfdaf01705ccbfce02e2f6d1cb`;
- staged copy `S/scripts/tests/fixtures/staged_references-geometry.json`: `be27c4999b0d48491dbb9a14d4a7b6ab4b46028c5a0b89cac3ad9d4421b83708`;
- staged copy `S/scripts/tests/staged_printed_output.py`: `36a8cb6d4b5f998c0af62f3173c54541d2374e4cfeaa156c30d8b2e6992a20a7`;
- staged copy `tests/staged_python_floor.py`: `41015332645c53626bc6454ed2134b0ce1d8d07321f091888ca5e798ab96cf75`;
- staged copy `tests/staged_run_safety_rules.py`: `3f44798b91235d938fba1dd36899dd7b2837b13f8fd25e6e77a179527cb735ba`;
- after the patch, `S/scripts/lint_mermaid.py`: `2ea626f012c577b2b3b752dbe0d82c346546d75d89dfec5660f98d7cb1462a79`;
- after the patch, `S/scripts/render_check.py`: `5c61658e2d1a3d2899c7631da2c3480555bb248fd8f038c165ef500cfcf1bbb9`;
- after the patch, `S/scripts/svg_geometry.py`: `b7f77dc99b77b5a3197297d640163ab5a6f30475e0f9e3582b503158329b4b5c`;
- after the patch, `S/scripts/tests/fixtures/paired-examples-geometry.json`: `4f5c8b92c093cddf1f00e87aa328b818a74db5dfdaf01705ccbfce02e2f6d1cb`;
- after the patch, `S/scripts/tests/fixtures/references-geometry.json`: `be27c4999b0d48491dbb9a14d4a7b6ab4b46028c5a0b89cac3ad9d4421b83708`;
- after the patch, `S/scripts/tests/test_printed_output.py`: `36a8cb6d4b5f998c0af62f3173c54541d2374e4cfeaa156c30d8b2e6992a20a7`;
- after the patch, `.agent/workflows/framework-upgrade.md`: `02bc1ca934a81b95c0f32c7410fe1d70e42f0002b2e7d10ada653c7a4e67f5c9`;
- after the patch, `tests/test_python_floor.py`: `41015332645c53626bc6454ed2134b0ce1d8d07321f091888ca5e798ab96cf75`;
- after the patch, `tests/test_run_safety_rules.py`: `3f44798b91235d938fba1dd36899dd7b2837b13f8fd25e6e77a179527cb735ba`;
- H2: `run_gates.sh` first failed one step: `test_skill_refs` of the curated suite found two skill
  names of the example quoted in Problem 6 of the TASK, which resolve to nothing. The TASK names
  them now without the prefix (revision 5). On the rerun all 18 steps pass. Every one of the 30
  paths of `git status` is declared.
- H3: `listing.py --show-git` lists 16 paths of `.git`: `config`, 14 files of `hooks` and 2 of
  `info`. Each command below ran once between two listings of 3689 files, with exit 0 and equal
  listings:
  - `python3 -m pytest`, from the root, `S/`, `.agent/skills/run-feedback` and `.agent/tools`;
  - `python3 tests/run_tests.py` and `python3 -m unittest discover -s tests -v`, from the root;
  - `python3 -m unittest discover -s scripts/tests`, from `S/`;
  - `bash -x tests/test_e2e.sh`, from `.agent/skills/run-feedback/scripts`.

## Stage 2 — reviews

### Round 1, at the fingerprint `8cf1bd40dd4e`: both PASS

**Code review: PASS.** The reviewer applied the patch in a throwaway worktree outside the
repository and removed it. On the patched tree: the skill's suite 716 passed with the known skip,
`tests/run_tests.py` 610, the eval selftest 226 of 226, and all 18 CI steps. Its findings:
- R1-1, LOW: no test depended on the escape of each line of the inventory; a path with a newline
  could forge a line there if that escape went;
- R1-4, LOW: the changelogs stated a wider stop rule than the workflow;
- R1-5, LOW: the headline of the lint's entry claimed more than its outputs, since argparse's own
  messages stay raw;
- INFO:
  - R1-2: the AST check missed a `print` outside a function and a direct write to `sys.stdout`;
  - R1-3: the first error line of `svg_geometry.py` is untested, and its message is a repr already;
  - R1-6: the docstring of `tests/test_bare_pytest.py`;
  - R1-7: the reviewer's brief quoted a wrong hash for the staged pin; this record holds the right
    one.

**Security audit: PASS**, `scan_status: findings`. The scan ran in full (`not_run` empty). It hit no
line of the change: three lines of `tests/staged_python_floor.py` repeat lines of the base file.
A fuzz of 600 hostile documents through the four outputs of the lint gave no raw character. Its
findings, all LOW:
- S1-1: the check left out `.git/commondir`, through which `git status` runs another
  repository's `core.fsmonitor`, and missed refs, the stash and the flags of the index;
- S1-2: managed settings, plugins and the Auto mode classifier were not named;
- S1-3: the put-back's `git restore` took a path as a pattern, left the index, and did not check
  the restored hash; item 6 claimed more than the run does;
- S1-4: the check misses a child that writes after the second listing, code that acts otherwise
  under its two variables, and writes outside the tree, the user's `~/.gitconfig` among them;
- S1-5: the records quoted rules of the local and the user's settings;
- S1-6: the run's tools: bytecode in the driver, raw paths and no timeout in `listing.py`.

Before the task, per the reviewers: `render_corpus.py` prints run paths and reasons raw (LOW); the
example sends `OPENAI_API_KEY` to whatever `OPENAI_BASE_URL` names (LOW, D10); WI-41 (LOW); the
scanner's 28 critical and 9 high hits are the base tree's. No CRITICAL or HIGH finding predates
the task. The ignored `tests/.scratch/` that the security auditor saw go was swept by
`tests/conftest.py` during the code reviewer's collection run.

### Fix round 1 (TASK D18)

TASK revision 6 and PLAN revision 5 apply the LOW findings of both reviews; R1-3 stays as stated.
- The R1.1 fence: the listing of `.git` and the user's two files, the put-back, and the sources
  outside the count; the staged pin took its step 4 again. Item 6 of `WORKFLOWS.md` follows R1.4.
- The records name each rule by its class and the first 16 hex digits of its hash.
- The changelogs: the stop rule of the workflow, and argparse as the lint's residual.
- `staged_printed_output.py`: a test of the inventory of a path with a newline, and an AST check
  of every call; `tests/test_bare_pytest.py` names TASK 123 in its docstring.
- The tools: `listing.py` lists the new scope, escapes paths and has a timeout; `stage_driver.py`
  writes no bytecode; `rules_check.py` hashes every top-level key. The settings still hash to the
  reading at §2.2, so the new recording holds the same content.

Evidence:
- the pin: `base` and `old-pin` fail the step-4 case, `patched` passes 6 of 6;
- `printed base` fails 15 of 15, the new test among them; `printed staged` passes 15 of 15;
- `regress` passes 717 with the known skip, and the collection hook prints True;
- the register check finds no new warning; the R1.1 span is lines 111 to 166 of the patched
  workflow, with no warning;
- the patch: 836 lines, `git apply --check` passes;
- `run_gates.sh`: 18 of 18; every one of the 30 paths of `git status` is declared;
- the check of R1.1 with the new listing, which holds 41 paths of `.git` and five views: every
  command of H3 left equal listings.

The SHA-256 values for round 2, with `S/` for the skill's directory:
- the patch `docs/reviews/framework-audit-123-stage3.diff`: `adc54fdfb1e5549b6650f50e26162b463368d7e9edaad9aa8333548f31b8c545`;
- staged copy `S/scripts/staged_lint_mermaid.py`: `2ea626f012c577b2b3b752dbe0d82c346546d75d89dfec5660f98d7cb1462a79`;
- staged copy `S/scripts/staged_svg_geometry.py`: `b7f77dc99b77b5a3197297d640163ab5a6f30475e0f9e3582b503158329b4b5c`;
- staged copy `S/scripts/tests/fixtures/staged_paired-examples-geometry.json`: `4f5c8b92c093cddf1f00e87aa328b818a74db5dfdaf01705ccbfce02e2f6d1cb`;
- staged copy `S/scripts/tests/fixtures/staged_references-geometry.json`: `be27c4999b0d48491dbb9a14d4a7b6ab4b46028c5a0b89cac3ad9d4421b83708`;
- staged copy `S/scripts/tests/staged_printed_output.py`: `d83c1dcfaab7084377585853ee54eb03ec518de8769cebce4ed78ccf4aa9fb23`;
- staged copy `tests/staged_python_floor.py`: `41015332645c53626bc6454ed2134b0ce1d8d07321f091888ca5e798ab96cf75`;
- staged copy `tests/staged_run_safety_rules.py`: `d85aa34651813d8b7cfdadad3daa41c9fc39236a0938495ce61871bd1faa383d`;
- after the patch, `S/scripts/lint_mermaid.py`: `2ea626f012c577b2b3b752dbe0d82c346546d75d89dfec5660f98d7cb1462a79`;
- after the patch, `S/scripts/render_check.py`: `5c61658e2d1a3d2899c7631da2c3480555bb248fd8f038c165ef500cfcf1bbb9`;
- after the patch, `S/scripts/svg_geometry.py`: `b7f77dc99b77b5a3197297d640163ab5a6f30475e0f9e3582b503158329b4b5c`;
- after the patch, `S/scripts/tests/fixtures/paired-examples-geometry.json`: `4f5c8b92c093cddf1f00e87aa328b818a74db5dfdaf01705ccbfce02e2f6d1cb`;
- after the patch, `S/scripts/tests/fixtures/references-geometry.json`: `be27c4999b0d48491dbb9a14d4a7b6ab4b46028c5a0b89cac3ad9d4421b83708`;
- after the patch, `S/scripts/tests/test_printed_output.py`: `d83c1dcfaab7084377585853ee54eb03ec518de8769cebce4ed78ccf4aa9fb23`;
- after the patch, `.agent/workflows/framework-upgrade.md`: `9bbee9124235844ad3e3653e0301800868ad2c699686338e989fb9e702f35ca1`;
- after the patch, `tests/test_python_floor.py`: `41015332645c53626bc6454ed2134b0ce1d8d07321f091888ca5e798ab96cf75`;
- after the patch, `tests/test_run_safety_rules.py`: `d85aa34651813d8b7cfdadad3daa41c9fc39236a0938495ce61871bd1faa383d`;

### Round 2, at the fingerprint `84565c6ea168`: code review FAIL, security audit PASS

Both agents quoted the fingerprint at their start and end, and it held. Neither wrote in the
repository.

**Code review: FAIL (REJECTED).** The reviewer applied the patch in a throwaway worktree outside the
repository, and removed it. Its findings:
- R2-1, HIGH: the view `git stash list`, which D18 added, matches `UNNAMED_PATH_COMMAND` of
  `tests/test_git_rollback_contract.py` outside the sentences that the test allows. On the patched
  tree `tests/run_tests.py` passed 609 of 610 and `run_gates.sh` 17 of 18. Fix round 1 had run H2
  on the unpatched tree, which does not hold the new text;
- R2-2, LOW: two lines of the Mode A round 3 summary quoted three rules of the user's settings;
- R2-3, LOW: the changelogs stated a narrower stop rule than R1.1, and with item 6 a wider
  put-back;
- R2-4, LOW: the put-back treated `.git` as it treats the tree. It could remove a `refs/stash` that
  the command created, and its `git restore` ran a `core.fsmonitor` that the command planted;
- R2-5, LOW: the listing held files only. An empty directory under `tests/.scratch/` appeared during
  the H3 check of fix round 1. `session_scratch()` of `tests/_scratch.py` creates it, and only the
  end-of-session hook of the pytest conftest removes it. So the "equal listings" of H3 and of fix
  round 1 could not show it. The directory itself comes from other code, a finding before the task;
- R2-6, LOW: the PLAN cited revision 4 of the TASK;
- INFO: R2-7, git reads `~/.config/git/config` as it reads `~/.gitconfig`; R2-8, an alias of
  `print` passes the AST check, which a syntactic check cannot see, and needs no action.

It verified the hashes, the three pin modes, and the fixes of R1-1, R1-2, R1-5, R1-6 and S1-1 to
S1-6. On the patched tree the skill's suite passed 717 with the known skip, the eval selftest 226
of 226, and the lint commands of R9.6 printed no raw character.

**Security audit: PASS**, `scan_status: findings`. The scan ran in full, with the counts of round 1.
Every hit on a changed file repeats a base line, and gitleaks finds no leak in the change. A fuzz of
700 hostile documents through the four outputs of the lint, with 80 error lines and 480 runs of the
command line of `svg_geometry.py`, gave no raw character. Its findings, all LOW:
- S2-1: the check's own `git ls-files` and the put-back's `git restore` run a `core.fsmonitor` that
  the checked command planted, directly or through a created `commondir`;
- S2-2: the quotes of R2-2;
- S2-3: a FIFO under `.git` blocked the listing, which then failed closed;
- S2-4: item 6 claimed that the run puts back what git holds;
- INFO: `~/.claude.json`, `~/.claude/agents` and `~/.claude/skills` are further files of the user
  through which a later session runs code.

Before the task, per the security audit: the fingerprint formula and the `git status` of §5 step 1
also run a planted `core.fsmonitor` (LOW); `OPENAI_API_KEY` goes to whatever server
`OPENAI_BASE_URL` names (LOW, D10); WI-41 (LOW). No CRITICAL or HIGH finding predates the task.

### Fix round 2 (TASK D19)

TASK revision 7 and PLAN revision 6 apply every finding of round 2 but R2-8.
- The R1.1 fence: of `logs` the listing takes `refs/stash`, in place of the view. It lists each
  directory, hashes regular files only, and lists `~/.config/git/config` too. Each git command of
  the check and of the put-back runs with `-c core.fsmonitor=false`. A difference under `.git` or in
  a file of the user, or a file that the second listing lacks, stops the run before any further git
  command. The put-back removes each directory that the command created. The staged pin took its
  step 4 again.
- Item 6 and both changelogs state the put-back as step 4 does, and the changelogs its stop rule.
- The Mode A round 3 summary of this record names the user's rules by class and hash.
- PLAN H4 runs the gates on the patched tree, in a throwaway worktree.
- The tools: `listing.py` lists the new scope, runs git with the monitor off, and opens no FIFO.

Evidence:
- the pin: `base` and `old-pin` fail the step-4 case, `patched` passes 6 of 6. The staged code and
  the other staged tests are unchanged since round 2;
- the register check finds no new warning. The R1.1 span is lines 111 to 172 of the patched
  workflow, with no warning;
- H1: the patch, 848 lines; `git apply --check` passes, and it holds no raw character;
- H2: `run_gates.sh` on the unpatched tree, 18 of 18. Every one of the 30 paths of `git status` is
  declared;
- H4: the worktree `patched/` under the scratchpad, at the base, took the tracked changes, the four
  declared files that git does not track, and the patch. There `run_gates.sh` passed 18 of 18:
  `tests/run_tests.py` ran 610 tests, `test_git_rollback_contract` among them, and the skill's suite
  passed 717 with the known skip. `git worktree remove --force` removed the worktree, and
  `git worktree list` names no `patched/`;
- H3: `listing.py --show-git` lists 58 entries of `.git`, among them `config`, `hooks`, `info`,
  `refs`, `packed-refs` and the entries of `worktrees`, and five views. Each command ran once
  between two listings and exited 0. Checks 1 to 6 began at 4599 entries, files and directories
  together. Check 6 added two directories, and checks 7 and 8 ran with them present, at 4601
  entries: the put-back came after check 8, not after check 6 as R1.1 has it (R3-1):
  - `python3 -m pytest` from the root, `S/`, `.agent/skills/run-feedback` and `.agent/tools`,
    `python3 tests/run_tests.py` from the root, `python3 -m unittest discover -s scripts/tests`
    from `S/`, and `bash -x tests/test_e2e.sh` from `.agent/skills/run-feedback/scripts`: equal
    listings;
  - `python3 -m unittest discover -s tests -v`, from the root: two directories added,
    `tests/.scratch/` and an empty session directory in it. `session_scratch()` of
    `tests/_scratch.py` creates both, and only the end-of-session hook of the pytest conftest
    removes them; no file of the change imports that module. It is a finding before the task
    (R2-5). The put-back removed both with `rmdir`, the inner one first, and `git status` still
    shows the 30 declared paths.

The SHA-256 values for round 3, with `S/` for the skill's directory:
- the patch `docs/reviews/framework-audit-123-stage3.diff`: `36465221d6f3aec944010714526a2b96dd646e9e1867ddd98782681eaf36daac`;
- staged copy `S/scripts/staged_lint_mermaid.py`: `2ea626f012c577b2b3b752dbe0d82c346546d75d89dfec5660f98d7cb1462a79`;
- staged copy `S/scripts/staged_svg_geometry.py`: `b7f77dc99b77b5a3197297d640163ab5a6f30475e0f9e3582b503158329b4b5c`;
- staged copy `S/scripts/tests/fixtures/staged_paired-examples-geometry.json`: `4f5c8b92c093cddf1f00e87aa328b818a74db5dfdaf01705ccbfce02e2f6d1cb`;
- staged copy `S/scripts/tests/fixtures/staged_references-geometry.json`: `be27c4999b0d48491dbb9a14d4a7b6ab4b46028c5a0b89cac3ad9d4421b83708`;
- staged copy `S/scripts/tests/staged_printed_output.py`: `d83c1dcfaab7084377585853ee54eb03ec518de8769cebce4ed78ccf4aa9fb23`;
- staged copy `tests/staged_python_floor.py`: `41015332645c53626bc6454ed2134b0ce1d8d07321f091888ca5e798ab96cf75`;
- staged copy `tests/staged_run_safety_rules.py`: `67529f4c7a03e6c82e77841c9dd64f28e91b8f3564ae5e1c34f0ee20a9c7ace8`;
- after the patch, `S/scripts/lint_mermaid.py`: `2ea626f012c577b2b3b752dbe0d82c346546d75d89dfec5660f98d7cb1462a79`;
- after the patch, `S/scripts/render_check.py`: `5c61658e2d1a3d2899c7631da2c3480555bb248fd8f038c165ef500cfcf1bbb9`;
- after the patch, `S/scripts/svg_geometry.py`: `b7f77dc99b77b5a3197297d640163ab5a6f30475e0f9e3582b503158329b4b5c`;
- after the patch, `S/scripts/tests/fixtures/paired-examples-geometry.json`: `4f5c8b92c093cddf1f00e87aa328b818a74db5dfdaf01705ccbfce02e2f6d1cb`;
- after the patch, `S/scripts/tests/fixtures/references-geometry.json`: `be27c4999b0d48491dbb9a14d4a7b6ab4b46028c5a0b89cac3ad9d4421b83708`;
- after the patch, `S/scripts/tests/test_printed_output.py`: `d83c1dcfaab7084377585853ee54eb03ec518de8769cebce4ed78ccf4aa9fb23`;
- after the patch, `.agent/workflows/framework-upgrade.md`: `fbd920dcee156335384724b570b5f367ecf900725088962acdc7956f7365c46e`;
- after the patch, `tests/test_python_floor.py`: `41015332645c53626bc6454ed2134b0ce1d8d07321f091888ca5e798ab96cf75`;
- after the patch, `tests/test_run_safety_rules.py`: `67529f4c7a03e6c82e77841c9dd64f28e91b8f3564ae5e1c34f0ee20a9c7ace8`;

### Round 3, at the fingerprint `387c650a2da8`: both PASS

Both agents, resumed, quoted the fingerprint at their start and end, and it held. Neither wrote in
the repository.

**Code review: PASS (APPROVED).** The reviewer replayed stage 3 in a throwaway worktree, whose copy
fingerprinted `387c650a2da8`. All 17 hashes of the round-3 list matched. There
`test_git_rollback_contract` passed, `tests/run_tests.py` ran 610 tests, `run_gates.sh` passed 18 of
18, and the skill's suite 717 with the known skip. R2-1 to R2-7 are fixed. A planted monitor ran 0
times under `-c core.fsmonitor=false`, and 2 times without it. Its findings, each a LOW route of a
class that an earlier round fixed:
- R3-1: checks 7 and 8 of H3 ran with the two directories of check 6 present, and `h3.sh` runs
  every check whatever the one before found;
- R3-2: `listing.py` lists a user file that is a link by its target, and R1.1 does not say how it
  lists such a file;
- R3-3: D4 still said that the run puts back what git holds;
- INFO: R3-4, the restore command of R1.1 omits `-c core.fsmonitor=false`, which the sentence before
  it requires; R3-5, §9 named a git configuration under `$XDG_CONFIG_HOME`, which is
  `~/.config/git/config` while that variable is unset.

**Security audit: PASS**, `scan_status: findings`. The scan gave the counts of rounds 1 and 2, and
every hit on a changed file repeats a base line; gitleaks finds no leak in the change. S2-1 to S2-4
are closed: through the new `listing.py`, a monitor planted in `.git/config` or through a created
`commondir` did not run, and both differences stop the run. A FIFO under `.git` is listed, and the
listing ends. A check over all 376 local and user rules found no rule text in the records of the
run. Its findings, each a LOW route of a class that an earlier round fixed:
- S3-1: a created file can hold the only copy of a changed file, after a copy and an overwrite, and
  the put-back removes it;
- S3-2: `listing.py` keyed a created link to a directory as a directory, and `rmdir` of that key,
  with its trailing slash, removes the link's empty target;
- S3-3: `h3.sh` does not stop between checks, so a later command can run git after a difference
  under `.git`;
- INFO: I-1, the flag of R3-4; I-2, R1.1 does not say that a failed hash check after the restore
  stops the run; I-3, the user files of R3-2.

Before the task, per both reviews: the empty directories that `tests/_scratch.py` leaves (R2-5);
the fingerprint formula runs a planted monitor; D10; WI-41. All LOW, and no CRITICAL or HIGH
finding predates the task.

**Review verdict:** passed at round 3 of 3.

### After round 3 (TASK D20)

Every finding of round 3 is a LOW route of a class that an earlier round fixed, so the run asked the
operator, as `framework-upgrade` §3 step 4 states. Answer "Остаток + backlog": the routes in the
text of R1.1 stay residuals in §9 of the TASK, and WI-54 holds them (S3-1, S3-2, R3-2, R3-4 and
I-2). No fourth round runs.

The run fixed the findings in its own records and tools, and no file of the patch:
- TASK revision 8 adds D20, the residuals of §9, and the wording of D4 and §9 (R3-3, R3-5);
- PLAN revision 7 adds I2, and the check of H3 and J3 stops at the first listing that differs;
- `docs/backlog/wi-54-residual-routes-of-the-task-123-put-back.md` and its line in
  `docs/BACKLOG.md`, both declared. `docs/BACKLOG.md` is tracked, the new record is not ignored, and
  both paths pass the checks of §3.1;
- this record states how H3 ran (R3-1);
- `h3.sh` stops at the first listing that differs, and takes the command to start from (R3-1,
  S3-3). `listing.py` keys a link without a trailing separator, prints the kind of each
  difference, and hashes what a user file holds through a link (S3-2, I-3). In a sandbox, one
  command made a link, a directory, a backup, an overwrite and a FIFO under `.git`. The listing
  printed each with its kind, and ended.

The patch and the staged copies keep the SHA-256 values of round 3.

## §4.5 and the settings (J1)

- `check_positional_refs.py --targets-changed`: 0 errors, and 75 warnings over 796 references:
  72 `DRIFT_SUSPECT`, a coordinate into a file that this change edits, and three `ESCAPES_ROOT`.
  Of the 72, 47 cite a line above the first change of their file. The other 25 cite:
  - lines that R8 edited in place, with no line added or removed;
  - the empty `docs/TASK.md` slot of §9;
  - line 394 of `test_task_id_tool.py`, which the escape of R7 at line 301 does not move;
  - lines of the changelogs, four coordinates of two old records; every entry moves those lines.

  No coordinate of the living corpus cites a line of the workflow past line 108, so the patch
  moves none. A9 holds: no error lies in a line that R8 names.
- `--targets-changed --fix`: exit 0, and nothing repaired. The fingerprint `a5de41027cdc` held
  before and after, so the run touched no file.
- `rules_check.py compare`: the local file and the user's are unchanged since the reading at §2.2;
  no rule is new.

## Stage 3 (J2)

Step 1: the patch and the seven staged copies hash to the values of round 3. Step 2, the values
that stage 3 and its failure path check, with `S/` for the skill's directory:
- the patch `docs/reviews/framework-audit-123-stage3.diff`: `36465221d6f3aec944010714526a2b96dd646e9e1867ddd98782681eaf36daac`, 848 lines;
- staged copy `S/scripts/staged_lint_mermaid.py`: `2ea626f012c577b2b3b752dbe0d82c346546d75d89dfec5660f98d7cb1462a79`;
- staged copy `S/scripts/staged_svg_geometry.py`: `b7f77dc99b77b5a3197297d640163ab5a6f30475e0f9e3582b503158329b4b5c`;
- staged copy `S/scripts/tests/fixtures/staged_paired-examples-geometry.json`: `4f5c8b92c093cddf1f00e87aa328b818a74db5dfdaf01705ccbfce02e2f6d1cb`;
- staged copy `S/scripts/tests/fixtures/staged_references-geometry.json`: `be27c4999b0d48491dbb9a14d4a7b6ab4b46028c5a0b89cac3ad9d4421b83708`;
- staged copy `S/scripts/tests/staged_printed_output.py`: `d83c1dcfaab7084377585853ee54eb03ec518de8769cebce4ed78ccf4aa9fb23`;
- staged copy `tests/staged_python_floor.py`: `41015332645c53626bc6454ed2134b0ce1d8d07321f091888ca5e798ab96cf75`;
- staged copy `tests/staged_run_safety_rules.py`: `67529f4c7a03e6c82e77841c9dd64f28e91b8f3564ae5e1c34f0ee20a9c7ace8`;
- before the patch, `S/scripts/lint_mermaid.py`: mode `100644`, `c40c0a10152a1558f8a91190c8ae5b8b34497d1528a7a26733ff07aefb830cbd`;
- before the patch, `S/scripts/render_check.py`: mode `100644`, `d3e40e1a173616c70752f6d21eda52401a12f42ad633d8621e5e168bbf322a37`;
- before the patch, `S/scripts/svg_geometry.py`: mode `100644`, `56505d9dcaaba2cd31c9da061d2a51be53ba190f54a83593e5df856123cafad0`;
- before the patch, `S/scripts/tests/fixtures/paired-examples-geometry.json`: mode `100644`, `10ffee8fd55d256b01e8c0e7870dbd8354d1ffd77a27d5e7ff4c71efe93e4f4b`;
- before the patch, `S/scripts/tests/fixtures/references-geometry.json`: mode `100644`, `dad79e21c6d74f66d2589b0219b54c164a1859e276c7380523febd81acfac37f`;
- before the patch, `S/scripts/tests/test_printed_output.py`: absent;
- before the patch, `.agent/workflows/framework-upgrade.md`: mode `100644`, `2e263ae8a8f137c9297fcabb9cd077a78681fa6a0cc0625c35060359bda32bcc`;
- before the patch, `tests/test_python_floor.py`: mode `100644`, `d4c32a75d17658b75a7d4a9d0d80eea9079c4ba8fa16954bda0ac5eeadff9791`;
- before the patch, `tests/test_run_safety_rules.py`: mode `100644`, `a258ee29a22891ba726e03cb301d872ed5f2e7dfb62a5a16173cda994c493064`;

The patch:

~~~~diff
diff --git a/tests/test_run_safety_rules.py b/tests/test_run_safety_rules.py
--- a/tests/test_run_safety_rules.py
+++ b/tests/test_run_safety_rules.py
@@ -5,8 +5,9 @@
 stopped, and the operator deferred the hook to WI-34. This file pins the rules whole:
 
 * `framework-upgrade` §3 step 4, whole and up to the end of §3: what takes effect at once, the
-  scripts that allow rules run, the test-module exemption, the four stages, the failure branch;
-  and §3.1's fixture exception (``TC-1``);
+  allow rules of every settings file and the scripts they run, the test-module exemption, the
+  check of what a change runs (TASK 123), the four stages, the failure branch; and §3.1's
+  fixture exception (``TC-1``);
 * `security-audit` §6.2, whole: the three verdicts, one re-run per part, the operator's decision,
   no unverified control, tests are not the hunt (``TC-2``);
 * each place that routes an audit, as the whole paragraph, list item or table row that holds its
@@ -39,18 +40,68 @@
    change that alters what runs, or what runs without a prompt. The list is not exhaustive:
    - a hook in a settings file, or in the frontmatter of an agent or a skill;
    - the script of a registered hook, code that script calls, and a new module it would import;
-   - a script that a committed allow rule names, code that script calls, and a new module it
-     would import;
+   - a script that an allow rule names, code that script calls, and a new module it would import;
    - a permission rule, `additionalDirectories` or the permission mode, an agent's
      `permissionMode` and the `allowed-tools` of a skill or a command among them;
    - a settings key that names a command, such as `statusLine`, or sets a command's environment,
      `env`;
    - the MCP servers of `.mcp.json` or a settings file, and `enableAllProjectMcpServers`.
 
+   The allow rules are those of `.claude/settings.json`, `.claude/settings.local.json` and the
+   user's `~/.claude/settings.json`, and the `allowed-tools` of a skill or a command. A command that
+   one of them approves is an allowed command, and a rule names a file also through a symbolic link
+   that resolves to it. Rules that managed settings or plugins add, and the commands that the Auto
+   mode classifier approves, lie outside this count; the operator answers for them. Git holds
+   neither the local file nor the user's, and Claude Code adds a rule to one of them when the
+   operator approves a command permanently. The run reads both when §2.2 writes the PLAN, again at
+   §4.5, and again after the gates of stage 3. A rule added since the first reading that runs a
+   file the change adds or edits in place, directly or through other code, stops the run for the
+   operator. The audit record names each file of the change that a rule of either file runs,
+   directly or through other code, and quotes no such rule.
+
    Test modules and fixtures that no rule names by path are exempt, and so is code that runs
-   without a prompt only through them. A test module is a `test_*.py` or `conftest.py` file that no
-   hook or listed script runs or imports; a fixture is a data file that a test reads.
+   without a prompt only through them. A rule that names a directory, such as `discover -s tests`,
+   names no module in it. A test module is a `test_*.py` or `conftest.py` file that no hook or
+   listed script runs or imports; a fixture is a data file that a test reads.
    `tests/run_tests.py` is named by a rule and is not exempt.
+
+   **What the change runs.** The run checks what code of the change writes when an allowed command
+   runs it. That code is what the change adds or edits, test modules among them. It is also what an
+   allowed command first reaches through the change, such as a test that a collection error had
+   blocked. A rule with a wildcard, or one whose command runs other code from another directory,
+   gives one command for each option, input or directory that reaches code the change adds or
+   edits. For each command, one process lists every file and directory under the repository root,
+   each regular file with its SHA-256, ignored files included and no link followed. Of `.git` it
+   lists every file but `index` and those under `objects` and `logs`, and of `logs` it lists
+   `refs/stash`, which holds every stash. It adds the output of `git rev-parse HEAD` and
+   `git ls-files -s -v`, and lists the user's `~/.gitconfig`, `~/.config/git/config` and
+   `~/.claude/settings.json`. Each git command of the check and of the put-back runs with
+   `-c core.fsmonitor=false`, so that git runs no file-system monitor that the checked command
+   configured. The process then runs the command as the rule approves it, with
+   `PYTHONDONTWRITEBYTECODE=1` and `PYTEST_ADDOPTS=-p no:cacheprovider` in its environment, and
+   lists again. The audit record names the code that wrote each difference, read from that code or
+   from the command's output.
+   - A difference that the command is meant to write, such as the state that `update_state.py`
+     records, passes the check.
+   - Any other difference that code of the change writes fails the check. Before the change lands,
+     that code writes into a temporary directory, which it removes.
+   - A difference that other code writes is a finding before the task.
+
+   After the check, the run puts back each difference that the command was not meant to write. A
+   difference under `.git` or in a file of the user, or a file of the first listing that the second
+   lacks, stops the run. The run names each difference to the operator and runs no further git
+   command. Otherwise:
+   - it removes each file that the command created, and then each directory that it created;
+   - it restores a tracked file that no kind of §5 step 1 declares, with
+     `git restore --source=<base> --staged --worktree -- ':(literal)<path>'`, and checks that the
+     file hashes as in the first listing;
+   - it records a changed session state again through `update_state.py`;
+   - it names every other difference to the operator, the run's own records among them.
+
+   The check runs with the gates of §3.3, and for the code of stage 3 with the gates of stage 3,
+   where a failed check is a failed gate. The audit record holds each command, with its paths
+   relative to the repository root, and its result. TASK 122 unblocked the bare pytest run, and a
+   test it reached rewrote the live session state.
 
    A change that only narrows what runs without a prompt, such as a removed allow rule, may land
    at once: it runs nothing new, and at worst a command asks. Before the edit, a check shows that
diff --git a/tests/test_python_floor.py b/tests/test_python_floor.py
--- a/tests/test_python_floor.py
+++ b/tests/test_python_floor.py
@@ -19,7 +19,9 @@
   it runs, such as ``dataclass(slots=True)`` in an imported module, is out of its reach;
 * each guarded script and the grader, run under a faked 3.9.6 in an empty directory, exit 2, name
   the script that was run and both versions, and write nothing, in that directory or in the
-  skills; the preflight reports FAIL and names both versions (``TC-04``);
+  skills; the grader runs with a stub for each local module it imports before ``run_evals``, and
+  holds none of their files at its exit; the preflight reports FAIL and names both versions
+  (``TC-04``);
 * the installer, given a ``python3`` that reports 3.9.6, exits 2 and names both versions
   (``TC-05``);
 * no living document or script claims support for Python 3.10 or older (``TC-06``);
@@ -30,6 +32,12 @@
 ``grade_figures.py``, and the eval selftest re-derives each report from its corpus (TC-ME-22), so an
 edit to the grader would turn every stored report stale. It imports ``run_evals`` at its top,
 before it reads an argument or writes a file, and that guard stops it (TASK D6).
+
+TC-04 stubs the local modules that the grader imports before ``run_evals``, so the allowed runs
+of this file execute none of their bodies (TASK 123 R2). Under the fake those bodies would run on
+the current interpreter and prove nothing about 3.9, and TC-03 parses them. The residual: TC-04
+no longer checks them for a write at import, which a real 3.9 would run before the guard. None
+of them writes or reads ``sys.version_info`` today.
 
 ``TC-06`` is a tripwire for the known spellings of a claim, not a parser of intent.
 """
@@ -201,10 +209,49 @@
     return state
 
 
-def _run_under_old(path, cwd):
-    code = f"{FAKE_VERSION}; import runpy; runpy.run_path({str(path)!r}, run_name='__main__')"
+def _run_under_old(path, cwd, prelude=""):
+    """*path* run as `__main__` under the faked 3.9.6, after the child code *prelude*."""
+    code = (f"{FAKE_VERSION}\n{prelude}import runpy\n"
+            f"runpy.run_path({str(path)!r}, run_name='__main__')\n")
     return subprocess.run([sys.executable, "-B", "-c", code], cwd=cwd, capture_output=True,
                           text=True, timeout=120)
+
+
+#: What the grader's child writes at its exit: the files of `GRADER_PATH` that `sys.modules`
+#: holds then, the grader aside (TASK 123 R2.2).
+LOADED = "held from GRADER_PATH: "
+
+
+def _grader_local_imports():
+    """The modules that the grader imports at module level before `run_evals`, from a directory of
+    `GRADER_PATH`, found in its source as TC-03 finds them. TC-04 stubs each one (TASK 123 R2.1)."""
+    tree = ast.parse(GRADER.read_text(encoding="utf-8"))
+    names = []
+    for node in tree.body:
+        if isinstance(node, ast.Import):
+            if any(a.name == GRADER_GUARD for a in node.names):
+                break
+            names.extend(_top(a.name) for a in node.names)
+        elif isinstance(node, ast.ImportFrom) and node.level == 0:
+            names.append(_top(node.module))
+    return tuple(n for n in dict.fromkeys(names)
+                 if any((d / f"{n}.py").is_file() for d in GRADER_PATH))
+
+
+def _stubs_and_report(stubs):
+    """Child code: an empty module in `sys.modules` for each name of *stubs*, and a report at exit
+    of each module whose file lies in a directory of `GRADER_PATH`, the grader aside."""
+    dirs = tuple(str(d) + os.sep for d in GRADER_PATH)
+    return ("import atexit, types\n"
+            f"for _name in {tuple(stubs)!r}:\n"
+            "    sys.modules[_name] = types.ModuleType(_name)\n"
+            "def _report():\n"
+            "    held = sorted(m.__file__ for m in list(sys.modules.values())\n"
+            "                  if isinstance(getattr(m, '__file__', None), str)\n"
+            f"                  and m.__file__.startswith({dirs!r})\n"
+            f"                  and m.__file__ != {str(GRADER)!r})\n"
+            f"    sys.stderr.write({LOADED!r} + repr(held) + '\\n')\n"
+            "atexit.register(_report)\n")
 
 
 def _minimal_env(first_dir):
@@ -348,16 +395,21 @@
 class TC04GuardedScriptsStopAndWriteNothing(unittest.TestCase):
     def test_each_script_and_the_grader_under_a_faked_3_9(self):
         minimum, main = stated()
+        stubs = _grader_local_imports()
         for path in GUARDED + (GRADER,):
             with self.subTest(script=path.name), tempfile.TemporaryDirectory() as tmp:
                 before = _snapshot(WATCHED)
-                proc = _run_under_old(path, tmp)
+                prelude = _stubs_and_report(stubs) if path == GRADER else ""
+                proc = _run_under_old(path, tmp, prelude)
                 self.assertEqual(proc.returncode, 2, proc.stderr[-400:])
                 for needle in (f"{path.name} needs Python", _version(minimum), _version(main),
                                "this is Python 3.9"):
                     self.assertIn(needle, proc.stderr)
                 self.assertEqual(os.listdir(tmp), [])
                 self.assertEqual(_snapshot(WATCHED), before, "a guarded run wrote into the skills")
+                if path == GRADER:
+                    # TASK 123 R2.2: no module body of the grader's local imports ran
+                    self.assertIn(LOADED + "[]", proc.stderr, proc.stderr[-800:])
 
     def test_under_python_m_each_guard_names_its_own_module(self):
         # `python -m <package>` leaves `__main__.py` in argv[0]; that name would tell nothing.
diff --git a/.agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py b/.agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py
--- a/.agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py
+++ b/.agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py
@@ -2227,6 +2227,40 @@
     return f"{c['error']} error / {c['warn']} warn / {c['expected']} expected"
 
 
+def _json_text(value, **kw) -> str:
+    """`json.dumps(value, ensure_ascii=False, **kw)` with each character that `str.isprintable()`
+    refuses, a newline aside, written as a JSON escape. A copy of `json_text` of render_check.py,
+    which the lint does not import: the lint's allow rule would then run render_check.py and
+    svg_geometry.py (TASK 123 R3.1, D7). A test pins the two to one output."""
+    out = []
+    for ch in json.dumps(value, ensure_ascii=False, **kw):
+        if ch.isprintable() or ch == "\n":
+            out.append(ch)
+            continue
+        code = ord(ch)
+        if code > 0xFFFF:
+            code -= 0x10000
+            out.append("\\u%04x\\u%04x" % (0xD800 + (code >> 10), 0xDC00 + (code & 0x3FF)))
+        else:
+            out.append("\\u%04x" % code)
+    return "".join(out)
+
+
+def _shown(text: str, lines: bool = False) -> str:
+    """*text* as the lint prints it: each character that `str.isprintable()` refuses, a newline
+    among them, written as its Python escape. With *lines*, a newline stays: the text is JSON from
+    `_json_text`, or lines that `_format_text` or `_format_inventory` escaped one by one. A
+    backslash stays single (TASK 122 D5). A copy of `_shown` of render_check.py (TASK 123 R3.1); a
+    test pins the two to one output."""
+    return "".join(ch if ch.isprintable() or (lines and ch == "\n") else ascii(ch)[1:-1]
+                   for ch in text)
+
+
+def _say(text: str, file=None, lines: bool = False) -> None:
+    """Print *text* through `_shown`: the only `print` of the lint (TASK 123 R3.2)."""
+    print(_shown(text, lines), file=file)
+
+
 def _finding_line(f: Finding) -> str:
     fence = f" [fence {f.fence}]" if f.fence else ""
     return f"{f.path}:{f.line}: {f.severity} {f.rule}{fence} {f.message}"
@@ -2252,7 +2286,7 @@
     if paths and len(paths) > 1:
         out += [f"{p}: {_summary(counts([f for f in findings if f.path == p]))}" for p in paths]
     out.append(_summary(counts(findings)))
-    return "\n".join(out)
+    return "\n".join(_shown(line) for line in out)
 
 
 def _cell(value) -> str:
@@ -2273,7 +2307,7 @@
         for r in block["rows"]:
             out.append(f"| {_cell(r['kind'])} | {_cell(r['id'])} | {_cell(r['text'])} | {r['line']} |  |")
         out.append("")
-    return "\n".join(out)
+    return "\n".join(_shown(line) for line in out)
 
 
 def build_parser() -> argparse.ArgumentParser:
@@ -2302,21 +2336,21 @@
         return EXIT_USAGE
     if args.probe and (args.paths or args.json or args.inventory):
         # a CI line `--probe docs/*.md` would otherwise pass without linting a file
-        print("usage error: --probe takes no paths and no other option; run the lint without --probe",
-              file=sys.stderr)
+        _say("usage error: --probe takes no paths and no other option; run the lint without --probe",
+             file=sys.stderr)
         return EXIT_USAGE
     try:
         notation = mm.load_notation(notation_path)
     except (OSError, ValueError) as exc:
-        print(f"internal error: notation unreadable: {exc}", file=sys.stderr)
+        _say(f"internal error: notation unreadable: {exc}", file=sys.stderr)
         return EXIT_INTERNAL
     dead = run_probes(notation=notation)
     if dead:
-        print(f"dead rule(s): {', '.join(dead)} — a probe pair failed; the lint reports nothing",
-              file=sys.stderr)
+        _say(f"dead rule(s): {', '.join(dead)} — a probe pair failed; the lint reports nothing",
+             file=sys.stderr)
         return EXIT_INTERNAL
     if args.probe:
-        print(f"{len(RULES)}/{len(RULES)} rules live")
+        _say(f"{len(RULES)}/{len(RULES)} rules live")
         return EXIT_OK
     texts = []
     for raw in args.paths:
@@ -2324,7 +2358,7 @@
         try:
             texts.append((raw, path.read_text(encoding="utf-8"), path.suffix.lower() == ".mmd"))
         except (OSError, UnicodeDecodeError) as exc:
-            print(f"usage error: cannot read {raw}: {exc}", file=sys.stderr)
+            _say(f"usage error: cannot read {raw}: {exc}", file=sys.stderr)
             return EXIT_USAGE
     try:
         if args.inventory:
@@ -2338,19 +2372,21 @@
                         raise LintInternalError(f"{raw}:{broken['line']}: {broken['message']}")
                     blocks.append({"path": raw, "figure_line": fig.fence.start, "figure_kind": fig.kind,
                                    "inventoried": inventoried(fig), "rows": inventory(fig)})
-            print(json.dumps({"schema": "mermaid-inventory/v1", "figures": blocks}, ensure_ascii=False, indent=2)
-                  if args.json else _format_inventory(blocks))
+            if args.json:
+                _say(_json_text({"schema": "mermaid-inventory/v1", "figures": blocks}, indent=2), lines=True)
+            else:
+                _say(_format_inventory(blocks), lines=True)
             return EXIT_OK
         findings = []
         for raw, text, is_mmd in texts:
             findings.extend(lint_text(text, raw, is_mmd=is_mmd, notation=notation))
     except LintInternalError as exc:
-        print(f"internal error: {exc}", file=sys.stderr)
+        _say(f"internal error: {exc}", file=sys.stderr)
         return EXIT_INTERNAL
     paths = [raw for raw, _t, _m in texts]
     total = counts(findings)
     if args.json:
-        print(json.dumps({
+        _say(_json_text({
             "schema": "mermaid-lint/v1",
             "files": paths,
             "rules": len(RULES),
@@ -2358,9 +2394,9 @@
             "per_file": {p: counts([f for f in findings if f.path == p]) for p in paths},
             "findings": [_finding_dict(f) for f in findings if not f.expected],
             "expected": [_finding_dict(f) for f in findings if f.expected],
-        }, ensure_ascii=False, indent=2))
+        }, indent=2), lines=True)
     else:
-        print(_format_text(findings, paths))
+        _say(_format_text(findings, paths), lines=True)
     return EXIT_FINDINGS if total["error"] else EXIT_OK
 
 
diff --git a/.agent/skills/mermaid-authoring-guidelines/scripts/svg_geometry.py b/.agent/skills/mermaid-authoring-guidelines/scripts/svg_geometry.py
--- a/.agent/skills/mermaid-authoring-guidelines/scripts/svg_geometry.py
+++ b/.agent/skills/mermaid-authoring-guidelines/scripts/svg_geometry.py
@@ -2233,7 +2233,8 @@
 
 def main(argv: Optional[list] = None) -> int:
     """Debug entry point: `svg_geometry.py FIG.svg [MEASURE.json] [--source FIG.mmd]` prints
-    metrics and findings; `--source` scopes text contrast by the figure's own colours."""
+    metrics and findings; `--source` scopes text contrast by the figure's own colours. The JSON is
+    ASCII, and an error line escapes what it quotes (TASK 123 R4.1)."""
     args = list(sys.argv[1:] if argv is None else argv)
     usage = "usage: svg_geometry.py FIG.svg [MEASURE.json] [--column PX] [--source FIG.mmd]"
     if not args or args[0] in ("-h", "--help"):
@@ -2254,7 +2255,7 @@
         print(usage, file=sys.stderr)
         return 3
     except OSError as exc:
-        print("svg_geometry.py: %s" % exc, file=sys.stderr)
+        print("svg_geometry.py: %s" % _escaped(str(exc)), file=sys.stderr)
         return 2
     try:
         svg_text = Path(args[0]).read_text(encoding="utf-8")
@@ -2262,11 +2263,11 @@
         metrics = analyze_svg(svg_text, column, measure,
                               author_colours(source) if source is not None else None)
     except (OSError, ValueError) as exc:
-        print("svg_geometry.py: %s" % exc, file=sys.stderr)
+        print("svg_geometry.py: %s" % _escaped(str(exc)), file=sys.stderr)
         return 2
     findings = evaluate(metrics)
     print(json.dumps({"metrics": metrics, "findings": findings, "pass": passes(findings)},
-                     indent=1, ensure_ascii=False))
+                     indent=1, ensure_ascii=True))
     return 0 if passes(findings) else 1
 
 
diff --git a/.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_printed_output.py b/.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_printed_output.py
new file mode 100644
--- /dev/null
+++ b/.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_printed_output.py
@@ -0,0 +1,262 @@
+"""What the lint and the debug command line of svg_geometry.py print (TASK 123 R3, R4.1).
+
+The lint quotes label text, ids and names in its findings and in its inventory. Before TASK 123 it
+printed that text raw, and its `--json` left U+2028 and U+202E raw, so a figure could put a
+terminal control sequence into the output. Now a printed line writes each non-printable character
+as its Python escape, and JSON writes it as a JSON escape. Printable text, Cyrillic among it,
+prints as it is. The lint holds copies of `json_text` and `_shown` of render_check.py, which it
+does not import (TASK 123 D7); a test here pins each pair to one output.
+
+The debug command line of svg_geometry.py prints ASCII JSON, and escapes its error lines with the
+`_escaped` that the file holds (TASK 123 R4.1).
+"""
+import ast
+import contextlib
+import io
+import json
+import sys
+import tempfile
+import unittest
+from pathlib import Path
+from unittest import mock
+
+HERE = Path(__file__).resolve().parent
+sys.path.insert(0, str(HERE.parent))
+
+import lint_mermaid as lm  # noqa: E402
+import render_check as rc  # noqa: E402
+import svg_geometry as sg  # noqa: E402
+
+
+def chars(*codes):
+    return "".join(chr(c) for c in codes)
+
+
+ESC, CSI, RLO, LSEP = chars(0x1B), chars(0x9B), chars(0x202E), chars(0x2028)
+CYRILLIC = "Кириллица"
+#: Label text with control characters, a bidirectional mark and a line separator. As an edge label
+#: it is longer than the limit, so MA-LABEL-03 quotes it in its message.
+HOSTILE = "Evil" + ESC + "[2J" + CSI + "7m" + RLO + "Z" + LSEP + " " + CYRILLIC + " words"
+
+
+def non_printable(text):
+    """The non-printable characters of *text*, a newline aside, as code points."""
+    return sorted({hex(ord(ch)) for ch in text if not ch.isprintable() and ch != "\n"})
+
+
+def call_lint(argv):
+    out, err = io.StringIO(), io.StringIO()
+    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
+        code = lm.main(argv)
+    return code, out.getvalue(), err.getvalue()
+
+
+def figure(body):
+    return "## Figure\n\n```mermaid\nflowchart TB\n" + body + "\n```\n"
+
+
+class LintCase(unittest.TestCase):
+    def setUp(self):
+        tmp = tempfile.TemporaryDirectory()
+        self.addCleanup(tmp.cleanup)
+        self.dir = Path(tmp.name)
+
+    def write(self, name, text):
+        path = self.dir / name
+        path.write_text(text, encoding="utf-8")
+        return str(path)
+
+
+class TestTheLintPrintsNoControlCharacter(LintCase):
+    def test_a_finding_quotes_the_label_with_escapes(self):
+        code, out, err = call_lint([self.write("edge.md", figure("  A -->|" + HOSTILE + "| B"))])
+        self.assertEqual(non_printable(out + err), [])
+        lines = [line for line in out.split("\n") if "MA-LABEL-03" in line]
+        self.assertEqual(len(lines), 1, out)
+        for ch in (ESC, CSI, RLO, LSEP):
+            self.assertIn(ascii(ch)[1:-1], lines[0])
+        self.assertIn(CYRILLIC, lines[0])
+
+    def test_json_reads_back_to_the_message(self):
+        code, out, err = call_lint(["--json", self.write("edge.md", figure("  A -->|" + HOSTILE + "| B"))])
+        self.assertEqual(non_printable(out), [])
+        self.assertIn(CYRILLIC, out)
+        data = json.loads(out)
+        message = next(f["message"] for f in data["findings"] if f["rule"] == "MA-LABEL-03")
+        self.assertIn(ESC + "[2J" + CSI, message)
+        self.assertIn(RLO + "Z" + LSEP, message)
+
+    def test_the_inventory_table_and_its_json(self):
+        path = self.write("node.md", figure('  A["' + HOSTILE + '"] --> B'))
+        code, out, err = call_lint(["--inventory", path])
+        self.assertEqual(non_printable(out + err), [])
+        rows = [line for line in out.split("\n") if line.startswith("| node")]
+        self.assertTrue(rows, out)
+        code, out, err = call_lint(["--inventory", "--json", path])
+        self.assertEqual(non_printable(out), [])
+        texts = [row["text"] for block in json.loads(out)["figures"] for row in block["rows"]]
+        self.assertIn(HOSTILE, texts)
+
+    def test_a_newline_in_a_quoted_label_starts_no_line(self):
+        # A finding quotes label text in its message, and a label of a markdown string may span
+        # lines; the text output escapes the newline of the message (TASK 123 R3.3)
+        label = HOSTILE + "\nsecond line"
+        found = lm.Finding(rule="MA-LABEL-03", severity="warn", path="doc.md", line=5,
+                           message="`" + label + "`: 52 characters > 24", hint="Keep it short.")
+        text = lm._format_text([found], ["doc.md"])
+        self.assertEqual(non_printable(text), [])
+        lines = [line for line in text.split("\n") if "MA-LABEL-03" in line]
+        self.assertEqual(len(lines), 1, text)
+        self.assertIn(ascii("\n")[1:-1] + "second line", lines[0])
+        self.assertNotIn("\nsecond line", text)
+
+    def test_the_inventory_of_a_path_with_a_newline_forges_no_line(self):
+        # `_cell` turns a newline of a label into a space; the header of a block quotes the path,
+        # so only the escape of each line keeps a newline there from starting a line (TASK 123 R3.3)
+        path = self.write("a\nFORGED" + ESC + ".md", figure('  A["' + HOSTILE + '"] --> B'))
+        code, out, err = call_lint(["--inventory", path])
+        self.assertEqual(non_printable(out + err), [])
+        self.assertFalse([line for line in out.split("\n") if line.startswith("FORGED")], out)
+        self.assertIn("a" + ascii("\n")[1:-1] + "FORGED" + ascii(ESC)[1:-1], out)
+        rows = [line for line in out.split("\n") if line.startswith("| node")]
+        self.assertTrue(any(ascii(ESC)[1:-1] in row for row in rows), rows)
+        code, out, err = call_lint(["--inventory", "--json", path])
+        self.assertEqual(non_printable(out), [])
+        self.assertEqual(json.loads(out)["figures"][0]["path"], path)
+
+    def test_a_newline_in_a_path_starts_no_line(self):
+        path = self.write("a\nb" + ESC + ".md", figure("  A -->|" + HOSTILE + "| B"))
+        code, out, err = call_lint([path])
+        self.assertEqual(non_printable(out + err), [])
+        self.assertNotIn("\nb", out)
+        self.assertIn("a" + ascii("\n")[1:-1] + "b" + ascii(ESC)[1:-1], out)
+
+    def test_the_usage_error_of_a_path_it_cannot_read(self):
+        missing = str(self.dir / ("gone\n" + ESC + ".md"))
+        code, out, err = call_lint([missing])
+        self.assertEqual(code, lm.EXIT_USAGE)
+        self.assertEqual(non_printable(err), [])
+        self.assertEqual(err.count("\n"), 1, err)
+
+    def test_the_usage_error_of_probe_with_a_path_goes_through_shown(self):
+        # The line quotes no input; it goes through `_shown` as every line does (TASK 123 R3.2)
+        with mock.patch.object(lm, "_shown", wraps=lm._shown) as shown:
+            code, out, err = call_lint(["--probe", str(self.dir / ("x" + ESC + ".md"))])
+        self.assertEqual(code, lm.EXIT_USAGE)
+        self.assertEqual(non_printable(err), [])
+        self.assertTrue(any("--probe takes no paths" in str(c.args[0]) for c in shown.call_args_list),
+                        shown.call_args_list)
+
+    def test_the_internal_error_line(self):
+        failure = lm.LintInternalError("rule MA-X failed on " + HOSTILE + "\nforged line")
+        # the probes run lint_text too; they stay live, so the failure reaches the linted file
+        with mock.patch.object(lm, "run_probes", return_value=[]), \
+                mock.patch.object(lm, "lint_text", side_effect=failure):
+            code, out, err = call_lint([self.write("doc.md", figure("  A --> B"))])
+        self.assertEqual(code, lm.EXIT_INTERNAL)
+        self.assertEqual(non_printable(err), [])
+        self.assertEqual(err.count("\n"), 1, err)
+
+
+class TestOnlySayPrints(unittest.TestCase):
+    """TASK 123 R3.2, R3.3: every line of the lint goes through `_say`."""
+
+    @classmethod
+    def setUpClass(cls):
+        cls.tree = ast.parse(Path(lm.__file__).read_text(encoding="utf-8"))
+
+    def test_the_only_print_is_the_one_in_say(self):
+        # every call of the module, at any depth: each `print` lies in `_say`, and nothing writes
+        # to `sys.stdout` or `sys.stderr` directly
+        owner = {}
+        for fn in ast.walk(self.tree):
+            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
+                for node in ast.walk(fn):
+                    owner.setdefault(id(node), fn.name)
+        prints, writes = [], []
+        for node in ast.walk(self.tree):
+            if not isinstance(node, ast.Call):
+                continue
+            if isinstance(node.func, ast.Name) and node.func.id == "print":
+                prints.append(owner.get(id(node), "<module>"))
+            text = ast.unparse(node.func)
+            if text in ("sys.stdout.write", "sys.stderr.write"):
+                writes.append(owner.get(id(node), "<module>") + ": " + text)
+        self.assertEqual(prints, ["_say"])
+        self.assertEqual(writes, [])
+        # TASK 123 D7: the lint holds its own copies, so its rule runs neither of these
+        imported = set()
+        for node in ast.walk(self.tree):
+            if isinstance(node, ast.Import):
+                imported.update(a.name.split(".")[0] for a in node.names)
+            elif isinstance(node, ast.ImportFrom) and node.module:
+                imported.add(node.module.split(".")[0])
+        self.assertEqual(sorted(imported & {"render_check", "svg_geometry"}), [])
+
+    def test_lines_go_only_with_json_or_escaped_lines(self):
+        allowed = {"_json_text", "_format_text", "_format_inventory"}
+        kept = []
+        for node in ast.walk(self.tree):
+            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
+                    and node.func.id == "_say"):
+                continue
+            keeps = any(k.arg == "lines" for k in node.keywords) or len(node.args) > 2
+            if keeps:
+                first = node.args[0]
+                kept.append(first.func.id if isinstance(first, ast.Call)
+                            and isinstance(first.func, ast.Name) else ast.unparse(first))
+        self.assertTrue(kept)
+        self.assertEqual(sorted(set(kept) - allowed), [])
+
+
+class TestTheCopiesAgree(unittest.TestCase):
+    """TASK 123 D7: the lint's copies give the output of render_check.py's functions."""
+
+    PROBE = "".join(chr(c) for c in range(0x110000))
+
+    def test_json_text(self):
+        self.assertEqual(lm._json_text(self.PROBE), rc.json_text(self.PROBE))
+        self.assertEqual(lm._json_text({"k": [self.PROBE]}, indent=2),
+                         rc.json_text({"k": [self.PROBE]}, indent=2))
+
+    def test_shown(self):
+        self.assertEqual(lm._shown(self.PROBE), rc._shown(self.PROBE))
+        self.assertEqual(lm._shown(self.PROBE, True), rc._shown(self.PROBE, True))
+
+
+class TestSvgGeometryCommandLine(unittest.TestCase):
+    """TASK 123 R4.1: the debug command line prints ASCII JSON and escaped error lines."""
+
+    def setUp(self):
+        tmp = tempfile.TemporaryDirectory()
+        self.addCleanup(tmp.cleanup)
+        self.svg = Path(tmp.name) / "fig.svg"
+        self.svg.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
+
+    def run_main(self, argv):
+        out, err = io.StringIO(), io.StringIO()
+        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
+            code = sg.main(argv)
+        return code, out.getvalue(), err.getvalue()
+
+    def test_the_json_is_ascii_and_reads_back(self):
+        metrics = {"labels": [HOSTILE + chr(0xD800)]}
+        with mock.patch.object(sg, "analyze_svg", return_value=metrics), \
+                mock.patch.object(sg, "evaluate", return_value=[]), \
+                mock.patch.object(sg, "passes", return_value=True):
+            code, out, err = self.run_main([str(self.svg)])
+        self.assertEqual(code, 0, err)
+        self.assertTrue(out.isascii(), out[:200])
+        self.assertEqual(json.loads(out)["metrics"], metrics)
+
+    def test_an_error_line_holds_no_control_character(self):
+        failure = ValueError("bad path data near " + HOSTILE + "\nforged line")
+        with mock.patch.object(sg, "analyze_svg", side_effect=failure):
+            code, out, err = self.run_main([str(self.svg)])
+        self.assertEqual(code, 2)
+        self.assertEqual(non_printable(err), [])
+        self.assertEqual(err.count("\n"), 1, err)
+
+
+if __name__ == "__main__":
+    unittest.main()
diff --git a/.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/paired-examples-geometry.json b/.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/paired-examples-geometry.json
--- a/.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/paired-examples-geometry.json
+++ b/.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/paired-examples-geometry.json
@@ -3,8 +3,8 @@
  "about": "Render evidence of every mermaid fence of the files below, keyed by file and opening fence line; written by `python3 scripts/render_check.py <file> --fixture <this file>` (TASK R7.8, R9.5, A19). Per file it holds the sha256 of the instruments and the notation values the renders ran with. scripts/tests/test_paired_examples.py recomputes each sha256 from the file and evaluates the stored metrics against notation.json without node.",
  "files": {
   "references/paired-examples.md": {
-   "generated": "2026-10-15T09:22:01Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:53:03Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
diff --git a/.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/references-geometry.json b/.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/references-geometry.json
--- a/.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/references-geometry.json
+++ b/.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/references-geometry.json
@@ -3,8 +3,8 @@
  "about": "Render evidence of every mermaid fence of the files below, keyed by file and opening fence line; written by `python3 scripts/render_check.py <file> --fixture <this file>` (TASK R7.8, R9.5, A19). Per file it holds the sha256 of the instruments and the notation values the renders ran with. scripts/tests/test_paired_examples.py recomputes each sha256 from the file and evaluates the stored metrics against notation.json without node.",
  "files": {
   "references/ascii.md": {
-   "generated": "2026-10-15T09:24:20Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:53:50Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
@@ -19,8 +19,8 @@
    "figures": {}
   },
   "references/eval-results.md": {
-   "generated": "2026-10-15T09:24:20Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:53:50Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
@@ -35,8 +35,8 @@
    "figures": {}
   },
   "references/flowchart.md": {
-   "generated": "2026-10-15T09:22:43Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:53:50Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
@@ -808,8 +808,8 @@
    }
   },
   "references/gantt.md": {
-   "generated": "2026-10-15T09:22:43Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:54:04Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
@@ -1407,8 +1407,8 @@
    }
   },
   "references/layout-and-planarity.md": {
-   "generated": "2026-10-15T09:22:43Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:54:13Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
@@ -2117,8 +2117,8 @@
    }
   },
   "references/other-kinds.md": {
-   "generated": "2026-10-15T09:22:43Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:54:27Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
@@ -3458,8 +3458,8 @@
    }
   },
   "references/renderer-facts.md": {
-   "generated": "2026-10-15T09:22:43Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:54:51Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
@@ -6241,8 +6241,8 @@
    }
   },
   "references/review-checklist.md": {
-   "generated": "2026-10-15T09:22:43Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:55:31Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
@@ -6429,8 +6429,8 @@
    }
   },
   "references/sequence.md": {
-   "generated": "2026-10-15T09:22:43Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:55:34Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
@@ -6738,8 +6738,8 @@
    }
   },
   "references/state.md": {
-   "generated": "2026-10-15T09:22:43Z",
-   "instruments": "ceef084dc985af09d2c42082616631ac6211c9517b210a966c530a88e3101b10",
+   "generated": "2026-10-15T14:55:37Z",
+   "instruments": "7b29e01af879b87dc05b98ec56cb78204110530ed8adb730218a02f3c1238ba9",
    "settings": {
     "column_px": 900,
     "render_width_px": 1800,
diff --git a/.agent/workflows/framework-upgrade.md b/.agent/workflows/framework-upgrade.md
--- a/.agent/workflows/framework-upgrade.md
+++ b/.agent/workflows/framework-upgrade.md
@@ -108,18 +108,68 @@
    change that alters what runs, or what runs without a prompt. The list is not exhaustive:
    - a hook in a settings file, or in the frontmatter of an agent or a skill;
    - the script of a registered hook, code that script calls, and a new module it would import;
-   - a script that a committed allow rule names, code that script calls, and a new module it
-     would import;
+   - a script that an allow rule names, code that script calls, and a new module it would import;
    - a permission rule, `additionalDirectories` or the permission mode, an agent's
      `permissionMode` and the `allowed-tools` of a skill or a command among them;
    - a settings key that names a command, such as `statusLine`, or sets a command's environment,
      `env`;
    - the MCP servers of `.mcp.json` or a settings file, and `enableAllProjectMcpServers`.
 
+   The allow rules are those of `.claude/settings.json`, `.claude/settings.local.json` and the
+   user's `~/.claude/settings.json`, and the `allowed-tools` of a skill or a command. A command that
+   one of them approves is an allowed command, and a rule names a file also through a symbolic link
+   that resolves to it. Rules that managed settings or plugins add, and the commands that the Auto
+   mode classifier approves, lie outside this count; the operator answers for them. Git holds
+   neither the local file nor the user's, and Claude Code adds a rule to one of them when the
+   operator approves a command permanently. The run reads both when §2.2 writes the PLAN, again at
+   §4.5, and again after the gates of stage 3. A rule added since the first reading that runs a
+   file the change adds or edits in place, directly or through other code, stops the run for the
+   operator. The audit record names each file of the change that a rule of either file runs,
+   directly or through other code, and quotes no such rule.
+
    Test modules and fixtures that no rule names by path are exempt, and so is code that runs
-   without a prompt only through them. A test module is a `test_*.py` or `conftest.py` file that no
-   hook or listed script runs or imports; a fixture is a data file that a test reads.
+   without a prompt only through them. A rule that names a directory, such as `discover -s tests`,
+   names no module in it. A test module is a `test_*.py` or `conftest.py` file that no hook or
+   listed script runs or imports; a fixture is a data file that a test reads.
    `tests/run_tests.py` is named by a rule and is not exempt.
+
+   **What the change runs.** The run checks what code of the change writes when an allowed command
+   runs it. That code is what the change adds or edits, test modules among them. It is also what an
+   allowed command first reaches through the change, such as a test that a collection error had
+   blocked. A rule with a wildcard, or one whose command runs other code from another directory,
+   gives one command for each option, input or directory that reaches code the change adds or
+   edits. For each command, one process lists every file and directory under the repository root,
+   each regular file with its SHA-256, ignored files included and no link followed. Of `.git` it
+   lists every file but `index` and those under `objects` and `logs`, and of `logs` it lists
+   `refs/stash`, which holds every stash. It adds the output of `git rev-parse HEAD` and
+   `git ls-files -s -v`, and lists the user's `~/.gitconfig`, `~/.config/git/config` and
+   `~/.claude/settings.json`. Each git command of the check and of the put-back runs with
+   `-c core.fsmonitor=false`, so that git runs no file-system monitor that the checked command
+   configured. The process then runs the command as the rule approves it, with
+   `PYTHONDONTWRITEBYTECODE=1` and `PYTEST_ADDOPTS=-p no:cacheprovider` in its environment, and
+   lists again. The audit record names the code that wrote each difference, read from that code or
+   from the command's output.
+   - A difference that the command is meant to write, such as the state that `update_state.py`
+     records, passes the check.
+   - Any other difference that code of the change writes fails the check. Before the change lands,
+     that code writes into a temporary directory, which it removes.
+   - A difference that other code writes is a finding before the task.
+
+   After the check, the run puts back each difference that the command was not meant to write. A
+   difference under `.git` or in a file of the user, or a file of the first listing that the second
+   lacks, stops the run. The run names each difference to the operator and runs no further git
+   command. Otherwise:
+   - it removes each file that the command created, and then each directory that it created;
+   - it restores a tracked file that no kind of §5 step 1 declares, with
+     `git restore --source=<base> --staged --worktree -- ':(literal)<path>'`, and checks that the
+     file hashes as in the first listing;
+   - it records a changed session state again through `update_state.py`;
+   - it names every other difference to the operator, the run's own records among them.
+
+   The check runs with the gates of §3.3, and for the code of stage 3 with the gates of stage 3,
+   where a failed check is a failed gate. The audit record holds each command, with its paths
+   relative to the repository root, and its result. TASK 122 unblocked the bare pytest run, and a
+   test it reached rewrote the live session state.
 
    A change that only narrows what runs without a prompt, such as a removed allow rule, may land
    at once: it runs nothing new, and at worst a command asks. Before the edit, a check shows that
diff --git a/.agent/skills/mermaid-authoring-guidelines/scripts/render_check.py b/.agent/skills/mermaid-authoring-guidelines/scripts/render_check.py
--- a/.agent/skills/mermaid-authoring-guidelines/scripts/render_check.py
+++ b/.agent/skills/mermaid-authoring-guidelines/scripts/render_check.py
@@ -487,8 +487,9 @@
     above U+FFFF becomes its pair of surrogate escapes; printable text, Cyrillic or an emoji, stays
     as it is. The JSON reads back to *value*, save one case: a high surrogate followed by a low one,
     as two code points, reads back joined into one. No control character, bidirectional mark or
-    lone surrogate reaches a terminal or a file. svg_geometry.py is not edited for it: its module
-    body runs without a prompt (TASK 122 D10)."""
+    lone surrogate reaches a terminal or a file. TASK 122 left svg_geometry.py unedited for it,
+    since that module's body then ran without a prompt (D10). lint_mermaid.py holds copies of this
+    function and of `_shown`; a test pins each pair to one output (TASK 123)."""
     out = []
     for ch in json.dumps(value, ensure_ascii=False, **kw):
         if ch.isprintable() or ch == "\n":
~~~~

Step 3: `git diff --quiet <base> --` each of the eight files that the patch edits exited 0, and the
new test module was absent. `git apply --whitespace=nowarn` of the patch exited 0.

Step 4, the postconditions, all pass:
- each file on the right of TASK R9.1 hashes to its staged copy;
- each file that the patch touches hashes to its value of round 3 and has mode 644, the new test
  module among them;
- `git apply --check -R` of the patch exits 0.

Step 5: `rm --` removed each staged copy, one at a time, and no `rm` failed:
- `tests/staged_run_safety_rules.py`;
- `tests/staged_python_floor.py`;
- `S/scripts/staged_lint_mermaid.py`;
- `S/scripts/staged_svg_geometry.py`;
- `S/scripts/tests/staged_printed_output.py`;
- `S/scripts/tests/fixtures/staged_paired-examples-geometry.json`;
- `S/scripts/tests/fixtures/staged_references-geometry.json`.

`git status` then shows 34 paths, each declared by the PLAN or by `framework-upgrade` §5.

## The gates of stage 3 (J3)

- `run_gates.sh` on the applied tree: 18 of 18. `tests/run_tests.py` passes, the skill's suite
  passes 717 with the known skip, and the eval selftest 226 of 226.
- `regcheck.py` of the 13 changed documents, `.agent/workflows/framework-upgrade.md` among them,
  this record and WI-54: no warning on an added line.
- The check of TASK R1.1, with `h3.sh <repo> <log dir> 1 lint`:
  - checks 1 to 5, the four `python3 -m pytest` and `python3 tests/run_tests.py`: equal listings;
  - check 6, `python3 -m unittest discover -s tests -v`: two empty directories added,
    `tests/.scratch/` and a session directory in it, from `tests/_scratch.py` as at H3. Before the
    task. `h3.sh` stopped there; the put-back removed both with `rmdir --`, the inner one first;
  - checks 7 to 15, run again from check 7: equal listings. They are the unittest run of the
    skill's tests, the E2E script of `run-feedback`, and seven runs of the lint. Those seven are
    its text output, `--json`, `--inventory` and `--inventory --json` of
    `S/references/paired-examples.md`, `--probe`, `--probe` with a path and a missing path, with
    exits 0, 0, 0, 0, 0, 3 and 3;
  - the four outputs of the lint hold no raw control character, and the text output holds the 21
    findings of TASK §8.
- `rules_check.py compare` after the gates: the local file and the user's are unchanged since the
  reading at §2.2; no rule is new.
- `git status` shows the 34 declared paths.

## Stage 4 (J4), at the fingerprint `2d3e67490983`: both PASS

Both agents, resumed, quoted the fingerprint at their start and end, and it held. Neither wrote in
the repository; the code reviewer tested in a clone outside it.

**Code review: PASS (APPROVED).** The nine files that the patch touched hash to the values of round
3, with mode 100644, and the fence of J2 equals the patch byte for byte. No staged copy remains, and
since round 3 only the patched files and the named records changed. The fences of the TASK still
equal the applied text. The pin, `test_git_rollback_contract`, the floor test and the bare-pytest
test passed 33, and `run_gates.sh` 18 of 18. The entries of J1 to J3 match the logs. One finding:
- R4-1, LOW, records only: revision 8 had moved the residual sentence of S1-4 in §9 under the list
  of WI-54. The operator allowed the fix after stage 3 ("Да, переставь"), and the sentence is back
  at the end of its bullet. No file of the patch changed.

**Security audit: PASS**, `scan_status: findings`. The applied files hash to the values of round 3,
and no staged copy, `.rej` or `.orig` file remains. A fuzz of 300 hostile documents through the four
outputs of the applied lint gave no raw character, and neither did eight command-line runs, two of
them of `svg_geometry.py`. The scan gives 210 findings, 25 critical and 9 high; the removed staged
copy had repeated three lines of the base. Every hit on a changed file repeats a base line, and
gitleaks finds no leak in the change. No record quotes an allow rule. The fixes of S3-2 and S3-3 in
the run's tools hold in a sandbox. No new finding.

Before the task, per both reviews: the empty directories of `tests/_scratch.py` (R2-5); the
fingerprint formula runs a planted monitor; D10; WI-41. All LOW.

**Verdict:** stage 4 passed, and the Failure path does not apply.

## Retro (K1)

`run_feedback.py` held the claim `framework-upgrade-staging-rules-and-loose-ends` from §0. The retro
question listed four candidates:
- the HIGH of round 2;
- the empty directories of `tests/_scratch.py`;
- the monitor that the fingerprint formula runs;
- three rounds on one class.

The operator answered "ничего", so the retro collects and files nothing. `release` freed the claim.

The operator also chose TASK 124 for the split of `lint_mermaid.py`, `svg_geometry.py` and
`mermaid_model.py` into modules, after the commit of TASK 123, with no backlog record.
