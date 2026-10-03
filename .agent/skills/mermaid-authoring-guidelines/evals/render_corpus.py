#!/usr/bin/env python3
"""Render every Mermaid figure of an eval campaign and store its render evidence (TASK 108, R11.5).

For each run directory that holds `outputs/answer.md`, the Mermaid fences are read with
`mermaid_model.extract_fences(text, ("mermaid",))`. Figure `fig-N` is the N-th such fence in
document order; `figures_of` is the one place that numbers them. `render_check.render` renders
each figure once per render key of `render_plan`:

  v11        mermaid 11.17.2, light                                   headline
  v11-dark   mermaid 11.17.2, theme `dark` on the dark page colour    headline
  v10        mermaid 10.9.8, light                                    headline
  v12        mermaid 12.1.0, light                                    information only

The keys come from `assets/notation.json`: the tags of `renderers.check_pair`, a dark render of
its first tag (`renderers.dark`), and `renderers.forward`. The result is `outputs/geometry.json`:

  {"fig-1": {"v11": {...}, "v11-dark": {...}, "v10": {...}, "v12": {...}}, "fig-2": {...}}

A run without a Mermaid fence gets `{}`.

A render entry is the evidence of render_check for that render (TASK R7.8), without the local
paths of the renders. A path under the home directory is written `~/...` (`home_relative`), in
`browser_path` and in `log_head`, so a committed entry names no account (SEC2-05):

  render              the render key
  renderer            tag, mermaid and cli versions of the install, their pins, the browser
                      build the text was measured in (`browser`), and the browser executable
                      of the install (`browser_path`)
  dark                True for the dark render
  status              see below
  ok                  True when status is `rendered`
  pass                rendered, and no finding of severity `fail` (`svg_geometry.passes`)
  fence_sha256        `mermaid_model.fence_sha256` of the fence body: its lines as
                      `extract_fences` returns them, each ended by LF, in UTF-8
  fence_line          line of the opening fence in `answer.md`
  metrics             `svg_geometry.analyze_svg` metrics; `metrics.contrast.texts` holds one
                      entry per measured text: text, kind, fg, bg, ratio, scope
  findings            `svg_geometry.evaluate` findings, contrast findings included
  font_family         the font family the browser drew, read from the text measurement
  svg_sha256          sha256 of the SVG; the SVG and PNG files stay outside the repository
  png_sha256          sha256 of the PNG
  instrument_sha256   `instrument_sha256()` of the files that render and measure
  log_head            the first lines of the renderer log of a render that failed
  attempts            renders tried

A field that `render_check.render` returns beyond these is copied under its own name.

`status` of a render entry
  rendered      an SVG of the source's diagram exists; metrics and findings are filled
  parse_error   the renderer refused the source: the figure does not render in that version
  render_error  mermaid failed inside its own code while drawing the figure; it counts as not
                rendering and stays named so that a reviewer reads the log
  infra_error   a timeout, a browser failure or an exception in the render call; never a model
                failure; rendered again by the next invocation
  absent        the information renderer (`v12`) is not installed at its pinned version

Renders (SVG and PNG) are written outside the repository: `--render-dir`, or
`${MERMAID_RENDER_HOME:-~/.cache/mermaid-authoring-guidelines}/renders/corpus/`. A render
directory inside a git work tree is refused; `render_check.inside_git_work_tree` decides, as it
does for every render. Only `geometry.json` lands in the corpus.

Re-entrant: an entry is kept when its fence sha256, dark flag, renderer version, browser
executable (compared as `home_relative` writes it) and instrument hash are unchanged and its
status is `rendered` or `parse_error`;
`--force` renders again. An edit to the render instrument, or another browser, therefore renders
the whole corpus again, so both arms are measured by one instrument (EI-26). The grader refuses
a corpus whose headline renders name more than one browser. CI does not run this script: it
needs node and a browser. The eval selftest replaces `render` with a sentinel.

Exit codes (TASK D20; ARCHITECTURE section 10.5, invariant L6)
  0  every figure has a rendered, parse_error or render_error entry in each headline render
  1  an infra_error remains in a headline render after the retries; run the same command again
  2  not rendered: a headline renderer absent or at another version, or the parse model or the
     render check unavailable; prints `not rendered: <reason>`. Also an interpreter below the
     framework's minimum Python, before any render
  3  usage error

Standard library only.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Optional

# The framework's minimum Python, stated in README §3. Checked before anything is imported from
# this repository or written. Exit 2: this interpreter cannot run the script.
if sys.version_info < (3, 11):
    _name = Path(sys.argv[0] if sys.argv and sys.argv[0].endswith(".py") else __file__).name
    if _name == "__main__.py":  # `python -m <package>`: name this module instead
        _name = Path(__file__).name
    sys.stderr.write(f"not rendered: {_name} needs Python 3.11 or newer (3.14 is the main version); "
                     f"this is Python {sys.version_info[0]}.{sys.version_info[1]}.\n")
    sys.exit(2)

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import mermaid_model as mm  # noqa: E402
import render_check as rc  # noqa: E402
import svg_geometry as sg  # noqa: E402
from render_check import find_renderers, render  # noqa: E402,F401  (module names the selftest replaces)

EXIT_OK, EXIT_INFRA, EXIT_NOT_RENDERED, EXIT_USAGE = 0, 1, 2, 3

STATUSES = ("rendered", "parse_error", "render_error", "infra_error", "absent")
#: Statuses a later invocation keeps when the source, the renderer and the instrument are unchanged.
FINAL = ("rendered", "parse_error")
#: `RenderResult.status` of render_check, mapped to a corpus status.
RENDER_CHECK_STATUS = {"ok": "rendered", "parse_error": "parse_error",
                       "render_error": "render_error", "not_rendered": "infra_error"}
#: Suffix of the render key of a dark render.
DARK_SUFFIX = "-dark"

#: Files whose content decides a render and its measurement; `instrument_sha256` hashes them.
INSTRUMENT_FILES = ("scripts/render_check.py", "scripts/svg_geometry.py",
                    "scripts/measure_text.mjs", "scripts/mermaid_model.py", "assets/notation.json")

#: Fields of `render_check.RenderResult` that `render_one` maps itself; a local path is never stored.
_MAPPED_FIELDS = ("tag", "dark", "ok", "svg", "png", "log", "metrics", "findings", "status",
                  "browser", "measure")

#: What a renderer log says when the SOURCE is at fault. Mermaid's own parser messages.
PARSE_SIGNS = re.compile(r"Parse error|Lexical error|UnknownDiagramError|No diagram type detected"
                         r"|Syntax error in|Expecting '|Unrecognized text", re.I)
#: What a renderer log says when the RENDERER is at fault: node, puppeteer, the browser, the OS.
INFRA_SIGNS = re.compile(r"TimeoutError|timed out|Navigation timeout|Protocol error|Target closed"
                         r"|Session closed|browser has disconnected|Failed to launch"
                         r"|Could not find (?:Chrome|Chromium|expected browser|browser)"
                         r"|ECONNREFUSED|ECONNRESET|socket hang up|ENOMEM|out of memory"
                         r"|SIGKILL|SIGSEGV|spawn \S+ ENOENT", re.I)

LOG_HEAD_LINES = 25


# --------------------------------------------------------------------------- helpers


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path) -> Optional[str]:
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except (OSError, TypeError):
        return None


def fence_sha256(body: str) -> str:
    """The `fence_sha256` of a figure: `mermaid_model.fence_sha256` of its body."""
    return mm.fence_sha256(body)


def instrument_sha256(skill_dir: Path = SKILL_DIR) -> str:
    """sha256 over the path and sha256 of each file of `INSTRUMENT_FILES`, in that order."""
    h = hashlib.sha256()
    for rel in INSTRUMENT_FILES:
        digest = _sha256_file(Path(skill_dir) / rel) or "absent"
        h.update(f"{rel}\0{digest}\n".encode("utf-8"))
    return h.hexdigest()


def _jsonable(value):
    """Turn render results into JSON values: paths and unknown objects become text."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _jsonable(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def home_relative(path) -> Optional[str]:
    """*path* as a committed file writes it: under the user's home directory as `~/...`, by
    exact prefix, so no account name or home layout is published (SEC2-05). Any other path, and
    None, comes back as it is. `grade_figures.home_relative` is the same function."""
    if path is None:
        return None
    text, home = str(path), os.path.expanduser("~").rstrip("/\\")
    if home and text.startswith(home) and text[len(home):][:1] in ("", "/", os.sep):
        return "~" + text[len(home):]
    return text


