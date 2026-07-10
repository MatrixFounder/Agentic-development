# Development Plan: Task 086 — KNOWN_ISSUES format framework-resident (mechanism B)

> Mode A/B gates via `skill-self-improvement-verificator`. **Architecture untouched** (no
> system-structure change). Release **v3.20.15**. No code, no installer, no test change.
> Seed mechanism: **B (skill-driven)** — operator-selected.

## Step 0 — Backup (rollback safety)
```
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done   # §3.1 mandate
cp .agent/skills/artifact-management/SKILL.md            .agent/archive/artifact-management.SKILL.md.bak
cp .agent/skills/skill-reverse-engineering/SKILL.md      .agent/archive/skill-reverse-engineering.SKILL.md.bak2
cp CHANGELOG.md CHANGELOG.ru.md README.md README.ru.md   .agent/archive/   # version-bump set
```

## Step 1 — Template asset (R1, R4)
Create `.agent/skills/artifact-management/assets/KNOWN_ISSUES.template.md`:
- Project-agnostic, rules-only. Purpose + thin-index note + **Rules / Conventions** (frontmatter schema,
  a **generic** prefix→category starter table, status/severity vocab, index-line format, "Adding a new issue").
- **No** `AT-`/`WR-` issues (repo-specific). Empty-state placeholder `_No issues recorded yet._`.
- Lives under `.agent/skills/…/assets/` → auto-ships via the existing `.agent/skills` link component (R4, no installer change).

## Step 2 — artifact-management contract (R2), TIER 0, v1.1 → 1.2
- Add **KNOWN_ISSUES.md** to §Global Artifacts (one line, alongside TASK/PLAN/ARCHITECTURE).
- Add a **compact** "Known Issues (thin index)" subsection: one-file-per-issue under `docs/issues/`, the
  frontmatter/index-line contract in brief, and the **create-if-absent** rule:
  *"if `docs/KNOWN_ISSUES.md` is absent when you record an issue, materialize it from
  `assets/KNOWN_ISSUES.template.md` first."* Keep it tight — TIER-0 is loaded every session.

## Step 3 — reverse-engineering pointer redirect (R3), v1.2 → 1.3
- In §2, change the pointer from *"that file's Rules/Conventions section"* to defer to **`artifact-management`**
  (the framework-resident contract) — so it resolves in a fresh project. Keep the "do NOT append flat `- [ ]`"
  and new-prefix guidance.

## Step 4 — Verify (R5)
- Template self-consistent with the live `docs/KNOWN_ISSUES.md` field set (frontmatter keys, index-line format).
- Both skills: valid frontmatter, version bumped, no broken links, `core-principles`/`skill-safe-commands` untouched.
- Fresh-project trace (desk-check): TIER-0 load → format known → create-if-absent → §2 pointer resolves.
- No installer touched ⇒ installer pytest unaffected (spot-run `tests/installer` optional sanity).

## Step 5 — Docs, registry, release
- `System/Docs/SKILLS.md`: bump artifact-management / skill-reverse-engineering version rows if present.
- `CHANGELOG.md` + `CHANGELOG.ru.md`: new **v3.20.15** entry (Added: template asset; Changed: TIER-0 contract, §2 redirect).
- `README.md` + `README.ru.md`: title stamp v3.20.14 → v3.20.15.
- `update_state.py` at completion.

## Rollback
Restore any edited file from `.agent/archive/<file>.bak`. Template asset removal + version-header reverts fully undo the change; no data migration performed.
