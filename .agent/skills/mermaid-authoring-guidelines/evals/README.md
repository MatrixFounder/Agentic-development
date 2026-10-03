# mermaid-authoring-guidelines evals — what each instrument measures, and what none of it shows

TASK 108 R11. The question: does `SKILL.md` with its routed references change the figures a model
writes into a document? Two arms answer it. They differ in one input (ARCHITECTURE §7.6, L5).

| Arm | Input |
| :--- | :--- |
| `without_skill` | the case prompt |
| `with_skill` | one skill block, then the same case prompt byte for byte |

The skill block holds `SKILL.md` and the reference files of one row of its routing table.
`run_evals.py` reads that table at run time:

- the table is the one below the anchor line `<!-- contract:routing -->`;
- the first code span of column 1 is the figure kind, every code span of column 2 is a file;
- the header row is not read, so its wording and language do not matter;
- the row is the `kind` of the case's key;
- the row `none` names no reference, so a case of kind `none` gets `SKILL.md` alone.

## Instruments

| File | Role | Cost |
| :--- | :--- | :--- |
| `run_evals.py` | runs both arms with `claude -p` and writes the corpus | tokens |
| `render_corpus.py` | renders every Mermaid figure and writes `outputs/geometry.json` per run | node and a browser |
| `grade_figures.py` | grades every run against the checks of `evals.json` | none; reads committed files only |
| `fidelity.py` | maps the elements of an answer to the case key | none |
| `stats.py` | computes the case-cluster bootstrap interval and the sign test | none |
| `selftest_figure_evals.py` | checks the instrument itself | none; spawns no agent and renders nothing |

`run_evals.py` is the only script here that spends tokens. CI runs the selftest, never a campaign.

## Cases

Eleven cases live under `fixtures/<slug>/`: `document.md`, `key.json`, `pass.md` and `fail.md`.
`evals.json` (schema `mermaid-evals/v1`) holds the request, the environment line and the output
instruction of each case.

| Id | Slug | Kind | Acceptable forms | Medium | Role |
| ---: | :--- | :--- | :--- | :--- | :--- |
| 0 | `c0-control-thumbnails` | flowchart | flowchart | document | control without decoys |
| 1 | `c1-wms-container-view` | flowchart | flowchart | document | container view |
| 2 | `c2-card-3ds-sequence` | sequence | sequence | document | one payment scenario |
| 3 | `c3-leave-request-lifecycle` | state | state | document | lifecycle, Russian |
| 4 | `c4-reporting-migration-gantt` | gantt | gantt | document | calendar plan in working days |
| 5 | `c5-sales-pipeline-dataflow` | flowchart | flowchart | document | data flow |
| 6 | `c6-clinic-deployment` | flowchart | flowchart | document | deployment, Russian |
| 7 | `c7-refund-decision` | flowchart | flowchart | document | decision flow |
| 8 | `c8-frontends-services-k33` | flowchart | flowchart, table | document | three callers to three services |
| 9 | `f1-ci-stages-terminal` | none | ascii, list | terminal | stage order in a terminal reply |
| 10 | `f2-roles-operations-matrix` | none | table | document | role-by-operation relation |

A decoy is a relation, number, group or writer that the document does not state and that a model
is likely to draw. Each key lists:

- the entities with aliases, and the stated relations, numbers and groups;
- the decoys, typed from the vocabulary `decoy_types` of `evals.json`;
- `kind`: the figure kind the request names, or `none` when it names none;
- `acceptable_forms`: the Mermaid kinds, `table`, `list` or `ascii` that answer the case;
- the check families that apply.

C0 and C8 ask for a figure of relations between components. Step 1 of `SKILL.md` gives that
concern, structure, the kind `flowchart`. `evals.json` repeats each key's kind as `figure_kind`.
`run_evals.py` refuses a difference between the two (exit 2). Keys are written before any run.

An answer may hold Mermaid fences, Markdown tables, lists and `text` fences. The fidelity matcher
reads an ASCII chain or tree and a Markdown table with the key semantics it applies to a Mermaid
figure. A key names three sets of check families:

