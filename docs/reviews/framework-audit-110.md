# Framework Audit 110 — Figure-instrument follow-ups, the renderer supply chain, plan status and fix-round rules

- **Task:** 110 `figure-instrument-follow-ups`. It archives to
  `docs/tasks/task-110-figure-instrument-follow-ups.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1,
  Modes A and B.
- **Date:** 2026-10-05. **Base revision:** `6ae772bea1c7ce702bc161f9046e875a599d69cc`, clean tree
  at start.
- **Source:** WI-32, WI-30, WI-22 and WI-27, with the operator's choice of 2026-10-05.
- **Independence:** each audit round ran in a separate read-only agent. Same-model agreement is
  corroboration, not independent confirmation.

## 0. Emergency Bypass

None set.

## Mode A — SPECIFICATION AUDIT

### Round 1 — FAIL (1 BLOCKING, 9 MAJOR, 12 MINOR)

Reviewer: `task-reviewer`, on TASK revision 2. No tree fingerprint was in the brief, so the round
is not pinned to a tree state.

| Id | Severity | Finding | Revision 3 |
| :--- | :--- | :--- | :--- |
| TR-01 | BLOCKING | A4 cannot hold for R5 and R4.3: both pass on the base code by design | A4 splits; R5.3 and mutations 5 and 6 |
| TR-02 | MAJOR | the R4.3 oracle misses `code_line_reader` | R4.3 adds it; the fuzz compares it |
| TR-03 | MAJOR | no performance number | R4.4: 0.5 s and 0.25 s; A8 growth ≤ 2.5 |
| TR-04 | MAJOR | tree-hash recipe, `MERMAID_RENDER_CHROME` directory, floor, existing tests | R7.3 recipe; A7 cases; D5 floor |
| TR-05 | MAJOR | A6 passes by construction; headless switch; audit level | A6 against base fixtures; R7.1; R7.2 |
| TR-06 | MAJOR | vdd-05 never sets `in-progress` | R8.2 Step A; failure path |
| TR-07 | MAJOR | no skill-absent path; old PLANs without status | R8.1, R8.3 |
| TR-08 | MAJOR | the VDD review path loads no checklist | D8 states the gap; R9.3 |
| TR-09 | MAJOR | sub-features without a criterion | A13 |
| TR-10 | MAJOR | R9.4 corpus undefined for `svg_geometry.py` | R9.4 per instrument |
| TR-11 | MINOR | vdd-05 numbers two steps "6." | R8.6; others out of scope |
| TR-12 | MINOR | the "no status" statements not listed | §1 lists six; R8.5 |
| TR-13 | MINOR | the crossing function returns below 3 lifelines | R1.1 |
| TR-14 | MINOR | 12.1.0 crosses from 24 characters | D2, R1.4 |
| TR-15 | MINOR | other negatives that fail the gate | R1.3 generalised |
| TR-16 | MINOR | departures from the WIs not all listed | §5 lists six |
| TR-17 | MINOR | no path for the table and the report | R7.4, R7.6 |
| TR-18 | MINOR | ARCHITECTURE §10.7, §10.8 and the §10.6 pin | R10.6 |
| TR-19 | MINOR | the grader regex runs on model output | R6.1 time bound |
| TR-20 | MINOR | "done only after review" cannot be checked at plan review | R8.4 narrowed |
| TR-21 | MINOR | no fix round, nothing to measure; "verifier" undefined | R10.4 |
| TR-22 | MINOR | a file-type spelling | moot: the details left the repository (review round 2) |
| TR-23 | MINOR | the vdd-03 loop window | R8.2 last item |

**Measured for TR-02.** The prototype scanner against the base scanner over 30,000 generated
documents: spans, comments, plain lines and the per-line answer of `code_line_reader` are equal in
every document. The generator reaches every scanner branch except `_list_item`'s indent check,
which no input of `_scan` reaches (R5.2).

### Round 2 — PASS, with comments

Reviewer: `task-reviewer`, on TASK revision 3. Tree fingerprint `a447d578f583` quoted by the
reviewer; recomputed by the orchestrator at the return: equal. Scan 0 warn; resolver 25 of 25.

- Round 1: 21 findings resolved, TR-09 and TR-16 partial.
- New: 3 MAJOR, 13 MINOR. Revision 4 applies each:
  - TR2-01: R8.2 re-entry after `done`; R8.3 "a status edit changes the value", no entry added;
  - TR2-02: A13 names the wiring pins for R8.2–R8.4, R8.6 and the `update_state.py` flags;
  - TR2-03: R7.7, the install stamp that `render_check.py` checks, and D10's changelog line;
  - TR2-04: R7.8; TR2-05: the path convention of §1; TR2-06: D11; TR2-07: the R10.6 row;
  - TR2-08: R7.3 symlink, dry run and exit code; TR2-09: D5 trust on first use;
  - TR2-10: R4.4 times; TR2-11: UC-6; TR2-12: A5; TR2-13: R9.1 terms;
  - TR2-14: §7 `framework-upgrade`; TR2-15: the R4.3 oracle; TR2-16: R7.1.

## Mode B — PLAN AUDIT

### Round 1 — FAIL (1 BLOCKING, 5 MAJOR, 15 MINOR)

Reviewer: `plan-reviewer`, on PLAN revision 1 against TASK revision 2. No fingerprint in the
brief. PLAN revision 2 applies each finding:

| Id | Severity | Finding | PLAN revision 2 |
| :--- | :--- | :--- | :--- |
| P1 | BLOCKING | a regrade can rewrite a `grading.json` with no verdict moved | E1 byte diff; declared before E2; `GRADER_VERSION` stays |
| P2 | MAJOR | shared files; missing dependencies of the fixtures task | clusters A1, A2, B in order; D after A2, B, C, F |
| P3 | MAJOR | the default render home lies outside the repository | D renders from a scratch home; the default home is the operator's step |
| P4 | MAJOR | `eval-results.md` quotes the report | declared on the grading condition |
| P5 | MAJOR | the gate-name pin is in `test_render_check.py` | declared; B1 points there |
| P6 | MAJOR | where reviews are stored | in this audit |
| P7–P21 | MINOR | 15 items, listed below the table | in the PLAN items named below |

**P7–P21.**

- P7: `expected.json` declared. P8: B1 tests old metrics. P9: C1 updates the v10 pin.
- P10: D2 regenerates the plan fixture through `test_plan_gantt.py`.
- P11: H1 edits ARCHITECTURE §10.6 and §10.8. P12: F1 tests R8.6.
- P13: cluster A splits in three. P14: F3 keeps vdd-03 Step 3 and cites TASK R8.2.
- P15: the PLAN maps A8, A10, A11 and the use cases.
- P16: H5 runs the resolver after the last fix; D runs again after an instrument fix.
- P17: D4 records the external figures. P18: the time bounds keep a margin of 10 or more.
- P19: PLANs 107 to 109 had no task files either. P20: TASK revisions 3 and 4 hold it.
- P21: the header follows TASK revision 4.

**P17, measured.** The sequence figures outside the skill, rendered and read by the prototype gate:
`docs/presentation/FRAMEWORK_EVOLUTION.md` has one own-end crossing, on the self-message
`Agent->>Agent`, which stays a `warn` (D2). `brainstorming/examples/demo_complex.md` has none.

### Round 2 — PASS, with comments

Reviewer: `plan-reviewer`, on PLAN revision 2 against TASK revision 4. Tree fingerprint
`c47eca7597bc` quoted by the reviewer; recomputed at the return: equal. `plan_gantt.py --check`
exit 0; scan 0 warn; resolver 24 of 24.

- Round 1: 20 findings resolved, P2 partial (`test_render_check.py` order).
- New: 3 MAJOR, 13 MINOR. PLAN revision 3 applies each:
  - P2-01: F1 defines a command; P2-02: the scratch home for the live tests, 0 skips;
  - P2-03: A1.4 times twice the input; P2-04: 110.5 waits for 110.4;
  - P2-05: npm with a scratch cache; P2-06: base instruments by `git archive`, a deviation below;
  - P2-07: E and A2.5 run again after an instrument edit; P2-08: B4 takes the negatives from D1;
  - P2-09: every test-first step records its failure on the base; P2-10: F3 vdd-05 Step 4;
  - P2-11: E2 and the `SKILL.md` quote; P2-12: H1 §10.1 row; P2-13: C2 `engines.node`;
  - P2-14: A1.4 seeded generator; P2-15: the P7–P21 list above; P2-16: H2 byte-identical revert.

## Deviations

- **Base instruments in the scratchpad (P2-06).** `framework-upgrade` §3.1 says no copy of any
  file is written outside version control. The replays of R9.4 need the base instruments, so
  `git archive 6ae772b` extracts the skill into the session scratchpad. The extraction is read
  only and rebuilt from the base commit; it holds none of this run's work.
- **Scratch renders and installs.** Renders and the render home of this run lie in the session
  scratchpad, outside every git work tree, as `framework-upgrade` and TASK 108 R7 require.

## Execution (§3)

- **Base check:** HEAD equals the base. 52 edited paths are tracked, 4 created paths are not
  ignored, and every path has a safe form. PLAN revision 4 added 3 fixture files (B1).
- **Deviation found in execution (TASK revision 5).** TASK 108 decided that a self-message's own
  lifeline is no crossing (`fixtures/expected.json`, `fx-seq-skip`). Revision 4 had made it a
  warning, which every labelled self-message would raise. R1.1, R1.2, D2 and UC-1 now keep the
  base rule. The fixture `fx-seq-own` holds the case.

**Tests first, failing on the base code.**

| Cluster | New tests | Failing on the base code |
| :--- | :--- | :--- |
| A1 | `test_commonmark_scan.py`, 9 tests | the 2 time bounds; the 7 branch and digest tests pass by design |
| A2 | MA-SYN-09, the merge-then-down join | every new positive case |
| A3 | TC-ME-48, 2 rows | the Q16 row; the time row passes, as the base pattern is linear |
| B | `fx-seq-own`, the split severity, the gate name | 13 checks |
| C | browser hash, stamps, the v10 override | 12 checks |
| F | plan status, step numbers, `update_state.py` flags | 9 checks |
| G | `test_fix_round_rules.py` | 4 of 4 |

**Mutations (H2).** Each was applied alone; each revert was byte-identical:

| Mutation | Fails |
| :--- | :--- |
| `_Line.find` rescans | `test_a_staircase_of_nested_items` |
| the blank-line walk restored | `test_nested_markers_then_blank_lines` |
| each of 6 branches deleted or inverted | its own branch test, and the digest test for 5 of them |
| one span `indent` off by one | the digest test |
| `lifeline_through_label` back in `WARN_CHECKS` | 3 tests in `test_svg_geometry` and `test_render_check` |
| the own-end test removed | 3 tests on `fx-seq-own` |
| the `timeline-header` hazard not recorded | MA-SYN-09 probe and 19 more lint tests |
| the corner form removed | `test_a_merge_that_turns_down_is_a_join` |
| `_FENCE_LINE` restored | TC-ME-48 and TC-ME-22 |

The ambiguous form of the fence pattern took 0.16 s, 2.6 s and 41 s on 20, 24 and 28 markers;
TC-ME-48 would not finish under it.

**Replays (R9.4, A11).**

- Scanner, A8: 30,000 generated documents, base scanner from `git archive 6ae772b` against the
  new one: 0 differ, spans, comments, plain lines and `code_line_reader` included. Growth: time
  ×4.05 for input ×3.99 (staircase), ×2.01 for ×2.00 (markers and blank lines).
- Lint, A2.5: 77 files, the 11 references and the 66 answers. Corrected in fix round 2, below:
  the first harness ran the base lint from its scratch extraction on relative names, so both runs
  read the references as outside the skill (MA-NEG-03). Its "266 before and after" compared that
  artefact, not the instruments.
- Geometry and v10 install, D1 and D4: 144 renders of the references, metrics equal to the base
  fixtures with the R1 keys aside. N7: its non-sequence metrics are equal, and each of its 3
  renders gains one `lifeline_through_label` fail. All other negatives and every positive keep
  their verdict.
- Grader, E1: 0 of 66 `grading.json` changed, byte for byte. `report.json` changed only in the
  sha256 of `grade_figures.py`; the benchmark only in its timestamp, so the committed one stays.

**Gates (H3).** Every step of `framework-gates.yml` ran locally and passed. The advisory archive
step reports 5 unresolvable references, all in archives of TASKs 103 and 105 and of 2026-08-13.
The skill suite with the scratch render home: 636 passed, 0 skipped. Without it, the 7 live-render
tests skip: the default home predates the stamp. `validate_skill.py` exits 0 on the five skills.
`scan_register.py` reports no warning that the base version of each edited file did not have.

## Review round 1 (H4)

Two reviewers read the frozen tree `0391f1e907f4`: one code reviewer with the plain exhaustive
prompt, and one security auditor. Each quoted the fingerprint; the tree was unchanged at both
returns. Same-model agreement is corroboration, not independent confirmation.

- **Code review:** CHANGES REQUESTED; 0 BLOCKING, 1 MAJOR (CR-01), 9 MINOR, 5 NIT. The reviewer
  ran 70,000 more generated documents against the base scanner: 0 differ.
- **Security audit:** PASS; 0 CRITICAL, 0 HIGH, 2 MEDIUM (M1, M2), 3 LOW, 4 INFO. External
  scanners other than npm are not installed.

### Fix round 1 — the closed list

| Id | Severity | Finding | Fix |
| :--- | :--- | :--- | :--- |
| M1 | MEDIUM | a link to a path that ends in a newline passes the hash check | one resolved path for hash, config and stamp; control characters refused |
| M2 | MEDIUM | a public issue discloses an unpatched bypass | private vulnerability report; only the text below the rule |
| L1 | LOW | the checked browser is not bound to the one that runs | resolved path stored; private browser directory at setup and render |
| L2 | LOW | the hash recipe fails open and can collide | node recipe: `lstat` walk, JSON lines, refusal of unreadable and special entries |
| L3 | LOW | nothing says the hash variable is the operator's | `SKILL.md` and the refusal message say so |
| I3 | INFO | a path with glob characters expands in the candidate loops | `set -f` around both loops |
| CR-01 | MAJOR | R1.4 partly met; `SKILL.md` overclaims | the two severities and the forward render, in `SKILL.md` and FIG-9 |
| CR-02 | MINOR | the `_joins` docstring says three forms | four forms, one bullet each |
| CR-03 | MINOR | the changelog says WI-32 and WI-22 closed | H6 lands in this round |
| CR-04 | MINOR | the P17 note predates TASK revision 5 | the final-code result |
| CR-05 | MINOR | A8 growth not measured at twice the bytes | staircase at 707 items |
| CR-06 | MINOR | the install hint names a build the table lacks | the recorded build and the variable |
| CR-07 | MINOR | a re-pointed link switches browsers silently | as L1 |
| CR-08 | MINOR | a failed smoke render reads as a refused hash | a flag per attempted smoke render |
| CR-09 | MINOR | the vdd-05 summary says "merged" on the failure path | `<TaskName>: <verdict>` |
| CR-10 | MINOR | `expected.json` reformatted as a whole | written back with its own indent |
| CR-11 | NIT | a malformed stamp hash reads as another browser | its own message and test |
| CR-12 | NIT | a comment left above the wrong block | moved |
| CR-13 | NIT | MA-SYN-09 fires on `timeline %% note` | measured: no period in 10.9.8 or 11.17.2; the comment is cut first |
| CR-14 | NIT | the third stamp refusal unlisted; join form 3 has no ASCII spelling | ARCHITECTURE, changelogs, `ascii.md` |
| CR-15 | NIT | the tree hash is read once per tag | once per executable |

Out of the list: I1, I2 and I4 need no change. A defect found in the round goes to round 2 as a
new finding (`developer-guidelines` §6.4).

### Fix round 1 — hand-off (`developer-guidelines` §6.4)

Every item of the closed list is fixed. No edit was made outside the list, apart from three
measured moves the list items needed:

- `SKILL.md` stays under 3000 words (TC-ME-32): CR-01 and L3 took 20 words, so the network
  sentence was shortened. TASK R1.4 now has `SKILL.md` cite `sequence.md` §3 for the forward
  render (TASK revision 6).
- The tree hash changed with the L2 recipe: the recorded entry is now `6c16d726…ab9c`. A node
  implementation and the Python oracle of the test agree on it.
- TASK revision 6 states R7.3, R7.4, R7.6, R7.7, R10.3, D5 and D6 as fixed.

**Differential replay.**

| Instrument | Corpus | Result |
| :--- | :--- | :--- |
| `render_check.py`, `svg_geometry.py` (unchanged) | the 147 renders of the references, round 1 against round 2 | 0 of 147 moved, metrics and findings |
| `mermaid_model.py` (docstring; `%%` cut from the `timeline` header) | lint over the 11 references and the 66 answers | corrected in fix round 2: the harness was flawed |
| `grade_figures.py` | unchanged | no stored corpus to replay |
| `setup_renderers.sh` | no stored corpus; the test battery and two scratch installs | both installs accepted the recorded browser |

**New tests, each failing under the mutation of its fix** (restored byte-identical):

| Mutation | Fails |
| :--- | :--- |
| control characters accepted | `test_a_path_with_a_control_character_is_refused` |
| the browser directory privacy skipped at setup | `test_a_browser_directory_others_may_write_in_is_refused` |
| the smoke flag never set | `test_a_failed_smoke_render_is_not_reported_as_a_refused_hash` |
| a malformed stamp hash accepted | `test_a_stamp_without_a_tree_hash_is_refused` |
| the browser directory privacy skipped at render | `test_a_browser_directory_others_may_write_in_is_refused` |

**Measured for CR-05 and CR-04.** The staircase from 500 to 707 items doubles its bytes, and its
time grows ×2.03. With the final code, `docs/presentation/FRAMEWORK_EVOLUTION.md` passes with one
skipped-lifeline warning (SkillDB on `Agent -> User`); its self-message is not counted.
`brainstorming/examples/demo_complex.md` passes with two skipped-lifeline warnings.

**Gates.** Skill suite 642 passed, 0 skipped, with the scratch home `rh-110b` that the final
script installed; eval selftest 225 of 225; every step of `framework-gates.yml` passed again; the
setup tests ran under `/bin/bash` 3.2.57.

## Review round 2 (H4)

The same two reviewers read the frozen tree `cb84b76e77c8`; the security auditor recomputed it
before and after its checks, equal.

- **Code review:** CHANGES REQUESTED; 0 BLOCKING, 1 MAJOR. Of the 21 items, 19 resolved, CR-14
  and M2 partial. **Regressions from fix round 1: 5** (R1 MINOR, R2 to R5 NIT).
- **Security audit:** PASS; 0 CRITICAL, 0 HIGH, 1 MEDIUM (M2 residual). **Regressions: 0.** M1,
  L2, L3 and I3 re-tested: resolved. New: N1 and N2, both LOW, the rest of L1.

**WI-27 measurement (TASK R10.4).** The fix round reported its replay. Round 2 found 5
regressions from it against 21 items addressed, of which 19 resolved and 2 in part. TASK 108 measured 23, 17 and 17 regressions in its
waves.

### Fix round 2 — the closed list

| Id | Severity | Finding | Fix |
| :--- | :--- | :--- | :--- |
| CR2-N1, SEC2-M2 | MAJOR | the public repository would publish the report text and the RF-21 root cause | report text out of the repository; RF-21 and TASK §1 at the detail of the base |
| SEC2-N1 | LOW | a directory above the two checked can be swapped for a link to an older build | `render_check.py` refuses a browser path that no longer resolves to itself |
| SEC2-N2 | LOW | file modes are not read | an entry others may write in refuses the browser; the executable's mode checked at render |
| CR2-R1 | MINOR | a launcher link resolves to its launcher | a link whose resolved file name differs from its own is refused |
| CR2-R2 | NIT | the dry run prints the given path | it prints the resolved path and its build |
| CR2-R3 | NIT | the `_joins` docstring names the second form only | forms 2 and 4 |
| CR2-R4 | NIT | R7.7 says every refusal names the setup | R7.7 and the docstring state which refusals do |
| CR2-R5 | NIT | the hash advice follows a refusal it cannot help | given only when a hash was not recorded |
| CR2-S1 | NIT | the stand-in browser of `test_render_check` is `sys.executable` | a stand-in two levels inside the private temp directory |
| CR2-N2, CR-14 | NIT | the changelogs list three refusals | four |
| CR2-N3 | NIT | a link into a shared directory hashes all of it | the variable names a self-contained browser directory, stated |

### Fix round 2 — hand-off (`developer-guidelines` §6.4)

Every item of the closed list is fixed. Edits outside the list, each with its reason (corrected
after review round 3, N3-1):

- the correction of the lint replay in `evals/AMENDMENTS.md` and below: a defect of this run's
  own record, found while replaying; it is a finding outside the list, reported here;
- the WI-27 closure, its BACKLOG line and the changelog lines: the pipeline step H6.

- The report text left the repository: the file created in round 1 is removed, and its text is
  handed to the operator outside the repository. RF-21 is back at the detail of the base, plus the
  upstream status. TASK §1, R7.5, R7.6 and D6 follow (TASK revision 7); PLAN revision 5 drops the
  created path.
- `setup_renderers.sh` refuses a launcher link and an entry others may write in, prints the
  resolved path in the dry run, and gives the hash advice only after an unrecorded hash.
- `render_check.py` refuses a browser path that no longer resolves to itself and an executable
  others may write. Its test stand-in browser lies two levels inside the private temp directory.

**Correction of the lint replay.** Rerunning the lint replay showed that the harness of A2.5 and
of fix round 1 was flawed. It passed relative names. It ran the base lint from its scratch
extraction, so the base lint read every reference as a file outside its skill (MA-NEG-03). The
corrected harness copies the current references into the base extraction and lints each file by
its absolute path in each tree. Result, base against new on the same text:

| Corpus | Base | New | Moved |
| :--- | ---: | ---: | :--- |
| the 66 campaign answers | — | — | 0 |
| the 11 references | 247 findings in all | 246 in all | 1: MA-NEG-02 on N7, whose marker names the new gate |

**Differential replay of fix round 2.**

| Instrument | Corpus | Result |
| :--- | :--- | :--- |
| `render_check.py` | the 147 renders of the references, round 1 against round 2 | 0 of 147 moved |
| `mermaid_model.py` (docstring only) | the corrected lint replay above | 1 moved, explained |
| `setup_renderers.sh` | no stored corpus; a third scratch install | the recorded browser accepted |

**Mutations of the new checks.** Each was restored byte-identical, and each fails its test:

- a launcher link accepted; open entries accepted;
- the hash advice after any refusal; the dry run printing the given path;
- a path resolving elsewhere accepted; a writable executable accepted.

**Gates.** Skill suite 646 passed, 0 skipped, with the scratch home `rh-110c`; eval selftest 225
of 225; every step of `framework-gates.yml` passed.

## Review round 3 (H4)

The same two reviewers read the frozen tree `c0c20dcff8b0`.

- **Code review:** APPROVED. Of the 11 items, 10 resolved, SEC2-N2 partial. **Regressions from
  fix round 2: 2** (RG3-1, RG3-2, both MINOR). Two findings on this run's own records (N3-1,
  N3-2).
- **Security audit:** PASS; 0 MEDIUM. M2 resolved: no root cause or reproduction of the mermaid-cli
  defect remains in the working tree. N1 and N2 partial, LOW. **Regressions: 1**, the same as
  RG3-2.

### Fix round 3 — the closed list

| Id | Severity | Finding | Fix |
| :--- | :--- | :--- | :--- |
| SEC3-N1 | LOW | a build swapped in by rename above the checked directories passes | a stat stamp of the browser directory, compared at every render |
| SEC3-N2, RG3-2 | MINOR | the walk accepts a group-writable entry of a shared primary group, and render refuses it | one group rule, `_own_group`, in the walk and at render; the stat stamp covers every file |
| RG3-1 | MINOR | a link to the browser under another name reads as "another program" | the message names a link under another name |
| N3-1 | MINOR | the hand-off of fix round 2 claims no edit outside its list | the hand-off lists the replay correction as a finding outside the list |
| N3-2 | MINOR | the WI-27 closure says 21 items fixed | 21 addressed: 19 resolved, 2 partial |
| SEC3-I1 | INFO | TASK §1 says no upstream report exists | "reported privately; status in WI-30" |

### Fix round 3 — hand-off (`developer-guidelines` §6.4)

Every item of the closed list is fixed. No edit outside the list.

- **Stat stamp (SEC3-N1, SEC3-N2).** The setup's walk also computes a stat digest of the browser
  directory and stamps it as the second line of `.browser.sha256`. `render_check.py` recomputes it
  with `lstat` at every render and refuses a change. A render leaves the digest unchanged:
  measured on the real browser before and after a render, 22 entries, the same digest. The node
  digest of the setup equals the Python digest of `render_check.py` on the same directory.
- **One group rule (RG3-2).** The walk accepts group write only for the user's own group, passed
  from `id -g` when `id -gn` equals `id -un`, as `private_problem` and `_own_group` do. It also
  refuses an entry owned by another user than this one or root.
- RG3-1, N3-1, N3-2 and SEC3-I1: the message, the hand-off of round 2, the WI-27 numbers and
  TASK §1, as listed. TASK revision 8.

**Differential replay.** `render_check.py`: the 147 renders of the references, round 2 against
round 3: 0 moved. `setup_renderers.sh`: no stored corpus; a fourth scratch install accepted the
recorded browser and stamped both lines.

**Mutations.** Each was restored byte-identical, and each fails its test:

- the stat comparison skipped: the rewrite and the rename-swap tests;
- a stamp without a stat line accepted: its own test;
- the group rule back to the process gid: `test_group_write_follows_the_own_group_rule`.

**Gates.** Skill suite 650 passed, 0 skipped, with the scratch home `rh-110d`; eval selftest 225
of 225.

## Review round 4 (H4)

The same two reviewers read the frozen tree `546ce36b4124`.

- **Code review:** APPROVED. **Regressions from fix round 3: 3**, all NIT (RG4-1 to RG4-3); N3-2
  partial in one BACKLOG line.
- **Security audit:** PASS; 0 MEDIUM. N1, N2 and R1 resolved; the stat stamp held under five
  probes. **Regressions: 0.** New: N3 (LOW, a swap inside the render window under a shared cache)
  and N4 (LOW, availability: a metadata change alone refuses renders until a new setup).

### Fix round 4 — NIT only, verified by tests

RG4-1 to RG4-3, the N3-2 line, and N4 as a stated behaviour (TASK D5, ARCHITECTURE §10.7). The
round adds `surrogateescape` to `browser_stat_digest`, with a test that runs on Linux and skips on
macOS, whose file system keeps every name valid UTF-8. Every other edit is text.

No fifth review round ran. Every remaining item was NIT or LOW, and the round changed one line of
code; its test and the replay below verify it. N3 was offered in the retro and not chosen; it
stays recorded here. Its remedy, a privacy check of every ancestor of the browser, changes what a
shared cache may hold.

**Replay and gates.** The 147 renders of the references, round 3 against round 4: 0 moved. Skill
suite 650 passed, 1 skipped (the Linux-only test); eval selftest 225 of 225; every step of
`framework-gates.yml` passed. `check_positional_refs.py --targets-changed --fix` repaired nothing:
its 12 errors lie in old changelog entries and in archives of TASKs 095, 103 and 105.

## Regressions per fix round

| Fix round | Items | Regressions found by the next round |
| :--- | ---: | ---: |
| 1 | 21 | 5 (code) + 0 (security) |
| 2 | 11 | 2 (code) + 1 (security, the same defect) |
| 3 | 6 | 3 NIT (code) + 0 (security) |
| 4 | 5 | not reviewed; tests and replay |
| I-1 | 21 | 6 (code) + 8 (security), one defect in both |
| I-2 | 14 | not reviewed; tests |

## Retro items (cluster I, TASK R11, D12)

The retro offered its items as work-items. The operator chose three and asked to fix them in this
run: the step numbers, the disclosure rule and the `SKILL.md` headroom.

- **I1, step numbers.** A scan of every workflow before I1 found `01-start-feature` ("4."
  twice), `security-audit` ("5." twice) and `vdd-adversarial` ("3." twice). `test_mermaid_wiring`
  now reads every workflow, and a `##` or `###` heading starts a list. In `01-start-feature` the
  second "4.", which reads the architect prompt, became the first line of step 5, so the steps
  after it keep their numbers. In the other two the Retro step took the next number; the test
  then failed once more, on the "4." that `vdd-adversarial` gave twice, and its Announce step
  became 5. No line was added, so every loop-contract window held: 25 loops, 0 errors, 0
  warnings. The step numbers that other documents cite (`01-start-feature` 4 and 5,
  `vdd-adversarial` 2a, `security-audit` 2 and 4) are unchanged.
