"""The human channel: reports and `--help` survive a non-UTF-8 locale.

The defect: stderr is opened errors="backslashreplace" and survives, but stdout
gets "surrogateescape" (or "strict" under an explicit PYTHONIOENCODING), and
neither can represent an em dash — surrogateescape rescues lone surrogates and
nothing else. One `—` or `✓` in a report, or in an argparse `help=` string,
took the whole command down.

Measured before the fix: `analyze_gaps.py <skill>` returned 54 bytes where UTF-8 returned 1373.

The contract is OBEY the caller's codec, not ignore it. Writing UTF-8 into a
terminal that declared cp1252 is mojibake, not robustness — so the fix degrades
per character and leaves a working machine's bytes untouched.

The fix lives on the STREAM (`codecs.register_error` + `reconfigure(errors=)`),
not at the call sites, so these tests are in two halves: the handler's own
behaviour, and — the half that actually catches regressions — proof that every
command in this skill installs it.

Issue: docs/issues/human-cli-output-locale-class.md
"""

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _load(filename, name):
    """Import a script by path, registered in sys.modules.

    Registration is not optional: a module that resolves string annotations at
    import time (dataclasses, typing.get_type_hints) looks itself up there and
    dies with `'NoneType' object has no attribute '__dict__'` without it.
    """
    loader = importlib.machinery.SourceFileLoader(name, str(SCRIPTS / filename))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


H = _load("skill_utils.py", "skill_enhancer_skill_utils")

GLYPHS = {"—": "--", "…": "...", "→": "->", "✓": "+", "✗": "x", "⚠": "!", "§": "S"}


def _degrade(text, encoding="ascii"):
    """What this skill's reports look like under `encoding`.

    Goes through the registered handler rather than restating the table, so a
    test cannot drift from the code by describing a spelling the code does not
    produce.
    """
    return text.encode(encoding, H.HUMAN_ERRORS).decode(encoding)


def _strict(encoding):
    return io.TextIOWrapper(io.BytesIO(), encoding=encoding, errors="strict")


class TestTheHandler(unittest.TestCase):
    """`_asciify` in isolation. Registered under `HUMAN_ERRORS`, so it is
    reachable as an ordinary `errors=` argument — which is how every
    expectation below is written."""

    def test_a_codec_that_copes_is_not_consulted_at_all(self):
        """The UTF-8 case — nearly every real run. The handler only fires on a
        character the codec rejects, so a working machine's bytes are the same
        bytes they always were."""
        text = "доклад — ECMA §2 [✓] [✗] → café"
        self.assertEqual(_degrade(text, "utf-8"), text)

    def test_every_glyph_has_an_ascii_spelling(self):
        for glyph, expected in GLYPHS.items():
            with self.subTest(glyph=glyph):
                self.assertEqual(_degrade(glyph), expected)

    def test_an_emoji_variation_selector_is_dropped_not_escaped(self):
        """`⚠️` is U+26A0 U+FE0F — one grapheme, two code points. Mapping only
        the base glyph left the selector to backslashreplace and the report
        read `!\\ufe0f`; measured on `validate_skill.py skills/docx`. A
        variation selector carries no meaning of its own, so the correct
        degradation is to drop it."""
        self.assertEqual(_degrade("⚠️"), "!")
        self.assertEqual(_degrade("✅ ok"), "+ ok")
        self.assertNotIn(r"\u", _degrade("⚠️ ✅ ❌"))

    def test_a_multi_character_run_is_spelled_per_character(self):
        """The codec hands the handler a RUN, not a character: `exc.start` to
        `exc.end` covers every consecutive unencodable position. A handler that
        looked up `exc.object[exc.start]` alone would silently drop the rest of
        the run, and a report of `— ✓ →` is exactly such a run."""
        self.assertEqual(_degrade("—✓→"), "--+->")
        self.assertEqual(_degrade("a—✓→b"), "a--+->b")

    def test_degradation_is_per_character_under_a_partial_codec(self):
        """A codec must keep everything it CAN represent. cp1251 has Cyrillic
        and an em dash; it lacks a check mark. Only the check mark may move."""
        got = _degrade("доклад — ✓", "cp1251")
        self.assertEqual(got, "доклад — +")
        got.encode("cp1251")

    def test_anything_absent_from_the_table_falls_back_to_an_escape(self):
        """The table is a courtesy; `backslashreplace` is the guarantee. CJK
        has no ASCII spelling and must not be dropped silently."""
        # Raw string, spelled out: written as a normal literal this would BE
        # the CJK characters, which ASCII-decoded text can never contain — a
        # vacuously passing test.
        self.assertEqual(_degrade("日本語"), r"\u65e5\u672c\u8a9e")

    def test_the_result_always_encodes(self):
        cases = {"cyrillic": "Привет", "latin1": "café", "astral": "\U0001F600",
                 "cjk": "日本語", "lone surrogate": "/tmp/out\udcff.md"}
        for label, text in cases.items():
            for enc in ("ascii", "cp1251", "cp1252", "utf-8", "latin-1"):
                with self.subTest(text=label, encoding=enc):
                    _degrade(text, enc).encode(enc)

    def test_a_lone_surrogate_survives_even_under_utf8(self):
        """UTF-8 is the one codec with no representation for U+DC80-DCFF, and
        POSIX puts them into str(path) via surrogateescape. So this crashed on
        a correctly configured machine."""
        path = "/tmp/out\udcff.md"
        with self.assertRaises(UnicodeEncodeError):
            path.encode("utf-8")
        self.assertEqual(_degrade(path, "utf-8"), "/tmp/out\\udcff.md")

    def test_a_decode_error_is_re_raised_rather_than_guessed_at(self):
        """Installed on a readable stream the handler would be asked to invent
        input, not to tidy output. Refuse: corrupting what was read is worse
        than failing to read it."""
        with self.assertRaises(UnicodeDecodeError):
            b"\xe2\x80\x94".decode("ascii", H.HUMAN_ERRORS)


