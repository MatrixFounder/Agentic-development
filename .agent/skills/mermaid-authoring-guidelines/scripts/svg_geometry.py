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
"""

from __future__ import annotations

import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mermaid_model as mm  # noqa: E402

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
                            # "lifelines": [...]}], "lifeline_label_crossings": n)
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
          "label_overlaps", "clipped_labels", "legibility", "contrast", "title_near_miss",
          "duplicate_edges", "lifeline_gap", "lifeline_through_label", "gantt_overflow", "geometry")

#: Checks whose `fail` finding fails a figure (TASK R7.6). They are the render checks a negative
#: fence may name (TASK R9.4; `mermaid_model.RENDER_CHECK_NAMES` holds the same names for the
#: lint, and a test pins the two equal). A named check shows its defect when it fails in at
#: least one render.
GATE_CHECKS = ("crossings", "edges_through_nodes", "title_crossings", "edges_through_labels",
               "label_overlaps", "clipped_labels", "legibility", "contrast", "gantt_overflow")

#: Checks that never fail a figure. A negative fence cannot name them: the lint rejects the name
#: (MA-NEG-02), and the render check reads it as no render check.
WARN_CHECKS = ("title_near_miss", "duplicate_edges", "lifeline_gap", "lifeline_through_label",
               "geometry")

#: Severities in report order. `info` reports a measurement that gates nothing.
SEVERITIES = ("fail", "warn", "info")

# ----------------------------------------------------------------------------- instrument tolerances

FLATTEN_TOL_PX = 0.3          # maximum distance of a flattened Bezier from the true curve
SAMPLE_STEP_PX = 1.0          # step when an edge is sampled inside a node outline
SHARED_END_MARGIN_PX = 10.0   # an intersection this close to a node both edges touch is a join
DEDUPE_RADIUS_PX = 4.0        # intersection points closer than this are one crossing
END_SNAP_PX = 12.0            # an edge end this close to a node box attaches to that node
THROUGH_NOISE_PX = 2.0        # a stroke within this distance of a node border runs along it
THROUGH_MIN_RUN_PX = 3.0      # a run inside a node shorter than this is a corner touch
TITLE_MIN_INSIDE_PX = 2.0     # edge length inside a title box that counts as a crossing
TITLE_NEAR_MARGIN_PX = 4.0    # margin around a reserved title box that makes a near miss
OVERLAP_MIN_AREA_PX2 = 4.0    # overlap area below this is anti-aliasing
EDGE_IN_LABEL_MIN_PX = 3.0    # edge length inside another edge's label box that counts
CLIP_TOL_PX = 2.0             # text overhang allowed past the box of an HTML label (reserved
                              # space inside a padded shape) or past the figure's edge, whatever
                              # the box width. Measured 2026-10-03 on the 147 reference renders:
                              # 0 px on every positive figure, 1.17 px on the one drawn in a
                              # fallback font (renderer-facts.md, MA-SET-03)
PAINTED_CLIP_TOL_PX = 0.5     # text overhang allowed past the box of SVG text that is the drawn
                              # outline around it (PAINTED_BOX_KINDS): half a 1 px outline. A
                              # note line 1.82 px past its box shows ink past the border in the
                              # PNG (TASK 108 calibration, 2026-10-03)
PAINTED_BOX_KINDS = ("note", "actor", "task")  # SVG text measured against its drawn rectangle
GANTT_EDGE_TOL_PX = 0.5       # a gantt label this far past the chart edge is cut off
MESSAGE_END_SNAP_PX = 25.0    # a message end this close to a lifeline belongs to it (activation
                              # bars move the end 5 px per nesting level)
LIFELINE_LABEL_MARGIN_PX = 2.0  # a lifeline this far inside a label's glyph box strikes it

# ----------------------------------------------------------------------------- affine transforms

IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)  # (a, b, c, d, e, f): x' = a x + c y + e; y' = b x + d y + f


def mat_mul(m, n):
    """Return the matrix m * n: n is applied first, then m."""
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return (a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D,
            a * E + c * F + e, b * E + d * F + f)


def mat_apply(m, x, y):
    """Map the point (x, y) through the matrix m."""
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


_TF = re.compile(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)")
_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def parse_transform(text: Optional[str]):
    """Return the matrix of an SVG `transform` attribute (a list of functions, left to right)."""
    m = IDENT
    if not text:
        return m
    for name, args in _TF.findall(text):
        v = [float(t) for t in _NUM.findall(args)]
        if name == "matrix" and len(v) == 6:
            t = tuple(v)
        elif name == "translate" and v:
            t = (1.0, 0.0, 0.0, 1.0, v[0], v[1] if len(v) > 1 else 0.0)
        elif name == "scale" and v:
            sx = v[0]
            sy = v[1] if len(v) > 1 else sx
            t = (sx, 0.0, 0.0, sy, 0.0, 0.0)
        elif name == "rotate" and v:
            r = math.radians(v[0])
            t = (math.cos(r), math.sin(r), -math.sin(r), math.cos(r), 0.0, 0.0)
            if len(v) == 3:
                t = mat_mul(mat_mul((1.0, 0.0, 0.0, 1.0, v[1], v[2]), t),
                            (1.0, 0.0, 0.0, 1.0, -v[1], -v[2]))
        elif name == "skewX" and v:
            t = (1.0, 0.0, math.tan(math.radians(v[0])), 1.0, 0.0, 0.0)
        elif name == "skewY" and v:
            t = (1.0, math.tan(math.radians(v[0])), 0.0, 1.0, 0.0, 0.0)
        else:
            continue
        m = mat_mul(m, t)
    return m


# ----------------------------------------------------------------------------- path flattening


class _PathScanner:
    def __init__(self, d: str):
        self.d, self.i, self.n = d, 0, len(d)

    def _skip(self):
        while self.i < self.n and self.d[self.i] in " \t\r\n,":
            self.i += 1

    def command(self):
        self._skip()
        if self.i < self.n and self.d[self.i].isalpha():
            c = self.d[self.i]
            self.i += 1
            return c
        return None

    def has_number(self):
        self._skip()
        return self.i < self.n and (self.d[self.i].isdigit() or self.d[self.i] in "+-.")

    def number(self):
        self._skip()
        m = _NUM.match(self.d, self.i)
        if not m:
            raise ValueError("bad path data near %r" % self.d[self.i:self.i + 20])
        self.i = m.end()
        return float(m.group())

    def flag(self):
        self._skip()
        if self.i >= self.n or self.d[self.i] not in "01":
            raise ValueError("bad arc flag near %r" % self.d[self.i:self.i + 20])
        c = self.d[self.i]
        self.i += 1
        return c == "1"


def _dist_point_line(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length < 1e-12:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    return abs((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / length


def _mid(a, b):
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def flatten_cubic(p0, p1, p2, p3, tol=FLATTEN_TOL_PX, out=None, depth=0):
    """Append points approximating a cubic Bezier (p0 excluded, p3 included) to *out*.

    De Casteljau subdivision until both control points lie within *tol* of the chord.
    """
    if out is None:
        out = []
    if depth > 16 or max(_dist_point_line(p1, p0, p3), _dist_point_line(p2, p0, p3)) <= tol:
        out.append(p3)
        return out
    p01, p12, p23 = _mid(p0, p1), _mid(p1, p2), _mid(p2, p3)
    p012, p123 = _mid(p01, p12), _mid(p12, p23)
    p0123 = _mid(p012, p123)
    flatten_cubic(p0, p01, p012, p0123, tol, out, depth + 1)
    flatten_cubic(p0123, p123, p23, p3, tol, out, depth + 1)
    return out


def _flatten_arc(p0, rx, ry, phi, large, sweep, p1, out):
    """Append points of an elliptical arc (SVG 1.1 F.6.5 centre parameterisation)."""
    x1, y1 = p0
    x2, y2 = p1
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2):
        out.append(p1)
        return
    rx, ry = abs(rx), abs(ry)
    ph = math.radians(phi)
    cs, sn = math.cos(ph), math.sin(ph)
    dx2, dy2 = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p = cs * dx2 + sn * dy2
    y1p = -sn * dx2 + cs * dy2
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        coef = -coef
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    cx = cs * cxp - sn * cyp + (x1 + x2) / 2.0
    cy = sn * cxp + cs * cyp + (y1 + y2) / 2.0

    def angle(ux, uy, vx, vy):
        return math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)

    th1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dth > 0:
        dth -= 2 * math.pi
    elif sweep and dth < 0:
        dth += 2 * math.pi
    steps = max(4, int(abs(dth) / (math.pi / 16)) + 1)
    for k in range(1, steps):
        t = th1 + dth * k / steps
        out.append((cx + rx * math.cos(t) * cs - ry * math.sin(t) * sn,
                    cy + rx * math.cos(t) * sn + ry * math.sin(t) * cs))
    out.append(p1)  # the exact end point, free of trigonometric rounding


def path_polylines(d: Optional[str], tol: float = FLATTEN_TOL_PX) -> list:
    """Flatten SVG path data into polylines: a list of lists of (x, y), one per subpath.

    Supports M L H V C S Q T A Z in absolute and relative form, implicit command repetition,
    and the implicit lineto after a moveto. Raises ValueError on data it cannot read, such as
    numbers after a closepath, instead of looping on them.
    """
    sc = _PathScanner(d or "")
    subs, cur = [], []
    x = y = sx = sy = 0.0
    last_c = last_q = None
    cmd = None
    last_i = -1
    while True:
        if sc.i == last_i:  # an iteration that consumes nothing would repeat forever
            raise ValueError("path data does not advance near %r" % sc.d[sc.i:sc.i + 20])
        last_i = sc.i
        c = sc.command()
        if c is None:
            if cmd is None or not sc.has_number():
                break
            if cmd in "Zz":
                raise ValueError("numbers after closepath near %r" % sc.d[sc.i:sc.i + 20])
            c = cmd
            if c in "Mm":
                c = "L" if c == "M" else "l"
        cmd = c
        rel = c.islower()
        C = c.upper()
        if C == "Z":
            if cur:
                cur.append((sx, sy))
                subs.append(cur)
            cur = []
            x, y = sx, sy
            last_c = last_q = None
            continue
        while True:
            if C == "M":
                nx, ny = sc.number(), sc.number()
                if rel:
                    nx, ny = x + nx, y + ny
                if cur:
                    subs.append(cur)
                cur = [(nx, ny)]
                x, y, sx, sy = nx, ny, nx, ny
                C = "L"
                last_c = last_q = None
            elif C == "L":
                nx, ny = sc.number(), sc.number()
                if rel:
                    nx, ny = x + nx, y + ny
                if not cur:
                    cur = [(x, y)]
                cur.append((nx, ny))
                x, y = nx, ny
                last_c = last_q = None
            elif C == "H":
                nx = sc.number()
                nx = x + nx if rel else nx
                if not cur:
                    cur = [(x, y)]
                cur.append((nx, y))
                x = nx
                last_c = last_q = None
            elif C == "V":
                ny = sc.number()
                ny = y + ny if rel else ny
                if not cur:
                    cur = [(x, y)]
                cur.append((x, ny))
                y = ny
                last_c = last_q = None
            elif C in "CS":
                if C == "C":
                    x1, y1 = sc.number(), sc.number()
                    if rel:
                        x1, y1 = x + x1, y + y1
                else:
                    x1, y1 = (2 * x - last_c[0], 2 * y - last_c[1]) if last_c else (x, y)
                x2, y2, nx, ny = sc.number(), sc.number(), sc.number(), sc.number()
                if rel:
                    x2, y2, nx, ny = x + x2, y + y2, x + nx, y + ny
                if not cur:
                    cur = [(x, y)]
                flatten_cubic((x, y), (x1, y1), (x2, y2), (nx, ny), tol, cur)
                last_c, last_q = (x2, y2), None
                x, y = nx, ny
            elif C in "QT":
                if C == "Q":
                    qx, qy = sc.number(), sc.number()
                    if rel:
                        qx, qy = x + qx, y + qy
                else:
                    qx, qy = (2 * x - last_q[0], 2 * y - last_q[1]) if last_q else (x, y)
                nx, ny = sc.number(), sc.number()
                if rel:
                    nx, ny = x + nx, y + ny
                if not cur:
                    cur = [(x, y)]
                c1 = (x + 2.0 / 3 * (qx - x), y + 2.0 / 3 * (qy - y))
                c2 = (nx + 2.0 / 3 * (qx - nx), ny + 2.0 / 3 * (qy - ny))
                flatten_cubic((x, y), c1, c2, (nx, ny), tol, cur)
                last_q, last_c = (qx, qy), None
                x, y = nx, ny
            elif C == "A":
                rx, ry, phi = sc.number(), sc.number(), sc.number()
                large, sweep = sc.flag(), sc.flag()
                nx, ny = sc.number(), sc.number()
                if rel:
                    nx, ny = x + nx, y + ny
                if not cur:
                    cur = [(x, y)]
                _flatten_arc((x, y), rx, ry, phi, large, sweep, (nx, ny), cur)
                x, y = nx, ny
                last_c = last_q = None
            else:
                raise ValueError("unsupported path command %r" % c)
            if not sc.has_number():
                break
    if cur:
        subs.append(cur)
    return [s for s in subs if s]


# ----------------------------------------------------------------------------- plane geometry


def bbox_of(points) -> tuple:
    """(x0, y0, x1, y1) of a non-empty point list."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def box_union(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def box_grow(b, d):
    return (b[0] - d, b[1] - d, b[2] + d, b[3] + d)


