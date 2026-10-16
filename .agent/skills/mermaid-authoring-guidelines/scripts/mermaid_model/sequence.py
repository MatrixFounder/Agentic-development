"""Sequence-diagram parser of the parse model (TASK 124)."""

from __future__ import annotations

import re
from typing import Optional

from .figure import Block, Figure, Message, Note, Participant, Sequence
from .hazards import _strip_entities


_SEQ_ARROWS = r"<<-->>|<<->>|-->>|->>|-->|->|--x|-x|--\)|-\)|--?\|[\\/]|[\\/]\|--?"
_SEQ_MESSAGE = re.compile(
    r"^(?P<src>[^:]*?)\s*(?P<arrow>" + _SEQ_ARROWS + r")\s*(?P<act>[+-]?)\s*(?P<dst>[^:]*?)\s*:(?P<text>.*)$")
_SEQ_PARTICIPANT = re.compile(
    r"^(?:(?P<create>create)\s+)?(?P<kind>participant|actor)\s+(?P<rest>.+)$")
_SEQ_NOTE = re.compile(
    r"^note\s+(?P<pos>left of|right of|over)\s+(?P<who>[^:]+?)\s*:(?P<text>.*)$", re.IGNORECASE)
_SEQ_BLOCK = re.compile(r"^(?P<kw>loop|alt|opt|par|par_over|critical|break|rect)\b\s*(?P<label>.*)$")
_SEQ_CONT = re.compile(r"^(?P<kw>else|and|option)\b\s*(?P<label>.*)$")
_SEQ_BOX = re.compile(r"^box\b\s*(?P<rest>.*)$")
_COLOR_PREFIX = re.compile(r"^(?:rgba?\([^)]*\)|hsla?\([^)]*\)|#[0-9A-Fa-f]{3,8}\b|transparent\b)\s*")
_HEX_COLOUR_START = re.compile(r"^\s*#[0-9A-Fa-f]{3,8}\b")


def _seq_message(s: str):
    """`_SEQ_MESSAGE.match(s)`, skipped on a line without `:`. A message needs the colon, and the
    two lazy groups backtrack quadratically on a long line of arrows that has none."""
    return _SEQ_MESSAGE.match(s) if ":" in s else None


def _seq_text_hazards(fig: Figure, text: str, line: int, where: str) -> None:
    plain = _strip_entities(text)
    if ";" in plain:
        fig.hazard("seq-semicolon", line, text, f"`;` in a {where} ends the statement")
    if "#" in plain:
        fig.hazard("seq-hash", line, text, f"`#` in a {where} cuts the text there")
    if "\\n" in text:
        fig.hazard("literal-newline", line, text, f"a {where} prints `\\n` as text")


