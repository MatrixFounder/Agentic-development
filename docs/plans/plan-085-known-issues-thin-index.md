# Development Plan: Task 085 — KNOWN_ISSUES thin-index restructure

> Mode: Framework Upgrade, **docs-only**. No code / skills / prompts / workflows touched.
> Living docs untouched (ARCHITECTURE.md not affected — no system-structure change).
> Scope fixed by operator: `docs/KNOWN_ISSUES.md` → thin index + `docs/issues/*.md`.

## Step 0 — Backup (rollback safety)
```
mkdir -p .agent/archive
cp docs/KNOWN_ISSUES.md .agent/archive/KNOWN_ISSUES.md.bak
```
Rollback = `cp .agent/archive/KNOWN_ISSUES.md.bak docs/KNOWN_ISSUES.md && rm -rf docs/issues`.
(No bootstrap file — CLAUDE/AGENTS/GEMINI — is edited, so per framework-upgrade §3.1 they
need no backup here; only the one file being restructured is backed up.)

## Step 1 — Create per-issue files (R1, R2, R3)
`mkdir -p docs/issues`, then write 10 files `docs/issues/<slug>.md`. Each file:
- Frontmatter: `id`, `type: known-issue`, `status`, `opened_at`, `category`,
  `severity` (only AT-2/AT-6/WR-1), `slug`.
- `# <Title>` (H1).
- Body structured as `- **Constraint / Symptom**`, `- **Guidance / Workaround**`,
  `- **Affected components**` (where known), `- **Related**` (MD cross-links) —
  **carrying the full original sentence(s) verbatim** so no clause is lost (R3/NFR-1).
- WR-1 additionally carries the "Scaffold wrappers are generated" sub-bullet in full.

Slugs (`<id-slug>-<title-slug>`), matching the wiki convention:
`at-1-no-session-resumption`, `at-2-task-status-lag`, `at-3-one-team-per-session`,
`at-4-no-leadership-transfer`, `at-5-higher-token-costs`,
`at-6-teamdelete-does-not-clean-up-after-protocol-shutdown`,
`at-7-async-spawn-not-sync-return`,
`at-8-model-inheritance-inconsistent-across-agent-types`,
`at-9-runtime-sends-structured-json-despite-docs`, `wr-1-wrapper-sot-drift-risk`.

## Step 2 — Rewrite the thin index (R4, R5)
Overwrite `docs/KNOWN_ISSUES.md` **in place** (same path — R7) with:
1. Title + Purpose line (kept from the original).
2. **## Rules / Conventions** — the "правила": what the file is (hand-maintained, no
   render tooling), ID scheme table (AT/WR → category), status vocab
   (`open`/`fixed`/`documented`/`by-design`/`mitigated`/`wontfix`), severity vocab
   (`SEV-2..4`/`LOW`), the one-line index format, and the "adding a new issue" recipe.
3. **## <category>** groups (`agent-teams`, `wrappers`) with one line per issue:
   `- **ID** [title](issues/slug.md) — severity \`X\`, status \`Y\`, opened YYYY-MM-DD`
   (severity omitted when none). Preserve the "Layer A not affected" scoping note.

## Step 3 — Verify (R6, R7)
```
ls docs/issues/*.md | wc -l          # expect 10
grep -oE 'issues/[a-z0-9-]+\.md' docs/KNOWN_ISSUES.md | sort -u   # every target exists
for f in $(grep -oE 'issues/[a-z0-9-]+\.md' docs/KNOWN_ISSUES.md | sort -u); do \
  test -f "docs/$f" || echo "BROKEN: $f"; done
grep -c 'type: known-issue' docs/issues/*.md   # frontmatter present
head -1 docs/KNOWN_ISSUES.md                    # still at same path
```
- Manual content-preservation check: each of the 10 original clauses appears in a file.
- Confirm no other file references were broken (path unchanged → none expected).

## Step 4 — Finalize
- Record meta-audit (Modes A+B) in `docs/reviews/framework-audit-085.md`.
- Persist session state (`update_state.py`) at the phase boundary.
- No version bump / CHANGELOG entry required unless operator asks (pure docs restructure);
  note the option in the completion summary.

## Rollback
`cp .agent/archive/KNOWN_ISSUES.md.bak docs/KNOWN_ISSUES.md && rm -rf docs/issues`.
