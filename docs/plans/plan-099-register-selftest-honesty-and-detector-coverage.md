# PLAN 099 — Register scanner: close the REG-2…REG-13 selftest-honesty batch

**TASK:** [docs/TASK.md](../tasks/task-099-register-selftest-honesty-and-detector-coverage.md) · **Closes:** REG-2 … REG-13

## Sequencing rule

Five clusters, executed in order. No two clusters edit the same file, and each cluster observes the
previous one's edits on disk. Counts are read from a run, never computed from arithmetic: the data
cluster moves the lexicon sizes that cluster C pins, and cluster C moves the case count that
clusters D and E state.

| Order | Cluster | File(s) | Closes |
| :--- | :--- | :--- | :--- |
| A | Rule data | `data/register-en.json` | REG-11, REG-12 |
| B | Scanner | `scripts/scan_register.py` | REG-3, REG-4, REG-10 (code), REG-9 (docstring) |
| C | Battery | `scripts/selftest_scan.py` | REG-2, REG-5, REG-6, REG-7 + repairs and new cases from A and B |
| D | Documents | `SKILL.md`, `references/measurement-baseline.md`, `System/Docs/SKILLS.md` | REG-13, REG-8 (sites), REG-10 (wording), REG-9 (row) |
| E | Count pin | `scripts/selftest_scan.py` | REG-8 (assertion) |

## Cluster A — rule data

- [ ] A1. Insert the rule-4 red/green verb entry into `register-en.json`, after the
      `always green / forever green` entry, per D8 (`\s+` between verb and colour).
- [ ] A2. Insert the rule-2 ranking entry, after `the key insight / the whole point`, listing only
      the measured members per D9.
- [ ] A3. Run `--probe`. Expect `en maxim 9/9`, `en marker 28/28`, `18/18 detectors live`, exit 0.
- [ ] A4. Record the new-finding delta over `docs/` for the change report.

**Postcondition.** `--probe` exits 0 and the battery still passes; no document under `.agent/` or
`System/` gains a finding.

## Cluster B — scanner

- [ ] B1. **REG-4.** Add `STRUCTURAL_KINDS`, `PROBE_ROSTER`, `SHIPPED_LANGS` beside
      `LEXICAL_RULES`. Add `_pin_roster` and the `strict` parameter to `verify_detectors`, applied
      on both return paths.
- [ ] B2. **REG-4.** Key strictness on `not args.rules` in the `--probe` path and the scan path,
      per D6. Union the loaded languages with `SHIPPED_LANGS` so a missing language reports DEAD.
- [ ] B3. **REG-3.** Make a declared example mandatory in `_validate_reasoning`, inside the existing
      `if not errors:` guard.
- [ ] B4. **REG-3.** Fold `unprobed` into the reasoning row's liveness, and turn the no-anchor
      branch into a DEAD row.
- [ ] B5. **REG-10.** Add `TICK_GLYPHS`, add `☐` to `STATUS_GLYPHS`, and rewrite the rule-5 guard so
      a tick is exempt in every position. Rewrite the narrowing comment: both of its stated
      premises are refuted by the corpus it cites.
- [ ] B6. **REG-10.** Branch the guidance string so a status glyph gets status-word advice.
- [ ] B7. **REG-9.** Restate the `_dedupe_spans` docstring example so it names something the shipped
      data can produce.
- [ ] B8. **REG-8.** Add a revision identifier to the `128/128` narrative in the reasoning-row
      comment.
- [ ] B9. Run `--probe` (expect `18/18`, exit 0) and the battery. Record which cases fail — the
      expected set is the three reasoning fixtures cluster C repairs.

**Postcondition.** `--probe` exits 0. The battery's failures are exactly the fixtures named in B9.

## Cluster C — battery

- [ ] C1. Repair the reasoning fixtures B3 invalidated: add `probes` to the rule-file fixtures at
      `TC-SCHEMA-15` and `TC-R3-01`, and re-pin `TC-097-15` to the mandatory-example contract.
