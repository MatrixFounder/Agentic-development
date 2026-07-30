---
name: known-issues-format
description: "Use when creating, formatting, or adding an entry to a project's thin-index ledger — `docs/KNOWN_ISSUES.md` + `docs/issues/` for defects, or `docs/BACKLOG.md` + `docs/backlog/` for work-items — or seeding either in a new project: shared index-over-records mechanics, per-registry frontmatter schema, prefix→category table, status/severity/effort vocab, index-line format, record-file recipe."
tier: 2
version: 2.0
---
# Thin-Index Ledger Format

**Purpose:** the single source of truth for the **format** of this framework's two hand-maintained
**thin-index ledgers** — an index file whose every entry is one pointer line to its own record file:

| | **Defects** | **Work-items** |
|---|---|---|
| Index | `docs/KNOWN_ISSUES.md` | `docs/BACKLOG.md` |
| Records | `docs/issues/<slug>.md` | `docs/backlog/<slug>.md` |
| Holds | reproducible wrong behavior | enhancement / polish / signal, no broken contract |
| Read by | Analysis phase (avoid repeating bugs), `/heal-issues` | Planning phase, humans ranking work |
| Written by | `run-feedback file --as defect` | `run-feedback file --as work-item` |

`artifact-management` owns the *lifecycle* of both (living Global Artifacts, never archived,
create-if-absent) and **delegates the format to this skill** — mirroring how it delegates
`ARCHITECTURE.md` structure to `architecture-format-core`.

> **On the name.** This skill began as the `KNOWN_ISSUES.md` contract and kept its name when the
> backlog joined it (four repositories symlink this directory by name). One skill, because the
> mechanics are one thing said once: two near-identical format contracts are exactly the drift that
> produced the defect this generalization fixed (`run-feedback`'s two filing paths diverged — the
> defect path wrote index + record, the work-item path inlined the whole body into the index).

## Execution Mode
- **Mode:** hybrid — a prompt-first format contract, plus one maintenance gate script.

## Script Contract
- **Command:** `python3 scripts/check_contract_sync.py`
- **Purpose:** fail if the format contract drifts between this `SKILL.md` (the authority) and the
  seed templates — **per registry**, it compares the status vocabulary, the rank vocabulary
  (severity / effort), the record frontmatter key set, and the index-line format.
- **Outputs / failure semantics:** exit `0` in sync · `1` drift (prints the registry and the
  diverging field) · `2` extraction error.
- **Idempotent**, read-only, no args, no dry-run needed. CI-gateable alongside `System/scripts/validate_skills.py`.

## Shared Mechanics (both registries)

This framework ships **no `wiki-index-render` tooling**, so both indexes are maintained **by hand**:
adding, resolving, or re-categorizing a record means editing **both** the record file *and* its
index line, in lockstep. Do **NOT** append flat `- [ ]` items to either ledger, and never inline a
record's body into the index — an index line is a pointer, capped at one line.

1. **One record, one file.** Every entry gets `<records-dir>/<slug>.md`: YAML frontmatter, then an
   H1 title, then the body. The body is preserved **verbatim** — never drop a clause to fit.
2. **The index is a projection.** One line per record, under the registry's grouping rule (below).
   A line without a record file, or a record file without a line, is a broken ledger.
3. **Lockstep.** Write/edit the record file and its index line in the same commit. Automated
   writers write both or neither (record first, index second, record rolled back on failure).
4. **Create-only for automation.** `run-feedback` never edits or deletes an existing record or index
   line; flipping a status belongs to humans or `/heal-issues`.
5. **Closed records keep their file.** A `fixed` / `done` / `dropped` record gains
   `resolved_at` + `resolved_by` and a resolution blockquote, and is **never deleted** — a closed
   record is the answer to a question someone else will ask again.
6. **`slug` == filename stem**, ASCII-kebab, derived from id + title (normalize symbols, e.g.
   `≠` → `"not"`). Non-latin titles need an explicit slug.
