#!/usr/bin/env python3
"""Parse model for the figures of a Markdown document (TASK 108, R6.1).

One module reads figures for three callers: `lint_mermaid.py`, `render_check.py` and the eval
grader. Each caller imports the dataclasses and functions below; none parses Mermaid on its own.

Scope of the parser. It reads the subset of Mermaid syntax that the skill's references license,
plus the constructs the lint must detect as hazards. It is not a Mermaid validator: a figure the
parser accepts may still fail to render, and `render_check.py` reports that.

Two lists on a Figure carry what the parser saw besides the structure:

* `hazards` — source constructs that the pinned renderers (10.9.8, 11.17.2, 12.1.0) reject,
  misread or change without a diagnostic, each with a `code` the lint maps to a rule;
* `parse_errors` — statements the parser could not read. An entry with `"internal": True` means
  the parser itself failed; the lint treats that as a broken instrument (TASK D20, exit 2).

Figures of a document: every `mermaid` fence and every `text figure` fence (FIGURE_LANGS,
TASK R2.5), found as CommonMark finds fences (`_scan`). A fence inside a blockquote, a GitHub
alert or a list item counts too, its opener on a list marker line included; its body loses the
container's markers and indent. A mermaid fence whose last body line is `%% negative: <names>`
shows a defect on purpose (`Fence.negative`, TASK R9.4). The marker counts only in a document
that `negative_allowed` accepts: the skill's references and test fixtures.

Every line number is a 1-based line of the file the figure came from.

Standard library only.
"""

from __future__ import annotations

import hashlib
import html
import html.entities
import json
import re
import unicodedata
from bisect import bisect_left, bisect_right
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).resolve().parent.parent
NOTATION_PATH = SKILL_DIR / "assets" / "notation.json"

#: Fence specs the model extracts by default (TASK R2.5, R6.1). A spec is the first word of the
#: info string, or that word and a marker token: `text figure` matches a fence whose info string
#: starts with `text` and holds the token `figure` later. A plain `text` fence is a listing, a
#: log or command output, never a figure. A caller that wants every `text` fence passes `text`.
FIGURE_LANGS = ("mermaid", "text figure")

#: Render check names a negative-fence marker may name (TASK R9.4). `render_check.py` evaluates
#: them; the lint accepts them in a marker and leaves them to the render check.
RENDER_CHECK_NAMES = ("crossings", "edges_through_nodes", "title_crossings",
                      "edges_through_labels", "label_overlaps", "clipped_labels", "legibility",
                      "contrast", "gantt_overflow")

#: The negative-fence marker: a Mermaid comment `%% negative: <names>`, the last body line of a
#: fence that shows a defect on purpose. Names are comma-separated.
NEGATIVE_MARKER = re.compile(r"^[ \t]*%%[ \t]*negative:(?P<names>.*)$")

#: The directories whose documents may show a defect on purpose: the skill's references and its
#: test fixtures. Anywhere else a marker would let one comment line silence the lint gate.
NEGATIVE_ROOTS = (SKILL_DIR / "references", SKILL_DIR / "scripts" / "tests" / "fixtures")


def negative_allowed(path) -> bool:
    """True when *path* names an existing file under NEGATIVE_ROOTS, symlinks resolved.

    The lint and the render check honour a `%% negative:` marker only in such a file. A
    pseudo-path such as `<text>` names no file and is never allowed."""
    try:
        resolved = Path(path).resolve()
        if not resolved.is_file():
            return False
    except (OSError, RuntimeError, ValueError, TypeError):
        return False
    for root in NEGATIVE_ROOTS:
        try:
            resolved.relative_to(Path(root).resolve())
            return True
        except (OSError, RuntimeError, ValueError):
            continue
    return False


