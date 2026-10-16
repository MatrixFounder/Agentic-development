"""Plane geometry of the SVG geometry: boxes, segments, polylines, hulls and their
intersections (TASK 125)."""

from __future__ import annotations

import math

from .tolerances import SAMPLE_STEP_PX, DEDUPE_RADIUS_PX, THROUGH_NOISE_PX


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


