---
name: skill-legacy-migrator
description: Use when migrating legacy Python 2 codebases to Python 3 or when encountering `ImportError` due to deprecated modules.
tier: 2
version: 1.1
---
# Legacy Code Migrator

**Purpose**: Guides the agent through the process of migrating legacy Python 2.7 codebases to modern Python 3.10+ with strict typing. It ensures business logic preservation while upgrading syntax and libraries.

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I'll just run 2to3 and commit" -> **WRONG**. Automated tools miss logic changes (e.g., unicode vs bytes).
- "I don't need to run tests first" -> **WRONG**. You have no baseline.
- "I'll add types later" -> **WRONG**. Add types *during* migration to catch bugs immediately.

## 2. Capabilities
- Audit legacy dependencies.
- Generate type stubs for untyped modules.
- Convert syntax safely using modern patterns.

## 3. Instructions

### Phase 1: Audit
1.  **Run Audit**: Execute `python3 scripts/audit_legacy.py <path>`.
2.  **Verify Report**: Check `defaults/audit_report.md`.
    - *Tip*: If the report contains "CRITICAL" warnings, ask User for guidance before proceeding.

### Phase 2: Refactoring
1.  **Strict Typing**: Add `typing` hints to every function signature you touch.
2.  **Safe Conversion**: Use `six` library only if supporting both versions is required. Otherwise, use native Python 3.

## 4. Best Practices & Anti-Patterns

| DO THIS | DO NOT DO THIS |
| :--- | :--- |
| **Audit First**: Know what you are breaking. | **Blind Rewrite**: Changing code without understanding dependencies. |
| **Incremental**: Migrate one module at a time. | **Big Bang**: Migrating the entire repo in one go. |

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "It's just a print statement" | Python 3 print is a function. Parentheses matter. |
| "I know the code works" | Logic changes in `map`/`filter` (iterators vs lists) cause silent bugs. |
| "Types slow me down" | Types catch `bytes` vs `str` errors that will crash production. |

## 5. Examples (Few-Shot)

**Input:**
```python
# Legacy Code
def process_data(data):
    print "Processing", data
    return map(lambda x: x*2, data)
```

**Output:**
```python
# Migrated Code
from typing import List, Iterable

def process_data(data: List[int]) -> Iterable[int]:
    print(f"Processing {data}")
    # Note: map returns iterator in Py3, cast to list if needed, or document return type as Iterable
    return map(lambda x: x*2, data)
```

## 6. Resources
- `resources/type_mapping.json`: Maps legacy types to `typing` equivalents.