- `families`: the families that apply;
- `families_conditional`: the ones that apply only to an answer of a given form;
- `families_not_applicable`: the ones that never apply.

## Checks

`evals.json` holds the check texts; `grading.json` copies them verbatim.

- **Headline checks Q01–Q17.** Families: renders (Q01, Q02), geometry (Q03–Q06), budget (Q07),
  concern (Q08), fidelity (Q09–Q12), docs (Q13, Q14), form (Q15), ascii (Q16), colour (Q17).
- **Form fit, Q15.** Every figure takes a form of the key's `acceptable_forms`. A terminal reply
  holds no Mermaid fence and no image.
- **Contract checks K01–K09** test whether the skill block reached the model: settings line,
  palette, shapes, caption and legend form and position, direction, names, one edge per pair,
  soft budget. They enter criterion C1 and never enter H, H-core or `expectations`.

`render_corpus.py` renders each figure four times:

| Render key | Mermaid | Page | Role |
| :--- | :--- | :--- | :--- |
| `v11` | 11.17.2, which GitHub runs | light | headline |
| `v11-dark` | 11.17.2, theme `dark` | GitHub's dark page colour | headline |
| `v10` | 10.9.8, which JetBrains IDEs run | light | headline |
| `v12` | 12.1.0 | light | information; enters no check |

A figure passes a geometry check only when it passes in `v11` and `v10`. Legibility, Q06, also
requires the contrast minimum for every text whose colour or background the figure sets. That
holds in `v11`, `v10` and `v11-dark`.

The thresholds come from `assets/notation.json`. The values the decision depends on, at
registration:

| Value | `notation.json` key | At registration |
| :--- | :--- | ---: |
| document column | `column_px` | 900 px |
| minimum effective font | `min_effective_font_px` | 10 px |
| crossings allowed | `thresholds.max_crossings` | 2 |
| contrast minimum | `contrast_min` | 4.5 |

## Pre-registered decision rule (TASK 108 D8, revision 3)

This section is written before the first paid run. Its sha256 is recorded in `PROVENANCE.txt`
and in `docs/reviews/framework-audit-108.md`. A threshold changed after an arm's result is read
voids the campaign.

### Scores

- A run's headline score H is the fraction of the case's applicable headline checks it passes.
- A per-figure check passes only when every figure of the run passes it.
- A run whose answer holds no figure in any form fails every applicable check.
- H-core is the same score without the budget, caption and legend checks: Q07, Q13 and Q14.
- A case's score is the median over its repetitions.
- Δ_H is the mean, over the ten cases C1–C8, F1 and F2, of the `with_skill` case score minus the
  `without_skill` case score. Δ_H-core is the same mean over H-core.
- C0 is not in Δ_H. It enters V3, and the clause of H3 on cases behind by more than 0.10.

### Validity criteria, evaluated first

A failure here marks the campaign invalid. The instrument is fixed, and the affected runs are run
again or graded again. This uses no revision round.

| # | Criterion |
| :--- | :--- |
| V1 | no ungraded infrastructure failure; the served model is the pinned one in every run |
| V2 | detector precision and recall ≥ 0.9 per defect type, and Cohen's κ ≥ 0.8, on the calibration set |
| V3 | control C0: `without_skill` H-core ≥ 0.9 |
| C1 | contract-check rate ≥ 0.8 with the skill; the rate without it is reported for information |

### Effect criteria

The claim "the model without the skill does much worse" holds only when all four hold on a valid
campaign.

| # | Criterion |
| :--- | :--- |
| H1 | Δ_H ≥ 0.25 and its 95 % case-cluster lower bound ≥ 0.10 |
| H2 | Δ_H-core ≥ 0.15 and its lower bound > 0 |
| H3 | `with_skill` ahead on 8 or more of the ten cases; behind beyond 0.10 on none, C0 included |
| V4 | Δ_H > 0 with any one check family left out |

The sign test is reported as information. H3 is a breadth criterion, not a significance test.

### Definitions fixed with the rule

