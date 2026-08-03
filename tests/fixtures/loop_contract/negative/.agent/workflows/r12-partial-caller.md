---
description: fixture — the F10 shape, binding across a fragment delegation
contract:
  version: 1
  loops: []
  calls:
    - workflow: r12-partial-callee
      kind: invoke
      partial: "Step 3"
      binds:
        far-loop:
          max: 3
---
1. Step.
