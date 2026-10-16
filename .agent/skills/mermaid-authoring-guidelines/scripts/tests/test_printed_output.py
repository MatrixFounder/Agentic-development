"""What the lint and the debug command line of svg_geometry.py print (TASK 123 R3, R4.1).

The lint quotes label text, ids and names in its findings and in its inventory. Before TASK 123 it
printed that text raw, and its `--json` left U+2028 and U+202E raw, so a figure could put a
terminal control sequence into the output. Now a printed line writes each non-printable character
as its Python escape, and JSON writes it as a JSON escape. Printable text, Cyrillic among it,
prints as it is. The lint holds copies of `json_text` and `_shown` of render_check.py, which it
does not import (TASK 123 D7); a test here pins each pair to one output.

The debug command line of svg_geometry.py prints ASCII JSON, and escapes its error lines with the
`_escaped` that the file binds from `svg_geometry_parts/api.py` (TASK 123 R4.1, TASK 125).
"""
import ast
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import lint_mermaid as lm  # noqa: E402
import render_check as rc  # noqa: E402
import svg_geometry as sg  # noqa: E402


def chars(*codes):
    return "".join(chr(c) for c in codes)


ESC, CSI, RLO, LSEP = chars(0x1B), chars(0x9B), chars(0x202E), chars(0x2028)
CYRILLIC = "Кириллица"
#: Label text with control characters, a bidirectional mark and a line separator. As an edge label
#: it is longer than the limit, so MA-LABEL-03 quotes it in its message.
HOSTILE = "Evil" + ESC + "[2J" + CSI + "7m" + RLO + "Z" + LSEP + " " + CYRILLIC + " words"


def non_printable(text):
    """The non-printable characters of *text*, a newline aside, as code points."""
    return sorted({hex(ord(ch)) for ch in text if not ch.isprintable() and ch != "\n"})


