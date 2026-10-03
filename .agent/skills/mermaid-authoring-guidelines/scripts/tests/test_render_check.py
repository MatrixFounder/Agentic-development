"""Tests for render_check.py (TASK 108, R7.4, R7.7, R7.8, R7.9, R9.4; acceptance A17).

The first class runs the script as a process with an empty install home: it must report
`not rendered` and exit 2 before it needs node (A17). The stubbed classes call the module with a
stand-in for `render`, so the run logic is checked without renderers: the skipped dark render,
negative fences and their scope, forward renders, figures whose geometry is not modelled,
inputs with no fence, the evidence fields, the mmdc command line and the fixture file. The
classes after them check the parts that decide exit 0, 1 or 2 with no browser: the renderer
config, the private directories, the install lookup, the failure classes, and `render` itself
driven by stand-in `mmdc` and `node` programs, which record the directory they run in. The last
class renders with the installed pinned renderers and is skipped when they are absent. It checks
what only the browser measures: a name taller than its box, the lines of one name, the smallest
text, and text past the figure's edge; and that a puppeteer configuration of the caller's
directory never runs.
"""
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(SCRIPTS))
import mermaid_model as mm  # noqa: E402
import render_check as rc  # noqa: E402
import svg_geometry as sg  # noqa: E402

NOTATION = mm.load_notation()
SCRIPT = SCRIPTS / "render_check.py"
FLOW = "flowchart TB\n  A --> B\n"
TREE_SVG = (HERE / "fixtures" / "fx-tree-v11.svg").read_text(encoding="utf-8")
CAN_CHMOD = hasattr(os, "geteuid") and os.geteuid() != 0  # root ignores a read-only directory


def temp_dir(test):
    d = tempfile.TemporaryDirectory()
    test.addCleanup(d.cleanup)
    return Path(d.name)


def set_env(test, **values):
    """Set (or, with None, unset) environment variables for one test."""
    for key, value in values.items():
        old = os.environ.get(key)
        test.addCleanup(lambda k=key, v=old: os.environ.pop(k, None) if v is None
                        else os.environ.__setitem__(k, v))
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def read_only(test, path):
    path.chmod(stat.S_IRUSR | stat.S_IXUSR)
    test.addCleanup(path.chmod, stat.S_IRWXU)


class TestNotRenderedWithoutInstalls(unittest.TestCase):
    """A17: an empty MERMAID_RENDER_HOME gives exit 2 and a `not rendered:` line."""

    def run_script(self, *args):
        home = temp_dir(self)
        fig = home / "fig.mmd"
        fig.write_text(FLOW, encoding="utf-8")
        env = dict(os.environ, MERMAID_RENDER_HOME=str(home / "empty"))
        return subprocess.run([sys.executable, str(SCRIPT), str(fig), *args], env=env,
                              capture_output=True, text=True, timeout=60)

    def test_text_output(self):
        proc = self.run_script()
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertTrue(any(line.startswith("not rendered: ") for line in proc.stdout.splitlines()),
                        proc.stdout)
        self.assertNotIn("pass", proc.stdout.lower().replace("passed", ""))

    def test_json_output(self):
        proc = self.run_script("--json")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertEqual(report["exit"], 2)
        self.assertEqual(sorted(report["missing"]), sorted(NOTATION["renderers"]["check_pair"]))
        self.assertTrue(proc.stderr.startswith("not rendered: "), proc.stderr)

    def test_usage_errors_exit_3(self):
        fig = temp_dir(self) / "fig.mmd"
        fig.write_text(FLOW, encoding="utf-8")
        with redirect_stderr(io.StringIO()) as err:
            self.assertEqual(rc.main([]), 3)
            self.assertEqual(rc.main(["/nonexistent/fig.mmd"]), 3)
            self.assertEqual(rc.main([str(SCRIPT)]), 3)
            self.assertEqual(rc.main([str(fig), "--versions", "v99"]), 3)
            self.assertEqual(rc.main([str(fig), "--fixture", str(fig.parent / "no-dir" / "x.json")]), 3)
            self.assertEqual(rc.main([str(fig), "--fixture", str(fig.parent / "x.txt")]), 3)
        self.assertIn("unknown version tag(s): v99", err.getvalue())

    def test_out_inside_a_git_work_tree_is_refused(self):
        fig = temp_dir(self) / "fig.mmd"
        fig.write_text(FLOW, encoding="utf-8")
        inside = SCRIPTS / "renders-must-not-land-here"
        if not rc.inside_git_work_tree(inside):
            self.skipTest("the skill is not inside a git work tree here")
        with redirect_stderr(io.StringIO()) as err:
            self.assertEqual(rc.main([str(fig), "--out", str(inside)]), 3)
        self.assertFalse(inside.exists())
        self.assertIn("git work tree", err.getvalue())

    def test_a_missing_directory_and_dotdot_do_not_hide_a_work_tree(self):
        # `missing/../repo` reaches the repository once mkdir has made `missing`
        tmp = temp_dir(self).resolve()
        (tmp / "repo" / ".git").mkdir(parents=True)
        sneaky = tmp / "missing" / ".." / "repo" / "renders"
        self.assertTrue(rc.inside_git_work_tree(sneaky))
        fig = tmp / "fig.mmd"
        fig.write_text(FLOW, encoding="utf-8")
        with redirect_stderr(io.StringIO()):
            self.assertEqual(rc.main([str(fig), "--out", str(sneaky)]), 3)
        self.assertFalse((tmp / "missing").exists())
        self.assertFalse((tmp / "repo" / "renders").exists())

    def test_a_symlink_into_a_work_tree_is_seen(self):
        tmp = temp_dir(self).resolve()
        (tmp / "repo" / ".git").mkdir(parents=True)
        (tmp / "link").symlink_to(tmp / "repo", target_is_directory=True)
        self.assertTrue(rc.inside_git_work_tree(tmp / "link" / "renders"))

    def test_an_out_that_is_a_file_is_a_usage_error(self):
        tmp = temp_dir(self)
        fig = tmp / "fig.mmd"
        fig.write_text(FLOW, encoding="utf-8")
        with redirect_stderr(io.StringIO()) as err:
            self.assertEqual(rc.main([str(fig), "--out", str(fig)]), 3)
            self.assertEqual(rc.main([str(fig), "--out", str(fig / "sub")]), 3)
        self.assertIn("not a directory", err.getvalue())
        self.assertIn("runs through the file", err.getvalue())

    def test_an_out_other_users_may_write_in_is_a_usage_error(self):
        # SEC2-08: another user could plant a symlink under the predictable name of a render
        tmp = temp_dir(self)
        fig = tmp / "fig.mmd"
        fig.write_text(FLOW, encoding="utf-8")
        shared = tmp / "shared"
        shared.mkdir()
        shared.chmod(0o1777)
        self.addCleanup(shared.chmod, 0o700)
        for out in (shared, shared / "renders"):
            with self.subTest(out=str(out)), redirect_stderr(io.StringIO()) as err:
                self.assertEqual(rc.main([str(fig), "--out", str(out)]), 3)
                self.assertIn("%s is writable by every user" % shared, err.getvalue())
        self.assertFalse((shared / "renders").exists())
        self.assertEqual(sorted(p.name for p in shared.iterdir()), [])

    def test_the_install_home_is_resolved(self):
        # SEC2-01: the node processes run in an install directory, so every path is absolute
        tmp = temp_dir(self).resolve()
        (tmp / "real").mkdir()
        (tmp / "link").symlink_to(tmp / "real", target_is_directory=True)
        here = os.getcwd()
        os.chdir(str(tmp))
        self.addCleanup(os.chdir, here)
        set_env(self, MERMAID_RENDER_HOME="link")
        self.assertEqual(rc.render_home(), tmp / "real")
        set_env(self, MERMAID_RENDER_HOME=None)
        self.assertTrue(rc.render_home().is_absolute())


