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
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCANNER = os.path.join(HERE, "scan_register.py")

# Every other case runs the scanner as a subprocess, which is what pins the
# EXIT CODES and the printed report. A frozenset and a defaults dict have no
# command-line surface, so the only way to assert their VALUE is to read the
# module. ARC-9 records the alternative: a case that asserted a schema literal
# against a test literal, named the dispatcher it was checking, and never
# imported it -- it stayed green when the dispatcher was reverted.
sys.path.insert(0, HERE)
import scan_register                                       # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []

#: Shipped vocabulary sizes, PINNED. Deriving them from the file under test
#: made the assertion agree with itself after any edit: deleting `of course`
#: from register-en.json left the whole battery green because both sides of the
#: comparison shrank together (REG-2).
SHIPPED_ENTRIES = {
    "en": {2: 28, 4: 9, 6: 5},
    "ru": {2: 22, 4: 10, 6: 6},
}
#: Shipped rule-3 vocabulary sizes, PINNED -- the same defect one structure
#: over. SHIPPED_ENTRIES counts CATEGORY entries, so it reaches rules 2, 4 and
#: 6 only, while the rule-3 patterns live in `languages.<lang>.reasoning` and
#: nothing pinned them. Measured: 21 of the 24 shipped patterns could each be
#: deleted with its `probes` key, leaving the battery green and `--probe` at
#: 18/18 with a real finding lost -- dropping `\bfor the reason that\b` took
#: `The installer shall abort for the reason that the target exists.` from one
#: finding to none. The probe row reprints the defect rather than catching it:
#: `N exercised of M patterns` derives both sides from the file under test
#: (REG-2, REG-3).
SHIPPED_REASONING = {
    "en": {"modals": 5, "causals": 6},
    "ru": {"modals": 6, "causals": 7},
}
#: 5 structural + marker + maxim + metaphor + reasoning, per shipped language.
SHIPPED_PROBES = 18

#: Shipped detection surfaces, PINNED BY IDENTITY. The counts above answer
#: "how many"; an entry REPLACED in place keeps the count, keeps matching its
#: own declared probe, and removes real detection with both gates at exit 0.
#: Measured: swapping the rule-2 `robust` pattern for `\bZZZNEVERWORD\b` and
#: moving its probe with it left the battery at `174/174` and the roster at
#: `18/18`, both exit 0, while `marker` findings over 636 documents fell from
#: 447 to 406; the same edit on the rule-3 causal `\bfor the reason that\b` took
#: `The installer shall abort for the reason that the target exists.` from one
#: finding to none (REG-14).
#:
#: `flags` rides in the tuple because it is half of what a pattern MATCHES, and
#: no roster check can hold it: a check keyed on the declared flag is switched
#: off by the edit that removes the flag. Dropping `"flags": "i"` from the 35
#: entries no case names cost 15 `marker` findings at `174/174` and `18/18`,
#: both exit 0 (REG-16). Rule 3 carries no flags -- `_scan_reasoning` compiles
#: its vocabulary with `IGNORECASE` unconditionally -- so its tuple is patterns.
SHIPPED_SURFACES = {
    "en": {
        2: (
            (r"\bof course\b", "i"),
            (r"\b(un)?obvious(ly)?\b", "i"),
            (r"\bmerely\b", "i"),
            (r"\bindeed\b", "i"),
            (r"\bit is worth noting\b", "i"),
            (r"\belegant\w*\b", "i"),
            (r"\bnothing more than\b", "i"),
            (r"\bwaste\b", "i"),
            (r"\bna(i|ï)ve(ly)?\b", "i"),
            (r"\b(trap|pitfall)s?\b", "i"),
            (r"\bunfortunately\b", "i"),
            (r"\b(the key insight|the whole point|the real question)\b", "i"),
            (r"\b(the|a|an|our|its|this)\s+(main|biggest|largest|primary|key|greatest|central)\s+(risk|problem|danger|challenge|question|idea|thing)\b", "i"),
            (r"\bsubtle(ty|ties)?\b", "i"),
            (r"\brobust\b", "i"),
            (r"\bseamless\w*\b", "i"),
            (r"\bcrucial\b", "i"),
            (r"\bpivotal\b", "i"),
            (r"\bcomprehensive\b", "i"),
            (r"\bleverag(e|es|ed|ing)\b", "i"),
            (r"\butiliz(e|es|ed|ing)\b", "i"),
            (r"\bdelv(e|es|ed|ing)\b", "i"),
            (r"\bunderscor(e|es|ed|ing)\b", "i"),
            (r"\bintricate\w*\b", "i"),
            (r"\bprecisely\b", "i"),
            (r"\bexactly\b", "i"),
            (r"\bsimply\b", "i"),
            (r"\bthe very\b", "i"),
        ),
        4: (
            (r"\b(can ?not|could ?n[o']t|will never) fail\b", "i"),
            (r"\b(proves|checks|verifies|asserts) nothing\b", "i"),
            (r"\b(always|forever|permanently) green\b", "i"),
            (r"\b(go(es|ing)?|went|gone|turn(s|ed|ing)?|flip(s|ped|ping)?)\s+(back\s+)?(red|green)\b", "i"),
            (r"\b(bless(es|ed)?|rubber-?stamps?)\b", "i"),
            (r"\bbit(e|es|ing)\b", "i"),
            (r"\b(outliv|outlast)(ed|es|ing)\b", "i"),
            (r"\b(strikes?|starv(e|es|ing)|punish(es|ing)?)\b", "i"),
            (r"\bsilent(ly)?\b", "i"),
        ),
        6: (
            (r"\bseams?\b", "i"),
            (r"\blegs?\b", "i"),
            (r"\bbeads?\b", "i"),
            (r"\b(head|tail)s?\b", ""),
            (r"\bin[- ]flight\b", "i"),
        ),
        3: (
            r"\bmust\b",
            r"\bshall\b",
            r"\bis required to\b",
            r"\bmay not\b",
            r"\bis forbidden\b",
            r"\bbecause\b",
            r"\bsince\b",
            r"\botherwise\b",
            r"\bfor the reason that\b",
            r"\bas a result of\b",
            r"\bwhich is why\b",
        ),
    },
    "ru": {
        2: (
            (r"\bразумеется\b", "i"),
            (r"\b(не)?очевид(н\w*|ен)\b", "i"),
            (r"\bпопросту\b", "i"),
            (r"\bна самом деле\b", "i"),
            (r"\bстоит отмети(ть|м)\b", "i"),
            (r"\bважно (понимать|помнить|отметить)\b", "i"),
            (r"\bэлегантн\w*\b", "i"),
            (r"\bчестн(о|ый|ая|ое|ые)\b", "i"),
            (r"\bнаив(н\w*|ен)\b", "i"),
            (r"\bловушк\w*\b", "i"),
            (r"\bковарн\w*\b", "i"),
            (r"\b(красив|изящн)\w*\b", "i"),
            (r"\b(к сожалению|увы)\b", "i"),
            (r"\bглавн(ая|ое|ый)\s+(опасность|проблема|риск|мысль|идея|сложность)\b", "i"),
            (r"\b(самое (важное|главное)|суть в том)\b", "i"),
            (r"\bтонк(ое место|ий момент|ость)\b", "i"),
            (r"\bбесшовн\w*\b", "i"),
            (r"\bкраеугольн\w*\b", "i"),
            (r"\bигра(ет|ют) ключев\w+ роль\b", "i"),
            (r"\bровно\b", "i"),
            (r"\bименно\b", "i"),
            (r"\bпросто\b", "i"),
        ),
        4: (
            (r"\bне мож(ет|но) провалиться\b", "i"),
            (r"\bничего не (провер|доказ)\w+", "i"),
            (r"\bвечно зел[её]н\w*\b", "i"),
            (r"\bснятие которого не рон\w+", "i"),
            (r"\b(по)?(красне|зелене)(ет|ют|л|ла|ло|ли|я|ть)\b|\bкраснит\b", "i"),
            (r"\bблагослов\w+", "i"),
            (r"\b(на укус|укус\w*|кусает\w*)\b", "i"),
            (r"\bпережи(л|ла|ло|ли|вш\w+)\b", "i"),
            (r"\b(бь[её]т|душ(ит|ат)|убива(ет|ют))\b", "i"),
            (r"\b(молч(а|ит|ат|аливо)|тих(ая|ий|ое|ую)\s+(ложь|правка|подмена|откат))\b", "i"),
        ),
        6: (
            (r"\b(шов|шв(ов|ы|а|е|у|ам|ами))\b", "i"),
            (r"\bбусин\w+", "i"),
            (r"\b(ног(а|и|у|ой|ах)|плеч(о|а|у|ом|и|ах))\b", "i"),
            (r"\bв пол[её]те\b", "i"),
            (r"\b(голов(а|ы|у|е|ой)|хвост\w*)\b", "i"),
            (r"\bмост(ик)?(ом|а|у|ы|ов|е)?\b", "i"),
        ),
        3: (
            r"\bобязан\w*\b",
            r"\bдолж(ен|на|но|ны)\b",
            r"\bнельзя\b",
            r"\bзапрещ(ён|ен|ена|ено|ены)\b",
            r"\bтребуется\b",
            r"\bне имеет права\b",
            r"\bпотому что\b",
            r"\bпоскольку\b",
            r"\bтак как\b",
            r"\bведь\b",
            r"\bиначе\b",
            r"\bоттого что\b",
            r"\bпо той причине\b",
        ),
    },
}

