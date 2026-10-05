"""Tests for svg_geometry.py (TASK 108, R7.5, R7.6; PLAN C5).

The fixtures are SVGs that mermaid 10.9.8 and 11.17.2 rendered from `fixtures/fx-*.mmd`;
`fixtures/expected.json` holds the values read off their PNGs one by one. `fx-seq-names` also
keeps the `measure_text.mjs` output of each render (`*.measure.json`). Nothing here starts node
or a browser: the geometry is a function of the committed SVG text. Thresholds come from
`assets/notation.json`; no test restates one.
"""
import json
import math
import sys
import threading
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import mermaid_model as mm  # noqa: E402
import svg_geometry as sg  # noqa: E402

FIXTURES = HERE / "fixtures"
EXPECTED = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
VERSIONS = ("v10", "v11")
NOTATION = mm.load_notation()
TH = NOTATION["thresholds"]

_CACHE = {}


def fixture_svg(name, version):
    return (FIXTURES / ("%s-%s.svg" % (name, version))).read_text(encoding="utf-8")


def fixture_metrics(name, version):
    key = (name, version)
    if key not in _CACHE:
        _CACHE[key] = sg.analyze_svg(fixture_svg(name, version), EXPECTED["column_px"])
    return _CACHE[key]


def checks(findings, severity):
    return sorted(set(f["check"] for f in findings if f["severity"] == severity))


def base_metrics(**over):
    """Metrics of a clean, measured, legible figure; keyword arguments override keys."""
    m = sg._empty_metrics()
    m.update({"diagram": "flowchart-v2", "width": 400.0, "height": 300.0, "font_px": 16.0,
              "effective_font_px": 16.0, "geometry": "modelled", "measured": True,
              "contrast": {"page": "#ffffff", "texts": [], "measured": True}})
    m.update(over)
    return m


def returns_within(test, fn, *args, timeout=5.0):
    """(value, exception) of fn(*args); the test fails when fn has not returned in *timeout* s.

    The call runs in a daemon thread, so a hang fails the test instead of stalling the run.
    """
    box = {}

    def run():
        try:
            box["value"] = fn(*args)
        except Exception as exc:  # noqa: BLE001 - handed back to the test
            box["error"] = exc

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(timeout)
    if worker.is_alive():
        test.fail("%s(%r) did not return within %.0f s" % (fn.__name__, args[:1], timeout))
    return box.get("value"), box.get("error")


def measured_label(text, font_px=16.0, bbox=(10.0, 10.0, 60.0, 20.0), **over):
    """One label as measure_text.mjs prints it: drawn, with a painted box."""
    lab = {"text": text, "kind": "other", "id": "", "owner": "", "el": "text", "cls": "",
           "bbox": list(bbox), "box": None, "clipped_px": 0.0, "font_px": font_px,
           "fg": "#333333", "bg": "#ffffff", "under": []}
    lab.update(over)
    return lab


def measure_of(*labels, font_px=16):
    return {"labels": list(labels), "titles": [], "font_px": font_px, "page": "#ffffff"}


