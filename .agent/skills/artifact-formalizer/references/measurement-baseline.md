# Measurement baseline — why each rule exists, and why the others do not

Every rule in this skill traces to a row below. Rules that a measurement did not support are
recorded as **not adopted**, with their figures, so that nobody re-proposes them from impression.

Measured 2026-08-03 and re-measured 2026-08-04 over two independently authored corpora: this
framework's `docs/tasks/` and a downstream project's `docs/tasks/`, ~12,200 lines in total.

## 1. The corpus baseline

Prose segmented per block (a list item is its own block), sentences split inside a block only.

| Corpus | Files | Mean words/sentence | >35 words | Evaluative markers /100 lines |
| :--- | ---: | ---: | ---: | ---: |
| framework, oldest tasks | 21 | 5.8 | 0.0% | 0.1 |
| framework, middle tasks | 33 | 12.1 | 2.6% | 0.6 |
| framework, newest tasks | 9 | 14.1 | 3.8% | 1.4 |
| downstream, oldest tasks | 48 | 13.6 | 2.9% | 1.2 |
| downstream, newest tasks | 10 | 15.4 | 3.6% | 2.1 |

Evaluative-marker density rises monotonically in **both** corpora: 14× across the framework's, 1.75×
across the downstream project's. Mean sentence length rises 2.4× in the framework's. Two signals
moving the same direction in two independently authored corpora is why they became rules 1 and 2.

**Threshold derivation.** 35 words sits far above every corpus mean, so a conforming sentence is
never flagged, and it catches the ~3.7% tail that both newest corpora grew.

## 2. A first measurement was wrong and was discarded

The initial pass split sentences over the whole file. Consecutive `- [ ]` lines carry no terminal
punctuation, so they glued into single pseudo-sentences of 101 to 167 words. Those figures measured
the checklist format, not the prose. The block-aware pass above replaced them.

The same defect appeared a second time, one construct later: `*Actor:* X. *Main:* Y.` glued because
the boundary test looked for whitespace-then-capital and found `*`. It was caught by running the
scanner against the specification that defined it.

Both are pinned as regressions (TC-REG-01, TC-REG-03). **A silent zero and a broken instrument look
identical** — which is now enforced rather than remembered: §5 below.

## 3. Candidates the measurement refuted

Expected to show drift. Did not.

| Candidate | Measured (newest vs older) | Verdict |
| :--- | :--- | :--- |
| Bold density | 9.1 vs 30.7 per 100 lines | Improved. No rule. |
| Em-dash density | 12.2 vs 22.8 per 100 lines | Improved. No rule. |
| Emoji density | 0.0 vs 8.7 per 100 lines | improved here, rose on a small base downstream (§6) |
| Table-cell prose | 22% of cells over 120 chars | real, and owned by `documentation-standards` §5.1 |

Some general style guides rate **em-dash density** a critical AI tell. This corpus disagrees: the
density is falling. A general heuristic loses to a measurement of the actual corpus.

## 4. Generic AI-writing tells, measured at zero

A published catalogue of generic AI-writing tells was measured against the same ~12,200 lines
before any of it was adopted. The regexes were probe-tested against known-positive strings first
(§2). Almost nothing fired: these documents have a different failure mode than marketing or blog
AI-slop.

| Pattern | Hits | Action |
| :--- | ---: | :--- |
| Marketing vocabulary (`robust`, `seamless`, `leverage`, `delve`, `crucial`…) | 3 | **adopted** as `warn` — rule-2 class, near-zero cost |
| Negative parallelism (`не просто X, а Y`, `not just X but Y`) | 0 | not adopted — the RU `просто` entry already reports the surface at `info` |
| Filler transitions (`Moreover`, `Furthermore`, `In conclusion`) | 0 | not adopted — a rule that never fires is prose read for nothing |
| `-ing` footers (`…, underscoring the shift`) | 0 | not adopted — its target is rule 3, which has its own detector (§7) |
| Authoritative truisms (`at its core`, `the reality is`) | 0 | not adopted |
| Hedging disclaimers (`arguably`, `undoubtedly`) | 0 | not adopted — Open Questions already carry uncertainty |
| Future tense in specifications | 0 | not adopted — the RTM uses `MUST`, so the tell has no surface |

