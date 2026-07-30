# run-feedback evals — provenance and how to run them

Two independent instruments live here. They measure different things and fail in
different ways; conflating them is how a broken probe got read as a bad skill.

| file | measures | grader | cost |
|---|---|---|---|
| `trigger_eval_set.json` | does the **`description:`** cause the skill to load? | `skill-creator/scripts/run_eval.py` | real `claude -p` runs |
| `evals.json` (19 cases) | does the **skill body** produce correct judgement? | `grade_run.py`, a pure function | real agent runs; grading is free |

## ⚠️ The last recorded trigger-eval result is instrument failure, not data

The 2026-07-13 run recorded **0 triggers across 69 runs** — which is exactly
`23 queries × 3 runs`, i.e. *every* query. That was
[VAL-2](../../../docs/issues/val-2-run-eval-py-trigger-probe-false-negatives-name-competition-with-installed-skill-and-first-call-strictness.md),
a defect in the probe:

* the probe registered a uuid-suffixed **clone** of the skill and only counted that
  name, so when the real skill was installed the model rationally invoked the
  canonical name and scored "not triggered";
* the detector returned False unless the **first** tool call named the probe, so a
  model that oriented itself with `Bash` first scored "not triggered".

Consequence for the recorded numbers: **12 positives failed falsely and 11
negatives passed vacuously**, for a summary of 11/23 that looks half-plausible
rather than obviously broken. Do not cite that run, and do not change the
`description:` on its evidence. VAL-2 was fixed on 2026-07-30; the first run after
the fix is the first usable measurement.

Four queries carry `"instrument_sensitive": true` — they name a concrete file path
or a sibling skill, so they were the ones VAL-2's two mechanisms hit hardest. The
key is inert (`run_eval` reads only `query` / `should_trigger`); it is a note to the
next human.

## Running the trigger set

```sh
python3 .agent/skills/skill-creator/scripts/run_eval.py \
  --eval-set .agent/skills/run-feedback/evals/trigger_eval_set.json \
  --skill-path .agent/skills/run-feedback \
  --runs-per-query 3 --verbose
```

**`--runs-per-query` must be ODD.** The threshold is `rate >= 0.5` for positives and
`rate < 0.5` for negatives, so an even value makes an exact 50/50 split decide by
which side of the comparison it lands on — a coin flip recorded as a result.

The skill is installed in this repo, so `run_eval` reports `canonical_matches` per
query and warns at startup: a canonical-name trigger may have been caused by the
**installed** description rather than the candidate one under test. That confound is
inherent to probing a skill in a repo that already has it; the number is reported
rather than hidden.

## Running the behavioural suite with ZERO tokens

None of this spawns an agent. It verifies the *instrument*, never the skill:

```sh
cd .agent/skills/run-feedback/evals
python3 grade_run.py --lint     # every check type exists and is configured
python3 selftest.py             # golden runs score 1.00; violators are caught
```

`selftest.py` also prints which cases have **no violator transcript** — their checks
are proven reachable but never proven to *fire*. Treat that list as the honest
coverage statement it is.

What none of it proves: that a change to `SKILL.md` improves agent behaviour. Only
real runs do.

## The pin

`pinned/iteration-5-v1.2/` is a frozen historical benchmark from the iteration-5
campaign. `verify_pin.py` re-runs the aggregation math over the committed
`grading.json` files; it never reads `evals.json`, so **editing the evals cannot
break the pin** — and equally, the pin's numbers do not describe the current suite.
Its `PROVENANCE.txt` records SKILL.md v1.2 while the shipped skill is v1.4, and case
17's prompt has since been rewritten. When you next spend a campaign, mint a new
sibling directory (`pinned/iteration-N-v<skill-version>/`) rather than amending it.

## Lockstep obligations when editing `evals.json`

1. `checks[i].text` must equal `expectations[i]` **verbatim**, same order, and
   likewise for `forbidden_*` — `grade_run.py` exits **2** rather than grading
   otherwise.
2. Every case **must** have a golden transcript in `selftest.py`'s `gold()`, or the
   selftest hard-fails. A violator is optional but is the only thing that proves the
   case's checks can fire.
3. A violator's `expect_failed` entries match check texts by **exact string** — so
   retexting a check means editing `selftest.py` in the same change.
4. New check texts want a keyword row in `analyze_rules.py`'s `RULES`, or they drop
   silently out of the per-rule verdict table.
5. A newly-seeded component needs a row in `harness.py`'s `CONFIG['id_prefixes']`
   (or a deliberate omission, as case 16 does).
