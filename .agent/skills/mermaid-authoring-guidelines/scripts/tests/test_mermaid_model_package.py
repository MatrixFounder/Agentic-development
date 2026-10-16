"""Tests of the package `mermaid_model` (TASK 124 R4).

`mermaid_model.py` became the package `scripts/mermaid_model/`: one module per section of the
former file, and `__init__.py`, which holds the entry points and binds every top-level name of the
15 modules (TASK 124 R1). These tests pin:

* the package's files: `__init__.py` and the 15 modules, and no former file (``TC-01``);
* each module imports only from the modules above it, and `__init__.py` imports each module in
  that order (``TC-02``);
* each of the 230 top-level names of the former file is defined in its module and bound on
  `mermaid_model` to the same object (``TC-03``);
* `SKILL_DIR` names the skill directory, and `NOTATION_PATH` an existing file (``TC-04``);
* `INSTRUMENT_FILES` of `evals/render_corpus.py`, read by AST, names each file of the package once
  and not the former file (``TC-05``);
* `NEGATIVE_ROOTS` assigned on `sys.modules[mm.negative_allowed.__module__]` reaches
  `negative_allowed` (``TC-06``);
* the skill stays self-contained: each absolute import of a script of `scripts/` and of a module of
  the package names a standard-library module or a module of `scripts/` (``TC-07``).

A top-level name is one that a top-level `def`, `class` or assignment binds, each name of a tuple
target included and imported names excluded (TASK 124 §0).
"""
import ast
import importlib
import inspect
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import mermaid_model as mm  # noqa: E402

PACKAGE = SCRIPTS / "mermaid_model"
#: TASK 124 R1.1: the modules of the package; each imports only from those above it.
MODULES = ("base", "document", "figure", "hazards", "labels", "kinds", "settings", "preprocessing",
           "flowchart", "sequence", "state", "gantt", "er", "other_kinds", "ascii_figures")
