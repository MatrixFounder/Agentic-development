"""Minimal YAML frontmatter reader/writer for issue files.

Deliberately NOT a YAML parser: the known-issues-format contract uses only
flat ``key: scalar`` pairs plus (for our optional ``evidence_paths``) a
block list of strings. Reading is tolerant (unknown keys kept, inline
comments stripped); writing preserves insertion order and quotes nothing
it does not have to.
"""

from __future__ import annotations

import re
from pathlib import Path

_DELIM = "---"
_KEY_RE = re.compile(r"^([A-Za-z_][\w\-]*):\s*(.*)$")
_LIST_ITEM_RE = re.compile(r"^\s+-\s+(.*)$")


def _strip_comment(value):
    # strip an unquoted trailing comment: `open   # note` -> `open`
    if value.startswith(("'", '"')):
        quote = value[0]
        end = value.find(quote, 1)
        if end != -1:
            return value[1:end]
    hash_pos = value.find(" #")
    if hash_pos != -1:
        value = value[:hash_pos]
    return value.strip()


def parse(text):
    """Return (meta: dict, body: str). meta is {} when no frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != _DELIM:
        return {}, text
    meta = {}
    idx = 1
    current_list_key = None
    while idx < len(lines):
        line = lines[idx]
        if line.strip() == _DELIM:
            idx += 1
            break
        item = _LIST_ITEM_RE.match(line)
        if item and current_list_key is not None:
            meta[current_list_key].append(_strip_comment(item.group(1).strip()))
            idx += 1
            continue
        current_list_key = None
        match = _KEY_RE.match(line)
        if match:
            key, raw = match.group(1), match.group(2).strip()
            if raw == "":
                meta[key] = []
                current_list_key = key
            else:
                value = _strip_comment(raw)
                if value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                meta[key] = value
        idx += 1
    body = "\n".join(lines[idx:])
    return meta, body


def parse_file(path):
    return parse(Path(path).read_text(encoding="utf-8"))


def serialize(meta):
    out = [_DELIM]
    for key, value in meta.items():
        if isinstance(value, list):
            out.append("%s:" % key)
            out.extend("  - %s" % item for item in value)
        elif isinstance(value, bool):
            out.append("%s: %s" % (key, "true" if value else "false"))
        else:
            out.append("%s: %s" % (key, value))
    out.append(_DELIM)
    return "\n".join(out) + "\n"
