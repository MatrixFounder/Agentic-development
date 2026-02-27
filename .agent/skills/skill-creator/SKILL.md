---
name: skill-creator
description: Guidelines for creating new Agent Skills following Gold Standard structures. Use when defining new capabilities or upgrading existing skills.
tier: 2
version: 1.3
---
# Skill Creator Guide

This skill provides the authoritative standard for creating new Agent Skills in this project. It combines the [Anthropic Skills Standard](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) with our local architecture rules.

## 1. Anatomy of a Skill

Every skill **MUST** strictly follow this directory structure. This structure is non-negotiable for "Rich Skills".

```
skill-name/
├── SKILL.md (Required)
│   ├── YAML frontmatter (name, description, tier, version)
│   └── Markdown body (instructions)
└── Bundled Resources (Optional)
    ├── examples/      # FEW-SHOT TRAINING: Input/Output pairs to teach the Agent
    ├── assets/        # USER OUTPUT: Templates/Files to be given to User or used in output
    ├── references/    # AGENT KNOWLEDGE: Compendiums, Specs, Guidelines, Schemas
    └── scripts/       # EXECUTABLE LOGIC: Python/Bash tools (if logic > 5 lines). We also bundle eval automation tools here (`validate_skill.py`, `generate_review.py`, etc).
```

> [!WARNING]
> **Prohibited Files:** Do NOT create `README.md`, `CHANGELOG.md`, `INSTALLATION.md`, or other aux docs inside the skill folder. All instructions must be in `SKILL.md`.

## 2. Rich Skill Philosophy (Hybrid Standard)

A "Rich Skill" is comprehensive. We separate files by their **Semantic Purpose** to help the Agent understand *why* it is reading a file.

### `examples/` (The "Train" Data)
*   **Purpose**: Teach the Agent **Behavior**.
*   **Content**: "When user says X, do Y."
*   **Files**: `examples/usage_demo.py`, `examples/complex_scenario.md`.
*   **Rule**: Use these to reduce hallucination on complex flows.

### `assets/` (The "Material" Data)
*   **Purpose**: Provide materials for the **User**.
*   **Content**: "Here is the template you asked for."
*   **Files**: `assets/boilerplate.py`, `assets/logo.svg`, `assets/report_template.md`.
*   **Rule**: The Agent does not "learn" from these; it indiscriminately uses/copies them.

### `references/` (The "Knowledge" Data)
*   **Purpose**: Provide context for the **Agent**.
*   **Content**: "Here are the rules/specs you must follow."
*   **Files**: `references/api_spec.yaml`, `references/design_guidelines.md`.
*   **Rule**: Heavy context that is read only when needed.

### `scripts/` (The "Tool" Data)
*   **Purpose**: **Execute** logic reliably.
*   **Content**: Python scripts for deterministic tasks.

## 3. Script-First Methodology (Opt O6a)

**CRITICAL RULE**: Agents are terrible at executing complex algorithmic logic from text instructions.
If your skill requires logic (loops, conditions, parsing, scanning), you **MUST** write a Python script in `scripts/`.

- **❌ Bad (Text)**: "Go through every file, check if it imports X, then if it does, check Y..."
- **✅ Good (Script)**: "Run `python scripts/scanner.py`. It produces `report.json`."

> [!IMPORTANT]
> **The 5-Line Logic Limit:** If a step in `SKILL.md` requires more than 5 lines of logical "if/then/else" text to explain, **IT MUST BE A SCRIPT**.

## 3.5. Execution Mode
- **Mode**: `hybrid`
- **Rationale**: Skill authoring needs judgement for structure/quality decisions and deterministic scripts for repeatable validation and generation.

## 3.6. Script Contract
- **Primary Commands**:
  - `python3 scripts/init_skill.py <name> --tier <N>`
  - `python3 scripts/validate_skill.py <skill-path>`
- **Inputs**: skill name/path, tier, and local policy config.
- **Outputs**: generated skill skeletons, validation pass/fail output, warnings.
- **Failure Semantics**: non-zero exit code on validation errors.
- **Migration Mode**: execution-policy checks are warning-first by default, strict mode via `--strict-exec-policy`.

## 3.7. Safety Boundaries
- **Scope**: operate only on explicit target skill directories.
- **Default Exclusions**: no broad or implicit repo-wide mutation.
- **Destructive Actions**: never default; require explicit user/task intent.
- **Optional Artifacts**: missing optional resources generate warnings unless policy marks them mandatory.

