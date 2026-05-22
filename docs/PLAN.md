# Development Plan — Skill-Validator Inline-Rule Reform (Task 064)

**Parent**: [docs/TASK.md](TASK.md) — Skill-Validator Inline-Code-Block Rule Reform
**Architecture**: [docs/ARCHITECTURE.md §8](ARCHITECTURE.md#8-skill-architecture--optimization-standards) — Skill Architecture Standards (Rule 2: Example Separation). No structural change; §8 Rule 2 already cites "50 lines" as the bad case, so the reform aligns the implementation to the existing architecture intent.
**Mode**: Framework Upgrade (`/framework-upgrade`) — meta-operation
**Meta-Audit**: [docs/reviews/framework-audit-064.md](reviews/framework-audit-064.md) (Mode A PASS)

## Approved Design Decisions (from Analysis gate)
- **D1 (Q1)**: Threshold strategy = **fixed line count** (no tokenizer dependency in CI). Token-budget recorded as future work.
- **D2 (Q2)**: **Two-tier severity** — `warn` band `> 20` lines, hard `fail` ceiling `> 60` lines. The single hard FAIL at 12 is removed.
- **D3 (Q3-TASK)**: De-duplication = **verified-identical logic**, not a cross-skill shared module (skills must stay self-contained). A fixture asserts `validate_skill.py` and `analyze_gaps.py` agree.

## Design Spec (inputs for implementation)
- Config keys (replace `max_inline_lines: 12`):
  - `max_inline_lines_warn: 20`
  - `max_inline_lines_fail: 60`
  - `inline_exempt_fence_langs: [mermaid]` — fully exempt (diagrams).
  - `inline_softcheck_fence_langs: [text, console, output]` — fail suppressed, warn kept.
- Code fallback (backward compat): `fail = get('max_inline_lines_fail', get('max_inline_lines', 60))`; `warn = get('max_inline_lines_warn', 20)`.
- Fence info-string = opening-fence line `[3:].strip()`. Empty/untagged + known code langs → full two-tier.
- Parser hardening: after the scan, if still `in_block` → emit explicit "unclosed fence" error.

## Stub-First Strategy
Phase 1 writes fixtures + the verification harness **first** (Red). Phases 2–4 implement logic until the harness is Green. No production logic before its fixture exists.

---

## Phase 0 — Backup (rollback safety)

### T0 — Backup edited files
- [ ] `mkdir -p .agent/archive`
- [ ] Copy each target before edit: `validate_skill.py`, `analyze_gaps.py`, `.agent/rules/skill_standards.yaml`, all `skill_standards_default.yaml`, affected docs → `.agent/archive/`.
- **Verifies**: NFR Safety. **Rollback**: `cp .agent/archive/<file> <orig>`.

## Phase 1 — Fixtures & Harness (Stub-First / Red)

### T1 — Create fixture skills + verification harness
- [ ] Add fixture `SKILL.md` cases under `skill-creator/tests/` (or existing test dir): (a) code block 13–20 lines → expect PASS; (b) 21–60 lines → expect WARN; (c) >60 lines → expect FAIL; (d) `mermaid` block >60 → expect PASS (exempt); (e) `text` block >60 → expect WARN not FAIL; (f) unclosed fence → expect FAIL.
- [ ] Add a test asserting `check_inline_efficiency` (validate_skill.py) and the `analyze_gaps.py` inline logic return the **same** verdict per fixture (D3).
- [ ] Run harness against current code → confirm **Red** (current logic fails fixtures b/d/e/f).
- **Verifies**: UC-01 AC, UC-02 AC, UC-03 (fixture coverage).

## Phase 2 — Logic Reform

### T2 — Reform `check_inline_efficiency()` in `validate_skill.py`
- [ ] Track opening-fence language; apply `inline_exempt_fence_langs` / `inline_softcheck_fence_langs`.
- [ ] Two-tier: `> warn` → warning; `> fail` → error.
- [ ] Detect unclosed fence (odd fence count).
- [ ] Return `(errors, warnings)` tuple instead of a flat error list.
- [ ] Update remediation text: always-needed → "split into labelled sub-blocks"; rarely-needed → "extract to resources/".
- **Verifies**: UC-01 AC 1–5.

### T3 — Update caller in `validate_skill.py`
- [ ] Route `check_inline_efficiency` warnings into the `warnings` channel, errors into `errors` (mirror Execution-Policy warning handling).
- **Verifies**: UC-01 A1/A2.

### T4 — Mirror reform into `analyze_gaps.py` (skill-enhancer)
- [ ] Apply identical thresholds/fence logic; `[Token Efficiency]` gap fires at the `fail` ceiling, soft note at `warn`.
- [ ] Confirm parity test from T1 passes.
- **Verifies**: UC-02 AC 1.

## Phase 3 — Config & Docs

### T5 — Update config (all copies)
- [ ] `.agent/rules/skill_standards.yaml` (live config) — new keys per Design Spec.
- [ ] 4× `skill_standards_default.yaml` (creator/enhancer × agentic) — same.
- [ ] Re-evaluate `inline_exempt_skills` (`skill-safe-commands`, `skill-orchestrator-patterns`): if they pass under the 60-line ceiling, note it (removal optional, not forced).
- **Verifies**: UC-02 AC 2.

### T6 — Update documentation
- [ ] `skill-creator/SKILL.md`, `skill-creator/references/default_parameters.md`, `System/Docs/skill-writing.md` — replace the "12" rule with the two-tier model.
- [ ] ARCHITECTURE.md §8 Rule 2 — optional one-line clarification referencing warn/fail thresholds (living doc, in place).
- **Verifies**: NFR Documentation; Audit Mode A check 3.

## Phase 4 — Sync & Verify

### T7 — Re-sync Universal-skills independent copies
- [ ] `Universal-skills/skills/skill-creator/scripts/validate_skill.py` ← canonical.
- [ ] `Universal-skills/skills/skill-creator|skill-enhancer/scripts/skill_standards_default.yaml` ← canonical.
- [ ] `Universal-skills/skills/skill-enhancer/scripts/analyze_gaps.py` ← canonical.
- [ ] Confirm symlinked artifacts (`.agent/skills/*`, `System/`) need no action.
- **Verifies**: UC-02 AC 3.

### T8 — Full verification
- [ ] `python System/scripts/validate_skills.py --root . --quiet` → `43/43 passed`, exit 0.
- [ ] Run T1 harness → **Green**; each new branch (warn / fail / exempt / softcheck / unclosed) exercised.
- [ ] Confirm `skill-archive-task` still passes (regression check on the original CI failure).
- **Verifies**: UC-03 AC 1–3.

---

## Rollback Plan
On any instability: restore each file from `.agent/archive/` (`cp .agent/archive/<file> <orig>`), re-run T8 to confirm the pre-reform green state.

## Verification Summary (Definition of Done)
- [ ] All 43 catalog skills validate; CI `Skill validate` green.
- [ ] Fixtures cover warn / fail / exempt / softcheck / unclosed branches.
- [ ] `validate_skill.py` and `analyze_gaps.py` verified verdict-identical.
- [ ] Config consistent across `.agent/rules/` + 4 `_default.yaml`; Universal-skills copies re-synced.
- [ ] Docs updated; backups present in `.agent/archive/`.
