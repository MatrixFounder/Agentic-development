# Development Plan: [Project Name]

<!--
  The `contract:*` anchors below are how a MACHINE addresses a section. They are
  HTML comments; this one does not spell their closing delimiter, because a
  comment ends at the FIRST one and the rest of the block would render as text.
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
  Keep them; translate the headings freely. Never invent an unregistered one.
-->

<!--
  REGISTER. Write in whichever language the project uses; nothing in this pipeline changes that
  choice. In that language, apply the authoring contract BEFORE the first sentence:
  `.agent/skills/artifact-formalizer/references/authoring-contract.md` — six per-sentence tests and
  the licensed statement forms. It is the single source for them, so this template does not restate
  the rules. Audit with `artifact-formalizer/scripts/scan_register.py`.
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
