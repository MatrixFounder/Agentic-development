# Framework Audit 116 — The file mode refuses a directory that resolves outside, and three git commands are denied

- **Task:** 116 `archive-hardening-and-git-deny-rules`. It archives to
  `docs/tasks/task-116-archive-hardening-and-git-deny-rules.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1,
  Modes A and B.
- **Date:** 2026-10-08. **Base revision:** `c8aba597ed06545a8fc0933238aaa4510f059db2`, clean tree
  at start.
- **Source:** WI-40, WI-43 (part), WI-44 and WI-45, with the operator's request of 2026-10-08 (TASK
  D1).
- **Independence:** each audit round runs in a separate read-only agent. Same-model agreement is
  corroboration, not independent confirmation.

## 0. Emergency Bypass

`[BYPASS_TIER_PROTECTION]`: `skill-safe-commands` is a TIER 0 skill (TASK R5.1). One cell of its
table states that `rebase_links.py` compares paths without resolving links; after R1 that cell
is false. The edit changes that cell and the version, in the stage-3 patch, and no pattern.

## Archive (§1)

TASK 115 archived under ID 115 with `task_id_tool.py "inbound-slot-links-retargeted-on-archive"
--proposed-id "115" --no-correction` (`generated`). The commands, as run:

```sh
python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/task-115-inbound-slot-links-retargeted-on-archive.md
python3 .agent/tools/rebase_links.py docs/tasks/task-115-inbound-slot-links-retargeted-on-archive.md --from docs --to docs/tasks --slot docs/PLAN.md=docs/plans/plan-115-inbound-slot-links-retargeted-on-archive.md
python3 .agent/tools/archive_move.py docs/PLAN.md docs/plans/plan-115-inbound-slot-links-retargeted-on-archive.md
python3 .agent/tools/rebase_links.py docs/plans/plan-115-inbound-slot-links-retargeted-on-archive.md --from docs --to docs/plans --slot-must-exist --slot docs/TASK.md=docs/tasks/task-115-inbound-slot-links-retargeted-on-archive.md
python3 .agent/tools/rebase_links.py --inbound --task docs/tasks/task-115-inbound-slot-links-retargeted-on-archive.md --plan docs/plans/plan-115-inbound-slot-links-retargeted-on-archive.md --since fc534769f2f946488c89a7fa48179b76f9c8750a
```

- Both moves: `"ok": true`, method `link`.
- Step 5.5: 5 rewritten, exit 0. Step 7.6.5: 1 `SLOT_RESOLVED`, exit 0.
- Step 8, its first run in this repository: exit 3, 0 re-targeted, 8 `INBOUND`, 3 slot links in
  the archived documents, lines attributed since the base of TASK 115. Step 8 rewrote no file.
  The 8 records are those of the TASK 115 §13.5 dry run; three of them are WI-44.

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

A read-only `task-reviewer` agent, with no execution tool: it ran neither the register scan nor the
resolver. It found no `skill-self-improvement-verificator` §4 failure condition, and it confirmed
the staging of R6 but for one module.

| # | Severity | Finding | Applied in revision 2 |
| :--- | :--- | :--- | :--- |
| B1 | BLOCKER | the new sentence of §5 rule 6 names the commands, and `test_git_rollback_contract` TC-04 fails | §10.4 names them by position; R4.5; A7 |
| M1 | MAJOR | Example Flow keeps a ledger `INBOUND` link that Step 8 gives to the operator | §10.2 |
| M2 | MAJOR | closing WI-40 drops I1; D5 cites I1 for a window the file mode does not pin | D5, D8; §11 |
| M3 | MAJOR | WI-45 closes with no live check | R4.7, A9 |
| M4 | MAJOR | R5.7 cannot pass on the table row | R5.7 exception |
| M5 | MAJOR | no mechanism for the base-fail run; no rule against the commands of D1 of audit 115 | R6.5, R6.6 |
| m1–m12 | MINOR | twelve items, listed below | listed below |
| n1–n7 | NIT | seven items, listed below | listed below |

The MINOR items, each with where revision 2 applies it:

- m1 the TC-G14 clause → TC-G14; m2 the basis of D4 → D4; m3 a run without `--plan` → §10.2;
- m4 a wrap before `--inbound` → R2.3; m5 "ends with" → R2.1, R2.2; m6 the WI-43 body → R5.6;
- m7 the count of 5 → R3.5; m8 ARC-2 → D6; m9 the carriers → D10, §11;
- m10 documents before stage 3 → R6.7; m11 the inferred forms → R4 Limit; m12 committed
  cases → R2.5.

The NIT items: n1 → R6.1; n2 → R1 **Why**; n3 → R2.4; n4 → D1 to D3, D9; n5 → §2, §4, §12;
n6 → §10.1; n7 → §12.

The orchestrator ran the checks the agent could not: `scan_register.py` on revision 2, 0 warn;
`check_positional_refs.py --all docs/TASK.md`, 10 of 10 references resolve.

### Round 2 — TASK revision 2: PASS

The same agent, resumed. Its first round-2 turn was stopped at the operator's pause and run again
on the same tree; it quoted fingerprint `3decfe7cc594`, and the caller recomputed it: equal. No
§4 failure condition, no staging rule violated. B1, M1, M3 and M5 are closed; M4 and m3 stay
partly open. Revision 3 applies these findings, with no further round:

| # | Severity | Finding | Revision 3 |
| :--- | :--- | :--- | :--- |
| 1 | MAJOR | the §10.5 cell is 190 characters, a second `cell_width` WARN | §10.5 under 120 characters |
| 2 | MINOR | bullet 1 of §10.2 still takes a `docs/PLAN.md` link of a run without `--plan` | §10.2 |
| 3 | MINOR | D5 credits option 1 to the operator | D5 |
| 4 | MINOR | the follow-up work-item depends on the retro | R5.6 |
| 5 | MINOR | R4.7 has no precondition check and no failure rule | R4.7 |
| 6 | MINOR | R6.7 names no marker and omits R5.5 | R6.7 |
| 7 | MINOR | three of the five kept links mean TASK 063 | the operator decides (D11) |
| 8 | MINOR | R2.4 does not tell a value from a positional argument | R2.4 |
| 9–14 | NIT | R6.5 deviation; R1.1 last; documented forms; `_approves` docstring; A4; indentation | R6.5, R1.1, R4 Limit, R6.1, A4, §10.1 |

**Revision 3.** It applies findings 1 to 6 and 8 to 14 as the table states. `scan_register.py`:
0 warn; `check_positional_refs.py --all docs/TASK.md`: 12 of 12 resolve.

**Operator decisions (2026-10-08), quoted:**

- On the summary of the planned changes: "Yes, proceed".
- D11, on finding 7: "Yes, all six links (Recommended)".

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: FAIL

A read-only `plan-reviewer` agent, at fingerprint `7ef08f99f504`. No BLOCKER and no §4 failure
condition. It confirmed the F2 failure set, the declared paths and the staging.

| # | Severity | Finding | Applied in revision 2 |
| :--- | :--- | :--- | :--- |
| M1 | MAJOR | the H Failure paragraph has no triggers, no mismatch rule and no `INCOMPLETE` branch | H Failure; H1 re-apply |
| M2 | MAJOR | the mutations and the copy runs have no mechanism, and their scripts no inventory line | Mutations; inventory; A1, A4 |
| M3 | MAJOR | R5.7 is never checked for `skill-safe-commands` | E2, H2 |
| m1–m14 | MINOR | fourteen items, listed below | listed below |
| n1–n8 | NIT | eight items, listed below | listed below |

The MINOR items, each with where revision 2 applies it:

- m1 the class of TC-G13 and TC-G14 → A2, E1;
- m2 the failing methods → F2, E1;
- m3 the fix-round re-runs → G1;
- m4 the parts of §4.5 → H1 step 1;
- m5 the resolver after the apply → H2;
- m6 the dependency of D on A → the schedule;
- m7 the title of WI-46 → Declared paths;
- m8 the pytest cache → Rollback point;
- m9 the base text of the register scan → `regcheck.py`;
- m10 the scope of the copy → A4;
- m11 the probe's fingerprint and failure → I2;
- m12 TC-S6 and TC-S9 shown green → F2;
- m13 `skill-enhancer` → B0, B2, H2;
- m14 the reviewed hashes → G1, H1 step 2.

The NIT items: n1 and n2 → Sequencing rule; n3 → `run_gates.sh`; n4 → H2; n5 → E1 (`SLUG`);
n6 → F2; n7 → Rollback point, E1; n8 → Coverage, E1, Declared paths.

Checks the agent could not run: `scan_register.py` on revision 2, 0 warn, 9 of 9 detectors live;
`plan_gantt.py --check`, current; `check_positional_refs.py --all docs/PLAN.md`, 9 of 9 resolve.

### Round 2 — PLAN revision 2: PASS

The same agent, resumed, at fingerprint `ce572b04231c`. M1 to M3 and every MINOR and NIT item of
round 1 are closed. Revision 3 applies its findings, with no further round:

| # | Severity | Finding | Revision 3 |
| :--- | :--- | :--- | :--- |
| r1 | MINOR | H2's resolver rule against the Failure paragraph; the generator deleted too early | H2 precedence; inventory to I1 |
| r2 | MINOR | the failures of H1 steps 2, 4 and 5 trigger nothing | H1 steps 2, 4, 5 |
| r3 | MINOR | `run_gates.sh` would run the install steps | inventory: `run:` steps only, no install |
| r4 | MINOR | the source of the test text at A2 and A4 | Test text before the patch |
| r5 | MINOR | E2 stricter than R5.7 | E2: WARNs matched to added lines |
| r6–r11 | NIT | the `INCOMPLETE` branch; G1 re-runs; quoted hashes; reopening; `tests/.scratch/`; `PAIRS` | Failure, G1, Rollback point, E1 |

## Execution (§3)

§3.1 base check: HEAD is the base; every path the PLAN edits is tracked; every path it creates is
absent and not ignored.

### Cluster A

- **A1.** `rebase_links_next.py`, a byte copy: SHA-256 `094304333b45…`, equal to the base file's.
  `copy_runner.py`: 44 passed, with `rebase_links` loaded from the copy.
- **A2.** TC-G13 and TC-G14, loaded from memory against the copy: TC-G13 fails, because the copy
  rewrote the file outside through the link; TC-G14 and the five other cases pass. The tree
  fingerprint is the same before and after.
- **A3.** The check of TASK R1.1 is the last of `_refuse_operand`, and its docstring states it.
- **A4.**
  - The seven cases of `TestRebaseLinksGuard` pass against the copy;
  - `copy_runner.py`: 44 passed;
  - the copy differs from the base in three hunks, all in `_refuse_operand`;
  - `mutation_driver.py`: 2 of 2 mutants killed, and the copy restored to its SHA-256
    `07e0f2929d3f…`.

### Clusters B to D

- **B0.** Before any skill edit, `validate_skill.py` exits 0 for both skills. `analyze_gaps.py`
  reports 1 gap and 6 advisories for `skill-archive-task`, and 1 gap and 7 advisories for
  `skill-safe-commands`. Each gap is "[Richness] Missing or empty 'examples/' directory".
- **B1, B2.** `skill-archive-task` 2.4 holds the text of TASK §10.2. TC-S7 passes as at the base,
  `validate_skill.py` exits 0, and `analyze_gaps.py` reports B0's gap and advisories, no more.
  - The register check found two sentences of §10.2 over the limit, 42 and 39 words, on added
    lines (R5.7). TASK revision 4 splits both, in the TASK and in the skill, with no change of
    meaning; the check then finds no `WARN` on an added line.
- **C1.** The six links of TASK R3 name their archives, and each file differs from the base only
  in them. All four targets exist.
- **C2.** The dry run of TASK §13 item 5 lists two records, `CHANGELOG.md:3121@c8aba59` and
  `CHANGELOG.ru.md:3125@c8aba59`, and counts 3 slot links in archived documents; exit 3. D3 then
  moved both lines down by the v3.39.0 entry. The tree
  fingerprint `259638a349a2` is the same before and after.
- **D1.** §5 rule 6 holds the text of TASK §10.4. `test_git_rollback_contract`,
  `test_mermaid_wiring` and `test_loop_contract` pass.
- **D2, D3.** `docs/ARCHITECTURE.md` states R1.1 and the deny list; both changelogs hold v3.39.0
  with the key for an existing install. No `WARN` on an added line.
- **D4.** WI-40, WI-44 and WI-45 are `done`; WI-46 is filed and named by WI-40's blockquote; WI-43
  stays open with a blockquote above its body; the index moved three lines and added one.
- **D5.** `System/Docs/SKILLS.md`, `ORCHESTRATOR.md` and `WORKFLOWS.md` name neither a version
  nor a behaviour that changes. No file was edited.

### Clusters E and F

- **E1.** The generator wrote `docs/reviews/framework-audit-116-stage3.diff`: 6 file sections,
  962 lines. **E2.** `git apply --check` passes. The patched `skill-safe-commands`, scanned
  through stdin, carries one `WARN` on an added line: `cell_width`, 480 characters, the
  command cell of the Framework scripts row, unchanged from the base. The new reason cell is 113
  characters.
- **F1.** Every gate passes. The CI pytest list counts 520, the tool suite 249, the curated suite
  543. The advisory archive scan lists the 8 errors of the base. `git status` lists 21 entries,
  each declared. No `WARN` on an added line in the run's documents.
- **F2,** one run of `basefail_driver.py`:
  - with the patch's two test parts applied, 39 cases ran, and exactly the four expected ones
    failed: TC-G13, TC-S6, the table case of TC-S8 and the denied case of TC-S9;
  - with the deny list in memory, TC-S6 and TC-S9 pass, 4 cases;
  - with checks that accept everything in memory, TC-S7b and TC-S7c fail, 2 of 2;
  - `TestRebaseLinksGuard` against the copy: 7 passed;
  - the reverse apply restored both files to their SHA-256, and the tree fingerprint was the same
    before and after.

Hashes for stage 2: the patch `e9cea5e9eccd126812f915675fba21bea5d3a138bbe9b6e76874ec8c9698deff`, `rebase_links_next.py` `07e0f2929d3fb9cb634d32020e9ddf586763c50fe9647b9bd4bde63ce0107b55`.

### G1 — stage 2, round 1

Both agents read the tree at fingerprint `b4ce0d925511` and quoted it at their start and end; the
caller recomputed it at each return: equal. Both quoted the patch `e9cea5e9eccd…` and the copy
`07e0f2929d3f…`.

- **Code review: CHANGES REQUESTED.** BLOCKING 1: an operand with `..` after a directory link
  defeats R1.1. MINOR 2 to 6, LOW 7 and 8, NIT 9 to 12, LOW 13.
- **Security audit: FAIL.** H1 (HIGH, CWE-59): the same defect, measured; in a default consumer
  install the links of `.agentic-development`, `.agent/tools` and `System` let an operand such as
  `.agent/tools/../../CLAUDE.md` rewrite a file outside. M1: the documents claim R1.1. L1: the deny
  rules miss `git reset --ha` (measured) and other spellings. L2: WI-46 names one race of three.
  I1 to I7. The external scanners are not installed.
- The two agents found H1 and BLOCKING 1 apart, with the same model: corroboration, not
  independent confirmation.

**Incident.** The two agents chose the same scratch name, `probe116`, for their probe directories.
The code reviewer's directory `probe116.HpMQkn` was removed at cleanup, by one of the two agents,
and the code reviewer's `probe116.path` was overwritten by the security auditor. Both reports were complete, and the tree
fingerprint was equal at both returns. The next briefs give each agent its own name.

**Operator decision D12 (2026-10-08), quoted**, on the external scanners: "Это уже записано как wi-42
и будет исправлено в следующей задаче".

### G1 — fix round 1

TASK revision 5 states the round. The test came first: TC-G15 failed against the copy, which
rewrote the file outside through `docs/up/../victim.md`.

- **The copy (BLOCKING 1, H1):** R1.1 resolves the operand's directory as written, each link before
  the `..` that follows it; the docstring states it.
- **The patch's tests:**
  - TC-G15; the reason of TC-G2's firmlink case (MINOR 5);
  - TC-S7c asserts the reason of each planting, and plants `--dry-run=1` and `--since --dry-run`
    (MINOR 4, LOW 7);
  - one `_fill` helper for the placeholders, used by `_archive_commands` and `_inbound_problems`;
    exact continuations, and no comment line read as a command (MINOR 6);
  - the docstrings of `TestRebaseLinksGuard`, TC-S9 and `_denied` (NIT 9, NIT 10, I4).
- **Documents (M1, L1, I1, I2, NIT 12, LOW 13):**
  - the TASK: the text of §10.2 and §10.4, the Limit of R4, D9 and R6.7;
  - Example Flow item 11, §5 rule 6, `ARCHITECTURE.md` and both changelogs: no spelling that
    passes a deny rule is named.
- **Records (MINOR 2, L2, NIT 11):** WI-43 names four items; WI-46 names three races; one blank line
  after each resolution blockquote.
- **Not taken:** LOW 8, since a wrapped `add_argument` fails safe.

The re-runs:

- **A4:**
  - the eight cases of `TestRebaseLinksGuard` pass against the copy;
  - `copy_runner.py`: 44 passed;
  - the copy differs from the base only in `_refuse_operand`;
  - `mutation_driver.py`: 4 of 4 killed, among them the vulnerable form of round 1 and R1.1 moved
    first.
- **E1, E2:** the patch, 6 sections, 1023 lines; `git apply --check` passes; one `WARN` on an
  added line of `skill-safe-commands`, the base `cell_width` of the command cell.
- **F1:** every gate passes; the curated suite OK.
- **F2:**
  - exactly five cases fail, TC-G13 and TC-G15 among them;
  - TC-S6 and TC-S9 pass with the deny list in memory;
  - TC-S7b and TC-S7c fail with checks that accept everything;
  - eight guard cases pass against the copy;
  - both files are restored, and the fingerprint is the same before and after.

Hashes for the re-check: the patch `9844633e209735ae0f0829c46eaf26f50245dc3bdba65e179bf2a5eeb92e9179`, `rebase_links_next.py` `c8d8d7af39717ad92f608f35636ec4dfee072ee5b6f9870eeca8054de449f135`.

### G1 — stage 2, round 2 (the re-check of fix round 1)

Both agents read the tree at fingerprint `4658961667a5` and quoted it, with the patch
`9844633e2097…` and the copy `c8d8d7af3971…`; the caller recomputed the fingerprint: equal. Each
used its own probe name, `cr116r2.` and `sec116r2.`.

- **Security re-check: PASS.** No CRITICAL, HIGH or MEDIUM finding. 49 operand shapes and 6
  consumer operands were refused, or failed with no write; no archive operand of Steps 5.5 and
  7.6.5 was refused. INFO I1 to I7: WI-40's blockquote omits TC-G15; two documents overstate the
  scope of §5 rule 6; the compound-command claim waits for the probe of R4.7; four older or
  fail-safe items.
- **Code review: APPROVED.** Every round-1 item is closed but LOW 8, not taken. LOW A: four
  sub-checks of `--task` and `--plan` share a reason and have no planting each. LOW B: the order
  mutant is killed on darwin only. LOW C: a comment that ends with `\` hides the next line.
  NIT D: as I1. NIT E: either agent may have removed `probe116.HpMQkn`.

### G1 — fix round 2

The test parts of the patch and four documents change; the copy, the settings hunk and the table
row do not.

- **LOW A:** four plantings, a directory of the right length and a name in the right directory,
  for `--task` and for `--plan`. In memory, 11 of 11 single-check mutants of the helpers fail
  `TestArchiving`.
- **LOW B:** TC-G1 asserts `lies outside the working directory`; the mutant "R1.1 moved first"
  fails TC-G1 on every platform.
- **LOW C:** a comment line continues no line, in `_shell_commands` and in `_archive_commands`,
  which now reads its commands through `_shell_commands`. A case pins it: its mutant fails.
- **NIT D, I1:** WI-40's blockquote names TC-G13 to TC-G15. **I2:** `ARCHITECTURE.md`, both
  changelogs and WI-45 say that `framework-upgrade` forbids the commands in every spelling during a
  run. **NIT E:** the incident paragraph.

The re-runs:

- the four non-test sections of the patch hash to `545963fcabec029d` before and after the round;
- A4: eight guard cases pass against the copy, and 4 of 4 mutants are killed;
- E1, E2: 6 sections; `git apply --check` passes;
- F1: every gate passes; F2: the same five cases fail of 41, the in-memory checks hold, both files
  restored, the fingerprint the same before and after; 21 `git status` entries, each declared.

Hashes for the re-check: the patch `f928411dad5a305e930caeeb81539e6ddd1a623a3cd7fea41a540f700b2444e2`, `rebase_links_next.py` `c8d8d7af39717ad92f608f35636ec4dfee072ee5b6f9870eeca8054de449f135`.

### G1 — stage 2, round 3 (the re-check of fix round 2)

Both agents read the tree at fingerprint `97cc02adb6dd`, with the patch `f928411dad5a…` and the copy
`c8d8d7af3971…`; the caller recomputed the fingerprint: equal.

- **Code review: APPROVED.** Every round-2 item is closed. `_archive_commands` yields the base's 11
  commands for the real skill text, and the same commands for all 335 fenced files of the
  repository. LOW 1 and LOW 2, an inline comment and a trailing `\\`, predate the change. NIT 3
  and NIT 4.
- **Security confirmation: PASS.** The four non-test sections equal those of round 2; the changed
  tests weaken no guard; I1 and I2 are applied. INFO-1: no case pins the move of
  `_archive_commands` onto `_shell_commands`. INFO-2, as LOW 2.

**Operator decision D13 (2026-10-08), quoted**, on WI-46: "надо обработать / решить в рамках этой
же задачи", then "Both modes (Recommended)". TASK 116 takes WI-46 in both modes. The stage-2
verdicts above cover the change before WI-46; its code returns to stage 1.

## Mode A — round 3 (TASK revision 6, the scope of D13)

TASK revision 6 adds R7, both modes of WI-46. It also adds TC-G16 to TC-G19, A10, TC-S7d for
INFO-1, and D13. It changes D5, D8 and §11, and R6.1 adds `slot_links.py`. Every requirement of
revision 5 stands. The round audits the new part.

### Round 3 — TASK revision 6: FAIL

The same agent, resumed, at fingerprint `0aecd5af8196`. No §4 failure condition and no staging rule
broken. The open-then-check design of R7 closes the three windows of WI-46, a racer that swaps back
included, and it keeps R1.2.

| # | Severity | Finding | Revision 7 |
| :--- | :--- | :--- | :--- |
| B1 | BLOCKER | R7 contradicts R1.3, R2.6 and R7.5: a read-only operand, an operand that cannot be opened | R1.3, R2.6; R7.1 read-only open, R7.3 a second open to write; R7.5 names the one change |
| M1 | MAJOR | nothing runs `slot_links_next.py` before stage 3 | R6.4, R6.5, §13 item 4 |
| M2 | MAJOR | the re-check before the write has no test, and no input makes it refuse as worded | R7.3, TC-G20, §11 |
| M3 | MAJOR | no case runs `_main` on CRLF, non-UTF-8, a dry run, a read-only or a shrinking file | TC-F1 to TC-F6, A2 |
| M4 | MAJOR | the records and documents omit R7 and WI-46 | R5.3, R5.4, R5.6, R6.7 |
| m1–m5 | MINOR | `O_NONBLOCK` and no `O_NOFOLLOW`; TC-S7d; A2; reasons; the inbound read | R7.1, R7.2, R6.1, A2, A4, §11 |
| n1–n3 | NIT | the Why; the title; the order of sections, criteria and decisions | R7, H1, §5, §6, §10.6 |

This round was the third Mode A round of the run, the bound of `framework-upgrade` §1.3.

**Operator decision D14 (2026-10-08), quoted:** "New count: fix and re-audit (Recommended)". The
scope of D13 starts its own count of audit rounds.

### Round 4 — TASK revision 7: PASS (the second round of the count of D14)

The same agent, at fingerprint `1406d5853602`. Every finding of round 3 is closed. R7.1 to R7.5 keep
every base result for an operand that nothing changes. TC-G16 to TC-G20 can fail at the base as
stated. Revision 8 applies these findings, with no further round:

| # | Severity | Finding | Revision 8 |
| :--- | :--- | :--- | :--- |
| 1 | MAJOR | R7.4 compares against `os.getcwd()`; `_write_file` receives its own root | R7.4 |
| 2 | MINOR | R7.5 names one deliberate change of three | R7.5, TC-G22 |
| 3 | MINOR | no case pins the comparison with the read descriptor | R7.3, TC-G21 |
| 4 | MINOR | R6.5 claims the subprocess cases of `test_slot_links.py` reach the copy | R6.5, §13 item 4 |
| 5 | MINOR | TC-F5 fails at the base when run as root | TC-F5 |
| 6–9 | NIT | the failure of R7.3; the clauses of TC-F2 to TC-F4; the pytest cache; `fsync` | R7.3, §8, R6.5, §12 |

## Mode B — the scope of D13

PLAN revision 5 adds cluster K for R7, the declared paths of `slot_links.py`, its copy and
`test_rebase_links.py`, and the driver `copies_driver.py`. E, F and G are entered again after K. The
round audits the new part.

### Round 1 of D14's count — PLAN revision 5: FAIL

The plan-reviewer agent, resumed, at fingerprint `14db61f406d4`. The order of K, the staging, the
declared paths and the rollback of the new part are correct. No BLOCKER.

| # | Severity | Finding | Revision 6 (and TASK revision 9) |
| :--- | :--- | :--- | :--- |
| MA1 | MAJOR | the Mutations protocol and the test text cover one copy | Mutations; Test text before the patch (`REBASE`, `SLOT`) |
| MA2 | MAJOR | the `O_NOFOLLOW` row survives TC-G17; two rows need a stated mutant scope | K4 table; TASK §8: TC-G16 reason, TC-G17 inside sub-case, mutant scope |
| m1–m8 | MINOR | eight items: exact ids, TC-S7d, G1's brief, scope after K, §3.1, R6.7, WI-46, TC-F | E1, F2, G1, A4, K0, K4, K5 |
| n1–n6 | NIT | ten clusters; both copies; UC-2; no committed loader; the subprocess driver; a reflow | Sequencing rule, Failure, Coverage, TASK R7.6, F2, H1 |

### Round 2 of D14's count — PLAN revision 6: PASS

The same agent, at fingerprint `a0fa9cf87b23`. MA1, MA2 and every MINOR and NIT item of round 1 are
closed. Each of the seven TC-G rows of the K4 table can be killed by its case as TASK §8 revision 9
states it. Revision 7 applies the round's findings, with no further round:

- r1: the mutants of TC-F1 and TC-F2 are stated, `\r\n` decoded to `\n` and `latin-1` with a
  planted `é`;
- r2: each TC-F mutant runs in a fresh subprocess;
- n1 to n5, n7: the scope of a mutant as TASK states it; the inventory; "no test text"; G1 for a
  change of `test_rebase_links.py`; TC-F5 "not examined" when skipped; `_refuse_operand` kept as
  A left it;
- n6: D5 holds for R7. `System/Docs` names none of `O_NOFOLLOW`, `descriptor`, `hard link` and
  `_write_file`, checked by `grep` on 2026-10-08.

### Cluster K

- **K0.** `slot_links.py` and `test_rebase_links.py` are tracked; `slot_links_next.py` was absent
  and not ignored before K1.
- **K1.** `slot_links_next.py`, a byte copy: SHA-256 `e729c176870f…`, equal to the base file's.
  `copies_driver.py` passed its three suites.
- **K2.** TC-F1 to TC-F6 pass at the base, 6 of 6, and against the copy, 50 of 50 with
  `copy_runner.py`. `basefail_driver.py --copy-only`, run before K3, failed each of TC-G16 to
  TC-G22.
- **K3.** R7.1 to R7.3 and R7.5 in the file mode of `rebase_links_next.py`, and R7.4 in
  `_write_file` of `slot_links_next.py`. `_refuse_operand` stays as A left it.
- **K4.**
  - `TestRebaseLinksGuard` and TC-G19 pass against the copies, 15 cases;
  - `copy_runner.py`: 50 passed; `copies_driver.py`: 177 passed, with both modules loaded from
    the copies;
  - `rebase_links_next.py` differs from its base in four hunks: the `stat` import,
    `_refuse_operand`, the new helpers after it, and `_main`. `slot_links_next.py` differs in two
    hunks, both in `_write_file`: its docstring and the check of R7.4;
  - `mutation_driver.py`: 17 of 19 killed, both copies restored to `e42563b75734…` and
    `5ab8e620be00…`. Every K4 row is killed. Two A4 rows survive: "no real-path check" (TC-G13)
    and "the lexically normalised directory" (TC-G15). The directory check of R7.2 refuses the
    same operands, so neither single layer is seen alone. With both layers dropped, both
    compound mutants are killed.
- **K5.** WI-46 is `done` and its index line is in `## Closed`; WI-40's blockquote names it as
  closed by R7; `ARCHITECTURE.md` and both changelogs state R7.

