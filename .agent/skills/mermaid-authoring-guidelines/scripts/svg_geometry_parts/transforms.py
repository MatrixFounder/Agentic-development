"""Affine transforms of the SVG geometry: the matrices of SVG `transform` attributes
(TASK 125)."""

from __future__ import annotations

import math
import re
from typing import Optional


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


