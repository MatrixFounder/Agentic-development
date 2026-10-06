# TASK 112 — Safe commands that admit no write: an archive script and closed patterns

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 112 |
| Slug | safe-commands-that-admit-no-write |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | WI-35; the operator's request of 2026-10-06 (D1) |
| Base revision | `eb7248f8027e64cb10aaa20511a4f7b519151117` |
| Closes | WI-35 |
| Archive name | `task-112-safe-commands-that-admit-no-write.md` |
| Revision | 7: Mode A rounds 1, 2; D4 per the operator; Mode B gaps; stage-2 fix rounds 1–3 |

**Records.**

- [WI-35](backlog/wi-35-safe-command-patterns-that-still-admit-a-write-or-a-program.md)
- [TASK 111](tasks/task-111-checks-that-cover-what-they-claim.md), decisions D13 and D14

<!-- contract:problem -->

## 1. Problem

WI-35 lists allow rules and safe-command patterns that admit more than their purpose. Every fact
below was measured on 2026-10-06 at the base revision.

**Committed Claude Code rules (`.claude/settings.json`).**

- `Bash(mv docs/TASK.md docs/tasks/*)` and `Bash(mv docs/PLAN.md docs/plans/*)` match any text
  after the prefix: `mv docs/TASK.md docs/tasks/../../x` and extra source operands.
- `Bash(mkdir -p docs/*)`, `Bash(mkdir -p .agent/*)` and `Bash(mkdir -p tests/*)` admit a second
  operand anywhere: `mkdir -p docs/x /any/dir`.
- `Bash(file *)` admits `file -C` and its abbreviation `file --co`. Measured: `file --co` in the
  repository root wrote a 7 MB `magic.mgc` (file 5.41).
- `rebase_links.py` rewrites in place every file operand, wherever it lies.
- `init_skill.py` creates a skill directory at any `--path`, or at a path-shaped name.

**Patterns of `skill-safe-commands`, every vendor.**

- `rg --pre <program>` runs the program on each file; measured with ripgrep 14.1.1.
  `rg --hostname-bin <program>` runs a program too. ripgrep 14.1.1 rejects abbreviated long
  options (`--pr`, `--hostname-b`), measured.
- `fd -x` and `fd -X` (`--exec`, `--exec-batch`) run a program on the matches.
- `^cd\s+\.agent/tools\s+&&\s+python` and `^python3?\s+-c\s+'from\s+scripts\.tool_runner` admit
  any text after the prefix.
- The symlink-aware patterns `^rg\s+(--follow|-L)` and `^fd\s+-[a-zA-Z]*L` match before any
  exclusion: `rg -L --pre x` matches.
- The command table and the patterns list different commands. §Implementation Guidelines step 1
  accepts a match on either.
- The skill's Antigravity list holds `rg`, `fd`, `ls -L`, `rg --follow` and `fd -L`; the READMEs'
  lists do not.
- Troubleshooting item 2 suggests shortening an entry to `mv` alone.

**The Antigravity matcher.** antigravity.google/docs/permissions, fetched 2026-10-06:

- "Matches by exact word or token prefix literally by default."
- "Standard shell composition still prefix-matches normally: pipelines, `&&`/`||`/`;` chains,
  quoted literals, plain `$VAR` arguments, simple file redirects, …"
- Command or process substitution, among other constructs, "disables prefix matching for the
  entire command line".

An entry `ls` therefore does not admit `lsof`. An entry admits a simple file redirect, which
writes.

**Claude Code redirects.** code.claude.com/docs/en/permissions, § Redirections, fetched
2026-10-06: "When a command redirects output or input, Claude Code checks the redirect target
against your file rules as if Claude wrote or read that file directly." The page does not state
whether an allow rule approves a simple command that carries a command substitution. Its list of
built-in read-only commands holds neither `test` nor `mkdir`.

**Related checks.**

- `run_external_tools` runs `yarn audit` in the scanned root
  (`.agent/skills/security-audit/scripts/audit/external.py:54@eb7248f` `run_command(["yarn", "audit"]`).
  Yarn reads `.yarnrc` and `.yarnrc.yml` there; `yarnPath` in `.yarnrc.yml` names a JavaScript
  file that yarn executes.
- `full-robust` §3 gates on "the automated scan exits clean". `run_audit.py` exits 0 unless
  `--fail-on` is given, and this repository's scan always reports findings.
