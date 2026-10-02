# TASK 106 — artifact-formalizer: a test-to-rule map, one name per check, and ASD-STE100 on record

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 106 |
| Slug | formalizer-term-map-and-ste100 |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Operator review 2026-10-02: "should ASD-STE100 be built into artifact-formalizer?" |
| Operator decision | Items Р1, Р2, Р3 and Р5 of that review; Р4 (a terminology rule) deferred |
| Depends on | TASK 101 (eval battery), TASK 102 (§6 rule 5) |
| Archive name | `task-106-formalizer-term-map-and-ste100.md` |

<!-- contract:problem -->

## 1. Problem

Three defects and one missing record, all found while assessing ASD-STE100 against the skill.

**P1 — the eval-battery size is stated wrong in two documents.**
`evals/selftest_evals.py` pins `EXPECTED_CASES = 78`. Two documents state 59:

- `.agent/skills/artifact-formalizer/SKILL.md:263@5b96f01` `` `evals/selftest_evals.py` — 59 cases ``
- `System/Docs/SKILLS.md:94@5b96f01` `runs 59 cases`

Commit `e737c08` moved the battery from 59 to 78 and updated `evals/README.md` only.

**Why no gate caught it.** `TC-SHIP-08` exempts every claim naming `selftest_evals` by design.
`TC-EV-13b` reads `evals/README.md` alone, and asserts only that the substring `78` occurs in it.

**P2 — the two numberings of the six checks have no map.**
`references/authoring-contract.md` numbers the checks as tests T1–T6. The scanner, the guide and
`documentation-standards` §5.5 number them as rules 1–6. The two orders differ:

| Test | Rule |
| :--- | :--- |
| T1 Verifiable | 2 |
| T2 Real subject | 4 |
| T3 Resolvable referent | 6 |
| T4 One claim | 3 |
| T5 Named severity | 5 |
| T6 Budget | 1 |

A scanner finding names a rule, as `§5.5 r3`. `SKILL.md` §6 rule 1 then asks whether a test T1–T6
forbids the finding. No document states which test that is.

**P3 — one name labels two different checks.** `One claim` labels T4 in the contract. `One claim
per sentence` labels rule 1 in three documents. T4 corresponds to rule 3, and rule 1 corresponds to
T6. A reader matching by name reaches the wrong test.

**P4 — ASD-STE100 has no record in the measurement baseline.** The operator review measured six
STE100 rules over `docs/tasks/`. `measurement-baseline.md` §4 exists so that a refuted candidate is
not re-proposed from impression. The figures currently live only in a chat transcript.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Verified by |
| :--- | :--- | :--- | :--- |
| R1 | `SKILL.md` §8 and `System/Docs/SKILLS.md` state the eval-battery size as 78 | Y | A2, A5 |
| R2 | `TC-EV-13b` asserts every count stated after a `selftest_evals.py` mention equals `EXPECTED_CASES` | Y | A2, A5 |
| R3 | The contract's test table carries a column naming the §5.5 rule of each test | Y | A4, A6 |
| R4 | T4 is labelled `Reasoning separated`; `One claim` labels rule 1 only | Y | A4, A6 |
| R5 | `SKILL.md` §6 rule 1 points to the R3 column | Y | A4 |
| R6 | `measurement-baseline.md` §4.2 records ASD-STE100 with its figures and verdicts | Y | A1, A4 |
| R7 | Both changelogs carry the release; the skill's `version` moves 2.1 → 2.2 | Y | A7 |
| R8 | No rule number, test number, scanner output, threshold or data file changes | Y | A1, A3, A7 |

### 2.1 Sub-features

**R1 — two sites.**

1. `SKILL.md` §8, the "Behavioural evals" item: `59 cases` → `78 cases`.
2. `System/Docs/SKILLS.md`, the "Mode C" item: `runs 59 cases` → `runs 78 cases`.
3. `CHANGELOG.md:692@5b96f01` `evals 59/59` and `CHANGELOG.ru.md:704@5b96f01` `evals 59/59` stay
   as written: each states what a past release measured (D6).

**R2 — the pin.**

1. Sites: `evals/README.md`, `SKILL.md`, `System/Docs/SKILLS.md`.
   The `evals/README.md` sentence describing `TC-EV-13b` names all three.
2. A count is every `<n> case(s)` after a `selftest_evals.py` mention, up to the next full stop.
   The numeral and `cases` may sit on two lines. A numeral continuing another number, as in
   `1,078`, is not read as a count.
3. Every count found equals `EXPECTED_CASES`.
4. A present site with no count fails, since deleting the numeral is the same defect as drift.
5. An absent `System/Docs/SKILLS.md` is skipped only where `System/Docs/` is absent, as in a
   vendored copy. In this repository its absence fails.
