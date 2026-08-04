#!/usr/bin/env python3
"""Register scanner for authored artifacts (TASK 096).

Advisory by construction: findings never change the exit code.
  0  scan completed (any number of findings)
  2  BROKEN INSTRUMENT — unreadable rule file, invalid rules, conflicting or
     inconsistent thresholds, unreadable input, or a dead detector
  3  usage error (an unknown flag, mutually exclusive modes)

Exit 3 exists so that a typo in a flag is not indistinguishable from a dead
detector: `argparse` exits 2 by default, and 2 is this tool's "the instrument is
broken" code. A CI wrapper must be able to tell the two apart.

The dead-detector exit is the point of the tool. A silent zero and a broken
instrument look identical, so every run probe-tests each detector against a
known-positive fixture and reports the result next to the findings. A rule that
cannot match its own `probe` string, or whose probe would be masked away before
matching, is rejected at load time.

Six register rules are covered (`documentation-standards` §5.5). Rules 1, 2 and
5 are decided by the scanner alone. Rules 3, 4 and 6 have detectors with
DECLARED RECALL LIMITS: they surface the constructions that are recognisable
from the text, and the reading pass still owns everything they cannot see.
SKILL.md §5 states what each one does not reach. Cell shape is
`documentation-standards` §5.1 and is reported under that section, not under a
§5.5 rule number.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCHEMA = "register-rules/v1"
FLAG_MAP = {"i": re.IGNORECASE}
SEVERITIES = ("warn", "info")
ENTRY_KEYS = ("marker", "pattern", "guidance", "probe", "flags", "severity",
              "rule", "note")
THRESHOLD_KEYS = ("sentence_max_words", "sentence_near_words",
                  "sentence_pressure_band", "cell_max_chars",
                  "cell_max_sentences", "cell_prose_chars")
DEFAULTS = {"sentence_max_words": 35, "sentence_near_words": 30,
            "sentence_pressure_band": 2, "cell_max_chars": 120,
            "cell_max_sentences": 1, "cell_prose_chars": 40}
CYR = re.compile(r"[а-яА-ЯёЁ]")

#: §5.5 rules that a lexicon entry may declare, and the finding kind each
#: produces. Rule 3 is DELIBERATELY absent: its detector is structural (a
#: vocabulary of modals and causals), so an entry declaring `"rule": 3` would
#: emit `reasoning` findings that `verify_detectors` never probes. Validation
#: rejects it and says so.
RULE_KIND = {2: "marker", 4: "maxim", 6: "metaphor"}
LEXICAL_RULES = tuple(sorted(RULE_KIND))
#: Rule 3's vocabularies plus the known-positive its detector must fire on.
#: `probes` maps a pattern to a string that matches it. Every pattern declares
#: one (TASK 099 D7): while it was optional, a pattern without an example was
#: reported `unprobed` and its row still printed live, which is exactly the
#: path that re-opens the TASK 097 D3 defect.
REASONING_KEYS = ("modals", "causals", "probe", "probes")
REASONING_VOCAB = ("modals", "causals")

#: The structural detector classes, in the order `_structural_probes` builds
#: their fixtures. THE TWO ARE COUPLED: a fixture added there without its name
#: here leaves the roster short, and a name here with no fixture there reports
#: DEAD on every run.
STRUCTURAL_KINDS = ("sentence_length", "sentence_near_limit", "cell_width",
                    "cell_sentences", "emoji_severity")
#: The roster `--probe` must account for, as a LITERAL rather than a count
#: derived from the file under test. Deriving it let the denominator shrink
#: with the numerator: deleting every rule-6 entry of one language printed
#: `17/17 detectors live` exit 0, and loading only `register-en.json` printed
#: `9/9` exit 0, with the missing class emitting no row at all (REG-4). A class
#: with no detector now appends a DEAD row.
PROBE_ROSTER = (STRUCTURAL_KINDS
                + tuple(RULE_KIND[r] for r in LEXICAL_RULES)
                + ("reasoning",))     # 9 rows per fully-configured language
#: The languages this skill ships, so that a wholly absent rule file still
#: contributes its nine rows instead of halving the roster: deleting
#: `register-ru.json` printed `9/9 detectors live` exit 0, and now prints
#: `14/18` exit 2 — the four lexical and reasoning classes DEAD, the five
#: structural ones live, since those are built from thresholds and are
#: language-independent. 9 x 2 is the 18 SKILL.md §5 promises. Applied only
#: when no `--rules` argument was given (TASK 099 D6): a caller supplying its
#: own rule file is entitled to a partial one, and the acceptance battery
#: builds single-language partials by design.
SHIPPED_LANGS = ("en", "ru")

#: Findings name the section of `documentation-standards` they violate. Cell
#: shape is §5.1 and is NOT a §5.5 rule; reporting it as "rule 1" claimed an
#: ownership this skill explicitly disclaims.
SEC_5_1 = 0


def standard_of(rule):
    return ("documentation-standards §5.1" if rule == SEC_5_1
            else f"documentation-standards §5.5 rule {rule}")


def label_of(rule):
    return "§5.1" if rule == SEC_5_1 else f"§5.5 r{rule}"


# --------------------------------------------------------------- validate ----
class DuplicateKey(ValueError):
    """A rule file declaring the same key twice is ambiguous, not last-wins."""


def _no_duplicates(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise DuplicateKey(f"duplicate key {k!r} in the same object")
        seen[k] = v
    return seen


#: A pattern is run against every line of arbitrary documents. Data files are
#: the declared extension point (R7), so a contributed entry must not be able to
#: hang the scan. Two checks, in this order, because the second cannot stand
#: alone: TIMING A REGEX REQUIRES IT TO FINISH, and the patterns worth rejecting
#: are exactly the ones that do not. The first draft of this guard hung the
#: validator on `\b(\w+\s?)+ing\b` — the very pattern it was written to reject.
#:
#: 1. Static: a group carrying an unbounded quantifier, itself repeated. That is
#:    the shape of catastrophic backtracking and it is decidable by reading.
#: 2. Dynamic, under SIGALRM where the platform has it: a wall-clock budget
#:    against adversarial strings, which catches shapes the static rule misses.
BUDGET_SECONDS = 0.15
BUDGET_STRINGS = (
    "a" * 256,
    "а" * 256,
    ("word " * 64).strip(),
    ("слово " * 64).strip(),
    "не " + ("просто слово " * 24),
)
#: A parenthesised group whose body contains `+`, `*` or `{n,}`, and which is
#: itself followed by `+`, `*` or `{n,}`.
NESTED_QUANT = re.compile(
    r"\((?![?]:?[=!<])[^()]*(?:[+*]|\{\d+,\})[^()]*\)\s*(?:[+*]|\{\d+,\})")
#: Ordinary prose carrying no obligation and no justification. A rule-3
#: vocabulary item that matches either of these is too loose to mean anything.
NEUTRAL_CONTROLS = (
    "The quick brown fox jumps over the lazy dog.",
    "Быстрая бурая лиса прыгает через ленивого пса.",
)


def _budget_check(rx, where, marker):
    """→ [errors]. A pattern that cannot finish on a hostile line is rejected."""
    if NESTED_QUANT.search(rx.pattern):
        return [f"{where}: pattern for {marker!r} nests an unbounded "
                f"quantifier inside a repeated group — that is the shape of "
                f"catastrophic backtracking, and it would hang a scan on a "
                f"line that nearly matches"]
    try:
        import signal
        has_alarm = hasattr(signal, "setitimer")
    except ImportError:                                    # pragma: no cover
        has_alarm = False
    if not has_alarm:                                      # pragma: no cover
        return []

    class _Timeout(Exception):
        pass

    def _raise(signum, frame):
        raise _Timeout()

    prev = signal.signal(signal.SIGALRM, _raise)
    try:
        for s in BUDGET_STRINGS:
            signal.setitimer(signal.ITIMER_REAL, BUDGET_SECONDS * 4)
            start = time.perf_counter()
            try:
                rx.search(s)
            except _Timeout:
                return [f"{where}: pattern for {marker!r} did not finish "
                        f"within {BUDGET_SECONDS * 4}s on a {len(s)}-char "
                        f"adversarial line — it would hang a scan"]
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
            spent = time.perf_counter() - start
            if spent > BUDGET_SECONDS:
                return [f"{where}: pattern for {marker!r} took {spent:.2f}s on "
                        f"a {len(s)}-char adversarial line (budget "
                        f"{BUDGET_SECONDS}s) — it backtracks and would slow "
                        f"every scan"]
    finally:
        signal.signal(signal.SIGALRM, prev)
    return []


def validate_rules(doc):
    """Structural check of a register-rules/v1 document → list of errors."""
    errors = []
    if not isinstance(doc, dict):
        return ["rule file root must be an object"]
    if doc.get("schema") != SCHEMA:
        errors.append(f'schema must be "{SCHEMA}"')

    th = doc.get("thresholds", {})
    if not isinstance(th, dict):
        errors.append("thresholds must be an object")
    else:
        for k, v in th.items():
            if k not in THRESHOLD_KEYS:
                errors.append(f"thresholds.{k}: unknown key — allowed "
                              f"{list(THRESHOLD_KEYS)}")
            elif not isinstance(v, int) or isinstance(v, bool) or v <= 0:
                errors.append(f"thresholds.{k} must be a positive integer")

    langs = doc.get("languages")
    if not isinstance(langs, dict) or not langs:
        return errors + ["languages must be a non-empty object"]

    for lang, spec in langs.items():
        if not isinstance(spec, dict):
            errors.append(f"languages.{lang} must be an object")
            continue
        errors += _validate_reasoning(lang, spec.get("reasoning"))
        cats = spec.get("categories")
        if not isinstance(cats, list) or not cats:
            errors.append(f"languages.{lang}.categories must be a non-empty list")
            continue
        for ci, cat in enumerate(cats):
            where = f"languages.{lang}.categories[{ci}]"
            if not isinstance(cat, dict) or not cat.get("name"):
                errors.append(f"{where}: category needs a name")
                continue
            entries = cat.get("entries")
            if not isinstance(entries, list) or not entries:
                errors.append(f"{where}: entries must be a non-empty list")
                continue
            for ei, e in enumerate(entries):
                errors += _validate_entry(f"{where}.entries[{ei}]", e)
    return errors


def check_thresholds(th, where="thresholds"):
    """Cross-key invariants, checked on the MERGED configuration.

    Checking these per file let the invariant be evaded by splitting the two
    keys across two rule files: each file validated, no key collided, and the
    merged result was exactly the configuration a single file is rejected for.
    """
    errors = []
    near, hard = th.get("sentence_near_words"), th.get("sentence_max_words")
    if isinstance(near, int) and isinstance(hard, int) and near >= hard:
        errors.append(f"{where}.sentence_near_words ({near}) must be below "
                      f"sentence_max_words ({hard}) — an info band at or above "
                      f"the limit reports nothing new")
    band = th.get("sentence_pressure_band")
    if isinstance(band, int) and isinstance(hard, int) and band >= hard:
        errors.append(f"{where}.sentence_pressure_band ({band}) must be below "
                      f"sentence_max_words ({hard})")
    prose, width = th.get("cell_prose_chars"), th.get("cell_max_chars")
    if isinstance(prose, int) and isinstance(width, int) and prose > width:
        errors.append(f"{where}.cell_prose_chars ({prose}) must not exceed "
                      f"cell_max_chars ({width}) — above the width limit every "
                      f"such cell is already reported")
    return errors


def _validate_reasoning(lang, block):
    """Rule 3's per-language vocabularies. Absent means the detector is off."""
    if block is None:
        return []
    where = f"languages.{lang}.reasoning"
    if not isinstance(block, dict):
        return [f"{where} must be an object"]
    errors = []
    unknown = [k for k in block if k not in REASONING_KEYS]
    if unknown:
        errors.append(f"{where}: unknown keys {unknown} — allowed "
                      f"{list(REASONING_KEYS)}")
    for key in REASONING_VOCAB:
        vals = block.get(key)
        if not isinstance(vals, list) or not vals or \
                any(not isinstance(v, str) or not v for v in vals):
            errors.append(f"{where}.{key} must be a non-empty list of strings")
            continue
        for v in vals:
            try:
                rx = re.compile(v)
            except re.error as exc:
                errors.append(f"{where}.{key}: {v!r} does not compile ({exc})")
                continue
            # A vocabulary item that fires on ordinary prose makes rule 3
            # report every sentence carrying its counterpart, which reads as a
            # working detector. `\b` and `x*` are the cheap ways in: neither
            # matches the empty string, so an emptiness test misses both.
            loose = [c for c in NEUTRAL_CONTROLS if rx.search(c)]
            if rx.match("") or loose:
                errors.append(f"{where}.{key}: {v!r} matches text carrying "
                              f"neither an obligation nor a justification "
                              f"({(loose or [''])[0][:40]!r}) — it would fire "
                              f"on every sentence")
            errors += _budget_check(rx, f"{where}.{key}", v)
    probe = block.get("probe")
    if not isinstance(probe, str) or not probe:
        errors.append(f"{where}.probe is required (a sentence carrying an "
                      f"obligation and its justification)")
    elif not errors:
        if mask(probe) != probe:
            errors.append(f"{where}.probe {probe!r} contains a masked construct "
                          f"— production scans masked text, so the probe would "
                          f"verify a path the detector never takes")
        elif not _scan_reasoning(mask(probe + "\n"), block, "<probe>"):
            errors.append(f"{where}.probe {probe!r} does not trigger the rule-3 "
                          f"detector — the vocabulary is dead on arrival")
    if not errors:
        vocabulary = set(block.get("modals") or []) | set(block.get("causals")
                                                          or [])
        for pat in (block.get("probes") or {}):
            if pat not in vocabulary:
                # Editing a pattern ORPHANS its example rather than breaking
                # it, because `probes` is keyed by the pattern. The orphan is
                # therefore the detectable signature of the edit, and it is
                # what makes this check falsifiable (TASK 097 D3).
                errors.append(
                    f"{where}.probes: {pat!r} is an example for a pattern that "
                    f"is not in the vocabulary — the pattern was edited or "
                    f"removed and its example was left behind")
        for key in ("modals", "causals"):
            for pat in block.get(key, []):
                declared = (block.get("probes") or {}).get(pat)
                if declared is None:
                    # An example is MANDATORY (TASK 099 D7). While it was
                    # optional, a pattern without one was reported `unprobed`
                    # and the row still printed live, which is the state that
                    # re-opens the TASK 097 D3 defect: drop the example for
                    # `\bshall\b`, replace the pattern with `\bZZZNEVER\b`, and
                    # the file loads clean at 18/18 exit 0 while `The installer
                    # shall abort because the target exists.` reports nothing.
                    errors.append(
                        f"{where}.{key}: {pat!r} declares no example in "
                        f"{where}.probes — an unexercised pattern can be "
                        f"edited away without any probe noticing")
                elif not re.search(pat, declared, re.I):
                    # The pattern was edited and its example was not. That is
                    # the signature of a vocabulary changed away from what it
                    # was for, and it is the mutation the probe exists to
                    # catch (TASK 097 R19).
                    errors.append(
                        f"{where}.{key}: {pat!r} no longer matches its own "
                        f"example {declared!r} in {where}.probes — the pattern "
                        f"was edited away from what it is for")
    return errors


