# TASK 099 — Register scanner: close the REG-2…REG-13 selftest-honesty batch

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 099 |
| Slug | register-selftest-honesty-and-detector-coverage |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Operator request 2026-08-04: close `REG-*` |
| Depends on | TASK 096, TASK 097 |
| Closes | REG-2, REG-3, REG-4, REG-5, REG-6, REG-7, REG-8, REG-9, REG-10, REG-11, REG-12, REG-13 |
| Archive name | `task-099-register-selftest-honesty-and-detector-coverage.md` |

<!-- contract:problem -->

## 1. Problem

`artifact-formalizer` ships two CI gates: the acceptance battery (`selftest_scan.py`) and the
detector roster (`scan_register.py --probe`). Twelve filed defects state that both gates measure
themselves against the data under test, so an edit that removes a detector leaves them green.

Four measurements taken against the current tree:

- Deleting one rule-6 entry from `data/register-en.json` leaves the battery at `145/145` and the
  roster at `18/18`. The English metaphor detector loses an entry and nothing reports it.
- Deleting every rule-6 entry of one language makes `--probe` print `17/17 detectors live` and exit
  0. The denominator shrinks with the numerator.
- Dropping the `probes` example for a rule-3 pattern and then replacing that pattern with
  `\bZZZNEVER\b` loads clean, prints `18/18 detectors live`, exits 0, and keeps the battery at
  `145/145`, while `The installer shall abort because the target exists.` reports zero findings.
  `.agent/skills/artifact-formalizer/references/measurement-baseline.md:236-240@8b51620` records this defect as closed by TASK 097.
- Removing a test function from the tuple at `.agent/skills/artifact-formalizer/scripts/selftest_scan.py:1148@8b51620` prints a self-consistent
  `N/N passed` and exits 0.

Two documentation defects are already live rather than latent. Commit `5c9da31` raised the battery
from 128 cases to 145 and updated `System/Docs/SKILLS.md`, leaving `.agent/skills/artifact-formalizer/SKILL.md:114@8b51620`,
`.agent/skills/artifact-formalizer/SKILL.md:213@8b51620` and `.agent/skills/artifact-formalizer/references/measurement-baseline.md:155@8b51620` asserting 128. `SKILL.md` states the licensed
statement forms as `thirteen` in one place and `nine` in another against 14 rows shipped.

Two normative documents state that `✓` and `✗` are excluded from rule 5 without qualification.
`.agent/skills/artifact-formalizer/scripts/scan_register.py:865@8b51620` exempts them only inside a table cell. A census over 631 tracked documents
found 704 out-of-table status glyphs, of which 0 rank a finding.

**Why.** The exemption the documents promise costs no true positive, and the narrowing comment's
own premises fail against the corpus it cites.

Two detectors named in `references/authoring-contract.md` as canonical failing surfaces ship in
Russian and not in English: the T2 surface `a test goes red` and the T1 surface `the main risk`.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Closes |
| :--- | :--- | :--- | :--- |
| R1 | The detector roster is a literal, and a vanished detector class reports DEAD | Y | REG-4 |
| R2 | Every rule-3 pattern declares an example, enforced at load | Y | REG-3 |
| R3 | The battery pins the shipped vocabulary sizes rather than deriving them | Y | REG-2 |
| R4 | `dequote`, the SENT_SPLIT lookbehinds and the threshold invariants each carry a pin | Y | REG-5, REG-6, REG-7 |
| R5 | The battery asserts its own case count and the count `SKILL.md` states | Y | REG-8 |
| R6 | `✓` and `✗` are exempt from rule 5 wherever they appear | Y | REG-10 |
| R7 | A rule-5 finding on a status glyph gives guidance that applies to a status glyph | Y | REG-10 |
| R8 | English ships the two detectors the authoring contract names and Russian already has | Y | REG-11, REG-12 |
| R9 | `references/measurement-baseline.md` §4 records negative parallelism as the data shows it | Y | REG-9 |
| R10 | `SKILL.md` states no cardinal for a set the contract declares open | Y | REG-13 |
| R11 | Each fix carries a case that fails when the fix is reverted | Y | all |

### 2.1 Sub-features

**R1.** `PROBE_ROSTER` and `SHIPPED_LANGS` are module-level literals. A missing detector class
appends a DEAD row instead of emitting none. Strictness applies when no `--rules` argument is
given. A wholly absent shipped language holds the denominator at 18 and reports four DEAD rows.

