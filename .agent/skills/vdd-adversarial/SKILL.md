---
name: vdd-adversarial
description: "Use when performing Verification-Driven Development with adversarial approach. Actively challenge assumptions and find weak spots."
tier: 2
version: 1.0
---
# VDD Adversarial

## 1. Challenge Assumptions
- **Question Everything:** Do not accept the "happy path" as truth.
- **Input Validation:** What if input is null? Too long? Invalid chars?
- **State:** What if the DB is down? api is slow?

## 2. Decision Tree
1. **Is it clear?** -> If not, reject.
2. **Is it safe?** -> If not, reject.
3. **Does it break anything?** -> Check regression.

## 3. Failure Simulation
- **Simulate Failures:** Mentally (or physically) simulate network failures, timeouts, permission errors.
- **Check Error Handling:** Ensure graceful degradation.

## 4. Output Artifacts

If the User or Workflow requests a **Report**, **Critique**, or **Artifact**, you **MUST** use this standard template:

If the User or Workflow requests a **Report**, **Critique**, or **Artifact**, you **MUST** use the standard template found in:
`.agent/skills/vdd-adversarial/assets/template_critique.md`

Read this file using `read_resource` or `view_file` before generating the report.
