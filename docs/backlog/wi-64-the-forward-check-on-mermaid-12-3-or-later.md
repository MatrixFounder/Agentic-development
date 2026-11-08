---
id: WI-64
type: work-item
status: open
opened_at: 2026-11-08
slug: wi-64-the-forward-check-on-mermaid-12-3-or-later
effort: L
value: 'the forward check shows what the next mermaid release changes'
source: 'TASK 144, D2 and D3'
component: '.agent/skills/mermaid-authoring-guidelines'
---

# WI-64 — The forward check on mermaid 12.3 or later

**Signal.** The forward check (`render_check.py --forward`, tag `v12`) renders with mermaid
12.1.0. On 2026-11-08 the latest release is 12.3.0, and 13.0.0-alpha.1 is published. TASK 144
kept 12.1.0 with mermaid-cli 12.2.0 (D2): mermaid 12.2.0 and 12.3.0 change the layout engine.

**What changes.** The release notes of 12.2.0 and 12.3.0 list, among others:

- the bundled elkjs moves from 0.9.3 to 0.12.0 (#8532), and ELK routes edges differently (#8395,
  #8661);
- an edge label no longer moves the nodes it joins a rank apart (#8385);
- a circle node takes its size from its label (#8409);
- the legacy ER renderer is removed (#8633);
- new syntax: the edge `step` (#8470), two edge markers (#8164), BPMN shapes (#8165).

**What needs a new measurement.** Each file of the skill with a line that names 12.1.0, by
`git grep -c '12\.1\.0'` on 2026-11-08, the lockfile and campaign `2026-10-opus55-xhigh-r1` aside:

- `references/`: `renderer-facts.md` 54 lines, `sequence.md` 6, `other-kinds.md` 6,
  `layout-and-planarity.md` 4, `state.md` 3, `gantt.md` 3, `review-checklist.md` 2,
  `flowchart.md` 1;
- `scripts/mermaid_model/`: `hazards.py` 2, `__init__.py` 1, `er.py` 1, `flowchart.py` 1; they
  name the constructs that each pinned renderer rejects or draws;
- `scripts/lint_mermaid_parts/flowchart.py` 1: `12.1.0 styles every edge`;
- `scripts/plan_gantt.py` 2: the lexers and the directive sanitizer, read in the 12.1.0 bundle;
- `scripts/svg_geometry.py` 1: the SVG anatomy, measured on 12.1.0;
- `scripts/render_check.py` 2, `scripts/setup_renderers.sh` 2, `assets/notation.json` 1, the v12
  manifest 3;
- `evals/`: `render_corpus.py` 3, `README.md` 2, `grade_figures.py` 1;
- `scripts/tests/`: `test_lint_mermaid.py` 1, `test_render_check.py` 1, `test_svg_geometry.py` 1.

`evals/evals.json` and `evals/fixtures/c4-reporting-migration-gantt/key.json` also name 12.1.0.
They are records of the campaign and stay.

The test fixtures need no change: they hold renders of v10, v11 and v11 dark only. The base
in 12.1.0 needs no stored copy: the v12 pin reproduces it until the move.

**Start condition.** The move starts when one of these holds:

1. GitHub or VS Code runs mermaid 12. The check pair then moves to 12 and the forward check to
   13; this item becomes part of that move.
2. mermaid 13.0.0 has been released for 14 days. The forward check then moves to 13, and 12.3
   is skipped.
3. The v12 pin is 3 or more minor releases behind the latest 12.x release. The target is the
   newest 12.x minor released 14 days or more before the start.

Before the start, the upstream issues that name the target version are read. An open
regression in a kind that a reference figure uses moves the target to the next minor.

**Why 14 days.** The npm release dates of mermaid 11.8.0 to 12.3.0, read 2026-11-08:

- a regression patch followed its minor by 3 to 6 days: 11.8.1 (+4 d), 11.10.1 (+3 d),
  11.17.1 (+5 d), 11.17.2 (+6 d);
- every later patch came 39 days or more after its minor;
- no 12.x minor has a patch release; a 12.x minor stood 10 to 22 days before the next one.

⇒ On 12.x a fix arrives in the next minor, so a count of patch releases is no signal. 14 days
is more than twice the longest patch delay observed, 6 days.

**Check.** `npm view mermaid dist-tags time --json` gives the releases and their dates.
`gh search issues --repo mermaid-js/mermaid "<version>"` gives the reports that name a version.
On 2026-11-08 they included:

- #8692: sequence shadows use unscoped ids in 12.3.0;
- #8580: ELK edge labels of bidirectional edges overlap since 12.1.0;
- #8674: the ELK layout of a mindmap is broken.

**Upkeep.** Someone runs the check by hand, when the skill is next changed. No job runs it.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | At the start condition, one task: compare the 12.1.0 and target renders, measure each fact again | L | facts, lint rules and hazards may change |
| 2 | A scheduled job that reports the lag of the v12 pin | S | one more job, with network access |
| 3 | Do nothing | — | the forward preview ages; it sets no exit code |

**Recommendation.** Option 1 at the start condition. Option 2 only if the check by hand is missed.

**Acceptance.** The forward check renders the target version. Each fact that named 12.1.0 names
the version it was measured in. The base and the target renders are compared figure by figure,
and the tests of the skill pass.
