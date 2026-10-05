#!/usr/bin/env python3
"""Plan chart generator: a dependency schedule drawn as a Mermaid gantt (TASK 108, R8).

The chart is a critical-path early-start schedule with no calendar. One estimate hour is drawn as
one millisecond (`dateFormat x`, durations `Nms`, `axisFormat %Q`). Each bar starts at a numeric
start the script computes; the block never uses `after`, because mermaid drops an `after`
dependency declared below the dependent task without a diagnostic. Sections are stages, statuses
are `done` / `active` / plain, and `crit` marks the critical path the script computes.

Inputs (TASK R8.1, D19)
  * a JSON file: {"schema": "plan-schedule/v1", "tasks": [{"id", "title", "stage", "est", "deps"}]}
    `est` is an integer number of hours; `deps` a list of task ids; `status` is optional:
    "done" | "in-progress" | "not-started". A task without `status` is not started.
  * a Markdown plan holding exactly one JSON block of the same schema, `status` optional there
    too, in the fenced block that follows the anchor `<!-- contract:schedule -->`. The framework's
    plan template writes `not-started`, and the develop workflows set the status (TASK 110 R8).
    The prose of the plan is never parsed, so a plan in
    any language yields the same chart (ARCHITECTURE invariant L1).

Output (TASK R8.3, R8.5, research r4 §4.6-4.8)
  A caption, the mermaid fence, a one-line legend, the ready-to-start list and the critical-path
  line. The settings line is `settings.gantt` of `assets/notation.json`, its `useWidth` and
  `themeCSS` included, with the computed `leftPadding`, `rightPadding` and, above 30 bars,
  `topAxis` merged into its `gantt` object. Every key and value of the merged line is checked
  against mermaid's directive sanitizer before the line is written.
  `--write` puts the block between `<!-- generated:plan-gantt-start -->` and
  `<!-- generated:plan-gantt-end -->`; `--check` compares that region with what `--write` would
  put there, and writes nothing. A plan of fewer than MIN_TASKS tasks gets an empty region:
  `--write` empties it and prints the reason on stderr, and `--check` passes on a region that
  holds blank lines only. Without `--write` and `--check`, the chart is printed wrapped in the
  markers, for a plan of any size. Only the region changes; every other line keeps its bytes,
  its line end included. Every mode draws the charts before it reads the document, a small plan
  included. A check of the plan or of the settings line therefore gives one exit code in all
  three modes.

Stage groups (TASK R8.6, UC-2 A3)
  `--stages A,B --stages C` draws one chart per group. The groups name every stage exactly once.
  A split region opens with `<!-- plan-gantt-groups: [["A", "B"], ["C"]] -->`, and a `--write`
  or `--check` without `--stages` reuses that line, so the plain commands keep a split chart
  current. A new `--stages` replaces it; one group of every stage gives one chart and no line.

Markers (TASK R8.4)
  The scan for the markers stops at the first line that is either marker, so two start markers
  and one end marker are an error, not a pair. Markers and the schedule anchor inside fenced or
  indented code, as CommonMark reads it (`mermaid_model.code_line_reader`), are text. A region
  that holds a heading, an HTML comment other than the stored groups, or a fence other than
  `mermaid` holds document text that a lost marker let in: it is refused, and nothing is written.

Exit codes (TASK D20, ARCHITECTURE §7.4)
  0  ok
  1  `--check` found the region stale, or the plan is invalid: cycle, unknown dependency,
     duplicate id, non-integer estimate, unknown status, no schedule block, missing markers, a
     region that holds document text, stage groups that leave out or repeat a stage, or a hard
     budget exceeded under `--strict`; the message names which
  2  instrument broken: an internal error, or a `notation.json` setting that mermaid would drop
     or alter
  3  usage error: bad arguments, `--write` with `--check`, an unreadable plan or document, a
     document that cannot be written or is read-only, an unknown stage in `--stages`

It needs the standard library only, on the framework's minimum Python (README §3). No output
depends on the interpreter's Unicode version: the text cleaning and the width estimate use fixed
character tables.
"""

from __future__ import annotations

import argparse
import errno
import heapq
import json
import math
import os
import re
import shlex
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mermaid_model as mm  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parent.parent
NOTATION_PATH = SKILL_DIR / "assets" / "notation.json"

EXIT_OK, EXIT_FAIL, EXIT_INTERNAL, EXIT_USAGE = 0, 1, 2, 3
SCHEDULE_ANCHOR = "<!-- contract:schedule -->"
SCHEMA = "plan-schedule/v1"

MARKER_START = "<!-- generated:plan-gantt-start -->"
MARKER_END = "<!-- generated:plan-gantt-end -->"
#: The first line of a split region: the stage groups as JSON, between these two strings.
GROUPS_PREFIX, GROUPS_SUFFIX = "<!-- plan-gantt-groups: ", " -->"
_GROUPS_LINE_RE = re.compile(re.escape(GROUPS_PREFIX) + r"(.*)" + re.escape(GROUPS_SUFFIX))
#: Escaped in the stored groups: `<` and `>` would open a tag or end the comment early, and the
#: others would split the line. JSON reads each `\uXXXX` back.
_GROUPS_ESCAPE_RE = re.compile("[<>\x7f-\x9f\u2028\u2029\ud800-\udfff]")
#: A plan of fewer tasks gets no chart: the region between the markers stays empty (TASK R8.5).
MIN_TASKS = 8

STATUSES = ("done", "in-progress", "not-started")
TOP_KEYS = ("schema", "tasks")
TASK_KEYS = ("id", "title", "stage", "est", "deps")
TASK_KEYS_OPTIONAL = ("status",)

#: Matched whole (`fullmatch`): `$` alone also matches before a final line break.
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
#: Words that open a gantt statement. The gantt lexer is case-insensitive, and a bar label starts
#: with the task id, so a task id equal to one of them turns the task line into that statement.
GANTT_KEYWORDS = frozenset({
    "gantt", "title", "section", "dateformat", "axisformat", "tickinterval", "todaymarker",
    "excludes", "includes", "weekday", "weekend", "topaxis", "inclusiveenddates", "click",
    "call", "href", "acctitle", "accdescr", "accdescription",
})
#: Three of them need only a word boundary after them (`gantt\b`, `topAxis\b`,
#: `inclusiveEndDates\b` in the lexers of 10.9.8, 11.17.2 and 12.1.0), so `gantt-1` opens one too.
GANTT_KEYWORD_PREFIX_RE = re.compile(r"(?:gantt|topaxis|inclusiveenddates)\b", re.I | re.A)
#: The gantt lexer reads a leading `YYYY-MM-DD` as a date token.
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")

# Fixed character tables. `unicodedata` answers by the interpreter's Unicode version, so a code
# point that one Python knows and another does not would give two charts for one plan.
#: Characters that split a line or reorder the text around them: C0 and C1 controls, the line
#: and paragraph separators, the bidi controls and lone surrogates.
_CONTROL_RE = re.compile("[\x00-\x1f\x7f-\x9f\u061c\u200e\u200f\u2028\u2029\u202a-\u202e"
                         "\u2066-\u2069\ud800-\udfff]")
#: Characters that draw no glyph: Unicode's Default_Ignorable_Code_Point set.
_INVISIBLE_RE = re.compile("[\u00ad\u034f\u061c\u115f\u1160\u17b4\u17b5\u180b-\u180f"
                           "\u200b-\u200f\u202a-\u202e\u2060-\u206f\u3164\ufe00-\ufe0f\ufeff"
                           "\uffa0\ufff0-\ufff8\U0001bca0-\U0001bca3\U0001d173-\U0001d17a"
                           "\U000e0000-\U000e0fff]")
