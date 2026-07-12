---
description: Bounded self-healing over the known-issues ledger — select an explicitly auto-fixable open issue, reproduce, fix on a branch, verify with the component's gates, flip status. Never touches main, never pushes.
---
# Workflow: Heal Issues

**Description:**
Consumes `docs/issues/` (the `known-issues-format` ledger, fed by `run-feedback`): picks ONE
`status: open` + `auto_fixable: true` issue, re-proves it red, fixes it on a `fix/` branch under
hard rails, verifies with the component's own gates, and flips the ledger status in the same
commit. Output is a PR-ready branch for HUMAN review — this workflow NEVER pushes, merges, or
opens PRs, and never commits to the base branch.

**Invocation:** `/heal-issues [issue-id] [--max-issues=K] [--dry-run] [--scheduled] [--config=PATH]`
- `issue-id` — bypass ranking, heal this specific issue (still all rails).
- `--dry-run` — Phases 0–1 only: select + reproduce + report; no branch, no edits.
- `--scheduled` — set by an unattended scheduler; honors the config kill-switch.
- Config default: `docs/feedback/heal-config.json` (per-repo gates map & rails; missing file →
  built-in conservative defaults + a warning in the report).

> [!IMPORTANT]
> **Loop protocol (applies to every phase):**
> 1. Gates are **objective** — script exit codes, `diff -q`, test runs. Never self-assessment.
> 2. On a gate failure, feed the error output **verbatim** into the retry.
> 3. Persist state at each phase boundary
>    (`python3 .agent/skills/skill-session-state/scripts/update_state.py …`).
> 4. **Session hygiene:** export `RUN_FEEDBACK_HOOKS=0` for the whole run (the healer's own
>    failing commands must not pollute the feedback inbox); stage surgically — explicit paths
>    only, NEVER `git add -A`/`-u`/`.`.

**Steps:**

0. **SELECT** — preconditions and ranking.
   - **Run-lock:** `python3 .agent/skills/run-feedback/scripts/run_feedback.py journal
     --event-type heal_run --subject "start"` then take the lock: if
     `.agent/feedback/heal.lock` is flock-held by a live run (attempt a non-blocking flock via
     `python3 -c "import fcntl,os,sys; fd=os.open('.agent/feedback/heal.lock',os.O_CREAT|os.O_RDWR); fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)"`),
     a failure means another heal run is live → print "heal-issues: another run holds the lock"
     and STOP (success, not error). Hold the fd for the whole run.
   - **Preconditions (any failure → STOP with the reason):** `git status --porcelain` is empty;
     current branch == config `base_branch` (default `main`); config parses. With
     `--scheduled` and config `scheduling.enabled: false` → print "disabled by config" and STOP
     cleanly (kill-switch; manual runs ignore this flag).
   - **Eligibility** — via `run_feedback.py issues --status open --json`, an issue is eligible
     ONLY when ALL hold:
     a. `status: open` (never by-design/mitigated/handled/wontfix/documented/fixed);
     b. **explicit `auto_fixable: true`** in frontmatter — absence = NOT eligible (this is the
        human opt-in; honest-scope/design decisions are protected by default);
     c. `.agent/feedback/heal-state.json` shows `attempts < max_attempts_per_issue` (default 2)
        and no `blocked` flag for this id;
     d. its `component` maps to at least one verification gate in the config `gates` map AND
        that component's declared venv/tooling exists (e.g. `skills/<c>/scripts/.venv`) — a
        missing gate or venv means "not auto-fixable here", never "run it anyway".
   - **Rank:** severity rank desc (unknown/missing severity → lowest) → `auto_fixable` → oldest
     `opened_at`. Take top `max_issues_per_run` (default **1** — one reviewable diff per run).
   - Zero eligible → report "ledger clean or all blocked" + per-issue skip reasons → STOP (success).

1. **REPRODUCE** — prove it is still red.
   - Extract the repro EXCLUSIVELY from the issue body's `## Reproduction` / `**Reproduction.**`
     fenced `sh` block, or a script listed in frontmatter `evidence_paths`. **NEVER synthesize
     commands from prose.** No runnable repro → record `repro-blocked` in heal-state (does NOT
     consume an attempt), skip to report.
   - Run it under the same command allowlist as the gates; with `--scheduled`, network access is
     forbidden — a repro needing the network is `repro-blocked`.
   - **Still red** → the failing repro is the red test; proceed. `--dry-run` stops here and reports.
   - **Green (already fixed)** → branch `fix/<id-lower>-<slug>`, flip frontmatter
     `status: fixed` + `resolved_at` + `resolved_by: heal-issues (verified-gone <ts>)`, append a
     resolution blockquote (body text preserved verbatim), update the ONE index line in
     `docs/KNOWN_ISSUES.md` in lockstep, commit the ledger-only change (explicit paths), report.

