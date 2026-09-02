# Usage Example: Enhancing a Legacy Skill

**Scenario**: You ran a **Pressure Test** (TDD Red Phase) and the agent failed to use the logger, claiming "it's too simple to need logging". You invoke `skill-enhancer` to fix this.

## 1. Audit (Phase 1)
**Input:**
```bash
python3 .agent/skills/skill-enhancer/scripts/analyze_gaps.py .agent/skills/skill-legacy-logger
```

**Output:** two blocks, and the split matters. `gaps` decide the exit code;
`advisories` are reported and leave it at 0 (`--strict` promotes them).

```text
⚠️  Gaps Detected for 'skill-legacy-logger':
  - [Resilience] Missing 'Red Flags' section
  - [Resilience] Missing 'Rationalization Table' section
  - [Richness] Missing or empty 'examples/' directory
ℹ️  Advisories for 'skill-legacy-logger' (do not fail the gate):
  - [Execution Policy] Missing 'Execution Mode' section (warning-first migration target).
  - [Execution Policy] Missing 'Script Contract' section (warning-first migration target).
  - [Execution Policy] Missing 'Safety Boundaries' section (warning-first migration target).
  - [Execution Policy] Missing 'Validation Evidence' section (warning-first migration target).
  - [Language] Weak wording found. Apply graduated fix (MUST + why for safety, explain-why + imperative for behavioral):
    Line 11: Found ['should'] -> "You should use the logger to debug."
```

Three things to read out of that shape:

- **The reported line is the line in `SKILL.md`, frontmatter included.** Open the
  file at 11 and the sentence is there.
- **`[Language]` and `[Execution Policy]` are advisory** — reported, exit code
  still 0 if they were the only findings. An advisory is closed by fixing it or
  by writing down why it stands, never by editing correct prose to satisfy a
  rule that is reading it wrong. `--strict` promotes them when you are sweeping
  that backlog deliberately.
- **No `[CSO]` line here, and that is the project config talking.** This
  repository's `.agent/rules/skill_standards.yaml` sets
  `enforce_cso_prefix: false`, which both gates honour. Under the bundled
  defaults the same description raises
  `[CSO] Description should start with one of ['Use when', ...]`.

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
description: Use when debugging complex state changes, race conditions, or persisting errors. Apply even when the issue seems simple.
...
## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I'll just print to stdout" -> **WRONG**. Use the structured logger — stdout is lost on restart and cannot be searched.
- "This function is too simple to log" -> **WRONG**. Simple functions are where silent failures hide.

## Instructions
1. **Import** the logger module immediately.
2. **Execute** `logger.info()` at the start of the transaction — without this, you have no audit trail if the transaction fails silently.
3. **IF** error occurs:
    *   **CALL** `logger.error(e)` — this ensures error context is preserved for debugging.
    *   **RAISE** the exception (do not swallow — swallowed exceptions cause cascading failures).

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