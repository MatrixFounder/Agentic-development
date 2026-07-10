# Development Plan: Task 088 — clear VDD-adversarial findings (enterprise hardening)

> Mode A/B gates via `skill-self-improvement-verificator` (both PASS — `docs/reviews/framework-audit-088.md`).
> Architecture untouched. Release **v3.20.17**. No product code; one maintenance gate script added.
> Each step clears a verified finding from `docs/reviews/vdd-adversarial-known-issues-format.md`.

## Step 0 — Backup (done)
Bootstrap files + `known-issues-format/SKILL.md` + template + `docs/KNOWN_ISSUES.md` + CHANGELOG/README → `.agent/archive/`.

## Step 1 — F1 (MED): close contract drift with an automated gate
- Add `known-issues-format/scripts/check_contract_sync.py` — compares status/severity vocab + frontmatter keys + index-line format between `SKILL.md` (authority) and the seed template; exit `0`/`1`/`2`.
- Reconcile the drifted glosses across `SKILL.md`, template, and the live ledger.
- Wire the gate into the skill's **Script Contract** + **Validation Evidence** (skill → `hybrid`).
- **Verify:** gate exits 0 in sync; negative test (inject drift) exits 1.

## Step 2 — F2/F3/F4/F7 (skill + template + example)
- F2: seed comment owner `artifact-management` → `known-issues-format`.
- F3: soften the slug machine-equality (AT-7 `≠` counterexample) to a human-readable-stem rule.
- F4: unify the seed "keep/delete" instruction across skill / template / example.
- F7: add commented `resolved_at` / `resolved_by` keys to both frontmatter examples.

## Step 3 — F5/F6/F8 (docs + read-path)
- F5: CHANGELOG squash note on the v3.20.15 entry (EN+RU) — 086→087 landed in one commit.
- F6: "skip if absent — created on the first filed issue" on all 5 read sites (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `01-start-feature.md`, `vdd-01-start-feature.md`).
- F8: name `known-issues-format` at those read sites (TIER-2 discoverability).

## Step 4 — Verify + re-run exit bar
- `validate_skills` 44/44; `check_contract_sync` exit 0 + negative test; version 3.20.17 ×4; 5 read sites guarded.
- Re-evaluate the adversarial Objective-Convergence bar → **PASS**; record §5 in the critique artifact.

## Step 5 — Release
- CHANGELOG v3.20.17 (EN+RU), README stamp, SKILLS.md row (+ gate script). `update_state.py`.

## Rollback
Restore edited files from `.agent/archive/*.bak`; `rm` the gate script; revert version headers. No data migration.