class TestSourceReading(unittest.TestCase):
    def test_negative_marker(self):
        self.assertIsNone(rc.negative_names(FLOW))
        self.assertIsNone(rc.negative_names(""))
        self.assertEqual(rc.negative_names(FLOW + "  %% negative: MA-LR, crossings\n"),
                         ["MA-LR", "crossings"])
        self.assertEqual(rc.negative_names(FLOW + "%%negative:legibility,contrast\n\n  \n"),
                         ["legibility", "contrast"])
        self.assertEqual(rc.negative_names(FLOW + "%% negative:\n"), [])
        # the marker counts only as the last non-blank line
        self.assertIsNone(rc.negative_names("%% negative: crossings\n" + FLOW))

    def test_the_marker_reads_as_the_lint_reads_it(self):
        # R6: one definition of the marker, mermaid_model's
        for last in ("%% negative: MA-LR, crossings", "%%negative:legibility;contrast",
                     "  %% negative : crossings", "%% negative:", "%% negativity: crossings"):
            with self.subTest(marker=last):
                body = FLOW + last + "\n"
                marker = mm.Fence(lang="mermaid", start=1, end=5, body=body).negative
                self.assertEqual(rc.negative_names(body), None if marker is None else marker.names)

    def test_parse_check_names(self):
        for names in (["MA-SYN-01"], ["syn"], ["MA-PARSE"], ["crossings", "parse"], ["Ma-Syn-02"]):
            self.assertTrue(rc.names_parse_check(names), names)
        for names in ([], ["MA-LR"], ["crossings"], ["synonyms"], ["MA-LABEL-05"]):
            self.assertFalse(rc.names_parse_check(names), names)

    def test_fences_carry_lines_and_hashes(self):
        doc = temp_dir(self) / "doc.md"
        doc.write_text("# T\n\n```mermaid\n" + FLOW + "```\n\n- item\n\n   ```mermaid\n   " +
                       "flowchart LR\n     X --> Y\n   ```\n", encoding="utf-8")
        figs = rc._figures_of(doc)
        self.assertEqual([(f["index"], f["line"], f["end"]) for f in figs], [(1, 3, 6), (2, 10, 13)])
        self.assertEqual(figs[0]["sha256"], rc.fence_sha256(FLOW.rstrip("\n").split("\n")))
        # the hash covers the body; the fence's indent is not part of the figure
        self.assertEqual(figs[1]["sha256"], rc.fence_sha256(["flowchart LR", "  X --> Y"]))
        self.assertEqual(figs[1]["sha256"], mm.fence_sha256(figs[1]["body"]))
        self.assertEqual(figs[1]["body"], "flowchart LR\n  X --> Y")

    def test_a_fence_in_a_blockquote_or_an_alert_is_a_figure(self):
        # RG-03: the fences come from mermaid_model.extract_fences, quotes and alerts included
        doc = temp_dir(self) / "alert.md"
        doc.write_text("# T\n\n> [!NOTE]\n> ```mermaid\n> flowchart TB\n>   A --> B\n> ```\n",
                       encoding="utf-8")
        figs = rc._figures_of(doc)
        self.assertEqual([(f["line"], f["end"], f["body"]) for f in figs],
                         [(4, 7, "flowchart TB\n  A --> B")])
        self.assertEqual(figs[0]["sha256"], rc.fence_sha256(["flowchart TB", "  A --> B"]))

    def test_mmd_file_is_one_figure(self):
        fig = temp_dir(self) / "fig.mmd"
        fig.write_bytes(FLOW.replace("\n", "\r\n").encode("utf-8"))
        figs = rc._figures_of(fig)
        self.assertEqual(len(figs), 1)
        self.assertEqual(figs[0]["line"], 0)
        self.assertEqual(figs[0]["sha256"], rc.fence_sha256(["flowchart TB", "  A --> B"]))
        fig.write_text("\n  \n", encoding="utf-8")
        self.assertEqual(rc._figures_of(fig), [])

    def test_mmdc_command_line(self):
        def renderer(cli):
            return rc.Renderer(tag="v", mermaid="x", mmdc=Path("mmdc"), puppeteer_config=Path("p.json"),
                               root=Path("."), cli=cli)
        p = Path("f")
        v12 = rc.mmdc_command(renderer("12.0.0"), p, p, p, "white", None, 900)
        self.assertEqual(v12[v12.index("-t") + 1], "default")
        self.assertIn("--size", v12)
        v12_dark = rc.mmdc_command(renderer("12.0.0"), p, p, p, "#0d1117", "dark", 900)
        self.assertEqual(v12_dark[v12_dark.index("-t") + 1], "dark")
        v11 = rc.mmdc_command(renderer("11.17.0"), p, p, p, "white", None, 1800)
        self.assertNotIn("-t", v11)
        self.assertEqual(v11[v11.index("-w") + 1], "1800")

    def test_negative_render_check_names_are_the_gate_checks(self):
        # the lint (MA-NEG-02) and the render check accept the same render check names
        self.assertEqual(set(mm.RENDER_CHECK_NAMES), set(sg.GATE_CHECKS))
        self.assertFalse(set(sg.WARN_CHECKS) & set(mm.RENDER_CHECK_NAMES))


# ----------------------------------------------------------------------------- stubbed runs


def fake_renderers(skip=()):
    out = {}
    for tag, pin in NOTATION["renderers"]["installs"].items():
        if tag in skip:
            continue
        out[tag] = rc.Renderer(tag=tag, mermaid=pin["mermaid"], mmdc=Path("/nonexistent/mmdc"),
                               puppeteer_config=Path("/nonexistent/puppeteer.json"),
                               root=Path("/nonexistent"), cli=pin["cli"])
    return out


def fake_render(source, renderer, out_base, dark=False, notation=None):
    """A render whose findings the source names: a line `%% FAILS <check>` fails that check,
    `%% PARSE-ERROR-IN-<tag>` makes that version reject the source, and `%% UNMODELLED` gives a
    kind whose geometry svg_geometry does not read."""
    findings = [{"check": line.split()[-1], "severity": "fail", "message": "stub"}
                for line in source.split("\n") if line.strip().startswith("%% FAILS")]
    if "PARSE-ERROR-IN-" + renderer.tag in source:
        return rc.RenderResult(tag=renderer.tag, dark=dark, ok=False, svg=None, png=None,
                               log="Parse error on line 2", status="parse_error")
    metrics = {"diagram": "flowchart-v2", "width": 100.0, "height": 80.0,
               "effective_font_px": 16.0, "geometry": "modelled", "warnings": []}
    if "%% UNMODELLED" in source:
        metrics.update(diagram="quadrantChart", geometry="not modelled",
                       warnings=["diagram kind 'quadrantChart' is not modelled: size, font and "
                                 "the overlap of its measured texts only"])
        findings.append({"check": "geometry", "severity": "warn", "message": "geometry not checked"})
    return rc.RenderResult(tag=renderer.tag, dark=dark, ok=True, svg=None, png=None, log="",
                           metrics=metrics, findings=findings, status="ok",
                           browser="HeadlessChrome/0.0", font_family="Trebuchet MS",
                           fonts=[{"family": "Trebuchet MS", "glyphs": 10}])


class StubbedRun(unittest.TestCase):
    def setUp(self):
        self.dir = temp_dir(self)
        self.saved = (rc.find_renderers, rc.render, mm.NEGATIVE_ROOTS)
        rc.find_renderers = lambda home=None, notation=None: fake_renderers()
        rc.render = fake_render
        # the documents of these tests stand in for the skill's teaching files
        mm.NEGATIVE_ROOTS = mm.NEGATIVE_ROOTS + (self.dir,)
        self.addCleanup(self.restore)

    def restore(self):
        rc.find_renderers, rc.render, mm.NEGATIVE_ROOTS = self.saved

    def doc(self, *bodies, name="doc.md", where=None):
        path = (where or self.dir) / name
        parts = ["# Figures\n"]
        for body in bodies:
            parts.append("```mermaid\n%s```\n" % body)
        path.write_text("\n".join(parts), encoding="utf-8")
        return path

    def run_main(self, *args, out=None):
        out_s, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out_s), redirect_stderr(err):
            code = rc.main([*map(str, args), "--out", str(out or self.dir / "renders")])
        return code, out_s.getvalue(), err.getvalue()