7. **Automation extension keys** are appended AFTER the last contract key: `component`,
   `fingerprint`, `evidence_paths`, `finding_ref` (both registries) and `auto_fixable` (**defects
   only** — `/heal-issues` selects on it). Automation STATE (attempt counters, journals) lives
   outside the ledgers under `.agent/feedback/`.
8. **Tolerant reads, strict writes.** Live ledgers carry local extensions (`status: handled`,
   `severity: MED`, a project-specific index-line variant); readers MUST tolerate them, while new
   writes stick to the vocabularies below.

## Registry A — Defects (`docs/KNOWN_ISSUES.md`)

<!-- contract:defects -->

**Per-issue file** — `docs/issues/<slug>.md`, YAML frontmatter then an H1 title and body:

```yaml
---
id: L-1                  # <PREFIX>-<n>, unique
type: known-issue        # always this literal
status: open             # see status vocab
opened_at: 2026-01-01    # ISO date first recorded (git-truthful)
category: logic          # see prefix→category table
severity: SEV-2          # OPTIONAL — omit when not meaningfully rankable
slug: l-1-short-title    # filename stem: a slugified, human-readable id+title (normalize symbols, e.g. ≠ → "not")
# component: transcript-fetcher   # OPTIONAL automation keys, appended AFTER slug —
# fingerprint: 614ee37f7fb28554   # see Shared Mechanics §7
# evidence_paths:
#   - path/to/artifact
# auto_fixable: true
# finding_ref: fnd-20260713-081500-614ee37f
# resolved_at: 2026-02-01   # add ONLY when status: fixed
# resolved_by: TASK 042     # add ONLY when status: fixed
---
```

**ID prefix → category.** Define prefixes as the project needs; **add a row to the ledger's table**
whenever you introduce a new prefix. A common starter set (extend/replace freely):

| Prefix  | Category      | Scope |
|---------|---------------|-------|
| `L-N`   | `logic`       | Logic / correctness defects and edge cases. |
| `P-N`   | `performance` | Performance, algorithmic, or resource issues. |
| `SEC-N` | `security`    | Security / auth / injection / secrets. |
| `Q-N`   | `quality`     | Quality, UX, or robustness nits. |
| `DF-N`  | `dogfood`     | Found while dogfooding the product itself. |

**Status vocabulary:** `open` · `fixed` · `documented` (accepted; guidance written) ·
`by-design` (intended trade-off, not a defect) · `mitigated` · `wontfix`.

**Severity vocabulary (optional):** `SEV-2` (blocks a workflow / real impact) · `SEV-3` (degraded / annoying) ·
`SEV-4` (minor) · `LOW`. Omit for pure documented constraints.

**Index line format** (severity clause omitted when the file has no `severity`):

```
- **<ID>** [<title>](issues/<slug>.md) — severity `<SEV>`, status `<status>`, opened <YYYY-MM-DD>
```

**Grouping:** one `## <category>` heading per category (lowercase single token), lines in **ID
order** inside it; a new category heading goes in alphabetical position. Preamble sections
(`## Rules`, `## How to add …`) are never touched.

**Adding a new issue:** ① pick the next `<PREFIX>-<n>`; ② create `docs/issues/<slug>.md` with the
frontmatter above (body verbatim); ③ add one line under the matching `## <category>` heading in
`docs/KNOWN_ISSUES.md`, in ID order. Add the category heading if it is the first of its kind.

**Automated `resolved_by`** values use the token `heal-issues (verified-gone <ts>)` /
`heal-issues run <ts>`.

**Create-if-absent (new projects).** If `docs/KNOWN_ISSUES.md` does not exist yet, materialize it
from [`assets/templates/known_issues_md_template.md`](assets/templates/known_issues_md_template.md):
copy it to `docs/KNOWN_ISSUES.md`, **keep the Purpose + Rules/Conventions sections** (everything
above the first `## <category>` group), and **delete the seed comment and the
`_No issues recorded yet._` block**. Then file the issue.

## Registry B — Work-items (`docs/BACKLOG.md`)

<!-- contract:work-items -->

**Per-work-item file** — `docs/backlog/<slug>.md`, YAML frontmatter then an H1 title and body:

