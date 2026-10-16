"""Engine of the figure lint: the rules run over figures and documents, the probes, the
inventory and the counts. The command line stays in `lint_mermaid.py` (TASK 126).

`RULES` holds the rules of the modules imported so far. Imported alone, this module
sees only some of them, so callers import `lint_mermaid`, which imports every module
in order."""

from __future__ import annotations

import re
from typing import Optional

import mermaid_model as mm

from .base import Finding, RULES, LintContext, LintInternalError, _lines_of
from .negatives import _is_negative, _named_rule_ids, _inside


def _figure_at(line: int, figures: list):
    """The figure whose fence holds *line*; None when no fence does."""
    return next((fig for fig in figures if _inside(fig, line)), None)


def _rule_results(r, figures: list, ctx) -> list:
    """`(figure, line, message)` of one rule over the figures of one document.

    A document rule compares the positive figures among themselves, then each negative figure
    against them; a finding of the second pass counts only inside that negative figure. So a
    negative example never moves a finding onto a positive figure."""
    out = []
    if r.scope == "figure":
        for fig in figures:
            out += [(fig, line, message) for line, message in r.check(fig, ctx)]
    elif r.scope == "document":
        positives = [f for f in figures if not _is_negative(f, ctx)]
        out += [(_figure_at(line, positives), line, message) for line, message in r.check(positives, ctx)]
        for neg in figures:
            if _is_negative(neg, ctx):
                out += [(neg, line, message) for line, message in r.check(positives + [neg], ctx)
                        if _inside(neg, line)]
    else:
        out += [(_figure_at(line, figures), line, message) for line, message in r.check(figures, ctx)]
    return out


def lint_figures(figures: list, ctx: LintContext, rules: Optional[list] = None) -> list:
    """Apply *rules* (default: RULES) to parsed figures and return Findings sorted by line.

    Every finding carries the line of its fence. A finding inside a negative fence is marked
    `expected` when its rule is one the marker names, by id or by family; the other findings of
    the fence count, and so do the findings of the marker rules (MA-NEG).
    Raises LintInternalError when the parser or a rule failed (exit 2 at the CLI)."""
    rules = RULES if rules is None else rules
    for fig in figures:
        for err in fig.parse_errors:
            if err.get("internal"):
                raise LintInternalError(f"{ctx.path}:{err['line']}: {err['message']}")
    named = {id(fig): _named_rule_ids(fig, ctx) for fig in figures}
    findings = []
    for r in rules:
        try:
            results = _rule_results(r, figures, ctx)
        except Exception as exc:  # noqa: BLE001 — a failing rule is a broken instrument
            raise LintInternalError(f"rule {r.id} failed on {ctx.path}: {exc!r}") from exc
        for fig, line, message in results:
            expected = r.scope != "marker" and fig is not None and r.id in named.get(id(fig), ())
            findings.append(Finding(rule=r.id, severity=r.severity, path=ctx.path, line=int(line),
                                    message=str(message), hint=r.hint,
                                    fence=fig.fence.start if fig is not None else 0, expected=expected))
    order = {r.id: k for k, r in enumerate(rules)}
    findings.sort(key=lambda f: (f.line, order.get(f.rule, 0)))
    return findings


def lint_text(text: str, path: str = "<text>", is_mmd: bool = False,
              notation: Optional[dict] = None, rules: Optional[list] = None,
              langs: tuple = mm.FIGURE_LANGS, negative: Optional[bool] = None) -> list:
    """Parse *text* and lint it. The entry point the eval grader calls.

    *langs* selects the fences that are figures (`mermaid_model.FIGURE_LANGS`: `mermaid` and
    `text figure`). A caller that reads every `text` fence as an ASCII figure passes
    `("mermaid", "text")`. *negative* says whether `%% negative:` markers count; None decides by
    *path* (`mermaid_model.negative_allowed`). The returned list holds the expected findings too;
    filter on `Finding.expected`."""
    notation = notation if notation is not None else mm.load_notation()
    figures = [mm.parse_figure(mm.figure_from_mmd(text))] if is_mmd else mm.parse_document(text, langs)
    return lint_figures(figures, LintContext(notation=notation, path=path, is_mmd=is_mmd,
                                             negative=negative), rules)


def _probe_text(probe, notation: dict) -> str:
    return probe(notation) if callable(probe) else probe


def run_probes(rules: Optional[list] = None, notation: Optional[dict] = None) -> list:
    """Return the ids of rules whose probe pair fails. An empty list means every rule is live.

    A rule with several fire probes is live only when each of them fires: one detector of the
    rule that dies cannot hide behind another."""
    notation = notation if notation is not None else mm.load_notation()
    dead = []
    for r in (RULES if rules is None else rules):
        fires = r.probe_fire if isinstance(r.probe_fire, (tuple, list)) else (r.probe_fire,)
        try:
            fired = [lint_text(_probe_text(p, notation), "<probe>", notation=notation, rules=[r],
                               negative=r.probe_negative) for p in fires]
            quiet = lint_text(_probe_text(r.probe_quiet, notation), "<probe>", notation=notation,
                              rules=[r], negative=r.probe_negative)
        except Exception:  # noqa: BLE001 — a probe that crashes is a dead rule
            dead.append(r.id)
            continue
        if not fires or not all(fired) or quiet:
            dead.append(r.id)
    return dead


