# Framework Audit 111 — Checks that cover what they claim

- **Task:** 111 `checks-that-cover-what-they-claim`. It archives to
  `docs/tasks/task-111-checks-that-cover-what-they-claim.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1,
  Modes A and B.
- **Date:** 2026-10-05. **Base revision:** `3a6e07ed53a3e8c25ea0c64a44708ee1b251cfa5`, clean tree
  at start.
- **Source:** WI-31, with the operator's answers of 2026-10-05 (TASK D1, D2).
- **Independence:** each audit round runs in a separate read-only agent. Same-model agreement is
  corroboration, not independent confirmation.

## 0. Emergency Bypass

`[BYPASS_TIER_PROTECTION]`: `skill-safe-commands` is a TIER 0 skill, and TASK R1.13 edits it.

- The edit adds two conditions and a name. Its framework-script patterns hold from the project
  root only, and its test runners in the project's own work tree only. The hook of TASK R1
  enforces both in Claude Code. The edit removes no pattern and changes no other section.
- TASK 110 edited `core-principles`, also TIER 0, and its audit recorded no bypass. That omission is
  noted here; the TASK 110 audit is archived and stays as written.

`[OVERRIDE_VERIFICATION]`: Mode A failed in rounds 3 and 4; the operator accepted revision 5 (TASK
D7).

- Findings per round fell 11, 4, 4, 3 MAJOR. From round 2 on, each one is a shell edge case of the
  R1 hook, and revision 5 applies the fix the reviewer stated for each round-4 finding.
- A hook that reads command text cannot model the shell completely. The TASK states the
  principle that it errs toward asking, and §7 lists the residuals.
- The hook is verified where it runs: 26 test cases, then the final review, whose code reviewer
  and security auditor hold Bash and run the hook.

## Archive (§1)

TASK 110 and PLAN 110 archived in lockstep under ID 110 with `task_id_tool.py --proposed-id 110
--no-correction`. `rebase_links.py` rewrote 4 links of the task and 1 slot link of the plan, exit 0
for both.

## Mode A — SPECIFICATION AUDIT

### Round 1 — FAIL (0 BLOCKING, 11 MAJOR, 5 MINOR)

Reviewer: `task-reviewer`, on TASK revision 1, tree `031418c9fbfa` (the formula of TASK R4.1
without `--no-ext-diff --no-textconv`). Mode A checklist: Root Integrity pass, Skill Compatibility
not applicable, Documentation partial, Migration fail. No blocking condition.

| Id | Severity | Finding | Revision 2 |
| :--- | :--- | :--- | :--- |
| TR-1 | MAJOR | a `cd` inside a command from the root escapes the hook | R1.2 follows literal `cd`/`pushd`; TC-H3, TC-H4 |
| TR-2 | MAJOR | test runners run a nested checkout's code | R1.4, R1.6; TC-H5, TC-H6 |
| TR-3 | MAJOR | a tokenizer failure lets the command through | R1.5 third case; TC-H7 |
| TR-4 | MAJOR | a hook that exits 2 blocks every Bash call | R1.8, R1.9 `\|\| true`, timeout |
| TR-5 | MAJOR | `additionalDirectories` ships home paths | R2.2, R2.5 over every `permissions` string |
| TR-6 | MAJOR | the R2.1 criterion is ambiguous | Appendix A; TC-S1 equality |
| TR-7 | MAJOR | D5 conflicts with `framework-upgrade` §3.1 | R2.3 after the commit; D5 rewritten |
| TR-8 | MAJOR | no migration for installed consumers | R6.3 second item |
| TR-9 | MAJOR | the caller's untracked output moves the new value | R4.3 |
| TR-10 | MAJOR | a failed audit reads as clean | R5.3; TC-L5 |
| TR-11 | MAJOR | A1 cannot hold for every case | base-fail marks; R6.6 |
| TR-12 | MINOR | R5.4 wording, double audit, R5.3 trigger | R5.1 one per directory, R5.4, R5.5 |
| TR-13 | MINOR | the hook-relative root is ambiguous | R1.7 `parents[2]`; R1.9 timeout |
| TR-14 | MINOR | four documents missing | R6.2, R6.4 |
| TR-15 | MINOR | `claude -p`, diff drivers, nested repositories | D3; R4.1 flags; R4.2 |
| TR-16 | MINOR | register: long enumeration, counts, reasons inline, case ids | §1 list with counts, `Why` blocks, TC ids |

### Round 2 — FAIL (0 BLOCKING, 4 MAJOR, 6 MINOR)

Reviewer: `task-reviewer`, on TASK revision 2, tree `c719187582fc`. The orchestrator appended round
1 to this audit after computing that value, so its recomputation at the return differs. The TASK
was frozen; the round stands for revision 2. From round 3 on, the value is computed after the last
write to this audit (TASK R4.3).

Round 1: TR-3 to TR-16 resolved, TR-1 and TR-2 partial. **Regressions from revision 2: 5.**

| Id | Severity | Finding | Revision 3 |
| :--- | :--- | :--- | :--- |
| TR2-1 | MAJOR | subshells, `builtin cd`, `popd` and runner prefixes escape the segment model | R1.4 runners anywhere; R1.5 word-order tracking; TC-H11, TC-H16 |
| TR2-2 | MAJOR | a runner's path argument reaches a nested checkout | R1.7 path arguments; TC-H12 |
| TR2-3 | MAJOR | the split ignores quotes | R1.2 `shlex` with `punctuation_chars`; TC-H14 |
| TR2-4 | MAJOR | a `cd` target is judged after its own move | R1.7 judges it before; R1.11; TC-H13 |
| TR2-5 | MINOR | the unparsable case over-asks at the root | R1.7 fourth case; TC-H7 from `docs/` |
| TR2-6 | MINOR | §0 of this audit is stale | §0 rewritten |
| TR2-7 | MINOR | R2.5 claims more than it checks | R2.5 names five subcommands; §7 |
| TR2-8 | MINOR | R2.3 has no actor, R4.5 no case | R2.3 actor and counts; TC-F5 |
| TR2-9 | MINOR | a crash is silent | R1.9 exception → `ask`; TC-H17 |
| TR2-10 | MINOR | case gaps and register | TC-L5, TC-F `sh` block, R1.6 wording, R1 title, R5.5 `Why` block |

**Design principle of revision 3.** The hook errs toward asking. It reads words in order instead
of modelling the shell; what it cannot model becomes an unknown directory, which is foreign.

### Round 3 — FAIL (0 BLOCKING, 4 MAJOR, 4 MINOR); bound reached, escalated

Reviewer: `task-reviewer`, on TASK revision 3, tree `d772a6218162`, unchanged at the return.
Round 2: TR2-1 and TR2-3 to TR2-10 resolved, TR2-2 partial; TR-1 and TR-2 partial. Every R2 to R6
item is resolved. **Regressions from revision 3: 4.** No false positive on the common commands
traced from the root.

| Id | Severity | Finding | Fix proposed |
| :--- | :--- | :--- | :--- |
| TR-1 | MAJOR | a target with `*`, `$` inside or no such directory is not unknown | unknown when it holds an expansion character or names no directory |
| TR-2 | MAJOR | a runner at the root recurses into `tmp/clone/` | ask when no path is named and `.git` exists below the root, or §7 |
| TR2-2 | MAJOR | node ids and globs as arguments escape the path check | judge the nearest existing ancestor |
| TR3-1 | MAJOR | `shlex` reads an unquoted `#` as a comment | `commenters = ''`; a new case |
| TR3-2 | MINOR | an unparsable command with a runner skips the path check | ask whenever the text holds a runner |
| TR3-3 | MINOR | a relative target after an unknown directory resolves from `cwd` | it stays unknown |
| TR3-4 | MINOR | "argument" is undefined; `2>/dev/null` would count | words after the runner, before the next operator, not after a redirection |
| — | MINOR | §1 says "23 others"; the file holds 25; TC-H10's comparison is unstated | count 25; compare by normalised or resolved path |

