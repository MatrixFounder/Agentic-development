# Workspace Workflows & VDD Method

This project supports multiple development "variants" via workspace workflows.

## Workflow Registry

| Variant | Prefix | Description | Use Case |
| :--- | :--- | :--- | :--- |
| **Standard** | `(01-04)` | Stub-First Agentic Development | General features, MVPs, Prototypes |
| **VDD** | `vdd-` | Verification-Driven Development (Adversarial) | Mission-critical components, complex logic, security-sensitive code |

## Usage
To trigger a workflow, simply use the slash command or ask the agent to run the specific file.

- **Standard**: "Start feature X" -> Agent runs `01-start-feature.md`
- **VDD**: "Start feature X in VDD mode" -> Agent runs `vdd-01-start-feature.md`

## Workflow File Naming Schema
New workflows must follow this schema to keep the registry clean:
`[variant]-[stage]-[action].md`

- **variant**: `std` (implicit/omitted for backward compat), `vdd`, `bdd`, etc.
- **stage**: `01` (Init), `02` (Plan), `03` (Dev), `04` (Docs/Misc).
- **action**: Kebab-case description (e.g., `start-feature`, `develop`).

## Variations Details

### 1. Standard (Stub-First)
The default agentic workflow focusing on speed and structure.
- `01-start-feature`: Analysis & Architecture
- `02-plan-implementation`: Planning
- `03-develop-task`: Implementation Loop
- `04-update-docs`: Documentation

### 2. VDD (Verification-Driven Development)
A high-integrity mode using "Iterative Adversarial Refinement".

**Source**: [Verification-Driven Development (VDD) via Iterative Adversarial Refinement](https://gist.github.com/dollspace-gay/45c95ebfb5a3a3bae84d8bebd662cc25#file-method-md)

#### Core Concept
VDD is designed to eliminate "code slop" (lazy patterns, hidden technical debt, hallucinations) through a **Generative Adversarial Loop**:
1. **Builder**: Writes the code and tests.
2. **Sarcasmotron (Adversary)**: A hostile AI persona that critiques the code with zero tolerance.
3. **Loop**: The process only ends when the code is so robust that the Adversary starts "hallucinating" flaws because it can't find real ones (The "Hallucination Exit").

#### VDD vs. TDD (Comparison)
| Feature | TDD (Test-Driven) | VDD (Verification-Driven) |
| :--- | :--- | :--- |
| **Primary Goal** | Functional Correctness | Robustness & "Zero-Slop" |
| **Driver** | Unit Tests (Red-Green-Refactor) | Adversarial Critique (The "Roast") |
| **Mindset** | "Does it work as expected?" | "Can I break it? Is it lazy?" |
| **Exit Condition** | All tests pass | Adversary runs out of valid critiques |
| **Best For** | Domain logic, Algorithms | Security, High-Reliability Systems |

#### Workflows
- **[vdd-01-start-feature](file:///Users/sergey/Antigravity/agentic-development/.agent/workflows/vdd-01-start-feature.md)**
    - *Focus*: Chainlink Decomposition (Epics -> Issues).
- **[vdd-02-plan](file:///Users/sergey/Antigravity/agentic-development/.agent/workflows/vdd-02-plan.md)**
    - *Focus*: Atomic Breakdown (Issues -> Beads). A Bead is a unit verifiable by a single test.
- **[vdd-03-develop](file:///Users/sergey/Antigravity/agentic-development/.agent/workflows/vdd-03-develop.md)**
    - *Focus*: **The Adversarial Loop** (Implement -> Verify -> Sarcasmotron -> Refine).

## Extension Guide
To add a new variant (e.g., `tdd`):
1. **Define the Philosophy**: What makes it different? (e.g., "Write tests BEFORE code").
2. **Create Workflows**:
    - `tdd-02-plan.md`: Plan the tests.
    - `tdd-03-develop.md`: Red-Green-Refactor loop.
3. **Update Registry**: Add to this file.
