# Framework Audit — Task 086 (KNOWN_ISSUES format framework-resident, mechanism B)

Meta-validator: `skill-self-improvement-verificator`. Scope: `artifact-management` (TIER 0) + a
template asset + a pointer redirect in `skill-reverse-engineering`. No code, no installer, no bootstrap.

## Mode A — SPECIFICATION AUDIT (gates Analysis → Planning)

| # | Check | Verdict |
|---|-------|---------|
| 1 | **Root Integrity** — respects `core-principles` (atomicity, no hallucination). | ✅ Atomic doc/skill edits; every claim grounded in verified installer behavior (cli.py:117-127 copy-if-absent, 289-294 uninstall-removes-copy). |
| 2 | **Skill Compatibility** — new agents/prompts load TIER 0. | ✅ N/A — no new agent/prompt; the change *strengthens* a TIER-0 skill. |
| 3 | **Documentation** — task updates `System/Docs`. | ✅ PLAN Step 5 syncs `SKILLS.md` + CHANGELOG + README. |
| 4 | **Migration** — existing sessions/projects handled. | ✅ Repo's own `docs/KNOWN_ISSUES.md` is unchanged; template targets NEW projects; create-if-absent never clobbers an existing file. |

**Failure conditions:** none. No `core-principles`/`skill-safe-commands` removal; no bootstrap edit without docs; no new workflow. **Mode A: PASS.**

## Mode B — PLAN AUDIT (gates Planning → Execution)

| # | Check | Verdict |
|---|-------|---------|
| 1 | **Verification Step** — explicit validation. | ✅ Step 4: template↔live-format consistency, skill structural validity, fresh-project desk-trace. No code ⇒ installer pytest unaffected (optional sanity run). |
| 2 | **Rollback** — backup step. | ✅ Step 0 backs up both skills + version-bump set to `.agent/archive/`. |
| 3 | **Atomic Updates** — safe, verifiable chunks. | ✅ Steps 1-3 independent: asset add, skill contract, pointer redirect. |
| 4 | **Test Coverage** — tests for new behavior. | ✅ Rationale-documented exception: mechanism B adds **no executable code** (a template asset + prose skill edits), so there is nothing to unit-test; verification is the format-consistency desk-check in Step 4. Mechanism A (installer `seed` action) — which *would* have required installer tests — was rejected on the uninstall-data-loss finding. |

**Mode B: PASS.** No emergency-bypass flags used.

## Key design record
- **Why mechanism B, not A:** the installer's `copy` action is deleted on uninstall (`cli.py:289-294`), so
  installer-seeding `docs/KNOWN_ISSUES.md` would erase a project's issue history on `uninstall`/`switch`. B keeps
  the file project-owned (installer never references it) → uninstall-safe by construction, and the template ships
  free with the `.agent/skills` link. Operator-selected.
