---
id: REG-16
type: known-issue
status: open
opened_at: 2026-08-04
category: register
severity: SEV-3
slug: reg-16-dropping-the-flags-key-from-entries-no-case-references-removes-findings-silently
component: '.agent/skills/artifact-formalizer/data/register-en.json'
---

# REG-16 — Dropping the `flags` key from entries no case references removes findings silently

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
