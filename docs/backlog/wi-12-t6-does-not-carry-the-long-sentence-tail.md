---
id: WI-12
type: work-item
status: done
opened_at: 2026-08-05
slug: wi-12-t6-does-not-carry-the-long-sentence-tail
effort: M
value: 'closes the one rule class the first campaign measured as not improved'
source: 'TASK 101 campaign, measurement-baseline.md §12.2'
provenance: human
component: artifact-formalizer
resolved_at: 2026-08-05
resolved_by: 'TASK 101, verified by a six-run redraw (measurement-baseline.md §12.2.1)'
---

# WI-12 — T6 does not carry the long-sentence tail

> **Resolved 2026-08-05 (TASK 101).** `references/authoring-contract.md` now states that a licensed
> form exceeding T6 is rendered as a list, one item per line. Verified by a six-run redraw of the
> `with_contract` arm: documents over the 35-word bound fell from 4 of 6 to 0 of 6 and
> `sentence_length` warns from 5 to 0. No threshold moved. Evidence: `evals/corpus-wi12/`,
> `measurement-baseline.md` §12.2.1.

> **The title records the first framing and is wrong.** Reading the sentences rather than counting
> them moved the finding: T6 carried the tail for prose, and the residue is a collision between two
> licensed forms and the budget. The slug is kept because the index line, the commit and
> `measurement-baseline.md` §12.2 cite it. §"What the sentences turned out to be" carries the
> corrected diagnosis.

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

## What the sentences turned out to be

Counting said "rule 1 did not move". Reading all fourteen over-bound sentences said something else.

| Arm | Over-bound | Composition |
| :--- | ---: | :--- |
| baseline | 6 | running prose in every case: subordinate clauses, parenthetical explanation, justification welded into the statement |
| with_contract | 8 | 5 `In scope` / `Out of scope` enumerations, 3 acceptance criteria, **0 running prose** |

The contract removed the long prose sentence completely. Every survivor is a construct the contract
**told the author to write**:

- `Scope` — `In scope: <enumeration>. Out of scope: <enumeration> (<who carries it instead>)`
- `Test obligation` — `<test id> — <input> → <asserted outcome>; fails when <mutation>`

Both render as one sentence. The `Budget` test forbids that sentence past 35 words. The contract
licensed both and never said how they resolve, so an author following it exactly produced a 52-word
sentence and a scanner finding.

## The fix, in the contract rather than in the threshold

`references/authoring-contract.md` now states that **a licensed form which exceeds T6 becomes a
list**, one item per line, so each item is its own block and is measured on its own. The budget is
not waived and no threshold moves.

The worked conversion added there is the real 52-word sentence from
`evals/corpus/A1/with_contract/rep-2.md`. Rendered as a list its longest block is 7 words, with
nothing added and nothing cut.

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

## The amendment was measured before this record was closed

Six runs, `A1` and `A5`, `with_contract` only, three repetitions each, same prompts and same model.
One input changed: the contract text. `$4.15`. The corpus ships at `evals/corpus-wi12/`.

```sh
python3 .agent/skills/artifact-formalizer/evals/run_authoring.py \
  --cases A1 --cases A5 --arm with_contract --reps 3 --jobs 3 \
  --out-root evals/corpus-wi12
```

| Case | before r1 | r2 | r3 | after r1 | r2 | r3 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 | **36** | **52** | **47** | 32 | 32 | 29 |
| A5 | **47** | 23 | 23 | 26 | 21 | 25 |

Documents over the 35-word bound: **4 of 6 → 0 of 6.** `sentence_length` warns: **5 → 0.** No
document in either set presses against the limit.

**One movement is deliberately not claimed.** `maxim` warns fell 7 to 0 over the same documents. The
seven were one word repeated on seven lines of a single document, and this amendment says nothing
about rule 4. That is a different draw, not an effect.

**A threshold move remained out of scope and was not made.** The bound is still 35 and the target is
still 15.

## Reproduction

```sh
python3 .agent/skills/artifact-formalizer/evals/grade_run.py
```

Reads the committed `evals/corpus/`. The grader is a pure function of the corpus and the shipped
rule files, so the before figures reproduce without spawning an agent, and `TC-EV-14` pins them.