def load_notation(path: Optional[Path] = None) -> dict:
    """Return `assets/notation.json` as a dict. The single source of every threshold."""
    with open(path or NOTATION_PATH, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- document level


@dataclass
class Paragraph:
    """A block of non-blank lines next to a fence. `start`/`end` are 1-based line numbers."""

    text: str
    start: int
    end: int


@dataclass
class NegativeMarker:
    """One `%% negative: <names>` line of a mermaid fence.

    `names` holds the comma-separated names as written, stripped, empty ones dropped. `last` is
    True when the line is the last non-blank body line, which is the only place where the marker
    makes the fence negative.
    """

    names: list
    line: int
    last: bool


@dataclass
class Fence:
    """One fenced block of a Markdown document.

    `start` is the line of the opening fence, `end` the line of the closing fence (1-based).
    `body` excludes both fence lines. `lang` is the first word of the info string, lowercased;
    `info` is the whole info string. `before` is the paragraph that ends on the line directly
    above the opening fence, or the line above a single blank line; `after` is the paragraph that
    starts directly below the closing fence or below one blank line. Either is None when a heading,
    another fence or a second blank line intervenes. Caption and legend are found by these
    positions only, never by a word (TASK D13, ARCHITECTURE invariant L1).
    """

    lang: str
    start: int
    end: int
    body: str
    before: Optional[Paragraph] = None
    after: Optional[Paragraph] = None
    info: str = ""

    @property
    def body_start(self) -> int:
        """1-based document line of the first body line."""
        return self.start + 1

    @property
    def markers(self) -> list:
        """Every negative marker line of a mermaid fence, in order (see `negative_markers`)."""
        return negative_markers(self)

    @property
    def negative(self) -> Optional[NegativeMarker]:
        """The marker that makes this fence negative: the one on the last non-blank body line."""
        return next((m for m in negative_markers(self) if m.last), None)


def negative_markers(fence: Fence) -> list:
    """Return the `%% negative:` lines of a mermaid fence as NegativeMarker, in order.

    Any other fence has none: in a `text figure` fence the comment would be a visible line.
    """
    if fence.lang != "mermaid":
        return []
    rows = fence.body.split("\n")
    last = max((k for k, row in enumerate(rows) if row.strip()), default=-1)
    out = []
    for k, row in enumerate(rows):
        m = NEGATIVE_MARKER.match(row)
        if m:
            names = [n.strip() for n in m.group("names").split(",") if n.strip()]
            out.append(NegativeMarker(names=names, line=fence.body_start + k, last=k == last))
    return out


_ATX_HEADING = re.compile(r"^[ \t]{0,3}#{1,6}(?:[ \t]|$)")
_SETEXT_UNDERLINE = re.compile(r"^[ \t]{0,3}(?:=+|-+)[ \t]*$")
_THEMATIC_BREAK = re.compile(r"^[ \t]{0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$")
_COMMENT_LINE = re.compile(r"^[ \t]*<!--.*-->[ \t]*$")
_QUOTE_MARK = re.compile(r" {0,3}>")
_LIST_ITEM = re.compile(r"^(?P<indent>[ \t]*)(?P<mark>[-+*]|\d{1,9}[.)])(?P<space>[ \t]+|$)")
_TABLE_ROW = re.compile(r"^[ \t]{0,3}\|")

# CommonMark block starts (spec 0.31.2), matched at the first non-space character of a line once
# its containers are removed. `_scan` follows the parsing strategy of the spec's appendix.
_CM_FENCE = re.compile(r"(?P<fence>`{3,}|~{3,})(?P<info>.*)")
_CM_CLOSE = re.compile(r"(?P<fence>`{3,}|~{3,})[ \t]*$")
_CM_ATX = re.compile(r"#{1,6}(?:[ \t]|$)")
_CM_SETEXT = re.compile(r"(?:=+|-+)[ \t]*$")
_CM_BREAK = re.compile(r"(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$")
_CM_BULLET = re.compile(r"[-+*]")
_CM_ORDERED = re.compile(r"(?P<start>\d{1,9})[.)]")
_CM_SPECIAL = frozenset("#`~*+_=<>-0123456789")  # the first characters of every block start
_HTML_BLOCK_NAMES = (
    "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|"
    "dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h1|h2|h3|h4|h5|h6|"
    "head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|optgroup|option|"
    "p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul")
_HTML_ATTRIBUTE = (r"""(?:[ \t]+[A-Za-z_:][A-Za-z0-9_.:-]*"""
                   r"""(?:[ \t]*=[ \t]*(?:[^ \t"'=<>`\x00-\x20]+|'[^']*'|"[^"]*"))?)""")
#: The seven kinds of HTML block: (start, end). A fence inside one is text. Kinds 6 and 7 end
#: at a blank line; kind 7 cannot interrupt a paragraph.
_HTML_BLOCKS = (
    (re.compile(r"<(?:script|pre|style|textarea)(?:[ \t>]|$)", re.I),
     re.compile(r"</(?:script|pre|style|textarea)>", re.I)),
    (re.compile(r"<!--"), re.compile(r"-->")),
    (re.compile(r"<\?"), re.compile(r"\?>")),
    (re.compile(r"<![A-Za-z]"), re.compile(r">")),
    (re.compile(r"<!\[CDATA\["), re.compile(r"\]\]>")),
    (re.compile(r"</?(?:" + _HTML_BLOCK_NAMES + r")(?:[ \t>]|/>|$)", re.I), None),
    (re.compile(r"(?:<[A-Za-z][A-Za-z0-9-]*" + _HTML_ATTRIBUTE + r"*[ \t]*/?>"
                r"|</[A-Za-z][A-Za-z0-9-]*[ \t]*>)[ \t]*$"), None),
)


@dataclass
class _Span:
    """One fenced block found by `_scan` (0-based line indices)."""

    open: int
    close: int  # the closing fence line; for an unclosed fence, the first line after its body
    info: str
    indent: int  # display column of the opening fence on its line
    closed: bool = False
    body: list = field(default_factory=list)  # the body lines as CommonMark reads them

    def last(self, n: int) -> int:
        """Index of the fence's last line: the closing line, or the last body line of a fence
        that the end of its blockquote or list item ends; `n` (past the end) for a fence left
        open at the end."""
        return self.close if self.closed or self.close >= n else self.close - 1


def _quote_strip(line: str, limit: Optional[int] = None) -> tuple:
    """Return `(depth, rest)`: the number of blockquote markers `>` that open *line*, at most
    *limit*, and the line without them. A marker takes one following space; a tab after it gives
    up one column and keeps the rest as spaces (CommonMark)."""
    depth, col, rest = 0, 0, line
    while limit is None or depth < limit:
        m = _QUOTE_MARK.match(rest)
        if not m:
            break
        col += m.end()
        rest = rest[m.end():]
        if rest[:1] == " ":
            rest, col = rest[1:], col + 1
        elif rest[:1] == "\t":
            rest, col = " " * (3 - col % 4) + rest[1:], col + 1
        depth += 1
    return depth, rest


class _Line:
    """One line under the block scan of `_scan`: the scan position in characters (`offset`) and
    in display columns (`column`). A tab reaches the next multiple of 4 columns; a tab of which a
    container took some columns is `partial` (CommonMark §2.2). `find` reads the spaces and tabs
    at the position: `nn` is the index after them, `indent` their width in columns."""

    __slots__ = ("text", "offset", "column", "partial", "nn", "nn_column", "indent", "blank",
                 "_rule_from")

    def __init__(self, text: str):
        self.text, self.offset, self.column, self.partial = text, 0, 0, False
        self._rule_from = None
        self.find()

    def find(self) -> None:
        i, col = self.offset, self.column
        while i < len(self.text) and self.text[i] in " \t":
            col += 1 if self.text[i] == " " else 4 - col % 4
            i += 1
        self.nn, self.nn_column = i, col
        self.indent = col - self.column
        self.blank = i == len(self.text)

    def advance(self, count: int, columns: bool) -> None:
        """Move past *count* characters, or past *count* columns when *columns* is set."""
        while count > 0 and self.offset < len(self.text):
            if self.text[self.offset] == "\t" and columns:
                to_tab = 4 - self.column % 4
                self.partial = to_tab > count
                step = min(count, to_tab)
                self.column += step
                self.offset += 0 if self.partial else 1
                count -= step
                continue
            self.column += 4 - self.column % 4 if self.text[self.offset] == "\t" else 1
            self.partial = False
            self.offset += 1
            count -= 1

    def skip_space(self) -> None:
        self.offset, self.column, self.partial = self.nn, self.nn_column, False

    def at_space(self) -> bool:
        return self.offset < len(self.text) and self.text[self.offset] in " \t"

    def rest(self) -> str:
        """The line from the position on; the columns left of a partial tab become spaces."""
        if self.partial:
            return " " * (4 - self.column % 4) + self.text[self.offset + 1:]
        return self.text[self.offset:]

    def rule_at(self, pos: int) -> bool:
        """True when a thematic break may start at *pos*: every non-space character from there
        on is one character of `*-_`. Read once per line, so the scan of a line that opens many
        list items stays linear."""
        if self._rule_from is None:
            text = self.text.rstrip(" \t")
            k = len(text) - 1
            if k >= 0 and text[k] in "*-_":
                while k >= 0 and text[k] in (text[-1], " ", "\t"):
                    k -= 1
                self._rule_from = k + 1
            else:
                self._rule_from = len(self.text) + 1
        return pos >= self._rule_from


@dataclass
class _Block:
    """An open block of `_scan`: a container (`quote`, `item`) or a leaf (`para`, `fence`,
    `code`, `html`)."""

    kind: str
    offset: int = 0  # item: columns its lines sit past its parent's; fence: its own indent
    child: bool = False  # item: holds a block
    fence: str = ""  # fence: the characters of the opening fence
    html: int = 0  # html: the kind of HTML block, 1 to 7
    start: int = 0  # the line the block opens on
    span: Optional[_Span] = None


def _list_item(ln: _Line, interrupts: bool) -> Optional[int]:
    """Read a list marker at the position of *ln* and return the columns between the position
    and the item's content, or None when the line opens no item. An item that *interrupts* a
    paragraph needs content and, when ordered, the start number 1 (CommonMark §5.2)."""
    if ln.indent >= 4:
        return None
    m = _CM_BULLET.match(ln.text, ln.nn) or _CM_ORDERED.match(ln.text, ln.nn)
    if not m or (interrupts and m.re is _CM_ORDERED and int(m.group("start")) != 1):
        return None
    end = m.end()
    if end < len(ln.text) and ln.text[end] not in " \t":
        return None
    if interrupts and not ln.text[end:].strip(" \t"):
        return None
    marker, width = ln.indent, end - ln.nn
    ln.skip_space()
    ln.advance(width, True)
    col, off = ln.column, ln.offset
    while True:
        ln.advance(1, True)
        if ln.column - col >= 5 or not ln.at_space():
            break
    spaces = ln.column - col
    if spaces >= 5 or spaces < 1 or ln.offset >= len(ln.text):
        # content that starts with indented code, or an empty item: one column after the marker
        ln.column, ln.offset, ln.partial = col, off, False
        if ln.at_space():
            ln.advance(1, True)
        return marker + width + 1
    return marker + width + spaces


def _html_kind(text: str, pos: int, para: bool) -> int:
    """The kind of the HTML block that opens at *pos* of *text*, 1 to 7, or 0 for none. Kind 7
    cannot interrupt a paragraph (*para*)."""
    for kind, (start, _end) in enumerate(_HTML_BLOCKS, 1):
        if start.match(text, pos) and (kind < 7 or not para):
            return kind
    return 0


class _BlockScan:
    """The block scan of `_scan`, one line at a time (CommonMark spec 0.31.2, appendix "A
    parsing strategy"). Each line first continues the open blocks it can, then opens new ones."""

    def __init__(self, lines: list):
        self.lines = lines
        self.spans: list = []
        self.comments: set = set()
        self.stack: list = []  # the open blocks, outermost first; a leaf only at the end

    def run(self) -> None:
        for i in range(len(self.lines)):
            self.line(i)
        self.close(0, len(self.lines))

    def close(self, k: int, i: int) -> None:
        """Close the blocks from `stack[k]` on; line *i* is the first line after them."""
        for blk in self.stack[k:]:
            if blk.kind == "fence":
                blk.span.close = i
            elif blk.kind == "html" and blk.html == 2 and i - 1 > blk.start:
                self.comments.update(range(blk.start, i))
        del self.stack[k:]

    def push(self, blk: _Block) -> None:
        """Open *blk* inside the innermost container. A block start ends the paragraph it
        interrupts."""
        if self.stack and self.stack[-1].kind == "para":
            self.stack.pop()
        if self.stack and self.stack[-1].kind == "item":
            self.stack[-1].child = True
        if blk.kind:
            self.stack.append(blk)

    def html_line(self, blk: _Block, ln: _Line, i: int) -> None:
        """Close an HTML block of kind 1 to 5 on the line that holds its end condition."""
        end = _HTML_BLOCKS[blk.html - 1][1]
        if end is not None and end.search(ln.text, ln.offset):
            if blk.html == 2 and i > blk.start:
                self.comments.update(range(blk.start, i + 1))
            self.stack.pop()

    def line(self, i: int) -> bool:
        """Read line *i*. Return True when it lies in a fenced or an indented code block, the
        fence lines included."""
        stack, ln = self.stack, _Line(self.lines[i])
        matched = 0
        for blk in stack:
            ln.find()
            if blk.kind == "quote":
                if ln.indent >= 4 or ln.text[ln.nn:ln.nn + 1] != ">":
                    break
                ln.skip_space()
                ln.advance(1, False)
                if ln.at_space():
                    ln.advance(1, True)
            elif blk.kind == "item":
                if ln.blank and not blk.child:
                    break  # an item holds at most one blank line before its content
                if ln.indent >= blk.offset:  # a blank line keeps the columns past the item
                    ln.advance(blk.offset, True)
                elif ln.blank:
                    ln.skip_space()
                else:
                    break
            elif blk.kind == "fence":
                m = _CM_CLOSE.match(ln.text, ln.nn) if ln.indent <= 3 else None
                if m and m.group("fence")[0] == blk.fence[0] and len(m.group("fence")) >= len(blk.fence):
                    blk.span.close, blk.span.closed = i, True
                    stack.pop()
                    return True
                k = blk.offset
                while k > 0 and ln.at_space():
                    ln.advance(1, True)
                    k -= 1
            elif blk.kind == "code":
                if ln.indent >= 4:
                    ln.advance(4, True)
                elif ln.blank:
                    ln.skip_space()
                else:
                    break
            elif ln.blank and (blk.kind == "para" or blk.html >= 6):
                break
            matched += 1
        all_matched = matched == len(stack)
        container = stack[matched - 1].kind if matched else ""
        started = False  # a block start has closed the blocks this line does not continue
        while container not in ("fence", "code", "html"):
            ln.find()
            ch, at, indented = ln.text[ln.nn:ln.nn + 1], ln.nn, ln.indent >= 4
            if not indented and ch not in _CM_SPECIAL:
                ln.skip_space()
                break
            if not indented and ch == ">":
                ln.skip_space()
                ln.advance(1, False)
                if ln.at_space():
                    ln.advance(1, True)
                self.close(matched, i)
                self.push(_Block("quote", start=i))
                matched, started, container = len(stack), True, "quote"
                continue
            fence = None if indented else _CM_FENCE.match(ln.text, at)
            if fence and fence.group("fence")[0] == "`" and "`" in fence.group("info"):
                fence = None  # a backtick fence's info string holds no backtick
            if not indented and ch == "<":
                lazy = not all_matched and not started and bool(stack) and stack[-1].kind == "para"
                kind = _html_kind(ln.text, at, container == "para" or lazy)
            else:
                kind = 0
            # a thematic break, unless `---` under a paragraph makes that a setext heading
            rule = (not indented and ln.rule_at(at) and _CM_BREAK.match(ln.text, at)
                    and not (container == "para" and _CM_SETEXT.match(ln.text, at)))
            if rule or (not indented and _CM_ATX.match(ln.text, at)):
                self.close(matched, i)
                self.push(_Block(""))  # a heading or a thematic break: one line, no block left open
                return False
            if fence:
                self.close(matched, i)
                span = _Span(open=i, close=len(self.lines), info=fence.group("info").strip(),
                             indent=ln.nn_column)
                self.spans.append(span)
                self.push(_Block("fence", offset=ln.indent, fence=fence.group("fence"), start=i, span=span))
                return True
            if kind:
                self.close(matched, i)
                blk = _Block("html", html=kind, start=i)
                self.push(blk)
                self.html_line(blk, ln, i)
                return False
            if not indented and container == "para" and _CM_SETEXT.match(ln.text, at):
                stack.pop()  # the paragraph becomes a heading
                return False
            offset = None if indented else _list_item(ln, container == "para")
            if offset is not None:
                self.close(matched, i)
                self.push(_Block("item", offset=offset, start=i))
                matched, started, container = len(stack), True, "item"
                continue
            if indented and not ln.blank and not (stack and stack[-1].kind == "para"):
                ln.advance(4, True)
                self.close(matched, i)
                self.push(_Block("code", start=i))
                return True
            ln.skip_space()
            break
        tip = stack[-1] if stack else None
        if not started and not all_matched and not ln.blank and tip is not None and tip.kind == "para":
            return False  # a lazy continuation line of the paragraph
        self.close(matched, i)
        tip = stack[-1] if stack else None
        if tip is not None and tip.kind == "fence":
            tip.span.body.append(ln.rest())
        elif tip is not None and tip.kind == "html":
            self.html_line(tip, ln, i)
        elif not ln.blank and (tip is None or tip.kind not in ("para", "code")):
            self.push(_Block("para", start=i))
        return tip is not None and tip.kind in ("fence", "code")


def code_line_reader(lines: list):
    """Return a reader of *lines* for a caller that walks a document itself, as `plan_gantt.py`
    does: call it with line indices in rising order, and it returns True for a line that
    CommonMark puts in a fenced or an indented code block, fence lines included (`_scan`). A
    line the caller does not pass to it is left out of the document. A new reader starts
    outside every block, as at the top of a document."""
    return _BlockScan(lines).line


def _scan(lines: list) -> tuple:
    """Return `(spans, comments, plain)` for the lines of a document.

    The scan reads the block structure of CommonMark (`_BlockScan`): blockquotes and list items
    hold blocks, a fenced block ends at its closing fence or where its container ends, and a
    line indented 4 or more columns past its container opens an indented code block unless it
    continues a paragraph. So a fence may open on a list marker line (`1. ```mermaid`), and a
    fence, a heading or an HTML block at column 0 ends the list above it. A fence inside an HTML
    block is text.

    `spans` holds a `_Span` per fenced block. `comments` holds the indices of the lines of every
    multi-line HTML comment. `plain` holds each line without its blockquote markers, for caption
    and legend positions.
    """
    scan = _BlockScan(lines)
    scan.run()
    return scan.spans, scan.comments, [_quote_strip(line)[1] for line in lines]


def _fence_spans(lines: list) -> list:
    """Return `(open_idx, close_idx, info, indent)` for every fenced block (0-based indices).

    `close_idx == len(lines)` marks a fence left open at the end of the document; for a fence
    that the end of its blockquote or list item closes, `close_idx` is its last body line.
    `indent` is the display column of the opening fence.
    """
    n = len(lines)
    return [(s.open, s.last(n), s.info, s.indent) for s in _scan(lines)[0]]


def _is_boundary(line: str) -> bool:
    """A line that ends a caption or legend paragraph: blank, heading, rule, comment."""
    return (not line.strip() or bool(_ATX_HEADING.match(line)) or bool(_SETEXT_UNDERLINE.match(line))
            or bool(_THEMATIC_BREAK.match(line)) or bool(_COMMENT_LINE.match(line)))


def _paragraph_before(lines: list, open_idx: int, fenced: set) -> Optional[Paragraph]:
    k = open_idx - 1
    if k >= 0 and not lines[k].strip():
        k -= 1
    if k < 0 or k in fenced or _is_boundary(lines[k]):
        return None
    end = k
    while k - 1 >= 0 and (k - 1) not in fenced and not _is_boundary(lines[k - 1]):
        k -= 1
    return Paragraph(text="\n".join(x.rstrip() for x in lines[k:end + 1]), start=k + 1, end=end + 1)


def _paragraph_after(lines: list, close_idx: int, fenced: set) -> Optional[Paragraph]:
    n = len(lines)
    k = close_idx + 1
    if k < n and not lines[k].strip():
        k += 1
    if k >= n or k in fenced or _is_boundary(lines[k]):
        return None
    start = k
    while k + 1 < n and (k + 1) not in fenced and not _is_boundary(lines[k + 1]):
        k += 1
    # A paragraph followed directly by `===` or `---` is a setext heading, not a legend. After a
    # list or a table the line is a thematic break: an underline is never a lazy continuation.
    block = lines[start:k + 1]
    if k + 1 < n and _SETEXT_UNDERLINE.match(lines[k + 1]) and not any(
            _LIST_ITEM.match(x) or _TABLE_ROW.match(x) for x in block):
        return None
    return Paragraph(text="\n".join(x.rstrip() for x in block), start=start + 1, end=k + 1)


def fence_sha256(body: str) -> str:
    """The sha256 of a figure's text, one definition for every instrument (TASK R7.8).

    The UTF-8 bytes of the body lines as `extract_fences` returns them, each ended by LF. For a
    fence at column 0 these are the lines between the fence lines as written; an indented fence
    loses the fence's indent; a `.mmd` file gives its lines. `render_check.py` evidence, the
    reference fixtures, the plan-chart fixture, `render_corpus.py` and the grader all use it.
    """
    return hashlib.sha256("".join(line + "\n" for line in body.split("\n")).encode("utf-8")).hexdigest()


def normalize_text(text: str) -> str:
    """Drop a leading byte-order mark and turn CRLF and CR line ends into LF."""
    return text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")


def fence_matches(info: str, specs) -> bool:
    """True when the info string *info* matches one of *specs* (see FIGURE_LANGS).

    A spec of one word matches the first word of the info string; the empty spec matches a fence
    without an info string. A spec of several words also needs every further word as a later
    token of the info string. Words compare without case: they are markers of the fence syntax,
    not words of the document's language.
    """
    tokens = [t.lower() for t in info.split()]
    lang = tokens[0] if tokens else ""
    for spec in specs:
        words = str(spec).lower().split()
        if not words:
            if not tokens:
                return True
            continue
        if words[0] == lang and all(w in tokens[1:] for w in words[1:]):
            return True
    return False


def extract_fences(text: str, langs: tuple = FIGURE_LANGS) -> list:
    """Return every fenced block whose info string matches a spec of *langs*.

    The default reads every `mermaid` fence and every `text figure` fence (TASK R2.5); a plain
    `text` fence is not a figure. Handles backtick and tilde fences of length >= 3, an info string
    after the fence, and a closing fence of the same character and at least the same length.
    Nested fences of a longer outer fence are not figures and are skipped. Fences are found as
    CommonMark finds them (`_scan`): a fence inside a blockquote, a GitHub alert or a list item,
    its opener on the list marker line included, is read without the container's markers and
    indent, by every caller; an opener indented 4 or more columns past its container is an
    indented code block and is skipped. Caption and legend are read without blockquote markers;
    a multi-line HTML comment ends them.
    """
    lines = normalize_text(text).split("\n")
    n = len(lines)
    spans, comments, plain = _scan(lines)
    fenced = set(comments)
    for s in spans:
        fenced.update(range(s.open, min(s.last(n), n - 1) + 1))
    out = []
    for s in spans:
        if not fence_matches(s.info, langs):
            continue
        lang = s.info.split()[0].lower() if s.info.split() else ""
        last = s.last(n)
        out.append(Fence(
            lang=lang,
            start=s.open + 1,
            end=last + 1,
            body="\n".join(s.body),
            before=_paragraph_before(plain, s.open, fenced),
            after=_paragraph_after(plain, last, fenced) if last < n else None,
            info=s.info,
        ))
    return out


def figure_from_mmd(text: str) -> Fence:
    """Wrap a `.mmd` file's text as one `mermaid` fence starting at line 0 with no neighbours."""
    text = normalize_text(text)
    lines = text.splitlines()
    return Fence(lang="mermaid", start=0, end=len(lines) + 1, body=text, info="mermaid")


# --------------------------------------------------------------------------- figure level


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


# --------------------------------------------------------------------------- hazard codes

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


# --------------------------------------------------------------------------- labels


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


# --------------------------------------------------------------------------- kinds

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
#: the grammar rejects, and `zenuml`, which needs a plugin that no pinned renderer and not GitHub
#: loads.
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


# --------------------------------------------------------------------------- settings


_DIRECTIVE = re.compile(r"%%\{\s*(\w+)\s*(?::\s*([\s\S]*?))?\s*\}%%")


def _parse_directive(raw_args: str):
    """Parse an init directive body the way mermaid does: single quotes become double quotes,
    then strict JSON. Returns (dict or None, error or None)."""
    text = (raw_args or "").strip().replace("'", '"')
    if not text:
        return None, "empty directive"
    try:
        value = json.loads(text)
    except ValueError as exc:
        return None, f"not valid JSON ({exc}); mermaid ignores the whole directive"
    if not isinstance(value, dict):
        return None, "the directive is not a JSON object; mermaid ignores it"
    return value, None


class YamlError(ValueError):
    def __init__(self, line: int, message: str):
        super().__init__(message)
        self.line = line


def _yaml_scalar(text: str, line: int):
    """Parse one YAML scalar or flow collection of the subset mermaid frontmatter uses."""
    s = text.strip()
    if not s:
        return None
    if s[0] in "{[":
        value, rest = _yaml_flow(s, 0, line)
        rest_text = s[rest:].strip()
        if rest_text and not rest_text.startswith("#"):
            raise YamlError(line, f"unexpected text after a flow collection: {rest_text!r}")
        return value
    if s[0] in "\"'":
        value, end = _yaml_quoted(s, 0, line)
        rest_text = s[end:].strip()
        if rest_text and not rest_text.startswith("#"):
            raise YamlError(line, f"unexpected text after a quoted scalar: {rest_text!r}")
        return value
    # plain scalar: a comment starts at " #"
    m = re.search(r"\s#", s)
    if m:
        s = s[:m.start()].rstrip()
    if s.startswith(("%", "@", "`")):
        raise YamlError(line, f"a plain scalar cannot start with {s[0]!r}")
    if s.startswith(("&", "!")):
        rest = s.split(None, 1)[1] if len(s.split(None, 1)) > 1 else ""
        return _yaml_scalar(rest, line) if rest else None
    if s.startswith("*"):
        return s  # an alias; the subset does not resolve it
    low = s.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~"):
        return None
    if re.fullmatch(r"[-+]?\d+", s):
        return int(s)
    if re.fullmatch(r"[-+]?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?", s):
        return float(s)
    return s


def _yaml_quoted(s: str, i: int, line: int):
    q = s[i]
    j = i + 1
    out = []
    while j < len(s):
        ch = s[j]
        if q == "'" and ch == "'":
            if j + 1 < len(s) and s[j + 1] == "'":
                out.append("'")
                j += 2
                continue
            return "".join(out), j + 1
        if q == '"' and ch == "\\" and j + 1 < len(s):
            out.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(s[j + 1], s[j + 1]))
            j += 2
            continue
        if q == '"' and ch == '"':
            return "".join(out), j + 1
        out.append(ch)
        j += 1
    raise YamlError(line, "unexpected end of the line within a quoted scalar")


