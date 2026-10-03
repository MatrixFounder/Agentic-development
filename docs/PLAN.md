# PLAN 108 — mermaid-authoring-guidelines: figures chosen by form, checked in two renderers, measured by A/B evals

**TASK:** [docs/TASK.md](TASK.md) (revision 3) · **Covers:** R1–R13 · **Acceptance:** A1–A19

This plan predates the plan chart that TASK 108 introduces. It holds no schedule block, so
`plan_gantt.py --check` does not apply to it.

<!-- contract:sequence -->

## Sequencing rule

Eight clusters. Cluster A is done. Clusters B, C and D run in parallel. Cluster E needs B and C,
because the grader imports the lint and the geometry analysis. Cluster F drafts the references in
parallel with B–E and fixes the skill text after the `without_skill` arm of E has run; the
`with_skill` arm runs only on the fixed text. Cluster G runs in parallel with E and F; it edits
files no other cluster touches. Cluster H closes the run.

| Order | Cluster | Files | Covers |
| :--- | :--- | :--- | :--- |
| A | Skeleton, data, stubs (done) | skill directory, `assets/notation.json`, script stubs, test skeletons | R1, R6–R8 stubs |
| B | Model, lint, planarity | `mermaid_model.py`, `lint_mermaid.py`, `planarity.py`, their tests | R2.7, R6, D21, D25 |
| C | Geometry, render, setup | `svg_geometry.py`, `render_check.py`, `measure_text.mjs`, `setup_renderers.sh`, lockfiles, fixtures | R7, §3 |
| D | Plan chart | `plan_gantt.py`, its tests | R8, D19 |
| E | Eval instrument and the `without_skill` arm | `evals/` | R11 |
| F | Skill text, references, examples, the `with_skill` arm | `SKILL.md`, `references/`, example geometry | R1–R5, R9 |
| G | Integration | templates, standard, prompts, checklists, settings, loading, other skills, wiring test | R10, R12.2 |
| H | Docs, release, gates, reviews | registry, changelogs, backlog, audit | R12, R13, A9–A16 |

**Why the `without_skill` arm runs before the skill text is fixed.** It needs no skill file, so it
runs while Cluster F is written. The skill text comes from the draft and the research reports.
Per-case outputs of that arm are not read while F is written; only the aggregate check rates are.

The skill directory is `.agent/skills/mermaid-authoring-guidelines/`, abbreviated `S/` in the steps.

**Declared paths (A11, `framework-upgrade` §2.2).** Edited:

- `.agent/skills/architecture-format-core/SKILL.md`
- `.agent/skills/architecture-format-extended/SKILL.md`
- `.agent/skills/documentation-standards/SKILL.md`
- `.agent/skills/architecture-review-checklist/SKILL.md`
- `.agent/skills/plan-review-checklist/SKILL.md`
- `.agent/skills/task-review-checklist/SKILL.md`
- `.agent/skills/code-review-checklist/SKILL.md`
- `.agent/skills/skill-phase-context/SKILL.md`
- `.agent/skills/brainstorming/SKILL.md`
- `.agent/skills/security-audit/references/checklists/threat_model.md`
- `.agent/skills/skill-reverse-engineering/SKILL.md`
- `.agent/skills/skill-planning-format/SKILL.md`
- `.agent/skills/skill-planning-format/assets/templates/plan_md_template.md`
- `System/Agents/04_architect_prompt.md`
- `System/Agents/05_architecture_reviewer_prompt.md`
- `System/Agents/06_planner_prompt.md`
- `.claude/agents/architect.md`
- `.claude/agents/planner.md`
- `.claude/settings.json`
- `System/Docs/SKILLS.md`
- `System/Docs/SKILL_TIERS.md`
- `CLAUDE.md`
- `AGENTS.md`
- `GEMINI.md`
- `docs/ARCHITECTURE.md`
- `docs/BACKLOG.md`
- `tests/run_tests.py`
- `.github/workflows/framework-gates.yml`
- `CHANGELOG.md`
- `CHANGELOG.ru.md`
- `.agent/workflows/01-start-feature.md`
- `.agent/workflows/vdd-01-start-feature.md`
- `.agent/workflows/02-plan-implementation.md`
- `.agent/workflows/vdd-02-plan.md`
- `System/Agents/07_plan_reviewer_prompt.md`
- `.agent/skills/skill-planning-format/examples/PLAN_EXAMPLE.md`

