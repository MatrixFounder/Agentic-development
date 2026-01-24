---
name: skill-product-strategic-analysis
description: "Guidelines for conducting Market Research (TAM/SAM/SOM) and Competitive Analysis."
tier: 2
version: 1.0
---

# Strategic Analysis

## 1. Objective
To provide data-backed justification for *why* a product should exist. This skill powers the **Strategic Analyst (p01)** agent.

## 2. Market Sizing (The Numbers)

You MUST use the **TAM/SAM/SOM** model.

### Definitions
1.  **TAM (Total Addressable Market):** 
    *   *Formula:* Total Potential Customers x Average Annual Revenue per Customer.
    *   *Scope:* Global, Theoretical maximum.
2.  **SAM (Serviceable Available Market):**
    *   *Formula:* Segment % of TAM that fits your geographical/technological reach.
    *   *Scope:* Realistic reach within 3-5 years.
3.  **SOM (Serviceable Obtainable Market):**
    *   *Formula:* SAM x Target Market Share (usually 1-5% for startups).
    *   *Scope:* Year 1 target.

### Citation Rule
> [!IMPORTANT]
> **No Hallucinations.** If real data is unavailable, you MUST explicitly state: 
> *"Based on Conservative Estimate 2026 guidelines"* and explain your logic (e.g., "Assumed 10% of developers use VS Code...").

## 3. Competitive Matrix

Use the following Markdown table structure to identify the "Blue Ocean":

```markdown
| Competitor | Key Feature | Pricing Model | Weakness (The Gap) |
|------------|-------------|---------------|--------------------|
| Comp A     | ...         | ...           | ...                |
| Comp B     | ...         | ...           | ...                |
| **US**     | **...**     | **...**       | **N/A**            |
```

## 4. Verification Check
- [ ] Is TAM > $1B? (If not, is it a niche lifestyle business?)
- [ ] Is SAM < TAM? (If SAM > TAM, your math is broken).
- [ ] Is SOM < SAM? (If SOM = SAM, you are overly optimistic).
- [ ] Is the "Gap" defensible? (Technology vs Marketing)
- [ ] Are all numbers cited or estimated with disclaimers?
