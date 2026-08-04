#!/usr/bin/env python3
"""
Rebase document-relative links when a markdown file moves between directories.

ARC-2. Archiving moves `docs/TASK.md` -> `docs/tasks/task-NNN-slug.md` and
`docs/PLAN.md` -> `docs/plans/plan-NNN-slug.md`. Every relative link in the
moved document was written against the OLD directory and silently denotes a
different path (or nothing) from the new one.

The rewrite is arithmetic, not a substitution:

    new_target = relpath(normpath(join(from_dir, target)), to_dir)

One expression covers every shape the corpus actually contains --
`../X -> ../../X`, `X.md -> ../X.md`, `tasks/y.md -> ../tasks/y.md` -- and stays
correct for any future layout change. A rule keyed on the literal string `../`
misses 38 of 56 real instances, measured on this repository.

Filesystem existence is the GUARD, never the trigger. The trigger is the move.

Decision table, per link:

    resolves    resolves
    from old    from new
    dir         dir (as written)   action
    --------    ----------------   -------------------------------------------
    yes         no                 REWRITTEN      the pure ARC-2 case
    yes         yes (same file)    UNCHANGED      denotation already identical
    yes         yes (other file)   REWRITTEN      + AMBIGUOUS_REBASE warning:
                                                  silence would re-point it
    no          yes                ACCIDENTAL_RESOLVE, left alone: it was broken
                                                  where written; rewriting turns
                                                  an accidentally-working link
                                                  into a definitely-broken one
    no          no                 PRE_BROKEN, left alone and reported

Anything whose old denotation escapes `repo_root` is left alone (ESCAPES_ROOT).

Idempotence falls out of the table rather than being bolted on: re-running the
same (from_dir, to_dir) over an already-rebased file lands in the
`no / yes` row, which never writes.

Exit codes: 0 clean / 1 rewrite or validation failed / 2 could not run /
3 completed with warnings.
"""

from __future__ import annotations

import os
import re
from typing import NamedTuple

#: Schemes and forms that are never document-relative.
_ABSOLUTE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|/|#)", re.IGNORECASE)

#: Fenced blocks: ``` or ~~~, any info string, closed by a fence at least as long.
_FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*?^[ \t]{0,3}\1[ \t]*$",
                    re.S | re.M)
#: An unterminated fence: everything from the opener to end of document.
_FENCE_OPEN = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*\Z", re.S | re.M)
#: Inline code span. Two boundary rules matter, and the naive `(`+)(?:.|\n)*?\1`
#: gets both wrong:
#:   1. The closing run must be the SAME length, not merely start with one. A
#:      lone backtick closed against the first character of a ``` run, leaving
#:      the mask desynchronized for the rest of the file.
#:   2. A code span cannot contain a blank line -- a blank line ends the
#:      paragraph. Without that bound an unbalanced backtick pairs with one
#:      hundreds of lines later and blanks every real link in between.
#: Measured on this corpus: (1)+(2) recover 3 real links in
#: docs/design/095_workflow_loop_contract.md that were invisible to the tool,
#: and keep masking all 13 links that are syntax examples inside code spans.
_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(?:[^\n]|\n(?![ \t]*\n))*?(?<!`)\1(?!`)")

# NOTE: indented code blocks are deliberately NOT masked. In this corpus a
# 4-or-more-space indent is overwhelmingly a lazy continuation of a list item,
# not a code block -- 8 of 42 real broken links sit at 6-space indent inside
# `- [ ]` continuations in docs/plans/plan-095-*.md alone. Masking them silently
# skipped 19% of the defect, which is the exact under-fix this tool exists to
# prevent. Fenced blocks and inline spans carry the real code.

