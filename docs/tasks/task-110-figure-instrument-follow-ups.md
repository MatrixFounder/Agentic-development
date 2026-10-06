# TASK 110 — Figure-instrument follow-ups, the renderer supply chain, plan status and fix-round rules

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 110 |
| Slug | figure-instrument-follow-ups |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | WI-32, WI-30, WI-22, WI-27; records listed under the table; the run's retro (R11) |
| Operator decision | 2026-10-05: fix the six WI-32 items; take WI-30, WI-22 and WI-27 into the same run |
| Base revision | `6ae772bea1c7ce702bc161f9046e875a599d69cc` |
| Closes | WI-32, WI-22; WI-30 and WI-27 under the conditions of R10.3 and R10.4 |
| Archive name | `task-110-figure-instrument-follow-ups.md` |
| Revision | 12: the upstream report is sent by e-mail; R10.3 and D13 (`docs/reviews/framework-audit-110.md`) |

**Records.**

- [WI-32](../backlog/wi-32-lint-and-scanner-follow-ups-from-task-108-reviews.md)
- [WI-30](../backlog/wi-30-renderer-supply-chain-v10-lockfile-mermaid-cli-request-filter-browser-hash.md)
- [WI-22](../backlog/wi-22-plan-status-tokens-for-the-generated-plan-chart.md)
- [WI-27](../backlog/wi-27-fix-loops-hand-off-a-differential-replay-of-the-stored-corpus.md)

<!-- contract:problem -->

## 1. Problem

Four work-items remain open after TASK 108. Every number below was measured on 2026-10-05 at the
base revision. A path under `scripts/`, `references/`, `assets/` or `evals/` is relative to
`.agent/skills/mermaid-authoring-guidelines/`. A path under `tests/` or `docs/` is relative to
the repository root.

**WI-32, six items of the figure instruments.**

1. **`lifeline_through_label` gates nothing (RG-19).** It counts only the lifeline of a skipped
   participant. A 33-character message between neighbours draws a 250 px label in a 200 px gap.
   Its own lifelines run 26 px and 24 px inside the label in 10.9.8 and 11.17.2, and the render
   check reports nothing. A self-message draws its label centred on its own lifeline in both
   versions.
2. **No rule reports text after `timeline`.** For `timeline TD` and `timeline LR`, 10.9.8 draws
   `TD` or `LR` as a first period. 11.17.2 draws `TD` top to bottom. The lint reports 0
   findings.
3. **An ASCII merge that turns down is no join.** `test ---+-----+` over a stroke down to `v`,
   and the same form with `┴` and `┐`, give `joins=[]`. The lint asks for no legend.
4. **The CommonMark scanner is superlinear.** 500 nested list items as a staircase take 1.88 s,
   8.5 times the time of 250. One line of 4000 nested markers and 4000 blank lines (12 KB) take
   1.76 s, 4 times the time of 2000. `_Line.find` rescans the leading whitespace once per open
   container, and every blank line walks the whole container stack.
5. **Scanner branches without a test.** Under the skill's suite, 8 branches of `_quote_strip` to
   `_BlockScan` are never taken: `mermaid_model.py` lines 238, 246, 337, 345, 359, 394, 471 and
   478.
6. **The grader misses a `text` fence on a list marker.** `_FENCE_LINE` of
   `evals/grade_figures.py` matches no opener of the form `1. ```text` or `- ```text`. Q16 then
   lints no figure there.

**WI-30, the renderer supply chain.**

- `npm audit` of the v10 lockfile: 6 high. They are `extract-zip` 2.0.1, `tar-fs` 2.1.1,
  `ws` 8.13.0 and three parents, all through `puppeteer` 19.11.1 of `mermaid-cli` 10.9.1. v11
  and v12: 0.
- `extract-zip` has no release with a fix. Overrides of `tar-fs` and `ws` alone leave 4 high.
- An override of `puppeteer` to 25.12.0, the version of v11, gives 0 vulnerabilities and 135
  lockfile entries instead of 190. `mermaid` stays 10.9.8 and `mermaid-cli` 10.9.1. Installed in
  a scratch render home, it rendered all 49 mermaid figures of `references/` in 10.9.8 with
  metrics identical to the committed fixtures.
