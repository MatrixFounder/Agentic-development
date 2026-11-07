# TASK 141 — [LIGHT] vdd-adversarial works outside the framework, and the copies of both VDD skills match canonical

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 141 |
| Slug | vdd-skills-standalone |
| Type | Light Mode (D1) |
| Source | the operator's requests of 2026-11-07 |
| Base revision | `02619856ddb5e75dd303a38bcad8b1c969122562` |
| Archive name | `task-141-vdd-skills-standalone.md` |
| Revision | 3 |

**Request.** `Universal-skills/skills/vdd-adversarial` is a full copy of the canonical skill, and
the public repository `MatrixFounder/Universal-skills` publishes it as a standalone skill and a
plugin. The operator asked to bring the copy up to date. The copy must work outside this
framework.

**Findings of 2026-11-07.**

1. The copy of `vdd-adversarial` differs from canonical in `SKILL.md` only. Canonical v1.11 has
   the §3 item "Figures behind a decision" of commit `511ec04`; the copy is v1.10.
2. Both copies carry references that a standalone consumer cannot resolve. The lines are those
   of `.agent/skills/vdd-adversarial/` at the base revision `0261985`:
   - `.agent/skills/vdd-adversarial/SKILL.md:28@0261985` `docs/reviews/ab-experiment-075.md`,
     `/vdd-multi`;
   - `.agent/skills/vdd-adversarial/SKILL.md:25@0261985` and `references/vdd-methodology.md`
     `audit-067 C-01`, `C-02`;
   - `.agent/skills/vdd-adversarial/SKILL.md:31@0261985` and `vdd-methodology.md` §IV
     `execution evidence supplied by the orchestrator`;
   - `.agent/skills/vdd-adversarial/SKILL.md:49@0261985` `the runtime version the brief names`;
   - `.agent/skills/vdd-adversarial/SKILL.md:68@0261985` `view_file`;
     `assets/template_critique.md` `list_dir`.
3. `.agent/skills/vdd-adversarial/SKILL.md:26@0261985` requires an issue per line of code; a
   project without an issue tracker cannot meet it.
4. `SKILL.md` §2 requires confidence and severity per finding. The template has no per-finding
   confidence, no CRITICAL severity and no place for the test evidence of the exit bar.
5. The copy of `vdd-sarcastic` is ahead of canonical. Copy v1.6 has §2.5 Execution Mode, §2.6
   Safety Boundaries, and the §4 heading "Validation Evidence". `validate_skill.py` reports four
   Execution Policy warnings on canonical v1.5 and none on the copy.

**Revision 2** follows the code review of cycle 1: CHANGES REQUESTED, with one MAJOR, seven MINOR
and twelve NIT findings, none BLOCKING. The fix pass:
- the MAJOR: the template has a Verification column, and each row of the example names its line
  and its check (R2, R3);
- the template defines PASS, WARNING and FAIL, takes `none` as a Source, carries an optional Tree
  state line, and puts the unverifiable exit bar into the Risk table as a finding;
- the methodology states Linear Accountability as `SKILL.md` §2 does, and glosses `Sarcasmotron`,
  `Chainlink`, `bead` and `GitHub Runners`;
- "Syntax vs runtime" checks every supported version; the example keeps the client response
  generic on a failed login;
- `tests/test_skill_refs.py` pins the standalone property (R9);
- the URL of D4 is a permalink, and `vdd-sarcastic` §4 states the exit bar of R1 (D9, D10).

**Revision 3** follows cycle 2: APPROVED, with seven MINOR and fifteen NIT findings. The fixes
land in place, with no further review round (D12):
- the example's rate-limit check tests the recommended backoff; its summary names the missing
  test run;
- the Tree state line and `SKILL.md` §4 item 6 count the untracked files; the line takes
  `NOT COMPUTED (<reason>)`; the unverifiable finding has severity HIGH;
- methodology §IV puts the unverifiable finding into the risk table;
- the `vdd-sarcastic` example names a line and a check per row, and the unverifiable test run;
- the test derives the slash commands and the backticked framework names, and scans each file
  with its whitespace collapsed; each alternative has a planted literal;
