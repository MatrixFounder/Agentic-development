# Task 096.1 — Close Q1 and write the normative short form


> [!IMPORTANT]
> **Superseded in part, 2026-08-04 — recorded, not rewritten.**
>
> This file states the plan as approved. Execution diverged, and the divergence is listed here so
> the plan of record stays readable as history rather than being silently corrected.
>
> | This file says | What shipped | Recorded in |
> | :--- | :--- | :--- |
> | emoji severity is `info` | `warn` — rule 5 admits no author judgement | baseline §6 |
> | rules 3 and 4 ship without a detector on purpose | all six rules reach a detector; 3, 4 and 6 carry DECLARED RECALL LIMITS | baseline §7, SKILL.md §5 |
> | five rules | six rules — rule 6 (private metaphor) was added | documentation-standards §5.5 |
>
> Every other statement in this file still holds. The mechanism, the measurements and the current
> contract live in `.agent/skills/artifact-formalizer/` — SKILL.md §5 for detector coverage,
> `references/measurement-baseline.md` §10 for why each divergence happened.

**Requirements:** R1, R2, R3, R5 · **Acceptance:** A10, A11 · **Stage:** 1 of 6 · **Dependencies:** none

<!-- contract:goal -->

## Goal

Fix the thresholds from the TASK §1.1 measurement, and state the register rules once, in the
document that owns artifact format. Every later task reads its numbers from here.

<!-- contract:changes -->

## Changes

### Decision — Q1, sentence-length bound

`warn` at **35 words**. Justification recorded in §5.5:

| Corpus | Mean | >35 words |
| :--- | ---: | ---: |
| agentic oldest | 5.8 | 0.0% |
| agentic newest | 14.1 | 3.8% |
| onchain newest | 15.4 | 3.6% |

35 sits far above every corpus mean, so a conforming sentence is never flagged. It catches the
3.6–3.8% tail that both newest corpora grew. The oldest corpus mean of 5.8 is not adopted as a
target: those documents were terser than a specification with acceptance criteria needs.

### `documentation-standards` — new §5.5 "Register"

Under 40 lines (A10). States, in this order:

1. **Scope.** Applies to authored prose in any language. Names no language (R3).
2. **Rule 1 — one claim per sentence.** `warn` above 35 words.
3. **Rule 2 — no evaluative markers.** A word asserting a judgment the reader cannot check does not
   belong in a document of checkable requirements. Per-language lists live in the skill's data.
4. **Rule 3 — reasoning is separated from requirement.** A requirement sentence states what must
   hold. Its justification goes in a `**Why.**` lead-in or a Notes section, not inside the clause.
5. **Rule 4 — a rule is stated as a rule.** No aphorism or personification in place of a norm.
6. **Rule 5 — emoji are not severity.** Severity is a named value. `info`.
7. **Cross-references, not restatements** (A11): cell width → §5.1; paragraph and list shape → §5.2;
   line length → §5.3. §5.5 owns register only.
8. Pointer to `artifact-formalizer` for the guide, the worked example and the scanner.

<!-- contract:tests -->

## Test cases

- **TC-01** — `wc -l` on `documentation-standards/SKILL.md` is ≤ 401 (baseline 361).
- **TC-02** — Read §5.1, §5.2, §5.3 and §5.5 together. No property is governed by two sections.
- **TC-03** — No sentence in §5.5 constrains which language an artifact uses.
- **TC-04** — Each of the five rules traces to a row of the TASK §1.1 measurement, or to the
  rejected table with its reason.

<!-- contract:acceptance -->

## Acceptance criteria

- [ ] Q1 closed at 35 words, with the measurement table justifying it
- [ ] §5.5 present, under 40 lines, cross-referencing §5.1/§5.2/§5.3 rather than restating
- [ ] No language rule anywhere in the added text
- [ ] Rules 1, 2 and 5 map to measured signals; rules 3 and 4 declared as guide-only (no detector)
- [ ] The four refuted candidates are named as rejected, with their figures

## Notes

**Rules 3 and 4 ship without a detector on purpose.** Aphorism and braided reasoning are the two
defects most visible in the samples and neither is reachable by pattern matching. Stating them in
§5.5 and working them in the guide is the honest treatment. Claiming the scanner covers them would
be the failure mode this framework calls a gate that looks like a check.
