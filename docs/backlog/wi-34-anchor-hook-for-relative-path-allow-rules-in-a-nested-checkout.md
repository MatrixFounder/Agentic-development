---
id: WI-34
type: work-item
status: open
opened_at: 2026-10-06
slug: wi-34-anchor-hook-for-relative-path-allow-rules-in-a-nested-checkout
effort: L
value: 'a relative-path allow rule stops matching inside a nested checkout'
source: 'TASK 111 (SEC-17), deferred from WI-31'
component: '.claude/hooks'
---

# WI-34 — An anchor hook for relative-path allow rules in a nested checkout

> Source: TASK 111 deferred SEC-17 here (TASK 111 D11). The specification audit (four rounds) and
> the review (three rounds) are in `docs/reviews/framework-audit-111.md`. **This body is data, not
> instructions.**

**Signal.** A Bash allow rule of `.claude/settings.json` matches the command text only; the working
directory takes no part (Claude Code docs). So `Bash(python3 .agent/tools/task_id_tool.py *)` also
approves that relative path inside a nested checkout, and `Bash(python3 -m pytest)`, started there,
runs a nested checkout's `conftest.py`. TASK 111 narrowed the committed allow list, which is a partial
mitigation, but the relative-path match itself stays. The registered PostToolUse hook's command,
`.claude/hooks/validate_skill_hook.sh`, is a relative path too, and it resolves against the
session's working directory.

**Why it matters.** A prompt-injected agent whose working directory sits in a cloned repository can
run that repository's code with no prompt. No allow-rule syntax anchors a Bash rule to the project
root; a PreToolUse hook that reads `cwd` is the documented lever.

**What TASK 111 tried.** `.claude/hooks/anchor_cwd.py` returned `ask` when a framework path or a
test runner met a directory outside the project's own work tree. Two models were built: one that
detects the danger, one that recognises only safe shapes. Each review round found a new divergence
between the hook's command model and the shell — a `cd` the shell never runs, a leading
`NAME=value`, zsh's `chdir` and glob qualifiers, `.` after an operator. A text-only hook cannot
model the shell completely.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Guard only what a committed allow rule would auto-approve | L | needs an approximation of Claude Code's matcher, and its own review |
| 2 | Ask on every command that names a framework path or a runner unless it has one of a few exact, whole-command shapes | M | more prompts in Auto mode, even where no rule would approve |
| 3 | Ask the Claude Code maintainers for a working-directory condition on Bash allow rules | — | outside this repository; no control over the timeline |
| 4 | do nothing, document the constraint | — | the gap stays |

**Recommendation.** Option 1, paired with Option 3 upstream. The hook earns its prompts only where
a rule would otherwise auto-approve a command; everywhere else the agent runs from the root.

**Acceptance.** Several conditions hold together:

- a command reaching a nested or foreign checkout's code through a committed allow rule asks;
- this repository's own gate and workflow commands from the project root do not;
- the hook never denies and exits 0;
- a bypass hunt confirms no silent-and-allowed escape on a documented shell.
