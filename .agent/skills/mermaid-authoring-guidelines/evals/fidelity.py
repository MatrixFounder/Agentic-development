#!/usr/bin/env python3
"""Key-based fidelity matcher for the figure evals (TASK 108, R11; r7 design section 9.4).

Eval code, not a production twin: the key is eval data written before any run, and the skill's
own fidelity step is a reading pass with no deterministic counterpart. Every public function is
pure: it reads a key dict and already-parsed figures and returns plain values. Nothing here
reads `assets/notation.json`; thresholds belong to the lint and the geometry analysis.

What the matcher decides (headline checks of `evals.json`):

  Q09  nothing drawn that the document does not state: relations, messages, transitions,
       branches, dependencies, control blocks, order
  Q10  every required relation drawn, directly or through a stated aggregate
  Q11  no number absent from the document or attached to the wrong subject
  Q12  no invented node, participant, state, task, group or writer

It also reports decoy hits by type and the claims of a caption (an input of Q13).

Forms it reads: Mermaid flowchart, sequence, state and gantt figures (the dataclasses of
`scripts/mermaid_model.py`, read by attribute), ASCII chains and trees in a `text` fence,
Markdown tables, Markdown lists and one-line arrow chains. Each form is reduced to one shape
(elements, claims, groups, numbers), so a matrix drawn as a table and the same matrix drawn as a
flowchart meet the same key.

Rules the matcher applies, beyond r7 section 9.4:

  * A claim from an aggregate node (a node that names a group) is the group-level relation when
    the key states one with that group as its endpoint; its member pairs are then neither
    checked one by one nor matched against pair decoys.
  * Order is a path: `order` and `stage_order` of the key, and `order_violation` decoys, are
    checked on the directed paths of one figure, so a check drawn after another through any
    number of steps counts.
  * Coverage (Q10) is kept per relation, in the relation's own orientation. A relation with
    `directed: false` is covered by an edge in either direction; a directed relation only by an
    edge that runs its way, even when an undirected relation of the same pair is drawn.
  * Numbers that the key lists under `name_numbers` (section numbers, `Table 4.3`,
    `PostgreSQL 15`, `R6.1`) and digits inside identifiers are names, not numbers. A name number
    matches across any run of white space and across the lines of one label.
  * The decoy vocabulary is the `decoy_types` list of `evals.json`, passed to `compile_key`; a
    listed type the matcher has no rule for is a stress decoy that fails no check.

Names match as whole-token sequences after `normalize()`. The normalisation carries a version
string, `NORMALIZE_VERSION`, and `NORMALIZE_SHA256`, the sha256 of the source text of the rule;
the grader records both beside the full key hashes in every grading and report (TASK R11.2).

Review round 1 (TASK 108, before any grading):

  * A flowchart node that draws an entity another node draws already, under a first line that
    is not a stated name of it (`Picking DB replica` beside `Picking DB`), is an invented
    element (Q12). The same name drawn twice and a check shape about an entity are not; a soft
    alias maps only from the first line of a label (EI-04).
  * A box titled with a stated entity holds that entity or its parts (`part_of` in the key), and
    an edge to a part covers the relations of its container (EI-08). Toward a group box, a part
    counts as its container.
  * An edge with an end that maps to nothing stated is a relation the document does not state
    (Q09), as well as an invented element (Q12) (EI-30). A link between nodes that name several
    entities claims only its stated pairs when it states one (`push to merge request -> lint`).
  * A number in a sequence note belongs to the participants the note sits over and to the key
    entities it names; a `number_from_other_rule` decoy hits only when no subject the document
    gives the number is among the subjects (EI-10, R3). A `condition_as_entity` decoy hits when
    the figure draws every pair it lists: the condition placed between its stages.
  * Text on an ASCII link, beside a vertical link, or above a horizontal one is the label of
    that link, not a node; text over a junction of a fork or a join is a stage (EI-03, R5).
    ASCII figures outside fences are found by `parse_ascii_blocks`; lines that start with an
    arrow read as a chain (EI-01). In a document, an indented block must draw to be a figure,
    and an arrow glued to words on both sides is code (R4).
  * A caption's label may be plain, dotted or emphasised, and a cited file position
    (`PIPELINE.md:6-14`) is no number (EI-05). A caption's claims are read from its title and
    its claim sentence, the skill's form; later sentences claim nothing (EI-06, R1). A gantt
    figure shows the dates its bars cover, and a figure shows the step numbers it draws by
    `autonumber` or `1.` markers; such a number and a part of a date back only a caption number
    without a unit (EI-07, R2).
  * Fenced lines are found by the scan of `mermaid_model.extract_fences`, so a fence inside a
    blockquote holds no list, chain or table.

Standard library only.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import inspect
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import mermaid_model as _mm  # noqa: E402  (the fence scan every instrument shares)

#: Any change to `normalize()` or `tokens()` changes this string. The grader records it beside
#: the key hashes, so a key graded under another rule is visible.
NORMALIZE_VERSION = ("fidelity-normalize/1: NFC; strip HTML tags, Mermaid and HTML entities; "
                     "drop quote marks; casefold; fold yo to ye; tokens are runs of Unicode "
                     "letters and digits, Latin and Cyrillic alike")

#: The decoy types the matcher has a rule for. `evals.json` `decoy_types` is the vocabulary a key
#: may use (`compile_key(vocabulary=...)`); the selftest asserts that every listed type is here.
DECOY_TYPES = frozenset({
    "aggregation_needed", "boundary_edge", "calendar_rule", "caption_overclaim",
    "condition_as_entity", "cyrillic_labels", "dynamics_in_structure", "excluded_item",
    "invented_block", "invented_branch", "invented_dependency", "invented_entity",
    "invented_group", "invented_hub", "invented_number", "invented_state", "invented_writer",
    "k33_core", "long_payload", "lr_width", "number_from_other_rule", "order_violation",
    "reversed_direction", "unstated_relation", "v11_only_syntax", "wrong_form",
})

#: The headline check a decoy hit fails. `None`: a stress decoy, which the render, geometry,
#: budget or form checks measure; the matcher only reports the hit.
DECOY_CHECK = {
    "unstated_relation": "Q09", "reversed_direction": "Q09", "invented_dependency": "Q09",
    "invented_branch": "Q09", "invented_block": "Q09", "order_violation": "Q09",
    "condition_as_entity": "Q09",
    "number_from_other_rule": "Q11", "invented_number": "Q11", "calendar_rule": "Q11",
    "invented_group": "Q12", "invented_entity": "Q12", "invented_hub": "Q12",
    "invented_state": "Q12", "invented_writer": "Q12", "excluded_item": "Q12",
    "dynamics_in_structure": "Q08", "caption_overclaim": "Q13",
    "wrong_form": None, "boundary_edge": None, "aggregation_needed": None, "k33_core": None,
    "long_payload": None, "lr_width": None, "cyrillic_labels": None, "v11_only_syntax": None,
}

#: Decoy types whose aliases name an element a model is likely to draw.
ELEMENT_DECOYS = frozenset({"invented_entity", "invented_hub", "invented_state", "excluded_item"})

#: Decoy types whose aliases are looked for in edge, message and transition labels as well.
LABEL_DECOYS = frozenset({"dynamics_in_structure", "invented_branch"})

#: Decoy types that name a pair of entities: a claim of that pair hits them.
RELATION_DECOYS = frozenset({"unstated_relation", "reversed_direction", "invented_dependency",
                             "invented_branch", "order_violation", "condition_as_entity"})

#: Stress decoys the matcher cannot see in the source; the report shows them as not computed.
UNSEEN_DECOYS = frozenset({"aggregation_needed", "cyrillic_labels"})

#: Mermaid kinds the matcher models. Any other kind is reported `modelled: false`.
MODELLED_KINDS = ("flowchart", "sequence", "state", "gantt")

#: Sequence blocks that state control flow; `rect` and `box` are decoration.
CONTROL_BLOCKS = ("loop", "alt", "opt", "par", "critical", "break")

#: Claim kinds whose direction is an order (a path through them is an order of drawing).
ORDER_KINDS = ("edge", "order", "dependency", "transition")


class KeyInvalid(ValueError):
    """The key is malformed: an unknown endpoint, a duplicate id, a missing field."""


# =========================================================================== normalisation

_TAG = re.compile(r"<[^<>]{0,200}>")
_ENTITY = re.compile(r"#[A-Za-z0-9]{1,12};|&#?[A-Za-z0-9]{1,12};")
_QUOTES = "«»\"'`‘’“”„‚"
_TOKEN = re.compile(r"[^\W_]+")


def _clean(s) -> str:
    """NFC; tags and entities become spaces; quote marks are dropped. Idempotent."""
    s = unicodedata.normalize("NFC", str(s or ""))
    s = _TAG.sub(" ", s)
    s = _ENTITY.sub(" ", s)
    for q in _QUOTES:
        s = s.replace(q, "")
    return s


def _fold(token: str) -> str:
    return token.casefold().replace("ё", "е")


def tokens(s) -> list:
    """Normalised tokens of *s*: runs of letters and digits in any script, casefolded."""
    return [_fold(t) for t in _TOKEN.findall(_clean(s))]


def normalize(s) -> str:
    """*s* normalised per `NORMALIZE_VERSION`: its tokens joined by single spaces."""
    return " ".join(tokens(s))


def _normalize_source() -> str:
    """The text the normalisation rule is made of: the patterns and quote marks it uses and the
    source of `_clean`, `_fold`, `tokens` and `normalize`. A hand-written version string can
    stay the same while the code changes; this text cannot (EI-13)."""
    parts = [_TAG.pattern, _ENTITY.pattern, _QUOTES, _TOKEN.pattern]
    try:
        parts += [inspect.getsource(fn) for fn in (_clean, _fold, tokens, normalize)]
    except (OSError, TypeError):            # no source at hand: hash the whole module
        with open(__file__, encoding="utf-8") as fh:
            parts.append(fh.read())
    return "\n".join(parts)


#: sha256 of `_normalize_source()`; recorded with the key hashes in gradings and reports.
NORMALIZE_SHA256 = hashlib.sha256(_normalize_source().encode("utf-8")).hexdigest()


_BR = re.compile(r"<\s*br\s*/?\s*>|\\n|\n", re.IGNORECASE)


def label_lines(label) -> list:
    """Split a label at `<br/>`, `<br>` and `\\n`; drop tags and entities; keep visible lines."""
    out = []
    for part in _BR.split(str(label or "")):
        part = _ENTITY.sub(" ", _TAG.sub(" ", part)).replace("**", "").replace("__", "").strip()
        if part.strip("`*_ \"'"):
            out.append(part)
    return out


_CAMEL = re.compile(r"(?<=[a-zа-яё0-9])(?=[A-ZА-ЯЁ])")


def split_identifier(ident) -> str:
    """`WebShop` -> `Web Shop`, `web_shop` -> `web shop`: an id drawn as its own label."""
    return _CAMEL.sub(" ", str(ident)).replace("_", " ")


def jaccard(a, b) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


#: An ordinal step marker at the start of a label, made of digits and punctuation only.
ORDINAL_PREFIX = re.compile(r"^\s*(?:\(\s*\d{1,2}\s*\)|\d{1,2}\s*[.)])(?=\s|$)")


def ordinal_prefix(text) -> bool:
    """True when *text* starts with `1.`, `2)` or `(3)`. No word of any language is read."""
    return bool(ORDINAL_PREFIX.match(_clean(text)))


def _step_number(text) -> int:
    """The number of the step marker *text* starts with (see `ordinal_prefix`)."""
    return int(re.search(r"\d{1,2}", ORDINAL_PREFIX.match(_clean(text)).group(0)).group(0))


def _contains(toks, sub) -> bool:
    n = len(sub)
    if not n or n > len(toks):
        return False
    sub = tuple(sub)
    return any(tuple(toks[i:i + n]) == sub for i in range(len(toks) - n + 1))


# =========================================================================== numbers

_UNIT_TABLE = {
    "ms": ("ms", "msec", "millisecond", "milliseconds", "мс"),
    "s": ("s", "sec", "secs", "second", "seconds", "с", "сек", "секунд", "секунды",
          "секунда", "секунду"),
    "min": ("min", "mins", "minute", "minutes", "мин", "минут", "минуты", "минута", "минуту"),
    "h": ("h", "hr", "hrs", "hour", "hours", "ч", "час", "часа", "часов"),
    "d": ("d", "day", "days", "дн", "день", "дня", "дней", "сут", "суток", "сутки", "wd",
          "working days", "business days", "working day", "business day", "раб. дн",
          "раб. дня", "рабочих дня", "рабочих дней", "рабочий день", "working_day"),
    "w": ("w", "wk", "wks", "week", "weeks", "нед", "неделя", "недели", "недель"),
    "mo": ("mo", "month", "months", "мес", "месяц", "месяца", "месяцев"),
    "y": ("y", "yr", "yrs", "year", "years", "год", "года", "лет"),
    "%": ("%", "percent", "процент", "процента", "процентов"),
    "KB": ("kb", "кб"), "MB": ("mb", "мб"), "GB": ("gb", "гб"), "TB": ("tb", "тб"),
    "req/s": ("req/s", "requests/s", "request/s", "rps", "req/sec", "requests/sec",
              "requests per second", "запросов/с", "запросов в секунду"),
    "×": ("x", "×", "times", "time", "retries", "retry", "tries", "раз", "раза"),
    "attempts": ("attempts", "attempt", "попытки", "попыток", "попытка"),
    "$": ("$", "usd", "dollars"), "€": ("€", "eur"), "₽": ("₽", "rub", "руб"),
}
_UNIT_CANON = {}
for _canon, _names in _UNIT_TABLE.items():
    for _n in _names:
        _UNIT_CANON[_n.casefold()] = _canon
_UNIT_ALT = "|".join(sorted((re.escape(u) for u in _UNIT_CANON), key=len, reverse=True))
_NUM = re.compile(
    r"(?<![\w.,/\-])"                     # not the tail of an identifier: S3, v2, app-01
    r"(?P<cur>[$€£₽])?\s?"
    r"(?P<val>\d+(?:[.,]\d+)*)"
    r"(?:\s?(?P<unit>" + _UNIT_ALT + r")(?![^\W\d_]))?"
    r"(?![\w]|[.,]\d|-[^\W\d_])",         # not the head of an identifier: 2xx, 3-D
    re.IGNORECASE)
_DATE = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
_SECTION_REF = re.compile(r"§\s*\d+(?:\.\d+)*")
#: A cited position in a file, `ci/PIPELINE.md:6-14` or `SKILL.md:130`: a reference, not a
#: number a figure or caption claims. `strip_file_refs` finds its bounded tail and extends it
#: left over the path characters. The one-piece pattern `[\w./-]*\w\.[A-Za-z]\w{0,7}:\d+...`
#: restarted at every dot of a long path-like run: quadratic time (SEC2-09).
_FILE_REF_TAIL = re.compile(r"\w\.[A-Za-z]\w{0,7}:\d+(?:[-–]\d+)?")
_PATH_CHAR = re.compile(r"[\w./-]")


def strip_file_refs(text: str) -> str:
    """*text* with each cited file position replaced by one space, in linear time. The result
    equals `re.sub(r"[\\w./-]*\\w\\.[A-Za-z]\\w{0,7}:\\d+(?:[-–]\\d+)?", " ", text)`: a match
    starts where its run of path characters starts, or where the previous match ended."""
    out, pos = [], 0
    for m in _FILE_REF_TAIL.finditer(text):
        start = m.start()
        while start > pos and _PATH_CHAR.match(text, start - 1):
            start -= 1
        out += [text[pos:start], " "]
        pos = m.end()
    out.append(text[pos:])
    return "".join(out)


def canonical_unit(unit) -> str:
    u = str(unit or "").strip()
    if not u:
        return ""
    return _UNIT_CANON.get(u.casefold(), u.casefold())


def _num_value(raw: str):
    raw = raw.strip()
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+", raw):
        return float(raw.replace(",", ""))
    if raw.count(".") + raw.count(",") > 1:
        return None
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


@dataclass(frozen=True)
class Number:
    value: object  # float, or "YYYY-MM-DD" for a date
    unit: str      # canonical unit; "" when none is written
    raw: str


#: The unit of a number a figure shows without a unit of its own: a step number it draws, a
#: part of a date. It backs a caption number only when the caption writes no unit either (R2).
BARE = "#"


def extract_numbers(text) -> list:
    """Numbers with units in *text*. Digits inside identifiers (S3, v2, OAuth2, app-01, 3-D)
    and section references (`§2.4`) are not numbers. An ISO date is one number, unit `date`."""
    s = _SECTION_REF.sub(" ", strip_file_refs(_clean(text)))
    out = []
    for m in _DATE.finditer(s):
        out.append(Number(f"{m.group(1)}-{m.group(2)}-{m.group(3)}", "date", m.group(0)))
    s = _DATE.sub(" ", s)
    for m in _NUM.finditer(s):
        val = _num_value(m.group("val"))
        if val is None:
            continue
        unit = canonical_unit(m.group("unit")) if m.group("unit") else ""
        if m.group("cur"):
            unit = canonical_unit(m.group("cur"))
        out.append(Number(val, unit, m.group(0).strip()))
    return out


def _values_equal(a, b) -> bool:
    if isinstance(a, str) or isinstance(b, str):
        return str(a) == str(b)
    try:
        return abs(float(a) - float(b)) <= 1e-9
    except (TypeError, ValueError):
        return False


def numbers_equal(a, a_unit, b, b_unit, b_units=None) -> bool:
    """Same value; the units are equal, or one side writes none. *b_units*: further units the
    key accepts for *b* (its `unit_aliases`, canonical)."""
    if not _values_equal(a, b):
        return False
    ua, ub = canonical_unit(a_unit), canonical_unit(b_unit)
    if not ua or not ub or ua == ub:
        return True
    return bool(b_units) and ua in b_units


# =========================================================================== the key

@dataclass(frozen=True)
class Alias:
    toks: tuple
    target: str   # "entity" | "group" | "generic" | "decoy"
    tid: str
    soft: bool = False


@dataclass
class Rel:
    id: str
    src: str                 # raw endpoint: an entity id, a group id, or "[*]"
    dst: str
    src_set: frozenset       # entity ids after group expansion
    dst_set: frozenset
    directed: bool = True
    required: bool = True
    kind: str = "relation"   # the key's kind: call, write, message, transition, branch, ...
    source: str = "relations"  # relations | messages | transitions | tasks | decisions | matrix
    concern: str = ""
    reply: Optional[bool] = None
    label_aliases: tuple = ()
    writer: Optional[str] = None
    order: Optional[float] = None
    expand: str = "all_pairs"


@dataclass
class CKey:
    raw: dict
    entities: dict            # id -> {"kind", "names", "soft", "optional"}
    groups: dict              # id -> {"members", "names", "soft", "parallel"}
    relations: list           # [Rel]
    numbers: list             # [{"id", "value", "unit", "units", "subjects": set | None}]
    name_numbers: list        # [str] texts that are names, not numbers
    decoys: list              # [dict] with "_pairs", "_toks", "_value", "_unit", "_wrong"
    aliases: list             # [Alias], longest first
    writers: set
    caption_decoys: list      # [{"id", "toks": [tuple], "decoys": [decoy ids], "bare": bool}]
    initial: set
    final: set
    tasks: dict               # id -> task dict (gantt)
    calendar: dict
    blocks: list              # [{"id", "kinds": set, "messages": set}]
    message_order: list       # [(message id, message id)]
    element_order: list       # [(frozenset, frozenset)]: the first set comes before the second
    layers: list              # [frozenset]: stage layers in order
    required_any: list        # [[relation id]]
    matrix: Optional[dict]
    medium: str
    families: Optional[list]
    required_concern: str
    part_of: dict = field(default_factory=dict)   # part entity id -> container entity id


def _as_list(v) -> list:
    if v is None:
        return []
    if isinstance(v, (list, tuple, set, frozenset)):
        return list(v)
    return [v]


def _names_of(item: dict) -> list:
    names = []
    for k in ("name", "label", "title"):
        if isinstance(item.get(k), str) and tokens(item[k]):
            names.append(item[k])
    for a in _as_list(item.get("aliases")):
        if isinstance(a, str) and tokens(a):
            names.append(a)
    return names


def _label_toks(item: dict) -> tuple:
    out = []
    for k in ("label_aliases", "aliases", "keywords", "label_keywords", "condition_keywords",
              "label", "text"):
        for a in _as_list(item.get(k)):
            if isinstance(a, str) and tokens(a):
                out.append(tuple(tokens(a)))
    return tuple(dict.fromkeys(out))


def _ref_name(ref) -> str:
    if isinstance(ref, (list, tuple, set)):
        return "+".join(sorted(str(r) for r in ref))
    return str(ref)


def _num_or_none(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _key_value(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    s = str(v).strip()
    if _DATE.fullmatch(s):
        return s
    nv = _num_value(s)
    return nv if nv is not None else s


def _calendar_working(cal: dict) -> bool:
    """True when the key's calendar counts working days only (weekends excluded)."""
    if not cal:
        return False
    if cal.get("working_days") is True or cal.get("excludes_weekends") is True:
        return True
    blob = json.dumps(cal, ensure_ascii=False).casefold()
    return "weekend" in blob or "working" in blob or "saturday" in blob


