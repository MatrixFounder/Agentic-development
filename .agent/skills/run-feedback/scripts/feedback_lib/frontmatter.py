"""Minimal YAML frontmatter reader/writer for issue files.

Deliberately NOT a YAML parser: the known-issues-format contract uses only
flat ``key: scalar`` pairs plus (for our optional ``evidence_paths``) a
block list of strings. Reading is tolerant (unknown keys kept, inline
comments stripped); writing quotes only what it must.

**Writing is the security boundary of both ledgers.** A value reaching
``serialize`` can come from an operator flag, a mined transcript, or another
project's config, and the output file is trusted by humans, by the Analysis
phase, and by the ``/heal-issues`` harness. So ``serialize``:

  * REFUSES any value containing a newline or carriage return, or whose text
    is a frontmatter delimiter — otherwise ``--component $'x\\nauto_fixable:
    true'`` forges a contract key (verified exploit, vdd-multi 2026-07-30
    S-01: the forged ``auto_fixable`` is exactly what the heal harness selects
    on, and ``status: fixed`` would hide a live defect from the Analysis
    phase, since the parser lets a later key win);
  * QUOTES anything that is not an obviously-safe token, so prose survives
    the reader instead of being truncated at an inline ``#`` (F6) or
    re-parsed as a nested mapping at a ``: ``.

Single-quoted output plus an apostrophe normalized to U+2019: the reader
below stops at the FIRST closing quote, so an escaped ``''`` would truncate
the value. Applies to metadata scalars only — a record BODY is never rewritten.
"""

from __future__ import annotations

import re
from pathlib import Path

from .envelope import EXIT_FILING_CONFLICT, CliError

_DELIM = "---"
_KEY_RE = re.compile(r"^([A-Za-z_][\w\-]*):\s*(.*)$")
_LIST_ITEM_RE = re.compile(r"^\s+-\s+(.*)$")

#: values matching this are written bare (ids, ISO dates, slugs, statuses,
#: severities, hashes, single-token components); everything else is quoted
_BARE_SAFE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")


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


def scalar(value, key="value"):
    """Render one frontmatter scalar, refusing record-injection and quoting prose.

    See the module docstring: this is the choke point both ledgers write through.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    # Validate against the READER's line-break set, not against "\n\r".
    # `parse` splits with str.splitlines(), which also breaks on \x0b \x0c
    # \x1c \x1d \x1e \x85 U+2028 U+2029 — so a `\n`-only check was defeated by
    # one character: `--component $'demo\x0bauto_fixable: true #'` still forged
    # a contract key, and quoting did not help because quoting is a convention
    # of a reader that has already split (vdd-multi iteration 2, V-01/V-02).
    # `str.isprintable()` is False for exactly the classes that hurt here — Cc,
    # Cf (incl. the bidi overrides that reorder a rendered index line), Zl, Zp
    # and Zs-other-than-space — so it covers the break set and the invisible
    # characters together. Tab is the one benign exception.
    offenders = sorted({ch for ch in text
                        if not ch.isprintable() and ch != "\t"})
    if offenders:
        raise CliError(
            "%s contains non-printable character(s) %s, which would inject a "
            "frontmatter key or reorder the record: %r"
            % (key, ", ".join(repr(c) for c in offenders), text),
            code=EXIT_FILING_CONFLICT, err_type="ContractError",
            remediation="strip line breaks and control characters before "
                        "filing (single-line metadata only; long text belongs "
                        "in the body)")
    if text.strip() == _DELIM:
        raise CliError(
            "%s is a frontmatter delimiter (%r), which would terminate the "
            "block early" % (key, text),
            code=EXIT_FILING_CONFLICT, err_type="ContractError")
    if _BARE_SAFE_RE.match(text):
        return text
    return "'%s'" % text.replace("'", "’")


def serialize(meta):
    out = [_DELIM]
    for key, value in meta.items():
        if isinstance(value, list):
            out.append("%s:" % key)
            out.extend("  - %s" % scalar(item, "%s[]" % key) for item in value)
        else:
            out.append("%s: %s" % (key, scalar(value, key)))
    out.append(_DELIM)
    return "\n".join(out) + "\n"