#: Inline link / image target: `](target)` or `](<target>)`, optional title.
#: Deliberately does NOT require a preceding `[text]`, so link text containing
#: nested brackets still matches. Measured non-rule: tightening it to
#: `\[[^\]\n]*\]\(` changes 2 findings in the whole corpus, both `#anchor`
#: targets already dropped as absolute -- it buys nothing and costs recall. The
#: bare `](x)` shapes that could be false positives all sit inside code spans
#: and are killed by the _CODE_SPAN fix above, not by tightening this.
_INLINE = re.compile(r"\]\(\s*(<[^>\n]*>|[^)\s]+)")
#: Reference definition: `[id]: target`
_REFDEF = re.compile(r"^[ ]{0,3}\[[^\]\n]+\]:[ \t]*(<[^>\n]*>|\S+)", re.M)
#: HTML attributes.
_HTML_ATTR = re.compile(r"""\b(?:href|src)\s*=\s*(?:"([^"\n]*)"|'([^'\n]*)')""",
                        re.IGNORECASE)


class LinkRecord(NamedTuple):
    line: int
    authored: str          # target exactly as written
    denotes_old: str       # repo-relative path it denoted from from_dir
    action: str            # REWRITTEN | UNCHANGED | PRE_BROKEN | ...
    new_target: str        # target after rewrite (== authored when untouched)


ACTIONS_WARN = ("PRE_BROKEN", "ACCIDENTAL_RESOLVE", "ESCAPES_ROOT",
                "AMBIGUOUS_REBASE", "UNMAPPED_SLOT")
#: Actions that actually wrote a new target.
_WROTE = ("REWRITTEN", "SLOT_RESOLVED", "AMBIGUOUS_REBASE")
#: Actions subject to the conservation law -- their target resolved BEFORE the
#: move, so it must resolve after. SLOT_RESOLVED is excluded on purpose: see the
#: conservation block in main() for why a declared identity is not probed.
_CONSERVED = ("REWRITTEN", "AMBIGUOUS_REBASE")

#: Repo-relative paths that are SLOTS, not identities: the artifact living there
#: rotates. Knowing them intrinsically is what makes the safe behaviour the
#: DEFAULT. When a link denotes one of these and the caller supplied no identity
#: for it, rewriting the path would re-point the citation at whatever is live
#: now -- turning a dead link into a confidently wrong one, invisible to every
#: link checker because it resolves. So the link is left exactly as authored and
#: reported as UNMAPPED_SLOT.
KNOWN_SLOTS = ("docs/TASK.md", "docs/PLAN.md")


def _mask(text: str) -> str:
    """Blank non-prose regions, preserving length and newlines.

    Offsets in the masked text therefore address the original text exactly, so
    matches found here can be spliced back without a second parse.
    """
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))

    masked = _FENCE.sub(blank, text)
    masked = _FENCE_OPEN.sub(blank, masked)
    masked = _CODE_SPAN.sub(blank, masked)
    return masked


def _targets(masked: str):
    """Yield (start, end, raw_target) for every link target in masked text."""
    for rx in (_INLINE, _REFDEF):
        for m in rx.finditer(masked):
            yield m.start(1), m.end(1), m.group(1)
    for m in _HTML_ATTR.finditer(masked):
        gi = 1 if m.group(1) is not None else 2
        yield m.start(gi), m.end(gi), m.group(gi)


def _split_fragment(target: str):
    """-> (path, suffix). Suffix keeps `#anchor` and any `?query` verbatim."""
    for sep in ("#", "?"):
        i = target.find(sep)
        if i != -1:
            return target[:i], target[i:]
    return target, ""


