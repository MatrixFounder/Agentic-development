---
name: security-audit
description: "Use when performing security vulnerability assessment (OWASP, secrets, dependencies)."
tier: 2
version: 1.0
---
# Security Audit

## 1. Automated Detection
- **Execution:** You MUST run the unified audit script to detect vulnerabilities:
  ```bash
  python3 .agent/skills/security-audit/scripts/run_audit.py
  ```
- **Analysis:** Review the output. If tools fail or report Critical/High issues, they are **BLOCKERS**.

## 2. "Think Like a Hacker" Review
Refuse to merge/approve until you have manually verified the code against the relevant checklist in `references/checklists/`.

### 🛡️ Smart Contracts (Solidity)
**MANDATORY:** Read `references/checklists/solidity_security.md`.
- **Top 3 Checks:**
  1. **Reentrancy:** Are checks-effects-interactions followed? `nonReentrant` used?
  2. **Price Manipulation:** Are spot prices used? (Use Oracles).
  3. **Access Control:** Who owns the contract? Timelocks?

### 🦀 Smart Contracts (Solana/Rust)
**MANDATORY:** Read `references/checklists/solana_security.md`.
- **Top 3 Checks:**
  1. **Account Validation:** Are ALL accounts checked for ownership and signer status?
  2. **PDA bumps:** Are bumps strictly validated (Anchor does this, raw Rust often fails)?
  3. **Arithmetic:** Is `overflow_checks` on? Checked math used?

### 🌐 Web/API (Python/JS)
**MANDATORY:** Read `references/checklists/owasp_top_10.md`.
- Check for Injections, Auth flaws, and Secrets.

## 3. Reporting
- **Critical:** Immediate Blocker. (Money at risk, Data leak).
- **High:** Must fix before release.
- **Medium/Low:** Document in `open_questions.md` or Backlog.
