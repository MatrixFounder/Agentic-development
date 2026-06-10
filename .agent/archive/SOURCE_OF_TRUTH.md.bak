# Source of Truth Map

This document defines authoritative files for prompts, skills, workflows, and tools.

## Canonical Sources

| Domain | Authoritative Source | Notes |
|---|---|---|
| Orchestrator system prompt (Cursor) | `AGENTS.md` | Main runtime policy for Cursor-like environments. |
| Orchestrator system prompt (Antigravity) | `GEMINI.md` | Main runtime policy for Antigravity/Gemini environments. |
| Agent role prompts | `System/Agents/*.md` | Technical prompts use numeric prefixes (`00-10`), product prompts use `p00-p04`. |
| Skills definitions | `.agent/skills/*/SKILL.md` | Skill behavior source; scripts/examples are colocated in each skill directory. |
| Skills taxonomy & guidance | `System/Docs/SKILLS.md` and `System/Docs/SKILL_TIERS.md` | Catalog + loading policy. |
| Workflow definitions | `.agent/workflows/*.md` | Executable workflow steps and nested calls. |
| Workflow manual | `System/Docs/WORKFLOWS.md` | Human-readable workflow guide. |
| Tool schemas | `.agent/tools/schemas.py` | Native tool/function definitions and parameters. |
| Tool execution engine | `System/scripts/tool_runner.py` | Dispatcher and runtime guardrails. |
| Orchestrator tooling guide | `System/Docs/ORCHESTRATOR.md` | Operational reference for tools and dispatcher. |

## Memory Artifacts Contract (BI-006)

1. `AGENTS.md` (and `GEMINI.md` where applicable) are root runtime policy files.
2. `.AGENTS.md` is a per-directory memory artifact for source-code folders in the target development project.
3. `.AGENTS.md` creation policy is preserved for target source-code development folders.
4. `skill-update-memory` is the canonical helper for synchronizing `.AGENTS.md` with code changes.
5. If `.AGENTS.md` does not exist yet, helpers must not fail; bootstrap mode may create missing files only inside explicit development roots (`--development-root`, default: `src`).

## Command Conventions

1. Canonical workflow command form: `run <workflow-name>`.
2. Chat alias form: `/workflow-name`.
3. Nested workflow calls inside workflow files: `Call /workflow-name`.

## Naming Conventions

### Prompts (`System/Agents`)
1. Technical prompts: `NN_<role>_prompt.md` (example: `06_planner_prompt.md`).
2. Product prompts: `pNN_<role>_prompt.md` (example: `p03_product_director_prompt.md`).

### Workflows (`.agent/workflows`)
1. Preferred pattern: `[variant]-[stage]-[action].md`.
2. Use kebab-case names and keep names stable after publication.

### Skills (`.agent/skills`)
1. Skill directory name must match frontmatter `name` in `SKILL.md`.
2. Existing legacy names are supported; new skills should prefer explicit, stable names.
3. Tier and version metadata are required in frontmatter (`tier`, `version`).

### Tools (`.agent/tools`)
1. Tool names in `.agent/tools/schemas.py` are canonical API names.
2. Documentation must reference real tool names (for example: `git_status`, not `git_ops`).

## Governance Rule

If documentation conflicts with runtime files, runtime files are authoritative:
1. `AGENTS.md` / `GEMINI.md`
2. `System/Agents/*.md`
3. `.agent/tools/schemas.py`
4. `.agent/workflows/*.md`
