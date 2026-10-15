# TASK 121 — The render check redraws HTML labels in GitHub's font, and the settings lines keep them whole

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 121 |
| Slug | github-font-swap |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | WI-53; the operator's request of 2026-10-14, quoted below the table |
| Base revision | `eea6a96a53985b17a19cf5b8268fc35054644932` |
| Closes | WI-53 |
| Archive name | `task-121-github-font-swap.md` |
| Revision | 5 |

**Record.** [WI-53](../backlog/wi-53-mermaid-html-labels-are-cut-on-github.md)

**Request.** "реализуй доработки docs/backlog/wi-53-mermaid-html-labels-are-cut-on-github.md"

**Revision 2** applies the findings of Mode A round 1 (F1 to F6, m1 to m12) and the operator's
decision D8. **Revision 3** applies N1 to N3 of round 2. **Revision 4** applies the findings of
stage-2 round 1 (D10), and **revision 5** those of stage-2 round 2 (D11).

<!-- contract:problem -->

## 1. Problem

GitHub shows the HTML labels of a Mermaid figure cut at the right edge of their boxes. VS Code
shows the same figures whole, and `render_check.py` passes them in 11.17.2, 10.9.8 and dark.

Mechanism, from WI-53 and the measurements of this run (§8):

1. Mermaid measures each HTML label once, in its own font, and fixes the label's `foreignObject` to
   that size. A `<small>` second line is measured smaller.
2. GitHub then shows the labels in its own font, with `<small>` at full size. The text grows wider
   than its `foreignObject`, which clips it.
3. The render check draws on a clean page, where no font changes after the drawing.

The defect reaches every figure kind that draws HTML labels in 11.17.2: flowchart, state, ER,
class, requirement and mindmap. Sequence, gantt, timeline, quadrant and gitGraph figures draw SVG
text. Journey figures wrap their text. Neither loses a label.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | The settings lines keep HTML labels whole | Y | R1.1–R1.4 | A1 |
| R2 | A node's second line is plain text | Y | R2.1–R2.3 | A4 |
| R3 | The render check redraws labels in GitHub's font | Y | R3.1–R3.6 | A2, A3 |
| R4 | The lint warns before the render | Y | R4.1–R4.3 | A4, A7 |
| R5 | The skill's documents and figures follow | Y | R5.1–R5.9 | A1, A2, A6 |
| R6 | Evidence, tests and the eval instrument | Y | R6.1–R6.7 | A2, A3, A5, A8 |
| R7 | Documents and records | Y | R7.1–R7.4 | A6 |
| R8 | Staging (`framework-upgrade` §3 step 4) | Y | R8.1–R8.7 | A5, A7, A8 |

## 3. Requirements

All paths below are relative to `.agent/skills/mermaid-authoring-guidelines/`, unless they start
with `docs/`, `System/` or `tests/`.

### R1 — settings lines (`assets/notation.json`)

- **R1.1** The settings lines of `flowchart`, `state`, `er`, `class` and `requirement` end with the
  key `"themeCSS": "foreignObject { overflow: visible; }"`. The new lines:

  ```text
  flowchart:
  %%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}, "themeCSS": "foreignObject { overflow: visible; }"}}%%
  state, er, class, requirement:
  %%{init: {"layout": "dagre", "look": "classic", "themeCSS": "foreignObject { overflow: visible; }"}}%%
  ```

- **R1.2** `settings.mindmap` is a new line:
  `%%{init: {"look": "classic", "themeCSS": "foreignObject { overflow: visible; }"}}%%`.
- **R1.3** `renderers.font_swap` is a new object with two keys:
  - `tags`: `["v11"]`, the tag of the version GitHub runs; each tag is a key of
    `renderers.installs`;
  - `css`: `* { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial,
    sans-serif !important; } small { font-size: inherit !important; }`, on one line.

  The css holds only letters, digits, spaces and the characters `*{}:;,!".-`.
- **R1.4** No threshold key is added. The findings of R3.4 count against
  `thresholds.max_clipped_labels` (D4).

### R2 — second lines

- **R2.1** A node's second line is plain text after `<br/>`. Outside a negative fence, no label of a
  flowchart, state or ER figure holds `<small>` in these files and figures:
  - `SKILL.md` and `references/*.md`;
  - `evals/fixtures/*/pass.md`;
  - the figures of R5.9: `System/Docs/WORKFLOWS.md:324` and `System/Docs/PRODUCT_DEVELOPMENT.md:30`.
