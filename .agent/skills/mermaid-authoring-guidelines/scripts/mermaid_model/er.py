"""Entity-relationship parser of the parse model (TASK 124)."""

from __future__ import annotations

import re
from typing import Optional

from .figure import ErDiagram, ErEntity, ErRelation, Figure

_ER_RELATION = re.compile(
    r'^(?P<a>"[^"]+"|[^\s"{}]+)\s*(?P<card>[|}o][|o]?(?:--|\.\.)[|o][|{o]?)\s*(?P<b>"[^"]+"|[^\s"{}:]+)\s*'
    r'(?::(?P<label>.*))?$')
_ER_ENTITY_OPEN = re.compile(r'^(?P<name>[^\s"{\[]+)(?:\s*\[\s*"?(?P<alias>[^"\]]*)"?\s*\])?\s*\{\s*(?P<rest>.*)$')

#: Styling that mermaid 10.9.8 rejects or misreads, per kind and construct. Measured 2026-10-02:
#: 11.17.2 and 12.1.0 render each of them; `style`, `cssClass` and `:::` in a class diagram
#: render in all three versions.
_STYLING_DETAIL = {
    ("er", "classDef"): "`classDef` in an ER diagram is a parse error in mermaid 10.9",
    ("er", "class"): "`class` in an ER diagram draws its words as stray entities in mermaid 10.9",
    ("er", "style"): "`style` in an ER diagram is a parse error in mermaid 10.9",
    ("er", ":::"): "`:::` in an ER diagram is a parse error in mermaid 10.9",
    ("class", "classDef"): "`classDef` in a class diagram is a parse error in mermaid 10.9",
    ("requirementDiagram", "classDef"): "`classDef` in a requirement diagram is a parse error in mermaid 10.9",
    ("requirementDiagram", "class"): "`class` in a requirement diagram is a parse error in mermaid 10.9",
    ("requirementDiagram", "style"): "`style` in a requirement diagram is a parse error in mermaid 10.9",
    ("requirementDiagram", ":::"): "`:::` in a requirement diagram stops the render in mermaid 10.9",
}
_STYLING_STATEMENT = {
    "classDef": re.compile(r"^classDef\s+\S+\s+\S"),
    "class": re.compile(r"^class\s+[^\s,]+(?:\s*,\s*[^\s,]+)*\s+[\w-]+\s*;?\s*$"),
    "style": re.compile(r"^style\s+\S+\s+[\w-]+:\S"),
}


def _styling_statement(s: str, kind: str) -> str:
    """The detail of a styling statement that mermaid 10.9 rejects in *kind*, or ""."""
    for word, pattern in _STYLING_STATEMENT.items():
        if (kind, word) in _STYLING_DETAIL and pattern.match(s):
            return _STYLING_DETAIL[kind, word]
    return ""


def _parse_er(rows: list, fig: Figure) -> ErDiagram:
    er = ErDiagram(entities={}, relations=[])
    current: Optional[ErEntity] = None

    def ensure(name: str, line: int) -> ErEntity:
        name = name.strip('"')
        ent = er.entities.get(name)
        if ent is None:
            ent = ErEntity(name=name, alias="", line=line)
            er.entities[name] = ent
        return ent

    for line, text in rows[1:]:
        s = text.strip()
        if not s:
            continue
        if current is not None:
            if s.startswith("}"):
                current = None
            else:
                current.attributes.append(s)
                current.attribute_lines.append(line)
            continue
        if re.match(r"^direction\s+\S+$", s) or re.match(r"^title\b", s):
            continue
        styling = "" if _ER_RELATION.match(s) else _styling_statement(s, "er")
        if styling:
            fig.hazard("styling-v10", line, s, styling)
            continue
        if ":::" in s:
            fig.hazard("styling-v10", line, s, _STYLING_DETAIL["er", ":::"])
            s = re.sub(r":::[\w-]+", "", s)
        m = _ER_ENTITY_OPEN.match(s)
        if m:
            ent = ensure(m.group("name"), line)
            if m.group("alias"):
                ent.alias = m.group("alias")
            rest = m.group("rest").strip()
            if rest.endswith("}"):
                continue
            current = ent
            continue
        m = _ER_RELATION.match(s)
        if m:
            ensure(m.group("a"), line)
            ensure(m.group("b"), line)
            er.relations.append(ErRelation(a=m.group("a").strip('"'), b=m.group("b").strip('"'),
                                           cardinality=m.group("card"),
                                           label=(m.group("label") or "").strip().strip('"'), line=line))
            continue
        if re.fullmatch(r'[^\s"{}]+', s):
            ensure(s, line)
            continue
        fig.error(line, f"cannot read the statement {s!r}")
    return er


