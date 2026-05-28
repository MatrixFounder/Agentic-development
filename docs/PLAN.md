# Development Plan — Reviewers Hardening (Task 065)

**Parent**: [docs/TASK.md](TASK.md) — Reviewers Hardening (provable clean review + objective Sarcasmotron exit, cross-vendor)
**Architecture**: [docs/ARCHITECTURE.md](ARCHITECTURE.md) — no structural change. The reviewer output contract and Sarcasmotron exit criterion live in prompts/skills, not in ARCHITECTURE.md (only a one-line flow mention at §line 92). No edit required.
**Mode**: Framework Upgrade (`/framework-upgrade`) — meta-operation
**Meta-Audit (Mode A)**: [docs/reviews/framework-audit-065.md](reviews/framework-audit-065.md) — **APPROVED**

## Approved Design Decisions (from Analysis gate)
- **D1 (Q1)**: "Verified" block = **markdown body only**, conditional on `has_critical_issues = false`. No structured flag.
- **D2 (Q2)**: Structured superset = `{ has_critical_issues, e2e_tests_pass, stubs_replaced, review_status }`. `comments` = prose body, never a JSON key.
- **D3**: New Sarcasmotron exit label = **"Objective Convergence"**, applied to all four authoritative definitions identically.
- **D4 (Epic D)**: framework-upgrade backup/rollback iterates over present bootstrap files `CLAUDE.md AGENTS.md GEMINI.md` via a shell loop that skips absent files.

## Design Spec (inputs for implementation)

### Reviewer JSON footer (new superset) — replaces `09_…` lines 61-67
```json
{
  "review_status": "APPROVED | REJECTED",
  "has_critical_issues": false,
  "e2e_tests_pass": true,
  "stubs_replaced": true
}
```
- `has_critical_issues` semantics **unchanged** (sole control-flow key; DECISION TABLE untouched).
- `comments`/prose report stays in the text body, not the footer.

### "Verified" block (markdown, report body) — added to `09_…` report format
Appears when `has_critical_issues = false`:
```markdown
## Verified (clean pass)
- Requirements checked: <TASK req IDs / acceptance criteria cross-checked>
- Edge cases considered: <list>
- Tests observed: <which E2E/unit results were inspected>
```
Tiers (🔴/🟡/🟢), three-pillar structure, compliance frame, quality-gate role: **unchanged**.

### Objective Convergence — canonical wording (reused verbatim across all 4 defs)
> **Exit Strategy — Objective Convergence.** Approve **only when all four hold**: (1) the full test run has actually been executed (not assumed); (2) zero CRITICAL findings; (3) zero legitimate findings in logic / security / slop; (4) only bikeshedding/style remains. Until all four hold → **REJECT**. Approval is bound to this objective bar — **never** to "I'm forced to invent nitpicks." Stance unchanged: assume broken until proven; the burden of proof is on the code.

### framework-upgrade backup/rollback (Epic D)
- Backup (Step 3.1): `for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done`
- Fallback (Step 5): `for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f ".agent/archive/$f.bak" ] && cp ".agent/archive/$f.bak" "$f"; done`

## Stub-First note (prompt-edit analogue)
There is no compile/test cycle for prompt text. The Stub-First analogue: **Phase 0 backup first (rollback safety)**, then make additive edits, then **verify** with the skill quality gate + consistency greps + prompt-level scenario reasoning (TASK §7). No edit is considered done until its verification grep passes.

---

## Phase 0 — Backup (rollback safety) — Audit Mode B requirement

### T0 — Back up every edited file to `.agent/archive/`
- [ ] `mkdir -p .agent/archive`
- [ ] Copy each target before edit: `09_code_reviewer_prompt.md`, `01_orchestrator.md`, `skill-orchestrator-patterns/SKILL.md`, `code-reviewer.md`, `vdd-03-develop.md`, `vdd-adversarial/SKILL.md`, `vdd-sarcastic/SKILL.md`, `vdd-methodology.md`, `vdd-05-run-full-task.md`, `WORKFLOWS.md`, `framework-upgrade.md` → `.agent/archive/`.
- **Verifies**: NFR Safety. **Rollback**: `cp .agent/archive/<file>.bak <orig>`.

