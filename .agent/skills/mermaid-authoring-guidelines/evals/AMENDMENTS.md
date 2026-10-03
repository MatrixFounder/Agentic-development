# Amendments to a registered campaign

TASK 108 R11.2 and R11.10 register the files a campaign grades against: `evals.json` and every
`fixtures/*/key.json`. `PROVENANCE.txt` lists their sha256 before the first paid run, and
`run_evals.py` copies the verified hashes into `campaign.json` and into every run record.

`grade_figures.py` grades a campaign only under those files. Before it writes a report, it
compares the sha256 of `evals.json` and of every key it graded with the hashes the campaign
recorded. A file with another sha256 is an instrument error: exit 2, and no report.

An amendment is the one sanctioned departure. It names each changed file, the hash the campaign
registered for it, the amended file and its hash, and the reason. A report graded under an
amendment is a post-hoc sensitivity analysis, never the pre-registered result:

- `report.json` carries `"post_hoc": true` and the amendment under `provenance.amendment`;
- the decision statement and the first line of `benchmark.md` start with `POST-HOC SENSITIVITY`;
- the pre-registered report stays the one graded without an amendment.

## When an amendment applies

- A review finds that a registered key contradicts its own case document or the skill's rule,
  and the operator decides to measure the effect of a correction.
- A registered text, such as `README.md`, needs a correction after a campaign has started. The
  grader reads no README, so the correction is an entry of the section "Deviations from the
  registered README" below, not an edit of the registered file.

A grader defect is not an amendment. It is an instrument fix (TASK D8, UC-5 A2): the grader is
corrected, and the campaign is graded again under its registered files.

## The file

An amendment is a JSON file under `evals/amendments/`. The files it supplies sit under the same
directory, for example `evals/amendments/a1/`.

```json
{
  "schema": "mermaid-eval-amendment/v1",
  "id": "a1",
  "campaign": "2026-10-opus55-xhigh-r1",
  "decided_by": "operator",
  "date": "2026-10-03",
  "reason": "the C7 key lacks the start wording of its own document",
  "files": [
    {
      "registered": "fixtures/c7-refund-decision/key.json",
      "registered_sha256": "<64 hex digits: the hash in campaign.json>",
      "amended": "amendments/a1/c7-refund-decision.key.json",
      "amended_sha256": "<64 hex digits: the hash of the amended file>",
      "reason": "EI-09: the document's line 3 names the start 'Customer asks for a refund'"
    }
  ]
}
```

| Field | Rule |
| :--- | :--- |
| `schema` | `mermaid-eval-amendment/v1` |
| `id` | a short token: letters, digits, `.`, `_`, `-` |
| `campaign` | optional; when present, the name of the graded campaign or its baseline |
| `decided_by`, `reason` | non-empty texts |
| `date`, `status` | optional; `status` is `POST-HOC` for an amendment made after the runs |
| `files[].registered` | a path relative to `evals/`, as `campaign.json` lists it |
| `files[].registered_sha256` | the hash the campaign registered for that path |
| `files[].amended` | a path relative to `evals/`, inside `evals/amendments/` |
| `files[].amended_sha256` | the sha256 of the amended file |
| `files[].reason` | a non-empty text, naming the finding or the decision |

## What the grader checks

1. The amendment file lies under `evals/amendments/`. Otherwise: usage error, exit 3.
2. The schema, the id, the texts and every entry are well formed. Otherwise: exit 2.
3. Each amended file exists under `evals/amendments/` and has the sha256 the entry records.
   Otherwise: exit 2.
4. An entry does not amend a file to its registered content. Otherwise: exit 2.
5. Each entry's `registered_sha256` equals the hash the graded campaign registered for that
   path. Otherwise: exit 2.
6. Every other graded file has its registered sha256. Otherwise: exit 2.
7. A `campaign` field names the graded campaign or its baseline. Otherwise: exit 2.

The grader then reads the amended content in place of the registered file. Case paths stay
relative to the registered `evals.json`.

## Running it

```sh
E=.agent/skills/mermaid-authoring-guidelines/evals
python3 $E/grade_figures.py --corpus $E/corpus/2026-10-opus55-xhigh-r1 \
  --amendment $E/amendments/a1.json --out "$SCRATCH/post-hoc-a1"
```

