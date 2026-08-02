# Development Plan: [Project Name]

<!--
  Anchors below (`<!-- contract:* -->`) are how a MACHINE addresses a section:
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
  Keep them; translate the headings freely. Never invent an unregistered one.
-->

<!-- contract:sequence -->

## Task Execution Sequence

### Stage 1: Structure Creation and Stubs
- **Task {ID}.1** — [Brief description]
  - Use Cases: UC-01, UC-02
  - Description File: `docs/tasks/task-{ID}-01-{task-slug}.md`
  - Priority: Critical
  - Dependencies: none

- **Task {ID}.2** — [Brief description]
  - Use Cases: UC-01
  - Description File: `docs/tasks/task-{ID}-02-core-logic.md`
  - Priority: High
  - Dependencies: Task 1.1

### Stage 2: Core Functionality Implementation
[...]

### Stage 3: Testing
[...]

### Stage 4: Deployment
[...]

<!-- contract:coverage -->

## Use Case Coverage

| Use Case | Tasks |
|-----------|--------|
| UC-01 | 1.1, 1.2, 2.1, 3.1 |
| UC-02 | 1.1, 2.3, 3.2 |
[...]
