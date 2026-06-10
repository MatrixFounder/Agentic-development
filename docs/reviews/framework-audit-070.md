# Framework Audit: OWASP Top 10 Checklist Re-map to 2025 Final (Task 070)

**Date:** 2026-06-10
**Auditor:** Self-Improvement Verificator
**Target:** `docs/TASK.md`
**Status:** **APPROVED** (Mode A — Specification Audit)

## 1. Compliance Checklist (Mode A)

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | ID 070, slug `owasp-top10-2025-remap`, Mode = Framework Upgrade, source traced to roadmap item 4 + audit-067 claim C-09 + user request (2026-06-10). |
| **Root Integrity** | ✅ Pass | Taxonomy re-map, zero behavior change. Anti-hallucination honored: all ten 2025 category names **web-verified this session directly against owasp.org/Top10/2025/** (not model memory, not even the audit-067 paraphrase — which the verification caught simplifying A09's official name "Security Logging and Alerting Failures" to "Logging & Alerting Failures"). Blast radius established by grep, not assumption — including the **evidence-based correction** that `patterns.py` carries no A-number tags (they live in `scanners.py` docstrings). Stub-First: N/A (no new code; checklist + docstring edits only). Atomicity: R1–R5 independently verifiable. |
| **Skill Compatibility** | ✅ Pass | No new agents/prompts/workflows/skills. No new files in `.agent/skills/` → `init_skill.py` gate N/A. Existing-skill modification is gated by `validate_skill.py` (43/43 baseline) per roadmap global gate 2. TIER 0 loading blocks untouched. |
| **Documentation** | ✅ Pass | R5 covers `System/Docs/SKILLS.md` registry row (v3.4→v3.5), CHANGELOG EN+RU, and the roadmap status flip. Checklist header gets a primary-source citation with verification date. |
| **Migration** | ✅ Pass (N/A) | No persisted state, no session impact. Downstream compliance exports (Jira/Snyk) self-correct on the next audit run; the CHANGELOG entry flags the renumbering so previously exported A-number mappings are known-stale. |

## 2. Failure-Condition Scan
- Removing `core-principles`/`skill-safe-commands` from any agent? ❌ No.
- Modifying a bootstrap file (`CLAUDE.md`/`AGENTS.md`/`GEMINI.md`) without `System/Docs` update? ❌ No bootstrap file touched.
- Creating a new Workflow without defining its Trigger? ❌ No new workflow.
→ **No blocking conditions.**

## 3. Risk Analysis

- **R1 — Content loss/duplication during re-sectioning.** Moving checks between 10 sections is the classic place to silently drop a checkbox. *Mitigation:* PLAN must include a **conservation check**: checkbox count before/after, and every 2021 item explicitly accounted for (moved, merged, or deliberately reworded — no silent deletions).
- **R2 — CWE header drift.** Section CWE lines must follow the moved content (A01 gains CWE-918 from old-A10; new A10 gets CWE-209/390/754/636; CWE-209 leaves the old Misconfiguration section). *Mitigation:* explicit per-section CWE review step in PLAN.
- **R3 — Version-string drift.** "3.4" is synced across SKILL frontmatter, H1, `run_audit.py` docstring, `audit/__init__.__version__`, and the SKILLS.md registry row (069's R4d sync list). *Mitigation:* PLAN greps for `3\.4` across the skill + registry and bumps every hit to 3.5.
- **R4 — Test breakage on docstring assertions.** If any pytest asserts the old A-number strings, the doc-only claim breaks. *Mitigation:* PLAN greps the test suite for A-number literals before editing; updates ride in the same change if found.
- **R5 — Grep-gate false positives.** The R4 acceptance grep will legitimately hit ASI01–ASI10 (`mcp_agentic_security.md`), API1–API10 (`api_security.md`), and immutable CHANGELOG history. *Mitigation:* gate definition in PLAN excludes those classes explicitly, so "clean" is objective, not judged ad hoc.
- **R6 — Scope creep into Current checklists.** API Top 10:2023 and LLM Top 10 v2.0 were audited Current. *Mitigation:* TASK §2 fences them out; reviewer checks the diff touches only the four declared files + docs.

## 4. Verdict
**APPROVED.** Specification is primary-source-anchored, grep-scoped, behavior-neutral by design, and fenced against neighboring roadmap items (10). Proceed to Planning.

**Carry-forward for the PLAN:**
1. Conservation check for checklist items (count + per-item accounting).
2. Per-section CWE header review (A01 +918; new A10 set; 209 relocation).
3. Version-sync grep (`3\.4` → 3.5 across frontmatter/header/docstring/`__version__`/registry).
4. Pre-edit grep of tests for A-number literals.
5. Objective grep-gate definition with named exclusions (ASI, API-numbers, CHANGELOG history).
6. Backup step before edits (workflow §3.1); `validate_skill.py` + pytest gates; rollback instructions.

---

# Mode B — Plan Audit (Task 070)

**Target:** `docs/PLAN.md` · **Status:** **APPROVED**

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | ✅ Pass | T5 is a dedicated 5-gate phase: conservation count (objective: 66 checkboxes, derived 61−1+5+1), stale-reference grep with named exclusions, `validate_skill.py` single + 43/43 loop, behavior proof (pytest 30/30 + `run_audit.py` finding counts identical to T0 baseline; full summary differs only by the intentional version-header line — see `adversarial-review-070.md`), diff-scope check. |
| **Rollback** | ✅ Pass | T0 backs up all 9 edit targets + bootstrap files; T0.4 captures pre-edit behavioral baselines so "identical" is checkable, not asserted. No file creations/deletions → restore = `cp` only. |
| **Atomic Updates** | ✅ Pass | T1–T4 map 1:1 to RTM R1/R2/R3/R5 (R4 is the T5.2 gate); strict order; the T1 content-move map pins every section's source so the re-map is reviewable line-by-line. |
| **Test Coverage** | ✅ Pass (N/A justified) | No new framework behavior → no new tests required. The plan inverts the obligation correctly: existing 30 tests + run_audit baseline serve as a **regression oracle proving zero behavior change** (the task's core contract). Pre-verified that no test asserts A-number literals. |

**Carry-forward checks honored:** all 6 Mode A items appear as concrete PLAN steps — conservation check (T1 + T5.1), CWE header review (T1 table, incl. A01+918, A06−209, new A10 set), version-sync grep (T2.3), test-literal pre-check (T3), objective grep gate (T5.2), backup/gates/rollback (T0/T5/Rollback).

**Residual risks accepted:** (i) judgment calls in the A03↔A08 split (CI/CD + code signing → A03; unsigned auto-update stays A08) follow the official 2025 category descriptions but reasonable people could re-home individual items — the 2021→2025 mapping table in the checklist makes the choice transparent; (ii) checkbox-count target (66) depends on the dedup decision — count is re-derived in T5.1, not treated as sacred.
