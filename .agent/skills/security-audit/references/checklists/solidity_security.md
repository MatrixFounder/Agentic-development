# High-Grade Solidity Security Checklist

> **Standard:** Aligned with SCSVS (Smart Contract Security Verification Standard) L2.
> **Updated:** March 2026 — includes EIP-1153 (Transient Storage), EIP-6780 (selfdestruct changes), ERC-4337 (Account Abstraction).

## 1. Access Control (SCSVS V2)
- [ ] **Role Management:** Are admins, owners, and minters strictly defined?
- [ ] **Timelocks:** Are critical parameter changes timelocked (e.g., `TimelockController`)?
- [ ] **Multi-Sig:** Is the owner a multisig (Safe) rather than EOA?
- [ ] **Initialization:** Is `initialize()` protected with `initializer` modifier?
- [ ] **Two-Step Transfer:** Does ownership transfer use a two-step (propose + accept) pattern?
- [ ] **Default Admin:** Is OpenZeppelin `DEFAULT_ADMIN_ROLE` properly protected?

## 2. DeFi Patterns & Economics
- [ ] **Flash Loan Attack:** Does the protocol rely on spot price? (Vulnerable).
  - *Fix:* Use TWAP or Chainlink Oracles.
- [ ] **Oracle Manipulation:** Are oracle updates validated (staleness check, min/max bounds)?
- [ ] **Slippage:** Do swap functions accept a `minOutput` parameter?
- [ ] **Rounding Errors:** Check for dust locking or favor-user rounding.
- [ ] **Sandwich Attack:** Can MEV bots extract value from user transactions?
- [ ] **Read-Only Reentrancy:** Are view functions (e.g., `getRate()`) used by other protocols safe from manipulation?

## 3. Cryptography (SCSVS V5)
- [ ] **Signature Replay:** Does the signature message include `nonce`, `chainId`, and `deadline`?
- [ ] **Malleability:** Are signatures checked against `ecrecover` malleability issues (use OpenZeppelin `ECDSA`)?
- [ ] **Randomness:** Is randomness secure (Chainlink VRF v2+) or predictable (block.timestamp/prevrandao)?
- [ ] **EIP-712:** Are typed structured data signatures used (not raw `keccak256`)?

## 4. Upgradability
- [ ] **Storage Collisions:** Do storage layouts match between versions? Use `@openzeppelin/upgrades` plugin to validate.
- [ ] **Constructors:** Are initializers used instead of constructors for proxies?
- [ ] **selfdestruct (EIP-6780):** Post-Dencun, `selfdestruct` only sends ETH but does NOT delete storage/code (except in same-tx creation). Is this behavior accounted for?
- [ ] **UUPS vs Transparent:** Is the upgrade function protected from unauthorized calls?
- [ ] **Beacon Proxy:** If using BeaconProxy, is the beacon admin protected?
- [ ] **Storage Gaps:** Do base contracts include `__gap` storage for future upgrades?

## 5. ERC-4337 Account Abstraction
- [ ] **Validation:** Is `validateUserOp` properly implemented (signature verification, nonce check)?
- [ ] **Paymaster Trust:** Are paymaster contracts verified and trusted?
- [ ] **Bundler MEV:** Can bundlers extract value or censor UserOperations?
- [ ] **Replay Protection:** Are UserOps protected against cross-chain replay?
- [ ] **Storage Access:** Does validation phase access only allowed storage slots (ERC-7562)?
- [ ] **Gas Estimation:** Is gas estimation accurate (avoid griefing via underestimation)?

## 6. Transient Storage (EIP-1153)
- [ ] **TSTORE/TLOAD Usage:** Is transient storage used correctly (cleared at end of transaction)?
- [ ] **Reentrancy Locks:** If using tstore for reentrancy guards, is the pattern correct?
- [ ] **Cross-Call State:** Is transient storage not relied upon across external calls to untrusted contracts?
- [ ] **EVM Compatibility:** Is the target chain post-Dencun (supports EIP-1153)?

## 7. SWC Registry (Common Pitfalls)
- [ ] **SWC-107 (Reentrancy):** Use `ReentrancyGuard` (`nonReentrant`) on ALL external calls.
- [ ] **SWC-101 (Overflow):** Is Solidity ^0.8.0 used? (Auto-checks). Beware `unchecked {}` blocks.
- [ ] **SWC-114 (Tx.Origin):** Avoid `tx.origin` for auth.
- [ ] **SWC-116 (Timestamp):** Don't use `block.timestamp` for strict timing (< 15s).
- [ ] **SWC-136 (Unencrypted Data):** Don't store sensitive data on-chain (it's all public).

## 8. Gas & Denial of Service
- [ ] **Unbounded Loops:** Can an attacker cause a loop to exceed block gas limit?
- [ ] **Gas Griefing:** Can a called contract waste gas to make the caller fail (63/64 rule)?
- [ ] **Array Growth:** Can arrays grow unbounded (DoS via storage cost)?
- [ ] **Front-Running:** Can a bot observe a tx and profit by ordering before it?
- [ ] **Block Stuffing:** Can an attacker fill blocks to delay time-sensitive operations?
- [ ] **returndata Bomb:** Can a called contract return excessive data to waste gas?

## 9. Cross-Chain & L2
- [ ] **Bridge Security:** Are bridge messages validated (nonce, source chain, sender)?
- [ ] **L2 Sequencer:** Is L2 sequencer downtime handled (Chainlink L2 Sequencer Uptime Feed)?
- [ ] **Gas Pricing:** Are L1↔L2 gas dynamics accounted for?
