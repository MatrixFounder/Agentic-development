"""Document level of the parse model: Markdown fences found as CommonMark finds them,
the paragraphs next to a fence, and the negative-fence markers (TASK 124)."""

from __future__ import annotations

import hashlib
import re
from bisect import bisect_left
from dataclasses import dataclass, field
from typing import Optional

from .base import FIGURE_LANGS, NEGATIVE_MARKER


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


def _quote_strip(line: str) -> tuple:
    """Return `(depth, rest)`: the number of blockquote markers `>` that open *line*, and the
    line without them. A marker takes one following space; a tab after it gives
    up one column and keeps the rest as spaces (CommonMark)."""
    depth, col, rest = 0, 0, line
    while True:
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
                 "_rule_from", "_run_from")

    def __init__(self, text: str):
        self.text, self.offset, self.column, self.partial = text, 0, 0, False
        self._rule_from = None
        self._run_from = None
        self.find()

    def find(self) -> None:
        """Read the spaces and tabs at the position. A position inside the run the last scan read
        ends at the same character and column, since a tab reaches the next multiple of 4 from
        any column inside it. So a line's run is read once, however many containers take columns
        of it (TASK 110 R4.1)."""
        i, col = self.offset, self.column
        if self._run_from is not None and self._run_from <= i <= self.nn:
            i, col = self.nn, self.nn_column
        else:
            self._run_from = i
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
    paragraph needs content and, when ordered, the start number 1 (CommonMark §5.2). The caller
    passes a position indented less than 4 columns: from 4 on, the line is indented code."""
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
        self.quotes: list = []  # the stack indices of the open blockquotes, rising

    def run(self) -> None:
        for i in range(len(self.lines)):
            self.line(i)
        self.close(0, len(self.lines))

    def close(self, k: int, i: int) -> None:
        """Close the blocks from `stack[k]` on; line *i* is the first line after them."""
        while self.quotes and self.quotes[-1] >= k:
            self.quotes.pop()
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
        if blk.kind == "quote":
            self.quotes.append(len(self.stack))
        if blk.kind:
            self.stack.append(blk)

    def blank_stop(self, k: int) -> int:
        """The number of open blocks that a line with nothing left to read after `stack[k - 1]`
        continues. Each block from `stack[k]` on takes such a line as `line` reads it, up to the
        first one that cannot: a blockquote, a paragraph, an HTML block of kind 6 or 7, or an
        item that holds no block yet. Only the last block can be one of the last three, since
        `push` marks every item it opens a block in (TASK 110 R4.2)."""
        stack = self.stack
        j = bisect_left(self.quotes, k)
        stop = self.quotes[j] if j < len(self.quotes) else len(stack)
        tip = len(stack) - 1
        if k <= tip < stop:
            blk = stack[tip]
            if blk.kind == "para" or (blk.kind == "html" and blk.html >= 6) \
                    or (blk.kind == "item" and not blk.child):
                stop = tip
        return stop

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
            if ln.blank and ln.offset == len(ln.text):
                matched = self.blank_stop(matched)  # nothing left to read on the line
                break
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


