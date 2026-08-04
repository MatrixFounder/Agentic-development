# TASK 100 — Register scanner: close the REG-14…REG-18 mutation-survivor batch

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 100 |
| Slug | register-mutation-survivors-surface-and-threshold-pins |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Operator request 2026-08-04: close the remaining `REG-*` |
| Depends on | TASK 096, TASK 097, TASK 099 |
| Closes | REG-14, REG-15, REG-16, REG-17, REG-18 |
| Archive name | `task-100-register-mutation-survivors-surface-and-threshold-pins.md` |

<!-- contract:problem -->

## 1. Problem

`artifact-formalizer` ships two CI gates: the acceptance battery (`selftest_scan.py`) and the
detector roster (`scan_register.py --probe`). TASK 099 pinned what each gate *counts*. Five filed
defects state that a count is not an identity: an edit that keeps the count and removes detection
leaves both gates at exit 0.

Six mutations, each applied to a throwaway copy of the skill and measured over the 636 tracked
`.md` files present on disk. The unmutated copy reports 4,835 findings, `174/174 passed` exit 0,
and `18/18 detectors live` exit 0.

| Record | Mutation | Battery | Roster | Detection lost |
| :--- | :--- | :--- | :--- | :--- |
| REG-14 | rule-3 `\bfor the reason that\b` replaced, its example moved with it | 174/174 exit 0 | 18/18 exit 0 | the named sentence, 1 → 0 |
| REG-14 | rule-2 `robust` pattern replaced, its probe moved with it | 174/174 exit 0 | 18/18 exit 0 | `marker` 447 → 406 |
| REG-15 | `cell_max_chars` 120 → 150 in both rule files | 174/174 exit 0 | 18/18 exit 0 | `cell_width` 811 → 613 |
| REG-16 | `flags` dropped from the 35 entries no case names | 174/174 exit 0 | 18/18 exit 0 | `marker` 447 → 432 |
| REG-17 | `[-*+]\s` added to the `SKIP_LINE` alternation | 174/174 exit 0 | 18/18 exit 0 | 4,835 → 4,354 |
| REG-18 | `TICK_GLYPHS` widened to ten glyphs | 174/174 exit 0 | 18/18 exit 0 | `emoji_severity` 1,012 → 779 |

The REG-14 rule-3 mutation costs no corpus finding, because `for the reason that` has no corpus
occurrence. `The installer shall abort for the reason that the target exists.` reports
`[('reasoning', 'shall … for the reason that')]` before it and `[]` after.

The REG-17 loss splits as `sentence_length` 826 → 546, `sentence_near_limit` 712 → 517 and
`reasoning` 22 → 16.

**Why the gates miss all six.** Each gate compares the data under test against itself. `SHIPPED_ENTRIES`
and `SHIPPED_REASONING` count entries. `verify_detectors` runs each entry against the entry's own
declared `probe`. `_structural_probes` builds each fixture from the active threshold. A mutation
that moves both sides of one of those comparisons is invisible to it.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Closes |
| :--- | :--- | :--- | :--- |
| R1 | The battery pins which patterns ship, not how many | Y | REG-14 |
| R2 | The battery pins every threshold the scanner applies | Y | REG-15 |
| R3 | The pinned surface carries each entry's flags, and the roster verifies they are applied | Y | REG-16 |
| R4 | The structural fixtures exercise every line form `LIST_MARK` accepts | Y | REG-17 |
| R5 | The battery pins the membership of both rule-5 glyph sets | Y | REG-18 |
| R6 | Each fix carries a case that fails when the fix is reverted | Y | all |

### 2.1 Sub-features

**R1.** `SHIPPED_SURFACES` holds the pattern strings of rules 2, 4 and 6 and of the rule-3 modal
and causal vocabularies, per language. A case reports the symmetric difference between the pinned
set and the loaded set. A further case asserts that `SHIPPED_SURFACES` and the TASK 099 count pins
state the same sizes.

**Why the pattern and not the marker.** The pattern is what matches a document. A marker is the
label a finding prints. REG-14's reproduction keeps the marker and replaces the pattern.

**R2.** `SHIPPED_THRESHOLDS` holds the four keys each rule file declares. `SHIPPED_DEFAULTS` holds
the six keys of the scanner's `DEFAULTS`, which supply `sentence_pressure_band` and
`cell_prose_chars`. The battery imports `scan_register` to read the second.

**Why the whole set.** REG-15 names `cell_max_chars`. The same comparison covers the other five
keys, and `TC-SHIP-02` pinned one of them.