`framework-upgrade` §1 allows three specification audit rounds. The run stops here and asks the
operator how to proceed.

**Operator decision (TASK D6).** The operator chose a fourth round over splitting the hook off or
stopping. That answer overrides the bound of `framework-upgrade` §1 for one round.

**Revision 4.** Each round-3 fix is in R1.2, R1.5 to R1.9, with TC-H18 to TC-H22 and the §1 count.
A prototype of the hook, outside the work tree, gives the expected outcome on TC-H1 to TC-H22 and
on 13 further probes. In this repository, which holds no nested `.git`, the gate commands
`python3 -m pytest ... tests/...`, `PYTHONPATH=. python3 tests/run_tests.py` and the skill suite
draw no prompt.

### Round 4 — FAIL (0 BLOCKING, 3 MAJOR, 1 MINOR); the operator's extra round used

Reviewer: `task-reviewer`, on TASK revision 4, tree `9db69090f122`. Round 3: TR-1, TR3-1 to TR3-4
and both minors resolved; TR-2 and TR2-2 partial. **Regressions from revision 4: 1.** One new
MAJOR on unchanged text. Every finding sits in R1 and has a one-clause fix.

| Id | Severity | Finding | Revision 5 |
| :--- | :--- | :--- | :--- |
| TR-2 | MAJOR | an option value such as `--junitxml=docs/r.xml` displaces the current directory | R1.8 always counts the current directory; TC-H22 moved, TC-H23 |
| TR2-2 | MAJOR | `~/other/tests` and `$HOME/...` resolve inside the root | R1.7 makes such an argument unknown; TC-H24 |
| TR4-2 | MAJOR | a backquoted `cd` stays inside one word | R1.2 adds the backquote to the punctuation; R1.5, R1.7; TC-H25 |
| TR4-1 | MINOR | whether the root's own `.git` counts is unstated | R1.6 "excluding the root"; the fixture root holds `.git`; TC-H26 |

The prototype, updated to revision 5, gives the specified outcome on TC-H1 to TC-H26 and five more
probes. The gate commands of this repository still draw no prompt.

