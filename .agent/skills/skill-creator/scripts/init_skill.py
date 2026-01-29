#!/usr/bin/env python3
import os
import argparse
import sys

def create_skill(name, base_path, tier):
    """
    Creates a new skill directory with the standard Antigravity structure.
    """
    # Sanitize name
    safe_name = name.lower().replace(" ", "-").replace("_", "-")
    skill_dir = os.path.join(base_path, safe_name)

    if os.path.exists(skill_dir):
        print(f"Error: Skill directory '{skill_dir}' already exists.")
        sys.exit(1)

    # 1. Create Directories
    try:
        os.makedirs(skill_dir)
        os.makedirs(os.path.join(skill_dir, "scripts"))
        os.makedirs(os.path.join(skill_dir, "examples"))
        os.makedirs(os.path.join(skill_dir, "resources"))
        print(f"Created directory structure in {skill_dir}/")
    except OSError as e:
        print(f"Error creating directories: {e}")
        sys.exit(1)

    # 2. Create SKILL.md from Template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "..", "resources", "SKILL_TEMPLATE.md")
    
    skill_md_content = ""
    
    if os.path.exists(template_path):
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Replace placeholders
            skill_md_content = template_content.replace("skill-[name]", safe_name)
            skill_md_content = skill_md_content.replace("[Skill Name]", name.replace("-", " ").title())
            skill_md_content = skill_md_content.replace("[0|1|2]", tier)
            # Basic cleanup of other placeholders to make it valid YAML
            # We leave the [Detailed explanation...] parts for the user to fill
            
            print(f"Loaded template from {template_path}")
        except Exception as e:
            print(f"Warning: Could not read template file: {e}")
            skill_md_content = ""
    
    # Fallback if template missing or failed
    if not skill_md_content:
        skill_md_content = f"""---
name: {safe_name}
description: "Use when [TRIGGER]... (One-line constraints)"
tier: {tier}
version: 1.0
---
# {name.replace("-", " ").title()}

## Purpose
TODO: Describe the primary purpose of this skill.

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I'll skip the tests" -> **WRONG**. Tests are mandatory.
- "I'll just write text logic" -> **WRONG**. Logic > 5 lines must be a script.

## 2. Capabilities
- [Capability 1]

## 3. Instructions
1. Step 1 (Imperative)

## 4. Best Practices

| DO THIS | DO NOT DO THIS |
| :--- | :--- |
| Strong Verbs | Weak language (should, try) |

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "It's too simple" | Simple tasks are where quality slips. |

## 5. Examples
See `examples/` for reference usage.
"""
    
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_md_content)
    print("Created SKILL.md template.")

    # 3. Create Placeholder Files
    with open(os.path.join(skill_dir, "scripts", ".keep"), "w") as f:
        f.write("")
    with open(os.path.join(skill_dir, "examples", "usage_example.md"), "w") as f:
        f.write(f"# Usage Example for {name}\n\nTODO: Add a concrete example of how to use this skill.")
    with open(os.path.join(skill_dir, "resources", "template.txt"), "w") as f:
        f.write("TODO: Add any static templates or assets here.")

    print(f"\nSkill '{safe_name}' initialized successfully!")
    print(f"Path: {os.path.abspath(skill_dir)}")
    
    if not safe_name.endswith("ing") and "-" in safe_name:
        print("\n> [!TIP] Consideration: Best practices suggest using Gerund Form for names (e.g., 'processing-pdfs' instead of 'pdf-processor').")

def main():
    parser = argparse.ArgumentParser(description="Initialize a new Agent Skill (Antigravity Standard).")
    parser.add_argument("name", help="Name of the skill (e.g., 'pdf-editor')")
    parser.add_argument("--path", default=".agent/skills", help="Output directory (default: .agent/skills)")
    parser.add_argument("--tier", type=str, default="2", choices=["0", "1", "2"], help="Skill Tier (0=Bootstrap, 1=Phase, 2=Extended)")

    args = parser.parse_args()

    project_root = os.getcwd()
    # Resolve path relative to CWD if it's not absolute
    target_path = os.path.abspath(args.path)
    
    create_skill(args.name, target_path, args.tier)

if __name__ == "__main__":
    main()
