# Security Refactoring Guide

**Purpose**: Provide safe alternatives for common security vulnerabilities found in skills.

## 1. Dangerous Shell Patterns

### A. Pipe to Shell (`curl | bash`)
**Vulnerability**: Network interruption or Man-in-the-Middle can cause partial execution of malicious commands.
**Fix**: Two-step process (Download -> Execute).

**BAD:**
```bash
curl -sL https://example.com/install.sh | bash
```

**GOOD:**
```bash
# Download first
curl -sL https://example.com/install.sh -o /tmp/install.sh
# (Optional but recommended: Verify checksum)
# Execute
bash /tmp/install.sh
rm /tmp/install.sh
```

### B. Command Injection (`eval`, `exec`)
**Vulnerability**: User input can inject arbitrary commands.
**Fix**: Use `subprocess.run` with argument lists (never `shell=True` with user input).

**BAD (Python):**
```python
os.system(f"grep {pattern} {file}")
```

**GOOD (Python):**
```python
import subprocess
subprocess.run(["grep", pattern, file], check=True)
```

## 2. Information Leaks & Traversal

### A. Path Traversal
**Vulnerability**: User input can access files outside the intended directory (e.g., `../../etc/passwd`).
**Fix**: Validate paths use `os.path.abspath` and check common prefix.

**BAD:**
```python
with open(os.path.join("/var/data", user_input), 'r') as f: ...
```

**GOOD:**
```python
base_dir = os.path.abspath("/var/data")
target = os.path.abspath(os.path.join(base_dir, user_input))
if not target.startswith(base_dir):
    raise ValueError("Access denied")
```

### B. Hardcoded Secrets
**Vulnerability**: API keys committed to git are compromised.
**Fix**: Use Environment Variables.

**BAD:**
```python
API_KEY = "sk-1234567890"
```

**GOOD:**
```python
import os
API_KEY = os.getenv("MY_SKILL_API_KEY")
if not API_KEY:
    raise ValueError("Missing MY_SKILL_API_KEY environment variable")
```

### B. Temporary Files
**Vulnerability**: Sensitive data left in `/tmp` (world readable).
**Fix**: Use `tempfile` module with secure permissions.

**GOOD (Python):**
```python
import tempfile
with tempfile.NamedTemporaryFile(mode='w+', delete=True) as tf:
    tf.write(data)
    # process tf.name
```

## 3. Structural Compliance

### A. Weak Permissions
**Vulnerability**: Creating files with 777 permissions.
**Fix**: Use default (usually 644/755) or strict (600/700).

**BAD:**
```bash
chmod 777 my_script.sh
```

**GOOD:**
```bash
chmod +x my_script.sh # or chmod 755
```
