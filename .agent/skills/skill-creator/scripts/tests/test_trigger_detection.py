"""Regression tests for VAL-2 — run_eval.py trigger-probe false negatives.

VAL-2 reported two mechanisms; reproducing it turned up three more, and the fix has
to WIDEN what counts while TIGHTENING how it matches. Both directions are tested
here, because doing only the first is what would turn a false-negative defect into
a false-positive one:

  widen   (1) the REAL skill name counts, not only the uuid-suffixed probe clone —
              when the skill is installed the model rationally invokes the canonical
              name, which scored "not triggered"
          (2) a non-Skill/Read first tool call no longer aborts the scan
          (3) `message_stop` no longer ends the scan (found by recording a real
              stream: a turn is SEVERAL messages, so the skill call can follow a
              Bash call in the next message)
          (4) the final read at child exit is parsed instead of discarded

  tighten (5) EXACT name matching, never substring — the old `in` test already
              scored `Skill(skill="<clone>-extra")` and, worse,
              `Skill(skill="brainstorming", args="...<clone>...")` as triggers: a
              DIFFERENT skill counted as a trigger, which the record's own "Do-not"
              forbids
          (6) `Skill.args` is never inspected; only the name-bearing key
          (7) a `Read` counts only when it loads SKILL.md or the probe command file,
              not merely when the path contains the name

Two layers. Layer 1 tests the pure helpers with no subprocess at all. Layer 2 spawns
`run_single_query` against a fake `claude` on PATH — zero tokens, no API key — which
is the only way to test the stream state machine that actually broke.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import run_eval  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PROBE = "run-feedback-skill-deadbeef"
REAL = "run-feedback"
ACCEPTED = frozenset({PROBE, REAL})


# --- Layer 1: the pure helpers ---------------------------------------------

class TestMatchSkillRef(unittest.TestCase):
    def test_exact_names_match(self):
        self.assertEqual(run_eval.match_skill_ref(PROBE, ACCEPTED), PROBE)
        self.assertEqual(run_eval.match_skill_ref(REAL, ACCEPTED), REAL)

    def test_a_superstring_does_not_match(self):
        """The old substring test scored this True — a different skill whose name
        merely CONTAINS ours. Live examples exist: `wiki-query` inside
        `wiki-query-synthesis`."""
        for value in (PROBE + "-extra", REAL + "-synthesis", "x" + REAL):
            with self.subTest(value=value):
                self.assertIsNone(run_eval.match_skill_ref(value, ACCEPTED))

    def test_plugin_and_directory_scoped_names_normalize(self):
        for value in ("myplugin:" + REAL, "apps/web:" + REAL, "/" + REAL,
                      REAL + ".md"):
            with self.subTest(value=value):
                self.assertEqual(run_eval.match_skill_ref(value, ACCEPTED), REAL)

    def test_empty_and_none_never_match(self):
        for value in (None, "", "   ", ":"):
            with self.subTest(value=value):
                self.assertIsNone(run_eval.match_skill_ref(value, ACCEPTED))


class TestMatchReadPath(unittest.TestCase):
    def test_reading_the_skill_definition_counts(self):
        for path in (".agent/skills/run-feedback/SKILL.md",
                     "/abs/.claude/skills/run-feedback/SKILL.md",
                     r".claude\skills\run-feedback\SKILL.md"):
            with self.subTest(path=path):
                self.assertEqual(run_eval.match_read_path(path, ACCEPTED), REAL)

    def test_reading_the_probe_command_file_counts(self):
        self.assertEqual(
            run_eval.match_read_path(".claude/commands/%s.md" % PROBE, ACCEPTED),
            PROBE)

    def test_a_path_that_merely_contains_the_name_does_not_count(self):
        """Proven false positive of the old `clean_name in file_path` test."""
        for path in ("docs/backlog/rf-1-%s-notes.md" % PROBE,
                     "docs/issues/%s-thing.md" % REAL,
                     ".agent/skills/run-feedback/references/cli_reference.md"):
            with self.subTest(path=path):
                self.assertIsNone(run_eval.match_read_path(path, ACCEPTED))

    def test_an_unrelated_skill_md_does_not_count(self):
        self.assertIsNone(
            run_eval.match_read_path(".agent/skills/brainstorming/SKILL.md",
                                     ACCEPTED))


class TestClassifyToolUse(unittest.TestCase):
    def test_skill_args_are_never_inspected(self):
        """The old code tested the whole accumulated input JSON, so a call to a
        DIFFERENT skill that merely quoted our name scored as a trigger — the
        record's "Do-not" verbatim."""
        self.assertIsNone(run_eval.classify_tool_use(
            "Skill", {"skill": "brainstorming", "args": "how should %s work" % PROBE},
            ACCEPTED))

    def test_every_other_tool_is_neutral(self):
        """Neutral means: not a trigger, and not a reason to abort the scan."""
        for tool in ("Bash", "Grep", "Glob", "Write", "Task", "TodoWrite"):
            with self.subTest(tool=tool):
                self.assertIsNone(run_eval.classify_tool_use(
                    tool, {"command": PROBE, "pattern": REAL}, ACCEPTED))

    def test_slash_command_is_accepted(self):
        self.assertEqual(run_eval.classify_tool_use(
            "SlashCommand", {"command": "/%s some args" % REAL}, ACCEPTED), REAL)

    def test_a_non_dict_input_does_not_raise(self):
        self.assertIsNone(run_eval.classify_tool_use("Skill", None, ACCEPTED))


