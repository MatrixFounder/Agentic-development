#!/usr/bin/env python3
"""Static lint for the figures of a Markdown document or a `.mmd` file (TASK 108, R6).

Figures. Every `mermaid` fence and every `text figure` fence of a Markdown document (TASK R2.5,
R6.1); a plain `text` fence is a listing and is not linted. A `.mmd` file is one figure.

Each rule carries a probe pair: one or more figures on which it must fire, and a figure on which
it must not. Every run checks the probes first. A rule whose probe fails stops the run with
exit 2, so a dead rule cannot report a clean document.

Thresholds come from `assets/notation.json` only (ARCHITECTURE §10.1). Probes that depend on a
threshold are built from the active notation, so a probe measures its detector, never the value.

Severity. `error` marks a render failure, a silent change of the figure, a construct that mermaid
10.9 cannot render, a hard budget, text below the contrast minimum, or a negative marker that is
broken or stands in a project document. Everything else is `warn`.

Negative fences (TASK R9.4, R6.7). A mermaid fence whose last body line is
`%% negative: <names>` shows a defect on purpose. The names are lint rule ids, lint family names
(FAMILY_PREFIXES) or render check names (`mermaid_model.RENDER_CHECK_NAMES`). The findings of the
named rules and families inside the fence are `expected`: they are reported apart and set no
exit code. Every other finding of the fence counts, so a marker never hides a defect it does
not name. The marker counts only in the skill's references and test fixtures
(`mermaid_model.negative_allowed`); elsewhere MA-NEG-03 reports it and the fence is linted as a
positive figure. MA-NEG-01 reports a negative fence on which none of the named lint checks
fires; MA-NEG-02 reports a malformed marker. All three count.

Language. No rule keys on a natural-language word (ARCHITECTURE invariant L1): caption and legend
are the paragraphs next to the fence; label limits count characters per line; the case rule
applies only to scripts that have case.

Exit codes (TASK D20, ARCHITECTURE §7.4)
  0  no `error` finding outside negative fences
  1  one or more `error` findings outside negative fences, MA-NEG-01, MA-NEG-02 and MA-NEG-03
     included
  2  instrument broken: a failed probe, a rule or the parser failed, notation unreadable
  3  usage error, including an unreadable input path, and `--probe` given with paths

The lint writes no file. Standard library only. Runs in CI.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mermaid_model as mm  # noqa: E402
import planarity  # noqa: E402

EXIT_OK, EXIT_FINDINGS, EXIT_INTERNAL, EXIT_USAGE = 0, 1, 2, 3


@dataclass
class Finding:
    rule: str  # e.g. "MA-PARSE-01"
    severity: str  # "error" | "warn"
    path: str
    line: int  # 1-based document line; 0 when the finding concerns a whole figure of a .mmd file
    message: str
    hint: str = ""
    fence: int = 0  # line of the opening fence of the finding's figure; 0 for a .mmd file
    expected: bool = False  # True inside a negative fence: reported apart, no exit code


@dataclass
class Rule:
    """One lint rule.

    `check(figure, ctx)` returns a list of `(line, message)` pairs for one figure. Document-level
    rules set `scope="document"` and receive the list of figures as `figure`: the positive
    figures of the document, or those plus one negative figure last. Marker rules set
    `scope="marker"`, receive every figure, and report on the negative markers themselves; their
    findings are never `expected`.
    `probe_fire` and `probe_quiet` are Markdown documents; the probe passes when the rule reports
    at least one finding on `probe_fire` and none on `probe_quiet`. A probe may also be a callable
    that takes the notation dict and returns the document, for rules whose probe depends on a
    threshold. `probe_fire` may be a tuple of probes, one per detector of the rule; each must
    fire. The probes run with negative markers honoured unless `probe_negative` is False.
    """

    id: str
    severity: str
    title: str
    hint: str
    check: Callable
    probe_fire: object  # a probe, or a tuple of probes that must each fire
    probe_quiet: object
    scope: str = "figure"  # "figure" | "document" | "marker"
    probe_negative: bool = True


#: Rule registry, filled below. Order is report order.
RULES: list = []

#: Lint family names a negative marker may name, and the rule-id prefix each stands for. A family
#: name is the middle part of its rule ids; a marker may write it in any case, with or without
#: `MA-` (`budget`, `BUDGET`, `MA-BUDGET`). The marker rules (MA-NEG) are not a nameable family.
FAMILY_PREFIXES = {
    "parse": "MA-PARSE-",
    "syn": "MA-SYN-",
    "set": "MA-SET-",
    "id": "MA-ID-",
    "budget": "MA-BUDGET-",
    "flow": "MA-FLOW-",
    "state": "MA-STATE-",
    "seq": "MA-SEQ-",
    "label": "MA-LABEL-",
    "class": "MA-CLASS-",
    "gantt": "MA-GANTT-",
    "ascii": "MA-ASCII-",
    "doc": "MA-DOC-",
    "model": "MA-MODEL-",
}


@dataclass
class LintContext:
    notation: dict
    path: str
    is_mmd: bool = False
    extra: dict = field(default_factory=dict)
    #: whether `%% negative:` markers count; None decides by the path (`mm.negative_allowed`)
    negative: Optional[bool] = None
    #: id(figure) -> the marker that makes the figure negative, or None; filled once per figure,
    #: so a fence with many findings does not rescan its body per finding
    markers: dict = field(default_factory=dict)

    def honours_markers(self) -> bool:
        if self.negative is None:
            self.negative = mm.negative_allowed(self.path)
        return self.negative


class LintInternalError(RuntimeError):
    """A rule or the parser failed: the instrument is broken (exit 2)."""


def rule(rule_id: str, severity: str, title: str, hint: str, probe_fire, probe_quiet,
         scope: str = "figure", probe_negative: bool = True):
    """Register the decorated check function as a Rule."""
    def deco(fn):
        RULES.append(Rule(id=rule_id, severity=severity, title=title, hint=hint, check=fn,
                          probe_fire=probe_fire, probe_quiet=probe_quiet, scope=scope,
                          probe_negative=probe_negative))
        return fn
    return deco


ASCII = "text figure"  # the info string of an ASCII figure (TASK R2.5)


def _doc(body: str, lang: str = "mermaid") -> str:
    """A probe document: caption, fence, legend."""
    return f"**Figure 1.** Probe.\n\n```{lang}\n{body}\n```\n\nLegend: probe.\n"


def _hazard_check(*codes: str) -> Callable:
    def check(fig, ctx):
        return [(h.line, f"{h.detail or h.code}: `{h.text}`") for h in fig.hazards if h.code in codes]
    return check


def _fig_line(fig) -> int:
    """Line for a finding about a whole figure: the opening fence, or 0 for a `.mmd` file."""
    return fig.fence.start


def _lines_of(label: str, fallback: str = "") -> list:
    lines = mm.label_lines(label)
    if not lines and fallback:
        lines = mm.label_lines(fallback)
    return lines


# =========================================================================== PARSE: parse hazards

rule("MA-PARSE-01", "error", "Bracket or quote that breaks a node label or subgraph title",
     'Quote the label: id["text (detail)"]; mermaid 10.9, 11.17 and 12.1 reject ( ) [ ] { } and a '
     "leading / or \\ in an unquoted label.",
     _doc("flowchart TB\n  A[API (gateway)] --> B"),
     _doc('flowchart TB\n  A["API (gateway)"] --> B'))(
    _hazard_check("label-unquoted-bracket", "label-leading-slash", "shape-unclosed"))

rule("MA-PARSE-02", "error", "Raw quote inside a quoted label",
     "Write #quot; for a quote inside a quoted label.",
     _doc('flowchart TB\n  A["say "hi" now"] --> B'),
     _doc('flowchart TB\n  A["say #quot;hi#quot; now"] --> B'))(
    _hazard_check("label-quote-inside"))

rule("MA-PARSE-03", "error", "Edge label that the parser rejects",
     'Use the pipe form with a quoted label: A -->|"text (x)"| B.',
     _doc("flowchart TB\n  A -->|x (y)| B"),
     _doc('flowchart TB\n  A -->|"x (y)"| B'))(
    _hazard_check("edge-label-bracket", "edge-label-dotted-dot", "edge-label-double-dash"))

rule("MA-PARSE-04", "error", "Tag-like text that the renderer strips from a label",
     "Write #lt; and #gt; for angle brackets; the tags a label may hold are <br/>, <small>, <b>, <i>.",
     _doc('flowchart TB\n  A["List<T> x"] --> B'),
     _doc('flowchart TB\n  A["List #lt;T#gt;<br/><small>x</small>"] --> B'))(
    _hazard_check("html-tag"))

rule("MA-PARSE-05", "error", "The keyword `end` used as an id",
     "Rename the id (End, done); `end` closes a block and the figure does not parse.",
     _doc("flowchart TB\n  A --> end"),
     _doc("flowchart TB\n  A --> End"))(
    _hazard_check("end-id"))

rule("MA-PARSE-06", "error", "`;` or `#` in a sequence message or note",
     "`;` ends the statement and `#` cuts the text; write #59; and #35;, or reword.",
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: step #1; done"),
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: step #35;1#59; done"))(
    _hazard_check("seq-semicolon", "seq-hash"))

rule("MA-PARSE-07", "error", "`:`, `;` or `#n;` in a state label",
     "Reword the label: `:` fails in mermaid 10.9, `;` creates stray states, `#1;` is a character code.",
     _doc("stateDiagram-v2\n  a --> b : x; y"),
     _doc("stateDiagram-v2\n  a --> b : x and y"))(
    _hazard_check("state-label-colon", "state-label-semicolon", "state-label-entity"))

rule("MA-PARSE-08", "error", "Literal \\n that the renderer prints as text",
     "Break the line with <br/>.",
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: one\\ntwo"),
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: one<br/>two"))(
    _hazard_check("literal-newline"))


@rule("MA-PARSE-09", "error", "Message endpoint that no participant line declares",
      "Declare every participant with an alias, or fix the arrow: `V--xFO` sends to a new "
      "participant FO.",
      _doc("sequenceDiagram\n  participant O as Orchestrator\n  participant V as Validator\n"
           "  V--xFO: error log"),
      _doc("sequenceDiagram\n  participant O as Orchestrator\n  participant V as Validator\n"
           "  V--xO: error log"))
def _check_phantom(fig, ctx):
    seq = fig.sequence
    if seq is None or not any(p.declared for p in seq.participants):
        return []
    return [(p.line, f"`{p.id}` appears in a message or note but no participant line declares it")
            for p in seq.participants if not p.declared]


rule("MA-PARSE-10", "error", "An id glued to an `o` or `x` arrowhead",
     "Put a space after the link: `A --- ops`; `A---ops` draws a circle edge to `ps`.",
     _doc("flowchart TB\n  A---ops"),
     _doc("flowchart TB\n  A --- ops"))(
    _hazard_check("link-head-id"))

rule("MA-PARSE-11", "error", "linkStyle index past the edges defined so far",
     "Count edges from 0 in definition order and put linkStyle after them.",
     _doc("flowchart TB\n  A --> B\n  linkStyle 3 stroke:#546E7A"),
     _doc("flowchart TB\n  A --> B\n  linkStyle 0 stroke:#546E7A"))(
    _hazard_check("linkstyle-range"))

rule("MA-PARSE-12", "error", "`direction` followed by a direction in a subgraph title",
     "Reword the title; `direction LR` in a title is a parse error, quoted or not.",
     _doc('flowchart TB\n  subgraph S["direction LR here"]\n    A\n    B\n  end'),
     _doc('flowchart TB\n  subgraph S["the flow"]\n    A\n    B\n  end'))(
    _hazard_check("subgraph-direction-title"))

rule("MA-PARSE-13", "error", "Deactivating a participant that is not active",
     "Balance activate/deactivate (or +/-); mermaid stops the render on an inactive participant.",
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: x\n  deactivate B"),
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>+B: x\n  B-->>-A: y"))(
    _hazard_check("seq-deactivate-inactive"))


rule("MA-PARSE-14", "error", "Comment after a flowchart statement",
     "Put the `%%` comment on its own line; after a statement it is a parse error.",
     _doc("flowchart TB\n  A --> B %% note"),
     _doc("flowchart TB\n  %% note\n  A --> B"))(
    _hazard_check("inline-comment"))

rule("MA-PARSE-15", "error", "`accTitle` or `accDescr` in a mindmap or sankey-beta figure",
     "Drop accTitle and accDescr from this kind; the caption above the fence carries the title.",
     _doc("mindmap\n  accTitle: Topics\n  root((Guide))\n    Forms"),
     _doc("mindmap\n  root((Guide))\n    Forms"))(
    _hazard_check("acc-unsupported"))

rule("MA-PARSE-16", "error", "State `class` statement that lists an id with a non-ASCII character",
     "Put the class on the state line instead, `Новый:::hold --> done`, or use ASCII ids.",
     _doc("stateDiagram-v2\n  Новый --> done\n  classDef hold fill:#E8F0FB,color:#0F2A47\n  class Новый hold"),
     _doc("stateDiagram-v2\n  Новый:::hold --> done\n  classDef hold fill:#E8F0FB,color:#0F2A47"))(
    _hazard_check("state-class-ids"))

rule("MA-PARSE-17", "error", "Flowchart header line that mermaid cannot read",
     "Write the keyword and one direction (TB, TD, BT, LR or RL) alone on the first line; put each "
     "statement on a line of its own or after `;`.",
     (_doc("flowchart TB A --> B"), _doc("flowchart A --> B")),
     _doc("flowchart TB\n  A --> B"))(
    _hazard_check("header-line"))

rule("MA-PARSE-18", "error", "Character code `#n;` in a flowchart label",
     "Write #35; for `#` and #59; for `;`, or reword: `#1;` renders as character 1, so "
     "\"step #1; done\" shows `step  done`.",
     _doc('flowchart TB\n  A["step #1; done"] --> B'),
     _doc('flowchart TB\n  A["step #35;1#59; done"] --> B'))(
    _hazard_check("label-entity"))


# =========================================================================== SYN: above the 10.9 floor

rule("MA-SYN-01", "error", "`@{ }` shape or participant metadata (mermaid 11 only)",
     "Use the classic shapes: [( )] cylinder, ([ ]) stadium, [[ ]] subroutine; mermaid 10.9 rejects @{ }.",
     _doc('flowchart TB\n  A@{ shape: cyl, label: "x" } --> B'),
     _doc('flowchart TB\n  A[("x")] --> B'))(
    _hazard_check("shape-at"))

rule("MA-SYN-02", "error", "Edge id or edge animation (mermaid 11.5+)",
     "Drop the edge id; mermaid 10.9 rejects `e1@-->` and `animate`.",
     _doc("flowchart TB\n  A e1@--> B"),
     _doc("flowchart TB\n  A --> B"))(
    _hazard_check("edge-id", "animate"))


def _unsupported_kinds(notation: dict) -> list:
    return list(notation.get("lint", {}).get("unsupported_v10_kinds", []))


def _avoid_only_kinds(notation: dict) -> list:
    bad = set(_unsupported_kinds(notation))
    return [k for k in notation.get("kinds", {}).get("avoid", []) if k not in bad]


def _kind_probe(pick: Callable) -> Callable:
    def make(notation):
        kinds = pick(notation)
        keyword = kinds[0] if kinds else "flowchart"
        return _doc(f"{keyword}\n  a")
    return make


@rule("MA-SYN-03", "error", "Diagram kind that mermaid 10.9 cannot render",
      "Use a kind of notation.json `kinds.preferred` or `kinds.allowed`, or a table.",
      _kind_probe(_unsupported_kinds),
      _doc("flowchart TB\n  A --> B"))
def _check_kind_floor(fig, ctx):
    if fig.kind == "ascii":
        return []
    if fig.keyword in _unsupported_kinds(ctx.notation):
        return [(_fig_line(fig), f"`{fig.keyword}` needs mermaid 11 or newer")]
    return []


@rule("MA-SYN-04", "warn", "Diagram kind the skill avoids",
      "Use a kind of notation.json `kinds.preferred` or `kinds.allowed`, or a table.",
      _kind_probe(_avoid_only_kinds),
      _doc("flowchart TB\n  A --> B"))
def _check_kind_avoid(fig, ctx):
    if fig.kind != "ascii" and fig.keyword in _avoid_only_kinds(ctx.notation):
        return [(_fig_line(fig), f"`{fig.keyword}` is in notation.json `kinds.avoid`")]
    return []


rule("MA-SYN-05", "error", "Gantt `vert` marker (mermaid 10.9 stops the render)",
     "Drop the vertical marker; state the date in the text or a milestone.",
     _doc("gantt\n  dateFormat x\n  axisFormat %Q\n  todayMarker off\n  section S\n  t1 :a, 0, 3ms\n"
          "  marker :vert, v1, 2, 0ms"),
     _doc("gantt\n  dateFormat x\n  axisFormat %Q\n  todayMarker off\n  section S\n  t1 :a, 0, 3ms"))(
    _hazard_check("gantt-vert"))

rule("MA-SYN-06", "error", "Sequence syntax above the 10.9 floor",
     "Use the classic arrows and an integer `autonumber`; draw `A<<->>B` as two messages.",
     _doc("sequenceDiagram\n  participant A\n  participant B\n  autonumber 1.1 0.1\n  A->>B: x"),
     _doc("sequenceDiagram\n  participant A\n  participant B\n  autonumber\n  A->>B: x"))(
    _hazard_check("seq-syntax-above-floor"))


@rule("MA-SYN-07", "error", "Unknown diagram keyword, or no diagram in the fence",
      "Start the fence with a diagram keyword: flowchart, sequenceDiagram, stateDiagram-v2, gantt, "
      "erDiagram.",
      (_doc("foobar\n  a --> b"), _doc("%% only a comment")),
      _doc("flowchart TB\n  A --> B"))
def _check_unknown(fig, ctx):
    if fig.kind != "unknown":
        return []
    if fig.keyword:
        return [(_fig_line(fig), f"`{fig.keyword}` is not a diagram keyword of mermaid 10.9–12.1")]
    # an empty fence, or one with only comments or settings: every viewer shows an error box
    return [(_fig_line(fig), "the fence holds no diagram keyword; mermaid detects no diagram")]


rule("MA-SYN-08", "error", "Styling that mermaid 10.9 rejects in an ER, class or requirement diagram",
     "Drop classDef, class, style and ::: from ER and requirement diagrams, and classDef from class "
     "diagrams; a table or the legend carries the category.",
     _doc("erDiagram\n  CUSTOMER ||--o{ ORDER : places\n  classDef hot fill:#FFF4E0,color:#4A2C00"),
     _doc("erDiagram\n  CUSTOMER ||--o{ ORDER : places"))(
    _hazard_check("styling-v10"))

rule("MA-SYN-09", "error", "Text after `timeline` on its header line",
     "Write `timeline` alone on its line; mermaid 10.9 draws the text as a first period, and 11.17 "
     "reads `TD` as a direction.",
     _doc("timeline TD\n  2025 Q1 : v1 search"),
     _doc("timeline\n  2025 Q1 : v1 search"))(
    _hazard_check("timeline-header"))


# =========================================================================== SET: settings

@rule("MA-SET-01", "error", "Malformed init directive (mermaid ignores it without a diagnostic)",
      "Make the directive strict JSON: double quotes, no trailing comma.",
      _doc('%%{init: {"look": "classic",}}%%\nflowchart TB\n  A --> B'),
      _doc('%%{init: {"look": "classic"}}%%\nflowchart TB\n  A --> B'))
def _check_directive(fig, ctx):
    return [(s.line, s.error) for s in fig.settings_blocks if s.form == "directive" and s.error]


@rule("MA-SET-02", "error", "Frontmatter that does not parse or loses its settings",
      "Fix the YAML: two spaces per level, no tabs, one entry per key, `key: value` with a space, "
      "colours in quotes; a YAML error stops the render, and a lost value changes it silently.",
      _doc("---\nconfig:\n  look: classic\n    layout: dagre\n---\nflowchart TB\n  A --> B"),
      _doc("---\nconfig:\n  look: classic\n  layout: dagre\n---\nflowchart TB\n  A --> B"))
def _check_frontmatter(fig, ctx):
    return [(s.line, s.error) for s in fig.settings_blocks if s.form == "frontmatter" and s.error]


def _theme_pattern(notation: dict):
    return re.compile(notation.get("lint", {}).get("theme_value_pattern", r"^[\d \"#%(),.;A-Za-z]+$"))


@rule("MA-SET-03", "error", "themeVariables value that the sanitizer blanks",
      "Mermaid blanks a theme value holding -, _, : or /; drop the value (no font family).",
      _doc('%%{init: {"themeVariables": {"fontFamily": "Helvetica, Arial, sans-serif"}}}%%\n'
           "flowchart TB\n  A --> B"),
      _doc('%%{init: {"themeVariables": {"fontSize": "14px"}}}%%\nflowchart TB\n  A --> B'))
def _check_sanitizer(fig, ctx):
    pattern = _theme_pattern(ctx.notation)
    out = []
    for s in fig.settings_blocks:
        tv = (s.config or {}).get("themeVariables")
        if not isinstance(tv, dict):
            continue
        for key, value in tv.items():
            if isinstance(value, str) and not pattern.match(value):
                out.append((s.line, f"themeVariables.{key} = {value!r} is blanked by mermaid's sanitizer"))
    return out


@rule("MA-SET-04", "error", "Top-level fontFamily (mermaid 10.9 drops every other theme variable)",
      "Remove the top-level fontFamily; settings lines set no font (TASK D15).",
      _doc('%%{init: {"fontFamily": "Helvetica"}}%%\nflowchart TB\n  A --> B'),
      _doc('%%{init: {"themeVariables": {"fontSize": "14px"}}}%%\nflowchart TB\n  A --> B'))
def _check_toplevel_font(fig, ctx):
    return [(s.line, "a top-level `fontFamily` replaces the theme variables in mermaid 10.9")
            for s in fig.settings_blocks if isinstance(s.config, dict) and "fontFamily" in s.config]


@rule("MA-SET-05", "warn", "Fixed `theme` key (light text on GitHub's dark page)",
      "Remove `theme`; the viewer then picks a light or a dark theme (TASK R4.2).",
      _doc('%%{init: {"theme": "base", "look": "classic"}}%%\nflowchart TB\n  A --> B'),
      _doc('%%{init: {"look": "classic"}}%%\nflowchart TB\n  A --> B'))
def _check_theme(fig, ctx):
    return [(s.line, f"`theme: {s.config.get('theme')}` fixes the colours in dark mode")
            for s in fig.settings_blocks if isinstance(s.config, dict) and "theme" in s.config]


_SETTINGS_KEY = {"flowchart": "flowchart", "state": "state", "sequence": "sequence", "er": "er",
                 "gantt": "gantt", "class": "class", "requirementDiagram": "requirement"}


def _notation_settings(notation: dict, kind: str) -> Optional[dict]:
    line = notation.get("settings", {}).get(_SETTINGS_KEY.get(kind, ""), "")
    m = re.match(r"^%%\{init:\s*(.*)\}%%$", line.strip(), re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def _settings_probe(fire: bool) -> Callable:
    def make(notation):
        line = notation.get("settings", {}).get("flowchart", "")
        body = "flowchart TB\n  A --> B"
        return _doc(body if fire else f"{line}\n{body}")
    return make


@rule("MA-SET-06", "warn", "Settings line without the pinned layout and look",
      "Copy the settings line of the kind from notation.json; it pins dagre and classic, which "
      "mermaid 12 changed.",
      _settings_probe(True), _settings_probe(False))
def _check_pinned(fig, ctx):
    want = _notation_settings(ctx.notation, fig.kind)
    if not want:
        return []
    required = {k: want[k] for k in ("layout", "look") if k in want}
    if not required:
        return []
    have = fig.settings.config if fig.settings and isinstance(fig.settings.config, dict) else {}
    missing = [f'"{k}": "{v}"' for k, v in required.items() if have.get(k) != v]
    if missing:
        line = fig.settings.line if fig.settings else _fig_line(fig)
        return [(line, "missing " + ", ".join(missing))]
    return []


def _settings_signature(fig, notation: Optional[dict] = None) -> str:
    """The settings of a figure as one comparable string. Keys that notation.json `lint`
    `settings_per_chart_keys` lists for the kind (the width and padding of one gantt chart) may
    differ between figures, so they are left out."""
    s = fig.settings
    if s is None:
        return "none"
    if isinstance(s.config, dict):
        config = json.loads(json.dumps(s.config))
        per_chart = (notation or {}).get("lint", {}).get("settings_per_chart_keys", {})
        for section, keys in per_chart.items():
            if section == fig.kind and isinstance(config.get(section), dict):
                for key in keys:
                    config[section].pop(key, None)
        return json.dumps(config, sort_keys=True)
    return " ".join(s.raw.split())


@rule("MA-SET-07", "warn", "Figures of one kind with different settings in one document",
      "Use one settings line per kind in a document (TASK R3.8); the width and padding of one gantt "
      "chart may differ.",
      lambda n: (_doc("flowchart TB\n  A --> B") + "\n"
                 + _doc(n.get("settings", {}).get("flowchart", "") + "\nflowchart TB\n  C --> D")),
      lambda n: (_doc(n.get("settings", {}).get("flowchart", "") + "\nflowchart TB\n  A --> B") + "\n"
                 + _doc(n.get("settings", {}).get("flowchart", "") + "\nflowchart TB\n  C --> D")),
      scope="document")
def _check_settings_consistency(figures, ctx):
    first: dict = {}
    out = []
    for fig in figures:
        if fig.kind in ("ascii", "unknown"):
            continue
        sig = _settings_signature(fig, ctx.notation)
        if fig.kind not in first:
            first[fig.kind] = (sig, fig)
        elif sig != first[fig.kind][0]:
            out.append((_fig_line(fig), f"settings differ from the {fig.kind} figure at line "
                                        f"{_fig_line(first[fig.kind][1])}"))
    return out


# =========================================================================== ID

@rule("MA-ID-01", "error", "Two edges that mermaid 12 gives one edge id (it stops the render)",
      "Rename the ids without `_`: `a --> b_c` and `a_b --> c` both become L_a_b_c_0.",
      _doc("flowchart TB\n  a --> b_c\n  a_b --> c"),
      _doc("flowchart TB\n  a --> bc\n  ab --> c"))
def _check_edge_ids(fig, ctx):
    fc = fig.flowchart
    if fc is None:
        return []
    seen: dict = {}
    out = []
    for edge, eid in zip(fc.edges, mm.flowchart_edge_ids(fc)):
        prev = seen.get(eid)
        if prev is not None and (prev.src, prev.dst) != (edge.src, edge.dst):
            out.append((edge.line, f"`{prev.src} --> {prev.dst}` and `{edge.src} --> {edge.dst}` "
                                   f"share the edge id {eid}"))
        else:
            seen.setdefault(eid, edge)
    return out


def _figure_ids(fig) -> list:
    """(id, line) of every id the author wrote."""
    out = []
    if fig.flowchart:
        out += [(n.id, n.line) for n in fig.flowchart.nodes.values()]
        out += [(s.id, s.line) for s in fig.flowchart.subgraphs.values() if not s.auto_id]
    if fig.state:
        out += [(s.id, s.line) for s in fig.state.states.values()]
    if fig.sequence:
        out += [(p.id, p.line) for p in fig.sequence.participants]
    if fig.gantt:
        out += [(t.id, t.line) for t in fig.gantt.tasks if t.id]
    return out


@rule("MA-ID-02", "warn", "Id outside [A-Za-z0-9]",
      "Use letters and digits for ids and put the name in the label: apiGw[\"api-gw\"].",
      _doc("flowchart TB\n  api-gw --> db"),
      _doc("flowchart TB\n  apiGw --> db"))
def _check_id_shape(fig, ctx):
    pattern = re.compile(ctx.notation.get("lint", {}).get("id_pattern", r"^[A-Za-z0-9]+$"))
    out, seen = [], set()
    for ident, line in _figure_ids(fig):
        if ident not in seen and not pattern.match(ident):
            seen.add(ident)
            out.append((line, f"id `{ident}`"))
    return out


# =========================================================================== BUDGET

#: Budget key of notation.json per kind that the model counts in `Figure.counts`.
_COUNT_BUDGETS = {"class": "class", "mindmap": "mindmap", "timeline": "timeline", "journey": "journey",
                  "gitGraph": "gitgraph"}


def _budget_values(fig) -> list:
    """(kind key, metric, value) for the budgets of notation.json."""
    counts = getattr(fig, "counts", None)
    if counts and fig.kind in _COUNT_BUDGETS:
        return [(_COUNT_BUDGETS[fig.kind], metric, value) for metric, value in counts.items()]
    if fig.flowchart:
        fc = fig.flowchart
        return [("flowchart", "nodes", len(fc.nodes)),
                ("flowchart", "edges", sum(1 for e in fc.edges if e.style != "invisible"))]
    if fig.sequence:
        seq = fig.sequence
        return [("sequence", "participants", len(seq.participants)),
                ("sequence", "messages", len(seq.messages)),
                ("sequence", "phase_blocks", sum(1 for b in seq.blocks if b.kind == "rect"))]
    if fig.state:
        return [("state", "states", len(fig.state.states))]
    if fig.gantt:
        return [("gantt", "bars", sum(1 for t in fig.gantt.tasks if "vert" not in t.tags))]
    if fig.er:
        return [("er", "entities", len(fig.er.entities))]
    return []


def _budget_findings(fig, ctx, hard: bool) -> list:
    out = []
    budgets = ctx.notation.get("budgets", {})
    for kind, metric, value in _budget_values(fig):
        pair = budgets.get(kind, {}).get(metric)
        if not pair:
            continue
        soft, hard_limit = pair
        if hard and value > hard_limit:
            out.append((_fig_line(fig), f"{metric}: {value} > hard budget {hard_limit}; split the figure"))
        elif not hard and soft < value <= hard_limit:
            out.append((_fig_line(fig), f"{metric}: {value} > soft budget {soft}; aggregate or split"))
    return out


def _chain(n: int, direction: str = "TB") -> str:
    lines = [f"flowchart {direction}"]
    lines += [f"  N{k} --> N{k + 1}" for k in range(1, n)]
    return "\n".join(lines)


def _budget_probe(which: str) -> Callable:
    def make(notation):
        soft, hard = notation["budgets"]["flowchart"]["nodes"]
        n = {"soft-fire": soft + 1, "soft-quiet": soft, "hard-fire": hard + 1, "hard-quiet": hard}[which]
        return _doc(_chain(n))
    return make


@rule("MA-BUDGET-01", "warn", "Over the soft budget",
      "Aggregate (one node for a group, members on its second line) or split; keep the figure only "
      "if it passes the render check.",
      _budget_probe("soft-fire"), _budget_probe("soft-quiet"))
def _check_soft_budget(fig, ctx):
    return _budget_findings(fig, ctx, hard=False)


@rule("MA-BUDGET-02", "error", "Over the hard budget",
      "Split the figure by concern.",
      _budget_probe("hard-fire"), _budget_probe("hard-quiet"))
def _check_hard_budget(fig, ctx):
    return _budget_findings(fig, ctx, hard=True)


# =========================================================================== FLOW: flowchart structure

def _visible_edges(fc) -> list:
    return [e for e in fc.edges if e.style != "invisible"]


def _decision_flow(fc) -> bool:
    """A flowchart that holds a rhombus (decision) node: it may hold one edge per direction."""
    return any(n.shape == "rhombus" for n in fc.nodes.values())


def _edge_directions(e) -> set:
    """The ordered pairs an edge claims: one for an arrow, both for `<-->` and an open link."""
    return {(e.src, e.dst)} if e.arrow == "->" else {(e.src, e.dst), (e.dst, e.src)}


@rule("MA-FLOW-01", "warn", "More than one edge between one pair of nodes",
      "Merge parallel relations into one label (`claim · finish`), or one two-headed edge; a "
      "decision flow may hold one edge per direction.",
      _doc("flowchart TB\n  A --> B\n  B --> A"),
      _doc("flowchart TB\n  A <--> B"))
def _check_duplicate_edges(fig, ctx):
    """TASK R3.3: at most one edge per unordered node pair; in a flowchart that holds a rhombus
    node, at most one edge per direction."""
    if fig.flowchart is None:
        return []
    per_direction = _decision_flow(fig.flowchart)
    seen: dict = {}  # unordered pair -> [claimed ordered pairs, first line]
    out = []
    for e in _visible_edges(fig.flowchart):
        key = frozenset((e.src, e.dst))
        dirs = _edge_directions(e)
        if key not in seen:
            seen[key] = [set(dirs), e.line]
            continue
        claimed, first = seen[key]
        if per_direction and not dirs & claimed:
            claimed |= dirs
            continue
        where = " in this direction" if per_direction else ""
        out.append((e.line, f"`{e.src}` and `{e.dst}` are already joined{where} at line {first}"))
    return out


@rule("MA-FLOW-02", "error", "Edge to a subgraph id",
      "Draw the node-to-node edges the text states; mermaid ends a subgraph edge on the box "
      "border, and a reader takes it for a relation of the member nearest that end.",
      _doc('flowchart TB\n  subgraph S["Group"]\n    A\n    B\n  end\n  C --> S'),
      _doc('flowchart TB\n  subgraph S["Group"]\n    A\n    B\n  end\n  C --> A'))
def _check_subgraph_edge(fig, ctx):
    fc = fig.flowchart
    if fc is None:
        return []
    return [(e.line, f"`{e.src} --> {e.dst}` ends on subgraph `{x}`")
            for e in fc.edges for x in (e.src, e.dst) if x in fc.subgraphs]


@rule("MA-FLOW-03", "warn", "Subgraph with fewer than two members",
      "Drop the subgraph and put its role on the node's second line.",
      _doc('flowchart TB\n  subgraph S["Group"]\n    A\n  end\n  B --> A'),
      _doc('flowchart TB\n  subgraph S["Group"]\n    A\n    C\n  end\n  B --> A'))
def _check_small_subgraph(fig, ctx):
    fc = fig.flowchart
    if fc is None:
        return []
    return [(s.line, f"subgraph `{s.title or s.id}` holds {len(s.members)} member(s)")
            for s in fc.subgraphs.values() if len(s.members) < 2]


_NUMBERED = re.compile(r"^\s*[(\[]?\d{1,3}[.):\]](?!\d)")


def _numbered_probe(fire: bool) -> Callable:
    def make(notation):
        n = max(2, int(notation.get("lint", {}).get("numbered_edge_labels_min", 2)))
        lines = ["flowchart TB"]
        for k in range(1, n + 1):
            label = f"{k}. step" if fire else "step"
            lines.append(f'  N{k} -->|"{label}"| N{k + 1}')
        return _doc("\n".join(lines))
    return make


@rule("MA-FLOW-04", "warn", "Numbered edge labels: an order drawn in a structure figure",
      "Draw the order as a sequence diagram, or drop the numbers.",
      _numbered_probe(True), _numbered_probe(False))
def _check_numbered(fig, ctx):
    fc = fig.flowchart
    if fc is None:
        return []
    numbered = [e for e in fc.edges if _NUMBERED.match(" ".join(mm.label_lines(e.label)))]
    minimum = int(ctx.notation.get("lint", {}).get("numbered_edge_labels_min", 2))
    if len(numbered) >= minimum:
        return [(numbered[0].line, f"{len(numbered)} edge labels start with a number: "
                                   + ", ".join(f"`{e.label}`" for e in numbered[:4]))]
    return []


@rule("MA-FLOW-05", "warn", "Non-planar flowchart: every drawing has a crossing",
      "Aggregate one side (one node for the group), split the figure, or use a table.",
      _doc("flowchart TB\n  A1 --> B1 & B2 & B3\n  A2 --> B1 & B2 & B3\n  A3 --> B1 & B2 & B3"),
      _doc("flowchart TB\n  A1 --> B1 & B2 & B3\n  A2 --> B1 & B2\n  A3 --> B3"))
def _check_planarity(fig, ctx):
    fc = fig.flowchart
    if fc is None:
        return []
    hard_nodes = ctx.notation.get("budgets", {}).get("flowchart", {}).get("nodes", [0, 0])[1]
    hard_edges = ctx.notation.get("budgets", {}).get("flowchart", {}).get("edges", [0, 0])[1]
    edges = _visible_edges(fc)
    if len(fc.nodes) > hard_nodes or len(edges) > hard_edges:
        return []
    planar, reason = planarity.is_planar([(e.src, e.dst) for e in edges])
    if planar:
        return []
    return [(_fig_line(fig), f"the graph is not planar ({reason})")]


def _lr_probe(direction: str) -> Callable:
    def make(notation):
        n = int(notation.get("structure", {}).get("lr_max_nodes", 6)) + 1
        return _doc(_chain(n, direction))
    return make


@rule("MA-FLOW-06", "warn", "Flowchart over the node limit that is not laid out top to bottom",
      "Lay the figure out top to bottom (TASK R3.4); a wide LR figure shrinks its text in a 900 px "
      "column.",
      (_lr_probe("LR"), _lr_probe("BT")), _lr_probe("TB"))
def _check_lr(fig, ctx):
    fc = fig.flowchart
    if fc is None or fc.direction in ("TB", "TD"):
        return []
    limit = int(ctx.notation.get("structure", {}).get("lr_max_nodes", 6))
    if len(fc.nodes) > limit:
        return [(_fig_line(fig), f"{fc.direction} with {len(fc.nodes)} nodes > {limit}")]
    return []


rule("MA-FLOW-07", "warn", "`style` line that draws a node no other statement defines",
     "Fix the id in the `style` line, or drop the line; mermaid draws a box for any id a `style` "
     "line names.",
     _doc("flowchart TB\n  A --> B\n  style PHANTOM stroke:#546E7A"),
     _doc("flowchart TB\n  A --> B\n  style A stroke:#546E7A"))(
    _hazard_check("style-node"))

rule("MA-FLOW-08", "warn", "`linkStyle` in a flowchart",
     "Drop linkStyle (flowchart.md §2 rule 7): under `linkStyle default` 10.9.8 skips dotted and "
     "thick edges, while 12.1.0 styles every edge. Edge style and the legend carry the meaning.",
     _doc("flowchart TB\n  A --> B\n  linkStyle 0 stroke:#C62828"),
     _doc("flowchart TB\n  A ==> B"))(
    _hazard_check("linkstyle"))

rule("MA-FLOW-09", "warn", "`direction` inside a subgraph",
     "Drop the subgraph's `direction` (flowchart.md §4 rule 8): mermaid ignores it once a member "
     "links outside the subgraph.",
     _doc('flowchart TB\n  subgraph S["Group"]\n    direction LR\n    A --> B\n  end'),
     _doc('flowchart TB\n  subgraph S["Group"]\n    A --> B\n  end'))(
    _hazard_check("subgraph-direction"))


# =========================================================================== STATE

@rule("MA-STATE-01", "error", "Transition across a composite state boundary",
      "Use a flat graph with classes, or attach the transition to the composite itself.",
      _doc("stateDiagram-v2\n  state W {\n    x --> y\n  }\n  a --> x"),
      _doc("stateDiagram-v2\n  state W {\n    x --> y\n  }\n  a --> W"))
def _check_composite_cross(fig, ctx):
    sd = fig.state
    if sd is None:
        return []
    out = []
    for t in sd.transitions:
        if "[*]" in (t.src, t.dst) or t.src not in sd.states or t.dst not in sd.states:
            continue
        ps, pd = sd.states[t.src].parent, sd.states[t.dst].parent
        if ps != pd:
            inner = [p for p in (ps, pd) if p]
            out.append((t.line, f"`{t.src} --> {t.dst}` crosses the boundary of "
                                + " and ".join(f"`{p}`" for p in inner)))
    return out


rule("MA-STATE-02", "error", "`style` in a state diagram",
     "Use classDef and class; mermaid 10.9 rejects `style` or turns it into stray states.",
     _doc("stateDiagram-v2\n  a --> b\n  style a fill:#FFFFFF"),
     _doc("stateDiagram-v2\n  a --> b\n  classDef c fill:#FFFFFF,color:#263238\n  class a c"))(
    _hazard_check("state-style"))


def _state_end(sid: str, scope: Optional[str], role: str) -> str:
    """A transition end as a node: `[*]` is a start or an end node of its composite."""
    return f"[*] {role} {scope or ''}" if sid == "[*]" else sid


@rule("MA-STATE-03", "warn", "Two transitions in one direction between one pair of states",
      "Merge them into one label (`claim · finish`); a state diagram holds one transition per "
      "direction (TASK R3.3).",
      _doc("stateDiagram-v2\n  a --> b : go\n  a --> b : retry"),
      _doc("stateDiagram-v2\n  a --> b : go\n  b --> a : back"))
def _check_duplicate_transitions(fig, ctx):
    sd = fig.state
    if sd is None:
        return []
    seen: dict = {}
    out = []
    for t in sd.transitions:
        key = (_state_end(t.src, t.scope, "start"), _state_end(t.dst, t.scope, "end"))
        if key in seen:
            out.append((t.line, f"`{t.src} --> {t.dst}` repeats the transition at line {seen[key]}"))
        else:
            seen[key] = t.line
    return out


rule("MA-STATE-04", "warn", "Quotes around a state transition label or description",
     "Drop the quotes: mermaid prints them. Quotes belong only in `state \"name\" as id`.",
     _doc('stateDiagram-v2\n  a --> b : "go now"'),
     _doc("stateDiagram-v2\n  a --> b : go now"))(
    _hazard_check("state-label-quoted"))


# =========================================================================== SEQ

rule("MA-SEQ-01", "error", "classDef, class or style in a sequence diagram",
     "Sequence diagrams take no classes; use box and rect, or nothing.",
     _doc("sequenceDiagram\n  participant A\n  A->>A: x\n  classDef c fill:#FFFFFF"),
     _doc("sequenceDiagram\n  participant A\n  A->>A: x"))(
    _hazard_check("seq-styling"))


def _skip_probe(fire: bool) -> Callable:
    def make(notation):
        n = int(notation["labels"]["edge_label_chars_max"]) + 1
        label = "x" * n
        target = "C" if fire else "B"
        return _doc("sequenceDiagram\n  participant A\n  participant B\n  participant C\n"
                    f"  A->>{target}: {label}")
    return make


@rule("MA-SEQ-02", "warn", "Long label on a message that passes a lifeline",
      "Order participants so the pair is adjacent, or shorten the label to an edge label's length.",
      _skip_probe(True), _skip_probe(False))
def _check_skip(fig, ctx):
    seq = fig.sequence
    if seq is None:
        return []
    limit = int(ctx.notation["labels"]["edge_label_chars_max"])
    pos = {p.id: k for k, p in enumerate(seq.participants)}
    out = []
    for m in seq.messages:
        if m.src not in pos or m.dst not in pos:
            continue
        passed = abs(pos[m.src] - pos[m.dst]) - 1
        longest = max((mm.char_count(x) for x in mm.label_lines(m.text)), default=0)
        if passed >= 1 and longest > limit:
            out.append((m.line, f"`{m.src}->{m.dst}` passes {passed} lifeline(s) with a "
                                f"{longest}-character label (limit {limit})"))
    return out


def _phase_probe(fire: bool) -> Callable:
    def make(notation):
        colour = "#E8F0FB" if fire else notation["palette"]["sequence"]["phase"]
        return _doc(f"sequenceDiagram\n  participant A\n  participant B\n  rect {colour}\n    A->>B: x\n  end")
    return make


rule("MA-SEQ-03", "error", "Hex colour after `rect` or `box` in a sequence diagram",
     "Write the colour as rgba(), from notation.json palette.sequence (`box`, `phase`).",
     _phase_probe(True), _phase_probe(False))(
    _hazard_check("seq-hex-colour"))


# =========================================================================== LABEL

def _label_probe(where: str, key: str, fire: bool) -> Callable:
    def make(notation):
        n = int(notation["labels"][key]) + (1 if fire else 0)
        text = "x" * n
        bodies = {
            "node1": f'flowchart TB\n  A["{text}"] --> B',
            "node2": f'flowchart TB\n  A["short<br/><small>{text}</small>"] --> B',
            "edge": f'flowchart TB\n  A -->|"{text}"| B',
            "message": f"sequenceDiagram\n  participant A\n  participant B\n  A->>B: {text}",
            "note": f"sequenceDiagram\n  participant A\n  Note over A: {text}",
            "gantt": ("gantt\n  dateFormat x\n  axisFormat %Q\n  todayMarker off\n  section S\n"
                      f"  {text} :a, 0, 3ms"),
            "participant": f"sequenceDiagram\n  participant A as {text}\n  participant B\n  A->>B: x",
        }
        return _doc(bodies[where])
    return make


def _lines_probe(where: str, key: str, fire: bool) -> Callable:
    """A probe whose label has one line more than the limit (fire) or exactly the limit."""
    def make(notation):
        n = int(notation["labels"][key]) + (1 if fire else 0)
        text = "<br/>".join(f"line {k}" for k in range(1, n + 1))
        bodies = {
            "node": f'flowchart TB\n  A["{text}"] --> B',
            "message": f"sequenceDiagram\n  participant A\n  participant B\n  A->>B: {text}",
            "note": f"sequenceDiagram\n  participant A\n  Note over A: {text}",
            "edge": f"flowchart TB\n  A -->|{text}| B",
            "participant": f"sequenceDiagram\n  participant A as {text}\n  participant B\n  A->>B: x",
        }
        return _doc(bodies[where])
    return make


def _node_label_items(fig) -> list:
    """(line, id, visible lines) for every node-like element: flowchart nodes and subgraph
    titles, states, and ER entities by the name their box shows (other-kinds.md rule 6)."""
    out = []
    if fig.flowchart:
        out += [(n.line, n.id, _lines_of(n.label, n.id)) for n in fig.flowchart.nodes.values()]
        out += [(s.line, s.id, _lines_of(s.title, s.id)) for s in fig.flowchart.subgraphs.values()]
    if fig.state:
        out += [(s.line, s.id, _lines_of(s.label, s.id)) for s in fig.state.states.values()]
    if fig.er:
        out += [(e.line, e.name, _lines_of(e.alias, e.name)) for e in fig.er.entities.values()]
    return out


def _edge_label_items(fig) -> list:
    out = []
    if fig.flowchart:
        out += [(e.line, e.label) for e in fig.flowchart.edges if e.label]
    if fig.state:
        out += [(t.line, t.label) for t in fig.state.transitions if t.label]
    if fig.er:
        out += [(r.line, r.label) for r in fig.er.relations if r.label]
    return out


@rule("MA-LABEL-01", "warn", "Node label first line over the character limit",
      "Keep the name to about 4 words; move the role to a <small> second line.",
      _label_probe("node1", "node_line1_chars_max", True), _label_probe("node1", "node_line1_chars_max", False))
def _check_node_line1(fig, ctx):
    limit = int(ctx.notation["labels"]["node_line1_chars_max"])
    return [(line, f"`{nid}`: {mm.char_count(lines[0])} characters > {limit}")
            for line, nid, lines in _node_label_items(fig) if lines and mm.char_count(lines[0]) > limit]


@rule("MA-LABEL-02", "warn", "Node label second line over the character limit",
      "Shorten the second line; detail belongs in the text.",
      _label_probe("node2", "node_second_line_chars_max", True),
      _label_probe("node2", "node_second_line_chars_max", False))
def _check_node_line2(fig, ctx):
    limit = int(ctx.notation["labels"]["node_second_line_chars_max"])
    out = []
    for line, nid, lines in _node_label_items(fig):
        for extra in lines[1:]:
            if mm.char_count(extra) > limit:
                out.append((line, f"`{nid}`: a line of {mm.char_count(extra)} characters > {limit}"))
    return out


@rule("MA-LABEL-03", "warn", "Edge label over the character limit",
      "Keep an edge label to about 3 words; the payload goes in the text.",
      _label_probe("edge", "edge_label_chars_max", True), _label_probe("edge", "edge_label_chars_max", False))
def _check_edge_label(fig, ctx):
    limit = int(ctx.notation["labels"]["edge_label_chars_max"])
    out = []
    for line, label in _edge_label_items(fig):
        for text in mm.label_lines(label):
            if mm.char_count(text) > limit:
                out.append((line, f"`{text}`: {mm.char_count(text)} characters > {limit}"))
    return out


@rule("MA-LABEL-04", "warn", "Sequence message over the character limit",
      "Name the call; parameters and payloads go in the text's table.",
      _label_probe("message", "sequence_message_chars_max", True),
      _label_probe("message", "sequence_message_chars_max", False))
def _check_message(fig, ctx):
    if fig.sequence is None:
        return []
    limit = int(ctx.notation["labels"]["sequence_message_chars_max"])
    out = []
    for m in fig.sequence.messages:
        for text in mm.label_lines(m.text):
            if mm.char_count(text) > limit:
                out.append((m.line, f"{mm.char_count(text)} characters > {limit}"))
    return out


@rule("MA-LABEL-05", "warn", "Note line over the character limit",
      "Break the note with <br/> or move it to the text.",
      _label_probe("note", "note_chars_max", True), _label_probe("note", "note_chars_max", False))
def _check_note(fig, ctx):
    limit = int(ctx.notation["labels"]["note_chars_max"])
    notes = (fig.sequence.notes if fig.sequence else []) + (fig.state.notes if fig.state else [])
    out = []
    for n in notes:
        for text in mm.label_lines(n.text):
            if mm.char_count(text) > limit:
                out.append((n.line, f"{mm.char_count(text)} characters > {limit}"))
    return out


@rule("MA-LABEL-06", "warn", "Gantt task label over the character limit",
      "Shorten the task label; the plan table holds the full title.",
      _label_probe("gantt", "gantt_label_chars_max", True), _label_probe("gantt", "gantt_label_chars_max", False))
def _check_gantt_label(fig, ctx):
    if fig.gantt is None:
        return []
    limit = int(ctx.notation["labels"]["gantt_label_chars_max"])
    return [(t.line, f"`{t.label}`: {mm.char_count(t.label)} characters > {limit}")
            for t in fig.gantt.tasks if mm.char_count(t.label) > limit]


_LETTERS = re.compile(r"[^\W\d_]+")


def _drawn_names(fig) -> set:
    """The words of the names a figure draws: each letter run of a node, state, entity or group
    label, in the case the label writes it."""
    return {word for _line, _id, lines in _node_label_items(fig) for text in lines
            for word in _LETTERS.findall(text)}


def _starts_uppercase(label: str, acronym_max: int, names: frozenset = frozenset()) -> bool:
    """True when the first word of *label* starts with a capital letter and is neither an
    acronym of at most *acronym_max* letters nor a word of *names* (SKILL.md Step 5.3: a name
    keeps its case)."""
    lines = mm.label_lines(label)
    if not lines:
        return False
    text = lines[0]
    start = next((k for k, ch in enumerate(text) if ch.isupper() or ch.islower()), None)
    if start is None or text[start].islower():
        return False
    m = _LETTERS.match(text[start:])
    word = m.group(0) if m else ""
    if word and not any(ch.islower() for ch in word) and len(word) <= acronym_max:
        return False
    return word not in names


@rule("MA-LABEL-07", "warn", "Edge label that starts with a capital letter in a cased script",
      "Write edge labels lowercase: `reads`, not `Reads`; acronyms and the names the figure's "
      "boxes show keep their case.",
      _doc("flowchart TB\n  A -->|Sends data| B"),
      _doc("flowchart TB\n  A -->|sends SQL| B\n  B -->|Kafka topic| K[Kafka]"))
def _check_edge_case(fig, ctx):
    acronym_max = int(ctx.notation.get("lint", {}).get("acronym_max_chars", 5))
    names = frozenset(_drawn_names(fig))
    return [(line, f"`{label}`") for line, label in _edge_label_items(fig)
            if _starts_uppercase(label, acronym_max, names)]


@rule("MA-LABEL-08", "warn", "Node label with more lines than the limit",
      "Keep a name line and one <small> role line; further detail belongs in the text.",
      _lines_probe("node", "node_label_lines_max", True), _lines_probe("node", "node_label_lines_max", False))
def _check_node_lines(fig, ctx):
    limit = int(ctx.notation["labels"]["node_label_lines_max"])
    return [(line, f"`{nid}`: {len(lines)} lines > {limit}")
            for line, nid, lines in _node_label_items(fig) if len(lines) > limit]


@rule("MA-LABEL-09", "warn", "Sequence message with more lines than the limit",
      "Name the call in a few words; parameters and payloads go in the text's table.",
      _lines_probe("message", "sequence_message_lines_max", True),
      _lines_probe("message", "sequence_message_lines_max", False))
def _check_message_lines(fig, ctx):
    if fig.sequence is None:
        return []
    limit = int(ctx.notation["labels"]["sequence_message_lines_max"])
    return [(m.line, f"{len(mm.label_lines(m.text))} lines > {limit}")
            for m in fig.sequence.messages if len(mm.label_lines(m.text)) > limit]


@rule("MA-LABEL-10", "warn", "Participant name over the character limit",
      "Shorten the display name (`participant GW as Gateway`); the full name goes in the text.",
      _label_probe("participant", "participant_chars_max", True),
      _label_probe("participant", "participant_chars_max", False))
def _check_participant(fig, ctx):
    if fig.sequence is None:
        return []
    limit = int(ctx.notation["labels"]["participant_chars_max"])
    out = []
    for p in fig.sequence.participants:
        for text in _lines_of(p.label, p.id):
            if mm.char_count(text) > limit:
                out.append((p.line, f"`{p.id}`: `{text}` has {mm.char_count(text)} characters > {limit}"))
    return out


@rule("MA-LABEL-11", "warn", "Note with more lines than the limit",
      "Shorten the note or move it to the text.",
      _lines_probe("note", "note_lines_max", True), _lines_probe("note", "note_lines_max", False))
def _check_note_lines(fig, ctx):
    limit = int(ctx.notation["labels"]["note_lines_max"])
    notes = (fig.sequence.notes if fig.sequence else []) + (fig.state.notes if fig.state else [])
    return [(n.line, f"{len(mm.label_lines(n.text))} lines > {limit}")
            for n in notes if len(mm.label_lines(n.text)) > limit]


@rule("MA-LABEL-12", "warn", "Edge label with more lines than the limit",
      "Keep an edge label to one line of about 3 words; the payload goes in the text.",
      _lines_probe("edge", "edge_label_lines_max", True), _lines_probe("edge", "edge_label_lines_max", False))
def _check_edge_lines(fig, ctx):
    limit = int(ctx.notation["labels"]["edge_label_lines_max"])
    return [(line, f"{len(mm.label_lines(label))} lines > {limit}")
            for line, label in _edge_label_items(fig) if len(mm.label_lines(label)) > limit]


@rule("MA-LABEL-13", "warn", "Participant name with more lines than the limit",
      "Give the participant a one-line display name; the role goes in the text.",
      _lines_probe("participant", "participant_lines_max", True),
      _lines_probe("participant", "participant_lines_max", False))
def _check_participant_lines(fig, ctx):
    if fig.sequence is None:
        return []
    limit = int(ctx.notation["labels"]["participant_lines_max"])
    return [(p.line, f"`{p.id}`: {len(_lines_of(p.label, p.id))} lines > {limit}")
            for p in fig.sequence.participants if len(_lines_of(p.label, p.id)) > limit]


# =========================================================================== CLASS

_HEX = re.compile(r"^#([0-9A-Fa-f]{3,4}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")
_FUNC_COLOUR = re.compile(r"^(rgba?|hsla?)\(\s*([^)]*)\)$", re.IGNORECASE)

#: The 148 CSS named colours (CSS Color 4, as the `color-name` package of the pinned renderers
#: lists them). `fill:yellow,color:white` measures 1.07:1 in every render, so a name is a colour.
_CSS_NAMED = {
    "aliceblue": "f0f8ff", "antiquewhite": "faebd7", "aqua": "00ffff", "aquamarine": "7fffd4",
    "azure": "f0ffff", "beige": "f5f5dc", "bisque": "ffe4c4", "black": "000000",
    "blanchedalmond": "ffebcd", "blue": "0000ff", "blueviolet": "8a2be2", "brown": "a52a2a",
    "burlywood": "deb887", "cadetblue": "5f9ea0", "chartreuse": "7fff00", "chocolate": "d2691e",
    "coral": "ff7f50", "cornflowerblue": "6495ed", "cornsilk": "fff8dc", "crimson": "dc143c",
    "cyan": "00ffff", "darkblue": "00008b", "darkcyan": "008b8b", "darkgoldenrod": "b8860b",
    "darkgray": "a9a9a9", "darkgreen": "006400", "darkgrey": "a9a9a9", "darkkhaki": "bdb76b",
    "darkmagenta": "8b008b", "darkolivegreen": "556b2f", "darkorange": "ff8c00",
    "darkorchid": "9932cc", "darkred": "8b0000", "darksalmon": "e9967a", "darkseagreen": "8fbc8f",
    "darkslateblue": "483d8b", "darkslategray": "2f4f4f", "darkslategrey": "2f4f4f",
    "darkturquoise": "00ced1", "darkviolet": "9400d3", "deeppink": "ff1493",
    "deepskyblue": "00bfff", "dimgray": "696969", "dimgrey": "696969", "dodgerblue": "1e90ff",
    "firebrick": "b22222", "floralwhite": "fffaf0", "forestgreen": "228b22", "fuchsia": "ff00ff",
    "gainsboro": "dcdcdc", "ghostwhite": "f8f8ff", "gold": "ffd700", "goldenrod": "daa520",
    "gray": "808080", "green": "008000", "greenyellow": "adff2f", "grey": "808080",
    "honeydew": "f0fff0", "hotpink": "ff69b4", "indianred": "cd5c5c", "indigo": "4b0082",
    "ivory": "fffff0", "khaki": "f0e68c", "lavender": "e6e6fa", "lavenderblush": "fff0f5",
    "lawngreen": "7cfc00", "lemonchiffon": "fffacd", "lightblue": "add8e6", "lightcoral": "f08080",
    "lightcyan": "e0ffff", "lightgoldenrodyellow": "fafad2", "lightgray": "d3d3d3",
    "lightgreen": "90ee90", "lightgrey": "d3d3d3", "lightpink": "ffb6c1", "lightsalmon": "ffa07a",
    "lightseagreen": "20b2aa", "lightskyblue": "87cefa", "lightslategray": "778899",
    "lightslategrey": "778899", "lightsteelblue": "b0c4de", "lightyellow": "ffffe0",
    "lime": "00ff00", "limegreen": "32cd32", "linen": "faf0e6", "magenta": "ff00ff",
    "maroon": "800000", "mediumaquamarine": "66cdaa", "mediumblue": "0000cd",
    "mediumorchid": "ba55d3", "mediumpurple": "9370db", "mediumseagreen": "3cb371",
    "mediumslateblue": "7b68ee", "mediumspringgreen": "00fa9a", "mediumturquoise": "48d1cc",
    "mediumvioletred": "c71585", "midnightblue": "191970", "mintcream": "f5fffa",
    "mistyrose": "ffe4e1", "moccasin": "ffe4b5", "navajowhite": "ffdead", "navy": "000080",
    "oldlace": "fdf5e6", "olive": "808000", "olivedrab": "6b8e23", "orange": "ffa500",
    "orangered": "ff4500", "orchid": "da70d6", "palegoldenrod": "eee8aa", "palegreen": "98fb98",
    "paleturquoise": "afeeee", "palevioletred": "db7093", "papayawhip": "ffefd5",
    "peachpuff": "ffdab9", "peru": "cd853f", "pink": "ffc0cb", "plum": "dda0dd",
    "powderblue": "b0e0e6", "purple": "800080", "rebeccapurple": "663399", "red": "ff0000",
    "rosybrown": "bc8f8f", "royalblue": "4169e1", "saddlebrown": "8b4513", "salmon": "fa8072",
    "sandybrown": "f4a460", "seagreen": "2e8b57", "seashell": "fff5ee", "sienna": "a0522d",
    "silver": "c0c0c0", "skyblue": "87ceeb", "slateblue": "6a5acd", "slategray": "708090",
    "slategrey": "708090", "snow": "fffafa", "springgreen": "00ff7f", "steelblue": "4682b4",
    "tan": "d2b48c", "teal": "008080", "thistle": "d8bfd8", "tomato": "ff6347",
    "turquoise": "40e0d0", "violet": "ee82ee", "wheat": "f5deb3", "white": "ffffff",
    "whitesmoke": "f5f5f5", "yellow": "ffff00", "yellowgreen": "9acd32"
}


def _channel(text: str, scale: float) -> float:
    text = text.strip()
    return float(text[:-1]) * scale / 100 if text.endswith("%") else float(text)


def _hsl_to_rgb(h: float, s: float, l: float) -> tuple:
    s, l = s / 100, l / 100
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    sector = int(h % 360 // 60)
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][sector]
    return (r + m) * 255, (g + m) * 255, (b + m) * 255


def _rgba(value: str) -> Optional[tuple]:
    """(r, g, b, alpha) of a CSS colour written as hex, rgb(), rgba(), hsl(), hsla(), a CSS name
    or `transparent`; None for any other form (`none`, `currentColor`, a variable)."""
    value = value.strip()
    named = value.lower()
    if named == "transparent":
        return 0, 0, 0, 0.0
    if named in _CSS_NAMED:
        h = _CSS_NAMED[named]
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0
    m = _HEX.match(value)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        alpha = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha
    m = _FUNC_COLOUR.match(value)
    if not m:
        return None
    parts = [p for p in re.split(r"[\s,/]+", m.group(2).strip()) if p]
    if len(parts) not in (3, 4):
        return None
    try:
        alpha = _channel(parts[3], 1.0) if len(parts) == 4 else 1.0
        if m.group(1).lower().startswith("rgb"):
            rgb = tuple(_channel(p, 255) for p in parts[:3])
        else:
            rgb = _hsl_to_rgb(float(parts[0].rstrip("deg")), _channel(parts[1], 100), _channel(parts[2], 100))
    except ValueError:
        return None
    return tuple(min(255.0, max(0.0, c)) for c in rgb) + (min(1.0, max(0.0, alpha)),)


def _over(top: tuple, bottom: tuple) -> tuple:
    a = top[3]
    return tuple(top[k] * a + bottom[k] * (1 - a) for k in range(3)) + (1.0,)


def _luminance(rgb: tuple) -> float:
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: tuple, bg: tuple) -> float:
    """WCAG 2.2 contrast ratio of two opaque RGB colours."""
    hi, lo = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _style_contrast(props: dict, notation: dict) -> Optional[float]:
    """Lowest contrast of `color` on `fill` over a light and a dark page; None without both."""
    fill, color = _rgba(props.get("fill", "")), _rgba(props.get("color", ""))
    if fill is None or color is None:
        return None
    pages = [(255, 255, 255, 1.0)]
    dark = _rgba(notation.get("renderers", {}).get("dark", {}).get("background", ""))
    if dark is not None and fill[3] < 1:
        pages.append(dark)
    ratios = []
    for page in pages:
        bg = _over(fill, page)
        ratios.append(contrast_ratio(_over(color, bg), bg))
    return min(ratios)


def _style_blocks(fig) -> list:
    """(line, name, props) for every classDef and style statement of the figure."""
    out = []
    for diagram in (fig.flowchart, fig.state):
        if diagram is None:
            continue
        out += [(d["line"], f"classDef {name}", d["props"]) for name, d in diagram.classdefs.items()]
        out += [(s["line"], f"style {s['target']}", mm._parse_props(s["raw"])) for s in diagram.styles]
    return out


@rule("MA-CLASS-01", "error", "Text colour on fill below the contrast minimum",
      "Darken `color` or lighten `fill` until the ratio reaches notation.json `contrast_min` "
      "(WCAG 2.2 SC 1.4.3).",
      _doc("flowchart TB\n  A --> B\n  classDef c fill:#FFFFFF,color:#BBBBBB\n  class A c"),
      _doc("flowchart TB\n  A --> B\n  classDef c fill:#E8F0FB,color:#0F2A47\n  class A c"))
def _check_contrast(fig, ctx):
    minimum = float(ctx.notation.get("contrast_min", 4.5))
    out = []
    for line, name, props in _style_blocks(fig):
        ratio = _style_contrast(props, ctx.notation)
        if ratio is not None and ratio < minimum:
            out.append((line, f"`{name}`: contrast {ratio:.2f}:1 < {minimum}:1"))
    return out


def _class_uses(fig) -> dict:
    """class name -> first line where a node, state or subgraph uses it."""
    uses: dict = {}
    if fig.flowchart:
        for n in fig.flowchart.nodes.values():
            for c in n.classes:
                uses.setdefault(c, n.line)
        for sid, names in fig.flowchart.subgraph_classes.items():
            sg = fig.flowchart.subgraphs.get(sid)
            for c in names:
                uses.setdefault(c, sg.line if sg else _fig_line(fig))
    if fig.state:
        for s in fig.state.states.values():
            for c in s.classes:
                uses.setdefault(c, s.line)
    return uses


def _class_defs(fig) -> dict:
    defs: dict = {}
    for diagram in (fig.flowchart, fig.state):
        if diagram is not None:
            defs.update(diagram.classdefs)
    return defs


@rule("MA-CLASS-02", "warn", "Class used but not defined",
      "Define the class with classDef in this figure, or drop it.",
      _doc("flowchart TB\n  A:::missing --> B"),
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#FFFFFF,color:#263238"))
def _check_undefined_class(fig, ctx):
    defs = _class_defs(fig)
    return [(line, f"class `{name}`") for name, line in _class_uses(fig).items()
            if name not in defs and name != "default"]


@rule("MA-CLASS-03", "warn", "Class defined but not used",
      "Delete unused classDef lines.",
      _doc("flowchart TB\n  A --> B\n  classDef unused fill:#FFFFFF,color:#263238"),
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#FFFFFF,color:#263238"))
def _check_unused_class(fig, ctx):
    uses = _class_uses(fig)
    return [(d["line"], f"classDef `{name}`") for name, d in _class_defs(fig).items()
            if name not in uses and name != "default"]


rule("MA-CLASS-04", "warn", "classDef default",
     "Name the class and apply it; in mermaid 10.9 `default` also styles every subgraph.",
     _doc("flowchart TB\n  A --> B\n  classDef default fill:#FFFFFF,color:#263238"),
     _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#FFFFFF,color:#263238"))(
    _hazard_check("classdef-default"))


def _theme_text_contrasts(fill: tuple, notation: dict) -> list:
    """(theme, ratio) of each theme's own text colour on *fill*, composed over that theme's page.

    The text colours are notation.json `lint.theme_text_colours`; the light page is white, the
    dark page `renderers.dark.background`."""
    pages = {"default": (255, 255, 255, 1.0)}
    dark = _rgba(notation.get("renderers", {}).get("dark", {}).get("background", ""))
    if dark is not None:
        pages["dark"] = dark
    out = []
    for theme, colour in notation.get("lint", {}).get("theme_text_colours", {}).items():
        text, page = _rgba(colour), pages.get(theme)
        if text is None or page is None:
            continue
        bg = _over(fill, page)
        out.append((theme, contrast_ratio(_over(text, bg), bg)))
    return out


@rule("MA-CLASS-05", "warn", "Fill without a text colour that a theme's own text cannot be read on",
      "Set `color` next to `fill`: without it the dark theme draws light text and the light theme "
      "dark text on the fill.",
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#E8F0FB,stroke:#2E5A8A"),
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47"))
def _check_fill_without_color(fig, ctx):
    minimum = float(ctx.notation.get("contrast_min", 4.5))
    out = []
    for line, name, props in _style_blocks(fig):
        fill = _rgba(props.get("fill", ""))
        if "color" in props or fill is None:
            continue
        low = [f"{theme} theme {ratio:.2f}:1" for theme, ratio in _theme_text_contrasts(fill, ctx.notation)
               if ratio < minimum]
        if low:
            out.append((line, f"`{name}` sets fill {props['fill']} and no color: " + ", ".join(low)
                        + f" < {minimum}:1"))
    return out


rule("MA-CLASS-06", "error", "`class` statement above the line that defines its node",
     "Move the `class` line below the node's first statement, or write `A:::c` on that statement; "
     "mermaid styles only nodes that exist at the `class` line, so the class is lost silently.",
     _doc("flowchart TB\n  class A c\n  A --> B\n  classDef c fill:#FFFFFF,color:#263238"),
     _doc("flowchart TB\n  A --> B\n  class A c\n  classDef c fill:#FFFFFF,color:#263238"))(
    _hazard_check("class-before-node"))

rule("MA-CLASS-07", "warn", "Styling in a kind that draws in the viewer's theme colours",
     "Drop classDef, style, cssClass and ::: from class, chart and timeline figures "
     "(other-kinds.md rule 5); the legend carries any category.",
     _doc("classDiagram\n  class Dog\n  style Dog fill:#FFF4E0,color:#4A2C00"),
     _doc("classDiagram\n  class Dog"))(
    _hazard_check("styling-theme"))


# =========================================================================== GANTT

_GANTT_HEAD = "gantt\n  dateFormat x\n  axisFormat %Q\n  todayMarker off\n"


@rule("MA-GANTT-01", "error", "`after` or `until` names a task declared below or never declared",
      "Declare a task before every task that names it, or generate the chart with plan_gantt.py.",
      _doc(_GANTT_HEAD + "  section S\n  first :a, 0, 3ms\n  second :b, after c, 2ms\n  third :c, 0, 4ms"),
      _doc(_GANTT_HEAD + "  section S\n  first :a, 0, 3ms\n  third :c, 0, 4ms\n  second :b, after c, 2ms"))
def _check_after(fig, ctx):
    g = fig.gantt
    if g is None:
        return []
    first_line = {}
    for t in g.tasks:
        if t.id:
            first_line.setdefault(t.id, t.line)
    out = []
    for t in g.tasks:
        for ref in mm.gantt_refs(t):
            where = first_line.get(ref)
            if where is None:
                out.append((t.line, f"`{ref}` is not declared; mermaid starts the bar at today"))
            elif where > t.line:
                out.append((t.line, f"`{ref}` is declared below, at line {where}; mermaid drops "
                                    "the dependency"))
    return out


@rule("MA-GANTT-02", "error", "Dotted id in `after`",
      "Use ids without dots; mermaid does not resolve `after t1.1`.",
      _doc(_GANTT_HEAD + "  section S\n  first :t1.1, 0, 3ms\n  second :b, after t1.1, 2ms"),
      _doc(_GANTT_HEAD + "  section S\n  first :t11, 0, 3ms\n  second :b, after t11, 2ms"))
def _check_dotted_after(fig, ctx):
    if fig.gantt is None:
        return []
    return [(t.line, f"`{ref}`") for t in fig.gantt.tasks for ref in mm.gantt_refs(t) if "." in ref]


rule("MA-GANTT-03", "error", "Colon in a gantt task label",
     "Remove the colon from the label; it moves the task id into the data.",
     _doc(_GANTT_HEAD + "  section S\n  T2 Orders: logic :t2, 3, 4ms"),
     _doc(_GANTT_HEAD + "  section S\n  T2 Orders logic :t2, 3, 4ms"))(
    _hazard_check("gantt-label-colon"))


@rule("MA-GANTT-04", "error", "Repeated gantt section",
      "Keep each section contiguous: one section line per stage.",
      _doc(_GANTT_HEAD + "  section S1\n  t1 :a, 0, 3ms\n  section S2\n  t2 :b, 3, 3ms\n  section S1\n"
           "  t3 :c, 6, 3ms"),
      _doc(_GANTT_HEAD + "  section S1\n  t1 :a, 0, 3ms\n  t3 :c, 6, 3ms\n  section S2\n  t2 :b, 3, 3ms"))
def _check_repeated_section(fig, ctx):
    g = fig.gantt
    if g is None:
        return []
    seen: dict = {}
    out = []
    lines = g.section_lines or [_fig_line(fig)] * len(g.sections)
    for name, line in zip(g.sections, lines):
        if name in seen:
            out.append((line, f"section `{name}` also starts at line {seen[name]}"))
        else:
            seen[name] = line
    return out


@rule("MA-GANTT-05", "warn", "Millisecond axis format %L or %-L",
      "Use `axisFormat %Q`: %L restarts at every second, so ticks read 0 again.",
      _doc("gantt\n  dateFormat x\n  axisFormat %L\n  todayMarker off\n  section S\n  t1 :a, 0, 3ms"),
      _doc(_GANTT_HEAD + "  section S\n  t1 :a, 0, 3ms"))
def _check_axis(fig, ctx):
    g = fig.gantt
    if g is None or not re.search(r"%-?L", g.axis_format):
        return []
    line = next((s["line"] for s in g.statements if s["keyword"] == "axisFormat"), _fig_line(fig))
    return [(line, f"axisFormat {g.axis_format}")]


rule("MA-GANTT-06", "error", "`topAxis` statement",
     "Remove `topAxis`; it is a parse error in 10.9, 11.17 and 12.1.",
     _doc(_GANTT_HEAD + "  topAxis\n  section S\n  t1 :a, 0, 3ms"),
     _doc(_GANTT_HEAD + "  section S\n  t1 :a, 0, 3ms"))(
    _hazard_check("gantt-topaxis"))


@rule("MA-GANTT-07", "warn", "Gantt without `todayMarker off`",
      "Add `todayMarker off`; otherwise the chart changes as time passes.",
      _doc("gantt\n  dateFormat x\n  axisFormat %Q\n  section S\n  t1 :a, 0, 3ms"),
      _doc(_GANTT_HEAD + "  section S\n  t1 :a, 0, 3ms"))
def _check_today(fig, ctx):
    g = fig.gantt
    if g is None or g.today_marker.strip().lower() == "off":
        return []
    return [(_fig_line(fig), "no `todayMarker off`")]


@rule("MA-GANTT-08", "error", "Bare number as a duration under `dateFormat x`",
      "Write the unit: `3ms`; a bare number is an absolute end time, so the bar vanishes.",
      _doc(_GANTT_HEAD + "  section S\n  first :a, 0, 3ms\n  second :b, 3, 5"),
      _doc(_GANTT_HEAD + "  section S\n  first :a, 0, 3ms\n  second :b, 3, 5ms"))
def _check_bare_duration(fig, ctx):
    g = fig.gantt
    if g is None or g.date_format.strip() not in ("x", "X"):
        return []
    return [(t.line, f"`{t.duration}` in `{t.label}`") for t in g.tasks
            if re.fullmatch(r"\d+(\.\d+)?", t.duration.strip())]


# =========================================================================== ASCII

@rule("MA-ASCII-01", "error", "Tab in an ASCII figure",
      "Replace tabs with spaces; viewers expand tabs to different widths.",
      _doc("a\t-> b", ASCII), _doc("a  -> b", ASCII))
def _check_tabs(fig, ctx):
    return [(line, "tab character") for line in fig.ascii.tabs] if fig.ascii else []


@rule("MA-ASCII-02", "warn", "Double-width character on an aligned line",
      "Use single-width characters inside boxes and trees; an emoji or CJK character shifts the border.",
      _doc("+--------+\n| 名前 |\n+--------+", ASCII),
      _doc("+--------+\n| name   |\n+--------+", ASCII))
def _check_wide(fig, ctx):
    if fig.ascii is None:
        return []
    aligned = set(fig.ascii.aligned)
    return [(line, "double-width character on a line with borders") for line in fig.ascii.wide if line in aligned]


def _width_probe(fire: bool) -> Callable:
    def make(notation):
        n = int(notation["ascii"]["max_columns"]) + (1 if fire else 0)
        return _doc("a" * n, ASCII)
    return make


@rule("MA-ASCII-03", "warn", "Line wider than the ASCII column limit",
      "Shorten or wrap the line; terminals and diff views cut it.",
      _width_probe(True), _width_probe(False))
def _check_width(fig, ctx):
    if fig.ascii is None:
        return []
    limit = int(ctx.notation["ascii"]["max_columns"])
    return [(line, f"{width} columns > {limit}")
            for (line, _text), width in zip(fig.ascii.lines, fig.ascii.widths) if width > limit]


@rule("MA-ASCII-04", "warn", "Box side or corner off its column",
      "Move the side or the corner to the column of the box's top corners; pad every line of the "
      "box to the top-right corner.",
      (_doc("+------+\n| api |\n+------+", ASCII), _doc("+------+\n| api  |\n | db  |\n+------+", ASCII),
       _doc("┌──────┐\n│ api  │\n └──────┘", ASCII)),
      _doc("+------+\n| api  |\n| db   |\n+------+", ASCII))
def _check_ragged(fig, ctx):
    if fig.ascii is None:
        return []
    out = []
    for box in fig.ascii.boxes:
        off = sorted(set(box.ragged) | set(box.shifted))
        if not off:
            continue
        which = ("right border" if not box.shifted else
                 "left side or bottom corner" if not box.ragged else "border")
        out.append((off[0], f"box at line {box.top}: {which} off its column on {len(off)} line(s)"))
    return out


def _ascii_probe(which: str) -> Callable:
    def make(notation):
        soft, hard = (int(x) for x in notation["budgets"]["ascii"]["elements"])
        n = {"soft-fire": soft + 1, "soft-quiet": soft, "hard-fire": hard + 1, "hard-quiet": hard}[which]
        return _doc(" -> ".join(f"s{k}" for k in range(1, n + 1)), ASCII)
    return make


def _ascii_elements(fig, ctx) -> tuple:
    soft, hard = (int(x) for x in ctx.notation["budgets"]["ascii"]["elements"])
    return len(fig.ascii.elements), soft, hard


@rule("MA-ASCII-05", "warn", "ASCII figure over the soft element budget",
      "Aggregate or split: an ASCII figure holds a chain or a tree within the soft budget.",
      _ascii_probe("soft-fire"), _ascii_probe("soft-quiet"))
def _check_ascii_budget(fig, ctx):
    if fig.ascii is None:
        return []
    count, soft, hard = _ascii_elements(fig, ctx)
    return [(_fig_line(fig), f"{count} elements > soft budget {soft}")] if soft < count <= hard else []


@rule("MA-ASCII-06", "error", "ASCII figure over the hard element budget",
      "Write a numbered list, a nested list or a table instead (ascii.md §2 rule 4).",
      _ascii_probe("hard-fire"), _ascii_probe("hard-quiet"))
def _check_ascii_hard_budget(fig, ctx):
    if fig.ascii is None:
        return []
    count, _soft, hard = _ascii_elements(fig, ctx)
    return [(_fig_line(fig), f"{count} elements > hard budget {hard}; use a list or a table")] if count > hard else []


@rule("MA-ASCII-07", "warn", "Vertical connector off its column",
      "Move the connector to the column of the stroke above or below it (ascii.md §2).",
      (_doc("sensor\n  │ MQTT\n   ▼\ngateway", ASCII),
       _doc("a --+--> b ---+--> d\n    |         |\n     +--> c ---+", ASCII),
       _doc("root\n├── a\n │   └── b\n└── c", ASCII)),
      _doc("sensor\n  │ MQTT\n  ▼\ngateway", ASCII))
def _check_connector_drift(fig, ctx):
    if fig.ascii is None or not fig.ascii.drift:
        return []
    lines = sorted({lower for _upper, lower in fig.ascii.drift})
    shown = ", ".join(str(x) for x in lines[:6]) + (" …" if len(lines) > 6 else "")
    return [(lines[0], f"a vertical stroke moves by one column at line(s) {shown}")]


# =========================================================================== DOC: caption, legend, one notation

def _in_document(fig, ctx) -> bool:
    """True for a fence of a Markdown document; a `.mmd` file has no caption or legend."""
    return not ctx.is_mmd and fig.fence.start > 0


def _legend_reasons(fig, ctx) -> list:
    """The encodings that make a figure need a legend (TASK R3.7: two or more), per notation.json
    `lint` `legend_min_*`. In an ASCII figure, a fork and its join are the second encoding next
    to the links (ascii.md §4); a fan-out, a fork without a join, is none."""
    if fig.kind == "ascii":
        a = fig.ascii
        return ["a fork and a join"] if a is not None and a.forks and a.joins else []
    lint = ctx.notation.get("lint", {})
    classes, edge_styles, shapes = _legend_encodings(fig)
    reasons = []
    if len(classes) >= int(lint.get("legend_min_classes", 2)):
        reasons.append(f"{len(classes)} classes or styles")
    if len(edge_styles) >= int(lint.get("legend_min_edge_styles", 2)):
        reasons.append(f"{len(edge_styles)} edge styles")
    if len(shapes) >= int(lint.get("legend_min_shapes", 3)):
        reasons.append(f"{len(shapes)} node shapes")
    return reasons


@rule("MA-DOC-01", "warn", "Figure without a caption above the fence",
      "Put the caption in the paragraph directly above the fence; a heading is not a caption.",
      "## Heading\n\n```mermaid\nflowchart TB\n  A --> B\n```\n",
      _doc("flowchart TB\n  A --> B"))
def _check_caption(fig, ctx):
    """TASK R3.7: the caption is the paragraph directly above the fence. A figure whose only
    neighbour is a paragraph below, and which needs no legend, gets MA-DOC-05 instead."""
    if not _in_document(fig, ctx) or fig.fence.before is not None:
        return []
    if fig.fence.after is not None and not _legend_reasons(fig, ctx):
        return []
    return [(_fig_line(fig), "no paragraph directly above the fence")]


@rule("MA-DOC-05", "warn", "Caption below the fence",
      "Move the caption to the paragraph directly above the fence; the paragraph below is the legend.",
      "```mermaid\nflowchart TB\n  A --> B\n```\n\n**Figure 1.** Probe.\n",
      _doc("flowchart TB\n  A --> B"))
def _check_caption_below(fig, ctx):
    if not _in_document(fig, ctx) or fig.fence.before is not None or fig.fence.after is None:
        return []
    if _legend_reasons(fig, ctx):
        return []
    return [(_fig_line(fig), f"caption below the fence: the paragraph at line {fig.fence.after.start} "
                             "is the only one next to the fence")]


def _encodings(fig) -> tuple:
    """(classes, edge styles, node shapes) a figure uses."""
    classes, edge_styles, shapes = set(), set(), set()
    if fig.flowchart:
        fc = fig.flowchart
        for n in fc.nodes.values():
            classes.update(c for c in n.classes if c != "default")
            shapes.add(n.shape)
        for names in fc.subgraph_classes.values():
            classes.update(c for c in names if c != "default")
        classes.update(f"style:{s['raw']}" for s in fc.styles if s["target"] in fc.nodes)
        edge_styles.update(e.style for e in fc.edges if e.style != "invisible")
    if fig.state:
        for s in fig.state.states.values():
            classes.update(c for c in s.classes if c != "default")
        classes.update(f"style:{s['raw']}" for s in fig.state.styles)
    if fig.gantt:
        for t in fig.gantt.tasks:
            classes.update(tag for tag in t.tags if tag != "vert")
    return classes, edge_styles, shapes


def _legend_encodings(fig) -> tuple:
    """`_encodings` plus what the legend rule also counts: in a flowchart each `linkStyle`
    stroke, in a sequence each arrow kind (`->>` a call, `-->>` a reply: sequence.md §10) and
    each `rect` or `box` fill. `_encodings` stays as the eval grader reads it."""
    classes, edge_styles, shapes = _encodings(fig)
    if fig.flowchart:
        strokes = {mm._parse_props(s["raw"]).get("stroke", "") for s in fig.flowchart.link_styles
                   if s["index"] != "default"}
        edge_styles.update(f"linkStyle:{x}" for x in strokes if x)
    if fig.sequence:
        edge_styles.update(m.arrow for m in fig.sequence.messages)
        classes.update(f"{b.kind}:{b.colour}" for b in fig.sequence.blocks if b.colour)
    return classes, edge_styles, shapes


_TWO_CLASSES = ("flowchart TB\n  A:::x --> B:::y\n  classDef x fill:#FFFFFF,color:#263238\n"
                "  classDef y fill:#E8F0FB,color:#0F2A47")


@rule("MA-DOC-02", "warn", "Figure with two or more encodings and no legend below the fence",
      "Put the legend in the paragraph or list directly below the fence; name each class, edge "
      "style and shape the figure uses.",
      f"**Figure 1.** Probe.\n\n```mermaid\n{_TWO_CLASSES}\n```\n",
      _doc(_TWO_CLASSES))
def _check_legend(fig, ctx):
    """TASK R3.7: the legend is the paragraph or list directly below the fence."""
    if not _in_document(fig, ctx):
        return []
    reasons = _legend_reasons(fig, ctx)
    if reasons and fig.fence.after is None:
        return [(_fig_line(fig), "the figure uses " + ", ".join(reasons)
                 + " but no paragraph or list sits directly below the fence")]
    return []


@rule("MA-DOC-03", "warn", "One class name with different properties in two figures",
      "Use one class block for the whole document (TASK R3.8).",
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#FFFFFF,color:#263238") + "\n"
      + _doc("flowchart TB\n  C:::c --> D\n  classDef c fill:#E8F0FB,color:#0F2A47"),
      _doc("flowchart TB\n  A:::c --> B\n  classDef c fill:#FFFFFF,color:#263238") + "\n"
      + _doc("flowchart TB\n  C:::c --> D\n  classDef c fill:#FFFFFF,color:#263238"),
      scope="document")
def _check_class_consistency(figures, ctx):
    first: dict = {}
    out = []
    for fig in figures:
        for name, d in _class_defs(fig).items():
            props = json.dumps(d["props"], sort_keys=True)
            if name not in first:
                first[name] = (props, d["line"])
            elif props != first[name][0]:
                out.append((d["line"], f"classDef `{name}` differs from line {first[name][1]}"))
    return out


@rule("MA-DOC-04", "warn", "One participant with different names in two figures",
      "Give each participant one alias in the whole document (TASK R3.8).",
      _doc("sequenceDiagram\n  participant A as Api\n  A->>A: x") + "\n"
      + _doc("sequenceDiagram\n  participant A as Gateway\n  A->>A: y"),
      _doc("sequenceDiagram\n  participant A as Api\n  A->>A: x") + "\n"
      + _doc("sequenceDiagram\n  participant A as Api\n  A->>A: y"),
      scope="document")
def _check_alias_consistency(figures, ctx):
    first: dict = {}
    out = []
    for fig in figures:
        if fig.sequence is None:
            continue
        for p in fig.sequence.participants:
            if not p.declared:
                continue
            name = p.label or p.id
            if p.id not in first:
                first[p.id] = (name, p.line)
            elif name != first[p.id][0]:
                out.append((p.line, f"`{p.id}` is `{name}` here and `{first[p.id][0]}` at line {first[p.id][1]}"))
    return out


# =========================================================================== MODEL

@rule("MA-MODEL-01", "warn", "Statement the lint's parser could not read",
      "Check the statement against the kind's reference; the render check decides whether it renders.",
      _doc("flowchart TB\n  A --> B )("),
      _doc("flowchart TB\n  A --> B"))
def _check_unread(fig, ctx):
    return [(e["line"], e["message"]) for e in fig.parse_errors if not e.get("internal")]


# =========================================================================== NEG: negative-fence markers

def _marker(fig, ctx):
    """The marker that makes *fig* negative, or None: a fence's last-line marker in a document
    where markers count. Read once per figure per run."""
    key = id(fig)
    if key not in ctx.markers:
        ctx.markers[key] = fig.fence.negative if ctx.honours_markers() else None
    return ctx.markers[key]


def _is_negative(fig, ctx) -> bool:
    return _marker(fig, ctx) is not None


def _named_rule_ids(fig, ctx) -> set:
    """The ids of the rules the marker of a negative *fig* names, by id or by family."""
    marker = _marker(fig, ctx)
    out = set()
    for name in (marker.names if marker is not None else []):
        kind = classify_marker_name(name)
        out.update(r.id for r in (kind[1] if kind else []))
    return out


def _inside(fig, line: int) -> bool:
    return fig.fence.start <= line <= fig.fence.end


def _nameable_rules() -> list:
    """The rules a negative marker may name: every rule but the marker rules themselves."""
    return [r for r in RULES if r.scope != "marker"]


def classify_marker_name(name: str):
    """Return `("rule", [rule])`, `("family", [rules])`, `("render", [])` or None for one name of
    a negative marker. Rule ids and family names compare without case."""
    rules = _nameable_rules()
    upper = name.upper()
    by_id = [r for r in rules if r.id == upper]
    if by_id:
        return "rule", by_id
    key = name.lower()
    key = key[3:] if key.startswith("ma-") else key
    prefix = FAMILY_PREFIXES.get(key)
    if prefix:
        return "family", [r for r in rules if r.id.startswith(prefix)]
    if name in mm.RENDER_CHECK_NAMES:
        return "render", []
    return None


def _fires_on(r, fig, figures: list, ctx) -> bool:
    """True when rule *r* reports a finding inside the negative figure *fig*."""
    if r.scope == "figure":
        return bool(r.check(fig, ctx))
    positives = [f for f in figures if not _is_negative(f, ctx)]
    return any(_inside(fig, line) for line, _message in r.check(positives + [fig], ctx))


_NEG_NAMES_HINT = ("Name lint rule ids (MA-FLOW-01), lint families ("
                   + ", ".join(FAMILY_PREFIXES) + ") or render checks ("
                   + ", ".join(mm.RENDER_CHECK_NAMES) + "), comma-separated, in "
                   "`%% negative: <names>` as the last body line of the fence.")


@rule("MA-NEG-01", "error", "Negative fence on which none of the named lint checks fires",
      "The example no longer shows its defect: restore the defect, or name the checks it fails.",
      _doc("flowchart TB\n  A --> B\n  %% negative: MA-FLOW-01"),
      _doc("flowchart TB\n  A --> B\n  B --> A\n  %% negative: MA-FLOW-01"),
      scope="marker")
def _check_negative_fires(figures, ctx):
    out = []
    for fig in figures:
        marker = _marker(fig, ctx)
        if marker is None:
            continue
        named, seen = [], set()
        for name in marker.names:
            kind = classify_marker_name(name)
            for r in (kind[1] if kind else []):
                if r.id not in seen:
                    seen.add(r.id)
                    named.append(r)
        if named and not any(_fires_on(r, fig, figures, ctx) for r in named):
            out.append((marker.line, "none of " + ", ".join(r.id for r in named[:8])
                        + (" …" if len(named) > 8 else "") + " fires on this negative fence"))
    return out


@rule("MA-NEG-02", "error", "Negative marker that names nothing, names an unknown check, or is not "
      "the last body line", _NEG_NAMES_HINT,
      _doc("flowchart TB\n  A --> B\n  B --> A\n  %% negative: MA-FLOW-99"),
      _doc("flowchart TB\n  A --> B\n  B --> A\n  %% negative: MA-FLOW-01, crossings"),
      scope="marker")
def _check_marker_shape(figures, ctx):
    if not ctx.honours_markers():
        return []  # MA-NEG-03 reports every marker of such a document
    out = []
    for fig in figures:
        for marker in fig.fence.markers:
            if not marker.last:
                out.append((marker.line, "the marker is not the last body line, so the fence is "
                                         "linted as a positive figure"))
                continue
            if not marker.names:
                out.append((marker.line, "the marker names no check"))
            for name in marker.names:
                if classify_marker_name(name) is None:
                    out.append((marker.line, f"`{name}` is not a lint rule id, a lint family or a "
                                             "render check"))
    return out


@rule("MA-NEG-03", "error", "Negative marker outside the skill's references and test fixtures",
      "Remove the `%% negative:` line: only the skill's references and test fixtures show a defect "
      "on purpose. Here the fence is linted as a positive figure, and each of its findings counts.",
      _doc("flowchart TB\n  A --> B\n  B --> A\n  %% negative: MA-FLOW-01"),
      _doc("flowchart TB\n  A --> B"),
      scope="marker", probe_negative=False)
def _check_marker_ignored(figures, ctx):
    if ctx.honours_markers():
        return []
    return [(marker.line, "the marker is ignored: it counts only in the skill's references/ and "
                          "scripts/tests/fixtures/")
            for fig in figures for marker in fig.fence.markers]


# =========================================================================== engine


def _figure_at(line: int, figures: list):
    """The figure whose fence holds *line*; None when no fence does."""
    return next((fig for fig in figures if _inside(fig, line)), None)


def _rule_results(r, figures: list, ctx) -> list:
    """`(figure, line, message)` of one rule over the figures of one document.

    A document rule compares the positive figures among themselves, then each negative figure
    against them; a finding of the second pass counts only inside that negative figure. So a
    negative example never moves a finding onto a positive figure."""
    out = []
    if r.scope == "figure":
        for fig in figures:
            out += [(fig, line, message) for line, message in r.check(fig, ctx)]
    elif r.scope == "document":
        positives = [f for f in figures if not _is_negative(f, ctx)]
        out += [(_figure_at(line, positives), line, message) for line, message in r.check(positives, ctx)]
        for neg in figures:
            if _is_negative(neg, ctx):
                out += [(neg, line, message) for line, message in r.check(positives + [neg], ctx)
                        if _inside(neg, line)]
    else:
        out += [(_figure_at(line, figures), line, message) for line, message in r.check(figures, ctx)]
    return out


def lint_figures(figures: list, ctx: LintContext, rules: Optional[list] = None) -> list:
    """Apply *rules* (default: RULES) to parsed figures and return Findings sorted by line.

    Every finding carries the line of its fence. A finding inside a negative fence is marked
    `expected` when its rule is one the marker names, by id or by family; the other findings of
    the fence count, and so do the findings of the marker rules (MA-NEG).
    Raises LintInternalError when the parser or a rule failed (exit 2 at the CLI)."""
    rules = RULES if rules is None else rules
    for fig in figures:
        for err in fig.parse_errors:
            if err.get("internal"):
                raise LintInternalError(f"{ctx.path}:{err['line']}: {err['message']}")
    named = {id(fig): _named_rule_ids(fig, ctx) for fig in figures}
    findings = []
    for r in rules:
        try:
            results = _rule_results(r, figures, ctx)
        except Exception as exc:  # noqa: BLE001 — a failing rule is a broken instrument
            raise LintInternalError(f"rule {r.id} failed on {ctx.path}: {exc!r}") from exc
        for fig, line, message in results:
            expected = r.scope != "marker" and fig is not None and r.id in named.get(id(fig), ())
            findings.append(Finding(rule=r.id, severity=r.severity, path=ctx.path, line=int(line),
                                    message=str(message), hint=r.hint,
                                    fence=fig.fence.start if fig is not None else 0, expected=expected))
    order = {r.id: k for k, r in enumerate(rules)}
    findings.sort(key=lambda f: (f.line, order.get(f.rule, 0)))
    return findings


def lint_text(text: str, path: str = "<text>", is_mmd: bool = False,
              notation: Optional[dict] = None, rules: Optional[list] = None,
              langs: tuple = mm.FIGURE_LANGS, negative: Optional[bool] = None) -> list:
    """Parse *text* and lint it. The entry point the eval grader calls.

    *langs* selects the fences that are figures (`mermaid_model.FIGURE_LANGS`: `mermaid` and
    `text figure`). A caller that reads every `text` fence as an ASCII figure passes
    `("mermaid", "text")`. *negative* says whether `%% negative:` markers count; None decides by
    *path* (`mermaid_model.negative_allowed`). The returned list holds the expected findings too;
    filter on `Finding.expected`."""
    notation = notation if notation is not None else mm.load_notation()
    figures = [mm.parse_figure(mm.figure_from_mmd(text))] if is_mmd else mm.parse_document(text, langs)
    return lint_figures(figures, LintContext(notation=notation, path=path, is_mmd=is_mmd,
                                             negative=negative), rules)


def _probe_text(probe, notation: dict) -> str:
    return probe(notation) if callable(probe) else probe


def run_probes(rules: Optional[list] = None, notation: Optional[dict] = None) -> list:
    """Return the ids of rules whose probe pair fails. An empty list means every rule is live.

    A rule with several fire probes is live only when each of them fires: one detector of the
    rule that dies cannot hide behind another."""
    notation = notation if notation is not None else mm.load_notation()
    dead = []
    for r in (RULES if rules is None else rules):
        fires = r.probe_fire if isinstance(r.probe_fire, (tuple, list)) else (r.probe_fire,)
        try:
            fired = [lint_text(_probe_text(p, notation), "<probe>", notation=notation, rules=[r],
                               negative=r.probe_negative) for p in fires]
            quiet = lint_text(_probe_text(r.probe_quiet, notation), "<probe>", notation=notation,
                              rules=[r], negative=r.probe_negative)
        except Exception:  # noqa: BLE001 — a probe that crashes is a dead rule
            dead.append(r.id)
            continue
        if not fires or not all(fired) or quiet:
            dead.append(r.id)
    return dead


_NUMBER = re.compile(r"\d+(?:[.,]\d+)*%?")


def _rows_numbers(rows: list, owner: str, text: str, line: int) -> None:
    for num in _NUMBER.findall(text or ""):
        rows.append({"kind": "number", "id": owner, "text": num, "line": line, "support": ""})


def inventory(figure) -> list:
    """Return one row per element of *figure*: node, edge, label, note, number, group, message,
    transition or task. Row keys: `kind`, `id`, `text`, `line`, `support` (always "")."""
    rows: list = []

    def add(kind, ident, text, line):
        rows.append({"kind": kind, "id": str(ident), "text": text, "line": line, "support": ""})
        _rows_numbers(rows, str(ident), text if kind not in ("edge", "message", "transition") else "", line)

    fig = figure
    if fig.flowchart:
        fc = fig.flowchart
        for sg in fc.subgraphs.values():
            add("group", sg.id, " / ".join(_lines_of(sg.title, sg.id)), sg.line)
        for n in fc.nodes.values():
            add("node", n.id, " / ".join(_lines_of(n.label, n.id)), n.line)
        for k, e in enumerate(fc.edges):
            if e.style == "invisible":
                continue
            sym = {"<->": "<->", "->": "->", "none": "--"}[e.arrow]
            rows.append({"kind": "edge", "id": f"e{k}", "text": f"{e.src} {sym} {e.dst}", "line": e.line,
                         "support": ""})
            if e.label:
                add("label", f"e{k}", " / ".join(mm.label_lines(e.label)), e.line)
    if fig.sequence:
        seq = fig.sequence
        for p in seq.participants:
            add("node", p.id, p.label or p.id, p.line)
        for b in seq.blocks:
            add("group", b.kind, b.label, b.start)
        for k, m in enumerate(seq.messages):
            text = " / ".join(mm.label_lines(m.text))
            rows.append({"kind": "message", "id": f"m{k}", "text": f"{m.src} {m.arrow} {m.dst}: {text}",
                         "line": m.line, "support": ""})
            _rows_numbers(rows, f"m{k}", text, m.line)
        for k, n in enumerate(seq.notes):
            add("note", f"n{k}", " / ".join(mm.label_lines(n.text)), n.line)
    if fig.state:
        sd = fig.state
        for s in sd.states.values():
            if s.composite:
                add("group", s.id, " / ".join(_lines_of(s.label, s.id)), s.line)
            else:
                add("node", s.id, " / ".join(_lines_of(s.label, s.id)), s.line)
        for k, t in enumerate(sd.transitions):
            label = " / ".join(mm.label_lines(t.label))
            rows.append({"kind": "transition", "id": f"t{k}",
                         "text": f"{t.src} -> {t.dst}" + (f": {label}" if label else ""), "line": t.line,
                         "support": ""})
            _rows_numbers(rows, f"t{k}", label, t.line)
        for k, n in enumerate(sd.notes):
            add("note", f"n{k}", " / ".join(mm.label_lines(n.text)), n.line)
    if fig.gantt:
        g = fig.gantt
        for name, line in zip(g.sections, g.section_lines or [fig.fence.start] * len(g.sections)):
            add("group", name, name, line)
        for k, t in enumerate(g.tasks):
            add("task", t.id or f"task{k + 1}", t.label, t.line)
    if fig.er:
        for ent in fig.er.entities.values():
            add("node", ent.name, ent.alias or ent.name, ent.line)
            for text, line in zip(ent.attributes, ent.attribute_lines or [ent.line] * len(ent.attributes)):
                add("label", ent.name, text, line)
        for k, r in enumerate(fig.er.relations):
            rows.append({"kind": "edge", "id": f"r{k}", "text": f"{r.a} {r.cardinality} {r.b}", "line": r.line,
                         "support": ""})
            if r.label:
                add("label", f"r{k}", r.label, r.line)
    if fig.ascii:
        for k, (line, text) in enumerate(fig.ascii.elements):
            add("node", f"a{k}", text, line)
    for kind, ident, text, line in getattr(fig, "items", []):
        if kind in ("edge", "number"):
            rows.append({"kind": kind, "id": str(ident), "text": text, "line": line, "support": ""})
        else:
            add(kind, ident, text, line)
    rows.sort(key=lambda r: r["line"])
    return rows


def inventoried(figure) -> bool:
    """True when `inventory` reads the elements of the figure's kind. For any other kind an
    empty table would read as a figure with no elements, so the output says so instead."""
    return (figure.kind in ("flowchart", "sequence", "state", "gantt", "er", "ascii")
            or figure.kind in mm.ITEM_KINDS)


def counts(findings: list) -> dict:
    """`error` and `warn` count the findings outside negative fences; `expected` the rest."""
    return {"error": sum(1 for f in findings if f.severity == "error" and not f.expected),
            "warn": sum(1 for f in findings if f.severity == "warn" and not f.expected),
            "expected": sum(1 for f in findings if f.expected)}


def _summary(c: dict) -> str:
    return f"{c['error']} error / {c['warn']} warn / {c['expected']} expected"


def _finding_line(f: Finding) -> str:
    fence = f" [fence {f.fence}]" if f.fence else ""
    return f"{f.path}:{f.line}: {f.severity} {f.rule}{fence} {f.message}"


def _finding_dict(f: Finding) -> dict:
    return {"rule": f.rule, "severity": f.severity, "path": f.path, "line": f.line, "fence": f.fence,
            "message": f.message, "hint": f.hint}


def _format_text(findings: list, paths: Optional[list] = None) -> str:
    """One line per finding with the line of its fence and the rule's hint after `→` (TASK
    R6.4), the expected findings of negative fences apart, a count line per file when there are
    several, and the total."""
    out = []
    for f in findings:
        if not f.expected:
            out.append(_finding_line(f) + (f" → {f.hint}" if f.hint else ""))
    expected = [f for f in findings if f.expected]
    if expected:
        out.append("expected on negative fences (not counted):")
        out += [_finding_line(f) for f in expected]
    if paths and len(paths) > 1:
        out += [f"{p}: {_summary(counts([f for f in findings if f.path == p]))}" for p in paths]
    out.append(_summary(counts(findings)))
    return "\n".join(out)


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _format_inventory(blocks: list) -> str:
    out = []
    for block in blocks:
        if not block["inventoried"]:
            out.append(f"{block['path']}:{block['figure_line']} {block['figure_kind']} — not inventoried: "
                       f"{block['figure_kind']}; list its elements from the source")
            out.append("")
            continue
        out.append(f"{block['path']}:{block['figure_line']} {block['figure_kind']} — {len(block['rows'])} rows")
        out.append("| kind | id | text | line | support |")
        out.append("| :--- | :--- | :--- | :--- | :--- |")
        for r in block["rows"]:
            out.append(f"| {_cell(r['kind'])} | {_cell(r['id'])} | {_cell(r['text'])} | {r['line']} |  |")
        out.append("")
    return "\n".join(out)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="lint_mermaid.py",
                                description="Static lint for Mermaid and ASCII figures.")
    p.add_argument("paths", nargs="*", help="Markdown (.md) or Mermaid (.mmd) files")
    p.add_argument("--json", action="store_true", help="print findings as JSON")
    p.add_argument("--inventory", action="store_true",
                   help="print the element inventory of every figure instead of findings")
    p.add_argument("--probe", action="store_true",
                   help="check every rule's probe pair and exit (0 all live, 2 a dead rule); takes no "
                        "paths")
    return p


def main(argv: Optional[list] = None, notation_path: Optional[Path] = None) -> int:
    """The CLI. *notation_path* replaces `assets/notation.json` for a test; no option reaches it,
    so the auto-approved command line cannot lint against relaxed thresholds."""
    p = build_parser()
    try:
        args = p.parse_args(argv)
    except SystemExit as exc:
        return EXIT_USAGE if exc.code else EXIT_OK
    if not args.paths and not args.probe:
        p.print_usage(sys.stderr)
        return EXIT_USAGE
    if args.probe and (args.paths or args.json or args.inventory):
        # a CI line `--probe docs/*.md` would otherwise pass without linting a file
        print("usage error: --probe takes no paths and no other option; run the lint without --probe",
              file=sys.stderr)
        return EXIT_USAGE
    try:
        notation = mm.load_notation(notation_path)
    except (OSError, ValueError) as exc:
        print(f"internal error: notation unreadable: {exc}", file=sys.stderr)
        return EXIT_INTERNAL
    dead = run_probes(notation=notation)
    if dead:
        print(f"dead rule(s): {', '.join(dead)} — a probe pair failed; the lint reports nothing",
              file=sys.stderr)
        return EXIT_INTERNAL
    if args.probe:
        print(f"{len(RULES)}/{len(RULES)} rules live")
        return EXIT_OK
    texts = []
    for raw in args.paths:
        path = Path(raw)
        try:
            texts.append((raw, path.read_text(encoding="utf-8"), path.suffix.lower() == ".mmd"))
        except (OSError, UnicodeDecodeError) as exc:
            print(f"usage error: cannot read {raw}: {exc}", file=sys.stderr)
            return EXIT_USAGE
    try:
        if args.inventory:
            blocks = []
            for raw, text, is_mmd in texts:
                figures = [mm.parse_figure(mm.figure_from_mmd(text))] if is_mmd else mm.parse_document(text)
                for fig in figures:
                    broken = next((e for e in fig.parse_errors if e.get("internal")), None)
                    if broken is not None:
                        # an inventory the parser failed to read is no inventory (TASK D20)
                        raise LintInternalError(f"{raw}:{broken['line']}: {broken['message']}")
                    blocks.append({"path": raw, "figure_line": fig.fence.start, "figure_kind": fig.kind,
                                   "inventoried": inventoried(fig), "rows": inventory(fig)})
            print(json.dumps({"schema": "mermaid-inventory/v1", "figures": blocks}, ensure_ascii=False, indent=2)
                  if args.json else _format_inventory(blocks))
            return EXIT_OK
        findings = []
        for raw, text, is_mmd in texts:
            findings.extend(lint_text(text, raw, is_mmd=is_mmd, notation=notation))
    except LintInternalError as exc:
        print(f"internal error: {exc}", file=sys.stderr)
        return EXIT_INTERNAL
    paths = [raw for raw, _t, _m in texts]
    total = counts(findings)
    if args.json:
        print(json.dumps({
            "schema": "mermaid-lint/v1",
            "files": paths,
            "rules": len(RULES),
            "counts": total,
            "per_file": {p: counts([f for f in findings if f.path == p]) for p in paths},
            "findings": [_finding_dict(f) for f in findings if not f.expected],
            "expected": [_finding_dict(f) for f in findings if f.expected],
        }, ensure_ascii=False, indent=2))
    else:
        print(_format_text(findings, paths))
    return EXIT_FINDINGS if total["error"] else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
