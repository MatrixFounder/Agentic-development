"""Text contrast of the SVG geometry: theme and author colours, and the contrast of
each text against what it is drawn on (TASK 125)."""

from __future__ import annotations

import json
import math
import re
from typing import Optional

import mermaid_model as mm

from .svg_model import _Svg
from .graph import _NODE_ID_PATTERNS


#: themeVariables from which mermaid derives the colours of most other elements: a figure that
#: sets one of them, or a `theme`, sets the colour of every text it draws.
THEME_GLOBAL_KEYS = frozenset({"darkMode", "background", "primaryColor", "primaryTextColor",
                               "secondaryColor", "tertiaryColor", "mainBkg", "textColor"})

#: themeVariables that colour a kind of measured text or the box mermaid draws it in.
THEME_TEXT_KEYS = {
    "node": frozenset({"nodeBkg", "nodeTextColor", "stateBkg", "stateLabelColor", "labelColor",
                       "classText", "altBackground", "compositeBackground"}),
    "edge": frozenset({"edgeLabelBackground", "labelBackground", "transitionLabelColor"}),
    "title": frozenset({"clusterBkg", "titleColor", "compositeBackground",
                        "compositeTitleBackground", "altBackground"}),
    "note": frozenset({"noteBkgColor", "noteTextColor"}),
    "actor": frozenset({"actorBkg", "actorTextColor"}),
    "message": frozenset({"signalTextColor"}),
    "task": frozenset({"taskBkgColor", "taskTextColor", "taskTextLightColor", "taskTextDarkColor",
                       "taskTextOutsideColor", "taskTextClickableColor", "activeTaskBkgColor",
                       "doneTaskBkgColor", "critBkgColor"}),
    "section": frozenset({"sectionBkgColor", "altSectionBkgColor", "sectionBkgColor2",
                          "titleColor"}),
    "other": frozenset({"labelTextColor", "labelBoxBkgColor", "loopTextColor", "titleColor",
                        "sequenceNumberColor", "signalColor"}),
}

#: themeVariables that colour a backdrop layer, by the layer role `measure_text.mjs` reports.
THEME_LAYER_KEYS = {
    "node": frozenset({"nodeBkg", "stateBkg", "altBackground", "compositeBackground"}),
    "cluster": frozenset({"clusterBkg", "compositeBackground", "compositeTitleBackground",
                          "altBackground"}),
    "edgeLabel": frozenset({"edgeLabelBackground", "labelBackground"}),
    "note": frozenset({"noteBkgColor"}),
    "actor": frozenset({"actorBkg"}),
    "activation": frozenset({"activationBkgColor"}),
    "task": frozenset({"taskBkgColor", "activeTaskBkgColor", "doneTaskBkgColor", "critBkgColor"}),
    "section": frozenset({"sectionBkgColor", "altSectionBkgColor", "sectionBkgColor2"}),
    "labelBox": frozenset({"labelBoxBkgColor"}),
    "marker": frozenset({"signalColor", "sequenceNumberColor"}),
}

#: Style properties that set the colour of a label or of the shape it sits in.
_COLOUR_PROPS = frozenset({"fill", "color", "background", "background-color"})
_FILL_PROPS = frozenset({"fill", "background", "background-color"})

_CLASSDEF_RE = re.compile(r"^\s*classDef\s+(\S+)\s+(.+?)\s*;?\s*$")
_CLASS_RE = re.compile(r"^\s*class\s+(\S+)\s+([A-Za-z0-9_][\w-]*)\s*;?\s*$")
_CSSCLASS_RE = re.compile(r'^\s*cssClass\s+"([^"]+)"\s+([A-Za-z0-9_][\w-]*)')
_STYLE_RE = re.compile(r"^\s*style\s+(\S+)\s+(.+?)\s*;?\s*$")
_LINKSTYLE_RE = re.compile(r"^\s*linkStyle\s+(\S+)\s+(.+?)\s*;?\s*$")
_TRIPLE_RE = re.compile(r":::\s*([A-Za-z0-9_][\w-]*)")
_SUBGRAPH_RE = re.compile(r"^\s*subgraph\s+([^\s\[\"(]+)")
#: The id of an edge, `e1@-->`: an `@` followed by the start of a link, never by `{`.
_EDGE_ID_RE = re.compile(r"(?<![\w@-])([A-Za-z0-9_][\w-]*)@(?=[-=~.<]|[ox][-=.])")
_COMPOSITE_RE = re.compile(r'^\s*state\s+(?:"[^"]*"\s+as\s+)?([^\s{"]+)\s*\{')
_INIT_RE = re.compile(r"%%\{\s*init\s*:\s*(\{.*\})\s*\}%%")