def box_area(b) -> float:
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def box_overlap_area(a, b) -> float:
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if (w > 0 and h > 0) else 0.0


def boxes_touch(a, b) -> bool:
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def point_in_box(p, b) -> bool:
    return b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]


def dist_point_box(p, b) -> float:
    dx = max(b[0] - p[0], 0.0, p[0] - b[2])
    dy = max(b[1] - p[1], 0.0, p[1] - b[3])
    return math.hypot(dx, dy)


def segment_intersection(p, p2, q, q2):
    """Proper intersection point of segments p-p2 and q-q2, or None.

    Parallel and collinear segments return None: running along another edge is not a crossing.
    """
    rx, ry = p2[0] - p[0], p2[1] - p[1]
    sx, sy = q2[0] - q[0], q2[1] - q[1]
    den = rx * sy - ry * sx
    if abs(den) < 1e-9:
        return None
    qpx, qpy = q[0] - p[0], q[1] - p[1]
    t = (qpx * sy - qpy * sx) / den
    u = (qpx * ry - qpy * rx) / den
    if -1e-9 <= t <= 1 + 1e-9 and -1e-9 <= u <= 1 + 1e-9:
        return (p[0] + t * rx, p[1] + t * ry)
    return None


def segments_of(polyline) -> list:
    """Segments of a polyline as (a, b, bbox), zero-length segments dropped."""
    out = []
    for i in range(len(polyline) - 1):
        a, b = polyline[i], polyline[i + 1]
        if a == b:
            continue
        out.append((a, b, (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))))
    return out


def polyline_intersections(seg_a, seg_b) -> list:
    pts = []
    for a, a2, ba in seg_a:
        for b, b2, bb in seg_b:
            if ba[2] < bb[0] or bb[2] < ba[0] or ba[3] < bb[1] or bb[3] < ba[1]:
                continue
            p = segment_intersection(a, a2, b, b2)
            if p is not None:
                pts.append(p)
    return pts


def clip_length_in_box(a, b, box) -> float:
    """Length of segment a-b inside an axis-aligned box (Liang-Barsky)."""
    x0, y0 = a
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - box[0]), (dx, box[2] - x0), (-dy, y0 - box[1]), (dy, box[3] - y0)):
        if abs(p) < 1e-12:
            if q < 0:
                return 0.0
        else:
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return 0.0
    return (t1 - t0) * math.hypot(dx, dy)


def length_in_box(segs, box) -> float:
    if box[2] <= box[0] or box[3] <= box[1]:
        return 0.0
    total = 0.0
    for a, b, bb in segs:
        if bb[2] < box[0] or bb[0] > box[2] or bb[3] < box[1] or bb[1] > box[3]:
            continue
        total += clip_length_in_box(a, b, box)
    return total


def convex_hull(points) -> list:
    """Convex hull, counter-clockwise in a y-up frame (Andrew's monotone chain)."""
    pts = sorted(set((round(p[0], 4), round(p[1], 4)) for p in points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def point_in_convex(p, hull) -> bool:
    """True when p lies strictly inside a convex polygon of 3 or more points (either winding)."""
    n = len(hull)
    if n < 3:
        return False
    sign = 0
    for i in range(n):
        a, b = hull[i], hull[(i + 1) % n]
        cr = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        if abs(cr) < 1e-12:
            return False
        s = 1 if cr > 0 else -1
        if sign == 0:
            sign = s
        elif s != sign:
            return False
    return True


def polygon_area(poly) -> float:
    """Signed area of a polygon (shoelace); its sign gives the winding."""
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def box_hull_overlap_area(box, hull) -> float:
    """Area of the axis-aligned *box* inside the convex *hull* (Sutherland-Hodgman clip).

    A label in the empty corner of a diamond's or a circle's box overlaps the box, not the shape.
    A hull of fewer than 3 points has no inside: its bounding box stands in for it.
    """
    if len(hull) < 3:
        return box_overlap_area(box, bbox_of(hull)) if hull else 0.0
    if box_overlap_area(box, bbox_of(hull)) <= 0:
        return 0.0
    orient = 1.0 if polygon_area(hull) > 0 else -1.0
    poly = [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3])]
    for i in range(len(hull)):
        a, b = hull[i], hull[(i + 1) % len(hull)]

        def side(p):
            return orient * ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]))

        clipped = []
        for k in range(len(poly)):
            p, q = poly[k], poly[(k + 1) % len(poly)]
            sp, sq = side(p), side(q)
            if sp >= 0:
                clipped.append(p)
            if (sp >= 0) != (sq >= 0):
                t = sp / (sp - sq)
                clipped.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        poly = clipped
        if len(poly) < 3:
            return 0.0
    return abs(polygon_area(poly))


