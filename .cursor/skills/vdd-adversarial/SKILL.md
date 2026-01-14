---
name: vdd-adversarial
description: Verification-Driven Development with adversarial approach. Actively challenge assumptions and find weak spots.
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
