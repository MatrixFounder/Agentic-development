# TASK 102 — artifact-formalizer: the glyph citation convention, and a maintenance rule for narrowing

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 102 |
| Slug | formalizer-glyph-citation-and-narrowing-rule |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Operator request 2026-08-05: resolve WI-14 and WI-15 |
| Depends on | TASK 096, TASK 097, TASK 099, TASK 100, TASK 101 |
| Closes | [WI-14](../backlog/wi-14-glyph-citation-convention-in-authoring-contract.md), [WI-15](../backlog/wi-15-skill-md-6-has-no-rule-for-narrowing-a-rule.md) |
| Archive name | `task-102-formalizer-glyph-citation-and-narrowing-rule.md` |

<!-- contract:problem -->

## 1. Problem

Two gaps, both carried out of [WI-13](../backlog/wi-13-narrow-rule-5-clause-2-to-the-vocabulary-slot.md)
when that record was dropped. Neither depends on the narrowing WI-13 proposed.

**Gap 1 — the contract states the citation convention for one surface only.**
`references/authoring-contract.md` states the code-span convention under "Why code spans". It names
a **marker**. It does not name a **glyph**. A record that reports glyph severities therefore fires
rule 5 on every glyph it quotes.

Measured over the declared scope at `2edf1a2`: 211 documents, 307 `emoji_severity` findings, of
which 26 are a severity-coloured glyph quoted inside a record about glyph severity. They sit in
`wir-11` (12), `wir-2` (10), `task-065` (3) and `wir-4` (1). WI-13 §8 classifies all 26 as not a
defect.

**Gap 2 — `SKILL.md` §6 triages one direction.**

| Rule | Answers |
| :--- | :--- |
| 1 | a test already forbids the phrase — add a faster detector |
| 2 | no test reaches it — amend the contract first |
| 3 | every entry ships with a `probe` |
| 4 | a rule ships only when a measurement supports it |

Rules 1 and 2 route **under**-coverage. Rule 4 gates what a new rule needs before it ships. No rule
states what a proposal to **remove** coverage must produce.

**Why the gap has a cost.** Two events in this repository, both recorded. WI-13 §7.5 identified the
gap while proposing a narrowing, then routed itself through rule 2 — the rule for the opposite
direction. WI-13 §7.2 records P2 as the widening `task-099` D2 had already rejected, re-proposed
with a sample three times smaller than the measured blast radius. Verified: 584 findings erased,
battery `188/191`.

`measurement-baseline.md` §4 keeps refuted candidates on record so nobody re-proposes them from
impression. §6 carries no such record for the widening D2 rejected.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Verified by |
| :--- | :--- | :--- | :--- |
| R1 | `authoring-contract.md` states the code-span convention for a glyph beside the marker it already names | Y | A1, A3 |
| R2 | The same paragraph names the classes the convention does not reach, and states that rule 5 gains no exemption | Y | A1, A3 |
| R3 | `SKILL.md` §6 carries a fifth rule stating what a narrowing produces before it ships | Y | A1, A3 |
| R4 | `measurement-baseline.md` §6 records the widening `task-099` D2 rejected, with its figures | Y | A1, A3 |
| R5 | The battery reports no `emoji_severity` for a glyph inside a code span | Y | A2 |
| R6 | Every document stating the battery size states the pinned total | Y | A2 |
| R7 | No already-filed document is edited to adopt the convention | Y | A5 |

### 2.1 Sub-features

**R1 — the convention, stated for glyphs.** The "Why code spans" paragraph of
`references/authoring-contract.md` states that a marker cited as an example goes in a code span. R1
extends that sentence to a glyph. The scanner already blanks code spans, so no code changes and no
rule changes.

**R2 — the bound.** `known-issues-format` §8 states that a record body is preserved byte-for-byte as
supplied, and that this is what makes it evidence. A machine-filed record therefore cannot adopt the
convention after filing. R2 requires the contract to name that class, and to state that rule 5 gains
no exemption — the scanner still reports those glyphs. A reader of a residual finding then reads a
recorded reason rather than an oversight.

**R3 — the fifth maintenance rule.** A narrowing proposal produces three items before it ships:

1. the population it removes, measured over the **declared** scope, with the scope and the commit
   named;
2. the battery result after the change, since a narrowing that fails a case is a rule the battery
   still asks for;
3. the class the narrowed rule keeps, with one occurrence that the narrowed rule still reports.

**Why point 3.** WI-13 §8 measured zero occurrences of its keep-class over the declared scope, and
§7.3 recorded that the class is unreachable where its vocabulary lives.

**R4 — the rejection on record.** `measurement-baseline.md` §6 states which glyphs rule 5 exempts
and where. It does not state that exempting `` `✅` ``, `` `❌` ``, `` `☑` `` and `` `☒` `` everywhere
was proposed and rejected. WI-13 §7.2 records the re-proposal citing §6 as support. R4 adds the
figures to §6.

**R5 — the battery case.** `TC-FP-02` pins a marker inside a code span at zero findings. No case
pins a glyph. R5 adds one beside it.

**R6 — the case count.** `TC-SHIP-08` asserts every present-tense case count in `SKILL.md`,
`System/Docs/SKILLS.md` and `measurement-baseline.md` equals `EXPECTED_CASES`. R5 moves that total
from 191 to 192.