- **R2.2** `labels.node_second_line_chars_max` stays 40. The limit counts a line drawn at full
  size.
- **R2.3** A label line breaks at `<br/>` only, as before.

### R3 — the font-swap probe

- **R3.1** `scripts/measure_text.mjs` takes the option `--font-swap <css>`. After the clean
  measurement and the PNG, it runs four steps:
  1. it adds a `style` element whose text is `<css>` to the page's `head` element;
  2. it waits for the fonts, as it does before the clean measurement;
  3. it measures every `foreignObject` that holds text again;
  4. it reads the platform fonts of the measured labels again.

  The JSON gains the key `font_swap`: `{"labels": [...], "fonts": [...], "font_family": ...}`.
  `fonts` and `font_family` have the form of the clean measurement's keys. Each label holds:
  - `text`, `kind`, `id`, `owner` and `n`, as the clean measurement gives them;
  - `overflow`: the computed `overflow` of the `foreignObject`;
  - `clipped_px`: the largest overrun of the text's line boxes past the `foreignObject`, on any
    side, in root units;
  - `outside_px`: the largest overrun of the text past the `viewBox`;
  - `past_shape_px`: for a label inside `g.node`, how far its text runs past the shapes of that
    node, in root units. A label outside a node, and a label of a node that draws no shape,
    hold `null`. The measurement:
    1. each corner of each line box is taken 1 px inside the box vertically;
    2. the corner moves toward the line's middle in steps of 0.25 px, up to half the line's width;
    3. it stops where it lies in the fill or the stroke of a shape of the node;
    4. the value is the largest move of any corner.

  Without `--font-swap` the JSON holds no `font_swap` key. A `<css>` that holds any other
  character than those of R1.3 ends the script with exit 3, before the browser starts.
- **R3.2** `scripts/render_check.py` passes `--font-swap` with `renderers.font_swap.css` to the
  measurement of every render whose tag is in `renderers.font_swap.tags`: the light and the dark
  11.17.2 render. `render_settings()` holds `font_swap`, so evidence measured under other swap
  settings reads as stale. A measurement that exits non-zero, a refused stylesheet included, leaves
  its render `not rendered`, as today, and the run exits 2.
- **R3.3** `scripts/svg_geometry.py`: `analyze_svg` adds the metric `font_swap`:
  `{"probed": bool, "font_family": str, "hidden": [...], "past_border": [...]}`.
  - `hidden` holds `{"label", "kind", "overflow_px", "where"}` for each label whose text runs more
    than `CLIP_TOL_PX` past its `foreignObject` while its `overflow` is not `visible`, or more
    than `CLIP_TOL_PX` past the `viewBox`. `where` is `its box` or `the figure's edge`.
  - `past_border` holds `{"label", "overflow_px"}` for each node label whose `overflow` is
    `visible` and whose `past_shape_px` exceeds `CLIP_TOL_PX`.
  - A measurement without `font_swap` gives `{"probed": false, "font_family": "", "hidden": [],
    "past_border": []}`. `METRIC_KEYS` and `_empty_metrics()` hold the key.
  - `font_family` doubles each backslash, as `printable` of `security-audit` does, and writes each
    other character that `str.isprintable()` refuses as its Python escape. A font name then cannot
    drive the terminal that shows a finding or the report, nor print as an escape it does not hold
    (CWE-150, D10, D11).
  - A length that is not a JSON number, or whose float is not finite, raises `ValueError`, and so
    does `labels` that is not a list: the render is `not rendered` (D10, D11). A length of `null`
    reads as 0.
- **R3.4** `evaluate()` reports the check `font_swap`. It stands in `CHECKS` and `GATE_CHECKS`
  directly after `clipped_labels`.
  - Each `hidden` and each `past_border` entry is one finding.
  - The severity is `fail` when the number of entries exceeds `thresholds.max_clipped_labels`,
    and `warn` otherwise.
  - Metrics whose `font_swap.probed` is false or absent give no finding. A stored `font_swap`
    that is missing or `null` reads as absent; any other value that is not an object raises
    `ValueError` (D10, D11).
  - A `hidden` message names the text, the overrun, and the fix: the settings line of the kind and
    no `<small>`. A `past_border` message names the text, the overrun, and the fix: a shorter line.