def _reasoning_literal(block, pattern):
    """→ the DECLARED example for `pattern`, or None if it no longer matches.

    Deriving the example from the pattern was tried and rejected: it makes the
    probe tautological. `\\bshall\\b` reduces to `shall`, which matches by
    construction, so replacing the pattern with `\\bZZZNEVER\\b` reduces to
    `ZZZNEVER` and probes live just as happily — the exact mutation the probe
    exists to catch. A declared example is an independent statement of what the
    pattern is FOR, so changing the pattern and not the example is detected.
    """
    declared = (block.get("probes") or {}).get(pattern)
    if isinstance(declared, str) and re.search(pattern, declared, re.I):
        return declared
    return None


def _validate_entry(ew, e):
    """One lexicon entry. `probe` is required and must match `pattern`.

    The probe is not decoration. A pattern that cannot match its own example is
    the exact failure this scanner exists to make impossible: it reports zero
    and reads as a clean document.
    """
    if not isinstance(e, dict):
        return [f"{ew}: entry must be an object"]
    errors = []
    unknown = [k for k in e if k not in ENTRY_KEYS]
    if unknown:
        errors.append(f"{ew}: unknown keys {unknown} — allowed "
                      f"{list(ENTRY_KEYS)}")
    for req in ("marker", "pattern", "guidance", "probe"):
        if not isinstance(e.get(req), str) or not e.get(req):
            errors.append(f"{ew}: {req} is required (non-empty string)")

    flags = e.get("flags", "")
    if not isinstance(flags, str) or any(f_ not in FLAG_MAP for f_ in flags):
        errors.append(f"{ew}: flags must be a string over {sorted(FLAG_MAP)}")
        flags = ""
    if e.get("severity", "warn") not in SEVERITIES:
        errors.append(f"{ew}: severity must be one of {list(SEVERITIES)}")
    rule = e.get("rule", 2)
    if rule == 3:
        errors.append(f"{ew}: rule 3 is structural, not lexical — configure "
                      f"`languages.<lang>.reasoning`. A rule-3 entry emits "
                      f"findings that the detector probe never exercises")
    elif rule not in LEXICAL_RULES:
        errors.append(f"{ew}: rule must be one of {list(LEXICAL_RULES)} "
                      f"(documentation-standards §5.5)")
    if not isinstance(e.get("note", ""), str):
        errors.append(f"{ew}: note must be a string")

    if isinstance(e.get("pattern"), str):
        fl = 0
        for f_ in flags:
            fl |= FLAG_MAP[f_]
        try:
            rx = re.compile(e["pattern"], fl)
        except re.error as exc:
            errors.append(f"{ew}: pattern does not compile ({exc})")
            return errors
        errors += _budget_check(rx, ew, e.get("marker", "?"))
        probe = e.get("probe")
        if isinstance(probe, str) and probe:
            m = rx.search(probe)
            if not m:
                errors.append(f"{ew}: pattern does not match its own probe "
                              f"{probe!r} — the rule is dead on arrival")
            elif not m.group(0):
                # A zero-width match is truthy here but falsy at probe time,
                # so the entry would load clean and then be reported DEAD.
                errors.append(f"{ew}: pattern matches its probe with a "
                              f"zero-width match — a finding needs a surface "
                              f"string to report")
            if mask(probe) != probe:
                errors.append(f"{ew}: probe {probe!r} contains a masked "
                              f"construct (code span, link target, comment) — "
                              f"it would be blanked before matching and verify "
                              f"nothing")
    return errors


