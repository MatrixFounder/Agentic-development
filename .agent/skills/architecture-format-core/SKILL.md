---
name: architecture-format-core
description: Core structure for Architecture documents. For full templates with examples, load architecture-format-extended.
version: 1.1
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

## Living Document & Index-Mode

> [!IMPORTANT]
> `docs/ARCHITECTURE.md` is a **single LIVING document**. It is updated **in place**
> across tasks and is **NEVER** archived or rotated per-task. There is no
> `docs/architectures/architecture-NNN-*.md`, nothing is moved into `docs/archives/`,
> and `skill-archive-task` does **not** touch it. The only structural operation
> permitted is the size-driven Index-Mode split below.

### Size Threshold

After writing/updating `docs/ARCHITECTURE.md`, check its size:

```bash
wc -l docs/ARCHITECTURE.md      # read-only, SAFE TO AUTO-RUN
```

- **≤ 1500 lines** → keep as a single file. Done.
- **> 1500 lines** → perform the **Index-Mode split** below.

### Index-Mode Split Procedure

1. `mkdir -p docs/architectures` (idempotent, SAFE TO AUTO-RUN).
2. Enumerate top-level (`## N. Title`) sections.
3. **Extract large sections.** Rule of thumb: any section larger than ~150 lines is a
   candidate; extract enough sections to bring the rewritten index under ~200 lines.
   Small sections (e.g. Task Description, Open Questions) MAY stay inline in the index.
4. For each extracted section, write its full content to
   `docs/architectures/<section-slug>.md`, where `<section-slug>` is the kebab-case of
   the section title **with no numeric prefix** (e.g. `## 7. Security` →
   `docs/architectures/security.md`).
   - Numeric prefixes are forbidden — they imply per-task versioning, the exact drift
     this protocol removes. Section-slug names stay stable as content evolves.
   - Each chunk file opens with an H1 = the section title and a one-line back-link:
     `> Part of [docs/ARCHITECTURE.md](../ARCHITECTURE.md).`
5. **Rewrite `docs/ARCHITECTURE.md` as an INDEX** (~under 200 lines) containing only:
   - The H1 title.
   - A banner: `> This is a living INDEX. Section bodies live in docs/architectures/.`
   - A Table of Contents.
   - Per extracted section: its heading + a **one-line summary** + a relative link,
     e.g. `→ [details](architectures/security.md)`.
   - Any small sections kept inline.

### After the Split

Once in Index-Mode:
- Edit the relevant `docs/architectures/<slug>.md` chunk; keep the index's one-line
  summary in sync.
- A new top-level section becomes a new chunk file + a new index entry.
- If a section is renamed, update **both** the chunk filename and the index link in the
  same edit (avoids broken links).
- Re-check the index against the ~200-line target after large edits.

---

## Loading Conditions

| Condition | Load |
|-----------|------|
| Updating existing architecture (minor change) | `core` only |
| Adding new component to existing system | `core` only |
| ARCHITECTURE.md exceeds 1500 lines (Index-Mode split) | `core` only |
| Creating NEW system from scratch | `extended` |
| Major refactor (>3 components changed) | `extended` |
| Sophisticated requirement / complex task | `extended` |
| User explicitly requests full template | `extended` |
