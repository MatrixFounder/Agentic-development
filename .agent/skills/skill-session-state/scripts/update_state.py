#!/usr/bin/env python3
import sys
import os
import uuid
import datetime
import argparse
import re
import fcntl

# Constants
SESSION_DIR = ".agent/sessions"
SESSION_FILE = "latest.yaml"

def get_session_path():
    """Get absolute path to session file."""
    # Assumes script is run from project root or we find root
    # We will just use the relative path from CWD as per standard agent execution
    return os.path.join(SESSION_DIR, SESSION_FILE)

def ensure_session_dir():
    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR)

# --- Minimal YAML Parser (Read-Only specific to our schema) ---
# We ONLY need to preserve: session_id, active_blockers, recent_decisions.
# Everything else (task, mode, summary) is overwritten by the Agent's update.

def parse_simple_yaml(content):
    """
    Robustly extract specific fields from our generated YAML.
    Does NOT aim to be a full YAML parser.
    """
    data = {
        "session_id": None,
        "active_blockers": [],
        "recent_decisions": [],
        "completed_tasks": []
    }
    
    # Extract session_id
    sid_match = re.search(r'^session_id:\s*[\'"]?([^\'"\n]+)[\'"]?', content, re.MULTILINE)
    if sid_match:
        data["session_id"] = sid_match.group(1).strip()
        
    # Extract active_blockers (List of strings)
    # Assumes format:
    # active_blockers:
    #   - "Blocker 1"
    #   - "Blocker 2"
    blockers_section = re.search(r'^active_blockers:\s*\n((?:\s+-\s+.*(?:\n|$))*)', content, re.MULTILINE)
    if blockers_section:
        items = re.findall(r'^\s+-\s+[\'"]?(.*?)[\'"]?\s*$', blockers_section.group(1), re.MULTILINE)
        data["active_blockers"] = [item.strip() for item in items]

    # Extract recent_decisions
    decisions_section = re.search(r'^recent_decisions:\s*\n((?:\s+-\s+.*(?:\n|$))*)', content, re.MULTILINE)
    if decisions_section:
        items = re.findall(r'^\s+-\s+[\'"]?(.*?)[\'"]?\s*$', decisions_section.group(1), re.MULTILINE)
        data["recent_decisions"] = [item.strip() for item in items]

    # Extract completed_tasks
    completed_section = re.search(r'^completed_tasks:\s*\n((?:\s+-\s+.*(?:\n|$))*)', content, re.MULTILINE)
    if completed_section:
        items = re.findall(r'^\s+-\s+[\'"]?(.*?)[\'"]?\s*$', completed_section.group(1), re.MULTILINE)
        data["completed_tasks"] = [item.strip() for item in items]
        
    return data

def generate_yaml(data):
    """
    Generate clean, valid YAML string.
    """
    iso_time = datetime.datetime.now().isoformat()
    
    # Handle multiline summary
    summary = data.get('context_summary', '').strip()
    formatted_summary = ""
    if '\n' in summary or len(summary) > 80:
        formatted_summary = "|\n" + "\n".join([f"  {line}" for line in summary.splitlines()])
    else:
        formatted_summary = f'"{summary}"'

    yaml = f"""session_id: "{data.get('session_id')}"
last_updated: "{iso_time}"
mode: "{data.get('mode', 'UNKNOWN')}"

current_task:
  name: "{data.get('task_name', 'Unknown Task')}"
  status: "{data.get('task_status', 'Initializing')}"
  predicted_steps: {data.get('predicted_steps', 0)}

context_summary: {formatted_summary}

active_blockers:
"""
    # Add lists
    for blocker in data.get('active_blockers', []):
        yaml += f'  - "{blocker}"\n'
    
    if not data.get('active_blockers'):
        yaml += "  []\n"
        
    yaml += "\nrecent_decisions:\n"
    for decision in data.get('recent_decisions', []):
        yaml += f'  - "{decision}"\n'
        
    if not data.get('recent_decisions'):
        yaml += "  []\n"
        
    yaml += "\ncompleted_tasks:\n"
    for task in data.get('completed_tasks', []):
        yaml += f'  - "{task}"\n'
        
    if not data.get('completed_tasks'):
        yaml += "  []\n"
        
    return yaml