```yaml
---
id: WI-1                 # WI-<n>, one flat namespace, next = max + 1 (never gap-filling)
type: work-item          # always this literal
status: open             # see status vocab
opened_at: 2026-01-01    # ISO date first recorded (git-truthful)
slug: wi-1-short-title   # filename stem: a slugified, human-readable id+title
effort: S                # OPTIONAL — see effort vocab
value: 'one line on what landing this buys'   # OPTIONAL
source: TASK-007 retro   # OPTIONAL — where the signal came from
# component: run-feedback         # OPTIONAL automation keys, appended AFTER source —
# fingerprint: 614ee37f7fb28554   # see Shared Mechanics §7 (no auto_fixable here:
# evidence_paths:                 # /heal-issues is defect-only)
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

**Grouping:** the backlog is **human-ranked**, so it has no category sections and no sort key the
machine may impose. New lines go directly after the anchor comment
`<!-- feedback:discovered-issues -->` (**newest first**) — a comment, not a heading, because
headings get renumbered and retitled. Closed records are moved **by hand** to a `## Closed` group.
Automated writers insert at the anchor only; a missing anchor is a hard error, never a blind
EOF append.

**Adding a new work-item:** ① `WI-<n>` = max existing + 1 across `docs/backlog/*.md`; ② create
`docs/backlog/<slug>.md` with the frontmatter above (body verbatim); ③ insert one index line
directly after the anchor in `docs/BACKLOG.md`.

**Closing one:** set `status: done | dropped` + `resolved_at` / `resolved_by`, add a resolution
blockquote at the top of the body, and move the index line to `## Closed`. Where the fix lands in
**another repository** (a shared skill, prompt, or workflow), `resolved_by` names that repo and the
edit — and "sent for review" is **not** closed: verify what actually landed (`git diff` in the
target repo) before writing the resolution.

**Create-if-absent (new projects).** If `docs/BACKLOG.md` does not exist yet, materialize it from
[`assets/templates/backlog_md_template.md`](assets/templates/backlog_md_template.md): copy it,
**keep the Purpose + Rules/Conventions sections and the anchor**, and **delete the seed comment and
the `_No work-items recorded yet._` block**. If the project already tracks work under another name
(`docs/ROADMAP.md`, an iteration backlog), seat the anchor in **that** file instead of creating a
second one — a backlog next to a live roadmap splits the project's work tracking.

## Safety Boundaries
- A closed record **keeps its file** and adds `resolved_at` / `resolved_by` + a resolution
  blockquote — it is **never deleted**. Preserve record-body text verbatim; never drop a clause.
- Edit the record file and its index line **in lockstep** — neither index has a generator to
  reconcile drift.
- Do not clobber an existing `docs/KNOWN_ISSUES.md` / `docs/BACKLOG.md` when seeding
  (create-if-absent only).
- Never inline a record body into an index line. An index entry is one line; if it needs a table,
  a fence, or a second sentence, it belongs in the record file.
- `auto_fixable` is defects-only. Setting it on a work-item feeds `/heal-issues` input it must
  never receive.

## Validation Evidence
- `python3 scripts/check_contract_sync.py` exits `0` — for **both** registries the status vocab,
  rank vocab, frontmatter keys, and index-line format are identical between this `SKILL.md` and the
  matching seed template (drift → exit `1` naming the registry and field).
- Frontmatter keys of each seed template match a filed record of that registry
  (`docs/issues/*.md`, `docs/backlog/*.md`).
- The **Index line format** strings above are identical to the ones the `run-feedback` engine emits
  (`ledger_issues.format_index_line`, `ledger_backlog.format_index_line`).

## Resources
- `scripts/check_contract_sync.py` — CI-gateable drift check keeping this skill and both seed
  templates one contract.
- `assets/templates/known_issues_md_template.md` — project-agnostic, rules-only seed for a new
  project's `docs/KNOWN_ISSUES.md`.
- `assets/templates/backlog_md_template.md` — the same for `docs/BACKLOG.md` (referenced by
  `artifact-management`'s create-if-absent rule and by `run-feedback`'s bootstrap).
