
import subprocess
import time
import os
import sys

# Path to update_state.py
UPDATE_SCRIPT = ".agent/skills/skill-session-state/scripts/update_state.py"
SESSION_FILE = ".agent/sessions/latest.yaml"

def reset_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    if os.path.exists(SESSION_FILE + ".lock"):
        os.remove(SESSION_FILE + ".lock")
    
    # Initialize
    subprocess.run([
        "python3", UPDATE_SCRIPT,
        "--mode", "TEST",
        "--task", "Init",
        "--status", "Running",
        "--summary", "Init"
    ], check=True)

def run_concurrent_updates():
    print("Starting concurrent updates...")
    
    # Process A
    p1 = subprocess.Popen([
        "python3", UPDATE_SCRIPT,
        "--mode", "TEST",
        "--task", "Task A",
        "--status", "Done",
        "--summary", "Summary A",
        "--add_completed_task", "Task A"
    ])
    
    # Process B
    p2 = subprocess.Popen([
        "python3", UPDATE_SCRIPT,
        "--mode", "TEST",
        "--task", "Task B",
        "--status", "Done",
        "--summary", "Summary B",
        "--add_completed_task", "Task B"
    ])
    
    p1.wait()
    p2.wait()
    
    print("Concurrent updates finished.")

def verify():
    with open(SESSION_FILE, 'r') as f:
        content = f.read()
        
    print(f"Final Content:\n{content}")
    
    if "Task A" in content and "Task B" in content:
        print("SUCCESS: Both tasks recorded.")
    else:
        print("FAILURE: Lost data.")
        sys.exit(1)

if __name__ == "__main__":
    reset_session()
    run_concurrent_updates()
    verify()