Write the post-hoc report beside the pre-registered one, never over it. `--calibration-sample`
accepts `--amendment` as well and stamps the worksheet and the evidence `post_hoc`.

## What a report records in every case

- `provenance.status`: `verified` when every graded campaign recorded its files; `unrecorded`
  for a synthetic or fixture corpus without `campaign.json` and without run records.
- `provenance.files`: per graded file, the sha256 graded and the hash each campaign registered.
- `grader.keys_sha256` and `grader.evals_sha256`: the full hashes graded.
- `grader.normalize_sha256`: the sha256 of the source of the matcher's normalisation rule, so a
  changed rule shows with the key hashes (TASK R11.2).
- `grader.instrument`: the sha256 of `grade_figures.py` and `fidelity.py`. They are recorded,
  not registered: an instrument fix changes them by design.
- `provenance.instrument`: per graded campaign, whether it registered the normalisation rule,
  `grade_figures.py` and `fidelity.py` before its runs, under `campaign.json`
  `provenance.instrument`. Its statement opens a section of `benchmark.md` and a line of the
  summary (EI-13).

Campaign `2026-10-opus55-xhigh-r1` registered `evals.json`, the keys, the README and the prompt
template. It registered no grader hash. Its reports state three facts:

- the normalisation rule, `grade_figures.py` and `fidelity.py` were not registered before the
  runs;
- their sha256 is recorded at grading time;
- a change after the runs shows in that sha256, and nothing refuses it.

## Register

| Id | Campaign | Decided by | Files | Findings |
| :--- | :--- | :--- | :--- | :--- |
| a1 | `2026-10-opus55-xhigh-r1` | the orchestrator of review round 1; the operator has not confirmed it | keys of C0, C5, C6, C7, C8 | EI-02, EI-08, EI-09, EI-27; POST-HOC |

## Amendment a1

Amendment a1 was made on 2026-10-03. That was after the 66 runs of campaign
`2026-10-opus55-xhigh-r1`, and after reviewers had seen per-case scores. Amendment a1 is
POST-HOC: its report is a sensitivity analysis beside the pre-registered report.

| Registered key | Change | Finding |
| :--- | :--- | :--- |
| C0 `c0-control-thumbnails` | `acceptable_forms` becomes `[flowchart, ascii]`; `kind` stays `flowchart` | EI-02 |
| C0 `c0-control-thumbnails` | the originals and the thumbnails prefixes: optional entities with `part_of: mb` | EI-08 |
| C5 `c5-sales-pipeline-dataflow` | the groups `consumers` and `pipeline` of the document's §5.2 and line 3 | EI-09 |
| C6 `c6-clinic-deployment` | app-01, app-02 and app-03: optional entities with `part_of: app`, no aliases of `app` | EI-08 |
| C7 `c7-refund-decision` | entity `request`: alias "Customer asks for a refund", soft alias "Customer" | EI-09 |
| C8 `c8-frontends-services-k33` | relations `r_adm_cat` and `r_adm_pri`: `required: false` | EI-27 |

- Each amended key keeps every other field of its registered key. Its `written` field names a1.
- `a1.json` records the reason of each entry and the date of the amendment.
- The bundle is routed by `kind`, and the prompts are hashed, so C0 keeps `kind: flowchart`.

One grader rule goes with a1: toward a group box, a stated part counts as its container. No
registered key states a part, so the rule leaves the pre-registered grading as it is. Without
the rule, the C6 parts of a1 fail Q12 on the site box of the C6 baseline runs 1 and 3.

The effect was measured on 2026-10-03 on a copy of the corpus, in memory, with render checks not
run. Under a1, 25 headline checks change from fail to pass. No check changes from pass to fail.

- `with_skill`: C0 Q08 and Q15 in runs 2 and 3; C0 Q09, Q10 and Q12 in run 1.
- `with_skill`: C7 Q09 and Q12 in runs 1 to 3; C8 Q10 in run 1.
- `without_skill`: C5 Q12 in runs 1 and 3; C7 Q09 and Q12 in runs 1 to 3; C8 Q10 in runs 1 to 3.

## Deviations from the registered README

