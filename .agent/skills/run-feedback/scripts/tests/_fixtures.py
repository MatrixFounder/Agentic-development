"""Shared hermetic fixture helpers for the run-feedback unittest suite.

No real git is required: ``config.find_repo_root`` only checks that a
``.git`` entry EXISTS, and ``config.main_worktree_root`` falls back to
``repo_root`` when ``git rev-parse`` fails — which it does inside these
bare fixture repos (an empty ``.git`` dir is not a valid gitdir).
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Hermeticity: a config file leaked in from the outer environment would
# silently re-point every fixture at a foreign repo.
os.environ.pop("RUN_FEEDBACK_CONFIG", None)


def make_repo(tmp):
    """Turn *tmp* into a minimal fixture 'repo' (bare .git dir marker)."""
    root = Path(tmp).resolve()
    (root / ".git").mkdir(parents=True, exist_ok=True)
    return root


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def load_cfg(root):
    from feedback_lib.config import load_config
    return load_config(repo_root=str(root))


def run_cli(argv):
    """Call run_feedback.main() in-process; returns (code, stdout, stderr)."""
    import run_feedback
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = run_feedback.main([str(a) for a in argv])
    return code, out.getvalue(), err.getvalue()


def tree_hash(root):
    """Content hash of an entire directory tree (paths + file bytes)."""
    root = Path(root)
    entries = []
    for base, dirs, files in os.walk(str(root)):
        rel = os.path.relpath(base, str(root))
        for d in dirs:
            entries.append(("dir", os.path.normpath(os.path.join(rel, d)), ""))
        for f in files:
            full = os.path.join(base, f)
            digest = hashlib.sha256(Path(full).read_bytes()).hexdigest()
            entries.append(
                ("file", os.path.normpath(os.path.join(rel, f)), digest))
    entries.sort()
    return hashlib.sha256(json.dumps(entries).encode("utf-8")).hexdigest()


ISSUE_TMPL = """---
id: {id}
type: known-issue
status: {status}
opened_at: {opened_at}
category: {category}
{severity_line}slug: {slug}
{extra}---
# {id} — {title}

{body}
"""


def write_issue(issues_dir, issue_id, slug, title="Fixture issue",
                status="open", opened_at="2026-01-01", category="logic",
                severity=None, extra_lines=(), body="Body."):
    severity_line = "severity: %s\n" % severity if severity else ""
    extra = "".join(line + "\n" for line in extra_lines)
    text = ISSUE_TMPL.format(id=issue_id, status=status, opened_at=opened_at,
                             category=category, severity_line=severity_line,
                             slug=slug, extra=extra, title=title, body=body)
    return write(Path(issues_dir) / (slug + ".md"), text)


INDEX_FIXTURE = """# Known Issues & Tech Debt

**Purpose:** fixture ledger for the run-feedback test suite.

---

## Rules / Conventions

> The index below is hand-maintained — this preamble must never be touched
> by the filing engine. | pipes # hashes — all preserved verbatim.

**Index line format:** see the known-issues-format skill.

---

## correctness

- **RF-1** [First issue](issues/rf-1-first-issue.md) — status `open`, opened 2026-01-01
- **RF-3** [Third issue](issues/rf-3-third-issue.md) — status `open`, opened 2026-01-02

## robustness

- **RF-4** [Fourth issue](issues/rf-4-fourth-issue.md) — status `open`, opened 2026-01-03
"""

BACKLOG_FIXTURE = """# Product Backlog

## Discovered Issues

<!-- feedback:discovered-issues -->
- **Old item (2026-01-01)** — pre-existing bullet

## Other

Unrelated section text.
"""
