# Framework Audit 112 — Safe commands that admit no write

- **Task:** 112 `safe-commands-that-admit-no-write`. It archives to
  `docs/tasks/task-112-safe-commands-that-admit-no-write.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1,
  Modes A and B.
- **Date:** 2026-10-06. **Base revision:** `eb7248f8027e64cb10aaa20511a4f7b519151117`, clean tree
  at start.
- **Source:** WI-35, with the operator's request of 2026-10-06 (TASK D1).
- **Independence:** each audit round runs in a separate read-only agent. Same-model agreement is
  corroboration, not independent confirmation.

## 0. Emergency Bypass

`[BYPASS_TIER_PROTECTION]`: `skill-safe-commands` and `artifact-management` are TIER 0 skills.

- `skill-safe-commands` (TASK R3): patterns for `file`, the open-ended `cd`/`tool_runner` forms
  and the `mv` and wildcard `mkdir` forms leave; `rg` and `fd` gain an exclusion; the table and
  the vendor lists follow the patterns. No pattern widens what it admits, except the one that
  names the archive script, which refuses every operand but the two archive pairs.
- `artifact-management` (TASK R1.6): one line names the archive script in place of `mv`.

## Archive (§1)

TASK 111 and PLAN 111 archived in lockstep under ID 111 with `task_id_tool.py --proposed-id 111
--no-correction`. `rebase_links.py` rewrote 1 link of the task and 1 slot link of the plan, exit 0
for both. The two commands, as run:

```sh
python3 .agent/tools/rebase_links.py docs/tasks/task-111-checks-that-cover-what-they-claim.md --from docs --to docs/tasks --slot docs/PLAN.md=docs/plans/plan-111-checks-that-cover-what-they-claim.md
python3 .agent/tools/rebase_links.py docs/plans/plan-111-checks-that-cover-what-they-claim.md --from docs --to docs/plans --slot-must-exist --slot docs/TASK.md=docs/tasks/task-111-checks-that-cover-what-they-claim.md
```

## Probe incident (§1)

While measuring R3.1, `file --co` ran in the repository root and wrote `magic.mgc` (7 273 344
bytes). The run removed that untracked file at once with `rm --`; `git status` then listed the
archive pair only. The incident is the measurement D2 cites.

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

A read-only `task-reviewer` agent; no blocker, no §4 condition. It confirmed Appendix A (44 rules),
the base versions, the free WI numbers, every §1 code claim and the mapping of every WI-35 item.

| # | Severity | Finding | Applied in revision 2 |
| :--- | :--- | :--- | :--- |
| 1 | MAJOR | CLI tests of `test_rebase_links.py` and `archive_protocol.py` use temporary paths | R4.1: guard in `_main` only; the tests `chdir` |
| 2 | MAJOR | migration omits copied patterns and Antigravity lists | R8.2 second item |
| 3 | MAJOR | `System/Docs/SKILL_TIERS.md:18@eb7248f` and `.agent/skills/skill-phase-context/SKILL.md:24@eb7248f` claim `mv` auto-runs | R8.4, R8.1 |
| 4 | MAJOR | Steps 6 and 7.7 retry `mv`; unlink failure undefined | R1.5, R1.3 |
| 5 | MAJOR | "every fence" ambiguous for TC-S7 | R6.1 shell-fence definition, info-word pins |
| 6 | MAJOR | test-runner exemption decided by the orchestrator | D4 asked; the operator chose "test modules only" |
| 7 | MINOR | guard placement vs `skill_utils.py` | R4.2 |
| 8 | MINOR | TC-A8 never reaches the dash rule | TC-A8 |
| 9 | MINOR | hard links; check-then-act race | R1.2, R1.3 descriptors; TC-A12; R4.1 nlink; §7 residual |
| 10 | MINOR | unresolved paths: directory links, `.git/` | R4 `.git` segment; §7 residual |
| 11 | MINOR | `rg`/`fd` leave the general line; fd abbreviations; `fd -l` | R3.2 `--exe`; §4.1 cases; §7 |
| 12 | MINOR | Tool calls row | R3.5 |
| 13 | MINOR | yarn lockfile links; temp location; javascript gate | R5.1 |
| 14 | MINOR | exit codes of a wrong shape and of TC-G4/G5 | R1.1, R1.2, TC-G4/G5 |
| 15 | MINOR | final name of the script; stage-3 test edits | R1.7, R6.5 |

**Operator decision D4 (2026-10-06), quoted:** "Exempt test modules only (Recommended)".

### Round 2 — TASK revision 2: PASS

The same agent, resumed. No blocker, no MAJOR, no §4 condition; it read "TASK revision 2, 514
lines" with no tree fingerprint, and ran neither the register scan nor the resolver (no execution
tool). The orchestrator ran `scan_register.py` on revision 3: 0 warn.

| # | Severity | Finding | Applied in revision 3 |
| :--- | :--- | :--- | :--- |
| a/8 | MINOR | `TC-L9b` cited but undefined in the TASK | TC-Y3, A5, R5.1 |
| 1 | MINOR | a refusal could leave `docs/tasks` created | R1.2 order of checks; TC-A10 |
| 2 | MINOR | source swapped between check and `os.link`; copy path open | R1.3 post-link check, `O_NOFOLLOW` + `fstat`, removal on any later failure; §7 |
| 3 | MINOR | the skill handles exit 1 only | R1.5: non-zero exit |
| 4 | MINOR | `run_tests.py` change never reviewed in stage 2 | R4.4 states the registration text |
| 5 | MINOR | "fixture" undefined | D4 defines test module and fixture |
| 6 | MINOR | `os.getcwd()` vs `/var` on darwin | R4.1 defines the working directory; test note |
| 7 | MINOR | TC-A11/A13 need an in-process call | `main(argv)`, in-process cases |

Mode A closes at round 2 with PASS; revision 3 applies its MINOR findings.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: FAIL

A read-only `plan-reviewer` agent; 9 MAJOR, 9 MINOR. No tree fingerprint; it ran no command.

| # | Severity | Finding | Applied in PLAN revision 2 / TASK revision 4 |
| :--- | :--- | :--- | :--- |
| 1 | MAJOR | H's restore reverts C's edits; untracked `_next` copies cannot be restored; triggers incomplete | the stage-3 patch; Failure = `git apply -R`; I1 and `INCOMPLETE` triggers |
| 2 | MAJOR | G2 reviews a description of H, not its text | G2 writes the patch; G4 reviews it; H applies it |
| 3 | MAJOR | C3–C5 name `archive_move.py` for other vendors before review | TASK R1.7; every vendor entry moves into the patch |
| 4 | MAJOR | H edits after §4.5; skill-creator Script Contract contradicts R4.2 | the contract in the patch; H2 runs the resolver without `--fix` |
| 5 | MAJOR | the new modules and the guarded `_main` run first in H | G1 runs both modules by name; B5 runs against `rebase_links_next` |
| 6 | MAJOR | no base-fail run of final TC-S1/TC-S7 | G3 |
| 7 | MAJOR | narrowing check covers 2 of 4 results | C2 prints all four |
| 8 | MAJOR | no coverage table, schedule block or plan chart | Coverage; Schedule; chart by `plan_gantt.py` |
| 9 | MAJOR | A8's `git status` check has no step | G1, H2 |
| 10 | MINOR | the `full-robust` pin is red between D5 and E1 | the gate moves to E5 |
| 11 | MINOR | F1 overlaps version steps | F1: `security-audit` only |
| 12 | MINOR | `schemas.py`, ARCHITECTURE `run_tests` row stale | TASK R5.3; D4, F3 |
| 13 | MINOR | no restart step | J1 |
| 14 | MINOR | no gate re-run after §4.5 | G6 |
| 15 | MINOR | G2 has no failure branch | G4 branches |
| 16 | MINOR | TASK §1 line references unpinned | left to the resolver in G5 (`REFERENT_MOVED`) |
| 17 | MINOR | the resolver could rewrite the TASK 111 archive | E6 hashes, checked in G1 and H2 |
| 18 | MINOR | no task files; retro records; which step 4 governs | no task files (PLAN 111 precedent); retro note; Sequencing rule |

### Round 2 — PLAN revision 2: FAIL

The same agent, resumed. Resolved: 2, 3, 5, 8–14, 16, 18. Partly resolved: 1, 4, 6, 7, 15, 17. The
patch design holds: `git apply -R` restores deletions, and the `.diff` is declared and not ignored.

| # | Severity | Finding | Applied in PLAN revision 3 |
| :--- | :--- | :--- | :--- |
| 1 | MAJOR | TC-S3's command set lacks `mv` while the `mv` rules stay until H | C1 set plus `mv`; the patch removes it |
| 2 | MAJOR | the patch omits the new fence pin of `skill-archive-task` | G2 patch list |
| 3 | MINOR | C1 keeps the `mkdir` wildcards in `FRAMEWORK_ALLOW_RULES` | C1 |
| 4 | MINOR | C2 fourth result vs `init_skill_next.py` | C2: no imported name added or changed |
| 5 | MINOR | §5 removes the `.diff` | the audit record holds the patch text and SHA-256 (G4) |
| 6 | MINOR | no integrity checks around H | H1 hashes and modes; `--whitespace=nowarn`; Failure compares |
| 7 | MINOR | H2 resolver hit undefined | H2: failed gate, back to G4 |
| 8 | MINOR | G5 may rewrite the archive pair | G5 dry run; rebuild from `git show` and §1's commands |
| 9 | MINOR | scratchpad scripts vs "no file outside" | Rollback point names the two helpers |
| 10 | MINOR | C3 includes the archive pattern and row | C3 excepts them |
| a6 | — | G3 omits TC-S8's archive cases | G3 |
| a15 | — | a fix round skips G3 | G4: G1 to G3 |

### Round 3 — PLAN revision 3: PASS

The same agent, resumed. Round-2 findings 1–10, a6 and a15 resolved. Five MINOR findings, applied
in PLAN revision 4:

1. the stored patch could close a backtick fence early → `~~~~diff` fence, hash check (G4);
2. G3's expected failures were incomplete → TC-S3 and the fence pin listed;
3. the §1 rebase commands were not quoted → quoted in §1 above; a hash mismatch stops the run;
4. the resolver reads the stored patch text → H2 states such a hit is not caused by the patch;
5. no action on a hash or mode mismatch after `-R` → STOP; §5 is the fallback.

Mode B closes at round 3 with PASS.

## Execution (§3)

**Base check (§3.1).** `git rev-parse HEAD` = base. 38 edited paths tracked; 8 created paths not
ignored; every path matches `[A-Za-z0-9._/-]+`, with no `..` or `.git` segment.

### Cluster A — the archive script

- A1 base-fail: `tests/test_archive_move.py` against the base tree: 32 failed, 3 passed; TC-A1
  failed (the script is absent).
- A2 stub: TC-A8 passed (1 test, 5 subtests).
- A3: 14 passed, 21 subtests passed. One fix during A3: `_supported()` reads `os.supports_dir_fd`
  by function name, since `mock.patch` of `os.link` replaced the object the set holds.

### Cluster B — script guards

- B1 base-fail: the module with its constants on `rebase_links.py` and `init_skill.py`: TC-G1,
  TC-G2 (4 subtest failures) and TC-G4, TC-G5 (3 subtest failures) failed; TC-G3, TC-G6 passed.
  Every write of the base scripts landed in the tests' temporary directories.
- B2, B3: the guards in `rebase_links_next.py` (`_refuse_operand`, called in `_main`) and
  `init_skill_next.py` (`_refuse_target`, called in `create_skill`). `skill_utils.py` unchanged.
- B4: `tests/test_script_guards.py` on the copies: 6 passed, 6 subtests passed.
- B5: `.agent/tools/test_rebase_links.py`, the CLI classes `chdir` into `tmp_path`: 44 passed
  against `rebase_links.py`, 44 passed against `rebase_links_next.py` loaded as `rebase_links`.

### Cluster C — narrowed patterns and settings

- C1 base-fail: `tests/test_committed_settings.py` (C state) against the base skill and settings:
  38 failed, 13 passed, 315 subtests passed. The failures are the new reject cases of TASK §4.1,
  the pattern block, the table, the fence list, the pinned sentences and TC-S3's command set.
- C2 narrowing check (`framework-upgrade` §3 step 4), run before the edit, output verbatim:

~~~text
1. each new allow rule and the base rule that covers it:
   Bash(mkdir -p docs/tasks)  <=  ['Bash(mkdir -p docs/*)']
   Bash(mkdir -p docs/plans)  <=  ['Bash(mkdir -p docs/*)']
   Bash(mkdir -p docs/architectures)  <=  ['Bash(mkdir -p docs/*)']
   removed: ['Bash(file *)', 'Bash(mkdir -p .agent/*)', 'Bash(mkdir -p docs/*)', 'Bash(mkdir -p tests/*)']
2. base deny/ask rules: {'deny': [], 'ask': []} -> all present: True
3. every other key equals the base's: True ['env', 'hooks']
4. hook code unchanged: True | names the hook's scripts import: ['argparse', 'atexit', 'codecs', 'json', 'os', 'pathlib', 're', 'skill_utils', 'sys', 'yaml']
   new files beside them: ['.agent/skills/skill-creator/scripts/init_skill_next.py'] | shadowing an imported name: []
NARROWS: True
~~~

  Then `.claude/settings.json`: `Bash(file *)` removed; three exact `mkdir` rules replace the
  three wildcards (+3 −4 lines).
- C3, C4: `skill-safe-commands` 1.4 and the READMEs' Antigravity lists. The settings module: 17
  passed, 340 subtests passed.

### Cluster D — related checks

- D1 base-fail: `tests/test_lockfile_audit.py` with TC-Y1 to TC-Y3: 4 failed (TC-Y1; TC-Y2's three
  subtests), 27 passed; TC-Y3 (formerly TC-L9b) passed.
- D2: `external.py` runs `yarn audit` through `npm_audit_dir`, the copy helper of TASK 111 R5.2;
  `helpers.py` unchanged. Lockfile module: 28 passed, 12 subtests; `security-audit/tests`: 30
  passed.
- D3 base-fail: TC-T1 failed (8 refused commands accepted at the base, and the error text); TC-T2
  passed. `subprocess.run` was replaced in the test, so no refused command ran.
- D4: `ALLOWED_TEST_COMMANDS` in `tool_runner.py`; `schemas.py` and `ORCHESTRATOR.md` list the
  same set. `test_tool_runner.py` and `test_tool_runner_security_contract.py`: 17 passed,
  15 subtests.

### Cluster E — step 4 and wording

- E1 base-fail: `tests/test_run_safety_rules.py` (step 4 to the end of §3, whole blocks): 4 failed.
  They are step 4, the wrapper lead, the `full-robust` gate and the `SKILLS.md` row. That row
  quotes the version F1 changes, so its 3.10 → 3.11 moved into E and the pin stays green.
- E2, E3, E5: step 4 of R7.1, the wrapper lead of R7.2, the gate of R5.2. Pins: 5 passed, 11
  subtests passed.
- E4: R7.3 rewrapped 4 items of `security-audit/SKILL.md`, 2 of `security-audit.md` and 1 of
  `10_security_auditor.md` at 100 columns; their text is unchanged with whitespace collapsed, and
  no line the run added there exceeds 100 characters.
- E6: the SHA-256 of the TASK 111 archive pair as archived in §1:
  - `docs/tasks/task-111-checks-that-cover-what-they-claim.md`
    `4e9dba7206909c3b683a1d3c0c0904cd95f92c928122c759da3a6d685694e08f`
  - `docs/plans/plan-111-checks-that-cover-what-they-claim.md`
    `91be08cbc2703dcc56706f176d80ffe4a6bc4647aaba6024720632b2a7dc3936`

### Cluster F — records

- F1: `security-audit` 3.11 in front matter, H1, `__init__.py`, `run_audit.py` and `VDD.md`
  (`SKILLS.md` in E); its SKILL.md names the `yarn audit` copy.
- F2: v3.37.0 in both changelogs. Register: `CHANGELOG.md` 235 warn at the base and now,
  `CHANGELOG.ru.md` 185 and 185.
- F3: `docs/ARCHITECTURE.md`: the archive script beside the allow-list note; the `run_tests` row.
  Register: 1 warn at the base and now.
- F4: WI-35 `done` (resolution blockquote, `resolved_at`, `resolved_by`); WI-36 and WI-37 filed
  `open`; `docs/BACKLOG.md` index lines in lockstep.

## Cluster G — gates and stage 2

### G1 — gates, by name and in full

Every step of `framework-gates.yml`, run locally (`scratchpad/gates.sh`):

| Gate | Exit | Result |
| :--- | :--- | :--- |
| tooling pytest list | 0 | 399 passed, 66 subtests |
| curated suite | 0 | OK |
| `test_archive_move.py`, `test_script_guards.py` by name | 0 | 20 passed, 27 subtests |
| formalizer selftest / eval selftest | 0 / 0 | 192/192; 78/78 |
| mermaid unit tests | 0 | 650 passed, 1 skipped |
| figure lint probe / references / eval selftest | 0 / 0 / 0 | 98/98 live; 0 error; 225/225 |
| register probe / living sweep | 0 / 0 | 18/18 live; advisory |
| validate skills / prompt references | 0 / 0 | 47/47; 41 resolve |
| positional refs, living corpus | 0 | after the fix below |
| positional refs, archives (advisory) | 1 | no finding in a file this run touched |
| security lint / workflow smoke / loop contract | 0 / 0 / 0 | passed; 25 loops, 0 error |
| loop contract negative fixture | 1 | fails as required |

The living-corpus check first exited 1 on two coordinates of TASK §1, `external.py:54@eb7248f` and
`tool_runner.py:49@eb7248f`, which D2 and D4 moved. TASK §1 states facts at the base, so both now carry
`@eb7248f`, the licensed pinned form. The audit record's round-1 table got the same pin.

Declared paths: every path of `git status` is declared. The archive-pair hashes equal E6.
Register: no edited file gained a `warn` against its base text; the new files report 0, except
this record, whose one long sentence was split.

### G2 — the stage-3 patch

`docs/reviews/framework-audit-112-stage3.diff`, written by `scratchpad/gen_stage3.py`, which holds
the new hunk text and writes no other file. 18 file sections: 16 edits and the deletion of the two
`_next` copies. `git apply --check --whitespace=nowarn` passes. SHA-256 at G2: `bfa7fccf6f3ca82b7a5c0ceb6d776ef279734eae0390df106b953c47e457ecca`. The audit
record stores the patch text after G6 (PLAN G4).

### G3 — base-fail of the stage-3 tests

The test part alone (`git apply --include=tests/test_committed_settings.py`): 18 failed, 13
passed. The failures are the expected set and no other:

- TC-S1, and TC-S3 for the two `mv` rules;
- TC-S7: 6 commands, 2 expected prefixes, the fence pin;
- TC-S8: the archive accept case, the pattern block, the table, the three Antigravity lists.

Then `git apply -R` of the same part; the file's SHA-256 equals its value before.

### G4 — stage 2, round 1 (fingerprint `6ff2e081f2ab`)

**Security audit: `PASS`** (`scan_status: findings`; 0 CRITICAL, 0 HIGH). The scan's two in-scope
hits, in `init_skill_next.py`, are false positives on print text. 16 probes of `archive_move.py`
held. Findings:

| # | Severity | Finding | Fix round 1 |
| :--- | :--- | :--- | :--- |
| M-1 | MEDIUM | the `fd` pattern admits a cluster with a digit, `fd -1x rm` | `-[^-\s]*[xX]`; reject cases |
| M-2 | MEDIUM | `.git` compared case-sensitively; `--path .GIT` wrote into `.git/` (measured, APFS) | casefold, and an ancestor that is `.git` |
| L-1 | LOW | the Antigravity entry names a relative path | the note states it (WI-34 class) |
| L-2 | LOW | the tests match raw text, not text after quote removal | TC-S8 matches after `shlex.split` |
| L-3 | LOW | the yarn copy keeps `packageManager` | the copy drops it; WI-37 updated |
| I-1 | INFO | two error paths of `archive_move.py` end in a traceback | with CR-1 |
| I-2 | INFO | `run_tests` accepts a `cwd` anywhere in the repository (base) | WI-34 class; no change |

**Code review: REJECT** (no CRITICAL or HIGH). Findings:

| # | Severity | Finding | Fix round 1 |
| :--- | :--- | :--- | :--- |
| CR-1 | MEDIUM | an `OSError` other than a refusal ends in a traceback and leaves `docs/tasks/` (overlong name, reproduced) | every `OSError` becomes a refusal with cleanup; TC-A14 |
| CR-2 | MEDIUM | `.git` compared case-sensitively (= M-2) | as M-2 |
| CR-3 | MEDIUM | five mutations of the race defences survive the tests | TC-A15 to TC-A18; TC-A11, TC-A12 assert the path taken |
| CR-4 | LOW | no test that `rebase_links` refuses before any write | TC-G7 |
| CR-5 | LOW | "write inside the working directory only" overclaims through a linked directory | "by path, without resolving links" |
| CR-6 | LOW | "with no option" vs `pytest -q` | "with no other option" |
| CR-7 | LOW | `run_tests` compares a joined string | token tuples |
| CR-8 | LOW | a module planted beside `archive_move.py` would be imported | the script's directory leaves `sys.path` |
| CR-9 | LOW | the definition "under a test directory" excludes `.agent/tools/test_*.py` | D4 and step 4: `test_*.py` or `conftest.py` |
| CR-10 | LOW | a kill between link and unlink leaves two names | Edge Cases row with the recovery |

**Process deviation.** The code reviewer applied the patch in a full copy of the repository under
the scratchpad (`scratchpad/repo`, 75 MB), and left a byte copy of `archive_move.py` and probe roots
there. That is a copy outside version control (`framework-upgrade` §3.1). The orchestrator removed
them after the report; no file in the repository changed.

### G4 — fix round 1

TASK revision 5 states the fixes. Each fix has its test first; the new cases failed before it:

- CR-1, I-1: `_move` turns every `OSError` into a refusal and removes a directory it created; the
  post-link `stat` and the copy's `close` remove the destination on failure. TC-A14 (overlong
  name) failed with a traceback before, passes now. Probe: exit 1, a JSON error, no `docs/tasks/`.
- CR-8: the script's directory leaves `sys.path` before the first import that is not built in.
- CR-3: TC-A15 to TC-A18; TC-A11 asserts `"method": "copy"`, TC-A12 asserts the error names the
  hard links. Five in-memory mutants: the post-link check, the `fstat` re-check, `O_NOFOLLOW` on
  the copy source and the remove after a failed copy are each killed by an in-process case. The
  fifth, no `OSError` conversion, is the code before CR-1, which TC-A14 failed on.
- CR-2 = M-2: `_under_git` in both `_next` copies: a `.git` segment in any case, or an existing
  prefix that is the same directory as `.git`. TC-G2 and TC-G5 gained `.GIT` and a link to `.git`
  and failed before; TC-G7 (one refused operand of two) passed before and after.
- M-1: `fd` excludes `x` or `X` anywhere in a cluster, `-[^-\s]*[xX]`; `fd -1x rm`, `fd -0X rm` and
  `fd -H1x rm` failed before. L-2: TC-S8 matches after `shlex.split`; the quoted cases pass.
- CR-7: `run_tests` compares token tuples; `["pytest -q"]` failed before.
- L-3: the yarn copy drops `packageManager`; TC-Y1 failed before. WI-37 updated.
- CR-9: step 4 and D4: a test module is a `test_*.py` or `conftest.py` file.
- CR-5, CR-6: `ARCHITECTURE.md`, both changelogs and the patch's table row say "compared without
  resolving links"; the `run_tests` row says "no other option".
- L-1, CR-10: the patch adds the relative-path note to the Antigravity entry and an Edge Cases
  row with the recovery after a kill between link and unlink.

Gates after the round: all as G1, `test_archive_move.py` and `test_script_guards.py` 26 passed,
31 subtests; the living corpus clean; no undeclared path; archive-pair hashes unchanged. The patch
was regenerated, `git apply --check` passes, SHA-256 `365301616c156168a05acbb272f8fd2c13ac119acf0dd42150fac0db7c07030d`. G3 on it: the same 18 expected
failures, and the test file restored byte for byte.

### G4 — round 2 verdicts and fix round 2

Round 2 (fingerprint `c9eec26354c4`): the security audit `PASS` (0 CRITICAL, 0 HIGH; L-1 to L-3,
I-1, I-2); the code review `APPROVE` (one MEDIUM, six LOW). Both re-reviews made no copy of the
repository. The orchestrator took the findings in fix round 2, before stage 3 makes the scripts
rule-named; TASK revision 6 states them. Each new case failed before its fix.

- MEDIUM (code review 1): the `sys.path` filter ran when a test loaded the script and dropped
  `.agent/tools` from the test process. It now runs only as `__main__`; TC-A20 pins both sides,
  and `test_archive_move.py` with `test_task_id_tool.py` passes 68.
- `.git` (security L-1, code review 2): `_under_git` compares the real path, links resolved
  before `..`, with the repository's git directories, a worktree's gitfile and `commondir`
  included, case-folded. TC-G2 and TC-G5 gained a link into `.git/hooks`, `..` after a link and a
  worktree gitfile.
- The archive's last name (code review 3, security I-1): after a failed unlink of the source,
  the archive is removed only while the source still holds the moved file. Otherwise it stays,
  and the error says so (TC-A21).
- Surviving mutants (code review 4): TC-A19 (a failed `stat` after the link) and TC-A20.
- `devEngines` (security L-2, code review 6): the yarn copy keeps nine `package.json` fields only.
- Shell spellings (security L-3): the lookaheads use `[\s\S]*`; a command with a line
  continuation or `$'…'` quoting is not safe; TC-S8 gained the continuation cases and the rule.
- The exemption (code review 7): a test module is one that no hook or listed script runs or
  imports.
- The Edge Cases row of the patch (code review 5) covers an interrupted copy.

Recorded, no change: security I-2, an operator's `PYTHONPATH` or `sitecustomize` loads before any
filter, for every `python3` rule. Two prunable worktrees in other sessions' scratchpads, which the
auditor saw in `git worktree list`, are not this run's.

Gates after the round: as G1; new modules 31 passed, 34 subtests; no undeclared path; archive
hashes unchanged. The patch was regenerated: `git apply --check` passes, SHA-256 `02f59be1aab41c508899427b05ce5dfb833621c980e6b58cda78d6e4fc20bada`. G3: the
same 18 expected failures; the test file restored byte for byte.

### G4 — round 3 verdicts and fix round 3

Round 3 (fingerprint `a3cdce92240f`): the code review `APPROVE` (five LOW), the security audit
`PASS` (two LOW, two INFO). The orchestrator took the cheap ones in fix round 3 and set a bound:
after this round, a remaining LOW is recorded, not iterated. TASK revision 7 states the round.

- `_undo_after_failed_unlink` tells a vanished source from an unconfirmed one; the exit-code
  docstring and the patch's Steps 5 and 7.6 name the one exit 1 that keeps the archive.
  TC-A22 kills the mutant that ignores the inode.
- `_git_dirs` finds the git directory of the nearest ancestor with a `.git`; `_under_git`
  compares every existing ancestor of the real path by file identity (`samestat`), so a firmlink
  or a Unicode normalisation does not hide `.git`. TC-G2 gained the subdirectory case and, on
  darwin, the `/System/Volumes/Data` firmlink.
- `skill-safe-commands`: a command with `$"…"` quoting, a parameter or brace expansion, or an
  unquoted glob for `rg`, `fd` and `git` is not safe either.
- The patch's Edge Cases row: when the two names differ, both are reported and neither is
  removed.

Recorded as residuals (TASK §7): the two races with a concurrent writer of `docs/`; a link into a
nested repository's `.git` (WI-34); what the kept `package.json` fields can still make yarn fetch,
which runs nothing (security I-2).

Gates after the round: all as G1; no undeclared path; no new register `warn`; archive hashes
unchanged. Patch regenerated, `git apply --check` passes, SHA-256 `7ce6dfef3c86ec5d16bc97ffef4407fbd1574a755cd127f05a09cdf601ea939e`. G3: the same 18
expected failures; the test file restored byte for byte.

### G4 — stage 2 closes (fingerprint `8cd7f8b7b9ec`)

The code review `APPROVE` and the security audit `PASS`, with no new CRITICAL, HIGH or MEDIUM
finding. The firmlink and NFD link cases are refused. Residuals, recorded, not iterated:

- a link from inside a nested checkout to the outer repository's `.git` (WI-34 class);
- the two races with a concurrent writer of `docs/` (TASK §7).

The code review's other residual, no case for a source `stat` error after a failed unlink, got
TC-A23, a test-only change (D4): both names remain. Archive tests: 25 passed, 21 subtests.

### G5 — reference resolver (§4.5)

`check_positional_refs.py --targets-changed`, first without `--fix`: no reference in the TASK 111
archive pair, so no rebuild. Its errors before the repair: cross-repository coordinates in
`plan-103` and `framework-audit-105`, and `review-095-independent.md:35` twice. Only the
`REFERENT_MOVED` there came from this change: E5 moved `full-robust.md:82` to 83. Then `--fix`
repaired that one coordinate. Files a repair touched:

- `docs/reviews/review-095-independent.md` (1 line)

Archive-pair hashes unchanged after the repair.

### G6 — gates after §4.5

Every gate as G1; `git apply --check` of the patch passes; no undeclared path.

### The stage-3 patch, stored

SHA-256 `7ce6dfef3c86ec5d16bc97ffef4407fbd1574a755cd127f05a09cdf601ea939e`, the text below byte for byte. `framework-upgrade` §5 removes the `.diff` file;
this copy stays with the record.

~~~~~diff
diff --git a/.agent/skills/artifact-management/SKILL.md b/.agent/skills/artifact-management/SKILL.md
--- a/.agent/skills/artifact-management/SKILL.md
+++ b/.agent/skills/artifact-management/SKILL.md
@@ -2,7 +2,7 @@
 name: artifact-management
 description: "Rules for managing local .AGENTS.md and global artifacts (TASK.md, PLAN.md, ARCHITECTURE.md, KNOWN_ISSUES.md, BACKLOG.md)."
 tier: 0
-version: 1.4
+version: 1.5
 ---
 # Artifact Management
 
@@ -71,7 +71,9 @@
 
 > See **`skill-safe-commands`** for the complete list of commands safe for auto-execution.
 
-Key commands: `mv docs/TASK.md docs/tasks/...`, `mv docs/PLAN.md docs/plans/...`, `ls`, `cat` — read-only validation.
+Key commands: `python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/...` and
+`python3 .agent/tools/archive_move.py docs/PLAN.md docs/plans/...` (the archive script); `ls`,
+`cat` — read-only validation.
 
 ## Protocol
 1. **Read First:** Before starting work, read relevant artifacts.
diff --git a/.agent/skills/skill-archive-task/SKILL.md b/.agent/skills/skill-archive-task/SKILL.md
--- a/.agent/skills/skill-archive-task/SKILL.md
+++ b/.agent/skills/skill-archive-task/SKILL.md
@@ -2,7 +2,7 @@
 name: skill-archive-task
 description: "Complete protocol for archiving TASK.md and PLAN.md (lockstep) with ID generation. Single source of truth for archiving."
 tier: 1
-version: 2.0
+version: 2.1
 ---
 # Task Archiving Protocol
 
@@ -124,15 +124,22 @@
 
 ### Step 5: Archive (Move File)
 
-**Collision guard first.** `mv` overwrites, and Step 3's conflict check sees *parent* archives
-only — a destination shaped like a sub-task (`task-096-01-x.md`) is invisible to it.
-
-```bash
-test -e docs/tasks/{filename} && echo "STOP: target exists" || mv docs/TASK.md docs/tasks/{filename}
-```
+The archive script moves the file and guards the destination. Step 3's conflict check sees
+*parent* archives only, so a destination shaped like a sub-task (`task-096-01-x.md`) is invisible
+to it; the script refuses that too, as it refuses every existing destination. It also refuses any
+destination but `docs/tasks/task-<ID>-<slug>.md`, a link, and a source with a second hard link. It
+creates `docs/tasks/` when it is absent.
+
+```bash
+python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/{filename}
+```
+
+- Exit `0`: moved. A non-zero exit means **STOP** and report the script's JSON error. Nothing
+  moved, unless the error says the archive was kept; then follow the Edge Cases row.
 
 > [!IMPORTANT]
-> The `mv` is **SAFE TO AUTO-RUN**. Do NOT wait for user approval.
+> The script is **SAFE TO AUTO-RUN**: one allow rule names it, and it moves nothing but the two
+> archive pairs (`skill-safe-commands`). Do NOT wait for user approval.
 
 ### Step 5.5: Rebase the moved document's links (MANDATORY)
 
@@ -168,8 +175,7 @@
       non-zero when a link it rewrote fails to resolve.
 
 **If validation fails:**
-- Check if mv command returned error
-- If `docs/TASK.md` still exists: retry mv or notify user
+- Report the script's exit code and JSON error to the user; a failed move is not retried.
 - DO NOT create new TASK.md until validation passes
 
 ## PLAN.md Archiving (Lockstep)
@@ -206,11 +212,8 @@
     DO NOT archive PLAN.md — Planner overwrites it in place → DONE
 ```
 
