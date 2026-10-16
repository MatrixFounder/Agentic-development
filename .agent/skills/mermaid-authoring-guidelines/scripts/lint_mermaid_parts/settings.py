"""SET rules of the figure lint: front matter, `%%{init}%%` directives and the settings
lines of the notation (TASK 126)."""

from __future__ import annotations

import json
import re
from typing import Callable, Optional

from .base import rule, _doc, _fig_line


@rule("MA-SET-01", "error", "Malformed init directive (mermaid ignores it without a diagnostic)",
      "Make the directive strict JSON: double quotes, no trailing comma.",
      _doc('%%{init: {"look": "classic",}}%%\nflowchart TB\n  A --> B'),
      _doc('%%{init: {"look": "classic"}}%%\nflowchart TB\n  A --> B'))
def _check_directive(fig, ctx):
    return [(s.line, s.error) for s in fig.settings_blocks if s.form == "directive" and s.error]


@rule("MA-SET-02", "error", "Frontmatter that does not parse or loses its settings",
      "Fix the YAML: two spaces per level, no tabs, one entry per key, `key: value` with a space, "
      "colours in quotes; a YAML error stops the render, and a lost value changes it silently.",
      _doc("---\nconfig:\n  look: classic\n    layout: dagre\n---\nflowchart TB\n  A --> B"),
      _doc("---\nconfig:\n  look: classic\n  layout: dagre\n---\nflowchart TB\n  A --> B"))
def _check_frontmatter(fig, ctx):
    return [(s.line, s.error) for s in fig.settings_blocks if s.form == "frontmatter" and s.error]


def _theme_pattern(notation: dict):
    return re.compile(notation.get("lint", {}).get("theme_value_pattern", r"^[\d \"#%(),.;A-Za-z]+$"))


@rule("MA-SET-03", "error", "themeVariables value that the sanitizer blanks",
      "Mermaid blanks a theme value holding -, _, : or /; drop the value (no font family).",
      _doc('%%{init: {"themeVariables": {"fontFamily": "Helvetica, Arial, sans-serif"}}}%%\n'
           "flowchart TB\n  A --> B"),
      _doc('%%{init: {"themeVariables": {"fontSize": "14px"}}}%%\nflowchart TB\n  A --> B'))
def _check_sanitizer(fig, ctx):
    pattern = _theme_pattern(ctx.notation)
    out = []
    for s in fig.settings_blocks:
        tv = (s.config or {}).get("themeVariables")
        if not isinstance(tv, dict):
            continue
        for key, value in tv.items():
            if isinstance(value, str) and not pattern.match(value):
                out.append((s.line, f"themeVariables.{key} = {value!r} is blanked by mermaid's sanitizer"))
    return out


@rule("MA-SET-04", "error", "Top-level fontFamily (mermaid 10.9 drops every other theme variable)",
      "Remove the top-level fontFamily; settings lines set no font (TASK D15).",
      _doc('%%{init: {"fontFamily": "Helvetica"}}%%\nflowchart TB\n  A --> B'),
      _doc('%%{init: {"themeVariables": {"fontSize": "14px"}}}%%\nflowchart TB\n  A --> B'))
def _check_toplevel_font(fig, ctx):
    return [(s.line, "a top-level `fontFamily` replaces the theme variables in mermaid 10.9")
            for s in fig.settings_blocks if isinstance(s.config, dict) and "fontFamily" in s.config]


@rule("MA-SET-05", "warn", "Fixed `theme` key (light text on GitHub's dark page)",
      "Remove `theme`; the viewer then picks a light or a dark theme (TASK R4.2).",
      _doc('%%{init: {"theme": "base", "look": "classic"}}%%\nflowchart TB\n  A --> B'),
      _doc('%%{init: {"look": "classic"}}%%\nflowchart TB\n  A --> B'))
def _check_theme(fig, ctx):
    return [(s.line, f"`theme: {s.config.get('theme')}` fixes the colours in dark mode")
            for s in fig.settings_blocks if isinstance(s.config, dict) and "theme" in s.config]


_SETTINGS_KEY = {"flowchart": "flowchart", "state": "state", "sequence": "sequence", "er": "er",
                 "gantt": "gantt", "class": "class", "requirementDiagram": "requirement",
                 "mindmap": "mindmap"}


