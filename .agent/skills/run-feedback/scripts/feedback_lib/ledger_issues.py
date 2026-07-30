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

from . import (atomic, body as body_mod, frontmatter, ids,
               ledger_core, markdown)
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

#: frontmatter keys in contract order; ``severity`` is the one optional member.
#: This tuple BUILDS the mapping (``_build_meta``) — it used to be dead code
#: sitting beside a hand-written literal that restated it (iteration 2, V11).
#: Pinned to the `known-issues-format` SKILL.md authority by a test.
CONTRACT_KEYS = ("id", "type", "status", "opened_at", "category", "severity",
                 "slug")
OPTIONAL_CONTRACT_KEYS = frozenset({"severity"})
#: optional keys written AFTER the contract keys, in this order
EXTENSION_KEYS = ("provenance", "component", "fingerprint", "evidence_paths",
                  "auto_fixable", "finding_ref")


def severity_rank(value):
    return SEVERITY_RANK.get(str(value or "").strip(), 0)


def format_index_line(issue_id, title, slug, status, opened_at, severity=None):
    """The canonical Registry A index line (pure, single-line by construction).

    Title collapsing + `[`/`]` escaping is the same guard as the work-item
    grammar: a raw newline spliced a second, forged pointer line into a
    hand-maintained index, and an unescaped `]` closed the link early
    (vdd-multi S-02).
    """
    severity_clause = "severity `%s`, " % severity if severity else ""
    line = ("- **%s** [%s](issues/%s.md) — %sstatus `%s`, opened %s"
            % (" ".join(str(issue_id).split()),
               re.sub(r"([\\\[\]])", r"\\\1", " ".join(str(title).split())),
               " ".join(str(slug).split()), severity_clause,
               " ".join(str(status).split()),
               " ".join(str(opened_at).split())))
    if "\n" in line or "\r" in line:
        raise CliError("index line would span multiple lines: %r" % line,
                       code=EXIT_FILING_CONFLICT, err_type="ContractError")
    return line


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

def _eol_of(lines, _near=None):
    """The line ending this FILE uses, decided from the whole file.

    Sampling one line near the insertion point was wrong in the case that matters
    most: when the category is new and sorts last, ``insert_at == len(lines)`` and
    the sampled line is the empty tail element that ``split("\\n")`` produces for
    any file ending in a newline — so ``"".endswith("\\r")`` is False and a CRLF
    ledger silently gained bare-LF lines. That path is not exotic: a freshly
    seeded index has no category sections at all, so the **first defect ever
    filed** takes it (iteration 3, L-1).
    """
    return "\r\n" if any(l.endswith("\r") for l in lines if l) else "\n"


def _rejoin(lines, eol, trailer):
    """Join back, restoring the file's ORIGINAL trailing shape.

    ``rstrip("\\r\\n") + eol`` collapsed however many trailing blank lines a human
    had left into exactly one newline — a multi-line diff for a one-line insertion,
    in a file this module promises only to insert into (iteration 3, L-15).
    *trailer* is what `_trailing_shape` measured before the edit.
    """
    text = "\n".join(lines).rstrip("\r\n")
    return text + (trailer if trailer else eol)


def _trailing_shape(text, eol):
    """The exact trailing whitespace of *text* (so it can be restored verbatim)."""
    stripped = text.rstrip("\r\n")
    trailer = text[len(stripped):]
    return trailer if trailer else eol


def insert_index_line(index_text, category, line):
    """Pure function: return index text with *line* routed into
    ``## <category>`` (section created alphabetically when absent).

    ``split("\\n")``, not ``splitlines()``: the latter also breaks on ``\\x0b``,
    ``\\x0c``, ``\\x1c-\\x1e``, ``\\x85``, ``U+2028`` and ``U+2029``, and it
    normalizes CRLF — so a one-line insertion silently rewrote the whole file's
    line endings and split any record line containing one of those characters into
    two. The work-item ledger was fixed for this in TASK 091 and **this module was
    not**, which is the asymmetry WI-7 is about (iteration 2, V12). Pair with
    ``atomic.read_verbatim`` on the read side.
    """
    lines = index_text.split("\n")
    eol = _eol_of(lines)
    trailer = _trailing_shape(index_text, eol)
    pad = "\r" if eol == "\r\n" else ""
    # Fenced regions are skipped, via the SAME scanner the work-item anchor uses.
    # Without it a `## <category>` heading or a `- **<ID>** …` example inside a
    # fence counted as the real thing, and the new pointer was inserted into the
    # code block — F3, on the sibling registry, a whole task later (iteration 3,
    # L-2). Both live ledgers and the shipped template already contain such a
    # fenced example.
    fenced = markdown.fenced_mask(index_text)

    def structural(index):
        return not fenced[index] and markdown.is_structure(lines[index])

    headings = [(i, m.group(1)) for i, m in
                ((i, _CATEGORY_HEADING_RE.match(l)) for i, l in enumerate(lines))
                if m and structural(i)]

    def section_end(start_idx):
        for j in range(start_idx + 1, len(lines)):
            if lines[j].startswith("## ") and structural(j):
                return j
        return len(lines)

    target = next(((i, cat) for i, cat in headings if cat == category), None)
    if target is None:
        # Compare against the SORTED heading list: taking the first heading that
        # sorts higher *in file order* put a new section in the wrong place in a
        # ledger whose sections had drifted out of order — and this file is
        # hand-maintained with no generator, so drift is its normal state
        # (iteration 3, L-24).
        insert_at = len(lines)
        later = sorted((cat for _, cat in headings if cat > category))
        if later:
            target_cat = later[0]
            insert_at = next(i for i, cat in headings if cat == target_cat)
        block = ["## %s%s" % (category, pad), pad, line + pad, pad]
        # keep exactly one blank line before a newly appended heading
        while insert_at > 0 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        block.insert(0, pad)
        lines[insert_at:insert_at] = block
        return _rejoin(lines, eol, trailer)

    start, end = target[0], section_end(target[0])
    id_match = _INDEX_ENTRY_RE.match(line)
    if id_match is None:  # only format_index_line produces these; be explicit
        raise CliError("index line %r does not match the pointer grammar" % line,
                       code=EXIT_FILING_CONFLICT, err_type="ContractError")
    new_key = _id_sort_key(id_match.group(1))
    insert_at = None
    last_entry = None
    for j in range(start + 1, end):
        match = _INDEX_ENTRY_RE.match(lines[j])
        if not match or not structural(j):
            continue
        last_entry = j
        if _id_sort_key(match.group(1)) > new_key and insert_at is None:
            insert_at = j
    if insert_at is None:
        insert_at = (last_entry + 1) if last_entry is not None else start + 2
        if last_entry is None and insert_at > len(lines):
            insert_at = end
    lines.insert(insert_at, line + pad)
    return _rejoin(lines, eol, trailer)


