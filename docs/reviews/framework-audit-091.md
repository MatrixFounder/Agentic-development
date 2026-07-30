# Framework Audit: two-level work-item ledger for `run-feedback` (TASK 091)

**Date:** 2026-07-29
**Auditor:** Self-Improvement Verificator (Mode A + Mode B, single pass — TASK and PLAN authored together)
**Target:** `docs/TASK.md` **and** `docs/PLAN.md`
**Status:** **APPROVED**

## 0. Emergency Bypass
- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

**Justification:** none — no flag set. `artifact-management` (TIER 0) is edited **additively**
(one bullet + one description clause); no TIER 0 rule is removed, so tier protection is respected
rather than bypassed.

## 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | TASK ID `091`, slug `run-feedback-two-level-backlog`, allocated via `task_id_tool.py`. `docs/tasks/task-091-*` free; nothing to archive (no prior `TASK.md`/`PLAN.md` on disk). |
| **Tier Protection** | ✅ Pass | Touches TIER 0 `artifact-management` only to ADD `BACKLOG.md` as a living artifact with format delegated to `known-issues-format` — same shape as the existing `KNOWN_ISSUES.md` bullet. `core-principles`, `skill-safe-commands`, `skill-session-state` untouched. |
| **Skill Compatibility** | ✅ Pass | No new agent or prompt is introduced, so no new TIER 0 load list to declare. `known-issues-format` keeps its **name** — verified that `Universal-skills/.agent/skills/known-issues-format` and `run-feedback` are symlinks into this repo; a rename would have broken them, and the plan states that constraint explicitly. |
| **Documentation** | ✅ Pass | Step 9 covers `System/Docs/QUALITY_FEEDBACK_LOOP.md` (the subsystem's architecture doc), `System/Docs/SKILLS.md`, `artifact-management`, and `CLAUDE.md`, and includes a grep sweep for now-false claims. `docs/ARCHITECTURE.md` deliberately untouched: it documents agents/workflows and never mentioned the feedback ledgers. |
| **Migration** | ✅ Pass | `config.v` stays `1`; the three new keys are additive with defaults chosen so an existing `{backlog_path, backlog_anchor}` config lands on the layout the project already uses by hand (R8, verified against `onchain-analytics` and this repo). No session-state migration applies. |
| **Verification Step** | ✅ Pass | Step 12 names four executable gates (unittest discover, `test_e2e.sh`, `check_contract_sync.py`, `validate_skills.py`), plus Step 7's scratch-repo E2E. |
| **Rollback Plan** | ✅ Pass | Clean tree at HEAD `4281c96`; per-path `git checkout --` or task-wide `git reset --hard`. The template's `cp X X.bak` suggestion is deliberately declined — an untracked `.bak` beside a git checkout is litter, and the plan says so instead of silently skipping the check. |
| **Atomicity** | ✅ Pass | 12 steps, each with its own verify line; contract (1–2) → stub (3) → tests RED (4) → config (5) → Green (6) → E2E (7) → docs (8–9) → dogfood (10) → downstream (11) → gates (12). |
| **Test Coverage** | ✅ Pass | Step 4 precedes Step 6 (Stub-First honored: tests RED before the CLI is wired) and enumerates one case per acceptance criterion R1–R6, plus R8's old-config compatibility case. |

## 2. Risk Analysis

- **Risk 1 — behavior change lands in 3 repos at once (symlinked skills).** `Universal-skills` and
  `onchain-analytics` consume both skills by symlink, so this edit is live for them the moment it is
  saved, with no merge step to review it. *Mitigation:* the new default matches the layout those
  repos already maintain by hand (`docs/backlog/` + anchor), so the change makes the script agree
  with their convention instead of imposing a new one; the legacy flat path survives behind
  `backlog_layout: "flat"`.
- **Risk 2 — a repo with a genuinely flat backlog silently starts getting record files.** Only
  reachable where `backlog_path` is set and no `docs/backlog/` exists. *Mitigation:* Step 6's
  `doctor` output names the active layout and the record dir, and Step 10 migrates this repo's own
  flat backlog so the framework does not ship a contract it violates.
- **Risk 3 — new write surface (`backlog_dir`) could escape the repo.** Slugs come from
  `ids.normalize_slug` (ASCII, `[a-z0-9-]` only, no dots or slashes survive), and the dir is
  `repo_root / backlog_dir`. *Mitigation:* Step 12 includes an explicit security pass on path
  handling; the invariant to assert is that a hostile `--slug` cannot produce a path outside
  `backlog_dir`.
- **Risk 4 — the two format contracts drift again** (this is the failure mode WI-23 itself
  describes). *Mitigation:* the decision NOT to create a second format skill, plus
  `check_contract_sync.py` rewritten to gate both templates against the one authority — drift
  becomes an exit-1, not a review-time hope.
- **Risk 5 — closing WI-23 from the wrong evidence.** The downstream ledger's own rule is that
  sending a fix is not closing a record. *Mitigation:* Step 11 requires reading `git diff` in this
  repo before writing the resolution, and naming which of WI-23's three options actually landed.

## 3. Verdict & Actions

**APPROVED** — no blocking finding.

**Required actions carried into execution:**
1. Keep the skill **directory name** `known-issues-format` (symlink integrity) while its scope
   widens — reflect the widening in `description:`, not in the path.
2. Assert the anchor **before** writing the record file, so the exit-4 path leaves zero writes
   (R3) — audited as the single most likely half-state bug in this change.
3. Do not grant work-items `auto_fixable`: `/heal-issues` selects on it and must stay
   defect-only.
4. Report Step 11 from `git diff`, never from this plan's intent.
