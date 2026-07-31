#!/usr/bin/env python3
"""Resolve positional (``path:line``) references found in Markdown documents.

Implements the *scriptable toolchain* row of ``documentation-standards`` §4.1:
"Resolve every ``path:line`` from the document and print the target line back for
the author to compare."

Design constraints that shape this tool:

* **Diff-scoped by default.** §4.1 describes a diff-local failure — one task changes
  both an artifact and a document referencing it positionally. Scanning a whole
  repository instead floods the report with archived documents whose references were
  correct when written, which is exactly why a repo-wide gate was rejected.
* **Advisory by default.** Only objectively decidable problems (a path nothing
  resolves to, a line past end-of-file) are errors. Drift suspicion is a warning that
  prints the target line back for a human to judge.
* **Read-only.** The tool never writes to the repository.

Exit codes:
    0: no errors (warnings may still be present)
    1: at least one error, or any finding when ``--strict`` is used
    2: the check could not be performed — not a git repository, git unavailable, or an
       unresolvable ``--base``. Never 0, so a failed query cannot pass for a clean review.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Extensions a positional reference may point at. An explicit allowlist keeps
# host:port strings ("example.com:80") from being read as references.
_EXT = (
    "md|py|yaml|yml|json|sh|bash|zsh|ts|tsx|js|jsx|toml|cfg|ini|txt|sql|"
    "rs|go|java|rb|php|c|h|hpp|cpp|cs|kt|swift|scala|ex|exs"
)

#: ``path/to/file.ext:12``, ``:12-30`` and the pinned form ``:12@v3.21.10``.
CODE_SPAN_REF = re.compile(
    r"`(?P<path>[^`\s]+?\.(?:" + _EXT + r")):(?P<line>\d+)"
    r"(?:-(?P<end>\d+))?"
    r"(?:@(?P<pin>[A-Za-z0-9._~^/-]+))?`"
)

#: Markdown links carrying a line anchor: ``[label](src/main.py#L42-L51)``.
MD_LINK_REF = re.compile(
    r"\[[^\]]*\]\((?P<path>[^)\s#]+?\.(?:" + _EXT + r"))"
    r"#L(?P<line>\d+)(?:-L?(?P<end>\d+))?\)"
)

#: A prose revision pin on the same line, e.g. "verified at v3.19.1", "as of 4f2a91c".
#: The hex alternative excludes all-digit runs so that quantities and dates ("per 1000000
#: requests", "at 20260731") are not mistaken for commit hashes — that would silently
#: exempt a live reference from checking, which is the very failure §4.1 exists to stop.
PROSE_PIN = re.compile(
    r"\b(?:at|as of|per|against)\s+(?:commit\s+|tag\s+|revision\s+)?"
    r"(?P<rev>v\d[\w.\-]*|(?![0-9]+\b)[0-9a-f]{7,40}|HEAD(?:[~^]\d*)?)\b",
    re.IGNORECASE,
)

#: A section ordinal whose target is named immediately before it: a skill name, a repo
#: path, or a markdown link. Ordinals without an adjacent target are out of scope — their
#: antecedent lives in surrounding prose and no regex recovers it.
SECTION_ORDINAL = re.compile(
    r"(?:"
    r"\[[^\]]*\]\((?P<link>[^)\s#]+?\.md)(?:#[^)\s]*)?\)"
    r"|`(?P<quoted>[^`\s]+)`"
    r"|(?<![\w/`-])(?P<bare>[a-z][a-z0-9]*(?:-[a-z0-9]+)+)"
    r")"
    r"[ ,]*(?:SKILL\.md[ ,]*)?"
    r"§\s?(?P<ord>\d+(?:\.\d+)*)"
)

#: Ordinals continuing a chain on the same line: "§1–§7", "§3.1 + §3.3", "§3/§5".
#: They inherit the target of the ordinal that precedes them.
#: Applied with ``.match(line, pos)``, which anchors at ``pos`` on its own.
ORDINAL_CONTINUATION = re.compile(
    r"\s*(?P<sep>[–—-]|[,/+&]|and|or)\s*§\s?(?P<ord>\d+(?:\.\d+)*)",
    re.IGNORECASE,
)

#: Antecedents that are not documents in this repository. Binding these to a sibling
#: SKILL.md manufactures confident failures about files the tool cannot see.
EXTERNAL_ANTECEDENT = re.compile(
    r"\b(?:CommonMark|OWASP|RFC ?\d+|POSIX|ISO ?\d+|Universal-skills|consumer repo)",
    re.IGNORECASE,
)

#: A numbered heading, including range headings such as "## 5-10. Extended Sections".
HEADING_ORDINAL = re.compile(
    r"^#{1,6}\s+(?P<start>\d+(?:\.\d+)*)(?:\s*[-–]\s*(?P<end>\d+))?\.?\s"
)

#: A top-level ordered list item, which declares a sub-ordinal of the enclosing section.
LIST_ORDINAL = re.compile(r"^(?P<indent> {0,3})(?P<num>\d+)[.)]\s")

#: Leading blockquote markers, stripped before headings and list items are recognised.
BLOCKQUOTE_PREFIX = re.compile(r"^(?:\s*>)+ ?")

#: ``ESCAPES_ROOT`` is deliberately NOT here. A path above the root is refused a read — that
#: is the security boundary — but it is *unverifiable*, not provably wrong: this corpus holds
#: genuine cross-repository references. Reporting it as an error would fail correct documents.
ERROR_KINDS = {"UNRESOLVABLE", "AMBIGUOUS", "OUT_OF_RANGE", "ORDINAL_MISSING"}


@dataclass
class Ref:
    """A single positional reference discovered in a document.

    Attributes:
        doc: Repo-relative path of the document containing the reference.
        doc_line: 1-indexed line of the document where the reference appears.
        path: The referenced path exactly as written by the author.
        line: The referenced start line number.
        end: The referenced end line number, when a range was written.
        pin: Revision identifier if the reference is pinned, else ``None``.
    """

    doc: str
    doc_line: int
    path: str
    line: int = 0
    end: int | None = None
    pin: str | None = None
    ordinal: str | None = None

    @property
    def label(self) -> str:
        """Return the reference as the author wrote it, for display."""
        return f"{self.path} §{self.ordinal}" if self.ordinal else f"{self.path}:{self.line}"


@dataclass
class Finding:
    """A classified reference plus the evidence a reviewer needs to judge it."""

    ref: Ref
    kind: str
    detail: str = ""
    target: str | None = None
    target_text: str | None = None
    candidates: list[str] = field(default_factory=list)

    @property
    def severity(self) -> str:
        """Return ``"error"`` for objective defects, ``"warning"`` otherwise."""
        return "error" if self.kind in ERROR_KINDS else "warning"


class GitError(RuntimeError):
    """A git query failed.

    This is deliberately an exception rather than an empty result. A failed query that
    degrades to "nothing changed" would make the tool report success while checking
    nothing — the same silent pass §4.1 exists to prevent.
    """


def _git(root: Path, *args: str) -> list[str]:
    """Run a read-only git command and return its stdout lines.

    Args:
        root: Repository root the command runs in.
        *args: Arguments passed to git.

    Returns:
        Stdout split into non-empty lines.

    Raises:
        GitError: If git is unavailable or the command exits non-zero.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitError("git executable not found on PATH") from exc

    if proc.returncode != 0:
        detail = proc.stderr.strip().splitlines()
        hint = detail[0] if detail else f"exit {proc.returncode}"
        raise GitError(f"`git {' '.join(args)}` failed: {hint}")
    return [ln for ln in proc.stdout.splitlines() if ln.strip()]


