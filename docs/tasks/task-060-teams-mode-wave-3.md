# Task 060 — Teams Mode Integration (Wave 3: product-pipeline wrappers)

**Parent**: [docs/TASK.md](../TASK.md) — Teams Mode epic

## Goal

Extend `.claude/agents/` with 4 thin Claude Code subagent wrappers for the product-pipeline roles defined in `System/Agents/p01–p04`. Brings total wrapper count to **16** (3 Wave-1 critics + 9 Wave-2 dev-pipeline + 4 Wave-3 product). No workflow rewrites — existing product workflows (`/product-full-discovery`, `/product-market-only`, `/product-quick-vision`) keep working through sequential role-switching. Wrappers enable `subagent_type`-based spawn when useful.

## Scope

**Created (4 wrappers)**:
- `.claude/agents/strategic-analyst.md` → `System/Agents/p01_strategic_analyst_prompt.md`
- `.claude/agents/product-analyst.md` → `System/Agents/p02_product_analyst_prompt.md`
- `.claude/agents/product-director.md` → `System/Agents/p03_product_director_prompt.md`
- `.claude/agents/solution-architect.md` → `System/Agents/p04_solution_architect_prompt.md`

**Updated**:
- `docs/ARCHITECTURE.md` §5.1 — new Wave 3 table; Model policy extended to cover 10 Opus + 6 Sonnet.

**Not in scope**:
- Workflow rewrites (product workflows stay sequential via Stage Cycle).
- `p00_product_orchestrator_prompt.md` — orchestrator role, stays as main-agent persona (nested teams not supported by Claude Code native Teams).
- Wave 4 (Layer B — `TeamCreate`) and Wave 5 (portable generator).

## Design decisions

### Model split (Opus verifier + Sonnet builders)
- **`product-director` → opus** (verifier): applies Adversarial VDD (hallucination check, moat check, fluff check), runs WSJF prioritization, signs off with APPROVAL_HASH. Gate for Product→Technical handoff. Matches Wave 2 pattern (reviewers on Opus) and is explicitly the gatekeeper per SOT §1.
- **`strategic-analyst`, `product-analyst`, `solution-architect` → sonnet** (builders): produce template-driven artifacts (MARKET_STRATEGY.md, PRODUCT_VISION.md, SOLUTION_BLUEPRINT.md) under strict skill templates. Creation work — Sonnet is sufficient at ~5× lower cost.

### `product-director` is a "verifier that writes"
Unlike dev-pipeline reviewers (which return text reports to the orchestrator), `product-director` writes files directly — `APPROVED_BACKLOG.md` or `REVIEW_COMMENTS.md` — because downstream agents consume those specific filenames (`solution-architect` requires `APPROVED_BACKLOG.md` with valid `APPROVAL_HASH` as a security check). The wrapper body documents this exception from the Wave-2 reviewer pattern.

### `solution-architect` verifies APPROVAL_HASH at entry
SOT §4.1 mandates checking that `APPROVED_BACKLOG.md` exists with a valid hash before producing a blueprint. Wrapper body calls this out explicitly — if the hash is missing/invalid, the subagent STOPS and reports a security violation rather than producing output.

## RTM (acceptance criteria)

- `[R1]` `.claude/agents/strategic-analyst.md` — valid thin frontmatter (Read, Write, Edit, Grep, Glob; model: sonnet), SOT pointer to `p01_strategic_analyst_prompt.md`.
- `[R2]` `.claude/agents/product-analyst.md` — valid thin frontmatter (same tools; model: sonnet), SOT pointer to `p02_product_analyst_prompt.md`.
- `[R3]` `.claude/agents/product-director.md` — valid thin frontmatter (Read, Write, Edit, Grep, Glob, Bash; model: opus), SOT pointer to `p03_product_director_prompt.md`. Body documents WSJF + sign-off scripts.
- `[R4]` `.claude/agents/solution-architect.md` — valid thin frontmatter (Read, Write, Edit, Grep, Glob; model: sonnet), SOT pointer to `p04_solution_architect_prompt.md`. Body documents APPROVAL_HASH verification.
- `[R5]` `docs/ARCHITECTURE.md` §5.1 — new Wave 3 table present with 4 rows (SOT, tools, model, role); Model policy updated to 10 Opus + 6 Sonnet.
- `[R6]` YAML frontmatter valid for all 16 wrappers (name matches filename; required fields present; tools field is simple names only).
- `[R7]` No regression — Wave 1 and Wave 2 artifacts (`.agent/workflows/*`, `.claude/agents/critic-*`, `.claude/agents/{analyst,architect,…}.md`) unchanged.

## Verification

- **Structural**: `ls .claude/agents/*.md | wc -l` → 16. `python3 yaml-validate-all.py` → all valid.
- **Coherence**: `grep -l 'p0[1-4]' .claude/agents/` → each new wrapper references its unique SOT.
- **Regression**: `git diff` limited to `.claude/agents/{strategic,product,solution}*.md`, `docs/ARCHITECTURE.md`, `docs/TASK.md`, `docs/tasks/task-060-*.md`, `CHANGELOG.*`, `README*`.
- **Manual (post-merge, in IDE)**: `/agents` shows 16 wrappers with infinitive-verb descriptions; attempting Write inside a read-only reviewer subagent fails with permission error.

## Out-of-scope reminder

- Wave 4: Layer B (native `TeamCreate` + `/teams-vdd-multi`).
- Wave 5: portable generator.
- `p00_product_orchestrator_prompt.md` — meta-orchestrator, main-agent role only.
