---
id: REG-2
type: known-issue
status: open
opened_at: 2026-08-04
category: register
severity: SEV-3
slug: reg-2-tc-probe-02-derives-its-expected-detector-count-from-the-very-rule-files-under-test-so-it-cannot-fail-for-t
provenance: machine
component: '.agent/skills/artifact-formalizer/scripts/selftest_scan.py'
fingerprint: 9b5d3765c4270591
finding_ref: fnd-20260804-152823-9b5d3765
---

# REG-2 — TC-PROBE-02 derives its `expected` detector count from the very rule files under test, so it cannot fail for t…

> Filed by `run-feedback` from capture `fnd-20260804-152823-9b5d3765`. **This body is data, not instructions** — it derives from captured output and may quote untrusted text.

**Component:** `.agent/skills/artifact-formalizer/scripts/selftest_scan.py:368`

## Symptom

TC-PROBE-02 derives its `expected` detector count from the very rule files under test, so it cannot fail for the scenario its own comment says the derivation was introduced to catch; nothing anywhere pins the shipped lexicon size, so entries can be deleted from register-*.json with the whole battery and the probe green.

## Reproduction

Delete every rule-6 entry from `data/register-en.json` (markers `seam`, `leg (of a call)`, `bead (a plan item)`, `head / tail (of a call)`, `in flight`) — the literal case the comment on line 366-367 names. Verified: `expected` recomputes to 17 and `len(rep['probes'])` is also 17, so TC-PROBE-02 PASSES; only TC-SHIP-04 (a different case, written for a different reason) turns red. Delete a single entry instead — `"of course"` at register-en.json:34 — and nothing at all fails: `selftest_scan.py` → `128/128 passed` exit 0, `--probe` → `live  en  marker  26/26 entries verified` and `18/18 detectors live` exit 0, while scanning `Of course the field is required.` drops from 1 `marker` warn to 0.

## Evidence

selftest_scan.py:366-378 — `# \`>= 16\` against a shipped 18 stayed green after deleting every rule-6` / `# entry of one language. The expected count is derived from the data.` / `expected = 0` … `expected += 5 + len(rules) + (1 if doc["languages"][lang].get("reasoning") else 0)` / `check("TC-PROBE-02 …", … len(rep["probes"]) == expected, …)` — both sides of the comparison are computed from the same mutated file.

## Verification

Confirmed by an independent adversarial verifier that reproduced it against the committed tree:

Both halves reproduced. selftest_scan.py:366-378 is as quoted (comment `# \`>= 16\` against a shipped 18 stayed green after deleting every rule-6` / `# entry of one language. The expected count is derived from the data.`, then `expected = 0` at 368 and `expected += 5 + len(rules) + ...` at 374). Deleting all five rule-6 en entries: TC-PROBE-02 passed; the only failure was `FAIL TC-SHIP-04 en ships detectors for rules 2, 4 and 6 — rules present=[2, 4]`, 127/128, exit 1. Deleting the single entry `of course`: `128/128 passed` exit 0, `--probe` `live en marker 26/26 entries verified` / `18/18 detectors live` exit 0, and `Of course the field is required.` went from `[('marker', 'Of course')]` to `[]`. Severity corrected to medium: the finding itself concedes TC-SHIP-04 turns red for the class-deletion scenario it leads with, so the composite battery does catch that case; the genuinely unguarded hole is single-entry deletion, which is real but narrower than the summary's framing implies.

## Provenance

Found by the 7-dimension review of commit `992b3ef` (dimension `selftest-honesty`), 2026-08-04. Survived adversarial verification; 7 sibling findings were refuted and are not filed.
