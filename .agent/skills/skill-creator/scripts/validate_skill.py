#!/usr/bin/env python3
import os
import argparse
import sys
# import yaml  <-- Removed dependency

def parse_frontmatter(file_path):
    """
    Parses the YAML frontmatter from a markdown file using basic string parsing.
    Returns a dict. Limitation: Only supports simple key: value pairs.
    """
    with open(file_path, 'r') as f:
        content = f.read()

    lines = content.splitlines()
    if not lines or lines[0].strip() != '---':
        raise ValueError("Missing YAML frontmatter start (---)")

    frontmatter = {}
    found_end = False
    
    for line in lines[1:]:
        if line.strip() == '---':
            found_end = True
            break
        
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            
            # Simple list parsing for 'tier' if it looks like [1, 2]
            if value.startswith('[') and value.endswith(']'):
                # clean up list string
                inner = value[1:-1]
                frontmatter[key] = [x.strip() for x in inner.split(',')]
            else:
                frontmatter[key] = value

    if not found_end:
        raise ValueError("Missing YAML frontmatter end (---)")

    return frontmatter

def validate_skill(skill_path):
    """
    Validates a single skill directory against Antigravity standards.
    """
    skill_name = os.path.basename(os.path.normpath(skill_path))
    print(f"Validating '{skill_name}' at {skill_path}...")
    
    errors = []

    # 1. Check Required Files
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        errors.append("Missing SKILL.md file.")
    
    # 2. Check Prohibited Files
    prohibited = ["README.md", "CHANGELOG.md", "INSTALLATION.md"]
    for item in os.listdir(skill_path):
        if item in prohibited:
            errors.append(f"Prohibited file found: {item} (Instructions belong in SKILL.md)")

    # 3. Check Directory Structure
    allowed_dirs = ["scripts", "examples", "resources"]
    for item in os.listdir(skill_path):
        item_path = os.path.join(skill_path, item)
        if os.path.isdir(item_path):
            if item not in allowed_dirs:
                errors.append(f"Unknown directory '{item}'. Allowed: {allowed_dirs}")
            
            # Enforce content for examples
            if item == "examples":
                # Check for files excluding .DS_Store and .keep
                example_files = [f for f in os.listdir(item_path) if f not in [".DS_Store", ".keep"]]
                if not example_files:
                    errors.append("Directory 'examples/' is empty. You MUST provide at least one example file.")

    # 4. Check SKILL.md Content
    if os.path.exists(skill_md_path):
        try:
            meta = parse_frontmatter(skill_md_path)
            
            # Check Required Fields
            if 'name' not in meta:
                errors.append("Frontmatter missing 'name'")
            elif meta['name'] != skill_name:
                errors.append(f"Frontmatter name '{meta['name']}' does not match directory name '{skill_name}'")
            
            if 'description' not in meta:
                errors.append("Frontmatter missing 'description'")
            else:
                desc = meta['description']
                # CSO Rule 1: Must start with "Use when"
                if not desc.lower().strip().startswith("use when"):
                    errors.append("CSO Violation: Description MUST start with 'Use when...'. Found: " + desc[:30] + "...")
                
                # CSO Rule 2: Token Efficiency (Approx 50 words)
                word_count = len(desc.split())
                if word_count > 50:
                    errors.append(f"CSO Violation: Description is too long ({word_count} words). Keep under 50 words.")

            if 'tier' not in meta:
                errors.append("Frontmatter missing 'tier'")
            elif str(meta['tier']) not in ['0', '1', '2']:
                errors.append(f"Invalid tier '{meta['tier']}'. Must be 0, 1, or 2.")

            if 'version' not in meta:
                errors.append("Frontmatter missing 'version'")

        except Exception as e:
            errors.append(f"YAML Frontmatter Error: {str(e)}")

    # Report
    if errors:
        print(f"❌ Validation FAILED for '{skill_name}':")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print(f"✅ Validation PASSED for '{skill_name}'")
        return True

def main():
    parser = argparse.ArgumentParser(description="Validate an Agent Skill (Antigravity Standard).")
    parser.add_argument("path", help="Path to the skill directory")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"Error: Directory '{args.path}' not found.")
        sys.exit(1)

    success = validate_skill(args.path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
