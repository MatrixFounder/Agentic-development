"""State-diagram parser of the parse model (TASK 124)."""

from __future__ import annotations

import re
from typing import Optional

from .figure import Figure, Note, StateDiagram, StateNode, Transition
from .hazards import _ENTITY, _bad_tags, _printable_entity, _strip_entities
from .flowchart import _DIRECTIONS, _parse_props


_STATE_TRANSITION = re.compile(r"^(?P<src>\S+?)\s*-->\s*(?P<rest>.+)$")
_STATE_DECL = re.compile(r'^state\s+(?:"(?P<desc>[^"]*)"\s+as\s+)?(?P<id>[^\s{:<]+)\s*(?P<tail>.*)$')
_STATE_DESC = re.compile(r"^(?P<id>[^\s:]+)\s*:(?P<desc>.*)$")
_STATE_NOTE = re.compile(r"^note\s+(?P<pos>left of|right of)\s+(?P<who>[^:\s]+)\s*(?::(?P<text>.*))?$",
                         re.IGNORECASE)
_STATE_CLASS = re.compile(r"^class\s+(?P<ids>[^\s,]+(?:\s*,\s*[^\s,]+)*)\s+(?P<name>\S+)\s*$")


def _state_label_hazards(fig: Figure, label: str, line: int, where: str, quoted: bool = False) -> None:
    """Record hazards of a state label. Inside `state "…" as id` quotes, `:` and `;` are safe in
    10.9, 11.17 and 12.1 (calibration); entities, tags and `\\n` still change the text. Quotes
    around a transition label or a `id : description` text are printed as written."""
    text = label.strip()
    if not quoted and len(text) >= 2 and text[0] in "\"'" and text[-1] == text[0]:
        fig.hazard("state-label-quoted", line, label,
                   f"the quotes around a {where} are printed in mermaid 10.9, 11.17 and 12.1")
    if ":" in label and not quoted:
        fig.hazard("state-label-colon", line, label, f"`:` in a {where} is a parse error in mermaid 10.9")
    if ";" in _strip_entities(label) and not quoted:
        fig.hazard("state-label-semicolon", line, label, f"`;` in a {where} creates stray states")
    for m in _ENTITY.finditer(label):
        if not _printable_entity(m.group(1)):
            fig.hazard("state-label-entity", line, m.group(0),
                       f"`{m.group(0)}` in a {where} is read as a character code")
    if "\\n" in label:
        fig.hazard("literal-newline", line, label, f"mermaid 11.17 prints `\\n` in a {where} as text")
    for tag in _bad_tags(label):
        fig.hazard("html-tag", line, tag, where)


def _split_class_suffix(token: str):
    if ":::" in token:
        base, cls = token.split(":::", 1)
        return base, cls
    return token, ""