def compile_key(key: dict, vocabulary=None) -> CKey:
    """Normalise a `mermaid-key/v1` dict into the matcher's model. Raises KeyInvalid.

    *vocabulary*: the decoy types a key may use, normally `evals.json` `decoy_types`; default
    `DECOY_TYPES`. A decoy of another type is a malformed key. A listed type without a rule of
    this module is accepted as a stress decoy: its hits are reported and fail no check.
    """
    if not isinstance(key, dict):
        raise KeyInvalid("the key is not a JSON object")
    allowed = frozenset(str(t) for t in vocabulary) if vocabulary is not None else DECOY_TYPES
    entities, groups, seen = {}, {}, set()

    def add_entity(item, kind_default):
        if not isinstance(item, dict):
            raise KeyInvalid(f"an entity is not an object: {item!r}"[:200])
        eid = item.get("id")
        if not isinstance(eid, str) or not eid:
            raise KeyInvalid(f"an entity without an id: {item!r}"[:200])
        if eid in entities:
            return
        if eid in seen:
            raise KeyInvalid(f"duplicate id {eid!r}")
        seen.add(eid)
        entities[eid] = {"kind": item.get("kind", kind_default), "names": _names_of(item),
                         "soft": [s for s in _as_list(item.get("soft_aliases"))
                                  if isinstance(s, str) and tokens(s)],
                         "optional": bool(item.get("optional")),
                         "part_of": item.get("part_of")}

    for item in _as_list(key.get("entities")):
        add_entity(item, "entity")
    for sec, kind in (("participants", "participant"), ("states", "state"),
                      ("writers", "writer"), ("stages", "stage"), ("roles", "role"),
                      ("operations", "operation"), ("outcomes", "outcome")):
        for item in _as_list(key.get(sec)):
            if isinstance(item, dict) and "id" in item:
                add_entity(item, kind)
    tasks = {}
    for item in _as_list(key.get("tasks")):
        if isinstance(item, dict) and "id" in item:
            add_entity(item, "task")
            tasks[item["id"]] = item
    part_of = {}
    for eid, e in entities.items():         # a stated part of a stated entity (EI-08)
        owner = e.get("part_of")
        if owner is None:
            continue
        if owner not in entities or owner == eid:
            raise KeyInvalid(f"entity {eid!r} is part_of {owner!r}, which is no other entity")
        part_of[eid] = owner

    for item in _as_list(key.get("groups")):
        gid = item.get("id") if isinstance(item, dict) else None
        if not isinstance(gid, str) or not gid:
            raise KeyInvalid(f"a group without an id: {item!r}"[:200])
        if gid in seen:
            raise KeyInvalid(f"duplicate id {gid!r}")
        seen.add(gid)
        groups[gid] = {"members_raw": _as_list(item.get("members")), "names": _names_of(item),
                       "soft": [s for s in _as_list(item.get("soft_aliases"))
                                if isinstance(s, str) and tokens(s)],
                       "parallel": bool(item.get("parallel"))}
    decisions = {d["id"]: d for d in _as_list(key.get("decisions"))
                 if isinstance(d, dict) and isinstance(d.get("id"), str)}

    def expand(ref, stack=()):
        if isinstance(ref, (list, tuple, set, frozenset)):
            out = set()
            for r in ref:
                out |= expand(r, stack)
            return out
        if ref == "[*]":
            return {"[*]"}
        if ref in entities:
            return {ref}
        if ref in groups:
            if ref in stack:
                raise KeyInvalid(f"group {ref!r} contains itself")
            out = set()
            for m in groups[ref]["members_raw"]:
                out |= expand(m, stack + (ref,))
            return out
        raise KeyInvalid(f"unknown endpoint or member {ref!r}")

    def resolve(ref):
        """An entity, a group, a decision (through its checks) or a list of them."""
        if isinstance(ref, (list, tuple, set)):
            out = set()
            for r in ref:
                out |= resolve(r)
            return out
        if ref in decisions and ref not in entities and ref not in groups:
            return resolve(_as_list(decisions[ref].get("checks")))
        return expand(ref)

    for gid, g in groups.items():
        g["members"] = frozenset(expand(gid))

    relations, rel_ids, pairs_seen = [], set(), set()

    def add_rel(rid, src, dst, skip_dup_pair=False, **kw):
        src_set, dst_set = frozenset(expand(src)), frozenset(expand(dst))
        pair_key = (src_set, dst_set)
        if skip_dup_pair and (pair_key in pairs_seen or (dst_set, src_set) in pairs_seen):
            return
        if rid in rel_ids:
            raise KeyInvalid(f"duplicate relation id {rid!r}")
        rel_ids.add(rid)
        pairs_seen.add(pair_key)
        relations.append(Rel(id=rid, src=_ref_name(src), dst=_ref_name(dst), src_set=src_set,
                             dst_set=dst_set, **kw))

    def req(item):
        return item.get("required", True) is not False

    for i, r in enumerate(_as_list(key.get("relations"))):
        rid = r.get("id") or f"rel{i + 1}"
        if "from" not in r or "to" not in r:
            raise KeyInvalid(f"relation {rid!r} lacks from or to")
        writer = r.get("writer")
        if writer is not None and writer not in entities:
            raise KeyInvalid(f"relation {rid!r} names unknown writer {writer!r}")
        add_rel(rid, r["from"], r["to"], directed=r.get("directed", True) is not False,
                required=req(r), kind=str(r.get("kind", "relation")), source="relations",
                concern=str(r.get("concern", "")), label_aliases=_label_toks(r), writer=writer,
                order=_num_or_none(r.get("order")), expand=str(r.get("expand", "all_pairs")))
    for i, m in enumerate(_as_list(key.get("messages"))):
        rid = m.get("id") or f"msg{i + 1}"
        if "from" not in m or "to" not in m:
            raise KeyInvalid(f"message {rid!r} lacks from or to")
        add_rel(rid, m["from"], m["to"], kind="message", source="messages", required=req(m),
                reply=m.get("reply"), label_aliases=_label_toks(m), concern="dynamics",
                order=_num_or_none(m.get("order", m.get("step"))))
    for i, t in enumerate(_as_list(key.get("transitions"))):
        rid = t.get("id") or f"tr{i + 1}"
        if rid in rel_ids:
            continue                     # the same transition listed under `relations`
        if "from" not in t or "to" not in t:
            raise KeyInvalid(f"transition {rid!r} lacks from or to")
        writer = t.get("writer")
        if writer is not None and writer not in entities:
            raise KeyInvalid(f"transition {rid!r} names unknown writer {writer!r}")
        add_rel(rid, t["from"], t["to"], kind="transition", source="transitions",
                required=req(t), writer=writer, label_aliases=_label_toks(t))
    for tid, t in tasks.items():
        for d in _as_list(t.get("deps", t.get("after"))):
            add_rel(f"{tid}<-{d}", d, tid, skip_dup_pair=True, kind="dependency",
                    source="tasks", required=True)
    if not any(r.kind == "branch" for r in relations):
        for did, d in decisions.items():
            for j, b in enumerate(_as_list(d.get("branches"))):
                if not isinstance(b, dict) or b.get("to") is None:
                    raise KeyInvalid(f"decision {did!r} has a branch without 'to'")
                add_rel(b.get("id") or f"{did}>{j + 1}", did, b["to"], kind="branch",
                        source="decisions", required=req(b), label_aliases=_label_toks(b))
    matrix = key.get("matrix")
    if matrix is not None:
        if not isinstance(matrix, dict):
            raise KeyInvalid("matrix is not an object")
        for ref in _as_list(matrix.get("rows")) + _as_list(matrix.get("cols")):
            expand(ref)
        for j, pair in enumerate(_as_list(matrix.get("allowed"))):
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise KeyInvalid(f"matrix.allowed[{j}] is not a [row, col] pair")
            add_rel(f"m:{pair[0]}:{pair[1]}", pair[0], pair[1], skip_dup_pair=True,
                    kind="matrix", source="matrix", directed=False, required=True)

    writers = {eid for eid, e in entities.items() if e["kind"] == "writer"}
    writers |= {r.writer for r in relations if r.writer}

    numbers = []
    for i, n in enumerate(_as_list(key.get("numbers"))):
        if not isinstance(n, dict) or "value" not in n:
            raise KeyInvalid(f"numbers[{i}] lacks a value")
        subj = n.get("subjects", n.get("subject"))
        units = {canonical_unit(u) for u in _as_list(n.get("unit_aliases")) if str(u).strip()}
        numbers.append({"id": n.get("id", f"n{i + 1}"), "value": _key_value(n["value"]),
                        "unit": canonical_unit(n.get("unit")), "units": units,
                        "subjects": set(_as_list(subj)) if subj not in (None, [], "") else None})
    name_numbers = [str(n.get("text") if isinstance(n, dict) else n)
                    for n in _as_list(key.get("name_numbers"))]
    name_numbers = sorted({t for t in name_numbers if t.strip()}, key=len, reverse=True)

    def pairs_of(rel):
        if isinstance(rel, str):
            found = [r for r in relations if r.id == rel]
            if not found:
                raise KeyInvalid(f"a decoy names unknown relation {rel!r}")
            return {(a, b) for r in found for a in r.src_set for b in r.dst_set if a != b}
        if isinstance(rel, dict):
            return {(a, b) for a in resolve(rel["from"]) for b in resolve(rel["to"]) if a != b}
        if isinstance(rel, list):
            out = set()
            for x in rel:
                out |= pairs_of(x)
            return out
        raise KeyInvalid(f"a decoy relation is neither an id nor an object: {rel!r}")

    decoys, dids = [], set()
    for i, d in enumerate(_as_list(key.get("decoys")) + _as_list(key.get("traps"))):
        if not isinstance(d, dict):
            raise KeyInvalid(f"decoy {i} is not an object")
        did = d.get("id") or f"d{i + 1}"
        if did in dids:
            raise KeyInvalid(f"duplicate decoy id {did!r}")
        if str(d.get("type")) not in allowed:
            raise KeyInvalid(f"decoy {did!r} has type {d.get('type')!r}, which the decoy "
                             f"vocabulary does not list")
        dids.add(did)
        dd = dict(d)
        dd["id"] = did
        rel = d.get("relation")
        if rel is None and isinstance(d.get("message"), dict):
            rel = d["message"]
        if rel is None and "from" in d and "to" in d:
            rel = {"from": d["from"], "to": d["to"]}
        if rel is None and d.get("relations") is not None:
            rel = [x for x in _as_list(d["relations"]) if isinstance(x, dict)]
        if rel is None and "before" in d and "after" in d:
            rel = {"from": d["before"], "to": d["after"]}
        dd["_pairs"] = pairs_of(rel) if rel is not None else set()
        toks = [tuple(tokens(a)) for a in _as_list(d.get("aliases")) if tokens(a)]
        if isinstance(d.get("message"), dict):
            toks += [tuple(tokens(a)) for a in _as_list(d["message"].get("label_keywords"))
                     if tokens(a)]
        toks += [tuple(tokens(a)) for a in _as_list(d.get("label_keywords")) if tokens(a)]
        toks += [tuple(tokens(a)) for a in _as_list(d.get("fields")) if tokens(a)]
        dd["_toks"] = list(dict.fromkeys(toks))
        if "value" in d:
            dd["_value"] = _key_value(d["value"])
            dd["_unit"] = canonical_unit(d.get("unit"))
        ws = d.get("wrong_subjects")
        dd["_wrong"] = set(_as_list(ws)) if ws else None
        decoys.append(dd)

    rank = {"entity": 0, "group": 1, "generic": 2, "decoy": 3}
    aliases = []
    for eid, e in entities.items():
        aliases += [Alias(tuple(tokens(n)), "entity", eid) for n in e["names"]]
        aliases += [Alias(tuple(tokens(n)), "entity", eid, True) for n in e["soft"]]
    for gid, g in groups.items():
        aliases += [Alias(tuple(tokens(n)), "group", gid) for n in g["names"]]
        aliases += [Alias(tuple(tokens(n)), "group", gid, True) for n in g["soft"]]
    for gen in _as_list(key.get("allowed_generic")):
        for n in ([gen] if isinstance(gen, str) else _names_of(gen)):
            if tokens(n):
                aliases.append(Alias(tuple(tokens(n)), "generic", f"generic:{normalize(n)}"))
    for d in decoys:
        if d.get("type") in ELEMENT_DECOYS:
            aliases += [Alias(tk, "decoy", d["id"]) for tk in d["_toks"]]
    aliases = list(dict.fromkeys(aliases))
    aliases.sort(key=lambda a: (-len(a.toks), rank[a.target], a.soft))

    caption_decoys = []
    for i, c in enumerate(_as_list(key.get("caption_claim_decoys"))
                          + _as_list(key.get("caption_claim_traps"))):
        if isinstance(c, str):
            caption_decoys.append({"id": f"c{i + 1}", "toks": [tuple(tokens(c))], "decoys": [],
                                   "bare": False})
        elif isinstance(c, dict):
            names = _as_list(c.get("claims")) + _as_list(c.get("aliases")) \
                + _as_list(c.get("pattern"))
            caption_decoys.append({"id": c.get("id", f"c{i + 1}"),
                                   "toks": [tuple(tokens(a)) for a in names if tokens(a)],
                                   "decoys": [], "bare": False})
    for d in decoys:                           # a caption_overclaim decoy hits a bare claim only
        if d.get("type") != "caption_overclaim":
            continue
        target = d.get("caption_claim")
        hit = [cd for cd in caption_decoys if target is not None and cd["id"] == target]
        if hit:
            hit[0]["decoys"].append(d["id"])
            hit[0]["bare"] = True
        elif d["_toks"]:
            caption_decoys.append({"id": d["id"], "toks": d["_toks"], "decoys": [d["id"]],
                                   "bare": True})

    initial, final = set(_as_list(key.get("initial"))), set(_as_list(key.get("final")))
    for ref in initial | final:
        expand(ref)
    blocks = []
    for i, b in enumerate(_as_list(key.get("blocks"))):
        if isinstance(b, dict):
            blocks.append({"id": b.get("id", f"b{i + 1}"),
                           "kinds": {str(k).casefold() for k in _as_list(b.get("kind"))},
                           "messages": set(_as_list(b.get("messages")))})
    msg_ids = {r.id for r in relations if r.source == "messages"}
    message_order, element_order = [], []

    def add_order(a, b):
        if a in msg_ids and b in msg_ids:
            message_order.append((a, b))
        else:
            element_order.append((frozenset(resolve(a)), frozenset(resolve(b))))

    order = key.get("order")
    if isinstance(order, list) and order and all(isinstance(o, str) for o in order):
        for a, b in zip(order, order[1:]):
            add_order(a, b)
    else:
        for o in _as_list(order):
            if isinstance(o, dict) and "first" in o and "then" in o:
                add_order(o["first"], o["then"])
            elif isinstance(o, (list, tuple)):
                for a, b in zip(o, o[1:]):
                    add_order(a, b)
    layers = []
    so = key.get("stage_order")
    for entry in _as_list(so.get("layers") if isinstance(so, dict) else so):
        layers.append(frozenset(resolve(_as_list(entry))))
    required_any = [[str(x) for x in _as_list(grp)] for grp in _as_list(key.get("required_any"))]
    for grp in required_any:
        for rid in grp:
            if rid not in rel_ids:
                raise KeyInvalid(f"required_any names unknown relation {rid!r}")
    fams = key.get("families")
    return CKey(raw=key, entities=entities, groups=groups, relations=relations, numbers=numbers,
                name_numbers=name_numbers, decoys=decoys, aliases=aliases, writers=writers,
                caption_decoys=caption_decoys, initial=initial, final=final, tasks=tasks,
                calendar=dict(key.get("calendar") or {}), blocks=blocks,
                message_order=message_order, element_order=element_order, layers=layers,
                required_any=required_any, matrix=matrix,
                medium=str(key.get("medium", "document")),
                families=list(fams) if isinstance(fams, list) else None,
                required_concern=str(key.get("required_concern") or key.get("concern") or ""),
                part_of=part_of)


