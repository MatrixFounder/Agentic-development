"""Gantt parser of the parse model (TASK 124)."""

from __future__ import annotations

import re

from .figure import Figure, Gantt, GanttTask

GANTT_TAGS = ("done", "active", "crit", "milestone", "vert")


def _parse_gantt(rows: list, fig: Figure) -> Gantt:
    g = Gantt(date_format="", axis_format="", tick_interval="", today_marker="", sections=[], tasks=[],
              statements=[])
    section = ""
    for line, text in rows[1:]:
        s = text.strip()
        if not s:
            continue
        m = re.match(r"^(dateFormat|axisFormat|tickInterval|todayMarker|title|excludes|includes|weekday|"
                     r"weekend|inclusiveEndDates|topAxis|displayMode|click)\b\s*(.*)$", s)
        if m:
            keyword, value = m.group(1), m.group(2).strip()
            if keyword == "dateFormat":
                g.date_format = value
            elif keyword == "axisFormat":
                g.axis_format = value
            elif keyword == "tickInterval":
                g.tick_interval = value
            elif keyword == "todayMarker":
                g.today_marker = value
            elif keyword == "topAxis":
                fig.hazard("gantt-topaxis", line, s, "`topAxis` is a parse error in 10.9, 11.17 and 12.1")
            g.statements.append({"keyword": keyword, "value": value, "line": line})
            continue
        m = re.match(r"^section\s+(.*)$", s)
        if m:
            section = m.group(1).strip()
            g.sections.append(section)
            g.section_lines.append(line)
            continue
        if ":" not in s:
            fig.error(line, f"cannot read the statement {s!r}")
            continue
        label, data = s.split(":", 1)
        data = re.split(r"[#;]", data, maxsplit=1)[0]
        if re.search(r"(?<!\d):|:(?!\d)", data):
            fig.hazard("gantt-label-colon", line, s,
                       "a `:` in the task label moves the task id into the data")
        if "\\n" in label:
            fig.hazard("literal-newline", line, label, "a gantt task label prints `\\n` as text")
        fields = [f.strip() for f in data.split(",")]
        tags = []
        while fields and fields[0] in GANTT_TAGS:
            tags.append(fields.pop(0))
        if "vert" in tags:
            fig.hazard("gantt-vert", line, s, "`vert` stops the render in mermaid 10.9")
        tid, start, duration = "", "", ""
        if len(fields) == 1:
            duration = fields[0]
        elif len(fields) == 2:
            start, duration = fields
        elif len(fields) == 3:
            tid, start, duration = fields
        else:
            fig.error(line, f"a task with {len(fields)} data fields")
        g.tasks.append(GanttTask(id=tid, label=label.strip(), section=section, tags=tags, start=start,
                                 duration=duration, line=line))
    return g


def gantt_refs(task: GanttTask) -> list:
    """Return the task ids a task's `after` or `until` names."""
    refs = []
    for part in (task.start, task.duration):
        m = re.match(r"^(after|until)\s+(.+)$", part.strip())
        if m:
            refs.extend(m.group(2).split())
    return refs