class TestInstallHumanChannel(unittest.TestCase):
    def test_it_points_the_stream_at_the_handler(self):
        stream = _strict("ascii")
        H.install_human_channel(stream)
        self.assertEqual(stream.errors, H.HUMAN_ERRORS)
        stream.write("report — готово ✓\n")
        stream.flush()
        # Cyrillic has no ASCII spelling, so it takes the backslashreplace
        # backstop; the em dash and the check mark have one and take it.
        self.assertEqual(
            stream.buffer.getvalue().decode("ascii"),
            r"report -- \u0433\u043e\u0442\u043e\u0432\u043e +" + "\n")

    def test_a_stream_that_cannot_be_reconfigured_is_not_an_error(self):
        """A test's StringIO, a capture proxy, `prog >&-` leaving sys.stdout as
        None. None of that is a reason to fail a report."""
        for sink in (io.StringIO(), None, object()):
            with self.subTest(sink=type(sink).__name__):
                H.install_human_channel(sink)

    def test_it_leaves_the_encoding_alone(self):
        """The whole distinction this fix rests on. `reconfigure(encoding=)`
        would override the caller's codec and produce mojibake in a cp1252
        terminal; `reconfigure(errors=)` changes only what happens to a
        character that codec cannot represent."""
        stream = _strict("cp1251")
        H.install_human_channel(stream)
        self.assertEqual(stream.encoding, "cp1251")
        stream.write("доклад — ✓\n")
        stream.flush()
        self.assertEqual(stream.buffer.getvalue().decode("cp1251"), "доклад — +\n")


class TestArgparseNeedsNoSubclass(unittest.TestCase):
    """`--help` was 31 of the 102 measured findings, and the skill's own code
    never does that writing — argparse does, with a bare `file.write`. Its
    guard catches AttributeError and OSError but not UnicodeEncodeError.

    The earlier fix subclassed ArgumentParser to intercept `_print_message`.
    With the handler on the stream the stock class is already safe, and these
    tests exist to keep that claim honest rather than assumed."""

    def _parser(self):
        p = argparse.ArgumentParser(prog="demo", description="Report — §2")
        p.add_argument("--x", help="does a thing → fast")
        return p

    def test_stock_argparse_help_reaches_a_strict_ascii_stream(self):
        stream = _strict("ascii")
        H.install_human_channel(stream)
        self._parser().print_help(stream)
        stream.flush()
        text = stream.buffer.getvalue().decode("ascii")
        self.assertIn("Report -- S2", text)
        self.assertIn("does a thing -> fast", text)

    def test_the_same_help_is_untouched_when_the_codec_copes(self):
        stream = _strict("utf-8")
        H.install_human_channel(stream)
        self._parser().print_help(stream)
        stream.flush()
        self.assertIn("Report — §2", stream.buffer.getvalue().decode("utf-8"))

    def test_a_subcommands_help_is_covered_by_the_same_stream(self):
        """Subparsers needed a dedicated argument under the old fix (the class
        had to be inherited). Under this one they are not a special case at
        all: there is no class to inherit, only a stream they all write to."""
        sub = self._parser().add_subparsers().add_parser("go", description="sub — prose")
        stream = _strict("ascii")
        H.install_human_channel(stream)
        sub.print_help(stream)
        stream.flush()
        self.assertIn(b"sub -- prose", stream.buffer.getvalue())