# =========================================================================== alias matching

def find_aliases(toks, aliases, soft: bool = False) -> list:
    """Non-overlapping whole-token matches, longest first: `[(start, end, Alias)]` by start."""
    toks = list(toks)
    taken = [False] * len(toks)
    found = []
    for al in aliases:
        if al.soft != soft:
            continue
        n = len(al.toks)
        if not n or n > len(toks):
            continue
        for i in range(len(toks) - n + 1):
            if not any(taken[i:i + n]) and tuple(toks[i:i + n]) == al.toks:
                for k in range(i, i + n):
                    taken[k] = True
                found.append((i, i + n, al))
    found.sort(key=lambda f: f[0])
    return found


_NAME_NUMBER_RES = {}


def _name_number_re(text: str):
    """A pattern for one `name_numbers` text: its words in order, any run of white space between
    them, letter case ignored. None for a text without a visible character."""
    if text not in _NAME_NUMBER_RES:
        parts = [re.escape(p) for p in _clean(text).split()]
        _NAME_NUMBER_RES[text] = re.compile(r"\s+".join(parts), re.IGNORECASE) if parts else None
    return _NAME_NUMBER_RES[text]


def _blank_spans(cleaned: str, ck: CKey) -> str:
    """*cleaned* with every alias span and every `name_numbers` text blanked out. A name number
    counts only as a whole: no letter or digit may touch it on a side where it starts or ends
    with one."""
    chars = list(cleaned)
    for text in ck.name_numbers:
        pat = _name_number_re(text)
        if pat is None:
            continue
        for m in pat.finditer(cleaned):
            k, e = m.start(), m.end()
            if k == e:
                continue
            before = cleaned[k - 1] if k else " "
            after = cleaned[e] if e < len(cleaned) else " "
            if (before.isalnum() and cleaned[k].isalnum()) or \
                    (after.isalnum() and cleaned[e - 1].isalnum()):
                continue
            for j in range(k, e):
                chars[j] = " "
    spans = [(_fold(m.group(0)), m.start(), m.end()) for m in _TOKEN.finditer(cleaned)]
    for (i, j, _) in find_aliases([t for t, _, _ in spans], ck.aliases):
        for k in range(spans[i][1], spans[j - 1][2]):
            chars[k] = " "
    return "".join(chars)


def _numbers_of(text, ck: CKey) -> list:
    """Numbers of *text* outside alias spans, `name_numbers` and a leading step marker."""
    t = _clean(text)
    if ORDINAL_PREFIX.match(t):
        t = ORDINAL_PREFIX.sub(" ", t, count=1)
    return extract_numbers(_blank_spans(t, ck))


def _numbers_of_lines(lines, ck: CKey) -> list:
    """Numbers of the visible lines of one label, read as one text: a name number broken over
    two lines (`PostgreSQL<br/>15`) is still a name. A leading step marker leaves each line."""
    parts = []
    for ln in lines:
        t = _clean(ln)
        if ORDINAL_PREFIX.match(t):
            t = ORDINAL_PREFIX.sub(" ", t, count=1)
        parts.append(t)
    return extract_numbers(_blank_spans(" ".join(parts), ck))


@dataclass
class Element:
    """A drawn element: node, participant, state, task, stage, table row or column."""

    fid: str
    text: str
    kind: str
    ents: frozenset = frozenset()
    group: Optional[str] = None
    status: str = "invented"   # mapped | renamed | generic | invented | pseudo | annotation
    line: int = 0
    decoys: tuple = ()
    numbers: list = field(default_factory=list)
    subjects_extra: frozenset = frozenset()
    #: How the element was mapped: 3 an exact alias that covers the head of its line, 2 an exact
    #: alias with further words, 1 a soft alias, 0 a token Jaccard or nothing (EI-04).
    quality: int = 0
    via: tuple = ()          # the alias tokens that mapped it
    shape: str = ""          # flowchart node shape, as the parse model names it


#: Quality of an exact alias that covers the head of its line; see `Element.quality`.
COVERS = 3


def _quality(line: str, hits: list) -> int:
    """3 when the alias *hits* cover every token of the head of *line*, the part before its
    first clause break (an annotation after `(`, `:`, ` — ` or ` - ` is allowed); else 2."""
    head, _rest = _head_and_rest(line)
    n = len(tokens(head))
    covered = set()
    for (i, j, _al) in hits:
        covered.update(range(i, j))
    return COVERS if n and all(k in covered for k in range(n)) else 2


def _named_entities(text, ck: CKey) -> set:
    """The entities an exact alias of the key names in *text*."""
    return {h[2].tid for h in find_aliases(tokens(text), ck.aliases) if h[2].target == "entity"}


def map_text(lines, ck: CKey, kind: str, fid: str, line: int = 0,
             id_text: Optional[str] = None) -> Element:
    """Map the visible lines of one element to key entities (r7 section 9.4).

    The first line that names an entity decides: its entities are the element's. A line that
    names only a group makes an aggregate: the group's members plus every entity the label
    names. With no exact name, a soft alias or a token Jaccard of at least 0.6 maps the element
    and flags it renamed (contract check K07); then an allowed generic name; else the element
    is invented. `quality` and `via` record how it mapped, for the duplicate rule of `match`.
    """
    lines = [ln for ln in lines if tokens(ln)]
    renamed_id = False
    if not lines and id_text is not None:
        drawn = split_identifier(id_text)
        lines = [drawn]
        renamed_id = drawn != str(id_text)
    el = Element(fid=str(fid), text=" / ".join(lines), kind=kind, line=line)
    per_line = []
    for ln in lines:
        toks = tokens(ln)
        per_line.append((toks, find_aliases(toks, ck.aliases)))
    el.numbers.extend(_numbers_of_lines(lines, ck))
    el.decoys = tuple(sorted({h[2].tid for (_, hs) in per_line for h in hs
                              if h[2].target == "decoy"}))
    exact = "renamed" if renamed_id else "mapped"
    for ln, (toks, hs) in zip(lines, per_line):
        es = {h[2].tid for h in hs if h[2].target == "entity"}
        gs = [h[2].tid for h in hs if h[2].target == "group"]
        if es:
            el.ents, el.status = frozenset(es), exact
            named = [h for h in hs if h[2].target == "entity"]
            el.quality = _quality(ln, named)
            el.via = tuple(h[2].toks for h in named)
            return el
        if gs:
            members = set(ck.groups[gs[0]]["members"])
            for _, hs2 in per_line:
                members |= {h[2].tid for h in hs2 if h[2].target == "entity"}
            el.ents, el.group, el.status = frozenset(members), gs[0], exact
            el.quality = _quality(ln, [h for h in hs if h[2].target == "group"])
            return el
    for toks, _ in per_line[:1]:            # a soft alias in an annotation line maps nothing
        hs = find_aliases(toks, ck.aliases, soft=True)
        es = {h[2].tid for h in hs if h[2].target == "entity"}
        gs = [h[2].tid for h in hs if h[2].target == "group"]
        if es:
            el.ents, el.status, el.quality = frozenset(es), "renamed", 1
            el.via = tuple(h[2].toks for h in hs if h[2].target == "entity")
            return el
        if gs:
            el.ents, el.group = frozenset(ck.groups[gs[0]]["members"]), gs[0]
            el.status, el.quality = "renamed", 1
            return el
    if per_line:
        first = per_line[0][0]
        best, best_al = 0.0, None
        for al in ck.aliases:
            if al.target in ("entity", "group") and not al.soft:
                j = jaccard(first, al.toks)
                if j > best:
                    best, best_al = j, al
        if best_al is not None and best >= 0.6:
            if best_al.target == "entity":
                el.ents = frozenset({best_al.tid})
            else:
                el.ents, el.group = frozenset(ck.groups[best_al.tid]["members"]), best_al.tid
            el.status = "renamed"
            return el
    if any(h[2].target == "generic" for _, hs in per_line for h in hs):
        el.status = "generic"
        return el
    el.status = "invented"
    return el


# =========================================================================== common facts

@dataclass
class Claim:
    """One drawn relation between two elements."""

    src: Element
    dst: Element
    directed: bool = True
    label: str = ""
    kind: str = "edge"     # edge | message | transition | dependency | cell | order
    line: int = 0
    reply: Optional[bool] = None
    numbers: list = field(default_factory=list)
    to_subgraph: bool = False
    #: The drawn link a claim comes from, when one link between two multi-name ASCII nodes
    #: makes several claims; -1: the claim is its own link.
    edge: int = -1


@dataclass
class GroupBox:
    title: str
    members: frozenset
    kind: str          # subgraph | composite | section | box
    line: int = 0
    title_el: Optional[Element] = None


@dataclass
class Facts:
    """One figure reduced to the matcher's common shape."""

    form: str                    # mermaid:<kind> | text | table | list | chain
    index: int
    kind: str = ""
    line: int = 0
    source: str = ""
    direction: str = ""
    modelled: bool = True
    elements: list = field(default_factory=list)
    claims: list = field(default_factory=list)
    groups: list = field(default_factory=list)
    number_uses: list = field(default_factory=list)   # (Number, subjects | None, where)
    texts: list = field(default_factory=list)         # (text, where): notes and block labels
    unsupported: list = field(default_factory=list)   # Q09 findings an adapter made
    invented: list = field(default_factory=list)      # Q12 findings an adapter made
    bad_numbers: list = field(default_factory=list)   # Q11 findings an adapter made
    covered: set = field(default_factory=set)         # relation ids an adapter covered
    decoy_hits: dict = field(default_factory=dict)    # decoy id -> where
    ordinal_edges: int = 0
    messages: list = field(default_factory=list)      # sequence: message claims in order
    blocks: list = field(default_factory=list)        # sequence: (kind, label, start, end)
    statements: list = field(default_factory=list)    # gantt: other statements, casefolded
    diagnostics: list = field(default_factory=list)
    shown_dates: set = field(default_factory=set)     # gantt: ISO dates the bars cover (EI-07)
    shown_steps: set = field(default_factory=set)     # step numbers drawn, not written (EI-07)


def _where(f: Facts, line) -> str:
    return f"figure {f.index} line {line}"


def _type_hit(f: Facts, ck: CKey, dtype: str, where: str):
    for d in ck.decoys:
        if d.get("type") == dtype:
            f.decoy_hits.setdefault(d["id"], where)


# =========================================================================== flowchart

def facts_from_flowchart(fig, ck: CKey, index: int) -> Facts:
    fc = fig.flowchart
    fence = getattr(fig, "fence", None)
    f = Facts(form="mermaid:flowchart", index=index, kind="flowchart",
              line=getattr(fence, "start", 0), source=getattr(fence, "body", ""),
              direction=str(getattr(fc, "direction", "") or ""))
    els = {}
    for nid, node in (fc.nodes or {}).items():
        lab = str(getattr(node, "label", "") or "")
        el = map_text(label_lines(lab), ck, "node", nid, getattr(node, "line", 0),
                      id_text=nid if not tokens(lab) else None)
        el.shape = str(getattr(node, "shape", "") or "")
        els[nid] = el
        f.elements.append(el)
    subs = fc.subgraphs or {}

    def members_of(sid, stack=()):
        out = set()
        for m in getattr(subs[sid], "members", []) or []:
            if m in els:
                out |= set(els[m].ents)
            elif m in subs and m not in stack:
                out |= members_of(m, stack + (sid,))
        return frozenset(out)

    sub_els = {}
    for sid, sg in subs.items():
        mem = members_of(sid)
        title = sg.title if tokens(getattr(sg, "title", "")) else sid
        title_el = map_text(label_lines(title), ck, "group-title", sid, getattr(sg, "line", 0))
        f.groups.append(GroupBox(title=str(title), members=mem, kind="subgraph",
                                 line=getattr(sg, "line", 0), title_el=title_el))
        owner = _box_entity(title_el, mem, ck)
        sub_els[sid] = Element(fid=sid, text=f"subgraph {title}", kind="subgraph",
                               ents=frozenset({owner}) if owner else mem,
                               status="mapped" if (mem or owner) else "generic",
                               line=getattr(sg, "line", 0))
    for e in fc.edges or []:
        if getattr(e, "style", "solid") == "invisible":
            continue
        ends = []
        for ref in (e.src, e.dst):
            el = els.get(ref) or sub_els.get(ref)
            if el is None:
                el = map_text([], ck, "node", ref, e.line, id_text=ref)
                els[ref] = el
                f.elements.append(el)
            ends.append(el)
        a, b = ends
        lab = " ".join(label_lines(getattr(e, "label", "")))
        if lab and ordinal_prefix(lab):
            f.ordinal_edges += 1
            f.shown_steps.add(_step_number(lab))
        nums = _numbers_of(lab, ck) if lab else []
        to_sub = e.src in sub_els or e.dst in sub_els
        arrow = getattr(e, "arrow", "->")
        if a is b:
            for num in nums:
                f.number_uses.append((num, set(a.ents), _where(f, e.line)))
            f.texts.append((lab, _where(f, e.line)))
            continue
        if arrow == "<->":
            f.claims.append(Claim(a, b, True, lab, "edge", e.line, numbers=nums,
                                  to_subgraph=to_sub))
            f.claims.append(Claim(b, a, True, lab, "edge", e.line, to_subgraph=to_sub))
        else:
            f.claims.append(Claim(a, b, arrow != "none", lab, "edge", e.line, numbers=nums,
                                  to_subgraph=to_sub))
    return f


# =========================================================================== sequence

def facts_from_sequence(fig, ck: CKey, index: int) -> Facts:
    sq = fig.sequence
    fence = getattr(fig, "fence", None)
    f = Facts(form="mermaid:sequence", index=index, kind="sequence",
              line=getattr(fence, "start", 0), source=getattr(fence, "body", ""))
    els = {}

    def participant(pid, lab, line):
        el = map_text(label_lines(lab), ck, "participant", pid, line,
                      id_text=pid if not tokens(lab) else None)
        els[pid] = el
        f.elements.append(el)
        return el

    for p in sq.participants or []:
        participant(p.id, str(getattr(p, "label", "") or ""), getattr(p, "line", 0))
    if getattr(sq, "autonumber", False):     # the figure shows 1..N beside its messages
        f.shown_steps |= set(range(1, len(sq.messages or []) + 1))
    for m in sq.messages or []:
        for pid in (m.src, m.dst):
            if pid not in els:
                participant(pid, "", m.line)
        text = str(getattr(m, "text", "") or "")
        if ordinal_prefix(text):
            f.shown_steps.add(_step_number(text))
        reply = "--" in str(getattr(m, "arrow", "") or "")
        c = Claim(els[m.src], els[m.dst], True, text, "message", m.line, reply=reply,
                  numbers=_numbers_of(text, ck))
        f.claims.append(c)
        f.messages.append(c)
    for n in sq.notes or []:
        subj = set()
        for pid in getattr(n, "over", []) or []:
            if pid in els:
                subj |= set(els[pid].ents)
        named = _named_entities(getattr(n, "text", ""), ck)
        for num in _numbers_of(getattr(n, "text", ""), ck):
            # the numbers of a note belong to the participants it sits over and to the entities
            # it names, its subject or its target (EI-10, R3)
            f.number_uses.append((num, (named | subj) or None, _where(f, n.line)))
        f.texts.append((str(getattr(n, "text", "") or ""), _where(f, n.line)))
    f.blocks = [(str(b.kind).casefold(), str(getattr(b, "label", "") or ""), b.start, b.end)
                for b in (sq.blocks or [])]
    for (kind, label, start, _end) in f.blocks:
        if kind in CONTROL_BLOCKS:
            for num in _numbers_of(label, ck):
                f.number_uses.append((num, None, _where(f, start)))
    boxes = {}
    for p in sq.participants or []:
        box = getattr(p, "box", None)
        if box:
            boxes.setdefault(str(box), set()).update(els[p.id].ents)
    for title, mem in boxes.items():
        f.groups.append(GroupBox(title=title, members=frozenset(mem), kind="box",
                                 title_el=map_text(label_lines(title), ck, "group-title",
                                                   f"box:{title}", 0)))
    return f


# =========================================================================== state

