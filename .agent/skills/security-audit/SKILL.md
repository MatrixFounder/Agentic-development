---
name: security-audit
description: Use when performing security vulnerability assessment (OWASP, secrets, dependencies, IaC, LLM, API) or when "thinking like a hacker" to find exploits.
tier: 2
version: 3.2
---

# Security Audit v3.2

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I'll skip the script because I just checked the code manually" -> **WRONG**. Humans miss regex patterns. **EXECUTE** the script.
- "This is an internal tool, so AuthZ doesn't matter" -> **WRONG**. Zero Trust applies everywhere.
- "Dependencies are probably fine" -> **WRONG**. Supply chain attacks are the #1 vector.
- "I don't have time for a full audit" -> **WRONG**. Breach cleanup takes 100x longer.
- "The LLM output is safe to use directly" -> **WRONG**. LLM output is untrusted input. Sanitize it.

## 2. Automated Detection
**EXECUTE** the unified audit script to detect vulnerabilities:
```bash
python3 .agent/skills/security-audit/scripts/run_audit.py [project_path] [--scan-type all|deps|secrets|patterns|config|iac|sbom|external] [--fail-on critical|high|medium] [--output json|summary] [--no-limit]
```
- **Analysis**: Review the output. If tools fail or report Critical/High issues, they are **BLOCKERS**.
- **Scope**: The script checks:
  - Secrets (OWASP A02, CWE-798) — 30+ patterns including cloud, AI, SaaS keys + entropy detection
  - Dependencies (A06/A08, CWE-1104) — lock files, npm audit
  - Code Patterns / Injection (A03, CWE-79/89/78) — eval, XSS, SQLi, SSTI, SSRF, path traversal, prototype pollution, deserialization
  - **Smart Contract / Solidity** — reentrancy, delegatecall, selfdestruct (EIP-6780), tx.origin, oracle manipulation, unchecked returns, unprotected initializers
  - Config / Misconfiguration (A05, CWE-16) — debug mode, CORS, headers
  - IaC / Containers — Docker, Kubernetes, Terraform, CloudFormation patterns
  - SBOM — Software Bill of Materials presence check
- **External Tools**: Auto-runs `slither`, `bandit`, `pip-audit`, `npm audit`, `cargo audit`, `govulncheck`, `checkov`, `trivy` if detected.
- **CI/CD Gate**: Use `--fail-on critical` to exit with code 1 in CI pipelines.
- **Self-Exclusion**: The scanner skips its own source files to prevent false positives.
- **CWE Mapping**: All findings include CWE identifiers for compliance integration.
- **Known Limitation**: The scanner uses **regex-only** (no AST parsing). It WILL match patterns inside comments, docstrings, and string literals. This is a deliberate trade-off: false positives on comments are preferable to false negatives on real vulnerabilities. Always **manually verify** findings before acting.

## 3. "Think Like a Hacker" (Adversarial Review)

**Refuse to merge/approve until you have manually verified the code against the relevant checklist.**

### Smart Contracts (Solidity)
**MANDATORY:** Read `references/checklists/solidity_security.md`.
**Top Checks:**
1. **Reentrancy**: Are checks-effects-interactions followed? `nonReentrant` used?
2. **Access Control**: Who owns the contract? `onlyOwner` checks? Two-step transfer?
3. **Price Manipulation**: Are spot prices used? (Use Oracles + TWAP).
4. **EIP-6780**: `selfdestruct` semantics changed post-Dencun — accounted for?
5. **ERC-4337**: Account Abstraction validation and paymaster checks.
6. **Fuzzing**: See `references/checklists/fuzzing_invariants.md`.

### Smart Contracts (Solana/Rust)
**MANDATORY:** Read `references/checklists/solana_security.md`.
**Top Checks:**
1. **Account Validation**: Are ALL accounts checked for ownership and signer status?
2. **PDA bumps**: Are bumps strictly validated (canonical bump)?
3. **Arithmetic**: Is `overflow_checks` on? Using `checked_*` methods?
4. **Token-2022**: Are transfer hooks, fees, and extensions handled correctly?
5. **CPI Guard**: Is CPI Guard used where appropriate?

