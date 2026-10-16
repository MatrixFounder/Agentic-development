"""Gantt figures of the SVG geometry: the metrics of a gantt render (TASK 125)."""

from __future__ import annotations

from typing import Optional

from .tolerances import OVERLAP_MIN_AREA_PX2, GANTT_EDGE_TOL_PX
from .transforms import mat_apply
from .plane import bbox_of, box_grow, box_overlap_area
from .text_estimate import estimate_text_width
from .svg_model import _classes, _text_of, _font_px_of, _Svg


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


