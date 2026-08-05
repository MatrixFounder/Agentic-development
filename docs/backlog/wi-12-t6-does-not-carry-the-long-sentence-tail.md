---
id: WI-12
type: work-item
status: open
opened_at: 2026-08-05
slug: wi-12-t6-does-not-carry-the-long-sentence-tail
effort: M
value: 'closes the one rule class the first campaign measured as not improved'
source: 'TASK 101 campaign, measurement-baseline.md §12.2'
provenance: human
component: artifact-formalizer
---

# WI-12 — T6 does not carry the long-sentence tail

## What was measured

The first behavioural campaign (TASK 101, `evals/corpus/`) ran six authoring prompts through two
arms differing only in `references/authoring-contract.md`. Findings over ten documents per arm:

| Class | baseline | with_contract |
| :--- | ---: | ---: |
| `cell_width` + `cell_sentences` (§5.1) | 499 | 1 |
| `metaphor` (rule 6) | 42 | 0 |
| `marker` (rule 2) | 35 | 13 |
| `maxim` (rule 4) | 9 | 7 |
| `sentence_length` (rule 1) | **6** | **5** |

Rule 1 is the class that did not move. The longest sentence in the campaign is 52 words, written by
the contract arm, against a bound of 35.

## Three repetitions confirm it is systematic, not one draw

`A1` and `A5` ran three times per arm for exactly this question. Longest sentence per repetition:

| Case / arm | rep-1 | rep-2 | rep-3 | over the bound |
| :--- | ---: | ---: | ---: | :--- |
| A1 baseline | 46 | 30 | 39 | 2 of 3 |
| **A1 with_contract** | 36 | **52** | 47 | **3 of 3** |
| A5 baseline | 29 | 32 | 35 | 0 of 3 |
| A5 with_contract | **47** | 23 | 23 | 1 of 3 |

**Verdict: confirmed, and narrower than first stated.** On `A1` the contract arm exceeds the bound
in every repetition, and its worst exceeds the baseline's worst. That is not a sampling artefact. On
`A5` it is one repetition of three.

**The baseline is not a clean comparison.** `A5/baseline/rep-3` stops at exactly 35 words, which
`measurement-baseline.md` §8 counts as the other failure of the same rule: a distribution written
for the gate. Two baseline documents show that shape and no contract-arm document does.

The mean obeys T6 (10.96 to 9.04 words). The tail does not.

## Why this is a work-item and not a defect

No contract is broken. T6 states the rule, states 35 as a failure bound rather than a target, and
names 15 words as the target. `SKILL.md` §5 promises no rule is fully prevented by Mode A. The
measurement says T6 is carried less reliably than T1 to T4, which is a signal about the contract's
wording rather than a violated obligation.

## What the campaign does not settle

- Six prompts. Repetitions reduce sampling noise inside a case and do nothing for the diversity of
  the set.
- Why `A1` and `A5` and not the other four. Document length does not explain it: `A2/with_contract`
  is the longest contract-arm document at 359 lines and its longest sentence is 30 words.
- Whether the cause is the wording of T6, its position in the contract, or the absence of a worked
  conversion for a sentence that is one claim and still over the bound.

## Candidate actions, none applied

1. Add a worked conversion to `references/authoring-contract.md` for a single-claim sentence over
   the bound. Every existing T6 example is a sentence that is also two claims.
2. State the target as a per-sentence check rather than a corpus mean, since the mean improved while
   the tail did not.
3. Measure any wording change against the committed corpus. `A1 with_contract` at 3 of 3 over the
   bound is the figure a fix has to move, and `TC-EV-14` pins it.

**A threshold move is out of scope.** `measurement-baseline.md` §11 requires that from a corpus, and
this one is 12 documents drawn once.

## Reproduction

```sh
python3 .agent/skills/artifact-formalizer/evals/grade_run.py
```

Reads the committed `evals/corpus/`. The grader is a pure function of the corpus and the shipped
rule files, so the figures above reproduce without spawning an agent.
