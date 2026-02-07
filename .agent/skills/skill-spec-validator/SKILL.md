---
name: skill-spec-validator
description: Validates conformance between TASK.md (RTM) and PLAN.md (Atomic Checklists).
tier: 2
---

# Skill: Spec Validator

> [!IMPORTANT]
> **TIER 2 (High Integrity)**: This skill acts as a mechanical gatekeeper for the `/vdd-enhanced` workflow.

## 1. Purpose
To strictly enforce "Requirements Hardening" by mechanically verifying that:
1.  `TASK.md` contains a Requirements Traceability Matrix (RTM).
2.  `PLAN.md` explicitly covers every item in the RTM using Atomic Checklists.

## 2. Usage

### Mode A: TASK Validation
**Trigger**: After Analysis Phase.
**Command**:
```bash
python3 scripts/validate.py --mode task /absolute/path/to/docs/TASK.md
```
**Checks**:
- Presence of table `## Requirements Traceability`.
- Columns `ID`, `Requirement`.

### Mode B: PLAN Validation
**Trigger**: After Planning Phase.
**Command**:
```bash
python3 scripts/validate.py --mode plan /absolute/path/to/docs/PLAN.md /absolute/path/to/docs/TASK.md
```
**Checks**:
- Every `ID` in TASK matches a `[ID]` tag in PLAN.

## 3. Failure Handling
- **Exit Code 1**: Issues found. Orchestrator should trigger a **Correction Loop** (instruct Analyst/Planner to fix).
- **Bypass**: If validation is buggy, add `[BYPASS_VALIDATION]` to the Title of text in `TASK.md`.

## 4. Dependencies
- Python 3
- `validate.py` (in `scripts/`)
