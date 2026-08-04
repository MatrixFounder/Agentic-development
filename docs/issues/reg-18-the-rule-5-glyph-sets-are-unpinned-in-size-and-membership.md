---
id: REG-18
type: known-issue
status: open
opened_at: 2026-08-04
category: register
severity: SEV-4
slug: reg-18-the-rule-5-glyph-sets-are-unpinned-in-size-and-membership
component: '.agent/skills/artifact-formalizer/scripts/scan_register.py'
---

# REG-18 — The rule-5 glyph sets are unpinned in size and membership

**Component:** `.agent/skills/artifact-formalizer/scripts/scan_register.py`

## Symptom

`SHIPPED_ENTRIES` pins the JSON lexicons. Nothing pins the Python frozensets `TICK_GLYPHS` and
`STATUS_GLYPHS`, so a glyph moved into the exempt set stops being reported. Individual cases cover
`🔴`, `✅`, `⛔`, `✔` and `‼`; every other pictograph is unprotected.

## Reproduction

Widen `TICK_GLYPHS` at `scan_register.py:589` to `frozenset("✓✗❌⚠🚀📘🛠🧪❓🔧")`. Measured over the
631 tracked `.md` files: `emoji_severity` findings fall from 1,011 to 778, a loss of 233, while
`selftest_scan.py` reports `174/174 passed` exit 0 and `scan_register.py --probe` reports
`18/18 detectors live` exit 0.

## Provenance

Found by the adversarial verification of TASK 099, 2026-08-04, and independently reproduced by the
orchestrator before filing. Each is the class TASK 099 closed elsewhere: a gate that reports a clean
instrument while a detector is gone. None is the symptom any `REG-2`…`REG-13` record states, so
TASK 099 recorded them here rather than widening its own scope (TASK 099 OQ-2).