- **R3.5** `scripts/mermaid_model.py`: `RENDER_CHECK_NAMES` holds `font_swap` (staged, R8).
- **R3.6** The text report of `render_check.py` names the swap font of each probed render, next to
  the font it names today.

### R4 — the lint (staged, R8)

- **R4.1** New rule `MA-LABEL-14`, severity `warn`, titled "`<small>` in a flowchart, state or ER
  label". It reports each label that holds `<small`, in any case:
  - a flowchart node label, a subgraph title or an edge label;
  - a state label or a transition label;
  - an ER entity label or a relation label.

  Hint: "Write the second line as plain text after <br/>: GitHub shows <small> at full size in a
  box that mermaid sized for small text." The rule has a probe pair, as every rule has. The
  finding quotes the label as R3.3 writes `font_family`: each backslash doubled, and each
  character that `str.isprintable()` refuses written as its Python escape (D10, D11).
- **R4.2** `MA-SET-06` checks `themeCSS` as it checks `layout` and `look`, for every kind whose
  settings line in `notation.json` holds the key: the kinds of R1.1 and R1.2, and `gantt` (D9).
  - A figure whose `themeCSS` differs from the line gets the finding
    `missing "themeCSS": "<value>"`. A value over 60 characters is named as
    `missing "themeCSS" of settings.<kind>`.
  - The title becomes "Settings line without the pinned layout, look and themeCSS".
  - `_SETTINGS_KEY` gains `mindmap`.
- **R4.3** The hints of `MA-PARSE-04`, `MA-LABEL-01` and `MA-LABEL-08`, the quiet probe of
  `MA-PARSE-04` and the second-line probe of `MA-LABEL-02` show a plain second line, not `<small>`.

### R5 — the skill's documents and figures

- **R5.1** `SKILL.md` takes version 1.2, and four edits:
  - Red Flag "It renders in my preview" names GitHub's font swap and RF-23;
  - Step 5.1 names the `themeCSS` key of the settings lines;
  - Step 5.3 states the second line as plain text after `<br/>`, never `<small>`, its 40
    characters counted at full size;
  - Step 8.3 states that the render check redraws the 11.17.2 renders in GitHub's font, and fails a
    label that the swap hides or pushes past its node's border.

  `SKILL.md` holds 2864 words at the base; TC-ME-32 caps it below 3000.
- **R5.2** Each settings line of a kind of R1.1 that `SKILL.md` and `references/*.md` quote takes
  the new line of R1.1. This covers mermaid fences, `text` listings of Mermaid source, and code
  spans in prose, such as `references/state.md:10` and the listing of
  `references/review-checklist.md`. These fences keep their line:
  - a fence whose defect is its settings line, such as the font and theme examples of
    `renderer-facts.md`;
  - the negative fence of RF-23 (R5.5).
- **R5.3** `<small>` leaves every label of the fences of R5.2 (R2.1). N6 of `paired-examples.md`,
  "P1 drawn left to right", takes the labels of the reworked P1 (R5.7).
- **R5.4** Negative fences and `font_swap`:
  - a negative fence that keeps its line or has none names `font_swap` in its marker when the
    check fails on it in a required render;
  - §8 measured six such fences, all in `renderer-facts.md`: RF-01, RF-02, RF-03, RF-04, RF-07
    and RF-08;
  - every negative fence fails only the render checks its marker names (A2).
- **R5.5** `references/renderer-facts.md` gains RF-23, "GitHub draws HTML labels in its own font
  after mermaid sized them". It holds:
  - a negative fence of the old form, the settings line without `themeCSS` and a `<small>` second
    line, marked `%% negative: font_swap, MA-SET-06, MA-SET-07, MA-LABEL-14`;
  - the same figure in the form of R1.1 and R2.1, positive;
  - the variants WI-53 measured, and the numbers of this run;
  - the viewers: GitHub swaps the font; VS Code showed the figures whole; JetBrains was not
    observed.

  The sentence that names Figures 1 and 2 (RF-12) as the file's only fences that follow every rule
  names the positive fence of RF-23 too. The list of safe label markup
  (`renderer-facts.md:712@eea6a96`) points to RF-23 for `<small>`.
