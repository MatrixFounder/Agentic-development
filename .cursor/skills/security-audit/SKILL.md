---
name: security-audit
description: Security vulnerability assessment (OWASP, secrets, dependencies).
version: 1.0
---
# Security Audit

## 1. Vulnerability Scan
- **Injections:** SQLi, XSS, Command Injection.
- **Auth:** Broken Access Control, Weak Passwords.
- **Secrets:** Hardcoded headers, keys, passwords.

## 2. Tooling Suggestions
- **Python:** `bandit`, `safety`
- **JS:** `npm audit`
- **General:** `semgrep`

## 3. Reporting
- **Critical:** Immediate Blocker.
- **High:** Must fix before release.
- **Medium/Low:** Backlog.
