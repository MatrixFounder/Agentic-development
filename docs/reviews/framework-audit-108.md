# Framework Audit 108 — mermaid-authoring-guidelines

- **Task:** 108 `mermaid-authoring-guidelines`. It archives to
  `docs/tasks/task-108-mermaid-authoring-guidelines.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1,
  Modes A and B.
- **Date:** 2026-10-02. **Base revision:** `ee69bf2e0e35b11a2c525a5b75d64879d903c232`, clean tree
  at start.
- **Source:** operator request and draft specification, 2026-10-02.

## 0. Emergency Bypass

None set.

## Mode A — SPECIFICATION AUDIT — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Root Integrity | PASS — R1–R13 each map to an acceptance id; Cluster A writes stubs and their tests first |
| 2 | Skill Compatibility | PASS — no new agent or workflow; edited prompts keep their TIER 0 loads; TIER 0 untouched (D9) |
| 3 | Documentation | PASS — R13 edits `System/Docs/SKILLS.md` and `SKILL_TIERS.md`; both changelogs carry v3.33.0 |
| 4 | Migration | PASS — consumers receive the skill after `install.py update`; UC-1 A3 reports an absent skill |
| — | Blocking conditions | None triggered |

**Blocking conditions.** `core-principles` and `skill-safe-commands` are unmodified. `GEMINI.md`
changes together with `System/Docs/SKILL_TIERS.md` and `System/Docs/SKILLS.md` (R10.6, R13). No
workflow is added.

**Check 4.** A consumer project links skills per item, so the new directory reaches it only after
`install.py update`. Its prompts name the skill at once, because `System/` is linked as a folder.
UC-1 A3 makes the architect report the absence instead of drawing without the rules, and the
changelog's migration note names the command.

## Mode B — PLAN AUDIT — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Verification step | PASS — every cluster ends in a run; H2 runs every CI gate locally |
| 2 | Rollback | PASS — base `ee69bf2` recorded on a clean tree; 138 paths declared, one per item |
| 3 | Atomic updates | PASS — eight clusters; stubs (A) precede logic (B, C, D) |
| 4 | Test coverage | PASS — unit tests per script, a wiring test, an eval selftest, all registered in CI |

**Check 2.** The eval corpus is written by a campaign, so its file names are known only after the
runs. H4 appends them to the PLAN, one full path per item, before the review rounds. Renders and
renderer installs live outside the repository and are not part of the rollback set.

**RTM coverage.** R1 → A, F. R2 → B, F. R3–R5 → F. R6 → A, B. R7 → A, C. R8 → A, D. R9 → F.
R10 → G. R11 → E, F. R12 → B–E, G, H. R13 → H.

## Risks recorded before execution

- A parse model shared by the lint, the render check and the grader is written in parallel with
  its callers. A signature mismatch would fail Cluster E; the A4 stub tests pin every signature
  and detect it.
- The `without_skill` arm runs before the skill text exists → the text is tuned to the eval
  cases if per-case outputs are read (mitigated by the PLAN's sequencing rule; F reads aggregate
  rates only).
- Renderer installs fetch packages from npm → a compromised package runs in the browser
  (mitigated by exact pins, `PUPPETEER_SKIP_DOWNLOAD=1`, and installs outside every repository).

## Review round 1 — `task-reviewer` on TASK revision 1

Verdict REJECTED: 2 blocking findings (B1 writes outside the repository and a commit; B2 the plan
input keyed on prose), 15 MAJOR, 23 MINOR. The reviewer had no execution tool and no tree
fingerprint. The operator answered its four questions on 2026-10-02 (TASK D9, D16, D17, D18).
TASK revision 2 maps every finding to its resolution in §8.

## Mode A — SPECIFICATION AUDIT, round 2 — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Root Integrity | PASS — R1–R13 each name an acceptance id (RTM column); stubs and their tests precede logic |
| 2 | Skill Compatibility | PASS — no new agent or workflow; TIER 0 untouched (D9) |
| 3 | Documentation | PASS — R13 and A16; both changelogs; ARCHITECTURE §10 |
| 4 | Migration | PASS — consumers after `install.py update`; UC-1 A3 falls back to a list or table |
| — | Blocking conditions | None triggered |

**The deviation.** `framework-upgrade` §3.1 forbids edits outside the repository. TASK §3 records
three kinds of path written outside it (renders, renderer installs, eval temporary directories)
under the operator's licence of 2026-10-02 (D17). None is a copy of a repository file or a path of
another repository, so the rollback through git (§5) is unaffected.

## Mode B — PLAN AUDIT, round 2 — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Verification step | PASS — every cluster ends in a run; H2 runs every `framework-gates.yml` job |
| 2 | Rollback | PASS — base `ee69bf2`; 149 paths declared, one full path per item; corpus list appended at H4 |
| 3 | Atomic updates | PASS — clusters B–H; A done |
| 4 | Test coverage | PASS — unit tests per script, planarity, paired-example geometry, wiring test, eval selftest |

Tree fingerprint at this audit: `eeb7a1b15917`.

## Review round 2 — `task-reviewer` on TASK revision 2

Verdict APPROVED WITH CHANGES: 0 BLOCKING, 13 MAJOR, 18 MINOR. Kept in
`docs/reviews/task-108-review-r2.md`; round 1 is kept in `docs/reviews/task-108-review-r1.md`.
The operator confirmed on 2026-10-02 that the D17 licence covers the complete list of writes
outside the repository (TASK §3). TASK revision 3 maps every finding to its resolution in §8.

## Mode A — SPECIFICATION AUDIT, round 3 — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Root Integrity | PASS — R1–R13 trace to A1–A19 |
| 2 | Skill Compatibility | PASS — no new agent or workflow; TIER 0 untouched (D9) |
| 3 | Documentation | PASS — R13, A16 |
| 4 | Migration | PASS — consumers after `install.py update`; UC-1 A3; changelog note on `settings.json` |
| — | Blocking conditions | None triggered |

## Mode B — PLAN AUDIT, round 3 — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Verification step | PASS — every cluster ends in a run; H2 runs every `framework-gates.yml` job |
| 2 | Rollback | PASS — base `ee69bf2`; 162 paths declared; corpus list appended at H4 |
| 3 | Atomic updates | PASS — the revision-3 deltas are a separate pass per cluster |
| 4 | Test coverage | PASS — A17–A19 add the render-check, setup and template tests |


## Pre-registration (TASK R11.10), 2026-10-03

Written before the first paid run. `evals/PROVENANCE.txt` holds the same lines; its own sha256 is
`54f001a869157e85e9f5c0e3fd5f6e3a63a23fcfa863caf0ced7517f177c0091`. `run_evals.py` refuses a paid run while any line differs.

```text
4815053e5bc533acd68ecb93c9977aa0c20b4ea0948232ff8e9e47609ff2df4b  README.md
5be7d4f492fd2ca41d9ba8dd7b99bc49788d5b3b46558e96f2841a96aa748a66  prompts/task-template.md
a86c5945919bcd2ce02f01a719cfdfadece41ff8765f905a57de18538b0fd9aa  evals.json
3cc409a385dd5ab89bde948a53dd6681e0e3033ac9a194ad87f54b10ac81b20e  fixtures/c0-control-thumbnails/key.json
3abb94da7a8d44a0a0ee2ece27e0f45b0c62afc7bf4a905e95f5a0d0baf67b57  fixtures/c1-wms-container-view/key.json
2f5074840ee249df84ad1cfceb70316ca2a90e42b067e93e6c29d7ffa717462e  fixtures/c2-card-3ds-sequence/key.json
4eca378efb88c859d4ad581156d4ca8b472fc64ed366875582e625d17f381ffb  fixtures/c3-leave-request-lifecycle/key.json
7797fbd052f0ef79f0fec748b14aeb5e236a990cc26867da952dffbbeeb80108  fixtures/c4-reporting-migration-gantt/key.json
4c6cafae3c81071a242b1b101259592ac1535da07417ff3d96d738f2f85186c4  fixtures/c5-sales-pipeline-dataflow/key.json
0d52c3cf432e46bb177d242e3c36c6fc2a7f7283a2f9814e7661f02a691bc047  fixtures/c6-clinic-deployment/key.json
03b6c1ef8185df26e2330bbbd866b6d87d9b5f8124d098cf06b8a64a057695f4  fixtures/c7-refund-decision/key.json
19feb5c6420e8ca862f29139d436bc5ae9d01a1d67f7694bbb912ce0095dd850  fixtures/c8-frontends-services-k33/key.json
5b80108cd16c2fbae3f98efe6080d695a3d68df18e204d7945d5996bddb2dae2  fixtures/f1-ci-stages-terminal/key.json
e5ccd14ac8289a86ab4762d029983c5df253f7b695458c807c951d95ad7b25a9  fixtures/f2-roles-operations-matrix/key.json
```

## Campaign `2026-10-opus55-xhigh-r1`, 2026-10-03

- **Runs:** 66 of 66 graded; spend 28.56 USD of 60 USD. The first `without_skill` pass failed 30
  runs on API errors with cost 0. The executor now records the cause and backs off exponentially;
  the arm resumed and completed.
- **D8:** the campaign is invalid. V1, V3 and C1 are met; V2 is not met on two types whose single
  positive does not come from the detector. So the effect criteria decide nothing.
- **Numbers, for information:** Δ_H 0.084 [0.035, 0.129], 0.077 before the detector fixes; strict
  0.61 against 0.33. Under amendment `a1`, a post-hoc analysis: Δ_H 0.070 [0.024, 0.118].
- **Calibration:** 39 items drawn, 34 labelled by two raters each, blind to the arm. The 5 paired
  top-ups had no renders and stayed unlabelled. The disagreements exposed three detector defects,
  fixed under the D8 validity rule; the corpus was rendered and graded again.
- **Revision round:** not run, by operator decision D28. The baseline sits near the ceiling.
- **Report:** `.agent/skills/mermaid-authoring-guidelines/references/eval-results.md`.

## Code review round 1 — six reviewers and verifiers, 2026-10-03

169 findings: 5 BLOCKING, 23 MAJOR, 139 MINOR, 2 refuted. A fix loop of four verified waves
closed every BLOCKING finding; the deferred ones carry a destination. The round was not on a
frozen tree, since the fixes followed it. Record: `docs/reviews/task-108-code-review-r1.md`.

## Deviations from the registered plan

- The grader, the detector and the normalisation rule changed after the runs, as instrument
  fixes under D8. They are listed in `evals/AMENDMENTS.md`, and the report records their sha256.
- `SKILL.md` and several references changed after the campaign, in review round 1. The measured
  bundle is the one each run record holds.
- Amendment `a1` (keys) is post-hoc, made after reviewers had seen per-case scores. The operator
  has not confirmed it, and it never replaces the registered report.

## Code review round 2 — code reviewer and security auditor, frozen tree, 2026-10-03

- **Tree fingerprint:** `cd2a33d726d3`, the same at the start and the end of both reviews. Recipe:
  `{ git rev-parse HEAD; git status --porcelain --untracked-files=all; git diff HEAD;
  git ls-files -o --exclude-standard -z | xargs -0 shasum -a 256; } | shasum -a 256 | cut -c1-12`.
- **Findings:** 26, all confirmed by a verifier: 0 BLOCKING, 7 MAJOR, 19 MINOR. A12 holds: no
  BLOCKING finding remains.
- **Fixed and verified:** every MAJOR and most MINOR findings, by three owners with verifiers.
  Re-rendering the corpus left every metric of the 66 runs unchanged, and the regrade kept every
  check verdict. Record: `docs/reviews/task-108-code-review-r2.md`.

## Hand-off, 2026-10-03

- **Tree fingerprint at hand-off:** `80d2926f1095` (recipe above), taken before this section was
  written. 630 changed or new paths, every one declared in PLAN 108.
- **Gates:** every job of `framework-gates.yml` passes locally. The archived-references step is
  advisory and reports only references that predate this change.
- **Retro:** WI-26 to WI-33 filed; the round-1 deferrals point at them.
- **After the fingerprint:** at the operator's direction, WI-33 now targets Python 3.14 instead of
  3.9 support. Its file was renamed, and PLAN 108 and the backlog index carry the new path.
- **Not done by this run:** the commit, which is the operator's; the sync of Universal-skills and
  of consumer projects, which follows the commit.
