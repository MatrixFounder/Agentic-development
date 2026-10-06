---
id: WI-36
type: work-item
status: open
opened_at: 2026-10-06
slug: wi-36-command-substitution-inside-an-allow-approved-command
effort: S
value: 'the framework states what Claude Code does with a substitution inside an approved command'
source: 'TASK 112 (WI-35 follow-up)'
component: 'skill-safe-commands'
---

# WI-36 — Command substitution inside an allow-approved command

**Signal.** code.claude.com/docs/en/permissions, fetched 2026-10-06, states two things:

- deny and ask rules apply to a command nested in a command substitution;
- a redirect target is checked against the file rules, as if Claude wrote that file.

It does not state whether an allow rule such as `Bash(echo *)` approves `echo "$(date)"` with no
prompt. `skill-safe-commands` treats such a command as not safe on the agent's side; Claude Code's
own behaviour is unchecked.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Measure it in Manual mode with a harmless inner command; record the result and the version | S | holds for that version only |
| 2 | An `ask` rule for `$(` forms | S | the docs call argument patterns fragile |
| 3 | do nothing | — | the case stays unknown |

**Recommendation.** Option 1.

**Acceptance.** `skill-safe-commands` states the measured behaviour and the Claude Code version.
