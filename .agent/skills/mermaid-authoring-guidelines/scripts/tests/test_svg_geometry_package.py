"""Tests of the package `svg_geometry_parts` (TASK 125 R4).

`svg_geometry.py` became a thin file over `scripts/svg_geometry_parts/`: one module per section
of the former file. The thin file binds every top-level name of the 12 modules and holds the debug
command line `main` (TASK 125 R1, R2). These tests pin:

* the package's files: `__init__.py` and the 12 modules (``TC-01``);
* each module imports exactly the names that its code reads: relatively only from the modules above
  it, and absolutely only the standard library and `mermaid_model`. `__init__.py` holds a
  docstring only (``TC-02``);
* each of the 119 names of the package is defined in its module and bound on `svg_geometry` to the
  same object. The thin file defines `main` and `__all__`, which lists the 120 names (``TC-03``);
* `INSTRUMENT_FILES` of `scripts/render_check.py` and of `evals/render_corpus.py`, read by AST,
  name the thin file and each file of the package once (``TC-04``).

A top-level name is one that a top-level `def`, `class` or assignment binds, each name of a tuple
target included and imported names excluded (TASK 124 §0).
"""
import ast
import builtins
import importlib
import symtable
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import svg_geometry as sg  # noqa: E402

PACKAGE = SCRIPTS / "svg_geometry_parts"
#: TASK 125 R1: the modules of the package, in order; each imports only from those above it.
MODULES = ("base", "tolerances", "transforms", "flattening", "plane", "text_estimate", "svg_model",
           "graph", "sequence", "gantt", "contrast", "api")
#: TASK 125 R3: the files that both INSTRUMENT_FILES name.
PACKAGE_FILES = ("scripts/svg_geometry.py",) + tuple(
    f"scripts/svg_geometry_parts/{m}.py" for m in ("__init__",) + MODULES)
#: TASK 125 TC-03: the top-level names of the former file, by the module that defines each.
NAMES = {
    "base": ("METRIC_KEYS", "CHECKS", "GATE_CHECKS", "WARN_CHECKS", "SEVERITIES"),
    "tolerances": ("FLATTEN_TOL_PX", "SAMPLE_STEP_PX", "SHARED_END_MARGIN_PX", "DEDUPE_RADIUS_PX",
                   "END_SNAP_PX", "THROUGH_NOISE_PX", "THROUGH_MIN_RUN_PX", "TITLE_MIN_INSIDE_PX",
                   "TITLE_NEAR_MARGIN_PX", "OVERLAP_MIN_AREA_PX2", "EDGE_IN_LABEL_MIN_PX",
                   "CLIP_TOL_PX", "PAINTED_CLIP_TOL_PX", "PAINTED_BOX_KINDS", "GANTT_EDGE_TOL_PX",
                   "MESSAGE_END_SNAP_PX", "LIFELINE_LABEL_MARGIN_PX"),
    "transforms": ("IDENT", "mat_mul", "mat_apply", "_TF", "_NUM", "parse_transform"),
    "flattening": ("_PathScanner", "_dist_point_line", "_mid", "flatten_cubic", "_flatten_arc",
                   "path_polylines"),
    "plane": ("bbox_of", "box_union", "box_grow", "box_area", "box_overlap_area", "boxes_touch",
              "point_in_box", "dist_point_box", "segment_intersection", "segments_of",
              "polyline_intersections", "clip_length_in_box", "length_in_box", "convex_hull",
              "point_in_convex", "polygon_area", "box_hull_overlap_area", "dist_point_segment",
              "penetration", "dedupe_points"),
    "text_estimate": ("_HELVETICA", "estimate_text_width"),
    "svg_model": ("_local", "_classes", "_text_of", "_font_px_of", "_XML_FORBIDDEN", "_Svg"),
    "graph": ("_NODE_ID_PATTERNS", "_EDGE_CLASSES", "_node_name", "_cluster_name", "_is_edge_path",
              "_INVISIBLE_STYLE", "_is_invisible", "_in_label_group", "_edge_display_names",
              "_extract_graph", "_graph_metrics"),
    "sequence": ("_measured_texts", "_lifeline_label_crossings", "_sequence_metrics"),
    "gantt": ("_gantt_metrics",),
    "contrast": ("THEME_GLOBAL_KEYS", "THEME_TEXT_KEYS", "THEME_LAYER_KEYS", "_COLOUR_PROPS",
                 "_FILL_PROPS", "_CLASSDEF_RE", "_CLASS_RE", "_CSSCLASS_RE", "_STYLE_RE",
                 "_LINKSTYLE_RE", "_TRIPLE_RE", "_SUBGRAPH_RE", "_EDGE_ID_RE", "_COMPOSITE_RE",
                 "_INIT_RE", "_hex_rgb", "relative_luminance", "contrast_ratio", "_triple_targets",
                 "_props", "_settings_configs", "_css_class_sets", "author_colours", "_owner_name",
                 "_layer_is_author", "text_scope", "_contrast_metrics"),
    "api": ("_empty_metrics", "_unprobed_swap", "_escaped", "_swap_px", "_font_swap_from_measure",
            "_box_clip_tolerance", "_clipped_from_measure", "_line_anchor",
            "_painted_label_overlaps", "_legibility_exempt", "_smallest_text", "analyze_svg",
            "evaluate", "passes", "fired"),
}


def _imports(path):
    """(line, level, module) of each import statement of *path*, at any depth."""
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom):
            found.append((node.lineno, node.level, node.module))
        elif isinstance(node, ast.Import):
            found.extend((node.lineno, 0, a.name) for a in node.names)
    return found