**R7 — no retroactive edit.** All four documents holding the 26 quoted glyphs are already filed:
three are `provenance: machine` records under R2's bound, and
`docs/tasks/task-065-reviewers-hardening.md` is an archived artifact, immutable per
ARCHITECTURE §7.2. The convention therefore binds documents written from now on, and removes no
existing finding. D2 records the reverted attempt.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — an author files a record about glyph severity.**
*Actor:* any role writing a TASK, an issue record or a work-item record.
*Precondition:* the author has read `references/authoring-contract.md`.
*Main:* the author quotes a glyph, wraps it in a code span per the stated convention, and the
scanner reports no `emoji_severity` for it.
*Postcondition:* the document is about the register and is not reported as a document in it.

**UC-2 — a maintainer proposes removing detector coverage.**
*Actor:* any role editing `data/register-*.json` or `scan_register.py`.
*Precondition:* a finding class reads as over-coverage.
*Main:* the maintainer reads `SKILL.md` §6, finds rule 5, and produces the three items it names.
*Alternative A1 (at Main):* the keep-class has zero occurrences in scope. The proposal does not
ship, and the measurement goes on record.
*Postcondition:* a re-proposal reads the recorded figures before it is written.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion |
| :--- | :--- |
| A1 | `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py` over `SKILL.md` and `references/*.md` reports 0 `warn`, exit 0 |
| A2 | `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py` reports 192 of 192, exit 0 |
| A3 | `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py --probe` reports 18 detectors live, exit 0 |
| A4 | `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py` reports 0 errors |
| A5 | `emoji_severity` over the declared scope stays at 307, and `git diff` shows no already-filed document edited |
| A6 | `python3 System/scripts/validate_skills.py` reports every skill valid |
| A7 | `PYTHONPATH=. python3 tests/run_tests.py` reports OK |
| A8 | `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py` reports 59 of 59, exit 0 |

<!-- contract:open-questions -->

## 5. Open Questions

**OQ1 — none open.** WI-14 §3 step 2 named four documents. D1 and D2 reduce the reachable set to
zero, and §6 records both reasons. The operator has ruled out new mechanism, so the 26 residual
findings stay reported and the contract states why.

<!-- contract:decisions -->

## 6. Decisions

**D1, 2026-08-05, orchestrator: the three `provenance: machine` records are not edited.**
`known-issues-format` §8 states that a record body is byte-for-byte what was supplied. That property
is what makes the body evidence. Git history records the rule: `wir-11`, `wir-2` and
`wir-4` were created by `5c9da31` and touched again only by `7708e2f`, which changed frontmatter
status keys and added no body edit. Rejected: wrapping the 23 glyphs in those bodies — it rewrites
evidence, which WI-2 records this framework declining to do for the same reason.

**D2, 2026-08-05, orchestrator: `docs/tasks/task-065-reviewers-hardening.md` is NOT edited.** An
earlier draft of this task wrapped its three glyphs, on the reasoning that no verbatim rule reaches
an archived TASK. An adversarial review of that draft produced two facts against it.

1. `docs/ARCHITECTURE.md:273` states that archived artifacts are immutable by doctrine.
2. `docs/backlog/wi-13-narrow-rule-5-clause-2-to-the-vocabulary-slot.md:294` quotes the pre-edit bytes of that line, so the edit falsified a
   quotation inside a closed record.

The edit was reverted. Rejected: amending ARCHITECTURE to carve out a register exception — the
operator has ruled out new mechanism, and the benefit was 3 findings in a population WI-13 §8
already classes as not a defect.

**D3, 2026-08-05, orchestrator: the convention ships with its exemption stated.** WI-14 §3 proposed
the convention without a bound. D1 creates a class the convention cannot reach. Rejected: an
unqualified sentence — a reader of a `wir-*` finding would read it as a document that skipped the
contract.

**D4, 2026-08-05, orchestrator: the rejection record goes in `measurement-baseline.md` §6.** Rule 5
of `SKILL.md` §6 requires a measurement on record. A record placed where the re-proposal does not
read it does not stop a re-proposal. WI-13 §7.2 records the author citing §6 as support for the
option §6's own decision had rejected. Rejected: `docs/backlog/wi-13-*.md` alone — a dropped
work-item is not in the reading path of a maintainer editing rule 5.

**D5, 2026-08-05, orchestrator: WI-14's `value:` frontmatter line is left in place and superseded
in the body.** The line claims the change removes 26 of 307 findings; D1 and D2 reduce the removal
to 0. The resolution blockquote states the measured outcome and names the line it supersedes.
Rejected: rewriting the `value:` line — a closed record's own claim is what the resolution is
answering, and overwriting it hides that the estimate was wrong.

<!-- contract:out-of-scope -->

## 7. Out of scope

| Excluded | Carried by |
| :--- | :--- |
| Any change to rule 5's detector, its glyph sets or its thresholds | WI-13, dropped |
| `--severities` and any vocabulary-slot detector | WI-13 P1, not adopted |
| Widening the unconditional exemption set | `task-099` D2, rejected; WI-13 P2, not adopted |
| Editing any `provenance: machine` record body | D1 |
| `data/register-*.json` | rule 5 has no data-file surface (`scan_register.py:59`) |
