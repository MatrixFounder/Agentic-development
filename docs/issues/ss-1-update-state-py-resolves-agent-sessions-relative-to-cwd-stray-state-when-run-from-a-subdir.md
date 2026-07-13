---
id: SS-1
type: known-issue
status: fixed
opened_at: 2026-07-13
resolved_at: 2026-07-13
resolved_by: direct fix 2026-07-13 (run-feedback dogfood, SS-1)
category: session-state
severity: SEV-3
slug: ss-1-update-state-py-resolves-agent-sessions-relative-to-cwd-stray-state-when-run-from-a-subdir
component: skill-session-state
fingerprint: 441bc711c76ea0cc
auto_fixable: true
finding_ref: fnd-20260713-101821-441bc711
---

# SS-1 — update_state.py resolves .agent/sessions relative to CWD — stray state when run from a subdir

> **Resolved 2026-07-13.** `update_state.py` now anchors `SESSION_DIR` at the repo root:
> walk-up from CWD to the first directory containing `.git` (dir or worktree file), then
> `CLAUDE_PROJECT_DIR` fallback, then legacy CWD for non-git scratch dirs. Regression suite:
> `scripts/tests/test_update_state.py` (6 tests — subdir, worktree marker, root, env fallback,
> legacy, no-fork merge). Original red repro re-run green; live subdir invocation verified
> against the Universal-skills checkout.

> Mined from Universal-skills session transcripts (2026-07): the orchestrator, working with
> CWD inside `skills/transcript-fetcher/`, invoked the phase-boundary protocol and got
> `python3: can't open file '…/skills/transcript-fetcher/.agent/skills/skill-session-state/scripts/update_state.py'`.
> Two layers: the relative *script path* was the immediate miss, but the script itself has the
> same class of bug — `SESSION_DIR = ".agent/sessions"` is CWD-relative.

**Symptom.** `update_state.py` resolves `.agent/sessions/latest.yaml` relative to the CURRENT
working directory. Run from anywhere below the repo root it silently creates a stray
`.agent/sessions/` tree in that subdirectory (state fragmentation: the real session file is
not updated, and a junk dir appears inside a skill).

**Reproduction.**

```sh
cd "$(mktemp -d)" && git init -q . && mkdir -p sub .agent/sessions
cd sub
python3 <path-to-framework>/.agent/skills/skill-session-state/scripts/update_state.py \
  --mode Test --task t --status s --summary x
ls .agent/sessions/latest.yaml   # stray state created under sub/ — BUG
ls ../.agent/sessions/           # real location untouched
```

**Workaround.** Always invoke the protocol from the repo root (CLAUDE.md examples assume it),
or `cd "$(git rev-parse --show-toplevel)"` first.

**Fix path.** Resolve the repo root by walking up from CWD to the first directory containing
`.git` (or honor `CLAUDE_PROJECT_DIR` when set) and anchor `SESSION_DIR` there — same
resolution `run-feedback/scripts/feedback_lib/config.py` already implements; add a regression
test invoking the script from a subdirectory.

**Related.** `.agent/skills/skill-session-state/scripts/update_state.py` (SESSION_DIR
constant); `run-feedback` `feedback_lib/config.py` (reference implementation of the walk-up).

**Do-not.** Do not fix by hardcoding absolute paths or requiring an env var without the
walk-up fallback — the script must keep working in plain `python3 … update_state.py` calls
from the repo root with zero setup.