#: Combining marks that draw over the character before them.
_COMBINING_RANGES = ((0x0300, 0x036F), (0x0483, 0x0489), (0x1AB0, 0x1AFF), (0x1DC0, 0x1DFF),
                     (0x20D0, 0x20FF), (0xFE20, 0xFE2F))
#: East Asian wide and fullwidth blocks, and the pictographs from U+1F000, drawn about 1 em wide.
_WIDE_RANGES = ((0x1100, 0x115F), (0x2E80, 0x303E), (0x3041, 0x33FF), (0x3400, 0x4DBF),
                (0x4E00, 0x9FFF), (0xA000, 0xA4CF), (0xA960, 0xA97F), (0xAC00, 0xD7A3),
                (0xF900, 0xFAFF), (0xFE10, 0xFE19), (0xFE30, 0xFE6F), (0xFF00, 0xFF60),
                (0xFFE0, 0xFFE6), (0x1F000, 0x1FAFF), (0x20000, 0x3FFFD))
#: A `themeVariables` value mermaid keeps; any other value is blanked (renderer fact X1).
#: Matched whole, as the JavaScript `$` matches only at the end.
THEME_VALUE_RE = re.compile(r'^[\d "#%(),.;A-Za-z]+$')

# The directive sanitizer of mermaid 10.9.8, 11.17.2 and 12.1.0 (read in their bundles on
# 2026-10-02). `sanitizeDirective` deletes a key that starts with `__`, holds `proto` or `constr`,
# or is not a configuration key, and a null value; it blanks a `themeVariables` value outside
# THEME_VALUE_RE and replaces CSS whose braces do not balance. Config `sanitize` deletes a string
# that holds `<`, `>` or `url(data:`. The directive scanner reads every `'` as `"`, a `}%%` ends
# the directive, and `%%` opens a comment elsewhere in a figure.
#: Top-level keys the gantt settings line may hold.
SETTINGS_TOP_KEYS = frozenset({"themeVariables", "themeCSS", "gantt", "look"})
#: The gantt configuration keys of the three versions (`defaultConfig.gantt`, `tickInterval` and
#: `useWidth` included); any other key under `gantt` is deleted without a diagnostic.
GANTT_CONFIG_KEYS = frozenset({
    "useMaxWidth", "titleTopMargin", "barHeight", "barGap", "topPadding", "rightPadding",
    "leftPadding", "gridLineStartPadding", "fontSize", "sectionFontSize", "numberSectionStyles",
    "axisFormat", "topAxis", "displayMode", "weekday", "tickInterval", "useWidth",
})
#: Text that makes mermaid delete or reread a string value of the settings line.
UNSAFE_SETTING_TEXT = ("<", ">", "url(data:", "'", "%%")
#: A key whose value mermaid sanitizes as CSS (`key.includes(...)`, as mermaid tests it).
CSS_KEY_PARTS = ("themeCSS", "fontFamily", "altFontFamily")

# Layout (research r4 §4.8). Text width is estimated from characters, never measured, so the
# script needs no browser and gives one result for one input on every machine.
CHAR_EM = 0.6  # average glyph width in em; measured 0.48-0.51 em for mermaid's default font stack
WIDE_CHAR_EM = 1.0  # East Asian wide and fullwidth characters
TITLE_MARGIN_PX = 24  # mermaid draws a section title from x = 10; 14 px keep it off the first bar
LEFT_MIN_PX, LEFT_MAX_PX = 140, 300
SECTION_LINES_MAX = 2
RIGHT_EDGE_MIN_PX = 20  # the time area ends at least this far from the right edge
AREA_MIN_SHARE = 0.35  # below this share of the width the labels yield, not the time area
LABEL_SIDE_FACTOR = 1.5  # mermaid draws a label right of its bar iff end + width + 1.5 * left <= W
TICKS_MAX = 10  # E4
TOP_AXIS_ABOVE_BARS = 30  # E5
MIN_BAR_PX = 6
ELLIPSIS = "…"

#: Fixed strings of the block. Task titles and stage names are never translated.
TEXT = {
    "caption_title": "Plan chart",
    "caption_title_stages": "Plan chart: {stages}",
    "caption": "Each bar starts when its last dependency ends and lasts its estimate; the axis "
               "counts estimate hours from the start, not dates.",
    "caption_stages": "Each bar starts when its last dependency ends and lasts its estimate; the "
                      "axis counts estimate hours from the start of the whole plan, not dates.",
    "legend": "Legend: {items}.",
    "legend_done": "green fill — done",
    "legend_active": "amber fill — in progress",
    "legend_waiting": "white fill — not started",
    "legend_crit": "red border — critical path",
    "ready_head": "Ready to start — every dependency done:",
    "ready_none": "Ready to start: none.",
    "ready_item": "- **{id}** {title} — {est} h, {where}",
    "on_cp": "critical path",
    "slack": "slack {s} h",
    "in_progress": "in progress",
    "cp": "Critical path — {h} h by estimates: {chain}.",
    "cp_status": "Critical path — {h} h by estimates, {done} of {n} tasks done, "
                 "{rem} h remaining: {chain}.",
    "cp_also": " Also at zero slack: {ids}.",
}


class PlanError(ValueError):
    """Invalid plan input; the CLI maps it to exit 1 with the message."""


class UsageError(Exception):
    """The invocation is wrong: an unreadable path, a document that cannot be written, or an
    unknown stage. The CLI exits 3."""


@dataclass
class Task:
    id: str
    title: str
    stage: str
    est: int
    deps: list = field(default_factory=list)
    status: str = "not-started"


@dataclass
class Schedule:
    es: dict  # id -> earliest start (hours)
    ef: dict  # id -> earliest finish (hours)
    critical: list  # ids on the critical path, in order
    ready: list  # ids whose dependencies are all done and which are not done themselves
    span: int  # hours from the first start to the last finish
    slack: dict = field(default_factory=dict)  # id -> total float (hours); 0 on a longest path


@dataclass
class Rendered:
    """The charts with the ready list and the critical-path line, the warnings for stderr and the
    bar count of each chart. `region_block` adds the stored stage groups of a split chart."""

    text: str
    warnings: list
    bars: list


# --------------------------------------------------------------------------- input


def load_notation(path: Optional[Path] = None) -> dict:
    """Return `assets/notation.json`, the single source of budgets, label limits and settings."""
    with open(path or NOTATION_PATH, encoding="utf-8") as fh:
        return json.load(fh)


_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")


def _fence_open(line: str):
    """Return `(char, length, info)` when *line* opens a fenced code block, else None."""
    m = _FENCE_OPEN_RE.match(line)
    if not m:
        return None
    marker, info = m.group(1), m.group(2)
    if marker[0] == "`" and "`" in info:  # CommonMark: no backtick in a backtick fence's info
        return None
    return marker[0], len(marker), info.strip()


def _fence_closes(line: str, fence) -> bool:
    m = _FENCE_CLOSE_RE.match(line)
    return bool(m) and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1]


