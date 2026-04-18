# Fuzzing & Invariant Guidelines

> **Scope:** Smart contracts (Solidity/EVM) + high-value server logic. Unit tests prove code works for **one** input. Fuzzing proves it works for **all** inputs. Invariants prove the **state** is always valid.

## 1. Invariant Categories

Define each invariant mathematically. Failing any one is a protocol-breaking bug.

### 1.1 Accounting (Core)
- **Solvency:** `totalAssets() >= totalLiabilities()`
- **Conservation of Value:** `sum(user_balances) == token.totalSupply()` (no mint/burn leak)
- **Share/Asset ratio (ERC-4626):** `convertToAssets(convertToShares(x)) <= x` (round-down contract)
- **Fee invariant:** `user_received + protocol_fee == principal` (no overcharge, no undercharge)

### 1.2 Access Control
- **Ownership uniqueness:** exactly one `owner` at any time
- **Two-step transfer:** pending owner is zero unless `acceptOwnership` in-flight
- **Role coverage:** every state-mutating function has an explicit role check OR is marked as public-writable

### 1.3 Monotonicity
- **Nonces:** `nonce` strictly increases (CWE-294, replay protection)
- **Global counters:** `totalDeposits`, `totalWithdrawals` never decrease
- **Timestamps:** `lastUpdated >= previousUpdate`

### 1.4 Pausability
- **Pause gate:** when `paused == true`, no state-mutating public function succeeds
- **Emergency exit:** paused state MUST still permit withdrawals (users can exit)
- **Unpause authorization:** only `pauser` role can unpause

### 1.5 ERC-20 specific
- `transfer(to, amount)` where `amount == 0` MUST NOT revert (ERC-20 compliance)
- `approve(spender, 0)` MUST always succeed (race-condition reset)
- Balance of `address(0)` is always `0`
- `transferFrom` consumes allowance exactly by `amount` (no over/under-charge)

### 1.6 ERC-4626 specific
- `maxDeposit(user) == type(uint256).max` when not paused (no silent cap)
- `maxWithdraw(user) <= balanceOf(user)` (no illusory withdrawable)
- `totalAssets()` monotonically non-decreasing in absence of losses/withdrawals
- Share price (`totalAssets / totalSupply`) non-decreasing under yield accrual

### 1.7 Oracle / Price Safety
- `price > 0` at every read-point
- Oracle `updatedAt` within freshness window (e.g., `block.timestamp - updatedAt < 1 hour`)
- TWAP interval ≥ minimum required (e.g., 30 minutes on Uniswap V3)

### 1.8 Reentrancy
- Contract state is **consistent** both before AND after external calls
- `nonReentrant` modifier present on every state-mutating entry with external calls

## 2. Tooling Setup

### 2.1 Foundry (invariant tests)
```solidity
// test/foundry/Invariants.t.sol
import "forge-std/Test.sol";

contract InvariantTest is Test {
    Protocol protocol;
    Handler handler;

    function setUp() public {
        protocol = new Protocol();
        handler = new Handler(protocol);
        targetContract(address(handler));     // handler-based, see §3
        excludeContract(address(protocol));   // let handler drive
    }

    function invariant_solvency() public {
        assertGe(protocol.totalAssets(), protocol.totalLiabilities());
    }

    function invariant_totalSupply_equals_userBalances() public {
        assertEq(handler.sumOfBalances(), protocol.token().totalSupply());
    }
}
```

Run with:
```bash
forge test --match-contract Invariant -vvv
# Depth & runs tuned in foundry.toml: fuzz.runs = 10000, invariant.depth = 500
```

### 2.2 Echidna (property-based)
```solidity
// contracts/EchidnaProtocol.sol
contract EchidnaProtocol is Protocol {
    function echidna_solvency() public view returns (bool) {
        return totalAssets() >= totalLiabilities();
    }
}
```
Run: `echidna EchidnaProtocol.sol --config echidna.yaml`

