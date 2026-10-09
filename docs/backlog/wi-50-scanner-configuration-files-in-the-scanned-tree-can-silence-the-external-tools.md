---
id: WI-50
type: work-item
status: open
opened_at: 2026-10-09
slug: wi-50-scanner-configuration-files-in-the-scanned-tree-can-silence-the-external-tools
effort: M
value: 'an external tool reports what the scanner asks for, not what the scanned tree allows'
source: 'TASK 118 stage 2, M2 (D14)'
component: '.agent/skills/security-audit/scripts/audit/external.py'
---

# WI-50 — Scanner configuration files in the scanned tree can silence the external tools

**Signal.** The external tools of `security-audit` read configuration files from the directory
they scan. The stage-2 audit of TASK 118 named `.gitleaks.toml` and `.gitleaksignore` for gitleaks
(high confidence), `.semgrepignore` for semgrep, and `trivy.yaml` and `.trivyignore` for trivy
(medium confidence). None of the tools is installed on the machine of that run, so the list is not
measured. A scanned tree that holds such a file can exclude its own findings; the tool then exits
0 and the scan reads clean. TASK 118 stated this in `security-audit` §2 (D14 of TASK 118).

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Point each tool at a scanner-owned configuration; report the tree's tool configuration files | M | per-tool options to verify |
| 2 | Report the files as findings only | S | the tools stay silenced; the reader sees why |

**Recommendation.** Option 1; option 2 for a tool with no override.