- **Ahead** means a case difference above 0. **Behind beyond 0.10** means a case difference
  below −0.10.
- **Interval.** A two-stage bootstrap with 10,000 resamples and seed 0:
  1. each resample draws the ten cases with replacement;
  2. it then draws repetitions with replacement inside each arm of each drawn case;
  3. a case score in a resample is the median of its drawn repetitions;
  4. the bound is the 2.5th percentile of the resampled Δ.
- **Contract-check rate.** The fraction of applicable contract checks a run passes, averaged per
  case and then over the cases where any contract check applies.
- **V2.** Measured on the calibration set of the next section. κ is the agreement between the
  labels and the detector's verdicts, per defect type. The report marks V2 `corroborated`.
- **V4.** The families are the nine of `evals.json`: renders, geometry, budget, concern, fidelity,
  docs, form, ascii and colour.

### Outcomes

| Outcome | Consequence |
| :--- | :--- |
| a validity criterion fails | the campaign is invalid; the instrument is fixed (TASK UC-5 A2) |
| valid, every effect criterion met | the claim holds |
| valid, an effect criterion not met | the skill reached the model (C1) and missed the margin; one revision round follows |
| the budget runs out | `report.json` marks each criterion it could not evaluate `not evaluated (budget)` |

## Calibration (TASK D16), between rendering and grading

1. Both arms are run and rendered first.
2. A seeded sample of at least 30 outputs is drawn over all outputs, stratified by case and arm.
   It is drawn before any grading is read, and its seed is recorded with the labels.
   `grade_figures.py --calibration-sample 30 --seed S` writes two files: `worksheet.json`, what
   the labeller reads, and `evidence.json`, what the detector reads.
3. The orchestrating model labels each sampled output per defect type from its PNGs and its text.
   It does not see the detector's verdicts: `evidence.json` stays closed until every item is
   labelled. The labels go to `calibration/labels.json`, and `evidence.json` is committed beside
   them.
4. A defect type with fewer than 3 positives in the sample is topped up. The top-up comes from the
   `fail.md` fixtures and the negative paired examples that carry the type. Each top-up item is
   recorded as seeded. `--fixture-corpus D` lays the `fail.md` fixtures out as a campaign in `D`;
   `render_corpus.py D` renders it; `--seed-corpus D` adds its items to the sample.
5. `grade_figures.py` grades the corpus and computes V2 from the labels, per defect type. A type
   with no positive has no precision, so V2 is not met while one remains.

## Budget and the revision round (TASK D18)

The campaign spends at most 60 USD across all its runs. Planned: 11 cases × 2 arms ×
3 repetitions = 66 runs of `claude-opus-5-5` at effort `xhigh`.

- **Measure.** `run_evals.py` sums `total_cost_usd` over the run envelopes. Every attempt appends
  its cost to the campaign's `attempts.jsonl`. The sum covers every such file under `corpus*/`,
  so both arms and the revision round share it.
- **Unknown cost.** An attempt that reports no cost, such as a timeout, counts at the mean cost
  per run.
- **Projection.** A run is projected at the mean cost per run of its arm so far. Before its arm
  has a recorded cost, the mean of all runs applies; before any cost, `--run-cap-usd`.
- **Stop rule.** A run starts only while the spend, the projections of the runs in progress and
  its own projection stay within the cap.
- **Run cap.** Each run passes `--max-budget-usd 5` to the CLI.

When an effect criterion of D8 is not met, one round of skill revisions follows. A revision
changes a rule for every figure, never for one case. The second round draws the `with_skill` arm
again, into a new campaign directory. `grade_figures.py --baseline-corpus <first round>` reads
the `without_skill` arm from the first round. The report shows both rounds and labels the second
`post-revision, same cases`.

## Provenance (TASK R11.10)

`PROVENANCE.txt` sits next to `evals.json`. It holds one line per file, as `shasum -a 256` prints
it: `<sha256>  <path relative to evals/>`. Lines that start with `#` are comments.

- It lists `README.md`, `prompts/task-template.md` and every `fixtures/*/key.json`.
- A further listed file, `evals.json` for example, is verified as well.
- The same hashes go to `docs/reviews/framework-audit-108.md` and to the operator before the first
  paid run.

