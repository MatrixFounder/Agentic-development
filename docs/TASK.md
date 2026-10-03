# TASK 108 — mermaid-authoring-guidelines: figures chosen by form, checked in two renderers, measured by A/B evals

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 108 |
| Slug | mermaid-authoring-guidelines |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Operator request and draft specification, 2026-10-02 |
| Base revision | `ee69bf2e0e35b11a2c525a5b75d64879d903c232` |
| Release | v3.33.0 |
| Archive name | `task-108-mermaid-authoring-guidelines.md` |
| Revision | 3 — answers `task-reviewer` rounds 1 and 2 (§8); measured amendments of 2026-10-02 in D26 |

<!-- contract:problem -->

## 1. Problem

The operator reports Mermaid figures in generated documents that a reader cannot trace: many
boxes, many converging arrows, no legend. The operator also states that not every figure belongs
in Mermaid. The measurements of 2026-10-02 below are reproduced in
`references/renderer-facts.md` of the new skill, one minimal figure per fact.

**The framework gives no figure guidance.**

- `architecture-format-core` §2.2 holds the placeholder
  `[Mermaid diagram showing connections between components]`, and §3.3 holds
  `[Mermaid diagram showing components and their interaction]`. No rule accompanies either.
- `architecture-format-core` line 12 states that the extended skill carries diagrams. It carries
  none.
- `architecture-format-extended` line 48 prescribes an ER diagram in PlantUML. GitHub does not
  render PlantUML.
- No skill, prompt or checklist states a budget, a layout rule, a fidelity rule or a legend rule.

**The framework's living documentation carries the defects.** In scope here are the READMEs,
`System/Docs/` and the skills. They hold seven Mermaid figures:

- `README.md:240`, `README.ru.md:240`;
- `System/Docs/PRODUCT_DEVELOPMENT.md:27`;
- `System/Docs/WORKFLOWS.md:37`, `:383`, `:406`;
- `.agent/skills/brainstorming/examples/demo_complex.md:68`.

All 7 render. 3 draw an edge through a subgraph title. `WORKFLOWS.md:37` holds 26 nodes and is 5:1
wide in mermaid 10.9. `demo_complex.md:68` has 8 participants. Six further figures sit in
`docs/presentation/`, `docs/design/` and `Backlog/`; they are out of scope.

**Viewers run different renderers.**

| Viewer | Mermaid |
| :--- | :--- |
| GitHub | 11.17.2 |
| GitLab.com | 11.16.1 |
| VS Code 1.140, built in | 11.17.0 |
| JetBrains IDEs 2024.3–2026.1 | 10.9.3 |
| Obsidian 1.13 | 11.13.0 |

Mermaid 12.0.0 (2026-09-10) changed the default layout to ELK and the default look to `neo`. No
viewer above renders with 12.x.

**Renderer behaviour that changes a figure and reports nothing.**

- A `themeVariables` value containing `-`, `_`, `:` or `/` is blanked in 10.9, 11.17 and 12.1.
  The draft's `"fontFamily": "Helvetica, Arial, sans-serif"` therefore sets no font.
- A diagram that fixes `theme: base` with light colours draws light-theme text on GitHub's dark
  page. Sequence messages, `alt` guards and gantt axis labels become unreadable there.
- `gantt` drops an `after` dependency declared below the dependent task. In one 86-task plan,
  5 bars start 7–12 h too early, identically in 10.9 and 12.1.
- 10.9 does not wrap node labels; 11.x wraps at 200 px; 12.x wraps at 120 px.
- 12.1 crashes when two ids containing `_` produce one edge id (`a --> b_c` and `a_b --> c`).

**Mermaid is not the form for every figure.** A terminal shows Mermaid source as code. A
many-to-many relation between two sets of three members each is `K3,3`, which is not planar:
every drawing of it has a crossing.

### 1.1 Goal

Add the skill `mermaid-authoring-guidelines` so that every figure an agent writes uses the least
elaborate sufficient form and, as Mermaid, passes the lint and the render check in mermaid
11.17.2 and 10.9.8.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Verified by |
| :--- | :--- | :--- | :--- | :--- |
| R1 | Skill skeleton and `SKILL.md` | Y | init_skill; sections; description; routing table; validation | A1, A14 |
| R2 | Form choice before any figure | Y | form ladder; output medium; table rule; ASCII reference; ASCII lint | A2, A14 |
| R3 | Authoring contract for a Mermaid figure | Y | one concern; budgets; layout; fidelity; labels; caption and legend; one notation | A5, A14 |
| R4 | Notation and version-safe settings per figure kind | Y | per-kind references; settings lines; dark render; palette; ER subset | A5, A15, A19 |
| R5 | Renderer facts reference | Y | measured versions; corrections; safe and avoid lists; viewer table | A15 |
| R6 | Static lint `lint_mermaid.py` | Y | rule set; probes; pinned rule list; JSON; inventory; CI scope | A2 |
| R7 | Render check and renderer setup | Y | pinned installs; versions; geometry; dark render; evidence file; not-rendered status | A4, A5, A17, A18, A19 |
| R8 | Plan chart generator `plan_gantt.py` | Y | schedule block; schedule; encoding; markers; split | A3 |
| R9 | Paired examples from the draft | Y | self-contained pairs; source lines; reworked positives; negatives fail | A5 |
| R10 | Integration into authoring and review surfaces | Y | templates; standard; prompts; checklists; workflows; settings; loading | A8 |
| R11 | A/B evaluation of the skill | Y | cases and keys; executor; renders; grader; statistics; decision rule; campaign | A6, A7, A13 |
| R12 | Tests and CI | Y | unit tests; wiring test; eval selftest; CI registration | A9 |
| R13 | Documentation, registry and release | Y | SKILLS.md; SKILL_TIERS.md; ARCHITECTURE; changelogs; backlog | A16 |

### 2.1 Sub-features

**R1 — skeleton and `SKILL.md`.**

1. `init_skill.py mermaid-authoring-guidelines --tier 2 --path <absolute .agent/skills>` creates the
   directory. Placeholder files the PLAN does not declare are removed.
2. The `description` starts with `Use when`, holds at most 50 words, and quotes request phrasings
   in English and Russian.
3. `SKILL.md` holds Purpose, Red Flags, Rationalization Table, Capabilities, Execution Mode,
   Script Contract, Safety Boundaries, Validation Evidence, Instructions, Examples and Resources.
