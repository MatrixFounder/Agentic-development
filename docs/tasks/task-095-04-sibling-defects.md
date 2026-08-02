# Task 095.4 — Sibling defects of the same class

<!--
  Anchors below (`<!-- contract:* -->`) are how a MACHINE addresses a section:
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
-->

## Use Case Connection
- UC-1 (generalized)
- Covers `R7`

<!-- contract:goal -->

## Task Goal
Close the same defect where it already exists but nobody filed it. WI-30 reported one site; a
sweep found three more, and the unreported ones are the silent kind.

<!-- contract:changes -->

## Changes Description
### Changes in Existing Files
- **`skill-product-backlog-prioritization/scripts/calculate_wsjf.py`** — `get_column_indices`
  falls back to POSITION when no English name matches. A **partial** match is deliberately not
  rescued: mixing strategies inside one table would pair the wrong column with the wrong weight,
  and a wrong WSJF score is worse than a refusal.
- **`.agent/tools/task_id_tool.py`** — `normalize_slug` transliterates (Cyrillic table, then NFKD)
  BEFORE the character strip. `"untitled"` survives only for input with no word characters.
- **`.agent/tools/archive_protocol.py`** — three couplings: the meta section is located by
  `contract:meta` first; both private slug derivations now DELEGATE to `normalize_slug`; the
  `| Slug |` value is captured as non-pipe text and normalized.

<!-- contract:tests -->

## Test Cases
`tests/test_language_independence.py` — 14 tests in three classes. Each fix landed its failing
test first (3, then 5, observed Red). Includes latin-behaviour regression guards, because every
existing archived task was named by these functions.

<!-- contract:acceptance -->

## Acceptance Criteria
- [ ] two different non-latin titles produce two different filenames
- [ ] latin slugs byte-identical (6 pinned pairs)
- [ ] a genuinely empty slug still falls back to `untitled`
- [ ] every slug is a safe filename stem
- [ ] the 59 pre-existing `.agent/tools/` tests stay green
- [ ] `archive_protocol` DELEGATES rather than re-implementing (asserted directly)

## Notes
`parse_task_meta` gated on the English string `"Meta Information"`, so it did not recognize the
meta table this framework's own template writes (`## 0. Meta`) and quietly took the H1 fallback.
Found while fixing the slug, not reported by anyone.

**Known limit, stated rather than left implicit:** the `| Task ID |` and `| Slug |` FIELD LABELS
are still English. They are written by the framework's own template, so they are closer to a key
than to prose — but a project that translates its meta table will not be read. Recorded here
instead of silently half-fixed.
