---
id: REG-16
type: known-issue
status: fixed
opened_at: 2026-08-04
category: register
severity: SEV-3
slug: reg-16-dropping-the-flags-key-from-entries-no-case-references-removes-findings-silently
component: '.agent/skills/artifact-formalizer/data/register-en.json'
resolved_at: 2026-08-04
resolved_by: TASK 100
---

# REG-16 — Dropping the `flags` key from entries no case references removes findings silently

> **Resolved 2026-08-04 by TASK 100.** `SHIPPED_SURFACES` carries each entry's `flags` beside its
> pattern, so this record's own reproduction fails `TC-100-01` and names every entry that lost the
> key. A roster check alone could not close it: keyed on the declared flag, it is switched off by
> the edit that removes the flag, and the reproduction stayed at `174/174` and `18/18`, both exit 0.
> The roster gained the sibling guarantee instead — every entry declaring `i` is re-run against a
> case-flipped copy of its own probe, so a flag declared and not applied exits 2 with all six
> lexical rows DEAD (`TC-100-12`), where before it named only the 15 entries whose own probe
> happened to carry a capital.

**Component:** `.agent/skills/artifact-formalizer/data/register-en.json`

## Symptom

An entry whose own `probe` still matches case-sensitively survives load validation and the roster
after its `"flags": "i"` key is removed, because both check the entry against its own probe. The
entry count is unchanged, so the count pins stay green.

## Reproduction

Remove `"flags": "i"` from the shipped entries whose probe still matches without it AND whose
marker text appears in no case in `selftest_scan.py`. Measured by the TASK 099 verification run:
41 real `marker` findings lost across 8 files, both gates exit 0.
A broader variant that also touches battery-referenced entries IS caught, by `TC-097-01` — the
hole is specific to entries no case names.

## Provenance

Found by the adversarial verification of TASK 099, 2026-08-04, and independently reproduced by the
orchestrator before filing. Each is the class TASK 099 closed elsewhere: a gate that reports a clean
instrument while a detector is gone. None is the symptom any `REG-2`…`REG-13` record states, so
TASK 099 recorded them here rather than widening its own scope (TASK 099 OQ-2).