**Deliberate divergence from user-documentation style guides.** Several forbid
`**Title:** description` lists and prescribe flowing paragraphs. This skill *requires* the labelled
form: rule 3 moves justification under a `**Why.**` lead-in. The genres differ — user documentation
optimizes for reading order, a specification for separating a claim from its justification.

## 5. The measurement that produced version 2.0

A ten-file downstream task set was scanned with v1.0. It returned **0 warn over 2352 lines**, and
the document was full of defects. Four causes, each now closed.

| Cause | Evidence | Fix |
| :--- | :--- | :--- |
| The exit criterion could not see the dominant defect | 158 emoji severities, all hard-coded `info`; SKILL.md required "zero `warn`" | `emoji_severity` is `warn` (§6) |
| Rules 3, 4 and 6 had no detector at all | 27 maxim-shaped sentences, 127 private-metaphor occurrences across 15 families | Partial detectors with declared recall (§7) |
| A bare zero is unreadable | `sentence_length` max **35** against a limit of `>35`; six sentences at exactly 35 | `DIAGNOSTICS` + `sentence_near_limit` (§8) |
| A lexicon entry could be dead on arrival | `\bочевидно\b` matched no inflected form; «неочевиден», «очевидный» passed | mandatory `probe`, validated against the entry's own pattern |

The last one reproduced twice during this very revision: `\b(bites?|biting) (back|test)?\b` failed
its own probe `"Check that the gate bites."`, and `\bочевид(н\w*)\b` failed the Russian short form
«очевиден», whose fleeting vowel removes the stem. Both were rejected at load time rather than
shipping as silent zeros.

**Cost of fixing late.** In that corpus, prose carrying a rule-4 or rule-6 `warn` is 50 of 987
sentences: 731 of 14,288 words, or 5.1%. Removing it after the fact requires reading and editing all
14,288.

The first draft of this paragraph converted both figures to tokens. It used **two different
word-to-token ratios for the same corpus** — 1.50 and 2.52 — which inflated the ratio it argued from
by about 1.7×.

Words are the measured unit and are quoted directly. A token count depends on the tokenizer and is
not reproducible from this document.

## 6. Emoji severity: `info` → `warn`

v1.0 reported emoji at `info` on the reasoning that emoji density was *falling* (§3). That measured
the wrong thing. The trend was falling; the absolute count in a single artifact was 158, and `info`
placed it outside the stated exit criterion.

Rule 5 admits no judgement: a glyph either carries a severity or it does not. `info` is the class
for findings the author decides, so it was the wrong class here.

`✓` and `✗` (U+2713/U+2717) are excluded everywhere. They are status **values** throughout this
repository, not severities, and 33 of their 52 occurrences sit outside a table.

`✅`, `❌`, `☑`, `☒` and `☐` are excluded inside a table cell, where §5.1 governs, and are reported
outside one. Those 671 occurrences are what rule 5's second clause covers. A glyph carrying no
severity at all is diff metadata, and does not belong in a specification either
([`formalization-guide.md`](formalization-guide.md) rule 5).

## 7. Rules 3, 4 and 6 — detectors with declared recall

v1.0 stated that these rules "have no detector and will not get one". That claim is true of *full*
coverage and was applied to *any* coverage, which is what let 127 metaphor occurrences through. The
adopted position is narrower and measured:

| Rule | Detector | Measured on the ten-file corpus | Recall limit, stated in SKILL.md §5 |
| :--- | :--- | ---: | :--- |
| 3 | obligation + causal connective in one sentence | 5 findings, all true positives on inspection | reasoning split across two sentences is invisible |
| 4 | named personifications + maxim templates | 46 `warn`, 15 `info` | a novel aphorism passes |
| 6 | candidate list + `--terms` string test | 31 `warn`, 34 `info` | a metaphor coined today is in neither list |

Precision was checked against the framework's own corpus. The same detectors produce 2 rule-4
`warn` and 9 rule-6 `info` over 3,821 sentences there.

**Why that number matters.** It is the rate of a corpus without this failure mode, not the rate of a
rule that fires everywhere.

**One false-positive class was found and closed by measurement:** `\b(head|tail)s?\b` with the `i`
flag matched the git ref `HEAD` on every anchor line. It is the only case-sensitive entry in either
lexicon, and its `note` records why.

## 8. Reading a zero correctly

Every run now prints what each detector saw. On the ten-file corpus the sentence distribution stops
at exactly the limit:

```
sentences : 987, mean 14.5, max 35 (limit 35)   <-- PRESSED AGAINST THE LIMIT
```

