# TASK 101 — artifact-formalizer: behavioural evals for Mode A and the §5 recall gaps

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 101 |
| Slug | formalizer-behavioural-evals-mode-a-and-recall-gaps |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Operator request 2026-08-05: build the minimal eval set, two axes, 8–12 cases |
| Depends on | TASK 096, TASK 097, TASK 099, TASK 100 |
| Closes | no ledger record; this task opens a measurement, it does not fix a defect |
| Archive name | `task-101-formalizer-behavioural-evals-mode-a-and-recall-gaps.md` |

<!-- contract:problem -->

## 1. Problem

`artifact-formalizer` ships three CI steps and two instruments. All of them measure Mode B.

| Instrument | Covers | Evidence today |
| :--- | :--- | :--- |
| `selftest_scan.py` | the scanner as a pure function | 191 cases, exit 0 |
| `scan_register.py --probe` | the detector roster | 18 detectors, exit 0 |
| Mode A, the authoring contract | what a model writes | none |
| §5 reading pass (B4) | rules 3, 4 and 6 beyond the detectors | none |

`SKILL.md` §Purpose states the order: "Mode A prevents the defect; Mode B measures what Mode A
missed." It quotes 5.1% of a corpus's words against reading 14,288 to remove them. The value the
skill claims is therefore Mode A's, and no number in this repository describes Mode A.

§5 declares a recall limit for three of six rules and assigns the remainder to a reading pass. Step
B4 instructs that pass over the `--sections` worklist. No measurement states what that pass finds.

`references/measurement-baseline.md` §11 records the third gap in its own words. Every figure from
the ten-file downstream corpus is not reproducible here. That section requires a future threshold
move to be justified from a corpus that ships with the skill. No such corpus ships.

**Why this is the failure class the skill names.** The gates report `18/18 detectors live` and exit
0. The claim carrying the skill's stated value stays untested. `measurement-baseline.md` §2 records
the same shape: a zero and a working instrument differ only in what the instrument was pointed at.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Verified by |
| :--- | :--- | :--- | :--- |
| R1 | An executor produces authored artifacts under two arms that differ only in the contract | Y | A1, A2 |
| R2 | The grader calls `scan_register.py` and reimplements no threshold or finding rule | Y | A3 |
| R3 | Axis B fixtures carry planted defects that the scanner does not report | Y | A4 |
| R4 | The eval instrument carries a selftest that spawns no agent | Y | A5 |
| R5 | The authored outputs ship as the corpus §11 requires | Y | A6 |
| R6 | The report states what the run did not cover | Y | A7 |
| R7 | The eval set holds 8 to 12 cases across both axes | Y | A8 |

### 2.1 Sub-features

**R1 — the executor.** `evals/run_authoring.py` runs each Axis A case twice. Both arms receive the
same task prompt, the same working directory shape and the same model. The `with_contract` arm
additionally receives the text of `references/authoring-contract.md`. No other input differs.

**Why one variable.** `skill-creator/references/advanced-eval-patterns.md` §7 attributes a delta to
a change only when the two arms differ in one input.

**Why an isolated working directory.** A run under this repository loads `CLAUDE.md`, which names
the skill catalogue. The baseline arm would then read the contract that defines the arm. `~/.claude/
skills/` does not hold `artifact-formalizer`, so a directory outside this repository isolates it.
The executor asserts the directory holds no `CLAUDE.md`, no `.agent/` and no `.claude/`.

**Why every tool is denied.** The authoring task needs no tool. Denying the file and command tools
removes the second path to the contract, and it removes the agent's ability to write anywhere. The
executor records `permission_denials` from the run envelope, so an attempted read is visible rather
than assumed absent.

**R2 — the grader.** `evals/grade_run.py` imports `scan_register` and calls it on each authored
document. It reads four values from the scanner's JSON and derives no finding of its own.

| Value | Derivation | Role |
| :--- | :--- | :--- |
| `warn_per_100_lines` | `len(warn) / lines × 100` | outcome |
| `marker_per_100_lines` | `findings_by_kind.marker / lines × 100` | outcome |
| `sentence_mean` | `diagnostics.sentence_mean` | outcome |
| `prose_share_of_nonblank` | `diagnostics.prose_share_of_nonblank` | validity guard |
| `sentence_pressure` | `diagnostics.sentence_pressure` | outcome |

