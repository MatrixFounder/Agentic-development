# Development Plan: Task 087 — dedicated `known-issues-format` skill

> Mode A/B gates. Architecture untouched. Release **v3.20.16**. No code/installer/test change.
> SKILL CREATION GATE: `init_skill.py` (manual skill-file creation is prohibited).

## Step 0 — Backup
```
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done
cp .agent/skills/artifact-management/SKILL.md       .agent/archive/artifact-management.SKILL.md.bak2
cp .agent/skills/skill-reverse-engineering/SKILL.md .agent/archive/skill-reverse-engineering.SKILL.md.bak3
cp System/Docs/SKILLS.md CHANGELOG.md CHANGELOG.ru.md README.md README.ru.md .agent/archive/
```

## Step 1 — Scaffold the skill (R1, gate)
`python3 .agent/skills/skill-creator/scripts/init_skill.py known-issues-format --tier 2`
Tier 2 (Extended, on-demand): referenced by `artifact-management` (TIER 0) + `skill-reverse-engineering`;
not gated to one pipeline phase.

## Step 2 — Author the contract (R2)
Populate `known-issues-format/SKILL.md` with the full format authority: thin-index model, per-issue file
frontmatter schema, prefix→category table, status/severity vocab, index-line format, "Adding a new issue"
recipe, and the create-if-absent note pointing at its own template.

## Step 3 — Own the template (R2, R3)
`git mv .agent/skills/artifact-management/assets/KNOWN_ISSUES.template.md \
        .agent/skills/known-issues-format/assets/templates/known_issues_md_template.md`
Remove the now-empty `artifact-management/assets/`. Template body unchanged (schema already verified in 086).

## Step 4 — Slim the hub (R4)
In `artifact-management` (v1.2 → 1.3): keep the KNOWN_ISSUES.md Global-Artifact line + create-if-absent, but
replace the detailed inline contract (frontmatter block, index-line format) with a **one-line delegation** to
`known-issues-format` — mirroring the existing ARCHITECTURE → `architecture-format-core` delegation.

## Step 5 — Repoint reverse-engineering (R5)
`skill-reverse-engineering §2` (v1.3 → 1.4): point the filing pointer at `known-issues-format`.

## Step 6 — Verify (R6)
- `python3 System/scripts/validate_skills.py` → 44/44.
- Template frontmatter keys == live `docs/KNOWN_ISSUES.md`; index-line format string identical.
- `artifact-management/assets/` gone (no orphan); refs in hub + reverse-eng resolve to the new skill.
- `core-principles`/`skill-safe-commands` untouched.

## Step 7 — Docs, registry, release
- `System/Docs/SKILLS.md`: add a `known-issues-format` row; revert the artifact-management row's asset mention to a delegation note.
- `CHANGELOG.md` + `.ru.md`: **v3.20.16** entry. README EN/RU stamp v3.20.15 → v3.20.16.
- `update_state.py`.

## Rollback
Restore edited skills from `.agent/archive/*.bak`; `git mv` the template back; `rm -rf` the new skill dir. No data migration.
