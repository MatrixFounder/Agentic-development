---
name: documentation-standards
description: Standards for code documentation, comments, and artifact updates.
tier: 1
version: 1.3
---
# Documentation Standards

**Purpose**: Defines the non-negotiable standards for code comments, docstrings, and global artifacts.

## 1. Red Flags (Anti-Rationalization)
**STOP if you are thinking:**
- "I'll add comments later" -> **WRONG**. Undocumented code is technical debt from the moment it is written.
- "The code is self-documenting" -> **WRONG**. Code explains *how*; comments explain *why*.
- "Artifacts are optional" -> **WRONG**. Artifacts like `.AGENTS.md` are the agent's long-term memory.

## 2. Docstrings & JSDoc
All classes and functions MUST have documentation.

### Python
Use Google-style docstrings.
> [!TIP]
> See `assets/templates/python_docstring.py` for the format.

### JavaScript / TypeScript
Use JSDoc standards.
> [!TIP]
> See `assets/templates/jsdoc_template.ts` for the format.

## 3. Comments
- **Why vs What**: Explain the *reason* for logic, not the syntax.
- **Work Tracking**: Use `# T O D O:` (Python) or `// T O D O:` (JS/TS) for future work.

## 4. Path Standards (CRITICAL)
- **Relative Paths Only**: When linking to internal files in Artifacts (PLAN.md, TASK.md), ALWAYS use relative paths.
    - ✅ `[Ref](src/main.py)`
    - ✅ `[.agent/skills/core.md](.agent/skills/core.md)`
    - ❌ `file:///Users/username/project/src/main.py`
    - ❌ `/Absolute/System/Path`

## 5. Artifacts (`.AGENTS.md`)
**MANDATORY**: Every directory must have this file.
> [!TIP]
> Use the template at `assets/templates/agents_md_template.md`.

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "It's a throwaway script" | Scripts evolve into products. Documenting later costs 3x more time. |
| "I don't know the types yet" | Use `Any` or `unknown` but document *what* the value represents. |

## 6. Resources
- `assets/templates/`: Collections of templates.
- `examples/good_documentation.py`: Gold standard example.