## Mode B — PLAN AUDIT

### Round 1 — FAIL (0 BLOCKING, 2 MAJOR, 7 MINOR)

Reviewer: `plan-reviewer`, on PLAN revision 1, tree `242082f4952c`. Verification step, rollback
and atomic updates pass; test coverage partial. Declared paths complete; no existing test needs an
edit.

| Id | Severity | Finding | Revision 2 |
| :--- | :--- | :--- | :--- |
| PR-1 | MAJOR | R5.4 has no test | E1 adds TC-L7 to TC-L9 on `run_external_tools` |
| PR-2 | MAJOR | a pytest-style module would load 0 tests in the curated suite | §Tests: `unittest.TestCase` only; F5 records counts, 0 fails |
| PR-3 | MINOR | H1's undo works by counts | H1 records positions and the key; the undo removes those |
| PR-4 | MINOR | R5.5 is not named | E3, E4; TC-L10 |
| PR-5 | MINOR | fixtures and git configuration | §Tests: system temp; D1 git environment; TC-L5 patches `subprocess.run` |
| PR-6 | MINOR | `test_frozen_tree_contract.py` pins D3's files | D3 runs it |
| PR-7 | MINOR | no restart step (§4.3) | G5 restart; H2 live probe |
| PR-8 | MINOR | two items own the same version bumps | F1 holds the six `security-audit` places only |
| PR-9 | MINOR | rollback wording; the decision function unnamed; the timeout unchecked | Rollback names the §3.1 exemption; A2 names `decide`; B1 checks 10 s |

### Round 2 — PASS with comments (0 BLOCKING, 0 MAJOR, 2 MINOR)

Reviewer: `plan-reviewer`, on PLAN revision 2, tree `37e193e4d3f8`. PR-1 to PR-9 resolved. Mode B
checklist: verification step, rollback, atomic updates and test coverage pass. Traceability has no
gap. **Regressions from revision 2: 2**, both MINOR, applied in revision 3:

- PR2-1: the `types` argument of TC-L7 to TC-L9, the recorder that replaces `run_command`, and
  `PATH` of the `npm` absent case;
- PR2-2: H1 states the counts R2.3 asks for.

The PLAN's extra cases TC-L7 to TC-L10 extend TASK A6.

## Execution (§3)

**Base check (§3.1).** `HEAD` equals the base. The 25 edited paths are tracked, the 7 created paths
are not ignored, and every path matches `[A-Za-z0-9._/-]+`.

**Test first.** The five modules ran on the base code before any fix. Every base-fail case failed:
TC-H1, TC-S1, TC-P1, TC-F1, TC-L1 and TC-L7. Counts on the base:

- hook: 26 of 26 failed, with no hook file;
- settings: 5 tests, 16 failures;
- pins: 3 tests, 14 failures and 1 error;
- fingerprint: 5 tests, 6 failures;
- lockfiles: 10 tests, 11 failures.

**A TASK fact corrected.** TC-F2, a regression guard, passed on the base formula. A measurement
showed why: `git diff HEAD` prints `index 8366c98..b0f0704` for a binary file, and the second hash
changes with the content. TASK §1 had said a second binary edit left the value unchanged. §1 now
says the edit enters only through that 7-character hash. R4.1 keeps `--binary`, which hashes the
content itself.

**Clusters A to F.** Each module passes after its cluster; the curated suite loads 49 tests from
the five: hook 26, settings 5, pins 3, fingerprint 5, lockfiles 10. On this repository the new
dependency scan lists the three renderer lockfiles, audits each in 2.9 s in all, and reports
`[OK] Secure`.

**Gates (G1).** Every step of `framework-gates.yml` passed locally:

- tooling 397 passed; curated suite OK; installer 183 passed;
- skill suite 650 passed and 1 skipped (Linux only); eval selftest 225 of 225;
- 47 of 47 skills valid; `validate_skill.py` exits 0 on the three edited skills, with old warnings;
- loop contract 25 loops, 0 errors; `security-audit` tests 30 passed;
- `scan_register.py`: no edited markdown file holds more `warn` than at the base.

## Review round 1 (G2)

One code reviewer with the plain exhaustive prompt and one security auditor, both holding Bash,
read the frozen tree `e23ef1711320`; both recomputed it unchanged at their end.

- **Code review:** REJECTED. CR-1 to CR-3 BLOCKING, CR-4 to CR-6 MAJOR, CR-7 to CR-12 minor.
  8 of 15 hook mutants and 6 of 6 scanner mutants survived the tests. It confirmed the 3 pins with
  `git ls-remote` and the counts of R2.
- **Security audit:** FAIL. SEC-1 and SEC-2 HIGH, SEC-3 and SEC-6 MEDIUM, SEC-4, SEC-5 and SEC-7 to
  SEC-12 LOW, SEC-13 INFO. It ran the dependency scan: 3 lockfiles, 0 vulnerabilities. It did not
  run the hook bypass hunt.

### Fix round 1