def load_rules(paths):
    """→ (lexicon, reasoning, thresholds, errors).

    Conflicting thresholds across files are an ERROR, not a last-file-wins
    race: which file happens to load last must never change a verdict.
    """
    lex, reasoning, errors = {}, {}, []
    thresholds = dict(DEFAULTS)
    declared = {}
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                doc = json.load(f, object_pairs_hook=_no_duplicates)
        except (OSError, ValueError) as exc:
            errors.append(f"{path}: unreadable ({type(exc).__name__}: {exc})")
            continue
        errs = validate_rules(doc)
        if errs:
            errors.extend(f"{path}: {e}" for e in errs)
            continue
        for k, v in doc.get("thresholds", {}).items():
            if k in declared and declared[k][0] != v:
                errors.append(
                    f"thresholds.{k} conflicts: {declared[k][1]} says "
                    f"{declared[k][0]}, {path} says {v}")
            else:
                declared[k] = (v, path)
                thresholds[k] = v
        for lang, spec in doc["languages"].items():
            if spec.get("reasoning"):
                slot = reasoning.setdefault(lang, {k: [] for k in REASONING_VOCAB})
                for key in REASONING_VOCAB:
                    slot[key] += spec["reasoning"][key]
                # The probe of the first file to declare one; a second file
                # adding vocabulary does not invalidate the first probe.
                slot.setdefault("probe", spec["reasoning"]["probe"])
                # Per-pattern probes travel WITH their patterns. Merging the
                # vocabulary without them would leave the merged block unable
                # to exercise a pattern its own source file could.
                if spec["reasoning"].get("probes"):
                    slot.setdefault("probes", {}).update(
                        spec["reasoning"]["probes"])
            for cat in spec["categories"]:
                for e in cat["entries"]:
                    fl = 0
                    for f_ in e.get("flags", ""):
                        fl |= FLAG_MAP[f_]
                    lex.setdefault(lang, []).append({
                        "rx": re.compile(e["pattern"], fl),
                        "marker": e["marker"],
                        "guidance": e["guidance"],
                        "probe": e["probe"],
                        # Carried so `verify_detectors` can check that a
                        # DECLARED flag is APPLIED. The declaration is read from
                        # the data and the application from this compile, which
                        # is a different site from the validator's own compile
                        # above; a divergence between the two is invisible to
                        # every other check.
                        "flags": e.get("flags", ""),
                        "severity": e.get("severity", "warn"),
                        "rule": e.get("rule", 2),
                        "note": e.get("note", ""),
                        "category": cat["name"],
                    })
    # The invariants run on the MERGED thresholds, never per file (see
    # check_thresholds): splitting two keys across two files evaded them.
    errors += check_thresholds(thresholds, "merged thresholds")
    return lex, reasoning, thresholds, errors


# ------------------------------------------------------------------ detect ----
#: YAML frontmatter. Three guards, each closing a way the block ran away:
#:   - the lookahead stops a document that OPENS WITH A HORIZONTAL RULE from
#:     having its title and first block masked away (real frontmatter never
#:     begins with a blank line, a rule always is followed by one);
#:   - the body is bounded to 40 lines, so a stray `---` far down the document
#:     cannot close a block that was never frontmatter;
#:   - every body line must look like YAML (a key, a list item, an indented
#:     continuation, or blank). Prose between two `---` lines is a thematic
#:     break around a paragraph, not metadata, and stays scanned.
FRONTMATTER_CANDIDATE = re.compile(r"\A---\n(?![ \t]*\n)((?:[^\n]*\n){0,40}?)---\n")
YAMLISH = re.compile(r"^(?:\s*$|\s*#|\s*-\s|\s+\S|[A-Za-z_][\w.-]*\s*:)")
FENCE = re.compile(r"^([ \t]*)(`{3,}|~{3,})[^\n]*\n(?:.*?\n)??"
                   r"(?:\1?\2`*~*[ \t]*(?:\n|\Z)|\Z)", re.S | re.M)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
LINK_TARGET = re.compile(r"\]\([^)\n]*\)")
#: CommonMark code spans: a run of N backticks closes on the next run of
#: exactly N. The previous single-backtick pattern leaked the body of a
#: ``double-backtick`` span and never masked a span crossing a line break.
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
QUOTE_PREFIX = re.compile(r"^\s*>+ ?")
SKIP_LINE = re.compile(r"^\s*(#{1,6}\s|```|~~~|-{3,}\s*$)")
LIST_MARK = re.compile(r"^\s*([-*+]\s+(\[[ xX]\]\s*)?|\d+\.\s+)")
#: A table delimiter row, with or without leading/trailing pipes: GFM permits
#: `a | b` tables, and requiring the pipe scanned their rows as prose.
DELIM_ROW = re.compile(r"^\s*:?-{1,}:?(\s*\|\s*:?-{1,}:?)+\s*$|"
                       r"^\s*\|[\s:|-]+\|\s*$")
#: Table-cell separator: a pipe that is not backslash-escaped.
CELL_SPLIT = re.compile(r"(?<!\\)\|")
UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")
#: Sentence boundary: terminator, optional closing punctuation, whitespace,
#: capital. Closing quotes and brackets were missing, so `«нет.» Далее` and
#: `…the thing.) Next` glued into one pseudo-sentence and inflated its length.
#:
#: The abbreviation set is measured, not guessed. Corpus occurrences that
#: actually reach the rule (abbreviation + whitespace + capital): `e.g.` 12,
#: `vs.` 4, `см.` 1 — every one inspected and mid-sentence. `i.e.` is carried on
#: 14 occurrences with 0 hits: identical construct, and its zero is a sampling
#: accident rather than evidence.
#:
#: NOT adopted, and the reasons differ:
#:   - `cf.`, `др.`, `т.е.` — zero occurrences. A rule with no instance is a
#:     guess.
#:   - `etc.` (35) and `т.д.`/`т.п.` (1 each) — zero hits here, and in general
#:     prose they genuinely DO end sentences. Exempting them would trade this
#:     false split for a false *glue*, which is the worse defect: it inflates
#:     sentence length and fabricates findings.
#:   - Decimals need no exemption at all. `1.5 Beta` has no whitespace after
#:     the period, so the rule never fired there. The claim was refuted by
#:     execution, not accepted from the report.
SENT_SPLIT = re.compile(
    r"(?<!e\.g\.)(?<!i\.e\.)(?<!vs\.)(?<!см\.)"
    r"(?<=[.!?])[»\"'\)\]]*\s+(?=[A-ZА-ЯЁ«\"'\(\[])", re.IGNORECASE)
EMPHASIS = re.compile(r"\*\*|__|(?<!\w)\*(?!\s)|(?<!\s)\*(?!\w)")

#: Pictographic ranges. The previous class was declared "complete for
#: pictographic glyphs" while omitting Miscellaneous Symbols and Dingbats
#: entirely: ⛔, ⚡, ☠, ❕, ‼ and ✔ all scored zero against a rule whose §5
#: recall limit read "nothing".
#:
#: Arrows (U+2190–U+21FF) are deliberately NOT included: `→` is notation in
#: this repository's own documents, not a severity.
_PICTO = "[\U0001F000-\U0001FAFF☀-➿⬀-⯿‼⁉]"
#: One glyph per finding, not one codepoint: a skin-tone or ZWJ sequence is a
#: single authored character and was being counted two or three times.
EMOJI = re.compile(
    _PICTO + r"(?:[︎️\U0001F3FB-\U0001F3FF]|‍" + _PICTO + r")*")
