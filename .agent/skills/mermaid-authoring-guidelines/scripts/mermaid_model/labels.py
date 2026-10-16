"""Labels of the parse model: label text, its lines and its width (TASK 124)."""

from __future__ import annotations

import html
import re
import unicodedata

from .hazards import _ENTITY


_BR = re.compile(r"<br\s*/?>|\\n", re.IGNORECASE)
_ANY_TAG = re.compile(r"</?[A-Za-z][^<>]*>")
_MD_EMPHASIS = re.compile(r"(\*\*|__|\*|_)(?=\S)(.+?)(?<=\S)\1")


def _decode_entities(text: str) -> str:
    def repl(m: re.Match) -> str:
        name = m.group(1)
        if name.isdigit():
            try:
                return chr(int(name))
            except (ValueError, OverflowError):
                return m.group(0)
        return html.unescape("&" + name + ";")
    return html.unescape(_ENTITY.sub(repl, text))


def label_lines(label: str) -> list:
    """Split a label at `<br/>`, `<br>` and `\\n`, strip tags (`<small>`, `<b>`, `<i>`) and
    entities (`#quot;` and the like), and return the visible lines."""
    if not label:
        return []
    text = label.strip()
    if len(text) >= 2 and text.startswith("`") and text.endswith("`"):
        text = text[1:-1]
        text = _MD_EMPHASIS.sub(lambda m: m.group(2), text)
    parts = []
    for chunk in text.split("\n"):
        parts.extend(_BR.split(chunk))
    out = []
    for part in parts:
        visible = _decode_entities(_ANY_TAG.sub("", part)).strip()
        if visible:
            out.append(visible)
    return out


def word_count(line: str) -> int:
    """Count whitespace-separated tokens. Language-independent by construction (L1)."""
    return len([t for t in re.split(r"\s+", line.strip()) if t])


def char_count(line: str) -> int:
    """Count the characters of one visible label line (TASK D25: limits are characters)."""
    return len(line)


_EMOJI_PRESENTATION = "\ufe0f"  # VS16: the character before it draws as a two-column emoji


def char_widths(text: str) -> list:
    """Return the monospace display width of each character of *text*: East Asian Wide and
    Fullwidth count 2, marks and format characters 0, a tab runs to the next multiple of 8.
    VS16 counts 1 after a one-column character, so `⚠️` takes two columns as viewers draw it."""
    widths, col = [], 0
    for ch in text:
        if ch == "\t":
            w = 8 - col % 8
        elif ch == _EMOJI_PRESENTATION:
            w = 1 if widths and widths[-1] == 1 else 0
        elif unicodedata.combining(ch) or unicodedata.category(ch) in ("Mn", "Me", "Cf"):
            w = 0
        elif unicodedata.east_asian_width(ch) in ("W", "F"):
            w = 2
        else:
            w = 1
        widths.append(w)
        col += w
    return widths


def display_width(text: str) -> int:
    """Return the monospace display width of *text* (see `char_widths`)."""
    return sum(char_widths(text))


