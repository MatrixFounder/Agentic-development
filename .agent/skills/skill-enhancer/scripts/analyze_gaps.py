#!/usr/bin/env python3
import os
import argparse
import sys
import re

# Add script directory to path to import skill_utils
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
try:
    import skill_utils
except ImportError:
    # Fail gracefully if utils missing (should be there due to copy)
    print("Error: skill_utils.py not found. Please ensure it is in the scripts directory.")
    sys.exit(1)

def extract_frontmatter(file_path):
    """
    Extracts frontmatter string and body from file.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        lines = content.splitlines()
        if not lines or lines[0].strip() != '---':
            return None, content, "Missing YAML frontmatter start (---)"

        frontmatter_lines = []
        body_lines = []
        found_end = False
        
        for i, line in enumerate(lines[1:], 1):
            if not found_end:
                if line.strip() == '---':
                    found_end = True
                    continue
                frontmatter_lines.append(line)
            else:
                body_lines.append(line)

        if not found_end:
            return None, content, "Missing YAML frontmatter end (---)"

        return "\n".join(frontmatter_lines), "\n".join(body_lines), None

    except Exception as e:
        return None, "", f"File Error: {str(e)}"

def analyze_skill(skill_path, config):
    """
    Analyzes a skill directory for gaps against the Standards.
    """
    skill_name = os.path.basename(os.path.normpath(skill_path))
    print(f"Analyzing '{skill_name}' at {skill_path}...")
    
    validation_config = config.get('validation', {})
    quality_config = validation_config.get('quality_checks', {})
    
    gaps = []
    
    # 1. Check SKILL.md existence
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        print(f"CRITICAL: Missing SKILL.md in {skill_path}")
        return
        
    fm_str, body, err = extract_frontmatter(skill_md_path)
    if err:
        gaps.append(f"[Structure] {err}")
        meta = {}
    else:
        parser = skill_utils.VanillaYamlParser()
        try:
            meta = parser.parse(fm_str)
        except Exception as e:
            gaps.append(f"[Structure] YAML Parse Error: {e}")
            meta = {}

    body_lower = body.lower()

    # 2. Check CSO (Description)
    if 'description' in meta:
        desc = meta['description']
        # Configurable Prefixes
        allowed_prefixes = validation_config.get('allowed_cso_prefixes', ["Use when"])
        desc_lower_meta = desc.lower().strip()
        if not any(desc_lower_meta.startswith(prefix.lower()) for prefix in allowed_prefixes):
            gaps.append(f"[CSO] Description should start with one of {allowed_prefixes}")
        
        max_words = quality_config.get('max_description_words', 50)
        if len(desc.split()) > max_words:
             gaps.append(f"[CSO] Description too long ({len(desc.split())} words). Target < {max_words}.")
    else:
        gaps.append("[Critical] Missing 'description' in frontmatter")

    # 3. Check Required Sections (Configurable)
    req_sections = validation_config.get('required_sections', [])
    for sec in req_sections:
        if sec.lower() not in body_lower:
            gaps.append(f"[Resilience] Missing '{sec}' section")

    # 4. Check Deep Logic (Passive Voice)
    passive_keywords = quality_config.get('banned_words', ["should"])
    
    # Analyze line by line
    body_lines = body.splitlines()
    deep_logic_gaps = []
    
    for i, line in enumerate(body_lines, 1):
        line_lower = line.lower()
        
        # Skip Markdown tables
        if line.strip().startswith("|"):
            continue

        # Strip quoted strings
        line_clean = re.sub(r'("[^"]*"|\'[^\']*\')', '', line_lower)

        found = [w for w in passive_keywords if re.search(r'\b' + re.escape(w) + r'\b', line_clean)]
        if found:
            snippet = line.strip()[:60] + "..." if len(line.strip()) > 60 else line.strip()
            deep_logic_gaps.append(f"Line {i}: Found {found} -> \"{snippet}\"")
            
    if deep_logic_gaps:
        gaps.append(f"[Deep Logic] Passive wording found. Rewrite to Imperative:\n    " + "\n    ".join(deep_logic_gaps[:5]))
        if len(deep_logic_gaps) > 5:
            gaps.append(f"    ... and {len(deep_logic_gaps) - 5} more.")

    # 5. Lazy TODO / Placeholder checks
    body_clean = re.sub(r'("[^"]*"|\'[^\']*\')', '', body_lower)
    if "todo" in body_clean:
        gaps.append("[Lazy] Found 'TODO' placeholder. Finish the skill.")
    
    # Check for template placeholders like [Instruction] or [Why this is wrong]
    # Simple heuristic: Look for [text] where text is > 2 chars and has spaces? 
    # Or just generic [ ] patterns that look like template artifacts.
    # We avoid matching markdown links [text](url) by stripping them first or being careful.
    # Markdown links are [text](url). If we see [text] followed by (, it's a link.
    # If we see [text] NOT followed by (, it's likely a placeholder.
    
    # Detect [Placeholder] 
    # Regex: \[ ([^\]]+) \] (?! \()
    placeholders = re.findall(r'\[([^\]]+)\](?!\()', body)
    # Filter out common false positives like " " (checkboxes) or single chars
    real_placeholders = [p for p in placeholders if len(p) > 3 and " " in p]
    
    if real_placeholders:
        gaps.append(f"[Lazy] Found {len(real_placeholders)} bracket placeholders (e.g., '[{real_placeholders[0]}]'). Fill them in.")

    # 6. Check Examples Content
    examples_dir = os.path.join(skill_path, "examples")
    if not os.path.isdir(examples_dir) or not os.listdir(examples_dir):
        gaps.append("[Richness] Missing or empty 'examples/' directory")
    else:
        for f in os.listdir(examples_dir):
            if f.startswith("."): continue
            fp = os.path.join(examples_dir, f)
            if os.path.getsize(fp) < 10:
                gaps.append(f"[Richness] Example '{f}' is too small/empty. Real examples required.")

    # 7. Check Token Efficiency (Inline Blocks)
    in_block = False
    block_start = 0
    max_inline = quality_config.get('max_inline_lines', 12)
    
    for i, line in enumerate(body_lines):
        line = line.strip()
        if line.startswith("```"):
            if in_block:
                block_length = i - block_start - 1
                if block_length > max_inline:
                    gaps.append(f"[Token Efficiency] Inline code block at line {block_start + 1} is too large ({block_length} lines). Max allowed is {max_inline}.")
                in_block = False
            else:
                in_block = True
                block_start = i

        # Anti-Patterns Checks
        if re.search(r'[a-zA-Z0-9_\-]+\\[a-zA-Z0-9_\-]+', line):
             gaps.append(f"[Anti-Pattern] Potential Windows-style path at line {i+1}. Use forward slashes.")

        abs_match = re.search(r'(?:^|[\s`"\'(\[])(/[\w\-\.]+(?:/[\w\-\.]+)+)', line)
        if abs_match:
            hit = abs_match.group(1)
            if "://" not in line: 
                gaps.append(f"[Anti-Pattern] Potential Absolute Path '{hit}' at line {i+1}. Use relative paths.")

    # 8. POV Check
    if 'description' in meta:
        desc = meta['description'].lower()
        if "i can" in desc or "i help" in desc or "my job" in desc or "you can" in desc:
             gaps.append("[CSO] Description uses First/Second Person POV. Use Third Person.")

    # 9. Naming Convention (Soft Check)
    if "helper" in skill_name or "utils" in skill_name:
        gaps.append(f"[Naming] Avoid vague names like '{skill_name}'. Use specific action-oriented names.")

    # Report
    if gaps:
        print(f"⚠️  Gaps Detected for '{skill_name}':")
        for gap in gaps:
            print(f"  - {gap}")
        print("\nRecommendation: Run 'Execute Improvement Plan' to fix these gaps.")
        sys.exit(1)
    else:
        print(f"✅ No Gaps Found for '{skill_name}'. Skill is compliant.")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Analyze a skill for Standard compliance gaps.")
    parser.add_argument("path", help="Path to the skill directory")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"Error: Directory '{args.path}' not found.")
        sys.exit(1)
    
    # Load Config
    project_root = os.getcwd() 
    config = skill_utils.load_config(project_root)

    analyze_skill(args.path, config)

if __name__ == "__main__":
    main()
