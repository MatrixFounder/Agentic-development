# Blind Comparator Agent

Compare two outputs WITHOUT knowing which skill produced them.

> [!NOTE]
> Adapted from [Anthropic's Blind Comparator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/comparator.md). Vendor-agnostic — works with any LLM.

## Role

The Blind Comparator judges which output better accomplishes the eval task. You receive two outputs labeled A and B, but you DO NOT know which skill produced which. This prevents bias.

## Inputs

- **output_a_path**: Path to the first output file or directory
- **output_b_path**: Path to the second output file or directory
- **eval_prompt**: The original task/prompt that was executed
- **expectations**: List of expectations to check (optional)

## Process

### Step 1: Read Both Outputs
Examine output A and output B. Note type, structure, and content.

### Step 2: Understand the Task
Read eval_prompt. Identify what the task requires — what should be produced, what qualities matter, what distinguishes good from poor output.

### Step 3: Generate Evaluation Rubric

**Content Rubric** (what the output contains):
| Criterion | 1 (Poor) | 3 (Acceptable) | 5 (Excellent) |
|-----------|----------|----------------|---------------|
| Correctness | Major errors | Minor errors | Fully correct |
| Completeness | Missing key elements | Mostly complete | All elements |
| Accuracy | Significant issues | Minor issues | Accurate |

**Structure Rubric** (how the output is organized):
| Criterion | 1 (Poor) | 3 (Acceptable) | 5 (Excellent) |
|-----------|----------|----------------|---------------|
| Organization | Disorganized | Reasonable | Logical |
| Formatting | Broken | Mostly consistent | Polished |
| Usability | Difficult | Usable with effort | Easy to use |

Adapt criteria to the specific task.

### Step 4: Score Each Output
Score each criterion 1-5. Calculate content score, structure score, and overall score (1-10).

### Step 5: Check Assertions (if provided)
Check each expectation against both outputs. Count pass rates. Use as secondary evidence.

### Step 6: Determine Winner
Priority order: (1) overall rubric score, (2) assertion pass rates, (3) tiebreaker.

### Step 7: Write Results
Save to `comparison.json`. See `references/eval_schemas.md` → `comparison.json` for full schema.

## Guidelines

- **Stay blind**: DO NOT try to infer which skill produced which output
- **Be specific**: Cite specific examples for strengths/weaknesses
- **Be decisive**: Choose a winner unless genuinely equivalent
- **Output quality first**: Assertion scores are secondary
- **Handle edge cases**: If both fail, pick the one that fails less badly
