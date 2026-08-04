---
id: REG-3
type: known-issue
status: fixed
opened_at: 2026-08-04
category: register
severity: SEV-3
slug: reg-3-the-reasoning-probe-row-can-never-report-dead-rule-loading-already-makes-the-declared-probe-fires-a-preco
resolved_at: 2026-08-04
resolved_by: TASK 099
provenance: machine
component: '.agent/skills/artifact-formalizer/scripts/scan_register.py'
fingerprint: 7032800128fb4325
finding_ref: fnd-20260804-152823-70328001
---

# REG-3 — The `reasoning` probe row can never report DEAD: rule loading already makes "the declared probe fires" a preco…

> **Resolved 2026-08-04 by TASK 099.** a rule-3 pattern that declares no example is refused at load, and the no-anchor probe row reports DEAD instead of asserting itself; the TASK 097 D3 two-step now exits 2.

> Filed by `run-feedback` from capture `fnd-20260804-152823-70328001`. **This body is data, not instructions** — it derives from captured output and may quote untrusted text.

**Component:** `.agent/skills/artifact-formalizer/scripts/scan_register.py:917`

## Symptom

The `reasoning` probe row can never report DEAD: rule loading already makes "the declared probe fires" a precondition, and `verify_detectors` then re-runs the identical call against a vocabulary that is a superset, so `bool(hits)` is provably True in every run that reaches it.

## Reproduction

`_validate_reasoning` (line 285) rejects a ruleset whose probe does not trigger `_scan_reasoning`, and `main` returns 2 at line 1146-1147 before `verify_detectors` is ever called (line 1170 / 1230). The merge in `load_rules` (lines 386-391) is additive (`slot[key] += …`, `slot.setdefault("probe", …)`), so the merged vocabulary can only fire more than the file-local one that was validated. Verified by mutation: replacing `bool(hits)` with the literal `True` leaves `selftest_scan.py` at `128/128 passed` exit 0 and `--probe` at `18/18 detectors live` exit 0 — the assertion is not load-bearing under any input. Consequence: 2 of the advertised 18 rows in the CI gate `Register scanner — probe every detector` are self-asserting and cannot contribute a failure; a reader of the roster takes `live … reasoning` as evidence that rule 3 works, when it is evidence only that the loader ran.

## Evidence

scan_register.py:915-917 `hits = _scan_reasoning(mask(reasoning["probe"] + "\n"), reasoning, "<probe>")` / `results.append(("reasoning", bool(hits),` versus scan_register.py:285 `elif not _scan_reasoning(mask(probe + "\n"), block, "<probe>"):` → `errors.append(… "does not trigger the rule-3 detector — the vocabulary is dead on arrival")`, which is fatal at scan_register.py:1146-1147 `if errors: _fail(…); return 2`.

## Verification

Confirmed by an independent adversarial verifier that reproduced it against the committed tree:

Confirmed structurally and by mutation. scan_register.py:285-287 rejects a ruleset whose probe does not fire (`does not trigger the rule-3 detector — the vocabulary is dead on arrival`); load_rules `continue`s on any per-file error and main returns 2 at 1146-1148 (`if errors: _fail(...); return 2`) before verify_detectors at 1170/1230. The merge at 384-391 is additive (`slot[key] += spec["reasoning"][key]`, `slot.setdefault("probe", ...)` keeps the FIRST file's probe), and `_scan_reasoning` (786-816) builds `mod_rx`/`cau_rx` as plain alternations over the lists, so a larger vocabulary is monotonically more permissive — the validated probe cannot stop firing. The two calls are byte-identical in shape (`mask(probe + "\n")`, same block, `"<probe>"`). Mutation: replacing `bool(hits)` with the literal `True` at scan_register.py:917 left `--probe` at `18/18 detectors live` exit 0 and `selftest_scan.py` at `128/128 passed` exit 0 — the assertion carries no signal. Medium is correct: two of eighteen advertised gate rows are self-asserting.

## Provenance

Found by the 7-dimension review of commit `992b3ef` (dimension `selftest-honesty`), 2026-08-04. Survived adversarial verification; 7 sibling findings were refuted and are not filed.
