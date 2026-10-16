"""Parse model: the scan of the other diagram kinds the skill licenses (TASK 124)."""

from __future__ import annotations

import re

from .figure import Figure
from .er import _STYLING_DETAIL, _styling_statement

_CLASS_LINK = re.compile(
    r'^(?P<a>[^\s"]+?)\s*(?:"[^"]*"\s*)?(?P<link>[<*o|]{0,2}(?:--|\.\.)[>*o|]{0,2})\s*'
    r'(?:"[^"]*"\s*)?(?P<b>[^\s":]+)')
_CLASS_SKIP = re.compile(r"^(note|style|cssClass|classDef|click|link|callback|direction|title)\b")


def _class_name(token: str) -> str:
    return re.sub(r"~[^~]*~|:::[\w-]+|\[.*$", "", token).strip()


def _count_classes(rows: list) -> dict:
    """Classes a class diagram draws: declared, linked or given a member line."""
    names: set = set()
    stack: list = []  # "body" for a class body, "namespace" for a namespace block
    for _line, text in rows[1:]:
        s = text.strip()
        if not s:
            continue
        if stack and stack[-1] == "body":
            if s.startswith("}"):
                stack.pop()
            continue
        if s.startswith("}"):
            if stack:
                stack.pop()
            continue
        if re.match(r"^namespace\s+\S+\s*\{", s):
            stack.append("namespace")
            continue
        m = re.match(r"^class\s+(\S+)", s)
        if m:
            names.add(_class_name(m.group(1).rstrip("{")))
            if s.endswith("{"):
                stack.append("body")
            continue
        m = re.match(r"^<<[^>]*>>\s*(\S+)", s)
        if m:
            names.add(_class_name(m.group(1)))
            continue
        if _CLASS_SKIP.match(s):
            continue
        m = _CLASS_LINK.match(s)
        if m:
            names.update(_class_name(x) for x in (m.group("a"), m.group("b")))
            continue
        m = re.match(r"^([^\s:]+)\s*:", s)
        if m:
            names.add(_class_name(m.group(1)))
    names.discard("")
    return {"classes": len(names)}


def _count_mindmap(rows: list) -> dict:
    """Nodes of a mind map: one per statement line; icon and class lines belong to a node."""
    nodes = [r for r in rows[1:] if r[1].strip() and not r[1].strip().startswith(("::icon(", ":::"))]
    return {"nodes": len(nodes)}


def _count_timeline(rows: list) -> dict:
    """Periods of a timeline: a line that starts a period; `: event` lines continue one."""
    periods = [r for r in rows[1:] if r[1].strip() and not r[1].strip().startswith(":")
               and not re.match(r"^(title|section)\b", r[1].strip())]
    return {"periods": len(periods)}


def _count_journey(rows: list) -> dict:
    """Tasks of a user journey: `name: score: actors` lines."""
    tasks = [r for r in rows[1:] if ":" in r[1] and not re.match(r"^(title|section)\b", r[1].strip())]
    return {"tasks": len(tasks)}


def _count_gitgraph(rows: list) -> dict:
    """Commits of a git graph: `commit`, `merge` and `cherry-pick` each draw one."""
    commits = [r for r in rows[1:] if re.match(r"^(commit|merge|cherry-pick)\b", r[1].strip())]
    return {"commits": len(commits)}


_COUNTERS = {"class": _count_classes, "mindmap": _count_mindmap, "timeline": _count_timeline,
             "journey": _count_journey, "gitGraph": _count_gitgraph}


