# Solidity Developer Guidelines

## Security First
- **Checks-Effects-Interactions:** ALWAYS update state variables BEFORE making external calls to prevent reentrancy.
- **Access Control:** Explicitly define function visibility (`external`, `public`, `internal`, `private`). Use `Ownable` or `AccessControl` for restricted functions.
- **Overflow/Underflow:** Rely on Solidity 0.8+ built-in checks.

## Gas Optimization
- **Storage:** Minimize storage writes. Use `calldata` instead of `memory` for read-only function arguments.
- **Loops:** Avoid unbounded loops that could hit block gas limits.

## Testing
- Use Hardhat or Foundry for testing.
- Test both success and failure cases (reverts).
