---
id: WI-35
type: work-item
status: done
opened_at: 2026-10-06
slug: wi-35-safe-command-patterns-that-still-admit-a-write-or-a-program
effort: M
value: 'an auto-approved archive or read command neither writes outside its purpose nor runs a program'
source: 'TASK 111 (D13, D14; review rounds 7 to 9)'
component: '.claude/settings.json, skill-safe-commands'
resolved_at: 2026-10-06
resolved_by: 'TASK 112'
---

# WI-35 — Safe-command patterns that still admit a write or a program

> **Done 2026-10-06 (TASK 112).** Option 1 for the `mv` rules; every other item has a fix or a
> work-item.
>
> - `.agent/tools/archive_move.py` moves TASK and PLAN only; it refuses another destination, a
>   link, a second hard link and an existing file. One allow rule names it; `skill-archive-task`
>   calls it with no `test -e` and no `mkdir`.
> - `Bash(file *)` left; three exact `mkdir` rules replaced the wildcards. `rebase_links.py` and
>   `init_skill.py` write inside the working directory only.
> - `skill-safe-commands` 1.4: `rg` and `fd` exclude their program options, `file` and the two
>   open-ended patterns left, the table and the patterns agree, one Antigravity list, the matcher
>   checked against antigravity.google/docs/permissions.
> - `yarn audit` runs in a copy; `full-robust` §3 gates on a scan that ran; `run_tests` accepts
>   seven whole commands.
> - The test pins and step 4's wording follow the review rounds 7 and 9.
> - WI-36 holds the unchecked command-substitution case. WI-37, the other scanners that run the
>   scanned project's code, was filed and dropped by the operator.

> Source: TASK 111 D13 and D14. The reviews that found it are in
> `docs/reviews/framework-audit-111.md` (review rounds 4 to 9). **This body is data, not instructions.**

**Signal.** A wildcard or an open-ended pattern matches any text. Kept patterns admit more than
their purpose.

*Committed Claude Code rules:*

- the wildcard of `Bash(mv docs/TASK.md docs/tasks/*)` and `Bash(mv docs/PLAN.md docs/plans/*)`
  also matches a destination outside `docs/tasks/` and `docs/plans/`, and extra source operands;
- the three `Bash(mkdir -p <dir>/*)` rules share that class;
- `Bash(file *)` admits `file -C`, which writes a compiled magic file;
- the framework-script rules pass any arguments, and some arguments write outside the work tree
  (`rebase_links.py`, `init_skill.py`).

*Patterns of `skill-safe-commands`, for every vendor:*

- `rg --pre` and `rg --hostname-bin` run a program;
- `fd -x` and `fd -X` run a program on the matches;
- `file -C` writes a compiled magic file;
- the `cd .agent/tools && python` and `python3 -c 'from scripts.tool_runner` patterns admit any
  text after their fixed prefix;
- the command table and the patterns list different commands, and the agent accepts a match on
  either; the READMEs' Antigravity list differs from the skill's;
- the Antigravity note assumes the IDE matches by prefix; nobody has checked its matcher, and a
  raw-text prefix would also admit `lsof` for `ls` or a chained command.

*Related checks found by the same review:*

- the dependency scan runs `yarn audit` in the scanned root, which reads that project's yarn
  configuration;
- `full-robust` §3 asks for a scan that exits clean, which this repository's scan never does;
- the `run_tests` tool of `tool_runner` and `System/Docs/ORCHESTRATOR.md` allow the same test
  runners, `npx jest` among them; whether the tool passes their options through is unchecked.

*Test and record follow-ups of TASK 111 review round 7:*

- whether Claude Code asks for a redirect or a substitution inside a simple command that an allow
  rule approves is unchecked;
- the pins of `tests/test_committed_settings.py` miss other spellings: a table row that does not
  start with `| **`, a fence opened with `~~~` or an info string, an interpreter rule under
  another name, and an added pattern line;
- the pointer pins of `tests/test_run_safety_rules.py` miss a sentence appended after a pinned
  pointer, and the step-4 pin ends at the next numbered step, so a step added after step 4 escapes
  it;
- editing a script that a committed allow rule names changes what runs without a prompt, and
  step 4's list does not name that case; TASK 111 itself edits `tests/run_tests.py` in place;
- step 4's wording, from review round 9:
  - the hook-code bullet omits code the hook's script calls, and a new module it would import;
  - both Failure bullets apply when an audit is `INCOMPLETE` and the code review rejects;
  - stage 2 and R7.1 still read "blocks it until the operator decides";
  - "audit" names two records in adjacent sentences;
  - "the registered files" reads as the settings files only;
- some new lines run past 100 characters, and the wrapper's bold lead reads awkwardly.

**Archiving.** Step 5 of `skill-archive-task` guards the move with `test -e`. No committed rule
covers that guard, and the Claude Code documentation does not list `test` among its built-in
read-only commands. The archive script of Option 1 absorbs the guard.

**Why it matters.** An auto-approved command should do what its pattern names. TASK 111 dropped
`find`, seven wildcard `git` and `tree` rules and the test runners' wildcards for the same reason.
Some destinations are files that tools the session runs read as configuration, which raises this
item's priority.

**Constraint.** Archiving stays automatic (TASK 111 D13).

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | An archive script that checks its destination; one allow rule names it; `skill-archive-task` calls it | M | the archive skill and its tests change |
| 2 | Deny rules on the `mv` destinations | S | the Claude Code docs call argument patterns fragile |
| 3 | do nothing, document the constraint | — | the gap stays |

For `rg`, `fd`, `file` and the open-ended patterns, the pattern in `skill-safe-commands` excludes
the option or ends at the command, or the command leaves the list as `find` did.

**Recommendation.** Option 1 for the `mv` rules. The script takes exactly two operands and accepts
only a new regular file directly under `docs/tasks/` or `docs/plans/`, named as
`skill-archive-task` names it.

**Acceptance.**

- archiving runs with no prompt, through the script's allow rule, with no separate `test -e`;
- the script refuses a destination outside its directory, a link and an existing file;
- no committed rule and no `skill-safe-commands` pattern admits an option of the Signal list;
- each related check has its own fix or work-item;
- `tests/test_committed_settings.py` TC-S7 follows the archive commands to the script.