- [ ] C2. **REG-2.** Add `SHIPPED_ENTRIES` and `SHIPPED_PROBES` literals. Rewrite `TC-PROBE-02`
      against `SHIPPED_PROBES`. Add `TC-SHIP-07` comparing loaded counts against `SHIPPED_ENTRIES`.
      The literals carry cluster A's new sizes.
- [ ] C3. **REG-4.** Add the roster cases. They cannot use `--rules`, so they build a throwaway
      skill root and run a copy of the scanner. Include the unmutated control.
- [ ] C4. **REG-3.** Add the mandatory-example case and the TASK 097 D3 two-step case.
- [ ] C5. **REG-5.** Add the callout-table case for `dequote`.
- [ ] C6. **REG-6.** Add the `i.e.`, `vs.` and `см.` lookbehind cases.
- [ ] C7. **REG-7.** Add the two `check_thresholds` rejection cases, keyed on fragments unique to
      each branch.
- [ ] C8. **REG-10.** Add the tick-in-a-list case, the `☐`-in-a-table case, and the guidance-wording
      case.
- [ ] C9. **REG-11 / REG-12.** Add the two detection cases, the `Red-Green-Refactor` control, the
      `forever green` no-double-report control, and the `the key insight` collision control.
- [ ] C10. Run the battery. Record the printed total.

**Postcondition.** The battery exits 0. The printed total is the number clusters D and E state.

## Cluster D — documents

- [ ] D1. **REG-13.** Remove the cardinal from the `SKILL.md` §2 bullet, its §9 Quick Reference
      row, and the matching sentence in `System/Docs/SKILLS.md`.
- [ ] D2. **REG-8.** `SKILL.md` §8 states cluster C's measured total and names the case that asserts
      it. `SKILL.md` §3 and `measurement-baseline.md` §9 drop the numeral.
- [ ] D3. **REG-8.** Add a revision identifier to the `128/128` narrative in
      `measurement-baseline.md` §10.1.
- [ ] D4. **REG-10.** Rewrite the `SKILL.md` §5 rule-5 bullet and `measurement-baseline.md` §6 to name which glyphs
      are exempt where. Keep the §5 coverage-table row coherent with them.
- [ ] D5. **REG-9.** Correct §4 row 65 to `not adopted` in the established form, and repair its
      Pattern cell.
- [ ] D6. **REG-9.** Re-derive both cardinals in `SKILL.md` §6 item 4 from the current tables.
- [ ] D7. Record the roster pin and the mandatory-example contract in `SKILL.md` §5/§8 and
      `measurement-baseline.md` §10.1.

**Postcondition.** No live document states a case count other than cluster C's measured total, and
none states a cardinal adjacent to `licensed`.

## Cluster E — count pin

- [ ] E1. Add the case asserting `SKILL.md` states `EXPECTED_CASES`, scoped to `SKILL.md` and
      `System/Docs/SKILLS.md`, skipping rather than failing when a file is absent.
- [ ] E2. Re-run, read the printed total, set `EXPECTED_CASES` to it plus one.
- [ ] E3. Add `TC-META-01` immediately before `failed = …`, computing the total before `check`
      appends.
- [ ] E4. Run the battery. Expect `EXPECTED_CASES` printed, exit 0.

**Postcondition.** Dropping a test function from the tuple makes `TC-META-01` fail. Changing
`SKILL.md`'s count makes E1's case fail.

## Verification

- [ ] V1. Execute every mutation in TASK §4 (A2–A10) and record the observed result.
- [ ] V2. Run the five `framework-gates.yml` jobs locally.
- [ ] V3. Adversarially verify each claimed fix against its issue record's Reproduction.
- [ ] V4. Flip twelve issue files and twelve `docs/KNOWN_ISSUES.md` index lines in lockstep.