6. The existing `TC-EV-13b` call is changed in place, so the battery total stays 78 (D3).

**R3 — the column.** Header `§5.5 rule`, values 2, 4, 6, 3, 5, 1 for T1–T6. One paragraph under
the table states that a finding names the rule and the column maps it to the test. The map lives
in the contract only (D2).

**R4 — the label.** One cell edit at
`.agent/skills/artifact-formalizer/references/authoring-contract.md:46@5b96f01` `| T4 | **One claim** |`.
The name repeats rule 3's own
name, so the label itself states the pairing (D1).

**R5 — the pointer.** One sentence in `SKILL.md` §6 rule 1, naming the column R3 adds.

**R6 — the record.** A subsection `### 4.2` after §4.1, in that section's established shape:

1. the source, its issue and date, and its intended reader;
2. the method and scope, with the §11 reproducibility class stated;
3. one row per STE100 rule: measured value and verdict;
4. the one principle carried forward as a candidate, not adopted;
5. what would reopen the record.

**Constraints on R6, from the battery.** `TC-SHIP-08` reads `measurement-baseline.md` for
`<n> cases`. `TC-SHIP-10` parses §4 table rows of three cells whose second cell is digits only.
The new text states no `<n> cases`, and no row verdict begins with `adopted`.

**R7 — release.** Patch release v3.31.2 in `CHANGELOG.md` and `CHANGELOG.ru.md`. `SKILL.md`
frontmatter `version: 2.1` → `2.2`.

**R8 — what stays.** `scan_register.py`, `data/register-*.json`, every rule number 1–6, every test
number T1–T6, the scanner's output format and guidance strings, and the count "six tests". The file
`documentation-standards/SKILL.md` stays unedited.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — an author maps a scanner finding to a test.**
*Actor:* analyst, architect or planner, with the contract loaded.
*Precondition:* the scanner reports `§5.5 r1 sentence_length` on a document the actor wrote.
*Main:* the actor reads the `§5.5 rule` column, finds T6, and applies `SKILL.md` §6 rule 1.
*Alternative A1 (at Main):* the finding is `cell_width` or `cell_sentences`. It carries `§5.1`, no
§5.5 rule, so the column has no row for it; `documentation-standards` §5.1 owns it.
*Postcondition:* the triage names T6, not T1 or T4.

**UC-2 — a maintainer changes the eval-battery size.**
*Actor:* any role editing `evals/selftest_evals.py`.
*Precondition:* the edit adds or removes a `check()` call, so the battery total moves.
*Main:* the maintainer moves `EXPECTED_CASES` and updates every site that states it.
*Alternative A1 (at Main):* one site keeps the old number. `TC-EV-13b` fails and names the site.
*Postcondition:* every stated count equals the pinned literal.

**UC-3 — a maintainer proposes an ASD-STE100 rule.**
*Actor:* any role proposing a register rule.
*Precondition:* the proposal cites ASD-STE100 or a style guide derived from it.
*Main:* the maintainer reads §4.2, finds the rule's measured figure, and meets the reopen condition
before proposing.
*Alternative A1 (at Main):* the proposed rule has no row in §4.2. `SKILL.md` §6 rules 1–4 apply
as they do to any new rule.
*Postcondition:* a re-proposal carries a new measurement, not the old impression.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion |
| :--- | :--- |
| A1 | `scripts/selftest_scan.py` reports 192 of 192, exit 0 |
| A2 | `evals/selftest_evals.py` reports 78 of 78, exit 0 |
| A3 | `scripts/scan_register.py --probe` reports 18 detectors live, exit 0 |
| A4 | `scan_register.py` over `SKILL.md`, `references/*.md` and `docs/TASK.md` reports 0 `warn` |
| A5 | Each R2 mutation gives the outcome listed below; every revert restores 78 of 78 |
| A6 | `grep -rn "One claim" .agent/skills` returns the three rule-1 sites, the §4.2 record, and no T4 label |
| A7 | `git diff --stat` lists only the files `docs/PLAN.md` declares |
| A8 | `check_positional_refs.py --targets-changed` reports no `REFERENT_MOVED` left unrepaired |
| A9 | `System/scripts/validate_skills.py`, `tests/run_tests.py` and `pytest tests/` all pass |

**A5 mutations.** Each is applied alone, on a working copy, and reverted.