def tracked_files(root: Path) -> list[str]:
    """Return every git-tracked path in the repository, repo-relative."""
    return _git(root, "ls-files")


def has_commits(root: Path) -> bool:
    """Return whether the repository has at least one commit."""
    try:
        _git(root, "rev-parse", "--verify", "HEAD")
        return True
    except GitError:
        return False


def safe_join(root: Path, rel: str) -> Path | None:
    """Join a document-supplied path to the repository root, refusing escapes.

    The check is **lexical** and does not call ``resolve()``: this repository legitimately
    contains symlinked skill directories, and resolving them would push a valid target
    outside the root and reject it. Traversal and absolute paths are still refused, so a
    document cannot make the tool read arbitrary files on the host.

    Args:
        root: Repository root.
        rel: Path exactly as written in the document.

    Returns:
        The joined path, or ``None`` if the path is absolute or escapes the root.
    """
    if os.path.isabs(rel) or (len(rel) > 1 and rel[1] == ":"):
        return None
    normalized = os.path.normpath(rel)
    if normalized == ".." or normalized.startswith(".." + os.sep) or os.path.isabs(normalized):
        return None
    return root / normalized


def build_suffix_index(paths: list[str]) -> dict[str, list[str]]:
    """Index paths by every trailing path segment, for shorthand resolution.

    ``docs/reviews/audit.md`` is indexed under ``audit.md``, ``reviews/audit.md``
    and the full path, so an author writing a shorthand can still be resolved —
    and a shorthand matching several files can be reported as ambiguous.

    Args:
        paths: Repo-relative paths.

    Returns:
        Mapping of path suffix to the list of full paths sharing it.
    """
    index: dict[str, list[str]] = {}
    for full in paths:
        parts = full.split("/")
        for i in range(len(parts)):
            index.setdefault("/".join(parts[i:]), []).append(full)
    return index