def _scan(lines: list):
    """Return `(anchors, starts, ends)`: line indexes of the schedule anchor and of the two
    markers, counted outside fenced and indented code as CommonMark reads them
    (`mermaid_model.code_line_reader`): an example of the markers indented 4 columns is text.

    The text between a start marker and the end marker that follows it is script output; it is
    skipped, and the scan starts afresh after it, so a damaged block cannot hide the lines that
    follow it. The look-ahead stops at the first line that is either marker: a start marker
    whose next marker is another start marker, or that has none, skips nothing, so a lost end
    marker never pairs a start marker with a later one.
    """
    anchors, starts, ends = [], [], []
    code = mm.code_line_reader(lines)
    i, n = 0, len(lines)
    while i < n:
        if code(i):
            i += 1
            continue
        s = lines[i].strip()
        if s == MARKER_START:
            starts.append(i)
            j = next((k for k in range(i + 1, n)
                      if lines[k].strip() in (MARKER_START, MARKER_END)), None)
            if j is not None and lines[j].strip() == MARKER_END:
                ends.append(j)
                i = j
                code = mm.code_line_reader(lines)
            i += 1
            continue
        if s == MARKER_END:
            ends.append(i)
        elif s == SCHEDULE_ANCHOR:
            anchors.append(i)
        i += 1
    return anchors, starts, ends


def _parse_json(text: str, first_line: int = 1):
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise PlanError(f"line {first_line + exc.lineno - 1}, column {exc.colno}: the schedule "
                        f"is not valid JSON: {exc.msg}") from None


def _markdown_schedule(text: str):
    """Return the parsed JSON of the one fenced block that follows the schedule anchor."""
    lines = text.split("\n")
    anchors, _, _ = _scan(lines)
    if not anchors:
        raise PlanError(f"no schedule block: no line {SCHEDULE_ANCHOR} outside code blocks and "
                        "outside the generated plan chart")
    if len(anchors) > 1:
        where = ", ".join(str(a + 1) for a in anchors)
        raise PlanError(f"{SCHEDULE_ANCHOR} appears {len(anchors)} times (lines {where}); a plan "
                        "holds one schedule block")
    a = anchors[0]
    k = a + 1
    if k < len(lines) and not lines[k].strip():
        k += 1
    fence = _fence_open(lines[k]) if k < len(lines) else None
    if not fence:
        raise PlanError(f"line {a + 1}: {SCHEDULE_ANCHOR} is not followed by a fenced JSON block "
                        "(one blank line may sit between them)")
    info = fence[2].split()[0].lower() if fence[2] else ""
    if info not in ("", "json"):
        raise PlanError(f"line {k + 1}: the schedule block is a `{info}` fence; it must be `json`")
    end = next((j for j in range(k + 1, len(lines)) if _fence_closes(lines[j], fence)), None)
    if end is None:
        raise PlanError(f"line {k + 1}: the fence of the schedule block is not closed")
    return _parse_json("\n".join(lines[k + 1:end]), first_line=k + 2)


def _is_markdown(path: Path, text: str) -> bool:
    suffix = path.suffix.lower()
    if suffix in (".md", ".markdown", ".mdown", ".mkd"):
        return True
    if suffix == ".json":
        return False
    return not text.lstrip().startswith("{")


def _tasks_from_data(data) -> list:
    """Build Tasks from the parsed schedule, from a JSON file or a Markdown block alike.

    `status` is optional in both inputs (TASK R8.1); a task without it is not started. Raises
    PlanError listing every shape problem.
    """
    if not isinstance(data, dict):
        raise PlanError(f'the schedule must be a JSON object {{"schema": "{SCHEMA}", '
                        '"tasks": [...]}')
    problems = []
    if data.get("schema") != SCHEMA:
        problems.append(f'"schema" must be "{SCHEMA}" (got {data.get("schema")!r})')
    extra = [k for k in data if k not in TOP_KEYS]
    if extra:
        problems.append(f"unknown top-level key {', '.join(map(repr, extra))}; "
                        f"allowed: {', '.join(TOP_KEYS)}")
    raw = data.get("tasks")
    if not isinstance(raw, list) or not raw:
        problems.append('"tasks" must be a non-empty list')
        raise PlanError("\n".join(problems))
    tasks = []
    for i, r in enumerate(raw, 1):
        where = f"task #{i}"
        if not isinstance(r, dict):
            problems.append(f"{where}: must be a JSON object")
            continue
        if isinstance(r.get("id"), str) and r.get("id"):
            where = f"task {r['id']}"
        missing = [k for k in TASK_KEYS if k not in r]
        if missing:
            problems.append(f"{where}: missing key {', '.join(missing)}")
        unknown = [k for k in r if k not in TASK_KEYS + TASK_KEYS_OPTIONAL]
        if unknown:
            problems.append(f"{where}: unknown key {', '.join(map(repr, unknown))}")
        if missing:
            continue
        est = r["est"]
        if isinstance(est, float) and est.is_integer():
            est = int(est)
        title, stage = r["title"], r["stage"]
        tasks.append(Task(id=r["id"], title=title.strip() if isinstance(title, str) else title,
                          stage=stage.strip() if isinstance(stage, str) else stage, est=est,
                          deps=r["deps"], status=r.get("status", "not-started")))
    if problems:
        raise PlanError("\n".join(problems))
    return tasks


