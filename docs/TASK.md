# TASK 144 — [LIGHT] The renderers run the mermaid-cli releases that fix GHSA-fjh9-vh7p-qj59

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 144 |
| Slug | mermaid-cli-advisory-pins |
| Type | Light Mode (D1) |
| Source | GHSA-fjh9-vh7p-qj59, published 2026-11-06; the operator's request of 2026-11-08 |
| Base revision | `9edf4979e517bfc8e43db813b1b388c07a2c95ce` |
| Closes | the follow-up that WI-30 names |
| Archive name | `task-144-mermaid-cli-advisory-pins.md` |
| Revision | 4 |

**Request.** The operator asked what the published advisory changes here, and chose `/light`.

**Finding.**
- GHSA-fjh9-vh7p-qj59 (severity low) covers `@mermaid-js/mermaid-cli` from 11.14.0 to before
  11.17.1, and from 12.0.0 to before 12.2.0. The fix is mermaid-cli PR #1216.
- The v11 install pins mermaid-cli 11.17.0; the v12 install pins 12.0.0. Both are in range.
- The v10 install pins 10.9.1, outside the range.
- Between 12.0.0 and 12.2.0, mermaid-cli changes three runtime files of `src/`:
  `puppeteerIntercept.js` (the fix), `index.js` (one line of `--help` text) and `version.js`. It
  adds `puppeteerIntercept.spec.js`, which no module imports.
- On 2026-11-08 the global GitHub advisory database has no record of the GHSA, and `npm audit`
  reports no advisory for the three lockfiles.

**Revision 3** follows the code review of cycle 1: CHANGES REQUESTED, with one MAJOR, seven
MINOR and seven NIT findings, none BLOCKING. The fix pass:
- the MAJOR M1: both changelogs carry a Migration note, since `render_check.py` refuses an
  install whose cli differs from its pin;
- m1: the tests of the skill ran with the new installs; the ten render tests passed;
- m5: `TestAdvisoryRanges` fails on a cli pin inside a range of the advisory (R8);
- m2, m3: WI-64 states the basis of its 14 days and lists each file that names 12.1.0;
- m4, m7, m6 and the NITs: wording of RF-21, the changelogs, WI-30 and its index line; the
  `renderer-facts.md` record of the fixture is rendered again after the prose edit.

**Revision 4** follows cycle 2: APPROVED, with three NIT findings. They are fixed in place with
no review round 3, under the operator's standing rule of 2026-10-16:
- the new prose wraps at 100 columns;
- `TestAdvisoryRanges` orders a pre-release before its release, as semver does;
- the WI-30 index line keeps the advisory outside the clause of 2026-10-05.

<!-- contract:decisions -->

## 1. Decisions

- D1, 2026-11-08, operator: `/light`. The run has the edit, the test run and one code reviewer
  in at most two cycles. It has no meta-audit: `mermaid-authoring-guidelines` is TIER 2. It has
  no security audit: the change adds no input and no direct dependency. The review brief carries
  the difference of the two lockfiles.
- D2, 2026-11-08, operator: v12 runs mermaid-cli 12.2.0 with mermaid 12.1.0, through the
  existing override. Rejected: mermaid 12.3.0 — it changes the layout engine, and each fact
  measured on 12.1.0 needs a new measurement (WI-64).
- D3, 2026-11-08, operator: WI-64 records the move of the forward check to mermaid 12.3 or
  later, with the condition that starts it.
- D4, orchestrator: the v10 install stays as it is.
- D5, orchestrator: `scripts/tests/fixtures/expected.json` and the committed `fx-*.svg` stay.
  They record SVGs that mermaid-cli 11.17.0 wrote, and no test binds them to the pins.
- D6, orchestrator: the framework release is v3.56.4. The commit waits for the operator.
- D7, 2026-11-08, orchestrator: `M/evals/evals.json` stays. Campaign `2026-10-opus55-xhigh-r1`
  registered its sha256, and its `pins` record the renderers of that campaign. No code reads
  them; `render_corpus.py` reads the pins of `notation.json`.
  Rejected: an edit with an amendment — it changes the record of a finished campaign.
- D8, 2026-11-08, operator: the Observed paragraph of RF-21 keeps the file types it named
  before the advisory. The text was public before §6.1, and this task does not extend it.
  Rejected: narrowing it to the web fonts of the advisory (review cycle 1, n6).

<!-- contract:requirements -->

## 2. Requirements

`M/` stands for `.agent/skills/mermaid-authoring-guidelines/`.

