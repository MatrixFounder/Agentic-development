# Antigravity Workflows Manual

This document serves as the **Single Source of Truth** for all automation workflows in the Antigravity system. Workflows are defined in `.agent/workflows/` and can be executed by the Orchestrator to automate complex development processes.

## 🚀 Workflow Registry

| Variant | Workflow Name | Description | Command to Run |
| :--- | :--- | :--- | :--- |
| **Standard** | **Start Feature** | Begins a new feature cycle: Analysis, TZ creation, Architecture review. | `Start feature [Name]` / `run 01-start-feature` |
| **Standard** | **Plan Implementation** | Generates a detailed implementation plan and task breakdown (Stub-First). | `Plan implementation` / `run 02-plan-implementation` |
| **Standard** | **Develop Task** | Executes a single development task from the plan. | `Develop task [ID]` / `run 03-develop-task` |
| **Standard** | **Update Docs** | Updates project documentation (README, Architecture, etc.). | `Update docs` / `run 04-update-docs` |
| **VDD** | **VDD Start Feature** | Starts a feature in High-Integrity VDD mode (Chainlink Decomposition). | `Start VDD feature [Name]` / `run vdd-01-start-feature` |
| **VDD** | **VDD Plan** | Atomic breakdown of issues into verifiable "Beads". | `Plan VDD` / `run vdd-02-plan` |
| **VDD** | **VDD Develop** | Runs the **Adversarial Loop** (Sarcasmotron) to implement code with zero slop. | `Develop VDD task` / `run vdd-03-develop` |
| **Nested** | **Base Stub-First** | The core Stub-First pipeline (can be called by other workflows). | `run base-stub-first` |
| **Nested** | **VDD Adversarial** | Isolated Adversarial Refinement Loop. | `run vdd-adversarial` |
| **Nested** | **VDD Enhanced** | Combines Stub-First structure with VDD verification (`Base` → `Adversarial`). | `run vdd-enhanced` |
| **Robust** | **Full Robust** | The Ultimate Pipeline: `VDD Enhanced` + `Security Audit`. | `run full-robust` |
| **Audit** | **Security Audit** | Standalone security check using the Security Auditor agent. | `Run security audit` / `run security-audit` |

---

## 📖 Detailed Guides

### 1. Standard Workflow (Stub-First)
*Best for: MVPs, Prototypes, Standard Features*

The default "happy path" for development. Focuses on speed and structural integrity.
1. **Analysis (`01`)**: The Agent reads instructions, checks for known issues, and creates a Technical Specification (TZ).
2. **Planning (`02`)**: The Agent creates a `plan.md` and detailed task files (`docs/tasks/`).
3. **Development (`03`)**: The Agent implements tasks one by one, prioritizing stubs before logic.

### 2. VDD (Verification-Driven Development)
*Best for: Mission-Critical Systems, Complex Logic, Security Components*

A high-integrity mode based on **Adversarial Refinement**.
- **Philosophy**: "It's not done until the Adversary can't roast it."
- **Mechanism**: A secondary AI persona ("Sarcasmotron") aggressively critiques the code and tests. The developer must fix all issues until the Adversary is satisfied (the "Hallucination Exit").
- **Workflow**:
    - `vdd-01`: Breaks down Epics into Issues (Chainlink).
    - `vdd-02`: Breaks down Issues into Beads (Atomic Verifiable Units).
    - `vdd-03`: The Implementation Loop with the Adversary.

### 3. Nested & Advanced Workflows
*Best for: Power Users, Architects*

These workflows utilize the **Nesting** capability, where one workflow calls another (`Call /workflow-name`).

- **`/vdd-enhanced`**:
    - **Why?** You want the structure of "Stub-First" but the quality assurance of "VDD".
    - **How?** It runs the standard planning phase, then switches to the Adversarial Loop for implementation.

- **`/full-robust`**:
    - **Why?** You need maximum confidence for production deployment.
    - **How?** It runs `vdd-enhanced` and follows it up with a dedicated **Security Audit**.

### 4. specialized Workflows

- **`/security-audit`**:
    - **Agent**: `System/Agents/10_security_auditor.md`
    - **Action**: Scans the codebase for OWASP Top 10 vulnerabilities, secret leaks, and hazardous dependencies.
    - **Output**: `docs/SECURITY_AUDIT.md`

---

## 🛠 Extension Guide

To add a new workflow:
1. Create a `.md` file in `.agent/workflows/`.
2. Use the standard header:
   ```markdown
   ---
   description: Your workflow description
   ---
   ```
3. Define the steps (Agent prompts, shell commands, or nested workflow calls).
4. **Update this file** to include it in the Registry.