### Clusters E and F, entered again after K

- **E1.** The generator wrote the patch: 8 file sections, 2194 lines. `slot_links.py` takes the
  text of its copy, and both copies are deleted. **E2.** `git apply --check` passes. The patched
  `skill-safe-commands`, scanned through stdin, carries one `WARN` on an added line: the base
  `cell_width` `WARN` of the command cell, 480 characters.
- **F1.** Every gate passes. The CI pytest list counts 526, the tool suite 255, the curated suite
  543. The advisory archive scan lists the 8 errors of the base. `git status` lists 23 entries,
  each declared. No `WARN` on an added line in the run's documents.
- **F2,** one run of `basefail_driver.py`:
  - with the patch's two test parts applied, 48 cases ran, and exactly the 12 expected ones
    failed. They are TC-G13, TC-G15 to TC-G22, TC-S6, the table case of TC-S8 and the denied
    case of TC-S9;
  - with the deny list in memory, TC-S6 and TC-S9 pass, 4 cases;
  - with checks that accept everything in memory, TC-S7b and TC-S7c fail, 2 of 2;
  - `TestRebaseLinksGuard` and TC-G19 against the copies: 15 passed; `copies_driver.py`: 177
    passed, both modules loaded from the copies;
  - the reverse apply restored both files to their SHA-256, and the tree fingerprint
    `bbc145bdbe53` was the same before and after.

Hashes for stage 2, round 4:

- the patch `6aecca3ebf71d28886808f2e8e8dd107383fb7a0cd76a02f478b23c75d9f31ba`;
- `rebase_links_next.py` `e42563b75734ac3168c9322789c795838a4d175118fef8880855abc6a40447e1`;
- `slot_links_next.py` `5ab8e620be00f814b68b53111ed7f77bfdb612c19e64a9b5285db1304466daca`.

### G1 — stage 2, round 4 (the whole patch, after K)

Both agents read the tree at fingerprint `7d071e520a02` and quoted it at their start and end, with
the three hashes of "Clusters E and F, entered again after K". The caller recomputed it at each
return: equal. Each used its own probe prefix, `s2r4-code-116.` and `s2r4-sec-116.`, and removed it.

- **Code review: CHANGES REQUESTED.** No BLOCKING item; the code meets R1 to R7.
  - M1: TC-S7d calls `_shell_commands`, so a mutant of `_archive_commands` passes it.
  - M2: no case kills the directory checks of R7.2 and R7.4. A directory renamed out of the root
    and replaced by a link keeps the file's inode; only those checks refuse it. Measured: both
    single-check mutants pass all 15 guard cases and write outside.
  - m1: TC-G19 passes with no swap. m2: the file mode holds every descriptor at once. m3: no case
    pins `O_NONBLOCK` or the closes.
  - m4 to m9: R7.5's directory claim, the open message, the changelogs, a reflow, a docstring and
    `ARCHITECTURE.md`.
- **Security audit: FAIL.** H1 (HIGH, at the base): the file mode writes the `--slot` ARCHIVE text
  over the slot links of any operand, and an operand may be any file. L1 (LOW): the identity check
  looks the path up twice, so three swaps pass it; measured, the outside file is rewritten. L2
  (LOW): a failed write leaves the new text's start over the old text's end. INFO I1 to I9. The
  external scanners are not installed; `deps` and `external` were not run, since each copies
  repository files (D12).

**Operator decisions (2026-10-08), quoted.** D15, on H1: "Fix in TASK 116 (Recommended)". D16, on
L1: "Fix with the fd's own path (Recommended)". D17, the agent's, on L2 and m2: the write truncates
first, and R7.5 states the limit of open files. TASK revision 10 states R8 and the changes of R7;
the scope of D15 starts its own count of audit rounds.

## Mode A — the scope of D15

### Round 1 of D18's count — TASK revision 10: FAIL

The task-reviewer agent, fresh. **FAIL for a procedural reason:** the brief named no tree
fingerprint, so the agent tied its reading to no tree state. The caller's fingerprint was
`05f9d4bc09ba` before and after the round. On content the agent would pass with comments: no
BLOCKING item, one MAJOR.

| # | Severity | Finding | Revision 11 |
| :--- | :--- | :--- | :--- |
| MA1 | MAJOR | the §10.5 cell is 122 characters: a second `cell_width` `WARN` | "in the working directory", 118 |
| m1–m8 | MINOR | eight items of wording, test input and scope, listed below | §12, UC-6, §8, R8.2, D15, D18, R7.4, R7.5, R8.3 |
| n1–n15 | NIT | fifteen items of citation, wording and record, listed below | all but n9 and part of n2 |

- m1 to m8: §12 still said R1.1 runs last; UC-6; the inputs of TC-G25 and TC-G26; the hooks of
  TC-G27. Then markdown files outside `docs/`, which R8.2 now refuses; D15's count; R7.5; and
  reasons written inside two requirements.
- n1 to n15: citations; the `fcntl` import; `str.strip()`; `[0-9]{3,}`; the hook paragraph;
  `_Refusal`; the skips; the three scripts; the lookup copy (n9, not taken); `.git/`; darwin; §13;
  R8's Why; the rejected options.

m6 found that D15's quote grants no new count; under D14's count the round was the third.
**Operator decision D18 (2026-10-08), quoted**: "New count: fix and re-audit (Recommended)". The
scope of D15 starts its own count, and this round is its first.

### Round 2 of D18's count — TASK revision 11: PASS

The same agent, resumed, at fingerprint `71d044ca3d3b`, quoted at its start and end; the caller
recomputed it at the return: equal. Every finding of round 1 is closed but n9 and the optional part
of n2, which were not taken. No BLOCKING or MAJOR item. Revision 12 applies the round's comments,
with no further round:

- r1 (MINOR): §11 no longer says that the written link text holds no space. A rebased link is built
  from the name of an existing path, which `--repo-root` and `--from` choose;
- n-a: the §11 bullet names any link inside the root on the operand's path, also before a `..`;
- n-b: the title says "markdown files under docs/";
- n-c: the base's slot normalisation moves from R8.1 to R8's Why;
- n-d: the darwin measurement is recorded below;
- n-e: TC-G27 is one sentence of input and outcome.

**The darwin measurement of TASK §12 (2026-10-08, Python 3.14 on Darwin 25.6.0).** `fcntl.F_GETPATH`
is 50. The path it gives for a descriptor, by the spelling the file was opened with:

| Opened as | `F_GETPATH` gives |
| :--- | :--- |
| `docs/TASK.md`, from the repository root | `/Users/sergey/dev-projects/agentic-development/docs/TASK.md` |
| `/System/Volumes/Data/Users/sergey/…/docs/TASK.md` | the same `/Users/…` path |
| `/USERS/sergey/…/DOCS/task.md` | the same `/Users/…` path |
| `/tmp` | `/private/tmp` |
| a file through a directory link | the path through the link's target |
| the same descriptor after its directory was renamed | the new path |

`os.getcwd()` gives `/Users/sergey/dev-projects/agentic-development` after a `cd` by the
`/System/Volumes/Data/…` spelling and by the `/USERS/…` spelling; `os.path.realpath` of it is the
same.

## Mode B — the scope of D15

PLAN revision 8 adds cluster L for R8 and the R7 changes of TASK revisions 10 to 12. E, F and G are
entered again after L; G is stage-2 round 5. An earlier run of the round was stopped by the
operator before any verdict, and the round started again.

### Round 1 of D18's count — PLAN revision 8: FAIL

The plan-reviewer agent, fresh, at fingerprint `e45aead33dd3`; the caller recomputed it at the
return: equal. No BLOCKING item.

- **MA1 (MAJOR):** the generator's TC-G29 text held `\n` in a string that is not raw, so the
  patched `tests/test_script_guards.py` did not compile. The line wrote an unused root file; it is
  removed, and both patched test texts compile.
- m1 to m7 (MINOR), each applied:
  - the scratchpad inventory; the two A4 rows that survive by design since K;
  - the TC-S7d mutant, now the base's loop reading `text`;
  - the length rule of L5 for headings; the failed open's message in the changelogs;
  - mutation runs for a change of a case's text in G1; the Coverage row of R5.3, R5.4 and R5.6.
- n1 to n18 (NIT): each applied, but n15 (`fcntl` in TC-G11) and n18 (a relative descriptor path,
  which neither platform gives for a regular file).

PLAN revision 9 and TASK revision 13 apply the round. TASK revision 13 changes only TC-G15's clause,
to the mutant that drops both layers (m2). `basefail_driver.py --copy-only` against K's copies:
TC-G24, TC-G27, TC-G28, TC-G29 and TC-G19 fail; TC-G23, TC-G25, TC-G26 and the earlier cases pass.
`plan_rev8.py` is deleted.

### Round 2 of D18's count — PLAN revision 9: PASS

The same agent, resumed, at fingerprint `1d8cca41fee6`; the caller recomputed it at the return:
equal. Every finding of round 1 is closed but n15 and n18, which were not taken. The schedule,
the chart and the register scan are verified from the outputs in the brief. No BLOCKING or MAJOR
item. PLAN revision 10 and TASK revision 14 apply the round's comments, with no further round:

- r1: the `_approves` docstring moves under `tests/test_committed_settings.py` in E1;
- r2: the inventory note says `plan_rev8.py` was deleted after round 1;
- r3: L cites TASK revisions 10 to 14;
- r4: the paragraph on the test text names L3;
- r5: the driver's docstring; the error mark on rows of the test text; the firmlink row runs on
  darwin only;
- r6: TC-G15's clause holds no reason inside it.

### Cluster L

- **L1.** The generator holds TC-G23 to TC-G29, the three sub-cases of TC-G19, the reasons of
  TC-G17, TC-G18 and TC-G20, and TC-S7d. Both patched test texts compile. `basefail_driver.py
  --copy-only` against K's copies: TC-G24, TC-G27, TC-G28, TC-G29 and TC-G19 fail; TC-G23, TC-G25
  and TC-G26 pass, since K holds their checks.
- **L2.** `fix_round5.py` wrote the two copies and `test_rebase_links.py`. The copies now hash to
  `1776dd00cab7…` and `2e5ffe0ee7e6…`.
- **L3.**
  - all 22 guard cases pass against the copies;
  - `copy_runner.py` 50 passed; `copies_driver.py` 177 passed, both modules loaded from the copies;
  - `test_rebase_links.py` 50 passed at the base, with R8.4;
  - `rebase_links_next.py` differs from its base in eight hunks: the `stat` import, the two
    constants after `KNOWN_SLOTS`, `_refuse_operand`, the helpers of R7, and four in `_main`.
    `slot_links_next.py` differs in two: `_descriptor_path` and `_write_file`.
- **L4.** `mutation_driver.py`: 32 of 32 examined mutants killed, both copies restored, the
  fingerprint `dbb2fae3997d` the same before and after. The two single-layer rows of A4 survive, as
  stated. The platform check of K4 is killed by an error: the mutant fails on `flags | None`.
- **L5.** `docs_l5.py` wrote `ARCHITECTURE.md`, both changelogs and WI-46. No `WARN` on an added
  line, and no line of body text over 100 characters.

### Clusters E and F, entered again after L

- **E1.** The generator wrote the patch: 8 file sections, 2622 lines. **E2.** `git apply --check`
  passes. The patched `skill-safe-commands`, scanned through stdin, carries one `WARN` on an added
  line: the base `cell_width` `WARN` of the command cell. The new reason cell is 118 characters.
- **F1.** Every gate passes: the CI pytest list 526, the tool suite 255, the curated suite 543. The
  advisory archive scan lists the 8 errors of the base. `git status` lists 23 entries, each
  declared. No `WARN` on an added line in the run's documents.
- **F2,** one run of `basefail_driver.py`:
  - with the patch's two test parts applied, 55 cases ran, and exactly the 18 expected ones
    failed. They are TC-G13, TC-G15 to TC-G25, TC-G27 to TC-G29, TC-S6, the table case of TC-S8
    and the denied case of TC-S9. TC-G14 and TC-G26 pass at the base;
  - with the deny list in memory, TC-S6 and TC-S9 pass, 4 cases;
  - with checks that accept everything in memory, TC-S7b and TC-S7c fail, 2 of 2;
  - the 22 guard cases pass against the copies; `copies_driver.py`: 177 passed;
  - the reverse apply restored both files to their SHA-256, and the fingerprint `e2b607cd61d7` was
    the same before and after.

Hashes for stage 2, round 5:

- the patch `95fe88c49a313bd902bce31b961ff4dbf12e6af1dc791b1413536f6b53f748ee`;
- `rebase_links_next.py` `1776dd00cab7da3e078432c7a607bbc26276324a5d7f965bcd1f634797b705a1`;
- `slot_links_next.py` `2e5ffe0ee7e64725a57fff27d2827eceeee8f7f9690bf922e028cdbc4dec6005`.

### G1 — stage 2, round 5 (the whole patch, after L)

Both agents read the tree at fingerprint `299d0daa02b5` and quoted it at their start and end, with
the three hashes of "Clusters E and F, entered again after L". The caller recomputed it at each
return: equal. Each used its own probe prefix, `s2r5-code-116.` and `s2r5-sec-116.`, and removed
it.

- **Code review: APPROVED.** The code meets R1 to R8, and every round-4 finding is closed. Base
  and copy agree on 21 differential fixtures but for the changes of R7.5. MINOR 1 to 5 are test
  gaps:
  - the slug grammar of the archive forms;
  - the order of R7.1;
  - the `realpath` hooks of TC-G27 and TC-G19;
  - the hard-link hook of TC-G26;
  - the order of the two checks of R8.2.

  NITs and two INFO items: the Linux branch first runs in CI, and a non-UTF-8 `--from`.
