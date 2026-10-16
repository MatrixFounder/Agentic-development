# TASK 123 — `framework-upgrade` counts local allow rules and checks what a change runs; the findings that TASK 122 left open are fixed

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 123 |
| Slug | staging-rules-and-loose-ends |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | TASK 122 D13 (operator); the findings before the task that TASK 122 recorded; the operator's request of 2026-10-15 |
| Base revision | `09765e1d1379bd70eae996fe87e483ce73cf96fa` |
| Closes | none: no backlog record holds these items |
| Opens | WI-54, the residual routes of the put-back (D20) |
| Archive name | `task-123-staging-rules-and-loose-ends.md` |
| Revision | 8 |

**Request.** The operator committed and pushed TASK 122, and CI passed. They then wrote "запускай
TASK-123 и добавь еще эти 4 пункта в работу". TASK 123 holds the two items of TASK 122 D13 and
the four groups that the answer to "что осталось сделать?" listed:
- the positional-reference errors in old records;
- the test through which `svg_geometry.py` runs without a prompt, and its debug command line;
- the skill-testing example;
- the raw invisible characters of `test_ledger_hardening.py`, the JSON of `render_corpus.py`, and
  the output of the lint.

During Mode A round 2 the operator added the user's settings to the rules that step 4 counts: "Да,
и пользовательские" (D16).

**Revision 2** applied M1 to M5, m1 to m13 and N1 of Mode A round 1. **Revision 3** applies M6 to
M8 and m14 to m20 of round 2, D16, and the shape of the stage-3 patch (D17). **Revision 4** applies
L1 to L8 of round 3, which passed, with no further round, on the precedent of TASK 122.
**Revision 5** splits one sentence of the English fence of R8.2, which the register scan of the
changelog found at 36 words (PLAN G8). It also names the two skills of Problem 6 without the prefix
that resolves to nothing, as `test_skill_refs` requires of a living document (PLAN H2).
**Revision 6** applies the LOW findings of stage-2 round 1, which passed (D18). **Revision 7**
applies the findings of round 2, whose code review failed on the view that named the stash (D19).
**Revision 8** records the operator's choice after round 3, which passed: its LOW routes in the
text of R1.1 stay residuals, and WI-54 holds them (D20).

<!-- contract:problem -->

## 1. Problem

1. **Step 4 disagrees with itself on a local rule.** `framework-upgrade` §3 step 4 lists "a script
   that a committed allow rule names". Its exemption covers "test modules and fixtures that no rule
   names by path". An allow rule of the ignored `.claude/settings.local.json` names
   `tests/test_tool_runner.py`. TASK 122 D12 left the reading to the operator, and D13 counts the
   local rules. The text still says "committed". The user's `~/.claude/settings.json` also holds
   allow rules, which the session applies in this repository (§8).
2. **No step checks what newly run code writes.** TASK 122 let the bare `python3 -m pytest` collect
   again. A test that the run then reached, `tests/test_mock_agent.py`, rewrote the live
   `.agent/sessions/latest.yaml` at every allowed run. Review round 1 found it (TASK 122 F1); no
   step of the workflow asks for that check. Git ignores the session state, so `git status` does
   not show the write.
3. **`svg_geometry.py` runs without a prompt through a test.** `tests/run_tests.py`, which an allow
   rule names, runs `test_python_floor`. Its TC-04 runs `evals/grade_figures.py` under a faked
   Python 3.9.6. The grader imports five local modules before the `run_evals` whose guard stops
   it, and the lint imports a sixth (§8). Their module bodies run, so an edit of `svg_geometry.py`,
   `fidelity.py` or `stats.py` takes the four stages. The debug command line of `svg_geometry.py`
   prints its JSON with `ensure_ascii=False`.
4. **The lint prints label text raw.** Rules such as MA-LABEL-03 quote the label in their message.
   The text output then prints ESC, U+202E and U+2028 raw, and `--json` leaves U+2028 and U+202E
   raw (§8). The inventory prints label text raw in its table. Only MA-LABEL-14 escapes its
   quotation (TASK 121 D11).
5. **A lone surrogate stops a corpus render.** `evals/render_corpus.py` writes `geometry.json` with
   `json.dump(…, ensure_ascii=False)`. Written that way to a UTF-8 file, a lone surrogate raises
   `UnicodeEncodeError` (TASK 122 §8). The file also keeps non-printable characters raw.
6. **The skill-testing example fails as a script, and can send a key to the wrong server.** Its
   `__main__` names `08_agent_developer.md`, and two skills by names that add a `skill-` prefix to
   `tdd-stub-first` and `documentation-standards`. None exists, and a run ends in
   `FileNotFoundError` (§8). With only `XAI_API_KEY` set, `query_model` sends that key to the
   default `https://api.openai.com/v1` (CWE-201).
7. **Test sources hold raw invisible characters.** Lines 68 and 87 of `test_ledger_hardening.py`
   hold U+2028, U+2029, U+202E, U+2066, U+200B and U+00AD raw in string literals. Three more test
   files hold U+2028 or U+FEFF raw (§8). A reader and a diff do not show them, and U+202E reorders
   the line on screen (CVE-2021-42574).
8. **Old records hold positional references that fail.** With `--targets-changed`,
   `check_positional_refs.py` reports 11 errors whenever a change touches a file that the
   changelogs cite.
   Ten are coordinates in another repository; one quotes a line that was edited later. A scan of
   `docs` and the root finds five more of the same two classes in old records (§8).

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | §3 step 4 counts the rules of every settings file the session applies, and checks what a change runs | Y | R1.1–R1.5 | A1, A2, A10 |
| R2 | TC-04 runs no module body of the grader's local imports | Y | R2.1–R2.3 | A3 |
| R3 | The lint prints and writes no raw non-printable character | Y | R3.1–R3.5 | A4 |
| R4 | The debug command line of `svg_geometry.py` prints no raw non-printable character | Y | R4.1–R4.4 | A4, A5 |
| R5 | A corpus render writes `geometry.json` with escapes | Y | R5.1–R5.2 | A6 |
| R6 | The example runs as a script and sends no key to another server | Y | R6.1–R6.3 | A7 |
| R7 | Test sources hold no raw invisible character | Y | R7.1–R7.2 | A8 |
| R8 | The positional references of old records resolve or are pinned | Y | R8.1–R8.3 | A9 |
| R9 | Staging, evidence and records | Y | R9.1–R9.8 | A2, A10 |

