# PLAN 102 — artifact-formalizer: the glyph citation convention, and a maintenance rule for narrowing

**TASK:** [docs/TASK.md](TASK.md) · **Covers:** R1–R7 · **Acceptance:** A1–A8

## Sequencing rule

Four clusters in order. Cluster A adds the battery case first and leaves the battery failing, since
`EXPECTED_CASES` is pinned against the printed total. Cluster B moves the pinned total and the three
documents that state it. Cluster C writes the contract text and the maintenance rule. Cluster D
closes both work-items and runs every gate.

| Order | Cluster | Files | Covers |
| :--- | :--- | :--- | :--- |
| A | Battery case | `scripts/selftest_scan.py` | R5 |
| B | Pinned total | `scripts/selftest_scan.py`, `SKILL.md`, `System/Docs/SKILLS.md` | R6 |
| C | Contract and maintenance rule | `references/authoring-contract.md`, `SKILL.md`, `references/measurement-baseline.md` | R1, R2, R3, R4 |
| D | No retroactive edit, ledgers, and the gates | ledgers | R7, A1–A8 |

**Backup.** Before Cluster A: `mkdir -p .agent/archive`, then copy every file the clusters edit to
`.agent/archive/<name>.bak`. No bootstrap file changes in this task, so `CLAUDE.md`, `AGENTS.md` and
`GEMINI.md` are copied for the workflow's fallback step and are expected to stay identical.

**Rollback.** Every edit is to a tracked file, and no cluster creates, moves or deletes one.
Reverting is `git checkout --` on all **eight** edited paths — the five under
`.agent/skills/artifact-formalizer/`, `System/Docs/SKILLS.md`, and the three ledger files Cluster D
touches (`docs/BACKLOG.md`, `docs/backlog/wi-14-*.md`, `docs/backlog/wi-15-*.md`). Reverting the
first five alone leaves both records at `status: done` with their index lines under `## Closed`,
which is the record-vs-index breakage `known-issues-format` Shared Mechanics item 3 forbids. The
three ledger files have no `.agent/archive/` backup, so `git checkout --` is their only path back.

## Cluster A — the battery case (R5)

- [x] A1. Add `TC-FP-05` to `t_false_positives()` in `scripts/selftest_scan.py`, directly after
      `TC-FP-02`. Fixture: prose citing a severity glyph inside a code span, written as an escape so
      the glyph cannot become a look-alike character. Assertion: exit 0 and no `emoji_severity`
      finding.
- [x] A2. Add the control that separates masking from suppression: the same glyph outside a code
      span in the same case is still reported. Reuse the existing `TC-ADV-13` shape rather than
      duplicating it — assert on one document holding both positions.
- [x] A3. Run `python3 scripts/selftest_scan.py`. Expected: `TC-META-01` fails, because the printed
      total is 192 against `EXPECTED_CASES = 191`.

**Why the case is a false-positive control and not a detector case.** The claim is that the scanner
reports nothing here. `t_false_positives` is the group holding that claim for markers.

## Cluster B — the pinned total (R6)

- [x] B1. Set `EXPECTED_CASES = 192` in `scripts/selftest_scan.py`.
- [x] B2. Update `SKILL.md` §8: `191 cases` becomes `192 cases`.
- [x] B3. Update `System/Docs/SKILLS.md` lines 89 and 92: `191-case` becomes `192-case`. Line 92
      carries the `evals/` exemption of `TC-SHIP-08`, so its numeral is corrected for truth rather
      than for the gate.
- [x] B4. Run `python3 scripts/selftest_scan.py`. Expected: 192 of 192, exit 0.

## Cluster C — the contract and the maintenance rule (R1–R4)

- [x] C1. `references/authoring-contract.md`, "Why code spans": extend the convention sentence to
      name a glyph beside a marker.
- [x] C2. Same paragraph: state the class the convention does not reach — a record body under
      `known-issues-format` §8 is preserved byte-for-byte, so it cannot adopt the convention after
      filing.
- [x] C3. `SKILL.md` §6: add rule 5. It states three items a narrowing produces before it ships.
      - the removed population, measured over the declared scope, scope and commit named
      - the battery result after the change
      - one occurrence the narrowed rule still reports
- [x] C4. `references/measurement-baseline.md` §6: record the rejected widening. Surfaces:
      `` `✅` ``, `` `❌` ``, `` `☑` ``, `` `☒` ``. Decision: `task-099` D2. Verification: WI-13 §7.2
      — 584 findings erased, battery `188/191`.
- [x] C5. Run `scan_register.py` over `SKILL.md` and `references/*.md`. Expected: 0 `warn`, exit 0.

**Why C4 sits in §6 and not only in the dropped work-item.** WI-13 §7.2 records the re-proposal
citing §6 as support for the option §6's own decision had rejected.

## Cluster D — the convention applied, and the gates (R7, A1–A8)

- [x] D1. ~~Wrap the three glyphs in `docs/tasks/task-065-reviewers-hardening.md:29`.~~ **Reverted.**
      `docs/ARCHITECTURE.md:273` states archived artifacts are immutable by doctrine, and
      `docs/backlog/wi-13-narrow-rule-5-clause-2-to-the-vocabulary-slot.md:294` quotes the pre-edit bytes of that line. TASK 102 D2 records both.
- [x] D2. Re-measure `emoji_severity` over the declared scope. Expected: 307, unchanged — the
      convention reaches no already-filed document.
- [x] D3. Close WI-14 and WI-15 in `docs/backlog/` and in `docs/BACKLOG.md`: `status: done`,
      `resolved_at`, `resolved_by: TASK 102`, a resolution blockquote, and the index line moved to
      `## Closed`. WI-14's blockquote states the measured outcome D5 requires.
- [x] D4. Run every acceptance gate A1–A8 and record the figures.

**Why no already-filed document is edited.** TASK 102 D1 and D2 state the two reasons. A record
body is evidence, and an archived artifact is immutable by doctrine.
