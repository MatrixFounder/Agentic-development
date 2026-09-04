# artifact-formalizer evals — what each instrument measures, and what none of it proves

TASK 101. The skill's two CI gates (`selftest_scan.py`, `scan_register.py --probe`) measure Mode B,
which is a pure function. This directory measures the two halves that are not.

| Axis | Question | Reference value | Grader |
| :--- | :--- | :--- | :--- |
| **A — authoring** | does `references/authoring-contract.md` change what a model writes? | the other arm of the same case | `scan_register.py`, called |
| **B — recall gaps** | does the SKILL.md step B4 reading pass find what no detector reaches? | a key written before the run | exact line and rule match |

Ten cases: six on axis A (both shipped languages, five artifact kinds), four on axis B (three
seeded fixtures and one control). ARCHITECTURE §7.6 states the invariant behind the two reference
values.

**The first campaign's figures live in [`../references/measurement-baseline.md`](../references/measurement-baseline.md) §12**, together with what they do not license. Read §12.2 before quoting §12.1: the headline rate is dominated by table shape, and the long-sentence tail moved the wrong way.

## What none of this proves

A green `selftest_evals.py` says the instrument works. It says nothing about the skill. Only a
campaign — `run_authoring.py`, which spawns agents — produces evidence about Mode A, and a
single-repetition campaign carries no interval (`advanced-eval-patterns.md` §8).

## Running the instrument selftest with ZERO tokens

```sh
python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py
```

78 cases. It spawns no agent: `run_authoring.spawn` is replaced with a sentinel that raises, and
TC-EV-12 asserts the sentinel was never reached. This is the step wired into CI.

`EXPECTED_CASES` is a literal in the battery, and TC-EV-13b reads the same number out of this file.
A dropped case is then a red run rather than a smaller self-consistent total.

## Running a campaign (this spends tokens)

```sh
python3 .agent/skills/artifact-formalizer/evals/run_authoring.py --reps 1 --model claude-opus-5
python3 .agent/skills/artifact-formalizer/evals/grade_run.py --out evals/report.json
```

`--dry-run` prints every command and spawns nothing. `--reps` must be **odd**.

**Measuring a contract change.** It moves one arm, so re-drawing the other spends tokens to
reproduce a number the committed corpus already holds. Draw the moved arm into its own directory so
the pinned corpus stays intact:

```sh
python3 .agent/skills/artifact-formalizer/evals/run_authoring.py \
  --cases A1 --cases A5 --arm with_contract --reps 3 --jobs 3 \
  --out-root evals/corpus-wi12
```

## The two properties that keep this honest

**The arms differ in one input.** `build_prompt` prepends the contract for `with_contract` and
nothing for `baseline`. TC-EV-06a removes that block and compares the remainder byte for byte
against the baseline prompt. No prompt names a register rule, or both arms would carry the
contract (TC-EV-06c).

**A fixture the scanner reports on is not measuring a gap.** Each axis-B fixture reports `0 warn`
today, and its planted defects sit where §5 declares the detector cannot reach. TC-EV-04 asserts
both per fixture. A lexicon entry added later can break that without touching the fixture, and then
the fixture is re-planted rather than kept as a detector test.

## Isolation

Both arms run under `tempfile.mkdtemp()`. `leaks_above` walks from there up to `$HOME` and refuses a
directory holding `CLAUDE.md`, `.agent`, `.claude`, `AGENTS.md` or `GEMINI.md` — under this
repository the baseline arm would otherwise read the catalogue that names the contract. Every file
and command tool is denied, so the run has no second path to it, and `permission_denials` from the
envelope is recorded per run rather than assumed empty.

`~/.claude` is deliberately outside the walk. It is user-level configuration, identical in both
arms, and it does not hold this skill.

## Reading a result

- `prose_share_of_nonblank` is a **validity guard**, not an outcome. Under `PROSE_FLOOR = 25` the
  case is reported `measured: false` with its reason, and it is excluded from the arm mean.
