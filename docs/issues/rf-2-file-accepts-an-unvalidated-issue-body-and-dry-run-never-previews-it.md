---
id: RF-2
type: known-issue
status: fixed
opened_at: 2026-07-14
category: feedback
severity: SEV-3
slug: rf-2-file-accepts-an-unvalidated-issue-body-and-dry-run-never-previews-it
component: run-feedback
fingerprint: 2c90df145756fcae
auto_fixable: true
finding_ref: fnd-20260714-032058-2c90df14
resolved_at: 2026-07-30
resolved_by: TASK 095
---

# RF-2 — file accepts an unvalidated issue body and dry-run never previews it

> **✅ FIXED 2026-07-30 (TASK 095, Light Mode).** Both halves, per the Fix path.
>
> **The gate:** `body.guard_structure`, called from `ledger_core.file_record`, refuses an unterminated
> code fence (**both** registries — an unbalanced fence swallows the rest of the rendered file) and a
> defect body with no `## Reproduction` / `**Reproduction.**` section, with **exit 4** as specified.
> The reproduction in this record — an unterminated ```sh fence with no repro section — now exits 4
> and writes **nothing**; it previously exited 0 and put the unbalanced fence in the ledger.
>
> **The preview:** `--dry-run` now echoes the rendered record under
> `--- record as it would be written ---`. Previewing the id, the paths and the index line but never
> the BODY meant the dry run could not catch the one mistake it existed to catch: the body is the part
> an agent composes by hand, and §5 create-only forbids repairing it afterwards.
>
> **The "Do-not" was honored:** create-only was not relaxed. The gate was fixed, not the invariant —
> which is what removes the trap that made an agent hand-edit a filed record and journal
> `body-amended`, a violation the rules left it no legal way to avoid.
>
> **Cost, recorded because it was not trivial:** the requirement exposed that **28 test fixtures were
> filing defect bodies the documented contract had always forbidden** (bare stubs like `"Body."`, no
> repro section). They now use one shared `fx.DEFECT_BODY`. Making the fixtures conform is the honest
> direction; loosening the gate to accept stubs would have been the gate bending to the tests. Two
> assertions that compared a body line-by-line, and one E2E line that broke under `set -o pipefail`
> (`doctor` exits 3 by design there, so the pipeline failed even when the grep matched), were fixed
> alongside.
>
> **Asymmetry that is deliberate:** work-item bodies need no Reproduction section — `/heal-issues`
> selects on a defect repro and a work-item has nothing to reproduce — but they DO need balanced
> fences. Both stated and pinned.
>
> Pinned by `tests/test_rf1_rf2.py::TestRF2BodyGate` (10 tests incl. the record's verbatim
> reproduction); all three guards mutation-verified. `SKILL.md` §1's Red Flag citing this record as an
> open trap has been rewritten to describe the gate instead.

**Symptom.** `file` performs no validation of the issue body, and `--dry-run` previews only the allocated ID, the paths and the index line — never the body. An agent that pipes a malformed body (unterminated ```sh fence, missing template sections) via `--body-file -` cannot discover the defect before the write, and afterwards §5 create-only forbids repairing it. Observed in the eval campaign (case 5, iteration 4): the agent filed VM-1 with a broken body, then hand-edited `docs/issues/vm-1-*.md` to repair it and journaled `body-amended` — a create-only violation the skill's own rules left it no legal way to avoid.

**Reproduction.**

```sh
T=$(mktemp -d) && mkdir -p "$T/.git" "$T/docs/issues"
RF="python3 .agent/skills/run-feedback/scripts/run_feedback.py --repo-root $T"
$RF collect --source test --kind test-failure --component demo --message "boom" >/dev/null
FND=$(ls "$T/.agent/feedback/inbox" | sed 's/\.json//')
# a body with an UNTERMINATED sh fence and no Workaround/Fix path sections
printf '**Symptom.** x\n\n**Reproduction.**\n\n```sh\necho broken\n' > "$T/bad.md"
$RF file --finding "$FND" --as defect --title "demo" --category robustness \
  --severity SEV-3 --body-file "$T/bad.md" --dry-run   # previews ID + index line, NOT the body
$RF file --finding "$FND" --as defect --title "demo" --category robustness \
  --severity SEV-3 --body-file "$T/bad.md"             # accepted, exit 0
grep -c '```' "$T/docs/issues/rf-1-demo.md"            # 1 -> unbalanced fence is now in the ledger
rm -rf "$T"
```

**Workaround.** Compose the body in a real file, verify it (balanced fences, all template sections) BEFORE `file`, and never build it from a heredoc you cannot re-read. If a body lands broken, do NOT hand-edit the filed issue — leave it and tell the human.

**Fix path.** Add a body gate in `feedback_lib/ledger_issues.py` at filing time: reject an unbalanced code fence and a missing `## Reproduction` / `**Reproduction.**` section with exit 4 (the existing "filing conflict" code), and echo the rendered body under `--dry-run`. Both are mechanical and covered by the existing unit suite (`scripts/tests/test_file_lockstep.py` already exercises the filing path), so this is gate-verifiable.

**Related.** finding_ref: see `finding_ref` in frontmatter · sibling [RF-1](rf-1-doctor-reports-ready-true-on-built-in-defaults-contradicting-its-own-remediation.md) (same "the gate does not check what it claims" class) · eval case 5, `.agent/skills/run-feedback/evals/evals.json`.

**Do-not.** Do not relax §5 create-only to let agents repair filed bodies — the audit trail and `/heal-issues` both assume issue files are immutable once written. Fix the gate, not the invariant.