```sh
cd .agent/skills/mermaid-authoring-guidelines/evals
shasum -a 256 README.md prompts/task-template.md fixtures/*/key.json > PROVENANCE.txt
```

`run_evals.py` refuses a paid run (exit 2) in three states:

- `PROVENANCE.txt` is absent;
- a required file is not listed in it;
- a listed file has another sha256.

`--dry-run` reports the state and runs without the file. Every run record and `campaign.json`
carry the verified hashes. A campaign directory started under other hashes refuses further runs.

## Running

Dry run first. It prints every command, the bundle files with their sha256 and word counts, the
provenance state and the budget projection, and spawns nothing:

```sh
python3 .agent/skills/mermaid-authoring-guidelines/evals/run_evals.py \
  --dry-run --cases 8 --arm with_skill --reps 1
```

The dry run exits 2 while a bundle file, a key or a case document is absent. It also prints the
words of every routed bundle against the limit of TASK R1.5.

A campaign, in order (TASK UC-5):

1. Install the renderers.
2. Write `PROVENANCE.txt` and record the same hashes in the audit.
3. Run both arms; `without_skill` first, as PLAN 108 orders.
4. Render the corpus.
5. Draw and label the calibration sample (previous sections).
6. Grade the corpus.

```sh
E=.agent/skills/mermaid-authoring-guidelines/evals
SCRATCH="$(mktemp -d)"   # outside the repository (TASK D17)
bash .agent/skills/mermaid-authoring-guidelines/scripts/setup_renderers.sh --forward
python3 $E/run_evals.py --campaign-id 2026-10-opus55-xhigh-r1 --arm without_skill --jobs 4
python3 $E/run_evals.py --campaign-id 2026-10-opus55-xhigh-r1 --arm with_skill --jobs 4
python3 $E/render_corpus.py $E/corpus/2026-10-opus55-xhigh-r1
# step 5: sample, top up from the fail.md fixtures, label; no grading is read before the labels
python3 $E/grade_figures.py --fixture-corpus "$SCRATCH/fixture-corpus"
python3 $E/render_corpus.py "$SCRATCH/fixture-corpus"
python3 $E/grade_figures.py --corpus $E/corpus/2026-10-opus55-xhigh-r1 \
  --calibration-sample 30 --seed 108 --seed-corpus "$SCRATCH/fixture-corpus" --out $E/calibration
# the labels go to $E/calibration/labels.json, beside evidence.json
python3 $E/grade_figures.py --corpus $E/corpus/2026-10-opus55-xhigh-r1
```

Model, effort, repetitions and budget default to the `campaign` block of `evals.json`. `--reps`
is odd, so each case has a median run. A run directory that exists is never written again, so
the same command resumes a stopped campaign. One campaign directory holds one model, one effort,
one set of provenance hashes and one prompt per case and arm. A changed prompt needs a new
`--campaign-id`.

| Exit | `run_evals.py` | `render_corpus.py` |
| ---: | :--- | :--- |
| 0 | every planned run completed or existed | every figure classified in each headline render |
| 1 | a run failed, or the budget stopped runs | an infrastructure failure remains; run again |
| 2 | instrument broken, provenance absent or changed, or not isolated | `not rendered: <reason>` (ARCHITECTURE §10.5, L6) |
| 3 | usage error | usage error |

## Corpus layout

```text
corpus/<campaign-id>/
├── campaign.json · attempts.jsonl · errors.jsonl
└── eval-<id>-<name>/
    ├── eval_metadata.json
    └── <arm>/
        ├── eval_metadata.json
        └── run-<k>/
            ├── outputs/answer.md · outputs/geometry.json
            ├── run.meta.json · timing.json · envelope.json
            └── grading.json
```

The layout is the one `skill-creator` reads, so `aggregate_benchmark.py` and the review viewer
work on it. `run.meta.json` records:

