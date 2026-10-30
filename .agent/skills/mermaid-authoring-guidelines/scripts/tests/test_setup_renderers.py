"""Tests for setup_renderers.sh (TASK 108, R7.1-R7.3, R7.9; acceptance A18).

Nothing here installs or downloads anything. `--dry-run` runs as is. The install steps that
follow `npm ci` run on an install home that already holds stand-ins of the pinned packages: the
script then only reads them, asks a stand-in `@puppeteer/browsers` for the stable browser, which
reports the build already under `<home>/chrome` as the real tool reports a cached build, writes
puppeteer.json and the empty .puppeteerrc.json, and smoke-renders with a stand-in `mmdc`, which
records the directory it runs in. A stand-in `npm` that fails shows the mode of a new install home. The
tests need bash, and node, which the script uses to
read JSON; without either they are skipped with the reason printed. The listing and install
tests also need npm and a node at or above the `engines.node` floor of the check pair; the
script refuses an older node, so on such a runner (a CI image with node 20) those tests are
skipped with the reason printed. The pinned pairs are read from `assets/notation.json`, never
restated here.
"""
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import mermaid_model as mm  # noqa: E402
import render_check as rc  # noqa: E402

SCRIPT = HERE.parent / "setup_renderers.sh"
NOTATION = mm.load_notation()
MISSING = [tool for tool in ("bash", "node") if shutil.which(tool) is None]
ASSETS = HERE.parent.parent / "assets" / "renderers"
#: The build of the stand-in browser; any build, since the setup installs the stable one of its
#: day and keeps no build number (TASK 137 D16).
BUILD = "156.0.8078.80"
#: v10 overrides the puppeteer of mermaid-cli 10.9.1 with the one of v11 and v12 (TASK 110 R7.1,
#: TASK 129 R3.2).
PUPPETEER = {"v10": "25.16.0", "v11": "25.16.0", "v12": "25.16.0"}
#: The overrides of each renderer manifest (TASK 129 R3.1).
DOMPURIFY = "3.4.17"
KATEX = "0.18.10"
HASH_VARIABLE = "MERMAID_RENDER_BROWSER_SHA256"

FAKE_MMDC = """#!/bin/sh
# Stand-in mmdc: records the directory it runs in and writes an SVG to the file after -o.
pwd -P >> "$(dirname "$0")/cwd.log"
out=""
while [ $# -gt 0 ]; do
  if [ "$1" = "-o" ]; then out="$2"; shift; fi
  shift
done
printf '<svg xmlns="http://www.w3.org/2000/svg"></svg>\\n' > "$out"
"""


def _version(text):
    return tuple(int(part) for part in text.strip().lstrip("v").split(".")[:3])


def listing_blocker():
    """Why the dry-run listing cannot pass on this machine, or None."""
    if shutil.which("npm") is None:
        return "npm not on PATH"
    have = subprocess.run(["node", "-p", "process.versions.node"], capture_output=True, text=True,
                          timeout=60).stdout
    for tag in NOTATION["renderers"]["check_pair"]:
        manifest = json.loads((ASSETS / tag / "package.json").read_text(encoding="utf-8"))
        floor = manifest.get("engines", {}).get("node", "").lstrip(">=").strip()
        if floor and _version(have) < _version(floor):
            return "node %s is older than %s, which the %s install requires" % (have.strip(), floor, tag)
    return None


def setUpModule():
    if MISSING:
        reason = "setup_renderers.sh tests skipped: %s not on PATH" % " and ".join(MISSING)
        print(reason, file=sys.stderr)
        raise unittest.SkipTest(reason)


