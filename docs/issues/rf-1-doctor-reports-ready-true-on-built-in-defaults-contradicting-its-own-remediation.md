---
id: RF-1
type: known-issue
status: fixed
opened_at: 2026-07-13
category: feedback
severity: SEV-4
slug: rf-1-doctor-reports-ready-true-on-built-in-defaults-contradicting-its-own-remediation
component: run-feedback
fingerprint: 05ad70c4ab4d6d67
finding_ref: fnd-20260713-220152-05ad70c4
resolved_at: 2026-07-30
resolved_by: TASK 095
---

# RF-1 — doctor reports ready:true on built-in defaults, contradicting its own remediation

> **✅ FIXED 2026-07-30 (TASK 095, Light Mode).** `doctor` now reports `configured` as its own check
> **and folds it into `ready`**, so an unconfigured repo is `ready: false` / exit 3. The record's own
> reproduction was re-run before and after: before, `ready: true` with a one-item remediation; after,
> `ready: false`, `configured: false`, exit 3 — and `init` then makes it ready, which is the bootstrap
> flow the fix exists to enable.
>
> **Option (a) from the Fix path**, taken over (b) deliberately: adding a `configured` field while
> leaving `ready` alone would not have fixed the reported harm, which is that *callers gate on
> `ready`*. A field they still would not read changes nothing.
>
> **The "Do-not" was honored in lockstep** — flipping `ready` semantics required all three:
> `tests/test_e2e.sh` (which asserted `doctor` exits 0 in a config-less repo) now asserts the NEW
> contract, both halves of it, plus an `init` → `doctor` step it never had; `references/cli_reference.md`
> documents what `ready` means; and `SKILL.md` §7's Bootstrap protocol lost the paragraph that existed
> only to teach agents not to trust this field. No heal-config impact, as the record predicted.
>
> **What deliberately did NOT change:** `collect` / `file` still run on built-in defaults and exit 0.
> Only `doctor` refuses. Gating filing on configuration is a much larger behaviour change and was not
> what this record asked for.
>
> Pinned by `tests/test_rf1_rf2.py::TestRF1DoctorReadiness` — including the invariant stated directly
> (`ready` and a non-empty remediation are never both true, across three config states), which is the
> assertion that would have caught this at any point. Both guards mutation-verified.

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
