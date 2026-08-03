---
description: fixture — cycle half A
contract:
  version: 1
  loops:
    - id: recursive-no-edge
      what: declares recursion without the self-edge R5 keys on
      site: "<!-- loop:recursive-no-edge -->"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
      recursive: true
  calls:
    - workflow: r5-cycle-b
      kind: invoke
---
1. Step.
   <!-- loop:recursive-no-edge -->
   - Retry — max 2 attempts.