Created, outside the skill directory:

- `tests/test_mermaid_wiring.py`
- `docs/reviews/framework-audit-108.md`
- `docs/backlog/wi-21-redraw-the-framework-figures-under-mermaid-authoring-guidelines.md`
- `docs/backlog/wi-22-plan-status-tokens-for-the-generated-plan-chart.md`
- `docs/backlog/wi-23-tool-loop-natural-cases-and-ascii-in-documents-for-the-figure-evals.md`
- `docs/backlog/wi-24-figure-rules-in-wiki-import-and-the-meeting-summary-workflow.md`
- `docs/backlog/wi-25-trigger-evaluation-of-the-mermaid-skill-description.md`
- `docs/reviews/task-108-review-r1.md`
- `docs/reviews/task-108-review-r2.md`
- `docs/reviews/task-108-code-review-r1.md`
- `docs/reviews/task-108-code-review-r2.md`

Created, inside the skill directory:

- `.agent/skills/mermaid-authoring-guidelines/SKILL.md`
- `.agent/skills/mermaid-authoring-guidelines/assets/notation.json`
- `.agent/skills/mermaid-authoring-guidelines/assets/renderers/v10/package.json`
- `.agent/skills/mermaid-authoring-guidelines/assets/renderers/v10/package-lock.json`
- `.agent/skills/mermaid-authoring-guidelines/assets/renderers/v11/package.json`
- `.agent/skills/mermaid-authoring-guidelines/assets/renderers/v11/package-lock.json`
- `.agent/skills/mermaid-authoring-guidelines/assets/renderers/v12/package.json`
- `.agent/skills/mermaid-authoring-guidelines/assets/renderers/v12/package-lock.json`
- `.agent/skills/mermaid-authoring-guidelines/references/ascii.md`
- `.agent/skills/mermaid-authoring-guidelines/references/flowchart.md`
- `.agent/skills/mermaid-authoring-guidelines/references/sequence.md`
- `.agent/skills/mermaid-authoring-guidelines/references/state.md`
- `.agent/skills/mermaid-authoring-guidelines/references/gantt.md`
- `.agent/skills/mermaid-authoring-guidelines/references/other-kinds.md`
- `.agent/skills/mermaid-authoring-guidelines/references/layout-and-planarity.md`
- `.agent/skills/mermaid-authoring-guidelines/references/renderer-facts.md`
- `.agent/skills/mermaid-authoring-guidelines/references/paired-examples.md`
- `.agent/skills/mermaid-authoring-guidelines/references/review-checklist.md`
- `.agent/skills/mermaid-authoring-guidelines/references/eval-results.md`
- `.agent/skills/mermaid-authoring-guidelines/scripts/mermaid_model.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/planarity.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/svg_geometry.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/render_check.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/measure_text.mjs`
- `.agent/skills/mermaid-authoring-guidelines/scripts/setup_renderers.sh`
- `.agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/__init__.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_lint_mermaid.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_planarity.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_svg_geometry.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_plan_gantt.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_notation_consistency.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_paired_examples.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/expected.json`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/paired-examples-geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_render_check.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_setup_renderers.py`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/references-geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/plan-example.json`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/plan-example-geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-tree.mmd`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-tree-v10.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-tree-v11.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-k33.mmd`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-k33-v10.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-k33-v11.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-title.mmd`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-title-v10.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-title-v11.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-through.mmd`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-through-v10.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-through-v11.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-state.mmd`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-state-v10.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-state-v11.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-long.mmd`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-long-v10.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-long-v11.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-gantt.mmd`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-gantt-v10.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-gantt-v11.svg`
- `.agent/skills/mermaid-authoring-guidelines/evals/README.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/evals.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/.gitignore`
- `.agent/skills/mermaid-authoring-guidelines/evals/PROVENANCE.txt`
- `.agent/skills/mermaid-authoring-guidelines/evals/prompts/task-template.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/run_evals.py`
- `.agent/skills/mermaid-authoring-guidelines/evals/render_corpus.py`
- `.agent/skills/mermaid-authoring-guidelines/evals/grade_figures.py`
- `.agent/skills/mermaid-authoring-guidelines/evals/fidelity.py`
- `.agent/skills/mermaid-authoring-guidelines/evals/stats.py`
- `.agent/skills/mermaid-authoring-guidelines/evals/selftest_figure_evals.py`
- `.agent/skills/mermaid-authoring-guidelines/evals/calibration/labels.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c0-control-thumbnails/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c0-control-thumbnails/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c0-control-thumbnails/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c0-control-thumbnails/fail.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c1-wms-container-view/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c1-wms-container-view/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c1-wms-container-view/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c1-wms-container-view/fail.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c2-card-3ds-sequence/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c2-card-3ds-sequence/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c2-card-3ds-sequence/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c2-card-3ds-sequence/fail.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c3-leave-request-lifecycle/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c3-leave-request-lifecycle/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c3-leave-request-lifecycle/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c3-leave-request-lifecycle/fail.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c4-reporting-migration-gantt/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c4-reporting-migration-gantt/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c4-reporting-migration-gantt/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c4-reporting-migration-gantt/fail.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c5-sales-pipeline-dataflow/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c5-sales-pipeline-dataflow/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c5-sales-pipeline-dataflow/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c5-sales-pipeline-dataflow/fail.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c6-clinic-deployment/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c6-clinic-deployment/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c6-clinic-deployment/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c6-clinic-deployment/fail.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c7-refund-decision/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c7-refund-decision/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c7-refund-decision/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c7-refund-decision/fail.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c8-frontends-services-k33/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c8-frontends-services-k33/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c8-frontends-services-k33/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/c8-frontends-services-k33/fail.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/f1-ci-stages-terminal/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/f1-ci-stages-terminal/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/f1-ci-stages-terminal/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/f1-ci-stages-terminal/fail.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/f2-roles-operations-matrix/document.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/f2-roles-operations-matrix/key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/f2-roles-operations-matrix/pass.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/fixtures/f2-roles-operations-matrix/fail.md`

