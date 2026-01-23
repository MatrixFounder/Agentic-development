# Task 045: Enrich architecture-design

> **Status:** ACTIVE
> **Created:** 2026-01-23
> **Owner:** Orchestrator

## 0. Meta Information
- **Task ID:** 045
- **Slug:** `enrich-architecture-design`

## 1. Goal
Enrich `architecture-design` skill by providing standard architectural pattern references (Clean Architecture, Event-Driven) in `resources/patterns/` to guide consistent system design.

## 2. Scope
- **Target Skill:** `.agent/skills/architecture-design`
- **New Directory:** `.agent/skills/architecture-design/resources/patterns/`
- **New Files:** 
  - `resources/patterns/clean_architecture.md`
  - `resources/patterns/event_driven.md`
- **Modified File:** `SKILL.md` (Add references).

## 3. Deliverables
1. [ ] Created `clean_architecture.md` (Layer definitions, Dependency Rule).
2. [ ] Created `event_driven.md` (Async flows, Brokers, Idempotency).
3. [ ] Updated `SKILL.md` to point to these new resources.

## 4. Implementation Plan
See `docs/PLAN.md` for detailed steps.
