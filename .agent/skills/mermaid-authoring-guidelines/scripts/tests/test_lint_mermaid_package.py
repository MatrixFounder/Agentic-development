"""Tests of the package `lint_mermaid_parts` (TASK 126 R3).

`lint_mermaid.py` keeps its command line and became a thin file over `scripts/lint_mermaid_parts/`:
one module per section of the former file. The thin file imports the 17 modules in order, binds
every top-level name of them and holds the command line, from `_summary` to `main` (TASK 126 R1,
R2). These tests pin:

* the package's files: `__init__.py` and the 17 modules (``TC-01``);
* each module imports exactly the names that its code reads: relatively only from the modules above
  it, and absolutely only the standard library, `mermaid_model` and `planarity`. `__init__.py` holds
  a docstring only (``TC-02``);
* each of the 158 names of the package is defined in its module and bound on `lint_mermaid` to the
  same object. The thin file defines the 11 names of the command line and `__all__`, which lists
  the 169 names (``TC-03``);
* `RULES` holds the rules in the order of the modules and of their sources, and each rule lies in
  the module of its family (``TC-04``). The thin file imports each name from its module, in the
  order of the modules (``TC-03``).

The helpers that the package tests share lie in `package_checks.py` (TASK 126 R3).
"""
import ast
import importlib
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(SCRIPTS), str(Path(__file__).resolve().parent)]
import lint_mermaid as lm  # noqa: E402
from package_checks import (bound_at_top, docstring_only, import_mismatch,  # noqa: E402
                            imports)

PACKAGE = SCRIPTS / "lint_mermaid_parts"
#: TASK 126 R1: the modules of the package, in order; each imports only from those above it.
MODULES = ("base", "parse", "syntax", "settings", "ids", "budget", "flowchart", "state", "sequence",
           "labels", "classes", "gantt", "ascii_figures", "doc", "model", "negatives", "engine")
#: Absolute imports that a module of the package may hold besides the standard library.
LOCAL = {"mermaid_model", "planarity"}
#: TASK 126 TC-03: the top-level names of the former file, by the module that defines each.
NAMES = {
    "base": ("EXIT_OK", "EXIT_FINDINGS", "EXIT_INTERNAL", "EXIT_USAGE", "Finding", "Rule", "RULES",
             "FAMILY_PREFIXES", "LintContext", "LintInternalError", "rule", "ASCII", "_doc",
             "_hazard_check", "_fig_line", "_lines_of"),
    "parse": ("_check_phantom",),
    "syntax": ("_unsupported_kinds", "_avoid_only_kinds", "_kind_probe", "_check_kind_floor",
               "_check_kind_avoid", "_check_unknown"),
    "settings": ("_check_directive", "_check_frontmatter", "_theme_pattern", "_check_sanitizer",
                 "_check_toplevel_font", "_check_theme", "_SETTINGS_KEY", "_notation_settings",
                 "_settings_probe", "_no_themecss_probe", "_PINNED_SETTINGS", "_QUOTED_SETTING_MAX",
                 "_check_pinned", "_settings_signature", "_check_settings_consistency"),
    "ids": ("_check_edge_ids", "_figure_ids", "_check_id_shape"),
    "budget": ("_COUNT_BUDGETS", "_budget_values", "_budget_findings", "_chain", "_budget_probe",
               "_check_soft_budget", "_check_hard_budget"),
    "flowchart": ("_visible_edges", "_decision_flow", "_edge_directions", "_check_duplicate_edges",
                  "_check_subgraph_edge", "_check_small_subgraph", "_NUMBERED", "_numbered_probe",
                  "_check_numbered", "_check_planarity", "_lr_probe", "_check_lr"),
    "state": ("_check_composite_cross", "_state_end", "_check_duplicate_transitions"),
    "sequence": ("_skip_probe", "_check_skip", "_phase_probe"),
    "labels": ("_label_probe", "_lines_probe", "_node_label_items", "_edge_label_items",
               "_check_node_line1", "_check_node_line2", "_check_edge_label", "_check_message",
               "_check_note", "_check_gantt_label", "_LETTERS", "_drawn_names", "_starts_uppercase",
               "_check_edge_case", "_check_node_lines", "_check_message_lines",
               "_check_participant", "_check_note_lines", "_check_edge_lines",
               "_check_participant_lines", "_html_label_items", "_SMALL_TAG", "_escaped",
               "_check_small"),
    "classes": ("_HEX", "_FUNC_COLOUR", "_CSS_NAMED", "_channel", "_hsl_to_rgb", "_rgba", "_over",
                "_luminance", "contrast_ratio", "_style_contrast", "_style_blocks",
                "_check_contrast", "_class_uses", "_class_defs", "_check_undefined_class",
                "_check_unused_class", "_theme_text_contrasts", "_check_fill_without_color"),
    "gantt": ("_GANTT_HEAD", "_check_after", "_check_dotted_after", "_check_repeated_section",
              "_check_axis", "_check_today", "_check_bare_duration"),
    "ascii_figures": ("_check_tabs", "_check_wide", "_width_probe", "_check_width", "_check_ragged",
                      "_ascii_probe", "_ascii_elements", "_check_ascii_budget",
                      "_check_ascii_hard_budget", "_check_connector_drift"),
    "doc": ("_in_document", "_legend_reasons", "_check_caption", "_check_caption_below",
            "_encodings", "_legend_encodings", "_TWO_CLASSES", "_check_legend",
            "_check_class_consistency", "_check_alias_consistency"),
    "model": ("_check_unread",),
    "negatives": ("_marker", "_is_negative", "_named_rule_ids", "_inside", "_nameable_rules",
                  "classify_marker_name", "_fires_on", "_NEG_NAMES_HINT", "_check_negative_fires",
                  "_check_marker_shape", "_check_marker_ignored"),
    "engine": ("_figure_at", "_rule_results", "lint_figures", "lint_text", "_probe_text",
               "run_probes", "_NUMBER", "_rows_numbers", "inventory", "inventoried", "counts"),
}
#: TASK 126 R1: the family of rules that each module registers.
FAMILIES = {"parse": "PARSE", "syntax": "SYN", "settings": "SET", "ids": "ID", "budget": "BUDGET",
            "flowchart": "FLOW", "state": "STATE", "sequence": "SEQ", "labels": "LABEL",
            "classes": "CLASS", "gantt": "GANTT", "ascii_figures": "ASCII", "doc": "DOC",
            "model": "MODEL", "negatives": "NEG"}
