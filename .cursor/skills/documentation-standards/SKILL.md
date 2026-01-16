---
name: documentation-standards
description: Standards for code documentation, comments, and artifact updates.
version: 1.2
---
# Documentation Standards

## 1. Docstrings & JSDoc
All classes and functions must have documentation.

### 3. Path Standards (CRITICAL)
- **Relative Paths Only:** When linking to internal files in Artifacts (PLAN.md, TASK.md), ALWAYS use relative paths.
    - ✅ `[Ref](src/main.py)`
    - ✅ `[.agent/skills/core.md](.agent/skills/core.md)`
    - ❌ `file:///Users/username/project/src/main.py`
    - ❌ `/Absolute/System/Path`
- **Portability:** Absolute paths break portability. Relative paths work everywhere.


```python
def calculate(price: float, rate: float) -> float:
    """
    Calculates total price.

    Args:
        price (float): Base price.
        rate (float): Tax rate.

    Returns:
        float: Total price.
    """
    return price * (1 + rate)
```

### JavaScript / TypeScript (JSDoc)
```typescript
/**
 * Calculates total price.
 * 
 * @param {number} price - Base price.
 * @param {number} rate - Tax rate.
 * @returns {number} Total price.
 */
function calculate(price: number, rate: number): number {
    return price * (1 + rate);
}
```

## 2. Comments
- **Why vs What:** Explain the *reason* for logic, not the syntax.
- **TODOs:** Use `# TODO:` (Python) or `// TODO:` (JS/TS) for stubs.

## 3. Artifacts (`.AGENTS.md`)
**MANDATORY:** Every directory must have this file.

### Template
```markdown
# Directory: src/example/

## Purpose
Handles specific business logic.

## Files
- `service.py` / `service.ts`: Main logic.
- `models.py` / `types.ts`: Data definitions.

## Dependencies
- `src/database`: DB connection.
```
