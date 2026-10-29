# TASK 136 — [LIGHT] The bypass token counts only in the title, TC-SHIP-08 reads SKILLS.md's count, and the zenuml comment states what the renderers do

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 136 |
| Slug | bypass-in-h1-and-two-stale-claims |
| Type | Light Mode (D1) |
| Source | FW-1, REG-19, `docs/reviews/code-129-3-review.md:39`; the operator's request of 2026-10-29 |
| Base revision | `33e497f7b2916c9da9e727be8a6b3816ad55aedc` |
| Closes | FW-1, REG-19 |
| Archive name | `task-136-bypass-in-h1-and-two-stale-claims.md` |
| Revision | 3 |

**Request.** The operator took three items of the residual report as one `/light` task:

- FW-1: `validate.py:291@33e497f` and `validate.py:328@33e497f` test the bypass token as a
  substring of the whole `TASK.md`;
- REG-19: no case reads the `192-case` count of `System/Docs/SKILLS.md:93`;
- the comment of `mermaid_model/kinds.py:25-28@33e497f` says that no pinned renderer loads the
  zenuml plugin. No record holds it; the code review of TASK 129 names it.

**Revision 2** follows the code review of round 1: CHANGES REQUESTED, with seven MINOR and six NIT
findings. The fix pass takes all thirteen:

- 1, 13: `SKILL.md` of the validator states 60 tests and the `compat_diff.py` replay;
- 2, 9: the coordinates of this TASK carry `@33e497f`, and D3 states the two counts apart;
- 3, 11, 12: `EVAL_SPAN` and `SITE_COUNTS` in `selftest_scan.py`, `TC-SHIP-08c`, and a
  `TC-SHIP-08b` item with a count after the span (R6);
- 4, 10: a BOM, `\n` line ends, the limits in `SKILL.md` §3, and decoys above the title (R4);
- 5, 6, 7, 8: the token constant in both messages, two comments, the place of the resolution.

**Revision 3** follows round 2: CHANGES REQUESTED, with one MAJOR, one MINOR and four NIT findings.
The review bound of `/light` was reached; the operator chose a fix of all six and a narrow round 3
(D6). The fix pass:

- N1: `validate.py` reads each file as UTF-8; under the locale's encoding a BOM hid the title (R1);
- N2: D5 states 194;
- N3: a count inside the eval span of `measurement-baseline.md` fails `TC-SHIP-08` (R6);
- N4: a run of two backticks above the title opens no fence (R4);
- N5: the comment on line ends; N6: the wrap of §0.

## 1. Decisions

- D1, 2026-10-29, operator: Light Mode, one TASK for the three items. The run has the edits with
  their tests, the test run, and one code reviewer with the exhaustive prompt, in at most two
  review cycles (`light-02-develop-task`).
- D2, 2026-10-29, operator: FW-1 — the token counts only in the first H1 of `TASK.md`. Rejected:
  - an HTML-comment marker — the title already carries the mode tag `[LIGHT]`, and task-050 placed
    the token in the title;
  - no change — one mention in prose switches off the RTM check and the PLAN coverage check (§2).
- D3, 2026-10-29, orchestrator: the first H1 is searched, not line 1. In 8 of 1841 task files the
  first H1 stands below `<!-- contract:meta -->` or a Meta block; 3 files have no H1 (§2).
- D4, 2026-10-29, operator: zenuml — the comment only. MA-SYN-07, its message and the test
  `test_keywords_no_pinned_renderer_reads` stay. The comment states the measurements of §2. The
  claim about GitHub leaves it: this run did not measure GitHub.
- D5, 2026-10-29, orchestrator: two new cases pin REG-19: `TC-SHIP-08b` on a list item written in
  the case, and `TC-SHIP-08c` on the copy of `EVAL_SPAN`. The battery grows from 192 to 194, and
  the three document sites state 194.
- D6, 2026-10-29, operator: past the review bound of `/light`, a fix of N1 to N6 and a narrow
  round 3 on the lines of that fix.

## 2. Measurements of this run

- **The bypass on copies of real tasks.** The token added to a decision or an open question of a
  copy, and one requirement ID removed from the copy of its PLAN:

  | Task | ID removed | Now | With the H1 rule |
  | :--- | :--- | :--- | :--- |
  | TASK 132 | R3 | `bypassed`, exit 0 | `NOT covered … ['R3']`, exit 1 |
  | TASK 133 | R5 | `bypassed`, exit 0 | `NOT covered … ['R5']`, exit 1 |
  | whip-insight Task 042 | R11 | `bypassed`, exit 0 | `NOT covered … ['R11']`, exit 1 |

- **The corpus.** 15 repositories under `~/dev-projects` that link or copy the skill hold 1841
  task files (`docs/TASK.md`, `docs/tasks/*.md`).
  - The token occurs in one file: `docs/tasks/task-050-hardening-quality.md:112`, in prose.
  - The first H1 outside a fenced block is on line 1 in 1830 files, below line 1 in 8, absent
    in 3.
  - No file has a front matter block or a setext H1. 4 files have more than one H1.
  - 14 repositories link the skill; `swbera-conversions` holds a copy.
