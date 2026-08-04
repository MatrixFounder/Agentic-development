---
id: WI-11
type: work-item
status: done
opened_at: 2026-08-04
resolved_at: 2026-08-04
resolved_by: third review round (see docs/reviews/vdd-adversarial-arc-1-2.md §7)
category: quality
effort: M
slug: wi-11-adversarial-review-med-low-tail-arc-1-2
source: /vdd-adversarial on the ARC-1/ARC-2 changeset, 2026-08-04
---

# WI-11 — Adversarial-review MED/LOW tail from the ARC-1/ARC-2 changeset

> **Done 2026-08-04.** Closed under this file's own rule — **execute each entry, do not read it**.
> Of the ten tail entries, **six were confirmed and fixed, four were refuted by measurement**. The
> rule earned its place: executing the entries surfaced a **HIGH** that was never in this ledger,
> and that round 1 had explicitly recorded as *not reproducing* — the documented Step 5.5 command
> exits `1` on the happy path. Full record in
> [the review](../reviews/vdd-adversarial-arc-1-2.md) §7.

The `/vdd-adversarial` pass over the ARC-1/ARC-2 fixes produced 85 findings; 75 survived an
independent per-finding refutation. The five HIGH ones were fixed in the same session. 30 MED and
33 LOW were separated into this file rather than bundled: 63 more edits would have made the HIGH
remediation unreviewable.

## Closed by the second review round

The doc/contract-drift group turned out to contain a **live instance of ARC-1**, not drift, so it
was taken immediately rather than left here.

- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `System/Docs/ORCHESTRATOR.md` all documented the bare
  `task_id_tool.py <slug>` form. Measured by execution: with `task-095-01..03` present and no
  parent it returns **096** where the protocol form returns **095**. Fixed in all four; pinned by
  `TestBareInvocationShadowsTheParentId`.
- `schemas.py` `allow_correction: default true` → `false`; pinned by
  `TestSchemaMatchesTheDispatcher`.
- `System/Agents/02_analyst_prompt.md` now calls the tool instead of scanning `docs/tasks/`.
- ORCHESTRATOR stale test counts corrected to measured.

## Closed by the third review round

**Confirmed and fixed.**

| Entry | Reproduction | Fix |
| :--- | :--- | :--- |
| Escaped pipe under-counts `cell_width` | 200-char cell containing `\|` → no finding | split on unescaped pipes (`CELL_SPLIT`) |
| U+2028 shifts line numbers | reported line 4, real `\n`-line 3 | count lines by `\n`, not `str.splitlines()` |
| Duplicate `--rules` double-counts | 1 info → 2 info, same document | dedupe by `realpath` |
| Leading `---` eaten as frontmatter | `---\n\n# Title\n\n<prose>` scanned to **zero** findings | frontmatter may not open with a blank line |
| `e.g. Capital` splits a sentence | 12 corpus instances, each halving the measured length | measured abbreviation exemptions |
| `selftest_scan.py` not in CI | only the pytest list ran | its own workflow step |
| `skill-archive-task` `version: 1.3` after a ~93-line rewrite | — | `2.0`; the protocol's mandatory steps changed |
| Stale `Example Flow` | showed a bare tool call, bare `mv`, no Step 5.5 | rewritten to the real 11-step sequence — **and executed** |

**Refuted by measurement.** Recorded because the refutation is the useful part:

- *"A stray unmatched backtick masks the rest of the line."* The pairing is CommonMark-correct: the
  first opener pairs with the next run of equal length. A genuinely unmatched backtick masks
  **nothing** — the regex requires a closer. Pinned as `TC-PREC-08`.
- *"Sentence splitting glues on decimals."* `1.5 Beta` has no whitespace after the period, so the
  rule never fired there. Pinned as `TC-PREC-07`.
- *`__pycache__` hygiene.* Already covered by `.gitignore`; **0** tracked. Nothing to do.
- *Exempting `etc.` / `т.д.` along with `e.g.`* — rejected. Both measured **0** hits here and in
  general prose they genuinely do end sentences; exempting them trades a false split for a false
  glue, which inflates sentence length and fabricates findings. Pinned as `TC-PREC-09`.

## What executing the entries found that reading them would not

The `Example Flow` rewrite was a documentation entry — the lowest-stakes item in the list. Running
the rewritten commands showed Step 5.5 exiting **1**, "a link regressed", on the protocol's own
happy path: the conservation law probed a `SLOT_RESOLVED` target, but a slot map is a **forward
reference** that Step 7 fulfils moments later. An agent following the protocol literally would
stop on success.

Round 1 had received this exact finding from a critic and refuted it — by measuring the command
*without* `--slot`, which is not the documented command. A refutation is a measurement and can be
defective like any other.

## Follow-up — closed 2026-08-04

`scan_register.py` was replaced mid-session by a rewrite (probe-tested detectors, rule numbers,
per-language `reasoning` vocabularies). **All five precision fixes above are present in it and were
re-verified against it.**

At the time this record was written, `data/register-{en,ru}.json` still carried the previous schema
and lacked the required `probe` field, so the scanner exited 2 on its own rules and the CI selftest
step was red. Both data files now carry `probe` on every entry, and the field is validated against
the entry's own pattern at load time.

Verified 2026-08-04: `scan_register.py --probe` → 18/18 detectors live, exit 0;
`selftest_scan.py` → 128/128, exit 0.

## Related

[[ARC-1]], [[ARC-2]], and `docs/reviews/vdd-adversarial-arc-1-2.md` (full method, agent counts,
the six refuted findings, and the round-3 correction).