## 3.8. Validation Evidence
- **Local Evidence**: `validate_skill.py` output and generated diffs.
- **Quality Evidence**: section coverage, CSO checks, inline efficiency, and metadata checks.
- **CI Evidence**: skill-validation jobs consume validator exit semantics for pass/fail gating.

## 4. Frontmatter & Metadata

The YAML frontmatter is CRITICAL for the Orchestrator's loading logic.

- **Frontmatter** (YAML): Contains `name` and `description` fields (required), plus optional fields like `tier`, `version`, `license`, `metadata`, and `compatibility` etc.

```yaml
---
name: skill-my-new-capability
description: "One-line summary of what this skill enables the agent to do."
tier: [0|1|2]
version: 1.0
---
```

### Protocol: Tier Definitions
Run `python3 scripts/init_skill.py --help` to see the available Tiers for your project.
> [!IMPORTANT]
> **DO NOT** attempt to guess tiers or read configuration files manually. The script handles complex merging logic (Defaults + Project Overrides). Always trust the script output.

## 5. Token Efficiency (Global Rule)

To prevent context window saturation, we strictly enforce limits on inline content:

### The 12-Line Rule
*   **PROHIBITED**: Inline code blocks, templates, or examples larger than **12 lines**.
*   **REQUIRED**: Extract large blocks to `examples/`, `assets/`, or `references/` and reference them.
    *   *Bad*: A 20-line JSON object inline.
    *   *Good*: "See `examples/payload.json`."

### Why?
*   Skills are read frequently.
*   Large inline examples multiply token costs.
*   External files are only read when needed.

## 6. Instruction Language: Graduated Approach

Skills must work across different LLMs (Claude, Gemini, Codex, Qwen, Llama, etc.). Use a **graduated approach** to instruction strength — not blind `MUST` everywhere, and not soft suggestions either.

### The Graduated Rule

| Instruction Type | Style | Why |
| :--- | :--- | :--- |
| **Safety-critical** (data loss, destructive ops, security) | `MUST` / `ALWAYS` + **explain why** | Open-source models (Qwen, Llama) need the imperative; frontier models benefit from the rationale |
| **Behavioral** (formatting, style, workflow preferences) | **Explain why** + imperative verb | Frontier models (Claude, Gemini) follow motivated instructions better than bare commands |
| **Prohibited patterns** | `MUST NOT` + consequence | All models need explicit prohibition for dangerous patterns |

**Example — Graduated Style:**
```markdown
# ❌ Only MUST (too rigid, no motivation)
You MUST run the validation script after every edit.

# ❌ Only "explain why" (too soft for open-source models)
Run validation after edits — unvalidated XML often has subtle errors.

# ✅ Graduated (works for all models)
You MUST run validation after every edit — unvalidated XML often has
subtle namespace or encoding errors that look fine in text but silently
corrupt the document when opened.
```

### Weak Language (Still Prohibited)
These words trigger lazy behavior in all models. Replace with graduated alternatives:

| ❌ Weak / Prohibited | ✅ Graduated Replacement |
| :--- | :--- |
| "should", "could" | Strong imperative + reason: "Do X because Y" |
| "try to", "attempt" | "Execute X — failure to do so causes Y" |
| "recommended" | "This is required because…" or "This prevents…" |
| "consider" | "Ensure X — skipping this leads to Y" |
| "if possible" | Remove condition; state the requirement directly |

### Red Flags (Rationalization Management)
Every skill **MUST** include a "Red Flags" section — this prevents the agent from making excuses.

**Example Red Flags:**
- "Stop if you think: 'I can skip the script and just read the file manually.'" -> **WRONG**. Run the script.
- "Stop if you think: 'This is a small change, I don't need tests.'" -> **WRONG**. All changes need verification.
- "Stop if you think: 'The user knows what they're doing, I'll skip the warning.'" -> **WRONG**. Always warn on destructive actions.

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "This skill is too simple for a script" | If logic > 5 lines, text instructions fail 30% of the time. Use a script. |
| "I'll add examples later" | You won't. Do it now. Examples define behavior. |
| "The description is descriptive enough" | No. `Use when` triggers are mechanical. Follow the schema. |

## 7. Claude Search Optimization (CSO)

The `description` frontmatter field is the **single most important line**. It determines if your skill is loaded.

### Allowed Schemas (Validation Rules)
You **MUST** start your description with one of these prefixes:

1.  **Trigger-Based** (Preferred for Tools/Workflows):
    *   `Use when...`
    *   *Example*: "Use when debugging Python race conditions."

