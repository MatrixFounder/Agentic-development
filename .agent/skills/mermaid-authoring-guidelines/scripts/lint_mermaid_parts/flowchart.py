"""FLOW rules of the figure lint: flowchart structure (TASK 126)."""

from __future__ import annotations

import re
from typing import Callable

import mermaid_model as mm
import planarity

from .base import rule, _doc, _hazard_check, _fig_line
from .budget import _chain


def _visible_edges(fc) -> list:
    return [e for e in fc.edges if e.style != "invisible"]


def _decision_flow(fc) -> bool:
    """A flowchart that holds a rhombus (decision) node: it may hold one edge per direction."""
    return any(n.shape == "rhombus" for n in fc.nodes.values())


def _edge_directions(e) -> set:
    """The ordered pairs an edge claims: one for an arrow, both for `<-->` and an open link."""
    return {(e.src, e.dst)} if e.arrow == "->" else {(e.src, e.dst), (e.dst, e.src)}


@rule("MA-FLOW-01", "warn", "More than one edge between one pair of nodes",
      "Merge parallel relations into one label (`claim · finish`), or one two-headed edge; a "
      "decision flow may hold one edge per direction.",
      _doc("flowchart TB\n  A --> B\n  B --> A"),
      _doc("flowchart TB\n  A <--> B"))
def _check_duplicate_edges(fig, ctx):
    """TASK R3.3: at most one edge per unordered node pair; in a flowchart that holds a rhombus
    node, at most one edge per direction."""
    if fig.flowchart is None:
        return []
    per_direction = _decision_flow(fig.flowchart)
    seen: dict = {}  # unordered pair -> [claimed ordered pairs, first line]
    out = []
    for e in _visible_edges(fig.flowchart):
        key = frozenset((e.src, e.dst))
        dirs = _edge_directions(e)
        if key not in seen:
            seen[key] = [set(dirs), e.line]
            continue
        claimed, first = seen[key]
        if per_direction and not dirs & claimed:
            claimed |= dirs
            continue
        where = " in this direction" if per_direction else ""
        out.append((e.line, f"`{e.src}` and `{e.dst}` are already joined{where} at line {first}"))
    return out


@rule("MA-FLOW-02", "error", "Edge to a subgraph id",
      "Draw the node-to-node edges the text states; mermaid ends a subgraph edge on the box "
      "border, and a reader takes it for a relation of the member nearest that end.",
      _doc('flowchart TB\n  subgraph S["Group"]\n    A\n    B\n  end\n  C --> S'),
      _doc('flowchart TB\n  subgraph S["Group"]\n    A\n    B\n  end\n  C --> A'))
def _check_subgraph_edge(fig, ctx):
    fc = fig.flowchart
    if fc is None:
        return []
    return [(e.line, f"`{e.src} --> {e.dst}` ends on subgraph `{x}`")
            for e in fc.edges for x in (e.src, e.dst) if x in fc.subgraphs]


@rule("MA-FLOW-03", "warn", "Subgraph with fewer than two members",
      "Drop the subgraph and put its role on the node's second line.",
      _doc('flowchart TB\n  subgraph S["Group"]\n    A\n  end\n  B --> A'),
      _doc('flowchart TB\n  subgraph S["Group"]\n    A\n    C\n  end\n  B --> A'))
def _check_small_subgraph(fig, ctx):
    fc = fig.flowchart
    if fc is None:
        return []
    return [(s.line, f"subgraph `{s.title or s.id}` holds {len(s.members)} member(s)")
            for s in fc.subgraphs.values() if len(s.members) < 2]


_NUMBERED = re.compile(r"^\s*[(\[]?\d{1,3}[.):\]](?!\d)")


def _numbered_probe(fire: bool) -> Callable:
    def make(notation):
        n = max(2, int(notation.get("lint", {}).get("numbered_edge_labels_min", 2)))
        lines = ["flowchart TB"]
        for k in range(1, n + 1):
            label = f"{k}. step" if fire else "step"
            lines.append(f'  N{k} -->|"{label}"| N{k + 1}')
        return _doc("\n".join(lines))
    return make


