---
name: architecture-design
description: Guidelines for designing scalable and modular system architecture.
tier: 1
version: 1.1
---
# Architecture Design

## 1. Core Principles

### Simplicity Above All
- **Goal:** Solve the task maximally simply.
- **Avoid Overengineering:** Complex architecture and heavy libraries complicate maintenance.
- **Zero-Dependency:** Add only truly necessary components.
- **No-ORM Preference:** Do not use ORM if simple SQL queries are easier.
- **Frameworks:** Do not use frameworks if API is easier on lower-level libraries.

### Modularity
- Loose coupling, high cohesion.
- Clear interface definitions between components.

### Common Patterns
If building a complex system, refer to these standard patterns:
- **Clean Architecture:** `resources/patterns/clean_architecture.md` (Layers, Dependency Rule).
- **Event-Driven:** `resources/patterns/event_driven.md` (Async, Brokers, Idempotency).

## 2. Requirements for Architecture Components

### Data Model
1. **Design Detailedly:**
   - All entities, attributes with types.
   - All relationships (1:1, 1:N, M:N).
   - All constraints and indexes.
2. **Think about Migrations:**
   - How data will migrate with changes.
   - Backward compatibility.
3. **Consider Performance:**
   - Frequent queries -> Indexes.
   - Denormalization if necessary.

### Security
- **Built-in:** Security must be designed, not patched.
- **Auth:** OAuth2/JWT/Session strategies defined.
- **Protection:** OWASP Top 10 consideration.

### Scalability
- **Horizontal:** Stateless services.
- **Database:** Partitioning, Replication strategies.

## 3. Important Rules

### ✅ DO:
1. **Base on TASK:** Justify every decision by requirements from TASK.
2. **Consider Existing:** Structure new components to fit existing patterns.
3. **Be Specific:** Indicate specific technologies (e.g., "PostgreSQL 14"), not just "SQL DB".
4. **Link to Use Cases:** Map components to the UC they fulfill.

### ❌ DO NOT:
1. **Write Code:** You design architecture, not implementation.
2. **Ignore Legacy:** Study existing project before designing.
3. **Leave Decisions for Later:** Key technologies must be selected now.
4. **Accumulate Debt:** If refactoring is needed, record it.

## 4. Uncertainty Management
**Critical Stage:** Wrong architectural decisions are expensive.
1. **Pay attention to Open Questions.**
2. **Do not assume critical things.**
3. **If in doubt about technology:** Add to "Open Questions" for the user.
