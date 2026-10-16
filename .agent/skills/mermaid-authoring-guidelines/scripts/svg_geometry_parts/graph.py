"""Graph figures of the SVG geometry: the nodes, edges, clusters and labels of a render
and their metrics (TASK 125)."""

from __future__ import annotations

import re
from typing import Optional

from .tolerances import (
    SHARED_END_MARGIN_PX, END_SNAP_PX, THROUGH_MIN_RUN_PX, TITLE_MIN_INSIDE_PX,
    TITLE_NEAR_MARGIN_PX, OVERLAP_MIN_AREA_PX2, EDGE_IN_LABEL_MIN_PX)
from .transforms import mat_apply
from .flattening import path_polylines
from .plane import (
    bbox_of, box_union, box_grow, box_area, box_overlap_area, boxes_touch, point_in_box,
    dist_point_box, segments_of, polyline_intersections, length_in_box, convex_hull,
    box_hull_overlap_area, penetration, dedupe_points)
from .svg_model import _local, _classes, _text_of, _Svg


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


