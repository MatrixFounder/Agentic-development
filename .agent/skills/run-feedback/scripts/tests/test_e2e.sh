#!/usr/bin/env bash
# run-feedback E2E: unit suite (zero-test guarded) + scripted pipeline in a
# throwaway repo. Mirrors the office-skills harness discipline: a discovery
# run that executes zero tests is a FAILURE, not a green gate.
set -uo pipefail

# Hermetic against the operator's session env: the opt-in capture flags may be
# exported globally via settings.local.json and MUST NOT leak into the suite.
unset RUN_FEEDBACK_HOOKS RUN_FEEDBACK_MINE_ON_END RUN_FEEDBACK_HOOK_DEBUG RUN_FEEDBACK_CONFIG

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$(dirname "$HERE")"
PY=python3
fail=0

echo "== unit suite =="
out="$(cd "$SCRIPTS" && $PY -m unittest discover -s tests 2>&1)" || fail=1
echo "$out" | tail -5
echo "$out" | grep -qE '^Ran [1-9][0-9]* test' || { echo "FAIL: zero-test discovery"; fail=1; }
echo "$out" | grep -qE '^OK' || { echo "FAIL: unit suite not OK"; fail=1; }

echo "== pipeline in a mktemp repo =="
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/.git" "$TMP/docs/issues"
RF="$PY $SCRIPTS/run_feedback.py --repo-root $TMP"

step() { echo "-- $1"; }

step "doctor"
$RF doctor >/dev/null || { echo "FAIL: doctor not ready"; fail=1; }

step "collect x2 (cross-source dedup)"
$RF collect --source hook --kind tool-error --component demo \
  --message "boom at /a/b 1" --command "python3 x.py" --exit-code 7 >/dev/null || fail=1
out="$($RF collect --source transcript --kind tool-error --component demo \
  --message "boom at /c/d 2" --command "python3 x.py" --exit-code 7 --json)" || fail=1
echo "$out" | grep -q '"deduped": true' || { echo "FAIL: no dedup"; fail=1; }
[ "$(ls "$TMP/.agent/feedback/inbox" | wc -l | tr -d ' ')" = "1" ] \
  || { echo "FAIL: inbox != 1 finding"; fail=1; }

step "triage"
$RF triage | grep -q "hook+transcript" || { echo "FAIL: sources not merged"; fail=1; }

FND="$(ls "$TMP/.agent/feedback/inbox" | sed 's/\.json//')"
BODY="$TMP/body.md"
printf '**Symptom.** boom.\n\n**Reproduction.**\n```sh\npython3 x.py\n```\n' > "$BODY"

step "file --dry-run leaves the tree untouched"
before="$(find "$TMP/docs" -type f -exec shasum {} + | shasum)"
$RF file --finding "$FND" --as defect --title "demo boom" --category robustness \
  --severity SEV-3 --body-file "$BODY" --dry-run >/dev/null || fail=1
after="$(find "$TMP/docs" -type f -exec shasum {} + | shasum)"
[ "$before" = "$after" ] || { echo "FAIL: dry-run wrote files"; fail=1; }

step "file --as defect (lockstep + seeded index)"
$RF file --finding "$FND" --as defect --title "demo boom" --category robustness \
  --severity SEV-3 --auto-fixable --body-file "$BODY" >/dev/null || fail=1
[ -f "$TMP/docs/issues/rf-1-demo-boom.md" ] || { echo "FAIL: issue file missing"; fail=1; }
grep -q '^- \*\*RF-1\*\* \[demo boom\](issues/rf-1-demo-boom.md) — severity `SEV-3`, status `open`,' \
  "$TMP/docs/KNOWN_ISSUES.md" || { echo "FAIL: index line format"; fail=1; }
grep -q '^## robustness$' "$TMP/docs/KNOWN_ISSUES.md" || { echo "FAIL: category section"; fail=1; }
[ -f "$TMP/.agent/feedback/filed/$FND.json" ] || { echo "FAIL: finding not moved to filed/"; fail=1; }