def facts_from_state(fig, ck: CKey, index: int) -> Facts:
    st = fig.state
    fence = getattr(fig, "fence", None)
    f = Facts(form="mermaid:state", index=index, kind="state",
              line=getattr(fence, "start", 0), source=getattr(fence, "body", ""),
              direction=str(getattr(st, "direction", "") or ""))
    states = st.states or {}
    els, children = {}, {}
    for sid, s in states.items():
        if getattr(s, "parent", None):
            children.setdefault(s.parent, []).append(sid)
    for sid, s in states.items():
        if str(sid).startswith("[*]"):
            continue
        lab = str(getattr(s, "label", "") or "")
        if lab == sid:
            lab = ""
        el = map_text(label_lines(lab), ck, "state", sid, getattr(s, "line", 0),
                      id_text=sid if not tokens(lab) else None)
        if getattr(s, "kind", "state") in ("choice", "fork", "join") and el.status == "invented":
            el.status = "generic"          # a pseudo-state of the notation
        els[sid] = el
        if not getattr(s, "composite", False):
            f.elements.append(el)

    def members_of(sid, stack=()):
        out = set()
        for c in children.get(sid, []):
            if getattr(states[c], "composite", False):
                if c not in stack:
                    out |= members_of(c, stack + (sid,))
            elif c in els:
                out |= set(els[c].ents)
        return frozenset(out)

    for sid, s in states.items():
        if getattr(s, "composite", False):
            title = s.label if tokens(getattr(s, "label", "")) else sid
            f.groups.append(GroupBox(title=str(title), members=members_of(sid), kind="composite",
                                     line=getattr(s, "line", 0),
                                     title_el=map_text(label_lines(title), ck, "group-title",
                                                       sid, getattr(s, "line", 0))))
    pseudo = Element(fid="[*]", text="[*]", kind="pseudo", ents=frozenset({"[*]"}),
                     status="pseudo")
    for t in st.transitions or []:
        ends = []
        for ref in (t.src, t.dst):
            if str(ref).startswith("[*]"):
                ends.append(pseudo)
                continue
            if ref not in els:
                el = map_text([], ck, "state", ref, t.line, id_text=ref)
                els[ref] = el
                f.elements.append(el)
            ends.append(els[ref])
        lab = str(getattr(t, "label", "") or "")
        f.claims.append(Claim(ends[0], ends[1], True, lab, "transition", t.line,
                              numbers=_numbers_of(lab, ck)))
    for n in getattr(st, "notes", []) or []:
        f.texts.append((str(getattr(n, "text", "") or ""), _where(f, getattr(n, "line", 0))))
        for num in _numbers_of(getattr(n, "text", ""), ck):
            f.number_uses.append((num, None, _where(f, getattr(n, "line", 0))))
    return f


# =========================================================================== gantt

_DATE_FORMATS = {
    "YYYY-MM-DD": r"(?P<y>\d{4})-(?P<m>\d{1,2})-(?P<d>\d{1,2})",
    "DD.MM.YYYY": r"(?P<d>\d{1,2})\.(?P<m>\d{1,2})\.(?P<y>\d{4})",
    "DD-MM-YYYY": r"(?P<d>\d{1,2})-(?P<m>\d{1,2})-(?P<y>\d{4})",
    "YYYY/MM/DD": r"(?P<y>\d{4})/(?P<m>\d{1,2})/(?P<d>\d{1,2})",
    "DD/MM/YYYY": r"(?P<d>\d{1,2})/(?P<m>\d{1,2})/(?P<y>\d{4})",
    "MM/DD/YYYY": r"(?P<m>\d{1,2})/(?P<d>\d{1,2})/(?P<y>\d{4})",
}


def parse_gantt_date(text, date_format) -> Optional[str]:
    """`YYYY-MM-DD` for a date written in *date_format*, or None."""
    pat = _DATE_FORMATS.get(str(date_format or "YYYY-MM-DD").strip())
    if pat is None:
        return None
    m = re.fullmatch(pat, str(text).strip())
    if not m:
        return None
    try:
        return _dt.date(int(m.group("y")), int(m.group("m")), int(m.group("d"))).isoformat()
    except ValueError:
        return None


_DUR = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(ms|s|m|h|d|w|y)\s*$", re.IGNORECASE)


def parse_duration(text) -> Optional[tuple]:
    """`(value, unit)` of a gantt duration such as `4d`; a bare number counts days."""
    if text is None:
        return None
    if isinstance(text, (int, float)) and not isinstance(text, bool):
        return (float(text), "d")
    m = _DUR.match(str(text))
    if not m:
        return None
    unit = m.group(2).lower()
    return (float(m.group(1)), "min" if unit == "m" else unit)


def _key_duration(task: dict) -> Optional[tuple]:
    for k in ("duration_days", "days"):
        if task.get(k) is not None:
            v = _num_or_none(task[k])
            return (v, "d") if v is not None else None
    for k in ("duration", "est"):
        if task.get(k) is not None:
            return parse_duration(task[k])
    return None


def _task_dates(task: Optional[dict], which: str) -> set:
    """Dates a task accepts: `start` (or `at` for a milestone), or its explicit end dates."""
    out = set()
    if not task:
        return out
    keys = ("start", "start_date", "at") if which == "start" else \
        ("explicit_end_ok", "end", "end_date", "next_working_day")
    for k in keys:
        for v in _as_list(task.get(k)):
            if isinstance(v, str) and _DATE.fullmatch(v.strip()):
                out.add(v.strip())
    if which == "end" and not out:
        v = task.get("last_day")
        if isinstance(v, str) and _DATE.fullmatch(v.strip()):
            out |= _end_variants(v.strip())
    return out


def _end_variants(iso: str) -> set:
    """An end date written inclusive, or exclusive (the next calendar or working day)."""
    d = _dt.date.fromisoformat(iso)
    nxt = d + _dt.timedelta(days=1)
    out = {iso, nxt.isoformat()}
    while nxt.weekday() >= 5:
        nxt += _dt.timedelta(days=1)
    out.add(nxt.isoformat())
    return out


def _statement_texts(statements) -> list:
    out = []
    for s in statements or []:
        if isinstance(s, str):
            out.append(s)
        elif isinstance(s, dict) and s.get("keyword"):
            out.append(f"{s.get('keyword')} {s.get('value') or ''}".strip())
        elif isinstance(s, dict):
            out.append(str(s.get("text") or s.get("raw") or s.get("statement") or ""))
        elif isinstance(s, (list, tuple)) and s:
            out.append(next((str(x) for x in s if isinstance(x, str)), str(s[0])))
        else:
            out.append(str(s))
    return out


_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def _excluded_days(statements) -> tuple:
    """`(weekday numbers, ISO dates)` the `excludes` statements of a gantt remove: `weekends`
    is Saturday and Sunday; a weekday name or an ISO date removes that day."""
    weekdays, dates = set(), set()
    for s in statements or []:
        if not (isinstance(s, dict) and s.get("keyword") == "excludes"):
            continue
        for part in re.split(r"[\s,]+", str(s.get("value") or "").casefold()):
            if part == "weekends":
                weekdays |= {5, 6}
            elif part in _WEEKDAYS:
                weekdays.add(_WEEKDAYS.index(part))
            elif _DATE.fullmatch(part):
                dates.add(part)
    return weekdays, dates


def _mermaid_end(start, days: int, excluded) -> _dt.date:
    """The exclusive end of a bar of *days* calendar days from *start*: each excluded day the
    bar covers moves the end one day later, as mermaid's `fixTaskDates` does."""
    end = start + _dt.timedelta(days=days)
    d = start + _dt.timedelta(days=1)
    while d <= end:
        if excluded(d):
            end += _dt.timedelta(days=1)
        d += _dt.timedelta(days=1)
    return end


def gantt_schedule(g, date_format) -> dict:
    """`{task index: (start, last day, end)}` of a gantt figure, `datetime.date` values, the end
    exclusive, as mermaid places its bars. A start is a date, the latest end of the tasks that
    `after` names, or the end of the task before. A duration in days or weeks runs on calendar
    days and skips excluded days (`_mermaid_end`); an end written as a date is kept. A task
    whose start or end cannot be read is left out, and so is a task that waits for it."""
    weekdays, dates = _excluded_days(getattr(g, "statements", []))

    def excluded(d):
        return d.weekday() in weekdays or d.isoformat() in dates

    out, ends, prev_end = {}, {}, None
    for k, t in enumerate(g.tasks or []):
        raw = str(t.start or "").strip()
        start = None
        if raw.casefold().startswith("after"):
            refs = [ends.get(r) for r in raw.split()[1:]]
            if refs and all(r is not None for r in refs):
                start = max(refs)
        elif raw:
            iso = parse_gantt_date(raw, date_format)
            start = _dt.date.fromisoformat(iso) if iso else None
        else:
            start = prev_end
        end, dur = None, str(t.duration or "").strip()
        if start is not None and dur:
            iso_end = parse_gantt_date(dur, date_format)
            if iso_end:
                end = _dt.date.fromisoformat(iso_end)
            else:
                got = parse_duration(dur)
                if got is not None and got[1] in ("d", "w") and float(got[0]).is_integer():
                    end = _mermaid_end(start, int(got[0]) * (7 if got[1] == "w" else 1), excluded)
        prev_end = end
        if start is None or end is None:
            continue
        last = end - _dt.timedelta(days=1) if end > start else start
        while last > start and excluded(last):
            last -= _dt.timedelta(days=1)
        out[k] = (start, last, end)
        if t.id:
            ends[t.id] = end
    return out


def _shown_dates(g, date_format) -> set:
    """ISO dates a gantt figure shows without writing them: the start, the last day and the end
    of every bar it computes, and the day before a milestone, which a reader takes for the end
    of that day (EI-07)."""
    out = set()
    for start, last, end in gantt_schedule(g, date_format).values():
        out |= {start.isoformat(), last.isoformat(), end.isoformat()}
        if end == start:
            out.add((start - _dt.timedelta(days=1)).isoformat())
    return out


def facts_from_gantt(fig, ck: CKey, index: int) -> Facts:
    g = fig.gantt
    fence = getattr(fig, "fence", None)
    f = Facts(form="mermaid:gantt", index=index, kind="gantt",
              line=getattr(fence, "start", 0), source=getattr(fence, "body", ""))
    task_els, by_fid = [], {}
    for t in g.tasks or []:
        el = map_text(label_lines(t.label), ck, "task", t.id or t.label, t.line)
        if el.status in ("invented", "generic") and t.id:
            for tid in ck.tasks:
                if str(tid).casefold() == str(t.id).casefold():
                    el.ents, el.status = frozenset({tid}), "renamed"
        task_els.append((t, el))
        if t.id:
            by_fid[t.id] = el
        f.elements.append(el)
    sections = {}
    for t, el in task_els:
        if t.section:
            sections.setdefault(str(t.section), set()).update(el.ents)
    for title, mem in sections.items():
        f.groups.append(GroupBox(title=title, members=frozenset(mem), kind="section",
                                 title_el=map_text(label_lines(title), ck, "group-title",
                                                   f"section:{title}", 0)))
    f.statements = [s.strip().casefold() for s in _statement_texts(getattr(g, "statements", []))]
    required = [str(d.get("required_statement")).casefold() for d in ck.decoys
                if d.get("type") == "calendar_rule" and d.get("required_statement")]
    if ck.tasks and _calendar_working(ck.calendar):
        required.append("excludes weekends")
    for need in dict.fromkeys(required):
        want = " ".join(need.split())
        if not any(" ".join(s.split()).startswith(want) for s in f.statements):
            f.bad_numbers.append(f"figure {index}: the document's calendar needs `{need}`, "
                                 f"which the chart lacks")
            _type_hit(f, ck, "calendar_rule", f"figure {index}: no `{need}`")
    dfmt = getattr(g, "date_format", "") or "YYYY-MM-DD"
    f.shown_dates = _shown_dates(g, dfmt)
    for t, el in task_els:
        tids = [e for e in el.ents if e in ck.tasks]
        task = ck.tasks.get(tids[0]) if len(tids) == 1 else None
        subj = set(el.ents)
        start = str(t.start or "").strip()
        if start.casefold().startswith("after"):
            for ref in start.split()[1:]:
                dep = by_fid.get(ref)
                if dep is None:
                    f.unsupported.append(f"{_where(f, t.line)}: `after {ref}` names no task")
                    continue
                f.claims.append(Claim(dep, el, True, "", "dependency", t.line))
        elif start:
            iso = parse_gantt_date(start, dfmt)
            if iso:
                f.number_uses.append((Number(iso, "date", start), subj, _where(f, t.line)))
                want = _task_dates(task, "start")
                if want and iso not in want:
                    f.bad_numbers.append(f"{_where(f, t.line)}: {el.text!r} starts {iso}; the "
                                         f"document's calendar gives {sorted(want)[0]}")
                    _type_hit(f, ck, "invented_number", _where(f, t.line))
                elif want:
                    for d in _as_list(task.get("deps", task.get("after"))):
                        for r in ck.relations:
                            if d in r.src_set and tids[0] in r.dst_set and \
                                    r.kind == "dependency":
                                f.covered.add(r.id)
        dur = str(t.duration or "").strip()
        if dur:
            iso_end = parse_gantt_date(dur, dfmt)
            if iso_end:
                f.number_uses.append((Number(iso_end, "date", dur), subj, _where(f, t.line)))
                want_end = _task_dates(task, "end")
                if want_end and iso_end not in want_end:
                    f.bad_numbers.append(f"{_where(f, t.line)}: {el.text!r} ends {iso_end}; "
                                         f"the document's calendar accepts {sorted(want_end)}")
                    _type_hit(f, ck, "invented_number", _where(f, t.line))
            else:
                got = parse_duration(dur)
                if got is not None:
                    f.number_uses.append((Number(got[0], got[1], dur), subj, _where(f, t.line)))
                    want_d = _key_duration(task) if task else None
                    if want_d is not None and not (abs(got[0] - want_d[0]) < 1e-9
                                                   and got[1] == want_d[1]):
                        f.bad_numbers.append(f"{_where(f, t.line)}: {el.text!r} lasts {dur}; "
                                             f"the document states {want_d[0]:g}{want_d[1]}")
        tags = [str(x).casefold() for x in (t.tags or [])]
        if task is not None and "milestone" in tags and not task.get("milestone") \
                and ck.entities.get(tids[0], {}).get("kind") != "milestone":
            f.unsupported.append(f"{_where(f, t.line)}: {el.text!r} is drawn as a milestone")
    return f


# =========================================================================== ASCII

_ARROW_R = set(">►▶→⟶➜➔⇒▸")
_ARROW_L = set("<◄◀←⟵⇐◂")
_ARROW_D = set("▼↓⇓▾")
_ARROW_U = set("▲↑⇑▴^")
_ARROWS = _ARROW_R | _ARROW_L | _ARROW_D | _ARROW_U
_BOX_CHARS = {chr(c) for c in range(0x2500, 0x2580)}
_CONNECT_ONLY = set("|=+/\\") | _BOX_CHARS | _ARROWS
_TL, _TR, _BL, _BRC = set("┌╭+╔┏"), set("┐╮+╗┓"), set("└╰+╚┗"), set("┘╯+╝┛")
_HZ, _VT = set("─-═━="), set("│|║┃")


def _classify_line(line: str) -> list:
    """Per character: 'T' text, 'C' connector, ' ' gap."""
    n = len(line)
    cls = []
    for ch in line:
        if ch in " \t":
            cls.append(" ")
        elif ch.isalnum():
            cls.append("T")
        elif ch in _CONNECT_ONLY:
            cls.append("C")
        elif ch == "-":
            cls.append("?")
        else:
            cls.append("p")
    for i, ch in enumerate(line):
        if cls[i] == "?":
            left = line[i - 1] if i else " "
            right = line[i + 1] if i + 1 < n else " "
            cls[i] = "T" if left.isalnum() and right.isalnum() else "C"
    for i, ch in enumerate(line):       # a lone v is a down arrowhead
        if ch in "vV" and cls[i] == "T":
            left = cls[i - 1] if i else " "
            right = cls[i + 1] if i + 1 < n else " "
            if left in " C" and right in " C":
                cls[i] = "C"
    changed = True
    while changed:                      # punctuation touching text is text
        changed = False
        for i in range(n):
            if cls[i] == "p" and ((i and cls[i - 1] == "T") or (i + 1 < n and cls[i + 1] == "T")):
                cls[i] = "T"
                changed = True
    return ["C" if c == "p" else c for c in cls]


def _head_dir(ch: str):
    if ch in _ARROW_R:
        return (0, 1)
    if ch in _ARROW_L:
        return (0, -1)
    if ch in _ARROW_D or ch in "vV":
        return (1, 0)
    if ch in _ARROW_U:
        return (-1, 0)
    return None


