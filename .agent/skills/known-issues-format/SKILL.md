---
name: known-issues-format
description: Use when creating, formatting, or adding an entry to a project's docs/KNOWN_ISSUES.md thin-index ledger, or seeding it in a new project — frontmatter schema, prefix→category table, status/severity vocab, index-line format, per-issue file recipe.
tier: 2
version: 1.0
---
# Known Issues Format

**Purpose:** The single source of truth for the **format** of `docs/KNOWN_ISSUES.md` — a living,
hand-maintained **thin index** where each issue is its own file under `docs/issues/`. `artifact-management`
owns the *lifecycle* (it is a living Global Artifact, never archived, create-if-absent) and **delegates the
format to this skill** — mirroring how it delegates `ARCHITECTURE.md` structure to `architecture-format-core`.

This framework ships **no `wiki-index-render` tooling**, so the index is maintained **by hand**: adding,
resolving, or re-categorizing an issue means editing **both** the per-issue file *and* its index line, in
lockstep. Do **NOT** append flat `- [ ]` items to the ledger.

## Execution Mode
- **Mode:** prompt-first (a format contract; no scripts).

## Format Contract

**Per-issue file** — `docs/issues/<slug>.md`, YAML frontmatter then an H1 title and body:

```yaml
---
id: L-1                  # <PREFIX>-<n>, unique
type: known-issue        # always this literal
status: open             # see status vocab
opened_at: 2026-01-01    # ISO date first recorded (git-truthful)
category: logic          # see prefix→category table
severity: SEV-2          # OPTIONAL — omit when not meaningfully rankable
slug: l-1-short-title    # == filename stem, == slugify(id)-slugify(title)
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
`by-design` (intended trade-off) · `mitigated` · `wontfix`.

**Severity vocabulary (optional):** `SEV-2` (blocks a workflow / real impact) · `SEV-3` (degraded) ·
`SEV-4` (minor) · `LOW`. Omit for pure documented constraints.

**Index line format** (severity clause omitted when the file has no `severity`):

```
- **<ID>** [<title>](issues/<slug>.md) — severity `<SEV>`, status `<status>`, opened <YYYY-MM-DD>
```

**Adding a new issue:** ① pick the next `<PREFIX>-<n>`; ② create `docs/issues/<slug>.md` with the
frontmatter above (body preserved verbatim); ③ add one line under the matching `## <category>` heading in
`docs/KNOWN_ISSUES.md`, in ID order. Add the category heading if it is the first of its kind.

**Create-if-absent (new projects).** If `docs/KNOWN_ISSUES.md` does not exist yet, materialize it from
[`assets/templates/known_issues_md_template.md`](assets/templates/known_issues_md_template.md) (copy to
`docs/KNOWN_ISSUES.md`, keep the *Rules / Conventions* header, drop the seed comment), then file the issue.

## Safety Boundaries
- A `fixed` issue **keeps its file** and adds a `resolved_at` / `resolved_by` line + a resolution
  blockquote — it is **never deleted**. Preserve issue-body text verbatim; never drop a clause.
- Edit the per-issue file and its index line **in lockstep** — the index has no generator to reconcile drift.
- Do not clobber an existing `docs/KNOWN_ISSUES.md` when seeding (create-if-absent only).

## Validation Evidence
- Frontmatter keys of `assets/templates/known_issues_md_template.md` match a filed `docs/issues/*.md`.
- The **Index line format** string above is identical to the one used in the live ledger.

## Resources
- `assets/templates/known_issues_md_template.md` — the project-agnostic, rules-only seed for a new
  project's `docs/KNOWN_ISSUES.md` (referenced by `artifact-management`'s create-if-absent rule).