def _class_items(rows: list) -> list:
    """Inventory items of a class diagram: classes, members, relations with their labels and
    numeric multiplicities, and notes."""
    items, seen, stack, current = [], set(), [], None

    def add_class(name: str, line: int) -> None:
        if name and name not in seen:
            seen.add(name)
            items.append(("node", name, name, line))

    for line, text in rows[1:]:
        s = text.strip()
        if not s:
            continue
        if stack and stack[-1] == "body":
            if s.startswith("}"):
                stack.pop()
                current = None
            elif not s.startswith("<<"):
                items.append(("label", current, s, line))
            continue
        if s.startswith("}"):
            if stack:
                stack.pop()
            continue
        if re.match(r"^namespace\s+\S+\s*\{", s):
            stack.append("namespace")
            continue
        m = re.match(r"^class\s+(\S+)", s)
        if m:
            current = _class_name(m.group(1).rstrip("{"))
            add_class(current, line)
            if s.endswith("{"):
                stack.append("body")
            continue
        m = re.match(r'^note\s+(?:for\s+\S+\s+)?"(.*)"\s*$', s)
        if m:
            items.append(("note", f"n{sum(1 for i in items if i[0] == 'note')}", m.group(1), line))
            continue
        m = re.match(r"^<<[^>]*>>\s*(\S+)", s)
        if m:
            add_class(_class_name(m.group(1)), line)
            continue
        if _CLASS_SKIP.match(s):
            continue
        m = _CLASS_LINK.match(s)
        if m:
            a, b = _class_name(m.group("a")), _class_name(m.group("b"))
            add_class(a, line)
            add_class(b, line)
            rid = f"r{sum(1 for i in items if i[0] == 'edge')}"
            items.append(("edge", rid, f"{a} {m.group('link')} {b}", line))
            items += [("number", rid, x, line) for x in re.findall(r'"(\d+(?:\.\.\d+)?)"', s[:m.end()])]
            rest = s[m.end():].strip()
            if rest.startswith(":") and rest[1:].strip():
                items.append(("label", rid, rest[1:].strip(), line))
            continue
        m = re.match(r"^([^\s:]+)\s*:\s*(.*)$", s)
        if m:
            name = _class_name(m.group(1))
            add_class(name, line)
            if m.group(2).strip():
                items.append(("label", name, m.group(2).strip(), line))
    return items


_MINDMAP_NODE = re.compile(r"^(?P<id>[^\s()\[\]{}]*?)\s*(?:\(\(|\)\)|\{\{|\(|\)|\[)(?P<text>.*?)"
                           r"(?:\)\)|\(\(|\}\}|\)|\(|\])$")


def _mindmap_items(rows: list) -> list:
    """Inventory items of a mind map: one node per statement line; icon and class lines belong
    to the node above them."""
    items = []
    for line, text in rows[1:]:
        s = text.strip()
        if not s or s.startswith(("::icon(", ":::")):
            continue
        m = _MINDMAP_NODE.match(s)
        ident = (m.group("id") if m else "") or f"m{len(items)}"
        label = (m.group("text") if m else s).strip().strip('"').strip("`")
        items.append(("node", ident, label, line))
    return items


def _timeline_items(rows: list) -> list:
    """Inventory items of a timeline: sections, periods and the events of each period."""
    items, period = [], "p0"
    for line, text in rows[1:]:
        s = text.strip()
        if not s or re.match(r"^title\b", s):
            continue
        m = re.match(r"^section\s+(.*)$", s)
        if m:
            items.append(("group", m.group(1).strip(), m.group(1).strip(), line))
            continue
        parts = [p.strip() for p in s.split(":")]
        if parts[0]:
            period = f"p{sum(1 for i in items if i[0] == 'node') + 1}"
            items.append(("node", period, parts[0], line))
        items += [("label", period, p, line) for p in parts[1:] if p]
    return items


def _journey_items(rows: list) -> list:
    """Inventory items of a user journey: sections, tasks with their score and their actors."""
    items = []
    for line, text in rows[1:]:
        s = text.strip()
        if not s or re.match(r"^title\b", s):
            continue
        m = re.match(r"^section\s+(.*)$", s)
        if m:
            items.append(("group", m.group(1).strip(), m.group(1).strip(), line))
            continue
        parts = [p.strip() for p in s.split(":")]
        tid = f"task{sum(1 for i in items if i[0] == 'task') + 1}"
        items.append(("task", tid, parts[0], line))
        if len(parts) > 1 and parts[1]:
            items.append(("number", tid, parts[1], line))
        if len(parts) > 2 and parts[2]:
            items.append(("label", tid, parts[2], line))
    return items


