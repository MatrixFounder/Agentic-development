---
description: fixture — the site resolves, the window does not
contract:
  version: 1
  loops:
    - id: bad-window
      what: a correctly placed marker under an invalid window
      site: "<!-- loop:bad-window -->"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
      window: 0
    - id: wrong-name
      what: site names a marker that is not this loop's id
      site: "<!-- loop:some-other-loop -->"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---
1. Step.
   <!-- loop:bad-window -->
   - Retry — max 2 attempts.