The closed list is CR-1 to CR-12 and SEC-1 to SEC-13 (TASK D8).

| Items | Disposition |
| :--- | :--- |
| SEC-1, CR-1 | Fixed: R2.6, each rule names its command whole; 18 rules become 31 |
| SEC-2, CR-5 | Fixed: `Bash(find *)` leaves; `find -exec` makes the directory unknown (R1.5); TC-H31 |
| SEC-6 | Fixed: the `mv` rules name `docs/tasks/` and `docs/plans/` |
| CR-2 | Fixed: four roots, TC-H27 to TC-H36; 20 hook mutants, each killed |
| CR-3 | Fixed: the walk skips pytest's `norecursedirs`, so `.agentic-development` is skipped; TC-H33 |
| CR-4 | Fixed: an argument is read after its last `=`; `@` is unknown; TC-H29, TC-H30 |
| SEC-8, CR-9 | Fixed: a walk budget of 20,000 directories asks when spent; TC-H34 |
| SEC-9 | Fixed: the hook runs as `python3 -I` (R1.12) |
| SEC-10, CR-10 | Fixed: reasons quote with `repr`, cut to 120 characters, and name both directories |
| CR-12 | Fixed: shells by base name with an option holding `c`; the external log names its lockfile |
| SEC-3, SEC-4 | Fixed: the audit runs in a copy without `.npmrc`; no `package.json`, no audit (R5.6) |
| SEC-5, CR-8 | Fixed: the section status names unaudited lockfiles; the reason quotes npm's `message` |
| CR-6 | Fixed: TC-L11 to TC-L15; 14 scanner mutants, each killed |
| SEC-11 | Fixed: `persist-credentials: false`; a 7-day Dependabot cooldown |
| SEC-12 | Fixed: §2.4.1 lists the edits the value does not see |
| CR-11 | Fixed: the migration lists every personal rule, "on or after", and `-I` |
| CR-7 | Stated: a runner word used as data may ask (R1.4) |
| SEC-7 | Stated in TASK §7: not verified against Claude Code's matcher |
| SEC-13 | Left to the operator at H1 (TASK D1, §7) |

**Mutation runs.** Each ran on a copy in the session scratchpad; the work tree was not mutated.
The first hook run left 4 survivors. Two showed redundant code: the `::` strip duplicated the
nearest-ancestor rule and was removed. The other two showed tests that passed by a neighbouring
rule; TC-H19, TC-H25 and TC-H35 now pin them. TC-H36 pins the last survivor in process.

## Review round 2 (G2)

Both reviewers read the frozen tree `e98da0ef81d5` and recomputed it unchanged. The security
auditor's session ended on an API error after it delivered its report; the orchestrator recomputed
the value afterwards: unchanged, 37 entries.

- **Code review:** REJECTED. CR-1, CR-4, CR-5, CR-7, CR-8, CR-9, CR-11 resolved; CR-2 and CR-6
  partial: 36 of its 40 hook mutants and 12 of its 19 scanner mutants survived. **Regressions from
  fix round 1: 4.**
  - CR2-1 HIGH: `-o norecursedirs=` or a project config undoes the walk's skip of pytest's
    default `norecursedirs`.
  - CR2-3 MEDIUM: reading after the last `=` hides `--rootdir=../x/a=b`.
  - CR2-2 LOW: a reason cut at its end loses the nested checkout's name.
  - CR2-4 minor: the skill text of R6.2 predates the temporary copy.
- **Security audit:** FAIL. It ran the hook bypass hunt on about 30 inputs, confirming escapes with
  marker files. SEC-1 to SEC-5 and SEC-8 to SEC-12 resolved; SEC-6 partial. **Regressions from fix
  round 1: 1** (SEC2-2, the same defect as CR2-1). New findings:
  - SEC2-1 HIGH: a `cd` the shell never runs moves the modelled directory back to the root. Its
    forms are `echo cd <root>`, a failed `&&` and a subshell. The hook stays silent while a nested
    checkout's code runs.
  - SEC2-3 MEDIUM: `..` in the `mv` and `mkdir` rules.
  - SEC2-4 LOW: a link inside the root into a foreign checkout.

**Observation.** Each round of the hook finds a new way the shell differs from the model: rounds
1 to 4 of the specification audit, then both review rounds. SEC2-1 shows the model can move toward
the root, against the principle the TASK states. The orchestrator escalates the hook's design to
the operator.

### Fix round 2

The operator chose to redesign the hook (TASK D9) and to keep it strict (D10). The closed list is
CR2-1 to CR2-4 and SEC2-1 to SEC2-7.

