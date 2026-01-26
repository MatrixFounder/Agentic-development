# Usage Example: Enhancing a Legacy Skill

**Scenario**: You ran a **Pressure Test** (TDD Red Phase) and the agent failed to use the logger, claiming "it's too simple to need logging". You invoke `skill-enhancer` to fix this.

## 1. Audit (Phase 1)
**Input:**
```bash
python3 .agent/skills/skill-enhancer/scripts/analyze_gaps.py .agent/skills/skill-legacy-logger
```

**Output:**
```text
⚠️  Gaps Detected for 'skill-legacy-logger':
  - [CSO] Description does not start with 'Use when...'
  - [Resilience] Missing 'Red Flags' section
  - [Resilience] Missing 'Rationalization Table'
  - [Deep Logic] Found passive wording: ['should', 'suggested']. Rewrite to Imperative.
```

## 2. Plan & Execute (Phases 2-3)

**Action**: You rewrite the description and add the missing sections to address the specific excuse ("too simple") found during pressure testing.

**Before (SKILL.md):**
```markdown
description: A tool for logging variables.
...
You should use the logger to debug.
It is suggested to log errors.
```

**After (SKILL.md):**
```markdown
description: Use when debugging complex state changes, race conditions, or persisting errors.
...
## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I'll just print to stdout" -> **WRONG**. Use the structured logger for persistence.
- "This function is too simple to log" -> **WRONG**. Simple functions are where silent failures hide.

## Instructions
1. **Import** the logger module immediately.
2. **Execute** `logger.info()` at the start of the transaction.
3. **IF** error occurs:
    *   **CALL** `logger.error(e)`.
    *   **RAISE** the exception (do not swallow).

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "It's just a quick script" | Scripts become production code. Log from day one. |
| "I'll add logs if it breaks" | You won't have info *why* it broke unless you log now. |
```

## 3. Verify
**Input:**
```bash
python3 .agent/skills/skill-enhancer/scripts/analyze_gaps.py .agent/skills/skill-legacy-logger
```

**Output:**
```text
✅ No Gaps Found for 'skill-legacy-logger'. Skill is Gold Standard compliant.
```