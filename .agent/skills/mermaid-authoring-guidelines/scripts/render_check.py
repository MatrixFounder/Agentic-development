#!/usr/bin/env python3
"""Render a figure in pinned Mermaid versions and check what the reader sees (TASK 108, R7).

Renders each `mermaid` fence of a `.md` file, or a `.mmd` file, with the installs that
`setup_renderers.sh` placed under `${MERMAID_RENDER_HOME:-~/.cache/mermaid-authoring-guidelines}`.
The default renders are the check pair of `notation.json` (11.17.2, the version GitHub runs, and
10.9.8, the floor), plus a dark render of 11.17.2 in theme `dark` on GitHub's dark page colour.
`--forward` adds 12.1.0, rendered with `-t default`: without it mermaid-cli 12 draws its own
`redux` theme in a 14 px font that no viewer of TASK section 1 uses. A forward render is
information only: it is reported with its own status and sets no exit code (TASK D3). Mermaid
runs with `securityLevel: strict`; the browser resolves no host name and uses no proxy, so a
render fetches nothing from the network. Text is measured in the browser by `measure_text.mjs`;
geometry and contrast come from `svg_geometry.py`.

A check is complete only with every render of the check pair and the dark render. `--no-dark`
skips the dark render and `--versions` may leave out a version; the run then does the other
renders and reports `not rendered: dark render skipped` (or `not rendered: <tag> render
skipped`), exit 2 unless a figure fails (TASK R7.4, D4). An input with no mermaid fence renders
nothing: it reports `not rendered: no mermaid fence found in <file>`, exit 2 (invariant L6).

A figure of a kind whose geometry `svg_geometry` does not model (quadrantChart, timeline,
journey, mindmap, gitGraph and the like; an ER or requirement figure read only in part) passes as
`pass, geometry not checked`, in the text and in the JSON: its size, text, clipping, contrast
and the overlap of its texts are measured; its crossings and edges through nodes are not, and
the PNG answers for them.

Every render is written outside the repository: `--out DIR`, or a fresh `check-*` directory
under `${MERMAID_RENDER_HOME}/renders/`, of which the newest RENDER_KEEP are kept; a run removes
the older ones, so pass `--out` to keep a render. A path inside a git work tree is refused; the
path is resolved first, so `missing/..` and a symlink are read as the directory they reach.

Exit codes (TASK D20, ARCHITECTURE §7.4)
  0  every figure passed in every required render (`pass` or `pass, geometry not checked`)
  1  a figure fails: a threshold, or its source does not parse in a pinned version; or a
     negative fence fails a render check it does not name, or names render checks and none
     of them fails (a broken example)
  2  not rendered: renderers or browser absent or not to be run, a required render skipped,
     the renderer crashed, an input holds no mermaid fence, or the renders or the fixture
     cannot be written; prints `not rendered: <reason>` and is never a pass (invariant L6)
  3  usage error, including an `--out` that is not a directory or that another user may write
     in, and a `--fixture` file that is not a render-evidence fixture

Negative fences (TASK R9.4). A fence whose last non-blank body line is the Mermaid comment
`%% negative: <name>, <name>` shows a defect on purpose. The check reads the marker as the lint
reads it (`mermaid_model`). The marker counts only in a file that
`mermaid_model.negative_allowed` accepts: the skill's own `references/` and
`scripts/tests/fixtures/`. In any other file the fence is checked as an ordinary figure, and the
report says the marker was ignored. Its names are lint rule ids or families and render check
names (`svg_geometry.GATE_CHECKS`). The fence is rendered and measured like any figure. A
failure of a render check it names is expected and sets no exit code. A failure of any other
render check fails the fence, as it fails a positive figure. A fence whose marker names no
render check is thus graded on its renders as a positive figure. When the marker names render
checks, at least one of them must report its defect in a required render that ran
(`svg_geometry.fired`); otherwise the example is broken and the run exits 1. A parse or render
error in a required render stays a failure unless the marker names a parse check: a rule or
the family of PARSE_FAMILIES. Lint names are otherwise left to `lint_mermaid.py`.

Evidence (TASK R7.8). Per figure the report records the sha256 of the fence text
(`mermaid_model.fence_sha256`: the body lines, each ended by LF), each renderer version, the
browser build and the font family the browser drew. `--json` prints the report and writes it as
`evidence.json` next to the renders. `--fixture FILE` also writes the hash-bound evidence that
the unit tests read without node (TASK R9.5, A19): one entry per file and fence line with the
sha256, the versions, the browser, the metrics and findings of each render, and the negative
flag and names; per file, the sha256 of the instruments (INSTRUMENT_FILES) and the notation
values that shaped the renders. Its keys are paths relative to the skill directory; an existing
fixture keeps the entries of the other files. It is written only when every required render
ran, and only over a file that does not exist yet or already is a render-evidence fixture.

The browser runs with its sandbox. `--no-sandbox` is passed only when the environment sets
`MERMAID_RENDER_NO_SANDBOX=1`.

How a failed render is classified. A parse error, an unknown diagram type, or an exception raised
inside mermaid's own code while it draws the figure (12.1 on two edge ids that collide) is a fact
about the figure in that version: in a required render the figure fails, exit 1. A browser that
does not start, a timeout, a protocol error, a missing install or a render directory that cannot
be written says nothing about the figure: not rendered, exit 2. When both occur, exit 1 wins,
and every render that did not run is still listed.

Renders per figure. Each figure is rendered once per requested version at the width of
`notation.renderers.render_width_px`; a flowchart, state or sequence figure keeps its natural
size at any page width. A gantt is drawn as wide as its container, so it is rendered at the
document column (`notation.column_px`): the check then measures the chart a reader sees in that
column. The PNG is a screenshot of the SVG at twice its natural size, for the visual check.

Every renderer config is checked before use: its `puppeteer.json` must be exactly what
`setup_renderers.sh` writes: the keys `executablePath`, `headless`, `args` and `pipe`; `pipe`
true; the arguments BROWSER_ARGS, followed by `--no-sandbox` only when
`MERMAID_RENDER_NO_SANDBOX=1` is set. A config that is not is not run. Over the pipe the browser
opens no DevTools port and exits with the process that started it.

Every node process of a render (mmdc and `measure_text.mjs`) runs in the install directory of
its renderer, never in the caller's directory. Puppeteer searches its working directory and each
parent for a configuration and runs one written in JavaScript (`.puppeteerrc.cjs`,
`puppeteer.config.js`); the empty PUPPETEER_RC that `setup_renderers.sh` writes into each
install directory ends that search there. An install runs only when it holds that file and when
the install home and the install directory are private (`private_dir_problem`): they belong to
this user or root, and no other user may write in them. `--out` must be private too, or another
user could plant a symlink under the predictable name of a render.

Standard library only; node, the installs and the browser are needed only to render.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mermaid_model as mm  # noqa: E402
import svg_geometry as sg  # noqa: E402

EXIT_PASS, EXIT_FAIL, EXIT_NOT_RENDERED, EXIT_USAGE = 0, 1, 2, 3

DEFAULT_HOME = Path(os.path.expanduser("~")) / ".cache" / "mermaid-authoring-guidelines"
SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS_DIR.parent
MEASURE_SCRIPT = SCRIPTS_DIR / "measure_text.mjs"

RENDER_TIMEOUT_S = 180
MEASURE_TIMEOUT_S = 120
#: Seconds between the SIGTERM and the SIGKILL of a command that timed out: on SIGTERM
#: puppeteer closes the browser it started.
TERM_GRACE_S = 5
PNG_SCALE = 2
#: mermaid-cli 10 and 11 draw a container-wide figure `-w` minus the page margins (8 px each
#: side; measured on 10.9.1 and 11.17.0). mermaid-cli 12 `--size` is the drawing width itself.
MMDC_PAGE_MARGIN_PX = 16
#: The browser arguments `setup_renderers.sh` writes into every puppeteer.json, in this order
#: (TASK R7.9). No host name resolves, localhost included, and no proxy is used, so a figure
#: cannot make the browser fetch anything; a later `--host-resolver-rules` would replace the first.
BROWSER_ARGS = ("--host-resolver-rules=MAP * ~NOTFOUND", "--no-proxy-server")
#: Appended to BROWSER_ARGS only when the operator sets MERMAID_RENDER_NO_SANDBOX=1.
NO_SANDBOX_ARG = "--no-sandbox"
#: Chrome switches, with or without a value, that turn the sandbox off.
_SANDBOX_SWITCHES = ("--no-sandbox", "--disable-setuid-sandbox", "--no-zygote")
#: The keys of a puppeteer.json. `pipe: true` makes puppeteer talk to the browser over a pipe:
#: no DevTools port opens, and the browser exits when the process that started it dies.
CONFIG_KEYS = frozenset({"executablePath", "headless", "args", "pipe"})
HEADLESS_MODES = (True, "new", "shell")
#: The empty puppeteer configuration `setup_renderers.sh` writes into each install directory.
#: Puppeteer reads the first configuration it finds from its working directory up: this one ends
#: the search in the install directory, so no file of a parent directory is read or run.
PUPPETEER_RC = ".puppeteerrc.json"
#: The theme mermaid-cli 12 is given for a light render (its own default is `redux`).
FORWARD_LIGHT_THEME = "default"
#: `check-*` render directories kept under `${MERMAID_RENDER_HOME}/renders`, the new one included.
RENDER_KEEP = 20

FIXTURE_SCHEMA = "render-evidence-fixture/v1"
#: Files whose content decides the stored metrics of a render. The fixture records their sha256,
#: so evidence measured by other instruments reads as stale (TASK R9.5). `mermaid_model.py` is
#: left out: the fence hash already binds the text it extracts, and the lint changes it often.
INSTRUMENT_FILES = ("scripts/render_check.py", "scripts/svg_geometry.py",
                    "scripts/measure_text.mjs")
#: Lint families whose rules say a source does not parse in a pinned version. A negative fence
#: that names one of them, or one of their rules, may show a parse or render error.
PARSE_FAMILIES = ("PARSE", "SYN")

_PARSE_FAILURE = re.compile(r"Parse error|Lexical error|UnknownDiagramError|No diagram type detected|"
                            r"Syntax error in|YAMLException|ParseError", re.IGNORECASE)
_MERMAID_FRAME = re.compile(r"node_modules/mermaid/|/mermaid/dist/")
_INFRA_FAILURE = re.compile(r"Failed to launch|Browser was not found|TimeoutError|timed out|Protocol error|"
                            r"Target closed|ECONNREFUSED|ENOENT|EACCES|socket hang up|"
                            r"Navigation timeout|Session closed", re.IGNORECASE)


def render_home() -> Path:
    """Return the install home: `$MERMAID_RENDER_HOME` or the default cache directory, resolved.

    The node processes of a render run in an install directory, not in the caller's directory,
    so every path they receive is absolute."""
    env = os.environ.get("MERMAID_RENDER_HOME")
    return (Path(env).expanduser() if env else DEFAULT_HOME).resolve()


@dataclass
class Renderer:
    tag: str  # "v10" | "v11" | "v12"
    mermaid: str  # version string the install reports
    mmdc: Path  # path to node_modules/.bin/mmdc
    puppeteer_config: Path
    root: Path
    cli: str = ""  # mermaid-cli version the install reports
    browser: str = ""  # executablePath of puppeteer.json


@dataclass
class RenderResult:
    tag: str
    dark: bool
    ok: bool
    svg: Optional[Path]
    png: Optional[Path]
    log: str
    metrics: dict = field(default_factory=dict)
    findings: list = field(default_factory=list)
    #: "ok", "parse_error" or "render_error" (the figure fails), "not_rendered" (no verdict)
    status: str = ""
    browser: str = ""  # browser version the measurement ran in
    measure: Optional[Path] = None  # the measure_text.mjs JSON next to the SVG
    font_family: str = ""  # the platform font that drew most glyphs
    fonts: list = field(default_factory=list)  # [{"family", "glyphs"}], most glyphs first


# ----------------------------------------------------------------------------- helpers


def inside_git_work_tree(path: Path) -> bool:
    """True when *path*, or its nearest existing ancestor, lies inside a git work tree.

    The path is resolved before the walk: `missing/../repo` is read as `repo`, and a symlink as
    the directory it reaches, which is where `mkdir` would write.
    """
    p = Path(path).expanduser().resolve()
    while not p.exists() and p != p.parent:
        p = p.parent
    for d in [p, *p.parents]:
        if (d / ".git").exists():
            return True
    return False


def out_dir_problem(path: Path) -> Optional[str]:
    """Why *path* cannot hold renders, or None: it, or its nearest existing ancestor, is a file."""
    p = Path(path).expanduser().absolute()
    if p.exists():
        return None if p.is_dir() else "%s is not a directory" % p
    for parent in p.parents:
        if parent.exists():
            return None if parent.is_dir() else "%s runs through the file %s" % (p, parent)
    return None


def _own_group(gid: int) -> bool:
    """True when *gid* is this user's private group: the primary group, named as the user."""
    try:
        import grp
        import pwd
        user = pwd.getpwuid(os.geteuid())
        return gid == user.pw_gid and grp.getgrgid(gid).gr_name == user.pw_name
    except (ImportError, KeyError):
        return False