-**7.3 — Ensure destination** (idempotent, SAFE TO AUTO-RUN):
-
-```bash
-mkdir -p docs/plans
-```
+**7.3 — Destination.** The script of 7.6 creates `docs/plans/` when it is absent; nothing runs
+here.
 
 **7.4 — Derive filename** (NO new ID generation):
 
@@ -229,19 +232,18 @@
 `archive_protocol.archive_task(allow_renumber=True)`; there TASK and PLAN both take the corrected
 ID and stay paired.
 
-**7.5 — Collision guard:**
-
-```
-IF exists("docs/plans/{plan_filename}"):
-    STOP. Do NOT overwrite. Report to user:
-      "Plan archive collision: docs/plans/{plan_filename} already exists."
-```
+**7.5 — Collision guard.** The script of 7.6 refuses an existing destination with exit 1 and
+moves nothing. Report it to the user: "Plan archive collision: docs/plans/{plan_filename} already
+exists."
 
 **7.6 — Archive (move):**
 
 ```bash
-mv docs/PLAN.md docs/plans/{plan_filename}
-```
+python3 .agent/tools/archive_move.py docs/PLAN.md docs/plans/{plan_filename}
+```
+
+A non-zero exit means **STOP** and report. Nothing moved, unless the error says the archive was
+kept (Edge Cases).
 
 **7.6.5 — Rebase the plan's links** (mirrors Step 5.5):
 
@@ -268,7 +270,7 @@
 ASSERT NOT exists("docs/PLAN.md")
 ASSERT exists("docs/plans/{plan_filename}")
 ASSERT every link denoted before the move still resolves   # rebase_links exit code
-IF validation fails: retry mv once, else notify user.
+IF validation fails: notify the user; a failed move is not retried.
 ```
 
 ### Edge Cases
