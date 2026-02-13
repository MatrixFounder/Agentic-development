
import subprocess
import time
import os
import sys

# Paths
SPAWN_SCRIPT = ".agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py"
OUTPUT_DIR = "docs/tasks/mock_results"

def cleanup():
    if os.path.exists(OUTPUT_DIR):
        import shutil
        shutil.rmtree(OUTPUT_DIR)

def test_spawn():
    print("Spawning Mock Agent...")
    
    cmd = [
        "python3", SPAWN_SCRIPT,
        "--task_name", "test-task-123",
        "--goal", "Verify infrastructure",
        "--output_dir", OUTPUT_DIR
    ]
    
    start_time = time.time()
    subprocess.run(cmd, check=True)
    duration = time.time() - start_time
    
    print(f"Agent finished in {duration:.2f}s")
    
    # Verify Result File
    result_file = os.path.join(OUTPUT_DIR, "test-task-123.result.md")
    if os.path.exists(result_file):
        print(f"SUCCESS: Result file created at {result_file}")
    else:
        print(f"FAILURE: Result file missing.")
        sys.exit(1)
        
    # Verify Content
    with open(result_file, 'r') as f:
        content = f.read()
        if "Execution Log" in content:
            print("SUCCESS: Content valid.")
        else:
            print("FAILURE: Content invalid.")
            sys.exit(1)

if __name__ == "__main__":
    cleanup()
    test_spawn()