def _yaml_flow(s: str, i: int, line: int):
    """Parse a flow mapping or sequence starting at s[i]; return (value, next index)."""
    opener = s[i]
    closer = "}" if opener == "{" else "]"
    result = {} if opener == "{" else []
    j = i + 1
    while True:
        while j < len(s) and s[j] in " \t":
            j += 1
        if j >= len(s):
            raise YamlError(line, f"missing {closer!r} in a flow collection")
        if s[j] == closer:
            return result, j + 1
        # one entry
        if s[j] in "{[":
            item, j = _yaml_flow(s, j, line)
            key, has_value = item, False
        elif s[j] in "\"'":
            item, j = _yaml_quoted(s, j, line)
            key, has_value = item, False
        else:
            m = re.compile(r"[^,:\]\}]*(?::(?!\s)[^,:\]\}]*)*").match(s, j)
            item = m.group(0).strip()
            j = m.end()
            key, has_value = _yaml_scalar(item, line) if item else None, False
        while j < len(s) and s[j] in " \t":
            j += 1
        if opener == "{":
            if j < len(s) and s[j] == ":":
                j += 1
                while j < len(s) and s[j] in " \t":
                    j += 1
                if j < len(s) and s[j] in "{[":
                    value, j = _yaml_flow(s, j, line)
                elif j < len(s) and s[j] in "\"'":
                    value, j = _yaml_quoted(s, j, line)
                else:
                    m = re.compile(r"[^,\]\}]*").match(s, j)
                    value = _yaml_scalar(m.group(0), line)
                    j = m.end()
                has_value = True
            if not isinstance(key, (str, int, float, bool)) and key is not None:
                raise YamlError(line, "a flow mapping key must be a scalar")
            if key in result:
                raise YamlError(line, f"duplicated mapping key {key!r}")
            result[key] = value if has_value else None
        else:
            result.append(item if not isinstance(item, str) else _yaml_scalar(item, line))
        while j < len(s) and s[j] in " \t":
            j += 1
        if j < len(s) and s[j] == ",":
            j += 1
            continue
        if j < len(s) and s[j] == closer:
            return result, j + 1
        raise YamlError(line, f"expected ',' or {closer!r} in a flow collection")


_YAML_KEY = re.compile(r"""^(?P<key>"(?:[^"\\]|\\.)*"|'(?:[^']|'')*'|[^\s#'"{}\[\],&*!|>%@`][^#]*?)\s*:(?:\s+(?P<rest>.*)|\s*)$""")


def parse_yaml(text: str, first_line: int = 1):
    """Parse the YAML subset of a mermaid frontmatter: block mappings and sequences, plain and
    quoted scalars, flow collections, comments. Raises YamlError(line, message) where js-yaml
    raises: a tab in the indentation, a mapping entry indented deeper than its siblings, a line
    that is not an entry, a duplicated key, an unterminated quote."""
    rows = []
    for k, raw in enumerate(text.split("\n")):
        line = first_line + k
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        lead = raw[:len(raw) - len(raw.lstrip(" \t"))]
        if "\t" in lead:
            raise YamlError(line, "a tab character in the indentation")
        rows.append((len(lead), raw.strip(), line))
    if not rows:
        return {}
    rows = _yaml_join_continuations(rows)
    value, nxt = _yaml_block(rows, 0, rows[0][0])
    if nxt < len(rows):
        raise YamlError(rows[nxt][2], "bad indentation: the line does not belong to any block")
    return value


def _yaml_value_text(content: str) -> str:
    m = _YAML_KEY.match(content)
    if m:
        return m.group("rest") or ""
    if content.startswith("- "):
        return content[2:]
    return content


def _yaml_unclosed(text: str) -> bool:
    """True when *text* opens a quoted scalar or a flow collection that it does not close."""
    t = text.strip()
    if not t:
        return False
    if t[0] in "\"'":
        q, k = t[0], 1
        while k < len(t):
            if q == '"' and t[k] == "\\":
                k += 2
                continue
            if t[k] == q:
                if q == "'" and k + 1 < len(t) and t[k + 1] == "'":
                    k += 2
                    continue
                return False
            k += 1
        return True
    if t[0] in "{[":
        depth, quote = 0, None
        for ch in t:
            if quote:
                if ch == quote:
                    quote = None
                continue
            if ch in "\"'":
                quote = ch
            elif ch in "{[":
                depth += 1
            elif ch in "}]":
                depth -= 1
        return depth > 0
    return False


