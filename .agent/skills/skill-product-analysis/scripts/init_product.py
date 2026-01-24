#!/usr/bin/env python3
"""
Script to scaffold docs/PRODUCT_VISION.md.
Dual-mode: Interactive (prompts user) and Headless (args).
"""

import argparse
import sys
import os


# Default Template
VISION_TEMPLATE = """# Product Vision: {name}

## 1. Problem Statement
**The Problem:** {problem}

## 2. Target Audience
**Who is this for?** {audience}

## 3. Solution & Value
**The Solution:** [ Describe the solution ]

## 4. Success Metrics (KPIs)
{metrics}

## 5. Timeline (Rough)
- **Phase 0:** Bootstrap
- **Phase 1:** MVP
"""

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Scaffold PRODUCT_VISION.md")
    parser.add_argument("--name", help="Product Name")
    parser.add_argument("--problem", help="Problem Statement")
    parser.add_argument("--audience", help="Target Audience")
    parser.add_argument("--metrics", help="Success Metrics")
    parser.add_argument("--output", default="docs/PRODUCT_VISION.md", help="Output file path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing file")
    return parser.parse_args()

def interactive_mode():
    """Gather input from user interactively."""
    print("Interactive Mode: Please answer the following questions.")
    data = {}
    data['name'] = input("Product Name: ").strip() or "Untitled Product"
    data['problem'] = input("Problem Statement: ").strip() or "To be defined"
    data['audience'] = input("Target Audience: ").strip() or "To be defined"
    data['metrics'] = input("Success Metrics (comma separated): ").strip()
    
    # Format metrics as list if provided
    if data['metrics']:
        metrics_list = [m.strip() for m in data['metrics'].split(',')]
        data['metrics'] = "\\n".join([f"- {m}" for m in metrics_list])
    else:
        data['metrics'] = "- [ ] Define KPI 1"
        
    return data

def generate_content(data):
    """Generate Markdown content from data."""
    return VISION_TEMPLATE.format(**data)

def main():
    """Main execution flow."""
    args = parse_arguments()
    
    data = {}
    
    # Determine mode
    if args.name or args.problem or args.audience:
        # Headless/Partial Headless
        data['name'] = args.name or "Untitled Product"
        data['problem'] = args.problem or "To be defined"
        data['audience'] = args.audience or "To be defined"
        if args.metrics:
             metrics_list = [m.strip() for m in args.metrics.split(',')]
             data['metrics'] = "\\n".join([f"- {m}" for m in metrics_list])
        else:
             data['metrics'] = "- [ ] Define KPI 1"
    else:
        # Interactive
        try:
            data = interactive_mode()
        except KeyboardInterrupt:
            print("\\nCancelled.")
            sys.exit(1)

    # Generate content
    content = generate_content(data)
    
    # Output handling
    output_path = args.output
    
    # Check existence
    if os.path.exists(output_path) and not args.force:
        print(f"Error: File '{output_path}' already exists.")
        print("Use --force to overwrite.")
        sys.exit(1)
        
    # Write file
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Success: Created {output_path}")
    except OSError as e:
        print(f"Error: Failed to write file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