class TestEveryEntryPointInstallsIt(unittest.TestCase):
    """The regression test that matters.

    The old fix failed open: a `print` added later by someone who never read
    the helper silently reintroduced the crash, and mutation testing caught
    exactly that. This one fails open differently — a NEW CLI that forgets
    `install_human_channel()` — so the failure mode is enumerable, and this
    walks the enumeration instead of trusting a list someone has to maintain.
    """

    SKILL = SCRIPTS

    def _clis(self):
        """Every Python CLI in this skill, found rather than listed.

        Two traps this walk has already fallen into, both caught by
        `test_there_is_something_to_check` rather than by review:

        * matching on the literal string `"--help"` found NOTHING in
          skill-auto-improve — argparse adds -h/--help itself, so an ordinary
          CLI never mentions it;
        * globbing `*.py` found nothing in design-md, whose user-facing
          commands are deliberately EXTENSIONLESS (`lint`, `check-contrast`)
          because a `html.py` on `scripts/` would shadow a stdlib module.
        """
        found = []
        for path in sorted(self.SKILL.rglob("*")):
            parts = set(path.parts)
            if parts & {".venv", "__pycache__", "node_modules", "tests", "fixtures"}:
                continue
            if not path.is_file():
                continue
            if path.suffix and path.suffix != ".py":
                continue
            if path.stat().st_size > 2_000_000:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if not path.suffix and not text.startswith("#!"):
                continue
            if not (path.suffix or "python" in text.split("\n", 1)[0]):
                continue
            if "__main__" in text and "ArgumentParser" in text:
                found.append(path)
        return found

    def test_there_is_something_to_check(self):
        """Guards the walk: an rglob that silently matches nothing would make
        every assertion below vacuous."""
        self.assertTrue(self._clis(), "no CLI scripts found under %s" % self.SKILL)

    def test_every_cli_help_survives_an_ascii_locale(self):
        env = dict(os.environ)
        env.update(PYTHONIOENCODING="ascii", PYTHONUTF8="0", LC_ALL="C")
        for path in self._clis():
            with self.subTest(cli=path.name):
                utf8 = subprocess.run(
                    [sys.executable, str(path), "--help"], timeout=120,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if not utf8.stdout:
                    self.skipTest("%s prints no help here" % path.name)
                got = subprocess.run(
                    [sys.executable, str(path), "--help"], env=env, timeout=120,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.assertNotIn(b"UnicodeEncodeError", got.stderr,
                                 "%s does not install the human channel" % path)
                self.assertTrue(got.stdout, "%s produced no help" % path)


class TestTheRealCommands(unittest.TestCase):
    """`--help` above is the cheap half. These run the report paths, where the
    non-ASCII usually comes from user data rather than a literal."""

    CWD = Path(__file__).resolve().parents[4]
    COMMANDS = {
        "analyze_gaps.py": ["skills/skill-enhancer/scripts/analyze_gaps.py",
                            "skills/text-humanizer"],
    }

    def _require(self, argv):
        """Skip rather than silently test something else.

        These skills are consumed through a symlink from other checkouts, where
        `CWD` resolves somewhere with a different layout. A command whose
        target is absent there still RUNS — it just takes its own "not found"
        branch, and every assertion below then passes on that instead of on the
        report.

        argv[0] is always the script; beyond it only arguments that LOOK like
        paths are checked, so a bare value token is not mistaken for a file.
        """
        for arg in [argv[0]] + [a for a in argv[1:] if "/" in a]:
            if not (self.CWD / arg).exists():
                self.skipTest("%s is absent under %s" % (arg, self.CWD))

    def _run(self, argv, ascii_locale):
        env = dict(os.environ)
        if ascii_locale:
            env.update(PYTHONIOENCODING="ascii", PYTHONUTF8="0", LC_ALL="C")
        else:
            env.update(PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        return subprocess.run([sys.executable] + argv, cwd=str(self.CWD),
                              env=env, timeout=180,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_every_documented_command_survives_an_ascii_locale(self):
        for label, argv in self.COMMANDS.items():
            with self.subTest(command=label):
                self._require(argv)
                utf8 = self._run(argv, ascii_locale=False)
                if utf8.returncode != 0 and not utf8.stdout:
                    self.skipTest("%s does not run in this environment" % label)
                got = self._run(argv, ascii_locale=True)
                self.assertNotIn(b"UnicodeEncodeError", got.stderr,
                                 "%s still dies on its own prose" % label)
                self.assertEqual(got.returncode, utf8.returncode,
                                 "%s changed its verdict with the locale" % label)
                self.assertTrue(got.stdout, "%s produced no report" % label)

    def test_the_ascii_report_is_exactly_the_utf8_report_degraded(self):
        """The strongest form of the contract.

        Every other test here can pass while one output path bypasses the
        configured stream — writing to a `subprocess` handle, a freshly opened
        file wrapper, a stream captured before `install_human_channel` ran. This
        one compares the whole report against the handler applied to the UTF-8
        run, so a path that did NOT go through the configured stream shows up
        as a difference whether or not it would have crashed.
        """
        for label, argv in self.COMMANDS.items():
            with self.subTest(command=label):
                self._require(argv)
                utf8 = self._run(argv, ascii_locale=False)
                if not utf8.stdout:
                    self.skipTest("%s produces no report in this environment" % label)
                got = self._run(argv, ascii_locale=True)
                self.assertEqual(got.stdout.decode("ascii"),
                                 _degrade(utf8.stdout.decode("utf-8")),
                                 "%s: the ascii run is not the utf-8 run degraded"
                                 % label)


class TestTheMachineChannelIgnoresTheLocale(unittest.TestCase):
    """The opposite contract, in the same file, on purpose.

    Everything above obeys the caller's codec. `emit_json` must NOT: JSON is
    UTF-8 by RFC 8259 §8.1, and a consumer parsing this stream did not agree to
    read cp1251. `ensure_ascii` keeps its default so the document is pure ASCII
    and the text layer's codec can neither alter these bytes nor abort
    mid-write on them — which also means the human-channel handler installed on
    the same stream never fires for them.

    Here because the two contracts are one edit apart: flipping `ensure_ascii`
    to False makes the JSON follow the locale like prose, and no test of the
    human half would notice.
    """

    def _emit(self, payload, encoding):
        stream = io.TextIOWrapper(io.BytesIO(), encoding=encoding, errors="strict")
        H.install_human_channel(stream)
        saved = sys.stdout
        sys.stdout = stream
        try:
            H.emit_json(payload)
        finally:
            sys.stdout = saved
        stream.flush()
        return stream.buffer.getvalue()

    def test_the_bytes_are_the_same_under_every_locale(self):
        payload = {"note": "доклад — готово ✓", "path": "/tmp/café.md"}
        first = self._emit(payload, "utf-8")
        for encoding in ("ascii", "cp1251", "cp1252", "latin-1"):
            with self.subTest(encoding=encoding):
                self.assertEqual(self._emit(payload, encoding), first)

    def test_it_is_not_transliterated_like_prose(self):
        """`—` must stay `\u2014` in the document, not become `--`. The
        difference is the whole reason the two channels are separate: a parser
        round-trips the escape, and cannot round-trip `--`."""
        got = self._emit({"note": "доклад — ✓"}, "ascii").decode("ascii")
        self.assertIn(r"\u2014", got)
        self.assertNotIn("--", got)
        self.assertEqual(json.loads(got)["note"], "доклад — ✓")


class TestNonAsciiUserData(unittest.TestCase):
    """The half of this class that ASCII-only source code does not fix.

    44 of the 102 measured findings came from user DATA, not from literals: a
    path with Cyrillic in it, or a filename with `café`, kills a report whose
    own source is pure ASCII. Every other test here would pass on a build where
    the literals were scrubbed and nothing else changed, so this is the one
    that distinguishes the two.
    """

    REPO = Path(__file__).resolve().parents[4]
    TARGET = "skills/skill-enhancer/scripts/analyze_gaps.py"

    def _fixture(self):
        """A skill copied under a directory whose NAME is non-ASCII.

        The skill's own name stays ASCII on purpose: the validator requires it
        to match the directory, so the non-ASCII has to come from an ancestor
        — which is exactly how it arrives in real life, from the checkout path
        rather than from the skill.
        """
        tmp = tempfile.mkdtemp(prefix="human-channel-")
        self.addCleanup(shutil.rmtree, tmp, True)
        dst = Path(tmp) / "проект — café" / "skill-enhancer"
        shutil.copytree(self.REPO / "skills" / "skill-enhancer", dst,
                        ignore=shutil.ignore_patterns(".venv", "__pycache__",
                                                      "node_modules"))
        return dst

    def _run(self, target, ascii_locale):
        env = dict(os.environ)
        if ascii_locale:
            env.update(PYTHONIOENCODING="ascii", PYTHONUTF8="0", LC_ALL="C")
        else:
            env.update(PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        return subprocess.run([sys.executable, self.TARGET, str(target)],
                              cwd=str(self.REPO), env=env, timeout=180,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_a_non_ascii_path_does_not_take_the_report_down(self):
        target = self._fixture()
        utf8 = self._run(target, ascii_locale=False)
        got = self._run(target, ascii_locale=True)
        self.assertNotIn(b"UnicodeEncodeError", got.stderr)
        self.assertEqual(got.returncode, utf8.returncode)
        self.assertEqual(got.stdout.decode("ascii"),
                         _degrade(utf8.stdout.decode("utf-8")))

    def test_the_fixture_really_does_carry_non_ascii_into_the_output(self):
        """Guards the test above: if the command stopped echoing the path, the
        test would keep passing while covering nothing."""
        utf8 = self._run(self._fixture(), ascii_locale=False)
        self.assertIn("café", utf8.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