- **R5.6** The prose follows the figures:
  - `flowchart.md` §3 gains a `themeCSS` row;
  - `flowchart.md` §5.1 and §6 state the second line as plain text after `<br/>`, its 40
    characters counted at full size;
  - `other-kinds.md` §1 states the settings lines of ER, class, requirement and mindmap, and its
    mindmap figure carries its line;
  - `layout-and-planarity.md` §6 drops the 13.3 px `<small>` size and measures the second line at
    full size.
- **R5.7** P1 of `paired-examples.md` passes every render check, `font_swap` included. A Rework
  note states what failed, what changed, and the numbers before and after per version. Every
  element of P1 keeps a supporting source line.
- **R5.8** The prose numbers of a fence whose geometry changes are measured again and dated. This
  covers the template table of `flowchart.md` §5, P1, N6, the figure and the listing of
  `review-checklist.md` with its widths and its claim that the lint reports nothing, and RF-09.
  `themeCSS` changes no layout (§8), so a fence that only takes the new line keeps its numbers.
- **R5.9** The two figures outside the skill that carry the old flowchart line take the new line of
  R1.1: the fences that open at `System/Docs/WORKFLOWS.md:324` and
  `System/Docs/PRODUCT_DEVELOPMENT.md:30`.

### R6 — evidence, tests and the eval instrument

- **R6.1** `render_check.py --fixture` writes `scripts/tests/fixtures/references-geometry.json` and
  `scripts/tests/fixtures/paired-examples-geometry.json` anew, from every file they cover.
- **R6.2** `scripts/tests/test_svg_geometry.py` covers R3.3 and R3.4 with synthetic measurements:
  - a hidden label and a visible one;
  - a label past the `viewBox`;
  - a label past its node's border;
  - a measurement without `font_swap`;
  - the `fail` and `warn` threshold;
  - a label that runs past the `viewBox` and past its node's border is one `hidden` entry, and a
    clipping box gives no `past_border` entry (D10);
  - a malformed length, `labels` or stored metric raises `ValueError`, and a control character
    of the font name is escaped (D10);
  - a numeric string, an integer too large for a float, and each falsy stored metric that is not
    an object raise `ValueError`, and a backslash of the font name is doubled (D11).
- **R6.3** `scripts/tests/test_render_check.py` covers R3.1, R3.2 and R3.6:
  - the measurement command of a `v11` render carries `--font-swap`; a `v10` render's does not;
  - `render_settings()` holds `font_swap`;
  - the text report names the swap font;
  - `measure_text.mjs` exits 3 on a css with a refused character. The test skips without `node`;
  - a stand-in measurement that exits 3 leaves the render `not rendered`, as in
    `TestRenderWithStandIns`;
  - with the installed renderers, the old form fails `font_swap` in 11.17.2 and the form of R1.1
    and R2.1 passes. The test skips without the installs, as its class does;
  - with the installed renderers, a `<small>` second line under the line of R1.1 runs past its
    node's border in 11.17.2: one `past_border` entry, and `font_swap` fails (D10).
- **R6.4** `scripts/tests/test_lint_mermaid.py` covers R4.1 and R4.2: `MA-LABEL-14` on each label
  kind of R4.1, and its silence on a plain second line; `MA-SET-06` on a settings line without
  `themeCSS`. `TestWritesNoFile` gains the module attribute `GUARD_PRELUDE`, empty by default,
  which the driver of R8.3 sets. Per D10: a `themeCSS` of 60 characters is quoted and one of 61 is
  named; `MA-LABEL-14` escapes a control character of the label it quotes. Per D11: it doubles a
  backslash, and the two copies of the escape give the same output.
- **R6.5** `scripts/tests/test_notation_consistency.py`: `SETTINGS_KEY` gains `mindmap`. A test
  checks R1.3: the tags are installs, and the css holds only the characters of R1.3.
- **R6.6** The committed campaign `evals/corpus/2026-10-opus55-xhigh-r1/` gains `notation.json`, a
  byte copy of `assets/notation.json` at the base: the notation its gradings derive under.
  `t_committed` of `evals/selftest_figure_evals.py` grades a campaign under the `notation.json`
  its directory holds, and under the live notation when it holds none (D8). The selftest's
  docstring states this rule and the residual of D8.