`README.md` is registered: `PROVENANCE.txt` lists its sha256, and its text stays as written.
Review rounds 1 and 2 changed the instrument after the registration. Each entry below names the
date, the finding, the README text and the rule the instrument applies instead. Each entry also
states the effect on grading.

The effects were measured on 2026-10-03 on a copy of the corpus of campaign
`2026-10-opus55-xhigh-r1`, in memory, with render checks not run. An effect named "none" means
that no verdict of the 66 answers changes.

### V2 covers the geometry and form types (EI-11)

- Date: 2026-10-03.
- README, "Definitions fixed with the rule": "V2. Measured on the calibration set of the next
  section."
- Instrument: V2 is measured on the random sample of the calibration set, per defect type of
  `grade_figures.DEFECT_TYPES`:
  - `crossings_over_allowance`, `edge_through_node`, `title_crossing`;
  - `label_overlap_or_clip`, `illegible_at_column`, `dark_contrast`, `form_unfit`.
- κ is the agreement between the labels and the detector's verdicts, per defect type.
- The report marks V2 `corroborated` and states its scope: these geometry and form types only.
- The fidelity, caption, legend, concern, budget, ASCII and colour checks are not calibrated by V2.
- The labeller may also label `invented_element`, `missing_required_relation`, `wrong_direction`
  and `untrue_caption`. The report scores them for agreement. They never enter V2.
- Effect on grading: none. V2 has no labels yet.

### Calibration steps 2 to 5 (EI-22, EI-11, SEC-15)

- Date: 2026-10-03.
- README, "Calibration (TASK D16)": steps 2 to 5 as registered.
- Instrument, step 2: a seeded sample of at least 30 outputs is drawn over all outputs,
  stratified by case and arm. It is drawn before any grading is read. Its seed is recorded with
  the labels.
- `grade_figures.py --calibration-sample 30 --seed S` writes `worksheet.json`, what the labeller
  reads, and `evidence.json`, what the detector reads.
- The worksheet holds opaque ids, the PNG paths, the answer text and empty label slots. It holds
  no verdict, no source, no arm and no top-up mark.
- Step 3: the orchestrating model labels each item per defect type from its PNGs and its text.
- The item text is untrusted model output. It is read as data, and no instruction in it is
  followed.
- The labeller works in a session or subagent without tools. It does not see the detector's
  verdicts: `evidence.json` stays closed until every item is labelled.
- The labels go to `calibration/labels.json`, and `evidence.json` is committed beside them.
- Step 4: each defect type is topped up with up to 3 items that carry it by construction. Such an
  item is a `fail.md` fixture whose `fail_expect_failed` declares a check of that type alone
  (Q03, Q04 or Q15). It may also be a negative paired example whose `%% negative:` line names
  the render check.
- An item is used only when its evidence lets the detector judge the type. The detector's verdict
  never chooses it.
- `--fixture-corpus D` lays the `fail.md` fixtures out as a campaign in `D`;
  `render_corpus.py D` renders it; `--seed-corpus D` adds its items.
- Step 5: `grade_figures.py` grades the corpus and computes V2 from the labels of the random
  sample, per defect type.
- The top-up items are reported apart: per type, how many the detector flags and how many the
  labeller marks.
- A type with no positive in the random sample has no precision, so V2 is not met while one
  remains.
- Effect on grading: none on the checks. V2 can stay unmet: no item carries `dark_contrast` by
  construction.

### Provenance at grading time (EI-13)

- Date: 2026-10-03.
- README, "Provenance (TASK R11.10)": the paragraph that ends "A campaign directory started under
  other hashes refuses further runs."
- Instrument: `grade_figures.py` grades a campaign only under the hashes its `campaign.json`
  records for `evals.json` and every key. A graded file with another sha256 exits 2.
- The one sanctioned departure is `--amendment FILE`, a file under `evals/amendments/` that this
  file describes.
- A report graded under an amendment carries `post_hoc: true`. Its statement and `benchmark.md`
  start with POST-HOC SENSITIVITY.
- Every grading and report records the sha256 of the matcher's normalisation rule beside the key
  hashes (TASK R11.2).
