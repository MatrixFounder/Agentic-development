# OWASP Top 10:2025 Checklist

> **Source:** OWASP Top 10:2025 — https://owasp.org/Top10/2025/ (taxonomy verified against the primary source on 2026-06-10).
> **CWE Mapping:** Each category includes primary CWE references for compliance integration.
> **Renumbered from 2021:** A-numbers changed in 2025. Before reusing previously exported mappings (Jira/Snyk), see the 2021 → 2025 table at the end of this file.

## A01: Broken Access Control — CWE-284, CWE-639, CWE-918
- [ ] **Enforcement:** Is access denied by default (allowlist, not blocklist)?
- [ ] **IDOR:** Can User A access User B's resources by changing an ID? (CWE-639)
- [ ] **Path Traversal:** Can users access files outside intended directories? (CWE-22)
- [ ] **Forced Browsing:** Are admin/internal URLs protected beyond obscurity?
- [ ] **HTTP Method Tampering:** Can changing GET→DELETE bypass controls?
- [ ] **CORS:** Is it too permissive (`*`)? Is `Access-Control-Allow-Credentials` restricted?

### SSRF — absorbed into A01 in 2025 (was 2021-A10) — CWE-918
- [ ] **URL Allowlist:** Are user-supplied URLs validated against an allowlist of domains/IPs? (CWE-918)
- [ ] **Internal Network:** Is the server isolated from internal metadata services (AWS IMDS 169.254.169.254)?
- [ ] **DNS Rebinding:** Are DNS resolution results cached and validated?
- [ ] **Protocol Restriction:** Are only HTTP/HTTPS protocols allowed (no `file://`, `gopher://`)?
- [ ] **Redirect Following:** Are HTTP redirects to internal resources blocked?
- [ ] **Response Filtering:** Is the response from fetched URLs sanitized before returning to the user?

## A02: Security Misconfiguration — CWE-16, CWE-611
- [ ] **Hardening:** Are unused features/ports/services disabled?
- [ ] **Headers:** Are security headers configured (`CSP`, `HSTS`, `X-Frame-Options`, `X-Content-Type-Options`)?
- [ ] **XML External Entities:** Is XXE disabled in XML parsers? (CWE-611)
- [ ] **Default Credentials:** Are all default passwords/keys changed?
- [ ] **Directory Listing:** Is directory listing disabled on web servers?
- [ ] **Cloud Config:** Are S3 buckets, storage accounts, and security groups properly restricted?

> Stack-trace / verbose-error leakage (CWE-209) moved to **A10** in 2025.

## A03: Software Supply Chain Failures — CWE-1104, CWE-829, CWE-494
- [ ] **SCA Scanning:** Is automated Software Composition Analysis running in CI?
- [ ] **Dependency Audit:** Is `npm audit` / `cargo audit` / `pip-audit` clean?
- [ ] **End-of-Life:** Are we using EOL OS, runtimes, or libraries?
- [ ] **Pinned Versions:** Are dependencies pinned to specific versions (not ranges)?
- [ ] **Lock Files:** Are `package-lock.json` / `Cargo.lock` / `poetry.lock` committed?
- [ ] **CI/CD Pipeline:** Is the build pipeline secured against tampering (signed commits, protected branches)?
- [ ] **Code Signing:** Are releases and packages signed?
- [ ] **License Compliance:** Are dependency licenses compatible with project requirements?
- [ ] **SBOM:** Is a Software Bill of Materials generated and maintained?

## A04: Cryptographic Failures — CWE-259, CWE-327, CWE-331
- [ ] **Transmission:** Is TLS 1.3 enforced? Is HSTS enabled with `includeSubDomains`?
- [ ] **Storage:** Are passwords hashed (Argon2id/bcrypt, NOT MD5/SHA1)?
- [ ] **Secrets:** Are keys hardcoded? (Use `run_audit.py` to check). (CWE-798)
- [ ] **Randomness:** Is `Math.random()` used for crypto? (Use `crypto.getRandomValues`). (CWE-338)
- [ ] **Key Management:** Are encryption keys rotated? Is key material stored in a vault?
- [ ] **Data Classification:** Is PII/sensitive data identified and encrypted at rest?

## A05: Injection — CWE-79, CWE-89, CWE-78
- [ ] **SQL Injection:** Are all queries parameterized (no string concatenation)? (CWE-89)
- [ ] **XSS:** Is user input escaped in HTML output? Is CSP configured? (CWE-79)
- [ ] **Command Injection:** Is user input passed to shell commands? (CWE-78)
- [ ] **LDAP/NoSQL Injection:** Are non-SQL data stores also using parameterized queries?
- [ ] **Template Injection (SSTI):** Is user input rendered in server-side templates? (CWE-1336)
- [ ] **Header Injection:** Can user input be injected into HTTP headers? (CWE-113)

