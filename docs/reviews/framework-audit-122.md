# Framework Audit 122 — The render check prints no raw control character, a bare pytest run collects, and the quick-reference figure is redrawn

- **Task:** 122 `render-output-pytest-figure`. It archives to
  `docs/tasks/task-122-render-output-pytest-figure.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1.
- **Date:** 2026-10-15. **Base revision:** `b6362e3444eaa1b9109a104a445b100f7e4e964d`, clean tree
  at start (TASK 121, committed by the operator as `b6362e3`).
- **Source:** findings of TASK 121 marked as before the task; the operator's request "Я сделал
  коммит, выполни доработки".

## 0. Emergency Bypass

None.

## Archive (§1)

TASK 121 and PLAN 121 archived under ID 121:
- `task_id_tool.py "github-font-swap" --proposed-id "121" --no-correction`: `generated`,
  `task-121-github-font-swap.md`;
- both moves `"ok": true`;
- Step 5.5: one rewrite, the link to WI-53, exit 0; Step 7.6.5: one `SLOT_RESOLVED`, exit 0;
- Step 8 with `--since eea6a96…`: exit 3. It lists the two `INBOUND` records of the v3.13.0
  changelog entries (`CHANGELOG.md:3328@b6362e3`, `CHANGELOG.ru.md:3344@b6362e3`), which carry no
  reason and stay. Step 8 rewrote no file.

## Research (§1)

The measurements of TASK §8 ran in the session's scratchpad and in temporary directories outside
the repository. The two new figures were written to a scratch file, linted and rendered there. No
repository file was written by the research.

The retro claim `framework-upgrade-render-output-pytest-figure` was taken at the start of the run.

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

The reviewer quoted the fingerprint `9a4f21409387`. It had no shell, so the register scan and the
reference resolver of `task-review-checklist` §6 and §7 did not run in its audit.

- M1, MAJOR: R3.2 cannot hold. The `__main__` block of the example names a role file that does not
  exist, so a run ends in `FileNotFoundError` before `query_model`. No criterion tested R3.2.
- M2, MAJOR: the fidelity table cited lines that do not state `complex, ambiguous`, `simple` or
  `standard`, and no row covered four node labels.
- m1: R1.2 left out `mermaid-config.json`; `browser_stat_digest` must keep its form; R1.4 left out
  the `fixture:` line and the error of reading `notation.json`; argparse prints its errors itself.
- m2: the rule for code points above U+FFFF read as covering printable ones, and the round trip has
  an exception for a joined surrogate pair.
- m3: the tests left the measurement file, mmdc's error lines, a command-line error, R1.3 and the
  second cut unchecked.
- m4: R1 and R5.3 claimed every file; the `.mmd`, SVG and PNG keep the figure's text.
- m5: R5.5 did not name the two bare pytest rules.
- m6: the lint count was wrong: 18 warnings on the legacy figure, not 11.
- m7: D2 stated no rejected alternative.
- Notes: the traceback of §1.2 stops the run at the first render; the nested collection runs on
  3.11 in CI; the residual of D5; the lint's `--json` in §9; preconditions of the use cases.

Revision 2 applies all of them:
- R3.2 is restated on `query_model`, and R3.3 tests both branches; the example's `__main__` is in
  §9.
- The first figure takes the document's own words: 9 nodes and 8 edges, rendered again (§8).
- R1.2, R1.4 and R1.5 list each site and each exclusion; D8 keeps argparse's messages.
- R1.1 and R5.2 name U+E0001 and U+1F4E6 and the round-trip exception.
- R5.2 adds the tests of m3; A1 names the measurement file.
- D9 records the 3.11 grammar check, and the bare run's 709 passes are in §8.

### Round 2 — TASK revision 2: PASS

The reviewer quoted the fingerprint `c9409264f138`. M1, M2 and m1 to m7 are RESOLVED, apart from
part (c) of m3, which returns as r2-1. The reviewer read the scratch figures: 9 nodes and 8 edges,
then 5 and 4, no cycle; the settings line and the class equal the product figure's.

- r2-1, MINOR: the test of R1.3 seeded a font name, which TASK 121 already escapes, so it would
  pass on the base. Seed a label of `font_swap.hidden` instead; the stubbed run names the clean
  font name.
- Notes N1 to N8:
  - A1's measurement file comes from the stand-in run (N1).
  - `measure_text.mjs` writes the PNG (N2).
  - "No key" means neither variable is set (N3).
  - §8 records the run with `--ignore=examples`, not the bare run (N4).
  - The 3.11 run happens first in CI (N5).
  - D8's residual also covers a glob (N6).
  - One line held 120 characters (N7).
  - The scan's detectors line belongs in this record (N8).

Revision 3 applies r2-1 and N1 to N8, on the precedent of PLAN 121 revision 3: comments of a passing
round take no further round.

The orchestrator ran the checks the reviewer could not run, on revision 3:
- `scan_register.py docs/TASK.md`: exit 0, "0 warn / 0 info — advisory". The detectors, all
  probe-tested in that run: `sentence_length`, `sentence_near_limit`, `cell_width`,
  `cell_sentences`, `emoji_severity`, `marker` (28/28), `maxim` (9/9), `metaphor` (5/5) and
  `reasoning` (11 of 11). 209 sentences, mean 11.2, longest 27 (limit 35).
- `check_positional_refs.py --all docs/TASK.md` on revision 2: 3 of 3 references resolve.

**Mode A verdict:** PASS, TASK revision 3.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: FAIL

The reviewer quoted the fingerprint `96532cc943de`.

- M1, MAJOR: the Sequencing rule said "No code of this run is named by an allow rule (TASK R5.5),
  so no step is staged". R5.5's claim that no listed script runs the edited code is false for
  `svg_geometry.py`. The allow rule of `tests/run_tests.py` runs `test_python_floor`, whose TC-04
  runs `grade_figures.py`. The grader imports `svg_geometry` before its version guard. TASK 121
  made the same claim, so its unstaged edits of that file rest on the same oversight.
- m1: nothing recorded that the installed-renderer test ran.
- m2: B4's red run shows the failed write of R1, not the cut of R2.
- m3: B5's branch with a key passed on the base, which exits at import with the same message.
- m4: B2 left the `_stop_early` print and the `--fixture` output untested.
- m5: the fix-round order had no D2, and 122.D did not depend on 122.C.
- m6: H1 stated no rule for an `INCOMPLETE` security audit.
- m7: B5's children could write caches.
- m8: the ARCHITECTURE bullet claimed more than R1: a newline stays, and argparse prints raw.
- Notes n1 to n9:
  - repairs of §4.5 after G1 (n1), and TC-03 for a C1 in `svg_geometry.py` (n2);
  - two red-run descriptions (n3), `openai` absent at C6 (n4), and `OPENAI_BASE_URL` (n5);
  - the records of the retro (n6), the 3.11 half of A5 (n7), and no sub-task files (n8);
  - `render_corpus.py` writes with `ensure_ascii=False`, before the task (n9).

TASK revision 4 and PLAN revision 2 apply them:
- `json_text` lives in `render_check.py`, and `svg_geometry.py` stays unedited (TASK D10). R1.3 is
  withdrawn, and R5.5 names the chain. C2 checks with `git diff --quiet` that the file is unchanged.
- B2 to B5, C2, C3, C6 and E2 take m1 to m4, m7, n3 to n5.
- 122.D depends on 122.C, and H1 states D2, the `INCOMPLETE` rule and the LOW-route rule.
- I1 and I2 take n1 and n6; the ARCHITECTURE bullet takes m8; §9 of the TASK takes n9.
- n2 lapses with D10. n7 goes into the end-of-run report.

### Round 2 — PLAN revision 2: PASS

The reviewer quoted the fingerprint `558153abc47d`. M1 and m1 to m8 are RESOLVED. The chain of TASK
R5.5 holds, and nothing it reaches is edited.
- r2-1, MINOR: C2 said B4 fails on the code-point count. On the base the text is also 120 code
  points; only its last one, a lone U+D83D, differs.
- r2-2, MINOR: the Sequencing rule said that no edited code runs without a prompt. The example and
  the new test module do, as exempt test modules.
- Notes: R5.5 named `render_check.py` as the only runner of `measure_text.mjs`; a retro record is
  no declared path; this record misquoted revision 1.

**Mode B verdict:** PASS, PLAN revision 2.

## Mode A — round 3, TASK revision 4: PASS

The reviewer, resumed, quoted `558153abc47d` and checked the delta of revision 4. It verified the
chain and that no listed script reaches `render_check.py` or `measure_text.mjs`. D10 is sound.
- r3-1, MINOR: the two new cases of R5.2 named only ESC, which `json.dumps` already escapes.
- Notes: R5.5's "its version guard"; the runners of `measure_text.mjs`; `render_corpus.py` writes
  metrics; D10's second rejected alternative stated no reason.

TASK revision 5 and PLAN revision 3 apply r2-1, r2-2, r3-1 and the notes of both rounds. They take
no further round, on the precedent of PLAN 121 revision 3.

## §3 — Execution (clusters A to G)

Logs, the gate runner and the scratch figures stay in the session's scratchpad until the run ends.
Every run set `PYTHONDONTWRITEBYTECODE=1` and passed `-p no:cacheprovider`.

- **A1:** `HEAD` equals the base; the 11 edited paths are tracked; `git check-ignore` exits 1 for
  `tests/test_bare_pytest.py`; the 12 declared paths match the pattern.
- **B, red against the base code:**
  - the three `json_text` tests fail: `render_check` has no `json_text`;
  - the text output, the command-line error, the run with no renderer and `dump_json` print raw
    C1 controls, U+202E and U+2028;
  - `evidence.json`, the stand-in measurement file and the fixture at a path with ESC raise
    `UnicodeEncodeError` on the lone surrogate when written;
  - the cut test raises `UnicodeEncodeError` on U+D83D at the write of the measurement; it ran
    and did not skip;
  - `tests/test_bare_pytest.py`: the collection exits 3, and each child exits at import before
    its marker.
- **C1, C2:** `json_text`, `_shown` and `_say` in `render_check.py`; its 18 `print` calls go
  through `_say`. Postconditions:
  - B1 to B3 pass;
  - B4 fails on the text: the last code point is a lone U+D83D;
  - `git diff --quiet <base> -- scripts/svg_geometry.py` exits 0.
- One test was corrected after C2. Its fixture check re-encoded the loaded data with `json.dumps`,
  which writes ESC as an escape, so it could not find the raw text. It now compares the decoded
  font names. Against a copy of the base `render_check.py` it still fails, with
  `UnicodeEncodeError` at the fixture's write; against the edited one it passes.
- **C3:** both cuts take `Array.from(…).slice(0, 120)`; `node --check` passes. B4 passes, both
  subtests; `-rs` shows no skip.
- **C4, C5:** the example imports `openai` in `query_model`; the tooling step lists the new test.
- **C6:** B5 passes, 4 of 4. `python3 -c "import openai"` fails here with `ModuleNotFoundError`.
  `python3 -m pytest --co -q -p no:cacheprovider` from the root: "713 tests collected", exit 0,
  no `INTERNALERROR`.
- **D1, D2:** the two figures replace the legacy one. `lint_mermaid.py System/Docs/WORKFLOWS.md`:
  "0 error / 0 warn / 0 expected". `render_check.py System/Docs/WORKFLOWS.md`: exit 0, 3 figures
  pass. Sizes: 653×1085 and 746×317 px (11.17.2); the product figure 641×837 px.
- **E1:** both fixtures hold the instrument hash `7c8538c0fa1c` of the current files.
  - `paired-examples-geometry.json`: 14 figures, 6 pass, 8 negative as expected, exit 0.
  - `references-geometry.json`: 37 figures, 15 pass, 7 pass with geometry not checked, 15
    negative as expected, exit 0.
  - The two files with no fence exit 2.
- **E2:** the skill's suite: 697 passed, 1 skipped, the APFS test, before the task. The
  installed-renderer tests ran. `evals/selftest_figure_evals.py`: 225 of 225.
- **F1:** the §10.7 bullet, written at §2.1. **F2:** v3.42.1 in both changelogs.
- **F3:** `System/Docs/SKILLS.md` states no fact this task changes; not edited.
- **F4:** no register `WARN` on an added line of the changed documents.
- **G1:** the scratchpad runner reads the tooling step's arguments from the workflow file. All 17
  CI steps pass; the tooling step runs 532 tests, the new module among them. The bare
  `python3 -m pytest -p no:cacheprovider` from the root: "713 passed", exit 0. `git status` holds
  17 entries, all declared. No bytecode file is newer than the run's start. `.pytest_cache` at the
  root dates from before the task.

## Reviews (H1)

### Round 1 — fingerprint `2de563bdc930`

Both agents quoted the fingerprint at their start and end; equal on return. Neither wrote a
tracked or untracked path of the tree.

**Code review: REJECTED.** The code meets R1 to R5, every gate passes, and 26 planted mutations
were run. F1 blocks: a regression that the change causes.
- F1, MEDIUM: the allowed bare `python3 -m pytest` ran nothing at the base. It now runs every test,
  `tests/test_mock_agent.py` among them. That test's mock calls `update_state.py`, which anchors at
  the nearest `.git` and rewrites the live `.agent/sessions/latest.yaml`. The reviewer's own run of
  G1 rewrote it at 11:51:28, and the orchestrator's G1 run did the same before it.
- F2, LOW: 11 of the 18 `_say` sites survive a revert to `print`, the `note:` line among them.
- F3, LOW: `tests/test_tool_runner.py` writes `tests/temp_tool_test/`, a path git does not ignore;
  an interrupted bare run would leave it.
- F4, LOW: the docstring of `json_text` omits the joined-surrogate exception of R1.1.

**Security audit: PASS**, `scan_status: findings`. The scan exited 0 with `not_run` empty,
`scan_complete` true and external `COMPLETE`; no scanner hit falls on the change's lines.
- LOW-1, CWE-117: `_shown` keeps a newline, so a field that holds one forges lines of the text
  report. The audit reproduced a forged passing `summary:` line through a sequence participant
  and through a file name, on the pinned 11.17.2 install.
- LOW-2: F1 of the code review.
- LOW-3: the changelogs claim no raw control character, but a newline and argparse's messages
  print raw.
- INFO: the residuals of D5 and D8 hold as stated; `json_text` and `_shown` were checked over all
  1,114,112 code points.

Before the task, per the reviewers:
- LOW: `check_positional_refs.py --targets-changed` reports 11 errors: the nine of D2, and two more
  of the same coordinates in `docs/reviews/framework-audit-105.md`.
- LOW: `test_mock_agent.py` and its mock run `python3` from PATH with paths relative to the
  working directory, and the mock sleeps 5 s.
- LOW, CWE-201: with only `XAI_API_KEY` set, the example sends that key to the default OpenAI URL.
  The example's `__main__` fails first (TASK §9).
- LOW: GHSA-238p-pmpm-9mq7 (KaTeX) in the three renderer lockfiles.
- LOW: the lint prints label text raw (TASK §9).
- LOW: `test_ledger_hardening.py` of `run-feedback` holds raw U+2028, U+2029, U+202E, U+2066,
  U+200B and U+00AD in string literals.
- CRITICAL and HIGH, scanner severity: 25 and 9 raw hits, all triaged as false positives or seeded
  fixtures outside the change.

The live session state held the mock's record after G1. The orchestrator restores it in fix round 1.

### Fix round 1

The code review did not pass, so the run returns to the fix of its findings. TASK revision 6
(D11) and PLAN revision 4 apply F1 to F4 and LOW-1 to LOW-3.

Red runs first:
- against the code before the edit: both newline tests fail, since a field's newline starts a line;
- against a copy of the base `render_check.py`: the forward `note:` test and the AST test fail;
- the AST test against a copy with only the `note:` call turned back into `print`: it finds
  `['_say', 'main']`;
- `test_mock_agent.py` with its new assertion and the old run: the live state is rewritten, and its
  sha256 changes from `b8c5a6dd18e9…` to `d003f78ebbab…`;
- `test_tool_runner.py` with its new assertion and the old directory: `git check-ignore` exits 1.

Edits:
- `render_check.py`: `_shown` writes a newline as an escape too, unless the caller passes `lines`
  for JSON from `json_text`. The text report prints its lines one by one. The docstring of
  `json_text` names the joined-surrogate exception.
- `tests/test_mock_agent.py`: the mock runs in a sandbox under `tmp_path`, with an empty `.git`, a
  copy of `update_state.py` and no `CLAUDE_PROJECT_DIR`. The test asserts that the record lands
  there and that the live file's bytes stay.
- `tests/test_tool_runner.py`: its directory comes from `repo_scratch_dir`, under `tests/.scratch`.
- The changelogs and the §10.7 bullet name the newline, the line-by-line report and argparse; the
  changelogs add the bare run's hygiene.
- The live session state was written anew, and its records `Task A`, `Task B` and `test-task-123`
  were dropped.

Checks, in the order of H1:
- E1: both fixtures re-rendered with the summaries of §3; both hold the instrument hash
  `ceef084dc985` of the current files.
- D2: `WORKFLOWS.md` lints "0 error / 0 warn / 0 expected"; the render check exits 0, 3 figures
  pass.
- E2: the skill's suite gives 701 passed, 1 skipped (APFS); the eval selftest gives 225 of 225.
- F4: no register `WARN` on an added line.
- G1: all 17 CI steps pass; the tooling step runs 533 tests. The bare run gives "714 passed", and
  the sha256 of the live session state is `008845300d2a…` before and after it. `git status` holds
  19 entries, all declared; no bytecode file is newer than the run's start, and no
  `temp_tool_test` remains.

### Round 2 — fingerprint `2767fb0cc01c`

Both agents, resumed, quoted the fingerprint at their start and end; equal on return. The live
session state read `dd4c95efa7da7a2c` before and after the code reviewer's bare run in the live
repository.

**Code review: APPROVED.** F1 to F4 and the fix of LOW-1 are RESOLVED, each checked by plantings in
a clone. A second, unsandboxed mock run fails the live-state assertion. Each of the 18 `_say`
sites turned back into `print` fails the AST test. New LOW findings:
- R2-1: `.claude/settings.local.json`, which git ignores, holds an allow rule that names
  `tests/test_tool_runner.py`. Fix round 1 edited that file. Whether local rules fall under
  `framework-upgrade` §3 step 4 is for the operator.
- R2-2: `lines=True` at a non-JSON `_say` site survives at 14 of 16 sites, the class of F2.
- R2-3: the sandbox's copy of `update_state.py` stays in pytest's base temps after the test.
- R2-4: the record gives no replay line for the fixtures: 0 of 51 figure entries moved.
- R2-5: TASK §9 says the test runs the mock with `python3`; it now uses `sys.executable`.

**Security audit: PASS**, `scan_status: findings`. LOW-1 to LOW-3 are RESOLVED, each replayed on
the pinned install or in a git copy. A bare run of a copy left its 2926-entry manifest unchanged.
No new finding. INFO: `lines=True` is a general switch (R2-2), and the live-state assertion fails
closed if `update_state.py` runs concurrently during the mock's 5 s.

### Fix round 2

The round passed. The orchestrator applies R2-2 to R2-5 in the touched lines, on the precedent of
TASK 120 D3 and TASK 121 D10, and records R2-1 as TASK D12. Round 3 is the last of the bound.

- Red first: the AST check of `lines` passes on the code and fails against a copy that passes
  `lines=True` to the `note:` line, with `[True, True, False]`.
- R2-3: the mock's sandbox is a `TemporaryDirectory`, removed on exit.
- R2-4, the replay of the fixtures re-rendered in fix round 1: 0 of 51 figure entries moved against
  the base. Only `instruments` and `generated` changed in each file entry.
- R2-5: TASK §9 names the mock's `python3`; D12 records R2-1.
- Checks: the skill's suite gives 702 passed, 1 skipped (APFS). All 17 CI steps pass, the tooling
  step with 533 tests. The bare run gives "714 passed", and the live session state reads
  `dd4c95efa7da7a2c` before and after it. A run of `tests/test_mock_agent.py` creates no base temp
  of pytest. `git status` holds 19 entries, all declared; no bytecode file is newer than the run's
  start. No instrument changed, so the fixtures and `WORKFLOWS.md` were not rendered again.

### Round 3 — fingerprint `981ac85ed7ee`

Both agents, resumed, quoted the fingerprint at their start and end; equal on return. The live
session state read `8152f9ca8fc7e73c` before and after the code reviewer's bare run.

**Code review: APPROVED.** R2-1 to R2-5 are RESOLVED. Each of 16 plantings of `lines=True` at a
non-JSON `_say` site fails the AST check, and so does a third JSON print. A sandbox that is never
removed leaves the one copy that the residue search finds. Two notes that set no verdict:
- R3-1, LOW: R5.5 said that no allow rule names an edited file, against D12. It now says
  "committed" in both places and cites D12.
- R3-2, nit: the docstring of `tests/test_mock_agent.py` named `tmp_path`; it no longer does.

**Security audit: PASS**, `scan_status: findings`. The scan at this fingerprint gives round 2's
result. Five mutants of `lines` fail the AST check. A bare run of a git copy left its manifest and
a synthetic session file unchanged. No new finding.
- On D12: `framework-upgrade` §3 step 4 lists "a script that a committed allow rule names" and
  exempts only "test modules and fixtures that no rule names by path". The two sentences disagree
  on a local rule. D12 is acceptable for this run, and the reading is the operator's call.
- Before the task, LOW (process): that disagreement in the workflow text. INFO: each bare run
  leaves about 175 temporary entries in the private `$TMPDIR` from earlier tests.

**Review verdict:** passed at round 3 of 3. D12 now quotes both sentences and names the reading as
the operator's call. The wording of R3-1 and R3-2 took no further round, on the precedent of PLAN
121 revision 3. `tests/test_mock_agent.py` passes after its docstring edit.

## §4.5 — references (I1)

- `check_positional_refs.py --targets-changed`, then with `--fix`: 11 errors, the 11 of review
  round 1 before the task, and no `REFERENT_MOVED`. The fingerprint `8a3f339d6d80` is the same
  before and after `--fix`, so the tool repaired no file.
- One `DRIFT_SUSPECT` came from this change: `docs/reviews/framework-audit-121.md` cited
  `test_render_check.py:811` for the APFS skip, which the new tests moved. At `b6362e3` that line
  is the skip. The quotation of that state takes the pin `@b6362e3`.

Files a §4.5 repair touched: `docs/reviews/framework-audit-121.md`.

After the repair, the `refs-living` step gives 0 errors in 124 documents, and `--targets-changed`
gives 11 errors and 60 warnings.

## Retro (§6)

The retro claim `framework-upgrade-render-output-pytest-figure` was taken at the start of the run.
The one question listed four candidates; the operator picked two:
- the text of `framework-upgrade` §3 step 4, which disagrees with itself on local rules (D12);
- the side effect of the bare pytest run, which this task unblocked: a test rewrote the live
  session state.

The operator then chose to fix both rather than file them (TASK D13). TASK 123 does it after the
commit of this task, with the four stages, since a curated test pins the text of §3 step 4. The rules that
§3 step 4 counts include those of `.claude/settings.local.json`. The retro filed no record.

Not picked, so recorded here only: the chain through which `svg_geometry.py` runs without a prompt,
and the findings before the task listed in review round 1.

After the retro's records, the CI steps ran once more: 17 of 17 pass. `git status` holds 20 entries,
all declared, the §4.5 repair among them. The operator commits.