- **I2, the disclosure rule.** `security-audit` §6.1 and a §7 row, version 3.9. `core-principles`
  1.1 points to it, because the orchestrator wrote this run's draft and does not load
  `security-audit`. Step 4 of the `security-audit` workflow points to it where the report is
  saved. `tests/test_disclosure_rule.py` joins the curated suite. `analyze_gaps.py` reports the
  same items on both skills as on the base. The review below widened all of this.
- **I3, headroom.** 2998 → 2864 words. Two Red Flags that restated Step 4 now cite it, the
  negative-fence grading that `references/review-checklist.md` §3 states under "Evidence labels"
  is a pointer, Step 1 cites the routing table, and two rows leave the examples teaser. No rule
  left the skill.
- **Register.** Every edited markdown file holds no more `warn` than at the base. The sweep found
  two that earlier rounds missed: a two-sentence row in `System/Docs/SKILLS.md` from G and one in
  `System/Docs/WORKFLOWS.md` from F. Both rows are one sentence now.
- **Gates.** Every step of `framework-gates.yml` passed: skill suite 650 passed and 1 skipped
  (Linux only), eval selftest 225 of 225, curated suite OK, 47 of 47 skills valid. The resolver
  repaired nothing; its 12 errors are the ones listed under round 4.

## Review of cluster I, round 1

