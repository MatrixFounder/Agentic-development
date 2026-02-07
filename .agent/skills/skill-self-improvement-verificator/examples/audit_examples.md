# Audit Examples

## ✅ Good Audit (Approved)

**Context:** The user wants to add a new skill `skill-magic-wand`.
**Artifact:** `docs/TASK.md`

### Critique Output

# Framework Audit: Magic Wand Skill

**Date:** 2026-02-07
**Auditor:** Self-Improvement Verificator
**Target:** `docs/TASK.md`
**Status:** **APPROVED**

## 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | Task ID `042` present. |
| **Tier Protection** | ✅ Pass | No core skills deleted. |
| **Documentation** | ✅ Pass | Includes update to `SKILLS.md`. |
| **Atomicity** | ✅ Pass | Broken down into Init -> Implement -> Test steps. |
| **Rollback Plan** | ✅ Pass | Backup of `.agent/skills` specified. |

## 2. Risk Analysis
- **Risk 1:** New skill might overlap with `brainstorming`. *Mitigation: Explicit "Use When" clause added.*

## 3. Verdict
**APPROVED**. Proceed to Planning.

---

## ❌ Bad Audit (Blocked)

**Context:** The user wants to "Rewrite the Orchestrator to be faster".
**Artifact:** `docs/PLAN.md`

### Critique Output

# Framework Audit: Orchestrator Rewrite

**Date:** 2026-02-07
**Auditor:** Self-Improvement Verificator
**Target:** `docs/PLAN.md`
**Status:** **BLOCKED**

## 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | ID present. |
| **Tier Protection** | ❌ Fail | **CRITICAL:** Plan removes `skill-core-principles` from TIER 0 loading list! |
| **Documentation** | ❌ Fail | No updates to `ORCHESTRATOR.md` planned. |
| **Atomicity** | ❌ Fail | Single step "Rewrite prompt" is too large. |
| **Rollback Plan** | ❌ Fail | No backup of `01_orchestrator.md` mentioned. |

## 2. Risk Analysis
- **Risk 1:** Removing `skill-core-principles` will cause massive hallucinations.
- **Risk 2:** Lack of documentation will de-sync the team.

## 3. Verdict
**BLOCKED**.

**Required Actions:**
1. **Restore TIER 0**: Do not touch `core-principles`.
2. **Add Documentation**: Include `System/Docs` updates.
3. **Backup**: Add `cp 01_orchestrator.md .agent/archive/` step.

---

## ⚠️ Bypass Audit (Emergency)

**Context:** Hotfix for a critical bug in `skill-core-principles`.
**Artifact:** `docs/PLAN.md`

### Critique Output

# Framework Audit: Core Principles Hotfix

**Date:** 2026-02-07
**Auditor:** Self-Improvement Verificator
**Target:** `docs/PLAN.md`
**Status:** **APPROVED (WITH OVERRIDE)**

## 0. Emergency Bypass
- [x] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

**Justification:**
> Critical bug in core principles is blocking all agents. Must patch immediately. Refactoring constitutes a modification of Tier 0.

## 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | ID present. |
| **Tier Protection** | ⚠️ **BYPASS** | Modifying `skill-core-principles`. |
| ... | ... | ... |
