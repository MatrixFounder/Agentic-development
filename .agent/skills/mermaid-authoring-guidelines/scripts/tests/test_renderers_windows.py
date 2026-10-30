"""Tests of the Windows branches of setup_renderers.sh and render_check.py (TASK 137, MR-1).

On POSIX the tests simulate Windows. The setup runs with a module that NODE_OPTIONS preloads: it
sets `process.platform` to "win32" and removes `process.getuid`, as Node on Windows has them. The
render check runs with its platform flag patched. On Windows (the job of TASK 137 R11) the same
tests run with no simulation, under Git Bash, and the tests marked native run there only: an 8.3
short path, letter case, a junction and a real process tree. The setup runs on the stand-ins of
test_setup_renderers.py and a stand-in chrome-headless-shell.exe; nothing is installed or
downloaded. Without bash or node the setup tests are skipped with the reason printed, as in
test_setup_renderers.py.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE)]
import render_check as rc  # noqa: E402
import test_setup_renderers as tsr  # noqa: E402

#: True on Windows itself, where no simulation is needed.
NATIVE = os.name == "nt"
#: The preload of the simulation: the platform, and the uid that Node on Windows does not define.
WIN32_PRELOAD = ('Object.defineProperty(process, "platform", {value: "win32"});\n'
                 "process.getuid = undefined;\n")
#: The environment variables of the setup that hold a path; Git Bash reads them in its own form.
PATH_VARIABLES = ("MERMAID_RENDER_HOME", "MERMAID_RENDER_CHROME")
#: A child that starts a grandchild, writes its pid to the file argv[1] names, and waits.
TREE_CHILD = ("import subprocess, sys, time\n"
              "g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
              "open(sys.argv[1], 'w').write(str(g.pid))\n"
              "time.sleep(120)\n")


def win_browser_in(cache, build=tsr.BUILD):
    """A stand-in chrome-headless-shell.exe of *build*, laid out as @puppeteer/browsers lays out
    the win64 build."""
    exe = (cache / "chrome-headless-shell" / ("win64-%s" % build) / "chrome-headless-shell-win64"
           / "chrome-headless-shell.exe")
    exe.parent.mkdir(parents=True)
    exe.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    exe.chmod(0o755)
    return exe


def bash_path(path):
    """*path* in the form Git Bash reads on Windows (`/c/...`); unchanged elsewhere."""
    if not NATIVE:
        return str(path)
    return subprocess.run(["cygpath", "-u", str(path)], capture_output=True, text=True,
                          check=True, timeout=60).stdout.strip()


def same_path(a, b):
    """True when *a* and *b* name one file as Windows compares names: letter case ignored."""
    return os.path.normcase(os.path.realpath(str(a))) == os.path.normcase(os.path.realpath(str(b)))


def short_path(path):
    """The 8.3 short form of *path* on Windows, or *path* where the volume keeps none."""
    import ctypes
    buf = ctypes.create_unicode_buffer(32768)
    n = ctypes.windll.kernel32.GetShortPathNameW(str(path), buf, 32768)
    return buf.value if n else str(path)


def process_alive(pid):
    """True while the Windows process *pid* runs."""
    import ctypes
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(0x00100000 | 0x1000, False, pid)  # SYNCHRONIZE | QUERY_LIMITED
    if not handle:
        return False
    try:
        return kernel32.WaitForSingleObject(handle, 0) == 0x102  # WAIT_TIMEOUT
    finally:
        kernel32.CloseHandle(handle)


class WindowsSetupTest(tsr.StandInTest):
    """The stand-ins of test_setup_renderers.py with a Windows browser and mermaid-cli packages,
    and the setup run as on Windows, with the temporary directory as the user profile."""

    def setUp(self):
        if tsr.MISSING:
            self.skipTest("setup_renderers.sh tests skipped: %s not on PATH" % " and ".join(tsr.MISSING))
        if NATIVE and not os.environ.get("MSYSTEM"):
            self.skipTest("the setup tests run under Git Bash on Windows")
        super().setUp()
        # The POSIX stand-in leaves the setup's cache; the Windows build names its binary `.exe`.
        shutil.rmtree(str(self.exe.parent.parent))
        self.exe = win_browser_in(self.cache)
        # Enough entries for NTFS to give the directory an index allocation, whose size Python
        # reports and Node does not (TASK 137 D4; CI run 40920523466).
        for n in range(120):
            (self.exe.parent / ("locale-%03d-%s.pak" % (n, "x" * 24))).write_bytes(b"")
        # A link, whose size Node and Python report differently on Windows (D4).
        try:
            (self.exe.parent / "locale.pak").symlink_to("locale-000-%s.pak" % ("x" * 24))
        except OSError:
            pass  # Windows without the right to create a link
        # Python and Node on Windows report such bits for each writable file, and Git Bash
        # emulates them for a directory (TASK 137 §0).
        self.exe.chmod(0o777)
        self.exe.parent.chmod(0o777)
        self.addCleanup(lambda: self.exe.exists() and self.exe.chmod(0o755))
        self.addCleanup(lambda: self.exe.parent.exists() and self.exe.parent.chmod(0o755))
        for tag in ("v10", "v11"):
            self.mermaid_cli(tag)
        self.preload = self.tmp / "win32.js"
        self.preload.write_text(WIN32_PRELOAD, encoding="utf-8")

    def mermaid_cli(self, tag, bin_field=None):
        """A stand-in @mermaid-js/mermaid-cli of *tag* whose package.json names its mmdc script."""
        package = self.home / tag / "node_modules" / "@mermaid-js" / "mermaid-cli"
        (package / "src").mkdir(parents=True, exist_ok=True)
        (package / "src" / "cli.js").write_text("// stand-in\n", encoding="utf-8")
        manifest = {"version": tsr.NOTATION["renderers"]["installs"][tag].get("cli", ""),
                    "bin": bin_field if bin_field is not None else {"mmdc": "src/cli.js"}}
        (package / "package.json").write_text(json.dumps(manifest), encoding="utf-8")
        return package

    def run_script(self, home, *args, timeout=120, cwd=None, **env):
        full = dict(os.environ, MERMAID_RENDER_HOME=str(home), USERPROFILE=str(self.tmp))
        for key in ("MERMAID_RENDER_CHROME", "MERMAID_RENDER_NO_SANDBOX", "NODE_OPTIONS",
                    tsr.HASH_VARIABLE):
            full.pop(key, None)
        full.update(env)
        if NATIVE:
            for key in PATH_VARIABLES:
                if key in full:
                    full[key] = bash_path(full[key])
        else:
            full["NODE_OPTIONS"] = '--require "%s"' % self.preload
        bash = shutil.which("bash") or "bash"
        return subprocess.run([bash, str(tsr.SCRIPT), *args], env=full, capture_output=True,
                              text=True, timeout=timeout, cwd=None if cwd is None else str(cwd))

    def renderer(self, tag):
        dest = self.home / tag
        return rc.Renderer(tag=tag, mermaid="", mmdc=dest / "node_modules" / ".bin" / "mmdc",
                           puppeteer_config=dest / "puppeteer.json", root=dest)

    def windows(self):
        """The render check's platform flag set, and the temporary directory as the profile."""
        for patcher in (mock.patch.object(rc, "WINDOWS", True),
                        mock.patch.dict(os.environ, {"USERPROFILE": str(self.tmp)})):
            patcher.start()
            self.addCleanup(patcher.stop)

    def stamped_tree(self, tag="v11"):
        """The tree hash that the setup stamped into the install of *tag*."""
        stamp = (self.home / tag / rc.BROWSER_STAMP).read_text(encoding="utf-8")
        return stamp.splitlines()[0].partition("  ")[0]