#: Thresholds, PINNED. `TC-SHIP-02` pinned `sentence_max_words` alone, and
#: `_structural_probes` builds every fixture FROM the active thresholds, so the
#: fixture moves with the value and cannot notice it: raising `cell_max_chars`
#: to 150 in both rule files cost 198 `cell_width` findings over 636 documents
#: with the battery at `174/174` and the roster at `18/18`, both exit 0
#: (REG-15). The band above ~200 was caught incidentally by
#: `TC-PREC-01`/`TC-PREC-02`; everything below it was not.
SHIPPED_THRESHOLDS = {
    "sentence_max_words": 35, "sentence_near_words": 30,
    "cell_max_chars": 120, "cell_max_sentences": 1,
}
#: The scanner's own fallbacks, which supply the two keys no rule file declares.
#: Pinning the rule files alone would leave `sentence_pressure_band` and
#: `cell_prose_chars` movable in code with every gate green.
SHIPPED_DEFAULTS = {
    "sentence_max_words": 35, "sentence_near_words": 30,
    "sentence_pressure_band": 2, "cell_max_chars": 120,
    "cell_max_sentences": 1, "cell_prose_chars": 40,
}

#: Rule 5's exempt sets, PINNED BY MEMBERSHIP. `SHIPPED_ENTRIES` and
#: `SHIPPED_SURFACES` reach the JSON lexicons; these two frozensets live in the
#: scanner and nothing held them. A glyph moved into the exempt set stops being
#: reported, and the individual cases cover `\U0001F534`, `\u2705`, `\u26D4`,
#: `\u2714` and `\u203C` only. Measured: widening `TICK_GLYPHS` to ten glyphs
#: cost 233 `emoji_severity` findings over 636 documents with the battery at
#: `174/174` and the roster at `18/18`, both exit 0 (REG-18).
SHIPPED_TICK_GLYPHS = frozenset("\u2713\u2717")
SHIPPED_STATUS_GLYPHS = frozenset("\u2713\u2717\u2705\u274C\u2611\u2612\u2610")