def load_tasks(path: Path) -> list:
    """Read tasks from a JSON file or the schedule block of a Markdown plan.

    Raises PlanError on invalid input; OSError and UnicodeDecodeError when the file is unreadable.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    data = _markdown_schedule(text) if _is_markdown(p, text) else _parse_json(text)
    tasks = _tasks_from_data(data)
    validate_tasks(tasks)
    return tasks


# --------------------------------------------------------------------------- validation


def figure_id(task_id: str) -> str:
    """Return the mermaid id of a task: `t` plus the id, each character outside [A-Za-z0-9]
    replaced by `x`. Nothing references it; it names the bar in the SVG."""
    return "t" + re.sub(r"[^A-Za-z0-9]", "x", task_id)


def validate_tasks(tasks: list) -> None:
    """Raise PlanError naming every invalid task: id, title, stage, estimate, status, deps."""
    problems = []
    seen, fids = {}, {}
    for i, t in enumerate(tasks, 1):
        if not isinstance(t.id, str) or not ID_RE.fullmatch(t.id):
            problems.append(f"task #{i}: id must be a string matching {ID_RE.pattern} "
                            f"(got {t.id!r})")
            continue
        where = f"task {t.id}"
        if (t.id.lower() in GANTT_KEYWORDS or GANTT_KEYWORD_PREFIX_RE.match(t.id)
                or DATE_PREFIX_RE.match(t.id)):
            problems.append(f"{where}: the id opens a gantt statement; rename the task")
        if t.id in seen:
            problems.append(f"{where}: duplicate id (task #{seen[t.id]} has it too)")
        else:
            seen[t.id] = i
            fid = figure_id(t.id)
            if fid in fids:
                problems.append(f"{where}: its figure id {fid} equals that of task {fids[fid]}; "
                                "rename one")
            fids.setdefault(fid, t.id)
        for key in ("title", "stage"):
            value = getattr(t, key)
            if not isinstance(value, str) or not value.strip():
                problems.append(f"{where}: {key} must be a non-empty string")
            elif not _drawable(value):  # `section ` alone does not parse (10.9.8, 11.17.2)
                problems.append(f"{where}: {key} {value!r} holds no drawable character once `#`, "
                                "controls and zero-width characters are dropped")
        if isinstance(t.est, bool) or not isinstance(t.est, int) or t.est < 1:
            problems.append(f"{where}: est must be a whole number of hours, at least 1 "
                            f"(got {t.est!r})")
        if not isinstance(t.status, str) or t.status not in STATUSES:
            problems.append(f"{where}: unknown status {t.status!r}; "
                            f"expected one of {', '.join(STATUSES)}")
        if not isinstance(t.deps, list) or not all(isinstance(d, str) for d in t.deps):
            problems.append(f"{where}: deps must be a list of task ids")
    if problems:
        raise PlanError("\n".join(problems))
    for t in tasks:
        for d in dict.fromkeys(t.deps):
            if d == t.id:
                problems.append(f"task {t.id}: depends on itself")
            elif d not in seen:
                problems.append(f"task {t.id}: unknown dependency {d}")
    if problems:
        raise PlanError("\n".join(problems))


# --------------------------------------------------------------------------- schedule


def _topological_order(tasks: list) -> list:
    """Kahn's algorithm; ties go to input order. Raises PlanError naming a cycle."""
    index = {t.id: i for i, t in enumerate(tasks)}
    indeg = {t.id: len(dict.fromkeys(t.deps)) for t in tasks}
    succ = {t.id: [] for t in tasks}
    for t in tasks:
        for d in dict.fromkeys(t.deps):
            succ[d].append(t.id)
    heap = [index[t.id] for t in tasks if indeg[t.id] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        tid = tasks[heapq.heappop(heap)].id
        order.append(tid)
        for s in succ[tid]:
            indeg[s] -= 1
            if indeg[s] == 0:
                heapq.heappush(heap, index[s])
    if len(order) < len(tasks):
        raise PlanError("dependency cycle: " + _cycle_text(tasks, set(order)))
    return order


def _cycle_text(tasks: list, done: set) -> str:
    """Name one cycle among the tasks Kahn's algorithm left. Each of them has a left dependency."""
    by_id = {t.id: t for t in tasks}
    left = [t.id for t in tasks if t.id not in done]
    path, pos = [], {}
    cur = left[0]
    while cur not in pos:
        pos[cur] = len(path)
        path.append(cur)
        cur = next(d for d in by_id[cur].deps if d not in done)
    cycle = path[pos[cur]:] + [cur]
    return ", ".join(f"{cycle[k]} depends on {cycle[k + 1]}" for k in range(len(cycle) - 1))


def _backward_pass(tasks: list, order: list, es: dict, ef: dict) -> dict:
    """Return the total float of every task against the latest finish of the plan."""
    by_id = {t.id: t for t in tasks}
    succ = {t.id: [] for t in tasks}
    for t in tasks:
        for d in dict.fromkeys(t.deps):
            succ[d].append(t.id)
    makespan = max(ef.values())
    ls = {}
    for tid in reversed(order):
        lf = min((ls[s] for s in succ[tid]), default=makespan)
        ls[tid] = lf - by_id[tid].est
    return {t.id: ls[t.id] - es[t.id] for t in tasks}


def schedule(tasks: list) -> Schedule:
    """Compute early starts, the critical path and the ready list. Raises PlanError on a cycle."""
    validate_tasks(tasks)
    order = _topological_order(tasks)
    by_id = {t.id: t for t in tasks}
    index = {t.id: i for i, t in enumerate(tasks)}
    es, ef = {}, {}
    for tid in order:
        es[tid] = max((ef[d] for d in by_id[tid].deps), default=0)
        ef[tid] = es[tid] + by_id[tid].est
    makespan = max(ef.values())
    # the critical path: the longest path to the latest-finishing task; ties go to input order
    chain = [min((t for t in ef if ef[t] == makespan), key=index.__getitem__)]
    while True:
        cur = by_id[chain[-1]]
        tight = [d for d in cur.deps if ef[d] == es[cur.id]]
        if not tight:
            break
        chain.append(min(tight, key=index.__getitem__))
    chain.reverse()
    ready = [t.id for t in tasks
             if t.status != "done" and all(by_id[d].status == "done" for d in t.deps)]
    return Schedule(es={t.id: es[t.id] for t in tasks}, ef={t.id: ef[t.id] for t in tasks},
                    critical=chain, ready=ready, span=makespan - min(es.values()),
                    slack=_backward_pass(tasks, order, es, ef))


# --------------------------------------------------------------------------- text helpers


def _clean(text: str) -> str:
    """Make *text* safe inside a gantt line (research r4 E6).

    `:` ends a task's text, `#` and `;` end its data, and `%%` would open a directive or a
    comment; control characters and line breaks would split the line.
    """
    text = _CONTROL_RE.sub(" ", text)
    text = re.sub(r"\s*:\s*", " — ", text)
    text = text.replace("#", "").replace(";", ",")
    while "%%" in text:
        text = text.replace("%%", "%")
    return re.sub(r"\s+", " ", text).strip()


#: Markdown punctuation that opens a link, an image, emphasis, a code span or an escape.
_MARKDOWN_RE = re.compile(r"([\\`*_\[\]()!#])")


def _prose(text: str) -> str:
    """Make *text* safe in a Markdown paragraph: one line; Markdown punctuation escaped, so a
    title opens no link, image (a remote fetch) or emphasis; and no `<` that opens a tag or a
    comment (a title that holds a marker must not end the generated block)."""
    text = re.sub(r"\s+", " ", _CONTROL_RE.sub(" ", text)).strip()
    return _MARKDOWN_RE.sub(r"\\\1", text).replace("<", "&lt;")


def _drawable(text: str) -> bool:
    """True when *text* keeps a visible character in a gantt line."""
    return bool(_INVISIBLE_RE.sub("", _clean(text)).strip())


def _in_ranges(cp: int, ranges) -> bool:
    return any(lo <= cp <= hi for lo, hi in ranges)


def _text_px(text: str, font: float) -> float:
    em = 0.0
    for ch in text:
        cp = ord(ch)
        if _in_ranges(cp, _COMBINING_RANGES) or _INVISIBLE_RE.match(ch):
            continue
        em += WIDE_CHAR_EM if _in_ranges(cp, _WIDE_RANGES) else CHAR_EM
    return em * font


def _shorten(text: str, fits, keep: int = 0) -> str:
    """Cut *text* until `fits(cut + ellipsis)` holds; prefer a cut at a space. The first *keep*
    characters, a task id, are never cut into, trimmed, or dropped by the cut at a space."""
    if fits(text):
        return text
    cut = text
    while len(cut) > max(1, keep) and not fits(cut.rstrip() + ELLIPSIS):
        cut = cut[:-1]
    space = cut.rfind(" ")
    if space > keep and space >= max(1, len(cut) // 2):
        cut = cut[:space]
    return cut[:keep] + cut[keep:].rstrip(" ,.—-") + ELLIPSIS


def _bar_label(task: Task, max_chars: int) -> str:
    """`<id> <title>`, cleaned, at most *max_chars* characters (TASK D25: characters, not words).
    The limit counts the id; an id longer than the limit stays whole."""
    return _shorten(_clean(f"{task.id} {task.title}"), lambda s: len(s) <= max_chars,
                    keep=len(task.id))


def _fit_label(label: str, id_len: int, room_px: float, font: float) -> str:
    """Shorten a bar label to *room_px*. The task id always stays whole; at the least, the label
    is the id and the ellipsis."""
    return _shorten(label, lambda s: _text_px(s, font) <= room_px or len(s) <= id_len + 2,
                    keep=id_len)


def _wrap_title(title: str, max_chars: int, max_px: float, font: float):
    """Wrap a section title into at most two lines joined by `<br>`; return (lines, shortened)."""
    def fits(s: str) -> bool:
        return len(s) <= max_chars and _text_px(s, font) <= max_px

    lines, cur = [], ""
    for word in title.split(" "):
        trial = f"{cur} {word}" if cur else word
        if fits(trial):
            cur = trial
            continue
        if cur:
            lines.append(cur)
        while not fits(word) and len(word) > 1:  # a word longer than a line is split
            n = len(word)
            while n > 1 and not fits(word[:n]):
                n -= 1
            lines.append(word[:n])
            word = word[n:]
        cur = word
    if cur:
        lines.append(cur)
    shortened = len(lines) > SECTION_LINES_MAX
    if shortened:
        rest = " ".join(lines[SECTION_LINES_MAX - 1:])
        lines = lines[:SECTION_LINES_MAX - 1] + [_shorten(rest, fits)]
    return lines, shortened


def _nice_steps():
    """1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, ... (research r4 E4)."""
    base = 1
    while True:
        for m in ((1, 2, 5) if base == 1 else (1, 2, 2.5, 5)):
            yield int(m * base)
        base *= 10


def tick_step(lo: int, hi: int, max_ticks: int = TICKS_MAX) -> int:
    """The smallest nice step whose multiples inside [lo, hi] number at most *max_ticks*."""
    for step in _nice_steps():
        if hi // step - (-(-lo // step)) + 1 <= max_ticks:
            return step
    raise AssertionError("unreachable")  # pragma: no cover


def _gantt_settings(notation: dict) -> dict:
    """Return the parsed `settings.gantt` line of notation.json, a fresh dict on every call."""
    line = notation["settings"]["gantt"].strip()
    m = re.fullmatch(r"%%\{\s*init\s*:\s*(\{.*\})\s*\}%%", line, re.S)
    if not m:
        raise RuntimeError("notation.json settings.gantt is not a %%{init: {...}}%% line")
    cfg = json.loads(m.group(1))
    if not isinstance(cfg, dict):
        raise RuntimeError("notation.json settings.gantt does not hold a JSON object")
    return cfg


def _balanced_css(css: str) -> bool:
    """mermaid's `sanitizeCss`: no `}` before its `{`, and as many `{` as `}`."""
    opened = closed = 0
    for ch in css:
        if opened < closed:
            return False
        if ch == "{":
            opened += 1
        elif ch == "}":
            closed += 1
    return opened == closed


def _setting_problems(cfg: dict) -> list:
    """Name every key and value of a gantt settings line that mermaid would drop or alter.

    An empty list means the line reaches the renderer as written. The rules are those of the
    sanitizer comment above SETTINGS_TOP_KEYS; a fixed `theme` is refused as well (TASK R4.2).
    """
    problems = []

    def walk(value, path: str, key: str) -> None:
        if isinstance(value, dict):
            for k, item in value.items():
                where = f"{path}.{k}" if path else str(k)
                if not isinstance(k, str) or k.startswith("__") or "proto" in k or "constr" in k:
                    problems.append(f"{where}: mermaid deletes this key")
                    continue
                walk(item, where, k)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                walk(item, f"{path}[{i}]", key)
        elif value is None:
            problems.append(f"{path}: null; mermaid deletes it")
        elif isinstance(value, str):
            unsafe = [s for s in UNSAFE_SETTING_TEXT if s in value]
            if unsafe:
                problems.append(f"{path}: holds {', '.join(map(repr, unsafe))}; mermaid deletes "
                                "or rereads the value")
            if _CONTROL_RE.search(value):
                problems.append(f"{path}: holds a control character or a line break")
            if any(part in key for part in CSS_KEY_PARTS) and not _balanced_css(value):
                problems.append(f"{path}: unbalanced braces; mermaid replaces the CSS")
        elif isinstance(value, float) and not math.isfinite(value):
            problems.append(f"{path}: not a finite number")

    if "theme" in cfg:
        problems.append("theme: a fixed theme draws light-theme text on a dark page (TASK R4.2)")
    for key in cfg:
        if key != "theme" and key not in SETTINGS_TOP_KEYS:
            problems.append(f"{key}: not a key of the gantt settings line; allowed: "
                            f"{', '.join(sorted(SETTINGS_TOP_KEYS))}")
    gantt = cfg.get("gantt", {})
    if not isinstance(gantt, dict):
        problems.append("gantt: must be a JSON object")
    else:
        for key in gantt:
            if key not in GANTT_CONFIG_KEYS:
                problems.append(f"gantt.{key}: not a gantt configuration key; mermaid deletes it")
    theme_variables = cfg.get("themeVariables", {})
    if not isinstance(theme_variables, dict):
        problems.append("themeVariables: must be a JSON object")
    else:
        for key, value in theme_variables.items():
            if isinstance(value, str) and not THEME_VALUE_RE.fullmatch(value):
                problems.append(f"themeVariables.{key} = {value!r}: mermaid blanks it")
    walk(cfg, "", "")
    return problems


# --------------------------------------------------------------------------- rendering


def _stage_order(tasks: list) -> list:
    return list(dict.fromkeys(t.stage for t in tasks))


def _figure(tasks: list, sched: Schedule, stages: Optional[list], notation: dict) -> dict:
    """One chart: caption, fence lines, legend, bar count and warnings."""
    known = _stage_order(tasks)
    if stages:
        unknown = [s for s in stages if s not in known]
        if unknown:
            raise PlanError(f"unknown stage {', '.join(unknown)}; the plan's stages: "
                            f"{', '.join(known)}")
        wanted = set(stages)
        drawn = [s for s in known if s in wanted]
    else:
        drawn = known
    index = {t.id: i for i, t in enumerate(tasks)}
    shown = [t for t in tasks if t.stage in drawn]
    critical = set(sched.critical)
    cfg = _gantt_settings(notation)  # a fresh dict on every call
    problems = _setting_problems(cfg)
    if problems:
        raise RuntimeError("notation.json settings.gantt: " + "; ".join(problems))
    gantt = cfg.setdefault("gantt", {})
    font = gantt.get("fontSize", 11)
    section_font = gantt.get("sectionFontSize", font)
    # The chart is drawn `useWidth` wide; without it, it would fill its container, and every
    # padding below would be computed for a width no viewer guarantees.
    width = gantt.get("useWidth", notation["column_px"])
    if isinstance(width, bool) or not isinstance(width, (int, float)) or not width > 0:
        raise RuntimeError(f"notation.json settings.gantt: useWidth = {width!r} is not a positive "
                           "number")
    width = int(width)
    max_chars = int(notation["labels"]["gantt_label_chars_max"])
    soft, hard = notation["budgets"]["gantt"]["bars"]
    warnings = []

    # section titles and leftPadding. Every stage gets its title, so that no two stages share one
    # in any chart: mermaid draws two sections of one title as one section (G6).
    title_px = LEFT_MAX_PX - TITLE_MARGIN_PX
    titles, owner = {}, {}
    for s in known:
        lines, shortened = _wrap_title(_clean(s), max_chars, title_px, section_font)
        title = "<br>".join(lines)
        if title in owner:
            raise PlanError(f"stages {owner[title]!r} and {s!r} give the same section title "
                            f"{title!r}; rename one")
        owner[title] = s
        if shortened and s in drawn:
            warnings.append(f"section title shortened: {s!r}")
        titles[s] = lines
    widest = max((_text_px(line, section_font) for s in drawn for line in titles[s]), default=0)
    left = int(min(LEFT_MAX_PX, max(LEFT_MIN_PX, math.ceil(widest) + TITLE_MARGIN_PX)))

    # labels, and the largest time area that keeps every label right of its bar
    labels = {t.id: _bar_label(t, max_chars) for t in shown}
    for t in shown:
        if labels[t.id] == _clean(f"{t.id} {t.title}"):
            continue
        if len(t.id) + 2 + len(ELLIPSIS) > max_chars:  # no `<id> <c>…` fits; the id stays whole
            warnings.append(f"label of {t.id} shows no title: the id leaves no room in "
                            f"{max_chars} characters; shorten the id")
        else:
            warnings.append(f"label of {t.id} shortened to {max_chars} characters, its id "
                            "included; shorten its title")
    lo = min(sched.es[t.id] for t in shown)
    hi = max(sched.ef[t.id] for t in shown)
    span = max(1, hi - lo)
    area = float(width - left - RIGHT_EDGE_MIN_PX)
    for t in shown:
        frac = (sched.ef[t.id] - lo) / span
        room = width - LABEL_SIDE_FACTOR * left - _text_px(labels[t.id], font)
        if frac > 0 and room / frac < area:
            area = room / frac
    area = math.floor(area)
    area_min = min(math.ceil(AREA_MIN_SHARE * width), width - left - RIGHT_EDGE_MIN_PX)
    if area < area_min:
        area = area_min
        for t in shown:
            room = width - LABEL_SIDE_FACTOR * left - (sched.ef[t.id] - lo) / span * area
            if _text_px(labels[t.id], font) > room:
                labels[t.id] = _fit_label(labels[t.id], len(t.id), room, font)
                warnings.append(f"label of {t.id} shortened to fit right of its bar")
    right = width - left - area
    shortest = min(t.est for t in shown)
    if shortest * area / span < MIN_BAR_PX:
        warnings.append(f"the shortest bar is {shortest * area / span:.1f} px wide (< {MIN_BAR_PX}"
                        " px); split the chart with --stages")
    if len(shown) > hard:
        warnings.append(f"{len(shown)} bars in one chart exceed the hard budget of {hard}; split "
                        "it with --stages")
    elif len(shown) > soft:
        warnings.append(f"{len(shown)} bars in one chart exceed the soft budget of {soft}; split "
                        "it with --stages")

    # Merged into the settings line; every other key and value of it, `themeCSS` included, stays
    # as notation.json writes it.
    gantt["useWidth"] = width
    gantt["leftPadding"] = left
    gantt["rightPadding"] = right
    if len(shown) > TOP_AXIS_ABOVE_BARS:
        gantt["topAxis"] = True  # never the `topAxis` statement: it throws in 10.9 and 12.1
    problems = _setting_problems(cfg)
    if problems:  # pragma: no cover - the computed values are whole numbers and a boolean
        raise RuntimeError("the merged gantt settings line: " + "; ".join(problems))

    subset = len(drawn) < len(known)
    stage_list = " · ".join(_clean(s) for s in drawn)  # a stage name may hold a comma
    caption_title = (TEXT["caption_title_stages"].format(stages=stage_list) if subset
                     else TEXT["caption_title"])
    caption_body = TEXT["caption_stages"] if subset else TEXT["caption"]
    fence = ["```mermaid", "%%{init: " + json.dumps(cfg, ensure_ascii=False) + "}%%", "gantt",
             f"  accTitle: {_clean(caption_title)}",
             f"  accDescr: {_clean(caption_body)}",
             "  dateFormat x", "  axisFormat %Q",
             f"  tickInterval {tick_step(lo, hi)}millisecond", "  todayMarker off"]
    for s in drawn:
        fence.append(f"  section {'<br>'.join(titles[s])}")
        rows = sorted((t for t in shown if t.stage == s),
                      key=lambda t: (sched.es[t.id], index[t.id]))
        for t in rows:
            tags = ["done"] if t.status == "done" else ["active"] if t.status == "in-progress" \
                else []
            if t.id in critical:
                tags.append("crit")
            meta = ", ".join(tags + [figure_id(t.id), str(sched.es[t.id]), f"{t.est}ms"])
            # no space before the colon: mermaid keeps it in the drawn text (10.9.8, 11.17.2)
            fence.append(f"    {labels[t.id]}:{meta}")
    fence.append("```")

    items = []
    if any(t.status == "done" for t in shown):
        items.append(TEXT["legend_done"])
    if any(t.status == "in-progress" for t in shown):
        items.append(TEXT["legend_active"])
    if any(t.status == "not-started" for t in shown):
        items.append(TEXT["legend_waiting"])
    if any(t.id in critical for t in shown):
        items.append(TEXT["legend_crit"])
    return {"caption": f"**{_prose(caption_title)}.** {caption_body}", "fence": fence,
            "legend": TEXT["legend"].format(items=" · ".join(items)),
            "bars": len(shown), "warnings": warnings}


def _remaining_hours(tasks: list) -> int:
    """The longest path when done tasks cost nothing."""
    by_id = {t.id: t for t in tasks}
    rem = {}
    for tid in _topological_order(tasks):
        t = by_id[tid]
        rem[tid] = max((rem[d] for d in t.deps), default=0) + (0 if t.status == "done" else t.est)
    return max(rem.values())


def _status_lines(tasks: list, sched: Schedule) -> list:
    """The ready-to-start list and the critical-path line, for the whole plan."""
    by_id = {t.id: t for t in tasks}
    index = {t.id: i for i, t in enumerate(tasks)}
    slack = sched.slack or _backward_pass(tasks, _topological_order(tasks), sched.es, sched.ef)
    critical = set(sched.critical)
    out = []
    ready = sorted(sched.ready, key=lambda tid: (slack.get(tid, 0), index[tid]))
    if ready:
        out += [TEXT["ready_head"], ""]
        for tid in ready:
            t = by_id[tid]
            where = TEXT["on_cp"] if tid in critical else TEXT["slack"].format(s=slack.get(tid, 0))
            if t.status == "in-progress":
                where += ", " + TEXT["in_progress"]
            out.append(TEXT["ready_item"].format(id=tid, title=_prose(t.title), est=t.est,
                                                 where=where))
    else:
        out.append(TEXT["ready_none"])
    chain = " → ".join(sched.critical)
    if any(t.status != "not-started" for t in tasks):
        done = sum(1 for tid in sched.critical if by_id[tid].status == "done")
        line = TEXT["cp_status"].format(h=sched.span, done=done, n=len(sched.critical),
                                        rem=_remaining_hours(tasks), chain=chain)
    else:
        line = TEXT["cp"].format(h=sched.span, chain=chain)
    also = [t.id for t in tasks if slack.get(t.id) == 0 and t.id not in critical]
    if also:
        line += TEXT["cp_also"].format(ids=", ".join(also))
    return out + ["", line]


def render_charts(tasks: list, sched: Schedule, groups: Optional[list] = None,
                  notation: Optional[dict] = None) -> Rendered:
    """Render one chart per stage group (None or [] = every stage) into one block, followed once
    by the ready-to-start list and the critical-path line. Hours stay absolute in every chart."""
    notation = notation if notation is not None else load_notation()
    parts, warnings, bars = [], [], []
    for stages in (groups or [None]):
        fig = _figure(tasks, sched, stages, notation)
        parts += [fig["caption"], "", *fig["fence"], "", fig["legend"], ""]
        warnings += fig["warnings"]
        bars.append(fig["bars"])
    parts += _status_lines(tasks, sched)
    return Rendered(text="\n".join(parts), warnings=warnings, bars=bars)


def render_block(tasks: list, sched: Schedule, stages: Optional[list] = None,
                 notation: Optional[dict] = None) -> str:
    """Return the Markdown block: caption, the mermaid fence, the legend, the ready list and the
    critical-path line. *stages* limits the drawn sections; hours stay absolute."""
    return render_charts(tasks, sched, [stages] if stages else None, notation).text


def groups_line(groups: list) -> str:
    """The first line of a split region: the stage groups as JSON in an HTML comment."""
    text = json.dumps(groups, ensure_ascii=False)
    return GROUPS_PREFIX + _GROUPS_ESCAPE_RE.sub(lambda m: f"\\u{ord(m.group()):04x}",
                                                 text) + GROUPS_SUFFIX


def region_block(rendered: Rendered, groups: Optional[list] = None) -> str:
    """The text `--write` puts between the markers: the stored stage groups when the chart is
    split, then the charts, the ready list and the critical-path line."""
    return groups_line(groups) + "\n\n" + rendered.text if groups else rendered.text


def _doc_lines(doc: str):
    """Return `(lines, ends)`: the lines of *doc* without their line ends, and each line's end:
    `\\r\\n`, `\\n`, or an empty string for a last line without one."""
    lines, ends = [], []
    pieces = doc.split("\n")
    for k, piece in enumerate(pieces):
        if k == len(pieces) - 1:
            lines.append(piece)
            ends.append("")
        elif piece.endswith("\r"):
            lines.append(piece[:-1])
            ends.append("\r\n")
        else:
            lines.append(piece)
            ends.append("\n")
    return lines, ends


#: A heading, a setext underline or a rule: `plan_gantt.py` writes none of them.
_HEADING_RE = re.compile(r"^ {0,3}(?:#{1,6}(?:[ \t]|$)|=+[ \t]*$|-+[ \t]*$)")


def _foreign_line(lines: list, start: int, end: int):
    """Return `(index, what)` of the first line between the markers that `plan_gantt.py` never
    writes there, or None: a heading, an HTML comment other than the stored stage groups in the
    first line (`_stored_groups` reports a damaged one), or a fence other than `mermaid`. Such a
    line is document text that a lost or misplaced marker let into the region. Text inside a
    `mermaid` fence is not read: a label may hold `<!--`, and a damaged fence may run to the end
    marker."""
    fence, first = None, True
    for i in range(start + 1, end):
        line = lines[i]
        if fence:
            if _fence_closes(line, fence):
                fence = None
            continue
        if not line.strip():
            continue
        is_first, first = first, False
        opened = _fence_open(line)
        if opened:
            info = opened[2].split()[0].lower() if opened[2] else ""
            if info != "mermaid":
                return i, f"a fence that is not mermaid ({line.strip()!r})"
            fence = opened
        elif _HEADING_RE.match(line):
            return i, f"a heading or a rule ({line.strip()!r})"
        elif "<!--" in line and not (is_first
                                     and line.strip().startswith(GROUPS_PREFIX.rstrip())):
            return i, f"an HTML comment ({line.strip()!r})"
    return None


def _marker_pair(doc: str):
    """Return `(lines, ends, start, end)`: the lines of *doc* as `_doc_lines` splits them and the
    indexes of its two marker lines.

    Raises PlanError unless the document holds exactly one marker pair, in order, outside fenced
    code, around a region that holds no document text (`_foreign_line`).
    """
    lines, ends = _doc_lines(doc)
    _, starts, found_ends = _scan(lines)
    if len(starts) != 1 or len(found_ends) != 1 or found_ends[0] < starts[0]:
        raise PlanError(f"the document needs exactly one {MARKER_START} line followed by one "
                        f"{MARKER_END} line (found {len(starts)} and {len(found_ends)})")
    start, end = starts[0], found_ends[0]
    foreign = _foreign_line(lines, start, end)
    if foreign:
        i, what = foreign
        raise PlanError(f"line {i + 1}: the plan chart region (lines {start + 1}-{end + 1}) holds "
                        f"{what}, which plan_gantt.py never writes there; a plan chart marker is "
                        "lost or misplaced. Fix the markers; the document is unchanged")
    return lines, ends, start, end


def region_is_empty(doc: str) -> bool:
    """True when the region between the markers of *doc* holds blank lines only (TASK R8.5).

    Raises PlanError as `replace_between_markers` does.
    """
    lines, _, start, end = _marker_pair(doc)
    return not any(line.strip() for line in lines[start + 1:end])


def replace_between_markers(doc: str, block: str) -> str:
    """Return *doc* with the text between the two markers replaced by *block*.

    The region becomes: the start marker line, a blank line, the block, a blank line, the end
    marker line. An empty *block* puts the end marker line directly under the start marker line,
    as the plan template writes them. Every line outside the region keeps its bytes; the new
    lines take the line end of the end marker line. Raises PlanError as `_marker_pair` does.
    """
    lines, ends, start, end = _marker_pair(doc)
    eol = ends[end] or ends[start]  # an end marker on the last line has no line end
    body = ["", *block.strip("\n").split("\n"), ""] if block.strip() else []
    head = "".join(line + e for line, e in zip(lines[:start + 1], ends[:start + 1]))
    tail = "".join(line + e for line, e in zip(lines[end:], ends[end:]))
    return head + "".join(line + eol for line in body) + tail


def _stored_groups(doc: str):
    """Return `(line index, groups)` stored in the first line of the region of *doc*, or
    `(None, None)` when that line holds none. Raises PlanError on a line that cannot be read."""
    lines, _, start, end = _marker_pair(doc)
    i = next((k for k in range(start + 1, end) if lines[k].strip()), None)
    if i is None or not lines[i].strip().startswith(GROUPS_PREFIX.rstrip()):
        return None, None
    m = _GROUPS_LINE_RE.fullmatch(lines[i].strip())
    try:
        groups = json.loads(m.group(1)) if m else None
    except ValueError:
        groups = None
    if not (isinstance(groups, list) and groups and all(
            isinstance(g, list) and g and all(isinstance(s, str) for s in g) for g in groups)):
        raise PlanError(f"line {i + 1}: the stored stage groups are not a JSON list of lists of "
                        "stage names; pass --stages to replace them")
    return i, groups


# --------------------------------------------------------------------------- CLI


EXIT_CODES_HELP = ("exit codes (TASK 108 D20): 0 ok; 1 stale region or invalid plan; "
                   "2 instrument broken; 3 usage error")
#: Opens each warning on stderr; a warning leaves the exit code 0, so the planner reads each one.
WARNING_PREFIX = "plan_gantt: warning:"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="plan_gantt.py",
                                description="Draw a plan as a dependency-scheduled Mermaid gantt. "
                                            "Without --write or --check, print the chart wrapped "
                                            "in its markers.",
                                epilog=EXIT_CODES_HELP)
    p.add_argument("plan", nargs="?", help="JSON schedule, or a Markdown plan with a schedule block")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--write", metavar="DOC",
                   help="replace the region between the markers of DOC; a plan of fewer than "
                        f"{MIN_TASKS} tasks empties it")
    g.add_argument("--check", metavar="DOC",
                   help="exit 1 when the region of DOC differs from what --write puts there; "
                        "writes nothing")
    p.add_argument("--stages", action="append", metavar="A,B",
                   help="comma-separated stage names drawn in one chart; repeat the option for "
                        "one chart per stage group. The groups name every stage once; --write "
                        "stores them in the region, and a later --write or --check without "
                        "--stages reuses them")
    p.add_argument("--strict", action="store_true",
                   help="exit 1 when a chart exceeds the hard bar budget")
    return p


