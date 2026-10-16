"""Sequence figures of the SVG geometry: lifelines and their labels (TASK 125)."""

from __future__ import annotations

import re
from typing import Optional

from .tolerances import MESSAGE_END_SNAP_PX, LIFELINE_LABEL_MARGIN_PX
from .transforms import IDENT, mat_apply
from .flattening import path_polylines
from .text_estimate import estimate_text_width
from .svg_model import _local, _classes, _text_of, _font_px_of, _Svg


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
    """Message labels that a lifeline runs through: under `lifelines` the lifelines of skipped
    participants, under `own` the lifelines of the message's own two ends (TASK 110 R1.1).

    A message's label is the run of `messageText` elements that precede its line in document
    order (one per printed line). Its ends are the `data-from` and `data-to` of the line (11.x,
    12.x), else the lifelines nearest to its first and last point (10.9). A lifeline strikes a
    label when it runs more than LIFELINE_LABEL_MARGIN_PX inside the label's glyph box, measured
    in the browser when *measure* is given, estimated otherwise. A self-message's label sits
    centred on its own lifeline in 10.9.8 and 11.17.2, so that lifeline is not counted.
    """
    if len(lifelines) < 2:
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
        hit, own = [], []
        for t in texts:
            x0, y0, x1, y1 = label_box(t)
            for lx, name, ly0, ly1 in lifelines:
                if name in (src, dst):
                    if src == dst:
                        continue
                    found = own
                else:
                    found = hit
                if name in found:
                    continue
                if x0 + LIFELINE_LABEL_MARGIN_PX < lx < x1 - LIFELINE_LABEL_MARGIN_PX \
                        and y1 > ly0 and y0 < ly1:
                    found.append(name)
        if hit or own:
            out.append({"message": " ".join(_text_of(t) for t in texts)[:80], "from": src,
                        "to": dst, "lifelines": hit, "own": own})
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
           "lifeline_label_crossings": sum(len(s["lifelines"]) for s in struck),
           "lifeline_own_crossings": sum(len(s["own"]) for s in struck)}
    return {"nodes": len(lifelines), "edges": len(messages), "sequence": seq, "font_px": font}


