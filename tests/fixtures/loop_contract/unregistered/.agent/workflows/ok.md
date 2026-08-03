---
description: fixture — valid, but the anchor is unregistered in this root
contract:
  version: 1
  loops:
    - id: fine-loop
      what: reviewer rejects -> retry
      site: "<!-- loop:fine-loop -->"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---
1. Step.
   <!-- loop:fine-loop -->
   - Retry — max 2 attempts.
