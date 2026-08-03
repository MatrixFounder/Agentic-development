---
description: fixture — frontmatter says 3, prose says 2
contract:
  version: 1
  loops:
    - id: drifted-loop
      what: reviewer rejects -> retry
      site: "<!-- loop:drifted-loop -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---
1. Do the thing.
   <!-- loop:drifted-loop -->
   - On rejection, retry — **Max 2 attempts**, then STOP.