def parse_ascii(body: str) -> dict:
    """Read an ASCII chain or tree in a `text` fence.

    Returns `{"nodes": [(text, row, node_id)], "edges": [(a, b)], "arrowheads": bool,
    "labels": {(a, b): [text]}, "free_labels": [(text, row)]}`. Runs of text are nodes; the
    text inside a drawn box is one node that owns its border. Connector cells are followed one
    by one, and one blank cell is crossed horizontally. Arrowheads met along a path give its
    direction. A figure without any arrowhead reads parent to child: a path that leaves a node's
    right or lower side and reaches another node's left or upper side.

    Text that labels a link is not a node (EI-03, ascii.md §5.1): a run between two connector
    cells of a line that no arrowhead enters (`──MQTT──▶`), a run beside a vertical link
    (`│ MQTT`), and a run above or below a horizontal link, alone on its row. A run over a
    junction of that link that opens toward it is a stage on a fork or a join (R5). A `+` opens
    toward the run unless a vertical link continues it on the far side: a label over the T of
    `build site ---+---> link check` stays a label. The label goes to every edge whose path runs
    through it or past the cell it sits on; a label no edge passes is free.
    """
    lines = [ln.replace("\t", "    ") for ln in body.split("\n")]
    width = max((len(ln) for ln in lines), default=0)
    lines = [ln.ljust(width) for ln in lines]
    rows = len(lines)
    cls = [_classify_line(ln) for ln in lines]
    segs = []                                      # (sid, row, c0, c1, text)
    for r, ln in enumerate(lines):
        c = 0
        while c < width:
            if cls[r][c] != "T":
                c += 1
                continue
            j = c
            while True:
                if j + 1 < width and cls[r][j + 1] == "T":
                    j += 1
                elif j + 2 < width and cls[r][j + 1] == " " and cls[r][j + 2] == "T":
                    j += 2
                else:
                    break
            segs.append((len(segs), r, c, j, ln[c:j + 1]))
            c = j + 1
    owner = {}
    for (sid, r, c0, c1, _) in segs:
        for c in range(c0, c1 + 1):
            owner[(r, c)] = sid
    node_of = {s[0]: s[0] for s in segs}
    border, boxed = {}, set()

    def at(r, c):
        return lines[r][c] if 0 <= r < rows and 0 <= c < width else " "

    def hz_join(r, c):
        """A cell inside a horizontal border: a line, a junction, or a pure-ASCII `+` that
        the border goes on past (a link leaves the box there)."""
        ch = at(r, c)
        return ch in _HZ or ch in "┬┴┼" or (ch == "+" and (at(r, c + 1) in _HZ
                                                           or at(r, c + 1) in "┬┴┼+"))

    def box_at(r, c):
        """`(bottom row, right column)` of a box whose top-left corner is at *r*, *c*; None."""
        corners, c2 = [], c + 1
        while True:                            # every `+` along the top may be the corner
            if at(r, c2) in _TR and c2 > c + 1:
                corners.append(c2)
            if not hz_join(r, c2):
                break
            c2 += 1
        r2 = r + 1
        while at(r2, c) in _VT or at(r2, c) in "├┤┼":
            r2 += 1
        if r2 == r + 1 or at(r2, c) not in _BL:
            return None
        for c2 in corners:
            if at(r2, c2) in _BRC and all(hz_join(r2, k) or at(r2, k) == "+"
                                          for k in range(c + 1, c2)) \
                    and all(at(k, c2) in _VT or at(k, c2) in "├┤┼+"
                            for k in range(r + 1, r2)):
                return r2, c2
        return None

    for r in range(rows):
        for c in range(width):
            if at(r, c) not in _TL:
                continue
            found = box_at(r, c)
            if found is None:
                continue
            r2, c2 = found
            inside = [s for s in segs if r < s[1] < r2 and s[2] > c and s[3] < c2]
            if not inside:
                continue
            head = inside[0][0]
            for s in inside:
                node_of[s[0]] = head
                boxed.add(s[0])
            for k in range(c, c2 + 1):
                border[(r, k)] = head
                border[(r2, k)] = head
            for k in range(r, r2 + 1):
                border[(k, c)] = head
                border[(k, c2)] = head

    def drawn(r, c):
        return 0 <= r < rows and 0 <= c < width and cls[r][c] == "C"

    def conn0(r, c):
        return drawn(r, c) and (r, c) not in border

    any_head = any(conn0(r, c) and _head_dir(lines[r][c]) is not None
                   for r in range(rows) for c in range(width))
    labels, label_cells = _link_labels(segs, boxed, lines, conn0, any_head, drawn)
    for sid in labels:
        for c in range(segs[sid][2], segs[sid][3] + 1):
            owner.pop((segs[sid][1], c), None)
    texts, first_row = {}, {}
    for (sid, r, _, _, text) in segs:
        if sid in labels:
            continue
        h = node_of[sid]
        texts.setdefault(h, []).append(text.strip())
        first_row.setdefault(h, r)

    def is_conn(r, c):
        return conn0(r, c) or (r, c) in label_cells

    def head_at(r, c):
        return None if (r, c) in label_cells else _head_dir(lines[r][c])

    def node_at(r, c):
        if (r, c) in border:
            return border[(r, c)]
        sid = owner.get((r, c))
        return node_of[sid] if sid is not None else None

    side_of_step = {(0, 1): "left", (0, -1): "right", (1, 0): "top", (-1, 0): "bottom"}
    into_dir = {"left": (0, 1), "right": (0, -1), "top": (1, 0), "bottom": (-1, 0)}

    def ports(nid):
        out = []
        cells = [k for k, v in border.items() if v == nid]
        if cells:
            r0, r1 = min(k[0] for k in cells), max(k[0] for k in cells)
            c0, c1 = min(k[1] for k in cells), max(k[1] for k in cells)
            for (r, c) in cells:
                for (dr, dc), side in (((-1, 0), "top"), ((1, 0), "bottom"),
                                       ((0, -1), "left"), ((0, 1), "right")):
                    rr, cc = r + dr, c + dc
                    if r0 <= rr <= r1 and c0 <= cc <= c1:
                        continue
                    if conn0(rr, cc):
                        out.append((rr, cc, side))
                    elif dc and at(rr, cc) == " " and conn0(rr, cc + dc):
                        out.append((rr, cc + dc, side))
            return out
        for (sid, r, c0, c1, _) in segs:
            if node_of[sid] != nid or sid in labels:
                continue
            for dc, side, edge in ((-1, "left", c0), (1, "right", c1)):
                if conn0(r, edge + dc):
                    out.append((r, edge + dc, side))
                elif at(r, edge + dc) == " " and conn0(r, edge + 2 * dc):
                    out.append((r, edge + 2 * dc, side))
            for c in range(c0, c1 + 1):
                for dr, side in ((-1, "top"), (1, "bottom")):
                    if conn0(r + dr, c):
                        out.append((r + dr, c, side))
        return out

    edges, paths = set(), {}
    for nid in sorted(texts):
        seen, queue, came = {}, [], {}
        for (r, c, side) in ports(nid):
            if head_at(r, c) == into_dir[side]:
                continue                       # an arrowhead into this node: an incoming line
            if (r, c) not in seen:
                seen[(r, c)] = (side, 0)
                came[(r, c)] = None
                queue.append((r, c))
        reached = {}
        qi = 0
        while qi < len(queue):
            r, c = queue[qi]
            qi += 1
            leave, score = seen[(r, c)]
            head = head_at(r, c)
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                if dr and (r, c) in label_cells:
                    continue                   # a label is crossed along its line only
                step_score = 0 if head is None else (1 if head == (dr, dc) else
                                                     (-1 if head == (-dr, -dc) else 0))
                for gap in ((1, 2) if dr == 0 else (1,)):
                    rr, cc = r + dr * gap, c + dc * gap
                    if gap == 2 and at(r, c + dc) != " ":
                        break
                    other = node_at(rr, cc)
                    if other is not None:
                        if other != nid:
                            arrive = side_of_step[(dr, dc)]
                            head_in = head == into_dir[arrive]
                            cand = (score + step_score, head_in, arrive, leave, (r, c))
                            prev = reached.get(other)
                            if prev is None or (cand[1], cand[0]) > (prev[1], prev[0]):
                                reached[other] = cand
                        break
                    if is_conn(rr, cc) and not (dr and (rr, cc) in label_cells):
                        if (rr, cc) not in seen:
                            seen[(rr, cc)] = (leave, score + step_score)
                            came[(rr, cc)] = (r, c)
                            queue.append((rr, cc))
                        break
        for other, (score, head_in, arrive, leave, last) in reached.items():
            if any_head:
                keep = head_in or score > 0
            else:
                keep = leave in ("right", "bottom") and arrive in ("left", "top")
            if keep:
                edges.add((nid, other))
                path, cell = set(), last
                while cell is not None:
                    path.add(cell)
                    cell = came.get(cell)
                paths[(nid, other)] = path
    edge_labels, free = {}, []
    for sid in sorted(labels):
        anchor = labels[sid]
        owners = [e for e in sorted(edges) if anchor & paths.get(e, set())]
        for e in owners:
            edge_labels.setdefault(e, []).append(segs[sid][4].strip())
        if not owners:
            free.append((segs[sid][4].strip(), segs[sid][1]))
    return {"nodes": [(" ".join(texts[n]), first_row[n], n) for n in sorted(texts)],
            "edges": sorted(edges), "arrowheads": any_head, "labels": edge_labels,
            "free_labels": free}


#: Characters that carry a horizontal or a vertical link, for the label rules of `parse_ascii`.
_HZ_LINK = _HZ | _ARROW_R | _ARROW_L | set("┬┴┼+")
_VT_LINK = _VT | _ARROW_D | _ARROW_U | set("├┤┼+vV")
#: Junctions of a horizontal link that open upward and downward. Text over a junction that opens
#: toward it sits on a fork or a join as a stage; it is no label of the link (R5). A box-drawing
#: junction opens by its shape. A pure-ASCII `+` has no shape: it opens toward the text unless a
#: vertical link continues it on the far side, where it is a T that opens away from the text.
#: Text that a vertical link meets on its other side is a stage of a chain all the same. Residual:
#: a first stage drawn right on a fork line whose middle `+` goes on down reads as a label.
_JOIN_UP = set("┴┼+└┘")
_JOIN_DOWN = set("┬┼+┌┐")


def _link_labels(segs: list, boxed: set, lines: list, conn, any_head: bool,
                 drawn=None) -> tuple:
    """`({segment id: anchor cells}, inline label cells)`: the text runs of an ASCII figure that
    label a link (see `parse_ascii`). *conn* tells a connector cell outside every box border;
    *drawn* tells a connector cell, on a box border or not."""
    width = len(lines[0]) if lines else 0
    drawn = drawn or conn

    def char(r, c):
        return lines[r][c] if 0 <= r < len(lines) and 0 <= c < width else " "

    def opens_toward(r, c, dr):
        """True when the junction at *r*, *c* of a horizontal link opens toward text on row
        *r* - *dr*. A `+` opens toward it unless a vertical link continues it on row *r* + *dr*
        (R5): `|`, `v`, `^`, another `+`, or a junction that opens back toward it."""
        joins = _JOIN_UP if dr == 1 else _JOIN_DOWN
        ch = char(r, c)
        if ch != "+":
            return ch in joins
        far = char(r + dr, c)
        return not (drawn(r + dr, c) and (far in _VT_LINK or far in joins))

    def chained(r, c, dr):
        """True when a vertical link meets the text cell *r*, *c* on its other side, row
        *r* - *dr*, away from the horizontal link on row *r* + *dr*: the text is a stage of a
        chain, such as a stage drawn on the line of a fork with an arrow into it (R5)."""
        ch = char(r - dr, c)
        return conn(r - dr, c) and (ch in _VT_LINK or ch in (_JOIN_DOWN if dr == 1 else _JOIN_UP))

    def beside(r, c, step):
        """The cell next to column *c* toward *step*, across one blank cell."""
        if char(r, c + step) == " " and char(r, c + 2 * step) != " ":
            return c + 2 * step
        return c + step

    labels, cells = {}, set()
    for (sid, r, c0, c1, _text) in segs:
        if sid in boxed:
            continue
        left, right = beside(r, c0, -1), beside(r, c1, 1)
        if any_head and conn(r, left) and conn(r, right) and char(r, left) in _HZ_LINK \
                and char(r, right) in _HZ_LINK and char(r, left) not in _ARROW_R \
                and char(r, right) not in _ARROW_L:
            span = {(r, c) for c in range(c0, c1 + 1)}
            labels[sid] = span                 # on the link: `──MQTT──▶`
            cells |= span
            continue
        if char(r, left) in _VT and char(r, right) in _VT:
            continue                           # framed on both sides: a box row, not a label
        for c in (left, right):
            if conn(r, c) and char(r, c) in _VT and (
                    (conn(r - 1, c) and char(r - 1, c) in _VT_LINK)
                    or (conn(r + 1, c) and char(r + 1, c) in _VT_LINK)):
                labels[sid] = {(r, c)}         # beside a vertical link: `│ MQTT`
                break
    free_rows = {}
    for (sid, r, c0, c1, _text) in segs:
        if sid in boxed or sid in labels:
            continue
        left, right = beside(r, c0, -1), beside(r, c1, 1)
        if conn(r, left) or conn(r, right):
            continue                           # it touches a link on its own row: a node
        free_rows[sid] = (r, c0, c1)
    changed = True
    while changed:                             # above or below a horizontal link, or stacked
        changed = False
        for sid, (r, c0, c1) in free_rows.items():
            if sid in labels:
                continue
            for dr in (1, -1):
                row = [(r + dr, c) for c in range(c0, c1 + 1)]
                if all(conn(*x) and char(*x) in _HZ_LINK for x in row) \
                        and not any(opens_toward(*x, dr) for x in row) \
                        and not any(chained(r, c, dr) for c in range(c0, c1 + 1)):
                    labels[sid] = {row[0]}
                    break
                stacked = [s for s, (rr, a, b) in free_rows.items()
                           if s in labels and rr == r + dr and a <= c1 and c0 <= b]
                if stacked:
                    labels[sid] = set(labels[stacked[0]])
                    break
            changed = changed or sid in labels
    return labels, cells


_BREAK = re.compile(r"\s[—–]\s|\s-\s|[(:;]|\.\s|\.$")


def _head_and_rest(text: str) -> tuple:
    m = _BREAK.search(text)
    return (text, "") if not m else (text[:m.start()], text[m.start():])


def map_chunk(text: str, ck: CKey, kind: str, fid: str, line: int) -> list:
    """Map one ASCII node, list item or chain link. The names before the first clause break
    are its elements; the rest is an annotation whose numbers attach to them."""
    head, _rest = _head_and_rest(text)
    nums = _numbers_of(text, ck)
    hits = [h for h in find_aliases(tokens(head), ck.aliases)
            if h[2].target in ("entity", "group", "decoy")]
    if not hits:
        el = map_text([head] if tokens(head) else [text], ck, kind, fid, line)
        el.numbers = nums
        return [el]
    out = []
    for k, (_, _, al) in enumerate(hits):
        el = Element(fid=f"{fid}#{k}", text=" ".join(al.toks), kind=kind, line=line)
        if al.target == "entity":
            el.ents, el.status = frozenset({al.tid}), "mapped"
        elif al.target == "group":
            el.ents, el.group, el.status = ck.groups[al.tid]["members"], al.tid, "mapped"
        else:
            el.status, el.decoys = "invented", (al.tid,)
        out.append(el)
    shared = frozenset().union(*(o.ents for o in out))
    for el in out:
        el.subjects_extra = shared
    out[0].numbers = nums
    return out


def facts_from_ascii(body: str, ck: CKey, index: int, line_offset: int = 0) -> Facts:
    """An ASCII figure. A fence whose lines all start with ordinals or bullets reads as a list."""
    f = Facts(form="text", index=index, kind="ascii", source=body, line=line_offset)
    lines = body.split("\n")
    item_re = re.compile(r"^\s*(?:\d{1,2}[.)]|[-*+])\s+(\S.*)$")
    nonblank = [ln for ln in lines if ln.strip()]
    listed = [ln for ln in nonblank if item_re.match(ln)]
    if len(listed) >= 2 and len(listed) == len(nonblank):
        items = [(item_re.match(ln).group(1), line_offset + k + 1, 0)
                 for k, ln in enumerate(lines) if item_re.match(ln)]
        _facts_from_items(f, items, ck, ordered=True)
        return f
    led = [ln for ln in nonblank if _ARROW_LEAD.match(ln.replace("\t", "    "))]
    drawn = [ln for ln in nonblank if _link_line(ln) and ln not in led]
    if len(led) >= 2 and not drawn:            # `-> stage` lines, one per line
        _facts_from_arrow_lines(f, [(ln, k + 1) for k, ln in enumerate(lines)], ck, line_offset)
        return f
    g = parse_ascii(body)
    nodes = {}
    for (text, row, nid) in g["nodes"]:
        nodes[nid] = (row, map_chunk(text, ck, "stage", f"n{nid}", line_offset + row + 1))
    connected = {a for a, _ in g["edges"]} | {b for _, b in g["edges"]}
    for nid, (row, els) in nodes.items():
        for el in els:
            if el.status == "invented" and nid not in connected:
                el.status = "annotation"
            f.elements.append(el)
    for k, (a, b) in enumerate(g["edges"]):
        lab = " ".join(g.get("labels", {}).get((a, b), []))
        nums = _numbers_of(lab, ck) if lab else []
        for ea in nodes[a][1]:
            for eb in nodes[b][1]:
                f.claims.append(Claim(ea, eb, True, lab, "edge", ea.line, numbers=nums, edge=k))
                nums = []                      # the numbers of a label count once
    for (text, row) in g.get("free_labels", []):
        f.texts.append((text, f"figure {index} line {line_offset + row + 1}"))
        for num in _numbers_of(text, ck):
            f.number_uses.append((num, None, f"figure {index} line {line_offset + row + 1}"))
    by_row = {}
    for nid, (row, els) in nodes.items():
        by_row.setdefault(row, []).extend(e for e in els if e.status != "annotation")
    for nid, (row, els) in nodes.items():
        for el in els:
            if el.status != "annotation":
                continue
            f.texts.append((el.text, f"figure {index} line {el.line}"))
            if not el.numbers:
                continue
            mates, r = [], row
            while r >= 0 and not mates:
                mates = by_row.get(r, [])
                r -= 1
            subj = set().union(*(set(m.ents) for m in mates)) if mates else None
            for num in el.numbers:
                f.number_uses.append((num, subj, f"figure {index} line {el.line}"))
            el.numbers = []
    return f


# =========================================================================== lists and chains

_LIST_ITEM = re.compile(r"^(?P<ind>[ \t]*)(?P<mark>\d{1,3}[.)]|[-*+])\s+(?P<text>\S.*)$")
#: An arrow inside a line of text. It holds no whitespace and a run of `─` matches from its
#: first character only: `\s*` around the arrow, and a `─+` tried at every character of a run,
#: cost quadratic time on a long line (SEC2-09). `split_arrows` strips the spaces next to it.
_INLINE_ARROW = re.compile(r"-{1,2}>|(?<!─)─+[>►]|=>|→|⟶|➜|➔|⇒")


def split_arrows(text: str) -> list:
    """The parts of *text* between its inline arrows, without the whitespace next to an arrow:
    the split at `\\s*(?:<arrow>)\\s*` the matcher used before, in linear time (SEC2-09)."""
    parts = _INLINE_ARROW.split(text)
    out = []
    for i, part in enumerate(parts):
        if i > 0:
            part = part.lstrip()
        if i < len(parts) - 1:
            part = part.rstrip()
        out.append(part)
    return out


