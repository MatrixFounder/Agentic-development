# High-Grade Solana Security Checklist

> **Framework:** Focus on Anchor, but applicable to raw Rust.

## 1. Account Validation (The "Missing Check" Problem)
- [ ] **Ownership:** Are all accounts checked for `owner == program_id` (unless explicitly external)?
- [ ] **Signer Checks:** Are sensitive actions (transfers, authority changes) gated by `is_signer` checks?
  - *Anchor:* Use `#[account(signer)]`.
- [ ] **Executable:** Are accounts correctly marked `executable` (or not)?

## 2. Arithmetic & numeric
- [ ] **Overflow/Underflow:** Is `overflow-checks = true` in `Cargo.toml`? (Default in modern Anchor).
- [ ] **Precision:** Are decimal calculations handled safely (e.g., multiply before divide)?
- [ ] **Casting:** usage of `try_from` or `safe_cast` instead of raw `as u64` (truncation risks)?

## 3. PDA (Program Derived Addresses)
- [ ] **Seeds Validation:** Are PDA bump seeds validated?
  - *Anchor:* `#[account(seeds = [...], bump)]` handles this. Manual checks MUST verify `find_program_address` matches.
- [ ] **Uniqueness:** Do seeds guarantee a unique account per user/state (avoid aliasing)?

## 4. Cross-Program Invocations (CPI)
- [ ] **Program ID Check:** Is the target program ID hardcoded or rigorously checked?
  - *Risk:* Calling a malicious "Token Program".
- [ ] **Privilege Escalation:** Does the PDA sign ONLY for what it owns?

## 5. Anchor Specifics (Soteria)
- [ ] **Init:** Is `init` used correctly to prevent re-initialization attacks?
- [ ] **Close:** Are closed accounts zeroed out or marked to prevent revival?
- [ ] **Big Space:** Are accounts with `space` > 10KB allocated using `zero_copy`?

## 6. Hacker Mindset (Solana Edition)
- [ ] **Fake Accounts:** Can I inject a fake "SysVar" or "TokenAccount" that satisfies the type check but has malicious data?
- [ ] **Front-Running (MEV):** Solana has no mempool, but Jito/MEV exists. Are instructions atomic?
