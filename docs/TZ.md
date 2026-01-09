## 0. Meta Information
- **Task ID:** 007
- **Slug:** security-audit

## 1. General Description
The goal is to implement a dedicated **Security Audit** workflow and agent role within the Antigravity system. This involves creating a specialized agent (`System/Agents/10_security_auditor.md`) focused on identifying vulnerabilities (OWASP Top 10, secrets, dependencies) and a modular workflow (`.agent/workflows/security-audit.md`) that executes this audit. This new workflow should be capable of being run independently or nested within other workflows (e.g., `/full-robust`). Documentation and system prompts must be updated to reflect these new capabilities.

## 2. List of Use Cases

### UC-01: Execute Security Audit Workflow
**Actors:** User, Orchestrator, Security Auditor
**Preconditions:** Codebase is in a state ready for audit (implementation complete).
**Main Scenario:**
1. User or Orchestrator triggers `/security-audit`.
2. System gathers context (ARCHITECTURE, modified files, dependencies).
3. **Security Auditor** agent analyzes code for vulnerabilities (OWASP, secrets, etc.).
4. Security Auditor produces a structured report (`docs/SECURITY_AUDIT.md`).
5. (Optional) If critical issues are found, fix tasks are generated.
**Postconditions:** Verification report exists in `docs/SECURITY_AUDIT.md`.

### UC-02: Nested Execution in Full Robust Workflow
**Actors:** Orchestrator
**Preconditions:** `/full-robust` workflow is executed.
**Main Scenario:**
1. Orchestrator executes standard robust steps (VDD, etc.).
2. Orchestrator calls `/security-audit` as a nested workflow.
3. Security phase completes before final success.
**Postconditions:** Project is audited as part of the full robust pipeline.

### UC-03: Security Auditor Role Definition
**Actors:** System
**Preconditions:** None.
**Main Scenario:**
1. `System/Agents/10_security_auditor.md` is loaded as the instruction set.
2. Agent follows "Core Principles" (OWASP, static analysis mindset).
3. Agent outputs strictly formatted security reports.
**Postconditions:** Agent behaves as a specialized security expert.

## 3. Non-functional Requirements
- **Modularity:** The security workflow must be decoupled and reusable.
- **Standards:** Audit should align with generic OWASP Top 10 principles where applicable.
- **Integration:** Seamless experience when calling via slash commands.

## 4. Constraints and Assumptions
- New agent role will be `System/Agents/10_security_auditor.md`.
- Workflow file will be `.agent/workflows/security-audit.md`.
- "Manual" tools (grep, find) will be used by the agent to simulate static analysis if external binary tools (bandit, npm audit) are not available/reliable in the env.

## 5. Open Questions
- None.
