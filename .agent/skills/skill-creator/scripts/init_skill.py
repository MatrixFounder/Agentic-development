#!/usr/bin/env python3
import os
import argparse
import sys

# Add script directory to path to import skill_utils
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
import skill_utils

def create_skill(name, base_path, tier_value, config):
    """
    Creates a new skill directory with the standard structure.
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
        os.makedirs(os.path.join(skill_dir, "assets"))
        os.makedirs(os.path.join(skill_dir, "references"))
        print(f"Created directory structure in {skill_dir}/")
    except OSError as e:
        print(f"Error creating directories: {e}")
        sys.exit(1)

    # 2. Create SKILL.md from Template
    template_path = os.path.join(script_dir, "..", "assets", "SKILL_TEMPLATE.md")
    skill_md_content = ""
    
    if os.path.exists(template_path):
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Replace placeholders
            skill_md_content = template_content.replace("skill-[name]", safe_name)
            skill_md_content = skill_md_content.replace("[Skill Name]", name.replace("-", " ").title())
            skill_md_content = skill_md_content.replace("[TIER_VALUE]", str(tier_value))
            
            print(f"Loaded template from {template_path}")
        except Exception as e:
            print(f"Warning: Could not read template file: {e}")
            skill_md_content = ""
            
    # Fallback if template missing
    if not skill_md_content:
        skill_md_content = f"""---
name: {safe_name}
description: "Use when [TRIGGER]... (One-line constraints)"
tier: {tier_value}
version: 1.0
---
# {name.replace("-", " ").title()}
## Purpose
TODO: Describe the primary purpose of this skill.
"""

    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_md_content)
    print("Created SKILL.md template.")

    # 3. Create Placeholder Files
    with open(os.path.join(skill_dir, "scripts", ".keep"), "w") as f:
        f.write("")
    with open(os.path.join(skill_dir, "examples", "usage_example.md"), "w") as f:
        f.write(f"# Usage Example for {name}\n\nTODO: Add a concrete example of how to use this skill.")
    with open(os.path.join(skill_dir, "assets", "template.txt"), "w") as f:
        f.write("TODO: Add any static templates or assets here (files used for output).")
    with open(os.path.join(skill_dir, "references", "guidelines.md"), "w") as f:
        f.write("# Guidelines\nTODO: Add domain knowledge, API specs, or rules here.")

    print(f"\nSkill '{safe_name}' initialized successfully!")
    print(f"Path: {os.path.abspath(skill_dir)}")
    
    # 4. Reminder Check
    catalog_file = config.get('project_config', {}).get('catalog_file')
    if catalog_file and os.path.exists(catalog_file):
        print(f"\n> [!IMPORTANT] NEXT STEP: Please update '{catalog_file}' to register this new skill!")
    
    # 5. Mandatory Cleanup Instructions
    print("\n" + "="*60)
    print("MANDATORY CLEANUP REQUIRED")
    print("="*60)
    print(f"Skill created at: {skill_dir}")
    print("1. IMPLEMENT your skill (Add scripts, assets, examples).")
    print("2. CLEANUP unused directories:")
    print(f"   - Scripts: If logic < 5 lines, delete '{skill_dir}/scripts/'")
    print(f"   - Assets: If no assets, delete '{skill_dir}/assets/'")
    print(f"   - References: If no ext refs, delete '{skill_dir}/references/'")
    print(f"   - Examples: Update usage_example.md or delete folder if Simple Skill.")
    print("="*60 + "\n")

def main():
    # 1. Load Configuration
    project_root = os.getcwd() # Assume run from root
    config = skill_utils.load_config(project_root)
    
    # 2. Extract Options
    tier_defs = config.get('taxonomy', {}).get('tiers', [])
    valid_tiers = [str(t.get('value')) for t in tier_defs] if tier_defs else ["0", "1", "2"]
    
    default_root = config.get('project_config', {}).get('skills_root', '.agent/skills')

    # Build rich help for tiers
    tier_help = "Skill Tier choices:\n"
    if tier_defs:
        for t in tier_defs:
            val = t.get('value')
            name = t.get('name', '')
            desc = t.get('description', '')
            tier_help += f"    {val}: {name} - {desc}\n"
    else:
        tier_help += "    [0, 1, 2] (Default tiers)"

    parser = argparse.ArgumentParser(
        description="Initialize a new Agent Skill (Portable Standard).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("name", help="Name of the skill (e.g., 'pdf-editor')")
    parser.add_argument("--path", default=default_root, help=f"Output directory (default: {default_root})")
    parser.add_argument("--tier", type=str, default="2", choices=valid_tiers, help=tier_help)

    args = parser.parse_args()

    # Resolve path relative to CWD if it's not absolute
    target_path = os.path.abspath(args.path)
    
    create_skill(args.name, target_path, args.tier, config)

if __name__ == "__main__":
    main()
