# OWASP Top 10:2025 Checklist

> **Source:** OWASP Top 10:2025 (Final Release, Q4 2025).
> **CWE Mapping:** Each category includes primary CWE references for compliance integration.

## A01: Broken Access Control — CWE-284, CWE-639, CWE-918
- [ ] **Enforcement:** Is access denied by default (allowlist, not blocklist)?
- [ ] **IDOR:** Can User A access User B's resources by changing an ID? (CWE-639)
- [ ] **SSRF:** Are external resource fetches validated against an allowlist? (CWE-918)
- [ ] **CORS:** Is it too permissive (`*`)? Is `Access-Control-Allow-Credentials` restricted?
- [ ] **Path Traversal:** Can users access files outside intended directories? (CWE-22)
- [ ] **Forced Browsing:** Are admin/internal URLs protected beyond obscurity?
- [ ] **HTTP Method Tampering:** Can changing GET→DELETE bypass controls?

## A02: Cryptographic Failures — CWE-259, CWE-327, CWE-331
- [ ] **Transmission:** Is TLS 1.3 enforced? Is HSTS enabled with `includeSubDomains`?
- [ ] **Storage:** Are passwords hashed (Argon2id/bcrypt, NOT MD5/SHA1)?
- [ ] **Secrets:** Are keys hardcoded? (Use `run_audit.py` to check). (CWE-798)
- [ ] **Randomness:** Is `Math.random()` used for crypto? (Use `crypto.getRandomValues`). (CWE-338)
- [ ] **Key Management:** Are encryption keys rotated? Is key material stored in a vault?
- [ ] **Data Classification:** Is PII/sensitive data identified and encrypted at rest?

## A03: Injection — CWE-79, CWE-89, CWE-78
- [ ] **SQL Injection:** Are all queries parameterized (no string concatenation)? (CWE-89)
- [ ] **XSS:** Is user input escaped in HTML output? Is CSP configured? (CWE-79)
- [ ] **Command Injection:** Is user input passed to shell commands? (CWE-78)
- [ ] **LDAP/NoSQL Injection:** Are non-SQL data stores also using parameterized queries?
- [ ] **Template Injection (SSTI):** Is user input rendered in server-side templates? (CWE-1336)
- [ ] **Header Injection:** Can user input be injected into HTTP headers? (CWE-113)

## A04: Insecure Design — CWE-209, CWE-256, CWE-501
- [ ] **Threat Modeling:** Was a threat model created for this feature?
- [ ] **Rate Limiting:** Is it implemented to prevent abuse?
- [ ] **Logic Flaws:** Are business flows protected against manipulation (e.g., buying negative quantity)?
- [ ] **Secure Defaults:** Are security features enabled by default (not opt-in)?
- [ ] **Attack Surface:** Is the attack surface minimized? Are unused features disabled?

## A05: Security Misconfiguration — CWE-16, CWE-611
- [ ] **Hardening:** Are unused features/ports/services disabled?
- [ ] **Error Messages:** Do stack traces leak to users? (Disable `DEBUG` mode). (CWE-209)
- [ ] **Headers:** Are security headers configured (`CSP`, `HSTS`, `X-Frame-Options`, `X-Content-Type-Options`)?
- [ ] **XML External Entities:** Is XXE disabled in XML parsers? (CWE-611)
- [ ] **Default Credentials:** Are all default passwords/keys changed?
- [ ] **Directory Listing:** Is directory listing disabled on web servers?
- [ ] **Cloud Config:** Are S3 buckets, storage accounts, and security groups properly restricted?

## A06: Vulnerable and Outdated Components — CWE-1104
- [ ] **SCA Scanning:** Is automated Software Composition Analysis running in CI?
- [ ] **End-of-Life:** Are we using EOL OS, runtimes, or libraries?
- [ ] **Pinned Versions:** Are dependencies pinned to specific versions (not ranges)?
- [ ] **Lock Files:** Are `package-lock.json` / `Cargo.lock` / `poetry.lock` committed?
- [ ] **License Compliance:** Are dependency licenses compatible with project requirements?
- [ ] **SBOM:** Is a Software Bill of Materials generated and maintained?

## A07: Identification and Authentication Failures — CWE-287, CWE-384
- [ ] **MFA:** Is Multi-Factor Authentication available/enforced for sensitive operations?
- [ ] **Sessions:** Do sessions expire (both absolute and idle timeout)?
- [ ] **Brute Force:** Is there lockout/delay logic after failed attempts? (CWE-307)
- [ ] **Password Policy:** Are minimum length, complexity, and breach-list checks enforced?
- [ ] **Session Fixation:** Are session IDs regenerated after authentication? (CWE-384)
- [ ] **Credential Recovery:** Is the password reset flow secure (time-limited tokens, no user enumeration)?

## A08: Software and Data Integrity Failures — CWE-502, CWE-829
- [ ] **Dependencies:** Is `npm audit` / `cargo audit` / `pip-audit` clean?
- [ ] **CI/CD Pipeline:** Is the build pipeline secured against tampering (signed commits, protected branches)?
- [ ] **Verification:** Are signatures verified for external artifacts and updates?
- [ ] **Deserialization:** Is user data deserialized unsafely (pickle, Java serialization)? (CWE-502)
- [ ] **Code Signing:** Are releases and packages signed?
- [ ] **Unsigned Updates:** Is there an auto-update mechanism without signature verification?

## A09: Security Logging and Monitoring Failures — CWE-778
- [ ] **Audit Trail:** Are login, access control, and failure events logged?
- [ ] **Protection:** Are logs protected from tampering (append-only, centralized)?
- [ ] **Alerting:** Do critical failures trigger real-time alerts (SIEM integration)?
- [ ] **Sensitive Data:** Are secrets, tokens, and PII excluded from logs?
- [ ] **Retention:** Are logs retained for a sufficient period for incident response?
- [ ] **Correlation:** Can logs be correlated across services (trace IDs)?

## A10: Server-Side Request Forgery (SSRF) — CWE-918
- [ ] **URL Allowlist:** Are user-supplied URLs validated against an allowlist of domains/IPs?
- [ ] **Internal Network:** Is the server isolated from internal metadata services (AWS IMDS 169.254.169.254)?
- [ ] **DNS Rebinding:** Are DNS resolution results cached and validated?
- [ ] **Protocol Restriction:** Are only HTTP/HTTPS protocols allowed (no `file://`, `gopher://`)?
- [ ] **Redirect Following:** Are HTTP redirects to internal resources blocked?
- [ ] **Response Filtering:** Is the response from fetched URLs sanitized before returning to the user?