class TestRunOutcomes(StubbedRun):
    def test_all_renders_pass(self):
        code, out, _ = self.run_main(self.doc(FLOW))
        self.assertEqual(code, 0, out)
        self.assertFalse([x for x in out.splitlines() if x.startswith("not rendered")], out)

    def test_no_dark_does_the_other_renders_then_exits_2(self):
        code, out, _ = self.run_main(self.doc(FLOW), "--no-dark")
        self.assertEqual(code, 2, out)
        self.assertIn("not rendered: dark render skipped", out.splitlines())
        self.assertIn("v10       mermaid", out)
        self.assertIn("v11       mermaid", out)

    def test_a_left_out_version_is_not_rendered(self):
        code, out, _ = self.run_main(self.doc(FLOW), "--versions", "v11")
        self.assertEqual(code, 2, out)
        self.assertIn("not rendered: v10 render skipped", out.splitlines())

    def test_a_failure_wins_over_a_skipped_render(self):
        code, out, _ = self.run_main(self.doc(FLOW + "%% FAILS crossings\n"), "--no-dark")
        self.assertEqual(code, 1, out)

    def test_a_parse_error_fails_the_figure(self):
        code, out, _ = self.run_main(self.doc(FLOW + "%% PARSE-ERROR-IN-v10\n"))
        self.assertEqual(code, 1, out)

    def test_a_file_without_a_mermaid_fence_is_not_rendered(self):
        # L6: a check that rendered nothing never reports a pass
        prose = self.dir / "prose.md"
        prose.write_text("# Notes\n\n```{mermaid}\nflowchart TB\n  A --> B\n```\n\n"
                         "```text figure\nA -> B\n```\n", encoding="utf-8")
        code, out, _ = self.run_main(prose)
        self.assertEqual(code, 2, out)
        self.assertIn("not rendered: no mermaid fence found in %s" % prose, out.splitlines())
        self.assertNotIn("PASS", out)
        code, out, _ = self.run_main(prose, "--no-dark")
        self.assertEqual(code, 2, out)
        self.assertIn("not rendered: dark render skipped", out.splitlines())
        code, out, _ = self.run_main(prose, self.doc(FLOW), "--json")
        self.assertEqual(code, 2, out)
        report = json.loads(out)
        self.assertEqual([src["status"] for src in report["inputs"]], ["not rendered", "pass"])
        self.assertEqual(report["summary"]["no_fence"], 1)

    def test_a_forward_failure_is_information_only(self):
        # the check pair and the dark render decide; 12.1.0 is a forward look (TASK D3)
        code, out, _ = self.run_main(self.doc(FLOW + "%% PARSE-ERROR-IN-v12\n"), "--forward")
        self.assertEqual(code, 0, out)
        self.assertIn("information only", out)
        self.assertIn("figure 1 (line 3, flowchart-v2): PASS", out)
        rc.find_renderers = lambda home=None, notation=None: fake_renderers(skip=("v12",))
        code, out, _ = self.run_main(self.doc(FLOW), "--forward")
        self.assertEqual(code, 0, out)
        self.assertTrue([x for x in out.splitlines() if x.startswith("note: ")
                         and "information only" in x], out)
        self.assertFalse([x for x in out.splitlines() if x.startswith("not rendered")], out)

    def test_an_unmodelled_kind_passes_with_geometry_not_checked(self):
        path = self.doc(FLOW + "%% UNMODELLED\n")
        code, out, _ = self.run_main(path)
        self.assertEqual(code, 0, out)
        self.assertIn("PASS, GEOMETRY NOT CHECKED", out)
        self.assertIn("pass, geometry not checked", out)
        self.assertIn("note diagram kind 'quadrantChart' is not modelled", out)
        code, out, _ = self.run_main(path, "--json")
        report = json.loads(out)
        self.assertEqual(report["inputs"][0]["figures"][0]["status"], "pass, geometry not checked")
        self.assertEqual(report["inputs"][0]["status"], "pass, geometry not checked")
        self.assertEqual((report["summary"]["pass"], report["summary"]["unchecked"]), (0, 1))

    def test_expected_failures_of_a_negative_set_no_exit_code(self):
        neg = FLOW + "%% FAILS crossings\n%% negative: MA-PLAN-01, crossings\n"
        code, out, _ = self.run_main(self.doc(FLOW, neg))
        self.assertEqual(code, 0, out)
        self.assertIn("EXPECTED", out)
        self.assertIn("fail, expected", out)

    def test_a_marker_that_names_no_render_check_grades_its_renders(self):
        # STI-01: a marker of lint rules excuses no render failure; the renders count as a
        # positive figure's
        code, out, _ = self.run_main(self.doc(FLOW + "%% FAILS legibility\n%% negative: MA-LR\n"))
        self.assertEqual(code, 1, out)
        self.assertIn("figure 1 (line 3, flowchart-v2): FAIL", out)
        self.assertNotIn("fail, expected", out)
        code, out, _ = self.run_main(self.doc(FLOW + "%% PARSE-ERROR-IN-v10\n%% FAILS contrast\n"
                                                     "%% negative: MA-SYN-01\n"))
        self.assertEqual(code, 1, out)  # the parse error is expected, the contrast failure is not

    def test_a_failure_the_marker_does_not_name_fails_the_figure(self):
        neg = FLOW + "%% FAILS crossings\n%% FAILS legibility\n%% negative: crossings\n"
        code, out, _ = self.run_main(self.doc(neg))
        self.assertEqual(code, 1, out)
        self.assertIn("also fails legibility, which it does not name", out)
        self.assertNotIn("fail, expected", out)
        code, out, _ = self.run_main(self.doc(neg), "--json")
        fig = json.loads(out)["inputs"][0]["figures"][0]
        self.assertEqual((fig["status"], fig["negative_fired"], fig["negative_unexpected"]),
                         ("fail", ["crossings"], ["legibility"]))

    def test_the_marker_scope_is_the_lints(self):
        # R6: render_check reads mermaid_model.NEGATIVE_ROOTS through negative_allowed
        elsewhere = temp_dir(self)
        path = self.doc(FLOW + "%% FAILS crossings\n%% negative: crossings\n", where=elsewhere)
        self.assertEqual(self.run_main(path)[0], 1)
        mm.NEGATIVE_ROOTS = mm.NEGATIVE_ROOTS + (elsewhere,)
        code, out, _ = self.run_main(path)
        self.assertEqual(code, 0, out)
        self.assertIn("EXPECTED", out)

    def test_markers_count_in_the_references_and_nowhere_else(self):
        ref = SCRIPTS.parent / "references" / "renderer-facts.md"
        copy = temp_dir(self) / ref.name
        shutil.copyfile(str(ref), str(copy))
        for path, honoured in ((ref, True), (copy, False)):
            with self.subTest(path=str(path)):
                report = rc.check_path(path, list(NOTATION["renderers"]["check_pair"]), True,
                                       self.dir / "renders", NOTATION, fake_renderers())
                marked = [f for f in report["figures"] if f["negative"] or f["negative_ignored"]]
                self.assertTrue(marked)
                self.assertEqual({f["negative"] for f in marked}, {honoured})

    def test_a_negative_whose_render_checks_all_pass_is_broken(self):
        code, out, _ = self.run_main(self.doc(FLOW + "%% negative: crossings, legibility\n"))
        self.assertEqual(code, 1, out)
        self.assertIn("BROKEN", out)

    def test_a_negative_naming_only_lint_rules_is_expected(self):
        code, out, _ = self.run_main(self.doc(FLOW + "%% negative: MA-LR\n"))
        self.assertEqual(code, 0, out)

    def test_a_parse_error_fails_a_negative_that_names_no_parse_check(self):
        # a figure that does not parse in a pinned version shows no defect a lint name excuses
        code, out, _ = self.run_main(self.doc(FLOW + "%% PARSE-ERROR-IN-v10\n%% negative: MA-LR\n"))
        self.assertEqual(code, 1, out)
        neg = FLOW + "%% FAILS crossings\n%% PARSE-ERROR-IN-v10\n%% negative: crossings\n"
        code, out, _ = self.run_main(self.doc(neg))
        self.assertEqual(code, 1, out)
        for names in ("MA-SYN-01", "syn", "MA-PARSE"):
            with self.subTest(names=names):
                code, out, _ = self.run_main(self.doc(FLOW + "%% PARSE-ERROR-IN-v10\n"
                                                      "%% negative: " + names + "\n"))
                self.assertEqual(code, 0, out)

    def test_a_negative_marker_outside_the_skill_is_ignored(self):
        # one comment line in a project document must not excuse a failing figure
        elsewhere = temp_dir(self)
        path = self.doc(FLOW + "%% FAILS crossings\n%% negative: crossings\n", where=elsewhere)
        code, out, _ = self.run_main(path)
        self.assertEqual(code, 1, out)
        self.assertIn("negative marker ignored", out)
        code, out, _ = self.run_main(path, "--json")
        fig = json.loads(out)["inputs"][0]["figures"][0]
        self.assertEqual((fig["negative"], fig["negative_ignored"], fig["status"]),
                         (False, ["crossings"], "fail"))

    def test_a_warn_check_in_a_marker_is_not_a_render_check(self):
        code, out, _ = self.run_main(self.doc(FLOW + "%% negative: lifeline_gap\n"), "--json")
        fig = json.loads(out)["inputs"][0]["figures"][0]
        self.assertEqual(fig["negative_render_checks"], [])

    def test_evidence_per_figure(self):
        path = self.doc(FLOW, FLOW + "%% FAILS contrast\n%% negative: contrast\n")
        code, out, _ = self.run_main(path, "--json")
        self.assertEqual(code, 0, out)
        report = json.loads(out)
        figs = report["inputs"][0]["figures"]
        lines = path.read_text(encoding="utf-8").split("\n")
        for fig in figs:
            body = lines[fig["fence_line"]:fig["fence_end"] - 1]
            self.assertEqual(fig["sha256"], rc.fence_sha256(body))
            self.assertEqual(set(fig["renderers"]), {"v11", "v11-dark", "v10"})
            self.assertEqual(fig["renderers"]["v11"]["mermaid"],
                             NOTATION["renderers"]["installs"]["v11"]["mermaid"])
            self.assertEqual(fig["browsers"], ["HeadlessChrome/0.0"])
            self.assertEqual(fig["fonts"], ["Trebuchet MS"])
        self.assertEqual((figs[1]["negative"], figs[1]["negative_names"], figs[1]["status"],
                          figs[1]["negative_fired"]), (True, ["contrast"], "expected", ["contrast"]))
        self.assertTrue((self.dir / "renders" / "evidence.json").is_file())
        self.assertEqual(report["instruments"], rc.instrument_sha256())

    def test_an_unwritable_render_directory_is_not_rendered(self):
        if not CAN_CHMOD:
            self.skipTest("a read-only directory does not stop root")
        ro = self.dir / "ro"
        ro.mkdir()
        read_only(self, ro)
        code, out, err = self.run_main(self.doc(FLOW), "--json", out=ro)
        self.assertEqual(code, 2, out + err)
        self.assertIn("not rendered: cannot write renders to %s" % ro, err)
        self.assertEqual(json.loads(out)["exit"], 2)

    def test_old_render_directories_are_pruned(self):
        home = self.dir / "home"
        base = home / "renders"
        base.mkdir(parents=True)
        for k in range(rc.RENDER_KEEP + 5):
            d = base / ("check-%02d" % k)
            d.mkdir()
            os.utime(d, (1000000 + k, 1000000 + k))
        (base / "corpus").mkdir()
        set_env(self, MERMAID_RENDER_HOME=str(home))
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(rc.main([str(self.doc(FLOW))]), 0)
        left = sorted(d.name for d in base.iterdir() if d.name.startswith("check-"))
        self.assertEqual(len(left), rc.RENDER_KEEP)
        self.assertNotIn("check-00", left)
        self.assertTrue((base / "corpus").is_dir())

    def test_a_render_directory_other_users_may_write_in_is_a_usage_error(self):
        # SEC2-08: the default renders directory must be private too; a new one is made 0700
        home = self.dir.resolve() / "home"
        set_env(self, MERMAID_RENDER_HOME=str(home))
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(rc.main([str(self.doc(FLOW))]), 0)
        base = home / "renders"
        self.assertEqual(stat.S_IMODE(base.stat().st_mode), 0o700)
        base.chmod(0o777)
        self.addCleanup(base.chmod, 0o700)
        before = sorted(p.name for p in base.iterdir())
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err:
            self.assertEqual(rc.main([str(self.doc(FLOW))]), 3)
        self.assertIn("%s is writable by every user" % base, err.getvalue())
        self.assertEqual(sorted(p.name for p in base.iterdir()), before)