`.agent/skills/mermaid-authoring-guidelines/evals/corpus/` holds the campaign. H4 appends its file
list to this PLAN, one full path per item, generated from the tree before the reviews.

The run's own `docs/TASK.md`, `docs/PLAN.md` and the TASK 107 archive pair are declared by §5.

**Rollback point.** Base `ee69bf2e0e35b11a2c525a5b75d64879d903c232`, clean at the start of the run.
No copy of a repository file is written. Renders, renderer installs and eval temporary
directories live outside the repository under the D17 licence and are not part of the rollback
set. Fallback follows `framework-upgrade` §5 over the paths above.

## Revision-3 deltas

TASK revision 3 changed definitions that Clusters B–G implement. A delta pass after the first
build applies them:

- B: the `text figure` marker (R2.5); caption above and legend below (R3.7); line counts and the
  message and note limits (D25); duplicate edges per R3.3.
- C: hash-bound evidence (R7.8, A19); text contrast in the light and dark render (R7.5–R7.6);
  `--no-dark` as `not rendered` (R7.4); the npm cache in the install home (R7.2).
- D: the empty region under 8 tasks (R8.5); the hash-bound example (A3).
- E: key kinds and acceptable forms (R11.2–R11.3); D8 scores and validity order; the D18 budget
  stop; the D16 calibration step; the named variable list and `--no-session-persistence` (R11.4);
  the hash check before a paid run (R11.10).
