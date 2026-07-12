---
id: HK-1
type: known-issue
status: documented
opened_at: 2026-07-13
category: hooks
slug: hk-1-posttooluse-fires-only-on-successful-tool-calls-cannot-capture-bash-failures
component: run-feedback
fingerprint: 8da25e67fded6863
finding_ref: fnd-20260713-022730-8da25e67
---

# HK-1 — PostToolUse fires only on successful tool calls — cannot capture Bash failures

> Verified live 2026-07-13 on Claude Code 2.1.207 (headless discriminator experiment:
> one succeeding + one failing Bash call in a fresh `claude -p` session with
> `RUN_FEEDBACK_HOOK_DEBUG=1`). Guidance shipped in
> `run-feedback/references/capture_surfaces.md` §B; mitigation = mine-on-session-end.

**Symptom.** A `PostToolUse` hook with `matcher: "Bash"` fires ONLY when the tool call
completes successfully. A Bash command exiting non-zero produces NO PostToolUse event at all,
and even for successful calls the `tool_response` payload
(`{stdout, stderr, interrupted, isImage, noOutputExpected}`) carries no exit-code field.
Per-command failure capture via PostToolUse is therefore impossible.

**Reproduction.**

```sh
cd <consumer-repo-with-run-feedback-hooks>
rm -f .agent/feedback/hook_debug-*.json
RUN_FEEDBACK_HOOKS=1 RUN_FEEDBACK_HOOK_DEBUG=1 claude -p \
  "Run these two bash commands one after another, then reply DONE: first \`echo hello-ok\`, second \`bash -c 'echo boom >&2; exit 3'\`" \
  --allowedTools "Bash" --model haiku
ls .agent/feedback/hook_debug-*.json   # exactly ONE dump — from `echo hello-ok` only
```

**Workaround.** Capture failures from the session transcript instead: `SessionEnd` fires
reliably (verified same experiment) and receives `transcript_path`; with
`RUN_FEEDBACK_MINE_ON_END=1` the `session_end_marker.py` hook auto-mines the just-ended
session (transcripts record failures as `tool_result {content: "Exit code N\n…", is_error: true}`,
which the shared extraction ladder parses).

**Fix path.** None on our side — external platform behavior. Re-test on Claude Code upgrades;
if a failure-carrying PostToolUse (or equivalent) event appears, `scripts/hooks/posttooluse_filter.py`
is kept + tested and can be re-wired into consumer `settings.json`.

**Related.** `run-feedback` SKILL.md §11, `references/capture_surfaces.md` §B,
`tests/test_hook_filter.py` (incl. `TestSessionEndMineOnEnd`).

**Do-not.** Do not wire a PostToolUse hook into consumer repos expecting failure telemetry;
do not "fix" the posttooluse filter to compensate — the event simply never arrives.
