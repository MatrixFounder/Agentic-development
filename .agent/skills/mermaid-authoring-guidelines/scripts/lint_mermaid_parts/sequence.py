"""SEQ rules of the figure lint (TASK 126)."""

from __future__ import annotations

from typing import Callable

import mermaid_model as mm

from .base import rule, _doc, _hazard_check


rule("MA-SEQ-01", "error", "classDef, class or style in a sequence diagram",
     "Sequence diagrams take no classes; use box and rect, or nothing.",
     _doc("sequenceDiagram\n  participant A\n  A->>A: x\n  classDef c fill:#FFFFFF"),
     _doc("sequenceDiagram\n  participant A\n  A->>A: x"))(
    _hazard_check("seq-styling"))


def _skip_probe(fire: bool) -> Callable:
    def make(notation):
        n = int(notation["labels"]["edge_label_chars_max"]) + 1
        label = "x" * n
        target = "C" if fire else "B"
        return _doc("sequenceDiagram\n  participant A\n  participant B\n  participant C\n"
                    f"  A->>{target}: {label}")
    return make


@rule("MA-SEQ-02", "warn", "Long label on a message that passes a lifeline",
      "Order participants so the pair is adjacent, or shorten the label to an edge label's length.",
      _skip_probe(True), _skip_probe(False))
def _check_skip(fig, ctx):
    seq = fig.sequence
    if seq is None:
        return []
    limit = int(ctx.notation["labels"]["edge_label_chars_max"])
    pos = {p.id: k for k, p in enumerate(seq.participants)}
    out = []
    for m in seq.messages:
        if m.src not in pos or m.dst not in pos:
            continue
        passed = abs(pos[m.src] - pos[m.dst]) - 1
        longest = max((mm.char_count(x) for x in mm.label_lines(m.text)), default=0)
        if passed >= 1 and longest > limit:
            out.append((m.line, f"`{m.src}->{m.dst}` passes {passed} lifeline(s) with a "
                                f"{longest}-character label (limit {limit})"))
    return out


def _phase_probe(fire: bool) -> Callable:
    def make(notation):
        colour = "#E8F0FB" if fire else notation["palette"]["sequence"]["phase"]
        return _doc(f"sequenceDiagram\n  participant A\n  participant B\n  rect {colour}\n    A->>B: x\n  end")
    return make


rule("MA-SEQ-03", "error", "Hex colour after `rect` or `box` in a sequence diagram",
     "Write the colour as rgba(), from notation.json palette.sequence (`box`, `phase`).",
     _phase_probe(True), _phase_probe(False))(
    _hazard_check("seq-hex-colour"))


