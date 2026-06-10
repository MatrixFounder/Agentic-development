# Development Plan: Severity-Escalation Redesign — R3a/R3b/R3d (Task 072)

**Source spec:** `docs/TASK.md` (Task 072, slug `severity-escalation-redesign`).
**Architecture impact:** none — merge-rule wording in workflow/skill documentation; `docs/ARCHITECTURE.md` untouched (living document, no structural change).
**Change class:** pure documentation (no scripts, no code) → no new tests; existing suites run as regression evidence (G4).

## Canonical wording (single source for all 4 locations)

**Rule 3 replacement (vdd-multi.md Phase 2 / SKILL.md §6 — identical modulo "critics"↔"teammates"):**

> 3. **Severity escalation (mechanism-aware)**: all critics share one base model, so same-location agreement is **corroboration** (the finding survived persona/prompt variation), **not independent confirmation** — same-model pairs pick the same wrong answer ~60% of the time when erring (arXiv:2506.07962):
>    - **Same failure mechanism** (the duplicates' exploit/failure scenarios are paraphrases of each other) → do **NOT** escalate. Severity = max of the duplicates (rule 1); tag the merged finding `corroborated` ("flagged by N critics — weak positive signal").
>    - **Different failure mechanisms at the same location** (e.g., critic-logic: unhandled edge case; critic-security: exploitable injection at the same line) → two distinct analyses, not duplicate detection: escalate severity by one level. Mechanism-difference test: the scenarios are not paraphrases of each other — orchestrator judgment, documented in the merged report.

## Steps

### Step 0 — Backup (rollback provision)
```bash
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done
cp .agent/workflows/vdd-multi.md .agent/archive/vdd-multi.md.bak
cp .agent/skills/skill-parallel-orchestration/SKILL.md .agent/archive/skill-parallel-orchestration-SKILL.md.bak
cp .agent/skills/skill-parallel-orchestration/references/sequential-fallback.md .agent/archive/sequential-fallback.md.bak
cp .agent/skills/skill-parallel-orchestration/examples/usage_example.md .agent/archive/usage_example.md.bak
```
**Rollback:** restore each file from its `.agent/archive/*.bak`; bootstrap files via the workflow §5 loop. (Repo is also clean at start — `git checkout -- <file>` is the secondary rollback.)

### Step 1 — `.agent/workflows/vdd-multi.md` (R1: R3a + R3b)
1. Replace Phase-2 rule 3 (line 106) with the canonical wording (actor noun: **critics**).
2. Overlaps placeholder (line 131): `<cross-category items with escalated severity>` → `<corroborated findings (tag, severity = max — no escalation) + different-mechanism items (escalated +1)>`.

### Step 2 — `.agent/skills/skill-parallel-orchestration/SKILL.md` (R2: R3a + R3b)
1. Replace §6 rule 3 (line 107) with the canonical wording (actor noun: **teammates**; example critic names kept verbatim).
2. §2.3 step 3 (line 60): `escalate severity on cross-category overlap` → `tag same-mechanism agreement corroborated, escalate only different-mechanism overlap (§6 rule 3)`.
3. Frontmatter `version: 3.0` → `3.1`; History entry for v3.1.

### Step 3 — `references/sequential-fallback.md` (R3: R3d)
1. Merge step 3 (line 47) → explicit no-escalation sentence: sequential personas never escalate (weakest independence — same session window, same model instance); tag `corroborated` only; different-mechanism findings get at most a `priority` flag, never +1.
2. Anti-patterns line 97: reword "stronger signal" so it claims corroboration-by-persona-variation, not independent confirmation; cross-ref merge step 3.

### Step 4 — `examples/usage_example.md` (R4: walkthrough sync)
Replace the Step-3 escalation bullet with: corroborated tag for same-mechanism agreement (severity = max, no auto-escalation) + escalate only on different-mechanism overlap.

### Step 5 — Verification gates (TASK §3)
```bash
# G1 migration greps
grep -rn "escalate severity by one level" .agent/ .claude/ System/        # only new R3b wording (3 hits expected)
grep -rnE "independently flagging the same location|independently flag the same location|escalation on independent overlap|escalate severity on cross-category overlap" .agent/ .claude/ System/   # empty
# G2 byte-consistency: extract rule-3 block from both files, normalize teammates→critics, diff → empty
# G3 skill gate
python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/skill-parallel-orchestration
# full sweep = 43/43
# G4 regression
python3 -m pytest .agent/skills/security-audit/tests/ -q                  # 30/30
python3 -m pytest .agent/skills/skill-parallel-orchestration/tests/ -q    # green
```

### Step 6 — Documentation & release (R5)
1. `CHANGELOG.md` + `CHANGELOG.ru.md`: **v3.20.3** entry (Changed: severity-escalation redesign R3a/R3b/R3d, C-08).
2. `README.md` + `README.ru.md`: version header bump → v3.20.3 (convention per `3df62a2`).
3. `docs/verification_roadmap.md` item 7: mark R3a/R3b/R3d ✅ done-in Task 072 / v3.20.3; R3c remains pending (tier-diverse 🔜 now, cross-vendor ⏳ item 6); update Dependencies block line "7 R3a/R3b/R3d".
4. Audit artifact `docs/reviews/framework-audit-072.md` (Modes A + B verdicts + gate outputs).
5. Session-state update (phase boundaries: post-plan, post-execution, completion).

## Mode B self-check mapping
- **Verification step:** Step 5 (greps + validate_skill + 2 pytest suites). ✓
- **Rollback:** Step 0 backups + git-clean fallback. ✓
- **Atomicity:** Steps 1–4 are one-file chunks, each independently revertible. ✓
- **Test coverage:** no new framework feature/scripts → no new tests; justification recorded in audit artifact. ✓
