# Development Plan — Multi-Critic Objective Convergence (Task 066)

**Parent**: [docs/TASK.md](TASK.md) — Multi-Critic Objective Convergence
**Architecture**: no change (convergence contract lives in critic wrappers + `vdd-multi`/`skill-parallel-orchestration`, not ARCHITECTURE.md).
**Mode**: Framework Upgrade (`/framework-upgrade`)
**Meta-Audit (Mode A)**: [docs/reviews/framework-audit-066.md](reviews/framework-audit-066.md) — APPROVED

## Design Spec
- **New state:** `hallucinating` → **`bikeshedding-only`**. Definition (reused verbatim): *"no legitimate findings remain in this category — only style/nits; objective bar, NOT 'forced to invent problems'."*
- **Enum becomes:** `clean-pass | issues-found | bikeshedding-only`.
- **Termination gate:** category ✓ when `clean-pass` OR `bikeshedding-only` (objective). Drop "critic inventing problems".
- **Noise-filter:** a critic reporting `bikeshedding-only` → drop its low-severity items this iteration (mechanic unchanged, key renamed).

## Phase 0 — Backup
### T0 — Back up the 7 edit targets to `.agent/archive/`
- [ ] `critic-logic.md`, `critic-security.md`, `critic-performance.md`, `vdd-multi.md`, `skill-parallel-orchestration/SKILL.md`, `examples/usage_example.md`, `references/sequential-fallback.md`.

## Phase 1 — Critic enum (E-1)
### T1 — Rename + define the state in the 3 critic agents
- [ ] `.claude/agents/critic-logic.md:13`, `critic-security.md:13`, `critic-performance.md:13`: `hallucinating` → `bikeshedding-only` + objective definition.
- **Verifies**: E1.

## Phase 2 — Consumers (E-2, E-3)
### T2 — `vdd-multi.md` termination gate + noise-filter
- [ ] Phase-3 termination (state 2): objective `bikeshedding-only` wording, not "inventing problems".
- [ ] Merge rule 4: re-key off `bikeshedding-only`; mechanic unchanged. Leave dedup/escalation/severity/iteration-cap untouched.
- **Verifies**: E2, E3, INV.

### T3 — `skill-parallel-orchestration/SKILL.md` merge filter + §2.3 wording
- [ ] Rule 4 (§6): re-key off `bikeshedding-only`.
- [ ] §2.3 step-3 "filter hallucinations" → objective wording.
- **Verifies**: E3, E4.

## Phase 3 — Satellites (E-4)
### T4 — Reference files
- [ ] `examples/usage_example.md` step 4: "clean-pass or hallucinating" → "clean-pass or bikeshedding-only".
- [ ] `references/sequential-fallback.md` merge step 4: "Hallucination filter" → "Bikeshedding filter".
- **Verifies**: E4.

## Phase 4 — Verify
### T5 — Gate + grep + adversarial review
- [ ] `python System/scripts/validate_skills.py --root . --quiet` → green.
- [ ] **Grep:** `hallucinating`/"Hallucination filter" gone from the parallel-critic subsystem (3 critics + vdd-multi + skill-parallel + 2 satellites); `bikeshedding-only` present in all 3 critics + both consumers; surviving `hallucinat*` only in historical artifacts.
- [ ] **INV diff:** dedup / cross-category / severity escalation / `--severity` / iteration cap / Layer A·B rule byte-unchanged vs backup.
- [ ] **Adversarial review** of the diff against the objective bar (dogfood).
- **Verifies**: E1–E4, INV, GATE.

## Rollback Plan
Restore each file from `.agent/archive/<file>.bak`; re-run T5.

## Definition of Done
- [ ] Enum objective across 3 critics; termination + filter key off `bikeshedding-only`; satellites updated.
- [ ] Merge mechanics + Layer A/B rule unchanged; skill gate green; no stale subsystem terminology.