def _yaml_join_continuations(rows: list) -> list:
    """Fold a quoted scalar or a flow collection that spans lines into its first row."""
    out = []
    k = 0
    while k < len(rows):
        ind, content, line = rows[k]
        k += 1
        while _yaml_unclosed(_yaml_value_text(content)) and k < len(rows) and rows[k][0] >= ind:
            content = f"{content} {rows[k][1]}"
            k += 1
        out.append((ind, content, line))
    return out


def _yaml_block(rows: list, i: int, indent: int):
    content = rows[i][1]
    if content.startswith("- ") or content == "-":
        return _yaml_seq(rows, i, indent)
    if not _YAML_KEY.match(content):
        # a plain scalar written on the lines below its key
        parts = []
        while i < len(rows) and rows[i][0] >= indent:
            parts.append(rows[i][1])
            i += 1
        return _yaml_scalar(" ".join(parts), rows[i - 1][2]), i
    return _yaml_map(rows, i, indent)


def _yaml_value_after_key(rows: list, i: int, indent: int, rest: Optional[str], line: int):
    """Return (value, next row) for the value of a mapping key whose entry is rows[i]."""
    if rest is not None and re.fullmatch(r"[&!]\S+", rest.strip()):
        rest = None  # an anchor or a tag before a nested block
    if rest is None or not rest.strip() or rest.strip().startswith("#"):
        if i + 1 < len(rows) and rows[i + 1][0] > indent:
            return _yaml_block(rows, i + 1, rows[i + 1][0])
        if i + 1 < len(rows) and rows[i + 1][0] == indent and (
                rows[i + 1][1].startswith("- ") or rows[i + 1][1] == "-"):
            return _yaml_seq(rows, i + 1, indent)
        return None, i + 1
    stripped = rest.strip()
    if stripped[0] in "|>":
        j = i + 1
        parts = []
        while j < len(rows) and rows[j][0] > indent:
            parts.append(rows[j][1])
            j += 1
        return ("\n" if stripped[0] == "|" else " ").join(parts), j
    value = _yaml_scalar(rest, line)
    j = i + 1
    # A deeper line after a scalar continues a plain scalar, unless it reads as an entry.
    while j < len(rows) and rows[j][0] > indent:
        cont = rows[j][1]
        if _YAML_KEY.match(cont) or cont.startswith("- ") or not isinstance(value, str) \
                or stripped[0] in "\"'{[":
            raise YamlError(rows[j][2], "bad indentation of a mapping entry")
        value = f"{value} {cont}"
        j += 1
    return value, j


def _yaml_map(rows: list, i: int, indent: int):
    result = {}
    while i < len(rows):
        ind, content, line = rows[i]
        if ind < indent:
            break
        if ind > indent:
            raise YamlError(line, "bad indentation of a mapping entry")
        if content.startswith("- ") or content == "-":
            raise YamlError(line, "a sequence entry where a mapping entry was expected")
        m = _YAML_KEY.match(content)
        if not m:
            raise YamlError(line, f"can not read a block mapping entry: {content!r}")
        key = m.group("key").strip()
        if key[:1] in "\"'":
            key, _end = _yaml_quoted(key, 0, line)
        if key in result:
            raise YamlError(line, f"duplicated mapping key {key!r}")
        value, i = _yaml_value_after_key(rows, i, indent, m.group("rest"), line)
        result[key] = value
    return result, i


def _yaml_seq(rows: list, i: int, indent: int):
    items = []
    while i < len(rows) and rows[i][0] == indent and (rows[i][1].startswith("- ") or rows[i][1] == "-"):
        _ind, content, line = rows[i]
        rest = content[1:].strip()
        if not rest:
            if i + 1 < len(rows) and rows[i + 1][0] > indent:
                value, i = _yaml_block(rows, i + 1, rows[i + 1][0])
            else:
                value, i = None, i + 1
            items.append(value)
            continue
        if _YAML_KEY.match(rest) and rest[0] not in "{[\"'":
            inner = indent + (len(content) - len(rest))
            sub = [(inner, rest, line)] + rows[i + 1:]
            value, used = _yaml_map(sub, 0, inner)
            items.append(value)
            i = i + used
            continue
        items.append(_yaml_scalar(rest, line))
        i += 1
    if i < len(rows) and rows[i][0] > indent:
        raise YamlError(rows[i][2], "bad indentation of a sequence entry")
    return items, i


# --------------------------------------------------------------------------- preprocessing


def _body_lines(fence: Fence) -> list:
    base = fence.body_start
    return [[base + k, t] for k, t in enumerate(fence.body.split("\n"))]


_YAML_HEX_COMMENT = re.compile(r"^\s*([\w-]+):\s+(#[0-9A-Fa-f]{3,8})\b")


def _take_settings(rows: list, fig: Optional[Figure]) -> list:
    """Remove frontmatter, directives and `%%` comments from *rows* in place (blanked, so line
    numbers stay); record Settings on *fig*. Returns the statement rows `[line, text]`."""
    # frontmatter: the first non-blank line is `---`. Mermaid 11 reads it only from the fence's
    # first line at column 0; after a blank line or an indent, 11.17.2 fails to parse the fence.
    first = next((k for k, r in enumerate(rows) if r[1].strip()), None)
    misplaced = None
    if first is not None and rows[first][1].strip() == "---" and (first > 0 or rows[first][1][:1] in " \t"):
        misplaced = (f"line {rows[first][0]}: frontmatter must start on the fence's first line, at "
                     "column 0; after a blank line or an indent mermaid 11 fails to parse the fence")
    if first is not None and rows[first][1].strip() == "---":
        close = next((k for k in range(first + 1, len(rows)) if rows[k][1].strip() == "---"), None)
        if close is None:
            if fig is not None:
                st = Settings(raw="\n".join(r[1] for r in rows[first:]), line=rows[first][0],
                              form="frontmatter", config=None,
                              error="; ".join(x for x in (misplaced, "frontmatter has no closing --- line; "
                                                          "mermaid detects no diagram") if x))
                fig.settings_blocks.append(st)
        else:
            raw = "\n".join(r[1] for r in rows[first + 1:close])
            config, error = None, None
            try:
                data = parse_yaml(raw, rows[first + 1][0] if first + 1 < close else rows[first][0])
                if data is None:
                    data = {}
                if not isinstance(data, dict):
                    error = "frontmatter is not a YAML mapping"
                else:
                    cfg = data.get("config", {})
                    if cfg is None:
                        cfg = {}
                    if not isinstance(cfg, dict):
                        error = "frontmatter `config` is not a mapping; mermaid drops the settings"
                    else:
                        config = cfg
            except YamlError as exc:
                error = f"YAML error on line {exc.line}: {exc}"
            if error is None:
                for k in range(first + 1, close):
                    hm = _YAML_HEX_COMMENT.match(rows[k][1])
                    if hm:
                        error = (f"line {rows[k][0]}: `{hm.group(1)}: {hm.group(2)}` is a YAML comment, "
                                 "so the value is empty; quote the colour")
                        break
            error = "; ".join(x for x in (misplaced, error) if x) or None
            if fig is not None:
                fig.settings_blocks.append(Settings(raw=raw, line=rows[first][0], form="frontmatter",
                                                    config=config, error=error))
            for k in range(first, close + 1):
                rows[k][1] = ""
    # directives, possibly spanning lines
    joined = "\n".join(r[1] for r in rows)
    starts = []
    pos = 0
    for r in rows:
        starts.append(pos)
        pos += len(r[1]) + 1
    chars = list(joined)
    for m in _DIRECTIVE.finditer(joined):
        k = max(idx for idx, s in enumerate(starts) if s <= m.start())
        dtype = m.group(1)
        if dtype in ("init", "initialize") and fig is not None:
            config, error = _parse_directive(m.group(2) or "")
            fig.settings_blocks.append(Settings(raw=m.group(0), line=rows[k][0], form="directive",
                                                config=config, error=error))
        for c in range(m.start(), m.end()):
            if chars[c] != "\n":
                chars[c] = " "
    blanked = "".join(chars).split("\n")
    for k, r in enumerate(rows):
        r[1] = blanked[k]
        if r[1].lstrip().startswith("%%"):
            r[1] = ""
    return [r for r in rows if r[1].strip()]


def _take_accessibility(rows: list, fig: Figure) -> list:
    """Remove `accTitle:`, `accDescr:` and `accDescr { … }` from the statement rows; record the
    line of each in `fig.acc_lines`."""
    out = []
    k = 0
    while k < len(rows):
        line, text = rows[k]
        s = text.strip()
        m = re.match(r"accTitle\s*:\s*(.*)$", s)
        if m:
            fig.acc_title = m.group(1).strip()
            fig.acc_lines.append(line)
            k += 1
            continue
        m = re.match(r"accDescr\s*:\s*(.*)$", s)
        if m:
            fig.acc_descr = m.group(1).strip()
            fig.acc_lines.append(line)
            k += 1
            continue
        m = re.match(r"accDescr\s*\{(.*)$", s)
        if m:
            fig.acc_lines.append(line)
            parts = [m.group(1)]
            if "}" in m.group(1):
                fig.acc_descr = m.group(1).split("}")[0].strip()
                k += 1
                continue
            k += 1
            while k < len(rows) and "}" not in rows[k][1]:
                parts.append(rows[k][1].strip())
                k += 1
            if k < len(rows):
                parts.append(rows[k][1].split("}")[0].strip())
                k += 1
            fig.acc_descr = " ".join(p for p in parts if p).strip()
            continue
        out.append(rows[k])
        k += 1
    return out


def detect_kind(body: str) -> tuple:
    """Return `(kind, keyword)` from the first statement after settings and comments."""
    rows = _take_settings([[k + 1, t] for k, t in enumerate(body.split("\n"))], None)
    if not rows:
        return "unknown", ""
    keyword = diagram_keyword(rows[0][1])
    if keyword in KIND_OF_KEYWORD:
        return KIND_OF_KEYWORD[keyword], keyword
    if keyword in _known_keywords():
        return keyword, keyword
    return "unknown", keyword


# --------------------------------------------------------------------------- flowchart


_DIRECTIONS = {"TB": "TB", "TD": "TD", "BT": "BT", "LR": "LR", "RL": "RL",
               ">": "LR", "<": "RL", "^": "BT", "v": "TB"}

#: Openers tried longest first; each with its closers and shape name.
_SHAPE_OPENERS = (
    ("(((", (")))",), "other"),
    ("((", ("))",), "circle"),
    ("([", ("])",), "stadium"),
    ("(", (")",), "round"),
    ("[[", ("]]",), "subroutine"),
    ("[(", (")]",), "cylinder"),
    ("[/", ("/]", "\\]"), "other"),
    ("[\\", ("\\]", "/]"), "other"),
    ("[", ("]",), "rect"),
    ("{{", ("}}",), "hexagon"),
    ("{", ("}",), "rhombus"),
    (">", ("]",), "other"),
)

_LINK_FULL = re.compile(r"[xo<]?-{2,}[-xo>]|[xo<]?={2,}[=xo>]|[xo<]?-?\.+-[xo>]?|~{3,}")
_LINK_TEXT_START = re.compile(r"(?P<tok>[xo<]?--|[xo<]?==|[xo<]?-\.)")
_EDGE_ID_PREFIX = re.compile(r"[A-Za-z0-9_]+@(?=[-=~.<xo])")
_ID_STOP = set(" \t[](){}<>|&;,\"'")
_CLASS_NAME = re.compile(r"[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*")
_BRACKET_CHARS = set('()[]{}"')


def _split_statements(text: str) -> list:
    """Split a flowchart line at `;` outside quotes, brackets and |pipe| labels."""
    out, depth, quoted, pipe, start = [], 0, False, False, 0
    for k, ch in enumerate(text):
        if quoted:
            if ch == '"':
                quoted = False
            continue
        if ch == '"':
            quoted = True
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == "|" and depth == 0:
            pipe = not pipe
        elif ch == ";" and depth == 0 and not pipe:
            out.append(text[start:k])
            start = k + 1
    out.append(text[start:])
    return [x for x in out if x.strip()]