- **Security audit: INCOMPLETE.** No CRITICAL or HIGH finding.
  - M1 (MEDIUM, at the base): R8 narrows H1, but `--repo-root` is not checked and `--to` may lead
    above it. Their names reach the slot link, so the file mode can still write chosen text into
    a slot link under `docs/` (measured). §11's bound for the written text does not hold.
  - L1 (LOW, at the base): a directory that `init_skill.py` makes can name `--from`.
  - L2 (LOW, the patch): no case pins the normalisation of R8.2.
  - INFO I1 to I10.
  - The scan ran six of eight parts. `deps` copies repository lockfiles, which the brief forbids;
    `external` has no scanners installed (D12).

**Operator decisions (2026-10-08), quoted.** D19, on M1: "Close it here (Recommended)". D20, on
the scan: "Accept the gap (Recommended)": D12 also covers `deps` for this task, which adds no
dependency, and the rule against copies stays.

### Mode A — round 3 of D18's count — TASK revision 15: PASS

TASK revision 15 states R8.6, R8.7 and the round-5 test gaps (D19). The same agent, resumed, at
fingerprint `392ad0d170bf`; the caller recomputed it at the return: equal. R8.6 and R8.7 refuse
no current caller, and each new clause of §8 holds against the copies. No BLOCKING item.

- MA1 (MAJOR): the §10.5 cell said `docs/`, but the inbound mode writes in the whole working tree.
  Revision 16 restores the cell that round 2 audited, so no further round is needed.
- m1 to m4 (MINOR): R8's Why on `--repo-root`; the pair in TC-G28's error, as `repr` gives it;
  R8.7 counted each character on its own. R8.7 is now an allow-list. It also catches a colon, a
  quote, a format character and a non-UTF-8 name.
- n1 to n8 (NIT): each applied. TC-G30 gains a sub-case with a colon in `--from`.

### Mode B — round 3 of D18's count — PLAN revision 11: PASS

The same agent, resumed, at fingerprint `eeea3f22a9d5`; the caller recomputed it at the return:
equal. The PLAN covers TASK revision 16; each of the nine rows of M4 is the mutant that its
clause names, and its case kills it as written. No BLOCKING or MAJOR item. PLAN revision 12 and
TASK revision 17 apply the round's comments, with no further round:

- m1: the Coverage rows of UC-6 and of R5.3, R5.4 and R5.6 name M;
- n1 to n4, n8: M in the paragraphs and the inventory; D21 and R8.1 to R8.5 in the header; the
  count of TC-G30's sub-cases; the revisions cited; the option numbering in WI-46's note;
- n5: M is held in schedule task `116.L`, as stated;
- n6: TC-G30 gains a dry-run sub-case, and M4 its mutant;
- n7: two blank lines before the new constant.

### Cluster M

- **M1.** The generator holds TC-G30, with its eight sub-cases, and the round-5 gaps of TC-G19,
  TC-G22 and TC-G25 to TC-G29. `basefail_driver.py --copy-only` against L's copy: TC-G30 fails,
  and the 22 other guard cases pass.
- **M2.** `fix_round6.py` wrote `rebase_links_next.py` only; it now hashes to `25af394983c3…`.
  `slot_links_next.py` stays at `2e5ffe0ee7e6…`.
- **M3.** The 23 guard cases pass against the copies; `copy_runner.py` 50 passed;
  `copies_driver.py` 177 passed.
- **M4.** `mutation_driver.py`: 42 of 42 examined mutants killed, the ten rows of M4 among them,
  both copies restored. The fingerprint `bac4bf61fc94` was the same before and after. The two
  single-layer rows of A4 survive, as stated.
- **M5.** `docs_m5.py` wrote `ARCHITECTURE.md`, both changelogs and WI-46. No `WARN` on an added
  line, and no line of body text over 100 characters.

### Clusters E and F, entered again after M

- **E1, E2.** The patch: 8 file sections, 2780 lines; `git apply --check` passes. The patched
  `skill-safe-commands` carries one `WARN` on an added line, the base `cell_width` of the command
  cell.
- **F1.** Every gate passes: 526, 255 and 543; the archive scan at the base's 8 errors; 23 status
  entries, each declared; no `WARN` on an added line.
- **F2.** 56 cases ran, and exactly the 19 expected ones failed, TC-G30 among them. The in-memory
  checks hold. The 23 guard cases pass against the copies, and `copies_driver.py` 177. Both files
  were restored, and the fingerprint `ff8ff54b80d0` was the same before and after.

Hashes for stage 2, round 6:

- the patch `120dbd24f07c112ab3789cd68f8e9705bb2664a41c6530d0bfe4ae5f56e117ec`;
- `rebase_links_next.py` `25af394983c3889376af977d7231ba15c20380696454e8bb0bb1d71c4e5222b2`;
- `slot_links_next.py` `2e5ffe0ee7e64725a57fff27d2827eceeee8f7f9690bf922e028cdbc4dec6005`.

### G1 — stage 2, round 6 (the whole patch, after M)

Both agents, resumed, read the tree at fingerprint `8ed86c3f2e16` and quoted it at their start and
end, with the three hashes of "Clusters E and F, entered again after M". The caller recomputed it
at each return: equal. Each used its own probe prefix, `s2r6-code-116.` and `s2r6-sec-116.`, and
removed it.

- **Code review: APPROVED.** R8.6 and R8.7 refuse no legitimate operand or link: 30 link forms and
  a dry run over 390 documents give the same result from base and copy. Every round-5 item is
  closed. MINOR 1 to 4: four mutants survive every suite. They widen the safe set, drop the
  normalisation of R8.6, compare sets of characters, and check `REWRITTEN` records only.
- **Security audit: PASS.** No CRITICAL, HIGH or MEDIUM finding; M1's route and its variants are
  refused. L1 (LOW): a `--from` of safe characters still names a part of the link, and `%` can
  carry anything in percent-encoding. L2 (LOW): a character that the authored link's `..`
  cancels still counts in R8.7's budget. I1: overlapping links spliced one into the other gain a
  character. The scan ran six of eight parts; `deps` and `external` are the gap of D12 and D20.

**Operator decision D22 (2026-10-08), quoted**, on L1, L2 and the four gaps: "Close L1/L2 and the
gaps (Recommended)". TASK revision 18 states the fix round: R8.7 gains a check of path parts and
a check of the whole text, and TC-G30 seven sub-cases. As in fix rounds 1 and 2, G1's rule
governs the round; the counts of Mode A and Mode B under D18 are spent.

### Cluster N

- **N1.** TC-G30 holds the seven new sub-cases of TASK §8, revision 18, and its ambiguous rebase
  runs alone. Against M's copy TC-G30 failed, by the sub-cases of path parts and of the whole
  text; the 22 other guard cases passed.
- **N2.** `fix_round7.py` wrote `rebase_links_next.py` only; it now hashes to `5a9fdf76b771…`.
- **N3.** The 23 guard cases pass against the copies; `copy_runner.py` 50 passed;
  `copies_driver.py` 177 passed.
- **N4.** `mutation_driver.py`: 49 of 49 examined mutants killed, the seven rows of N4 among them,
  both copies restored. The fingerprint `df9822174b28` was the same before and after. The two
  single-layer rows of A4 survive, as stated.
- **N5.** `docs_n5.py` wrote `ARCHITECTURE.md` and both changelogs. No `WARN` on an added line; one
  line of the Russian changelog was reflowed to 100 characters.

### Clusters E and F, entered again after N

- **E1, E2.** The patch: 8 file sections, 2862 lines; `git apply --check` passes; one `WARN` on an
  added line of `skill-safe-commands`, the base `cell_width` of the command cell.
- **F1.** Every gate passes; the curated suite 543; the archive scan at the base's 8 errors; 23
  status entries, each declared; no `WARN` on an added line.
- **F2.** 56 cases ran, and exactly the 19 expected ones failed. The in-memory checks hold; the 23
  guard cases pass against the copies, and `copies_driver.py` 177. Both files were restored, and
  the fingerprint `dcef7f7023f9` was the same before and after.

Hashes for stage 2, round 7:

- the patch `7b4cc642e5245fa88ee32bb2fe95163cc2a3d0e2f6fec74a0d5a878336beccd2`;
- `rebase_links_next.py` `5a9fdf76b771ab6fafdea19205c53d58542169dcaa0350a32b11db9c2c90cf88`;
- `slot_links_next.py` `2e5ffe0ee7e64725a57fff27d2827eceeee8f7f9690bf922e028cdbc4dec6005`.

### G1 — stage 2, round 7 (the whole patch, after N)

Both agents, resumed, read the tree at fingerprint `2e36863a0f21` and quoted it at their start and
end, with the three hashes of "Clusters E and F, entered again after N". The caller recomputed it
at each return: equal. Each used its own probe prefix, `s2r7-code-116.` and `s2r7-sec-116.`, and
removed it.

- **Code review: APPROVED.** Neither new check refuses a legitimate archive rewrite. A 780-run
  replay and the 30-link battery agree with the base. Each TASK-named mutant is killed. MINOR 1:
  the check of path parts on an ambiguous rebase is not pinned. MINOR 2: the documents do not
  state the refused moves. NITs: dry runs of the two new checks, and the docstrings.
- **Security audit: PASS.** Round 6's L1, L2 and I1 are refused, and the corpus replay refuses 0
  of 280 rewrites. L1 (LOW): the slug of a slot archive is chosen text. I1: the check of path
  parts is a set test, so the author's parts can be reordered. I2 (base): a splice at one offset.

**Operator decision D23 (2026-10-08), quoted**: "Tests and docs, file the rest (Recommended)".
TASK revision 19 and PLAN revision 14 state cluster O.

### Cluster O, and E and F entered again

- **O1.** TC-G30 gains the ambiguous rebase with `--from docs/plain-words` and the two dry runs.
  Against N's copy the 23 guard cases pass, since the code is unchanged.
- **O4.** `mutation_driver.py`: 52 of 52 examined mutants killed, the three rows of O4 among them,
  both copies restored to `5a9fdf76b771…` and `2e5ffe0ee7e6…`. The fingerprint `ee13318ae519` was
  the same before and after.
- **O5.** Both changelogs and `ARCHITECTURE.md` state the check of the whole text and the refused
  moves. WI-47 is filed with its index line. No `WARN` on an added line.
- **E1, E2.** The patch: 8 file sections, 2868 lines; `git apply --check` passes; the one base
  `cell_width` `WARN` of the command cell.
- **F1.** Every gate passes; the curated suite 543; the archive scan at the base's 8 errors; 24
  status entries, WI-47 among them, each declared.
- **F2.** 56 cases ran, and exactly the 19 expected ones failed; the in-memory checks hold; both
  files restored, and the fingerprint `c28164229d9b` the same before and after.

Hashes for the re-check of O: the patch
`7544f178693c76990c993f82b40d81443742e844f4730fa4cf16df5b4f1f1db6`; the two copies as above.

### G1 — the re-check of cluster O

Both agents, resumed, at fingerprint `a5cac5e7c03f`, quoted at their start and end; the caller
recomputed it at each return: equal. Each re-checked the changed parts only.

- **Code review: APPROVED.** Round 7's MINOR 1 and 2 and its two dry-run NITs are closed; WI-47's
  three measurements reproduce. NIT: one line of D23 was 109 characters; it is reflowed.
- **Security audit: PASS.** The non-test sections give the hashes of round 7, and the changed test
  text weakens no guard. LOW-1: the documents overclaimed the check of path parts and named no
  residual. INFO-1: the splice is wider, also through an `href=` value. INFO-2: a move is refused
  when the document links to a file under `--from`. INFO-3: §11 lacked "but for the splice".
  TASK revision 20, both changelogs, `ARCHITECTURE.md` and WI-47 apply each, as written, with no
  change of the patch.

G1 is passed.

## Stage 3 (§4.5, H1)

**§4.5.** `check_positional_refs.py --targets-changed`, without `--fix` and then with it: 9 errors
and no `REFERENT_MOVED`. The 9 predate the change: 8 in old changelog entries citing files the
repository never held, and one in `review-095`, whose cited file this run did not touch. No repair
touched a file; the fingerprint `b9747db815de` was the same before and after.

**The three SHA-256, equal to the values that G's reviewers quoted:**

- the patch `7544f178693c76990c993f82b40d81443742e844f4730fa4cf16df5b4f1f1db6`;
- `rebase_links_next.py` `5a9fdf76b771ab6fafdea19205c53d58542169dcaa0350a32b11db9c2c90cf88`;
- `slot_links_next.py` `2e5ffe0ee7e64725a57fff27d2827eceeee8f7f9690bf922e028cdbc4dec6005`.

**Every file the patch touches, before the apply** (SHA-256, mode):

- `.agent/tools/rebase_links.py` `094304333b45dd06a9ba0f686332b14b8e6fd2ec8fa6ff366fb6bc3392799787` `644`
- `.agent/tools/rebase_links_next.py` `5a9fdf76b771ab6fafdea19205c53d58542169dcaa0350a32b11db9c2c90cf88` `644`
- `.agent/tools/slot_links.py` `e729c176870fe15e60d66a71ee438fb57ae09cda95cb98e9d0700ba41b0ea339` `644`
- `.agent/tools/slot_links_next.py` `2e5ffe0ee7e64725a57fff27d2827eceeee8f7f9690bf922e028cdbc4dec6005` `644`
- `.claude/settings.json` `e782afb6955297d7a94d7ae8d0f70485ff4f0dfea416ffa10077602eb6403c03` `644`
- `tests/test_committed_settings.py` `4017ecaf765253f5498ac69bbb605ca50b02837cefc0da53d2d3b5956d531d5a` `644`
- `tests/test_script_guards.py` `b9eb54da5e60818a41ed91a549c2d2b522af2c878a0227bbb8210aec79ca7c9d` `644`
- `.agent/skills/skill-safe-commands/SKILL.md` `fda598a62c609e7cc425f88acd6269d9213d1718ce1c75ef83c41cddb5b7adff` `644`

**The patch text:**

~~~~diff
diff --git a/.agent/tools/rebase_links.py b/.agent/tools/rebase_links.py
--- a/.agent/tools/rebase_links.py
+++ b/.agent/tools/rebase_links.py
@@ -83,6 +83,7 @@
     sys.pycache_prefix = os.path.join(os.devnull, "rebase-links-pycache")
 
 import re  # noqa: E402
+import stat  # noqa: E402
 from typing import NamedTuple  # noqa: E402
 
 #: Schemes and forms that are never document-relative.
@@ -153,6 +154,16 @@
 #: link checker because it resolves. So the link is left exactly as authored and
 #: reported as UNMAPPED_SLOT.
 KNOWN_SLOTS = ("docs/TASK.md", "docs/PLAN.md")
+#: The grammar of `archive_move.SLUG`, held here so the file mode loads no sibling (TASK 115
+#: R1.2, TASK 116 R8.3). TC-G28 pins the two equal.
+_SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
+#: TASK 116 R8.1: the slots that `--slot` takes, each with the form of the archive it names.
+_SLOT_ARCHIVES = {
+    "docs/TASK.md": ("docs/tasks/task-<ID>-<slug>.md",
+                     re.compile(rf"docs/tasks/task-[0-9]{{3,}}-{_SLUG}\.md")),
+    "docs/PLAN.md": ("docs/plans/plan-<ID>-<slug>.md",
+                     re.compile(rf"docs/plans/plan-[0-9]{{3,}}-{_SLUG}\.md")),
+}
 
 
 def _mask(text: str) -> str:
@@ -391,14 +402,56 @@
         probe = parent
     return False
 
+
+#: TASK 116 R8.7: the characters a rewrite may add to a link; any other is counted.
+_LINK_SAFE = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._~/%-")
+
+
+def _adds_characters(authored, new):
+    """True when `new` holds a character outside `_LINK_SAFE` more often than `authored` does.
+
+    Each character is counted on its own (TASK 116 R8.7). A link to a file named with a space,
+    authored as `<a b.md>`, keeps its space when it is rebased.
+    """
+    def counts(text):
+        found = {}
+        for ch in text:
+            if ch not in _LINK_SAFE:
+                found[ch] = found.get(ch, 0) + 1
+        return found
+    before = counts(authored)
+    return any(n > before.get(ch, 0) for ch, n in counts(new).items())
+
+
+def _adds_parts(record):
+    """True when a part of the new target's path is not one its author wrote (TASK 116 R8.7).
+
+    A part, between `/`, other than `.` and `..`, must be a part of the authored target's path,
+    or, for a slot link, of the archive it names. A rewrite may drop parts and add `..`.
+    """
+    def parts(target):
+        if target.startswith("<") and target.endswith(">"):
+            target = target[1:-1]
+        return set(_split_fragment(target)[0].split("/")) - {"", ".", ".."}
+    known = parts(record.authored)
+    if record.action == "SLOT_RESOLVED":
+        known |= parts(record.denotes_old)
+    return not parts(record.new_target) <= known
+
+
 def _refuse_operand(path):
-    """Why `_main` refuses to rewrite this file operand, or None (TASK 112 R4.1).
+    """Why `_main` refuses to rewrite this file operand, or None (TASK 112 R4.1, TASK 116 R1.1).
 
     `Bash(python3 .agent/tools/rebase_links.py *)` approves any operand, and the rewrite writes the
     file in place. A file outside the working directory, by its absolute path normalised without
     resolving links, is refused; so is a file under `.git/` (`_under_git`), a symbolic link, and a
