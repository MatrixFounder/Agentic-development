---
name: skill-product-analysis
description: Process for creating and refining Product Vision and Strategy.
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
### How to Initialise
Run the following command (Headless mode):
```bash
python3 [skill_path]/scripts/init_product.py --name "Product Name" --problem "Problem description" --audience "Users" --metrics "KPI1, KPI2"
```
> **Note:** `[skill_path]` is the path to this skill (e.g. `.agent/skills/skill-product-analysis`).

## 3. Artifact Standards (`PRODUCT_VISION.md`)

### Template Structure
See `resources/templates/vision_template.md` for the authoritative structure.
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
- **Problem Statement:** Is it specific? (Bad: "Slow app". Good: "Page load > 5s causes 30% drop-off")
- **Metrics:** Are they SMART? (Specific, Measurable, Achievable, Relevant, Time-bound)
- **Soul Check:** Does the Vision allow for emotional connection?

## 6. Examples
- **Good:** `examples/vision_example_good.md` (Clear, specific, focused)
- **Bad:** `examples/vision_example_bad.md` (Vague, buzzwords, solution-first)