The framework's own corpus, unaffected by that pressure, runs to a maximum of 76 words with 61
sentences over the limit. A distribution that halts one word below the bound was written for the
gate. `sentence_near_limit` converts that invisible tail into a worklist without moving the
threshold. Its default band of 30 words covers 4.6% and 3.3% of the two corpora.

## 9. Selftest coverage

`scripts/selftest_scan.py` covers:

- **Schema** — each case asserts the message fragment it expects, rather than a non-zero exit.
  Rejected inputs:
  - a non-compiling regex, unknown keys, a bad severity;
  - a pattern that misses its own probe, or matches it zero-width;
  - a catastrophically backtracking pattern;
  - a rule-3 vocabulary whose probe does not fire, and a lexicon entry claiming rule 3;
  - duplicate keys, and thresholds that conflict or become inconsistent when merged.
- **Masking** — frontmatter, multi-backtick and line-spanning code spans, tilde and unterminated
  fences, CRLF, and the plain-prose control that separates masking from blanket suppression.
- **Detectors** — one case each, plus the false-positive controls named in §7 and §10.
- **Instrument** — the probe contract, the dead-detector exit, diagnostics including the pressure
  band edges, the section worklist, the terms downgrade and its false-downgrade control.
- **Interface** — same-basename origin disambiguation, duplicate input paths, and every exit code.

`--probe` verifies 18 detectors across both shipped languages on every ordinary run as well.

## 10. The adversarial review that produced this revision

Two fresh-context reviews of the v2.0 candidate returned 65 findings. Every one was reproduced by
execution before it was accepted. Four defeated a headline design claim of the tool:

| Finding | Reproduction | Fix |
| :--- | :--- | :--- |
| A code span of two or more backticks leaked its body | a marker quoted that way → 1 `warn` | CommonMark backtick runs, `re.S` |
| `--terms` downgraded on a substring | sources holding `legacy` downgraded `leg` | whole-word match, plus a false-downgrade control |
| `---` prose was eaten as frontmatter | a paragraph between two rules → 0 findings | bounded body, every line must look like YAML |
| Rule 5 was declared complete and was not | `⛔`, `✔`, `‼` all scored zero | class widened to the pictographic blocks |

Three of the four produced **exactly the silent zero this tool exists to prevent**, while the run
reported `18/18 detectors live` and exited 0. A probe roster is evidence about the detectors, not
about the masker feeding them.

Also closed, each with its own pin:

- a binary `--terms` file exited 1, outside the documented contract;
- an `argparse` usage error exited 2, indistinguishable from a dead detector — it is now 3;
- the prose-coverage share printed two denominators as one statement;
- the `near < max` invariant was evadable by splitting the two keys across two rule files;
- rule-3 probes were exempt from the masking guard every lexicon entry already carried.

**One guard hung on the case it was written for.** The first draft of the regex budget timed each
pattern by running it to completion — and the patterns worth rejecting are exactly the ones that do
not complete. It is now a static check for a repeated group carrying an unbounded quantifier, plus
a `SIGALRM` budget for the shapes that check misses.

**Five battery cases were structurally unfailable** and were replaced:

1. a byte-comparison of a file nothing writes to;
2. an assertion the constructor guaranteed;
3. thirteen schema cases sharing a predicate that only required non-empty stderr;
4. an exit-code-only check on the skill's own document;
5. a `>= 16` count against a shipped 18.

## 10.1 The masking defect, and the numbers that found it (TASK 097)

`mask()` applied four regular expressions in sequence, each over the whole text, with
`HTML_COMMENT` ahead of `CODE_SPAN` and `re.S` on both. A comment boundary landing inside a code
span removed one backtick. The survivor paired with a later one, and from that offset prose was
masked as code and code scanned as prose, to the end of the file.

Found by measurement, like the two defects above it. Every figure is reproducible in this
repository.

| # | Measurement | Value |
| :--- | :--- | :--- |
| E1 | Fixture of valid Markdown: Cyrillic letters surviving `mask()` | 28 of 167 |
| E2 | Same fixture, findings reported | none; `0 warn`, exit 0 |
| E3 | Same fixture with the trigger removed | 1 finding, `§5.5 r2` |
| E4 | Documents with odd backtick parity after `mask()` | 14 of 598 |
| E5 | `task_md_template.md`: prose reaching rule 1 | 27%, against 50% |
| E6 | `task_md_template.md`: lines masked away | 42, against 17 |
| E7 | Prose the corrected pass restores to the rules | +61,889 letters, 169 documents |
| E8 | Masked-letter share across the corpus | p50 22.1%, p95 63.1%, max 97.3% |

