#!/usr/bin/env python3
import sys
import argparse

def calculate_roi(dev_hours_s, dev_hours_m, dev_hours_l, som_users, price, retention_months=12, hourly_rate=100):
    """
    Calculates ROI based on T-Shirt sized inputs.
    """
    # 1. Calculate Cost
    # T-Shirt constants
    HOURS_S = 40
    HOURS_M = 120
    HOURS_L = 320
    MAINTENANCE_BUFFER = 1.20 # 20%
    
    total_hours = (dev_hours_s * HOURS_S) + (dev_hours_m * HOURS_M) + (dev_hours_l * HOURS_L)
    dev_cost = total_hours * hourly_rate
    total_cost = dev_cost * MAINTENANCE_BUFFER
    
    # 2. Calculate Revenue
    annual_revenue = som_users * price * retention_months
    
    # 3. Calculate ROI
    if total_cost == 0:
        roi = 0.0
    else:
        roi = (annual_revenue - total_cost) / total_cost
        
    # Output Markdown
    print(f"## Business Case Calculation")
    print(f"- **Inputs:** S={dev_hours_s}, M={dev_hours_m}, L={dev_hours_l}")
    print(f"- **Total Dev Hours:** {total_hours}h")
    print(f"- **Total Cost (w/ Buffer):** ${total_cost:,.2f}")
    print(f"- **Projected Revenue:** ${annual_revenue:,.2f}")
    print(f"- **ROI:** {roi:.2f}x")
    
    if roi < 1.0:
        print(f"\n> [!WARNING]\n> **High Risk:** Negative or low ROI (< 1.0). Justification required.")
    else:
        print(f"\n> [!TIP]\n> **Viable:** Positive ROI.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate ROI')
    parser.add_argument('--small', type=int, default=0, help='Number of Small features (40h)')
    parser.add_argument('--medium', type=int, default=0, help='Number of Medium features (120h)')
    parser.add_argument('--large', type=int, default=0, help='Number of Large features (320h)')
    parser.add_argument('--users', type=int, required=True, help='SOM User count')
    parser.add_argument('--price', type=float, required=True, help='Monthly price per user')
    
    args = parser.parse_args()
    
    calculate_roi(args.small, args.medium, args.large, args.users, args.price)
