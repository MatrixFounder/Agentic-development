---
name: skill-product-analysis
description: "Guidelines for creating and refining Product Vision and Strategy."
tier: 2
version: 1.1
---

# Product Analysis & Vision

## 1. Objective
To define **what** we are building and **why**, before writing code.
This skill powers the **Product Analyst (p02)** role.

## 2. Core Tooling
You MUST use the provided Python script to scaffold the Vision document.
**DO NOT** write the `PRODUCT_VISION.md` header/structure manually.

### How to Initialise
Run the following command (Headless mode):
```bash
python3 [skill_path]/scripts/init_product.py --name "Product Name" --problem "Problem description" --audience "Users" --metrics "KPI1, KPI2"
```
> **Note:** `[skill_path]` is the path to this skill (e.g. `.agent/skills/skill-product-analysis`).

## 3. The 10-Factor Scoring Matrix
Before drafting the Vision, you MUST score the idea to determine viability.

### Protocol
Run the scoring script with your estimated values (1-10, where 10 is Best/Easiest):
```bash
# Example: High problem intensity (9), but weak moat (3)
python3 [skill_path]/scripts/score_product.py --problem_intensity 9 --moat_durability 3 --market_size 8
```
- **Goal:** Score > 70/100.
- **Output:** Application of this script must be included in `PRODUCT_VISION.md`.

## 4. Artifact Standards (`PRODUCT_VISION.md`)

### Template Structure
See `assets/vision_template.md` for the authoritative structure.
All sections are mandatory.

### INVEST Criteria (User Stories)
When breaking down the vision into the Backlog:
- **I**ndependent
- **N**egotiable
- **V**aluable (to the user)
- **E**stimable
- **S**mall
- **T**estable

## 4. Frameworks (The "Soul")

### Crossing the Chasm (Differentiation)
When defining the product features, you MUST position it for the **Early Majority**.
*   **The Beachhead:** What is the single specific niche we can dominate?
*   **The Whole Product:** What eco-system/integrations are needed to make it a complete solution?

### Emotional Logic (User Centricity)
Every feature implementation plan must start with:
1.  **Trigger:** What emotional state is the user in? (e.g. Anxiety about API keys)
2.  **Action:** The feature they use.
3.  **Reward:** The emotional relief/gain. (e.g. "Safety", "Control")

## 5. Verification Guidelines
- **Problem Statement:** Is it specific?
- **Metrics:** Are they SMART?
- **Soul Check:** Does the Vision allow for emotional connection?

## 6. Output
> **[Use the Official Template](assets/vision_template.md)** for the full structure.

## 7. Examples
- **Strong Go:** `examples/01_strong_go_devboost.md`
- **Consider:** `examples/02_consider_talentflow.md`
- **No-Go:** `examples/03_nogo_quickbites.md`
