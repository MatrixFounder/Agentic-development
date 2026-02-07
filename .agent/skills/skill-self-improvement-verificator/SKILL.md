---
name: skill-self-improvement-verificator
description: Meta-skill for verifying Framework Upgrades (Gemini Self-Improvement).
---

# Skill: Self-Improvement Verificator

> [!IMPORTANT]
> **TIER 3 (Meta-Skill)**: Use ONLY when creating or modifying `System/Agents`, `System/Docs`, or `GEMINI.md`.

## 1. Purpose
This skill acts as a **Guardian** for the Framework itself. Before any changes are applied to the "Brain" of the IDE (Prompts, Skills, Docs), this skill verifies that the proposed changes are safe, consistent, and do not break the "Constitutional" rules (Tier 0 skills).

## 2. Modes
This skill operates in two distinct modes depending on the current Stage.

### Mode A: SPECIFICATION AUDIT (Analysis Phase)
**Trigger**: When `docs/TASK.md` proposes a Framework Upgrade.
**Action**: Verify the Specification.

**Checklist**:
1. [ ] **Root Integrity**: Does the update respect `skill-core-principles` (Stub-First, Atomicity)?
2. [ ] **Skill Compatibility**: Do new Agents/Prompts explicitly load `TIER 0` skills?
3. [ ] **Documentation**: Does the task include updating `System/Docs/` to reflect changes?
4. [ ] **Migration**: Does the task describe how to migrate existing sessions (if applicable)?

### Mode B: PLAN AUDIT (Planning Phase)
**Trigger**: When `docs/PLAN.md` details the implementation steps.
**Action**: Verify the Execution Plan.

**Checklist**:
1. [ ] **Verification Step**: Is there an explicit step to run `pytest` or `validation_scripts`?
2. [ ] **Rollback**: Is there a backup step (e.g., `cp GEMINI.md GEMINI.bak`)?
3. [ ] **Atomic Updates**: Are changes broken down into safe, verifiable chunks?
4. [ ] **Test Coverage**: Does the plan include adding/updating tests for new framework features?

## 3. Usage (Workflow Integration)
This skill is primarily called by the **`/framework-upgrade`** workflow.

```markdown
# Example Usage in Workflow
- Validator: `spec-validator` (Standard)
- **Meta-Validator**: `skill-self-improvement-verificator` (Framework Safety)
```

## 4. Failure Conditions (Blocking)
If ANY of the following are found, **STOP** and return a `CRITICAL` failure:
- Removing `skill-core-principles` or `skill-safe-commands` from any Agent.
- Modifying `GEMINI.md` without a corresponding update to `System/Docs`.
- Creating a new Workflow without defining its Trigger in `GEMINI.md`.

## 5. Output
The output of this skill is a **Critique Artifact**:
- `docs/reviews/framework-audit-[ID].md`

### Resources
- **Template**: [`assets/audit_template.md`](assets/audit_template.md)
- **examples**: [`examples/audit_examples.md`](examples/audit_examples.md) (See Good/Bad patterns)

## 6. Emergency Bypass Protocols
In rare cases (e.g., hotfixes, core refactoring), checks may be bypassed.
**REQUIREMENT**: ANY bypass must be explicitly justified in the Audit Artifact.

| Flag | Effect | Use Case |
| :--- | :--- | :--- |
| `[BYPASS_TIER_PROTECTION]` | Allows modifying `TIER 0` skills (Core Principles). | Upgrading the Core Framework. |
| `[BYPASS_DOCS_CHECK]` | Skips documentation verification. | Emergency Hotfixes. |
| `[OVERRIDE_VERIFICATION]` | Force-Approves the Audit despite failures. | False positives or manual override. |