**R3.** `SHIPPED_SURFACES` holds `(pattern, flags)` per entry, so a removed `flags` key fails R1's
case. `verify_detectors` additionally runs every entry that declares `i` against a case-flipped copy
of its own probe, and lists an entry that stops matching as case-blind. `load_rules` carries `flags`
into the loaded entry, which it did not before.

**Why both.** The two close different mutations. A `flags` key removed from the data moves the
roster's own input, so no roster check can see it; the pin is a value declared outside the data. A
flag declared and not applied leaves the data intact, so the pin cannot see it. Measured: the scan
compiles its regex at a different site from the validator's own compile, and losing the flag at the
scan site alone left 15 entries reported through their own probes and 63 unreported. With the
case-flip check all six lexical rows report DEAD and name every entry.

**R4.** `_structural_probes` returns one or more line forms per kind. `sentence_length` and
`sentence_near_limit` carry a bare line, a `- ` list item and a `1. ` ordered item. The reasoning
row exercises each pattern in all three. The roster stays at nine rows per shipped language.

**Why three.** `LIST_MARK` accepts both list forms, and the corpus holds 12,415 bullet lines and
3,336 ordered-list lines against 34,852 other non-blank lines. With the bullet form alone, widening
`SKIP_LINE` with `\d+\.\s` instead cost 63 findings at `18/18 detectors live` exit 0.

**Why not a row per form.** The roster size is 18. `SKILL.md`, `System/Docs/SKILLS.md` and
acceptance criterion A1 of TASK 099 state that number.

**R5.** `TICK_GLYPHS` and `STATUS_GLYPHS` are compared against literals in the battery, read from
the imported module. A case reports the symmetric difference.

**R6.** Each requirement names the mutation that turns its case red. Every mutation is executed and
recorded before the ledger is flipped.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — a maintainer replaces a lexicon pattern in place.**

1. An entry keeps its `marker` and receives a new `pattern` and `probe`.
2. The battery compares the loaded pattern set against `SHIPPED_SURFACES`.
3. The case fails and names the pattern added and the pattern removed.
4. The CI step exits 1.

**UC-2 — a maintainer raises a threshold.**

1. `cell_max_chars` is set to 150 in both rule files.
2. The battery compares the loaded thresholds against `SHIPPED_THRESHOLDS`.
3. The case fails and prints both dicts.
4. The CI step exits 1.

**UC-3 — a maintainer removes a case flag.**

1. `"flags": "i"` is removed from an entry whose own probe still matches without it.
2. The roster runs that entry against a case-flipped copy of its probe and finds no match.
3. The `marker` row for that language reports the entry as case-blind and prints DEAD.
4. The run exits 2, and both register CI steps fail.

**UC-4 — a maintainer widens the line filter.**

1. `SKIP_LINE` gains an alternative that matches a bullet marker or an ordered marker.
2. The `sentence_length` and `sentence_near_limit` fixtures fire on the bare line and not on the
   matching list form.
3. Both rows print DEAD naming the form, and the reasoning row prints DEAD with them.
4. The run exits 2.

**UC-5 — a maintainer moves a glyph into the exempt set.**

1. `⚠` is added to `TICK_GLYPHS`.
2. The battery compares the imported set against its literal.
3. The case fails and names `⚠`.
4. The CI step exits 1.

**UC-6 — a maintainer adds a lexicon entry on a measurement.**