def dist_point_segment(p, a, b) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def penetration(segs, hull, hull_box, inset=THROUGH_NOISE_PX) -> tuple:
    """(run_px, perpendicular_px) of a polyline inside a convex outline.

    run_px is the length of the polyline inside the outline inset by *inset* px: how far the
    line travels inside the node, ignoring a stroke that runs along the border.
    perpendicular_px is the largest distance from a point of the polyline to the border.
    Sampled every SAMPLE_STEP_PX along each segment that touches the outline's box.

    The run, not the perpendicular depth, decides: an edge that enters a node on one side and
    leaves through the next side reads as two edges joined at that node, however close to a
    border it stays (11.17 K3,3: 60 px run at 9.5 px depth).
    """
    run = perpendicular = 0.0
    n = len(hull)
    for a, b, bb in segs:
        if not boxes_touch(bb, hull_box):
            continue
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        steps = max(1, int(math.ceil(L / SAMPLE_STEP_PX)))
        for k in range(steps):
            t = (k + 0.5) / steps
            p = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
            if not point_in_box(p, hull_box) or not point_in_convex(p, hull):
                continue
            d = min(dist_point_segment(p, hull[i], hull[(i + 1) % n]) for i in range(n))
            if d > perpendicular:
                perpendicular = d
            if d >= inset:
                run += L / steps
    return run, perpendicular


def dedupe_points(points, radius=DEDUPE_RADIUS_PX) -> list:
    out = []
    for p in points:
        if all(math.hypot(p[0] - q[0], p[1] - q[1]) > radius for q in out):
            out.append(p)
    return out


# ----------------------------------------------------------------------------- text estimate

# Helvetica advance widths (1/1000 em) for ASCII 32..126. Used only where the SVG carries no
# width and no browser measurement was supplied: sequence and gantt <text>. Error up to ~16 %.
_HELVETICA = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278,
              556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556,
              1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
              667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
              333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
              556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]


def estimate_text_width(text: str, font_px: float) -> float:
    """Approximate advance width of *text* in px (Helvetica metrics; no browser)."""
    units = 0
    for ch in text:
        o = ord(ch)
        if 32 <= o <= 126:
            units += _HELVETICA[o - 32]
        elif o >= 0x2E80:
            units += 1000      # CJK and other full-width scripts
        elif o in (0x2014, 0x2026, 0x2192):
            units += 1000      # em dash, ellipsis, arrow
        else:
            units += 600       # Cyrillic, Greek, Latin-1 and other letters, rough average
    return units * font_px / 1000.0


# ----------------------------------------------------------------------------- SVG model


def _local(tag) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _classes(el) -> list:
    return (el.get("class") or "").split()


def _text_of(el) -> str:
    return " ".join(t.strip() for t in el.itertext() if t.strip())


def _font_px_of(el) -> Optional[float]:
    m = re.search(r"font-size:\s*([\d.]+)px", el.get("style") or "")
    if m:
        return float(m.group(1))
    fs = el.get("font-size")
    if fs:
        m = re.match(r"\s*([\d.]+)", fs)
        if m:
            return float(m.group(1))
    return None


#: Characters XML 1.0 forbids. Mermaid writes one raw when a label holds an entity such as `#1;`.
_XML_FORBIDDEN = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f]")