2.  **Standards & Guidelines** (Passive Knowledge):
    *   `Guidelines for...`
    *   `Helps with...` (Use sparingly)
    *   `Standards for...`
    *   *Example*: "Standards for Secure Coding and OWASP compliance."

3.  **Definitions**:
    *   `Defines...`
    *   *Example*: "Defines the Architect role and responsibilities."

**Constraint**: Keep descriptions under 50 words. Focus on *symptoms* and *triggers*, not solutions.

### Preventing Under-Triggering ("Pushiness")
LLMs tend to **under-trigger** skills — they skip loading them even when they're relevant. To combat this, make descriptions slightly "pushy":

*   **❌ Passive**: "How to build dashboards for internal data."
*   **✅ Pushy**: "Build dashboards for internal data. Use this skill whenever the user mentions dashboards, data visualization, metrics display, or wants to show any kind of structured data, even if they don't explicitly ask for a 'dashboard.'"

Include edge-case triggers and adjacent domains. Add phrases like "even if the user doesn't explicitly ask for…" to catch implicit intent.

## 8. Writing High-Quality Instructions

Use the **Template** found in `assets/SKILL_TEMPLATE.md` as your starting point.

### Target Audience
Before writing, define who will use this skill. If the audience is broad (non-developers, cross-functional teams), avoid jargon and briefly explain technical terms. If the audience is technical, keep instructions concise — Claude is smart enough to fill gaps.

### Section Guidelines:
1.  **Purpose**: Define the "Why".
2.  **Red Flags**: Immediate "Stop and Rethink" triggers.
3.  **Capabilities**: Bulleted list of what is possible.
4.  **Execution Mode**: Explicitly choose `prompt-first`, `script-first`, or `hybrid`.
5.  **Script Contract**: Required for `script-first` and `hybrid`.
6.  **Safety Boundaries**: Explicit scope, exclusions, and non-default destructive behavior.
7.  **Validation Evidence**: Define objective verification output.
8.  **Instructions**: Imperative, step-by-step algorithms.
9.  **Examples (Few-Shot)**: Input -> Output pairs.
    *   *Reference*: See `examples/SKILL_EXAMPLE_LEGACY_MIGRATOR.md` for a **Gold Standard** example of a rich skill.

## 9. Best Practices (Extended)

### Naming Conventions
- **Gerund Form**: Use `verb-ing-noun` (e.g., `processing-pdfs`, `analyzing-data`).
- **Consistent**: `finding-files` (not `file-finder`).
- **Lowercase**: `my-skill` (not `MySkill`).

### Scripting Standards
- **Solve, Don't Punt**: Scripts must handle errors (try/except), not crash.
- **No Voodoo Constants**: Document why a timeout is 30s.
- **No Windows Paths**: ALWAYS use forward slashes (`/`), even for Windows support.
- **Relativity**: ALWAYS use relative paths.
    - **Local**: `scripts/tool.py` (inside skill)
    - **Global**: `System/scripts/tool_runner.py` (project root)
    - **BANNED**: `<absolute_path>` (Absolute OS paths)

## 10. Advanced Design Patterns
> [!TIP]
> See `references/skill_design_patterns.md` for deep dives on **Degrees of Freedom**, **Progressive Disclosure**, and the **Evaluation-Driven Development**.

### Environment Adaptation
Skills may run in different environments (Claude Code, Gemini CLI, Antigravity, API-only). If your skill depends on specific capabilities (subagents, browser, file system), provide fallback strategies:
- **Needs subagents?** → Describe a sequential alternative
- **Needs browser?** → Provide a static HTML export option
- **Needs specific CLI?** → Document which commands are vendor-specific

## 11. Creation Process

When creating a new skill, you **MUST** strictly follow this sequence:

1.  **Check Duplicates**: Verify in your **Skill Catalog** (the file path defined in `.agent/rules/skill_standards.yaml` under `catalog_file`).
2.  **Initialize**:
    ```bash
    # (From skill-creator directory)
    python3 scripts/init_skill.py my-new-skill --tier 2
    ```
3.  **Populate**:
    *   **MANDATORY**: Edit the auto-generated `SKILL.md` (it already contains the template).
    *   **MANDATORY**: Fill in the "Red Flags" and "Use when..." description.
    *   **MANDATORY**: Fill `Execution Mode`, `Script Contract`, `Safety Boundaries`, and `Validation Evidence`.
    *   **MANDATORY**: If logic > 5 lines, write a `scripts/` tool.
    *   **MANDATORY**: Consult `references/skill_design_patterns.md` and `references/writing_skills_best_practices_anthropic.md` for structural decisions.
