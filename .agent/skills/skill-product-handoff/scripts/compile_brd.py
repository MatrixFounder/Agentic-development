#!/usr/bin/env python3
import sys
import os
import datetime

def read_file(path):
    if not os.path.exists(path):
        return f"> *Missing Artifact: {path}*"
    with open(path, 'r') as f:
        return f.read()

def compile_brd(product_dir, output_path, template_path):
    """
    Compiles separate markdown files into a single BRD.
    """
    
    # Paths
    market_strategy = os.path.join(product_dir, "MARKET_STRATEGY.md")
    product_vision = os.path.join(product_dir, "PRODUCT_VISION.md")
    solution_blueprint = os.path.join(product_dir, "SOLUTION_BLUEPRINT.md")
    
    # Read Content
    strategy_content = read_file(market_strategy)
    vision_content = read_file(product_vision)
    blueprint_content = read_file(solution_blueprint)
    
    # Read Template (if we were using a real template file, but here we can construct it or read it)
    # For simplicity, we will construct the BRD structure programmatically to match the Vision v3.2 spec
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    brd = f"""# Business Requirements Document (BRD)
> **Generated:** {timestamp}
> **Status:** Compiled

---

## 1. Introduction
This document aggregates the approved product strategy, vision, and solution design into a single source of truth.

---

## 2. Market Strategy (Source: MARKET_STRATEGY.md)
{strategy_content}

---

## 3. Product Vision (Source: PRODUCT_VISION.md)
{vision_content}

---

## 4. Solution Blueprint (Source: SOLUTION_BLUEPRINT.md)
{blueprint_content}

---

## 5. Appendices
- [Original Strategy]({market_strategy})
- [Original Vision]({product_vision})
- [Original Blueprint]({solution_blueprint})
"""

    with open(output_path, 'w') as f:
        f.write(brd)
        
    print(f"SUCCESS: BRD compiled at {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 compile_brd.py <product_dir> <output_path>")
        sys.exit(1)
        
    product_dir = sys.argv[1]
    output_path = sys.argv[2]
    
    compile_brd(product_dir, output_path, None)
