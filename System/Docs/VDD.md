# VDD (Verification-Driven Development)

**Source / Inspiration**: [Verification-Driven Development (VDD) via Iterative Adversarial Refinement](https://gist.github.com/dollspace-gay/45c95ebfb5a3a3bae84d8bebd662cc25#file-method-md)

## Core Philosophy
VDD is a high-integrity development mode designed for mission-critical or complex components. It shifts the focus from "Validation" (Does it work?) to "Verification" (Is it robust/secure/correct?).

It uses an **Adversarial Agent** (often called "Sarcasmotron") to actively try to break the code, find logical inconsistencies, or point out "slop" (lazy implementation).

## The Cycle (Adversarial Loop)
1.  **Build**: Developer implements the feature (often using Stub-First TDD).
2.  **Attack (The Roast)**: The Adversarial Agent reviews the code with the specific goal of finding flaws, security holes, or bad practices.
3.  **Refine**: Developer fixes the identified issues.
4.  **Repeat**: The loop continues until the Adversary runs out of substantial things to criticize (The "Hallucination Exit").

## When to use VDD?
*   Security-sensitive modules (Auth, Payments).
*   Complex algorithmic logic.
*   Core system architecture.
*   Smart contract development (Solidity, Solana).
*   When "good enough" is not enough.

## Integration with Security Audit
VDD pairs naturally with the `security-audit` skill (v3.2). The adversarial loop can include automated scanning (`run_audit.py`) to verify that the scanner itself catches real-world vulnerability patterns. This was validated in VDD Rounds 1-3 against recent DeFi hacks (Dec 2025 – Mar 2026), resulting in 16 new Solidity-specific detection patterns.