4. `SKILL.md` holds a routing table under the anchor `<!-- contract:routing -->`. Its first column
   holds a kind token, its second the reference files for that kind. The row `none` names no
   reference: Step 0 runs first, then the row of the chosen kind applies. The eval executor reads
   the table by the anchor and by column position.
5. `validate_skill.py` reports 0 errors. `SKILL.md` stays under 3,000 words; one routed bundle
   (`SKILL.md` plus its references for one kind) stays under 16,000 words (D26). The eval selftest
   checks both counts.

**R2 — form choice.** Step 0 of the skill runs before any figure is written.

1. The agent draws a figure only when the text states at least one relation, order, state change
   or dependency between two or more named elements. A section gets no figure by default.
2. The agent takes the first sufficient form of the ladder: no figure → list or table → ASCII →
   Mermaid → image.
3. Output shown by a medium that does not render Mermaid carries no Mermaid fence. Such media
   include a terminal, a log, an MCP response and a chat surface without a diagram renderer. When
   the operator asks for Mermaid source there, the answer gives it and states that this medium
   does not render it.
4. A many-to-many relation, an attribute set or a full schema is a table.
5. ASCII is limited to the five patterns of `references/ascii.md` §2: a chain, a chain with one
   parallel pair, a tree, a directory tree and a two-column mapping. It stays within the ASCII
   budget of D14, in a fence whose info string is `text figure`. A `text` fence without the token
   `figure` is a listing, a log or command output, and no figure rule applies to it.
   `references/ascii.md` states the character set, the alignment rules and the caption rule.
6. An image file replaces no Mermaid source. Images are limited to screenshots and visual design.
7. The lint reports, per `text figure` fence:
   - a tab;
   - a double-width character on an aligned line;
   - a line wider than 100 columns;
   - a box border that is not aligned.

**R3 — authoring contract for Mermaid.**

1. One figure carries one concern: structure, dynamics, state, or plan.
2. Each kind has the soft and hard budget of D14. Over the soft budget the agent aggregates or
   splits, unless the figure passes the R7.6 thresholds. Over the hard budget the agent splits.
3. A rendered figure has 0 edges through a node, at most 2 edge crossings, and no edge through a
   subgraph title or a label. In a flowchart, at most one edge joins an unordered pair of nodes;
   a decision flow and a state diagram may hold one edge per direction.
4. A flowchart of more than 6 nodes is laid out top to bottom.
5. Each node, edge, label, note and number is supported by a line of the document. Names are
   written as the text writes them. Groups use the text's own categories. Arrows point the way
   the text states the call.
6. Label lengths and line counts are checked in characters per line, per D25. An edge label is
   lowercase in a script that has letter case.
7. A caption is the paragraph directly above the fence; a heading is not a caption. A legend is the
   paragraph or list directly below the fence when the figure uses two or more encodings; it names
   one item per encoding. The lint and the contract check enforce these positions. Scripts find
   both by position, never by a word of one language.
8. All figures of one document share one settings line per kind, one class block and one alias
   per participant.

**R4 — notation and version-safe settings.**

1. `references/flowchart.md`, `sequence.md`, `state.md`, `gantt.md`, `other-kinds.md` and
   `ascii.md` each hold the notation, a settings line and a template for their kinds.
2. Every settings line pins `"look": "classic"`; the lines of the kinds that dagre lays out
   (flowchart, state, ER, class, requirement) also pin `"layout": "dagre"`. No line holds a `theme`
   key or a `themeVariables` value containing `-`, `_`, `:` or `/`. The lint reports a `theme` key.
3. Every template passes the render check of R7, the dark render included (A19).
4. The palette of `assets/notation.json` is the default palette. Each class pairs a fill with a
   text colour of contrast ratio 4.5:1 or more (WCAG 2.2 SC 1.4.3). No category is carried by
   colour alone: shape or stroke style also differs, and the legend names each (SC 1.4.1).
5. An ER figure stays within the ER budget of D14. A full schema is a table.
6. `other-kinds.md` lists the allowed kinds with their version floor, and the kinds to avoid:
   `architecture-beta`, `block-beta`, C4, `kanban`, `packet`, `radar`, `treemap`, `pie`,
   `xychart-beta`, `sankey-beta`, and unsuffixed `xychart` and `sankey`.

**R5 — renderer facts.** `references/renderer-facts.md` states each fact with:

- the versions measured;
- a minimal reproduction;
- the author rule.

It corrects the draft's facts 1, 2, 5 and 7. It lists the constructs safe in 10.9.8, 11.17.2 and
12.1.0, and the constructs to avoid. It holds the viewer table of §1 with its date. It records the
comparison of 10.9.3, which JetBrains ships, with 10.9.8 as a one-time measurement: its date, the
install it used, and the result per reproduction.

**R6 — `scripts/lint_mermaid.py`.** Python standard library only. The lint writes no file.

1. Input: a Markdown file, from which every `mermaid` fence and every `text figure` fence is read,
   or a `.mmd` file.
2. Each rule has an id, a severity (`error`, `warn`) and a probe pair. The positive probe must fire
   and the negative probe must not fire. `--probe` checks every pair. A failed probe exits 2.
3. The rules cover:
   - parse hazards, and syntax above the 10.9 floor;
   - settings validity, the sanitizer rule, a `theme` key, and settings consistency in a document;
   - id shape `[A-Za-z0-9]+`;
   - budgets, duplicate edges per R3.3, and planarity (D21, severity `warn`);
   - edges to a subgraph id, and single-node subgraphs;
   - transitions across composite states, and `style` in state diagrams;
   - `classDef` in sequence diagrams;
   - numbered flowchart edges, label lengths and line counts (D25), and `LR` flowcharts;
   - class contrast, and classes used but not defined;
   - gantt hazards, `text figure` fences, and caption and legend positions.
4. Output: one line per finding with the line of its fence, or JSON with `--json`. Exit codes
   follow D20.
5. `--inventory` prints every node, edge, label, note and number of a figure in a table with an
   empty column for the supporting line.
6. The unit test holds the rule ids as a literal set and compares it with the registry both ways.
7. CI runs the lint as a gate on the skill's own references, templates and the paired examples.
   A sweep of other documents is advisory.
8. The lint checks one document in under 2 seconds on the CI runner.

**R7 — `scripts/render_check.py` and `scripts/setup_renderers.sh`.**

1. The setup script installs three pinned pairs:
   - mermaid-cli 10.9.1 with mermaid 10.9.8;
   - mermaid-cli 11.17.0 with mermaid 11.17.2;
   - mermaid-cli 12.0.0 with mermaid 12.1.0.