def _log_head(log) -> str:
    """The first lines of a renderer log, each path under the home directory written `~/...`."""
    head = "\n".join(str(log or "").splitlines()[:LOG_HEAD_LINES])
    home = os.path.expanduser("~").rstrip("/\\")
    if not home:
        return head
    return re.sub(r"(?<![\w.~/-])" + re.escape(home) + r"(?=[/\\])", "~", head)


def figures_of(answer_text: str) -> list:
    """The Mermaid fences of an answer in document order; `fig-N` is item N-1."""
    return list(mm.extract_fences(answer_text, ("mermaid",)))


def render_plan(notation: dict, forward: bool = True) -> list:
    """`[(render key, tag, dark)]` in report order: each tag of the check pair, the dark render
    of the first one directly after it, then the forward tag when *forward* is set."""
    pair = list(notation["renderers"]["check_pair"])
    plan = []
    for i, tag in enumerate(pair):
        plan.append((tag, tag, False))
        if i == 0:
            plan.append((tag + DARK_SUFFIX, tag, True))
    if forward:
        tag = notation["renderers"]["forward"]
        plan.append((tag, tag, False))
    return plan


def headline_keys(notation: dict) -> list:
    """The render keys the headline checks read: the check pair and its dark render."""
    return [key for key, _tag, _dark in render_plan(notation, forward=False)]


