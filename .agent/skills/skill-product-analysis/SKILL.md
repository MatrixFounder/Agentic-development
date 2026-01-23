---
name: skill-product-analysis
description: Process for creating and refining Product Vision and Strategy.
tier: 2
version: 1.0
---

# Product Analysis & Vision

## 1. Objective
To define **what** we are building and **why**, before writing code.
This skill powers the **Product Analyst (p01)** role.

## 2. Core Tooling
You MUST use the provided Python script to scaffold the Vision document.
**DO NOT** write the `PRODUCT_VISION.md` header/structure manually.

### How to Initialise
Run the following command (Headless mode):
```bash
python3 System/scripts/init_product.py --name "Product Name" --problem "Problem description" --audience "Users" --metrics "KPI1, KPI2"
```

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

## 4. Verification Guidelines
- **Problem Statement:** Is it specific? (Bad: "Slow app". Good: "Page load > 5s causes 30% drop-off")
- **Metrics:** Are they SMART? (Specific, Measurable, Achievable, Relevant, Time-bound)

## 5. Examples
- **Good:** `examples/vision_example_good.md` (Clear, specific, focused)
- **Bad:** `examples/vision_example_bad.md` (Vague, buzzwords, solution-first)
