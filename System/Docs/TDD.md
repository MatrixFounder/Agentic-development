# Stub-First TDD (Test-Driven Development)

## Core Philosophy
The "Stub-First" strategy is a strict adaptation of TDD designed for Agentic Development. It ensures that the **Architecture** and **Contract** are verified before any implementation logic is written.

## The Cycle
1.  **Define Interface**: Create the class/function signatures with empty bodies or returns (Stubs).
2.  **Write Tests**: Create E2E or Unit tests that assert the expected behavior.
    *   *Crucial Step*: At the stub stage, tests must assert the *stubbed* return values (e.g., `assert result == None` or `assert result == True`). This proves the **wiring** works.
3.  **Verify Stubs**: Run tests. They should PASS on the stubs. This confirms the system components can talk to each other.
4.  **Implement Logic**: Replace stubs with real logic.
5.  **Update Tests**: Update assertions to valid real output.
6.  **Verify Implementation**: Run tests. They should PASS on valid logic.

## Why Stub-First?
*   **Prevents Hallucinations**: Agents cannot "guess" the implementation if they are forced to define the contract first.
*   **Separates Concerns**: "Does it run?" (Wiring) is separated from "Does it work?" (Logic).
*   **Reduces Rewrites**: If the design is wrong, you catch it at the Stub stage, before writing complex code.
