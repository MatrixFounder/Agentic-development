# Framework Backlog — work-items

**Purpose:** living work-item ledger for agentic-development — enhancements, polish, and signals
with no broken contract. Defects live in [`docs/issues/`](issues/) +
[`KNOWN_ISSUES.md`](KNOWN_ISSUES.md); the split is the one `run-feedback` triages on: **defect** =
reproducible wrong behavior with a fix path, **work-item** = improvement or signal without a broken
contract.

This file is a **thin index**. Each work-item lives in its own file under [`docs/backlog/`](backlog/);
the lines below are one-per-item pointers. Read the linked file for the full signal, options, and
recommendation.

---

## Rules / Conventions

> The index below is **hand-maintained** — there is no generator. When you add or close a work-item
> you MUST edit **both** the per-item file *and* the matching line here. An index line is a
> **pointer**: one line, never a record body inlined. Format authority:
> [`known-issues-format`](../.agent/skills/known-issues-format/SKILL.md) (Registry B) — the same
> skill that owns `KNOWN_ISSUES.md`.

<!-- contract:work-items -->

**Per-work-item file** — `docs/backlog/<slug>.md`, YAML frontmatter then an H1 title and body:

```yaml
---
id: WI-1                 # WI-<n>, one flat namespace, next = max + 1 (never gap-filling)
type: work-item          # always this literal
status: open             # see status vocab below
opened_at: 2026-01-01    # ISO date first recorded (git-truthful)
slug: wi-1-short-title   # filename stem: a slugified, human-readable id+title
effort: S                # OPTIONAL — see effort vocab below
value: 'one line on what landing this buys'   # OPTIONAL
source: TASK-007 retro   # OPTIONAL — where the signal came from
# component: run-feedback         # OPTIONAL automation keys, appended AFTER source, written by
# fingerprint: 614ee37f7fb28554   # the `run-feedback` filing step. No `auto_fixable` here:
# evidence_paths:                 # /heal-issues is defect-only.
#   - path/to/artifact
# finding_ref: fnd-20260713-081500-614ee37f
# resolved_at: 2026-02-01   # add ONLY when status: done | dropped
# resolved_by: TASK 042     # add ONLY when status: done | dropped
---
```

**Status vocabulary:** `open` · `done` · `dropped` (decided against — the reasoning stays in the file).

**Effort vocabulary (optional):** `S` (hours) · `M` (a day or two) · `L` (multi-day; wants its own
TASK). Omit when the size is genuinely unknown.

**Index line format** (effort clause omitted when the file has no `effort`):

```
- **<ID>** [<title>](backlog/<slug>.md) — effort `<E>`, status `<status>`, opened <YYYY-MM-DD>
```

**Grouping.** This backlog is **human-ranked** — no category sections, no machine-imposed sort.
New lines go directly after the `<!-- feedback:discovered-issues -->` anchor (**newest first**);
that anchor is a comment rather than a heading because headings get renumbered and retitled, and
because `run-feedback`'s `file` / `doctor` are wired to it. **Do not move or delete the anchor.**

**Adding one:** ① `WI-<n>` = max existing + 1 across `docs/backlog/*.md`; ② create
`docs/backlog/<slug>.md` with the frontmatter above (body preserved verbatim — never drop a clause);
③ insert one index line directly after the anchor. `run-feedback file --as work-item` does all three.

**Closing one:** set `status: done | dropped` + `resolved_at` / `resolved_by`, add a resolution
blockquote at the top of the body, and move the index line to `## Closed`. Nothing is ever deleted:
a closed item is the answer to a question someone will ask again.

---

## Discovered issues / work-items

<!-- feedback:discovered-issues -->
- **WI-16** [A claim about code state carries no required referent](backlog/wi-16-state-claims-carry-no-required-referent.md) — effort `M`, status `open`, opened 2026-08-05
- **WI-10** [Trigger evals run on one vendor only](backlog/wi-10-trigger-evals-run-on-one-vendor-only.md) — effort `M`, status `open`, opened 2026-07-30


## Closed