## 3. Requirements

A character is **non-printable** when `str.isprintable()` returns false for it.

### R1 — `framework-upgrade` §3 step 4

- **R1.1** In `.agent/workflows/framework-upgrade.md`, §3 step 4 holds a span that runs from the
  line `   - a script that a committed allow rule names, code that script calls, and a new module it`
  to the line `` `tests/run_tests.py` is named by a rule and is not exempt.``, both included. The span
  becomes the text of the fence below, line for line. Every other line of the file stays as it is.

```text
   - a script that an allow rule names, code that script calls, and a new module it would import;
   - a permission rule, `additionalDirectories` or the permission mode, an agent's
     `permissionMode` and the `allowed-tools` of a skill or a command among them;
   - a settings key that names a command, such as `statusLine`, or sets a command's environment,
     `env`;
   - the MCP servers of `.mcp.json` or a settings file, and `enableAllProjectMcpServers`.

   The allow rules are those of `.claude/settings.json`, `.claude/settings.local.json` and the
   user's `~/.claude/settings.json`, and the `allowed-tools` of a skill or a command. A command that
   one of them approves is an allowed command, and a rule names a file also through a symbolic link
   that resolves to it. Rules that managed settings or plugins add, and the commands that the Auto
   mode classifier approves, lie outside this count; the operator answers for them. Git holds
   neither the local file nor the user's, and Claude Code adds a rule to one of them when the
   operator approves a command permanently. The run reads both when §2.2 writes the PLAN, again at
   §4.5, and again after the gates of stage 3. A rule added since the first reading that runs a
   file the change adds or edits in place, directly or through other code, stops the run for the
   operator. The audit record names each file of the change that a rule of either file runs,
   directly or through other code, and quotes no such rule.

   Test modules and fixtures that no rule names by path are exempt, and so is code that runs
   without a prompt only through them. A rule that names a directory, such as `discover -s tests`,
   names no module in it. A test module is a `test_*.py` or `conftest.py` file that no hook or
   listed script runs or imports; a fixture is a data file that a test reads.
   `tests/run_tests.py` is named by a rule and is not exempt.

   **What the change runs.** The run checks what code of the change writes when an allowed command
   runs it. That code is what the change adds or edits, test modules among them. It is also what an
   allowed command first reaches through the change, such as a test that a collection error had
   blocked. A rule with a wildcard, or one whose command runs other code from another directory,
   gives one command for each option, input or directory that reaches code the change adds or
   edits. For each command, one process lists every file and directory under the repository root,
   each regular file with its SHA-256, ignored files included and no link followed. Of `.git` it
   lists every file but `index` and those under `objects` and `logs`, and of `logs` it lists
   `refs/stash`, which holds every stash. It adds the output of `git rev-parse HEAD` and
   `git ls-files -s -v`, and lists the user's `~/.gitconfig`, `~/.config/git/config` and
   `~/.claude/settings.json`. Each git command of the check and of the put-back runs with
   `-c core.fsmonitor=false`, so that git runs no file-system monitor that the checked command
   configured. The process then runs the command as the rule approves it, with
   `PYTHONDONTWRITEBYTECODE=1` and `PYTEST_ADDOPTS=-p no:cacheprovider` in its environment, and
   lists again. The audit record names the code that wrote each difference, read from that code or
   from the command's output.
   - A difference that the command is meant to write, such as the state that `update_state.py`
     records, passes the check.
   - Any other difference that code of the change writes fails the check. Before the change lands,
     that code writes into a temporary directory, which it removes.
   - A difference that other code writes is a finding before the task.

   After the check, the run puts back each difference that the command was not meant to write. A
   difference under `.git` or in a file of the user, or a file of the first listing that the second
   lacks, stops the run. The run names each difference to the operator and runs no further git
   command. Otherwise:
   - it removes each file that the command created, and then each directory that it created;
   - it restores a tracked file that no kind of §5 step 1 declares, with
     `git restore --source=<base> --staged --worktree -- ':(literal)<path>'`, and checks that the
     file hashes as in the first listing;
   - it records a changed session state again through `update_state.py`;
   - it names every other difference to the operator, the run's own records among them.

   The check runs with the gates of §3.3, and for the code of stage 3 with the gates of stage 3,
   where a failed check is a failed gate. The audit record holds each command, with its paths
   relative to the repository root, and its result. TASK 122 unblocked the bare pytest run, and a
   test it reached rewrote the live session state.
```

- **R1.2** The new text states five things:
  - the allow rules are those of both project files, the user's `~/.claude/settings.json` and the
    `allowed-tools` of a skill or a command. A command that one of them approves is an allowed
    command, and a rule names a file also through a symbolic link (D15, D16). Managed settings,
    plugins and the Auto mode classifier lie outside this count (D18);
  - the run reads the local file and the user's at §2.2, at §4.5 and after the gates of stage 3. A
    rule added since the first reading stops the run when it runs a file that the change adds or
    edits in place (D13);
  - the audit record names the files that a rule of those two files runs, and quotes no such rule.
    It records each command of the check with paths relative to the repository root, even when
    the command's text matches a rule (D3);
  - a rule that names a directory names no module in it (D2);
  - the check of what the change runs: the commands it picks and what it lists, `.git` and three
    files of the user among it. Its git commands turn off the file-system monitor, and the run
    puts back what the command was not meant to write, or stops (D4, D18, D19).
- **R1.3** `STEP_4` of `tests/test_run_safety_rules.py` holds the new text of step 4 whole. Its
  module docstring names the two new parts: the rules of every settings file, and the check of what
  a change runs. The pin test passes against the patched workflow and fails against the base text.
- **R1.4** `System/Docs/WORKFLOWS.md`, the **Safety Protocol** list of §5, gains item 6. No other
  line changes:

```text
6. **Allowed Commands:** `framework-upgrade` §3 step 4 counts the allow rules of
   `.claude/settings.json`, `.claude/settings.local.json`, the user's `~/.claude/settings.json` and
   the `allowed-tools` of skills and commands. When an allowed command runs code of the change, the
   run lists the tree before and after one run of that command, ignored files included. A file
   that the code writes and is not meant to write fails the check. The run puts back what step 4
   lets it put back, and names every other difference to the operator.
```

- **R1.5** This run applies the text of R1.1 to itself:
  - its audit record names each file of the change that a rule of the local or the user's file
    runs; §8 lists them;
  - it reads both files again at §4.5 and after the gates of stage 3;
  - its gates run the check of R1.1 for the commands of R9.6.

