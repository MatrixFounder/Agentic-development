# Example: filing a new known issue

**Situation:** during development you find that `reindex --delta` misses an mtime-preserved rename,
orphaning inbound links. You want to record it. The project's ledger has no `logic` category yet.

## Step 1 — pick the next ID
No `logic` issues exist. Introduce prefix `L`, next number `L-1`. Add a row to the ledger's
prefix→category table: `| L-N | logic | Logic / correctness defects. |`.

## Step 2 — create the per-issue file
`docs/issues/l-1-reindex-delta-misses-mtime-preserved-rename.md`:

```yaml
---
id: L-1
type: known-issue
status: open
opened_at: 2026-07-10
category: logic
severity: SEV-2
slug: l-1-reindex-delta-misses-mtime-preserved-rename
---
```
…followed by `# reindex --delta misses an mtime-preserved rename` and a body
(`- **Symptom** … - **Root cause** … - **Affected components** … - **Fix plan** …`).

## Step 3 — add ONE index line (lockstep)
Under `## logic` in `docs/KNOWN_ISSUES.md`:

```
- **L-1** [reindex --delta misses an mtime-preserved rename](issues/l-1-reindex-delta-misses-mtime-preserved-rename.md) — severity `SEV-2`, status `open`, opened 2026-07-10
```

## Fresh project?
If `docs/KNOWN_ISSUES.md` did not exist, first copy
`assets/templates/known_issues_md_template.md` → `docs/KNOWN_ISSUES.md` — keep the Purpose +
Rules/Conventions sections (everything above the first `## <category>` group), and delete the seed
comment and the `_No issues recorded yet._` block — then do Steps 1-3.

## Later — when it's fixed
Keep the file. Add `resolved_at` / `resolved_by`, flip `status: fixed`, prepend a resolution
blockquote, and update the index line's `status`. **Never delete the file.**