def _write_atomic(path, text):
    """Delegates to the shared primitive (see feedback_lib/atomic.py)."""
    atomic.write_atomic(path, text)


# --- frontmatter assembly ---------------------------------------------------

def _build_meta(issue_id, slug, status, opened_at, category, severity,
                extensions):
    """Assemble the record frontmatter IN CONTRACT ORDER, driven by the tuple.

    ``sources[key]`` is indexed, not ``.get()``: a key added to ``CONTRACT_KEYS``
    with no value here raises ``KeyError`` immediately rather than emitting a
    record missing a contract key. Mirrors ``ledger_backlog._build_meta`` — the
    two ledgers implement one contract, so their assembly should be readable
    side by side (WI-7).
    """
    sources = {"id": issue_id, "type": "known-issue", "status": status,
               "opened_at": opened_at, "category": category,
               "severity": severity, "slug": slug}
    meta = {}
    for key in CONTRACT_KEYS:
        value = sources[key]
        if value in (None, "", []):
            if key not in OPTIONAL_CONTRACT_KEYS:
                raise CliError(
                    "contract key %r is empty — a defect record cannot be "
                    "written without it" % key,
                    code=EXIT_FILING_CONFLICT, err_type="ContractError")
            continue
        meta[key] = value
    provenance = (extensions or {}).get("provenance")
    if not provenance and (extensions or {}).get("finding_ref"):
        provenance = body_mod.PROVENANCE_MACHINE
    for key in EXTENSION_KEYS:
        value = provenance if key == "provenance" else (extensions or {}).get(key)
        if value not in (None, "", []):
            meta[key] = value
    return meta


# --- the lockstep defect write ----------------------------------------------

def file_defect(config, issue_id, slug, title, category, body, status="open",
                severity=None, opened_at=None, extensions=None, dry_run=False):
    """Create ``<issues_dir>/<slug>.md`` + its index line, atomically-ish.

    Registry A's descriptor over the shared choreography in `ledger_core`.
    Signature and result-dict keys unchanged from before the extraction.
    """
    issues_dir = Path(config.issues_dir)
    resolved_at = opened_at or time.strftime("%Y-%m-%d")

    registry = ledger_core.Registry(
        noun="issue",
        records_dir=issues_dir,
        index_path=Path(config.index_path),
        status_vocab=STATUS_WRITE,
        rank_name="severity",
        rank_vocab=SEVERITY_WRITE,
        seed_text=seed_index_text,
        insert=lambda text, line, where: insert_index_line(text, category, line),
        format_line=format_index_line,
        build_meta=_build_meta,
        write_index=_write_atomic,
        require_repro=True,
    )
    result = ledger_core.file_record(
        registry, config, issue_id, slug, title, body, status,
        rank=severity, opened_at=opened_at, extensions=extensions,
        dry_run=dry_run,
        meta_kwargs={"issue_id": issue_id, "slug": slug, "status": status,
                     "opened_at": resolved_at, "category": category,
                     "severity": severity, "extensions": extensions},
        line_kwargs={"issue_id": issue_id, "title": title, "slug": slug,
                     "status": status, "opened_at": resolved_at,
                     "severity": severity},
    )
    out = {"issue_id": result["record_id"], "slug": result["slug"],
           "issue_path": result["record_path"],
           "index_path": result["index_path"],
           "index_line": result["index_line"],
           "seeded_index": result["seeded_index"],
           "dry_run": result["dry_run"]}
    if "record_text" in result:
        out["issue_text"] = result["record_text"]
    if "provisional_id" in result:
        out["provisional_id"] = result["provisional_id"]
    return out


# --- tolerant reads ---------------------------------------------------------

def list_issues(config, status=None, component=None, auto_fixable=None):
    """Frontmatter scan of the issues dir; tolerant of local vocab."""
    issues_dir = Path(config.issues_dir)
    out = []
    if not issues_dir.is_dir():
        return out
    for path in sorted(issues_dir.glob("*.md")):
        try:
            meta = frontmatter.parse_meta_only(path)
        except (OSError, CliError):
            # A malformed record must not abort a whole-ledger scan. The
            # duplicate-key refusal (sec-L-01) is a WRITE-side contract check;
            # applied to a tolerant read it would turn one tampered file into a
            # dead `issues` feed and a dead id allocator (audit 094 Risk 7 /
            # standing constraint 5). Skip the record, keep the scan alive.
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