class TestFixture(StubbedRun):
    def test_fixture_is_written_and_merged(self):
        fixture = self.dir / "fixture.json"
        fixture.write_text(json.dumps({"schema": rc.FIXTURE_SCHEMA, "files": {"other.md": {
            "generated": "x", "figures": {}}}}), encoding="utf-8")
        path = self.doc(FLOW)
        code, out, _ = self.run_main(path, "--fixture", fixture)
        self.assertEqual(code, 0, out)
        data = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], rc.FIXTURE_SCHEMA)
        key = rc._fixture_key(path)
        self.assertEqual(sorted(data["files"]), sorted(["other.md", key]))
        entry = data["files"][key]["figures"]["3"]
        self.assertEqual(sorted(entry["renders"]), ["v10", "v11", "v11-dark"])
        self.assertEqual(entry["sha256"], rc.fence_sha256(FLOW.rstrip("\n").split("\n")))
        self.assertFalse(entry["negative"])
        # the evidence names the instruments and the notation values it was measured with
        self.assertEqual(data["files"][key]["instruments"], rc.instrument_sha256())
        self.assertEqual(data["files"][key]["settings"], rc.render_settings(NOTATION))
        self.assertEqual([p.name for p in self.dir.iterdir() if p.name.endswith(".tmp")], [])

    def test_the_settings_bind_the_legibility_exemptions(self):
        # another exemption list changes the smallest text the evidence stores: it reads stale
        n = json.loads(json.dumps(NOTATION))
        n["thresholds"]["legibility_exempt_classes"] = []
        self.assertNotEqual(rc.render_settings(n), rc.render_settings(NOTATION))
        del n["thresholds"]
        self.assertIsNone(rc.render_settings(n)["legibility_exempt_classes"])

    def test_fixture_is_not_written_with_a_skipped_render(self):
        fixture = self.dir / "fixture.json"
        code, out, _ = self.run_main(self.doc(FLOW), "--no-dark", "--fixture", fixture)
        self.assertEqual(code, 2, out)
        self.assertFalse(fixture.exists())
        self.assertIn("not written", out)

    def test_a_foreign_json_file_is_never_replaced(self):
        # an existing file must already be render evidence; anything else stays as it was
        targets = {
            "settings.json": json.dumps({"permissions": {"allow": ["Bash(git status)"]}}),
            "plan.json": json.dumps({"schema": "plan-gantt-geometry/v1", "renders": []}),
            "array.json": "[1, 2]",
            "conflict.json": '<<<<<<< HEAD\n{"schema": "%s"}\n=======\n' % rc.FIXTURE_SCHEMA,
            # SEC2-06: a fixture whose files member is no object of objects is named before
            # the renders, not after them with a traceback and exit 1
            "files-list.json": json.dumps({"schema": rc.FIXTURE_SCHEMA, "files": [["a"]]}),
            "files-text.json": json.dumps({"schema": rc.FIXTURE_SCHEMA, "files": "x"}),
            "files-number.json": json.dumps({"schema": rc.FIXTURE_SCHEMA, "files": 5}),
            "entry-number.json": json.dumps({"schema": rc.FIXTURE_SCHEMA, "files": {"a.md": 5}}),
        }
        path = self.doc(FLOW)
        for name, text in targets.items():
            with self.subTest(target=name):
                target = self.dir / name
                target.write_text(text, encoding="utf-8")
                code, out, err = self.run_main(path, "--fixture", target)
                self.assertEqual(code, 3, out + err)
                self.assertIn("fix or delete it", err)
                self.assertEqual(target.read_text(encoding="utf-8"), text)

    def test_a_fixture_damaged_during_the_renders_is_not_written(self):
        # SEC2-06: the target is read again after the renders; a damaged one is a fixture that
        # cannot be written (exit 2), never a failing figure (exit 1)
        fixture = self.dir / "fixture.json"
        fixture.write_text(json.dumps({"schema": rc.FIXTURE_SCHEMA, "files": {}}), encoding="utf-8")
        damaged = json.dumps({"schema": rc.FIXTURE_SCHEMA, "files": [["a"]]})

        def damaging_render(*args, **kwargs):
            fixture.write_text(damaged, encoding="utf-8")
            return fake_render(*args, **kwargs)

        rc.render = damaging_render
        code, out, _ = self.run_main(self.doc(FLOW), "--fixture", fixture)
        self.assertEqual(code, 2, out)
        self.assertIn("not written: its files member is not an object of file entries", out)
        self.assertEqual(fixture.read_text(encoding="utf-8"), damaged)

    def test_a_file_without_a_fence_gets_an_empty_entry(self):
        fixture = self.dir / "fixture.json"
        prose = self.dir / "prose.md"
        prose.write_text("# Notes\n\nNo figure here.\n", encoding="utf-8")
        code, out, _ = self.run_main(prose, self.doc(FLOW), "--fixture", fixture)
        self.assertEqual(code, 2, out)
        data = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertEqual(data["files"][rc._fixture_key(prose)]["figures"], {})
        self.assertIn(rc._fixture_key(self.dir / "doc.md"), data["files"])


