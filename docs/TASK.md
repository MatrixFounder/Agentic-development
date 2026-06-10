# Technical Specification: Retire the Politeness-Filter Rationale; Reposition vdd-sarcastic (C-01, C-03, K2)

### 0. Meta Information
- **Task ID:** 071
- **Slug:** `retire-politeness-filter-rationale`
- **Mode:** Framework Upgrade (meta-operation — modifies Tier-2 adversarial skills, one critic wrapper, one example, registry rows)
- **Type:** P1 modernization, roadmap item 5. Closes audit-067 claims **C-01** ("Forced Negativity bypasses LLM politeness filters" — Outdated) and **C-03** ("Meanness is the mechanism" — Outdated/Unsubstantiated as causal); implements the **K2 repositioning** ("opt-in stylistic skin with explicit no-evidence-base disclaimer").
- **Workflow:** `/framework-upgrade` (with `skill-self-improvement-verificator` gate, Modes A + B).
- **Source:** User request (2026-06-10): "выполни ### 5. 🔜 [C-01, C-03, K2]" + `docs/verification_roadmap.md` item 5 + `docs/reviews/verification-stack-currency-audit-067.md` (claims C-01, C-03; component verdicts K1, K2; backlog item 5).

## 1. General Description

The adversarial-review stack justifies harsh/sarcastic tone with a GPT-4-era theory: *"Forced Negativity bypasses the politeness filters inherent in standard LLM interactions."* Audit 067 scored this **Outdated**: vendors now train sycophancy out (GPT-5 system card −70–75%; Opus 4.5/4.6 system cards), harsh judge prompts are documented to **inflate false positives** (arXiv:2603.00539, 2604.16790), there is **zero** direct evidence for sarcasm as a recall lever, and the vendor-documented recall lever is the **reporting-threshold instruction**, not tone (Opus 4.7+ migration guidance). Claim C-03 ("Meanness is the mechanism") is additionally Unsubstantiated as causal.

**The replacement rationale (canonical wording, reused across all edits):**
> Report **every** issue, including low-confidence ones; attach **confidence + severity** to each finding; filtering happens **downstream** — never in the reviewer's head.

**What this task is NOT:** K1's mechanics (Objective Convergence bar, mandatory critique template + Hallucination Check, decision tree, failure simulation) scored **Current** and stay byte-untouched. The fresh-context practice and its "relationship drift" wording are claim **C-02 = roadmap item 8** — explicitly out of scope here, even where those lines sit in the same files. The keep-vs-deprecate decision for `vdd-sarcastic` awaits the pre-registered A/B (item 13); this task implements the interim roadmap branch: **keep as opt-in skin + disclaimer**.