2. Installs go to `${MERMAID_RENDER_HOME:-~/.cache/mermaid-authoring-guidelines}`. The npm cache
   goes there too. The script never installs globally and never writes inside a git work tree.
3. The script installs from committed lockfiles with `npm ci --ignore-scripts`. It reuses a cached
   `chrome-headless-shell`. With none cached, it fails at a named step and prints how to supply
   one (`MERMAID_RENDER_CHROME`).
4. `render_check.py` renders each figure in 11.17.2 and 10.9.8, plus a dark render in 11.17.2.
   `--forward` adds 12.1.0. `--no-dark` skips the dark render and then exits 2 with
   `not rendered: dark render skipped`.
5. It writes SVG and PNG per render and computes, from the SVG and from text measured in the
   browser:
   - crossings;
   - edges through nodes, through titles and through labels;
   - label overlaps and clipped labels;
   - size, and the effective font size in a 900 px column;
   - the contrast of every text element against the background it is drawn on.
6. A figure passes with:
   - at most 2 crossings;
   - 0 edges through nodes, through titles and through labels;
   - 0 label overlaps and 0 clipped labels;
   - the smallest text a reader must read at 10 px or more in the column; text of a class in
     `thresholds.legibility_exempt_classes` of `notation.json` is excepted (today the `autonumber`
     digits of a sequence figure);
   - every text whose colour or background the figure sets at a contrast of 4.5:1 or more, in the
     light and in the dark render. Text drawn entirely in the viewer's theme colours is reported
     with its contrast, for information (D26).
   A lifeline is not an edge: a lifeline through a message label is the warning
   `lifeline_through_label`, which gates nothing; the review reads it in the PNG (FIG-9).
7. Exit codes follow D20. Absent renderers or no browser exit 2 and print `not rendered: <reason>`.
   A check that did not render never reports a pass. An input with no mermaid fence is not
   rendered (exit 2). A figure of a kind whose geometry the check does not model passes as
   `pass, geometry not checked`.
8. `--json` writes an evidence file next to the renders. Per figure it records the sha256 of the
   fence text, each renderer version, the browser build and the font family drawn.
9. Renders run with mermaid `securityLevel: strict`. The browser keeps its sandbox, resolves no host
   name (localhost included), uses no proxy, and talks to puppeteer over a pipe, so no DevTools
   port opens.
10. The default output directory is a fresh directory under the install home, outside any git work
    tree.

**R8 — `scripts/plan_gantt.py`.**

1. Input: a JSON file, or a Markdown plan holding one JSON block under the anchor
   `<!-- contract:schedule -->` (D19). A task carries `id`, `title`, `stage`, `est` (integer hours),
   `deps`, and optionally `status`. The framework's plan template omits `status` (D11).
2. The script computes early starts, the critical path and the ready-to-start list. A cycle, an
   unknown dependency, a duplicate id or a non-integer estimate exits 1 with a message.
3. The block uses:
   - numeric starts, and no `after`;
   - `axisFormat %Q`;
   - `todayMarker off`;
   - sanitized labels;
   - one contiguous section per stage.
4. `--write` replaces the region between `<!-- generated:plan-gantt-start -->` and
   `<!-- generated:plan-gantt-end -->`; `--check` exits 1 when that region is stale and writes
   nothing. The two options together exit 3. A document without both markers exits 1. A region
   that holds a heading, an HTML comment other than the stored stage groups, or a fence other than
   `mermaid` exits 1 and is not written; so do two start markers with one end marker.
5. A plan of fewer than 8 tasks gets an empty region from `--write`, and `--check` passes on it.
6. `--stages` draws named stages on the whole-plan schedule, so hours stay absolute. The groups name
   every stage once. `--write` stores them in the first line of the region, and `--write` or
   `--check` without `--stages` reuses them, so the UC-2 postcondition holds for a split chart.
7. A plan whose headings and titles are Russian yields, compared with its English twin, the same
   bar starts, durations, section order, critical path and ready list.

**R9 — paired examples.**

1. `references/paired-examples.md` holds the draft's pairs N1–N14 and P1–P14, and P15, which has
   no negative.
2. Each pair carries the source lines its figure illustrates. No pair cites a path or a task id of
   another project.
3. Every positive figure passes the lint with 0 `error` and the render check in 10.9.8 and 11.17.2.
   P1, P4 and P9 fail the render check as drafted; their rework is recorded beside them.
4. Every negative figure fails at least one named lint rule or render threshold. A failure of a
   render check that the marker does not name fails the fence.
5. `scripts/tests/fixtures/paired-examples-geometry.json` holds the render evidence of every
   example (R7.8). A unit test recomputes each fence hash from `paired-examples.md` and fails with
   `re-render` when one differs; it checks the stored geometry against the thresholds without node.

**R10 — integration.** The PLAN lists every edited path. The surfaces are:

1. Templates: `architecture-format-core` §2.2, §3.3 and line 12; `architecture-format-extended`
   line 48.
2. Parent standard: `documentation-standards` gains §5.6 "Figures". §4.4 gains the anchors
   `contract:schedule`, `contract:routing`, `generated:plan-gantt-start` and
   `generated:plan-gantt-end`.
3. Prompts:
   - `04_architect_prompt.md` loads the skill before the first figure. An absent skill makes the
     architect use a list or a table and report the absence.
   - `05_architecture_reviewer_prompt.md` rates a figure that contradicts its text MAJOR. Its line
     49, `- **MINOR:** Descriptions, diagram clarity.`, is reworded to match.
   - `06_planner_prompt.md` writes the schedule block, and the generated chart for 8 or more tasks.
   - `07_plan_reviewer_prompt.md` lists the caller-supplied `plan_gantt.py --check` output and the
     figure lint output among its inputs.
4. Checklists: `architecture-review-checklist`, `plan-review-checklist`, `task-review-checklist`
   and `code-review-checklist` gain figure items and Script Contract entries (D24).
5. Workflows: `01-start-feature.md`, `vdd-01-start-feature.md`, `02-plan-implementation.md` and
   `vdd-02-plan.md` name the figure lint, and `plan_gantt.py --check` for a plan, in the evidence
   the caller runs before a review.
6. Permissions: `.claude/agents/architect.md` permits the lint and the render check.
   `.claude/settings.json` allows exactly three patterns without approval (D9):
   `lint_mermaid.py *`, `plan_gantt.py --check *` and `plan_gantt.py docs/PLAN.md --check *`.
