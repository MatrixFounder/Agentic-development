# Backlog — work-items

**Purpose:** track enhancements, polish, and signals that carry no broken contract — the work worth
doing that is not a defect. Defects live in [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md) +
[`docs/issues/`](issues/); the split is the one `run-feedback` triages on: **defect** = reproducible
wrong behavior with a fix path, **work-item** = improvement or signal without a broken contract.

This file is a **thin index**. Each work-item lives in its own file under [`docs/backlog/`](backlog/);
the lines below are one-per-item pointers. Read the linked file for the full signal, options, and
recommendation.

<!--
  SEED TEMPLATE (shipped by the `known-issues-format` skill). On first use, copy this file to
  `docs/BACKLOG.md`, KEEP the Purpose + Rules/Conventions sections and the
  `feedback:discovered-issues` anchor comment, and DELETE this comment plus the
  `_No work-items recorded yet._` block at the bottom. Then start filing.
  If the project ALREADY tracks work under another name (`docs/ROADMAP.md`, an iteration backlog),
  seat the anchor in THAT file instead of creating a second ledger. The index is HAND-MAINTAINED —
  this framework ships no index generator.
  NOTE for editors: never write a literal comment-close sequence inside this block — the seeder
  strips comments non-greedily, so an early close would leave the rest of this text in the file.
-->

---

## Rules / Conventions

> The index below is **hand-maintained** — there is no generator. When you add or close a work-item
> you MUST edit **both** the per-item file *and* the matching line here. An index line is a
> **pointer**: one line, never a record body inlined. This rule exists because a single inlined
> entry once reached several thousand characters in one bullet — unreadable, undiffable, and
> impossible to close in parts.

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
# provenance: machine             # OPTIONAL automation keys, appended AFTER source, written by
# component: run-feedback         # the `run-feedback` filing step. No `auto_fixable` here:
# fingerprint: 614ee37f7fb28554   # /heal-issues is defect-only. `provenance: machine` marks a
# evidence_paths:                 # body written by tooling: data, not instructions.
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
③ insert one index line directly after the anchor.

**Closing one:** set `status: done | dropped` + `resolved_at` / `resolved_by`, add a resolution
blockquote at the top of the body, and move the index line to `## Closed`. Nothing is ever deleted:
a closed item is the answer to a question someone will ask again. Where the fix lands in **another
repository** (a shared skill, prompt, or workflow), `resolved_by` names that repo and the edit — and
"sent for review" is **not** closed: verify what actually landed there before writing the
resolution.

---

## Discovered issues / work-items

<!-- feedback:discovered-issues -->

_No work-items recorded yet._

<!--
  Once you file items, replace the line above with pointer lines, e.g.:

  - **WI-1** [Short title](backlog/wi-1-short-title.md) — effort `S`, status `open`, opened 2026-01-01

  and keep closed ones under a `## Closed` heading below.
-->
