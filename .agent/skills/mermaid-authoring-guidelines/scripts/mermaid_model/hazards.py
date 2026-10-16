"""Hazard codes of the parse model: the codes the parser records and the lint maps to
rules (TASK 124)."""

from __future__ import annotations

import html.entities
import re

#: Codes the parser records in `Figure.hazards`. The lint maps each code to one rule.
HAZARD_CODES = (
    "label-unquoted-bracket",  # ( ) [ ] { } or " in an unquoted node label or subgraph title
    "label-leading-slash",  # an unquoted rectangle label that starts with / or \
    "shape-unclosed",  # a node shape bracket with no closing bracket
    "label-quote-inside",  # a raw " inside a quoted label
    "edge-label-bracket",  # ( ) [ ] { } or " in an unquoted |pipe| edge label
    "edge-label-dotted-dot",  # . inside a -. text .-> label
    "edge-label-double-dash",  # -- or == inside a -- text --> or == text ==> label
    "html-tag",  # <T> or another tag-like token that the renderer strips as HTML
    "end-id",  # the keyword `end` used as a node or participant id
    "link-head-id",  # an id that starts with o or x directly after a link: A---ops
    "shape-at",  # A@{ shape: … } (11.3+) or participant X@{ … } (11.11+)
    "edge-id",  # an edge id e1@--> (11.5+)
    "animate",  # edge animation (11.5+)
    "linkstyle-range",  # linkStyle index past the edges defined so far
    "subgraph-direction-title",  # a subgraph title holding `direction XX`
    "classdef-default",  # classDef default
    "inline-comment",  # %% after a flowchart statement (parse error)
    "seq-semicolon",  # ; in a sequence message or note outside an entity
    "seq-hash",  # # in a sequence message or note outside an entity
    "literal-newline",  # a literal \n where the renderer prints it as text
    "seq-styling",  # classDef, class or style in a sequence diagram
    "seq-syntax-above-floor",  # half-arrows, decimal autonumber, A<<->>B (11.x)
    "seq-deactivate-inactive",  # deactivating a participant that is not active
    "seq-hex-colour",  # a hex colour after rect (10.9: black rect) or box (fill and title lost)
    "state-label-colon",  # : in a state label (10.9 parse error)
    "state-label-semicolon",  # ; in a state label (stray states)
    "state-label-entity",  # #n; in a state label (read as a control character)
    "state-label-quoted",  # quotes around a transition label or description (they print)
    "state-style",  # style statement in a state diagram
    "state-class-ids",  # a class statement whose ids hold a non-ASCII character
    "gantt-label-colon",  # : in a gantt task label (shifts the task id)
    "gantt-topaxis",  # topAxis statement (parse error)
    "gantt-vert",  # vert marker (10.9 crash)
    "timeline-header",  # text after `timeline` on its header line (10.9: a period; 11.17: a direction)
    "styling-v10",  # classDef, class, style or ::: that 10.9 rejects in ER, class, requirement
    "acc-unsupported",  # accTitle or accDescr in a mindmap or sankey-beta figure (render error)
    "header-line",  # text after a flowchart's direction, or no direction there (parse error)
    "label-entity",  # #n; in a flowchart label that names no printable character
    "class-before-node",  # class X c before X is defined: mermaid drops the class
    "style-node",  # style X … where no other statement names X: mermaid draws a stray node
    "linkstyle",  # any linkStyle (flowchart.md §2 rule 7: 10.9.8 and 12.1.0 differ)
    "subgraph-direction",  # a direction statement inside a subgraph (dropped once a member links out)
    "styling-theme",  # classDef, style, cssClass or ::: in a kind that draws in theme colours
)

#: Kinds that fail to render with an `accTitle` or `accDescr` statement (10.9.8, 11.17.2, 12.1.0).
ACC_UNSUPPORTED_KINDS = ("mindmap", "sankey-beta")

#: HTML tags a label may hold; anything else that looks like a tag is stripped by the renderer.
ALLOWED_TAGS = frozenset({"br", "small", "b", "i", "u", "strong", "em", "sub", "sup", "code",
                          "span", "s", "del", "mark", "big"})

_TAGLIKE = re.compile(r"</?([A-Za-z][^\s<>/]*)(?:\s[^<>]*)?/?>")


def _bad_tags(text: str) -> list:
    """Return tag-like tokens of *text* that are not in ALLOWED_TAGS."""
    return [m.group(0) for m in _TAGLIKE.finditer(text) if m.group(1).lower() not in ALLOWED_TAGS]


_ENTITY = re.compile(r"#(\w+);")


def _printable_entity(name: str) -> bool:
    """True for `#35;`-style codes of printable characters and for named HTML entities."""
    if name.isdigit():
        return int(name) >= 32
    return name in html.entities.name2codepoint or (name + ";") in html.entities.html5


def _strip_entities(text: str) -> str:
    """Remove the Mermaid entities that render a printable character (`#35;`, `#quot;`), so a
    `;` or `#` inside them is not counted. `#1;` stays: it renders a control character."""
    return _ENTITY.sub(lambda m: "" if _printable_entity(m.group(1)) else m.group(0), text)


