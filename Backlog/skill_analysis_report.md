# Analysis Report: `writing-skills` (External Source)

**Source:** [github.com/obra/superpowers/.../writing-skills/SKILL.md](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md)
**Date:** 2026-01-26

## 1. Executive Summary
The external `writing-skills` document presents a highly mature, TDD-inspired approach to skill creation. It treats skills not as static documentation, but as **executable code for agents** that must be tested, optimized for search (CSO), and hardened against "rationalization" (agent excuses).

Implementing these concepts will significantly increase the reliability and discoverability of our agent skills.

## 2. Key Concepts to Adopt

### 2.1 TDD for Skills (Red-Green-Refactor)
*   **Concept**: You cannot write a good skill unless you know *exactly* how an agent fails without it.
*   **Workflow**:
    1.  **RED**: Run a "pressure scenario" with a subagent *without* the skill. Record the failure and the specific "rationalization" (excuse) the agent used.
    2.  **GREEN**: Write the minimal skill to address that specific failure.
    3.  **REFACTOR**: Generalize and optimize.

### 2.2 Claude Search Optimization (CSO)
*   **Critical Insight**: The `description` field determines *if* a skill is loaded.
*   **Rule**: Description must be **"Use when [TRIGGER]"**, NOT "What this skill does".
    *   *Bad*: "Guide for TDD workflow." (Summarizes content)
    *   *Good*: "Use when implementing a new feature or fixing a bug." (Triggering condition)
*   **Reason**: If the description summarizes the workflow, the model might just follow the summary and *skip loading the file*.

### 2.3 Rationalization Management
*   **Concept**: Agents (like humans) will find excuses to skip steps ("it's too simple", "I'll test later").
*   **Solution**: explicit **"Red Flags"** and **"Rationalization Tables"** in the skill.
    *   *Example*: "Stop if you think 'I already tested manually'. Delete code and start over."

### 2.4 Skill Organization Types
*   **Technique**: Step-by-step method (e.g., "debugging-race-conditions").
*   **Pattern**: Mental model (e.g., "stub-first-development").
*   **Reference**: Heavy documentation (move to sidecar files if >100 lines).

## 3. Gap Analysis

| Feature | Current `skill-creator` | External `writing-skills` | Recommendation |
| :--- | :--- | :--- | :--- |
| **Creation Philosophy** | Progressive Disclosure | TDD (Red-Green-Refactor) | **Adopt TDD/Adversarial mindset.** |
| **Description Field** | "One-line summary" | "Use when [TRIGGER]" | **Enforce "Use when..." format.** |
| **Resilience** | Best Practices section | Rationalization Tables & Red Flags | **Add "Red Flags" section.** |
| **Validation** | Basic structure check | CSO & Token Efficiency checks | **Add CSO checks to script.** |

## 4. Action Plan

I recommend upgrading our `skill-creator` with the following changes:

### Phase 1: Documentation Update (`SKILL.md`)
1.  **Update Philosophy**: explicit shift to "Skills as Code" and TDD.
2.  **New Section**: "Claude Search Optimization" (CSO) guidelines.
3.  **New Section**: "hardening Skills" (Red Flags/Rationalizations).

### Phase 2: Template Update (`resources/SKILL_TEMPLATE.md`)
1.  **Frontmatter**: Change description placeholder to `Use when [TRIGGER]...`.
2.  **New Sections**: Add "Red Flags / Rationalizations" to the template.

### Phase 3: Tooling Update (`scripts/validate_skill.py`)
1.  **Check**: Warn if `description` does not start with "Use when".
2.  **Check**: Warn if Description > 50 words (Token Efficiency).
