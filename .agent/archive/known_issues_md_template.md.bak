# Known Issues & Tech Debt

**Purpose:** Track recurring bugs, architectural limitations, and sensitive areas to avoid
repeating mistakes.

This file is a **thin index**. Each issue lives in its own file under [`docs/issues/`](issues/);
the lines below are one-per-issue pointers grouped by category. Read the linked file for the full
symptom, workaround, and cross-links.

<!--
  SEED TEMPLATE (shipped by the `artifact-management` skill). On first use, copy this file to
  `docs/KNOWN_ISSUES.md`, keep everything down to the second `---`, then start filing issues.
  Delete this comment. This layout mirrors the `obsidian-llm-wiki` schema; this framework ships
  NO `wiki-index-render` tooling, so the index is HAND-MAINTAINED.
-->

---

## Rules / Conventions

> The index below is **hand-maintained** — there is no generator. When you add, resolve, or
> re-categorize an issue you MUST edit **both** the per-issue file *and* the matching line here.
> These rules keep that hand-editing consistent.

**Per-issue file** — `docs/issues/<slug>.md`, YAML frontmatter then an H1 title and body:

```yaml
---
id: L-1                  # <PREFIX>-<n>, unique (see prefix→category table)
type: known-issue        # always this literal
status: open             # see status vocab below
opened_at: 2026-01-01    # ISO date first recorded (git-truthful)
category: logic          # see prefix→category table
severity: SEV-2          # OPTIONAL — omit when not meaningfully rankable
slug: l-1-short-kebab-title   # == filename stem, == slugify(id)-slugify(title)
---
```

**ID prefix → category.** Define prefixes as the project needs them; **add a row here** whenever you
introduce a new prefix. A common starter set (extend/replace freely):

| Prefix  | Category      | Scope |
|---------|---------------|-------|
| `L-N`   | `logic`       | Logic / correctness defects and edge cases. |
| `P-N`   | `performance` | Performance, algorithmic, or resource issues. |
| `SEC-N` | `security`    | Security / auth / injection / secrets. |
| `Q-N`   | `quality`     | Quality, UX, or robustness nits. |
| `DF-N`  | `dogfood`     | Found while dogfooding the product itself. |

**Status vocabulary:** `open` · `fixed` · `documented` (accepted; guidance written) ·
`by-design` (intended trade-off, not a defect) · `mitigated` · `wontfix`.
A `fixed` issue **keeps its file** and adds `resolved_at` / `resolved_by` + a resolution
blockquote; it is never deleted.

**Severity vocabulary (optional):** `SEV-2` (blocks a workflow / real impact) ·
`SEV-3` (degraded / annoying) · `SEV-4` (minor) · `LOW`. Omit for pure documented constraints.

**Index line format** (severity clause omitted when the file has no `severity`):

```
- **<ID>** [<title>](issues/<slug>.md) — severity `<SEV>`, status `<status>`, opened <YYYY-MM-DD>
```

**Adding a new issue:** ① pick the next `<PREFIX>-<n>`; ② create `docs/issues/<slug>.md` with the
frontmatter above (body preserved verbatim — never drop a clause); ③ add one line under the matching
`## <category>` heading below, in ID order. Add the category heading if it is the first of its kind.

---

_No issues recorded yet._

<!--
  Once you file issues, replace the line above with category groups, e.g.:

  ## logic
  - **L-1** [Short title](issues/l-1-short-kebab-title.md) — severity `SEV-2`, status `open`, opened 2026-01-01
-->