def fenced_line_ranges(text: str) -> list:
    """1-based inclusive `(start, end)` of every fenced block, any info string, as the scan of
    `mermaid_model.extract_fences` finds them: a fence inside a blockquote counts, an indented
    code block does not, and a fence that its blockquote ends stops there."""
    lines = str(text).split("\n")
    if lines and lines[0].startswith("\ufeff"):
        lines[0] = lines[0][1:]
    n = len(lines)
    return [(o + 1, min(c, n - 1) + 1) for (o, c, _info, _ind) in _mm._fence_spans(lines)]


def _fenced_lines(text: str) -> set:
    inside = set()
    for a, b in fenced_line_ranges(text):
        inside.update(range(a, b + 1))
    return inside


def parse_lists(text: str) -> list:
    """Markdown lists outside fences:
    `[{"start", "end", "ordered", "items": [(text, line, level)]}]`."""
    infence = _fenced_lines(text)
    blocks, cur, blank = [], None, False
    for k, ln in enumerate(text.split("\n"), start=1):
        m = _LIST_ITEM.match(ln) if k not in infence else None
        if m:
            level = len(m.group("ind").replace("\t", "    ")) // 2
            if cur is None:
                cur = {"start": k, "end": k, "ordered": m.group("mark")[0].isdigit(), "items": []}
            cur["items"].append([m.group("text").strip(), k, level])
            cur["end"], blank = k, False
        elif cur is not None and k not in infence and ln.strip() and ln[:1] in (" ", "\t"):
            cur["items"][-1][0] += " " + ln.strip()
            cur["end"], blank = k, False
        elif cur is not None and not ln.strip() and not blank:
            blank = True
        else:
            if cur is not None:
                blocks.append(cur)
            cur, blank = None, False
    if cur is not None:
        blocks.append(cur)
    for b in blocks:
        b["items"] = [tuple(i) for i in b["items"]]
    return blocks


def _facts_from_items(f: Facts, items: list, ck: CKey, ordered: bool):
    """Top-level items in order; nested items join their parent and run in parallel.
    Consecutive top-level items of an ordered list are order claims; an arrow inside an item
    chains its parts."""
    tops = []
    for (text, line, level) in items:
        if level == 0 or not tops:
            tops.append([(text, line)])
        else:
            tops[-1].append((text, line))
    prev_tails = None
    for k, group in enumerate(tops):
        heads, tails = [], []
        for gi, (text, line) in enumerate(group):
            parts = [p for p in split_arrows(text) if tokens(p)]
            chain = [map_chunk(p, ck, "stage", f"i{k}.{gi}.{j}", line) for j, p in enumerate(parts)]
            if gi == 0 and len(group) > 1 and len(chain) == 1 and all(
                    e.status == "invented" and not e.decoys for e in chain[0]):
                for e in chain[0]:
                    e.status = "annotation"     # a heading over nested items
                f.elements.extend(chain[0])
                continue
            for a, b in zip(chain, chain[1:]):
                for ea in a:
                    for eb in b:
                        f.claims.append(Claim(ea, eb, True, "", "order", line))
            for part in chain:
                f.elements.extend(part)
            if chain:
                heads.extend(chain[0])
                tails.extend(chain[-1])
        if ordered and prev_tails is not None:
            for ea in prev_tails:
                for eb in heads:
                    f.claims.append(Claim(ea, eb, True, "", "order", eb.line))
        if heads:
            prev_tails = tails


def facts_from_list(block: dict, ck: CKey, index: int) -> Facts:
    f = Facts(form="list", index=index, kind="list", line=block["start"])
    _facts_from_items(f, list(block["items"]), ck, ordered=bool(block.get("ordered")))
    return f


def parse_chains(text: str) -> list:
    """Lines outside fences, tables and lists that chain names with arrows: `a → b → c`.
    Returns `[{"line", "text"}]`."""
    infence = _fenced_lines(text)
    out = []
    for k, ln in enumerate(text.split("\n"), start=1):
        if k in infence or "|" in ln or _LIST_ITEM.match(ln):
            continue
        if len([p for p in split_arrows(ln) if tokens(p)]) >= 2:
            out.append({"line": k, "text": ln.strip()})
    return out


def facts_from_chain(chain: dict, ck: CKey, index: int) -> Facts:
    f = Facts(form="chain", index=index, kind="chain", line=chain["line"])
    _facts_from_items(f, [(chain["text"], chain["line"], 0)], ck, ordered=True)
    return f


# =========================================================================== ASCII outside fences

#: A line of an ASCII figure that starts with an arrow: `-> lint`, `→ unit tests`.
_ARROW_LEAD = re.compile(r"^(?P<ind>[ \t]*)(?:-{1,3}>|={1,2}>|[→⟶➜➔⇒▶►])[ \t]*"
                         r"(?P<text>\S.*)$")
#: An arrow inside a line: `a -> b`, `a <-- b`, `a ──▶ b`, `▼`. An arrow glued to a word on both
#: sides is code, `$client->call` or `x-->0`, not a link (R4).
_ANY_ARROW = re.compile(r"(?<![\w$-])-{1,3}>|-{1,3}>(?![\w$])|<-{1,3}"
                        r"|(?<![\w$=])={1,2}>|={1,2}>(?![\w$])|[→⟶➜➔⇒▶►◀◄←▼▲↓↑]")
#: Characters of a line that only draws links: `|`, `v`, `+------+`, `│`, `▼`.
_LINK_ONLY = _CONNECT_ONLY | set("-vV^<> ")
_LINK_MARK = set("|│┃║+┼┬┴├┤└┘┌┐╭╮╯╰vV▼▲^")


def _indent(line: str) -> int:
    return len(line.replace("\t", "    ")) - len(line.replace("\t", "    ").lstrip(" "))


def _link_line(line: str) -> bool:
    """True for a line that draws links only (`|`, `+-----+`, `v`) or starts with an arrow."""
    s = line.strip()
    if not s:
        return False
    if _ARROW_LEAD.match(line.replace("\t", "    ")):
        return True
    return all(ch in _LINK_ONLY for ch in s) and any(ch in _LINK_MARK for ch in s)


def parse_ascii_blocks(text: str, terminal: bool = False) -> list:
    """ASCII figures written outside a fence: `[{"start", "end", "body"}]`, 1-based lines.

    An indented code block (lines indented by 4 or more columns, after a blank line) renders as
    preformatted text in every viewer, as a bare fence does. In a document it is a figure when
    it draws: one of its lines draws links only or starts with an arrow and another line draws
    or carries an arrow, or one line chains three elements. Two lines with one arrow each read
    as a legend or as code there (R4). In a medium that prints text as typed (a terminal), an
    indented block is a figure when two of its lines draw links or carry an arrow, and a run of
    lines is a figure when two of its lines draw links only or start with an arrow (`-> lint`).
    Lines in fences, tables and lists are skipped. The body loses the indent its lines share
    (EI-01).
    """
    lines = text.split("\n")
    skip = _fenced_lines(text)
    for t in parse_tables(text):
        skip.update(range(t["start"], t["end"] + 1))
    for lb in parse_lists(text):
        skip.update(range(lb["start"], lb["end"] + 1))
    out, k, n = [], 0, len(lines)

    def run_end(i):
        while i + 1 < n and lines[i + 1].strip() and (i + 2) not in skip:
            i += 1
        return i

    while k < n:
        if (k + 1) in skip or not lines[k].strip():
            k += 1
            continue
        j = run_end(k)
        indented = (k == 0 or not lines[k - 1].strip()) and all(
            _indent(ln) >= 4 for ln in lines[k:j + 1])
        while indented:                        # an indented block goes on past a blank line
            m = j + 1
            while m < n and not lines[m].strip():
                m += 1
            if m >= n or (m + 1) in skip or _indent(lines[m]) < 4:
                break
            e = run_end(m)
            if not all(_indent(ln) >= 4 for ln in lines[m:e + 1]):
                break
            j = e
        run = [ln for ln in lines[k:j + 1] if ln.strip()]
        links = sum(1 for ln in run if _link_line(ln))
        arrows = [len(_ANY_ARROW.findall(ln)) for ln in run]
        drawn = sum(1 for ln, a in zip(run, arrows) if a or _link_line(ln))
        if terminal:
            figure = (indented and (drawn >= 2 or max(arrows) >= 2)) or links >= 2
        else:                                  # a document: the block must draw (R4)
            figure = indented and ((links >= 1 and drawn >= 2) or max(arrows) >= 2)
        if figure:
            cut = min(_indent(ln) for ln in run)
            body = "\n".join(ln.replace("\t", "    ")[cut:].rstrip() if ln.strip() else ""
                             for ln in lines[k:j + 1])
            out.append({"start": k + 1, "end": j + 1, "body": body})
        k = j + 1
    return out


def _facts_from_arrow_lines(f: Facts, rows: list, ck: CKey, line_offset: int):
    """An ASCII figure drawn as lines that start with an arrow, one stage per line:

        push
         -> lint
         -> build site
             -> link check            the deeper lines run in parallel after the line above
             -> accessibility check
         -> deploy preview            and the next line at the first depth waits for them all

    Lines before the first arrow are its roots. Text after a gap of two or more spaces is a
    note on that stage; a line without an arrow after the first arrow is a note too (EI-01).
    """
    items, notes = [], []
    seen_arrow = False
    for ln, no in rows:
        m = _ARROW_LEAD.match(ln.replace("\t", "    "))
        if m:
            seen_arrow = True
            items.append((m.group("text"), len(m.group("ind")), True, line_offset + no))
        elif ln.strip() and not seen_arrow:
            items.append((ln.strip(), _indent(ln), False, line_offset + no))
        elif ln.strip():
            notes.append((ln.strip(), line_offset + no))
    base = min(i[1] for i in items if i[2])
    last_top, branch, links = [], [], 0      # [(item, elements)] of the line(s) to follow
    for k, (text, ind, arrow, no) in enumerate(items):
        parts = re.split(r"\s{2,}", text.strip(), maxsplit=1)
        stage, note = parts[0], (parts[1] if len(parts) > 1 else "")
        els = map_chunk(stage, ck, "stage", f"a{k}", no)
        if note.strip():
            f.texts.append((note.strip(), f"figure {f.index} line {no}"))
            els[0].numbers = list(els[0].numbers) + _numbers_of(note, ck)
        f.elements.extend(els)
        if arrow and ind > base and last_top:
            sources = last_top
            branch.append(els)
        else:
            sources = branch or last_top
            last_top, branch = [els], []
        for src in sources:                      # one drawn link per pair of lines
            for ea in src:
                for eb in els:
                    f.claims.append(Claim(ea, eb, True, "", "edge", no, edge=links))
            links += 1
    for text, no in notes:
        f.texts.append((text, f"figure {f.index} line {no}"))
        subj = set().union(*(set(e.ents) for els in last_top for e in els)) if last_top else None
        for num in _numbers_of(text, ck):
            f.number_uses.append((num, subj, f"figure {f.index} line {no}"))


# =========================================================================== tables

_POS_MARKS = {"yes", "y", "да", "allowed", "allow", "permitted", "true", "x"}
_NEG_MARKS = {"no", "n", "нет", "denied", "deny", "forbidden", "false"}


def cell_mark(cell) -> str:
    """`pos`, `neg` or `other` for a matrix cell: yes/no, check/cross, dash, +/-, x, blank.
    A cell is read by its first mark, so `yes (own drafts)` is positive."""
    s = _clean(cell).replace("*", "").replace("`", "").strip()
    if s in ("", "-", "—", "–", "−", "·"):
        return "neg"
    if s[0] in "✓✔✅☑●+":
        return "pos"
    if s[0] in "✗✘❌☒":
        return "neg"
    first = s.split()[0].strip(".,;:()[]!").casefold()
    if first in _POS_MARKS:
        return "pos"
    if first in _NEG_MARKS:
        return "neg"
    return "other"


def _split_row(line: str) -> list:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur, prev = [], "", ""
    for ch in s:
        if ch == "|" and prev != "\\":
            cells.append(cur.strip())
            cur = ""
        else:
            cur += ch
        prev = ch
    cells.append(cur.strip())
    return cells


#: The delimiter row of a Markdown table, matched against the stripped line: the leading and
#: trailing `\s*` of `^\s*\|?\s*:?-+...\|?\s*$` cost quadratic time on a long blank run
#: (SEC2-09). Stripping first matches the same lines.
_SEP = re.compile(r"^\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?$")


def parse_tables(text: str) -> list:
    """Markdown tables outside fences:
    `[{"start", "end", "header": [cells], "rows": [(cells, line)]}]`."""
    infence = _fenced_lines(text)
    lines = text.split("\n")
    out, k = [], 0
    while k < len(lines) - 1:
        if (k + 1) not in infence and "|" in lines[k] and "-" in lines[k + 1] \
                and _SEP.match(lines[k + 1].strip()):
            header, rows, j = _split_row(lines[k]), [], k + 2
            while j < len(lines) and "|" in lines[j] and lines[j].strip() \
                    and (j + 1) not in infence:
                rows.append((_split_row(lines[j]), j + 1))
                j += 1
            out.append({"start": k + 1, "end": j, "header": header, "rows": rows})
            k = j
        else:
            k += 1
    return out


def facts_from_table(table: dict, ck: CKey, index: int) -> Facts:
    """A table. Header cells after the first and first-column cells are elements; a positive
    mark in a body cell claims the pair of its row and column, in either orientation."""
    f = Facts(form="table", index=index, kind="table", line=table["start"])
    cols = {c: map_text([cell], ck, "col", f"h{c}", table["start"])
            for c, cell in enumerate(table["header"]) if c >= 1}
    rows = {r: map_text([cells[0]], ck, "row", f"r{r}", line)
            for r, (cells, line) in enumerate(table["rows"]) if cells}
    marked_c, marked_r = set(), set()
    marks = {}
    for r, (cells, line) in enumerate(table["rows"]):
        for c in cols:
            val = cells[c] if c < len(cells) else ""
            mk = cell_mark(val)
            marks[(r, c)] = (mk, val, line)
            if mk != "other" and val.strip():
                marked_c.add(c)
                marked_r.add(r)
    for c, el in cols.items():
        if el.status == "invented" and c not in marked_c:
            el.status = "annotation"
        f.elements.append(el)
    for r, el in rows.items():
        if el.status == "invented" and r not in marked_r:
            el.status = "annotation"
        f.elements.append(el)
    for (r, c), (mk, val, line) in marks.items():
        a, b = rows.get(r), cols.get(c)
        if a is None or b is None:
            continue
        if mk == "pos":
            f.claims.append(Claim(a, b, False, val, "cell", line))
        elif mk == "other":
            subj = set(a.ents) | set(b.ents)
            for num in _numbers_of(val, ck):
                f.number_uses.append((num, subj or None, f"table {index} line {line}"))
    return f


# =========================================================================== matching

def stated(ck: CKey, a: str, b: str) -> list:
    """Key relations that state the pair `a -> b` (undirected relations either way)."""
    out = []
    for r in ck.relations:
        if (a in r.src_set and b in r.dst_set) or (
                not r.directed and a in r.dst_set and b in r.src_set):
            out.append(r)
    return out


def _group_level(c: Claim, ck: CKey) -> list:
    """`[(relation, src_group_level, dst_group_level, reversed)]` for a claim with an aggregate
    end, where the key states the relation with that group as its endpoint. *reversed*: the
    claim runs against the relation, which an undirected relation or an undirected claim
    allows; the two flags then name the claim's ends, not the relation's."""
    sg, dg = c.src.group, c.dst.group
    if not sg and not dg:
        return []
    out = []
    for r in ck.relations:
        orients = [(r.src, r.dst, r.src_set, r.dst_set, False)]
        if not r.directed or not c.directed:
            orients.append((r.dst, r.src, r.dst_set, r.src_set, True))
        for (rs, rd, rss, rds, rev) in orients:
            s_grp = bool(sg) and rs == sg
            d_grp = bool(dg) and rd == dg
            s_ok = s_grp if sg else bool(set(c.src.ents) & rss)
            d_ok = d_grp if dg else bool(set(c.dst.ents) & rds)
            if s_ok and d_ok and (s_grp or d_grp):
                out.append((r, s_grp, d_grp, rev))
                break
    return out


def _covered_pairs(r: Rel, c: Claim, s_grp: bool, d_grp: bool, rev: bool) -> set:
    """The pairs of relation *r*, in the relation's own orientation, that the aggregate claim
    *c* draws (see `_group_level`)."""
    if rev:
        src_end, src_grp, dst_end, dst_grp = c.dst, d_grp, c.src, s_grp
    else:
        src_end, src_grp, dst_end, dst_grp = c.src, s_grp, c.dst, d_grp
    srcs = r.src_set if src_grp else set(src_end.ents) & r.src_set
    dsts = r.dst_set if dst_grp else set(dst_end.ents) & r.dst_set
    return {(a, b) for a in srcs for b in dsts if a != b}