def kind_svg(kind, width=400, height=300):
    """An SVG of a diagram kind with nothing in it but its size."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" id="my-svg" viewBox="0 0 %d %d" '
            'aria-roledescription="%s"><style>#my-svg{font-size:16px;}</style></svg>'
            % (width, height, kind))


# ----------------------------------------------------------------------------- synthetic SVGs


def flowchart_svg(nodes, edges, kind="flowchart-v2"):
    """An SVG in the 11.x flowchart anatomy.

    nodes: {id: (cx, cy, w, h)}; edges: [(data_id, path_d, class, style)].
    """
    out = ['<svg xmlns="http://www.w3.org/2000/svg" id="my-svg" viewBox="0 0 400 300" '
           'aria-roledescription="%s"><style>#my-svg{font-size:16px;}</style><g class="root">' % kind,
           '<g class="edgePaths">']
    for did, d, cls, style in edges:
        out.append('<path d="%s" id="my-svg-%s" class="%s" style="%s" data-edge="true" '
                   'data-id="%s"/>' % (d, did, cls, style, did))
    out.append('</g><g class="edgeLabels"/><g class="nodes">')
    for i, (nid, (cx, cy, w, h)) in enumerate(nodes.items()):
        out.append('<g class="node default" id="my-svg-flowchart-%s-%d" transform="translate(%s, %s)">'
                   '<rect class="basic label-container" x="%s" y="%s" width="%s" height="%s"/></g>'
                   % (nid, i, cx, cy, -w / 2.0, -h / 2.0, w, h))
    out.append("</g></g></svg>")
    return "".join(out)


SOLID = "edge-thickness-normal edge-pattern-solid flowchart-link"


def diamond_svg(text_box, title=False):
    """A flowchart with one rhombus node Q, centre (200, 150) and half-diagonal 80, and one text
    box (x0, y0, x1, y1): an edge label, or with *title* the title of a subgraph."""
    x0, y0, x1, y1 = text_box
    fo = ('<foreignObject x="%s" y="%s" width="%s" height="%s"><div '
          'xmlns="http://www.w3.org/1999/xhtml"><span>yes</span></div></foreignObject>'
          % (x0, y0, x1 - x0, y1 - y0))
    if title:
        text = ('<g class="clusters"><g class="cluster" id="my-svg-G" data-id="G">'
                '<rect x="20" y="20" width="360" height="260"/><g class="cluster-label">%s</g>'
                '</g></g><g class="edgePaths"/><g class="edgeLabels"/>' % fo)
    else:
        text = ('<g class="clusters"/><g class="edgePaths"/>'
                '<g class="edgeLabels"><g class="edgeLabel">%s</g></g>' % fo)
    return ('<svg xmlns="http://www.w3.org/2000/svg" id="my-svg" viewBox="0 0 400 300" '
            'aria-roledescription="flowchart-v2"><style>#my-svg{font-size:16px;}</style>'
            '<g class="root">%s<g class="nodes"><g class="node default" id="my-svg-flowchart-Q-0" '
            'transform="translate(200, 150)"><polygon class="label-container" '
            'points="0,-80 80,0 0,80 -80,0"/></g></g></g></svg>' % text)


def names_svg(groups, group_class=""):
    """A sequence SVG and its measure, one group per name, as mermaid 10.9.8 to 12.1.0 draw a
    participant or actor name: each line a `<text>` at the group's anchor, set apart by the `dy`
    of its `<tspan>`. *groups* is a list of [(line, dy)]; the painted lines are 16 px apart and
    19 px high, so consecutive lines overlap by 3 px."""
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" id="my-svg" viewBox="-50 -10 700 300" '
           'aria-roledescription="sequence"><style>#my-svg{font-size:16px;}</style>']
    labels = []
    for k, lines in enumerate(groups):
        x = 75 + 200 * k
        svg.append('<g class="%s"><rect x="%d" y="0" width="150" height="65" class="actor"/>'
                   % (group_class, x - 75))
        for text, dy in lines:
            svg.append('<text x="%d" y="32.5" class="actor actor-box"><tspan x="%d" dy="%s">%s'
                       '</tspan></text>' % (x, x, dy, text))
            top = 32.5 + float(dy) - 9.5
            labels.append(measured_label(text, kind="actor", n=len(labels), cls="actor actor-box",
                                         bbox=(x - 40.0, top, 80.0, 19.0),
                                         box=[x - 75.0, 0.0, 150.0, 65.0]))
        svg.append("</g>")
    svg.append("</svg>")
    return "".join(svg), measure_of(*labels)


class TestStubShape(unittest.TestCase):
    def test_metric_keys(self):
        for key in ("crossings", "edges_through_nodes", "title_crossings", "effective_font_px"):
            self.assertIn(key, sg.METRIC_KEYS)

    def test_passes_on_no_findings(self):
        self.assertTrue(sg.passes([]))
        self.assertFalse(sg.passes([{"severity": "fail"}]))
        self.assertTrue(sg.passes([{"severity": "warn"}]))


# ----------------------------------------------------------------------------- pure functions


class TestTransforms(unittest.TestCase):
    def assertPoint(self, got, want, places=6):
        self.assertAlmostEqual(got[0], want[0], places=places)
        self.assertAlmostEqual(got[1], want[1], places=places)

    def test_list_applies_right_to_left(self):
        m = sg.parse_transform("translate(10,20) scale(2)")
        self.assertPoint(sg.mat_apply(m, 1, 1), (12, 22))

    def test_rotate_about_a_point(self):
        self.assertPoint(sg.mat_apply(sg.parse_transform("rotate(90)"), 1, 0), (0, 1))
        self.assertPoint(sg.mat_apply(sg.parse_transform("rotate(90, 10, 10)"), 11, 10), (10, 11))

    def test_matrix_and_skew(self):
        self.assertPoint(sg.mat_apply(sg.parse_transform("matrix(1 0 0 1 5 6)"), 0, 0), (5, 6))
        self.assertPoint(sg.mat_apply(sg.parse_transform("skewX(45)"), 0, 10), (10, 10))

    def test_identity_and_empty(self):
        self.assertEqual(sg.parse_transform(None), sg.IDENT)
        self.assertEqual(sg.mat_mul(sg.IDENT, sg.IDENT), sg.IDENT)

    def test_nested_groups_compose_to_the_root(self):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
               '<g transform="translate(10,0)"><g transform="scale(2)">'
               '<rect x="1" y="1" width="2" height="2"/></g></g></svg>')
        S = sg._Svg(svg)
        rect = next(S.elements("rect"))
        self.assertEqual(sg.bbox_of(S.shape_points(rect)), (12.0, 2.0, 16.0, 6.0))


def _bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def _dist_to_polyline(p, poly):
    return min(sg.dist_point_segment(p, poly[i], poly[i + 1]) for i in range(len(poly) - 1))


class TestPathFlattening(unittest.TestCase):
    def test_cubic_stays_within_tolerance(self):
        p = ((0, 0), (0, 100), (100, 100), (100, 0))
        poly = [p[0]] + sg.flatten_cubic(*p, tol=0.3)
        self.assertEqual(poly[-1], p[3])
        worst = max(_dist_to_polyline(_bezier(*p, t=k / 200.0), poly) for k in range(201))
        self.assertLess(worst, 0.5)

    def test_lines_and_close(self):
        self.assertEqual(sg.path_polylines("M0,0 L10,0 H20 V10 Z"),
                         [[(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (20.0, 10.0), (0.0, 0.0)]])

    def test_relative_commands_and_implicit_lineto(self):
        self.assertEqual(sg.path_polylines("m0,0 l10,0 0,10"),
                         [[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]])
        self.assertEqual(sg.path_polylines("M0 0 10 0 10 10"),
                         [[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]])

    def test_subpaths_split(self):
        self.assertEqual(len(sg.path_polylines("M0,0 L1,1 M5,5 L6,6")), 2)

    def test_arc_points_lie_on_the_circle(self):
        poly = sg.path_polylines("M0,0 A10,10 0 0 1 20,0")[0]
        self.assertEqual(poly[-1], (20.0, 0.0))
        for x, y in poly:
            self.assertAlmostEqual(math.hypot(x - 10, y), 10.0, places=6)

    def test_quadratic_apex(self):
        poly = sg.path_polylines("M0,0 Q50,100 100,0")[0]
        apex = max(poly, key=lambda q: q[1])
        self.assertAlmostEqual(apex[1], 50.0, delta=0.5)

    def test_bad_path_data_raises(self):
        with self.assertRaises(ValueError):
            sg.path_polylines("M0,0 L10")
        with self.assertRaises(ValueError):
            sg.path_polylines("M0,0 X10,10")

    def test_numbers_after_closepath_raise_instead_of_hanging(self):
        # RG-06: a closepath takes no numbers; the scanner used to repeat Z forever
        for d in ("M0,0 L10,0 Z 5,5", "M0,0 L10,0 z 5 5 L1,1", "M0,0 L10,0 Z5,5"):
            with self.subTest(d=d):
                _, error = returns_within(self, sg.path_polylines, d)
                self.assertIsInstance(error, ValueError)
        value, error = returns_within(self, sg.path_polylines, "M0,0 L10,0 Z M5,5 6,6")
        self.assertIsNone(error)
        self.assertEqual(len(value), 2)

    def test_an_edge_with_numbers_after_closepath_is_skipped(self):
        svg = flowchart_svg({"a": (50, 50, 40, 20), "b": (350, 50, 40, 20)},
                            [("L_a_b_0", "M70,50 L330,50 Z 5,5", SOLID, "")])
        metrics, error = returns_within(self, sg.analyze_svg, svg, 900)
        self.assertIsNone(error)
        self.assertEqual(metrics["edges"], 0)
        self.assertTrue(any("skipped" in w for w in metrics["warnings"]), metrics["warnings"])


class TestSegmentGeometry(unittest.TestCase):
    def test_proper_crossing(self):
        self.assertEqual(sg.segment_intersection((0, 0), (10, 10), (0, 10), (10, 0)), (5.0, 5.0))

    def test_parallel_and_collinear_are_not_crossings(self):
        self.assertIsNone(sg.segment_intersection((0, 0), (10, 0), (0, 1), (10, 1)))
        self.assertIsNone(sg.segment_intersection((0, 0), (10, 0), (5, 0), (15, 0)))

    def test_disjoint(self):
        self.assertIsNone(sg.segment_intersection((0, 0), (1, 1), (5, 0), (6, -1)))

    def test_touching_end(self):
        self.assertEqual(sg.segment_intersection((0, 0), (10, 0), (5, 0), (5, 10)), (5.0, 0.0))

    def test_clip_length(self):
        self.assertAlmostEqual(sg.clip_length_in_box((-5, 5), (15, 5), (0, 0, 10, 10)), 10.0)
        self.assertEqual(sg.clip_length_in_box((-5, 20), (15, 20), (0, 0, 10, 10)), 0.0)

    def test_hull_and_inside(self):
        hull = sg.convex_hull([(0, 0), (10, 0), (10, 10), (0, 10), (5, 5)])
        self.assertEqual(len(hull), 4)
        self.assertTrue(sg.point_in_convex((5, 5), hull))
        self.assertFalse(sg.point_in_convex((15, 5), hull))

    def test_penetration_run_and_depth(self):
        hull = sg.convex_hull([(0, 0), (40, 0), (40, 40), (0, 40)])
        through = sg.segments_of([(-10, 20), (50, 20)])
        run, depth = sg.penetration(through, hull, (0, 0, 40, 40))
        self.assertAlmostEqual(run, 40 - 2 * sg.THROUGH_NOISE_PX, delta=1.5)
        self.assertAlmostEqual(depth, 20.0, delta=0.6)
        along = sg.segments_of([(-10, 1), (50, 1)])
        run, depth = sg.penetration(along, hull, (0, 0, 40, 40))
        self.assertEqual(run, 0.0)
        self.assertLess(depth, sg.THROUGH_NOISE_PX)

    def test_text_estimate_scales_with_font(self):
        self.assertAlmostEqual(sg.estimate_text_width("ab", 20), 2 * sg.estimate_text_width("ab", 10))
        self.assertGreater(sg.estimate_text_width("ЖЖ", 10), 0)


# ----------------------------------------------------------------------------- committed fixtures


class TestFixtures(unittest.TestCase):
    def test_every_key_present_and_serialisable(self):
        for name in EXPECTED["fixtures"]:
            for v in VERSIONS:
                m = fixture_metrics(name, v)
                self.assertEqual(set(m), set(sg.METRIC_KEYS), "%s %s" % (name, v))
                json.dumps(m)
                self.assertFalse(m["measured"])

    def test_values_match_expected(self):
        for name, entry in EXPECTED["fixtures"].items():
            for v in VERSIONS:
                with self.subTest(fixture=name, version=v):
                    want, m = entry[v], fixture_metrics(name, v)
                    for key in ("diagram", "nodes", "edges", "crossings", "font_px",
                                "effective_font_px"):
                        self.assertEqual(m[key], want[key], key)
                    self.assertAlmostEqual(m["width"], want["width"], places=1)
                    self.assertAlmostEqual(m["height"], want["height"], places=1)
                    self.assertEqual(sorted([t["edge"], t["node"]] for t in m["edges_through_nodes"]),
                                     sorted(want["edges_through_nodes"]))
                    strikes = [t for t in m["title_crossings"] if not t["near_miss"]]
                    self.assertEqual(len(strikes), want["title_crossings"])
                    self.assertEqual(len(m["title_crossings"]) - len(strikes), want["title_near_misses"])
                    self.assertEqual(len(m["label_overlaps"]), want["label_overlaps"])
                    self.assertEqual(len(m["duplicate_edges"]), want["duplicate_edges"])
                    self.assertEqual(m["warnings"], [])

    def test_edge_ends_match_the_source(self):
        for name, entry in EXPECTED["fixtures"].items():
            for v in VERSIONS:
                if "edge_names" not in entry[v]:
                    continue
                with self.subTest(fixture=name, version=v):
                    S = sg._Svg(fixture_svg(name, v))
                    edges = sg._extract_graph(S, [])[2]
                    self.assertEqual(sorted(e["name"] for e in edges), entry[v]["edge_names"])

    def test_clean_tree_has_no_crossing(self):
        for v in VERSIONS:
            m = fixture_metrics("fx-tree", v)
            self.assertEqual(m["crossings"], 0, v)
            self.assertEqual(m["edges_through_nodes"], [], v)

    def test_k33_has_a_crossing(self):
        for v in VERSIONS:
            self.assertGreaterEqual(fixture_metrics("fx-k33", v)["crossings"], 1, v)

    def test_title_case_strikes_the_title(self):
        for v in VERSIONS:
            strikes = [t for t in fixture_metrics("fx-title", v)["title_crossings"] if not t["near_miss"]]
            self.assertGreaterEqual(len(strikes), 1, v)
            self.assertEqual(strikes[0]["title"], "Conversation workers")
            self.assertEqual(strikes[0]["edge"], "CLI->API")

    def test_forced_case_runs_through_a_node(self):
        for v in VERSIONS:
            deep = [t for t in fixture_metrics("fx-through", v)["edges_through_nodes"]
                    if t["depth_px"] >= TH["through_node_min_depth_px"]]
            self.assertGreaterEqual(len(deep), 1, v)
            self.assertEqual((deep[0]["edge"], deep[0]["node"]), ("A->B", "X"))

    def test_sequence_gaps(self):
        for name in ("fx-seq-long", "fx-seq-skip", "fx-seq-own"):
            for v in VERSIONS:
                with self.subTest(fixture=name, version=v):
                    want = EXPECTED["fixtures"][name][v]["sequence"]
                    seq = fixture_metrics(name, v)["sequence"]
                    self.assertEqual(seq["participants"], want["participants"])
                    self.assertEqual(seq["lifeline_gaps"], want["lifeline_gaps"])
                    self.assertAlmostEqual(seq["widest_message_px"], want["widest_message_px"],
                                           places=1)
                    self.assertEqual(seq["lifeline_through_label"], want["lifeline_through_label"])
                    self.assertEqual(seq["lifeline_label_crossings"],
                                     sum(len(x["lifelines"]) for x in want["lifeline_through_label"]))
                    self.assertEqual(seq["lifeline_own_crossings"],
                                     sum(len(x["own"]) for x in want["lifeline_through_label"]))

    def test_gantt_bars(self):
        for v in VERSIONS:
            want = EXPECTED["fixtures"]["fx-gantt"][v]["gantt"]
            g = fixture_metrics("fx-gantt", v)["gantt"]
            self.assertEqual(g["bars"], want["bars"])
            self.assertEqual(g["labels_outside"], want["labels_outside"])
            self.assertEqual(len(g["overflow"]), want["overflow"])
            self.assertEqual(g["today_marker"], want["today_marker"])

    def test_state_transitions_attach_by_geometry(self):
        for v in VERSIONS:
            S = sg._Svg(fixture_svg("fx-state", v))
            edges = sg._extract_graph(S, [])[2]
            self.assertTrue(all(e["mapped_by"] == "geometry" for e in edges), v)
            labels = sg._extract_graph(S, [])[3]
            owners = {lab["text"]: lab["edge"]["name"] for lab in labels}
            self.assertEqual(owners["approve"], "Submitted->Approved", v)
            self.assertEqual(owners["revise"], "Rejected->Draft", v)


# ----------------------------------------------------------------------------- verdicts


class TestEvaluate(unittest.TestCase):
    def test_fixture_verdicts(self):
        for name, entry in EXPECTED["fixtures"].items():
            for v in VERSIONS:
                with self.subTest(fixture=name, version=v):
                    findings = sg.evaluate(fixture_metrics(name, v), NOTATION)
                    self.assertEqual(checks(findings, "fail"), entry[v]["fail_checks"])
                    self.assertEqual(checks(findings, "warn"), entry[v]["warn_checks"])

    def test_notation_loaded_by_default(self):
        self.assertEqual(sg.evaluate(base_metrics()), [])

    def test_crossings_threshold(self):
        at = sg.evaluate(base_metrics(crossings=TH["max_crossings"]), NOTATION)
        over = sg.evaluate(base_metrics(crossings=TH["max_crossings"] + 1), NOTATION)
        self.assertEqual(checks(at, "fail"), [])
        self.assertEqual(checks(at, "warn"), ["crossings"])
        self.assertEqual(checks(over, "fail"), ["crossings"])

    def test_through_node_depth_threshold(self):
        limit = TH["through_node_min_depth_px"]
        shallow = sg.evaluate(base_metrics(edges_through_nodes=[
            {"edge": "a->b", "node": "m", "depth_px": limit - 0.1}]), NOTATION)
        deep = sg.evaluate(base_metrics(edges_through_nodes=[
            {"edge": "a->b", "node": "m", "depth_px": limit}]), NOTATION)
        self.assertEqual(checks(shallow, "fail"), [])
        self.assertEqual(checks(shallow, "warn"), ["edges_through_nodes"])
        self.assertEqual(checks(deep, "fail"), ["edges_through_nodes"])

    def test_title_strike_fails_and_near_miss_warns(self):
        strike = sg.evaluate(base_metrics(title_crossings=[
            {"edge": "a->b", "title": "T", "near_miss": False}]), NOTATION)
        near = sg.evaluate(base_metrics(title_crossings=[
            {"edge": "a->b", "title": "T", "near_miss": True}]), NOTATION)
        self.assertEqual(checks(strike, "fail"), ["title_crossings"])
        self.assertEqual(checks(near, "fail"), [])
        self.assertEqual(checks(near, "warn"), ["title_near_miss"])

    def test_overlap_clipping_and_overflow_fail(self):
        f = sg.evaluate(base_metrics(
            label_overlaps=[{"a": "label:x", "b": "node:y", "area_px": 30.0}],
            clipped_labels=[{"label": "Conversati", "overflow_px": 14.0}],
            gantt={"bars": 1, "labels_outside": 1, "section_overflow": [],
                   "overflow": [{"label": "T9", "reason": "past the right edge", "px": 12.0}]}),
            NOTATION)
        self.assertEqual(checks(f, "fail"), ["clipped_labels", "gantt_overflow", "label_overlaps"])

    def test_an_edge_through_a_label_fails_its_own_check(self):
        # TASK R7.6 lists edges through labels apart from label overlaps (calibration items 08,
        # 30, 34): the edge fails edges_through_labels, never label_overlaps
        through = {"edge": "t->u", "label": "yes", "inside_px": 16.0}
        f = sg.evaluate(base_metrics(edges_through_labels=[through]), NOTATION)
        self.assertEqual(checks(f, "fail"), ["edges_through_labels"])
        self.assertIn("edge t->u runs 16.0 px inside the label 'yes'",
                      [x["message"] for x in f if x["check"] == "edges_through_labels"])
        # metrics stored before the check existed hold the edge as a label_overlaps entry
        stored = {"a": "edge:t->u", "b": "label:yes", "area_px": 16.0, "kind": "edge-label"}
        overlap = {"a": "label:x", "b": "node:y", "area_px": 30.0, "kind": "label-node"}
        old = sg.evaluate(base_metrics(label_overlaps=[stored, overlap]), NOTATION)
        self.assertEqual(checks(old, "fail"), ["edges_through_labels", "label_overlaps"])
        self.assertEqual([x["message"] for x in old if x["check"] == "edges_through_labels"],
                         [x["message"] for x in f if x["check"] == "edges_through_labels"])
        self.assertEqual(len([x for x in old if x["check"] == "label_overlaps"]), 1)

    def test_legibility_floor(self):
        floor = NOTATION["min_effective_font_px"]
        self.assertEqual(checks(sg.evaluate(base_metrics(effective_font_px=floor), NOTATION), "fail"), [])
        low = sg.evaluate(base_metrics(effective_font_px=floor - 0.5, width=2000.0), NOTATION)
        self.assertEqual(checks(low, "fail"), ["legibility"])

    def test_warn_only_checks(self):
        f = sg.evaluate(base_metrics(
            duplicate_edges=[{"pair": ["a", "b"], "edges": ["a->b", "a->b#2"]}],
            sequence={"participants": ["A", "B", "C", "D"], "lifeline_gaps": [200.0, 600.0, 200.0]},
            gantt={"bars": 1, "labels_outside": 0, "overflow": [],
                   "section_overflow": [{"label": "Long section", "px": 9.0}]}), NOTATION)
        self.assertEqual(checks(f, "fail"), [])
        self.assertEqual(checks(f, "warn"), ["duplicate_edges", "gantt_overflow", "lifeline_gap"])
        self.assertTrue(sg.passes(f))

    def test_even_gaps_do_not_warn(self):
        f = sg.evaluate(base_metrics(sequence={"participants": ["A", "B", "C"],
                                               "lifeline_gaps": [200.0, 300.0]}), NOTATION)
        self.assertEqual(f, [])

    def test_unmeasured_text_is_reported(self):
        f = sg.evaluate(base_metrics(measured=False), NOTATION)
        self.assertEqual(checks(f, "warn"), ["clipped_labels", "contrast"])

    def test_fails_come_first(self):
        f = sg.evaluate(base_metrics(crossings=TH["max_crossings"] + 1, measured=False), NOTATION)
        self.assertEqual([x["severity"] for x in f], ["fail", "warn", "warn"])


# ----------------------------------------------------------------------------- browser measurement


class TestMeasureApplied(unittest.TestCase):
    """A measure dict as measure_text.mjs prints it, applied without a browser."""

    def setUp(self):
        self.svg = fixture_svg("fx-title", "v11")
        S = sg._Svg(self.svg)
        clusters = sg._extract_graph(S, [])[1]
        self.cluster = clusters[0]

    def measure(self, title_bbox, labels=(), font_px=16):
        return {"labels": list(labels), "font_px": font_px,
                "titles": [{"text": "Conversation workers", "id": self.cluster["raw_id"],
                            "bbox": title_bbox, "box": None}]}

    def test_painted_title_off_the_edge_is_a_near_miss(self):
        x0, y0, x1, y1 = self.cluster["title"]
        narrow = [x0, y0, 20.0, y1 - y0]  # glyphs end 20 px into the reserved box, left of the edge
        m = sg.analyze_svg(self.svg, 900, self.measure(narrow))
        self.assertTrue(m["measured"])
        self.assertEqual([t["near_miss"] for t in m["title_crossings"]], [True])
        f = sg.evaluate(m, NOTATION)
        self.assertEqual(checks(f, "fail"), [])
        self.assertIn("title_near_miss", checks(f, "warn"))

    def test_painted_title_on_the_edge_is_a_strike(self):
        x0, y0, x1, y1 = self.cluster["title"]
        m = sg.analyze_svg(self.svg, 900, self.measure([x0, y0, x1 - x0, y1 - y0]))
        self.assertEqual([t["near_miss"] for t in m["title_crossings"]], [False])

    def test_clipped_label_beyond_tolerance(self):
        cut = {"text": "Conversation API", "kind": "node", "bbox": [70, 183, 140, 24],
               "box": [70, 183, 119.5, 24], "clipped_px": 20.5}
        bearing = {"text": "Client apps", "kind": "node", "bbox": [90, 23, 81, 24],
                   "box": [90, 23, 80.2, 24], "clipped_px": 0.8}
        m = sg.analyze_svg(self.svg, 900, self.measure(None, labels=[cut, bearing]))
        self.assertEqual([c["label"] for c in m["clipped_labels"]], ["Conversation API"])
        self.assertIn("clipped_labels", checks(sg.evaluate(m, NOTATION), "fail"))

    def test_measured_font_size_decides_legibility(self):
        m = sg.analyze_svg(self.svg, 900, self.measure(None, font_px=8))
        self.assertEqual(m["font_px"], 8.0)
        self.assertIn("legibility", checks(sg.evaluate(m, NOTATION), "fail"))

    def test_clip_tolerance_is_a_constant_allowance(self):
        # RG-07: a wide box gets no more slack than a narrow one. The box of an HTML label is
        # space reserved inside a padded shape (CLIP_TOL_PX); the box of SVG text in a note, an
        # actor or a gantt bar is the outline drawn around it (PAINTED_CLIP_TOL_PX)
        cases = [("foreignObject", "node", sg.CLIP_TOL_PX), ("foreignObject", "edge", sg.CLIP_TOL_PX)]
        cases += [("text", kind, sg.PAINTED_CLIP_TOL_PX) for kind in ("note", "actor", "task")]
        for el, kind, tol in cases:
            for over, clipped in ((tol + 0.1, True), (tol - 0.1, False)):
                with self.subTest(el=el, kind=kind, over=over):
                    lab = {"text": "Payment authorization service", "kind": kind, "el": el,
                           "bbox": [10, 10, 300 + over, 24], "box": [10, 10, 300, 24],
                           "clipped_px": over}
                    m = sg.analyze_svg(self.svg, 900, self.measure(None, labels=[lab]))
                    self.assertEqual(bool(m["clipped_labels"]), clipped)

    def test_a_note_line_past_its_drawn_box_is_clipped(self):
        # TASK 108 calibration item-06: a note line 1.82 px past rect.note, the outline drawn
        # around it, shows ink past the border in the PNG; the figure's edge keeps CLIP_TOL_PX
        note = {"text": "Fail the payment if no webhook", "kind": "note", "el": "text",
                "bbox": [486.18, 649.19, 227.64, 19], "box": [488, 639, 224, 58],
                "clipped_px": 1.82, "outside_px": 0.0}
        m = sg.analyze_svg(self.svg, 900, self.measure(None, labels=[note]))
        self.assertEqual([(c["label"], c["overflow_px"], c["where"]) for c in m["clipped_labels"]],
                         [("Fail the payment if no webhook", 1.8, "its box")])
        self.assertIn("clipped_labels", checks(sg.evaluate(m, NOTATION), "fail"))
        edge = dict(note, box=None, clipped_px=0.0, outside_px=sg.CLIP_TOL_PX - 0.1)
        m = sg.analyze_svg(self.svg, 900, self.measure(None, labels=[edge]))
        self.assertEqual(m["clipped_labels"], [])

    def test_the_clip_tolerances_are_calibrated(self):
        # R2-11: fixed overruns, not values derived from the constants, hold each tolerance in
        # place. A drawn outline (a note, an actor, a gantt bar) allows at least 0.25 px and
        # less than 0.75 px, about half its 1 px stroke; the reserved box of an HTML label and
        # the figure's edge allow at least 1.9 px and less than 2.1 px
        boxed = [("text", kind, 0.25, 0.75) for kind in ("note", "actor", "task")]
        boxed += [("foreignObject", kind, 1.9, 2.1) for kind in ("node", "edge")]
        for el, kind, kept, cut in boxed:
            for over, clipped in ((kept, False), (cut, True)):
                with self.subTest(el=el, kind=kind, over=over):
                    lab = {"text": "Payment authorization service", "kind": kind, "el": el,
                           "bbox": [10, 10, 300 + over, 24], "box": [10, 10, 300, 24],
                           "clipped_px": over, "outside_px": 0.0}
                    m = sg.analyze_svg(self.svg, 900, self.measure(None, labels=[lab]))
                    self.assertEqual([c["where"] for c in m["clipped_labels"]],
                                     ["its box"] if clipped else [])
        for el, kind in (("text", "note"), ("text", "actor"), ("foreignObject", "node")):
            for over, clipped in ((1.9, False), (2.1, True)):
                with self.subTest(edge_of=kind, over=over):
                    lab = {"text": "Billing", "kind": kind, "el": el,
                           "bbox": [10, -over, 60, 20], "box": None, "clipped_px": 0.0,
                           "outside_px": over}
                    m = sg.analyze_svg(self.svg, 900, self.measure(None, labels=[lab]))
                    self.assertEqual([c["where"] for c in m["clipped_labels"]],
                                     ["the figure's edge"] if clipped else [])

    def test_text_past_the_figure_edge_is_clipped(self):
        # RG-16: a text with no reserved box that runs out of the canvas is cut for every reader
        lab = {"text": "Billing", "kind": "actor", "bbox": [10, -25, 60, 20], "box": None,
               "clipped_px": 0.0, "outside_px": 25.0}
        inside = dict(lab, bbox=[10, 5, 60, 20], outside_px=0.0)
        m = sg.analyze_svg(self.svg, 900, self.measure(None, labels=[lab, inside]))
        self.assertEqual([c["label"] for c in m["clipped_labels"]], ["Billing"])
        self.assertIn("edge", m["clipped_labels"][0]["where"])
        self.assertIn("clipped_labels", checks(sg.evaluate(m, NOTATION), "fail"))

    def test_the_smallest_drawn_text_decides_legibility(self):
        # RG-02: one 6 px label among 16 px labels fails, and the finding names it
        labels = [measured_label("Alpha"), measured_label("Beta"),
                  measured_label("Terms and conditions apply", font_px=6.0, kind="node")]
        m = sg.analyze_svg(self.svg, 900, measure_of(*labels))
        self.assertEqual((m["font_px"], m["smallest_font_px"]), (16.0, 6.0))
        self.assertEqual(m["smallest_text"], "Terms and conditions apply")
        fails = [f for f in sg.evaluate(m, NOTATION)
                 if f["severity"] == "fail" and f["check"] == "legibility"]
        self.assertEqual(len(fails), 1)
        self.assertIn("Terms and conditions apply", fails[0]["message"])

    def test_undrawn_text_and_sequence_numbers_do_not_set_the_smallest_size(self):
        labels = [measured_label("Alpha"), measured_label("hidden", font_px=6.0, fg=None),
                  measured_label("1", font_px=6.0, cls="sequenceNumber")]
        m = sg.analyze_svg(self.svg, 900, measure_of(*labels))
        self.assertEqual(m["smallest_font_px"], 16.0)
        self.assertEqual(checks(sg.evaluate(m, NOTATION), "fail"), ["title_crossings"])

    def test_the_notation_lists_the_legibility_exemptions(self):
        # RG-02: the exempt classes are thresholds.legibility_exempt_classes, not a constant
        self.assertIn("sequenceNumber", TH["legibility_exempt_classes"])
        labels = [measured_label("Alpha"), measured_label("1", font_px=6.0, cls="sequenceNumber")]
        n = json.loads(json.dumps(NOTATION))
        n["thresholds"]["legibility_exempt_classes"] = []
        m = sg.analyze_svg(self.svg, 900, measure_of(*labels), None, n)
        self.assertEqual((m["smallest_font_px"], m["smallest_text"]), (6.0, "1"))
        n["thresholds"]["legibility_exempt_classes"] = ["sequenceNumber"]
        self.assertEqual(sg.analyze_svg(self.svg, 900, measure_of(*labels), None, n)
                         ["smallest_font_px"], 16.0)
        for bad in (None, "sequenceNumber", [3]):
            with self.subTest(value=bad):
                n["thresholds"]["legibility_exempt_classes"] = bad
                with self.assertRaises(ValueError):
                    sg.analyze_svg(self.svg, 900, measure_of(*labels), None, n)

    def test_a_five_task_journey_is_sized_by_its_task_text(self):
        # RG-02: 14 px task text in a 1300 px journey reads at 9.7 px; the 16 px legend passed it
        tasks = [measured_label("Task %d" % k, font_px=14.0, bbox=(100.0 + 220 * k, 200.0, 80.0, 16.0))
                 for k in range(5)]
        legend = [measured_label("Guest", bbox=(10.0, 10.0 + 30 * k, 50.0, 18.0)) for k in range(2)]
        m = sg.analyze_svg(kind_svg("journey", 1300, 600), 900, measure_of(*(tasks + legend)))
        self.assertAlmostEqual(m["effective_font_px"], 16 * 900 / 1300, places=1)
        self.assertAlmostEqual(m["smallest_effective_font_px"], 14 * 900 / 1300, places=1)
        self.assertIn("legibility", checks(sg.evaluate(m, NOTATION), "fail"))


# ----------------------------------------------------------------------------- anatomy rules


class TestSyntheticAnatomy(unittest.TestCase):
    NODES = {"a": (50, 50, 40, 20), "b": (350, 50, 40, 20), "c": (50, 250, 40, 20),
             "d": (350, 250, 40, 20)}

    def test_crossing_counted_once(self):
        svg = flowchart_svg(self.NODES, [("L_a_d_0", "M50,60 L350,240", SOLID, ""),
                                         ("L_b_c_0", "M350,60 L50,240", SOLID, "")])
        m = sg.analyze_svg(svg, 900)
        self.assertEqual(m["crossings"], 1)
        self.assertEqual(m["crossing_pairs"], [["a->d", "b->c", 200.0, 150.0]])

    def test_shared_end_is_not_a_crossing(self):
        nodes = {"a": (200, 50, 40, 20), "b": (100, 250, 40, 20), "c": (300, 250, 40, 20)}
        svg = flowchart_svg(nodes, [("L_a_b_0", "M200,60 L100,240", SOLID, ""),
                                    ("L_a_c_0", "M200,60 L300,240", SOLID, "")])
        self.assertEqual(sg.analyze_svg(svg, 900)["crossings"], 0)

    def test_invisible_links_are_excluded(self):
        svg = flowchart_svg(self.NODES, [
            ("L_a_d_0", "M50,60 L350,240", SOLID, ""),
            ("L_b_c_0", "M350,60 L50,240", "edge-thickness-invisible edge-pattern-solid", ""),
            ("L_c_b_0", "M50,240 L350,60", SOLID, "stroke-width: 0;fill:none;")])
        m = sg.analyze_svg(svg, 900)
        self.assertEqual((m["edges"], m["crossings"]), (1, 0))

    def test_edge_through_a_node(self):
        nodes = {"a": (50, 150, 40, 20), "m": (200, 150, 60, 40), "b": (350, 150, 40, 20)}
        svg = flowchart_svg(nodes, [("L_a_b_0", "M70,150 L330,150", SOLID, "")])
        hits = sg.analyze_svg(svg, 900)["edges_through_nodes"]
        self.assertEqual([(h["edge"], h["node"]) for h in hits], [("a->b", "m")])
        self.assertAlmostEqual(hits[0]["depth_px"], 60 - 2 * sg.THROUGH_NOISE_PX, delta=1.5)

    def test_duplicate_edges(self):
        svg = flowchart_svg(self.NODES, [("L_a_b_0", "M70,50 L330,50", SOLID, ""),
                                         ("L_b_a_0", "M330,55 L70,55", SOLID, "")])
        dup = sg.analyze_svg(svg, 900)["duplicate_edges"]
        self.assertEqual(dup, [{"pair": ["a", "b"], "edges": ["a->b", "b->a"]}])

    def test_v10_classes_name_the_ends(self):
        svg = flowchart_svg(self.NODES, [("x", "M70,50 L330,50", SOLID + " LS-a LE-b", "")])
        svg = svg.replace('data-id="x"', "")
        S = sg._Svg(svg)
        edge = sg._extract_graph(S, [])[2][0]
        self.assertEqual((edge["src"], edge["dst"], edge["mapped_by"]), ("a", "b", "id"))

    def test_ambiguous_id_falls_back_to_geometry(self):
        nodes = {"a": (50, 50, 40, 20), "b_c": (350, 50, 40, 20), "a_b": (50, 250, 40, 20),
                 "c": (350, 250, 40, 20)}
        svg = flowchart_svg(nodes, [("L_a_b_c_0", "M70,50 L330,50", SOLID, "")])
        warnings = []
        edge = sg._extract_graph(sg._Svg(svg), warnings)[2][0]
        self.assertEqual((edge["src"], edge["dst"], edge["mapped_by"]), ("a", "b_c", "geometry"))
        self.assertTrue(any("splits 2 ways" in w for w in warnings))

    def test_unknown_kind_reports_size_only(self):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" id="my-svg" viewBox="0 0 1800 100" '
               'aria-roledescription="mindmap"><style>#my-svg{font-size:16px;}</style></svg>')
        m = sg.analyze_svg(svg, 900)
        self.assertEqual((m["width"], m["font_px"], m["effective_font_px"]), (1800.0, 16.0, 8.0))
        self.assertTrue(any("not modelled" in w for w in m["warnings"]))

    def test_an_unmodelled_kind_says_its_geometry_is_not_checked(self):
        # RG-01: a pass on a kind whose geometry is not read here must not look like a full pass
        m = sg.analyze_svg(kind_svg("quadrantChart", 500, 500), 900, measure_of(measured_label("A")))
        self.assertEqual(m["geometry"], "not modelled")
        f = sg.evaluate(m, NOTATION)
        self.assertEqual(checks(f, "warn"), ["geometry"])
        self.assertTrue(sg.passes(f))
        self.assertEqual(sg.analyze_svg(fixture_svg("fx-tree", "v11"), 900)["geometry"], "modelled")
        self.assertEqual(sg.analyze_svg(fixture_svg("fx-seq-skip", "v11"), 900)["geometry"],
                         "modelled")

    def test_painted_labels_of_an_unmodelled_kind_must_not_overlap(self):
        # RG-01: three quadrant points 0.01 apart draw their labels over each other
        pts = [measured_label("Campaign Alpha", bbox=(101.5, 221.6, 155.9, 14.0)),
               measured_label("Campaign Beta long name", bbox=(105.0, 213.2, 139.6, 14.0)),
               measured_label("Campaign Gamma", bbox=(97.8, 217.4, 144.7, 14.0)),
               measured_label("Re-evaluate", bbox=(300.0, 40.0, 80.0, 16.0))]
        m = sg.analyze_svg(kind_svg("quadrantChart", 500, 500), 900, measure_of(*pts))
        self.assertEqual(len(m["label_overlaps"]), 3)
        self.assertTrue(all(o["kind"] == "label-label" for o in m["label_overlaps"]))
        self.assertIn("label_overlaps", checks(sg.evaluate(m, NOTATION), "fail"))

    def test_rotated_and_undrawn_labels_are_not_compared_by_box(self):
        # a rotated label's box is far larger than its glyphs (gitGraph commit ids)
        pts = [measured_label("a1b2c3d", bbox=(100.0, 100.0, 40.0, 40.0), rotated=True),
               measured_label("e4f5a6b", bbox=(120.0, 100.0, 40.0, 40.0), rotated=True),
               measured_label("hidden", bbox=(100.0, 100.0, 40.0, 40.0), fg=None),
               measured_label("main", bbox=(10.0, 10.0, 40.0, 16.0))]
        m = sg.analyze_svg(kind_svg("gitGraph", 400, 300), 900, measure_of(*pts))
        self.assertEqual(m["label_overlaps"], [])

    def test_painted_labels_of_a_sequence_figure_must_not_overlap(self):
        svg = fixture_svg("fx-seq-skip", "v11")
        labels = [measured_label("alt", kind="other", bbox=(20.0, 300.0, 30.0, 18.0)),
                  measured_label("[the card is enrolled]", kind="other", bbox=(25.0, 302.0, 160.0, 18.0))]
        m = sg.analyze_svg(svg, 900, measure_of(*labels))
        self.assertEqual([(o["a"], o["b"]) for o in m["label_overlaps"]],
                         [("label:alt", "label:[the card is enrolled]")])

    def test_the_lines_of_one_name_are_one_label(self):
        # R1: a two- or three-line participant or actor name is one label, not overlapping lines
        for group_class in ("", "actor-man actor-top"):
            with self.subTest(group=group_class or "participant"):
                svg, measure = names_svg([[("Access control", "-8"), ("server", "8")],
                                          [("Payments", "-16"), ("gateway", "0"), ("west", "16")]],
                                         group_class)
                m = sg.analyze_svg(svg, 900, measure)
                self.assertEqual(m["label_overlaps"], [])
                self.assertNotIn("label_overlaps", checks(sg.evaluate(m, NOTATION), "fail"))

    def test_two_labels_at_one_anchor_still_overlap(self):
        # one `dy`: two labels drawn over each other, not two lines of one label
        svg, measure = names_svg([[("Orders", "0"), ("Billing", "0")]])
        m = sg.analyze_svg(svg, 900, measure)
        self.assertEqual([(o["a"], o["b"]) for o in m["label_overlaps"]],
                         [("label:Orders", "label:Billing")])
        # lines of two groups, and a measured text that is not the SVG text at its index
        svg, measure = names_svg([[("Access control", "-8")], [("server", "8")]])
        measure["labels"][1]["bbox"] = list(measure["labels"][0]["bbox"])
        self.assertEqual(len(sg.analyze_svg(svg, 900, measure)["label_overlaps"]), 1)
        svg, measure = names_svg([[("Access control", "-8"), ("server", "8")]])
        measure["labels"][1]["text"] = "service"
        self.assertEqual(len(sg.analyze_svg(svg, 900, measure)["label_overlaps"]), 1)

    def test_a_wrapped_participant_name_passes_in_both_versions(self):
        # R1 on real renders: `wrap` breaks "Access control server" in two lines, `<br/>` breaks
        # "Orders<br/>API"; mermaid draws the lines 16 px apart, and their 19 px boxes overlap
        source = (FIXTURES / "fx-seq-names.mmd").read_text(encoding="utf-8")
        for v in VERSIONS:
            with self.subTest(version=v):
                measure = json.loads((FIXTURES / ("fx-seq-names-%s.measure.json" % v))
                                     .read_text(encoding="utf-8"))
                lines = {lab["text"]: lab["bbox"] for lab in measure["labels"]
                         if lab["kind"] == "actor"}
                top, under = lines["Access control"], lines["server"]
                self.assertGreater(top[1] + top[3] - under[1], 2.0, "the lines no longer overlap")
                m = sg.analyze_svg(fixture_svg("fx-seq-names", v), 900, measure,
                                   sg.author_colours(source))
                self.assertEqual(m["label_overlaps"], [])
                self.assertEqual(checks(sg.evaluate(m, NOTATION), "fail"), [])

    def test_an_edge_through_another_edges_label_is_not_a_label_overlap(self):
        # an edge runs through the label of a->b: edges_through_labels, not label_overlaps
        nodes = {"a": (50, 150, 40, 20), "b": (350, 150, 40, 20), "t": (200, 30, 40, 20),
                 "u": (200, 270, 40, 20)}
        svg = flowchart_svg(nodes, [("L_a_b_0", "M70,150 L330,150", SOLID, ""),
                                    ("L_t_u_0", "M200,40 L200,260", SOLID, "")])
        label = ('<g class="edgeLabels"><g class="edgeLabel"><g class="label" data-id="L_a_b_0">'
                 '<foreignObject x="180" y="140" width="40" height="20"><div '
                 'xmlns="http://www.w3.org/1999/xhtml"><span>yes</span></div></foreignObject>'
                 '</g></g></g>')
        m = sg.analyze_svg(svg.replace('<g class="edgeLabels"/>', label), 900)
        self.assertEqual(m["edges_through_labels"], [{"edge": "t->u", "label": "yes", "inside_px": 16.0}])
        self.assertEqual(m["label_overlaps"], [])
        f = checks(sg.evaluate(m, NOTATION), "fail")
        self.assertIn("edges_through_labels", f)
        self.assertNotIn("label_overlaps", f)

    def test_a_label_in_a_diamond_corner_is_not_an_overlap(self):
        # RG-14: the rhombus |x-200| + |y-150| <= 80 does not reach the corner of its box
        corner = sg.analyze_svg(diamond_svg((255, 105, 285, 125)), 900)
        self.assertEqual(corner["label_overlaps"], [])
        inside = sg.analyze_svg(diamond_svg((185, 140, 215, 160)), 900)
        self.assertEqual([(o["kind"], o["area_px"]) for o in inside["label_overlaps"]],
                         [("label-node", 504.0)])

    def test_a_title_in_a_diamond_corner_is_not_an_overlap(self):
        corner = sg.analyze_svg(diamond_svg((255, 105, 285, 125), title=True), 900)
        self.assertEqual(corner["label_overlaps"], [])
        inside = sg.analyze_svg(diamond_svg((185, 140, 215, 160), title=True), 900)
        self.assertEqual([o["kind"] for o in inside["label_overlaps"]], ["title-node"])

    def test_control_character_from_an_entity_is_removed(self):
        svg = flowchart_svg(self.NODES, [("L_a_b_0", "M70,50 L330,50", SOLID, "")])
        svg = svg.replace("</svg>", "<text>a \x01 w</text></svg>")
        m = sg.analyze_svg(svg, 900)
        self.assertEqual(m["edges"], 1)
        self.assertTrue(any("control character" in w for w in m["warnings"]))

    def test_unreadable_input_raises(self):
        for text in ('<!DOCTYPE svg [<!ENTITY x "y">]><svg xmlns="http://www.w3.org/2000/svg"/>',
                     "<html><body/></html>", "<svg", ""):
            with self.subTest(text=text[:20]):
                with self.assertRaises(ValueError):
                    sg.analyze_svg(text, 900)


# ----------------------------------------------------------------------------- lifelines


class TestLifelines(unittest.TestCase):
    def test_a_skipped_lifeline_through_a_label_warns(self):
        """TASK 110 D2: a skipped participant's lifeline runs through the label centre in every
        version, so the crossing warns. Metrics stored before TASK 110 have no `own` key and give
        the verdict they gave then (P8)."""
        for entry in ({"message": "m", "from": "A", "to": "C", "lifelines": ["B"], "own": []},
                      {"message": "m", "from": "A", "to": "C", "lifelines": ["B"]}):
            with self.subTest(entry=entry):
                f = sg.evaluate(base_metrics(sequence={
                    "participants": ["A", "B", "C"], "lifeline_gaps": [200.0, 200.0],
                    "lifeline_through_label": [entry]}), NOTATION)
                self.assertEqual(checks(f, "warn"), ["lifeline_through_label"])
                self.assertEqual(checks(f, "fail"), [])
                self.assertTrue(sg.passes(f))

    def test_an_own_lifeline_through_a_label_fails(self):
        """TASK 110 R1.2: a label wider than the gap between its own two lifelines fails."""
        f = sg.evaluate(base_metrics(sequence={
            "participants": ["A", "B"], "lifeline_gaps": [200.0],
            "lifeline_through_label": [{"message": "m", "from": "A", "to": "B", "lifelines": [],
                                        "own": ["A", "B"]}]}), NOTATION)
        self.assertEqual(checks(f, "fail"), ["lifeline_through_label"])
        self.assertFalse(sg.passes(f))
        self.assertTrue(sg.fired(f, "lifeline_through_label"))

    def test_own_lifelines_are_measured_from_two_participants(self):
        """The fixture has two participants; the self-message's own lifeline is no crossing."""
        for v in VERSIONS:
            with self.subTest(version=v):
                found = fixture_metrics("fx-seq-own", v)["sequence"]["lifeline_through_label"]
                self.assertEqual([(x["from"], x["to"], x["own"]) for x in found], [("A", "B", ["A", "B"])])
                self.assertNotIn("validate", " ".join(x["message"] for x in found))

    def test_gap_ratio_comes_from_the_notation(self):
        r = TH["max_lifeline_gap_ratio"]
        at = sg.evaluate(base_metrics(sequence={"participants": ["A", "B", "C", "D"],
                                                "lifeline_gaps": [200.0, 200.0 * r, 200.0]}), NOTATION)
        over = sg.evaluate(base_metrics(sequence={"participants": ["A", "B", "C", "D"],
                                                  "lifeline_gaps": [200.0, 200.0 * r + 1, 200.0]}),
                           NOTATION)
        self.assertEqual(at, [])
        self.assertEqual(checks(over, "warn"), ["lifeline_gap"])

    def test_measured_boxes_replace_the_estimate(self):
        svg = fixture_svg("fx-seq-skip", "v11")
        S = sg._Svg(svg)
        labels = []
        for k, t in enumerate(S.elements("text")):
            if "messageText" not in sg._classes(t):
                continue
            x0, y0, x1, y1 = S.text_box_estimate(t)
            # each glyph box moved left of every lifeline: no lifeline runs through it
            labels.append({"text": sg._text_of(t), "kind": "message", "el": "text", "n": k,
                           "bbox": [x0 - 400.0, y0, 10.0, y1 - y0]})
        m = sg.analyze_svg(svg, 900, {"labels": labels, "titles": [], "font_px": 16})
        self.assertEqual(m["sequence"]["lifeline_through_label"], [])
        self.assertEqual(m["sequence"]["lifeline_label_crossings"], 0)


