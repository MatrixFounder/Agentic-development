# Technical Specification: Skill-Validator Inline-Code-Block Rule Reform

### 0. Meta Information
- **Task ID:** 064
- **Slug:** `validator-inline-rule-reform`
- **Mode:** Framework Upgrade (meta-operation — modifies the framework's own validation logic)
- **Type:** Refinement — quality-gate rule alignment with Agent Skills best practices
- **Workflow:** `/framework-upgrade`
- **Source:** User review of CI failure on commit `c3d9373` (v3.16.0). `skill-archive-task`
  hard-failed the `max_inline_lines: 12` rule; user requested a best-practice evaluation
  and reform of the rule.

## 1. General Description

The skill quality gate forbids any fenced code block longer than **12 lines**, as a
**hard CI failure** (`check_inline_efficiency` in `validate_skill.py`). The *principle*
— keep `SKILL.md` lean, push bulk to on-demand resources (progressive disclosure) — is
correct and current. The *implementation* is crude and produces false positives:

- threshold (12) is arbitrary, low, and line-based rather than token-based;
- severity is a single hard FAIL — no warning tier — disproportionate for a style rule
  (compare: Execution Policy checks are `warning-first`);
- no differentiation by fence type — `text` output samples, `mermaid` diagrams, and
  procedural pseudocode are scored identically to bulk source code;
- the remediation hint ("Extract to examples/") is counter-productive for procedural
  content needed on *every* skill run — extraction adds an extra read, costing tokens;
- the fence parser does not validate fence pairing (an unclosed ``` is silently
  swallowed).

The rule's logic is also **duplicated** and its config is **scattered** (see §4 Drift
Map), so any correction must be applied consistently across all copies.

This task reforms the rule to match best practice and re-verifies the CI gate.

## 2. List of Use Cases

### UC-01: Skill author writes a coherent procedural block
**Actors:** Skill author, Orchestrator, CI (`validate_skills.py`)
**Preconditions:** A `SKILL.md` contains one fenced pseudocode/procedure block of
13–30 lines that is core guidance (needed every run).
**Main Scenario:**
1. Author commits the skill.
2. CI runs `validate_skills.py --quiet`.
3. Validator measures the block, applies the reformed two-tier policy.
4. Block within the new threshold → **PASS** (optionally a non-blocking warning).

**Alternative Scenarios:**

**A1: Genuinely oversized bulk block (at step 3)**
1. Block exceeds the FAIL ceiling.
2. Validator emits a hard error with remediation guidance that distinguishes
   *always-needed* (split into labelled sub-blocks) vs *rarely-needed* (extract to
   `resources/`).

**A2: Non-code fence (at step 3)**
1. Block is fenced as `text` / `mermaid` / output sample.
2. Validator exempts or relaxes the limit for non-`code` fences.

**Postconditions:** All 43 catalog skills validate; CI gate reflects real bloat only.

**Acceptance Criteria:**
- ✅ Threshold raised to a best-practice value (≥ 25 lines) **or** switched to a
  token/character budget; value sourced from config, not hard-coded.
- ✅ Two-tier severity: a `warning` band and a `fail` ceiling (single hard FAIL removed).
- ✅ Non-`code`-language fences (`text`, `mermaid`, untagged output samples) are exempt
  or held to a relaxed limit.
- ✅ Remediation message distinguishes always-needed vs rarely-needed content.
- ✅ Fence parser detects an odd/unclosed fence count and reports it explicitly.

### UC-02: Maintainer keeps the rule consistent across all copies
**Actors:** Maintainer
**Preconditions:** The inline rule logic + config exist in multiple files (§4).
**Main Scenario:**
1. Maintainer applies the reform.
2. Every logic copy (`validate_skill.py`, `analyze_gaps.py`) and config copy is updated
   or de-duplicated to a single source.
3. Independent copy in `Universal-skills/skills/skill-creator/` is re-synced.

**Acceptance Criteria:**
- ✅ `validate_skill.py::check_inline_efficiency` and the `analyze_gaps.py` inline loop
  produce identical verdicts (shared module **or** verified-identical logic).
- ✅ `max_inline_lines` value is consistent across `.agent/rules/skill_standards.yaml`
  and all `skill_standards_default.yaml` copies.
- ✅ `Universal-skills/skills/skill-creator/scripts/validate_skill.py` matches the
  agentic-development canonical copy.

### UC-03: CI gate re-verified after the correction
**Actors:** CI, Maintainer
**Main Scenario:**
1. `python System/scripts/validate_skills.py --root . --quiet` runs locally.
2. Result is `43/43 passed`, exit `0`.
3. The reformed validator is exercised against fixture skills (oversized block, non-code
   fence, unclosed fence) to confirm each new branch fires correctly.

**Acceptance Criteria:**
- ✅ Local full-catalog validation green (exit 0) before push.
- ✅ Each new validator branch covered by an explicit check or fixture.
- ✅ GitHub Actions `Framework Gates` → `Skill validate` green after push.

## 3. Non-functional Requirements
- **Backward compatibility:** No currently-passing skill may begin to FAIL because of
  the threshold/severity change. The parser-hardening branch (R-04) *may* surface a
  pre-existing unclosed fence — if so, fix the skill, do not weaken the check.
- **Single source of truth:** Prefer de-duplicating the rule logic over maintaining
  parallel copies; if duplication is retained, it must be deliberate and documented.
- **Safety (meta-operation):** Back up edited files to `.agent/archive/` before changes;
  `skill-self-improvement-verificator` gates both the TASK and the PLAN.
- **No scope creep:** Only the inline-code-block rule is in scope. The `banned_words`
  substring matcher is a related defect but **out of scope** (see §5).

## 4. Constraints and Assumptions

**Drift Map — where the rule lives:**

| Artifact | Role | Sync status |
|---|---|---|
| `.agent/skills/skill-creator/scripts/validate_skill.py` | CI logic (hard FAIL) — `check_inline_efficiency()` | Canonical; hard-linked to `.claude/skills/skill-creator/...` (same inode) |
| `.agent/skills/skill-enhancer/scripts/analyze_gaps.py` | Audit logic — `[Token Efficiency]` gap | **Duplicated** logic, default 12 |
| `Universal-skills/skills/skill-creator/scripts/validate_skill.py` | CI logic copy | **Independent copy**, identical content, different inode — drift risk |
| `.agent/rules/skill_standards.yaml` | **Live** project config (`max_inline_lines: 12`, `inline_exempt_skills`) | Loaded by validator |
| `skill_standards_default.yaml` ×4 (creator/enhancer × agentic/Universal) | Bundled fallback config | All identical |
| `System/scripts/validate_skills.py` | CI runner (shells out per skill) | Symlinked into Universal-skills |
| Docs: `skill-creator/SKILL.md`, `references/default_parameters.md`, `System/Docs/skill-writing.md` | Document the "12" value | Update after logic change |

- **Assumption:** `agentic-development` is the canonical repo; `Universal-skills` consumes
  it via per-item symlinks (`.agent/skills/*`, `System/`) — except the standalone
  `Universal-skills/skills/skill-creator` copy, which must be re-synced explicitly.
- **Constraint:** CI entrypoint is fixed — `framework-gates.yml:49` runs
  `validate_skills.py --root . --quiet`; the reform must not change this invocation.
- **Constraint:** `inline_exempt_skills` (`skill-safe-commands`, `skill-orchestrator-patterns`)
  must keep working; the reform should *reduce* reliance on this allowlist, not break it.

## 5. Open Questions
- **Q1:** Threshold strategy — fixed line count (≥25) vs token/character budget? Token
  budget is more accurate but needs a tokenizer dependency in CI. **Proposed:** raise to
  a fixed line count now (no new dependency); record token-budget as future work.
- **Q2:** Two-tier severity values — proposed `warn > 20`, `fail > 60`. Confirm bands.
- **Q3:** De-duplication target — extract a shared `inline_efficiency.py` importable by
  both `validate_skill.py` and `analyze_gaps.py`, or keep synced copies? Shared module
  is cleaner but adds an import path across two skills.
- **Q4 (out of scope, flagged):** `banned_words: ["should", "can"]` matches substrings
  ("shoulder", "cancel", "scan"). Worth a follow-up task — not addressed here.