def _seq_checks(f: Facts, ck: CKey):
    """Assign drawn messages to key messages (pair and keyword first, then pair alone); check
    stated order, control blocks, self-messages, and call versus reply."""
    key_msgs = [r for r in ck.relations if r.source == "messages"]
    msgs = f.messages

    def fits(c, km):
        return bool(set(c.src.ents) & km.src_set) and bool(set(c.dst.ents) & km.dst_set)

    assigned, used = {}, set()
    for labelled in (True, False):
        for km in key_msgs:
            if km.id in assigned:
                continue
            for k, c in enumerate(msgs):
                if k in used or not fits(c, km):
                    continue
                if labelled and not (km.label_aliases and any(
                        _contains(tokens(c.label), al) for al in km.label_aliases)):
                    continue
                assigned[km.id] = k
                used.add(k)
                break
    f.covered |= set(assigned)
    for kid, k in assigned.items():
        km = next(r for r in key_msgs if r.id == kid)
        if km.reply is not None and bool(km.reply) != bool(msgs[k].reply):
            f.diagnostics.append(f"{_where(f, msgs[k].line)}: drawn as "
                                 f"{'a reply' if msgs[k].reply else 'a call'}; the document "
                                 f"states {'a reply' if km.reply else 'a call'}")
    for c in msgs:
        if c.src.ents and c.src.ents == c.dst.ents:
            if not any(fits(c, km) and km.src_set == km.dst_set for km in key_msgs):
                f.unsupported.append(f"{_where(f, c.line)}: a self-message the document does "
                                     f"not state")
    pos = {kid: msgs[k].line for kid, k in assigned.items()}
    pairs = list(ck.message_order)
    ordered = sorted((r for r in key_msgs if r.order is not None), key=lambda r: r.order)
    pairs += [(x.id, y.id) for x, y in zip(ordered, ordered[1:]) if x.order != y.order]
    for a, b in dict.fromkeys(pairs):
        if a in pos and b in pos and pos[a] > pos[b]:
            f.unsupported.append(f"figure {f.index}: message {b} (line {pos[b]}) comes before "
                                 f"{a} (line {pos[a]}); the document states the opposite")
            _type_hit(f, ck, "order_violation", _where(f, pos[b]))
    for (kind, label, start, end) in f.blocks:
        if kind not in CONTROL_BLOCKS:
            continue
        inside = {kid for kid, k in assigned.items() if start <= msgs[k].line <= end}
        ok = any((kind in kb["kinds"] or (kind in ("alt", "opt") and kb["kinds"] & {"alt", "opt"}))
                 and (not kb["messages"] or kb["messages"] & inside) for kb in ck.blocks)
        if not ok:
            f.unsupported.append(f"{_where(f, start)}: a `{kind}` block the document does not "
                                 f"state around these messages")
        for d in ck.decoys:
            if d.get("type") != "invented_block":
                continue
            spec = d.get("block") if isinstance(d.get("block"), dict) else {}
            kinds = {str(x).casefold() for x in _as_list(spec.get("kind") or d.get("kind"))}
            encl = set(_as_list(spec.get("encloses_any")))
            if kinds and kind not in kinds:
                continue
            if encl and not (encl & inside):
                continue
            if not encl and ok:
                continue
            f.decoy_hits.setdefault(d["id"], _where(f, start))


def _state_checks(f: Facts, ck: CKey):
    """A transition label that names a writer must name that transition's stated writer, and
    an `invented_writer` decoy hits when its alias labels one of its transitions."""
    writer_aliases = [al for al in ck.aliases
                      if al.target == "entity" and al.tid in ck.writers and not al.soft]
    for c in f.claims:
        if c.kind != "transition" or not c.label:
            continue
        toks = tokens(c.label)
        rels = [r for a in sorted(c.src.ents) for b in sorted(c.dst.ents) if a != b
                for r in stated(ck, a, b) if r.kind == "transition" or r.source == "transitions"]
        rel_ids = {r.id for r in rels}
        for d in ck.decoys:
            if d.get("type") != "invented_writer":
                continue
            scope = d.get("transitions", "any")
            if scope != "any" and not (set(_as_list(scope)) & rel_ids):
                continue
            if any(_contains(toks, tk) for tk in d["_toks"]):
                f.decoy_hits.setdefault(d["id"], _where(f, c.line))
        named = {al.tid for al in writer_aliases if _contains(toks, al.toks)}
        if not named or not rels:
            continue
        writers = {r.writer for r in rels if r.writer}
        if not (named & writers):
            f.invented.append(f"{_where(f, c.line)}: names writer {sorted(named)}; the document "
                              f"names {sorted(writers) if writers else 'no writer, a condition'}")


def _branch_label(c: Claim, rels: list, ck: CKey, f: Facts):
    """A decision edge whose label names another branch of the same decision is swapped."""
    branch = [r for r in rels if r.kind == "branch" and r.label_aliases]
    if not branch or not c.label:
        return
    toks = tokens(c.label)
    if any(_contains(toks, al) for r in branch for al in r.label_aliases):
        return
    srcs = {r.src for r in branch}
    others = [r for r in ck.relations if r.kind == "branch" and r.src in srcs and r not in branch]
    if any(_contains(toks, al) for r in others for al in r.label_aliases):
        f.unsupported.append(f"{_where(f, c.line)}: branch label {c.label!r} belongs to "
                             f"another branch of this decision")


def _pseudo_claim(c: Claim, ck: CKey, f: Facts):
    if c.src.status == "pseudo" and c.dst.status == "pseudo":
        return
    initial = c.src.status == "pseudo"
    targets = set(c.dst.ents if initial else c.src.ents)
    ok_set = set()
    for x in (ck.initial if initial else ck.final):
        ok_set |= {x} if x in ck.entities else set(ck.groups.get(x, {}).get("members", ()))
    for r in ck.relations:
        if r.src == "[*]" if initial else r.dst == "[*]":
            side = r.dst_set if initial else r.src_set
            ok_set |= set(side)
            if targets & side:
                f.covered.add(r.id)
    if not ok_set:
        return
    for t in sorted(targets):
        if t not in ok_set:
            f.unsupported.append(f"{_where(f, c.line)}: {t} is not a stated "
                                 f"{'initial' if initial else 'final'} state")


def _box_entity(title_el, members, ck: CKey) -> Optional[str]:
    """The entity a box stands for: its title names one stated entity, not a group, and every
    member it draws is that entity or one of its stated parts (`part_of`). None otherwise. A
    container drawn as a box of its parts is the container, not an invented group (EI-08)."""
    if title_el is None or title_el.group or title_el.status not in ("mapped", "renamed") \
            or len(title_el.ents) != 1:
        return None
    owner = next(iter(title_el.ents))
    allowed = {owner} | {p for p, o in ck.part_of.items() if o == owner}
    return owner if set(members) <= allowed else None


def _fit_group(g: GroupBox, ck: CKey) -> tuple:
    """`(group_id, ok, renamed)`: the box maps to a stated group that holds every member it
    draws. A title that names no group still fits when the box holds exactly the members of a
    stated group; the box is then that group under another name (contract check K07). A box
    titled with a stated entity fits as that entity when it holds the entity or its stated
    parts only (`_box_entity`); the id returned is then the entity's. A stated part counts as
    its container toward a group, so a site box that holds `app-01` holds the application
    nodes (EI-08)."""
    tel = g.title_el
    members = frozenset(ck.part_of.get(m, m) for m in g.members)
    if tel is not None and tel.group and tel.status in ("mapped", "renamed"):
        return tel.group, members <= ck.groups[tel.group]["members"], tel.status == "renamed"
    owner = _box_entity(tel, g.members, ck)
    if owner is not None:
        return owner, True, tel.status == "renamed"
    for gid, gg in ck.groups.items():
        if members and members == gg["members"]:
            return gid, True, True
    return None, False, False


def _check_number(num: Number, subj, ck: CKey) -> Optional[str]:
    """None when *num* is stated for one of *subj* (None: any subject); else the reason."""
    if num.unit == "date":
        if any(num.value in _task_dates(t, "start") | _task_dates(t, "end")
               for t in ck.tasks.values()) or str(ck.calendar.get("start", "")) == num.value:
            return None
    same = [n for n in ck.numbers
            if numbers_equal(num.value, num.unit, n["value"], n["unit"], n["units"])]
    if not same:
        return "absent from the document"
    if subj is None:
        return None
    if any(n["subjects"] is None or n["subjects"] & set(subj) for n in same):
        return None
    return "stated for another subject"


def _claim_rels(ck: CKey, c: Claim, a: str, b: str) -> tuple:
    """`(a, b, relations)`: the key relations a claim states for the pair `a -> b`. A line or a
    table cell runs either way; a reply answers a stated call. A part with no relation of its
    own stands for its container (`part_of`, EI-08); the pair returned is then the containers'."""
    def lookup(x, y):
        rels = stated(ck, x, y)
        if not c.directed:
            seen = {r.id for r in rels}
            rels = rels + [r for r in stated(ck, y, x) if r.id not in seen]
        elif not rels and c.kind == "message" and c.reply:
            rels = stated(ck, y, x)
        return rels

    rels = lookup(a, b)
    if not rels and (a in ck.part_of or b in ck.part_of):
        a, b = ck.part_of.get(a, a), ck.part_of.get(b, b)
        rels = lookup(a, b) if a != b else []
    return a, b, rels


def _anchored_links(f: Facts, ck: CKey) -> set:
    """The drawn links of a figure that state at least one key relation. A link between nodes
    that each name several entities (`push to merge request -> lint`) claims a pair per name;
    when one pair is stated, the pairs that name a modifier are not relations (EI-01)."""
    out = set()
    for c in f.claims:
        if c.src.status == "pseudo" or c.dst.status == "pseudo" or _group_level(c, ck):
            continue
        key = (f.index, c.edge if c.edge >= 0 else id(c))
        if key in out:
            continue
        if any(a != b and _claim_rels(ck, c, a, b)[2]
               for a in c.src.ents for b in c.dst.ents):
            out.add(key)
    return out


def _stated_subjects(ck: CKey, value, unit) -> Optional[set]:
    """The subjects the document gives a number of this value: their union, or None when one
    statement of it names no subject (it holds for any)."""
    out = set()
    for n in ck.numbers:
        if numbers_equal(value, unit, n["value"], n["unit"], n["units"]):
            if n["subjects"] is None:
                return None
            out |= n["subjects"]
    return out


#: Node shapes of a check in a decision flow: a check about an entity is not that entity.
CHECK_SHAPES = ("rhombus", "hexagon")


def _duplicates(f: Facts) -> list:
    """Q12 findings for the nodes of one flowchart that draw an entity another node draws
    already, under a name the document does not give it: a first line that extends a stated
    name (`Picking DB replica` beside `Picking DB`, `API gateway WAF` before `API gateway`) or
    that holds only a soft alias (`Slotting DB` beside `Slotting service`) is an element the
    document does not state (EI-04). A node whose first line is a stated name is never one:
    the same outcome drawn twice, or parts the key names (`app-01`, `app-02`); nor is a check
    of a decision flow (`Agent approves?`). The best-named node stays."""
    by_ent = {}
    for el in f.elements:
        if el.kind != "node" or el.group or el.status not in ("mapped", "renamed") \
                or len(el.ents) != 1:
            continue
        by_ent.setdefault(next(iter(el.ents)), []).append(el)
    out = []
    for ent, els in sorted(by_ent.items()):
        if len(els) < 2:
            continue
        keep = max(els, key=lambda e: (e.quality, -e.line))
        out += [f"{_where(f, e.line)}: node {e.text!r} draws {ent} a second time, beside "
                f"{keep.text!r}" for e in els
                if e is not keep and e.quality < COVERS and e.shape not in CHECK_SHAPES]
    return out


def _reach(f: Facts) -> dict:
    """id(element) -> set of id(element) reachable along directed order claims of one figure."""
    succ = {}
    for c in f.claims:
        if c.directed and c.kind in ORDER_KINDS:
            succ.setdefault(id(c.src), []).append(c.dst)
    reach = {}
    for el in f.elements:
        seen, stack = set(), list(succ.get(id(el), ()))
        while stack:
            x = stack.pop()
            if id(x) in seen:
                continue
            seen.add(id(x))
            stack.extend(succ.get(id(x), ()))
        reach[id(el)] = seen
    return reach


def _path_exists(f: Facts, reach: dict, a_set, b_set) -> bool:
    """True when an element naming one of *a_set* reaches an element naming one of *b_set*."""
    srcs = [e for e in f.elements if set(e.ents) & a_set and not (set(e.ents) & b_set)]
    dsts = {id(e) for e in f.elements if set(e.ents) & b_set and not (set(e.ents) & a_set)}
    return any(reach.get(id(s), set()) & dsts for s in srcs)


def _order_checks(f: Facts, ck: CKey):
    """Stated order and stage layers as paths, and `order_violation` decoys as paths."""
    if not (ck.element_order or ck.layers or any(
            d.get("type") == "order_violation" for d in ck.decoys)):
        return
    reach = _reach(f)
    for (first, then) in ck.element_order:
        if _path_exists(f, reach, set(then), set(first)):
            f.unsupported.append(f"figure {f.index}: {sorted(then)} drawn before "
                                 f"{sorted(first)}; the document states the opposite order")
    for i, early in enumerate(ck.layers):
        for late in ck.layers[i + 1:]:
            if _path_exists(f, reach, set(late), set(early)):
                f.unsupported.append(f"figure {f.index}: stage {sorted(late)} drawn before "
                                     f"stage {sorted(early)}")
        members = sorted(early)
        for a in members:
            for b in members:
                if a != b and _path_exists(f, reach, {a}, {b}):
                    f.unsupported.append(f"figure {f.index}: {a} drawn before {b}; the "
                                         f"document runs them in parallel")
    for d in ck.decoys:
        if d.get("type") != "order_violation":
            continue
        for (a, b) in sorted(d.get("_pairs", ())):
            if _path_exists(f, reach, {a}, {b}):
                f.decoy_hits.setdefault(d["id"], f"figure {f.index}: {a} drawn before {b}")
                break


def _label_scan(f: Facts, ck: CKey):
    """Decoys whose aliases name a group title, or appear in edge, message or transition
    labels, notes and block labels."""
    titles = [(g.title, f"figure {f.index}: {g.kind} {g.title!r}") for g in f.groups]
    labels = [(c.label, _where(f, c.line)) for c in f.claims if c.label] + list(f.texts) \
        + [(lab, _where(f, s)) for (_k, lab, s, _e) in f.blocks if lab]
    for d in ck.decoys:
        t = d.get("type")
        if not d["_toks"] or d["id"] in f.decoy_hits:
            continue
        scope = titles if t == "invented_group" else labels if t in LABEL_DECOYS else []
        for (text, where) in scope:
            toks = tokens(text)
            if any(_contains(toks, tk) for tk in d["_toks"]):
                f.decoy_hits.setdefault(d["id"], where)
                break


