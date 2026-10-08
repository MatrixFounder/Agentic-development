# Framework Audit 115 — Links into the TASK and PLAN slots are re-targeted on archive

- **Task:** 115 `inbound-slot-links-retargeted-on-archive`. It archives to
  `docs/tasks/task-115-inbound-slot-links-retargeted-on-archive.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1,
  Modes A and B.
- **Date:** 2026-10-07. **Base revision:** `fc534769f2f946488c89a7fa48179b76f9c8750a`, clean tree
  at start.
- **Source:** WI-38, with the operator's request of 2026-10-07 (TASK D1).
- **Independence:** each audit round runs in a separate read-only agent. Same-model agreement is
  corroboration, not independent confirmation.

## 0. Emergency Bypass

`[BYPASS_TIER_PROTECTION]`: `artifact-management` is a TIER 0 skill (TASK R12.5). Its two step
enumerations of `skill-archive-task` ("Steps 1-6 … Step 7") gain Step 8. No rule of the skill
changes; without the edit its summary of the protocol omits a step.

`skill-safe-commands`, the other TIER 0 skill near this change, is not edited (TASK R12.11).

## Archive (§1)

TASK 114 archived under ID 114 with `task_id_tool.py "subtask-classified-by-h1" --proposed-id
"114" --no-correction` (`generated`). TASK 114 had no PLAN. The two commands, as run:

```sh
python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/task-114-subtask-classified-by-h1.md
python3 .agent/tools/rebase_links.py docs/tasks/task-114-subtask-classified-by-h1.md --from docs --to docs/tasks
```

`archive_move.py`: `"ok": true`, method `link`. `rebase_links.py`: 0 rewritten, 0 needing review,
exit 0. Step 8 did not exist at the base, so no file was re-targeted.

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

A read-only `task-reviewer` agent; 2 BLOCKER, 5 MAJOR, 12 MINOR, 3 NIT; no §4 condition. The brief
carried no tree fingerprint, so the round was not pinned to a tree state.

| # | Severity | Finding | Applied in revision 2 |
| :--- | :--- | :--- | :--- |
| B1 | BLOCKER | a prompting Step 8 reverses TASK 111 D13; TC-S7 pins every archive command and the fence order | D6 (operator); §7 staging; §10.2, §10.3 |
| B2 | BLOCKER | no Use Cases, no Acceptance | §4, §5 with registered anchors |
| M1 | MAJOR | no RTM; seven unregistered anchors | §2 RTM; anchors dropped |
| M2 | MAJOR | symlinks excluded yet expected as `REFUSED`; scan set used for two things | D5, R2.4, R2.5, TC-11 |
| M3 | MAJOR | which base revision Step 8 uses | D7 (operator); R8.2; R10 |
| M4 | MAJOR | "ARCHITECTURE.md is never touched" turns false | R8.6, R8.7 |
| M5 | MAJOR | §5 rollback stops on files Step 8 rewrote | R11 |
| m1–m15 | MINOR, NIT | operand shapes, git hardening, line mapping, link text, risks, outputs, tests, docs, counts | R1, R3, R4, R6, R7, §8, §12, R12, §1 |

**Operator decisions (2026-10-07), quoted:**

- D6, on B1: "Авто через rebase_links (Recommended)".
- D7, on M3: "Строка в шаблон TASK (Recommended)".

### Round 2 — TASK revision 2: PASS

The same agent, resumed. Tree fingerprint `b06cabdc12fd` in the brief, quoted in the report, and
recomputed at its return: equal. No blocker, no MAJOR, no §4 condition; 8 MINOR, 6 NIT. It
confirmed the three checks of the brief:

- §7 puts every change to code an allow rule names, or a listed script runs, into the patch;
- the §10.3 tuple matches the fence order;
- TC-S7 accepts both §10.2 commands under `Bash(python3 .agent/tools/rebase_links.py *)`.

| # | Severity | Finding | Applied in revision 3 |
| :--- | :--- | :--- | :--- |
| n1 | MINOR | nothing ties the reviewed `slot_links.py` to the text stage 3 makes reachable | §7.3 hashes |
| n2 | MINOR | a Base revision row after the ID row reads as the slug | R9.1, R10.1, R10.2, TC-25 |
| n3 | MINOR | prefix and guard compare paths that differ by a resolved link | R3.3, R5.2, TC-23 |
| n4 | MINOR | a module planted beside `rebase_links.py` runs under the allow rule | R1.1, R1.2, D8, TC-G11 |
| n5 | MINOR | TC-21 has no positive control | TC-21 |
| n6 | MINOR | `analyze_gaps.py`, the `skill-task-model` bullet, the bypass flag | R12.9, R10.4, R12.5 |
| n7 | MINOR | `WORKFLOWS.md` rollback summary | R12.10 |
| n8 | MINOR | uncommitted changes and smudge filters; a rebased base | §12, R6.3, TC-10 |
| n9–n14 | NIT | stage-1 prose, flags per line, RTM numbering, small branches, walk mode, the safe-commands row | §7.1, §10.2, §2, R1.7, R2.2, R5, R7.3, R9.3, R12.11 |

Mode A closes at round 2 with PASS; revision 3 applies its findings.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: FAIL

A read-only `plan-reviewer` agent. Tree fingerprint `b9a0b5b869c6` in the brief, quoted in the
report, and recomputed at its return: equal. No blocker, 1 MAJOR, 12 MINOR, 13 NIT; Mode B items
2–4 pass, item 1 fails on M1.

| # | Severity | Finding | Applied in PLAN revision 2 or TASK revision 4 |
| :--- | :--- | :--- | :--- |
| M1 | MAJOR | the CLI cases of A4 need `rebase_links_next.py`, which B1 creates after A | B1 after A1; A2 runs with the dispatch; TASK §8 (M1 note below) |
| m1 | MINOR | F3's expected failures, include list and hash check | F3; TASK TC-G9, TC-G11 |
| m2 | MINOR | curated test text in the tree during F3 | F3 runs as one command |
| m3 | MINOR | TC-G8 to TC-G11 never green before G | F1 smoke run against `rebase_links_next.py` |
| m4 | MINOR | PLAN 112 H2's resolver rules; the §13.5 check | G2; TASK §13.5 |
| m5 | MINOR | the state while G stands reversed | G Failure, last paragraph |
| m6 | MINOR | skill checks after G; fix-round re-runs | G2; F4 |
| m7 | MINOR | "step 8" and "step 10" in the Example Flow | D1; TASK R8.8 |
| m8 | MINOR | scratch drafts become copies | Rollback point |
| m9 | MINOR | environment leaks across CI pytest modules | Tests paragraph |
| m10 | MINOR | A3 too large | A3 and A4 by requirement group; schedule re-estimated |
| m11 | MINOR | no stub for B and C; no stub-pass case | A1, C0; TASK TC-0 |
| m12 | MINOR | no `docs/tasks/task-115-*.md` | Sequencing rule, on the PLAN 111 and 112 precedent |
| n1–n12 | NIT | mutations, wording, postconditions, re-runs, cache option, order, coverage, docstrings | the PLAN sections they name (n12 note below) |
| n13 | NIT | line continuations are not safe for a vendor that applies the patterns | TASK D9: one-line commands in §10.2 |

**M1 note.** In TASK §8 every exit-2 case also asserts the stderr object of R7.4, and TC-22
compares the records of two completed runs.

**n1–n12 note.** Applied in the Mutations paragraph, B1, G1, F6, Commands, Tests, Retro and I1,
Coverage, the Sequencing rule, C2 and D5. n12, an optional pin of R11 in
`test_git_rollback_contract.py`, is not taken.

TASK revision 4 holds the TASK-level parts: R1.2, R8.4, R8.8, §8 (TC-0, TC-9, TC-10, TC-22,
TC-G9, TC-G11), D9 and §13.5. It changes no requirement that Mode A passed.

### Round 2 — PLAN revision 2: PASS

The same agent, resumed. Tree fingerprint `5fba665e47cd` in the brief, quoted in the report, and
recomputed at its return: equal. No blocker, no MAJOR; Mode B items 1–4 pass. M1 and m1–m12 are
closed; n12 stays not taken. PLAN revision 3 and TASK revision 5 apply the round's comments.

| # | Severity | Finding | Applied |
| :--- | :--- | :--- | :--- |
| R2-1 | MINOR | the scratchpad holds copies and drafts the PLAN does not list | cleared before §3.1 (below); inventory in the Rollback point |
| R2-2 | MINOR | a failing run can skip the restore | Mutations paragraph and F3: `finally`, text held in memory |
| R2-3 | MINOR | absence-only cases pass on the stub | A2: every case asserts an exit code or a completed result |
| R2-4 | MINOR | A3's cases need parts A4 listed | A3 and A4 regrouped |
| R2-5 | NIT | step and schedule numbering | A5, A6; ids `115.A-stub`, `115.A-logic` |
| R2-6 | NIT | "step 7" in the Example Flow | D1 |
| R2-7 | NIT | `tests` as a namespace package | F3: `PYTHONPATH=tests` |
| R2-8 | NIT | the precedent's citation | Sequencing rule |
| R2-9 | NIT | how A6 loads the copy | A6: inline `python3 -c` |
| R2-10 | NIT | G2 against the Failure paragraph | G2: its resolver rule takes precedence |
| R2-11 | NIT | two statements of the Sequencing rule | Sequencing rule |
| R2-12 | NIT | the smoke script can drift from the patch | F3 runs the patch's own TC-G8 to TC-G11 against the copy |
| R2-13 | NIT | the `__future__` directive | TASK R1.2, PLAN B1 |
| R2-14 | NIT | bytecode in `__pycache__/` | Rollback point |
| R2-15 | NIT | TC-0 fails at the base only by construction | A2; noted here |

**Scratchpad, before §3.1 (R2-1).** Deleted on 2026-10-08:

- copies of repository files made by the TASK 114 review: `base/`, `mut/`, `n8n/`, `am/`, `am2/`,
  `tmp7_v09s2r/`, `longdig/`, `sk/`, and the files `classify.py`, `cmp_grep.py`, `mutate.py`,
  `probe.py`, `h1_this.txt` and `refs.txt`;
- this run's mutation copies `mut2/` and `coretest/`, and its measurement scripts `inbound.py`,
  `inbound2.py`, `inbound3.py`, `cmp_classify.py` and `smoke_draft.py`;
- `wi-slot-links.md`, whose text is the body of WI-38;
- `draft/PLAN.md`, whose text is `docs/PLAN.md`.

What remains is listed with its deletion step in the PLAN's Rollback point.

## Execution (§3)

§3.1 on 2026-10-08: `HEAD` equals the base; the 23 edited paths pass `git ls-files
--error-unmatch`; the 4 created paths are absent and `git check-ignore -q` exits 1 for each; every
path has the shape of §3.1.

### Cluster A and B

- **A1, B1.** The stub of `slot_links.py`, then `rebase_links_next.py`: the `--inbound` branch
  reaches the stub's `main`, which raises `NotImplementedError`.
- **A2 base-fail** with the stub and the dispatch present: 1 passed (TC-0), 40 failed. The
  in-process cases raise `NotImplementedError`; the CLI cases (TC-9, TC-10, TC-20) exit 1, not 2
  or 3; TC-18 fails on the stub's missing `_write_file`. TC-0 fails at `fc53476` only because the
  module is absent there (Mode B round 2, R2-15).
- **A3**, the logic of R2, R3 and R4: its 20 cases pass, and the 15 cases of A4 fail.
- **A4**, the rest: 41 passed.
- **A5 mutations**, by the driver of the Mutations paragraph; each restore matched the SHA-256
  `4180acc267a4`:

  | Mutation | Result |
  | :--- | :--- |
  | TC-1: sub-tasks are not own | killed, 17 failed |
  | TC-2: whole files count as own | killed, 3 failed |
  | TC-5: archives are listed | killed, 1 failed |
  | TC-18: the postcondition is dropped | killed, 1 failed |
  | TC-21: the module runs `git status` | killed, 1 failed, after one fixture change |
  | TC-21: the module runs `git diff` | killed, 1 failed |
  | ledger records are rewritten | killed, 1 failed |
  | the git environment is not dropped | killed, 1 failed |
  | the hard-link guard is dropped | killed, 1 failed |

  **The fixture change.** The first `git status` mutant survived: the module's
  `core.fsmonitor=false` stops the hook, and a file changed in size needs no clean filter.
  TC-21 now also changes a tracked file at the same size, which `git status` must read through the
  clean filter.
- **A6.** `test_rebase_links.py` with `rebase_links_next.py` loaded as `rebase_links`: 44 passed.

**Scratchpad.** Deleted after A2: `draft/test_slot_links.py`; after B1: the dispatch shim; after
A3: `draft/slot_links_core.py`; after A4: `draft/slot_links.py`. Added: the mutation driver of A5,
which holds no copy of a repository file; it is deleted with the generator after G1.

### Cluster C

- **C0.** The stub: `retarget_inbound_slot_links()` raises `NotImplementedError`, and
  `parse_task_meta()` returns `base_revision: None`. The 40 existing cases pass.
- **C1 base-fail.** 7 of the 10 new cases fail on the stub. The other 3 pass there by design: they
  assert `None` for `none`, a placeholder and two hash values, which pins that the reader invents
  no base. C1 said "the new cases fail"; this note records the 3 that cannot.
- **C2, C3.** `test_archive_protocol.py`: 50 passed. The tool suite: 213 passed.
  `tests/test_language_independence.py`, which loads `archive_protocol.py` by path: 19 passed.

### Cluster D

- **D0**, `analyze_gaps.py` before any edit (run on 2026-10-07, after §0):

  | Skill | Gaps | Advisories |
  | :--- | ---: | ---: |
  | `skill-archive-task` | 1 | 6 |
  | `requirements-analysis` | 1 | 7 |
  | `skill-task-model` | 0 | 4 |
  | `artifact-management` | 1 | 6 |

  Each gap is "[Richness] Missing or empty 'examples/' directory".

**Stash incident (D1).** One verification command ended with `git stash -q`, which
`framework-upgrade` §5 rule 6 forbids. It stashed the four modified tracked files of the moment:
`skill-archive-task`, `archive_protocol.py`, `test_archive_protocol.py` and `docs/TASK.md`;
untracked files stayed. The next command ran `git stash pop`: no conflict, the stash list empty,
the same four `M` entries back. Then the anchors of D1, TASK revision 5 and the new function were
present, and the tool suite passed, 213 cases. No other command ran in between.

**Temporary copy (D1).** To compare the register findings of `skill-archive-task` with the base,
a check wrote the base text of the skill to a temporary file and removed it in the same command.
That was a copy outside version control, against §3.1; later comparisons read the base text into
memory only.
- **D1–D7.** `skill-archive-task` 2.3, `requirements-analysis` 1.4 (the template's Base revision
  bullet), `docs/_TASK_template.md`, `02_analyst_prompt.md`, `skill-task-model` 1.2,
  `framework-upgrade.md` §1.2 and §5.1, `00_agent_development.md`, and `artifact-management` 1.6
  under the bypass of §0. The skill carries the two `stage3:` anchors and no new fence; TC-S7
  passes. `test_git_rollback_contract.py` and `test_run_safety_rules.py` pass.
- **D8.** `validate_skill.py` exits 0 for the four skills; `analyze_gaps.py` reports the gaps and
  advisories of D0, no more; `skill-safe-commands` is unchanged. The register scan finds no
  `WARN` on a line added since the base in the eight edited markdown files.

### Cluster E

- **E1–E5.** `docs/ARCHITECTURE.md`, `System/Docs/ORCHESTRATOR.md` (Steps 1–8, the new function
  and modules; it also said "6-step" and "15 automated tests"), `System/Docs/SKILLS.md`,
  `System/Docs/WORKFLOWS.md`, and the CI pytest list, which now passes whole: 484 passed.
- **E6.** v3.38.0 in `CHANGELOG.md` and `CHANGELOG.ru.md`.
- **E7.** WI-38: `status: done`, `resolved_at: 2026-10-08`, `resolved_by: 'TASK 115'`, the
  resolution blockquote; its index line moved to `## Closed`.