**Why per 100 lines.** `measurement-baseline.md` §1 states the corpus baseline in evaluative markers
per 100 lines. The eval reports the same unit, so the two tables can be read together.

**Why the prose share is a guard and not an outcome.** A document padded with fenced blocks lowers
every per-line rate without changing a sentence. The share names how much of the document reached
rule 1. `SKILL.md` §2 already assigns it that role.

**Why `sentence_pressure` is reported.** T6 states that 35 words is the failure bound and not the
target. An arm scoring zero `warn` with the distribution pressed against the limit was written for
the gate; `measurement-baseline.md` §8 measured that shape.

**R3 — the Axis B fixtures.** Each fixture is a specification-shaped document carrying planted
defects of rules 3, 4 or 6 that the detectors do not reach:

- rule 3 — the obligation and its justification split across two sentences;
- rule 4 — an aphorism written for this fixture, matching no maxim template;
- rule 6 — a metaphor coined for this fixture, absent from both candidate lists.

Each fixture ships an answer key naming the planted lines and the rule. One fixture is a **control**
carrying no planted defect.

**Why a control.** `advanced-eval-patterns.md` §6 states that a positive-only set measures recall
and is blind to over-firing.

**Why the answer key is the ground truth.** The defects are planted mechanically, so the key is
objective by construction and carries no author judgement about what a real document meant.

**R4 — the instrument selftest.** `evals/selftest_evals.py` runs without spawning an agent and
asserts:

1. the grader scores a known-conforming document and a known-defective one, and the second scores
   higher on every outcome metric;
2. the Axis B scorer returns recall 1.0 and precision 1.0 for a golden answer, and lower values for
   an answer that misses one planted defect and invents one;
3. **the fixture invariant** — `scan_register.py` reports no `warn` on any planted line of any
   fixture;
4. the control fixture carries no planted line and no `warn`.

**Why the fixture invariant is an assertion and not a comment.** A fixture whose planted defect the
scanner reports measures the detector, not the gap. A lexicon entry added later can move a fixture
into that state without touching the fixture.

**R5 — the corpus.** Every authored document is written under `evals/corpus/<case>/<arm>/` and
committed with the run metadata that produced it: model, timestamp, prompt hash, contract hash.

**Why the hashes.** A corpus whose inputs are not recorded cannot support the threshold move §11
requires it to support.

**R6 — the honest report.** `grade_run.py` writes `grading.json` and prints a summary naming the
number of cases, the number of repetitions per arm, and every case that produced no output. A case
whose validity guard falls below the declared floor is reported as **not measured** rather than as
a value.

**R7 — the set size.** Six Axis A cases and four Axis B fixtures, ten in total. The Axis A cases
span both shipped languages and four artifact kinds.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — a maintainer asks whether the contract changes what a model writes.**

*Actor:* framework maintainer. *Main:* runs `run_authoring.py`, then `grade_run.py`; reads the
per-arm means. *Postcondition:* a number per metric per arm, and the documents that produced it.

**UC-2 — a maintainer changes a threshold and must justify it.**

*Actor:* framework maintainer. *Main:* scans `evals/corpus/` with the candidate threshold and
compares against the committed figures. *Postcondition:* the justification §11 requires, from a
corpus that ships here.

**UC-3 — a maintainer asks what the reading pass finds that the detectors do not.**

*Actor:* framework maintainer. *Main:* runs the Axis B cases; reads recall against the answer keys
and precision against the control. *Postcondition:* a recall figure for the §5 gaps of rules 3, 4
and 6.

**UC-4 — a contributor adds a lexicon entry that reaches a planted defect.**

*Actor:* contributor. *Main:* runs `selftest_evals.py`. *Postcondition:* the fixture invariant fails
and names the fixture, so the fixture is re-planted rather than converted into a detector test with
no failing case.

**UC-5 — a reviewer asks what the campaign did not measure.**