- `mermaid-cli` 11.14.0 to 12.0.0 hold a vulnerability (RF-21, D13). 12.0.0 is the latest release.
  It goes to the maintainers as a private report; the status is in WI-30.
- `setup_renderers.sh` accepts any cached `chrome-headless-shell` at or above
  `BROWSER_MIN_BUILD`, and any `MERMAID_RENDER_CHROME`, without a hash. Chrome for Testing
  publishes no sha256. The browser directory holds 17 files: the executable, three libraries and
  data files.

**WI-22, plan status.** The develop workflows never update the plan chart, so every bar draws as
waiting. `plan_gantt.py` already reads `done`, `in-progress` and `not-started`. Six places state
that the framework plan writes no status:

- the comment of the plan template of `skill-planning-format`: "The block holds no `status` key";
- `skill-planning-format` `SKILL.md`: "No entry holds `status`";
- `references/gantt.md`: "The framework's plan template writes no `status`";
- the docstring of `plan_gantt.py`: "The framework's plan template omits `status` (TASK D11)";
- `tests/test_mermaid_wiring.py` `TestPlanTemplate`, which requires the five keys without status;
- `docs/ARCHITECTURE.md` §10.8, which puts plan status out of scope.

**WI-27, fix rounds.** No workflow or skill states a replay of a stored corpus before a fix is
handed off, or a closed item list for later fix rounds. TASK 108 measured 23, 17 and 17
regressions in its fix waves.

**Found during the analysis.** `vdd-05-run-full-task.md` Step 4 calls `update_state.py` without
`--summary`, which the script requires: argparse exits 2 and no state is written.
`vdd-03-develop.md` numbers two steps "5.", and `vdd-05-run-full-task.md` two steps "6.".

**Found by the retro.** Three more workflows repeat a step number: `01-start-feature.md` "4.",
`security-audit.md` "5." and `vdd-adversarial.md` "3.". The run drafted a report of a
vulnerability in a dependency, root cause and reproduction included, inside this public
repository; no rule of the framework stops that. The mermaid `SKILL.md` holds 2998 words against
the 3000 that TC-ME-32 allows, so the next edit that adds a sentence fails the eval selftest.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Verified by |
| :--- | :--- | :--- | :--- | :--- |
| R1 | A lifeline through a label of its own message fails the render check | Y | R1.1–R1.5 | A1, A4, A5, A13 |
| R2 | The lint reports text after `timeline` | Y | R2.1–R2.3 | A1, A4, A13 |
| R3 | An ASCII merge that turns down counts as a join | Y | R3.1–R3.3 | A1, A4, A13 |
| R4 | The CommonMark scanner runs in linear time with unchanged output | Y | R4.1–R4.4 | A1, A4, A8 |
| R5 | Every branch of the scanner has a test | Y | R5.1–R5.3 | A1, A4 |
| R6 | The grader opens a fence on a list marker as an ASCII figure | Y | R6.1–R6.3 | A2, A4, A9 |
| R7 | The renderer supply chain: no high advisory, a pinned browser, the upstream report | Y | R7.1–R7.6 | A1, A6, A7, A13 |
| R8 | The plan chart shows task status | Y | R8.1–R8.6 | A3, A10 |
| R9 | Fix rounds replay the stored corpus and keep a closed list | Y | R9.1–R9.4 | A3, A11, A13 |
| R10 | Records, versions and work-items | Y | R10.1–R10.6 | A3, A12, A13 |
| R11 | The retro items: step numbers, the disclosure rule, `SKILL.md` headroom | Y | R11.1–R11.3 | A1–A3, A13 |

### 2.1 Sub-features

- **R1.1** `svg_geometry` records a message label that a lifeline of one of the message's own two
  ends runs through, by the margin of `LIFELINE_LABEL_MARGIN_PX`. It measures from two lifelines
  on; today it returns nothing below three. A self-message's own lifeline is not counted, as at
  the base revision: its label is centred on that lifeline in both versions.