#: Status values, not severities. Two exemptions with different scopes, each
#: measured over the 627 tracked `.md` documents of this repository.
#:
#: `✓`/`✗` are exempt in EVERY position (TASK 099 D2). The narrowing this
#: replaces was justified on two premises and both fail against the corpus it
#: cited: it claimed every inspected occurrence was a table cell, while 704 of
#: the 1,042 status glyphs (68%) sit outside a table, and it existed to catch a
#: status glyph used AS A SEVERITY in prose, a class with no members. Of the
#: ticks, 33 of 52 are out of a table — `docs/TASK.md gone ✓` in a numbered
#: list — and exempting them turns no acceptance case red.
#:
#: `✅`/`❌`/`☑`/`☒`/`☐` stay exempt only INSIDE A TABLE CELL, where §5.1
#: governs. Exempting them everywhere would erase the 671 out-of-table findings
#: that `references/formalization-guide.md:19-21` defends (a glyph carrying no
#: severity is diff metadata and does not belong in a specification either),
#: and would turn TC-ADV-13 red. `☐` joins them because all 6 of its
#: occurrences are table cells; `✔` (U+2714) deliberately stays out, and
#: TC-ADV-10 requires it to fire.
TICK_GLYPHS = frozenset("✓✗")
STATUS_GLYPHS = frozenset("✓✗✅❌☑☒☐")
#: Rule 5's guidance branches on the glyph. One string told the author of
#: `docs/TASK.md gone ✓` to replace it with `SEV-2`, which is not advice about
#: a done/not-done value (REG-10).
SEVERITY_GUIDANCE = ("Rule 5: severity is a named value. Replace with a word "
                     "(`warn`, `SEV-2`, `Critical`), or delete the glyph if it "
                     "carries no severity at all.")
STATUS_GUIDANCE = ("Rule 5: a status glyph is not a specification value. "
                   "Replace with the status word (`done`, `pass`, `n/a`), or "
                   "delete it where the sentence already says so.")


def normalize(text):
    """NFC, so that a decomposed `ё` is the same character as a composed one.

    A Russian document authored with NFD input scored zero on every entry whose
    pattern spells `ё`, and `\\w`/`\\b` break around a combining diaeresis.
    """
    return unicodedata.normalize("NFC", text)


#: A code span may cross a line ending but never a blank line: the blank line
#: ends the paragraph, and CommonMark closes the span there. The bound is also
#: what stops one mispaired backtick from reaching the end of the file.
BLANK_LINE = re.compile(r"\n[ \t]*\n")


def _blank(s):
    """Same length, same line breaks, no content."""
    return re.sub(r"[^\n]", " ", s)


def scan_constructs(text):
    """→ (spans, defects). One left-to-right pass over the document.

    At each offset at most one construct opens, and it is consumed whole, so a
    construct can never BEGIN INSIDE another one (ARCHITECTURE §7.4, invariant
    L3). The previous implementation applied four regexes in sequence, each
    over the whole text, with `HTML_COMMENT` ahead of `CODE_SPAN`. A comment
    boundary landing inside a code span removed one backtick; the survivor
    paired with a later one; and from that offset prose was masked as code and
    code scanned as prose, to the end of the file (TASK 097 §1).

    `defects` are facts about the DOCUMENT, not about this scanner — an
    unterminated comment, a backtick that never pairs. They are named in the
    output and exit 0, because a document the project may legitimately hold
    must not fail a phase (`documentation-standards` §4).
    """
    spans, defects = [], []
    i, n = 0, len(text)
    while i < n:
        m = None
        if i == 0 or text[i - 1] == "\n":
            m = FENCE.match(text, i)
        if m is None and text.startswith("<!--", i):
            m = HTML_COMMENT.match(text, i)
            if m is None:
                defects.append(("unterminated comment",
                                text.count("\n", 0, i) + 1))
        if m is None and text.startswith("](", i):
            m = LINK_TARGET.match(text, i)
        if m is None and text[i] == "`":
            m = CODE_SPAN.match(text, i)
            if m is not None and BLANK_LINE.search(m.group(0)):
                m = None                  # a span does not cross a paragraph
            if m is None:
                defects.append(("unpaired backtick",
                                text.count("\n", 0, i) + 1))
        if m is not None and m.end() > m.start():
            spans.append((m.start(), m.end()))
            i = m.end()
        else:
            i += 1
    return spans, defects


def mask(text):
    """Blank every non-prose construct, preserving length and line breaks."""
    m = FRONTMATTER_CANDIDATE.match(text)
    if m and all(YAMLISH.match(l) for l in m.group(1).split("\n") if l.strip()):
        text = _blank(m.group(0)) + text[m.end():]
    out, prev = [], 0
    for start, end in scan_constructs(text)[0]:
        out.append(text[prev:start])
        out.append(_blank(text[start:end]))
        prev = end
    out.append(text[prev:])
    return "".join(out)


def input_defects(text):
    """Document defects the mask pass observed, deduplicated by (kind, line)."""
    seen, ordered = set(), []
    for kind, line in scan_constructs(text)[1]:
        if (kind, line) not in seen:
            seen.add((kind, line))
            ordered.append((kind, line))
    return ordered


def masked_letter_share(text):
    """Share of alphabetic characters the mask removed, 0.0–1.0.

    A zero finding count is only a measurement if the document was read. This
    is the number that separates the two, and `SKILL.md` §2 names it.
    """
    letters = sum(1 for c in text if c.isalpha())
    if not letters:
        return 0.0
    return 1.0 - sum(1 for c in mask(text) if c.isalpha()) / letters


#: A row of the unambiguous pipe-delimited form, which needs no delimiter row
#: to be recognisable as a table row.
PIPE_ROW = re.compile(r"^\s*\|.*(?<!\\)\|\s*$")


def dequote(lines):
    """Strip blockquote prefixes, preserving the line count.

    Structure detection and prose segmentation must see the same text. Stripping
    `>` only inside `prose_blocks` meant a table written inside a `> [!IMPORTANT]`
    callout was invisible to `table_lines`, so its rows fell through to the prose
    path and glued into one 83-word pseudo-sentence.
    """
    return [QUOTE_PREFIX.sub("", l) if QUOTE_PREFIX.match(l) else l
            for l in lines]


def table_lines(lines):
    """→ set of 1-based line numbers that are table rows (delimiter included).

    Two ways in, because neither alone is enough:

    - a line fenced by pipes on both sides is a table row on its own, which is
      how every table in this repository is written;
    - otherwise a table is anchored by its DELIMITER row and extended over the
      contiguous neighbours carrying an unescaped pipe. That second path is
      what admits GFM's pipe-less `a | b` form, whose rows were previously
      segmented as prose and produced spurious sentence findings.
    """
    rows = {i for i, line in enumerate(lines, 1) if PIPE_ROW.match(line)}
    for i, line in enumerate(lines, 1):
        if not line.strip() or not DELIM_ROW.match(line):
            continue
        rows.add(i)
        for step in (-1, 1):
            j = i + step
            while 1 <= j <= len(lines) and lines[j - 1].strip() \
                    and UNESCAPED_PIPE.search(lines[j - 1]):
                rows.add(j)
                j += step
    return rows


def prose_blocks(masked, tables=None):
    """→ [{line, text, map}]. A list item is its own block.

    `map` is [(offset_in_text, line_no)], so a finding is attributed to the line
    that carries it rather than to the block's first line — a 40-word sentence
    at the end of a ten-line paragraph used to be reported ten lines above
    itself.

    Segmenting per block is what keeps a run of `- [ ]` lines from gluing into
    one pseudo-sentence — the defect that invalidated the first TASK 096
    measurement (TC-REG-01). Blockquote prose is included with its `>` prefix
    stripped: `> [!TIP]` callouts in this framework carry real requirements.
    """
    lines = masked.split("\n")
    tables = table_lines(dequote(lines)) if tables is None else tables
    view = dequote(lines)
    blocks, cur, start = [], [], None

    def flush():
        nonlocal cur, start
        if cur:
            text, offs, pos = [], [], 0
            for ln, frag in cur:
                offs.append((pos, ln))
                text.append(frag)
                pos += len(frag) + 1
            blocks.append({"line": start, "text": " ".join(text), "map": offs})
        cur, start = [], None

    for i, line in enumerate(view, 1):
        stripped = line.strip()
        if not stripped or SKIP_LINE.match(line) or i in tables:
            flush()
            continue
        m = LIST_MARK.match(line)
        if m:
            flush()
            cur, start = [(i, line[m.end():].strip())], i
            continue
        if not cur:
            start = i
        cur.append((i, stripped))
    flush()
    return blocks


def sentences(block_text):
    """Split a block into (offset, sentence).

    Emphasis markers are blanked at preserved LENGTH rather than removed, so
    the offsets stay valid. `*Actor:* X. *Main:* Y.` is two sentences, but a
    boundary test looking for whitespace-then-capital sees `*` and joins them —
    the same glue defect as the checklist run, one construct later (TC-REG-03).
    """
    text = EMPHASIS.sub(lambda m: " " * len(m.group(0)), block_text)
    out, last = [], 0
    for m in SENT_SPLIT.finditer(text):
        out.append((last, text[last:m.start()]))
        last = m.end()
    out.append((last, text[last:]))
    return [(o, s) for o, s in out if s.strip()]


def line_at(block, offset):
    """Map an offset inside a block back to the document line carrying it."""
    line = block["line"]
    for pos, ln in block["map"]:
        if pos > offset:
            break
        line = ln
    return line