def _bound_at_top(path):
    """The names that a top-level `def`, `class` or assignment of *path* binds."""
    names = set()
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            stack = list(node.targets) if isinstance(node, ast.Assign) else [node.target]
            while stack:
                target = stack.pop()
                if isinstance(target, ast.Name):
                    names.add(target.id)
                elif isinstance(target, (ast.Tuple, ast.List)):
                    stack.extend(target.elts)
                elif isinstance(target, ast.Starred):
                    stack.append(target.value)
    return names


#: Names that a module reads with no import or definition of its own.
_MODULE_ATTRS = {"__name__", "__file__", "__doc__", "__spec__", "__package__", "__loader__",
                 "__builtins__"}


def _reads(source):
    """The global names that *source* reads, annotations included, builtins aside."""
    reads = set()

    def walk(table, top):
        for sym in table.get_symbols():
            if sym.is_referenced() and (top or sym.is_global()):
                reads.add(sym.get_name())
        for child in table.get_children():
            walk(child, False)

    walk(symtable.symtable(source, "<module>", "exec"), True)
    for node in ast.walk(ast.parse(source)):
        notes = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            notes = [node.returns] + [a.annotation for a in args.posonlyargs + args.args
                                      + args.kwonlyargs + [args.vararg, args.kwarg] if a]
        elif isinstance(node, ast.AnnAssign):
            notes = [node.annotation]
        for note in filter(None, notes):
            reads.update(n.id for n in ast.walk(note) if isinstance(n, ast.Name))
    return reads - set(dir(builtins)) - _MODULE_ATTRS


def _imported(tree):
    """The names that the top-level imports of *tree* bind, `from __future__` aside."""
    names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names.update(a.asname or a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            names.update(a.asname or a.name for a in node.names)
    return names


def _instrument_files(path):
    """The value of `INSTRUMENT_FILES` in *path*, read by AST."""
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and getattr(node.targets[0], "id", "") == "INSTRUMENT_FILES"):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{path.name} binds no INSTRUMENT_FILES")


class TestPackageFiles(unittest.TestCase):
    """TC-01 — the files of the package."""

    def test_the_package_holds_init_and_the_12_modules(self):
        found = sorted(p.name for p in PACKAGE.glob("*.py"))
        self.assertEqual(found, sorted(["__init__.py"] + [f"{m}.py" for m in MODULES]))


class TestImports(unittest.TestCase):
    """TC-02 — the imports of each module."""

    def test_each_module_imports_only_modules_above_it(self):
        for index, module in enumerate(MODULES):
            for line, level, target in _imports(PACKAGE / f"{module}.py"):
                with self.subTest(module=module, line=line):
                    if level:
                        self.assertEqual(level, 1)
                        self.assertIn(target, MODULES[:index],
                                      f"{module}.py imports {target!r}, not a module above it")
                    else:
                        top = target.split(".")[0]
                        self.assertTrue(top in sys.stdlib_module_names or top == "mermaid_model",
                                        f"{module}.py imports {top!r}")

    def test_each_module_imports_exactly_the_names_its_code_reads(self):
        for module in MODULES:
            path = PACKAGE / f"{module}.py"
            source = path.read_text(encoding="utf-8")
            reads, imported = _reads(source), _imported(ast.parse(source))
            with self.subTest(module=module):
                self.assertEqual(sorted(imported - reads), [],
                                 f"{module}.py imports names that its code never reads")
                self.assertEqual(sorted(reads - imported - _bound_at_top(path)), [],
                                 f"{module}.py reads names that it neither defines nor imports")

    def test_init_holds_a_docstring_only(self):
        body = ast.parse((PACKAGE / "__init__.py").read_text(encoding="utf-8")).body
        self.assertEqual(len(body), 1, "__init__.py holds more than its docstring")
        self.assertIsInstance(body[0], ast.Expr)
        self.assertIsInstance(getattr(body[0].value, "value", None), str)


class TestNames(unittest.TestCase):
    """TC-03 — each name is defined in its module and bound on `svg_geometry`."""

    def test_each_name_is_defined_in_its_module_and_bound_on_svg_geometry(self):
        self.assertEqual(sum(len(names) for names in NAMES.values()), 119)
        self.assertEqual(tuple(NAMES), MODULES)
        for module, names in NAMES.items():
            defining = importlib.import_module(f"svg_geometry_parts.{module}")
            with self.subTest(module=module):
                self.assertEqual(_bound_at_top(PACKAGE / f"{module}.py"), set(names))
            for name in names:
                with self.subTest(module=module, name=name):
                    self.assertIs(getattr(sg, name), getattr(defining, name))

    def test_the_thin_file_defines_main_and_lists_every_name(self):
        self.assertEqual(_bound_at_top(SCRIPTS / "svg_geometry.py"), {"main", "__all__"})
        self.assertEqual(sg.main.__module__, "svg_geometry")
        every = [name for names in NAMES.values() for name in names] + ["main"]
        self.assertEqual(sg.__all__, every)


class TestInstrumentFiles(unittest.TestCase):
    """TC-04 — both INSTRUMENT_FILES name the thin file and each file of the package once."""

    def test_both_lists_name_each_file_of_the_package_once(self):
        for path in (SCRIPTS / "render_check.py", SKILL / "evals" / "render_corpus.py"):
            listed = _instrument_files(path)
            for rel in PACKAGE_FILES:
                with self.subTest(list=path.name, file=rel):
                    self.assertEqual(listed.count(rel), 1)
                    self.assertTrue((SKILL / rel).is_file())


if __name__ == "__main__":
    unittest.main()