class _Svg:
    """A parsed SVG with the absolute transform of every element."""

    def __init__(self, svg_text: str):
        if "<!ENTITY" in svg_text or "<!DOCTYPE" in svg_text:
            raise ValueError("an SVG with a DOCTYPE or an entity declaration is not analysed")
        svg_text, self.removed_controls = _XML_FORBIDDEN.subn("", svg_text)
        self.root = ET.fromstring(svg_text)
        if _local(self.root.tag) != "svg":
            raise ValueError("the root element is <%s>, not <svg>" % _local(self.root.tag))
        self.parent = {}
        self.abs = {}
        self.order = {}
        self._walk(self.root, IDENT)
        vb = [float(v) for v in _NUM.findall(self.root.get("viewBox") or "")]
        self.viewbox = tuple(vb) if len(vb) == 4 else (0.0, 0.0, 0.0, 0.0)
        self.kind = self.root.get("aria-roledescription") or ""
        self.svg_id = self.root.get("id") or "my-svg"
        css = " ".join((s.text or "") for s in self.root.iter() if _local(s.tag) == "style")
        self.css = css
        m = re.search(r"#%s\s*\{[^}]*?font-size:\s*([\d.]+)px" % re.escape(self.svg_id), css)
        self.css_font_px = float(m.group(1)) if m else 16.0

    def _walk(self, el, m):
        mm_ = mat_mul(m, parse_transform(el.get("transform")))
        self.abs[el] = mm_
        self.order[el] = len(self.order)
        if _local(el.tag) == "foreignObject":
            # HTML content: no SVG geometry below this point.
            for ch in el.iter():
                if ch is not el:
                    self.parent.setdefault(ch, el)
            return
        for ch in el:
            self.parent[ch] = el
            self._walk(ch, mm_)

    def elements(self, tag=None):
        for el in self.order:
            if tag is None or _local(el.tag) == tag:
                yield el

    def ancestors(self, el, stop=None):
        cur = self.parent.get(el)
        while cur is not None and cur is not stop:
            yield cur
            cur = self.parent.get(cur)

    def strip_prefix(self, ident: str) -> str:
        pre = self.svg_id + "-"
        return ident[len(pre):] if ident.startswith(pre) else ident

    def fo_box(self, el):
        """Absolute box of a foreignObject, or None when it has no area."""
        m = self.abs.get(el, IDENT)
        x, y = float(el.get("x") or 0), float(el.get("y") or 0)
        w, h = float(el.get("width") or 0), float(el.get("height") or 0)
        if w <= 0 or h <= 0:
            return None
        return bbox_of([mat_apply(m, x, y), mat_apply(m, x + w, y), mat_apply(m, x, y + h),
                        mat_apply(m, x + w, y + h)])

    def shape_points(self, el):
        """Absolute outline points of a basic shape, or None."""
        t = _local(el.tag)
        m = self.abs.get(el, IDENT)

        def f(name, default=0.0):
            try:
                return float(el.get(name) or default)
            except ValueError:
                return default

        if t == "rect":
            w, h = f("width"), f("height")
            if w <= 0 or h <= 0:
                return None
            x, y = f("x"), f("y")
            return [mat_apply(m, x, y), mat_apply(m, x + w, y), mat_apply(m, x + w, y + h),
                    mat_apply(m, x, y + h)]
        if t in ("circle", "ellipse"):
            cx, cy = f("cx"), f("cy")
            rx = f("r") if t == "circle" else f("rx")
            ry = f("r") if t == "circle" else f("ry")
            if rx <= 0 or ry <= 0:
                return None
            return [mat_apply(m, cx + rx * math.cos(k * math.pi / 16),
                              cy + ry * math.sin(k * math.pi / 16)) for k in range(32)]
        if t in ("polygon", "polyline"):
            nums = [float(v) for v in _NUM.findall(el.get("points") or "")]
            pts = [mat_apply(m, nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
            return pts or None
        if t == "path":
            try:
                polys = path_polylines(el.get("d") or "", tol=0.5)
            except ValueError:
                return None
            pts = [mat_apply(m, x, y) for poly in polys for (x, y) in poly]
            return pts or None
        if t == "line":
            return [mat_apply(m, f("x1"), f("y1")), mat_apply(m, f("x2"), f("y2"))]
        return None

    def text_box_estimate(self, t, font_px=None):
        """Estimated absolute box of an SVG <text> (Helvetica metrics, no browser)."""
        m = self.abs.get(t, IDENT)
        fs = font_px or _font_px_of(t) or self.css_font_px
        lines = [_text_of(ts) for ts in t if _local(ts.tag) == "tspan"] or [_text_of(t)]
        w = max(estimate_text_width(s, fs) for s in lines) if lines else 0.0
        h = fs * 1.2 * max(1, len(lines))
        x, y = float(t.get("x") or 0), float(t.get("y") or 0)
        anchor = t.get("text-anchor") or ""
        style = t.get("style") or ""
        if "text-anchor: middle" in style or anchor == "middle":
            x0 = x - w / 2
        elif "text-anchor: end" in style or anchor == "end":
            x0 = x - w
        else:
            x0 = x
        return bbox_of([mat_apply(m, x0, y - h / 2), mat_apply(m, x0 + w, y + h / 2)])


# ----------------------------------------------------------------------------- graph figures

_NODE_ID_PATTERNS = (re.compile(r"^flowchart-(.+)-\d+$"), re.compile(r"^state-(.+)-\d+$"),
                     re.compile(r"^classId-(.+)-\d+$"), re.compile(r"^entity-(.+)-\d+$"))
_EDGE_CLASSES = ("flowchart-link", "transition", "relation", "relationshipLine", "er")


def _node_name(S: _Svg, el) -> str:
    if el.get("data-id"):
        return el.get("data-id")
    ident = S.strip_prefix(el.get("id") or "")
    for pat in _NODE_ID_PATTERNS:
        m = pat.match(ident)
        if m:
            return m.group(1)
    return ident


def _cluster_name(S: _Svg, el) -> str:
    ident = el.get("data-id") or S.strip_prefix(el.get("id") or "")
    m = re.match(r"^state-(.+)-\d+$", ident)
    return m.group(1) if m else ident


def _is_edge_path(S: _Svg, p) -> bool:
    if p.get("data-edge") == "true":
        return True
    cl = _classes(p)
    if any(c in cl for c in _EDGE_CLASSES[:4]):
        return True
    par = S.parent.get(p)
    return par is not None and "edgePaths" in _classes(par)


_INVISIBLE_STYLE = re.compile(r"(^|;)\s*(stroke-width:\s*0(px)?\s*(;|$)|display:\s*none|visibility:\s*hidden)")


def _is_invisible(p) -> bool:
    """An invisible link: class `edge-thickness-invisible` (11.x, 12.x) or `stroke-width: 0` (10.9)."""
    if "edge-thickness-invisible" in _classes(p):
        return True
    return _INVISIBLE_STYLE.search(p.get("style") or "") is not None


def _in_label_group(S: _Svg, el, stop) -> bool:
    for a in S.ancestors(el, stop):
        if _local(a.tag) == "foreignObject":
            return True
        if _local(a.tag) == "g" and ("label" in _classes(a) or "cluster-label" in _classes(a)):
            return True
    return False


def _edge_display_names(edges) -> None:
    """Give every edge a readable name `src->dst`, numbered when a pair repeats."""
    seen = {}
    for e in edges:
        base = "%s->%s" % (e["src"] or "?", e["dst"] or "?")
        seen[base] = seen.get(base, 0) + 1
        e["name"] = base if seen[base] == 1 else "%s#%d" % (base, seen[base])


def _extract_graph(S: _Svg, warnings: list) -> tuple:
    """Nodes, clusters, edges and edge labels of a flowchart, state, class or ER figure."""
    clusters, nodes, edges, labels = [], [], [], []
    # --- clusters: subgraphs and composite states
    for g in S.elements("g"):
        cl = _classes(g)
        if "cluster" not in cl and "statediagram-cluster" not in cl:
            continue
        box, outer = None, None
        for ch in g.iter():
            if ch is g or _local(ch.tag) != "rect" or _in_label_group(S, ch, g):
                continue
            pts = S.shape_points(ch)
            if not pts:
                continue
            if "outer" in _classes(ch):
                outer = bbox_of(pts)
            if "inner" in _classes(ch):
                continue
            box = box_union(box, bbox_of(pts))
        if outer is not None:
            box = outer
        title, title_text = None, ""
        for lab in g.iter():
            if _local(lab.tag) == "g" and "cluster-label" in _classes(lab):
                title_text = _text_of(lab)
                for fo in lab.iter():
                    if _local(fo.tag) == "foreignObject":
                        title = box_union(title, S.fo_box(fo))
                if title is None:
                    for t in lab.iter():
                        if _local(t.tag) == "text" and _text_of(t):
                            title = box_union(title, S.text_box_estimate(t))
                break
        clusters.append({"id": _cluster_name(S, g), "raw_id": g.get("id") or "", "box": box,
                         "title": title, "title_fo": title, "title_text": title_text})
    # --- nodes
    for g in S.elements("g"):
        cl = _classes(g)
        if "node" not in cl:
            continue
        if any(_local(d.tag) == "g" and "root" in _classes(d) for d in g.iter() if d is not g):
            continue  # a group laid out recursively, drawn as a node wrapper (10.9)
        pts = []
        for ch in g.iter():
            if ch is g or _local(ch.tag) not in ("rect", "path", "polygon", "circle", "ellipse"):
                continue
            if _in_label_group(S, ch, g):
                continue
            sp = S.shape_points(ch)
            if sp:
                pts.extend(sp)
        if len(pts) < 2:
            continue
        name = _node_name(S, g)
        hull = convex_hull(pts)
        box = bbox_of(pts)
        shape_classes = set()
        for ch in g.iter():
            shape_classes.update(_classes(ch))
        pseudo = ("statediagram-note" in cl or name.endswith("----parent")
                  or "state-start" in shape_classes or "state-end" in shape_classes
                  or (S.kind.lower().startswith("state")
                      and re.search(r"(^|_)(start|end)$", name) is not None))
        nodes.append({"id": name, "box": box, "hull": hull, "pseudo": pseudo,
                      "label": _text_of(g)[:60]})
    # --- edges (document order; invisible links kept for label alignment, then dropped)
    all_paths = [p for p in S.elements("path") if _is_edge_path(S, p)]
    for p in all_paths:
        cl = _classes(p)
        invisible = _is_invisible(p)
        try:
            polys = [[mat_apply(S.abs[p], x, y) for (x, y) in poly]
                     for poly in path_polylines(p.get("d"))]
        except ValueError as exc:
            warnings.append("edge %s skipped: %s" % (p.get("id") or "?", exc))
            continue
        pts = [pt for poly in polys for pt in poly]
        if len(pts) < 2:
            continue
        raw = p.get("data-id") or S.strip_prefix(p.get("id") or "")
        src = dst = None
        ls = [c[3:] for c in cl if c.startswith("LS-")]
        le = [c[3:] for c in cl if c.startswith("LE-")]
        if ls and le:
            src, dst = ls[0], le[0]
        edges.append({"raw": raw, "src": src, "dst": dst, "polys": polys, "invisible": invisible,
                      "mapped_by": "id" if src is not None else None})
    known = {n["id"] for n in nodes} | {c["id"] for c in clusters}
    for e in edges:
        if e["src"] is None and e["raw"].startswith("L_"):
            core = re.sub(r"_\d+$", "", e["raw"][2:])
            parts = core.split("_")
            splits = [("_".join(parts[:k]), "_".join(parts[k:])) for k in range(1, len(parts))]
            splits = [s for s in splits if s[0] in known and s[1] in known]
            if len(splits) == 1:
                e["src"], e["dst"] = splits[0]
                e["mapped_by"] = "id"
            elif len(splits) > 1:
                warnings.append("edge id %s splits %d ways; ends taken from geometry"
                                % (e["raw"], len(splits)))
    node_ids = {n["id"] for n in nodes}
    cluster_ids = {c["id"] for c in clusters}

    def nearest(pt):
        best, best_d = None, None
        for n in nodes:
            d = dist_point_box(pt, n["box"])
            if best_d is None or d < best_d or (d == best_d and box_area(n["box"]) < box_area(best["box"])):
                best, best_d = n, d
        return best["id"] if best is not None and best_d <= END_SNAP_PX else None

    unmapped = 0
    for e in edges:
        first, last = e["polys"][0][0], e["polys"][-1][-1]
        geo = (nearest(first), nearest(last))
        if e["src"] is None:
            e["src"], e["dst"] = geo
            e["mapped_by"] = "geometry"
            if not e["invisible"] and (geo[0] is None or geo[1] is None):
                unmapped += 1
        ends = {e["src"], e["dst"]}
        if e["src"] in cluster_ids or e["src"] not in node_ids:
            ends.add(geo[0])
        if e["dst"] in cluster_ids or e["dst"] not in node_ids:
            ends.add(geo[1])
        e["ends"] = ends - {None}
        e["segs"] = [s for poly in e["polys"] for s in segments_of(poly)]
        e["box"] = bbox_of([pt for poly in e["polys"] for pt in poly])
    if unmapped:
        warnings.append("%d edge(s) have an end that no node box is near" % unmapped)
    # --- edge labels: by data-id when present, else by document order of all edge paths
    by_raw = {e["raw"]: e for e in edges}
    groups = [g for g in S.elements("g") if "edgeLabel" in _classes(g)]
    for i, g in enumerate(groups):
        box = None
        for fo in g.iter():
            if _local(fo.tag) == "foreignObject":
                box = box_union(box, S.fo_box(fo))
        text = _text_of(g)
        if box is None:
            for t in g.iter():
                if _local(t.tag) == "text" and _text_of(t):
                    box = box_union(box, S.text_box_estimate(t))
        if box is None or not text:
            continue
        owner = None
        did = next((d.get("data-id") for d in g.iter() if d.get("data-id")), None)
        if did is not None:
            owner = by_raw.get(did)
        elif len(groups) == len(edges):
            owner = edges[i]
        labels.append({"text": text[:60], "box": box, "edge": owner})
    visible = [e for e in edges if not e["invisible"]]
    _edge_display_names(visible)
    labels = [lab for lab in labels if lab["edge"] is None or not lab["edge"]["invisible"]]
    orphans = sum(1 for lab in labels if lab["edge"] is None)
    if orphans:
        warnings.append("%d edge label(s) could not be matched to their edge" % orphans)
    return nodes, clusters, visible, labels


def _graph_metrics(S: _Svg, measure: Optional[dict], warnings: list) -> dict:
    nodes, clusters, edges, labels = _extract_graph(S, warnings)
    by_id = {}
    for n in nodes:
        by_id.setdefault(n["id"], n)
    # Painted title extents from the browser replace the reserved boxes for the strike test;
    # the reserved box then only decides near misses.
    if measure:
        painted = {t.get("id"): t for t in measure.get("titles", []) if t.get("bbox")}
        for c in clusters:
            t = painted.get(c["raw_id"])
            if t and c["title"] is not None:
                x, y, w, h = t["bbox"]
                if w > 0 and h > 0:
                    c["title"] = (x, y, x + w, y + h)
    # crossings
    crossing_pairs = []
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            a, b = edges[i], edges[j]
            if not boxes_touch(a["box"], b["box"]):
                continue
            shared = a["ends"] & b["ends"]
            keep = []
            for p in polyline_intersections(a["segs"], b["segs"]):
                if any(point_in_box(p, box_grow(by_id[s]["box"], SHARED_END_MARGIN_PX))
                       for s in shared if s in by_id):
                    continue
                keep.append(p)
            for p in dedupe_points(keep):
                crossing_pairs.append([a["name"], b["name"], round(p[0], 1), round(p[1], 1)])
    # edges through nodes other than their ends
    through = []
    for e in edges:
        for n in nodes:
            if n["id"] in e["ends"] or len(n["hull"]) < 3:
                continue
            if not boxes_touch(e["box"], n["box"]):
                continue
            run, perpendicular = penetration(e["segs"], n["hull"], n["box"])
            if run >= THROUGH_MIN_RUN_PX:
                through.append({"edge": e["name"], "node": n["id"], "depth_px": round(run, 1),
                                "perpendicular_px": round(perpendicular, 1)})
    # edges through group titles
    titles = []
    for c in clusters:
        if c["title"] is None:
            continue
        strike_box = box_grow(c["title"], -1.0)
        near_box = box_grow(c["title_fo"] or c["title"], TITLE_NEAR_MARGIN_PX)
        for e in edges:
            inside = length_in_box(e["segs"], strike_box)
            if inside >= TITLE_MIN_INSIDE_PX:
                titles.append({"edge": e["name"], "title": c["title_text"][:60], "cluster": c["id"],
                               "near_miss": False, "inside_px": round(inside, 1)})
            elif length_in_box(e["segs"], near_box) >= TITLE_MIN_INSIDE_PX:
                titles.append({"edge": e["name"], "title": c["title_text"][:60], "cluster": c["id"],
                               "near_miss": True, "inside_px": 0.0})
    # label overlaps: label-label, label-node, label-title, title-node; and edges through labels.
    # A node is measured by its outline, not its box: a diamond leaves the box corners empty.
    def node_overlap(box, n):
        if box_overlap_area(box, n["box"]) <= OVERLAP_MIN_AREA_PX2:
            return 0.0
        return box_hull_overlap_area(box, n["hull"])

    overlaps, through_labels = [], []
    for li, lab in enumerate(labels):
        lb = box_grow(lab["box"], -1.0)
        for n in nodes:
            area = node_overlap(lb, n)
            if area > OVERLAP_MIN_AREA_PX2:
                overlaps.append({"a": "label:" + lab["text"], "b": "node:" + n["id"],
                                 "area_px": round(area, 1), "kind": "label-node"})
        for lj in range(li + 1, len(labels)):
            area = box_overlap_area(lb, box_grow(labels[lj]["box"], -1.0))
            if area > OVERLAP_MIN_AREA_PX2:
                overlaps.append({"a": "label:" + lab["text"], "b": "label:" + labels[lj]["text"],
                                 "area_px": round(area, 1), "kind": "label-label"})
        for c in clusters:
            if c["title"] is not None:
                area = box_overlap_area(lb, c["title"])
                if area > OVERLAP_MIN_AREA_PX2:
                    overlaps.append({"a": "label:" + lab["text"], "b": "title:" + c["title_text"][:60],
                                     "area_px": round(area, 1), "kind": "label-title"})
        if lab["edge"] is None:
            continue  # owner unknown: its own edge cannot be told apart from another
        for e in edges:
            if lab["edge"] is e:
                continue
            inside = length_in_box(e["segs"], box_grow(lab["box"], -2.0))
            if inside >= EDGE_IN_LABEL_MIN_PX:
                through_labels.append({"edge": e["name"], "label": lab["text"],
                                       "inside_px": round(inside, 1)})
    for c in clusters:
        if c["title"] is None:
            continue
        for n in nodes:
            area = node_overlap(box_grow(c["title"], -1.0), n)
            if area > OVERLAP_MIN_AREA_PX2:
                overlaps.append({"a": "title:" + c["title_text"][:60], "b": "node:" + n["id"],
                                 "area_px": round(area, 1), "kind": "title-node"})
    # duplicate edges: more than one edge per unordered node pair
    pairs = {}
    for e in edges:
        if e["src"] and e["dst"]:
            pairs.setdefault(tuple(sorted((e["src"], e["dst"]))), []).append(e["name"])
    duplicates = [{"pair": list(k), "edges": v} for k, v in pairs.items() if len(v) > 1]
    real = [n for n in nodes if not n["pseudo"]]
    return {"nodes": len(real), "edges": len(edges), "crossings": len(crossing_pairs),
            "crossing_pairs": crossing_pairs, "edges_through_nodes": through,
            "title_crossings": titles, "edges_through_labels": through_labels,
            "label_overlaps": overlaps, "duplicate_edges": duplicates, "font_px": S.css_font_px}


# ----------------------------------------------------------------------------- sequence figures


def _measured_texts(measure: Optional[dict], kind: str) -> dict:
    """{index among the root's <text> elements: measured label} for measured SVG text of *kind*."""
    out = {}
    for m in (measure or {}).get("labels", []):
        if m.get("kind") == kind and m.get("el", "text") == "text" and isinstance(m.get("n"), int) \
                and m.get("bbox"):
            out[m["n"]] = m
    return out


def _lifeline_label_crossings(S: _Svg, lifelines: list, measure: Optional[dict],
                              warnings: list) -> list:
    """Message labels that a lifeline other than the message's own ends runs through.

    A message's label is the run of `messageText` elements that precede its line in document
    order (one per printed line). Its ends are the `data-from` and `data-to` of the line (11.x,
    12.x), else the lifelines nearest to its first and last point (10.9). A lifeline strikes a
    label when it runs more than LIFELINE_LABEL_MARGIN_PX inside the label's glyph box, measured
    in the browser when *measure* is given, estimated otherwise.
    """
    if len(lifelines) < 3:
        return []
    index_of = {el: k for k, el in enumerate(S.elements("text"))}
    measured = _measured_texts(measure, "message")

    def label_box(t):
        m = measured.get(index_of.get(t))
        if m:
            x, y, w, h = m["bbox"]
            return (x, y, x + w, y + h)
        return S.text_box_estimate(t)

    def nearest(x):
        best = min(lifelines, key=lambda life: abs(life[0] - x))
        return best[1] if abs(best[0] - x) <= MESSAGE_END_SNAP_PX else None

    messages, pending = [], []
    for el in S.order:
        tag, cl = _local(el.tag), _classes(el)
        if tag == "text" and "messageText" in cl:
            pending.append(el)
        elif tag in ("line", "path") and any(c.startswith("messageLine") for c in cl):
            messages.append((el, pending))
            pending = []
    out, unmapped = [], 0
    for el, texts in messages:
        if not texts:
            continue
        src, dst = el.get("data-from"), el.get("data-to")
        if not (src and dst):
            m = S.abs.get(el, IDENT)
            if _local(el.tag) == "line":
                p = mat_apply(m, float(el.get("x1") or 0), float(el.get("y1") or 0))
                q = mat_apply(m, float(el.get("x2") or 0), float(el.get("y2") or 0))
            else:
                try:
                    polys = path_polylines(el.get("d"))
                except ValueError:
                    polys = []
                if not polys:
                    unmapped += 1
                    continue
                p, q = mat_apply(m, *polys[0][0]), mat_apply(m, *polys[-1][-1])
            src, dst = nearest(p[0]), nearest(q[0])
        if src is None or dst is None:
            unmapped += 1
            continue
        hit = []
        for t in texts:
            x0, y0, x1, y1 = label_box(t)
            for lx, name, ly0, ly1 in lifelines:
                if name in (src, dst) or name in hit:
                    continue
                if x0 + LIFELINE_LABEL_MARGIN_PX < lx < x1 - LIFELINE_LABEL_MARGIN_PX \
                        and y1 > ly0 and y0 < ly1:
                    hit.append(name)
        if hit:
            out.append({"message": " ".join(_text_of(t) for t in texts)[:80], "from": src,
                        "to": dst, "lifelines": hit})
    if unmapped:
        warnings.append("%d message(s) have an end that no lifeline is near" % unmapped)
    return out


def _sequence_metrics(S: _Svg, measure: Optional[dict], warnings: list) -> dict:
    lifelines = []
    for ln in S.elements("line"):
        if not (ln.get("data-et") == "life-line" or re.match(r"^actor\d+$", ln.get("id") or "")):
            continue
        name = ln.get("data-id") or ln.get("name")
        if not name:
            par = S.parent.get(ln)
            if par is not None:
                for d in par.iter():
                    if d is not ln and d.get("name"):
                        name = d.get("name")
                        break
        x, y0 = mat_apply(S.abs[ln], float(ln.get("x1") or 0), float(ln.get("y1") or 0))
        y1 = mat_apply(S.abs[ln], float(ln.get("x2") or 0), float(ln.get("y2") or 0))[1]
        lifelines.append((x, name or ln.get("id") or "?", min(y0, y1), max(y0, y1)))
    lifelines.sort()
    gaps = [round(lifelines[i + 1][0] - lifelines[i][0], 1) for i in range(len(lifelines) - 1)]
    messages = [el for el in S.order
                if _local(el.tag) in ("line", "path")
                and any(c.startswith("messageLine") for c in _classes(el))]
    texts = [t for t in S.elements("text") if "messageText" in _classes(t)]
    sizes = [_font_px_of(t) for t in texts]
    sizes = [s for s in sizes if s]
    font = max(set(sizes), key=sizes.count) if sizes else S.css_font_px
    widest, widest_text, source = 0.0, "", "estimate"
    measured = [m for m in (measure or {}).get("labels", []) if m.get("kind") == "message"]
    if measured:
        source = "measure"
        for m in measured:
            if m["bbox"][2] > widest:
                widest, widest_text = m["bbox"][2], m.get("text", "")
    else:
        for t in texts:
            s = _text_of(t)
            w = estimate_text_width(s, _font_px_of(t) or font)
            if w > widest:
                widest, widest_text = w, s
    ordered = sorted(gaps)
    median = ordered[len(ordered) // 2] if len(ordered) % 2 else (
        (ordered[len(ordered) // 2 - 1] + ordered[len(ordered) // 2]) / 2.0 if ordered else 0.0)
    struck = _lifeline_label_crossings(S, lifelines, measure, warnings)
    seq = {"participants": [life[1] for life in lifelines], "lifeline_gaps": gaps,
           "median_gap_px": round(median, 1), "widest_message_px": round(widest, 1),
           "widest_message": widest_text[:80], "width_source": source,
           "messages": len(messages), "lifeline_through_label": struck,
           "lifeline_label_crossings": sum(len(s["lifelines"]) for s in struck)}
    return {"nodes": len(lifelines), "edges": len(messages), "sequence": seq, "font_px": font}


# ----------------------------------------------------------------------------- gantt figures


def _gantt_metrics(S: _Svg, measure: Optional[dict], warnings: list) -> dict:
    vx, _, vw, _ = S.viewbox
    right_edge = vx + vw
    bars = {}
    for r in S.elements("rect"):
        cl = _classes(r)
        if "task" in cl and "section" not in cl:
            pts = S.shape_points(r)
            if pts:
                bars[S.strip_prefix(r.get("id") or "bar%d" % len(bars))] = bbox_of(pts)
    grid = next((g for g in S.elements("g") if "grid" in _classes(g)), None)
    left_pad = S.abs[grid][4] if grid is not None else 0.0
    measured = {}
    for m in (measure or {}).get("labels", []):
        if m.get("kind") == "task" and m.get("id"):
            measured[m["id"]] = m["bbox"]
    sizes, outside, overflow = [], 0, []
    for t in S.elements("text"):
        cl = _classes(t)
        if not any(c.startswith("taskText") for c in cl):
            continue
        fs = _font_px_of(t) or 11.0
        sizes.append(fs)
        text = _text_of(t)
        raw_id = t.get("id") or ""
        own = S.strip_prefix(raw_id)[:-5] if raw_id.endswith("-text") else None
        x, y = mat_apply(S.abs[t], float(t.get("x") or 0), float(t.get("y") or 0))
        if raw_id in measured:
            bx, by, bw, bh = measured[raw_id]
            box = (bx, by, bx + bw, by + bh)
        else:
            mw = next((float(c[6:]) for c in cl if c.startswith("width-")), None)
            w = mw if mw is not None else estimate_text_width(text, fs)
            if any(c.startswith("taskTextOutsideRight") for c in cl):
                box = (x, y - fs, x + w, y)
            elif any(c.startswith("taskTextOutsideLeft") for c in cl):
                box = (x - w, y - fs, x, y)
            else:
                box = (x - w / 2, y - fs, x + w / 2, y)
        if any(c.startswith("taskTextOutside") for c in cl):
            outside += 1
        if box[2] > right_edge + GANTT_EDGE_TOL_PX:
            overflow.append({"label": text[:80], "reason": "past the right edge",
                             "px": round(box[2] - right_edge, 1)})
        elif box[0] < left_pad - GANTT_EDGE_TOL_PX:
            overflow.append({"label": text[:80], "reason": "into the section column",
                             "px": round(left_pad - box[0], 1)})
        for bid, b in bars.items():
            if bid == own:
                continue
            area = box_overlap_area(box_grow(box, -1.0), b)
            if area > OVERLAP_MIN_AREA_PX2:
                overflow.append({"label": text[:80], "reason": "over the bar " + bid,
                                 "px": round(area, 1)})
    section_overflow = []
    msec = {m.get("text"): m["bbox"] for m in (measure or {}).get("labels", [])
            if m.get("kind") == "section" and m.get("bbox")}
    for t in S.elements("text"):
        if not any(c.startswith("sectionTitle") for c in _classes(t)):
            continue
        text = _text_of(t)
        x = mat_apply(S.abs[t], float(t.get("x") or 0), 0)[0]
        if text in msec:
            right = msec[text][0] + msec[text][2]
        else:
            right = x + estimate_text_width(text, _font_px_of(t) or 11.0)
        if grid is not None and right > left_pad + GANTT_EDGE_TOL_PX:
            section_overflow.append({"label": text[:80], "px": round(right - left_pad, 1)})
    today = any("today" in _classes(el) for el in S.elements("line"))
    font = max(set(sizes), key=sizes.count) if sizes else 11.0
    g = {"bars": len(bars), "labels_outside": outside, "overflow": overflow,
         "section_overflow": section_overflow, "today_marker": today,
         "chart_width_px": round(vw, 1)}
    return {"nodes": len(bars), "edges": 0, "gantt": g, "font_px": font}


# ----------------------------------------------------------------------------- text contrast

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


# ----------------------------------------------------------------------------- public API


def _empty_metrics() -> dict:
    return {"diagram": "", "width": 0.0, "height": 0.0, "nodes": 0, "edges": 0, "crossings": 0,
            "crossing_pairs": [], "edges_through_nodes": [], "title_crossings": [],
            "edges_through_labels": [], "label_overlaps": [], "clipped_labels": [],
            "duplicate_edges": [], "font_px": 0.0,
            "effective_font_px": 0.0, "smallest_font_px": 0.0, "smallest_text": "",
            "smallest_effective_font_px": 0.0, "geometry": "not modelled", "sequence": {},
            "gantt": {}, "contrast": {"page": None, "texts": [], "measured": False},
            "measured": False, "warnings": []}


def _box_clip_tolerance(m: dict) -> float:
    """The overhang allowed past the box of measured label *m*: PAINTED_CLIP_TOL_PX for SVG text
    whose box is the rectangle drawn around it (a note, an actor, a gantt bar), CLIP_TOL_PX for
    the space reserved for an HTML label inside its padded shape."""
    if m.get("el", "text") == "text" and m.get("kind") in PAINTED_BOX_KINDS:
        return PAINTED_CLIP_TOL_PX
    return CLIP_TOL_PX


def _clipped_from_measure(measure: dict) -> list:
    """Texts that run past their reserved box (`clipped_px`, both axes) or past the figure's
    edge (`outside_px`). A gantt bar label past the edge is left to `gantt_overflow`."""
    out = []
    for m in measure.get("labels", []):
        in_box = float(m.get("clipped_px") or 0.0) if m.get("box") else 0.0
        outside = 0.0 if m.get("kind") == "task" else float(m.get("outside_px") or 0.0)
        past = [(over, where) for over, where, tol in (
            (in_box, "its box", _box_clip_tolerance(m)),
            (outside, "the figure's edge", CLIP_TOL_PX)) if over > tol]
        if past:
            over, where = max(past, key=lambda p: p[0])
            out.append({"label": (m.get("text") or "")[:80], "overflow_px": round(over, 1),
                        "kind": m.get("kind", ""), "where": where})
    return out


def _line_anchor(S: _Svg, texts: list, m: dict) -> Optional[tuple]:
    """(parent, x, y, dy) of the SVG `<text>` that a measured label is, or None.

    `dy` is that of the text's first `<tspan>`, else its own. A label that is no `<text>`, an
    index past the SVG's texts, a text that is not the one measured and a text with no `x` or `y`
    give None.
    """
    n = m.get("n")
    if m.get("el", "text") != "text" or not isinstance(n, int) or not 0 <= n < len(texts):
        return None
    t = texts[n]
    painted = re.sub(r"\s+", " ", "".join(t.itertext())).strip()[:120].strip()
    if painted != (m.get("text") or "").strip():
        return None  # measure_text.mjs keeps 120 characters of the collapsed text
    if t.get("x") is None or t.get("y") is None:
        return None
    span = next((c for c in t if _local(c.tag) == "tspan"), None)
    return S.parent.get(t), t.get("x"), t.get("y"), (span if span is not None else t).get("dy")


def _painted_label_overlaps(S: _Svg, measure: dict) -> list:
    """label-label overlaps of the painted text boxes `measure_text.mjs` reports.

    For the kinds whose own anatomy is not read here, and for sequence figures. A rotated text
    is left out: its box holds far more than its glyphs (a gitGraph commit id). Two lines of one
    label are not compared: sibling `<text>` elements at one anchor with different `dy`. Mermaid
    draws the lines of a participant name 16 px apart, and their painted boxes are 19 px high.
    """
    labs = [m for m in measure.get("labels", [])
            if m.get("bbox") and m.get("fg", "") is not None and not m.get("rotated")
            and (m.get("text") or "").strip()]
    boxes = [box_grow((x, y, x + w, y + h), -1.0) for x, y, w, h in (m["bbox"] for m in labs)]
    texts = list(S.elements("text"))
    anchors = [_line_anchor(S, texts, m) for m in labs]
    out = []
    for i in range(len(labs)):
        for j in range(i + 1, len(labs)):
            a, b = anchors[i], anchors[j]
            if a and b and a[0] is not None and a[:3] == b[:3] and a[3] != b[3]:
                continue  # two lines of one label
            area = box_overlap_area(boxes[i], boxes[j])
            if area > OVERLAP_MIN_AREA_PX2:
                out.append({"a": "label:" + labs[i]["text"][:60], "b": "label:" + labs[j]["text"][:60],
                            "area_px": round(area, 1), "kind": "label-label"})
    return out


def _legibility_exempt(notation: dict) -> frozenset:
    """The classes of `thresholds.legibility_exempt_classes`; ValueError when it is no list of
    class names."""
    classes = notation["thresholds"].get("legibility_exempt_classes")
    if not isinstance(classes, list) or not all(isinstance(c, str) and c for c in classes):
        raise ValueError("notation thresholds.legibility_exempt_classes %r is not a list of class "
                         "names" % (classes,))
    return frozenset(classes)


def _smallest_text(measure: dict, exempt: frozenset) -> Optional[dict]:
    """The drawn text of the smallest size that a reader must read, or None.

    Text that is not drawn (`fg` null) and text of a class in *exempt* are left out. The
    `autonumber` digits are such a class: drawn at a fixed 12 px in their marker circle, they
    read at 8.6 px in the 1250 px sequence figures of the references, whose message text reads
    at 11.5 px (measured 2026-10-03).
    """
    best = None
    for m in measure.get("labels", []):
        size = float(m.get("font_px") or 0.0)
        if size <= 0 or m.get("fg", "") is None or not (m.get("text") or "").strip():
            continue
        if exempt & set((m.get("cls") or "").split()):
            continue
        if best is None or size < float(best["font_px"]):
            best = m
    return best


def analyze_svg(svg_text: str, column_px: int = 900, measure: Optional[dict] = None,
                author: Optional[dict] = None, notation: Optional[dict] = None) -> dict:
    """Return the metrics of METRIC_KEYS for one rendered figure.

    *measure* is the JSON `measure_text.mjs` prints for the same SVG. Without it, title boxes
    are the boxes mermaid reserved, `<text>` widths are estimates, `clipped_labels` stays
    empty with `measured` False, and contrast is not measured.
    *author* is `author_colours()` of the figure source; it scopes each measured text `author`
    or `theme`. Without it every text is scoped `unknown`, which `evaluate` does not gate.
    *notation* gives the legibility exemptions; `assets/notation.json` when None.
    Raises ValueError when the text is not an SVG this module can read, or when the notation's
    `thresholds.legibility_exempt_classes` is not a list of class names.
    """
    try:
        S = _Svg(svg_text)
    except ET.ParseError as exc:
        raise ValueError("the SVG does not parse: %s" % exc) from exc
    out = _empty_metrics()
    warnings = out["warnings"]
    if S.removed_controls:
        warnings.append("%d control character(s) removed before parsing; a label holds an entity "
                        "such as #1; that mermaid wrote as a raw control character"
                        % S.removed_controls)
    out["diagram"] = S.kind
    _, _, width, height = S.viewbox
    out["width"], out["height"] = round(width, 1), round(height, 1)
    kind = S.kind.lower()
    geometry = "modelled"
    if kind.startswith("flowchart") or kind.startswith("state") or kind in (
            "class", "classdiagram", "er", "erdiagram", "requirement"):
        res = _graph_metrics(S, measure, warnings)
        if kind in ("er", "erdiagram", "requirement") and res["nodes"] == 0:
            warnings.append("diagram kind %s is only partly modelled" % S.kind)
            geometry = "partly modelled"
    elif kind == "sequence":
        res = _sequence_metrics(S, measure, warnings)
    elif kind == "gantt":
        res = _gantt_metrics(S, measure, warnings)
    else:
        res = {"font_px": S.css_font_px}
        warnings.append("diagram kind %r is not modelled: size, font and the overlap of its "
                        "measured texts only" % (S.kind or "?"))
        geometry = "not modelled"
    out.update(res)
    out["geometry"] = geometry
    smallest = None
    if measure:
        out["measured"] = True
        if float(measure.get("font_px") or 0) > 0:
            out["font_px"] = float(measure["font_px"])
        out["clipped_labels"] = _clipped_from_measure(measure)
        out["contrast"] = _contrast_metrics(S, measure, author)
        if author is None and out["contrast"]["texts"]:
            warnings.append("no figure source given: text contrast is reported, not gated")
        if kind == "sequence" or geometry == "not modelled":
            out["label_overlaps"] = list(out["label_overlaps"]) + _painted_label_overlaps(S, measure)
        n = notation if notation is not None else mm.load_notation()
        smallest = _smallest_text(measure, _legibility_exempt(n))
    if width <= 0:
        warnings.append("the SVG has no viewBox; effective font equals the font size")
    scale = min(1.0, column_px / width) if width > 0 else 1.0
    out["font_px"] = round(float(out["font_px"]), 2)
    out["effective_font_px"] = round(out["font_px"] * scale, 2)
    if smallest is not None:
        out["smallest_font_px"] = round(float(smallest["font_px"]), 2)
        out["smallest_text"] = (smallest.get("text") or "")[:60]
    else:
        out["smallest_font_px"] = out["font_px"]
    out["smallest_effective_font_px"] = round(out["smallest_font_px"] * scale, 2)
    return out


def evaluate(metrics: dict, notation: Optional[dict] = None) -> list:
    """Compare *metrics* with the thresholds of `notation.json`.

    Returns findings as dicts: `{"check": str, "severity": "fail" | "warn" | "info",
    "message": str}`, fails first. `check` is one of CHECKS. Only `fail` fails a figure;
    `info` reports a measurement that gates nothing (text contrast in the viewer's theme).
    Raises ValueError when `thresholds.contrast_scope` is neither `author_set` nor `all`.
    """
    n = notation if notation is not None else mm.load_notation()
    th = n["thresholds"]
    scope_rule = th["contrast_scope"]
    if scope_rule not in ("author_set", "all"):
        raise ValueError("notation thresholds.contrast_scope %r is neither author_set nor all"
                         % (scope_rule,))
    out = []

    def add(check, severity, message):
        out.append({"check": check, "severity": severity, "message": message})

    crossings = int(metrics.get("crossings") or 0)
    if crossings > th["max_crossings"]:
        add("crossings", "fail", "%d edge crossings, more than %d" % (crossings, th["max_crossings"]))
    elif crossings:
        add("crossings", "warn", "%d edge crossing(s); allowed %d, aim at 0"
            % (crossings, th["max_crossings"]))

    deep = [t for t in metrics.get("edges_through_nodes", [])
            if t["depth_px"] >= th["through_node_min_depth_px"]]
    shallow = [t for t in metrics.get("edges_through_nodes", [])
               if t["depth_px"] < th["through_node_min_depth_px"]]
    severity = "fail" if len(deep) > th["max_edges_through_nodes"] else "warn"
    for t in deep:
        add("edges_through_nodes", severity, "edge %s runs %.1f px inside node %s"
            % (t["edge"], t["depth_px"], t["node"]))
    for t in shallow:
        add("edges_through_nodes", "warn", "edge %s grazes node %s (%.1f px inside)"
            % (t["edge"], t["node"], t["depth_px"]))

    strikes = [t for t in metrics.get("title_crossings", []) if not t.get("near_miss")]
    severity = "fail" if len(strikes) > th["max_title_crossings"] else "warn"
    for t in strikes:
        add("title_crossings", severity, "edge %s crosses the title %r" % (t["edge"], t["title"]))

    # Edges through labels. Metrics stored before `edges_through_labels` existed (2026-10-03)
    # hold such an edge as a `label_overlaps` entry of kind edge-label: {"a": "edge:<id>",
    # "b": "label:<text>", "area_px": <length inside>}. The check keeps the threshold those
    # entries had, `max_label_overlaps`: TASK R7.6 allows 0 of either.
    stored = metrics.get("label_overlaps", [])
    through_labels = list(metrics.get("edges_through_labels", [])) + [
        {"edge": t["a"].partition(":")[2], "label": t["b"].partition(":")[2],
         "inside_px": t["area_px"]} for t in stored if t.get("kind") == "edge-label"]
    severity = "fail" if len(through_labels) > th["max_label_overlaps"] else "warn"
    for t in through_labels:
        add("edges_through_labels", severity, "edge %s runs %.1f px inside the label %r"
            % (t["edge"], float(t["inside_px"]), t["label"]))

    overlaps = [t for t in stored if t.get("kind") != "edge-label"]
    severity = "fail" if len(overlaps) > th["max_label_overlaps"] else "warn"
    for t in overlaps:
        add("label_overlaps", severity, "%s overlaps %s (%s px)" % (t["a"], t["b"], t["area_px"]))

    clipped = metrics.get("clipped_labels", [])
    severity = "fail" if len(clipped) > th["max_clipped_labels"] else "warn"
    for t in clipped:
        add("clipped_labels", severity, "text %r runs %.1f px past %s"
            % (t["label"], t["overflow_px"], t.get("where") or "its box"))
    if not metrics.get("measured"):
        add("clipped_labels", "warn", "text was not measured in a browser; clipped labels unchecked")

    # Legibility gates the smallest text a reader must read; metrics written before that key
    # existed fall back to the most common size.
    eff = float(metrics.get("effective_font_px") or 0)
    low = metrics.get("smallest_effective_font_px")
    smallest = float(low) if low else eff
    floor = n["min_effective_font_px"]
    if smallest < floor:
        named = metrics.get("smallest_text") or ""
        if named and smallest < eff:
            add("legibility", "fail", "text %r renders at %.1f px in a %d px column (figure %.0f px "
                "wide, font %.1f px; most text %.1f px); the floor is %s px"
                % (named, smallest, n["column_px"], float(metrics.get("width") or 0),
                   float(metrics.get("smallest_font_px") or 0), eff, floor))
        else:
            add("legibility", "fail", "text renders at %.1f px in a %d px column (figure %.0f px "
                "wide, font %.1f px); the floor is %s px"
                % (smallest, n["column_px"], float(metrics.get("width") or 0),
                   float(metrics.get("font_px") or 0), floor))

    contrast = metrics.get("contrast") or {}
    cmin = float(n["contrast_min"])
    reported = {}
    for t in contrast.get("texts") or []:
        ratio = t.get("ratio")
        gated = scope_rule == "all" or t.get("scope") == "author"
        if t.get("uncertain"):
            # The ratio was taken against the colour under a gradient or pattern fill, which
            # the reader never sees: it can neither pass nor be trusted.
            add("contrast", "fail" if gated else "warn",
                "%s text %r: contrast not measured, it is drawn on a gradient or pattern "
                "backdrop%s" % (t.get("kind") or "other", t.get("text", ""),
                                "; the figure sets its colours" if gated else ""))
            continue
        if ratio is None or float(ratio) >= cmin:
            continue
        if gated:
            add("contrast", "fail", "%s text %r measures %.2f:1 (%s on %s); the figure sets its "
                "colours, and the minimum is %s:1" % (t.get("kind") or "other", t.get("text", ""),
                                                      float(ratio), t.get("fg"), t.get("bg"), cmin))
        else:
            reported.setdefault(t.get("kind") or "other", []).append(t)
    for kind in sorted(reported):
        items = reported[kind]
        low = min(items, key=lambda x: float(x["ratio"]))
        add("contrast", "info", "%d %s text(s) in the viewer's theme colours below %s:1, lowest "
            "%.2f:1 (%r, %s on %s); reported, not gated"
            % (len(items), kind, cmin, float(low["ratio"]), low.get("text", ""), low.get("fg"),
               low.get("bg")))
    if metrics.get("measured") and not contrast.get("measured"):
        add("contrast", "warn", "text colours were not measured; contrast unchecked")
    elif not metrics.get("measured"):
        add("contrast", "warn", "text was not measured in a browser; contrast unchecked")

    for t in metrics.get("title_crossings", []):
        if t.get("near_miss"):
            add("title_near_miss", "warn", "edge %s passes within the box reserved for the title %r"
                % (t["edge"], t["title"]))

    for d in metrics.get("duplicate_edges", []):
        add("duplicate_edges", "warn", "%d edges join %s and %s: %s"
            % (len(d["edges"]), d["pair"][0], d["pair"][1], ", ".join(d["edges"])))

    seq = metrics.get("sequence") or {}
    gaps = seq.get("lifeline_gaps") or []
    if len(gaps) >= 2:
        ordered = sorted(gaps)
        k = len(ordered)
        median = ordered[k // 2] if k % 2 else (ordered[k // 2 - 1] + ordered[k // 2]) / 2.0
        ratio = float(th["max_lifeline_gap_ratio"])
        names = seq.get("participants") or []
        for i, g in enumerate(gaps):
            if median > 0 and g > ratio * median:
                pair = ("%s and %s" % (names[i], names[i + 1])) if len(names) > i + 1 else "#%d" % i
                add("lifeline_gap", "warn", "the gap between %s is %.0f px, %.1fx the median %.0f px; "
                    "a long message label widens it" % (pair, g, g / median, median))
    for s in seq.get("lifeline_through_label") or []:
        add("lifeline_through_label", "warn", "the lifeline of %s runs through the label %r of "
            "%s -> %s; another participant order or a shorter label may avoid it"
            % (", ".join(s["lifelines"]), s["message"], s["from"], s["to"]))

    gantt = metrics.get("gantt") or {}
    for o in gantt.get("overflow", []):
        add("gantt_overflow", "fail", "bar label %r runs %s (%s px)" % (o["label"], o["reason"], o["px"]))
    for o in gantt.get("section_overflow", []):
        add("gantt_overflow", "warn", "section title %r runs %s px into the bar area"
            % (o["label"], o["px"]))

    # Metrics written before the key existed come from modelled kinds only.
    geometry = metrics.get("geometry") or "modelled"
    if geometry != "modelled":
        add("geometry", "warn", "geometry not checked: diagram kind %s is %s, so crossings and "
            "edges through nodes and titles are not measured; read the PNG"
            % (metrics.get("diagram") or "?", geometry))

    order = {c: i for i, c in enumerate(CHECKS)}
    rank = {s: i for i, s in enumerate(SEVERITIES)}
    out.sort(key=lambda f: (rank.get(f["severity"], 9), order.get(f["check"], 99)))
    return out


def passes(findings: list) -> bool:
    """True when no finding has severity `fail`."""
    return not any(f.get("severity") == "fail" for f in findings)


def fired(findings: list, check: str) -> bool:
    """True when *check* reports its defect: a `fail` of a GATE_CHECKS check, or any `fail` or
    `warn` of a WARN_CHECKS check. A negative fence names GATE_CHECKS only (TASK R9.4)."""
    severities = ("fail",) if check in GATE_CHECKS else ("fail", "warn")
    return any(f.get("check") == check and f.get("severity") in severities for f in findings)


def main(argv: Optional[list] = None) -> int:
    """Debug entry point: `svg_geometry.py FIG.svg [MEASURE.json] [--source FIG.mmd]` prints
    metrics and findings; `--source` scopes text contrast by the figure's own colours."""
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
        print("svg_geometry.py: %s" % exc, file=sys.stderr)
        return 2
    try:
        svg_text = Path(args[0]).read_text(encoding="utf-8")
        measure = json.loads(Path(args[1]).read_text(encoding="utf-8")) if len(args) > 1 else None
        metrics = analyze_svg(svg_text, column, measure,
                              author_colours(source) if source is not None else None)
    except (OSError, ValueError) as exc:
        print("svg_geometry.py: %s" % exc, file=sys.stderr)
        return 2
    findings = evaluate(metrics)
    print(json.dumps({"metrics": metrics, "findings": findings, "pass": passes(findings)},
                     indent=1, ensure_ascii=False))
    return 0 if passes(findings) else 1


if __name__ == "__main__":
    sys.exit(main())