7. Loading: `skill-phase-context`, `System/Docs/SKILL_TIERS.md`, and the bootstrap files
   `CLAUDE.md`, `AGENTS.md` and `GEMINI.md`. The bootstrap files carry the output-medium rule of
   R2.3 themselves, with its exception (D2). A generated plan chart needs no skill load.
8. Other authoring skills:
   - `brainstorming` replaces its order "Mermaid → ASCII → bullet lists" with a pointer to Step 0;
   - `security-audit` `threat_model.md` draws its DFD with the skill;
   - `skill-reverse-engineering` writes the text first and draws figures from it with the skill;
   - `skill-planning-format`, its plan template and `examples/PLAN_EXAMPLE.md` carry the schedule
     block and the markers.
9. `skill-product-solution-blueprint` is not edited; it keeps its text-only rule.
10. Surfaces point at the skill and restate no budget, threshold or label-limit value.

**R11 — A/B evaluation.** Files live under `evals/` of the skill.

1. Cases:
   - a control C0: a 4-node, 4-edge component paragraph with no decoy, which a plain correct
     figure passes;
   - eight decoy cases C1–C8 over the Mermaid kinds: container view, sequence, state, calendar
     gantt, data flow, deployment, decision flow, and a `K3,3` structure;
   - two form cases: F1 asks for an explanation printed in a terminal, F2 for a role-by-operation
     relation.
2. A decoy is a relation, number, group or writer that the case document does not state and that a
   model is likely to draw. A key lists:
   - entities with aliases, stated relations, stated numbers, stated groups and decoys;
   - the kind the prompt names (`none` when it names none) and the acceptable forms;
   - the check families that apply.

   C8 accepts a flowchart and a table. F1 accepts an ASCII figure and a list. F2 accepts a table.
   The grader's normalisation rule is hashed with the keys.
3. The arms differ in one input. `with_skill` receives the case prompt preceded by `SKILL.md` and
   the references the routing table names for the key's kind; kind `none` adds no reference. A
   selftest removes that block and compares the rest with the `without_skill` prompt byte for byte.
4. `run_evals.py` runs `claude -p` in a fresh temporary directory with no context file above it.
   - Tools, skills, MCP servers and slash commands are off; session persistence is off.
   - Model and effort are passed as flags, overriding user settings.
   - A named list of inherited variables is removed, among them `CLAUDECODE` and `CLAUDE_EFFORT`;
     authentication variables are kept. Each run record names the removed variables.
   - `--dry-run` spawns nothing. `--reps` is odd, so each case has a median run.
5. `render_corpus.py` renders every extracted figure in 11.17.2, 10.9.8 and a dark 11.17.2, and in
   12.1.0 for information. It stores the render evidence per run. CI does not run it.
6. `grade_figures.py` is a function of committed files. It imports the lint and the geometry
   analysis of R6 and R7 and restates none of their thresholds.
7. Headline checks: renders, geometry, legibility (dark included), hard budget, one concern,
   fidelity, form fit, ASCII lint, colour, caption present and true, legend present and true.
   Caption and legend count in either position next to the fence.
8. Contract checks are reported apart, as a check that the bundle reached the model: settings
   line, palette, shapes, caption and legend form and position, names, one edge per pair, soft
   budget, top-to-bottom direction.
9. Statistics pair the arms by case: a case-cluster bootstrap interval and a sign test.
10. The decision rule of D8 is written to `evals/README.md` before the first paid run. The sha256
    of the README, every key and the prompt template is recorded in `evals/PROVENANCE.txt` and
    `docs/reviews/framework-audit-108.md`, and reported to the operator. `run_evals.py` refuses to
    start while any of those hashes differs, and writes them into every run record.
11. Campaign: `claude-opus-5-5`, effort `xhigh`, 3 repetitions, 11 cases, 2 arms (66 runs), within
    the D18 budget. Corpus, render evidence, gradings and report are committed.
12. The calibration of D16 runs between rendering and grading (UC-5).
13. F1 measures the wording of Step 0. It does not measure the delivery of D2 through the bootstrap
    files, which no eval run loads.

**R12 — tests and CI.**

1. Unit tests cover every lint rule, the plan generator, the geometry analysis on committed SVG
   fixtures, and the stored example and template geometry. No unit test needs node or a browser.
2. A wiring test pins every R10 surface. It also fails when a surface quotes a value of
   `assets/notation.json` with its unit, such as `18 nodes` or `10 px`.
3. The eval selftest spawns no agent and renders nothing, and it re-derives a committed report.
4. Count sentences in `System/Docs/SKILLS.md` keep two existing pins passing:
   - `artifact-formalizer` TC-EV-13b, which reads the count after `selftest_evals.py`;
   - `selftest_scan.py` TC-SHIP-08, which reads every `<n> cases` outside `evals/` list items.
5. The new modules run in CI through the curated suite or `framework-gates.yml`.

**R13 — documentation and release.** `System/Docs/SKILLS.md`, `System/Docs/SKILL_TIERS.md` and
`docs/ARCHITECTURE.md` list the skill. `CHANGELOG.md` and `CHANGELOG.ru.md` carry v3.33.0 with a
migration note for consumer projects. `docs/BACKLOG.md` carries each follow-up of §9.

## 3. Non-functional requirements, constraints and assumptions

**Supply chain.**

- Each renderer install has a committed lockfile under `assets/renderers/<tag>/`.
- `npm ci --ignore-scripts` installs from it; exact versions only.

**Browser safety.** The headless browser keeps its sandbox; only `MERMAID_RENDER_NO_SANDBOX=1`
removes it. Mermaid runs with `securityLevel: strict`. The browser resolves no host name, localhost
included, and uses no proxy (`--host-resolver-rules=MAP * ~NOTFOUND`, `--no-proxy-server`);
puppeteer talks to it over a pipe. Every node process of a render runs inside its install
directory, never in the caller's. Each install holds an empty `.puppeteerrc.json`, so puppeteer's
search for a configuration file stops there. The install home, each install and the output
directory are private to the user; a directory others may write to is refused (review round 2,
SEC2-01, SEC2-08).

**Compatibility.**

- Python 3.11 or newer.
- Node.js 22.13 or newer for the 11.17 and 12.1 installs. Measured: mermaid-cli 12.0.0 declares
  `>=22.13.0`, and the puppeteer of mermaid-cli 11.17.0 declares `>=22.12.0`.
- `setup_renderers.sh` targets macOS and Linux with bash.
- The static lint, the plan generator and the grader need no node.

**Assumptions.**

- A `chrome-headless-shell` is cached, or its path is supplied.
- The `claude` CLI is installed and authenticated for the eval runs.
- The viewer versions of §1 hold as of 2026-10-02.

