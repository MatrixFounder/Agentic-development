# Task 096.3 — Masking pass and structural checks


> [!IMPORTANT]
> **Superseded in part, 2026-08-04 — recorded, not rewritten.**
>
> This file states the plan as approved. Execution diverged, and the divergence is listed here so
> the plan of record stays readable as history rather than being silently corrected.
>
> | This file says | What shipped | Recorded in |
> | :--- | :--- | :--- |
> | emoji severity is `info` | `warn` | baseline §6 |
> | the masker handles single-backtick code spans | any backtick run, across line breaks; tilde and unterminated fences | baseline §10 |
>
> Every other statement in this file still holds. The mechanism, the measurements and the current
> contract live in `.agent/skills/artifact-formalizer/` — SKILL.md §5 for detector coverage,
> `references/measurement-baseline.md` §10 for why each divergence happened.

**Requirements:** R12, R4, R8 · **Stage:** 3 of 6 · **Dependencies:** 096.2

<!-- contract:goal -->

## Goal

Make matching honest before any marker list is applied, then implement the checks that need no
lexicon and therefore work in every language.

<!-- contract:changes -->

## Changes

### Masking (R12) — runs before every matcher

Replace with same-length filler, so line and column numbers survive:

| Construct | Reason |
| :--- | :--- |
| Fenced blocks ` ``` ` | Code is not prose |
| Inline code spans `` ` `` | Measured: 6 of 6 evaluative hits in `docs/TASK.md` were cited markers inside backticks |
| Link targets `](...)` | A path is not prose; link **text** stays scannable |
| HTML comments | Carries the `<!-- contract:* -->` anchors |
| Table delimiter rows | Not prose |

### Structural checks — language-independent (R4)

- **Sentence length.** Block-aware segmentation. A block ends at a blank line, heading, table row,
  fence, HTML comment, or list marker; each list item is its own block. Sentences split inside a
  block only.
- **Table cell width.** Reports against §5.1's existing 120-character bound. §5.5 adds no rule
  here; the scanner surfaces the rule that already exists.
- **Emoji as severity.** Reported at `info`.

### Exit discipline (R8)

Findings never change the exit code. `0` on any number of findings; `2` only for a broken rule file
or unreadable input.

<!-- contract:tests -->

## Test cases

- **TC-MASK-01…04** turn green, plus the plain-prose control.
- **TC-STRUCT-01…03** turn green.
- **TC-EXIT-01** turns green: a file full of findings exits 0.
- **TC-REG-01** — the block-aware segmenter is pinned against the defect that produced the first,
  discarded measurement: a run of `- [ ]` lines must yield one sentence per item, never one
  pseudo-sentence of 100+ words.
- **TC-REG-02** — masking preserves line numbers: a marker on line 40 is reported at line 40 with
  a code span earlier in the file.

<!-- contract:acceptance -->

## Acceptance criteria

- [ ] All masking cases green, including the control that proves masking is not blanket suppression
- [ ] Structural cases green in both a Cyrillic and a Latin fixture
- [ ] TC-REG-01 pins the checklist-glue defect that invalidated the first measurement
- [ ] Exit code is 0 on a fixture carrying at least one finding of every structural kind
- [ ] Lexical cases still failing — this task does not touch them

## Notes

**The control case matters more than the masking cases.** Masking that suppresses everything would
pass all four TC-MASK cases and detect nothing. The plain-prose control is what separates masking
from blanket suppression.
