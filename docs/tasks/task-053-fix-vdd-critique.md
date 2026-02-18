# Task: Fix VDD Critique Issues

## Goal
Fix all 10 issues identified in the VDD adversarial critique of `security-audit` skill.

## Checklist
- [x] [HIGH] Fix silent `except: pass` — log skipped files <!-- id: 0 -->
- [x] [HIGH] Fix self-flagging false positives — add self-exclusion <!-- id: 1 -->
- [x] [HIGH] Fix shallow SKIP_DIRS matching — use basename <!-- id: 2 -->
- [x] [MED] Fix OWASP category mappings in SKILL.md <!-- id: 3 -->
- [x] [MED] Fix duplicate A10 in owasp_top_10.md <!-- id: 4 -->
- [x] [MED] Add Rationalization Table to SKILL.md <!-- id: 5 -->
- [x] [MED] Capture exit codes in run_command <!-- id: 6 -->
- [x] [LOW] Add timeouts to subprocess calls <!-- id: 7 -->
- [x] Verify script runs without errors <!-- id: 8 -->
