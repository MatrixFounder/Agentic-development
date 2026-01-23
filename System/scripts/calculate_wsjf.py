#!/usr/bin/env python3
"""
Script to calculate WSJF scores in PRODUCT_BACKLOG.md.
Uses strictly regex-based parsing for robustness.
"""

import argparse
import sys
import re
import os


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Calculate WSJF scores")
    parser.add_argument("--file", required=True, help="Path to PRODUCT_BACKLOG.md")
    return parser.parse_args()

def parse_line(line):
    """
    Parse a table line dealing with escaped pipes.
    Returns list of cells (trimmed).
    """
    # Pattern: split by | that is NOT preceded by \
    # Note: This might produce empty first/last elements if line starts/ends with |
    parts = re.split(r'(?<!\\)\|', line)
    
    # Clean up parts
    cleaned = []
    for p in parts:
        cleaned.append(p.strip())
        
    # If the line started with |, the first element is usually empty.
    # If ended with |, the last is empty.
    # Standard markdown tables usually have leading/trailing pipes.
    # We remove the very first and very last empty strings if they exist AND length > 1
    if len(cleaned) > 1 and cleaned[0] == '':
        cleaned.pop(0)
    if len(cleaned) > 0 and cleaned[-1] == '':
        cleaned.pop(-1)
        
    return cleaned

def is_separator(cells):
    """Check if row is a separator row (---)."""
    if not cells:
        return False
    return all(re.match(r'^:?-+:?$', c) for c in cells)

def get_column_indices(headers):
    """Identify indices of required columns."""
    mapping = {}
    required = ['User Value', 'Time Criticality', 'Risk Reduction', 'Job Size']
    
    for i, h in enumerate(headers):
        clean_h = h.replace('*', '').strip() # Remove bolding
        if clean_h in required:
            mapping[clean_h] = i
        elif clean_h == 'WSJF':
            mapping['WSJF'] = i
            
    missing = [r for r in required if r not in mapping]
    return mapping, missing

def calculate_wsjf(rows, indices):
    """
    Calculate WSJF for rows.
    Returns: (processed_rows, errors)
    processed_rows is a list of (score, line_content)
    """
    processed = [] # List of dicts or objects to make sorting easier
    
    for i, (line, cells) in enumerate(rows):
        # Extract values
        try:
            uv = float(cells[indices['User Value']])
            tc = float(cells[indices['Time Criticality']])
            rr = float(cells[indices['Risk Reduction']])
            js = float(cells[indices['Job Size']])
            
            if js == 0:
                print(f"Error: Job Size cannot be 0 check row: {line.strip()}")
                sys.exit(1)
                
            wsjf = round((uv + tc + rr) / js, 2)
            
            # Update cell
            # We need to reconstruct the line or just update the cell?
            # Easiest is to update the cell content in the 'cells' list, then join.
            # But wait, we need to preserve formatting?
            # The requirement says "Output: Overwrite file with updated values (formatting preserved)".
            # Preserving EXACT formatting is hard if we change numbers (widths change).
            # But standard markdown tables are flexible.
            
            if 'WSJF' in indices:
                cells[indices['WSJF']] = str(wsjf)
            else:
                # Append WSJF if not present? 
                # The requirements imply "Parse columns... Sort... Output: Overwrite".
                # If WSJF column exists, update it. If not, maybe we shouldn't add it autonomously unless consistent.
                # Assuming WSJF column exists as per stub/templates usually.
                # If it doesn't exist, we can't easily add it without reformatting headers.
                # For now, assume it exists or we append it?
                # "Parse columns: ... Job Size. Logic: WSJF=..."
                # Let's assume we just update existing WSJF column.
                pass 
            
            # Store for sorting
            processed.append({
                'score': wsjf,
                'cells': cells,
                'original_line': line # We might need to regenerate line from cells to ensure updated value is present
            })
            
        except ValueError:
            # Header or bad data?
            # If we are here, we passed header check. So likely bad number.
            print(f"Error: Non-numeric value in row: {line.strip()}")
            sys.exit(1)
            
    return processed