- the model, the effort, the served model and the CLI version;
- the key's kind and the sha256 of the prompt and of each bundle file, with word counts;
- the provenance hashes and the names of the removed environment variables;
- cost, tokens, duration and permission denials.

`geometry.json` holds, per figure and render key, the evidence of `render_check.py`:

- the fence sha256 and line, and the versions of mermaid, mermaid-cli and the browser;
- the metrics with their contrast entries, the findings, and the font family drawn;
- the sha256 of the SVG, of the PNG and of the render instrument.

Renders stay outside the repository; only `geometry.json` is committed. An edit to the render
instrument renders the corpus again on the next invocation, so both arms share one instrument.

## Isolation

- Each run starts in a fresh `tempfile.mkdtemp()` directory. `leaks_above` refuses one with
  `CLAUDE.md`, `CLAUDE.local.md`, `.agent`, `.claude`, `AGENTS.md`, `GEMINI.md` or `.git` at or
  above it.
- `--safe-mode`, `--tools ""`, `--disable-slash-commands` and `--strict-mcp-config` with an empty
  `--mcp-config` turn off tools, skills, MCP servers and slash commands.
- `--model` and `--effort` pass the model and the effort as flags.
- The child environment loses a named list of variables, `REMOVED_ENV_VARS` of `run_evals.py`:
  - the session-control variables of the calling session, `CLAUDECODE` and `CLAUDE_EFFORT`
    among them;
  - the variables that override the pinned model, effort, thinking budget, output limit or
    session persistence.
- Authentication variables pass: `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY`,
  `CLAUDE_CONFIG_DIR`, `HOME`.
- Each run record names the variables removed from its environment.
- stdin is closed, and `--no-session-persistence` keeps the runs out of the session store.
- Before the first run, `run_evals.py` checks every flag it passes against `claude --help`.

`~/.claude` stays outside the `leaks_above` walk. It is user-level configuration, the same in both
arms, and `--safe-mode` turns off what it holds.

## What none of this shows

- The cases are seeded around known failure modes. Δ measures how much the skill fixes those
  modes, not the mean gain on an arbitrary figure request.
- The runs measure the guidance under perfect loading. They do not measure whether the skill
  triggers, or the render-look-fix loop that the skill also teaches.
- F1 measures the wording of Step 0 in `SKILL.md` (TASK R11.13). The bootstrap files carry the
  medium rule as well (TASK D2), and no eval run loads them, so F1 does not measure that delivery.
- One model at one effort was measured.
- Headless Chrome draws with the fonts of the machine that renders. GitHub's page can lay out text
  a few pixels wider or narrower.
- A passing selftest says the instrument works. It says nothing about the skill; only a campaign
  produces evidence about it.

## Departures from the design brief of the research phase

| Brief | This set |
| :--- | :--- |
| renders in 12.1.0 and 10.9.8 | headline renders in 11.17.2, a dark 11.17.2 and 10.9.8; 12.1.0 for information |
| `gold.md`, `naive.md` | `pass.md`, `fail.md`, and `fail_expect_failed` in `evals.json` |
| nine cases | eleven: C0, eight decoy cases, F1 in a terminal, F2 as a role-by-operation relation |
| checks Q01–Q14, K01–K08 | checks Q01–Q17, K01–K09; Q13 and Q14 count either position next to the fence |
| one environment line | one line for document cases, one for the terminal case, one for F2 |
| keys without medium or form | keys add `medium`, `kind`, `acceptable_forms`, `families` and the F1 and F2 facts |
| a routing table found by its header | a routing table found by its anchor and read by column position |
| a campaign summary in `PROVENANCE.txt` | one sha256 line per file, checked before every paid run |
| bars of H1–H3 to decide | TASK 108 D8: validity first, then H1–H3 and V4 over ten cases |
| a fixed opening sentence | "You are working in a project repository", which fits the terminal case too |

## Deliberately not here

- **Trigger evaluation of the description.** A backlog work-item.
- **A tool-loop variant and natural cases.** They go into a new eval file, as `skill-creator`
  advises for a changed contract.
- **A placebo arm.** The brief offered it as an option; TASK 108 does not require it.