#: TASK 126 R2: the names of the command line, which the thin file defines.
COMMAND_LINE = ("_summary", "_json_text", "_shown", "_say", "_finding_line", "_finding_dict",
                "_format_text", "_cell", "_format_inventory", "build_parser", "main")


def _is_rule_call(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "rule" and bool(node.args))


def _rule_ids(path):
    """The id of each rule that *path* registers, in source order: with the decorator
    `@rule(...)`, or with a top-level statement `rule(...)(check)`."""
    ids = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        calls = [deco for deco in getattr(node, "decorator_list", []) if _is_rule_call(deco)]
        if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and _is_rule_call(node.value.func)):
            calls.append(node.value.func)
        ids.extend(ast.literal_eval(call.args[0]) for call in calls)
    return ids


class TestPackageFiles(unittest.TestCase):
    """TC-01 — the files of the package."""

    def test_the_package_holds_init_and_the_17_modules(self):
        found = sorted(p.name for p in PACKAGE.glob("*.py"))
        self.assertEqual(found, sorted(["__init__.py"] + [f"{m}.py" for m in MODULES]))


class TestImports(unittest.TestCase):
    """TC-02 — the imports of each module."""

    def test_each_module_imports_only_modules_above_it(self):
        for index, module in enumerate(MODULES):
            for line, level, target, _names in imports(PACKAGE / f"{module}.py"):
                with self.subTest(module=module, line=line):
                    if level:
                        self.assertEqual(level, 1)
                        self.assertIn(target, MODULES[:index],
                                      f"{module}.py imports {target!r}, not a module above it")
                    else:
                        top = target.split(".")[0]
                        self.assertTrue(top in sys.stdlib_module_names or top in LOCAL,
                                        f"{module}.py imports {top!r}")

    def test_each_module_imports_exactly_the_names_its_code_reads(self):
        for module in MODULES:
            unused, missing = import_mismatch(PACKAGE / f"{module}.py")
            with self.subTest(module=module):
                self.assertEqual(unused, [], f"{module}.py imports names that its code never reads")
                self.assertEqual(missing, [], f"{module}.py reads names that it neither defines "
                                              "nor imports")

    def test_init_holds_a_docstring_only(self):
        self.assertTrue(docstring_only(PACKAGE / "__init__.py"),
                        "__init__.py holds more than its docstring")


class TestNames(unittest.TestCase):
    """TC-03 — each name is defined in its module and bound on `lint_mermaid`."""

    def test_each_name_is_defined_in_its_module_and_bound_on_lint_mermaid(self):
        self.assertEqual(sum(len(names) for names in NAMES.values()), 158)
        self.assertEqual(tuple(NAMES), MODULES)
        for module, names in NAMES.items():
            defining = importlib.import_module(f"lint_mermaid_parts.{module}")
            with self.subTest(module=module):
                self.assertEqual(bound_at_top(PACKAGE / f"{module}.py"), set(names))
            for name in names:
                with self.subTest(module=module, name=name):
                    self.assertIs(getattr(lm, name), getattr(defining, name))

    def test_the_thin_file_defines_the_command_line_and_lists_every_name(self):
        self.assertEqual(bound_at_top(SCRIPTS / "lint_mermaid.py"), set(COMMAND_LINE) | {"__all__"})
        self.assertEqual(lm.main.__module__, "lint_mermaid")
        every = [name for names in NAMES.values() for name in names] + list(COMMAND_LINE)
        self.assertEqual(lm.__all__, every)

    def test_the_thin_file_imports_each_name_from_its_module_in_order(self):
        thin = imports(SCRIPTS / "lint_mermaid.py")
        found = [(module, names) for _line, level, module, names in thin
                 if level == 0 and (module or "").startswith("lint_mermaid_parts.")]
        self.assertEqual(found, [(f"lint_mermaid_parts.{m}", NAMES[m]) for m in MODULES])


class TestRuleOrder(unittest.TestCase):
    """TC-04 — `RULES` holds the rules in the order of the modules and of their sources: the thin
    file imports the modules in order, and each module registers its rules as it runs."""

    def test_rules_follow_the_modules_and_their_sources(self):
        expected = [rule_id for module in MODULES
                    for rule_id in _rule_ids(PACKAGE / f"{module}.py")]
        self.assertEqual([r.id for r in lm.RULES], expected)

    def test_each_rule_lies_in_the_module_of_its_family(self):
        for module in MODULES:
            for rule_id in _rule_ids(PACKAGE / f"{module}.py"):
                with self.subTest(module=module, rule=rule_id):
                    self.assertEqual(rule_id.split("-")[1], FAMILIES.get(module))


if __name__ == "__main__":
    unittest.main()
