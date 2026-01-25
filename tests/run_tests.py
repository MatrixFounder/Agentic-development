import unittest
import sys
import json
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

# --- Dynamic Import Helper ---
import importlib.util

def load_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

PROJECT_ROOT = Path(__file__).parent.resolve()

# Load Scripts
roi_script = load_module_from_path("calculate_roi", 
    PROJECT_ROOT / ".agent/skills/skill-product-solution-blueprint/scripts/calculate_roi.py")

score_script = load_module_from_path("score_product",
    PROJECT_ROOT / ".agent/skills/skill-product-analysis/scripts/score_product.py")

wsjf_script = load_module_from_path("calculate_wsjf",
    PROJECT_ROOT / ".agent/skills/skill-product-backlog-prioritization/scripts/calculate_wsjf.py")

class TestProductSkills(unittest.TestCase):

    # --- ROI Tests ---
    def test_roi_effort_calculation(self):
        config = {
            "sizing": {"S": 10},
            "financials": {"llm_global_accel": 0.5}
        }
        # Friendliness 1.0 -> Factor 0.5 -> 5 hours
        stories = [{"size": "S", "llm_friendly": 1.0}]
        base, effective = roi_script.calculate_granular_effort(stories, config)
        self.assertEqual(base, 10)
        self.assertEqual(effective, 5.0)

    def test_roi_time_travel_clamping(self):
        """Ensure time travel bug is fixed."""
        config = {
            "sizing": {"S": 10},
            "financials": {"llm_global_accel": 0.5}
        }
        # Friendliness 3.0 -> Should clamp to 1.0 -> Factor 0.5 -> 5 hours
        stories = [{"size": "S", "llm_friendly": 3.0}] 
        base, effective = roi_script.calculate_granular_effort(stories, config)
        self.assertGreater(effective, 0)
        self.assertEqual(effective, 5.0) 

    # --- Score Tests ---
    def test_score_product_clamping(self):
        scores = {
            "problem_intensity": 100, # Should clamp to 10
            "market_size": 0          # Should clamp to 1
        }
        # Capture stdout to avoid clutter
        with patch('sys.stdout', new=MagicMock()):
             final_score, risk = score_script.score_product(scores)
        
        # Total weight = 12.0 (sum of weights)
        # Score calculation: 
        # problem: 10 * 2.0 = 20
        # market: 1 * 1.5 = 1.5
        # others: 5 * weight...
        
        # Just ensure range is valid
        self.assertTrue(0 <= final_score <= 100)

    # --- WSJF Tests ---
    def test_wsjf_mapping(self):
        self.assertEqual(wsjf_script.map_size_to_fib("XS"), 1)
        self.assertEqual(wsjf_script.map_size_to_fib("medium"), 5) # Case insensitive check
        self.assertEqual(wsjf_script.map_size_to_fib("Small"), 2)

    def test_wsjf_logic(self):
        # Expected input: list of (line_content, cells)
        rows = [("| A | 3 | 3 | 2 | S | |", ["A", "3", "3", "2", "S", ""])]
        indices = {"User Value": 1, "Time Criticality": 2, "Risk Reduction": 3, "Job Size": 4, "WSJF": 5}
        processed = wsjf_script.calculate_wsjf(rows, indices)
        self.assertEqual(processed[0]['score'], 4.0)

if __name__ == '__main__':
    unittest.main()