- **Register.** No `WARN` on an added line, except two on the `skill-archive-task` row of
  `SKILLS.md`: the row repeats the skill's description (R12.3), and the base row carried the same
  two findings.

### Cluster F — gates, the stage-3 patch, stage 2

- **F1, every gate of `framework-gates.yml`, run locally:**

  | Gate | Result |
  | :--- | :--- |
  | tooling pytest list | 484 passed |
  | tool tests (`.agent/tools`) | 213 passed |
  | curated unittest suite | 538, OK, after one fix below |
  | artifact-formalizer selftest and eval selftest | 192/192, 78/78 |
  | mermaid unit tests, figure lint probe and references, eval selftest | 650 passed; 98/98; 0 error; 225/225 |
  | register scanner probe | 18/18 detectors live |
  | validate skills catalog, prompt references | 47/47; 41 references resolve |
  | positional refs, living corpus | 0 errors |
  | security lint, workflow smoke, loop contracts | pass; pass; 25 loops, 0 errors |
  | R3 negative fixture | fails, as required |

  **The fix.** The first curated run failed `test_mermaid_wiring` TestPlanStatus: D5 named
  `update_state.py` with `--add_decision` only, and the test requires every such command to pass
  the four required flags. §1.2 now refers to §0 instead.

  The advisory archive scan of positional references exits 1, with 8 errors in archived tasks and
  reviews; none is in a file of this run. The declared-paths check: every `git status` entry is a
  declared path or a file of the run itself.
