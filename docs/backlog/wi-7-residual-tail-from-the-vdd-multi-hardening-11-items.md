---
id: WI-7
type: work-item
status: open
opened_at: 2026-07-30
slug: wi-7-residual-tail-from-the-vdd-multi-hardening-11-items
effort: M
value: 'closes the asymmetry between the two ledger writers and pins three unpinned guards'
source: 'vdd-multi task-091'
component: run-feedback
fingerprint: 5db1f7129dde5d90
finding_ref: fnd-20260730-112009-5db1f712
---

# WI-7 — Residual tail from the vdd-multi hardening (11 items)

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