## Phase 1 — Reviewer: Verified block + contract superset (Epics A, B)

### T1 — `System/Agents/09_code_reviewer_prompt.md`: Verified block + footer superset
- [ ] Step 3 Content Requirements: add item 5 — **"Verified" block (when `has_critical_issues = false`)**: verified requirements + edge cases (markdown body).
- [ ] Step 4 JSON footer → superset `{review_status, has_critical_issues, e2e_tests_pass, stubs_replaced}` (per Design Spec); note `comments`/prose stays in body.
- [ ] Preserve tiers, three pillars, compliance frame (A4).
- **Verifies**: A1, A3, A4. **RTM**: A-1, A-2, B-1.

### T2 — `.agent/skills/skill-orchestrator-patterns/SKILL.md`: align Extended Schema (Code Reviewer)
- [ ] Lines 126-133: drop `comments` as a key; reframe it as the prose report body (comment line); add `review_status`; keep `has_critical_issues`, `e2e_tests_pass`, `stubs_replaced`.
- [ ] **Do NOT touch the DECISION TABLE (lines 57-64).**
- **Verifies**: A2, A3. **RTM**: B-1, B-2.

### T3 — `System/Agents/01_orchestrator.md`: align Step 11 Expected line
- [ ] Line 89: `Expected:` → structured footer `{ review_status, has_critical_issues, e2e_tests_pass, stubs_replaced }` **+ prose review report** (reframe `comments` as prose, not a key).
- **Verifies**: A3. **RTM**: B-1, B-2.

### T4 — `.claude/agents/code-reviewer.md`: verify wrapper footer matches superset
- [ ] Confirm line 13 footer = superset. It already lists `{review_status, has_critical_issues, stubs_replaced, e2e_tests_pass}` → **already correct**; normalize key order to match `09_…` for readability (optional, cosmetic). No semantic change.
- **Verifies**: A3, C1 (Claude-Code wrapper consistency). **RTM**: B-1.

## Phase 2 — Sarcasmotron: objective exit criterion (Epic C)

### T5 — `.agent/workflows/vdd-03-develop.md`: objective overlay
- [ ] Line 19 (Exit Strategy rule 4) + line 23 (Refinement Strategy APPROVED): replace the "forced to hallucinate nitpicks → approve" trigger with the **Objective Convergence** wording (Design Spec). Keep hostile rules 1-3.
- **Verifies**: B1, B2. **RTM**: C-1, C-2.

### T6 — `.agent/skills/vdd-adversarial/SKILL.md`: Convergence Signal → objective (via skill-enhancer)
- [ ] §"Convergence Signal (Exit Strategy)" (lines 28-29): replace hallucination-based termination with Objective Convergence.
- **Verifies**: B1, B3. **RTM**: C-1.

### T7 — `.agent/skills/vdd-sarcastic/SKILL.md`: Convergence Signal → objective (via skill-enhancer)
- [ ] §4 (lines 27-30): replace with Objective Convergence; update the §1 red-flag (line 13) and §5 rationalization-table row (line 39) that reference "the exit signal" to point at the objective bar, not "can't find bugs → invent".
- **Verifies**: B1, B3. **RTM**: C-1.

### T8 — `.agent/skills/vdd-adversarial/references/vdd-methodology.md`: §IV rewrite
- [ ] §IV "Convergence and the Exit Strategy" (lines 37-40): replace hallucination-based termination with Objective Convergence; keep "Zero-Slop"/"Maximum Viable Refinement" framing but bind the exit to the objective bar.
- **Verifies**: B1, B3. **RTM**: C-1.

