#!/usr/bin/env python3
import sys
import os
import re

def verify_gate(backlog_path):
    """
    Checks if the backlog contains a valid APPROVAL_HASH line.
    Hash Format: APPROVAL_HASH: <UUID>-<TIMESTAMP>-APPROVED
    """
    if not os.path.exists(backlog_path):
        print(f"FAIL: File not found: {backlog_path}")
        return False

    try:
        with open(backlog_path, 'r') as f:
            content = f.read()

        # Regex for UUID-TIMESTAMP-APPROVED
        # UUID: 8-4-4-4-12 hex chars
        # Timestamp: digits
        hash_pattern = r"^APPROVAL_HASH: [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}-\d+-APPROVED$"
        
        matches = re.findall(hash_pattern, content, re.MULTILINE)
        
        if not matches:
            print("FAIL: No valid APPROVAL_HASH found.")
            print("Expected format: APPROVAL_HASH: <UUID>-<TIMESTAMP>-APPROVED")
            return False
        
        print(f"SUCCESS: Found valid hash: {matches[0]}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to verify gate: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify_gate.py <path_to_approved_backlog>")
        sys.exit(1)
        
    path = sys.argv[1]
    if verify_gate(path):
        sys.exit(0)
    else:
        sys.exit(1)
