---
description: VDD-Enhanced Development
---

# Workflow: VDD-Enhanced Development

**Description:**  
Full robust mode: Standard Stub-First + adversarial refinement.

**Steps:**

1. Call /base-stub-first          # Run core pipeline first
2. After completion:
   Call /vdd-adversarial          # Add adversarial roast on top
3. Final regression tests and commit