### R2 — TC-04 runs no module body of the grader's local imports

- **R2.1** TC-04 of `tests/test_python_floor.py` runs the grader with a stub in `sys.modules` for
  each module that the grader imports at module level before `run_evals`, from a directory of
  `GRADER_PATH`. The test finds those modules in the grader's source, as TC-03 finds them. A stub
  is an empty module.
- **R2.2** Under the faked 3.9.6 the grader still exits 2, names itself and both versions, and
  writes nothing. At the child's exit, `sys.modules` holds no module whose file lies in a directory
  of `GRADER_PATH`, the grader aside; TC-04 asserts it from the child's report. The top of
  `run_evals.py` runs up to its guard, and the guard's exit removes that module from
  `sys.modules`.
- **R2.3** The docstring of `test_python_floor.py` states the stubs, their reason and their
  residual. The allowed runs of the test then execute none of those module bodies (TASK 123).
  TC-04 no longer checks those bodies for a write at import, which a real 3.9 would run before the
  guard; none writes or reads `sys.version_info` today. After R2, no allowed command runs
  `svg_geometry.py`, `fidelity.py` or `stats.py` but through test modules that step 4 exempts
  (§8). `mermaid_model.py`, `lint_mermaid.py` and `planarity.py` still run through the rules of the
  lint and of `plan_gantt.py --check`.

### R3 — the output of the lint

- **R3.1** `lint_mermaid.py` gains three functions, copies of those of `render_check.py`:
  - `_json_text(value, **kw)`, as `json_text` (TASK 122 R1.1);
  - `_shown(text, lines=False)`, as `_shown`: each non-printable character, a newline among them,
    takes its Python escape, and a backslash stays single (TASK 122 D5);
  - `_say(text, file=None, lines=False)`, which prints `_shown(text, lines)`.

  The lint does not import `render_check.py` (D7).
- **R3.2** The only `print` call of the lint is the one inside `_say`. Its calls print:
  - the findings of the text output, and the table of `--inventory`;
  - `--json` of the findings and of the inventory, as `_json_text(…, indent=2)`;
  - the probe line, and each usage and internal error.

  argparse prints its usage and its errors itself, and stays as it is.
- **R3.3** `_format_text` and `_format_inventory` pass each line they build through `_shown` before
  they join the lines. A newline inside a message, a path or a cell then starts no line. `main`
  passes `lines=True` only with the text of `_json_text`, `_format_text` or `_format_inventory`.
- **R3.4** `lint_text` and the messages of its findings stay as they are. The grader reads
  `Finding.message` into its reports (D6), so the escape stays in the command line. A message of
  MA-LABEL-14 is printable already, and prints as before.
- **R3.5** Printable text prints as before: Cyrillic, `→` and the backslash of a hint among it.
  `json.loads` of each JSON output equals the dictionary that `main` builds.

### R4 — the debug command line of `svg_geometry.py`

- **R4.1** `main()` of `svg_geometry.py` prints its JSON with `ensure_ascii=True` (D8). Its two
  error lines print `_escaped(str(exc))`, the escape that the file already holds (TASK 121 D11).
- **R4.2** No line of `svg_geometry.py` outside `main` changes.
- **R4.3** In `scripts/render_check.py`, the docstring of `json_text` ends with the three lines
  below. They replace lines 490 and 491, which end in "its module" and "(TASK 122 D10).". No other
  line of the file changes:

```text
    lone surrogate reaches a terminal or a file. TASK 122 left svg_geometry.py unedited for it,
    since that module's body then ran without a prompt (D10). lint_mermaid.py holds copies of this
    function and of `_shown`; a test pins each pair to one output (TASK 123)."""
```

- **R4.4** R4.1 and R4.3 change the instrument hash of `render_check.py`. Both fixtures,
  `paired-examples-geometry.json` and `references-geometry.json`, are rendered again with the
  staged `svg_geometry.py` and the patched `render_check.py` (D9). Each holds the instrument hash of
  the files after stage 3. In each, every file key and figure entry equals that of the base
  fixture; only `instruments` and `generated` differ per file.

### R5 — the metrics file of a corpus render

- **R5.1** `evals/render_corpus.py` writes `geometry.json` as `rc.json_text(geometry, indent=1)`
  and a newline. `rc` is its import of `render_check` at line 109, and the write lies below the
  guard of the file (§8). The import line of `find_renderers` and `render` stays as it is.
- **R5.2** A new check of the eval selftest, TC-ME-49, renders one run with a stand-in render. Its
  entry holds a lone surrogate, ESC and U+2028. The run writes `geometry.json` and goes on. The
  file holds no non-printable character but newlines, and `json.loads` of it equals the geometry.
  `EXPECTED_CASES` of the selftest goes from 225 to 226.

### R6 — the skill-testing example

- **R6.1** The `__main__` block of `examples/skill-testing/test_skill.py` names
  `08_developer_prompt.md` and the skills `tdd-stub-first` and `documentation-standards`.
- **R6.2** `query_model` reads its key from `OPENAI_API_KEY` only, and its server from
  `OPENAI_BASE_URL`, with the default `https://api.openai.com/v1`. No line reads `XAI_API_KEY`
  (D10). Without `OPENAI_API_KEY` the function returns the dry-run text and imports nothing. Its
  warning and the comment at the top name `OPENAI_API_KEY` and `OPENAI_BASE_URL`.
- **R6.3** `tests/test_bare_pytest.py` gains two tests. Each runs a child in which `import openai`
  fails, with no key but the one the test sets:
  - with only `XAI_API_KEY` set, `query_model` returns "Dry run complete.", which the child prints,
    and the child exits 0 without the message of a failed `import openai`;
  - run as a script from the repository root with no key, the example exits 0. Its output names
    the role file and both skill files, and holds neither "File not found" nor "Warning: Skill".

  The test of TASK 122 with `OPENAI_API_KEY` set stays and passes.

### R7 — raw invisible characters in test sources

- **R7.1** Each raw non-printable character of a string literal becomes its `\u` escape of four hex
  digits, in these files and lines:
  - `.agent/skills/run-feedback/scripts/tests/test_ledger_hardening.py`, lines 68 and 87;
  - `.agent/skills/run-feedback/scripts/tests/test_wi_tail.py`, lines 624, 625 and 636;
  - `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_lint_mermaid.py`, lines 1530 and
    1533;
  - `.agent/tools/test_task_id_tool.py`, line 301.
