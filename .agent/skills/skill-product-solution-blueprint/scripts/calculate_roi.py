#!/usr/bin/env python3
import sys
import argparse
import json
import math
from pathlib import Path

def load_config(skill_path):
    """Loads sizing config from json."""
    # Robust path resolution
    config_path = (Path(skill_path) / "config" / "sizing_config.json").resolve()
    if not config_path.exists():
        # Fallback defaults if config missing
        return {
            "sizing": {"XS": 8, "S": 20, "M": 60, "L": 160, "XL": 400, "XXL": 800},
            "financials": {"hourly_rate": 100, "llm_global_accel": 0.5, "infra_cost_monthly": 200, "cac": 50, "churn_rate": 0.05, "growth_rate": 0.1, "discount_rate": 0.2},
            "risk": {"buffer_base": 1.3}
        }
    with open(config_path, 'r') as f:
        return json.load(f)

def calculate_granular_effort(stories, config):
    """
    Calculates total hours from a list of user stories with LLM acceleration.
    Story format: {"name": "...", "size": "S", "llm_friendly": 0.8}
    """
    sizing = config.get('sizing', {})
    fin = config.get('financials', {})
    
    total_base_hours = 0
    total_effective_hours = 0
    breakdown = {}
    
    for story in stories:
        size = story.get('size', 'M')
        base_hours = sizing.get(size, 60)
        
        # Clamp friendliness 0.0 - 1.0 to prevent user error
        friendliness = max(0.0, min(1.0, float(story.get('llm_friendly', 0.0))))
        
        # Linear interpolation
        accel_factor = 1.0 - (friendliness * fin.get('llm_global_accel', 0.5))
        
        # Safety clamp: never less than 10% of base time (sanity check)
        accel_factor = max(0.1, accel_factor)
        
        effective_hours = base_hours * accel_factor
        
        total_base_hours += base_hours
        total_effective_hours += effective_hours
        
    return total_base_hours, total_effective_hours

def calculate_metrics(effective_hours, users, price, config, monthly_arpu=None, som=None):
    """Calculates NPV, ROI, Payback."""
    fin = config['financials']
    risk = config['risk']
    
    # Costs
    dev_cost = effective_hours * fin['hourly_rate']
    total_initial_investment = dev_cost * risk['buffer_base']
    
    # Revenue (Annualized snapshot logic vs Monthly projection)
    # We'll do a 3-year monthly projection for NPV
    
    arpu = monthly_arpu if monthly_arpu else price
    target_users = som if som else users
    
    # Projections
    months = 36
    monthly_cash_flows = []
    cumulative_cash_flow = -total_initial_investment
    payback_month = None
    
    current_users = 0
    # Simple logistic growth or linear ramp to SOM? Let's assume linear growth to SOM over 18 months then plateau
    growth_period = 18
    new_users_per_month = target_users / growth_period
    
    discount_rate_monthly = fin['discount_rate'] / 12
    npv = -total_initial_investment
    
    for m in range(1, months + 1):
        # User Growth
        if current_users < target_users:
            current_users += new_users_per_month
        
        # Churn
        churned = current_users * fin['churn_rate']
        current_users -= churned
        
        # Financials
        revenue = current_users * arpu
        infra = fin['infra_cost_monthly'] + (current_users * 0.05) # Scaling infra
        marketing = new_users_per_month * fin['cac'] if m <= growth_period else (churned * fin['cac']) # Replace churn
        
        profit = revenue - infra - marketing
        
        # NPV
        npv += profit / ((1 + discount_rate_monthly) ** m)
        
        # Payback
        cumulative_cash_flow += profit
        if payback_month is None and cumulative_cash_flow > 0:
            payback_month = m
            
    # LTV
    avg_lifetime_months = 1 / fin['churn_rate'] if fin['churn_rate'] > 0 else 24
    ltv = arpu * avg_lifetime_months
    
    return {
        "investment": total_initial_investment,
        "npv_3yr": npv,
        "payback_months": payback_month,
        "ltv": ltv,
        "roi_3yr": (cumulative_cash_flow + total_initial_investment) / total_initial_investment if total_initial_investment > 0 else 0
    }

