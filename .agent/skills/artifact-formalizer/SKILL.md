---
name: artifact-formalizer
description: >-
  Use BEFORE authoring a specification (TASK, ARCHITECTURE, PLAN, task files,
  issue records) to write in specification register, and AFTER to audit one that
  reads as an essay: long sentences, unverifiable evaluative words, maxims,
  personification, coined metaphors, reasoning inside requirements, emoji as
  severity. Authoring contract plus a self-probing scanner; never changes the
  document's language. Triggers: «формализуй задачу», «проверь регистр»,
  "formalize this spec", "reads like an essay", "write the spec".
tier: 2
version: 2.0
---

# Artifact formalizer (specification register)

## Purpose

A reader of an essay-register artifact performs two passes: one to locate the requirement, one to
decide whether a given sentence carried one. This skill removes the second pass. It has two modes.

| Mode | When | Instrument | Owns |
| :--- | :--- | :--- | :--- |
| **A — Authoring** | before and during writing | `references/authoring-contract.md` | the defect is not written |
| **B — Audit** | on an existing document | `scripts/scan_register.py` + a reading pass | what Mode A missed |

Mode A prevents the defect; Mode B measures what Mode A missed.

**Why in that order.** Defective prose measured 5.1% of one corpus's words (731 of 14,288), while
removing it required reading and editing all 14,288. Register also varied by authoring model on the
same repository, so an unwritten standard is not a standard.
[`references/measurement-baseline.md`](references/measurement-baseline.md) §5 carries both figures.

## Scope boundary — what this is NOT

This is not a jargon or terminology tool. Domain terms are precise and stay verbatim:
`singleflight`, `RTM`, `дедлайн`, `throttle`. Translating engineering vocabulary into business
language for customer-facing documents is a different problem with a different audience, and this
skill does not attempt it.

## 1. Red Flags (Anti-Rationalization)

A definition list, not a table: the reality column is prose, and `documentation-standards` §5.1
prescribes converting such a column rather than widening it.

- **"I'll write it, then run the formalizer."** That is the expensive order. §Purpose gives the
  measured cost. Mode A first.
- **"The scan is clean, so the text is clean."** Every zero is reported next to what the detector
  actually saw. Read `DIAGNOSTICS`: a corpus whose longest sentence equals the limit was written
  for the gate.
- **"I'll add a pattern for this new phrasing."** First ask whether a test in the authoring
  contract already forbade it. If it did, the lexicon gains a faster detector and nothing else
  changes. If it did not, **the contract is amended** (§6).
- **"«Шов», «нога», «мост» — это термины проекта."** A term appears in ARCHITECTURE.md, a public
  API, or a cited standard. Run `--terms docs/ARCHITECTURE.md` and let the scanner apply that test.
- **"I formalized the section that was quoted at me."** The pass that produced this skill's own
  worked example did exactly that. It left seventeen occurrences of one metaphor in the same task
  set. Coverage is per section: `--sections`.
- **"The whole document reads badly — I'll rewrite it."** Conforming sentences stay verbatim.
  Over-rewriting introduces errors that were not there.
- **"I'll shorten it by trimming the requirement."** Register changes, substance does not. Numbers,
  identifiers, obligations and scope limits survive verbatim.
- **"This word is fine — I'll widen the threshold."** A failing scan is fixed in the prose.
  Thresholds move only when a measurement moves them.
- **"It flagged a false positive, so the rule is wrong."** The scanner is advisory by design. Judge
  the finding; `info` exists because the author decides.

## 2. Capabilities

- **Authoring contract.** Six tests applied per sentence, and the licensed statement forms.
  The tests are stated as properties rather than as a word list, which is what lets them reach a
  phrasing the lexicon has never seen. That is a design intent, not a guarantee: §6 says what to do
  when a finding escapes all six.
- **Self-probing detectors.** Every run probe-tests each detector against a known positive and
  prints the result beside the findings. A rule whose pattern cannot match its own `probe` string is
  rejected at load time; a dead detector exits `2` instead of reporting a clean document.
- **Measured diagnostics.** A zero is never bare: sentence count, mean, observed maximum against the
  limit, cell counts, active lexicon size. `PRESSED AGAINST THE LIMIT` names a distribution written
  for the gate.
- **The value that invalidates a scan is `letters masked away`.** Read it before the findings.
  Masking blanks fenced blocks, comments, link targets and code spans, so a high share is correct in
  a code-heavy document and suspicious in a prose one. Corpus reference: median 22%, p95 63%. A
  share far above the p95 in a document with **no fenced block** means the scan measured little of
  what it was given. `INPUT DEFECT` lines name what stopped it — an unterminated comment, a backtick
  that never pairs. Both are facts about the document, so they are reported and exit `0`
  (ARCHITECTURE §7.4).
