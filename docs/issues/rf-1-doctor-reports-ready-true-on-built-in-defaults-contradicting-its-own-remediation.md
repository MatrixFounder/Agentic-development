---
id: RF-1
type: known-issue
status: open
opened_at: 2026-07-13
category: feedback
severity: SEV-4
slug: rf-1-doctor-reports-ready-true-on-built-in-defaults-contradicting-its-own-remediation
component: run-feedback
fingerprint: 05ad70c4ab4d6d67
finding_ref: fnd-20260713-220152-05ad70c4
---

# RF-1 — doctor reports ready:true on built-in defaults, contradicting its own remediation

**Symptom.** In a repo with no `docs/feedback/config.json`, `doctor --json` reports `"ready": true` while `remediation` simultaneously says `no docs/feedback/config.json — run run_feedback.py init to bootstrap`. Any caller that gates on `ready` (a workflow step, a heal run) concludes an unconfigured repo is configured; filings then run on built-in defaults and the SKILL.md Bootstrap trigger ("collect/file exits 3") never fires — discovered because eval agents filed into an unbootstrapped fixture repo and nothing stopped them.

**Reproduction.**

```sh
T=$(mktemp -d) && mkdir -p "$T/.git" "$T/docs/issues"
python3 .agent/skills/run-feedback/scripts/run_feedback.py --repo-root "$T" doctor --json
# observe: "ready": true  AND a non-empty "remediation" — contradictory
rm -rf "$T"
```

**Workaround.** Gate on `remediation == []` (or `config_source != "built-in defaults"`), not on `ready`. SKILL.md §7 Bootstrap step 3 already states the correct criterion ("ready: true with an empty remediation list").

**Fix path.** Decide the contract in `scripts/feedback_lib/config.py` / `run_feedback.py doctor`: either (a) `ready: false` whenever remediation is non-empty, or (b) add an explicit `configured: bool` check and keep `ready` as "filesystem-writable". NOTE: `scripts/tests/test_e2e.sh` asserts `doctor` exits 0 in a config-less mktemp repo — option (a) changes that contract; the e2e assertion must move to the new field in lockstep.

**Related.** finding_ref: fnd-20260713-220152-05ad70c4 · eval campaign 2026-07-13 (case 10, `.agent/skills/run-feedback/evals/evals.json`).

**Do-not.** Do not flip `ready` semantics without updating `test_e2e.sh` and `references/cli_reference.md` in the same change; heal gates select on the issues feed, not on doctor, so no heal-config impact.
