You are an expert Product Manager and Agentic Framework Engineer specializing in early-stage product discovery and development estimation in 2026, with deep knowledge of Lean Startup, Agile, RICE/WSJF prioritization, LLM-accelerated development, and indie-hacker practices.

Your task is to refactor and upgrade the following skills in the Agentic-development framework:
- skill-product-solution-blueprint (including scripts/calculate_roi.py)
- skill-product-analysis
- skill-product-backlog-prioritization
- skill-product-handoff 

All technical parameters of the skill-scripts must be described in file System/Docs/SKILLS.md (at this moment not presented in full manner).  Strictly follow rules of skill-forming listed in System/Docs/SKILLS.md

Key improvements required:

1. **Granular Sizing**:
   - Shift from epic-level counting of S/M/L to user-story-level T-shirt sizing.
   - First, generate a detailed backlog of user stories/use cases from the product idea.
   - Then, assign S/M/L/XL (or XS–XXL) to each story individually.
   - Calibrate base hours: start with LLM-adjusted values (S=20h, M=60h, L=160h, XL=400h) and allow tuning based on tech stack, team velocity, and historical data. These parameters must be encapsulated in the separate file as customizable yaml-file in the same folder as the script (sizing_config.yml). 
- add detailed description of this skill to the playbook configuration with examples (file System/Docs/PRODUCT_DEVELOPMENT.md)

2. **Enhanced ROI Calculation**:
   - Upgrade calculate_roi.py to a more sophisticated model:
     - Inputs: story sizes, hourly_rate, llm_acceleration_factor (default 0.5–0.7), infra_cost/month, cac_per_user, monthly_arpu, churn_rate, growth_rate, som_users.
     - Calculate: total_effort_hours (with LLM discount), dev_cost (+30% buffer for integration/risks), annual_cost (incl. infra), LTV = ARPU / churn, total_revenue = SOM × LTV × growth, ROI = (revenue - costs)/costs, payback_period, NPV (discount 20%).
     - Add risk-adjusted score and sensitivity analysis (best/worst case).
     - Output structured JSON + Markdown summary with clear verdict (Strong Go / Consider / No-Go).

3. **LLM Acceleration Integration**:
   - For each story, estimate "LLM-friendliness" (0–1) and apply multiplier.
   - Add guidance: boilerplate/UI/tests get higher acceleration.

4. **Full Product Scoring Matrix**:
   - In skill-product-analysis: 10-factor matrix (Market Size, Problem Intensity, Solution Fit, Moat, Timing, Competition, Monetization, Technical Risk, Founder Fit, Trend Alignment).
   - Score each 1–10, weighted sum → Overall Product Score + Risk Level.
- all calculations must be incorporated into corresponding scripts 

5. **Prioritization**:
   - In skill-product-backlog-prioritization: implement RICE/RICEF or WSJF automatically using sized effort and estimated value/impact.
   - Output prioritized backlog with cumulative effort and phased roadmap (MVP, V1, V2).

6. **Prompt & Output Best Practices**:
   - All skills must use Chain-of-Thought reasoning, few-shot examples (include successful cases like Superhuman, Notion, and failures).
   - Structured outputs: YAML/JSON for parsing + human-readable Markdown.
   - Adversarial critique section: "Potential flaws and mitigations".
   - Tool calls for market research when needed.

7. **Backward Compatibility**:
   - Keep simple mode for quick indie estimates (original S/M/L count).
   - Add advanced mode with full story breakdown.

Generate:
- Updated directory structure suggestions
- New/updated prompt files for each skill
- Patched calculate_roi.py code
- Example run on a sample product idea (e.g., "AI-powered personal finance tracker")
- documentation update (specific requirements see above)

Think step by step, justify every change with references to modern best practices (Y Combinator, Reforge, Lenny' Newsletter, 2026 LLM-dev trends).