#!/usr/bin/env python3
import os
import argparse
import sys
import re

# Add script directory to path to import skill_utils
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
import skill_utils

def check_inline_efficiency(content: str, max_lines: int) -> list:
    """
    Checks for inline code blocks larger than max_lines.
    """
    errors = []
    lines = content.splitlines()
    in_block = False
    block_start = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("```"):
            if in_block:
                # End of block
                block_length = i - block_start - 1
                if block_length > max_lines:
                    errors.append(f"Inline code block at line {block_start + 1} is too large ({block_length} lines). Max allowed is {max_lines}. Extract to examples/ or resources/.")
                in_block = False
            else:
                # Start of block
                in_block = True
                block_start = i
                
    return errors

def extract_frontmatter(file_path):
    """
    Extracts frontmatter string from file.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        lines = content.splitlines()
        if not lines or lines[0].strip() != '---':
            return None, "Missing YAML frontmatter start (---)"

        frontmatter_lines = []
        found_end = False
        
        for line in lines[1:]:
            if line.strip() == '---':
                found_end = True
                break
            frontmatter_lines.append(line)

        if not found_end:
            return None, "Missing YAML frontmatter end (---)"

        return "\n".join(frontmatter_lines), None

    except Exception as e:
        return None, f"File Error: {str(e)}"

def extract_body_content(file_path: str) -> str:
    """
    Returns markdown body (without YAML frontmatter when present).
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return ""

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return content

    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return "\n".join(lines[i + 1 :])
    return content


