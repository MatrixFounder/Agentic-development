#!/usr/bin/env python3
"""Static lint for the figures of a Markdown document or a `.mmd` file (TASK 108, R6).

Figures. Every `mermaid` fence and every `text figure` fence of a Markdown document (TASK R2.5,
R6.1); a plain `text` fence is a listing and is not linted. A `.mmd` file is one figure.

Each rule carries a probe pair: one or more figures on which it must fire, and a figure on which
it must not. Every run checks the probes first. A rule whose probe fails stops the run with
exit 2, so a dead rule cannot report a clean document.

Thresholds come from `assets/notation.json` only (ARCHITECTURE §10.1). Probes that depend on a
threshold are built from the active notation, so a probe measures its detector, never the value.

Severity. `error` marks a render failure, a silent change of the figure, a construct that mermaid
10.9 cannot render, a hard budget, text below the contrast minimum, or a negative marker that is
broken or stands in a project document. Everything else is `warn`.

Negative fences (TASK R9.4, R6.7). A mermaid fence whose last body line is
`%% negative: <names>` shows a defect on purpose. The names are lint rule ids, lint family names
(FAMILY_PREFIXES) or render check names (`mermaid_model.RENDER_CHECK_NAMES`). The findings of the
named rules and families inside the fence are `expected`: they are reported apart and set no
exit code. Every other finding of the fence counts, so a marker never hides a defect it does
not name. The marker counts only in the skill's references and test fixtures
(`mermaid_model.negative_allowed`); elsewhere MA-NEG-03 reports it and the fence is linted as a
positive figure. MA-NEG-01 reports a negative fence on which none of the named lint checks
fires; MA-NEG-02 reports a malformed marker. All three count.

Language. No rule keys on a natural-language word (ARCHITECTURE invariant L1): caption and legend
are the paragraphs next to the fence; label limits count characters per line; the case rule
applies only to scripts that have case.

Exit codes (TASK D20, ARCHITECTURE §7.4)
  0  no `error` finding outside negative fences
  1  one or more `error` findings outside negative fences, MA-NEG-01, MA-NEG-02 and MA-NEG-03
     included
  2  instrument broken: a failed probe, a rule or the parser failed, notation unreadable
  3  usage error, including an unreadable input path, and `--probe` given with paths

The lint writes no file. Standard library only. Runs in CI.

The lint is a package (TASK 126): `lint_mermaid_parts/` holds one module per section, in this
order, each importing only from the modules above it: `base`, `parse`, `syntax`, `settings`,
`ids`, `budget`, `flowchart`, `state`, `sequence`, `labels`, `classes`, `gantt`,
`ascii_figures`, `doc`, `model`, `negatives` and `engine`. This file imports them in that
order, so `RULES` holds the rules in the order of their sections. It binds every top-level name
of the 17 modules, so a caller imports `lint_mermaid` as before, and it holds the command line,
from `_summary` to `main`. A test that replaces a name that the command line calls patches it
on this module. A name that a module of the package looks up is replaced on that module:
`sys.modules[<function>.__module__]`.
"""

import os
import sys

# Run as a script, the script's own directory leaves `sys.path` before any other import, matched by
# real path and by device and inode, so a module planted beside the script is never imported. No
# `.pyc` is written or read from a `__pycache__/`, and the siblings load by their path (`_load`).
if __name__ == "__main__":
    def _identity(path):
        """`(st_dev, st_ino)` of `path`, or None where it cannot be read or has no inode."""
        try:
            st = os.stat(path)
        except OSError:
            return None
        return (st.st_dev, st.st_ino) if st.st_ino else None

    _DIRS = {os.path.dirname(os.path.abspath(__file__)),
             os.path.dirname(os.path.realpath(__file__))}
    _NAMES = {os.path.normcase(os.path.realpath(path)) for path in _DIRS}
    _IDS = {_identity(path) for path in _DIRS} - {None}
    sys.path[:] = [entry for entry in sys.path
                   if os.path.normcase(os.path.realpath(entry or os.curdir)) not in _NAMES
                   and _identity(entry or os.curdir) not in _IDS]
    sys.dont_write_bytecode = True
    if os.path.isabs(os.devnull):
        sys.pycache_prefix = os.path.join(os.devnull, "lint_mermaid-pycache")
    else:
        sys.pycache_prefix = os.path.join(os.path.realpath(__file__), "pycache")

