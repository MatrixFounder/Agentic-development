"""Path flattening of the SVG geometry: SVG path data as polylines (TASK 125)."""

from __future__ import annotations

import math
from typing import Optional

from .tolerances import FLATTEN_TOL_PX
from .transforms import _NUM


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


