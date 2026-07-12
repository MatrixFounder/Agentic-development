"""docs/issues/ + KNOWN_ISSUES.md lockstep writer and reader.

Write discipline (the known-issues-format contract, owned by the sibling
skill in this repo):
  * create-only — this module NEVER edits or deletes an existing issue
    file or index line; resolving/flipping stays with humans / heal-issues;
  * frontmatter keys in contract order, optional extension keys AFTER
    ``slug``;
  * the index line goes INTO the matching ``## <category>`` section, in ID
    order; new categories are created in alphabetical position; preamble
    sections (``## Rules``, ``## How to add …`` — anything not matching a
    lowercase single-token heading) are never touched;
  * lockstep rollback: the issue file is written first; if the index write
    fails the issue file is removed so a half-state never exists.

Read discipline is TOLERANT: live ledgers carry local extensions
(``status: handled``, ``severity: MED``) that must not crash a scan.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path

from . import frontmatter, ids
from .envelope import EXIT_CONFIG, EXIT_FILING_CONFLICT, CliError

# --- vocab -----------------------------------------------------------------

STATUS_WRITE = ("open", "fixed", "documented", "by-design", "mitigated",
                "wontfix")
SEVERITY_WRITE = ("SEV-2", "SEV-3", "SEV-4", "LOW")

# read-side ranking: tolerant superset, unknown/missing sorts lowest
SEVERITY_RANK = {
    "SEV-2": 50, "HIGH": 45, "SEV-3": 40, "MED": 30, "MEDIUM": 30,
    "SEV-4": 20, "LOW": 10,
}

_CATEGORY_HEADING_RE = re.compile(r"^## ([a-z0-9][a-z0-9\-]*)\s*$")
_INDEX_ENTRY_RE = re.compile(r"^- \*\*([^*]+)\*\* ")
_ID_SORT_RE = re.compile(r"^(.*?)-(\d+)(?:[A-Z\-].*)?$")

CONTRACT_KEYS = ("id", "type", "status", "opened_at", "category", "severity",
                 "slug")
EXTENSION_KEYS = ("component", "fingerprint", "evidence_paths",
                  "auto_fixable", "finding_ref")


def severity_rank(value):
    return SEVERITY_RANK.get(str(value or "").strip(), 0)


def format_index_line(issue_id, title, slug, status, opened_at, severity=None):
    severity_clause = "severity `%s`, " % severity if severity else ""
    return ("- **%s** [%s](issues/%s.md) — %sstatus `%s`, opened %s"
            % (issue_id, title, slug, severity_clause, status, opened_at))


def _id_sort_key(issue_id):
    match = _ID_SORT_RE.match(issue_id)
    if match:
        return (match.group(1), int(match.group(2)))
    return (issue_id, 0)


# --- index seeding ---------------------------------------------------------

def _seed_template_path():
    skills_dir = Path(__file__).resolve().parents[3]
    return (skills_dir / "known-issues-format" / "assets" / "templates"
            / "known_issues_md_template.md")


def seed_index_text():
    """Materialize a fresh index from the known-issues-format seed template:
    keep everything above the first category group, drop the seed comments
    and the ``_No issues recorded yet._`` placeholder."""
    template = _seed_template_path()
    if not template.is_file():
        raise CliError(
            "known-issues-format seed template not found at %s" % template,
            code=EXIT_CONFIG, err_type="ConfigError",
            remediation="install/symlink the known-issues-format skill next "
                        "to run-feedback")
    text = template.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->\n?", "", text, flags=re.DOTALL)
    text = text.replace("_No issues recorded yet._\n", "")
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


# --- index insertion -------------------------------------------------------

def insert_index_line(index_text, category, line):
    """Pure function: return index text with *line* routed into
    ``## <category>`` (section created alphabetically when absent)."""
    lines = index_text.splitlines()
    headings = [(i, m.group(1)) for i, m in
                ((i, _CATEGORY_HEADING_RE.match(l)) for i, l in enumerate(lines))
                if m]

    def section_end(start_idx):
        for j in range(start_idx + 1, len(lines)):
            if lines[j].startswith("## "):
                return j
        return len(lines)

    target = next(((i, cat) for i, cat in headings if cat == category), None)
    if target is None:
        insert_at = len(lines)
        for i, cat in headings:
            if cat > category:
                insert_at = i
                break
        block = ["## %s" % category, "", line, ""]
        # keep exactly one blank line before a newly appended heading
        while insert_at > 0 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        block.insert(0, "")
        lines[insert_at:insert_at] = block
        return "\n".join(lines).rstrip("\n") + "\n"

    start, end = target[0], section_end(target[0])
    new_id = _INDEX_ENTRY_RE.match(line).group(1)
    new_key = _id_sort_key(new_id)
    insert_at = None
    last_entry = None
    for j in range(start + 1, end):
        match = _INDEX_ENTRY_RE.match(lines[j])
        if not match:
            continue
        last_entry = j
        if _id_sort_key(match.group(1)) > new_key and insert_at is None:
            insert_at = j
    if insert_at is None:
        insert_at = (last_entry + 1) if last_entry is not None else start + 2
        if last_entry is None and insert_at > len(lines):
            insert_at = end
    lines.insert(insert_at, line)
    return "\n".join(lines).rstrip("\n") + "\n"


