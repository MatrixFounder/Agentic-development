---
id: WI-53
type: work-item
status: done
opened_at: 2026-10-14
slug: wi-53-mermaid-html-labels-are-cut-on-github
effort: M
value: 'a figure that passes the render check is not cut on GitHub'
source: 'the operator, n8n-lazy-loading-skills, 2026-10-14'
component: '.claude/skills/mermaid-authoring-guidelines'
resolved_at: 2026-10-14
resolved_by: 'TASK 121'
---

# WI-53 — Mermaid's HTML labels are cut on GitHub, and the render check cannot see it

> **Done 2026-10-14 (TASK 121).** The proposal, widened to every kind that draws HTML labels in
> 11.17.2 (TASK D1, D2). The settings lines of flowchart, state, ER, class and requirement carry
> `"themeCSS": "foreignObject { overflow: visible; }"`, and mindmap has a line of its own. A node's
> second line is plain text after `<br/>`; MA-LABEL-14 warns on `<small>`, and MA-SET-06 on a line
> without the pinned `themeCSS`. `render_check.py` redraws the 11.17.2 renders with the stylesheet
> of `renderers.font_swap`, and its check `font_swap` fails a label that the swap hides or pushes
> past its node's border. The references, the eval fixtures and two figures of `System/Docs` follow;
> `renderer-facts.md` RF-23 records the facts. The committed eval campaign is graded under the
> notation it ran with (TASK D8).

**Seen.** On GitHub's web view, every flowchart and state figure of the n8n-lazy-loading-skills documents had labels
cut at the right edge of their boxes ("the delivery runne", "Execute Workflow Tri"). The same figures were whole in
VS Code, and all passed `render_check.py` in 11.17.2, 10.9.8 and dark. Sequence figures were not affected.

**Cause, reproduced.** In headless Chrome with the pinned 11.17.2, the screenshot repeats exactly:
- Mermaid measures each HTML label once, in its own font (Trebuchet MS, 16 px, a `<small>` second line smaller),
  and fixes the label's `foreignObject` to that size.
- GitHub then shows the labels in its own font, with `<small>` at full size. The text grows wider than the box, and
  the `foreignObject` clips it.
- The render check draws on a clean page, where nothing changes the font after the drawing, so it cannot see this.
- A stylesheet present before the drawing clips nothing, so the defect is the font change after it.
- Sequence figures draw SVG text, which nothing clips.

**What was tried, measured under a GitHub-like font swap after the drawing** (13 figures):
- as now: 2 to 27 hidden labels per figure;
- `htmlLabels: false` (SVG text): nothing hidden, but in 11.17 the state figures' transition labels overlap, and
  subgraph titles fall to 1.01:1 contrast in dark: rejected by the operator;
- more `flowchart.padding`: no change, since the label's box is the text's measured width;
- no `<small>` only: still clipped, by less;
- `themeCSS` `foreignObject { overflow: visible; }` only: nothing hidden, but text crosses its node's right border;
- **both, overflow visible and no `<small>`: nothing hidden, nothing crosses a border**, and the render check still
  passes. On GitHub itself, a temporary branch showed the four variants, and the operator confirmed this one renders
  whole (2026-10-14).

**Applied in that project** (commit `2edd8da`): 15 figures, with lint 0 errors, so the current lint accepts the
added `themeCSS`.

**Proposed for the skill.**
- `assets/notation.json`: the `flowchart` and `state` settings lines gain
  `"themeCSS": "foreignObject { overflow: visible; }"`; the references quote the new lines.
- `references/flowchart.md`, `state.md`, `paired-examples.md`: a node's second line is plain text after `<br/>`, never
  `<small>`, and its 40-character limit is counted at full size. The lint warns on `<small>` in a flowchart or state
  label.
- `scripts/render_check.py`: a GitHub font-swap probe. Draw, apply a system-font stylesheet with `small { font-size:
  inherit }`, and fail a figure whose label text is hidden (`foreignObject` not `overflow: visible` and narrower than
  its text) or crosses its node's shape. Pin it with a fixture of the old form (fails) and the new form (passes).
- `SKILL.md` Red Flags: "It renders in my preview" names GitHub's font swap too.
