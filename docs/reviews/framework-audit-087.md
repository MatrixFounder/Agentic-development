# Framework Audit — Task 087 (dedicated `known-issues-format` skill)

Meta-validator: `skill-self-improvement-verificator`. Scope: new tier-2 format skill + refactor of
`artifact-management` (TIER 0) and `skill-reverse-engineering`. No code, no installer, no bootstrap.

## Mode A — SPECIFICATION AUDIT (Analysis → Planning)

| # | Check | Verdict |
|---|-------|---------|
| 1 | **Root Integrity** — `core-principles` (atomicity, no hallucination). | ✅ Atomic; the inconsistency and the fix are grounded in the verified artifact pattern (planning-format/documentation-standards own templates; hub delegates ARCHITECTURE format). |
| 2 | **Skill Compatibility** — new skill loads TIER 0 correctly. | ✅ New skill is a leaf format reference (tier 2); it is *referenced by* TIER-0 `artifact-management`, not the reverse. No TIER-0 dependency inversion. |
| 3 | **Documentation** — updates `System/Docs`. | ✅ PLAN Step 7 adds the SKILLS.md row + reverts the hub row + CHANGELOG/README. |
| 4 | **Migration** — existing projects/sessions. | ✅ Template body unchanged (`git mv` only); create-if-absent repointed; repo's own ledger untouched. |

**Failure conditions:** none (no core-skill removal; no bootstrap edit without docs; SKILL CREATION GATE honored via `init_skill.py`). **Mode A: PASS.**

## Mode B — PLAN AUDIT (Planning → Execution)

| # | Check | Verdict |
|---|-------|---------|
| 1 | **Verification Step** — explicit validation. | ✅ Step 6: `validate_skills` 44/44, template↔live schema, orphan-asset check, reference resolution. |
| 2 | **Rollback** — backup step. | ✅ Step 0 backs up both edited skills + registry/release set; new skill dir is `rm -rf`-reversible; template move is `git mv`-reversible. |
| 3 | **Atomic Updates** — safe chunks. | ✅ Scaffold → author → move → slim hub → repoint: each independently verifiable. |
| 4 | **Test Coverage** — tests for new behavior. | ✅ No executable code added (skill prose + a moved template); the structural gate is `validate_skills.py` (44/44). Rationale-documented, same as Task 086. |

**Mode B: PASS.** No bypass flags.

## Design record
- KNOWN_ISSUES = living, non-planning artifact → its own format skill, mirroring `architecture-format-core`
  (ARCHITECTURE is the precedent, not planning-format). The hub keeps lifecycle + create-if-absent and
  **delegates** format — restoring the "hub delegates, format skills own templates" invariant that Task 086
  had broken by putting the first-ever asset into the hub.