import argparse
import json
from pathlib import Path
from typing import Optional


def _load(name, package=False):
    """The sibling module or package `name`, loaded by its path beside this file.

    A file planted beside the script under a sibling's name is never chosen. A package loads from
    its `__init__.py`, and the spec gives it its own directory to search for its submodules. A
    module that `sys.modules` holds is reused, so the import statements after the loads search no
    path.
    """
    if name in sys.modules:
        return sys.modules[name]
    import importlib.util
    here = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(here, name, "__init__.py") if package else os.path.join(here, name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        del sys.modules[name]
        raise
    return module


_load("mermaid_model", package=True)
_load("planarity")  # `lint_mermaid_parts.flowchart` imports it by name
_load("lint_mermaid_parts", package=True)
import mermaid_model as mm  # noqa: E402
from lint_mermaid_parts.base import (  # noqa: E402
    EXIT_OK, EXIT_FINDINGS, EXIT_INTERNAL, EXIT_USAGE, Finding, Rule, RULES, FAMILY_PREFIXES,
    LintContext, LintInternalError, rule, ASCII, _doc, _hazard_check, _fig_line, _lines_of)
from lint_mermaid_parts.parse import _check_phantom  # noqa: E402
from lint_mermaid_parts.syntax import (  # noqa: E402
    _unsupported_kinds, _avoid_only_kinds, _kind_probe, _check_kind_floor, _check_kind_avoid,
    _check_unknown)
from lint_mermaid_parts.settings import (  # noqa: E402
    _check_directive, _check_frontmatter, _theme_pattern, _check_sanitizer, _check_toplevel_font,
    _check_theme, _SETTINGS_KEY, _notation_settings, _settings_probe, _no_themecss_probe,
    _PINNED_SETTINGS, _QUOTED_SETTING_MAX, _check_pinned, _settings_signature,
    _check_settings_consistency)
from lint_mermaid_parts.ids import _check_edge_ids, _figure_ids, _check_id_shape  # noqa: E402
from lint_mermaid_parts.budget import (  # noqa: E402
    _COUNT_BUDGETS, _budget_values, _budget_findings, _chain, _budget_probe, _check_soft_budget,
    _check_hard_budget)
from lint_mermaid_parts.flowchart import (  # noqa: E402
    _visible_edges, _decision_flow, _edge_directions, _check_duplicate_edges, _check_subgraph_edge,
    _check_small_subgraph, _NUMBERED, _numbered_probe, _check_numbered, _check_planarity, _lr_probe,
    _check_lr)
from lint_mermaid_parts.state import (  # noqa: E402
    _check_composite_cross, _state_end, _check_duplicate_transitions)
from lint_mermaid_parts.sequence import _skip_probe, _check_skip, _phase_probe  # noqa: E402
from lint_mermaid_parts.labels import (  # noqa: E402
    _label_probe, _lines_probe, _node_label_items, _edge_label_items, _check_node_line1,
    _check_node_line2, _check_edge_label, _check_message, _check_note, _check_gantt_label, _LETTERS,
    _drawn_names, _starts_uppercase, _check_edge_case, _check_node_lines, _check_message_lines,
    _check_participant, _check_note_lines, _check_edge_lines, _check_participant_lines,
    _html_label_items, _SMALL_TAG, _escaped, _check_small)
from lint_mermaid_parts.classes import (  # noqa: E402
    _HEX, _FUNC_COLOUR, _CSS_NAMED, _channel, _hsl_to_rgb, _rgba, _over, _luminance, contrast_ratio,
    _style_contrast, _style_blocks, _check_contrast, _class_uses, _class_defs,
    _check_undefined_class, _check_unused_class, _theme_text_contrasts, _check_fill_without_color)
from lint_mermaid_parts.gantt import (  # noqa: E402
    _GANTT_HEAD, _check_after, _check_dotted_after, _check_repeated_section, _check_axis,
    _check_today, _check_bare_duration)
from lint_mermaid_parts.ascii_figures import (  # noqa: E402
    _check_tabs, _check_wide, _width_probe, _check_width, _check_ragged, _ascii_probe,
    _ascii_elements, _check_ascii_budget, _check_ascii_hard_budget, _check_connector_drift)
from lint_mermaid_parts.doc import (  # noqa: E402
    _in_document, _legend_reasons, _check_caption, _check_caption_below, _encodings,
    _legend_encodings, _TWO_CLASSES, _check_legend, _check_class_consistency,
    _check_alias_consistency)
from lint_mermaid_parts.model import _check_unread  # noqa: E402
from lint_mermaid_parts.negatives import (  # noqa: E402
    _marker, _is_negative, _named_rule_ids, _inside, _nameable_rules, classify_marker_name,
    _fires_on, _NEG_NAMES_HINT, _check_negative_fires, _check_marker_shape, _check_marker_ignored)
from lint_mermaid_parts.engine import (  # noqa: E402
    _figure_at, _rule_results, lint_figures, lint_text, _probe_text, run_probes, _NUMBER,
    _rows_numbers, inventory, inventoried, counts)

#: Every top-level name of the package's modules and of the command line: what a
#: caller reads from this file. An editor then reads the imports above as re-exports.
__all__ = [
    "EXIT_OK", "EXIT_FINDINGS", "EXIT_INTERNAL", "EXIT_USAGE", "Finding", "Rule", "RULES",
    "FAMILY_PREFIXES", "LintContext", "LintInternalError", "rule", "ASCII", "_doc", "_hazard_check",
    "_fig_line", "_lines_of", "_check_phantom", "_unsupported_kinds", "_avoid_only_kinds",
    "_kind_probe", "_check_kind_floor", "_check_kind_avoid", "_check_unknown", "_check_directive",
    "_check_frontmatter", "_theme_pattern", "_check_sanitizer", "_check_toplevel_font",
    "_check_theme", "_SETTINGS_KEY", "_notation_settings", "_settings_probe", "_no_themecss_probe",
    "_PINNED_SETTINGS", "_QUOTED_SETTING_MAX", "_check_pinned", "_settings_signature",
    "_check_settings_consistency", "_check_edge_ids", "_figure_ids", "_check_id_shape",
    "_COUNT_BUDGETS", "_budget_values", "_budget_findings", "_chain", "_budget_probe",
    "_check_soft_budget", "_check_hard_budget", "_visible_edges", "_decision_flow",
    "_edge_directions", "_check_duplicate_edges", "_check_subgraph_edge", "_check_small_subgraph",
    "_NUMBERED", "_numbered_probe", "_check_numbered", "_check_planarity", "_lr_probe", "_check_lr",
    "_check_composite_cross", "_state_end", "_check_duplicate_transitions", "_skip_probe",
    "_check_skip", "_phase_probe", "_label_probe", "_lines_probe", "_node_label_items",
    "_edge_label_items", "_check_node_line1", "_check_node_line2", "_check_edge_label",
    "_check_message", "_check_note", "_check_gantt_label", "_LETTERS", "_drawn_names",
    "_starts_uppercase", "_check_edge_case", "_check_node_lines", "_check_message_lines",
    "_check_participant", "_check_note_lines", "_check_edge_lines", "_check_participant_lines",
    "_html_label_items", "_SMALL_TAG", "_escaped", "_check_small", "_HEX", "_FUNC_COLOUR",
    "_CSS_NAMED", "_channel", "_hsl_to_rgb", "_rgba", "_over", "_luminance", "contrast_ratio",
    "_style_contrast", "_style_blocks", "_check_contrast", "_class_uses", "_class_defs",
    "_check_undefined_class", "_check_unused_class", "_theme_text_contrasts",
    "_check_fill_without_color", "_GANTT_HEAD", "_check_after", "_check_dotted_after",
    "_check_repeated_section", "_check_axis", "_check_today", "_check_bare_duration", "_check_tabs",
    "_check_wide", "_width_probe", "_check_width", "_check_ragged", "_ascii_probe",
    "_ascii_elements", "_check_ascii_budget", "_check_ascii_hard_budget", "_check_connector_drift",
    "_in_document", "_legend_reasons", "_check_caption", "_check_caption_below", "_encodings",
    "_legend_encodings", "_TWO_CLASSES", "_check_legend", "_check_class_consistency",
    "_check_alias_consistency", "_check_unread", "_marker", "_is_negative", "_named_rule_ids",
    "_inside", "_nameable_rules", "classify_marker_name", "_fires_on", "_NEG_NAMES_HINT",
    "_check_negative_fires", "_check_marker_shape", "_check_marker_ignored", "_figure_at",
    "_rule_results", "lint_figures", "lint_text", "_probe_text", "run_probes", "_NUMBER",
    "_rows_numbers", "inventory", "inventoried", "counts", "_summary", "_json_text", "_shown",
    "_say", "_finding_line", "_finding_dict", "_format_text", "_cell", "_format_inventory",
    "build_parser", "main",
]


def _summary(c: dict) -> str:
    return f"{c['error']} error / {c['warn']} warn / {c['expected']} expected"


def _json_text(value, **kw) -> str:
    """`json.dumps(value, ensure_ascii=False, **kw)` with each character that `str.isprintable()`
    refuses, a newline aside, written as a JSON escape. A copy of `json_text` of render_check.py,
    which the lint does not import: the lint's allow rule would then run render_check.py and
    svg_geometry.py (TASK 123 R3.1, D7). A test pins the two to one output."""
    out = []
    for ch in json.dumps(value, ensure_ascii=False, **kw):
        if ch.isprintable() or ch == "\n":
            out.append(ch)
            continue
        code = ord(ch)
        if code > 0xFFFF:
            code -= 0x10000
            out.append("\\u%04x\\u%04x" % (0xD800 + (code >> 10), 0xDC00 + (code & 0x3FF)))
        else:
            out.append("\\u%04x" % code)
    return "".join(out)


def _shown(text: str, lines: bool = False) -> str:
    """*text* as the lint prints it: each character that `str.isprintable()` refuses, a newline
    among them, written as its Python escape. With *lines*, a newline stays: the text is JSON from
    `_json_text`, or lines that `_format_text` or `_format_inventory` escaped one by one. A
    backslash stays single (TASK 122 D5). A copy of `_shown` of render_check.py (TASK 123 R3.1); a
    test pins the two to one output."""
    return "".join(ch if ch.isprintable() or (lines and ch == "\n") else ascii(ch)[1:-1]
                   for ch in text)


def _say(text: str, file=None, lines: bool = False) -> None:
    """Print *text* through `_shown`: the only `print` of the lint (TASK 123 R3.2)."""
    print(_shown(text, lines), file=file)


def _finding_line(f: Finding) -> str:
    fence = f" [fence {f.fence}]" if f.fence else ""
    return f"{f.path}:{f.line}: {f.severity} {f.rule}{fence} {f.message}"


def _finding_dict(f: Finding) -> dict:
    return {"rule": f.rule, "severity": f.severity, "path": f.path, "line": f.line, "fence": f.fence,
            "message": f.message, "hint": f.hint}


def _format_text(findings: list, paths: Optional[list] = None) -> str:
    """One line per finding with the line of its fence and the rule's hint after `→` (TASK
    R6.4), the expected findings of negative fences apart, a count line per file when there are
    several, and the total."""
    out = []
    for f in findings:
        if not f.expected:
            out.append(_finding_line(f) + (f" → {f.hint}" if f.hint else ""))
    expected = [f for f in findings if f.expected]
    if expected:
        out.append("expected on negative fences (not counted):")
        out += [_finding_line(f) for f in expected]
    if paths and len(paths) > 1:
        out += [f"{p}: {_summary(counts([f for f in findings if f.path == p]))}" for p in paths]
    out.append(_summary(counts(findings)))
    return "\n".join(_shown(line) for line in out)


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _format_inventory(blocks: list) -> str:
    out = []
    for block in blocks:
        if not block["inventoried"]:
            out.append(f"{block['path']}:{block['figure_line']} {block['figure_kind']} — not inventoried: "
                       f"{block['figure_kind']}; list its elements from the source")
            out.append("")
            continue
        out.append(f"{block['path']}:{block['figure_line']} {block['figure_kind']} — {len(block['rows'])} rows")
        out.append("| kind | id | text | line | support |")
        out.append("| :--- | :--- | :--- | :--- | :--- |")
        for r in block["rows"]:
            out.append(f"| {_cell(r['kind'])} | {_cell(r['id'])} | {_cell(r['text'])} | {r['line']} |  |")
        out.append("")
    return "\n".join(_shown(line) for line in out)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="lint_mermaid.py",
                                description="Static lint for Mermaid and ASCII figures.")
    p.add_argument("paths", nargs="*", help="Markdown (.md) or Mermaid (.mmd) files")
    p.add_argument("--json", action="store_true", help="print findings as JSON")
    p.add_argument("--inventory", action="store_true",
                   help="print the element inventory of every figure instead of findings")
    p.add_argument("--probe", action="store_true",
                   help="check every rule's probe pair and exit (0 all live, 2 a dead rule); takes no "
                        "paths")
    return p


