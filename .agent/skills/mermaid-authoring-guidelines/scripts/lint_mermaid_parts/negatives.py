"""NEG rules of the figure lint: negative-fence markers (TASK 126)."""

from __future__ import annotations

import mermaid_model as mm

from .base import RULES, FAMILY_PREFIXES, rule, _doc


def _marker(fig, ctx):
    """The marker that makes *fig* negative, or None: a fence's last-line marker in a document
    where markers count. Read once per figure per run."""
    key = id(fig)
    if key not in ctx.markers:
        ctx.markers[key] = fig.fence.negative if ctx.honours_markers() else None
    return ctx.markers[key]


def _is_negative(fig, ctx) -> bool:
    return _marker(fig, ctx) is not None


def _named_rule_ids(fig, ctx) -> set:
    """The ids of the rules the marker of a negative *fig* names, by id or by family."""
    marker = _marker(fig, ctx)
    out = set()
    for name in (marker.names if marker is not None else []):
        kind = classify_marker_name(name)
        out.update(r.id for r in (kind[1] if kind else []))
    return out


def _inside(fig, line: int) -> bool:
    return fig.fence.start <= line <= fig.fence.end


def _nameable_rules() -> list:
    """The rules a negative marker may name: every rule but the marker rules themselves."""
    return [r for r in RULES if r.scope != "marker"]


def classify_marker_name(name: str):
    """Return `("rule", [rule])`, `("family", [rules])`, `("render", [])` or None for one name of
    a negative marker. Rule ids and family names compare without case."""
    rules = _nameable_rules()
    upper = name.upper()
    by_id = [r for r in rules if r.id == upper]
    if by_id:
        return "rule", by_id
    key = name.lower()
    key = key[3:] if key.startswith("ma-") else key
    prefix = FAMILY_PREFIXES.get(key)
    if prefix:
        return "family", [r for r in rules if r.id.startswith(prefix)]
    if name in mm.RENDER_CHECK_NAMES:
        return "render", []
    return None


def _fires_on(r, fig, figures: list, ctx) -> bool:
    """True when rule *r* reports a finding inside the negative figure *fig*."""
    if r.scope == "figure":
        return bool(r.check(fig, ctx))
    positives = [f for f in figures if not _is_negative(f, ctx)]
    return any(_inside(fig, line) for line, _message in r.check(positives + [fig], ctx))


_NEG_NAMES_HINT = ("Name lint rule ids (MA-FLOW-01), lint families ("
                   + ", ".join(FAMILY_PREFIXES) + ") or render checks ("
                   + ", ".join(mm.RENDER_CHECK_NAMES) + "), comma-separated, in "
                   "`%% negative: <names>` as the last body line of the fence.")


@rule("MA-NEG-01", "error", "Negative fence on which none of the named lint checks fires",
      "The example no longer shows its defect: restore the defect, or name the checks it fails.",
      _doc("flowchart TB\n  A --> B\n  %% negative: MA-FLOW-01"),
      _doc("flowchart TB\n  A --> B\n  B --> A\n  %% negative: MA-FLOW-01"),
      scope="marker")
def _check_negative_fires(figures, ctx):
    out = []
    for fig in figures:
        marker = _marker(fig, ctx)
        if marker is None:
            continue
        named, seen = [], set()
        for name in marker.names:
            kind = classify_marker_name(name)
            for r in (kind[1] if kind else []):
                if r.id not in seen:
                    seen.add(r.id)
                    named.append(r)
        if named and not any(_fires_on(r, fig, figures, ctx) for r in named):
            out.append((marker.line, "none of " + ", ".join(r.id for r in named[:8])
                        + (" …" if len(named) > 8 else "") + " fires on this negative fence"))
    return out


@rule("MA-NEG-02", "error", "Negative marker that names nothing, names an unknown check, or is not "
      "the last body line", _NEG_NAMES_HINT,
      _doc("flowchart TB\n  A --> B\n  B --> A\n  %% negative: MA-FLOW-99"),
      _doc("flowchart TB\n  A --> B\n  B --> A\n  %% negative: MA-FLOW-01, crossings"),
      scope="marker")
def _check_marker_shape(figures, ctx):
    if not ctx.honours_markers():
        return []  # MA-NEG-03 reports every marker of such a document
    out = []
    for fig in figures:
        for marker in fig.fence.markers:
            if not marker.last:
                out.append((marker.line, "the marker is not the last body line, so the fence is "
                                         "linted as a positive figure"))
                continue
            if not marker.names:
                out.append((marker.line, "the marker names no check"))
            for name in marker.names:
                if classify_marker_name(name) is None:
                    out.append((marker.line, f"`{name}` is not a lint rule id, a lint family or a "
                                             "render check"))
    return out


@rule("MA-NEG-03", "error", "Negative marker outside the skill's references and test fixtures",
      "Remove the `%% negative:` line: only the skill's references and test fixtures show a defect "
      "on purpose. Here the fence is linted as a positive figure, and each of its findings counts.",
      _doc("flowchart TB\n  A --> B\n  B --> A\n  %% negative: MA-FLOW-01"),
      _doc("flowchart TB\n  A --> B"),
      scope="marker", probe_negative=False)
def _check_marker_ignored(figures, ctx):
    if ctx.honours_markers():
        return []
    return [(marker.line, "the marker is ignored: it counts only in the skill's references/ and "
                          "scripts/tests/fixtures/")
            for fig in figures for marker in fig.fence.markers]


