---
description: fixture — three ways site and bound fail to resolve
contract:
  version: 1
  loops:
    - id: no-bound
      what: loop whose window holds no canonical form
      site: "<!-- loop:no-bound -->"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
      window: 2
    - id: two-bounds
      what: loop whose window holds disagreeing bounds
      site: "<!-- loop:two-bounds -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
    - id: prose-site
      what: loop addressed by prose, which is not a locator
      site: "step 4c"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---
1. First.
   <!-- loop:no-bound -->
   - Retry a few times, then give up.
2. Second.
   <!-- loop:two-bounds -->
   - Retry — max 3 attempts here and max 2 attempts there.
3. Third has a prose site.