- Every report states whether the campaign registered the normalisation rule and the grader
  before its runs. Campaign `2026-10-opus55-xhigh-r1` did not. For it, R11.2 holds as a
  recorded hash, not as a registered one.
- Effect on grading: none on the checks. The report gains `provenance.instrument`.

### Repetitions of a case (EI-18)

- Date: 2026-10-03.
- README, "Scores": no rule names a case and arm with fewer graded runs than the repetitions.
- Instrument: a case and arm with fewer graded runs than the campaign's repetitions is missing.
- A criterion that needs it is not evaluated: for the budget when the budget stopped that arm,
  else for the missing arm.
- Effect on grading: none while every run of the campaign grades. All 66 runs exist. A run that a
  missing render excludes makes its case and arm missing.

### ASCII outside a fence (EI-01, R4)

- Date: 2026-10-03.
- README, "Cases": "An answer may hold Mermaid fences, Markdown tables, lists and `text`
  fences."
- Instrument: an ASCII figure outside a fence is graded as a `text` fence.
- In any medium, an indented code block that draws is such a figure. It draws when one of its
  lines draws links only or starts with an arrow and a second line draws or carries an arrow.
  One line that chains three names draws as well.
- In a terminal reply, an indented block with two lines that draw or carry an arrow counts too.
  So does a run of lines of which two draw links only or start with an arrow.
- An arrow glued to words on both sides is code, such as `$client->call`, not a link.
- Next to an ASCII figure, a list explains it and is no figure.
- Residual: in a document, an indented legend whose lines start with an arrow sample, such as
  `--> synchronous call`, draws by this rule. It counts as a figure, and next to C1 `pass.md` it
  fails Q08 and Q15. No live answer holds one.
- Effect on grading: the three F1 baseline answers hold one ASCII figure each and match the
  key. The R4 rule changes no verdict.

### Caption truth, Q13 (EI-06, R1)

- Date: 2026-10-03.
- README, "Checks": no rule names which sentences of a caption claim.
- Instrument: a caption claims its title and its claim sentence, above or below the fence. The
  skill's form is a label, a title, then one sentence.
- After a label of that form, a first sentence with no comma, semicolon, colon or spaced dash is
  the title. The next sentence is then the claim.
- Otherwise the first sentence holds the claim: a title and its claim joined by a dash or a
  colon, or a paragraph without a label.
- A bold label may hold the title after its number: `**Figure 3. Containers.**`.
- Later sentences claim nothing, such as what the figure leaves out.
- The rule was chosen by measurement on the 66 live captions, labelled sentence by sentence.
  "Missed" counts title and claim sentences not read; "omissions read" counts omission
  sentences read.

| Rule | `without_skill` | `with_skill` |
| :--- | :--- | :--- |
| whole paragraph, registered grader | 0 missed, 8 omissions read | 1 missed, 0 omissions read |
| first sentence, fix wave 1 | 36 missed, 0 omissions read | 8 missed, 0 omissions read |
| title and claim sentence, this rule | 30 missed, 0 omissions read | 4 missed, 0 omissions read |

- Reading two sentences of every caption reads one omission, in C8 baseline run 3.
- Reading a second sentence after any first sentence without a clause break reads no live
  omission and misses 20 claim sentences. It reads an omission in an unlabelled synthetic
  caption, so it was not taken.
- A caption decoy of type `caption_overclaim` matches a bare claim only: one of its aliases ends
  a sentence of the title and the claim sentence. A sentence that goes on after the alias
  qualifies the claim, and the decoy does not match it.
- A reference in brackets after the alias, such as `(§2.3.1)`, does not qualify the claim. Such a
  reference holds a digit. A bracketed group without a digit qualifies the claim.
- The other caption decoys of a key, `caption_claim_decoys` and `caption_claim_traps`, match
  anywhere in that text. No registered key lists one.
- The skill's own captions read the same way under the t6 aliases of the registered C3 key. The
  positive caption P13 qualifies the alias and does not match. The negative caption N13 ends
  with an alias and matches (`references/paired-examples.md`).
- Effect on grading: C3 `with_skill` run 1 fails Q13. Its claim sentence ends with an alias of
  the caption decoy t6, and its qualification follows as a sentence of its own.
