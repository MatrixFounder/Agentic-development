---
description: VDD Adversarial Refinement
---

# Workflow: VDD Adversarial Refinement

**Description:**  
Post-implementation adversarial cycle for zero-slop robustness.

**Required Skills:** `vdd-adversarial` (Tier 2), `vdd-sarcastic` (Tier 2)

**Steps:**

1. **Load Skills**: Read `.agent/skills/vdd-adversarial/SKILL.md` and `.agent/skills/vdd-sarcastic/SKILL.md`.
2. For each implemented module:
   a. Activate Adversary (Sarcasmotron)
      - Apply the `vdd-adversarial` skill: Red Flags, Challenge Assumptions, Failure Simulation.
      - Use critique template from `.agent/skills/vdd-adversarial/assets/template_critique.md`.
      - Review all code + tests with fresh context (no relationship drift).
   b. If real issues found:
      - Call workflow `03-develop-single-task` to fix issues.
      - Repeat this workflow (recursive call if needed).
   c. Terminate when adversary hallucinations dominate (Convergence Signal — see skill).
3. Announce: "VDD cycle complete: zero-slop achieved"