- **All six rules reach a detector**, three of them with declared recall limits (§5).
- **Termhood applied mechanically.** `--terms ARCHITECTURE.md …` downgrades rule-6 findings that
  occur in the declared sources, which is the guide's own test executed rather than remembered.
- **Section worklist.** `--sections` enumerates the document so "the reading pass was done" has a
  denominator.
- **Data-driven markers.** `data/register-ru.json`, `data/register-en.json` (schema
  `register-rules/v1`). Entry = marker + pattern + `guidance` + `probe`, plus optional `flags`,
  `severity`, `rule` and `note`. New language = new data file, zero code.
- **Masking before matching.** Code spans (any backtick run, across line breaks), fenced blocks
  (backtick or tilde, terminated or not), link targets and HTML comments are blanked at preserved
  length. Line numbers survive, and a marker quoted as an example is not reported as one used.
- **Advisory exit codes.** `0` on any number of findings. `2` for a broken instrument: an invalid
  rule file, thresholds that conflict or are inconsistent once merged, unreadable input, or a dead
  detector. `3` for a usage error, so a mistyped flag is not read as a dead detector.

## 3. Execution Mode

Hybrid. Mode A is prompt-driven judgement. Rule-file validation, detector probing and scanning are
deterministic. Judging `info` findings and covering the recall gaps in §5 are yours.

### Script Contract

| Command | Purpose | Exit |
|---|---|---|
| `python3 scripts/scan_register.py FILE… [--rules R.json…] [--terms T.md…] [--lang auto\|<lang>] [--sections] [--json]` | validate → probe → scan | 0 findings / 2 broken instrument / 3 usage |
| `python3 scripts/scan_register.py --probe` | verify every detector against a known positive | 0 all live / 2 any dead |
| `python3 scripts/scan_register.py --list [LANG]` | render the rule set as a table | 0 / 3 unknown language |
| `python3 scripts/selftest_scan.py` | acceptance battery | 0 / 1 |

Finding kinds: `sentence_length`, `sentence_near_limit`, `cell_width`, `cell_sentences`,
`emoji_severity`, `marker`, `reasoning`, `maxim`, `metaphor`.

Every finding names the section it violates. Register findings carry a §5.5 rule number;
`cell_width` and `cell_sentences` carry **§5.1**, which owns cell shape. Reporting them under a
§5.5 rule number claimed an ownership this skill disclaims two paragraphs later.

## 4. Instructions

### Mode A — authoring (default)

**A1.** Read [`references/authoring-contract.md`](references/authoring-contract.md). Identify the
document's language; it is the author's choice and this skill never changes it.

**A2.** For each statement, pick its **licensed form** before writing the sentence. There is no step
at which prose is generated and then repaired.

**A3.** Apply tests T1–T6 as you write. T6's target is the corpus mean of 5.8–15.4 words, not the
35-word failure bound.

**A4.** Hand off to Mode B on what you wrote. Findings there are residue, and §6 says what each one
obliges.

### Mode B — audit

**B1.** `scan_register.py <file> --sections --terms <ARCHITECTURE.md>`. Exit 2 means a broken rule
file or a dead detector — fix that first; findings from a run with a dead detector are not a
measurement.

**B2.** Read `DETECTORS` and `DIAGNOSTICS` before reading the findings. A clean scan whose
diagnostics show `PRESSED AGAINST THE LIMIT`, or a low `prose reaching rule 1` share, is not
evidence of a conforming document.

**B3.** Fix every `warn`; judge each `info`. `ровно`, `именно`, `exactly` are load-bearing when they
name an exact count or location.

**B4.** Walk the `--sections` worklist and read **every** section for the recall gaps in §5 — not
only the sections that already carry findings.

**B5.** Re-scan. Then apply the specification test: could a reader who was not in the discussion
verify each claim from the document alone?

## 5. Detector coverage, and what each detector does not reach

Stated so that a zero is read correctly. Rules 1, 2 and 5 are decided by the scanner. Rules 3, 4
and 6 have detectors with declared recall limits, and the reading pass owns the remainder.