1. An entry is added under the `SKILL.md` §6 maintenance rule.
2. The count pin and the surface pin both fail.
3. The author adds the pattern to `SHIPPED_SURFACES` and raises the count in `SHIPPED_ENTRIES`.
4. `TC-100-03` fails until the two pins state the same size.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion | Verification |
| :--- | :--- | :--- |
| A1 | `--probe` on the shipped data prints `18/18 detectors live` and exits 0 | `scan_register.py --probe` |
| A2 | The battery prints `EXPECTED_CASES` and exits 0 | `selftest_scan.py` |
| A3 | Replacing a rule-2 pattern in place fails a case naming both patterns | mutation, recorded |
| A4 | Replacing a rule-3 pattern in place fails a case naming both patterns | mutation, recorded |
| A5 | Raising `cell_max_chars` to 150 fails a case | mutation, recorded |
| A6 | Changing any key of `DEFAULTS` fails a case | mutation, recorded |
| A7 | Dropping `flags` from an entry no case names fails a case naming that entry | mutation, recorded |
| A7a | Losing the flag at the scan-side compile exits 2 with all six lexical rows DEAD | mutation, recorded |
| A8 | Adding `[-*+]\s` to `SKIP_LINE` exits 2 with DEAD `sentence_length`, `sentence_near_limit` and `reasoning` rows | mutation, recorded |
| A8a | Adding `\d+\.\s` to `SKIP_LINE` exits 2 with the same three rows DEAD | mutation, recorded |
| A8b | A lexicon entry duplicated in place fails a case | mutation, recorded |
| A9 | Adding a glyph to `TICK_GLYPHS` fails a case naming that glyph | mutation, recorded |
| A10 | Adding a glyph to `STATUS_GLYPHS` fails a case naming that glyph | mutation, recorded |
| A11 | Raising `SHIPPED_ENTRIES` without adding the pattern to `SHIPPED_SURFACES` fails a case | mutation, recorded |
| A12 | The two scanners report the same findings over one corpus | both scanners over the 638 `.md` files of `23827c1` |
| A13 | `SKILL.md` and `System/Docs/SKILLS.md` state the new case count | `TC-SHIP-08` |
| A14 | All six `framework-gates.yml` jobs pass locally | each job's commands run locally |
| A15 | Five issue files and five index lines flip in lockstep | `grep -c "REG-1[4-8]" docs/KNOWN_ISSUES.md` |

<!-- contract:open-questions -->

## 5. Open Questions

**OQ-1 — the surface pin duplicates the pattern text held in `data/register-*.json`.**
Blocks: nothing. Owner: operator. Adding an entry then requires two edits: the data file and the
pin. That cost is the mechanism — a pin an edit does not touch is the defect REG-14 records.
`TC-100-03` reports the two pins disagreeing, so a partial edit exits 1.

<!-- contract:decisions -->

## 6. Decisions

**D1, 2026-08-04, orchestrator: the surface pin holds pattern strings rather than a digest.**
Rejected: a SHA-256 over the canonicalised entries. A digest states that something changed and
cannot name it, so the maintainer re-pins by copying the printed value, which accepts the mutation
under review.

**D2, 2026-08-04, orchestrator: REG-16 is closed by the surface pin, and the roster check covers the
sibling code defect.** Rejected: close it in the roster alone. Measured: a roster check keyed on the
declared flag is switched off by the edit that removes the flag, so the reproduction stayed at
`174/174` and `18/18`, both exit 0. Rejected: pin the number of entries declaring `i`. A count
states that some flag moved and does not name the entry that stopped detecting.

**D3, 2026-08-04, orchestrator: REG-17 adds line forms to the existing rows, not new rows.**
Rejected: one row per line form. The roster size is stated in `SKILL.md` §5, in
`System/Docs/SKILLS.md` and in TASK 099 acceptance criterion A1, and TASK 099 `TC-099-02` and
`TC-099-03` assert `17/18` and `14/18` against it.

**D6, 2026-08-04, orchestrator: adversarial verification widened two fixes within their records.**
Two mutations survived the first implementation and are closed here. A `SKIP_LINE` widened with
`\d+\.\s` cost 63 findings at exit 0, so the ordered-list form joined `LINE_FORMS`. A lexicon entry
duplicated in place kept `TC-100-01` green, because two identical surfaces collapse into one set
member, so the case asserts distinctness alongside the comparison.

**Why inside the records.** Each is the symptom its record states — a detector removed with both
gates at exit 0 — rather than a new class, so closing them here does not widen the batch.

**D4, 2026-08-04, orchestrator: the glyph pin imports `scan_register` rather than reading its
source text.** Rejected: a regex over the source. ARC-9 records a case that asserted a schema
literal against a test literal without inspecting the code it named. A source regex pins the
spelling of an assignment, not the value the scanner uses.

**D5, 2026-08-04, orchestrator: the case-flip probe applies only to entries declaring `i`.**
Rejected: flip every probe. `head / tail (of a call)` declares no flag deliberately: with `i` it
matched the git ref `HEAD` on every anchor line of the corpus. A flipped probe would report that
entry dead for conforming to its own note.

<!-- contract:out-of-scope -->

## 7. Out of scope

In scope: `.agent/skills/artifact-formalizer/scripts/` and the two `System/Docs/` and `SKILL.md`
sentences that state the battery's case count.

Out of scope: the `WIR-*` batch, `AT-*`, `HK-*`, `WR-*` and `FW-1`, each carried by its own task.
Out of scope: the lexicon content of `data/register-*.json`, which this task pins and does not
extend. Out of scope: `CHANGELOG.md`, `docs/tasks/`, `docs/plans/`, `docs/reviews/` and
`docs/issues/` bodies.
