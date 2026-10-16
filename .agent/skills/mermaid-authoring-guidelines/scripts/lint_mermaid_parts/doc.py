"""DOC rules of the figure lint: caption, legend and one notation per document (TASK 126)."""

from __future__ import annotations

import json

import mermaid_model as mm

from .base import rule, _doc, _fig_line
from .classes import _class_defs


def _in_document(fig, ctx) -> bool:
    """True for a fence of a Markdown document; a `.mmd` file has no caption or legend."""
    return not ctx.is_mmd and fig.fence.start > 0


def _legend_reasons(fig, ctx) -> list:
    """The encodings that make a figure need a legend (TASK R3.7: two or more), per notation.json
    `lint` `legend_min_*`. In an ASCII figure, a fork and its join are the second encoding next
    to the links (ascii.md §4); a fan-out, a fork without a join, is none."""
    if fig.kind == "ascii":
        a = fig.ascii
        return ["a fork and a join"] if a is not None and a.forks and a.joins else []
    lint = ctx.notation.get("lint", {})
    classes, edge_styles, shapes = _legend_encodings(fig)
    reasons = []
    if len(classes) >= int(lint.get("legend_min_classes", 2)):
        reasons.append(f"{len(classes)} classes or styles")
    if len(edge_styles) >= int(lint.get("legend_min_edge_styles", 2)):
        reasons.append(f"{len(edge_styles)} edge styles")
    if len(shapes) >= int(lint.get("legend_min_shapes", 3)):
        reasons.append(f"{len(shapes)} node shapes")
    return reasons


@rule("MA-DOC-01", "warn", "Figure without a caption above the fence",
      "Put the caption in the paragraph directly above the fence; a heading is not a caption.",
      "## Heading\n\n```mermaid\nflowchart TB\n  A --> B\n```\n",
      _doc("flowchart TB\n  A --> B"))
def _check_caption(fig, ctx):
    """TASK R3.7: the caption is the paragraph directly above the fence. A figure whose only
    neighbour is a paragraph below, and which needs no legend, gets MA-DOC-05 instead."""
    if not _in_document(fig, ctx) or fig.fence.before is not None:
        return []
    if fig.fence.after is not None and not _legend_reasons(fig, ctx):
        return []
    return [(_fig_line(fig), "no paragraph directly above the fence")]


@rule("MA-DOC-05", "warn", "Caption below the fence",
      "Move the caption to the paragraph directly above the fence; the paragraph below is the legend.",
      "```mermaid\nflowchart TB\n  A --> B\n```\n\n**Figure 1.** Probe.\n",
      _doc("flowchart TB\n  A --> B"))
def _check_caption_below(fig, ctx):
    if not _in_document(fig, ctx) or fig.fence.before is not None or fig.fence.after is None:
        return []
    if _legend_reasons(fig, ctx):
        return []
    return [(_fig_line(fig), f"caption below the fence: the paragraph at line {fig.fence.after.start} "
                             "is the only one next to the fence")]


def _encodings(fig) -> tuple:
    """(classes, edge styles, node shapes) a figure uses."""
    classes, edge_styles, shapes = set(), set(), set()
    if fig.flowchart:
        fc = fig.flowchart
        for n in fc.nodes.values():
            classes.update(c for c in n.classes if c != "default")
            shapes.add(n.shape)
        for names in fc.subgraph_classes.values():
            classes.update(c for c in names if c != "default")
        classes.update(f"style:{s['raw']}" for s in fc.styles if s["target"] in fc.nodes)
        edge_styles.update(e.style for e in fc.edges if e.style != "invisible")
    if fig.state:
        for s in fig.state.states.values():
            classes.update(c for c in s.classes if c != "default")
        classes.update(f"style:{s['raw']}" for s in fig.state.styles)
    if fig.gantt:
        for t in fig.gantt.tasks:
            classes.update(tag for tag in t.tags if tag != "vert")
    return classes, edge_styles, shapes


def _legend_encodings(fig) -> tuple:
    """`_encodings` plus what the legend rule also counts: in a flowchart each `linkStyle`
    stroke, in a sequence each arrow kind (`->>` a call, `-->>` a reply: sequence.md §10) and
    each `rect` or `box` fill. `_encodings` stays as the eval grader reads it."""
    classes, edge_styles, shapes = _encodings(fig)
    if fig.flowchart:
        strokes = {mm._parse_props(s["raw"]).get("stroke", "") for s in fig.flowchart.link_styles
                   if s["index"] != "default"}
        edge_styles.update(f"linkStyle:{x}" for x in strokes if x)
    if fig.sequence:
        edge_styles.update(m.arrow for m in fig.sequence.messages)
        classes.update(f"{b.kind}:{b.colour}" for b in fig.sequence.blocks if b.colour)
    return classes, edge_styles, shapes


_TWO_CLASSES = ("flowchart TB\n  A:::x --> B:::y\n  classDef x fill:#FFFFFF,color:#263238\n"
                "  classDef y fill:#E8F0FB,color:#0F2A47")


@rule("MA-DOC-02", "warn", "Figure with two or more encodings and no legend below the fence",
      "Put the legend in the paragraph or list directly below the fence; name each class, edge "
      "style and shape the figure uses.",
      f"**Figure 1.** Probe.\n\n```mermaid\n{_TWO_CLASSES}\n```\n",
      _doc(_TWO_CLASSES))
def _check_legend(fig, ctx):
    """TASK R3.7: the legend is the paragraph or list directly below the fence."""
    if not _in_document(fig, ctx):
        return []
    reasons = _legend_reasons(fig, ctx)
    if reasons and fig.fence.after is None:
        return [(_fig_line(fig), "the figure uses " + ", ".join(reasons)
                 + " but no paragraph or list sits directly below the fence")]
    return []


@rule("MA-DOC-03", "warn", "One class name with different properties in two figures",
      "Use one class block for the whole document (TASK R3.8).",
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#FFFFFF,color:#263238") + "\n"
      + _doc("flowchart TB\n  C:::c --> D\n  classDef c fill:#E8F0FB,color:#0F2A47"),
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#FFFFFF,color:#263238") + "\n"
      + _doc("flowchart TB\n  C:::c --> D\n  classDef c fill:#FFFFFF,color:#263238"),
      scope="document")
def _check_class_consistency(figures, ctx):
    first: dict = {}
    out = []
    for fig in figures:
        for name, d in _class_defs(fig).items():
            props = json.dumps(d["props"], sort_keys=True)
            if name not in first:
                first[name] = (props, d["line"])
            elif props != first[name][0]:
                out.append((d["line"], f"classDef `{name}` differs from line {first[name][1]}"))
    return out


@rule("MA-DOC-04", "warn", "One participant with different names in two figures",
      "Give each participant one alias in the whole document (TASK R3.8).",
      _doc("sequenceDiagram\n  participant A as Api\n  A->>A: x") + "\n"
      + _doc("sequenceDiagram\n  participant A as Gateway\n  A->>A: y"),
      _doc("sequenceDiagram\n  participant A as Api\n  A->>A: x") + "\n"
      + _doc("sequenceDiagram\n  participant A as Api\n  A->>A: y"),
      scope="document")
def _check_alias_consistency(figures, ctx):
    first: dict = {}
    out = []
    for fig in figures:
        if fig.sequence is None:
            continue
        for p in fig.sequence.participants:
            if not p.declared:
                continue
            name = p.label or p.id
            if p.id not in first:
                first[p.id] = (name, p.line)
            elif name != first[p.id][0]:
                out.append((p.line, f"`{p.id}` is `{name}` here and `{first[p.id][0]}` at line {first[p.id][1]}"))
    return out