-    file with a second hard link, which would write through to another name. `rebase_file()` keeps
-    no such guard: `archive_protocol.py` calls it with temporary paths.
+    file with a second hard link, which would write through to another name. Then a file whose
+    directory resolves outside the working directory, both by real path, is refused: a directory
+    link would carry the write there. The directory is the operand's own, resolved as the kernel
+    resolves it, each link before the `..` that follows it. Last, an operand that does not lie
+    under `docs/`, and then a name that does not end in `.md`, is refused (TASK 116 R8.2): only
+    a markdown file under `docs/` is this script's to rewrite. `rebase_file()` keeps no such
+    guard: `archive_protocol.py` calls it with temporary paths.
     """
     cwd = os.getcwd()
     absolute = os.path.normpath(os.path.join(cwd, path))
@@ -410,7 +463,110 @@
         return "is a symbolic link"
     if os.path.exists(path) and os.lstat(path).st_nlink != 1:
         return "has a second hard link"
+    real_cwd = os.path.realpath(cwd)
+    directory = os.path.realpath(os.path.dirname(os.path.join(cwd, path)))
+    if os.path.commonpath([directory, real_cwd]) != real_cwd:
+        return "its directory resolves outside the working directory"
+    if os.path.relpath(absolute, cwd).split(os.sep)[0] != "docs":
+        return "does not lie under docs/"
+    if not path.endswith(".md"):
+        return "is not a markdown file"
     return None
+
+
+class _Unsafe(Exception):
+    """An operand that the file mode refuses to read or to write (TASK 116 R7)."""
+
+
+def _check_descriptor(fd, path, cwd):
+    """The `fstat` of `fd`, if it is the regular file at `path`'s real path (TASK 116 R7.2).
+
+    The real path is `path` joined to `cwd` and resolved as the kernel resolves it. The directory
+    of the descriptor's own path (`_descriptor_path`), or of the real path where the platform
+    gives none, lies inside `cwd` by real path. Any other descriptor raises `_Unsafe` with its
+    reason.
+    """
+    st = os.fstat(fd)
+    if not stat.S_ISREG(st.st_mode):
+        raise _Unsafe("is not a regular file")
+    if st.st_nlink != 1:
+        raise _Unsafe(f"has {st.st_nlink} hard links")
+    try:
+        real = os.path.realpath(os.path.join(cwd, path))
+        now = os.stat(real)
+    except (OSError, ValueError):
+        raise _Unsafe("is not the file at its real path") from None
+    if (now.st_dev, now.st_ino) != (st.st_dev, st.st_ino):
+        raise _Unsafe("is not the file at its real path")
+    try:
+        where = _descriptor_path(fd) or real
+    except OSError:
+        raise _Unsafe("is not the file at its real path") from None
+    real_cwd = os.path.realpath(cwd)
+    if os.path.commonpath([os.path.dirname(where), real_cwd]) != real_cwd:
+        raise _Unsafe("its directory resolves outside the working directory")
+    return st
+
+
+def _descriptor_path(fd):
+    """The path the kernel holds for `fd`, or None where the platform gives none (TASK 116 R7.2).
+
+    `fcntl.F_GETPATH` gives it on darwin, and the link `/proc/self/fd/<fd>` on Linux. It is one
+    lookup, so no swap of a directory between two lookups by name can change it, as one can
+    between `realpath` and `stat`. A failed lookup raises `OSError`.
+    """
+    try:
+        import fcntl
+    except ImportError:
+        fcntl = None
+    if hasattr(fcntl, "F_GETPATH"):
+        return os.fsdecode(fcntl.fcntl(fd, fcntl.F_GETPATH, bytes(1024)).split(b"\0", 1)[0])
+    if os.path.isdir("/proc/self/fd"):
+        return os.readlink(f"/proc/self/fd/{fd}")
+    return None
+
+
+def _open_checked(path, cwd, flags):
+    """`(descriptor, fstat)` of `path` opened with `flags` and no link followed (TASK 116 R7.1)."""
+    nofollow = getattr(os, "O_NOFOLLOW", None)
+    if nofollow is None:
+        raise _Unsafe("this platform has no O_NOFOLLOW")
+    try:
+        fd = os.open(path, flags | nofollow | getattr(os, "O_NONBLOCK", 0))
+    except OSError as exc:
+        raise _Unsafe(f"cannot open it: {exc.strerror or exc}") from None
+    try:
+        return fd, _check_descriptor(fd, path, cwd)
+    except BaseException:
+        os.close(fd)
+        raise
+
+
+def _read_descriptor(fd):
+    """Every byte of the file open on `fd`, from its start."""
+    chunks = []
+    while chunk := os.read(fd, 1 << 16):
+        chunks.append(chunk)
+    return b"".join(chunks)
+
+
+def _write_checked(path, cwd, read_st, data):
+    """Write `data` over `path` through a second descriptor of the inode read (TASK 116 R7.3).
+
+    The file is truncated first, as the base's `open(path, "w")` truncates it, so a write that
+    fails leaves a prefix of `data`.
+    """
+    fd, st = _open_checked(path, cwd, os.O_WRONLY)
+    try:
+        if (st.st_dev, st.st_ino) != (read_st.st_dev, read_st.st_ino):
+            raise _Unsafe("changed during the run")
+        os.ftruncate(fd, 0)
+        view, written = memoryview(data), 0
+        while written < len(data):
+            written += os.write(fd, view[written:])
+        os.fsync(fd)
+    finally:
+        os.close(fd)
 
 
 def _load_siblings():
@@ -454,15 +610,19 @@
                "[--plan docs/plans/plan-<ID>-<slug>.md] [--since <rev>] [--dry-run] [--json] "
                "re-targets the slot links an archived task wrote in other documents "
                "(TASK 115, skill-archive-task Step 8).")
-    ap.add_argument("files", nargs="+", help="moved markdown file(s)")
+    ap.add_argument("files", nargs="+",
+                    help="moved markdown file(s) under docs/; any other operand is refused")
     ap.add_argument("--from", dest="from_dir", required=True,
                     help="directory the file used to live in (repo-relative)")
     ap.add_argument("--to", dest="to_dir", required=True,
                     help="directory it lives in now (repo-relative)")
-    ap.add_argument("--repo-root", default=".")
+    ap.add_argument("--repo-root", default=".",
+                    help="the working directory, the only root the file mode takes")
     ap.add_argument("--slot", action="append", default=[], metavar="SLOT=ARCHIVE",
                     help="a mutable slot and the archive identity it held, e.g. "
-                         "docs/PLAN.md=docs/plans/plan-096-x.md. Repeatable. "
+                         "docs/PLAN.md=docs/plans/plan-096-x.md. Repeatable. SLOT is "
+                         "docs/TASK.md, with ARCHIVE docs/tasks/task-<ID>-<slug>.md, or "
+                         "docs/PLAN.md, with ARCHIVE docs/plans/plan-<ID>-<slug>.md. "
                          "Resolved before any filesystem probe, so it still "
                          "works once the slot file has been moved away.")
     ap.add_argument("--slot-must-exist", action="store_true",
@@ -475,6 +635,18 @@
     ap.add_argument("--json", action="store_true")
     args = ap.parse_args(argv)
 
+    # TASK 116 R8.6: a rewritten link is built from these paths, so each stays in the tree.
+    if os.path.realpath(args.repo_root) != os.path.realpath(os.getcwd()):
+        problem = "--repo-root is not the working directory"
+    else:
+        problem = next((f"{name} does not lie inside the working directory"
+                        for name, value in (("--from", args.from_dir), ("--to", args.to_dir))
+                        if os.path.isabs(value)
+                        or os.path.normpath(value).split(os.sep)[0] == ".."), None)
+    if problem:
+        print(json.dumps({"ok": False, "error": problem}), file=sys.stderr)
+        return 2
+
     slot_map = {}
     for pair in args.slot:
         if "=" not in pair:
@@ -482,8 +654,30 @@
                               "error": f"--slot expects SLOT=ARCHIVE, got {pair!r}"}),
                   file=sys.stderr)
             return 2
-        slot, archive = pair.split("=", 1)
-        slot_map[slot.strip()] = archive.strip()
+        slot, archive = (part.strip() for part in pair.split("=", 1))
+        # TASK 116 R8.1: the allow rule approves any argument, and ARCHIVE is written as a link.
+        known = _SLOT_ARCHIVES.get(slot)
+        if known is None:
+            problem = "its slot is not docs/TASK.md or docs/PLAN.md"
+        elif not known[1].fullmatch(archive):
+            problem = f"its archive is not {known[0]}"
+        else:
+            slot_map[slot] = archive
+            continue
+        print(json.dumps({"ok": False, "error": f"--slot {pair!r}: {problem}"}), file=sys.stderr)
+        return 2
+
+    opened = []
+    try:
+        return _file_mode(args, slot_map, opened)
+    finally:
+        for _path, fd, _st in opened:
+            os.close(fd)
+
+
+def _file_mode(args, slot_map, opened):
+    """The file mode of `_main`; each descriptor it opens is appended to `opened` (TASK 116 R7)."""
+    import json
 
     for path in args.files:
         reason = _refuse_operand(path)
@@ -491,13 +685,45 @@
             print(json.dumps({"ok": False, "error": f"{path}: {reason}"}), file=sys.stderr)
             return 2
 
-    report, warned, failed, pending = [], False, False, []
+    # TASK 116 R7.1: every operand is open and checked before any of them is read.
+    cwd = os.getcwd()
     for path in args.files:
         try:
-            changed, records = rebase_file(path, args.from_dir, args.to_dir,
-                                           args.repo_root, args.dry_run,
-                                           slot_map)
-        except OSError as exc:
+            fd, st = _open_checked(path, cwd, os.O_RDONLY)
+        except _Unsafe as exc:
+            print(json.dumps({"ok": False, "error": f"{path}: {exc}"}), file=sys.stderr)
+            return 2
+        opened.append((path, fd, st))
+
+    report, warned, failed, pending = [], False, False, []
+    for path, fd, st in opened:
+        try:
+            text = _read_descriptor(fd).decode("utf-8")
+            new_text, records = rebase_document_links(text, args.from_dir, args.to_dir,
+                                                      args.repo_root, slot_map)
+            changed = new_text != text
+            # TASK 116 R8.7, in a dry run too: a rewrite adds no character that ends a link.
+            added = [r.line for r in records if r.action in _WROTE
+                     and _adds_characters(r.authored, r.new_target)]
+            if added:
+                print(json.dumps({"ok": False, "error": f"{path}:{added[0]}: a rewritten link "
+                                  "holds text that its authored link does not"}),
+                      file=sys.stderr)
+                return 2
+            parts = [r.line for r in records if r.action in _WROTE and _adds_parts(r)]
+            if parts:
+                print(json.dumps({"ok": False, "error": f"{path}:{parts[0]}: a rewritten link "
+                                  "holds a path part that its authored link does not"}),
+                      file=sys.stderr)
+                return 2
+            # Overlapping links are spliced one into the other: the text gains no character either.
+            if _adds_characters(text, new_text):
+                print(json.dumps({"ok": False, "error": f"{path}: the rewritten text holds a "
+                                  "character that the text did not"}), file=sys.stderr)
+                return 2
+            if changed and not args.dry_run:
+                _write_checked(path, cwd, st, new_text.encode("utf-8"))
+        except (OSError, _Unsafe) as exc:
             print(json.dumps({"ok": False, "error": f"{path}: {exc}"}),
                   file=sys.stderr)
             return 2
diff --git a/.agent/tools/rebase_links_next.py b/.agent/tools/rebase_links_next.py
deleted file mode 100644
--- a/.agent/tools/rebase_links_next.py
+++ /dev/null
@@ -1,796 +0,0 @@
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
-import stat  # noqa: E402
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
-#: The grammar of `archive_move.SLUG`, held here so the file mode loads no sibling (TASK 115
-#: R1.2, TASK 116 R8.3). TC-G28 pins the two equal.
-_SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
-#: TASK 116 R8.1: the slots that `--slot` takes, each with the form of the archive it names.
-_SLOT_ARCHIVES = {
-    "docs/TASK.md": ("docs/tasks/task-<ID>-<slug>.md",
-                     re.compile(rf"docs/tasks/task-[0-9]{{3,}}-{_SLUG}\.md")),
-    "docs/PLAN.md": ("docs/plans/plan-<ID>-<slug>.md",
-                     re.compile(rf"docs/plans/plan-[0-9]{{3,}}-{_SLUG}\.md")),
-}
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
-
-#: TASK 116 R8.7: the characters a rewrite may add to a link; any other is counted.
-_LINK_SAFE = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._~/%-")
-
-
-def _adds_characters(authored, new):
-    """True when `new` holds a character outside `_LINK_SAFE` more often than `authored` does.
-
-    Each character is counted on its own (TASK 116 R8.7). A link to a file named with a space,
-    authored as `<a b.md>`, keeps its space when it is rebased.
-    """
-    def counts(text):
-        found = {}
-        for ch in text:
-            if ch not in _LINK_SAFE:
-                found[ch] = found.get(ch, 0) + 1
-        return found
-    before = counts(authored)
-    return any(n > before.get(ch, 0) for ch, n in counts(new).items())
-
-
-def _adds_parts(record):
-    """True when a part of the new target's path is not one its author wrote (TASK 116 R8.7).
-
-    A part, between `/`, other than `.` and `..`, must be a part of the authored target's path,
-    or, for a slot link, of the archive it names. A rewrite may drop parts and add `..`.
-    """
-    def parts(target):
-        if target.startswith("<") and target.endswith(">"):
-            target = target[1:-1]
-        return set(_split_fragment(target)[0].split("/")) - {"", ".", ".."}
-    known = parts(record.authored)
-    if record.action == "SLOT_RESOLVED":
-        known |= parts(record.denotes_old)
-    return not parts(record.new_target) <= known
-
-
-def _refuse_operand(path):
-    """Why `_main` refuses to rewrite this file operand, or None (TASK 112 R4.1, TASK 116 R1.1).
-
-    `Bash(python3 .agent/tools/rebase_links.py *)` approves any operand, and the rewrite writes the
-    file in place. A file outside the working directory, by its absolute path normalised without
-    resolving links, is refused; so is a file under `.git/` (`_under_git`), a symbolic link, and a
-    file with a second hard link, which would write through to another name. Then a file whose
-    directory resolves outside the working directory, both by real path, is refused: a directory
-    link would carry the write there. The directory is the operand's own, resolved as the kernel
-    resolves it, each link before the `..` that follows it. Last, an operand that does not lie
-    under `docs/`, and then a name that does not end in `.md`, is refused (TASK 116 R8.2): only
-    a markdown file under `docs/` is this script's to rewrite. `rebase_file()` keeps no such
-    guard: `archive_protocol.py` calls it with temporary paths.
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
-    real_cwd = os.path.realpath(cwd)
-    directory = os.path.realpath(os.path.dirname(os.path.join(cwd, path)))
-    if os.path.commonpath([directory, real_cwd]) != real_cwd:
-        return "its directory resolves outside the working directory"
-    if os.path.relpath(absolute, cwd).split(os.sep)[0] != "docs":
-        return "does not lie under docs/"
-    if not path.endswith(".md"):
-        return "is not a markdown file"
-    return None
-
-
-class _Unsafe(Exception):
-    """An operand that the file mode refuses to read or to write (TASK 116 R7)."""
-
-
-def _check_descriptor(fd, path, cwd):
-    """The `fstat` of `fd`, if it is the regular file at `path`'s real path (TASK 116 R7.2).
-
-    The real path is `path` joined to `cwd` and resolved as the kernel resolves it. The directory
-    of the descriptor's own path (`_descriptor_path`), or of the real path where the platform
-    gives none, lies inside `cwd` by real path. Any other descriptor raises `_Unsafe` with its
-    reason.
-    """
-    st = os.fstat(fd)
-    if not stat.S_ISREG(st.st_mode):
-        raise _Unsafe("is not a regular file")
-    if st.st_nlink != 1:
-        raise _Unsafe(f"has {st.st_nlink} hard links")
-    try:
-        real = os.path.realpath(os.path.join(cwd, path))
-        now = os.stat(real)
-    except (OSError, ValueError):
-        raise _Unsafe("is not the file at its real path") from None
-    if (now.st_dev, now.st_ino) != (st.st_dev, st.st_ino):
-        raise _Unsafe("is not the file at its real path")
-    try:
-        where = _descriptor_path(fd) or real
-    except OSError:
-        raise _Unsafe("is not the file at its real path") from None
-    real_cwd = os.path.realpath(cwd)
-    if os.path.commonpath([os.path.dirname(where), real_cwd]) != real_cwd:
-        raise _Unsafe("its directory resolves outside the working directory")
-    return st
-
-
-def _descriptor_path(fd):
-    """The path the kernel holds for `fd`, or None where the platform gives none (TASK 116 R7.2).
-
-    `fcntl.F_GETPATH` gives it on darwin, and the link `/proc/self/fd/<fd>` on Linux. It is one
-    lookup, so no swap of a directory between two lookups by name can change it, as one can
-    between `realpath` and `stat`. A failed lookup raises `OSError`.
-    """
-    try:
-        import fcntl
-    except ImportError:
-        fcntl = None
-    if hasattr(fcntl, "F_GETPATH"):
-        return os.fsdecode(fcntl.fcntl(fd, fcntl.F_GETPATH, bytes(1024)).split(b"\0", 1)[0])
-    if os.path.isdir("/proc/self/fd"):
-        return os.readlink(f"/proc/self/fd/{fd}")
-    return None
-
-
-def _open_checked(path, cwd, flags):
-    """`(descriptor, fstat)` of `path` opened with `flags` and no link followed (TASK 116 R7.1)."""
-    nofollow = getattr(os, "O_NOFOLLOW", None)
-    if nofollow is None:
-        raise _Unsafe("this platform has no O_NOFOLLOW")
-    try:
-        fd = os.open(path, flags | nofollow | getattr(os, "O_NONBLOCK", 0))
-    except OSError as exc:
-        raise _Unsafe(f"cannot open it: {exc.strerror or exc}") from None
-    try:
-        return fd, _check_descriptor(fd, path, cwd)
-    except BaseException:
-        os.close(fd)
-        raise
-
-
-def _read_descriptor(fd):
-    """Every byte of the file open on `fd`, from its start."""
-    chunks = []
-    while chunk := os.read(fd, 1 << 16):
-        chunks.append(chunk)
-    return b"".join(chunks)
-
-
-def _write_checked(path, cwd, read_st, data):
-    """Write `data` over `path` through a second descriptor of the inode read (TASK 116 R7.3).
-
-    The file is truncated first, as the base's `open(path, "w")` truncates it, so a write that
-    fails leaves a prefix of `data`.
-    """
-    fd, st = _open_checked(path, cwd, os.O_WRONLY)
-    try:
-        if (st.st_dev, st.st_ino) != (read_st.st_dev, read_st.st_ino):
-            raise _Unsafe("changed during the run")
-        os.ftruncate(fd, 0)
-        view, written = memoryview(data), 0
-        while written < len(data):
-            written += os.write(fd, view[written:])
-        os.fsync(fd)
-    finally:
-        os.close(fd)
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
-    ap.add_argument("files", nargs="+",
-                    help="moved markdown file(s) under docs/; any other operand is refused")
-    ap.add_argument("--from", dest="from_dir", required=True,
-                    help="directory the file used to live in (repo-relative)")
-    ap.add_argument("--to", dest="to_dir", required=True,
-                    help="directory it lives in now (repo-relative)")
-    ap.add_argument("--repo-root", default=".",
-                    help="the working directory, the only root the file mode takes")
-    ap.add_argument("--slot", action="append", default=[], metavar="SLOT=ARCHIVE",
-                    help="a mutable slot and the archive identity it held, e.g. "
-                         "docs/PLAN.md=docs/plans/plan-096-x.md. Repeatable. SLOT is "
-                         "docs/TASK.md, with ARCHIVE docs/tasks/task-<ID>-<slug>.md, or "
-                         "docs/PLAN.md, with ARCHIVE docs/plans/plan-<ID>-<slug>.md. "
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
-    # TASK 116 R8.6: a rewritten link is built from these paths, so each stays in the tree.
-    if os.path.realpath(args.repo_root) != os.path.realpath(os.getcwd()):
-        problem = "--repo-root is not the working directory"
-    else:
-        problem = next((f"{name} does not lie inside the working directory"
-                        for name, value in (("--from", args.from_dir), ("--to", args.to_dir))
-                        if os.path.isabs(value)
-                        or os.path.normpath(value).split(os.sep)[0] == ".."), None)
-    if problem:
-        print(json.dumps({"ok": False, "error": problem}), file=sys.stderr)
-        return 2
-
-    slot_map = {}
-    for pair in args.slot:
-        if "=" not in pair:
-            print(json.dumps({"ok": False,
-                              "error": f"--slot expects SLOT=ARCHIVE, got {pair!r}"}),
-                  file=sys.stderr)
-            return 2
-        slot, archive = (part.strip() for part in pair.split("=", 1))
-        # TASK 116 R8.1: the allow rule approves any argument, and ARCHIVE is written as a link.
-        known = _SLOT_ARCHIVES.get(slot)
-        if known is None:
-            problem = "its slot is not docs/TASK.md or docs/PLAN.md"
-        elif not known[1].fullmatch(archive):
-            problem = f"its archive is not {known[0]}"
-        else:
-            slot_map[slot] = archive
-            continue
-        print(json.dumps({"ok": False, "error": f"--slot {pair!r}: {problem}"}), file=sys.stderr)
-        return 2
-
-    opened = []
-    try:
-        return _file_mode(args, slot_map, opened)
-    finally:
-        for _path, fd, _st in opened:
-            os.close(fd)
-
-
-def _file_mode(args, slot_map, opened):
-    """The file mode of `_main`; each descriptor it opens is appended to `opened` (TASK 116 R7)."""
-    import json
-
-    for path in args.files:
-        reason = _refuse_operand(path)
-        if reason:
-            print(json.dumps({"ok": False, "error": f"{path}: {reason}"}), file=sys.stderr)
-            return 2
-
-    # TASK 116 R7.1: every operand is open and checked before any of them is read.
-    cwd = os.getcwd()
-    for path in args.files:
-        try:
-            fd, st = _open_checked(path, cwd, os.O_RDONLY)
-        except _Unsafe as exc:
-            print(json.dumps({"ok": False, "error": f"{path}: {exc}"}), file=sys.stderr)
-            return 2
-        opened.append((path, fd, st))
-
-    report, warned, failed, pending = [], False, False, []
-    for path, fd, st in opened:
-        try:
-            text = _read_descriptor(fd).decode("utf-8")
-            new_text, records = rebase_document_links(text, args.from_dir, args.to_dir,
-                                                      args.repo_root, slot_map)
-            changed = new_text != text
-            # TASK 116 R8.7, in a dry run too: a rewrite adds no character that ends a link.
-            added = [r.line for r in records if r.action in _WROTE
-                     and _adds_characters(r.authored, r.new_target)]
-            if added:
-                print(json.dumps({"ok": False, "error": f"{path}:{added[0]}: a rewritten link "
-                                  "holds text that its authored link does not"}),
-                      file=sys.stderr)
-                return 2
-            parts = [r.line for r in records if r.action in _WROTE and _adds_parts(r)]
-            if parts:
-                print(json.dumps({"ok": False, "error": f"{path}:{parts[0]}: a rewritten link "
-                                  "holds a path part that its authored link does not"}),
-                      file=sys.stderr)
-                return 2
-            # Overlapping links are spliced one into the other: the text gains no character either.
-            if _adds_characters(text, new_text):
-                print(json.dumps({"ok": False, "error": f"{path}: the rewritten text holds a "
-                                  "character that the text did not"}), file=sys.stderr)
-                return 2
-            if changed and not args.dry_run:
-                _write_checked(path, cwd, st, new_text.encode("utf-8"))
-        except (OSError, _Unsafe) as exc:
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
diff --git a/.agent/tools/slot_links.py b/.agent/tools/slot_links.py
--- a/.agent/tools/slot_links.py
+++ b/.agent/tools/slot_links.py
@@ -321,11 +321,33 @@
     return os.path.isfile(os.path.join(root, resolved))
 
 
+def _descriptor_path(fd):
+    """The path the kernel holds for `fd`, or None where the platform gives none (TASK 116 R7.4).
+
+    `fcntl.F_GETPATH` gives it on darwin, and the link `/proc/self/fd/<fd>` on Linux. It is one
+    lookup, so no swap of a directory between two lookups by name can change it, as one can
+    between `realpath` and `stat`. A failed lookup raises `OSError`. The same lookup as
+    `rebase_links._descriptor_path`, held here since a copy of one module may run beside
+    the base of the other.
+    """
+    try:
+        import fcntl
+    except ImportError:
+        fcntl = None
+    if hasattr(fcntl, "F_GETPATH"):
+        return os.fsdecode(fcntl.fcntl(fd, fcntl.F_GETPATH, bytes(1024)).split(b"\0", 1)[0])
+    if os.path.isdir("/proc/self/fd"):
+        return os.readlink(f"/proc/self/fd/{fd}")
+    return None
+
+
 def _write_file(root, rel, original, ident, data, dry_run=False):
     """Write `data` over `rel` through a descriptor that follows no link (R5.2, R5.3).
 
-    Returns None when the file was written, or, in a dry run, would be; else a `_Refusal`. A dry
-    run makes every check of a real run and writes nothing (R5.4).
+    After the open, the descriptor must be the file at the real path of `rel`, and the directory
+    of its own path must lie inside `root` (TASK 116 R7.4). Returns None when the file was
+    written, or, in a dry run, would be; else a `_Refusal`. A dry run makes every check of a real
+    run and writes nothing (R5.4).
     """
     path = os.path.join(root, rel)
     real_root = os.path.realpath(root)
@@ -345,6 +367,17 @@
             return _Refusal("is not a regular file", False)
         if st.st_nlink != 1:
             return _Refusal(f"has {st.st_nlink} hard links", False)
+        # TASK 116 R7.4: the descriptor is the file at the real path of `rel`, inside the root.
+        try:
+            real = os.path.realpath(path)
+            now = os.stat(real)
+            where = _descriptor_path(fd) or real
+        except (OSError, ValueError):
+            return _Refusal("is not the file at its real path", False)
+        if (now.st_dev, now.st_ino) != (st.st_dev, st.st_ino):
+            return _Refusal("is not the file at its real path", False)
+        if os.path.commonpath([os.path.dirname(where), real_root]) != real_root:
+            return _Refusal("its directory resolves outside the working directory", False)
         if (st.st_dev, st.st_ino) != ident:
             return _Refusal("changed during the run", False)
         chunks, size = [], 0
diff --git a/.agent/tools/slot_links_next.py b/.agent/tools/slot_links_next.py
deleted file mode 100644
--- a/.agent/tools/slot_links_next.py
+++ /dev/null
@@ -1,669 +0,0 @@
-"""Re-target the links into the TASK and PLAN slots that a task wrote (TASK 115, WI-38).
-
-`skill-archive-task` Step 8 runs this module as `rebase_links.py --inbound ...`. An allow rule
-names `rebase_links.py`, and it passes every argument after `--inbound` to `main(argv)` here, so
-archiving stays automatic (TASK 111 D13, TASK 115 D6).
-
-Steps 5.5 and 7.6.5 rebase the links inside the moved documents. A link in another document whose
-target resolves to `docs/TASK.md` or `docs/PLAN.md` still names the slot, and the next task's TASK
-and PLAN fill it. This module rewrites the slot links the task wrote to the archive paths and lists
-every other one:
-
-* own links: every slot link in a sub-task file of the task, and, with `--since <rev>`, every slot
-  link on a line added since that revision, except in a ledger record (TASK 115 R3);
-* every other slot link of the scan set is recorded as `INBOUND` and left as written;
-* the slots, the archived documents and the symbolic links are not rewritten.
-
-Added lines are computed here, from `git cat-file blob`, with `difflib`. No `git diff` runs, so no
-diff driver, textconv driver or clean filter runs (TASK 115 D3).
-
-Exit codes of `main`: 0 nothing listed; 1 a rewritten link does not resolve, a write failed after
-its first byte, or an unexpected error; 2 an operand, git, `<rev>` or the platform; 3 completed with
-`INBOUND`, `REFUSED`, `UNREADABLE` or `SKIPPED` records.
-"""
-from __future__ import annotations
-
-import argparse
-import bisect
-import difflib
-import errno
-import json
-import os
-import posixpath
-import re
-import stat
-import subprocess
-import unicodedata
-from typing import NamedTuple, Optional
-
-import rebase_links as _rl
-from archive_move import SLUG
-from task_id_tool import classify_task_file
-
-#: Slot -> the kind of archive that replaces it, which also names the link text (`task-033`).
-SLOTS = {"docs/TASK.md": "task", "docs/PLAN.md": "plan"}
-TASK_ARCHIVE_RE = re.compile(rf"docs/tasks/(task-([0-9]{{3,}})-({SLUG})\.md)")
-PLAN_ARCHIVE_RE = re.compile(rf"plan-[0-9]{{3,}}-{SLUG}\.md")
-#: Ledger records keep their bodies byte for byte (`known-issues-format` §8).
-LEDGER_DIRS = ("docs/issues/", "docs/backlog/")
-WALK_SKIPS = {".git", "node_modules"}
-#: Environment variables that would point a git call at another repository, index or object store.
-DROPPED_GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
-                   "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_NAMESPACE",
-                   "GIT_PREFIX")
-GIT_TIMEOUT = 60
-#: The largest file read, and the longest text attributed by `difflib` (TASK 115 D12).
-MAX_BYTES = 4 << 20
-MAX_LINES = 20000
-CHUNK = 1 << 16
-#: Control and bidirectional formatting characters, escaped in the text output (R7.5).
-_UNSAFE = re.compile("[\x00-\x1f\x7f-\x9f\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]")
-#: Actions that the report lists and that make the exit code 3.
-LISTED = ("INBOUND", "REFUSED", "UNREADABLE", "SKIPPED")
-
-
-class InboundError(Exception):
-    """An operand, git, `<rev>` or the platform: nothing was written (exit 2)."""
-
-
-class InboundRecord(NamedTuple):
-    file: str
-    line: Optional[int]
-    action: str            # RETARGETED | INBOUND | REFUSED | UNREADABLE | SKIPPED
-    authored: str          # the target as written
-    new_target: str        # the target after the rewrite; empty unless RETARGETED
-    reason: str
-
-
-class InboundResult(NamedTuple):
-    records: list
-    archived_slot_links: int
-    scan: str              # "git" | "walk"
-    since: Optional[str]   # the full hash `--since` resolved to
-    exit_code: int
-
-
-class _Link(NamedTuple):
-    start: int
-    end: int
-    line: int
-    raw: str               # target text as written, with `<...>` brackets if any
-    bare: str              # target without brackets
-    path: str              # path part of `bare`
-    suffix: str            # `#fragment` or `?query`, kept verbatim
-    slot: str              # the slot the path resolves to
-    bracket: Optional[int]  # index of the `]` of an inline link, else None
-
-
-class _Unreadable(Exception):
-    pass
-
-
-class _Refusal(NamedTuple):
-    reason: str
-    partial: bool          # bytes were written before the failure (R5.3): the run exits 1
-
-
-def _git_env():
-    """The environment of every git call: no redirection, no prompt, no fetch (R6.6)."""
-    env = {key: value for key, value in os.environ.items() if key not in DROPPED_GIT_ENV}
-    env["GIT_OPTIONAL_LOCKS"] = "0"
-    env["GIT_NO_LAZY_FETCH"] = "1"
-    env["GIT_TERMINAL_PROMPT"] = "0"
-    # GIT_NO_LAZY_FETCH needs git 2.44; on an older git this stops the lazy fetch (R6.6).
-    env["GIT_ALLOW_PROTOCOL"] = "none"
-    return env
-
-
-def _git(root, *args):
-    """stdout of `git -C <root> ...` as bytes; raises InboundError on any failure."""
-    command = ["git", "-C", root, "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false",
-               *args]
-    try:
-        proc = subprocess.run(command, capture_output=True, env=_git_env(), timeout=GIT_TIMEOUT,
-                              stdin=subprocess.DEVNULL, check=False)
-    except (OSError, subprocess.TimeoutExpired) as exc:
-        raise InboundError(f"git {args[0]}: {exc}") from exc
-    if proc.returncode != 0:
-        detail = proc.stderr.decode("utf-8", "replace").strip().splitlines()
-        raise InboundError(f"git {args[0]} exited {proc.returncode}"
-                           + (f": {detail[-1]}" if detail else ""))
-    return proc.stdout
-
-
-def _toplevel(root):
-    """The work tree's top level, or None when `root` is not inside one (walk mode)."""
-    try:
-        out = _git(root, "rev-parse", "--show-toplevel")
-    except InboundError:
-        return None
-    return os.fsdecode(out.rstrip(b"\n"))
-
-
-def _resolve(root, since):
-    """The full hash of `since`, a commit that is an ancestor of HEAD, or InboundError (R6.2)."""
-    if since.startswith("-"):
-        raise InboundError(f"--since must not start with '-': {since!r}")
-    try:
-        out = _git(root, "rev-parse", "--verify", "--quiet", f"{since}^{{commit}}")
-    except InboundError as exc:
-        raise InboundError(f"--since {since!r} names no commit") from exc
-    base = out.decode("ascii", "replace").strip()
-    try:
-        _git(root, "merge-base", "--is-ancestor", base, "HEAD")
-    except InboundError as exc:
-        raise InboundError(f"--since {since!r} is not an ancestor of HEAD") from exc
-    return base
-
-
-def _ls_files(root):
-    """The tracked and the untracked, not ignored, paths of the work tree (R2.1)."""
-    out = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
-    return sorted({os.fsdecode(p) for p in out.split(b"\0") if p})
-
-
-def _walk(root, unreadable):
-    """Every file under `root`, repo-relative; a directory it cannot read goes to `unreadable`."""
-    def failed(exc):
-        rel = os.path.relpath(exc.filename or root, root).replace(os.sep, "/")
-        unreadable.append(InboundRecord(rel, None, "UNREADABLE", "", "", exc.strerror or str(exc)))
-
-    found = []
-    for dirpath, dirnames, filenames in os.walk(root, onerror=failed):
-        dirnames[:] = sorted(d for d in dirnames if d not in WALK_SKIPS
-                             and not os.path.isfile(os.path.join(dirpath, d, "pyvenv.cfg")))
-        for name in filenames:
-            rel = os.path.relpath(os.path.join(dirpath, name), root)
-            found.append(rel.replace(os.sep, "/"))
-    return sorted(found)
-
-
-def _read(path):
-    """`(bytes, (st_dev, st_ino))` of a regular file, through a descriptor that follows no link."""
-    try:
-        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0))
-    except OSError as exc:
-        raise _Unreadable(exc.strerror or str(exc)) from exc
-    try:
-        st = os.fstat(fd)
-        if not stat.S_ISREG(st.st_mode):
-            raise _Unreadable("not a regular file")
-        if st.st_size > MAX_BYTES:
-            raise _Unreadable(f"larger than {MAX_BYTES} bytes")
-        chunks, size = [], 0
-        while size <= MAX_BYTES and (chunk := os.read(fd, min(CHUNK, MAX_BYTES + 1 - size))):
-            chunks.append(chunk)
-            size += len(chunk)
-        if size > MAX_BYTES:
-            raise _Unreadable(f"larger than {MAX_BYTES} bytes")
-        return b"".join(chunks), (st.st_dev, st.st_ino)
-    except OSError as exc:
-        raise _Unreadable(exc.strerror or str(exc)) from exc
-    finally:
-        os.close(fd)
-
-
-def _slot_links(text, rel):
-    """Every slot link of `text`, a file at repo-relative `rel`, outside fences and code spans."""
-    masked = _rl._mask(text)
-    brackets = {m.start(1): m.start(0) for m in _rl._INLINE.finditer(masked)}
-    newlines = [i for i, ch in enumerate(text) if ch == "\n"]
-    base_dir = posixpath.dirname(rel)
-    links, seen = [], set()
-    for start, end, raw in _rl._targets(masked):
-        if (start, end) in seen:
-            continue
-        seen.add((start, end))
-        bare = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
-        if not bare or _rl._ABSOLUTE.match(bare):
-            continue
-        path, suffix = _rl._split_fragment(bare)
-        if not path:
-            continue
-        slot = posixpath.normpath(posixpath.join(base_dir, path))
-        if slot in SLOTS:
-            links.append(_Link(start, end, bisect.bisect_left(newlines, start) + 1, raw, bare,
-                               path, suffix, slot, brackets.get(start)))
-    return links, masked
-
-
-def _escaped(text, i):
-    """True when `text[i]` follows an odd number of backslashes."""
-    count = 0
-    while i - 1 - count >= 0 and text[i - 1 - count] == "\\":
-        count += 1
-    return count % 2 == 1
-
-
-def _text_span(masked, close):
-    """`(open, close)` of the link text ending at `masked[close] == ']'`, or None."""
-    depth, i = 0, close - 1
-    while i >= 0:
-        ch = masked[i]
-        if ch == "\n":
-            previous = masked.rfind("\n", 0, i)
-            if not masked[previous + 1:i].strip():
-                return None                      # a blank line ends the paragraph
-        elif ch in "[]" and not _escaped(masked, i):
-            if ch == "]":
-                depth += 1
-            elif depth:
-                depth -= 1
-            else:
-                return i, close
-        i -= 1
-    return None
-
-
-def _new_text(text, link, digits):
-    """The replacement link text, or None when the text is not the slot's name (R4.3)."""
-    inner, ticks = text, ""
-    if len(text) >= 2 and text[0] == "`" and text[-1] == "`" and not text.startswith("``"):
-        inner, ticks = text[1:-1], "`"
-    if inner in {link.slot, posixpath.basename(link.slot), link.bare, link.path, link.raw}:
-        return f"{ticks}{SLOTS[link.slot]}-{digits}{ticks}"
-    return None
-
-
-def _added_lines(base_text, text):
-    """1-based numbers of the lines of `text` that `base_text` lacks (TASK 115 R3)."""
-    def lines(value):
-        return [part[:-1] if part.endswith("\r") else part for part in value.split("\n")]
-    base, work = lines(base_text), lines(text)
-    if len(base) > MAX_LINES or len(work) > MAX_LINES:
-        return None                              # not attributed (R3.3.6)
-    matcher = difflib.SequenceMatcher(None, base, work, autojunk=False)
-    added = set()
-    for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
-        if tag in ("insert", "replace"):
-            added.update(range(j1 + 1, j2 + 1))
-    return added
-
-
-def _target(rel, link, archives):
-    """The link's new target: the archive's path relative to the linking file's directory."""
-    new_path = posixpath.relpath("/" + archives[link.slot], "/" + (posixpath.dirname(rel) or "."))
-    new_target = new_path + link.suffix
-    return f"<{new_target}>" if link.raw.startswith("<") else new_target
-
-
-def _rewrite_text(text, masked, rel, links, archives, digits):
-    """`text` with each link of `links` re-targeted, and its text renamed where R4.3 applies."""
-    edits = []
-    for link in links:
-        edits.append((link.start, link.end, _target(rel, link, archives)))
-        if link.bracket is None:
-            continue
-        span = _text_span(masked, link.bracket)
-        if span is None:
-            continue
-        if span[0] > 0 and text[span[0] - 1] == "!" and not _escaped(text, span[0] - 1):
-            continue                             # an image keeps its alt text
-        replacement = _new_text(text[span[0] + 1:span[1]], link, digits)
-        if replacement is not None:
-            edits.append((span[0] + 1, span[1], replacement))
-    out, cursor = [], 0
-    for start, end, replacement in sorted(edits):
-        if start < cursor:
-            return None                          # overlapping links (R4.7)
-        out.append(text[cursor:start])
-        out.append(replacement)
-        cursor = end
-    out.append(text[cursor:])
-    return "".join(out)
-
-
-def _resolves(root, record):
-    """True when a RETARGETED record's new target names an existing archive (R5.5)."""
-    target = record.new_target[1:-1] if record.new_target.startswith("<") else record.new_target
-    path, _suffix = _rl._split_fragment(target)
-    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(record.file), path))
-    return os.path.isfile(os.path.join(root, resolved))
-
-
-def _descriptor_path(fd):
-    """The path the kernel holds for `fd`, or None where the platform gives none (TASK 116 R7.4).
-
-    `fcntl.F_GETPATH` gives it on darwin, and the link `/proc/self/fd/<fd>` on Linux. It is one
-    lookup, so no swap of a directory between two lookups by name can change it, as one can
-    between `realpath` and `stat`. A failed lookup raises `OSError`. The same lookup as
-    `rebase_links._descriptor_path`, held here since a copy of one module may run beside
-    the base of the other.
-    """
-    try:
-        import fcntl
-    except ImportError:
-        fcntl = None
-    if hasattr(fcntl, "F_GETPATH"):
-        return os.fsdecode(fcntl.fcntl(fd, fcntl.F_GETPATH, bytes(1024)).split(b"\0", 1)[0])
-    if os.path.isdir("/proc/self/fd"):
-        return os.readlink(f"/proc/self/fd/{fd}")
-    return None
-
-
-def _write_file(root, rel, original, ident, data, dry_run=False):
-    """Write `data` over `rel` through a descriptor that follows no link (R5.2, R5.3).
-
-    After the open, the descriptor must be the file at the real path of `rel`, and the directory
-    of its own path must lie inside `root` (TASK 116 R7.4). Returns None when the file was
-    written, or, in a dry run, would be; else a `_Refusal`. A dry run makes every check of a real
-    run and writes nothing (R5.4).
-    """
-    path = os.path.join(root, rel)
-    real_root = os.path.realpath(root)
-    parent = os.path.realpath(os.path.dirname(path))
-    if os.path.commonpath([parent, real_root]) != real_root:
-        return _Refusal("its directory resolves outside the working directory", False)
-    if _rl._under_git(rel, root):
-        return _Refusal("lies under .git/", False)
-    try:
-        fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0))
-    except OSError as exc:
-        return _Refusal(f"cannot open it: {exc.strerror or exc}", False)
-    written = 0
-    try:
-        st = os.fstat(fd)
-        if not stat.S_ISREG(st.st_mode):
-            return _Refusal("is not a regular file", False)
-        if st.st_nlink != 1:
-            return _Refusal(f"has {st.st_nlink} hard links", False)
-        # TASK 116 R7.4: the descriptor is the file at the real path of `rel`, inside the root.
-        try:
-            real = os.path.realpath(path)
-            now = os.stat(real)
-            where = _descriptor_path(fd) or real
-        except (OSError, ValueError):
-            return _Refusal("is not the file at its real path", False)
-        if (now.st_dev, now.st_ino) != (st.st_dev, st.st_ino):
-            return _Refusal("is not the file at its real path", False)
-        if os.path.commonpath([os.path.dirname(where), real_root]) != real_root:
-            return _Refusal("its directory resolves outside the working directory", False)
-        if (st.st_dev, st.st_ino) != ident:
-            return _Refusal("changed during the run", False)
-        chunks, size = [], 0
-        while size <= len(original) and (chunk := os.read(fd, CHUNK)):
-            chunks.append(chunk)
-            size += len(chunk)
-        if b"".join(chunks) != original:
-            return _Refusal("changed during the run", False)
-        if dry_run:
-            return None
-        os.lseek(fd, 0, os.SEEK_SET)
-        view = memoryview(data)
-        while written < len(data):
-            written += os.write(fd, view[written:])
-        os.ftruncate(fd, len(data))
-        os.fsync(fd)
-        now = os.stat(path, follow_symlinks=False)
-        if (now.st_dev, now.st_ino) != (st.st_dev, st.st_ino):
-            return _Refusal("changed during the run", False)   # an editor saved over it (R5.3)
-    except OSError as exc:
-        if written:
-            return _Refusal(f"partly written: {exc.strerror or exc}", True)
-        return _Refusal(f"cannot write it: {exc.strerror or exc}", False)
-    finally:
-        os.close(fd)
-    return None
-
-
-def _check_archives(root, task_archive, plan_archive):
-    """`(digits, {slot: archive})` for the operands of R1.4 and R1.5, or InboundError."""
-    match = TASK_ARCHIVE_RE.fullmatch(task_archive or "")
-    if not match:
-        raise InboundError(f"--task must be docs/tasks/task-<ID>-<slug>.md, not {task_archive!r}")
-    name, digits, slug = match.groups()
-    _check_regular(root, task_archive)
-    kind = classify_task_file(os.path.join(root, "docs", "tasks"), name)
-    if kind is None or kind[1]:
-        raise InboundError(f"{task_archive} is a sub-task, not a task archive")
-    archives = {"docs/TASK.md": task_archive}
-    if plan_archive is not None:
-        expected = f"docs/plans/plan-{digits}-{slug}.md"
-        if plan_archive != expected:
-            raise InboundError(f"--plan must be {expected}, not {plan_archive!r}")
-        _check_regular(root, plan_archive)
-        archives["docs/PLAN.md"] = plan_archive
-    return digits, archives
-
-
-def _check_regular(root, rel):
-    """InboundError unless `rel` is a regular file and not a link."""
-    try:
-        st = os.lstat(os.path.join(root, rel))
-    except OSError as exc:
-        raise InboundError(f"{rel}: {exc.strerror or exc}") from exc
-    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
-        raise InboundError(f"{rel} is a symbolic link or not a regular file")
-
-
-def _archived(root, rel, task_id):
-    """`(archived, own_subtask)` for a repo-relative path."""
-    head, name = posixpath.split(rel)
-    if head == "docs/plans":
-        return bool(PLAN_ARCHIVE_RE.fullmatch(name)), False
-    if head == "docs/tasks":
-        kind = classify_task_file(os.path.join(root, "docs", "tasks"), name)
-        if kind is not None:
-            if not kind[1]:
-                return True, False
-            return False, kind[0] == task_id
-    return False, False
-
-
-def _scan_set(root, unreadable):
-    """`(scan, paths, prefix)`: the `*.md` paths of R2.1 or R2.2, repo-relative and sorted."""
-    toplevel = _toplevel(root)
-    if toplevel is None:
-        return "walk", [p for p in _walk(root, unreadable) if p.endswith(".md")], ""
-    real_root, real_top = os.path.realpath(root), os.path.realpath(toplevel)
-    if os.path.commonpath([real_root, real_top]) != real_top:
-        raise InboundError(f"{root} does not lie inside its git top level {toplevel}")
-    paths = {unicodedata.normalize("NFC", p): p for p in _ls_files(root) if p.endswith(".md")}
-    try:
-        with os.scandir(os.path.join(root, "docs", "tasks")) as entries:
-            for entry in entries:
-                if entry.name.endswith(".md") and (entry.is_symlink()
-                                                  or entry.is_file(follow_symlinks=False)):
-                    rel = f"docs/tasks/{entry.name}"
-                    paths.setdefault(unicodedata.normalize("NFC", rel), rel)
-    except OSError as exc:
-        if exc.errno not in (errno.ENOENT, errno.ENOTDIR):
-            unreadable.append(InboundRecord("docs/tasks", None, "UNREADABLE", "", "",
-                                            exc.strerror or str(exc)))
-    prefix = os.fsdecode(_git(root, "rev-parse", "--show-prefix").rstrip(b"\n"))
-    return "git", sorted(paths.values()), prefix
-
-
-def retarget_inbound(repo_root, task_archive, plan_archive=None, since=None, dry_run=False):
-    """Re-target the task's own slot links and list the others (TASK 115 R1-R7).
-
-    Args:
-        repo_root: the project root; `task_archive` and `plan_archive` are relative to it.
-        task_archive: `docs/tasks/task-<ID>-<slug>.md`, an existing parent archive.
-        plan_archive: `docs/plans/plan-<ID>-<slug>.md` when Step 7 archived the plan, else None.
-        since: the task's base revision; lines added since it are own (R3.2). None: none are.
-        dry_run: make every check and write nothing (R5.4).
-
-    Returns:
-        InboundResult(records, archived_slot_links, scan, since, exit_code).
-
-    Raises:
-        InboundError: an operand, git, `<rev>` or the platform (exit 2); nothing was written.
-    """
-    if not hasattr(os, "O_NOFOLLOW"):
-        raise InboundError("this platform has no O_NOFOLLOW")
-    root = os.path.abspath(repo_root)
-    digits, archives = _check_archives(root, task_archive, plan_archive)
-    task_id = int(digits)
-    records = []
-    scan, paths, prefix = _scan_set(root, records)
-    if since is not None and scan == "walk":
-        raise InboundError("--since needs a git work tree")
-    base = _resolve(root, since) if since is not None else None
-    base_paths = None
-
-    archived_count, writes = 0, []
-    for rel in paths:
-        if rel in SLOTS:
-            continue
-        path = os.path.join(root, rel)
-        if not os.path.lexists(path):
-            continue
-        if os.path.islink(path):
-            records.append(InboundRecord(rel, None, "SKIPPED", "", "", "symbolic link"))
-            continue
-        archived, own_file = _archived(root, rel, task_id)
-        try:
-            data, ident = _read(path)
-            text = data.decode("utf-8")
-        except (_Unreadable, UnicodeDecodeError) as exc:
-            if not archived:
-                reason = "not UTF-8" if isinstance(exc, UnicodeDecodeError) else str(exc)
-                records.append(InboundRecord(rel, None, "UNREADABLE", "", "", reason))
-            continue
-        if "TASK.md" not in text and "PLAN.md" not in text:
-            continue                             # no slot name: no slot link, no mask cost (L3)
-        links, masked = _slot_links(text, rel)
-        if not links:
-            continue
-        if archived:
-            archived_count += len(links)
-            continue
-        added, inbound_reason = None, ""
-        if base is not None and not own_file and not rel.lower().startswith(LEDGER_DIRS):
-            if base_paths is None:
-                listing = _git(root, "ls-tree", "-r", "-z", "--name-only", "--full-tree", base)
-                base_paths = {os.fsdecode(p) for p in listing.split(b"\0") if p}
-            top_rel = prefix + rel
-            if top_rel in base_paths:
-                blob = _git(root, "cat-file", "blob", f"{base}:{top_rel}")
-                added = _added_lines(blob.decode("utf-8", "replace"), text)
-            elif text.count("\n") < MAX_LINES:
-                added = range(1, text.count("\n") + 2)
-            if added is None:
-                added, inbound_reason = set(), f"not attributed: more than {MAX_LINES} lines"
-        own = [link for link in links if link.slot in archives
-               and (own_file or (added is not None and link.line in added))]
-        own_starts = {link.start for link in own}
-        for link in links:
-            if link.start not in own_starts:
-                records.append(InboundRecord(rel, link.line, "INBOUND", link.raw, "",
-                                             inbound_reason))
-        if own:
-            writes.append((rel, data, ident, text, masked, own))
-
-    partial = False
-    for rel, data, ident, text, masked, own in writes:
-        new_text = _rewrite_text(text, masked, rel, own, archives, digits)
-        if new_text is None:
-            refusal = _Refusal("overlapping links", False)
-        else:
-            refusal = _write_file(root, rel, data, ident, new_text.encode("utf-8"), dry_run)
-        partial = partial or bool(refusal and refusal.partial)
-        for link in own:
-            if refusal is None:
-                records.append(InboundRecord(rel, link.line, "RETARGETED", link.raw,
-                                             _target(rel, link, archives), ""))
-            else:
-                records.append(InboundRecord(rel, link.line, "REFUSED", link.raw, "",
-                                             refusal.reason))
-
-    unresolved = any(r.action == "RETARGETED" and not _resolves(root, r) for r in records)
-    records.sort(key=lambda r: (r.file, r.line or 0, r.action))
-    if unresolved or partial:
-        code = 1
-    elif any(r.action in LISTED for r in records):
-        code = 3
-    else:
-        code = 0
-    return InboundResult(records, archived_count, scan, base, code)
-
-
-class _Parser(argparse.ArgumentParser):
-    """An argument error is an `InboundError`, so it exits 2 with the stderr object of R7.4."""
-
-    def error(self, message):
-        raise InboundError(message)
-
-
-def _escape(value):
-    """`value` with control and bidirectional formatting characters as `\\uXXXX` (R7.5)."""
-    return _UNSAFE.sub(lambda m: f"\\u{ord(m.group()):04x}", value)
-
-
-def _emit(stream, line):
-    """Write `line` and a newline; text the stream cannot encode becomes backslash escapes."""
-    encoding = getattr(stream, "encoding", None) or "utf-8"
-    stream.write(line.encode(encoding, "backslashreplace").decode(encoding, "replace") + "\n")
-
-
-def _summary(result, dry_run):
-    """The last line of the text output (R7.4)."""
-    counts = {}
-    for record in result.records:
-        counts[record.action] = counts.get(record.action, 0) + 1
-    listed = sum(counts.get(action, 0) for action in LISTED)
-    attributed = (f"lines attributed since {result.since}" if result.since
-                  else "lines not attributed")
-    return (f"{counts.get('RETARGETED', 0)} retargeted / {listed} listed / "
-            f"{result.archived_slot_links} slot links in archived documents (not listed); "
-            f"scan {result.scan}; {attributed}" + (" (dry run)" if dry_run else ""))
-
-
-def main(argv=None):
-    """`rebase_links.py --inbound` passes the arguments after `--inbound` here."""
-    import sys
-    parser = _Parser(prog="rebase_links.py --inbound", allow_abbrev=False,
-                     description="Re-target the slot links a task wrote (TASK 115, WI-38).")
-    parser.add_argument("--task", required=True, help="docs/tasks/task-<ID>-<slug>.md")
-    parser.add_argument("--plan", help="docs/plans/plan-<ID>-<slug>.md, when Step 7 archived it")
-    parser.add_argument("--since", help="the task's base revision; lines added since it are own")
-    parser.add_argument("--dry-run", action="store_true")
-    parser.add_argument("--json", action="store_true")
-    try:
-        args = parser.parse_args(sys.argv[1:] if argv is None else list(argv))
-        result = retarget_inbound(os.getcwd(), args.task, args.plan, args.since, args.dry_run)
-    except InboundError as exc:
-        _emit(sys.stderr, json.dumps({"ok": False, "error": str(exc)}))
-        return 2
-    except Exception as exc:                      # R7.4: an unexpected error is exit 1
-        _emit(sys.stderr, json.dumps({"ok": False,
-                                      "error": f"unexpected: {type(exc).__name__}: {exc}"}))
-        return 1
-    try:
-        _report(sys.stdout, result, args.json, args.dry_run)
-        sys.stdout.flush()
-    except OSError as exc:                        # a closed stdout, after the writes (R7.4)
-        try:
-            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
-        except (AttributeError, OSError, ValueError):
-            pass                                  # no descriptor: nothing flushes at exit
-        try:
-            _emit(sys.stderr, json.dumps({"ok": False, "error": f"report not written: {exc}"}))
-        except OSError:
-            pass
-        return 1
-    return result.exit_code
-
-
-def _report(stream, result, as_json, dry_run):
-    """The records and the summary line, or the `--json` object (R7.4, R7.5)."""
-    if as_json:
-        _emit(stream, json.dumps({"ok": result.exit_code in (0, 3),
-                                  "exit_code": result.exit_code, "scan": result.scan,
-                                  "since": result.since,
-                                  "archived_slot_links": result.archived_slot_links,
-                                  "records": [r._asdict() for r in result.records]},
-                                 ensure_ascii=True, indent=1))
-        return
-    for r in result.records:
-        where = r.file if r.line is None else f"{r.file}:{r.line}"
-        line = f"[{r.action}] {_escape(where)}"
-        if r.authored:
-            line += f"  {_escape(r.authored)}"
-        if r.action == "RETARGETED":
-            line += f"  ->  {_escape(r.new_target)}"
-        if r.reason:
-            line += f"  ({_escape(r.reason)})"
-        _emit(stream, line)
-    _emit(stream, _summary(result, dry_run))
diff --git a/.claude/settings.json b/.claude/settings.json
--- a/.claude/settings.json
+++ b/.claude/settings.json
@@ -48,6 +48,14 @@
       "Bash(python System/scripts/check_prompt_references.py --root .)",
       "Bash(python System/scripts/security_lint.py --root .)",
       "Bash(python System/scripts/smoke_workflows.py --root .)"