**Blast radius (established by repo-wide grep, 2026-06-10):** the rationale token "politeness" appears in exactly 3 framework files (`vdd-adversarial/SKILL.md:59`, `vdd-adversarial/references/vdd-methodology.md:44`, `vdd-sarcastic/SKILL.md:40`); mandatory-sarcasm directives in 2 (`skill-adversarial-security/SKILL.md:16,19` and its wrapper `.claude/agents/critic-security.md:8` "(mandatory per SKILL §2)"); the C-03 claim in 1 (`vdd-sarcastic/SKILL.md:38`); a procedural sarcasm instruction in 1 (`skill-adversarial-performance/SKILL.md:68` "State the problem sarcastically"). `System/Agents/` is clean. `docs/verification_roadmap.md` and `docs/reviews/*` quote the retired claim as documentation/immutable audit history — excluded by design (acceptance grep scope: `.agent/ System/` + wrappers).

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | Target file(s) | Audit claim | Verification |
|----|-------------|----------------|-------------|--------------|
| R1 | Replace the **Forced Negativity** principle with **Exhaustive Reporting** (supersedes-note kept for traceability); reword the §7 "too harsh" rationalization row (drop "Politeness hides bugs") | `.agent/skills/vdd-adversarial/SKILL.md` (§2 principle bullet, §7 table row; version 1.1→1.2) | C-01 | File read; greps G1/G2; `validate_skill.py` |
| R2 | Reword methodology principle §V.2 to the exhaustive-reporting rationale with explicit retirement note (note's wording must NOT contain the token "politeness") | `.agent/skills/vdd-adversarial/references/vdd-methodology.md` (§V.2) | C-01 | File read; grep G1 |
| R3 | Reposition K2 as **opt-in stylistic skin**: add §2 positioning disclaimer ("tone is a stylistic choice with no evidence base; the mechanism is exhaustive reporting + objective bar, not meanness"); reword §1 red-flag "tone it down" (style optional / findings non-negotiable), §5 rows "Meanness is the mechanism" (C-03) and "bypass politeness filters" (C-01); update frontmatter description | `.agent/skills/vdd-sarcastic/SKILL.md` (version 1.1→1.2) | C-01, C-03, K2 | File read; greps G1/G2; `validate_skill.py` |
| R4 | Soften mandatory persona to **optional style note** + make exhaustive reporting the non-optional part: §1 red-flag "Sarcasm breaks complacency. Use it." → exhaustive-reporting red flag (also fixes severity-threshold literalism for this prompt, per item 5.1 parenthetical); §2 MANDATORY → optional; §5 step 4 sync; §7 "persona" → "optional persona"; description sync | `.agent/skills/skill-adversarial-security/SKILL.md` (version 1.2→1.3) | C-01, C-05-adjacent | File read; greps G1/G2; `validate_skill.py` |
| R5 | Wrapper sync (anti-drift, KNOWN_ISSUES Wave-1/2 discipline): "(mandatory per SKILL §2)" → optional-persona wording; mandatory = exhaustive reporting + objective bar | `.claude/agents/critic-security.md` | C-01 | Grep G2 (wrapper-drift) |
| R6 | Remove the last procedural sarcasm mandate: Process step 2 "State the problem sarcastically" → optional framing; add one style-note line under ## Tone | `.agent/skills/skill-adversarial-performance/SKILL.md` (version 1.0→1.1) | acceptance "sarcasm nowhere mandatory" | File read; grep G2; `validate_skill.py` |
| R7 | Update the K2 example to demonstrate the new reporting contract: Roast table gains **Severity + Confidence** columns + one explicitly low-confidence finding; exit-check line states findings are filtered downstream | `.agent/skills/vdd-sarcastic/examples/usage_example.md` | acceptance "examples updated" | File read |
| R8 | Registry sync: 3 rows (vdd-sarcastic → "opt-in stylistic skin…", adversarial-security/-performance → "optional sarcastic skin") | `System/Docs/SKILLS.md` | workflow §4.2 | File read |
| R9 | Release bookkeeping: CHANGELOG EN+RU **v3.20.2**; README version-header bump (release convention per `3df62a2`/`c348928`); roadmap item 5 → ✅ DONE; session-state at phase boundaries | `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md`, `README.ru.md`, `docs/verification_roadmap.md` | — | File reads |
| R10 | Acceptance gates pass (G1–G4 below) | — | item 5 acceptance | Bash outputs in PLAN/audit artifact |

## 3. Acceptance Criteria (Gates)

- **G1 (roadmap acceptance, verbatim):** `grep -ri "politeness filter" .agent/ System/` → **empty**. Hardened form also run: `grep -rin "politeness" .agent/ System/ .claude/` → empty (new wording must not reintroduce the token; lesson 070: never let your own edit trip your own acceptance grep).
- **G2 (sarcasm nowhere mandatory + wrapper drift):** `grep -rinE 'mandatory per SKILL §2|Sarcasm breaks complacency|Meanness is the mechanism|frame ALL feedback sarcastically|State the problem sarcastically' .agent/ .claude/ System/` → empty; `grep -rin "Forced Negativity" .agent/ .claude/ System/` → only the two `(supersedes "Forced Negativity")` traceability notes (R1, R2) and vdd-sarcastic's §1 line is reworded.
- **G3 (skill quality gate):** `validate_skill.py` per edited skill; full sweep across `.agent/skills/*/` = **43/43** (baseline).
- **G4 (regression evidence):** `python3 -m pytest .agent/skills/security-audit/tests/ -q` = 30/30 (no scripts touched in this task — pure-docs change; suite run as no-regression proof).

## 4. Out of Scope (considered and excluded — with reasons)

1. `.agent/workflows/vdd-03-develop.md` Sarcasmotron persona overlay — opt-in VDD workflow identity; mandates harsh *persona*, not sarcasm, carries **no** retired rationale, and its exit is already Objective Convergence. K2's repositioning ("opt-in skin") is exactly what /vdd-* workflows are.
2. `skill-adversarial-security/references/prompts/sarcastic.md` — content of the now-optional skin; no mechanism claims. Stays as the optional persona definition.
3. "Relationship drift" / fresh-context wording (`vdd-sarcastic:24`, `vdd-adversarial:25`, `vdd-methodology:23,46`) — claim **C-02 = roadmap item 8**.
4. Critic model-pin hygiene & full severity-threshold-literalism audit of all wrappers — roadmap item 9 (R4 fixes only the one prompt line that item 5.1 explicitly names).
5. Deprecation of `vdd-sarcastic` — deferred to item 13's A/B outcome (roadmap: "final form waits on 13").
6. `docs/verification_roadmap.md` item-5 body and `docs/reviews/verification-stack-currency-audit-067.md` — backlog documents/immutable audit history quoting the retired claim; only the roadmap **status marker** changes (R9).

## 5. Open Questions
None. The roadmap pre-specifies wording, file list, and acceptance; the only judgment calls (R5 wrapper sync, R6 perf-critic line, G1 hardened grep) follow from the acceptance criteria and the documented Wave-1/2 anti-drift discipline, and are recorded above.
