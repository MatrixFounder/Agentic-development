# OWASP Top 10 (Web2) Checklist

1.  **Broken Access Control:**
    - [ ] Users cannot access other users' data (IDOR).
    - [ ] Admin endpoints are protected.

2.  **Cryptographic Failures:**
    - [ ] No hardcoded keys.
    - [ ] Use strong algorithms (Avoid MD5, SHA1).

3.  **Injection:**
    - [ ] SQL Injection (Use ORMs/Parameterized queries).
    - [ ] Command Injection (Avoid `subprocess.Popen` with `shell=True` on user input).

4.  **Insecure Design:**
    - [ ] Rate limiting implemented?
    - [ ] CAPTCHA on public forms?

5.  **Security Misconfiguration:**
    - [ ] Debug mode disabled?
    - [ ] Default credentials changed?

6.  **Vulnerable Components:**
    - [ ] Dependencies updated (`npm audit` / `safety check`).

7.  **Auth Failures:**
    - [ ] MFA supported?
    - [ ] Session timeout?

8.  **Integrity Failures:**
    - [ ] CI/CD pipeline secure?

9.  **Logging Failures:**
    - [ ] Critical actions logged?

10. **SSRF:**
    - [ ] Validate URLs fetched by backend.
