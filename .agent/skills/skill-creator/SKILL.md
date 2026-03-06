---
name: skill-creator
description: Use when creating new Agent Skills, upgrading existing skills, running evals to test a skill, benchmarking skill performance, or optimizing a skill's description for better triggering accuracy. Guidelines for Gold Standard skill structures.
tier: 2
version: 2.0
---
# Skill Creator Guide

This skill provides the authoritative standard for creating and iteratively improving Agent Skills. It combines the [Anthropic Skills Standard](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) with our local architecture rules.

**Core loop**: Draft skill → Write test cases → Run evals (with-skill + baseline) → Review with user → Improve → Repeat.

Your job is to figure out where the user is in this process and help them progress. Maybe they want to create a skill from scratch — help narrow intent, write a draft, create tests, run them, iterate. Maybe they already have a draft — go straight to eval/iterate. Be flexible.

## Red Flags (Anti-Rationalization)

**STOP and READ THIS if you are thinking:**
- "I'll skip the eval step, the skill looks fine" → **WRONG**. Run evals — untested skills fail silently in production.
- "I can write the whole skill without talking to the user" → **WRONG**. Capture Intent first — assumptions cause rewrites.
- "The description is descriptive enough" → **WRONG**. CSO triggers are mechanical. Follow the schema.
- "This skill is too simple for a script" → **WRONG**. If logic > 5 lines, text instructions fail 30% of the time. Use a script.
- "I'll skip the viewer and evaluate outputs myself" → **WRONG**. Generate the eval viewer BEFORE evaluating — get results in front of the human ASAP.

## Purpose

Enable agents to create, test, and iteratively improve Agent Skills following the Gold Standard. This skill provides both the quality standards (what makes a good skill) and the workflow engine (how to iterate to get there).

## Capabilities

- Create new skills from scratch with validated structure
- Run structured evals with baseline comparison (with-skill vs without-skill)
- Grade, benchmark, and review eval results via interactive viewer
- Iteratively improve skills based on user feedback
- Optimize skill descriptions for better triggering accuracy
- Package skills into distributable `.skill` files
- Adapt workflow to different environments (Claude Code, Codex, Antigravity, Claude.ai, Cowork)

## 1. Quality Standards (Summary)

> Full details: `references/writing_skills_best_practices_anthropic.md`
> Design patterns: `references/skill_design_patterns.md`

### Skill Anatomy

Every skill follows this directory structure:

```
skill-name/
├── SKILL.md (Required — YAML frontmatter + markdown body)
├── examples/      # Few-shot training: input/output pairs
├── assets/        # User output: templates, files for output
├── references/    # Agent knowledge: specs, guidelines, schemas
├── scripts/       # Executable logic: Python/Bash tools
└── eval-viewer/   # (Optional) Interactive eval review UI
```

All subdirectories are optional. Do NOT create `README.md`, `CHANGELOG.md`, or other aux docs inside the skill folder — all instructions go in `SKILL.md`.

### Key Rules

- **Script-First**: If a step requires >5 lines of if/then/else logic, it MUST be a Python script in `scripts/` — agents are unreliable at executing complex logic from text.
- **12-Line Rule**: Inline code blocks, templates, or examples >12 lines MUST be extracted to `examples/`, `assets/`, or `references/`.
- **Graduated Language**: Skills must work across LLMs (Claude, Gemini, Codex, Qwen, Llama). Use graduated instruction strength:
  - Safety-critical: `MUST`/`ALWAYS` + explain why
  - Behavioral: Explain why + imperative verb
  - Prohibited: `MUST NOT` + consequence
- **CSO (Search Optimization)**: The `description` field determines if a skill is loaded. Start with `Use when...` (preferred), `Guidelines for...`, `Helps with...`, `Standards for...`, or `Defines...`. Keep under 50 words. Make descriptions "pushy" to prevent under-triggering.
- **Red Flags**: Every skill MUST include a "Red Flags" section to prevent agent rationalization.
- **Naming**: Use gerund form `verb-ing-noun` (e.g., `processing-pdfs`). Always lowercase kebab-case.