| Items | Disposition |
| :--- | :--- |
| SEC2-1 | Fixed by design: no word `cd` outside the shape of R1.10, so no unexecuted `cd` moves anything |
| CR2-1, SEC2-2 | Fixed: the walk skips only environments and caches; `-o`, `-p <module>` and `--pyargs` ask |
| CR2-3 | Fixed: an option with `=` asks, whatever follows it |
| SEC2-3 | Fixed: `..` in an `mv` or `mkdir` operand, or a third `mv` operand, asks |
| SEC2-4 | Fixed: a linked directory in the walk, or a collection directory, counts by its resolved path |
| CR2-2 | Fixed: a reason keeps the last 120 characters of a path |
| CR2-4 | Fixed: the `security-audit` text names the copy, R5.6 and R5.7 |
| SEC2-5 | Fixed by design: shell code asks by the shell's base name |
| SEC2-6, SEC2-7 | Stated: a hook that times out, and a shell profile that moves `cd`, stay residuals |
| CR-2, CR-6 | Fixed: 51 hook mutants and 21 scanner mutants, each killed with a passing baseline |
| Residual of CR2 | Fixed: `skill-safe-commands` drops `find` for every vendor |

**Mutation runs.** Both run from scripts in the session scratchpad against copies. A run stops when
the unmutated code fails its tests: one run of the hook did fail first, on `npm run test`, which
the text filter of R1.2 missed; the filter was fixed before the counted run. Four mutants of the
first hook run showed duplicate rules, which were removed: `startswith("-exec")`, the `..` and
absolute-path parts of a literal path, and the `foreign` check of the `cd` shape. Each duplicates a
check that runs later.

**Prompts during the run.** The operator saw approval prompts in Auto mode. They came from the
live hook asking on the orchestrator's own commands, which held `$`, `cd` and framework paths
together. Those commands now run as scripts from the scratchpad. A narrower hook goes to a new
work-item (TASK D10).

**Gates after fix round 2 (G1).** Every step of `framework-gates.yml` passed locally:

- tooling 397; curated suite OK; installer 183; `security-audit` tests 30;
- skill suite 650 and 1 skipped; eval selftest 225 of 225;
- 47 of 47 skills; loop contract 25 loops and 0 errors. The five modules load 61
tests in the curated suite: hook 23, settings 6, pins 3, fingerprint 5, lockfiles 24. These replace
the counts recorded after clusters A to F. No edited markdown file holds more `warn` than at the
base, and `git status` lists 37 entries, each declared.

## Review round 3 and the split (G2)

- **Code review:** REJECTED. The redesigned hook still let foreign code run (CR3-1 to CR3-6).
  Each of these was silent while a nested checkout's code ran:
  - a leading `NAME=value` before a runner;
  - zsh's `chdir` builtin and a glob qualifier;
  - `.` after an operator.

  No false positive on this repo's own commands.
- **Security audit:** INCOMPLETE. A safety classifier stopped its bypass hunt before any probe ran
  against the redesign; its scan found nothing new.

**The split (TASK D11).** Three review rounds each found a new divergence between the hook's command
model and the shell. The adversarial hunt could not run to a conclusion in this session. The
operator deferred the hook to **WI-34**, with its design, its test module and this review history:
specification audit rounds 1 to 4 and review rounds 1 to 3.

This change ships R2 to R6, each carried by its own reviews:

- the committed allow list is narrowed to 59 framework rules (SEC-1, SEC-2 resolved);
- the actions are pinned (SEC-11);
- the fingerprint covers untracked content (SEC-19);
- the dependency scan audits every lockfile in a clean copy (SEC-3 to SEC-6).

The `PreToolUse` block leaves `.claude/settings.json`, and its PostToolUse hook returns to the
base command.

**The scanner's low gaps (CR-6).** Review round 3 left three scanner mutants alive. TC-L21 to
TC-L23 pin the `error` code in the reason, the count of unaudited lockfiles and a moderate advisory
that is no finding. The scanner's mutation run then killed 24 of 24.

## Retro items (cluster I, TASK R7, D12)

The retro offered three items. The operator chose two and asked to fix them in this run.

- **I1.** `framework-upgrade` §3 step 4: a hook or an allow rule takes effect in the running
  session at once, so a run builds it on a fixture root and registers it last.
- **I2.** `security-audit` §6.2: an audit whose adversarial part does not run is `INCOMPLETE`; one
  re-run, then the operator decides; tests and mutation runs do not stand in for the hunt. The
  security-auditor wrapper points to it.
- **I3.** `tests/test_run_safety_rules.py` joins the curated suite.

The third item, a guideline for security controls that parse shell text, was not chosen.

## Review round 4: cluster I (G2)

Tree fingerprint `1e18be8f80fc`. One code reviewer with the plain exhaustive prompt and one
security auditor.

- **Code review:** CHANGES REQUESTED, 5 MAJOR and 4 MINOR (CRI-1 to CRI-9):
  - step 4 contradicted §3.1 on the fixture (CRI-1);
  - it left the registration unreviewed and waited for the code review only (CRI-2, CRI-3);
  - it named a hook but no rule, and "last" had no anchor (CRI-4);
  - the pin test checked labels, and four text mutants stayed green (CRI-5);
  - §6.2 had no pointers where an audit is routed (CRI-6);
  - §6.2's provenance line was wrong (CRI-7), and the records miscounted (CRI-8, CRI-9).
