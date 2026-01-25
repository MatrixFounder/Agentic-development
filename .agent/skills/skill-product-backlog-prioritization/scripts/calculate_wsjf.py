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

def map_size_to_fib(value_str):
    """Maps T-shirt sizes or hours to WSJF Fibonacci scale."""
    val = value_str.upper().strip()
    
    # Text mapping
    mapping = {
        'XS': 1, 'EXTRA SMALL': 1,
        'S': 2, 'SMALL': 2,
        'M': 5, 'MEDIUM': 5,
        'L': 13, 'LARGE': 13,
        'XL': 20, 'EXTRA LARGE': 20,
        'XXL': 40, '2XL': 40
    }
    
    # Check for direct match
    if val in mapping:
        return mapping[val]
    
    # Check for "M (60h)" format
    match = re.match(r'^([A-Z]+)', val)
    if match and match.group(1) in mapping:
        return mapping[match.group(1)]
        
    # Check for numeric (direct input)
    try:
        # If number is > 100, assume it's hours and map it down
        num = float(val)
        if num > 40: # Assume hours
             if num <= 10: return 1
             if num <= 30: return 2
             if num <= 80: return 5
             if num <= 200: return 13
             if num <= 500: return 20
             return 40
        return max(1, num) # Ensure at least 1
    except ValueError:
        return 20 # Unknown/High default penalty

def calculate_wsjf(rows, indices):
    """
    Calculate WSJF for rows.
    Returns: (processed_rows, errors)
    processed_rows is a list of (score, line_content)
    """
    processed = [] 
    
    for i, (line, cells) in enumerate(rows):
        try:
            uv = float(cells[indices['User Value']])
            tc = float(cells[indices['Time Criticality']])
            rr = float(cells[indices['Risk Reduction']])
            
            # Smart sizing
            size_raw = cells[indices['Job Size']]
            js = map_size_to_fib(size_raw)
            
            if js == 0: js = 1 # Avoid div by zero
                
            wsjf = round((uv + tc + rr) / js, 2)
            
            # Update output column
            if 'WSJF' in indices:
                cells[indices['WSJF']] = str(wsjf)
            
            processed.append({
                'score': wsjf,
                'cells': cells,
                'line_idx': i # Keep track if we need it
            })
            
        except (ValueError, IndexError):
            print(f"Warning: Skipping invalid row: {line.strip()}")
            # Keep original order for bad rows? Or drop? 
            # Requirements say "Overwrite". Better to preserve bad rows at bottom or top?
            # Or just fail? Legacy script failed. Let's fail for safety.
            print(f"Error: Non-numeric value in critical column (UV, TC, RR) in row: {line.strip()}")
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
    
    in_table = False
    table_rows = [] # Tuple (line_index, line_content, cells)
    mapping = {}
    
    for i, line in enumerate(lines):
        if not line.strip(): continue
        cells = parse_line(line)
        
        if not in_table:
            m, missing = get_column_indices(cells)
            if not missing:
                in_table = True
                mapping = m
                headers = cells
                continue
        else:
            if is_separator(cells): continue
            elif len(cells) >= len(headers):
                table_rows.append((i, line, cells))
            else:
                if not line.strip().startswith('|'): break
                else: 
                     # Tolerant of malformed lines?
                     pass

    if not in_table:
        print("Error: No valid Backlog table found (Missing columns: User Value, Time Criticality, Risk Reduction, Job Size).")
        sys.exit(1)
        
    # Process rows
    data_rows = [(r[1], r[2]) for r in table_rows] # line, cells
    results = calculate_wsjf(data_rows, mapping)
    
    # Sort
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Reconstruct
    new_data_lines = []
    for row in results:
        new_data_lines.append(reconstruct_line(row['cells']) + "\n")
        
    if not table_rows:
        sys.exit(0)
        
    start_index = table_rows[0][0]
    last_index = table_rows[-1][0]
    
    lines[start_index : last_index+1] = new_data_lines
    
    with open(args.file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Success: Backlog updated.")

if __name__ == "__main__":
    main()