def run_dirs(paths) -> list:
    """`(root, run_dir)` for every run directory under *paths* that holds `outputs/answer.md`."""
    found = []
    for root in paths:
        root = Path(root)
        if (root / "outputs" / "answer.md").is_file():
            found.append((root.parent, root))
            continue
        for answer in sorted(root.rglob("answer.md")):
            if answer.parent.name != "outputs":
                continue
            rd = answer.parent.parent
            if any(part.startswith(".partial-") for part in rd.parts):
                continue
            found.append((root, rd))
    seen, out = set(), []
    for root, rd in found:
        key = rd.resolve()
        if key not in seen:
            seen.add(key)
            out.append((root, rd))
    return out


def classify(result) -> str:
    """Corpus status of one `RenderResult`: rendered, parse_error, render_error or infra_error.

    A status of `STATUSES` wins. A render_check status maps through `RENDER_CHECK_STATUS`; its
    `ok` becomes `parse_error` when the SVG is Mermaid's error graphic. Without a known status:
    an error graphic or a log with a parser message is `parse_error`; a log naming a timeout or
    a browser failure is `infra_error`; any other failure is `render_error`.
    """
    explicit = getattr(result, "status", None)
    metrics = getattr(result, "metrics", None) or {}
    error_graphic = str(metrics.get("diagram", "")).lower() == "error"
    if explicit in STATUSES:
        return explicit
    if explicit in RENDER_CHECK_STATUS:
        status = RENDER_CHECK_STATUS[explicit]
        return "parse_error" if status == "rendered" and error_graphic else status
    log = str(getattr(result, "log", "") or "")
    if getattr(result, "ok", False):
        return "parse_error" if error_graphic else "rendered"
    if PARSE_SIGNS.search(log):
        return "parse_error"
    if INFRA_SIGNS.search(log):
        return "infra_error"
    return "render_error"


# --------------------------------------------------------------------------- rendering


def _renderer_info(tag: str, renderer, notation: dict, browser: str = "") -> dict:
    pin = notation["renderers"]["installs"].get(tag, {})
    return {"tag": tag,
            "mermaid": getattr(renderer, "mermaid", None) if renderer else None,
            "cli": (getattr(renderer, "cli", "") or None) if renderer else None,
            "pinned_mermaid": pin.get("mermaid"), "pinned_cli": pin.get("cli"),
            "browser": browser or None,
            "browser_path": home_relative(_browser_path(renderer))}


def _browser_path(renderer) -> Optional[str]:
    """The browser executable of an install, or None."""
    return (getattr(renderer, "browser", "") or None) if renderer else None


def _base_entry(key: str, tag: str, dark: bool, renderer, notation: dict, source: str,
                instrument: str, status: str, attempts: int) -> dict:
    return {"render": key, "renderer": _renderer_info(tag, renderer, notation), "dark": dark,
            "status": status, "ok": status == "rendered", "pass": False,
            "fence_sha256": fence_sha256(source), "fence_line": None, "metrics": {},
            "findings": [], "font_family": None, "svg_sha256": None, "png_sha256": None,
            "instrument_sha256": instrument, "log_head": "", "attempts": attempts}


