"""Tests for assets/notation.json and the values the prose quotes from it (TASK 108, F4).

`notation.json` holds every threshold, budget, label limit, palette, shape and settings line of the
skill. `SKILL.md` and `references/*.md` quote many of these values for the reader. A test here fails
when a quoted value differs from `notation.json`: a value changed in `notation.json` fails until the
prose follows it, and prose that drifts fails at once. Seven checks find the quotes:

1. keyed values: a backticked key of `notation.json` with a numeric value, such as `contrast_min`,
   `labels.note_chars_max`, `budgets.sequence.messages`, or a key of a settings line such as
   `wrappingWidth`. The sentence or table row that names the key states the value;
2. palette: a table row that starts with a class of a palette and quotes a style; a `classDef` line;
   the `style` line of a subgraph; the `box` and `rect` colours of a sequence; a block that names a
   palette entry and quotes a colour;
3. shapes: the shape table of `references/flowchart.md` against `shapes`;
4. settings lines: each `%%{init: ...}%%` line of a figure source and of the prose against the
   `settings` line of its kind;
5. budget tables: each row of a table with a budget column against `budgets`;
6. phrases: values that the prose states without a key, such as the label limits of SKILL.md
   Step 5, found by the phrases of PHRASES;
7. kind lists: the lists of preferred, allowed and avoided kinds that the prose copies from `kinds`.

A meta-test requires each check to find its items and to cover the entries of `notation.json` it
checks, so a parser that matches nothing fails.

Figure sources are the mermaid fences and the plain `text` listings of Mermaid source. A source
whose last non-blank line is `%% negative: <names>` shows a defect on purpose and is exempt.
Correct a quote outside a fence: an edit inside a fence changes its sha256 and needs a new render
(`test_paired_examples.py`). Standard library only; no node, no network.
"""
import json
import re
import sys
import unittest
from bisect import bisect_right
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import mermaid_model as mm  # noqa: E402

SKILL = HERE.parent.parent
NOTATION = mm.load_notation()

# --------------------------------------------------------------------------- explicit mappings

#: Palette of a prose table row or `classDef` span, by file. In a file absent here, the palette that
#: names the class applies; no two palettes share a class name today, and a class that two
#: palettes name fails in an unlisted file until it gets an entry here.
FILE_PALETTE = {
    "references/flowchart.md": "flowchart",
    "references/state.md": "state",
    "references/sequence.md": "sequence",
}

#: Kind of a settings line in the prose, by file, when the block that holds the line names no
#: `settings.<kind>` key and no "<kind> settings line".
FILE_SETTINGS = {
    "references/flowchart.md": "flowchart",
    "references/state.md": "state",
    "references/sequence.md": "sequence",
    "references/gantt.md": "gantt",
}

#: Figure kind of `mermaid_model` -> key of `settings`. The lint keeps its own map (MA-SET-06);
#: this one is written out again so that the two checks stay independent.
SETTINGS_KEY = {"flowchart": "flowchart", "state": "state", "sequence": "sequence", "er": "er",
                "gantt": "gantt", "class": "class", "requirementDiagram": "requirement"}

#: First cell of a budget-table row, lowercased, without backticks -> kind of `budgets`. A kind
#: that `budgets` does not name has no budget, and its row says "none". The kinds of
#: `kinds.avoid` have no row: a budget table lists only kinds a figure may take.
BUDGET_ROW_KIND = {
    "flowchart": "flowchart", "sequence": "sequence", "sequencediagram": "sequence",
    "state": "state", "statediagram-v2": "state", "plan chart": "gantt", "gantt": "gantt",
    "er": "er", "erdiagram": "er", "ascii": "ascii", "class": "class", "classdiagram": "class",
    "gitgraph": "gitgraph", "timeline": "timeline", "journey": "journey", "mindmap": "mindmap",
    "requirementdiagram": "requirement", "quadrantchart": "quadrant",
}

#: Shape words of the shape table of `references/flowchart.md` -> shape names of `shapes`.
SHAPE_WORDS = {"stadium": "stadium", "rounded": "round", "subroutine": "subroutine",
               "cylinder": "cylinder", "rectangle": "rect", "hexagon": "hexagon",
               "diamond": "rhombus"}

#: Sentences that state a value of their own next to a notation key: (file, key, words of the
#: sentence) -> whose value it is. An entry that matches no sentence fails.
OWN_VALUES = {
    ("references/gantt.md", "gantt.useWidth", "GitHub sets `gantt.useWidth` to 1200"):
        "GitHub's site configuration",
    ("references/renderer-facts.md", "gantt.useWidth", "as GitHub's renderer bundle sets"):
        "GitHub's site configuration",
}

_HEX = r"(#[0-9A-Fa-f]{6})"
_NODE1, _NODE2 = "labels.node_line1_chars_max", "labels.node_second_line_chars_max"
_EDGE, _PART = "labels.edge_label_chars_max", "labels.participant_chars_max"
_MSG, _MSG_LINES = "labels.sequence_message_chars_max", "labels.sequence_message_lines_max"
_NOTE, _NOTE_LINES = "labels.note_chars_max", "labels.note_lines_max"
_GANTT_LABEL, _FONT = "labels.gantt_label_chars_max", "min_effective_font_px"
_GANTT_VARS = "settings.gantt/themeVariables."
_INSTALL = "renderers.installs.{%s}."

