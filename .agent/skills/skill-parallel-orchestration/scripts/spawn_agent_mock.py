#!/usr/bin/env python3
import argparse
import time
import os
import subprocess
import json

# Configuration
UPDATE_STATE_SCRIPT = ".agent/skills/skill-session-state/scripts/update_state.py"

def update_session(mode, task, status, summary, completed_task=None):
    """Helper to call update_state.py safely."""
    cmd = [
        "python3", UPDATE_STATE_SCRIPT,
        "--mode", mode,
        "--task", task,
        "--status", status,
        "--summary", summary
    ]
    if completed_task:
        cmd.extend(["--add_completed_task", completed_task])
        
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error updating session state: {e}")

def main():
    parser = argparse.ArgumentParser(description="Mock Agent Runner")
    parser.add_argument("--task_name", required=True, help="Task Identifier")
    parser.add_argument("--goal", required=True, help="Goal Description")
    parser.add_argument("--context_file", help="Path to context file")
    parser.add_argument("--output_dir", required=True, help="Output Directory")
    
    args = parser.parse_args()
    
    # 1. Announce Start
    print(f"[{args.task_name}] Starting... Goal: {args.goal}")
    update_session(
        mode="EXECUTION",
        task=f"Sub-Agent: {args.task_name}",
        status="Running",
        summary=f"Started sub-task {args.task_name}"
    )
    
    # 2. Simulate Work
    time.sleep(5) # Simulate LLM thinking
    
    # 3. Generate Output
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        
    result_path = os.path.join(args.output_dir, f"{args.task_name}.result.md")
    
    with open(result_path, "w") as f:
        f.write(f"# Result for {args.task_name}\n")
        f.write(f"**Goal**: {args.goal}\n\n")
        f.write("## Execution Log\n")
        f.write("- Analysis: Completed\n")
        f.write("- Implementation: Mocked success.\n")
        f.write(f"- Timestamp: {time.ctime()}\n")
        
    print(f"[{args.task_name}] Finished. Result saved to {result_path}")
    
    # 4. Announce Completion
    update_session(
        mode="EXECUTION",  # Keep control in EXECUTION mode after sub-agent completes
        task=f"Sub-Agent: {args.task_name}",
        status="Completed",
        summary=f"Finished sub-task {args.task_name}",
        completed_task=args.task_name
    )

if __name__ == "__main__":
    main()
