"""Preprocessing of the parse model: the body lines of a fence, its settings and its
accessibility lines, before a kind's parser reads it (TASK 124)."""

from __future__ import annotations

import re
from typing import Optional

from .document import Fence
from .figure import Figure, Settings
from .kinds import KIND_OF_KEYWORD, _known_keywords, diagram_keyword
from .settings import YamlError, _DIRECTIVE, _parse_directive, parse_yaml


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