# ----------------------------------------------------------------------------- contrast


def text_entry(ratio, scope, kind="node", label="x"):
    return {"text": label, "kind": kind, "fg": "#000000", "bg": "#ffffff", "ratio": ratio,
            "scope": scope}


def contrast_of(*texts):
    return {"page": "#ffffff", "texts": list(texts), "measured": True}


class TestContrastRatio(unittest.TestCase):
    def test_extremes_and_symmetry(self):
        self.assertAlmostEqual(sg.contrast_ratio("#000000", "#ffffff"), 21.0, places=6)
        self.assertAlmostEqual(sg.contrast_ratio("#fff", "#000"), 21.0, places=6)
        self.assertEqual(sg.contrast_ratio("#777777", "#ffffff"),
                         sg.contrast_ratio("#ffffff", "#777777"))
        self.assertAlmostEqual(sg.contrast_ratio("#123456", "#123456"), 1.0)

    def test_known_values(self):
        self.assertAlmostEqual(sg.contrast_ratio("#767676", "#ffffff"), 4.54, places=2)
        # TASK D26: the dark theme's own edge label
        self.assertAlmostEqual(sg.contrast_ratio("#cccccc", "#585858"), 4.43, places=2)

    def test_bad_colour_raises(self):
        with self.assertRaises(ValueError):
            sg.contrast_ratio("red", "#ffffff")