def _result_fields(result) -> dict:
    """Fields of a render result beyond `_MAPPED_FIELDS`, without local paths."""
    if dataclasses.is_dataclass(result) and not isinstance(result, type):
        fields = {f.name: getattr(result, f.name) for f in dataclasses.fields(result)}
    else:
        fields = dict(getattr(result, "__dict__", {}) or {})
    return {k: v for k, v in fields.items()
            if k not in _MAPPED_FIELDS and not k.startswith("_") and not isinstance(v, Path)}


def _font_family(result) -> Optional[str]:
    """The font family the browser drew, from the measurement file render_check wrote."""
    path = getattr(result, "measure", None)
    if not path:
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            family = json.load(fh).get("font_family")
    except (OSError, ValueError, AttributeError):
        return None
    return family if isinstance(family, str) and family else None


def render_one(source: str, key: str, tag: str, dark: bool, renderer, out_base: Path,
               notation: dict, retries: int, instrument: str) -> dict:
    """Render one figure for one render key; retry infra and unexplained failures."""
    out_base.parent.mkdir(parents=True, exist_ok=True)
    attempts, status, result, error = 0, "infra_error", None, ""
    for _ in range(1 + max(0, retries)):
        attempts += 1
        try:
            result = render(source, renderer, out_base, dark=dark, notation=notation)
            status = classify(result)
            error = ""
        except NotImplementedError:
            raise
        except Exception as exc:  # the renderer call itself failed: infrastructure
            result, status, error = None, "infra_error", f"{type(exc).__name__}: {exc}"
        if status in ("rendered", "parse_error"):
            break
    entry = _base_entry(key, tag, dark, renderer, notation, source, instrument, status, attempts)
    if result is None:
        entry["log_head"] = _log_head(error)
        return entry
    entry["renderer"]["browser"] = getattr(result, "browser", "") or None
    if status == "rendered":
        findings = _jsonable(getattr(result, "findings", []) or [])
        entry["metrics"] = _jsonable(getattr(result, "metrics", {}) or {})
        entry["findings"] = findings
        entry["pass"] = sg.passes(findings)
        entry["font_family"] = _font_family(result)
        entry["svg_sha256"] = _sha256_file(getattr(result, "svg", None))
        entry["png_sha256"] = _sha256_file(getattr(result, "png", None))
    else:
        entry["log_head"] = _log_head(getattr(result, "log", ""))
    for name, value in _result_fields(result).items():
        value = _jsonable(value)
        if name not in entry:
            entry[name] = value
        elif entry[name] != value:
            entry[f"render_check_{name}"] = value
    return entry


def absent_entry(key: str, tag: str, dark: bool, reason: str, source: str, notation: dict,
                 instrument: str) -> dict:
    entry = _base_entry(key, tag, dark, None, notation, source, instrument, "absent", 0)
    entry["log_head"] = reason
    return entry


def _reusable(entry, fence_sha: str, dark: bool, renderer, instrument: str) -> bool:
    """An entry kept from an earlier invocation: the same source, dark flag, instrument, mermaid
    and browser executable. A browser update changes text widths, so it renders again (EI-26).
    The executable is compared as `home_relative` writes it, whichever form the entry holds."""
    if not isinstance(entry, dict):
        return False
    got = entry.get("renderer") or {}
    return (entry.get("status") in FINAL
            and entry.get("fence_sha256") == fence_sha
            and bool(entry.get("dark")) == dark
            and entry.get("instrument_sha256") == instrument
            and got.get("mermaid") == getattr(renderer, "mermaid", None)
            and home_relative(got.get("browser_path")) == home_relative(_browser_path(renderer)))