+    ],
+    "deny": [
+      "Bash(git stash)",
+      "Bash(git stash *)",
+      "Bash(git reset --hard)",
+      "Bash(git reset --hard *)",
+      "Bash(git clean)",
+      "Bash(git clean *)"
     ]
   },
   "hooks": {
diff --git a/tests/test_committed_settings.py b/tests/test_committed_settings.py
--- a/tests/test_committed_settings.py
+++ b/tests/test_committed_settings.py
@@ -10,15 +10,20 @@
   admit `--output`, `-o` or a write to a ref; each rule's command name is one of a fixed set
   (``TC-S3``, TASK 111 R2.7, TASK 112 TC-S3);
 * the repository ignores the operator's local settings file (``TC-S4``);
-* the settings hold `env`, `permissions.allow` and the one PostToolUse hook of the base, nothing
-  else (``TC-S6``);
+* the settings hold `env`, `permissions.allow`, `permissions.deny` and the one PostToolUse hook
+  of the base, nothing else; the deny list is TASK 116 §10.1 (``TC-S6``);
 * every part of every shell block of `skill-archive-task` matches a committed rule; no part runs
   `mv`, `test` or `mkdir`; each archive command calls `archive_move.py` with operands the script
-  accepts (``TC-S7``, TASK 111 D13, TASK 112 R6.2);
+  accepts (``TC-S7``, TASK 111 D13, TASK 112 R6.2); each `--inbound` command is one line, has
+  `--inbound` first and names operands the inbound mode accepts (``TC-S7``, ``TC-S7b``,
+  ``TC-S7c``, TASK 116 R2.3 to R2.5);
 * `skill-safe-commands`, the READMEs' Antigravity lists, `GEMINI.md` and `AGENTS.md` state the
   limit of R2.7 for every vendor; the pattern block, the command table and the fence lists equal
   their reviewed text; table and patterns name the same commands; no pattern admits an option that
-  runs a program or writes (``TC-S8``, TASK 112 R3, R6.1).
+  runs a program or writes (``TC-S8``, TASK 112 R3, R6.1);
+* the deny rules match `git stash`, `git reset --hard` and `git clean`, alone and in a compound
+  command; they match none of six listed commands that the framework's steps run, and no archive
+  command (``TC-S9``, TASK 116 R4.4).
 
 A fence is read as CommonMark reads it: three or more backticks or tildes, any info string. A shell
 fence is one whose first info word is `bash`, `sh`, `shell`, `zsh` or `console`.
@@ -112,6 +117,11 @@
 #: A `python` rule runs a bare `-m pytest` or a named script, never `-c` or arbitrary code.
 PYTHON_RULE = re.compile(r"Bash\(python3? (-m pytest|[\w./-]+\.py( .*)?)\)")
 ARCHIVE_SCRIPT = PROJECT_ROOT / ".agent" / "tools" / "archive_move.py"
+#: The module of `rebase_links.py --inbound`; TC-S7 reads the options of its `main` as text.
+SLOT_LINKS = PROJECT_ROOT / ".agent" / "tools" / "slot_links.py"
+#: TASK 116 §10.1: Claude Code refuses these three git commands, bare and with arguments.
+DENY_RULES = ("Bash(git stash)", "Bash(git stash *)", "Bash(git reset --hard)",
+              "Bash(git reset --hard *)", "Bash(git clean)", "Bash(git clean *)")
 ARCHIVE_COMMANDS = ("python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/",
                     "python3 .agent/tools/archive_move.py docs/PLAN.md docs/plans/",
                     "python3 .agent/tools/task_id_tool.py", "python3 .agent/tools/rebase_links.py",
@@ -150,7 +160,11 @@
 
 
 def _approves(rule, command):
-    """Claude Code's documented match: the whole command text, `*` standing in for any text."""
+    """Claude Code's documented match: the whole command text, `*` standing in for any text.
+
+    One difference: here a ` *` after a space needs an argument, while Claude Code also matches the
+    bare command. Each rule is therefore written in both forms (TASK 116 D4).
+    """
     m = re.fullmatch(r"Bash\((.*)\)", rule)
     pattern = ".*".join(re.escape(part) for part in m.group(1).split("*"))
     return re.fullmatch(pattern, command, re.S) is not None
@@ -186,21 +200,113 @@
             yield body
 
 
-def _archive_commands():
-    """Every part of every shell block of `skill-archive-task`."""
-    for block in _shell_blocks(ARCHIVE_SKILL.read_text(encoding="utf-8")):
-        block = block.replace("\\\n", " ")
-        for line in block.splitlines():
-            if not line.strip() or line.strip().startswith("#"):
+def _archive_commands(text=None):
+    """Every part of every shell command of `text`, read by `_shell_commands`.
+
+    With no `text`, the text of `skill-archive-task`, as at the base (TASK 116 TC-S7d).
+    """
+    if text is None:
+        text = ARCHIVE_SKILL.read_text(encoding="utf-8")
+    for _, line in _shell_commands(text):
+        line = re.sub(r'"<[^<>"]+>"', '"sample"', _fill(line))
+        for part in re.split(r"&&|\|\||[;|&]", line):
+            part = " ".join(part.split())
+            if part:
+                yield part
+
+
+def _fill(line):
+    """`line` with the placeholders of `skill-archive-task` filled: `PLACEHOLDERS`, then `112`."""
+    for key, value in PLACEHOLDERS.items():
+        line = line.replace(key, value)
+    return re.sub(r"\{[^}]+\}", "112", line)
+
+
+def _shell_commands(text):
+    """`(physical lines, joined text)` of every command of every shell block of `text`.
+
+    A line that ends with `\\` continues on the next one, as the shell reads it. A comment line is
+    no command and continues no line.
+    """
+    for block in _shell_blocks(text):
+        lines = block.splitlines()
+        i = 0
+        while i < len(lines):
+            group = [lines[i]]
+            comment = lines[i].strip().startswith("#")
+            while not comment and group[-1].endswith("\\") and i + 1 < len(lines):
+                i += 1
+                group.append(lines[i])
+            i += 1
+            if group[0].strip().startswith("#"):
                 continue
-            for key, value in PLACEHOLDERS.items():
-                line = line.replace(key, value)
-            line = re.sub(r"\{[^}]+\}", "112", line)
-            line = re.sub(r'"<[^<>"]+>"', '"sample"', line)
-            for part in re.split(r"&&|\|\||[;|&]", line):
-                part = " ".join(part.split())
-                if part:
-                    yield part
+            joined = " ".join(line[:-1] if line.endswith("\\") else line for line in group)
+            yield group, " ".join(joined.split())
+
+
+def _wrapped_inbound(text):
+    """The `--inbound` commands of `text` that a line continuation wraps (TASK 116 R2.3)."""
+    return [joined for group, joined in _shell_commands(text)
+            if "rebase_links.py --inbound" in joined
+            and any(line.rstrip().endswith("\\") for line in group)]
+
+
+def _inbound_options():
+    """`{option: takes a value}` of the `add_argument` calls of `slot_links.main`, read as text."""
+    text = SLOT_LINKS.read_text(encoding="utf-8")
+    main = text[text.index("def main("):]
+    return {m.group(1): 'action="store_true"' not in m.group(2)
+            for m in re.finditer(r'add_argument\("(--[a-z-]+)"(.*)$', main, re.M)}
+
+
+def _inbound_problems(text, options, pairs):
+    """Why an `--inbound` command of `text` would not run as Step 8 means it (TASK 116 R2.4).
+
+    The placeholders are filled as TC-S7 fills them. `--task` names
+    `docs/tasks/task-<ID>-<slug>.md`, and `--plan` the plan of the same `<ID>` and `<slug>`, by the
+    name patterns of `archive_move.PAIRS`.
+    """
+    problems = []
+    for _, joined in _shell_commands(text):
+        if "rebase_links.py" not in joined or "--inbound" not in joined:
+            continue
+        words = _fill(joined).split()
+        args = words[words.index(".agent/tools/rebase_links.py") + 1:]
+        if args[:1] != ["--inbound"]:
+            problems.append((joined, "--inbound is not the first argument"))
+            continue
+        seen, problem, i, rest = {}, None, 0, args[1:]
+        while i < len(rest) and problem is None:
+            name, eq, value = rest[i].partition("=")
+            if not name.startswith("--"):
+                problem = f"a positional argument {rest[i]!r}"
+            elif name not in options:
+                problem = f"{name} is not an option of the inbound mode"
+            elif options[name] and not eq:
+                i += 1
+                if i < len(rest) and not rest[i].startswith("--"):
+                    seen[name] = rest[i]
+                else:
+                    problem = f"{name} has no value"
+            elif options[name]:
+                seen[name] = value
+            elif eq:
+                problem = f"{name} takes no value"
+            else:
+                seen[name] = True
+            i += 1
+        task, plan = seen.get("--task"), seen.get("--plan")
+        if problem is None and not (isinstance(task, str) and task.startswith("docs/tasks/")
+                                    and pairs["docs/TASK.md"][1].fullmatch(task[11:])):
+            problem = "--task is not docs/tasks/task-<ID>-<slug>.md"
+        if problem is None and plan is not None and not (
+                isinstance(plan, str) and plan.startswith("docs/plans/")
+                and pairs["docs/PLAN.md"][1].fullmatch(plan[11:])
+                and plan[len("docs/plans/plan-"):] == task[len("docs/tasks/task-"):]):
+            problem = "--plan is not the plan of the --task"
+        if problem:
+            problems.append((joined, problem))
+    return problems
 
 
 def _pattern_block():
@@ -286,18 +392,30 @@
 
 
 class TestHooks(unittest.TestCase):
-    """TC-S6: a settings key takes effect in the running session; none joins without review."""
-
-    def test_s6_settings_hold_env_allow_and_the_base_hook_only(self):
+    """TC-S6: a settings key takes effect in the running session; none joins without review.
+
+    `permissions` holds the allow list and the deny list of TASK 116 §10.1, in that order.
+    """
+
+    def test_s6_settings_hold_env_allow_deny_and_the_base_hook_only(self):
         settings = _settings()
         self.assertEqual(sorted(settings), ["env", "hooks", "permissions"])
-        self.assertEqual(list(settings["permissions"]), ["allow"])
+        self.assertEqual(list(settings["permissions"]), ["allow", "deny"])
+        self.assertEqual(tuple(settings["permissions"]["deny"]), DENY_RULES)
         self.assertEqual(settings["env"], ENV)
         self.assertEqual(settings["hooks"], HOOKS)
 
 
+#: The two `--inbound` commands of `skill-archive-task`, Step 8 and Example Flow item 11.
+STEP8 = ("python3 .agent/tools/rebase_links.py --inbound --task docs/tasks/{filename} "
+         "--plan docs/plans/{plan_filename} --since {base_revision}")
+FLOW = ("python3 .agent/tools/rebase_links.py --inbound "
+        "--task docs/tasks/task-{OLD_ID}-{old-slug}.md "
+        "--plan docs/plans/plan-{OLD_ID}-{old-slug}.md --since {old-base}")
+
+
 class TestArchiving(unittest.TestCase):
-    """TC-S7: archiving stays automatic (TASK 111 D13)."""
+    """TC-S7: archiving stays automatic (TASK 111 D13); TC-S7b to TC-S7d (TASK 116 R2.5)."""
 
     def test_s7_archive_commands_match_a_committed_rule(self):
         allow = _settings()["permissions"]["allow"]
@@ -317,6 +435,59 @@
                     operands = command.split()[2:]
                     self.assertEqual(len(operands), 2)
                     module._parse(*operands)  # raises Refused on an operand the script refuses
+
+    def test_s7_inbound_commands_are_one_line_with_known_operands(self):
+        text = ARCHIVE_SKILL.read_text(encoding="utf-8")
+        self.assertEqual(len([j for _, j in _shell_commands(text) if "--inbound" in j]), 2)
+        self.assertEqual(_wrapped_inbound(text), [])
+        self.assertEqual(_inbound_problems(text, _inbound_options(), _archive_module().PAIRS), [])
+
+    def test_s7b_a_wrapped_inbound_command_is_found(self):
+        text = ARCHIVE_SKILL.read_text(encoding="utf-8")
+        self.assertIn(STEP8, text)
+        for wrapped in (STEP8.replace(" --plan", " \\\n  --plan"),
+                        STEP8.replace(" --inbound", " \\\n  --inbound")):
+            with self.subTest(wrapped=wrapped):
+                self.assertTrue(_wrapped_inbound(text.replace(STEP8, wrapped, 1)))
+
+    def test_s7d_a_comment_continues_no_line(self):
+        # bash, sh and zsh run the line after a comment that ends with a backslash.
+        text = "```bash\n# a note \\\nmv a b\n```\n"
+        self.assertEqual([joined for _, joined in _shell_commands(text)], ["mv a b"])
+        self.assertIn("mv a b", list(_archive_commands(text)))
+
+    def test_s7c_an_inbound_command_with_wrong_operands_is_found(self):
+        text = ARCHIVE_SKILL.read_text(encoding="utf-8")
+        options, pairs = _inbound_options(), _archive_module().PAIRS
+        self.assertIn(STEP8, text)
+        self.assertIn(FLOW, text)
+        plan = "--plan is not the plan of the --task"
+        task = "--task is not docs/tasks/task-<ID>-<slug>.md"
+        plantings = (
+            # one planting per sub-check of `--task` and `--plan`: a directory of the right
+            # length, and a name in the right directory
+            (STEP8, STEP8.replace("docs/tasks/{filename}", "docs/taskz/{filename}"), task),
+            (STEP8, STEP8.replace("docs/tasks/{filename}", "docs/tasks/ksat-112-sample.md"), task),
+            (STEP8, STEP8.replace("docs/plans/{plan_filename}", "docs/planz/{plan_filename}"), plan),
+            (STEP8, STEP8.replace("docs/plans/{plan_filename}", "docs/plans/nalp-112-sample.md"),
+             plan),
+            (STEP8, STEP8.replace("--since", "--base"),
+             "--base is not an option of the inbound mode"),
+            (STEP8, STEP8.replace("docs/plans/{plan_filename}", "docs/plan/{plan_filename}"), plan),
+            (STEP8, STEP8.replace("docs/tasks/{filename}", "{filename}"), task),
+            (FLOW, FLOW.replace("--inbound --task docs/tasks/task-{OLD_ID}-{old-slug}.md",
+                                "--task docs/tasks/task-{OLD_ID}-{old-slug}.md --inbound"),
+             "--inbound is not the first argument"),
+            (FLOW, FLOW.replace("plan-{OLD_ID}", "plan-113"), plan),
+            (STEP8, STEP8 + " extra", "a positional argument 'extra'"),
+            (STEP8, STEP8 + " --dry-run=1", "--dry-run takes no value"),
+            (STEP8, STEP8.replace("--since {base_revision}", "--since --dry-run"),
+             "--since has no value"),
+        )
+        for old, new, reason in plantings:
+            with self.subTest(planted=new):
+                problems = _inbound_problems(text.replace(old, new, 1), options, pairs)
+                self.assertEqual([found for _, found in problems], [reason])
 
     def test_s7_fences_of_the_archive_skill(self):
         words = tuple(word for word, _ in _fences(ARCHIVE_SKILL.read_text(encoding="utf-8")))
@@ -410,7 +581,7 @@
         '| **Archiving** | `python3 .agent/tools/archive_move.py` | Moves `docs/TASK.md` and `docs/PLAN.md` into `docs/tasks/` and `docs/plans/`; refuses every other operand (TASK 112) |',
         '| **Directory** | `mkdir -p docs/tasks`, `mkdir -p docs/plans`, `mkdir -p docs/architectures` | Idempotent; three fixed directories |',
         '| **Tool calls** | `generate_task_archive_filename`, `list_directory`, `read_file` | Native tools |',
-        '| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py`, `python3 .agent/skills/artifact-formalizer/evals/grade_run.py`, `python3 System/scripts/doctor.py` | Framework automation; `rebase_links.py` and `init_skill.py` write only inside the working directory, compared without resolving links |',
+        '| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py`, `python3 .agent/skills/artifact-formalizer/evals/grade_run.py`, `python3 System/scripts/doctor.py` | Framework automation; `rebase_links.py` writes markdown in the working directory by real path, `init_skill.py` by path |',
         '| **Testing** | `python -m pytest`, `python3 -m pytest`, `npm test`, `cargo test`, with no argument | Their options can run a program, delete a directory or overwrite a file (TASK 111 D14) |',
     )
 
@@ -500,6 +671,45 @@
                               "`SafeToAutoRun: true`", text)
 
 
