# Product Development Guide

## Overview
This document outlines the **Product Bootstrap** process, enabling the rapid creation and prioritization of product artifacts (`PRODUCT_VISION.md`, `PRODUCT_BACKLOG.md`) using strict TIER 2 tooling.

## 1. Architecture
The system uses a **Script-First** approach to prevent Agent hallucinations.

- **Identity**: Agents (`p01`, `p02`) provide the persona and semantic reasoning.
- **Logic**: Python scripts (`scripts/`) provide the mathematical and formatting logic.
- **Skills**: TIER 2 skills bridge the gap, instructing agents on which script to call.

## 2. Tools & Scripts

### A. `System/scripts/init_product.py`
Scaffolds the `PRODUCT_VISION.md` file.
- **Interactive Mode**: Run without arguments to answer questions manually.
- **Headless Mode**: Use flags (`--name`, etc.) for Agents to generate file atomically.

### B. `System/scripts/calculate_wsjf.py`
Calculates and sorts the `PRODUCT_BACKLOG.md` using Weighted Shortest Job First.
- **Input**: Markdown table with `User Value`, `Time Criticality`, `Risk Reduction`, `Job Size`.
- **Logic**: `WSJF = (UV + TC + RR) / Job Size`.
- **Safety**: Exits with error if Job Size is 0 to prevent div-by-zero.

## 3. Workflow for Agents

### Phase 1: Bootstrap (p01)
1. Agent interviews user to gather Vision data.
2. Agent calls `init_product.py` to create file.
3. Agent helps user define initial Backlog items.
4. Agent calls `calculate_wsjf.py` to sort.

### Phase 2: Review (p02)
1. Reviewer reads artifacts.
2. Checks for "Fluff" in Vision using `skill-product-analysis`.
3. Verifies logic consistency in Backlog.

## 4. Troubleshooting
- **Job Size 0 Error**: Ensure all Backlog items have a Job Size >= 1.
- **Table Parsing Error**: Ensure the Markdown table has valid pipe structure. The script is robust but needs a header row.

## 5. Agent Interaction Examples

### Scenario A: Starting a New Product (p01)
**User:** "I want to build a Tinder for Cats."
**Analyst (p01):**
1.  **Thought:** I need to scaffold the vision. I check `skill-product-analysis`.
2.  **Action:** "That sounds interesting. To start, I need to define the Vision.
    - What is the specific problem for cat owners?
    - Who is the target audience (owners or cats)?
    - What are the success metrics?"
3.  **User:** "Problem: cats are lonely. Audience: Cat owners. Metric: 1000 matches per day."
4.  **Action (Tool Call):**
    ```python
    init_product(
        name="Tinder for Cats",
        problem="Cats are lonely and need social interaction.",
        audience="Cat Owners looking for playdates",
        metrics="1000 matches/day, 30% retention"
    )
    ```

### Scenario B: Prioritizing Features (p01)
**User:** "Add 'Swipe Left' and 'Super Like' to backlog. Swipe Left is critical."
**Analyst (p01):**
1.  **Action:** "I've added them. Let's score them for WSJF.
    - For 'Swipe Left': Value is High (10), Time Criticality is High (10)?
    - For 'Super Like': Maybe Value (5)?"
2.  **Action (Update File):** Writes to `docs/PRODUCT_BACKLOG.md`:
    ```markdown
    | Feature | User Value | Time Criticality | Risk Reduction | Job Size | WSJF |
    |---|---|---|---|---|---|
    | Swipe Left | 10 | 10 | 1 | 2 | 0 |
    | Super Like | 5 | 5 | 1 | 5 | 0 |
    ```
3.  **Action (Tool Call):**
    ```python
    calculate_wsjf(file="docs/PRODUCT_BACKLOG.md")
    ```
4.  **Result:** The file is automatically sorted. 'Swipe Left' (Score 10.5) moves to top.

### Scenario C: VDD Audit (p02)
**User:** "Please review the vision."
**Reviewer (p02):**
1.  **Thought:** I need to check for fluff and valid metrics.
2.  **Observation:** `PRODUCT_VISION.md` says "World-class synergy for felines."
3.  **Action:**
    > [!CRITIC]
    > **REJECTION:** "World-class synergy" is fluff. Replace with concrete value proposition.
    > The metric "Make cats happy" is not measurable. Use "Time spent purring" or "Revisit rate".

