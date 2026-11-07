# Usage Example: Adversarial Critique

## Input

The Builder submits a user authentication function:

```python
def login(username, password):
    user = db.get_user(username)
    if user and user.password == password:
        return create_session(user)
    return None
```

## Adversarial Critique (using `assets/template_critique.md`)

### 1. Executive Summary
- **Verdict**: FAIL
- **Confidence**: High
- **Summary**: One critical and two further security flaws in authentication logic: plaintext password comparison, no rate limiting, a timing attack. No test run was handed over.

### 2. Test Evidence (Exit Bar)
- **Command**: none
- **Result**: `NOT RUN (snippet submitted without tests)`
- **Source**: none: nothing handed over, nothing run
- **Tree state**: absent

### 3. Risk Analysis

Lines are counted in the submitted snippet (l.1 = `def login`).

| Severity | Confidence | Category | Issue | Impact | Recommendation | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CRITICAL** | High | Security | Plaintext password comparison, l.3 | Credential theft if DB is compromised | Store a bcrypt/argon2 hash and compare with the library's verify call | Test: the stored value is a hash; a correct password logs in, a wrong one does not |
| **HIGH** | High | Process | exit-bar condition unverifiable — test run NOT RUN (snippet submitted without tests) | No evidence that any path works | Submit the function with its tests | The test run's output is handed over with the next review |
| **HIGH** | Medium | Security | No rate limiting, l.1 (may exist in middleware outside the snippet) | Brute-force attacks | Add exponential backoff after N failures | Test: after N failures, each next attempt waits longer than the one before |
| **MEDIUM** | Medium | Security | Timing attack on `==`, l.3 | Password length leak | Use `hmac.compare_digest()` (or the hash library's verify call) | Review: no `==` on a secret remains |
| **MEDIUM** | Medium | Logic | `None` return hides the failure reason from the code, l.5 | Callers and logs cannot tell "user not found" from "wrong password" | Distinguish the two internally (typed error or log); keep the client response generic | Test: both failures return the same client response and log different reasons |
| **LOW** | High | Resilience | No DB error handling, l.2 | Unhandled exception if DB is down | Wrap in try/except with graceful degradation | Test: a DB error yields a controlled failure, not a traceback |

### 4. Hallucination Check
- [x] **Files**: No external files cited.
- [x] **Line Numbers**: Code reviewed matches submitted snippet.