def rebase_document_links(text: str, from_dir: str, to_dir: str,
                          repo_root: str = ".", slot_map: dict | None = None):
    """Re-express every document-relative link from `from_dir` against `to_dir`.

    Args:
        text: the document's full content.
        from_dir: directory the document used to live in (repo-relative).
        to_dir: directory it lives in now (repo-relative).
        repo_root: root that paths must not escape.
        slot_map: repo-relative MUTABLE SLOT -> the archived identity it held
            at the moment of this move, e.g.
            ``{"docs/TASK.md": "docs/tasks/task-063-framework-installer.md"}``.
            Checked BEFORE any filesystem probe, so it still works after the
            slot file has already been moved away by a sibling step.

    Returns:
        (new_text, [LinkRecord]). `new_text is text` when nothing was rewritten.
    """
    root = os.path.abspath(repo_root)
    old_base = os.path.join(root, from_dir)
    new_base = os.path.join(root, to_dir)
    slots = {os.path.normpath(os.path.join(root, k)):
             os.path.normpath(os.path.join(root, v))
             for k, v in (slot_map or {}).items()}
    known_slots = {os.path.normpath(s) for s in KNOWN_SLOTS}

    masked = _mask(text)
    edits, records = [], []

    for start, end, raw in _targets(masked):
        authored = raw
        bare = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
        if not bare or _ABSOLUTE.match(bare):
            continue

        path, suffix = _split_fragment(bare)
        if not path:                       # pure `#anchor`
            continue

        line = text.count("\n", 0, start) + 1
        denote_old = os.path.normpath(os.path.join(old_base, path))
        denote_new = os.path.normpath(os.path.join(new_base, path))

        if os.path.commonpath([root, denote_old]) != root:
            records.append(LinkRecord(line, authored, denote_old,
                                      "ESCAPES_ROOT", authored))
            continue

        # A MUTABLE SLOT is checked first, and without touching the filesystem.
        #
        # `docs/TASK.md` is a slot, not an identity: the link was written when
        # the slot held THIS task's spec. Preserving the path preserves the
        # wrong thing -- it would re-point the citation at whatever task is
        # current. Preserving the referent means naming the archive the slot
        # held at this moment. Doing it before any existence probe is what makes
        # it work when a sibling step has already emptied the slot.
        if denote_old in slots:
            identity = slots[denote_old]
            new_path = os.path.relpath(identity, new_base)
            if os.sep != "/":
                new_path = new_path.replace(os.sep, "/")
            new_target = new_path + suffix
            if raw.startswith("<"):
                new_target = f"<{new_target}>"
            records.append(LinkRecord(line, authored,
                                      os.path.relpath(identity, root),
                                      "SLOT_RESOLVED", new_target))
            edits.append((start, end, new_target))
            continue

        # A known slot with no identity supplied is NEVER rewritten. Rebasing
        # the path here is what converts "dead" into "silently wrong".
        if os.path.relpath(denote_old, root) in known_slots:
            records.append(LinkRecord(line, authored,
                                      os.path.relpath(denote_old, root),
                                      "UNMAPPED_SLOT", authored))
            continue

        resolved_old = os.path.exists(denote_old)
        resolved_new = os.path.exists(denote_new)
        rel_old = os.path.relpath(denote_old, root)

        if not resolved_old:
            action = "ACCIDENTAL_RESOLVE" if resolved_new else "PRE_BROKEN"
            records.append(LinkRecord(line, authored, rel_old, action, authored))
            continue

        if denote_old == denote_new:
            records.append(LinkRecord(line, authored, rel_old, "UNCHANGED",
                                      authored))
            continue

        new_path = os.path.relpath(denote_old, new_base)
        if os.sep != "/":
            new_path = new_path.replace(os.sep, "/")
        new_target = new_path + suffix
        if raw.startswith("<"):
            new_target = f"<{new_target}>"

        # `resolved_new` here means the untouched text ALSO resolves from the
        # new home -- to a different file. Rewriting is still correct (the
        # denotation is what we preserve), but the silent case is not this one.
        action = "AMBIGUOUS_REBASE" if resolved_new else "REWRITTEN"
        records.append(LinkRecord(line, authored, rel_old, action, new_target))
        edits.append((start, end, new_target))

    if not edits:
        return text, records

    out, cursor = [], 0
    for start, end, replacement in sorted(edits):
        out.append(text[cursor:start])
        out.append(replacement)
        cursor = end
    out.append(text[cursor:])
    return "".join(out), records


def rebase_file(path: str, from_dir: str, to_dir: str, repo_root: str = ".",
                dry_run: bool = False, slot_map: dict | None = None):
    """Apply :func:`rebase_document_links` to a file in place.

    Reads and writes with ``newline=""`` so CRLF documents round-trip.
    """
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    new_text, records = rebase_document_links(text, from_dir, to_dir, repo_root,
                                              slot_map)
    changed = new_text != text
    if changed and not dry_run:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_text)
    return changed, records


