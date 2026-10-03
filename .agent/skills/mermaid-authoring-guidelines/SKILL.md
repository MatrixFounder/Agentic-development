---
name: mermaid-authoring-guidelines
description: >-
  Use when a document needs a diagram: «нарисуй схему», «добавь диаграмму»,
  "draw a diagram", "mermaid", architecture, sequence, state or plan (gantt)
  figures, or fixing a figure that is a mess of boxes and arrows. Chooses
  list, table, ASCII or Mermaid first; checks layout, legend and fidelity.
tier: 2
version: 1.0
---

# Mermaid authoring guidelines

**Purpose.** A figure in a Markdown artifact restates facts of the text in a form a reader traces at
a glance, in every viewer that shows the document. This skill decides whether a figure is needed and
in which form. When the form is Mermaid, it fixes how the figure is drawn: one concern, a size
budget, no avoidable crossings, and nothing the text does not state. A render check runs in the two
versions readers run: mermaid 11.17 (GitHub, VS Code) and 10.9 (JetBrains IDEs).

Load it before the first figure of any output, in any phase. The rules hold in any document
language: scripts find caption and legend by their position, never by a word.

## 1. Red Flags (Anti-Rationalization)

- **"A diagram means Mermaid."** Step 0 comes first. A terminal shows Mermaid as code, a
  many-to-many relation reads better as a table, and a short chain reads better as a list.
- **"One figure for the whole section is more complete."** Structure, time and state in one figure
  produce edges nobody can follow. Split by concern; do not trim.
- **"The layout engine will sort it out."** dagre reduces crossings heuristically. It cannot remove
  the ones the graph forces: three sources each linked to the same three targets cross at least
  once in any drawing. Reduce, aggregate or split the graph itself.
- **"I'll reorder the declarations until it looks right."** Declaration and edge order move nodes
  in some figures and not in others. Change the structure first (fewer edges, a shorter title,
  another grouping), then re-render and look after every order change.
- **"The text implies this relation, I'll add it."** Draw only what a line of the text states. An
  invented arrow is read as a fact by the next implementer.
- **"The colours explain themselves."** A legend sits below the fence and names the notation this
  figure uses. Colour never carries a category alone.
- **"It renders in my preview."** GitHub runs 11.17, JetBrains 10.9, and 12.x changed every
  default. Check both pinned versions, or write `not rendered` in the hand-off.
- **"LR fits better."** Width sets the text size: a 900 px column shrinks the text of an 1800 px
  figure to half. A flowchart of more than 6 nodes runs top to bottom.
- **"I'll set the font and the theme for a consistent look."** Mermaid blanks any theme value
  containing `-`, `_`, `:` or `/`, so `sans-serif` disappears. A fixed `theme` draws dark text on
  GitHub's dark page. Set neither.

### Rationalization Table

| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "A single-node subgraph shows the system boundary." | Its title sits in the path of the only edge; the role goes on the node's second line. |
| "The full payload on the message saves the reader a lookup." | The settings line wraps it, and both lifelines cut through its text; the payload stays in the text's table. |
| "An edge between two subgraphs is shorter than three edges." | It runs border to border, and readers take it for a relation of the nearest members. |
| "Composite states group the lifecycle neatly." | A transition into an inner composite state becomes a long diagonal in 10.9 and 11.17; draw a flat graph. |
| "I'll write the plan chart by hand with `after`." | `after` drops a dependency declared below the task; `plan_gantt.py` computes starts. |
| "The render check is optional, the lint passed." | The lint reads source; crossings, title crossings and width exist only in the render. |

## 2. Capabilities

- Decide whether a figure is needed and choose its form: list, table, ASCII, Mermaid or image.
- Author flowchart, sequence, state, plan and small ER figures in one notation per document.
- Lint every figure of a document; render it in pinned versions, light and dark, and measure it.
- Generate a dependency plan chart with its critical path from a task list.
- Verify a figure element by element against the lines of the text.

## 3. Execution Mode

- **Mode**: hybrid.
- **Why this mode**: form, concern, aggregation and fidelity need judgement. Parsing, budgets,
  crossings, legibility and schedules are computed by scripts, because each is more than five lines
  of logic.

## 4. Script Contract