2. **FIX** — bounded loop, max 3 iterations, on branch `fix/<id-lower>-<slug>`.
   - **Branch collision:** if the branch already exists from a previous attempt, resume it;
     if resuming is unsafe (diverged), create `fix/<id-lower>-<slug>-2`. Never delete branches.
   - **Hard rails checked on EVERY iteration (violation → revert the edit, iteration FAILS):**
     - **Replication protocol** (consumer repo's CLAUDE.md §2, e.g. Universal-skills): never
       edit a non-master replica (xlsx/pptx/pdf/html copies of docx-mastered files; html's
       `web_clean/` master is **pdf**); editing a master REQUIRES the full replication commands
       + all `diff -q` byte-identity checks + the 4-skill validator in the SAME iteration.
     - **Protected paths** (config `protected_paths` + defaults): any `LICENSE`/`NOTICE`,
       `THIRD_PARTY_NOTICES.md`, `.claude/settings*`, framework symlinks, both feedback
       configs, `.git/` internals.
     - **Diff guard:** ≤ `max_changed_lines` (default 300) / ≤ `max_changed_files` (default 10),
       mechanically replicated copies excluded from the count. Bigger fix → this is not a small
       correction: STOP, mark `needs-human`, keep the analysis in the report (the fix belongs
       to the normal TASK pipeline).
     - **No new dependencies** (they would require THIRD_PARTY_NOTICES — protected → human).
   - **Iteration body:** implement the minimal fix → run in order: (a) the Phase-1 repro (must
     now be green); (b) the component's gates from config (e2e script, unit suite via the
     component's venv, validator) — each with a per-gate timeout (config `gate_timeout_sec`,
     default 900; timeout → `needs-human`, not silent abort); (c) replication `diff -q` set when
     office-mastered files were touched. Any FAIL → feed output verbatim into the next iteration.
   - **Exhaustion (3 iterations):** commit what exists as
     `WIP(heal-issues): <ID> attempt <ts> — NOT FIXED` (branch kept — it carries the red repro),
     annotate the issue file ON THE BRANCH with an `## Auto-heal attempt <ts>` blockquote,
     `git switch` back to base leaving it pristine, then `attempts += 1` in heal-state; at
     `max_attempts_per_issue` → `blocked: needs-human` (Phase 0 will never re-select it until a
     human clears the entry).

3. **VERIFY & FILE** — only reached with all gates green.
   - Flip the ledger IN THE SAME COMMIT as the fix: issue frontmatter `status: fixed`,
     `resolved_at: <ISO date>`, `resolved_by: heal-issues run <ts> (branch fix/<id>-<slug>)`,
     resolution blockquote appended (never edit existing body text), and the matching
     `docs/KNOWN_ISSUES.md` index line updated in lockstep. Never delete the issue file; never
     touch any other ledger entry.
   - Commit: `fix(<component>): <ID> <short title> [heal-issues]` — body lists the gates run and
     `Refs: docs/issues/<slug>.md`. Explicit paths only.
   - Write the run report `docs/feedback/heal-reports/<YYYY-MM-DD-HHMM>-<id-lower>.md` ON THE
     BRANCH: selection table, repro evidence before/after, per-iteration log, gate matrix,
     diff stat, review instructions. Journal `heal_run` end via `run_feedback.py journal`.
   - **NEVER `git push`, NEVER merge, NEVER `gh pr create`.**

4. **REPORT** — no silent outcomes.
   - Final line, always (also on no-op/blocked):
     `heal-issues <ts>: <ID> fixed on fix/<id>-<slug> (N iterations, gates ✓) — review: git diff <base>..fix/<id>-<slug>`
     or `heal-issues <ts>: NO-OP (<reason>)` or `heal-issues <ts>: <ID> BLOCKED needs-human (<reason>)`.
   - If a notification channel is available (e.g. Claude Code PushNotification), send the same
     line. Unattended runs must leave a human-visible trace beyond the branch itself.
   - Retro (Global Protocol) does NOT apply to `--scheduled` runs (no user to ask); manual runs
     follow the standard retro claim/skip semantics.

**Human review loop (documentation, not a step):** `git branch --list 'fix/*'` → read the run
report on the branch → optionally re-run the gates → merge (the ledger flip lands with the
merge) → delete the branch. `blocked: needs-human` entries surface in every run report until a
human clears `.agent/feedback/heal-state.json` or fixes the issue via the normal pipeline.

**Scheduling (operator-side, NOT a repo artifact):** the documented contract is MANUAL
invocation. An operator MAY schedule it user-side (e.g. a weekly Claude Code scheduled task
running `/heal-issues --scheduled` in the repo) — start only after ≥3 consecutive manual runs
whose branches merged without correction, keep `scheduling.enabled: false` in git and flip it in
a human commit, and remember kill-switches: delete the scheduled task / the config flag /
`git branch -D`. Do NOT add repo-level cron/CI/git-hooks for this (see the consumer repo's
honest-scope precedent: backlog xlsx-10 / review R2-H2 — never document automation whose runner
does not exist).

## Fallback
Single-agent and sequential by design — no vendor-specific primitives. Any vendor runs it
unmodified; only `--scheduled` semantics assume an external scheduler exists.