**E8 is why the share is reported and not gated.** A threshold at 60% fires on 26 correct
documents. Eight of them are fenced by construction, where a high share is the right answer.
`documentation-standards` §4 forbids a gate that fails on correct documents. The share is therefore
diagnostic, and `SKILL.md` §2 says how to read it.

**The rule-3 probe exercised 1 pattern of 23.** One declared sentence stood in for the whole
modal-by-causal cross-product. Replacing `\bshall\b` in `register-en.json` left `--probe` at
`18/18 detectors live` and the battery at `128/128` — the count v3.24.0 shipped — while `The
installer shall abort because the target exists.` lost its finding. Each pattern now carries a
declared example and is exercised against a known-good partner.

**Deriving the example from the pattern was tried and rejected.** `\bshall\b` reduces to `shall`,
which matches by construction — so `\bZZZNEVER\b` reduces to `ZZZNEVER` and probes live just as
happily. A derived example cannot detect the edit it exists to detect. The declared example can,
through two signatures: an example its pattern no longer matches, and an example left orphaned when
its pattern was renamed.

**A declared example is now mandatory (TASK 099).** While it was optional, a pattern carrying none
was reported `unprobed` and its row still printed live, which is the state that re-opens the defect
above. A rule file holding a rule-3 pattern that declares no example no longer loads.

**The probe roster is a literal, not a count of what loaded (TASK 099).** It holds nine rows per
shipped language. Deleting every rule-6 entry of one language printed `17/17 detectors live` and
exit 0; it now prints `17/18` and exits 2, and deleting `register-ru.json` prints `14/18` rather
than `9/9`. A class with no detector behind it appends a DEAD row instead of leaving the
denominator with the numerator.

**After the fix, over 602 documents:** every one exits 0, odd parity falls from 14 to 13, and 19
unpaired backticks are named as input defects rather than silently mispaired.

## 11. Which figures here are reproducible, and which are not

Reproducible in this repository, by the commands in SKILL.md §3: every detector count, the selftest
count, the zero-`warn` claim about this skill's own documents, and the framework-corpus figures in
§7.

**Not reproducible here**: every figure derived from the downstream ten-file corpus (§5, §8) —
`0 warn over 2352 lines`, 158 emoji, 127 metaphor occurrences, 27 maxims, the 987-sentence
distribution, and the 5.1% cost measurement. That corpus is another project's `docs/tasks/`, it is
not vendored here, and no revision pins it.

Treat those as the record of a measurement taken once, not as a claim a reader can check. A
reproducible replacement is the framework's own corpus in §7, and any future threshold move must be
justified from a corpus that ships with the skill.

**A second shipped corpus now exists**: `evals/corpus/`, 20 documents authored for §12 and committed
with the inputs that produced them. It is small and drawn once, so it supports the ordering claim
§12 makes and not a threshold move. §7's corpus remains the larger one.

## 12. The first behavioural campaign — Mode A and the §5 recall gaps (TASK 101)

Every section above measures the scanner. The scanner is Mode B. §Purpose of `SKILL.md` states that
Mode A carries the value, and until this campaign no figure described Mode A.

**Method.** Six authoring prompts, two arms each, `claude-opus-5`, 2026-08-05. The arms differ in
one input: `with_contract` is handed `references/authoring-contract.md` and `baseline` is not. Both
run under `tempfile.mkdtemp()` with every file and command tool denied, so neither can reach this
repository.

**Repetitions are not uniform.** `A1` and `A5` ran three times per arm. The other four cases and
axis B ran once.

**Why those two.** They carry the whole rule-1 finding of §12.2, and three draws separate a
systematic effect from a sampling artefact at a quarter of the cost of a uniform campaign.

26 runs, `$10.80`, 20 authoring documents, none rejected by a validity guard. The corpus ships at
`evals/corpus/`, each document beside the model, prompt hash and contract hash that produced it.

### 12.1 Axis A — what the contract changed

Findings over the ten documents per arm. The scanner is the grader, so these are its own counts.