def _parse_sequence(rows: list, fig: Figure) -> Sequence:
    seq = Sequence(participants=[], messages=[], notes=[], blocks=[], autonumber=False)
    by_id: dict = {}
    open_blocks: list = []  # [kind, label, start]
    current_box: Optional[str] = None
    active: dict = {}

    def add_participant(pid: str, line: int, label: str = "", kind: str = "participant",
                        declared: bool = True) -> None:
        if pid in by_id:
            if declared:
                # a later declaration keeps the place of the first use and sets the name and the
                # kind mermaid draws (addActor overwrites the description)
                p = by_id[pid]
                p.declared = True
                p.kind = kind
                if label:
                    p.label = label
            return
        if pid == "end":
            fig.hazard("end-id", line, pid)
        p = Participant(id=pid, label=label, kind=kind, line=line, box=current_box, declared=declared)
        by_id[pid] = p
        seq.participants.append(p)

    for line, text in rows[1:]:
        s = text.strip()
        if not s:
            continue
        low = s.lower()
        if re.match(r"(classDef|class|style)\b", s):
            fig.hazard("seq-styling", line, s)
            continue
        m = _SEQ_PARTICIPANT.match(s)
        if m:
            rest = m.group("rest").strip()
            if "@{" in rest:
                fig.hazard("shape-at", line, rest, "participant metadata needs mermaid 11.11")
                rest = rest.split("@{")[0].strip()
            am = re.match(r"^(?P<id>.+?)\s+as\s+(?P<alias>.+)$", rest)
            pid, alias = (am.group("id").strip(), am.group("alias").strip()) if am else (rest, "")
            if alias:
                _seq_text_hazards(fig, alias, line, "participant alias")
            add_participant(pid, line, alias, m.group("kind"))
            continue
        if low.startswith("destroy "):
            continue
        m = _SEQ_BOX.match(s)
        if m and not _seq_message(s):
            rest = m.group("rest")
            cm = _COLOR_PREFIX.match(rest)
            title = rest[cm.end():].strip() if cm else rest.strip()
            if _HEX_COLOUR_START.match(rest):
                fig.hazard("seq-hex-colour", line, s, "a hex colour after `box` drops the box fill and "
                           "its title in mermaid 10.9 and 11.17")
            open_blocks.append(["box", title, line, cm.group(0).strip() if cm else ""])
            current_box = title or "box"
            continue
        m = _SEQ_BLOCK.match(s)
        if m and not _seq_message(s):
            if m.group("kw") == "rect" and _HEX_COLOUR_START.match(m.group("label")):
                fig.hazard("seq-hex-colour", line, s, "a hex colour after `rect` draws a black rect over "
                           "the messages in mermaid 10.9 and a theme colour in 11.17")
            label = m.group("label").strip()
            open_blocks.append([m.group("kw"), label, line, label if m.group("kw") == "rect" else ""])
            continue
        if _SEQ_CONT.match(s) and not _seq_message(s):
            continue
        if s == "end":
            if open_blocks:
                kind, label, start, colour = open_blocks.pop()
                seq.blocks.append(Block(kind=kind, label=label, start=start, end=line, colour=colour))
                if kind == "box":
                    current_box = None
            else:
                fig.error(line, "`end` without an open block")
            continue
        m = _SEQ_NOTE.match(s)
        if m:
            who = [w.strip() for w in m.group("who").split(",") if w.strip()]
            for w in who:
                add_participant(w, line, declared=False)
            note_text = m.group("text").strip()
            _seq_text_hazards(fig, note_text, line, "note")
            seq.notes.append(Note(over=who, position=m.group("pos").lower(), text=note_text, line=line))
            continue
        if low.startswith("autonumber"):
            seq.autonumber = "off" not in low.split()
            if re.search(r"\d+\.\d+", s):
                fig.hazard("seq-syntax-above-floor", line, s, "decimal autonumber needs mermaid 11.15")
            continue
        m = re.match(r"^(activate|deactivate)\s+(.+)$", s)
        if m:
            pid = m.group(2).strip()
            add_participant(pid, line, declared=False)
            seq.activations.append({"verb": m.group(1), "id": pid, "line": line})
            if m.group(1) == "activate":
                active[pid] = active.get(pid, 0) + 1
            elif active.get(pid, 0) <= 0:
                fig.hazard("seq-deactivate-inactive", line, s,
                           f"{pid} is not active here; mermaid stops the render")
            else:
                active[pid] -= 1
            continue
        if re.match(r"^(title|links?|properties|details)\b", s):
            continue
        m = _seq_message(s)
        if m:
            arrow = m.group("arrow")
            if "|" in arrow:
                fig.hazard("seq-syntax-above-floor", line, s, "half-arrows need mermaid 11.13")
            if arrow.startswith("<<"):
                fig.hazard("seq-syntax-above-floor", line, s,
                           f"`{arrow}` needs mermaid 11; 10.9 draws a participant named "
                           f"`{m.group('src').strip()}<<`")
            src, dst = m.group("src").strip(), m.group("dst").strip()
            if not src or not dst:
                fig.error(line, "a message without a sender or a receiver")
                continue
            add_participant(src, line, declared=False)
            add_participant(dst, line, declared=False)
            msg_text = m.group("text").strip()
            if msg_text.lower().startswith(("wrap:", "nowrap:")):
                msg_text = msg_text.split(":", 1)[1].strip()
            _seq_text_hazards(fig, msg_text, line, "message")
            act = m.group("act")
            seq.messages.append(Message(src=src, dst=dst, text=msg_text, arrow=arrow, line=line,
                                        activate=act))
            if act == "+":
                active[dst] = active.get(dst, 0) + 1
            elif act == "-":
                if active.get(src, 0) <= 0:
                    fig.hazard("seq-deactivate-inactive", line, s,
                               f"`-` deactivates {src}, which is not active; mermaid stops the render")
                else:
                    active[src] -= 1
            continue
        fig.error(line, f"cannot read the statement {s!r}")
    for kind, _label, start, _colour in open_blocks:
        fig.error(start, f"`{kind}` block has no closing `end`")
    return seq