def _stage_list(value: str, known: list) -> list:
    """Split one `--stages` value at commas. A stage name that holds a comma is matched whole:
    at each position the longest run of comma-joined pieces that names a stage wins."""
    pieces, names, i = value.split(","), [], 0
    while i < len(pieces):
        end = next((j for j in range(len(pieces), i, -1)
                    if ",".join(pieces[i:j]).strip() in known), None)
        if end is None:
            if pieces[i].strip():
                raise UsageError(f"--stages: unknown stage {pieces[i].strip()}; the plan's "
                                 f"stages: {'; '.join(known)}")
            i += 1
            continue
        names.append(",".join(pieces[i:end]).strip())
        i = end
    if not names:
        raise UsageError("--stages: no stage name given")
    return names


def _normal_groups(groups: list, known: list, source: str) -> Optional[list]:
    """Check that *groups* name every stage of the plan once, and return them in a fixed order:
    each group in plan order, the groups by their first stage. One group of every stage is one
    chart and returns None. Raises PlanError naming the stages left out or repeated."""
    order = {s: i for i, s in enumerate(known)}
    named = [s for g in groups for s in g]
    unknown = [s for s in dict.fromkeys(named) if s not in order]
    if unknown:
        raise PlanError(f"{source} name stage {'; '.join(unknown)}, which the plan does not "
                        f"hold; the plan's stages: {'; '.join(known)}")
    missing = [s for s in known if s not in named]
    repeated = [s for s in known if named.count(s) > 1]
    if missing or repeated:
        found = ([f"left out: {'; '.join(missing)}"] if missing else []) + (
            [f"named more than once: {'; '.join(repeated)}"] if repeated else [])
        raise PlanError(f"{source} must name every stage exactly once; {', '.join(found)}")
    ordered = sorted((sorted(g, key=order.__getitem__) for g in groups),
                     key=lambda g: order[g[0]])
    return ordered if len(ordered) > 1 else None


