# Solidity Security Quick-Reference

> **Source**: `developer-guidelines/references/security/solidity.md`
> **Standard**: SCSVS L2 / OWASP Smart Contract Top 10

## 1. LLM Anti-Patterns ( DO NOT DO THIS )
- **External Calls Before State Updates**: NEVER update state after an external call (Reentrancy).
    - *Bad*: `call(); balance = 0;`
    - *Good*: `balance = 0; call();`
- **Using `tx.origin`**: NEVER use `tx.origin` for **authentication** (Phishing risk). Only use for EOA checks (`msg.sender == tx.origin`).
- **Unchecked Return Values**: NEVER ignore the return value of `call()`, `delegatecall()`, or `send()`.
- **Timestamp Dependence**: NEVER use `block.timestamp` for critical logic or randomness (miners can manipulate).
- **Floating Pragma**: NEVER use `^0.8.0`. Lock it: `pragma solidity 0.8.20;`.

## 2. Critical Grep Patterns (Audit These First)
| Pattern | Risk | Check |
| :--- | :--- | :--- |
| `\.call\{value:` | Reentrancy / Unchecked Call | Ensure checks-effects-interactions interaction AND check return bool. |
| `delegatecall` | Context Hijacking | Verify target address is immutable or strictly controlled admin-only. |
| `tx.origin` | Phishing / Auth Bypass | Replace with `msg.sender` unless strictly necessary (e.g. EOA check). |
| `block.timestamp` | Manipulation | Verify not used for randomness or short-term deadlines (< 15s). |
| `selfdestruct` | Logic Bomb | Deprecated. Verify unreachable or admin-only. |
| `public` (state var) | Visibility | Verify if sensitive data is exposed (public != private). |
| `assembly` | Memory Safety | Audit all inline assembly for memory corruption/slot clashes. |

## 3. Critical Vulnerabilities & Patterns

### Reentrancy (The "Billion Dollar Mistake")
**Secure Pattern (Checks-Effects-Interactions):**
```solidity
// 1. CHECKS
require(balances[msg.sender] > 0, "No balance");

// 2. EFFECTS (Update State Access)
uint256 amount = balances[msg.sender];
balances[msg.sender] = 0;

// 3. INTERACTIONS (External Call)
(bool success, ) = msg.sender.call{value: amount}("");
require(success, "Transfer failed"); // ALWAYS check return value
```
**Alternative**: Use `ReentrancyGuard` (`nonReentrant` modifier) from OpenZeppelin on **ALL** external state-changing functions.

### Integer Overflow/Underflow
- **Solidity >= 0.8.0**: Built-in checks. Reverts on overflow.
- **Solidity < 0.8.0**: MUST use `SafeMath` library.

### Access Control (Broken vs Secure)
**Vulnerable**:
```solidity
function withdraw(uint amount) public { msg.sender.transfer(amount); } // Anyone can call!
```
**Secure**:
```solidity
import "@openzeppelin/contracts/access/Ownable.sol";
contract Secure is Ownable {
    function withdraw(uint amount) public onlyOwner { ... }
}
```

### Input Validation
Always validate inputs at the start of functions:
```solidity
require(to != address(0), "Invalid recipient");
require(amount > 0, "Amount must be positive");
require(amount <= balances[msg.sender], "Insufficient balance");
```

### Front-Running Mitigation
- **Commit-Reveal Scheme**:
    1. User submits `hash(choice, secret)`.
    2. Next block/phase, user reveals `choice` and `secret`.
- **Min Return**: Always accept a `minOutput` or `maxSlippage` parameter for swaps.

## 4. Emergency Stop (Circuit Breaker)
Always implement a pause mechanism for critical systems.
```solidity
import "@openzeppelin/contracts/security/Pausable.sol";
contract Stoppable is Pausable, Ownable {
    function criticalOps() external whenNotPaused { ... }
    function emergencyPause() external onlyOwner { _pause(); }
}
```

## 5. Dangerous Functions
- `transfer()` / `send()`: Forward fixed 2300 gas. Can break with gas price changes. Prefer `call{value: ...}("")` with Checks-Effects-Interactions.
- `delegatecall()`: Executes code in *your* context. Target MUST be trusted. **CRITICAL**: Storage slots MUST match exactly to avoid corruption.
