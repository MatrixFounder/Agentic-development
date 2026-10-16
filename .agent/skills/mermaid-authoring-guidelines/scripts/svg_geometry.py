#!/usr/bin/env python3
"""Geometry of a rendered Mermaid SVG (TASK 108, R7.5, R7.6).

Reads the SVG that mermaid-cli writes and measures what a reader sees: crossings, edges through
nodes, edges through group titles, edges through edge labels, label overlaps, clipped labels,
size, the effective text size in a document column, and the contrast of every text against what
it is drawn on. Pure
function of the SVG text plus an optional text-measurement dict produced in the browser by
`measure_text.mjs` and an optional colour spec read from the figure source by
`author_colours()`; it needs no node and no browser itself, so the eval grader and the unit
tests run it in CI on committed SVGs.

Contrast (TASK R7.6, D26). The browser measures each text's drawn colour and the colour under
it. A text is `author`-scoped when the figure source sets its colour or its background: a node
or state with a class or `style` that sets `fill` or `color`, a subgraph or composite state the
same way, a `themeVariables` key that colours that kind of text or what it is drawn on, a
`themeCSS` rule whose classes the text carries, a fixed `theme`, or a topmost filled shape under
the text whose fill the source sets (a styled node or subgraph, a sequence `rect` or `box`
block). Any other text is drawn in the viewer's theme colours and is `theme`-scoped.
`evaluate()` fails an author-scoped text below `contrast_min` and reports a theme-scoped one as
information; `thresholds.contrast_scope` = `all` gates every text.

Coordinates are absolute SVG user units after composing every `transform` up to the root. Width
and height come from the `viewBox`: mermaid-cli 12 writes a fixed `max-width`, and PNG sizes are
rescaled, so neither measures the figure.

Anatomy handled (measured on mermaid 10.9.8, 11.17.2 and 12.1.0; research report r3b):

* the diagram kind is the root's `aria-roledescription`;
* flowchart, state, class and ER figures share one extractor: `g.node` shapes, `g.cluster` and
  `g.statediagram-cluster` groups with their `g.cluster-label` titles, edge paths, `g.edgeLabel`
  boxes; invisible links (`~~~`: class `edge-thickness-invisible` in 11.x and 12.x,
  `stroke-width: 0` in 10.9) are excluded;
* edge ends come from the SVG ids: the `LS-<src> LE-<dst>` classes of 10.9, the
  `L_<src>_<dst>_<n>` ids of 11.x and 12.x split against the known node and group ids; an edge
  with no usable id (every state transition, an ambiguous split) is attached to the node boxes
  nearest to its first and last point;
* sequence figures: lifelines, messages, message texts, and the message labels a lifeline other
  than the message's own ends runs through (the struck-label class of research report r6);
  gantt figures: bars and their labels;
* any other kind reports its size only, with a warning, and `geometry` says `not modelled`, so a
  pass never reads as a full check. Its measured texts, and those of a sequence figure, are
  still tested for overlapping one another. The lines of one label count as one label: mermaid
  draws each line of a participant name, an actor name or a journey task as its own `<text>`,
  all at one anchor, and the `dy` of each `<tspan>` sets the lines apart (`_line_anchor`).

Legibility (TASK R7.6) is read off the smallest text a reader must read, not the most common
size: one 6 px label among 16 px labels fails the figure, and the finding names it. Text of a
class in `thresholds.legibility_exempt_classes` of `assets/notation.json` is not text a reader
must read.

The thresholds that decide pass and fail live in `assets/notation.json`. `evaluate()` reads
them; `analyze_svg()` reads the legibility exemptions. The constants below are tolerances of the
instrument (stroke width, flattening error, text overhang); they are not thresholds.

Standard library only.

The geometry is a package (TASK 125): `svg_geometry_parts/` holds one module per section, in
this order, each importing only from the modules above it: `base`, `tolerances`, `transforms`,
`flattening`, `plane`, `text_estimate`, `svg_model`, `graph`, `sequence`, `gantt`, `contrast`
and `api`. The tolerances that the paragraph above names lie in `tolerances.py`. This file
binds every top-level name of the 12 modules, so a caller imports `svg_geometry` as before,
and it holds the debug command line `main`. A test that replaces a name that `main` calls
patches it on this module. A name that a module of the package looks up is replaced on that
module: `sys.modules[<function>.__module__]`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mermaid_model as mm  # noqa: E402
from svg_geometry_parts.base import (  # noqa: E402
    METRIC_KEYS, CHECKS, GATE_CHECKS, WARN_CHECKS, SEVERITIES)
from svg_geometry_parts.tolerances import (  # noqa: E402
    FLATTEN_TOL_PX, SAMPLE_STEP_PX, SHARED_END_MARGIN_PX, DEDUPE_RADIUS_PX, END_SNAP_PX,
    THROUGH_NOISE_PX, THROUGH_MIN_RUN_PX, TITLE_MIN_INSIDE_PX, TITLE_NEAR_MARGIN_PX,
    OVERLAP_MIN_AREA_PX2, EDGE_IN_LABEL_MIN_PX, CLIP_TOL_PX, PAINTED_CLIP_TOL_PX, PAINTED_BOX_KINDS,
    GANTT_EDGE_TOL_PX, MESSAGE_END_SNAP_PX, LIFELINE_LABEL_MARGIN_PX)
from svg_geometry_parts.transforms import (  # noqa: E402
    IDENT, mat_mul, mat_apply, _TF, _NUM, parse_transform)
from svg_geometry_parts.flattening import (  # noqa: E402
    _PathScanner, _dist_point_line, _mid, flatten_cubic, _flatten_arc, path_polylines)
from svg_geometry_parts.plane import (  # noqa: E402
    bbox_of, box_union, box_grow, box_area, box_overlap_area, boxes_touch, point_in_box,
    dist_point_box, segment_intersection, segments_of, polyline_intersections, clip_length_in_box,
    length_in_box, convex_hull, point_in_convex, polygon_area, box_hull_overlap_area,
    dist_point_segment, penetration, dedupe_points)
from svg_geometry_parts.text_estimate import _HELVETICA, estimate_text_width  # noqa: E402
from svg_geometry_parts.svg_model import (  # noqa: E402
    _local, _classes, _text_of, _font_px_of, _XML_FORBIDDEN, _Svg)
from svg_geometry_parts.graph import (  # noqa: E402
    _NODE_ID_PATTERNS, _EDGE_CLASSES, _node_name, _cluster_name, _is_edge_path, _INVISIBLE_STYLE,
    _is_invisible, _in_label_group, _edge_display_names, _extract_graph, _graph_metrics)
from svg_geometry_parts.sequence import (  # noqa: E402
    _measured_texts, _lifeline_label_crossings, _sequence_metrics)
from svg_geometry_parts.gantt import _gantt_metrics  # noqa: E402
from svg_geometry_parts.contrast import (  # noqa: E402
    THEME_GLOBAL_KEYS, THEME_TEXT_KEYS, THEME_LAYER_KEYS, _COLOUR_PROPS, _FILL_PROPS, _CLASSDEF_RE,
    _CLASS_RE, _CSSCLASS_RE, _STYLE_RE, _LINKSTYLE_RE, _TRIPLE_RE, _SUBGRAPH_RE, _EDGE_ID_RE,
    _COMPOSITE_RE, _INIT_RE, _hex_rgb, relative_luminance, contrast_ratio, _triple_targets, _props,
    _settings_configs, _css_class_sets, author_colours, _owner_name, _layer_is_author, text_scope,
    _contrast_metrics)
from svg_geometry_parts.api import (  # noqa: E402
    _empty_metrics, _unprobed_swap, _escaped, _swap_px, _font_swap_from_measure,
    _box_clip_tolerance, _clipped_from_measure, _line_anchor, _painted_label_overlaps,
    _legibility_exempt, _smallest_text, analyze_svg, evaluate, passes, fired)

#: Every top-level name of the package's modules, and `main`: what a caller reads
#: from this file. An editor then reads the imports above as re-exports.
__all__ = [
    "METRIC_KEYS", "CHECKS", "GATE_CHECKS", "WARN_CHECKS", "SEVERITIES", "FLATTEN_TOL_PX",
    "SAMPLE_STEP_PX", "SHARED_END_MARGIN_PX", "DEDUPE_RADIUS_PX", "END_SNAP_PX", "THROUGH_NOISE_PX",
    "THROUGH_MIN_RUN_PX", "TITLE_MIN_INSIDE_PX", "TITLE_NEAR_MARGIN_PX", "OVERLAP_MIN_AREA_PX2",
    "EDGE_IN_LABEL_MIN_PX", "CLIP_TOL_PX", "PAINTED_CLIP_TOL_PX", "PAINTED_BOX_KINDS",
    "GANTT_EDGE_TOL_PX", "MESSAGE_END_SNAP_PX", "LIFELINE_LABEL_MARGIN_PX", "IDENT", "mat_mul",
    "mat_apply", "_TF", "_NUM", "parse_transform", "_PathScanner", "_dist_point_line", "_mid",
    "flatten_cubic", "_flatten_arc", "path_polylines", "bbox_of", "box_union", "box_grow",
    "box_area", "box_overlap_area", "boxes_touch", "point_in_box", "dist_point_box",
    "segment_intersection", "segments_of", "polyline_intersections", "clip_length_in_box",
    "length_in_box", "convex_hull", "point_in_convex", "polygon_area", "box_hull_overlap_area",
    "dist_point_segment", "penetration", "dedupe_points", "_HELVETICA", "estimate_text_width",
    "_local", "_classes", "_text_of", "_font_px_of", "_XML_FORBIDDEN", "_Svg", "_NODE_ID_PATTERNS",
    "_EDGE_CLASSES", "_node_name", "_cluster_name", "_is_edge_path", "_INVISIBLE_STYLE",
    "_is_invisible", "_in_label_group", "_edge_display_names", "_extract_graph", "_graph_metrics",
    "_measured_texts", "_lifeline_label_crossings", "_sequence_metrics", "_gantt_metrics",
    "THEME_GLOBAL_KEYS", "THEME_TEXT_KEYS", "THEME_LAYER_KEYS", "_COLOUR_PROPS", "_FILL_PROPS",
    "_CLASSDEF_RE", "_CLASS_RE", "_CSSCLASS_RE", "_STYLE_RE", "_LINKSTYLE_RE", "_TRIPLE_RE",
    "_SUBGRAPH_RE", "_EDGE_ID_RE", "_COMPOSITE_RE", "_INIT_RE", "_hex_rgb", "relative_luminance",
    "contrast_ratio", "_triple_targets", "_props", "_settings_configs", "_css_class_sets",
    "author_colours", "_owner_name", "_layer_is_author", "text_scope", "_contrast_metrics",
    "_empty_metrics", "_unprobed_swap", "_escaped", "_swap_px", "_font_swap_from_measure",
    "_box_clip_tolerance", "_clipped_from_measure", "_line_anchor", "_painted_label_overlaps",
    "_legibility_exempt", "_smallest_text", "analyze_svg", "evaluate", "passes", "fired", "main",
]


def main(argv: Optional[list] = None) -> int:
    """Debug entry point: `svg_geometry.py FIG.svg [MEASURE.json] [--source FIG.mmd]` prints
    metrics and findings; `--source` scopes text contrast by the figure's own colours. The JSON is
    ASCII, and an error line escapes what it quotes (TASK 123 R4.1)."""
    args = list(sys.argv[1:] if argv is None else argv)
    usage = "usage: svg_geometry.py FIG.svg [MEASURE.json] [--column PX] [--source FIG.mmd]"
    if not args or args[0] in ("-h", "--help"):
        print(usage, file=sys.stderr)
        return 3
    column = mm.load_notation()["column_px"]
    source = None
    try:
        if "--column" in args:
            i = args.index("--column")
            column = int(args[i + 1])
            del args[i:i + 2]
        if "--source" in args:
            i = args.index("--source")
            source = Path(args[i + 1]).read_text(encoding="utf-8")
            del args[i:i + 2]
    except (IndexError, ValueError):
        print(usage, file=sys.stderr)
        return 3
    except OSError as exc:
        print("svg_geometry.py: %s" % _escaped(str(exc)), file=sys.stderr)
        return 2
    try:
        svg_text = Path(args[0]).read_text(encoding="utf-8")
        measure = json.loads(Path(args[1]).read_text(encoding="utf-8")) if len(args) > 1 else None
        metrics = analyze_svg(svg_text, column, measure,
                              author_colours(source) if source is not None else None)
    except (OSError, ValueError) as exc:
        print("svg_geometry.py: %s" % _escaped(str(exc)), file=sys.stderr)
        return 2
    findings = evaluate(metrics)
    print(json.dumps({"metrics": metrics, "findings": findings, "pass": passes(findings)},
                     indent=1, ensure_ascii=True))
    return 0 if passes(findings) else 1


if __name__ == "__main__":
    sys.exit(main())