- **F2.** The generator wrote `docs/reviews/framework-audit-115-stage3.diff` with 6 file sections;
  `git apply --check` passes.
- **F3**, the driver of the PLAN, as one run:
  - with the patch's two test parts applied, exactly the 6 expected cases fail: the `--inbound`
    prefix and the fence pin of TC-S7, and TC-G8 to TC-G11;
  - the patch's `TestInboundGuard` against `rebase_links_next.py`: 4 passed;
  - the reverse apply restored both files to their SHA-256.

  The first F3 run found a defect in the patch's TC-G8 to TC-G10: `inbound(self, script=REBASE)`
  bound the script when the class was defined, so the in-process override reached only TC-G11.
  The patch now resolves `REBASE` at the call; F3 then passed. A separate bounded run removed the
  `sys.path` move from `rebase_links_next.py`: TC-G11 failed, and the file was restored to its
  SHA-256.

### F4 — stage 2, round 1

Both agents read the tree at fingerprint `c7d82e70da04` and quoted it; the caller recomputed it at
each return: equal. The patch, `slot_links.py` and `rebase_links_next.py` hashed to
`70bcc8c1875a`, `4180acc267a4` and `7eeeb40e375e`.

- **Code review: CHANGES REQUESTED.** B1: a `__future__.py` planted beside `rebase_links.py` runs
  before the `sys.path` move (R1.2). B2: `--dry-run` skips the write guard (R5.4). M1: four of the
  five R5.2 conditions have no test. 21 MINOR and NIT findings.
- **Security audit: INCOMPLETE**, no CRITICAL or HIGH. M1 (MEDIUM) is the code review's B1.
  - L1–L5 (LOW): a planted `.pyc`, overlapping edits, cost bounds, escaped output, an
    unencodable name.
  - L6–L10 (LOW): a lost update, the dry run, a lazy fetch on old git, the Step 2 value shape, the
    file mode writing through a linked parent.
  - I1–I7 (INFO).
  - The scan types `deps` and `external` did not run: both copy lockfiles, which the brief forbade.
- **Re-run of the unfinished part (§6.2 step 1),** with the scanner's own temporary lockfile
  copies allowed:
  - `deps` COMPLETE, no CRITICAL or HIGH;
  - `external`: semgrep, gitleaks, trufflehog, bandit and pip-audit are not installed;
  - `npm audit` reported GHSA-238p-pmpm-9mq7 (LOW, katex 0.16.47) in the three mermaid renderer
    lockfiles, which this change does not touch.

  Verdict: still INCOMPLETE.

**Operator decisions (2026-10-08), quoted:**

- D10, on the fix scope: "Всё дешёвое сейчас (Recommended)". The cheap LOW, INFO and MINOR findings
  are fixed in round 1. Work-items: L10, the `sys.path` move of the other allow-listed scripts, and
  the directory-swap race of R5.2.
- D11, on the INCOMPLETE audit after the re-run: "Продолжить, записав пробел (Recommended)". The
  gap is the external layer above; TASK 115 adds no dependency.

### F4.1 — fix round 1

TASK revision 6 and PLAN revision 4 state the round. The tests came first:

- **Red before the fix (14):** TC-27 to TC-38 and the bracketed case of TC-39, all in
  `test_slot_links.py`; four `base_revision` cases in `test_archive_protocol.py`.
- **Green on the old code (9), as pins of behaviour that had no test:** TC-26 (four guards), TC-39
  (the escaped opener and `_text_span`), TC-40, TC-41 and the TC-21 additions. The mutations
  below show that each one fails a mutant.

The fixes:

- `rebase_links_next.py` (B1, M1, L1): no `from __future__` statement; under `__main__` the
  directory move, `sys.dont_write_bytecode` and `sys.pycache_prefix` under `/dev/null`.