def sections(text):
    """→ [{title, level, start, end}] — the reading-pass worklist.

    Titles come from the RAW text so that a heading containing a glyph is not
    rendered as a row of blanks by the masker, while the fence check uses the
    masked text so a `#` inside a code block is not a section.

    The pass that produced this skill's own worked example rewrote the one
    section quoted in the guide and left the rest of the document untouched.
    Enumerating sections is what makes "the reading pass was done" a claim with
    a denominator instead of an impression.
    """
    raw_lines = text.split("\n")
    masked_lines = mask(text).split("\n")
    last = len(raw_lines) - (1 if text.endswith("\n") else 0)
    found = []
    for i, (raw, cooked) in enumerate(zip(raw_lines, masked_lines), 1):
        if HEADING.match(cooked):
            m = HEADING.match(raw) or HEADING.match(cooked)
            found.append({"title": m.group(2) or "(untitled)",
                          "level": len(m.group(1)), "start": i, "end": last})
    if not found or found[0]["start"] > 1:
        found.insert(0, {"title": "(preamble)", "level": 0, "start": 1,
                         "end": last})
    for a, b in zip(found, found[1:]):
        a["end"] = b["start"] - 1
    return found


def _cells(line):
    """Table-row cells.

    Split on UNESCAPED pipes only. A `\\|` inside a cell is content, and
    splitting there cut one over-long cell into two short ones -- the finding
    vanished, and a table got wider the more it was escaped.
    """
    return [c.strip() for c in CELL_SPLIT.split(line.strip().strip("|"))]


def scan_document(text, entries, reasoning, thresholds, origin):
    """→ findings [{where, kind, rule, standard, severity, match, …}]."""
    findings = []
    text = normalize(text)
    masked = mask(text)
    lines = dequote(masked.split("\n"))
    tables = table_lines(lines)

    def add(line_no, kind, rule, severity, match, guidance, context, span=None):
        findings.append({
            "where": f"{origin}:{line_no}", "kind": kind, "rule": rule,
            "standard": standard_of(rule), "severity": severity,
            "match": match, "guidance": guidance,
            "context": " ".join(context.split())[:100],
            "_line": line_no, "_span": span})

    # --- rule 1: sentence length, and the band just under the limit ---
    limit = thresholds["sentence_max_words"]
    near = thresholds["sentence_near_words"]
    for block in prose_blocks(masked, tables):
        for offset, sentence in sentences(block["text"]):
            n = len(sentence.split())
            ln = line_at(block, offset)
            if n > limit:
                add(ln, "sentence_length", 1, "warn", f"{n} words",
                    f"Over {limit} words. Split into one claim per sentence.",
                    sentence)
            elif n >= near:
                add(ln, "sentence_near_limit", 1, "info", f"{n} words",
                    f"{limit - n} word(s) under the {limit}-word limit. A "
                    f"distribution that stops at the limit is a distribution "
                    f"written for the gate; judge whether this carries one "
                    f"claim.", sentence)

    # --- documentation-standards §5.1: a cell is a label, not prose ---
    cell_limit = thresholds["cell_max_chars"]
    max_sent = thresholds["cell_max_sentences"]
    prose_at = thresholds["cell_prose_chars"]
    for i in sorted(tables):
        line = lines[i - 1]
        if DELIM_ROW.match(line):
            continue
        for cell in _cells(line):
            if not cell:
                continue
            if len(cell) > cell_limit:
                add(i, "cell_width", SEC_5_1, "warn", f"{len(cell)} chars",
                    f"Over {cell_limit} chars (§5.1). Keep a short marker; "
                    f"move detail to a section below.", cell)
            n_sent = len(sentences(cell))
            if n_sent > max_sent:
                # Severity follows the measurement, not the letter of the rule.
                # §5.1 targets PROSE stuck in a cell. A short cell holding two
                # terse labels -- "Improved. No rule." -- satisfies the letter
                # of "one sentence per cell" and is not that defect. The
                # boundary is its own threshold, derived from the measurement
                # (label pairs ran under 40 chars), not half of an unrelated
                # width limit.
                prose = len(cell) > prose_at
                add(i, "cell_sentences", SEC_5_1, "warn" if prose else "info",
                    f"{n_sent} sentences",
                    f"§5.1 allows {max_sent} sentence per cell. "
                    + ("This cell is prose: keep the first sentence and move "
                       "the rest below the table." if prose else
                       "Short terse labels are judged by the author."), cell)

    # --- rule 5: severity is a named value ---
    for i, line in enumerate(lines, 1):
        for m in EMOJI.finditer(line):
            glyph = m.group(0)
            key = glyph.strip("︎️")
            if key in TICK_GLYPHS or (i in tables and key in STATUS_GLYPHS):
                continue          # a status VALUE, not a severity
            add(i, "emoji_severity", 5, "warn", glyph,
                STATUS_GUIDANCE if key in STATUS_GLYPHS else SEVERITY_GUIDANCE,
                line, (m.start(), m.end()))

    # --- rules 2, 4 and 6: per-language lexicon over masked text ---
    for i, line in enumerate(lines, 1):
        for e in entries:
            for m in e["rx"].finditer(line):
                add(i, RULE_KIND[e["rule"]], e["rule"], e["severity"],
                    m.group(0), e["guidance"], line, (m.start(), m.end()))

    # --- rule 3, structural: a justification inside a requirement ---
    findings += _scan_reasoning(masked, reasoning, origin, tables)
    return _dedupe_spans(findings)


def _dedupe_spans(findings):
    """Drop a finding whose span is contained in another's on the same line.

    The case is a broader marker covering a narrower one, so that one defect is
    reported once: an entry for `not just X but Y` and an entry for `just` both
    match `It is not just fast but correct.` The wider span wins; ties keep the
    first.

    The shipped lexicons produce no such pair today — measured at 0 contained
    spans over the 627 tracked documents of this repository — so the invariant
    is pinned on a synthetic pair by TC-ADV-43, not on shipped data. The
    earlier example here named `просто` inside `не просто X, а Y`, which no
    shipped Russian entry can produce: negative parallelism was measured at a
    zero baseline and never adopted (REG-9).
    """
    keep, byline = [], {}
    for f in findings:
        span = f.pop("_span", None)
        line = f.pop("_line", None)
        if span is None:
            keep.append(f)
            continue
        byline.setdefault(line, []).append((span, f))
    for line, items in byline.items():
        items.sort(key=lambda t: (t[0][0], -(t[0][1] - t[0][0])))
        chosen = []
        for (a, b), f in items:
            if any(a >= x and b <= y for (x, y), _ in chosen):
                continue
            chosen.append(((a, b), f))
        keep += [f for _, f in chosen]
    return keep


def _scan_reasoning(masked, reasoning, origin, tables=None):
    """Rule 3: one sentence carrying both an obligation and its justification.

    Recall limit, stated rather than implied: this sees a requirement and a
    causal connective INSIDE ONE SENTENCE. Reasoning braided across two
    sentences of the same paragraph is invisible to it and belongs to the
    reading pass.
    """
    if not reasoning:
        return []
    modals = reasoning.get("modals") or []
    causals = reasoning.get("causals") or []
    if not modals or not causals:
        return []
    mod_rx = re.compile("|".join(f"(?:{v})" for v in modals), re.IGNORECASE)
    cau_rx = re.compile("|".join(f"(?:{v})" for v in causals), re.IGNORECASE)
    out = []
    for block in prose_blocks(masked, tables):
        for offset, sentence in sentences(block["text"]):
            m, c = mod_rx.search(sentence), cau_rx.search(sentence)
            if m and c:
                out.append({
                    "where": f"{origin}:{line_at(block, offset)}",
                    "kind": "reasoning", "rule": 3,
                    "standard": standard_of(3), "severity": "info",
                    "match": f"{m.group(0)} … {c.group(0)}",
                    "guidance": "Rule 3: the requirement states what must "
                                "hold; its justification moves under a "
                                "`**Why.**` lead-in or into Notes.",
                    "context": " ".join(sentence.split())[:100]})
    return out


# ------------------------------------------------------------------ terms ----
def load_terms(paths):
    """→ (lowercased blob, errors). Sources that declare established terms."""
    blob, errors = [], []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                blob.append(normalize(f.read()).lower())
        except (OSError, ValueError) as exc:
            # UnicodeDecodeError is a ValueError, and a binary --terms file
            # used to escape as an uncaught traceback with exit 1 — a code
            # outside the documented contract.
            errors.append(f"{p}: unreadable ({type(exc).__name__}: {exc})")
    return "\n".join(blob), errors


def apply_terms(findings, terms_blob, sources):
    """Downgrade rule-6 findings whose surface string occurs in the sources.

    Matched on WORD BOUNDARIES. A substring test downgraded `leg` because the
    sources contained `legacy`, `seam` because of `seamless` and `tail` because
    of `detailed` — silently converting the actionable band into `info` under a
    message asserting the term was declared.

    DOWNGRADE, never suppress. The guide's test is "does this appear in
    ARCHITECTURE.md, a public API, or a cited standard" — and a metaphor that
    spread into the architecture document satisfies that test while still being
    a metaphor. The author confirms; the scanner only says which ones have a
    claim to termhood.
    """
    if not terms_blob:
        return findings, 0
    label = ", ".join(os.path.basename(s) for s in sources)
    hits = 0
    for f in findings:
        if f["rule"] != 6:
            continue
        needle = f["match"].lower()
        if re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", terms_blob):
            f["severity"] = "info"
            f["guidance"] = (f"Occurs as a whole word in the declared term "
                             f"sources ({label}). Confirm it is a term there "
                             f"and not the same metaphor repeated; if it is a "
                             f"term, keep it verbatim.")
            hits += 1
    return findings, hits