- **R6.7** `evals/fixtures/{c0,c1,c3,c5,c6,c7,c8}/pass.md` take the new lines of R1.1, and their
  labels lose `<small>` (TC-ME-17b). `grade_figures.py`, `evals/README.md` and every file that
  `evals/PROVENANCE.txt` pins stay unchanged.

### R7 — documents and records

- **R7.1** `docs/ARCHITECTURE.md`:
  - §10.1 and §10.2 step 4 name the font-swap probe;
  - §10.4 states that the selftest grades a committed campaign under the `notation.json` it holds,
    and the residual of D8;
  - §10.7 states that `measure_text.mjs` takes a swap stylesheet of the characters of R1.3 only,
    and inserts it as the text of a `style` element.
- **R7.2** `CHANGELOG.md` and `CHANGELOG.ru.md` get v3.42.0, titled "the render check redraws
  HTML labels in GitHub's font, and the settings lines keep them whole (TASK 121)".
- **R7.3** WI-53 gets `status: done`, `resolved_at`, `resolved_by: 'TASK 121'` and a resolution
  blockquote; its index line moves under `## Closed`.
- **R7.4** The `mermaid-authoring-guidelines` row of `System/Docs/SKILLS.md` changes only where it
  states a fact this task changes.

### R8 — staging

- **R8.1** Stage 1 writes the new text of these files under staged names:

  | Final path | Staged name |
  | :--- | :--- |
  | `scripts/lint_mermaid.py` | `scripts/lint_mermaid_next.py` |
  | `scripts/mermaid_model.py` | `scripts/mermaid_model_next.py` |

  The basis:
  - a committed allow rule names `lint_mermaid.py`; another names `plan_gantt.py --check`. Both
    import `mermaid_model.py`;
  - `planarity.py` and `plan_gantt.py` are not edited;
  - `notation.json` is data that the lint, `plan_gantt.py --check` and the curated
    `tests/test_mermaid_wiring.py` read. Its new keys hold no new numeric tree, and the base
    `MA-SET-06` reads only `layout` and `look`. It is edited in place;
  - no allow rule, hook or listed script imports `svg_geometry.py`, `render_check.py` or the eval
    scripts. `measure_text.mjs` runs only under `render_check.py`, which asks for approval;
  - the hook's `validate_skill.py` runs no skill code;
  - no registration exists, so stage 3 adds no settings test.

  No allow rule, hook or listed script names or imports a staged name. pytest's default patterns
  match no staged name.
- **R8.2** The text under a staged name is the final text. Stage 3 renames it over its final path
  unchanged. The audit record holds the SHA-256 of each staged file and of its final file after
  stage 3; the two are equal.
- **R8.3** A driver in the session's scratchpad runs the instruments against the staged files. The
  command asks for approval. Its modes:
  - `next` registers the staged files under the names `mermaid_model` and `lint_mermaid` before a
    test module imports them, and sets `GUARD_PRELUDE` of R6.4, so that the subprocess of
    `TestWritesNoFile` registers them too. It runs the skill's test modules;
  - `next-selftest` registers them the same way and runs `evals/selftest_figure_evals.py`;
  - `next-lint` registers them and runs the staged lint;
  - `base` runs the tests against the base files.

  The `next` modes assert that each registered module's `__file__` is its staged file.
- **R8.4** Stub first. Each new test is written, and run red against its base code, before that code
  is edited:
  - the lint tests of R6.4 fail in mode `base`;
  - the tests of R6.2, R6.3 and R6.5 fail against the base text of the file they test.

  The audit record holds each red run, or names why a test passes on the base.
- **R8.5** Stage 3, after §4.5, is one edit: the two renames of R8.1. Every other edit lands
  before stage 3. The gates run again after it:
  - `python3 tests/run_tests.py`;
  - the pytest list of CI and the skill's unit tests;
  - `lint_mermaid.py --probe` and the lint of `references/*.md`;
  - `evals/selftest_figure_evals.py`;
  - the skill validators;
  - `check_positional_refs.py --all docs/*.md docs/issues docs/backlog`.