def _parse_props(raw: str) -> dict:
    """Parse `fill:#fff,stroke:#333,color:#000` (commas escaped as `\\,` stay in the value)."""
    props = {}
    for part in re.split(r"(?<!\\),", raw.strip().rstrip(";")):
        if ":" in part:
            key, value = part.split(":", 1)
            props[key.strip()] = value.strip().replace("\\,", ",")
    return props


class _Frame:
    """An open subgraph while its block is read."""

    def __init__(self, sid: Optional[str], title: str, line: int):
        self.sid = sid
        self.title = title
        self.line = line
        self.members: list = []
        self.children: list = []  # closed child frames, in order
        self.final_id: Optional[str] = None


class _FlowParser:
    def __init__(self, fig: Figure):
        self.fig = fig
        self.fc = Flowchart(direction="TB", nodes={}, edges=[], subgraphs={}, classdefs={},
                            styles=[], link_styles=[])
        self.stack: list = []
        self.closed_count = 0
        self.assigned: set = set()
        self.hazard_lines: set = set()
        self.class_uses: list = []  # (class name, line)
        self.style_nodes: dict = {}  # id -> line of the `style` statement that created the node

    # -- helpers
    def hazard(self, code: str, line: int, text: str, detail: str = "") -> None:
        self.fig.hazard(code, line, text, detail)
        self.hazard_lines.add(line)

    def error(self, line: int, message: str) -> None:
        if line not in self.hazard_lines:
            self.fig.error(line, message)

    def mention(self, nid: str) -> None:
        if self.stack and nid not in self.stack[-1].members:
            self.stack[-1].members.append(nid)

    def label_codes(self, label: str, line: int, where: str) -> None:
        """Record each `#n;` of a label that renders no printable character: `#1;` is read as
        character 1, so `step #1; done` shows `step  done` (flowchart.md §6)."""
        for m in _ENTITY.finditer(label):
            if not _printable_entity(m.group(1)):
                self.hazard("label-entity", line, m.group(0), f"`{m.group(0)}` in a {where} is read as a "
                                                              "character code")

    def ensure_node(self, nid: str, line: int) -> Node:
        node = self.fc.nodes.get(nid)
        if node is None:
            node = Node(id=nid, label="", shape="rect", line=line)
            self.fc.nodes[nid] = node
        return node

    # -- statements
    def run(self, rows: list) -> Flowchart:
        header_done = False
        for line, text in _join_open_quotes(rows):
            cut = _comment_start(text)
            if cut >= 0:
                self.hazard("inline-comment", line, text[cut:].strip(),
                            "`%%` after a statement is a parse error; put the comment on its own line")
                text = text[:cut]
            parts = _split_statements(text)
            if not header_done:
                parts = self.header(parts[0].strip() if parts else "", line) + parts[1:]
                header_done = True
            for stmt in parts:
                self.statement(stmt.strip(), line)
        while self.stack:
            frame = self.stack[-1]
            self.error(frame.line, "subgraph has no closing `end`")
            self.close_subgraph(frame.line)
        for sid in self.fc.subgraphs:
            popped = self.fc.nodes.pop(sid, None)
            if popped is not None and popped.classes:
                self.fc.subgraph_classes.setdefault(sid, []).extend(popped.classes)
        for sid, at in self.style_nodes.items():
            if sid not in self.fc.subgraphs:
                self.hazard("style-node", at, sid, f"no statement but `style` names `{sid}`, so mermaid "
                                                   "draws it as a node of its own")
        for node in self.fc.nodes.values():
            for sg in self.fc.subgraphs.values():
                if node.id in sg.members:
                    node.parent = sg.id
                    break
        return self.fc

    def header(self, header: str, line: int) -> list:
        """Read the direction of the header line; return the statements written after it.

        The flowchart lexer takes one direction token after the keyword: TB, TD, BT, LR, RL or
        one of `> < ^ v`, upper case. Anything else on the line fails to parse in 10.9.8 and
        11.17.2, so it is a hazard, and the text is still read for the inventory."""
        head = header.split()
        if len(head) < 2:
            return []
        direction = head[1].rstrip(";")
        if direction not in _DIRECTIONS:
            self.hazard("header-line", line, header, f"`{direction}` is not a direction; mermaid fails "
                                                     "to parse the header line")
            rest = header.split(None, 1)[1]
            # `A-->B` is a statement written in the direction's place; `td` is a mistyped direction
            return [rest] if re.search(r"[-=.~(\[{]", rest) else []
        self.fc.direction = _DIRECTIONS[direction]
        if len(head) > 2:
            self.hazard("header-line", line, header, "a statement after the direction needs `;` or a "
                                                     "line of its own; mermaid fails to parse the header line")
            return [header.split(None, 2)[2]]
        return []

    def statement(self, stmt: str, line: int) -> None:
        if not stmt:
            return
        word = stmt.split()[0]
        if stmt == "end":
            if self.stack:
                self.close_subgraph(line)
            else:
                self.error(line, "`end` without an open subgraph")
            return
        if word == "subgraph":
            self.open_subgraph(stmt[len("subgraph"):].strip(), line)
            return
        if word == "direction":
            if self.stack:
                self.hazard("subgraph-direction", line, stmt, "mermaid drops a subgraph's direction once a "
                                                              "member links outside the subgraph")
            return
        if word == "classDef":
            m = re.match(r"classDef\s+(\S+)\s*(.*)$", stmt)
            if not m:
                self.error(line, "classDef without a name")
                return
            for name in m.group(1).split(","):
                if name == "default":
                    self.hazard("classdef-default", line, stmt)
                self.fc.classdefs[name] = {"raw": m.group(2).strip(), "props": _parse_props(m.group(2)),
                                           "line": line}
            return
        if word == "class":
            m = re.match(r"class\s+(\S+)\s+(\S+)\s*$", stmt)
            if not m:
                self.error(line, "class statement needs ids and one class name")
                return
            name = m.group(2)
            for nid in m.group(1).split(","):
                if name == "animate" or name.startswith("animate"):
                    self.hazard("animate", line, stmt)
                    continue
                if nid in self.fc.subgraphs or any(f.sid == nid for f in self.stack):
                    self.fc.subgraph_classes.setdefault(nid, []).append(name)
                    self.class_uses.append((name, line))
                    continue
                # mermaid's setClass styles only vertices that exist at this statement
                node = self.fc.nodes.get(nid)
                if node is None:
                    self.hazard("class-before-node", line, stmt, f"`{nid}` is not defined above this line, "
                                                                 "so mermaid drops the class")
                    continue
                if name not in node.classes:
                    node.classes.append(name)
                self.class_uses.append((name, line))
            return
        if word == "style":
            m = re.match(r"style\s+(\S+)\s+(.*)$", stmt)
            if not m:
                self.error(line, "style statement needs an id and properties")
                return
            target = m.group(1)
            self.fc.styles.append({"target": target, "raw": m.group(2).strip(), "line": line})
            # mermaid's style statement adds the vertex when it does not exist yet
            if target not in self.fc.nodes and target not in self.fc.subgraphs \
                    and not any(f.sid == target for f in self.stack):
                self.ensure_node(target, line)
                self.style_nodes[target] = line
            return
        if word == "linkStyle":
            m = re.match(r"linkStyle\s+(\S+)\s*(.*)$", stmt)
            if not m:
                self.error(line, "linkStyle needs an index")
                return
            index = m.group(1)
            self.fc.link_styles.append({"index": index, "raw": m.group(2).strip(), "line": line})
            self.hazard("linkstyle", line, stmt, "`linkStyle` styles edges differently in 10.9.8 and "
                                                 "12.1.0")
            if index != "default":
                for part in index.split(","):
                    if part.isdigit() and int(part) >= len(self.fc.edges):
                        self.hazard("linkstyle-range", line, stmt,
                                    f"index {part} with {len(self.fc.edges)} edges defined so far")
            return
        if word == "click":
            return
        self.vertex_statement(stmt, line)

    def open_subgraph(self, rest: str, line: int) -> None:
        sid, title, quoted = None, rest, False
        m = re.match(r'^(?P<id>[^\s\[\]"]+)\s*\[(?P<title>.*)\]\s*$', rest)
        if m:
            sid, title = m.group("id"), m.group("title").strip()
        if title.startswith('"') and title.endswith('"') and len(title) >= 2:
            title, quoted = title[1:-1], True
        if m is None:
            if not re.search(r"\s", title):
                sid = title
        if not quoted:
            bad = sorted({c for c in title if c in _BRACKET_CHARS})
            if bad:
                self.hazard("label-unquoted-bracket", line, title, "subgraph title holds " + " ".join(bad))
        if re.search(r"\bdirection\s+(TB|TD|BT|LR|RL)\b", title):
            self.hazard("subgraph-direction-title", line, title)
        for tag in _bad_tags(title):
            self.hazard("html-tag", line, tag, "subgraph title")
        self.label_codes(title, line, "subgraph title")
        if sid == "end":
            self.hazard("end-id", line, rest)
        self.stack.append(_Frame(sid, title, line))

    def close_subgraph(self, line: int) -> None:
        frame = self.stack.pop()
        sid = frame.sid or f"subGraph{self.closed_count}"
        self.closed_count += 1
        frame.final_id = sid
        members = []
        for mem in frame.members:
            if mem in self.assigned or mem == sid:
                continue
            members.append(mem)
            self.assigned.add(mem)
        for child in frame.children:
            members.append(child.final_id)
            sub = self.fc.subgraphs.get(child.final_id)
            if sub is not None:
                sub.parent = sid
        self.fc.subgraphs[sid] = Subgraph(id=sid, title=frame.title, members=members, line=frame.line,
                                          auto_id=frame.sid is None)
        if self.stack:
            self.stack[-1].children.append(frame)

    # -- vertex and edge statements
    def vertex_statement(self, stmt: str, line: int) -> None:
        cur = [stmt, 0]
        group = self.read_group(cur, line)
        if group is None:
            self.error(line, f"cannot read the statement {stmt!r}")
            return
        while True:
            self.skip_ws(cur)
            if cur[1] >= len(cur[0]):
                break
            link = self.read_link(cur, line)
            if link is None:
                self.error(line, f"unexpected text {cur[0][cur[1]:]!r}")
                return
            self.skip_ws(cur)
            target = self.read_group(cur, line)
            if not target:
                self.error(line, "a link without a target node")
                return
            style, arrow, label, reverse = link
            for src in group:
                for dst in target:
                    a, b = (dst, src) if reverse else (src, dst)
                    self.fc.edges.append(Edge(src=a, dst=b, label=label, style=style, arrow=arrow, line=line))
            group = target

    @staticmethod
    def skip_ws(cur: list) -> None:
        s, p = cur
        while p < len(s) and s[p] in " \t":
            p += 1
        cur[1] = p

    def read_group(self, cur: list, line: int) -> Optional[list]:
        ids = []
        nid = self.read_node(cur, line)
        if nid is None:
            return None
        ids.append(nid)
        while True:
            save = cur[1]
            self.skip_ws(cur)
            if cur[1] < len(cur[0]) and cur[0][cur[1]] == "&":
                cur[1] += 1
                self.skip_ws(cur)
                nid = self.read_node(cur, line)
                if nid is None:
                    self.error(line, "`&` without a node")
                    return ids
                ids.append(nid)
                continue
            cur[1] = save
            return ids

    def read_id(self, cur: list) -> str:
        s, p = cur
        start = p
        while p < len(s):
            ch = s[p]
            nxt = s[p + 1] if p + 1 < len(s) else ""
            if ch in _ID_STOP or ch in ":@":
                break
            if ch == "-" and nxt in "-.>":
                break
            if ch == "=" and nxt == "=":
                break
            if ch == "~" and nxt == "~":
                break
            if ch == "." and nxt == "-":
                break
            p += 1
        cur[1] = p
        return s[start:p]

    def read_node(self, cur: list, line: int) -> Optional[str]:
        s = cur[0]
        nid = self.read_id(cur)
        if not nid:
            return None
        if nid == "end":
            self.hazard("end-id", line, s)
        node = self.ensure_node(nid, line)
        if self.style_nodes.pop(nid, None) is not None:
            node.line = line  # a `style` line above created the vertex; this line draws it
        self.mention(nid)
        p = cur[1]
        if s.startswith("@{", p):
            close = _matching_brace(s, p + 1)
            content = s[p + 2:close if close > 0 else len(s)]
            self.hazard("shape-at", line, s[p:close + 1 if close > 0 else len(s)])
            lm = re.search(r'label\s*:\s*"([^"]*)"', content)
            if lm:
                node.label = lm.group(1)
            node.shape = "other"
            cur[1] = close + 1 if close > 0 else len(s)
        else:
            self.read_shape(cur, node, line)
        p = cur[1]
        if s.startswith(":::", p):
            m = _CLASS_NAME.match(s, p + 3)
            if m:
                if m.group(0) not in node.classes:
                    node.classes.append(m.group(0))
                self.class_uses.append((m.group(0), line))
                cur[1] = m.end()
            else:
                self.error(line, "`:::` without a class name")
                cur[1] = p + 3
        return nid

    def read_shape(self, cur: list, node: Node, line: int) -> None:
        s, p = cur
        for opener, closers, shape in _SHAPE_OPENERS:
            if not s.startswith(opener, p):
                continue
            q = p + len(opener)
            if s.startswith('"', q):
                end_quote = s.find('"', q + 1)
                if end_quote < 0:
                    self.error(line, "unclosed quote in a node label")
                    cur[1] = len(s)
                    return
                after = end_quote + 1
                closer = next((c for c in closers if s.startswith(c, after)), None)
                if closer is None:
                    # a raw " inside the quoted label, or text after the closing quote
                    close_at, closer = _find_first(s, closers, after)
                    if close_at < 0:
                        continue
                    self.hazard("label-quote-inside", line, s[q:close_at],
                                "a raw \" inside a quoted label; write #quot;")
                    node.label = s[q + 1:close_at].strip().strip('"')
                    node.shape = shape
                    self.label_codes(node.label, line, "node label")
                    cur[1] = close_at + len(closer)
                    return
                node.label = s[q + 1:end_quote]
                node.shape = shape
                for tag in _bad_tags(node.label):
                    self.hazard("html-tag", line, tag, "node label")
                self.label_codes(node.label, line, "node label")
                cur[1] = after + len(closer)
                return
            close_at, closer = _find_first(s, closers, q)
            if close_at < 0:
                continue
            label = s[q:close_at]
            if opener == "[" and label[:1] in ("/", "\\"):
                self.hazard("label-leading-slash", line, label,
                            "an unquoted label that starts with / or \\ opens a shape")
            bad = sorted({c for c in label if c in _BRACKET_CHARS})
            if bad:
                self.hazard("label-unquoted-bracket", line, label, "node label holds " + " ".join(bad))
            for tag in _bad_tags(label):
                self.hazard("html-tag", line, tag, "node label")
            self.label_codes(label, line, "node label")
            node.label = label
            node.shape = shape
            cur[1] = close_at + len(closer)
            return
        if p < len(s) and s[p] in "([{>":
            self.hazard("shape-unclosed", line, s[p:], "a shape bracket that never closes")
            cur[1] = len(s)

    def read_link(self, cur: list, line: int):
        """Read a link at cur; return (style, arrow, label, reverse) or None."""
        s, p = cur
        m = _EDGE_ID_PREFIX.match(s, p)
        if m:
            self.hazard("edge-id", line, s[p:m.end()])
            p = m.end()
        label = ""
        full = _LINK_FULL.match(s, p)
        text_start = _LINK_TEXT_START.match(s, p) if not full else None
        if full:
            token = full.group(0)
            p = full.end()
            # Only a link that is complete without its last letter can lose that letter to the id:
            # `---ops` reads as `---o` + `ps`, but `--` is no link, so `--xray` is a cross head.
            if token[-1] in "ox" and _LINK_FULL.fullmatch(token[:-1]) and p < len(s) \
                    and s[p] not in " \t|" and (s[p].isalnum() or s[p] == "_"):
                self.hazard("link-head-id", line, s[full.start():p + 1],
                            f"`{token}` ends in {token[-1]!r}, so the next id loses its first letter")
        elif text_start:
            tok = text_start.group("tok")
            kind = "=" if "=" in tok else ("." if "." in tok else "-")
            p = text_start.end()
            if kind == "-":
                closing = re.compile(r"[xo<]?-{2,}[-xo>]")
            elif kind == "=":
                closing = re.compile(r"[xo<]?={2,}[=xo>]")
            else:
                closing = re.compile(r"\.+-[xo>]?")
            cm = closing.search(s, p)
            if not cm:
                return None
            raw_text = s[p:cm.start()].strip()
            if raw_text.startswith('"') and raw_text.endswith('"') and len(raw_text) >= 2:
                label = raw_text[1:-1]
                for tag in _bad_tags(label):
                    self.hazard("html-tag", line, tag, "edge label")
            else:
                label = raw_text
                if kind == "." and "." in raw_text:
                    self.hazard("edge-label-dotted-dot", line, raw_text,
                                "a `.` inside a -. text .-> label is a lexical error")
                if kind == "-" and "--" in raw_text or kind == "=" and "==" in raw_text:
                    self.hazard("edge-label-double-dash", line, raw_text,
                                "the label holds the link characters")
                for tag in _bad_tags(raw_text):
                    self.hazard("html-tag", line, tag, "edge label")
            self.label_codes(label, line, "edge label")
            token = tok.strip() + cm.group(0)
            p = cm.end()
        else:
            return None
        # pipe label
        q = p
        while q < len(s) and s[q] in " \t":
            q += 1
        if q < len(s) and s[q] == "|":
            r = q + 1
            while r < len(s) and s[r] in " \t":
                r += 1
            close = -1
            if r < len(s) and s[r] == '"':
                # a quoted pipe label may hold `|`: close after the closing quote
                end_quote = s.find('"', r + 1)
                if end_quote > 0:
                    close = s.find("|", end_quote + 1)
            if close < 0:
                close = s.find("|", q + 1)
            if close < 0:
                self.error(line, "unclosed |label|")
                return None
            raw_text = s[q + 1:close]
            stripped = raw_text.strip()
            if stripped.startswith('"') and stripped.endswith('"') and len(stripped) >= 2:
                label = stripped[1:-1]
                if '"' in label:
                    self.hazard("label-quote-inside", line, stripped, "a raw \" inside a quoted label")
                for tag in _bad_tags(label):
                    self.hazard("html-tag", line, tag, "edge label")
            else:
                label = stripped
                bad = sorted({c for c in stripped if c in _BRACKET_CHARS})
                if bad:
                    self.hazard("edge-label-bracket", line, stripped, "edge label holds " + " ".join(bad))
                for tag in _bad_tags(stripped):
                    self.hazard("html-tag", line, tag, "edge label")
            self.label_codes(label, line, "edge label")
            p = close + 1
        cur[1] = p
        style = "invisible" if "~" in token else ("thick" if "=" in token else
                                                  ("dotted" if "." in token else "solid"))
        head_start = token[0] in "<ox" and len(token) > 1 and token[1] in "-=."
        head_end = token[-1] in ">ox"
        if style == "invisible":
            arrow, reverse = "none", False
        elif head_start and head_end:
            arrow, reverse = "<->", False
        elif head_end:
            arrow, reverse = "->", False
        elif head_start:
            arrow, reverse = "->", True
        else:
            arrow, reverse = "none", False
        return style, arrow, label, reverse