- `tool_runner.run_tests` accepts any arguments after `pytest`, `python -m pytest`, `npm test`,
  `npx jest` and `cargo test` (`System/scripts/tool_runner.py:49@eb7248f` `_is_allowed_test_command`).
  `System/Docs/ORCHESTRATOR.md` lists the same five commands.

**Test pins.**

- `tests/test_committed_settings.py` reads table rows that start with `| **` only, fences opened
  with three backticks and no info string after the language, and the `python` interpreter only.
  An added pattern line passes.
- `tests/test_run_safety_rules.py` checks each pointer as a substring, so a sentence appended
  after it passes. The step-4 pin ends at the next numbered step, so an added step 5 passes.

**`framework-upgrade` §3 step 4.**

- Its list does not name a script that a committed allow rule runs. TASK 111 edited
  `tests/run_tests.py` in place, and `Bash(python3 tests/run_tests.py)` runs it.
- The narrowing check omits code that a hook's script calls and a new module it would import.
- Both Failure bullets apply when the security audit is `INCOMPLETE` and the code review rejects.
- Stage 2 reads "blocks the registration until the operator decides"; `security-audit` §6.2
  re-runs the part once first.
- "audit" names the audit record and the security audit in adjacent sentences.
- "the registered files" reads as the settings files only.

**Archiving.** Step 5 of `skill-archive-task` guards the move with `test -e`. No committed rule
approves `test`, and Claude Code does not list it as read-only.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Verified by |
| :--- | :--- | :--- | :--- | :--- |
| R1 | An archive script moves TASK and PLAN; one allow rule names it | Y | R1.1–R1.8 | A1, A2 |
| R2 | The committed allow list admits no write outside its purpose | Y | R2.1–R2.4 | A1, A3 |
| R3 | `skill-safe-commands` patterns, table and vendor lists agree and exclude program options | Y | R3.1–R3.9 | A1, A3 |
| R4 | Allowed framework scripts write inside the working directory only | Y | R4.1–R4.3 | A1, A4 |
| R5 | The related checks: `yarn audit`, the `full-robust` gate, `run_tests` | Y | R5.1–R5.3 | A1, A5 |
| R6 | The test pins read every spelling | Y | R6.1–R6.5 | A3, A6 |
| R7 | `framework-upgrade` §3 step 4 and the auditor wording | Y | R7.1–R7.4 | A6 |
| R8 | Records, versions, documents and work-items | Y | R8.1–R8.6 | A7, A8 |

### 2.1 Sub-features

**The archive script (R1).**

- **R1.1** `.agent/tools/archive_move.py` takes exactly two operands. It accepts two pairs only:
  - `docs/TASK.md` and `docs/tasks/task-<ID>-<slug>.md`;
  - `docs/PLAN.md` and `docs/plans/plan-<ID>-<slug>.md`.

  `<ID>` matches `[0-9]{3,}` and `<slug>` matches `[a-z0-9]+(-[a-z0-9]+)*`, the shapes
  `task_id_tool.py` produces. The operands are compared as text; `./`, `..`, an absolute path and
  any other directory are refused with exit 1.
- **R1.2** The script refuses, with exit 1 and no change on disk:
  - an operand pair of another shape (R1.1);
  - a source that is absent, not a regular file, a symbolic link, or a file with more than one
    hard link;
  - `docs` or the destination directory when it is a symbolic link or not a directory;
  - a destination that exists, a dangling symbolic link included.

  A wrong operand count, or an operand that starts with `-`, exits 2. Exit 0 means moved. The
  script checks the operands and the source before it creates a directory. Any other `OSError`,
  such as an overlong name, is a refusal too: exit 1, a JSON error, and no change on disk.
- **R1.3** The script works through directory descriptors. It opens `docs` and the destination
  directory with `O_DIRECTORY | O_NOFOLLOW`, and names every file relative to them.
  - It creates `docs/tasks` or `docs/plans` when it is absent.
  - It moves by `os.link` and `os.unlink` on those descriptors, without following links.
  - After the link, the destination must be a regular file with the source's inode and two hard
    links; otherwise the script removes it and exits 1.
  - Where the file system refuses the hard link, it opens the source with
    `O_RDONLY | O_NOFOLLOW`, checks it with `fstat` as R1.2 does, and copies it into a file
    created with `O_CREAT | O_EXCL | O_NOFOLLOW`. Then it removes the source.
  - Any failure after the destination exists removes the destination and exits 1; the source
    stays.
  - Removing the source can fail while the script cannot confirm that the source still holds the
    moved file. Then it keeps the archive, and its error says so. This is the one exit 1 that
    leaves a change on disk.
  - An existing destination is never overwritten.

  A platform without `dir_fd` support for these calls exits 2.