- F: the routing anchor and the `none` row (R1.4); the UC-3 exception in Step 0; paired-example
  geometry bound to fence hashes (R9.5).
- G: the UC-3 exception in the bootstrap files; the surfaces of R10.3 and R10.5 (G9).

## Cluster A — skeleton, data, stubs (done)

- [x] A1. `init_skill.py mermaid-authoring-guidelines --tier 2 --path <absolute .agent/skills>`;
      placeholders removed.
- [x] A2. `S/assets/notation.json`: budgets (D14), thresholds (R7.6), label limits (D25), settings
      lines, palettes, kinds.
- [x] A3. Stubs with final signatures and D20 exit codes.
- [x] A4. Stub tests green (10 cases).
- [x] A5. `S/SKILL.md` with every required section and the routing table; `validate_skill.py` 0 errors.

## Cluster B — model, lint, planarity (R2.7, R6, D21, D25)

- [x] B1. `mermaid_model.py`: fences with line numbers and neighbouring paragraphs; settings from
      `%%{init}%%` and frontmatter; parsers for flowchart, sequence, state, gantt, ER, `text`.
- [x] B2. `planarity.py`: the edge bounds, then an exact test per biconnected component of the
      simple undirected graph.
- [x] B3. `lint_mermaid.py`: the rules of TASK R6.3 with probe pairs; label limits in characters
      (D25); `--probe`, `--json`, `--inventory`; D20 exit codes.
- [x] B4. Tests: the rule ids as a literal list (R6.6); one case per rule; exit codes; caption and
      legend by position in English and Russian text; `K3,3`, `K5` and planar controls.
- [x] B5. Run the lint over the seven figures of TASK §1, as an advisory sweep (R6.7).

## Cluster C — geometry, render, setup (R7, §3)

- [x] C1. `svg_geometry.py`: transforms, path flattening, crossings, edges through nodes and
      titles, overlaps, size, effective font. Invisible links are excluded.
- [x] C2. `assets/renderers/<tag>/package.json` with exact versions; lockfiles generated once;
      `setup_renderers.sh` installs with `npm ci --ignore-scripts`, reuses a cached
      `chrome-headless-shell`, keeps the sandbox unless `MERMAID_RENDER_NO_SANDBOX=1`.
- [x] C3. `measure_text.mjs` and `render_check.py`: 11.17.2, 10.9.8 and a dark 11.17.2 by default;
      `securityLevel: strict`; no network; evidence JSON with versions; D20 exit codes.
- [x] C4. Render the seven `fx-*.mmd` fixtures in 10.9.8 and 11.17.2 into
      `S/scripts/tests/fixtures/`. Write `expected.json` from the PNGs, looked at one by one.
- [x] C5. `test_svg_geometry.py` over the committed SVGs. No node is needed.
      1. The clean tree has 0 crossings; `K3,3` has 1 or more.
      2. The title case has 1 or more title crossings; the forced case has an edge through a node.
      3. The state, the long sequence label and the gantt match `expected.json`.

## Cluster D — plan chart (R8, D19)

- [x] D1. `plan_gantt.py`: the JSON schedule and the block under `<!-- contract:schedule -->`;
      schedule, critical path, ready list; validation; the encoding of TASK R8.3; markers
      `generated:plan-gantt-start` and `-end`; `--write`, `--check`, `--stages`.
- [x] D2. `test_plan_gantt.py`: schedule values on the 10-task example; each invalid input; label
      sanitizing; `--check` on a stale and a current block; a Russian plan equals its English twin.
- [x] D3. Render the 10-task example; bar starts in the SVG equal the computed early starts (A3).

## Cluster E — eval instrument and the `without_skill` arm (R11)

- [x] E1. The eleven cases under `S/evals/fixtures/`: `document.md`, `key.json`, `pass.md`,
      `fail.md`. No case reuses a name of the paired examples.
- [x] E2. `evals.json` (schema `mermaid-evals/v1`) with the headline and contract check families
      of TASK R11.7–R11.8, and `prompts/task-template.md`.
