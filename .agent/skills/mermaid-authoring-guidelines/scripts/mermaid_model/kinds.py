"""Kinds of the parse model: the diagram keyword and the kind it names (TASK 124)."""

from __future__ import annotations

import re
from typing import Optional

from .base import load_notation

#: Keyword -> kind for the kinds that have a parser. `flowchart-v2` is a diagram id, not a
#: keyword: 10.9.8 and 11.17.2 report a lexical error on it.
KIND_OF_KEYWORD = {
    "flowchart": "flowchart",
    "graph": "flowchart",
    "flowchart-elk": "flowchart",
    "sequenceDiagram": "sequence",
    "stateDiagram-v2": "state",
    "stateDiagram": "state",
    "gantt": "gantt",
    "erDiagram": "er",
    "classDiagram": "class",
    "classDiagram-v2": "class",
}

#: Diagram keywords of mermaid 10.9–12.1 besides the ones `notation.json` lists. A keyword that is
#: in neither list gives the kind "unknown". Not here: `requirement`, which the detector takes but
#: the grammar rejects, and `zenuml`, which not every pinned install draws. The v11 and v12
#: installs draw it with the plugin `@mermaid-js/mermaid-zenuml`. Mermaid 10.9.8 draws it with no
#: plugin, and that render fails `render_check.py`: its text runs past its box (measured
#: 2026-10-29, TASK 136).
OTHER_KEYWORDS = (
    "journey", "pie", "gitGraph", "mindmap", "timeline", "quadrantChart", "requirementDiagram",
    "info", "usecase-beta", "agentflow-beta", "treeView-beta",
    "wardley-beta", "eventmodeling", "swimlane-beta", "cynefin-beta", "railroad-beta",
    "railroad-ebnf-beta", "railroad-abnf-beta", "railroad-peg-beta", "ishikawa",
    "architecture", "radar", "treemap", "venn",
)


def diagram_keyword(statement: str) -> str:
    """The diagram keyword of a fence's first statement: its first token. `gitGraph:` is the
    colon form of `gitGraph`, which the 10.9 and 11 grammars accept."""
    m = re.match(r"[^\s;]+", statement.strip())
    word = m.group(0) if m else ""
    return "gitGraph" if word == "gitGraph:" else word


def _known_keywords(notation: Optional[dict] = None) -> set:
    known = set(KIND_OF_KEYWORD) | set(OTHER_KEYWORDS)
    try:
        kinds = (notation or load_notation()).get("kinds", {})
        for key in ("preferred", "allowed", "avoid"):
            known.update(kinds.get(key, []))
    except (OSError, ValueError):
        pass
    return known