class TestContrastVerdicts(unittest.TestCase):
    MIN = NOTATION["contrast_min"]

    def test_author_text_below_the_minimum_fails(self):
        f = sg.evaluate(base_metrics(contrast=contrast_of(text_entry(self.MIN - 0.01, "author"))),
                        NOTATION)
        self.assertEqual(checks(f, "fail"), ["contrast"])
        self.assertFalse(sg.passes(f))
        self.assertTrue(sg.fired(f, "contrast"))

    def test_author_text_at_the_minimum_passes(self):
        f = sg.evaluate(base_metrics(contrast=contrast_of(text_entry(self.MIN, "author"))), NOTATION)
        self.assertEqual(f, [])

    def test_theme_text_is_information(self):
        f = sg.evaluate(base_metrics(contrast=contrast_of(
            text_entry(self.MIN - 0.07, "theme", "edge", "a"),
            text_entry(self.MIN - 0.10, "theme", "edge", "b"),
            text_entry(self.MIN - 1.5, "unknown", "other", "c"))), NOTATION)
        self.assertEqual(checks(f, "fail"), [])
        self.assertEqual(checks(f, "info"), ["contrast"])
        info = [x["message"] for x in f if x["severity"] == "info"]
        self.assertEqual(len(info), 2)  # one line per text kind
        self.assertTrue(any("2 edge text(s)" in x and "'b'" in x for x in info), info)
        self.assertTrue(sg.passes(f))
        self.assertFalse(sg.fired(f, "contrast"))

    def test_scope_all_gates_theme_text(self):
        n = json.loads(json.dumps(NOTATION))
        n["thresholds"]["contrast_scope"] = "all"
        f = sg.evaluate(base_metrics(contrast=contrast_of(text_entry(self.MIN - 0.07, "theme", "edge"))),
                        n)
        self.assertEqual(checks(f, "fail"), ["contrast"])

    def test_unknown_scope_rule_is_a_broken_instrument(self):
        n = json.loads(json.dumps(NOTATION))
        n["thresholds"]["contrast_scope"] = "some"
        with self.assertRaises(ValueError):
            sg.evaluate(base_metrics(), n)

    def test_unmeasured_colours_warn(self):
        f = sg.evaluate(base_metrics(contrast={"page": None, "texts": [], "measured": False}),
                        NOTATION)
        self.assertEqual(checks(f, "warn"), ["contrast"])

    def test_info_sorts_after_warn(self):
        f = sg.evaluate(base_metrics(crossings=1, contrast=contrast_of(
            text_entry(self.MIN - 1, "theme", "edge"))), NOTATION)
        self.assertEqual([x["severity"] for x in f], ["warn", "info"])

    def test_a_text_on_a_gradient_never_counts_as_passing(self):
        # RG-18: its ratio was taken against the colour under the gradient, which nobody sees
        author = dict(text_entry(12.0, "author"), uncertain=True)
        theme = dict(text_entry(12.0, "theme", "edge"), uncertain=True)
        f = sg.evaluate(base_metrics(contrast=contrast_of(author)), NOTATION)
        self.assertEqual(checks(f, "fail"), ["contrast"])
        self.assertIn("gradient", f[0]["message"])
        f = sg.evaluate(base_metrics(contrast=contrast_of(theme)), NOTATION)
        self.assertEqual((checks(f, "fail"), checks(f, "warn")), ([], ["contrast"]))