def _gitgraph_items(rows: list) -> list:
    """Inventory items of a git graph: commits with their tags, branches, merges and picks."""
    items, drawn = [], 0
    for line, text in rows[1:]:
        s = text.strip()
        m = re.match(r"^(commit|merge|cherry-pick|branch)\b\s*(.*)$", s)
        if not m:
            continue
        verb, rest = m.group(1), m.group(2)
        cid = re.search(r'\bid:\s*"([^"]*)"', rest)
        tag = re.search(r'\btag:\s*"([^"]*)"', rest)
        name = rest.split()[0] if rest.split() else ""
        if verb == "branch":
            items.append(("group", name, name, line))
            continue
        drawn += 1
        ident = cid.group(1) if cid and verb != "cherry-pick" else f"c{drawn}"
        if verb == "commit":
            items.append(("node", ident, cid.group(1) if cid else "commit", line))
        elif verb == "merge":
            items.append(("edge", ident, f"merge {name}", line))
        else:
            items.append(("node", ident, f"cherry-pick {cid.group(1) if cid else rest}", line))
        if tag:
            items.append(("label", ident, tag.group(1), line))
    return items


def _pie_items(rows: list) -> list:
    """Inventory items of a pie chart: one node per slice and the slice's value."""
    items = []
    for line, text in rows[1:]:
        m = re.match(r'^\s*"([^"]*)"\s*:\s*(\S+)', text)
        if m:
            sid = f"s{sum(1 for i in items if i[0] == 'node') + 1}"
            items += [("node", sid, m.group(1), line), ("number", sid, m.group(2), line)]
    return items


_ITEMS = {"class": _class_items, "mindmap": _mindmap_items, "timeline": _timeline_items,
          "journey": _journey_items, "gitGraph": _gitgraph_items, "pie": _pie_items}

#: Kinds without a full parser whose elements `Figure.items` lists for the inventory.
ITEM_KINDS = tuple(_ITEMS)

#: Kinds that draw in the viewer's theme colours; other-kinds.md rule 5 forbids styling them.
THEME_KINDS = ("class", "mindmap", "timeline", "quadrantChart", "journey", "gitGraph", "pie",
               "xychart-beta", "sankey-beta")
#: The styling each kind's grammar reads in mermaid 11.17.2: a class diagram has `style`,
#: `classDef`, `cssClass` and `:::`; a mind map a line that starts with `:::`; a quadrant chart
#: `classDef` and `:::`. The other grammars hold no styling statement.
_THEME_STYLING = {
    "class": re.compile(r"^(?:style|cssClass|classDef)\s|:::"),
    "mindmap": re.compile(r"^:::"),
    "quadrantChart": re.compile(r"^classDef\s|:::"),
}
#: A styling statement written out in full: keyword, target and a property. In a kind without
#: styling, any other line that starts with `style` or `classDef` is a node, a period or a task.
_THEME_STATEMENT = re.compile(r"^(?:style|classDef)\s+\S+\s+[\w-]+:\S")

#: Kinds read by `_scan_other`: no full parser, but styling hazards, a budget count or items.
OTHER_SCANNED_KINDS = ("requirementDiagram",) + THEME_KINDS


def _scan_other(rows: list, fig: Figure) -> None:
    """Record the styling hazards, the element count and the items of a kind without a full
    parser."""
    depth = 0
    for line, text in rows[1:]:
        s = text.strip()
        if not s:
            continue
        if depth == 0:
            styling = _styling_statement(s, fig.kind)
            if styling:
                fig.hazard("styling-v10", line, s, styling)
            elif (fig.kind, ":::") in _STYLING_DETAIL and ":::" in s:
                fig.hazard("styling-v10", line, s, _STYLING_DETAIL[fig.kind, ":::"])
            elif fig.kind in THEME_KINDS and (_THEME_STATEMENT.match(s) or (
                    fig.kind in _THEME_STYLING and _THEME_STYLING[fig.kind].search(s))):
                fig.hazard("styling-theme", line, s, f"a {fig.kind} figure draws in the viewer's theme "
                                                     "colours (other-kinds.md rule 5)")
        depth = max(0, depth + s.count("{") - s.count("}"))
    counter = _COUNTERS.get(fig.kind)
    if counter is not None:
        fig.counts.update(counter(rows))
    items = _ITEMS.get(fig.kind)
    if items is not None:
        fig.items = items(rows)


