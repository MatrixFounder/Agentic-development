---
description: fixture — a bar the body does not state
contract:
  version: 1
  loops:
    - id: unquotable-bar
      what: judgment-terminated loop whose bar is invented
      site: "<!-- loop:unquotable-bar -->"
      default_max: null
      override: allowed
      on_exhaust: escalate_user
      judgment_terminated: true
      exit_bar: "until done"
  calls: []
---
1. Roast it.
   <!-- loop:unquotable-bar -->
   - Stop when no legitimate findings remain.