- **Security audit:** FAIL. Cluster I had no CRITICAL or HIGH finding; SECI-1 to SECI-7 are
  MEDIUM or LOW. SECI-8, HIGH, lies in R2's committed settings: seven wildcard `git` and `tree`
  rules approve forms that write. The auditor's probe was refused. The Claude Code permissions
  page confirms the claim: it lists `git log --output=<file> main` as a match of a wildcard rule.

### Fix round 4

The operator moved SECI-8 into this run and kept archiving automatic (TASK D13).

- **Step 4** (CRI-1 to CRI-4, SECI-4, SECI-5). It covers a new hook, an edited hook script and a
  new or wider rule. The TASK states the registration, and both reviews check it. An `INCOMPLETE`
  audit blocks it. The run's last edit after §4.5 registers it, and a focused review checks that
  diff. §3.1 allows a fixture that the test creates and removes.
- **§6.2** (CRI-6, CRI-7, SECI-2, SECI-3). It covers both parts of an audit. The orchestrator
  records `INCOMPLETE` when no report returns. Each part gets one re-run in a run, and the
  operator decides in their own message. `10_security_auditor.md`, `security-audit.md`,
  `full-robust.md` and `SKILLS.md` point to it; `full-robust` §3 gates on `audit_status: PASS`
  (SECI-1).
- **The pin** (CRI-5). `tests/test_run_safety_rules.py` pins the rule sentences and the pointers.
- **The settings** (SECI-8, SECI-6). The seven rules leave, and Appendix A holds 52 rules. TC-S3
  forbids them, TC-S6 pins the hooks block, and TC-S7 pins the archive commands of
  `skill-archive-task`. `skill-safe-commands` states the read forms. WI-35 holds the archive `mv`
  rules and three patterns of `skill-safe-commands` that run a program or write.
- **Records** (CRI-8, CRI-9): this section, the PLAN and the counts below.
- **SECI-7.** The ignored, inert `.claude/hooks/__pycache__/anchor_cwd.cpython-314.pyc` is deleted.

**Mutants.** 19 text and settings mutants on copies, with a passing baseline; each is killed. They
include the four that survived round 4: "until it finishes", "as verified", "registered at once"
and a wrapper `PASS`.

## Review round 5: fix round 4 (G2)

Tree fingerprint `0c8255f1166f`, the same one at each reviewer's start and end.

- **Code review:** REJECTED, 1 BLOCKING, 2 MAJOR and 17 MINOR (CR5-1 to CR5-21). It confirmed
  CRI-1 to CRI-4 and CRI-6 to CRI-9 closed, and CRI-5 closed in part. Its main findings:
  - the Antigravity lists of `skill-safe-commands` and both READMEs still named the writing forms
    (CR5-1);
  - `GEMINI.md` and `AGENTS.md` still called `find -L` auto-runnable (CR5-2);
  - TC-S7 skipped indented blocks and most parts of a command (CR5-3);
  - three pointers and the settings keys were not pinned, and 14 mutants survived (CR5-4, CR5-9,
    CR5-10).
- **Security audit:** FAIL, 1 HIGH, 6 MEDIUM and 6 LOW (SECI5-1 to SECI5-12). SECI-1 to SECI-7
  are closed; SECI-8 was closed in `.claude/settings.json` only. SECI5-1, HIGH, existed at the
  base: the test-runner wildcard rules approve options that run a program, delete a directory or
  overwrite a file. The operator-only block of the report stays out of this record.

### Fix round 5

The operator kept only the bare forms of the test runners, and moved the older classes to WI-35
(TASK D14).

- **The settings** (SECI5-1, CR5-9). Six test-runner rules leave, `npx jest` among them; Appendix
  A holds 46 rules. TC-S3 forbids any `git` wildcard but `git status *`. TC-S6 pins the settings
  keys and `env`.
- **Every vendor** (CR5-1, CR5-2, CR5-10, SECI5-2, SECI5-5, SECI5-6). `skill-safe-commands` keeps
  bare test runners and states that a pattern applies to each simple command after quote removal.
  Its false "stays safe" bullet is gone. The Antigravity lists name no writing form. `GEMINI.md`
  and `AGENTS.md` follow the skill. TC-S8 pins all of it.
- **Archiving** (CR5-3). TC-S7 reads every shell block of `skill-archive-task` and checks every
  part. Only the `test -e` guard of Step 5 has no committed rule; WI-35's archive script absorbs
  it.
- **Step 4 and §6.2** (CR5-4 to CR5-8, CR5-19 to CR5-21, SECI5-3, SECI5-4). Step 4 covers every
  change that alters what runs, and a change that only narrows may land at once. It names both
  reviewers and restores the base text on a failed gate or review. §6.2 defines `PASS`, `FAIL`
  and `INCOMPLETE`. `tests/test_run_safety_rules.py` pins both texts whole and every pointer
  sentence.
- **Sources** (CR5-16). R2.7 and D13 cite the Claude Code docs, Configure permissions,
  § Read-only commands.
- **Records** (CR5-11, CR5-12, CR5-15, CR5-17, CR5-18, SECI5-10). WI-31's dates read
  2026-10-06; the migration guide returns to its base text; WI-34 notes the relative hook command;
  the PLAN and the changelogs are corrected.
