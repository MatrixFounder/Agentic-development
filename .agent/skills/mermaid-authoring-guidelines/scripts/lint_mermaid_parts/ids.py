"""ID rules of the figure lint: node and edge ids (TASK 126)."""

from __future__ import annotations

import re

import mermaid_model as mm

from .base import rule, _doc


@rule("MA-ID-01", "error", "Two edges that mermaid 12 gives one edge id (it stops the render)",
      "Rename the ids without `_`: `a --> b_c` and `a_b --> c` both become L_a_b_c_0.",
      _doc("flowchart TB\n  a --> b_c\n  a_b --> c"),
      _doc("flowchart TB\n  a --> bc\n  ab --> c"))
def _check_edge_ids(fig, ctx):
    fc = fig.flowchart
    if fc is None:
        return []
    seen: dict = {}
    out = []
    for edge, eid in zip(fc.edges, mm.flowchart_edge_ids(fc)):
        prev = seen.get(eid)
        if prev is not None and (prev.src, prev.dst) != (edge.src, edge.dst):
            out.append((edge.line, f"`{prev.src} --> {prev.dst}` and `{edge.src} --> {edge.dst}` "
                                   f"share the edge id {eid}"))
        else:
            seen.setdefault(eid, edge)
    return out


def _figure_ids(fig) -> list:
    """(id, line) of every id the author wrote."""
    out = []
    if fig.flowchart:
        out += [(n.id, n.line) for n in fig.flowchart.nodes.values()]
        out += [(s.id, s.line) for s in fig.flowchart.subgraphs.values() if not s.auto_id]
    if fig.state:
        out += [(s.id, s.line) for s in fig.state.states.values()]
    if fig.sequence:
        out += [(p.id, p.line) for p in fig.sequence.participants]
    if fig.gantt:
        out += [(t.id, t.line) for t in fig.gantt.tasks if t.id]
    return out


@rule("MA-ID-02", "warn", "Id outside [A-Za-z0-9]",
      "Use letters and digits for ids and put the name in the label: apiGw[\"api-gw\"].",
      _doc("flowchart TB\n  api-gw --> db"),
      _doc("flowchart TB\n  apiGw --> db"))
def _check_id_shape(fig, ctx):
    pattern = re.compile(ctx.notation.get("lint", {}).get("id_pattern", r"^[A-Za-z0-9]+$"))
    out, seen = [], set()
    for ident, line in _figure_ids(fig):
        if ident not in seen and not pattern.match(ident):
            seen.add(ident)
            out.append((line, f"id `{ident}`"))
    return out