**Deviation (D17).** `framework-upgrade` §3.1 states "No path outside this repository is edited
during the run." and "No copy of any file is written outside version control." This run writes,
outside the repository:

- renders in the session scratch directory;
- renderer installs, the npm cache, and the copies of the committed manifests inside each install,
  in `~/.cache/mermaid-authoring-guidelines`;
- temporary browser profiles in the system temporary directory, removed after each render;
- the temporary working directories of the eval runs;
- the research material in the session scratch directory: earlier renderer installs and viewer
  bundles unpacked for version checks.

The eval runs keep no session transcript (`--no-session-persistence`). None of the paths above is
a rollback copy or a path of another repository. The operator licensed the complete list on
2026-10-02.

**Budget (D18).** The paid campaign spends at most 60 USD across all its runs.

<!-- contract:use-cases -->

## 4. Use Cases

**UC-1 — the architect adds a figure to `docs/ARCHITECTURE.md`.**
*Actor:* the architect agent.
*Precondition:* the section text states the relations to show.
*Main:*
1. The agent loads the skill and runs Step 0. The form is Mermaid.
2. The agent lists the facts with their line numbers and picks the kind by concern.
3. The agent writes the figure in a scratch file and runs the lint. Postcondition: 0 `error`.
4. The agent runs the render check and opens the PNGs. Postcondition: exit 0.
5. The agent fills the inventory with a supporting line per element.
6. The agent inserts the figure with its caption and legend and runs the lint on the document.
   Postcondition: 0 `error` on the fences the edit adds or touches.

*Alternative A1 (at 4):* the render check exits 2. The agent records `not rendered: <reason>` in
its hand-off and claims no visual check.
*Alternative A2 (at 3):* the figure exceeds the hard budget. The agent splits it by concern.
*Alternative A3 (at 1):* the skill is absent from the project. The agent writes a list or a table
and reports the absent skill.
*Alternative A4 (at 4):* the render check exits 1. The agent changes the figure under R3 and
repeats from step 3, at most 3 times; it then takes the next simpler form of the ladder.
*Postcondition:* the document holds a figure whose every element cites a line.

**UC-2 — the planner adds the plan chart.**
*Actor:* the planner agent.
*Precondition:* `docs/PLAN.md` holds a schedule block with 8 or more tasks.
*Main:* the planner runs `plan_gantt.py docs/PLAN.md --write docs/PLAN.md`. The chart appears
between the markers.
*Alternative A1:* a dependency names an unknown task. The script exits 1; the planner fixes the
block.
*Alternative A2:* the plan holds fewer than 8 tasks. The region stays empty.
*Alternative A3:* the plan holds more than 60 tasks. The planner writes one chart per stage group
with `--stages`.
*Alternative A4:* the plan changes after review. The planner edits the block and runs `--write`.
*Postcondition:* `plan_gantt.py docs/PLAN.md --check docs/PLAN.md` exits 0.

**UC-3 — an agent explains a flow in a terminal.**
*Actor:* any agent answering the operator.
*Precondition:* the answer goes to a medium that does not render Mermaid.
*Main:* the medium rule applies; the answer holds an ASCII chain or a numbered list.
*Alternative A1:* the operator asks for Mermaid source. The answer gives the source in a fence and
states that this medium does not render it.
*Postcondition:* without such a request, the answer holds no Mermaid fence.

**UC-4 — a read-only reviewer checks a figure.**
*Actor:* `architecture-reviewer`.
*Precondition:* the caller supplies the lint output, and the render evidence or a
`not rendered: <reason>` line.
*Main:* the reviewer applies the checklist items to that output and to the text.
*Alternative A1:* the lint output is absent. The figure is reported not verified, and the review
does not return APPROVED while a figure is not verified.
*Postcondition:* the figure items carry a verdict. `not rendered` with a reason lets the review
conclude; it is not a pass of the render items (D24).

**UC-5 — the operator runs the eval campaign.**
*Actor:* the operator, or the orchestrator on the operator's licence.
*Precondition:* renderers installed; hashes recorded and reported (R11.10); budget per D18.
*Main:*
1. `run_evals.py` draws the runs of both arms.
2. `render_corpus.py` renders every figure.
3. A seeded sample, stratified by case and arm over all outputs, is drawn and labelled (D16). The
   labels are written to `evals/calibration/labels.json`.
4. `grade_figures.py` grades the corpus and writes `report.json`.

*Alternative A1:* a run fails on infrastructure. It is excluded, listed, and run again.
*Alternative A2:* a validity criterion of D8 fails. The instrument is fixed and the affected runs
are re-run or re-graded; this uses no revision round.
*Alternative A3:* an effect criterion of D8 is not met. One revision round follows (D18); the
report shows both rounds.
*Alternative A4:* the budget runs out. The campaign stops, and `report.json` marks each criterion
it could not evaluate `not evaluated (budget)`.
*Postcondition:* `report.json` states each criterion of D8 as met, not met, or not evaluated.

**UC-6 — a section with an old figure is edited.**
*Actor:* any authoring agent.
*Precondition:* the section holds a figure that fails the lint or the render check.
*Main:* the agent redraws that figure with the skill in the same edit.
*Alternative A1:* the renderers are absent. The agent runs the lint only and records
`not rendered: <reason>`.
*Postcondition:* every figure the edit touches passes; figures in sections it does not touch stay.

<!-- contract:acceptance -->

## 5. Acceptance Criteria

| ID | Criterion |
| :--- | :--- |
| A1 | `validate_skill.py` reports 0 errors on the skill; `validate_skills.py` reports every skill valid |
| A2 | The lint tests pass; the rule-id set is a literal; `lint_mermaid.py --probe` exits 0 |
| A3 | The plan tests pass; the example's bar starts equal its early starts in a hash-bound SVG fixture |
| A4 | The geometry tests pass on committed SVG fixtures without node |
| A5 | The paired-example test passes against `paired-examples-geometry.json` (R9.3–R9.5) |
| A6 | The eval selftest passes with zero tokens and zero renders |
| A7 | `report.json` states each D8 criterion as met, not met, or not evaluated with its reason |
| A8 | The wiring test passes |
| A9 | Every job of `.github/workflows/framework-gates.yml` passes when run locally |
| A10 | `scan_register.py` reports no new `warn` on an edited Markdown file |
| A11 | `git status --short` lists only the paths `framework-upgrade` §5 accepts as declared |
| A12 | The final `code-reviewer` and `security-auditor` rounds leave no open blocking finding |
| A13 | A run starts only while the projected spend stays within 60 USD (D18); release notes state the D8 outcome |
| A14 | `SKILL.md`, the references and `evals/README.md` report 0 `warn` in `scan_register.py` |
| A15 | Each fact of `renderer-facts.md` has a reproduction that renders as stated |
| A16 | `SKILLS.md`, `SKILL_TIERS.md`, ARCHITECTURE §10 and both changelogs name the skill |
| A17 | A unit test runs `render_check.py` with an empty `MERMAID_RENDER_HOME`: exit 2, `not rendered:` |
| A18 | `setup_renderers.sh --dry-run` lists the three pairs and refuses a home inside a git work tree |
| A19 | Every `references/` template passes the render check, dark included, per R7.7; a hash-bound fixture holds it |