- **R8.6** Stage 2 is one code review and one security audit at one fingerprint. They review the
  staged code, `measure_text.mjs`, `render_check.py`, `svg_geometry.py`, `notation.json`, the eval
  changes of R6.6 and R6.7, the tests and this TASK. The bound is 3 rounds
  (`stage2-review-retry`), and the boundary of §3 step 4 applies. Stage 4 is a code review and a
  security audit of the stage-3 diff on the new fingerprint.
- **R8.7** The Failure rule of §3 step 4 applies as written. If stage 3 is restored, or the run
  stops before it, the audit record lists under `Pending after restore` each edit that landed
  before stage 3. The operator decides on each.

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — An agent draws a new flowchart

**Actors:** an agent, `lint_mermaid.py`, `render_check.py`.

**Preconditions:** the renderers of `setup_renderers.sh` are installed.

**Main scenario:**

1. The agent copies `settings.flowchart` and writes each second line after `<br/>`.
2. The lint reports neither `MA-LABEL-14` nor `MA-SET-06`.
3. The render check redraws the 11.17.2 renders in GitHub's font. No label is hidden and none
   crosses its node's border.
4. The hand-off line states the pass.

**Alternatives:**

- A. The renderers are absent: the render check reports `not rendered: <reason>` and exits 2. The
  hand-off line says `not rendered`.
- B. `renderers.font_swap.css` holds a refused character: `measure_text.mjs` exits 3, and the render
  check reports the render as not rendered, exit 2.
- C. The swap stylesheet resolves to another font on another platform. The overruns differ from §8;
  the evidence names the swap font of each render.

**Postconditions:** GitHub shows every label whole.

### UC-2 — An agent checks a figure of the old form

**Actors:** an agent, `lint_mermaid.py`, `render_check.py`.

**Preconditions:** the figure carries the old settings line and `<small>` second lines.

**Main scenario:**

1. The lint warns `MA-SET-06` (`missing "themeCSS"`) and `MA-LABEL-14`.
2. The render check fails the figure on `font_swap` in the light and dark 11.17.2 renders. Each
   finding names a hidden label and its overrun.
3. The agent copies the new line and writes plain second lines.
4. The lint reports neither rule, and the render check passes.

**Postconditions:** the figure has the form of UC-1.

### UC-3 — The swap pushes a label past its node's border

**Actors:** an agent, `render_check.py`.

**Preconditions:** the figure has the new form; one line fills its node.

**Main scenario:**

1. The render check reports `font_swap`: the text runs past its node's border by the overrun.
2. The agent shortens the line, or moves words between the two lines, and renders again.
3. The render check passes.

**Postconditions:** no label crosses its node's border in GitHub's font.

<!-- contract:acceptance -->

## 5. Acceptance criteria

- **A1** — `notation.json` holds the lines of R1.1 and R1.2 and the object of R1.3.
  `test_notation_consistency.py` passes: every quoted settings line equals its line.
- **A2** — `test_paired_examples.py` passes on the fixtures of R6.1:
  - the negative fence of RF-23 fails `font_swap` in the light and the dark 11.17.2 render;
  - every negative fence fails only the render checks its marker names;
  - every positive fence of `references/*.md` passes every render check in every required render.

  In the `render_check.py --json` report of each file of R5.9, the figure of R5.9 has the status
  `pass`.
- **A3** — the tests of R6.2 and R6.3 pass. The installed-renderer test of R6.3 ran, rather than
  skipped, in the run that wrote the fixtures.
- **A4** — after stage 3:
  - `lint_mermaid.py --probe` exits 0, and the lint of `references/*.md` exits 0;
  - the lint reports no `MA-LABEL-14` and no `MA-SET-06` in the files and figures of R2.1, outside
    a negative fence;
  - the tests of R6.4 pass.
- **A5** — after stage 3, every gate of R8.5 passes.
- **A6** — the documents and records of R5, R7.1 to R7.4 hold the stated content.
  `scan_register.py` reports no `WARN` on an added line of `docs/TASK.md` or the CHANGELOG entries.
  `SKILL.md` holds fewer than 3000 words, and each routed bundle fewer than 16000.
- **A7** — before stage 3, each red run of R8.4 is recorded, and each new test passes in mode
  `next` or against its edited code.
