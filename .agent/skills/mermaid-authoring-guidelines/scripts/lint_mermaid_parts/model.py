"""MODEL rule of the figure lint: a statement that the parser could not read (TASK 126)."""

from __future__ import annotations

from .base import rule, _doc


@rule("MA-MODEL-01", "warn", "Statement the lint's parser could not read",
      "Check the statement against the kind's reference; the render check decides whether it renders.",
      _doc("flowchart TB\n  A --> B )("),
      _doc("flowchart TB\n  A --> B"))
def _check_unread(fig, ctx):
    return [(e["line"], e["message"]) for e in fig.parse_errors if not e.get("internal")]