def process_run(root: Path, rd: Path, plan: list, renderers: dict, absent: dict, notation: dict,
                render_root: Path, force: bool, retries: int, jobs: int, instrument: str,
                all_keys: Optional[list] = None) -> dict:
    """Render the figures of one run for every render key of *plan*; write `geometry.json`.

    *plan* is `render_plan(...)`. An entry of a render key outside *plan* stays when its fence
    is unchanged; *all_keys* gives the key order of the file. Returns counts per `<key>:<status>`.
    """
    answer = (rd / "outputs" / "answer.md").read_text(encoding="utf-8")
    fences = figures_of(answer)
    path = rd / "outputs" / "geometry.json"
    old = {}
    if path.is_file():
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old = {}
    if not isinstance(old, dict):
        old = {}
    try:
        rel = rd.resolve().relative_to(root.resolve())
    except ValueError:
        rel = Path(rd.name)
    base = render_root / root.resolve().name / rel
    geometry, tasks, counts = {}, [], {"figures": len(fences), "reused": 0}
    for n, fence in enumerate(fences, 1):
        fig = f"fig-{n}"
        source = fence.body
        sha = fence_sha256(source)
        prior_fig = old.get(fig) if isinstance(old.get(fig), dict) else {}
        geometry[fig] = {}
        for key, tag, dark in plan:
            prior = prior_fig.get(key)
            if tag in absent:
                kept = (isinstance(prior, dict) and prior.get("status") in FINAL
                        and prior.get("fence_sha256") == sha
                        and prior.get("instrument_sha256") == instrument)
                geometry[fig][key] = prior if kept else absent_entry(
                    key, tag, dark, absent[tag], source, notation, instrument)
            elif not force and _reusable(prior, sha, dark, renderers[tag], instrument):
                geometry[fig][key] = prior
                counts["reused"] += 1
            else:
                tasks.append((fig, key, tag, dark, source, base / f"{fig}-{key}" / f"{fig}-{key}"))
            if key in geometry[fig]:
                geometry[fig][key]["fence_line"] = fence.start
    if tasks:
        def work(task):
            fig, key, tag, dark, source, out_base = task
            return fig, key, render_one(source, key, tag, dark, renderers[tag], out_base,
                                        notation, retries, instrument)
        if jobs > 1:
            with concurrent.futures.ThreadPoolExecutor(jobs) as pool:
                done = list(pool.map(work, tasks))
        else:
            done = [work(t) for t in tasks]
        for fig, key, entry in done:
            entry["fence_line"] = fences[int(fig.split("-")[1]) - 1].start
            geometry[fig][key] = entry
    plan_keys = [key for key, _tag, _dark in plan]
    order = list(dict.fromkeys(list(all_keys or plan_keys) + plan_keys))
    for n, fence in enumerate(fences, 1):  # a key this call skipped keeps its earlier entry
        fig = f"fig-{n}"
        prior_fig = old.get(fig) if isinstance(old.get(fig), dict) else {}
        for key, entry in prior_fig.items():
            if (key not in geometry[fig] and isinstance(entry, dict)
                    and entry.get("fence_sha256") == fence_sha256(fence.body)):
                geometry[fig][key] = entry
        extra = [k for k in geometry[fig] if k not in order]
        geometry[fig] = {key: geometry[fig][key] for key in order + extra if key in geometry[fig]}
    tmp = path.with_name(f"geometry.json.tmp.{os.getpid()}")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(geometry, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, path)
    for fig in geometry.values():
        for key, entry in fig.items():
            name = f"{key}:{entry.get('status')}"
            counts[name] = counts.get(name, 0) + 1
    return counts


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="render_corpus.py",
        description="Render the Mermaid figures of an eval campaign in 11.17.2, a dark 11.17.2, "
                    "10.9.8 and 12.1.0; write outputs/geometry.json")
    p.add_argument("paths", nargs="+", help="campaign directories, eval directories or run dirs")
    p.add_argument("--no-forward", action="store_true",
                   help="skip the information render in mermaid 12.1.0")
    p.add_argument("--render-dir", help="directory for SVG and PNG renders, outside any git "
                                        "work tree (default: under MERMAID_RENDER_HOME)")
    p.add_argument("--force", action="store_true", help="render again what geometry.json holds")
    p.add_argument("--retries", type=int, default=1,
                   help="further renders after an infra or unexplained failure (default 1)")
    p.add_argument("--jobs", type=int, default=1, help="concurrent renders per run (default 1)")
    p.add_argument("--dry-run", action="store_true",
                   help="list the runs, figures and render keys; render nothing")
    return p


def _not_rendered(reason: str) -> int:
    print(f"not rendered: {reason}")
    return EXIT_NOT_RENDERED