@@ -277,7 +279,8 @@
 |------|----------|
 | `docs/PLAN.md` absent | Skip silently (7.1). Not an error — many tasks reach analysis but not planning. |
 | Task refinement (same task) | Step 7.2 returns early. PLAN.md is overwritten in place by the Planner. |
-| `docs/plans/` missing | `mkdir -p` in 7.3 creates it. |
+| `docs/plans/` missing | The script of 7.6 creates it. |
+| A move killed between its link (or copy) and its unlink, or an error that says the archive was kept | `docs/TASK.md` (or `docs/PLAN.md`) and the archive may both remain, and the script refuses again. Compare them with `cmp`. Equal: remove the `docs/` name by hand. Different: report both to the user; never remove a name whose content exists nowhere else. |
 | Corrected `used_id` | Unreachable under this protocol: Step 3 runs correction OFF and Step 4 stops on a mismatch. Only `archive_task(allow_renumber=True)` reaches it, and there 7.4 keeps TASK and PLAN paired. |
 | **Orphan PLAN.md** (PLAN.md exists, no TASK.md) | Step 1 skipped archiving (no TASK.md) → Step 7 is never reached. The orphan PLAN.md is **left in place**. Warn the user it may be stale. PLAN.md has no independent ID, so it cannot be safely archived alone — this is a deliberate limitation. |
 
@@ -286,25 +289,29 @@
 > See **`skill-safe-commands`** for the authoritative list of commands safe for auto-execution.
 
 Key commands for this skill:
-- `mv docs/TASK.md docs/tasks/...` — archiving TASK.md
-- `mv docs/PLAN.md docs/plans/...` — archiving PLAN.md (lockstep)
-- `mkdir -p docs/plans` — ensure PLAN archive destination exists
+- `python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/...` — archiving TASK.md
+- `python3 .agent/tools/archive_move.py docs/PLAN.md docs/plans/...` — archiving PLAN.md
+  (lockstep); the script creates `docs/plans/`
+- `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py` — ID and links
 - `ls`, `cat` — validation
 
 
 ## Safety Boundaries
 
-This skill performs **file mutations** (`mv`, `mkdir`). The following boundaries apply:
-
-- **Move, never delete.** Archiving uses `mv` only — `docs/TASK.md` / `docs/PLAN.md`
-  content is relocated, never destroyed.
-- **No overwrite.** Step 5 and Step 7.5 enforce collision guards: if the target archive
-  filename already exists, **STOP** and report — never overwrite an existing archive.
+This skill performs **file mutations**: the archive script's move, and its creation of
+`docs/tasks/` or `docs/plans/`. The following boundaries apply:
+
+- **Move, never delete.** Archiving uses `archive_move.py` only — `docs/TASK.md` /
+  `docs/PLAN.md` content is relocated, never destroyed. A failure after the destination exists
+  removes the destination and keeps the source.
+- **No overwrite.** The script refuses an existing destination (Steps 5 and 7.5): **STOP** and
+  report — never overwrite an existing archive.
 - **Lockstep integrity.** PLAN.md is archived only after TASK.md archiving is validated
   (Step 6). A failed TASK archive aborts the PLAN archive.
 - **Living documents untouched.** `docs/ARCHITECTURE.md` is never moved or archived.
-- **Validate before proceeding.** Each `mv` is followed by an existence assertion
-  (Steps 6, 7.7); on failure, retry once then notify the user — do not continue blindly.
+- **Validate before proceeding.** Each move is followed by an existence assertion
+  (Steps 6, 7.7); on failure, notify the user — a failed move is not retried, and the run does
+  not continue blindly.
 
 ## Integration
 
@@ -329,11 +336,9 @@
    `status: "conflict"` → **STOP**; the operator decides. Sub-task files matching
    `task-{OLD_ID}-<digits>-*` are **not** a conflict.
 6. **Step 4** — assert `id_in_filename == {OLD_ID}`. This step never assigns.
-7. **Step 5** — collision guard, then move:
+7. **Step 5** — move; the script refuses an existing destination:
    ```bash
-   test -e docs/tasks/task-{OLD_ID}-{old-slug}.md \
-     && echo "STOP: target exists" \
-     || mv docs/TASK.md docs/tasks/task-{OLD_ID}-{old-slug}.md
+   python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/task-{OLD_ID}-{old-slug}.md
    ```
 8. **Step 5.5** — rebase the moved document's links. `docs/tasks/` is one level deeper, so every
    relative link now denotes something else. `docs/PLAN.md` is a slot, so pass the pairing Step 7
@@ -348,8 +353,9 @@
    Exit `3` lists links left alone deliberately — report them, never guess a target.
 9. **Step 6** — validate: `docs/TASK.md` gone ✓, archive present ✓, links still resolve ✓.
 10. **Step 7** — PLAN lockstep. `docs/PLAN.md` exists? → YES.
