"""Issue ID allocation and slug normalization.

The live ID namespace is messy on purpose-of-history: ``TF-X-7`` (dash
inside the prefix), ``XLSX-10B-DEFER`` (letter suffix on the number),
``HTML2MD-11-BUG`` (word suffix). Allocation is therefore anchored on the
CONFIGURED prefix: for prefix ``P`` every id matching
``^P-(\\d+)([A-Z-].*)?$`` contributes its integer; next id = max + 1
(never gap-filling — matches task_id_tool semantics). IDs that do not
match contribute nothing and never crash the scan.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from . import frontmatter
from .envelope import EXIT_USAGE, CliError


def normalize_slug(text):
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("_", "-").replace(" ", "-")
    text = re.sub(r"[^a-z0-9-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text


def prefix_for(component, id_prefixes):
    """Resolve the ID prefix for a component from the config map."""
    if component and component in id_prefixes:
        return id_prefixes[component]
    default = id_prefixes.get("_default")
    if not default:
        raise CliError(
            "no ID prefix configured for component %r and no _default set"
            % component, code=EXIT_USAGE, err_type="UsageError",
            remediation="add the component to id_prefixes in docs/feedback/config.json")
    return default


def existing_ids(issues_dir, recursive=False):
    """Every frontmatter ``id:`` value found under *issues_dir*.

    ``recursive=True`` also walks subdirectories: a record archived into
    ``docs/backlog/archive/`` is still holding its id, and a non-recursive scan
    silently freed it for reuse (vdd-multi iteration 2, V2). Allocation keeps
    the flat scan (a subdir is not the next-number namespace); uniqueness
    verification uses the recursive one.
    """
    issues_dir = Path(issues_dir)
    if not issues_dir.is_dir():
        return []
    out = []
    for path in sorted(issues_dir.rglob("*.md") if recursive
                       else issues_dir.glob("*.md")):
        try:
            meta, _ = frontmatter.parse_file(path)
        except OSError:
            continue
        value = meta.get("id")
        if value:
            out.append(str(value))
    return out


def next_number(issues_dir, prefix):
    pattern = re.compile(r"^%s-(\d+)(?:[A-Z-].*)?$" % re.escape(prefix))
    highest = 0
    for value in existing_ids(issues_dir):
        match = pattern.match(value)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def allocate(issues_dir, prefix, title):
    """Return (issue_id, slug) for a new issue; slug must not be empty."""
    number = next_number(issues_dir, prefix)
    issue_id = "%s-%d" % (prefix, number)
    slug = normalize_slug("%s-%s" % (issue_id, title))
    if slug == normalize_slug(issue_id):
        raise CliError(
            "title %r normalizes to an empty slug (non-latin title?) — pass "
            "an explicit --slug" % title,
            code=EXIT_USAGE, err_type="UsageError")
    return issue_id, slug