- **A8** — before stage 3, `evals/selftest_figure_evals.py` passes in mode `next-selftest`, and
  TC-ME-17b, TC-ME-22 and TC-ME-23 pass in it. The audit record holds its summary line.

<!-- contract:open-questions -->

## 6. Open questions

None. The scope questions were answered (D1, D2, D8).

## 7. Decisions

- **D1**, 2026-10-14, operator: the fix and the probe cover every kind that draws HTML labels in
  11.17.2: flowchart, state, ER, class, requirement and mindmap. Answer "Все виды с
  HTML-подписями". Rejected: flowchart and state only, as WI-53 states. The probe would then pass
  hidden labels of the other four kinds.
- **D2**, 2026-10-14, operator: `MA-SET-06` checks `themeCSS` as it checks `layout` and `look`.
  Answer "Да, MA-SET-06 проверяет themeCSS". Rejected: the `<small>` warning alone. A missing key
  would then show only in a render.
- **D3**, 2026-10-14, orchestrator: the probe runs in the renders of the version GitHub runs,
  11.17.2, light and dark. Rejected: every render. 10.9.8 stands for JetBrains IDEs, where no font
  swap was observed.
- **D4**, 2026-10-14, orchestrator: `font_swap` counts against `thresholds.max_clipped_labels`.
  Rejected: a new threshold key. Its name needs a unit word in `tests/test_mermaid_wiring.py`, a
  module that a listed script runs, and it would limit the same quantity: text a reader cannot see
  whole.
- **D5**, 2026-10-14, orchestrator: the swap stylesheet is the one WI-53 measured, which reproduced
  the operator's screenshot. Rejected: a guessed copy of GitHub's current font stack.
- **D6**, 2026-10-14, orchestrator: both probe tests use `CLIP_TOL_PX` (2.0 px).
  - Measured: `past_shape_px` 0.00 in every clean render of 102 SVGs.
  - Measured: 3.75 px and 2.50 px on two stadium labels whose swapped PNGs show the text touching
    the border.
  - Rejected: points at a quarter of the line's height. They gave 1.25 px and 0.25 px on the same
    two labels, under the tolerance.
- **D7**, 2026-10-14, orchestrator: a negative fence that quotes a settings line takes the new line
  and loses `<small>`, as a positive one does. Rule 3 of `paired-examples.md` says a negative
  carries the settings line of its kind. Rejected: keeping the old line in the negatives. They
  would then fail `font_swap`, a check they do not show.
- **D8**, 2026-10-14, operator: the committed campaign is graded under the notation its gradings
  derive under (R6.6), and the `pass.md` fixtures take the new lines (R6.7). Answer "Снимок
  нотации кампании". Rejected: re-deriving the campaign's gradings under the new notation. K01
  would then record a failure for 17 `with_skill` answers that copied the line their skill gave
  them, and the A/B result would change after the fact. This decision replaces revision 1's D8,
  whose premise round 1 disproved: the eval selftest reads the live settings lines.
  - Residual: the grader's CLI, `grade_figures.py --corpus`, keeps the live notation. Run on the
    committed campaign, it records those K01 failures. R6.6 and R7.1 state this residual.
- **D9**, 2026-10-14, orchestrator: `MA-SET-06` checks the `themeCSS` of `settings.gantt` as well.
  The gantt line pins it for its bar labels, and `plan_gantt.py` writes the whole line. Rejected:
  excluding gantt, which would make the rule check one key in five kinds and skip it in a sixth.
- **D10**, 2026-10-14, orchestrator: stage-2 round 1 passed with one MEDIUM and six LOW findings of
  the code review and one LOW of the security audit, all in the touched lines. Fix round 1 applies
  them, as TASK 120 D3 did. The MEDIUM one leaves the border search, the half of the probe that
  UC-3 needs, guarded by synthetic data only. Rejected: shipping on round 1.
  - The escape covers the two routes this task adds: the swap font name and the label that
    `MA-LABEL-14` quotes. The base routes of the same class stay as they are, before the task.
