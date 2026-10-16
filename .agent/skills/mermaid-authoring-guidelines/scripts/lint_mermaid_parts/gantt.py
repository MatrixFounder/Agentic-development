"""GANTT rules of the figure lint (TASK 126)."""

from __future__ import annotations

import re

import mermaid_model as mm

from .base import rule, _doc, _hazard_check, _fig_line


_GANTT_HEAD = "gantt\n  dateFormat x\n  axisFormat %Q\n  todayMarker off\n"


@rule("MA-GANTT-01", "error", "`after` or `until` names a task declared below or never declared",
      "Declare a task before every task that names it, or generate the chart with plan_gantt.py.",
      _doc(_GANTT_HEAD + "  section S\n  first :a, 0, 3ms\n  second :b, after c, 2ms\n  third :c, 0, 4ms"),
      _doc(_GANTT_HEAD + "  section S\n  first :a, 0, 3ms\n  third :c, 0, 4ms\n  second :b, after c, 2ms"))
def _check_after(fig, ctx):
    g = fig.gantt
    if g is None:
        return []
    first_line = {}
    for t in g.tasks:
        if t.id:
            first_line.setdefault(t.id, t.line)
    out = []
    for t in g.tasks:
        for ref in mm.gantt_refs(t):
            where = first_line.get(ref)
            if where is None:
                out.append((t.line, f"`{ref}` is not declared; mermaid starts the bar at today"))
            elif where > t.line:
                out.append((t.line, f"`{ref}` is declared below, at line {where}; mermaid drops "
                                    "the dependency"))
    return out


@rule("MA-GANTT-02", "error", "Dotted id in `after`",
      "Use ids without dots; mermaid does not resolve `after t1.1`.",
      _doc(_GANTT_HEAD + "  section S\n  first :t1.1, 0, 3ms\n  second :b, after t1.1, 2ms"),
      _doc(_GANTT_HEAD + "  section S\n  first :t11, 0, 3ms\n  second :b, after t11, 2ms"))
def _check_dotted_after(fig, ctx):
    if fig.gantt is None:
        return []
    return [(t.line, f"`{ref}`") for t in fig.gantt.tasks for ref in mm.gantt_refs(t) if "." in ref]


rule("MA-GANTT-03", "error", "Colon in a gantt task label",
     "Remove the colon from the label; it moves the task id into the data.",
     _doc(_GANTT_HEAD + "  section S\n  T2 Orders: logic :t2, 3, 4ms"),
     _doc(_GANTT_HEAD + "  section S\n  T2 Orders logic :t2, 3, 4ms"))(
    _hazard_check("gantt-label-colon"))


@rule("MA-GANTT-04", "error", "Repeated gantt section",
      "Keep each section contiguous: one section line per stage.",
      _doc(_GANTT_HEAD + "  section S1\n  t1 :a, 0, 3ms\n  section S2\n  t2 :b, 3, 3ms\n  section S1\n"
           "  t3 :c, 6, 3ms"),
      _doc(_GANTT_HEAD + "  section S1\n  t1 :a, 0, 3ms\n  t3 :c, 6, 3ms\n  section S2\n  t2 :b, 3, 3ms"))
def _check_repeated_section(fig, ctx):
    g = fig.gantt
    if g is None:
        return []
    seen: dict = {}
    out = []
    lines = g.section_lines or [_fig_line(fig)] * len(g.sections)
    for name, line in zip(g.sections, lines):
        if name in seen:
            out.append((line, f"section `{name}` also starts at line {seen[name]}"))
        else:
            seen[name] = line
    return out


@rule("MA-GANTT-05", "warn", "Millisecond axis format %L or %-L",
      "Use `axisFormat %Q`: %L restarts at every second, so ticks read 0 again.",
      _doc("gantt\n  dateFormat x\n  axisFormat %L\n  todayMarker off\n  section S\n  t1 :a, 0, 3ms"),
      _doc(_GANTT_HEAD + "  section S\n  t1 :a, 0, 3ms"))
def _check_axis(fig, ctx):
    g = fig.gantt
    if g is None or not re.search(r"%-?L", g.axis_format):
        return []
    line = next((s["line"] for s in g.statements if s["keyword"] == "axisFormat"), _fig_line(fig))
    return [(line, f"axisFormat {g.axis_format}")]


rule("MA-GANTT-06", "error", "`topAxis` statement",
     "Remove `topAxis`; it is a parse error in 10.9, 11.17 and 12.1.",
     _doc(_GANTT_HEAD + "  topAxis\n  section S\n  t1 :a, 0, 3ms"),
     _doc(_GANTT_HEAD + "  section S\n  t1 :a, 0, 3ms"))(
    _hazard_check("gantt-topaxis"))


@rule("MA-GANTT-07", "warn", "Gantt without `todayMarker off`",
      "Add `todayMarker off`; otherwise the chart changes as time passes.",
      _doc("gantt\n  dateFormat x\n  axisFormat %Q\n  section S\n  t1 :a, 0, 3ms"),
      _doc(_GANTT_HEAD + "  section S\n  t1 :a, 0, 3ms"))
def _check_today(fig, ctx):
    g = fig.gantt
    if g is None or g.today_marker.strip().lower() == "off":
        return []
    return [(_fig_line(fig), "no `todayMarker off`")]


@rule("MA-GANTT-08", "error", "Bare number as a duration under `dateFormat x`",
      "Write the unit: `3ms`; a bare number is an absolute end time, so the bar vanishes.",
      _doc(_GANTT_HEAD + "  section S\n  first :a, 0, 3ms\n  second :b, 3, 5"),
      _doc(_GANTT_HEAD + "  section S\n  first :a, 0, 3ms\n  second :b, 3, 5ms"))
def _check_bare_duration(fig, ctx):
    g = fig.gantt
    if g is None or g.date_format.strip() not in ("x", "X"):
        return []
    return [(t.line, f"`{t.duration}` in `{t.label}`") for t in g.tasks
            if re.fullmatch(r"\d+(\.\d+)?", t.duration.strip())]