- **R1.4** The script prints one JSON object: `{"ok": true, ...}` on stdout, or
  `{"ok": false, "error": ...}` on stderr.
- **R1.5** `skill-archive-task` calls the script.
  - Step 5 and Step 7.6 run it; a non-zero exit means STOP and report.
  - Step 7.3 and Step 7.5 state that the script creates the directory and refuses an existing
    destination.
  - Step 6 and Step 7.7 drop "retry mv": a failed move is reported, not retried.
  - No shell block of the skill runs `mv`, `test` or `mkdir`.
  - Its Example Flow, Edge Cases, Safe Commands and Safety Boundaries follow.
- **R1.6** `artifact-management` names the script where it lists the archiving commands.
- **R1.8** Run as a script, it removes its own directory from `sys.path` before it imports a
  module, so a module planted beside it is never imported. A test that loads it keeps its path.
- **R1.7** `archive_move.py` is written at its final name: no rule names it before stage 3. No
  safe-command pattern, table row, Antigravity entry or vendor prompt names it before stage 3
  either; those land in the stage-3 edit with the rule.

**The committed settings (R2).**

- **R2.1** `.claude/settings.json` adds one rule, `Bash(python3 .agent/tools/archive_move.py *)`,
  and drops the two `mv` rules. This is the registration of §3 step 4 (stages 1 to 4).
- **R2.2** `Bash(mkdir -p docs/tasks)`, `Bash(mkdir -p docs/plans)` and
  `Bash(mkdir -p docs/architectures)` replace the three `mkdir` wildcards.
- **R2.3** `Bash(file *)` leaves. Claude Code's built-in read-only check analyses `file` on its
  own (permissions page, § Read-only commands).
- **R2.4** R2.2 and R2.3 only narrow. They land before stage 3 after the narrowing check of §3
  step 4; the audit record holds its output. Appendix A lists the 44 rules that result.

**The safe-command patterns (R3).**

- **R3.1** `file` leaves the table, the patterns and every vendor list.

  **Why.** `file` accepts abbreviated long options (`--co` for `--compile`), and `-C` combines with
  other short options. An exclusion pattern would have to model that parser.
- **R3.2** `rg` and `fd` leave the general read-only pattern. A short-option cluster is a `-`
  followed by characters other than `-` and whitespace, digits included. One pattern each excludes the
  options that run a program, wherever they stand in the command:
  - `rg`: `--pre` and `--hostname-bin`, with `=` or a space;
  - `fd`: every long option that starts with `--exe` (`--exec`, `--exec-batch` and their
    abbreviations), and `x` or `X` in any short-option cluster.

  The symlink-aware lines for `rg` and `fd` leave the patterns; the `rg` and `fd` patterns cover
  `-L` and `--follow`.

  **Why.** fd's handling of abbreviated long options was not measured; `--exe` covers every
  unambiguous abbreviation of the two options.
- **R3.3** The archiving pattern names the script:
  `^python3\s+\.agent/tools/archive_move\.py(\s|$)`. The `mkdir` pattern names the three
  directories of R2.2 and ends there.
- **R3.4** The two open-ended patterns of `cd .agent/tools && python` and
  `python3 -c 'from scripts.tool_runner` leave.
- **R3.5** The table names the same commands as the patterns.
  - Each command of the table matches a pattern, and each pattern matches a command of the table.
    The **Tool calls** row names native tools, not shell commands, and takes no part.
  - §Implementation Guidelines step 1 decides by the patterns; the table approves nothing alone.
  - The table gains the two eval scripts the patterns already hold.
- **R3.6** The Antigravity list of the skill and of both READMEs is one list:
  `ls,cat,head,tail,grep,wc,stat,du,df,git status,python3 .agent/tools/archive_move.py`.
  The note states the matcher as quoted in §1, and that an entry admits a simple file redirect.