def match(ck: CKey, facts: list, forms: Optional[set] = None) -> dict:
    """Match every figure of one answer against the key and return the fidelity record.

    *forms*: the forms the answer holds (`mermaid`, `text`, `table`, `list`, `image`), for
    `wrong_form` decoys.
    """
    res = {"normalize_version": NORMALIZE_VERSION, "figures": [], "mapped": {}, "renamed": [],
           "invented": [], "unsupported": [], "missing_required": [], "covered": [],
           "bad_numbers": [], "decoy_hits": [], "decoys": {}, "diagnostics": [],
           "dynamics_claims": [], "ordinal_edges": 0, "modelled": True}
    covered_rel, drawn_all = set(), set()
    covered_by = {}          # relation id -> pairs drawn, in the relation's own orientation

    def cover(rid, pairs):
        covered_by.setdefault(rid, set()).update(pairs)
    for f in facts:
        drawn, fig_numbers = set(), []
        if not f.modelled:
            res["modelled"] = False
            res["diagnostics"].append(f"figure {f.index}: kind {f.kind!r} is not modelled")
            res["figures"].append({"index": f.index, "form": f.form, "line": f.line,
                                   "modelled": False, "entities": [], "numbers": []})
            continue
        res["ordinal_edges"] += f.ordinal_edges
        if f.kind == "sequence":
            _seq_checks(f, ck)
        if f.kind == "state":
            _state_checks(f, ck)
        _order_checks(f, ck)
        _label_scan(f, ck)
        for el in f.elements:
            if el.status == "annotation":
                continue
            res["mapped"][f"{f.index}:{el.fid}"] = {"text": el.text, "entities": sorted(el.ents),
                                                    "group": el.group, "status": el.status}
            if el.status in ("mapped", "renamed"):
                drawn |= set(el.ents) | ({el.group} if el.group else set())
            if el.status == "renamed":
                res["renamed"].append(f"{_where(f, el.line)}: {el.text!r} -> {sorted(el.ents)}")
            if el.status == "invented":
                res["invented"].append(f"{_where(f, el.line)}: {el.kind} {el.text!r}")
            for did in el.decoys:
                f.decoy_hits.setdefault(did, f"{_where(f, el.line)}: {el.text!r}")
            subj = set(el.ents) | set(el.subjects_extra) | ({el.group} if el.group else set())
            for num in el.numbers:
                f.number_uses.append((num, subj, f"{_where(f, el.line)}: {el.text!r}"))
        if f.kind == "flowchart":
            res["invented"] += _duplicates(f)
        anchored, between = _anchored_links(f, ck), {}
        for g in f.groups:
            gid, ok, renamed = _fit_group(g, ck)
            if not ok:
                res["invented"].append(f"figure {f.index}: {g.kind} {g.title!r}")
            elif renamed:
                res["renamed"].append(f"figure {f.index}: {g.kind} {g.title!r} -> {gid}")
            if gid and ok:
                drawn.add(gid)
        for c in f.claims:
            if c.src.status == "pseudo" or c.dst.status == "pseudo":
                _pseudo_claim(c, ck, f)
                continue
            if c.to_subgraph:
                _type_hit(f, ck, "boundary_edge", _where(f, c.line))
            if c.src.status == "invented" or c.dst.status == "invented":
                # an edge to an element the document does not state is a relation it does not
                # state either (Q09's text), besides the invented element of Q12 (EI-30)
                res["unsupported"].append(f"{_where(f, c.line)}: {c.src.text!r} -> "
                                          f"{c.dst.text!r}: an end the document does not state")
            rel_ids = set()
            group_rels = _group_level(c, ck)
            if group_rels:
                for (r, s_grp, d_grp, rev) in group_rels:
                    rel_ids.add(r.id)
                    if s_grp and d_grp:
                        covered_rel.add(r.id)
                    cover(r.id, _covered_pairs(r, c, s_grp, d_grp, rev))
            else:
                for a0 in sorted(c.src.ents):
                    for b0 in sorted(c.dst.ents):
                        if a0 == b0:
                            continue
                        a, b, rels = _claim_rels(ck, c, a0, b0)
                        if a == b:
                            continue          # a link inside one container
                        if rels:
                            for r in rels:
                                if a in r.src_set and b in r.dst_set:
                                    cover(r.id, {(a, b)})
                                elif (not r.directed or not c.directed) \
                                        and b in r.src_set and a in r.dst_set:
                                    cover(r.id, {(b, a)})   # drawn against an undirected one
                            rel_ids |= {r.id for r in rels}
                            _branch_label(c, rels, ck, f)
                            if f.kind == "flowchart" and ck.required_concern == "structure" and \
                                    any(r.concern == "dynamics" for r in rels):
                                res["dynamics_claims"].append(f"{_where(f, c.line)}: {a}->{b}")
                        elif (f.index, c.edge if c.edge >= 0 else id(c)) not in anchored:
                            why = "reads backwards" if c.directed and stated(ck, b, a) \
                                else "not stated"
                            res["unsupported"].append(f"{_where(f, c.line)}: {a} -> {b} {why}")
                        for d in ck.decoys:
                            pairs = d.get("_pairs")
                            if d.get("type") not in RELATION_DECOYS or not pairs:
                                continue
                            if (a, b) not in pairs and not (not c.directed and (b, a) in pairs):
                                continue
                            if d.get("type") == "condition_as_entity":
                                # the condition placed between its stages: every pair of the
                                # decoy drawn; one pair alone is the condition beside a stage
                                drawn_pairs = between.setdefault(d["id"], set())
                                drawn_pairs.add((a, b) if (a, b) in pairs else (b, a))
                                if drawn_pairs >= pairs:
                                    f.decoy_hits.setdefault(d["id"], _where(f, c.line))
                                continue
                            if d["_toks"] and not any(
                                    _contains(tokens(c.label), tk) for tk in d["_toks"]):
                                continue
                            f.decoy_hits.setdefault(d["id"], _where(f, c.line))
            subj = set(c.src.ents) | set(c.dst.ents) | rel_ids
            for num in c.numbers:
                f.number_uses.append((num, subj, _where(f, c.line)))
        if f.kind == "flowchart" and ck.required_concern == "structure" and f.ordinal_edges:
            _type_hit(f, ck, "dynamics_in_structure", f"figure {f.index}: numbered edges")
        res["unsupported"] += f.unsupported
        res["invented"] += f.invented
        res["bad_numbers"] += f.bad_numbers
        res["diagnostics"] += f.diagnostics
        covered_rel |= f.covered
        for (num, subj, where) in f.number_uses:
            fig_numbers.append(num)
            bad = _check_number(num, subj, ck)
            if bad:
                res["bad_numbers"].append(f"{where}: {num.raw!r} {bad}")
            for d in ck.decoys:
                if d.get("type") != "number_from_other_rule" or "_value" not in d:
                    continue
                if not numbers_equal(num.value, num.unit, d["_value"], d["_unit"]):
                    continue
                wrong = d["_wrong"]
                said = _stated_subjects(ck, d["_value"], d["_unit"])
                # a subject the document gives this number keeps it off the decoy (EI-10)
                if (wrong is None and bad) or (wrong is not None and subj and set(subj) & wrong
                                               and said is not None and not said & set(subj)):
                    f.decoy_hits.setdefault(d["id"], where)
        for did, where in f.decoy_hits.items():
            res["decoys"].setdefault(did, where)
        drawn_all |= drawn
        shown = []
        dates = [(n.value, n.unit) for n in fig_numbers] + [(iso, "date")
                                                             for iso in sorted(f.shown_dates)]
        dates += [(float(k), BARE) for k in sorted(f.shown_steps)]   # step numbers it draws
        for value, unit in dates:
            shown.append([value, unit])
            if unit == "date":                 # the parts of a date carry no unit (R2)
                y, m, dd = str(value).split("-")
                shown += [[float(y), BARE], [float(m), BARE], [float(dd), BARE]]
        res["figures"].append({"index": f.index, "form": f.form, "line": f.line,
                               "modelled": True, "elements": len(f.elements),
                               "claims": len(f.claims), "entities": sorted(drawn),
                               "numbers": shown})
    has_sequence = any(fx.kind == "sequence" and fx.modelled for fx in facts)
    status = {}
    for r in ck.relations:
        if r.id in covered_rel:
            status[r.id] = True
            continue
        if (r.source == "messages" and has_sequence) or r.src == "[*]" or r.dst == "[*]":
            status[r.id] = False
            continue
        pairs = [(a, b) for a in r.src_set for b in r.dst_set if a != b]
        got = covered_by.get(r.id, set())
        status[r.id] = bool(pairs) and (any if r.expand == "any" else all)(
            p in got for p in pairs)
    for r in ck.relations:
        if r.required:
            (res["covered"] if status[r.id] else res["missing_required"]).append(r.id)
    for grp in ck.required_any:
        if not any(status.get(rid) for rid in grp):
            res["missing_required"].append("one of " + "|".join(grp))
    _eval_stress_decoys(ck, facts, res, forms or set())
    res["decoy_state"] = {}
    for d in ck.decoys:
        did = d["id"]
        if did in res["decoys"]:
            hit = True
        elif d.get("type") in UNSEEN_DECOYS or not facts:
            hit = None
        else:
            hit = False
        res["decoy_state"][did] = {"type": d.get("type"), "hit": hit,
                                   "where": res["decoys"].get(did)}
    res["decoy_hits"] = sorted(did for did, s in res["decoy_state"].items() if s["hit"])
    res["drawn_entities"] = sorted(drawn_all)
    res["verdicts"] = verdicts(res)
    return res


_V11_PATTERNS = (re.compile(r"@\{"), re.compile(r"^\s*(?:architecture-beta|block-beta)\b", re.M),
                 re.compile(r"\b\w+@-{2,3}>"))


def _eval_stress_decoys(ck: CKey, facts: list, res: dict, forms: set):
    """Stress decoys the source shows directly: the answer's form, a wide direction,
    version-only syntax, a long payload on one label, and a bipartite core drawn pair by pair."""
    for d in ck.decoys:
        t, did = d.get("type"), d["id"]
        if did in res["decoys"]:
            continue
        if t == "wrong_form":
            hit = sorted(set(_as_list(d.get("forms"))) & set(forms))
            if hit:
                res["decoys"][did] = f"the answer holds {', '.join(hit)}"
            continue
        for f in facts:
            if t == "lr_width" and f.kind == "flowchart" and f.direction.upper() in ("LR", "RL"):
                res["decoys"][did] = f"figure {f.index}: flowchart {f.direction}"
            elif t == "v11_only_syntax" and f.form.startswith("mermaid:"):
                pats = [re.compile(re.escape(p)) for p in _as_list(d.get("patterns"))] \
                    or list(_V11_PATTERNS)
                if any(p.search(f.source or "") for p in pats):
                    res["decoys"][did] = f"figure {f.index}: syntax above the 10.9 floor"
            elif t == "long_payload" and d["_toks"]:
                need = int(d.get("min", 3))
                for c in f.claims:
                    toks = tokens(c.label)
                    if sum(1 for tk in d["_toks"] if _contains(toks, tk)) >= need:
                        res["decoys"][did] = f"{_where(f, c.line)}: {need} or more payload fields"
                        break
            elif t == "k33_core" and d.get("_pairs"):
                drawn = {(a, b) for c in f.claims if c.src.group is None and c.dst.group is None
                         for a in c.src.ents for b in c.dst.ents}
                if d["_pairs"] <= drawn:
                    res["decoys"][did] = f"figure {f.index}: every pair drawn as its own edge"
            if did in res["decoys"]:
                break


def verdicts(res: dict) -> dict:
    """Q09-Q12 from a fidelity record: `{"Q09": {"passed", "evidence"}, ...}`."""
    hits = {}
    for did, st in res.get("decoy_state", {}).items():
        chk = DECOY_CHECK.get(st.get("type"))
        if st.get("hit") is True and chk:
            hits.setdefault(chk, []).append(f"decoy {did} ({st.get('type')})")

    def ev(items, extra):
        items = list(items) + extra
        text = "; ".join(str(i) for i in items[:6])
        return text + (f"; and {len(items) - 6} more" if len(items) > 6 else "")

    q09 = not res["unsupported"] and not hits.get("Q09")
    q10 = not res["missing_required"]
    q11 = not res["bad_numbers"] and not hits.get("Q11")
    q12 = not res["invented"] and not hits.get("Q12")
    return {
        "Q09": {"passed": q09, "evidence": "every drawn relation is stated" if q09
                else ev(res["unsupported"], hits.get("Q09", []))},
        "Q10": {"passed": q10, "evidence": "every required relation is drawn" if q10
                else "missing: " + ", ".join(res["missing_required"][:12])},
        "Q11": {"passed": q11, "evidence": "every number is stated for its subject" if q11
                else ev(res["bad_numbers"], hits.get("Q11", []))},
        "Q12": {"passed": q12, "evidence": "every element maps to the document" if q12
                else ev(res["invented"], hits.get("Q12", []))},
    }


# =========================================================================== captions

_LEAD_LABEL = re.compile(r"^\s*(?:\*\*(?P<b>[^*]{1,80})\*\*|__(?P<u>[^_]{1,80})__)")
#: A plain or emphasised label: a word, a number with dotted parts and an optional letter, an
#: optional stop, an optional closing emphasis: `Figure 6.1 —`, `Рис. 2.1.`, `*Figure 3:`,
#: `_Table 4._`, `Figure 6a.` (EI-05). A stop or an emphasis marks a label of the skill's form;
#: in `Figure 6.1 shows ...` the number opens the sentence.
_LEAD_WORD_NUM = re.compile(r"^\s*[*_]{0,2}[^\W\d_]{1,20}\.?\s*\d{1,3}(?:\.\d{1,3})*"
                            r"(?:[^\W\d_](?![^\W\d_]))?\s*(?P<stop>[.:—–-])?(?P<emph>[*_]{0,2})")
#: The end of a caption's sentence: a stop, closing marks, then white space (EI-06).
_SENTENCE_END = re.compile(r"(?<=[.!?…])[*_)\]»\"”’]*\s+")
#: A break inside a sentence: a comma, a semicolon, a colon, or a dash between spaces. A title
#: holds none; `Containers — who calls whom` is a title and its claim in one sentence (R1).
_CLAUSE_BREAK = re.compile(r"[,;:]|\s[—–-]\s")


def caption_body(text) -> str:
    """The caption without its leading label (`**Figure 3.**`, `Рис. 2 —`, `Figure 6.1`,
    `*Figure 3:`), found by position."""
    t = str(text or "").strip()
    m = _LEAD_LABEL.match(t) or _LEAD_WORD_NUM.match(t)
    return t[m.end():] if m else t


def _caption_parts(text) -> tuple:
    """`(titled, body)`: the caption without its label, and whether a title follows the label.
    A bold label is the skill's form, as is a plain or emphasised one closed by a stop, a colon
    or a dash. A bold run that holds a title after its number (`**Figure 3. Containers.**`,
    `**Permission matrix.**`) keeps that title in the body (R1)."""
    t = str(text or "").strip()
    m = _LEAD_LABEL.match(t)
    if m:
        inner = (m.group("b") or m.group("u") or "").strip()
        n = _LEAD_WORD_NUM.match(inner)
        title = inner[n.end():].strip() if n else inner
        return True, (title + " " + t[m.end():].strip()).strip()
    m = _LEAD_WORD_NUM.match(t)
    if m:
        return bool(m.group("stop") or m.group("emph")), t[m.end():]
    return False, t


def caption_sentence(text) -> str:
    """The text a caption claims: its title and its claim sentence, as the skill writes them, a
    label, a title, then one sentence (R1). After a label of that form, a first sentence with no
    clause break is the title, and the next sentence is the claim. Otherwise the first sentence
    holds the claim: `Containers — who calls whom.`, or a paragraph without a label. Later
    sentences, such as what the figure leaves out, claim nothing about what it shows. Found by
    position and punctuation, never by a word (ARCHITECTURE L1; EI-06). Residual: a claim
    sentence with no clause break after a label reads as the title, and the sentence after it
    reads as the claim, an omission too (AMENDMENTS.md, "Caption truth, Q13")."""
    titled, body = _caption_parts(text)
    m = _SENTENCE_END.search(body)
    if not m:
        return body
    if titled and not _CLAUSE_BREAK.search(body[:m.start()]):
        n = _SENTENCE_END.search(body, m.end())
        return body[:n.start()] if n else body
    return body[:m.start()]


#: The stops of a sentence, and the closing marks that may follow a bracketed group before them.
_STOPS = frozenset(".!?…")
_CLOSING_MARKS = frozenset("*_\"”’»")
_DIGIT = re.compile(r"\d")


def _drop_tail_refs(text) -> str:
    """*text* without the references in brackets that end its sentences. Such a reference is a
    group in round or square brackets that holds a digit (`(§2.3.1)`, `(FS-1, FS-2)`,
    `(см. §2.3.1)`), and only white space, closing marks, stops and further such groups follow
    it up to the end of its sentence. The white space before the group goes with it; the stop
    after it stays. A stop inside the group, as in `(see Fig. 3)`, ends no sentence. The text is
    read once from its end, so the time grows linearly with its length."""
    keep = []
    tail = True  # only marks, white space and dropped groups lie between here and a stop or the end
    i = len(text)
    while i > 0:
        ch = text[i - 1]
        if ch in _STOPS:
            tail = True
        elif tail and ch in ")]":
            k = i - 2
            while k >= 0 and text[k] not in "()[]":
                k -= 1
            if k >= 0 and text[k] in "([" and _DIGIT.search(text, k + 1, i - 1):
                i = k
                while i > 0 and text[i - 1].isspace():
                    i -= 1
                continue
            tail = False
        elif not (ch.isspace() or ch in _CLOSING_MARKS):
            tail = False
        keep.append(ch)
        i -= 1
    return "".join(reversed(keep))


def _bare_claim(text, sub) -> bool:
    """True when a sentence of *text* ends with the tokens *sub*: the claim stops there. A
    sentence that goes on after them qualifies the claim (`each transition labelled with its
    writer, or with its condition ...`). The references in brackets that end its sentences are
    dropped first (`_drop_tail_refs`), so an abbreviation inside one does not split a sentence.
    Sentences are then found by punctuation, as `caption_sentence` finds them (R1, EI-06)."""
    sub = list(sub)
    if not sub:
        return False
    text = _drop_tail_refs(text)
    start = 0
    for m in list(_SENTENCE_END.finditer(text)) + [None]:
        sentence = text[start:m.start() if m is not None else len(text)]
        if tokens(sentence)[-len(sub):] == sub:
            return True
        if m is not None:
            start = m.end()
    return False


def _shows(num: Number, value, unit) -> bool:
    """True when a number the figure shows, `(value, unit)`, backs the caption number *num*: the
    same value, and the units agree or one side writes none. A `BARE` number backs only a
    caption number written without a unit (R2)."""
    if not _values_equal(num.value, value):
        return False
    if unit == BARE:
        return not num.unit
    return not num.unit or not unit or canonical_unit(unit) == num.unit


def caption_claims(caption, ck: CKey, drawn, drawn_numbers) -> dict:
    """Q13's second half: the caption names no entity, group or number the figure lacks, and
    matches no caption decoy. *drawn*: entity and group ids the figure draws; *drawn_numbers*:
    `[(value, unit)]` the figure shows. An optional entity or the start of a procedure may be
    named without being drawn: it is the subject of the caption, not a claim of a node. Claims
    are read from the label, the title and the claim sentence (`caption_sentence`), wherever the
    caption sits. A decoy of type `caption_overclaim` matches a bare claim only: one of its
    aliases ends a sentence of that text (`_bare_claim`). For that test the claim sentence is
    found after the references in brackets that end sentences are dropped, so an abbreviation
    inside one does not cut the claim. Other caption decoys match anywhere."""
    body = caption_sentence(caption)
    bare_body = caption_sentence(_drop_tail_refs(caption))
    toks = tokens(body)
    drawn = set(drawn)
    problems, decoy_hits = [], []
    for (_, _, al) in find_aliases(toks, ck.aliases):
        if al.target == "entity" and al.tid not in drawn:
            e = ck.entities[al.tid]
            if e.get("optional") or e.get("kind") == "start":
                continue
            problems.append(f"names {' '.join(al.toks)!r}, which the figure does not draw")
        elif al.target == "group" and al.tid not in drawn and not (
                set(ck.groups[al.tid]["members"]) & drawn):
            problems.append(f"names group {' '.join(al.toks)!r}, which the figure does not draw")
    for num in _numbers_of(body, ck):
        if not any(_shows(num, v, u) for (v, u) in drawn_numbers):
            problems.append(f"states {num.raw!r}, which the figure does not show")
    for cd in ck.caption_decoys:
        if cd.get("bare"):
            hit = any(_bare_claim(bare_body, tk) for tk in cd["toks"])
        else:
            hit = any(_contains(toks, tk) for tk in cd["toks"])
        if hit:
            decoy_hits += [cd["id"]] + list(cd.get("decoys", []))
            problems.append(f"matches caption decoy {cd['id']}")
    return {"ok": not problems, "problems": problems, "decoy_hits": sorted(set(decoy_hits))}


# =========================================================================== dispatch

def facts_for_figure(fig, ck: CKey, index: int) -> Facts:
    """Reduce one parsed fence (a `mermaid_model.Figure`) to Facts. A fence that is not a
    Mermaid fence is read as ASCII."""
    kind = getattr(fig, "kind", "unknown")
    fence = getattr(fig, "fence", None)
    if getattr(fence, "lang", "mermaid") != "mermaid" or kind == "ascii":
        return facts_from_ascii(getattr(fence, "body", ""), ck, index,
                                line_offset=getattr(fence, "start", 0))
    if kind == "flowchart" and getattr(fig, "flowchart", None) is not None:
        return facts_from_flowchart(fig, ck, index)
    if kind == "sequence" and getattr(fig, "sequence", None) is not None:
        return facts_from_sequence(fig, ck, index)
    if kind == "state" and getattr(fig, "state", None) is not None:
        return facts_from_state(fig, ck, index)
    if kind == "gantt" and getattr(fig, "gantt", None) is not None:
        return facts_from_gantt(fig, ck, index)
    return Facts(form=f"mermaid:{kind}", index=index, kind=kind, modelled=False,
                 source=getattr(fence, "body", ""), line=getattr(fence, "start", 0))