class TestWindowsSetup(WindowsSetupTest):
    """TASK 137 R1 to R5, D10, D12: the setup finds, checks and stamps a Windows browser."""

    def test_w1_a_writable_exe_with_a_vouched_hash_is_installed(self):
        proc = self.setup()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        for tag in ("v10", "v11"):
            with self.subTest(tag=tag):
                cfg = json.loads((self.home / tag / "puppeteer.json").read_text(encoding="utf-8"))
                self.assertTrue(same_path(cfg["executablePath"], self.exe), cfg["executablePath"])
                self.assertTrue(cfg["executablePath"].endswith("chrome-headless-shell.exe"))
        self.assertIn("(build %s" % tsr.BUILD, proc.stdout)

    def test_w1_a_link_named_in_other_letter_case_is_the_browser(self):
        # NTFS compares names without letter case (TASK 137 R2): the name check of a link folds it
        link = self.tmp / "links" / "Chrome-Headless-Shell.exe"
        link.parent.mkdir()
        try:
            link.symlink_to(self.exe)
        except OSError as exc:
            self.skipTest("no symbolic link here: %s" % exc)
        proc = self.setup(MERMAID_RENDER_CHROME=str(link),
                          **{tsr.HASH_VARIABLE: tsr.tree_sha256(self.exe.parent)})
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("under another name", proc.stdout + proc.stderr)

    def test_w1_a_link_under_another_name_is_refused(self):
        # a launcher picks its program by the name it was called by; an 8.3 name is no link
        launcher = self.tmp / "links" / "chromium.exe"
        launcher.parent.mkdir()
        try:
            launcher.symlink_to(self.exe)
        except OSError as exc:
            self.skipTest("no symbolic link here: %s" % exc)
        proc = self.setup(MERMAID_RENDER_CHROME=str(launcher),
                          **{tsr.HASH_VARIABLE: tsr.tree_sha256(self.exe.parent)})
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("under another name", proc.stdout + proc.stderr)

    def test_w2_a_browser_the_operator_names_needs_its_hash(self):
        other = win_browser_in(self.tmp / "elsewhere")
        proc = self.setup(MERMAID_RENDER_CHROME=str(other))
        out = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 1, out)
        self.assertIn("is not the one MERMAID_RENDER_BROWSER_SHA256 names", out)
        self.assertIn(tsr.tree_sha256(other.parent), out)
        self.assertFalse((self.home / "v10" / "puppeteer.json").exists())

    def test_w3_the_stamped_stat_digest_is_the_one_the_render_check_computes(self):
        proc = self.setup()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.windows()
        digest = rc.browser_stat_digest(Path(os.path.realpath(str(self.exe))).parent)
        for tag in ("v10", "v11"):
            with self.subTest(tag=tag):
                stamp = (self.home / tag / rc.BROWSER_STAMP).read_text(encoding="utf-8")
                self.assertEqual(stamp.splitlines()[1], "stat %s" % digest)

    def test_w17_a_debug_log_beside_the_browser_is_left_out_of_the_hash(self):
        # D14: Chrome writes debug.log beside its executable on Windows (CI run 40953801835)
        without = tsr.tree_sha256(self.exe.parent)
        (self.exe.parent / "debug.log").write_text("[1029/120000:ERROR] logged\n", encoding="utf-8")
        proc = self.setup()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.stamped_tree(), without)
        self.windows()
        stamp = (self.home / "v11" / rc.BROWSER_STAMP).read_text(encoding="utf-8")
        digest = rc.browser_stat_digest(Path(os.path.realpath(str(self.exe))).parent)
        self.assertEqual(stamp.splitlines()[1], "stat %s" % digest)

    def test_w17_a_debug_log_with_a_second_link_is_hashed(self):
        # audit L-1: only a debug.log of one link is left out of the tree hash
        other = self.tmp / "elsewhere.txt"
        other.write_text("x\n", encoding="utf-8")
        os.link(str(other), str(self.exe.parent / "debug.log"))
        proc = self.setup()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.stamped_tree(), tsr.tree_sha256(self.exe.parent))

    def test_w9_a_home_outside_the_profile_is_refused(self):
        profile = self.tmp / "profile"
        profile.mkdir()
        proc = self.setup(USERPROFILE=str(profile))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("lies outside %USERPROFILE%", proc.stderr)
        self.assertFalse((self.home / "v10" / "puppeteer.json").exists())

    @unittest.skipUnless(NATIVE, "an 8.3 short name exists on Windows only")
    def test_w13_native_a_short_path_is_stamped_in_its_long_form(self):
        # D10: Node's fs.realpathSync keeps `RUNNER~1`, which Python resolves to the long name
        short = short_path(self.exe)
        if short == str(self.exe):
            self.skipTest("this volume keeps no 8.3 name for %s" % self.exe)
        proc = self.setup(MERMAID_RENDER_CHROME=short,
                          **{tsr.HASH_VARIABLE: tsr.tree_sha256(self.exe.parent)})
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        cfg = json.loads((self.home / "v11" / "puppeteer.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["executablePath"], os.path.realpath(str(self.exe)))


class TestWindowsRenderCheck(WindowsSetupTest):
    """TASK 137 R6 to R8a, D12: the render check runs the install that the setup made."""

    def setUp(self):
        super().setUp()
        proc = self.setup()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.node_dir = self.tmp / "nodebin"
        self.node_dir.mkdir()
        self.node = self.node_dir / "node.exe"
        self.node.write_text("stand-in\n", encoding="utf-8")
        # A node.exe planted where a relative PATH entry leads, as `.` leads to the project.
        planted = self.tmp / "planted"
        planted.mkdir()
        (planted / "node.exe").write_text("planted\n", encoding="utf-8")
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(str(self.tmp))
        path_env = mock.patch.dict(os.environ,
                                   {"PATH": os.pathsep.join(["planted", str(self.node_dir)])})
        path_env.start()
        self.addCleanup(path_env.stop)
        self.windows()

    def test_w4_the_install_runs_until_a_file_of_the_browser_changes(self):
        renderer = self.renderer("v11")
        self.assertIsNone(rc.install_problem(renderer))
        with open(str(self.exe), "ab") as fh:
            fh.write(b"\n")
        problem = rc.install_problem(renderer)
        self.assertIsNotNone(problem)
        self.assertIn("changed since the setup hashed it", problem)

    def test_w17_a_debug_log_that_chrome_writes_after_the_setup_is_not_a_change(self):
        # D14: the file and the mtime of its directory change at a render on Windows
        renderer = self.renderer("v11")
        log = self.exe.parent / "debug.log"
        log.write_text("[1029/120000:ERROR] logged\n", encoding="utf-8")
        self.assertIsNone(rc.install_problem(renderer))
        with open(str(log), "a", encoding="utf-8") as fh:
            fh.write("[1029/120001:ERROR] logged again\n")
        self.assertIsNone(rc.install_problem(renderer))
        log.unlink()
        log.mkdir()  # a directory of that name is an entry like any other
        problem = rc.install_problem(renderer)
        self.assertIsNotNone(problem)
        self.assertIn("changed since the setup hashed it", problem)

    def test_w17_a_debug_log_with_a_second_link_is_an_entry(self):
        # audit L-1: a hard link would let Chrome append its log to another file
        other = self.tmp / "elsewhere.txt"
        other.write_text("x\n", encoding="utf-8")
        os.link(str(other), str(self.exe.parent / "debug.log"))
        problem = rc.install_problem(self.renderer("v11"))
        self.assertIsNotNone(problem)
        self.assertIn("changed since the setup hashed it", problem)

    def test_w18_renders_go_to_the_profile_only(self):
        # audit M-2: on Windows `--out` lies in the profile, as the install does
        profile = self.tmp / "profile"
        profile.mkdir()
        figure = self.tmp / "f.mmd"
        figure.write_text("flowchart TB\n  A --> B\n", encoding="utf-8")
        err = io.StringIO()
        with mock.patch.dict(os.environ, {"USERPROFILE": str(profile)}), redirect_stderr(err), \
                redirect_stdout(io.StringIO()):
            code = rc.main([str(figure), "--out", str(self.tmp / "renders")])
        self.assertEqual(code, rc.EXIT_USAGE, err.getvalue())
        self.assertIn("lies outside %USERPROFILE%", err.getvalue())

    def test_w19_json_on_windows_is_ascii_and_reads_back(self):
        # audit I-d: a pipe on Windows writes the ANSI code page
        report = {"label": "Привет \u2192 \U0001F600", "n": 1}
        text = rc._json_out(report)
        self.assertTrue(text.isascii(), text)
        self.assertEqual(json.loads(text), report)

    def test_w5_a_render_starts_node_by_its_path_with_the_cli_script(self):
        renderer = self.renderer("v11")
        out = self.tmp / "out"
        cmd = rc.mmdc_command(renderer, out / "f.mmd", out / "f.svg", out / "c.json", "white",
                              None, 800)
        script = (self.home / "v11" / "node_modules" / "@mermaid-js" / "mermaid-cli" / "src"
                  / "cli.js").resolve()
        self.assertEqual(cmd[:3], [str(self.node), str(script), "-q"])
        measure = rc.measure_command(renderer, out / "f.svg", out / "f.png", "white",
                                     tsr.NOTATION)
        self.assertEqual(measure[0], str(self.node))

    def test_w5_a_quoted_path_entry_is_read(self):
        with mock.patch.dict(os.environ, {"PATH": '"%s"' % self.node_dir}):
            self.assertEqual(rc.node_executable(), str(self.node))

    def test_w5_a_cli_script_outside_its_package_is_refused(self):
        outside = self.home / "v11" / "outside.js"
        outside.write_text("// planted\n", encoding="utf-8")
        self.mermaid_cli("v11", bin_field={"mmdc": "../../../outside.js"})
        problem = rc.install_problem(self.renderer("v11"))
        self.assertIsNotNone(problem)
        self.assertIn("outside", problem)

    def test_w5_a_cli_script_that_links_outside_its_package_is_refused(self):
        outside = self.home / "v11" / "outside.js"
        outside.write_text("// planted\n", encoding="utf-8")
        script = self.mermaid_cli("v11") / "src" / "cli.js"
        script.unlink()
        try:
            script.symlink_to(outside)
        except OSError as exc:
            self.skipTest("no symbolic link here: %s" % exc)
        problem = rc.install_problem(self.renderer("v11"))
        self.assertIsNotNone(problem)
        self.assertIn("outside", problem)

    def test_w11_a_cli_script_with_a_drive_a_root_or_a_share_is_refused_by_its_text(self):
        # I-2: no path of such a value is resolved or opened, so a share receives no connection
        for value in ("C:\\x.js", "\\\\host\\share\\x.js", "/etc/x.js", "src/../../x.js"):
            with self.subTest(value=value):
                self.mermaid_cli("v11", bin_field={"mmdc": value})
                with mock.patch.object(rc.Path, "resolve", side_effect=AssertionError("resolved")):
                    script, problem = rc.mmdc_script(self.home / "v11")
                self.assertIsNone(script)
                self.assertIn("outside", problem)

    def test_w5_no_node_on_an_absolute_path_is_refused(self):
        with mock.patch.dict(os.environ, {"PATH": "planted"}):
            problem = rc.install_problem(self.renderer("v11"))
        self.assertIsNotNone(problem)
        self.assertIn("node.exe", problem)

    def test_w9_an_install_outside_the_profile_is_refused(self):
        profile = self.tmp / "profile"
        profile.mkdir()
        with mock.patch.dict(os.environ, {"USERPROFILE": str(profile)}):
            problem = rc.install_problem(self.renderer("v11"))
        self.assertIsNotNone(problem)
        self.assertIn("lies outside %USERPROFILE%", problem)

    def test_w12_a_digest_that_cannot_be_built_is_refused(self):
        # m1, L-4: a name UTF-8 cannot carry, or a walk without end, is a refusal, not a traceback
        for exc in (UnicodeEncodeError("utf-8", "\ud800", 0, 1, "surrogates not allowed"),
                    RecursionError("maximum recursion depth exceeded")):
            with self.subTest(exc=type(exc).__name__):
                with mock.patch.object(rc, "browser_stat_digest", side_effect=exc):
                    problem = rc.install_problem(self.renderer("v11"))
                self.assertIsNotNone(problem)
                self.assertIn("changed since the setup hashed it", problem)

    @unittest.skipUnless(NATIVE, "NTFS letter case is read on Windows only")
    def test_w14_native_a_stamped_path_in_other_letter_case_is_the_same_browser(self):
        # R6: os.path.realpath gives the case on disk; the stamp may hold another
        renderer = self.renderer("v11")
        upper = str(os.path.realpath(str(self.exe))).upper()
        cfg_path = self.home / "v11" / "puppeteer.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cfg["executablePath"] = upper
        cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
        stamp = self.home / "v11" / rc.BROWSER_STAMP
        lines = stamp.read_text(encoding="utf-8").splitlines()
        lines[0] = "%s  %s" % (lines[0].partition("  ")[0], upper)
        stamp.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertIsNone(rc.install_problem(renderer))


@unittest.skipUnless(NATIVE, "a junction exists on Windows only")
class TestWindowsJunction(WindowsSetupTest):
    """TASK 137 D4: a junction is a link on both sides, and the walk does not enter it."""

    def test_w15_native_a_junction_in_the_browser_directory_is_read_as_a_link(self):
        import _winapi
        target = self.tmp / "resources"
        target.mkdir()
        (target / "data.pak").write_bytes(b"x")
        _winapi.CreateJunction(str(target), str(self.exe.parent / "resources"))
        proc = self.setup()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.windows()
        self.assertIsNone(rc.install_problem(self.renderer("v11")))


class TestWindowsTimeout(unittest.TestCase):
    """TASK 137 R9, D7, D9: a command on Windows starts by its path and ends with its tree."""

    def test_w6_a_timed_out_command_ends_through_taskkill(self):
        calls, started = [], []
        real_popen = subprocess.Popen

        def fake_run(cmd, *args, **kwargs):
            calls.append(list(cmd))
            return subprocess.CompletedProcess(cmd, 0)

        def popen(*args, **kwargs):
            proc = real_popen(*args, **kwargs)
            started.append(proc)
            self.addCleanup(lambda: proc.poll() is None and proc.kill())
            return proc

        sleeper = [sys.executable, "-c", "import time; time.sleep(60)"]
        with mock.patch.object(rc, "WINDOWS", True), \
                mock.patch.object(rc.subprocess, "run", fake_run), \
                mock.patch.object(rc.subprocess, "Popen", popen):
            code, _out, err = rc._run(sleeper, 1, HERE)
        self.assertIsNone(code)
        self.assertIn("timed out after 1 s", err)
        self.assertEqual(len(calls), 1, calls)
        self.assertEqual(calls[0][:4], [rc.taskkill_path(), "/T", "/F", "/PID"])
        self.assertEqual(calls[0][4], str(started[0].pid))
        self.assertIsNotNone(started[0].poll(), "the command still runs")
        if NATIVE:
            self.assertTrue(os.path.isfile(calls[0][0]), calls[0][0])

    def test_w10_a_program_named_by_a_bare_name_is_not_started(self):
        # D9: CreateProcess searches the caller's directory for a bare name
        with mock.patch.object(rc, "WINDOWS", True), \
                mock.patch.object(rc.subprocess, "Popen", side_effect=AssertionError("started")):
            code, _out, err = rc._run(["node", "-v"], 5, HERE)
        self.assertIsNone(code)
        self.assertIn("absolute path only", err)

    @unittest.skipUnless(NATIVE, "taskkill runs on Windows only")
    def test_w16_native_the_process_tree_of_a_timed_out_command_ends(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            pid_file = Path(tmp) / "grandchild.pid"
            code, _out, err = rc._run([sys.executable, "-c", TREE_CHILD, str(pid_file)], 5,
                                      Path(tmp))
            self.assertIsNone(code)
            self.assertIn("timed out", err)
            grandchild = int(pid_file.read_text(encoding="utf-8"))
            deadline = time.monotonic() + 10
            while process_alive(grandchild) and time.monotonic() < deadline:
                time.sleep(0.2)
            self.assertFalse(process_alive(grandchild), "the grandchild still runs")


if __name__ == "__main__":
    unittest.main()
