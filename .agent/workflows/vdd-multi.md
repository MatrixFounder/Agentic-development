---
description: VDD Multi-Adversarial - Sequential multi-critic verification
---

# Workflow: VDD Multi-Adversarial

**Description:**  
Sequential execution of multiple specialized adversarial critics for maximum code quality.

**Critics Pipeline:**
```
vdd-multi
 ├── Phase 1: skill-vdd-adversarial (General Logic)
 ├── Phase 2: skill-adversarial-security (OWASP)
 └── Phase 3: skill-adversarial-performance (Performance)
```

---

## Steps

### 1. General Logic Review
Apply **`skill-vdd-adversarial`** to review:
- Edge cases and error handling
- Input validation
- State management
- Business logic correctness

**Loop:** If issues found → fix → re-run until clean or hallucinating.

---

### 2. Security Review
Apply **`skill-adversarial-security`** to review:
- Injection attacks (SQLi, XSS, Command)
- Authentication & Authorization flaws
- Secrets exposure
- Data protection

**Loop:** If issues found → fix → re-run until clean or hallucinating.

---

### 3. Performance Review
Apply **`skill-adversarial-performance`** to review:
- N+1 queries, missing indexes
- Memory leaks, unbounded allocations
- Blocking async, missing pooling
- Algorithm complexity

**Loop:** If issues found → fix → re-run until clean or hallucinating.

---

## Termination Criteria

Each phase terminates when:
1. **Clean pass:** No real issues found
2. **Hallucination detected:** Critic inventing non-existent problems
3. **Diminishing returns:** Only micro-optimizations remain

**Final Announcement:**
> "VDD Multi-Adversarial complete: Logic ✓ Security ✓ Performance ✓"

---

## Integration

This workflow can be called from:
- `/full-robust` — after base implementation
- Directly via `/vdd-multi` — for existing code review

**Prerequisite:** Code must be implemented and functional before running this workflow.
