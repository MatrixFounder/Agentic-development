#!/usr/bin/env python3
import sys
import argparse
import json

def score_product(scores_dict):
    """
    Calculates overall product score and risk level from 10 factors.
    """
    factors = [
        "market_size", "problem_intensity", "solution_fit", "moat_durability",
        "timing", "competition_gap", "monetization_strength", "technical_risk",
        "founder_fit", "trend_alignment"
    ]
    
    # Weights (can be adjusted)
    weights = {
        "market_size": 1.5,
        "problem_intensity": 2.0, # Most critical
        "solution_fit": 1.5,
        "moat_durability": 1.2,
        "timing": 1.0,
        "competition_gap": 0.8,
        "monetization_strength": 1.2,
        "technical_risk": 1.0, # Inverted scoring (10 = Low Risk) in input? No, standard is 10=Good. 
                               # So 10 = Very Low Risk/Easy.
        "founder_fit": 1.0,
        "trend_alignment": 0.5
    }
    
    total_score = 0
    total_weight = sum(weights.values())
    
    print("## 🎯 Product Viability Scorecard\n")
    print("| Factor | Score (1-10) | Weighted Contribution |")
    print("|--------|--------------|-----------------------|")
    
    for f in factors:
        raw_input = scores_dict.get(f, 5)
        # Sarcastic Fix: Clamp inputs so users can't give 11/10
        raw_score = max(1, min(10, int(raw_input)))
        
        weight = weights[f]
        weighted_score = raw_score * weight
        total_score += weighted_score
        
        # ASCII Bar
        bar = "█" * int(raw_score) + "░" * (10 - int(raw_score))
        
        print(f"| **{f.replace('_', ' ').title()}** | {raw_score}/10 {bar} | {weighted_score:.1f} |")
        
    final_score = (total_score / (10 * total_weight)) * 100
    
    print(f"\n### 🏆 Final Score: {final_score:.1f}/100")
    
    # Verdict
    risk_level = "Unknown"
    if final_score >= 80:
        print("> [!TIP]")
        print("> **Verdict: STRONG GO.** High potential, low risk.")
        risk_level = "Low"
    elif final_score >= 60:
        print("> [!NOTE]")
        print("> **Verdict: CONSIDER.** Good potential, but has weaknesses. Requires mitigation.")
        risk_level = "Medium"
    else:
        print("> [!WARNING]")
        print("> **Verdict: NO GO.** Too many risks or low upsides. Pivot needed.")
        risk_level = "High"
        
    return final_score, risk_level

def main():
    parser = argparse.ArgumentParser(description='Score Product Viability')
    # Add args for all 10 factors
    factors = [
        "market_size", "problem_intensity", "solution_fit", "moat_durability",
        "timing", "competition_gap", "monetization_strength", "technical_risk",
        "founder_fit", "trend_alignment"
    ]
    
    for f in factors:
        parser.add_argument(f'--{f}', type=int, default=5, help=f'Score 1-10 for {f}')
        
    args = parser.parse_args()
    
    scores = {f: getattr(args, f) for f in factors}
    score_product(scores)

if __name__ == "__main__":
    main()