def changed_files(root: Path, base: str) -> set[str]:
    """Return paths changed between ``base`` and the working tree, plus untracked.

    The base revision is verified before it is used. A revision that does not exist is an
    error rather than an empty diff, because an empty diff silently disables every drift
    check and still exits 0 — a mistyped ``--base`` would look exactly like a clean review.

    Args:
        root: Repository root.
        base: Git revision to diff against (``HEAD`` means uncommitted work).

    Returns:
        Set of repo-relative paths considered part of the current change.

    Raises:
        GitError: If ``base`` cannot be resolved to a commit.
    """
    untracked = set(_git(root, "ls-files", "--others", "--exclude-standard"))

    if base == "HEAD" and not has_commits(root):
        # A repository with no commits: every file present is part of the first change.
        return untracked

    try:
        _git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    except GitError as exc:
        raise GitError(f"unknown revision {base!r} — nothing was compared") from exc

    return set(_git(root, "diff", "--name-only", base)) | untracked


def extract_refs(doc_rel: str, text: str) -> list[Ref]:
    """Extract every positional reference from a document's text.

    A reference is treated as pinned — and therefore a deliberate claim about a past
    revision — when it carries an ``@rev`` suffix or when its line contains a prose
    revision identifier.

    A prose pin applies **only when the line carries a single reference**. Prose is
    line-granular and cannot say which reference it qualifies, so on a line mixing a
    historical quotation with a live reference it would silently exempt both. Explicit
    ``@rev`` suffixes are per-reference and always apply.

    Args:
        doc_rel: Repo-relative path of the document, recorded on each ref.
        text: Full document text.

    Returns:
        References in document order within each line.
    """
    refs: list[Ref] = []
    for doc_line, line in enumerate(text.splitlines(), start=1):
        matches = [
            m for pattern in (CODE_SPAN_REF, MD_LINK_REF) for m in pattern.finditer(line)
        ]
        matches.sort(key=lambda m: m.start())

        prose = PROSE_PIN.search(line)
        prose_rev = prose.group("rev") if prose and len(matches) == 1 else None

        for m in matches:
            groups = m.groupdict()
            end = groups.get("end")
            refs.append(
                Ref(
                    doc=doc_rel,
                    doc_line=doc_line,
                    path=groups["path"],
                    line=int(groups["line"]),
                    end=int(end) if end else None,
                    pin=groups.get("pin") or prose_rev,
                )
            )
    return refs


def parse_ordinals(lines: list[str]) -> set[str]:
    """Collect every section ordinal a document declares.

    Two things declare an ordinal, and both are needed. Numbered **headings** are the
    obvious case, including range headings like ``## 5-10. Extended Sections``. Numbered
    **list items** under a numbered section are the non-obvious one: references such as
    ``01_orchestrator.md §1.3`` and ``run-feedback §7.1`` address a list item, not a
    heading, and an index that skips them reports correct references as broken.

    Args:
        lines: The target document's lines.

    Returns:
        Every declared ordinal as a dotted string, e.g. ``{"4", "4.1", "7.1"}``.
    """
    declared: set[str] = set()
    section: str | None = None

    for raw in lines:
        # Strip blockquote markers: prime-directive style lists are quoted, and their
        # items are exactly what references like `01_orchestrator.md` §1.3 address.
        raw = BLOCKQUOTE_PREFIX.sub("", raw)
        heading = HEADING_ORDINAL.match(raw)
        if heading:
            start = heading.group("start")
            declared.add(start)
            end = heading.group("end")
            if end and "." not in start:
                # "## 5-10. Extended Sections" declares every ordinal in the range.
                for n in range(int(start), int(end) + 1):
                    declared.add(str(n))
            section = start
            continue

        if section is None or "." in section:
            continue
        item = LIST_ORDINAL.match(raw)
        if item and len(item.group("indent")) == 0:
            declared.add(f"{section}.{item.group('num')}")
    return declared


