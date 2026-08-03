---
description: fixture — owns a loop outside any delegated fragment
contract:
  version: 1
  loops:
    - id: far-loop
      what: a loop a fragment delegation never reaches
      site: "<!-- loop:far-loop -->"
      default_max: 2
      override: allowed
      on_exhaust: escalate_user
  calls: []
---
1. Step.
   <!-- loop:far-loop -->
   - Retry — max 2 attempts.