def _stage_groups(values: Optional[list], known: list) -> Optional[list]:
    if not values:
        return None
    return _normal_groups([_stage_list(value, known) for value in values], known, "--stages")


def _command(plan, groups: Optional[list], option: str, doc) -> str:
    """The shell command that writes the region again, its stage groups included."""
    words = ["plan_gantt.py", str(plan)]
    for group in groups or ():
        words += ["--stages", ",".join(group)]
    return " ".join(shlex.quote(w) for w in words + [option, str(doc)])


def _read_doc(path: Path):
    """Return `(text, whether it starts with a BOM)`; the text keeps the file's line ends."""
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    bom = raw.startswith("\ufeff")
    return (raw[1:] if bom else raw), bom


def _write_doc(path: Path, text: str, bom: bool) -> None:
    """Write through a temporary file in the same directory, then rename it over *path*."""
    target = path.resolve()
    # The rename succeeds over a read-only file; a document its owner made read-only stays so.
    if not os.access(target, os.W_OK):
        raise PermissionError(errno.EACCES, "the document is read-only", str(path))
    data = ("\ufeff" if bom else "") + text
    fd, tmp = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(data)
        try:
            os.chmod(tmp, os.stat(target).st_mode & 0o7777)
        except OSError:
            pass
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _load_doc(doc_path: Path):
    try:
        return _read_doc(doc_path)
    except (OSError, UnicodeDecodeError) as exc:
        raise UsageError(f"cannot read {doc_path}: {exc}") from None