def main(argv: Optional[list] = None, notation_path: Optional[Path] = None) -> int:
    """The CLI. *notation_path* replaces `assets/notation.json` for a test; no option reaches it,
    so the auto-approved command line cannot lint against relaxed thresholds."""
    p = build_parser()
    try:
        args = p.parse_args(argv)
    except SystemExit as exc:
        return EXIT_USAGE if exc.code else EXIT_OK
    if not args.paths and not args.probe:
        p.print_usage(sys.stderr)
        return EXIT_USAGE
    if args.probe and (args.paths or args.json or args.inventory):
        # a CI line `--probe docs/*.md` would otherwise pass without linting a file
        _say("usage error: --probe takes no paths and no other option; run the lint without --probe",
             file=sys.stderr)
        return EXIT_USAGE
    try:
        notation = mm.load_notation(notation_path)
    except (OSError, ValueError) as exc:
        _say(f"internal error: notation unreadable: {exc}", file=sys.stderr)
        return EXIT_INTERNAL
    dead = run_probes(notation=notation)
    if dead:
        _say(f"dead rule(s): {', '.join(dead)} — a probe pair failed; the lint reports nothing",
             file=sys.stderr)
        return EXIT_INTERNAL
    if args.probe:
        _say(f"{len(RULES)}/{len(RULES)} rules live")
        return EXIT_OK
    texts = []
    for raw in args.paths:
        path = Path(raw)
        try:
            texts.append((raw, path.read_text(encoding="utf-8"), path.suffix.lower() == ".mmd"))
        except (OSError, UnicodeDecodeError) as exc:
            _say(f"usage error: cannot read {raw}: {exc}", file=sys.stderr)
            return EXIT_USAGE
    try:
        if args.inventory:
            blocks = []
            for raw, text, is_mmd in texts:
                figures = [mm.parse_figure(mm.figure_from_mmd(text))] if is_mmd else mm.parse_document(text)
                for fig in figures:
                    broken = next((e for e in fig.parse_errors if e.get("internal")), None)
                    if broken is not None:
                        # an inventory the parser failed to read is no inventory (TASK D20)
                        raise LintInternalError(f"{raw}:{broken['line']}: {broken['message']}")
                    blocks.append({"path": raw, "figure_line": fig.fence.start, "figure_kind": fig.kind,
                                   "inventoried": inventoried(fig), "rows": inventory(fig)})
            if args.json:
                _say(_json_text({"schema": "mermaid-inventory/v1", "figures": blocks}, indent=2), lines=True)
            else:
                _say(_format_inventory(blocks), lines=True)
            return EXIT_OK
        findings = []
        for raw, text, is_mmd in texts:
            findings.extend(lint_text(text, raw, is_mmd=is_mmd, notation=notation))
    except LintInternalError as exc:
        _say(f"internal error: {exc}", file=sys.stderr)
        return EXIT_INTERNAL
    paths = [raw for raw, _t, _m in texts]
    total = counts(findings)
    if args.json:
        _say(_json_text({
            "schema": "mermaid-lint/v1",
            "files": paths,
            "rules": len(RULES),
            "counts": total,
            "per_file": {p: counts([f for f in findings if f.path == p]) for p in paths},
            "findings": [_finding_dict(f) for f in findings if not f.expected],
            "expected": [_finding_dict(f) for f in findings if f.expected],
        }, indent=2), lines=True)
    else:
        _say(_format_text(findings, paths), lines=True)
    return EXIT_FINDINGS if total["error"] else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
