"""LABEL rules of the figure lint: label text, its length, markup and escapes (TASK 126)."""

from __future__ import annotations

import re
from typing import Callable

import mermaid_model as mm

from .base import rule, _doc, _lines_of


def _label_probe(where: str, key: str, fire: bool) -> Callable:
    def make(notation):
        n = int(notation["labels"][key]) + (1 if fire else 0)
        text = "x" * n
        bodies = {
            "node1": f'flowchart TB\n  A["{text}"] --> B',
            "node2": f'flowchart TB\n  A["short<br/>{text}"] --> B',
            "edge": f'flowchart TB\n  A -->|"{text}"| B',
            "message": f"sequenceDiagram\n  participant A\n  participant B\n  A->>B: {text}",
            "note": f"sequenceDiagram\n  participant A\n  Note over A: {text}",
            "gantt": ("gantt\n  dateFormat x\n  axisFormat %Q\n  todayMarker off\n  section S\n"
                      f"  {text} :a, 0, 3ms"),
            "participant": f"sequenceDiagram\n  participant A as {text}\n  participant B\n  A->>B: x",
        }
        return _doc(bodies[where])
    return make


def _lines_probe(where: str, key: str, fire: bool) -> Callable:
    """A probe whose label has one line more than the limit (fire) or exactly the limit."""
    def make(notation):
        n = int(notation["labels"][key]) + (1 if fire else 0)
        text = "<br/>".join(f"line {k}" for k in range(1, n + 1))
        bodies = {
            "node": f'flowchart TB\n  A["{text}"] --> B',
            "message": f"sequenceDiagram\n  participant A\n  participant B\n  A->>B: {text}",
            "note": f"sequenceDiagram\n  participant A\n  Note over A: {text}",
            "edge": f"flowchart TB\n  A -->|{text}| B",
            "participant": f"sequenceDiagram\n  participant A as {text}\n  participant B\n  A->>B: x",
        }
        return _doc(bodies[where])
    return make


def _node_label_items(fig) -> list:
    """(line, id, visible lines) for every node-like element: flowchart nodes and subgraph
    titles, states, and ER entities by the name their box shows (other-kinds.md rule 6)."""
    out = []
    if fig.flowchart:
        out += [(n.line, n.id, _lines_of(n.label, n.id)) for n in fig.flowchart.nodes.values()]
        out += [(s.line, s.id, _lines_of(s.title, s.id)) for s in fig.flowchart.subgraphs.values()]
    if fig.state:
        out += [(s.line, s.id, _lines_of(s.label, s.id)) for s in fig.state.states.values()]
    if fig.er:
        out += [(e.line, e.name, _lines_of(e.alias, e.name)) for e in fig.er.entities.values()]
    return out


def _edge_label_items(fig) -> list:
    out = []
    if fig.flowchart:
        out += [(e.line, e.label) for e in fig.flowchart.edges if e.label]
    if fig.state:
        out += [(t.line, t.label) for t in fig.state.transitions if t.label]
    if fig.er:
        out += [(r.line, r.label) for r in fig.er.relations if r.label]
    return out


@rule("MA-LABEL-01", "warn", "Node label first line over the character limit",
      "Keep the name to about 4 words; move the role to a second line after <br/>.",
      _label_probe("node1", "node_line1_chars_max", True), _label_probe("node1", "node_line1_chars_max", False))
def _check_node_line1(fig, ctx):
    limit = int(ctx.notation["labels"]["node_line1_chars_max"])
    return [(line, f"`{nid}`: {mm.char_count(lines[0])} characters > {limit}")
            for line, nid, lines in _node_label_items(fig) if lines and mm.char_count(lines[0]) > limit]


@rule("MA-LABEL-02", "warn", "Node label second line over the character limit",
      "Shorten the second line; detail belongs in the text.",
      _label_probe("node2", "node_second_line_chars_max", True),
      _label_probe("node2", "node_second_line_chars_max", False))
def _check_node_line2(fig, ctx):
    limit = int(ctx.notation["labels"]["node_second_line_chars_max"])
    out = []
    for line, nid, lines in _node_label_items(fig):
        for extra in lines[1:]:
            if mm.char_count(extra) > limit:
                out.append((line, f"`{nid}`: a line of {mm.char_count(extra)} characters > {limit}"))
    return out


@rule("MA-LABEL-03", "warn", "Edge label over the character limit",
      "Keep an edge label to about 3 words; the payload goes in the text.",
      _label_probe("edge", "edge_label_chars_max", True), _label_probe("edge", "edge_label_chars_max", False))
def _check_edge_label(fig, ctx):
    limit = int(ctx.notation["labels"]["edge_label_chars_max"])
    out = []
    for line, label in _edge_label_items(fig):
        for text in mm.label_lines(label):
            if mm.char_count(text) > limit:
                out.append((line, f"`{text}`: {mm.char_count(text)} characters > {limit}"))
    return out


