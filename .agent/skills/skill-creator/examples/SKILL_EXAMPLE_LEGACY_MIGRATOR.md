---
name: skill-legacy-migrator
description: Guidelines for migrating legacy Python 2 code to Python 3 with type hints.
tier: 2
version: 1.0
---
# Legacy Code Migrator

## Purpose
This skill guides the agent through the process of migrating legacy Python 2.7 codebases to modern Python 3.10+ with strict typing. It ensures preserving business logic while upgrading syntax and libraries.

## 1. Process Overview
1.  **Audit**: Analyze dependencies and syntax using `scripts/audit_legacy.py`.
2.  **Stubbing**: Create type stubs for untyped modules.
3.  **Conversion**: Apply 2to3 fixes and manual refactoring.
4.  **Verification**: detailed testing.

## 2. Detailed Instructions

### Phase 1: Audit
- Run `python3 .agent/skills/skill-legacy-migrator/scripts/audit_legacy.py <path>`.
- **CRITICAL**: Do not start editing until the audit report is generated in `defaults/audit_report.md`.

### Phase 2: Refactoring
- Use the `six` library for cross-version compatibility if immediate switch is impossible.
- **MUST** add python type hints to every function signature.

## 3. Examples

**Bad Refactor:**
```python
# Just printing
print "Hello"
```

**Good Refactor:**
```python
# Modern print with typing
def greet(name: str) -> None:
    print(f"Hello, {name}")
```

## 4. Resources
- `resources/type_mapping.json`: Maps legacy types to `typing` equivalents.