### Frontmatter

```yaml
---
name: skill-my-capability
description: "Use when..."
tier: [0|1|2]
version: 1.0
---
```

Run `python3 scripts/init_skill.py --help` to see available Tiers. Do NOT guess tiers manually.

### Required Sections in SKILL.md

1. **Purpose** — the "Why"
2. **Red Flags** — "Stop and Rethink" triggers
3. **Capabilities** — bulleted list
4. **Execution Mode** — `prompt-first`, `script-first`, or `hybrid`
5. **Script Contract** — required for script-first/hybrid (command, inputs, outputs, exit codes)
6. **Safety Boundaries** — explicit scope and exclusions
7. **Validation Evidence** — objective verification output
8. **Instructions** — step-by-step algorithms
9. **Examples** — input/output pairs (see `examples/SKILL_EXAMPLE_LEGACY_MIGRATOR.md`)

Template: `assets/SKILL_TEMPLATE.md`

### Execution Mode
- **Mode**: `hybrid`
- **Rationale**: Skill authoring needs judgement for structure/quality decisions and deterministic scripts for repeatable validation and generation.

### Script Contract
- **Primary Commands**:
  - `python3 scripts/init_skill.py <name> --tier <N>` — generate skill skeleton
  - `python3 scripts/validate_skill.py <skill-path>` — validate structure and compliance
  - `python3 scripts/package_skill.py <skill-path>` — package into `.skill` file
- **Inputs**: skill name/path, tier, and local policy config.
- **Outputs**: generated skeletons, validation pass/fail, warnings, `.skill` archives.
- **Failure Semantics**: non-zero exit code on validation errors.

### Safety Boundaries
- Operate only on explicit target skill directories.
- No broad or implicit repo-wide mutation.
- Destructive actions never default; require explicit user intent.

### Validation Evidence
- `validate_skill.py` output and generated diffs.
- Quality checks: section coverage, CSO, inline efficiency, metadata.

## 2. Creating a Skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow they want to capture. If so, extract answers from conversation history first — tools used, sequence of steps, corrections made, I/O formats observed.

1. What should this skill enable the agent to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? Skills with objectively verifiable outputs (file transforms, data extraction, code generation) benefit from tests. Subjective skills (writing style, art) often don't. Suggest the appropriate default, let the user decide.

### Interview and Research

Proactively ask about edge cases, I/O formats, example files, success criteria, dependencies. Wait to write test prompts until this is ironed out.

Check available MCPs — if useful for research, research in parallel via subagents if available, otherwise inline.

### Write the SKILL.md

1. **Check Duplicates**: Verify in your Skill Catalog.
2. **Initialize**:
   ```bash
   python3 scripts/init_skill.py my-new-skill --tier 2
   ```
3. **Populate**: Edit the auto-generated `SKILL.md`. Fill in Red Flags, description, Execution Mode, Script Contract, Safety Boundaries, Validation Evidence. Consult `references/skill_design_patterns.md` and `references/writing_skills_best_practices_anthropic.md`.
4. **Cleanup**: Remove unused placeholder files/directories created by init.
5. **Validate**:
   ```bash
   python3 scripts/validate_skill.py ../my-new-skill
   ```

### Test Cases

After the draft, write 2-3 realistic test prompts — things a real user would actually say. Share them with the user for confirmation, then run them.

Save to `evals/evals.json`. Don't write assertions yet — just prompts. You'll draft assertions while runs are in progress.

```json
{"skill_name": "my-skill", "evals": [
  {"id": 1, "prompt": "Realistic user prompt", "files": [],
   "expectations": ["Verifiable outcome 1", "Verifiable outcome 2"]}
]}
```

See `references/eval_schemas.md` for the full schema.

## 3. Running and Evaluating Test Cases

This section is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Organize by iteration (`iteration-1/`, `iteration-2/`) and within that, each test case gets a directory.

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. Launch everything at once so it all finishes around the same time.

