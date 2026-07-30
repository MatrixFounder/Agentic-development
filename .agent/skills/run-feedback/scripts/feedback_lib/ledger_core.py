"""ONE lockstep write path, shared by both thin-index registries.

`ledger_issues` (defects) and `ledger_backlog` (work-items) implement one contract
— `known-issues-format`: a thin index of one-line pointers over one record file per
entry. They used to implement it *twice*, in ~110 near-parallel lines each, and
that duplication produced a confirmed defect in **every** adversarial iteration
over this code:

  * **WI-23** — the work-item path wrote only an index line; the defect path wrote
    record + pointer in lockstep with rollback.
  * **iteration 2, V12** — the CRLF/reader-break fix landed only in the backlog
    module, leaving the defect index with the corruption the other no longer had.
  * **iteration 3** — six more: CRLF re-broken in one insertion branch (L-1), NO
    fence awareness in the defect index (L-2), `OSError`-only rollback (L-4), the
    body guard in neither writer (L-5), no id-uniqueness guard at all (L-6), and
    path containment on one of two `resolve` branches (H-04).

Three iterations is enough evidence to stop treating each instance as its own bug.
The mechanisms were shared first (`markdown.scan`, `ids.assert_id_free`,
`atomic.read_verbatim`, `body.guard_config_body`); this module shares the
**choreography**, which is what removes the class: a guard added here is a guard
both registries have, by construction rather than by review.

What is deliberately NOT shared: the two index *layouts*. A work-item pointer goes
directly after a comment anchor (newest first, human-ranked); a defect pointer goes
into its `## <category>` section in id order. Those are genuinely different
documented behaviours, so each registry keeps its own inserter and passes it in.

**The compatibility contract of this refactor:** `file_defect` and
`file_work_item` keep their exact signatures and their exact result-dict keys
(`issue_id`/`item_id`, `issue_path`/`record_path`, `index_path`/`backlog_path`,
`seeded_index`/`seeded_backlog`, `layout`). Those four synonym pairs are
gratuitous, and normalizing them is a separate change with its own callers to
update — doing it here would have destroyed the property that made the extraction
reviewable, namely that the whole pre-existing test suite passes **unmodified**.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from . import atomic, body as body_mod, frontmatter, ids
from .envelope import EXIT_FILING_CONFLICT, CliError


class Registry:
    """Everything that differs between the two registries.

    Anything not here is choreography and lives in ``file_record``.
    """

    def __init__(self, noun, records_dir, index_path, status_vocab,
                 seed_text, insert, format_line, build_meta, write_index=None,
                 link_for=None, rank_name=None, rank_vocab=None):
        self.noun = noun                  # "work-item" / "issue" — error wording
        self.records_dir = Path(records_dir)
        self.index_path = Path(index_path)
        self.status_vocab = status_vocab
        self.seed_text = seed_text        # () -> str
        self.insert = insert              # (index_text, line, where) -> str
        self.format_line = format_line    # (record_id, title, status, ...) -> str
        self.build_meta = build_meta      # (...) -> dict
        # How this registry's index is written. A real seam, not vestigial: each
        # registry declares it, which is also what lets the pre-existing rollback
        # tests patch their own module and keep verifying the shared choreography.
        self.write_index = write_index or atomic.write_atomic
        self.link_for = link_for          # optional: (index_path, record) -> str
        self.rank_name = rank_name        # "effort" / "severity"
        self.rank_vocab = rank_vocab


def check_vocab(reg, status, rank=None):
    """Status and rank vocabulary, identically for both registries."""
    if status not in reg.status_vocab:
        raise CliError("status %r outside the write vocabulary %s"
                       % (status, list(reg.status_vocab)),
                       code=EXIT_FILING_CONFLICT, err_type="ContractError")
    if rank and reg.rank_vocab and rank not in reg.rank_vocab:
        raise CliError("%s %r outside the write vocabulary %s"
                       % (reg.rank_name, rank, list(reg.rank_vocab)),
                       code=EXIT_FILING_CONFLICT, err_type="ContractError")


def read_index(reg):
    """(index_text, seeded). Seeds a missing OR BLANK index from the template.

    Seeding used to be gated on ``is_file()`` alone, so a **0-byte** index — a
    `touch`, a failed editor save, a half-applied patch — was a file and got no
    template. Filing then produced a ledger with no H1, no purpose block, no rules
    section and no prefix table, exit 0: the hand-maintained preamble the whole
    contract depends on, silently gone (iteration 3, L-16).
    """
    if reg.index_path.is_file():
        text = atomic.read_verbatim(reg.index_path)
        if text.strip():
            return text, False
    return reg.seed_text(), True


def _assert_records_dir_intact(reg):
    """Re-verify the record dir right before the create (TOCTOU).

    ``O_NOFOLLOW`` protects the FINAL component only, and ``is_symlink()`` only the
    leaf directory — so an *intermediate* component swapped to a symlink after
    `_contained` resolved still escaped, and ``mkdir(parents=True)`` would happily
    walk through it (iteration 3, sec-L-07). `config` hands us an already-resolved
    path, so if the realpath has changed since, something moved underneath us.
    """
    if reg.records_dir.is_symlink():
        raise CliError(
            "%s dir is a symlink, refusing to write through it: %s"
            % (reg.noun, reg.records_dir),
            code=EXIT_FILING_CONFLICT, err_type="FilingConflict")
    real = Path(os.path.realpath(str(reg.records_dir)))
    if real != reg.records_dir:
        raise CliError(
            "%s dir %s now resolves to %s — a path component changed underneath "
            "the containment check" % (reg.noun, reg.records_dir, real),
            code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
            remediation="a directory on that path is a symlink or was replaced "
                        "since the config was validated; nothing was written")


def _rollback(record_path):
    """Remove a just-written record so a half-state never survives.

    ``os.unlink`` on the path itself (never a symlink target), and reports nothing:
    this runs while another exception is propagating.
    """
    try:
        os.unlink(str(record_path))
    except OSError:
        pass


def file_record(reg, config, record_id, slug, title, body, status,
                rank=None, opened_at=None, extensions=None, dry_run=False,
                meta_kwargs=None, line_kwargs=None):
    """The whole lockstep write, once, for either registry.

    Order (identical for both, which it was not before — the backlog resolved its
    anchor before guarding the body while the defect path did the reverse, so the
    two reported different errors for the same doubly-invalid input):

      vocab → lexists pre-check → id uniqueness → body policy → frontmatter →
      record text → index line → index insertion → [dry-run returns here] →
      records-dir integrity → create-only write → index write

    Nothing is written until every check above has passed, so an anchorless index
    or a bad body still fails with **zero** writes. Both writes roll the record
    file back, so no half-state survives a catchable failure; a SIGKILL can still
    leave a record with no index line, and the next run detects it via the
    id/lexists guards rather than pretending it cannot happen.
    """
    check_vocab(reg, status, rank)
    opened_at = opened_at or time.strftime("%Y-%m-%d")
    record_path = reg.records_dir / (slug + ".md")

    # `exists()` FOLLOWS symlinks, so a DANGLING one reported False and create-only
    # never fired while the write followed it out of the record dir (verified
    # exploit S-03). `O_EXCL|O_NOFOLLOW` below is the enforcing guard; this check
    # exists for the friendly error, and its message is deliberately DIFFERENT from
    # the kernel one so a test can tell which of the two fired (V-22).
    if os.path.lexists(str(record_path)):
        raise CliError("%s file already exists: %s" % (reg.noun, record_path),
                       code=EXIT_FILING_CONFLICT, err_type="FilingConflict")
    # the id is the human-facing registry key, not the filename: re-scan under the
    # caller's lock, casefolded and recursively (F10 / V2 / L-6)
    ids.assert_id_free(reg.records_dir, record_id)

    body = body_mod.guard_config_body(config, body)
    meta = reg.build_meta(**(meta_kwargs or {}))
    banner = ""
    if meta.get("finding_ref"):
        banner = body_mod.provenance_banner(meta["finding_ref"]) + "\n\n"
    record_text = (frontmatter.serialize(meta) + "\n# %s — %s\n\n%s%s\n"
                   % (record_id, title, banner, body.strip()))

    index_line = reg.format_line(**(line_kwargs or {}))
    index_before, seeded = read_index(reg)
    # the index resolution happens BEFORE any write, so an anchorless or ambiguous
    # index exits 4 having written nothing
    index_after = reg.insert(index_before, index_line, reg.index_path)

    result = {"record_id": record_id, "slug": slug,
              "record_path": str(record_path),
              "index_path": str(reg.index_path),
              "index_line": index_line, "seeded_index": seeded,
              "dry_run": dry_run}
    if dry_run:
        result["record_text"] = record_text
        # the id came from a disk scan that a real filing may win the race on
        result["provisional_id"] = True
        return result

    _assert_records_dir_intact(reg)
    reg.records_dir.mkdir(parents=True, exist_ok=True)
    try:
        # O_EXCL|O_NOFOLLOW: create-only enforced by the kernel, and a symlink at
        # this path is refused rather than followed (S-03)
        fd = os.open(str(record_path),
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(record_text)
    except FileExistsError:
        raise CliError(
            "%s file appeared while filing (create-only refused it): %s"
            % (reg.noun, record_path),
            code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
            remediation="another process filed this slug, or a symlink was "
                        "planted at that path — re-run to get a fresh id")
    except BaseException as exc:
        # ANY failure, not just OSError: a KeyboardInterrupt or MemoryError
        # mid-write left a truncated orphan record with no index line while the
        # docstring claimed no half-state could exist (iteration 2 V1 on one
        # writer; iteration 3 L-4 on the other — now impossible to have on one)
        _rollback(record_path)
        if not isinstance(exc, OSError):
            raise
        raise CliError("could not write the %s record %s (%s)"
                       % (reg.noun, record_path, exc),
                       code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
                       remediation="check that %s is a writable directory and "
                                   "not a symlink" % reg.records_dir)
    try:
        reg.index_path.parent.mkdir(parents=True, exist_ok=True)
        reg.write_index(reg.index_path, index_after)
    except BaseException:
        _rollback(record_path)
        raise
    return result