- **zenuml.** `render_check.py --forward` of the fence `zenuml` / `title Probe` / `A->B: hello`:

  | Install | Plugin package | Result |
  | :--- | :--- | :--- |
  | v10, mermaid 10.9.8 | none | rendered; fail: text runs 148.0 px past its box |
  | v11, mermaid 11.17.2 | `@mermaid-js/mermaid-zenuml` 0.2.3 | pass, light and dark |
  | v12, mermaid 12.1.0 | `@mermaid-js/mermaid-zenuml` 1.0.1 | pass |

## 3. Requirements

- R1 (FW-1) — `validate.py` reads the token `[BYPASS_VALIDATION]` only in the first H1 of
  `TASK.md`. The H1 is the first ATX heading of level 1 outside a fenced code block. The rule
  holds in `--mode task` and in `--mode plan`.
- R2 (FW-1) — a token outside that H1 leaves both checks running: in prose, in a fenced line, or in
  a later H1.
- R3 (FW-1) — `SKILL.md` §3 states the rule of R1 and loses the warning about the substring test.
  The skill's version goes from 1.1 to 1.2.
- R4 (FW-1) — tests:
  - the H1 bypasses in both modes, also below a `<!-- contract:meta -->` line, a BOM, a backtick
    line indented four spaces, or a run of two backticks;
  - each placement of R2 does not bypass. Each decoy stands above the title:
    - an h2, indented code, a `#` after U+2028;
    - a fence with a shorter closer, a closer of the other character or with an info string;
    - an unclosed fence;
  - the test that pinned the substring test is inverted;
  - `test_corpus.py` skips a bypassed file by the predicate of R1;
  - the fixture of `tests/test_spec_validator.py` carries the token in its title;
  - `TestEncoding` asserts that each `open(` and `read_text(` of `validate.py` names UTF-8, and
    the suite passes under an ISO-8859-1 locale.
- R5 (REG-19) — `TC-SHIP-08` exempts only the span that `TC-EV-13b` reads. The span runs from a
  `selftest_evals.py` mention to the next full stop. The rest of the list item is read.
- R6 (REG-19) — pins:
  - `TC-SHIP-08b` reads a list item that names both batteries and asserts the counts of this
    battery before the span and after its full stop;
  - `TC-SHIP-08c` asserts that `EVAL_SPAN` of `selftest_scan.py` equals the one of
    `evals/selftest_evals.py`;
  - `SITE_COUNTS` pins the number of counts at each site of `TC-SHIP-08`;
  - a count inside the eval span of a site that `TC-EV-13b` does not read fails `TC-SHIP-08`.

  `EXPECTED_CASES` is 194. The sites state 194:
  - `.agent/skills/artifact-formalizer/SKILL.md:249`;
  - `System/Docs/SKILLS.md:90`;
  - `System/Docs/SKILLS.md:93`.
- R7 (REG-19) — the comment of `EVAL_SPAN` in `evals/selftest_evals.py` states the narrowed
  exemption and cites no numeral of the other battery.
- R8 — the comment above `OTHER_KEYWORDS` in `mermaid_model/kinds.py` states the measurements of §2
  for zenuml. No code changes there.
- R9 — FW-1 and REG-19 are `fixed` in their records and in `docs/KNOWN_ISSUES.md`. Both changelogs
  carry v3.53.1.

**Out of scope.**

- the message of MA-SYN-07 and the name of its test (D4);
- whether GitHub draws a zenuml fence (D4);
- the copy of the skill in `swbera-conversions`, which keeps the substring test;
- the two `INBOUND` records of the archive of TASK 134: `CHANGELOG.md:3865@33e497f` and
  `CHANGELOG.ru.md:3901@33e497f`, slot links that TASK 134 did not write.

## 4. Files

- `.agent/skills/skill-spec-validator/scripts/validate.py`
- `.agent/skills/skill-spec-validator/SKILL.md`
- `.agent/skills/skill-spec-validator/scripts/tests/test_validate.py`, `test_corpus.py`,
  `_fixtures.py`
- `tests/test_spec_validator.py`
- `.agent/skills/artifact-formalizer/scripts/selftest_scan.py`
- `.agent/skills/artifact-formalizer/evals/selftest_evals.py`
- `.agent/skills/artifact-formalizer/SKILL.md`, `System/Docs/SKILLS.md`
- `.agent/skills/mermaid-authoring-guidelines/scripts/mermaid_model/kinds.py`
- `docs/issues/validator-bypass-substring.md`, the record of REG-19, `docs/KNOWN_ISSUES.md`
- `CHANGELOG.md`, `CHANGELOG.ru.md`
- `docs/TASK.md`; the archive pair of TASK 134

<!-- contract:acceptance -->

## 5. Acceptance

- TC-1 — `bash .agent/skills/skill-spec-validator/scripts/tests/run_tests.sh` → OK, with no skip
  inside the repository.
- TC-2 — the copy of TASK 133 with the token in a decision, against the copy of its PLAN without
  R5 → exit 1 and `['R5']`.
  Fails when the bypass reads the whole file.
- TC-3 — `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py` → `194/194`.
- TC-4 — the reproduction of REG-19 with `The 190-case` in `System/Docs/SKILLS.md` → `TC-SHIP-08`
  fails.
- TC-5 — `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py` → `78/78`.
- TC-6 — the full suite, `python3 tests/run_tests.py` → the same result as at the base.
- TC-7 — `scan_register.py` on this TASK and on the edited document lines → no new finding.