**With-skill run:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
```

**Baseline run** (depends on context):
- **New skill**: no skill at all → save to `without_skill/outputs/`
- **Improving existing skill**: snapshot the old version first (`cp -r`), point baseline at snapshot → save to `old_skill/outputs/`

Write `eval_metadata.json` for each test case with a descriptive name.

### Step 2: While runs are in progress, draft assertions

Don't wait — use this time to draft quantitative assertions. Good assertions are objectively verifiable with descriptive names. Don't force assertions onto subjective outputs.

Update `eval_metadata.json` and `evals/evals.json` with assertions.

### Step 3: As runs complete, capture timing data

When each subagent completes, save `total_tokens` and `duration_ms` to `timing.json` in the run directory. This is the only opportunity to capture this data.

### Step 4: Grade, aggregate, and launch the viewer

1. **Grade each run** — spawn a grader subagent reading `agents/grader.md`. Save `grading.json` with fields `text`, `passed`, `evidence`. For programmatic assertions, write and run a script.

2. **Aggregate into benchmark**:
   ```bash
   python3 scripts/aggregate_benchmark.py <workspace>/iteration-N --skill-name <name>
   ```
   Produces `benchmark.json` and `benchmark.md`.

3. **Analyst pass** — read benchmark data, surface patterns (see `agents/analyzer.md`).

4. **Launch the viewer**:
   ```bash
   nohup python3 eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+, add `--previous-workspace <workspace>/iteration-<N-1>`.

5. **Tell the user**: "I've opened the results in your browser. 'Outputs' tab shows test cases with feedback boxes. 'Benchmark' tab shows quantitative comparison. Come back when you're done."

### Step 5: Read the feedback

When the user is done, read `feedback.json`. Empty feedback = looks good. Focus improvements on test cases with specific complaints.

```bash
kill $VIEWER_PID 2>/dev/null
```

## 4. Improving the Skill

### How to think about improvements

1. **Generalize from feedback.** You're iterating on a few examples to create a skill used many times. Rather than overfitty changes or oppressively constrictive MUSTs, try different metaphors or recommend different patterns.

2. **Keep the prompt lean.** Remove things not pulling their weight. Read transcripts — if the skill wastes time on unproductive steps, trim those instructions.

3. **Explain the why.** Today's LLMs are smart. When given good harness they go beyond rote instructions. If you find yourself writing ALWAYS/NEVER in all caps, reframe with reasoning. That's more powerful and effective.

4. **Look for repeated work across test cases.** Read transcripts — if all subagents independently wrote similar helper scripts, that script should be bundled in `scripts/`.

### The iteration loop

1. Apply improvements
2. Rerun all test cases into `iteration-<N+1>/`, including baselines
3. Launch viewer with `--previous-workspace`
4. Wait for user review
5. Read feedback, improve, repeat

Stop when: user is happy, feedback is all empty, or no meaningful progress.

## 5. Description Optimization

After the skill is working well, optimize the `description` for better triggering accuracy.

### Step 1: Generate trigger eval queries

Create ~20 eval queries — mix of should-trigger and should-not-trigger. Save as JSON:
```json
[{"query": "realistic user prompt with details", "should_trigger": true}]
```

Queries must be realistic — include file paths, personal context, abbreviations, typos, casual speech. Focus on edge cases: near-misses that share keywords but need different skills.

### Step 2: Review with user

Present eval set using the HTML template:
1. Read `assets/eval_review.html`
2. Replace `__EVAL_DATA_PLACEHOLDER__`, `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`
3. Write to temp file and open it
4. User edits queries, exports as `eval_set.json`

### Step 3: Run the optimization loop

> **Dependencies**: Requires `pip install anthropic` and `claude` CLI installed. Claude Code specific — see Section 6 for other environments.

```bash
python3 scripts/run_loop.py \
  --eval-set <path-to-eval-set.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 --verbose
```

