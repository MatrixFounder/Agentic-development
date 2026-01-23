# High-Grade Solidity Security Checklist

> **Standard:** Aligned with SCSVS (Smart Contract Security Verification Standard) L2.

## 1. Access Control (SCSVS V2)
- [ ] **Role Management:** Are admins, owners, and minters strictly defined?
- [ ] **Timelocks:** Are critical parameter changes timelocked (e.g., `TimelockController`)?
- [ ] **Multi-Sig:** Is the owner a multisig (Gnosis Safe) rather than EOA?
- [ ] **Initialization:** Is `initialize()` protected with `initializer` modifier?

## 2. DeFi Patterns & Economics
- [ ] **Flash Loan Attack:** Does the protocol rely on spot price? (Vulnerable).
  - *Fix:* Use TWAP or Chainlink Oracles.
- [ ] **Oracle Manipulation:** Are oracle updates validated?
- [ ] **Slippage:** Do swap functions accept a `minOutput` parameter?
- [ ] **Rounding Errors:** Check for dust locking or favor-user rounding.

## 3. Cryptography (SCSVS V5)
- [ ] **Signature Replay:** Does the signature message include `nonce` and `chainId`?
- [ ] **Malleability:** Are signatures checked against `ecrecover` malleability issues (use OpenZeppelin `ECDSA`)?
- [ ] **Randomness:** Is randomness secure (Chainlink VRF) or predictable (block.timestamp/hash)?

## 4. Upgradability
- [ ] **Storage Collisions:** Do storage layouts match between versions?
- [ ] **Constructors:** Are initializers used instead of constructors for proxies?
- [ ] **Self-Destruct:** (Deprecated) Is `selfdestruct` reachable? 

## 5. SWC Registry (Common Pitfalls)
- [ ] **SWC-107 (Reentrancy):** Use `ReentrancyGuard` (`nonReentrant`) on ALL external calls.
- [ ] **SWC-101 (Overflow):** Is Solidity ^0.8.0 used? (Auto-checks).
- [ ] **SWC-114 (Tx.Origin):** Avoid `tx.origin` for auth.
- [ ] **SWC-116 (Timestamp):** Don't use `block.timestamp` for strict timing (< 15s).

## 6. Logic & "The Hacker Mindset"
- [ ] **Denial of Service:** Can an attacker loop forever or fill an array to block functionality?
- [ ] **Front-Running:** Can a bot observe a tx and profit by ordering before it?