| Kind | Severity | baseline | with_contract |
| :--- | :--- | ---: | ---: |
| `cell_width` | warn | 315 | 1 |
| `cell_sentences` | warn | 175 | 0 |
| `sentence_length` | warn | 6 | 5 |
| `marker` | warn | 6 | 0 |
| `maxim` | warn | 1 | **7** |
| **warn, total** | | **503** | **13** |
| `metaphor` (rule 6) | info | 42 | 0 |
| `marker` (rule 2) | info | 29 | 13 |
| `sentence_near_limit` | info | 25 | 3 |
| `maxim` (rule 4) | info | 8 | 0 |
| `cell_sentences` | info | 9 | 0 |

| Metric | baseline | with_contract |
| :--- | ---: | ---: |
| `warn_per_100_lines` | 13.41 | 0.60 |
| `marker_per_100_lines` | 1.15 | 0.72 |
| `sentence_mean` | 10.96 | 9.04 |
| `prose_share_of_nonblank` | 48.2% | 58.2% |
| documents pressed against the limit | 2 | 0 |
| lines authored | 2819 | 2371 |

**Read the warn column before the rate.** 490 of the 503 baseline `warn` findings are `cell_width`
and `cell_sentences`, which `documentation-standards` §5.1 owns. The contract's licensed **Table
row** form removes them. So `warn_per_100_lines` reports table shape first and register second, and
a reader who quotes the 22× ratio as a register figure is quoting the wrong thing.

**The register classes proper.** `metaphor` falls 42 to 0 and `marker` 35 to 13, both counting warn
and info together. Those are rules 6 and 2, and they are where the contract does what it claims.

**The two documents pressed against the limit are both baseline.** `A5/baseline/rep-3` stops at
exactly 35 words and `A6/baseline/rep-1` at 34. §8 names that distribution: written for the gate.
No contract-arm document shows it.

### 12.2 Rule 1 — the one class the contract did not carry

`sentence_length` is 6 against 5, and the longest sentence in the campaign is 52 words, written by
the contract arm. Longest sentence per document, against a bound of 35:

| Case / arm | rep-1 | rep-2 | rep-3 | over the bound |
| :--- | ---: | ---: | ---: | :--- |
| A1 baseline | 46 | 30 | 39 | 2 of 3 |
| **A1 with_contract** | 36 | **52** | 47 | **3 of 3** |
| A5 baseline | 29 | 32 | 35 | 0 of 3 |
| A5 with_contract | **47** | 23 | 23 | 1 of 3 |

**Three repetitions were run to separate a systematic effect from one draw, and they separate it.**
On `A1` the contract arm exceeds the bound in every repetition and its worst exceeds the baseline's
worst. That is not a sampling artefact. On `A5` it is one repetition of three, and the baseline
never exceeds — though `A5/baseline/rep-3` reaches exactly 35, which §8 counts as the other failure
of the same rule.

**Reading the sentences changed the finding.** Every over-bound sentence was examined rather than
counted.

| Arm | Over-bound sentences | What they are |
| :--- | ---: | :--- |
| baseline | 6 | running prose: subordinate clauses, parenthetical explanation, justification welded into the statement |
| with_contract | 8 | 5 `In scope` / `Out of scope` enumerations and 3 acceptance criteria — **no running prose at all** |

The contract removed the long *prose* sentence entirely. What remained was a collision inside the
contract itself: the **Scope** and **Test obligation** forms each produce one sentence whose length
the **Budget** test forbids, and the contract said nothing about how the two resolve. An author who
followed it exactly produced a 52-word sentence.

**Closed in `authoring-contract.md`, not in the threshold.** A licensed form that exceeds the budget
is rendered as a list, one item per line, so each item is its own block. The worked conversion there
is the 52-word sentence from `evals/corpus/A1/with_contract/rep-2.md`, which the rule takes to a
longest block of 7 words with nothing added and nothing cut.

### 12.2.1 The amendment was measured, not assumed

Six runs, `A1` and `A5`, `with_contract` only, three repetitions each, same prompts and same model.
One input changed: the contract text. The baseline arm was not re-drawn — the contract does not
reach it, so re-running it would spend tokens to reproduce a number the committed corpus holds.
`$4.15`. The corpus ships at `evals/corpus-wi12/`.

```sh
python3 evals/run_authoring.py --cases A1 --cases A5 --arm with_contract \
  --reps 3 --jobs 3 --out-root evals/corpus-wi12
```

Longest sentence per document, bound 35:

