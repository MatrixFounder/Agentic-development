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

    # 2. Create SKILL.md Template
    skill_md_content = f"""---
name: {safe_name}
description: "TODO: One-line summary of what this skill enables the agent to do."
tier: {tier}
version: 1.0
---
# {name.replace("-", " ").title()}

## Purpose
TODO: Describe the primary purpose of this skill.

## Usage
TODO: Describe when and how to use this skill.

## Examples
See `examples/` for reference usage.
"""
    
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_md_content)
    print("Created SKILL.md template.")

    # 3. Create Placeholder Files
    with open(os.path.join(skill_dir, "scripts", ".keep"), "w") as f:
        f.write("")
    with open(os.path.join(skill_dir, "examples", "usage_example.md"), "w") as f:
        f.write("# Usage Example\n\nTODO: Add a concrete example of how to use this skill.")
    with open(os.path.join(skill_dir, "resources", "template.txt"), "w") as f:
        f.write("TODO: Add any static templates or assets here.")

    print(f"\nSkill '{safe_name}' initialized successfully!")
    print(f"Path: {os.path.abspath(skill_dir)}")

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
