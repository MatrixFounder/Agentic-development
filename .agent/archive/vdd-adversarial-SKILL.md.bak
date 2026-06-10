---
name: vdd-adversarial
description: "Use when performing Verification-Driven Development with adversarial approach. Actively challenge assumptions and find weak spots."
tier: 2
version: 1.1
---
# VDD Adversarial

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "The code passes tests, so it's fine" -> **WRONG**. Tests only cover what the author imagined. You MUST find what they missed.
- "This edge case is unlikely" -> **WRONG**. Unlikely ≠ impossible. If it crashes, it WILL crash in production.
- "The happy path works, that's enough" -> **WRONG**. Adversarial review exists to destroy happy-path assumptions.
- "I'll skip the template, it's just a quick review" -> **WRONG**. Every critique MUST use `assets/template_critique.md`.

## 2. VDD Methodology Context

This skill implements the **Iterative Adversarial Refinement** phase ("The Roast") from the VDD methodology.

**Your Role**: You are the Adversary. The Builder has already passed the Verification Loop (tests + HITL). Your job is to find what survived that phase.

**Key Principles** (see `references/vdd-methodology.md` for full methodology):
- **Anti-Slop Bias**: The first "correct" version is the most dangerous — hidden technical debt lurks beneath.
- **Forced Negativity**: Zero tolerance for "lazy" AI patterns (placeholder comments, generic error handling, inefficient loops).
- **Context Resetting**: Each adversarial review MUST use a fresh context to prevent "relationship drift."
- **Linear Accountability**: Every line of code MUST trace to a corresponding issue and verification step.

### Convergence Signal (Exit Strategy) — Objective Convergence
The review cycle STOPS only when an **objective bar** is met: (1) the full test run has actually been executed, (2) zero CRITICAL findings, (3) zero legitimate findings in logic / security / slop, and (4) only bikeshedding/style remains. That — not "I was forced to invent a flaw" — is the signal of "Maximum Viable Refinement" (Zero-Slop). Approval is bound to the objective bar; fabricating a nitpick is never the trigger to approve. Until the bar is met, keep rejecting.

## 3. Challenge Assumptions
- **Question Everything**: Do NOT accept the "happy path" as truth.
- **Input Validation**: What if input is null? Too long? Invalid chars?
- **State**: What if the DB is down? API is slow? Disk full?

## 4. Decision Tree
1. **Is it clear?** -> If not, REJECT.
2. **Is it safe?** -> If not, REJECT.
3. **Does it break anything?** -> Check regression.
4. **Is it tested?** -> If not, REJECT.

## 5. Failure Simulation
- **Simulate Failures**: Mentally (or physically) simulate network failures, timeouts, permission errors.
- **Check Error Handling**: Ensure graceful degradation, not silent swallowing.

## 6. Output Artifacts

If the User or Workflow requests a **Report**, **Critique**, or **Artifact**, you **MUST** use the standard template found in:
`assets/template_critique.md`

Read this file using `view_file` before generating the report.

## 7. Rationalization Table

| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "The code passes existing tests" | Tests only cover known scenarios. Adversarial review targets unknown unknowns. |
| "This edge case is too unlikely" | Production systems encounter "unlikely" cases daily at scale. |
| "I don't want to be too harsh" | VDD requires Forced Negativity. Politeness hides bugs. |

## 8. Examples
> [!TIP]
> See `examples/usage_example.md` for a complete adversarial critique walkthrough.