#: Values that the prose states without naming a key: (phrase, the notation path of each group).
#: A path is dotted, `[i]` picks one value of a [soft, hard] pair, `settings.<kind>/<path>` reads
#: inside a settings line, and `{check0}`, `{check1}`, `{forward}` name the renderer tags of
#: `renderers`. Each phrase matches at least once; every match states the notation values.
PHRASES = [
    (r"(?<!takes )\b(?:a|the) (\d+) px column\b", ["column_px"]),
    (r"\b(?:least|under|below|is) (\d+) px in (?:a|the) (\d+) px column\b", [_FONT, "column_px"]),
    (r"\bat most (\d+) crossings\b", ["thresholds.max_crossings"]),
    (r"\b(\d+) edges through an? (?:node|state);", ["thresholds.max_edges_through_nodes"]),
    (r"\bmore than (\d+) nodes\b", ["structure.lr_max_nodes"]),
    (r"\ba tree of at most (\d+) elements\b", ["budgets.ascii.elements[0]"]),
    (r"\bat most (\d+) entities\b", ["budgets.er.entities[0]"]),
    (r"\btheme `(\w+)` on (?:background )?`" + _HEX + "`",
     ["renderers.dark.theme", "renderers.dark.background"]),
    (r"(?:note colours[^.`]*?[:,]|sets both:) `" + _HEX + "` on `" + _HEX + "`",
     ["settings.sequence/themeVariables.noteTextColor", "settings.sequence/themeVariables.noteBkgColor"]),
    (r"`contrast_scope` `(\w+)`", ["thresholds.contrast_scope"]),
    # label limits
    (r"\ba node label: about \w+ words, at most (\d+) characters", [_NODE1]),
    (r"\bsecond line of at most (\d+)\b", [_NODE2]),
    (r"\ban edge label: about \w+ words, at most (\d+) characters", [_EDGE]),
    (r"\ba sequence message: at most (\d+) characters per line and (\d+) lines", [_MSG, _MSG_LINES]),
    (r"\ba participant name: at most (\d+) characters", [_PART]),
    (r"\ba note: at most (\d+) characters per line, (\d+) lines", [_NOTE, _NOTE_LINES]),
    (r"\bLabel lines stay within (\d+), (\d+) and (\d+) characters", [_NODE1, _NODE2, _EDGE]),
    (r"\b(\d+)-character first line over a (\d+)-character\b", [_NODE1, _NODE2]),
    (r"\bedge label at its limit \| (\d+) \|", [_EDGE]),
    (r"\bnode first line at its limit \| (\d+) \|", [_NODE1]),
    (r"\bsecond line at its limit \| (\d+) \|", [_NODE2]),
    (r"\bevery second line at most (\d+) characters", [_NODE2]),
    (r"\bpair runs past (\d+) characters", [_EDGE]),
    (r"\bA label holds about \w+ words and at most (\d+) characters per line", [_EDGE]),
    (r"\bA state name holds about \w+ words and at most (\d+) characters", [_NODE1]),
    (r"\bLabels hold at most (\d+) characters per line", [_EDGE]),
    (r"\bstate names hold at most (\d+) characters", [_NODE1]),
    (r"\bA box name holds at most (\d+) characters", [_NODE1]),
    (r"\bA relation label holds at most (\d+) characters", [_EDGE]),
    (r"\ba quoted label of at most (\d+) characters", [_EDGE]),
    (r"\bEach participant name holds at most (\d+) characters", [_PART]),
    (r"\bA seventh participant takes the text under (\d+) px", [_FONT]),
    (r"\bEach message line holds at most (\d+) characters, in at most (\d+) lines", [_MSG, _MSG_LINES]),
    (r"\bEach note line holds at most (\d+) characters, in at most (\d+) lines", [_NOTE, _NOTE_LINES]),
    (r"\bagainst a limit of (\d+) per line", [_MSG]),
    (r"\ba note of \d+ characters against a limit of (\d+)", [_NOTE]),
    (r"\bat most (\d+) characters per message line", [_MSG]),
    (r"\blong labels broken with `<br/>`, at most (\d+) characters per line", [_MSG]),
    (r"\bthe bar label, at most (\d+) characters", [_GANTT_LABEL]),
    (r"\bat most \d+ lines of (\d+) characters", [_GANTT_LABEL]),
    (r"\bLabels: at most (\d+) characters", [_GANTT_LABEL]),
    (r"\bEach label holds at most (\d+) characters", [_GANTT_LABEL]),
    # budgets
    (r"\bsoft budget is (\d+) states and the hard budget (\d+)",
     ["budgets.state.states[0]", "budgets.state.states[1]"]),
    (r"\bAt most (\d+) participants, (\d+) messages and (\d+) phases; "
     r"never more than (\d+), (\d+) and (\d+)",
     ["budgets.sequence.participants[0]", "budgets.sequence.messages[0]",
      "budgets.sequence.phase_blocks[0]", "budgets.sequence.participants[1]",
      "budgets.sequence.messages[1]", "budgets.sequence.phase_blocks[1]"]),
    (r"\bhard budget of (\d+) nodes and (\d+) edges",
     ["budgets.flowchart.nodes[1]", "budgets.flowchart.edges[1]"]),
    (r"\bedges against a hard budget of (\d+)", ["budgets.flowchart.edges[1]"]),
    (r"\bhard budget of (\d+) bars", ["budgets.gantt.bars[1]"]),
    (r"\bat most (\d+) bars\b", ["budgets.gantt.bars[1]"]),
    # settings lines, quoted value by value
    (r"\bunder the (\d+) px wrap\b", ["settings.flowchart/flowchart.wrappingWidth"]),
    (r"\| no tag \| `" + _HEX + "` \\| `" + _HEX + "` \\|",
     [_GANTT_VARS + "taskBkgColor", _GANTT_VARS + "taskBorderColor"]),
    (r"\| `done` \| `" + _HEX + "` \\| `" + _HEX + "` \\|",
     [_GANTT_VARS + "doneTaskBkgColor", _GANTT_VARS + "doneTaskBorderColor"]),
    (r"\| `active` \| `" + _HEX + "` \\| `" + _HEX + "` \\|",
     [_GANTT_VARS + "activeTaskBkgColor", _GANTT_VARS + "activeTaskBorderColor"]),
    (r"\| `crit` \| the fill of its status \| `" + _HEX + "` \\|", [_GANTT_VARS + "critBorderColor"]),
    (r"\bA label inside a bar is `" + _HEX + "`", [_GANTT_VARS + "taskTextColor"]),
    (r"`taskTextDarkColor`, `" + _HEX + "`", [_GANTT_VARS + "taskTextDarkColor"]),
    # renderers
    (r"\bIt renders ([\d.]+\d), ([\d.]+\d) and a dark ([\d.]+\d) by default",
     [_INSTALL % "check0" + "mermaid", _INSTALL % "check1" + "mermaid", _INSTALL % "check0" + "mermaid"]),
    (r"\brendered ([\d.]+\d) \+ ([\d.]+\d) \+ dark\b",
     [_INSTALL % "check0" + "mermaid", _INSTALL % "check1" + "mermaid"]),
    (r"\| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| the check pair, as its floor \|",
     [_INSTALL % "check1" + "mermaid", _INSTALL % "check1" + "mermaid", _INSTALL % "check1" + "cli"]),
    (r"\| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| the check pair; GitHub \|",
     [_INSTALL % "check0" + "mermaid", _INSTALL % "check0" + "mermaid", _INSTALL % "check0" + "cli"]),
    (r"\| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| the forward check \|",
     [_INSTALL % "forward" + "mermaid", _INSTALL % "forward" + "mermaid", _INSTALL % "forward" + "cli"]),
    (r"\bRenders in [\w.]+ and [\d.]+ used `-w (\d+)`", ["renderers.render_width_px"]),
]

