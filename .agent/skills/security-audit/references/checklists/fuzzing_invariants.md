# Fuzzing & Invariant Guidelines

## Philosophy
Unit tests prove code works for *one* input. Fuzzing proves it works for *all* inputs. Invariants prove the *state* is always valid.

## 1. Invariants (Properties that MUST hold true)
Define these mathematically:

- **Solvency:** `totalAssets() >= totalLiabilities()`
- **Conservation of Energy:** `sum(user_balances) == token.totalSupply()`
- **Monotonicity:** `nonces` only increase.
- **Access:** Only `owner` can call `mint`.

## 2. Foundry / Echidna Setup

### Foundry (`test/foundry/Invariants.t.sol`)
```solidity
import "forge-std/Test.sol";

contract InvariantTest is Test {
    Protocol protocol;

    function setUp() public {
        protocol = new Protocol();
        targetContract(address(protocol));
    }

    // "invariant_" prefix
    function invariant_solvency() public {
        assertGe(protocol.assets(), protocol.liabilities());
    }
}
```

## 3. Handler-Based Fuzzing
Avoid random calls. Use a **Handler** contract to guide the fuzzer to meaningful actions (e.g., only swap tokens that exist).

## 4. Checklist
- [ ] Are all state variables covered by at least one invariant?
- [ ] Does the fuzzer run for adequate time/depth? (> 10k runs)?
- [ ] Are edge cases (0, max_uint, empty string) explicitly covered in unit tests too?
