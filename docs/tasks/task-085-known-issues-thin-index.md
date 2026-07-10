# Technical Specification: Restructure `docs/KNOWN_ISSUES.md` into a thin index + per-issue files

### 0. Meta Information
- **Task ID:** 085
- **Slug:** `known-issues-thin-index`
- **Mode:** Framework Upgrade (docs-only; no code, no skills, no prompt/workflow changes)
- **Type:** Documentation restructure / maintainability.
- **Workflow:** `/framework-upgrade` (verificator Modes A + B).
- **Operator request (verbatim):** "Переведи файл `docs/KNOWN_ISSUES.md` как в проекте
  `/Users/sergey/dev-projects/obsidian-llm-wiki/docs/KNOWN_ISSUES.md` (тонкий индекс с
  правилами и все issues в отдельных файлах в подпапке `issues`)."

### 1. Problem Description
Today `docs/KNOWN_ISSUES.md` is a single 22-line flat file holding 10 known-issue entries
as `- [ ]` checkboxes under two prose sections. This does not scale, has no per-issue
identity (no IDs, no status/severity/date frontmatter), and cannot be linked to, filtered,
or cited individually.

The operator wants it restructured to mirror the `obsidian-llm-wiki` layout:
1. **A thin index** at `docs/KNOWN_ISSUES.md` — a short ledger grouping issues by category,
   one line per issue (ID · title link · severity · status · opened date).
2. **Per-issue files** under `docs/issues/<slug>.md`, each with YAML frontmatter
   (`id`, `type: known-issue`, `status`, `opened_at`, `category`, optional `severity`, `slug`)
   and the issue body preserved verbatim (**no content loss** — NFR-1).
3. **Rules section** ("правила") at the top of the thin index documenting the ID scheme,
   category/status/severity vocabularies, the index line format, and the "how to add an
   issue" procedure — because this repo has **no** `wiki-index-render` tooling (unlike the
   source vault), so the index is **hand-maintained** and its conventions must be written down.

### 2. Constraints & Non-Goals
- **NFR-1 (No data loss):** every sentence of the 10 current entries survives into a
  per-issue file. The wrapper-drift entry's sub-bullet ("Scaffold wrappers are generated")
  is preserved in full.
- **Path stability:** the thin index stays at `docs/KNOWN_ISSUES.md`. The ~30 references to
  that path across the repo (README, CLAUDE/AGENTS/GEMINI, ARCHITECTURE, pipeline steps)
  must keep resolving — **do not rename or move the index file**.
- **No tooling import:** do NOT copy the wiki's Python migration/render scripts, SQLite
  index, or Obsidian dependency into this repo. This is a one-time hand restructure.
- **Link syntax:** standard Markdown links (`[title](issues/slug.md)`), NOT Obsidian
  `[[wikilinks]]` — this repo is not an Obsidian vault; links must be clickable in
  GitHub/VSCode. (Operator decision, 2026-07-10.)
- **No behavior/logic change:** docs only. No agent, skill, workflow, or prompt edits.

### 3. Requirements Traceability Matrix (RTM)

| ID | Requirement | Source | Acceptance |
|----|-------------|--------|------------|
| R1 | Create `docs/issues/` with one file per current known issue (10 files). | Operator | `ls docs/issues/*.md` = 10 files. |
| R2 | Each per-issue file has valid frontmatter (`id`, `type`, `status`, `opened_at`, `category`, `slug`; `severity` when applicable) mirroring the wiki schema. | obsidian-llm-wiki | Frontmatter keys present & well-formed on every file. |
| R3 | Full original text of each entry preserved (no dropped sentence). | NFR-1 | Manual diff: every clause of the 10 entries appears in some issue file. |
| R4 | `docs/KNOWN_ISSUES.md` becomes a thin index: rules header + category-grouped one-line entries. | Operator | Index ≤ ~1 screen of ledger + rules; no full issue bodies inline. |
| R5 | Rules section documents ID scheme, category/status/severity vocab, line format, add-procedure. | "с правилами" | Rules section present and self-consistent with the emitted files. |
| R6 | All index links resolve to existing files; opened dates match git history. | Integrity | `grep`-based link check passes; dates = 2026-04-17 (AT-*), 2026-06-10 (WR-1). |
| R7 | Path `docs/KNOWN_ISSUES.md` unchanged; existing references unbroken. | Path stability | File still at same path; no other doc edited to chase a rename. |

### 4. ID / Category Scheme (this repo)
Two prefixes cover the current content; documented in the index rules for future issues:

| Prefix | Category   | Meaning |
|--------|------------|---------|
| `AT-N` | `agent-teams` | Native Claude Code Agent Teams (Layer B `TeamCreate`/`SendMessage`) limitations. |
| `WR-N` | `wrappers`    | Thin-wrapper ↔ SOT synchronization hazards (`.claude/agents/` etc.). |

Mapping of the 10 current entries:

| ID | Title (short) | Category | Status | Severity | Opened |
|----|---------------|----------|--------|----------|--------|
| AT-1 | No session resumption | agent-teams | documented | — | 2026-04-17 |
| AT-2 | Task status lag | agent-teams | documented | SEV-3 | 2026-04-17 |
| AT-3 | One team per session | agent-teams | documented | — | 2026-04-17 |
| AT-4 | No leadership transfer | agent-teams | documented | — | 2026-04-17 |
| AT-5 | Higher token costs | agent-teams | by-design | — | 2026-04-17 |
| AT-6 | `TeamDelete` does not clean up after protocol shutdown | agent-teams | open | SEV-2 | 2026-04-17 |
| AT-7 | Async spawn ≠ sync return | agent-teams | documented | — | 2026-04-17 |
| AT-8 | Model inheritance inconsistent across agent types | agent-teams | documented | — | 2026-04-17 |
| AT-9 | Runtime sends structured JSON despite docs | agent-teams | documented | — | 2026-04-17 |
| WR-1 | Wrapper/SOT drift risk | wrappers | documented | SEV-3 | 2026-06-10 |

### 5. Acceptance Criteria (Definition of Done)
- [ ] R1–R7 satisfied.
- [ ] `.agent/archive/KNOWN_ISSUES.md.bak` backup exists (rollback safety).
- [ ] Meta-audit (`skill-self-improvement-verificator`, Modes A+B) recorded in
      `docs/reviews/framework-audit-085.md`.
- [ ] Session state persisted at the phase boundary.