<!-- contract:open-questions -->

## 6. Open Questions

**OQ1 — none open.** The operator answered OQ-A to OQ-D on 2026-10-02 and confirmed the complete
D17 list the same day; D17, D18, D9 and D16 record the answers. OQ-E and OQ-F became D24 and D23.

## 7. Decisions

**D1, 2026-10-02, operator: the skill is named `mermaid-authoring-guidelines`.** The operator
named it. Rejected: `mermaid-guidelines` (the draft's name). This departs from the gerund naming
advice of `skill-creator`; the framework's skills mostly use noun phrases.

**D2, 2026-10-02, orchestrator: tier 2, loaded on a condition.** The condition is the first figure
of any output, in any phase; a generated plan chart needs no load. The bootstrap files carry the
medium rule of R2.3 themselves, so a terminal answer obeys it with no skill loaded. Rejected:
tier 1 — the phases would then load it when no figure is drawn.

**D3, 2026-10-02, orchestrator: 11.17.2 and 10.9.8 are the check pair; 12.1.0 is a forward check.**
Rejected: 12.1 and 10.9, as drafted — no viewer of §1 renders with 12.x.

**D4, 2026-10-02, orchestrator: every render check includes a dark render of 11.17.2.** A check
without it reports `not rendered`. Rejected: a fixed light theme — GitHub's dark page then hides
text drawn on the canvas.

**D5, 2026-10-02, orchestrator: renderers install to a cache outside the repository.** The 10.9
and 11.17 installs measure 549 MB together; the 12.1 install adds 438 MB. Rejected: an install
inside the skill — `.gitignore` has no `node_modules` rule, and the installer links every skill
entry into consumers.

**D6, 2026-10-02, orchestrator: the lint is CI-gated on the skill's own files; rendering is an
optional tier.** CI installs Python only. Rejected: a render step in CI — it adds node and a
browser to every run.

**D7, 2026-10-02, operator: Mermaid is the last textual rung of the form ladder.** Rejected: Mermaid
by default for every figure — the operator's statement of 2026-10-02.

**D8, 2026-10-02, orchestrator: the decision rule of the campaign.**

*Scores.*

- A run's headline score H is the fraction of the case's applicable headline checks it passes.
- A per-figure check passes only when every figure of the run passes it.
- A run whose answer holds no figure in any form fails every applicable check.
- H-core is the same score without the budget, caption and legend checks.
- A case's score is the median over its repetitions.
- Δ_H is the mean, over the ten cases C1–C8, F1 and F2, of the `with_skill` case score minus the
  `without_skill` case score. C0 is not in Δ_H: it enters V3 and the "behind" clause of H3.

*Validity criteria, evaluated first.* A failure here marks the campaign invalid; the instrument is
fixed and the affected runs are re-run or re-graded, which uses no revision round.

| # | Criterion |
| :--- | :--- |
| V1 | no ungraded infrastructure failure; the served model is the pinned one in every run |
| V2 | detector precision and recall ≥ 0.9 per defect type, and Cohen's κ ≥ 0.8, on the calibration set |
| V3 | control C0: `without_skill` H-core ≥ 0.9 |
| C1 | contract-check rate ≥ 0.8 with the skill; the rate without it is reported for information |

*Effect criteria.* The claim "the model without the skill does much worse" holds only when all hold:

| # | Criterion |
| :--- | :--- |
| H1 | Δ_H ≥ 0.25 and its 95 % case-cluster lower bound ≥ 0.10 |
| H2 | Δ_H-core ≥ 0.15 and its lower bound > 0 |
| H3 | `with_skill` ahead on 8 or more of the ten cases; behind beyond 0.10 on none, C0 included |
| V4 | Δ_H > 0 with any one check family left out |

The sign test is reported as information; H3 is a breadth criterion, not a significance test.
Rejected: one pooled pass rate — it lets a single check family carry the claim.

**D9, 2026-10-02, operator: `.claude/settings.json` allows the lint and `plan_gantt.py --check`
without approval.** The patterns are those of R10.6. The render check and the setup script ask
every time. No TIER 0 skill changes, so `skill-safe-commands` names neither command. Rejected: a
`skill-safe-commands` edit — audits 097–104 pass on "no TIER 0 skill modified".

**D10, 2026-10-02, orchestrator: other repositories change after the operator's commit.** That
covers Universal-skills, consumer projects and the obsidian wiki skills.

**D11, 2026-10-02, orchestrator: plan status tokens are deferred.** The framework's plan chart
shows every bar as waiting, and the critical path. Rejected: status tokens now — they change four
develop workflows.

**D12, 2026-10-02, operator: the paired examples stay.** The draft calls them its strongest
teaching material. Each pair carries its own source lines, and no pair cites another project.

**D13, 2026-10-02, orchestrator: caption and legend are found by position.** ARCHITECTURE §7
invariant L1 forbids a gate keyed on the document's language.

**D14, 2026-10-02, orchestrator: budgets are soft and hard.**

| Kind | Soft | Hard |
| :--- | :--- | :--- |
| Flowchart nodes / edges | 12 / 12 | 18 / 18 |
| Sequence participants / messages / phase blocks | 6 / 18 / 3 | 6 / 24 / 4 |
| State states | 12 | 16 |
| Plan chart bars | 40 | 60 |
| ER entities | 8 | 10 |
| ASCII elements | 8 | 12 |

Rejected: one hard limit — `System/Docs/WORKFLOWS.md:383` holds 15 nodes and 16 edges and renders
with 0 crossings in both versions.

**D15, 2026-10-02, orchestrator: settings lines carry no font family.** Measured: a top-level
`fontFamily` makes 10.9 drop every other theme variable, and a hyphenated value is blanked.
Rejected: `"Helvetica, Arial"` in `themeVariables` — it binds every viewer to two fonts.

**D16, 2026-10-02, operator: the orchestrating model labels the calibration set.**

- The sample holds at least 30 outputs, seeded and stratified by case and arm, drawn before any
  grading is read.
- Each sampled output is labelled per defect type from its PNGs and text, without the detector's
  verdicts.
- A defect type with fewer than 3 positives in the sample is topped up from the `fail.md` fixtures
  and the negative paired examples that carry it, recorded as seeded.
- κ is the agreement between these labels and the detector's verdicts, per defect type.
- The report marks V2 `corroborated`, per the review-dispatch rule.

**D17, 2026-10-02, operator: the writes outside the repository listed in §3 are licensed for this
run.** The operator confirmed the complete list the same day.

**D18, 2026-10-02, operator: the campaign budget is 60 USD.**

- `run_evals.py` sums `total_cost_usd` over the run envelopes. It starts no run whose projected
  cost, at the mean cost per run so far, would cross the budget.
- When an effect criterion of D8 is not met, one round of skill revisions follows. A revision
  changes a rule for every figure, never for one case.
- The second round re-draws the `with_skill` arm only. The report shows both rounds and labels the
  second `post-revision, same cases`.

**D19, 2026-10-02, orchestrator: the plan generator reads a JSON schedule block.** The block sits
under the registered anchor `<!-- contract:schedule -->`. Rejected: parsing the plan's prose fields
— `Task`, `Stage` and `Dependencies:` are prose that consumer projects translate (L1).

**D20, 2026-10-02, orchestrator: exit codes.** Codes 2 and 3 mean what they mean in ARCHITECTURE
§7.4: a broken or absent instrument, and a wrong invocation. Code 1 is a gate failure, which the
advisory scanner of §7.4 does not have.

| Script | 0 | 1 | 2 | 3 |
| :--- | :--- | :--- | :--- | :--- |
| `lint_mermaid.py` | no error | error findings | instrument broken or dead rule | usage |
| `render_check.py` | pass | the figure fails or does not parse | not rendered | usage |
| `plan_gantt.py` | ok | stale region or invalid plan | instrument broken | usage |

**D21, 2026-10-02, orchestrator: planarity is tested exactly.** The lint runs a planarity test on
the undirected simple graph of each flowchart within the hard budget. The edge bounds
`E ≤ 3V − 6`, and `E ≤ 2V − 4` for a triangle-free graph, run first. A non-planar graph is a
`warn` pointing at aggregation, a split or a table; the render check decides pass or fail.
Rejected: the first bound alone — it misses `K3,3` (9 ≤ 12).

**D22, 2026-10-02, orchestrator: the eval keeps `skill-creator`'s formats and replaces its runner.**
The corpus uses the on-disk layout and `grading.json` shape of `skill-creator`, so
`aggregate_benchmark.py` and the review viewer work. Rejected: subagent runs — subagents inherit
`CLAUDE.md` and the skill catalogue, so the arms would differ in more than one input (L5).

**D23, 2026-10-02, operator: one run.** The operator chose one run under the D17 licence. The
commit may be split by the operator.

**D24, 2026-10-02, orchestrator: lint output is required review evidence; render output is
optional.** The line `not rendered: <reason>` is a distinct state. It lets a review conclude and
does not pass the render items. Rejected: requiring renders — a project without renderers could
never pass a review that holds a figure.

**D25, 2026-10-02, orchestrator: label length is checked in characters per line.**

| Label | Characters per line | Lines |
| :--- | :--- | :--- |
| Node label, first line | 32 | 1 |
| Node label, second line | 40 | 1 |
| Edge label | 24 | 2 |
| Sequence message | 24 | 2 |
| Sequence participant name | 18 | 1 |
| Note | 48 | 3 |

`SKILL.md` keeps "about 4 words" and "about 3 words" as writing guidance. Rejected: word counts as
the check — a script without spaces has one word per line.

Amended 2026-10-02, after the references: an edge label may take a second line only for the
second writer of a state transition (`state.md` §4 rule 4). P9 of `paired-examples.md` names both
writers of S41, 38 characters in all, and passes every render check in two lines. A flowchart
edge label keeps one line as writing guidance; the lint checks 2.

**D26, 2026-10-02, orchestrator: amendments measured while the references were written.**

| Change | Measurement |
| :--- | :--- |
| Sequence participants 6 soft, 6 hard | 7 participants measure 1450 px: 9.9 px text in a 900 px column |
| Sequence message 24 characters per line | with `wrap`: 26 characters touch one lifeline, 27–32 cross both |
| Participant name 18 characters | `wrap` breaks a name wider than 150 px inside a word |
| Fixed light note colours in the sequence line | the dark theme's note text measures 4.44:1 |
| Gantt `useWidth` 900 and a `themeCSS` rule | labels outside done and active bars measure 1.1–1.2:1 on the dark page |
| Contrast judged on figure-set colours only | the dark theme's own edge labels measure 4.43:1 in every figure |
| Bundle limit 16,000 words | the flowchart bundle measures 14,557 words |

Rejected: a translucent `edgeLabelBackground` — in 10.9.8 the edge line then shows through the
label text.

**D27, 2026-10-03, orchestrator: amendments from code review round 1.** The campaign had finished
its runs; nothing was graded yet. Report: `docs/reviews/task-108-code-review-r1.md`.

| Change | Finding |
| :--- | :--- |
| The browser resolves no host name, localhost included; no proxy; a pipe, not a DevTools port (R7.9) | SEC-01, SEC-11 |
| Legibility gates the smallest text a reader must read, not the most common size (R7.6) | RG-02 |
| No mermaid fence: not rendered, exit 2; an unmodelled kind: `pass, geometry not checked` (R7.7) | RG-01, RG-03 |
| A negative marker counts only in the skill's `references/` and test fixtures, for the rules it names | LM-20, STI-01 |
| Split charts store their stage groups in the region; a damaged region is refused (R8.4, R8.6) | PC-01, PC-02 |
| A13 states the D18 projection rule, not a hard spend bound | SEC-12 |
| Hard budgets a passing render reaches: sequence participants 6, timeline periods 5, journey tasks 5 | STI-29 |
| `pie`, `xychart-beta` and `sankey-beta` move to the kinds to avoid (R4.6): their fills merge into the page | STI-30 |
| ASCII covers the five patterns of `ascii.md` §2 (R2.5) | STI-42 |
| Grader fixes are instrument fixes under D8 and use no revision round | EI-01 to EI-30 |

The keys stay as registered. Key defects the review found (EI-02, EI-08, EI-09, EI-27) are graded
apart, as amendment `a1` (`evals/AMENDMENTS.md`). That analysis is post-hoc: the reviewers had seen
per-case scores. The decision rule is evaluated on the registered keys.

**D28, 2026-10-03, operator: no revision round.** Under D8 the campaign is invalid: V2 is not
met, so the effect criteria decide nothing. The effect numbers are reported for information:
Δ_H 0.084 [0.035, 0.129], with the `without_skill` arm at H 0.883. Near that ceiling no revision
can reach H1 (0.25) or H2 (0.15), and three cases tie at 1.0, so H3 cannot reach 8 of 10. The
round D18 allows is not run; the remaining budget is not spent.

UC-5 A2 asks for the instrument to be fixed and the campaign graded again. That was done for the
three detector defects the calibration exposed. The two V2 failures that remain hold one positive
each, and neither comes from the detector: one is a rubric wording that D26 overrules, one is the
C0 key defect (EI-02). No instrument change can remove them, so the campaign stays invalid. The
next campaign is work-item WI-26: large cases, a tool-loop arm, more positives per defect type.

## 8. Review findings and their resolution

The two `task-reviewer` reports are kept in `docs/reviews/task-108-review-r1.md` and
`docs/reviews/task-108-review-r2.md`.

| Finding | Resolution |
| :--- | :--- |
| r1 B1 writes outside the repo; commit | §3 Deviation, D17; R11.10 hashes instead of a commit |
| r1 B2 plan input keyed on prose | R8.1, D19; R8.7 Russian twin |
| r1 M1 headline measures conventions | R11.7, R11.8; colour in the headline; C4 is a calendar gantt |
| r1 M2 no failure path, no budget | D8, D18, A13, UC-5 A2–A4 |
| r1 M3 calibration and provenance | D16, R11.12, UC-5 step 3, V2 |
| r1 M4 planarity bound misses `K3,3` | D21 |
| r1 M5 numbers contradict D14 | R2.5, R3.2, R4.5 cite D14 |
| r1 M6 dark render optional | R7.4, R7.6, D4 |
| r1 M7 render evidence stalls reviews | D24, R10.4, UC-4 |
| r1 M8 integration gaps | R10.3, R10.6, R10.7, R10.8, D2 |
| r1 M9 no non-functional requirements | §3 |
| r1 M10 use cases incomplete | UC-1 A3–A4, UC-2 A3–A4, UC-3, UC-4, UC-5, UC-6 |
| r1 M11 criteria do not trace | RTM column; A3, A5, A9, A17–A19 |
| r1 M12 rule list checked against itself | R6.6 |
| r1 M13 CI scope of the lint | R6.7, D6 |
| r1 M14 skill-creator tooling | D22, R12.3 |
| r1 M15 one run or three | D23 |
| r1 m1–m23 | rows r2 MINOR-1 to MINOR-18 below re-checked them |
| r2 MAJOR-1 licence narrower than the run | §3 Deviation, D17 (confirmed by the operator) |
| r2 MAJOR-2 revision round, Δ_H undefined | D8 scores and validity criteria; UC-5 A2 |
| r2 MAJOR-3 budget measure and stop rule | D18; UC-5 A4; A7 |
| r2 MAJOR-4 calibration procedure | UC-5 step 3; D16 |
| r2 MAJOR-5 dark render in name only | R7.4–R7.6, D4, R11.5, R11.7 |
| r2 MAJOR-6 every `text` fence a figure | R2.5, R2.7, R6.1 |
| r2 MAJOR-7 caption position undefined | R3.7, R11.7, R11.8 |
| r2 MAJOR-8 geometry not bound to its figure | R7.8, R9.5, A3, A19 |
| r2 MAJOR-9 message and note units | D25, R6.3 |
| r2 MAJOR-10 `--check` permission | R8.4, R6, R10.6, D9 |
| r2 MAJOR-11 form-case bundles | R1.4, R11.2, R11.3 |
| r2 MAJOR-12 R7 untested | A17, A18, A19, A12 |
| r2 MAJOR-13 failing render path | UC-1 A4 and step 6 |
| r2 MINOR-1 figure scope | §1 |
| r2 MINOR-2 quote not verbatim | R10.3 |
| r2 MINOR-3 exit-code wording | D20 |
| r2 MINOR-4 undefined lint rules | R3.3, R3.4, D21, D25, R7.5 |
| r2 MINOR-5 plan generator wording | R8.1, R8.4, R8.5, R8.7 |
| r2 MINOR-6 render environment | R7.3, R7.5, R7.8, R7.10 |
| r2 MINOR-7 environment and effort | R11.4 |
| r2 MINOR-8 C0 and naming | R11.1, D8 |
| r2 MINOR-9 hashes recorded first | R11.10 |
| r2 MINOR-10 routing table by header | R1.4, R10.2 |
| r2 MINOR-11 bundle size untested | R1.5 |
| r2 MINOR-12 rule ids one way | R6.6 |
| r2 MINOR-13 forbidden values | R10.10, R12.2 |
| r2 MINOR-14 use-case verdicts | UC-4 A1, UC-6 A1 |
| r2 MINOR-15 minor findings unmapped | this table; both reports kept |
| r2 MINOR-16 assumptions, performance | §3, R6.8 |
| r2 MINOR-17 10.9.3 claim | R5 |
| r2 MINOR-18 F1 and D2 | R11.13 |

## 9. Out of scope

| Excluded | Carried by |
| :--- | :--- |
| Redrawing the seven figures of §1 | WI-21 (UC-6 applies when their sections change) |
| Figures in `docs/presentation/`, `docs/design/` and `Backlog/` | outside the §1 scope |
| Universal-skills symlinks, consumer `install.py update`, `brainstorming` re-sync | operator, after the commit |
| `wiki-import` and the meeting-summary workflow rules | WI-24 |
| Plan status tokens and develop-workflow updates | WI-22 (D11) |
| Tool-loop eval variant, natural cases, ASCII inside documents | WI-23 (`evals-v2.json`) |
| Trigger evaluation of the description | WI-25 |
| GitLab self-managed 16.11–18.10, which runs mermaid 10.7.0 | unsupported floor, stated in `renderer-facts.md` |
| Slides, image exports, `skill-product-solution-blueprint` UX flows | unchanged |
| Any edit to `docs/tasks/`, `docs/plans/` or ledger record bodies | ARCHITECTURE §7.2, immutable |