def _join_open_quotes(rows: list) -> list:
    """Join a row whose quoted label stays open with the rows that close it; mermaid accepts a
    newline inside a quoted label. The joined row keeps the first row's line number."""
    out = []
    k = 0
    while k < len(rows):
        line, text = rows[k][0], rows[k][1]
        k += 1
        while text.count('"') % 2 == 1 and k < len(rows):
            text = text + "\n" + rows[k][1]
            k += 1
        out.append((line, text))
    return out


def _comment_start(text: str) -> int:
    """Index of a `%%` that starts a comment after a statement; -1 when none. A `%%` inside
    quotes, a shape bracket or a |pipe| label is label text: `A[100%% done]` renders."""
    quoted, depth, pipe = False, 0, False
    for k, ch in enumerate(text):
        if quoted:
            if ch == '"':
                quoted = False
            continue
        if ch == '"':
            quoted = True
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == "|" and depth == 0:
            pipe = not pipe
        elif depth == 0 and not pipe and text.startswith("%%", k) and text[:k].strip():
            return k
    return -1


def _find_first(s: str, closers: tuple, start: int):
    best, which = -1, None
    for c in closers:
        k = s.find(c, start)
        if k >= 0 and (best < 0 or k < best):
            best, which = k, c
    return best, which


def _matching_brace(s: str, open_idx: int) -> int:
    """Index of the `}` matching s[open_idx] == '{', skipping quoted text; -1 when unmatched."""
    depth, quoted = 0, False
    for k in range(open_idx, len(s)):
        ch = s[k]
        if quoted:
            if ch == '"':
                quoted = False
            continue
        if ch == '"':
            quoted = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return k
    return -1


def flowchart_edge_ids(fc: Flowchart) -> list:
    """Return the edge id mermaid 11.x/12.x assigns to each edge, in order: `L_<src>_<dst>_<n>`,
    where n is 0 for the first edge of a pair and the count of earlier edges of the pair plus one
    after that. Two edges of different pairs with one id crash mermaid 12.1 (r3b §2.6)."""
    ids, seen = [], {}
    for e in fc.edges:
        count = seen.get((e.src, e.dst), 0)
        counter = 0 if count == 0 else count + 1
        ids.append(f"L_{e.src}_{e.dst}_{counter}")
        seen[(e.src, e.dst)] = count + 1
    return ids


# --------------------------------------------------------------------------- sequence


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


# --------------------------------------------------------------------------- state


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


# --------------------------------------------------------------------------- gantt

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


# --------------------------------------------------------------------------- er

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


# --------------------------------------------------------------------------- other kinds

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


# --------------------------------------------------------------------------- ascii

_BOX_TOP_LEFT = set("+┌╭╔┏")
_BOX_TOP_RIGHT = set("+┐╮╗┓")
_BOX_BOTTOM_LEFT = set("+└╰╚┗")
_BOX_BOTTOM_RIGHT = set("+┘╯╝┛")
_BOX_HORIZONTAL = set("-─═━")
_BOX_VERTICAL = set("|│║┃")
#: Junctions where a connector meets a box-drawing border: from above into the top border, and
#: out of the bottom border below (`└──┬──┘`). A junction toward the inside is a grid, read as
#: before. A pure-ASCII `+` inside a border is a junction too, unless a cell side meets it
#: (`_border_end`): `+--+--+` over `|a |b |` is a grid of cells.
_TOP_JUNCTION = set("┴┷╧╨┻╩")
_BOTTOM_JUNCTION = set("┬┯╤╥┳╦")
_SIDE_JUNCTION = set("├┤┝┥┠┨╟╢╞╡┣┫╠╣")
#: Side junctions toward the inside of a box: `├` on the left side, `┤` on the right side. A row
#: from one to the other (`├────┤`) ends a layer of a stack, as `+----+` does in pure ASCII.
_LAYER_LEFT = set("├┝┠╟╞┣╠")
_LAYER_RIGHT = set("┤┥┨╢╡┫╣")
_ALIGN_CHARS = set("|+") | {chr(c) for c in range(0x2500, 0x2580)}
#: Separators between the text runs of a line. U+25B2–U+25C4 are the geometric arrowheads
#: (`▲ ▶ ▼ ◀`): `a ▶ b` holds two elements, and `──▶ gateway` names `gateway`.
_SEGMENT_SPLIT = re.compile(
    r"\s{2,}|[─-╿←-⇿⟵-⟿▲-◄]+|[|+]|<?-{2,}>?|<?={2,}>?|->|<-|\s-\s|\s>\s|\s<\s")