# ----------------------------------------------------------------------------- renderer config


def write_config(test, folder, **over):
    """An install as setup_renderers.sh leaves it, in `<folder>/home/v11`: private directories,
    the empty PUPPETEER_RC, and a puppeteer.json whose keys the keyword arguments replace (the
    value None removes one)."""
    cfg = {"executablePath": sys.executable, "headless": "shell",
           "args": list(rc.BROWSER_ARGS), "pipe": True}
    for key, value in over.items():
        if value is None:
            cfg.pop(key, None)
        else:
            cfg[key] = value
    root = folder / "home" / "v11"
    for d in (root.parent, root):
        d.mkdir(exist_ok=True)
        d.chmod(0o700)  # whatever the umask
    (root / rc.PUPPETEER_RC).write_text("{}\n", encoding="utf-8")
    path = root / "puppeteer.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return rc.Renderer(tag="v11", mermaid="11.17.2", mmdc=root / "mmdc", puppeteer_config=path,
                       root=root, cli="11.17.0")


class TestConfigProblem(unittest.TestCase):
    """R7.9: only the config setup_renderers.sh writes is run."""

    def setUp(self):
        self.dir = temp_dir(self)
        set_env(self, MERMAID_RENDER_NO_SANDBOX=None)

    def problem(self, **over):
        return rc.config_problem(write_config(self, self.dir, **over))

    def test_the_written_config_is_accepted(self):
        self.assertIsNone(self.problem())

    def test_every_other_config_is_refused(self):
        base = list(rc.BROWSER_ARGS)
        refused = {
            "old network block": {"args": ["--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE localhost"]},
            "no network block": {"args": []},
            "rules undone": {"args": ["--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE *",
                                      "--no-proxy-server"]},
            "second rule": {"args": base + ["--host-resolver-rules=MAP nothing.invalid 127.0.0.1"]},
            "proxy": {"args": base + ["--proxy-server=http://localhost:3128"]},
            "no proxy switch": {"args": base[:1]},
            "sandbox off with a value": {"args": base + ["--no-sandbox=1"]},
            "setuid sandbox off": {"args": base + ["--disable-setuid-sandbox"]},
            "zygote off": {"args": base + ["--single-process", "--no-zygote"]},
            "devtools port": {"args": base + ["--remote-debugging-address=0.0.0.0",
                                              "--remote-debugging-port=9222"]},
            "web security off": {"args": base + ["--disable-web-security"]},
            "no pipe": {"pipe": None},
            "pipe off": {"pipe": False},
            "extra key": {"ignoreDefaultArgs": True},
            "headful": {"headless": False},
            "no browser": {"executablePath": None},
            "missing browser": {"executablePath": str(self.dir / "no-such-browser")},
        }
        for name, over in refused.items():
            with self.subTest(config=name):
                self.assertIsNotNone(self.problem(**over))

    def test_no_sandbox_needs_the_operator_switch(self):
        args = list(rc.BROWSER_ARGS) + [rc.NO_SANDBOX_ARG]
        self.assertIn("MERMAID_RENDER_NO_SANDBOX", self.problem(args=args))
        set_env(self, MERMAID_RENDER_NO_SANDBOX="1")
        self.assertIsNone(self.problem(args=args))
        self.assertIsNone(self.problem())
        self.assertIsNotNone(self.problem(args=args + ["--no-sandbox=1"]))

    def test_a_config_that_does_not_parse_is_refused(self):
        renderer = write_config(self, self.dir)
        renderer.puppeteer_config.write_text("{", encoding="utf-8")
        self.assertIn("does not parse", rc.config_problem(renderer))

    def test_a_relative_browser_path_is_refused(self):
        # node runs in the install directory and would read the path from there, not from here
        rel = os.path.relpath(sys.executable)
        self.assertTrue(Path(rel).is_file())
        self.assertIn("relative path", self.problem(executablePath=rel))


class TestPrivateDirectories(unittest.TestCase):
    """SEC2-08: renders and installs live only where no other user may plant a file."""

    def setUp(self):
        if not hasattr(os, "geteuid"):
            self.skipTest("no POSIX owners here")
        self.dir = temp_dir(self)
        self.d = self.dir / "d"
        self.d.mkdir()
        self.addCleanup(self.d.chmod, 0o700)

    def problem(self, mode, own_group=False, path=None):
        self.d.chmod(mode)
        with mock.patch.object(rc, "_own_group", lambda gid: own_group):
            return rc.private_dir_problem(path or self.d)

    def test_modes(self):
        every, group = "writable by every user", "writable by its group"
        cases = {(0o700, False): None, (0o755, False): None, (0o750, False): None,
                 (0o777, False): every, (0o1777, False): every, (0o757, True): every,
                 (0o770, False): group, (0o770, True): None}
        for (mode, own_group), words in cases.items():
            with self.subTest(mode=oct(mode), own_group=own_group):
                problem = self.problem(mode, own_group)
                if words is None:
                    self.assertIsNone(problem)
                else:
                    self.assertEqual(problem, "%s is %s" % (self.d, words))

    def test_a_missing_path_is_judged_by_its_nearest_existing_ancestor(self):
        # another user could make the missing directories before this user does
        self.assertIn("%s is writable by every user" % self.d,
                      self.problem(0o777, path=self.d / "missing" / "renders"))
        self.assertIsNone(self.problem(0o700, path=self.d / "missing" / "renders"))

    def test_a_symlink_is_judged_by_what_it_reaches(self):
        link = self.dir / "link"
        link.symlink_to(self.d, target_is_directory=True)
        self.assertIn("writable by every user", self.problem(0o777, path=link))
        self.assertIsNone(self.problem(0o700, path=link))

    def test_a_directory_of_another_user_is_refused(self):
        if os.geteuid() == 0:
            self.skipTest("root owns the directory, and a root-owned directory is accepted")
        with mock.patch.object(rc.os, "geteuid", lambda: os.getuid() + 4242):
            self.assertIn("belongs to another user", rc.private_dir_problem(self.d))

    def test_the_own_group_is_the_users_private_group(self):
        import grp
        import pwd
        user = pwd.getpwuid(os.geteuid())
        private = grp.getgrgid(user.pw_gid).gr_name == user.pw_name
        self.assertEqual(rc._own_group(user.pw_gid), private)
        others = [g.gr_gid for g in grp.getgrall() if g.gr_gid != user.pw_gid]
        if others:
            self.assertFalse(rc._own_group(others[0]))