- **R1.2** `lifeline_through_label` moves to `GATE_CHECKS`. An own-end crossing of a message
  between two participants is `fail`. A skipped participant's crossing stays `warn` (D2).
  `mermaid_model.RENDER_CHECK_NAMES` follows.
- **R1.3** Every negative figure that fails the gate in a required render names
  `lifeline_through_label` in its marker, and its paragraph states the finding. N7 of
  `references/paired-examples.md` is one.
- **R1.4** `references/sequence.md`, `references/review-checklist.md` and `SKILL.md` state the two
  severities. The first two also state that the forward render in 12.1.0 reports an own-end
  crossing from 24 characters as information; `SKILL.md` cites `sequence.md` §3, since it stays
  under 3000 words (TC-ME-32).
- **R1.5** Both reference fixtures and the plan-example fixture are re-rendered by the pinned
  renderers. Every positive figure passes in every required render.
- **R2.1** A hazard code `timeline-header` records any text after `timeline` on the header line.
- **R2.2** Rule `MA-SYN-09`, severity `error`, reports it.
- **R2.3** `references/other-kinds.md` §7 states the rule and the measured renders.
- **R3.1** `_joins` counts a stroke from above that meets a path in `+` or `┴`, when the path goes
  on to a corner that turns down to a down arrowhead.
- **R3.2** A fan-out trunk, a single path that turns down, and a corner with no arrowhead below
  stay no join.
- **R3.3** The docstring of `_joins` and `references/ascii.md` §5.2 list the fourth form.
- **R4.1** `_Line.find` reuses the end of a whitespace run that it already scanned on the line.
- **R4.2** A blank line skips the item walk once the line has no whitespace left. The first block
  that a blank line cannot continue then ends the walk.
- **R4.3** `_scan` returns the same spans, comments and plain lines as at the base revision, and
  `code_line_reader` the same answer per line. The oracle is a digest of that output over seeded
  generated documents, computed with the base scanner and stored in the test. The audit also
  records one run of at least 20,000 documents against the base scanner itself (A8).
- **R4.4** A test bounds the time of both shapes of §1, item 4: the staircase of 500 items within
  0.5 s, and 4000 markers with 4000 blank lines within 0.25 s. The prototype took 0.044 s and
  0.011 s; the base scanner 1.88 s and 1.76 s.
- **R5.1** Each of the 8 branches of §1, item 5 has a test of its own.
- **R5.2** A branch that no input of `_scan` reaches is tested through its function, or removed.
- **R5.3** Each R5 test fails when its branch is deleted or its condition inverted.
- **R6.1** `_FENCE_LINE` accepts list markers and blockquote markers before the fence, in any
  order CommonMark allows. A selftest row bounds its time on a line of 100,000 marker characters.
- **R6.2** A selftest row grades an answer with a `text` fence on a list marker, and Q16 lints it.
- **R6.3** The committed campaign is graded again. `evals/AMENDMENTS.md` records the change and
  the verdicts that moved.
- **R7.1** `assets/renderers/v10/package.json` overrides `puppeteer` to 25.12.0. The lockfile is
  rebuilt; `mermaid` stays 10.9.8 and `mermaid-cli` 10.9.1. With puppeteer 22 or newer the setup
  already selects headless mode `shell`, so v10 runs as v11 does with no change of code. The pin
  `PUPPETEER["v10"]` of `scripts/tests/test_setup_renderers.py` becomes 25.12.0, and a test pins
  the override.