### T9 — Terminology refresh in referencing files (no mechanics)
- [ ] `vdd-05-run-full-task.md` lines 13, 17, 20, 35: `Hallucination Convergence` → `Objective Convergence`; line 35 metric reframed (post-refinement Objective-Convergence APPROVED vs first-pass clean APPROVED). **Loop mechanics (3-REJECT/escalation/HITL/persist order) untouched.**
- [ ] `System/Docs/WORKFLOWS.md` line 206: update the exit-rule description to the objective criterion.
- **Verifies**: C2. **RTM**: C-3.

### T9b — Normative residuals caught by the Phase-4 adversarial review (RTM C-4)
- [ ] `.agent/workflows/vdd-adversarial.md` (step 2c): "terminate when hallucinations dominate" → Objective Convergence.
- [ ] `System/Docs/VDD.md` (cycle step 4): "Hallucination Exit" → Objective Convergence.
- [ ] `System/Docs/TDD_VS_VDD.md` (Exit Condition cell): "Adversary runs out of valid critiques" → objective bar.
- [ ] Out-of-scope boundary (documented, not changed): `/vdd-multi` + `skill-parallel-orchestration` `convergence: hallucinating` dedup-filter; historical `security-audit/docs/vdd-round*-critique.md`.
- **Verifies**: C2. **RTM**: C-4.

## Phase 3 — framework-upgrade vendor-aware backup (Epic D)

### T10 — `.agent/workflows/framework-upgrade.md`: bootstrap-file-aware backup/rollback
- [ ] Step 3.1 Backup: replace the `cp GEMINI.md …` line with the loop over `CLAUDE.md AGENTS.md GEMINI.md` (skips absent).
- [ ] Step 5 Fallback: replace the single-file restore with the matching restore loop.
- **Verifies**: D1. **RTM**: D-1.

## Phase 4 — Verification

### T11 — Gate + consistency greps + adversarial review
- [ ] `python System/scripts/validate_skills.py --root . --quiet` → green (edited skills `vdd-adversarial`, `vdd-sarcastic` still pass).
- [ ] **Contract grep**: all four reviewer-contract definitions list the same structured superset; `comments` appears only as prose, never a footer key.
- [ ] **Criterion grep**: no residual subjective "forced to invent/hallucinate → approve" wording in the 4 Sarcasmotron defs; `grep -rn "Hallucination Convergence"` returns only historical artifacts (CHANGELOG, docs/tasks, docs/plans, latest.yaml decision logs) — **not** live definitions.
- [ ] **Wrapper-drift grep** (KNOWN_ISSUES §Wave-1/2): `grep -l` for old SOT paths in `.claude/agents/` → none stale; `code-reviewer.md` footer matches `09_…`.
- [ ] **framework-upgrade**: Step 3.1/Step 5 snippets reference all three bootstrap files; shell-loop is syntactically valid and skips absent files.
- [ ] **Adversarial (Sarcasmotron / VDD) review** of the full diff for drift, contract breakage, tone regression, and control-flow invariance — applying the *new* Objective-Convergence bar to this very change.
- **Verifies**: A1-A4, B1-B3, C1, C2, D1; TASK §7 validation.

---

## Rollback Plan
On any instability: restore each file from `.agent/archive/` (`cp .agent/archive/<file>.bak <orig>`), re-run T11 to confirm the pre-change green state.

## Verification Summary (Definition of Done)
- [ ] Reviewer report defines a Verified block for clean passes; footer is the superset; tiers/compliance unchanged.
- [ ] All four reviewer-contract definitions agree on the superset; `comments` is prose everywhere.
- [ ] `has_critical_issues` + DECISION TABLE byte-identical; orchestrator control-flow unchanged.
- [ ] All four Sarcasmotron definitions state the identical Objective-Convergence criterion; no residual subjective wording.
- [ ] vdd-05 + WORKFLOWS.md terminology refreshed; loop mechanics untouched.
- [ ] framework-upgrade backs up/restores all present bootstrap files.
- [ ] `validate_skills.py` green; wrapper-drift grep clean; backups present in `.agent/archive/`.