One code reviewer with the plain exhaustive prompt and one security auditor read the frozen tree
`3c4f371815b0`. The value is the `skill-parallel-orchestration` §2.4.1 formula with the hash of
each untracked file added, because the round reads untracked files; the formula alone gives
`aaced322114c` for the same tree. Neither reviewer wrote to the tree, and the orchestrator's
recompute at their return matched the brief.

- **Code review:** CHANGES REQUESTED. CI-1 to CI-12: 1 HIGH, 4 MEDIUM, 5 LOW, 2 NIT. It
  confirmed the R11.1 citations, the loop contract, the K3,3 fact in Step 4.3 and the routing
  row that replaces the Step 1 sentence. Its skill suite skipped 7 more tests, because its
  default render home holds no browser stamp.
- **Security audit:** PASS; 0 CRITICAL, 0 HIGH. SI-1 to SI-9: 2 MEDIUM, 6 LOW, 1 INFO. Its
  sweep found no root cause or reproduction anywhere in the tree, untracked and ignored files
  included, and no history entry of the draft.
- **For the operator.** Since cd9a455 (2026-10-03) the public `main` names the defect class and the
  file types a page reaches. It does so in at least these places: the heading and "Observed" of
  RF-21; the title, `value`, "Signal" and option 1 of WI-30; its line in `docs/BACKLOG.md`; and
  `docs/reviews/task-108-code-review-r1.md` line 57. It holds no root cause and no working path.
  §6.1 leaves such detail as it is and extends nothing; TC-05 pins the two paragraphs. The private
  report should tell the maintainers that this description is public.