- **R7.2** `npm audit --package-lock-only --audit-level=high` exits 0 for v10, v11 and v12.
- **R7.3** `setup_renderers.sh` accepts a browser only when its tree hash is in the table of R7.4
  or equals `MERMAID_RENDER_BROWSER_SHA256`, and the browser directory and the one above it are
  private. This holds for every cached candidate and for `MERMAID_RENDER_CHROME`.
  `BROWSER_MIN_BUILD` still applies to cached candidates. The tree hash:
  1. Every symbolic link of the executable path is resolved once. The browser directory is the
     directory that holds the resolved executable. That resolved path is hashed, written into
     `puppeteer.json` and stamped.
  2. Every file and symbolic link under the directory, at any depth, gives one JSON line:
     `["file", "./<path>", "<sha256 of its content>"]` or `["link", "./<path>", "<target>"]`.
  3. The lines are sorted bytewise by path, each ends in a newline, and the tree hash is their
     sha256. File modes are not hashed.
  4. These refuse the browser:
     - a path or a name with a control character;
     - a file that cannot be read;
     - an entry that is neither a file, a directory nor a symbolic link;
     - an entry that belongs to another user than this one or root, or that another user may
       write in: every user, or a group other than the user's own group (`_own_group`);
     - a link whose file name differs from its target's, since it names a launcher.

     `MERMAID_RENDER_CHROME` names the browser binary in a directory that holds that browser
     only.
  5. The hash is computed once per executable in one run.
  6. The same walk computes the stat digest: one JSON line per entry, the directory included,
     `[path, kind, dev, inode, mode, size, mtime in ns, ctime in ns]`, sorted by path. It is
     stamped as the second line of `.browser.sha256`.

  `--dry-run` prints each candidate's tree hash and verdict and installs nothing. When no
  candidate is accepted, the setup exits 1, as for any failed step.
- **R7.4** `assets/renderers/browsers.json` records mac_arm 150.0.7871.24, the build of the
  committed evidence. A refusal prints the computed tree hash, names the variable, and asks the
  operator to confirm where the browser came from before setting it; an agent stops and reports
  the refusal.
- **R7.7** The setup writes the accepted tree hash and the browser path into each install as
  `.browser.sha256`. `render_check.py` refuses an install in these cases:
  - its `.lock.sha256` differs from the sha256 of the committed lockfile of its tag;
  - its `.browser.sha256` is missing, holds no tree hash or no stat digest, or names another
    browser than its `puppeteer.json`;
  - the browser path no longer resolves to itself;
  - another user may write the executable, or change the browser directory or the one above it;
  - the stat digest of the browser directory differs from the stamped one.

  A refusal of the first two kinds or of the last says to run `setup_renderers.sh` again; one of
  the other two names the path.
  An install made before this task is therefore refused until the setup runs again.
- **R7.8** The header of `setup_renderers.sh`, which is also its usage text, states the hash rule
  and the v10 override. Its sentences on a browser "used as given" and on the 6 high advisories
  change.
- **R7.5** `references/renderer-facts.md` RF-21 names 12.0.0 as affected and states the upstream
  status. It adds no detail beyond the base revision until a public advisory describes it.
- **R7.6** The run writes the report text outside the repository and hands it to the operator,
  with its channel: a private vulnerability report. The repository holds no root cause or
  reproduction of the defect until a public advisory describes it (D6).
- **R8.1** The plan template writes `"status": "not-started"` in every task of its schedule block.
  A PLAN without `status` keys stays valid: a task without one is not started.
- **R8.2** The status steps:
  - `03-develop-single-task.md` and `vdd-03-develop.md` set a task `in-progress` when it starts
    and `done` when its review approves it;
  - `vdd-05-run-full-task.md` sets `in-progress` in Step A and `done` in Step 4 after a merge;
  - a failure path leaves the status `in-progress`;
  - a task entered again after `done`, to be fixed, turns `in-progress`, and `done` again after
    its next approval;
  - in `vdd-03-develop.md` the edit sits below the bound line of `dev-review-loop`, and Step 3
    keeps its number.
- **R8.3** A status edit changes a task's `status` value. After each status edit the workflow
  runs `plan_gantt.py docs/PLAN.md --write docs/PLAN.md`, then `--check`. A step that leaves the
  value as it was runs neither command. The first status edit of a task adds its `status` key.
  The step skips:
  - a PLAN without the schedule anchor: no edit, no command;
  - a task without an entry in the block: no edit, no command; the step never adds an entry;
  - a project without the skill: the status is edited and the chart commands are skipped, as
    the planner prompt does for the chart.
- **R8.4** `plan-review-checklist` checks that a new plan holds `not-started` or no status in
  every task.
- **R8.5** `skill-planning-format`, `references/gantt.md`, `examples/PLAN_EXAMPLE.md` and the
  `plan_gantt.py` docstring state the status rule. The six statements of §1 change, and the
  wiring test requires `not-started` in the template and the example.
