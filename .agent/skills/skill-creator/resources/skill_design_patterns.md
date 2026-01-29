# Skill Design Patterns

## 1. Degrees of Freedom
Match the level of specificity to the task's fragility.

- **High Freedom (Text)**: Use when multiple approaches are valid.
    - *Example*: "Draft a polite email reply."
- **Medium Freedom (Pseudocode)**: Use when a preferred pattern exists but variation is okay.
    - *Ref*: `resources/email_templates.md`
- **Low Freedom (Scripts)**: Use when operations are fragile or consistency is critical.
    - *Example*: `scripts/deploy_production.py`

> [!TIP]
> **Script-First Rule**: If logic > 5 lines, force **Low Freedom** (Script).

## 2. Progressive Disclosure
Manage context efficiency by loading details only when needed.

1.  **Metadata (Frontmatter)**: Always in context (~100 words).
    - *Hook*: `description: "Use when..."`
2.  **SKILL.md Body**: Loaded when triggered (~1000 tokens max).
    - *Content*: Core workflow + Navigation.
3.  **Bundled Resources**: Loaded strictly on demand.
    - *Scripts*: Executed without reading.
    - *References*: Read only if specifically needed/linked.

### Pattern: Domain Split
Avoid giant monorepos. Split by domain.
```
skill-cloud/
├── SKILL.md (Router)
└── references/
    ├── aws.md
    └── gcp.md
```

## 3. Skills as Code (Evaluation-Driven Development)
We treat skills as executable code.

1.  **Define Evaluations**: Create 3 scenarios (inputs + expected outputs) *before* writing instructions.
2.  **RED (Pressure Test)**: Run a subagent *without* the skill on a hard task. Record the failure/laziness.
3.  **GREEN (Fix)**: Add the minimal instruction/script to solve it.
4.  **REFACTOR**: Extract inline blobs to `examples/` or `resources/`.

## 4. Workflows & Feedback Loops (Complex Tasks)
For multi-step or fragile tasks, use the **Checklist Pattern**.

> **Self-Correcting Loop**:
> 1.  **Plan**: Agent generates a plan/checklist.
> 2.  **Validate**: Agent runs a script to check the plan.
> 3.  **Execute**: Agent performs the action.
> 4.  **Verify**: Agent runs a script to verify the result.

**Example Checklist (Output Pattern):**
```markdown
- [ ] Analysis (run `analyze.py`)
- [ ] Planning (create `plan.json`)
- [ ] Validation (run `validate_plan.py`)
- [ ] Execution (run `execute.py`)
```

## 5. Anti-Hallucination Patterns
- **Ground Truth**: Provide `examples/input_output.json`.
- **Pre-Computation**: Don't ask the agent to "imagine" a file structure. Provide `resources/skeleton.zip` or a creation script.