- **R7.2** `ast.dump` of each file equals that of its base text, so each module runs the same
  statements with the same values. Each file holds no non-printable character but newlines. The
  suite of each file passes.

### R8 — positional references in old records

- **R8.1** A coordinate in the `onchain-analytics` repository takes a pin of that repository's
  revision, as TASK 103 pinned its own with `@e95b909` (D14):
  - the coordinates of line 117 of `get-token.ts` and line 92 of `wallet-balances.ts` take
    `@77fa89c` in `CHANGELOG.md` line 1056, `CHANGELOG.ru.md` line 1093,
    `docs/reviews/framework-audit-105.md` line 65, and
    `docs/reviews/framework-audit-20260813-reference-gate-scope.md` line 46;
  - the coordinate of line 1083 of `registry.ts` takes `@e95b909` in
    `docs/plans/plan-103-referent-carrying-positional-references.md` line 195.

  In each changelog, the next line takes the word that the pin pushes past the 100th column, and no
  line count changes. In each record under `docs/`, the pinned line keeps its place and may pass the
  100th column, so that no coordinate into a record moves.
- **R8.2** Two lines quote the list that the referent rule misread, and become prose (D14):
  - `CHANGELOG.md` lines 1177 to 1179 become:

```text
comma" — which is **exactly the shape of a comma-separated list of coordinates**. So a list of two
coordinates, line 117 of `get-token.ts` and line 92 of `wallet-balances.ts`, was read as "117 quotes
the text of the second". That text is nowhere in the target, and the document was reported broken.
```

  - `CHANGELOG.ru.md` lines 1211 to 1213 become:

```text
**ровно форма перечисления координат через запятую**. Поэтому перечень двух координат, строка 117
файла `get-token.ts` и строка 92 файла `wallet-balances.ts`, читался как «117 цитирует текст второй
координаты», которого в цели нет, и верный документ объявлялся сломанным.
```

- **R8.3** A quotation of an earlier state of this repository takes the pin of the revision whose
  line it quotes:
  - `docs/reviews/review-095-independent.md:35`: `check_prompt_references.py:21@b0d78f9`;
  - `docs/reviews/vdd-adversarial-known-issues-format.md:15`: the coordinates `:51` and `:49` of
    `.agent/skills/known-issues-format/SKILL.md`, each with `@1ca49cf`.

  At each pinned revision the cited line holds the quoted text, and each revision precedes the
  commit that added its record (§8). `check_positional_refs.py --all docs .` then reports none of
  the 16 errors of R8.

### R9 — staging, evidence and records

- **R9.1** The four stages of §3 step 4 carry this change (D11). Stage 1 writes these copies. The
  stage-3 patch gives each file on the right the bytes of its copy, and stage 3 then removes the
  copy (D17):
  - `tests/staged_run_safety_rules.py` → `tests/test_run_safety_rules.py`;
  - `tests/staged_python_floor.py` → `tests/test_python_floor.py`;
  - `scripts/staged_lint_mermaid.py` → `scripts/lint_mermaid.py`;
  - `scripts/staged_svg_geometry.py` → `scripts/svg_geometry.py`;
  - `scripts/tests/staged_printed_output.py` → `scripts/tests/test_printed_output.py`, a new file;
  - `scripts/tests/fixtures/staged_paired-examples-geometry.json` →
    `paired-examples-geometry.json`;
  - `scripts/tests/fixtures/staged_references-geometry.json` → `references-geometry.json`.

  A `scripts/` path lies in `.agent/skills/mermaid-authoring-guidelines/`. The patch also carries
  R1.1 and R4.3, as texts built from the fences of this TASK. The new test module and the fixtures
  are staged because they hold to the staged code, and would fail against the base.
- **R9.2** The run edits these files in place, each for the reason given:
  - the example and `tests/test_bare_pytest.py` are test modules that no rule names by path and no
    listed script runs (R1.1);
  - the change of R7 alters nothing that runs, since `ast.dump` of each file stays as it was
    (R7.2). `test_e2e.sh`, which rules of the user's settings name, runs two of the four files
    (§8);
  - TC-04 runs `render_corpus.py` and `selftest_figure_evals.py` under a faked 3.9.6, and the guard
    of each stops it above the edited lines. No allowed command runs them otherwise (TASK 122
    R5.5);
  - the documents of R1.4, R8 and R9.5 to R9.7 hold no code.
- **R9.3** Stub first: each new test fails against the base text of the code it tests, and the
  audit record holds each red run. A staged test runs red against the base modules and green
  against the staged ones. TC-04 is the exception: its stubs make it pass against the unedited
  grader, so its red run is the base child of A3.
- **R9.4** The tests:
  - `test_printed_output.py`: the text output, `--json`, both inventory forms and the error lines
    of the lint, for a label with ESC, U+009B, U+202E, U+2028, a newline and Cyrillic. Each line
    holds no non-printable character, and each JSON reads back. The error lines include the usage
    error of `--probe` with a path, and the internal error, raised in the process by a stand-in
    failure whose message holds such text;
  - in the same file, an AST check that the only `print` call of the lint is the one in `_say`, and
    that `lines=True` goes only with the three texts of R3.3;
  - in the same file, `main()` of `svg_geometry.py` with a stand-in analysis that returns such text:
    its JSON is ASCII and reads back, and an error line holds no non-printable character;
  - in the same file, the copies of R3.1 against `render_check.py`: equal output for a string of
    every code point;
  - TC-04 of R2, the pin of R1.3, TC-ME-49 of R5.2 and the two tests of R6.3.
- **R9.5** `CHANGELOG.md` and `CHANGELOG.ru.md` get v3.43.0, titled "framework-upgrade counts local
  allow rules and checks what a change runs (TASK 123)". R1 goes under Changed, and R2 to R8 under
  Fixed.