*Actor:* reviewer. *Main:* reads the report and `evals/README.md`. *Postcondition:* the uncovered
surfaces are named: triggering, and any case whose validity guard failed.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion | Command |
| :--- | :--- | :--- |
| A1 | Both arms of one case differ only in the contract input | `selftest_evals.py`, prompt-identity case |
| A2 | The executor refuses a working directory holding `CLAUDE.md`, `.agent/` or `.claude/` | `selftest_evals.py`, isolation case |
| A2.1 | The executor denies the file and command tools, and records `permission_denials` per run | `selftest_evals.py`, command-shape case |
| A3 | The grader imports `scan_register` and declares no threshold of its own | `selftest_evals.py`, no-reimplementation case |
| A4 | Every planted line of every fixture carries no `warn` | `selftest_evals.py`, fixture invariant |
| A5 | `python3 evals/selftest_evals.py` exits 0 and spawns no subprocess named `claude` | the run itself |
| A6 | `evals/corpus/` holds one document per case per arm, each with its metadata file | `ls`, and the selftest's corpus-shape case |
| A7 | The printed summary names cases, repetitions, empty outputs and unmeasured cases | `selftest_evals.py`, report case |
| A8 | `evals.json` holds 10 cases: 6 on Axis A, 4 on Axis B | `selftest_evals.py`, set-size case |
| A9 | The campaign runs and its results are recorded in `measurement-baseline.md` | the committed report |

<!-- contract:open-questions -->

## 5. Open Questions

**OQ1 — repetitions per arm.** `advanced-eval-patterns.md` §8 asks for several samples per arm when
a metric jitters. Blocks: the confidence statement in the report. Owner: operator. Default applied:
one repetition for the first campaign, with `--reps` accepting an odd value, and the report stating
that a single draw carries no interval.

**OQ2 — the model.** The executor pins a model so a rerun is comparable. Blocks: nothing; the value
is recorded either way. Owner: operator. Default applied: `claude-opus-5`, recorded per run.

<!-- contract:decisions -->

## 6. Decisions

**D1, 2026-08-05, orchestrator: the grader is `scan_register.py`, called as a module.** Rejected:
an LLM judge — it costs tokens per grading and is not reproducible, and
`advanced-eval-patterns.md` §1 assigns structured output to a script grader.

**D2, 2026-08-05, orchestrator: the headline unit is per 100 lines, with the prose share reported
beside it.** Rejected: per 100 prose lines — it is not the unit `measurement-baseline.md` §1 states,
so the two tables would not compare.

**D3, 2026-08-05, orchestrator: the executor captures stdout and writes no file through the agent.**
Rejected: instructing the agent to use the Write tool — a headless run cannot answer a permission
prompt, and a denial would be recorded as an empty document.

**D4, 2026-08-05, orchestrator: no second harness.** `run-feedback/evals` holds roughly 160 KB of
grading code and five lockstep obligations. This task adds three scripts and reuses the scanner.
Rejected: copying `grade_run.py` — a second instrument reports a clean run while its own checks are
broken, and that state is what this skill exists to catch.

**D5, 2026-08-05, orchestrator: no pin in this task.** `verify_pin.py` freezes committed numbers.
Rejected: pinning now — there are no campaign numbers yet, and a pin over an empty campaign asserts
nothing.

**D5.1, 2026-08-05, operator: D5 is reversed once the campaign has numbers.** D5 deferred the pin
because there was nothing to freeze. The first campaign removed that reason, so `TC-EV-14`
re-derives the committed `report.json` from the committed corpus and fails on any drift. Rejected:
`verify_pin.py` — it re-aggregates `grading.json` files under a `benchmark.json` schema this grader
does not emit, so using it would mean writing a second report shape.

**D5.2, 2026-08-05, operator: repetitions are targeted rather than uniform.** OQ1 asked for an odd
count per arm. Applied: three repetitions for `A1` and `A5`, one for the rest. **Why.** Those two
documents carry the whole rule-1 finding of §12.2, and three draws separate a systematic effect
from a sampling artefact at a quarter of the cost of a uniform three-repetition campaign. The arm
means therefore rest on documents of unequal repetition count, which `measurement-baseline.md` §12
states.

**D6, 2026-08-05, orchestrator: Axis B is graded against a planted key, not against the scanner.**
Rejected: grading the reading pass by comparison with `scan_register.py` output — the pass exists to
find what the scanner does not, so the scanner cannot be its reference.

<!-- contract:out-of-scope -->

## 7. Out of scope

| Excluded | Who carries it instead |
| :--- | :--- |
| Trigger evaluation of the `description:` field | deferred; `skill-phase-context` governs the load path, not description matching |
| Reproducibility pinning through `verify_pin.py` | a later task, once a campaign has numbers (D5) |
| Any change to `scan_register.py`, its data files or its thresholds | out of scope by construction; this task measures the skill, it does not move it |
| An LLM-judge grader | rejected in D1 |
| Wiring the campaign itself into CI | the selftest is wired; a campaign spawns agents and costs tokens per run |