def call_lint(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = lm.main(argv)
    return code, out.getvalue(), err.getvalue()


def figure(body):
    return "## Figure\n\n```mermaid\nflowchart TB\n" + body + "\n```\n"


class LintCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def write(self, name, text):
        path = self.dir / name
        path.write_text(text, encoding="utf-8")
        return str(path)


class TestTheLintPrintsNoControlCharacter(LintCase):
    def test_a_finding_quotes_the_label_with_escapes(self):
        code, out, err = call_lint([self.write("edge.md", figure("  A -->|" + HOSTILE + "| B"))])
        self.assertEqual(non_printable(out + err), [])
        lines = [line for line in out.split("\n") if "MA-LABEL-03" in line]
        self.assertEqual(len(lines), 1, out)
        for ch in (ESC, CSI, RLO, LSEP):
            self.assertIn(ascii(ch)[1:-1], lines[0])
        self.assertIn(CYRILLIC, lines[0])

    def test_json_reads_back_to_the_message(self):
        code, out, err = call_lint(["--json", self.write("edge.md", figure("  A -->|" + HOSTILE + "| B"))])
        self.assertEqual(non_printable(out), [])
        self.assertIn(CYRILLIC, out)
        data = json.loads(out)
        message = next(f["message"] for f in data["findings"] if f["rule"] == "MA-LABEL-03")
        self.assertIn(ESC + "[2J" + CSI, message)
        self.assertIn(RLO + "Z" + LSEP, message)

    def test_the_inventory_table_and_its_json(self):
        path = self.write("node.md", figure('  A["' + HOSTILE + '"] --> B'))
        code, out, err = call_lint(["--inventory", path])
        self.assertEqual(non_printable(out + err), [])
        rows = [line for line in out.split("\n") if line.startswith("| node")]
        self.assertTrue(rows, out)
        code, out, err = call_lint(["--inventory", "--json", path])
        self.assertEqual(non_printable(out), [])
        texts = [row["text"] for block in json.loads(out)["figures"] for row in block["rows"]]
        self.assertIn(HOSTILE, texts)

    def test_a_newline_in_a_quoted_label_starts_no_line(self):
        # A finding quotes label text in its message, and a label of a markdown string may span
        # lines; the text output escapes the newline of the message (TASK 123 R3.3)
        label = HOSTILE + "\nsecond line"
        found = lm.Finding(rule="MA-LABEL-03", severity="warn", path="doc.md", line=5,
                           message="`" + label + "`: 52 characters > 24", hint="Keep it short.")
        text = lm._format_text([found], ["doc.md"])
        self.assertEqual(non_printable(text), [])
        lines = [line for line in text.split("\n") if "MA-LABEL-03" in line]
        self.assertEqual(len(lines), 1, text)
        self.assertIn(ascii("\n")[1:-1] + "second line", lines[0])
        self.assertNotIn("\nsecond line", text)

    def test_the_inventory_of_a_path_with_a_newline_forges_no_line(self):
        # `_cell` turns a newline of a label into a space; the header of a block quotes the path,
        # so only the escape of each line keeps a newline there from starting a line (TASK 123 R3.3)
        path = self.write("a\nFORGED" + ESC + ".md", figure('  A["' + HOSTILE + '"] --> B'))
        code, out, err = call_lint(["--inventory", path])
        self.assertEqual(non_printable(out + err), [])
        self.assertFalse([line for line in out.split("\n") if line.startswith("FORGED")], out)
        self.assertIn("a" + ascii("\n")[1:-1] + "FORGED" + ascii(ESC)[1:-1], out)
        rows = [line for line in out.split("\n") if line.startswith("| node")]
        self.assertTrue(any(ascii(ESC)[1:-1] in row for row in rows), rows)
        code, out, err = call_lint(["--inventory", "--json", path])
        self.assertEqual(non_printable(out), [])
        self.assertEqual(json.loads(out)["figures"][0]["path"], path)

    def test_a_newline_in_a_path_starts_no_line(self):
        path = self.write("a\nb" + ESC + ".md", figure("  A -->|" + HOSTILE + "| B"))
        code, out, err = call_lint([path])
        self.assertEqual(non_printable(out + err), [])
        self.assertNotIn("\nb", out)
        self.assertIn("a" + ascii("\n")[1:-1] + "b" + ascii(ESC)[1:-1], out)

    def test_the_usage_error_of_a_path_it_cannot_read(self):
        missing = str(self.dir / ("gone\n" + ESC + ".md"))
        code, out, err = call_lint([missing])
        self.assertEqual(code, lm.EXIT_USAGE)
        self.assertEqual(non_printable(err), [])
        self.assertEqual(err.count("\n"), 1, err)

    def test_the_usage_error_of_probe_with_a_path_goes_through_shown(self):
        # The line quotes no input; it goes through `_shown` as every line does (TASK 123 R3.2)
        with mock.patch.object(lm, "_shown", wraps=lm._shown) as shown:
            code, out, err = call_lint(["--probe", str(self.dir / ("x" + ESC + ".md"))])
        self.assertEqual(code, lm.EXIT_USAGE)
        self.assertEqual(non_printable(err), [])
        self.assertTrue(any("--probe takes no paths" in str(c.args[0]) for c in shown.call_args_list),
                        shown.call_args_list)

    def test_the_internal_error_line(self):
        failure = lm.LintInternalError("rule MA-X failed on " + HOSTILE + "\nforged line")
        # the probes run lint_text too; they stay live, so the failure reaches the linted file
        with mock.patch.object(lm, "run_probes", return_value=[]), \
                mock.patch.object(lm, "lint_text", side_effect=failure):
            code, out, err = call_lint([self.write("doc.md", figure("  A --> B"))])
        self.assertEqual(code, lm.EXIT_INTERNAL)
        self.assertEqual(non_printable(err), [])
        self.assertEqual(err.count("\n"), 1, err)


class TestOnlySayPrints(unittest.TestCase):
    """TASK 123 R3.2, R3.3: every line of the lint goes through `_say`. The lint's code is the thin
    file and every module of `lint_mermaid_parts` (TASK 126 R3)."""

    @classmethod
    def setUpClass(cls):
        thin = Path(lm.__file__)
        package = sorted((thin.parent / "lint_mermaid_parts").glob("*.py"))
        assert package, "lint_mermaid_parts holds no module"
        cls.tree = ast.Module(body=[node for path in [thin, *package]
                                    for node in ast.parse(path.read_text(encoding="utf-8")).body],
                              type_ignores=[])

    def test_the_only_print_is_the_one_in_say(self):
        # every call of the module, at any depth: each `print` lies in `_say`, and nothing writes
        # to `sys.stdout` or `sys.stderr` directly
        owner = {}
        for fn in ast.walk(self.tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for node in ast.walk(fn):
                    owner.setdefault(id(node), fn.name)
        prints, writes = [], []
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                prints.append(owner.get(id(node), "<module>"))
            text = ast.unparse(node.func)
            if text in ("sys.stdout.write", "sys.stderr.write"):
                writes.append(owner.get(id(node), "<module>") + ": " + text)
        self.assertEqual(prints, ["_say"])
        self.assertEqual(writes, [])
        # TASK 123 D7: the lint holds its own copies, so its rule runs none of these; the
        # geometry's code lies in `svg_geometry_parts` since TASK 125
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(sorted(imported & {"render_check", "svg_geometry", "svg_geometry_parts"}),
                         [])

    def test_lines_go_only_with_json_or_escaped_lines(self):
        allowed = {"_json_text", "_format_text", "_format_inventory"}
        kept = []
        for node in ast.walk(self.tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "_say"):
                continue
            keeps = any(k.arg == "lines" for k in node.keywords) or len(node.args) > 2
            if keeps:
                first = node.args[0]
                kept.append(first.func.id if isinstance(first, ast.Call)
                            and isinstance(first.func, ast.Name) else ast.unparse(first))
        self.assertTrue(kept)
        self.assertEqual(sorted(set(kept) - allowed), [])


class TestTheCopiesAgree(unittest.TestCase):
    """TASK 123 D7: the lint's copies give the output of render_check.py's functions."""

    PROBE = "".join(chr(c) for c in range(0x110000))

    def test_json_text(self):
        self.assertEqual(lm._json_text(self.PROBE), rc.json_text(self.PROBE))
        self.assertEqual(lm._json_text({"k": [self.PROBE]}, indent=2),
                         rc.json_text({"k": [self.PROBE]}, indent=2))

    def test_shown(self):
        self.assertEqual(lm._shown(self.PROBE), rc._shown(self.PROBE))
        self.assertEqual(lm._shown(self.PROBE, True), rc._shown(self.PROBE, True))


class TestSvgGeometryCommandLine(unittest.TestCase):
    """TASK 123 R4.1: the debug command line prints ASCII JSON and escaped error lines."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.svg = Path(tmp.name) / "fig.svg"
        self.svg.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")

    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sg.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_the_json_is_ascii_and_reads_back(self):
        metrics = {"labels": [HOSTILE + chr(0xD800)]}
        with mock.patch.object(sg, "analyze_svg", return_value=metrics), \
                mock.patch.object(sg, "evaluate", return_value=[]), \
                mock.patch.object(sg, "passes", return_value=True):
            code, out, err = self.run_main([str(self.svg)])
        self.assertEqual(code, 0, err)
        self.assertTrue(out.isascii(), out[:200])
        self.assertEqual(json.loads(out)["metrics"], metrics)

    def test_an_error_line_holds_no_control_character(self):
        failure = ValueError("bad path data near " + HOSTILE + "\nforged line")
        with mock.patch.object(sg, "analyze_svg", side_effect=failure):
            code, out, err = self.run_main([str(self.svg)])
        self.assertEqual(code, 2)
        self.assertEqual(non_printable(err), [])
        self.assertEqual(err.count("\n"), 1, err)


if __name__ == "__main__":
    unittest.main()
