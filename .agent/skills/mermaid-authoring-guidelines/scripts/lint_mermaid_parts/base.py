"""The header of the figure lint: exit codes, findings, the rule registry, the `rule`
decorator and the helpers that rules share (TASK 126)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import mermaid_model as mm


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


#: Rule registry, filled as each module of the package registers its rules, in the order
#: in which `lint_mermaid.py` imports them. Order is report order.
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