#: An arrow whose start column the lines of a mapping share (ascii.md §5.5), and a text column
#: after a run of spaces, such as a comment column (§5.4).
_ARROW_TOKEN = re.compile(r"<?[-=─━]+[>▶►]|[→⟶▶►]")
_COLUMN_GAP = re.compile(r"(?<=\S) {2,}(?=\S)")
_FORK_GLYPHS = set("┬┳╦╤╥+")
_JOIN_GLYPHS = set("┘╯┛╝+")  # a path ends under a stroke from above: `───┘`
_MERGE_GLYPHS = _TOP_JUNCTION | {"+"}  # a stroke from above meets a path that goes on: `──┴──▶`
_JOIN_CANDIDATES = _JOIN_GLYPHS | _MERGE_GLYPHS | _LAYER_RIGHT
_ARROWHEADS = set(">▶►→")
_DOWN_ARROWHEADS = set("▼▾↓")


def _box_strokes() -> tuple:
    """The box-drawing characters with a stroke toward the line above, and those with a stroke
    toward the line below, read from their Unicode names (`UP`, `DOWN`, `VERTICAL`)."""
    up, down = set(), set()
    for code in range(0x2500, 0x2580):
        name = unicodedata.name(chr(code), "")
        if re.search(r"\b(?:VERTICAL|UP)\b", name):
            up.add(chr(code))
        if re.search(r"\b(?:VERTICAL|DOWN)\b", name):
            down.add(chr(code))
    return up, down


_UP_STROKE, _DOWN_STROKE = _box_strokes()
_UP_STROKE |= set("|▼▾↓")  # a down arrowhead ends a line that comes from above
_DOWN_STROKE |= set("|▲▴↑")  # an up arrowhead starts a line that goes below


def _cells(text: str) -> list:
    """Return [(display column, character)] for one line."""
    out, col = [], 0
    for ch, width in zip(text, char_widths(text)):
        out.append((col, ch))
        col += width
    return out


def _segments(text: str):
    """Yield `(index, run)` for each text run of a line between `_SEGMENT_SPLIT` separators."""
    pos = 0
    for m in _SEGMENT_SPLIT.finditer(text):
        if m.start() > pos:
            yield pos, text[pos:m.start()]
        pos = m.end()
    if pos < len(text):
        yield pos, text[pos:]


def _anchors(text: str, row: list) -> set:
    """The positions where an arrow or a text column starts, as character indices and as
    display columns: an author aligns by one, a viewer by the other."""
    starts = [m.start() for m in _ARROW_TOKEN.finditer(text)] + [m.end() for m in _COLUMN_GAP.finditer(text)]
    return {("char", k) for k in starts} | {("col", row[k][0]) for k in starts}


class _Grid:
    """The cells of an ASCII figure by row and display column, with the box regions."""

    def __init__(self, cells: list, consumed: list, interior: list):
        self.cells = cells
        self.consumed = consumed  # columns of a box, its borders included, per row
        self.interior = interior  # columns of a box's side rows, per row: no stroke there joins outside
        self.index = [{col: k for k, (col, _ch) in enumerate(row)} for row in cells]

    def char(self, r: int, col: int) -> str:
        k = self.index[r].get(col) if 0 <= r < len(self.cells) else None
        return self.cells[r][k][1] if k is not None else ""

    def lone(self, r: int, col: int) -> bool:
        """True when the cell has no other character on either side: an arrowhead, not a word."""
        k, row = self.index[r][col], self.cells[r]
        return (k == 0 or not row[k - 1][1].strip()) and (k + 1 >= len(row) or not row[k + 1][1].strip())

    def joins(self, r: int, col: int, up: bool) -> bool:
        """True when the cell carries a stroke toward the line above (*up*) or below. `+` joins
        both ways; a lone `v` ends a line from above and a lone `^` starts one toward below."""
        ch = self.char(r, col)
        if not ch or col in self.interior[r]:
            return False
        if ch == "+":
            return True
        if up:
            return ch in _UP_STROKE or (ch in "vV" and self.lone(r, col))
        return ch in _DOWN_STROKE or (ch == "^" and self.lone(r, col))


def _drift(lines: list, grid: _Grid) -> list:
    """(upper line, lower line) for each pair of adjacent lines between which a vertical stroke
    outside the boxes moves by one column: its neighbour in the same column carries no stroke,
    and the cell one column aside does (ascii.md §2: models drift by one column)."""
    pairs = set()
    for r, row in enumerate(grid.cells):
        for col, ch in row:
            if col in grid.consumed[r]:
                continue
            for dr, stroke in ((-1, _UP_STROKE), (1, _DOWN_STROKE)):
                r2 = r + dr
                if ch not in stroke or not 0 <= r2 < len(grid.cells) or grid.joins(r2, col, dr > 0):
                    continue
                if grid.joins(r2, col - 1, dr > 0) or grid.joins(r2, col + 1, dr > 0):
                    pairs.add((lines[min(r, r2)][0], lines[max(r, r2)][0]))
    return sorted(pairs)


def _arrow_after(row: list, k: int) -> bool:
    """True when the horizontal run after cell *k* ends in an arrowhead: `──▶`, `-->`."""
    j = k + 1
    while j < len(row) and row[j][1] in _BOX_HORIZONTAL:
        j += 1
    return j < len(row) and row[j][1] in _ARROWHEADS


def _arrow_below(grid: _Grid, r: int, col: int, memo: dict) -> bool:
    """True when the stroke below the cell at row *r* runs down its column to a down
    arrowhead: `┤` over `▼`, or over `│` lines and then `▼` or a lone `v`. A row that ends
    before the column, or a blank row, ends the stroke: its cell is empty. *memo* maps
    (row, column) to the answer from that cell down, so the cells of one stroke are read once
    per figure."""
    path, result = [], False
    for r2 in range(r + 1, len(grid.cells)):
        if (r2, col) in memo:
            result = memo[(r2, col)]
            break
        path.append((r2, col))
        ch = grid.char(r2, col)
        if ch in _DOWN_ARROWHEADS or (ch in ("v", "V") and grid.lone(r2, col)):
            result = True
            break
        if ch not in _UP_STROKE or ch not in _DOWN_STROKE:
            break
    for cell in path:
        memo[cell] = result
    return result


def _frame_bottom(grid: _Grid, r: int, k: int) -> bool:
    """True when the `┘` at cell *k* of row *r* closes a frame: the run to its left reaches a
    `└`, and the side above that `└` goes up to a `┌`. The bottom border of a box-drawing grid
    is such a frame, and it joins no flows."""
    row = grid.cells[r]
    j = k - 1
    while j >= 0 and (row[j][1] in _BOX_HORIZONTAL or row[j][1] in _TOP_JUNCTION):
        j -= 1
    if j < 0 or row[j][1] not in _BOX_BOTTOM_LEFT or row[j][1] == "+":
        return False
    col = row[j][0]
    for r2 in range(r - 1, -1, -1):
        ch = grid.char(r2, col)
        if ch in _BOX_TOP_LEFT:
            return ch != "+"
        if ch not in _BOX_VERTICAL and ch not in _LAYER_LEFT:
            return False
    return False


def _forks(lines: list, grid: _Grid) -> list:
    """Lines holding a fork of ascii.md §5.2: a `┬` or `+` on an arrow, `──┬──▶` or `--+-->`,
    with a stroke going down from it. A tree's `├` and `+--` start at their line's indent, and a
    grid's `┬` leads to no arrowhead, so neither is a fork."""
    out = []
    for r, row in enumerate(grid.cells):
        for k, (col, ch) in enumerate(row):
            if ch not in _FORK_GLYPHS or k == 0 or col in grid.consumed[r] \
                    or row[k - 1][1] not in _BOX_HORIZONTAL or not grid.joins(r + 1, col, True):
                continue
            if _arrow_after(row, k):
                out.append(lines[r][0])
                break
    return out


def _joins(lines: list, grid: _Grid) -> list:
    """Lines holding a join of ascii.md §5.2: a path meets a stroke from the line above, and one
    flow goes on. Three forms count:

    - the path ends under the stroke in `┘` or `+`, `───┘` or `---+`, and the flow goes on along
      the upper path;
    - the stroke meets the path in `┴` or `+`, and the path goes on to an arrowhead,
      `──┴──▶ deploy` or `--+--> deploy`;
    - the path ends in `┤`, `──┤`, and the stroke goes on down to an arrowhead below.

    A fan-out's branch ends in an element, `└──▶ orders`, so a fan-out holds a fork and no join.
    In the second form, a `+` with a stroke below it starts branches, as `┼` does: the trunk of
    a fan-out whose branches leave above and below it is no join. The bottom border of a
    box-drawing grid, `└────┴────┘`, closes a frame and is no join."""
    out, memo = [], {}
    for r, row in enumerate(grid.cells):
        for k, (col, ch) in enumerate(row):
            if ch not in _JOIN_CANDIDATES or k == 0 or col in grid.consumed[r] \
                    or row[k - 1][1] not in _BOX_HORIZONTAL or not grid.joins(r - 1, col, False):
                continue
            goes_on = k + 1 < len(row) and row[k + 1][1] in _BOX_HORIZONTAL
            merges = ch in _MERGE_GLYPHS and goes_on and _arrow_after(row, k) \
                and not (ch == "+" and grid.joins(r + 1, col, True))
            if (ch in _JOIN_GLYPHS and not goes_on and (ch == "+" or not _frame_bottom(grid, r, k))) \
                    or merges \
                    or (ch in _LAYER_RIGHT and not goes_on and _arrow_below(grid, r, col, memo)):
                out.append(lines[r][0])
                break
    return out


def _parse_ascii(fence: Fence) -> AsciiBlock:
    rows = _body_lines(fence)
    lines = [(line, text) for line, text in rows]
    cells = [_cells(text) for _line, text in lines]
    block = AsciiBlock(lines=lines, widths=[display_width(t) for _l, t in lines], tabs=[], wide=[],
                       aligned=[], boxes=[], elements=[])
    anchors = [_anchors(text, row) for (_line, text), row in zip(lines, cells)]
    for r, ((line, text), row) in enumerate(zip(lines, cells)):
        if "\t" in text:
            block.tabs.append(line)
        if _EMOJI_PRESENTATION in text or any(unicodedata.east_asian_width(ch) in ("W", "F") for ch in text):
            block.wide.append(line)
        near = (anchors[r - 1] if r > 0 else set()) | (anchors[r + 1] if r + 1 < len(lines) else set())
        if any(ch in _ALIGN_CHARS for ch in text) or anchors[r] & near:
            block.aligned.append(line)
    index = [dict(row) for row in cells]  # display column -> character, per row
    cols = [[c for c, _ch in row] for row in cells]  # display columns per row, rising
    consumed = [set() for _ in lines]  # display columns of a box, borders included, per row
    interior = [set() for _ in lines]  # display columns of a box's rows between its borders
    block.boxes = _find_boxes(lines, cells, index, cols, range(len(cells)), None, consumed, interior)
    grid = _Grid(cells, consumed, interior)
    block.drift = _drift(lines, grid)
    block.forks = _forks(lines, grid)
    block.joins = _joins(lines, grid)
    for box in block.boxes:
        block.elements.append((box.top, box.text))
    for r, (line, text) in enumerate(lines):
        visible = "".join(ch if col not in consumed[r] else " " for col, ch in cells[r])
        for start, run in _segments(visible):
            word = run.strip()
            if not word or not any(ch.isalnum() for ch in word):
                continue
            if word in ("v", "V"):
                col = cells[r][start + len(run) - len(run.lstrip())][0]
                if any(grid.joins(r - 1, c, False) for c in (col - 1, col, col + 1)):
                    continue  # the arrowhead of a line from above, not an element (ascii.md §3)
            block.elements.append((line, word))
    block.elements.sort(key=lambda e: e[0])
    return block