@rule("MA-LABEL-04", "warn", "Sequence message over the character limit",
      "Name the call; parameters and payloads go in the text's table.",
      _label_probe("message", "sequence_message_chars_max", True),
      _label_probe("message", "sequence_message_chars_max", False))
def _check_message(fig, ctx):
    if fig.sequence is None:
        return []
    limit = int(ctx.notation["labels"]["sequence_message_chars_max"])
    out = []
    for m in fig.sequence.messages:
        for text in mm.label_lines(m.text):
            if mm.char_count(text) > limit:
                out.append((m.line, f"{mm.char_count(text)} characters > {limit}"))
    return out


@rule("MA-LABEL-05", "warn", "Note line over the character limit",
      "Break the note with <br/> or move it to the text.",
      _label_probe("note", "note_chars_max", True), _label_probe("note", "note_chars_max", False))
def _check_note(fig, ctx):
    limit = int(ctx.notation["labels"]["note_chars_max"])
    notes = (fig.sequence.notes if fig.sequence else []) + (fig.state.notes if fig.state else [])
    out = []
    for n in notes:
        for text in mm.label_lines(n.text):
            if mm.char_count(text) > limit:
                out.append((n.line, f"{mm.char_count(text)} characters > {limit}"))
    return out


@rule("MA-LABEL-06", "warn", "Gantt task label over the character limit",
      "Shorten the task label; the plan table holds the full title.",
      _label_probe("gantt", "gantt_label_chars_max", True), _label_probe("gantt", "gantt_label_chars_max", False))
def _check_gantt_label(fig, ctx):
    if fig.gantt is None:
        return []
    limit = int(ctx.notation["labels"]["gantt_label_chars_max"])
    return [(t.line, f"`{t.label}`: {mm.char_count(t.label)} characters > {limit}")
            for t in fig.gantt.tasks if mm.char_count(t.label) > limit]


_LETTERS = re.compile(r"[^\W\d_]+")


def _drawn_names(fig) -> set:
    """The words of the names a figure draws: each letter run of a node, state, entity or group
    label, in the case the label writes it."""
    return {word for _line, _id, lines in _node_label_items(fig) for text in lines
            for word in _LETTERS.findall(text)}


def _starts_uppercase(label: str, acronym_max: int, names: frozenset = frozenset()) -> bool:
    """True when the first word of *label* starts with a capital letter and is neither an
    acronym of at most *acronym_max* letters nor a word of *names* (SKILL.md Step 5.3: a name
    keeps its case)."""
    lines = mm.label_lines(label)
    if not lines:
        return False
    text = lines[0]
    start = next((k for k, ch in enumerate(text) if ch.isupper() or ch.islower()), None)
    if start is None or text[start].islower():
        return False
    m = _LETTERS.match(text[start:])
    word = m.group(0) if m else ""
    if word and not any(ch.islower() for ch in word) and len(word) <= acronym_max:
        return False
    return word not in names


@rule("MA-LABEL-07", "warn", "Edge label that starts with a capital letter in a cased script",
      "Write edge labels lowercase: `reads`, not `Reads`; acronyms and the names the figure's "
      "boxes show keep their case.",
      _doc("flowchart TB\n  A -->|Sends data| B"),
      _doc("flowchart TB\n  A -->|sends SQL| B\n  B -->|Kafka topic| K[Kafka]"))
def _check_edge_case(fig, ctx):
    acronym_max = int(ctx.notation.get("lint", {}).get("acronym_max_chars", 5))
    names = frozenset(_drawn_names(fig))
    return [(line, f"`{label}`") for line, label in _edge_label_items(fig)
            if _starts_uppercase(label, acronym_max, names)]


@rule("MA-LABEL-08", "warn", "Node label with more lines than the limit",
      "Keep a name line and one role line; further detail belongs in the text.",
      _lines_probe("node", "node_label_lines_max", True), _lines_probe("node", "node_label_lines_max", False))
def _check_node_lines(fig, ctx):
    limit = int(ctx.notation["labels"]["node_label_lines_max"])
    return [(line, f"`{nid}`: {len(lines)} lines > {limit}")
            for line, nid, lines in _node_label_items(fig) if len(lines) > limit]


@rule("MA-LABEL-09", "warn", "Sequence message with more lines than the limit",
      "Name the call in a few words; parameters and payloads go in the text's table.",
      _lines_probe("message", "sequence_message_lines_max", True),
      _lines_probe("message", "sequence_message_lines_max", False))