- `slot_links.py` (B2, L2–L8, I2, I4, I6 and the review's minors 9–12, 17, 20, 21):
  - the guard runs in a dry run;
  - overlapping edits, a partial write and a file replaced after the write are refused;
  - the output is escaped, and the JSON is ASCII;
  - `GIT_ALLOW_PROTOCOL=none`, and a foreign `core.worktree` is refused;
  - a 4 MiB read cap and a 20000-line attribution bound;
  - a case-insensitive ledger check, and sub-tasks listed from `docs/tasks/` in git mode;
  - unreadable directories listed, no option abbreviations, an unexpected error exits 1.
- `archive_protocol.py` (minors 7, 8; I5): the base is read from the meta region only, and the
  structural read needs a letter and a digit.
- `skill-archive-task` (minors 5, 6, 13; L4, L9):
  - Step 8 runs after Step 7, and 7.1 leads to it;
  - the meaning of exit 3, and the records are data;
  - Step 2's value shape, and the Step 5.5 citation by code.
- `skill-planning-format` 1.5, `ORCHESTRATOR.md` and the changelogs (minors 14, 15).
- The patch: TC-G11 plants seven standard modules, `__future__` among them; TC-G12 plants an
  unchecked-hash `.pyc`.

The re-runs:

- **Tests.** `test_slot_links.py`: 66 passed. `test_archive_protocol.py`: 54. A6,
  `test_rebase_links.py` on the copy: 44.
- **Mutations (A5).** 32 mutants of `slot_links.py`: 31 killed.
  - The survivor dropped only the `fstat` size check; the bounded read still enforces the cap.
  - A compound mutant that drops both layers is killed.
  - The bounded read alone guards a file that grows during the read (I4); no case reaches it.
- **Gates (F1).** Every gate passes: the CI pytest list 513, the tool suite 242, the curated suite
  OK; the advisory archive scan as before.
- **D8.** `validate_skill.py` exits 0 for `skill-archive-task` and `skill-planning-format`.
  - `analyze_gaps.py`: 1 gap and 6 advisories for the first, as in D0.
  - 0 gaps and 4 advisories for the second; D0 did not cover it, since it joined in this round.
- **F3**, on the regenerated patch: exactly 7 cases fail, TC-G8 to TC-G12 among them, and no
  other. `TestInboundGuard` against `rebase_links_next.py`: 5 passed.
- **Sensitivity.** TC-G11 fails when `from __future__ import annotations` is put back. TC-G12 fails
  without the `sys.pycache_prefix` step. Both files were restored to their SHA-256.

Hashes after the round: the patch `d8b7aa94eaa5`, `slot_links.py` `95a23cf2145d`,
`rebase_links_next.py` `251d19668b19`.

### F4 — stage 2, round 2 (the re-check of fix round 1)

Both agents read the tree at fingerprint `5fb0a8d9966b` and quoted it; the caller recomputed it:
equal.

- **Code review: CHANGES REQUESTED.** The round-1 findings are closed, except the `autojunk` half
  of minor 2 and part of minor 19. N1 (blocking): a package directory `slot_links/__init__.py`, or
  an extension module, planted beside the script replaces a sibling module, because a path search
  prefers both to `slot_links.py`. 17 MINOR and NIT findings.
- **Security re-check: PASS** for the adversarial review of the changed parts, with M1 partly open.
  - `subprocess` imports `msvcrt` on POSIX, where the standard library has none.
  - The lookup then reaches the script's directory at the end of `sys.path`, and a planted
    `msvcrt.py` runs; its payload can hide itself.
  - L3 residual: `_mask` costs about O(n^1.5), bounded only by the 4 MiB cap.
- **Fix round 2** takes both: the script's directory leaves `sys.path` entirely, as in
  `archive_move.py`, and the `--inbound` branch loads its four siblings by explicit path. The
  operator's D10 covers it: it completes the M1 fix that round 1 began.

### F4.2 — fix round 2

TASK revision 7 and PLAN revision 5 state the round. The tests came first:

- **Red before the fix (6):** TC-43 to TC-46; two `base_revision` cases of TC-25. The patch's
  extended TC-G11 failed against the round-1 `rebase_links_next.py`.
- **Green on the old code, as pins:** TC-42 (`autojunk`) and the untracked case of TC-34.

The fixes:

- `rebase_links_next.py` (N1, M1 residual): the script's directory leaves `sys.path`; the
  `--inbound` branch loads `archive_move`, `task_id_tool` and `slot_links` by explicit path and
  registers the script as `rebase_links`; `sys.pycache_prefix` under `os.devnull`.
- `slot_links.py` (review items 2, 7, 11, 13, 15, 16; L3):
  - the `docs/tasks/` listing reads regular files and links only, deduplicates in NFC, and records
    an unreadable directory;
  - a file without `TASK.md` or `PLAN.md` is not masked, and the read-back is bounded;
  - a closed stdout exits 1 with the stderr object; docstrings.
- `archive_protocol.py` (item 5): the meta region prefers `0. Meta` and skips an H1.
- The skill, TASK and documents (items 3, 4, 6, 8, 9):
  - Step 2 strips one pair of backticks, and Step 8 STOPs on any other exit code;
  - the example's Base revision is readable;
  - the stale counts, and the changelogs' list of skills.
- Not taken: item 14, a Python 3.9 shim (TASK D14); item 12 is a §12 risk.

The re-runs:

- **Tests.** `test_slot_links.py` 71, `test_archive_protocol.py` 56, `test_rebase_links.py` on the
  copy 44.
- **Mutations (A5).** 38 mutants of `slot_links.py`, 38 killed; the read-cap mutant now drops both
  layers.
- **Sensitivity of the patch's guard tests,** each run on `rebase_links_next.py` and restored to
  its SHA-256:
  - TC-G11 fails when the future import is kept, when the directory is moved instead of removed,
    and when the siblings are found by a path search;
  - TC-G12 fails without the `pycache_prefix` step.
- **F3:** exactly 7 cases fail with the patch's test parts; `TestInboundGuard` against the copy:
  5 passed.
- **Gates (F1):** all pass; the CI pytest list 520, the tool suite 249, the curated suite OK.
- **D8:** both skills validate; gaps and advisories unchanged.

Hashes after the round (first 12 hex digits; F6 records them in full): the patch
`2218ae0c5d68`, `slot_links.py` `e729c176870f`, `rebase_links_next.py` `094304333b45`.

### F4 — stage 2, round 3 (the re-check of fix round 2)

Both agents read the tree at fingerprint `b32ac2f807b1` and quoted it; the caller recomputed it:
equal. Both checked the three hashes above against the brief: equal.

- **Security re-check: PASS.** No CRITICAL, HIGH or MEDIUM finding remains in the changed parts.
  - The M1 residual (`msvcrt`) and the code review's N1 (a planted package or extension module)
    are closed. Both were checked against the real script.
  - A module planted beside a symbolic link to the script does not run on 3.14, where
    `sys.path[0]` is the real directory. INFO: 3.11 to 3.13 were not tested, and the allow rule
    names the real path.
  - Carried residuals: L3, the `_mask` cost (fail-safe, TASK §12); `PYTHONPATH` (INFO, shared by
    every Python tool); the generic `except Exception` exits 1 (INFO); a labelled Base revision
    row accepts a hex-shaped word (INFO, git rejects it).
  - The external layer stays a gap, as D11 decided.
- **Code review: APPROVED.** N1 and the round-2 items 1–13 and 15–17 are closed. Item 14 was not
  taken under D14, and the reviewer accepts that.
  - MINOR 1: the F4.2 hash line was malformed by a zsh word split. It now holds one value per
    file, and F6 records the full SHA-256.
  - NIT 6 to 8, documents only, applied in this round:
    - the PLAN B1 note;
    - the TASK R2.1 wrap;
    - the changelog wraps, and the `skill-planning-format` 1.5 bullet in both languages;
    - `PYTHONPATH` as a TASK §12 risk.
  - NIT 2–4 and 9–11 touch code or tests. They go to a work-item at the retro, so that stage 3
    applies the hashes the reviewers checked:
    - no test pins the NFC deduplication (2), a link in the `docs/tasks/` listing (3) or the
      read-back bound (4);
    - a case mismatch on macOS can scan one file twice (9);
    - a `None` `sys.stdout` and the unguarded stderr emit on exit 2 skip the stderr object (10);
    - the mirror strips every backtick, where Step 2 strips one pair (11).
  - NIT 5: the `(ENOENT, ENOTDIR)` exemption cannot be reached. It is defensive code, not a
    defect.

The document edits of this round touch no file of the patch, and the three hashes are unchanged.

### F5 — reference resolver (§4.5)

`check_positional_refs.py --targets-changed` without `--fix` selected 67 documents and 345
references. It found no `REFERENT_MOVED`.

- **12 errors, each one older than this run:**
  - 11 `UNRESOLVABLE` coordinates into other repositories (`get-token.ts`, `wallet-balances.ts`,
    `registry.ts`), in old changelog entries, `plan-103` and `framework-audit-105`;
  - a `REFERENT_ABSENT` in `review-095-independent.md`, at line 35, which cites line 21 of
    `check_prompt_references.py`. This run does not touch that script.
- **93 `DRIFT_SUSPECT` warnings:** bare coordinates in records and archives that point into files
  this run edits. A coordinate with no referent is not examined, and it is not a defect
  (`documentation-standards` §4.1).
- **2 `ESCAPES_ROOT` warnings:** a coordinate into `../CLAUDE.md`, in old changelog entries.

Then `--fix` repaired nothing. The tree fingerprint was `f16fe2505da5` before the run and after
it, and the findings were the same. No file was touched by a repair.

### F6 — the stage-3 patch as reviewed

F5 repaired no file. No test part of the patch changed after the F3 run of F4.2. `git apply
--check` of the patch passes.

- **Gates,** run again after the document edits of round 3 and of this record: all pass, with the
  same counts as F4.2. The advisory archive scan lists the 8 errors it listed before.
- **The TASK §13.5 dry run through `rebase_links_next.py`, as a pre-check:** 8 `INBOUND`, 3 slot
  links in the archive, exit 3. The tree fingerprint `870c81dd30b9` is the same before the run
  and after it. The patch text in this record adds no record.

| File | SHA-256 |
| :--- | :--- |
| `docs/reviews/framework-audit-115-stage3.diff` | `2218ae0c5d68cc442ea668a71c6ed53bc1cb6052a46ef755abd16f1d4c9eedba` |
| `.agent/tools/slot_links.py` | `e729c176870fe15e60d66a71ee438fb57ae09cda95cb98e9d0700ba41b0ea339` |
| `.agent/tools/rebase_links_next.py` | `094304333b45dd06a9ba0f686332b14b8e6fd2ec8fa6ff366fb6bc3392799787` |

The patch, 859 lines in 6 file sections:

~~~~diff
diff --git a/.agent/tools/rebase_links.py b/.agent/tools/rebase_links.py
--- a/.agent/tools/rebase_links.py
+++ b/.agent/tools/rebase_links.py
@@ -51,13 +51,39 @@
 whose existence was already proven, so it reconstructs an existing path in every
 case. That probe is retained as a postcondition on the rewrite arithmetic, but
 it is not the gate that catches a wrong slot map -- `--slot-must-exist` is.
+
+Inbound mode (TASK 115, `skill-archive-task` Step 8). With `--inbound` as the
+first argument, the remaining arguments go to `main(argv)` of `slot_links.py`:
+
+    rebase_links.py --inbound --task docs/tasks/task-<ID>-<slug>.md
+        [--plan docs/plans/plan-<ID>-<slug>.md] [--since <rev>] [--dry-run] [--json]
+
+It re-targets the slot links that an archived task wrote in other documents, and
+lists the others. The allow rule that names this script covers the mode, so
+archiving stays automatic (TASK 111 D13). Its exit codes are those of
+`slot_links.py`.
 """
 
-from __future__ import annotations
-
 import os
-import re
-from typing import NamedTuple
+import sys
+
+# Run as a script, under the allow rule, three steps precede every import but `os` and `sys`
+# (TASK 115 R1.2, as TASK 112 R1.8 does for `archive_move.py`):
+# - its own directory leaves `sys.path`, so no file planted beside the script answers an import:
+#   not a standard-library name, not one the standard library lacks on this platform (`subprocess`
+#   imports `msvcrt` on POSIX), and not a sibling's name; the inbound mode loads its siblings by
+#   explicit path (`_load_siblings`);
+# - no bytecode is written, and `.pyc` files are looked up under the null device, where none can
+#   exist, so a `.pyc` planted in `__pycache__/` is never read.
+# The module has no `from __future__` statement: at run time it imports `__future__`.
+if __name__ == "__main__":
+    _HERE = os.path.dirname(os.path.realpath(__file__))
+    sys.path[:] = [entry for entry in sys.path if os.path.realpath(entry or os.curdir) != _HERE]
+    sys.dont_write_bytecode = True
+    sys.pycache_prefix = os.path.join(os.devnull, "rebase-links-pycache")
+
+import re  # noqa: E402
+from typing import NamedTuple  # noqa: E402
 
 #: Schemes and forms that are never document-relative.
 _ABSOLUTE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|/|#)", re.IGNORECASE)
@@ -387,14 +413,47 @@
     return None
 
 
+def _load_siblings():
+    """The `slot_links` module, its siblings loaded by explicit path (TASK 115 R1.2).
+
+    No sibling is found by a path search, so a package or an extension module planted beside the
+    script under a sibling's name is never chosen. `rebase_links` is this module, whether it runs
+    as `__main__` or was imported; `slot_links` finds all three in `sys.modules`.
+    """
+    import importlib.util
+    here = os.path.dirname(os.path.realpath(__file__))
+    sys.modules.setdefault("rebase_links", sys.modules[__name__])
+    for name in ("archive_move", "task_id_tool", "slot_links"):
+        if name in sys.modules:
+            continue
+        spec = importlib.util.spec_from_file_location(name, os.path.join(here, f"{name}.py"))
+        module = importlib.util.module_from_spec(spec)
+        sys.modules[name] = module
+        try:
+            spec.loader.exec_module(module)
+        except BaseException:
+            del sys.modules[name]
+            raise
+    return sys.modules["slot_links"]
+
+
 def _main(argv=None):
     import argparse
     import json
-    import sys
+
+    argv = sys.argv[1:] if argv is None else list(argv)
+    if argv[:1] == ["--inbound"]:
+        # TASK 115 R1.1: `skill-archive-task` Step 8, loaded here only, so the file mode never
+        # loads the inbound module.
+        return _load_siblings().main(argv[1:])
 
     ap = argparse.ArgumentParser(
         description="Rebase document-relative links after a file moves "
-                    "(ARC-2). The move is the trigger; existence is the guard.")
+                    "(ARC-2). The move is the trigger; existence is the guard.",
+        epilog="Inbound mode: rebase_links.py --inbound --task docs/tasks/task-<ID>-<slug>.md "
+               "[--plan docs/plans/plan-<ID>-<slug>.md] [--since <rev>] [--dry-run] [--json] "
+               "re-targets the slot links an archived task wrote in other documents "
+               "(TASK 115, skill-archive-task Step 8).")
     ap.add_argument("files", nargs="+", help="moved markdown file(s)")
     ap.add_argument("--from", dest="from_dir", required=True,
                     help="directory the file used to live in (repo-relative)")
diff --git a/.agent/tools/rebase_links_next.py b/.agent/tools/rebase_links_next.py
deleted file mode 100644
--- a/.agent/tools/rebase_links_next.py
+++ /dev/null
@@ -1,570 +0,0 @@
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
-
-Inbound mode (TASK 115, `skill-archive-task` Step 8). With `--inbound` as the
-first argument, the remaining arguments go to `main(argv)` of `slot_links.py`:
-
-    rebase_links.py --inbound --task docs/tasks/task-<ID>-<slug>.md
-        [--plan docs/plans/plan-<ID>-<slug>.md] [--since <rev>] [--dry-run] [--json]
-
-It re-targets the slot links that an archived task wrote in other documents, and
-lists the others. The allow rule that names this script covers the mode, so
-archiving stays automatic (TASK 111 D13). Its exit codes are those of
-`slot_links.py`.
-"""
-
-import os
-import sys
-
-# Run as a script, under the allow rule, three steps precede every import but `os` and `sys`
-# (TASK 115 R1.2, as TASK 112 R1.8 does for `archive_move.py`):
-# - its own directory leaves `sys.path`, so no file planted beside the script answers an import:
-#   not a standard-library name, not one the standard library lacks on this platform (`subprocess`
-#   imports `msvcrt` on POSIX), and not a sibling's name; the inbound mode loads its siblings by
-#   explicit path (`_load_siblings`);
-# - no bytecode is written, and `.pyc` files are looked up under the null device, where none can
-#   exist, so a `.pyc` planted in `__pycache__/` is never read.
-# The module has no `from __future__` statement: at run time it imports `__future__`.
-if __name__ == "__main__":
-    _HERE = os.path.dirname(os.path.realpath(__file__))
-    sys.path[:] = [entry for entry in sys.path if os.path.realpath(entry or os.curdir) != _HERE]
-    sys.dont_write_bytecode = True
-    sys.pycache_prefix = os.path.join(os.devnull, "rebase-links-pycache")
-
-import re  # noqa: E402
-from typing import NamedTuple  # noqa: E402
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
-def _load_siblings():
-    """The `slot_links` module, its siblings loaded by explicit path (TASK 115 R1.2).
-
-    No sibling is found by a path search, so a package or an extension module planted beside the
-    script under a sibling's name is never chosen. `rebase_links` is this module, whether it runs
-    as `__main__` or was imported; `slot_links` finds all three in `sys.modules`.
-    """
-    import importlib.util
-    here = os.path.dirname(os.path.realpath(__file__))
-    sys.modules.setdefault("rebase_links", sys.modules[__name__])
-    for name in ("archive_move", "task_id_tool", "slot_links"):
-        if name in sys.modules:
-            continue
-        spec = importlib.util.spec_from_file_location(name, os.path.join(here, f"{name}.py"))
-        module = importlib.util.module_from_spec(spec)
-        sys.modules[name] = module
-        try:
-            spec.loader.exec_module(module)
-        except BaseException:
-            del sys.modules[name]
-            raise
-    return sys.modules["slot_links"]
-
-
-def _main(argv=None):
-    import argparse
-    import json
-
-    argv = sys.argv[1:] if argv is None else list(argv)
-    if argv[:1] == ["--inbound"]:
-        # TASK 115 R1.1: `skill-archive-task` Step 8, loaded here only, so the file mode never
-        # loads the inbound module.
-        return _load_siblings().main(argv[1:])
-
-    ap = argparse.ArgumentParser(
-        description="Rebase document-relative links after a file moves "
-                    "(ARC-2). The move is the trigger; existence is the guard.",
-        epilog="Inbound mode: rebase_links.py --inbound --task docs/tasks/task-<ID>-<slug>.md "
-               "[--plan docs/plans/plan-<ID>-<slug>.md] [--since <rev>] [--dry-run] [--json] "
-               "re-targets the slot links an archived task wrote in other documents "
-               "(TASK 115, skill-archive-task Step 8).")
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
diff --git a/.agent/skills/skill-archive-task/SKILL.md b/.agent/skills/skill-archive-task/SKILL.md
--- a/.agent/skills/skill-archive-task/SKILL.md
+++ b/.agent/skills/skill-archive-task/SKILL.md
@@ -316,7 +316,9 @@
 Run it after Step 7, or after Step 7.1 skipped the plan, and before the new `docs/TASK.md` is
 written. An allow rule names `rebase_links.py`, so the command runs with no prompt.
 
-<!-- stage3:step8-command -->
+```bash
+python3 .agent/tools/rebase_links.py --inbound --task docs/tasks/{filename} --plan docs/plans/{plan_filename} --since {base_revision}
+```
 
 - **Operands.** Delete `--plan docs/plans/{plan_filename}` when Step 7 did not archive the plan,
   and `--since {base_revision}` when Step 2 found no base.
@@ -427,7 +429,9 @@
     - Validate: `docs/PLAN.md` does NOT exist ✓.
 11. **Step 8** — re-target the slot links this task wrote. `{old-base}` is the Base revision of
     Step 2:
-    <!-- stage3:flow-step8-command -->
+    ```bash
+    python3 .agent/tools/rebase_links.py --inbound --task docs/tasks/task-{OLD_ID}-{old-slug}.md --plan docs/plans/plan-{OLD_ID}-{old-slug}.md --since {old-base}
+    ```
     Exit `3`: report the records; an `INBOUND` link stays, and a `REFUSED` file is fixed by hand.
 12. Create new `docs/TASK.md` for the login feature with ID `{NEW_ID}` and its Base revision.
 
diff --git a/tests/test_committed_settings.py b/tests/test_committed_settings.py
--- a/tests/test_committed_settings.py
+++ b/tests/test_committed_settings.py
@@ -114,14 +114,15 @@
 ARCHIVE_SCRIPT = PROJECT_ROOT / ".agent" / "tools" / "archive_move.py"
 ARCHIVE_COMMANDS = ("python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/",
                     "python3 .agent/tools/archive_move.py docs/PLAN.md docs/plans/",
-                    "python3 .agent/tools/task_id_tool.py", "python3 .agent/tools/rebase_links.py")
+                    "python3 .agent/tools/task_id_tool.py", "python3 .agent/tools/rebase_links.py",
+                    "python3 .agent/tools/rebase_links.py --inbound")
 #: A part of an archive block that moves, guards or creates outside the script (TASK 112 R1.5).
 OUTSIDE_THE_SCRIPT = re.compile(r"^(mv|test|mkdir|\[)\s")
 #: The info words that make a fence a shell block (TASK 112 R6.1).
 SHELL = ("bash", "sh", "shell", "zsh", "console")
 #: The first info word of every fence, in order; an added or relabelled fence fails (R6.1).
 ARCHIVE_FENCES = ("", "", "bash", "python", "", "bash", "bash", "", "", "", "bash", "bash", "",
-                  "bash", "bash", "bash", "bash")
+                  "bash", "bash", "bash", "bash", "bash", "bash")
 SAFE_FENCES = ("", "markdown")
 FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
 