def _hex_rgb(colour: str) -> tuple:
    """(r, g, b) of `#rgb` or `#rrggbb`; ValueError otherwise."""
    c = (colour or "").strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6 or not re.fullmatch(r"[0-9A-Fa-f]{6}", c):
        raise ValueError("not a hex colour: %r" % colour)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(colour: str) -> float:
    """WCAG 2.2 relative luminance of a hex colour."""
    def channel(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in _hex_rgb(colour))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    """WCAG 2.2 contrast ratio of two hex colours, from 1.0 to 21.0."""
    a, b = relative_luminance(fg), relative_luminance(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def _triple_targets(line: str) -> list:
    """(id, class) for every `id:::class` and `id[label]:::class` of a line with quotes blanked."""
    out = []
    for m in _TRIPLE_RE.finditer(line):
        k = m.start() - 1
        while k >= 0 and line[k] in " \t":
            k -= 1
        if k >= 0 and line[k] in ")]}":
            depth = 0
            while k >= 0:  # walk back over the shape brackets to the node id
                if line[k] in ")]}":
                    depth += 1
                elif line[k] in "([{":
                    depth -= 1
                k -= 1
                if depth == 0:
                    break
        end = k + 1
        while k >= 0 and (line[k].isalnum() or line[k] in "_.-"):
            k -= 1
        ident = line[k + 1:end].lstrip("-.")
        if ident:
            out.append((ident, m.group(1)))
    return out


def _props(raw: str) -> dict:
    out = {}
    for part in re.split(r"(?<!\\),", raw or ""):
        if ":" in part:
            key, value = part.split(":", 1)
            out[key.strip().lower()] = value.strip()
    return out


def _settings_configs(source: str) -> list:
    """Every settings dict of a figure: its `%%{init}%%` directives and frontmatter `config`."""
    try:
        fig = mm.parse_figure(mm.figure_from_mmd(source))
        configs = [s.config for s in fig.settings_blocks if isinstance(s.config, dict)]
    except Exception:  # noqa: BLE001 - a model failure falls back to the directive alone
        configs = []
        for m in _INIT_RE.finditer(source or ""):
            try:
                value = json.loads(m.group(1))
            except ValueError:
                continue
            if isinstance(value, dict):
                configs.append(value)
    return configs


def _css_class_sets(css: str) -> list:
    """The class sets that the selectors of a `themeCSS` string require of the styled element."""
    out = []
    css = re.sub(r"/\*.*?\*/", "", css or "", flags=re.S)
    for block in re.finditer(r"([^{}]+)\{[^}]*\}", css):
        for selector in block.group(1).split(","):
            parts = [p for p in re.split(r"[\s>+~]+", selector.strip()) if p]
            if not parts:
                continue
            classes = frozenset(re.findall(r"\.(-?[_A-Za-z][\w-]*)", parts[-1]))
            if classes:
                out.append(classes)
    return out


def author_colours(source: str) -> dict:
    """What the figure source sets the colour of (TASK R7.6, D26).

    Returns a dict:

    * `nodes` / `node_fill`: ids of nodes and states whose class or `style` sets `fill` or
      `color` / sets `fill`; `all_nodes` / `all_nodes_fill` for `classDef default`;
    * `clusters` / `cluster_fill`: the same for subgraphs and composite states;
    * `edges`: ids of edges (`e1@-->`) whose class or `style` sets a colour: their labels;
    * `edge_labels`: a `linkStyle` sets a colour, so every edge label is author-scoped;
    * `theme_keys`: the `themeVariables` keys the settings set; `all_text`: a `theme` or a key
      of THEME_GLOBAL_KEYS is set, so every text is author-scoped;
    * `css`: the class sets the selectors of `themeCSS` require.

    Statements are read line by line, so the spec holds for every Mermaid kind; it never raises.
    """
    spec = {"nodes": set(), "node_fill": set(), "all_nodes": False, "all_nodes_fill": False,
            "clusters": set(), "cluster_fill": set(), "edges": set(), "edge_labels": False,
            "theme_keys": set(), "all_text": False, "css": []}
    try:
        for cfg in _settings_configs(source):
            if cfg.get("theme"):
                spec["all_text"] = True
            tv = cfg.get("themeVariables")
            if isinstance(tv, dict):
                spec["theme_keys"].update(k for k, v in tv.items() if v not in (None, ""))
            css = cfg.get("themeCSS")
            if isinstance(css, str):
                spec["css"].extend(_css_class_sets(css))
        if spec["theme_keys"] & THEME_GLOBAL_KEYS:
            spec["all_text"] = True
        classdefs, assigned, styled, containers, edge_ids = {}, [], [], set(), set()
        for raw in (source or "").split("\n"):
            line = re.sub(r"%%.*$", "", raw) if not raw.lstrip().startswith("%%{") else ""
            edge_ids.update(_EDGE_ID_RE.findall(re.sub(r'"[^"]*"', '""', line)))
            m = _CLASSDEF_RE.match(line)
            if m:
                props = _props(m.group(2))
                for name in m.group(1).split(","):
                    classdefs[name] = props
                continue
            m = _CLASS_RE.match(line) or _CSSCLASS_RE.match(line)
            if m:
                assigned.extend((t.strip(), m.group(2)) for t in m.group(1).split(",") if t.strip())
                continue
            m = _STYLE_RE.match(line)
            if m:
                styled.append((m.group(1), _props(m.group(2))))
                continue
            m = _LINKSTYLE_RE.match(line)
            if m:
                spec["edge_labels"] = spec["edge_labels"] or bool(_COLOUR_PROPS & set(_props(m.group(2))))
                continue
            m = _SUBGRAPH_RE.match(line) or _COMPOSITE_RE.match(line)
            if m:
                containers.add(m.group(1))
            assigned.extend(_triple_targets(re.sub(r'"[^"]*"', '""', line)))

        def mark(target, props):
            colour = bool(_COLOUR_PROPS & set(props))
            fill = bool(_FILL_PROPS & set(props))
            if not colour:
                return
            if target in edge_ids:
                spec["edges"].add(target)  # an edge id: the class colours that edge's label
                return
            group = "clusters" if target in containers else "nodes"
            spec[group].add(target)
            if fill:
                spec["cluster_fill" if group == "clusters" else "node_fill"].add(target)

        default = classdefs.get("default") or {}
        spec["all_nodes"] = bool(_COLOUR_PROPS & set(default))
        spec["all_nodes_fill"] = bool(_FILL_PROPS & set(default))
        for target, cname in assigned:
            if cname in classdefs:
                mark(target, classdefs[cname])
        for target, props in styled:
            mark(target, props)
    except Exception:  # noqa: BLE001 - an unreadable source sets nothing it can name
        pass
    return spec


def _owner_name(S: _Svg, ident: str) -> str:
    """The mermaid id of a node, state or cluster from its group's `data-id` or element id."""
    ident = S.strip_prefix(ident or "")
    for pat in _NODE_ID_PATTERNS:
        m = pat.match(ident)
        if m:
            return m.group(1)
    return ident


def _layer_is_author(S: _Svg, layer: dict, spec: dict) -> bool:
    role = layer.get("role") or "other"
    if role == "band":
        return True  # the source writes the colour of every sequence `rect` and `box` block
    if spec["theme_keys"] & THEME_LAYER_KEYS.get(role, frozenset()):
        return True
    if role == "node":
        return spec["all_nodes_fill"] or _owner_name(S, layer.get("id")) in spec["node_fill"]
    if role == "cluster":
        return _owner_name(S, layer.get("id")) in spec["cluster_fill"]
    return False


def text_scope(S: _Svg, label: dict, spec: Optional[dict]) -> str:
    """`author`, `theme` or `unknown` (no spec) for one measured text; see the module doc."""
    if spec is None:
        return "unknown"
    if spec["all_text"]:
        return "author"
    kind = label.get("kind") or "other"
    if spec["theme_keys"] & THEME_TEXT_KEYS.get(kind, THEME_TEXT_KEYS["other"]):
        return "author"
    classes = set((label.get("cls") or "").split())
    if any(required <= classes for required in spec["css"]):
        return "author"
    owner = _owner_name(S, label.get("owner") or label.get("id") or "")
    if kind == "node" and (spec["all_nodes"] or owner in spec["nodes"]):
        return "author"
    if kind == "title" and owner in spec["clusters"]:
        return "author"
    if kind == "edge" and (spec.get("edge_labels") or owner in spec.get("edges", ())):
        return "author"
    under = label.get("under") or []
    if under and _layer_is_author(S, under[-1], spec):
        return "author"  # the topmost filled shape under the text takes its fill from the source
    return "theme"


def _contrast_metrics(S: _Svg, measure: dict, spec: Optional[dict]) -> dict:
    texts = []
    labels = measure.get("labels", [])
    for lab in labels:
        fg, bg = lab.get("fg"), lab.get("bg")
        if not fg or not bg:
            continue
        try:
            ratio = math.floor(contrast_ratio(fg, bg) * 100) / 100.0
        except ValueError:
            continue
        entry = {"text": (lab.get("text") or "")[:60], "kind": lab.get("kind") or "other",
                 "fg": fg, "bg": bg, "ratio": ratio, "scope": text_scope(S, lab, spec)}
        if lab.get("uncertain"):
            entry["uncertain"] = True
        texts.append(entry)
    return {"page": measure.get("page"), "texts": texts,
            "measured": any("bg" in lab for lab in labels)}