class TestFindRenderers(unittest.TestCase):
    def install(self, home, tag, mermaid, cli):
        root = home / tag
        (root / "node_modules" / ".bin").mkdir(parents=True)
        (root / "node_modules" / ".bin" / "mmdc").write_text("", encoding="utf-8")
        for package, version in (("mermaid", mermaid), ("@mermaid-js/mermaid-cli", cli)):
            folder = root / "node_modules" / package
            folder.mkdir(parents=True)
            (folder / "package.json").write_text(json.dumps({"version": version}), encoding="utf-8")
        (root / "puppeteer.json").write_text(json.dumps({"executablePath": "/x"}), encoding="utf-8")

    def test_pins_decide(self):
        home = temp_dir(self)
        installs = NOTATION["renderers"]["installs"]
        v10, v11, v12 = (installs[t] for t in ("v10", "v11", "v12"))
        self.install(home, "v11", v11["mermaid"], v11["cli"])
        self.install(home, "v10", "10.9.1", v10["cli"])  # mermaid drifted
        self.install(home, "v12", v12["mermaid"], "11.0.0")  # mermaid-cli drifted
        found = rc.find_renderers(home, NOTATION)
        self.assertEqual(sorted(t for t in found if not t.startswith("_")), ["v11"])
        self.assertEqual(found["v11"].cli, v11["cli"])
        self.assertEqual(sorted(found["_mismatch"]), ["v10", "v12"])
        self.assertIn("installed under", rc.missing_reason("v10", found, NOTATION, home))

    def test_a_relative_home_gives_absolute_paths(self):
        # SEC2-01: the node processes run in the install directory, not in this one
        home = temp_dir(self).resolve() / "home"
        v11 = NOTATION["renderers"]["installs"]["v11"]
        self.install(home, "v11", v11["mermaid"], v11["cli"])
        here = os.getcwd()
        os.chdir(str(home.parent))
        self.addCleanup(os.chdir, here)
        renderer = rc.find_renderers(Path("home"), NOTATION)["v11"]
        self.assertEqual((renderer.root, renderer.mmdc, renderer.puppeteer_config),
                         (home / "v11", home / "v11" / "node_modules" / ".bin" / "mmdc",
                          home / "v11" / "puppeteer.json"))


class TestFailureClasses(unittest.TestCase):
    def test_logs(self):
        cases = {
            "Error: Parse error on line 2:\n...A --> end\n": "parse_error",
            "UnknownDiagramError: No diagram type detected matching given configuration": "parse_error",
            ("TypeError: Cannot read properties of undefined (reading 'filter')\n    at draw "
             "(file:///x/node_modules/mermaid/dist/mermaid.js:1:2)"): "render_error",
            "Error: Failed to launch the browser process!\nspawn /x/chrome ENOENT": "not_rendered",
            ("TimeoutError: Navigation timeout of 30000 ms exceeded\n    at "
             "file:///x/node_modules/mermaid/dist/mermaid.js:1:2"): "not_rendered",
            "": "not_rendered",
        }
        for log, status in cases.items():
            with self.subTest(log=log[:30]):
                self.assertEqual(rc._classify_failure(log), status)

    def test_root_attributes(self):
        self.assertEqual(rc._root_attributes('<svg id="x" aria-roledescription="error" '
                                             'viewBox="0 0 2412 512"><g/></svg>'), ("error", 2412.0))
        self.assertEqual(rc._root_attributes("<svg><g/></svg>"), ("", 0.0))


# ----------------------------------------------------------------------------- render with stand-ins


FAKE_PROGRAM = '''#!{python}
import json, os, pathlib, sys, time
spec = json.loads(pathlib.Path({spec!r}).read_text())
args = sys.argv[1:]
if spec.get("cwd_log"):
    with open(spec["cwd_log"], "a") as fh:
        fh.write(os.getcwd() + "\\n")
time.sleep(spec.get("sleep", 0))
for flag, key in (("-o", "svg"), ("--png", "png")):
    if spec.get(key) is not None and flag in args:
        pathlib.Path(args[args.index(flag) + 1]).write_text(spec[key])
sys.stdout.write(spec.get("stdout", ""))
sys.stderr.write(spec.get("log", ""))
sys.exit(spec.get("exit", 0))
'''

MEASURE = {"labels": [], "titles": [], "font_px": 16, "kind": "flowchart-v2",
           "browser": "HeadlessChrome/0.0", "page": "#ffffff", "fonts": [], "font_family": None}