# ------------------------------------------------------------- diagnostics ----
#: A fixture must reach the detector through the LINE FILTER, not only through
#: the rule. Rule 1 and rule 3 read `prose_blocks`, which drops a line matching
#: `SKIP_LINE` before any rule sees it, and most prose in the corpora this skill
#: scans is written as list items. Adding `[-*+]\s` to that alternation took
#: `sentence_length` from 826 findings to 546, `sentence_near_limit` from 712 to
#: 517 and `reasoning` from 22 to 16 over 636 documents, while the battery
#: printed `174/174 passed` and this roster printed `18/18 detectors live`, both
#: exit 0 (REG-17). Every fixture for those rules is therefore run in both line
#: forms, and a kind is live only when both fire.
#:
#: A form per ROW rather than a row per form: the roster is 18, and `SKILL.md`
#: §5, `System/Docs/SKILLS.md` and TASK 099 `TC-099-02`/`TC-099-03` state that
#: number (TASK 100 D3).
#:
#: BOTH list forms, because `LIST_MARK` accepts both and the corpus uses both:
#: 12,415 bullet lines and 3,336 ordered-list lines against 34,852 other
#: non-blank lines. With the bullet form alone, widening `SKIP_LINE` with
#: `\d+\.\s` instead cost 63 findings at `18/18 detectors live` exit 0.
LINE_FORMS = (("bare", "{}"), ("list item", "- {}"),
              ("ordered item", "1. {}"))


