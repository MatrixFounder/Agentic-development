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
* **The check never writes; ``--fix`` writes a line number and never writes a referent.** The
  default invocation is read-only. ``--fix`` is a separate invocation — the ``format:check``
  / ``format`` pairing, not a gate that mutates the tree it is judging — and its authority
  is bounded by what the two objects are: a referent is the CLAIM and is never
  machine-written, a line number is a value DERIVED from it and may be recomputed. It
  rewrites only ``REFERENT_MOVED``, only inside the reference span, and never the two
  verdicts a human must settle (TASK 103 D4).

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

#: A prose revision pin on the same line, e.g. "verified at v3.19.1", "на `985f843`".
#:
#: The pattern matches the revision TOKEN, not an English preposition. Anchoring on
#: "at / as of / per" made the documented escape hatch silently inert in every
#: non-English document — the mechanism looked present and did nothing, which is exactly
#: the failure mode §4.1 exists to stop. A revision-shaped token is language-independent.
#:
#: The hex alternative demands at least one digit AND at least one a-f letter. That
#: excludes quantities and dates ("1000000", "20260731") on one side and ordinary words
#: that happen to be hex-legal ("deadbeef", "defaced") on the other. Scope stays bounded
#: because a prose pin only applies to a line carrying a single reference.
#: A hash-shaped token: 7-40 hex digits carrying at least one digit AND one a-f letter.
#: Both are required — an all-digit run is a quantity or a date, an all-letter run is a
#: word that happens to be hex-legal ("deadbeef", "defaced").
_SHA = (
    r"(?<![0-9a-fA-F])(?=[0-9a-fA-F]*[0-9])(?=[0-9a-fA-F]*[a-fA-F])"
    r"[0-9a-fA-F]{7,40}(?![0-9a-fA-F])"
)

#: An English lead-in that announces a revision.
_CUE = r"\b(?:at|as of|per|against)\s+(?:commit\s+|tag\s+|revision\s+)?"

