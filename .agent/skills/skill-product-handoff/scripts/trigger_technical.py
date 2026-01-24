#!/usr/bin/env python3
import sys
import os

def trigger_technical(brd_path, task_output_path):
    """
    Creates the initial Technical TASK.md to start development.
    """
    if not os.path.exists(brd_path):
        print(f"FAIL: BRD not found at {brd_path}")
        return False
        
    try:
        # Use relative path for portability
        # Assuming brd_path is relative to project root
        relative_link = brd_path
        
        task_content = f"""# Task: Technical Architecture & Planning

> **Status:** Todo
> **Parent Initiative:** [BRD]({relative_link})

---

## 1. Executive Summary
**Objective:** Architecture and Planning phase for the approved BRD.
**Input:** `docs/BRD.md`

---

## 2. Implementation Steps

1.  **Architecture Design**:
    - [ ] Analyze BRD.
    - [ ] Create `docs/ARCHITECTURE.md`.
    
2.  **Implementation Planning**:
    - [ ] Create `docs/PLAN.md`.
    - [ ] Break down tasks.

---
"""
    
        with open(task_output_path, 'w') as f:
            f.write(task_content)
            
        print(f"SUCCESS: Technical Triggered. Task created at {task_output_path}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to trigger technical phase: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 trigger_technical.py <brd_path> <task_output_path>")
        sys.exit(1)
    
    brd_path = sys.argv[1]
    task_out = sys.argv[2]
    
    trigger_technical(brd_path, task_out)