def extract_ordinal_refs(doc_rel: str, text: str) -> list[Ref]:
    """Extract section-ordinal references that name their target adjacently.

    Only the verifiable slice is extracted. An ordinal whose antecedent sits in
    surrounding prose ("see §4.2", "TASK §4") is deliberately skipped: its target cannot
    be recovered mechanically, and guessing one manufactures false failures.

    Args:
        doc_rel: Repo-relative path of the document.
        text: Full document text.

    Returns:
        Ordinal references, including same-line chain continuations.
    """
    refs: list[Ref] = []
    for doc_line, line in enumerate(text.splitlines(), start=1):
        for m in SECTION_ORDINAL.finditer(line):
            antecedent = m.group("link") or m.group("quoted") or m.group("bare")
            prefix = line[max(0, m.start() - 40) : m.end()]
            if EXTERNAL_ANTECEDENT.search(prefix):
                continue

            pin = PROSE_PIN.search(line)
            ordinals = [m.group("ord")]

            # Absorb "§1–§7" / "§3.1 + §3.3" continuations that inherit this target.
            pos = m.end()
            while (cont := ORDINAL_CONTINUATION.match(line, pos)) is not None:
                previous, current = ordinals[-1], cont.group("ord")
                if cont.group("sep") in "–—-" and "." not in previous and "." not in current:
                    ordinals.extend(str(n) for n in range(int(previous) + 1, int(current) + 1))
                else:
                    ordinals.append(current)
                pos = cont.end()

            for ordinal in ordinals:
                refs.append(
                    Ref(
                        doc=doc_rel,
                        doc_line=doc_line,
                        path=antecedent,
                        pin=pin.group("rev") if pin else None,
                        ordinal=ordinal,
                    )
                )
    return refs


def resolve_ordinal_target(root: Path, antecedent: str) -> str | None:
    """Map an ordinal's antecedent to a repo-relative document, or ``None``.

    Args:
        root: Repository root.
        antecedent: The token written before the ordinal.

    Returns:
        A repo-relative path, or ``None`` when the antecedent names no document here.
    """
    joined = safe_join(root, antecedent)
    if joined is not None and joined.is_file():
        return os.path.normpath(antecedent)

    skill = safe_join(root, f".agent/skills/{antecedent}/SKILL.md")
    if skill is not None and skill.is_file():
        return f".agent/skills/{antecedent}/SKILL.md"
    return None


def classify_ordinal(
    ref: Ref,
    root: Path,
    line_cache: dict[str, list[str]],
    ordinal_cache: dict[str, set[str]],
) -> Finding | None:
    """Check that an ordinal reference addresses a section its target declares.

    Args:
        ref: The ordinal reference.
        root: Repository root.
        line_cache: Memoized file contents.
        ordinal_cache: Memoized ordinal sets, keyed by repo-relative path.

    Returns:
        A :class:`Finding` when the ordinal does not exist, else ``None``.
    """
    if ref.pin:
        return None

    target = resolve_ordinal_target(root, ref.path)
    if target is None:
        return None  # Informal label, workflow basename, or a file in another repository.

    if target not in ordinal_cache:
        try:
            lines = (root / target).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return None
        line_cache.setdefault(target, lines)
        ordinal_cache[target] = parse_ordinals(lines)

    declared = ordinal_cache[target]
    if not declared:
        # The target numbers nothing; the reference is unverifiable, not wrong.
        return None
    if ref.ordinal in declared:
        return None

    return Finding(
        ref,
        "ORDINAL_MISSING",
        f"{target} declares no §{ref.ordinal}",
        target=target,
    )