class TestTriggerScannerStateMachine(unittest.TestCase):
    """The state machine, fed events directly — no subprocess."""

    def _scan(self, events):
        scanner = run_eval.TriggerScanner(ACCEPTED)
        for event in events:
            if scanner.feed(event):
                break
        return scanner.verdict()

    @staticmethod
    def _tool(name, payload, tid):
        return [
            {"type": "stream_event", "event": {
                "type": "content_block_start",
                "content_block": {"type": "tool_use", "id": tid, "name": name}}},
            {"type": "stream_event", "event": {
                "type": "content_block_delta",
                "delta": {"type": "input_json_delta",
                          "partial_json": json.dumps(payload)}}},
            {"type": "stream_event", "event": {"type": "content_block_stop"}},
        ]

    def test_a_thinking_block_is_not_decisive(self):
        events = [
            {"type": "stream_event", "event": {
                "type": "content_block_start",
                "content_block": {"type": "thinking"}}},
            {"type": "stream_event", "event": {"type": "content_block_stop"}},
        ] + self._tool("Skill", {"skill": PROBE}, "t1")
        self.assertTrue(self._scan(events)[0])

    def test_message_stop_does_not_end_the_scan(self):
        """A real turn has several message_stop events; treating the first as
        end-of-turn is a false-negative mechanism the record does not name."""
        events = (self._tool("Bash", {"command": "ls"}, "t1")
                  + [{"type": "stream_event", "event": {"type": "message_stop"}}]
                  + self._tool("Skill", {"skill": PROBE}, "t2"))
        triggered, matched, reason = self._scan(events)
        self.assertTrue(triggered)
        self.assertEqual(matched, PROBE)

    def test_result_ends_the_scan(self):
        events = self._tool("Bash", {"command": "ls"}, "t1") + [{"type": "result"}]
        triggered, _, reason = self._scan(events)
        self.assertFalse(triggered)
        self.assertEqual(reason, run_eval.REASON_NO_TRIGGER)

    def test_the_tool_budget_is_enforced(self):
        events = []
        for i in range(run_eval.MAX_TOOL_CALLS_SCANNED + 2):
            events += self._tool("Bash", {"command": "ls %d" % i}, "t%d" % i)
        events += self._tool("Skill", {"skill": PROBE}, "late")
        triggered, _, reason = self._scan(events)
        self.assertFalse(triggered)
        self.assertEqual(reason, run_eval.REASON_BUDGET)

    def test_the_budget_is_not_double_counted_across_both_surfaces(self):
        """The same call is observed by the stream path AND the assistant
        fallback; counting it twice would halve the effective budget."""
        scanner = run_eval.TriggerScanner(ACCEPTED)
        for event in self._tool("Bash", {"command": "ls"}, "shared-id"):
            scanner.feed(event)
        scanner.feed({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "shared-id", "name": "Bash",
             "input": {"command": "ls"}}]}})
        self.assertEqual(scanner.tool_calls_seen, 1)

    def test_the_assistant_fallback_scans_every_item(self):
        """The old fallback `return`ed after the FIRST tool_use item."""
        scanner = run_eval.TriggerScanner(ACCEPTED)
        scanner.feed({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "a", "name": "Bash", "input": {}},
            {"type": "tool_use", "id": "b", "name": "Skill",
             "input": {"skill": PROBE}}]}})
        self.assertTrue(scanner.verdict()[0])

    def test_malformed_tool_input_is_a_non_match_not_an_abort(self):
        events = [
            {"type": "stream_event", "event": {
                "type": "content_block_start",
                "content_block": {"type": "tool_use", "id": "t1", "name": "Skill"}}},
            {"type": "stream_event", "event": {
                "type": "content_block_delta",
                "delta": {"type": "input_json_delta", "partial_json": '{"ski'}}},
            {"type": "stream_event", "event": {"type": "content_block_stop"}},
        ] + self._tool("Skill", {"skill": PROBE}, "t2")
        self.assertTrue(self._scan(events)[0])


