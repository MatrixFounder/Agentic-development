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
