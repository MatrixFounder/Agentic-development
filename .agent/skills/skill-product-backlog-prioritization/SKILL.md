---
name: skill-product-backlog-prioritization
description: Guidelines for managing and prioritizing the Product Backlog using WSJF.
tier: 2
version: 1.0
---

# Backlog Prioritization (WSJF)

## 1. Objective
To prioritize features scientifically using **Weighted Shortest Job First (WSJF)**.

## 2. Logic Locker (CRITICAL)
> [!IMPORTANT]
> **FORBIDDEN ACTION:** You are **strictly forbidden** from calculating WSJF scores manually or mentally.
> Humans and LLMs are bad at floating point arithmetic. Use the script.

## 3. Core Tooling
You MUST use the provided Python script to calculate scores and sort the backlog.

### How to Prioritize
Run the following command:
```bash
python3 [skill_path]/scripts/calculate_wsjf.py --file docs/PRODUCT_BACKLOG.md
```
> **Note:** `[skill_path]` is the path to this skill (e.g. `.agent/skills/skill-product-backlog-prioritization`).

## 4. Scoring Components
When adding a new item to the Backlog, you must estimate:
1.  **User Value (UV):** Relative value to the customer (1-10).
2.  **Time Criticality (TC):** Is there a deadline? (1-10).
3.  **Risk Reduction (RR):** Does this open new options or fix security? (1-10).
4.  **Job Size (JS):** Estimate of effort (1-10).

**Formula (Handled by Script):** `WSJF = (UV + TC + RR) / Job Size`

## 5. Artifact Standards
See `examples/backlog_table_example.md` for the correct table format.
The table MUST include all 4 input columns and the `WSJF` output column.