| Rule | Detector | Declared limit |
| :--- | :--- | :--- |
| 1 One claim per sentence | `sentence_length`, `sentence_near_limit` | counts words, never claims |
| 2 No evaluative markers | `marker` | judgement phrased in unlisted words |
| 3 Reasoning separated | `reasoning` | reasoning spread across two sentences |
| 4 A rule stated as a rule | `maxim` | a novel aphorism |
| 5 Severity is a named value | `emoji_severity` | nothing beyond the exemptions below — complete for pictographic glyphs |
| 6 A private metaphor is not a term | `metaphor` + `--terms` | a metaphor coined today |

- **Rule 1** — two claims inside twelve words pass, because the detector counts words.
- **Rule 3** — the detector needs the obligation and the causal connective in **one** sentence.
  Each vocabulary pattern declares its example in `probes`; a rule file holding a pattern that
  declares none does not load.
- **Rule 4** — it recognises named personifications and maxim templates, nothing beyond them.
- **Rule 5** — `✓` and `✗` (U+2713/U+2717) are excluded everywhere; `✅`, `❌`, `☑`, `☒` and `☐` are
  excluded inside a table cell, where §5.1 governs. Outside a cell those five are still reported.
  Rule 5's second clause is why: a glyph carrying no severity at all is diff metadata, and does not
  belong in a specification either
  ([`references/formalization-guide.md`](references/formalization-guide.md) rule 5).
- **Rule 6** — a candidate list plus a string test against the sources given to `--terms`.

`documentation-standards` §5.1 is surfaced by the same scanner (`cell_width`, `cell_sentences`) and
remains owned there.

## 6. Maintenance — how the lexicon stays a backstop instead of a list of yesterday's phrases

A new defective phrase found in the wild is triaged **before** any data file is edited:

1. **Does a test T1–T6 already forbid it?** If yes, the contract held and the author skipped it. Add
   the entry as a faster detector, and nothing else changes.
2. **Does no test reach it?** Then the finding is about the contract. Amend
   `references/authoring-contract.md` first — a test or a licensed form — and add the entry second.
3. **Every entry ships with a `probe`.** Validation rejects a pattern that cannot match its own
   probe, so a rule can never be added dead.
4. **A rule ships only when a measurement supports it.** Four properties expected to show drift did
   not, and six generic AI-writing tells measured at zero;
   [`references/measurement-baseline.md`](references/measurement-baseline.md) records them as
   non-rules so nobody re-proposes them from impression.

## 7. Safety Boundaries

Read-only: the scanner opens files and writes nothing. Rewrites in Mode B change register only, and
never alter numbers, identifiers, obligations, scope limits or the document's language. Ambiguity is
surfaced as an Open Question, not resolved. Reports and never fails a phase.

**Why advisory.** `documentation-standards` §4 records the mechanism it did measure: a gate that fails on
correct documents is how gates get switched off. The second mechanism — an author writing
*to* the bound rather than to the rule — is this skill's own measurement, and
`references/measurement-baseline.md` §8 carries the figures.

The two non-advisory exits are a **dead detector** (`2`) and a **usage error** (`3`). Neither is a
verdict on the document: the first says the instrument is broken, the second that the command was
mistyped.

## 8. Validation Evidence

- **Selftest**: `python3 scripts/selftest_scan.py` — 174 cases. `TC-META-01` asserts the battery ran
  that many, and a second case reads this number out of this file. A dropped case is then a red run
  rather than a smaller self-consistent total. They cover the schema, masking, every detector, the
  probe contract, diagnostics, sections, the terms downgrade and every exit code. Each finding of
  the WI-096 adversarial review carries its own regression pin.
- **Probe**: `--probe` verifies 18 detectors across both shipped languages on every run. The roster
  is a literal of nine rows per shipped language. A detector class with no rule behind it prints a
  DEAD row and exits 2, instead of leaving the denominator with the numerator.
- **Corpus check** and the full baseline, including the two detector defects found by measurement
  and pinned as regressions: [`references/measurement-baseline.md`](references/measurement-baseline.md).

## 9. Quick Reference

| File | Role |
|---|---|
| `references/authoring-contract.md` | Mode A — six tests, the licensed forms, worked conversions |
| `references/formalization-guide.md` | Mode B — the six rules, before/after, the specification test |
| `references/measurement-baseline.md` | why each rule exists; refuted and not-adopted candidates |
| `scripts/scan_register.py` | scanner (validate → probe → mask → scan → diagnose) |
| `scripts/selftest_scan.py` | acceptance battery |
| `data/register-ru.json` | RU markers, 5 categories, rules 2/4/6 + rule-3 vocabulary |
| `data/register-en.json` | EN markers, 5 categories, rules 2/4/6 + rule-3 vocabulary |
