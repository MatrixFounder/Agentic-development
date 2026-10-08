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

Exit codes:
  0  clean
  1  a declared-present slot target does not exist (requires --slot-must-exist)
  2  could not run
  3  completed with warnings

ARC-5 measured that exit 1 was unreachable before `--slot-must-exist` existed.
The conservation probe it guarded re-derives its target by `relpath` from a path
whose existence was already proven, so it reconstructs an existing path in every
case. That probe is retained as a postcondition on the rewrite arithmetic, but
it is not the gate that catches a wrong slot map -- `--slot-must-exist` is.

Inbound mode (TASK 115, `skill-archive-task` Step 8). With `--inbound` as the
first argument, the remaining arguments go to `main(argv)` of `slot_links.py`:

    rebase_links.py --inbound --task docs/tasks/task-<ID>-<slug>.md
        [--plan docs/plans/plan-<ID>-<slug>.md] [--since <rev>] [--dry-run] [--json]

It re-targets the slot links that an archived task wrote in other documents, and
lists the others. The allow rule that names this script covers the mode, so
archiving stays automatic (TASK 111 D13). Its exit codes are those of
`slot_links.py`.
"""

import os
import sys

# Run as a script, under the allow rule, three steps precede every import but `os` and `sys`
# (TASK 115 R1.2, as TASK 112 R1.8 does for `archive_move.py`):
# - its own directory leaves `sys.path`, so no file planted beside the script answers an import:
#   not a standard-library name, not one the standard library lacks on this platform (`subprocess`
#   imports `msvcrt` on POSIX), and not a sibling's name; the inbound mode loads its siblings by
#   explicit path (`_load_siblings`);
# - no bytecode is written, and `.pyc` files are looked up under the null device, where none can
#   exist, so a `.pyc` planted in `__pycache__/` is never read.
# The module has no `from __future__` statement: at run time it imports `__future__`.
if __name__ == "__main__":
    _HERE = os.path.dirname(os.path.realpath(__file__))
    sys.path[:] = [entry for entry in sys.path if os.path.realpath(entry or os.curdir) != _HERE]
    sys.dont_write_bytecode = True
    sys.pycache_prefix = os.path.join(os.devnull, "rebase-links-pycache")

import re  # noqa: E402
import stat  # noqa: E402
from typing import NamedTuple  # noqa: E402

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
#: The grammar of `archive_move.SLUG`, held here so the file mode loads no sibling (TASK 115
#: R1.2, TASK 116 R8.3). TC-G28 pins the two equal.
_SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
#: TASK 116 R8.1: the slots that `--slot` takes, each with the form of the archive it names.
_SLOT_ARCHIVES = {
    "docs/TASK.md": ("docs/tasks/task-<ID>-<slug>.md",
                     re.compile(rf"docs/tasks/task-[0-9]{{3,}}-{_SLUG}\.md")),
    "docs/PLAN.md": ("docs/plans/plan-<ID>-<slug>.md",
                     re.compile(rf"docs/plans/plan-[0-9]{{3,}}-{_SLUG}\.md")),
}


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


def _git_dirs(cwd):
    """The repository's git directories, as real paths (TASK 112 R4.1).

    The `.git` of the working directory, or of its nearest ancestor that has one. In a linked
    worktree `.git` is a file naming the worktree's git directory, whose `commondir` names the
    main one; both count.
    """
    here = os.path.realpath(cwd)
    while True:
        dot = os.path.join(here, ".git")
        if os.path.isdir(dot):
            return [os.path.realpath(dot)]
        if os.path.isfile(dot):
            break
        parent = os.path.dirname(here)
        if parent == here:
            return []
        here = parent
    try:
        with open(dot, encoding="utf-8") as fh:
            line = fh.readline().strip()
    except (OSError, UnicodeDecodeError):
        return []
    if not line.startswith("gitdir:"):
        return []
    gitdir = os.path.realpath(os.path.join(here, line[len("gitdir:"):].strip()))
    dirs = [gitdir]
    try:
        with open(os.path.join(gitdir, "commondir"), encoding="utf-8") as fh:
            dirs.append(os.path.realpath(os.path.join(gitdir, fh.read().strip())))
    except (OSError, UnicodeDecodeError):
        pass
    return dirs


def _under_git(path, cwd):
    """True when `path` lies under the repository's git directory (TASK 112 R4.1).

    A segment named `.git` in any letter case counts: a case-insensitive file system resolves
    `.GIT` to `.git`. So does any existing ancestor of the real path (links resolved before `..`)
    that is a git directory of `_git_dirs` by file identity, which a firmlink or a Unicode
    normalisation of the spelling does not hide.
    """
    absolute = os.path.normpath(os.path.join(cwd, path))
    segments = os.path.relpath(absolute, cwd).split(os.sep)
    if any(segment.casefold() == ".git" for segment in segments):
        return True
    gits = []
    for git in _git_dirs(cwd):
        try:
            gits.append(os.stat(git))
        except OSError:
            pass
    probe = os.path.realpath(os.path.join(cwd, path))
    while gits:
        try:
            st = os.stat(probe)
        except OSError:
            st = None
        if st is not None and any(os.path.samestat(st, git) for git in gits):
            return True
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent
    return False


#: TASK 116 R8.7: the characters a rewrite may add to a link; any other is counted.
_LINK_SAFE = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._~/%-")


def _adds_characters(authored, new):
    """True when `new` holds a character outside `_LINK_SAFE` more often than `authored` does.

    Each character is counted on its own (TASK 116 R8.7). A link to a file named with a space,
    authored as `<a b.md>`, keeps its space when it is rebased.
    """
    def counts(text):
        found = {}
        for ch in text:
            if ch not in _LINK_SAFE:
                found[ch] = found.get(ch, 0) + 1
        return found
    before = counts(authored)
    return any(n > before.get(ch, 0) for ch, n in counts(new).items())


def _adds_parts(record):
    """True when a part of the new target's path is not one its author wrote (TASK 116 R8.7).

    A part, between `/`, other than `.` and `..`, must be a part of the authored target's path,
    or, for a slot link, of the archive it names. A rewrite may drop parts and add `..`.
    """
    def parts(target):
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        return set(_split_fragment(target)[0].split("/")) - {"", ".", ".."}
    known = parts(record.authored)
    if record.action == "SLOT_RESOLVED":
        known |= parts(record.denotes_old)
    return not parts(record.new_target) <= known


def _refuse_operand(path):
    """Why `_main` refuses to rewrite this file operand, or None (TASK 112 R4.1, TASK 116 R1.1).

    `Bash(python3 .agent/tools/rebase_links.py *)` approves any operand, and the rewrite writes the
    file in place. A file outside the working directory, by its absolute path normalised without
    resolving links, is refused; so is a file under `.git/` (`_under_git`), a symbolic link, and a
    file with a second hard link, which would write through to another name. Then a file whose
    directory resolves outside the working directory, both by real path, is refused: a directory
    link would carry the write there. The directory is the operand's own, resolved as the kernel
    resolves it, each link before the `..` that follows it. Last, an operand that does not lie
    under `docs/`, and then a name that does not end in `.md`, is refused (TASK 116 R8.2): only
    a markdown file under `docs/` is this script's to rewrite. `rebase_file()` keeps no such
    guard: `archive_protocol.py` calls it with temporary paths.
    """
    cwd = os.getcwd()
    absolute = os.path.normpath(os.path.join(cwd, path))
    if os.path.commonpath([absolute, cwd]) != cwd or absolute == cwd:
        return "lies outside the working directory"
    if _under_git(path, cwd):
        return "lies under .git/"
    if os.path.islink(path):
        return "is a symbolic link"
    if os.path.exists(path) and os.lstat(path).st_nlink != 1:
        return "has a second hard link"
    real_cwd = os.path.realpath(cwd)
    directory = os.path.realpath(os.path.dirname(os.path.join(cwd, path)))
    if os.path.commonpath([directory, real_cwd]) != real_cwd:
        return "its directory resolves outside the working directory"
    if os.path.relpath(absolute, cwd).split(os.sep)[0] != "docs":
        return "does not lie under docs/"
    if not path.endswith(".md"):
        return "is not a markdown file"
    return None


class _Unsafe(Exception):
    """An operand that the file mode refuses to read or to write (TASK 116 R7)."""


def _check_descriptor(fd, path, cwd):
    """The `fstat` of `fd`, if it is the regular file at `path`'s real path (TASK 116 R7.2).

    The real path is `path` joined to `cwd` and resolved as the kernel resolves it. The directory
    of the descriptor's own path (`_descriptor_path`), or of the real path where the platform
    gives none, lies inside `cwd` by real path. Any other descriptor raises `_Unsafe` with its
    reason.
    """
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode):
        raise _Unsafe("is not a regular file")
    if st.st_nlink != 1:
        raise _Unsafe(f"has {st.st_nlink} hard links")
    try:
        real = os.path.realpath(os.path.join(cwd, path))
        now = os.stat(real)
    except (OSError, ValueError):
        raise _Unsafe("is not the file at its real path") from None
    if (now.st_dev, now.st_ino) != (st.st_dev, st.st_ino):
        raise _Unsafe("is not the file at its real path")
    try:
        where = _descriptor_path(fd) or real
    except OSError:
        raise _Unsafe("is not the file at its real path") from None
    real_cwd = os.path.realpath(cwd)
    if os.path.commonpath([os.path.dirname(where), real_cwd]) != real_cwd:
        raise _Unsafe("its directory resolves outside the working directory")
    return st


def _descriptor_path(fd):
    """The path the kernel holds for `fd`, or None where the platform gives none (TASK 116 R7.2).

    `fcntl.F_GETPATH` gives it on darwin, and the link `/proc/self/fd/<fd>` on Linux. It is one
    lookup, so no swap of a directory between two lookups by name can change it, as one can
    between `realpath` and `stat`. A failed lookup raises `OSError`.
    """
    try:
        import fcntl
    except ImportError:
        fcntl = None
    if hasattr(fcntl, "F_GETPATH"):
        return os.fsdecode(fcntl.fcntl(fd, fcntl.F_GETPATH, bytes(1024)).split(b"\0", 1)[0])
    if os.path.isdir("/proc/self/fd"):
        return os.readlink(f"/proc/self/fd/{fd}")
    return None


def _open_checked(path, cwd, flags):
    """`(descriptor, fstat)` of `path` opened with `flags` and no link followed (TASK 116 R7.1)."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise _Unsafe("this platform has no O_NOFOLLOW")
    try:
        fd = os.open(path, flags | nofollow | getattr(os, "O_NONBLOCK", 0))
    except OSError as exc:
        raise _Unsafe(f"cannot open it: {exc.strerror or exc}") from None
    try:
        return fd, _check_descriptor(fd, path, cwd)
    except BaseException:
        os.close(fd)
        raise