# --- Layer 2: end to end against a fake `claude` ---------------------------

@unittest.skipUnless(FIXTURES.joinpath("fake_cli_claude_code.py").exists(),
                     "fake claude fixture missing")
class TestRunSingleQueryEndToEnd(unittest.TestCase):
    """Spawns the real `run_single_query` with a fake `claude` on PATH.

    Zero tokens and no API key: the fixture replays shapes recorded from an actual
    stream. This is the only layer that exercises the subprocess plumbing, the EOF
    drain, and the kill/exit classification.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / ".claude" / "commands").mkdir(parents=True)
        self.bindir = self.root / "bin"
        self.bindir.mkdir()
        link = self.bindir / "claude"
        link.write_text(FIXTURES.joinpath("fake_cli_claude_code.py").read_text())
        link.chmod(0o755)

    def run_scenario(self, scenario):
        env = dict(os.environ)
        env["PATH"] = "%s:%s" % (self.bindir, env.get("PATH", ""))
        env["FAKE_CLAUDE_SCENARIO"] = scenario
        env["FAKE_PROBE_NAME"] = PROBE
        code = (
            "import sys, json; sys.path.insert(0, %r);\n"
            "import run_eval;\n"
            "run_eval.uuid = type('U', (), {'uuid4': staticmethod("
            "lambda: type('H', (), {'hex': 'deadbeef00'})())});\n"
            "print(json.dumps(run_eval.run_single_query("
            "'q', %r, 'desc', 20, %r, None)))" % (str(SCRIPTS), REAL, str(self.root))
        )
        out = subprocess.run([sys.executable, "-c", code], capture_output=True,
                             text=True, env=env, cwd=str(self.root))
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout.strip().splitlines()[-1])

    # --- the widening half: each was a FALSE NEGATIVE before the fix -------

    def test_probe_invoked_first(self):
        r = self.run_scenario("probe_first")
        self.assertTrue(r["triggered"])
        self.assertEqual(r["matched"], "probe")

    def test_bash_before_the_probe_still_counts(self):
        """VAL-2 mechanism 2."""
        self.assertTrue(self.run_scenario("bash_then_probe")["triggered"])

    def test_the_real_skill_name_counts(self):
        """VAL-2 mechanism 1: the model invokes the installed canonical name."""
        r = self.run_scenario("real_name_first")
        self.assertTrue(r["triggered"])
        self.assertEqual(r["matched"], "canonical")

    def test_reading_the_real_skill_md_counts(self):
        r = self.run_scenario("read_real_skill")
        self.assertTrue(r["triggered"])
        self.assertEqual(r["matched"], "canonical")

    def test_a_call_in_the_next_message_counts(self):
        """The third mechanism, from a recorded real stream."""
        self.assertTrue(self.run_scenario("next_message")["triggered"])

    def test_a_plugin_scoped_name_counts(self):
        self.assertTrue(self.run_scenario("plugin_scoped")["triggered"])

    def test_events_in_the_final_read_are_not_discarded(self):
        """The old EOF path appended the last chunk and then `break`ed out BEFORE
        the parse loop, throwing away every event it had just read."""
        self.assertTrue(self.run_scenario("fast_exit_eof")["triggered"])

    # --- the tightening half: each must remain a NON-trigger ---------------

    def test_an_unrelated_skill_is_not_a_trigger(self):
        r = self.run_scenario("other_skill")
        self.assertFalse(r["triggered"])
        self.assertEqual(r["reason"], run_eval.REASON_NO_TRIGGER,
                         "a non-trigger must be a DECISION, not a crash")

    def test_a_superstring_skill_name_is_not_a_trigger(self):
        self.assertFalse(self.run_scenario("clone_superstring")["triggered"])

    def test_a_name_quoted_in_args_is_not_a_trigger(self):
        self.assertFalse(self.run_scenario("args_echo_clone")["triggered"])

    def test_a_path_merely_containing_the_name_is_not_a_trigger(self):
        self.assertFalse(self.run_scenario("read_path_contains")["triggered"])

    def test_exceeding_the_budget_reports_its_own_reason(self):
        """Distinguishable from a clean non-trigger, so a run that is really the
        instrument giving up cannot be read as a description result."""
        r = self.run_scenario("budget_exceeded")
        self.assertFalse(r["triggered"])
        self.assertEqual(r["reason"], run_eval.REASON_BUDGET)

    def test_the_probe_command_file_is_always_cleaned_up(self):
        self.run_scenario("probe_first")
        self.assertEqual(
            list((self.root / ".claude" / "commands").glob("*.md")), [],
            "the probe command file leaked into the project")


if __name__ == "__main__":
    unittest.main()
