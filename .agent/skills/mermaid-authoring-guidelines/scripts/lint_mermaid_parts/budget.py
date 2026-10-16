"""BUDGET rules of the figure lint: the soft and hard size budgets of a figure (TASK 126)."""

from __future__ import annotations

from typing import Callable

from .base import rule, _doc, _fig_line


#: Budget key of notation.json per kind that the model counts in `Figure.counts`.
_COUNT_BUDGETS = {"class": "class", "mindmap": "mindmap", "timeline": "timeline", "journey": "journey",
                  "gitGraph": "gitgraph"}


def _budget_values(fig) -> list:
    """(kind key, metric, value) for the budgets of notation.json."""
    counts = getattr(fig, "counts", None)
    if counts and fig.kind in _COUNT_BUDGETS:
        return [(_COUNT_BUDGETS[fig.kind], metric, value) for metric, value in counts.items()]
    if fig.flowchart:
        fc = fig.flowchart
        return [("flowchart", "nodes", len(fc.nodes)),
                ("flowchart", "edges", sum(1 for e in fc.edges if e.style != "invisible"))]
    if fig.sequence:
        seq = fig.sequence
        return [("sequence", "participants", len(seq.participants)),
                ("sequence", "messages", len(seq.messages)),
                ("sequence", "phase_blocks", sum(1 for b in seq.blocks if b.kind == "rect"))]
    if fig.state:
        return [("state", "states", len(fig.state.states))]
    if fig.gantt:
        return [("gantt", "bars", sum(1 for t in fig.gantt.tasks if "vert" not in t.tags))]
    if fig.er:
        return [("er", "entities", len(fig.er.entities))]
    return []


def _budget_findings(fig, ctx, hard: bool) -> list:
    out = []
    budgets = ctx.notation.get("budgets", {})
    for kind, metric, value in _budget_values(fig):
        pair = budgets.get(kind, {}).get(metric)
        if not pair:
            continue
        soft, hard_limit = pair
        if hard and value > hard_limit:
            out.append((_fig_line(fig), f"{metric}: {value} > hard budget {hard_limit}; split the figure"))
        elif not hard and soft < value <= hard_limit:
            out.append((_fig_line(fig), f"{metric}: {value} > soft budget {soft}; aggregate or split"))
    return out


def _chain(n: int, direction: str = "TB") -> str:
    lines = [f"flowchart {direction}"]
    lines += [f"  N{k} --> N{k + 1}" for k in range(1, n)]
    return "\n".join(lines)


def _budget_probe(which: str) -> Callable:
    def make(notation):
        soft, hard = notation["budgets"]["flowchart"]["nodes"]
        n = {"soft-fire": soft + 1, "soft-quiet": soft, "hard-fire": hard + 1, "hard-quiet": hard}[which]
        return _doc(_chain(n))
    return make


@rule("MA-BUDGET-01", "warn", "Over the soft budget",
      "Aggregate (one node for a group, members on its second line) or split; keep the figure only "
      "if it passes the render check.",
      _budget_probe("soft-fire"), _budget_probe("soft-quiet"))
def _check_soft_budget(fig, ctx):
    return _budget_findings(fig, ctx, hard=False)


@rule("MA-BUDGET-02", "error", "Over the hard budget",
      "Split the figure by concern.",
      _budget_probe("hard-fire"), _budget_probe("hard-quiet"))
def _check_hard_budget(fig, ctx):
    return _budget_findings(fig, ctx, hard=True)


