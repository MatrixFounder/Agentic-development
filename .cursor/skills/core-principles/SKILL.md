---
name: core-principles
description: "Fundamental principles of agentic development: atomicity, traceability, stub-first, minimizing hallucinations."
version: 1.0
---
# Core Principles

All agents must adhere to these fundamental principles to ensure high quality and consistency.

## 1. Atomicity & Traceability
- **Atomic Tasks:** Break down complex problems into small, verifiable steps.
- **Traceability:** Every code change must be traceable to a specific task and requirement.

## 2. Stub-First Methodology
- **Structure First:** Always create the directory structure, files, class definitions, and method signatures BEFORE implementing logic.
- **Stubs:** Use stubs (`return None`, `pass`, hardcoded values) for initial implementation.
- **Verify Stubs:** Ensure stubs are syntactically correct and importable before adding logic.

## 3. Minimizing Hallucinations
- **Context Awareness:** Always read the relevant `.AGENTS.md` and project documentation before acting.
- **No Assumptions:** If a requirement is unclear, ask questions. Do not guess.
- **Verify Paths:** Always verify file paths exist before writing to them (unless creating new files).

## 4. Documentation First
- **Single Source of Truth:** `System/Agents` and `docs/` are the sources of truth.
- **Local Context:** Update local `.AGENTS.md` files to reflect changes in the codebase immediately.