diff --git a/tests/test_script_guards.py b/tests/test_script_guards.py
--- a/tests/test_script_guards.py
+++ b/tests/test_script_guards.py
@@ -9,6 +9,9 @@
   second hard link and a file under `.git/` in any letter case or through a link, with exit 2 and
   no write (``TC-G1``, ``TC-G2``); a file inside is rewritten as before (``TC-G3``); one refused
   operand stops every write (``TC-G7``);
+* `rebase_links.py --inbound` refuses a file with a second hard link and skips a symbolic link,
+  with exit 3 and no write; it rewrites a sub-task inside; neither a module nor a `.pyc`
+  planted beside the script runs (``TC-G8`` to ``TC-G12``, TASK 115);
 * `init_skill.py` refuses a skill directory outside the working directory or under `.git/`, with
   exit 1 and nothing created (``TC-G4``, ``TC-G5``); a directory inside is created (``TC-G6``).
 
@@ -29,6 +32,8 @@
 INIT = PROJECT_ROOT / ".agent" / "skills" / "skill-creator" / "scripts" / "init_skill.py"
 LINKED = "[a](ARCHITECTURE.md)\n"
 REBASED = "[a](../ARCHITECTURE.md)\n"
+SUBTASK = "# Task 112-01: a\n\n[docs/TASK.md](../TASK.md)\n"
+RETARGETED = "# Task 112-01: a\n\n[task-112](task-112-x.md)\n"
 
 
 def _tmp(case):
