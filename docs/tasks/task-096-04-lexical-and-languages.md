# Task 096.4 — Lexical rules, per-language data, language resolution


> [!IMPORTANT]
> **Superseded in part, 2026-08-04 — recorded, not rewritten.**
>
> This file states the plan as approved. Execution diverged, and the divergence is listed here so
> the plan of record stays readable as history rather than being silently corrected.
>
> | This file says | What shipped | Recorded in |
> | :--- | :--- | :--- |
> | an entry is marker + pattern + guidance | `probe` is required and is validated against the entry's own pattern | SKILL.md §2 |
>
> Every other statement in this file still holds. The mechanism, the measurements and the current
> contract live in `.agent/skills/artifact-formalizer/` — SKILL.md §5 for detector coverage,
> `references/measurement-baseline.md` §10 for why each divergence happened.

**Requirements:** R4, R7, R8 · **Stage:** 3 of 6 · **Dependencies:** 096.3

<!-- contract:goal -->

## Goal

Apply the per-language marker lists over masked text, and make an unknown language a reported
condition rather than an error.

<!-- contract:changes -->

## Changes

**`warn` markers, RU** — `разумеется`, `очевидно`, `попросту`, `на самом деле`, `стоит отметить`, `важно понимать`, `элегантно`, `честно`.

**`warn` markers, EN** — `of course`, `obviously`, `merely`, `indeed`, `it is worth noting`, `elegant`, `nothing more than`.

### Marker lists

`data/register-ru.json` and `data/register-en.json`, seeded from the markers that the TASK §1.1
measurement actually counted.

| Severity | Contents | Reason |
| :--- | :--- | :--- |
| `warn` | evaluative and marketing markers — enumerated below the table |
| `info` | `ровно`, `именно`; `precisely`, `exactly`, `simply`, `the very` | Sometimes load-bearing (TASK Q2) — "read in exactly one place" is a real constraint |

Each entry carries `guidance`, not a replacement: the author rewrites the sentence.

### Language resolution

Cyrillic-share heuristic, overridable with `--lang`. A language with no rule file is **not** an
error (R4): structural checks run, lexical findings are zero, and stderr states the resolved
language and that no lexicon backed it. Silence here would read as a clean document.

### Extensibility (R7)

Adding a marker is a data edit. Adding a language is a new `data/register-<lang>.json`. Tuning the
sentence bound is `thresholds.sentence_max_words`. None of these touch `scan_register.py`.

<!-- contract:tests -->

## Test cases

- **TC-LEX-01…02** green: a `warn` and an `info` marker reported at their own severities.
- **TC-LANG-01…03** green, including the no-lexicon diagnostic on stderr.
- **TC-DATA-01** green: a fixture rule file introduces a marker absent from the shipped data and it
  is reported, with `scan_register.py` unmodified.
- **TC-FP-01** — false-positive controls. `именно` inside a code span is silent (masking, 096.3);
  `точно` as an adverb of measurement is not a marker; `simply` inside a quoted requirement is
  reported at `info`, never `warn`.
- **TC-FP-02** — `docs/TASK.md` scans at **zero `warn`**. Its six known evaluative occurrences are
  all inside backticks and must all be masked.

<!-- contract:acceptance -->

## Acceptance criteria

- [ ] Full selftest battery green
- [ ] `docs/TASK.md` and `docs/PLAN.md` scan at zero `warn` (A8)
- [ ] A new marker requires no code edit, proven by TC-DATA-01
- [ ] Unknown language: structural findings still reported, diagnostic on stderr, exit 0
- [ ] Every shipped marker traces to the TASK §1.1 lists; none invented at implementation time

## Notes

**Q2 is closed here.** `именно` and `exactly` ship at `info`, not `warn`. Both have a legitimate
use in a specification — naming an exact count or an exact location — and the measurement cannot
distinguish that use from rhetorical emphasis. An `info` severity puts the judgment where it
belongs, with the author.
