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
import time
import fcntl
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from feedback_lib import (claims, filters, finding, frontmatter,
                          ids as ids_mod, inbox, journal, ledger_backlog,
                          ledger_issues, mine as mine_mod)
from feedback_lib.config import load_config
from feedback_lib.envelope import (EXIT_CONFIG, EXIT_OK, EXIT_UNEXPECTED,
                                   EXIT_USAGE, CliError, emit_json_error,
                                   install_json_errors, wants_json_errors)

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
    titles = []
    if Path(cfg.index_path).is_file():
        entry_re = ledger_issues._INDEX_ENTRY_RE
        for line in Path(cfg.index_path).read_text(encoding="utf-8").splitlines():
            match = entry_re.match(line)
            if match:
                title = line[match.end():].split("](", 1)[0].lstrip("[")
                titles.append((match.group(1), title))
    return titles


def _dup_candidates(record, issue_fps, titles):
    dups = []
    fprint = record.get("fingerprint")
    if fprint in issue_fps:
        dups.append("issue %s (fingerprint)" % issue_fps[fprint])
    message_tokens = {t for t in
                      (record["subject"].get("message") or "").lower().split()
                      if len(t) >= 4}
    for issue_id, title in titles:
        overlap = message_tokens & {t for t in title.lower().split()
                                    if len(t) >= 4}
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

def _read_body(args):
    if args.body_file:
        return _read_maybe_stdin(
            "@" + args.body_file if args.body_file != "-" else "-")
    raise CliError("--body-file is required for this classification",
                   code=EXIT_USAGE, err_type="UsageError")


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
            component = args.component or subject.get("component")
            prefix = args.prefix or ids_mod.prefix_for(component,
                                                       cfg.id_prefixes)
            if args.slug:
                slug = ids_mod.normalize_slug(args.slug)
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
                _read_body(args), severity=args.severity,
                extensions=extensions, dry_run=args.dry_run)
            filed_as = {"ledger": "issues", "id": issue_id,
                        "path": result["issue_path"]}
            human = ("DRY-RUN would file" if args.dry_run else "filed") + \
                " %s -> %s\nindex line: %s" % (
                    record["finding_id"], result["issue_path"],
                    result["index_line"])
        elif args.classification == "work-item":
            if not cfg.backlog_path:
                raise CliError("backlog_path is not configured",
                               code=EXIT_CONFIG, err_type="ConfigError")
            bullet = ledger_backlog.format_bullet(
                args.title, _read_body(args), time.strftime("%Y-%m-%d"),
                effort=args.effort, value=args.value)
            result = ledger_backlog.append_work_item(
                cfg.backlog_path, cfg.backlog_anchor, bullet,
                dry_run=args.dry_run)
            filed_as = {"ledger": "backlog", "id": None,
                        "path": str(cfg.backlog_path)}
            human = ("DRY-RUN would append" if args.dry_run else "appended") + \
                " work-item bullet:\n%s" % bullet
        else:  # noise
            if not args.reason:
                raise CliError("--reason is required for --as noise",
                               code=EXIT_USAGE, err_type="UsageError")
            result = {"reason": args.reason}
            filed_as = None
            human = "dismissed %s (%s)" % (record["finding_id"], args.reason)

        if not args.dry_run:
            if args.classification == "noise":
                record["dismiss_reason"] = args.reason
                inbox.consume(cfg, path, record, "dismissed")
                journal.append_event(cfg.journal_dir, "finding_dismissed",
                                     "%s %s" % (record["fingerprint"],
                                                args.reason))
            else:
                record["filed_as"] = filed_as
                inbox.consume(cfg, path, record, "filed")
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
        tmp = target.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        os.replace(tmp, target)
        created.append(str(target))

    todo = []
    if created:
        todo.append("verify docs/feedback/config.json: backlog_path/"
                    "backlog_section must point at a REAL section (or seed "
                    "'<!-- feedback:discovered-issues -->' inside it)")
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
    checks["issues_dir_exists"] = Path(cfg.issues_dir).is_dir()
    checks["index_exists"] = Path(cfg.index_path).is_file()
    template_ok = ledger_issues._seed_template_path().is_file()
    checks["seed_template_reachable"] = template_ok
    if not template_ok and not checks["index_exists"]:
        remediation.append("known-issues-format seed template unreachable and "
                           "no index exists — filing defects will fail")
    try:
        cfg.feedback_dir.mkdir(parents=True, exist_ok=True)
        probe = cfg.feedback_dir / ".doctor-probe"
        probe.write_text("ok")
        probe.unlink()
        checks["feedback_dir_writable"] = True
    except OSError:
        checks["feedback_dir_writable"] = False
        remediation.append("feedback dir not writable: %s" % cfg.feedback_dir)
    if cfg.backlog_path:
        exists = Path(cfg.backlog_path).is_file()
        anchored = exists and (cfg.backlog_anchor
                               in Path(cfg.backlog_path).read_text(
                                   encoding="utf-8"))
        checks["backlog_anchor_present"] = anchored
        if not anchored:
            remediation.append("seed the anchor %r inside the backlog's "
                               "Discovered Issues section"
                               % cfg.backlog_anchor)
    ready = checks["feedback_dir_writable"] and (
        checks["index_exists"] or checks["seed_template_reachable"])
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
    p.add_argument("--effort")
    p.add_argument("--value")
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
        return exc.code
    except Exception as exc:  # noqa: BLE001 - last-resort envelope
        if json_mode:
            return emit_json_error(str(exc), code=EXIT_UNEXPECTED,
                                   err_type=type(exc).__name__)
        raise


if __name__ == "__main__":
    sys.exit(main())
