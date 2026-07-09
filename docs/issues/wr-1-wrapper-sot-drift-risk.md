---
id: WR-1
type: known-issue
status: documented
opened_at: 2026-06-10
category: wrappers
severity: SEV-3
slug: wr-1-wrapper-sot-drift-risk
---

# Wrapper/SOT drift risk

*(reduced after v3.11.1 thin refactor)*

- **Symptom**: each of the 12 `.claude/agents/*.md` wrappers references exactly one SOT path
  (its primary `System/Agents/XX_*.md` or `.agent/skills/*/SKILL.md`). Two critic wrappers
  also reference the `template_critique.md` / `sarcastic.md` asset paths. If an SOT file is
  renamed or moved, wrappers must be updated manually — no automatic sync.
- **Verification after any rename** in `System/Agents/` or
  `.agent/skills/{vdd-adversarial,skill-adversarial-*}/`, across **all wrapper dirs**
  (v3.20.10, item 6e):
  `grep -rl '<old-path>' .claude/agents/ .gemini/agents/ .codex/agents/ .cursor/agents/ .antigravity/agents/`
  → should return no stale references.
- **Scaffold wrappers are generated**: the non-Claude critic wrappers (`.gemini/`, `.codex/`,
  `.cursor/`, `.antigravity/`) are emitted from
  `.agent/skills/skill-parallel-orchestration/scripts/wrappers_manifest.json` by
  `generate_wrappers.py`. Fix an SOT path drift in the **manifest**, then
  `python3 .agent/skills/skill-parallel-orchestration/scripts/generate_wrappers.py` — never
  hand-edit the generated files. `generate_wrappers.py --check` exits non-zero if any
  on-disk wrapper drifts from the manifest (CI-gateable). Claude Code wrappers stay
  hand-maintained (they are the validated reference/donor).