#: Stand-in @puppeteer/browsers: reports the newest build already under --path, as the real tool
#: reports a cached build, in the --format of setup_renderers.sh; fails when there is none.
FAKE_BROWSERS = """#!/bin/sh
path=""
while [ $# -gt 0 ]; do
  if [ "$1" = "--path" ]; then path="$2"; shift; fi
  shift
done
found=""
for exe in "$path"/chrome-headless-shell/*/*/chrome-headless-shell \\
           "$path"/chrome-headless-shell/*/*/chrome-headless-shell.exe; do
  [ -e "$exe" ] || [ -L "$exe" ] || continue
  found="$exe"
done
if [ -z "$found" ]; then
  echo "Error: no network" >&2
  exit 1
fi
d="$(dirname "$(dirname "$found")")"
printf '%s\\t%s\\n' "${d##*-}" "$found"
"""


def tree_sha256(directory):
    """The tree hash of TASK 110 R7.3, computed here without the script: one JSON line per file,
    `["file", "./<path>", "<sha256>"]`, and per symbolic link, `["link", "./<path>", "<target>"]`,
    under *directory*, sorted bytewise by path; the sha256 of those lines."""
    directory = Path(directory)
    rows = []
    for path in directory.rglob("*"):
        rel = "./" + path.relative_to(directory).as_posix()
        if path.is_symlink():
            rows.append(["link", rel, os.readlink(path)])
        elif path.is_file():
            rows.append(["file", rel, hashlib.sha256(path.read_bytes()).hexdigest()])
    rows.sort(key=lambda row: row[1].encode())
    return hashlib.sha256("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                                  for row in rows).encode()).hexdigest()


def browser_in(cache, build=BUILD):
    """A stand-in chrome-headless-shell of *build* in a browser cache laid out as
    @puppeteer/browsers lays it out; `<home>/chrome` is the one of the setup."""
    exe = (cache / "chrome-headless-shell" / ("linux-%s" % build) / "chrome-headless-shell-linux64"
           / "chrome-headless-shell")
    exe.parent.mkdir(parents=True)
    exe.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    exe.chmod(0o755)
    return exe


class ScriptTest(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.tmp = Path(d.name).resolve()

    def run_script(self, home, *args, timeout=120, cwd=None, **env):
        full = dict(os.environ, MERMAID_RENDER_HOME=str(home))
        for key in ("MERMAID_RENDER_CHROME", "MERMAID_RENDER_NO_SANDBOX", HASH_VARIABLE):
            full.pop(key, None)
        full.update(env)
        return subprocess.run(["bash", str(SCRIPT), *args], env=full, capture_output=True,
                              text=True, timeout=timeout, cwd=None if cwd is None else str(cwd))

    def need_listing(self):
        blocker = listing_blocker()
        if blocker:
            print("setup_renderers.sh test skipped: %s" % blocker, file=sys.stderr)
            self.skipTest(blocker)


class TestDryRun(ScriptTest):
    def test_lists_the_three_pinned_pairs_and_writes_nothing(self):
        self.need_listing()
        home = self.tmp / "home"
        proc = self.run_script(home, "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        installs = NOTATION["renderers"]["installs"]
        self.assertEqual(len(installs), 3)
        for tag, pin in installs.items():
            self.assertIn("%s: mermaid-cli %s + mermaid %s" % (tag, pin["cli"], pin["mermaid"]),
                          proc.stdout)
        self.assertIn("--ignore-scripts", proc.stdout)
        self.assertIn("npm_config_cache=%s" % (home / ".npm-cache"), proc.stdout)
        self.assertFalse(home.exists(), "a dry run created the install home")

    def test_refuses_a_home_inside_a_git_work_tree(self):
        repo = self.tmp / "repo"
        repo.mkdir()
        if shutil.which("git"):
            subprocess.run(["git", "init", "-q", str(repo)], check=True, timeout=60)
        else:
            (repo / ".git").mkdir()
        home = repo / "cache"
        proc = self.run_script(home, "--dry-run")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("inside a git work tree", proc.stderr)
        self.assertFalse(home.exists())

    def test_refuses_a_home_with_a_dot_dot_segment(self):
        # `missing/..` reaches the repository once mkdir -p has made `missing`
        (self.tmp / "repo" / ".git").mkdir(parents=True)
        home = "%s/missing/../repo/cache" % self.tmp
        proc = self.run_script(home, "--dry-run")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("step 'check the install home' failed", proc.stderr)
        self.assertFalse((self.tmp / "missing").exists())

    def test_a_home_under_a_file_fails_at_its_step(self):
        # the walk to the nearest existing directory used to spin forever on a file
        blocker = self.tmp / "a-file"
        blocker.write_text("x", encoding="utf-8")
        for home in (blocker, blocker / "sub", Path("/dev/null/x")):
            with self.subTest(home=str(home)):
                try:
                    proc = self.run_script(home, "--dry-run", timeout=30)
                except subprocess.TimeoutExpired:
                    self.fail("setup_renderers.sh did not return within 30 s for %s" % home)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn("step 'check the install home' failed", proc.stderr)

    def test_refuses_a_relative_home(self):
        proc = self.run_script("relative/home", "--dry-run")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("absolute path", proc.stderr)

    def test_refuses_a_home_other_users_may_write_in(self):
        # SEC2-08: another user could plant an install there, or make the home first
        shared = self.tmp / "shared"
        shared.mkdir()
        shared.chmod(0o1777)
        self.addCleanup(shared.chmod, 0o700)
        for home in (shared / "mermaid", shared):
            with self.subTest(home=str(home)):
                proc = self.run_script(home, "--dry-run")
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn("step 'check the install home' failed: %s is writable by every "
                              "user" % shared, proc.stderr)
        self.assertEqual(list(shared.iterdir()), [])
        if listing_blocker() is None:
            own = shared / "mine"
            own.mkdir()
            own.chmod(0o700)
            proc = self.run_script(own / "home", "--dry-run")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_refuses_a_relative_browser_path(self):
        # every render runs in an install directory, where a relative path names another file
        proc = self.run_script(self.tmp / "home", "--dry-run", MERMAID_RENDER_CHROME="relative/b")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("step 'check the browser paths' failed: MERMAID_RENDER_CHROME must be an "
                      "absolute path", proc.stderr)

    def test_unknown_argument_is_a_usage_error(self):
        proc = self.run_script(self.tmp / "home", "--no-such-option")
        self.assertEqual(proc.returncode, 3, proc.stdout + proc.stderr)

    def test_the_dry_run_names_the_stable_browser_and_downloads_nothing(self):
        # TASK 137 D16: the setup installs the stable build of its day into <home>/chrome
        self.need_listing()
        home = self.tmp / "home"
        proc = self.run_script(home, "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("browser: chrome-headless-shell@stable from "
                      "https://storage.googleapis.com/chrome-for-testing-public into %s"
                      % (home / "chrome"), proc.stdout)
        self.assertFalse(home.exists(), "a dry run created the install home")


class StandInTest(ScriptTest):
    """An install home of stand-ins of the pinned packages and of @puppeteer/browsers, with a
    stand-in browser already in `<home>/chrome`, the cache of the setup (TASK 137 D16)."""

    def setUp(self):
        super().setUp()
        self.need_listing()
        self.home = self.tmp / "home"
        for tag in ("v10", "v11"):
            self.stand_in(tag)
        self.cache = self.home / "chrome"
        self.exe = browser_in(self.cache)

    def stand_in(self, tag):
        """An install of *tag* that the script reads as installed from the committed lockfile."""
        dest = self.home / tag
        modules = dest / "node_modules"
        (modules / ".bin").mkdir(parents=True)
        for d in (self.home, dest):
            d.chmod(0o755)  # private whatever the umask
        for package, version in (("mermaid", NOTATION["renderers"]["installs"][tag]["mermaid"]),
                                 ("puppeteer", PUPPETEER[tag])):
            (modules / package).mkdir()
            (modules / package / "package.json").write_text(json.dumps({"version": version}),
                                                            encoding="utf-8")
        mmdc = modules / ".bin" / "mmdc"
        mmdc.write_text(FAKE_MMDC, encoding="utf-8")
        mmdc.chmod(0o755)
        tool = modules / ".bin" / "browsers"
        tool.write_text(FAKE_BROWSERS, encoding="utf-8")
        tool.chmod(0o755)
        lock = (ASSETS / tag / "package-lock.json").read_bytes()
        (dest / ".lock.sha256").write_text(hashlib.sha256(lock).hexdigest() + "\n", encoding="utf-8")

    def setup(self, cwd=None, **env):
        """Run the script on the stand-ins."""
        return self.run_script(self.home, cwd=cwd, **env)

    def config(self, tag):
        path = self.home / tag / "puppeteer.json"
        return path, json.loads(path.read_text(encoding="utf-8"))


class TestInstallSteps(StandInTest):
    """The steps after `npm ci`, on stand-ins of the pinned packages; nothing is downloaded."""

    def test_the_written_config_blocks_the_network_and_uses_a_pipe(self):
        # R7.9: no host resolves, no proxy is used, and no DevTools port opens
        proc = self.setup()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        for tag in ("v10", "v11"):
            with self.subTest(tag=tag):
                path, cfg = self.config(tag)
                self.assertEqual(cfg["args"], list(rc.BROWSER_ARGS))
                self.assertIs(cfg["pipe"], True)
                self.assertEqual(cfg["executablePath"], str(self.exe))
                renderer = rc.Renderer(tag=tag, mermaid="", mmdc=path, puppeteer_config=path,
                                       root=path.parent)
                saved = os.environ.pop("MERMAID_RENDER_NO_SANDBOX", None)
                try:
                    self.assertIsNone(rc.config_problem(renderer))
                finally:
                    if saved is not None:
                        os.environ["MERMAID_RENDER_NO_SANDBOX"] = saved
        self.assertIn("(build %s" % BUILD, proc.stdout)

    def test_the_smoke_render_runs_in_the_install_directory(self):
        # SEC2-01: mmdc never runs in the caller's directory, whose puppeteer configuration it
        # would run; the install directory holds the empty one at which that search ends
        caller = self.tmp / "caller"
        caller.mkdir()
        proc = self.setup(cwd=caller)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        for tag in ("v10", "v11"):
            with self.subTest(tag=tag):
                dest = self.home / tag
                log = dest / "node_modules" / ".bin" / "cwd.log"
                self.assertEqual(log.read_text(encoding="utf-8").splitlines(), [str(dest)])
                self.assertEqual(json.loads((dest / rc.PUPPETEER_RC).read_text(encoding="utf-8")),
                                 {})
                path, _cfg = self.config(tag)
                renderer = rc.Renderer(tag=tag, mermaid="", mmdc=path, puppeteer_config=path,
                                       root=dest)
                self.assertIsNone(rc.install_problem(renderer))

    def test_an_install_other_users_may_write_in_is_not_run(self):
        # SEC2-08: setup never reports as installed, nor smoke-renders, what another user planted
        (self.home / "v10").chmod(0o777)
        self.addCleanup((self.home / "v10").chmod, 0o755)
        proc = self.setup()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("step 'copy the v10 manifests' failed: %s is writable by every user"
                      % (self.home / "v10"), proc.stderr)
        self.assertFalse((self.home / "v10" / "node_modules" / ".bin" / "cwd.log").exists())

    def test_a_new_install_home_is_private(self):
        # SEC2-08: a new home, and the directories made for it, get mode 0700; the stand-in npm
        # fails, so nothing is installed
        fake = self.tmp / "bin"
        fake.mkdir()
        (fake / "npm").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        (fake / "npm").chmod(0o755)
        home = self.tmp / "new" / "home"
        proc = self.run_script(home, PATH=str(fake) + os.pathsep + os.environ.get("PATH", ""))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("step 'npm ci for v10' failed", proc.stderr)
        for d in (home.parent, home):
            self.assertEqual(d.stat().st_mode & 0o777, 0o700, d)

    def test_no_sandbox_is_written_only_on_the_operator_switch(self):
        proc = self.setup(MERMAID_RENDER_NO_SANDBOX="1")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.config("v10")[1]["args"], list(rc.BROWSER_ARGS) + [rc.NO_SANDBOX_ARG])

    def test_a_missing_package_manifest_fails_at_its_step(self):
        shutil.rmtree(str(self.home / "v10" / "node_modules" / "puppeteer"))
        proc = self.setup()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("step 'browser for v10' failed", proc.stderr)
        self.assertNotIn("readFileSync", proc.stderr)

    def test_a_browser_the_tool_cannot_install_fails_and_names_the_way_out(self):
        # offline: the operator may name a browser at hand (TASK 137 D16)
        shutil.rmtree(str(self.cache))
        proc = self.setup()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("step 'browser for v10' failed: cannot install chrome-headless-shell@stable",
                      proc.stderr)
        self.assertIn("no network", proc.stderr)
        self.assertIn("MERMAID_RENDER_CHROME", proc.stderr)
        self.assertFalse((self.home / "v10" / "puppeteer.json").exists())


class TestBrowserHash(StandInTest):
    """TASK 110 R7.3, R7.7, TASK 137 D16: the setup runs the stable browser it installed into its
    cache, or a browser the operator names with its tree hash, and stamps the tree hash, the stat
    digest and the date of the install."""

    def operator_browser(self):
        """A stand-in browser outside the cache of the setup, for MERMAID_RENDER_CHROME."""
        return browser_in(self.tmp / "elsewhere")

    def test_the_installed_browser_is_stamped_with_its_hash_digest_and_date(self):
        proc = self.setup()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        for tag in ("v10", "v11"):
            with self.subTest(tag=tag):
                stamp = (self.home / tag / ".browser.sha256").read_text(encoding="utf-8")
                # the stat digest of the setup's node walk equals the one render_check.py
                # computes at every render (review round 3, N1)
                self.assertEqual(stamp, "%s  %s\nstat %s\ninstalled %s\n" % (
                    tree_sha256(self.exe.parent), self.exe, rc.browser_stat_digest(self.exe.parent),
                    today))

    def test_a_browser_the_operator_names_runs_with_its_hash_only(self):
        other = self.operator_browser()
        proc = self.setup(MERMAID_RENDER_CHROME=str(other))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        out = proc.stdout + proc.stderr
        self.assertIn(tree_sha256(other.parent), out)
        self.assertIn(HASH_VARIABLE, out)
        self.assertIn("confirm where this browser came from", out)
        self.assertIn("an agent stops here", out)
        self.assertFalse((self.home / "v10" / "puppeteer.json").exists())
        proc = self.setup(MERMAID_RENDER_CHROME=str(other), **{HASH_VARIABLE: tree_sha256(other.parent)})
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.config("v10")[1]["executablePath"], str(other))

    def test_a_differing_hash_is_refused(self):
        other = self.operator_browser()
        proc = self.setup(MERMAID_RENDER_CHROME=str(other), **{HASH_VARIABLE: "0" * 64})
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn(tree_sha256(other.parent), proc.stdout + proc.stderr)

    def test_an_installed_browser_that_leads_outside_the_cache_is_refused(self):
        # a link in the cache would run a binary that no download put there
        other = self.operator_browser()
        self.exe.unlink()
        self.exe.symlink_to(other)
        proc = self.setup()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("lies outside %s" % self.cache, proc.stderr)

    def test_older_builds_leave_the_cache(self):
        older = browser_in(self.cache, "155.0.8000.1")
        proc = self.setup()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse(older.parent.parent.exists(), "the older build stayed")
        self.assertTrue(self.exe.exists())

    def test_a_linked_browser_is_hashed_where_the_link_leads(self):
        link_dir = self.tmp / "links"
        link_dir.mkdir()
        link = link_dir / "chrome-headless-shell"
        link.symlink_to(self.exe)
        proc = self.setup(MERMAID_RENDER_CHROME=str(link),
                          **{HASH_VARIABLE: tree_sha256(self.exe.parent)})
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        # the hashed browser is the one that runs and the one stamped (review round 1, M1, L1)
        self.assertEqual(self.config("v10")[1]["executablePath"], str(self.exe))
        stamp = (self.home / "v10" / ".browser.sha256").read_text(encoding="utf-8")
        self.assertTrue(stamp.splitlines()[0].endswith("  %s" % self.exe), stamp)
        proc = self.setup(MERMAID_RENDER_CHROME=str(link), **{HASH_VARIABLE: tree_sha256(link_dir)})
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        # the dry run shows the path the install writes (review round 2, R2)
        proc = self.run_script(self.tmp / "dry", "--dry-run", MERMAID_RENDER_CHROME=str(link),
                               **{HASH_VARIABLE: tree_sha256(self.exe.parent)})
        self.assertIn("browser: %s (build %s)" % (self.exe, BUILD), proc.stdout)

    def test_a_link_to_another_program_is_refused(self):
        # review round 2, R1: a launcher picks its program by the name it was called by
        launcher = self.tmp / "links" / "chromium"
        launcher.parent.mkdir()
        launcher.symlink_to(self.exe)
        proc = self.setup(MERMAID_RENDER_CHROME=str(launcher))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("under another name", proc.stdout + proc.stderr)
        self.assertNotIn("to its tree hash", proc.stderr)

    def test_a_path_with_a_control_character_is_refused(self):
        # review round 1, M1: `$(...)` drops a trailing newline, so `/x/genuine\n/exe` read as
        # `/x/genuine` passed the hash of the genuine directory and ran another binary
        evil = self.tmp / "genuine\n"
        evil.mkdir()
        (evil / "chrome-headless-shell").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        (evil / "chrome-headless-shell").chmod(0o755)
        link = self.tmp / "chrome"
        link.symlink_to(evil / "chrome-headless-shell")
        proc = self.setup(MERMAID_RENDER_CHROME=str(link))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("control character", proc.stdout + proc.stderr)

    def test_an_unreadable_file_or_a_special_entry_is_refused(self):
        # review round 1, L2: the hash covers every byte of the directory, or the browser is refused
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root reads a file of mode 000")
        secret = self.exe.parent / "lib.so"
        secret.write_bytes(b"x")
        vouched = tree_sha256(self.exe.parent)  # the hash the operator would name
        secret.chmod(0o000)
        self.addCleanup(lambda: secret.exists() and secret.chmod(0o644))
        proc = self.setup(**{HASH_VARIABLE: vouched})
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("lib.so", proc.stdout + proc.stderr)
        secret.chmod(0o644)
        secret.unlink()
        os.mkfifo(str(self.exe.parent / "pipe"))
        proc = self.setup()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("neither a file, a directory nor a symbolic link", proc.stdout + proc.stderr)

    def test_a_browser_directory_others_may_write_in_is_refused(self):
        # review round 1, L1: another user could change the browser after the hash; the
        # refusal gives no hash advice, which cannot help here (review round 2, R5)
        self.exe.parent.chmod(0o777)
        self.addCleanup(self.exe.parent.chmod, 0o755)
        proc = self.setup()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("writable by every user", proc.stdout + proc.stderr)
        self.assertNotIn("to its tree hash", proc.stderr)

    def test_a_browser_file_others_may_write_is_refused(self):
        # review round 2, N2: a file another user may rewrite after the hash
        self.exe.chmod(0o777)
        self.addCleanup(self.exe.chmod, 0o755)
        proc = self.setup()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("writable by every user", proc.stdout + proc.stderr)

    def test_group_write_follows_the_own_group_rule(self):
        # review round 3, RG3-2: the walk, private_problem and render_check.py allow group write
        # only to a group named as the user; a shared primary group such as `staff` is refused
        import grp
        import pwd
        own = grp.getgrgid(os.getgid()).gr_name == pwd.getpwuid(os.getuid()).pw_name
        lib = self.exe.parent / "lib.dylib"
        lib.write_bytes(b"x")
        os.chown(str(lib), -1, os.getgid())
        lib.chmod(0o664)
        proc = self.setup()
        if own:
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        else:
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("writable by its group", proc.stdout + proc.stderr)

    def test_a_failed_smoke_render_is_not_reported_as_a_refused_hash(self):
        # review round 1, CR-08
        for tag in ("v10", "v11"):
            mmdc = self.home / tag / "node_modules" / ".bin" / "mmdc"
            mmdc.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        proc = self.setup()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("does not render with v10", proc.stderr)
        self.assertNotIn("is accepted", proc.stderr)

    def test_the_dry_run_prints_the_hash_of_a_named_browser_and_its_verdict(self):
        other = self.operator_browser()
        h = tree_sha256(other.parent)
        proc = self.run_script(self.tmp / "dry", "--dry-run", MERMAID_RENDER_CHROME=str(other))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("tree sha256 %s: refused, %s does not name it" % (h, HASH_VARIABLE), proc.stdout)
        proc = self.run_script(self.tmp / "dry", "--dry-run", MERMAID_RENDER_CHROME=str(other),
                               **{HASH_VARIABLE: h})
        self.assertIn("tree sha256 %s: accepted" % h, proc.stdout)


class TestRecordedBrowsers(unittest.TestCase):
    """TASK 110 R7.1: the v10 override."""

    def test_v10_overrides_puppeteer_and_holds_no_extract_zip(self):
        manifest = json.loads((ASSETS / "v10" / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["overrides"].get("puppeteer"), PUPPETEER["v10"])
        self.assertEqual(manifest["dependencies"]["mermaid"], NOTATION["renderers"]["installs"]["v10"]["mermaid"])
        lock = json.loads((ASSETS / "v10" / "package-lock.json").read_text(encoding="utf-8"))
        packages = lock["packages"]
        self.assertEqual(packages["node_modules/puppeteer"]["version"], PUPPETEER["v10"])
        self.assertFalse([k for k in packages if k.endswith("/extract-zip")])


def _package_name(key, entry):
    """The package of a lockfile entry: an alias's name, else the path after `node_modules/`."""
    return entry.get("name") or key.rpartition("node_modules/")[2]


class TestLockfileOverrides(unittest.TestCase):
    """TC-L1 (TASK 129 R3.1-R3.3, A4): each lockfile holds the overridden and pinned versions."""

    def test_l1_each_lockfile_holds_the_overridden_versions(self):
        for tag in sorted(NOTATION["renderers"]["installs"]):
            with self.subTest(tag=tag):
                manifest = json.loads((ASSETS / tag / "package.json").read_text(encoding="utf-8"))
                overrides = manifest.get("overrides", {})
                self.assertEqual(overrides.get("dompurify"), DOMPURIFY)
                self.assertEqual(overrides.get("katex"), KATEX)
                lock = json.loads((ASSETS / tag / "package-lock.json").read_text(encoding="utf-8"))
                packages = lock["packages"]
                pinned = NOTATION["renderers"]["installs"][tag]
                expected = {
                    "node_modules/dompurify": DOMPURIFY,
                    "node_modules/katex": KATEX,
                    "node_modules/puppeteer": PUPPETEER[tag],
                    "node_modules/mermaid": pinned["mermaid"],
                    "node_modules/@mermaid-js/mermaid-cli": pinned["cli"],
                }
                for key, version in expected.items():
                    self.assertEqual(packages.get(key, {}).get("version"), version, key)
                copies = [key for key, entry in packages.items()
                          if key not in expected
                          and _package_name(key, entry) in ("dompurify", "katex", "puppeteer")]
                self.assertEqual(copies, [])


if __name__ == "__main__":
    unittest.main()