@rule("MA-FLOW-04", "warn", "Numbered edge labels: an order drawn in a structure figure",
      "Draw the order as a sequence diagram, or drop the numbers.",
      _numbered_probe(True), _numbered_probe(False))
def _check_numbered(fig, ctx):
    fc = fig.flowchart
    if fc is None:
        return []
    numbered = [e for e in fc.edges if _NUMBERED.match(" ".join(mm.label_lines(e.label)))]
    minimum = int(ctx.notation.get("lint", {}).get("numbered_edge_labels_min", 2))
    if len(numbered) >= minimum:
        return [(numbered[0].line, f"{len(numbered)} edge labels start with a number: "
                                   + ", ".join(f"`{e.label}`" for e in numbered[:4]))]
    return []


@rule("MA-FLOW-05", "warn", "Non-planar flowchart: every drawing has a crossing",
      "Aggregate one side (one node for the group), split the figure, or use a table.",
      _doc("flowchart TB\n  A1 --> B1 & B2 & B3\n  A2 --> B1 & B2 & B3\n  A3 --> B1 & B2 & B3"),
      _doc("flowchart TB\n  A1 --> B1 & B2 & B3\n  A2 --> B1 & B2\n  A3 --> B3"))
def _check_planarity(fig, ctx):
    fc = fig.flowchart
    if fc is None:
        return []
    hard_nodes = ctx.notation.get("budgets", {}).get("flowchart", {}).get("nodes", [0, 0])[1]
    hard_edges = ctx.notation.get("budgets", {}).get("flowchart", {}).get("edges", [0, 0])[1]
    edges = _visible_edges(fc)
    if len(fc.nodes) > hard_nodes or len(edges) > hard_edges:
        return []
    planar, reason = planarity.is_planar([(e.src, e.dst) for e in edges])
    if planar:
        return []
    return [(_fig_line(fig), f"the graph is not planar ({reason})")]


def _lr_probe(direction: str) -> Callable:
    def make(notation):
        n = int(notation.get("structure", {}).get("lr_max_nodes", 6)) + 1
        return _doc(_chain(n, direction))
    return make


@rule("MA-FLOW-06", "warn", "Flowchart over the node limit that is not laid out top to bottom",
      "Lay the figure out top to bottom (TASK R3.4); a wide LR figure shrinks its text in a 900 px "
      "column.",
      (_lr_probe("LR"), _lr_probe("BT")), _lr_probe("TB"))
def _check_lr(fig, ctx):
    fc = fig.flowchart
    if fc is None or fc.direction in ("TB", "TD"):
        return []
    limit = int(ctx.notation.get("structure", {}).get("lr_max_nodes", 6))
    if len(fc.nodes) > limit:
        return [(_fig_line(fig), f"{fc.direction} with {len(fc.nodes)} nodes > {limit}")]
    return []


rule("MA-FLOW-07", "warn", "`style` line that draws a node no other statement defines",
     "Fix the id in the `style` line, or drop the line; mermaid draws a box for any id a `style` "
     "line names.",
     _doc("flowchart TB\n  A --> B\n  style PHANTOM stroke:#546E7A"),
     _doc("flowchart TB\n  A --> B\n  style A stroke:#546E7A"))(
    _hazard_check("style-node"))

rule("MA-FLOW-08", "warn", "`linkStyle` in a flowchart",
     "Drop linkStyle (flowchart.md §2 rule 7): under `linkStyle default` 10.9.8 skips dotted and "
     "thick edges, while 12.1.0 styles every edge. Edge style and the legend carry the meaning.",
     _doc("flowchart TB\n  A --> B\n  linkStyle 0 stroke:#C62828"),
     _doc("flowchart TB\n  A ==> B"))(
    _hazard_check("linkstyle"))

rule("MA-FLOW-09", "warn", "`direction` inside a subgraph",
     "Drop the subgraph's `direction` (flowchart.md §4 rule 8): mermaid ignores it once a member "
     "links outside the subgraph.",
     _doc('flowchart TB\n  subgraph S["Group"]\n    direction LR\n    A --> B\n  end'),
     _doc('flowchart TB\n  subgraph S["Group"]\n    A --> B\n  end'))(
    _hazard_check("subgraph-direction"))