step "file --as work-item (two-level: record file + one-line pointer)"
cat > "$TMP/wi-config.json" <<'JSON'
{
  "v": 1,
  "issues_dir": "docs/issues",
  "index_path": "docs/KNOWN_ISSUES.md",
  "backlog_path": "docs/BACKLOG.md",
  "backlog_dir": "docs/backlog",
  "backlog_layout": "index+files"
}
JSON
RFW="$PY $SCRIPTS/run_feedback.py --repo-root $TMP --config $TMP/wi-config.json"
WI_BODY="$TMP/wi-body.md"
printf '**Signal.** the retro filed by hand.\n\n| Option | Cost |\n|---|---|\n| lockstep | S |\n\n**Recommendation:** option 1.\n' > "$WI_BODY"
$RFW collect --source workflow --kind user-friction --component demo \
  --message "work-item had to be filed by hand" --workflow e2e >/dev/null || fail=1
WFND="$(ls -t "$TMP/.agent/feedback/inbox" | head -1 | sed 's/\.json//')"
$RFW file --finding "$WFND" --as work-item --title "backlog needs records" \
  --effort S --value "bodies stop landing in the index" \
  --body-file "$WI_BODY" >/dev/null || { echo "FAIL: work-item filing"; fail=1; }
[ -f "$TMP/docs/backlog/wi-1-backlog-needs-records.md" ] \
  || { echo "FAIL: work-item record file missing"; fail=1; }
grep -q '^| Option | Cost |$' "$TMP/docs/backlog/wi-1-backlog-needs-records.md" \
  || { echo "FAIL: work-item body not preserved"; fail=1; }
grep -q '^- \*\*WI-1\*\* \[backlog needs records\](backlog/wi-1-backlog-needs-records.md) — effort `S`, status `open`,' \
  "$TMP/docs/BACKLOG.md" || { echo "FAIL: backlog index line format"; fail=1; }
grep -q 'Option | Cost' "$TMP/docs/BACKLOG.md" \
  && { echo "FAIL: body inlined into the backlog index"; fail=1; }
grep -q 'feedback:discovered-issues' "$TMP/docs/BACKLOG.md" \
  || { echo "FAIL: seeded backlog lost its anchor"; fail=1; }

step "flat layout refuses a body it would flatten"
sed 's/"index+files"/"flat"/' "$TMP/wi-config.json" > "$TMP/flat-config.json"
RFF="$PY $SCRIPTS/run_feedback.py --repo-root $TMP --config $TMP/flat-config.json"
$RFF collect --source workflow --kind user-friction --component demo \
  --message "second hand-filed work-item" --workflow e2e >/dev/null || fail=1
FFND="$(ls -t "$TMP/.agent/feedback/inbox" | head -1 | sed 's/\.json//')"
$RFF file --finding "$FFND" --as work-item --title "should be refused" \
  --body-file "$WI_BODY" >/dev/null 2>&1 && { echo "FAIL: flat layout flattened a structured body"; fail=1; }
[ -f "$TMP/.agent/feedback/inbox/$FFND.json" ] \
  || { echo "FAIL: refused filing consumed the finding"; fail=1; }

step "issues feed"
$RF issues --status open --json | grep -q '"auto_fixable": true' \
  || { echo "FAIL: issues feed"; fail=1; }

step "claim/release"
$RF claim --run-id e2e-run >/dev/null || { echo "FAIL: claim"; fail=1; }
$RF claim --run-id other-run >/dev/null 2>&1 && { echo "FAIL: nested claim not denied"; fail=1; }
$RF release --run-id e2e-run >/dev/null || { echo "FAIL: release"; fail=1; }

step "journal exists"
ls "$TMP/.agent/feedback/journal/"*.md >/dev/null 2>&1 || { echo "FAIL: no journal"; fail=1; }

if [ "$fail" = "0" ]; then echo "E2E: PASS"; else echo "E2E: FAIL"; fi
exit "$fail"