@@ -122,6 +127,106 @@
         self.assertEqual(moved.read_text(encoding="utf-8"), REBASED)
 
 
+class TestInboundGuard(unittest.TestCase):
+    """TC-G8 to TC-G12: `--inbound` writes only regular files with one hard link (TASK 115).
+
+    The root holds no git repository, so the script walks it. An own link is a slot link in a
+    sub-task file of task 112.
+    """
+
+    def setUp(self):
+        self.root = _tmp(self)
+        self.tasks = self.root / "docs" / "tasks"
+        self.tasks.mkdir(parents=True)
+        (self.tasks / "task-112-x.md").write_text("# Task 112: x\n", encoding="utf-8")
+        self.outside = _tmp(self)
+
+    def inbound(self, script=None):
+        return _run(script or REBASE, ["--inbound", "--task", "docs/tasks/task-112-x.md"],
+                    self.root)
+
+    def test_g8_a_second_hard_link(self):
+        # base-fail: the base rejects --inbound with exit 2.
+        sub = self.tasks / "task-112-01-a.md"
+        sub.write_text(SUBTASK, encoding="utf-8")
+        os.link(sub, self.root / "alias.md")
+        result = self.inbound()
+        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
+        self.assertIn("[REFUSED] docs/tasks/task-112-01-a.md", result.stdout)
+        self.assertEqual(sub.read_text(encoding="utf-8"), SUBTASK)
+        self.assertEqual((self.root / "alias.md").read_text(encoding="utf-8"), SUBTASK)
+
+    def test_g9_a_symbolic_link_to_a_file_outside(self):
+        victim = self.outside / "victim.md"
+        victim.write_text(SUBTASK, encoding="utf-8")
+        (self.tasks / "task-112-02-b.md").symlink_to(victim)
+        result = self.inbound()
+        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
+        self.assertIn("[SKIPPED] docs/tasks/task-112-02-b.md", result.stdout)
+        self.assertEqual(victim.read_text(encoding="utf-8"), SUBTASK)
+
+    def test_g10_a_subtask_inside_is_rewritten(self):
+        sub = self.tasks / "task-112-03-c.md"
+        sub.write_text(SUBTASK, encoding="utf-8")
+        result = self.inbound()
+        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
+        self.assertEqual(sub.read_text(encoding="utf-8"), RETARGETED)
+
+    def _tools_copy(self):
+        tools = self.outside / "tools"
+        tools.mkdir()
+        names = {REBASE.name, "rebase_links.py", "slot_links.py", "task_id_tool.py",
+                 "archive_move.py"}
+        for name in names:
+            shutil.copy2(REBASE.parent / name, tools / name)
+        (self.tasks / "task-112-04-d.md").write_text(SUBTASK, encoding="utf-8")
+        return tools
+
+    def test_g11_a_planted_module_is_not_imported(self):
+        # No module planted beside the script runs (TASK 115 R1.2): a standard-library name, one the
+        # standard library lacks on this platform (`subprocess` imports `msvcrt` on POSIX), a
+        # package or an extension module in a sibling's name.
+        import importlib.machinery
+        tools = self._tools_copy()
+        planted = ("__future__", "re", "typing", "argparse", "json", "difflib", "subprocess",
+                   "msvcrt", "_winapi")
+        for name in planted:
+            sentinel = self.outside / f"sentinel-{name}"
+            (tools / f"{name}.py").write_text(f"open({str(sentinel)!r}, 'w').close()\n",
+                                              encoding="utf-8")
+        siblings = ("slot_links", "rebase_links", "archive_move", "task_id_tool")
+        for name in siblings:
+            package = tools / name
+            package.mkdir()
+            sentinel = self.outside / f"sentinel-package-{name}"
+            (package / "__init__.py").write_text(f"open({str(sentinel)!r}, 'w').close()\n",
+                                                 encoding="utf-8")
+        suffix = importlib.machinery.EXTENSION_SUFFIXES[0]
+        (tools / f"slot_links{suffix}").write_bytes(b"not a shared object")
+        result = self.inbound(tools / REBASE.name)
+        self.assertIn(result.returncode, (0, 3), result.stdout + result.stderr)
+        ran = [name for name in planted if (self.outside / f"sentinel-{name}").exists()]
+        ran += [name for name in siblings
+                if (self.outside / f"sentinel-package-{name}").exists()]
+        self.assertEqual(ran, [], "a module planted beside the script was imported")
+
+    def test_g12_a_planted_pyc_is_never_read(self):
+        import py_compile
+        tools = self._tools_copy()
+        sentinel = self.outside / "sentinel-pyc"
+        evil = self.outside / "evil.py"
+        evil.write_text(f"open({str(sentinel)!r}, 'w').close()\n", encoding="utf-8")
+        cache = tools / "__pycache__"
+        cached = cache / f"slot_links.{sys.implementation.cache_tag}.pyc"
+        cache.mkdir()
+        py_compile.compile(str(evil), cfile=str(cached),
+                           invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
+        result = self.inbound(tools / REBASE.name)
+        self.assertIn(result.returncode, (0, 3), result.stdout + result.stderr)
+        self.assertFalse(sentinel.exists(), "a .pyc planted in __pycache__/ was read")
+        self.assertEqual(os.listdir(cache), [cached.name])
+
+
 class TestInitSkillGuard(unittest.TestCase):
     """TC-G4 to TC-G6."""
 
diff --git a/.agent/tools/test_slot_links.py b/.agent/tools/test_slot_links.py
--- a/.agent/tools/test_slot_links.py
+++ b/.agent/tools/test_slot_links.py
@@ -31,7 +31,7 @@
 
 TOOLS = Path(__file__).resolve().parent
 #: The script an allow rule names. Stage 3 of TASK 115 points this at `rebase_links.py`.
-REBASE = TOOLS / "rebase_links_next.py"
+REBASE = TOOLS / "rebase_links.py"
 
 TASK = "docs/tasks/task-033-admission-core-v1.md"
 PLAN = "docs/plans/plan-033-admission-core-v1.md"
~~~~

## Cluster G — stage 3, the registration edit

### G1 — the patch applied

The three SHA-256 values of F6 were checked first: equal. Every file the patch touches, before
the edit:

| File | SHA-256 | Mode |
| :--- | :--- | :--- |
| `.agent/tools/rebase_links.py` | `b0b03b3fdce06b0a29f3d91dfda3de63d002dfe1b01018497ff9f5cd96ff0366` | `100644` |
| `.agent/tools/rebase_links_next.py` | `094304333b45dd06a9ba0f686332b14b8e6fd2ec8fa6ff366fb6bc3392799787` | `100644` |
| `.agent/skills/skill-archive-task/SKILL.md` | `1fe324d7b7875756bb3c92b38049de714052ee657344c6b99a1bc6978eccacb7` | `100644` |
| `tests/test_committed_settings.py` | `8de4e86460834da34e68dbfca020969f114c919d27a83a74fb099f3d538478f7` | `100644` |
| `tests/test_script_guards.py` | `cff08db294391e8c811bdb647d0929903a129a8538d1afeccedd6d212de9209f` | `100644` |
| `.agent/tools/test_slot_links.py` | `bc5293ba9a8361c79748fb51f7b0cada2b5745174b497e9ddfe4fd09c59fb7d9` | `100644` |

`git apply --whitespace=nowarn` of the patch exited 0. The postcondition holds:

- `rebase_links.py` hashes to `094304333b45…`, the F6 value for the copy;
- `rebase_links_next.py` is gone;
- `git apply --check -R` of the patch passes.

The tree fingerprint was `df3e3dffc399` before the run and `c059d51f7ebb` after it, before this
paragraph was written.

### G2 — the gates of stage 3

- **Gates:** all pass. The CI pytest list counts 520 and the tool suite 249. The curated suite
  counts 543, which is 538 plus TC-G8 to TC-G12, and is OK. The advisory archive scan lists the
  same 8 errors.
- **Declared paths:** `git status` lists 32 entries, and each is declared. `rebase_links_next.py`
  is gone, as G declares.
- **Against D0:** `validate_skill.py` exits 0 for `skill-archive-task`. `analyze_gaps.py` reports
  1 gap and 6 advisories, as in D0; the weak-wording advisory is on a line of the base text.
- **Resolver,** `--targets-changed` without `--fix`: 69 documents and 347 references.
  - The same 12 errors as in F5, and no `REFERENT_MOVED`.
  - 3 more `DRIFT_SUSPECT` warnings: bare coordinates into `rebase_links.py` in the ARC-5 and
    ARC-6 records and in the PLAN 098 archive.
  - The patch causes no `REFERENT_MOVED` and no `REFERENT_ABSENT`.
- **The TASK §13.5 dry run,** the command as written: 8 `INBOUND`, 3 slot links in the archive,
  exit 3. The tree fingerprint `d911df64db6c` is the same before the run and after it, and no
  file under `.agent/tools/` is newer than the start of the run.

**Scratchpad.** Deleted after G1, as the PLAN's Rollback point lists them:

- `draft/inbound_guard_tests.py`, the generator `gen_stage3_patch.py`, the F3 driver and
  `mutation_driver.py`;
- `g11_mutation.py` and `one_mutant.py`, the sensitivity drivers of F4.1 and F4.2;
- the G1 driver, and the resolver's JSON output.

Kept until H1: the gate runner, the fingerprint script, the register check and a timestamp
marker. None of them holds a copy of a repository file.

## Cluster H — stage 4

### H1 — the focused review of the applied patch

Both agents read the tree at fingerprint `8035b1caac9e` and quoted it at their start and end; the
caller recomputed it at each return: equal. Both confirmed the hashes of `rebase_links.py`
(`094304333b45…`), `slot_links.py` (`e729c176870f…`) and the patch (`2218ae0c5d68…`), that the
copy is gone, and that `git apply --check -R` passes.

- **Code review: APPROVED.** No BLOCKING or MAJOR finding.
  - Each section of the patch, reversed in memory, gives the SHA-256 that G1 recorded.
  - The file mode matches the base on 35 of 37 argument lists. Only `-h` and `--help` differ, by
    the epilog that B1 intends.
  - The TASK §13.5 dry run, also with `--since` set to the base, lists the same 8 records and
    re-targets none.
  - TC-S7 fails on each of six planted edits of the skill text.
  - MINOR 1 to 4 concern tests:
    - the one-line rule of D9 is not pinned;
    - TC-S7 does not parse the `--inbound` operands;
    - in TC-G11 the package of the same name shadows the junk extension module;
    - the guard subprocesses inherit `PYTHONDONTWRITEBYTECODE`, `PYTHONSAFEPATH` and
      `PYTHONPYCACHEPREFIX`, and no case fails without `sys.dont_write_bytecode = True`.
  - MINOR 5 (medium confidence): Step 8 and TASK R8.5 say that an `INBOUND` record is a link the
    task did not write. Without `--since`, in a ledger record and above the line bound, it can
    be a link the task wrote.
  - NIT 1 to 3:
    - Example Flow item 11 names only `REFUSED`;
    - no step defines `{filename}` by name, which predates this task;
    - stale labels in the PLAN, in two test docstrings and in `ORCHESTRATOR.md`.
  - INFO 1 to 3: the scripts no longer run on Python 3.9 (D14); the wording of R1.1 for `-h`;
    the start-up time of the file mode, from 31 ms to 132 ms.
- **Security audit: INCOMPLETE.** The adversarial review of the stage-3 diff and of the code it
  registers ran to completion. It found no CRITICAL, HIGH or MEDIUM issue.
  - The import guard holds at the final name. No path lookup reaches `.agent/tools/`, the real
    `.pyc` is never read, and no `.pth` or customize hook is on the path.
  - The allow rule approves every form of Step 8. Option abbreviations and argument injection
    are refused, and TC-S7 pins every fenced command.
  - The file mode is byte-identical to the base.
  - INFO 1 to 4:
    - Python 3.9 (D14);
    - `PYTHONPATH`;
    - a link to the script on Python 3.11 to 3.13;
    - 31 MEDIUM hits of the in-process regex scan, triaged as false positives (docstring prose
      and test literals).
  - The unfinished part is the external-scanner layer: semgrep, gitleaks, trufflehog, bandit and
    pip-audit are not installed.

**The INCOMPLETE verdict.** Stage 2 left the same part unfinished, for the same cause.

- `security-audit` §6.2 rule 1 gives each part one re-run in a run. This part had its re-run in
  F4.
- Rule 2 then leaves the choice to the operator. D11 is that choice for this part in this run:
  ship with the gap recorded.
- Rule 3 does not apply, because the bypass hunt finished.

The run therefore does not take the Failure path of G. A restore, then a re-apply of the same
patch under D11, would end in this state, and the next stage-4 audit would end INCOMPLETE for the
same cause. The operator may still restore stage 3 with
`git apply -R --whitespace=nowarn docs/reviews/framework-audit-115-stage3.diff`.

**The findings.** After stage 3 only the retro's records follow (`framework-upgrade` §3 step 4,
item 3), and most of the items touch a file of the patch. The MINOR and NIT items go to the
retro's work-item, with the code NITs of round 3. These are not filed:

