---
description: fixture — states no cap, the caller must supply one
contract:
  version: 1
  loops:
    - id: caller-bound-loop
      what: the callee declares the loop, the caller declares its bound
      site: "<!-- loop:caller-bound-loop -->"
      default_max: null
      override: required
      on_exhaust: escalate_user
  calls: []
---
1. Step.
   <!-- loop:caller-bound-loop -->
   - Retry until the caller's cap is reached.
