---
id: WI-7
type: work-item
status: done
opened_at: 2026-07-30
slug: wi-7-residual-tail-from-the-vdd-multi-hardening-11-items
effort: M
value: 'closes the asymmetry between the two ledger writers and pins three unpinned guards'
source: 'vdd-multi task-091'
component: run-feedback
fingerprint: 5db1f7129dde5d90
finding_ref: fnd-20260730-112009-5db1f712
resolved_at: 2026-07-30
resolved_by: TASK 093
---

# WI-7 — Residual tail from the vdd-multi hardening (11 items)

> **✅ DONE 2026-07-30 (TASK 093) — all 11 rows.** Option 2 was recommended (split: V8/V12/V17
> first, the rest later); all of it landed in one pass instead, because the fixes turned out to share
> the primitives. Option 3 (extract a shared `ledger_core`) is still **not** done and remains the
> right answer when a third registry appears — recorded in TASK 093 §5.
>
> | id | Closed by |
> |----|-----------|
> | V7 | `_strip_placeholder` walks forward to the first non-blank line; a `## ` heading (any non-blank line) stops the walk, so a later section's placeholder can no longer be deleted. |
> | V8 | `scan_anchors` tracks the opening fence's **character and length** per CommonMark §4.5 — a 3-backtick line no longer closes a 4-backtick fence, `~~~`/``` do not close each other, an info string cannot close, and a ≥4-space-indented line is not a fence. **Still fail-closed**: an unclosed fence really does put the anchor inside a code block, so filing still exits 4 — but the remediation now names the opening line number. |
> | V9 | Every config-derived probe in `doctor` moved inside the guarded block (`issues_dir`/`index_path` were outside it, so the one command whose job is reporting a broken config aborted on one); `UnicodeDecodeError` is caught (it is not an `OSError`); an over-cap backlog reports `backlog_anchor_present: "unchecked"` and no longer counts as not-ready. |
> | V12 | `read_verbatim` moved to `atomic.py` and **both** ledgers read through it; `ledger_issues.insert_index_line` now splits on `\n` only, inherits `\r` on the inserted line, and preserves the file's own trailing ending. A CRLF-fidelity test runs against both modules. |
> | V-13 | `backlog_anchor` (non-empty, single line, unpadded — an empty one matched every blank line), `id_prefixes` (str keys, `^[A-Za-z][A-Za-z0-9_-]{0,31}$` values) and `excerpt_max_chars`/`body_max_chars` (int ≥ 1) are validated at access with exit 3. `TF-X` and `WIKI-INGEST` from the live `Universal-skills` config are **pinned as test cases** so a future tightening cannot silently break a consumer (audit 093 Risk 1). |
> | V-08 | `doctor`'s writability probe uses `tempfile.mkstemp` — the last predictable-name write in the engine. A planted `.doctor-probe` symlink is no longer written through. |
> | V-10 | `provisional_id` now exists on the **defect** path too, and both paths print a `NOTE: the id above is PROVISIONAL` line — the human line is what an operator or a model copies into a plan. |
> | V11 | Both ledgers **build** frontmatter from `CONTRACT_KEYS` via `_build_meta`, indexing `sources[key]` so a tuple key with no value raises `KeyError` at once. `ledger_issues.CONTRACT_KEYS` is live rather than dead. A test pins **both** tuples to the `known-issues-format` SKILL.md authority using the sync gate's own extractor — verified by mutation (adding a key reddens it). |
> | V17 | `_consume_or_explain`: on a failed move after a good ledger write, the finding's status is flipped in place best-effort and the error names both halves plus the recovery. A retry now reports "already filed" (exit 2, actionable) instead of "record exists" (exit 4, a dead end **forever**). |
> | V-22 | All three rewritten so each fails when its guard is removed, **confirmed by running the three mutations**: the one-line test now uses six real reader separators including `U+2028`/`U+2029` written as escapes (the old input was a tab and two spaces — it could not have produced two lines); the temp-name test asserts unpredictability across two writes rather than PID-absence (a fixed `x.tmp.0` passed the old one); the symlink test **split in two**, one per guard. |
> | V-21 | `serialize` quotes what a YAML 1.1 parser would coerce (`true/yes/off/null/~`, int/float/hex/octal), ISO dates stay bare, and the `'`→`’` rewrite now warns on stderr naming the key. |
>
> **Two findings the work surfaced that were not on the list.** ① Writing the V-22 symlink test
> revealed both create-only guards emitted the **same** message, so no test could name which one
> fired — they are now distinguishable, which is what made the split possible. ② In human mode the
> top-level handler **dropped `remediation` entirely**, so every carefully written remediation string
> in this engine was visible only under `--json-errors` — including V17's recovery instructions,
> whose whole value is telling the operator what to do next. Both fixed here.
>
> **The generalized lesson stands and was applied**: the fix for "a fix landed on one of two
> symmetric paths" is not vigilance but *shared primitives plus parameterized tests*. Where a guard
> exists in both ledgers, `tests/test_wi_tail.py` now tests both in one test rather than two
> hand-copied ones that can drift.