- **Commands**, run from the project root as
  `python3 .agent/skills/mermaid-authoring-guidelines/scripts/<script>`; `scripts/` below stands
  for that directory:
  - `python3 scripts/lint_mermaid.py <file.md|file.mmd> [--json] [--inventory] [--probe]` — exit
    0 no error, 1 error found, 2 internal failure or dead rule, 3 usage.
  - `python3 scripts/render_check.py <file> [--no-dark] [--forward] [--versions v11,v10] [--json]
    [--out DIR] [--fixture FILE]` — exit 0 pass; 1 a figure fails or does not parse; 2 not
    rendered: renderers or browser absent, a required render left out by `--no-dark` or
    `--versions`, or no mermaid fence; 3 usage. It renders 11.17.2, 10.9.8 and a dark 11.17.2 by
    default. A figure of a kind it does not model passes as `pass, geometry not checked`.
  - `bash scripts/setup_renderers.sh [--forward] [--dry-run]` — installs the pinned renderers once.
  - `python3 scripts/plan_gantt.py <plan.json|PLAN.md> [--write DOC | --check DOC] [--stages A,B]
    [--strict]` — exit 0 ok, 1 stale block or invalid plan, 2 internal failure, 3 usage.
- **Negative fences**: a fence whose last line is `%% negative: <names>` shows a defect on purpose.
  The marker counts only in this skill's `references/` and `scripts/tests/fixtures/`. Each
  instrument checks its own names. The lint requires one of the lint rules the marker names to
  fire. The render check requires one of the render checks it names to fail, and no render check
  it does not name may fail. A marker that names only lint rules has its renders graded as a
  positive figure. Never write the marker in a project document: there the lint reports the
  error MA-NEG-03, and both checks grade the fence as a figure.
- **Inputs**: Markdown or `.mmd` files; for plans, a JSON schedule or the JSON block under
  `<!-- contract:schedule -->` in a `PLAN.md`.
- **Outputs**: findings (text or JSON). Renders go outside the repository: to `--out`, or under
  the cache, where the check keeps the newest 20 `check-*` directories.
- **Thresholds and settings**: `assets/notation.json` only.
- **Idempotency**: the lint and `--check` write nothing. `--write` rewrites the marked block,
  `--fixture` its file, and the setup script its cache.
- **Dry-run support**: `setup_renderers.sh --dry-run`.

## 5. Safety Boundaries

- **Allowed scope**: the document the task names, and scratch files outside the repository.
- **Default exclusions**: archived artifacts (`docs/tasks/`, `docs/plans/`) and ledger records.
- **Network**: `setup_renderers.sh` downloads pinned npm packages once, into
  `${MERMAID_RENDER_HOME:-~/.cache/mermaid-authoring-guidelines}`, never globally and never into a
  repository. Run it only when the operator allows npm downloads. A render fetches nothing: the
  browser resolves no host name, uses no proxy, and talks to puppeteer over a pipe.
- **Browser sandbox**: stays on. `MERMAID_RENDER_NO_SANDBOX=1`, set by the operator, is the only
  switch that removes it.
- **Optional artifacts**: absent renderers do not block authoring; they make the hand-off say
  `not rendered`.

## 6. Validation Evidence

- **Local verification**, from this skill's directory:
  `python3 -m pytest -p no:cacheprovider scripts/tests -q`;
  `python3 scripts/lint_mermaid.py --probe`; `python3 evals/selftest_figure_evals.py`.
- **A/B evaluation** (2026-10-03, 66 runs): invalid under D8 (V2 not met). For information:
  one-pass success 0.61 against 0.33. `references/eval-results.md`.
- **CI signal**: Framework Gates → tooling tests, skill unit tests, eval-instrument selftest.

## 7. Instructions

### Step 0 — is a figure needed, and in which form

1. Draw a figure only when the text states relations, order, states or dependencies that a reader
   otherwise holds in memory. A section gets no figure by default.
2. Take the first form in this table that carries the information:

| Information | Read in | Form |
| :--- | :--- | :--- |
| up to 7 steps in a fixed order, no branches | anywhere | numbered list |
| a many-to-many relation, attribute sets, a full schema, a status matrix | anywhere but a log | table |
| a chain or a tree of at most 8 elements, link labels and comments included | anywhere | ASCII in a `text figure` fence |
| any figure | a medium that does not render Mermaid: terminal, log, MCP response, chat without a diagram renderer | list or ASCII; a table outside a log |
| structure, interaction in time, lifecycle, plan, a small ER model | Markdown on GitHub or in an IDE | Mermaid |
| a screenshot or a visual design | anywhere | image |

