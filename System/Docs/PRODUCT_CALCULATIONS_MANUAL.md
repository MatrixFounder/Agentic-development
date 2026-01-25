# Product Calculations & Metrics Manual (FAQ)

> "Wait, how does this AI actually estimate my money?" — You, probably.

This guide explains the "Magic Math" behind our Product Discovery agents (`p01`-`p04`). We assume you are a Product Manager, Indie Hacker, or curious developer, not a CFO.

---

## 1. Financials & ROI (`calculate_roi.py`)

This script tells you if your idea will make money or burn it. It powers the **Solution Architect (`p04`)**.

### Q: How is "Effort" calculated?
We use **Granular T-Shirt Sizing** combined with **LLM Acceleration**.

1.  **Base Hours**: Every feature gets a size.
    - `XS` (Extra Small): ~8 hours (1 day)
    - `S` (Small): ~20 hours (3 days)
    - `M` (Medium): ~60 hours (1.5 weeks)
    - `L` (Large): ~160 hours (1 month)
    - `XL` (Extra Large): ~400 hours (2.5 months)
    *(You can change these defaults in `config/sizing_config.json`)*

2.  **LLM Acceleration**: Can AI write this for me?
    - We ask: *"How LLM-friendly is this?"* (Score 0.0 to 1.0).
    - **1.0 (Very Friendly):** Boilerplate, CRUD, Unit Tests.
    - **0.0 (Not Friendly):** Novel cryptography, hardware integration, messy legacy code.
    
    **The Formula:**
    ```python
    Effective_Hours = Base_Hours * (1.0 - (Friendliness_Score * Global_Acceleration_Factor))
    ```
    *Default Global Factor is 0.5 (50%)*. So a perfectly friendly task (1.0) gets a 50% discount. A task with 0.0 friendliness gets 0% discount.

### Q: What is NPV and why do I care?
**Net Present Value (NPV)** answers: *"Is $100 today worth more than $100 in 3 years?"* (Yes, because of inflation/opportunity cost).

- We project your profit for **3 Years (36 Months)**.
- We discount future money by **20% per year** (High discount for startups).
- **If NPV is Positive:** You are creating value.
- **If NPV is Negative:** You are losing value (even if you make a small profit later).

### Q: What is LTV and CAC?
- **CAC (Customer Acquisition Cost):** How much to "buy" a user? (Ads, Marketing). *Default: $50*.
- **LTV (Lifetime Value):** How much money does a user give you before they leave?
    ```python
    LTV = Monthly_Price * (1 / Churn_Rate)
    ```
    *Example: $20/mo with 5% churn = 20 * (1/0.05) = $400 LTV.*
    
    > **Rule of Thumb:** LTV should be > 3x CAC. (e.g., $150 LTV for $50 CAC).

---

## 2. Product Viability (`score_product.py`)

This script stops you from building things nobody wants. It powers the **Product Analyst (`p02`)**.

### Q: What is the 10-Factor Matrix?
We score 10 dimensions from 1-10.
- **10/10:** Perfect/Easy.
- **1/10:** Terrible/Impossible.

| Factor | Description | Weight |
|--------|-------------|--------|
| **Problem Intensity** | How much pain is the user in? (1=Meh, 10=Bleeding) | 2.0x (Critical) |
| **Market Size** | How many people have this pain? (1=Niche, 10=Everyone) | 1.5x |
| **Solution Fit** | Does your app actually fix it? | 1.5x |
| **Moat Durability** | Can Google copy you tomorrow? (1=Yes, 10=No) | 1.2x |
| **Timing** | Is the market ready? | 1.0x |
| **Competition Gap** | Is the market crowded? (1=Crowded, 10=Empty) | 0.8x |
| **Monetization** | Will they pay? (1=Freeloader, 10=Visa Card Ready) | 1.2x |
| **Technical Risk** | Can we build it? (1=Nuclear Fusion, 10=CRUD App) | 1.0x |
| **Founder Fit** | Do YOU care about this? | 1.0x |
| **Trend Alignment** | Is the wind at your back? (AI in 2026 vs Web3 in 2019) | 0.5x |

**Verdict Logic:**
- **> 80/100:** Strong Go.
- **60-80:** Consider (Needs fixing).
- **< 60:** No Go.

---

## 3. Prioritization (`calculate_wsjf.py`)

This script decides *what to build first*. It powers the **Product Analyst (`p02`)**.

### Q: What is WSJF?
**Weighted Shortest Job First**.
> Do the most valuable, quickest things first.

```math
WSJF = (User Value + Time Criticality + Risk Reduction) / Job Size
```

### Q: How do I estimate these numbers?
Use relative Fibonacci sequences (1, 2, 3, 5, 8, 13, 20).
- **User Value:** 20 (Critical) vs 1 (Nice to have).
- **Time Criticality:** 20 (Deadline tomorrow) vs 1 (Next year).
- **Risk Reduction:** 20 (Fixes massive security hole) vs 1 (None).
- **Job Size:** Use T-Shirt Mapping:
    - `XS`, `Small` -> 1 or 2
    - `Medium` -> 5
    - `Large` -> 13
    - `XL` -> 20

---

## 4. Customization (Hacking the System)

### Q: How do I change the developer rate?
Edit `sizing_config.json` in `.agent/skills/skill-product-solution-blueprint/config/`.

```json
{
  "financials": {
    "hourly_rate": 50,      <-- Change this (e.g. outsourced vs onshore)
    "llm_global_accel": 0.5 <-- Change this (0.8 = AI does 80% work)
  },
  "sizing": {
    "M": 40                 <-- Change "Medium" to 40 hours
  }
}
```

### Q: I don't use Cloud, I use Bare Metal.
Set `"infra_cost_monthly"` in `sizing_config.json` to your dedicated server cost.

### Q: Can I turn off "Sarcastic Mode"?
Currently, sarcasm is part of the `vdd-sarcastic` workflow. To disable it, use standard `/product-full-discovery` instead of explicitly invoking adversarial personas, or edit the prompts in `System/Agents/`.
