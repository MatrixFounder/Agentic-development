---
name: architecture-format-core
description: Core structure for Architecture documents. For full templates with examples, load architecture-format-extended.
version: 1.0
tier: 1
---

# Architecture Document Structure (Core)

> [!NOTE]
> This is the **CORE** template for architecture documents.
> For full examples with JSON samples, diagrams, and detailed sections, load `architecture-format-extended`.

Your architecture must contain the following sections:

---

## 1. Task Description

Link to TASK and brief summary of requirements.

---

## 2. Functional Architecture

Description of the system in terms of functions it performs.

### 2.1. Functional Components

For each functional component describe:

**Component Name:** [Example, "User Management"]

**Purpose:** [Why this component is needed]

**Functions:**
- Function 1: [Description]
  - Input: [what accepts]
  - Output: [what returns]
  - Related Use Cases: [UC-01, UC-03]

**Dependencies:**
- Depends on which other components
- Which components depend on it

### 2.2. Functional Components Diagram

```
[Mermaid diagram showing connections between components]
```

---

## 3. System Architecture

Description of the system in terms of physical/logical components.

### 3.1. Architectural Style

Which architectural pattern is used:
- Monolith
- Microservices
- Layered Architecture
- Event-driven
- Etc.

**Justification:**
[Why this style was chosen]

### 3.2. System Components

For each system component describe:

**Component Name:** [Example, "User Service"]

**Type:** [Backend service / Frontend / Database / Message Queue / etc.]

**Purpose:** [Why needed]

**Implemented Functions:** [Links to functions from functional architecture]

**Technologies:** [Programming language, frameworks]

**Interfaces:**
- Inbound: [Who and how accesses this component]
- Outbound: [Who and how this component accesses]

**Dependencies:**
- External libraries
- Other system components
- External services

### 3.3. Components Diagram

```
[Mermaid diagram showing components and their interaction]
```

---

## 4. Data Model (Conceptual)

Description of data structure in the system at a high level.

### 4.1. Entities Overview

**Entities:**

#### Entity: [Name, e.g., "User"]

**Description:** [What this entity represents]

**Key Attributes:**
- `id` (UUID) — unique identifier
- [Other key attributes]

**Relationships:**
- [Entity relationships, e.g., One User has many Sessions (1:N)]

**Business Rules:**
- [Key business rules for this entity]

> [!TIP]
> For detailed logical data model with table schemas, indexes, and NoSQL examples, load `architecture-format-extended`.

---

## 5-10. Extended Sections

> [!IMPORTANT]
> The following sections are available in `architecture-format-extended`:
> - **5. Interfaces** — External APIs, Internal Interfaces, Integrations
> - **6. Technology Stack** — Backend, Frontend, Database, Infrastructure
> - **7. Security** — Authentication, Authorization, Data Protection, OWASP
> - **8. Scalability and Performance** — Scaling, Caching, DB Optimization
> - **9. Reliability and Fault Tolerance** — Error Handling, Backup, Monitoring
> - **10. Deployment** — Environments, CI/CD, Configuration
>
> Load `architecture-format-extended` when:
> - Creating a NEW system from scratch
> - Major architectural refactor (>3 components affected)
> - Sophisticated or complex requirements
> - User explicitly requests full template

---

## 11. Open Questions

List of questions requiring clarification from user.

- Question 1: [...]
- Question 2: [...]

---

## Loading Conditions

| Condition | Load |
|-----------|------|
| Updating existing architecture (minor change) | `core` only |
| Adding new component to existing system | `core` only |
| Creating NEW system from scratch | `extended` |
| Major refactor (>3 components changed) | `extended` |
| Sophisticated requirement / complex task | `extended` |
| User explicitly requests full template | `extended` |