def main():
    parser = argparse.ArgumentParser(description="Update Session State YAML")
    parser.add_argument("--mode", required=True, help="Current Agent Mode")
    parser.add_argument("--task", required=True, help="Current Task Name")
    parser.add_argument("--status", required=True, help="Current Task Status")
    parser.add_argument("--summary", required=True, help="Task Summary")
    parser.add_argument("--predicted_steps", type=int, default=0, help="Predicted remaining steps")
    parser.add_argument("--add_decision", help="Add a decision to recent_decisions")
    parser.add_argument("--add_blocker", help="Add a blocker item")
    parser.add_argument("--clear_blockers", action="store_true", help="Clear all blockers")
    parser.add_argument("--add_completed_task", help="Add a completed task to history")
    
    args = parser.parse_args()
    
    ensure_session_dir()
    fpath = get_session_path()
    
    # 1. Read existing state to preserve ID and lists
    existing_data = {}
    if os.path.exists(fpath):
        try:
            with open(fpath, 'r') as f:
                content = f.read()
                existing_data = parse_simple_yaml(content)
        except Exception as e:
            print(f"Warning: Could not read existing session file: {e}")
            existing_data = {}
            
    # 2. Merge Data
    session_id = existing_data.get("session_id") or str(uuid.uuid4())
    active_blockers = existing_data.get("active_blockers", [])
    recent_decisions = existing_data.get("recent_decisions", [])
    
    if args.clear_blockers:
        active_blockers = []
    
    if args.add_blocker:
        if args.add_blocker not in active_blockers:
            active_blockers.append(args.add_blocker)
            
            
    if args.add_decision:
        # Keep only last 10 decisions
        recent_decisions.append(args.add_decision)
        if len(recent_decisions) > 10:
            recent_decisions = recent_decisions[-10:]

    completed_tasks = existing_data.get("completed_tasks", [])
    if args.add_completed_task:
        if args.add_completed_task not in completed_tasks:
            completed_tasks.append(args.add_completed_task)
            
    
    # 3. Construct New State
    # Note: We construct it BEFORE locking to minimize lock time, 
    # but we must re-read inside the lock to get the TRUE latest state.
    
    # --- CRITICAL SECTION START ---
    # We use a separate lock file to avoid truncation issues with open(..., 'w')
    lock_path = fpath + ".lock"
    
    try:
        with open(lock_path, 'w') as lockfile:
            # Acquire Exclusive Lock
            fcntl.flock(lockfile, fcntl.LOCK_EX)
            
            try:
                # RE-READ existing state inside the lock to ensure we have the absolute latest
                # (Another agent might have updated it while we were parsing args)
                if os.path.exists(fpath):
                    with open(fpath, 'r') as f:
                        current_content = f.read()
                        latest_data = parse_simple_yaml(current_content)
                else:
                    latest_data = {}

                # Merge Logic (Re-apply on top of latest_data)
                # We prioritize the LATEST data for lists, but the ARGS for current status
                
                # Session ID: Persist if exists
                final_session_id = latest_data.get("session_id") or session_id
                
                # Active Blockers: Merge (Union)
                final_blockers = latest_data.get("active_blockers", [])
                if args.clear_blockers:
                    final_blockers = []
                elif args.add_blocker and args.add_blocker not in final_blockers:
                    final_blockers.append(args.add_blocker)
                    
                # Recent Decisions: Append
                final_decisions = latest_data.get("recent_decisions", [])
                if args.add_decision:
                    final_decisions.append(args.add_decision)
                    if len(final_decisions) > 10:
                        final_decisions = final_decisions[-10:]

                # Completed Tasks: Append
                final_completed = latest_data.get("completed_tasks", [])
                if args.add_completed_task and args.add_completed_task not in final_completed:
                    final_completed.append(args.add_completed_task)

                # Construct Final State Object
                final_state = {
                    "session_id": final_session_id,
                    "mode": args.mode,
                    "task_name": args.task,
                    "task_status": args.status,
                    "predicted_steps": args.predicted_steps,
                    "context_summary": args.summary,
                    "active_blockers": final_blockers,
                    "recent_decisions": final_decisions,
                    "completed_tasks": final_completed
                }
                
                # Generate YAML
                yaml_content = generate_yaml(final_state)
                
                # Write to actual file
                with open(fpath, 'w') as f:
                    f.write(yaml_content)
                    
                print(f"Session state updated: {fpath} (Locked)")
                
            finally:
                # Release Lock
                fcntl.flock(lockfile, fcntl.LOCK_UN)
                
    except Exception as e:
        print(f"Error updating session state: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
