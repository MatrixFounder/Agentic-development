"""Settings of the parse model: front matter, `%%{init}%%` directives and their
properties (TASK 124)."""

from __future__ import annotations

import json
import re
from typing import Optional


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