def _parse_state(rows: list, fig: Figure) -> StateDiagram:
    sd = StateDiagram(direction="TB", states={}, transitions=[], classdefs={}, styles=[], notes=[])
    stack: list = []
    class_uses: list = []

    def ensure(sid: str, line: int) -> Optional[StateNode]:
        if sid == "[*]":
            return None
        node = sd.states.get(sid)
        if node is None:
            node = StateNode(id=sid, label="", line=line, parent=stack[-1] if stack else None)
            sd.states[sid] = node
        elif node.parent is None and stack and sid not in stack:
            # mermaid places a state in the composite whose block mentions it (r3b, calibration)
            node.parent = stack[-1]
        return node

    k = 1
    while k < len(rows):
        line, text = rows[k]
        s = text.strip()
        k += 1
        if not s:
            continue
        if s == "}":
            if stack:
                stack.pop()
            else:
                fig.error(line, "`}` without an open composite state")
            continue
        if s == "--":
            continue
        m = re.match(r"^direction\s+(\S+)", s)
        if m:
            if not stack:
                sd.direction = _DIRECTIONS.get(m.group(1), m.group(1))
            continue
        if re.match(r"^(hide empty description|scale\b|click\b)", s):
            continue
        m = re.match(r"^classDef\s+(\S+)\s*(.*)$", s)
        if m:
            for name in m.group(1).split(","):
                sd.classdefs[name] = {"raw": m.group(2).strip(), "props": _parse_props(m.group(2)), "line": line}
            continue
        m = _STATE_CLASS.match(s) if "-->" not in s else None
        if m:
            ids = m.group("ids")
            if any(ord(ch) > 127 for ch in ids):
                fig.hazard("state-class-ids", line, s,
                           "the state lexer reads ASCII ids only: a first id with another character "
                           "is a lexical error in mermaid 10.9, 11.17 and 12.1, and a later one loses "
                           "the class; write `id:::class` on a state line")
            for sid in (x.strip() for x in ids.split(",")):
                node = ensure(sid, line)
                if node is not None and m.group("name") not in node.classes:
                    node.classes.append(m.group("name"))
                class_uses.append((m.group("name"), line))
            continue
        m = re.match(r"^style\s+(\S+)\s+(.*)$", s)
        if m:
            sd.styles.append({"target": m.group(1), "raw": m.group(2).strip(), "line": line})
            fig.hazard("state-style", line, s, "mermaid 10.9 rejects or misreads `style` in a state diagram")
            continue
        m = _STATE_NOTE.match(s)
        if m:
            who = m.group("who")
            ensure(who, line)
            if m.group("text") is not None:
                note_text = m.group("text").strip()
            else:
                parts = []
                while k < len(rows) and rows[k][1].strip().lower() != "end note":
                    parts.append(rows[k][1].strip())
                    k += 1
                k += 1
                note_text = "<br/>".join(parts)
            sd.notes.append(Note(over=[who], position=m.group("pos").lower(), text=note_text, line=line))
            continue
        m = _STATE_DECL.match(s)
        if m and "-->" not in s:
            sid, cls = _split_class_suffix(m.group("id"))
            node = ensure(sid, line)
            tail = m.group("tail").strip()
            if m.group("desc") is not None and node is not None:
                node.label = m.group("desc")
                _state_label_hazards(fig, node.label, line, "state description", quoted=True)
            if cls and node is not None:
                node.classes.append(cls)
                class_uses.append((cls, line))
            special = re.match(r"<<(choice|fork|join)>>", tail)
            if special and node is not None:
                node.kind = special.group(1)
                tail = tail[special.end():].strip()
            if tail.startswith(":") and node is not None:
                node.label = tail[1:].strip()
                _state_label_hazards(fig, node.label, line, "state description")
            elif tail.startswith("{"):
                if node is not None:
                    node.composite = True
                stack.append(sid)
            continue
        m = _STATE_TRANSITION.match(s)
        if m:
            src, src_cls = _split_class_suffix(m.group("src"))
            rest = m.group("rest")
            label = ""
            dst_part = rest
            colon = _first_label_colon(rest)
            if colon >= 0:
                dst_part, label = rest[:colon], rest[colon + 1:].strip()
            dst, dst_cls = _split_class_suffix(dst_part.strip())
            if not dst:
                fig.error(line, "a transition without a target")
                continue
            for sid, cls in ((src, src_cls), (dst, dst_cls)):
                node = ensure(sid, line)
                if cls and node is not None:
                    if cls not in node.classes:
                        node.classes.append(cls)
                    class_uses.append((cls, line))
            if label:
                _state_label_hazards(fig, label, line, "transition label")
            sd.transitions.append(Transition(src=src, dst=dst, label=label, line=line,
                                             scope=stack[-1] if stack else None))
            continue
        m = re.fullmatch(r"([^\s:{}]+):::([\w-]+)", s)
        if m:
            node = ensure(m.group(1), line)
            if node is not None and m.group(2) not in node.classes:
                node.classes.append(m.group(2))
            class_uses.append((m.group(2), line))
            continue
        m = _STATE_DESC.match(s)
        if m:
            node = ensure(m.group("id"), line)
            desc = m.group("desc").strip()
            if node is not None:
                node.label = desc if not node.label else node.label + "<br/>" + desc
            _state_label_hazards(fig, desc, line, "state description")
            continue
        if re.fullmatch(r"[^\s:{}]+", s):
            ensure(s, line)
            continue
        fig.error(line, f"cannot read the statement {s!r}")
    for sid in stack:
        fig.error(sd.states[sid].line if sid in sd.states else rows[0][0], f"composite {sid} has no closing `}}`")
    return sd


def _first_label_colon(rest: str) -> int:
    """Index of the `:` that starts a transition label, skipping `:::class` suffixes."""
    k = 0
    while k < len(rest):
        if rest.startswith(":::", k):
            k += 3
            continue
        if rest[k] == ":":
            return k
        k += 1
    return -1


def state_parent_chain(sd: StateDiagram, sid: str) -> list:
    """Return the composites that hold *sid*, innermost first."""
    chain, seen = [], set()
    node = sd.states.get(sid)
    while node is not None and node.parent and node.parent not in seen:
        seen.add(node.parent)
        chain.append(node.parent)
        node = sd.states.get(node.parent)
    return chain


