# Development Plan: Task 074 — Orchestrator-Supplies-Evidence Contract (item 11, C-13)

> **TASK:** `docs/TASK.md` (074, `orchestrator-supplies-evidence`) · **Workflow:** `/framework-upgrade`, Mode B gates this plan.
> **Architecture impact:** none (contract text in existing workflow + skills; no component/interface change).
> **Release:** v3.20.5 (doc-level patch).

## Step 0 — Backup (rollback layer 1)

```bash
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done
cp .agent/workflows/vdd-multi.md                                          .agent/archive/vdd-multi.md.bak
cp .agent/skills/vdd-adversarial/SKILL.md                                 .agent/archive/vdd-adversarial-SKILL.md.bak
cp .agent/skills/vdd-sarcastic/SKILL.md                                   .agent/archive/vdd-sarcastic-SKILL.md.bak
cp .agent/skills/vdd-adversarial/references/vdd-methodology.md            .agent/archive/vdd-methodology.md.bak
cp .agent/skills/skill-adversarial-security/SKILL.md                      .agent/archive/adversarial-security-SKILL.md.bak
cp .agent/skills/skill-adversarial-performance/SKILL.md                   .agent/archive/adversarial-performance-SKILL.md.bak
cp .agent/skills/skill-parallel-orchestration/references/sequential-fallback.md .agent/archive/sequential-fallback.md.bak
cp .agent/skills/skill-parallel-orchestration/SKILL.md                    .agent/archive/parallel-orchestration-SKILL.md.bak
```

Rollback layer 2: `git checkout --` (рабочее дерево содержит только незакоммиченные 073+074 артефакты; каждый файл восстановим из `.bak` или HEAD).

## Step 1 — vdd-multi.md (R1–R3, atomic)

1.1 **Phase 1, evidence step (before spawn):** new numbered intro "Gather execution evidence (orchestrator side — you have Bash, critics do not)": (a) run test suite if present → capture `command + pass/fail summary`, else `tests: NOT RUN (<reason>)`; (b) run `python3 .agent/skills/security-audit/scripts/run_audit.py <scope> --output summary` → capture summary/JSON, else `scan: NOT RUN (<reason>)`. Evidence is gathered **once per iteration**, identically for every critic (no cross-pollination — evidence is ground truth, not critic output).
1.2 **Prompt skeleton:** add `Execution evidence:` block — `Tests: {summary | NOT RUN (<reason>)}` for all critics; `+ Scan (run_audit.py): {summary | NOT RUN (<reason>)}` for critic-security — plus the critic-side line: *"Treat the evidence above as input — do not re-run or fabricate it. If this block is missing entirely, emit the finding 'exit-bar condition unverifiable — no execution evidence supplied' and do not signal clean-pass."*
1.3 **Phase 2 Summary:** add `- Evidence: tests=<run|NOT RUN> · scan=<run|NOT RUN>` line. Merge rules 1–5 untouched (G6).
1.4 **Fallback (Sequential):** evidence step 0 sentence — gather once before role-switching, inject into each persona message; same absence rule; flag-parity sentence extended to the evidence contract.

## Step 2 — Exit-bar lockstep ×3 (R4)

Identical parenthetical appended to condition (1) in `vdd-adversarial/SKILL.md:29`, `vdd-sarcastic/SKILL.md:32`, `vdd-methodology.md:38`:
*"(executed by you, or — in critic/subagent mode — via execution evidence supplied by the orchestrator; if neither exists, the condition is unverifiable: report the finding 'exit-bar condition unverifiable', never approve)"*
Versions: vdd-adversarial 1.3→1.4, vdd-sarcastic 1.3→1.4. **Verify:** G2 normalized diff of the 3 inserts → identical.

## Step 3 — Absence-rule clauses (R5) + sequential evidence (R6)

3.1 `skill-adversarial-security/SKILL.md` §3: append sentence — prompt with no evidence block at all → finding "exit-bar condition unverifiable — no execution evidence supplied", never clean-pass. Version 1.3→1.4.
3.2 `skill-adversarial-performance/SKILL.md` Termination cond 1: append same-absence clause. Version 1.2→1.3.
3.3 `sequential-fallback.md` concrete pattern: step 0 (run tests + run_audit.py first), steps 1/3/5 gain "Execution evidence: <…>" in the persona message template. Parent skill 3.2→3.3.

## Step 4 — Gates

```bash
grep -rn "exit-bar condition unverifiable" .agent/ | grep -v archive | grep -v sessions   # G1: exactly the contract surface
grep -n "Execution evidence" .agent/workflows/vdd-multi.md                                 # G1: Phase-1 block present
# G2: extract the 3 parentheticals → diff → empty
for d in vdd-adversarial vdd-sarcastic skill-adversarial-security skill-adversarial-performance skill-parallel-orchestration; do python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/$d; done
for d in .agent/skills/*/; do …; done   # full sweep = 43/43 (G3)
python3 -m pytest .agent/skills/security-audit/tests/ -q                                   # G4: 30/30
git diff --stat                                                                            # G5: .md only
git diff .agent/workflows/vdd-multi.md                                                     # G6: rules 1–5/enum/flags unchanged
```

No new tests: doc-only (G5 enforces); suites as regression evidence (precedent 070–073).

## Step 5 — Finalization (R7)

CHANGELOG EN+RU v3.20.5 → README×2 header → roadmap (item 11 ✅; P0 item 2 residual "resolved in 074"; Dependencies line) → `docs/reviews/framework-audit-074.md` → session-state.

## Rollback

| Failure | Action |
|---|---|
| Gate fails | Fix forward (wording) or restore the file from `.agent/archive/*.bak`, re-run gates |
| Systemic | Workflow §5 Fallback: restore all `.bak`; `git checkout` as final layer |