- **WI-35** (CR5-13, CR5-14, SECI5-6 to SECI5-9, SECI5-11, SECI5-12) holds the older classes.

**Mutants.** 30 mutants on copies, with a passing baseline; each is killed. They include the 14
that survived round 5. One more survived the first run, a README list with an appended entry; the
test now pins each list whole.

## Review round 6: fix round 5 (G2)

Tree fingerprint `b82098934399`, the same at each reviewer's start and end. Both reviews checked
the closed lists and the fix's diff only.

- **Security audit:** PASS. Both parts ran to completion; no CRITICAL or HIGH finding. SECI5-1 to
  SECI5-6 and SECI5-10 are fixed, and the rest are recorded. It found 2 MEDIUM and 4 LOW items
  (SECI6-1 to SECI6-6), none blocking. The operator-only block of the report stays out of this
  record.
- **Code review:** REJECTED, 1 MAJOR and 14 MINOR (CR6-1 to CR6-15), no BLOCKING. CR6-1: the
  pointers to §6.2 still called an unfinished audit `INCOMPLETE`, while §6.2 makes it `FAIL` when a
  part found a CRITICAL or HIGH issue. CR5-10 was closed only in part: the command table was not
  pinned.

### Fix round 6

- **Verdicts** (CR6-1). The wrapper, `10_security_auditor.md`, `security-audit.md`,
  `full-robust.md` and both changelogs follow §6.2: an unfinished part gives `INCOMPLETE`, or
  `FAIL` when a part found a CRITICAL or HIGH issue.
- **Step 4** (CR6-9, CR6-10, CR6-13, SECI6-5, SECI6-6). Its list is not exhaustive and names `env`,
  `permissionMode`, `allowed-tools` and `enableAllProjectMcpServers`. A narrowing needs a recorded
  check. A failure restores the text before stage 3's edit, and §6.2 governs what follows.
- **`skill-safe-commands`** (CR6-5, SECI6-1 to SECI6-3). A simple command with a redirection to a
  file or a substitution is not safe. The two open-ended patterns sit under their own heading. The
  Antigravity note no longer asserts the IDE's matcher.
- **Tests** (CR6-2 to CR6-4). TC-S8 pins the command table row by row. TC-S7 matches the `test -e`
  guard whole, splits at `&`, reads `zsh` and `console` fences, and rejects a redirect or a
  substitution. TC-S3 lets a `python` rule run a bare `-m pytest` or a named script only.
- **Records** (CR6-6 to CR6-8, CR6-11, CR6-12, CR6-15). The TASK's long lines rewrap; WI-34 and
  WI-35 follow D14; the PLAN's cluster table and schedule are current.