def classify(
    ref: Ref,
    root: Path,
    index: dict[str, list[str]],
    changed: set[str],
    line_cache: dict[str, list[str]],
) -> Finding | None:
    """Classify one reference against the working tree.

    Args:
        ref: The reference to classify.
        root: Repository root.
        index: Suffix index built by :func:`build_suffix_index`.
        changed: Paths belonging to the current change.
        line_cache: Memoized file contents, keyed by repo-relative path.

    Returns:
        A :class:`Finding` when the reference needs attention, else ``None``.
    """
    if ref.pin:
        return None

    if ref.line < 1 or (ref.end is not None and ref.end < ref.line):
        # Guard before any indexing: `:0` would otherwise reach lines[-1] and hand the
        # reviewer the LAST line of the file as evidence for the FIRST.
        return Finding(ref, "OUT_OF_RANGE", "line numbers start at 1 and ranges ascend")

    joined = safe_join(root, ref.path)
    if joined is None:
        return Finding(
            ref,
            "ESCAPES_ROOT",
            "points outside the repository — refused a read, and not verifiable here",
        )

    candidates = index.get(ref.path, [])
    if joined.is_file():
        candidates = [os.path.normpath(ref.path)]

    if not candidates:
        detail = (
            "nothing is tracked in this repository yet"
            if not index
            else "no file in the repository matches this path"
        )
        return Finding(ref, "UNRESOLVABLE", detail)
    if len(candidates) > 1:
        return Finding(
            ref,
            "AMBIGUOUS",
            f"{len(candidates)} files match this shorthand; write a repo-relative path",
            candidates=sorted(candidates)[:5],
        )

    target = candidates[0]
    if target not in line_cache:
        try:
            line_cache[target] = (root / target).read_text(
                encoding="utf-8", errors="replace"
            ).splitlines()
        except OSError as exc:  # unreadable target is an environment problem, not drift
            return Finding(ref, "UNRESOLVABLE", f"cannot read target: {exc}", target=target)
    lines = line_cache[target]

    last = ref.end or ref.line
    if last > len(lines):
        return Finding(
            ref,
            "OUT_OF_RANGE",
            f"target has {len(lines)} lines",
            target=target,
        )

    if target in changed:
        return Finding(
            ref,
            "DRIFT_SUSPECT",
            "target is modified by this same change — re-check after the edits are final",
            target=target,
            target_text=lines[ref.line - 1].strip(),
        )
    return None


def collect_docs(root: Path, changed: set[str], scan_all: list[str] | None) -> list[str]:
    """Choose which Markdown documents to inspect.

    Args:
        root: Repository root.
        changed: Paths belonging to the current change.
        scan_all: Roots to scan exhaustively, or ``None`` for diff scope.

    Returns:
        Sorted repo-relative Markdown paths.
    """
    if scan_all is not None:
        docs: set[str] = set()
        for base in scan_all:
            for path in (root / base).rglob("*.md"):
                if path.is_file():
                    docs.add(str(path.relative_to(root)))
        return sorted(docs)
    return sorted(d for d in changed if d.endswith(".md") and (root / d).is_file())


@dataclass
class Report:
    """The outcome of one run.

    Attributes:
        findings: Classified references needing attention.
        doc_count: How many documents were actually inspected.
        ref_count: How many positional references were resolved.
        notes: Scope caveats the reader needs in order to trust the verdict.
    """

    findings: list[Finding] = field(default_factory=list)
    doc_count: int = 0
    ref_count: int = 0
    ordinal_count: int = 0
    notes: list[str] = field(default_factory=list)


def run(root: Path, base: str, scan_all: list[str] | None) -> Report:
    """Collect findings for the selected document set.

    Args:
        root: Repository root.
        base: Git revision defining the current change.
        scan_all: Roots to scan exhaustively, or ``None`` for diff scope.

    Returns:
        A :class:`Report`. Counting happens here, not in the caller, so the printed
        totals cannot drift from the findings they summarise.

    Raises:
        GitError: If the repository cannot be queried or ``base`` does not resolve.
    """
    tracked = tracked_files(root)
    index = build_suffix_index(tracked)
    changed = changed_files(root, base)
    line_cache: dict[str, list[str]] = {}
    ordinal_cache: dict[str, set[str]] = {}
    report = Report()

    if not tracked:
        report.notes.append("no tracked files: every reference will fail to resolve")

    docs = collect_docs(root, changed, scan_all)
    report.doc_count = len(docs)

    for doc in docs:
        text = (root / doc).read_text(encoding="utf-8", errors="replace")

        for ref in extract_refs(doc, text):
            report.ref_count += 1
            found = classify(ref, root, index, changed, line_cache)
            if found:
                report.findings.append(found)

        for ref in extract_ordinal_refs(doc, text):
            report.ordinal_count += 1
            found = classify_ordinal(ref, root, line_cache, ordinal_cache)
            if found:
                report.findings.append(found)

    if report.ordinal_count:
        report.notes.append(
            "section ordinals: only those naming their target adjacently are checked; "
            "bare ordinals (§4.2) are out of scope and were NOT verified"
        )
    return report