- wording: Linear Accountability for process findings, "Meeting that bar", "Syntax vs runtime",
  the scripts of §2.6, blank lines before the exit-bar lists.

## 1. Decisions

- D1, 2026-11-07, operator: `/light`. The run has the edits, the test run and one code reviewer
  in at most two review cycles (`light-02-develop-task`). It has no meta-audit and no security
  audit: both skills are TIER 2, and no script changes. The tests gain one class and five
  entries of `EXCLUDED_SITES`.
- D2, 2026-11-07, operator: `vdd-sarcastic` §2.5 and §2.6 move from the copy into canonical.
- D3, orchestrator: canonical becomes standalone, and the copy is a byte-identical copy of it.
  Rejected: a standalone variant kept in `Universal-skills` only — each canonical change would
  then need a manual merge.
- D4, orchestrator, revised after review: the A/B figures stay in `SKILL.md`. Their source is
  the permalink of `ab-experiment-075.md` at commit `1918af6` of the public repository
  `MatrixFounder/Agentic-development`.
  **Why.** A figure without a source cannot be checked ⇒ the citation stays, as a URL.
- D5, orchestrator: the evidence wording of the exit bar is the form of
  `skill-parallel-orchestration` §2.4: the captured output of the command or a summary of it, or
  `NOT RUN (<reason>)`.
  A framework brief therefore still meets it.
- D6, orchestrator: the template severities are `CRITICAL`, `HIGH`, `MEDIUM` and `LOW`, the
  values of `vdd-multi --fail-on`.
- D7, orchestrator: the framework release is v3.56.1.
- D8, orchestrator: the commits in both repositories wait for the operator's approval.
- D9, orchestrator, after review: `vdd-sarcastic` §4 states the exit bar in the words of
  `vdd-adversarial` §2 (v1.6 → v1.7). Its example takes `MEDIUM` for `MED`.
  **Why.** `vdd-adversarial` §2, its methodology §IV and `vdd-sarcastic` §4 stated one bar in
  the same words ⇒ an edit of two of them leaves the third apart. The workflows and
  `System/Docs` restate the four conditions of the bar; they stay as they are.
- D10, orchestrator, after review: the standalone pin is a class of `tests/test_skill_refs.py`,
  the module that checks that references resolve. A new test file stays out of Light Mode.
- D11, orchestrator, after review: the PASS, WARNING and FAIL of the template:
  - PASS: the exit bar is met;
  - WARNING: no CRITICAL finding, and the bar is not met; not an approval;
  - FAIL: at least one CRITICAL finding.
- D12, orchestrator, under the operator's standing rule of 2026-10-16: the findings of an
  approved cycle 2 that are MINOR or NIT are fixed in place, with the tests re-run and no review
  round 3. Three NITs stay as limits: residuals 5 and 6.

## 2. Requirements

- **R1** `vdd-adversarial/SKILL.md` (v1.11 → v1.12):
  - §2 Context Resetting cites no `audit-067` ID;
  - §2 Linear Accountability requires per finding a location and a verifying check; an issue per
    change only where the project tracks issues;
  - the empirical note cites the A/B report by its permalink (D4) and names the measured
    version 1.4. It names no `/vdd-multi`: for class-complete coverage it names one critic per
    class (logic, security, performance) in parallel, with findings merged by location;
  - the exit bar is a numbered list. It accepts evidence from whoever hands over the review, in
    the form of D5, and the unverifiable bar is a finding of the risk table;
  - §3 "Syntax vs runtime" checks every version the project supports: the lowest version of a
    manifest and each CI matrix entry. A version that the request names takes precedence;
  - §2.6 states that the report link is a citation, not a fetch;
  - §6 names no tool of one vendor.
- **R2** `assets/template_critique.md`:
  - a section for the test evidence of the exit bar;
  - a Confidence column per finding;
  - the severities of D6, and a Verification column per finding;
  - the verdicts of D11;
  - the Source values run by the reviewer, handed over, and `none`; an optional Tree state line;
  - the hallucination check names no `list_dir`.
- **R3** `examples/usage_example.md` follows the template of R2. Each row names a snippet line
  and a check that tests its recommendation. The unverifiable bar is a row, and the summary
  names it. The failed-login row keeps the client response generic.
