#!/usr/bin/env python3
"""Acceptance battery for scan_register.py (TASK 096).

Covers the schema (including the probe contract every entry must satisfy),
masking, one case per detector, the dead-detector exit, diagnostics, the
section worklist, the `--terms` downgrade, and every exit code.

Run: python3 selftest_scan.py    → 0 all green / 1 any failure
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCANNER = os.path.join(HERE, "scan_register.py")

RESULTS: list[tuple[str, bool, str]] = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def run(args, text=None):
    """→ (exit_code, stdout, stderr)"""
    p = subprocess.run([sys.executable, SCANNER] + args, input=text,
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def scan_json(paths, extra=None):
    code, out, err = run(list(paths) + ["--json"] + (extra or []))
    try:
        return code, json.loads(out), err
    except ValueError:
        return code, None, err


def tmpfile(content, suffix=".md"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def rules_file(doc):
    return tmpfile(json.dumps(doc, ensure_ascii=False), ".json")


def kinds_of(rep):
    return [h["kind"] for h in ((rep["warn"] + rep["info"]) if rep else [])]


GOOD_RULES = {
    "schema": "register-rules/v1",
    "thresholds": {"sentence_max_words": 35, "sentence_near_words": 30,
                   "cell_max_chars": 120, "cell_max_sentences": 1},
    "languages": {"en": {"categories": [{"name": "t", "entries": [
        {"marker": "obviously", "pattern": r"\bobviously\b", "flags": "i",
         "severity": "warn", "guidance": "delete",
         "probe": "This is obviously wrong."},
        {"marker": "exactly", "pattern": r"\bexactly\b", "flags": "i",
         "severity": "info", "guidance": "judge",
         "probe": "It runs exactly once."},
    ]}]}},
}


def entry_rules(entry):
    """A one-entry rule file, for probing a single validation branch."""
    doc = json.loads(json.dumps(GOOD_RULES))
    doc["languages"]["en"]["categories"][0]["entries"] = [entry]
    return doc


# ---------------------------------------------------------------- schema ----
def t_schema():
    bad = [
        ("TC-SCHEMA-01 non-object root", [], 'rule file root must be an object'),
        ("TC-SCHEMA-02 wrong schema value",
         {"schema": "nope", "languages": GOOD_RULES["languages"]}, 'schema must be'),
        ("TC-SCHEMA-03 empty languages",
         {"schema": "register-rules/v1", "languages": {}}, 'languages must be a non-empty object'),
        ("TC-SCHEMA-04 entry missing guidance",
         entry_rules({"marker": "x", "pattern": "x", "probe": "x"}), 'guidance is required'),
        ("TC-SCHEMA-05 pattern does not compile",
         entry_rules({"marker": "x", "pattern": "[unclosed", "guidance": "g",
                      "probe": "x"}), 'pattern does not compile'),
        ("TC-SCHEMA-06 unknown entry key",
         entry_rules({"marker": "x", "pattern": "x", "guidance": "g",
                      "probe": "x", "bogus": 1}), 'unknown keys'),
        ("TC-SCHEMA-07 bad severity",
         entry_rules({"marker": "x", "pattern": "x", "guidance": "g",
                      "probe": "x", "severity": "loud"}), 'severity must be one of'),
        ("TC-SCHEMA-09 entry missing probe",
         entry_rules({"marker": "x", "pattern": "x", "guidance": "g"}), 'probe is required'),
        ("TC-SCHEMA-10 pattern does not match its own probe",
         entry_rules({"marker": "x", "pattern": r"\bfrobnicate\b",
                      "guidance": "g", "probe": "nothing matches here"}), 'does not match its own probe'),
        ("TC-SCHEMA-11 probe hidden inside a code span",
         entry_rules({"marker": "x", "pattern": r"\bfrob\b", "guidance": "g",
                      "probe": "the word `frob` is quoted"}), 'contains a masked construct'),
        ("TC-SCHEMA-12 unknown rule number",
         entry_rules({"marker": "x", "pattern": "x", "guidance": "g",
                      "probe": "x", "rule": 9}), 'rule must be one of'),
        ("TC-SCHEMA-13 near band at or above the hard limit",
         {"schema": "register-rules/v1",
          "thresholds": {"sentence_max_words": 35, "sentence_near_words": 35},
          "languages": GOOD_RULES["languages"]}, 'must be below'),
    ]
    doc = tmpfile("plain text\n")
    # Each case names the message fragment it expects. The previous shared
    # predicate was `exit == 2 and stderr non-empty`, which passed when a rule
    # file was rejected for the WRONG reason -- thirteen cases asserting one
    # thing between them.
    for name, rules, fragment in bad:
        rf = rules_file(rules)
        code, out, err = run([doc, "--rules", rf, "--json"])
        check(name, code == 2 and fragment in err,
              f"exit={code} want={fragment!r} stderr={err.strip()[:130]}")

    # conflicting thresholds across two files must be loud, not order-dependent
    a = rules_file(GOOD_RULES)
    b = json.loads(json.dumps(GOOD_RULES))
    b["thresholds"]["sentence_max_words"] = 20
    code, _, err = run([doc, "--rules", a, "--rules", rules_file(b), "--json"])
    check("TC-SCHEMA-08 conflicting thresholds rejected", code == 2,
          f"exit={code} stderr={err.strip()[:90]}")

    # a rule-3 vocabulary that does not fire on its own probe is dead on arrival
    r3 = json.loads(json.dumps(GOOD_RULES))
    r3["languages"]["en"]["reasoning"] = {
        "modals": [r"\bmust\b"], "causals": [r"\bbecause\b"],
        "probe": "This sentence carries neither."}
    code, _, err = run([doc, "--rules", rules_file(r3), "--json"])
    check("TC-SCHEMA-14 rule-3 probe must trigger the detector", code == 2,
          f"exit={code} stderr={err.strip()[:110]}")

    r3["languages"]["en"]["reasoning"]["probe"] = \
        "The field must be set, because the reader cannot derive it."
    code, _, err = run([doc, "--rules", rules_file(r3), "--json"])
    check("TC-SCHEMA-15 a firing rule-3 probe is accepted", code == 0,
          f"exit={code} stderr={err.strip()[:110]}")


# --------------------------------------------------------------- masking ----
def t_masking():
    rf = rules_file(GOOD_RULES)

    cases = [
        ("TC-MASK-01 code span", "The word `obviously` is quoted here.\n"),
        ("TC-MASK-02 fenced block",
         "text\n\n```\nobviously\n```\n\nmore text\n"),
        ("TC-MASK-03 link target",
         "See [the doc](../docs/obviously/page.md) for detail.\n"),
        ("TC-MASK-04 html comment", "<!-- obviously a note -->\ntext\n"),
    ]
    for name, body in cases:
        doc = tmpfile(body)
        code, rep, err = scan_json([doc], ["--rules", rf])
        hits = rep["counts"]["warn"] if rep else -1
        check(name, code == 0 and hits == 0, f"exit={code} warn={hits}")

    # YAML frontmatter is metadata, not prose
    fm = ("---\nname: x\ndescription: " + "word " * 45 + "\ntier: 2\n---\n\n"
          "Short body sentence.\n")
    doc = tmpfile(fm)
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-MASK-06 frontmatter is not scanned as prose",
          code == 0 and "sentence_length" not in kinds_of(rep),
          f"kinds={kinds_of(rep)}")

    # two files sharing a basename must stay distinguishable
    d1 = os.path.join(tempfile.mkdtemp(), "SKILL.md")
    d2 = os.path.join(tempfile.mkdtemp(), "SKILL.md")
    for p in (d1, d2):
        open(p, "w", encoding="utf-8").write("This is obviously wrong.\n")
    code, rep, _ = scan_json([d1, d2], ["--rules", rf])
    wheres = {h["where"].rsplit(":", 1)[0] for h in (rep["warn"] if rep else [])}
    check("TC-ORIGIN-01 same-basename files are distinguishable",
          code == 0 and len(wheres) == 2, f"origins={wheres}")

    # the control: masking must not be blanket suppression
    doc = tmpfile("This is obviously the wrong register.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-MASK-05 control: plain prose IS reported",
          code == 0 and rep and rep["counts"]["warn"] == 1,
          f"warn={rep['counts']['warn'] if rep else 'n/a'}")

    # line numbers survive masking
    doc = tmpfile("`code` here\n\nfiller\n\nThis is obviously wrong.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    where = rep["warn"][0]["where"] if rep and rep["warn"] else ""
    check("TC-REG-02 line numbers survive masking", where.endswith(":5"),
          f"where={where}")


# ------------------------------------------------------------ structural ----
def t_structural():
    rf = rules_file(GOOD_RULES)

    doc = tmpfile("Alpha " + "word " * 40 + "ends.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-STRUCT-01 over-long sentence",
          "sentence_length" in kinds_of(rep), f"kinds={set(kinds_of(rep))}")

    # the band under the limit: reported, and reported as info
    doc = tmpfile("Alpha " + "word " * 30 + "ends.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    near = [h for h in ((rep["warn"] + rep["info"]) if rep else [])
            if h["kind"] == "sentence_near_limit"]
    check("TC-STRUCT-04 sentence just under the limit is reported at info",
          len(near) == 1 and near[0]["severity"] == "info"
          and "sentence_length" not in kinds_of(rep),
          f"near={len(near)} kinds={set(kinds_of(rep))}")

    wide = "x" * 130
    doc = tmpfile(f"| a | b |\n| --- | --- |\n| {wide} | ok |\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-STRUCT-02 over-wide table cell",
          "cell_width" in kinds_of(rep), f"kinds={set(kinds_of(rep))}")

    # prose in a cell: multi-sentence AND long enough to be prose
    prose_cell = ("Первое утверждение занимает половину ячейки целиком. "
                  "Второе утверждение занимает вторую половину ячейки. ")
    doc = tmpfile(f"| a | b |\n| --- | --- |\n| {prose_cell} | ok |\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    hit = next((h for h in ((rep["warn"] + rep["info"]) if rep else [])
                if h["kind"] == "cell_sentences"), None)
    check("TC-STRUCT-05 prose in a cell is a warn (documentation-standards 5.1)",
          hit and hit["severity"] == "warn", f"hit={hit and hit['severity']}")

    # the control: two terse labels satisfy the width limit and are the
    # author's judgement, not the prose-in-a-cell defect §5.1 names
    doc = tmpfile("| a | b |\n| --- | --- |\n| Improved. No rule. | ok |\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    hit = next((h for h in ((rep["warn"] + rep["info"]) if rep else [])
                if h["kind"] == "cell_sentences"), None)
    check("TC-STRUCT-05a control: a short two-label cell is info, not warn",
          hit and hit["severity"] == "info", f"hit={hit and hit['severity']}")

    doc = tmpfile("\U0001F534 **Critical:** do the thing.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    emoji = [h for h in ((rep["warn"] + rep["info"]) if rep else [])
             if h["kind"] == "emoji_severity"]
    check("TC-STRUCT-03 emoji as severity is a WARN, not info",
          len(emoji) == 1 and emoji[0]["severity"] == "warn"
          and emoji[0]["rule"] == 5,
          f"emoji={[(e['severity'], e['rule']) for e in emoji]}")

    # ✓/✗ are table values in this repository and must stay silent
    doc = tmpfile("| a | b |\n| --- | --- |\n| ✓ | ✗ |\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-STRUCT-06 check marks are values, not severities",
          "emoji_severity" not in kinds_of(rep), f"kinds={set(kinds_of(rep))}")

    # the defect that invalidated the first TASK 096 measurement
    checklist = "".join(f"- [ ] {'word ' * 12}criterion {i}\n" for i in range(8))
    doc = tmpfile(checklist)
    code, rep, _ = scan_json([doc], ["--rules", rf])
    lens = [h for h in ((rep["warn"] + rep["info"]) if rep else [])
            if h["kind"] == "sentence_length"]
    check("TC-REG-01 checklist lines are not glued into one sentence",
          code == 0 and not lens,
          f"sentence_length hits={len(lens)} (expected 0)")

    # emphasis-labelled sentences must not glue either (found scanning TASK 096)
    uc = ("**UC-1 — Analyst drafts a TASK.**\n"
          "*Actor:* Analyst. *Precondition:* the prompt carries the rules.\n"
          "*Main:* the author writes requirements in the language of their "
          "choice, and the artifact conforms.\n"
          "*Postcondition:* register no longer depends on memory.\n")
    doc = tmpfile(uc)
    code, rep, _ = scan_json([doc], ["--rules", rf])
    lens = [h for h in ((rep["warn"] + rep["info"]) if rep else [])
            if h["kind"] == "sentence_length"]
    check("TC-REG-03 emphasis-labelled sentences are split, not glued",
          code == 0 and not lens,
          f"sentence_length hits={len(lens)} (expected 0)")


# ---------------------------------------------------------------- lexical ----
def t_lexical():
    rf = rules_file(GOOD_RULES)
    doc = tmpfile("This is obviously wrong.\n\nIt runs exactly once.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-LEX-01 warn marker reported",
          rep and rep["counts"]["warn"] == 1, f"rep={rep and rep['counts']}")
    check("TC-LEX-02 info marker reported at info",
          rep and rep["counts"]["info"] >= 1, f"rep={rep and rep['counts']}")
    # Naming the rule is not enough: the number and the section string must
    # agree with what the entry declared. `all("rule" in h)` was guaranteed by
    # `add()` and could not fail.
    hits = (rep["warn"] + rep["info"]) if rep else []
    check("TC-LEX-03 a finding carries the rule its entry declared",
          hits and all(h["rule"] == 2 and h["standard"].endswith("rule 2")
                       for h in hits if h["kind"] == "marker"),
          f"seen={[(h['kind'], h['rule'], h['standard']) for h in hits]}")

    # rule number selects the finding kind, with no scanner edit
    doc = tmpfile("The gate blesses the number.\n")
    rf4 = rules_file(entry_rules(
        {"marker": "blesses", "pattern": r"\bblesses\b", "guidance": "g",
         "probe": "The gate blesses it.", "rule": 4}))
    code, rep, _ = scan_json([doc], ["--rules", rf4])
    check("TC-LEX-04 rule 4 entries report as `maxim`",
          "maxim" in kinds_of(rep), f"kinds={set(kinds_of(rep))}")

    doc = tmpfile("The injection widget is built here.\n")
    rf6 = rules_file(entry_rules(
        {"marker": "widget", "pattern": r"\bwidget\b", "guidance": "g",
         "probe": "The widget is built.", "rule": 6}))
    code, rep, _ = scan_json([doc], ["--rules", rf6])
    check("TC-LEX-05 rule 6 entries report as `metaphor`",
          "metaphor" in kinds_of(rep), f"kinds={set(kinds_of(rep))}")


# --------------------------------------------------------------- rule 3 ----
def t_reasoning():
    doc = json.loads(json.dumps(GOOD_RULES))
    doc["languages"]["en"]["reasoning"] = {
        "modals": [r"\bmust\b"], "causals": [r"\bbecause\b"],
        "probe": "The field must be set, because the reader cannot derive it."}
    rf = rules_file(doc)

    src = tmpfile("The field must be set, because the reader cannot derive "
                  "it.\n")
    code, rep, _ = scan_json([src], ["--rules", rf])
    hits = [h for h in ((rep["warn"] + rep["info"]) if rep else [])
            if h["kind"] == "reasoning"]
    check("TC-R3-01 obligation and justification in one sentence is reported",
          len(hits) == 1 and hits[0]["severity"] == "info"
          and hits[0]["rule"] == 3, f"hits={len(hits)}")

    # the control: the SAME content, split as the rule prescribes, is silent
    src = tmpfile("The field must be set.\n\n**Why.** The reader cannot "
                  "derive it.\n")
    code, rep, _ = scan_json([src], ["--rules", rf])
    check("TC-R3-02 control: split into requirement + Why is silent",
          "reasoning" not in kinds_of(rep), f"kinds={set(kinds_of(rep))}")

    # a causal with no obligation is prose, not a braided requirement
    src = tmpfile("The counter is stale because the set grew.\n")
    code, rep, _ = scan_json([src], ["--rules", rf])
    check("TC-R3-03 control: a causal without an obligation is silent",
          "reasoning" not in kinds_of(rep), f"kinds={set(kinds_of(rep))}")


# ----------------------------------------------------------------- probe ----
def t_probe():
    code, out, _ = run(["--probe"])
    check("TC-PROBE-01 shipped detectors are all live", code == 0 and
          "DEAD" not in out, f"exit={code}")

    code, out, _ = run(["--probe", "--json"])
    try:
        rep = json.loads(out)
    except ValueError:
        rep = None
    # `>= 16` against a shipped 18 stayed green after deleting every rule-6
    # entry of one language. The expected count is derived from the data.
    expected = 0
    for lang in ("en", "ru"):
        doc = json.load(open(os.path.join(SKILL, "data", f"register-{lang}.json"),
                             encoding="utf-8"))
        rules = {e.get("rule", 2) for c in doc["languages"][lang]["categories"]
                 for e in c["entries"]}
        expected += 5 + len(rules) + (1 if doc["languages"][lang].get("reasoning")
                                      else 0)
    check("TC-PROBE-02 --probe --json reports exactly the shipped detectors",
          code == 0 and rep and rep["ok"] and len(rep["probes"]) == expected,
          f"exit={code} n={rep and len(rep['probes'])} expected={expected}")

    # a threshold that disables a detector is a DEAD detector, not a clean run
    doc = json.loads(json.dumps(GOOD_RULES))
    doc["thresholds"]["cell_max_sentences"] = 99
    rf = rules_file(doc)
    code, out, _ = run(["--probe", "--rules", rf])
    check("TC-PROBE-03 a disabled detector is reported DEAD and exits 2",
          code == 2 and "DEAD" in out, f"exit={code}")

    src = tmpfile("Ordinary prose here.\n")
    code, rep, err = scan_json([src], ["--rules", rf])
    check("TC-PROBE-04 a scan with a dead detector exits 2, not 0",
          code == 2 and rep and rep["dead_detectors"],
          f"exit={code} dead={rep and rep['dead_detectors']}")

    code, rep, _ = scan_json([src])
    check("TC-PROBE-05 an ordinary scan carries its probe results",
          code == 0 and rep and rep["detectors"]
          and all(d["live"] for d in rep["detectors"]), "")


# ----------------------------------------------------------- diagnostics ----
def t_diagnostics():
    rf = rules_file(GOOD_RULES)
    # a distribution that stops exactly at the limit must be named as such
    src = tmpfile("Alpha " + "word " * 33 + "ends.\n")
    code, rep, _ = scan_json([src], ["--rules", rf])
    d = rep["diagnostics"][src] if rep else {}
    check("TC-DIAG-01 pressure against the limit is reported",
          code == 0 and rep["counts"]["warn"] == 0 and d.get("sentence_pressure")
          and d.get("sentence_max_observed") == 35,
          f"warn={rep and rep['counts']['warn']} diag={d.get('sentence_pressure')}"
          f" max={d.get('sentence_max_observed')}")

    _, out, _ = run([src, "--rules", rf])
    check("TC-DIAG-02 the text report names the pressure in words",
          "PRESSED AGAINST THE LIMIT" in out, out[-160:])

    src = tmpfile("Short prose here.\n")
    code, rep, _ = scan_json([src], ["--rules", rf])
    d = rep["diagnostics"][src] if rep else {}
    check("TC-DIAG-03 a genuine zero reports what the detector saw",
          code == 0 and d.get("sentences") == 1
          and not d.get("sentence_pressure")
          and d.get("lexicon_entries") == 2,
          f"diag={d}")


# -------------------------------------------------------------- sections ----
def t_sections():
    rf = rules_file(GOOD_RULES)
    body = ("# Title\n\nPreface line.\n\n## Alpha\n\nThis is obviously wrong.\n"
            "\n## Beta\n\nA clean sentence.\n")
    src = tmpfile(body)
    code, rep, _ = scan_json([src], ["--rules", rf, "--sections"])
    rows = rep["sections"][src] if rep else []
    titles = [r["title"] for r in rows]
    alpha = next((r for r in rows if r["title"] == "Alpha"), None)
    beta = next((r for r in rows if r["title"] == "Beta"), None)
    check("TC-SEC-01 every section is enumerated, findings or not",
          "Alpha" in titles and "Beta" in titles, f"titles={titles}")
    check("TC-SEC-02 findings are attributed to their section",
          alpha and alpha["warn"] == 1 and beta and beta["warn"] == 0,
          f"alpha={alpha} beta={beta}")


# ----------------------------------------------------------------- terms ----
def t_terms():
    entry = {"marker": "widget", "pattern": r"\bwidget\b", "guidance": "g",
             "probe": "The widget is built.", "rule": 6, "severity": "warn"}
    rf = rules_file(entry_rules(entry))
    src = tmpfile("The widget is constructed at startup.\n")

    code, rep, _ = scan_json([src], ["--rules", rf])
    check("TC-TERM-01 an undeclared metaphor is a warn",
          code == 0 and rep and rep["counts"]["warn"] == 1,
          f"counts={rep and rep['counts']}")

    arch = tmpfile("# Architecture\n\nThe widget is the unit of scheduling.\n")
    code, rep, _ = scan_json([src], ["--rules", rf, "--terms", arch])
    hit = (rep["info"][0] if rep and rep["info"] else {})
    check("TC-TERM-02 a term declared in the sources is downgraded, not hidden",
          code == 0 and rep["counts"]["warn"] == 0
          and rep["counts"]["info"] == 1
          and "declared term sources" in hit.get("guidance", ""),
          f"counts={rep and rep['counts']}")

    code, _, err = run([src, "--rules", rf, "--terms",
                        os.path.join(SKILL, "no-such-file.md"), "--json"])
    check("TC-TERM-03 an unreadable term source exits 2", code == 2,
          f"exit={code} err={err.strip()[:80]}")


# --------------------------------------------------------------- language ----
def t_language():
    doc_ru = tmpfile("Это очевидно неверный регистр записи требования.\n")
    code, rep, _ = scan_json([doc_ru])
    check("TC-LANG-01 cyrillic resolves ru and reports",
          code == 0 and rep and rep["counts"]["warn"] >= 1,
          f"exit={code} counts={rep and rep['counts']}")

    doc_en = tmpfile("This is obviously the wrong register.\n")
    code, rep, _ = scan_json([doc_en])
    check("TC-LANG-02 latin resolves en and reports",
          code == 0 and rep and rep["counts"]["warn"] >= 1,
          f"exit={code} counts={rep and rep['counts']}")

    # a language with no rule file: structural still runs, lexical is zero,
    # and the scanner SAYS so rather than looking clean
    doc_de = tmpfile("Dies ist " + "wort " * 40 + "ende.\n")
    code, rep, err = scan_json([doc_de], ["--lang", "de"])
    check("TC-LANG-03 unknown language: structural runs, lexicon absent noted",
          code == 0 and "sentence_length" in kinds_of(rep) and "de" in err,
          f"exit={code} kinds={set(kinds_of(rep))} err={err.strip()[:80]}")


# ------------------------------------------------------------------ exits ----
def t_exits():
    rf = rules_file(GOOD_RULES)
    body = ("This is obviously wrong. " + "word " * 45 + ".\n"
            "| " + "y" * 130 + " |\n")
    doc = tmpfile(body)
    code, rep, _ = scan_json([doc], ["--rules", rf])
    total = (rep["counts"]["warn"] + rep["counts"]["info"]) if rep else 0
    check("TC-EXIT-01 findings never change the exit code",
          code == 0 and total > 0, f"exit={code} findings={total}")

    rf_bad = tmpfile("{not json", ".json")
    code, _, _ = run([doc, "--rules", rf_bad, "--json"])
    check("TC-EXIT-02 malformed rules exit 2", code == 2, f"exit={code}")

    code, _, _ = run([os.path.join(SKILL, "does-not-exist.md"), "--json"])
    check("TC-EXIT-03 unreadable input exits 2", code == 2, f"exit={code}")


# ------------------------------------------------------------------- data ----
def t_data_extensibility():
    """R7: a new marker must need no code edit."""
    custom = json.loads(json.dumps(GOOD_RULES))
    custom["languages"]["en"]["categories"][0]["entries"].append(
        {"marker": "frobnicate", "pattern": r"\bfrobnicate\b",
         "severity": "warn", "guidance": "invented for this test",
         "probe": "We frobnicate the pipeline."})
    rf = rules_file(custom)
    doc = tmpfile("We frobnicate the pipeline.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-DATA-01 new marker works with no scanner edit",
          code == 0 and rep and rep["counts"]["warn"] == 1,
          f"counts={rep and rep['counts']}")
    # The previous form compared the scanner's bytes before and after a test
    # that never opens it for writing -- it passed against any implementation,
    # including a stub. What R7 actually claims is that the marker lives ONLY
    # in data.
    blob = open(SCANNER, "rb").read()
    check("TC-DATA-02 the marker exists nowhere in the scanner source",
          b"frobnicate" not in blob, "R7: vocabulary is data, not code")


# -------------------------------------------------------- shipped rulesets ----
def t_shipped():
    for lang in ("en", "ru"):
        path = os.path.join(SKILL, "data", f"register-{lang}.json")
        check(f"TC-SHIP-01 {lang} rule file present", os.path.exists(path), path)
        if not os.path.exists(path):
            continue
        doc = json.load(open(path, encoding="utf-8"))
        check(f"TC-SHIP-02 {lang} threshold is 35 words",
              doc.get("thresholds", {}).get("sentence_max_words") == 35,
              str(doc.get("thresholds")))
        rules = [e.get("rule", 2)
                 for c in doc["languages"][lang]["categories"]
                 for e in c["entries"]]
        check(f"TC-SHIP-04 {lang} ships detectors for rules 2, 4 and 6",
              {2, 4, 6} <= set(rules), f"rules present={sorted(set(rules))}")
        check(f"TC-SHIP-05 {lang} declares a rule-3 vocabulary",
              bool(doc["languages"][lang].get("reasoning")), "")

    code, out, err = run(["--list"])
    check("TC-SHIP-03 --list renders the shipped rules",
          code == 0 and "obviously" in out and "очевидно" in out,
          f"exit={code}")

    # the skill's own reference must survive its own scanner
    # Asserting exit 0 alone could only fail on a dead detector. The claim
    # worth pinning is that the skill's own documents conform to the skill.
    own = sorted(glob.glob(os.path.join(SKILL, "references", "*.md"))) + \
        [os.path.join(SKILL, "SKILL.md")]
    code, rep, _ = scan_json(own)
    check("TC-SHIP-06 the skill's own documents scan at zero warn",
          code == 0 and rep and rep["counts"]["warn"] == 0,
          f"exit={code} warn={rep and rep['counts']['warn']} "
          f"{sorted({(h['kind'], h['where']) for h in (rep['warn'] if rep else [])})}")


def t_false_positives():
    """Shipped-lexicon controls: the words that must NOT fire."""
    doc = tmpfile("Простой случай: таблица прост. и ясна.\n")
    code, rep, _ = scan_json([doc])
    check("TC-FP-01 'простой'/'прост.' do not match 'просто'",
          code == 0 and rep and rep["counts"]["info"] == 0,
          f"counts={rep and rep['counts']} kinds={set(kinds_of(rep))}")

    doc = tmpfile("The value is read in `exactly` one place.\n")
    code, rep, _ = scan_json([doc])
    check("TC-FP-02 marker inside a code span is silent",
          code == 0 and rep and rep["counts"]["info"] == 0,
          f"counts={rep and rep['counts']}")

    # the git ref, not the metaphor: the one case-sensitive entry
    doc = tmpfile("Validate the anchors by grep at HEAD before merging.\n")
    code, rep, _ = scan_json([doc])
    check("TC-FP-03 the git ref HEAD is not the head/tail metaphor",
          code == 0 and "metaphor" not in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    # Red-Green-Refactor is terminology; only the verb forms are personification
    doc = tmpfile("Фаза 1 оставляет красный тест и зелёный прогон.\n")
    code, rep, _ = scan_json([doc])
    check("TC-FP-04 'красный тест' is TDD terminology, not personification",
          code == 0 and "maxim" not in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")


def t_precision():
    """Regression pins for the WI-11 precision findings.

    Every one was reproduced by execution before it was fixed, and two
    reported findings were REFUTED the same way — those are pinned too, so a
    later 'fix' for them turns the battery red instead of silently making the
    scanner wrong.
    """
    LS = chr(0x2028)

    # --- confirmed and fixed ---
    doc = tmpfile("| a | " + "x" * 100 + r"\|" + "x" * 100 + " |\n")
    code, rep, _ = scan_json([doc])
    check("TC-PREC-01 escaped pipe does not hide an over-wide cell",
          code == 0 and "cell_width" in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    doc = tmpfile("para" + LS + "one\n\n| a | " + "x" * 200 + " |\n")
    code, rep, _ = scan_json([doc])
    got = next((f["where"].rsplit(":", 1)[-1]
                for f in (rep["warn"] + rep["info"]) if rep), "?")
    check("TC-PREC-02 U+2028 does not shift the reported line number",
          got == "3", f"reported line {got}, real \\n-line 3")

    rules = os.path.join(SKILL, "data", "register-en.json")
    doc = tmpfile("It is obviously simple.\n")
    _, one, _ = scan_json([doc], ["--rules", rules])
    _, two, _ = scan_json([doc], ["--rules", rules, "--rules", rules])
    check("TC-PREC-03 the same rule file twice does not double-count",
          one and two and one["counts"] == two["counts"],
          f"{one and one['counts']} vs {two and two['counts']}")

    doc = tmpfile("---\n\n# Title\n\nThis block " + "word " * 40 +
                  "should be scanned.\n\n---\n")
    code, rep, _ = scan_json([doc])
    check("TC-PREC-04 a leading horizontal rule is not eaten as frontmatter",
          code == 0 and "sentence_length" in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    doc = tmpfile("---\nname: x\ntier: 2\n---\n\nShort prose.\n")
    code, rep, _ = scan_json([doc])
    check("TC-PREC-05 real frontmatter is still masked",
          code == 0 and rep and rep["counts"]["warn"] == 0,
          f"counts={rep and rep['counts']}")

    # These three fixtures are built so that EACH half is under the 35-word
    # limit and the whole is over it. A fixture whose second half alone
    # exceeds the limit reports a finding either way and discriminates nothing
    # -- the first draft of these pins had exactly that defect.
    def halves(mid):
        return "alpha " * 18 + mid + "beta " * 17 + "ends.\n"

    doc = tmpfile(halves("e.g. Foo "))
    code, rep, _ = scan_json([doc])
    check("TC-PREC-06 'e.g. Capital' is not a sentence boundary",
          code == 0 and "sentence_length" in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    # --- refuted, and pinned as non-defects ---
    doc = tmpfile(halves("1.5 Foo "))
    code, rep, _ = scan_json([doc])
    check("TC-PREC-07 a decimal never split a sentence (refuted finding)",
          code == 0 and "sentence_length" in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    bt = chr(96)
    doc = tmpfile(f"use {bt} an unmatched backtick and then obviously done\n")
    code, rep, _ = scan_json([doc])
    check("TC-PREC-08 an unmatched backtick masks nothing (refuted finding)",
          code == 0 and rep and rep["counts"]["warn"] >= 1,
          f"counts={rep and rep['counts']}")

    doc = tmpfile(halves("etc. Foo "))
    code, rep, _ = scan_json([doc])
    check("TC-PREC-09 'etc.' still ends a sentence (deliberately not exempt)",
          code == 0 and "sentence_length" not in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")



# ------------------------------------------- adversarial-review regressions ----
def t_masking_gaps():
    """Every masking path the WI-096 adversarial pass found leaking."""
    rf = rules_file(GOOD_RULES)

    doc = tmpfile("The word ``obviously`` is quoted.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-01 a double-backtick code span is masked",
          code == 0 and rep["counts"]["warn"] == 0,
          f"counts={rep and rep['counts']}")

    doc = tmpfile("use `obviously\nquoted` here\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-02 a code span crossing a line break is masked",
          code == 0 and rep["counts"]["warn"] == 0,
          f"counts={rep and rep['counts']}")

    doc = tmpfile("text\n\n```\nobviously\nnever closed\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-03 an unterminated fence runs to EOF",
          code == 0 and rep["counts"]["warn"] == 0,
          f"counts={rep and rep['counts']}")

    doc = tmpfile("text\n\n~~~\nobviously\n~~~\n\ntail\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-04 a tilde fence is masked",
          code == 0 and rep["counts"]["warn"] == 0,
          f"counts={rep and rep['counts']}")

    # a `---` opener with content on the next line is a thematic break around a
    # paragraph, not frontmatter, and its prose stays scanned
    doc = tmpfile("---\nThis is obviously wrong and the register is bad.\n"
                  "---\n\n# Title\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-05 prose between two rules is not eaten as frontmatter",
          code == 0 and rep["counts"]["warn"] == 1,
          f"counts={rep and rep['counts']}")

    doc = tmpfile("---\r\nname: x\r\ntier: 2\r\n---\r\n\r\nShort.\r\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-06 CRLF input does not crash the scan",
          code == 0 and rep is not None, f"exit={code}")

    # NFC: a decomposed cyrillic yo must match a pattern spelling the composed
    # one. Written as escapes so the fixture cannot silently become a latin `e`.
    doc = tmpfile("\u0414\u0435\u0434\u043b\u0430\u0439\u043d "
                  "\u0431\u044c\u0435\u0308\u0442 \u043f\u043e "
                  "\u0432\u044b\u0437\u043e\u0432\u0430\u043c.\n")
    code, rep, _ = scan_json([doc])
    check("TC-ADV-07 decomposed cyrillic is normalised before matching",
          code == 0 and "maxim" in kinds_of(rep), f"kinds={set(kinds_of(rep))}")

    # closing punctuation before the boundary must still end the sentence
    doc = tmpfile("«" + "слово " * 20 + "нет.» " + "Далее " + "слово " * 20
                  + "конец.\n")
    code, rep, _ = scan_json([doc])
    check("TC-ADV-08 a closing quote does not glue two sentences",
          code == 0 and "sentence_length" not in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")


def t_detector_gaps():
    rf = rules_file(GOOD_RULES)

    for name, glyph in (("TC-ADV-09 U+26D4 is a severity glyph", "\u26D4"),
                        ("TC-ADV-10 U+2714 is a severity glyph", "\u2714"),
                        ("TC-ADV-11 U+203C is a severity glyph", "\u203C")):
        doc = tmpfile(f"{glyph} Critical: the thing.\n")
        code, rep, _ = scan_json([doc], ["--rules", rf])
        check(name, code == 0 and "emoji_severity" in kinds_of(rep),
              f"kinds={set(kinds_of(rep))}")

    doc = tmpfile("| a | b |\n| --- | --- |\n| \u2705 | \u274C |\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-12 a status glyph in a table cell is a value, not a severity",
          code == 0 and "emoji_severity" not in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    doc = tmpfile("\u2705 The migration is done.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-13 the same glyph in PROSE is still reported",
          code == 0 and "emoji_severity" in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    doc = tmpfile("\U0001F44D\U0001F3FD ok\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    n = sum(1 for h in rep["warn"] if h["kind"] == "emoji_severity")
    check("TC-ADV-14 a skin-tone sequence is one finding, not two", n == 1,
          f"findings={n}")

    doc = tmpfile("> [!TIP]\n> " + "word " * 40 + "ends.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-15 blockquote prose reaches rule 1",
          code == 0 and "sentence_length" in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    doc = tmpfile("Col A | Col B\n--- | ---\n" + "x" * 130 + " | ok\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-16 a GFM table without leading pipes is a table",
          code == 0 and "cell_width" in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    doc = tmpfile("short one.\nshort two.\nshort three.\n"
                  + "word " * 40 + "ends.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    line = rep["warn"][0]["where"].rsplit(":", 1)[1] if rep["warn"] else "?"
    check("TC-ADV-17 a finding is attributed to the line that carries it",
          line == "4", f"reported line {line}, real line 4")

    doc = tmpfile("# One\n\ntext\n\n## Two\n\ntext\n")
    code, rep, _ = scan_json([doc], ["--rules", rf, "--sections"])
    rows = rep["sections"][doc] if rep else []
    check("TC-ADV-18 the last section ends on the last real line",
          [r["lines"] for r in rows] == ["1-4", "5-7"],
          f"{[r['lines'] for r in rows]}")

    doc = tmpfile("6. \U0001F534 Emoji severity\n\ntext\n")
    code, rep, _ = scan_json([doc], ["--rules", rf, "--sections"])
    check("TC-ADV-19 a section title keeps its glyphs in the worklist",
          code == 0, f"exit={code}")


def t_contract_gaps():
    rf = rules_file(GOOD_RULES)

    # --terms must match whole words: `legacy` is not a declaration of `leg`
    entry = {"marker": "leg", "pattern": r"\blegs?\b", "guidance": "g",
             "probe": "The paid leg runs.", "rule": 6, "severity": "warn"}
    rf6 = rules_file(entry_rules(entry))
    src = tmpfile("The paid leg runs to completion.\n")
    near = tmpfile("# Arch\n\nWe delegate to the legacy resolver.\n")
    exact = tmpfile("# Arch\n\nA leg is a sub-call.\n")
    code, rep, _ = scan_json([src], ["--rules", rf6, "--terms", near])
    check("TC-ADV-20 a substring in the term sources does NOT downgrade",
          code == 0 and rep["counts"]["warn"] == 1,
          f"counts={rep and rep['counts']}")
    code, rep, _ = scan_json([src], ["--rules", rf6, "--terms", exact])
    check("TC-ADV-21 control: a whole-word term DOES downgrade",
          code == 0 and rep["counts"]["info"] == 1
          and rep["diagnostics"][src]["terms_downgrades"] == 1,
          f"counts={rep and rep['counts']}")

    binary = tmpfile("", ".bin")
    with open(binary, "wb") as f:
        f.write(bytes(range(256)))
    code, _, err = run([src, "--rules", rf6, "--terms", binary, "--json"])
    check("TC-ADV-22 an undecodable term source exits 2, never 1",
          code == 2 and "term_errors" in err, f"exit={code}")

    # a Russian document wrapping a large English code fence stays Russian
    ru = tmpfile("Это очевидно неверный регистр.\n\n```ts\n"
                 + "\n".join(f"const someVariableName{i} = compute();"
                              for i in range(60)) + "\n```\n")
    code, rep, _ = scan_json([ru])
    check("TC-ADV-23 language is resolved on masked text, not raw",
          code == 0 and rep["diagnostics"][ru]["language"] == "ru"
          and rep["counts"]["warn"] >= 1,
          f"lang={rep and rep['diagnostics'][ru]['language']}")

    # the share and its denominator must be the same number
    body = ("Prose line here.\n\n```\n"
            + "\n".join(f"code_{i} = 1" for i in range(40)) + "\n```\n")
    doc = tmpfile(body)
    code, rep, _ = scan_json([doc], ["--rules", rf])
    d = rep["diagnostics"][doc]
    check("TC-ADV-24 the prose share states its own denominator",
          d["prose_lines"] == 1 and d["nonblank_lines"] == 43
          and d["prose_share_of_nonblank"] == 2,
          f"prose={d['prose_lines']} nonblank={d['nonblank_lines']} "
          f"share={d['prose_share_of_nonblank']}%")

    code, rep, _ = scan_json([src, src], ["--rules", rf6])
    check("TC-ADV-25 a repeated input path is scanned once",
          code == 0 and rep["counts"]["warn"] == 1
          and len(rep["diagnostics"]) == 1,
          f"counts={rep and rep['counts']} diag={len(rep['diagnostics'])}")

    code, rep, _ = scan_json([src], ["--rules", rf6])
    check("TC-ADV-26 detector rows name their language",
          all("lang" in d for d in rep["detectors"]), "")


def t_exit_contract():
    src = tmpfile("Ordinary prose.\n")
    code, _, err = run(["--sectons", src])
    check("TC-ADV-27 a usage error exits 3, not 2",
          code == 3 and "usage error" in err, f"exit={code}")

    code, _, _ = run(["--probe", "--terms", "/nonexistent-terms.md"])
    check("TC-ADV-28 --probe still validates --terms", code == 2,
          f"exit={code}")

    code, _, err = run(["--probe", "--list"])
    check("TC-ADV-29 --probe and --list are mutually exclusive",
          code == 3 and "mutually exclusive" in err, f"exit={code}")

    code, _, err = run(["--list", "zz"])
    check("TC-ADV-30 --list for an unknown language is a usage error",
          code == 3 and "no rules for language" in err, f"exit={code}")

    # a threshold invariant must not be evadable by splitting the keys
    a = {"schema": "register-rules/v1",
         "thresholds": {"sentence_near_words": 30},
         "languages": GOOD_RULES["languages"]}
    b = {"schema": "register-rules/v1",
         "thresholds": {"sentence_max_words": 20},
         "languages": GOOD_RULES["languages"]}
    code, _, err = run([src, "--rules", rules_file(a), "--rules",
                        rules_file(b), "--json"])
    check("TC-ADV-31 threshold invariants run on the merged configuration",
          code == 2 and "merged thresholds" in err, f"exit={code}")

    dup = tmpfile('{"schema":"register-rules/v1","thresholds":'
                  '{"sentence_max_words":35,"sentence_max_words":10},'
                  '"languages":{}}', ".json")
    code, _, err = run([src, "--rules", dup, "--json"])
    check("TC-ADV-32 a duplicate key in one rule file is rejected",
          code == 2 and "duplicate key" in err, f"exit={code}")


def t_rule_authoring_gaps():
    src = tmpfile("Ordinary prose.\n")

    code, _, err = run([src, "--rules", rules_file(entry_rules(
        {"marker": "x", "pattern": r"\bzzz\b", "guidance": "g",
         "probe": "zzz", "rule": 3})), "--json"])
    check("TC-ADV-33 a lexicon entry may not claim rule 3",
          code == 2 and "rule 3 is structural" in err, f"exit={code}")

    code, _, err = run([src, "--rules", rules_file(entry_rules(
        {"marker": "zw", "pattern": "(?=obvious)", "guidance": "g",
         "probe": "obviously"})), "--json"])
    check("TC-ADV-34 a zero-width pattern is rejected at load, not at probe",
          code == 2 and "zero-width" in err, f"exit={code}")

    code, _, err = run([src, "--rules", rules_file(entry_rules(
        {"marker": "redos", "pattern": r"\b(\w+\s?)+ing\b", "guidance": "g",
         "probe": "testing"})), "--json"])
    check("TC-ADV-35 a catastrophically backtracking pattern is rejected",
          code == 2 and "catastrophic" in err, f"exit={code}")

    for name, modal in (("TC-ADV-36 a rule-3 modal matching a word boundary",
                         r"\b"),
                        ("TC-ADV-37 a rule-3 modal matching any word", r"\w*")):
        d = json.loads(json.dumps(GOOD_RULES))
        d["languages"]["en"]["reasoning"] = {
            "modals": [modal], "causals": [r"\bbecause\b"],
            "probe": "x must be set because y"}
        code, _, err = run([src, "--rules", rules_file(d), "--json"])
        check(name + " is rejected",
              code == 2 and "carrying neither" in err, f"exit={code}")

    d = json.loads(json.dumps(GOOD_RULES))
    d["languages"]["en"]["reasoning"] = {
        "modals": [r"\bmust\b"], "causals": [r"\bbecause\b"],
        "probe": "The field `must` be set, because the reader cannot."}
    code, _, err = run([src, "--rules", rules_file(d), "--json"])
    check("TC-ADV-38 a rule-3 probe hidden in a code span is rejected",
          code == 2 and "masked construct" in err, f"exit={code}")


def t_reporting_gaps():
    rf = rules_file(GOOD_RULES)

    # cell shape belongs to §5.1 and must not be reported as a §5.5 rule
    doc = tmpfile("| a | b |\n| --- | --- |\n| " + "x" * 130 + " | ok |\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    hit = next(h for h in rep["warn"] if h["kind"] == "cell_width")
    check("TC-ADV-39 cell shape is reported under §5.1, not a §5.5 rule",
          hit["rule"] == 0 and hit["standard"].endswith("§5.1"),
          f"rule={hit['rule']} standard={hit['standard']}")

    # the warn/info boundary for a multi-sentence cell is its own threshold
    d = json.loads(json.dumps(GOOD_RULES))
    d["thresholds"]["cell_prose_chars"] = 40
    rfp = rules_file(d)
    short = "Ab. Cd."
    long_ = "A" * 30 + ". " + "B" * 20 + "."
    doc = tmpfile(f"| a | b |\n| --- | --- |\n| {short} | {long_} |\n")
    code, rep, _ = scan_json([doc], ["--rules", rfp])
    sevs = sorted(h["severity"] for h in rep["warn"] + rep["info"]
                  if h["kind"] == "cell_sentences")
    check("TC-ADV-40 the cell prose boundary is its own named threshold",
          sevs == ["info", "warn"], f"severities={sevs}")

    # the pressure band edges
    d = json.loads(json.dumps(GOOD_RULES))
    d["thresholds"]["sentence_pressure_band"] = 2
    rfb = rules_file(d)
    for words, want in ((33, True), (32, False)):
        doc = tmpfile("Alpha " + "word " * (words - 2) + "ends.\n")
        code, rep, _ = scan_json([doc], ["--rules", rfb])
        got = rep["diagnostics"][doc]["sentence_pressure"]
        check(f"TC-ADV-4{1 if want else 2} pressure at {words} words is {want}",
              got is want,
              f"observed={rep['diagnostics'][doc]['sentence_max_observed']} "
              f"pressure={got}")

    # two entries covering the same phrase report it once
    d = json.loads(json.dumps(GOOD_RULES))
    d["languages"]["en"]["categories"][0]["entries"] = [
        {"marker": "wide", "pattern": r"not just \w+ but \w+", "guidance": "g",
         "probe": "not just a but b", "severity": "info"},
        {"marker": "narrow", "pattern": r"\bjust\b", "guidance": "g",
         "probe": "just so", "severity": "info"},
    ]
    doc = tmpfile("It is not just fast but correct.\n")
    code, rep, _ = scan_json([doc], ["--rules", rules_file(d)])
    check("TC-ADV-43 an overlapping span is reported once, widest wins",
          rep["counts"]["info"] == 1
          and rep["info"][0]["match"].startswith("not just"),
          f"info={[h['match'] for h in rep['info']]}")

    # --list must not emit a table its own §5.1 rule would reject
    d = json.loads(json.dumps(GOOD_RULES))
    d["languages"]["en"]["categories"][0]["entries"] = [
        {"marker": "a|b", "pattern": r"\bpipe\b", "guidance": "keep a|b",
         "probe": "pipe here"}]
    code, out, _ = run(["--list", "--rules", rules_file(d)])
    check("TC-ADV-44 --list escapes a pipe inside a marker",
          code == 0 and "a\\|b" in out, f"out={out[-90:]!r}")


def main():
    for fn in (t_schema, t_masking, t_structural, t_lexical, t_reasoning,
               t_probe, t_diagnostics, t_sections, t_terms, t_language,
               t_exits, t_data_extensibility, t_shipped, t_false_positives,
               t_precision, t_masking_gaps, t_detector_gaps,
               t_contract_gaps, t_exit_contract, t_rule_authoring_gaps,
               t_reporting_gaps):
        try:
            fn()
        except Exception as exc:                      # noqa: BLE001
            check(f"{fn.__name__} raised", False, f"{type(exc).__name__}: {exc}")

    failed = [r for r in RESULTS if not r[1]]
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL  {name}  — {detail}")
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed")
    if failed:
        print(f"{len(failed)} FAILING CASES:")
        for name, _, _ in failed:
            print(f"  · {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
