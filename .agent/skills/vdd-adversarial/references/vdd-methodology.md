# Verification-Driven Development (VDD)

## Methodology: Iterative Adversarial Refinement

### Overview
Verification-Driven Development (VDD) is a high-integrity software engineering framework designed to eliminate "code slop" and logic gaps through a generative adversarial loop. Unlike traditional development cycles that rely on passive code reviews, VDD utilizes a specialized multi-model orchestration where a Builder AI and an Adversarial AI are placed in a high-friction feedback loop, mediated by a human developer and a granular tracking system.

**Terms.** `Sarcasmotron` is the name the original write-up gives the Adversarial AI; the `vdd-sarcastic` skill is its persona. `Chainlink` is the decomposition method of §II.1, and a `bead` is one of its sub-issues. `GitHub Runners` stands for the CI runners of the project.

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
- Context Resetting: A fresh context window is used for Sarcasmotron on every turn, ensuring every critique is as rigorous and detached as the first. Grounding (replaces the earlier anthropomorphic "drift" framing): (1) **multi-turn context interference / assumption lock-in** — models lock onto early assumptions and degrade ~39% vs single-turn on the same tasks (arXiv:2505.06120); (2) **context rot** — effective attention degrades as accumulated history grows (Chroma 2025); (3) **pushback-driven sycophantic belief updates** — in-session pushback measurably flips correct judgments (TRUTH DECAY / SYCON-Bench).

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
VDD terminates on an **objective bar** ("Objective Convergence"), not on a subjective "the critic ran out of real bugs" signal. The refinement cycle continues until all four conditions hold simultaneously:

1. The full test run has actually been executed, by you or by whoever handed you the review. Handed-over evidence is the command with its captured output, or a summary of it (exit code, pass/fail counts, failures). A handed-over `NOT RUN (<reason>)` means the run was not executed.
2. Zero CRITICAL findings.
3. Zero legitimate findings in logic / security / slop.
4. Only bikeshedding/style remains.

Condition 1 with no evidence, or with evidence that reads `NOT RUN`, is unverifiable: report the finding 'exit-bar condition unverifiable — <thing> NOT RUN (<reason>)' in the risk table, never approve.

Two consequences:

- Maximum Viable Refinement ("Zero-Slop"): the state in which the code provably clears the objective bar above — not the state in which a hyper-critical adversary feels forced to invent problems.
- The Exit Signal: approval is bound to the objective bar. A lazy or sycophantic adversary that fabricates a nitpick to exit early is exactly the failure mode this criterion eliminates; until the bar is met, the cycle continues.

### V. Core Principles of VDD

1. Anti-Slop Bias: Assumes that the first "correct" version of code is likely the most dangerous due to hidden technical debt.
2. Exhaustive Reporting (supersedes "Forced Negativity"): the reviewer must report every issue, including low-confidence ones, attaching confidence + severity to each finding; filtering happens downstream. (The earlier rationale — adversarial tone to bypass the model's default agreeableness — is retired: vendors now train sycophancy out, and the documented recall lever is the reporting-threshold instruction, not tone.)
3. Linear Accountability: every finding names the line it concerns and the check that verifies its fix. Where the project tracks issues, each change also traces to one; in the original method that is a `Chainlink` `bead`.
4. Context-Interference Resistance (formerly "Entropy Resistance"): by cycling context windows, VDD sidesteps the documented multi-turn failure modes — assumption lock-in (arXiv:2505.06120), context rot (Chroma 2025), and pushback-driven belief updates (TRUTH DECAY / SYCON) — not a vague "loss of focus."

> "VDD turns code generation into a survival-of-the-fittest environment where only the most robust logic survives the Sarcasmotron."