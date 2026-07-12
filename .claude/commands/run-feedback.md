Read and apply the skill defined in `.agent/skills/run-feedback/SKILL.md` in **ad-hoc mode**
(§7 "Ad-hoc" — no claim/release):

1. If the scope hint below contains `mine`, first run the transcript miner
   (`python3 .agent/skills/run-feedback/scripts/run_feedback.py mine --dry-run`, review the
   candidate yield with the user, then re-run without `--dry-run` if approved).
2. Gather friction signals from the CURRENT session — failed commands, retries, exhausted gates,
   escalations — plus `active_blockers` from `.agent/sessions/latest.yaml`, scoped by the hint.
3. Ask the one retro question ("Что прошло НЕ гладко?") with observed candidates pre-listed,
   then `collect` → `triage` → classify → `file --dry-run` → `file`, per the skill's §7 Triage
   protocol.
4. Finish with a one-line report: filed IDs, dismissed count, journal path.

Apply all Global Protocols (skill-session-state). This command is non-blocking feedback
collection — it never modifies existing issues or code.

Scope hint (optional):
$ARGUMENTS
