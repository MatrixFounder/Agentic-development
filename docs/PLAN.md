# Development Plan: Task 071 — Retire the Politeness-Filter Rationale; Reposition vdd-sarcastic (C-01, C-03, K2)

**Source spec:** `docs/TASK.md` (Task 071) · **Gate:** `skill-self-improvement-verificator` (Mode B)
**Architecture impact:** none — rationale/wording changes inside existing Tier-2 skills, one `.claude/agents/` wrapper, one example, registry/release docs. **No ARCHITECTURE.md edit** (precedent: 069/070).
**Behavior contract:** zero functional change — no script, pattern, test, CLI, or exit-bar semantics touched. Objective Convergence bars stay byte-identical. Proof: pytest 30/30 unchanged; `validate_skill.py` 43/43; G1/G2 greps.

**Canonical replacement wording (reused on every edited line, adapted only grammatically):**
> Report **every** issue, including low-confidence ones; attach **confidence + severity** to each finding; filtering happens **downstream** — never in the reviewer's head.

**Wording constraint (lesson 070 / TASK G1):** no new text may contain the token "politeness" (retirement notes phrase the old theory as "tone bypasses the model's default agreeableness").

## Phase T0 — Backup (Rollback safety) — workflow §3.1
1. `mkdir -p .agent/archive`
2. Bootstrap files (none edited; backed up per workflow §3.1): `for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done`
3. Edit targets → `.agent/archive/` (flat `<basename>.bak`, disambiguated where names collide):
   `vdd-adversarial-SKILL.md.bak`, `vdd-methodology.md.bak`, `vdd-sarcastic-SKILL.md.bak`, `vdd-sarcastic-usage_example.md.bak`, `skill-adversarial-security-SKILL.md.bak`, `skill-adversarial-performance-SKILL.md.bak`, `critic-security.md.bak`, `SKILLS.md.bak`, `verification_roadmap.md.bak`, `CHANGELOG.md.bak`, `CHANGELOG.ru.md.bak`, `README.md.bak`, `README.ru.md.bak`
4. Capture pre-edit baselines: `python3 -m pytest .agent/skills/security-audit/tests/ -q` (expect 30 passed); `validate_skill.py` full sweep (expect 43/43).

## Phase T1 — R1+R2: K1 rationale swap (`vdd-adversarial`)
1. `SKILL.md` §2 bullet (line 24): `**Forced Negativity**: Zero tolerance…` → `**Exhaustive Reporting** (supersedes "Forced Negativity"): report every issue, including low-confidence ones, with confidence + severity attached — filtering happens downstream. Zero tolerance for "lazy" AI patterns (placeholder comments, generic error handling, inefficient loops).`
2. `SKILL.md` §7 row (line 59): counter-argument → exhaustive-reporting wording; drop `VDD requires Forced Negativity. Politeness hides bugs.`
3. `SKILL.md` frontmatter `version: 1.1` → `1.2`.
4. `references/vdd-methodology.md` §V.2 (line 44) → `Exhaustive Reporting (supersedes "Forced Negativity"): …canonical wording… (The pre-2026 rationale — adversarial tone to bypass the model's default agreeableness — is retired per audit-067 C-01: vendors now train sycophancy out, and the documented recall lever is the reporting-threshold instruction, not tone.)`
5. **Phase check:** `grep -in "politeness\|Forced Negativity" .agent/skills/vdd-adversarial/SKILL.md .agent/skills/vdd-adversarial/references/vdd-methodology.md` → only the two `supersedes` notes. §V.2 stays principle №2 (numbering unchanged); lines 23/46 (C-02 wording) byte-untouched.

## Phase T2 — R3+R7: K2 repositioning (`vdd-sarcastic`)
1. `SKILL.md` frontmatter: `version: 1.2`; `description:` → opt-in delivery-style wording ("stylistic skin over vdd-adversarial mechanics").
2. §2 head: add positioning disclaimer blockquote — tone = stylistic choice, **no evidence base** as a recall lever (audit-067 C-01/C-03); mechanism = **exhaustive reporting + objective bar (§4)**, not meanness; keep-vs-deprecate awaits item 13's A/B.
3. §1 red flag (line 12): "tone it down" → style optional / withholding findings prohibited (canonical wording).
4. §5 row "I don't want to be mean" (line 38, C-03): → meanness is NOT the mechanism; style ≠ success criterion; never soften by withholding findings.
5. §5 row "Sarcasm is unprofessional" (line 40, C-01): → opt-in stylistic choice, no evidence base (see §2 disclaimer); process = exhaustive reporting + Objective Convergence (§4); "if the style gets in the way, drop the style, never the findings."
6. §3 line 24 ("relationship drift") — **DO NOT TOUCH** (C-02, item 8).
7. `examples/usage_example.md`: Roast table gains **Severity + Confidence** columns; add finding #6 with `LOW / Low confidence` (cache may store `None`/error sentinel from `fetch_from_api` — reported anyway per exhaustive-reporting rule); Exit Signal line updated: findings carry confidence + severity, filtering happens downstream, NOT Zero-Slop.
8. **Phase check:** file reads; no "politeness"/"Meanness is the mechanism" tokens; §4 byte-untouched.

