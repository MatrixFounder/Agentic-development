"""CLASS rules of the figure lint: colours, contrast and class definitions (TASK 126)."""

from __future__ import annotations

import re
from typing import Optional

import mermaid_model as mm

from .base import rule, _doc, _hazard_check, _fig_line


_HEX = re.compile(r"^#([0-9A-Fa-f]{3,4}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")
_FUNC_COLOUR = re.compile(r"^(rgba?|hsla?)\(\s*([^)]*)\)$", re.IGNORECASE)

#: The 148 CSS named colours (CSS Color 4, as the `color-name` package of the pinned renderers
#: lists them). `fill:yellow,color:white` measures 1.07:1 in every render, so a name is a colour.
_CSS_NAMED = {
    "aliceblue": "f0f8ff", "antiquewhite": "faebd7", "aqua": "00ffff", "aquamarine": "7fffd4",
    "azure": "f0ffff", "beige": "f5f5dc", "bisque": "ffe4c4", "black": "000000",
    "blanchedalmond": "ffebcd", "blue": "0000ff", "blueviolet": "8a2be2", "brown": "a52a2a",
    "burlywood": "deb887", "cadetblue": "5f9ea0", "chartreuse": "7fff00", "chocolate": "d2691e",
    "coral": "ff7f50", "cornflowerblue": "6495ed", "cornsilk": "fff8dc", "crimson": "dc143c",
    "cyan": "00ffff", "darkblue": "00008b", "darkcyan": "008b8b", "darkgoldenrod": "b8860b",
    "darkgray": "a9a9a9", "darkgreen": "006400", "darkgrey": "a9a9a9", "darkkhaki": "bdb76b",
    "darkmagenta": "8b008b", "darkolivegreen": "556b2f", "darkorange": "ff8c00",
    "darkorchid": "9932cc", "darkred": "8b0000", "darksalmon": "e9967a", "darkseagreen": "8fbc8f",
    "darkslateblue": "483d8b", "darkslategray": "2f4f4f", "darkslategrey": "2f4f4f",
    "darkturquoise": "00ced1", "darkviolet": "9400d3", "deeppink": "ff1493",
    "deepskyblue": "00bfff", "dimgray": "696969", "dimgrey": "696969", "dodgerblue": "1e90ff",
    "firebrick": "b22222", "floralwhite": "fffaf0", "forestgreen": "228b22", "fuchsia": "ff00ff",
    "gainsboro": "dcdcdc", "ghostwhite": "f8f8ff", "gold": "ffd700", "goldenrod": "daa520",
    "gray": "808080", "green": "008000", "greenyellow": "adff2f", "grey": "808080",
    "honeydew": "f0fff0", "hotpink": "ff69b4", "indianred": "cd5c5c", "indigo": "4b0082",
    "ivory": "fffff0", "khaki": "f0e68c", "lavender": "e6e6fa", "lavenderblush": "fff0f5",
    "lawngreen": "7cfc00", "lemonchiffon": "fffacd", "lightblue": "add8e6", "lightcoral": "f08080",
    "lightcyan": "e0ffff", "lightgoldenrodyellow": "fafad2", "lightgray": "d3d3d3",
    "lightgreen": "90ee90", "lightgrey": "d3d3d3", "lightpink": "ffb6c1", "lightsalmon": "ffa07a",
    "lightseagreen": "20b2aa", "lightskyblue": "87cefa", "lightslategray": "778899",
    "lightslategrey": "778899", "lightsteelblue": "b0c4de", "lightyellow": "ffffe0",
    "lime": "00ff00", "limegreen": "32cd32", "linen": "faf0e6", "magenta": "ff00ff",
    "maroon": "800000", "mediumaquamarine": "66cdaa", "mediumblue": "0000cd",
    "mediumorchid": "ba55d3", "mediumpurple": "9370db", "mediumseagreen": "3cb371",
    "mediumslateblue": "7b68ee", "mediumspringgreen": "00fa9a", "mediumturquoise": "48d1cc",
    "mediumvioletred": "c71585", "midnightblue": "191970", "mintcream": "f5fffa",
    "mistyrose": "ffe4e1", "moccasin": "ffe4b5", "navajowhite": "ffdead", "navy": "000080",
    "oldlace": "fdf5e6", "olive": "808000", "olivedrab": "6b8e23", "orange": "ffa500",
    "orangered": "ff4500", "orchid": "da70d6", "palegoldenrod": "eee8aa", "palegreen": "98fb98",
    "paleturquoise": "afeeee", "palevioletred": "db7093", "papayawhip": "ffefd5",
    "peachpuff": "ffdab9", "peru": "cd853f", "pink": "ffc0cb", "plum": "dda0dd",
    "powderblue": "b0e0e6", "purple": "800080", "rebeccapurple": "663399", "red": "ff0000",
    "rosybrown": "bc8f8f", "royalblue": "4169e1", "saddlebrown": "8b4513", "salmon": "fa8072",
    "sandybrown": "f4a460", "seagreen": "2e8b57", "seashell": "fff5ee", "sienna": "a0522d",
    "silver": "c0c0c0", "skyblue": "87ceeb", "slateblue": "6a5acd", "slategray": "708090",
    "slategrey": "708090", "snow": "fffafa", "springgreen": "00ff7f", "steelblue": "4682b4",
    "tan": "d2b48c", "teal": "008080", "thistle": "d8bfd8", "tomato": "ff6347",
    "turquoise": "40e0d0", "violet": "ee82ee", "wheat": "f5deb3", "white": "ffffff",
    "whitesmoke": "f5f5f5", "yellow": "ffff00", "yellowgreen": "9acd32"
}


