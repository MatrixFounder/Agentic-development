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

59 cases. It spawns no agent: `run_authoring.spawn` is replaced with a sentinel that raises, and
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

## Files

| File | Role |
| :--- | :--- |
| `evals.json` | the ten cases, schema `formalizer-evals/v1` |
| `prompts/` | six authoring prompts, identical across arms |
| `fixtures/` | three seeded documents, one control, and one key each |
| `run_authoring.py` | the executor — the only script here that spends tokens |
| `grade_run.py` | the deterministic grader; imports `scan_register` |
| `selftest_evals.py` | the instrument battery, 59 cases, zero tokens |
| `corpus/` | the campaign's authored documents plus the metadata that produced them |
| `corpus-wi12/` | the six-run redraw that verified the WI-12 amendment (`--arm with_contract`) |

## Deliberately not here

- **A trigger eval.** `skill-phase-context` governs when the contract loads in this framework, not
  description matching. `run-feedback/evals/README.md` records what a broken trigger probe cost.
- **A pin.** `verify_pin.py` freezes committed numbers, and there was no campaign to freeze when
  this was written (TASK 101 D5).
- **A second harness.** The grader is the shipped scanner. A reimplementation drifts from
  `data/register-*.json` and grades against the previous rule.