## Phase T3 — R4+R5+R6: critics de-mandate (security SKILL + wrapper + performance SKILL)
1. `skill-adversarial-security/SKILL.md`: frontmatter `version: 1.3`, `description:` → "adversarial style (optional sarcastic skin)"; §1 red flag (line 16) `Sarcasm breaks complacency. Use it.` → severity-threshold red flag with canonical wording ("I'll only report the high-severity stuff" -> WRONG…); §2 `**MANDATORY:**` → `**Optional style:**` (MAY adopt persona; no evidence base as recall lever) + `**NOT optional:**` exhaustive reporting + objective bar (§7); §5 step 4 → report per canonical wording, persona optional; §7 `The persona (§2)` → `The optional persona (§2)`.
2. `.claude/agents/critic-security.md` (R5, wrapper sync): `(paranoid sarcastic OWASP auditor)` → `(paranoid OWASP auditor; optional sarcastic skin)`; `Adopt the persona … (mandatory per SKILL §2)` → persona optional per SKILL §2; mandatory = exhaustive reporting (canonical wording) + objective bar (SKILL §7).
3. `skill-adversarial-performance/SKILL.md` (R6): frontmatter `version: 1.1`, `description:` → "(optional sarcastic skin)"; under `## Tone` add style-note line (opt-in delivery style, not the mechanism; canonical wording); Process step 2 `State the problem sarcastically` → `State the problem (sarcastic framing optional — style, never the success criterion)`. Checklists/examples/termination untouched (termination = item 12).
4. **Phase check:** G2 grep tokens (`mandatory per SKILL §2`, `Sarcasm breaks complacency`, `State the problem sarcastically`) → empty across `.agent/ .claude/ System/`.

## Phase T4 — Global gates (TASK §3)
1. **G1:** `grep -ri "politeness filter" .agent/ System/` → empty; hardened: `grep -rin "politeness" .agent/ System/ .claude/` → empty.
2. **G2:** `grep -rinE 'mandatory per SKILL §2|Sarcasm breaks complacency|Meanness is the mechanism|frame ALL feedback sarcastically|State the problem sarcastically' .agent/ .claude/ System/` → empty; `grep -rin "Forced Negativity" .agent/ .claude/ System/` → exactly 2 supersedes-notes.
3. **G3:** `validate_skill.py` × 4 edited skills, then full sweep `.agent/skills/*/` → 43/43.
4. **G4:** `python3 -m pytest .agent/skills/security-audit/tests/ -q` → 30 passed (regression evidence; no scripts touched).

## Phase T5 — R8+R9: registry, release, roadmap, session-state
1. `System/Docs/SKILLS.md` rows 106–108: vdd-sarcastic → opt-in stylistic skin wording; both critics → "(optional sarcastic skin)".
2. `CHANGELOG.md` + `CHANGELOG.ru.md`: new top entry **v3.20.2** (EN primary + RU mirror) — closes C-01/C-03/K2, lists per-file changes, notes zero behavior change + the supersedes-traceability.
3. `README.md` + `README.ru.md`: version header → v3.20.2 (release convention per `3df62a2`/`c348928`).
4. `docs/verification_roadmap.md` item 5: 🔜 → ✅ DONE block (commit/task/gate artifact references, verified-date), mirroring items 3/4 format; Dependencies note "final form (deprecate K2?) waits on 13" stays.
5. Session-state boundary update (`update_state.py`), status `completed-pending-operator-commit`.

## Rollback
Workflow §5: restore every `.agent/archive/*.bak` over its source path. No bootstrap file is edited, so instability risk is confined to the 13 backed-up targets; git (clean tree at start) provides the second-layer rollback.