4.  **Cleanup**:
    *   **MANDATORY**: Remove unused placeholder files created by the init script.
    *   **Scripts**: If no script is required (logic < 5 lines), delete `scripts/.keep` and the `scripts/` directory.
    *   **Assets**: If no user assets are provided, delete `assets/template.txt` and the `assets/` directory.
    *   **References**: If no external references are needed, delete `references/guidelines.md` and the `references/` directory.
    *   **Examples**: You **MUST** have at least one example. Replace `examples/usage_example.md` with a real one, or if you strictly follow the "Simple Skill" path (no external files), you may delete the directory (Rich Skills require examples).
5.  **Validate**:
    ```bash
    python3 scripts/validate_skill.py ../my-new-skill
    ```
6.  **Register**: Add to your **Skill Catalog** (if configured).
7.  **Iterate (Detect Repeated Work)**:
    *   After testing the skill on 2-3 real prompts, review what the agent actually did.
    *   If the agent wrote the **same helper code** across multiple test runs → extract it into `scripts/`.
    *   If the agent asked the **same clarifying questions** repeatedly → add answers to `references/`.
    *   If the agent consumed **excessive tokens** reading large inline blocks → extract to external files.

## 12. Scripts Reference

*   **`init_skill.py`**: Generates a compliant skill skeleton (`scripts/`, `examples/`, `assets/`, `references/`) using the rich template.
*   **`validate_skill.py`**: Enforces folder structure, frontmatter compliance, CSO rules, and execution-policy coverage checks (warning-first by default).
*   **`aggregate_benchmark.py`**: Reads all `grading.json` files in eval run subdirectories and computes a summary benchmark matrix.
*   **`generate_report.py`**: Consumes `benchmark.json` and builds a static HTML visual report.
*   **`generate_review.py`**: Launches an interactive, zero-dependency local HTTP server pointing to `viewer.html` for reviewing eval generated text, diffs, images, and leaving persistent structured feedback (`feedback.json`).
*   **`skill_utils.py`**: Prints effective merged config (defaults + project overlay) for troubleshooting and policy visibility.

## 13. Local Resources
*   **`references/default_parameters.md`**: Full defaults map (resolution order + all default keys + runtime fallbacks).
*   **`references/writing_skills_best_practices_anthropic.md`**: The complete "Gold Standard" authoring guide.
*   **`references/output-patterns.md`**: Templates for agent output formats.
*   **`references/workflows.md`**: Guide for designing skill-internal workflows.
*   **`references/persuasion-principles.md`**: (Advanced) Psychological principles for writing compliant instructions.
*   **`references/testing-skills-with-subagents.md`**: (Advanced) TDD methodology for verifying skills.
*   **`references/eval_schemas.md`**: JSON schemas for evals, grading, comparison, and analysis.
*   **`agents/grader.md`**: Prompt for evaluating skill execution results against expectations.
*   **`agents/comparator.md`**: Prompt for blind A/B comparison of two skill outputs.
*   **`agents/analyzer.md`**: Prompt for post-hoc analysis of comparison/benchmark results.

## 14. Structured Evals (Vendor-Agnostic)

After creating a skill, define 2-3 test prompts to verify it works. Store them in `evals/evals.json`:

```json
{"skill_name": "my-skill", "evals": [
  {"id": 1, "name": "basic-usage",
   "prompt": "Realistic user prompt",
   "files": [],
   "expectations": ["Verifiable outcome 1", "Verifiable outcome 2"]}
]}
```

### Why Evals Matter
Even without automation, recorded test cases force the author to think through edge cases and give the next developer a clear picture of what to test.

### Running Evals
Evals are **vendor-agnostic** — run them through any CLI or IDE:
- Copy the prompt, provide input files, check `expected_outcomes` manually
- Or automate via any LLM API with LLM-as-judge for `expected_outcomes`

### Eval Workflow (Full Cycle)
For rigorous testing, use the agent prompts from `agents/`:
1. **Execute** the eval prompt through any LLM CLI
2. **Grade**: Feed the transcript + outputs to `agents/grader.md` → produces `grading.json`
3. **Compare** (optional): Run same eval with/without skill, feed both outputs to `agents/comparator.md` → produces `comparison.json`
4. **Analyze** (optional): Feed comparison results to `agents/analyzer.md` → produces `analysis.json` with improvement suggestions

See `references/eval_schemas.md` for all JSON schemas.