def format_text(report: Report) -> str:
    """Render a report as human-readable text."""
    doc_count, findings = report.doc_count, report.findings
    suffix = "".join(f"\nnote: {n}" for n in report.notes)

    if doc_count == 0:
        # Never phrase an empty scope as a pass: "OK" here would be a verification claim
        # about documents nobody looked at — the §4.1 failure in miniature.
        return (
            "NOTHING CHECKED: no Markdown document is in scope. "
            "Nothing was verified." + suffix
        )
    if not findings:
        return (
            f"OK: {report.ref_count} path:line + {report.ordinal_count} ordinal "
            f"reference(s) in {doc_count} document(s) resolve against the working tree."
            + suffix
        )

    lines: list[str] = []
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    for group, title in ((errors, "ERRORS"), (warnings, "REVIEW (§4.1)")):
        if not group:
            continue
        lines.append(f"--- {title} ---")
        for f in group:
            lines.append(f"  {f.ref.doc}:{f.ref.doc_line}  [{f.kind}]")
            lines.append(f"    ref    : {f.ref.label}")
            lines.append(f"    detail : {f.detail}")
            if f.candidates:
                lines.append(f"    matches: {', '.join(f.candidates)}")
            if f.target_text is not None:
                lines.append(f"    line   : {f.target_text!r}")
        lines.append("")

    lines.append(
        f"{len(errors)} error(s), {len(warnings)} warning(s) across "
        f"{report.ref_count} reference(s) in {doc_count} document(s)."
    )
    if warnings:
        lines.append(
            "Warnings are not failures: confirm each line still says what the document "
            "claims, or pin the reference with @<rev>."
        )
    for note in report.notes:
        lines.append(f"note: {note}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. See module docstring for exit codes."""
    parser = argparse.ArgumentParser(
        description=(
            "Resolve positional path:line references in Markdown "
            "(documentation-standards §4.1)."
        )
    )
    parser.add_argument("--root", default=".", help="Repository root (default: cwd).")
    parser.add_argument(
        "--base",
        default="HEAD",
        help="Revision defining the current change (default: HEAD = uncommitted work).",
    )
    parser.add_argument(
        "--all",
        nargs="*",
        metavar="DIR",
        default=None,
        help="Scan these directories exhaustively instead of the diff (default: docs).",
    )
    parser.add_argument("--json", action="store_true", help="Emit findings as JSON.")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as failures (exit 1)."
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / ".git").exists():
        print(f"error: {root} is not a git repository", file=sys.stderr)
        return 2

    scan_all = None
    if args.all is not None:
        scan_all = args.all or ["docs"]

    try:
        report = run(root, args.base, scan_all)
    except GitError as exc:
        # Exit 2, never 0: a repository the tool could not query has not been checked,
        # and a mistyped --base must not be indistinguishable from a clean review.
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "doc_count": report.doc_count,
                    "ref_count": report.ref_count,
                    "ordinal_count": report.ordinal_count,
                    "notes": report.notes,
                    "findings": [
                        {
                            "doc": f.ref.doc,
                            "doc_line": f.ref.doc_line,
                            "path": f.ref.path,
                            "line": f.ref.line,
                            "ordinal": f.ref.ordinal,
                            "label": f.ref.label,
                            "kind": f.kind,
                            "severity": f.severity,
                            "detail": f.detail,
                            "target": f.target,
                            "target_text": f.target_text,
                            "candidates": f.candidates,
                        }
                        for f in report.findings
                    ],
                },
                indent=2,
            )
        )
    else:
        print(format_text(report))

    if any(f.severity == "error" for f in report.findings):
        return 1
    if args.strict and report.findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
