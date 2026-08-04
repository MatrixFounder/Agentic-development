---
id: REG-14
type: known-issue
status: fixed
opened_at: 2026-08-04
category: register
severity: SEV-3
slug: reg-14-a-shipped-pattern-replaced-in-place-keeps-the-count-and-removes-detection
component: '.agent/skills/artifact-formalizer/scripts/selftest_scan.py'
resolved_at: 2026-08-04
resolved_by: TASK 100
---

# REG-14 — A shipped pattern replaced in place keeps the count and removes detection

> **Resolved 2026-08-04 by TASK 100.** `SHIPPED_SURFACES` pins every shipped pattern by identity,
> per language and per rule class. This record's own reproduction fails `TC-100-02`, and the rule-2
> variant fails `TC-100-01`; each case prints the pattern added and the pattern removed. `TC-100-03`
> fails when the surface pin and the TASK 099 count pins are re-pinned apart.

**Component:** `.agent/skills/artifact-formalizer/scripts/selftest_scan.py`

## Symptom

`SHIPPED_ENTRIES` and `SHIPPED_REASONING` pin how MANY entries each rule class ships, never WHICH.
An entry edited in place keeps the count, keeps matching its own declared probe, and removes real
detection with both gates at exit 0.

## Reproduction

In `data/register-en.json` replace the rule-3 causal `\bfor the reason that\b` with
`\bZZZNEVERCAUSE\b` and move its `probes` key with it. Measured on a scratch copy:
`selftest_scan.py` -> `174/174 passed` exit 0; `scan_register.py --probe` -> `18/18 detectors live`
exit 0; and `The installer shall abort for the reason that the target exists.` goes from
`[('reasoning', 'shall … for the reason that')]` to `[]`.
The same shape applies to every rule-2, rule-4 and rule-6 entry.

## Provenance

Found by the adversarial verification of TASK 099, 2026-08-04, and independently reproduced by the
orchestrator before filing. Each is the class TASK 099 closed elsewhere: a gate that reports a clean
instrument while a detector is gone. None is the symptom any `REG-2`…`REG-13` record states, so
TASK 099 recorded them here rather than widening its own scope (TASK 099 OQ-2).