PROSE_PIN = re.compile(
    # 1. A BACKTICKED hash pins in any language. The backticks are what carry the meaning
    #    across languages: they mark the token as an identifier rather than prose, which
    #    no list of prepositions can do. This is the form real documents use — ``на
    #    `985f843` `` — and it is why the rule no longer depends on English.
    r"`(?P<quoted>" + _SHA + r")`"
    # 2. HEAD pins in any language, matched CASE-SENSITIVELY. Lower-case "head" is an
    #    ordinary English word ("the head of the list"), and honouring it would exempt
    #    every line containing it — a silent miss, which is the worst outcome here.
    r"|(?<!\w)(?P<head>(?-i:HEAD(?:[~^]\d*)*))(?!\w)"
    # 3. A BARE hash or version pins only after an English cue. Unmarked hex is a CSS
    #    colour, a build id or a digest far more often than a revision, and a bare version
    #    is usually the subject of the sentence ("bump to v3.4").
    r"|" + _CUE + r"(?P<cued>" + _SHA + r"|v\d[\w.\-]*)",
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

#: ANY section ordinal, whether or not its target can be identified. Counting these is how
#: the report can state what it did NOT examine instead of quietly omitting it.
ANY_ORDINAL = re.compile(r"§\s?\d+(?:\.\d+)*")

#: ``ESCAPES_ROOT`` is deliberately NOT here. A path above the root is refused a read — that
#: is the security boundary — but it is *unverifiable*, not provably wrong: this corpus holds
#: genuine cross-repository references. Reporting it as an error would fail correct documents.
#: The three referent verdicts are errors: each names a coordinate the tree contradicts.
#: ``REFERENT_MOVED`` is an error even though ``--fix`` repairs it mechanically — the document
#: asserts a wrong number until it is repaired, and a warning is the class readers skip.
ERROR_KINDS = {
    "UNRESOLVABLE",
    "AMBIGUOUS",
    "OUT_OF_RANGE",
    "ORDINAL_MISSING",
    "REFERENT_MOVED",
    "REFERENT_AMBIGUOUS",
    "REFERENT_ABSENT",
}

#: A REFERENT: the code span immediately following a reference span, separated by nothing
#: but whitespace and at most one comma.
#:
#: This is the form authors already write — ``\`registry.ts:1083\`, \`if (deadlineHit …) {\```
#: — so licensing it introduces no syntax. Adjacency is the same mechanism ``SECTION_ORDINAL``
#: uses to bind an ordinal to the target named beside it.
#:
#: A referent is NOT an anchor. ``documentation-standards`` §4.3 defines an anchor as
#: ``<!-- contract:<name> -->``, which addresses a SECTION of a document. A referent identifies
#: what a COORDINATE claims to point at. Two objects, two names, kept apart on purpose.
#: No ``^``: this is applied with ``.match(line, pos)``, which anchors at ``pos`` on its own,
#: while ``^`` would still demand the real start of the string and match nothing.
#: ``ORDINAL_CONTINUATION`` above carries the same note for the same reason.
REFERENT_SPAN = re.compile(r"[ \t]*,?[ \t]*`(?P<referent>[^`]+)`")

#: Applied to a referent and to a candidate target line before they are compared.
_WS_RUN = re.compile(r"\s+")


@dataclass
class Ref:
    # Raw string: the ``md_link`` note below writes escaped backticks (\`) to show a
    # literal code span. That is not a valid Python escape — under a plain string it
    # raises SyntaxWarning on 3.12+ and becomes a SyntaxError in a later version. Raw
    # keeps the docstring's runtime text byte-identical to what it already was.
    r"""A single positional reference discovered in a document.

    Attributes:
        doc: Repo-relative path of the document containing the reference.
        doc_line: 1-indexed line of the document where the reference appears.
        path: The referenced path exactly as written by the author.
        line: The referenced start line number.
        end: The referenced end line number, when a range was written.
        pin: Revision identifier if the reference is pinned, else ``None``.
        md_link: True when the reference was written as a Markdown link. Markdown
            link targets are resolved relative to the CONTAINING DOCUMENT, per the
            Markdown spec; a code span such as ``\`src/app.py:42\``` is repo-relative
            by this framework's convention. Conflating the two reports correct
            documents as escaping the root — `docs/reviews/x.md` linking
            ``../../.agent/...`` is a valid link to a repo file, and was flagged.
    """

    doc: str
    doc_line: int
    path: str
    line: int = 0
    end: int | None = None
    pin: str | None = None
    ordinal: str | None = None
    md_link: bool = False
    #: The referent quoted beside this reference, normalized, or ``None`` when it carries
    #: none. ``None`` means unverifiable, never wrong — see :func:`extract_referent`.
    referent: str | None = None
    #: Column offsets of the line-number token, so ``--fix`` can rewrite exactly it.
    num_start: int = 0
    num_end: int = 0
    #: Column offsets of the WHOLE reference span. ``--fix`` rewrites inside this slice and
    #: reassembles the line around it untouched, so no other byte of the document can move.
    span_start: int = 0
    span_end: int = 0

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
    #: For ``REFERENT_MOVED``: the 1-indexed line the referent actually sits on. This is the
    #: value ``--fix`` writes, and the only value it is ever permitted to write.
    target_line: int | None = None

    @property
    def severity(self) -> str:
        """Return ``"error"`` for objective defects, ``"warning"`` otherwise."""
        return "error" if self.kind in ERROR_KINDS else "warning"


def normalize_for_match(text: str) -> str:
    """Return ``text`` in the form referent comparison uses.

    Two normalizations, each required by a place documents actually put quotations:

    * **Whitespace runs collapse.** A quotation in prose wraps across document lines, and the
      target line carries its own indentation. Comparing raw text fails both.
    * **``\\|`` unescapes to ``|``.** A quotation inside a Markdown table cell MUST escape the
      pipe or the cell splits. Without this, every referent quoting a boolean-or or a union
      type fails inside a table — which is exactly where plans put them.

    Without both, a correctly written referent reports as broken, and a gate that fails correct
    documents is switched off (``documentation-standards`` §4.2).
    """
    return _WS_RUN.sub(" ", text.replace("\\|", "|")).strip()


def extract_referent(line: str, ref_end: int) -> str | None:
    """Return the referent following a reference span, or ``None``.

    Args:
        line: The document line carrying the reference.
        ref_end: Offset just past the reference's closing backtick.

    Returns:
        The referent text, normalized by :func:`normalize_for_match`, or ``None`` when the
        reference carries none. ``None`` is not a defect: an unreferenced coordinate is
        *unverifiable*, and the caller counts it as not examined.

    A referent FOLLOWS its reference and sits on the SAME document line (TASK 103 D9). One
    direction is licensed because a line carrying two references and one quotation is
    otherwise unassignable, and one line because ``extract_refs`` scans line by line, so a
    span wrapped across two document lines is not one span. A quotation written before its
    coordinate is therefore not examined — not reported as broken.
    """
    match = REFERENT_SPAN.match(line, ref_end)
    if match is None:
        return None
    referent = normalize_for_match(match.group("referent"))
    return referent or None


def prose_pin_for_line(line: str) -> str | None:
    """Return the revision a line's prose pins, or ``None``.

    Prose is line-granular: it cannot say *which* reference it qualifies. So a prose pin
    applies only when the line carries exactly one reference — counting `path:line` and
    `§` ordinals together, since a line mixing the two is just as ambiguous as a line
    with two of either. Explicit ``@rev`` suffixes are per-reference and bypass this.

    Args:
        line: One line of a document.

    Returns:
        The revision identifier, or ``None`` when the line has no pin or too many
        references for one to be unambiguous.
    """
    sites = sum(
        1
        for pattern in (CODE_SPAN_REF, MD_LINK_REF, SECTION_ORDINAL)
        for _ in pattern.finditer(line)
    )
    if sites != 1:
        return None
    return _pin_of(PROSE_PIN.search(line))


def _pin_of(match: re.Match | None) -> str | None:
    """Return the revision a :data:`PROSE_PIN` match names, or ``None``.

    The pattern has three alternatives, so the caller must not assume a single group.
    """
    if match is None:
        return None
    return match.group("quoted") or match.group("head") or match.group("cued")


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
            (m, pattern is MD_LINK_REF)
            for pattern in (CODE_SPAN_REF, MD_LINK_REF)
            for m in pattern.finditer(line)
        ]
        matches.sort(key=lambda pair: pair[0].start())
        prose_rev = prose_pin_for_line(line)

        for m, is_md_link in matches:
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
                    md_link=is_md_link,
                    referent=extract_referent(line, m.end()),
                    num_start=m.start("line"),
                    num_end=m.end("line"),
                    span_start=m.start(),
                    span_end=m.end(),
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
        pin = prose_pin_for_line(line)
        for m in SECTION_ORDINAL.finditer(line):
            antecedent = m.group("link") or m.group("quoted") or m.group("bare")
            prefix = line[max(0, m.start() - 40) : m.end()]
            if EXTERNAL_ANTECEDENT.search(prefix):
                continue

            ordinals = [m.group("ord")]

            # Absorb "§1–§7" / "§3.1 + §3.3" continuations that inherit this target.
            pos = m.end()
            while (cont := ORDINAL_CONTINUATION.match(line, pos)) is not None:
                previous, current = ordinals[-1], cont.group("ord")
                if cont.group("sep") in "–—-" and "." not in previous and "." not in current:
                    if int(current) < int(previous):
                        # A descending range ("§5–§3") asserts nothing coherent. Keep both
                        # endpoints rather than silently dropping the tail.
                        ordinals.append(current)
                    else:
                        ordinals.extend(
                            str(n) for n in range(int(previous) + 1, int(current) + 1)
                        )
                else:
                    ordinals.append(current)
                pos = cont.end()

            for ordinal in ordinals:
                refs.append(
                    Ref(
                        doc=doc_rel,
                        doc_line=doc_line,
                        path=antecedent,
                        pin=pin,
                        ordinal=ordinal,
                    )
                )
    return refs


