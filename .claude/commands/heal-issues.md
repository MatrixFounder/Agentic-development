Read and execute the workflow defined in `.agent/workflows/heal-issues.md`.

Follow all steps sequentially — SELECT → REPRODUCE → FIX → VERIFY & FILE → REPORT. Honor every
hard rail: branch-only (never commit to the base branch, never push/merge/PR), explicit
`auto_fixable: true` opt-in only, bounded iterations and attempts, protected paths, replication
protocol, surgical staging. Export `RUN_FEEDBACK_HOOKS=0` for the whole run.

Apply all Global Protocols (skill-session-state).

User's arguments (optional: issue-id, --max-issues=K, --dry-run, --scheduled, --config=PATH):
$ARGUMENTS
