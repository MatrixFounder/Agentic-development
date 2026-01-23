---
name: light-mode
description: Fast-track guidelines for trivial tasks (typos, UI tweaks, simple bugfixes).
tier: 2
triggers:
  - /light workflow
  - [LIGHT] tag in TASK.md
---

# Skill: Light Mode

> **Tier**: 2 (Load on specific trigger)
> **Purpose**: Provide streamlined instructions for trivial, low-risk tasks.

## Definition of "Low Risk"
A task qualifies for Light Mode if ALL of the following are true:
- [ ] No new files created (except minor config tweaks).
- [ ] No database schema changes.
- [ ] No API contract changes (endpoints, request/response formats).
- [ ] No new dependencies added.
- [ ] No modifications to files matching: `auth*`, `payment*`, `crypto*`, `security*`.
- [ ] Estimated implementation time: < 30 minutes.

If **ANY** condition is false, **ESCALATE** to standard pipeline.

---

## Instructions by Role

### For Analyst
1. Mark the TASK title with `[LIGHT]` tag.
2. Keep requirements minimal — focus on "What is broken?" and "What is the expected fix?".
3. Skip detailed acceptance criteria if the fix is obvious.

### For Developer
1. **Do not overengineer.** Fix the issue directly.
2. **Do not refactor** unrelated code.
3. **Run tests** after every change.
4. If you discover complexity (DB migration, API change), **STOP** and request workflow switch.

### For Code Reviewer
1. Focus on **correctness** and **tests**.
2. **Skip architectural nitpicks** unless they are critical bugs.
3. **Perform a basic security sanity check:**
   - No credentials or secrets in code.
   - No new dependencies without approval.
   - No changes to auth/payment/crypto files.
4. If security concerns arise, **ESCALATE** to `skill-security-audit`.

---

## Escalation Protocol
If at any point the task complexity exceeds Light Mode scope:
1. Inform the user: "This task requires standard pipeline due to [REASON]."
2. Switch workflow: Call `/01-start-feature` instead.
3. The `[LIGHT]` tag should be removed from the TASK.

---

## Safety Rules
The following files are **PROHIBITED** from Light Mode modifications:
- `**/auth/**`, `**/authentication/**`
- `**/payment/**`, `**/billing/**`
- `**/crypto/**`, `**/encryption/**`
- `**/security/**`
- `.env`, `*.pem`, `*.key`

If the task touches these files, **ALWAYS** escalate to standard pipeline with Security Audit.
