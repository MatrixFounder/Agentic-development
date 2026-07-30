"""docs/backlog/ + BACKLOG.md lockstep writer (work-item ledger).

Registry B of the ``known-issues-format`` contract: a thin index over record
files, exactly like the defect ledger. Write discipline:

  * create-only — this module NEVER edits or deletes an existing record file or
    index line; closing a work-item (``status: done|dropped`` + ``resolved_by``)
    stays with humans;
  * frontmatter keys in contract order, optional extension keys AFTER
    ``source``; no ``auto_fixable`` — ``/heal-issues`` is defect-only;
  * insertion is anchored on a seeded HTML comment marker (default
    ``<!-- feedback:discovered-issues -->``) rather than a section heading:
    headings get renumbered/retitled, comments do not. New index lines are
    inserted directly AFTER the anchor (newest first) because the backlog is
    human-ranked and the engine must not impose a sort. A missing anchor is a
    hard exit-4 conflict — never a blind EOF append;
  * the anchor is resolved BEFORE anything is written, and both writes roll the
    record file back, so no half-state survives a *catchable* failure. A SIGKILL
    or power loss can still leave a record with no index line; the next run
    detects it via the id/lexists guards rather than pretending it cannot happen.

Layout is configurable (``backlog_layout``):

  * ``index+files`` (default) — the two-level contract described above;
  * ``flat`` — the legacy single-bullet append, for a repo that genuinely wants
    a one-file backlog. That path now REFUSES a body it would have to flatten
    instead of silently collapsing it into the index (one such inlined entry
    once reached 7 849 characters in a single bullet, which is what motivated
    the two-level contract).
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path

from . import atomic, body as body_mod, frontmatter, ids
from .envelope import EXIT_CONFIG, EXIT_FILING_CONFLICT, CliError

# --- vocab (known-issues-format, Registry B) --------------------------------

STATUS_WRITE = ("open", "done", "dropped")
EFFORT_WRITE = ("S", "M", "L")

#: frontmatter keys in contract order. The first REQUIRED_KEY_COUNT are mandatory;
#: the rest are optional and omitted when empty. This tuple is what builds the
#: mapping (see ``_build_meta``) rather than something a hand-written literal is
#: asserted against three lines later — that assertion compared the code to
#: itself, so it could not fail (iteration 2, V11). Pinned to the
#: `known-issues-format` SKILL.md authority by a test.
CONTRACT_KEYS = ("id", "type", "status", "opened_at", "slug", "effort", "value",
                 "source")
REQUIRED_KEY_COUNT = 5
#: optional keys written AFTER the contract keys, in this order
EXTENSION_KEYS = ("provenance", "component", "fingerprint", "evidence_paths",
                  "finding_ref")

#: a flat-layout body longer than this (whitespace-collapsed) is refused
FLAT_BODY_MAX_CHARS = 300

# seed comments are dropped when materializing a backlog, but ``feedback:``
# markers (the insertion anchor) MUST survive
_SEED_COMMENT_RE = re.compile(r"<!--(?!\s*feedback:).*?-->\n?", re.DOTALL)


def _one_line(text):
    """Collapse a metadata scalar to a single line (quoting is frontmatter's job)."""
    return " ".join(str(text or "").split())


def _escape_link_text(title):
    """Escape markdown link-text metacharacters in an index-line title.

    An unescaped ``]`` closes the link early, so ``Fix [x](evil.md)`` renders as
    a link to ``evil.md`` from inside our own pointer line (vdd-multi S-02).
    Backslash escapes are standard markdown, so the rendered title is unchanged.
    """
    return re.sub(r"([\\\[\]])", r"\\\1", _one_line(title))


def format_index_line(item_id, title, link, status, opened_at, effort=None):
    """The canonical Registry B index line (pure, single-line by construction).

    Newlines are impossible here: the title is collapsed and escaped. A raw
    newline would have spliced a SECOND, forged pointer line into a
    hand-maintained index that has no generator to reconcile drift.
    """
    effort_clause = "effort `%s`, " % effort if effort else ""
    line = ("- **%s** [%s](%s) — %sstatus `%s`, opened %s"
            % (_one_line(item_id), _escape_link_text(title), _one_line(link),
               effort_clause, _one_line(status), _one_line(opened_at)))
    if "\n" in line or "\r" in line:  # belt and braces: never emit 2 lines
        raise CliError("index line would span multiple lines: %r" % line,
                       code=EXIT_FILING_CONFLICT, err_type="ContractError")
    return line


def record_link(index_path, record_path):
    """Index-relative posix link from the index file to a record file."""
    rel = os.path.relpath(str(Path(record_path)), str(Path(index_path).parent))
    return rel.replace(os.sep, "/")


# --- backlog seeding --------------------------------------------------------

def _seed_template_path():
    skills_dir = Path(__file__).resolve().parents[3]
    return (skills_dir / "known-issues-format" / "assets" / "templates"
            / "backlog_md_template.md")


def seed_backlog_text():
    """Materialize a fresh backlog index from the known-issues-format seed
    template: keep the preamble and the insertion anchor, drop the seed
    comments and the ``_No work-items recorded yet._`` placeholder."""
    template = _seed_template_path()
    if not template.is_file():
        raise CliError(
            "known-issues-format seed template not found at %s" % template,
            code=EXIT_CONFIG, err_type="ConfigError",
            remediation="install/symlink the known-issues-format skill next "
                        "to run-feedback")
    text = template.read_text(encoding="utf-8")
    text = _SEED_COMMENT_RE.sub("", text)
    text = text.replace("_No work-items recorded yet._\n", "")
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


# --- anchored insertion -----------------------------------------------------

#: A fence OPENER per CommonMark §4.5: at most 3 leading spaces, then 3+ of one
#: fence character, then an info string. A line indented 4+ spaces is an indented
#: code block, not a fence.
_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*(.*)$")

#: a placeholder line the seed/live index carries while it has no entries;
#: leaving it above a freshly inserted item reads as "no open work-items" over
#: a list of open work-items
_PLACEHOLDER_RE = re.compile(r"^_No\s.*work-items.*_$", re.IGNORECASE)


def scan_anchors(text, anchor):
    """(anchor line indices outside fences, 1-based line of an unclosed fence).

    Both the shipped template and every live ledger *document* the anchor in prose
    and in fences, so a naive "first line that equals it" resolution can splice
    the index line inside a code block — rendered invisible, outside the real
    list, exit 0 (vdd-multi F3). So fenced regions are skipped and the caller
    demands exactly one match.

    The first version toggled a boolean on any line starting with ``` or ``~~~``,
    which four shapes defeated (iteration 2, V8): a 3-backtick line **inside** a
    4-backtick fence closed it early, ``~~~`` closed a ``` fence, a 4-space
    indented line counted as a fence, and an info string was ignored. Now the
    opening fence's character and length are tracked and only a same-character run
    of at least that length closes it — CommonMark §4.5.

    An unclosed fence is reported rather than papered over. Note what is NOT done:
    the anchor inside an unclosed fence still resolves to *nothing*, so filing
    still exits 4. That is correct — per CommonMark an unclosed fence runs to end
    of file, so the anchor genuinely is inside a code block, and inserting there is
    the F3 defect. What V8 called a fail-closed DoS is fixed by making the
    *message* name the offending fence, not by granting permission to write.
    """
    out = []
    fence_char = None
    fence_len = 0
    fence_line = None
    for i, line in enumerate(text.split("\n")):
        match = _FENCE_OPEN_RE.match(line)
        if fence_char is None:
            if match:
                run, info = match.group(1), match.group(2)
                # an info string may not contain a backtick on a ``` fence
                if not (run[0] == "`" and "`" in info):
                    fence_char, fence_len, fence_line = run[0], len(run), i + 1
                    continue
        else:
            # only a run of the SAME character, at least as long, closes it —
            # and a closing fence carries no info string
            if match:
                run, info = match.group(1), match.group(2)
                if (run[0] == fence_char and len(run) >= fence_len
                        and not info.strip()):
                    fence_char, fence_len, fence_line = None, 0, None
                    continue
            continue  # any other line inside the fence is content
        if line.strip() == anchor:
            out.append(i)
    return out, fence_line


def anchor_positions(text, anchor):
    """Indices of every standalone anchor line outside a fenced code block."""
    return scan_anchors(text, anchor)[0]


def has_anchor(text, anchor):
    """Exactly-one-anchor predicate. `doctor` and `file` MUST share this — a
    substring test reported `anchor present` for a ledger whose only mention was
    documentation prose, i.e. the readiness gate lied precisely where it
    mattered (vdd-multi F4)."""
    return len(anchor_positions(text, anchor)) == 1


def insert_after_anchor(text, anchor, line, where=None):
    """Pure function: return *text* with *line* inserted right after *anchor*.

    Raises exit-4 when the anchor is absent OR ambiguous — the caller must
    therefore call this BEFORE writing anything else. ``split("\\n")`` rather
    than ``splitlines()``: the latter also splits on ``\\x0b``, ``\\x1c-\\x1e``,
    ``U+2028``/``U+2029`` and rewrites CRLF, silently mutating ledger text this
    function promises only to insert into (vdd-multi F13).
    """
    positions, unclosed = scan_anchors(text, anchor)
    if len(positions) != 1:
        remediation = ("the index needs exactly ONE standalone anchor line "
                       "outside any code fence — seed it inside the "
                       "Discovered Issues section (one-time human commit)")
        if not positions and unclosed is not None:
            # without this the operator sees "anchor not found" for an anchor
            # that is plainly there, and has no way to know a fence swallowed it
            remediation = (
                "a code fence opened on line %d is never closed, so everything "
                "below it — including the anchor — is inside a code block. "
                "Close that fence; then the anchor resolves." % unclosed)
        raise CliError(
            "backlog anchor %r %s in %s"
            % (anchor, "not found" if not positions
               else "found %d times" % len(positions), where or "backlog"),
            code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
            remediation=remediation)
    lines = text.split("\n")
    # match the file's own line ending: splicing a bare-LF line into a CRLF
    # ledger would leave one odd line out (the read keeps "\r" as the last char)
    if lines[positions[0]].endswith("\r"):
        line = line + "\r"
    lines.insert(positions[0] + 1, line)
    _strip_placeholder(lines, positions[0] + 2)
    return "\n".join(lines)


def _strip_placeholder(lines, start):
    """Delete a "no work-items yet" placeholder below the freshly inserted line.

    Walks forward to the first NON-BLANK line instead of probing offsets 2 and 3.
    The offset probe missed a two-blank-line shape, and — worse — could reach past
    a section boundary and delete a *different* section's placeholder, leaving the
    empty section looking populated (iteration 2, V7). A ``## `` heading or a
    non-blank non-placeholder line stops the walk.
    """
    for idx in range(start, len(lines)):
        stripped = lines[idx].strip()
        if not stripped:
            continue
        if _PLACEHOLDER_RE.match(stripped):
            del lines[idx]
        return


def _read_verbatim(path):
    """Newline-faithful ledger read — see ``atomic.read_verbatim``.

    Kept as a thin alias: this module owned the primitive while the defect ledger
    went without it (V12), so the implementation moved next to ``write_atomic``
    and both ledgers now read through the same function.
    """
    return atomic.read_verbatim(path)


def _write_atomic(path, text):
    """Delegates to the shared primitive (see feedback_lib/atomic.py)."""
    atomic.write_atomic(path, text)


# --- frontmatter assembly ---------------------------------------------------

def _build_meta(item_id, slug, status, opened_at, effort, value, source,
                extensions):
    """Assemble the record frontmatter IN CONTRACT ORDER, driven by the tuple.

    Indexing ``sources[key]`` is deliberate: add a key to ``CONTRACT_KEYS``
    without giving it a value here and this raises ``KeyError`` at once, instead
    of silently emitting a record that is missing a contract key. That is the
    property the old ``list(meta)[:5] != list(CONTRACT_KEYS[:5])`` assertion was
    reaching for and could never have — it compared a dict literal to a tuple
    that restated it (V11).
    """
    sources = {"id": item_id, "type": "work-item", "status": status,
               "opened_at": opened_at, "slug": slug, "effort": effort,
               "value": _one_line(value), "source": _one_line(source)}
    meta = {}
    for position, key in enumerate(CONTRACT_KEYS):
        item = sources[key]
        if isinstance(item, str):
            item = _one_line(item)
        if item in (None, "", []):
            if position < REQUIRED_KEY_COUNT:
                raise CliError(
                    "contract key %r is empty — a work-item record cannot be "
                    "written without it" % key,
                    code=EXIT_FILING_CONFLICT, err_type="ContractError")
            continue
        meta[key] = item
    provenance = (extensions or {}).get("provenance")
    if not provenance and (extensions or {}).get("finding_ref"):
        # anything reaching this function came through the engine, not a human
        # editor, and `finding_ref` is what proves it came from a capture (WI-3)
        provenance = body_mod.PROVENANCE_MACHINE
    for key in EXTENSION_KEYS:
        item = provenance if key == "provenance" else (extensions or {}).get(key)
        if isinstance(item, str):
            item = _one_line(item)
        if item not in (None, "", []):
            meta[key] = item
    return meta


# --- the lockstep work-item write -------------------------------------------

def file_work_item(config, item_id, slug, title, body, status="open",
                   opened_at=None, effort=None, value=None, source=None,
                   extensions=None, dry_run=False):
    """Create ``<backlog_dir>/<slug>.md`` + its index line, atomically-ish.

    Returns a dict describing what was (or would be) written. Caller holds the
    filing flock.
    """
    if status not in STATUS_WRITE:
        raise CliError("status %r outside the write vocabulary %s"
                       % (status, list(STATUS_WRITE)),
                       code=EXIT_FILING_CONFLICT, err_type="ContractError")
    if effort and effort not in EFFORT_WRITE:
        raise CliError("effort %r outside the write vocabulary %s"
                       % (effort, list(EFFORT_WRITE)),
                       code=EXIT_FILING_CONFLICT, err_type="ContractError")
    opened_at = opened_at or time.strftime("%Y-%m-%d")

    index_path = Path(config.backlog_path)
    records_dir = Path(config.backlog_dir)
    record_path = records_dir / (slug + ".md")
    # `exists()` FOLLOWS symlinks, so a dangling one reported False and the
    # create-only check passed while write_text wrote through it, outside the
    # record dir (verified exploit S-03). lexists + O_EXCL|O_NOFOLLOW below is
    # the real guard; this check stays for the friendly error message.
    if os.path.lexists(str(record_path)):
        raise CliError("work-item file already exists: %s" % record_path,
                       code=EXIT_FILING_CONFLICT, err_type="FilingConflict")
    # ids are the human-facing registry key: re-scan under the caller's lock so
    # a second feedback_dir or an archived subdir cannot silently reuse one
    # (F10). Compared CASE-INSENSITIVELY and RECURSIVELY: `--prefix wi` made
    # `next_number`'s `^wi-(\d+)` blind to `WI-1`, and the first version of this
    # guard used exact string membership, so it allocated `wi-1` beside `WI-1`
    # — F10's own headline scenario (vdd-multi iteration 2, V2).
    known = {str(existing).casefold()
             for existing in ids.existing_ids(records_dir, recursive=True)}
    if item_id.casefold() in known:
        raise CliError("work-item id already in use: %s" % item_id,
                       code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
                       remediation="another record already holds that id — "
                                   "re-run without --prefix/--slug overrides "
                                   "so the next id is allocated")

    if index_path.is_file():
        index_before = _read_verbatim(index_path)
        seeded = False
    else:
        index_before = seed_backlog_text()
        seeded = True

    index_line = format_index_line(
        item_id, title, record_link(index_path, record_path), status,
        opened_at, effort)
    # anchor first: an anchorless backlog must fail with ZERO writes
    index_after = insert_after_anchor(index_before, config.backlog_anchor,
                                     index_line, where=index_path)

    meta = _build_meta(item_id, slug, status, opened_at, effort, value, source,
                       extensions)
    banner = ""
    if meta.get("finding_ref"):
        banner = body_mod.provenance_banner(meta["finding_ref"]) + "\n\n"
    record_text = (frontmatter.serialize(meta) + "\n# %s — %s\n\n%s%s\n"
                   % (item_id, title, banner, body.strip()))

    result = {"item_id": item_id, "slug": slug,
              "record_path": str(record_path), "backlog_path": str(index_path),
              "index_line": index_line, "seeded_backlog": seeded,
              "layout": "index+files", "dry_run": dry_run}
    if dry_run:
        result["record_text"] = record_text
        # the id is read from disk state that a real filing may change first
        result["provisional_id"] = True
        return result

    if records_dir.is_symlink():
        raise CliError("record dir is a symlink, refusing to write through it: "
                       "%s" % records_dir,
                       code=EXIT_FILING_CONFLICT, err_type="FilingConflict")
    records_dir.mkdir(parents=True, exist_ok=True)
    # the record write is INSIDE the guard: a mid-write failure (ENOSPC, EIO)
    # must not leave a truncated orphan record with no index line (F2)
    try:
        # O_EXCL|O_NOFOLLOW: create-only enforced by the kernel, and a symlink
        # at this path is refused rather than followed (S-03)
        fd = os.open(str(record_path),
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(record_text)
    except FileExistsError:
        # DIFFERENT message from the lexists pre-check on purpose: reaching here
        # means the path appeared between the check and the open — a concurrent
        # filing, or a symlink planted in that window. `O_EXCL` is the guard that
        # actually refuses; without a distinct message no test could tell which of
        # the two fired, so neither was pinned (V-22).
        raise CliError(
            "work-item file appeared while filing (create-only refused it): %s"
            % record_path,
            code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
            remediation="another process filed this slug, or a symlink was "
                        "planted at that path — re-run to get a fresh id")
    except BaseException as exc:
        # ANY failure, not just OSError: a KeyboardInterrupt or MemoryError
        # mid-write left a truncated orphan record with no index line, while the
        # docstring claimed no half-state could exist (iteration 2, V1)
        _rollback(record_path)
        if not isinstance(exc, OSError):
            raise
        raise CliError("could not write the work-item record %s (%s)"
                       % (record_path, exc),
                       code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
                       remediation="check that %s is a writable directory and "
                                   "not a symlink" % records_dir)
    try:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        _write_atomic(index_path, index_after)
    except BaseException:
        _rollback(record_path)
        raise
    return result


def _rollback(record_path):
    """Remove a just-written record so a half-state never survives.

    Uses ``os.unlink`` on the path itself (never a symlink target) and reports
    nothing: this runs while another exception is propagating.
    """
    try:
        os.unlink(str(record_path))
    except OSError:
        pass


# --- legacy flat layout -----------------------------------------------------

def format_bullet(title, body, date, effort=None, value=None):
    """The legacy flat bullet — same single-line discipline as the pointer line.

    Every interpolated field is collapsed and the result asserted to be one
    line. Previously only `body` was collapsed, so `--value $'S\\n- **WI-99**
    [Already fixed](…) — status `done`'` spliced a SECOND, forged bullet into
    the ledger: the S-02 exploit surviving on the sibling code path
    (vdd-multi iteration 2, V-05).
    """
    tail = ""
    if effort or value:
        parts = []
        if effort:
            parts.append("Effort: %s" % _one_line(effort))
        if value:
            parts.append("Value: %s" % _one_line(value))
        tail = " · " + " · ".join(parts)
    bullet = "- **%s (%s)** — %s%s" % (_escape_link_text(title),
                                       _one_line(date),
                                       _one_line(body), tail)
    if "\n" in bullet or "\r" in bullet:
        raise CliError("backlog bullet would span multiple lines: %r" % bullet,
                       code=EXIT_FILING_CONFLICT, err_type="ContractError")
    return bullet


def guard_flat_body(body, max_chars=FLAT_BODY_MAX_CHARS):
    """Refuse a body the flat layout would silently flatten into the index.

    The flat layout inlines the whole body in one bullet, so anything with
    structure (a table, a fence, a second paragraph) becomes an unreadable,
    undiffable index line. Refusing is honest; flattening is not.
    """
    text = str(body or "")
    kept = [line for line in text.splitlines() if line.strip()]
    collapsed = " ".join(text.split())
    if len(kept) > 1 or len(collapsed) > max_chars:
        raise CliError(
            "work-item body does not fit the flat backlog layout "
            "(%d non-empty lines, %d chars after collapsing): the flat layout "
            "inlines the body INTO the index line"
            % (len(kept), len(collapsed)),
            code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
            remediation='use the default "backlog_layout": "index+files" so '
                        "the body lands in <backlog_dir>/<slug>.md and the "
                        "index keeps a one-line pointer, or shorten the body "
                        "to a single line")
    return text


def append_work_item(backlog_path, anchor, bullet, dry_run=False):
    """Flat layout: insert one bullet directly after the anchor."""
    backlog_path = Path(backlog_path)
    if not backlog_path.is_file():
        raise CliError("backlog file not found: %s" % backlog_path,
                       code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
                       remediation="set backlog_path in docs/feedback/config.json")
    text = _read_verbatim(backlog_path)
    new_text = insert_after_anchor(text, anchor, bullet, where=backlog_path)
    if dry_run:
        return {"backlog_path": str(backlog_path), "bullet": bullet,
                "layout": "flat", "dry_run": True}
    _write_atomic(backlog_path, new_text)
    return {"backlog_path": str(backlog_path), "bullet": bullet,
            "layout": "flat", "dry_run": False}