#: Least number of items each check finds in the current text. A parser that stops matching
#: drops below it; prose edits that remove quotes lower these numbers on purpose.
MINIMUM = {"keyed values": 60, "palette rows": 7, "palette lines in figures": 50,
           "palette quotes in prose": 10, "shape rows": 9, "settings lines": 25,
           "budget rows": 15}

# --------------------------------------------------------------------------- notation access


def settings_config(line):
    """The JSON object of a settings line `%%{init: {...}}%%`."""
    m = re.fullmatch(r"%%\{init:\s*(.*)\}%%", line.strip(), re.S)
    return json.loads(m.group(1))


def concrete(path, notation=None):
    """A path of PHRASES with its renderer tags filled in: `{check0}` -> `v11`."""
    renderers = (notation or NOTATION)["renderers"]
    return (path.replace("{check0}", renderers["check_pair"][0])
                .replace("{check1}", renderers["check_pair"][1])
                .replace("{forward}", renderers["forward"]))


def value_at(path, notation=None):
    """The value of `notation.json` at a path of PHRASES (see there for the syntax)."""
    n = notation or NOTATION
    path = concrete(path, n)
    node = n
    if "/" in path:
        head, path = path.split("/", 1)
        node = settings_config(value_at(head, n))
    for part in path.split("."):
        m = re.fullmatch(r"([\w-]+)(?:\[(\d+)\])?", part)
        node = node[m.group(1)]
        if m.group(2) is not None:
            node = node[int(m.group(2))]
    return node


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def numeric_index(notation=None):
    """Dotted path -> number, or (soft, hard) for a budget, for every numeric leaf of
    `notation.json` and of its settings lines (`settings.<kind>.<path inside the line>`)."""
    n = notation or NOTATION
    out = {}

    def walk(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, path + [key])
        elif _is_number(node):
            out[".".join(path)] = node
        elif isinstance(node, list) and len(node) == 2 and all(_is_number(x) for x in node):
            out[".".join(path)] = tuple(node)

    walk({k: v for k, v in n.items() if k != "settings"}, [])
    for kind, line in n["settings"].items():
        walk(settings_config(line), ["settings", kind])
    return out


INDEX = numeric_index()


def resolve_key(name):
    """{path: value} of the numeric entries that a backticked name denotes: a dotted name is the
    path or the end of a path (`flowchart.wrappingWidth` ends `settings.flowchart.flowchart.
    wrappingWidth`); a bare name is the last part of a path. A bare budget metric (`nodes`,
    `tasks`) is a plain word in prose, so a budget counts only under its `budgets.` path. A name
    whose paths hold different values is ambiguous; a sentence that states any one of them
    passes. No name is ambiguous today: `nodes` alone would be, and it is a budget metric."""
    if "." in name:
        return {p: v for p, v in INDEX.items() if p == name or p.endswith("." + name)}
    return {p: v for p, v in INDEX.items()
            if p.rsplit(".", 1)[-1] == name and not p.startswith("budgets.")}


def palettes():
    """{kind: {class: style}} of the palettes that map classes to styles."""
    return {k: v for k, v in NOTATION["palette"].items() if isinstance(v, dict)}


# --------------------------------------------------------------------------- reading the prose

