"""Flowchart parser of the parse model (TASK 124)."""

from __future__ import annotations

import re
from typing import Optional

from .figure import Edge, Figure, Flowchart, Node, Subgraph
from .hazards import _ENTITY, _bad_tags, _printable_entity


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