- **R8.6** `vdd-05-run-full-task.md` Step 4 passes `--summary`. `vdd-03-develop.md` and
  `vdd-05-run-full-task.md` number their steps once.
- **R9.1** `developer-guidelines` states the differential replay: a fix to code that an
  instrument applies to a stored corpus re-runs that instrument over the corpus before hand-off.
  The hand-off lists every verdict that moved, before and after, with its cause, or states
  "0 of N moved". The rule defines its two terms. An instrument is code that gives a verdict on
  an input: a linter, a parser, a grader, a measurement. A stored corpus is a set of inputs the
  project keeps with the verdicts the instrument gave them. A project without one states "no
  stored corpus" in the hand-off.
- **R9.2** `developer-guidelines` states the closed list: from the second fix round of one review
  on, a fix edits only for the findings on that round's list.
- **R9.3** `code-review-checklist` checks both. The VDD review path does not load it (D8).
- **R9.4** This run applies R9.1 to its own instrument changes:
  - `mermaid_model.py` and `lint_mermaid.py`: lint findings over `references/*.md` and the 66
    campaign answers, before and after;
  - `svg_geometry.py`: metrics and findings of the committed fixture renders, before and after;
  - `grade_figures.py`: every verdict of the campaign regrade.
  `AMENDMENTS.md` states that the new gate is not measured on the campaign: its stored metrics
  predate the own-end key.
- **R10.1** `CHANGELOG.md` and `CHANGELOG.ru.md` carry v3.35.0.
- **R10.2** Versions: `mermaid-authoring-guidelines` 1.0 → 1.1, `developer-guidelines` 1.11 →
  1.12, `code-review-checklist` 1.4 → 1.5, `skill-planning-format` 1.2 → 1.3,
  `plan-review-checklist` 1.2 → 1.3.
- **R10.3** WI-30 closes `done` when its record states that the private report is sent, with its
  channel and date (D13). Until then it stays open, and its record names the one item left.
- **R10.4** WI-27 closes `done` when this run's review fix round reports a replay, and the second
  review round finds fewer regressions from that fix round than items fixed. When round 1 needs
  no fix round, WI-27 stays open: nothing was measured.
- **R10.5** WI-32 and WI-22 close `done`; their index lines move to `## Closed`. The WI-32 record
  states that D2 resolves RG-19 in part: a skipped participant's crossing stays a `warn`.
- **R10.6** Living documents:
  - `System/Docs/WORKFLOWS.md` and `System/Docs/SKILLS.md` describe the new workflow steps and
    skill rules;
  - `docs/ARCHITECTURE.md` §10.7 states the browser pin and the install stamp, and §10.8 no
    longer lists plan status;
  - ARCHITECTURE §10.6 gains a row for the three workflows that run `plan_gantt.py`, and
    `SURFACES` of `tests/test_mermaid_wiring.py` pins them.
- **R11.1** No list in a workflow repeats a step number. `01-start-feature.md`, `security-audit.md`
  and `vdd-adversarial.md` are renumbered in place; a step that another document cites by number
  keeps it. The test of R8.6 reads every file of `.agent/workflows/`, and a `##` or `###` heading
  starts a new list.
- **R11.2** `security-audit` §6.1 defines a dependency finding: a vulnerability with no public
  advisory, in code the project does not maintain. It states five steps: a private report; only
  the status level in anything published with the repository; the operator sends; the status is
  recorded; after the advisory, a citation. It names the five duties of an audit that give way:
  the regression test, the vendored patch, the exploit scenario, the CWE and the defect record.
  `vdd-multi` and the `security-auditor` wrapper keep the exploit scenario out of a record. Detail
  already public is not extended. `core-principles` §5, step 4 of the `security-audit` workflow,
  Step 3 of `System/Agents/10_security_auditor.md` and the filing rules of `run-feedback` point
  to it. Versions: `security-audit` 3.8 → 3.9, `core-principles` 1.0 → 1.1, `run-feedback` 1.5 →
  1.6.
- **R11.3** The mermaid `SKILL.md` holds at most 2900 words, and no rule leaves it. A sentence that
  repeats a step or a reference becomes a pointer to it.