def _find_boxes(lines: list, cells: list, index: list, cols: list, rows, frame: Optional[tuple],
                taken: list, interior: list) -> list:
    """Trace the boxes whose top-left corner lies on *rows*, then the boxes inside each of them,
    to any depth: a box drawn inside a box is an element of its own (ascii.md §1). *frame* is
    `(left, right)` of the box whose inside is searched, which bounds the columns read, or None
    for the whole figure. *taken* holds the columns of the boxes found so far per row, borders
    included; *interior* gets the columns of their rows between the borders."""
    found = []
    for r in rows:
        row = cells[r]
        inside = index[r + 1] if r + 1 < len(cells) else None
        k = 0 if frame is None else bisect_right(cols[r], frame[0])
        while k < len(row) and (frame is None or row[k][0] < frame[1]):
            col, ch = row[k]
            if ch in _BOX_TOP_LEFT and col not in taken[r]:
                j = _border_end(row, k, _TOP_JUNCTION, inside)
                if not (j < len(row) and row[j][1] in _BOX_TOP_RIGHT):
                    # the corner a connector leaves along the border line: `+------+--> db`
                    j = next((i for i in range(min(j, len(row)) - 1, k, -1) if row[i][1] == "+"), None)
                if j is not None and j - k - 1 >= 2 and (frame is None or row[j][0] < frame[1]):
                    box = _trace_box(lines, cells, index, cols, r, col, row[j][0], taken)
                    if box is not None:
                        found.append((r, box))
                        _claim_box(box, lines, cols, index, r, taken, interior)
                        k = j + 1
                    else:
                        k = j  # the corner may start the next box: `+---+------+`
                    continue
            k += 1
    out = []
    for r, box in found:
        bottom = r + box.bottom - box.top
        held = defaultdict(set)  # the box's sides, then the boxes found inside it, per row
        for k in range(r, bottom + 1):
            held[k].update((box.left, box.right))
        inner = _find_boxes(lines, cells, index, cols, range(r + 1, bottom), (box.left, box.right), held,
                            defaultdict(set))
        if inner:  # the box's own text is the first text outside the boxes it holds
            box.text = next(filter(None, (_text_between(cells[k], box.left, box.right, held[k])
                                          for k in range(r + 1, bottom))), "")
        out += [box] + inner
    return out


def _text_between(row: list, left: int, right: int, skip: set) -> str:
    """The text of *row* between the display columns *left* and *right*, the columns of *skip*
    blanked; "" when it holds no letter or digit."""
    text = "".join(" " if col in skip else ch for col, ch in row if left < col < right)
    text = text.strip(" " + "".join(_BOX_VERTICAL))
    return text if any(ch.isalnum() for ch in text) else ""


def _claim_box(box: AsciiBox, lines: list, cols: list, index: list, top_row: int, consumed: list,
               interior: list) -> None:
    """Mark the cells of *box* in *consumed*, and the cells of its rows between the borders in
    *interior*. A row whose border drifted claims one column more on each side where a side or
    a corner stands one column outside the box. A divider that drifted inward claims nothing
    beyond the box, so the cell after it keeps its first letter. *cols* holds the display
    columns of each row, rising; *index* maps them to characters per row."""
    off = set(box.ragged) | set(box.shifted)
    r = top_row
    while r < len(lines) and lines[r][0] <= box.last:
        line = lines[r][0]
        left, right = box.left, box.right
        if line in off and index[r].get(box.left - 1, "") in _BOX_EDGE:
            left -= 1
        if line in off and index[r].get(box.right + 1, "") in _BOX_EDGE:
            right += 1
        at = cols[r]
        consumed[r].update(at[bisect_left(at, left):bisect_right(at, right)])
        if line != box.top and line != box.bottom:
            interior[r] |= set(range(left, right + 1))
        r += 1


_BOX_SIDE = _BOX_VERTICAL | _SIDE_JUNCTION
#: The characters of a box's border that a drifted row may hold one column outside the box.
_BOX_EDGE = _BOX_SIDE | _BOX_TOP_LEFT | _BOX_TOP_RIGHT | _BOX_BOTTOM_LEFT | _BOX_BOTTOM_RIGHT


def _border_end(row: list, k: int, junctions: set, inside: Optional[dict] = None,
                stop: Optional[int] = None) -> int:
    """Index of the first cell after the horizontal run that starts after the corner at *k*.

    The run goes past a connector's junction of *junctions*, and past a pure-ASCII `+` that a
    horizontal stroke follows: `+-----+-----+` is one border with a junction. A `+` that a side
    on the line *inside* the box meets is the corner of a grid cell, and a `+` in the column
    *stop* is the corner the border must reach; either ends the run. A side one column aside
    meets the `+` too: a cell side that drifted by one column still ends the cell, so the
    drift shows as a ragged border (ascii.md §2). *inside* maps the display columns of that
    line to its characters."""
    j = k + 1
    while j < len(row):
        col, ch = row[j]
        if ch == "+":
            if (col == stop or j + 1 >= len(row) or row[j + 1][1] not in _BOX_HORIZONTAL
                    or (inside is not None
                        and any(inside.get(c, "") in _BOX_VERTICAL for c in (col - 1, col, col + 1)))):
                break
        elif ch not in _BOX_HORIZONTAL and ch not in junctions:
            break
        j += 1
    return j


def _trace_box(lines: list, cells: list, index: list, cols: list, top_row: int, left: int,
               right: int, taken: Optional[list] = None) -> Optional[AsciiBox]:
    """Follow the left side of a box down from its top border to its bottom border. Returns None
    when the side ends first: a fork, a join or a rule drawn with corners is no box, and its
    strokes stay connectors.

    Below the line under the top border, a side or a bottom-left corner one column off the
    top-left corner is a drifted border when the corner's column holds a blank or the drifted
    bottom border: the line goes to `shifted` and the box goes on. A bottom border whose left
    corner has a side under it is the top border of the box below. When that box is as wide or
    wider, it closes this box with no drift: a box sits on a wider one. A row from a side
    junction toward the inside to the other side (`├────┤`) ends the box as a bottom border
    does, so each layer of a stack is an element of its own. *index* maps display columns to
    characters per row, and *cols* holds them rising; *taken* holds the columns of earlier boxes
    per row, which a drift never takes."""
    taken = taken if taken is not None else [set() for _ in cells]
    box = AsciiBox(top=lines[top_row][0], bottom=0, left=left, right=right, last=lines[top_row][0])
    texts = []
    r = top_row + 1
    while r < len(lines):
        row, at = cells[r], index[r]
        under = index[r + 1] if r + 1 < len(cells) else {}
        col, ch = left, at.get(left, "")
        if ch not in _BOX_SIDE and ch not in _BOX_BOTTOM_LEFT:
            near = None
            if r > top_row + 1 and (not ch.strip() or ch in _BOX_HORIZONTAL):
                near = next((c for c in (left - 1, left + 1) if c not in taken[r]
                             and (at.get(c, "") in _BOX_SIDE or at.get(c, "") in _BOX_BOTTOM_LEFT)), None)
            if near is None:
                return None
            col, ch = near, at[near]
            box.shifted.append(lines[r][0])
        ends = _BOX_BOTTOM_RIGHT if ch in _BOX_BOTTOM_LEFT else (
            _LAYER_RIGHT if col == left and ch in _LAYER_LEFT else None)
        if ends is not None:
            k = bisect_left(cols[r], col)
            j = _border_end(row, k, _BOTTOM_JUNCTION, index[r - 1], right)
            if j - k - 1 >= 2 and j < len(row) and row[j][1] in ends:
                box.bottom = box.last = lines[r][0]
                if col <= left and row[j][0] >= right and under.get(col, "") in _BOX_SIDE:
                    box.shifted = [x for x in box.shifted if x != box.bottom]
                elif col == left and row[j][0] != right:
                    box.ragged.append(lines[r][0])
                break
            if ch in _BOX_BOTTOM_LEFT and ch != "+":
                return None
        if col == left:
            right_ch = at.get(right, "")
            if right_ch not in _BOX_SIDE and right_ch != "+":
                box.ragged.append(lines[r][0])
        if not texts:
            between = row[bisect_right(cols[r], col):bisect_left(cols[r], right)]
            inner = "".join(x for _c, x in between).strip(" " + "".join(_BOX_VERTICAL))
            if inner and any(x.isalnum() for x in inner):
                texts.append(inner.strip())
        box.last = lines[r][0]
        r += 1
    if not box.bottom:
        return None
    box.text = texts[0] if texts else ""
    return box


# --------------------------------------------------------------------------- entry points


def parse_figure(fence: Fence) -> Figure:
    """Parse one fence into a Figure. Never raises on bad input; records `parse_errors`.

    A `mermaid` fence is parsed as Mermaid. Any other fence a caller extracted (`text figure`, or
    a plain `text` fence when the caller asked for one) is read as an ASCII figure.
    """
    if fence.lang != "mermaid":
        fig = Figure(fence=fence, kind="ascii", keyword=fence.lang or "text")
        try:
            fig.ascii = _parse_ascii(fence)
        except Exception as exc:  # noqa: BLE001 — the instrument reports its own failure
            fig.parse_errors.append({"line": fence.start, "message": f"internal parser error: {exc!r}",
                                     "internal": True})
        return fig
    fig = Figure(fence=fence, kind="unknown", keyword="")
    try:
        rows = _take_settings(_body_lines(fence), fig)
        valid = [s for s in fig.settings_blocks if s.form == "directive"] or fig.settings_blocks
        fig.settings = valid[0] if valid else None
        rows = _take_accessibility(rows, fig)
        if not rows:
            # kind "unknown" with no keyword: the lint reports it as a fence no viewer renders
            return fig
        keyword = diagram_keyword(rows[0][1])
        fig.keyword = keyword
        if keyword in KIND_OF_KEYWORD:
            fig.kind = KIND_OF_KEYWORD[keyword]
        elif keyword in _known_keywords():
            fig.kind = keyword
        else:
            fig.kind = "unknown"
        if fig.kind == "flowchart":
            fig.flowchart = _FlowParser(fig).run(rows)
        elif fig.kind == "sequence":
            fig.sequence = _parse_sequence(rows, fig)
        elif fig.kind == "state":
            fig.state = _parse_state(rows, fig)
        elif fig.kind == "gantt":
            fig.gantt = _parse_gantt(rows, fig)
        elif fig.kind == "er":
            fig.er = _parse_er(rows, fig)
        elif fig.kind in OTHER_SCANNED_KINDS:
            _scan_other(rows, fig)
        if fig.kind in ACC_UNSUPPORTED_KINDS:
            for line in fig.acc_lines:
                fig.hazard("acc-unsupported", line, "accTitle / accDescr",
                           f"`accTitle` and `accDescr` stop the render of a {fig.kind} figure in "
                           "mermaid 10.9, 11.17 and 12.1")
    except Exception as exc:  # noqa: BLE001 — the instrument reports its own failure
        fig.parse_errors.append({"line": fence.start, "message": f"internal parser error: {exc!r}",
                                 "internal": True})
    return fig


def parse_document(text: str, langs: tuple = FIGURE_LANGS) -> list:
    """Return a Figure for every fence of a Markdown document that *langs* selects: by default
    every `mermaid` fence and every `text figure` fence (TASK R6.1)."""
    return [parse_figure(f) for f in extract_fences(text, langs)]


def parse_path(path, langs: tuple = FIGURE_LANGS) -> list:
    """Parse a `.md` or `.mmd` file; a `.mmd` file is one figure."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".mmd":
        return [parse_figure(figure_from_mmd(text))]
    return parse_document(text, langs)