- C3 `with_skill` runs 2 and 3 pass Q13. They qualify the claim in the same sentence.
- C8 baseline runs 1 to 3 pass Q13: their omission sentence is not read.
- Against fix wave 1b, the bare-claim rule changes 2 verdicts of the 66 answers: Q13 of C3
  `with_skill` runs 2 and 3, from fail to pass. No other check changes.

#### Residual ambiguity of the title rule

- After a label, a claim sentence with no clause break reads as the title. The sentence after it
  then reads as the claim, also when it states an omission.
- Example: `**Figure 2.4.** Each front-end calls each domain service. Calls from the Admin
  console are not shown.` fails Q13 over a figure without the Admin console.
- Punctuation does not tell such a claim from a title. A clause break in the claim sentence, such
  as a comma, keeps the omission unread.
- The shape is a label, a first sentence without a clause break, then a second sentence.
- Measured on the live corpus: 10 of the 66 captions that Q13 reads have this shape. Of the 10,
  `without_skill` holds 6 and `with_skill` holds 4.
- In each of the 10, the first sentence is a title and the second a claim. No live caption is a
  claim followed by an omission in this shape: 0 of 66.
- C8 baseline run 3 is one rewritten clause away from it. With `and` in place of its comma
  clause, its omission sentence reads as the claim, and Q13 fails.
- The selftest pins this behaviour in a TC-ME-18 row.

### Numbers a figure draws, Q13 (EI-07, R2)

- Date: 2026-10-03.
- README, "Checks": no rule names numbers that a figure draws without writing them.
- Instrument: a date or a step number a figure draws without writing it counts as shown. It comes
  from `after` and durations, or from `autonumber` and `1.` markers.
- Such a number, and each part of a date, backs only a caption number written without a unit.
  Steps 1 to 11 match it; 7 min does not.
- Effect on grading: C4 baseline runs 2 and 3 pass Q13 on 23 November. The unit rule changes no
  verdict.

### Legend, Q14 (EI-29)

- Date: 2026-10-03.
- README, "Checks": no rule names the encodings of a sequence diagram.
- Instrument: Q14 counts the encodings of the lint's legend rule, MA-DOC-02
  (`lint_mermaid._legend_encodings`).
- In a sequence diagram each arrow kind is an encoding: `->>` a call, `-->>` a reply. Each fill of
  a `rect` or `box` block is an encoding too.
- In a flowchart each `linkStyle` stroke is an edge style.
- Effect on grading: the C2 baselines draw three arrow kinds and no legend, so they fail Q14. The
  C2 `with_skill` legends name both arrow kinds and pass.

### ASCII lint, Q16 (lint split of MA-ASCII-05)

- Date: 2026-10-03.
- README, "Checks": "ascii (Q16)", and `evals.json` Q16: "Every text-fence figure passes the
  ASCII lint".
- Instrument: Q16 leaves out the two element budgets, MA-ASCII-05 (soft) and MA-ASCII-06 (hard).
  Q07 and K09 hold the budget, and H-core leaves budget checks out.
- The registered grader left out one rule, which then held both budgets.
- Effect on grading: none.

### Budget measure (EI-17)

- Date: 2026-10-03.
- README, "Budget and the revision round": "The sum covers every such file under `corpus*/`, so
  both arms and the revision round share it."
- Instrument: the sum covers every such file under `corpus*/` and under `--budget-root`, wherever
  the out-root lies.
- Each admission reads the ledgers again under one lock that the executors of a checkout share.
  The lock file lives in `evals/corpus/` while it is held, and git ignores `*.lock`.
- SEC2-07, 2026-10-03: the lock file lived in the system temporary directory before. There a
  second local user could create it first and stop or hang a campaign. The executor now opens it
  without following a symlink, refuses a file of another owner, and stops with exit 2 when
  another process holds it for 60 s. A paid attempt is written to its ledger even when the lock
  fails.
- Effect on grading: none. The campaign has run.

### Bound settings of a campaign (EI-19)

- Date: 2026-10-03.
- README, "Running": "One campaign directory holds one model, one effort, one set of provenance
  hashes and one prompt per case and arm. A changed prompt needs a new `--campaign-id`."
- Instrument: one campaign directory also holds one run cap, timeout, retry count, repetition
  count and CLI version.
