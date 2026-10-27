---
name: requirements-analysis
description: "Use when gathering and refining requirements into a structured TASK."
tier: 1
version: 1.5
---
# Requirements Analysis

## 1. Analysis Loop
1. **Reconnaissance:** Read project structure, `.AGENTS.md`.
2. **Identification:** What are the use cases? Actors? Preconditions?
3. **Clarification:** List open questions. Better to ask now than fail later.

## 2. Technical Specification (TASK) Structure

You MUST follow the structure defined in `assets/task_template.md`.
Read this file to understand the required headers and sections.

## 3. Important Rules

### ✅ DO:
1. **Be detailed:** Describe every step in scenarios.
2. **Think about edge cases:** Consider errors, exceptions, boundary conditions.
3. **Ask questions:** If something is unclear — add to "Open Questions".
4. **Use existing terminology:** Use terms from project documentation.
5. **Link to existing functionality:** Explicitly state how new functionality interacts with existing.
6. **Measure the copies that run:** a task that fixes a published advisory in a dependency states,
   in its problem section, each copy of the library that a runtime loads. For each copy, it names
   the package that carries it, its version and the advisories that cover it. A library that no
   runtime of the project loads, such as a package of type declarations only, is stated as such.
   The requirements name the copies that the fix reaches and those it does not. Steps 1 to 3 of
   `security-audit` §3, Copies outside the dependency tree, give the measurement. A vulnerability
   with no published advisory follows `security-audit` §6.1. The problem section is the one under
   `<!-- contract:problem -->`, which `System/Agents/02_analyst_prompt.md` defines; the task
   template calls it §1, General Description.

### ❌ DO NOT:
1. **DO NOT write code:** You create TASK, not implementation.
2. **DO NOT design architecture:** This is the Architect's task.
3. **DO NOT invent:** If unclear, ask a question.
4. **DO NOT make assumptions:** Explicitly state where you make an assumption.
5. **DO NOT overcomplicate:** Keep it simple, don't overengineer.
6. **DO NOT ignore existing functionality:** Study the project before writing TASK.
7. **DO NOT leave important decisions for later:** All key decisions must be selected or clarification requested from user.

### 🔴 CRITICAL: Uncertainty Management
You are at the earliest stage of development. Unresolved uncertainty now can lead to project failure. Therefore:
1. **Pay maximum attention to unclear points**
2. **Do not hesitate to ask many questions**
3. **Better to ask a "stupid" question than make an incorrect assumption**
4. **If in doubt — add to "Open Questions"**