_NUMBER = re.compile(r"\d+(?:[.,]\d+)*%?")


def _rows_numbers(rows: list, owner: str, text: str, line: int) -> None:
    for num in _NUMBER.findall(text or ""):
        rows.append({"kind": "number", "id": owner, "text": num, "line": line, "support": ""})


def inventory(figure) -> list:
    """Return one row per element of *figure*: node, edge, label, note, number, group, message,
    transition or task. Row keys: `kind`, `id`, `text`, `line`, `support` (always "")."""
    rows: list = []

    def add(kind, ident, text, line):
        rows.append({"kind": kind, "id": str(ident), "text": text, "line": line, "support": ""})
        _rows_numbers(rows, str(ident), text if kind not in ("edge", "message", "transition") else "", line)

    fig = figure
    if fig.flowchart:
        fc = fig.flowchart
        for sg in fc.subgraphs.values():
            add("group", sg.id, " / ".join(_lines_of(sg.title, sg.id)), sg.line)
        for n in fc.nodes.values():
            add("node", n.id, " / ".join(_lines_of(n.label, n.id)), n.line)
        for k, e in enumerate(fc.edges):
            if e.style == "invisible":
                continue
            sym = {"<->": "<->", "->": "->", "none": "--"}[e.arrow]
            rows.append({"kind": "edge", "id": f"e{k}", "text": f"{e.src} {sym} {e.dst}", "line": e.line,
                         "support": ""})
            if e.label:
                add("label", f"e{k}", " / ".join(mm.label_lines(e.label)), e.line)
    if fig.sequence:
        seq = fig.sequence
        for p in seq.participants:
            add("node", p.id, p.label or p.id, p.line)
        for b in seq.blocks:
            add("group", b.kind, b.label, b.start)
        for k, m in enumerate(seq.messages):
            text = " / ".join(mm.label_lines(m.text))
            rows.append({"kind": "message", "id": f"m{k}", "text": f"{m.src} {m.arrow} {m.dst}: {text}",
                         "line": m.line, "support": ""})
            _rows_numbers(rows, f"m{k}", text, m.line)
        for k, n in enumerate(seq.notes):
            add("note", f"n{k}", " / ".join(mm.label_lines(n.text)), n.line)
    if fig.state:
        sd = fig.state
        for s in sd.states.values():
            if s.composite:
                add("group", s.id, " / ".join(_lines_of(s.label, s.id)), s.line)
            else:
                add("node", s.id, " / ".join(_lines_of(s.label, s.id)), s.line)
        for k, t in enumerate(sd.transitions):
            label = " / ".join(mm.label_lines(t.label))
            rows.append({"kind": "transition", "id": f"t{k}",
                         "text": f"{t.src} -> {t.dst}" + (f": {label}" if label else ""), "line": t.line,
                         "support": ""})
            _rows_numbers(rows, f"t{k}", label, t.line)
        for k, n in enumerate(sd.notes):
            add("note", f"n{k}", " / ".join(mm.label_lines(n.text)), n.line)
    if fig.gantt:
        g = fig.gantt
        for name, line in zip(g.sections, g.section_lines or [fig.fence.start] * len(g.sections)):
            add("group", name, name, line)
        for k, t in enumerate(g.tasks):
            add("task", t.id or f"task{k + 1}", t.label, t.line)
    if fig.er:
        for ent in fig.er.entities.values():
            add("node", ent.name, ent.alias or ent.name, ent.line)
            for text, line in zip(ent.attributes, ent.attribute_lines or [ent.line] * len(ent.attributes)):
                add("label", ent.name, text, line)
        for k, r in enumerate(fig.er.relations):
            rows.append({"kind": "edge", "id": f"r{k}", "text": f"{r.a} {r.cardinality} {r.b}", "line": r.line,
                         "support": ""})
            if r.label:
                add("label", f"r{k}", r.label, r.line)
    if fig.ascii:
        for k, (line, text) in enumerate(fig.ascii.elements):
            add("node", f"a{k}", text, line)
    for kind, ident, text, line in getattr(fig, "items", []):
        if kind in ("edge", "number"):
            rows.append({"kind": kind, "id": str(ident), "text": text, "line": line, "support": ""})
        else:
            add(kind, ident, text, line)
    rows.sort(key=lambda r: r["line"])
    return rows


def inventoried(figure) -> bool:
    """True when `inventory` reads the elements of the figure's kind. For any other kind an
    empty table would read as a figure with no elements, so the output says so instead."""
    return (figure.kind in ("flowchart", "sequence", "state", "gantt", "er", "ascii")
            or figure.kind in mm.ITEM_KINDS)


def counts(findings: list) -> dict:
    """`error` and `warn` count the findings outside negative fences; `expected` the rest."""
    return {"error": sum(1 for f in findings if f.severity == "error" and not f.expected),
            "warn": sum(1 for f in findings if f.severity == "warn" and not f.expected),
            "expected": sum(1 for f in findings if f.expected)}
