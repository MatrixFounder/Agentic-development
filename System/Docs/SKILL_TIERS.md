# Skill Tiers (Authoritative)

> **Source of Truth:** This document (System/Docs/SKILL_TIERS.md)
> **Purpose:** Optimize token usage by defining strict loading protocols for skills.

## Overview

All skills in `.agent/skills/` MUST define a `tier` property in their YAML frontmatter. This determines when they are loaded into the agent's context.

## TIER 0: SYSTEM FOUNDATION (Mandatory)

**Loading Rule:** Loaded at **SESSION STARTUP** (Bootstrap) via system prompts (`AGENTS.md`/`GEMINI.md`).
**Condition:** NEVER Lazy-Load. These enable the agent to function, execute commands, and manage files.

| Skill | Tier | Description |
|-------|------|-------------|
| `core-principles` | 0 | Anti-hallucination rules, Stub-First methodology |
| `skill-safe-commands` | 0 | **Enables automation** — auto-run for the archive script, `ls`, `git`, tests |
| `artifact-management` | 0 | Archiving protocol, file management |
| `skill-session-state` | 0 | Persist/Restore session context (Mode, Task) |

## TIER 1: PHASE-TRIGGERED

**Loading Rule:** Loaded when entering a specific **PHASE** (Analysis, Architecture, Planning, etc.).
**Condition:** Defined in `skill-phase-context`.

| Skill | Tier | Phase |
|-------|------|-------|
| `requirements-analysis` | 1 | Analysis |
| `skill-task-model` | 1 | Analysis |
| `skill-archive-task` | 1 | Analysis (New Task) |
| `architecture-design` | 1 | Architecture |
| `architecture-format-core` | 1 | Architecture |
| `planning-decision-tree` | 1 | Planning |
| `skill-planning-format` | 1 | Planning |
| `tdd-stub-first` | 1 | Planning / Development |
| `developer-guidelines` | 1 | Development |
| `documentation-standards` | 1 | Development |
| `code-review-checklist` | 1 | Review |
| `plan-review-checklist` | 1 | Review |
| `task-review-checklist` | 1 | Review |
| `architecture-review-checklist`| 1 | Review |

## TIER 2: EXTENDED (On-Demand)

**Loading Rule:** Loaded **ONLY** when explicitly requested by user, workflow, or specific trigger condition.
**Condition:** Default tier for most specialized skills unless explicitly marked Tier 3.

| Skill | Tier | Common Triggers |
|-------|------|-----------------|
| `architecture-format-extended` | 2 | New system creation, major refactor |
| `skill-reverse-engineering` | 2 | Sync docs with code |
| `skill-update-memory` | 2 | Post-development updates |
| `skill-adversarial-security` | 2 | VDD / Security Audit |
| `skill-adversarial-performance`| 2 | VDD / Performance Review |
| `vdd-adversarial` | 2 | VDD Workflow |
| `vdd-sarcastic` | 2 | VDD Workflow (Sarcastic Mode) |
| `skill-orchestrator-patterns` | 2 | Orchestrator internal use |
| `skill-phase-context` | 2 | System internal use |
| `testing-best-practices` | 2 | Complex testing scenarios |
| `security-audit` | 2 | Security Audit workflow |
| `skill-product-analysis` | 2 | Product Vision creation |
| `skill-product-backlog-prioritization` | 2 | Backlog prioritization (WSJF) |
| `mermaid-authoring-guidelines` | 2 | Before the first figure of any output, in any phase |
| *(All others)* | 2 | Explicit request |

## TIER 3: HIGH ASSURANCE

**Loading Rule:** Loaded only for strict or critical workflows where stronger verification is required.
**Condition:** Explicit workflow choice or direct user request.

| Skill | Tier | Common Triggers |
|-------|------|-----------------|
| `tdd-strict` | 3 | `full-robust`, critical production changes |

## Metadata Format

Every `SKILL.md` must start with:

```yaml
---
name: [skill-name]
description: [Short description]
tier: [0|1|2|3]
---
```
