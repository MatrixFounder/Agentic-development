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
- **Mode:** hybrid — a prompt-first format contract, plus one maintenance gate script.

## Script Contract
- **Command:** `python3 scripts/check_contract_sync.py`
- **Purpose:** fail if the format contract drifts between this `SKILL.md` (the authority) and the seed
  template — it compares the status/severity vocabularies, the frontmatter key set, and the index-line format.
- **Outputs / failure semantics:** exit `0` in sync · `1` drift (prints the diverging field) · `2` extraction error.
- **Idempotent**, read-only, no args, no dry-run needed. CI-gateable alongside `System/scripts/validate_skills.py`.

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
slug: l-1-short-title    # filename stem: a slugified, human-readable id+title (normalize symbols, e.g. ≠ → "not")
# component: transcript-fetcher   # OPTIONAL automation keys, appended AFTER slug —
# fingerprint: 614ee37f7fb28554   # see "Automation extension keys" below
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

**Automation extension keys (optional).** Automated tools append machine-oriented keys AFTER
`slug` — `component`, `fingerprint`, `evidence_paths`, `auto_fixable`, `finding_ref` (written by
the `run-feedback` skill's filing step; consumed by the `/heal-issues` harness, which selects
ONLY issues carrying an explicit `auto_fixable: true`). Automation STATE (attempt counters,
journals) lives outside the ledger under `.agent/feedback/`. Per-project ledgers may carry local
read-side extensions (e.g. `status: handled`, `severity: MED`); readers MUST tolerate them, while
new writes stick to the vocabularies above. Automated `resolved_by` values use the token
`heal-issues (verified-gone <ts>)` / `heal-issues run <ts>`.

**Adding a new issue:** ① pick the next `<PREFIX>-<n>`; ② create `docs/issues/<slug>.md` with the
frontmatter above (body preserved verbatim); ③ add one line under the matching `## <category>` heading in
`docs/KNOWN_ISSUES.md`, in ID order. Add the category heading if it is the first of its kind.

**Create-if-absent (new projects).** If `docs/KNOWN_ISSUES.md` does not exist yet, materialize it from
[`assets/templates/known_issues_md_template.md`](assets/templates/known_issues_md_template.md): copy it to
`docs/KNOWN_ISSUES.md`, **keep the Purpose + Rules/Conventions sections** (everything above the first
`## <category>` group), and **delete the seed comment and the `_No issues recorded yet._` block**. Then file the issue.

## Safety Boundaries
- A `fixed` issue **keeps its file** and adds a `resolved_at` / `resolved_by` line + a resolution
  blockquote — it is **never deleted**. Preserve issue-body text verbatim; never drop a clause.
- Edit the per-issue file and its index line **in lockstep** — the index has no generator to reconcile drift.
- Do not clobber an existing `docs/KNOWN_ISSUES.md` when seeding (create-if-absent only).

## Validation Evidence
- `python3 scripts/check_contract_sync.py` exits `0` — status/severity vocab, frontmatter keys, and the
  index-line format are identical between this `SKILL.md` and the seed template (drift → exit `1`).
- Frontmatter keys of `assets/templates/known_issues_md_template.md` match a filed `docs/issues/*.md`.
- The **Index line format** string above is identical to the one used in the live ledger.

## Resources
- `scripts/check_contract_sync.py` — CI-gateable drift check keeping this skill and the seed template one contract.
- `assets/templates/known_issues_md_template.md` — the project-agnostic, rules-only seed for a new
  project's `docs/KNOWN_ISSUES.md` (referenced by `artifact-management`'s create-if-absent rule).
