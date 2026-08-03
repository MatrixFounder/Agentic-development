# VDD Critique: KNOWN_ISSUES thin-index system (Tasks 085 / 086 / 087)

> Adversarial review ("The Roast"). Target: commit `1ca49cf` (+ `c699848`). Reviewed by a
> fresh-context critic (author was context-locked); every finding re-verified against files.
> Execution evidence for the exit bar: `validate_skills.py` → **44/44**.

## 1. Executive Summary
- **Verdict:** **WARNING** (not PASS — legitimate non-CRITICAL findings remain; not FAIL — no CRITICAL/HIGH, nothing functionally broken, every live link resolves).
- **Confidence:** High (all findings verified by file:line).
- **Summary:** The ledger is internally consistent and reference-clean, but 087's headline promise — *one source for the format* — is structurally undercut: the contract is embedded in 3 self-contained prose copies that have **already** diverged (2 glosses), the seed comment credits the wrong owning skill, and the stated slug equality is violated by the repo's own AT-7.

## 2. Risk Analysis
| Severity | Category | Issue | Impact | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **MED** | consistency | Contract duplicated in `known-issues-format/SKILL.md`, the template, and the live ledger Rules section; glosses already disagree — `.agent/skills/known-issues-format/SKILL.md:51` `SEV-3 (degraded)` vs template:56/ledger:46 `SEV-3 (degraded / annoying)`; `.agent/skills/known-issues-format/SKILL.md:49` `by-design (intended trade-off)` vs the other two `…, not a defect`. The "authority" is the *less* complete copy. | The drift 087 set out to kill is present at birth; future edits to one copy silently diverge. | Reconcile the 2 glosses now; add a "these must stay in sync" note + a consistency check to the skill's Validation Evidence (or generate the template's Rules block from `SKILL.md`). |
| **LOW** | correctness | `template:11` seed comment: "shipped by the `artifact-management` skill" — false after 087 moved it to `known-issues-format`. | An agent reading the seed is misinformed about the owner. | Change to "shipped by the `known-issues-format` skill". |
| **LOW** | correctness | `.agent/skills/known-issues-format/SKILL.md:33` / `template:35` assert `slug == slugify(id)-slugify(title)`, but AT-7 title "Async spawn ≠ sync return" → slug `at-7-async-spawn-not-sync-return` (human `≠`→`not`; real slugify drops `≠`). | An unenforceable rule the repo's own data violates; misleads anyone trusting the equality. | Soften to "a slugified, human-readable stem from id + title (normalize symbols like `≠`→`not`)". `slug` == filename stem does hold 10/10 — keep that. |
| **LOW** | clarity | `template:12` "keep everything down to the second `---`" is ambiguous (the frontmatter example contains `---` lines) and conflicts with two other phrasings (`.agent/skills/known-issues-format/SKILL.md:66`, `.agent/skills/known-issues-format/examples/usage_example.md:36`). | A fresh-project agent may truncate the seed at the wrong line. | Unify to one instruction: "keep Purpose + Rules/Conventions (everything above the first `## <category>`); delete this comment and the `_No issues recorded yet._` block." |
| **LOW** | history-honesty | CHANGELOG presents v3.20.15 (template at `artifact-management/assets/…`) as a release, but 086+087 landed in one commit — that path never existed in git history. | `git archaeology` for v3.20.15's added file finds nothing. | Add a one-line note that v3.20.15 is descriptive; 086→087 were squashed. |
| **LOW** | robustness | Read-path steps ("Read `docs/KNOWN_ISSUES.md`" in CLAUDE.md / start-feature) have no if-absent guard; create-if-absent is write-path only, so a fresh project reads a missing file. | Minor — most agents tolerate a missing file. | Add "(skip if absent — created on first filed issue)" to the read-path instructions. |
| **NIT** | docs | `resolved_at`/`resolved_by` prescribed in prose (`.agent/skills/known-issues-format/SKILL.md:69` et al.) but absent from the frontmatter schema examples; no `fixed` issue exists yet to disambiguate. | Slight ambiguity (frontmatter vs body) for the first fix. | Add commented `# resolved_at / # resolved_by (only when status: fixed)` keys to the schema example. |
| **NIT** | reachability | TIER-2 `known-issues-format` auto-loads nowhere; discovery relies on the TIER-0 hub bullet / reverse-engineering pointer. | Acceptable by tier design; an agent formatting an issue without reading that bullet won't find it. | Accept, or add a one-line load hint to the Analysis-phase read step. |

## 3. Hallucination Check
- [x] **Files**: All cited files exist (`known-issues-format/SKILL.md`, its `assets/templates/known_issues_md_template.md`, `examples/usage_example.md`; `artifact-management/SKILL.md`; `skill-reverse-engineering/SKILL.md`; `docs/KNOWN_ISSUES.md`; `docs/issues/*.md`; `System/Docs/SKILLS.md`).
- [x] **Line numbers**: F1/F2/F3 re-verified by grep at the cited lines (glosses differ; template:11 attribution; SKILL.md:33 slug rule vs AT-7:10 title / :7 slug).
- [x] **Non-findings confirmed correct**: 10/10 index↔frontmatter (status/severity presence/opened); 10/10 slug==filename-stem; index-line format byte-identical SKILL↔ledger; all 10 index links + 13 inter-issue Related links resolve; no live dangling ref to the old template path; `validate_skills` 44/44; skill count 44; ROADMAP `at-6..at-9` deep-links resolve.

## 4. Exit-bar (Objective Convergence)
1. Full test run executed — ✅ `validate_skills` 44/44 (evidence supplied).
2. Zero CRITICAL — ✅.
3. Zero legitimate logic/security/slop findings — ❌ (1 MED consistency + LOW correctness findings are legitimate).
4. Only bikeshedding remains — ❌.

**Bar NOT met → not approved (WARNING).** Nothing is a functional break, but the verified consistency/correctness findings should be cleared before this is called Zero-Slop.

---

## 5. Re-run after remediation (Task 088) — verdict flips to **PASS**

All 8 findings cleared (release v3.20.17, gate artifact `docs/reviews/framework-audit-088.md`):

| Finding | Resolution |
|---|---|
| MED — contract drift across 3 copies | Glosses reconciled **and** guarded by a new automated gate `known-issues-format/scripts/check_contract_sync.py` (exit 0/1/2; **negative-tested**: injected drift → exit 1 with a precise diff). |
| LOW — seed owner attribution | → `known-issues-format`. |
| LOW — slug machine-equality | Softened; AT-7 counterexample no longer contradicts the rule. |
| LOW — ambiguous seed instruction | Unified across skill / template / example. |
| LOW — CHANGELOG history-honesty | Squash note added to the v3.20.15 entry (EN+RU). |
| LOW — read-path no if-absent guard | "skip if absent" added to all 5 read sites (CLAUDE/AGENTS/GEMINI + 2 workflows). |
| NIT — resolved_at/by absent from schema | Commented keys added (skill + template). |
| NIT — TIER-2 discoverability | Read-path sites now name `known-issues-format`. |

**Exit-bar (Objective Convergence) re-evaluated:** (1) tests executed — ✅ `validate_skills` 44/44 + `check_contract_sync` exit 0 (+ negative test); (2) zero CRITICAL — ✅; (3) zero legitimate logic/consistency/slop findings — ✅ (all cleared); (4) only accept-by-design remains — ✅.

**Verdict: PASS (Zero-Slop / Maximum Viable Refinement).**