FLOW_SOURCE = """%%{init: {"layout": "dagre", "look": "classic"}}%%
flowchart TB
  subgraph G["Group"]
    A("Alpha")
    B("Beta")
  end
  C["Gamma"]:::svc --> D["Delta"]
  E["Epsilon x:::wfNew"]
  A --> B
  %% class E wfNew
  classDef wfNew fill:#FFF4E0,stroke:#B36B00,color:#4A2C00
  classDef svc color:#1F2A30
  classDef thick stroke-width:3px
  class A wfNew
  class D thick
  style G fill:#7F7F7F0D,stroke:#90A4AE
  style B stroke:#333
"""


def init_keys(settings_line):
    """The themeVariables keys of a settings line of notation.json."""
    import re
    config = json.loads(re.match(r"%%\{init:\s*(.*)\}%%$", settings_line).group(1))
    return set(config.get("themeVariables", {}))


class TestAuthorColours(unittest.TestCase):
    def test_classes_styles_and_containers(self):
        spec = sg.author_colours(FLOW_SOURCE)
        self.assertEqual(spec["nodes"], {"A", "C"})
        self.assertEqual(spec["node_fill"], {"A"})
        self.assertEqual(spec["clusters"], {"G"})
        self.assertEqual(spec["cluster_fill"], {"G"})
        self.assertFalse(spec["all_nodes"])
        self.assertFalse(spec["all_text"])
        self.assertEqual(spec["theme_keys"], set())

    def test_link_style_colour_scopes_edge_labels(self):
        spec = sg.author_colours("flowchart TB\n  A --> B\n  linkStyle 0 stroke:#f00,color:#777\n")
        self.assertTrue(spec["edge_labels"])
        S = sg._Svg(fixture_svg("fx-title", "v11"))
        self.assertEqual(sg.text_scope(S, {"kind": "edge"}, spec), "author")
        plain = sg.author_colours("flowchart TB\n  A --> B\n  linkStyle 0 stroke-width:2px\n")
        self.assertFalse(plain["edge_labels"])

    def test_a_class_on_an_edge_id_scopes_that_edge_label(self):
        # RG-12: `class e1 faint` colours the label of edge e1, not a node named e1
        spec = sg.author_colours('flowchart TB\n  A["Draft"] e1@-->|"sent for review"| B["Review"]\n'
                                 '  C@{ shape: cyl } --> A\n'
                                 '  classDef faint color:#d0d0d0\n  class e1 faint\n')
        self.assertEqual(spec["edges"], {"e1"})
        self.assertEqual(spec["nodes"], set())
        S = sg._Svg(fixture_svg("fx-title", "v11"))
        self.assertEqual(sg.text_scope(S, {"kind": "edge", "owner": "e1"}, spec), "author")
        self.assertEqual(sg.text_scope(S, {"kind": "edge", "owner": "e2"}, spec), "theme")

    def test_default_class_colours_every_node(self):
        spec = sg.author_colours("flowchart TB\n  A --> B\n  classDef default fill:#fff,color:#000\n")
        self.assertTrue(spec["all_nodes"])
        self.assertTrue(spec["all_nodes_fill"])

    def test_state_composite_is_a_container(self):
        spec = sg.author_colours('stateDiagram-v2\n  state "Waits" as W {\n    a --> b\n  }\n'
                                 '  classDef hold fill:#E8F0FB,color:#0F2A47\n'
                                 '  class W hold\n  class a hold\n')
        self.assertEqual(spec["clusters"], {"W"})
        self.assertEqual(spec["nodes"], {"a"})

    def test_settings_lines_of_the_notation(self):
        for kind in ("sequence", "gantt", "flowchart", "state"):
            with self.subTest(kind=kind):
                line = NOTATION["settings"][kind]
                spec = sg.author_colours(line + "\n" + kind + "\n")
                self.assertEqual(spec["theme_keys"], init_keys(line))
                self.assertFalse(spec["all_text"])
        gantt = sg.author_colours(NOTATION["settings"]["gantt"] + "\ngantt\n")
        self.assertIn(frozenset({"doneText0", "taskTextOutsideRight"}), gantt["css"])
        self.assertNotIn(frozenset(), gantt["css"])

    def test_global_key_or_theme_scopes_every_text(self):
        for line in ('%%{init: {"themeVariables": {"primaryColor": "#ffffff"}}}%%',
                     '%%{init: {"theme": "base"}}%%'):
            self.assertTrue(sg.author_colours(line + "\nflowchart TB\n  A --> B\n")["all_text"], line)

    def test_unreadable_source_sets_nothing(self):
        spec = sg.author_colours("%%{init: {broken\nflowchart TB\n  A --> B\n")
        self.assertEqual((spec["nodes"], spec["theme_keys"], spec["all_text"]), (set(), set(), False))