-    - `mkdir -p docs/plans`, reuse `{OLD_ID}` + `{old-slug}` from the TASK archive above.
-    - Collision guard, then `mv docs/PLAN.md docs/plans/plan-{OLD_ID}-{old-slug}.md`.
+    - Reuse `{OLD_ID}` + `{old-slug}` from the TASK archive above.
+    - `python3 .agent/tools/archive_move.py docs/PLAN.md docs/plans/plan-{OLD_ID}-{old-slug}.md`;
+      the script creates `docs/plans/` and refuses an existing destination.
     - **Step 7.6.5** — rebase, with `docs/TASK.md` mapped to the archive it just became:
       ```bash
       python3 .agent/tools/rebase_links.py docs/plans/plan-{OLD_ID}-{old-slug}.md \
diff --git a/.agent/skills/skill-creator/SKILL.md b/.agent/skills/skill-creator/SKILL.md
--- a/.agent/skills/skill-creator/SKILL.md
+++ b/.agent/skills/skill-creator/SKILL.md
@@ -2,7 +2,7 @@
 name: skill-creator
 description: Use when creating new Agent Skills, upgrading existing skills, running evals to test a skill, benchmarking skill performance, or optimizing a skill's description for better triggering accuracy. Guidelines for Gold Standard skill structures.
 tier: 2
-version: 2.4
+version: 2.5
 ---
 # Skill Creator Guide
 
@@ -117,11 +117,11 @@
 
 ### Script Contract
 - **Primary Commands**:
-  - `python3 scripts/init_skill.py <name> --tier <N> --path <ABSOLUTE-DIR>` — generate a
-    skill skeleton. Pass `--path` absolute: `init_skill.py:143` resolves it with
-    `os.path.abspath()`, i.e. against the **current working directory**, so the same
-    relative path lands in a different place depending on where you invoked it from —
-    run it from `scripts/` and the skill is scaffolded outside the repository.
+  - `python3 scripts/init_skill.py <name> --tier <N> --path <DIR>` — generate a skill
+    skeleton. Run it from the project root. `--path` and a path-shaped `<name>` resolve against
+    the **current working directory**, and the skill directory must lie inside it, outside
+    `.git/`, by its absolute path without resolving links. Anything else exits 1 and creates
+    nothing (TASK 112 R4.2).
   - `python3 scripts/validate_skill.py <skill-path> [--json] [--strict]` — validate
     structure and compliance
   - `python3 scripts/package_skill.py <skill-path> <output-dir>` — package into a `.skill`
diff --git a/.agent/skills/skill-creator/scripts/init_skill.py b/.agent/skills/skill-creator/scripts/init_skill.py
--- a/.agent/skills/skill-creator/scripts/init_skill.py
+++ b/.agent/skills/skill-creator/scripts/init_skill.py
@@ -9,6 +9,90 @@
 import skill_utils
 from skill_utils import install_human_channel
 
+def _git_dirs(cwd):
+    """The repository's git directories, as real paths (TASK 112 R4.1).
+
+    The `.git` of the working directory, or of its nearest ancestor that has one. In a linked
+    worktree `.git` is a file naming the worktree's git directory, whose `commondir` names the
+    main one; both count.
+    """
+    here = os.path.realpath(cwd)
+    while True:
+        dot = os.path.join(here, ".git")
+        if os.path.isdir(dot):
+            return [os.path.realpath(dot)]
+        if os.path.isfile(dot):
+            break
+        parent = os.path.dirname(here)
+        if parent == here:
+            return []
+        here = parent
+    try:
+        with open(dot, encoding="utf-8") as fh:
+            line = fh.readline().strip()
+    except (OSError, UnicodeDecodeError):
+        return []
+    if not line.startswith("gitdir:"):
+        return []
+    gitdir = os.path.realpath(os.path.join(here, line[len("gitdir:"):].strip()))
+    dirs = [gitdir]
+    try:
+        with open(os.path.join(gitdir, "commondir"), encoding="utf-8") as fh:
+            dirs.append(os.path.realpath(os.path.join(gitdir, fh.read().strip())))
+    except (OSError, UnicodeDecodeError):
+        pass
+    return dirs
+
+
+def _under_git(path, cwd):
+    """True when `path` lies under the repository's git directory (TASK 112 R4.1).
+
+    A segment named `.git` in any letter case counts: a case-insensitive file system resolves
+    `.GIT` to `.git`. So does any existing ancestor of the real path (links resolved before `..`)
+    that is a git directory of `_git_dirs` by file identity, which a firmlink or a Unicode
+    normalisation of the spelling does not hide.
+    """
+    absolute = os.path.normpath(os.path.join(cwd, path))
+    segments = os.path.relpath(absolute, cwd).split(os.sep)
+    if any(segment.casefold() == ".git" for segment in segments):
+        return True
+    gits = []
+    for git in _git_dirs(cwd):
+        try:
+            gits.append(os.stat(git))
+        except OSError:
+            pass
+    probe = os.path.realpath(os.path.join(cwd, path))
+    while gits:
+        try:
+            st = os.stat(probe)
+        except OSError:
+            st = None
+        if st is not None and any(os.path.samestat(st, git) for git in gits):
+            return True
+        parent = os.path.dirname(probe)
+        if parent == probe:
+            break
+        probe = parent
+    return False
+
+def _refuse_target(skill_dir):
+    """Why `create_skill` refuses this directory, or None (TASK 112 R4.2).
+
+    `Bash(python3 .agent/skills/skill-creator/scripts/init_skill.py *)` approves any `--path` and
+    any path-shaped name. A directory outside the working directory, by its absolute path
+    normalised without resolving links, is refused, and so is one under `.git/`. Links are not
+    resolved: in a consumer project `.agent/skills` can be a link into the framework.
+    """
+    cwd = os.getcwd()
+    absolute = os.path.normpath(os.path.join(cwd, skill_dir))
+    if os.path.commonpath([absolute, cwd]) != cwd or absolute == cwd:
+        return "lies outside the working directory"
+    if _under_git(skill_dir, cwd):
+        return "lies under .git/"
+    return None
+
+
 def create_skill(name, base_path, tier_value, config):
     """
     Creates a new skill directory with the standard structure.
@@ -22,7 +106,12 @@
     # Sanitize name
     safe_name = name.lower().replace(" ", "-").replace("_", "-")
     skill_dir = os.path.join(base_path, safe_name)
-    
+
+    reason = _refuse_target(skill_dir)
+    if reason:
+        print(f"Error: Skill directory '{skill_dir}' {reason}.")
+        sys.exit(1)
+
     if os.path.exists(skill_dir):
         print(f"Error: Skill directory '{skill_dir}' already exists.")
         sys.exit(1)
diff --git a/.agent/skills/skill-phase-context/SKILL.md b/.agent/skills/skill-phase-context/SKILL.md
--- a/.agent/skills/skill-phase-context/SKILL.md
+++ b/.agent/skills/skill-phase-context/SKILL.md
@@ -2,7 +2,7 @@
 name: skill-phase-context
 description: "Skill loading tiers: TIER 0 (always), TIER 1 (phase-triggered), TIER 2 (extended). Defines when to load which skills."
 tier: 2
-version: 1.2
+version: 1.3
 ---
 # Phase Context Loading Protocol
 
@@ -21,7 +21,7 @@
 | Skill | Tokens | Why Always Load |
 |-------|--------|-----------------|
 | `core-principles` | ~519 | Anti-hallucination rules, Stub-First, Documentation First |
-| `skill-safe-commands` | ~927 | **Enables automation** — `mv`, `ls`, `git`, tests auto-run |
+| `skill-safe-commands` | ~927 | **Enables automation** — the archive script, `ls`, `git`, tests auto-run |
 | `artifact-management` | ~636 | Archiving protocol, file management, dual state tracking |
 | **TOTAL** | **~2,082** | **Non-negotiable system foundation** |
 
diff --git a/.agent/skills/skill-safe-commands/SKILL.md b/.agent/skills/skill-safe-commands/SKILL.md
--- a/.agent/skills/skill-safe-commands/SKILL.md
+++ b/.agent/skills/skill-safe-commands/SKILL.md
@@ -20,9 +20,10 @@
 | **Symlink-aware** | `ls -L`, `rg --follow` / `rg -L`, `fd -L` | Read-only, but follow symlinks into framework dirs (`.agent/`, `.agents/`, `.cursor/skills/`, `System/`, `.agentic-development/`). Plain `find`/`ls`/`rg` do **not** descend into symlinked directories |
 | **File info** | `stat`, `du`, `df` | Informational only |
 | **Git read** | `git status`; `git log`, `git diff`, `git show` without `--output`; `git branch`, `git remote`, `git tag` with no argument | Read-only git operations |
+| **Archiving** | `python3 .agent/tools/archive_move.py` | Moves `docs/TASK.md` and `docs/PLAN.md` into `docs/tasks/` and `docs/plans/`; refuses every other operand (TASK 112) |
 | **Directory** | `mkdir -p docs/tasks`, `mkdir -p docs/plans`, `mkdir -p docs/architectures` | Idempotent; three fixed directories |
 | **Tool calls** | `generate_task_archive_filename`, `list_directory`, `read_file` | Native tools |
-| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py`, `python3 .agent/skills/artifact-formalizer/evals/grade_run.py`, `python3 System/scripts/doctor.py` | Framework automation |
+| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py`, `python3 .agent/skills/artifact-formalizer/evals/grade_run.py`, `python3 System/scripts/doctor.py` | Framework automation; `rebase_links.py` and `init_skill.py` write only inside the working directory, compared without resolving links |
 | **Testing** | `python -m pytest`, `python3 -m pytest`, `npm test`, `cargo test`, with no argument | Their options can run a program, delete a directory or overwrite a file (TASK 111 D14) |
 
 > [!IMPORTANT]
@@ -49,6 +50,10 @@
   wherever they stand. ripgrep 14.1.1 rejects an abbreviated long option; the `fd` pattern excludes
   every long option that starts with `--exe`, and `x` or `X` anywhere in a short-option cluster,
   digits included (`fd -1x`).
+- **Archiving runs through a script.** `archive_move.py` accepts `docs/TASK.md` with
+  `docs/tasks/task-<ID>-<slug>.md` and `docs/PLAN.md` with `docs/plans/plan-<ID>-<slug>.md`, and
+  refuses every other operand, a link and an existing file. The pattern admits any operand
+  because the script is the guard (TASK 112 R1).
 - **No `file`.** `file` is off this list: `-C`, and its abbreviation `--co`, write a compiled
   magic file (TASK 112 D2).
 - **An allow rule names its command whole.** `X *` matches `X` with arguments; `X*` also matches
@@ -84,6 +89,9 @@
 # Git read operations (the boundary keeps `git difftool -x <program>` out; `--output` writes a file)
 ^git\s+(status|log|diff|show)(?![\s\S]*\s--output)(\s|$)
 ^git\s+(branch|remote|tag)$
+
+# Archiving: the script refuses every operand but the two archive pairs
+^python3\s+\.agent/tools/archive_move\.py(\s|$)
 
 # Directory creation (three fixed directories)
 ^mkdir\s+-p\s+docs/(tasks|plans|architectures)$
@@ -131,7 +139,7 @@
 
 **Antigravity Users:**
 - Add the command list below to "Allow List Terminal Commands" setting in IDE options:
-  `ls,cat,head,tail,grep,wc,stat,du,df,git status`
+  `ls,cat,head,tail,grep,wc,stat,du,df,git status,python3 .agent/tools/archive_move.py`
 - Antigravity matches an entry as an exact word or token prefix, so `ls` does not admit `lsof`
   (antigravity.google/docs/permissions, read 2026-10-06). A chain or a pipeline of listed
   commands still matches, and so does a simple file redirect, which writes. A command or process
@@ -139,6 +147,9 @@
 - An entry cannot exclude an option, so the list names only commands with no option that writes
   or runs a program. `rg`, `fd`, `mkdir` and the test runners ask; from `git`, only `git status`
   is listed. The agent's `SafeToAutoRun` still rejects a redirect (Troubleshooting item 1).
+  `python3 .agent/tools/archive_move.py` admits any operand as a prefix entry; the script refuses
+  every operand but the two archive pairs. Its path is relative, like every framework-script
+  pattern, so the agent runs it from the project root (WI-34).
 
 ### Troubleshooting
 If the IDE still requests approval for commands listed here:
diff --git a/.agent/tools/rebase_links.py b/.agent/tools/rebase_links.py
--- a/.agent/tools/rebase_links.py
+++ b/.agent/tools/rebase_links.py
@@ -296,6 +296,95 @@
         with open(path, "w", encoding="utf-8", newline="") as fh:
             fh.write(new_text)
     return changed, records
+
+
+def _git_dirs(cwd):
+    """The repository's git directories, as real paths (TASK 112 R4.1).
+
+    The `.git` of the working directory, or of its nearest ancestor that has one. In a linked
+    worktree `.git` is a file naming the worktree's git directory, whose `commondir` names the
+    main one; both count.
+    """
+    here = os.path.realpath(cwd)
+    while True:
+        dot = os.path.join(here, ".git")
+        if os.path.isdir(dot):
+            return [os.path.realpath(dot)]
+        if os.path.isfile(dot):
+            break
+        parent = os.path.dirname(here)
+        if parent == here:
+            return []
+        here = parent
+    try:
+        with open(dot, encoding="utf-8") as fh:
+            line = fh.readline().strip()
+    except (OSError, UnicodeDecodeError):
+        return []
+    if not line.startswith("gitdir:"):
+        return []
+    gitdir = os.path.realpath(os.path.join(here, line[len("gitdir:"):].strip()))
+    dirs = [gitdir]
+    try:
+        with open(os.path.join(gitdir, "commondir"), encoding="utf-8") as fh:
+            dirs.append(os.path.realpath(os.path.join(gitdir, fh.read().strip())))
+    except (OSError, UnicodeDecodeError):
+        pass
+    return dirs
+
+
+def _under_git(path, cwd):
+    """True when `path` lies under the repository's git directory (TASK 112 R4.1).
+
+    A segment named `.git` in any letter case counts: a case-insensitive file system resolves
+    `.GIT` to `.git`. So does any existing ancestor of the real path (links resolved before `..`)
+    that is a git directory of `_git_dirs` by file identity, which a firmlink or a Unicode
+    normalisation of the spelling does not hide.
+    """
+    absolute = os.path.normpath(os.path.join(cwd, path))
+    segments = os.path.relpath(absolute, cwd).split(os.sep)
+    if any(segment.casefold() == ".git" for segment in segments):
+        return True
+    gits = []
+    for git in _git_dirs(cwd):
+        try:
+            gits.append(os.stat(git))
+        except OSError:
+            pass
+    probe = os.path.realpath(os.path.join(cwd, path))
+    while gits:
+        try:
+            st = os.stat(probe)
+        except OSError:
+            st = None
+        if st is not None and any(os.path.samestat(st, git) for git in gits):
+            return True
+        parent = os.path.dirname(probe)
+        if parent == probe:
+            break
+        probe = parent
+    return False
+
+def _refuse_operand(path):
+    """Why `_main` refuses to rewrite this file operand, or None (TASK 112 R4.1).
+
+    `Bash(python3 .agent/tools/rebase_links.py *)` approves any operand, and the rewrite writes the
+    file in place. A file outside the working directory, by its absolute path normalised without
+    resolving links, is refused; so is a file under `.git/` (`_under_git`), a symbolic link, and a
+    file with a second hard link, which would write through to another name. `rebase_file()` keeps
+    no such guard: `archive_protocol.py` calls it with temporary paths.
+    """
+    cwd = os.getcwd()
+    absolute = os.path.normpath(os.path.join(cwd, path))
+    if os.path.commonpath([absolute, cwd]) != cwd or absolute == cwd:
+        return "lies outside the working directory"
+    if _under_git(path, cwd):
+        return "lies under .git/"
+    if os.path.islink(path):
+        return "is a symbolic link"
+    if os.path.exists(path) and os.lstat(path).st_nlink != 1:
+        return "has a second hard link"
+    return None
 
 
 def _main(argv=None):
@@ -336,6 +425,12 @@
             return 2
         slot, archive = pair.split("=", 1)
         slot_map[slot.strip()] = archive.strip()
+
+    for path in args.files:
+        reason = _refuse_operand(path)
+        if reason:
+            print(json.dumps({"ok": False, "error": f"{path}: {reason}"}), file=sys.stderr)
+            return 2
 
     report, warned, failed, pending = [], False, False, []
     for path in args.files:
diff --git a/.claude/settings.json b/.claude/settings.json
--- a/.claude/settings.json
+++ b/.claude/settings.json
@@ -22,8 +22,6 @@
       "Bash(git branch)",
       "Bash(git remote)",
       "Bash(git tag)",
-      "Bash(mv docs/TASK.md docs/tasks/*)",
-      "Bash(mv docs/PLAN.md docs/plans/*)",
       "Bash(mkdir -p docs/tasks)",
       "Bash(mkdir -p docs/plans)",
       "Bash(mkdir -p docs/architectures)",
@@ -31,6 +29,7 @@
       "Bash(python3 -m pytest)",
       "Bash(npm test)",
       "Bash(cargo test)",
+      "Bash(python3 .agent/tools/archive_move.py *)",
       "Bash(python3 .agent/skills/skill-session-state/scripts/update_state.py *)",
       "Bash(python3 .agent/tools/task_id_tool.py *)",
       "Bash(python3 .agent/skills/skill-creator/scripts/validate_skill.py *)",
diff --git a/AGENTS.md b/AGENTS.md
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -51,7 +51,7 @@
 
 ### Safe Commands (Auto-Run without Approval)
 > **MANDATORY**: You MUST read **`skill-safe-commands`** to load the authoritative list of auto-run commands.
-> All commands listed in that skill (including `mv`, `ls`, the read forms of `git` and bare test runs) are `SafeToAutoRun: true`.
+> All commands listed in that skill (including the archive script `python3 .agent/tools/archive_move.py`, `ls`, the read forms of `git` and bare test runs) are `SafeToAutoRun: true`.
 > *(Note: detailed Regex patterns for IDE configuration are defined in the skill file)*
 
 ### Session State Persistence
diff --git a/GEMINI.md b/GEMINI.md
--- a/GEMINI.md
+++ b/GEMINI.md
@@ -54,7 +54,7 @@
 
 ### Safe Commands (Auto-Run)
 > **MANDATORY**: You MUST read **`skill-safe-commands`** to load the authoritative list of auto-run commands.
-> All commands listed in that skill (including `mv`, `ls`, the read forms of `git` and bare test runs) are `SafeToAutoRun: true`.
+> All commands listed in that skill (including the archive script `python3 .agent/tools/archive_move.py`, `ls`, the read forms of `git` and bare test runs) are `SafeToAutoRun: true`.
 
 ### Session State Persistence
 - **MANDATORY**: After every phase boundary, you **MUST** immediately execute `python3 .agent/skills/skill-session-state/scripts/update_state.py --mode "[Mode]" --task "[TaskName]" --status "[Status]" --summary "[Summary]"` to persist context.
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -112,7 +112,7 @@
 3.  **Workflows**: (Optional) Use `.agent/workflows/` for automated sequences.
 4.  **Auto-Run Permissions**: To enable autonomous command execution, add the following to **Allow List Terminal Commands** in IDE Settings:
     ```text
