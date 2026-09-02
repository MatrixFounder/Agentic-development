#!/usr/bin/env python3
import os
import argparse
import sys
import re

# Add script directory to path to import skill_utils
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
import skill_utils
from skill_utils import install_human_channel

def check_inline_efficiency(content, warn_lines=20, fail_lines=60,
                            exempt_fence_langs=None, softcheck_fence_langs=None):
    """Two-tier inline code-block size check.

    Returns (errors, warnings). A fenced block longer than fail_lines yields an
    error; longer than warn_lines yields a warning. Fences tagged with a
    language in exempt_fence_langs (e.g. mermaid diagrams) are skipped entirely;
    fences in softcheck_fence_langs (e.g. text output samples) can only warn,
    never fail. An unclosed fence is reported as an error.

    Shared logic — this function is duplicated verbatim in
    skill-creator/scripts/validate_skill.py and skill-enhancer/scripts/analyze_gaps.py;
    tests/test_shared_gate_logic.py asserts the two copies stay byte-identical.
    """
    if exempt_fence_langs is None:
        exempt_fence_langs = ["mermaid"]
    if softcheck_fence_langs is None:
        softcheck_fence_langs = ["text", "console", "output"]
    exempt = {str(x).lower() for x in exempt_fence_langs}
    softcheck = {str(x).lower() for x in softcheck_fence_langs}
    warn_lines = int(warn_lines)
    fail_lines = int(fail_lines)

    errors = []
    warnings = []
    lines = content.splitlines()
    in_block = False
    block_start = 0
    block_lang = ""

    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line.startswith("```"):
            continue
        if in_block:
            block_length = i - block_start - 1
            if block_lang not in exempt:
                is_soft = block_lang in softcheck
                if block_length > fail_lines and not is_soft:
                    errors.append(
                        f"Inline code block at line {block_start + 1} is too large "
                        f"({block_length} lines, max {fail_lines}). If this is core "
                        f"procedural content, split it into labelled sub-blocks; if "
                        f"it is reference material, extract it to references/ or assets/."
                    )
                elif block_length > warn_lines:
                    warnings.append(
                        f"Inline code block at line {block_start + 1} is large "
                        f"({block_length} lines, warn threshold {warn_lines}). "
                        f"Consider splitting it or extracting to references/."
                    )
            in_block = False
        else:
            in_block = True
            block_start = i
            info = line[3:].strip()
            block_lang = info.split()[0].lower() if info else ""

    if in_block:
        errors.append(
            f"Unclosed code fence: ``` opened at line {block_start + 1} is never "
            f"closed. Add the matching closing fence."
        )
    return errors, warnings

_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
_INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)*?\1")


def mask_code(body: str) -> str:
    """Blank every fenced block and inline code span, keeping lines and columns.

    The prose rules read English. A documented command line is not English:
    `[--page-size letter|a4|legal]` is CLI usage notation where the brackets mean
    "optional argument", and filling it in would make every documented command
    wrong. Masking with spaces (rather than deleting) keeps every line number and
    column valid, so a finding still points at the right place.

    Deliberately NOT used by the absolute-path check: a machine-specific path
    hardcoded inside a command example is exactly the defect that check exists
    for, so that one narrows on what the path names instead (see
    `is_machine_specific_path`).
    """
    lines = body.splitlines()

    # Which lines belong to a CLOSED fence. An unclosed one is deliberately not
    # masked: masking it would blank every following line, and a rule that sees
    # nothing reports nothing. A false positive inside an unterminated fence is
    # visible and fixable; the silence is neither. `check_inline_efficiency`
    # reports the unclosed fence itself.
    fenced = set()
    fence = None
    start = 0
    for i, raw in enumerate(lines):
        match = _FENCE_RE.match(raw)
        if fence is None:
            if match:
                fence, start = match.group(1), i
            continue
        if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
            fenced.update(range(start, i + 1))
            fence = None

    out = []
    for i, raw in enumerate(lines):
        if i in fenced:
            out.append(" " * len(raw))
        else:
            out.append(_INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), raw))
    return "\n".join(out)


