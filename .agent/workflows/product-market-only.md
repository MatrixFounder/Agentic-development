---
description: Run Market Research Only. Stops after Strategy.
---

# Product Discovery (Market Only)

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "product-market-only-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

1. **Strategic Analysis (p01)**
   - Agent: `p01_strategic_analyst`
   - Task: "Research the market and competition for [Idea]. Produce `docs/product/MARKET_STRATEGY.md`."

2. **Retro (Global Protocol)** — apply `run-feedback` SKILL.md §7 "Retro protocol":
   `claim --run-id "product-market-only-<task-slug>"` → exit 6 = nested, SKIP this step;
   exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
   from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
   collect → triage → file per the skill, and `release`. **Non-blocking**: failures
   here are reported in one line and never change this workflow's outcome.

3. **Report (Termination)**
   - Action: "Market Strategy completed. Review `docs/product/MARKET_STRATEGY.md` to decide if we should proceed."