<!-- contract:use-cases -->

## 3. Use Cases

| UC | Actor | Precondition | Main scenario | Alternative | Postcondition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| UC-1 long message | author | a 33-character message between neighbours | the render check fails `lifeline_through_label` | a skip: a `warn`; a self-message: none | the author shortens or breaks the label |
| UC-2 timeline | author | `timeline TD` | the lint reports MA-SYN-09, error | no text after `timeline`: no finding | one drawing in every version |
| UC-3 ASCII merge | author | two flows merge in `+`, then the path turns down to `v` | the lint counts a join and asks for a legend | a fan-out: no join | the legend states the merge |
| UC-4 large document | lint user | 4000 nested markers and 4000 blank lines | the scan ends within 0.25 s | — | the same fences as before |
| UC-5 renderer setup | maintainer | a cached browser of an unrecorded hash | `setup_renderers.sh` refuses it and prints its tree hash | the hash variable names it: accepted | `render_check.py` renders only from a stamped install |
| UC-6 develop | developer agent | a PLAN with a schedule block | the task turns `in-progress`, then `done` after approval; the chart is rewritten | no anchor, no entry or no skill: no chart command | at 8 tasks or more, the chart shows done and active bars |
| UC-7 fix round | developer agent | a fix changes a shared parser | the hand-off lists the verdicts that moved on the stored corpus | none moved: "0 of N moved" | the reviewer checks the list |

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion |
| :--- | :--- |
| A1 | `python3 -m pytest -q scripts/tests` in the skill directory passes |
| A2 | `python3 evals/selftest_figure_evals.py` passes every row, TC-ME-22 to TC-ME-24 included |
| A3 | `PYTHONPATH=. python3 tests/run_tests.py` reports OK; `check_loop_contract.py` reports 25 loops, 0 errors, 0 warnings |
| A4 | The tests of R1–R3, R4.4 and R6 fail on the base code; the R4.3 and R5 tests fail under the mutations below |
| A5 | `test_paired_examples` passes on the re-rendered fixtures; N7 fails `lifeline_through_label` in at least one required render |
| A6 | The audit of R7.2 exits 0; the new v10 install renders the references as the base fixtures, R1 keys aside |
| A7 | `test_setup_renderers` and `test_render_check` cover the browser and install cases listed under the table |
| A8 | Over at least 20,000 generated documents the scanner output equals the base scanner output (R4.3) |
| A9 | `report.json` of the committed campaign re-derives (TC-ME-22); AMENDMENTS names every verdict that moved |
| A10 | A PLAN fixture with statuses renders `done` and `active` bars; the template's block validates; the wiring tests pass |
| A11 | Each instrument of R9.4 has its replay in the audit |
| A12 | `scan_register.py` reports no new `warn` on the edited markdown; `git status` lists only declared paths |
| A13 | The content checks listed under the table hold |

**A4 mutations.** Each is applied alone and reverted:

1. `lifeline_through_label` back in `WARN_CHECKS`, or the own-end test removed;
2. the `timeline-header` hazard not recorded;
3. the corner form removed from `_joins`;
4. `_Line.find` scanning from its offset each time, or the blank-line walk restored;
5. for each R5 test, its branch deleted or its condition inverted in the new scanner;
6. for the R4.3 test, one span of `_scan` output changed, such as an `indent` off by one;
7. `_FENCE_LINE` restored.

**A7 cases.** A recorded hash is accepted. An unrecorded hash and a differing hash are refused.
The hash named by `MERMAID_RENDER_BROWSER_SHA256` is accepted. `MERMAID_RENDER_CHROME` passes the
same check, through a symbolic link too. `--dry-run` prints the hash and the verdict. The existing
tests set the variable to the hash of their stand-in browser. A path with a control character, an
unreadable file, a special entry and a directory others may write in are refused. A failed smoke
render is reported as such. `render_check.py` refuses an install with a stale `.lock.sha256`, with
no `.browser.sha256`, with a stamp that holds no hash or names another browser, or with a browser
directory others may write in.

**A8 growth.** The audit also records the time for twice the input of each shape. It is at most
2.5 times the time for the input.

