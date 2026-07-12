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

Consumer repos wire `.claude/settings.json`:

```json
"hooks": {
  "PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command",
    "command": "\"$CLAUDE_PROJECT_DIR\"/.agent/skills/run-feedback/scripts/hooks/posttooluse.sh",
    "timeout": 10}]}],
  "SessionEnd": [{"hooks": [{"type": "command",
    "command": "\"$CLAUDE_PROJECT_DIR\"/.agent/skills/run-feedback/scripts/hooks/session_end.sh",
    "timeout": 10}]}]
}
```

Default OFF (the wrapper exits 0 unless `RUN_FEEDBACK_HOOKS=1` — set it in personal
`settings.local.json` `env`). Fail-silent; inbox-only; `SessionEnd` (not `Stop` — Stop fires
every turn) journals the session-end marker the miner uses. Data paths resolve through
`git rev-parse --git-common-dir`, so captures made inside a linked worktree land in the MAIN
working tree and survive worktree teardown.

**Mandatory rollout gate**: the Bash `tool_response` payload shape is not formally documented.
Before trusting this surface, run one session with `RUN_FEEDBACK_HOOK_DEBUG=1`, make a command
fail, and verify the dump in `.agent/feedback/hook_debug-*.json` against the extraction ladder
in `posttooluse_filter.py` (structured exit fields → `^Exit code N` text → envelope sniffing).

## C. Miner

See `cli_reference.md` §mine. Key properties: enumerates ALL per-cwd transcript shards under the
repo root; incremental byte offsets; skips active sessions; retry aggregation; redaction; hard
excerpt caps; assistant text / thinking / file contents never scanned. First run: `--dry-run`.