def _read_descriptor(fd):
    """Every byte of the file open on `fd`, from its start."""
    chunks = []
    while chunk := os.read(fd, 1 << 16):
        chunks.append(chunk)
    return b"".join(chunks)


def _write_checked(path, cwd, read_st, data):
    """Write `data` over `path` through a second descriptor of the inode read (TASK 116 R7.3).

    The file is truncated first, as the base's `open(path, "w")` truncates it, so a write that
    fails leaves a prefix of `data`.
    """
    fd, st = _open_checked(path, cwd, os.O_WRONLY)
    try:
        if (st.st_dev, st.st_ino) != (read_st.st_dev, read_st.st_ino):
            raise _Unsafe("changed during the run")
        os.ftruncate(fd, 0)
        view, written = memoryview(data), 0
        while written < len(data):
            written += os.write(fd, view[written:])
        os.fsync(fd)
    finally:
        os.close(fd)


def _load_siblings():
    """The `slot_links` module, its siblings loaded by explicit path (TASK 115 R1.2).

    No sibling is found by a path search, so a package or an extension module planted beside the
    script under a sibling's name is never chosen. `rebase_links` is this module, whether it runs
    as `__main__` or was imported; `slot_links` finds all three in `sys.modules`.
    """
    import importlib.util
    here = os.path.dirname(os.path.realpath(__file__))
    sys.modules.setdefault("rebase_links", sys.modules[__name__])
    for name in ("archive_move", "task_id_tool", "slot_links"):
        if name in sys.modules:
            continue
        spec = importlib.util.spec_from_file_location(name, os.path.join(here, f"{name}.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            del sys.modules[name]
            raise
    return sys.modules["slot_links"]


def _main(argv=None):
    import argparse
    import json

    argv = sys.argv[1:] if argv is None else list(argv)
    if argv[:1] == ["--inbound"]:
        # TASK 115 R1.1: `skill-archive-task` Step 8, loaded here only, so the file mode never
        # loads the inbound module.
        return _load_siblings().main(argv[1:])

    ap = argparse.ArgumentParser(
        description="Rebase document-relative links after a file moves "
                    "(ARC-2). The move is the trigger; existence is the guard.",
        epilog="Inbound mode: rebase_links.py --inbound --task docs/tasks/task-<ID>-<slug>.md "
               "[--plan docs/plans/plan-<ID>-<slug>.md] [--since <rev>] [--dry-run] [--json] "
               "re-targets the slot links an archived task wrote in other documents "
               "(TASK 115, skill-archive-task Step 8).")
    ap.add_argument("files", nargs="+",
                    help="moved markdown file(s) under docs/; any other operand is refused")
    ap.add_argument("--from", dest="from_dir", required=True,
                    help="directory the file used to live in (repo-relative)")
    ap.add_argument("--to", dest="to_dir", required=True,
                    help="directory it lives in now (repo-relative)")
    ap.add_argument("--repo-root", default=".",
                    help="the working directory, the only root the file mode takes")
    ap.add_argument("--slot", action="append", default=[], metavar="SLOT=ARCHIVE",
                    help="a mutable slot and the archive identity it held, e.g. "
                         "docs/PLAN.md=docs/plans/plan-096-x.md. Repeatable. SLOT is "
                         "docs/TASK.md, with ARCHIVE docs/tasks/task-<ID>-<slug>.md, or "
                         "docs/PLAN.md, with ARCHIVE docs/plans/plan-<ID>-<slug>.md. "
                         "Resolved before any filesystem probe, so it still "
                         "works once the slot file has been moved away.")
    ap.add_argument("--slot-must-exist", action="store_true",
                    help="assert every --slot target is already on disk; a "
                         "missing one exits 1 instead of being reported as "
                         "pending. Pass it where the target was created BEFORE "
                         "this call (skill-archive-task Step 7.6.5); omit it "
                         "for a forward reference (Step 5.5).")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    # TASK 116 R8.6: a rewritten link is built from these paths, so each stays in the tree.
    if os.path.realpath(args.repo_root) != os.path.realpath(os.getcwd()):
        problem = "--repo-root is not the working directory"
    else:
        problem = next((f"{name} does not lie inside the working directory"
                        for name, value in (("--from", args.from_dir), ("--to", args.to_dir))
                        if os.path.isabs(value)
                        or os.path.normpath(value).split(os.sep)[0] == ".."), None)
    if problem:
        print(json.dumps({"ok": False, "error": problem}), file=sys.stderr)
        return 2

    slot_map = {}
    for pair in args.slot:
        if "=" not in pair:
            print(json.dumps({"ok": False,
                              "error": f"--slot expects SLOT=ARCHIVE, got {pair!r}"}),
                  file=sys.stderr)
            return 2
        slot, archive = (part.strip() for part in pair.split("=", 1))
        # TASK 116 R8.1: the allow rule approves any argument, and ARCHIVE is written as a link.
        known = _SLOT_ARCHIVES.get(slot)
        if known is None:
            problem = "its slot is not docs/TASK.md or docs/PLAN.md"
        elif not known[1].fullmatch(archive):
            problem = f"its archive is not {known[0]}"
        else:
            slot_map[slot] = archive
            continue
        print(json.dumps({"ok": False, "error": f"--slot {pair!r}: {problem}"}), file=sys.stderr)
        return 2

    opened = []
    try:
        return _file_mode(args, slot_map, opened)
    finally:
        for _path, fd, _st in opened:
            os.close(fd)


def _file_mode(args, slot_map, opened):
    """The file mode of `_main`; each descriptor it opens is appended to `opened` (TASK 116 R7)."""
    import json

    for path in args.files:
        reason = _refuse_operand(path)
        if reason:
            print(json.dumps({"ok": False, "error": f"{path}: {reason}"}), file=sys.stderr)
            return 2

    # TASK 116 R7.1: every operand is open and checked before any of them is read.
    cwd = os.getcwd()
    for path in args.files:
        try:
            fd, st = _open_checked(path, cwd, os.O_RDONLY)
        except _Unsafe as exc:
            print(json.dumps({"ok": False, "error": f"{path}: {exc}"}), file=sys.stderr)
            return 2
        opened.append((path, fd, st))

    report, warned, failed, pending = [], False, False, []
    for path, fd, st in opened:
        try:
            text = _read_descriptor(fd).decode("utf-8")
            new_text, records = rebase_document_links(text, args.from_dir, args.to_dir,
                                                      args.repo_root, slot_map)
            changed = new_text != text
            # TASK 116 R8.7, in a dry run too: a rewrite adds no character that ends a link.
            added = [r.line for r in records if r.action in _WROTE
                     and _adds_characters(r.authored, r.new_target)]
            if added:
                print(json.dumps({"ok": False, "error": f"{path}:{added[0]}: a rewritten link "
                                  "holds text that its authored link does not"}),
                      file=sys.stderr)
                return 2
            parts = [r.line for r in records if r.action in _WROTE and _adds_parts(r)]
            if parts:
                print(json.dumps({"ok": False, "error": f"{path}:{parts[0]}: a rewritten link "
                                  "holds a path part that its authored link does not"}),
                      file=sys.stderr)
                return 2
            # Overlapping links are spliced one into the other: the text gains no character either.
            if _adds_characters(text, new_text):
                print(json.dumps({"ok": False, "error": f"{path}: the rewritten text holds a "
                                  "character that the text did not"}), file=sys.stderr)
                return 2
            if changed and not args.dry_run:
                _write_checked(path, cwd, st, new_text.encode("utf-8"))
        except (OSError, _Unsafe) as exc:
            print(json.dumps({"ok": False, "error": f"{path}: {exc}"}),
                  file=sys.stderr)
            return 2

        # Conservation law: every file denoted before the move is denoted after.
        #
        # SLOT_RESOLVED is exempt BY DEFAULT. A slot map is usually a FORWARD
        # reference -- the caller declares what the slot is becoming, and in the
        # documented archive order that file does not exist yet: Step 5.5 rebases
        # the TASK naming `docs/plans/plan-NNN-x.md`, which Step 7 only creates
        # afterwards. Probing it there made the protocol's own happy path exit 1
        # ("a link regressed") and, read literally, told the agent to stop.
        #
        # ARC-6: that exemption over-covered Step 7.6.5, where the TASK archive
        # is ALREADY on disk and a mistyped slug is fully detectable. Measured:
        # `--slot docs/TASK.md=docs/tasks/task-077-logn.md` against an archive
        # named task-077-login.md rewrote the citation and returned 0 with
        # `"ok": true`, so the protocol's closing assertion passed on a link the
        # tool knew was dangling. `--slot-must-exist` is how a caller states
        # that its slot targets are present tense rather than forward-looking.
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
                    if args.slot_must_exist:
                        failed = True

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