**A13 content checks.**

- `tests/test_fix_round_rules.py` pins the R9.1–R9.3 rules and runs in the curated suite.
- `tests/test_mermaid_wiring.py` pins the status steps of R8.2, the skips of R8.3, the
  `plan-review-checklist` item of R8.4, and unique step numbers in every workflow (R8.6, R11.1).
  It also checks that every `update_state.py` command in `.agent/workflows/` passes `--mode`,
  `--task`, `--status` and `--summary`.
- `validate_skill.py` passes on the five skills of R10.2 and the three of R11.2.
- `tests/test_disclosure_rule.py` pins R11.2 and runs in the curated suite.
- `run_evals.routing_words()["none"]` reports at most 2900 (R11.3).
- A grep finds the R10.2 versions, the v3.35.0 entries and the WI statuses of R10.3–R10.5.
- A grep finds the texts of R1.4, R2.3, R3.3, R7.5 and R7.8, and of R10.6 in `WORKFLOWS.md`,
  `SKILLS.md` and ARCHITECTURE §10.7. No file of the repository holds the report text of R7.6.

<!-- contract:open-questions -->

## 5. Open Questions

**None open.** Seven decisions depart from what a work-item proposed. The operator may overrule
each:

- D1: WI-32 pairs with WI-28;
- D2: RG-19;
- D5 and D6: WI-30;
- D7: WI-22 names `05-run-full-task.md`;
- D8: WI-27 asks for a workflow rule;
- D11: WI-22 asks for a stale-status check.

## 6. Decisions

**D1, 2026-10-05, operator: one run for WI-32, WI-30, WI-22 and WI-27.** WI-32 recommends pairing
with WI-28, which waits for the second campaign, as its own record recommends. WI-26 and WI-23
cost paid runs. WI-24 edits other repositories. WI-29, WI-31, WI-10 and WI-16 touch other
subsystems.

**D2, 2026-10-05, orchestrator: the gate splits by whose lifeline crosses.** A lifeline of the
message's own end crosses the label only when the label is wider than the gap. A line of at most
24 characters stays inside the 200 px gap in 10.9.8 and 11.17.2 (`sequence.md` §3), so the
crossing is avoidable and fails. A skipped participant's lifeline runs through the label centre
in every version. It is unavoidable when the participants' exchanges form a cycle, so it stays a
`warn`. A self-message's label sits centred on its own lifeline; that lifeline is not counted,
as TASK 108 decided for fixture `fx-seq-skip`. P7 and P11 hold such cycles and keep their
content. In 12.1.0 both lifelines cross a message from 24
characters on; the forward render sets no exit code, so it reports this as information.

- Rejected: fail every crossing. No participant order of P7 or P11 removes a skip.
- Rejected: `"messageAlign": "left"`. It removed every crossing of P7 and P11 in 11.17.2. In
  10.9.8 it draws a right-to-left label from the sender outward, beyond its own arrow: in P7,
  "result" stood right of the rightmost lifeline.

**D3, 2026-10-05, orchestrator: MA-SYN-09 reports any text after `timeline`.** 10.9.8 draws any
such text as a period, so the rule needs no list of directions.

**D4, 2026-10-05, orchestrator: v10 overrides `puppeteer`, not its leaves.** The override gives 0
advisories and the identical metrics of §1.

- Rejected: overrides of `tar-fs` and `ws` only. 4 high stay, since `extract-zip` has no fixed
  release.
- Rejected: a vendored `extract-zip` stub through a `file:` override. npm resolved the path once
  per dependent package, under `node_modules/`, where no stub exists.