In a medium that does not render Mermaid, an answer carries Mermaid source only when the operator
asks for it, and then says that this medium does not render it. The info string `text figure`
marks an ASCII figure; a plain `text` fence is a listing or a log, and no figure rule applies to
it. List, table and ASCII rules: `references/ascii.md`.

### Step 1 — one concern, one kind

| Concern | Kind | Typical figure |
| :--- | :--- | :--- |
| structure: who calls, owns or reads whom | `flowchart` | container view, data flow, deployment |
| a decision procedure | `flowchart` | decision flow |
| dynamics: what happens in time | `sequenceDiagram` | one scenario, one request's life |
| lifecycle: what a record can be | `stateDiagram-v2` | states and their writers |
| a plan with dependencies | `gantt` | generated by `plan_gantt.py` |
| a few entities and cardinalities | `erDiagram` | at most 8 entities |

A section that needs two concerns gets two figures. Load the references for the kind; when the
request names no kind, run Step 0 first and then load the row of the kind it chose.

### Routing table

<!-- contract:routing -->

| Figure kind | Load |
| :--- | :--- |
| `none` | Step 0 first, then the row of the chosen kind |
| `flowchart` | `references/flowchart.md`, `references/layout-and-planarity.md`, `references/paired-examples.md` |
| `sequence` | `references/sequence.md`, `references/paired-examples.md` |
| `state` | `references/state.md`, `references/paired-examples.md` |
| `gantt` | `references/gantt.md` |
| `other`: ER, class, requirement and chart kinds | `references/other-kinds.md` |
| `ascii`, also a table or a list | `references/ascii.md` |

### Step 2 — facts first

List the facts the figure shows, each with the line that states it. The list is the figure's
scope. An element without a line is not drawn; a fact the figure's purpose needs is not left out.

### Step 3 — budget

| Kind | Soft budget | Hard budget |
| :--- | :--- | :--- |
| flowchart | 12 nodes, 12 edges | 18 nodes, 18 edges |
| sequence | 6 participants, 18 messages, 3 phase blocks | 6, 24, 4 |
| state | 12 states | 16 states |
| plan chart | 40 bars | 60 bars |
| ER | 8 entities | 10 entities |
| ASCII | 8 elements | 12 elements |

Over the soft budget: aggregate (one node for a group, members on its second line) or split. Keep
it only when the figure passes the render check. Over the hard budget: split.

### Step 4 — layout a reader traces

1. 0 edges through a node; at most 2 crossings, aim at 0; no edge through a title or a label.
2. In a flowchart, one edge per node pair. Merge parallel relations into one label
   (`claim · finish`); draw a start-and-reply pair as one two-headed dashed edge. A decision flow
   and a state diagram may hold one edge per direction.
3. A graph with more edges than 3 × nodes − 6 cannot be drawn without crossings. Three sources
   each linked to the same three targets cannot either. Aggregate one side, or use a table.
4. In a dependency graph, drop every edge a longer path already implies.
5. No edge to a subgraph id; no single-node subgraph; short subgraph titles; an external edge never
   enters the node under a title's centre.
6. A flowchart of more than 6 nodes runs top to bottom.
7. To move a node, change the structure first: fewer edges, a shorter title, another grouping.
   Order changes move nodes in some figures and not in others; re-render after each one.

Techniques with measured effects: `references/layout-and-planarity.md`.

### Step 5 — notation

1. The settings line of the kind is the fence's first line, copied from `assets/notation.json`. It
   pins `"look": "classic"`, and `"layout": "dagre"` for the kinds dagre lays out. It sets no
   `theme` and no font. A kind without a line there takes none.
2. Classes come from the palette of the kind's reference. Each category differs by shape or stroke
   style as well as by colour, and the legend names it.
3. Label limits, counted in characters per line so they hold in any script:
   - a node label: about 4 words, at most 32 characters, plus an optional `<small>` second line of
     at most 40;
   - an edge label: about 3 words, at most 24 characters, lowercase in cased scripts, names
     excepted;
   - a sequence message: at most 24 characters per line and 2 lines, broken with `<br/>`;
   - a participant name: at most 18 characters; a note: at most 48 characters per line, 3 lines.