def _main(argv=None):
    import argparse
    import json
    import sys

    ap = argparse.ArgumentParser(
        description="Rebase document-relative links after a file moves "
                    "(ARC-2). The move is the trigger; existence is the guard.")
    ap.add_argument("files", nargs="+", help="moved markdown file(s)")
    ap.add_argument("--from", dest="from_dir", required=True,
                    help="directory the file used to live in (repo-relative)")
    ap.add_argument("--to", dest="to_dir", required=True,
                    help="directory it lives in now (repo-relative)")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--slot", action="append", default=[], metavar="SLOT=ARCHIVE",
                    help="a mutable slot and the archive identity it held, e.g. "
                         "docs/PLAN.md=docs/plans/plan-096-x.md. Repeatable. "
                         "Resolved before any filesystem probe, so it still "
                         "works once the slot file has been moved away.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    slot_map = {}
    for pair in args.slot:
        if "=" not in pair:
            print(json.dumps({"ok": False,
                              "error": f"--slot expects SLOT=ARCHIVE, got {pair!r}"}),
                  file=sys.stderr)
            return 2
        slot, archive = pair.split("=", 1)
        slot_map[slot.strip()] = archive.strip()

    report, warned, failed, pending = [], False, False, []
    for path in args.files:
        try:
            changed, records = rebase_file(path, args.from_dir, args.to_dir,
                                           args.repo_root, args.dry_run,
                                           slot_map)
        except OSError as exc:
            print(json.dumps({"ok": False, "error": f"{path}: {exc}"}),
                  file=sys.stderr)
            return 2

        # Conservation law: every file denoted before the move is denoted after.
        #
        # SLOT_RESOLVED is deliberately exempt. A slot map is a FORWARD
        # reference -- the caller declares what the slot is becoming, and in the
        # documented archive order that file does not exist yet: Step 5.5 rebases
        # the TASK naming `docs/plans/plan-NNN-x.md`, which Step 7 only creates
        # afterwards. Probing it here made the protocol's own happy path exit 1
        # ("a link regressed") and, read literally, told the agent to stop.
        # Policing the caller's archiving sequence is not this tool's job; the
        # protocol's closing validation is where a wrong slot map is caught.
        # A pending target is still surfaced below, just not as a failure.
        for r in records:
            if r.action in _CONSERVED:
                target = os.path.normpath(
                    os.path.join(args.repo_root, args.to_dir,
                                 _split_fragment(r.new_target.strip("<>"))[0]))
                if not os.path.exists(target):
                    failed = True
            elif r.action == "SLOT_RESOLVED":
                target = os.path.normpath(
                    os.path.join(args.repo_root, args.to_dir,
                                 _split_fragment(r.new_target.strip("<>"))[0]))
                if not os.path.exists(target):
                    pending.append(f"{path}:{r.line} -> {r.new_target}")

        entry = {"file": path, "changed": changed,
                 "links": [r._asdict() for r in records]}
        report.append(entry)
        if any(r.action in ACTIONS_WARN for r in records):
            warned = True

    if args.json:
        print(json.dumps({"ok": not failed, "files": report,
                          "slot_targets_pending": pending},
                         ensure_ascii=False, indent=1))
    else:
        for entry in report:
            for r in entry["links"]:
                if r["action"] == "UNCHANGED":
                    continue
                print(f"[{r['action']}] {entry['file']}:{r['line']}  "
                      f"{r['authored']}"
                      + (f"  ->  {r['new_target']}" if r["action"] in _WROTE
                         else ""))
        n = sum(1 for e in report for r in e["links"] if r["action"] in _WROTE)
        w = sum(1 for e in report for r in e["links"] if r["action"] in ACTIONS_WARN)
        for p in pending:
            print(f"[SLOT_PENDING] {p}  (declared identity, not yet on disk)")
        print(f"{n} rewritten / {w} needing review"
              + (" (dry run)" if args.dry_run else ""))

    if failed:
        return 1
    return 3 if warned else 0


if __name__ == "__main__":
    import sys
    sys.exit(_main())
