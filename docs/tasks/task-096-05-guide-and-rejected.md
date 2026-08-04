# Task 096.5 — Formalization guide, worked example, rejected-candidates table


> [!IMPORTANT]
> **Superseded in part, 2026-08-04 — recorded, not rewritten.**
>
> This file states the plan as approved. Execution diverged, and the divergence is listed here so
> the plan of record stays readable as history rather than being silently corrected.
>
> | This file says | What shipped | Recorded in |
> | :--- | :--- | :--- |
> | the scanner covers three of five rules | the scanner reaches all six, three with declared recall limits | SKILL.md §5 |
> | aphorism and braided reasoning have no detector | both have detectors with stated limits; the reading pass owns the remainder | baseline §7 |
> | the guide is the only treatment for the undetectable rules | `references/authoring-contract.md` (Mode A) is the primary treatment; the guide is Mode B | SKILL.md §Purpose |
>
> Every other statement in this file still holds. The mechanism, the measurements and the current
> contract live in `.agent/skills/artifact-formalizer/` — SKILL.md §5 for detector coverage,
> `references/measurement-baseline.md` §10 for why each divergence happened.

**Requirements:** R2, R6 · **Stage:** 4 of 6 · **Dependencies:** 096.1, 096.4

<!-- contract:goal -->

## Goal

Write the reading pass. The scanner covers rules 1, 2 and 5 of §5.5. Rules 3 and 4 — braided
reasoning and aphorism-instead-of-rule — have no detector, and the guide is where they are caught.

<!-- contract:changes -->

## Changes

### `references/formalization-guide.md`

- **Register rules**, expanded from §5.5 with the reasoning §5.5 has no room for.
- **Worked example.** Input is a real paragraph from `docs/tasks/task-012-9-paid-leg-boundary.md`
  (the operator's cited example). Output is the same content as specification. A third column
  states which defect each rewrite removes. The example is Russian, and the guide states that the
  rewrite never changes the document's language.
- **Scope of a pass.** Rewrite: over-long sentences, evaluative markers, aphorisms, reasoning
  braided into a requirement clause. Leave alone: terminology, numbers, identifiers, quoted
  requirements, already-conforming sentences.
- **The specification test.** For each rewritten sentence: can a reader who was not in the
  discussion verify this claim from the document alone?

### Rejected candidates (R2) — in `SKILL.md`

| Candidate | Measured | Verdict |
| :--- | :--- | :--- |
| Bold density | 9.1 vs 30.7 per 100 lines, newest vs older | improved — no rule |
| Em-dash density | 12.2 vs 22.8 per 100 lines | improved — no rule |
| Emoji density | 0.0 vs 8.7 per 100 lines (agentic) | improved here, rose downstream — see the banner |
| Table-cell prose | 22% of cells over 120 chars | real, owned by §5.1 |

### Red Flags table — in `SKILL.md`

| Rationalization | Reality |
| :--- | :--- |
| "I'll add a pattern for this new phrasing" | markers are data — add an entry, the script never changes |
| "The scan is clean, so the text is clean" | three rules carry declared recall limits — see the banner |
| "The whole document reads badly — I'll rewrite it" | conforming sentences stay verbatim; over-rewriting adds errors |
| "I'll shorten it by cutting the requirement" | register changes, substance does not — numbers and obligations survive |
| "This word is fine, I'll widen the threshold" | a failing scan is fixed in the prose, never by moving a threshold |

<!-- contract:tests -->

## Test cases

- **TC-DOC-01** — every rule in §5.5 appears in the guide, and the guide adds no sixth rule.
- **TC-DOC-02** — the worked example's output scans at zero `warn` under the shipped scanner.
- **TC-DOC-03** — the four rejected candidates carry the figures from the TASK §1.1 measurement.
- **TC-DOC-04** — the guide states no rule about which language an artifact uses (R3).

<!-- contract:acceptance -->

## Acceptance criteria

- [ ] Guide present, covering all five rules, with the two undetectable ones marked as such
- [ ] Worked example uses real prose from the cited corpus, not an invented sample
- [ ] The rewritten output passes the scanner it ships beside
- [ ] Rejected-candidates table carries measured figures, not assertions
- [ ] Red Flags table present in `SKILL.md`

## Notes

**Why the example is Russian.** The operator's complaint began with Russian artifacts, and the
invariant is that register is independent of language. An English-only example would suggest the
rules are an English style guide.