- **R9.6** The check of R1.1 runs for these commands:
  - `python3 -m pytest`, from four directories: the repository root, the skill's directory,
    `.agent/skills/run-feedback` and `.agent/tools`. The rule names no path, so each directory
    gives other tests. The committed `python -m pytest` runs the same interpreter here (§8);
  - `python3 tests/run_tests.py` and `python3 -m unittest discover -s tests -v`;
  - the lint, once for each option or input whose code R3 edits: the text output, `--json`,
    `--inventory` and `--inventory --json` of `references/paired-examples.md`, `--probe`, `--probe`
    with a path, and a path that does not exist. No known input reaches an internal error; the
    tests of R9.4 run those lines in the process;
  - two commands that rules of the user's settings approve, given as commands of the check (D3):
    `python3 -m unittest discover -s scripts/tests` from the skill's directory, and
    `bash -x tests/test_e2e.sh` from `.agent/skills/run-feedback/scripts`. The E2E script runs from
    `tests/` too, as the same code.

  `plan_gantt.py --check` is left out: it runs `mermaid_model.py` only, which the change does not
  edit. Before stage 3 the check runs for every command but the lint. Those commands reach the
  example, `tests/test_bare_pytest.py` and the four files of R7. Through TC-04 they also run
  `render_corpus.py` and `selftest_figure_evals.py` up to their guards. With the gates of stage 3
  the check runs for every command of the list. A difference fails the check when code of the
  change writes it, and is a finding before the task otherwise (R1.1).
- **R9.7** `docs/ARCHITECTURE.md` §10.7: the bullet of TASK 122 on the escapes of the render check
  names the lint and `render_corpus.py` as well. It states that the debug command line of
  `svg_geometry.py` prints ASCII JSON.
- **R9.8** `System/Docs/SKILLS.md` is not edited: its lines 99 to 108 on
  `mermaid-authoring-guidelines` state no fact this task changes.

**Migration.** No session state, notation key or command changes. The lint's text output changes
only where it held a non-printable character, and a consumer of `--json` reads the same values.
The debug JSON of `svg_geometry.py` writes every character beyond ASCII as a `\u` escape, Cyrillic
included.

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — An agent edits `svg_geometry.py` after this task

**Precondition.** TASK 123 is committed. A task edits a function of `svg_geometry.py`.

1. The agent checks which allowed command runs the file. TC-04 stubs it, and only test modules that
   step 4 exempts import it.
2. The edit takes no stage of §3 step 4, and the fixtures are rendered again as before.

**Postcondition.** The edit lands in place, reviewed as any change.

### UC-2 — An agent lints a document whose label holds a control sequence

**Precondition.** An edge label of a figure holds ESC, U+202E and U+2028.

1. `lint_mermaid.py` reports MA-LABEL-03 with the label quoted.
2. Each of the three characters prints as its Python escape, and the finding stays on one line.

**Postcondition.** The terminal shows the escapes and runs no control sequence. `--json` holds
`\u` escapes and reads back to the same message.

### UC-3 — A change lets an allowed command reach a test that writes

**Precondition.** A change removes a collection error, so `python3 -m pytest` reaches a test that
writes the live session state.

1. The run lists the tree, runs the command, and lists the tree again.
2. The listings differ at `.agent/sessions/latest.yaml`. The run reads the test and names it as
   the writer, and the check fails.
3. The run records the session state again through `update_state.py`.
4. Before the change lands, the test writes into a temporary directory, and a second check holds
   two equal listings.

**Postcondition.** The allowed command leaves the tree as it found it.

### UC-4 — An operator with only an xAI key runs the example

**Precondition.** `XAI_API_KEY` is set; `OPENAI_API_KEY` is not.

1. `python3 examples/skill-testing/test_skill.py` builds the prompt from the role and two skills.
2. `query_model` finds no `OPENAI_API_KEY` and returns the dry run.

**Postcondition.** No key leaves the machine. The warning names the two variables that point the
example at a server.

<!-- contract:acceptance -->

## 5. Acceptance criteria

- **A1** — with the stage-3 patch applied, `tests/test_run_safety_rules.py` passes. Its staged copy
  fails against the base text of the workflow, and the audit record holds that red run.
- **A2** — the documents: `System/Docs/WORKFLOWS.md` holds item 6 as R1.4 states. The changelogs
  hold v3.43.0 (R9.5), `docs/ARCHITECTURE.md` §10.7 holds the bullet of R9.7, and
  `System/Docs/SKILLS.md` is unchanged (R9.8). The register check finds no `WARN` on an added line
  of a changed document.
- **A3** — `tests/test_python_floor.py` passes. At the exit of its TC-04 child, `sys.modules`
  holds no module whose file lies in a directory of `GRADER_PATH`, the grader aside. The base TC-04
  child holds the six modules of §8, and the audit record holds that run.
- **A4** — `test_printed_output.py` passes, and so does the full suite of the skill:
  `python3 -m pytest -p no:cacheprovider scripts/tests -q` from the skill's directory. The lint of
  a document with ESC, U+202E and U+2028 in an edge label prints no non-printable character but
  newlines, in
  each of its four outputs.
- **A5** — `test_paired_examples.py` passes after stage 3: both fixtures hold the instrument hash
  of the files. In each fixture every file key and figure entry equals that of the base fixture,
  and only `instruments` and `generated` differ per file.
- **A6** — `evals/selftest_figure_evals.py` passes with 226 cases, TC-ME-49 among them.
- **A7** — `tests/test_bare_pytest.py` passes, and the example run as a script exits 0.
- **A8** — R7.2 holds for each of the four files.
- **A9** — `check_positional_refs.py --all docs .` reports none of the 16 errors of R8.
  `--targets-changed` at §4.5 reports no error in a line that R8 names.
- **A10** — the run:
  - every step of `.github/workflows/framework-gates.yml` passes as CI runs it;
  - every path of `git status` is declared;
  - the audit record names the files of §8 that a rule of the local or the user's file runs, and
    the result of reading both files again at §4.5 (R1.5);
  - no check of R9.6 finds a difference that code of the change writes. Any other difference is
    a finding before the task, named to the operator.

<!-- contract:open-questions -->

## 6. Open questions

None.

## 7. Decisions

- **D1**, 2026-10-15, orchestrator: the scope. It holds the two items of TASK 122 D13 and the four
  groups the operator named. Two groups take more members of the same class:
  - five more positional-reference errors in old records, found by a scan of `docs` and the root;
  - three more test files with raw invisible characters, found by a scan of the tracked sources.

  Rejected: the 11 errors and one test file only, which would leave defects of the same class that
  the same scans report.
- **D2**, 2026-10-15, orchestrator: a rule that names a directory names no module in it by path.
  The local rule `ca2c33383ded254c`, unittest discovery over `tests/`, then reads as the committed
  `python3 -m pytest`, which names no path. Rejected: the reading that a directory names each
  module in it, which would stage nearly every edit of a test.
