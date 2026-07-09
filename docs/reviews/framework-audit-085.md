# Framework Audit 085 — KNOWN_ISSUES thin-index restructure

**Auditor:** `skill-self-improvement-verificator` (Modes A + B)
**Subject:** Task 085 — restructure `docs/KNOWN_ISSUES.md` into a thin index + `docs/issues/*.md`
**Verdict:** ✅ PASS (both modes). Docs-only; no constitutional surface touched.

---

## Mode A — SPECIFICATION AUDIT (`docs/TASK.md`)

| # | Check | Result | Note |
|---|-------|--------|------|
| A1 | **Root Integrity** — respects `core-principles` (Atomicity, no hallucination)? | ✅ | Atomic docs restructure; opened dates taken from `git blame` (2026-04-17 / 2026-06-10), not invented. No stub-first applies (no code). |
| A2 | **Skill Compatibility** — new Agents/Prompts load TIER 0? | ✅ N/A | No agents or prompts created or modified. |
| A3 | **Documentation** — task updates `System/Docs/` to reflect changes? | ✅ N/A | No system capability, workflow, or skill changes → SKILLS.md/WORKFLOWS.md unaffected. The change *is* documentation. |
| A4 | **Migration** — describes migrating existing state? | ✅ | Old content is migrated 1:1 into per-issue files (NFR-1 no-loss); index path unchanged so no reference migration needed (R7). |

**Failure conditions (§4) — none triggered:** no TIER-0 skill removed; no bootstrap file
(`CLAUDE/AGENTS/GEMINI.md`) modified; no new workflow created (so no trigger-registration
obligation). **No bypass flags used.**

## Mode B — PLAN AUDIT (`docs/PLAN.md`)

| # | Check | Result | Note |
|---|-------|--------|------|
| B1 | **Verification Step** — explicit validation? | ✅ | Step 3 runs link-integrity + frontmatter + file-count + path checks. No pytest applies (no code); the grep suite is the docs-equivalent gate. |
| B2 | **Rollback** — backup step present? | ✅ | Step 0 backs up `docs/KNOWN_ISSUES.md` → `.agent/archive/`; explicit one-line restore documented. |
| B3 | **Atomic Updates** — safe, verifiable chunks? | ✅ | Per-file creation (Step 1) then in-place index overwrite (Step 2), each independently checkable; backup precedes any mutation. |
| B4 | **Test Coverage** — tests for new features? | ✅ N/A | No new framework feature/behavior; content-preservation is verified by the Step 3 manual clause-diff instead of automated tests. |

---

## Residual notes (non-blocking)
- **Hand-maintained index.** This repo has no `wiki-index-render` equivalent, so the index
  will drift if an issue file is added without editing the ledger. Mitigation: the Rules
  section documents the add-procedure so the coupling is explicit and agent-followable.
- **Version bump.** Pure docs restructure — no `CHANGELOG`/version bump is forced; left to
  operator discretion (flagged in the completion summary).

---

## Addendum — post-restructure drift audit + follow-up fixes (same task)

A repo-wide audit classified **26 live/coupled references** to `docs/KNOWN_ISSUES.md` after the
restructure. **Verdict: nothing broken** — the file path is unchanged, so every read-by-path /
link-by-path reference still resolves; no reference cited a removed section name (`Wave-1/2` /
`Native Teams`). Adversarial verification reduced 10 candidates → **6 real** (2 Should, 4 Optional).

**Operator elected to apply the 2 `Should` fixes only** (Optional items left as documented drift-hardening):

| File | Change | Rationale |
|------|--------|-----------|
| `.agent/skills/skill-reverse-engineering/SKILL.md` §2 (v1.1 → **1.2**) | Added "Filing format (thin index)" guidance: create `docs/issues/<slug>.md` + one index line per the *Rules / Conventions* recipe; do **not** append flat `- [ ]`; add a new prefix→category row for RE findings. | The one **live automation write-path** that populates KNOWN_ISSUES; predated the per-file format. |
| `docs/ROADMAP.md` (Wave-4 blocking gotchas) | Deep-linked the 4 gotcha bullets to `issues/at-6..at-9.md` (summary text kept); intro reworded to "AT-6..AT-9". | Live content-duplicate; `AT-6` is `open` (SEV-2) → resolution would leave the copy stale. |

**Deferred (Optional, documented, not edited):** `references/claude-code.md:57-62` (append ID tags, do not
convert to links), `references/_stub-template.md:26` (wording), `README.md:578` + `README.ru.md:578`
(RE starter-prompt alignment). No historical records (docs/tasks · plans · reviews · CHANGELOG · archive) touched.

**Backups:** `.agent/archive/skill-reverse-engineering.SKILL.md.bak`, `.agent/archive/ROADMAP.md.bak`.
**Verify:** 4 ROADMAP deep-links resolve; skill frontmatter/structure intact; no broken links introduced.