- **R3.9** The patterns' lookaheads match across a line break. On the agent's side a command is
  not safe when it has a line continuation, `$'…'` or `$"…"` quoting, a parameter or brace
  expansion, or, for `rg`, `fd` and `git`, an unquoted glob.
- **R3.7** Troubleshooting item 2 states that a bare command entry, such as `mv`, admits every
  form of that command, and drops the advice to shorten an entry.

**The framework scripts (R4).**

- **R4.1** In R4 the working directory is `os.getcwd()`. `rebase_links.py` `_main` refuses a file
  operand that:
  - lies outside the working directory by its absolute path, normalised without resolving links;
  - holds a `.git` path segment in any letter case;
  - lies under an existing directory that is the working directory's `.git`;
  - lies, by file identity, under the repository's git directory: the `.git` of the working
    directory or of its nearest ancestor that has one, or the directory a `.git` file names, and
    its common directory;
  - is a symbolic link, or a file with more than one hard link.

  A refusal exits 2 and writes nothing. `rebase_file()` keeps its behaviour:
  `archive_protocol.py` calls it with temporary paths. The CLI tests of
  `.agent/tools/test_rebase_links.py` run with their temporary root as the working directory.
- **R4.2** `init_skill.py` refuses a skill directory that lies outside the working directory by its
  absolute path, normalised without resolving links, or that lies under `.git` as R4.1 states. This
  covers `--path` and a path-shaped name. A refusal exits 1 and creates nothing. The guard lives in
  `init_skill.py`; `skill_utils.py`, which the registered hook's `validate_skill.py` imports, stays
  unchanged.

  **Why.** In a consumer project `.agent/skills` can be a symbolic link into the framework. A test
  on resolved paths would refuse the default target there.
- **R4.3** The new code of R4.1 and R4.2 is written under a new name first:
  `.agent/tools/rebase_links_next.py` and `.agent/skills/skill-creator/scripts/init_skill_next.py`.
  Stage 3 copies each over its original, removes the copy, and points the guard tests at the
  originals (R7.1).
- **R4.4** The registration text for `tests/run_tests.py`, which a rule names (D4): stage 3
  appends to `CURATED_UNITTEST_MODULES`, after `"test_run_safety_rules",`, this comment and these
  two entries, and changes nothing else in the file:

  ```python
      # TASK 112 — the archive script and the guards of the scripts that allow rules run (WI-35).
      "test_archive_move",
      "test_script_guards",
  ```

**The related checks (R5).**

- **R5.1** `run_external_tools` runs `yarn audit` in a temporary directory outside the scanned
  root that holds copies of the root `yarn.lock` and `package.json` only. The copy of
  `package.json` keeps only `name`, `version`, `private`, `workspaces`, `resolutions` and the four
  dependency fields, so neither `packageManager` nor `devEngines` reaches a corepack `yarn` shim.
  - Each of the two is a regular file and not a symbolic link. A root that fails this runs no
    `yarn audit` and prints a skip line, as for npm (TASK 111 R5.6).
  - The gate on `"javascript" in types` stays (TC-Y3).
- **R5.2** `full-robust` §3 gates on a scan that ran to completion: `scan_status` is `clean` or
  `findings`. The manual review rules on each CRITICAL or HIGH scan hit, and the findings table
  holds no CRITICAL or HIGH finding. `NOT_RUN` still fails the gate.
- **R5.3** `run_tests` accepts these commands, whole: `pytest`, `pytest -q`,
  `pytest -q --tb=short` (its default), `python -m pytest`, `python3 -m pytest`, `npm test`,
  `cargo test`. `npx jest` leaves. These state the same set: `System/Docs/ORCHESTRATOR.md`, the
  `run_tests` description of `.agent/tools/schemas.py`, and the `run_tests` row of
  `docs/ARCHITECTURE.md` § Available Tools.

**The test pins (R6).**

- **R6.1** `tests/test_committed_settings.py` reads:
  - every line of the command table, whatever its first cell;
  - every fence, opened with three or more backticks or tildes, with any info string. A shell
    fence is one whose first info word is `bash`, `sh`, `shell`, `zsh` or `console`;
  - the info-word sequence of every fence of `skill-archive-task` and of `skill-safe-commands`,
    pinned whole, so an added or relabelled fence fails;
  - the whole pattern block, line by line;
  - the command name of every allow rule, against a fixed set.