+class TestDenyList(unittest.TestCase):
+    """TC-S9: the deny rules refuse three git commands that discard work (TASK 116 R4.4)."""
+
+    DENIED = ("git stash", "git stash -u", "git stash pop", "git stash list",
+              "git reset --hard", "git reset --hard HEAD~1", "git clean -fdx",
+              "git status && git stash -q")
+    NOT_DENIED = ("git restore --source=c8aba597ed06545a8fc0933238aaa4510f059db2 --staged "
+                  "--worktree -- docs/TASK.md",
+                  "git status", "git diff", "git reset",
+                  "git apply -R --whitespace=nowarn docs/reviews/framework-audit-116-stage3.diff",
+                  "rm -- docs/reviews/x.md")
+
+    @staticmethod
+    def _denied(command):
+        """A deny rule matches a part of `command`, split on the operators TC-S7 splits on.
+
+        Claude Code also splits on a newline and looks inside a subshell; no listed command holds
+        either.
+        """
+        deny = _settings()["permissions"].get("deny", [])
+        parts = [" ".join(part.split()) for part in re.split(r"&&|\|\||[;|&]", command)]
+        return any(_approves(rule, part) for rule in deny for part in parts if part)
+
+    def test_s9_denied_commands_match_a_rule(self):
+        for command in self.DENIED:
+            with self.subTest(command=command):
+                self.assertTrue(self._denied(command))
+
+    def test_s9_other_commands_match_none(self):
+        for command in self.NOT_DENIED:
+            with self.subTest(command=command):
+                self.assertFalse(self._denied(command))
+
+    def test_s9_archive_commands_match_none(self):
+        for command in _archive_commands():
+            with self.subTest(command=command):
+                self.assertFalse(self._denied(command))
+
+
 class TestGitignore(unittest.TestCase):
     """TC-S4: the operator's local settings never reach a commit."""
 
