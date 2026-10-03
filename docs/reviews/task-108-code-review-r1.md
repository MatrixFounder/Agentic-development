# TASK 108 code review, round 1, and its fix loop

- **Date:** 2026-10-03.
- **Scope:** the skill `mermaid-authoring-guidelines` (scripts, eval instrument, references) and
  its integration into the framework.
- **State:** the paid campaign had finished its 66 runs; nothing was graded yet.
- **Method:** six reviewers worked in parallel: five area reviewers with the plain exhaustive
  prompt, and one security auditor. A separate verifier per area then tried to refute each finding
  with its own reproduction.
- **Independence:** every agent ran the same model, so agreement between them is corroboration,
  not independent confirmation (`vdd-multi` Phase 2 rule 3).

## Findings

| Area | BLOCKING | MAJOR | MINOR | Refuted |
| :--- | ---: | ---: | ---: | ---: |
| Eval instrument | 3 | 13 | 14 | 0 |
| Plan chart | 2 | 0 | 12 | 0 |
| Render check and geometry | 0 | 4 | 17 | 0 |
| Security | 0 | 2 | 17 | 1 |
| Lint and parse model | 0 | 2 | 30 | 1 |
| Skill text and integration | 0 | 2 | 49 | 0 |
| **Total** | **5** | **23** | **139** | **2** |

MINOR counts include the findings a verifier rated PLAUSIBLE.

### The five BLOCKING findings

| Id | Defect | Resolution |
| :--- | :--- | :--- |
| EI-01 | the grader read an ASCII figure without a fence as no figure, which inflated Δ_H | read in a terminal medium; selftest rows from the live answers |
| EI-02 | the C0 key accepted only `flowchart`, although the request names no kind | registered key kept; amendment `a1` grades it apart as post-hoc |
| EI-13 | the grader never checked the key hashes against the campaign | it exits 2 on a mismatch; `--amendment` is the one exception |
| PC-01 | a chart split with `--stages` read as stale under the documented `--check` | the stage groups are stored in the region's first line |
| PC-02 | two start markers and one end marker deleted the text between them | the scan stops at either marker; a damaged region is refused |

## Fix loop

Each wave gave every owner disjoint files and ran a verifier that replayed the original failure.

| Wave | Content | Verified fixed | Deferred, verified justified | Regressions found |
| :--- | :--- | ---: | ---: | ---: |
| 1 | four code areas | 102 | 12 | 23 |
| 1b + 2 | wave-1 regressions; skill text and integration | 84 | 11 | 17 |
| 1c | what 1b and 2 left | 29 | 0 | 17, 1 BLOCKING |
| 1d | a closed list of 12 items, the crash among them | 12 | 0 | 1 MINOR |

The loop stopped at wave 1d: no BLOCKING finding remained.

## Deferred, with where each goes

| Finding | Why deferred | Where it goes |
| :--- | :--- | :--- |
| EI-02, EI-08, EI-09, EI-27 | the keys are pre-registered | amendment `a1`, post-hoc sensitivity analysis; WI-26 |
| EI-16, EI-23, EI-24, EI-25 | they change the registered design | the next campaign, WI-26 |
| SEC-09 | old transitive packages in the v10 lockfile, reached only by a browser download the setup never runs | WI-30 |
| SEC-20 | the request allowlist of mermaid-cli 11.17.0 and 12.0.0 is inverted; this is an upstream defect | WI-30; with SEC-01 no host resolves |
| RG-19 | gating a lifeline through a label fails the positive examples P7 and P11 | WI-32 |
| SEC-17, SEC-18, SEC-19 | framework-wide, outside this task | WI-31 |

## Known residual

- An ASCII `+` where the flow merges and then runs right and down no longer counts as a join, so
  the lint asks for no legend there (wave 1d).
- Wave 1c moved three hard budgets to the largest count a passing render reaches: sequence
  participants, timeline periods and journey tasks. The gitGraph budget stands, because a `TB`
  graph stays legible past 15 commits.
- The calibration found three detector defects. They are fixed under the D8 validity rule, and
  `references/eval-results.md` reports them.