| Case | before r1 | r2 | r3 | after r1 | r2 | r3 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 | **36** | **52** | **47** | 32 | 32 | 29 |
| A5 | **47** | 23 | 23 | 26 | 21 | 25 |

Documents over the bound: **4 of 6 → 0 of 6.** `warn` by kind over the same twelve documents:

| Kind | before | after | attributable to the amendment |
| :--- | ---: | ---: | :--- |
| `sentence_length` | 5 | **0** | yes — the amendment addresses exactly this construct, and the before side was 3 of 3 on `A1` across repetitions |
| `maxim` | 7 | 0 | **no** — those seven were one word repeated in one document (§12.3), and the amendment says nothing about rule 4 |
| `cell_width` | 1 | 1 | unchanged |

No document in either set presses against the limit.

**What the six runs do not establish.** Two cases of six, one campaign per side. The `maxim` row is
in the table to show which movement is *not* claimed: a metric that fell for a reason the change
cannot explain is a different draw, not an effect.

**What three repetitions still do not settle.** Six prompts. Repetitions reduce sampling noise
inside a case and do nothing for the diversity of the set, which is what §5 of
`skill-creator/references/advanced-eval-patterns.md` calls the mirage.

### 12.3 A finding count is not a document count

The contract arm's 7 `maxim` warns are seven occurrences of `краснеет` on seven consecutive lines of
**one** document, `A5/with_contract/rep-3`, in a list of test obligations. The baseline's single
`maxim` warn sits in a different document.

Counted by document rather than by finding, rule 4 is 1 contract-arm document against 1 baseline
document. Counted by finding it is 7 against 1. Both numbers are above; neither alone describes what
happened. The same caution applies to `cell_width`, where one table contributes a row per cell.

### 12.4 Axis B — the reading pass over the §5 recall gaps

Three seeded fixtures and one control, each reporting `0 warn / 0 info` from the scanner. Six
planted defects: two rule-3 requirements carrying their justification across a sentence boundary,
two aphorisms written for the fixture, two nouns coined for the fixture.

| Measure | Value |
| :--- | ---: |
| Planted defects found, on the declared line with the declared rule | 6 of 6 |
| Findings matching no planted defect | 0 |
| Findings on the control fixture | 0 |

**What this does not establish.** The defects are seeded, so the key is objective by construction
and carries no author judgement about what a real document meant. Their **difficulty** is not
calibrated: a defect planted for a fixture may be more conspicuous than one that occurs naturally.
The prompt also names the three rule classes, which is faithful to step B4 and easier than an
unprimed audit. Axis B ran **once**, so this figure carries the single-draw caveat §12.2 removed
from rule 1.

### 12.5 The campaign found a defect in its own grader

Two runs of `A5/baseline` died on a transport error, and `run_authoring.py` wrote the 80-byte string
the envelope returned. The executor recorded `is_error: true`, printed `FAILED` and exited 1.

The grader read the document and not its metadata. `API Error: Connection closed mid-response.` is
one line of prose, so it scored `0 warn`, `measured: true`, and a `prose_share_of_nonblank` of 100%,
and it entered the arm mean as a conforming document. `PROSE_FLOOR` cannot see it: in one line of
prose the prose share is total.

| Guard | Now | Catches |
| :--- | :--- | :--- |
| `is_error` read from `rep-N.meta.json` | the run's own record | any failure the executor already detected |
| `MIN_LINES = 5` | a shape floor | a corpus placed by hand, where no metadata exists |

Pinned as `TC-EV-10g` and `TC-EV-10h`. Both runs were re-executed and the committed corpus holds no
errored run.

**Why it belongs in this document.** It is the same shape as §2 and §10: an instrument reporting a
clean zero over an input it never measured, found by looking at what the zero was computed from.

### 12.6 What is reproducible, and what a rerun would change

Reproducible from this repository: every figure in §12.1 to §12.4, by
`python3 evals/grade_run.py` over the committed `evals/corpus/`. The grader is a pure function of
the corpus and the shipped rule files, and `TC-EV-14` asserts that grading the committed corpus
reproduces the committed `report.json`.

Not reproducible: the corpus itself. Four of the six cases were drawn once, and axis B was drawn
once. No interval is attached to any arm-level figure.

**What this campaign licenses.** It supports the ordering in §Purpose — Mode A before Mode B — with
figures from a corpus that ships. It does **not** license a threshold move: §11 requires that from a
corpus, and this one is 20 documents over six prompts.