### Fix round I-1

The closed list is CI-1 to CI-12 and SI-1 to SI-9.

| Items | Disposition |
| :--- | :--- |
| CI-1 | Fixed: the pointer names §3, "Evidence labels", in `SKILL.md`, the PLAN and this audit |
| CI-2, SI-9 | Fixed: the term covers a vulnerability with no public advisory |
| CI-3, SI-1, SI-6 | Fixed in part; see below the table |
| CI-4, SI-5 | Fixed: "only" the status level; public detail is not extended; TASK §1 trimmed |
| CI-5, CI-6, SI-3 | Fixed: the advisory is the trigger; the report URL is recorded at once |
| SI-2 | Fixed: §6.1 lists the public surfaces and tool records; `run-feedback` points to it |
| SI-4, CI-12 | Fixed: `core-principles` §5 "Disclosure" says "no file in the repository" |
| SI-7 | Fixed: the WI-30 acceptance names the URL of the private report |
| SI-8, CI-10 | Fixed: TC-05 pins two paragraph digests; TC-04 pins the version mirrors |
| CI-7, CI-8, CI-11 | Fixed: the counts and the wording of the PLAN and this audit |
| CI-9 | Fixed: a section is keyed by line and heading, and `1)` and a 2-space indent count |

**CI-3, SI-1 and SI-6.** §6.1 names the four duties that give way: the regression test, the
vendored patch, the exploit scenario and the defect record. Step 4 of the workflow covers each
output of the remediation step. Step 3 of the auditor prompt and the filing rules of
`run-feedback` point to §6.1, and an agent posts only when the operator asks in their own message.
The `critic-security` and `security-auditor` wrappers are unchanged. Neither writes a file: each
returns text to the orchestrator, and the orchestrator that saves the text loads `core-principles`
§5. The critic wrapper is also generated into four vendor copies from `wrappers_manifest.json`.