def main(argv: Optional[list] = None) -> int:
    p = build_parser()
    try:
        args = p.parse_args(argv)
    except SystemExit as exc:
        return EXIT_OK if not exc.code else EXIT_USAGE
    missing = [x for x in args.paths if not Path(x).exists()]
    if missing:
        print(f"usage error: no such path: {', '.join(missing)}", file=sys.stderr)
        return EXIT_USAGE
    if args.retries < 0 or args.jobs < 1:
        print("usage error: --retries must be 0 or more and --jobs at least 1", file=sys.stderr)
        return EXIT_USAGE
    notation = mm.load_notation()
    pair = list(notation["renderers"]["check_pair"])
    forward = notation["renderers"]["forward"]
    plan = render_plan(notation, forward=not args.no_forward)
    all_keys = [key for key, _tag, _dark in render_plan(notation, forward=True)]
    headline = headline_keys(notation)

    runs = run_dirs(args.paths)
    try:
        if args.dry_run:
            total = 0
            for _root, rd in runs:
                n = len(figures_of((rd / "outputs" / "answer.md").read_text(encoding="utf-8")))
                total += n
                print(f"{rd}: {n} figure(s)")
            print(f"{len(runs)} run(s), {total} figure(s), renders "
                  f"{', '.join(k for k, _t, _d in plan)}; nothing rendered")
            return EXIT_OK
    except NotImplementedError:
        return _not_rendered("mermaid_model.extract_fences is not implemented")

    render_root = Path(args.render_dir) if args.render_dir else (
        rc.render_home() / "renders" / "corpus")
    render_root = render_root.expanduser().resolve()   # the directory the check vetted
    if rc.inside_git_work_tree(render_root):            # one check for every render (SEC-04)
        print(f"usage error: {render_root} lies inside a git work tree; renders stay outside "
              f"the repository", file=sys.stderr)
        return EXIT_USAGE

    try:
        found = find_renderers(notation=notation)
    except NotImplementedError:
        return _not_rendered("render_check.find_renderers is not implemented")
    except Exception as exc:
        return _not_rendered(f"render_check.find_renderers failed: {type(exc).__name__}: {exc}")
    mismatch = dict(found.get("_mismatch") or {})
    renderers = {t: r for t, r in found.items() if not t.startswith("_")}
    reasons = []
    for tag in pair:
        want = notation["renderers"]["installs"][tag]["mermaid"]
        if tag in mismatch:
            reasons.append(f"{tag} is mermaid {mismatch[tag]}, pinned {want}")
        elif tag not in renderers:
            reasons.append(f"{tag} (mermaid {want}) is not installed; run scripts/setup_renderers.sh")
    if reasons:
        return _not_rendered("; ".join(reasons))
    absent = {}
    if not args.no_forward and forward not in renderers:
        want = notation["renderers"]["installs"][forward]["mermaid"]
        absent[forward] = (f"{forward} is mermaid {mismatch[forward]}, pinned {want}"
                           if forward in mismatch else f"{forward} (mermaid {want}) is not installed")
        print(f"information render skipped: {absent[forward]}")
    for tag in dict.fromkeys(t for _k, t, _d in plan):
        if tag in renderers:
            print(f"{tag}: mermaid {getattr(renderers[tag], 'mermaid', '?')}")
    instrument = instrument_sha256()
    print(f"instrument sha256 {instrument}")

    totals = {}
    try:
        for root, rd in runs:
            counts = process_run(root, rd, plan, renderers, absent, notation, render_root,
                                 args.force, args.retries, args.jobs, instrument, all_keys)
            for k, v in counts.items():
                totals[k] = totals.get(k, 0) + v
            print(f"{rd}: {counts['figures']} figure(s), {counts['reused']} entry(ies) kept")
    except NotImplementedError as exc:
        return _not_rendered(f"a parse or render function is not implemented ({exc!r})")
    summary = ", ".join(f"{k} {v}" for k, v in sorted(totals.items()))
    print(f"{len(runs)} run(s): {summary or 'no figure'}")
    infra = sum(v for k, v in totals.items()
                if k.endswith(":infra_error") and k.rsplit(":", 1)[0] in headline)
    if infra:
        print(f"{infra} headline render(s) failed on infrastructure; run the same command again")
        return EXIT_INFRA
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