def _structural_probes(thresholds):
    """Known-positive fixtures built from the ACTIVE thresholds.

    → [(kind, [(form_name, fixture), ...])]. Deriving the fixtures from the
    thresholds is what stops a moved threshold from leaving a probe behind,
    still green against a value nobody uses. It is also why a threshold cannot
    be pinned HERE: both sides of that comparison move together. The battery
    pins the threshold values against a literal (REG-15).

    The kinds returned here are `STRUCTURAL_KINDS`, which pins them into
    `PROBE_ROSTER`: adding a fixture without adding its name there leaves the
    roster short by one row, and the roster is the number the CI gate states.

    The cell rules and rule 5 carry one form each. `prose_blocks` never sees a
    table row, and the rule-5 loop reads every line without consulting
    `SKIP_LINE`, so a second form there would measure nothing new.
    """
    limit = thresholds["sentence_max_words"]
    near = thresholds["sentence_near_words"]
    wide = "x" * (thresholds["cell_max_chars"] + 10)
    prose_cell = ("Alpha " * ((thresholds["cell_prose_chars"] // 6) + 2)
                  + "ends. Second sentence here.")
    long_sentence = "Alpha " + "word " * (limit + 4) + "ends."
    near_sentence = "Alpha " + "word " * (near - 2) + "ends."
    return [
        ("sentence_length", [(n, f.format(long_sentence))
                             for n, f in LINE_FORMS]),
        ("sentence_near_limit", [(n, f.format(near_sentence))
                                 for n, f in LINE_FORMS]),
        ("cell_width", [("table", f"| a | b |\n| --- | --- |\n| {wide} | ok |")]),
        ("cell_sentences",
         [("table", f"| a | b |\n| --- | --- |\n| {prose_cell} | ok |")]),
        ("emoji_severity", [("bare", "\U0001F534 Critical: the thing.")]),
    ]


def _entry_fires(entry, text, thresholds, rule):
    """→ True when `entry` alone reports its own kind on `text`."""
    return any(h["match"] for h in scan_document(
        text + "\n", [entry], None, thresholds, "<probe>")
        if h["kind"] == RULE_KIND[rule])


def _pin_roster(results):
    """→ the rows ordered by `PROBE_ROSTER`, one DEAD row per absent class.

    A class with no detector used to emit NO ROW, so the gate divided a shrunk
    numerator by an equally shrunk denominator and reported the survivors as
    `N/N detectors live`, exit 0 (REG-4). The roster is the contract; a class
    missing from it is a failure, not a smaller run.
    """
    seen = {k for k, _, _ in results}
    for kind in PROBE_ROSTER:
        if kind not in seen:
            results.append((kind, False,
                            f"no detector for this class in this language "
                            f"— the roster is {len(PROBE_ROSTER)} per "
                            f"shipped language"))
    order = {k: i for i, k in enumerate(PROBE_ROSTER)}
    return sorted(results, key=lambda r: order.get(r[0], len(order)))


def verify_detectors(entries, reasoning, thresholds, strict=False):
    """Probe every detector against a known positive → [(kind, live, detail)].

    Structural detectors use synthesised fixtures. Every lexicon entry uses its
    own required `probe` string, so a zero from a marker rule is a measured
    zero rather than an unexercised one.

    Under `strict` the result is pinned to `PROBE_ROSTER`, which is what the
    shipped data is held to. It defaults off because a caller passing its own
    `--rules` file is entitled to configure fewer classes than this skill ships.
    """
    results = []
    for kind, forms in _structural_probes(thresholds):
        missed = [name for name, fixture in forms
                  if not any(h["kind"] == kind for h in scan_document(
                      fixture + "\n", [], None, thresholds, "<probe>"))]
        results.append((kind, not missed,
                        f"synthesised fixture, {len(forms)} line form(s)"
                        + (f"; no hit as: {', '.join(missed)}" if missed
                           else "")))

    for rule in LEXICAL_RULES:
        group = [e for e in entries if e["rule"] == rule]
        if not group:
            continue
        dead, caseblind = [], []
        for e in group:
            if not _entry_fires(e, e["probe"], thresholds, rule):
                dead.append(e["marker"])
                continue
            # An entry declaring `i` must still match when the case of its own
            # probe is flipped. Both the loader and the line above run an entry
            # against ITS OWN probe, and most shipped probes are lower-case
            # prose, so removing `"flags": "i"` left the entry matching that one
            # sentence and nothing else: 35 entries lost the key with the
            # battery at `174/174` and this roster at `18/18`, both exit 0, and
            # 15 real `marker` findings gone (REG-16). Applied only where the
            # flag is DECLARED -- `head / tail (of a call)` omits it on purpose,
            # because with `i` it matched the git ref `HEAD` corpus-wide.
            if "i" in (e.get("flags") or "") and not _entry_fires(
                    e, e["probe"].swapcase(), thresholds, rule):
                caseblind.append(e["marker"])
        verified = len(group) - len(dead) - len(caseblind)
        results.append((RULE_KIND[rule], not dead and not caseblind,
                        f"{verified}/{len(group)} entries verified"
                        + (f"; dead: {', '.join(dead)}" if dead else "")
                        + (f"; case-blind: {', '.join(caseblind)}"
                           if caseblind else "")))

    if reasoning and reasoning.get("probe"):
        # One declared sentence exercised the ONE modal and the ONE causal it
        # happened to contain, while the row advertised the whole cross-product.
        # Deleting any other pattern left `--probe` at 18/18 and the battery at
        # 128/128 — the count before commit 5c9da31 raised it to 145 — while
        # real findings vanished (TASK 097 D3). Each pattern is now exercised
        # against a known-good partner, so killing any one of them turns this
        # row DEAD.
        modals = reasoning.get("modals") or []
        causals = reasoning.get("causals") or []
        anchor_m = _reasoning_literal(reasoning, modals[0]) if modals else None
        anchor_c = _reasoning_literal(reasoning, causals[0]) if causals else None
        dead, unprobed, exercised = [], [], 0
        if anchor_m and anchor_c:
            for key, group, partner in (("modal", modals, anchor_c),
                                        ("causal", causals, anchor_m)):
                for pat in group:
                    lit = _reasoning_literal(reasoning, pat)
                    if lit is None:
                        # No example in the data. `_validate_reasoning` now
                        # rejects that at load (TASK 099 D7), so this is
                        # unreachable through the loader — and it counts
                        # against liveness rather than being merely reported,
                        # because the reported-and-live state is the one that
                        # re-opened TASK 097 D3 with every gate green.
                        unprobed.append(pat)
                        continue
                    sentence = (f"The field {lit} be set {partner} it holds."
                                if key == "modal" else
                                f"The field {partner} be set {lit} it holds.")
                    exercised += 1
                    # Both line forms, for the reason `LINE_FORMS` states: rule
                    # 3 reads `prose_blocks`, so a `SKIP_LINE` that swallows a
                    # list marker takes this vocabulary from 22 corpus findings
                    # to 16 with every gate at exit 0 (REG-17).
                    missed = [name for name, form in LINE_FORMS
                              if not _scan_reasoning(
                                  mask(form.format(sentence) + "\n"),
                                  reasoning, "<probe>")]
                    if missed:
                        dead.append(f"{key} {pat} ({', '.join(missed)})")
        else:
            # Nothing to pair against, so no pattern below can be exercised.
            # The previous row reported `bool(hits)` on the declared sentence,
            # which the loader had already made a precondition — provably True
            # in every run that reached it, and therefore not a measurement
            # (REG-3). This branch stands between a future loader regression
            # and a falsely-live roster, so it reports DEAD rather than
            # re-asserting what the loader guaranteed.
            total = len(modals) + len(causals)
            results.append(("reasoning", False,
                            f"0 exercised of {total} patterns — no example in "
                            f"`probes` to pair against, so the vocabulary is "
                            f"not verified by this run"))
            return _pin_roster(results) if strict else results
        total = len(modals) + len(causals)
        results.append(("reasoning", not dead and not unprobed,
                        f"{exercised} exercised of {total} patterns, "
                        f"{len(LINE_FORMS)} line form(s) each"
                        + (f"; unprobed: {', '.join(unprobed)}" if unprobed
                           else "")
                        + (f"; dead: {', '.join(dead)}" if dead else "")))
    return _pin_roster(results) if strict else results


def diagnostics(text, entries, reasoning, thresholds, findings, lang, counts):
    """Measured coverage of this document → what each detector actually saw.

    A bare zero is the failure mode this block exists to prevent. Every share
    below states its own denominator: the previous version printed
    `prose_lines / total_lines` under a percentage computed from
    `prose_lines / non_empty_lines`, so a document that was 80% fenced code
    reported `20/100 lines (100%)`.
    """
    text = normalize(text)
    masked = mask(text)
    lines = dequote(masked.split("\n"))
    if text.endswith("\n") and lines and lines[-1] == "":
        lines = lines[:-1]          # the phantom line `split` leaves behind
    raw_lines = text.split("\n")[:len(lines)]
    tables = table_lines(lines)

    blocks = prose_blocks(masked, tables)
    lengths = [len(s.split()) for b in blocks for _, s in sentences(b["text"])
               if s.split()]
    widths, per_cell = [], []
    for i in sorted(tables):
        if DELIM_ROW.match(lines[i - 1]):
            continue
        for c in _cells(lines[i - 1]):
            if c:
                widths.append(len(c))
                per_cell.append(len(sentences(c)))

    nonblank = sum(1 for l in raw_lines if l.strip())
    masked_away = sum(1 for r, m in zip(raw_lines, lines)
                      if r.strip() and not m.strip())
    prose = sum(1 for i, l in enumerate(lines, 1)
                if l.strip() and not SKIP_LINE.match(l) and i not in tables)
    limit = thresholds["sentence_max_words"]
    band = thresholds["sentence_pressure_band"]
    observed = max(lengths) if lengths else 0
    return {
        "lines": len(lines),
        "nonblank_lines": nonblank,
        "masked_lines": masked_away,
        # A zero is only a measurement if the document was read. These two say
        # how much of it reached the rules, and what stopped the rest.
        "masked_letter_share": round(masked_letter_share(text), 3),
        "input_defects": [{"defect": k, "line": n}
                          for k, n in input_defects(text)],
        "table_lines": len(tables),
        "prose_lines": prose,
        "prose_share_of_nonblank": round(100 * prose / max(1, nonblank)),
        "language": lang,
        "cyrillic_letters": counts.get("cyrillic", 0),
        "latin_letters": counts.get("latin", 0),
        "sentences": len(lengths),
        "sentence_max_observed": observed,
        "sentence_max_limit": limit,
        "sentence_mean": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "sentence_pressure": bool(lengths) and limit - band <= observed <= limit,
        "sentence_pressure_band": band,
        "cells": len(widths),
        "cell_max_observed": max(widths) if widths else 0,
        "cell_max_limit": thresholds["cell_max_chars"],
        "cell_sentences_max_observed": max(per_cell) if per_cell else 0,
        "lexicon_entries": len(entries),
        "reasoning_vocabulary": bool(reasoning and reasoning.get("modals")
                                     and reasoning.get("causals")),
        "terms_downgrades": counts.get("terms_downgrades", 0),
        "findings_by_kind": {k: sum(1 for f in findings if f["kind"] == k)
                             for k in sorted({f["kind"] for f in findings})},
    }


def section_report(text, findings, origin):
    """→ [{title, lines, warn, info}] — one row per section of one document."""
    own = [f for f in findings if f["where"].rsplit(":", 1)[0] == origin]
    rows = []
    for sec in sections(normalize(text)):
        inside = [f for f in own
                  if sec["start"] <= int(f["where"].rsplit(":", 1)[1]) <= sec["end"]]
        rows.append({
            "title": sec["title"], "level": sec["level"],
            "lines": f"{sec['start']}-{sec['end']}",
            "warn": sum(1 for f in inside if f["severity"] == "warn"),
            "info": sum(1 for f in inside if f["severity"] == "info")})
    return rows


def detect_lang(text):
    """→ (lang, cyrillic, latin). Counted on MASKED text.

    Counting the raw text let a Russian document with a large English code
    listing resolve to `en`: the whole Russian lexicon was skipped, and because
    `en` HAS a rule file the "no lexicon for this language" note never fired.
    """
    masked = mask(normalize(text))
    cyr = len(CYR.findall(masked))
    lat = len(re.findall(r"[A-Za-z]", masked))
    return ("ru" if cyr >= max(1, lat // 3) else "en"), cyr, lat


def render_list(lex, lang=None):
    def esc(s):
        return s.replace("|", "\\|")

    langs = [lang] if lang else sorted(lex)
    out = []
    for lg in langs:
        if lg not in lex:
            continue
        out.append(f"## {lg}\n")
        out.append("| Rule | Marker | Severity | Guidance | Category |")
        out.append("|---|---|---|---|---|")
        for e in sorted(lex[lg], key=lambda x: (x["rule"], x["marker"])):
            out.append(f"| {label_of(e['rule'])} | {esc(e['marker'])} "
                       f"| {e['severity']} | {esc(e['guidance'])} "
                       f"| {esc(e['category'])} |")
        out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------- cli ----
def _print_text(warn, info, diag, detectors, secrows):
    for f in warn:
        print(f"[WARN] {f['where']} ({label_of(f['rule'])}, {f['kind']}): "
              f"{f['match']}\n       → {f['guidance']}")
    for f in info:
        print(f"[info] {f['where']} ({label_of(f['rule'])}, {f['kind']}): "
              f"{f['match']}\n       → {f['guidance']}")

    print(f"\n{len(warn)} warn / {len(info)} info — advisory, exit 0")
    print("\nDETECTORS (probe-tested this run)")
    for lang, kind, live, detail in detectors:
        print(f"  {'live' if live else 'DEAD'}  {lang}  {kind:<20} {detail}")
    for origin, d in diag.items():
        print(f"\nDIAGNOSTICS {origin}  (language: {d['language']} — "
              f"{d['cyrillic_letters']} Cyrillic / {d['latin_letters']} Latin "
              f"letters after masking)")
        print(f"  lines                 : {d['lines']} total, "
              f"{d['nonblank_lines']} non-blank, {d['masked_lines']} masked "
              f"away, {d['table_lines']} table")
        print(f"  letters masked away   : "
              f"{round(100 * d['masked_letter_share'])}% "
              f"(non-prose constructs; a high share with no fenced block is "
              f"the signal to read next)")
        for df in d["input_defects"]:
            # The document, not the instrument: named here and exit 0.
            print(f"  INPUT DEFECT          : {df['defect']} at line "
                  f"{df['line']}")
        print(f"  prose reaching rule 1 : {d['prose_lines']} of "
              f"{d['nonblank_lines']} non-blank "
              f"({d['prose_share_of_nonblank']}%)")
        print(f"  sentences             : {d['sentences']}, mean "
              f"{d['sentence_mean']}, max {d['sentence_max_observed']} "
              f"(limit {d['sentence_max_limit']})"
              + ("   <-- PRESSED AGAINST THE LIMIT" if d["sentence_pressure"]
                 else ""))
        print(f"  table cells           : {d['cells']}, widest "
              f"{d['cell_max_observed']} (limit {d['cell_max_limit']}), most "
              f"sentences in one cell {d['cell_sentences_max_observed']}")
        print(f"  lexicon entries active: {d['lexicon_entries']}"
              f"   rule-3 vocabulary: "
              f"{'yes' if d['reasoning_vocabulary'] else 'no'}"
              f"   rule-6 downgrades by --terms: {d['terms_downgrades']}")
        if d["sentence_pressure"]:
            print("  NOTE: the longest sentence sits within "
                  f"{d['sentence_pressure_band']} words of the limit. Read the "
                  "`sentence_near_limit` findings; a zero here is not evidence "
                  "of a conforming document.")
    if secrows:
        print("\nREADING-PASS WORKLIST (rules 3, 4 and 6 are not fully "
              "reachable by any detector)")
        for origin, rows in secrows.items():
            print(f"  {origin}")
            for r in rows:
                print(f"    [ ] {r['lines']:>10}  {'  ' * r['level']}"
                      f"{r['title'][:58]:<60} warn {r['warn']:<3} "
                      f"info {r['info']}")


def build_parser():
    ap = argparse.ArgumentParser(
        description="Scan authored artifacts for register defects "
                    "(advisory: findings never fail the run)")
    ap.add_argument("files", nargs="*", help=".md/.txt, or stdin")
    ap.add_argument("--rules", action="append", dest="rules",
                    help="rule file(s); default data/register-*.json")
    ap.add_argument("--terms", action="append", dest="terms",
                    help="file(s) declaring established terminology "
                         "(ARCHITECTURE.md, a glossary); rule-6 findings found "
                         "there as whole words are downgraded to info")
    ap.add_argument("--lang", default="auto")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sections", action="store_true",
                    help="print the per-section reading-pass worklist")
    ap.add_argument("--probe", action="store_true",
                    help="verify every detector against a known positive and "
                         "exit; 2 if any detector is dead")
    ap.add_argument("--list", nargs="?", const="", default=None, metavar="LANG")
    ap.add_argument("--allow-missing", action="store_true",
                    help="an ABSENT file is named and skipped instead of "
                         "exiting 3. For the artifacts this framework archives "
                         "(docs/TASK.md, docs/PLAN.md); without it a mistyped "
                         "path is caught. A present-but-unreadable file still "
                         "exits 3, and an empty input set always does.")
    return ap


def _fail(args_json, payload):
    print(json.dumps(payload, ensure_ascii=False, indent=1)
          if args_json else json.dumps(payload, ensure_ascii=False),
          file=sys.stderr)


def main(argv=None):
    ap = build_parser()
    ap.exit_on_error = False
    try:
        args = ap.parse_args(argv)
    except argparse.ArgumentError as exc:
        # argparse's own exit code is 2, which is this tool's "broken
        # instrument". A typo in a flag must not read as a dead detector.
        print(f"usage error: {exc}", file=sys.stderr)
        return 3
    except SystemExit as exc:
        return 0 if exc.code == 0 else 3

    if args.probe and args.list is not None:
        print("usage error: --probe and --list are mutually exclusive",
              file=sys.stderr)
        return 3

    rule_paths = args.rules or sorted(
        glob.glob(os.path.join(SKILL, "data", "register-*.json")))
    # Same file named twice loaded its markers twice and doubled every lexical
    # finding, so a count depended on how the command was typed. Resolved via
    # realpath so `--rules a.json --rules ./a.json` is also one file.
    rule_paths = list(dict.fromkeys(os.path.realpath(p) for p in rule_paths))
    if not rule_paths:
        _fail(args.json, {"ok": False, "error": "no rule files found"})
        return 2

    lex, reasoning, thresholds, errors = load_rules(rule_paths)
    if errors:
        _fail(args.json, {"ok": False, "rule_errors": errors})
        return 2

    # --terms is validated BEFORE any early return: `--probe --terms missing`
    # used to exit 0, silently skipping the check the operator asked for.
    terms_blob, term_errors = ("", [])
    if args.terms:
        terms_blob, term_errors = load_terms(args.terms)
        if term_errors:
            _fail(args.json, {"ok": False, "term_errors": term_errors})
            return 2

    if args.list is not None:
        if args.list and args.list not in lex:
            print(f"usage error: no rules for language {args.list!r} "
                  f"(available: {', '.join(sorted(lex)) or 'none'})",
                  file=sys.stderr)
            return 3
        print(render_list(lex, args.list or None))
        return 0

    if args.probe:
        rows, dead = [], False
        # The UNION, not the loaded languages: enumerating what was loaded is
        # how deleting `register-ru.json` printed `9/9 detectors live` exit 0
        # (REG-4). A shipped language absent from the data now contributes its
        # nine rows, with every lexical class DEAD.
        strict_langs = set() if args.rules else set(SHIPPED_LANGS)
        for lang in sorted(set(lex) | strict_langs):
            for kind, live, detail in verify_detectors(
                    lex.get(lang, []), reasoning.get(lang), thresholds,
                    strict=lang in strict_langs):
                rows.append((lang, kind, live, detail))
                dead = dead or not live
        if args.json:
            print(json.dumps({"ok": not dead, "probes": [
                {"lang": l, "detector": k, "live": v, "detail": d}
                for l, k, v, d in rows]}, ensure_ascii=False, indent=1))
        else:
            for l, k, v, d in rows:
                print(f"{'live' if v else 'DEAD'}  {l}  {k:<20} {d}")
            print(f"\n{sum(1 for r in rows if r[2])}/{len(rows)} detectors live")
        return 2 if dead else 0

    # A path this tool cannot read is an INVOCATION error (3), never a broken
    # instrument (2). Under 2 the CI advisory step failed whenever docs/TASK.md
    # was absent — which is this framework's own state between `skill-archive-
    # task` and the next analysis phase — while its comment claimed it could
    # fail only on a dead detector (TASK 097 D2).
    inputs, missing = [], []
    if args.files:
        for fp in args.files:
            try:
                # the path AS GIVEN: two files both named SKILL.md must be
                # distinguishable in a multi-file scan
                with open(fp, encoding="utf-8") as f:
                    inputs.append((fp, f.read()))
            except FileNotFoundError as exc:
                if not args.allow_missing:
                    _fail(args.json, {"ok": False, "error": f"{fp}: {exc}"})
                    return 3
                missing.append(fp)
            except (OSError, ValueError) as exc:
                # Present but unreadable is never tolerated: --allow-missing
                # names an absence the framework produces, not a broken file.
                _fail(args.json, {"ok": False, "error": f"{fp}: {exc}"})
                return 3
        if not inputs:
            # Nothing was scanned, so nothing was measured. Reporting 0 here
            # would be the bare zero this tool exists to prevent.
            _fail(args.json, {"ok": False, "missing": missing,
                              "error": "no readable input"})
            return 3
        for fp in missing:
            print(f"SKIPPED (absent, --allow-missing): {fp}", file=sys.stderr)
    else:
        try:
            inputs.append(("stdin", sys.stdin.read()))
        except (OSError, ValueError) as exc:
            _fail(args.json, {"ok": False, "error": f"stdin: {exc}"})
            return 3

    # A repeated path doubled the findings while collapsing the diagnostics
    # entry, so `counts.warn` and `diagnostics[…]` disagreed in the same
    # document. Dedup by realpath, keeping the path as the operator typed it.
    seen, deduped = set(), []
    for origin, raw in inputs:
        key = os.path.realpath(origin) if origin != "stdin" else "stdin"
        if key in seen:
            continue
        seen.add(key)
        deduped.append((origin, raw))

    findings, diag, secrows, detectors, dead = [], {}, {}, [], []
    probed = set()
    for origin, raw in deduped:
        auto, cyr, lat = detect_lang(raw)
        lang = args.lang if args.lang != "auto" else auto
        if lang not in lex:
            print(f"note: {origin}: language {lang!r} has no rule file "
                  f"(available: {', '.join(sorted(lex)) or 'none'}) — "
                  f"structural checks ran, zero lexical findings by "
                  f"construction", file=sys.stderr)
        elif args.lang == "auto" and min(cyr, lat) and max(cyr, lat) < 3 * min(cyr, lat):
            print(f"note: {origin}: language resolved to {lang!r} on a close "
                  f"call ({cyr} Cyrillic vs {lat} Latin letters after "
                  f"masking) — pass --lang to pin it", file=sys.stderr)
        entries, reason = lex.get(lang, []), reasoning.get(lang)
        if lang not in probed:
            probed.add(lang)
            for kind, live, detail in verify_detectors(
                    entries, reason, thresholds,
                    strict=not args.rules and lang in SHIPPED_LANGS):
                detectors.append((lang, kind, live, detail))
                if not live:
                    dead.append(f"{lang}/{kind}: {detail}")
        mine = scan_document(raw, entries, reason, thresholds, origin)
        mine, downgrades = apply_terms(mine, terms_blob, args.terms or [])
        findings += mine
        diag[origin] = diagnostics(raw, entries, reason, thresholds, mine, lang,
                                   {"terms_downgrades": downgrades,
                                    "cyrillic": cyr, "latin": lat})
        if args.sections:
            secrows[origin] = section_report(raw, mine, origin)

    warn = [f for f in findings if f["severity"] == "warn"]
    info = [f for f in findings if f["severity"] == "info"]

    if args.json:
        print(json.dumps({"ok": not dead, "warn": warn, "info": info,
                          "thresholds": thresholds,
                          "terms_sources": args.terms or [],
                          "detectors": [{"lang": l, "detector": k, "live": v,
                                         "detail": d}
                                        for l, k, v, d in detectors],
                          "dead_detectors": dead,
                          "diagnostics": diag,
                          "sections": secrows,
                          "counts": {"warn": len(warn), "info": len(info)}},
                         ensure_ascii=False, indent=1))
    else:
        _print_text(warn, info, diag, detectors, secrows)

    if dead:
        _fail(args.json, {"ok": False, "dead_detectors": dead})
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
