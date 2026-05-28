---
name: skill-orchestrator-patterns
description: "Stage Cycle pattern and dispatch table for Orchestrator compression. Defines common Init→Review→Revision flow."
version: 1.0
tier: 2
---
# Orchestrator Patterns

This skill defines reusable patterns for the Orchestrator's pipeline stages, enabling compressed prompts.

> [!IMPORTANT]
> **Reference this skill for Stage Cycle logic.**
> The Orchestrator uses these patterns instead of verbose per-scenario instructions.

## Stage Dispatch Table

| Stage | Agent Prompt | Reviewer Prompt | Max Cycles | Skill | Next Stage |
|-------|--------------|-----------------|------------|-------|------------|
| Analysis | `02_analyst` | `03_task_reviewer` | 2 | `skill-archive-task` | Architecture |
| Architecture | `04_architect` | `05_architecture_reviewer` | 2 | `architecture-design` | Planning |
| Planning | `06_planner` | `07_plan_reviewer` | 2 (1 rev) | `planning-decision-tree` | Execution |
| Execution | `08_developer` | `09_code_reviewer` | 2 (1 fix) | `developer-guidelines` | Next Task / Completion |

---

## Pattern: Stage Cycle

### Applicability
- Stages with Init → Review → Revision flow
- Applies to: Analysis, Architecture, Planning, Execution

### Init Phase

```
INPUT: {stage_name}, {agent_prompt}, {artifact_path}

FLOW:
1. Read agent prompt
2. Pass required context to agent
3. Wait for result: { artifact_file, blocking_questions }

DECISION:
- IF blocking_questions → STOP, ask user (Scenario 14)
- ELSE → proceed to Review
```

### Review Phase

```
INPUT: {artifact_file}, {reviewer_prompt}, {iteration}

FLOW:
1. Read reviewer prompt
2. Pass artifact + context to reviewer
3. Wait for result: { review_file, has_critical_issues }

DECISION TABLE:
| Condition | Action |
|-----------|--------|
| No issues | → Next Stage |
| Issues AND iteration < max | → Revision |
| Critical issues AND iteration = max | → STOP, ask user |
| Non-critical issues AND iteration = max | → Next Stage (with warning) |
```

### Revision Phase

```
INPUT: {review_file}, {original_artifact}, {agent_prompt}

INSTRUCTION TO AGENT:
"Fix comments from {review_file}. Do NOT change unrelated parts. Preserve structure."

FLOW:
1. Pass review + original to agent
2. Wait for updated artifact
3. Return to Review Phase (+1 iteration)
```

---

## Expected Results Schema

### From Doer Agent (Analyst, Architect, Planner, Developer)

```yaml
artifact_file: "path/to/artifact.md"
blocking_questions: []  # Empty = proceed
```

### From Reviewer Agent

```yaml
review_file: "path/to/review.md"
has_critical_issues: true/false
```

### Extended Schema (Developer)

```yaml
modified_files: [...]
new_files: [...]
test_report: "tests/tests-{ID}/test-{ID}-{slug}.md"
documentation_updated: true
open_questions: []  # Treated as blocking_questions
```

### Extended Schema (Planner)

```yaml
plan_file: "path/to/plan.md"
task_files: ["path/to/task1.md", ...]
blocking_questions: []
```

### Extended Schema (Plan Reviewer)

```yaml
review_file: "path/to/plan_review.md"
has_critical_issues: true/false
comments_count: number
coverage_issues: [...]
missing_descriptions: [...]
```

### Extended Schema (Code Reviewer)

Structured footer (control-flow + status). The prose review report — three
pillars plus the "Verified" block — is passed to the developer as the report
**body**; it is NOT a structured key.

```yaml
review_status: "APPROVED | REJECTED"
has_critical_issues: true/false   # sole control-flow key (see DECISION TABLE)
e2e_tests_pass: true/false
stubs_replaced: true/false
```

---

## Exceptions (Not Pattern-Compatible)

### Scenario 13: Completion

No reviewer. Unique flow:
1. Archive current `docs/TASK.md` (via `skill-archive-task`)
2. Collect statistics
3. Generate final report

### Scenario 14: Blocking Questions

Immediate pause. Flow:
1. Formulate message with blocking questions
2. Wait for user answers
3. Resume at current stage

---

## Stage-Specific Notes

### Analysis Stage
- **Must apply**: `skill-archive-task` protocol before creating new TASK
- **Instruction for Analyst**: "Create/Overwrite docs/TASK.md completely. Do NOT append."

### Planning Stage
- **Iteration limits**: Max 1 revision cycle for Plan
- **Extended result**: `task_files[]`, `coverage_issues[]`, `missing_descriptions[]`

### Execution Stage
- **Per-task tracking**: TASK {n} of {total}
- **Iteration limit**: Max 1 fix cycle
- **Instruction for Developer**: "Fix comments. Do NOT refactor. Run tests."
