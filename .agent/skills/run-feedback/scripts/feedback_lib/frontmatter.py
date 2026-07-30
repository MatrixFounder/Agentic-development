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
    re-parsed as a nested mapping at a ``: ``;
  * QUOTES a token that would change TYPE on read — ``true``, ``no``, ``2026``,
    ``0x10`` — so a real YAML consumer gets back the string that was written
    (V-21). ISO dates stay bare on purpose (see ``_YAML_NUMERIC_RE``).

Single-quoted output plus an apostrophe normalized to U+2019: the reader
below stops at the FIRST closing quote, so an escaped ``''`` would truncate
the value. Applies to metadata scalars only — a record BODY is never rewritten.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from .envelope import EXIT_FILING_CONFLICT, CliError

_DELIM = "---"
_KEY_RE = re.compile(r"^([A-Za-z_][\w\-]*):\s*(.*)$")
_LIST_ITEM_RE = re.compile(r"^\s+-\s+(.*)$")

#: values matching this are written bare (ids, ISO dates, slugs, statuses,
#: severities, hashes, single-token components); everything else is quoted
_BARE_SAFE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")

#: bare-safe text a REAL YAML parser would hand back as a non-string. Our own
#: reader returns `"true"`/`"2026"` as a str (bar the explicit bool case in
#: `parse`), so this never bit us — but these records are read by humans, by
#: other tooling, and potentially by a PyYAML-based consumer, and
#: `status: 'true'` vs `status: true` is a type change in the ledger contract
#: (vdd-multi iteration 2, V-21). ISO dates are deliberately NOT here: quoting
#: `opened_at: 2026-07-30` would rewrite every record in every corpus, and a
#: date is the one coercion whose target type is what the contract means anyway.
_YAML_BOOLISH_RE = re.compile(
    r"^(?:true|false|yes|no|on|off|null|~)$", re.IGNORECASE)
_YAML_NUMERIC_RE = re.compile(
    r"^[+-]?(?:"
    r"0[bB][01_]+"                    # binary
    r"|0[xX][0-9a-fA-F_]+"            # hex
    r"|0[oO]?[0-7_]+"                 # octal (YAML 1.1 allows the bare 0NNN form)
    r"|[0-9][0-9_]*"                  # int
    r"|[0-9][0-9_]*\.[0-9_]*(?:[eE][+-]?[0-9]+)?"   # float
    r"|\.[0-9_]+(?:[eE][+-]?[0-9]+)?"               # .5
    r"|[0-9][0-9_]*(?:[eE][+-]?[0-9]+)"             # 1e6
    r"|\.(?:inf|Inf|INF|nan|NaN|NAN)"               # .inf / .nan
    r")$")


def _coerces_under_yaml(text):
    """True when a bare emission of *text* would change its type on read."""
    return bool(_YAML_BOOLISH_RE.match(text)
                or _YAML_NUMERIC_RE.match(text))


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
                # Was the value QUOTED in the source? Checked before
                # `_strip_comment` removes the quotes, because the answer decides
                # whether to coerce: `status: true` is a bool, `status: 'true'` is
                # the string "true". Without this, `scalar`'s new coercion guard
                # was defeated by our own reader — it quoted `"true"` on write and
                # this branch turned it straight back into `True`, so
                # `parse(serialize(m)) == m` failed for exactly the values V-21 is
                # about. Found by writing the round-trip test, not by reading.
                was_quoted = raw.startswith(("'", '"'))
                value = _strip_comment(raw)
                if not was_quoted and value.lower() in ("true", "false"):
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
    if _BARE_SAFE_RE.match(text) and not _coerces_under_yaml(text):
        return text
    if "'" in text:
        # the reader below stops at the FIRST closing quote, so an escaped `''`
        # would truncate the value — the apostrophe is normalized instead. That
        # is a silent rewrite of operator text, so it is announced (V-21).
        sys.stderr.write(
            "run-feedback: warning: apostrophe in %s normalized to U+2019 "
            "(’) so the single-quoted scalar cannot be truncated on read\n"
            % key)
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
