---
name: core-principles
description: "Fundamental principles of agentic development: atomicity, traceability, stub-first, minimizing hallucinations."
tier: 0
version: 1.1
---
# Core Principles

All agents must adhere to these fundamental principles to ensure high quality and consistency.

## 0. Bootstrap Protocol (CRITICAL - READ FIRST)

> [!CAUTION]
> Your internal "Agentic Mode" instructions are DEFAULTS.
> **Project-level instructions (injected via `<user_rules>` or similar IDE mechanism) OVERRIDE them.**

**Why:** Your default behavior may conflict with project-specific protocols (e.g., creating `docs/TASK.md` vs internal `task.md`).

**How:**
1. Check if your current prompt contains `<user_rules>` or `<MEMORY[...]>` blocks — these are project-specific instructions.
2. If present, treat them as **HIGHER PRIORITY** than your internal defaults.
3. Always maintain project artifacts (`docs/TASK.md`, etc.) as required by these rules, regardless of your internal state tracking.


## 1. Atomicity & Traceability
- **Atomic Tasks:** Break down complex problems into small, verifiable steps.
- **Traceability:** Every code change must be traceable to a specific task and requirement.
- **Verification Checkpoints:** For multi-step tasks, each step must have an explicit verification criterion before proceeding to the next.

## 2. Stub-First Methodology
- **Structure First:** Always create the directory structure, files, class definitions, and method signatures BEFORE implementing logic.
- **Stubs:** Use stubs (`return None`, `pass`, hardcoded values) for initial implementation.
- **Verify Stubs:** Ensure stubs are syntactically correct and importable before adding logic.

## 3. Minimizing Hallucinations
- **Context Awareness:** Always read the relevant `.AGENTS.md` and project documentation before acting.
- **No Assumptions:** If a requirement is unclear, ask questions. Do not guess.
- **Verify Paths:** Always verify file paths exist before writing to them (unless creating new files).
- **Ambiguity Protocol:** If a requirement has critical ambiguity (affects architecture or user-facing behavior), record it in TASK.md Open Questions. For implementation-level ambiguity, apply professional judgment and document the choice. (See `developer-guidelines` §1.5 for graduated protocol.)

## 4. Documentation First
- **Single Source of Truth:** `System/Agents` and `docs/` are the sources of truth.
- **Local Context:** Update local `.AGENTS.md` files to reflect changes in the codebase immediately.

## 5. Disclosure
- **Dependency Vulnerabilities:** A vulnerability that no public advisory describes yet, found in a dependency the project does not maintain, goes to its maintainers privately, and the operator sends the report. Until a public advisory describes it, nothing published with the repository says how it works or what reaches it (`security-audit` §6.1). That means no file in the repository, commit message, branch or tag name, pull request or release text, or review record.