def count_out_of_scope_ordinals(text: str) -> int:
    """Count `§` ordinals the tool never examines.

    These are the bare ones (`see §4.2`, `TASK §4`) and the ones pointing at an external
    specification. They are not failures — their target simply cannot be identified. They
    ARE, however, the majority, so a report that omits them lets a green run be read as
    covering every ordinal in the document.

    Args:
        text: Full document text.

    Returns:
        How many ordinal tokens fall outside the checked slice.
    """
    total = 0
    for line in text.splitlines():
        covered: list[tuple[int, int]] = []
        for m in SECTION_ORDINAL.finditer(line):
            if EXTERNAL_ANTECEDENT.search(line[max(0, m.start() - 40) : m.end()]):
                continue
            end = m.end()
            while (cont := ORDINAL_CONTINUATION.match(line, end)) is not None:
                end = cont.end()
            covered.append((m.start(), end))

        for token in ANY_ORDINAL.finditer(line):
            if not any(start <= token.start() < end for start, end in covered):
                total += 1
    return total


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
) -> tuple[Finding | None, str]:
    """Check that an ordinal reference addresses a section its target declares.

    Args:
        ref: The ordinal reference.
        root: Repository root.
        line_cache: Memoized file contents.
        ordinal_cache: Memoized ordinal sets, keyed by repo-relative path.

    Returns:
        ``(finding, outcome)``. The outcome names why an ordinal was or was not checked, so
        the report can say which references it actually verified instead of implying all of
        them. Outcomes: ``checked``, ``pinned``, ``unknown-target``, ``unnumbered-target``.
    """
    if ref.pin:
        return None, "pinned"

    target = resolve_ordinal_target(root, ref.path)
    if target is None:
        # Informal label, workflow basename, or a file in another repository.
        return None, "unknown-target"

    if target not in ordinal_cache:
        try:
            lines = (root / target).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return None, "unknown-target"
        line_cache.setdefault(target, lines)
        ordinal_cache[target] = parse_ordinals(lines)

    declared = ordinal_cache[target]
    if not declared:
        # The target numbers nothing — headings like "## D1 — Decision" declare no
        # ordinal. The reference is unverifiable here, not wrong.
        return None, "unnumbered-target"
    if ref.ordinal in declared:
        return None, "checked"

    return (
        Finding(ref, "ORDINAL_MISSING", f"{target} declares no §{ref.ordinal}", target=target),
        "checked",
    )