def _notation_settings(notation: dict, kind: str) -> Optional[dict]:
    line = notation.get("settings", {}).get(_SETTINGS_KEY.get(kind, ""), "")
    m = re.match(r"^%%\{init:\s*(.*)\}%%$", line.strip(), re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def _settings_probe(fire: bool) -> Callable:
    def make(notation):
        line = notation.get("settings", {}).get("flowchart", "")
        body = "flowchart TB\n  A --> B"
        return _doc(body if fire else f"{line}\n{body}")
    return make


def _no_themecss_probe(notation):
    """The flowchart settings line without its themeCSS key: the line before TASK 121."""
    want = _notation_settings(notation, "flowchart") or {}
    want.pop("themeCSS", None)
    return _doc("%%{init: " + json.dumps(want) + "}%%\nflowchart TB\n  A --> B")


#: The keys MA-SET-06 pins wherever the kind's settings line in notation.json holds them.
_PINNED_SETTINGS = ("layout", "look", "themeCSS")
#: A pinned value longer than this is named by its settings entry, not quoted (TASK 121 D9).
_QUOTED_SETTING_MAX = 60


@rule("MA-SET-06", "warn", "Settings line without the pinned layout, look and themeCSS",
      "Copy the settings line of the kind from notation.json; it pins dagre and classic, which "
      "mermaid 12 changed, and the themeCSS that keeps HTML labels whole in GitHub's font.",
      (_settings_probe(True), _no_themecss_probe), _settings_probe(False))
def _check_pinned(fig, ctx):
    want = _notation_settings(ctx.notation, fig.kind)
    if not want:
        return []
    required = {k: want[k] for k in _PINNED_SETTINGS if k in want}
    if not required:
        return []
    have = fig.settings.config if fig.settings and isinstance(fig.settings.config, dict) else {}
    missing = []
    for key, value in required.items():
        if have.get(key) == value:
            continue
        if isinstance(value, str) and len(value) > _QUOTED_SETTING_MAX:
            missing.append(f'"{key}" of settings.{_SETTINGS_KEY.get(fig.kind, fig.kind)}')
        else:
            missing.append(f'"{key}": "{value}"')
    if missing:
        line = fig.settings.line if fig.settings else _fig_line(fig)
        return [(line, "missing " + ", ".join(missing))]
    return []


def _settings_signature(fig, notation: Optional[dict] = None) -> str:
    """The settings of a figure as one comparable string. Keys that notation.json `lint`
    `settings_per_chart_keys` lists for the kind (the width and padding of one gantt chart) may
    differ between figures, so they are left out."""
    s = fig.settings
    if s is None:
        return "none"
    if isinstance(s.config, dict):
        config = json.loads(json.dumps(s.config))
        per_chart = (notation or {}).get("lint", {}).get("settings_per_chart_keys", {})
        for section, keys in per_chart.items():
            if section == fig.kind and isinstance(config.get(section), dict):
                for key in keys:
                    config[section].pop(key, None)
        return json.dumps(config, sort_keys=True)
    return " ".join(s.raw.split())


@rule("MA-SET-07", "warn", "Figures of one kind with different settings in one document",
      "Use one settings line per kind in a document (TASK R3.8); the width and padding of one gantt "
      "chart may differ.",
      lambda n: (_doc("flowchart TB\n  A --> B") + "\n"
                 + _doc(n.get("settings", {}).get("flowchart", "") + "\nflowchart TB\n  C --> D")),
      lambda n: (_doc(n.get("settings", {}).get("flowchart", "") + "\nflowchart TB\n  A --> B") + "\n"
                 + _doc(n.get("settings", {}).get("flowchart", "") + "\nflowchart TB\n  C --> D")),
      scope="document")
def _check_settings_consistency(figures, ctx):
    first: dict = {}
    out = []
    for fig in figures:
        if fig.kind in ("ascii", "unknown"):
            continue
        sig = _settings_signature(fig, ctx.notation)
        if fig.kind not in first:
            first[fig.kind] = (sig, fig)
        elif sig != first[fig.kind][0]:
            out.append((_fig_line(fig), f"settings differ from the {fig.kind} figure at line "
                                        f"{_fig_line(first[fig.kind][1])}"))
    return out


