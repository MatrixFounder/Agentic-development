"""SVG model of the SVG geometry: the parsed SVG tree, its classes, texts and font sizes
(TASK 125)."""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from typing import Optional

from .transforms import IDENT, mat_mul, mat_apply, _NUM, parse_transform
from .flattening import path_polylines
from .plane import bbox_of
from .text_estimate import estimate_text_width


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