- **D3**, 2026-10-15, orchestrator: the audit record names the files of the change that a rule of
  the local or the user's file runs, and quotes no such rule. Those files hold absolute paths of
  the operator's machine, and the audit record is committed. A command of the check is recorded
  with paths relative to the repository root, even when its text matches a rule. Rejected: a copy
  of those rules in the record.
- **D4**, 2026-10-15, orchestrator: the check of what the change runs.
  - It lists the whole tree with a SHA-256 per file, ignored files included. `git status` does not
    show an ignored file, and the session state is one. Of `.git` it lists every file but `index`
    and those under `objects` and `logs`. Through `commondir`, a hook, `config` or a ref, a later
    git command runs other code or sees other work. The index changes at each `git status`, so the
    output of `git ls-files -s -v` stands in for it, beside `git rev-parse HEAD` (D18). Of `logs`
    it lists `refs/stash`, which holds every stash (D19).
  - It also lists the user's `~/.gitconfig`, `~/.config/git/config` and `~/.claude/settings.json`,
    three files outside the tree through which a later command runs code (D18, D19).
  - A rule whose command runs other code from another directory, such as `python3 -m pytest`, gives
    one command for each directory that reaches code of the change.
  - One process holds both listings in memory and runs the command between them, so a variable in
    its environment adds no text to the command. The run starts that process with a command of its
    own, which asks or which Auto mode decides. The operator approves it once, not permanently. A
    permanent approval is a new local rule, which the next reading finds (D13).
  - Neither that process nor the script of D9 runs through the local rule `881e39b164a546fa`,
    which runs standard input as Python.
  - The run attributes each difference by reading the code or the command's output. A difference
    under `.git` or in a file of the user, or a missing file, stops the run (D19). Otherwise the
    run removes what the command created and restores each tracked file that it does not declare,
    since a listing of hashes cannot restore a file. Every other difference goes to the operator.

  Rejected: `git status` alone; a check of the session state alone; flags or a variable prefix on
  the command line, which would make it another command than the rule approves.
- **D5**, 2026-10-15, orchestrator: TC-04 stubs the grader's local imports, and the grader stays
  unedited. Every committed campaign report records the SHA-256 of `grade_figures.py`, and the eval
  selftest re-derives each report (TC-ME-22). Under the fake, the module bodies run on the current
  interpreter and prove nothing about 3.9; TC-03 parses them. The residual: TC-04 no longer checks
  those bodies for a write at import. Rejected: the guard moved above the grader's imports; each
  edit of those modules staged.
- **D6**, 2026-10-15, orchestrator: the lint escapes at its command line, not in `lint_text`. The
  grader reads `Finding.message` into the problems of its reports, so an escape in the messages
  could change a re-derived report. The residual: `_shown` keeps a backslash single, so a label
  that holds the text `\x1b` prints as an escaped ESC does (TASK 122 D5). A message of MA-LABEL-14
  doubles its backslashes (TASK 121 D11), so one output can hold both forms. Rejected: an escape at
  the creation of each finding.
- **D7**, 2026-10-15, orchestrator: the lint holds its own copies of `json_text` and `_shown`. An
  import of `render_check.py` would make it and `svg_geometry.py` run under the lint's rule. TASK
  121 D11 set the precedent: two copies of `_escaped` and a test that pins them to one output.
  Rejected: the functions moved into `mermaid_model.py`, which the lint and `plan_gantt.py`
  import; that would stage `mermaid_model.py` and put `render_check.py` into the stage-3 patch.
- **D8**, 2026-10-15, orchestrator: the debug command line of `svg_geometry.py` prints ASCII JSON,
  and escapes its error lines with the `_escaped` it holds. It is a developer's tool, so Cyrillic as
  `\u` escapes costs little. The residual: `_escaped(str(exc))` doubles the backslashes that `%r`
  already wrote into the file name of an `OSError`, the doubling TASK 122 D5 rejected for the
  render check. Rejected: a third copy of `json_text`.
- **D9**, 2026-10-15, orchestrator: the fixtures are rendered again inside the change.
  - A script in the scratchpad builds the patched `render_check.py` in memory, from its base bytes
    and the fence of R4.3. It loads that text and the staged `svg_geometry.py` under their own
    names.
  - It hashes the bytes that stage 3 writes, with the algorithm of `instrument_sha256`, and writes
    no copy of a repository file. Its renders land outside the repository, as every render does.
  - The staged file and the file after the patch hold the same bytes, so the hash names the code
    that measured.
  - A fix round that changes `staged_svg_geometry.py` or the fence of R4.3 renders both fixtures
    again.

  Rejected: an instrument hash written without a render; the debug command line moved to a TASK
  124, after the operator asked for it here.
- **D10**, 2026-10-15, orchestrator: the example reads `OPENAI_API_KEY` only. An operator with an
  xAI key sets it there, with `OPENAI_BASE_URL` naming the xAI server. Rejected: a fixed xAI server
  for `XAI_API_KEY`, which would also need a model name for that server.
- **D11**, 2026-10-15, orchestrator: the staging of R9.1. Three files are code that an allowed
  command runs at the base: the pin test, `test_python_floor.py` and the lint. `svg_geometry.py`
  joins them through TC-04 at the base. The new test module and both fixtures follow the code they
  hold to. The patch carries the workflow text and the docstring of `render_check.py` as texts.
- **D12**, 2026-10-15, orchestrator: the version is v3.43.0. R1 changes a rule of a workflow, as
  v3.41.0 did.
- **D13**, 2026-10-15, orchestrator: the run reads the local file and the user's again at §4.5, and
  after the gates of stage 3. Claude Code writes an approval that the operator makes permanent into
  one of them and applies it at once, so a rule can appear during the gates. Stage 3 starts the
  check's process after §4.5. Rejected: one reading at §2.2.
- **D14**, 2026-10-15, orchestrator: the references of R8.
  - A coordinate in another repository takes that repository's revision as its pin. TASK 103 did so
    with `@e95b909` (`docs/plans/plan-103-referent-carrying-positional-references.md`, lines 195 to
    197).
  - A pin keeps the coordinate and states its revision. The CI comment on the living corpus names
    that form for a record (`framework-gates.yml`, lines 203 to 205). `framework-audit-105.md:66`
    called the coordinate of review-095 "reported, not rewritten"; a pin rewrites no number.
  - The two changelog passages that quote the misread list become prose. A pin inside the
    quotation would change the text that the rule misread.

  Rejected: prose for every external coordinate, which drops the revision that makes it true.
