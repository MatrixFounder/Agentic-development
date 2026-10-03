"""Tests for the hash-bound render evidence of the references (TASK 108, R9.3-R9.5, A5, A19).

`fixtures/paired-examples-geometry.json` holds the render evidence of every mermaid fence of
`references/paired-examples.md`; `fixtures/references-geometry.json` holds that of every other
`references/*.md`. `render_check.py --fixture` writes both. No test here needs node:

1. every mermaid fence of those files has an entry whose sha256 equals the hash of the fence
   text, recomputed here. The entry is looked up by that hash: a prose edit that moves a fence
   to another line keeps its evidence. A fence without one, and an entry whose text no fence of
   the file holds any more, are named as `re-render <file>:<line>`;
2. each entry holds the renders of the check pair and the dark render, made by the pinned
   mermaid and mermaid-cli;
3. a positive figure passes `svg_geometry.evaluate` in each of them, against the current
   `notation.json`;
4. a negative figure that names render checks fails at least one of them in one render. A
   negative figure fails no render check it does not name, as `render_check` requires. Its lint
   names are checked by the lint's own gate (TASK R6.7);
5. each file's evidence was measured by the current instruments (`render_check.INSTRUMENT_FILES`,
   by sha256) under the current notation values that shape a render (the column, the render
   width, the dark theme and page, the security level, the legibility exemptions). Evidence of
   other instruments or settings is stale: the stored metrics would no longer be what the check
   measures.
"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import mermaid_model as mm  # noqa: E402
import render_check as rc  # noqa: E402
import svg_geometry as sg  # noqa: E402

SKILL = HERE.parent.parent
REFERENCES = SKILL / "references"
PAIRED = "references/paired-examples.md"
FIXTURE_FILES = {"paired-examples-geometry.json": lambda key: key == PAIRED,
                 "references-geometry.json": lambda key: key != PAIRED}
NOTATION = mm.load_notation()
PAIR = NOTATION["renderers"]["check_pair"]
REQUIRED = (PAIR[0], PAIR[0] + "-dark", PAIR[1])
REFRESH = ("python3 scripts/render_check.py <file> --fixture scripts/tests/fixtures/<fixture>.json "
           "(run from the skill directory, with the renderers of setup_renderers.sh)")


def load_fixture(name):
    path = HERE / "fixtures" / name
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


FIXTURES = {name: load_fixture(name) for name in FIXTURE_FILES}


def fence_texts(path):
    """[(opening fence line, `mermaid_model.fence_sha256` of the body, body)] of a file."""
    text = mm.normalize_text(path.read_text(encoding="utf-8"))
    return [(f.start, mm.fence_sha256(f.body), f.body) for f in mm.extract_fences(text, ("mermaid",))]


def entry_for(record, line, sha):
    """The stored entry of the fence at `line` with hash `sha`: the one at that line, or else any
    entry of the file with the same hash (the fence moved, its text did not)."""
    entry = record["figures"].get(str(line))
    if entry is not None and entry.get("sha256") == sha:
        return entry
    return next((e for e in record["figures"].values() if e.get("sha256") == sha), None)


def entries():
    """(file key, fence line, entry) of both fixtures."""
    for data in FIXTURES.values():
        for key, record in sorted((data or {}).get("files", {}).items()):
            for line, entry in sorted(record["figures"].items(), key=lambda kv: int(kv[0])):
                yield key, line, entry


class TestFixturesExist(unittest.TestCase):
    def test_both_fixtures_are_present(self):
        for name, data in FIXTURES.items():
            self.assertIsNotNone(data, "fixtures/%s is missing; write it with %s" % (name, REFRESH))
            self.assertEqual(data["schema"], rc.FIXTURE_SCHEMA, name)

    def test_each_fixture_covers_its_files(self):
        want = {PAIRED} | {"references/%s" % p.name for p in REFERENCES.glob("*.md")}
        covered = set()
        for name, belongs in FIXTURE_FILES.items():
            keys = set((FIXTURES[name] or {}).get("files", {}))
            self.assertEqual([k for k in keys if not belongs(k)], [], name)
            covered |= keys
        missing = sorted(want - covered)
        if missing:
            self.fail("\n".join(["re-render %s" % k for k in missing] + ["with: " + REFRESH]))


class TestHashBinding(unittest.TestCase):
    def test_every_fence_matches_its_entry(self):
        stale = []
        for data in FIXTURES.values():
            for key, record in sorted((data or {}).get("files", {}).items()):
                path = SKILL / key
                if not path.is_file():
                    stale.append("re-render %s (the file is gone)" % key)
                    continue
                found = {line: sha for line, sha, _ in fence_texts(path)}
                for line, sha in sorted(found.items()):
                    if entry_for(record, line, sha) is None:
                        stale.append("re-render %s:%d" % (key, line))
                held = set(found.values())
                for line, entry in sorted(record["figures"].items(), key=lambda kv: int(kv[0])):
                    if entry.get("sha256") not in held:
                        stale.append("re-render %s:%s (no fence holds this text)" % (key, line))
        if stale:
            self.fail("\n".join(stale + ["with: " + REFRESH]))

    def test_negative_flags_match_the_fences(self):
        wrong = []
        for data in FIXTURES.values():
            for key, record in sorted((data or {}).get("files", {}).items()):
                path = SKILL / key
                if not path.is_file():
                    continue
                for line, sha, body in fence_texts(path):
                    entry = entry_for(record, line, sha)
                    if entry is None:
                        continue
                    names = rc.negative_names(body)
                    if (entry["negative"], entry["negative_names"]) != (names is not None, names or []):
                        wrong.append("re-render %s:%d" % (key, line))
        if wrong:
            self.fail("\n".join(wrong))


class TestStoredVerdicts(unittest.TestCase):
    def test_every_entry_holds_the_required_renders(self):
        missing = ["%s:%s lacks %s" % (key, line, label)
                   for key, line, entry in entries() for label in REQUIRED
                   if label not in entry["renders"]]
        if missing:
            self.fail("\n".join(missing))

    def test_positive_figures_pass_every_render(self):
        failures = []
        for key, line, entry in entries():
            if entry["negative"]:
                continue
            for label in REQUIRED:
                r = entry["renders"].get(label)
                if r is None:
                    continue  # reported by test_every_entry_holds_the_required_renders
                if r["status"] != "ok":
                    failures.append("%s:%s %s: %s %s" % (key, line, label, r["status"],
                                                         r.get("error") or ""))
                    continue
                fails = [f for f in sg.evaluate(r["metrics"], NOTATION) if f["severity"] == "fail"]
                if fails:
                    failures.append("%s:%s %s: %s" % (key, line, label, "; ".join(
                        "%s: %s" % (f["check"], f["message"]) for f in fails)))
        if failures:
            self.fail("\n".join(failures))

    def test_negative_figures_fail_a_named_render_check(self):
        broken = []
        for key, line, entry in entries():
            named = [x for x in entry["negative_names"] if x in sg.GATE_CHECKS]
            if not entry["negative"] or not named:
                continue
            fired = {check for r in entry["renders"].values() if r["status"] == "ok"
                     for check in named if sg.fired(sg.evaluate(r["metrics"], NOTATION), check)}
            if not fired:
                broken.append("%s:%s names %s; none fails in any render"
                              % (key, line, ", ".join(named)))
        if broken:
            self.fail("\n".join(broken))

    def test_negative_figures_fail_only_the_render_checks_they_name(self):
        # STI-01: a marker excuses the render checks it names, and no other
        unnamed = []
        for key, line, entry in entries():
            if not entry["negative"]:
                continue
            for label in REQUIRED:
                r = entry["renders"].get(label)
                if r is not None and r["status"] in ("parse_error", "render_error") \
                        and not rc.names_parse_check(entry["negative_names"]):
                    unnamed.append("%s:%s %s: %s, and its marker names no parse check"
                                   % (key, line, label, r["status"]))
                if r is None or r["status"] != "ok":
                    continue
                extra = sorted({f["check"] for f in sg.evaluate(r["metrics"], NOTATION)
                                if f["severity"] == "fail"} - set(entry["negative_names"]))
                if extra:
                    unnamed.append("%s:%s %s fails %s, which its marker does not name"
                                   % (key, line, label, ", ".join(extra)))
        if unnamed:
            self.fail("\n".join(unnamed))

    def test_entries_record_their_renderers(self):
        pins = NOTATION["renderers"]["installs"]
        wrong = []
        for key, line, entry in entries():
            for label, r in entry["renders"].items():
                tag = label.split("-")[0]
                if r["status"] in ("ok", "parse_error", "render_error"):
                    pin = pins.get(tag, {})
                    if r.get("mermaid") != pin.get("mermaid"):
                        wrong.append("%s:%s %s rendered with mermaid %s" % (key, line, label, r.get("mermaid")))
                    if r.get("mermaid_cli") != pin.get("cli"):
                        wrong.append("%s:%s %s rendered with mermaid-cli %s" % (key, line, label,
                                                                                r.get("mermaid_cli")))
                if r["status"] == "ok" and not r.get("browser"):
                    wrong.append("%s:%s %s records no browser" % (key, line, label))
        if wrong:
            self.fail("\n".join(wrong + ["with: " + REFRESH]))

    def test_evidence_was_measured_by_the_current_instruments(self):
        # a changed column, dark page or instrument leaves the stored metrics measuring
        # something the check no longer does
        instruments = rc.instrument_sha256()
        settings = rc.render_settings(NOTATION)
        stale = []
        for data in FIXTURES.values():
            for key, record in sorted((data or {}).get("files", {}).items()):
                if record.get("instruments") != instruments:
                    stale.append("re-render %s (measured by other instruments than the current %s)"
                                 % (key, ", ".join(rc.INSTRUMENT_FILES)))
                elif record.get("settings") != settings:
                    stale.append("re-render %s (measured under %s; notation.json now gives %s)"
                                 % (key, json.dumps(record.get("settings")), json.dumps(settings)))
        if stale:
            self.fail("\n".join(stale + ["with: " + REFRESH]))


if __name__ == "__main__":
    unittest.main()
