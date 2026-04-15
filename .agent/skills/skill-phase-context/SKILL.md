---
name: skill-phase-context
description: "Skill loading tiers: TIER 0 (always), TIER 1 (phase-triggered), TIER 2 (extended). Defines when to load which skills."
tier: 2
version: 1.1
---
# Phase Context Loading Protocol

This skill defines **skill loading tiers** to optimize token consumption while preserving automation capabilities.

> [!IMPORTANT]
> **Single Source of Truth for Skill Loading Strategy.**
> Reference this skill to understand WHEN to load WHICH skills.

## TIER 0: System Foundation — ALWAYS LOADED

> [!CAUTION]
> **NEVER lazy-load TIER 0 skills. They enable core automation.**
> These skills MUST be available in EVERY session at bootstrap.

| Skill | Tokens | Why Always Load |
|-------|--------|-----------------|
| `core-principles` | ~519 | Anti-hallucination rules, Stub-First, Documentation First |
| `skill-safe-commands` | ~927 | **Enables automation** — `mv`, `ls`, `git`, tests auto-run |
| `artifact-management` | ~636 | Archiving protocol, file management, dual state tracking |
| **TOTAL** | **~2,082** | **Non-negotiable system foundation** |

### TIER 0 Loading Rule
- Load at session bootstrap (via `GEMINI.md` / `.cursorrules`)
- These skills are loaded BEFORE any phase begins
- Never remove or defer loading of TIER 0 skills

---

## TIER 1: Phase-Triggered — Load on Phase Entry

These skills are phase-specific and loaded when entering the corresponding phase.

| Phase | Skills to Load | Approx. Tokens |
|-------|----------------|----------------|
| **Analysis** | `requirements-analysis`, `skill-task-model`, (`skill-archive-task` if new task) | ~2,000-2,900 |
| **Architecture** | `architecture-design`, (`architecture-format-core` OR `-extended`) | ~1,750-3,100 |
| **Planning** | `planning-decision-tree`, `skill-planning-format`, `tdd-stub-first` | ~1,425 |
| **Development** | `developer-guidelines`, `documentation-standards` | ~1,100 |
| **Review** | Phase-specific `-review-checklist` skill | ~300-400 |
| **Security** | `security-audit` | ~500 |
| **VDD** | `vdd-adversarial`, (`adversarial-*` per workflow) | ~1,000-2,500 |

### TIER 1 Loading Conditions

**Analysis Phase:**
- `requirements-analysis` — When 02_analyst activated
- `skill-task-model` — When creating/updating TASK.md
- `skill-archive-task` — When existing TASK.md detected AND new (unrelated) task

**Architecture Phase:**
- `architecture-design` — When 04_architect activated
- `architecture-format-core` — **Default** for most updates
- `architecture-format-extended` — Load ONLY for:
  - Creating NEW system from scratch
  - Major refactor (>3 components affected)
  - User explicitly requests "full architecture template"

**Planning Phase:**
- `planning-decision-tree` — When 06_planner activated
- `skill-planning-format` — When creating PLAN.md
- `tdd-stub-first` — When stub creation starts

**Development Phase:**
- `developer-guidelines` — When 08_developer activated
- `documentation-standards` — When updating docs

**Review Phase:**
- Load the appropriate `*-review-checklist` for the current review type

---

## TIER 2: Extended — Load Only When Explicitly Requested

These skills are specialized and loaded only when explicitly invoked by user or workflow.

| Skill | Tokens | Loading Condition |
|-------|--------|-------------------|
| `architecture-format-extended` | ~3,000 | New system / major refactor / user requests full template |
| `skill-reverse-engineering` | ~1,322 | User requests "sync docs with code" / docs-code mismatch |
| `skill-update-memory` | ~1,101 | Post-development phase, .AGENTS.md updates needed |
| `skill-adversarial-security` | ~838 | VDD workflow with security focus |
| `skill-adversarial-performance` | ~946 | VDD workflow with performance focus |
| `vdd-sarcastic` | ~145 | VDD workflow with sarcastic mode |

---

## Integration

### How Agents Should Reference This

Agent prompts should:
1. Always load TIER 0 skills at session start
2. Load TIER 1 skills when entering their specific phase
3. Load TIER 2 skills only when explicitly triggered

### Referenced By
- `.gemini/GEMINI.md` — TIER 0 at bootstrap
- `.cursorrules` — TIER 0 at bootstrap
- All agent prompts — TIER 1 at phase entry
- VDD workflows — TIER 2 when invoked