## A06: Insecure Design — CWE-256, CWE-501, CWE-657
- [ ] **Threat Modeling:** Was a threat model created for this feature?
- [ ] **Rate Limiting:** Is it implemented to prevent abuse?
- [ ] **Logic Flaws:** Are business flows protected against manipulation (e.g., buying negative quantity)?
- [ ] **Secure Defaults:** Are security features enabled by default (not opt-in)?
- [ ] **Attack Surface:** Is the attack surface minimized? Are unused features disabled?

## A07: Authentication Failures — CWE-287, CWE-384
*(renamed in 2025; was "Identification and Authentication Failures")*
- [ ] **MFA:** Is Multi-Factor Authentication available/enforced for sensitive operations?
- [ ] **Sessions:** Do sessions expire (both absolute and idle timeout)?
- [ ] **Brute Force:** Is there lockout/delay logic after failed attempts? (CWE-307)
- [ ] **Password Policy:** Are minimum length, complexity, and breach-list checks enforced?
- [ ] **Session Fixation:** Are session IDs regenerated after authentication? (CWE-384)
- [ ] **Credential Recovery:** Is the password reset flow secure (time-limited tokens, no user enumeration)?

## A08: Software or Data Integrity Failures — CWE-502, CWE-345
*(renamed in 2025; supply-chain items re-homed to A03)*
- [ ] **Deserialization:** Is user data deserialized unsafely (pickle, Java serialization)? (CWE-502)
- [ ] **Verification:** Are signatures verified for external artifacts and updates? (CWE-345)
- [ ] **Unsigned Updates:** Is there an auto-update mechanism without signature verification?
- [ ] **Untrusted Sources:** Are plugins/models/extensions loaded only from trusted, verified origins? (CWE-829 — provenance/pinning concerns belong to A03)

## A09: Security Logging and Alerting Failures — CWE-778
*(renamed in 2025; was "Security Logging and Monitoring Failures")*
- [ ] **Audit Trail:** Are login, access control, and failure events logged?
- [ ] **Protection:** Are logs protected from tampering (append-only, centralized)?
- [ ] **Alerting:** Do critical failures trigger real-time alerts (SIEM integration)?
- [ ] **Sensitive Data:** Are secrets, tokens, and PII excluded from logs?
- [ ] **Retention:** Are logs retained for a sufficient period for incident response?
- [ ] **Correlation:** Can logs be correlated across services (trace IDs)?

## A10: Mishandling of Exceptional Conditions — CWE-209, CWE-390, CWE-754, CWE-636
*(NEW in 2025)*
- [ ] **Error Messages:** Do stack traces or internal details leak to users? (Disable `DEBUG` mode). (CWE-209)
- [ ] **Fail-Closed:** Do security controls (authn/authz, validation) fail closed when they error? (CWE-636)
- [ ] **Unchecked Returns:** Are return values and error codes checked and acted upon? (CWE-252, CWE-754)
- [ ] **Swallowed Exceptions:** Are there empty catch blocks or logged-and-ignored errors on security-relevant paths? (CWE-390)
- [ ] **Resource Cleanup:** Are resources (locks, handles, transactions) released on error paths (`finally`/`defer`/context managers)? (CWE-404, CWE-772)
- [ ] **Partial Failure:** Do multi-step operations roll back to a consistent state when an intermediate step fails? (CWE-460)

---

## 2021 → 2025 Mapping (for previously exported compliance references)

| 2021 | 2025 | Change |
|---|---|---|
| A01 Broken Access Control | A01 | unchanged #1; absorbs 2021-A10 (SSRF) |
| A02 Cryptographic Failures | A04 | renumbered ↓ |
| A03 Injection | A05 | renumbered ↓ |
| A04 Insecure Design | A06 | renumbered ↓ |
| A05 Security Misconfiguration | A02 | renumbered ↑; CWE-209 check re-homed to A10 |
| A06 Vulnerable and Outdated Components | A03 Software Supply Chain Failures | broadened + renamed; absorbs supply-chain items of 2021-A08 |
| A07 Identification and Authentication Failures | A07 Authentication Failures | renamed |
| A08 Software and Data Integrity Failures | A08 Software **or** Data Integrity Failures | renamed; CI/CD + code-signing + dep-audit items → A03 |
| A09 Security Logging and Monitoring Failures | A09 Security Logging and **Alerting** Failures | renamed |
| A10 Server-Side Request Forgery (SSRF) | — | merged into A01 |
| — | A10 Mishandling of Exceptional Conditions | **NEW** in 2025 |
