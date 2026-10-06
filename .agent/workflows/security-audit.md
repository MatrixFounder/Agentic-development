---
description: Security Audit
contract:
  version: 1
  loops:
    - id: audit-remediation
      what: fix -> re-run the audit script until clean
      site: "<!-- loop:audit-remediation -->"
      default_max: 3
      override: allowed
      on_exhaust: escalate_user
  calls: []
---

**Description:**
Comprehensive security review phase. Focuses on vulnerability scanning, best practices, and risk mitigation.
Run after implementation (and optionally after VDD-Adversarial) for critical projects.

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "security-audit-<task-slug>"` (non-blocking; exit 6 = an outer workflow of this task owns this run's retro — fine, continue; an owner from another task is a stale claim — run-feedback §7 Retro step 1).

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
   - **If you cannot execute it** (no execution tool in your role, or the environment refuses):
     record `scan_status: NOT_RUN (<reason>)`, continue to step 3, and carry that status into the
     report. **Never invent the output** (`security-audit` §1). `NOT_RUN` makes the audit
     `INCOMPLETE`, or `FAIL` when step 3 finds a CRITICAL or HIGH issue, never `PASS` — step 4's "until clean" loop cannot be satisfied by a scan that
     never ran.

3. **Manual Adversarial Review ("Think Like a Hacker")**
   - Refer to `.agent/skills/security-audit/SKILL.md` Section 3.
   - Verify against specific checklists (Solidity, Rust, OWASP).
   - Challenge assumptions (Input Validation, AuthZ, Secrets).
   - A review that does not run to completion makes the audit `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH issue:
     name the part. The orchestrator re-runs it once, then the operator decides (`security-audit`
     §6.2).

4. **Remediation & Reporting**
   - If findings exist:
     a. Fix implementation (apply patches, rotate secrets).
     b. Add regression tests (security-focused).
     <!-- loop:audit-remediation -->
     c. Re-run audit script until clean. **Bound: max 3 iterations** when this workflow is entered
        directly; a caller may re-scope both the cap and the definition of "clean" (`full-robust`
        §3 does exactly that). On exhaustion with findings still open → **STOP** and escalate the
        open findings to the user. Per step 2, a `scan_status: NOT_RUN` never satisfies this loop:
        the verdict is `INCOMPLETE` or `FAIL`, not clean, and `security-audit` §6.2 governs its one
        re-run.
   - Save report as `docs/audit/security-{ID}.md` (consistent with `security-auditor` agent and `skill-archive-task` ID convention).
   - A finding in a dependency with no public advisory goes to its maintainers privately. The patches of 4a, the tests of 4b, the saved report, the `.AGENTS.md` notes and the retro records hold no detail of it; a test pins this project's mitigation, never the defect (`security-audit` §6.1).
   - Update `.AGENTS.md` with security notes.

5. **Reference resolver (gate)** — run `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --targets-changed`.
   It selects documents **citing** the files this change touched; default diff scope
   selects documents the change *edited*, so a source-only commit checks nothing while
   being exactly the commit that shifts the cited lines. `REFERENT_MOVED` is repaired
   mechanically. A coordinate carrying no referent is reported as
   *not examined* and is **not** a defect (`documentation-standards` §4.1).

6. **Retro (Global Protocol)** — apply `run-feedback` SKILL.md §7 "Retro protocol":
   `claim --run-id "security-audit-<task-slug>"` → exit 6 = nested, SKIP this step (unless the owner is another task's run — a stale claim, run-feedback §7 Retro step 1);
   exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
   from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
   collect → triage → file per the skill, and `release`. **Non-blocking**: failures
   here are reported in one line and never change this workflow's outcome.

**Completion:** Security-hardened code ready for final review.