- **R6.2** TC-S7 follows the archive commands of `skill-archive-task` to the script: no part is
  exempt, no part runs `mv` or `test`, and both pairs of R1.1 are present.
- **R6.3** `tests/test_run_safety_rules.py` pins step 4 up to the end of §3, and each pointer as
  the whole paragraph or list item that holds it.
- **R6.4** New test modules join `CURATED_UNITTEST_MODULES` of `tests/run_tests.py` in the stage-3
  edit, as R4.4 states (D4). Until then they run as named modules.
- **R6.5** TC-S1, TC-S7 and the retargeting of the TC-G constants land with stage 3.

**Step 4 and the wording (R7).**

- **R7.1** `framework-upgrade` §3 step 4:
  - its list names a script that a committed allow rule names, code that script calls, and a new
    module it would import;
  - test modules and fixtures that no rule names by path are exempt (D4 defines both terms);
  - code that runs without a prompt only through them is exempt too;
  - `tests/run_tests.py` is named by a rule and is not exempt;
  - the hook bullet and the narrowing check name code the script calls and a new module;
  - stage 1 edits code of the list under a new name;
  - stage 2: an `INCOMPLETE` security audit re-runs once under `security-audit` §6.2, then the
    operator decides;
  - "audit record" names the file `docs/reviews/framework-audit-<ID>.md`, "security audit" the
    review;
  - the restore names every file of stage 3's edit;
  - the first Failure bullet applies when an `INCOMPLETE` security audit is the only failure.
- **R7.2** The bold lead of the auditor wrapper's bullet is one short sentence.
- **R7.3** Prose lines that TASK 111 added and that exceed 100 characters are wrapped in the
  files that wrap at 100: `security-audit/SKILL.md`, `.agent/workflows/security-audit.md`,
  `System/Agents/10_security_auditor.md`. Tables, fences, ledger index lines and files written one
  line per item keep their form.
- **R7.4** TASK 111 R7.1 keeps its text: an archived task is not edited.

**Records (R8).**

- **R8.1** Versions:
  - `skill-safe-commands` 1.3 → 1.4;
  - `skill-archive-task` 2.0 → 2.1;
  - `artifact-management` 1.4 → 1.5;
  - `skill-creator` 2.4 → 2.5;
  - `skill-phase-context` 1.2 → 1.3;
  - `security-audit` 3.10 → 3.11, in each place that quotes 3.10 (TASK 111 R6.1), including
    `System/Docs/SKILLS.md` and `System/Docs/VDD.md`.
- **R8.2** `CHANGELOG.md` and `CHANGELOG.ru.md` carry v3.37.0 with two migration items:
  - a consumer project whose copied `settings.json` holds the `mv`, `mkdir` or `file` rules of
    v3.36.0 replaces them as Appendix A does;
  - a project that copied the patterns or the Antigravity list into `.cursorrules`, `AGENTS.md`
    or the IDE settings replaces them with those of v3.37.0.
- **R8.3** `docs/ARCHITECTURE.md` states, beside its note on the committed allow list, that
  archiving runs through `archive_move.py`.
- **R8.4** These name the archive script where they name `mv` as an auto-run command:
  `AGENTS.md`, `GEMINI.md`, `System/Docs/SKILL_TIERS.md` and `skill-phase-context`.
- **R8.5** WI-35 closes `done`; its index line moves to `## Closed`.
- **R8.6** Two work-items are filed `open`:
  - WI-36: check whether a Claude Code allow rule approves a simple command that carries a
    command substitution;
  - WI-37: external scanners that run the scanned project's code or configuration: `cargo clippy`
    build scripts, `slither` through the project's build framework, `pip-audit` building a source
    distribution, and a yarn shim that honours `packageManager`.

<!-- contract:use-cases -->

## 3. Use Cases

