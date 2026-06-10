# Development Plan: Task 068 — Adversarial-Security Skill P0 Fixes (C-05 / C-15)

**Source spec:** `docs/TASK.md` (Task 068) · **Gate:** `skill-self-improvement-verificator` (Mode B)
**Architecture impact:** none — prompt-content edits inside one existing Tier-2 skill; `docs/ARCHITECTURE.md` unchanged.

## Phase 0 — T0: Backup (Rollback safety) — workflow §3.1
1. `mkdir -p .agent/archive`
2. Back up every present bootstrap file: `for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done`
3. Back up the edit target: `cp .agent/skills/skill-adversarial-security/SKILL.md .agent/archive/skill-adversarial-security.SKILL.md.bak`
4. **Verify:** backups exist (`ls .agent/archive/`).

**Rollback plan:** restore any edited file from `.agent/archive/<name>.bak` (workflow §5 Fallback). No state migration needed.

## Phase 1 — T1: [R1 / C-05] §7 Termination → objective bar only
Edit `.agent/skills/skill-adversarial-security/SKILL.md` §7 (line ~64–68):
- **Delete** the bullet "You have made at least one snarky comment about a questionable design choice."
- **Rebind** termination to the objective bar exactly as audit P0-1 prescribes: (1) automation **executed** (or honestly reported `scan: NOT RUN` per the new §3), (2) no Critical/High findings from manual review, (3) only bikeshedding/style remains.
- Add a one-line doctrine note: approval binds to the objective bar, never to tone — referencing `vdd-sarcastic` SKILL.md §4 (Objective Convergence).
- **Do not touch** §2 Persona (tone stays mandatory as *style*; it stops being a *success criterion*).

**Verify (atomic):** `grep -n "snarky" SKILL.md` → 0 hits; §7 lists exactly the three objective-bar conditions.

## Phase 2 — T2: [R2 / C-15] §3 Reconnaissance → no-fabrication protocol
Edit same file §3 (line ~29):
- **Delete** "*Mock the results if you cannot run it directly, but assume standard tool outputs (slither/bandit).*"
- **Replace** with: if the script cannot be executed in your context (the `critic-security` subagent has no Bash tool), report `scan: NOT RUN` and proceed with manual review only — **never fabricate scanner output**; the orchestrator runs `run_audit.py` and passes its results into the critic prompt.
- **Consistency sweep (R2c):** §5 Process step 1 "Run Automation (`run_audit.py`)" — align with the new §3 (execute *or* ingest orchestrator-supplied results *or* record `scan: NOT RUN`; never assume).
- Bump frontmatter `version: 1.1` → `1.2`.

**Verify (atomic):** `grep -n "Mock the results\|NOT RUN" SKILL.md` → mock gone, protocol present.

## Phase 3 — T3: [R3] Verification gate
1. **Skill gate:** `python3 .agent/skills/skill-creator/scripts/validate_skill.py` on the edited skill → must pass.
2. **Stale-reference grep:** `grep -rn "snarky\|Mock the results" .claude/agents/ .agent/workflows/ .agent/skills/skill-adversarial-*/ System/Agents/` → expected: zero hits outside historical archives (`docs/`, `.agent/archive/`).
3. **Satellite consistency:** re-read `.claude/agents/critic-security.md` + `.agent/workflows/vdd-multi.md` convergence semantics — must not contradict the new §3/§7 (pre-check says they already state the objective bar; this is a post-edit confirmation).
4. **Minimal-diff invariant:** `diff .agent/archive/skill-adversarial-security.SKILL.md.bak .agent/skills/skill-adversarial-security/SKILL.md` → changes confined to frontmatter version, §3, §5 step 1, §7.

## Phase 4 — T4: [R4] Documentation & finalization
1. CHANGELOG entry (EN in `CHANGELOG.md`, RU in `CHANGELOG.ru.md`): v3.19.2-class fix entry tracing to C-05/C-15 and audit 067.
2. Registry: `System/Docs/SKILLS.md` / `SKILL_TIERS.md` — confirmed generic, **no edit** (verified in Analysis).
3. Session state: `update_state.py` at each phase boundary; final status `done`.
4. No core-prompt change → no session-restart instruction needed.

## Test Coverage note
No runtime code is touched; coverage is prompt-level: the skill-gate validator (structure) + grep assertions (content) + minimal-diff check (scope). This matches the precedent of Tasks 065/066.

## Task list
- [x] T0 Backup (4 files in `.agent/archive/`)
- [x] T1 §7 termination fix (C-05) — snarky condition deleted; objective bar + doctrine note
- [x] T2 §3 no-fabrication fix + §5 consistency + version bump (C-15) — `scan: NOT RUN` protocol; v1.2
- [x] T3 Verification gate — validator PASS (pre-existing warnings only); stale-grep zero hits; satellites consistent; minimal-diff = 4 hunks; full skill gate 43/43
- [x] T4 CHANGELOG v3.19.2 EN+RU + README×2 headers; Code Reviewer APPROVED + Security Auditor PASS