#: TASK 124 R3.1: the files of the package that INSTRUMENT_FILES names, `__init__.py` first.
PACKAGE_FILES = tuple(f"scripts/mermaid_model/{m}.py" for m in ("__init__",) + MODULES)
#: TASK 124 TC-03: the top-level names of the former file, by the module that defines each.
NAMES = {
    "base": ("SKILL_DIR", "NOTATION_PATH", "FIGURE_LANGS", "RENDER_CHECK_NAMES",
             "NEGATIVE_MARKER", "NEGATIVE_ROOTS", "negative_allowed", "load_notation"),
    "document": ("Paragraph", "NegativeMarker", "Fence", "negative_markers", "_ATX_HEADING",
                 "_SETEXT_UNDERLINE", "_THEMATIC_BREAK", "_COMMENT_LINE", "_QUOTE_MARK",
                 "_LIST_ITEM", "_TABLE_ROW", "_CM_FENCE", "_CM_CLOSE", "_CM_ATX", "_CM_SETEXT",
                 "_CM_BREAK", "_CM_BULLET", "_CM_ORDERED", "_CM_SPECIAL", "_HTML_BLOCK_NAMES",
                 "_HTML_ATTRIBUTE", "_HTML_BLOCKS", "_Span", "_quote_strip", "_Line", "_Block",
                 "_list_item", "_html_kind", "_BlockScan", "code_line_reader", "_scan",
                 "_fence_spans", "_is_boundary", "_paragraph_before", "_paragraph_after",
                 "fence_sha256", "normalize_text", "fence_matches", "extract_fences",
                 "figure_from_mmd"),
    "figure": ("Settings", "Node", "Edge", "Subgraph", "Flowchart", "Participant", "Message",
               "Note", "Block", "Sequence", "StateNode", "Transition", "StateDiagram",
               "GanttTask", "Gantt", "ErEntity", "ErRelation", "ErDiagram", "AsciiBox",
               "AsciiBlock", "Hazard", "Figure"),
    "hazards": ("HAZARD_CODES", "ACC_UNSUPPORTED_KINDS", "ALLOWED_TAGS", "_TAGLIKE", "_bad_tags",
                "_ENTITY", "_printable_entity", "_strip_entities"),
    "labels": ("_BR", "_ANY_TAG", "_MD_EMPHASIS", "_decode_entities", "label_lines", "word_count",
               "char_count", "_EMOJI_PRESENTATION", "char_widths", "display_width"),
    "kinds": ("KIND_OF_KEYWORD", "OTHER_KEYWORDS", "diagram_keyword", "_known_keywords"),
    "settings": ("_DIRECTIVE", "_parse_directive", "YamlError", "_yaml_scalar", "_yaml_quoted",
                 "_yaml_flow", "_YAML_KEY", "parse_yaml", "_yaml_value_text", "_yaml_unclosed",
                 "_yaml_join_continuations", "_yaml_block", "_yaml_value_after_key", "_yaml_map",
                 "_yaml_seq"),
    "preprocessing": ("_body_lines", "_YAML_HEX_COMMENT", "_take_settings", "_take_accessibility",
                      "detect_kind"),
    "flowchart": ("_DIRECTIONS", "_SHAPE_OPENERS", "_LINK_FULL", "_LINK_TEXT_START",
                  "_EDGE_ID_PREFIX", "_ID_STOP", "_CLASS_NAME", "_BRACKET_CHARS",
                  "_split_statements", "_parse_props", "_Frame", "_FlowParser",
                  "_join_open_quotes", "_comment_start", "_find_first", "_matching_brace",
                  "flowchart_edge_ids"),
    "sequence": ("_SEQ_ARROWS", "_SEQ_MESSAGE", "_SEQ_PARTICIPANT", "_SEQ_NOTE", "_SEQ_BLOCK",
                 "_SEQ_CONT", "_SEQ_BOX", "_COLOR_PREFIX", "_HEX_COLOUR_START", "_seq_message",
                 "_seq_text_hazards", "_parse_sequence"),
    "state": ("_STATE_TRANSITION", "_STATE_DECL", "_STATE_DESC", "_STATE_NOTE", "_STATE_CLASS",
              "_state_label_hazards", "_split_class_suffix", "_parse_state", "_first_label_colon",
              "state_parent_chain"),
    "gantt": ("GANTT_TAGS", "_parse_gantt", "gantt_refs"),
    "er": ("_ER_RELATION", "_ER_ENTITY_OPEN", "_STYLING_DETAIL", "_STYLING_STATEMENT",
           "_styling_statement", "_parse_er"),
    "other_kinds": ("_CLASS_LINK", "_CLASS_SKIP", "_class_name", "_count_classes",
                    "_count_mindmap", "_count_timeline", "_count_journey", "_count_gitgraph",
                    "_COUNTERS", "_class_items", "_MINDMAP_NODE", "_mindmap_items",
                    "_timeline_items", "_journey_items", "_gitgraph_items", "_pie_items",
                    "_ITEMS", "ITEM_KINDS", "THEME_KINDS", "_THEME_STYLING", "_THEME_STATEMENT",
                    "OTHER_SCANNED_KINDS", "_scan_other"),
    "ascii_figures": ("_BOX_TOP_LEFT", "_BOX_TOP_RIGHT", "_BOX_BOTTOM_LEFT", "_BOX_BOTTOM_RIGHT",
                      "_BOX_HORIZONTAL", "_BOX_VERTICAL", "_TOP_JUNCTION", "_BOTTOM_JUNCTION",
                      "_SIDE_JUNCTION", "_LAYER_LEFT", "_LAYER_RIGHT", "_ALIGN_CHARS",
                      "_SEGMENT_SPLIT", "_ARROW_TOKEN", "_COLUMN_GAP", "_FORK_GLYPHS",
                      "_JOIN_GLYPHS", "_MERGE_GLYPHS", "_JOIN_CANDIDATES", "_ARROWHEADS",
                      "_DOWN_ARROWHEADS", "_box_strokes", "_UP_STROKE", "_DOWN_STROKE", "_cells",
                      "_segments", "_anchors", "_Grid", "_drift", "_arrow_after", "_turns_down",
                      "_arrow_below", "_frame_bottom", "_forks", "_joins", "_parse_ascii",
                      "_find_boxes", "_text_between", "_claim_box", "_BOX_SIDE", "_BOX_EDGE",
                      "_border_end", "_trace_box"),
    "__init__": ("parse_figure", "_timeline_header", "parse_document", "parse_path"),
}


def _imports(path):
    """(line, level, module, names) of each import statement of *path*, at any depth."""
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom):
            found.append((node.lineno, node.level, node.module, tuple(a.name for a in node.names)))
        elif isinstance(node, ast.Import):
            found.extend((node.lineno, 0, a.name, ()) for a in node.names)
    return found


def _bound_at_top(path):
    """The names that a top-level `def`, `class` or assignment of *path* binds, each name of a
    tuple target included; an imported name is not among them."""
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


class TestPackageFiles(unittest.TestCase):
    """TC-01 — the files of the package."""

    def test_the_package_holds_init_and_the_15_modules(self):
        self.assertTrue(hasattr(mm, "__path__"), f"mermaid_model is no package: {mm.__file__}")
        self.assertEqual(Path(mm.__file__).resolve(), (PACKAGE / "__init__.py").resolve())
        self.assertEqual(sorted(p.name for p in PACKAGE.glob("*.py")),
                         sorted(f"{m}.py" for m in ("__init__",) + MODULES))
        self.assertFalse((SCRIPTS / "mermaid_model.py").exists(), "the former file remains")


