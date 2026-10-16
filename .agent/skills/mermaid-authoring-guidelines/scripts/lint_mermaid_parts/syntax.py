"""SYN rules of the figure lint: what mermaid 10.9, the floor, cannot render (TASK 126)."""

from __future__ import annotations

from typing import Callable

from .base import rule, _doc, _hazard_check, _fig_line


rule("MA-SYN-01", "error", "`@{ }` shape or participant metadata (mermaid 11 only)",
     "Use the classic shapes: [( )] cylinder, ([ ]) stadium, [[ ]] subroutine; mermaid 10.9 rejects @{ }.",
     _doc('flowchart TB\n  A@{ shape: cyl, label: "x" } --> B'),
     _doc('flowchart TB\n  A[("x")] --> B'))(
    _hazard_check("shape-at"))

rule("MA-SYN-02", "error", "Edge id or edge animation (mermaid 11.5+)",
     "Drop the edge id; mermaid 10.9 rejects `e1@-->` and `animate`.",
     _doc("flowchart TB\n  A e1@--> B"),
     _doc("flowchart TB\n  A --> B"))(
    _hazard_check("edge-id", "animate"))


def _unsupported_kinds(notation: dict) -> list:
    return list(notation.get("lint", {}).get("unsupported_v10_kinds", []))


def _avoid_only_kinds(notation: dict) -> list:
    bad = set(_unsupported_kinds(notation))
    return [k for k in notation.get("kinds", {}).get("avoid", []) if k not in bad]


def _kind_probe(pick: Callable) -> Callable:
    def make(notation):
        kinds = pick(notation)
        keyword = kinds[0] if kinds else "flowchart"
        return _doc(f"{keyword}\n  a")
    return make


@rule("MA-SYN-03", "error", "Diagram kind that mermaid 10.9 cannot render",
      "Use a kind of notation.json `kinds.preferred` or `kinds.allowed`, or a table.",
      _kind_probe(_unsupported_kinds),
      _doc("flowchart TB\n  A --> B"))
def _check_kind_floor(fig, ctx):
    if fig.kind == "ascii":
        return []
    if fig.keyword in _unsupported_kinds(ctx.notation):
        return [(_fig_line(fig), f"`{fig.keyword}` needs mermaid 11 or newer")]
    return []


@rule("MA-SYN-04", "warn", "Diagram kind the skill avoids",
      "Use a kind of notation.json `kinds.preferred` or `kinds.allowed`, or a table.",
      _kind_probe(_avoid_only_kinds),
      _doc("flowchart TB\n  A --> B"))
def _check_kind_avoid(fig, ctx):
    if fig.kind != "ascii" and fig.keyword in _avoid_only_kinds(ctx.notation):
        return [(_fig_line(fig), f"`{fig.keyword}` is in notation.json `kinds.avoid`")]
    return []


rule("MA-SYN-05", "error", "Gantt `vert` marker (mermaid 10.9 stops the render)",
     "Drop the vertical marker; state the date in the text or a milestone.",
     _doc("gantt\n  dateFormat x\n  axisFormat %Q\n  todayMarker off\n  section S\n  t1 :a, 0, 3ms\n"
          "  marker :vert, v1, 2, 0ms"),
     _doc("gantt\n  dateFormat x\n  axisFormat %Q\n  todayMarker off\n  section S\n  t1 :a, 0, 3ms"))(
    _hazard_check("gantt-vert"))

rule("MA-SYN-06", "error", "Sequence syntax above the 10.9 floor",
     "Use the classic arrows and an integer `autonumber`; draw `A<<->>B` as two messages.",
     _doc("sequenceDiagram\n  participant A\n  participant B\n  autonumber 1.1 0.1\n  A->>B: x"),
     _doc("sequenceDiagram\n  participant A\n  participant B\n  autonumber\n  A->>B: x"))(
    _hazard_check("seq-syntax-above-floor"))


@rule("MA-SYN-07", "error", "Unknown diagram keyword, or no diagram in the fence",
      "Start the fence with a diagram keyword: flowchart, sequenceDiagram, stateDiagram-v2, gantt, "
      "erDiagram.",
      (_doc("foobar\n  a --> b"), _doc("%% only a comment")),
      _doc("flowchart TB\n  A --> B"))
def _check_unknown(fig, ctx):
    if fig.kind != "unknown":
        return []
    if fig.keyword:
        return [(_fig_line(fig), f"`{fig.keyword}` is not a diagram keyword of mermaid 10.9–12.1")]
    # an empty fence, or one with only comments or settings: every viewer shows an error box
    return [(_fig_line(fig), "the fence holds no diagram keyword; mermaid detects no diagram")]


rule("MA-SYN-08", "error", "Styling that mermaid 10.9 rejects in an ER, class or requirement diagram",
     "Drop classDef, class, style and ::: from ER and requirement diagrams, and classDef from class "
     "diagrams; a table or the legend carries the category.",
     _doc("erDiagram\n  CUSTOMER ||--o{ ORDER : places\n  classDef hot fill:#FFF4E0,color:#4A2C00"),
     _doc("erDiagram\n  CUSTOMER ||--o{ ORDER : places"))(
    _hazard_check("styling-v10"))

rule("MA-SYN-09", "error", "Text after `timeline` on its header line",
     "Write `timeline` alone on its line; mermaid 10.9 draws the text as a first period, and 11.17 "
     "reads `TD` as a direction.",
     _doc("timeline TD\n  2025 Q1 : v1 search"),
     _doc("timeline\n  2025 Q1 : v1 search"))(
    _hazard_check("timeline-header"))