**Not changed.** `scripts/audit/__init__.py` of `security-audit` holds `__version__ = "3.7"`. That
is the package version of its scripts; it predates this task (CI-10). A list that restarts within
one section still counts as a repeat, as the test's docstring states (CI-9).

## Review of cluster I, round 2

The same two reviewers read the frozen tree `da7dcf7dc91d` (the bare §2.4.1 formula:
`1362e55cfe6f`); both recomputed it at their end, unchanged. This round checks the closed list
of fix round I-1 and counts its regressions.

- **Code review:** CHANGES REQUESTED. Every item resolved except CI-3, CI-4 and the
  `__version__` part of CI-10, which are partial. It found that the CI-3 reason holds for
  `docs/audit/`. **Regressions from fix round I-1: 6** (CR2I-1 to CR2I-6: 1 MEDIUM, 3 LOW,
  2 NIT).
- **Security audit:** PASS; 0 CRITICAL, 0 HIGH. SI-1, SI-5 and SI-6 partial, the others
  resolved. Its sweep of the changed lines and of the history found no detail. **Regressions
  from fix round I-1: 8** (SR2I-1 to SR2I-8: 2 MEDIUM, 6 LOW). It holds the wrapper reason in
  part: `vdd-multi` writes a merged report that holds each critic's exploit scenario.