class TestTextScope(unittest.TestCase):
    def setUp(self):
        self.S = sg._Svg(fixture_svg("fx-title", "v11"))
        self.spec = sg.author_colours(FLOW_SOURCE)

    def scope(self, spec=None, **label):
        return sg.text_scope(self.S, label, self.spec if spec is None else spec)

    def test_node_by_class_or_style(self):
        self.assertEqual(self.scope(kind="node", id="my-svg-flowchart-A-0"), "author")
        self.assertEqual(self.scope(kind="node", id="flowchart-C-3", owner="C"), "author")
        self.assertEqual(self.scope(kind="node", id="my-svg-flowchart-D-4"), "theme")
        self.assertEqual(self.scope(kind="node", id="my-svg-flowchart-E-5"), "theme")

    def test_title_of_a_styled_subgraph(self):
        self.assertEqual(self.scope(kind="title", id="my-svg-G"), "author")
        self.assertEqual(self.scope(kind="title", id="my-svg-H"), "theme")

    def test_topmost_layer_decides_the_background(self):
        cluster = {"role": "cluster", "id": "my-svg-G", "fill": "rgba(127,127,127,0.05)"}
        label_bg = {"role": "edgeLabel", "id": "", "fill": "rgba(88,88,88,1)"}
        band = {"role": "band", "id": "", "fill": "rgba(127,127,127,0.1)"}
        self.assertEqual(self.scope(kind="edge", under=[cluster, label_bg]), "theme")
        self.assertEqual(self.scope(kind="other", under=[label_bg, cluster]), "author")
        self.assertEqual(self.scope(kind="message", under=[band]), "author")

    def test_theme_variables_by_kind(self):
        spec = sg.author_colours(NOTATION["settings"]["sequence"] + "\nsequenceDiagram\n")
        note = {"role": "note", "id": "", "fill": "rgba(255,248,225,1)"}
        self.assertEqual(self.scope(spec, kind="note"), "author")
        self.assertEqual(self.scope(spec, kind="message"), "theme")
        self.assertEqual(self.scope(spec, kind="actor"), "theme")
        self.assertEqual(self.scope(spec, kind="other", under=[note]), "author")

    def test_theme_css_classes(self):
        spec = sg.author_colours(NOTATION["settings"]["gantt"] + "\ngantt\n")
        self.assertEqual(self.scope(spec, kind="other", cls="taskTextOutsideRight activeText0"),
                         "author")
        self.assertEqual(self.scope(spec, kind="other", cls="taskTextOutsideRight"), "theme")

    def test_no_spec_is_unknown(self):
        self.assertEqual(sg.text_scope(self.S, {"kind": "node"}, None), "unknown")


