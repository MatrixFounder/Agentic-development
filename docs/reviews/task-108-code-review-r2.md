# TASK 108 code review, round 2 — frozen tree

- **Date:** 2026-10-03.
- **Roles:** one code reviewer with the plain exhaustive prompt, and one security auditor. A
  separate verifier per role tried to refute each finding with its own reproduction.
- **Tree fingerprint:** `cd2a33d726d3` at the start and the end of both reviews (recipe in
  `framework-audit-108.md`). The tree was frozen while they read it.
- **Independence:** same-model agreement is corroboration, not independent confirmation.

## Findings

26 findings, all confirmed by a verifier: 0 BLOCKING, 7 MAJOR, 19 MINOR.

| Id | Severity | Defect | Resolution |
| :--- | :--- | :--- | :--- |
| R2-01 | MAJOR | a fence on a list-marker line was never read, and its closing line swallowed the next figure | fence extraction follows CommonMark block structure |
| R2-02 | MAJOR | the docs reported D8 "not met" and hid that the campaign is invalid | every surface states the invalid verdict; numbers for information |
| R2-03 | MAJOR | 5 calibration top-ups had no renders and were dropped without a count | the report counts them; the sample refuses such an item |
| R2-04 | MAJOR | three detector fixes and their effect on Δ_H were not disclosed | `evals/AMENDMENTS.md` states each fix and its effect |
| R2-05, SEC2-02 | MAJOR | round-1 deferrals named a backlog that held no record | filed as work-items in the retro |
| SEC2-01 | MAJOR | a puppeteer configuration file in the caller's directory ran as code in every render | node runs inside the install directory, which ends the search |
| R2-06, R2-12, R2-13, R2-15 | MINOR | swapped table rows, mixed populations, overstated claims, a wrong rule count | corrected in the report and the changelogs |
| R2-07 to R2-09, R2-11, R2-14, R2-16 | MINOR | grader and model defects | fixed with tests; no check verdict moved |
| R2-10 | MINOR | a two-character milestone name is drawn on the diamond and now fails | `gantt.md` asks for three characters or more, measured |
| R2-17 | MINOR | PLAN 108 has no schedule block | the PLAN states that it predates the plan chart |
| SEC2-03 to SEC2-09 | MINOR | input checks, path disclosure, lock file, private directories, regex cost | fixed with tests |

## After the fixes

- The corpus was rendered again: every metric of the 66 runs is unchanged.
- The regrade kept every check verdict. V2 now reports 34 labelled items of 39, and the sign test
  follows the README.
- Two verifier notes remain as MINOR follow-ups. Pathological documents with thousands of nested
  list markers parse slower. Three branches of the new CommonMark scanner have no test of their
  own.
