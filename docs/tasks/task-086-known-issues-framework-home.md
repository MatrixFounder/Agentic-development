# Technical Specification: Make the KNOWN_ISSUES thin-index format framework-resident (portable to new projects)

### 0. Meta Information
- **Task ID:** 086
- **Slug:** `known-issues-framework-home`
- **Mode:** Framework Upgrade (skill + asset edits; **no code, no installer change**)
- **Type:** Portability / self-documentation. Follow-up to Task 085.
- **Workflow:** `/framework-upgrade` (verificator Modes A + B).
- **Seed mechanism:** **B — skill-driven** (operator-selected). Template asset + TIER-0 create-if-absent rule. Installer untouched.

### 1. Problem Description
Task 085 restructured `docs/KNOWN_ISSUES.md` into a thin index + per-issue files under `docs/issues/`,
and put the format **rules** in that file's *Rules / Conventions* section. But those rules live only in a
**project artifact of this repo**, which is never distributed to a new project:

- The installer deploys the framework (`.agent/`, `System/`, vendor bootstrap) but **does not seed `docs/`**
  (verified: `System/scripts/installer/bootstrap.py` has zero `docs/` references).
- **No TIER-0 skill mentions KNOWN_ISSUES** — `artifact-management` §Global Artifacts lists TASK / PLAN /
  ARCHITECTURE but not KNOWN_ISSUES.
- The Task-085 fix in `skill-reverse-engineering §2` points at *"that file's Rules/Conventions section"* — a
  **dangling pointer** in a fresh project where the file (and its Rules section) does not yet exist.

**Consequence:** an agent starting a clean project using this framework would not know the thin-index format and
would invent a flat `- [ ]` list, drifting from the canonical layout.

**Rejected mechanism (safety):** seeding via the installer's `copy` action was rejected — `_remove_install`
(`cli.py:289-294`) deletes every `copy` component on uninstall/switch, which would **destroy a project's
accumulated KNOWN_ISSUES history**. Mechanism B (skill owns the template; installer never owns the file) is
uninstall-safe by construction.

### 2. Requirements (RTM)

| ID | Requirement | Verification |
|----|-------------|--------------|
| R1 | Ship a **project-agnostic** `KNOWN_ISSUES.template.md` (rules-only, zero repo-specific issues/prefixes) as an asset of `artifact-management`. | File exists under `assets/`; contains Rules/Conventions, no `AT-`/`WR-` issues. |
| R2 | `artifact-management` (TIER 0) lists **KNOWN_ISSUES.md** as a Global Artifact + a **compact** format contract + the **create-if-absent-from-template** rule. | Skill body updated; version bumped 1.1→1.2. Kept concise (TIER-0 is always loaded). |
| R3 | `skill-reverse-engineering §2` pointer redirected to the framework skill (`artifact-management`) so it resolves in a fresh project. | §2 references `artifact-management`; version bumped 1.2→1.3. |
| R4 | The template asset auto-ships to new projects with **no installer change**. | Template lives under `.agent/skills/…/assets/` → already covered by the `.agent/skills` link component. |
| R5 | No `core-principles` / `skill-safe-commands` removal; no installer/Python/test change; docs + registry synced. | Meta-audit (Mode A/B); CHANGELOG + README + SKILLS.md updated. |

### 3. Non-Goals
- No new installer action, no `vendors.yaml` change, no Python, no installer tests (mechanism A was rejected).
- Not re-touching Task-085's already-committed per-issue files or the repo's own `docs/KNOWN_ISSUES.md`.
- Not migrating the repo's AT-/WR- categories into the generic template (they are this-repo-specific).

### 4. Acceptance Criteria
- Fresh-project trace holds: an agent loading TIER-0 skills learns the KNOWN_ISSUES format **before any file exists**,
  and is told to materialize `docs/KNOWN_ISSUES.md` from the shipped template on first issue.
- `skill-reverse-engineering §2` no longer dangles in a project without a pre-existing Rules section.
- Both skills structurally valid; template self-consistent with the repo's live `docs/KNOWN_ISSUES.md` format.