- **R4** `references/vdd-methodology.md`:
  - cites no `audit-067` ID;
  - §IV states the exit bar as in R1;
  - §V.3 states Linear Accountability as `SKILL.md` §2 does;
  - a Terms paragraph glosses `Sarcasmotron`, `Chainlink`, `bead` and `GitHub Runners`;
  - a blank line precedes each list.
- **R5** `vdd-sarcastic/SKILL.md` in canonical takes §2.5 and §2.6 of the copy (D2) and the exit
  bar of D9, as v1.7. Its example names a snippet line and a check per row, and a row for the
  unverifiable test run.
- **R6** `Universal-skills/skills/vdd-adversarial` and `Universal-skills/skills/vdd-sarcastic`
  are byte-identical to canonical, `.DS_Store` excluded.
- **R7** `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md` and `README.ru.md` carry v3.56.1 (D7).
- **R8** `tests/test_frozen_tree_contract.py` lists in `EXCLUDED_SITES` each file of
  `vdd-adversarial` that now carries `NOT RUN`: `references/vdd-methodology.md`,
  `assets/template_critique.md`, `examples/usage_example.md`; and `vdd-sarcastic/SKILL.md` and
  `vdd-sarcastic/examples/usage_example.md`.
- **R9** `tests/test_skill_refs.py::TestStandaloneBundle` fails on a framework-only reference in
  the bundle of `vdd-adversarial`:
  - a path under `docs/reviews`, `tasks`, `plans`, `issues`, `backlog`, a file `docs/<NAME>.md`,
    `.agent/`, `.claude/agents/` or `System/Agents`, `Docs`, `scripts`;
  - a slash command of `.claude/commands/`, or a backticked name of a framework skill or command
    other than `vdd-adversarial` and `vdd-sarcastic`;
  - an `audit-NNN` ID, `orchestrator`, `the brief`, `view_file`, `list_dir`.

  It scans each file with its whitespace collapsed. The permalink of D4 passes, and a URL on
  `blob/main` fails.

## 3. Files

- `.agent/skills/vdd-adversarial/`: `SKILL.md`, `assets/template_critique.md`,
  `examples/usage_example.md`, `references/vdd-methodology.md`;
- `.agent/skills/vdd-sarcastic/`: `SKILL.md`, `examples/usage_example.md`;
- `Universal-skills/skills/vdd-adversarial/`, `Universal-skills/skills/vdd-sarcastic/`;
- `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md`, `README.ru.md`;
- `tests/test_frozen_tree_contract.py`, `tests/test_skill_refs.py`;
- `docs/TASK.md`; the archive of TASK 140.

<!-- contract:acceptance -->

## 4. Acceptance

- TC-1 — `tests/test_skill_refs.py::TestStandaloneBundle` → pass. It fails when a literal
  carries any form of R9, or when the permalink of D4 moves to `blob/main`.
- TC-2 — `validate_skill.py` on both skills, in both repositories → pass with no warning.
- TC-3 — `diff -rq -x .DS_Store` of each canonical skill against its copy → no difference.
- TC-4 — `python3 tests/run_tests.py` → pass.
- TC-5 — `check_prompt_references.py`, `validate_skills.py` and `smoke_workflows.py` → pass.
- TC-6 — `scan_register.py` on the edited text → no finding that this run adds.

## 5. Out of scope and residuals

1. `vdd-sarcastic` keeps its framework references: `audit-067`, `ab-experiment-075.md` and
   roadmap item 13. R9 does not cover it.
2. The `description` of `vdd-adversarial` keeps the term VDD. A standalone consumer who does not
   know the term may not trigger the skill.
3. The other drifted copies: `brainstorming`, `hooks-creator`, `skill-enhancer`.
4. `plugins/vdd-adversarial/.claude-plugin/plugin.json` keeps version 1.0.0, a constant of
   `sync-plugins.sh`. Whether Claude Code reads that version to offer an update is not checked.
5. The forms of R9 are words: ordinary prose that spells one, such as "the brief window", fails
   the test. The allowed URL admits any 40-digit commit, pushed or not.
6. The verdict of the template belongs to one critique. The verdict of `vdd-multi` belongs to
   the merged report under `--fail-on`; the two can differ for the same findings.