- **D15**, 2026-10-15, orchestrator: the `allowed-tools` of a skill or a command count among the
  allow rules. The list of step 4 already names them as permission rules, and a command they
  approve runs without a prompt. None exists in the repository today. Rejected: the settings files
  alone, which would narrow the rule.
- **D16**, 2026-10-15, operator: the allow rules of the user's `~/.claude/settings.json` count as
  those of the local file do. The session applies them in this repository. A relative rule matches
  its command text in any directory, and some rules name files of this repository through the
  symbolic links of another one (§8). Answer "Да, и пользовательские". Rejected: the two project
  files only, with the user's rules left to the operator.
- **D17**, 2026-10-15, orchestrator: the stage-3 patch gives each file of R9.1 the bytes of its copy
  and leaves the copies out. The audit record holds the SHA-256 of each copy. Stage 3 removes each
  copy once its file hashes to it. On a failure the run writes back only the copies that stage 3
  removed, each from its file, and only when that file still hashes to the copy; then
  `git apply -R`. A patch that deleted the copies would hold each text a second time, over 16,000
  lines with the two fixtures. Rejected: the deletions inside the patch, as TASK 120 and TASK 121
  did.

- **D18**, 2026-10-15, orchestrator: fix round 1 of stage 2. Both reviews of round 1 passed, and
  the run applies their LOW findings before round 2, on the precedent of TASK 122:
  - the check lists every file of `.git` but `index`, `objects` and `logs`, the output of three git
    commands, and the user's `~/.gitconfig` and `~/.claude/settings.json` (S1-1, S1-4);
  - the put-back restores the index too, takes a path literally, and checks the restored hash
    (S1-3); item 6 of `WORKFLOWS.md` no longer claims that the run puts every file back;
  - managed settings, plugins and the Auto mode classifier are named as outside the count (S1-2);
  - the records name a rule by its class and hash, and quote none (S1-5);
  - a test of the inventory with a newline in a path, and an AST check of every call (R1-1, R1-2);
  - the changelogs match the workflow's stop rule and name argparse as the residual of the lint
    (R1-4, R1-5).

  Rejected: the round's LOW findings left as residuals, since the check that R1.1 adds would then
  miss the route through `commondir` that the security audit showed.
- **D19**, 2026-10-15, orchestrator: fix round 2 of stage 2. Its code review failed on R2-1, and
  its security audit passed with four LOW findings. The run applies all of them before round 3:
  - the listing drops the third git view of D18. Its command matches a pattern of
    `tests/test_git_rollback_contract.py`, which allows that command in three sentences of the
    workflow only, so the patched workflow failed that test (R2-1). Of `logs` the listing takes
    `refs/stash` instead, which holds every stash; the ref `refs/stash` was listed already;
  - each git command of the check and of the put-back runs with `-c core.fsmonitor=false`. A
    difference under `.git` or in a file of the user, or a file that the second listing lacks,
    stops the run before any further git command and before any removal (R2-4, S2-1). A created
    file that the put-back removed could have been the only copy of a moved one;
  - the listing holds each directory and hashes only regular files, so a FIFO under `.git` no
    longer blocks it (R2-5, S2-3). The put-back removes each directory that the command created;
  - the listing takes `~/.config/git/config` too, and §9 names the files of the user that it
    leaves out (R2-7);
  - the changelogs and item 6 state the put-back as step 4 does (R2-3, S2-4);
  - the audit record names the user's rules by hash, as D3 asks (R2-2), and the PLAN cites the
    current revision of this TASK (R2-6);
  - PLAN H4 runs the gates on the patched tree, in a throwaway worktree outside the repository.
    H2 runs them on the unpatched tree, which is why it missed R2-1.

  Rejected: the view kept under a name without the matched words, a second listing of what the
  file `logs/refs/stash` holds.
- **D20**, 2026-10-15, operator: round 3 of stage 2 passed, and each of its LOW findings is a route
  of a class that an earlier round fixed. Those in the text of R1.1 stay residuals of §9, and
  WI-54 holds them: S3-1, S3-2, R3-2, and the wordings of R3-4 and I-2. No fourth round runs. The
  run fixes the findings in its own records and tools: the audit's account of H3, `h3.sh`,
  `listing.py`, D4 and §9 (R3-1, R3-3, R3-5, S3-3, I-3). Answer "Остаток + backlog". Rejected: a
  fourth round, since each round of this review found a narrower route of one class (WI-48).

## 8. Measurements of this run

- Under a faked 3.9.6, the grader prints "grade_figures.py needs Python 3.11 or newer" and exits
  2. It has loaded six local modules by then: `fidelity`, `lint_mermaid`, `mermaid_model`,
  `planarity`, `stats` and `svg_geometry`. The lint imports `planarity`. `run_evals` is not in
  `sys.modules` after its guard raises, and neither is the grader that `runpy` ran.
- `render_corpus.py` holds its guard at line 97. Its imports follow at lines 107 to 111, the import
  of `render_check` as `rc` at line 109. The write of `geometry.json` is at lines 470 to 473.
  `EXPECTED_CASES` of the selftest is 225. No test of the skill's `scripts/tests` imports
  `render_corpus.py` or the selftest.
- A document whose edge label holds ESC, U+202E and U+2028 gives MA-LABEL-03. The text output holds
  the three characters raw, and `--json` holds U+2028 and U+202E raw. With the same characters in a
  node label, the inventory table holds all three raw. `references/paired-examples.md` gives 21
  expected findings and no other.
- `python3 examples/skill-testing/test_skill.py`, with no key, exits 1 with
  `FileNotFoundError: File not found: 08_agent_developer.md`.
  `System/Agents/08_developer_prompt.md`, `.agent/skills/tdd-stub-first/SKILL.md` and
  `.agent/skills/documentation-standards/SKILL.md` exist.
- Tracked sources with raw non-printable characters, newlines and tabs aside:
  - `test_ledger_hardening.py`, lines 68 and 87: U+2028, U+2029, U+202E, U+2066, U+200B, U+00AD;
  - `test_wi_tail.py`, lines 624, 625 and 636: U+2028;
  - `test_lint_mermaid.py`, lines 1530 and 1533: U+FEFF;
  - `test_task_id_tool.py`, line 301: U+FEFF;
  - `scan_register.py`, line 744: U+200D, in a pattern; an allow rule names the script (§9);
  - two Markdown task files and one captured fixture, as data (§9).