def _normalize_section_title(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def _collect_markdown_headings(body: str) -> list[str]:
    headings = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        heading = stripped.lstrip("#").strip()
        if heading:
            headings.append(heading)
    return headings


def _has_section(headings: list[str], target: str) -> bool:
    needle = _normalize_section_title(target)
    for heading in headings:
        normalized = _normalize_section_title(heading)
        if needle == normalized or needle in normalized:
            return True
    return False


def _has_real_files(directory: str) -> bool:
    if not os.path.isdir(directory):
        return False
    for item in os.listdir(directory):
        if item in [".DS_Store", ".keep"] or item.startswith("."):
            continue
        return True
    return False


def collect_execution_policy_warnings(
    skill_path: str,
    body: str,
    validation_config: dict,
) -> list[str]:
    required_sections = validation_config.get(
        "execution_policy_sections",
        [
            "Execution Mode",
            "Script Contract",
            "Safety Boundaries",
            "Validation Evidence",
        ],
    )
    warnings = []
    headings = _collect_markdown_headings(body)
    missing = [section for section in required_sections if not _has_section(headings, section)]
    missing_normalized = {_normalize_section_title(section) for section in missing}

    # Attempt to extract mode to skip Script Contract for prompt-first
    mode_match = re.search(r'\*\*Mode\*\*:\s*`?(prompt-first|script-first|hybrid)`?', body, re.IGNORECASE)
    mode = mode_match.group(1).lower() if mode_match else "unknown"

    for section in missing:
        normalized_sec = _normalize_section_title(section)
        # Script Contract is optional for prompt-first skills unless scripts/ is populated
        if normalized_sec == _normalize_section_title("Script Contract") and mode == "prompt-first":
            scripts_dir_check = os.path.join(skill_path, "scripts")
            if not _has_real_files(scripts_dir_check):
                continue
        
        warnings.append(
            f"Execution Policy: Missing '{section}' section (warning-first mode)."
        )

    scripts_dir = os.path.join(skill_path, "scripts")
    if _has_real_files(scripts_dir):
        if _normalize_section_title("Script Contract") in missing_normalized:
            warnings.append(
                "Execution Policy: 'scripts/' has executable content but 'Script Contract' is missing."
            )

    body_lower = body.lower()
    mutation_markers = (
        "delete",
        "remove",
        "overwrite",
        "rename",
        "migrate",
        "truncate",
        "destructive",
    )
    if any(marker in body_lower for marker in mutation_markers):
        if _normalize_section_title("Safety Boundaries") in missing_normalized:
            warnings.append(
                "Execution Policy: Mutation/destructive language found but 'Safety Boundaries' is missing."
            )

    if ("python3 scripts/" in body_lower or "scripts/" in body_lower):
        if _normalize_section_title("Validation Evidence") in missing_normalized:
            warnings.append(
                "Execution Policy: Script references found but 'Validation Evidence' is missing."
            )

    return warnings


def validate_skill(skill_path, config, strict_exec_policy=False):
    """
    Validates a single skill directory against configured standards.
    """
    skill_name = os.path.basename(os.path.normpath(skill_path))
    print(f"Validating '{skill_name}' at {skill_path}...")
    
    validation_config = config.get('validation', {})
    taxonomy_config = config.get('taxonomy', {})
    quality_config = validation_config.get('quality_checks', {})
    
    errors = []
    warnings = []

    # 1. Check Required Files
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        errors.append("Missing SKILL.md file.")
    
    # 2. Check Prohibited Files (Configurable)
    prohibited = validation_config.get('prohibited_files', [])
    for item in os.listdir(skill_path):
        if item in prohibited:
            errors.append(f"Prohibited file found: {item} (See .agent/rules/skill_standards.yaml)")

    # 3. Check Directory Structure (Standard)
    allowed_dirs = ["scripts", "examples", "assets", "references", "config", "agents", "evals"]
    for item in os.listdir(skill_path):
        item_path = os.path.join(skill_path, item)
        if os.path.isdir(item_path):
            if item not in allowed_dirs:
                if item == "resources":
                     errors.append(f"Deprecated directory 'resources/'. Please split into 'assets/' (output materials) and 'references/' (knowledge).")
                else:
                     warnings.append(f"Non-standard directory '{item}'. Known directories: {allowed_dirs}")
            
            # Enforce content for examples
            if item == "examples":
                example_files = [f for f in os.listdir(item_path) if f not in [".DS_Store", ".keep"]]
                if not example_files:
                    errors.append("Directory 'examples/' is empty. You MUST provide at least one example file.")

    # 4. Check SKILL.md Content
    if os.path.exists(skill_md_path):
        fm_content, err = extract_frontmatter(skill_md_path)
        if err:
            errors.append(err)
        else:
            parser = skill_utils.VanillaYamlParser()
            try:
                meta = parser.parse(fm_content)
                
                # Check Required Fields
                if 'name' not in meta:
                    errors.append("Frontmatter missing 'name'")
                elif meta['name'] != skill_name:
                    errors.append(f"Frontmatter name '{meta['name']}' does not match directory name '{skill_name}'")
                
                if 'description' not in meta:
                    errors.append("Frontmatter missing 'description'")
                else:
                    desc = meta['description']
                    # CSO Rule 1: Configured Prefixes (optional, configurable)
                    enforce_cso_prefix = validation_config.get('enforce_cso_prefix', True)
                    allowed_prefixes = validation_config.get('allowed_cso_prefixes', [])
                    if enforce_cso_prefix:
                        # Fallback to minimal safe default only when enforcement is enabled.
                        if not allowed_prefixes:
                            allowed_prefixes = ["Use when"]

                        desc_lower = desc.lower().strip()
                        if not any(desc_lower.startswith(prefix.lower()) for prefix in allowed_prefixes):
                            errors.append(f"CSO Violation: Description MUST start with one of {allowed_prefixes}. Found: " + desc[:30] + "...")
                    
                    # CSO Rule 2: Token Efficiency
                    max_words = quality_config.get('max_description_words', 50)
                    word_count = len(desc.split())
                    if word_count > max_words:
                        errors.append(f"CSO Violation: Description matches {word_count} words. Limit is {max_words} words.")

                if 'tier' not in meta:
                    errors.append("Frontmatter missing 'tier'")
                else:
                    raw_tiers = taxonomy_config.get('tiers', [])
                    valid_tiers = [t.get('value') for t in raw_tiers] if raw_tiers else [0, 1, 2] # fallback
                    # Meta tier might be int or string from parser
                    # Normalized comparison
                    tier_val = meta['tier']
                    # Try converting to match config types (usually int)
                    
                    match = False
                    for vt in valid_tiers:
                        if str(vt) == str(tier_val): 
                            match = True 
                            break
                    
                    if not match:
                        errors.append(f"Invalid tier '{tier_val}'. Allowed: {[t['value'] for t in raw_tiers]}")

                if 'version' not in meta:
                    errors.append("Frontmatter missing 'version'")

            except Exception as e:
                errors.append(f"YAML Parse Error: {str(e)}")

            # 5. Check Token Efficiency
            with open(skill_md_path, 'r') as f:
                 raw_content = f.read()
            
            max_inline = quality_config.get('max_inline_lines', 12)
            inline_exempt_skills = set(validation_config.get('inline_exempt_skills', []))
            if skill_name not in inline_exempt_skills:
                efficiency_errors = check_inline_efficiency(raw_content, max_inline)
                errors.extend(efficiency_errors)

            body_content = extract_body_content(skill_md_path)
            warnings.extend(
                collect_execution_policy_warnings(
                    skill_path,
                    body_content,
                    validation_config,
                )
            )

    # Report
    if errors:
        print(f"❌ Validation FAILED for '{skill_name}':")
        for err in errors:
            print(f"  - {err}")
        if warnings:
            print("⚠️  Additional warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        return False

    if warnings:
        print(f"⚠️  Validation PASSED with warnings for '{skill_name}':")
        for warning in warnings:
            print(f"  - {warning}")
        if strict_exec_policy:
            print("❌ Strict execution-policy mode enabled: warnings are treated as failures.")
            return False
        return True

    else:
        print(f"✅ Validation PASSED for '{skill_name}'")
        return True

def main():
    parser = argparse.ArgumentParser(description="Validate an Agent Skill (Portable Standard).")
    parser.add_argument("path", help="Path to the skill directory")
    parser.add_argument(
        "--strict-exec-policy",
        action="store_true",
        help="Treat execution-policy warnings as validation failures.",
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"Error: Directory '{args.path}' not found.")
        sys.exit(1)

    # Load Config
    project_root = os.getcwd() 
    config = skill_utils.load_config(project_root)

    success = validate_skill(
        args.path,
        config,
        strict_exec_policy=args.strict_exec_policy,
    )
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
