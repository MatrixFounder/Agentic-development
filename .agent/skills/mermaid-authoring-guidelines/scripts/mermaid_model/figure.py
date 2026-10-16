"""Figure level of the parse model: the dataclasses of a parsed figure and its hazards
(TASK 124)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .document import Fence


@dataclass
class Settings:
    """The settings line of a figure: `%%{init: …}%%` or YAML frontmatter `config:`.

    `raw` is the source text; `config` the parsed dict (None when it does not parse);
    `error` names the parse failure. Mermaid ignores a malformed directive without a
    diagnostic, so the lint reports `error` (renderer fact: trailing comma).
    """

    raw: str
    line: int
    form: str  # "directive" | "frontmatter"
    config: Optional[dict] = None
    error: Optional[str] = None


@dataclass
class Node:
    id: str
    label: str  # label text as written, without the shape delimiters; "" when the id is the label
    shape: str  # "rect" | "round" | "stadium" | "subroutine" | "cylinder" | "circle" | "rhombus" | "hexagon" | "other"
    line: int
    classes: list = field(default_factory=list)
    parent: Optional[str] = None  # the subgraph that holds the node; None at the top level


@dataclass
class Edge:
    src: str
    dst: str
    label: str
    style: str  # "solid" | "dotted" | "thick" | "invisible"
    arrow: str  # "->" | "<->" | "none"
    line: int


@dataclass
class Subgraph:
    id: str
    title: str
    members: list  # direct member node ids and nested subgraph ids
    line: int
    parent: Optional[str] = None
    auto_id: bool = False  # True when the source gives no id and mermaid generates subGraph<n>


@dataclass
class Flowchart:
    direction: str  # "TB" | "TD" | "BT" | "LR" | "RL"
    nodes: dict  # id -> Node
    edges: list  # Edge
    subgraphs: dict  # id -> Subgraph
    classdefs: dict  # name -> {"raw": str, "props": dict, "line": int}
    styles: list  # {"target": id, "raw": str, "line": int}
    link_styles: list  # {"index": str, "raw": str, "line": int}
    subgraph_classes: dict = field(default_factory=dict)  # subgraph id -> class names


@dataclass
class Participant:
    id: str
    label: str
    kind: str  # "participant" | "actor"
    line: int
    box: Optional[str] = None
    declared: bool = True  # False when the participant appears only in a message or note


@dataclass
class Message:
    src: str
    dst: str
    text: str
    arrow: str  # the arrow token as written, e.g. "->>", "-->>", "-x", "-)"
    line: int
    activate: str = ""  # "+" | "-" | ""


@dataclass
class Note:
    over: list  # participant ids
    position: str  # "over" | "left of" | "right of"
    text: str
    line: int


@dataclass
class Block:
    kind: str  # "loop" | "alt" | "opt" | "par" | "critical" | "break" | "rect" | "box"
    label: str
    start: int
    end: int
    colour: str = ""  # the fill a `rect` or `box` line names, as written; "" for none


@dataclass
class Sequence:
    participants: list
    messages: list
    notes: list
    blocks: list
    autonumber: bool
    activations: list = field(default_factory=list)  # {"verb": "activate"|"deactivate", "id", "line"}


@dataclass
class StateNode:
    id: str
    label: str
    line: int
    composite: bool = False
    parent: Optional[str] = None
    classes: list = field(default_factory=list)
    kind: str = "state"  # "state" | "choice" | "fork" | "join"


@dataclass
class Transition:
    src: str  # "[*]" for start/end pseudo-states
    dst: str
    label: str
    line: int
    scope: Optional[str] = None  # the composite whose block holds the statement; None at the top


@dataclass
class StateDiagram:
    direction: str
    states: dict  # id -> StateNode
    transitions: list
    classdefs: dict
    styles: list  # `style` statements; they fail in mermaid 10.9
    notes: list = field(default_factory=list)  # Note (position "left of" | "right of")


@dataclass
class GanttTask:
    id: str
    label: str
    section: str
    tags: list  # "done" | "active" | "crit" | "milestone"
    start: str  # as written: a number, a date, or "after a b"
    duration: str  # as written
    line: int


@dataclass
class Gantt:
    date_format: str
    axis_format: str
    tick_interval: str
    today_marker: str
    sections: list  # names in order of appearance, repeats kept
    tasks: list
    statements: list  # every other top-level statement with its line, e.g. "topAxis"
    section_lines: list = field(default_factory=list)  # line of each entry of `sections`


@dataclass
class ErEntity:
    name: str
    alias: str
    line: int
    attributes: list = field(default_factory=list)  # attribute lines as written
    attribute_lines: list = field(default_factory=list)  # the document line of each attribute


@dataclass
class ErRelation:
    a: str
    b: str
    cardinality: str  # the relation token as written, e.g. "||--o{"
    label: str
    line: int


@dataclass
class ErDiagram:
    entities: dict  # name -> ErEntity
    relations: list


@dataclass
class AsciiBox:
    """A box drawn with border characters. Columns are display columns (0-based)."""

    top: int  # document line of the top border
    bottom: int  # document line of the bottom border, or of the `├────┤` row that ends a layer
    left: int
    right: int  # display column of the top border's right corner
    ragged: list = field(default_factory=list)  # document lines whose right border is elsewhere
    text: str = ""  # the first text line inside the box, outside the boxes it holds
    last: int = 0  # document line of the last row of the box
    #: document lines whose left side or bottom-left corner sits one column off the top-left
    #: corner; the box goes on past them
    shifted: list = field(default_factory=list)


@dataclass
class AsciiBlock:
    """An ASCII figure: a `text figure` fence, or a fence a caller reads as one (R2.5, R2.7)."""

    lines: list  # [(line, text)]
    widths: list  # display width per line, double-width characters counted twice
    tabs: list  # lines holding a tab
    wide: list  # lines holding a double-width character (East Asian Wide, Fullwidth, VS16 emoji)
    #: lines a reader aligns by column: a border or tree character, or an arrow or a text column
    #: that starts where it starts on the line above or below (ascii.md §3)
    aligned: list
    boxes: list  # AsciiBox, a box drawn inside a box included
    elements: list  # [(line, text)]: one per box plus one per text run outside boxes
    #: (upper line, lower line) where a vertical stroke outside the boxes moves by one column
    drift: list = field(default_factory=list)
    forks: list = field(default_factory=list)  # lines holding a fork: `┬` or `+` with a stroke below
    joins: list = field(default_factory=list)  # lines holding a join of a path and a stroke (`_joins`)


@dataclass
class Hazard:
    """A source construct a pinned renderer rejects, misreads or changes without a diagnostic."""

    code: str
    line: int
    text: str
    detail: str = ""


@dataclass
class Figure:
    """A parsed figure. Exactly one of the kind-specific fields is set for a Mermaid fence."""

    fence: Fence
    kind: str  # "flowchart" | "sequence" | "state" | "gantt" | "er" | "class" | other keyword | "ascii" | "unknown"
    keyword: str  # the diagram keyword as written, e.g. "graph", "stateDiagram-v2"
    settings: Optional[Settings] = None
    flowchart: Optional[Flowchart] = None
    sequence: Optional[Sequence] = None
    state: Optional[StateDiagram] = None
    gantt: Optional[Gantt] = None
    acc_title: str = ""
    acc_descr: str = ""
    parse_errors: list = field(default_factory=list)  # {"line": int, "message": str}
    er: Optional[ErDiagram] = None
    ascii: Optional[AsciiBlock] = None
    settings_blocks: list = field(default_factory=list)  # every Settings of the fence, in order
    hazards: list = field(default_factory=list)  # Hazard
    acc_lines: list = field(default_factory=list)  # lines of accTitle and accDescr statements
    #: element counts of the kinds without a full parser, keyed by the budget metric of
    #: notation.json: classes (class), nodes (mindmap), periods (timeline), tasks (journey),
    #: commits (gitGraph)
    counts: dict = field(default_factory=dict)
    #: the elements of a kind without a full parser (ITEM_KINDS), for the inventory (TASK R6.5):
    #: `(kind, id, text, line)` with kind node, edge, label, note, number, group or task
    items: list = field(default_factory=list)

    def error(self, line: int, message: str) -> None:
        self.parse_errors.append({"line": line, "message": message})

    def hazard(self, code: str, line: int, text: str, detail: str = "") -> None:
        self.hazards.append(Hazard(code=code, line=line, text=text, detail=detail))