- `campaign.json` records them, and an invocation that differs exits 2. A changed prompt or
  setting needs a new `--campaign-id`.
- Effect on grading: none. The report flags run records whose settings differ.

### One browser for every render (EI-26)

- Date: 2026-10-03.
- README, "Corpus layout": "An edit to the render instrument renders the corpus again on the next
  invocation, so both arms share one instrument."
- Instrument: another browser executable renders the corpus again as well.
- The grader refuses a corpus whose headline renders name more than one browser.
- Effect on grading: the stored renders of the baseline runs lack the browser path, so the next
  `render_corpus.py` invocation renders them again.

### Calibration top-up without a PNG (R2-03)

- Date: 2026-10-03. Finding: R2-03 of review round 2.
- README, "Calibration (TASK D16)", step 4: "The top-up comes from the `fail.md` fixtures and the
  negative paired examples that carry the type."
- Registered grader: a negative paired example entered the top-up without a PNG. No paired
  example is rendered under the render root. Both labellers left such an item without a label,
  and V2 dropped it without a count.
- Instrument: a top-up candidate is refused for a render type when the labeller has no PNG of a
  render the type is judged in. `evidence.json` lists each refusal under `refused`. The sampler
  prints each type topped up with fewer than 3 items.
- V2 reports each item without a label by count and id, under `unlabelled`. A top-up item among
  them also counts under its type, in `top_up.<type>.unlabelled`.
- No label is changed.
- Effect on grading: none on the checks. V2 stays not met.
- The V2 block of the campaign names 5 items without a label. All 5 are top-up items from the
  paired examples: item-19, item-21, item-22, item-25 and item-35.
- So the top-up of `title_crossing` (3 items), `illegible_at_column` (2 items) and
  `label_overlap_or_clip` (1 item) was never labelled. The calibration holds 34 labelled items,
  not 39.
- A draw in memory with the same seed 108, corpus and fixture corpus keeps the same 30 sampled
  outputs. It refuses the 5 paired examples and tops up 4 items instead of 9.
- `title_crossing`, `illegible_at_column`, `label_overlap_or_clip` and `dark_contrast` then get
  no top-up item. They get one when the paired examples have PNG paths that the grader finds.

### Three detector fixes from the calibration (D8 validity rule)

- Date: 2026-10-03. Source: the disagreements between the blind labels and the detector,
  investigated with measurements and cross-checked (`references/eval-results.md` §4).
- README, D8: a validity failure sends the campaign back to the instrument; the affected runs are
  graded again, and no revision round is spent.
- Fix 1: a label on a gantt milestone is measured in the diamond's own frame. Before, the box
  around the rotated diamond held it, and a label that ran past the diamond read 0 px clipped.
- Fix 2: an edge that runs inside another edge's label is its own gate check,
  `edges_through_labels`. Before, it counted as a label overlap. R7.6 lists both in separate
  bullets, and both still fail the figure.
- Fix 3: text whose box is the drawn outline of a note, an actor or a task may run 0.5 px past
  it. Before, every label had 2 px, set for labels in reserved space. R7.6 sets no allowance.
- **Fix 3 changes a threshold after both arms' results were read.** The README pins thresholds
  before the runs, so this is a post-result change and is disclosed as one. It was made because
  both blind raters saw the ink of a note line past its border (item-06).
- Effect on grading:
  - Fix 3 moved one verdict. A `without_skill` answer of C2 has a note line 1.8 px past its
    border; it now fails Q05, and the C2 baseline score drops from 0.923 to 0.846.
  - Δ_H rose from 0.077 [0.032, 0.124] to 0.084 [0.035, 0.129], in the skill's favour.
  - Fixes 1 and 2 move no headline verdict.
  - V2 for label overlap or clip went from precision 0.67 and recall 0.5 to 1.0 and 1.0.

### Q17 reads the legend only (R2-07)

- Date: 2026-10-03. Finding: R2-07 of review round 2.
- README, "Checks", and `evals.json` Q17: "no category differs from another by fill alone unless
  the legend names both". No rule names which paragraph is the legend, or what names a category.
- Registered grader: any paragraph next to the fence with two or more clauses counted as a
  legend, the caption included. A comma in the caption passed Q17.