**Why.** The five structural detectors are built from thresholds and carry no language, so they
probe live with no rule file present. Marking them DEAD would state something false.

**R2.** `_validate_reasoning` rejects a pattern that declares no example. The reasoning probe row
reports DEAD when no pattern was exercised. `TC-097-15` is re-pinned to the new contract.

**R3.** `SHIPPED_ENTRIES` holds the per-language per-rule counts. `SHIPPED_PROBES` holds the roster
size. `TC-PROBE-02` compares against the literal, not against the loaded data.

**R4.** A table inside a `> [!IMPORTANT]` callout reports `cell_width`. Each of `i.e.`, `vs.` and
`см.` carries a fixture. Each of the two uncovered `check_thresholds` branches carries a rejection
case keyed on a fragment unique to that branch.

**R5.** `EXPECTED_CASES` is the number the battery prints. One case asserts the battery ran that
many. One case asserts `SKILL.md` states the same number. Two past-state narratives carry a
revision identifier.

**R6.** `TICK_GLYPHS` is exempt in every position. `STATUS_GLYPHS` stays exempt inside a table
cell. `☐` joins `STATUS_GLYPHS`.

**R7.** A finding on a `STATUS_GLYPHS` member names the status words. A finding on any other
pictograph keeps the severity wording.

**R8.** `register-en.json` gains one rule-4 entry for the red/green verb forms and one rule-2 entry
for the ranking family. Each carries a false-positive control case.

**R9.** Row 65 reads `not adopted` with its measured figure. The `_dedupe_spans` docstring stops
citing an example the shipped data cannot produce. `SKILL.md` §6 item 4 restates its count.

**R10.** The `SKILL.md` §2 bullet and its §9 Quick Reference row name the licensed forms without a
cardinal. `System/Docs/SKILLS.md` does the same.

**R11.** Each requirement names the mutation that turns its case red. Every mutation is executed
and recorded before the ledger is flipped.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — a maintainer deletes one lexicon entry.**

1. An entry is removed from `data/register-en.json`.
2. The battery compares the loaded counts against `SHIPPED_ENTRIES`.
3. `TC-SHIP-07 en` fails and names both counts.
4. The CI step exits 1.

**UC-2 — a maintainer deletes a whole detector class.**

1. Every rule-6 entry of one language is removed, and the emptied category is removed with them.
2. `--probe` finds no `metaphor` row for that language and appends a DEAD row.
3. The run prints `17/18 detectors live` and exits 2.
4. Both register CI steps fail: the probe step and the advisory sweep.

*Alternative 1a.* The emptied category is left in place. The schema reports `entries must be a
non-empty list` and the run exits 2 before any roster is printed.

**UC-3 — a maintainer edits a rule-3 pattern without its example.**

1. The `probes` entry for a pattern is dropped.
2. `_validate_reasoning` reports that the pattern declares no example.
3. The scanner exits 2 before any document is read.
4. No run reports the vocabulary as live.

**UC-4 — an author writes a status tick in a numbered list.**

1. A document contains `docs/TASK.md gone ✓` outside a table.
2. Rule 5 treats `✓` as exempt in every position.
3. The scan reports no `emoji_severity` finding for it.
4. `SKILL.md` §5 and `measurement-baseline.md` §6 state that behaviour.

**UC-5 — an author writes a checkmark that carries no severity.**

1. A document contains `- ✅ Criterion 1` outside a table.
2. Rule 5 reports it, because no document exempts `✅` outside a table cell.
3. The guidance names the status words rather than `SEV-2`.
4. The author replaces the glyph with a word or deletes it.

**UC-6 — an author writes a personified test in English.**

1. A specification contains `The gate goes red when the fixture passes`.
2. The English rule-4 vocabulary reports two `maxim` findings.
3. The Russian equivalent reports the same two findings.
4. `Red-Green-Refactor`, `the red phase` and `a green run` report nothing.

**UC-7 — someone adds a case to the battery.**

