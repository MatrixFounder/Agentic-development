"""Backlog work-item appender.

Insertion is anchored on a seeded HTML comment marker (default
``<!-- feedback:discovered-issues -->``) rather than a section heading:
headings get renumbered/retitled, comments do not. New bullets are
inserted directly AFTER the anchor (newest first). A missing anchor is a
hard exit-4 conflict — never a blind EOF append.
"""

from __future__ import annotations

import os
from pathlib import Path

from .envelope import EXIT_FILING_CONFLICT, CliError


def format_bullet(title, body, date, effort=None, value=None):
    tail = ""
    if effort or value:
        parts = []
        if effort:
            parts.append("Effort: %s" % effort)
        if value:
            parts.append("Value: %s" % value)
        tail = " · " + " · ".join(parts)
    body = " ".join(str(body or "").split())
    return "- **%s (%s)** — %s%s" % (title, date, body, tail)


def append_work_item(backlog_path, anchor, bullet, dry_run=False):
    backlog_path = Path(backlog_path)
    if not backlog_path.is_file():
        raise CliError("backlog file not found: %s" % backlog_path,
                       code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
                       remediation="set backlog_path in docs/feedback/config.json")
    text = backlog_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    anchor_idx = next((i for i, l in enumerate(lines) if l.strip() == anchor),
                      None)
    if anchor_idx is None:
        raise CliError(
            "backlog anchor %r not found in %s" % (anchor, backlog_path),
            code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
            remediation="seed the anchor comment inside the Discovered "
                        "Issues section (one-time human commit)")
    lines.insert(anchor_idx + 1, bullet)
    new_text = "\n".join(lines)
    if text.endswith("\n"):
        new_text += "\n"
    if dry_run:
        return {"backlog_path": str(backlog_path), "bullet": bullet,
                "dry_run": True}
    tmp = backlog_path.with_suffix(backlog_path.suffix + ".tmp.%d" % os.getpid())
    tmp.write_text(new_text, encoding="utf-8")
    os.replace(str(tmp), str(backlog_path))
    return {"backlog_path": str(backlog_path), "bullet": bullet,
            "dry_run": False}