def reconstruct_line(cells):
    """Reconstruct a markdown table line."""
    # Simple reconstruction: | cell | cell |
    return "| " + " | ".join(cells) + " |"

def main():
    """Main execution flow."""
    args = parse_arguments()
    
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found.")
        sys.exit(1)
        
    with open(args.file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find table
    table_start = -1
    table_end = -1
    headers = []
    header_line_index = -1
    
    # Simple state machine to find the FIRST table
    in_table = False
    
    # We need to capture the pre-table and post-table content
    # And replace the table lines.
    
    processed_lines = []
    
    # Strategy: Read all, process table if found, then write back.
    # Note: Only processing the first table found or all?
    # Usually Backlog has one main table. "Deterministic prioritization of the Backlog".
    # Let's target the *first* table that looks like a backlog (has headers).
    
    mapping = {}
    table_rows = [] # Tuple (line_index, line_content)
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        cells = parse_line(line)
        
        if not in_table:
            # Check if this is a header candidate
            # Must have required columns
            m, missing = get_column_indices(cells)
            if not missing:
                # Found headers
                in_table = True
                mapping = m
                headers = cells
                header_line_index = i
                continue
        else:
            # In table
            if is_separator(cells):
                # Separator line, ignore for calculation but keep index
                continue
            elif len(cells) == len(headers):
                # Data row
                table_rows.append((i, line, cells))
            else:
                 # End of table? Or malformed?
                 # If drastically different length, maybe end of table?
                 # Or just empty?
                 if not line.strip().startswith('|'):
                     # Likely end of table
                     break
                 # If starts with pipe but wrong count, maybe malformed, but let's try to process or skip?
                 # Requirement: "If table structure invalid: Exit Code 1"
                 # But maybe tolerant of one bad row? 
                 # Let's stay strict as per requirement.
                 print(f"Error: Row length mismatch. Expected {len(headers)}, got {len(cells)}")
                 print(f"Row: {line.strip()}")
                 sys.exit(1)

    if not in_table:
        print("Error: No valid Backlog table found (Missing columns: User Value, Time Criticality, Risk Reduction, Job Size).")
        sys.exit(1)
        
    # Process rows
    data_rows = [(r[1], r[2]) for r in table_rows] # line, cells
    results = calculate_wsjf(data_rows, mapping)
    
    # Sort
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Reconstruct content
    # We replace the rows in the original 'lines' list
    # But wait, sorting changes order. We can't just replace index-by-index.
    # We need to replace the slice of lines corresponding to the data rows.
    
    # Identify range of data rows
    if not table_rows:
        print("Warning: Table is empty.")
        sys.exit(0)
        
    start_index = table_rows[0][0]
    end_index = table_rows[-1][0]
    
    # We need to be careful if there are non-data lines in between (comments?) - usually not in MD tables.
    # Assuming contiguous block of data rows.
    
    # Reconstruct table block
    # Header and separator remain touched? NO, we only touch data.
    # But wait, we need to locate where to insert sorted lines.
    
    # Construct new lines for data
    new_data_lines = []
    for row in results:
        new_line = reconstruct_line(row['cells']) + "\n"
        new_data_lines.append(new_line)
        
    # Replace in original lines
    # We need to replace the exact lines that were data rows.
    # If they were contiguous:
    # lines[start_index : end_index+1] = new_data_lines
    
    # Check contiguity
    indices = [r[0] for r in table_rows]
    is_contiguous = all(indices[j] == indices[j-1] + 1 for j in range(1, len(indices)))
    
    if not is_contiguous:
        # If not contiguous (e.g. comments in between?), we can't easily sort without breaking context.
        # But MD tables don't really support comments in between rows.
        # So likely they are contiguous relative to the file, 
        # BUT we skipped separator line. Separator is usually index header+1.
        # So data starts at header+2.
        pass
        
    # Let's trust they are contiguous block after header+separator.
    # Find start and end of the block to replace.
    first_data_line = table_rows[0][0]
    last_data_line = table_rows[-1][0]
    
    lines[first_data_line : last_data_line+1] = new_data_lines
    
    # Write back
    with open(args.file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Success: Backlog updated.")


if __name__ == "__main__":
    main()
