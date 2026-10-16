"""ASCII figures of the parse model: the boxes, lines and labels of a `text figure`
fence (TASK 124)."""

from __future__ import annotations

import re
import unicodedata
from bisect import bisect_left, bisect_right
from collections import defaultdict
from typing import Optional

from .document import Fence
from .figure import AsciiBlock, AsciiBox
from .labels import _EMOJI_PRESENTATION, char_widths, display_width
from .preprocessing import _body_lines

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


def _turns_down(grid: _Grid, r: int, row: list, k: int, memo: dict) -> bool:
    """True when the horizontal run after cell *k* of row *r* ends in a corner whose stroke runs
    down to a down arrowhead: `──┐` or `--+` over `│` lines and `▼` or a lone `v`."""
    j = k + 1
    while j < len(row) and row[j][1] in _BOX_HORIZONTAL:
        j += 1
    return j > k + 1 and j < len(row) and row[j][1] in _BOX_TOP_RIGHT \
        and _arrow_below(grid, r, row[j][0], memo)


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
    flow goes on. Four forms count:

    - the path ends under the stroke in `┘` or `+`, `───┘` or `---+`, and the flow goes on along
      the upper path;
    - the stroke meets the path in `┴` or `+`, and the path goes on to an arrowhead,
      `──┴──▶ deploy` or `--+--> deploy`;
    - the path ends in `┤`, `──┤`, and the stroke goes on down to an arrowhead below;
    - the stroke meets the path in `┴` or `+`, and the path goes on to a corner that turns down
      to an arrowhead, `──┴──┐` or `--+--+` over a stroke to `▼` or `v` (TASK 110 R3).

    A fan-out's branch ends in an element, `└──▶ orders`, so a fan-out holds a fork and no join.
    In forms 2 and 4, a `+` with a stroke below it starts branches, as `┼` does: the trunk of
    a fan-out whose branches leave above and below it is no join. The bottom border of a
    box-drawing grid, `└────┴────┘`, closes a frame and is no join."""
    out, memo = [], {}
    for r, row in enumerate(grid.cells):
        for k, (col, ch) in enumerate(row):
            if ch not in _JOIN_CANDIDATES or k == 0 or col in grid.consumed[r] \
                    or row[k - 1][1] not in _BOX_HORIZONTAL or not grid.joins(r - 1, col, False):
                continue
            goes_on = k + 1 < len(row) and row[k + 1][1] in _BOX_HORIZONTAL
            merges = ch in _MERGE_GLYPHS and goes_on \
                and (_arrow_after(row, k) or _turns_down(grid, r, row, k, memo)) \
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