def _store_doc(doc_path: Path, text: str, bom: bool) -> None:
    try:
        _write_doc(doc_path, text, bom)
    except OSError as exc:
        raise UsageError(f"cannot write {doc_path}: {exc}") from None


def _small_plan(args, doc_path: Path, doc: str, bom: bool, n: int) -> int:
    """`--write` and `--check` for a plan of fewer than MIN_TASKS tasks (TASK R8.5): the region
    between the markers stays empty. `--check` passes on a region of blank lines only. `_run`
    calls it after the charts are drawn, so the plan has passed every check of a chart."""
    reason = (f"{n} tasks, fewer than {MIN_TASKS}: the plan gets no chart, and the region "
              "between the markers stays empty (TASK 108 R8.5)")
    empty = region_is_empty(doc)
    if args.check:
        if empty:
            print(f"{doc_path}: plan chart region is empty, as a plan of {n} tasks needs")
            return EXIT_OK
        print(f"{doc_path}: plan chart region is stale: {reason}; run "
              f"{_command(args.plan, None, '--write', doc_path)}", file=sys.stderr)
        return EXIT_FAIL
    print(f"plan_gantt: {reason}", file=sys.stderr)
    if empty:
        print(f"{doc_path}: plan chart region unchanged, empty")
        return EXIT_OK
    _store_doc(doc_path, replace_between_markers(doc, ""), bom)
    print(f"{doc_path}: plan chart region emptied")
    return EXIT_OK