> Origin: vdd-multi iteration 2 (2026-07-30) — the residual tail after two fix rounds.
> Full report: `docs/reviews/vdd-multi-091-092.md`.

**Signal.** Two adversarial iterations closed every exploit but left a documented tail of
robustness and test-validity findings. They are collected here rather than left in a review file,
because a finding that lives only in a report is a finding nobody will action.

| id | Where | What |
|----|-------|------|
| V7 | `ledger_backlog.insert_after_anchor` | the placeholder strip probes offsets 2-3 — it misses a two-blank-line shape and can delete a *different* section's placeholder; should walk forward to the first non-blank line instead |
| V8 | `ledger_backlog.anchor_positions` | naive fence toggle: one unclosed ``` above the anchor makes ALL filing exit 4 (fail-closed DoS); a 3-backtick line inside a 4-backtick fence, `~~~` nesting, and 4-space indented code all fool it |
| V9 | `run_feedback.cmd_doctor` | `cfg.backlog_path` / `issues_dir` / `index_path` are read OUTSIDE the try, so a bad config still aborts the report; `UnicodeDecodeError` is uncaught; an over-cap backlog reports `anchor absent` rather than `unchecked` |
| V12 | `ledger_issues.insert_index_line` | the CRLF/`U+2028` fix landed only in the backlog module; the defect index still `read_text()` + `splitlines()` + whole-file `rstrip` |
| V-13 | `config.py` | `backlog_anchor` (an empty value matches every blank line), `id_prefixes` values, and `excerpt_max_chars` reach behaviour with no validation |
| V-08 | `cmd_doctor` | the `.doctor-probe` write/unlink follows a planted symlink — the one remaining predictable-name write |
| V-10 | both ledgers | `provisional_id` exists only in the JSON payload; the human dry-run line still presents the id as final, and `file_defect` has no such flag |
| V11 | both ledgers | the `CONTRACT_KEYS[:5]` assertion restates the dict literal three lines above; `ledger_issues.CONTRACT_KEYS` is still dead, and nothing pins either tuple to the SKILL.md authority |
| V17 | `cmd_file` | if `inbox.consume` fails after the ledger write, the finding stays `new` while the record exists → every retry exits 4 forever, needing a hand edit |
| V-22 | tests | three tests pass for the wrong reason (a "one line" test whose input has no separator; a PID-absence test that a fixed-name regression would pass; a symlink test that cannot tell which of two guards is load-bearing) |
| V-21 | `frontmatter` | `"true"`/`"2026"` round-trip as bool/int under a real YAML parser; the `'`→U+2019 rewrite is silent |

**Why it matters.** None is exploitable on its own — that is why they are one work-item and not five
defects. But V8 is a live availability risk (a stray fence in a hand-edited ledger blocks all
filing), V12 leaves the *defect* ledger with the corruption the backlog ledger no longer has, and
V-22 means three guards are not actually pinned.

**Generalized.** Fixing a finding on one of two symmetric code paths is half a fix, and the half
that ships is the one that makes the reviewer stop looking. When two modules implement the same
contract, a fix lands in both or the asymmetry gets written down.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Work through the table in one pass, each with a test | M | a day, mostly mechanical |
| 2 | Split: V8/V12/V17 now (behaviour), the rest later | S+S | two passes, but the risky ones close first |
| 3 | Extract the shared ledger mechanics into one module so `ledger_issues`/`ledger_backlog` cannot diverge again | L | the real fix for the whole class; bigger blast radius |

**Recommendation.** Option 2 now, option 3 when a third registry appears — the divergence between the
two ledger modules is what produced WI-23 in the first place and it is still the shape of this list.

**Acceptance.** Each row either has a test pinning the fixed behaviour, or a line in the skill's
Safety Boundaries stating the limitation honestly.

**Related.** `docs/reviews/vdd-multi-091-092.md` (iteration 2 section) · WI-2…WI-6 (the iteration-1
deferrals) · `known-issues-format` RF-2 lineage.