4. Quote every flowchart label that holds punctuation. A state transition label takes no quotes,
   because they print. No raw `#`, `;` or `"` in a label: write `#35;`, `#59;` and `#quot;`; a
   state label is reworded instead.
5. Avoid: `@{ shape }`, edge ids, the kinds listed under `avoid` in `notation.json`, `style` in
   state diagrams, `classDef` in sequence diagrams, transitions into an inner composite state.
6. One document, one notation: one settings line per kind, one class block, one alias per
   participant.

### Step 6 — fidelity

1. Every node, edge, label, note and number has a supporting line. Names are written as the text
   writes them.
2. A group (subgraph, composite, section) uses a category the text defines.
3. A transition names its writer only where the text names one; otherwise it names the condition.
4. A call points from caller to callee. A value the callee returns is a reply arrow.
5. A number appears only on the subject the text attaches it to.
6. Run `lint_mermaid.py --inventory` and fill its support column with line numbers. For a figure
   in a review, use the adversarial verifier of `references/review-checklist.md`.

### Step 7 — caption and legend

- **Caption**: the paragraph directly above the fence. A bold label and title, then one sentence
  that states only what the figure shows: `**Figure 3.** Containers — who calls whom in §3.`
  The label follows the document's language (`**Рисунок 3.**`).
- **Legend**: the paragraph or list directly below the fence, when the figure uses two or more
  encodings. It names one item per encoding and only the notation this figure uses. With more
  than four items it is a list. It may state what is deliberately not drawn.
- `accTitle` and `accDescr` inside the fence give screen readers the same title and sentence.
  `mindmap` and `sankey-beta` fail to render with them, and `timeline` ignores them.

### Step 8 — check, then insert

1. Write the figure to a scratch `.mmd` outside the repository.
2. `python3 .agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py fig.mmd`.
   Postcondition: 0 `error`.
3. `python3 .agent/skills/mermaid-authoring-guidelines/scripts/render_check.py fig.mmd`.
   Postcondition: exit 0. Open the 11.17, 10.9 and dark PNGs and look for crossings, edges through
   titles, cut text and width.
4. Fix what the pictures show. After 3 render rounds, take the next simpler form of Step 0 — split,
   aggregate, or a table — instead of nudging.
5. Insert caption, fence and legend; run the lint on the whole document.
6. Exit 2 from the render check means `not rendered: <reason>` in the hand-off, never a pass.

**Plan charts.** Write the JSON schedule block under `<!-- contract:schedule -->`, then run
`plan_gantt.py`; never hand-write the dependency gantt. Details: `references/gantt.md`.

**Hand-off line.** One of these forms:

- `Figures: N · lint 0 error · rendered 11.17.2 + 10.9.8 + dark: pass`;
- `Figures: N · lint 0 error · rendered 11.17.2 + 10.9.8 + dark: pass, geometry not checked`,
  when the render check gives any figure that status;
- `Figures: N · lint 0 error · not rendered: <reason>`;
- `Figures: N · lint 0 error · render n/a: ASCII only`, when no figure is Mermaid.

## 8. Examples

`references/paired-examples.md` holds fourteen defects found in one production architecture
document, each with the fix that passed both renderers and a line-by-line check against its text.

| Pair | Defect → fix |
| :--- | :--- |
| N1 → P1 | one figure for structure and dynamics → a container view plus two sequences |
| N2 → P2 | a relation the text does not state → a support line per element |
| N3 → P3 | edges between subgraphs → the edges the text states, plus a legend sentence |
| N9 → P9 | composite states → a flat graph whose categories differ by fill and border |
| N13 → P13 | a caption that claims too much → a caption true to the figure |

## 9. Resources

- `assets/notation.json` — budgets, thresholds, settings lines, palettes, allowed and avoided kinds.
- `references/` — per-kind notation, layout and planarity, ASCII, renderer facts, paired examples,
  the review checklist, eval results.
- `scripts/` — the lint, the render check and its setup, the plan chart generator.
- `evals/` — the A/B evaluation; `evals/README.md` states what it measures.
