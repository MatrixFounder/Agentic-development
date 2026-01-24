---
name: skill-product-solution-blueprint
description: "Guidelines for creating Solution Blueprints (UX Flows, ROI, Risk Registers) for BRD preparation."
tier: 2
version: 1.0
---

# Solution Blueprinting

## 1. Objective
To translate abstract "Vision" into concrete "Requirements" without writing code. This skill powers the **Solution Architect (p04)** agent.

## 2. Text-Based UX Flows
**Constraint:** Do NOT use Mermaid graphs for flows detailed enough to need steps. Use text lists.

### Syntax
```markdown
1. User [Action] on [Page/Component].
   - *System:* [Validates/Checks/Loads].
   - *Error Path:* If [Condition], show [Error Message].
2. User sees [Result].
```

## 3. Business Case (ROI) Calculation

### Logic Locker (CRITICAL)
> [!IMPORTANT]
> **FORBIDDEN ACTION:** You are **strictly forbidden** from calculating ROI manually.
> Use the provided script to ensure consistent "T-Shirt Sizing" standards.

### How to Calculate
Run the script with your estimated feature counts:
### How to Calculate
Run the script with your estimated feature counts:
```bash
# Usage: python3 [skill_path]/scripts/calculate_roi.py --small <N> --medium <N> --large <N> --users <N> --price <N>
python3 [skill_path]/scripts/calculate_roi.py --small 2 --medium 1 --users 1000 --price 10
```
> **Note:** `[skill_path]` is the path to this skill (e.g. `.agent/skills/skill-product-solution-blueprint`).

### Protocol
- Copy the script output directly into `SOLUTION_BLUEPRINT.md`.
- If ROI < 1.0 (Negative), flag as **High Risk**.

## 4. Risk Register
Track top 5 risks using this structure:

| Risk ID | Risk Description | Impact (1-5) | Likelihood (1-5) | Mitigation Strategy |
|---------|------------------|--------------|------------------|---------------------|
| R01     | API Limit Hit    | 5            | 3                | Use Rotating Proxies|

## 5. Handoff Readiness
The output must be ready for `handoff_to_technical.py`.
- **Constraint:** Ensure all NFRs (Non-Functional Requirements) are quantifiable (e.g. "Sub-200ms latency", not "Fast").
