# PLAN 100 — Register scanner: close the REG-14…REG-18 mutation-survivor batch

**TASK:** [docs/TASK.md](TASK.md) · **Closes:** REG-14, REG-15, REG-16, REG-17, REG-18

## Sequencing rule

Three clusters, executed in order. Cluster A edits the scanner and changes what the roster reports.
Cluster B edits the battery and reads cluster A's behaviour. Cluster C reads the case count cluster
B printed. The case count is read from a run, never computed from arithmetic.

| Order | Cluster | File(s) | Closes |
| :--- | :--- | :--- | :--- |
| A | Scanner | `scripts/scan_register.py` | REG-16, REG-17 |
| B | Battery | `scripts/selftest_scan.py` | REG-14, REG-15, REG-18 + the cases for A |
| C | Count pin and documents | `scripts/selftest_scan.py`, `SKILL.md`, `System/Docs/SKILLS.md` | the count `TC-SHIP-08` asserts |

## Cluster A — scanner

- [ ] A1. **REG-17.** Change `_structural_probes` to return one or more line forms per kind. Give
      `sentence_length` and `sentence_near_limit` a bare line, a `- ` list item and a `1. ` ordered
      item — every form `LIST_MARK` accepts. Leave `cell_width`, `cell_sentences` and
      `emoji_severity` at one form: tables and rule 5 do not consult `SKIP_LINE`.
- [ ] A2. **REG-17.** Change the structural loop in `verify_detectors` to require every form to
      fire, and to name the form that did not.
- [ ] A3. **REG-17.** Exercise each rule-3 pattern in both line forms. Keep the detail phrase
      `N exercised of M patterns` — `TC-097-13` asserts the substring `4 exercised of 4`.
- [ ] A4. **REG-16, code half.** Carry `flags` into the loaded entry in `load_rules`. In the lexical
      loop, run every entry declaring `i` against a case-flipped copy of its own probe. Collect the
      failures as `case-blind`, count them against the row's liveness, and name them in the detail.
      The data half of REG-16 belongs to B6: a check keyed on the declared flag is switched off by
      the edit that removes the flag.
- [ ] A5. Run `--probe`. Expect `18/18 detectors live`, exit 0. Run the battery and record which
      cases fail; the expected set is empty.

**Postcondition.** `--probe` exits 0 at `18/18`. The battery's total is unchanged at 174.

## Cluster B — battery

- [ ] B1. Import `scan_register` beside the existing subprocess helpers, so a case can read a module
      constant. Add `scanner_copy(...)`, which copies the shipped skill root and applies a
      substitution to the scanner source, for the two mutations that live in code rather than data.
- [ ] B2. **REG-14.** Add `SHIPPED_SURFACES`: per language, the pattern strings of rules 2, 4 and 6
      and of the rule-3 modal and causal vocabularies. Add the two cases that compare the loaded
      sets against it and print the symmetric difference.
- [ ] B3. **REG-14.** Add the case asserting `SHIPPED_SURFACES` and the TASK 099 count pins state
      the same sizes, so a partial re-pin exits 1.
- [ ] B4. **REG-15.** Add `SHIPPED_THRESHOLDS` and rewrite `TC-SHIP-02` from one key to the whole
      declared dict. Add `SHIPPED_DEFAULTS` and the case comparing it against the imported
      `DEFAULTS`.
- [ ] B5. **REG-18.** Add `SHIPPED_TICK_GLYPHS` and `SHIPPED_STATUS_GLYPHS` and the two cases
      comparing them against the imported frozensets.
- [ ] B6. **REG-16.** Carry `flags` in `SHIPPED_SURFACES`, so the pin fails when the key is removed.
      Add the case that loses the flag at the scan-side compile in a scanner copy and asserts exit 2
      with all six lexical rows DEAD.
- [ ] B7. **REG-17.** Add the case that widens `SKIP_LINE` in a scanner copy and asserts exit 2 with
      DEAD `sentence_length`, `sentence_near_limit` and `reasoning` rows.
- [ ] B8. Add the control for `scanner_copy`: an unmutated scanner copy probes `18/18` at exit 0.
- [ ] B9. Run the battery. Record the printed total.

**Postcondition.** The battery exits 0 and prints a total above 174. `EXPECTED_CASES` is stale by
construction until cluster C.

## Cluster C — count pin and documents

- [ ] C1. Set `EXPECTED_CASES` to cluster B's printed total.
- [ ] C2. Update the count in `SKILL.md` §8 and in `System/Docs/SKILLS.md` to the same number.
- [ ] C3. Record the two roster changes in `SKILL.md` §5: the second line form and the case-flag
      check.
- [ ] C4. Run the battery. Expect `EXPECTED_CASES` printed, exit 0.

**Postcondition.** `TC-META-01` and `TC-SHIP-08` both pass against one number.

## Verification

- [ ] V1. Execute every mutation in TASK §4 (A3–A11) against the fixed tree and record the observed
      result.
- [ ] V2. Extract the `.md` files of `23827c1` and scan them with both the old scanner and the new
      one. Expect identical totals and an identical per-kind breakdown. Comparing the working tree
      against the pre-task number instead would measure this task's own prose.
- [ ] V3. Run the six `framework-gates.yml` jobs locally.
- [ ] V4. Adversarially verify each claimed fix against its issue record's Reproduction, and against
      variants of it the first implementation may not reach: a different list marker, a duplicated
      entry, a narrowed `_PICTO` range, a reverted fix.
- [ ] V5. Flip five issue files and five `docs/KNOWN_ISSUES.md` index lines in lockstep.
