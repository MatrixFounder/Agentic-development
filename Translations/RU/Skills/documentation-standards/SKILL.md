---
name: documentation-standards
description: Стандарты для документации кода, комментариев и обновления артефактов.
version: 1.2
---
# Стандарты Документации (Documentation Standards)

## 1. Docstrings & JSDoc
Все классы и функции должны иметь документацию.

### Python (Google Style)
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

## 2. Комментарии
- **Почему (Why) против Что (What):** Объясняйте *причину* логики, а не синтаксис.
- **TODOs:** Используйте `# TODO:` (Python) или `// TODO:` (JS/TS) для заглушек.

## 3. Артефакты (`.AGENTS.md`)
**ОБЯЗАТЕЛЬНО:** Каждая директория должна иметь этот файл.

### Шаблон
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