- [x] E3. `run_evals.py`, `render_corpus.py`, `fidelity.py`, `stats.py`, `grade_figures.py`.
- [x] E4. `selftest_figure_evals.py`: sentinels; the arm byte-diff; isolation; environment
      stripping; key integrity; pass and fail fixtures; grader unit cases; report re-derivation.
- [x] E5. `S/evals/README.md` with the D8 rule. Record the sha256 of `evals.json`, every key, the
      template and the README in `docs/reviews/framework-audit-108.md` and in `PROVENANCE.txt`
      before the first paid run (R11.10).
- [x] E6. Install the renderers (C2). Run `run_evals.py --arm without_skill --reps 3`, then
      `render_corpus.py`, then `grade_figures.py`. Expected: 33 graded runs, within D18.
- [x] E7. Label the calibration set (D16) into `evals/calibration/labels.json` before reading any
      grading.

## Cluster F — skill text, references, examples, the `with_skill` arm (R1–R5, R9)

- [x] F1. The references: `ascii.md`, `flowchart.md`, `sequence.md`, `state.md`, `gantt.md`,
      `other-kinds.md`, `layout-and-planarity.md`, `renderer-facts.md`, `review-checklist.md`.
      Every template passes the light and the dark render.
- [x] F2. `paired-examples.md`: N1–N14, P1–P14 and P15 with their source lines; P1, P4 and P9
      reworked; every negative fails a named rule or threshold.
- [x] F3. `render_check.py references/paired-examples.md --fixture
      S/scripts/tests/fixtures/paired-examples-geometry.json`; the other references into
      `references-geometry.json`; `test_paired_examples.py` (A5).
- [x] F4. `test_notation_consistency.py`: every value quoted in `SKILL.md` and the references
      equals `notation.json`.
- [x] F5. `validate_skill.py S/` 0 errors; `scan_register.py` 0 warn on `SKILL.md` and references.
- [x] F6. `run_evals.py --arm with_skill --reps 3`, then render and grade. Write `report.json` and
      `benchmark.md` with every D8 criterion marked met or not met (A7). D8 not met → one
      revision round per D18.
- [x] F7. `references/eval-results.md` and the Validation Evidence lines of `SKILL.md`.

## Cluster G — integration (R10, R12.2)

- [x] G1. `architecture-format-core` §2.2, §3.3, line 12; `architecture-format-extended` line 48.
- [x] G2. `documentation-standards` §5.6 "Figures"; §4.4 rows for `contract:schedule`,
      `generated:plan-gantt-start` and `generated:plan-gantt-end`; §5.1 scoped to Markdown tables.
- [x] G3. `04_architect_prompt.md`, `05_architecture_reviewer_prompt.md`, `06_planner_prompt.md`.
- [x] G4. The four checklists: figure items and Script Contract entries (D24), after each
      References section.
- [x] G5. `.claude/agents/architect.md`; `.claude/settings.json` allows the lint and
      `plan_gantt.py --check` only (D9).
- [x] G6. `skill-phase-context`, `SKILL_TIERS.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` with the
      conditional load and the medium rule (D2).
- [x] G7. `brainstorming`, `threat_model.md`, `skill-reverse-engineering`,
      `skill-planning-format` and its plan template (schedule block, markers).
- [x] G8. `tests/test_mermaid_wiring.py`, registered in `CURATED_UNITTEST_MODULES`.
- [x] G9. The four gate workflows name the figure lint and `plan_gantt.py --check` in the caller's
      evidence; `07_plan_reviewer_prompt.md` lists that evidence; `PLAN_EXAMPLE.md` carries the
      schedule block and the markers.

## Cluster H — docs, release, gates, reviews (R12, R13)

- [x] H1. `System/Docs/SKILLS.md` entry (R12.4 count sentences); `framework-gates.yml` steps for
      the skill's tests, the lint gate and the eval selftest; both changelogs v3.33.0 with the
      consumer migration note and the D8 outcome; WI-21 to WI-25 with their index lines.
