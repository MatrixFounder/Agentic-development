# Framework Audit — Task 088 (clear VDD-adversarial findings, enterprise-ready)

Meta-validator: `skill-self-improvement-verificator`. Scope: `known-issues-format` skill (+ a new
gate script), template, `docs/KNOWN_ISSUES.md` Rules, 3 bootstrap files + 2 workflows (read-path guard),
CHANGELOG. No product code.

## Mode A — SPECIFICATION AUDIT
| # | Check | Verdict |
|---|-------|---------|
| 1 | Root Integrity (core-principles). | ✅ Every fix traces to a verified finding in `vdd-adversarial-known-issues-format.md` (file:line). |
| 2 | Skill Compatibility (TIER 0). | ✅ Read-path guard added to CLAUDE/AGENTS/GEMINI in parity; no TIER-0 skill removed. |
| 3 | Documentation. | ✅ SKILLS.md/CHANGELOG synced (Step 6). |
| 4 | Migration. | ✅ Committed per-issue files untouched; ledger Rules reconciled in place (no schema change). |

**Failure conditions:** none. **Mode A: PASS.**

## Mode B — PLAN AUDIT
| # | Check | Verdict |
|---|-------|---------|
| 1 | Verification Step. | ✅ `validate_skills` 44/44 + new `check_contract_sync.py` (exit 0) + link/grep checks + adversarial exit-bar re-run. |
| 2 | Rollback. | ✅ Backups of skill/template/ledger/bootstrap/CHANGELOG in `.agent/archive/`. |
| 3 | Atomic Updates. | ✅ Per-finding edits (R1–R8) independently verifiable. |
| 4 | Test Coverage. | ✅ The MED fix ADDS an executable gate (`check_contract_sync.py`) with defined failure semantics (exit 1 on drift) — the enterprise upgrade over a one-time reconcile. Script Contract + Validation Evidence documented in the skill. |

**Mode B: PASS.** No bypass flags.

## Design record
- MED (contract drift) is closed two ways: (a) reconcile the 3 copies now; (b) an automated, CI-gateable
  `check_contract_sync.py` that fails on future divergence of the status/severity vocab, frontmatter keys,
  and index-line format between the skill (authority) and the template (seed). The ledger is a per-project
  instance, so the gate compares the two framework-shipped artifacts.
