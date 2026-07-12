# Capture surfaces — layering

Three surfaces feed one inbox. They share the fingerprint recipe and the noise policy
(`feedback_lib/filters.py`), so the same failure captured twice collapses into one finding.

| Surface | Portability | When it fires | Status |
|---|---|---|---|
| **A. Retro step + `/run-feedback`** | any vendor (prompt text) | end of terminal workflows / on demand | the documented contract |
| **B. Claude Code hooks** | Claude Code only | live, per Bash failure + session end | opt-in accelerator, EXPERIMENTAL until payload shape confirmed |
| **C. Transcript miner (`mine`)** | Claude Code only | post-hoc over `~/.claude/projects/` | opt-in backfill (works on history) |

The system is COMPLETE with surface A alone; B and C only raise recall. Consumers that lack
Claude Code simply never enable B/C.

## A. Retro step

One numbered step in each terminal workflow referencing SKILL.md §7 "Retro protocol". Ownership
is deterministic (`claim`/`release` on `.agent/feedback/retro_owner`) because workflows have no
runtime nesting signal — the first workflow of the run claims, nested ones get exit 6 and skip.
Non-blocking by contract.

## B. Hooks (opt-in: `RUN_FEEDBACK_HOOKS=1`)

**Verified reality (2026-07-13, Claude Code 2.1.207, live headless experiment):**
`PostToolUse` fires ONLY on successful tool completion — a Bash call exiting non-zero produces
NO PostToolUse event at all — and its `tool_response` payload
(`{stdout, stderr, interrupted, isImage, noOutputExpected}`) carries **no exit code**. A
per-command PostToolUse hook therefore CANNOT capture failures, and consumer repos should NOT
wire one. (`scripts/hooks/posttooluse.sh` + `posttooluse_filter.py` are kept + tested for
harnesses/versions where such an event does deliver failures; the extraction ladder is correct
for the confirmed payload shape.)

The live capture path is **mine-on-session-end**. Consumer repos wire `.claude/settings.json`:

```json
"hooks": {
  "SessionEnd": [{"hooks": [{"type": "command",
    "command": "\"$CLAUDE_PROJECT_DIR\"/.agent/skills/run-feedback/scripts/hooks/session_end.sh",
    "timeout": 30}]}]
}
```

Default OFF (the wrapper exits 0 unless `RUN_FEEDBACK_HOOKS=1` — set it in personal
`settings.local.json` `env`). With `RUN_FEEDBACK_HOOKS=1` alone, SessionEnd journals the
session-end marker; add `RUN_FEEDBACK_MINE_ON_END=1` to also auto-mine the just-ended session's
transcript into the inbox (single file, incremental byte offset, `--include-active` semantics —
the transcript is complete once SessionEnd fires; transcripts record failures as
`tool_result {content: "Exit code N\n<stderr>", is_error: true}`, which the shared extraction
ladder parses). `SessionEnd`, not `Stop` — Stop fires every turn. Fail-silent; inbox-only. Data
paths resolve through `git rev-parse --git-common-dir`, so captures made inside a linked
worktree land in the MAIN working tree and survive worktree teardown.

## C. Miner

See `cli_reference.md` §mine. Key properties: enumerates ALL per-cwd transcript shards under the
repo root; incremental byte offsets; skips active sessions; retry aggregation; redaction; hard
excerpt caps; assistant text / thinking / file contents never scanned. First run: `--dry-run`.