class TestRenderWithStandIns(unittest.TestCase):
    """`render` with stand-in `mmdc` and `node` programs: each way a render ends."""

    def setUp(self):
        self.dir = temp_dir(self)
        self.bin = self.dir / "bin"
        self.bin.mkdir()
        self.mmdc = self.program("mmdc", {"svg": TREE_SVG})
        self.program("node", {"stdout": json.dumps(MEASURE), "png": "png"}, folder=self.bin)
        self.renderer = write_config(self, self.dir)
        self.renderer.mmdc = self.mmdc
        set_env(self, PATH=str(self.bin) + os.pathsep + os.environ.get("PATH", ""),
                MERMAID_RENDER_NO_SANDBOX=None)

    def program(self, name, spec, folder=None):
        folder = folder or self.dir
        spec_path = folder / (name + ".spec.json")
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        path = folder / name
        path.write_text(FAKE_PROGRAM.format(python=sys.executable, spec=str(spec_path)),
                        encoding="utf-8")
        path.chmod(0o755)
        return path

    def render(self, source=FLOW, out=None):
        return rc.render(source, self.renderer, (out or self.dir / "out") / "fig", False, NOTATION)

    def test_a_clean_render_is_measured(self):
        res = self.render()
        self.assertEqual((res.status, res.ok), ("ok", True), res.log)
        self.assertEqual(res.metrics["diagram"], "flowchart-v2")
        self.assertTrue(res.measure.is_file())
        self.assertEqual(res.browser, "HeadlessChrome/0.0")

    def test_every_node_process_runs_in_the_install_directory(self):
        # SEC2-01: puppeteer runs a configuration file of its working directory or a parent,
        # so mmdc and measure_text.mjs never run in the caller's directory; the render
        # directory, given here as a relative path, reaches them as an absolute one
        log = self.dir / "cwd.log"
        self.program("mmdc", {"svg": TREE_SVG, "cwd_log": str(log)})
        self.program("node", {"stdout": json.dumps(MEASURE), "png": "png", "cwd_log": str(log)},
                     folder=self.bin)
        caller = self.dir / "caller"
        caller.mkdir()
        here = os.getcwd()
        os.chdir(str(caller))
        self.addCleanup(os.chdir, here)
        res = rc.render(FLOW, self.renderer, Path("renders") / "fig", False, NOTATION)
        self.assertEqual(res.status, "ok", res.log)
        root = os.path.realpath(str(self.renderer.root))
        ran_in = log.read_text(encoding="utf-8").splitlines()
        self.assertEqual([os.path.realpath(p) for p in ran_in], [root, root])
        self.assertTrue((caller / "renders" / "fig.svg").is_file())
        self.assertTrue(res.png.is_absolute())
        self.assertEqual(os.path.realpath(str(res.png)),
                         os.path.realpath(str(caller / "renders" / "fig.png")))

    def test_an_install_other_users_may_change_is_not_run(self):
        # SEC2-08: the stand-in mmdc of an open install home or install directory never runs
        log = self.dir / "ran.log"
        self.program("mmdc", {"svg": TREE_SVG, "cwd_log": str(log)})
        for d in (self.renderer.root.parent, self.renderer.root):
            with self.subTest(open=d.name):
                d.chmod(0o777)
                try:
                    res = self.render()
                finally:
                    d.chmod(0o700)
                self.assertEqual(res.status, "not_rendered")
                self.assertIn("%s is writable by every user" % d, res.log)
                self.assertFalse(log.exists())
        self.assertEqual(self.render().status, "ok")

    def test_an_install_without_the_empty_puppeteer_configuration_is_not_run(self):
        # SEC2-01: without it puppeteer's search for a configuration leaves the install
        log = self.dir / "ran.log"
        self.program("mmdc", {"svg": TREE_SVG, "cwd_log": str(log)})
        stop = self.renderer.root / rc.PUPPETEER_RC
        for text in (None, "", "[]", "{", '{"defaultBrowser": "firefox"}'):
            with self.subTest(text=text):
                if text is None:
                    stop.unlink()
                else:
                    stop.write_text(text, encoding="utf-8")
                res = self.render()
                self.assertEqual(res.status, "not_rendered")
                self.assertIn("%s is not the empty puppeteer configuration" % stop, res.log)
                self.assertFalse(log.exists())
        stop.write_text("{}\n", encoding="utf-8")
        self.assertEqual(self.render().status, "ok")

    def test_failures_are_classified(self):
        cases = {
            "parse_error": {"exit": 1, "log": "Error: Parse error on line 2:\n"},
            "render_error": {"exit": 1, "log": "TypeError: x\n    at f (/y/node_modules/mermaid/dist/m.js:1:1)"},
            "not_rendered": {"exit": 1, "log": "Error: Failed to launch the browser process!"},
        }
        for status, spec in cases.items():
            with self.subTest(status=status):
                self.program("mmdc", spec)
                self.assertEqual(self.render().status, status)

    def test_the_syntax_error_figure_is_a_parse_error(self):
        self.program("mmdc", {"svg": '<svg xmlns="http://www.w3.org/2000/svg" '
                                     'aria-roledescription="error" viewBox="0 0 2412 512"></svg>'})
        res = self.render()
        self.assertEqual(res.status, "parse_error")
        self.assertFalse(res.metrics)

    def test_a_render_that_hangs_is_not_rendered(self):
        self.program("mmdc", {"sleep": 30, "svg": TREE_SVG})
        saved = rc.RENDER_TIMEOUT_S, rc.TERM_GRACE_S
        rc.RENDER_TIMEOUT_S, rc.TERM_GRACE_S = 1, 1
        self.addCleanup(lambda: setattr(rc, "RENDER_TIMEOUT_S", saved[0]))
        self.addCleanup(lambda: setattr(rc, "TERM_GRACE_S", saved[1]))
        started = time.monotonic()
        res = self.render()
        self.assertEqual(res.status, "not_rendered")
        self.assertIn("timed out", res.log)
        self.assertLess(time.monotonic() - started, 20)

    def test_a_failed_measurement_is_not_rendered(self):
        cases = {"text measurement failed": {"exit": 2, "log": "measure_text.mjs: no browser"},
                 "printed no JSON": {"stdout": "not json"}}
        for words, spec in cases.items():
            with self.subTest(case=words):
                self.program("node", spec, folder=self.bin)
                res = self.render()
                self.assertEqual(res.status, "not_rendered")
                self.assertIn(words, res.log)

    def test_a_notation_without_legibility_exemptions_is_not_rendered(self):
        # the exempt classes are notation values; without them the text cannot be measured
        n = json.loads(json.dumps(NOTATION))
        del n["thresholds"]["legibility_exempt_classes"]
        res = rc.render(FLOW, self.renderer, self.dir / "out" / "fig", False, n)
        self.assertEqual(res.status, "not_rendered")
        self.assertIn("legibility_exempt_classes", res.log)

    def test_an_svg_that_cannot_be_analysed_is_not_rendered(self):
        self.program("mmdc", {"svg": '<svg xmlns="http://www.w3.org/2000/svg" '
                                     'aria-roledescription="flowchart-v2"><g></svg>'})
        res = self.render()
        self.assertEqual(res.status, "not_rendered")
        self.assertIn("could not be analysed", res.log)

    def test_no_node_and_a_bad_config_are_not_rendered(self):
        set_env(self, PATH=str(self.dir / "empty-path"))
        self.assertIn("node is not on PATH", self.render().log)
        set_env(self, PATH=str(self.bin) + os.pathsep + os.environ.get("PATH", ""))
        write_config(self, self.dir, pipe=None)
        res = self.render()
        self.assertEqual(res.status, "not_rendered")
        self.assertIn("pipe", res.log)

    def test_an_unwritable_directory_is_not_rendered(self):
        if not CAN_CHMOD:
            self.skipTest("a read-only directory does not stop root")
        ro = self.dir / "ro"
        ro.mkdir()
        read_only(self, ro)
        res = self.render(out=ro)
        self.assertEqual(res.status, "not_rendered")
        self.assertIn("cannot write renders", res.log)


class TestTimeoutStopsTheGroupGently(unittest.TestCase):
    def test_sigterm_comes_before_sigkill(self):
        # puppeteer closes its browser on SIGTERM; a SIGKILL alone gives it no chance
        tmp = temp_dir(self)
        marker = tmp / "got-term"
        script = tmp / "slow.py"
        script.write_text("import signal, sys, time\n"
                          "def term(*_):\n"
                          "    open(%r, 'w').write('term')\n"
                          "    sys.exit(0)\n"
                          "signal.signal(signal.SIGTERM, term)\n"
                          "time.sleep(30)\n" % str(marker), encoding="utf-8")
        saved = rc.TERM_GRACE_S
        rc.TERM_GRACE_S = 5
        self.addCleanup(lambda: setattr(rc, "TERM_GRACE_S", saved))
        code, _, err = rc._run([sys.executable, str(script)], 1, tmp)
        self.assertIsNone(code)
        self.assertIn("timed out", err)
        self.assertTrue(marker.is_file())


class TestPruneRenders(unittest.TestCase):
    def test_keeps_the_newest_and_touches_nothing_else(self):
        base = temp_dir(self)
        for k in range(8):
            d = base / ("check-%d" % k)
            d.mkdir()
            (d / "fig.svg").write_text("<svg/>", encoding="utf-8")
            os.utime(d, (1000 + k, 1000 + k))
        (base / "corpus").mkdir()
        (base / "check-file").write_text("x", encoding="utf-8")
        target = temp_dir(self)
        (base / "check-link").symlink_to(target, target_is_directory=True)
        removed = rc.prune_renders(base, 3)
        self.assertEqual(sorted(d.name for d in removed), ["check-%d" % k for k in range(5)])
        left = sorted(p.name for p in base.iterdir())
        self.assertEqual(left, ["check-5", "check-6", "check-7", "check-file", "check-link", "corpus"])
        self.assertTrue(target.is_dir())


# ----------------------------------------------------------------------------- installed renderers


def installed(tag):
    """The pinned renderer of *tag* when it can run here, else None and the reason it cannot."""
    if shutil.which("node") is None:
        return None, "node is not on PATH"
    renderer = rc.find_renderers(rc.render_home(), NOTATION).get(tag)
    if renderer is None:
        return None, "mermaid %s is not installed under %s" % (
            NOTATION["renderers"]["installs"][tag]["mermaid"], rc.render_home())
    problem = rc.install_problem(renderer) or rc.config_problem(renderer)
    return (None, problem) if problem else (renderer, None)


