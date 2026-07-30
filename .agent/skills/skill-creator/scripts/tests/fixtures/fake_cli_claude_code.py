#!/usr/bin/env python3
"""Test double for ONE vendor CLI: Claude Code's `claude -p` stream-json protocol.

Named for the PROTOCOL, not the concept. What is vendor-specific here is only the
wire format — the event names (`stream_event`, `content_block_start`,
`input_json_delta`) and the turn structure. A Gemini/Codex/Cursor harness that grew
a trigger probe would need its own fixture beside this one and its own
`TriggerScanner.feed`, but would REUSE the vendor-neutral half of the detector
(`normalize_skill_ref`, `match_skill_ref`, `match_read_path`, `classify_tool_use`),
which knows nothing about any CLI. That seam is deliberate; see
`run_eval.TriggerScanner` and the sibling adapter precedent in
`.agent/skills/skill-parallel-orchestration/references/<vendor>.md`.

Zero tokens, no API key.

The event SHAPES here are not invented — they were taken from a real
`claude -p --output-format stream-json --include-partial-messages` capture, which
established two facts the VAL-2 record does not mention and that a fixture built
from imagination would have missed:

  * a `thinking` content block ALWAYS precedes the tool_use block, so any detector
    keying on "the first content block" is wrong;
  * a turn spans SEVERAL message_start/message_stop pairs, so `message_stop` is not
    end-of-turn and a tool call can follow a tool RESULT in the next message.

Driven by two env vars so tests stay deterministic under parallel execution:
FAKE_CLAUDE_SCENARIO picks the script, FAKE_PROBE_NAME supplies the probe clone
name (never globbed from disk — globbing races when suites run concurrently).
"""
import json, os, sys
def emit(o): sys.stdout.write(json.dumps(o) + "\n"); sys.stdout.flush()
def se(ev): emit({"type": "stream_event", "event": ev})
def thinking():
    se({"type": "content_block_start", "index": 0,
        "content_block": {"type": "thinking"}})
    se({"type": "content_block_delta", "index": 0,
        "delta": {"type": "thinking_delta", "thinking": "considering"}})
    se({"type": "content_block_stop", "index": 0})
def tool(name, payload, tid="toolu_x"):
    se({"type": "content_block_start", "index": 1,
        "content_block": {"type": "tool_use", "id": tid, "name": name, "input": {}}})
    se({"type": "content_block_delta", "index": 1,
        "delta": {"type": "input_json_delta", "partial_json": json.dumps(payload)}})
    se({"type": "content_block_stop", "index": 1})
def msg_end(): se({"type": "message_delta", "delta": {}}); se({"type": "message_stop"})
probe = os.environ["FAKE_PROBE_NAME"]; s = os.environ.get("FAKE_CLAUDE_SCENARIO", "")
se({"type": "message_start"}); thinking()
if s == "probe_first": tool("Skill", {"skill": probe})
elif s == "bash_then_probe":
    tool("Bash", {"command": "ls"}, "t1"); tool("Skill", {"skill": probe}, "t2")
elif s == "real_name_first": tool("Skill", {"skill": "run-feedback"})
elif s == "read_real_skill": tool("Read", {"file_path": ".agent/skills/run-feedback/SKILL.md"})
elif s == "other_skill": tool("Skill", {"skill": "some-unrelated-skill"})
elif s == "clone_superstring": tool("Skill", {"skill": probe + "-extra"})
elif s == "args_echo_clone": tool("Skill", {"skill": "brainstorming", "args": "how should %s work" % probe})
elif s == "read_path_contains": tool("Read", {"file_path": "docs/backlog/rf-1-%s-notes.md" % probe})
elif s == "next_message":
    tool("Bash", {"command": "ls"}, "t1"); msg_end()
    se({"type": "message_start"}); thinking(); tool("Skill", {"skill": probe}, "t2")
elif s == "budget_exceeded":
    for i in range(10): tool("Bash", {"command": "ls %d" % i}, "t%d" % i)
    tool("Skill", {"skill": probe}, "tlast")
elif s == "plugin_scoped": tool("Skill", {"skill": "myplugin:run-feedback"})
elif s == "fast_exit_eof": pass
msg_end()
if s == "fast_exit_eof":
    emit({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": "ta", "name": "Skill", "input": {"skill": probe}}]}})
emit({"type": "result", "subtype": "success"})