1. A `check(...)` call is added.
2. `TC-META-01` observes a count above `EXPECTED_CASES` and fails.
3. The author raises `EXPECTED_CASES` and re-runs.
4. The case asserting `SKILL.md`'s count fails until `SKILL.md` is corrected.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion | Verification |
| :--- | :--- | :--- |
| A1 | `--probe` on the shipped data prints `18/18 detectors live` and exits 0 | `scan_register.py --probe` |
| A2 | Deleting every rule-6 entry of one language, and its emptied category, exits 2 at `17/18` with a DEAD `metaphor` row | mutation, recorded |
| A3 | Deleting `data/register-ru.json` exits 2 at `14/18` with four DEAD rows | mutation, recorded |
| A4 | Dropping one `probes` example exits 2 at load | mutation, recorded |
| A5 | The TASK 097 D3 two-step exits 2 at load | mutation, recorded |
| A6 | Deleting one lexicon entry makes `TC-SHIP-07` fail | mutation, recorded |
| A7 | Neutering `dequote` makes `TC-ADV-15a` fail and nothing else | mutation, recorded |
| A8 | Dropping each of the three lookbehinds makes exactly one `TC-PREC-06x` fail | mutation, recorded |
| A9 | Deleting each uncovered `check_thresholds` branch makes exactly one `TC-SCHEMA` case fail | mutation, recorded |
| A10 | Dropping a test function from the tuple makes `TC-META-01` fail | mutation, recorded |
| A11 | `.agent/skills/skill-archive-task/SKILL.md` reports zero `emoji_severity` findings | `scan_register.py` on that file |
| A12 | `System/Docs/ORCHESTRATOR.md` reports zero `emoji_severity` findings for `☐` | `scan_register.py` on that file |
| A13 | A `✅` in prose is still reported, with status-word guidance | `TC-ADV-13` plus a guidance case |
| A14 | `The gate goes red when the fixture passes, and turns green again after the revert.` reports 2 `maxim` findings | battery case |
| A15 | `The main risk is a proof that proves the wrong property.` reports 1 `marker` finding | battery case |
| A16 | `Phase 1 leaves the red phase and a green run behind, per Red-Green-Refactor.` reports 0 `maxim` findings | battery case |
| A17 | The battery prints `EXPECTED_CASES` and exits 0 | `selftest_scan.py` |
| A18 | `SKILL.md` states one case count and the battery asserts it | battery case |
| A19 | No live document states a case count other than the asserted one | `grep -rn "cases" SKILL.md System/Docs/SKILLS.md` |
| A20 | `SKILL.md` states no cardinal adjacent to `licensed` | `grep -n "licensed" SKILL.md` |
| A21 | `measurement-baseline.md` §4 row 65 reads `not adopted` with figure 0 | battery case `TC-SHIP-10` |
| A24 | Deleting one rule-3 pattern of either language fails a case | mutation, both languages |
| A25 | Narrowing either new English pattern fails a case naming the lost surface | mutation |
| A26 | Restoring a cardinal adjacent to `licensed` fails a case, in either wrapping | mutation |
| A27 | A count restated in `measurement-baseline.md` fails a case, unless it names a revision | mutation, both directions |
| A28 | Reverting §4 row 65 to `adopted` fails a case | mutation |
| A22 | All six `framework-gates.yml` jobs pass locally, and `reference-integrity` reports no more errors than it did at `8b51620` | each job's commands run locally |
| A23 | Twelve issue files and twelve index lines flip in lockstep | `grep -c "REG" docs/KNOWN_ISSUES.md` |

<!-- contract:open-questions -->

## 5. Open Questions

**OQ-1 — the two English entries add 26 `warn` findings to existing `docs/` artifacts.**
Blocks: nothing. Owner: operator. Measured over the 295 tracked documents under `docs/`: 21 from
the rule-4 entry and 5 from the rule-2 entry, against a corpus total of 2,139. The advisory CI
sweep exits 0 on any number of findings, so no gate changes colour. Five of the 26 fall inside this
task's scope, and four of those are this document and `docs/PLAN.md` naming their own mutation
cases. The findings are recorded rather than fixed.

**OQ-2 — adversarial verification found five silent-failure routes this task does not close.**
Blocks: nothing. Owner: operator. Each removes real detection while both gates exit 0, and none is
the symptom any `REG-2`…`REG-13` record states, so closing them here would widen the task past what
the records describe. They are filed as `REG-14`…`REG-18` with their reproductions.

<!-- contract:decisions -->

## 6. Decisions

**D1, 2026-08-04, orchestrator: REG-9 corrects the record rather than shipping a rule.**
Rejected: ship a Russian negative-parallelism entry. Measured at 0 hits over the ~12,200-line
corpus the baseline cites, and 1 hit over this repository, inside `Backlog/archive/`.

