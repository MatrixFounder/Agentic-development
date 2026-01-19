---
description: VDD Adversarial Refinement
---

# Workflow: VDD Adversarial Refinement

**Description:**  
Post-implementation adversarial cycle for zero-slop robustness.

**Steps:**

1. For each implemented module:
   a. Activate Adversary (Sarcasmotron)
      - Prompt: [Full Sarcasmotron prompt with cynicism, fresh context, hallucination termination]
      - Review all code + tests
   b. If real issues found:
      - Call /03-develop-single-task (to fix issues)
      - Repeat this workflow (recursive call if needed)
   c. Terminate when adversary hallucinations dominate
2. Announce: "VDD cycle complete: zero-slop achieved"
