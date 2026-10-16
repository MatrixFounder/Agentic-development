"""STATE rules of the figure lint (TASK 126)."""

from __future__ import annotations

from typing import Optional

from .base import rule, _doc, _hazard_check


@rule("MA-STATE-01", "error", "Transition across a composite state boundary",
      "Use a flat graph with classes, or attach the transition to the composite itself.",
      _doc("stateDiagram-v2\n  state W {\n    x --> y\n  }\n  a --> x"),
      _doc("stateDiagram-v2\n  state W {\n    x --> y\n  }\n  a --> W"))
def _check_composite_cross(fig, ctx):
    sd = fig.state
    if sd is None:
        return []
    out = []
    for t in sd.transitions:
        if "[*]" in (t.src, t.dst) or t.src not in sd.states or t.dst not in sd.states:
            continue
        ps, pd = sd.states[t.src].parent, sd.states[t.dst].parent
        if ps != pd:
            inner = [p for p in (ps, pd) if p]
            out.append((t.line, f"`{t.src} --> {t.dst}` crosses the boundary of "
                                + " and ".join(f"`{p}`" for p in inner)))
    return out


rule("MA-STATE-02", "error", "`style` in a state diagram",
     "Use classDef and class; mermaid 10.9 rejects `style` or turns it into stray states.",
     _doc("stateDiagram-v2\n  a --> b\n  style a fill:#FFFFFF"),
     _doc("stateDiagram-v2\n  a --> b\n  classDef c fill:#FFFFFF,color:#263238\n  class a c"))(
    _hazard_check("state-style"))


def _state_end(sid: str, scope: Optional[str], role: str) -> str:
    """A transition end as a node: `[*]` is a start or an end node of its composite."""
    return f"[*] {role} {scope or ''}" if sid == "[*]" else sid


@rule("MA-STATE-03", "warn", "Two transitions in one direction between one pair of states",
      "Merge them into one label (`claim · finish`); a state diagram holds one transition per "
      "direction (TASK R3.3).",
      _doc("stateDiagram-v2\n  a --> b : go\n  a --> b : retry"),
      _doc("stateDiagram-v2\n  a --> b : go\n  b --> a : back"))
def _check_duplicate_transitions(fig, ctx):
    sd = fig.state
    if sd is None:
        return []
    seen: dict = {}
    out = []
    for t in sd.transitions:
        key = (_state_end(t.src, t.scope, "start"), _state_end(t.dst, t.scope, "end"))
        if key in seen:
            out.append((t.line, f"`{t.src} --> {t.dst}` repeats the transition at line {seen[key]}"))
        else:
            seen[key] = t.line
    return out


rule("MA-STATE-04", "warn", "Quotes around a state transition label or description",
     "Drop the quotes: mermaid prints them. Quotes belong only in `state \"name\" as id`.",
     _doc('stateDiagram-v2\n  a --> b : "go now"'),
     _doc("stateDiagram-v2\n  a --> b : go now"))(
    _hazard_check("state-label-quoted"))


