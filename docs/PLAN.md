# PLAN 134 — Allow-listed scripts import no module planted beside them (WI-39)

**TASK:** [docs/TASK.md](TASK.md) (revision 2) · **Covers:** R1–R7 · **Acceptance:** TC-AL1–TC-AL6.

**Process:** reduced (TASK D1). Edits are in place; the tests come first and run red.

## Steps

- [x] P1 **Tests first.** `tests/test_allow_listed_imports.py` holds TC-AL1 to TC-AL5 from one table
      of the 14 scripts (TASK D4). On the base each of TC-AL1 to TC-AL5 fails; the run records
      which subtests fail and why.
- [x] P2 **Group A** (R1, R4): the guard in seven scripts, and no `from __future__` in the five of
      `System/scripts/` and in `scan_register.py`.
- [x] P3 **Group B** (R1 to R4): the guard, the bytecode settings and the explicit loads in six
      scripts. The module-level inserts into `sys.path` go. `selftest_scan.py`, `lint_mermaid.py`
      and `plan_gantt.py` lose `from __future__`.
- [x] P4 **Group C** (R1, R2, R5): `tests/run_tests.py`.
- [x] P5 **Green.** TC-AL1 to TC-AL5 pass. These also pass:
  - the tests of each skill that the change touches: `artifact-formalizer`,
    `mermaid-authoring-guidelines`, `skill-creator` and `security-audit`;
  - each step of `framework-gates.yml`, run on this machine;
  - the static check of eager annotations on the nine scripts of R4.

  One mutation per group removes the guard of one script, and its subtest of TC-AL1 fails.
- [x] P6 **Records** (R7): WI-39 and `docs/BACKLOG.md`; both changelogs, v3.53.0; the copies in
      `Universal-skills` (TASK D6).
- [x] P7 **Reviews.** One code reviewer with the exhaustive prompt and one security auditor, in
      parallel, on the same fingerprint; then one fix pass and the gates again.
- [ ] P8 **Commit and push** on the operator's word. The first CI run is read for its jobs on
      Python 3.11 (TC-AL6).