**Why.** Maintenance rule §6 item 4 admits a rule only on a supporting measurement. Row `:66` of §4
records a zero-baseline candidate as `not adopted`.

**D2, 2026-08-04, orchestrator: rule 5 exempts `✓`/`✗` everywhere and keeps `✅`/`❌` in-table-only.**
Rejected: exempt every status glyph everywhere — erases 704 of 1050 rule-5 findings and turns
`TC-ADV-13` red. Rejected: change only the documents — leaves the guidance instructing an author to
replace `docs/TASK.md gone ✓` with `SEV-2`. Measured: 0 of 704 out-of-table status glyphs rank a
finding; exempting `✓`/`✗` changes no battery case.

**D3, 2026-08-04, orchestrator: `☐` joins `STATUS_GLYPHS`.**
Rejected: leave it — `☑` and `☒` are already members, and `☐` produces 6 in-table findings at
`System/Docs/ORCHESTRATOR.md:271-276`. `✔` stays out: `TC-ADV-10` requires it to fire.

**D4, 2026-08-04, orchestrator: REG-13 removes the cardinal rather than correcting it to 14.**
Rejected: write `fourteen` — `authoring-contract.md:107` declares the list open, eight other
surfaces already name the forms without a cardinal, and `docs/ARCHITECTURE.md:307` states that a
restated rule is a place for it to drift.

**D5, 2026-08-04, orchestrator: REG-8 keeps one asserted count.**
Rejected: correct all three sites to 145 — that reproduces the defect three times.

**Why.** `skill-creator` §7 requires a count under Validation Evidence, so `SKILL.md` §8 keeps one
and a battery case asserts it. §3 and `measurement-baseline.md` §9 drop the numeral.

**D6, 2026-08-04, orchestrator: roster strictness keys on `not args.rules`.**
Rejected: apply it unconditionally — measured at 36 of 145 battery cases failing, because
`GOOD_RULES` and `entry_rules()` build partial single-language rule files by design.

**D7, 2026-08-04, orchestrator: a declared example becomes mandatory for a rule-3 pattern.**
Rejected: keep it optional and report `unprobed` — the `unprobed` state is the path that re-opens
TASK 097 D3 while every gate stays green. A rule file written before `probes` existed no longer
loads; `TC-097-15` is re-pinned to state that.

**D8, 2026-08-04, orchestrator: the English rule-4 pattern keeps `\s+` between verb and colour.**
Rejected: `[ \t]` — masking preserves length, so a code span between the two words becomes blanks.
Measured over `docs/`: 6 of the 21 rule-4 matches arrive that way, and each is a true positive.

**D10, 2026-08-04, orchestrator: the shipped vocabulary pin covers rule 3, and each named surface
carries its own case.**
Rejected: pin rules 2, 4 and 6 only — adversarial verification deleted 21 of the 24 shipped rule-3
patterns one at a time with both gates at exit 0 and a real finding lost each time. Rejected: pin
entry counts alone — an entry replaced in place keeps the count and removes detection.

**D11, 2026-08-04, orchestrator: the two ambiguous references inside the TASK 098 archive are
corrected, against §7.**
Rejected: leave them — this task moved that file into `docs/tasks/`, and the `reference-integrity`
job reports both as `AMBIGUOUS`. The edit resolves a citation and changes no claim the record makes.

**D9, 2026-08-04, orchestrator: the English rule-2 ranking entry lists only measured members.**
Rejected: the full adjective and noun families — `chief`, `principal`, `foremost`, `difficulty`,
`concern`, `issue`, `point` and `takeaway` scored zero over 977,960 masked lines, and `SKILL.md`
§6 item 4 admits a member on a measurement.

<!-- contract:out-of-scope -->

## 7. Out of scope

In scope: `.agent/skills/artifact-formalizer/` and the two `System/Docs/` sentences that restate its
counts.

Out of scope: the `WIR-*` batch, `AT-*`, `HK-*`, `WR-*` and `FW-1` (carried by their own tasks);
the 671 `✅`/`❌` findings rule 5's second clause defends
(`references/formalization-guide.md:19-21`); `CHANGELOG.md`, `docs/tasks/`, `docs/plans/`,
`docs/reviews/` and `docs/issues/` bodies (release notes and archived artifacts).