- **WI-18** [The reference resolver is invoked by nothing](backlog/wi-18-the-reference-resolver-is-invoked-by-nothing.md) — effort `M`, status `done`, opened 2026-08-07 · **done 2026-08-07** (TASK 104): 4 checklists + 7 workflows + a wiring test that partitions every workflow file; the workflow half does not reach consumers
- **WI-17** [A positional reference carries no referent](backlog/wi-17-positional-references-carry-no-referent.md) — effort `M`, status `done`, opened 2026-08-07 · **done 2026-08-07** (TASK 103): the referent layer ships; no corpus migrated and no workflow wired, both stated
- **WI-15** [`SKILL.md` §6 has no rule for narrowing a rule](backlog/wi-15-skill-md-6-has-no-rule-for-narrowing-a-rule.md) — effort `S`, status `done`, opened 2026-08-05 · **done 2026-08-05** (TASK 102): §6 gains rule 5 — the three items a narrowing produces
- **WI-14** [State the glyph citation convention in `authoring-contract.md`](backlog/wi-14-glyph-citation-convention-in-authoring-contract.md) — effort `S`, status `done`, opened 2026-08-05 · **done 2026-08-05** (TASK 102): the contract states it; 0 findings removed, not 26 — every holder is already filed
- **WI-13** [Narrow rule 5 clause 2 to the vocabulary slot](backlog/wi-13-narrow-rule-5-clause-2-to-the-vocabulary-slot.md) — effort `M`, status `dropped`, opened 2026-08-05 · **dropped 2026-08-05** (§8 re-measurement): the keep-class has zero occurrences in scope; P4 to WI-14, §7.5 to WI-15
- **WI-12** [T6 does not carry the long-sentence tail](backlog/wi-12-t6-does-not-carry-the-long-sentence-tail.md) — effort `M`, status `done`, opened 2026-08-05 · **done 2026-08-05** (TASK 101): the residue was a collision between two licensed forms and the budget; 4 of 6 documents over the bound to 0 of 6
- **WI-11** [Adversarial-review MED/LOW tail from the ARC-1/ARC-2 changeset](backlog/wi-11-adversarial-review-med-low-tail-arc-1-2.md) — effort `M`, status `done`, opened 2026-08-04 · **done 2026-08-04** (third review round): 6 of 10 entries confirmed and fixed, 4 refuted by measurement; executing them surfaced a HIGH that round 1 had refuted
- **WI-9** [Extract a shared ledger_core (WI-7 option 3)](backlog/wi-9-extract-a-shared-ledger-core-wi-7-option-3.md) — effort `L`, status `done`, opened 2026-07-30 · **done 2026-07-30** (TASK 094): one `file_record` for both registries; the whole pre-existing suite passed unmodified, and a per-registry guard inventory keeps it closed
- **WI-8** [Iteration-3 residue (16 recorded findings)](backlog/wi-8-iteration-3-residue-16-recorded-findings.md) — effort `M`, status `done`, opened 2026-07-30 · **done 2026-07-30** (TASK 094): 15 of 16 rows; sec-L-10 accepted and documented (it is how linked worktrees legitimately work)
- **WI-7** [Residual tail from the vdd-multi hardening (11 items)](backlog/wi-7-residual-tail-from-the-vdd-multi-hardening-11-items.md) — effort `M`, status `done`, opened 2026-07-30 · **done 2026-07-30** (TASK 093): all 11 rows; shared primitives + parameterized tests so the two ledgers cannot diverge again
- **WI-6** [--finding accepts any path and consume unlinks it](backlog/wi-6-finding-accepts-any-path-and-consume-unlinks-it.md) — effort `S`, status `done`, opened 2026-07-30 · **done 2026-07-30** (TASK 093): containment on every path the tool deletes or moves, not only the ones it creates
- **WI-5** [find_by_fingerprint rescans the whole inbox](backlog/wi-5-find-by-fingerprint-rescans-the-whole-inbox.md) — effort `S`, status `done`, opened 2026-07-30 · **done 2026-07-30** (TASK 093): glob on the fingerprint prefix already in the filename; the invariant that enables it is pinned by a test
- **WI-4** [Eager git spawn in every Config, with a 10s cliff on the hook path](backlog/wi-4-eager-git-spawn-in-every-config-with-a-10s-cliff-on-the-hook-path.md) — effort `S`, status `done`, opened 2026-07-30 · **done 2026-07-30** (TASK 093): lazy `data_root` cached per instance, `timeout=2`, hook loads config below the cheap filters
- **WI-3** [Ledger bodies are unmarked agent-trusted context](backlog/wi-3-ledger-bodies-are-unmarked-agent-trusted-context.md) — effort `S`, status `done`, opened 2026-07-30 · **done 2026-07-30** (TASK 093): `provenance: machine` + banner, and all three bootstrap files now say bodies are data, not instructions
- **WI-2** [Record bodies are neither redacted nor size-capped](backlog/wi-2-record-bodies-are-neither-redacted-nor-size-capped.md) — effort `S`, status `done`, opened 2026-07-30 · **done 2026-07-30** (TASK 093): capped + credential-screened, deliberately **not** redacted — see the record for why refusing beats rewriting evidence
- **WI-1** [Add unit tests for skill-spec-validator](backlog/wi-1-skill-spec-validator-unit-tests.md) — effort `S`, status `done`, opened 2026-07-20 · **done 2026-07-30** (TASK 092): 38 tests + corpus anti-drift guard; both historical matcher regressions now turn the suite red
