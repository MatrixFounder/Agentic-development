---
description: Security Audit
---

**Description:**
Comprehensive security review phase. Focuses on vulnerability scanning, best practices, and risk mitigation.
Run after implementation (and optionally after VDD-Adversarial) for critical projects.

**Steps:**

1. **Gather Context**
   - Review `docs/ARCHITECTURE.md`, `docs/TASK.md`, and all modified source files.
   - List dependencies (e.g., `requirements.txt`, `package.json`).

2. **Automated Security Scan**
   - **EXECUTE** the unified audit script:
     ```bash
     python3 .agent/skills/security-audit/scripts/run_audit.py . --scan-type all
     ```
   - Analyze output for Critical/High issues (BLOCKERS).

3. **Manual Adversarial Review ("Think Like a Hacker")**
   - Refer to `.agent/skills/security-audit/SKILL.md` Section 3.
   - Verify against specific checklists (Solidity, Rust, OWASP).
   - Challenge assumptions (Input Validation, AuthZ, Secrets).

4. **Remediation & Reporting**
   - If findings exist:
     a. Fix implementation (apply patches, rotate secrets).
     b. Add regression tests (security-focused).
     c. Re-run audit script until clean.
   - Save report as `docs/SECURITY_AUDIT.md`.
   - Update `.AGENTS.md` with security notes.

**Completion:** Security-hardened code ready for final review.
