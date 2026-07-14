"""The ledger-surface hashes, defined ONCE.

Both the instrumentation injected into the sandbox CLI and the grader import this exact
module, so the "before" and "after" hashes can never drift apart from a copy-paste.

Surfaces are hashed SEPARATELY, and one of them semantically, because "the CLI owns this
file" is false for KNOWN_ISSUES.md taken as a whole:

  issues_files   docs/issues/**        — CLI-owned outright. Any hand-written issue file is
                                         a lockstep violation.
  index_lines    the `- **ID** …` issue lines of the index, as a SET — CLI-owned. Hashing the
                                         whole file would be wrong: SKILL.md §7.6 explicitly
                                         tells the agent to hand-add a row to the
                                         prefix→category TABLE ("the script warns; the table
                                         edit is yours"). That legitimate preamble edit must
                                         not read as a forged index line, and a forged index
                                         line must not hide behind it.
  backlog        docs/BACKLOG.md       — CLI-owned via `file --as work-item`… except during
                                         bootstrap, where the agent creates it. Cases opt out.
  config         docs/feedback/**      — NOT CLI-owned: bootstrap has the agent finish init's
                                         todo by hand. Excluded from the default scope set.
  feedback_state .agent/feedback/**    — CLI-owned. Hand-editing an inbox finding breaks
                                         fingerprint dedup and the audit trail.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

TREE_SCOPES = {
    "issues_files": ["docs/issues"],
    "backlog": ["docs/BACKLOG.md"],
    "config": ["docs/feedback"],
    # The AUDIT TRAIL specifically — finding records and the journal — not the whole
    # .agent/feedback tree. §5 explicitly allows the skill to write anywhere under
    # .agent/feedback/** (it is gitignored machine state), and agents do legitimately drop a
    # scratch issue-body draft there. Hashing the whole tree scored that as a hand-edit. What
    # must never be touched outside the CLI is a finding JSON (it would break fingerprint
    # dedup) or the journal (it would break the audit trail).
    "feedback_state": [
        ".agent/feedback/inbox",
        ".agent/feedback/filed",
        ".agent/feedback/dismissed",
        ".agent/feedback/journal",
    ],
}

# Scopes the CLI is expected to own exclusively in a normal (non-bootstrap) case.
DEFAULT_SCOPES = ["issues_files", "index_lines", "backlog", "feedback_state"]

INDEX_REL = "docs/KNOWN_ISSUES.md"


def _tree(root: Path, subs) -> str:
    h = hashlib.sha256()
    for sub in subs:
        base = root / sub
        if not base.exists():
            h.update(b"\x00absent:" + str(sub).encode())
        elif base.is_file():
            h.update(str(sub).encode() + b"\x00")
            h.update(hashlib.sha256(base.read_bytes()).digest())
        else:
            for p in sorted(base.rglob("*")):
                if p.is_file():
                    h.update(str(p.relative_to(root)).encode() + b"\x00")
                    h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()[:32]


def index_lines(root: Path) -> list[str]:
    """The index's issue lines only. The template's format-example line carries `<ID>`
    placeholders — it is documentation, not an issue, and is excluded."""
    p = root / INDEX_REL
    if not p.exists():
        return []
    return [
        ln.strip() for ln in p.read_text().splitlines()
        if ln.startswith("- **") and "<ID>" not in ln
    ]


def scope_hashes(root: Path) -> dict[str, str]:
    out = {name: _tree(root, subs) for name, subs in TREE_SCOPES.items()}
    lines = index_lines(root)
    h = hashlib.sha256()
    for ln in sorted(lines):
        h.update(ln.encode() + b"\x00")
    out["index_lines"] = h.hexdigest()[:32]
    return out