def _write_atomic(path, text):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp.%d" % os.getpid())
    tmp.write_text(text, encoding="utf-8")
    os.replace(str(tmp), str(path))


# --- the lockstep defect write ----------------------------------------------

def file_defect(config, issue_id, slug, title, category, body, status="open",
                severity=None, opened_at=None, extensions=None, dry_run=False):
    """Create ``<issues_dir>/<slug>.md`` + its index line, atomically-ish.

    Returns a dict describing what was (or would be) written. Caller holds
    the filing flock.
    """
    if status not in STATUS_WRITE:
        raise CliError("status %r outside the write vocabulary %s"
                       % (status, list(STATUS_WRITE)),
                       code=EXIT_FILING_CONFLICT, err_type="ContractError")
    if severity and severity not in SEVERITY_WRITE:
        raise CliError("severity %r outside the write vocabulary %s"
                       % (severity, list(SEVERITY_WRITE)),
                       code=EXIT_FILING_CONFLICT, err_type="ContractError")
    opened_at = opened_at or time.strftime("%Y-%m-%d")

    issues_dir = Path(config.issues_dir)
    issue_path = issues_dir / (slug + ".md")
    if issue_path.exists():
        raise CliError("issue file already exists: %s" % issue_path,
                       code=EXIT_FILING_CONFLICT, err_type="FilingConflict")

    meta = {"id": issue_id, "type": "known-issue", "status": status,
            "opened_at": opened_at, "category": category}
    if severity:
        meta["severity"] = severity
    meta["slug"] = slug
    for key in EXTENSION_KEYS:
        value = (extensions or {}).get(key)
        if value not in (None, "", []):
            meta[key] = value

    issue_text = (frontmatter.serialize(meta) + "\n# %s — %s\n\n%s\n"
                  % (issue_id, title, body.strip()))
    index_line = format_index_line(issue_id, title, slug, status, opened_at,
                                   severity)

    index_path = Path(config.index_path)
    if index_path.is_file():
        index_before = index_path.read_text(encoding="utf-8")
        seeded = False
    else:
        index_before = seed_index_text()
        seeded = True
    index_after = insert_index_line(index_before, category, index_line)

    result = {"issue_id": issue_id, "slug": slug,
              "issue_path": str(issue_path), "index_path": str(index_path),
              "index_line": index_line, "seeded_index": seeded,
              "dry_run": dry_run}
    if dry_run:
        result["issue_text"] = issue_text
        return result

    issues_dir.mkdir(parents=True, exist_ok=True)
    issue_path.write_text(issue_text, encoding="utf-8")
    try:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        _write_atomic(index_path, index_after)
    except BaseException:
        try:
            issue_path.unlink()
        except OSError:
            pass
        raise
    return result


# --- tolerant reads ---------------------------------------------------------

def list_issues(config, status=None, component=None, auto_fixable=None):
    """Frontmatter scan of the issues dir; tolerant of local vocab."""
    issues_dir = Path(config.issues_dir)
    out = []
    if not issues_dir.is_dir():
        return out
    for path in sorted(issues_dir.glob("*.md")):
        try:
            meta, _ = frontmatter.parse_file(path)
        except OSError:
            continue
        if meta.get("type") != "known-issue":
            continue
        record = {
            "id": meta.get("id"), "slug": meta.get("slug", path.stem),
            "path": str(path), "status": meta.get("status"),
            "severity": meta.get("severity"),
            "severity_rank": severity_rank(meta.get("severity")),
            "category": meta.get("category"),
            "component": meta.get("component"),
            "fingerprint": meta.get("fingerprint"),
            "auto_fixable": meta.get("auto_fixable") is True,
            "evidence_paths": meta.get("evidence_paths") or [],
            "opened_at": meta.get("opened_at"),
            "resolved_by": meta.get("resolved_by"),
        }
        if status and record["status"] != status:
            continue
        if component and record["component"] != component:
            continue
        if auto_fixable is not None and record["auto_fixable"] != auto_fixable:
            continue
        out.append(record)
    return out
