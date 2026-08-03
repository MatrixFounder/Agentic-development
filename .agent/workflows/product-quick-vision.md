---
description: Run the Quick Product Vision Pipeline (Vision -> Gate -> Handoff). Skips Strategy.
contract:
  version: 1
  loops: []
  calls: []
---

# Product Discovery (Quick Mode)

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "product-quick-vision-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

1. **Product Vision (p02)**
   - Agent: `p02_product_analyst`
   - Task: "Create a Product Vision for [Idea] (Internal Tool/Hackathon). Skip deep market research. Produce `docs/product/PRODUCT_VISION.md`."

2. **Quality Gate (p03)**
   - Agent: `p03_product_director`
   - Task: "Review the vision. If approved, generate the Approval Hash in `docs/product/APPROVED_BACKLOG.md`."

3. **Handoff (Automation)**
   - Load Skill: `skill-product-handoff`
   - Execute: `python3 .agent/skills/skill-product-handoff/scripts/verify_gate.py --file docs/product/APPROVED_BACKLOG.md`
   - Execute: `python3 .agent/skills/skill-product-handoff/scripts/compile_brd.py --market-file docs/product/MARKET_STRATEGY.md --vision-file docs/product/PRODUCT_VISION.md --blueprint-file docs/product/SOLUTION_BLUEPRINT.md --output-file docs/BRD.md`
     *(Note: This will have empty sections for Market Strategy, which is expected for Quick Mode)*
   - Execute: `python3 .agent/skills/skill-product-handoff/scripts/trigger_technical.py docs/BRD.md docs/TASK.md`

4. **Retro (Global Protocol)** — apply `run-feedback` SKILL.md §7 "Retro protocol":
   `claim --run-id "product-quick-vision-<task-slug>"` → exit 6 = nested, SKIP this step;
   exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
   from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
   collect → triage → file per the skill, and `release`. **Non-blocking**: failures
   here are reported in one line and never change this workflow's outcome.