def _channel(text: str, scale: float) -> float:
    text = text.strip()
    return float(text[:-1]) * scale / 100 if text.endswith("%") else float(text)


def _hsl_to_rgb(h: float, s: float, l: float) -> tuple:
    s, l = s / 100, l / 100
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    sector = int(h % 360 // 60)
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][sector]
    return (r + m) * 255, (g + m) * 255, (b + m) * 255


def _rgba(value: str) -> Optional[tuple]:
    """(r, g, b, alpha) of a CSS colour written as hex, rgb(), rgba(), hsl(), hsla(), a CSS name
    or `transparent`; None for any other form (`none`, `currentColor`, a variable)."""
    value = value.strip()
    named = value.lower()
    if named == "transparent":
        return 0, 0, 0, 0.0
    if named in _CSS_NAMED:
        h = _CSS_NAMED[named]
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0
    m = _HEX.match(value)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        alpha = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha
    m = _FUNC_COLOUR.match(value)
    if not m:
        return None
    parts = [p for p in re.split(r"[\s,/]+", m.group(2).strip()) if p]
    if len(parts) not in (3, 4):
        return None
    try:
        alpha = _channel(parts[3], 1.0) if len(parts) == 4 else 1.0
        if m.group(1).lower().startswith("rgb"):
            rgb = tuple(_channel(p, 255) for p in parts[:3])
        else:
            rgb = _hsl_to_rgb(float(parts[0].rstrip("deg")), _channel(parts[1], 100), _channel(parts[2], 100))
    except ValueError:
        return None
    return tuple(min(255.0, max(0.0, c)) for c in rgb) + (min(1.0, max(0.0, alpha)),)


def _over(top: tuple, bottom: tuple) -> tuple:
    a = top[3]
    return tuple(top[k] * a + bottom[k] * (1 - a) for k in range(3)) + (1.0,)


def _luminance(rgb: tuple) -> float:
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: tuple, bg: tuple) -> float:
    """WCAG 2.2 contrast ratio of two opaque RGB colours."""
    hi, lo = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _style_contrast(props: dict, notation: dict) -> Optional[float]:
    """Lowest contrast of `color` on `fill` over a light and a dark page; None without both."""
    fill, color = _rgba(props.get("fill", "")), _rgba(props.get("color", ""))
    if fill is None or color is None:
        return None
    pages = [(255, 255, 255, 1.0)]
    dark = _rgba(notation.get("renderers", {}).get("dark", {}).get("background", ""))
    if dark is not None and fill[3] < 1:
        pages.append(dark)
    ratios = []
    for page in pages:
        bg = _over(fill, page)
        ratios.append(contrast_ratio(_over(color, bg), bg))
    return min(ratios)


def _style_blocks(fig) -> list:
    """(line, name, props) for every classDef and style statement of the figure."""
    out = []
    for diagram in (fig.flowchart, fig.state):
        if diagram is None:
            continue
        out += [(d["line"], f"classDef {name}", d["props"]) for name, d in diagram.classdefs.items()]
        out += [(s["line"], f"style {s['target']}", mm._parse_props(s["raw"])) for s in diagram.styles]
    return out


@rule("MA-CLASS-01", "error", "Text colour on fill below the contrast minimum",
      "Darken `color` or lighten `fill` until the ratio reaches notation.json `contrast_min` "
      "(WCAG 2.2 SC 1.4.3).",
      _doc("flowchart TB\n  A --> B\n  classDef c fill:#FFFFFF,color:#BBBBBB\n  class A c"),
      _doc("flowchart TB\n  A --> B\n  classDef c fill:#E8F0FB,color:#0F2A47\n  class A c"))
def _check_contrast(fig, ctx):
    minimum = float(ctx.notation.get("contrast_min", 4.5))
    out = []
    for line, name, props in _style_blocks(fig):
        ratio = _style_contrast(props, ctx.notation)
        if ratio is not None and ratio < minimum:
            out.append((line, f"`{name}`: contrast {ratio:.2f}:1 < {minimum}:1"))
    return out