- the PLAN label, which is history once the PLAN is archived;
- INFO 1 (D14), INFO 2 (a wording point of the TASK) and INFO 3 (negligible).

## Retro (`run-feedback` §7)

The claim `framework-upgrade-inbound-slot-links-retargeted-on-archive` was taken in §0 and released
after the filing. The run resumed after a context summary with the instruction to ask no further
question. The retro therefore used the observed signals only, as §7 allows for a run without the
operator's answer, and the final message lists them.

`collect` took 9 signals. `file` turned 7 of them into work-items:

| ID | Title | Source |
| :--- | :--- | :--- |
| WI-39 | Allow-listed scripts import a module planted beside them | D10; B1 and M1 of stage 2 |
| WI-40 | `rebase_links.py` writes through a linked parent directory | D10; L10 and I1 of stage 2 |
| WI-41 | KaTeX advisory GHSA-238p-pmpm-9mq7 in the renderer lockfiles | the `deps` re-run of F4 |
| WI-42 | Security-audit scans hide what did not run | O-1 to O-3; the two `INCOMPLETE` audits |
| WI-43 | Review follow-ups of the inbound slot-link mode | round 3 of stage 2; H1 |
| WI-44 | Three slot links older than Step 8 point at the current task | the TASK §13.5 dry run |
| WI-45 | No deny rule for the git commands that discard the uncommitted work of a run | the stash incident of D1 |

- **Dismissed as noise (2):** the gate failure of F1, fixed in the run; the slips recorded above,
  the temporary copy of D1 and the hash line of F4.2.
- **Duplicate candidates:** none was the same item. AT-2 concerns agent teams; ARC-11 and WIR-4
  matched common words only.
- **Gates after the filing:** all pass.

**Scratchpad, at the end of the run.** Deleted: the gate runner, the fingerprint script, the
register check, two timestamp markers, the resolver output of G2 and the seven work-item bodies.

The stage-4 reviewers left files of their own in the scratchpad, against their brief, and these
were deleted as well:

- `base_rl.py`, byte-identical to the base text of `rebase_links.py`: a copy of a repository file
  outside version control, which the brief forbade;
- import traces, a probe script, a help text and the JSON of one `--since` dry run.

The tree was not touched: the fingerprint `8035b1caac9e` was the same after both reviews
returned. No file of this run remains in the scratchpad.
