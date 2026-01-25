# Task 004: Unified Artefact Handling for docs/TZ.md

You are an expert Prompt Engineer and System Architect specializing in multi-agent LLM development frameworks.

CONTEXT:
We are improving the Agentic-development framework (v2.0) from https://github.com/MatrixFounder/Agentic-development.
The current handling of docs/TZ.md is inconsistent:
- Sometimes agents overwrite it completely (good for new tasks).
- Sometimes they append new requirements (bad — pollutes history).
- There are already some instructions in prompts (especially in 00_agent_development.md and 01_orchestrator.md) about copying completed TZ to docs/tasks/task-ID-name.md, but they are not strict enough, leading to variability.

GOAL:
Achieve STRICTLY UNIFIED behavior for all agents:
1. docs/TZ.md — EXCLUSIVELY for the CURRENT active task. Always overwrite completely when starting a new task. NEVER append.
2. Upon task completion OR before starting a new task in the same session:
   - Automatically archive the current TZ.md only if it represents a completed or meaningfully developed specification.
   - Generate unique filename: docs/tasks/task-<ID>-<slug>.md
     - ID: Incremental zero-padded number (scan existing files in docs/tasks/ and take next available: 001, 002, ...).
     - Slug: Short kebab-case description from task name (e.g., loyalty-system, fix-double-charging; max 30 chars).
   - Copy ENTIRE content of current TZ.md to this new file.
   - Add header: # Archived Task: <Full Task Name> — Date: YYYY-MM-DD
   - If docs/tasks/ folder does not exist — create it.
   - After archiving, overwrite docs/TZ.md with new content (or clear if no new task).
3. Intermediate refinements/clarifications within the SAME task MUST NOT trigger archiving — only overwrite TZ.md.
4. This must be mandatory and consistent across the entire pipeline.

TASK:
Analyze and update the following prompt files in /System/Agents/:

1. 00_agent_development.md (meta-prompt, included everywhere)
2. 01_orchestrator.md
3. 02_analyst_prompt.md
4. Optionally others if relevant (e.g., 03_tz_reviewer_prompt.md, 06_agent_planner.md, completion workflows)

STEPS TO FOLLOW:

1. First, recall/review the CURRENT content of each target file (you have access to the project).

2. For each file:
   - Identify existing instructions related to TZ.md, archiving, docs/tasks/.
   - Remove duplicates, conflicts, or weak wording.
   - Add or strengthen the UNIFIED RULES below.

UNIFIED RULES TO ENFORCE (add/strengthen in appropriate sections):

--- GLOBAL ARTEFACT HANDLING RULES (add to 00_agent_development.md and reference in others) ---
ARTEFACT HANDLING: TECHNICAL SPECIFICATION (TZ.md)

STRICT RULES (mandatory for all agents):
- docs/TZ.md contains ONLY the specification for the SINGLE CURRENT active task.
- Distinguish task phases:
  - "Clarification/refinement/iteration" = changes within the SAME task (e.g., "improve TZ", "add details to requirements", "fix inconsistencies after review").
    → Overwrite docs/TZ.md completely. DO NOT archive. Preserve as the evolving single document for the current task.
  - "New task" = explicitly different feature/bugfix/refactor (e.g., user says "now implement payments", "start new module", "next feature").
    → Archive current TZ.md first (if it contains meaningful content), then overwrite with new.
- When starting a NEW task:
  - If docs/TZ.md contains previous content → archive it first.
  - Then OVERWRITE docs/TZ.md completely with the new specification.
  - NEVER append to existing content.
- Archiving triggers (strict):
  - ONLY upon full task completion (after successful implementation, tests, and before final commit).
  - OR explicitly before starting a NEW task (when user input clearly indicates a new separate task).
  - Do NOT archive during early stages (analysis iterations, TZ review, clarifications).
- Archiving procedure (when triggered):
  1. Generate filename: docs/tasks/task-<ID>-<slug>.md
     - Determine ID: Check existing files in docs/tasks/, use next zero-padded number (001, 002, ...).
     - Slug: Derive from task name (kebab-case, max 30 chars, no spaces).
  2. Create the file with FULL content of current docs/TZ.md.
  3. Add header at top: # Archived Task: <Full Task Name> — Archived on: YYYY-MM-DD
  4. If folder docs/tasks/ does not exist — create it.
  5. Confirm archiving in your response (e.g., "Archived previous TZ to docs/tasks/task-003-loyalty-system.md").
- After archiving: Proceed with new TZ.md (overwrite completely).

--- END RULES ---

3. In 01_orchestrator.md:
   - Add explicit steps in pipeline:
     BEFORE launching Analyst for a potential new task:
       - Analyze user request: if clarification of current task → direct to Analyst for overwrite (no archiving).
       - If clear NEW task → archive current TZ.md (if meaningful), confirm, then proceed with new Analysis.
     AFTER task completion (Stage 5, before commit):
       - MANDATORY: Archive final TZ.md following the procedure.

4. In 02_analyst_prompt.md:
   - Explicitly: 
     - If refining existing TZ (clarification/iteration) → incorporate feedback and OVERWRITE completely. Do not archive.
     - If this is a new task → assume Orchestrator already archived previous TZ. Generate and overwrite docs/TZ.md fully.
     - Never reference or include old content from previous tasks.

OUTPUT FORMAT:
For each updated file:
1. File path (e.g., System/Agents/00_agent_development.md)
2. Diff-style patch (--- Original +++ Updated @@) showing only changed/added/removed sections.
3. If patch is complex — also provide the full new version of the modified section.

Finally:
- List all updated files.
- Summarize the changes.
- Confirm that the new rules prevent archiving of intermediate/unfinished TZ versions and ensure archiving only for completed tasks or at clear task boundaries.

Do not make other unrelated changes. Preserve existing style, structure, and tone of the original prompts.