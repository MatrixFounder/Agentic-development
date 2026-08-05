---
id: WI-14
type: work-item
status: done
opened_at: 2026-08-05
slug: wi-14-glyph-citation-convention-in-authoring-contract
effort: S
value: 'removes 26 of 307 in-scope rule-5 findings with no code change; the convention already exists for markers'
source: 'WI-13 P4, carried out of that record when it was dropped'
provenance: human
component: artifact-formalizer
resolved_at: 2026-08-05
resolved_by: TASK 102
---

# WI-14 — state the glyph citation convention in `authoring-contract.md`

> **Done 2026-08-05 (TASK 102), with §3 step 2 dropped and the reason recorded.**
> `authoring-contract.md` now names a glyph beside the marker it already named, and states the
> classes the convention does not reach. `TC-FP-05` pins both positions in one fixture: the cited
> glyph silent, the used glyph still a `warn`.
>
> **Step 2 reached none of the four documents.** `wir-11`, `wir-2` and `wir-4` are
> `provenance: machine` records, and `known-issues-format` §8 preserves a record body byte-for-byte
> because that property is what makes it evidence. `task-065` is an archived artifact, and
> `docs/ARCHITECTURE.md:273` states those are immutable by doctrine. Its three glyphs **were**
> wrapped in a first draft; an adversarial review found that the edit also falsified the quotation
> of that line in [WI-13](wi-13-narrow-rule-5-clause-2-to-the-vocabulary-slot.md) §8, and it was
> reverted.
>
> **Measured, declared scope, 211 documents:** `emoji_severity` stays at 307. The `value` line above
> claims this removes 26 findings, and is superseded: the count removed is **0**. The convention is
> an authoring rule, and it binds documents written from here on. The 26 residual findings stay
> reported, with the contract stating why — no exemption was added to rule 5.

Carried out of [WI-13](wi-13-narrow-rule-5-clause-2-to-the-vocabulary-slot.md) §4 (P4), the one
proposal there that no review finding contradicted. WI-13 was dropped on its §8 re-measurement;
this part does not depend on the narrowing that record proposed.

## 1. The gap

`authoring-contract.md` states the code-span convention for citing a **marker**, under "Why code
spans". It does not state it for citing a **glyph**. A record that reports glyph severities
therefore fires rule 5 on the glyphs it quotes.

## 2. Measured

WI-13 §8, at `b11b709`, over the declared scope: 26 of 307 `emoji_severity` findings are a
severity-coloured glyph quoted inside a record about glyph severity. They sit in `wir-11` (12),
`wir-2` (10), `task-065` (3) and `wir-4` (1).

`mask()` already blanks code spans. Every one of the 26 disappears when the citing document wraps
the glyph, with no rule change and no scanner change.

## 3. The change

1. Extend the "Why code spans" paragraph in `authoring-contract.md` to name glyphs beside markers.
2. Wrap the quoted glyphs in the four records above.
3. Add a battery case: a document quoting a glyph in a code span reports no `emoji_severity`.

WI-13 itself applies the convention to its own body already — its §1 note states so.

## 4. Bound

This is a convention for **citing**, not a licence. A glyph outside a code span is still reported,
which is what keeps the rule able to fire.
