# Technical Specification: Clear the VDD-adversarial findings on the KNOWN_ISSUES system (enterprise-ready)

### 0. Meta Information
- **Task ID:** 088
- **Slug:** `known-issues-vdd-fixes`
- **Mode:** Framework Upgrade (skill/docs/workflow edits + one gate script; **no product code**)
- **Type:** Consistency / hardening. Clears the WARNING from `docs/reviews/vdd-adversarial-known-issues-format.md`.
- **Workflow:** `/framework-upgrade` (verificator Modes A + B).

### 1. Problem Description
The adversarial review returned **WARNING** (1 MED, 5 LOW, 2 NIT — all verified). To reach the objective
exit bar (Zero-Slop), every finding must be cleared. "Enterprise-ready" means the MED (contract drift) is
closed with an **automated gate**, not just a one-time reconcile.

### 2. Requirements (RTM)

| ID | Finding | Fix | Verify |
|----|---------|-----|--------|
| R1 | **MED** contract duplicated across skill/template/ledger; glosses already drifted. | Reconcile all copies **and** add `scripts/check_contract_sync.py` (a CI-gateable drift check comparing status/severity vocab + frontmatter keys + index-line format across SKILL.md ↔ template); wire it into the skill's Script Contract + Validation Evidence. | Script exits 0; drift → exit 1. |
| R2 | **LOW** seed comment credits `artifact-management` as owner. | Fix attribution → `known-issues-format`. | grep. |
| R3 | **LOW** slug rule asserts machine equality the repo's AT-7 violates. | Soften to human-readable-stem phrasing (SKILL + template). | Re-read. |
| R4 | **LOW** "keep down to the second `---`" ambiguous; 3 phrasings disagree. | Unify to one unambiguous instruction across template/SKILL/example. | Re-read. |
| R5 | **LOW** CHANGELOG v3.20.15 describes a never-committed path. | Add a squash/descriptive note (EN+RU). | Re-read. |
| R6 | **LOW** read-path has no if-absent guard. | Add "(skip if absent — created on first filed issue)" to the 5 read sites (CLAUDE/AGENTS/GEMINI + 2 workflows). | grep. |
| R7 | **NIT** `resolved_at`/`resolved_by` prescribed but absent from schema example. | Add commented keys to SKILL + template frontmatter examples. | Re-read. |
| R8 | **NIT** TIER-2 discoverability. | Add a one-line load hint at the read/format site (accept-by-design otherwise). | Re-read. |

### 3. Non-Goals
- No change to the 10 committed per-issue files or their content.
- No installer/vendors.yaml change; the new script ships via the `.agent/skills` link (auto-deployed).

### 4. Acceptance Criteria
- Adversarial exit bar re-evaluated: 0 CRITICAL, 0 legitimate logic/consistency findings, only accept-by-design remains → **PASS**.
- `validate_skills` 44/44; `check_contract_sync.py` exits 0; all links resolve.