#: The total this battery PRINTS, PINNED. The denominator was `len(RESULTS)`,
#: so deleting a test function from the tuple in `main` printed a
#: self-consistent `N/N passed` and exited 0, and four documents stated a count
#: that nothing compared against anything: the drift had already shipped, 128
#: documented against 145 running (REG-8). `TC-META-01` pins the run against
#: this number, `TC-SHIP-08` pins the documents against it.
EXPECTED_CASES = 191


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def run_at(scanner, args, text=None):
    """→ (exit_code, stdout, stderr) for a scanner at an arbitrary path.

    The roster pin applies only when no `--rules` argument was given (TASK 099
    D6), so a mutated ruleset cannot be handed to the shipped scanner on the
    command line: passing `--rules` is precisely what switches the pin off.
    `skill_copy` builds a throwaway skill root instead, and this runs the copy.
    """
    p = subprocess.run([sys.executable, scanner] + args, input=text,
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def run(args, text=None):
    """→ (exit_code, stdout, stderr)"""
    return run_at(SCANNER, args, text)


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


def shipped_rules(lang):
    """→ a mutable copy of a shipped rule file."""
    path = os.path.join(SKILL, "data", f"register-{lang}.json")
    return json.load(open(path, encoding="utf-8"))


def skill_copy(rules):
    """→ the scanner path inside a throwaway skill root holding `rules`.

    The scanner resolves its data directory as dirname(dirname(__file__)) and
    globs `data/register-*.json`, so a copy under a fresh root reads the
    mutated files as if they were shipped -- which is the only way a mutation
    reaches the strict roster path (see `run_at`). `rules` maps a language to
    its rule document; an omitted language is a rule file that does not exist.
    """
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, "scripts"))
    os.makedirs(os.path.join(root, "data"))
    scanner = os.path.join(root, "scripts", "scan_register.py")
    shutil.copy(SCANNER, scanner)
    for lang, doc in rules.items():
        path = os.path.join(root, "data", f"register-{lang}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
    return scanner


def scanner_copy(old, new):
    """→ the scanner path inside a skill root whose SCANNER SOURCE was edited.

    `skill_copy` mutates the DATA. Two of the surfaces this battery has to hold
    are code: `SKIP_LINE` decides which lines reach rules 1 and 3, and the flag
    compilation decides whether a declared `i` is applied. Neither is a value a
    rule file states, so neither can be pinned as data -- the mutation has to be
    made in the scanner and observed through the roster.

    The shipped `data/` is copied verbatim, because the claim under test is what
    the SHIPPED ruleset reports through a changed scanner.
    """
    root = tempfile.mkdtemp()
    shutil.copytree(os.path.join(SKILL, "data"), os.path.join(root, "data"))
    os.makedirs(os.path.join(root, "scripts"))
    scanner = os.path.join(root, "scripts", "scan_register.py")
    src = open(SCANNER, encoding="utf-8").read()
    if old not in src:
        return None                  # the anchor moved; the caller fails loudly
    with open(scanner, "w", encoding="utf-8") as f:
        f.write(src.replace(old, new, 1))
    return scanner


def dead_rows(out):
    return [l for l in out.splitlines() if l.startswith("DEAD")]


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
        # The remaining two cross-key invariants were unexercised: deleting
        # either branch left the battery green (REG-7). The fragments are
        # load-bearing -- two branches say `must be below`, so keying both on
        # that phrase would let each case pass against the OTHER branch.
        ("TC-SCHEMA-16 pressure band at or above the hard limit",
         {"schema": "register-rules/v1",
          "thresholds": {"sentence_max_words": 35,
                         "sentence_pressure_band": 35},
          "languages": GOOD_RULES["languages"]}, 'sentence_pressure_band'),
        # `cell_prose_chars == cell_max_chars` is legal (the invariant is `>`),
        # so 121 against 120 is the smallest rejecting pair.
        ("TC-SCHEMA-17 cell prose boundary above the width limit",
         {"schema": "register-rules/v1",
          "thresholds": {"cell_max_chars": 120, "cell_prose_chars": 121},
          "languages": GOOD_RULES["languages"]}, 'must not exceed'),
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
    # `probes` is not what either case is about, but a per-pattern example is
    # mandatory (TASK 099 D7), so a block without one no longer reaches the
    # branch these two cases exercise.
    r3 = json.loads(json.dumps(GOOD_RULES))
    r3["languages"]["en"]["reasoning"] = {
        "modals": [r"\bmust\b"], "causals": [r"\bbecause\b"],
        "probes": {r"\bmust\b": "must", r"\bbecause\b": "because"},
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
        "probes": {r"\bmust\b": "must", r"\bbecause\b": "because"},
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
    # Both controls assert the exit code too. `kinds_of(None)` is `[]`, so a
    # rule file that fails to load satisfies `"reasoning" not in kinds` with no
    # document read at all -- which is how both passed vacuously once a
    # per-pattern example became mandatory.
    src = tmpfile("The field must be set.\n\n**Why.** The reader cannot "
                  "derive it.\n")
    code, rep, _ = scan_json([src], ["--rules", rf])
    check("TC-R3-02 control: split into requirement + Why is silent",
          code == 0 and "reasoning" not in kinds_of(rep),
          f"exit={code} kinds={set(kinds_of(rep))}")

    # a causal with no obligation is prose, not a braided requirement
    src = tmpfile("The counter is stale because the set grew.\n")
    code, rep, _ = scan_json([src], ["--rules", rf])
    check("TC-R3-03 control: a causal without an obligation is silent",
          code == 0 and "reasoning" not in kinds_of(rep),
          f"exit={code} kinds={set(kinds_of(rep))}")


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
    check("TC-PROBE-02 --probe --json reports exactly the shipped detectors",
          code == 0 and rep and rep["ok"]
          and len(rep["probes"]) == SHIPPED_PROBES,
          f"exit={code} n={rep and len(rep['probes'])} "
          f"expected={SHIPPED_PROBES}")

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

    # TASK 097 R16 moved this from 2 to 3. Code 2 claims a dead detector; a
    # path the operator mistyped says nothing about the instrument. Under 2 the
    # CI advisory step went red whenever `docs/TASK.md` was archived, which is
    # a state this framework produces on every task boundary.
    code, _, _ = run([os.path.join(SKILL, "does-not-exist.md"), "--json"])
    check("TC-EXIT-03 unreadable input exits 3, not 2", code == 3,
          f"exit={code}")


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
        # TC-SHIP-04's membership claim survives deleting all but one entry of
        # a rule. This is the count, against a literal (REG-2).
        counts = {r: rules.count(r) for r in sorted(set(rules))}
        check(f"TC-SHIP-07 {lang} ships the pinned per-rule entry counts",
              counts == SHIPPED_ENTRIES[lang],
              f"loaded={counts} pinned={SHIPPED_ENTRIES[lang]}")
        # TC-SHIP-05 asserts only that a rule-3 block EXISTS, and TC-SHIP-07
        # never reaches it -- `reasoning` is not a category. That left the
        # rule-3 lexicon unpinned: a pattern could be deleted with its `probes`
        # key at 168/168 exit 0 and 18/18 exit 0, losing a real finding (REG-2).
        block = doc["languages"][lang].get("reasoning") or {}
        sizes = {k: len(block.get(k) or []) for k in SHIPPED_REASONING[lang]}
        check(f"TC-SHIP-09 {lang} ships the pinned rule-3 vocabulary sizes",
              sizes == SHIPPED_REASONING[lang],
              f"loaded={sizes} pinned={SHIPPED_REASONING[lang]}")

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

    # The documentation half of REG-8. The root is derived from `__file__` -- a
    # hardcoded path would make the case pass vacuously by skipping when the
    # skill is checked out anywhere else.
    repo = os.path.dirname(os.path.dirname(os.path.dirname(SKILL)))
    sites = [os.path.join(SKILL, "SKILL.md"),
             os.path.join(repo, "System", "Docs", "SKILLS.md"),
             # REG-8 removed this file's numeral (D5) and nothing held it
             # removed: adding a sentence stating a count here left the battery
             # at 168/168 exit 0. It is a site of the same claim, so it is read
             # by the same case.
             os.path.join(SKILL, "references", "measurement-baseline.md")]
    # A vendored copy of the skill ships without `System/Docs/`. An absent file
    # is skipped, not failed: nothing there is wrong.
    present = [p for p in sites if os.path.exists(p)]
    # A claim naming a RELEASE records what that revision measured rather than
    # what this run counts: §10.1 states the battery at `128/128` -- the count
    # v3.24.0 shipped. Pinning that against EXPECTED_CASES would demand a
    # correct historical figure be falsified on every future edit, so a claim
    # carrying a release identifier is exempt BY CONSTRUCTION. The exemption
    # keys on the identifier, never on the file, so a new past-state claim in
    # any site is covered and a new present-tense claim in the same file is not.
    # The unit is the blank-line paragraph because these documents are
    # hard-wrapped and the identifier and the numeral land on different lines of
    # one claim (§10.1 wraps between `128/128` and `v3.24.0`'s sentence end); a
    # sentence unit would have to split on the period inside
    # `The installer shall abort because the target exists.`, a code span in
    # that same paragraph.
    release = re.compile(r"\bv\d+\.\d+")
    stated = [(os.path.basename(p), int(n))
              for p in present
              for para in re.split(r"\n[ \t]*\n",
                                   open(p, encoding="utf-8").read())
              if not release.search(para)
              for n in re.findall(r"\b(\d+)[ -]cases?\b", para)]
    # EVERY match is asserted, not the first: a second, newly-added claim in a
    # file already covered is then a red run rather than a silent pass. And a
    # present file that states NO count fails too -- deleting the numeral is
    # the same defect as letting it drift.
    check("TC-SHIP-08 every stated case count equals EXPECTED_CASES",
          not present or (bool(stated)
                          and all(n == EXPECTED_CASES for _, n in stated)),
          f"stated={stated} expected={EXPECTED_CASES} absent="
          f"{[os.path.basename(p) for p in sites if p not in present]}")

    # REG-9. Reverting §4 row `:65` of `measurement-baseline.md` from
    # `not adopted` back to `adopted at info in RU only` left the battery at
    # 168/168 exit 0 and the roster at 18/18 exit 0 -- the fix's whole
    # verification was a reviewer reading it. An `**adopted**` row asserts that
    # a shipped lexicon entry implements the family, so §4's adopted rows are
    # checked against the two shipped lexicons.
    #
    # The expected surface is a LITERAL per row rather than a string read out of
    # the row's own cell, because that row decides wrongly in BOTH directions:
    # its declared surface `не просто X, а Y` carries metavariables no pattern
    # can contain, and the shipped RU entry `просто` does contain the substring
    # `просто`. A row marked adopted that this map does not name is a failure --
    # that is what catches the revert, and it makes adopting a further row a
    # deliberate edit here rather than prose nothing reads.
    adopted_surfaces = {
        "Marketing vocabulary": ("robust", "seamless", "leverage", "delve",
                                 "crucial"),
    }
    base = os.path.join(SKILL, "references", "measurement-baseline.md")
    sec = re.search(r"^## 4\..*?(?=^## |\Z)",
                    open(base, encoding="utf-8").read(), re.M | re.S)
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")]
            for ln in (sec.group(0).splitlines() if sec else [])
            if ln.startswith("|")]
    # The Hits column selects the data rows: the header and the `:---`
    # separator are the two rows that carry no measurement.
    rows = [r for r in rows if len(r) == 3 and r[1].isdigit()]
    # `**adopted**` in the shipped row, bare `adopted` in the row REG-9
    # replaced. Emphasis is markup, so it is stripped before the verdict is
    # read; `not adopted` does not begin with `adopted`.
    claimed = [r[0] for r in rows
               if r[2].replace("*", "").strip().lower().startswith("adopted")]
    lex = [f"{e.get('marker', '')} {e.get('pattern', '')}"
           for lang in ("en", "ru")
           if os.path.exists(os.path.join(SKILL, "data",
                                          f"register-{lang}.json"))
           for c in shipped_rules(lang)["languages"][lang]["categories"]
           for e in c["entries"]]
    unnamed = [lab[:44] for lab in claimed
               if not any(k in lab for k in adopted_surfaces)]
    unbacked = [(k, s) for k, surfaces in adopted_surfaces.items()
                for s in surfaces if not any(s in blob for blob in lex)]
    # A parse that found no table would leave both lists empty and pass
    # vacuously, so the row this map names must be present AND adopted.
    missing = [k for k in adopted_surfaces
               if not any(k in lab for lab in claimed)]
    check("TC-SHIP-10 every §4 row marked adopted ships the entries it claims",
          not (unnamed or unbacked or missing),
          f"rows={len(rows)} adopted-but-unnamed={unnamed} "
          f"unbacked={unbacked} named-but-not-adopted={missing}")

    # REG-13 removed `thirteen`, `nine` and `fourteen` from the documents that
    # restated the licensed-form count, because `authoring-contract.md:107`
    # declares the list open (D4). Restoring any of them left the battery output
    # byte-identical at exit 0. It reads the same sites as TC-SHIP-08, since a
    # restated count drifts in whichever document restates it.
    # The pin is the ABSENCE of a cardinal, and the window is one token:
    # the defect wrote `thirteen licensed statement forms` and `six tests, nine
    # licensed forms`, while the wording that replaced it is `six tests, the
    # licensed forms` -- a wider window, or a bare `\w+`, would report that
    # correct sentence for the `six` that counts the TESTS.
    cardinal = (r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
                r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
                r"nineteen|twenty")
    counted = re.compile(rf"(?i)\b(?:(?:{cardinal})\s+licensed"
                         rf"|licensed\s+(?:{cardinal}))\b")
    stated_forms = [(os.path.basename(p), m.group(0))
                    for p in present
                    for m in counted.finditer(open(p, encoding="utf-8").read())]
    check("TC-SHIP-11 no document states a cardinal for the licensed forms",
          not stated_forms, f"counted={stated_forms}")


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

    # SENT_SPLIT carries four abbreviation lookbehinds and only `e.g.` was
    # pinned; dropping any of the other three produced silent sentence_length
    # false negatives with both gates green (REG-6). These run against the
    # SHIPPED rules -- no `--rules` -- which is what makes them pins on the
    # real SENT_SPLIT rather than on a fixture.
    for name, mid in (("TC-PREC-06a 'i.e. Capital'", "i.e. Foo "),
                      ("TC-PREC-06b 'vs. Capital'", "vs. Foo "),
                      ("TC-PREC-06c 'см. Capital'", "см. Foo ")):
        doc = tmpfile(halves(mid))
        code, rep, _ = scan_json([doc])
        check(f"{name} is not a sentence boundary",
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

    doc = tmpfile("| a | b |\n| --- | --- |\n| \u2610 | ok |\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-12a an empty checkbox in a table cell is a value too",
          code == 0 and "emoji_severity" not in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    # `\u2713`/`\u2717` are exempt in EVERY position, not only inside a table (REG-10).
    # The fixture is the shape at `skill-archive-task/SKILL.md`: a numbered
    # list item, where the narrowed guard reported both ticks and the guidance
    # told the author to write `SEV-2` instead. This case is what makes a
    # re-narrowing to in-table-only detectable.
    doc = tmpfile("9. **Step 6** \u2014 validate: `docs/TASK.md` gone \u2713, "
                  "archive present \u2713.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-12b a tick in a numbered list is exempt, not a severity",
          code == 0 and "emoji_severity" not in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    doc = tmpfile("\u2705 The migration is done.\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-13 the same glyph in PROSE is still reported",
          code == 0 and "emoji_severity" in kinds_of(rep),
          f"kinds={set(kinds_of(rep))}")

    # The finding above is only useful if its guidance applies to the glyph it
    # found. One string sent the author of a done/not-done value to `SEV-2`
    # (REG-10), so the branch is asserted from both sides: a status glyph gets
    # the status words and must NOT get the severity wording.
    hit = next((h for h in ((rep["warn"] + rep["info"]) if rep else [])
                if h["kind"] == "emoji_severity"), None)
    check("TC-ADV-13a a status glyph gets status-word guidance, not `SEV-2`",
          hit and "status word" in hit["guidance"]
          and "SEV-2" not in hit["guidance"],
          f"guidance={hit and hit['guidance']!r}")

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

    # The case above does not discriminate: its fixture is blockquote PROSE,
    # which is prose with or without `dequote`, and the quoted line is still 42
    # words. The claim `dequote` actually carries is that a TABLE inside a
    # callout is a table -- PIPE_ROW and DELIM_ROW anchor at `^\s*`, so without
    # the strip those rows never reach `table_lines` (REG-5).
    doc = tmpfile("> [!IMPORTANT]\n> | a | b |\n> | --- | --- |\n> | "
                  + "x" * 130 + " | ok |\n")
    code, rep, _ = scan_json([doc], ["--rules", rf])
    check("TC-ADV-15a a table inside a callout is a table, not prose",
          code == 0 and "cell_width" in kinds_of(rep),
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


# ------------------------------------------------- TASK 097: masking pins ----
# The shipped mask() applied four regexes in sequence. A comment boundary
# landing inside a code span removed one backtick, the survivor paired with a
# later one, and the code/prose classification inverted to the end of the file.
# Every case below FAILS against that implementation, which is what makes it a
# pin rather than a description.

#: TASK 097 E1. Valid Markdown: a marker cited in a code span, then a correct
#: comment. `Наивный` sits after both and must still be reported.
#:
#: The trailing code span is load-bearing. Without a LATER backtick the orphan
#: left by the comment has nothing to pair with, nothing further is masked, and
#: the case passes against the defect it is meant to pin.
F_INVERSION = ("Маркер `<!--` открывает HTML-комментарий.\n\n"
               "<!-- обычный, корректный комментарий -->\n\n"
               "Наивный подход здесь неверен.\n"
               "Ещё предложение с `кодом` внутри.\n")


def t_097_masking():
    src = tmpfile(F_INVERSION)
    code, rep, _ = scan_json([src])
    marks = [h["match"] for h in ((rep["warn"] + rep["info"]) if rep else [])]
    check("TC-097-01 a marker cited in a code span does not blind the scanner",
          code == 0 and any("аивн" in m for m in marks), f"marks={marks}")

    # The same document without the citation. The finding set must be equal:
    # that equality is the requirement, not merely "some finding appears".
    ctl = tmpfile(F_INVERSION.replace("`<!--`", "маркер"))
    _, rep2, _ = scan_json([ctl])
    check("TC-097-02 citation changes no finding",
          sorted(kinds_of(rep)) == sorted(kinds_of(rep2)),
          f"with={sorted(kinds_of(rep))} without={sorted(kinds_of(rep2))}")

    # A construct may not begin inside another: `naive` inside the fence is
    # code, the two outside it are prose. Three occurrences, two reported.
    src = tmpfile("The naive approach is wrong.\n\n"
                  "```text\n<!-- naive\n```\n\n"
                  "The naive approach is wrong again.\n")
    _, rep, _ = scan_json([src])
    check("TC-097-03 a fence body is not scanned and does not leak",
          kinds_of(rep).count("marker") == 2, f"kinds={kinds_of(rep)}")

    # CommonMark: a blank line ends the paragraph and closes the span. Two
    # backticks in separate paragraphs are NOT a span, so the prose between
    # them stays prose. Under `re.S` without the bound they pair and it does
    # not.
    src = tmpfile("A stray ` opens a paragraph.\n\n"
                  "The naive approach is wrong.\n\n"
                  "Another paragraph with a stray ` in it.\n")
    _, rep, _ = scan_json([src])
    check("TC-097-04 a code span does not cross a blank line",
          "marker" in kinds_of(rep), f"kinds={kinds_of(rep)}")


def t_097_input_defects():
    src = tmpfile("The naive approach is wrong.\n\n<!-- never terminated\n")
    code, out, _ = run([src])
    check("TC-097-05 an unterminated comment is named, and exits 0",
          code == 0 and "unterminated" in out.lower(), f"exit={code}")

    src = tmpfile("A stray ` backtick.\n\nThe naive approach is wrong.\n")
    code, out, _ = run([src])
    check("TC-097-06 an unpaired backtick is named, and exits 0",
          code == 0 and "unpaired" in out.lower(), f"exit={code}")

    # A zero is never bare: the masked share is what tells a clean document
    # from an unread one.
    src = tmpfile("Plain prose with nothing to report.\n")
    code, rep, _ = scan_json([src])
    diag = json.dumps(rep.get("diagnostics")) if rep else ""
    check("TC-097-07 DIAGNOSTICS carries the masked-letter share",
          "masked_letter_share" in diag, f"diag_keys={diag[:120]}")


def t_097_exit_contract():
    # 2 means the instrument is broken. An unreadable path is an invocation.
    code, out, err = run(["docs/NOSUCH-097.md"])
    check("TC-097-08 an unreadable path exits 3, not 2",
          code == 3, f"exit={code}")
    check("TC-097-09 the unreadable path is named",
          "NOSUCH-097" in (out + err), f"out={(out + err)[:120]!r}")

    real = tmpfile("Plain prose.\n")
    code, _, _ = run([real, "docs/NOSUCH-097.md", "--allow-missing"])
    check("TC-097-10 --allow-missing tolerates a named absence",
          code == 0, f"exit={code}")

    code, _, _ = run(["docs/NOSUCH-097.md", "--allow-missing"])
    check("TC-097-11 --allow-missing with nothing readable still exits 3",
          code == 3, f"exit={code}")


def t_097_probe_coverage():
    """Every rule-3 pattern is exercised, so killing any one turns it DEAD."""
    base = json.loads(json.dumps(GOOD_RULES))
    base["languages"]["en"]["reasoning"] = {
        "modals": [r"\bmust\b", r"\bshall\b"],
        "causals": [r"\bbecause\b", r"\bsince\b"],
        "probes": {r"\bmust\b": "must", r"\bshall\b": "shall",
                   r"\bbecause\b": "because", r"\bsince\b": "since"},
        "probe": "The field must be set, because the reader cannot derive it."}
    code, out, _ = run(["--probe", "--rules", rules_file(base)])
    check("TC-097-12 a fully live rule-3 vocabulary probes live",
          code == 0 and "DEAD" not in out, f"exit={code}")
    check("TC-097-13 the probe detail states what it exercised",
          "4 exercised of 4" in out, f"out={out[-160:]!r}")

    # Edit a pattern and leave its example. The DECLARED probe sentence still
    # fires, so an implementation that trusts that one sentence stays green
    # here — which is the defect (TASK 097 D3).
    for key, idx, name in (("modals", 1, "shall"), ("causals", 1, "since")):
        doc = json.loads(json.dumps(base))
        doc["languages"]["en"]["reasoning"][key][idx] = r"\bZZZNEVERMATCHES\b"
        code, out, err = run(["--probe", "--rules", rules_file(doc)])
        check(f"TC-097-14 a rule-3 {name} edited away from its example is "
              f"rejected",
              code == 2 and "left behind" in (out + err), f"exit={code}")

    # The other half of the same signature: the pattern kept, the example
    # changed to something it does not match.
    doc = json.loads(json.dumps(base))
    doc["languages"]["en"]["reasoning"]["probes"][r"\bshall\b"] = "zzznever"
    code, out, err = run(["--probe", "--rules", rules_file(doc)])
    check("TC-097-16 an example its pattern no longer matches is rejected",
          code == 2 and "no longer matches its own example" in (out + err),
          f"exit={code}")

    # A declared example is MANDATORY (TASK 099 D7). This case previously
    # pinned the opposite: a block with no `probes` loaded and reported `0
    # exercised of 4` while the row still printed live. That state is the one
    # that re-opens TASK 097 D3 -- drop the example, then edit the pattern away,
    # and every gate stays green.
    doc = json.loads(json.dumps(base))
    del doc["languages"]["en"]["reasoning"]["probes"]
    code, out, err = run(["--probe", "--rules", rules_file(doc)])
    check("TC-097-15 a reasoning block with no examples is rejected at load",
          code == 2 and "declares no example" in (out + err),
          f"exit={code} out={(out + err)[-160:]!r}")


# ------------------------------- TASK 099: gate honesty and the new entries ----
# Both CI gates measured themselves against the data under test, so every
# mutation below was green before the fix: deleting a whole detector class
# printed `17/17 detectors live` exit 0, and the two-step at TC-099-05 loaded
# clean at `18/18` exit 0 while its vocabulary reported nothing (REG-3, REG-4).


def t_099_roster_pin():
    """A vanished detector class reports DEAD instead of shrinking the roster.

    These cases cannot pass `--rules`: strictness is keyed on `not args.rules`
    (TASK 099 D6), so handing the mutation to the scanner on the command line
    switches off the very pin under test. They mutate a throwaway skill root.
    """
    # The control. `skill_copy` is machinery, and machinery that quietly stops
    # producing a runnable scanner would make the two mutations below "fail"
    # for the wrong reason -- a green pair of cases testing nothing.
    scanner = skill_copy({"en": shipped_rules("en"), "ru": shipped_rules("ru")})
    code, out, err = run_at(scanner, ["--probe"])
    check("TC-099-01 control: an unmutated skill copy probes 18/18 live",
          code == 0 and "18/18 detectors live" in out,
          f"exit={code} tail={out.strip()[-60:]!r} err={err.strip()[:90]}")

    # Every rule-6 entry of one language, removed. A category left with no
    # entries is rejected by the schema for an unrelated reason, so the empty
    # category goes with them -- the mutation under test is a MISSING CLASS,
    # not a malformed file.
    en = shipped_rules("en")
    cats = []
    for cat in en["languages"]["en"]["categories"]:
        cat["entries"] = [e for e in cat["entries"] if e.get("rule", 2) != 6]
        if cat["entries"]:
            cats.append(cat)
    en["languages"]["en"]["categories"] = cats
    scanner = skill_copy({"en": en, "ru": shipped_rules("ru")})
    code, out, _ = run_at(scanner, ["--probe"])
    check("TC-099-02 a deleted detector class is DEAD, not a smaller roster",
          code == 2 and "17/18 detectors live" in out
          and any(l.startswith("DEAD") and "metaphor" in l
                  for l in out.splitlines()),
          f"exit={code} tail={out.strip()[-60:]!r}")

    # The language dimension of the same defect: loading only
    # `register-en.json` printed `9/9 detectors live` exit 0. The denominator
    # is held by SHIPPED_LANGS, so 18 stays 18. Four rows go DEAD and the five
    # structural ones stay live -- those are built from thresholds and carry no
    # language, so calling them dead would state something false.
    scanner = skill_copy({"en": shipped_rules("en")})
    code, out, _ = run_at(scanner, ["--probe"])
    dead = [l for l in out.splitlines() if l.startswith("DEAD")]
    check("TC-099-03 an absent shipped language holds the denominator at 18",
          code == 2 and "14/18 detectors live" in out
          and len(dead) == 4 and all(" ru " in l for l in dead),
          f"exit={code} dead={len(dead)} tail={out.strip()[-60:]!r}")


def t_099_reasoning_examples():
    """A rule-3 pattern that declares no example does not load (TASK 099 D7).

    Both mutate the SHIPPED English vocabulary rather than a fixture, because
    the hatch they close was found in the shipped file: TC-099-05's sequence
    loaded clean, printed `18/18 detectors live`, exited 0 and left the battery
    at `145/145`, while the document below reported zero findings (REG-3).
    """
    SHALL = r"\bshall\b"
    doc = tmpfile("The installer shall abort because the target exists.\n")

    rules = shipped_rules("en")
    del rules["languages"]["en"]["reasoning"]["probes"][SHALL]
    code, _, err = run([doc, "--rules", rules_file(rules), "--json"])
    check("TC-099-04 a rule-3 pattern with no declared example is rejected",
          code == 2 and "declares no example" in err,
          f"exit={code} stderr={err.strip()[:130]}")

    # The TASK 097 D3 two-step. Order is what makes it a hatch: dropping the
    # example FIRST leaves the orphan check nothing to catch, and the pattern
    # can then be edited away with no probe noticing.
    rules = shipped_rules("en")
    block = rules["languages"]["en"]["reasoning"]
    del block["probes"][SHALL]
    block["modals"][block["modals"].index(SHALL)] = r"\bZZZNEVERMATCHES\b"
    code, _, err = run([doc, "--rules", rules_file(rules), "--json"])
    check("TC-099-05 the TASK 097 D3 two-step is rejected at load",
          code == 2 and "declares no example" in err,
          f"exit={code} stderr={err.strip()[:130]}")


def t_099_en_entries():
    """The two English detectors `authoring-contract.md` names as canonical.

    Both ship in Russian and did not ship in English (REG-11, REG-12). Every
    case runs against the SHIPPED rules -- no `--rules` -- so it pins the entry
    in `data/register-en.json` rather than a fixture, and each positive carries
    the control that kept its members out of the lexicon until they measured.
    """
    doc = tmpfile("The gate goes red when the fixture passes, and turns green "
                  "again after the revert.\n")
    code, rep, _ = scan_json([doc])
    hits = [h["match"] for h in ((rep["warn"] + rep["info"]) if rep else [])
            if h["kind"] == "maxim"]
    check("TC-099-06 a personified test reports one maxim per verb form",
          code == 0 and len(hits) == 2, f"exit={code} maxims={hits}")

    doc = tmpfile("The main risk is a proof that proves the wrong "
                  "property.\n")
    code, rep, _ = scan_json([doc])
    hits = [h["match"] for h in ((rep["warn"] + rep["info"]) if rep else [])
            if h["kind"] == "marker"]
    check("TC-099-07 an unranked superlative reports one marker",
          code == 0 and len(hits) == 1, f"exit={code} markers={hits}")

    # The English twin of TC-FP-04: Red-Green-Refactor is terminology, and the
    # entry matches verb forms only, so the adjectival uses stay silent.
    doc = tmpfile("Phase 1 leaves the red phase and a green run behind, per "
                  "Red-Green-Refactor.\n")
    code, rep, _ = scan_json([doc])
    check("TC-099-08 control: adjectival red/green is TDD terminology",
          code == 0 and "maxim" not in kinds_of(rep),
          f"exit={code} kinds={set(kinds_of(rep))}")

    # `stays forever green` sits within reach of BOTH rule-4 entries. The new
    # one lists verb forms and no state verb, so the two never claim the same
    # span: one finding, and it is the pre-existing entry's.
    doc = tmpfile("The guard stays forever green.\n")
    code, rep, _ = scan_json([doc])
    hits = [h["match"] for h in ((rep["warn"] + rep["info"]) if rep else [])
            if h["kind"] == "maxim"]
    check("TC-099-09 control: `forever green` is reported once, not twice",
          code == 0 and hits == ["forever green"], f"exit={code} maxims={hits}")

    # The same claim for rule 2: the ranking entry's noun list excludes
    # `insight` and `point`, which the entry above it already owns, and `whole`
    # is not in its adjective set. Two findings, both the older entry's.
    #
    # The finding COUNT cannot state that. `_dedupe_spans` collapses an
    # overlapping span, so extending the ranking noun set with `insight|point`
    # -- the exact overlap this case denies -- left the count at 2, both
    # matches and both guidance strings unchanged (the older entry sorts first
    # and wins the tie) and the battery at 168/168 exit 0. A pin another
    # mechanism guarantees is REG-3 one level up. So the entry is ISOLATED: the
    # rules are the shipped ones with every entry but the ranking one removed,
    # which no dedupe can hide behind, and the fixture must then report nothing.
    RANKING = "A ranking with no scale is unverifiable."
    doc = tmpfile("The key insight is the ordering, and the whole point is "
                  "the same.\n")
    code, rep, _ = scan_json([doc])
    hits = [(h["match"], h["guidance"])
            for h in ((rep["warn"] + rep["info"]) if rep else [])
            if h["kind"] == "marker"]

    only = shipped_rules("en")
    cats = []
    for cat in only["languages"]["en"]["categories"]:
        cat["entries"] = [e for e in cat["entries"]
                          if e.get("guidance", "").startswith(RANKING)]
        if cat["entries"]:                # an empty category fails the schema
            cats.append(cat)
    only["languages"]["en"]["categories"] = cats
    # A selector that matches nothing would make the isolated half pass
    # vacuously, so the entry count is asserted, not assumed. `guidance` is the
    # identity: it is what distinguishes the two entries in a report, and
    # rewording it IS an entry-identity change.
    kept = sum(len(c["entries"]) for c in cats)
    code2, rep2, err2 = scan_json([doc], ["--rules", rules_file(only)])
    alone = [h["match"]
             for h in ((rep2["warn"] + rep2["info"]) if rep2 else [])]
    check("TC-099-10 control: the ranking entry does not overlap `key insight`",
          code == 0 and [m for m, _ in hits] == ["The key insight",
                                                 "the whole point"]
          and all(g.startswith("Delete the frame") for _, g in hits)
          and kept == 1 and code2 == 0 and alone == [],
          f"exit={code} markers={hits} kept={kept} isolated={alone} "
          f"exit2={code2} {err2.strip()[:80]}")

    # Cardinality does not pin SURFACE. Each case above asserts only the new
    # entry's own probe string, so the pattern could be NARROWED with the entry
    # count and both gates unchanged: narrowing rule 4 to
    # `\b(goes|turns)\s+(red|green)\b` left 168/168 exit 0 and 18/18 exit 0
    # while `The gate went red.` and `The check flipped red.` reported nothing,
    # and narrowing rule 2 to `\bthe main risk\b` silenced `The biggest
    # problem is the ordering.` the same way. Both forms are enumerated in the
    # entries' own `note` and in `references/authoring-contract.md`, so these
    # pin every enumerated surface, one fixture per form, on the SHIPPED rules.
    missed = []
    for text, want in (("The gate went red.", "went red"),
                       ("The check flipped red.", "flipped red"),
                       ("The suite turns green.", "turns green"),
                       ("The gate goes red.", "goes red")):
        code, rep, _ = scan_json([tmpfile(text + "\n")])
        hits = [h["match"] for h in ((rep["warn"] + rep["info"]) if rep else [])
                if h["kind"] == "maxim"]
        if not (code == 0 and hits == [want]):
            missed.append((want, code, hits))
    check("TC-099-11 every enumerated rule-4 verb form still fires",
          not missed, f"missed={missed}")

    missed = []
    for text, want in (("The biggest problem is the ordering.",
                        "The biggest problem"),
                       ("The primary danger is an unreported truncation.",
                        "The primary danger"),
                       ("The key risk is a stale cache.", "The key risk")):
        code, rep, _ = scan_json([tmpfile(text + "\n")])
        hits = [h["match"] for h in ((rep["warn"] + rep["info"]) if rep else [])
                if h["kind"] == "marker"]
        if not (code == 0 and hits == [want]):
            missed.append((want, code, hits))
    check("TC-099-12 every enumerated rule-2 ranking surface still fires",
          not missed, f"missed={missed}")


# ------------------ TASK 100: what the gates measure against, not how many ----
# Every mutation below was green before this section: the battery printed
# `174/174 passed` exit 0 and the roster printed `18/18 detectors live` exit 0
# while a detector was gone. The counts TASK 099 pinned answer "how many"; each
# of these keeps the count and removes detection (REG-14 … REG-18).


def t_100_surface_pins():
    """Which patterns ship, and with which flags — not how many."""
    for lang in ("en", "ru"):
        doc = json.load(open(os.path.join(SKILL, "data", f"register-{lang}.json"),
                             encoding="utf-8"))
        keys = [(e.get("rule", 2), e["pattern"], e.get("flags", ""))
                for cat in doc["languages"][lang]["categories"]
                for e in cat["entries"]]
        loaded = set(keys)
        pinned = {(rule, pat, fl)
                  for rule, pairs in SHIPPED_SURFACES[lang].items()
                  if rule != 3 for pat, fl in pairs}
        # The symmetric difference, not a bare inequality: a pin that says only
        # "these differ" is re-pinned by copying the loaded value, which accepts
        # the mutation under review (TASK 100 D1).
        #
        # Uniqueness is asserted with it. Two entries carrying the same pattern
        # and flags collapse into one set member, so a duplicate would pass this
        # comparison while reporting every match twice.
        check(f"TC-100-01 {lang} ships the pinned lexical surfaces",
              loaded == pinned and len(keys) == len(loaded),
              f"added={sorted(loaded - pinned)} removed={sorted(pinned - loaded)} "
              f"entries={len(keys)} distinct={len(loaded)}")

        block = doc["languages"][lang].get("reasoning") or {}
        r3 = tuple(block.get("modals") or []) + tuple(block.get("causals") or [])
        check(f"TC-100-02 {lang} ships the pinned rule-3 surfaces",
              set(r3) == set(SHIPPED_SURFACES[lang][3]),
              f"added={sorted(set(r3) - set(SHIPPED_SURFACES[lang][3]))} "
              f"removed={sorted(set(SHIPPED_SURFACES[lang][3]) - set(r3))}")

        # The two pins state the same fact at different strengths. Re-pinning
        # one and not the other leaves the weaker one describing a vocabulary
        # that no longer exists, which is how REG-2's fix would rot.
        sizes = {rule: len(pairs)
                 for rule, pairs in SHIPPED_SURFACES[lang].items() if rule != 3}
        r3_size = len(SHIPPED_SURFACES[lang][3])
        want_r3 = sum(SHIPPED_REASONING[lang].values())
        check(f"TC-100-03 {lang} surface and count pins agree",
              sizes == SHIPPED_ENTRIES[lang] and r3_size == want_r3,
              f"surfaces={sizes}/{r3_size} counts={SHIPPED_ENTRIES[lang]}/{want_r3}")


def t_100_threshold_and_glyph_pins():
    """Values the scanner applies, pinned against literals declared here."""
    for lang in ("en", "ru"):
        doc = json.load(open(os.path.join(SKILL, "data", f"register-{lang}.json"),
                             encoding="utf-8"))
        check(f"TC-100-04 {lang} ships the pinned thresholds",
              doc.get("thresholds") == SHIPPED_THRESHOLDS,
              f"loaded={doc.get('thresholds')} pinned={SHIPPED_THRESHOLDS}")

    check("TC-100-05 the scanner's threshold defaults are pinned",
          scan_register.DEFAULTS == SHIPPED_DEFAULTS,
          f"loaded={scan_register.DEFAULTS} pinned={SHIPPED_DEFAULTS}")
    # Every key a rule file may declare has a default, or a partial rule file
    # raises KeyError deep inside a scan instead of being rejected at load.
    check("TC-100-06 every threshold key has a default",
          set(scan_register.THRESHOLD_KEYS) == set(SHIPPED_DEFAULTS),
          f"keys={sorted(scan_register.THRESHOLD_KEYS)} "
          f"defaults={sorted(SHIPPED_DEFAULTS)}")

    check("TC-100-07 TICK_GLYPHS membership is pinned",
          scan_register.TICK_GLYPHS == SHIPPED_TICK_GLYPHS,
          f"added={sorted(scan_register.TICK_GLYPHS - SHIPPED_TICK_GLYPHS)} "
          f"removed={sorted(SHIPPED_TICK_GLYPHS - scan_register.TICK_GLYPHS)}")
    check("TC-100-08 STATUS_GLYPHS membership is pinned",
          scan_register.STATUS_GLYPHS == SHIPPED_STATUS_GLYPHS,
          f"added={sorted(scan_register.STATUS_GLYPHS - SHIPPED_STATUS_GLYPHS)} "
          f"removed={sorted(SHIPPED_STATUS_GLYPHS - scan_register.STATUS_GLYPHS)}")
    # A tick is exempt everywhere and the wider set only inside a table, so the
    # first must stay a subset of the second or the two guards contradict.
    check("TC-100-09 every tick glyph is also a status glyph",
          scan_register.TICK_GLYPHS <= scan_register.STATUS_GLYPHS,
          f"outside={sorted(scan_register.TICK_GLYPHS - scan_register.STATUS_GLYPHS)}")


def t_100_code_mutations():
    """Two detectors blinded in CODE, where no data pin can reach them."""
    # The control. `scanner_copy` is machinery; machinery that stopped producing
    # a runnable scanner would make the mutations below "fail" for the wrong
    # reason -- a green pair of cases testing nothing.
    scanner = scanner_copy("SHIPPED_LANGS", "SHIPPED_LANGS")
    code, out, err = run_at(scanner, ["--probe"])
    check("TC-100-10 control: an unmutated scanner copy probes 18/18 live",
          code == 0 and "18/18 detectors live" in out,
          f"exit={code} tail={out.strip()[-60:]!r} err={err.strip()[:90]}")

    # REG-17. `prose_blocks` drops a `SKIP_LINE` match before rules 1 and 3 see
    # it, and the fixtures were bare sentences, so a filter that swallows list
    # markers was invisible: 4,835 findings fell to 4,354 over 636 documents
    # with both gates at exit 0. Most prose in these corpora is a list item.
    scanner = scanner_copy(
        r'SKIP_LINE = re.compile(r"^\s*(#{1,6}\s|```|~~~|-{3,}\s*$)")',
        r'SKIP_LINE = re.compile(r"^\s*([-*+]\s|#{1,6}\s|```|~~~|-{3,}\s*$)")')
    code, out, _ = run_at(scanner, ["--probe"]) if scanner else (0, "", "")
    dead = dead_rows(out)
    check("TC-100-11 a SKIP_LINE that swallows list markers reports DEAD",
          scanner and code == 2 and "12/18 detectors live" in out
          and {"sentence_length", "sentence_near_limit", "reasoning"}
          <= {l.split()[2] for l in dead},
          f"exit={code} dead={[l.split()[2] for l in dead]}")

    # REG-16, code half. The scan compiles its regex at a different site from
    # the validator's own compile, so losing the flag there left the loader
    # green. Before the case-flip check the roster named the 15 entries whose
    # own probe happened to carry a capital and reported the other 63 verified.
    scanner = scanner_copy(
        '                    for f_ in e.get("flags", ""):\n'
        "                        fl |= FLAG_MAP[f_]",
        '                    for f_ in e.get("flags", ""):\n'
        "                        fl |= 0")
    code, out, _ = run_at(scanner, ["--probe"]) if scanner else (0, "", "")
    dead = dead_rows(out)
    check("TC-100-12 a declared flag that is not applied reports DEAD",
          scanner and code == 2 and len(dead) == 6
          and all("case-blind" in l for l in dead),
          f"exit={code} dead={len(dead)} "
          f"kinds={[l.split()[2] for l in dead]}")

    # The other direction of the same claim: the shipped scanner APPLIES every
    # flag it accepts, so no shipped entry is case-blind. Without this, TC-100-12
    # would pass on a scanner that reported every entry case-blind always.
    code, out, _ = run(["--probe"])
    check("TC-100-13 no shipped entry is case-blind",
          code == 0 and "case-blind" not in out,
          f"exit={code} {[l for l in out.splitlines() if 'case-blind' in l]}")


def main():
    for fn in (t_schema, t_masking, t_structural, t_lexical, t_reasoning,
               t_probe, t_diagnostics, t_sections, t_terms, t_language,
               t_exits, t_data_extensibility, t_shipped, t_false_positives,
               t_precision, t_masking_gaps, t_detector_gaps,
               t_contract_gaps, t_exit_contract, t_rule_authoring_gaps,
               t_reporting_gaps, t_097_masking, t_097_input_defects,
               t_097_exit_contract, t_097_probe_coverage,
               t_099_roster_pin, t_099_reasoning_examples, t_099_en_entries,
               t_100_surface_pins, t_100_threshold_and_glyph_pins,
               t_100_code_mutations):
        try:
            fn()
        except Exception as exc:                      # noqa: BLE001
            check(f"{fn.__name__} raised", False, f"{type(exc).__name__}: {exc}")

    # `+ 1` counts this check itself: `check` has not appended it yet, and the
    # number under test is the one the run PRINTS. Here rather than in the
    # tuple above, so the synthetic `<fn> raised` rows are inside the total too
    # -- a function that dies halfway loses its remaining cases and gains one
    # row, and the same pin catches the difference.
    total = len(RESULTS) + 1
    check("TC-META-01 the battery ran every case it declares",
          total == EXPECTED_CASES, f"ran={total} declared={EXPECTED_CASES}")

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
