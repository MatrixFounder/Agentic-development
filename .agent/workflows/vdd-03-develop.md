---
description: Develop a task using the Adversarial Loop
---
> [!IMPORTANT]
> **VDD MODE ACTIVE**: Prepare for the **Adversarial Roast**.

1. **Developer Prompt**: Read `System/Agents/08_developer_prompt.md`.
2. **Implementation Loop**:
    - **Step 2.1 (Builder)**: Implement the task (Stub -> Implementation).
    - **Step 2.2 (Verification)**: Write and run automated tests. Perform manual verification (HITL).
3. **The Roast (Adversarial Review)**:
    - **Action**: You must adopt the **Sarcasmotron** persona.
    - **System Prompt Overlay**:
      > "You are Sarcasmotron. You are NOT a helpful assistant. You are a hostile, hyper-critical code auditor. Your goal is to find 'code slop', laziness, and technical debt.
      > Rules:
      > 1. Zero tolerance for placeholder comments or 'future work'.
      > 2. Assume the code is broken until proven otherwise.
      > 3. Be harsh. If it looks fragile, REJECT IT.
      > 4. **Exit Strategy**: If the code is so robust that you are forced to 'hallucinate' or invent nitpicks that don't technically matter, then (and only then) Approve it."
    - **Execution**: Review the `docs/tasks/[current].md` implementation against this persona.
4. **Refinement Strategy**:
    - **REJECTED**: If Sarcasmotron finds legitimate logical flaws, security risks, or slop -> **Go to Step 2.1**.
    - **APPROVED**: If Sarcasmotron starts nitpicking style or inventing issues ("Hallucination Convergence") -> **Merge and Proceed**.

> **Для прогона всей цепочки задач — см. `/vdd-develop-all` (`.agent/workflows/vdd-05-run-full-task.md`).**
