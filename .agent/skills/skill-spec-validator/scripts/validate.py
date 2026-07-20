#!/usr/bin/env python3
import sys
import argparse
import re
import os

# The RTM heading, matched against the shapes the repo ACTUALLY ships. A survey of
# docs/tasks/ finds the section written at least six ways — h2 AND h3, with/without a
# section number, with a trailing "(RTM)", and the current form `### N. Requirements (RTM)`
# which drops the word "Traceability" entirely. The old `## Requirements Traceability`
# literal (and its `$`-anchored relaxation) matched NONE of them, so this gate had never
# once passed on a shipped artifact and Step-1 validation was, in practice, skipped. A gate
# that cannot pass on the artifacts it governs is not a gate.
#
# Rule: an h2..h4 heading, an optional "N."/"N)" section number, then a lookahead requiring
# the line to name the RTM — either "Requirements Traceability[ Matrix]" or a bare "(RTM)"
# token. Kept zero-width / non-capturing so RTM_HEADER.split() stays clean. The table checks
# below (non-empty, columns ID + Requirement) are UNCHANGED.
RTM_HEADER = re.compile(
    r'^#{2,4}\s+(?:\d+[.)]\s*)?(?=.*(?:Requirements\s+Traceability|\bRTM\b)).*$',
    re.MULTILINE | re.IGNORECASE)


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
    if not RTM_HEADER.search(content):
        print("Error: '## Requirements Traceability' section missing in TASK.md.")
        print("Please add the RTM table (a section number and a trailing "
              "'Matrix' are both fine).")
        sys.exit(1)
        
    # 2. Extract Table
    # A simple regex to find the table block might be needed if parse_markdown_table isn't robust enough for full file
    # But usually the table follows the header.
    
    # Let's try to extract the section first
    rtm_section = RTM_HEADER.split(content)[1]
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
    if not RTM_HEADER.search(task_content):
        print("Error: '## Requirements Traceability' section missing in TASK.md.")
        sys.exit(1)

    rtm_section = RTM_HEADER.split(task_content)[1]
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

    # The contract is "every RTM item is referenced somewhere in the PLAN". Enforce THAT,
    # not a literal `[**R-1**]` token — which is what the original version demanded and why
    # the gate never passed on a shipped plan.
    #
    # IDs are referenced wherever the plan tracks them: the corpus splits between `- [ ]`
    # checklist bullets and `## Step N — ... (R1, R2)` step headings (some plans use prose),
    # so restricting to checklist lines would fail the majority. Search the WHOLE plan body,
    # but as a WHOLE TOKEN — `R1` must not be satisfied by `R10`, and the token charset
    # includes `-` for hyphenated namespaces (`R-065-1`, `TF-X-7`). IDs are normalised of
    # markdown emphasis / brackets / backticks first. A genuinely un-referenced ID (e.g. a
    # plan that omits R10, or tracks findings under a different `F#` scheme) is a real
    # traceability gap — reporting it is the gate doing its job, not a false negative.
    missing_ids = []
    for rid in rtm_ids:
        bare = rid.strip().strip("*`[] ")
        if not bare:
            continue
        token = re.compile(r'(?<![\w-])' + re.escape(bare) + r'(?![\w-])')
        if not token.search(plan_content):
            missing_ids.append(bare)

    if missing_ids:
        print(f"Error: The following Requirement IDs are NOT covered in PLAN.md: {missing_ids}")
        print("Please reference every RTM ID somewhere in PLAN.md "
              "(a step heading like '## Step 1 — ... (R1)' or a '- [ ] R1 ...' bullet).")
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