| UC | Actor | Precondition | Main scenario | Alternative | Postcondition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| UC-1 archive | orchestrator | `docs/TASK.md` and `docs/PLAN.md` exist | the script moves each, no prompt | the destination exists: exit 1, no move | TASK and PLAN archived as a pair |
| UC-2 bad operand | agent | a destination outside `docs/tasks/` | the script refuses with exit 1 | a link in place of `docs/tasks`: refused | no file written |
| UC-3 read command | agent on any vendor | `rg -L pattern` | a pattern matches; auto-run | `rg --pre x`: no pattern matches; asks | no program runs unasked |
| UC-4 link rebase | orchestrator | a moved archive | `rebase_links.py` rewrites it | a file outside the working directory: exit 2 | nothing written outside |
| UC-5 audit | auditor | a scanned root with `yarn.lock` | `yarn audit` runs in a copy | no `package.json`: skipped | the root's yarn configuration takes no part |

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion |
| :--- | :--- |
| A1 | Each case marked **base-fail** fails on the base tree and passes after the change |
| A2 | The archive cases TC-A1 to TC-A22 hold |
| A3 | The settings cases TC-S1, TC-S3 to TC-S8 hold |
| A4 | The guard cases TC-G1 to TC-G7 hold |
| A5 | The cases TC-Y1 to TC-Y3, TC-T1, TC-T2 hold |
| A6 | `tests/test_run_safety_rules.py` pins the new step 4, the pointers and the gate whole |
| A7 | `PYTHONPATH=. python3 tests/run_tests.py` reports OK; every gate of `framework-gates.yml` passes locally |
| A8 | `scan_register.py` reports no new `warn` on edited markdown; `git status` lists declared paths only |

The other cases are regression guards: they may pass on the base tree.

**Archive script.** Each case runs the script with `cwd` set to a temporary root. The script
exposes `main(argv)`; TC-A11 and TC-A13 call it in-process after `chdir`, with `os.link` or
`os.unlink` replaced.

- TC-A1 **base-fail** — `docs/TASK.md` → `docs/tasks/task-112-x.md` → exit 0; the content moved;
  `docs/tasks/` created.
- TC-A2 — `docs/PLAN.md` → `docs/plans/plan-112-x.md` → exit 0.
- TC-A3 — the destination exists → exit 1; both files unchanged.
- TC-A4 — the destination is a symbolic link, dangling or to a file → exit 1.
- TC-A5 — `docs/tasks` is a symbolic link to a directory outside the root → exit 1; nothing
  written there.
- TC-A6 — the source is a symbolic link → exit 1.
- TC-A7 — each of `docs/tasks/../x.md`, an absolute path, `docs/tasks/sub/task-112-x.md`,
  `docs/plans/plan-112-x.md` for `docs/TASK.md`, `docs/tasks/x.md`, `docs/tasks/task-12-x.md`,
  `./docs/tasks/task-112-x.md` → exit 1.
- TC-A8 — one operand, three operands, `-f docs/tasks/task-112-x.md`, `docs/TASK.md --help` →
  exit 2; nothing moved.
- TC-A9 — `docs` is a symbolic link → exit 1.
- TC-A10 — the source is absent → exit 1; `docs/tasks` is not created.
- TC-A11 — `os.link` raises `PermissionError` → the copy path moves the file; with the
  destination present, it refuses and keeps both.
- TC-A12 — the source has a second hard link → exit 1; the error names the hard links.
- TC-A13 — removing the source fails → exit 1; the destination is removed; the source stays.
- TC-A14 — an overlong archive name → exit 1 with a JSON error; no change on disk.
- TC-A15 — the source is swapped for another file just before the link → exit 1; no destination.
- TC-A16 — on the copy path, the source is swapped for another regular file → exit 1.
- TC-A17 — on the copy path, the source is swapped for a link → exit 1; the error names the open.
- TC-A18 — on the copy path, a write fails → exit 1; no destination; the source stays.
- TC-A19 — the `stat` after the link fails → exit 1; no destination.
- TC-A20 — a `json.py` planted beside the script is not imported when the script runs.
- TC-A21 — the source vanishes before its unlink → exit 1; the archive stays; the error says so.
- TC-A22 — the source is swapped for another file before its unlink → exit 1; the archive stays.

**Script guards.** The tests pass relative operands, or the `realpath` of their temporary root:
`os.getcwd()` returns the resolved path on darwin.

- TC-G1 **base-fail** — `rebase_links.py` with a file outside the working directory → exit 2; the
  file unchanged.
- TC-G2 — a file operand that is a symbolic link, or has a second hard link, or lies under
  `.git/` → exit 2; the target unchanged.
- TC-G3 — a file inside the working directory → rewritten as at the base.
- TC-G4 **base-fail** — `init_skill.py x --path <outside>` → exit 1; nothing created.
- TC-G5 — `init_skill.py ../x`, `init_skill.py <absolute path>` and `init_skill.py x --path .git`
  → exit 1; nothing created.