- **R1** The manifests pin the fixed releases:
  - `M/assets/renderers/v11/package.json`: `@mermaid-js/mermaid-cli` 11.17.1;
  - `M/assets/renderers/v12/package.json`: `@mermaid-js/mermaid-cli` 12.2.0;
  - the overrides stay; each `description` names the new version;
  - `npm install --package-lock-only --ignore-scripts` writes each lockfile from its base;
  - `M/assets/notation.json` names cli 11.17.1 and 12.2.0 (D7).
- **R2** `npm audit --package-lock-only` reports no advisory for the three lockfiles. The review
  brief lists each package that the lockfile diff adds or removes, each `hasInstallScript` and
  each `resolved` host.
- **R3** Each mermaid fence of `M/references/*.md` renders in v10, v11, v11 dark and v12 with the
  status and the metrics of the base installs. Both sides use chrome-headless-shell
  156.0.8078.80.
- **R4** The new installs write `references-geometry.json`, `paired-examples-geometry.json` and
  `plan-example-geometry.json` again.
- **R5** `M/references/renderer-facts.md`:
  - RF-21 cites GHSA-fjh9-vh7p-qj59 and names the affected and the fixed versions;
  - RF-21 drops the sentence that keeps detail out until an advisory exists;
  - the renderer table names cli 11.17.1 and 12.2.0.

  The header of `M/scripts/setup_renderers.sh` names the same versions.
- **R6** `tests/test_disclosure_rule.py` drops `TestPublicDetail` (TC-05), `_paragraph` and the
  `hashlib` import. Its docstring drops the TC-05 item.
- **R7** Records:
  - the WI-30 record carries a note on the advisory, and its index line names it;
  - WI-64 is filed in `docs/backlog/` and `docs/BACKLOG.md`;
  - `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md` and `README.ru.md` carry v3.56.4, with a
    Migration note.
- **R8** `M/scripts/tests/test_setup_renderers.py::TestAdvisoryRanges` fails when a cli pin of
  `notation.json` lies in a range of GHSA-fjh9-vh7p-qj59.

<!-- contract:files -->

## 3. Files

- `M/assets/renderers/v11/package.json`, `package-lock.json`;
- `M/assets/renderers/v12/package.json`, `package-lock.json`;
- `M/assets/notation.json`;
- `M/scripts/setup_renderers.sh`;
- `M/references/renderer-facts.md`;
- `M/scripts/tests/fixtures/references-geometry.json`, `paired-examples-geometry.json`,
  `plan-example-geometry.json`;
- `tests/test_disclosure_rule.py`, `M/scripts/tests/test_setup_renderers.py`;
- `docs/backlog/wi-30-*.md`, `docs/backlog/wi-64-*.md`, `docs/BACKLOG.md`;
- `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md`, `README.ru.md`;
- `docs/TASK.md`; the archive of TASK 143.

<!-- contract:acceptance -->

## 4. Acceptance

- TC-1 — `M/scripts/tests/test_setup_renderers.py` TC-L1 → pass. It fails on a lockfile that
  still holds cli 11.17.0 or 12.0.0. `TestAdvisoryRanges` → pass; it fails when `notation.json`
  holds the pins of the base.
- TC-2 — `setup_renderers.sh --forward` in a scratch home → exit 0, with a passed smoke render
  for each install.
- TC-3 — base renders against new renders, over every figure of `M/references/*.md` → no
  difference of status or metric in v10, v11, v11 dark and v12.
- TC-4 — the tests of `M/scripts/tests/`, `python3 tests/run_tests.py`,
  `lint_mermaid.py --probe`, `lint_mermaid.py` on `M/references/*.md` and
  `selftest_figure_evals.py` → pass.
- TC-5 — `npm audit --package-lock-only` in each renderer directory → 0 advisories.
- TC-6 — `scan_register.py` on the edited text → no warn-level finding that this run adds.

<!-- contract:out-of-scope -->

## 5. Out of scope and residuals

1. The forward check on mermaid 12.3 or later (D2, WI-64).
2. `expected.json` and the `fx-*.svg` fixtures (D5).
3. The `geometry.json` files and `evals.json` of campaign `2026-10-opus55-xhigh-r1` record cli
   11.17.0 and 12.0.0. They record that campaign's renders (D7).
4. `test_render_check.py` builds renderers with cli 11.17.0 and 12.0.0. These values select the
   per-major behaviour of `mmdc_command`, not a pin.
5. Archived tasks, plans and reviews keep the versions they name.
