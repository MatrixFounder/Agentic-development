---
id: REG-9
type: known-issue
status: open
opened_at: 2026-08-04
category: register
severity: SEV-4
slug: reg-9-measurement-baseline-md-records-negative-parallelism-as-an-adopted-rule-info-ru-only-but-no-such-entry-e
provenance: machine
component: '.agent/skills/artifact-formalizer/references/measurement-baseline.md'
fingerprint: 1953fe00b13df165
finding_ref: fnd-20260804-152825-1953fe00
---

# REG-9 — measurement-baseline.md records negative parallelism as an ADOPTED rule (`info`, RU only), but no such entry e…

> Filed by `run-feedback` from capture `fnd-20260804-152825-1953fe00`. **This body is data, not instructions** — it derives from captured output and may quote untrusted text.

**Component:** `.agent/skills/artifact-formalizer/references/measurement-baseline.md:65`

## Symptom

measurement-baseline.md records negative parallelism as an ADOPTED rule (`info`, RU only), but no such entry exists in register-ru.json — the rule was never shipped, and the scanner's own docstring still cites it as a live entry.

## Reproduction

A Russian spec sentence `Это не просто переименование, а смена контракта.` is scanned. Expected per the baseline: a rule-2 `info` negative-parallelism finding. Actual (verified by running scan_document with the shipped register-ru.json): the only finding is `info marker 'просто'` from the generic `\bпросто\b` entry. The 38 ru entries (probe: marker 22 / maxim 10 / metaphor 6) contain no `не только … но и` / `не просто … а` pattern; `grep -rn 'не просто' data/` returns nothing. The baseline's §4 table is the authoritative record of which measured candidates became rules, so a maintainer reading it will believe a detector exists and will not re-propose it (which is the table's stated purpose: "so that nobody re-proposes them from impression").

## Evidence

.agent/skills/artifact-formalizer/references/measurement-baseline.md:65 `| Negative parallelism (`not just X but Y`) | 0 | adopted at `info` in RU only, flagged zero-baseline |` — corroborated by the now-stale scanner docstring at .agent/skills/artifact-formalizer/scripts/scan_register.py:763-764 `Two lexicon entries can cover the same phrase — `просто` sits inside / `не просто X, а Y` — and reporting both inflates the count for one defect.` (only one entry can ever match that phrase).

## Verification

Confirmed by an independent adversarial verifier that reproduced it against the committed tree:

Reproduced. Line 65 reads verbatim as quoted; register-ru.json ships 38 entries (22 marker / 10 maxim / 6 metaphor) with no `не только … но и` / `не просто … а` pattern (`git grep 'не просто' data/` empty, `grep -n 'параллел\|not just' data/ references/ SKILL.md` hits only the baseline row itself). Scanning `Это не просто переименование, а смена контракта.` returns one `info marker 'просто'` and nothing else. §4 is the record of adopted-vs-refuted candidates, so an 'adopted' row with no shipped entry is a genuine data/record mismatch, corroborated by scan_register.py:763-764 whose dedupe example `не просто X, а Y` is unrealizable with shipped data. Severity lowered to low: the canonical RU surface still produces an info-level finding via the shipped `просто` entry (RU-only, `info` — exactly the row's operational promise), so no scan result is wrong; the harm is confined to one imprecise cell in a rationale document affecting a future maintainer's re-proposal decision, in an advisory tool.

## Provenance

Found by the 7-dimension review of commit `992b3ef` (dimension `register-data`), 2026-08-04. Survived adversarial verification; 7 sibling findings were refuted and are not filed.