-    ls,cat,head,tail,grep,wc,stat,du,df,git status
+    ls,cat,head,tail,grep,wc,stat,du,df,git status,python3 .agent/tools/archive_move.py
     ```
 
 #### 🟠 Option C: Claude Code (Native)
diff --git a/README.ru.md b/README.ru.md
--- a/README.ru.md
+++ b/README.ru.md
@@ -112,7 +112,7 @@
 3.  **Сценарии**: (Опционально) Используйте `.agent/workflows/` для автоматизированных последовательностей.
 4.  **Автономный режим**: Добавьте следующие команды в **Allow List Terminal Commands** в настройках IDE:
     ```text
-    ls,cat,head,tail,grep,wc,stat,du,df,git status
+    ls,cat,head,tail,grep,wc,stat,du,df,git status,python3 .agent/tools/archive_move.py
     ```
 
 #### 🟠 Вариант В: Claude Code (Нативно)
diff --git a/System/Docs/SKILL_TIERS.md b/System/Docs/SKILL_TIERS.md
--- a/System/Docs/SKILL_TIERS.md
+++ b/System/Docs/SKILL_TIERS.md
@@ -15,7 +15,7 @@
 | Skill | Tier | Description |
 |-------|------|-------------|
 | `core-principles` | 0 | Anti-hallucination rules, Stub-First methodology |
-| `skill-safe-commands` | 0 | **Enables automation** — auto-run for `mv`, `ls`, `git`, tests |
+| `skill-safe-commands` | 0 | **Enables automation** — auto-run for the archive script, `ls`, `git`, tests |
 | `artifact-management` | 0 | Archiving protocol, file management |
 | `skill-session-state` | 0 | Persist/Restore session context (Mode, Task) |
 
diff --git a/tests/run_tests.py b/tests/run_tests.py
--- a/tests/run_tests.py
+++ b/tests/run_tests.py
@@ -118,6 +118,9 @@
     "test_lockfile_audit",
     # TASK 111 retro (R7) — a hook is registered last; an unfinished review is INCOMPLETE.
     "test_run_safety_rules",
+    # TASK 112 — the archive script and the guards of the scripts that allow rules run (WI-35).
+    "test_archive_move",
+    "test_script_guards",
 )
 
 
diff --git a/tests/test_committed_settings.py b/tests/test_committed_settings.py
--- a/tests/test_committed_settings.py
+++ b/tests/test_committed_settings.py
@@ -12,8 +12,9 @@
 * the repository ignores the operator's local settings file (``TC-S4``);
 * the settings hold `env`, `permissions.allow` and the one PostToolUse hook of the base, nothing
   else (``TC-S6``);
-* every part of every shell block of `skill-archive-task` matches a committed rule, except the
-  `test -e` guard that the archive script absorbs (``TC-S7``, TASK 111 D13);
+* every part of every shell block of `skill-archive-task` matches a committed rule; no part runs
+  `mv`, `test` or `mkdir`; each archive command calls `archive_move.py` with operands the script
+  accepts (``TC-S7``, TASK 111 D13, TASK 112 R6.2);
 * `skill-safe-commands`, the READMEs' Antigravity lists, `GEMINI.md` and `AGENTS.md` state the
   limit of R2.7 for every vendor; the pattern block, the command table and the fence lists equal
   their reviewed text; table and patterns name the same commands; no pattern admits an option that
@@ -22,6 +23,7 @@
 A fence is read as CommonMark reads it: three or more backticks or tildes, any info string. A shell
 fence is one whose first info word is `bash`, `sh`, `shell`, `zsh` or `console`.
 """
+import importlib.util
 import json
 import re
 import shlex
@@ -33,11 +35,10 @@
 ARCHIVE_SKILL = PROJECT_ROOT / ".agent" / "skills" / "skill-archive-task" / "SKILL.md"
 SAFE_SKILL = PROJECT_ROOT / ".agent" / "skills" / "skill-safe-commands" / "SKILL.md"
 
-#: TASK 112 Appendix A before stage 3: the two `mv` rules stay until the archive script's rule
-#: replaces them. A rule joins the committed file only when `skill-safe-commands` lists its command,
-#: `framework-gates.yml` runs its script, or a test of `tests/` pins it (TASK 111 R2.1). Each names
-#: its command whole: `X` and `X *`, never `X*`, which also matches `X`-prefixed commands such as
-#: `git difftool` (TASK 111 R2.6).
+#: TASK 112 Appendix A. A rule joins the committed file only when `skill-safe-commands` lists its
+#: command, `framework-gates.yml` runs its script, or a test of `tests/` pins it (TASK 111 R2.1).
+#: Each names its command whole: `X` and `X *`, never `X*`, which also matches `X`-prefixed commands
+#: such as `git difftool` (TASK 111 R2.6).
 FRAMEWORK_ALLOW_RULES = (
     "Bash(ls *)",
     "Bash(cat *)",
@@ -57,8 +58,6 @@
     "Bash(git branch)",
     "Bash(git remote)",
     "Bash(git tag)",
-    "Bash(mv docs/TASK.md docs/tasks/*)",
-    "Bash(mv docs/PLAN.md docs/plans/*)",
     "Bash(mkdir -p docs/tasks)",
     "Bash(mkdir -p docs/plans)",
     "Bash(mkdir -p docs/architectures)",
@@ -66,6 +65,7 @@
     "Bash(python3 -m pytest)",
     "Bash(npm test)",
     "Bash(cargo test)",
+    "Bash(python3 .agent/tools/archive_move.py *)",
     "Bash(python3 .agent/skills/skill-session-state/scripts/update_state.py *)",
     "Bash(python3 .agent/tools/task_id_tool.py *)",
     "Bash(python3 .agent/skills/skill-creator/scripts/validate_skill.py *)",
@@ -88,7 +88,7 @@
 #: TASK 112 TC-S3: the command name of every allow rule. An interpreter or a runner under another
 #: name (`python3.14`, `py`, `node`, `bash`, `env`, `uv`) is none of these.
 COMMAND_NAMES = frozenset({"ls", "cat", "head", "tail", "grep", "wc", "stat", "du", "df", "echo",
-                           "git", "mkdir", "mv", "python", "python3", "npm", "cargo"})
+                           "git", "mkdir", "python", "python3", "npm", "cargo"})
 GIT_WRITES = ("add", "commit", "push", "reset", "restore")
 #: TASK 111 R2.7: commands with a form that writes or runs a program. Their bare forms may stay;
 #: Claude Code's built-in check approves the read forms of `git` with no rule.
@@ -107,19 +107,21 @@
 #: Placeholders of `skill-archive-task`'s shell blocks, filled with a sample archive name; any
 #: other `{...}` becomes `112`.
 PLACEHOLDERS = {"{filename}": "task-112-sample.md", "{plan_filename}": "plan-112-sample.md"}
-#: Step 5's collision guard, whole: no committed rule covers it, and the archive script absorbs it.
-NOT_COMMITTED = re.compile(r"test -e docs/tasks/task-[\w.-]+\.md")
 #: Shell syntax that Claude Code checks apart from the rule: a redirect or a substitution.
 SHELL_EXTRAS = re.compile(r"[<>`]|\$\(")
 #: A `python` rule runs a bare `-m pytest` or a named script, never `-c` or arbitrary code.
 PYTHON_RULE = re.compile(r"Bash\(python3? (-m pytest|[\w./-]+\.py( .*)?)\)")
-ARCHIVE_COMMANDS = ("mv docs/TASK.md", "mv docs/PLAN.md", "mkdir -p docs/",
+ARCHIVE_SCRIPT = PROJECT_ROOT / ".agent" / "tools" / "archive_move.py"
+ARCHIVE_COMMANDS = ("python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/",
+                    "python3 .agent/tools/archive_move.py docs/PLAN.md docs/plans/",
                     "python3 .agent/tools/task_id_tool.py", "python3 .agent/tools/rebase_links.py")
+#: A part of an archive block that moves, guards or creates outside the script (TASK 112 R1.5).
+OUTSIDE_THE_SCRIPT = re.compile(r"^(mv|test|mkdir|\[)\s")
 #: The info words that make a fence a shell block (TASK 112 R6.1).
 SHELL = ("bash", "sh", "shell", "zsh", "console")
 #: The first info word of every fence, in order; an added or relabelled fence fails (R6.1).
-ARCHIVE_FENCES = ("", "", "bash", "python", "", "bash", "bash", "", "", "bash", "", "", "bash",
-                  "bash", "", "bash", "bash", "bash", "bash")
+ARCHIVE_FENCES = ("", "", "bash", "python", "", "bash", "bash", "", "", "", "bash", "bash", "",
+                  "bash", "bash", "bash", "bash")
 SAFE_FENCES = ("", "markdown")
 FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
 
@@ -137,6 +139,13 @@
     elif isinstance(node, list):
         for value in node:
             yield from _strings(value)
+
+
+def _archive_module():
+    spec = importlib.util.spec_from_file_location("archive_move_for_tc_s7", ARCHIVE_SCRIPT)
+    module = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(module)
+    return module
 
 
 def _approves(rule, command):
@@ -292,6 +301,7 @@
     def test_s7_archive_commands_match_a_committed_rule(self):
         allow = _settings()["permissions"]["allow"]
         commands = list(_archive_commands())
+        module = _archive_module()
         for prefix in ARCHIVE_COMMANDS:
             with self.subTest(expected=prefix):
                 self.assertTrue(any(c.startswith(prefix) for c in commands),
@@ -299,10 +309,13 @@
         for command in commands:
             with self.subTest(command=command):
                 self.assertNotRegex(command, SHELL_EXTRAS, "a redirect or a substitution")
-                if NOT_COMMITTED.fullmatch(command):
-                    continue
+                self.assertNotRegex(command, OUTSIDE_THE_SCRIPT, "a move or a guard outside the script")
                 self.assertTrue(any(_approves(rule, command) for rule in allow),
                                 "no committed rule approves this archive command")
+                if command.startswith("python3 .agent/tools/archive_move.py "):
+                    operands = command.split()[2:]
+                    self.assertEqual(len(operands), 2)
+                    module._parse(*operands)  # raises Refused on an operand the script refuses
 
     def test_s7_fences_of_the_archive_skill(self):
         words = tuple(word for word, _ in _fences(ARCHIVE_SKILL.read_text(encoding="utf-8")))
@@ -326,7 +339,8 @@
               "ls -la", "python3 -m pytest", "python -m pytest", "npm test", "cargo test",
               # TASK 112 §4.1
               "ls -L .agent", "rg foo", "rg -L foo", "rg --follow foo",
-              "rg --pre-glob '*.gz' foo", "fd -L foo", "fd -e md", "mkdir -p docs/tasks")
+              "rg --pre-glob '*.gz' foo", "fd -L foo", "fd -e md", "mkdir -p docs/tasks",
+              "python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/task-112-x.md")
     REJECT = ("git diff --output=x", "git log -p --output x", "git show HEAD --output=x",
               "git branch -D x", "git tag v1", "git remote set-url origin x", "tree -o x",
               "find . -name x", "python3 -m pytest -x", "python -m pytest tests", "npm test -- x",
@@ -345,7 +359,8 @@
               "python -c 'x'", "python3 -c 'from scripts.tool_runner import x'",
               "python3 .agent/tools/task_id_tool.py.evil x")
     #: TASK 112 R3.6: one Antigravity list for the skill and both READMEs.
-    ANTIGRAVITY_LIST = "ls,cat,head,tail,grep,wc,stat,du,df,git status"
+    ANTIGRAVITY_LIST = ("ls,cat,head,tail,grep,wc,stat,du,df,git status,"
+                        "python3 .agent/tools/archive_move.py")
     PATTERN_BLOCK = (
         "# Read-only filesystem",
         r"^(ls|cat|head|tail|grep|wc|stat|du|df|echo)(?:\s|$)",
@@ -360,6 +375,9 @@
         "# Git read operations (the boundary keeps `git difftool -x <program>` out; `--output` writes a file)",
         r"^git\s+(status|log|diff|show)(?![\s\S]*\s--output)(\s|$)",
         r"^git\s+(branch|remote|tag)$",
+        "",
+        "# Archiving: the script refuses every operand but the two archive pairs",
+        r"^python3\s+\.agent/tools/archive_move\.py(\s|$)",
         "",
         "# Directory creation (three fixed directories)",
         r"^mkdir\s+-p\s+docs/(tasks|plans|architectures)$",
@@ -388,9 +406,10 @@
         '| **Symlink-aware** | `ls -L`, `rg --follow` / `rg -L`, `fd -L` | Read-only, but follow symlinks into framework dirs (`.agent/`, `.agents/`, `.cursor/skills/`, `System/`, `.agentic-development/`). Plain `find`/`ls`/`rg` do **not** descend into symlinked directories |',
         '| **File info** | `stat`, `du`, `df` | Informational only |',
         '| **Git read** | `git status`; `git log`, `git diff`, `git show` without `--output`; `git branch`, `git remote`, `git tag` with no argument | Read-only git operations |',
+        '| **Archiving** | `python3 .agent/tools/archive_move.py` | Moves `docs/TASK.md` and `docs/PLAN.md` into `docs/tasks/` and `docs/plans/`; refuses every other operand (TASK 112) |',
         '| **Directory** | `mkdir -p docs/tasks`, `mkdir -p docs/plans`, `mkdir -p docs/architectures` | Idempotent; three fixed directories |',
         '| **Tool calls** | `generate_task_archive_filename`, `list_directory`, `read_file` | Native tools |',
-        '| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py`, `python3 .agent/skills/artifact-formalizer/evals/grade_run.py`, `python3 System/scripts/doctor.py` | Framework automation |',
+        '| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py`, `python3 .agent/skills/artifact-formalizer/evals/grade_run.py`, `python3 System/scripts/doctor.py` | Framework automation; `rebase_links.py` and `init_skill.py` write only inside the working directory, compared without resolving links |',
         '| **Testing** | `python -m pytest`, `python3 -m pytest`, `npm test`, `cargo test`, with no argument | Their options can run a program, delete a directory or overwrite a file (TASK 111 D14) |',
     )
 
diff --git a/tests/test_script_guards.py b/tests/test_script_guards.py
--- a/tests/test_script_guards.py
+++ b/tests/test_script_guards.py
@@ -24,9 +24,9 @@
 from pathlib import Path
 
 PROJECT_ROOT = Path(__file__).resolve().parent.parent
-#: The scripts under test. Stage 3 of TASK 112 points them at the originals.
-REBASE = PROJECT_ROOT / ".agent" / "tools" / "rebase_links_next.py"
-INIT = PROJECT_ROOT / ".agent" / "skills" / "skill-creator" / "scripts" / "init_skill_next.py"
+#: The scripts under test, which committed allow rules name.
+REBASE = PROJECT_ROOT / ".agent" / "tools" / "rebase_links.py"
+INIT = PROJECT_ROOT / ".agent" / "skills" / "skill-creator" / "scripts" / "init_skill.py"
 LINKED = "[a](ARCHITECTURE.md)\n"
 REBASED = "[a](../ARCHITECTURE.md)\n"
 
diff --git a/.agent/skills/skill-creator/scripts/init_skill_next.py b/.agent/skills/skill-creator/scripts/init_skill_next.py
deleted file mode 100644
--- a/.agent/skills/skill-creator/scripts/init_skill_next.py
+++ /dev/null
@@ -1,237 +0,0 @@
-#!/usr/bin/env python3
-import os
-import argparse
-import sys
-
-# Add script directory to path to import skill_utils
-script_dir = os.path.dirname(os.path.abspath(__file__))
-sys.path.append(script_dir)
-import skill_utils
-from skill_utils import install_human_channel
-
-def _git_dirs(cwd):
-    """The repository's git directories, as real paths (TASK 112 R4.1).
-
-    The `.git` of the working directory, or of its nearest ancestor that has one. In a linked
-    worktree `.git` is a file naming the worktree's git directory, whose `commondir` names the
-    main one; both count.
-    """
-    here = os.path.realpath(cwd)
-    while True:
-        dot = os.path.join(here, ".git")
-        if os.path.isdir(dot):
-            return [os.path.realpath(dot)]
-        if os.path.isfile(dot):
-            break
-        parent = os.path.dirname(here)
-        if parent == here:
-            return []
-        here = parent
-    try:
-        with open(dot, encoding="utf-8") as fh:
-            line = fh.readline().strip()
-    except (OSError, UnicodeDecodeError):
-        return []
-    if not line.startswith("gitdir:"):
-        return []
-    gitdir = os.path.realpath(os.path.join(here, line[len("gitdir:"):].strip()))
-    dirs = [gitdir]
-    try:
-        with open(os.path.join(gitdir, "commondir"), encoding="utf-8") as fh:
-            dirs.append(os.path.realpath(os.path.join(gitdir, fh.read().strip())))
-    except (OSError, UnicodeDecodeError):
-        pass
-    return dirs
-
-
-def _under_git(path, cwd):
-    """True when `path` lies under the repository's git directory (TASK 112 R4.1).
-
-    A segment named `.git` in any letter case counts: a case-insensitive file system resolves
-    `.GIT` to `.git`. So does any existing ancestor of the real path (links resolved before `..`)
-    that is a git directory of `_git_dirs` by file identity, which a firmlink or a Unicode
-    normalisation of the spelling does not hide.
-    """
-    absolute = os.path.normpath(os.path.join(cwd, path))
-    segments = os.path.relpath(absolute, cwd).split(os.sep)
-    if any(segment.casefold() == ".git" for segment in segments):
-        return True
-    gits = []
-    for git in _git_dirs(cwd):
-        try:
-            gits.append(os.stat(git))
-        except OSError:
-            pass
-    probe = os.path.realpath(os.path.join(cwd, path))
-    while gits:
-        try:
-            st = os.stat(probe)
-        except OSError:
-            st = None
-        if st is not None and any(os.path.samestat(st, git) for git in gits):
-            return True
-        parent = os.path.dirname(probe)
-        if parent == probe:
-            break
-        probe = parent
-    return False
-
-def _refuse_target(skill_dir):
-    """Why `create_skill` refuses this directory, or None (TASK 112 R4.2).
-
-    `Bash(python3 .agent/skills/skill-creator/scripts/init_skill.py *)` approves any `--path` and
-    any path-shaped name. A directory outside the working directory, by its absolute path
-    normalised without resolving links, is refused, and so is one under `.git/`. Links are not
-    resolved: in a consumer project `.agent/skills` can be a link into the framework.
-    """
-    cwd = os.getcwd()
-    absolute = os.path.normpath(os.path.join(cwd, skill_dir))
-    if os.path.commonpath([absolute, cwd]) != cwd or absolute == cwd:
-        return "lies outside the working directory"
-    if _under_git(skill_dir, cwd):
-        return "lies under .git/"
-    return None
-
-
-def create_skill(name, base_path, tier_value, config):
-    """
-    Creates a new skill directory with the standard structure.
-    """
-    # If name is an absolute/relative path, split into base_path + name
-    if os.sep in name or "/" in name:
-        resolved = os.path.abspath(name)
-        base_path = os.path.dirname(resolved)
-        name = os.path.basename(resolved)
-
-    # Sanitize name
-    safe_name = name.lower().replace(" ", "-").replace("_", "-")
-    skill_dir = os.path.join(base_path, safe_name)
-
-    reason = _refuse_target(skill_dir)
-    if reason:
-        print(f"Error: Skill directory '{skill_dir}' {reason}.")
-        sys.exit(1)
-
-    if os.path.exists(skill_dir):
-        print(f"Error: Skill directory '{skill_dir}' already exists.")
-        sys.exit(1)
-
-    # 1. Create Directories
-    try:
-        os.makedirs(skill_dir)
-        os.makedirs(os.path.join(skill_dir, "scripts"))
-        os.makedirs(os.path.join(skill_dir, "examples"))
-        os.makedirs(os.path.join(skill_dir, "assets"))
-        os.makedirs(os.path.join(skill_dir, "references"))
-        print(f"Created directory structure in {skill_dir}/")
-    except OSError as e:
-        print(f"Error creating directories: {e}")
-        sys.exit(1)
-
-    # 2. Create SKILL.md from Template
-    template_path = os.path.join(script_dir, "..", "assets", "SKILL_TEMPLATE.md")
-    skill_md_content = ""
-    
-    if os.path.exists(template_path):
-        try:
-            with open(template_path, 'r', encoding='utf-8') as f:
-                template_content = f.read()
-            
-            # Replace placeholders
-            skill_md_content = template_content.replace("skill-[name]", safe_name)
-            skill_md_content = skill_md_content.replace("[Skill Name]", name.replace("-", " ").title())
-            skill_md_content = skill_md_content.replace("[TIER_VALUE]", str(tier_value))
-            
-            print(f"Loaded template from {template_path}")
-        except Exception as e:
-            print(f"Warning: Could not read template file: {e}")
-            skill_md_content = ""
-            
-    # Fallback if template missing
-    if not skill_md_content:
-        skill_md_content = f"""---
-name: {safe_name}
-description: "Use when [TRIGGER]... (One-line constraints)"
-tier: {tier_value}
-version: 1.0
----
-# {name.replace("-", " ").title()}
-## Purpose
-TODO: Describe the primary purpose of this skill.
-"""
-
-    with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
-        f.write(skill_md_content)
-    print("Created SKILL.md template.")
-
-    # 3. Create Placeholder Files
-    with open(os.path.join(skill_dir, "scripts", ".keep"), "w", encoding="utf-8") as f:
-        f.write("")
-    with open(os.path.join(skill_dir, "examples", "usage_example.md"), "w", encoding="utf-8") as f:
-        f.write(f"# Usage Example for {name}\n\nTODO: Add a concrete example of how to use this skill.")
-    with open(os.path.join(skill_dir, "assets", "template.txt"), "w", encoding="utf-8") as f:
-        f.write("TODO: Add any static templates or assets here (files used for output).")
-    with open(os.path.join(skill_dir, "references", "guidelines.md"), "w", encoding="utf-8") as f:
-        f.write("# Guidelines\nTODO: Add domain knowledge, API specs, or rules here.")
-
-    print(f"\nSkill '{safe_name}' initialized successfully!")
-    print(f"Path: {os.path.abspath(skill_dir)}")
-    
-    # 4. Reminder Check
-    catalog_file = config.get('project_config', {}).get('catalog_file')
-    if catalog_file and os.path.exists(catalog_file):
-        print(f"\n> [!IMPORTANT] NEXT STEP: Please update '{catalog_file}' to register this new skill!")
-    
-    # 5. Mandatory Cleanup Instructions
-    print("\n" + "="*60)
-    print("MANDATORY CLEANUP REQUIRED")
-    print("="*60)
-    print(f"Skill created at: {skill_dir}")
-    print("1. IMPLEMENT your skill (Add scripts, assets, examples).")
-    print("2. CLEANUP unused directories:")
-    print(f"   - Scripts: If logic < 5 lines, delete '{skill_dir}/scripts/'")
-    print(f"   - Assets: If no assets, delete '{skill_dir}/assets/'")
-    print(f"   - References: If no ext refs, delete '{skill_dir}/references/'")
-    print(f"   - Examples: Update usage_example.md or delete folder if Simple Skill.")
-    print("="*60 + "\n")
-
-def main():
-    install_human_channel()
-    # 1. Load Configuration
-    project_root = os.getcwd() # Assume run from root
-    config = skill_utils.load_config(project_root)
-    
-    # 2. Extract Options
-    tier_defs = config.get('taxonomy', {}).get('tiers', [])
-    valid_tiers = [str(t.get('value')) for t in tier_defs] if tier_defs else ["0", "1", "2"]
-    
-    default_root = config.get('project_config', {}).get('skills_root', '.agent/skills')
-
-    # Build rich help for tiers
-    tier_help = "Skill Tier choices:\n"
-    if tier_defs:
-        for t in tier_defs:
-            val = t.get('value')
-            name = t.get('name', '')
-            desc = t.get('description', '')
-            tier_help += f"    {val}: {name} - {desc}\n"
-    else:
-        tier_help += "    [0, 1, 2] (Default tiers)"
-
-    parser = argparse.ArgumentParser(
-        description="Initialize a new Agent Skill (Portable Standard).",
-        formatter_class=argparse.RawTextHelpFormatter
-    )
-    parser.add_argument("name", help="Name of the skill (e.g., 'pdf-editor')")
-    parser.add_argument("--path", default=default_root, help=f"Output directory (default: {default_root})")
-    parser.add_argument("--tier", type=str, default="2", choices=valid_tiers, help=tier_help)
-
-    args = parser.parse_args()
-
-    # Resolve path relative to CWD if it's not absolute
-    target_path = os.path.abspath(args.path)
-    
-    create_skill(args.name, target_path, args.tier, config)
-
-if __name__ == "__main__":
-    main()
diff --git a/.agent/tools/rebase_links_next.py b/.agent/tools/rebase_links_next.py
deleted file mode 100644
--- a/.agent/tools/rebase_links_next.py
+++ /dev/null
@@ -1,511 +0,0 @@
-#!/usr/bin/env python3
-"""
-Rebase document-relative links when a markdown file moves between directories.
-
-ARC-2. Archiving moves `docs/TASK.md` -> `docs/tasks/task-NNN-slug.md` and
-`docs/PLAN.md` -> `docs/plans/plan-NNN-slug.md`. Every relative link in the
-moved document was written against the OLD directory and silently denotes a
-different path (or nothing) from the new one.
-
-The rewrite is arithmetic, not a substitution:
-
-    new_target = relpath(normpath(join(from_dir, target)), to_dir)
-
-One expression covers every shape the corpus actually contains --
-`../X -> ../../X`, `X.md -> ../X.md`, `tasks/y.md -> ../tasks/y.md` -- and stays
-correct for any future layout change. A rule keyed on the literal string `../`
-misses 38 of 56 real instances, measured on this repository.
-
-Filesystem existence is the GUARD, never the trigger. The trigger is the move.
-
-Decision table, per link:
-
-    resolves    resolves
-    from old    from new
-    dir         dir (as written)   action
-    --------    ----------------   -------------------------------------------
-    yes         no                 REWRITTEN      the pure ARC-2 case
-    yes         yes (same file)    UNCHANGED      denotation already identical
-    yes         yes (other file)   REWRITTEN      + AMBIGUOUS_REBASE warning:
-                                                  silence would re-point it
-    no          yes                ACCIDENTAL_RESOLVE, left alone: it was broken
-                                                  where written; rewriting turns
-                                                  an accidentally-working link
-                                                  into a definitely-broken one
-    no          no                 PRE_BROKEN, left alone and reported
-
-Anything whose old denotation escapes `repo_root` is left alone (ESCAPES_ROOT).
-
-Idempotence falls out of the table rather than being bolted on: re-running the
-same (from_dir, to_dir) over an already-rebased file lands in the
-`no / yes` row, which never writes.
-
-Exit codes:
-  0  clean
-  1  a declared-present slot target does not exist (requires --slot-must-exist)
-  2  could not run
-  3  completed with warnings
-
-ARC-5 measured that exit 1 was unreachable before `--slot-must-exist` existed.
-The conservation probe it guarded re-derives its target by `relpath` from a path
-whose existence was already proven, so it reconstructs an existing path in every
-case. That probe is retained as a postcondition on the rewrite arithmetic, but
-it is not the gate that catches a wrong slot map -- `--slot-must-exist` is.
-"""
-
-from __future__ import annotations
-
-import os
-import re
-from typing import NamedTuple
-
-#: Schemes and forms that are never document-relative.
-_ABSOLUTE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|/|#)", re.IGNORECASE)
-
-#: Fenced blocks: ``` or ~~~, any info string, closed by a fence at least as long.
-_FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*?^[ \t]{0,3}\1[ \t]*$",
-                    re.S | re.M)
-#: An unterminated fence: everything from the opener to end of document.
-_FENCE_OPEN = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*\Z", re.S | re.M)
-#: Inline code span. Two boundary rules matter, and the naive `(`+)(?:.|\n)*?\1`
-#: gets both wrong:
-#:   1. The closing run must be the SAME length, not merely start with one. A
-#:      lone backtick closed against the first character of a ``` run, leaving
-#:      the mask desynchronized for the rest of the file.
-#:   2. A code span cannot contain a blank line -- a blank line ends the
-#:      paragraph. Without that bound an unbalanced backtick pairs with one
-#:      hundreds of lines later and blanks every real link in between.
-#: Measured on this corpus: (1)+(2) recover 3 real links in
-#: docs/design/095_workflow_loop_contract.md that were invisible to the tool,
-#: and keep masking all 13 links that are syntax examples inside code spans.
-_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(?:[^\n]|\n(?![ \t]*\n))*?(?<!`)\1(?!`)")
-
-# NOTE: indented code blocks are deliberately NOT masked. In this corpus a
-# 4-or-more-space indent is overwhelmingly a lazy continuation of a list item,
-# not a code block -- 8 of 42 real broken links sit at 6-space indent inside
-# `- [ ]` continuations in docs/plans/plan-095-*.md alone. Masking them silently
-# skipped 19% of the defect, which is the exact under-fix this tool exists to
-# prevent. Fenced blocks and inline spans carry the real code.
-
-#: Inline link / image target: `](target)` or `](<target>)`, optional title.
-#: Deliberately does NOT require a preceding `[text]`, so link text containing
-#: nested brackets still matches. Measured non-rule: tightening it to
-#: `\[[^\]\n]*\]\(` changes 2 findings in the whole corpus, both `#anchor`
-#: targets already dropped as absolute -- it buys nothing and costs recall. The
-#: bare `](x)` shapes that could be false positives all sit inside code spans
-#: and are killed by the _CODE_SPAN fix above, not by tightening this.
-_INLINE = re.compile(r"\]\(\s*(<[^>\n]*>|[^)\s]+)")
-#: Reference definition: `[id]: target`
-_REFDEF = re.compile(r"^[ ]{0,3}\[[^\]\n]+\]:[ \t]*(<[^>\n]*>|\S+)", re.M)
-#: HTML attributes.
-_HTML_ATTR = re.compile(r"""\b(?:href|src)\s*=\s*(?:"([^"\n]*)"|'([^'\n]*)')""",
-                        re.IGNORECASE)
-
-
-class LinkRecord(NamedTuple):
-    line: int
-    authored: str          # target exactly as written
-    denotes_old: str       # repo-relative path it denoted from from_dir
-    action: str            # REWRITTEN | UNCHANGED | PRE_BROKEN | ...
-    new_target: str        # target after rewrite (== authored when untouched)
-
-
-ACTIONS_WARN = ("PRE_BROKEN", "ACCIDENTAL_RESOLVE", "ESCAPES_ROOT",
-                "AMBIGUOUS_REBASE", "UNMAPPED_SLOT")
-#: Actions that actually wrote a new target.
-_WROTE = ("REWRITTEN", "SLOT_RESOLVED", "AMBIGUOUS_REBASE")
-#: Actions subject to the conservation law -- their target resolved BEFORE the
-#: move, so it must resolve after. SLOT_RESOLVED is excluded on purpose: see the
-#: conservation block in main() for why a declared identity is not probed.
-_CONSERVED = ("REWRITTEN", "AMBIGUOUS_REBASE")
-
-#: Repo-relative paths that are SLOTS, not identities: the artifact living there
-#: rotates. Knowing them intrinsically is what makes the safe behaviour the
-#: DEFAULT. When a link denotes one of these and the caller supplied no identity
-#: for it, rewriting the path would re-point the citation at whatever is live
-#: now -- turning a dead link into a confidently wrong one, invisible to every
-#: link checker because it resolves. So the link is left exactly as authored and
-#: reported as UNMAPPED_SLOT.
-KNOWN_SLOTS = ("docs/TASK.md", "docs/PLAN.md")
-
-
-def _mask(text: str) -> str:
-    """Blank non-prose regions, preserving length and newlines.
-
-    Offsets in the masked text therefore address the original text exactly, so
-    matches found here can be spliced back without a second parse.
-    """
-    def blank(m):
-        return re.sub(r"[^\n]", " ", m.group(0))
-
-    masked = _FENCE.sub(blank, text)
-    masked = _FENCE_OPEN.sub(blank, masked)
-    masked = _CODE_SPAN.sub(blank, masked)
-    return masked
-
-
-def _targets(masked: str):
-    """Yield (start, end, raw_target) for every link target in masked text."""
-    for rx in (_INLINE, _REFDEF):
-        for m in rx.finditer(masked):
-            yield m.start(1), m.end(1), m.group(1)
-    for m in _HTML_ATTR.finditer(masked):
-        gi = 1 if m.group(1) is not None else 2
-        yield m.start(gi), m.end(gi), m.group(gi)
-
-
-def _split_fragment(target: str):
-    """-> (path, suffix). Suffix keeps `#anchor` and any `?query` verbatim."""
-    for sep in ("#", "?"):
-        i = target.find(sep)
-        if i != -1:
-            return target[:i], target[i:]
-    return target, ""
-
-
-def rebase_document_links(text: str, from_dir: str, to_dir: str,
-                          repo_root: str = ".", slot_map: dict | None = None):
-    """Re-express every document-relative link from `from_dir` against `to_dir`.
-
-    Args:
-        text: the document's full content.
-        from_dir: directory the document used to live in (repo-relative).
-        to_dir: directory it lives in now (repo-relative).
-        repo_root: root that paths must not escape.
-        slot_map: repo-relative MUTABLE SLOT -> the archived identity it held
-            at the moment of this move, e.g.
-            ``{"docs/TASK.md": "docs/tasks/task-063-framework-installer.md"}``.
-            Checked BEFORE any filesystem probe, so it still works after the
-            slot file has already been moved away by a sibling step.
-
-    Returns:
-        (new_text, [LinkRecord]). `new_text is text` when nothing was rewritten.
-    """
-    root = os.path.abspath(repo_root)
-    old_base = os.path.join(root, from_dir)
-    new_base = os.path.join(root, to_dir)
-    slots = {os.path.normpath(os.path.join(root, k)):
-             os.path.normpath(os.path.join(root, v))
-             for k, v in (slot_map or {}).items()}
-    known_slots = {os.path.normpath(s) for s in KNOWN_SLOTS}
-
-    masked = _mask(text)
-    edits, records = [], []
-
-    for start, end, raw in _targets(masked):
-        authored = raw
-        bare = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
-        if not bare or _ABSOLUTE.match(bare):
-            continue
-
-        path, suffix = _split_fragment(bare)
-        if not path:                       # pure `#anchor`
-            continue
-
-        line = text.count("\n", 0, start) + 1
-        denote_old = os.path.normpath(os.path.join(old_base, path))
-        denote_new = os.path.normpath(os.path.join(new_base, path))
-
-        if os.path.commonpath([root, denote_old]) != root:
-            records.append(LinkRecord(line, authored, denote_old,
-                                      "ESCAPES_ROOT", authored))
-            continue
-
-        # A MUTABLE SLOT is checked first, and without touching the filesystem.
-        #
-        # `docs/TASK.md` is a slot, not an identity: the link was written when
-        # the slot held THIS task's spec. Preserving the path preserves the
-        # wrong thing -- it would re-point the citation at whatever task is
-        # current. Preserving the referent means naming the archive the slot
-        # held at this moment. Doing it before any existence probe is what makes
-        # it work when a sibling step has already emptied the slot.
-        if denote_old in slots:
-            identity = slots[denote_old]
-            new_path = os.path.relpath(identity, new_base)
-            if os.sep != "/":
-                new_path = new_path.replace(os.sep, "/")
-            new_target = new_path + suffix
-            if raw.startswith("<"):
-                new_target = f"<{new_target}>"
-            records.append(LinkRecord(line, authored,
-                                      os.path.relpath(identity, root),
-                                      "SLOT_RESOLVED", new_target))
-            edits.append((start, end, new_target))
-            continue
-
-        # A known slot with no identity supplied is NEVER rewritten. Rebasing
-        # the path here is what converts "dead" into "silently wrong".
-        if os.path.relpath(denote_old, root) in known_slots:
-            records.append(LinkRecord(line, authored,
-                                      os.path.relpath(denote_old, root),
-                                      "UNMAPPED_SLOT", authored))
-            continue
-
-        resolved_old = os.path.exists(denote_old)
-        resolved_new = os.path.exists(denote_new)
-        rel_old = os.path.relpath(denote_old, root)
-
-        if not resolved_old:
-            action = "ACCIDENTAL_RESOLVE" if resolved_new else "PRE_BROKEN"
-            records.append(LinkRecord(line, authored, rel_old, action, authored))
-            continue
-
-        if denote_old == denote_new:
-            records.append(LinkRecord(line, authored, rel_old, "UNCHANGED",
-                                      authored))
-            continue
-
-        new_path = os.path.relpath(denote_old, new_base)
-        if os.sep != "/":
-            new_path = new_path.replace(os.sep, "/")
-        new_target = new_path + suffix
-        if raw.startswith("<"):
-            new_target = f"<{new_target}>"
-
-        # `resolved_new` here means the untouched text ALSO resolves from the
-        # new home -- to a different file. Rewriting is still correct (the
-        # denotation is what we preserve), but the silent case is not this one.
-        action = "AMBIGUOUS_REBASE" if resolved_new else "REWRITTEN"
-        records.append(LinkRecord(line, authored, rel_old, action, new_target))
-        edits.append((start, end, new_target))
-
-    if not edits:
-        return text, records
-
-    out, cursor = [], 0
-    for start, end, replacement in sorted(edits):
-        out.append(text[cursor:start])
-        out.append(replacement)
-        cursor = end
-    out.append(text[cursor:])
-    return "".join(out), records
-
-
-def rebase_file(path: str, from_dir: str, to_dir: str, repo_root: str = ".",
-                dry_run: bool = False, slot_map: dict | None = None):
-    """Apply :func:`rebase_document_links` to a file in place.
-
-    Reads and writes with ``newline=""`` so CRLF documents round-trip.
-    """
-    with open(path, encoding="utf-8", newline="") as fh:
-        text = fh.read()
-    new_text, records = rebase_document_links(text, from_dir, to_dir, repo_root,
-                                              slot_map)
-    changed = new_text != text
-    if changed and not dry_run:
-        with open(path, "w", encoding="utf-8", newline="") as fh:
-            fh.write(new_text)
-    return changed, records
-
-
-def _git_dirs(cwd):
-    """The repository's git directories, as real paths (TASK 112 R4.1).
-
-    The `.git` of the working directory, or of its nearest ancestor that has one. In a linked
-    worktree `.git` is a file naming the worktree's git directory, whose `commondir` names the
-    main one; both count.
-    """
-    here = os.path.realpath(cwd)
-    while True:
-        dot = os.path.join(here, ".git")
-        if os.path.isdir(dot):
-            return [os.path.realpath(dot)]
-        if os.path.isfile(dot):
-            break
-        parent = os.path.dirname(here)
-        if parent == here:
-            return []
-        here = parent
-    try:
-        with open(dot, encoding="utf-8") as fh:
-            line = fh.readline().strip()
-    except (OSError, UnicodeDecodeError):
-        return []
-    if not line.startswith("gitdir:"):
-        return []
-    gitdir = os.path.realpath(os.path.join(here, line[len("gitdir:"):].strip()))
-    dirs = [gitdir]
-    try:
-        with open(os.path.join(gitdir, "commondir"), encoding="utf-8") as fh:
-            dirs.append(os.path.realpath(os.path.join(gitdir, fh.read().strip())))
-    except (OSError, UnicodeDecodeError):
-        pass
-    return dirs
-
-
-def _under_git(path, cwd):
-    """True when `path` lies under the repository's git directory (TASK 112 R4.1).
-
-    A segment named `.git` in any letter case counts: a case-insensitive file system resolves
-    `.GIT` to `.git`. So does any existing ancestor of the real path (links resolved before `..`)
-    that is a git directory of `_git_dirs` by file identity, which a firmlink or a Unicode
-    normalisation of the spelling does not hide.
-    """
-    absolute = os.path.normpath(os.path.join(cwd, path))
-    segments = os.path.relpath(absolute, cwd).split(os.sep)
-    if any(segment.casefold() == ".git" for segment in segments):
-        return True
-    gits = []
-    for git in _git_dirs(cwd):
-        try:
-            gits.append(os.stat(git))
-        except OSError:
-            pass
-    probe = os.path.realpath(os.path.join(cwd, path))
-    while gits:
-        try:
-            st = os.stat(probe)
-        except OSError:
-            st = None
-        if st is not None and any(os.path.samestat(st, git) for git in gits):
-            return True
-        parent = os.path.dirname(probe)
-        if parent == probe:
-            break
-        probe = parent
-    return False
-
-def _refuse_operand(path):
-    """Why `_main` refuses to rewrite this file operand, or None (TASK 112 R4.1).
-
-    `Bash(python3 .agent/tools/rebase_links.py *)` approves any operand, and the rewrite writes the
-    file in place. A file outside the working directory, by its absolute path normalised without
-    resolving links, is refused; so is a file under `.git/` (`_under_git`), a symbolic link, and a
-    file with a second hard link, which would write through to another name. `rebase_file()` keeps
-    no such guard: `archive_protocol.py` calls it with temporary paths.
-    """
-    cwd = os.getcwd()
-    absolute = os.path.normpath(os.path.join(cwd, path))
-    if os.path.commonpath([absolute, cwd]) != cwd or absolute == cwd:
-        return "lies outside the working directory"
-    if _under_git(path, cwd):
-        return "lies under .git/"
-    if os.path.islink(path):
-        return "is a symbolic link"
-    if os.path.exists(path) and os.lstat(path).st_nlink != 1:
-        return "has a second hard link"
-    return None
-
-
-def _main(argv=None):
-    import argparse
-    import json
-    import sys
-
-    ap = argparse.ArgumentParser(
-        description="Rebase document-relative links after a file moves "
-                    "(ARC-2). The move is the trigger; existence is the guard.")
-    ap.add_argument("files", nargs="+", help="moved markdown file(s)")
-    ap.add_argument("--from", dest="from_dir", required=True,
-                    help="directory the file used to live in (repo-relative)")
-    ap.add_argument("--to", dest="to_dir", required=True,
-                    help="directory it lives in now (repo-relative)")
-    ap.add_argument("--repo-root", default=".")
-    ap.add_argument("--slot", action="append", default=[], metavar="SLOT=ARCHIVE",
-                    help="a mutable slot and the archive identity it held, e.g. "
-                         "docs/PLAN.md=docs/plans/plan-096-x.md. Repeatable. "
-                         "Resolved before any filesystem probe, so it still "
-                         "works once the slot file has been moved away.")
-    ap.add_argument("--slot-must-exist", action="store_true",
-                    help="assert every --slot target is already on disk; a "
-                         "missing one exits 1 instead of being reported as "
-                         "pending. Pass it where the target was created BEFORE "
-                         "this call (skill-archive-task Step 7.6.5); omit it "
-                         "for a forward reference (Step 5.5).")
-    ap.add_argument("--dry-run", action="store_true")
-    ap.add_argument("--json", action="store_true")
-    args = ap.parse_args(argv)
-
-    slot_map = {}
-    for pair in args.slot:
-        if "=" not in pair:
-            print(json.dumps({"ok": False,
-                              "error": f"--slot expects SLOT=ARCHIVE, got {pair!r}"}),
-                  file=sys.stderr)
-            return 2
-        slot, archive = pair.split("=", 1)
-        slot_map[slot.strip()] = archive.strip()
-
-    for path in args.files:
-        reason = _refuse_operand(path)
-        if reason:
-            print(json.dumps({"ok": False, "error": f"{path}: {reason}"}), file=sys.stderr)
-            return 2
-
-    report, warned, failed, pending = [], False, False, []
-    for path in args.files:
-        try:
-            changed, records = rebase_file(path, args.from_dir, args.to_dir,
-                                           args.repo_root, args.dry_run,
-                                           slot_map)
-        except OSError as exc:
-            print(json.dumps({"ok": False, "error": f"{path}: {exc}"}),
-                  file=sys.stderr)
-            return 2
-
-        # Conservation law: every file denoted before the move is denoted after.
-        #
-        # SLOT_RESOLVED is exempt BY DEFAULT. A slot map is usually a FORWARD
-        # reference -- the caller declares what the slot is becoming, and in the
-        # documented archive order that file does not exist yet: Step 5.5 rebases
-        # the TASK naming `docs/plans/plan-NNN-x.md`, which Step 7 only creates
-        # afterwards. Probing it there made the protocol's own happy path exit 1
-        # ("a link regressed") and, read literally, told the agent to stop.
-        #
-        # ARC-6: that exemption over-covered Step 7.6.5, where the TASK archive
-        # is ALREADY on disk and a mistyped slug is fully detectable. Measured:
-        # `--slot docs/TASK.md=docs/tasks/task-077-logn.md` against an archive
-        # named task-077-login.md rewrote the citation and returned 0 with
-        # `"ok": true`, so the protocol's closing assertion passed on a link the
-        # tool knew was dangling. `--slot-must-exist` is how a caller states
-        # that its slot targets are present tense rather than forward-looking.
-        for r in records:
-            if r.action in _CONSERVED:
-                target = os.path.normpath(
-                    os.path.join(args.repo_root, args.to_dir,
-                                 _split_fragment(r.new_target.strip("<>"))[0]))
-                if not os.path.exists(target):
-                    failed = True
-            elif r.action == "SLOT_RESOLVED":
-                target = os.path.normpath(
-                    os.path.join(args.repo_root, args.to_dir,
-                                 _split_fragment(r.new_target.strip("<>"))[0]))
-                if not os.path.exists(target):
-                    pending.append(f"{path}:{r.line} -> {r.new_target}")
-                    if args.slot_must_exist:
-                        failed = True
-
-        entry = {"file": path, "changed": changed,
-                 "links": [r._asdict() for r in records]}
-        report.append(entry)
-        if any(r.action in ACTIONS_WARN for r in records):
-            warned = True
-
-    if args.json:
-        print(json.dumps({"ok": not failed, "files": report,
-                          "slot_targets_pending": pending},
-                         ensure_ascii=False, indent=1))
-    else:
-        for entry in report:
-            for r in entry["links"]:
-                if r["action"] == "UNCHANGED":
-                    continue
-                print(f"[{r['action']}] {entry['file']}:{r['line']}  "
-                      f"{r['authored']}"
-                      + (f"  ->  {r['new_target']}" if r["action"] in _WROTE
-                         else ""))
-        n = sum(1 for e in report for r in e["links"] if r["action"] in _WROTE)
-        w = sum(1 for e in report for r in e["links"] if r["action"] in ACTIONS_WARN)
-        for p in pending:
-            print(f"[SLOT_PENDING] {p}  (declared identity, not yet on disk)")
-        print(f"{n} rewritten / {w} needing review"
-              + (" (dry run)" if args.dry_run else ""))
-
-    if failed:
-        return 1
-    return 3 if warned else 0
-
-
-if __name__ == "__main__":
-    import sys
-    sys.exit(_main())
~~~~~