### 2.3 Medusa (EVM coverage-guided)
Preferred for deep state-space exploration; targets ABI by default; handle via `medusa.json`.

### 2.4 Halmos / Kontrol (symbolic execution)
For invariants that Foundry fuzzing cannot reach within reasonable depth. Slower but exhaustive within symbolic bounds.

## 3. Handler-Based Fuzzing (MANDATORY for non-trivial protocols)

Direct fuzzing on the protocol ABI produces ~99% reverting calls (invalid inputs, wrong preconditions). Use a **Handler** to guide the fuzzer to *meaningful* state transitions:

```solidity
contract Handler is Test {
    Protocol protocol;
    mapping(address => uint256) public ghostBalances;  // shadow accounting
    address[] public actors;
    uint256 public sumOfBalances;

    constructor(Protocol _p) {
        protocol = _p;
        for (uint i = 0; i < 5; i++) actors.push(address(uint160(0xA11CE + i)));
    }

    function deposit(uint256 actorSeed, uint256 amount) public {
        address actor = actors[actorSeed % actors.length];
        amount = bound(amount, 1, 1e24);  // realistic bounds
        vm.prank(actor);
        protocol.deposit(amount);
        ghostBalances[actor] += amount;
        sumOfBalances += amount;
    }

    function withdraw(uint256 actorSeed, uint256 amount) public {
        address actor = actors[actorSeed % actors.length];
        amount = bound(amount, 0, ghostBalances[actor]);
        vm.prank(actor);
        protocol.withdraw(amount);
        ghostBalances[actor] -= amount;
        sumOfBalances -= amount;
    }
}
```

## 4. Fuzzing Depth Requirements

| Criticality | Minimum runs | Minimum depth | Tool |
| :--- | :--- | :--- | :--- |
| Core accounting (ERC-20/4626/lending) | 50,000 | 500 | Foundry + Echidna |
| Access control | 10,000 | 200 | Foundry |
| New feature | 5,000 | 100 | Foundry |
| Pre-audit release | 100,000 | 1,000 | All three (Foundry, Echidna, Medusa) |

## 5. Coverage & Quality Gates

- [ ] **Invariant coverage** — every state-mutating function is reachable from at least one handler action.
- [ ] **Branch coverage** — `forge coverage` reports ≥90% on non-trivial contracts.
- [ ] **Revert coverage** — every `require`/`revert` path covered by at least one expected-revert test.
- [ ] **Ghost state** — Handler maintains shadow accounting for cross-verification against protocol state.

## 6. Post-Fuzz Regression Discipline

When the fuzzer finds a counterexample:
1. **Freeze the seed** — commit the reproducer as a traditional unit test (`testFuzz_repro_solvencyBug`).
2. **Fix** the root cause.
3. **Re-run** the full invariant suite — do NOT increase depth/runs to paper over a flaky finding.
4. **Add** the reverse invariant if applicable (e.g., if solvency broke via rounding, add `roundingDirection == DOWN` invariant).

## 7. Edge-Case Checklist (always cover in unit tests too)

- [ ] Input = `0`
- [ ] Input = `type(uint256).max`
- [ ] Input = one wei off common boundaries (e.g., `minDeposit - 1`, `minDeposit`, `minDeposit + 1`)
- [ ] Empty arrays and empty strings
- [ ] Single-element arrays
- [ ] Maximum-size arrays (gas-limit boundary)
- [ ] Self-interactions (`transfer(self, x)`, `approve(self, x)`)
- [ ] Zero-address recipient / sender
- [ ] Re-entry attempts through ERC-777/ERC-1155 `onReceived` hooks
- [ ] Block timestamp manipulation within MEV bounds (±12s)

## 8. Reporting

Include in every audit report:
- List of invariants tested
- Total runs / depth executed
- Any counterexamples found (with seed) + remediation
- Coverage percentage
- Tools used (Foundry / Echidna / Medusa / Halmos)

> **Rule of thumb:** If you can't write the invariant as a one-line mathematical expression, you don't understand the protocol well enough to audit it.