def private_dir_problem(path: Path) -> Optional[str]:
    """Why *path*, or its nearest existing ancestor, is open to another user, or None.

    It must belong to this user or root, and no one else may write in it: not every user, and
    its group only when that group is this user's own (`_own_group`, as user-private-group
    systems make). Another user could otherwise plant an install, a puppeteer configuration or
    a symlink under the name of a render (TASK R7.9). A symlink is read as what it reaches.
    """
    if not hasattr(os, "geteuid"):
        return None
    p = Path(path).expanduser().absolute()
    while not p.exists() and p != p.parent:
        p = p.parent
    try:
        st = p.stat()
    except OSError as exc:
        return "%s cannot be read: %s" % (p, exc)
    if st.st_uid not in (os.geteuid(), 0):
        return "%s belongs to another user (uid %d)" % (p, st.st_uid)
    if st.st_mode & stat.S_IWOTH:
        return "%s is writable by every user" % p
    if st.st_mode & stat.S_IWGRP and not _own_group(st.st_gid):
        return "%s is writable by its group" % p
    return None


def prune_renders(base: Path, keep: int) -> list:
    """Remove all but the newest *keep* `check-*` directories under *base*; return the removed.

    Only directories this script names (`tempfile.mkdtemp(prefix="check-")`) are touched; a
    symlink or a file of that name stays, and so does a directory that cannot be removed.
    """
    def mtime(d):
        try:
            return d.stat().st_mtime
        except OSError:
            return 0.0

    try:
        dirs = [d for d in Path(base).iterdir()
                if d.name.startswith("check-") and not d.is_symlink() and d.is_dir()]
    except OSError:
        return []
    dirs.sort(key=mtime, reverse=True)
    removed = []
    for d in dirs[max(0, keep):]:
        try:
            shutil.rmtree(str(d))
        except OSError:
            continue
        removed.append(d)
    return removed