- TC-G6 — `init_skill.py x --path skills` inside the working directory → `skills/x/SKILL.md`.
- TC-G7 — `rebase_links.py` with a valid operand and a refused one → exit 2; neither is written.

TC-G2 and TC-G5 include `.GIT`, a link to `.git`, a link into `.git/hooks` and `..` after a link.

**Settings and patterns.**

- TC-S1 **base-fail** — the allow list of `.claude/settings.json` equals Appendix A.
- TC-S3 — TASK 111's checks hold; each allow rule's command name is one of `ls`, `cat`, `head`,
  `tail`, `grep`, `wc`, `stat`, `du`, `df`, `echo`, `git`, `mkdir`, `python`, `python3`, `npm`,
  `cargo`.
- TC-S4 to TC-S6 — as TASK 111.
- TC-S7 **base-fail** — R6.2.
- TC-S8:
  - the patterns accept and reject the commands of §4.1, each after the shell's quote removal;
  - the pattern block, the table and the fence lists of R6.1 equal their pinned text;
  - table and patterns cover each other (R3.5);
  - the three Antigravity lists equal R3.6.

**Related checks.**

- TC-Y1 **base-fail** — a root with `yarn.lock`, `package.json` and `.yarnrc.yml`, a fake `yarn`
  on `PATH` → `yarn audit` runs once, in a directory that holds `yarn.lock` and `package.json`
  only; that `package.json` holds the kept fields only.
- TC-Y2 — no regular `package.json` beside `yarn.lock`, or a linked `yarn.lock` → no `yarn` run.
- TC-Y3 — a root with `yarn.lock` and `package.json`, types without `javascript` → no `yarn` run.
- TC-T1 **base-fail** — `run_tests` refuses `npx jest`, `pytest -p x`, `pytest --basetemp=/tmp/x`,
  `python3 -m pytest -x`, `npm test -- -u`, `cargo test x`.
- TC-T2 — the policy accepts each command of R5.3.

### 4.1 Pattern cases

Accept, with TASK 111's accept list:

- `ls -la`, `ls -L .agent`;
- `rg foo`, `rg -L foo`, `rg --follow foo`, `rg --pre-glob '*.gz' foo`;
- `fd -L foo`, `fd -e md`;
- `mkdir -p docs/tasks`;
- `python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/task-112-x.md`.

Reject, with TASK 111's reject list:

- `rg --pre cat x`, `rg --pre=cat x`, `rg -L --pre cat x`, `rg foo --pre cat`,
  `rg --hostname-bin x y`;
- `fd -x rm`, `fd -X rm`, `fd -Hx rm`, `fd -xrm`, `fd -L -x rm`, `fd -e md -x rm`;
- `fd --exec rm`, `fd --exec=rm`, `fd --exec-batch rm`, `fd --exe rm`;
- `fd -1x rm`, `fd -0X rm`, `rg foo '--pre' cat`, `fd foo '-x' rm`;
- `fd foo` with two line continuations before `-x rm`, and the same for `rg --pre` and
  `git diff --output`.
- `file x`, `file -C`;
- `mkdir -p docs/x /tmp/y`, `mkdir -p .agent/x`, `mkdir -p tests/x`;
- `mv docs/TASK.md docs/tasks/x.md`;
- `python -c 'x'`, `python3 -c 'from scripts.tool_runner import x'`.

<!-- contract:open-questions -->

## 5. Open Questions

None open. WI-36 holds the Claude Code question of §1 (R8.6).

## 6. Decisions

**D1, 2026-10-06, operator: implement WI-35 and verify that nothing broke.** The request names the
work-item; the orchestrator takes its Recommendation, Option 1, for the `mv` rules.

**D2, 2026-10-06, orchestrator: `file` leaves every list; `rg` and `fd` stay with an exclusion.**
Rejected: an exclusion for `file` — its parser accepts `--co` for `--compile`, measured.
ripgrep 14.1.1 rejects abbreviations, measured, so an exclusion of `--pre` holds for `rg`.

**D3, 2026-10-06, orchestrator: the scripts guard their own operands (R4).** Rejected: dropping
the two rules — `skill-archive-task` needs `rebase_links.py`, and `CLAUDE.md` requires
`init_skill.py` before every new skill. Rejected: narrowing the rule text — a `*` matches any
operand.

