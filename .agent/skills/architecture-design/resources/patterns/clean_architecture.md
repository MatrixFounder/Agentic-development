# Clean Architecture

## Core Philosophy
The center of your application is **Logic**, not Database or UI.

## The Dependency Rule
**Source code dependencies must point only inward, toward higher-level policies.**
- Nothing in an inner circle can know anything at all about something in an outer circle.

## Layers (Inner to Outer)

### 1. Entities (Enterprise Business Rules)
- Encapsulate Enterprise-wide business rules.
- Least likely to change when something external changes.
- **Example:** `User` class with method `isPasswordValid()`.

### 2. Use Cases (Application Business Rules)
- Orchestrate the flow of data to and from the entities.
- **Example:** `RegisterUserUseCase`.

### 3. Interface Adapters (Controllers, Gateways, Presenters)
- Convert data from the format most convenient for the use cases and entities, to the format most convenient for some external agency like the Database or the Web.
- **Example:** `UserRepository` (implementation), `UserController`.

### 4. Frameworks & Drivers (Web, DB, Devices)
- The outermost layer. Generally composed of frameworks and tools like the Database, the Web Framework, etc.
- **Example:** `FastAPI`, `PostgreSQL`, `React`.

## Implementation Guide
1.  Define **Entities** first.
2.  Define **Use Cases** that manipulate Entities.
3.  Define **Repository Interfaces** in the Use Case layer.
4.  Implement **Repository** in the Interface Adapters layer.
5.  Wire everything up in `main` (Dependency Injection).
