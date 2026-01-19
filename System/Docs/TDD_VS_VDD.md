# Comparison: TDD vs VDD

| Feature | **TDD (Test-Driven Development)** | **VDD (Verification-Driven Development)** |
| :--- | :--- | :--- |
| **Primary Goal** | Functional Correctness & Design | Robustness, Security & "Zero-Slop" |
| **Key Mechanism** | Unit/E2E Tests (Red-Green-Refactor) | Adversarial Critique (The "Roast") |
| **Driver** | Test Coverage | Adversarial Agent (Sarcasmotron) |
| **Mindset** | "Does it work as expected?" | "Can I break it? Is it lazy?" |
| **Exit Condition** | All tests pass | Adversary runs out of valid critiques |
| **Cost (Time)** | Medium (Standard) | High (Iterative) |
| **Best For** | General features, MVPs, UI | Security, Core Logic, High-Reliability Systems |

## How they work together
They are not mutually exclusive. The **Stub-First TDD** provides the foundation (structure and basic correctness), while **VDD** acts as a hardening layer on top.

**Workflow:**
`Analysis` -> `TDD (Stub -> Impl)` -> `VDD (Adversarial Refinement)` -> `Production`
