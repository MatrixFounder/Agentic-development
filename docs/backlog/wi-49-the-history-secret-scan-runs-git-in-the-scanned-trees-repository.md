---
id: WI-49
type: work-item
status: open
opened_at: 2026-10-09
slug: wi-49-the-history-secret-scan-runs-git-in-the-scanned-trees-repository
effort: M
value: 'a history secret scan of an untrusted tree runs no command that the tree names'
source: 'TASK 118 stage 2, H1 (D11)'
component: '.agent/skills/security-audit/scripts/audit/external.py'
---

# WI-49 — The history secret scan runs git in the scanned tree's repository

**Signal.** Slot `secrets-history` of `security-audit` runs `gitleaks detect` in git mode in the
scanned root, as the scanner did before TASK 118. git then reads the configuration of the scanned
tree's repository, and git documents configuration keys that name commands git runs. A tree that
arrives with its own `.git`, such as a tarball or a vendored copy, can therefore name a command
that runs as the operator. TASK 118 made the slot part of a complete scan and stated the exposure
in `security-audit` §2; the operator kept the git mode (D11 of TASK 118).

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Run the history scan in an isolated environment that the scanner starts, such as a container with no credentials | M | needs a container runtime |
| 2 | Run git mode against a clone that the scanner makes, so the tree's configuration stays behind | M | a local clone reads the source repository too; needs measuring |
| 3 | Make the history slot opt-in | S | a default scan reads `not_run` for the slot and exits 3 |

**Recommendation.** Measure option 2 first; option 1 where it does not hold.
