---
description: Security Audit
---

**Description:**  
Comprehensive security review phase. Focuses on vulnerability scanning, best practices, and risk mitigation.  
Run after implementation (and optionally after VDD) for critical projects.

**Steps:**

1. **Gather Context**
   - Review docs/ARCHITECTURE.md, docs/TZ.md, and all modified source files
   - List dependencies (e.g., requirements.txt, package.json)

2. **Static Security Analysis**
   - Agent: Security Auditor
   - Prompt: Include System/Agents/00_agent_development.md + System/Agents/10_security_auditor.md
   - Analyze for:
     - Common vulnerabilities (OWASP Top 10)
     - Insecure patterns (hardcoded secrets, weak crypto, unsafe deserialization)
     - Dependency vulnerabilities (suggest audit commands)
     - Input validation, auth/session issues
   - Output: Detailed report with severity levels

3. **Security Review and Fixes**
   - If findings:
     a. Agent: Code Reviewer (standard check)
     b. Agent: Developer
        - Implement fixes + add security-focused tests (e.g., fuzzing, negative cases)
     c. Repeat Static Analysis until no Critical/High issues
   - Announce: "Security audit complete: All risks mitigated or documented"

4. **Documentation**
   - Save report as docs/SECURITY_AUDIT.md
   - Update .AGENTS.md with security notes
   - Recommend: Add to CI/CD (e.g., bandit, trivy scans)

**Completion:** Security-hardened code ready.
