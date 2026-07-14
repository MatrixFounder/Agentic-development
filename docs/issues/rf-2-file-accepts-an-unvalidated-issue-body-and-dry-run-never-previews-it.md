---
id: RF-2
type: known-issue
status: open
opened_at: 2026-07-14
category: feedback
severity: SEV-3
slug: rf-2-file-accepts-an-unvalidated-issue-body-and-dry-run-never-previews-it
component: run-feedback
fingerprint: 2c90df145756fcae
auto_fixable: true
finding_ref: fnd-20260714-032058-2c90df14
---

# RF-2 — file accepts an unvalidated issue body and dry-run never previews it

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