class TestContrastFromMeasure(unittest.TestCase):
    MEASURE = {"font_px": 16, "titles": [], "page": "#0d1117", "labels": [
        {"text": "Client apps", "kind": "node", "id": "my-svg-flowchart-CLI-0", "fg": "#4a2c00",
         "bg": "#fff4e0", "under": []},
        {"text": "calls", "kind": "edge", "id": "L_CLI_API_0", "fg": "#cccccc", "bg": "#585858",
         "under": [{"role": "edgeLabel", "id": "", "fill": "rgba(88,88,88,1)"}]},
        {"text": "not drawn", "kind": "other", "fg": None, "bg": "#0d1117", "under": []}]}
    SOURCE = "flowchart TB\n  CLI --> API\n  classDef ext fill:#FFF4E0,color:#4A2C00\n  class CLI ext\n"

    def test_ratios_and_scope(self):
        m = sg.analyze_svg(fixture_svg("fx-title", "v11"), 900, self.MEASURE,
                           sg.author_colours(self.SOURCE))
        texts = m["contrast"]["texts"]
        self.assertTrue(m["contrast"]["measured"])
        self.assertEqual(m["contrast"]["page"], "#0d1117")
        self.assertEqual([t["text"] for t in texts], ["Client apps", "calls"])
        self.assertEqual([t["scope"] for t in texts], ["author", "theme"])
        self.assertEqual(texts[1]["ratio"], 4.43)
        f = sg.evaluate(m, NOTATION)
        self.assertNotIn("contrast", checks(f, "fail"))  # the fixture fails its title crossing
        self.assertIn("contrast", checks(f, "info"))

    def test_a_ratio_is_truncated_never_rounded_up(self):
        # #767776 on white measures 4.4962:1; rounding would store 4.50
        measure = {"font_px": 16, "titles": [], "page": "#ffffff", "labels": [
            {"text": "grey", "kind": "node", "id": "my-svg-flowchart-CLI-0", "fg": "#767776",
             "bg": "#ffffff", "under": []}]}
        m = sg.analyze_svg(fixture_svg("fx-title", "v11"), 900, measure,
                           sg.author_colours(self.SOURCE))
        ratio = m["contrast"]["texts"][0]["ratio"]
        self.assertLessEqual(ratio, sg.contrast_ratio("#767776", "#ffffff"))
        self.assertEqual(ratio, 4.49)

    def test_without_a_source_contrast_is_not_gated(self):
        m = sg.analyze_svg(fixture_svg("fx-title", "v11"), 900, self.MEASURE)
        self.assertEqual({t["scope"] for t in m["contrast"]["texts"]}, {"unknown"})
        self.assertTrue(any("not gated" in w for w in m["warnings"]))