def extract_frontmatter(file_path):
    """
    Extracts frontmatter string from file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
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

_PLAIN_SCALAR_RE = re.compile(r'^(?P<key>[A-Za-z0-9_.-]+):[ \t]+(?P<value>[^\s"\'#|>&*!\[{].*)$')


def _heuristic_unquoted_colon_warnings(frontmatter):
    """Stdlib-only floor for the strict-YAML check: flag plain scalars holding ': '."""
    warnings = []
    # +2: line 1 of the file is the opening '---', so frontmatter line 1 is file line 2.
    for offset, line in enumerate(frontmatter.splitlines(), start=2):
        match = _PLAIN_SCALAR_RE.match(line)
        if match and ": " in match.group("value"):
            warnings.append(
                f"Frontmatter line {offset}: '{match.group('key')}' is an unquoted scalar "
                "containing ': ' — strict YAML parsers reject it. Quote the value. "
                "(Install PyYAML for an exact check instead of this heuristic.)"
            )
    return warnings


def check_frontmatter_strict(frontmatter):
    """Second-opinion strict-YAML check on the frontmatter block. Returns (errors, warnings).

    VanillaYamlParser is lenient — it splits on the first ':' and keeps the remainder as a
    plain scalar — so `description: Use when X: "Y"` validates green here while strict YAML
    1.1/1.2 parsers (Obsidian, VSCode preview, js-yaml, PyYAML) reject the whole block and
    render the skill card as a parse error. PyYAML stays soft-optional: without it the
    heuristic above can only warn, never fail.
    """
    try:
        import yaml
    except ImportError:
        return [], _heuristic_unquoted_colon_warnings(frontmatter)

    try:
        yaml.safe_load(frontmatter)
    except yaml.YAMLError as e:
        detail = " ".join(str(e).split())
        return [
            "Strict YAML Parse Error: frontmatter is rejected by strict YAML parsers, so "
            f"previews (Obsidian/VSCode/js-yaml) render the skill card as an error: {detail}. "
            "Quote any value containing ': ' — e.g. description: \"Use when X: Y\"."
        ], []

    return [], []


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


def _section_body_lines(body: str, title: str) -> list[str]:
    """Non-blank lines under `title`, up to the next heading of any level."""
    needle = _normalize_section_title(title)
    out, inside = [], False
    for line in body.splitlines():
        if re.match(r"^#{1,6}\s", line):
            if inside:
                break
            if _normalize_section_title(re.sub(r"^#{1,6}\s+", "", line)).endswith(needle):
                inside = True
            continue
        if inside and line.strip():
            out.append(line)
    return out


def check_validation_evidence_size(body: str, validation_config: dict) -> list[str]:
    """Validation Evidence records the verdict, not the investigation.

    The bound lives in `skill_standards_default.yaml`
    (`quality_checks.max_validation_evidence_lines`), overridable per project via
    `.agent/rules/skill_standards.yaml`. No literal here: an absent key means the
    standard is not configured, which is not the same as a number this function
    invented. Warning only — a long section is verbose, not invalid. The fix is
    to move detail into `references/` and keep a summary plus a pointer.
    """
    limit = validation_config.get("quality_checks", {}).get(
        "max_validation_evidence_lines")
    if not isinstance(limit, int) or limit <= 0:
        return []
    lines = _section_body_lines(body, "Validation Evidence")
    if len(lines) > limit:
        return [f"Validation Evidence is {len(lines)} lines (soft limit {limit}). "
                f"Keep the verdict and the counts here; move the investigation "
                f"into references/ and link it."]
    return []


def collect_execution_policy_findings(skill_path, body, validation_config):
    """One finding per missing execution-policy section, never two.

    Three sub-rules used to fire on top of the "Missing '<section>'" finding
    rather than instead of it: a populated `scripts/` re-reported the absent
    Script Contract, mutation wording re-reported the absent Safety Boundaries,
    and a `scripts/` mention re-reported the absent Validation Evidence. Each
    fires ONLY when that section is already missing, so each could only ever
    restate a finding already made -- 7 of the 31 occurrences measured across
    this repo on 2026-09-02 were such duplicates. They now name the trigger
    inside the one finding, which is the information they actually carry (WI-034).

    The mutation-marker scan reads the masked body and matches whole words, so
    a `delete` inside a documented command line and the `remove` in "remove AI
    patterns" are no longer the same signal as a skill that deletes files. It is
    still a heuristic over prose -- acceptable now that it only shapes a
    message, where before it produced a finding of its own.

    The Validation Evidence trigger asks whether the skill SHIPS `scripts/`,
    not whether the body contains the substring `scripts/`. The substring test
    fired on `obsidian-cli`, whose only match was a path to another skill's
    script and which ships no `scripts/` at all.
    """
    required_sections = validation_config.get(
        "execution_policy_sections",
        [
            "Execution Mode",
            "Script Contract",
            "Safety Boundaries",
            "Validation Evidence",
        ],
    )
    headings = _collect_markdown_headings(body)
    missing = [s for s in required_sections if not _has_section(headings, s)]
    missing_normalized = {_normalize_section_title(s) for s in missing}

    # Script Contract is optional for prompt-first skills unless scripts/ is populated
    mode_match = re.search(r'\*\*Mode\*\*:\s*`?(prompt-first|script-first|hybrid)`?',
                           body, re.IGNORECASE)
    mode = mode_match.group(1).lower() if mode_match else "unknown"
    scripts_dir = os.path.join(skill_path, "scripts")
    has_scripts = _has_real_files(scripts_dir)

    masked_lower = mask_code(body).lower()
    mutation_markers = (
        "delete", "remove", "overwrite", "rename", "migrate", "truncate",
        "destructive",
    )
    mutation_words = sorted({
        m for m in mutation_markers
        if re.search(r"\b" + m + r"(?:s|d|ed|ing)?\b", masked_lower)
    })

    findings = []
    for section in missing:
        normalized = _normalize_section_title(section)
        trigger = ""
        if normalized == _normalize_section_title("Script Contract"):
            if has_scripts:
                trigger = " — 'scripts/' has executable content"
            elif mode == "prompt-first":
                continue  # prompt-first and nothing to contract for
        elif normalized == _normalize_section_title("Safety Boundaries") and mutation_words:
            trigger = f" — mutation wording found ({', '.join(mutation_words)})"
        elif (normalized == _normalize_section_title("Validation Evidence")
              and has_scripts):
            trigger = " — the skill ships scripts/"
        findings.append(
            f"Missing '{section}' section (warning-first migration target){trigger}."
        )
    return findings


def check_required_sections(body: str, validation_config: dict) -> list[str]:
    """`validation.required_sections` — Red Flags, Rationalization Table.

    **Advisory, not an error, and that is the point.** Read here for the same
    reason `enforce_cso_prefix` is read in `analyze_gaps.py`: a key declared in
    one project config must reach both gates, or the two return different
    verdicts on the same file. But it reaches both at the WARNING tier: these
    sections are a house convention, not a structural requirement, and a skill
    is free to carry its anti-rationalization material under another name or
    not at all.

    Measured 2026-09-02 before that was settled, with the rule blocking: 34 of
    46 skills in `agentic-development` and 11 of 23 in `obsidian-llm-wiki`
    flipped from passing to failing, and the CI gate that runs this validator
    went from 46/46 to 12/46. The rule had never blocked HERE, so promoting it
    made the gate stricter than it had ever been for every consumer — which is
    not what aligning two gates is supposed to mean.

    Substring, not heading, matching — deliberately the same rule the sibling
    gate applies, so the two cannot disagree on a skill that names the section
    in prose. Measured across this repo's 22 skills: substring and heading
    matching agree on every one.
    """
    errors = []
    body_lower = body.lower()
    for section in validation_config.get('required_sections', []):
        if section.lower() not in body_lower:
            errors.append(f"Missing '{section}' section (validation.required_sections)")
    return errors


def validate_skill(skill_path, config, strict_exec_policy=False, json_output=False):
    """
    Validates a single skill directory against configured standards.
    """
    skill_name = os.path.basename(os.path.normpath(skill_path))
    if not json_output:
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
    allowed_dirs = ["scripts", "examples", "assets", "references", "config", "agents", "evals", "eval-viewer", "data"]
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
            strict_errors, strict_warnings = check_frontmatter_strict(fm_content)
            errors.extend(strict_errors)
            warnings.extend(strict_warnings)

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
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                 raw_content = f.read()
            
            warn_lines = quality_config.get('max_inline_lines_warn', 20)
            fail_lines = quality_config.get('max_inline_lines_fail', 60)
            exempt_fence = validation_config.get('inline_exempt_fence_langs', ['mermaid'])
            softcheck_fence = validation_config.get(
                'inline_softcheck_fence_langs', ['text', 'console', 'output'],
            )
            inline_exempt_skills = set(validation_config.get('inline_exempt_skills', []))
            if skill_name not in inline_exempt_skills:
                eff_errors, eff_warnings = check_inline_efficiency(
                    raw_content, warn_lines, fail_lines, exempt_fence, softcheck_fence,
                )
                errors.extend(eff_errors)
                warnings.extend(eff_warnings)

            body_content = extract_body_content(skill_md_path)
            warnings.extend(check_required_sections(body_content, validation_config))
            warnings.extend(
                f"Execution Policy: {msg}" for msg in
                collect_execution_policy_findings(
                    skill_path, body_content, validation_config)
            )
            warnings.extend(
                check_validation_evidence_size(body_content, validation_config)
            )

    # Report
    #
    # `--json` carries the same two-list envelope as
    # `skill-enhancer/scripts/analyze_gaps.py --json`, under this gate's own
    # names: `errors` is that tool's `gaps` and `warnings` is its `advisories`.
    # A caller gating on one can gate on the other without a second parser.
    blocking = errors + warnings if strict_exec_policy else errors
    if json_output:
        skill_utils.emit_json({
            "skill": skill_name,
            "errors": errors,
            "warnings": warnings,
            "status": "failed" if blocking else "passed",
        })
        return not blocking

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
    install_human_channel()
    parser = argparse.ArgumentParser(description="Validate an Agent Skill (Portable Standard).")
    parser.add_argument("path", help="Path to the skill directory")
    parser.add_argument(
        "--strict-exec-policy",
        "--strict",
        dest="strict_exec_policy",
        action="store_true",
        help="Treat warnings as validation failures. `--strict` is the spelling "
             "shared with analyze_gaps.py; `--strict-exec-policy` is kept because "
             "callers and CI already use it.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the verdict as JSON: {skill, errors, warnings, status}.",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: Directory '{args.path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Load Config
    project_root = os.getcwd()
    config = skill_utils.load_config(project_root)

    success = validate_skill(
        args.path,
        config,
        strict_exec_policy=args.strict_exec_policy,
        json_output=args.json,
    )
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