def main():
    parser = argparse.ArgumentParser(description='Calculate Enhanced ROI')
    parser.add_argument('--file', help='Path to JSON/YAML containing user stories')
    parser.add_argument('--small', type=int, default=0, help='Legacy: Count of Small features')
    parser.add_argument('--medium', type=int, default=0, help='Legacy: Count of Medium features')
    parser.add_argument('--large', type=int, default=0, help='Legacy: Count of Large features')
    parser.add_argument('--users', type=int, required=True, help='SOM User count')
    parser.add_argument('--price', type=float, required=True, help='Monthly price per user')
    
    args = parser.parse_args()
    
    # Locate skill path (parent of script directory)
    skill_path = Path(__file__).parent.parent
    config = load_config(skill_path)
    
    stories = []
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
             print(f"Error: File {file_path} not found.")
             sys.exit(1)
        with open(file_path, 'r') as f:
            data = json.load(f)
            stories = data.get('stories', [])
            
    else:
        # Legacy Mode conversion
        for _ in range(args.small): stories.append({"size": "S", "llm_friendly": 0.5})
        for _ in range(args.medium): stories.append({"size": "M", "llm_friendly": 0.5})
        for _ in range(args.large): stories.append({"size": "L", "llm_friendly": 0.5})

    base_hours, effective_hours = calculate_granular_effort(stories, config)
    metrics = calculate_metrics(effective_hours, args.users, args.price, config, som=args.users)
    
    # Output
    print(f"## 📊 Business Case Analysis")
    print(f"### Effort & Cost")
    print(f"- **Feature Count:** {len(stories)}")
    print(f"- **Base Hours:** {base_hours}h")
    print(f"- **LLM-Accelerated Hours:** {effective_hours:.1f}h ({(1 - effective_hours/base_hours if base_hours else 0)*100:.1f}% savings)")
    print(f"- **Initial Investment:** ${metrics['investment']:,.2f} (incl. {int((config['risk']['buffer_base']-1)*100)}% buffer)")
    
    print(f"\n### Unit Economics")
    cac = config['financials']['cac']
    arpu = args.price # Simplified for display
    ltv_cac = metrics['ltv'] / cac if cac > 0 else 0
    
    print(f"- **ARPU:** ${arpu:.2f}")
    print(f"- **CAC:** ${cac:.2f}")
    print(f"- **LTV:** ${metrics['ltv']:.2f}")
    print(f"- **LTV/CAC:** {ltv_cac:.1f}x")
    
    print(f"\n### Returns (3-Year Projection)")
    print(f"- **ROI:** {metrics['roi_3yr']:.2f}x")
    print(f"- **NPV:** ${metrics['npv_3yr']:,.2f}")
    pb_text = f"{metrics['payback_months']} months" if metrics['payback_months'] else "> 36 months"
    print(f"- **Payback Period:** {pb_text}")
    
    # Verdict
    if metrics['roi_3yr'] < 2.0: # Higher bar for startups
        print(f"\n> [!WARNING]")
        print(f"> **Risky Investment:** ROI < 2.0x in 3 years. Payback: {pb_text}.")
        print(f"> *Mitigation:* Reduce scope or increase pricing.")
    elif metrics['payback_months'] and metrics['payback_months'] > 12:
         print(f"\n> [!NOTE]")
         print(f"> **Long Game:** Good ROI, but slow payback ({pb_text}). Ensure runway exists.")
    else:
        print(f"\n> [!TIP]")
        print(f"> **Strong Case:** Positive outcomes. ROI: {metrics['roi_3yr']:.2f}x.")

if __name__ == "__main__":
    main()
