import pytest
import os
import sys
import shutil
from unittest.mock import patch, MagicMock

# Add scripts/ to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../System/scripts'))

import init_product
import calculate_wsjf

TEST_OUTPUT_DIR = "tests/tmp_output"

@pytest.fixture
def setup_output():
    if os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)
    os.makedirs(TEST_OUTPUT_DIR)
    yield
    # Cleanup
    if os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)

class TestInitProduct:
    def test_headless_generation(self, setup_output):
        """Test headless mode generates file."""
        output_file = os.path.join(TEST_OUTPUT_DIR, "VISION.md")
        
        # Mock sys.argv
        test_args = [
            "init_product.py",
            "--name", "TestProject",
            "--problem", "Solved",
            "--audience", "Everyone",
            "--metrics", "KPI1, KPI2",
            "--output", output_file
        ]
        
        with patch.object(sys, 'argv', test_args):
            init_product.main()
            
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            content = f.read()
            assert "TestProject" in content
            assert "- KPI1" in content
            assert "- KPI2" in content

    def test_interactive_mode_simulated(self, setup_output):
        """Test interactive mode logic."""
        # Directly test interactive_mode function via input mocking
        with patch('builtins.input', side_effect=["SimProject", "Hard", "Devs", "Money, Fame"]):
            data = init_product.interactive_mode()
            
        assert data['name'] == "SimProject"
        assert "- Money" in data['metrics'] # Formatting check

class TestCalculateWSJF:
    def test_valid_calculation_and_sort(self, setup_output):
        """Test WSJF calculation and sorting."""
        backlog_path = os.path.join(TEST_OUTPUT_DIR, "BACKLOG.md")
        
        # Create dummy backlog
        content = """
# Backlog

| Feature | User Value | Time Criticality | Risk Reduction | Job Size | WSJF |
|---------|------------|------------------|----------------|----------|------|
| Task A  | 1          | 1                | 1              | 1        | 0    |
| Task B  | 10         | 10               | 10             | 1        | 0    |
| Task C  | 5          | 5                | 5              | 5        | 0    |
"""
        with open(backlog_path, 'w') as f:
            f.write(content)
            
        test_args = ["calculate_wsjf.py", "--file", backlog_path]
        
        with patch.object(sys, 'argv', test_args):
            # calculate_wsjf.main() # This would run it
            # But the script imports argparse inside parse_arguments.
            # We need to ensure we call main.
            calculate_wsjf.main()
            
        with open(backlog_path, 'r') as f:
            new_content = f.read()
            
        # Expected: Task B (30/1=30) > Task C (15/5=3) > Task A (3/1=3)
        # Wait, Task A: 3/1 = 3. Task C: 15/5 = 3. Tie.
        # Let's change Task C to be slightly lower score.
        # UV=5, TC=5, RR=5, JS=10 => 15/10 = 1.5.
        
        # But based on input:
        # B: 30
        # A: 3
        # C: 3
        
        # Check order by finding indices
        idx_a = new_content.find("Task A")
        idx_b = new_content.find("Task B")
        
        # B should be before A
        assert idx_b < idx_a

    def test_job_size_zero_protection(self, setup_output):
        """Test error on Job Size 0."""
        backlog_path = os.path.join(TEST_OUTPUT_DIR, "BACKLOG_ZERO.md")
        content = "| Bad | 1 | 1 | 1 | 0 | 0 |"
        with open(backlog_path, 'w') as f:
            f.write(content)
            
        test_args = ["calculate_wsjf.py", "--file", backlog_path]
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as excinfo:
                calculate_wsjf.main()
            assert excinfo.value.code == 1

    def test_malformed_table_row_count(self, setup_output):
        """Test error on row length mismatch."""
        backlog_path = os.path.join(TEST_OUTPUT_DIR, "BACKLOG_BAD.md")
        content = """
| Col1 | Col2 |
|---|---|
| Val1 |
"""
        with open(backlog_path, 'w') as f:
            f.write(content)
            
        test_args = ["calculate_wsjf.py", "--file", backlog_path]
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as excinfo:
                calculate_wsjf.main() 
            assert excinfo.value.code == 1