This splits eval set into 60% train / 40% test, runs each query 3 times, uses Claude with extended thinking to propose improvements, iterates up to 5 times, selects by test score to avoid overfitting.

### Step 4: Apply the result

Take `best_description` from output, update the skill's frontmatter. Show before/after and scores.

## 6. Environment Adaptations

### Claude Code (full workflow)

All features work: subagents for parallel test runs, viewer via browser, `claude -p` for description optimization, `package_skill.py` for packaging.

### Codex

Codex supports subagents. Adapt:
- **Description optimization**: `run_loop.py` uses `claude -p` which is Claude Code specific. Skip this step or run it manually.
- **Viewer**: If no browser, use `--static <output_path>` for standalone HTML.

### Antigravity IDE

Full workflow available. Follow the standard process. If subagents are available, use parallel test runs. Otherwise, run tests sequentially.

### Claude.ai (no subagents)

- **Running tests**: No subagents. Read the skill's SKILL.md, then follow its instructions yourself, one test at a time. Skip baseline runs.
- **Reviewing**: Skip browser viewer. Present results directly in conversation. Save output files and tell user where they are.
- **Benchmarking**: Skip quantitative benchmarking.
- **Description optimization**: Requires `claude` CLI. Skip on Claude.ai.
- **Packaging**: `package_skill.py` works anywhere with Python.

### Cowork (headless)

- Subagents work. If timeouts occur, run tests sequentially.
- No browser — use `--static <output_path>` for viewer. User clicks link to open HTML.
- Feedback: "Submit All Reviews" downloads `feedback.json` as file.
- GENERATE THE EVAL VIEWER BEFORE evaluating outputs yourself — get results in front of the human ASAP.

## 7. Advanced: Blind Comparison

For rigorous A/B comparison between skill versions, read `agents/comparator.md` and `agents/analyzer.md`. Give two outputs to an independent agent without telling it which is which, let it judge quality.

Optional. Most users won't need it — the human review loop is usually sufficient.

## 8. Package and Present

If the `present_files` tool is available:
```bash
python3 scripts/package_skill.py <path/to/skill-folder>
```
Direct the user to the resulting `.skill` file.

## 9. Scripts & Tools Reference

### `scripts/` — Core automation

- **`init_skill.py`**: Generate compliant skill skeleton
- **`validate_skill.py`**: Enforce structure, frontmatter, CSO, execution-policy
- **`skill_utils.py`**: Config loader (defaults + project overlay) + `parse_skill_md()`
- **`aggregate_benchmark.py`**: Compute benchmark summary from `grading.json` files
- **`generate_report.py`**: Build static HTML report from `benchmark.json`
- **`run_eval.py`**: Run trigger evaluation queries via CLI
- **`run_loop.py`**: Main eval + improvement loop for description optimization
- **`improve_description.py`**: Improve description using Claude with extended thinking
- **`package_skill.py`**: Package skill into `.skill` (ZIP) file

### `eval-viewer/` — Interactive eval review

- **`generate_review.py`**: Launch interactive eval viewer (serves `viewer.html`)
- **`viewer.html`**: Benchmark viewer with Outputs + Benchmark tabs

## 10. Resources Reference

- `references/writing_skills_best_practices_anthropic.md` — Full authoring guide (Anthropic standard)
- `references/skill_design_patterns.md` — Degrees of Freedom, Progressive Disclosure, EDD
- `references/default_parameters.md` — Config defaults and resolution order
- `references/eval_schemas.md` — JSON schemas for evals, grading, comparison, analysis
- `references/output-patterns.md` — Templates for agent output formats
- `references/workflows.md` — Designing skill-internal workflows
- `references/persuasion-principles.md` — Psychological principles for instructions
- `references/testing-skills-with-subagents.md` — TDD methodology for skills
- `agents/grader.md` — Evaluate assertions against outputs
- `agents/comparator.md` — Blind A/B comparison
- `agents/analyzer.md` — Post-hoc analysis of results