diff --git a/tests/test_script_guards.py b/tests/test_script_guards.py
--- a/tests/test_script_guards.py
+++ b/tests/test_script_guards.py
@@ -9,6 +9,19 @@
   second hard link and a file under `.git/` in any letter case or through a link, with exit 2 and
   no write (``TC-G1``, ``TC-G2``); a file inside is rewritten as before (``TC-G3``); one refused
   operand stops every write (``TC-G7``);
+* `rebase_links.py` refuses a file whose directory resolves outside the working directory, with
+  exit 2 and no write, also through a `..` after a link; a file whose directory link resolves
+  inside is rewritten (``TC-G13`` to ``TC-G15``, TASK 116 R1.1);
+* both modes write through the descriptor they checked: a directory swapped around the open or
+  moved out, a file swapped for a link, a second hard link, a file replaced after the read, a FIFO
+  and a platform with no `O_NOFOLLOW` are refused with no write, and so are three swaps around the
+  identity check; a failed write leaves a prefix of the new text, and no descriptor stays open
+  (``TC-G16`` to ``TC-G27``, TASK 116 R7);
+* `rebase_links.py` takes a slot map only for `docs/TASK.md` and `docs/PLAN.md`, each with an
+  archive of its form, and only a markdown operand under `docs/`. Its `--repo-root`, `--from` and
+  `--to` stay in the tree. A rewrite adds to a link no character outside letters, digits and
+  `._~/%-` and no path part that its author did not write, and the text gains no such character
+  (``TC-G28`` to ``TC-G30``, TASK 116 R8);
 * `rebase_links.py --inbound` refuses a file with a second hard link and skips a symbolic link,
   with exit 3 and no write; it rewrites a sub-task inside; neither a module nor a `.pyc`
   planted beside the script runs (``TC-G8`` to ``TC-G12``, TASK 115);