- [x] H2. Gates: every job of `framework-gates.yml` run locally (A9); `scan_register.py` on every
      edited Markdown file against its base (A10) and on the skill's Markdown (A14).
- [x] H3. `check_positional_refs.py --targets-changed --fix` (`framework-upgrade` §4.5).
- [x] H4. Append the corpus file list to this PLAN. `git status --short` lists only declared paths.
- [x] H5. Review rounds: `code-reviewer` and `security-auditor` on a frozen tree, fingerprint
      recorded in the audit. Fix loop until no blocking finding remains (A12).


## Paths added at H4

H4, 2026-10-03. The run created these paths after the PLAN was written: the review loop, the
calibration, amendment `a1`, and the corpus of campaign `2026-10-opus55-xhigh-r1`. One full path
per item. `review-095-independent.md` is the line-number repair of H3.

### Late paths

- `.agent/skills/mermaid-authoring-guidelines/evals/AMENDMENTS.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/amendments/a1.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/amendments/a1/c0-control-thumbnails.key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/amendments/a1/c5-sales-pipeline-dataflow.key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/amendments/a1/c6-clinic-deployment.key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/amendments/a1/c7-refund-decision.key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/amendments/a1/c8-frontends-services-k33.key.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/calibration/evidence.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/calibration/worksheet.json`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-names-v10.measure.json`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-names-v10.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-names-v11.measure.json`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-names-v11.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-names.mmd`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-skip-v10.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-skip-v11.svg`
- `.agent/skills/mermaid-authoring-guidelines/scripts/tests/fixtures/fx-seq-skip.mmd`
- `docs/reviews/review-095-independent.md`

- `docs/backlog/wi-26-figure-eval-campaign-2-thresholds-from-a-pilot-large-cases-keys-checked-before-registration.md`
- `docs/backlog/wi-27-fix-loops-hand-off-a-differential-replay-of-the-stored-corpus.md`
- `docs/backlog/wi-28-simplify-mermaid-authoring-guidelines-by-measured-use.md`
- `docs/backlog/wi-29-installer-leaves-declared-skill-development-paths-out-of-copy-installs.md`
- `docs/backlog/wi-30-renderer-supply-chain-v10-lockfile-mermaid-cli-request-filter-browser-hash.md`
- `docs/backlog/wi-31-anchored-allow-rules-sha-pinned-actions-a-full-fingerprint-and-a-nested-lockfile-audit.md`
- `docs/backlog/wi-32-lint-and-scanner-follow-ups-from-task-108-reviews.md`
- `docs/backlog/wi-33-skill-creator-scripts-target-python-3-14-not-3-9.md`

### Corpus

- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/attempts.jsonl`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/benchmark.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/benchmark.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/campaign.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/errors.jsonl`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-0-control-thumbnails/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-1-wms-container-view/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-10-roles-operations-matrix/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-2-card-3ds-sequence/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-3-leave-request-lifecycle/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-4-reporting-migration-gantt/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-5-sales-pipeline-dataflow/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-6-clinic-deployment/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-7-refund-decision/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-8-frontends-services-k33/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/with_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/eval_metadata.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-1/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-1/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-1/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-1/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-1/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-1/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-2/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-2/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-2/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-2/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-2/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-2/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-3/envelope.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-3/grading.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-3/outputs/answer.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-3/outputs/geometry.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-3/run.meta.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/eval-9-ci-stages-terminal/without_skill/run-3/timing.json`
- `.agent/skills/mermaid-authoring-guidelines/evals/corpus/2026-10-opus55-xhigh-r1/report.json`

<!-- contract:coverage -->

## Requirement coverage

| Requirement | Clusters |
| :--- | :--- |
| R1 | A, F |
| R2 | B, F |
| R3, R4, R5 | F |
| R6 | A, B |
| R7 | A, C |
| R8 | A, D |
| R9 | F |
| R10 | G |
| R11 | E, F |
| R12 | B, C, D, E, F, G, H |
| R13 | H |
