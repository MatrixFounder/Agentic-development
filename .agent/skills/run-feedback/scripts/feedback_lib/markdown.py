"""Fenced-code awareness for the ledger writers — ONE state machine, both ledgers.

Both ledgers are hand-maintained markdown that **documents its own format inside
itself**, in prose and in code fences. So any writer that locates a line by
pattern must know which lines are code, or it will eventually insert into an
example. That defect has now been found twice:

  * **F3** — the work-item anchor resolved inside a fenced block, so the pointer
    line was written into a code example: rendered as code, outside the real list,
    exit 0. Fixed in `ledger_backlog` in TASK 091.
  * **L-2 (iteration 3)** — `ledger_issues.insert_index_line` was still fence-blind
    a whole task later: a `## <category>` heading or a `- **<ID>** …` example line
    inside a fence was treated as the real thing, and a new defect pointer landed
    inside the fence. Same defect, sibling module, one registry apart.

That is exactly the asymmetry WI-7 is about, and the reason this module exists at
all: duplicating a state machine is how two implementations of one contract drift.
Both ledgers now consume `fenced_mask`, so a fence-handling bug can only ever be
in one place.

Scope, stated honestly: this implements the fence rules of CommonMark §4.5
(fence character, run length, info string, ≤3-space indent) — **not** a markdown
parser. Indented code blocks are handled by refusing to treat a ≥4-space-indented
line as structure at all, which is conservative in the right direction: it can
decline a line a full parser would accept, and cannot accept one a parser would
call code.
"""

from __future__ import annotations

import re

#: A fence OPENER per CommonMark §4.5: at most 3 leading spaces, then 3+ of one
#: fence character, then an info string. A line indented 4+ spaces is an indented
#: code block, not a fence.
_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*(.*)$")

#: structure (an anchor, a heading, a pointer line) is only recognized at an
#: indent a markdown renderer would not read as code
MAX_STRUCTURE_INDENT = 3


def scan(text):
    """Return ``(mask, unclosed_line)`` for *text* split on ``"\\n"``.

    ``mask[i]`` is True when line *i* must not be treated as structure — it is a
    fence delimiter itself, or content inside a fenced block. ``unclosed_line`` is
    the 1-based line number of a fence that never closes, else None.

    An unclosed fence extends to end of file, which is what CommonMark says and
    therefore what a renderer shows. Callers must keep failing closed on it; the
    line number exists so the error can say *why* rather than reporting a missing
    anchor that is plainly present.
    """
    mask = []
    fence_char = None
    fence_len = 0
    fence_line = None
    for index, line in enumerate(text.split("\n")):
        match = _FENCE_RE.match(line)
        if fence_char is None:
            if match:
                run, info = match.group(1), match.group(2)
                # an info string may not contain a backtick on a ``` fence
                if not (run[0] == "`" and "`" in info):
                    fence_char, fence_len, fence_line = run[0], len(run), index + 1
                    mask.append(True)
                    continue
            mask.append(False)
            continue
        # inside a fence: only a run of the SAME character, at least as long,
        # with no info string, closes it. Everything else is content.
        mask.append(True)
        if match:
            run, info = match.group(1), match.group(2)
            if (run[0] == fence_char and len(run) >= fence_len
                    and not info.strip()):
                fence_char, fence_len, fence_line = None, 0, None
    return mask, fence_line


def fenced_mask(text):
    """Just the mask (see ``scan``)."""
    return scan(text)[0]


def is_structure(line):
    """True when *line* is indented shallowly enough to count as structure.

    A properly seeded anchor, a heading and an index pointer all sit at column 0.
    A ≥4-space-indented copy is something a renderer shows as code, so treating it
    as live is how `doctor` came to report `anchor_present: true` for an anchor
    that renders inside an indented code block, and how a pointer line could be
    written into one (iteration 3, L-8).
    """
    stripped = line.lstrip(" ")
    if len(line) - len(stripped) > MAX_STRUCTURE_INDENT:
        return False
    # a tab is 4 columns for indentation purposes
    return not line.startswith("\t")