def _class_uses(fig) -> dict:
    """class name -> first line where a node, state or subgraph uses it."""
    uses: dict = {}
    if fig.flowchart:
        for n in fig.flowchart.nodes.values():
            for c in n.classes:
                uses.setdefault(c, n.line)
        for sid, names in fig.flowchart.subgraph_classes.items():
            sg = fig.flowchart.subgraphs.get(sid)
            for c in names:
                uses.setdefault(c, sg.line if sg else _fig_line(fig))
    if fig.state:
        for s in fig.state.states.values():
            for c in s.classes:
                uses.setdefault(c, s.line)
    return uses


def _class_defs(fig) -> dict:
    defs: dict = {}
    for diagram in (fig.flowchart, fig.state):
        if diagram is not None:
            defs.update(diagram.classdefs)
    return defs


@rule("MA-CLASS-02", "warn", "Class used but not defined",
      "Define the class with classDef in this figure, or drop it.",
      _doc("flowchart TB\n  A:::missing --> B"),
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#FFFFFF,color:#263238"))
def _check_undefined_class(fig, ctx):
    defs = _class_defs(fig)
    return [(line, f"class `{name}`") for name, line in _class_uses(fig).items()
            if name not in defs and name != "default"]


@rule("MA-CLASS-03", "warn", "Class defined but not used",
      "Delete unused classDef lines.",
      _doc("flowchart TB\n  A --> B\n  classDef unused fill:#FFFFFF,color:#263238"),
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#FFFFFF,color:#263238"))
def _check_unused_class(fig, ctx):
    uses = _class_uses(fig)
    return [(d["line"], f"classDef `{name}`") for name, d in _class_defs(fig).items()
            if name not in uses and name != "default"]


rule("MA-CLASS-04", "warn", "classDef default",
     "Name the class and apply it; in mermaid 10.9 `default` also styles every subgraph.",
     _doc("flowchart TB\n  A --> B\n  classDef default fill:#FFFFFF,color:#263238"),
     _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#FFFFFF,color:#263238"))(
    _hazard_check("classdef-default"))


def _theme_text_contrasts(fill: tuple, notation: dict) -> list:
    """(theme, ratio) of each theme's own text colour on *fill*, composed over that theme's page.

    The text colours are notation.json `lint.theme_text_colours`; the light page is white, the
    dark page `renderers.dark.background`."""
    pages = {"default": (255, 255, 255, 1.0)}
    dark = _rgba(notation.get("renderers", {}).get("dark", {}).get("background", ""))
    if dark is not None:
        pages["dark"] = dark
    out = []
    for theme, colour in notation.get("lint", {}).get("theme_text_colours", {}).items():
        text, page = _rgba(colour), pages.get(theme)
        if text is None or page is None:
            continue
        bg = _over(fill, page)
        out.append((theme, contrast_ratio(_over(text, bg), bg)))
    return out


@rule("MA-CLASS-05", "warn", "Fill without a text colour that a theme's own text cannot be read on",
      "Set `color` next to `fill`: without it the dark theme draws light text and the light theme "
      "dark text on the fill.",
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#E8F0FB,stroke:#2E5A8A"),
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47"))
def _check_fill_without_color(fig, ctx):
    minimum = float(ctx.notation.get("contrast_min", 4.5))
    out = []
    for line, name, props in _style_blocks(fig):
        fill = _rgba(props.get("fill", ""))
        if "color" in props or fill is None:
            continue
        low = [f"{theme} theme {ratio:.2f}:1" for theme, ratio in _theme_text_contrasts(fill, ctx.notation)
               if ratio < minimum]
        if low:
            out.append((line, f"`{name}` sets fill {props['fill']} and no color: " + ", ".join(low)
                        + f" < {minimum}:1"))
    return out


rule("MA-CLASS-06", "error", "`class` statement above the line that defines its node",
     "Move the `class` line below the node's first statement, or write `A:::c` on that statement; "
     "mermaid styles only nodes that exist at the `class` line, so the class is lost silently.",
     _doc("flowchart TB\n  class A c\n  A --> B\n  classDef c fill:#FFFFFF,color:#263238"),
     _doc("flowchart TB\n  A --> B\n  class A c\n  classDef c fill:#FFFFFF,color:#263238"))(
    _hazard_check("class-before-node"))

rule("MA-CLASS-07", "warn", "Styling in a kind that draws in the viewer's theme colours",
     "Drop classDef, style, cssClass and ::: from class, chart and timeline figures "
     "(other-kinds.md rule 5); the legend carries any category.",
     _doc("classDiagram\n  class Dog\n  style Dog fill:#FFF4E0,color:#4A2C00"),
     _doc("classDiagram\n  class Dog"))(
    _hazard_check("styling-theme"))