**D4, 2026-10-06, operator: test modules and fixtures that no rule names by path are exempt from
step 4's four stages.** Code that runs without a prompt only through them is exempt with them.
A test module is a `test_*.py` or `conftest.py` file that no hook or listed script runs or
imports; a fixture is a data file that a test reads.
`tests/run_tests.py` and every script that a rule names stay under the four stages, so this run
edits `run_tests.py` in the stage-3 edit. Rejected: exempting all test-runner code — it reverses
WI-35's example. Rejected: no exemption — `python3 -m pytest` runs every test module, so every
test edit would take four stages.

**D6, 2026-10-06, operator: WI-37 is dropped.** The retro asked what to do with it; the operator
answered that it is not needed. Rejected: queuing it as a task.

**D5, 2026-10-06, orchestrator: the Antigravity list keeps commands with no writing option.**
Rejected: dropping the list — the agent's `SafeToAutoRun` still rejects a redirect, and the IDE
asks when the agent sets it to false (Troubleshooting item 1).

## 7. Out of scope

- The anchor hook for relative-path rules in a nested checkout (WI-34).
- A kill between the link and the unlink of `archive_move.py`: both names stay, and a re-run
  refuses. `skill-archive-task` Edge Cases gives the recovery.
- Two races with a concurrent writer of `docs/`: between the source check and the archive's
  removal after a failed unlink, and at the unlink itself, which removes whatever the name holds.
  Closing them needs `renameat2(RENAME_NOREPLACE)`, which Python does not expose.
- A link into the `.git` of a nested repository inside the working directory (WI-34).
- `run_tests` accepts a `cwd` anywhere in the repository, a nested checkout included (WI-34).
- `rg -z`, which runs the decompressors on `PATH`, and `fd -l`, which runs `ls` from `PATH`; neither
  runs a program the command names.
- A directory symbolic link inside the working directory that points outside the git directory:
  R4 checks paths without resolving links, so `rebase_links.py` and `init_skill.py` write through
  one (R4.2 **Why**). A link into `.git` is refused (R4.1).
- A link swapped in between the guard of `rebase_links.py` and its write. `archive_move.py`
  checks the destination after the link (R1.3) and removes it when the check fails.
- `.claude/settings.local.json`; the operator's rules stay as they are.
- The mirror copy of `skill-creator` in Universal-skills; the operator syncs it after the commit.
- `archive_protocol.archive_task()`, the Python mirror of the protocol; no allow rule runs it.
- The external scanners other than `yarn audit` (WI-37, dropped: D6).

## Appendix A — the allow rules after the change

```
Bash(ls *)
Bash(cat *)
Bash(head *)
Bash(tail *)
Bash(grep *)
Bash(wc *)
Bash(stat *)
Bash(du *)
Bash(df *)
Bash(echo *)
Bash(git status)
Bash(git status *)
Bash(git log)
Bash(git diff)
Bash(git show)
Bash(git branch)
Bash(git remote)
Bash(git tag)
Bash(mkdir -p docs/tasks)
Bash(mkdir -p docs/plans)
Bash(mkdir -p docs/architectures)
Bash(python -m pytest)
Bash(python3 -m pytest)
Bash(npm test)
Bash(cargo test)
Bash(python3 .agent/tools/archive_move.py *)
Bash(python3 .agent/skills/skill-session-state/scripts/update_state.py *)
Bash(python3 .agent/tools/task_id_tool.py *)
Bash(python3 .agent/skills/skill-creator/scripts/validate_skill.py *)
Bash(python3 .agent/skills/skill-creator/scripts/init_skill.py *)
Bash(python3 .agent/tools/rebase_links.py *)
Bash(python3 .agent/skills/artifact-formalizer/scripts/scan_register.py *)
Bash(python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py *)
Bash(python3 .agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py *)
Bash(python3 .agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py --check *)
Bash(python3 .agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py docs/PLAN.md --check *)
Bash(python3 System/scripts/doctor.py)
Bash(python3 System/scripts/doctor.py *)
Bash(python3 tests/run_tests.py)
Bash(python System/scripts/validate_skills.py --root .)
Bash(python System/scripts/validate_skills.py --root . --quiet)
Bash(python System/scripts/check_prompt_references.py --root .)
Bash(python System/scripts/security_lint.py --root .)
Bash(python System/scripts/smoke_workflows.py --root .)
```
