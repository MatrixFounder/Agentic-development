# Security Audit Usage Example

This example demonstrates how to use the `security-audit` skill to identify and fix vulnerabilities in a project.

## Scenario: Auditing a Legacy Python/JS Project

**Context**: You've inherited a legacy codebase with an Express.js backend and Python data processing scripts. You need to ensure it's secure before deployment.

### Step 1: Automated Detection

**Action**: Run the unified audit script.

```bash
python3 .agent/skills/security-audit/scripts/run_audit.py . --output summary
```

**Output**:
```text
============================================================
Security Scan v3.12: /path/to/project
Timestamp: 2026-10-09T12:00:00
============================================================
Status: [!] HIGH RISK ISSUES
Total Findings: 3
  Critical: 0
  High: 3
  Medium: 0
  Low: 0
  Info: 0
Not run:
  - external python-sast: bandit not_installed
Tool exits:
  - semgrep exited 1 (sast)
============================================================

SECRETS: [!] HIGH: Secrets found
  - [HIGH] API Key in src/config.js:12
  - [HIGH] Password in .env.example:5

DEPENDENCIES: [OK] Secure

CODE_PATTERNS: [?] Patterns found
  - [HIGH] eval() usage in src/utils.js:45

EXTERNAL: PARTIAL
  - sast: semgrep ran (exit 1)
  - secrets-tree: gitleaks ran (exit 0)
  - secrets-history: gitleaks ran (exit 0)
  - python-sast: bandit not_installed
  - python-deps: pip-audit ran (exit 0)
  - npm-audit:package-lock.json: npm ran (exit 0)
```

The scan exits 3: bandit is not installed, so slot `python-sast` did not run, and stderr repeats
it under `[INCOMPLETE]`. semgrep exited 1, which is a finding or an error; its output on stderr
says which. With `--fail-on high`, the three high findings and the semgrep exit give exit 1
instead (`security-audit` §2, **Exit codes and summary**).

### Step 2: Analysis & "Think Like a Hacker"

**Refuse to rationalize away the findings.**

1.  **Secret in `src/config.js`**:
    *   *Bad Thought*: "It's just a test key."
    *   *Hacker Thought*: "I can use this to bill $10k to their account."
    *   *Action*: Rotate key, move to Environment Variables (Secrets Manager).

2.  **Password in `.env.example`**:
    *   *Bad Thought*: "It's an example file."
    *   *Hacker Thought*: "Developers often copy-paste this and forget to change it."
    *   *Action*: Remove actual values from examples.

3.  **`eval()` in `src/utils.js`**:
    *   *Bad Thought*: "It's only parsing internal JSON."
    *   *Hacker Thought*: "If I can inject a payload into that JSON, I have RCE."
    *   *Action*: Refactor to use `JSON.parse()`.

### Step 3: Verify Fixes

After applying fixes, run the scan again to confirm "Clean State".

```bash
python3 .agent/skills/security-audit/scripts/run_audit.py . --output summary
```

**Output**:
```text
Status: [OK] SECURE
Total Findings: 0
```

## Advanced: Supply Chain Attack Surface

When the tool reports `[OK]`, dig deeper manually (Adversarial Review):

1.  **Check `package.json` scripts**:
    *   Are there `preinstall` scripts running `curl | bash`?
2.  **Check `npm audit` manual run**:
    *   Are there "Low" severity issues that could be chained?

> **Rule of Thumb**: The script finds known bad patterns. YOU find the business logic flaws.