- `pressed_against_limit` counts documents whose sentence distribution stops at the bound. An arm
  scoring zero `warn` while pressing against the limit was written for the gate
  (`measurement-baseline.md` §8).
- A control case reports `vacuous_recall: true`. Its number is `spurious`, not `recall`.

## R10 — should B4's reading pass be split into three? Measured: no

Step B4 walks every section for the three rules whose detectors declare a recall limit — 3, 4 and
6 — in ONE pass. Registry item R10 (`Universal-skills/docs/text-humanizer-formalizer-improvement-spec.md`)
proposed splitting it into three passes, one rule each, on the strength of Shaib et al. 2025:
a model handed several dimensions at once collapses onto one or two.

The item shipped with its own condition — implement only if a measurement shows a recall gain —
and the decision rule was written into the spec **before** the run.

**The corpus this needed.** The B1–B3 fixtures plant defects of ONE rule each, and a combined
pass already scores recall 1.0 on them, so they cannot answer the question. M1–M4 are **mixed**.
Each carries two defects of rule 3, two of rule 4 and two of rule 6, spread across four to six
sections. The scanner reports `0 warn / 0 info` on all four, so anything found is found by
reading.

**Result.** `claude-opus-5`, 4 fixtures × 3 reps × 2 arms = 24 runs, 0 failures, `$11.96`.

| Arm | rule 3 | rule 4 | rule 6 | all | reported | spurious |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `combined` | 24/24 | 24/24 | 24/24 | **72/72** | 72 | 0 |
| `split` | 24/24 | 24/24 | 24/24 | **72/72** | 72 | 0 |

**The premise did not reproduce, which is more than the verdict needed.** No collapse appeared on
any document, in any repetition, for any rule. M4 is the case built to force it: 219 lines, with defects
at lines 167, 192 and 203. Half sit in the last quarter and two in non-normative sections. The
combined pass missed **nothing** there across three reps.

**Cost, now a number rather than an estimate.** `split` costs **2.83×** ($0.72 against $0.25 per
run). The item's own risk section said triple cost with no gain is pure loss. It is.

**What this does not establish.** The combined arm made no error, so `split` had nothing to
recover. That does not show splitting is useless on ANY corpus — only that at this document size
and defect density there is nothing to split. Reopening the question needs a corpus where the
combined pass actually **misses**: longer documents, denser defects, or subtler ones. Building it
is the next proposal's burden, not this verdict's.

The rig stays: `run_authoring.py --pass-mode combined|split`, pinned by TC-EV-15…15i, and the
four mixed fixtures. The combined arm is byte-identical to what B4 emits today (TC-EV-15g), both
arms are built from the same rule sentences (TC-EV-15c), and a split pass names its own rule and
no other (TC-EV-15d). A future attempt does not start from nothing.

## Files

| File | Role |
| :--- | :--- |
| `evals.json` | the ten cases, schema `formalizer-evals/v1` |
| `prompts/` | six authoring prompts, identical across arms |
| `fixtures/` | three seeded documents, one control, and one key each |
| `run_authoring.py` | the executor — the only script here that spends tokens |
| `grade_run.py` | the deterministic grader; imports `scan_register` |
| `selftest_evals.py` | the instrument battery, 78 cases, zero tokens |
| `corpus/` | the campaign's authored documents plus the metadata that produced them |
| `corpus-wi12/` | the six-run redraw that verified the WI-12 amendment (`--arm with_contract`) |

## Deliberately not here

- **A trigger eval.** `skill-phase-context` governs when the contract loads in this framework, not
  description matching. `run-feedback/evals/README.md` records what a broken trigger probe cost.
- **A pin.** `verify_pin.py` freezes committed numbers, and there was no campaign to freeze when
  this was written (TASK 101 D5).
- **A second harness.** The grader is the shipped scanner. A reimplementation drifts from
  `data/register-*.json` and grades against the previous rule.