@@ -18,18 +31,31 @@
 The working directory is the `realpath` of a temporary root: `os.getcwd()` returns the resolved
 path on darwin, where `tempfile` returns `/var/...`.
 """
+import builtins
+import contextlib
+import errno
+import gc
+import importlib.util
+import io
+import json
 import os
+import re
 import shutil
 import subprocess
 import sys
 import tempfile
 import unittest
 from pathlib import Path
+from unittest import mock
 
 PROJECT_ROOT = Path(__file__).resolve().parent.parent
 #: The scripts under test, which committed allow rules name.
 REBASE = PROJECT_ROOT / ".agent" / "tools" / "rebase_links.py"
 INIT = PROJECT_ROOT / ".agent" / "skills" / "skill-creator" / "scripts" / "init_skill.py"
+#: The inbound module; TC-G19 loads it in this process (TASK 116 R7.4).
+SLOT = PROJECT_ROOT / ".agent" / "tools" / "slot_links.py"
+#: TC-G28 pins the slug grammar of `rebase_links.py` to this module's (TASK 116 R8.3).
+ARCHIVE_MOVE = PROJECT_ROOT / ".agent" / "tools" / "archive_move.py"
 LINKED = "[a](ARCHITECTURE.md)\n"
 REBASED = "[a](../ARCHITECTURE.md)\n"
 SUBTASK = "# Task 112-01: a\n\n[docs/TASK.md](../TASK.md)\n"
@@ -47,8 +73,57 @@
                           capture_output=True, text=True, timeout=60)
 
 
+def _module(path, name):
+    """A fresh module of `path`, loaded in this process; its siblings come from its directory."""
+    sys.path.insert(0, str(Path(path).parent))
+    try:
+        spec = importlib.util.spec_from_file_location(name, path)
+        module = importlib.util.module_from_spec(spec)
+        spec.loader.exec_module(module)
+        return module
+    finally:
+        sys.path.remove(str(Path(path).parent))
+
+
+def _swap(directory, outside):
+    """Swap `directory` for a link to `outside`; return the function that swaps it back."""
+    aside = directory.with_name(directory.name + ".aside")
+    directory.rename(aside)
+    directory.symlink_to(outside, target_is_directory=True)
+
+    def back():
+        directory.unlink()
+        aside.rename(directory)
+    return back
+
+
+def _writes(args, kwargs):
+    """True when a call of `os.open` (its flags) or of the built-in `open` (its mode) writes."""
+    spec = args[0] if args else kwargs.get("mode", kwargs.get("flags", "r"))
+    if isinstance(spec, str):
+        return any(c in spec for c in "wax+")
+    return bool(spec & (os.O_WRONLY | os.O_RDWR))
+
+
+def _move_out(directory, outside):
+    """Rename `directory` into `outside` and put a link to its new place in its stead."""
+    moved = outside / directory.name
+    directory.rename(moved)
+    directory.symlink_to(moved, target_is_directory=True)
+    return moved
+
+
+def _descriptor_path_known():
+    """True where the platform gives the path of a descriptor (TASK 116 R7.2)."""
+    try:
+        import fcntl
+    except ImportError:
+        fcntl = None
+    return hasattr(fcntl, "F_GETPATH") or os.path.isdir("/proc/self/fd")
+
+
 class TestRebaseLinksGuard(unittest.TestCase):
-    """TC-G1 to TC-G3."""
+    """TC-G1 to TC-G3, TC-G7, TC-G13 to TC-G18 and TC-G20 to TC-G30 (TASK 116)."""
 
     def setUp(self):
         self.root = _tmp(self)
@@ -65,6 +140,9 @@
         victim.write_text(LINKED, encoding="utf-8")
         result = self.rebase(victim)
         self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        # TASK 116 R1.1 and R8.2 run after the checks of TASK 112, so the first one names the
+        # refusal on every platform.
+        self.assertIn("lies outside the working directory", result.stderr)
         self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
 
     def test_g2_a_link_a_second_hard_link_or_git(self):
@@ -106,6 +184,8 @@
             (self.root / "fl").symlink_to(firm, target_is_directory=True)
             result = self.rebase("fl/y.md")
             self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+            # TASK 116 R1.1 runs after the check of `.git`, so that check names the refusal.
+            self.assertIn("lies under .git/", result.stderr)
         self.assertEqual(hook.read_text(encoding="utf-8"), LINKED)
 
     def test_g7_one_refused_operand_stops_every_write(self):
@@ -126,9 +206,430 @@
         self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
         self.assertEqual(moved.read_text(encoding="utf-8"), REBASED)
 
+    def test_g13_a_directory_that_resolves_outside(self):
+        # base-fail: the base writes through the directory link.
+        victim = self.outside / "victim.md"
+        victim.write_text(LINKED, encoding="utf-8")
+        (self.root / "docs" / "out").symlink_to(self.outside, target_is_directory=True)
+        result = self.rebase("docs/out/victim.md")
+        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        self.assertIn("resolves outside", result.stderr)
+        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
+
+    def test_g14_a_directory_link_that_resolves_inside(self):
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+        (self.root / "docs" / "in").symlink_to(self.root / "docs" / "tasks",
+                                               target_is_directory=True)
+        result = self.rebase("docs/in/t.md")
+        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
+        self.assertEqual(moved.read_text(encoding="utf-8"), REBASED)
+
+    def test_g15_a_parent_segment_after_a_directory_link(self):
+        # base-fail: the kernel resolves the link before the `..`; a lexical check does not.
+        victim = self.outside / "victim.md"
+        victim.write_text(LINKED, encoding="utf-8")
+        (self.outside / "sub").mkdir()
+        (self.root / "docs" / "up").symlink_to(self.outside / "sub", target_is_directory=True)
+        result = self.rebase("docs/up/../victim.md")
+        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        self.assertIn("resolves outside", result.stderr)
+        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
+
+    def inprocess(self, operand, hooks, before=None):
+        """`_main` of `REBASE` in this process, with `hooks(real)` wrapping each kind of open.
+
+        `operand` is one operand or a list of them. The script is loaded fresh before `before`
+        runs, so a case can change `os` for the run alone. Returns the exit code and the text of
+        stderr.
+        """
+        module = _module(REBASE, "rebase_links_under_test")
+        err, cwd = io.StringIO(), os.getcwd()
+        os.chdir(self.root)
+        try:
+            with contextlib.ExitStack() as stack:
+                if before:
+                    stack.enter_context(before())
+                stack.enter_context(mock.patch("os.open", hooks(os.open)))
+                stack.enter_context(mock.patch("builtins.open", hooks(builtins.open)))
+                stack.enter_context(contextlib.redirect_stderr(err))
+                stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
+                operands = [operand] if isinstance(operand, str) else list(operand)
+                code = module._main([*operands, "--from", "docs", "--to", "docs/tasks"])
+        finally:
+            os.chdir(cwd)
+        return code, err.getvalue()
+
+    def test_g16_a_directory_swapped_around_the_open(self):
+        # base-fail: the base reads and writes the outside file through the swapped directory.
+        inside = self.root / "docs" / "x"
+        inside.mkdir()
+        (inside / "t.md").write_text(LINKED, encoding="utf-8")
+        victim = self.outside / "t.md"
+        victim.write_text(LINKED, encoding="utf-8")
+        target = str(inside / "t.md")
+
+        def hooks(real):
+            def opener(path, *args, **kwargs):
+                if os.path.abspath(path) != target:
+                    return real(path, *args, **kwargs)
+                back = _swap(inside, self.outside)
+                try:
+                    return real(path, *args, **kwargs)
+                finally:
+                    back()
+            return opener
+        code, err = self.inprocess("docs/x/t.md", hooks)
+        self.assertEqual(code, 2, err)
+        self.assertIn("is not the file at its real path", err)
+        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
+        self.assertEqual((inside / "t.md").read_text(encoding="utf-8"), LINKED)
+
+    def test_g17_a_file_swapped_for_a_link(self):
+        # base-fail: the base follows the planted link. The inside link needs O_NOFOLLOW itself.
+        other = self.root / "docs" / "other.md"
+        for name, target in (("outside", self.outside / "v.md"), ("inside", other)):
+            with self.subTest(link=name):
+                target.write_text(LINKED, encoding="utf-8")
+                operand = self.root / "docs" / "tasks" / f"{name}.md"
+                operand.write_text(LINKED, encoding="utf-8")
+
+                def hooks(real, operand=operand, target=target):
+                    def opener(path, *args, **kwargs):
+                        if os.path.abspath(path) == str(operand) and not operand.is_symlink():
+                            operand.unlink()
+                            operand.symlink_to(target)
+                        return real(path, *args, **kwargs)
+                    return opener
+                code, err = self.inprocess(f"docs/tasks/{name}.md", hooks)
+                self.assertEqual(code, 2, err)
+                self.assertIn("cannot open it", err)
+                self.assertEqual(target.read_text(encoding="utf-8"), LINKED)
+
+    def test_g18_a_second_hard_link_before_the_open(self):
+        # base-fail: the base writes through the shared inode.
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+        alias = self.outside / "alias.md"
+
+        def hooks(real):
+            def opener(path, *args, **kwargs):
+                if os.path.abspath(path) == str(moved) and not alias.exists():
+                    os.link(moved, alias)
+                return real(path, *args, **kwargs)
+            return opener
+        code, err = self.inprocess("docs/tasks/t.md", hooks)
+        self.assertEqual(code, 2, err)
+        self.assertIn("has 2 hard links", err)
+        self.assertEqual(alias.read_text(encoding="utf-8"), LINKED)
+
+    def test_g20_a_second_hard_link_before_the_write(self):
+        # base-fail: the base writes through the shared inode; R7.3 re-checks the link count.
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+        alias = self.outside / "alias.md"
+
+        def hooks(real):
+            def opener(path, *args, **kwargs):
+                if (os.path.abspath(path) == str(moved) and _writes(args, kwargs)
+                        and not alias.exists()):
+                    os.link(moved, alias)
+                return real(path, *args, **kwargs)
+            return opener
+        code, err = self.inprocess("docs/tasks/t.md", hooks)
+        self.assertEqual(code, 2, err)
+        self.assertIn("has 2 hard links", err)
+        self.assertEqual(alias.read_text(encoding="utf-8"), LINKED)
+        self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)
+
+    def test_g21_a_file_replaced_after_the_read(self):
+        # base-fail: the base writes the rebased old text over the new file.
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+        fresh = "# fresh\n"
+        replaced = []
+
+        def hooks(real):
+            def opener(path, *args, **kwargs):
+                if (os.path.abspath(path) == str(moved) and _writes(args, kwargs)
+                        and not replaced):
+                    replaced.append(True)
+                    new = moved.with_name("t.md.new")
+                    new.write_text(fresh, encoding="utf-8")
+                    os.replace(new, moved)
+                return real(path, *args, **kwargs)
+            return opener
+        code, err = self.inprocess("docs/tasks/t.md", hooks)
+        self.assertEqual(code, 2, err)
+        self.assertIn("changed during the run", err)
+        self.assertEqual(moved.read_text(encoding="utf-8"), fresh)
+
+    def test_g22_a_platform_with_no_o_nofollow(self):
+        # base-fail: the base file mode needs no O_NOFOLLOW, so it rewrites the file.
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+
+        @contextlib.contextmanager
+        def no_o_nofollow():
+            saved = os.O_NOFOLLOW
+            del os.O_NOFOLLOW
+            try:
+                yield
+            finally:
+                os.O_NOFOLLOW = saved
+        code, err = self.inprocess("docs/tasks/t.md", lambda real: real, before=no_o_nofollow)
+        self.assertEqual(code, 2, err)
+        self.assertIn("this platform has no O_NOFOLLOW", err)
+        self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)
+
+    def test_g23_a_directory_moved_out_and_linked_back(self):
+        # base-fail: the file keeps its inode, so only the directory check refuses it.
+        inside = self.root / "docs" / "x"
+        inside.mkdir()
+        (inside / "t.md").write_text(LINKED, encoding="utf-8")
+        target, moved = str(inside / "t.md"), []
+
+        def hooks(real):
+            def opener(path, *args, **kwargs):
+                if os.path.abspath(path) == target and not moved:
+                    moved.append(_move_out(inside, self.outside))
+                return real(path, *args, **kwargs)
+            return opener
+        code, err = self.inprocess("docs/x/t.md", hooks)
+        self.assertEqual(code, 2, err)
+        self.assertIn("its directory resolves outside the working directory", err)
+        self.assertEqual((moved[0] / "t.md").read_text(encoding="utf-8"), LINKED)
+
+    def test_g24_a_failed_write_leaves_a_prefix_of_the_new_text(self):
+        # base-fail: the base writes through a file object, so the hook never fires: exit 0.
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+        real_write = os.write
+
+        def full_disk(fd, data):
+            real_write(fd, bytes(data[:5]))
+            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC))
+
+        @contextlib.contextmanager
+        def failing_write():
+            with mock.patch("os.write", full_disk):
+                yield
+        code, err = self.inprocess("docs/tasks/t.md", lambda real: real, before=failing_write)
+        self.assertEqual(code, 2, err)
+        self.assertEqual(moved.read_bytes(), REBASED.encode("utf-8")[:5])
+
+    @unittest.skipUnless(hasattr(os, "mkfifo"), "no os.mkfifo")
+    def test_g25_a_fifo_operand(self):
+        # base-fail: the base rewrites the first operand, then blocks on the open of the FIFO.
+        first = self.root / "docs" / "tasks" / "t.md"
+        first.write_text(LINKED, encoding="utf-8")
+        os.mkfifo(self.root / "docs" / "tasks" / "f.md")
+        try:
+            result = subprocess.run([sys.executable, str(REBASE), "docs/tasks/t.md",
+                                     "docs/tasks/f.md", "--from", "docs", "--to", "docs/tasks"],
+                                    cwd=self.root, capture_output=True, text=True, timeout=30)
+        except subprocess.TimeoutExpired:
+            self.fail("the open of the FIFO blocked")
+        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        self.assertIn("is not a regular file", result.stderr)
+        # TASK 116 R7.1: every operand is opened before any is read or written.
+        self.assertEqual(first.read_text(encoding="utf-8"), LINKED)
+
+    @unittest.skipUnless(os.path.isdir("/dev/fd"), "no /dev/fd")
+    def test_g26_no_descriptor_stays_open(self):
+        # Passes at the base, which closes each file it opens.
+        moved = self.root / "docs" / "tasks" / "t.md"
+        second = self.root / "docs" / "tasks" / "u.md"
+        alias = self.outside / "alias.md"
+
+        def hooks(real):
+            def opener(path, *args, **kwargs):
+                if os.path.abspath(path) == str(second) and not alias.exists():
+                    os.link(second, alias)
+                return real(path, *args, **kwargs)
+            return opener
+        for operands in (["docs/tasks/t.md"], ["docs/tasks/t.md", "docs/tasks/u.md"]):
+            with self.subTest(operands=operands):
+                moved.write_text(LINKED, encoding="utf-8")
+                second.write_text(LINKED, encoding="utf-8")
+                gc.collect()
+                before = sorted(os.listdir("/dev/fd"))
+                code, err = self.inprocess(operands, hooks)
+                self.assertIn(code, (0, 2), err)
+                self.assertEqual(sorted(os.listdir("/dev/fd")), before)
+        self.assertTrue(alias.exists(), "the hook made no second link")
+
+    @unittest.skipUnless(_descriptor_path_known(), "no descriptor path on this platform")
+    def test_g27_three_swaps_around_the_identity_check(self):
+        # base-fail: the base reads and writes the outside file through the swapped directory.
+        inside = self.root / "docs" / "x"
+        inside.mkdir()
+        (inside / "t.md").write_text(LINKED, encoding="utf-8")
+        victim = self.outside / "t.md"
+        victim.write_text(LINKED, encoding="utf-8")
+        target, state = str(inside / "t.md"), {"swaps": 0}
+
+        def hooks(real):
+            def opener(path, *args, **kwargs):
+                if os.path.abspath(path) == target and "opened" not in state:
+                    state["opened"], state["back"] = True, _swap(inside, self.outside)
+                return real(path, *args, **kwargs)
+            return opener
+
+        @contextlib.contextmanager
+        def swaps_around_realpath():
+            real_realpath = os.path.realpath
+
+            def realpath(path, *args, **kwargs):
+                if "back" not in state or os.path.abspath(path) != target:
+                    return real_realpath(path, *args, **kwargs)
+                state.pop("back")()
+                state["swaps"] += 1
+                try:
+                    return real_realpath(path, *args, **kwargs)
+                finally:
+                    state["back"] = _swap(inside, self.outside)
+            try:
+                with mock.patch("os.path.realpath", realpath):
+                    yield
+            finally:
+                if "back" in state:
+                    state.pop("back")()
+        code, err = self.inprocess("docs/x/t.md", hooks, before=swaps_around_realpath)
+        self.assertEqual(code, 2, err)
+        self.assertIn("its directory resolves outside the working directory", err)
+        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
+        self.assertGreaterEqual(state["swaps"], 1, "the realpath hook never swapped")
+
+    def test_g28_a_slot_map_of_another_form(self):
+        # base-fail: the base writes any archive text over the slot link.
+        moved = self.root / "docs" / "tasks" / "t.md"
+        text = LINKED + "[t](TASK.md)\n[p](PLAN.md)\n"
+        refused = (("docs/NOTES.md=docs/tasks/task-116-x.md", "its slot is not"),
+                   ("docs/TASK.md=.agent/tools/x.py", "its archive is not"),
+                   ("docs/TASK.md=docs/plans/plan-116-x.md", "its archive is not"),
+                   ("docs/PLAN.md=docs/tasks/task-116-x.md", "its archive is not"),
+                   ("docs/TASK.md=docs/tasks/task-16-x.md", "its archive is not"),
+                   ("docs/TASK.md=docs/tasks/task-116-x.md\nevil", "its archive is not"),
+                   # a slug outside the grammar of `archive_move.SLUG`
+                   ("docs/TASK.md=docs/tasks/task-116-a b.md", "its archive is not"),
+                   ("docs/TASK.md=docs/tasks/task-116-A:b.md", "its archive is not"))
+        for pair, reason in refused:
+            with self.subTest(pair=pair):
+                moved.write_text(text, encoding="utf-8")
+                result = _run(REBASE, ["docs/tasks/t.md", "--from", "docs", "--to", "docs/tasks",
+                                       "--slot", pair], self.root)
+                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+                error = json.loads(result.stderr.strip().splitlines()[-1])["error"]
+                self.assertIn(reason, error)
+                self.assertIn(repr(pair), error)
+                self.assertEqual(moved.read_text(encoding="utf-8"), text)
+        for pair in ("docs/TASK.md=docs/tasks/task-116-x.md",
+                     "docs/PLAN.md=docs/plans/plan-116-x.md"):
+            with self.subTest(pair=pair):
+                moved.write_text(text, encoding="utf-8")
+                result = _run(REBASE, ["docs/tasks/t.md", "--from", "docs", "--to", "docs/tasks",
+                                       "--slot", pair], self.root)
+                self.assertIn(result.returncode, (0, 3), result.stdout + result.stderr)
+                self.assertIn("../ARCHITECTURE.md", moved.read_text(encoding="utf-8"))
+        grammar = re.compile(r'^_?SLUG = (r".*")$', re.M)
+        ours = grammar.search(Path(REBASE).read_text(encoding="utf-8"))
+        self.assertIsNotNone(ours, "rebase_links.py holds no slug grammar")
+        self.assertEqual(ours.group(1),
+                         grammar.search(ARCHIVE_MOVE.read_text(encoding="utf-8")).group(1))
+
+    def test_g29_an_operand_that_is_not_markdown_under_docs(self):
+        # base-fail: the base rewrites a link-shaped token in a file of any kind, anywhere.
+        for operand, reason in (("docs/tasks/t.py", "is not a markdown file"),
+                                ("CLAUDE.md", "does not lie under docs/"),
+                                # the normalised operand, not the operand as written
+                                ("docs/../CLAUDE.md", "does not lie under docs/"),
+                                # fails both checks: the check of `docs/` comes first
+                                ("notes.txt", "does not lie under docs/")):
+            with self.subTest(operand=operand):
+                path = self.root / operand
+                path.write_text(LINKED, encoding="utf-8")
+                result = self.rebase(operand)
+                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+                self.assertIn(reason, result.stderr)
+                self.assertEqual(path.read_text(encoding="utf-8"), LINKED)
+
+    def test_g30_options_and_rewritten_links_stay_in_the_tree(self):
+        # base-fail: the base builds the link from any --repo-root, --from and --to.
+        docs = self.root / "docs"
+        moved = docs / "tasks" / "t.md"
+        slot = ["--slot", "docs/TASK.md=docs/tasks/task-116-x.md"]
+        with_slot = LINKED + "[t](TASK.md)\n"
+        for name in ("x y", "a:b", "a)b", "plain-words"):
+            (docs / name).mkdir()
+            (docs / name / "ARCHITECTURE.md").write_text("# a\n", encoding="utf-8")
+        for name in ("a b/x y.md", "m n/a.md", 'href="x.md"', "x.md"):
+            (docs / name).parent.mkdir(exist_ok=True)
+            (docs / name).write_text("# a\n", encoding="utf-8")
+        text_held = "holds text that its authored link does not"
+        part_held = "holds a path part that its authored link does not"
+        refused = (
+            # (--from, --to, other options, the operand's text, the reason)
+            ("docs", "docs/tasks", ["--repo-root", str(self.root / "nowhere")] + slot, with_slot,
+             "--repo-root is not the working directory"),
+            ("docs", "docs/tasks", ["--repo-root", str(self.outside)] + slot, with_slot,
+             "--repo-root is not the working directory"),
+            ("docs", "../w", slot, with_slot, "--to does not lie inside the working directory"),
+            # R8.6 compares the normalised form
+            ("docs", "docs/../../w", slot, with_slot,
+             "--to does not lie inside the working directory"),
+            (str(self.outside), "docs/tasks", slot, with_slot,
+             "--from does not lie inside the working directory"),
+            # TASK 116 R8.7: the space of `docs/x y` would enter the link
+            ("docs/x y", "docs/tasks", [], LINKED, text_held),
+            # a colon and a bracket too: R8.7 counts every character outside its safe set
+            ("docs/a:b", "docs/tasks", [], LINKED, text_held),
+            ("docs/a)b", "docs/tasks", [], LINKED, text_held),
+            # a dry run makes the check too
+            ("docs/x y", "docs/tasks", ["--dry-run"], LINKED, text_held),
+            # each character is counted: a second space is one too many
+            ("docs/a b", "docs/tasks", [], "[a](<x y.md>)\n", text_held),
+            # a path part that the author did not write, of safe characters or of others
+            ("docs/plain-words", "docs/tasks", [], LINKED, part_held),
+            ("docs/m n", "docs/tasks", [], "[a](<q r/../a.md>)\n", part_held),
+            ("docs/plain-words", "docs/tasks", ["--dry-run"], LINKED, part_held),
+            # two links spliced one into the other: the text gains a quote
+            ("docs", "docs/tasks", [], '[a](href="x.md")\n',
+             "the rewritten text holds a character that the text did not"),
+            ("docs", "docs/tasks", ["--dry-run"], '[a](href="x.md")\n',
+             "the rewritten text holds a character that the text did not"))
+        for from_dir, to_dir, extra, text, reason in refused:
+            with self.subTest(from_dir=from_dir, to_dir=to_dir, extra=extra, text=text):
+                moved.write_text(text, encoding="utf-8")
+                result = _run(REBASE, ["docs/tasks/t.md", "--from", from_dir, "--to", to_dir,
+                                       *extra], self.root)
+                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+                self.assertIn(reason, result.stderr)
+                self.assertEqual(moved.read_text(encoding="utf-8"), text)
+        other = docs / "tasks" / "ARCHITECTURE.md"
+        other.write_text("# b\n", encoding="utf-8")
+        for from_dir, reason in (("docs/x y", text_held), ("docs/plain-words", part_held)):
+            # an ambiguous rebase: the target exists under --to as well
+            with self.subTest(ambiguous=from_dir):
+                moved.write_text(LINKED, encoding="utf-8")
+                result = _run(REBASE, ["docs/tasks/t.md", "--from", from_dir, "--to",
+                                       "docs/tasks"], self.root)
+                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+                self.assertIn(reason, result.stderr)
+                self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)
+        other.unlink()
+        with self.subTest(kept="a link authored with a space"):
+            # passes at the base: R8.7 refuses only what the rewrite adds
+            (docs / "sp ace.md").write_text("# a\n", encoding="utf-8")
+            moved.write_text("[a](<sp ace.md>)\n", encoding="utf-8")
+            result = self.rebase("docs/tasks/t.md")
+            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
+            self.assertEqual(moved.read_text(encoding="utf-8"), "[a](<../sp ace.md>)\n")
+
 
 class TestInboundGuard(unittest.TestCase):
-    """TC-G8 to TC-G12: `--inbound` writes only regular files with one hard link (TASK 115).
+    """TC-G8 to TC-G12 (TASK 115) and TC-G19 (TASK 116 R7.4): `--inbound` writes only regular
+    files with one hard link, through the descriptor it checked.
 
     The root holds no git repository, so the script walks it. An own link is a slot link in a
     sub-task file of task 112.
@@ -226,6 +727,74 @@
         self.assertFalse(sentinel.exists(), "a .pyc planted in __pycache__/ was read")
         self.assertEqual(os.listdir(cache), [cached.name])
 
+    def write_through(self, module, case):
+        """`_write_file` of `docs/<case>/t.md` given the identity and bytes of the file the hooks
+        of `case` put in its place. Returns the refusal, that file, its bytes before the call, and
+        the count of swaps around `os.path.realpath`.
+
+        `swap`: the directory is swapped for a link to `outside/<case>` around the open. `move`:
+        the directory is moved into `outside` and linked back. `three`: the swaps of TC-G27.
+        """
+        inside, away = self.root / "docs" / case, self.outside / case
+        inside.mkdir()
+        (inside / "t.md").write_text(SUBTASK, encoding="utf-8")
+        if case != "move":
+            away.mkdir()
+            (away / "t.md").write_text(SUBTASK, encoding="utf-8")
+        source = (inside if case == "move" else away) / "t.md"
+        original, st = source.read_bytes(), source.stat()
+        target, state = str(inside / "t.md"), {"swaps": 0}
+        real_open, real_realpath = os.open, os.path.realpath
+
+        def opener(path, *args, **kwargs):
+            if os.path.abspath(path) != target or "opened" in state:
+                return real_open(path, *args, **kwargs)
+            state["opened"] = True
+            if case == "move":
+                _move_out(inside, self.outside)
+                return real_open(path, *args, **kwargs)
+            state["back"] = _swap(inside, away)
+            try:
+                return real_open(path, *args, **kwargs)
+            finally:
+                if case == "swap":
+                    state.pop("back")()
+
+        def realpath(path, *args, **kwargs):
+            if case != "three" or "back" not in state or path != target:
+                return real_realpath(path, *args, **kwargs)
+            state.pop("back")()
+            state["swaps"] += 1
+            try:
+                return real_realpath(path, *args, **kwargs)
+            finally:
+                state["back"] = _swap(inside, away)
+        try:
+            with mock.patch("os.open", opener), mock.patch("os.path.realpath", realpath):
+                refusal = module._write_file(str(self.root), f"docs/{case}/t.md", original,
+                                             (st.st_dev, st.st_ino), RETARGETED.encode("utf-8"))
+        finally:
+            if "back" in state:
+                state.pop("back")()
+        return refusal, away / "t.md", original, state["swaps"]
+
+    def test_g19_a_directory_swapped_around_the_inbound_open(self):
+        # base-fail: the base writes the outside file; its post-write check refuses only a swap.
+        module = _module(SLOT, "slot_links_under_test")
+        reasons = {"swap": "is not the file at its real path",
+                   "move": "its directory resolves outside the working directory",
+                   "three": "its directory resolves outside the working directory"}
+        for case, reason in reasons.items():
+            with self.subTest(case=case):
+                if case == "three" and not _descriptor_path_known():
+                    self.skipTest("no descriptor path on this platform")
+                refusal, victim, original, swaps = self.write_through(module, case)
+                self.assertIsNotNone(refusal)
+                self.assertEqual(refusal.reason, reason)
+                self.assertEqual(victim.read_bytes(), original)
+                if case == "three":
+                    self.assertGreaterEqual(swaps, 1, "the realpath hook never swapped")
+
 
 class TestInitSkillGuard(unittest.TestCase):
     """TC-G4 to TC-G6."""
diff --git a/.agent/skills/skill-safe-commands/SKILL.md b/.agent/skills/skill-safe-commands/SKILL.md
--- a/.agent/skills/skill-safe-commands/SKILL.md
+++ b/.agent/skills/skill-safe-commands/SKILL.md
@@ -2,7 +2,7 @@
 name: skill-safe-commands
 description: "Centralized list of commands safe for auto-execution without user approval. Single source of truth."
 tier: 0
-version: 1.4
+version: 1.5
 ---
 # Safe Commands Protocol
 
@@ -23,7 +23,7 @@
 | **Archiving** | `python3 .agent/tools/archive_move.py` | Moves `docs/TASK.md` and `docs/PLAN.md` into `docs/tasks/` and `docs/plans/`; refuses every other operand (TASK 112) |
 | **Directory** | `mkdir -p docs/tasks`, `mkdir -p docs/plans`, `mkdir -p docs/architectures` | Idempotent; three fixed directories |
 | **Tool calls** | `generate_task_archive_filename`, `list_directory`, `read_file` | Native tools |
-| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py`, `python3 .agent/skills/artifact-formalizer/evals/grade_run.py`, `python3 System/scripts/doctor.py` | Framework automation; `rebase_links.py` and `init_skill.py` write only inside the working directory, compared without resolving links |
+| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py`, `python3 .agent/skills/artifact-formalizer/evals/grade_run.py`, `python3 System/scripts/doctor.py` | Framework automation; `rebase_links.py` writes markdown in the working directory by real path, `init_skill.py` by path |
 | **Testing** | `python -m pytest`, `python3 -m pytest`, `npm test`, `cargo test`, with no argument | Their options can run a program, delete a directory or overwrite a file (TASK 111 D14) |
 
 > [!IMPORTANT]
~~~~

**The apply (H1 steps 4 and 5).** `git apply --whitespace=nowarn` of the patch exited 0. Then:
`rebase_links.py` hashes to `5a9fdf76b771…` and `slot_links.py` to `2e5ffe0ee7e6…`, the values of
their copies; both copies are gone; `git apply --check -R` passes. `.claude/settings.json` holds
`allow` and `deny`, the deny list of TASK §10.1, and `skill-safe-commands` is version 1.5.

### H2 — the gates of stage 3

- `run_gates.sh`: every gate passes; the CI pytest list 526, the tool suite 255. The curated
  suite: 568 tests, OK, with the patch's new cases. The two patched modules: 56 passed.
- `validate_skill.py` exits 0 for `skill-safe-commands`. `analyze_gaps.py` reports B0's gap and
  its 7 advisories, no more.
- `regcheck.py` on `skill-safe-commands`: one `WARN` on an added line, the base `cell_width` of
  the command cell.
- `check_positional_refs.py --targets-changed`: the same 9 errors as before the apply; none is a
  `REFERENT_MOVED` or a `REFERENT_ABSENT` that the patch causes.
- The dry run of TASK §13 item 5: the two `INBOUND` records of R3.5, now
  `CHANGELOG.md:3191` and `CHANGELOG.ru.md:3196`; 3 slot links in archived documents; exit 3.
  The fingerprint `725bacc32dd7` was the same before and after.
- `git status` lists 28 entries, each declared.

### I1 — stage 4

Both agents, resumed, read the applied tree at fingerprint `a7c0616f9b6c` and quoted it at their
start and end; the caller recomputed it at each return: equal. Probe prefixes `s4-code-116.` and
`s4-sec-116.`, each removed.

- **Code review: APPROVED.** The six modified files equal the patch applied to the base, and both
  copies are gone. Against the final code, subprocess cases included: the tool suite 255; the two
  patched modules with `test_slot_links.py` and `test_archive_protocol.py`, 183; the curated suite
  568, OK. Dry runs of both modes agree with the base. NIT: a reflow of §11, applied.
- **Security audit: PASS.** No finding of any severity but INFO. The installed modules and settings
  equal base plus patch, byte for byte; `allow`, `env` and `hooks` are as at the base. Every route
  of rounds 4 to 7 is refused by the installed script, and the archive steps and Step 8 are
  accepted. The four residuals found are those of TASK §11 and WI-47. I1: `ARCHITECTURE.md`'s
  sentence of TASK 112 now names the exceptions of §11; applied.

Scratch files deleted after I1, per the inventory: `copy_runner.py`, `copies_driver.py`,
`mutation_driver.py`, `gen_stage3_patch.py`, `basefail_driver.py`, `fix_round5.py`,
`fix_round6.py`, `fix_round7.py`, `docs_l5.py`, `docs_m5.py` and `docs_n5.py`.

### I2 — the probe of TASK R4.7

`git status --porcelain -- README.md` printed nothing. The tree fingerprint was `b46e3de80ee9`
before the three probes and after them. Each probe ran as its own command in the orchestrator's
session:

| Command | Outcome |
| :--- | :--- |
| `git stash list` | refused by Claude Code: "Permission to use Bash with command git stash list has been denied." |
| `git status && git stash list` | refused as a whole, the same message; `git status` did not run either |
| `git restore --source=c8aba597ed06545a8fc0933238aaa4510f059db2 --staged --worktree -- README.md` | not refused; exit 0, and `README.md` is unchanged |

The deny list takes effect in the running session, alone and inside a compound command, and it
lets the restore of `framework-upgrade` §5 through. WI-45 stays `done`.

## Retro (`run-feedback` §7)

The claim `framework-upgrade-archive-hardening-and-git-deny-rules`, taken in §0, was this run's.
The one question listed four observed candidates; the operator chose "Раунды ревью без конца".

- Collected as `fnd-20261008-233928-ecc494cb` (user-friction). Triage's duplicate candidate,
  REG-17, is a fixed register defect, not the same. No open or resolved work-item covers a bound
  on the review of stage 2; TASK 111's review rounds 7 to 9 are a recurrence.
- Filed as **WI-48**, "Stage 2 of framework-upgrade has no bound on its review rounds", effort `S`:
  a behaviour change of a shared workflow, for the framework owner's review. Its index line is in
  `docs/BACKLOG.md`.
- The claim is released.

## J1 — restart

After the retro every gate passes again, and `git status` lists 29 entries, each declared
(WI-48 is the retro's). The last scratch files of the inventory, `fp.sh`, `run_gates.sh`,
`refs-living.log` and `regcheck.py`, are deleted. A TIER 0 skill (`skill-safe-commands` 1.5) and
the committed permission rules changed, so the operator restarts the session
(`framework-upgrade` §4.3). Nothing is committed: the operator commits.
