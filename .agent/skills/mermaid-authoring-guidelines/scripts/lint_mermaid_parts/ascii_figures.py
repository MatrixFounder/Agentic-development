"""ASCII rules of the figure lint: `text figure` fences (TASK 126)."""

from __future__ import annotations

from typing import Callable

from .base import rule, ASCII, _doc, _fig_line


@rule("MA-ASCII-01", "error", "Tab in an ASCII figure",
      "Replace tabs with spaces; viewers expand tabs to different widths.",
      _doc("a\t-> b", ASCII), _doc("a  -> b", ASCII))
def _check_tabs(fig, ctx):
    return [(line, "tab character") for line in fig.ascii.tabs] if fig.ascii else []


@rule("MA-ASCII-02", "warn", "Double-width character on an aligned line",
      "Use single-width characters inside boxes and trees; an emoji or CJK character shifts the border.",
      _doc("+--------+\n| 名前 |\n+--------+", ASCII),
      _doc("+--------+\n| name   |\n+--------+", ASCII))
def _check_wide(fig, ctx):
    if fig.ascii is None:
        return []
    aligned = set(fig.ascii.aligned)
    return [(line, "double-width character on a line with borders") for line in fig.ascii.wide if line in aligned]


def _width_probe(fire: bool) -> Callable:
    def make(notation):
        n = int(notation["ascii"]["max_columns"]) + (1 if fire else 0)
        return _doc("a" * n, ASCII)
    return make


@rule("MA-ASCII-03", "warn", "Line wider than the ASCII column limit",
      "Shorten or wrap the line; terminals and diff views cut it.",
      _width_probe(True), _width_probe(False))
def _check_width(fig, ctx):
    if fig.ascii is None:
        return []
    limit = int(ctx.notation["ascii"]["max_columns"])
    return [(line, f"{width} columns > {limit}")
            for (line, _text), width in zip(fig.ascii.lines, fig.ascii.widths) if width > limit]


@rule("MA-ASCII-04", "warn", "Box side or corner off its column",
      "Move the side or the corner to the column of the box's top corners; pad every line of the "
      "box to the top-right corner.",
      (_doc("+------+\n| api |\n+------+", ASCII), _doc("+------+\n| api  |\n | db  |\n+------+", ASCII),
       _doc("┌──────┐\n│ api  │\n └──────┘", ASCII)),
      _doc("+------+\n| api  |\n| db   |\n+------+", ASCII))
def _check_ragged(fig, ctx):
    if fig.ascii is None:
        return []
    out = []
    for box in fig.ascii.boxes:
        off = sorted(set(box.ragged) | set(box.shifted))
        if not off:
            continue
        which = ("right border" if not box.shifted else
                 "left side or bottom corner" if not box.ragged else "border")
        out.append((off[0], f"box at line {box.top}: {which} off its column on {len(off)} line(s)"))
    return out


def _ascii_probe(which: str) -> Callable:
    def make(notation):
        soft, hard = (int(x) for x in notation["budgets"]["ascii"]["elements"])
        n = {"soft-fire": soft + 1, "soft-quiet": soft, "hard-fire": hard + 1, "hard-quiet": hard}[which]
        return _doc(" -> ".join(f"s{k}" for k in range(1, n + 1)), ASCII)
    return make


def _ascii_elements(fig, ctx) -> tuple:
    soft, hard = (int(x) for x in ctx.notation["budgets"]["ascii"]["elements"])
    return len(fig.ascii.elements), soft, hard


@rule("MA-ASCII-05", "warn", "ASCII figure over the soft element budget",
      "Aggregate or split: an ASCII figure holds a chain or a tree within the soft budget.",
      _ascii_probe("soft-fire"), _ascii_probe("soft-quiet"))
def _check_ascii_budget(fig, ctx):
    if fig.ascii is None:
        return []
    count, soft, hard = _ascii_elements(fig, ctx)
    return [(_fig_line(fig), f"{count} elements > soft budget {soft}")] if soft < count <= hard else []


@rule("MA-ASCII-06", "error", "ASCII figure over the hard element budget",
      "Write a numbered list, a nested list or a table instead (ascii.md §2 rule 4).",
      _ascii_probe("hard-fire"), _ascii_probe("hard-quiet"))
def _check_ascii_hard_budget(fig, ctx):
    if fig.ascii is None:
        return []
    count, _soft, hard = _ascii_elements(fig, ctx)
    return [(_fig_line(fig), f"{count} elements > hard budget {hard}; use a list or a table")] if count > hard else []


@rule("MA-ASCII-07", "warn", "Vertical connector off its column",
      "Move the connector to the column of the stroke above or below it (ascii.md §2).",
      (_doc("sensor\n  │ MQTT\n   ▼\ngateway", ASCII),
       _doc("a --+--> b ---+--> d\n    |         |\n     +--> c ---+", ASCII),
       _doc("root\n├── a\n │   └── b\n└── c", ASCII)),
      _doc("sensor\n  │ MQTT\n  ▼\ngateway", ASCII))
def _check_connector_drift(fig, ctx):
    if fig.ascii is None or not fig.ascii.drift:
        return []
    lines = sorted({lower for _upper, lower in fig.ascii.drift})
    shown = ", ".join(str(x) for x in lines[:6]) + (" …" if len(lines) > 6 else "")
    return [(lines[0], f"a vertical stroke moves by one column at line(s) {shown}")]