- Instrument: the legend is the paragraph or list directly below the fence. Without one, it is
  the paragraph above the fence when that paragraph opens with no caption label. A caption is
  never read as a legend.
- The legend names each class of a pair that differs by colour alone. It names a class by its
  class name, or by a colour of its `classDef` that the other class does not share, as the
  figure writes it. The rule matches the figure's own tokens, never a word list (ARCHITECTURE
  L1).
- Residual: a legend that names such classes in other words, such as "light blue: holds", does
  not name them by this rule.
- Effect on grading: none. 18 of the 66 answers set a fill: 17 `with_skill`, 1
  `without_skill`, in 20 figures. No figure draws two classes that differ by colour alone, so the
  legend rule decides no verdict. Each of the 66 answers keeps its Q17 verdict.

### The sign test counts "ahead" above 0 (R2-14)

- Date: 2026-10-03. Finding: R2-14 of review round 2.
- README, "Definitions fixed with the rule": "**Ahead** means a case difference above 0." The
  README also says: "The sign test is reported as information."
- Registered grader: the sign test counted a case ahead only above a noise floor of 0.10. The
  README registers no floor. So `report.json` held two counts of cases ahead: the sign test's
  and H3's.
- Instrument: the sign test counts a case ahead above 0 and behind below 0, as the README and
  H3 define it. `sign_test.definition` states this.
- The reading with the 0.10 floor stays under `sign_test.sensitivity`, marked as not
  registered. `DECISION_RULE` no longer holds `noise_floor`. No criterion of D8 changes.
- Effect on grading: no check verdict and no criterion of D8 changes.
- `sign_test` of the campaign changes from 4 ahead, 0 behind, 6 ties (one-sided p 0.0625) to 7
  ahead, 0 behind, 3 ties (one-sided p 0.0078). The 7 cases ahead are the 7 that H3 counts. H3
  needs 8 and stays not met.

### Paths under the home directory (SEC2-05)

- Date: 2026-10-03. Finding: SEC2-05 of review round 2.
- README, "Corpus layout": `geometry.json` holds "the versions of mermaid, mermaid-cli and the
  browser". It names no local path.
- Instrument: a committed file writes a path under the home directory as `~/...`. A path field
  gets it by exact prefix: `renderer.browser_path` in `geometry.json`, the browser path in
  `grading.json` and `report.json`, and the PNG paths of the worksheet. A renderer log in
  `log_head` gets it at each path that starts with the home directory.
- `render_corpus.py` compares the browser executable in that form, so a render stored in
  either form is reused.
- The committed JSON of the campaign and of `calibration/` was rewritten once on 2026-10-03:
  521 paths in 103 files got `~` in place of the home directory, by exact prefix.
- Under the instrument of that date, before the other fixes of review round 2, `report.json` and
  every `grading.json` re-derive from the rewritten corpus: the selftest passed all 213 rows,
  TC-ME-22 and TC-ME-23 included.
- The labels map to the same 39 items. Only the home prefix of their 78 PNG paths changed.
- Effect on grading: none. The browser path enters no check.

### Drift between the arm windows (EI-24)

- Date: 2026-10-03.
- README, "What none of this shows": the list holds no entry on the order of the arms.
- Added limit: the `without_skill` runs were drawn before the `with_skill` runs, as PLAN 108
  orders.
- API conditions, failure rates and the CLI may differ between the two windows.
- No seeded subset of `without_skill` runs was drawn again in the `with_skill` window, so that
  drift is not measured.
- Effect on grading: none.

### The loading envelope of the skill block (EI-25)

- Date: 2026-10-03.
- README, top section: "The skill block holds `SKILL.md` and the reference files of one row of
  its routing table."
- Instrument: the block opens with the sentence "The skill `mermaid-authoring-guidelines` is
  loaded. Apply it to the task that follows." and the line
  `=== BEGIN SKILL mermaid-authoring-guidelines ===`.
- It closes with `=== END SKILL ===`.
- The opening sentence is part of the loading envelope that the `with_skill` arm receives. Its own
  effect is not measured.
- Effect on grading: none. The prompts of the campaign hold this envelope as registered.
