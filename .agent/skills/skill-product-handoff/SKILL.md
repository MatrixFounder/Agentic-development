---
name: skill-product-handoff
description: "Guidelines for managing the Product-to-Technical handoff, including Quality Gates and BRD Compilation."
tier: 1
version: 1.1
---

# Product Handoff Protocol

## 1. Objective
To ensure that NO technical work begins until the Product Artifacts are **Verified**, **Approved**, and **Compiled**.

## 2. The Quality Gate
You MUST verify that the Product Director (`p03`) has signed off.

### Verification Command
```bash
python3 [skill_path]/scripts/verify_gate.py docs/product/APPROVED_BACKLOG.md
```
> **Note:** `[skill_path]` is the path to this skill (e.g. `.agent/skills/skill-product-handoff`).

- **Exit Code 0:** GATE OPEN. Proceed.
- **Exit Code 1:** GATE CLOSED. Stop immediately.

## 3. BRD Compilation
Once the gate is open, you MUST compile the scattered artifacts into a single `BRD.md`.

### Compilation Command
```bash
python3 [skill_path]/scripts/compile_brd.py docs/product/ docs/BRD.md
```
- **Inputs:** `MARKET_STRATEGY.md`, `PRODUCT_VISION.md`, `SOLUTION_BLUEPRINT.md`.
- **Output:** `docs/BRD.md`.

## 4. Triggering Technical Phase
After the BRD is compiled, you initiate the Technical Phase.

### Trigger Command
```bash
python3 [skill_path]/scripts/trigger_technical.py docs/BRD.md docs/TASK.md
```
- **Effect:** Creates the root `TASK.md` for the Architect/Developer agents.

## 5. Workflow Integration
This skill is primarily used by the **Orchestrator (`p00`)** or the **Handoff Workflow** to accept the final output from `p04`.

## 6. Examples
- **BRD:** `examples/example_brd.md` (Typical output structure).
- **Gate:** `examples/example_approved_backlog.md` (Showing valid Hash format).