def _report(out: Rendered, strict: bool, notation: dict) -> None:
    """Print the warnings; under `--strict`, raise PlanError for a chart over the hard budget."""
    for w in out.warnings:
        print(f"{WARNING_PREFIX} {w}", file=sys.stderr)
    if strict:
        hard = notation["budgets"]["gantt"]["bars"][1]
        over = [n for n in out.bars if n > hard]
        if over:
            raise PlanError(f"{max(over)} bars in one chart exceed the hard budget of {hard} "
                            "(--strict); split the chart with --stages")


def _run(args) -> int:
    plan = Path(args.plan)
    try:
        tasks = load_tasks(plan)
    except (OSError, UnicodeDecodeError) as exc:
        raise UsageError(f"cannot read {plan}: {exc}") from None
    known = _stage_order(tasks)
    groups = _stage_groups(args.stages, known)
    sched = schedule(tasks)
    notation = load_notation()
    # The charts are drawn for every plan in every mode, before the document is read. Each check
    # they make, such as two stages with one section title or a settings line that mermaid
    # alters, then gives one exit code in the preview, `--write` and `--check`, at every plan
    # size. A plan of fewer than MIN_TASKS tasks still gets no chart written.
    out = render_charts(tasks, sched, groups, notation)
    target = args.write or args.check
    if not target:
        _report(out, args.strict, notation)
        if len(tasks) < MIN_TASKS:
            print(f"plan_gantt: note: {len(tasks)} tasks, fewer than {MIN_TASKS}: --write leaves "
                  "the region between the markers empty; the chart below is a preview",
                  file=sys.stderr)
        print(f"{MARKER_START}\n\n{region_block(out, groups)}\n\n{MARKER_END}")
        return EXIT_OK
    doc_path = Path(target)
    doc, bom = _load_doc(doc_path)
    if len(tasks) < MIN_TASKS:
        return _small_plan(args, doc_path, doc, bom, len(tasks))
    if args.stages is None:  # the groups a split --write stored (UC-2 A3)
        line, stored = _stored_groups(doc)
        if stored is not None:
            groups = _normal_groups(stored, known, f"line {line + 1}: the stage groups stored "
                                                   f"in {doc_path} (pass --stages to regroup)")
            out = render_charts(tasks, sched, groups, notation)
    _report(out, args.strict, notation)
    new = replace_between_markers(doc, region_block(out, groups))
    if args.check:
        if new == doc:
            print(f"{doc_path}: plan chart is current")
            return EXIT_OK
        print(f"{doc_path}: plan chart is stale; run "
              f"{_command(args.plan, groups, '--write', doc_path)}", file=sys.stderr)
        return EXIT_FAIL
    if new == doc:
        print(f"{doc_path}: plan chart unchanged")
        return EXIT_OK
    _store_doc(doc_path, new, bom)
    print(f"{doc_path}: plan chart written")
    return EXIT_OK


def main(argv: Optional[list] = None) -> int:
    p = build_parser()
    try:
        args = p.parse_args(argv)
    except SystemExit as exc:
        return EXIT_OK if not exc.code else EXIT_USAGE
    if not args.plan:
        p.print_usage(sys.stderr)
        return EXIT_USAGE
    try:
        return _run(args)
    except PlanError as exc:
        first, *rest = str(exc).split("\n")
        print(f"plan_gantt: {first}", file=sys.stderr)
        for line in rest:
            print(f"  {line}", file=sys.stderr)
        return EXIT_FAIL
    except UsageError as exc:
        print(f"plan_gantt: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except Exception as exc:  # the instrument is broken; never report it as a verdict
        print(f"plan_gantt: internal error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_INTERNAL


if __name__ == "__main__":
    sys.exit(main())