- **D11**, 2026-10-15, orchestrator: in stage-2 round 2 the security audit passed, and the code
  review failed on N1, a LOW finding that breaks R3.4. It found four more LOW items, N2 to N5. Fix
  round 2 applies all five, and round 3 is the last of the bound. Stage 2's rule for LOW routes of
  a fixed class does not apply, since N4 and N5 are new items. Rejected: residuals for N1 to N3,
  which would leave R3.4 unmet.
  - The escape stays in two copies, `svg_geometry.py` and the lint. A shared module would be a new
    module that the staged lint imports, so stage 3 would have to stage it too. Meanwhile the live
    `svg_geometry.py` imports only the live files. A test pins the two copies to one output.
  - The escape keeps the set that `str.isprintable()` refuses. It is wider than the categories of
    `printable` (Cc, Cf, Zl, Zp): it also escapes a lone surrogate, which a UTF-8 terminal cannot
    print.
- **D12**, 2026-10-15, operator: stage 3 was restored under the Failure rule, after the stage-4 code
  review rejected the orchestrator's decision to keep it past a failed gate run (S4-1). The same
  patch is applied again; the gates and stage 4 then run on the new fingerprint. A gate that fails
  again restores stage 3 and returns the decision to the operator. Answer "Применить заново".
  Rejected: one re-run of a timing failure outside the change, and stopping with stage 3 restored.

## 8. Measurements of this run

Taken in the session's scratchpad on 2026-10-14, with the pinned renderers and chrome-headless-shell
150.0.7871.24. The swap stylesheet of R1.3 resolved to `.SF NS` on macOS.

- Old form, Figure 1 of `flowchart.md`: 12 of 17 labels hidden after the swap. Second lines
  overran by 22 to 42 px.
- Forms of R1.1 and R2.1 on the 13 positive flowchart and state figures of `references/` that
  carry the settings line: 0 hidden labels in 11.17.2, its dark render and 10.9.8. One label
  crossed its node's border: the stadium of P1, by 3.75 px.
- `themeCSS` changes no layout: every figure without `<small>` kept its `viewBox` width, to 0.05 px.
- The same forms make P1 1493 px wide in 11.17.2, an effective font of 9.6 px, below the 10 px
  floor. It was 1372 px and 10.5 px. A rework that passes was measured:
  - one invisible link marked `%% layout only` gives 1255 px and 11.5 px in 11.17.2, and 1181 px
    and 12.2 px in 10.9.8;
  - the stadium label "Client apps · CRM · MMA" over "dashboard · MacWhisper" gives
    `past_shape_px` 0.00 in both versions.
- Negatives of `references/` in 11.17.2, with a 2 px tolerance:
  - the eight that take the new line under D7: 0 hidden, 0 past their border. N6, with the labels
    of the measured P1 rework, still fails `legibility` and `title_crossings`: 2348 px and 6.1 px
    in 11.17.2, 2240 px and 6.4 px in 10.9.8;
  - those that keep their line or have none: RF-01 3 hidden, RF-02 3, RF-03 6, RF-04 3, RF-07 2,
    RF-08 4; RF-05 and RF-09 0. The sequence negatives draw no HTML label.
- ER, class, requirement and mindmap in 11.17.2: 5 to 10 labels hidden per figure, by 1.2 to 9 px.
  With `themeCSS`: 0 hidden, 0 past their border. In 10.9.8 only the class figure draws HTML
  labels.
- `System/Docs/WORKFLOWS.md` and `PRODUCT_DEVELOPMENT.md` hold one flowchart each with the old
  line. `WORKFLOWS.md` also holds a `graph TD` figure with no settings line (§9).
- At the base, `SKILL.md` holds 2864 words; the routed bundles hold 5173 to 15408 words.

## 9. Out of scope

- Figures that do not carry a settings line of the skill, such as the figure of `README.md` and
  the `graph TD` figure at `System/Docs/WORKFLOWS.md:298`.
- Labels that the swap widens over an edge or over each other; ER attribute columns.
- A subgraph title that the swap pushes past its cluster's border.
- The views of VS Code and JetBrains IDEs.
- The forward render of 12.1.0.
- `htmlLabels: false`: WI-53 records its overlaps and its contrast in dark.
- The grader `grade_figures.py`, its CLI, and the files `evals/PROVENANCE.txt` pins (D8 and its
  residual).

**Migration.** A consumer project's figures of the old form get `MA-SET-06` and `MA-LABEL-14`
warnings, and fail `font_swap` in the render check. The fix is the new settings line and plain
second lines; one consumer project applied it to 15 figures before this task (WI-53).