def _package_version(package_json: Path) -> Optional[str]:
    try:
        with open(package_json, encoding="utf-8") as fh:
            return str(json.load(fh).get("version") or "") or None
    except (OSError, ValueError):
        return None


def _load_puppeteer_config(path: Path) -> Optional[dict]:
    try:
        with open(path, encoding="utf-8") as fh:
            cfg = json.load(fh)
        return cfg if isinstance(cfg, dict) else None
    except (OSError, ValueError):
        return None


def config_problem(renderer: Renderer) -> Optional[str]:
    """Why a renderer's puppeteer.json may not be used, or None when it is acceptable.

    It must be exactly what `setup_renderers.sh` writes (TASK R7.9): the keys of CONFIG_KEYS,
    `pipe` true, a headless mode, a browser that exists at an absolute path, and the arguments
    BROWSER_ARGS, followed by `--no-sandbox` only when `MERMAID_RENDER_NO_SANDBOX=1`. Any other
    argument is refused: a second `--host-resolver-rules`, a proxy, `--no-sandbox=1` or a
    DevTools port would each undo a guard.
    """
    path = renderer.puppeteer_config
    cfg = _load_puppeteer_config(path)
    if cfg is None:
        return "%s does not parse" % path
    again = "; run setup_renderers.sh again"
    extra = sorted(set(cfg) - CONFIG_KEYS)
    if extra:
        return "%s holds keys setup_renderers.sh does not write: %s%s" % (path, ", ".join(extra), again)
    args = cfg.get("args")
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        return "%s has no list of browser arguments%s" % (path, again)
    no_sandbox = os.environ.get("MERMAID_RENDER_NO_SANDBOX") == "1"
    if not no_sandbox and any(a.split("=", 1)[0] in _SANDBOX_SWITCHES for a in args):
        return "%s disables the browser sandbox but MERMAID_RENDER_NO_SANDBOX is not 1" % path
    allowed = [list(BROWSER_ARGS)]
    if no_sandbox:
        allowed.append(list(BROWSER_ARGS) + [NO_SANDBOX_ARG])
    if args not in allowed:
        return ("%s carries the browser arguments %s, not the network block %s%s"
                % (path, json.dumps(args), json.dumps(list(BROWSER_ARGS)), again))
    if cfg.get("pipe") is not True:
        return '%s does not set "pipe": true, so the browser would open a DevTools port%s' % (path, again)
    if cfg.get("headless") not in HEADLESS_MODES:
        return "%s sets headless %s%s" % (path, json.dumps(cfg.get("headless")), again)
    exe = cfg.get("executablePath")
    if not isinstance(exe, str) or not exe:
        return "%s names no browser%s" % (path, again)
    if not os.path.isabs(exe):
        # node runs in the install directory and would read the path from there
        return "%s names the browser by the relative path %s%s" % (path, exe, again)
    if not Path(exe).is_file():
        return "the browser %s is missing" % exe
    return None


def install_problem(renderer: Renderer) -> Optional[str]:
    """Why a renderer's install may not run, or None (TASK R7.9).

    The install home and the install directory must be private (`private_dir_problem`), and the
    install directory must hold PUPPETEER_RC exactly as `setup_renderers.sh` writes it: an empty
    object, at which puppeteer's search for a configuration ends.
    """
    root = Path(renderer.root)
    for d in (root.parent, root):
        problem = private_dir_problem(d)
        if problem:
            return "%s; a renderer runs only from directories no other user may change" % problem
    if _load_puppeteer_config(root / PUPPETEER_RC) != {}:
        return ("%s is not the empty puppeteer configuration setup_renderers.sh writes; run "
                "setup_renderers.sh again" % (root / PUPPETEER_RC))
    return None


def _major(version: str) -> int:
    m = re.match(r"\s*(\d+)", version or "")
    return int(m.group(1)) if m else 0


def _first_line(text: str, limit: int = 300) -> str:
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()[:limit]
    return ""


def _classify_failure(log: str) -> str:
    """'parse_error' | 'render_error' | 'not_rendered' for a failed mmdc run."""
    if _PARSE_FAILURE.search(log or ""):
        return "parse_error"
    if _MERMAID_FRAME.search(log or "") and not _INFRA_FAILURE.search(log or ""):
        return "render_error"
    return "not_rendered"


def _root_attributes(svg_text: str) -> tuple:
    """(aria-roledescription, viewBox width) of the root <svg>, read without a full parse."""
    m = re.search(r"<svg\b[^>]*>", svg_text)
    head = m.group(0) if m else ""
    kind = re.search(r'aria-roledescription="([^"]*)"', head)
    vb = re.search(r'viewBox="([^"]*)"', head)
    width = 0.0
    if vb:
        parts = re.split(r"[\s,]+", vb.group(1).strip())
        if len(parts) == 4:
            try:
                width = float(parts[2])
            except ValueError:
                width = 0.0
    return (kind.group(1) if kind else ""), width


def _kind_of_source(source: str) -> str:
    try:
        return mm.detect_kind(source)[0]
    except Exception:  # noqa: BLE001 - the renderer decides; this only picks a width
        return ""


def fence_sha256(lines: list) -> str:
    """sha256 of fence text given as body *lines* (`mermaid_model.fence_sha256`, TASK R7.8).

    For a Markdown fence the lines are the body as `extract_fences` returns it: the lines between
    the fence lines without the fence's indent, after CRLF and CR line ends become LF. For a
    `.mmd` file they are every line of the file.
    """
    return mm.fence_sha256("\n".join(lines))


def negative_names(body: str) -> Optional[list]:
    """The names a negative fence's marker lists, or None for a positive fence (TASK R9.4).

    The marker is read as the lint reads it (`mermaid_model.Fence.negative`): the last non-blank
    body line `%% negative: <name>, <name>`, with commas between the names.
    """
    marker = mm.Fence(lang="mermaid", start=0, end=0, body=body or "").negative
    return None if marker is None else list(marker.names)


def names_parse_check(names) -> bool:
    """True when a negative marker names a rule or the family of PARSE_FAMILIES, in any case and
    with or without `MA-` (`MA-SYN-01`, `syn`, `MA-PARSE`)."""
    for name in names or []:
        word = name.strip().upper()
        if word.startswith("MA-"):
            word = word[3:]
        if word.split("-")[0] in PARSE_FAMILIES:
            return True
    return False


# ----------------------------------------------------------------------------- renderers


def find_renderers(home: Optional[Path] = None, notation: Optional[dict] = None) -> dict:
    """Return `{tag: Renderer}` for every install whose mermaid version matches its pin.

    An install with a different version is left out and named in the returned dict under the key
    `"_mismatch"` as `{tag: found_version}`, so a caller reports drift instead of a pass. The
    paths are absolute: *home* is resolved.
    """
    home = Path(home).expanduser().resolve() if home is not None else render_home()
    n = notation if notation is not None else mm.load_notation()
    found, mismatch = {}, {}
    for tag, pin in n["renderers"]["installs"].items():
        root = home / tag
        mmdc = root / "node_modules" / ".bin" / "mmdc"
        pp = root / "puppeteer.json"
        version = _package_version(root / "node_modules" / "mermaid" / "package.json")
        if version is None or not mmdc.exists() or not pp.exists():
            continue
        cli = _package_version(root / "node_modules" / "@mermaid-js" / "mermaid-cli" / "package.json") or ""
        if version != pin["mermaid"]:
            mismatch[tag] = version
            continue
        if pin.get("cli") and cli != pin["cli"]:
            mismatch[tag] = "%s with mermaid-cli %s" % (version, cli or "?")
            continue
        cfg = _load_puppeteer_config(pp) or {}
        found[tag] = Renderer(tag=tag, mermaid=version, mmdc=mmdc, puppeteer_config=pp, root=root,
                              cli=cli, browser=str(cfg.get("executablePath") or ""))
    if mismatch:
        found["_mismatch"] = mismatch
    return found


