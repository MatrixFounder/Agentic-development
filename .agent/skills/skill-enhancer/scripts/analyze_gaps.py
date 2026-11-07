#!/usr/bin/env python3
import os
import argparse
import sys
import re
import json
import subprocess

# Add script directory to path to import skill_utils
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
try:
    import skill_utils
    from skill_utils import install_human_channel
except ImportError:
    # Fail gracefully if utils missing (should be there due to copy). `print`,
    # not `say`: this is the branch where skill_utils -- and therefore `say`
    # itself -- did not import. The message is ASCII, so no codec can reject it.
    print("Error: skill_utils.py not found. Please ensure it is in the scripts directory.")
    sys.exit(1)

def extract_frontmatter(file_path):
    """Split SKILL.md into (frontmatter, body, error, body_offset).

    `body_offset` is how many file lines precede the body, so a rule that finds
    something on body line N reports `N + body_offset` -- the line the reader
    opens the file at. Without it every reported line number is short by the
    length of the frontmatter, and a finding whose location does not resolve is
    a finding the reader stops checking.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        lines = content.splitlines()
        if not lines or lines[0].strip() != '---':
            return None, content, "Missing YAML frontmatter start (---)", 0

        frontmatter_lines = []
        body_lines = []
        found_end = False
        body_offset = 0

        for i, line in enumerate(lines[1:], 1):
            if not found_end:
                if line.strip() == '---':
                    found_end = True
                    body_offset = i + 1  # opening '---' + frontmatter + closing '---'
                    continue
                frontmatter_lines.append(line)
            else:
                body_lines.append(line)

        if not found_end:
            return None, content, "Missing YAML frontmatter end (---)", 0

        return "\n".join(frontmatter_lines), "\n".join(body_lines), None, body_offset

    except Exception as e:
        return None, "", f"File Error: {str(e)}", 0


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


def _has_real_files(directory: str) -> bool:
    if not os.path.isdir(directory):
        return False
    for item in os.listdir(directory):
        if item in [".DS_Store", ".keep"] or item.startswith("."):
            continue
        return True
    return False

# ---------------------------------------------------------------------------
# Rule scoping (WI-033)
#
# Three rules -- weak wording, template placeholders, absolute paths -- used to
# fire on documentation that is correct as written: CLI usage notation, a
# reproducible command line, a markdown escape. A report whose findings describe
# correct content carries no information, and the habit it teaches is to stop
# reading it. Each rule below states what it targets and what it deliberately
# leaves alone; `tests/test_rule_scoping.py` pins both halves.
# ---------------------------------------------------------------------------

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


# A quoted span never crosses a line. Without the `\n` exclusion, one ordinary
# apostrophe -- "Don't skip the review step." -- opens a span that runs to the
# next apostrophe several lines later and blanks everything between. Measured
# over this repo before the fix: 14.6% of body lines went blank, and a fixture
# holding both `[Why this is wrong]` and `TODO: finish this section` reported
# neither. The unscoped pattern is the one HEAD used for the TODO check, where
# it had the same hole; it became load-bearing when the placeholder rule started
# reading the stripped body too.
_QUOTED_RE = re.compile(r'"[^"\n]*"|\'[^\'\n]*\'')


def strip_quoted(text: str) -> str:
    """Blank quoted spans, preserving length and line structure.

    Red Flags quote the agent's excuse verbatim ("I can just read the files
    manually"); the quote is the specimen, not the skill's own wording.
    """
    return _QUOTED_RE.sub(lambda m: " " * len(m.group(0)), text)


# Absolute paths whose first segment names one machine or one user's account.
# `/tmp`, `/dev/null`, `/usr/...` are portable and are how a reproducible command
# in Validation Evidence is written; `/Users/alice/...` only resolves on the
# machine that wrote it. (`/tmp` is still absent on Windows -- that portability
# question is WI-032, not this check.) `srv` and `export` are here because the
# FHS defines them as data served BY THIS HOST.
_MACHINE_PATH_ROOTS = {
    "users", "home", "volumes", "mnt", "media", "root", "srv", "export",
    "cygdrive",
}


def is_machine_specific_path(hit: str) -> bool:
    """True when an absolute path names one machine or one user's account.

    Stated false negative: this is a denylist on the FIRST segment, so a
    machine-specific path rooted anywhere else stays silent -- measured
    examples are `/opt/homebrew/bin/soffice`,
    `/Applications/LibreOffice.app/Contents/MacOS/soffice`,
    `/var/folders/xy/.../T/build.pdf` and `/private/tmp/<session-uuid>/out.pdf`.
    An allowlist (fire on every root not known to be portable) would catch those
    and would also fire on `/scratch/...` and `/data/...` in ordinary prose. The
    denylist is the side that keeps the report readable; the cost is written down
    here rather than discovered.
    """
    segments = [seg for seg in hit.split("/") if seg]
    return bool(segments) and segments[0].lower() in _MACHINE_PATH_ROOTS


# A Windows path is a drive letter, a UNC share, or at least three
# backslash-separated segments. One backslash between two word characters is a
# markdown escape (`x\_1`), a LaTeX delimiter (`\(...\)`) or a C escape
# (`1.1.0\n`) far more often than it is a path.
# A relative Windows path is only distinguishable from a run of chained escapes
# by its filename: `\alpha\beta\gamma` is LaTeX, `.\scripts\run.bat` is a path.
# So the third alternative requires the last segment to carry an extension.
# Stated cost: an extension-less relative path (`x\y\z`) is not reported.
_WINDOWS_PATH_RE = re.compile(
    r"(?:[A-Za-z]:\\[^\s`\"\']+"
    r"|\\\\[A-Za-z0-9_.\-]+\\[^\s`\"\']+"
    r"|[%~.\w\-]+\\[%~.\w\-]+(?:\\[%~.\w\-]+)*\\?[\w\-]+\.[A-Za-z0-9]{1,6}\b)"
)

# `[--flag VALUE]` is CLI usage notation, `[^fn-1]` a pandoc footnote marker.
# Neither is an unfilled template slot.
_PLACEHOLDER_NOTATION_RE = re.compile(r"^\s*[-^]")

# An unfilled slot is prose the author meant to replace -- `[Why this is wrong]`,
# `[YOUR NAME]` -- so it always carries a word. A bracket span with no letter in
# it is data: a confidence interval (`[0.028, 0.195]`), a coordinate pair, a
# numeric range. Measured: the two intervals in `text-humanizer/SKILL.md` were
# the whole reason that skill failed this gate while `validate_skill.py` passed
# it (WI-033's exact shape). Stated cost: a slot written with no letters at all
# -- `[...]`, `[1]` -- is not reported; both are already below the length and
# space floors the rule applies anyway.
_PLACEHOLDER_HAS_WORD_RE = re.compile(r"[^\W\d_]")

# A TODO marker is a note to self: `TODO:` / `TODO(owner)` anywhere, or a line
# whose content STARTS with TODO once list, quote, heading and comment markers
# are stripped -- `- TODO fix the examples`, `<!-- TODO write this -->`.
# `TODO` in the middle of a sentence is prose describing something else's output
# ("a content slide with TODO placeholder", "titles + TODO bullets").
#
# The earlier `\bTODO\b(?!\s+[a-z])` did not implement that: `re.IGNORECASE`
# reaches into the lookahead's character class, so ANY following word killed the
# match and `- TODO fix the examples` went unreported.
_TODO_COLON_RE = re.compile(r"\bTODO\s*[:(]", re.IGNORECASE)
_LINE_MARKER_RE = re.compile(r"^\s*(?:[-*+>]\s*|#{1,6}\s*|\d+[.)]\s*|<!--\s*)*")


def has_todo_marker(text: str) -> bool:
    """True when `text` carries an unfinished-work marker."""
    if _TODO_COLON_RE.search(text):
        return True
    for line in text.splitlines():
        if _LINE_MARKER_RE.sub("", line).upper().startswith("TODO"):
            return True
    return False

# `can't` / `cannot` states an impossibility and `should-trigger` is a compound
# noun; neither is a weak instruction.
_WEAK_WORD_SUFFIX_SKIP = "-'"


def _is_git_ignored(path: str) -> bool:
    """True when git is present and deliberately ignoring `path`.

    A gitignored scratch directory is not part of the skill -- it is not
    committed and it is not in a packaged `.skill` archive -- so reporting it as
    a structure deviation is reporting the developer's working copy.

    The caller must also check that the SKILL directory itself is not ignored.
    `git check-ignore` answers yes for anything under an ignored parent, so a
    skill living under an ignored path (this repo ignores `/.agent/skills/*`)
    would otherwise have every structure finding silently dropped.
    """
    try:
        # capture_output keeps git's own diagnostics ("not a git repository")
        # off this tool's stderr, which is a contract channel. `encoding=` is
        # mandatory with it: text mode without a named codec decodes the CHILD
        # with the PARENT's locale codec under a strict handler, and a repo
        # path with non-ASCII in it then raises UnicodeDecodeError from inside
        # subprocess.communicate. See
        # docs/issues/subprocess-text-decode-locale-class.md.
        completed = subprocess.run(
            ["git", "check-ignore", "-q", "--", path],
            cwd=os.path.dirname(os.path.abspath(path)) or ".",
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0


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

def analyze_skill(skill_path, config, json_output=False, strict=False):
    """
    Analyzes a skill directory for gaps against the Standards.
    """
    skill_name = os.path.basename(os.path.normpath(skill_path))
    if not json_output:
        print(f"Analyzing '{skill_name}' at {skill_path}...")
    
    validation_config = config.get('validation', {})
    quality_config = validation_config.get('quality_checks', {})
    
    # `gaps` block the gate; `advisories` are reported and do not. The split
    # mirrors validate_skill.py, which already passes a skill that has only
    # warnings -- without it the two gates disagree about the same file, which
    # is the defect WI-033 was filed for. `--strict` folds advisories back in.
    gaps = []
    advisories = []

    # 1. Check SKILL.md existence
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        msg = f"CRITICAL: Missing SKILL.md in {skill_path}"
        if json_output:
            skill_utils.emit_json({"gaps": [msg], "advisories": [],
                                   "status": "critical"})
            sys.exit(1)
        print(msg)
        return
        
    fm_str, body, err, body_offset = extract_frontmatter(skill_md_path)
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
    # Prose rules read `masked_body`; code is not prose (see mask_code).
    masked_body = mask_code(body)

    # 2. Check CSO (Description)
    if 'description' in meta:
        desc = meta['description']
        # `enforce_cso_prefix` is honoured here for the same reason
        # validate_skill.py honours it: a project that has turned the prefix rule
        # off has turned it off for both gates, or the two disagree about one file.
        allowed_prefixes = validation_config.get('allowed_cso_prefixes', ["Use when"])
        # Handle multi-line descriptions by replacing newlines with spaces for prefix matching
        desc_lower_meta = " ".join(desc.split()).lower()
        if validation_config.get('enforce_cso_prefix', True):
            if not any(desc_lower_meta.startswith(prefix.lower()) for prefix in allowed_prefixes):
                gaps.append(f"[CSO] Description should start with one of {allowed_prefixes}")
        
        max_words = quality_config.get('max_description_words', 50)
        if len(desc.split()) > max_words:
             gaps.append(f"[CSO] Description too long ({len(desc.split())} words). Target < {max_words}.")
    else:
        gaps.append("[Critical] Missing 'description' in frontmatter")

    # 3. Check Required Sections (Configurable)
    # Advisory, at the same tier validate_skill.py reports it. These sections
    # are a house convention rather than a structural requirement: a skill may
    # carry the same material under another heading, and 45 skills across the
    # two sibling repositories legitimately do not carry it at all.
    req_sections = validation_config.get('required_sections', [])
    for sec in req_sections:
        if sec.lower() not in body_lower:
            advisories.append(f"[Resilience] Missing '{sec}' section")

    # 3.5 Execution Policy Checks (warning-first migration path)
    #
    # Shared with validate_skill.py, byte for byte: the same four sections, the
    # same prompt-first exemption, the same triggers. The two gates disagreeing
    # about this rule class is 31 of the 97 findings WI-033 measured.
    advisories.extend(
        f"[Execution Policy] {msg}" for msg in
        collect_execution_policy_findings(skill_path, body, validation_config)
    )

    # 4. Check Deep Logic (Language Review — Graduated Approach)
    passive_keywords = quality_config.get('banned_words', ["should"])
    
    # The rule targets a weak INSTRUCTION ("the script should be bundled"). It is
    # scoped away from four things that are not instructions at all: code (a
    # documented command line), a quoted agent excuse in Red Flags, a question in
    # an interview script, and a hyphenated compound or negation (`should-trigger`,
    # `can't`). What survives is a judgement call per instruction, which is why
    # [Language] is advisory rather than blocking -- the graduated-wording policy
    # is a separate pass (WI-033, Out of scope).
    body_lines = body.splitlines()
    masked_lines = masked_body.splitlines()
    deep_logic_gaps = []

    for i, line in enumerate(masked_lines, 1):
        stripped = line.strip()

        # Skip Markdown tables
        if stripped.startswith("|"):
            continue
        # A question asks; it does not instruct.
        if stripped.endswith("?"):
            continue

        line_clean = strip_quoted(line).lower()

        found = []
        for w in passive_keywords:
            for match in re.finditer(r'\b' + re.escape(w) + r'\b', line_clean):
                start, end = match.span()
                if start > 0 and line_clean[start - 1] == '-':
                    continue  # ...-should / mid-compound
                if end < len(line_clean) and line_clean[end] in _WEAK_WORD_SUFFIX_SKIP:
                    continue  # should-trigger, can't
                found.append(w)
        if found:
            found = sorted(set(found), key=passive_keywords.index)
            raw = body_lines[i - 1].strip()
            snippet = raw[:60] + "..." if len(raw) > 60 else raw
            deep_logic_gaps.append(
                f"Line {i + body_offset}: Found {found} -> \"{snippet}\"")

    if deep_logic_gaps:
        advisories.append(f"[Language] Weak wording found. Apply graduated fix (MUST + why for safety, explain-why + imperative for behavioral):\n    " + "\n    ".join(deep_logic_gaps[:5]))
        if len(deep_logic_gaps) > 5:
            advisories.append(f"    ... and {len(deep_logic_gaps) - 5} more.")

    # 5. Lazy TODO / Placeholder checks
    #
    # Both run on the masked body: inside code, `[--layout]` is CLI usage notation
    # and `obsidian tasks todo` is a subcommand name. Neither is unfinished work.
    body_clean = strip_quoted(mask_code(body))
    if has_todo_marker(body_clean):
        gaps.append("[Lazy] Found 'TODO' marker. Finish the skill.")

    # Detect an unfilled template slot -- [Instruction], [Why this is wrong].
    # Markdown links are [text](url), so a `(` immediately after the bracket
    # disqualifies. Three shapes are notation or data rather than a slot and are
    # exempt: `[--flag VALUE]` (an optional CLI argument), `[^fn-1]` (a pandoc
    # footnote marker) and a letterless span such as `[0.028, 0.195]` (a
    # confidence interval).
    placeholders = re.findall(r'\[([^\]\n\"\'\{\}\\]+)\](?!\()', body_clean)
    real_placeholders = [
        p for p in placeholders
        if len(p) > 3 and " " in p and not _PLACEHOLDER_NOTATION_RE.match(p)
        and _PLACEHOLDER_HAS_WORD_RE.search(p)
    ]

    if real_placeholders:
        gaps.append(f"[Lazy] Found {len(real_placeholders)} bracket placeholders (e.g., '[{real_placeholders[0]}]'). Fill them in.")

    # 5.5 Check Directory Structure Deviations
    allowed_dirs = ["scripts", "examples", "assets", "references", "config", "agents", "evals", "eval-viewer", "data"]
    for item in os.listdir(skill_path):
        item_path = os.path.join(skill_path, item)
        if os.path.isdir(item_path):
            if item == "resources":
                 gaps.append("[Structure] Found deprecated 'resources/' directory. Migrate contents to 'assets/' (output) or 'references/' (knowledge).")
            elif item not in allowed_dirs and not item.startswith("."):
                 # Advisory, because validate_skill.py reports the same thing as
                 # a warning and passes. Blocking here made the two gates
                 # disagree about `skills/html` whenever `git` was off PATH,
                 # since the exemption below then could not fire.
                 if not _is_git_ignored(skill_path) and _is_git_ignored(item_path):
                     continue  # a scratch directory the repo already excludes
                 advisories.append(f"[Structure] Non-standard directory '{item}'. Known directories: {allowed_dirs}")

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

    # 7. Check Token Efficiency (Inline Blocks) — shared two-tier policy
    warn_lines = quality_config.get('max_inline_lines_warn', 20)
    fail_lines = quality_config.get('max_inline_lines_fail', 60)
    exempt_fence = validation_config.get('inline_exempt_fence_langs', ['mermaid'])
    softcheck_fence = validation_config.get(
        'inline_softcheck_fence_langs', ['text', 'console', 'output'],
    )
    # `inline_exempt_skills` is honoured here for the same reason
    # validate_skill.py honours it -- an allowlisted skill must be allowlisted in
    # both gates or they disagree about the same file.
    inline_exempt_skills = set(validation_config.get('inline_exempt_skills', []))
    if skill_name in inline_exempt_skills:
        eff_errors, eff_warnings = [], []
    else:
        # The whole file, not the body: this shared check reports the line it
        # found the fence on, and every other finding in this report is
        # file-relative. validate_skill.py passes the raw content for the same
        # reason. A report that mixes two conventions is a report nobody trusts.
        with open(skill_md_path, 'r', encoding='utf-8', errors='replace') as fh:
            raw_content = fh.read()
        eff_errors, eff_warnings = check_inline_efficiency(
            raw_content, warn_lines, fail_lines, exempt_fence, softcheck_fence,
        )
    for msg in eff_errors:
        gaps.append(f"[Token Efficiency] {msg}")
    for msg in eff_warnings:
        # validate_skill.py reports the warn tier as a warning and still passes.
        advisories.append(f"[Token Efficiency] (minor) {msg}")

    # 7a. Validation Evidence size — advisory in both gates.
    for msg in check_validation_evidence_size(body, validation_config):
        advisories.append(f"[Execution Policy] {msg}")

    # 7b. Anti-Pattern line checks
    #
    # Both are scoped to what actually breaks on another machine. A reproducible
    # command in Validation Evidence writes `/tmp/invoice.pdf` and a shell
    # redirect writes `/dev/null`; neither is a defect, and rewriting them
    # relative would make the documented command wrong.
    for i, line in enumerate(body_lines):
        line = line.strip()
        win_match = _WINDOWS_PATH_RE.search(line)
        if win_match:
             gaps.append(f"[Anti-Pattern] Windows-style path '{win_match.group(0)}' at line {i + 1 + body_offset}. Use forward slashes.")

        # finditer, not search: a documented command routinely names two paths
        # (`pdf_merge.py /tmp/out.pdf /Users/alice/in.pdf`) and reporting only
        # the first hides the second. 16 lines in this repo carry more than one.
        # There is no `"://" not in line` guard: the extraction pattern requires
        # the path to start at a line start or after whitespace/quote/bracket, so
        # it never matches inside a URL -- while the guard did suppress a real
        # machine path on any line that merely mentioned one.
        seen_on_line = set()
        for abs_match in re.finditer(r'(?:^|[\s`"\'(\[])(/[\w\-\.]+(?:/[\w\-\.]+)+)', line):
            hit = abs_match.group(1)
            if hit in seen_on_line or not is_machine_specific_path(hit):
                continue
            seen_on_line.add(hit)
            gaps.append(f"[Anti-Pattern] Machine-specific absolute path '{hit}' at line {i + 1 + body_offset}. It resolves only on the machine that wrote it -- use a relative path or a portable scratch path.")

    # 8. POV Check
    if 'description' in meta:
        desc = meta['description'].lower()
        if "i can" in desc or "i help" in desc or "my job" in desc or "you can" in desc:
             gaps.append("[CSO] Description uses First/Second Person POV. Use Third Person.")

    # 9. Naming Convention (Soft Check)
    if "helper" in skill_name or "utils" in skill_name:
        gaps.append(f"[Naming] Avoid vague names like '{skill_name}'. Use specific action-oriented names.")

    # Report
    #
    # Exit code is decided by `gaps` alone. `advisories` are printed either way:
    # they name work that is real but is not this gate's to block on -- the
    # graduated-wording policy and the warning-first execution-policy migration.
    # `--strict` promotes them, which is the mode a migration sprint runs in.
    blocking = gaps + advisories if strict else gaps
    if json_output:
        result = {
            "skill": skill_name,
            "gaps": gaps,
            "advisories": advisories,
            "status": "failed" if blocking else "passed"
        }
        skill_utils.emit_json(result)
        sys.exit(1 if blocking else 0)
    else:
        if gaps:
            print(f"⚠️  Gaps Detected for '{skill_name}':")
            for gap in gaps:
                print(f"  - {gap}")
        if advisories:
            label = "promoted by --strict" if strict else "do not fail the gate"
            print(f"ℹ️  Advisories for '{skill_name}' ({label}):")
            for advisory in advisories:
                print(f"  - {advisory}")
        if blocking:
            print("\nRecommendation: Run 'Execute Improvement Plan' to fix these gaps.")
            sys.exit(1)
        if advisories:
            print(f"\n✅ No blocking gaps for '{skill_name}'; "
                  f"{len(advisories)} advisory item(s) above.")
        else:
            print(f"✅ No Gaps Found for '{skill_name}'. Skill is compliant.")
        sys.exit(0)

def main():
    install_human_channel()
    parser = argparse.ArgumentParser(description="Analyze a skill for Standard compliance gaps.")
    parser.add_argument("path", help="Path to the skill directory.")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat advisories (Language, Execution Policy, minor Token "
             "Efficiency) as blocking gaps.",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: Directory '{args.path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Load Config
    project_root = os.getcwd()
    config = skill_utils.load_config(project_root)

    analyze_skill(args.path, config, json_output=args.json, strict=args.strict)

if __name__ == "__main__":
    main()
