#!/usr/bin/env python3
"""run-feedback — collect run errors, triage them, file them into ledgers.

Stdlib-only CLI (no venv). Subcommands:

  collect   queue a finding into the inbox (idempotent, dedup by fingerprint)
  triage    list inbox findings with duplicate candidates (classification is
            the LLM's job — this only prepares the table)
  file      deterministically file a triaged finding (defect / work-item /
            noise); --dry-run previews without writing
  journal   append a free event to the run-feedback journal
  issues    machine-readable feed of the docs/issues/ ledger
  mine      extract failure signals from Claude Code session transcripts
  claim     claim retro ownership for this run (release with `release`)
  init      bootstrap docs/feedback/ configs from templates (create-only)
  doctor    readiness report

Exit codes: 0 ok · 1 unexpected · 2 usage · 3 config/env · 4 filing
conflict · 5 not found · 6 claim denied.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import time
import fcntl
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from feedback_lib import (atomic, body as body_mod, claims, filters, finding,
                          frontmatter, ids as ids_mod, inbox, journal,
                          ledger_backlog, ledger_issues, mine as mine_mod)
from feedback_lib.config import load_config
from feedback_lib.envelope import (EXIT_CONFIG, EXIT_FILING_CONFLICT, EXIT_OK,
                                   EXIT_UNEXPECTED, EXIT_USAGE, CliError,
                                   emit_json_error, install_json_errors,
                                   wants_json_errors)

EXIT_CLAIM_DENIED = 6


def _parse_kv(pairs):
    out = {}
    for pair in pairs or ():
        key, sep, value = pair.partition("=")
        if not sep:
            raise CliError("--context/--detail expects key=value, got %r" % pair,
                           code=EXIT_USAGE, err_type="UsageError")
        out[key.strip()] = value.strip()
    return out


def _read_maybe_stdin(spec):
    if spec == "-":
        return sys.stdin.read()
    if spec.startswith("@"):
        path = Path(spec[1:])
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise CliError("cannot read %s: %s" % (path, exc),
                           code=EXIT_USAGE, err_type="UsageError")
        except UnicodeDecodeError as exc:
            # UnicodeDecodeError is a ValueError, so it escaped the OSError arm and
            # reached the last-resort handler, which re-raises in human mode: a raw
            # traceback for the very ordinary case of a log file with one latin-1
            # byte (iteration 3, L-11). NOT errors="replace" — mangling a body that
            # the ledger contract preserves verbatim is worse than refusing it.
            raise CliError(
                "%s is not valid UTF-8 (byte %d: %s)"
                % (path, exc.start, exc.reason),
                code=EXIT_USAGE, err_type="UsageError",
                remediation="re-encode the file as UTF-8, or extract the "
                            "relevant lines by hand — a record body is embedded "
                            "verbatim, so it is refused rather than mangled")
    return spec


def _parse_envelope(spec):
    raw = _read_maybe_stdin(spec).strip()
    try:
        obj = json.loads(raw)
    except ValueError as exc:
        raise CliError("--error-envelope is not valid JSON: %s" % exc,
                       code=EXIT_USAGE, err_type="UsageError")
    if not isinstance(obj, dict) or "error" not in obj:
        raise CliError("--error-envelope must be a JSON object with an "
                       "'error' key", code=EXIT_USAGE, err_type="UsageError")
    return obj


def _emit(args, payload, human):
    if getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(human)


# --- collect -----------------------------------------------------------------

def cmd_collect(args, cfg):
    envelope_obj = _parse_envelope(args.error_envelope) \
        if args.error_envelope else None
    run_ctx = {k: v for k, v in {
        "session_id": args.session_id, "task_id": args.task_id,
        "workflow": args.workflow, "phase": args.phase, "step": args.step,
        "cwd": os.getcwd(),
    }.items() if v}
    extra = _parse_kv(args.context)
    if extra:
        run_ctx["extra"] = extra

    evidence = {"paths": list(args.evidence_path or []), "excerpts": []}
    if args.excerpt_file:
        try:
            text = Path(args.excerpt_file).read_text(encoding="utf-8",
                                                     errors="replace")
        except OSError as exc:
            raise CliError("cannot read --excerpt-file: %s" % exc,
                           code=EXIT_USAGE, err_type="UsageError")
        evidence["excerpts"].append({
            "path": args.excerpt_file,
            "text": filters.clip(text, cfg.excerpt_max_chars)})

    proposed = {k: v for k, v in {
        "classification": args.propose, "severity": args.severity,
        "category": args.category}.items() if v}

    record = finding.new_finding(
        args.source, args.kind, args.component,
        filters.redact(args.message), command=args.command,
        exit_code=args.exit_code, error_envelope=envelope_obj,
        run=run_ctx, evidence=evidence, proposed=proposed)
    record, deduped = inbox.collect(cfg, record)
    journal.append_event(
        cfg.journal_dir,
        "finding_deduped" if deduped else "finding_collected",
        "%s %s" % (args.component, record["fingerprint"]),
        {"kind": args.kind, "sources": ",".join(record["sources"]),
         "occurrences": record["occurrences"]})
    _emit(args, {"deduped": deduped, "finding": record},
          "%s %s (%s, seen ×%d)" % (
              "deduped into" if deduped else "collected",
              record["finding_id"], record["fingerprint"],
              record["occurrences"]))
    return EXIT_OK


# --- triage ------------------------------------------------------------------

def _index_titles(cfg):
    """[(issue_id, title, token_set)] from the index — tokens PRE-COMPUTED.

    The token set is loop-invariant across inbox entries, and `_dup_candidates`
    rebuilt it for every (entry, title) pair: at 200 entries × 500 titles that is
    100 000 `lower()`+`split()`+set constructions instead of 500 (iteration 3, perf
    Med-low). Read once, capped like every other hand-maintained-markdown read.
    """
    titles = []
    index_path = Path(cfg.index_path)
    if not index_path.is_file():
        return titles
    if index_path.stat().st_size > _DOCTOR_READ_CAP:
        return titles  # a megabyte-scale index is not worth slurping for hints
    entry_re = ledger_issues._INDEX_ENTRY_RE
    for line in index_path.read_text(encoding="utf-8").splitlines():
        match = entry_re.match(line)
        if match:
            title = line[match.end():].split("](", 1)[0].lstrip("[")
            tokens = {tok for tok in title.lower().split() if len(tok) >= 4}
            titles.append((match.group(1), title, tokens))
    return titles


def _dup_candidates(record, issue_fps, titles):
    dups = []
    fprint = record.get("fingerprint")
    if fprint in issue_fps:
        dups.append("issue %s (fingerprint)" % issue_fps[fprint])
    # `.get`, not a subscript: `inbox.scan` is deliberately tolerant of any
    # parseable JSON ("never let one bad file kill capture"), and every other read
    # in triage honors that — this one subscript meant a single foreign or
    # older-schema inbox file turned `triage` into a KeyError traceback until a
    # human found and removed it (iteration 3, L-12)
    message_tokens = {t for t in
                      ((record.get("subject") or {}).get("message")
                       or "").lower().split()
                      if len(t) >= 4}
    for issue_id, title, title_tokens in titles:
        overlap = message_tokens & title_tokens
        if len(overlap) >= 2:
            dups.append("issue %s (title overlap: %s)"
                        % (issue_id, ", ".join(sorted(overlap)[:3])))
    return dups


def cmd_triage(args, cfg):
    entries = inbox.scan(cfg.inbox_dir)
    issue_fps = {rec["fingerprint"]: rec["id"]
                 for rec in ledger_issues.list_issues(cfg)
                 if rec.get("fingerprint")}
    titles = _index_titles(cfg)
    rows = []
    for path, record in entries:
        subject = record.get("subject", {})
        rows.append({
            "finding_id": record.get("finding_id"),
            "sources": record.get("sources", []),
            "kind": record.get("kind"),
            "component": subject.get("component"),
            "failure": (subject.get("error_envelope") or {}).get("type")
                       or ("exit:%s" % subject.get("exit_code")
                           if subject.get("exit_code") is not None else "-"),
            "message": subject.get("message"),
            "occurrences": record.get("occurrences", 1),
            "proposed": record.get("proposed", {}),
            "evidence_paths": record.get("evidence", {}).get("paths", []),
            "dup_candidates": _dup_candidates(record, issue_fps, titles),
        })
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return EXIT_OK
    if not rows:
        print("inbox is empty — nothing to triage")
        return EXIT_OK
    print("| finding | src | kind | component | failure | ×N | message | dup candidates |")
    print("|---|---|---|---|---|---|---|---|")
    for row in rows:
        print("| %s | %s | %s | %s | %s | %d | %s | %s |" % (
            row["finding_id"], "+".join(row["sources"]), row["kind"],
            row["component"], row["failure"], row["occurrences"],
            (row["message"] or "")[:80].replace("|", "\\|"),
            "; ".join(row["dup_candidates"]) or "-"))
    for row in rows:
        if row["evidence_paths"]:
            print("- %s evidence: %s"
                  % (row["finding_id"], ", ".join(row["evidence_paths"])))
    return EXIT_OK


# --- file --------------------------------------------------------------------

def _run_source(record):
    """Human ``source:`` for a work-item, derived from the capture's run context
    (``workflow task-id phase``). None when the capture carried no context."""
    run = record.get("run") or {}
    parts = [str(run.get(key)) for key in ("workflow", "task_id", "phase")
             if run.get(key)]
    return " ".join(parts) or None


#: a title is one line of prose that lands in an H1 and a markdown link
_TITLE_MAX = 120
#: `--prefix` reaches `id:` in the record and the ledger's index line, so it is
#: an identifier, not free text (vdd-multi iteration 2, V-15: it was the third
#: delivery vector for the frontmatter-injection sink)
_PREFIX_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$")
#: doctor never reads more than this from a configured ledger path (S-12)
_DOCTOR_READ_CAP = 2 * 1024 * 1024
_CATEGORY_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _ledger_identity(args):
    """Validate the operator-supplied identity of a ledger record.

    Every guard fails LOUDLY on purpose: these ledgers are hand-maintained with
    no generator to reconcile drift, so junk lands permanently. Rejected here:
    a missing title (used to yield `<prefix>-1-none.md`), a control character or
    newline in the title (spliced a SECOND, forged index line — verified exploit
    S-02), an over-long title (ENAMETOOLONG surfaced as an unexpected exit 1),
    a slug that normalizes to nothing (a hidden `.md`), and — for defects — a
    missing or non-conforming category (produced a `## None` section or a
    TypeError traceback, F5).

    Returns the normalized explicit slug, or None when the slug is derived.
    """
    # Validate and NORMALIZE in one place, then write the normalized values back
    # onto args: the first version checked `.strip()`ed copies while the callers
    # passed the raw strings, so ` logic ` passed the category regex and became
    # the un-matchable heading `##  logic `, and a leading \r survived into the
    # record H1 (vdd-multi iteration 2, V3 / V-23).
    title = (args.title or "").strip()
    if not title:
        raise CliError("--title is required to file into a ledger",
                       code=EXIT_USAGE, err_type="UsageError")
    # tested on the RAW value: str.strip() would eat a leading \r or \x0b and
    # hide exactly what we are looking for
    offenders = sorted({ch for ch in (args.title or "")
                        if not ch.isprintable() and ch != "\t"})
    if offenders:
        raise CliError(
            "--title must be a single line without control or invisible "
            "characters (found %s): %r"
            % (", ".join(repr(c) for c in offenders), args.title),
            code=EXIT_USAGE, err_type="UsageError",
            remediation="put multi-line detail in the body (--body-file); the "
                        "title becomes one index line and one H1")
    args.title = title
    if len(title) > _TITLE_MAX:
        raise CliError("--title is %d chars, max %d" % (len(title), _TITLE_MAX),
                       code=EXIT_USAGE, err_type="UsageError",
                       remediation="shorten the title; the detail belongs in "
                                   "the body")
    if args.prefix is not None and not _PREFIX_RE.match(args.prefix):
        raise CliError(
            "--prefix %r is not an identifier (expected %s)"
            % (args.prefix, _PREFIX_RE.pattern),
            code=EXIT_USAGE, err_type="UsageError",
            remediation="prefixes become part of the record id, e.g. RF, SEC, WI")
    # every operator free-text scalar that lands in a git-tracked ledger, not just
    # the body: `--value "rotate sk-live_…"` wrote a credential into frontmatter and
    # a bearer-token-shaped `--title` into the index line, neither screened; `--value`
    # was uncapped so it slipped a 40 KB bullet past `guard_flat_body`
    # (iteration 3, sec-L-04 / L-7)
    body_mod.guard_scalar(args.title, "--title", max_chars=_TITLE_MAX)
    for flag, value in (("--value", args.value), ("--source", args.source),
                        ("--reason", args.reason),
                        ("--component", args.component)):
        body_mod.guard_scalar(value, flag)
    if args.classification == "defect":
        category = (args.category or "").strip()
        if not _CATEGORY_RE.match(category):
            raise CliError(
                "--category is required for a defect and must be a lowercase "
                "single token (got %r)" % args.category,
                code=EXIT_USAGE, err_type="UsageError",
                remediation="use a category from the ledger's prefix→category "
                            "table, e.g. logic / security / performance")
        args.category = category
    if not args.slug:
        return None
    slug = ids_mod.normalize_slug(args.slug)
    if not slug:
        raise CliError(
            "--slug %r normalizes to an empty slug (non-latin or punctuation "
            "only?)" % args.slug, code=EXIT_USAGE, err_type="UsageError",
            remediation="pass an ASCII kebab-case slug, or omit --slug and let "
                        "it be derived from the title")
    if len(slug) > 200:
        raise CliError("--slug is %d chars after normalization, max 200"
                       % len(slug), code=EXIT_USAGE, err_type="UsageError")
    return slug


def _reject_inapplicable_flags(args, layout=None):
    """Refuse flags that the chosen classification/layout would silently drop.

    A silently ignored flag is how "we marked it auto-fixable" survives as a
    belief into a heal run (S-16), and how `--slug` vanished under the flat
    layout (F15). Every one of these is an operator statement of intent about a
    permanent ledger record; dropping it quietly is worse than failing.
    """
    offenders = []
    if args.classification == "work-item":
        for flag, value in (("--auto-fixable", args.auto_fixable),
                            ("--severity", args.severity),
                            ("--category", args.category)):
            if value:
                offenders.append("%s (defects only)" % flag)
        if layout == "flat":
            for flag, value in (("--slug", args.slug), ("--source", args.source)):
                if value:
                    offenders.append('%s (ignored by backlog_layout "flat", '
                                     "which allocates no record)" % flag)
    elif args.classification == "defect":
        for flag, value in (("--effort", args.effort), ("--value", args.value),
                            ("--source", args.source)):
            if value:
                offenders.append("%s (work-items only)" % flag)
    else:  # noise — nothing is recorded but the reason, so nothing else may be
        # silently accepted. This branch was missing, so `--as noise
        # --auto-fixable --severity SEV-2 …` exited 0 having dropped every flag
        # (vdd-multi iteration 2, V-16).
        for flag, value in (("--auto-fixable", args.auto_fixable),
                            ("--severity", args.severity),
                            ("--category", args.category),
                            ("--effort", args.effort), ("--value", args.value),
                            ("--source", args.source), ("--slug", args.slug),
                            ("--prefix", args.prefix),
                            ("--body-file", args.body_file)):
            if value:
                offenders.append("%s (a dismissal records only --reason)" % flag)
    if args.classification != "noise" and args.reason:
        offenders.append("--reason (dismissals only)")
    if offenders:
        raise CliError(
            "these flags do not apply to --as %s: %s"
            % (args.classification, ", ".join(offenders)),
            code=EXIT_USAGE, err_type="UsageError",
            remediation="drop the flag, or change --as; run-feedback refuses "
                        "to accept a flag it would not record")


def _read_body(args, cfg):
    """Read and POLICE the record body — the one gate both ledgers pass through.

    Placed here rather than in either ledger on purpose: a check that lives in one
    writer is a check the other writer does not have, which is the whole shape of
    WI-7. See ``feedback_lib/body.py`` for why the body is capped and screened but
    never rewritten.
    """
    if args.body_file:
        return body_mod.guard_body(
            _read_maybe_stdin(
                "@" + args.body_file if args.body_file != "-" else "-"),
            cfg.body_max_chars,
            source=("stdin" if args.body_file == "-" else args.body_file))
    raise CliError("--body-file is required for this classification",
                   code=EXIT_USAGE, err_type="UsageError")


def _provisional_note(result):
    """Human-readable caveat on a dry-run id.

    The JSON payload carried ``provisional_id`` while the human line presented the
    same id as final — and the human line is what an operator (or a model) copies
    into a plan (iteration 2, V-10). The id comes from a disk scan that a real
    filing can win the race on.
    """
    if not result.get("provisional_id"):
        return ""
    return ("\nNOTE: the id above is PROVISIONAL — it is the next free number as "
            "of this scan, and a filing that lands first will take it.")


def _consume_or_explain(cfg, path, record, new_status, filed_as):
    """Move the finding out of the inbox; if that fails, leave a recoverable state.

    The ledger write already succeeded by this point and is create-only, so a
    failure here used to strand the run: the finding stayed ``new`` while the
    record existed, and every retry hit the create-only guard and exited 4
    **forever**, needing a hand edit to escape (iteration 2, V17).

    So on failure the finding's status is flipped in place, best-effort, and the
    error names both halves of the half-state. A retry then reports "already
    filed" (exit 2, actionable) instead of "record exists" (exit 4, a dead end).
    """
    try:
        inbox.consume(cfg, path, record, new_status)
        return
    except OSError as exc:
        try:
            record["status"] = new_status
            atomic.write_atomic(
                path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")
            noted = "the finding was marked %s in place" % new_status
        except OSError:
            noted = ("the finding could NOT be marked %s and is still `new`"
                     % new_status)
        written = (filed_as or {}).get("path")
        raise CliError(
            "the ledger write succeeded but the finding could not be moved out "
            "of the inbox (%s)" % exc,
            code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
            remediation="%s%s. Do NOT re-run with the same --slug: the record is "
                        "create-only and a retry would exit 4. Move %s to %s by "
                        "hand, or re-file under a new slug after deleting the "
                        "orphan." % (("the record IS written at %s; " % written)
                                     if written else "", noted, path,
                                     cfg.filed_dir if new_status == "filed"
                                     else cfg.dismissed_dir))


def cmd_file(args, cfg):
    path, record = inbox.resolve(cfg, args.finding)
    if record.get("status") != "new":
        raise CliError("finding %s is already %s"
                       % (record["finding_id"], record.get("status")),
                       code=EXIT_USAGE, err_type="UsageError")
    subject = record.get("subject", {})
    lock_fd = None
    if not args.dry_run:
        cfg.feedback_dir.mkdir(parents=True, exist_ok=True)
        lock_fd = os.open(str(cfg.filing_lock), os.O_WRONLY | os.O_CREAT, 0o644)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
    try:
        if args.classification == "defect":
            _reject_inapplicable_flags(args)
            component = args.component or subject.get("component")
            prefix = args.prefix or ids_mod.prefix_for(component,
                                                       cfg.id_prefixes)
            explicit_slug = _ledger_identity(args)
            if explicit_slug:
                slug = explicit_slug
                number = ids_mod.next_number(cfg.issues_dir, prefix)
                issue_id = "%s-%d" % (prefix, number)
            else:
                issue_id, slug = ids_mod.allocate(cfg.issues_dir, prefix,
                                                  args.title)
            extensions = {
                "component": component,
                "fingerprint": record.get("fingerprint"),
                "evidence_paths": record.get("evidence", {}).get("paths", []),
                "auto_fixable": True if args.auto_fixable else None,
                "finding_ref": record.get("finding_id"),
            }
            result = ledger_issues.file_defect(
                cfg, issue_id, slug, args.title, args.category,
                _read_body(args, cfg), severity=args.severity,
                extensions=extensions, dry_run=args.dry_run)
            filed_as = {"ledger": "issues", "id": issue_id,
                        "path": result["issue_path"]}
            human = ("DRY-RUN would file" if args.dry_run else "filed") + \
                " %s -> %s\nindex line: %s%s" % (
                    record["finding_id"], result["issue_path"],
                    result["index_line"], _provisional_note(result))
        elif args.classification == "work-item":
            if not cfg.backlog_path:
                raise CliError("backlog_path is not configured",
                               code=EXIT_CONFIG, err_type="ConfigError")
            _reject_inapplicable_flags(args, layout=cfg.backlog_layout)
            explicit_slug = _ledger_identity(args)
            body = _read_body(args, cfg)
            if cfg.backlog_layout == "flat":
                # legacy one-file backlog: refuse rather than silently inline a
                # structured body into the index line
                bullet = ledger_backlog.format_bullet(
                    args.title, ledger_backlog.guard_flat_body(body),
                    time.strftime("%Y-%m-%d"), effort=args.effort,
                    value=args.value)
                result = ledger_backlog.append_work_item(
                    cfg.backlog_path, cfg.backlog_anchor, bullet,
                    dry_run=args.dry_run)
                filed_as = {"ledger": "backlog", "id": None,
                            "path": str(cfg.backlog_path)}
                human = ("DRY-RUN would append" if args.dry_run
                         else "appended") + " work-item bullet:\n%s" % bullet
            else:
                prefix = args.prefix or cfg.backlog_prefix
                if explicit_slug:
                    slug = explicit_slug
                    item_id = "%s-%d" % (
                        prefix, ids_mod.next_number(cfg.backlog_dir, prefix))
                else:
                    item_id, slug = ids_mod.allocate(cfg.backlog_dir, prefix,
                                                     args.title)
                extensions = {
                    "component": args.component or subject.get("component"),
                    "fingerprint": record.get("fingerprint"),
                    "evidence_paths": record.get("evidence", {}).get("paths", []),
                    "finding_ref": record.get("finding_id"),
                }
                result = ledger_backlog.file_work_item(
                    cfg, item_id, slug, args.title, body, effort=args.effort,
                    value=args.value, source=args.source or _run_source(record),
                    extensions=extensions, dry_run=args.dry_run)
                filed_as = {"ledger": "backlog", "id": item_id,
                            "path": result["record_path"]}
                human = ("DRY-RUN would file" if args.dry_run else "filed") + \
                    " %s -> %s\nindex line: %s%s" % (
                        record["finding_id"], result["record_path"],
                        result["index_line"], _provisional_note(result))
        else:  # noise
            if not args.reason:
                raise CliError("--reason is required for --as noise",
                               code=EXIT_USAGE, err_type="UsageError")
            _reject_inapplicable_flags(args)
            # the noise path never reaches `_ledger_identity`, so `--reason` — which
            # IS recorded, in the finding and the journal — would otherwise be the
            # one operator scalar with no screen at all
            body_mod.guard_scalar(args.reason, "--reason")
            result = {"reason": args.reason}
            filed_as = None
            human = "dismissed %s (%s)" % (record["finding_id"], args.reason)

        if not args.dry_run:
            if args.classification == "noise":
                record["dismiss_reason"] = args.reason
                _consume_or_explain(cfg, path, record, "dismissed", None)
                journal.append_event(cfg.journal_dir, "finding_dismissed",
                                     "%s %s" % (record["fingerprint"],
                                                args.reason))
            else:
                record["filed_as"] = filed_as
                _consume_or_explain(cfg, path, record, "filed", filed_as)
                journal.append_event(
                    cfg.journal_dir, "finding_filed",
                    "%s %s" % (filed_as.get("id") or "backlog",
                               record["finding_id"]),
                    {"ledger": filed_as["ledger"], "path": filed_as["path"]})
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
    _emit(args, {"result": result, "filed_as": filed_as,
                 "dry_run": args.dry_run}, human)
    return EXIT_OK


# --- small subcommands ---------------------------------------------------------

def cmd_journal(args, cfg):
    offset = journal.append_event(cfg.journal_dir, args.event_type,
                                  args.subject, _parse_kv(args.detail))
    _emit(args, {"journal_dir": str(cfg.journal_dir), "byte_offset": offset},
          "journaled %s | %s" % (args.event_type, args.subject))
    return EXIT_OK


def cmd_issues(args, cfg):
    records = ledger_issues.list_issues(
        cfg, status=args.status, component=args.component,
        auto_fixable=True if args.auto_fixable else None)
    records.sort(key=lambda r: (-r["severity_rank"], r.get("opened_at") or ""))
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        for rec in records:
            print("%-24s %-10s %-8s %s" % (rec["id"], rec["status"],
                                           rec["severity"] or "-",
                                           rec["slug"]))
    return EXIT_OK


def cmd_claim(args, cfg):
    acquired, owner = claims.claim(cfg, args.run_id)
    if acquired:
        journal.append_event(cfg.journal_dir, "retro_claimed", args.run_id)
    _emit(args, {"acquired": acquired, "owner": owner},
          "retro %s (owner: %s)" % ("claimed" if acquired else "DENIED",
                                    owner))
    return EXIT_OK if acquired else EXIT_CLAIM_DENIED


def cmd_release(args, cfg):
    released = claims.release(cfg, args.run_id, force=args.force)
    if released:
        journal.append_event(cfg.journal_dir, "retro_released", args.run_id)
    _emit(args, {"released": released},
          "retro %s" % ("released" if released else "NOT released (foreign owner)"))
    return EXIT_OK if released else EXIT_CLAIM_DENIED


def cmd_mine(args, cfg):
    since = None
    if args.since:
        since = time.mktime(time.strptime(args.since, "%Y-%m-%d"))
    emitted, stats = mine_mod.mine(
        cfg, transcript_dirs=args.transcripts_dir or None, since=since,
        session=args.session, include_active=args.include_active,
        frustration=args.frustration, limit=args.limit, dry_run=args.dry_run)
    collected = deduped = 0
    if not args.dry_run:
        for record in emitted:
            _, was_dup = inbox.collect(cfg, record)
            collected += 0 if was_dup else 1
            deduped += 1 if was_dup else 0
        journal.append_event(cfg.journal_dir, "mine_run",
                             "%d candidates" % len(emitted),
                             {**stats, "collected": collected,
                              "deduped": deduped})
    payload = {"stats": stats, "collected": collected, "deduped": deduped,
               "dry_run": args.dry_run,
               "candidates": [
                   {"finding_id": r["finding_id"],
                    "fingerprint": r["fingerprint"], "kind": r["kind"],
                    "component": r["subject"]["component"],
                    "message": r["subject"]["message"],
                    "count": (r["run"].get("extra") or {}).get("count", 1)}
                   for r in emitted]}
    human = ["mine: %(files_scanned)d files scanned, "
             "%(files_skipped_active)d active skipped, "
             "%(candidates)d candidates" % stats]
    for c in payload["candidates"]:
        human.append("  %(kind)s %(component)s ×%(count)s: %(message)s" % c)
    if not args.dry_run:
        human.append("collected %d new, %d deduped" % (collected, deduped))
    _emit(args, payload, "\n".join(human))
    return EXIT_OK


_ID_PREFIX_RE = re.compile(r"^(.+?)-\d")


def cmd_init(args, cfg):
    """Bootstrap docs/feedback/ configs from the shipped templates (create-only).

    Deterministic part of the Bootstrap protocol (SKILL.md §7): copy the two
    config templates into the target repo — never overwriting anything — and
    seed the `id_prefixes` map from the EXISTING ledger (component→prefix pairs
    derived from `docs/issues/*.md` frontmatter). Judgement (backlog anchor,
    heal gates) stays with the agent; the emitted `todo` list names it."""
    templates = Path(__file__).resolve().parents[1] / "assets" / "templates"
    fb_dir = Path(cfg.repo_root) / "docs" / "feedback"
    targets = {
        "config": (fb_dir / "config.json",
                   templates / "feedback_config_template.json"),
        "heal-config": (fb_dir / "heal-config.json",
                        templates / "heal_config_template.json"),
    }
    for _, template in targets.values():
        if not template.is_file():
            raise CliError("config template missing: %s" % template,
                           code=EXIT_CONFIG, err_type="TemplateMissing")

    # Seed component→prefix from the ledger that already exists (if any).
    seeded, conflicts = {}, {}
    issues_dir = Path(cfg.issues_dir)
    if issues_dir.is_dir():
        for path in sorted(issues_dir.glob("*.md")):
            try:
                meta, _ = frontmatter.parse_file(path)
            except Exception:  # noqa: BLE001 - unparseable file is not init's problem
                continue
            issue_id = str(meta.get("id") or "")
            component = str(meta.get("component") or "").strip()
            match = _ID_PREFIX_RE.match(issue_id)
            if not (component and match):
                continue
            prefix = match.group(1)
            if component in seeded and seeded[component] != prefix:
                conflicts.setdefault(component, set()).update(
                    {seeded[component], prefix})
                continue
            seeded[component] = prefix
    for component in conflicts:
        seeded.pop(component, None)

    created, skipped = [], []
    fb_dir.mkdir(parents=True, exist_ok=True)
    for name, (target, template) in targets.items():
        if target.exists():
            skipped.append(str(target))
            continue
        data = json.loads(template.read_text(encoding="utf-8"))
        if name == "config" and seeded:
            data["id_prefixes"].update(seeded)
        atomic.write_atomic(target,
                            json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        created.append(str(target))

    todo = []
    if created:
        todo.append("verify docs/feedback/config.json: backlog_path must point "
                    "at the repo's REAL work-item ledger, with "
                    "'<!-- feedback:discovered-issues -->' seeded inside it; "
                    "backlog_dir (default docs/backlog) holds one file per "
                    "work-item — keep the default two-level layout unless the "
                    "project genuinely wants a single-file backlog")
        todo.append("fill docs/feedback/heal-config.json gates: only "
                    "components with REAL checks; replace 'example-component'")
        todo.append("every prefix in id_prefixes needs a row in the ledger's "
                    "prefix→category table")
    if conflicts:
        todo.append("resolve conflicting prefixes for: %s" % ", ".join(
            "%s (%s)" % (c, "/".join(sorted(v)))
            for c, v in sorted(conflicts.items())))
    payload = {"v": 1, "created": created, "skipped": skipped,
               "seeded_prefixes": seeded,
               "conflicts": {c: sorted(v) for c, v in conflicts.items()},
               "todo": todo}
    _emit(args, payload, "\n".join(
        ["created: %s" % (", ".join(created) or "-"),
         "skipped (already exist): %s" % (", ".join(skipped) or "-"),
         "seeded prefixes: %s" % (json.dumps(seeded, ensure_ascii=False)
                                  if seeded else "-")]
        + (["TODO:"] + ["  - " + t for t in todo] if todo else [])))
    return EXIT_OK


def cmd_doctor(args, cfg):
    checks = {}
    remediation = []
    checks["repo_root"] = str(cfg.repo_root)
    checks["data_root"] = str(cfg.data_root)
    checks["config_source"] = cfg.source or "built-in defaults"
    if not cfg.source:
        remediation.append("no docs/feedback/config.json — run "
                           "`run_feedback.py init` to bootstrap from the "
                           "shipped templates (create-only)")
    # EVERY config-derived probe is guarded. `cfg.issues_dir` and `cfg.index_path`
    # run containment checks that raise on a bad config, and they used to sit
    # outside the try — so `doctor`, the one command whose job is to REPORT a
    # broken config, aborted on it (iteration 2, V9).
    defects_ok = True
    try:
        checks["issues_dir_exists"] = Path(cfg.issues_dir).is_dir()
        checks["index_exists"] = Path(cfg.index_path).is_file()
    except CliError as exc:
        defects_ok = False
        checks["issues_config_error"] = str(exc)
        remediation.append("defect ledger configuration unusable: %s" % exc)
    except OSError as exc:
        defects_ok = False
        checks["issues_config_error"] = str(exc)
        remediation.append("defect ledger path unreadable: %s" % exc)
    template_ok = ledger_issues._seed_template_path().is_file()
    checks["seed_template_reachable"] = template_ok
    if not template_ok and not checks.get("index_exists"):
        remediation.append("known-issues-format seed template unreachable and "
                           "no index exists — filing defects will fail")
    try:
        cfg.feedback_dir.mkdir(parents=True, exist_ok=True)
        # mkstemp, not a fixed `.doctor-probe` + write_text: the name was
        # predictable in a directory another local process can pre-populate, and
        # write_text follows symlinks — the last predictable-name write in the
        # engine (iteration 2, V-08)
        fd, probe = tempfile.mkstemp(dir=str(cfg.feedback_dir),
                                    prefix=".doctor-probe.")
        try:
            os.write(fd, b"ok")
        finally:
            os.close(fd)
            os.unlink(probe)
        checks["feedback_dir_writable"] = True
    except OSError:
        checks["feedback_dir_writable"] = False
        remediation.append("feedback dir not writable: %s" % cfg.feedback_dir)
    try:
        # count directory entries; do NOT parse them. `inbox.scan` opens and
        # json.loads EVERY file, so producing an integer reintroduced the O(k) that
        # WI-5 had just deleted from the capture path — one command over, in the
        # same commit (iteration 3, perf Med-low).
        checks["inbox_depth"] = sum(
            1 for _ in Path(cfg.inbox_dir).glob("fnd-*.json")) \
            if Path(cfg.inbox_dir).is_dir() else 0
    except OSError as exc:
        checks["inbox_depth"] = "unreadable (%s)" % exc
    backlog_usable = True
    if cfg.backlog_path:
        # every probe is wrapped: doctor must REPORT a broken config, not crash
        # on the very misconfiguration it exists to diagnose (F17), and it must
        # not slurp an arbitrary configured path (S-12)
        try:
            backlog_file = Path(cfg.backlog_path)
            exists = backlog_file.is_file()
            anchored = False
            unchecked = False
            if exists:
                size = backlog_file.stat().st_size
                checks["backlog_size_bytes"] = size
                if size > _DOCTOR_READ_CAP:
                    # NOT scanned is not the same as NOT anchored: reporting
                    # `False` here read as "your ledger is broken" for a ledger
                    # nobody looked at, and made `ready` false on a healthy repo
                    # (iteration 2, V9)
                    unchecked = True
                    remediation.append(
                        "backlog %s is %d bytes (> %d cap) — not scanned for "
                        "the anchor" % (backlog_file, size, _DOCTOR_READ_CAP))
                else:
                    # SAME predicate the filing path uses: a substring test
                    # reported "anchor present" for a ledger whose only mention
                    # was documentation prose (F4)
                    anchored = ledger_backlog.has_anchor(
                        backlog_file.read_text(encoding="utf-8"),
                        cfg.backlog_anchor)
            checks["backlog_anchor_present"] = "unchecked" if unchecked else anchored
            layout = cfg.backlog_layout
            checks["backlog_layout"] = layout
            if layout == "index+files":
                checks["backlog_dir"] = str(cfg.backlog_dir)
                checks["backlog_dir_exists"] = Path(cfg.backlog_dir).is_dir()
                backlog_template_ok = (
                    ledger_backlog._seed_template_path().is_file())
                checks["backlog_seed_template_reachable"] = backlog_template_ok
                if not backlog_template_ok and not exists:
                    remediation.append(
                        "known-issues-format backlog template unreachable and "
                        "no backlog exists — filing work-items will fail")
            # "flat" is an explicit opt-in (the default is index+files), so it
            # is reported, not nagged about — a remediation line here would read
            # as a bootstrap signal forever in a repo that deliberately chose it
            backlog_usable = anchored or not exists or unchecked
            if not backlog_usable:
                remediation.append(
                    "backlog %s has no single standalone anchor line %r "
                    "outside a code fence — `file --as work-item` will exit 4"
                    % (backlog_file, cfg.backlog_anchor))
        except CliError as exc:
            backlog_usable = False
            checks["backlog_config_error"] = str(exc)
            remediation.append("backlog configuration unusable: %s" % exc)
        except (OSError, UnicodeDecodeError) as exc:
            # UnicodeDecodeError is not an OSError: a ledger holding one invalid
            # byte crashed the report instead of being reported (iteration 2, V9)
            backlog_usable = False
            checks["backlog_config_error"] = str(exc)
            remediation.append("backlog path unreadable: %s" % exc)
    # a configured-but-unusable backlog is NOT ready: work-item filing, half of
    # what triage produces, would fail every time (F17)
    ready = (checks["feedback_dir_writable"] and backlog_usable and defects_ok
             and (checks.get("index_exists")
                  or checks["seed_template_reachable"]))
    payload = {"v": 1, "ready": ready, "checks": checks,
               "remediation": remediation}
    _emit(args, payload, "\n".join(
        ["ready: %s" % ready]
        + ["  %s: %s" % (k, v) for k, v in checks.items()]
        + (["remediation:"] + ["  - " + r for r in remediation]
           if remediation else [])))
    return EXIT_OK if ready else EXIT_CONFIG


# --- parser -------------------------------------------------------------------

def build_parser(argv=None):
    parser = argparse.ArgumentParser(
        prog="run_feedback.py",
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    install_json_errors(parser, argv)
    parser.add_argument("--repo-root", help="target repo (default: walk up to .git)")
    parser.add_argument("--config", help="explicit config.json path")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("collect", help="queue a finding into the inbox")
    p.add_argument("--source", required=True, choices=finding.SOURCES)
    p.add_argument("--kind", required=True, choices=finding.KINDS)
    p.add_argument("--component", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--command")
    p.add_argument("--exit-code", type=int)
    p.add_argument("--error-envelope",
                   help="inline JSON, @path, or '-' for stdin")
    p.add_argument("--session-id")
    p.add_argument("--task-id")
    p.add_argument("--workflow")
    p.add_argument("--phase")
    p.add_argument("--step")
    p.add_argument("--context", action="append", metavar="K=V")
    p.add_argument("--evidence-path", action="append")
    p.add_argument("--excerpt-file")
    p.add_argument("--propose", choices=finding.CLASSIFICATIONS)
    p.add_argument("--severity")
    p.add_argument("--category")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_collect)

    p = sub.add_parser("triage", help="list inbox findings + dup candidates")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_triage)

    p = sub.add_parser("file", help="file a triaged finding")
    p.add_argument("--finding", required=True,
                   help="finding id, filename, or path")
    p.add_argument("--as", dest="classification", required=True,
                   choices=("defect", "work-item", "noise"))
    p.add_argument("--title")
    p.add_argument("--category")
    p.add_argument("--severity", choices=ledger_issues.SEVERITY_WRITE)
    p.add_argument("--prefix")
    p.add_argument("--slug")
    p.add_argument("--component")
    p.add_argument("--auto-fixable", action="store_true")
    p.add_argument("--body-file", help="path or '-' for stdin")
    p.add_argument("--effort", choices=ledger_backlog.EFFORT_WRITE)
    p.add_argument("--value")
    p.add_argument("--source",
                   help="work-item origin (default: the capture's run context)")
    p.add_argument("--reason")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_file)

    p = sub.add_parser("journal", help="append a journal event")
    p.add_argument("--event-type", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--detail", action="append", metavar="K=V")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_journal)

    p = sub.add_parser("issues", help="machine-readable ledger feed")
    p.add_argument("--status")
    p.add_argument("--component")
    p.add_argument("--auto-fixable", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_issues)

    p = sub.add_parser("claim", help="claim retro ownership")
    p.add_argument("--run-id", required=True)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_claim)

    p = sub.add_parser("release", help="release retro ownership")
    p.add_argument("--run-id", required=True)
    p.add_argument("--force", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_release)

    p = sub.add_parser("mine", help="mine session transcripts for failures")
    p.add_argument("--transcripts-dir", action="append")
    p.add_argument("--since", help="YYYY-MM-DD")
    p.add_argument("--session", help="session uuid")
    p.add_argument("--include-active", action="store_true")
    p.add_argument("--frustration", action="store_true")
    p.add_argument("--limit", type=int)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_mine)

    p = sub.add_parser(
        "init",
        help="bootstrap docs/feedback/ configs from templates (create-only)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("doctor", help="readiness report")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_doctor)

    return parser


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser(argv)
    args = parser.parse_args(argv)
    json_mode = wants_json_errors(argv)
    try:
        cfg = load_config(config_arg=args.config, repo_root=args.repo_root)
        return args.func(args, cfg)
    except CliError as exc:
        if json_mode:
            return emit_json_error(str(exc), code=exc.code,
                                   err_type=exc.err_type, details=exc.details)
        sys.stderr.write("run-feedback: error: %s\n" % exc)
        # Human mode used to DROP the remediation, so every carefully written
        # `remediation=` in this engine was visible only under --json-errors —
        # including the recovery instructions for a half-state, which is the one
        # error whose whole value is telling the operator what to do next
        # (found while testing V17, outside the WI-2..WI-7 list).
        hint = (exc.details or {}).get("remediation")
        if hint:
            sys.stderr.write("run-feedback: hint: %s\n" % hint)
        return exc.code
    except Exception as exc:  # noqa: BLE001 - last-resort envelope
        if json_mode:
            return emit_json_error(str(exc), code=EXIT_UNEXPECTED,
                                   err_type=type(exc).__name__)
        raise


if __name__ == "__main__":
    sys.exit(main())