- One MEDIUM is the same defect in both reports: step 2 lists what a record holds, and a duty
  bullet then let the record keep the impact (CR2I-1, SR2I-1).

### Fix round I-2

The closed list is CR2I-1 to CR2I-6 and SR2I-1 to SR2I-8, with the `vdd-multi` gap of SI-6.

| Items | Disposition |
| :--- | :--- |
| CR2I-1, SR2I-1 | Fixed: a record holds a severity; the exploit scenario stays out of it; the CWE waits for the advisory |
| SR2I-2 | Fixed: `core-principles` §5 names each surface of §6.1 and that the operator sends |
| CR2I-3 | Fixed: `run-feedback` files only what §6.1 step 2 lists, section by section |
| CR2I-4, SR2I-3 | Fixed: a public advisory is cited by its CVE or GHSA identifier |
| SR2I-4 | Fixed: one trigger, "until a public advisory describes it", in every touched place |
| SR2I-5 | Fixed: the operator asks for a channel, the send date is recorded, a decision lifts step 2 |
| SR2I-6 | Fixed: isolation or configuration first, since a narrow guard can show the defect too |
| SR2I-7 | Fixed: the operator paragraph says "at least", and the test names what it leaves out |
| SR2I-8 | Fixed: TC-05 checks the RF-21 rule and the WI-30 acceptance |
| SI-6 | Fixed: `vdd-multi` output routing and the `security-auditor` wrapper keep the scenario out |
| CR2I-2 | Fixed: 2864 words in both changelogs and here |
| CR2I-5 | Fixed: three lines re-wrapped; the short line in `CHANGELOG.md` ends its paragraph |
| CR2I-6 | Fixed: the test's docstring states the limit |

**Not changed.** The `critic-security` wrapper: it returns text only, and `vdd-multi` now routes
a dependency finding's scenario out of the report it writes. TC-05 pins two paragraphs, not every
line that holds public detail (the residual of SI-8).

## Close (§4.5, H6, H7)

- WI-32, WI-30, WI-22 and WI-27 are `done`. The operator e-mailed the upstream report to
  security@mermaid.live on 2026-10-05, the channel of the mermaid-js security policy, with the
  affected versions 11.14.0 to 12.0.0 (TASK D13). Its text stays outside the repository.
- `git status` lists 71 entries, each a declared path: 60 before cluster I and 11 from it. Three
  declared paths stayed unchanged: the benchmark files of the campaign and `test_plan_gantt.py`.
- The operator commits. A default render home installed before this task is refused until
  `setup_renderers.sh` runs again (CHANGELOG, Migration).
