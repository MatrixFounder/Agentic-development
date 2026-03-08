# High-Grade Solana Security Checklist

> **Framework:** Focus on Anchor v0.30+, but applicable to raw Rust.
> **Updated:** March 2026 — includes Token-2022, Anchor v0.30+ changes.

## 1. Account Validation (The "Missing Check" Problem)
- [ ] **Ownership:** Are all accounts checked for `owner == program_id` (unless explicitly external)?
- [ ] **Signer Checks:** Are sensitive actions (transfers, authority changes) gated by `is_signer` checks?
  - *Anchor:* Use `#[account(signer)]` or `Signer<'info>`.
- [ ] **Executable:** Are accounts correctly marked `executable` (or not)?
- [ ] **Discriminator:** Are account discriminators checked (Anchor does this automatically with `Account<'info, T>`)?
- [ ] **Constraint Validation:** Are `#[account(constraint = ...)]` checks used for business logic?

## 2. Arithmetic & Numeric
- [ ] **Overflow/Underflow:** Is `overflow-checks = true` in `Cargo.toml`? (Default in modern Anchor).
- [ ] **Precision:** Are decimal calculations handled safely (e.g., multiply before divide)?
- [ ] **Casting:** Usage of `try_from` or `checked_*` methods instead of raw `as u64` (truncation risks)?
- [ ] **u128 for Intermediate:** Are intermediate calculations done in u128 to prevent overflow?

## 3. PDA (Program Derived Addresses)
- [ ] **Seeds Validation:** Are PDA bump seeds validated?
  - *Anchor:* `#[account(seeds = [...], bump)]` handles this. Manual checks MUST verify `find_program_address` matches.
- [ ] **Uniqueness:** Do seeds guarantee a unique account per user/state (avoid aliasing)?
- [ ] **Canonical Bump:** Is the canonical bump (from `find_program_address`) used, not an arbitrary one?
- [ ] **Bump Storage:** Is the bump stored in the account data for efficiency and re-derivation?

## 4. Cross-Program Invocations (CPI)
- [ ] **Program ID Check:** Is the target program ID hardcoded or rigorously checked?
  - *Risk:* Calling a malicious "Token Program".
- [ ] **Privilege Escalation:** Does the PDA sign ONLY for what it owns?
- [ ] **CPI Guard:** Is CPI Guard (Token-2022) used where appropriate to prevent unauthorized CPI?
- [ ] **Remaining Accounts:** Are remaining accounts validated (not blindly forwarded to CPI)?

## 5. Anchor v0.30+ Specifics
- [ ] **Init:** Is `init` used correctly to prevent re-initialization attacks?
- [ ] **Close:** Are closed accounts zeroed out or marked to prevent revival (rent lamport drain)?
- [ ] **Big Space:** Are accounts with `space` > 10KB allocated using `zero_copy`?
- [ ] **Event CPI:** Are Anchor events emitted via `emit_cpi!()` when indexing is needed?
- [ ] **IDL:** Is the IDL up to date with account and instruction changes?
- [ ] **Error Codes:** Are custom error codes used (not generic `ProgramError`)?
- [ ] **Declare ID:** Is `declare_id!` consistent with deployed program address?

## 6. Token-2022 (Token Extensions)
- [ ] **Transfer Hooks:** Are transfer hook programs validated? Can a malicious hook block transfers (DoS)?
- [ ] **Transfer Fee:** Is transfer fee logic accounted for (amount received ≠ amount sent)?
- [ ] **Confidential Transfers:** Are zero-knowledge proof verifications correct?
- [ ] **Mint Close Authority:** Can the mint be closed unexpectedly?
- [ ] **Permanent Delegate:** Is permanent delegate authority properly scoped?
- [ ] **Non-Transferable:** Are non-transferable tokens (soul-bound) handled correctly in protocol logic?
- [ ] **Default Account State:** Is the default account state (frozen/initialized) appropriate?
- [ ] **Interest-Bearing Tokens:** Is the interest calculation accounted for in protocol math?

## 7. Clock & Time
- [ ] **Clock Drift:** Solana clock can drift. Don't rely on exact timestamps for critical logic.
- [ ] **Slot vs Timestamp:** Use `Clock::get()?.unix_timestamp` for time; `Clock::get()?.slot` for ordering.
- [ ] **Expiration:** Are time-sensitive operations (auctions, vesting) using appropriate time margins?

## 8. Hacker Mindset (Solana Edition)
- [ ] **Fake Accounts:** Can I inject a fake "SysVar" or "TokenAccount" that satisfies the type check but has malicious data?
- [ ] **Front-Running (MEV):** Solana has no mempool, but Jito/MEV exists. Are instructions atomic?
- [ ] **Lookup Tables:** Can Address Lookup Tables be manipulated to reference wrong accounts?
- [ ] **Versioned Transactions:** Are v0 transactions with ALTs handled correctly?
- [ ] **Compute Budget:** Can an attacker exhaust compute units to fail critical transactions?