def installed_v11():
    """The pinned 11.17.2 renderer when it can run here, else the reason it cannot."""
    return installed("v11")


class TestWithInstalledRenderers(unittest.TestCase):
    """measure_text.mjs runs in a browser, so its measurements are checked on real renders."""

    def setUp(self):
        self.renderer, reason = installed_v11()
        if self.renderer is None:
            print("installed-renderer tests skipped: %s" % reason, file=sys.stderr)
            self.skipTest(reason)

    def render(self, source):
        res = rc.render(source, self.renderer, temp_dir(self) / "fig", False, NOTATION)
        self.assertEqual(res.status, "ok", res.log)
        return res

    def test_a_name_taller_than_its_actor_box_is_clipped(self):
        res = self.render("sequenceDiagram\n"
                          "    participant B as Billing<br/>service<br/>primary<br/>region<br/>"
                          "west<br/>zone<br/>blue\n"
                          "    participant C as Client\n"
                          "    C->>B: pay\n")
        self.assertTrue(res.metrics["clipped_labels"], res.metrics)
        self.assertIn("clipped_labels", [f["check"] for f in res.findings if f["severity"] == "fail"])

    def test_a_label_past_its_milestone_diamond_is_clipped(self):
        # TASK 108 calibration item-04: CSS draws a milestone rect rotated 45 degrees and scaled
        # 0.8; the axis-aligned box of its corners holds the label, the diamond does not
        res = self.render('%%{init: {"gantt": {"barHeight": 16, "fontSize": 12}}}%%\n'
                          "gantt\n    dateFormat YYYY-MM-DD\n    axisFormat %d %b\n"
                          "    section Release\n    R1 :r1, 2026-11-02, 3d\n"
                          "    R2 :milestone, r2, after r1, 0d\n")
        measure = json.loads(res.measure.read_text(encoding="utf-8"))
        tasks = {lab["text"]: lab for lab in measure["labels"] if lab["kind"] == "task"}
        self.assertIn("milestoneText", tasks["R2"]["cls"])
        self.assertGreater(tasks["R2"]["clipped_px"], sg.CLIP_TOL_PX)
        self.assertEqual(tasks["R1"]["clipped_px"], 0)
        self.assertEqual([(c["label"], c["where"]) for c in res.metrics["clipped_labels"]],
                         [("R2", "its box")])
        self.assertIn("clipped_labels", [f["check"] for f in res.findings if f["severity"] == "fail"])

    def test_one_small_label_fails_legibility(self):
        # RG-02, R3: four 16 px labels set the most common size, so only the smallest text
        # catches the 6 px one
        res = self.render('flowchart TB\n    A["Alpha"] --> B["Beta"] --> C["Gamma"] --> D["Delta"]\n'
                          '    D --> E["Terms and conditions apply"]\n'
                          "    classDef tiny font-size:6px\n    class E tiny\n")
        self.assertEqual((res.metrics["font_px"], res.metrics["smallest_font_px"]), (16.0, 6.0))
        fails = [f for f in res.findings if f["severity"] == "fail" and f["check"] == "legibility"]
        self.assertEqual(len(fails), 1, res.findings)
        self.assertIn("Terms and conditions apply", fails[0]["message"])

    def test_the_lines_of_a_participant_name_are_one_label(self):
        # R1: mermaid draws the lines of a name 16 px apart in 19 px boxes; they overlap by 3 px
        res = self.render(NOTATION["settings"]["sequence"] + "\nsequenceDiagram\n"
                          "    participant A as Access control server\n"
                          "    participant O as Orders<br/>API\n"
                          "    A->>O: check the order\n")
        measure = json.loads(res.measure.read_text(encoding="utf-8"))
        lines = {lab["text"]: lab["bbox"] for lab in measure["labels"] if lab["kind"] == "actor"}
        top, under = lines["Access control"], lines["server"]
        self.assertGreater(top[1] + top[3] - under[1], 2.0, "the lines no longer overlap")
        self.assertEqual(res.metrics["label_overlaps"], [])
        self.assertTrue(sg.passes(res.findings), res.findings)

    def test_text_past_the_figure_edge_is_measured(self):
        # R4: measure_text.mjs measures how far painted text runs past the viewBox (outside_px)
        res = self.render("quadrantChart\n    x-axis Low --> High\n    y-axis Low --> High\n"
                          "    Campaign with a long descriptive name: [0.99, 0.5]\n")
        measure = json.loads(res.measure.read_text(encoding="utf-8"))
        label = next(lab for lab in measure["labels"] if lab["text"].startswith("Campaign"))
        self.assertIsNone(label["box"])
        self.assertGreater(label["outside_px"], sg.CLIP_TOL_PX)
        clipped = [c for c in res.metrics["clipped_labels"] if c["label"].startswith("Campaign")]
        self.assertEqual([c["where"] for c in clipped], ["the figure's edge"])
        self.assertIn("clipped_labels", [f["check"] for f in res.findings if f["severity"] == "fail"])

    def test_a_puppeteer_configuration_of_the_callers_directory_never_runs(self):
        # SEC2-01: puppeteer runs a .puppeteerrc.cjs it finds in its working directory or a
        # parent. Each render runs in the install directory, whose empty .puppeteerrc.json ends
        # that search, so a file a checked-out project holds is neither run nor read
        renderers = [self.renderer] + [r for r in (installed("v10")[0],) if r is not None]
        top = temp_dir(self)
        caller = top / "project"
        caller.mkdir()
        ran = top / "ran.log"
        planted = ("require('fs').appendFileSync(%s, process.argv.join(' ') + '\\n');\n"
                   "module.exports = {};\n" % json.dumps(str(ran)))
        here = os.getcwd()
        os.chdir(str(caller))
        self.addCleanup(os.chdir, here)
        cases = {"in the caller's directory": (caller / ".puppeteerrc.cjs", planted),
                 "in a parent of it": (top / ".config" / "puppeteerrc.cjs", planted),
                 "a data-only one": (caller / ".puppeteerrc.json",
                                     '{"defaultBrowser": "firefox", "defaultProduct": "firefox"}')}
        for where, (path, text) in cases.items():
            path.parent.mkdir(exist_ok=True)
            path.write_text(text, encoding="utf-8")
            for renderer in renderers:
                with self.subTest(config=where, tag=renderer.tag):
                    res = rc.render(FLOW, renderer, top / "renders" / renderer.tag, False, NOTATION)
                    self.assertEqual(res.status, "ok", res.log)
                    self.assertFalse(ran.exists(), ran.read_text(encoding="utf-8")
                                     if ran.exists() else "")
            path.unlink()

    def test_measure_text_run_by_hand_works_in_the_install_directory(self):
        # SEC2-01: measure_text.mjs moves to the install directory before it loads puppeteer;
        # the paths it was given still name files of the caller's directory
        caller = temp_dir(self)
        ran = caller / "ran.log"
        (caller / ".puppeteerrc.cjs").write_text(
            "require('fs').appendFileSync(%s, 'ran\\n');\nmodule.exports = {};\n"
            % json.dumps(str(ran)), encoding="utf-8")
        shutil.copyfile(str(HERE / "fixtures" / "fx-tree-v11.svg"), str(caller / "fig.svg"))
        proc = subprocess.run(["node", str(rc.MEASURE_SCRIPT), str(self.renderer.puppeteer_config),
                               "fig.svg", "--png", "fig.png"], cwd=str(caller),
                              capture_output=True, text=True, timeout=rc.MEASURE_TIMEOUT_S)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse(ran.exists())
        self.assertTrue((caller / "fig.png").is_file())
        self.assertEqual(os.path.realpath(json.loads(proc.stdout)["png"]),
                         os.path.realpath(str(caller / "fig.png")))


if __name__ == "__main__":
    unittest.main()