1. `SKILL.md` count 78 → 59 — drift in one site.
2. `System/Docs/SKILLS.md` count 78 → 59 — drift in the registry.
3. `evals/README.md` count after the run command 78 → 77 — drift beside a second, correct count.
4. `SKILL.md` numeral deleted — a present site that states no count.
5. `SKILL.md` gains `(59 cases before TASK 106)` after its count — a stale second count.
6. `SKILL.md` count written as `1,078` — a numeral aliasing 78.
7. `System/Docs/SKILLS.md` deleted while `System/Docs/` exists — a missing registry.
8. `SKILL.md` wraps between `78` and `cases` — a legitimate re-wrap.

Mutations 1–7 fail `TC-EV-13b` and name the site. Mutation 8 passes.

**Why mutation 3 drifts rather than deletes.** `evals/README.md` states the count twice. Deleting
one leaves the other, so the site still states a correct count and the case stays green.

<!-- contract:open-questions -->

## 5. Open Questions

**OQ1 — answered at Retro, 2026-10-02.** The deferred terminology rule (review item Р4) is
[WI-19](../backlog/wi-19-measure-term-consistency-before-the-authoring-contract-gains-a-rule-for-it.md).
Owner: operator.

<!-- contract:decisions -->

## 6. Decisions

**D1, 2026-10-02, orchestrator: T4 is renamed; rule 1 keeps its name.** T4's label occurs in one
cell. Rule 1's name occurs in `SKILL.md`, the guide and `documentation-standards` §5.5. The scanner
guidance `Split into one claim per sentence.` also carries it. Rejected: renaming rule 1 — three
files and a scanner output string, against one cell.

**D2, 2026-10-02, orchestrator: the test-to-rule map lives in the contract only.** The contract is
what the authoring phases load, and the map is read during Mode A handoff. Rejected: a second copy
in `SKILL.md` §5 — REG-13 records a restated value drifting in whichever document restated it.

**D3, 2026-10-02, orchestrator: `TC-EV-13b` is widened in place.** Rejected: a new case — it moves
`EXPECTED_CASES` to 79 and with it the three counts R1 corrects.

**D4, 2026-10-02, orchestrator: the STE100 figures carry §11's caveat.** The measuring script is not
vendored, so no shipped command re-runs it. The corpus ships, and §4.2 states the language test and
the ordering key, so the figures can be re-derived. Rejected: vendoring the script — a maintained
file and a battery case for a record whose verdicts are all "not adopted".

**D5, 2026-10-02, operator: no terminology rule ships in this task.** `SKILL.md` §6 rule 4 requires
a measurement before a rule ships, and none exists. Rejected: a T7 — the tests are applied per
sentence, and term consistency is a property of the whole document.

**D6, 2026-10-02, orchestrator: release-bound counts are not edited.**
`CHANGELOG.md:692@5b96f01` `evals 59/59` states that count for the release that measured it.
Rejected: updating it — a correct historical figure would become false.

**D7, 2026-10-02, orchestrator: the review round's findings, applied.** `code-reviewer` and
`security-auditor` ran over tree fingerprint `099216ac0488`, and both returned it unchanged. Fixed
in this task:

- the §4.2 reopen bar, which §4.2's own figures already met, is now a defect rate per rule;
- the §4.2 corpus is selected by `detect_lang()`, which drops four Russian files the first pass
  kept;
- the CHANGELOG states seven rules assessed and four measured;
- `TC-EV-13b` reads every count in a span, spans a re-wrap, and rejects `1,078`;
- the registry is required where `System/Docs/` exists;
- the third-party source link is pinned to commit `7d4a135` and marked as data;
- three sentences that broke T2 or T4 in the new text are rewritten.

**D8, 2026-10-02, orchestrator: three review findings are deferred.**

- `TC-SHIP-10` selects §4 rows by a digit-only second cell, so it cannot read the §4.2 table. The
  case lives in `scripts/selftest_scan.py`, outside this task's file set. The operator chose not
  to file it at Retro.
- `System/Docs/SKILLS.md` states `192-case` in the list item `TC-SHIP-08` exempts. No case reads
  it. Filed at Retro as REG-19.
- A per-site pin on how many counts each site states. Rejected: `TC-SHIP-08` pins values and never
  counts of claims, and a count pin turns every new mention into a test edit.

<!-- contract:out-of-scope -->

## 7. Out of scope

| Excluded | Carried by |
| :--- | :--- |
| A terminology-consistency test or detector | WI-19 |
| `TC-SHIP-08` exempting a whole list item that names `selftest_evals` | REG-19 |
| `TC-SHIP-10` not reading the §4.2 table | not filed; operator decision at Retro |
| Replacing the workflow's `.bak` backups with git rollback | WI-20 |
| Any edit to `docs/tasks/`, `docs/plans/` or ledger record bodies | ARCHITECTURE §7.2, immutable |
| Scanner code, rule files, thresholds | R8 |