def _check_message_lines(fig, ctx):
    if fig.sequence is None:
        return []
    limit = int(ctx.notation["labels"]["sequence_message_lines_max"])
    return [(m.line, f"{len(mm.label_lines(m.text))} lines > {limit}")
            for m in fig.sequence.messages if len(mm.label_lines(m.text)) > limit]


@rule("MA-LABEL-10", "warn", "Participant name over the character limit",
      "Shorten the display name (`participant GW as Gateway`); the full name goes in the text.",
      _label_probe("participant", "participant_chars_max", True),
      _label_probe("participant", "participant_chars_max", False))
def _check_participant(fig, ctx):
    if fig.sequence is None:
        return []
    limit = int(ctx.notation["labels"]["participant_chars_max"])
    out = []
    for p in fig.sequence.participants:
        for text in _lines_of(p.label, p.id):
            if mm.char_count(text) > limit:
                out.append((p.line, f"`{p.id}`: `{text}` has {mm.char_count(text)} characters > {limit}"))
    return out


@rule("MA-LABEL-11", "warn", "Note with more lines than the limit",
      "Shorten the note or move it to the text.",
      _lines_probe("note", "note_lines_max", True), _lines_probe("note", "note_lines_max", False))
def _check_note_lines(fig, ctx):
    limit = int(ctx.notation["labels"]["note_lines_max"])
    notes = (fig.sequence.notes if fig.sequence else []) + (fig.state.notes if fig.state else [])
    return [(n.line, f"{len(mm.label_lines(n.text))} lines > {limit}")
            for n in notes if len(mm.label_lines(n.text)) > limit]


@rule("MA-LABEL-12", "warn", "Edge label with more lines than the limit",
      "Keep an edge label to one line of about 3 words; the payload goes in the text.",
      _lines_probe("edge", "edge_label_lines_max", True), _lines_probe("edge", "edge_label_lines_max", False))
def _check_edge_lines(fig, ctx):
    limit = int(ctx.notation["labels"]["edge_label_lines_max"])
    return [(line, f"{len(mm.label_lines(label))} lines > {limit}")
            for line, label in _edge_label_items(fig) if len(mm.label_lines(label)) > limit]


@rule("MA-LABEL-13", "warn", "Participant name with more lines than the limit",
      "Give the participant a one-line display name; the role goes in the text.",
      _lines_probe("participant", "participant_lines_max", True),
      _lines_probe("participant", "participant_lines_max", False))
def _check_participant_lines(fig, ctx):
    if fig.sequence is None:
        return []
    limit = int(ctx.notation["labels"]["participant_lines_max"])
    return [(p.line, f"`{p.id}`: {len(_lines_of(p.label, p.id))} lines > {limit}")
            for p in fig.sequence.participants if len(_lines_of(p.label, p.id)) > limit]


def _html_label_items(fig) -> list:
    """(line, label as written) of every label the parsed kinds draw as HTML: flowchart nodes,
    subgraph titles and edges, states and transitions, ER entities and relations (TASK 121 R4.1)."""
    out = []
    if fig.flowchart:
        out += [(n.line, n.label) for n in fig.flowchart.nodes.values() if n.label]
        out += [(s.line, s.title) for s in fig.flowchart.subgraphs.values() if s.title]
        out += [(e.line, e.label) for e in fig.flowchart.edges if e.label]
    if fig.state:
        out += [(s.line, s.label) for s in fig.state.states.values() if s.label]
        out += [(t.line, t.label) for t in fig.state.transitions if t.label]
    if fig.er:
        out += [(e.line, e.alias) for e in fig.er.entities.values() if e.alias]
        out += [(r.line, r.label) for r in fig.er.relations if r.label]
    return out


_SMALL_TAG = re.compile(r"<\s*small\b", re.IGNORECASE)


def _escaped(text: str) -> str:
    """*text* with each backslash doubled and each character that `str.isprintable()` refuses
    written as its Python escape, so a label quoted from the linted document cannot drive the
    terminal, nor print as an escape it does not hold (CWE-150, TASK 121 D11). svg_geometry.py
    binds the same function, which `svg_geometry_parts/api.py` holds; a test pins the two to
    one output."""
    return "".join("\\\\" if ch == "\\" else ch if ch.isprintable() else ascii(ch)[1:-1]
                   for ch in text)


@rule("MA-LABEL-14", "warn", "`<small>` in a flowchart, state or ER label",
      "Write the second line as plain text after <br/>: GitHub shows <small> at full size in a "
      "box that mermaid sized for small text.",
      _doc('flowchart TB\n  A["Loan API<br/><small>host app-a</small>"] --> B'),
      _doc('flowchart TB\n  A["Loan API<br/>host app-a"] --> B'))
def _check_small(fig, ctx):
    return [(line, f"<small> in `{_escaped(' '.join(label.split())[:60])}`")
            for line, label in _html_label_items(fig) if _SMALL_TAG.search(label)]


