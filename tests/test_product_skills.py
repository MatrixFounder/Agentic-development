import pytest
import sys
import json
import yaml
from pathlib import Path
from unittest.mock import MagicMock, patch

# -----------------
# Setup & Helpers
# -----------------
PROJECT_ROOT = Path(__file__).parent.parent
# Add skill paths to sys.path so we can import scripts as modules
# Note: Since scripts often don't have __init__.py and are CLI tools, we might need to import by path or subprocess.
# Ideally refactor scripts to be importable. They currently have if __name__ == "__main__".
# We will use importlib for dynamic loading or subprocess for blackbox testing. 
# Subprocess is cleaner for CLI tools, but Logic testing is better with import.
# Let's try import logic.

import importlib.util

def load_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# Load Modules
roi_script = load_module_from_path("calculate_roi", 
    PROJECT_ROOT / ".agent/skills/skill-product-solution-blueprint/scripts/calculate_roi.py")

score_script = load_module_from_path("score_product",
    PROJECT_ROOT / ".agent/skills/skill-product-analysis/scripts/score_product.py")

wsjf_script = load_module_from_path("calculate_wsjf",
    PROJECT_ROOT / ".agent/skills/skill-product-backlog-prioritization/scripts/calculate_wsjf.py")


# -----------------
# 1. calculate_roi.py Tests
# -----------------

def test_roi_effort_calculation():
    config = {
        "sizing": {"S": 10},
        "financials": {"llm_global_accel": 0.5}
    }
    stories = [
        {"size": "S", "llm_friendly": 1.0}, # Max accel -> 1.0 - (1.0*0.5) = 0.5 factor. 10 * 0.5 = 5 hours
        {"size": "S", "llm_friendly": 0.0}  # No accel -> 1.0 - (0.0) = 1.0 factor. 10 * 1.0 = 10 hours
    ]
    base, effective = roi_script.calculate_granular_effort(stories, config)
    assert base == 20
    assert effective == 15

def test_roi_time_travel_bug():
    """Adversarial check: Friendliness > 1.0 should not cause negative time."""
    config = {
        "sizing": {"S": 10},
        "financials": {"llm_global_accel": 0.5}
    }
    # Friendliness 3.0 -> 1.0 - (3.0 * 0.5) = -0.5 factor. 
    # Current script DOES NOT clamp. This test shows EXPECTED FAILURE or behavior to be fixed.
    stories = [{"size": "S", "llm_friendly": 3.0}] 
    base, effective = roi_script.calculate_granular_effort(stories, config)
    
    # We WANT this to be positive (clamped), but for now asserting current behavior to confirm bug
    # Or asserting logical requirement
    if effective < 0:
        pytest.fail(f"Time travel check: Effective hours {effective} is negative!")

# -----------------
# 2. score_product.py Tests
# -----------------

def test_score_product_logic():
    scores = {
        "problem_intensity": 10, # Weight 2.0 -> 20
        "market_size": 10        # Weight 1.5 -> 15
        # Rest default 5
    }
    # Just ensure it runs without error
    final_score, risk = score_script.score_product(scores)
    assert 0 <= final_score <= 110 # Theoretically can go above 100 if user inputs > 10?

# -----------------
# 3. calculate_wsjf.py Tests
# -----------------

def test_wsjf_mapping():
    assert wsjf_script.map_size_to_fib("XS") == 1
    assert wsjf_script.map_size_to_fib("XXL") == 40
    assert wsjf_script.map_size_to_fib("M (60h)") == 5 # Regex check
    assert wsjf_script.map_size_to_fib("500") == 20 # Numeric Fallback > 200

def test_wsjf_mapping_unknown():
    # Should default to high penalty
    assert wsjf_script.map_size_to_fib("Unknown") == 20

def test_wsjf_line_parsing():
    line = "| Task 1 | 5 | 5 | 5 | M | |"
    cells = wsjf_script.parse_line(line)
    # expected: Task 1, 5, 5, 5, M, empty
    assert cells[0] == "Task 1"
    assert cells[4] == "M"

def test_wsjf_calculation_logic():
    rows = [(0, "| A | 3 | 3 | 2 | S | |", ["A", "3", "3", "2", "S", ""])]
    indices = {"User Value": 1, "Time Criticality": 2, "Risk Reduction": 3, "Job Size": 4, "WSJF": 5}
    
    # S maps to 2
    # WSJF = (3+3+2)/2 = 8/2 = 4.0
    processed = wsjf_script.calculate_wsjf(rows, indices)
    assert processed[0]['score'] == 4.0
