"""The header of the SVG geometry: the metric keys, the checks and their severities
(TASK 125)."""

from __future__ import annotations


#: Keys of the dict `analyze_svg` returns. Every key is always present. An edge id is the
#: readable `src->dst` (`#2`, `#3` for a repeated pair); a node id is the mermaid id.
METRIC_KEYS = (
    "diagram",              # aria-roledescription of the root, e.g. "flowchart-v2", "sequence"
    "width", "height",      # viewBox size in CSS px
    "nodes", "edges",       # counts of drawn nodes and visible edges (invisible links excluded);
                            # sequence: participants and messages; gantt: bars and 0
    "crossings",            # count of edge-edge crossings, shared endpoints excluded
    "crossing_pairs",       # [[edge_a, edge_b, x, y], ...]
    "edges_through_nodes",  # [{"edge": id, "node": id, "depth_px": float}, ...]; depth_px is the
                            # length the edge runs inside a node other than its ends, 2 px in from
                            # the node's outline (+ "perpendicular_px")
    "title_crossings",      # [{"edge": id, "title": text, "near_miss": bool}, ...] (+ "cluster");
                            # near_miss: the edge misses the painted text but enters the reserved box
    "edges_through_labels",  # [{"edge": id, "label": text, "inside_px": float}, ...]; inside_px is
                            # the length the edge runs inside another edge's label box, 2 px in
                            # from its border
    "label_overlaps",       # [{"a": id, "b": id, "area_px": float}, ...] (+ "kind": label-label,
                            # label-node, label-title or title-node)
    "clipped_labels",       # [{"label": text, "overflow_px": float, "where": "its box" |
                            # "the figure's edge"}, ...] (needs measure)
    "font_swap",            # {"probed": bool, "font_family": str, "hidden": [{"label", "kind",
                            # "overflow_px", "where"}], "past_border": [{"label", "overflow_px"}]}:
                            # the HTML labels redrawn in GitHub's font (TASK 121; needs measure)
    "duplicate_edges",      # [{"pair": [a, b], "edges": [id, ...]}, ...] (TASK R3.3)
    "font_px",              # the most common size of the label text drawn (the report line)
    "effective_font_px",    # font_px * min(1, column_px / width)
    "smallest_font_px",     # the smallest size of a drawn text a reader must read; font_px
                            # when nothing was measured
    "smallest_text",        # that text ("" when nothing was measured)
    "smallest_effective_font_px",  # smallest_font_px * min(1, column_px / width): legibility
    "geometry",             # "modelled", "partly modelled" or "not modelled": whether the
                            # crossings, edges through nodes and titles of this kind are read
    "sequence",             # {"lifeline_gaps": [...], "widest_message_px": float} or {}
                            # (+ "participants" in lifeline order, "median_gap_px",
                            # "widest_message", "width_source": "measure" | "estimate",
                            # "lifeline_through_label": [{"message", "from", "to",
                            # "lifelines": [...], "own": [...]}], "lifeline_label_crossings": n,
                            # "lifeline_own_crossings": n)
    "gantt",                # {"bars": n, "labels_outside": n, "overflow": [...]} or {}
                            # (overflow items {"label", "reason", "px"}; + "section_overflow",
                            # "today_marker", "chart_width_px")
    "contrast",             # {"page": "#rrggbb", "measured": bool, "texts": [{"text", "kind",
                            # "fg", "bg", "ratio", "scope": "author" | "theme" | "unknown"}]};
                            # ratio truncated to 2 decimals (needs measure)
    "measured",             # True when a measure_text dict was applied
    "warnings",             # analysis notes, e.g. an edge mapped to its ends by proximity
)

#: Checks `evaluate` can report, in report order.
CHECKS = ("crossings", "edges_through_nodes", "title_crossings", "edges_through_labels",
          "label_overlaps", "clipped_labels", "font_swap", "legibility", "contrast",
          "title_near_miss", "duplicate_edges", "lifeline_gap", "lifeline_through_label",
          "gantt_overflow", "geometry")

#: Checks whose `fail` finding fails a figure (TASK R7.6). They are the render checks a negative
#: fence may name (TASK R9.4; `mermaid_model.RENDER_CHECK_NAMES` holds the same names for the
#: lint, and a test pins the two equal). A named check shows its defect when it fails in at
#: least one render.
GATE_CHECKS = ("crossings", "edges_through_nodes", "title_crossings", "edges_through_labels",
               "label_overlaps", "clipped_labels", "font_swap", "legibility", "contrast",
               "lifeline_through_label", "gantt_overflow")

#: Checks that never fail a figure. A negative fence cannot name them: the lint rejects the name
#: (MA-NEG-02), and the render check reads it as no render check.
WARN_CHECKS = ("title_near_miss", "duplicate_edges", "lifeline_gap", "geometry")

#: Severities in report order. `info` reports a measurement that gates nothing.
SEVERITIES = ("fail", "warn", "info")