### Web/API (OWASP Top 10:2025)
**MANDATORY:** Read `references/checklists/owasp_top_10.md`.
**Top Checks:**
1. **Broken Access Control (A01)**: Can user A access user B's data? (IDOR, SSRF).
2. **Injection (A03)**: Are queries parameterized? Is output escaped?
3. **SSRF (A10)**: Are user-supplied URLs validated against allowlist?

### API Security (OWASP API Top 10:2023)
**MANDATORY:** Read `references/checklists/api_security.md`.
**Top Checks:**
1. **BOLA (API1)**: Object-level authorization on every endpoint?
2. **BOPLA (API3)**: Mass assignment prevention? Excessive data exposure?
3. **Rate Limiting (API4)**: Per-user, per-endpoint rate limits?

### AI/LLM Applications (OWASP LLM Top 10 v2.0)
**MANDATORY:** Read `references/checklists/llm_security.md`.
**Top Checks:**
1. **Prompt Injection (LLM01)**: Can user input override system prompts?
2. **Insecure Output Handling (LLM02)**: Is LLM output sanitized before use in HTML/SQL/shell?
3. **Excessive Agency (LLM06)**: Does the agent have minimal permissions? Human-in-the-loop for destructive actions?
4. **Supply Chain (LLM05)**: Are models from trusted sources? Plugins verified?

## 4. Threat Modeling
Before declaring "Secure", perform lightweight threat modeling:
**MANDATORY:** Read `references/checklists/threat_model.md`.
1. **STRIDE Analysis**: Evaluate each component for Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege.
2. **DREAD Scoring**: Rate each threat by Damage, Reproducibility, Exploitability, Affected Users, Discoverability.
3. **Attack Surface Mapping**:
   - **Entry Points**: APIs, forms, file uploads, webhooks, LLM interfaces.
   - **Data Flows**: Where does user input go? (Logs? DB? Shell? LLM prompt?).
   - **Assets**: Secrets, PII, Money, Model weights.
   - **Trust Boundaries**: Internet <-> DMZ <-> Internal <-> AI/Agent scope.

## 5. Secret Remediation
When secrets are found:
**MANDATORY:** Read `references/checklists/secret_rotation.md`.
1. **Rotate immediately** — the secret is compromised.
2. **Clean git history** — BFG or git-filter-repo.
3. **Prevent recurrence** — pre-commit hooks (gitleaks/trufflehog).

## 6. Reporting
- **Critical**: Immediate Blocker (RCE, Auth Bypass, Secrets Exposed, Prompt Injection). **Fix immediately**.
- **High**: Must fix before release (XSS, CSRF, Dep Vulns, SSRF, Mass Assignment).
- **Medium**: Document in Backlog (Missing headers, weak crypto, best practices).

All findings include **CWE identifiers** for integration with vulnerability management systems (Jira, Snyk, Sonar).

## 7. Rationalization Table

| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "The script reported [OK], so it's clean" | Check `skipped_files` count. Silent skips = false negatives. |
| "This is a test/dev environment" | Attackers pivot from dev to prod. Zero Trust applies everywhere. |
| "Dependencies are only dev dependencies" | `devDependencies` run during build. Supply chain attacks don't discriminate. |
| "The flag is a false positive" | Verify manually. Never dismiss without proof. |
| "I'll fix it later" | Later = Never. Critical/High = Blocker NOW. |
| "The LLM generated this code, it's fine" | LLMs hallucinate vulnerabilities. Treat output as untrusted. |
| "The IaC is only for staging" | Staging configs often get copy-pasted to production. Secure from day one. |
| "We don't need an SBOM" | EU Cyber Resilience Act and US EO 14028 require it. Regulators disagree. |