- `check_positional_refs.py --all docs .` reports 23 errors:
  - the 11 of R8 that `--targets-changed` reports: eight in the changelogs, two in
    `framework-audit-105.md:65`, and `review-095-independent.md:35`;
  - five more in old records: `framework-audit-20260813-reference-gate-scope.md:46` twice,
    `plan-103-referent-carrying-positional-references.md:195`, and
    `vdd-adversarial-known-issues-format.md:15` twice;
  - four in examples of two skills, and three coordinates of the `docs/TASK.md` slot (§9).
- The pins of R8:
  - in `onchain-analytics` at `77fa89c`, line 117 of `packages/mcp-server/src/tools/get-token.ts`
    and line 92 of `wallet-balances.ts` hold
    `const outcome = await resolveCapability(ctx.registry, …`. That commit added the task document
    that cites both lines;
  - at `b0d78f9`, line 21 of `System/scripts/check_prompt_references.py` is
    `AGENT_REF_RE = re.compile(…)`, the line `review-095-independent.md:35` quotes. `b0d78f9` is
    an ancestor of `14799d3`, the commit that added the review, where that line is a comment;
  - at `1ca49cf`, lines 49 and 51 of `.agent/skills/known-issues-format/SKILL.md` hold the two
    glosses that `vdd-adversarial-known-issues-format.md:15` quotes. `1ca49cf` is the parent of
    `4f11f71`, the commit that added the review.
- `.claude/settings.local.json` names these files of the repository: `run_audit.py` of
  `security-audit`, `validate_skill.py`, `analyze_gaps.py`, `task_id_tool.py`, and four test
  modules of `tests/`, none of which this task edits. Its rule `ca2c33383ded254c`, unittest
  discovery over `tests/`, runs these files of the change:
  - `tests/test_run_safety_rules.py`, `tests/test_python_floor.py` and `tests/test_bare_pytest.py`;
  - the example, through `tests/test_bare_pytest.py`;
  - `lint_mermaid.py`, through `tests/test_mermaid_wiring.py`;
  - `render_corpus.py` and `selftest_figure_evals.py` up to their guards, through TC-04;
  - at the base, `svg_geometry.py`, through TC-04.
- The user's `~/.claude/settings.json` holds 326 allow rules, and none names a file this task
  edits. These of them reach the repository:
  - two rules, `fcf7ae83aa61d9ee` and `3c013025af0d911c`, run
    `.agent/skills/run-feedback/scripts/tests/test_e2e.sh` from its directories. It runs that
    skill's tests, `test_ledger_hardening.py` and `test_wi_tail.py` among them;
  - the rule `9fa5cad71668c6f7` runs unittest discovery over the `scripts/tests` of the directory it
    runs in. In `mermaid-authoring-guidelines`, the files of this change among them are
    `test_lint_mermaid.py` and, after stage 3, `test_printed_output.py`. Through them it runs the
    lint, `svg_geometry.py` and `render_check.py`;
  - one rule names `validate.py` of `skill-spec-validator`;
  - rules with a path into `Universal-skills` run this repository's `task_id_tool.py` and
    `update_state.py`, whose directories that repository links here;
  - two rules, `89216e2cf09753da` and `aa8ebef8166f2dac`, run any code with this repository's
    `.venv`, and two, `1906407db7c8843f` and `9b7c28a93551887e`, run a git subcommand on any
    arguments (§9).

  A rule is named here by the first 16 hex digits of the SHA-256 of its text (D3).
- A bare `python3 -m pytest --co` collects 714 tests from 40 files, all in `tests/`. pytest does not
  enter a directory whose name starts with a dot, such as `.agent`. The same command from
  `.agent/tools` or from a skill's directory collects the tests there. `tests/conftest.py` removes
  stale entries of `tests/.scratch/` at the start of a pytest run. `python` and `python3` are the
  same pyenv shim here, at Python 3.14.8. No managed settings file exists on this machine.

<!-- contract:out-of-scope -->

## 9. Out of scope

- The coordinates in the examples of two skills: `documentation-standards/SKILL.md` lines 80 and
  81, and `skill-adversarial-performance/SKILL.md` lines 94 and 116. They show a reader the form of
  a reference.
- The coordinates of the `docs/TASK.md` slot in `docs/design/095_workflow_loop_contract.md`,
  `review-095-rev5-adversarial.md` and the ledger record ARC-11. They fail only while the slot is
  empty, and a ledger record is data.
- The raw U+200D in a pattern of `scan_register.py`, which an allow rule names. The emoji of two
  task files and the captured U+2028 of an `ab-corpus` fixture are data.
- Rules that run whatever code their command line or standard input holds, and name no file: the
  local rule `881e39b164a546fa`, which runs standard input as Python, and the user's rules
  `89216e2cf09753da` and `aa8ebef8166f2dac`. One of the user's two git rules can set a command that
  a later `git status` runs, and the other can discard work. Step 4 stages nothing for them;
  whether to keep them is the operator's call.
- Rules that managed settings or plugins add, and commands that the Auto mode classifier approves.
  No managed settings exist on this machine; the user's settings hold an allow list for the
  classifier, and plugin commands carry `allowed-tools` (D18).
- `tests/test_script_guards.py` checks the scripts that committed rules run, and not those of the
  local or the user's rules.
- Writes outside the repository, in `$TMPDIR` and in `$HOME`, but the three files of the user that
  the check lists (D18, D19). A later command can also run code through `~/.claude.json`,
  `~/.claude/agents/`, `~/.claude/skills/`, the git configuration of the system, and one under a
  `$XDG_CONFIG_HOME` other than `~/.config`, none of which the check lists. A child process that
  writes after the second listing, and code that behaves otherwise under the two variables of the
  check, also pass it unseen.
- The routes of the put-back that round 3 of stage 2 found, which WI-54 holds (D20):
  - a created file can hold the only copy of a changed file, which the put-back then removes
    (S3-1);
  - a created link to a directory can read as a directory, and the text does not say how the
    put-back removes a file or a directory (S3-2);
  - the text does not say that the check hashes what a linked user file holds (R3-2);
  - the restore command omits `-c core.fsmonitor=false`, and the text does not say that a file
    that hashes otherwise after the restore stops the run (R3-4, I-2).
- From TASK 122 §9: the mock of `tests/test_mock_agent.py` runs `python3` from PATH and sleeps 5 s;
  `measure_text.mjs` joins a label's lines with no separator. The KaTeX advisory of the renderer
  lockfiles is WI-41.