**D5, 2026-10-05, orchestrator: the browser is pinned by a tree hash, and an unrecorded hash is
refused.** The executable alone is not the browser: it loads three libraries and its data files.
The table records the one build this run can measure. Another platform or build needs
`MERMAID_RENDER_BROWSER_SHA256`, set by the operator. For such a build the pin is trust on first
use: the operator vouches for the browser once. The stamp of R7.7 records the accepted path,
hash and stat digest. `render_check.py` compares the path, the privacy of its directory and the
stat digest: a file written, renamed or swapped in changes its ctime, which no user can set. A
change of metadata alone, such as an extended attribute or a remount, also refuses the install
until the setup runs again; the refusal says so (review round 4, N4). The
hash covers the directory of the executable only, which holds all of `chrome-headless-shell`; an
application bundle or a wrapper script keeps code outside it. `BROWSER_MIN_BUILD` stays: it names
the build of the committed evidence. Rejected: a warning for an unrecorded hash. Untrusted
figures render in that browser. Rejected: recomputing the tree hash at every render. It reads
about 210 MB per render.

**D6, 2026-10-05, orchestrator: the operator sends the upstream report, privately.** A report on
GitHub publishes under the operator's account. 12.0.0, the latest release, holds the defect. The
report therefore goes as a private vulnerability report, and anything public follows a public
advisory (review round 1, M2; `security-audit` §6.1). The repository is public, so the text stays
out of it (review round 2). This run writes the text and does not send it.

**D7, 2026-10-05, orchestrator: the status step sits where a task starts and where a review
approves it.** WI-22 names `05-run-full-task.md`; it calls `03-develop-single-task.md` for each
task, as every workflow that delegates to 03 does, so 03 carries the step. `vdd-05` builds in its
own Step A and merges in its own Step 4. `--write` stays outside the allow-list of
`.claude/settings.json`, so each run of it asks for approval (`test_mermaid_wiring`
`TestPermissions`).

**D8, 2026-10-05, orchestrator: the fix-round rules live in `developer-guidelines` and
`code-review-checklist`.** The developer prompt loads the first, and every develop workflow and
`framework-upgrade` use that prompt, the VDD builders included. The reviewer prompts load the
second. The VDD review path loads neither the checklist nor the guidelines: the Sarcasmotron
overlay of `vdd-03` Step 3 and the critic agents. There the fixer's rule applies and no reviewer
checks it. Rejected: a rule in each fix-loop workflow, as WI-27 proposed. That is 10 workflows,
and their loop-contract windows are pinned.

**D9, 2026-10-05, orchestrator: the grader fix is an instrument fix.** `evals/AMENDMENTS.md`
states that a grader defect is corrected and the campaign graded again under its registered
files. It is not an amendment.

**D10, 2026-10-05, orchestrator: the release is v3.35.0.** A new gate, a new error rule and a
refused browser change what a user sees. The changelog entry tells a user to run
`setup_renderers.sh` again (R7.7).

**D11, 2026-10-05, orchestrator: the plan review checks the status of a new plan only.** WI-22
asks `plan-review-checklist` for a stale-status check. The plan review runs before any task, so
the only status it can check is that of a new plan. A stale status after development is the
develop workflows' step (R8.2). Rejected: a check against the session state, which is per machine
and not in git.

**D12, 2026-10-05, operator: the retro items are fixed in this run.** The retro offered three
items as work-items; the operator chose to fix them now (R11). The disclosure rule lives in
`security-audit`, the skill that defines a finding. `core-principles` points to it because every
role loads it at session start: the draft of this run was written by the orchestrator, which does
not load `security-audit`.

**D13, 2026-10-05, operator: the report went by e-mail.** The mermaid-js security policy names
security@mermaid.live, so the operator sent the report there on 2026-10-05, with the affected
versions 11.14.0 to 12.0.0 that a check of the published packages found. An e-mail has no URL:
WI-30 records the channel and the date, and `security-audit` §6.1 step 4 names both.

## 7. Out of scope

- WI-28, WI-26, WI-23, WI-24, WI-29, WI-31, WI-10 and WI-16 (D1).
- `light-02-develop-task.md` and the plan status. WI-22 names four workflows; light mode plans
  under 8 tasks, for which the chart is empty.
- `framework-upgrade.md` and the plan status. It builds through the developer prompt, not through
  03 or vdd-03; its PLAN keeps its checkboxes, and a status there is the orchestrator's edit.
- A hash for any browser build other than mac_arm 150.0.7871.24.
- The v12 install: not present on this machine. Its lockfile is audited, not rendered.
- Re-rendering the campaign corpus. Its stored metrics predate the own-end key (R9.4).
