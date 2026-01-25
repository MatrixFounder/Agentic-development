---
name: skill-product-solution-blueprint
description: "Guidelines for creating Solution Blueprints (UX Flows, ROI, Risk Registers) for BRD preparation."
tier: 2
version: 1.0
---

# Solution Blueprinting

## 1. Objective
To translate abstract "Vision" into concrete "Requirements" without writing code. This skill powers the **Solution Architect (p04)** agent.

## 2. Text-Based UX Flows (The "Skeleton")
**Constraint:** Do NOT use Mermaid graphs for detailed logical flows. Use text lists.

### Template
> **[Use the Official Template](resources/solution_blueprint_template.md)** for the full structure.

### Syntax Example
```markdown
### Flow 1: [User Story Name]
- **Size:** M (60h) | **LLM Friendly:** 0.8
1. User [Action] on [Page/Component].
   - *System:* [Validates/Checks/Loads].
   - *Error Path:* If [Condition], show [Error Message].
2. User sees [Result].
```

## 3. Business Case (Enhanced ROI)

### Logic Locker (CRITICAL)
> [!IMPORTANT]
> **FORBIDDEN ACTION:** You are **strictly forbidden** from calculating ROI/NPV manually.
> You MUST first list all User Stories with sizes + friendliness, then run the script.

### Protocol
1. **Estimate**: For each user story, assign a Size (XS, S, M, L, XL) and LLM Friendliness (0.0 - 1.0).
2. **Prepare**: Create a temp JSON file in `docs/product/` (e.g., `docs/product/stories.json`):
   ```json
   {
     "stories": [
       { "name": "Login", "size": "S", "llm_friendly": 0.9 },
       { "name": "Complex Dashboard", "size": "L", "llm_friendly": 0.3 }
     ]
   }
   ```
3. **Execute**:
   ```bash
   # Usage: python3 [skill_path]/scripts/calculate_roi.py --file docs/product/stories.json --users <SOM> --price <PRICE>
   python3 [skill_path]/scripts/calculate_roi.py --file docs/product/stories.json --users 5000 --price 29.99
   ```

### Output Interpretation
- **NPV (Net Present Value):** Must be Positive.
- **Payback Period:** Ideal < 12 months.
- **ROI:** Ideal > 3.0x.
- **LTV/CAC:** Ideal > 3.0x.
- **Verdict:** Script provides "Strong Case", "Long Game", or "Risky". Trust it.

## 4. Risk Register
Track top 5 risks using this structure:

| Risk ID | Risk Description | Impact (1-5) | Likelihood (1-5) | Mitigation Strategy |
|---------|------------------|--------------|------------------|---------------------|
| R01     | API Limit Hit    | 5            | 3                | Use Rotating Proxies|

## 5. Handoff Readiness
The output must be ready for `handoff_to_technical.py`.
- **Constraint:** Ensure all NFRs (Non-Functional Requirements) are quantifiable (e.g. "Sub-200ms latency", not "Fast").

## 6. Examples
- **Simple (B2C):** `examples/01_simple_flexarb.md`
- **Advanced (B2B SaaS):** `examples/02_advanced_loyaltyhub.md`
