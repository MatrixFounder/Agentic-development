#!/usr/bin/env python3
import sys
import argparse
import re
import os

def parse_markdown_table(content):
    """
    Parses a markdown table into a list of dictionaries.
    Assumes the first row is the header, and the second row is the separator.
    """
    lines = content.split('\n')
    table_data = []
    headers = []
    
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('|'):
            if in_table:
                break # End of table
            continue
            
        # It's a table row
        # Remove leading/trailing pipes and split using regex to handle escaped pipes \|
        # split by pipe that is NOT preceded by backslash
        cells = re.split(r'(?<!\\)\|', stripped.strip('|'))
        cells = [c.strip() for c in cells]
        
        if not in_table:
            # First row = Headers
            headers = cells
            in_table = True
        elif '---' in cells[0]:
            # Separator row
            continue
        else:
            # Data row
            if len(cells) != len(headers):
                # Handle mismatched columns if necessary, or skip
                continue
            
            row_dict = dict(zip(headers, cells))
            table_data.append(row_dict)
            
    return table_data

def validate_task(task_path):
    """
    Validates TASK.md for Requirements Traceability Matrix.
    """
    if not os.path.exists(task_path):
        print(f"Error: File '{task_path}' not found.")
        sys.exit(1)
        
    with open(task_path, 'r') as f:
        content = f.read()
        
    # check for bypass
    if "[BYPASS_VALIDATION]" in content:
         print("Validation bypassed via [BYPASS_VALIDATION] flag.")
         sys.exit(0)

    # 1. Check for RTM Header
    if "## Requirements Traceability" not in content:
        print("Error: '## Requirements Traceability' section missing in TASK.md.")
        print("Please add the RTM table.")
        sys.exit(1)
        
    # 2. Extract Table
    # A simple regex to find the table block might be needed if parse_markdown_table isn't robust enough for full file
    # But usually the table follows the header.
    
    # Let's try to extract the section first
    rtm_section = re.split(r'^## Requirements Traceability', content, flags=re.MULTILINE)[1]
    # Stop at next header
    rtm_block = re.split(r'^## ', rtm_section.strip(), flags=re.MULTILINE)[0]
    
    rows = parse_markdown_table(rtm_block)
    
    if not rows:
        print("Error: Requirements Traceability Matrix table is empty or invalid.")
        sys.exit(1)
        
    # 3. Check for specific columns
    expected_cols = ['ID', 'Requirement']
    if not all(col in rows[0] for col in expected_cols):
         print(f"Error: RTM table must contain columns: {expected_cols}")
         sys.exit(1)

    print(f"Success: Found {len(rows)} requirements in TASK.md.")
    sys.exit(0)

def validate_plan(plan_path, task_path):
    """
    Validates PLAN.md against TASK.md RTM.
    """
    if not os.path.exists(plan_path):
        print(f"Error: File '{plan_path}' not found.")
        sys.exit(1)
    if not os.path.exists(task_path):
        print(f"Error: File '{task_path}' not found.")
        sys.exit(1)

    with open(task_path, 'r') as f:
        task_content = f.read()
    
    # check for bypass
    if "[BYPASS_VALIDATION]" in task_content:
         print("Validation bypassed via [BYPASS_VALIDATION] flag.")
         sys.exit(0)

    # Extract IDs from TASK
    if "## Requirements Traceability" not in task_content:
        print("Error: '## Requirements Traceability' section missing in TASK.md.")
        sys.exit(1)

    rtm_section = re.split(r'^## Requirements Traceability', task_content, flags=re.MULTILINE)[1]
    rtm_block = re.split(r'^## ', rtm_section.strip(), flags=re.MULTILINE)[0]
    rows = parse_markdown_table(rtm_block)
    
    if not rows:
        print("Error: RTM table invalid.")
        sys.exit(1)
        
    rtm_ids = [r['ID'] for r in rows if 'ID' in r]
    
    if not rtm_ids:
        print("Error: No IDs found in RTM table.")
        sys.exit(1)

    # Check PLAN for IDs
    with open(plan_path, 'r') as f:
        plan_content = f.read()

    missing_ids = []
    for rid in rtm_ids:
        # Strict checking: Expecting "[RID]" or just "RID" if defined loosely?
        # Proposal said: "Checklist items MUST start with the RTM ID (e.g., [R1] Implement...)."
        # So we look for `[RID]` in the plan content.
        pattern = re.escape(f"[{rid}]")
        if pattern not in plan_content:
            missing_ids.append(rid)
            
    if missing_ids:
        print(f"Error: The following Requirement IDs are NOT covered in PLAN.md: {missing_ids}")
        print("Please ensure every RTM item differs a checklist item starting with [ID].")
        sys.exit(1)
        
    print(f"Success: All {len(rtm_ids)} requirements covered in PLAN.md.")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Validate artifacts for VDD-Enhanced workflow.")
    parser.add_argument("--mode", required=True, choices=['task', 'plan'], help="Validation mode")
    parser.add_argument("files", nargs='+', help="Input files. mode=task: [task.md], mode=plan: [plan.md task.md]")
    
    args = parser.parse_args()
    
    if args.mode == 'task':
        if len(args.files) < 1:
            print("Error: mode=task requires [task_path]")
            sys.exit(1)
        validate_task(args.files[0])
        
    elif args.mode == 'plan':
        if len(args.files) < 2:
            print("Error: mode=plan requires [plan_path] [task_path]")
            sys.exit(1)
        validate_plan(args.files[0], args.files[1])

if __name__ == "__main__":
    main()