def classify_referent(ref: Ref, target: str, lines: list[str]) -> Finding | None:
    """Judge a reference that carries a referent, against the target's current text.

    Args:
        ref: The reference. ``ref.referent`` is non-empty.
        target: Repo-relative path of the resolved target.
        lines: The target's current lines.

    Returns:
        ``None`` when the referent is present within the cited coordinate — the claim holds.
        Otherwise the verdict: moved (repairable), ambiguous or absent (both need a human).
    """
    last = min(ref.end or ref.line, len(lines))
    for number in range(ref.line, last + 1):
        if ref.referent in normalize_for_match(lines[number - 1]):
            return None

    matches = [
        number
        for number, text in enumerate(lines, start=1)
        if ref.referent in normalize_for_match(text)
    ]
    here = lines[ref.line - 1].strip()

    if not matches:
        return Finding(
            ref,
            "REFERENT_ABSENT",
            "the referent is nowhere in the target — the cited text was edited, so the "
            "sentence citing it needs re-reading, not a new number",
            target=target,
            target_text=here,
        )
    if len(matches) > 1:
        return Finding(
            ref,
            "REFERENT_AMBIGUOUS",
            f"the referent matches {len(matches)} lines; narrow it or pick one",
            target=target,
            target_text=here,
            candidates=[str(number) for number in matches[:5]],
        )
    return Finding(
        ref,
        "REFERENT_MOVED",
        f"the referent now sits at line {matches[0]} — repairable with --fix",
        target=target,
        target_text=here,
        target_line=matches[0],
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

    # A Markdown link is document-relative (`docs/reviews/x.md` -> `../../.agent/...`
    # names a repo file). Resolving it against the root instead reported valid links as
    # escaping — the document was correct and the gate was not.
    lookup = ref.path
    if ref.md_link and not os.path.isabs(ref.path):
        from_doc = os.path.normpath(
            os.path.join(os.path.dirname(ref.doc), ref.path)
        )
        if not from_doc.startswith("..") and safe_join(root, from_doc) is not None:
            lookup = from_doc

    joined = safe_join(root, lookup)
    if joined is None:
        return Finding(
            ref,
            "ESCAPES_ROOT",
            "points outside the repository — refused a read, and not verifiable here",
        )

    candidates = index.get(lookup, [])
    if joined.is_file():
        candidates = [os.path.normpath(lookup)]

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

    if ref.referent:
        # A confirmed referent SETTLES the coordinate, so DRIFT_SUSPECT is not also emitted
        # even when the target is in this change: the referent is direct evidence, and the
        # warning exists only where the tool has none.
        return classify_referent(ref, target, lines)

    if target in changed:
        return Finding(
            ref,
            "DRIFT_SUSPECT",
            "target is modified by this same change — re-check after the edits are final",
            target=target,
            target_text=lines[ref.line - 1].strip(),
        )
    return None


#: Inside a reference span only: the code-span numbers, or the Markdown-link ones.
_SPAN_NUMBERS = re.compile(r":(?P<line>\d+)(?P<range>-\d+)?")
_SPAN_LINK_NUMBERS = re.compile(r"#L(?P<line>\d+)(?P<range>-L?\d+)?")


def repair_document(root: Path, doc: str, findings: list[Finding]) -> int:
    """Rewrite the line numbers of ``REFERENT_MOVED`` references in one document.

    Args:
        root: Repository root.
        doc: Repo-relative path of the citing document.
        findings: Findings for this document. Only ``REFERENT_MOVED`` is acted on.

    Returns:
        How many references were repaired.

    The write is bounded three ways, and each bound is a test:

    * Only ``REFERENT_MOVED``. ``REFERENT_ABSENT`` and ``REFERENT_AMBIGUOUS`` are the cases
      the tool cannot decide, and repairing them would be guessing.
    * Only inside the reference span. The line is reassembled around that slice, so the
      referent, the prose and every other reference on the line are byte-identical after.
    * Only the number. The referent is the claim and is never machine-written (TASK 103 D4);
      the number is a value derived from it.
    """
    movable = [f for f in findings if f.kind == "REFERENT_MOVED" and f.target_line]
    if not movable:
        return 0

    path = root / doc
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Right-to-left within each line: an earlier rewrite would invalidate later offsets.
    for finding in sorted(movable, key=lambda f: (-f.ref.doc_line, -f.ref.span_start)):
        ref = finding.ref
        delta = finding.target_line - ref.line
        new_line, new_end = ref.line + delta, (ref.end + delta) if ref.end else None
        original = lines[ref.doc_line - 1]
        segment = original[ref.span_start : ref.span_end]
        pattern = _SPAN_LINK_NUMBERS if ref.md_link else _SPAN_NUMBERS
        separator = "#L" if ref.md_link else ":"

        def rewrite(match: re.Match) -> str:
            tail = ""
            if match.group("range"):
                tail = f"-L{new_end}" if ref.md_link else f"-{new_end}"
            return f"{separator}{new_line}{tail}"

        lines[ref.doc_line - 1] = (
            original[: ref.span_start]
            + pattern.sub(rewrite, segment, count=1)
            + original[ref.span_end :]
        )

    path.write_text("\n".join(lines), encoding="utf-8")
    return len(movable)


def collect_docs(root: Path, changed: set[str], scan_all: list[str] | None) -> list[str]:
    """Choose which Markdown documents to inspect.

    Args:
        root: Repository root.
        changed: Paths belonging to the current change.
        scan_all: Paths to scan exhaustively — a directory is walked, a file is taken as
            itself — or ``None`` for diff scope.

    Returns:
        Sorted repo-relative Markdown paths.

    A living corpus is normally a mix: ``docs/PLAN.md docs/TASK.md docs/architectures/``.
    Directories alone cannot express it, and naming the parent instead pulls in the archives,
    whose coordinates are correct records of a past state (§4.2).
    """
    if scan_all is not None:
        docs: set[str] = set()
        for base in scan_all:
            candidate = root / base
            if candidate.is_file():
                if candidate.suffix == ".md":
                    docs.add(str(candidate.relative_to(root)))
                continue
            for path in candidate.rglob("*.md"):
                if path.is_file():
                    docs.add(str(path.relative_to(root)))
        return sorted(docs)
    return sorted(d for d in changed if d.endswith(".md") and (root / d).is_file())


def docs_citing(
    root: Path,
    index: dict[str, list[str]],
    changed: set[str],
    scan_all: list[str] | None,
) -> set[str]:
    """Return documents that CITE a file the current change touched.

    Args:
        root: Repository root.
        index: Suffix index built by :func:`build_suffix_index`.
        changed: Paths belonging to the current change.
        scan_all: Corpus to search, or ``None`` to search every tracked Markdown file.

    Returns:
        Repo-relative Markdown paths citing at least one changed file.

    This is the selection the original tool lacked, and the lack is the defect: diff scope
    returns only documents the change EDITED, so a commit touching sources and no ``.md``
    scans nothing — while being exactly the commit that shifts the lines those documents
    cite. Measured in onchain-analytics: one commit in ``registry.ts`` invalidated 25
    references and no gate opened a single document.
    """
    if not changed:
        return set()

    corpus = collect_docs(root, set(), scan_all if scan_all is not None else ["."])
    citing: set[str] = set()
    for doc in corpus:
        try:
            text = (root / doc).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for ref in extract_refs(doc, text):
            if ref.pin:
                continue
            candidates = index.get(ref.path, [])
            if (root / ref.path).is_file():
                candidates = [os.path.normpath(ref.path)]
            if len(candidates) == 1 and candidates[0] in changed:
                citing.add(doc)
                break
    return citing


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
    pinned_count: int = 0
    #: R7 — the denominator travels with the number. These three partition every resolved,
    #: unpinned reference, and the coverage line prints them separately so a green run cannot
    #: be read as covering references it never examined.
    referent_checked: int = 0
    referent_missing: int = 0
    referent_unresolvable: int = 0
    fixed_count: int = 0
    ordinal_count: int = 0
    ordinal_outcomes: dict[str, int] = field(default_factory=dict)
    ordinal_out_of_scope: int = 0
    notes: list[str] = field(default_factory=list)

    @property
    def total_refs(self) -> int:
        """Return every reference seen, positional and ordinal alike."""
        return self.ref_count + self.ordinal_count

    @property
    def examined_refs(self) -> int:
        """Return references actually checked — pinned ones were deliberately skipped.

        Kept distinct from :attr:`total_refs` so the report never claims to have resolved
        a reference it was told to leave alone.
        """
        return self.total_refs - self.pinned_count - self.ordinal_outcomes.get("pinned", 0)


#: Kinds that say the PATH could not be settled. A reference in this state was never
#: examined for a referent, and counting it as "carries none" would overstate coverage.
_UNRESOLVED_KINDS = {"UNRESOLVABLE", "AMBIGUOUS", "OUT_OF_RANGE", "ESCAPES_ROOT"}


def run(
    root: Path,
    base: str,
    scan_all: list[str] | None,
    targets_changed: bool = False,
    fix: bool = False,
) -> Report:
    """Collect findings for the selected document set.

    Args:
        root: Repository root.
        base: Git revision defining the current change.
        scan_all: Roots to scan exhaustively, or ``None`` for diff scope.
        targets_changed: Select documents CITING a file the change touched, instead of
            documents the change edited. This is the scope that reaches a source-only
            commit — the commit that actually invalidates coordinates.
        fix: Rewrite the line number of every ``REFERENT_MOVED`` reference. Never rewrites
            a referent, and never touches the two verdicts a human must settle.

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
    if targets_changed:
        docs = sorted(set(docs) | docs_citing(root, index, changed, scan_all))
    report.doc_count = len(docs)

    for doc in docs:
        text = (root / doc).read_text(encoding="utf-8", errors="replace")
        doc_findings: list[Finding] = []

        for ref in extract_refs(doc, text):
            report.ref_count += 1
            if ref.pin:
                report.pinned_count += 1
            found = classify(ref, root, index, changed, line_cache)
            if found:
                report.findings.append(found)
                doc_findings.append(found)
            if not ref.pin:
                if found is not None and found.kind in _UNRESOLVED_KINDS:
                    report.referent_unresolvable += 1
                elif ref.referent:
                    report.referent_checked += 1
                else:
                    report.referent_missing += 1

        if fix:
            report.fixed_count += repair_document(root, doc, doc_findings)

        for ref in extract_ordinal_refs(doc, text):
            report.ordinal_count += 1
            found, outcome = classify_ordinal(ref, root, line_cache, ordinal_cache)
            report.ordinal_outcomes[outcome] = report.ordinal_outcomes.get(outcome, 0) + 1
            if found:
                report.findings.append(found)

        report.ordinal_out_of_scope += count_out_of_scope_ordinals(text)

    if report.ordinal_count or report.ordinal_out_of_scope:
        failed = sum(1 for f in report.findings if f.kind == "ORDINAL_MISSING")
        report.notes.append(
            describe_ordinal_scope(report.ordinal_outcomes, failed, report.ordinal_out_of_scope)
        )
    return report


def describe_ordinal_scope(outcomes: dict[str, int], failed: int, out_of_scope: int) -> str:
    """Spell out which ordinals were checked, which failed, and which were never examined.

    A bare count of findings implies every ordinal was checked. Most were not — their
    target is unnamed, unknown, or numbers nothing — and a report that hides that repeats
    the overclaim §4.1 is about. Unrecognised outcome names are printed verbatim rather
    than dropped, so adding an outcome cannot silently shrink the tally.

    Args:
        outcomes: Tally keyed by the outcome names :func:`classify_ordinal` returns.
        failed: How many checked ordinals produced a finding.
        out_of_scope: Ordinal tokens the tool never examined at all.

    Returns:
        A single note line.
    """
    reasons = {
        "unknown-target": "target is not a document in this repository",
        "unnumbered-target": "target declares no numbered sections",
        "pinned": "pinned to a revision",
    }
    checked = outcomes.get("checked", 0)
    parts = [f"{checked} checked ({checked - failed} passed, {failed} failed)"]
    parts += [
        f"{outcomes[key]} skipped ({why})" for key, why in reasons.items() if outcomes.get(key)
    ]
    parts += [
        f"{count} {key}" for key, count in sorted(outcomes.items())
        if key not in reasons and key != "checked" and count
    ]
    if out_of_scope:
        parts.append(f"{out_of_scope} NOT examined (no adjacent target)")
    return "section ordinals — " + ", ".join(parts)


def describe_referent_scope(report: Report) -> str:
    """State how much of the positional corpus was actually verified.

    A finding count alone implies every coordinate was checked. Most carry no referent and
    are unverifiable, so a report omitting that repeats the overclaim §4.1 is about — and
    repeats the second defect the routed record measured: a survey reporting a number
    without the area it searched. The three counts partition every unpinned reference.

    Args:
        report: The run being described.

    Returns:
        A single note line.
    """
    parts = [
        f"{report.referent_checked} with a referent",
        f"{report.referent_missing} without (not examined)",
    ]
    if report.referent_unresolvable:
        parts.append(f"{report.referent_unresolvable} unresolvable")
    if report.pinned_count:
        parts.append(f"{report.pinned_count} pinned")
    if report.fixed_count:
        parts.append(f"{report.fixed_count} repaired by --fix")
    return "path:line — " + ", ".join(parts)


def format_text(report: Report) -> str:
    """Render a report as human-readable text."""
    doc_count, findings = report.doc_count, report.findings
    # Built without mutating the report: format_text must return the same text when called
    # twice, and appending a note here would make the second call differ from the first.
    notes = list(report.notes)
    if report.ref_count:
        notes.append(describe_referent_scope(report))
    suffix = "".join(f"\nnote: {n}" for n in notes)

    if doc_count == 0:
        # Never phrase an empty scope as a pass: "OK" here would be a verification claim
        # about documents nobody looked at — the §4.1 failure in miniature.
        return (
            "NOTHING CHECKED: no Markdown document is in scope. "
            "Nothing was verified." + suffix
        )

    if not findings:
        skipped = report.total_refs - report.examined_refs
        tail = f" ({skipped} pinned, not checked)" if skipped else ""
        return (
            f"OK: {report.examined_refs} of {report.total_refs} reference(s) in "
            f"{doc_count} document(s) resolve against the working tree{tail}." + suffix
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
        f"{len(errors)} error(s), {len(warnings)} warning(s) across {report.total_refs} "
        f"reference(s) ({report.ref_count} path:line + {report.ordinal_count} ordinal) "
        f"in {doc_count} document(s)."
    )
    if warnings:
        lines.append(
            "Warnings are not failures: confirm each line still says what the document "
            "claims, or pin the reference with @<rev>."
        )
    # `notes`, not `report.notes`: the coverage line must print in BOTH branches. Printing it
    # only when nothing was found is the exact overclaim R7 exists against — a run WITH
    # findings is precisely the run whose reader needs to know how much went unexamined.
    for note in notes:
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
    parser.add_argument(
        "--targets-changed",
        action="store_true",
        help=(
            "Select documents citing a file the current change touched, instead of documents "
            "the change edited. This is the scope that catches a source-only commit shifting "
            "lines under a document nobody opened."
        ),
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help=(
            "Rewrite the line number of a REFERENT_MOVED reference. Never rewrites a referent, "
            "and never touches REFERENT_ABSENT or REFERENT_AMBIGUOUS — those need a human."
        ),
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
        report = run(
            root,
            args.base,
            scan_all,
            targets_changed=args.targets_changed,
            fix=args.fix,
        )
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
                    "ordinal_outcomes": report.ordinal_outcomes,
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
