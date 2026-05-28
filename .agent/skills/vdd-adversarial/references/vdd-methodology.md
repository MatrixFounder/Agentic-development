# Verification-Driven Development (VDD)

## Methodology: Iterative Adversarial Refinement

### Overview
Verification-Driven Development (VDD) is a high-integrity software engineering framework designed to eliminate "code slop" and logic gaps through a generative adversarial loop. Unlike traditional development cycles that rely on passive code reviews, VDD utilizes a specialized multi-model orchestration where a Builder AI and an Adversarial AI are placed in a high-friction feedback loop, mediated by a human developer and a granular tracking system.

### II. The Workflow Phases
#### 1. Decomposition via Chainlink
The software goal is first ingested by the Builder. Using the Chainlink methodology, the task is atomized into a hierarchical structure:
- Epics: Broad feature objectives.
- Issues: Functional components.
- Sub-issues (The "Beads"): Atomic units of work that ensure no logic is left unaddressed.

#### 2. The Verification Loop (Builder + Human)
Before adversarial stress-testing begins, the code must be functionally verified:
- Automated Verification: Test coverage is mandatory. The Builder must write unit and integration tests for all logic.
- Human-in-the-Loop (HITL): Manual testing to ensure the software matches the "spirit" of the requirement. Refinements are made here until the developer is satisfied with the initial feature set.

#### 3. Iterative Adversarial Refinement (The "Roast")
The verified codebase is presented to Sarcasmotron. This phase is defined by "The Roast":
- Negative Prompting: The Adversary is prompted to have zero tolerance for human error or "lazy" AI patterns (e.g., placeholder comments, inefficient loops, or generic error handling).
- Context Resetting: A fresh context window is used for Sarcasmotron on every turn. This prevents "relationship drift" or the AI becoming too agreeable, ensuring every critique is as harsh and detached as the first.

#### 4. Feedback Integration
The critique from Sarcasmotron is fed back to the Builder. The Builder must then:
1. Address legitimate flaws.
2. Refactor weak logic.
3. Update tests to cover the newly discovered edge cases.

### III. Mathematical Hardening and CI/CD Integration
As the refinement cycle progresses, the adversarial pressure often reveals edge cases that standard unit testing cannot fully guarantee against. This leads to the integration of Formal Verification tools into the GitHub Runners to ensure mathematical correctness:
- Model Checking & Symbolic Execution: Tools like Kani are integrated to prove that certain conditions (like memory safety or arithmetic overflows) are mathematically impossible within the code.
- Adversarial Cryptography/Security: Integrating suites like Wycheproof to test the implementation against known cryptographic vulnerabilities.
- Automated Correctness Gating: Once these formal methods are established, they are added to the CI/CD pipeline. The Builder is then tasked with ensuring every PR not only passes the "Roast" but also satisfies the mathematical proof requirements of the formal verifiers.

### IV. Convergence and the Exit Strategy (Objective Convergence)
VDD terminates on an **objective bar** ("Objective Convergence"), not on a subjective "the critic ran out of real bugs" signal. The refinement cycle continues until all four conditions hold simultaneously: (1) the full test run has actually been executed, (2) zero CRITICAL findings, (3) zero legitimate findings in logic / security / slop, and (4) only bikeshedding/style remains.
- Maximum Viable Refinement ("Zero-Slop"): the state in which the code provably clears the objective bar above — not the state in which a hyper-critical adversary feels forced to invent problems.
- The Exit Signal: approval is bound to the objective bar. A lazy or sycophantic adversary that fabricates a nitpick to exit early is exactly the failure mode this criterion eliminates; until the bar is met, the cycle continues.

### V. Core Principles of VDD
1. Anti-Slop Bias: Assumes that the first "correct" version of code is likely the most dangerous due to hidden technical debt.
2. Forced Negativity: Uses adversarial pressure to bypass the "politeness" filters inherent in standard LLM interactions.
3. Linear Accountability: The Chainlink "beads" ensure that every line of code has a corresponding issue and verification step.
4. Entropy Resistance: By cycling context windows, VDD resists the natural tendency for long-running AI conversations to lose focus or quality.

> "VDD turns code generation into a survival-of-the-fittest environment where only the most robust logic survives the Sarcasmotron."