_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s+)?")
_HEADING = re.compile(r"^\s{0,3}#{1,6}(?:\s|$)")
_CODE = re.compile(r"`([^`]+)`")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9`\"'(*])")
_SEPARATOR = re.compile(r"^:?-{3,}:?$")
_TOKEN = re.compile(r"[\w.#-]+")
_QUANTITY = re.compile(r"(\d+(?:\.\d+)?)(?:px|ms|x|h|s)?|(\d+(?:\.\d+)?)-[A-Za-z]+")
#: A number right after one of these words is a reference ("Step 4.5", "§8", "rule 4").
_REFERENCE = re.compile(r"(?:§\s*|\b(?:step|rule|row|figure|figures|pair|item|message|messages|"
                        r"task|mermaid|wcag)\s+)$", re.IGNORECASE)
_NUMBER_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                 "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def quantities(text):
    """The numbers a text states, as floats: digits with an optional decimal part or unit (`2px`,
    `24-character`) and the number words up to twelve. A version (`10.9.8`), a date, an id
    (`RF-18`, `N7`, `v12`), a hex colour and a number after a reference word are not numbers."""
    out = set()
    for m in _TOKEN.finditer(text):
        token = m.group(0).strip(".-")
        q = _QUANTITY.fullmatch(token)
        if q and not _REFERENCE.search(text[:m.start()]):
            out.add(float(q.group(1) or q.group(2)))
        elif token.lower() in _NUMBER_WORDS:
            out.add(float(_NUMBER_WORDS[token.lower()]))
    return out


class Block(object):
    """A unit of prose outside the fences: a table row, a list item, a paragraph or a heading.
    `text` joins its lines with one space; a list item drops its marker."""

    def __init__(self, kind, rel, parts):
        self.kind, self.rel = kind, rel
        text, starts, lines = "", [], []
        for k, (line, raw) in enumerate(parts):
            piece = _LIST_ITEM.sub("", raw, count=1) if k == 0 and kind == "item" else raw
            if text:
                text += " "
            starts.append(len(text))
            lines.append(line)
            text += piece.strip()
        self.text, self._starts, self._lines = text, starts, lines
        self.line = lines[0]

    def line_at(self, offset):
        """File line of a character offset of `text`."""
        return self._lines[bisect_right(self._starts, offset) - 1]

    def sentences(self):
        """(offset, text) of each sentence; a table row and a heading are one sentence. A sentence
        ends at `.`, `!` or `?` before a capital, a digit or a backtick, outside code spans."""
        if self.kind in ("row", "heading"):
            return [(0, self.text)]
        spans = [(m.start(), m.end()) for m in _CODE.finditer(self.text)]
        out, start = [], 0
        for m in _SENTENCE_END.finditer(self.text):
            if any(a < m.start() < b for a, b in spans):
                continue
            out.append((start, self.text[start:m.start()]))
            start = m.end()
        out.append((start, self.text[start:]))
        return out

    def cells(self):
        return [c.strip() for c in re.split(r"(?<!\\)\|", self.text.strip().strip("|"))]


def _negative_listing(fence):
    rows = [r for r in fence.body.split("\n") if r.strip()]
    return bool(rows) and bool(mm.NEGATIVE_MARKER.match(rows[-1]))


class Doc(object):
    """A prose file of the skill: its blocks, its tables and its figure sources."""

    def __init__(self, rel):
        self.rel = rel
        self.text = mm.normalize_text((SKILL / rel).read_text(encoding="utf-8"))
        lines = self.text.split("\n")
        fenced = set()
        for start, end, _info, _indent in mm._fence_spans(lines):
            fenced.update(range(start, min(end, len(lines) - 1) + 1))
        raw_blocks, current = [], None
        for i, raw in enumerate(lines):
            if i in fenced or not raw.strip():
                current = None
                continue
            if raw.strip().startswith("|"):
                kind = "row"
            elif _HEADING.match(raw):
                kind = "heading"
            elif _LIST_ITEM.match(raw):
                kind = "item"
            elif current is not None:
                current.append((i + 1, raw))
                continue
            else:
                kind = "para"
            parts = [(i + 1, raw)]
            raw_blocks.append((kind, parts))
            current = parts if kind in ("item", "para") else None
        self.blocks = [Block(kind, rel, parts) for kind, parts in raw_blocks]

    def tables(self):
        """[(header cells, [data row blocks], header line)] of every Markdown table."""
        groups, group, last = [], None, None
        for b in self.blocks:
            if b.kind == "row" and group is not None and b.line == last + 1:
                group.append(b)
            elif b.kind == "row":
                group = [b]
                groups.append(group)
            else:
                group = None
            last = b.line
        return [(g[0].cells(), g[2:], g[0].line) for g in groups
                if len(g) >= 2 and all(_SEPARATOR.match(c) for c in g[1].cells())]

    def figure_sources(self):
        """(fence, figure kind) of each positive figure source: a mermaid fence whose last body
        line is not a negative marker, and a plain `text` listing of Mermaid source."""
        out = []
        for f in mm.extract_fences(self.text, ("mermaid",)):
            if f.negative is None:
                out.append((f, mm.detect_kind(f.body)[0]))
        for f in mm.extract_fences(self.text, ("text",)):
            if "figure" in f.info.lower().split()[1:] or _negative_listing(f):
                continue
            kind = mm.detect_kind(f.body)[0]
            if kind not in ("unknown", "ascii"):
                out.append((f, kind))
        return out


@lru_cache(maxsize=None)
def docs():
    rels = ["SKILL.md"] + ["references/%s" % p.name
                           for p in sorted((SKILL / "references").glob("*.md"))]
    return tuple(Doc(rel) for rel in rels)


def _where(doc_rel, line):
    return "%s:%d" % (doc_rel, line)


def _fmt(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# --------------------------------------------------------------------------- check 1: keyed values


def _states(value, nums, sentence):
    """True when a sentence with the numbers *nums* states *value*: a number, or a budget pair.
    A pair counts in full, except that a sentence naming only the soft budget may state the soft
    value alone, and one naming only the hard budget with a single number the hard value alone."""
    if not isinstance(value, tuple):
        return float(value) in nums
    soft, hard = (float(v) for v in value)
    says_soft = re.search(r"\bsoft\b", sentence, re.I) is not None
    says_hard = re.search(r"\bhard\b", sentence, re.I) is not None
    if says_soft and not says_hard:
        return soft in nums
    if says_hard and not says_soft and len(nums) == 1:
        return hard in nums
    return soft in nums and hard in nums


@lru_cache(maxsize=None)
def check_keyed():
    """(items, named-only, problems, used OWN_VALUES keys)."""
    items, named, problems, used = [], [], [], set()
    for doc in docs():
        for block in doc.blocks:
            if block.kind == "heading":
                continue
            block_nums = quantities(block.text)
            for start, sentence in block.sentences():
                nums = quantities(sentence)
                for m in _CODE.finditer(sentence):
                    name = m.group(1).strip()
                    if not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", name):
                        continue
                    paths = resolve_key(name)
                    if not paths:
                        continue
                    where = _where(doc.rel, block.line_at(start + m.start()))
                    items.append(where + " " + name)
                    values = sorted(set(paths.values()), key=str)
                    if any(_states(v, nums, sentence) for v in values):
                        continue
                    if not block_nums:
                        # The block states no number at all: it names the key, quotes nothing.
                        named.append(where + " " + name)
                        continue
                    own = [k for k in OWN_VALUES if k[0] == doc.rel and k[1] == name and k[2] in sentence]
                    if own:
                        used.update(own)
                        continue
                    problems.append('%s %s=%s not found in "%s"' % (
                        where, name, " or ".join(_fmt(v) for v in values), sentence))
    return items, named, problems, used


# --------------------------------------------------------------------------- check 2: palette

_STYLE_LINE = re.compile(r"^\s*style\s+(\S+)\s+(.+?)\s*;?\s*$")
_CLASSDEF = re.compile(r"^\s*classDef\s+([\w,-]+)\s+(.+?)\s*;?\s*$")
_BOX_RECT = re.compile(r"^\s*(box|rect)\s+(rgba?\([^)]*\)|hsla?\([^)]*\)|#[0-9A-Fa-f]{3,8}\b)")
_RGBA_SPAN = re.compile(r"^(?:(box|rect)\s+)?(rgba\(\s*\d[^)]*\))")  # `rgba(…)` is a placeholder
_COLOUR = re.compile(r"fill:|rgba?\(|#[0-9A-Fa-f]{6}\b")


def _palette_kind(rel, cls):
    """(kind, None) of the palette that rules a class in a prose file, or (None, problem)."""
    kind = FILE_PALETTE.get(rel)
    if kind is not None:
        return (kind, None) if cls in palettes().get(kind, {}) else (None, None)
    owners = [k for k, v in palettes().items() if cls in v]
    if len(owners) > 1:
        return None, "class `%s` is in the palettes %s; add %s to FILE_PALETTE" % (cls, owners, rel)
    return (owners[0], None) if owners else (None, None)


@lru_cache(maxsize=None)
def check_palette():
    """{"rows": [...], "figures": [...], "prose": [...]} of the items found, and the problems."""
    found = {"rows": [], "figures": [], "prose": []}
    problems = []
    pal = palettes()
    seq = NOTATION["palette"]["sequence"]
    clusters = {NOTATION["palette"]["cluster"], NOTATION["palette"]["cluster_band"]}
    for doc in docs():
        # prose: table rows that start with a class and quote a style; classDef, box, rect spans
        for block in doc.blocks:
            spans = [m.group(1).strip() for m in _CODE.finditer(block.text)]
            if block.kind == "row":
                first = re.fullmatch(r"`(\w+)`", block.cells()[0])
                styles = [s for s in spans if s.startswith("fill:")]
                if first and styles:
                    kind, problem = _palette_kind(doc.rel, first.group(1))
                    if problem:
                        problems.append(_where(doc.rel, block.line) + " " + problem)
                    elif kind is not None:
                        want = pal[kind][first.group(1)]
                        found["rows"].append((doc.rel, kind, first.group(1)))
                        if styles[0] != want:
                            problems.append("%s palette.%s.%s is `%s`, the row quotes `%s`" % (
                                _where(doc.rel, block.line), kind, first.group(1), want, styles[0]))
            for span in spans:
                m = _CLASSDEF.match(span)
                if m:
                    for cls in m.group(1).split(","):
                        kind, problem = _palette_kind(doc.rel, cls)
                        if problem:
                            problems.append(_where(doc.rel, block.line) + " " + problem)
                        elif kind is not None:
                            found["prose"].append((doc.rel, "classDef " + cls))
                            if m.group(2) != pal[kind][cls]:
                                problems.append("%s palette.%s.%s is `%s`, the span quotes `%s`" % (
                                    _where(doc.rel, block.line), kind, cls, pal[kind][cls], m.group(2)))
                m = _RGBA_SPAN.match(span)
                if m:
                    want = {"box": [seq["box"]], "rect": [seq["phase"]]}.get(m.group(1), list(seq.values()))
                    found["prose"].append((doc.rel, span))
                    if m.group(2) not in want:
                        problems.append("%s `%s` quotes a sequence colour that palette.sequence "
                                        "does not hold (%s)" % (_where(doc.rel, block.line), span,
                                                                " or ".join(want)))
            # a block that names a palette entry with a string value and quotes a colour
            for span in spans:
                if not span.startswith("palette."):
                    continue
                try:
                    want = value_at(span)
                except (KeyError, TypeError):
                    problems.append("%s `%s` is not an entry of notation.json" % (
                        _where(doc.rel, block.line), span))
                    continue
                if not isinstance(want, str) or not _COLOUR.search(" ".join(
                        s for s in spans if not s.startswith("palette."))):
                    continue
                found["prose"].append((doc.rel, span))
                if not re.search(r"(?<![\w,])" + re.escape(want) + r"(?![\w,:-])", block.text):
                    problems.append('%s %s=%s not found in "%s"' % (
                        _where(doc.rel, block.line), span, want, block.text))
        # figure sources: classDef lines, subgraph styles, box and rect colours
        for fence, kind in doc.figure_sources():
            for k, row in enumerate(fence.body.split("\n")):
                line = fence.body_start + k
                m = _CLASSDEF.match(row)
                if m and kind in pal:
                    for cls in m.group(1).split(","):
                        if cls not in pal[kind]:
                            continue
                        found["figures"].append((doc.rel, kind, cls))
                        if m.group(2) != pal[kind][cls]:
                            problems.append("%s classDef %s is `%s`; palette.%s.%s is `%s`" % (
                                _where(doc.rel, line), cls, m.group(2), kind, cls, pal[kind][cls]))
                m = _STYLE_LINE.match(row)
                if m and kind == "flowchart":
                    found["figures"].append((doc.rel, kind, "style"))
                    if m.group(2) not in clusters:
                        problems.append("%s style %s is `%s`; a subgraph takes palette.cluster or "
                                        "palette.cluster_band" % (_where(doc.rel, line), m.group(1),
                                                                  m.group(2)))
                m = _BOX_RECT.match(row)
                if m and kind == "sequence":
                    want = seq["box"] if m.group(1) == "box" else seq["phase"]
                    found["figures"].append((doc.rel, kind, m.group(1)))
                    if m.group(2) != want:
                        problems.append("%s %s colour is `%s`; palette.sequence.%s is `%s`" % (
                            _where(doc.rel, line), m.group(1), m.group(2),
                            "box" if m.group(1) == "box" else "phase", want))
    return found, problems


# --------------------------------------------------------------------------- check 3: shapes


@lru_cache(maxsize=None)
def check_shapes():
    """(rows found, problems) of the shape table of references/flowchart.md."""
    doc = next(d for d in docs() if d.rel == "references/flowchart.md")
    tables = [rows for header, rows, _line in doc.tables()
              if header == ["Element", "Shape", "Mermaid", "Class"]]
    if len(tables) != 1:
        return [], ["references/flowchart.md holds %d tables `Element | Shape | Mermaid | Class`, "
                    "not 1" % len(tables)]
    shapes = NOTATION["shapes"]["flowchart"]
    check = NOTATION["shapes"].get("decision_check")
    found, problems, single, decision = [], [], set(), 0
    for row in tables[0]:
        cells = row.cells()
        where = _where(doc.rel, row.line)
        word = (re.findall(r"[a-z]+", cells[1].lower()) or [""])[0]
        shape = SHAPE_WORDS.get(word)
        classes = re.findall(r"`(\w+)`", cells[3])
        found.append((row.line, word, classes))
        if shape is None:
            problems.append("%s shape word %r is not in SHAPE_WORDS" % (where, word))
            continue
        code = re.findall(r"`([^`]+)`", cells[2])
        fig = mm.parse_figure(mm.figure_from_mmd("flowchart TB\n  " + (code[0] if code else "")))
        drawn = [n.shape for n in fig.flowchart.nodes.values()] if fig.flowchart else []
        if drawn != [shape]:
            problems.append("%s the Mermaid column draws %s; the Shape column says %s (%s)" % (
                where, drawn or "nothing", word, shape))
        if len(classes) == 1:
            single.add(classes[0])
            if classes[0] not in shapes:
                problems.append("%s class `%s` is not in shapes.flowchart" % (where, classes[0]))
            elif shapes[classes[0]] != shape:
                problems.append("%s shapes.flowchart.%s is %s; the row says %s" % (
                    where, classes[0], shapes[classes[0]], word))
        else:
            decision += 1
            if check is None:
                problems.append("%s a row of several classes needs shapes.decision_check" % where)
            elif sorted(classes) != sorted(check["classes"]) or check["shape"] != shape:
                problems.append("%s shapes.decision_check is %s of %s; the row says %s of %s" % (
                    where, check["shape"], check["classes"], shape, classes))
    for cls in sorted(set(shapes) - single):
        problems.append("references/flowchart.md: no shape row for class `%s` of shapes.flowchart" % cls)
    if check is not None and decision != 1:
        problems.append("references/flowchart.md: %d rows for shapes.decision_check, not 1" % decision)
    return found, problems


# --------------------------------------------------------------------------- check 4: settings

_INIT_LINE = re.compile(r"^\s*%%\{\s*init(?:ialize)?\s*:")


@lru_cache(maxsize=None)
def check_settings():
    """({settings key: [where]}, problems)."""
    lines_by_key = {}
    problems = []
    settings = NOTATION["settings"]
    for doc in docs():
        for fence, kind in doc.figure_sources():
            for k, row in enumerate(fence.body.split("\n")):
                if not _INIT_LINE.match(row):
                    continue
                where = _where(doc.rel, fence.body_start + k)
                key = SETTINGS_KEY.get(kind)
                if key is None or key not in settings:
                    problems.append("%s a %s figure has no settings line in notation.json" % (where, kind))
                    continue
                lines_by_key.setdefault(key, []).append(where)
                if row.strip() != settings[key]:
                    problems.append("%s the %s settings line differs from settings.%s:\n  %s\n  %s" % (
                        where, kind, key, row.strip(), settings[key]))
        for block in doc.blocks:
            for m in _CODE.finditer(block.text):
                span = m.group(1).strip()
                if not span.startswith("%%{init:"):
                    continue
                where = _where(doc.rel, block.line_at(m.start()))
                keys = [k for k in re.findall(r"`settings\.(\w+)`", block.text) if k in settings]
                if not keys:
                    keys = [k for k in re.findall(r"\b(\w+) settings line\b", block.text) if k in settings]
                if not keys and doc.rel in FILE_SETTINGS:
                    keys = [FILE_SETTINGS[doc.rel]]
                if not keys:
                    # The kind is not named: the line must be one of the settings lines.
                    lines_by_key.setdefault("?", []).append(where)
                    if span not in settings.values():
                        problems.append("%s `%s` is no settings line of notation.json" % (where, span))
                    continue
                for key in sorted(set(keys)):
                    lines_by_key.setdefault(key, []).append(where)
                    if span != settings[key]:
                        problems.append("%s the quoted line differs from settings.%s:\n  %s\n  %s" % (
                            where, key, span, settings[key]))
    return lines_by_key, problems


# --------------------------------------------------------------------------- check 5: budgets


def _metric(words, metrics, fallback):
    """The budget metric of *metrics* that *words* name ("phase blocks" -> phase_blocks), or
    *fallback* when no words follow the number."""
    if not words:
        return fallback
    w = " ".join(words.lower().split())
    for m in metrics:
        name = m.replace("_", " ")
        if w in (name, name.rstrip("s"), name + "s"):
            return m
    return None


def _cell_values(cell):
    """[(first number, second number or None, words or "")] of a budget cell, or None for
    "none"."""
    if cell.lower().startswith("none"):
        return None
    out = []
    for part in re.split(r"[,;]", cell):
        part = part.strip().strip("`")
        m = re.fullmatch(r"(\d+)(?:\s*/\s*(\d+))?(?:\s+([A-Za-z][A-Za-z ]*))?", part)
        if m:
            out.append((int(m.group(1)), int(m.group(2)) if m.group(2) else None, m.group(3) or ""))
    return out


def _budget_row_kind(first_cell):
    """(kind, metric or None) of the first cell of a budget-table row; kind None if unknown."""
    m = re.search(r"`budgets\.(\w+)\.(\w+)`", first_cell)
    if m:
        return m.group(1), m.group(2)
    return BUDGET_ROW_KIND.get(first_cell.replace("`", "").strip().lower()), None


@lru_cache(maxsize=None)
def check_budgets():
    """(rows found as (file, kind), problems)."""
    found, problems = [], []
    budgets = NOTATION["budgets"]
    for doc in docs():
        for header, rows, _line in doc.tables():
            roles = {}
            for i, h in enumerate(header[1:], 1):
                low = h.lower()
                if "soft" in low and "hard" in low:
                    roles[i] = "pair"
                elif "soft" in low:
                    roles[i] = "soft"
                elif "hard" in low:
                    roles[i] = "hard"
                elif "budget" in low:
                    roles[i] = "pair"
            if not roles:
                continue
            for row in rows:
                cells = row.cells()
                where = _where(doc.rel, row.line)
                kind, only = _budget_row_kind(cells[0])
                if kind is None:
                    problems.append("%s budget row of unknown kind %r; add it to BUDGET_ROW_KIND" % (
                        where, cells[0]))
                    continue
                found.append((doc.rel, kind))
                if kind not in budgets:
                    for i in roles:
                        if _cell_values(cells[i]) is not None:
                            problems.append('%s budgets has no "%s"; the row states "%s"' % (
                                where, kind, cells[i]))
                    continue
                metrics = budgets[kind]
                single = only or (next(iter(metrics)) if len(metrics) == 1 else None)
                soft, hard, order = {}, {}, []
                for i, role in sorted(roles.items()):
                    values = _cell_values(cells[i])
                    if values is None:
                        problems.append('%s budgets.%s is %s; the row says "%s"' % (
                            where, kind, metrics, cells[i]))
                        continue
                    for pos, (a, b, words) in enumerate(values):
                        fallback = order[pos] if role == "hard" and pos < len(order) else single
                        metric = _metric(words, metrics, fallback)
                        if metric is None:
                            problems.append('%s "%s" names no metric of budgets.%s' % (where, cells[i], kind))
                            continue
                        if role == "pair":
                            soft[metric], hard[metric] = a, b
                        elif role == "soft":
                            soft[metric] = a
                            order.append(metric)
                        else:
                            hard[metric] = a
                for metric in ([only] if only else list(metrics)):
                    want = tuple(metrics.get(metric, (None, None)))
                    have = (soft.get(metric), hard.get(metric))
                    if have != want:
                        problems.append('%s budgets.%s.%s is %s; the row states %s in "%s"' % (
                            where, kind, metric, list(want), list(have), row.text))
    return found, problems


# --------------------------------------------------------------------------- check 6: phrases


def _same(found, want):
    if _is_number(want):
        try:
            return float(found) == float(want)
        except ValueError:
            return False
    return str(found).lower() == str(want).lower()


@lru_cache(maxsize=None)
def check_phrases():
    """({phrase: number of matches}, problems)."""
    counts, problems = {}, []
    for phrase, paths in PHRASES:
        pattern = re.compile(phrase)
        counts[phrase] = 0
        wants = [value_at(p) for p in paths]
        for doc in docs():
            for block in doc.blocks:
                if block.kind == "heading":
                    continue
                for m in pattern.finditer(block.text):
                    counts[phrase] += 1
                    for group, (path, want) in enumerate(zip(paths, wants), 1):
                        if not _same(m.group(group), want):
                            problems.append('%s %s=%s, the text states %s in "%s"' % (
                                _where(doc.rel, block.line_at(m.start(group))), concrete(path),
                                want, m.group(group), m.group(0)))
    return counts, problems


# --------------------------------------------------------------------------- check 7: kind lists

_KIND_NAME = re.compile(r"`([A-Za-z][\w-]*)`")


@lru_cache(maxsize=None)
def check_kinds():
    """([(where, list)], problems) of the kind lists that the prose copies from `kinds`: a list
    item that starts `preferred:` or `allowed:` holds that list; one that starts `listed under
    `avoid`` holds part of `kinds.avoid`; the table below a sentence that names `kinds.avoid`
    holds that list in its first column."""
    found, problems = [], []
    kinds = NOTATION["kinds"]

    def compare(where, group, names):
        missing = sorted(set(kinds[group]) - set(names))
        extra = sorted(set(names) - set(kinds[group]))
        if missing or extra:
            problems.append("%s kinds.%s differs: missing %s, not in notation.json %s" % (
                where, group, missing, extra))

    for doc in docs():
        tables = doc.tables()
        for block in doc.blocks:
            where = _where(doc.rel, block.line)
            m = re.match(r"(preferred|allowed): ", block.text)
            if m:
                found.append((where, m.group(1)))
                compare(where, m.group(1), _KIND_NAME.findall(block.text))
            m = re.match(r"listed under `avoid` in `notation\.json`: ", block.text)
            if m:
                found.append((where, "part of avoid"))
                extra = sorted(set(_KIND_NAME.findall(block.text[m.end():])) - set(kinds["avoid"]))
                if extra:
                    problems.append("%s %s are not in kinds.avoid" % (where, extra))
            if block.kind != "row" and "`kinds.avoid`" in block.text:
                below = [rows for _h, rows, line in tables if 0 < line - block.line <= 3]
                if not below:
                    problems.append("%s names kinds.avoid, and no table follows" % where)
                    continue
                found.append((where, "avoid"))
                compare(where, "avoid", [n for row in below[0]
                                         for n in _KIND_NAME.findall(row.cells()[0])])
    return found, problems


# --------------------------------------------------------------------------- tests


class TestNotationShape(unittest.TestCase):
    def setUp(self):
        self.n = mm.load_notation()

    def test_schema(self):
        self.assertEqual(self.n["schema"], "mermaid-notation/v1")

    def test_budgets_are_soft_hard_pairs(self):
        for kind, limits in self.n["budgets"].items():
            for name, pair in limits.items():
                self.assertEqual(len(pair), 2, f"{kind}.{name}")
                self.assertLessEqual(pair[0], pair[1], f"{kind}.{name}")

    def test_settings_have_no_sanitized_values(self):
        for kind, line in self.n["settings"].items():
            cfg = settings_config(line)
            for key, value in cfg.get("themeVariables", {}).items():
                self.assertRegex(str(value), r'^[\d "#%(),.;A-Za-z]+$', f"{kind}.{key}")
            self.assertNotIn("theme", cfg, f"{kind}: no theme key (dark mode, TASK D4)")


class TestQuotedValues(unittest.TestCase):
    """Every value that SKILL.md and the references quote equals notation.json (PLAN F4)."""

    def _no_problems(self, problems):
        if problems:
            self.fail("%d quoted value(s) differ from notation.json:\n%s" % (
                len(problems), "\n".join(problems)))

    def test_keyed_values(self):
        self._no_problems(check_keyed()[2])

    def test_palette(self):
        self._no_problems(check_palette()[1])

    def test_shape_table(self):
        self._no_problems(check_shapes()[1])

    def test_settings_lines(self):
        self._no_problems(check_settings()[1])

    def test_budget_tables(self):
        self._no_problems(check_budgets()[1])

    def test_phrases(self):
        self._no_problems(check_phrases()[1])

    def test_kind_lists(self):
        self._no_problems(check_kinds()[1])


class TestChecksFindTheirItems(unittest.TestCase):
    """A check that finds nothing passes vacuously; these tests make that a failure."""

    def test_keyed_values_found(self):
        items, _named, _problems, used = check_keyed()
        self.assertGreaterEqual(len(items), MINIMUM["keyed values"])
        self.assertEqual(set(OWN_VALUES) - used, set(), "OWN_VALUES entries that match no sentence")

    def test_palette_found(self):
        found = check_palette()[0]
        self.assertGreaterEqual(len(found["rows"]), MINIMUM["palette rows"])
        self.assertGreaterEqual(len(found["figures"]), MINIMUM["palette lines in figures"])
        self.assertGreaterEqual(len(found["prose"]), MINIMUM["palette quotes in prose"])
        rows = {(k, c) for _rel, k, c in found["rows"]}
        lines = {(k, c) for _rel, k, c in found["figures"]}
        for kind, classes in palettes().items():
            for cls in classes:
                if kind == "flowchart":
                    self.assertIn((kind, cls), rows, "no palette row quotes palette.%s.%s" % (kind, cls))
                if kind in ("flowchart", "state"):
                    self.assertIn((kind, cls), lines, "no figure defines palette.%s.%s" % (kind, cls))
        for kind, what in (("flowchart", "style"), ("sequence", "box"), ("sequence", "rect")):
            self.assertIn((kind, what), lines, "no %s figure has a %s line" % (kind, what))

    def test_shape_rows_found(self):
        self.assertGreaterEqual(len(check_shapes()[0]), MINIMUM["shape rows"])

    def test_settings_lines_found(self):
        by_key = check_settings()[0]
        self.assertGreaterEqual(sum(len(v) for v in by_key.values()), MINIMUM["settings lines"])
        for key in NOTATION["settings"]:
            self.assertIn(key, by_key, "no figure or prose quotes settings.%s" % key)

    def test_budget_rows_found(self):
        found = check_budgets()[0]
        self.assertGreaterEqual(len(found), MINIMUM["budget rows"])
        kinds = {kind for _rel, kind in found}
        for kind in NOTATION["budgets"]:
            self.assertIn(kind, kinds, "no budget table has a row for budgets.%s" % kind)

    def test_every_phrase_matches(self):
        counts = check_phrases()[0]
        self.assertEqual([p for p, c in counts.items() if c == 0], [], "phrases that match nothing")

    def test_kind_lists_found(self):
        lists = {group for _where, group in check_kinds()[0]}
        self.assertEqual(lists, {"preferred", "allowed", "avoid", "part of avoid"})


if __name__ == "__main__":
    unittest.main()