class TestFired(unittest.TestCase):
    def test_gate_checks_need_a_fail(self):
        warn = [{"check": "crossings", "severity": "warn", "message": ""}]
        self.assertFalse(sg.fired(warn, "crossings"))
        self.assertTrue(sg.fired(warn + [{"check": "crossings", "severity": "fail", "message": ""}],
                                 "crossings"))

    def test_warn_checks_fire_on_a_warning(self):
        f = [{"check": "lifeline_gap", "severity": "warn", "message": ""}]
        self.assertTrue(sg.fired(f, "lifeline_gap"))
        self.assertFalse(sg.fired(f, "lifeline_through_label"))

    def test_the_lifeline_gate_fires_on_a_fail_only(self):
        """TASK 110 R1.2: `lifeline_through_label` is a gate check, so its warning fires nothing."""
        self.assertIn("lifeline_through_label", sg.GATE_CHECKS)
        warn = [{"check": "lifeline_through_label", "severity": "warn", "message": ""}]
        self.assertFalse(sg.fired(warn, "lifeline_through_label"))
        self.assertTrue(sg.fired(warn + [{"check": "lifeline_through_label", "severity": "fail",
                                          "message": ""}], "lifeline_through_label"))

    def test_the_two_sets_partition_the_checks(self):
        self.assertEqual(set(sg.GATE_CHECKS) | set(sg.WARN_CHECKS), set(sg.CHECKS))
        self.assertFalse(set(sg.GATE_CHECKS) & set(sg.WARN_CHECKS))


if __name__ == "__main__":
    unittest.main()