class TestImportOrder(unittest.TestCase):
    """TC-02 — a module imports only modules above it; `__init__.py` imports each in order."""

    def test_each_module_imports_only_modules_above_it(self):
        for k, module in enumerate(MODULES):
            with self.subTest(module=module):
                for line, level, target, _names in _imports(PACKAGE / f"{module}.py"):
                    if level == 0:
                        self.assertNotEqual((target or "").split(".")[0], "mermaid_model",
                                            f"{module}.py:{line} imports the package itself")
                        continue
                    self.assertEqual(level, 1, f"{module}.py:{line} reaches above the package")
                    self.assertIn(target, MODULES[:k],
                                  f"{module}.py:{line} imports {target!r}, not a module above it")

    def test_init_imports_each_module_in_order(self):
        targets = [t for _l, level, t, _n in _imports(PACKAGE / "__init__.py") if level == 1]
        self.assertEqual(targets, list(MODULES))


class TestNames(unittest.TestCase):
    """TC-03 — each top-level name of the former file, in its module and on the package."""

    def test_each_name_is_defined_in_its_module_and_bound_on_the_package(self):
        self.assertEqual(sum(len(v) for v in NAMES.values()), 230)
        for module, names in NAMES.items():
            full = "mermaid_model" if module == "__init__" else f"mermaid_model.{module}"
            with self.subTest(module=module):
                sub = importlib.import_module(full)
                bound = _bound_at_top(PACKAGE / f"{module}.py")
                for name in names:
                    self.assertIn(name, bound, f"{full} imports {name} and does not define it")
                    self.assertTrue(hasattr(sub, name), f"{full} lacks {name}")
                    obj = getattr(sub, name)
                    self.assertIs(getattr(mm, name, None), obj, f"mermaid_model.{name}")
                    if inspect.isfunction(obj) or inspect.isclass(obj):
                        self.assertEqual(obj.__module__, full,
                                         f"{full}.{name} comes from elsewhere")


class TestPaths(unittest.TestCase):
    """TC-04 — `SKILL_DIR` names the skill directory, and `NOTATION_PATH` an existing file."""

    def test_skill_dir_and_notation_path(self):
        self.assertEqual(Path(mm.SKILL_DIR).resolve(), SKILL.resolve())
        self.assertTrue(Path(mm.NOTATION_PATH).is_file(), mm.NOTATION_PATH)


class TestInstrumentFiles(unittest.TestCase):
    """TC-05 — `INSTRUMENT_FILES` of `evals/render_corpus.py`, read by AST, without an import."""

    def test_render_corpus_hashes_each_file_of_the_package(self):
        tree = ast.parse((SKILL / "evals" / "render_corpus.py").read_text(encoding="utf-8"))
        values = [ast.literal_eval(node.value) for node in tree.body
                  if isinstance(node, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "INSTRUMENT_FILES"
                          for t in node.targets)]
        self.assertEqual(len(values), 1, "render_corpus.py binds INSTRUMENT_FILES once")
        files = list(values[0])
        self.assertNotIn("scripts/mermaid_model.py", files)
        for path in PACKAGE_FILES:
            self.assertEqual(files.count(path), 1, f"INSTRUMENT_FILES names {path} not once")
        self.assertEqual([f for f in files if f.startswith("scripts/mermaid_model/")],
                         list(PACKAGE_FILES))


class TestPatchWhereLookedUp(unittest.TestCase):
    """TC-06 — `NEGATIVE_ROOTS`, assigned on the module whose code reads it, reaches the code."""

    def test_an_assignment_on_the_looking_up_module_reaches_negative_allowed(self):
        home = sys.modules[mm.negative_allowed.__module__]
        saved = home.NEGATIVE_ROOTS
        with tempfile.TemporaryDirectory() as tmp:
            inside = Path(tmp, "doc.md")
            inside.write_text("x\n", encoding="utf-8")
            self.assertFalse(mm.negative_allowed(inside))
            home.NEGATIVE_ROOTS = (Path(tmp),)
            try:
                self.assertTrue(mm.negative_allowed(inside))
            finally:
                home.NEGATIVE_ROOTS = saved


class TestSelfContained(unittest.TestCase):
    """TC-07 — the skill stays self-contained (TASK 124 R1.8, D12)."""

    def test_each_import_stays_in_the_skill_or_the_standard_library(self):
        local = ({p.stem for p in SCRIPTS.glob("*.py")}
                 | {p.name for p in SCRIPTS.iterdir() if (p / "__init__.py").is_file()})
        files = sorted(SCRIPTS.glob("*.py")) + sorted(PACKAGE.glob("*.py"))
        self.assertTrue(files, "no script found")
        for path in files:
            for line, level, target, _names in _imports(path):
                if level:
                    continue  # TC-02 reads the relative imports of the package
                top = (target or "").split(".")[0]
                with self.subTest(file=path.name, line=line):
                    self.assertTrue(top in sys.stdlib_module_names or top in local,
                                    f"{path.name}:{line} imports {top!r} from outside the skill")


if __name__ == "__main__":
    unittest.main()