def missing_reason(tag: str, renderers: dict, notation: dict, home: Path) -> str:
    """Why *tag* has no usable renderer, as one line without the tag."""
    pin = notation["renderers"]["installs"].get(tag, {})
    found = renderers.get("_mismatch", {}).get(tag)
    if found:
        return ("mermaid %s installed under %s, pinned %s; run setup_renderers.sh"
                % (found, home / tag, pin.get("mermaid", "?")))
    return ("mermaid %s is not installed under %s; run setup_renderers.sh%s"
            % (pin.get("mermaid", "?"), home / tag,
               " --forward" if tag == notation["renderers"].get("forward") else ""))


def _signal_group(proc, sig) -> None:
    try:
        os.killpg(proc.pid, sig)
    except OSError:
        try:
            proc.send_signal(sig)
        except OSError:
            pass


def _run(cmd: list, timeout: int, cwd: Path) -> tuple:
    """(returncode, stdout, stderr); returncode None when the command could not run or timed out.

    The command runs in *cwd*, the install directory of its renderer: puppeteer reads a
    configuration from its working directory and the parents of it, and runs one written in
    JavaScript, so a command run in the caller's directory would run the file a checked-out
    project holds (TASK R7.9). It runs in its own process group. On a timeout the group gets
    SIGTERM, on which puppeteer closes the browser it started, and SIGKILL TERM_GRACE_S later.
    The browser runs in a group of its own; it talks to puppeteer over the pipe that
    `config_problem` requires, so it exits once the command is gone. Output is decoded as UTF-8
    whatever the locale.
    """
    try:
        proc = subprocess.Popen(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
    except OSError as exc:
        return None, "", str(exc)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _signal_group(proc, signal.SIGTERM)
        try:
            proc.communicate(timeout=TERM_GRACE_S)
        except subprocess.TimeoutExpired:
            _signal_group(proc, signal.SIGKILL)
            proc.communicate()
        return None, "", "timed out after %d s" % timeout
    return (proc.returncode, out.decode("utf-8", errors="replace"),
            err.decode("utf-8", errors="replace"))


def mmdc_command(renderer: Renderer, mmd: Path, svg: Path, config: Path, background: str,
                 theme: Optional[str], width: int) -> list:
    """The mmdc command line of one render. mermaid-cli 12 gets `-t default` for a light render."""
    if theme is None and _major(renderer.cli) >= 12:
        theme = FORWARD_LIGHT_THEME
    cmd = [str(renderer.mmdc), "-q", "-p", str(renderer.puppeteer_config), "-c", str(config),
           "-i", str(mmd), "-o", str(svg), "-b", background]
    if theme:
        cmd += ["-t", theme]
    if _major(renderer.cli) >= 12:
        cmd += ["--size", str(width)]
    else:
        cmd += ["-w", str(width)]
    return cmd


def _mmdc(renderer: Renderer, mmd: Path, svg: Path, config: Path, background: str,
          theme: Optional[str], width: int) -> tuple:
    cmd = mmdc_command(renderer, mmd, svg, config, background, theme, width)
    if svg.exists():
        svg.unlink()
    rc, out, err = _run(cmd, RENDER_TIMEOUT_S, renderer.root)
    return rc, ((err or "") + (out or "")).strip()


def render(source: str, renderer: Renderer, out_base: Path, dark: bool = False,
           notation: Optional[dict] = None) -> RenderResult:
    """Render one figure source to `<out_base>.svg` and `<out_base>.png` and measure its text.

    The metrics carry the contrast of every text, scoped by the colours *source* sets
    (`svg_geometry.author_colours`). A render whose files cannot be written or read is
    `not_rendered`: the disk says nothing about the figure. So is an install that
    `install_problem` or `config_problem` refuses: nothing of it runs.
    """
    n = notation if notation is not None else mm.load_notation()
    out_base = Path(out_base).absolute()  # the node processes run in the install directory

    def result(ok, status, log, **kw):
        return RenderResult(tag=renderer.tag, dark=dark, ok=ok, svg=kw.get("svg"),
                            png=kw.get("png"), log=log, metrics=kw.get("metrics", {}),
                            findings=kw.get("findings", []), status=status,
                            browser=kw.get("browser", ""), measure=kw.get("measure"),
                            font_family=kw.get("font_family", ""), fonts=kw.get("fonts", []))

    problem = install_problem(renderer) or config_problem(renderer)
    if problem:
        return result(False, "not_rendered", problem)
    if shutil.which("node") is None:
        return result(False, "not_rendered", "node is not on PATH")
    try:
        return _render_files(source, renderer, out_base, dark, n, result)
    except OSError as exc:
        return result(False, "not_rendered", "cannot write renders to %s: %s" % (out_base.parent, exc))


def _render_files(source: str, renderer: Renderer, out_base: Path, dark: bool, n: dict,
                  result) -> RenderResult:
    """The body of `render` once the renderer is usable; OSError reaches the caller."""
    out_base.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    mmd = out_base.parent / (out_base.name + ".mmd")
    svg = out_base.parent / (out_base.name + ".svg")
    png = out_base.parent / (out_base.name + ".png")
    measure_path = out_base.parent / (out_base.name + ".measure.json")
    config = out_base.parent / "mermaid-config.json"
    mmd.write_text(source if source.endswith("\n") else source + "\n", encoding="utf-8")
    config.write_text(json.dumps({"securityLevel": n["render"]["security_level"]}) + "\n",
                      encoding="utf-8")
    background = n["renderers"]["dark"]["background"] if dark else "white"
    theme = n["renderers"]["dark"]["theme"] if dark else None
    page_width = n["renderers"]["render_width_px"]
    column = n["column_px"]
    gantt_width = column if _major(renderer.cli) >= 12 else column + MMDC_PAGE_MARGIN_PX
    width = gantt_width if _kind_of_source(source) == "gantt" else page_width
    rc, log = _mmdc(renderer, mmd, svg, config, background, theme, width)
    if rc != 0 or not svg.exists():
        status = "not_rendered" if rc is None else _classify_failure(log)
        return result(False, status, log or "mmdc exited %s" % rc)
    svg_text = svg.read_text(encoding="utf-8")
    kind, drawn_width = _root_attributes(svg_text)
    if kind == "error":
        return result(False, "parse_error", "mermaid drew its syntax-error figure", svg=svg)
    if kind == "gantt" and width != gantt_width and drawn_width >= width - MMDC_PAGE_MARGIN_PX - 1:
        rc, log = _mmdc(renderer, mmd, svg, config, background, theme, gantt_width)
        if rc != 0 or not svg.exists():
            status = "not_rendered" if rc is None else _classify_failure(log)
            return result(False, status, log or "mmdc exited %s" % rc)
        svg_text = svg.read_text(encoding="utf-8")
    if png.exists():
        png.unlink()
    rc, out, err = _run(["node", str(MEASURE_SCRIPT), str(renderer.puppeteer_config), str(svg),
                         "--png", str(png), "--scale", str(PNG_SCALE), "--background", background],
                        MEASURE_TIMEOUT_S, renderer.root)
    if rc != 0:
        return result(False, "not_rendered", "text measurement failed: %s"
                      % (_first_line(err) or "exit %s" % rc), svg=svg)
    try:
        measure = json.loads(out)
    except ValueError:
        return result(False, "not_rendered", "text measurement printed no JSON", svg=svg)
    measure_path.write_text(json.dumps(measure, indent=1, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    try:
        metrics = sg.analyze_svg(svg_text, column, measure, sg.author_colours(source), n)
        findings = sg.evaluate(metrics, n)
    except (ValueError, KeyError) as exc:
        return result(False, "not_rendered", "the SVG could not be analysed: %s" % exc, svg=svg)
    return result(True, "ok", log, svg=svg, png=png if png.exists() else None, metrics=metrics,
                  findings=findings, browser=str(measure.get("browser") or ""),
                  measure=measure_path, font_family=str(measure.get("font_family") or ""),
                  fonts=list(measure.get("fonts") or []))


# ----------------------------------------------------------------------------- checking


def _render_plan(tags: list, dark: bool, notation: dict) -> list:
    """The renders to run, as (tag, dark) pairs: each tag, and the dark render after its tag."""
    plan = [(t, False) for t in tags]
    dark_tag = notation["renderers"]["check_pair"][0]
    if dark and dark_tag in tags:
        plan.insert(tags.index(dark_tag) + 1, (dark_tag, True))
    return plan


def _required_renders(notation: dict) -> list:
    """The renders a complete check needs, as (tag, dark): the check pair and the dark render."""
    pair = list(notation["renderers"]["check_pair"])
    required = [(t, False) for t in pair]
    if notation.get("render", {}).get("dark_default", True):
        required.insert(1, (pair[0], True))
    return required


def _skipped_renders(plan: list, notation: dict) -> list:
    """Required renders the plan leaves out, as (tag, dark, reason) (TASK R7.4, D4)."""
    return [(t, d, "dark render skipped" if d else "%s render skipped" % t)
            for t, d in _required_renders(notation) if (t, d) not in plan]


def _figures_of(path: Path) -> list:
    """The figures of a `.mmd` file or the mermaid fences of a Markdown file.

    Each is a dict: `index` (1-based), `line` (the opening fence line; 0 for a `.mmd` file),
    `end` (the closing fence line; 0 for a `.mmd` file), `body` and `sha256` (fence_sha256).
    A blank `.mmd` file holds no figure.
    """
    text = mm.normalize_text(path.read_text(encoding="utf-8"))
    lines = text.split("\n")
    if path.suffix.lower() == ".mmd":
        own = lines[:-1] if lines and lines[-1] == "" else lines
        body = mm.figure_from_mmd(text).body
        if not body.strip():
            return []
        return [{"index": 1, "line": 0, "end": 0, "body": body, "sha256": fence_sha256(own)}]
    out = []
    for i, f in enumerate(mm.extract_fences(text, ("mermaid",)), 1):
        out.append({"index": i, "line": f.start, "end": f.end, "body": f.body,
                    "sha256": mm.fence_sha256(f.body)})
    return out


def _render_entry(res: RenderResult, renderer: Optional[Renderer], required: bool = True) -> dict:
    return {"tag": res.tag, "dark": res.dark, "required": required, "status": res.status,
            "ok": res.ok, "mermaid": renderer.mermaid if renderer else None,
            "mermaid_cli": renderer.cli if renderer else None,
            "browser": res.browser or None, "font_family": res.font_family or None,
            "fonts": res.fonts,
            "svg": str(res.svg) if res.svg else None, "png": str(res.png) if res.png else None,
            "measure": str(res.measure) if res.measure else None,
            "error": None if res.ok else _first_line(res.log, 600),
            "metrics": res.metrics, "findings": res.findings,
            "pass": bool(res.ok and sg.passes(res.findings))}


def _absent_entry(tag: str, dark: bool, status: str, reason: str, required: bool = True) -> dict:
    return {"tag": tag, "dark": dark, "required": required, "status": status, "ok": False,
            "mermaid": None, "mermaid_cli": None, "browser": None, "font_family": None,
            "fonts": [], "svg": None, "png": None, "measure": None, "error": reason,
            "metrics": {}, "findings": [], "pass": False}


def _render_problem(r: dict) -> Optional[str]:
    """What went wrong in one render entry, in one line, or None for a pass."""
    if r["status"] == "ok":
        if r["pass"]:
            return None
        return "fails " + ", ".join(sorted({f["check"] for f in r["findings"]
                                            if f.get("severity") == "fail"}))
    return "%s: %s" % (r["status"].replace("_", " "), r.get("error") or "")


def failed_checks(r: dict) -> set:
    """The checks with a `fail` finding in one render entry."""
    return {f["check"] for f in r.get("findings") or [] if f.get("severity") == "fail"}


def figure_status(fig: dict) -> str:
    """`pass`, `pass, geometry not checked`, `fail` or `not rendered` for a positive figure;
    `expected`, `broken`, `fail` or `not rendered` for a negative one. Only the required renders
    count; a forward render is information (TASK D3). On a negative figure, sets
    `negative_fired` (the named render checks that fail) and `negative_unexpected` (the failing
    checks it does not name, which fail it as they fail a positive figure)."""
    renders = [r for r in fig["renders"] if r.get("required", True)]
    missing = any(r["status"] in ("not_rendered", "skipped") for r in renders)
    errors = any(r["status"] in ("parse_error", "render_error") for r in renders)
    if not fig.get("negative"):
        if errors or any(r["status"] == "ok" and not r["pass"] for r in renders):
            return "fail"
        if missing:
            return "not rendered"
        unchecked = any(r["status"] == "ok"
                        and (r["metrics"].get("geometry") or "modelled") != "modelled"
                        for r in renders)
        return "pass, geometry not checked" if unchecked else "pass"
    named = fig.get("negative_render_checks") or []
    ran = [r for r in renders if r["status"] == "ok"]
    fired = sorted({c for r in ran for c in named if sg.fired(r["findings"], c)})
    unexpected = sorted({c for r in ran for c in failed_checks(r)} - set(named))
    fig["negative_fired"] = fired
    fig["negative_unexpected"] = unexpected
    if errors and not names_parse_check(fig.get("negative_names")):
        return "fail"  # a figure that does not parse shows no defect the marker names
    if unexpected:
        return "fail"  # a defect the marker does not name
    if fired:
        return "expected"
    if missing:
        return "not rendered"
    return "broken" if named else "expected"


def check_path(path: Path, tags: list, dark: bool, out_dir: Path,
               notation: Optional[dict] = None, renderers: Optional[dict] = None,
               prefix: Optional[str] = None) -> dict:
    """Render and evaluate every figure of *path*. Returns the JSON report the CLI prints.

    Each figure is rendered in every tag of *tags*, plus a dark render of the first tag of the
    check pair when *dark* is set and that tag is requested. A required render left out is
    listed with status `skipped`; any other render (the forward render) carries `required:
    false`, and its problems go to `info`. A file with no mermaid fence is `not rendered`.
    Output files are named `<prefix>-fig<NN>[-L<fence line>]-<tag>[-dark].{mmd,svg,png,measure.json}`
    in *out_dir*.
    """
    n = notation if notation is not None else mm.load_notation()
    home = render_home()
    rs = renderers if renderers is not None else find_renderers(home, n)
    path = Path(path)
    stem = prefix or re.sub(r"[^A-Za-z0-9._-]+", "_", path.stem) or "figure"
    report = {"source": str(path), "figures": [], "not_rendered": [], "info": [],
              "no_fence": False, "status": "pass"}
    try:
        figures = _figures_of(path)
    except Exception as exc:  # noqa: BLE001 - a broken fence reader is a broken instrument
        report["status"] = "not rendered"
        report["not_rendered"].append("%s: the fences could not be read: %s" % (path.name, exc))
        return report
    if not figures:
        report["status"] = "not rendered"
        report["no_fence"] = True
        report["not_rendered"].append(
            ("no mermaid figure found in %s: the file is blank" if path.suffix.lower() == ".mmd"
             else "no mermaid fence found in %s") % path)
        return report
    honoured = mm.negative_allowed(path)
    required = set(_required_renders(n))
    plan = _render_plan(tags, dark, n)
    skipped = _skipped_renders(plan, n)
    for src in figures:
        index, line = src["index"], src["line"]
        names = negative_names(src["body"])
        ignored = []
        if names is not None and not honoured:
            ignored, names = names, None
        fig = {"index": index, "fence_line": line, "fence_end": src["end"],
               "sha256": src["sha256"], "kind": "", "negative": names is not None,
               "negative_names": names or [], "negative_ignored": ignored,
               "negative_render_checks": [x for x in names or [] if x in sg.GATE_CHECKS],
               "negative_fired": [], "negative_unexpected": [], "status": "pass", "renders": []}
        for tag, is_dark in plan:
            needed = (tag, is_dark) in required
            renderer = rs.get(tag)
            if renderer is None:
                fig["renders"].append(_absent_entry(tag, is_dark, "not_rendered",
                                                    missing_reason(tag, rs, n, home), needed))
                continue
            base = Path(out_dir) / ("%s-fig%02d%s-%s%s" % (stem, index, "-L%d" % line if line else "",
                                                            tag, "-dark" if is_dark else ""))
            res = render(src["body"], renderer, base, is_dark, n)
            fig["renders"].append(_render_entry(res, renderer, needed))
            if res.ok and not fig["kind"]:
                fig["kind"] = res.metrics.get("diagram", "")
        for tag, is_dark, reason in skipped:
            fig["renders"].append(_absent_entry(tag, is_dark, "skipped", reason))
        fig["status"] = figure_status(fig)
        ran = [r for r in fig["renders"] if r["mermaid"]]
        fig["renderers"] = {r["tag"] + ("-dark" if r["dark"] else ""):
                            {"mermaid": r["mermaid"], "mermaid_cli": r["mermaid_cli"]} for r in ran}
        fig["browsers"] = sorted({r["browser"] for r in ran if r["browser"]})
        fig["fonts"] = sorted({r["font_family"] for r in ran if r["font_family"]})
        for r in fig["renders"]:
            label = r["tag"] + (" dark" if r["dark"] else "")
            where = "line %d" % line if line else "whole file"
            head = "%s figure %d (%s) %s" % (path.name, index, where, label)
            if r["required"]:
                if r["status"] == "not_rendered":
                    report["not_rendered"].append("%s: %s" % (head, r["error"]))
                continue
            problem = _render_problem(r)
            if problem:
                report["info"].append("%s (forward render, information only): %s" % (head, problem))
        report["figures"].append(fig)
    states = [f["status"] for f in report["figures"]]
    report["status"] = ("fail" if ("fail" in states or "broken" in states) else
                        "not rendered" if ("not rendered" in states or report["not_rendered"]) else
                        "pass, geometry not checked" if "pass, geometry not checked" in states else
                        "pass")
    return report


# ----------------------------------------------------------------------------- fixture


def instrument_sha256(skill_dir: Path = SKILL_DIR) -> str:
    """sha256 over the path and sha256 of each file of INSTRUMENT_FILES, line ends read as LF."""
    h = hashlib.sha256()
    for rel in INSTRUMENT_FILES:
        try:
            data = (Path(skill_dir) / rel).read_bytes().replace(b"\r\n", b"\n")
            digest = hashlib.sha256(data).hexdigest()
        except OSError:
            digest = "absent"
        h.update(("%s\0%s\n" % (rel, digest)).encode("utf-8"))
    return h.hexdigest()


def render_settings(notation: dict) -> dict:
    """The notation values that shaped a render: the fixture test compares them (TASK R9.5).

    The legibility exemptions count: they decide the smallest text the stored metrics hold."""
    r = notation["renderers"]
    exempt = (notation.get("thresholds") or {}).get("legibility_exempt_classes")
    return {"column_px": notation["column_px"], "render_width_px": r["render_width_px"],
            "dark": {"theme": r["dark"]["theme"], "background": r["dark"]["background"]},
            "security_level": notation["render"]["security_level"],
            "legibility_exempt_classes": (sorted(exempt, key=str) if isinstance(exempt, list)
                                          else exempt)}


def _fixture_key(path: Path) -> str:
    p = Path(path).resolve()
    try:
        return p.relative_to(SKILL_DIR).as_posix()
    except ValueError:
        return p.as_posix()


def _portable(text, out_dir: Optional[str]):
    """*text* without the machine's paths: the render directory and the home directory."""
    if not isinstance(text, str):
        return text
    if out_dir:
        text = text.replace(out_dir, "<renders>")
    return text.replace(str(Path.home()), "~")


def fixture_files(report: dict) -> dict:
    """The fixture entries of a report: {file key: {"generated", "instruments", "settings",
    "figures": {fence line: …}}}."""
    out = {}
    for src in report["inputs"]:
        figures = {}
        for fig in src["figures"]:
            renders = {}
            for r in fig["renders"]:
                renders[r["tag"] + ("-dark" if r["dark"] else "")] = {
                    "status": r["status"], "mermaid": r["mermaid"], "mermaid_cli": r["mermaid_cli"],
                    "browser": r["browser"], "font_family": r["font_family"], "pass": r["pass"],
                    "error": _portable(r["error"], report.get("out_dir")),
                    "metrics": r["metrics"], "findings": r["findings"]}
            figures[str(fig["fence_line"])] = {
                "fence_end": fig["fence_end"], "sha256": fig["sha256"], "kind": fig["kind"],
                "negative": fig["negative"], "negative_names": fig["negative_names"],
                "status": fig["status"], "renders": renders}
        out[_fixture_key(Path(src["source"]))] = {"generated": report["generated"],
                                                  "instruments": report["instruments"],
                                                  "settings": report["settings"],
                                                  "figures": figures}
    return out


def dump_json(value, indent: int = 0) -> str:
    """JSON with one line per scalar-only object or array, so a fixture diffs line by line."""
    def leaf(v):
        return not any(isinstance(x, (dict, list)) and x
                       for x in (v.values() if isinstance(v, dict) else v))

    pad, inner = " " * indent, " " * (indent + 1)
    if isinstance(value, dict) and value and not leaf(value):
        items = ["%s%s: %s" % (inner, json.dumps(k, ensure_ascii=False), dump_json(v, indent + 1))
                 for k, v in value.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(value, list) and value and not leaf(value):
        items = [inner + dump_json(v, indent + 1) for v in value]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    return json.dumps(value, ensure_ascii=False)


def _read_fixture(path: Path) -> tuple:
    """(data, None) for a fixture *path* may receive: its JSON object, `{}` when no file exists;
    or (None, why not). A file that exists must already be a render-evidence fixture whose
    `files` member, when present, maps each file to an object: any other JSON file is never
    replaced, and a damaged one is named before the renders run."""
    path = Path(path)
    if not path.exists():
        return {}, None
    if not path.is_file():
        return None, "it is not a file"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, "it does not parse as JSON (%s)" % _first_line(str(exc), 160)
    if not isinstance(data, dict):
        return None, "it holds no JSON object"
    if data.get("schema") != FIXTURE_SCHEMA:
        return None, "its schema is %s, not %s" % (json.dumps(data.get("schema")), FIXTURE_SCHEMA)
    files = data.get("files")
    if files is not None and not (isinstance(files, dict)
                                  and all(isinstance(v, dict) for v in files.values())):
        return None, "its files member is not an object of file entries"
    return data, None


def fixture_target_problem(path: Path) -> Optional[str]:
    """Why *path* may not receive render evidence, or None (`_read_fixture`)."""
    return _read_fixture(path)[1]


def _replace_file(path: Path, text: str) -> Optional[str]:
    """Write *text* to *path* through a temporary file and a rename; return the error, or None.

    An interrupted write leaves the old file whole."""
    try:
        fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=str(path.parent))
    except OSError as exc:
        return str(exc)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        if path.exists():
            shutil.copymode(str(path), tmp)
        else:
            os.chmod(tmp, 0o644)
        os.replace(tmp, str(path))
    except OSError as exc:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        return str(exc)
    return None


def write_fixture(path: Path, report: dict, notation: dict) -> Optional[str]:
    """Merge the report's entries into the fixture at *path*; return why not, or None.

    A file with no mermaid fence gets an entry with no figures. Any other input must have every
    required render; the target must pass `fixture_target_problem` when it is read here, after
    the renders, since it may have changed while they ran.
    """
    incomplete = [f for src in report["inputs"] for f in src["figures"]
                  if any(r["status"] in ("not_rendered", "skipped")
                         for r in f["renders"] if r.get("required", True))]
    unread = [src for src in report["inputs"] if src["not_rendered"] and not src.get("no_fence")]
    if incomplete or unread:
        return "%d figure(s) lack a required render" % max(1, len(incomplete))
    data, problem = _read_fixture(path)
    if problem:
        return "%s; fix or delete it" % problem
    report.setdefault("instruments", instrument_sha256())
    report.setdefault("settings", render_settings(notation))
    files = dict(data.get("files") or {})
    files.update(fixture_files(report))
    fixture = {"schema": FIXTURE_SCHEMA,
               "about": ("Render evidence of every mermaid fence of the files below, keyed by file "
                         "and opening fence line; written by `python3 scripts/render_check.py "
                         "<file> --fixture <this file>` (TASK R7.8, R9.5, A19). Per file it holds "
                         "the sha256 of the instruments and the notation values the renders ran "
                         "with. scripts/tests/test_paired_examples.py recomputes each sha256 from "
                         "the file and evaluates the stored metrics against notation.json without "
                         "node."),
               "files": {k: files[k] for k in sorted(files)}}
    return _replace_file(path, dump_json(fixture) + "\n")


# ----------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="render_check.py",
                                description="Render Mermaid figures in pinned versions and check them.")
    p.add_argument("paths", nargs="*", help=".md or .mmd files")
    p.add_argument("--forward", action="store_true",
                   help="also render with mermaid 12.1.0; information only, it sets no exit code")
    p.add_argument("--no-dark", action="store_true",
                   help="skip the dark render of 11.17.2; the run then exits 2 (not rendered)")
    p.add_argument("--json", action="store_true",
                   help="print the report as JSON and write it as evidence.json next to the renders")
    p.add_argument("--out", help="directory for renders, outside every git work tree (default: a "
                                 "new check-* directory under $MERMAID_RENDER_HOME/renders, of "
                                 "which the newest %d are kept)" % RENDER_KEEP)
    p.add_argument("--versions", help="comma-separated tags to render, e.g. v11,v10")
    p.add_argument("--fixture", metavar="FILE",
                   help="also merge the hash-bound evidence of the inputs into this JSON file, "
                        "which must not exist yet or be a render-evidence fixture")
    return p


def _summary(figures: list, inputs: list) -> dict:
    def count(status):
        return sum(1 for f in figures if f["status"] == status)

    return {"figures": len(figures), "pass": count("pass"),
            "unchecked": count("pass, geometry not checked"), "fail": count("fail"),
            "expected": count("expected"), "broken": count("broken"),
            "not_rendered": count("not rendered"),
            "no_fence": sum(1 for src in inputs if src.get("no_fence"))}


def _text_report(report: dict, out_dir: Optional[Path]) -> list:
    lines = []
    if out_dir is not None:
        lines.append("renders: %s" % out_dir)
    for src in report["inputs"]:
        lines.append("%s: %s" % (src["source"], src["status"].upper()))
        for fig in src["figures"]:
            where = "line %d" % fig["fence_line"] if fig["fence_line"] else "whole file"
            head = "  figure %d (%s, %s): %s" % (fig["index"], where, fig["kind"] or "?",
                                                fig["status"].upper())
            if fig["negative"]:
                head += " (negative: %s" % (", ".join(fig["negative_names"]) or "no name")
                if fig["negative_render_checks"]:
                    head += "; fails %s" % (", ".join(fig["negative_fired"]) or "none of "
                                            + ", ".join(fig["negative_render_checks"]))
                if fig.get("negative_unexpected"):
                    head += "; also fails %s, which it does not name" % ", ".join(
                        fig["negative_unexpected"])
                head += ")"
            if fig.get("negative_ignored"):
                head += (" (negative marker ignored: it counts only in the skill's references/ "
                         "and scripts/tests/fixtures/)")
            lines.append(head)
            for r in fig["renders"]:
                label = "%s%s" % (r["tag"], " dark" if r["dark"] else "")
                aside = "" if r.get("required", True) else "  (forward render, information only)"
                if r["status"] != "ok":
                    lines.append("    %-9s %s: %s%s" % (label, r["status"].replace("_", " "),
                                                        r.get("error") or "", aside))
                    continue
                m = r["metrics"]
                if not r["pass"]:
                    named = set(fig["negative_render_checks"]) if fig["negative"] else set()
                    verdict = "FAIL" if failed_checks(r) - named else "fail, expected"
                elif (m.get("geometry") or "modelled") != "modelled":
                    verdict = "pass, geometry not checked"
                else:
                    verdict = "pass"
                text = "text %.1f px in the column" % float(m.get("effective_font_px") or 0)
                low = float(m.get("smallest_effective_font_px") or 0)
                if 0 < low < float(m.get("effective_font_px") or 0):
                    text += ", smallest %.1f px (%r)" % (low, m.get("smallest_text") or "")
                lines.append("    %-9s mermaid %-7s %s  %.0fx%.0f px, %s, font %s%s"
                             % (label, r["mermaid"], verdict, m.get("width", 0), m.get("height", 0),
                                text, r.get("font_family") or "?", aside))
                for f in r["findings"]:
                    lines.append("      %-4s %s: %s" % (f["severity"], f["check"], f["message"]))
                for w in m.get("warnings") or []:
                    lines.append("      note %s" % w)
                if r.get("png"):
                    lines.append("      png: %s" % r["png"])
    s = report["summary"]
    lines.append("summary: %d figure(s): %d pass, %d pass with geometry not checked, %d fail, "
                 "%d negative as expected, %d broken negative, %d not rendered; %d file(s) "
                 "without a mermaid fence (exit %d)"
                 % (s["figures"], s["pass"], s["unchecked"], s["fail"], s["expected"],
                    s["broken"], s["not_rendered"], s["no_fence"], report["exit"]))
    return lines


def _write_evidence(out_dir: Path, report: dict) -> Optional[str]:
    """Write `evidence.json` into *out_dir*; return the not-rendered reason, or None."""
    try:
        Path(out_dir).mkdir(mode=0o700, parents=True, exist_ok=True)
        (Path(out_dir) / "evidence.json").write_text(
            json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError as exc:
        return "cannot write renders to %s: %s" % (out_dir, exc)
    return None


def _stop_early(report: dict, as_json: bool, reasons: list) -> int:
    """Print a run that rendered nothing: the report (with --json) and its reasons; exit 2."""
    report["exit"] = EXIT_NOT_RENDERED
    if not report["summary"]:
        report["summary"] = _summary([], [])
    if as_json:
        print(json.dumps(report, indent=1, ensure_ascii=False))
    for reason in reasons:
        print("not rendered: %s" % reason, file=sys.stderr if as_json else sys.stdout)
    return EXIT_NOT_RENDERED


def main(argv: Optional[list] = None) -> int:
    p = build_parser()
    try:
        args = p.parse_args(argv)
    except SystemExit as exc:
        return EXIT_PASS if not exc.code else EXIT_USAGE
    if not args.paths:
        p.print_usage(sys.stderr)
        return EXIT_USAGE
    try:
        n = mm.load_notation()
    except (OSError, ValueError) as exc:
        print("render_check.py: cannot read notation.json: %s" % exc, file=sys.stderr)
        return EXIT_NOT_RENDERED
    installs = n["renderers"]["installs"]
    paths = [Path(x) for x in args.paths]
    for path in paths:
        if not path.is_file():
            print("render_check.py: no such file: %s" % path, file=sys.stderr)
            return EXIT_USAGE
        if path.suffix.lower() not in (".md", ".markdown", ".mmd"):
            print("render_check.py: %s is neither .md nor .mmd" % path, file=sys.stderr)
            return EXIT_USAGE
    fixture = None
    if args.fixture:
        fixture = Path(args.fixture).expanduser().absolute()
        if fixture.suffix.lower() != ".json" or not fixture.parent.is_dir():
            print("render_check.py: --fixture %s must be a .json file in an existing directory"
                  % fixture, file=sys.stderr)
            return EXIT_USAGE
        problem = fixture_target_problem(fixture)
        if problem:
            print("render_check.py: --fixture %s: %s; fix or delete it" % (fixture, problem),
                  file=sys.stderr)
            return EXIT_USAGE
    if args.versions:
        tags = [t.strip() for t in args.versions.split(",") if t.strip()]
        unknown = [t for t in tags if t not in installs]
        if not tags or unknown:
            print("render_check.py: unknown version tag(s): %s; known: %s"
                  % (", ".join(unknown) or "(none)", ", ".join(installs)), file=sys.stderr)
            return EXIT_USAGE
    else:
        tags = list(n["renderers"]["check_pair"])
    forward = n["renderers"].get("forward")
    if args.forward and forward and forward not in tags:
        tags.append(forward)
    dark = (not args.no_dark) and bool(n.get("render", {}).get("dark_default", True))
    out_dir = None
    if args.out:
        out_dir = Path(args.out).expanduser().absolute()
        problem = out_dir_problem(out_dir)
        if problem:
            print("render_check.py: --out: %s" % problem, file=sys.stderr)
            return EXIT_USAGE
        problem = private_dir_problem(out_dir)
        if problem:
            print("render_check.py: --out %s: %s; renders are written only where no other user "
                  "may plant a file: pass a directory of your own, such as one `mktemp -d` makes"
                  % (out_dir, problem), file=sys.stderr)
            return EXIT_USAGE
        if inside_git_work_tree(out_dir):
            print("render_check.py: --out %s lies inside a git work tree; renders are written "
                  "outside every repository" % out_dir, file=sys.stderr)
            return EXIT_USAGE
    home = render_home()
    renderers = find_renderers(home, n)
    available = [t for t in tags if t in renderers]
    report = {"tool": "render_check", "schema": "render-check/v2",
              "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "column_px": n["column_px"], "instruments": instrument_sha256(),
              "settings": render_settings(n), "home": str(home), "out_dir": None,
              "renderers": {t: {"mermaid": r.mermaid, "mermaid_cli": r.cli, "browser": r.browser}
                            for t, r in renderers.items() if t in tags},
              "missing": {t: missing_reason(t, renderers, n, home)
                          for t in tags if t not in renderers},
              "skipped": [], "inputs": [], "summary": {}, "exit": EXIT_NOT_RENDERED}
    if not available:
        reasons = ["; ".join("%s: %s" % (t, report["missing"][t]) for t in tags)]
        if args.json and out_dir is not None:
            report["out_dir"] = str(out_dir)
            report["summary"] = _summary([], [])
            problem = _write_evidence(out_dir, report)
            if problem:
                reasons.append(problem)
        return _stop_early(report, args.json, reasons)
    try:
        if out_dir is None:
            base = home / "renders"
            if inside_git_work_tree(base):
                print("render_check.py: %s lies inside a git work tree; set MERMAID_RENDER_HOME "
                      "outside every repository or pass --out" % base, file=sys.stderr)
                return EXIT_USAGE
            base.mkdir(mode=0o700, parents=True, exist_ok=True)
            problem = private_dir_problem(base)
            if problem:
                print("render_check.py: %s; set MERMAID_RENDER_HOME to a directory of your own "
                      "or pass --out" % problem, file=sys.stderr)
                return EXIT_USAGE
            prune_renders(base, RENDER_KEEP - 1)
            out_dir = Path(tempfile.mkdtemp(prefix="check-", dir=str(base)))
        else:
            out_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError as exc:
        where = out_dir if out_dir is not None else home / "renders"
        return _stop_early(report, args.json, ["cannot write renders to %s: %s" % (where, exc)])
    report["out_dir"] = str(out_dir)
    report["skipped"] = [reason for _t, _d, reason in
                         _skipped_renders(_render_plan(tags, dark, n), n)]
    used = {}
    for path in paths:
        stem = re.sub(r"[^A-Za-z0-9._-]+", "_", path.stem) or "figure"
        used[stem] = used.get(stem, 0) + 1
        prefix = stem if used[stem] == 1 else "%s-%d" % (stem, used[stem])
        report["inputs"].append(check_path(path, tags, dark, out_dir, n, renderers, prefix))
    figures = [f for src in report["inputs"] for f in src["figures"]]
    report["summary"] = _summary(figures, report["inputs"])
    not_rendered = [line for src in report["inputs"] for line in src["not_rendered"]]
    not_rendered += report["skipped"]
    info = [line for src in report["inputs"] for line in src.get("info", [])]
    if any(src["status"] == "fail" for src in report["inputs"]):
        code = EXIT_FAIL
    elif not_rendered or any(src["status"] == "not rendered" for src in report["inputs"]):
        code = EXIT_NOT_RENDERED
    else:
        code = EXIT_PASS
    fixture_problem = None
    if fixture is not None:
        fixture_problem = write_fixture(fixture, report, n)
        report["fixture"] = {"path": str(fixture), "written": fixture_problem is None,
                             "problem": fixture_problem}
        if fixture_problem is not None and code == EXIT_PASS:
            code = EXIT_NOT_RENDERED  # the evidence asked for does not exist
    report["exit"] = code
    if args.json:
        problem = _write_evidence(out_dir, report)
        if problem:
            not_rendered.append(problem)
            if code == EXIT_PASS:
                code = EXIT_NOT_RENDERED
            report["exit"] = code
        print(json.dumps(report, indent=1, ensure_ascii=False))
        stream = sys.stderr
    else:
        print("\n".join(_text_report(report, out_dir)))
        stream = sys.stdout
    if fixture is not None:
        print("fixture: %s %s" % (fixture, "written" if fixture_problem is None
                                  else "not written: %s" % fixture_problem), file=stream)
    for line in info:
        print("note: %s" % line, file=stream)
    for line in not_rendered:
        print("not rendered: %s" % line, file=stream)
    return code


if __name__ == "__main__":
    sys.exit(main())