## Cluster H — stage 3

### H1 — before the edit

The patch's SHA-256 equals the stored one. Each file the patch touches, before `git apply`:

| File | SHA-256 | Mode |
| :--- | :--- | :--- |
| `.agent/skills/artifact-management/SKILL.md` | `30e439c6f73a188a42bce009ba03cd3219b5867143c62a106836a67955049cd9` | `644` |
| `.agent/skills/skill-archive-task/SKILL.md` | `86e932df1d7ac5dd53c695d5508dd0da018daeb8517f90643b9cab96e2eec59b` | `644` |
| `.agent/skills/skill-creator/SKILL.md` | `05227ca3160ca87d6894d90dd81587c698ed6cc6f92aac7a57000e37c111df65` | `644` |
| `.agent/skills/skill-creator/scripts/init_skill.py` | `62231762a4fedb6a016df2bab9f7e21e539248f51ed50bfadabccf3fbd55ab24` | `644` |
| `.agent/skills/skill-creator/scripts/init_skill_next.py` | `64792fe84d3366d95d6d103e2ae6e4df7d1b12450eb8c5fc624f80f0734c9fc1` | `644` |
| `.agent/skills/skill-phase-context/SKILL.md` | `dc896a1e7c470631d3f0e5dc1d6bd030ad1887e6330544c0e9f77649fda93056` | `644` |
| `.agent/skills/skill-safe-commands/SKILL.md` | `b599ba7b106d3b95bd1e15ff2e2d6c4500fc31968eb6dd0c2078d2c9866274bb` | `644` |
| `.agent/tools/rebase_links.py` | `9f15b133116d7f03512088f2af892e36ec4f109eaf7e024e24b78f12465edaef` | `644` |
| `.agent/tools/rebase_links_next.py` | `b0b03b3fdce06b0a29f3d91dfda3de63d002dfe1b01018497ff9f5cd96ff0366` | `644` |
| `.claude/settings.json` | `6570defa316271fc9fdf185071462f075884d87a0aea98bd1c733b33acc8ef78` | `644` |
| `AGENTS.md` | `5bf334ca3cc2b2cf1db23b2039ea39f3ea874f78fbe08ae31a44bbdc5661f1fd` | `644` |
| `GEMINI.md` | `726aaca5345f9865bb93cdd96312824be3abda82531bca13ef2e0a11fad30422` | `644` |
| `README.md` | `5ae39a4397bd29c73916a4d2734cda679e371d02d6f5f58c6db2396332cb4666` | `644` |
| `README.ru.md` | `fa37a4b9b5d1def2ef03a07153afa210d07a16978a21d03d75ad00336935035d` | `644` |
| `System/Docs/SKILL_TIERS.md` | `fffdbda779c9003459a73422862ed81e017c8535a34620c721d1a3b3bcb5f1f8` | `644` |
| `tests/run_tests.py` | `0cdc926dcab7233e84077d796a33c41edbb2f95f2d2313ef523a5d0cb889b3fc` | `644` |
| `tests/test_committed_settings.py` | `1c4f8d978da5b983e75a55fc91aa4ebda87e3aaac9b24d21b1379387e6c11d3d` | `644` |
| `tests/test_script_guards.py` | `95fef6273e5549a7a3a8d4669f9621157e0af7244d965218efa86f45fa168ba9` | `644` |