- **WI-35** (SECI6-2, SECI6-4, and the review's out-of-scope items) gains `Bash(file *)`, the
  table against the patterns, the Antigravity matcher and `ORCHESTRATOR.md`.
- **Residual** (CR6-14). Substring pins do not catch a contrary sentence appended elsewhere in
  `GEMINI.md`, `AGENTS.md` or after a pinned pointer. The whole-text pin of step 4 ends at the next
  numbered step, so a step added after it escapes. Step 4, §6.2 and the command table's bold rows
  are pinned whole.

**Mutants.** 20 mutants on copies, with a passing baseline; each is killed. They include the
survivors K01 to K04, K08, K10, A01 to A04, A06, P01 and P02 of round 6.

**The narrowing check of step 4.** A base rule covers each of the 46 committed rules. `env` and
`hooks` equal the base's; the only other change removes `additionalDirectories`.

## Review round 7: fix round 6 (G2)

Tree fingerprint `695aa38ebe62`, the same at each reviewer's start and end. Both reviews checked
the closed lists and the fix's diff only.

- **Security audit:** PASS. Both parts ran to completion; no CRITICAL or HIGH finding. SECI6-1 to
  SECI6-6 are fixed or recorded, and `.claude/settings.json` is unchanged. It found 3 LOW items:
  - the narrowing check named no direction, so a removed deny or ask rule would pass (SECI7-1);
  - `SKILLS.md` and `WORKFLOWS.md` still gave the verdict from before CR6-1 (SECI7-2);
  - after a `FAIL`, the Failure branch named no decider (SECI7-3).

  The operator-only block of the report stays out of this record.
- **Code review:** APPROVED with 12 MINOR (CR7-1 to CR7-12), no BLOCKING or MAJOR. CR7-1 and CR7-2
  match SECI7-2 and SECI7-1; CR7-7 asks what a re-run reads after the restore.

### Fix round 7

The operator chose a small edit before the commit, with the other MINOR items in WI-35.

- **Verdicts** (CR7-1, SECI7-2). `SKILLS.md` and `WORKFLOWS.md` follow §6.2; TC-3 pins both.
- **Narrowing** (CR7-2, SECI7-1). The check runs before the edit, list by list: new allow,
  `additionalDirectories` and `allowed-tools` entries are covered by the base; base deny, ask and
  `disallowedTools` entries stay or are covered; every other key equals the base's. The audit
  records its output. TASK 111's settings change predates the check; run afterwards, it passes:
  the base holds no deny, ask, `disallowedTools` or `defaultMode` entry, `env` and `hooks` equal
  the base's, and no `additionalDirectories` entry is new.
- **Failure** (SECI7-3, CR7-7). The restore brings back the copy under the new name, and the audit
  records the stage-3 diff. A §6.2 re-run reads that diff. After a `FAIL` the operator decides,
  and a changed registration returns to stage 1.
- **WI-35** holds the rest of round 7: the redirect question for Claude Code, the pins' missed
  spellings, appended sentences, and long lines.

**Mutants.** 7 mutants on copies, with a passing baseline; each is killed.

## Review round 8: fix round 7 (G2)

Tree fingerprint `175a0fc6b8a7`, the same at each reviewer's start and end. Both reviews checked
the fix-round-7 diff only, 8 files.

- **Code review:** APPROVED, no BLOCKING or MAJOR; 10 minor items. Among them: the Failure branch
  named no next step after a failed gate or a rejected review, and a `FAIL` that changes only a
  hook's code did not return to stage 1.
- **Security audit:** PASS, scan complete and unchanged. Two MEDIUM items in the rewritten text:
  - the narrowing check passed an in-place edit of code a registered hook runs (SECR8-1);
  - after a `FAIL`, only a changed registration text returned to stage 1, not changed hook code
    (SECR8-2).

  Four LOW items: "covers" named no list (SECR8-3, SECR8-4), a re-run that passes named no stage
  4 (SECR8-5), and an in-place edit of a script that an allow rule names passed the check
  (SECR8-6). The operator-only block stays out of this record.

### Fix round 8

The operator chose the fix and one more narrow re-check.

- **Narrowing** (SECR8-1, SECR8-3, SECR8-4). A cover comes from the same list, and no file that a
  registered hook, a `statusLine` command or an MCP server runs may change.
- **Failure** (SECR8-2, SECR8-5, code minor items 1 to 4). After an `INCOMPLETE` audit, a passing
  re-run applies the recorded diff again and stage 4 checks it on the new fingerprint. After a
  failed gate, a rejected code review or a `FAIL`, the operator decides; a registration or the
  code it runs, changed, returns to stage 1.
- **Records** (code minor items 6 to 10). R7.1 and R7.2 follow step 4 and name `WORKFLOWS.md`;
  WI-35 names rounds 7 and 8 and gains SECR8-6; this record states how TASK 111's own change
  passes the new check.

**Mutants.** 5 mutants on copies, with a passing baseline; each is killed.

## Review round 9: fix round 8 (G2)

Tree fingerprint `71abd9ecf6e5`, the same at each reviewer's start and end. Both reviews checked
the fix-round-8 diff only, 6 files.

- **Code review:** APPROVED, no BLOCKING or MAJOR. A mutation run of step 4 caught 10 of 11
  mutants; the survivor is the step added after step 4, recorded above.
- **Security audit:** PASS, scan complete and unchanged; no CRITICAL, HIGH or MEDIUM item in the
  diff. SECR8-1 to SECR8-5 are closed; SECR8-6 stays in WI-35.

Both reports list LOW and minor wording items in step 4, R7.1 and this record. They change no
verdict, so they go to WI-35 without another fix round.

## Close (§4.5, H)

- WI-31 is `done`, with SEC-17's hook handed to WI-34 (filed `open`). WI-35 is filed `open`.
  WI-32, WI-30, WI-22 and WI-27 were closed by TASK 110.
- `git status` lists 44 entries, each a declared path; the hook file and its test are gone.
- `check_positional_refs.py --targets-changed --fix` repaired nothing. Its 12 errors are the
  ones TASK 110 recorded, in old changelog entries and in archives of TASKs 095, 103 and 105.
- Every gate of `framework-gates.yml` passed after fix round 8. The curated suite runs 495 tests;
  the five new modules load 50: settings 11, pins 3, fingerprint 5, lockfiles 27, run-safety
  rules 4.
- The operator commits. R2.3 appends the 33 personal rules and 2 directories to the operator's
  `.claude/settings.local.json` after the commit, on the operator's go-ahead.

## Addendum: H1, after the operator's commit

The operator committed the change as `3af40e8` and gave the go-ahead to move all 33 personal rules
and both directories (R2.3, D1).

- **Moved:** 33 of 33 rules and 2 of 2 directories into `.claude/settings.local.json`, which git
  ignores. None was there before, so each was added.
- **Positions in the base allow list:** 42 to 45, 47, 48, 51 to 70, 74 to 80.
- **`additionalDirectories`:** H1 created the key.
- **Not moved:** `find *`, `tree *` and `npx jest*`. They left the committed file for safety
  (R2.6, D13, D14), not as personal rules.
- **Undo:** remove the allow entries taken from those base positions and the
  `additionalDirectories` key. The local file's 17 earlier rules stay.