### H1 — the edit

`git apply --whitespace=nowarn docs/reviews/framework-audit-112-stage3.diff`: applied. The two
`_next` copies are gone; `.claude/settings.json` holds `Bash(python3 .agent/tools/archive_move.py *)`
and no `mv` rule. From this edit on, the rule is in force in the running session.

### H2 — gates after the edit

- Curated suite: 537 tests, OK, `test_archive_move` and `test_script_guards` among them.
- Every gate of `framework-gates.yml` as in G1; the two new modules by name: 34 passed.
- Declared paths: none undeclared. Archive-pair hashes unchanged.
- `check_positional_refs.py --targets-changed` without `--fix`: the cross-repository coordinates
  of `plan-103`, `framework-audit-105` and `framework-audit-20260813-reference-gate-scope`, and
  `review-095-independent.md:35` → `check_prompt_references.py:21`. Each was there before the
  patch: the dry run of G5 lists the same findings, and this run does not touch
  `check_prompt_references.py`. The patch causes none.

## Cluster I — stage 4 (fingerprint `901c7c5e984e`)

- **Security audit: `PASS`**, no new finding. The applied allow list equals Appendix A (44 rules).
  Against the base, the one rule that runs anything new is the archive script's; the other
  changes narrow. The final `rebase_links.py` and `init_skill.py` hash to the values H1 recorded
  for the reviewed `_next` copies. Probes against the final names held. No file a registered
  hook runs changed.
- **Code review: `APPROVE`.** `git apply --check -R` of the patch passes, so every hunk is in the
  tree as approved. 537 curated tests OK; TC-A23 kills the mutant that removes the archive when
  the source cannot be checked.

Residuals, recorded in TASK §7: a link from inside a nested checkout to the outer `.git`
(WI-34 class); the two races with a concurrent writer of `docs/`.

## Cluster J — restart

Two TIER 0 skills (`skill-safe-commands`, `artifact-management`) and the committed settings
changed: the operator restarts the session after the commit (`framework-upgrade` §4.3).

## Retro (§6)

Claim `framework-upgrade-wi-35-safe-command-patterns`, taken at §0. The operator answered the
retro question on 2026-10-06:

- the stage-3 patch method is YAGNI, since the framework changes often: dismissed as noise;
- the reviewer's repository copy, the TASK §1 coordinates and the review rounds: noise;
- WI-37 is not needed: `dropped` (TASK D6);
- WI-36 stays `open`.

Four findings collected and dismissed as noise with those reasons. Nothing filed.
