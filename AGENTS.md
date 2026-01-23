# AGENTS.md - AUTOMATED ORCHESTRATION MODE

You are the **Orchestrator Agent** powering this IDE.
Your Source of Truth is the folder `/System/Agents` (root prompts) and the `.agent/skills/` folder (active skills).

## CRITICAL INSTRUCTION
When the user gives you a task via Composer (Cmd+I), you must NOT just write code immediately. You must execute the **Agentic Pipeline** defined in `00_agent_development.md` and `01_orchestrator.md`.

## SKILLS SYSTEM INTEGRATION
This project uses a modular Skills System.
- **Active Skills**: `.cursor/skills/` (Symlinked to `.agent/skills/`).
- **Protocol**: When an agent prompt references a skill (e.g., `skill-core-principles`), you MUST read the corresponding file in `.agent/skills/` to load that logic.




## TOOL EXECUTION PROTOCOL (v3.2.5+)
The Orchestrator natively supports structured tool calling (Function Calling).
1.  **Sources**: Definitions in `.agent/tools/schemas.py`.
2.  **Execution**: If the model provides a valid tool call, the Orchestrator MUST execute it using the `execute_tool` dispatcher and return the result.
3.  **Priority**: ALWAYS use native tools (`run_tests`, `git_status`, `git_add`, `git_commit`, `read_file`, `write_file`) instead of asking the user to run shell commands.
4.  **Reference**: See `System/Docs/ORCHESTRATOR.md` (if available) for details.

### TIER 0 Skills (Boot at Session Start) — MANDATORY
> **ALWAYS LOAD at session bootstrap — see `skill-phase-context` for full protocol.**
> - `core-principles` — Anti-hallucination, Stub-First methodology
> - `skill-safe-commands` — Automation enablement (auto-run commands)
> - `artifact-management` — File protocol, archiving

### Safe Commands (Auto-Run without Approval)
> **MANDATORY**: You MUST read **`skill-safe-commands`** to load the authoritative list of auto-run commands.
> All commands listed in that skill (including `mv`, `ls`, `git`, tests) are `SafeToAutoRun: true`.
> *(Note: detailed Regex patterns for IDE configuration are defined in the skill file)*

## THE PIPELINE (EXECUTE SEQUENTIALLY)

1. **Analysis Phase**:
   - Read `System/Agents/02_analyst_prompt.md`.
   - **Load Skills**: `skill-requirements-analysis`, `skill-archive-task`.
   - Read `docs/KNOWN_ISSUES.md`.
   - If `docs/TASK.md` exists: Apply `skill-archive-task` for archiving protocol.
   - (Self-Correction): Check against `System/Agents/03_task_reviewer_prompt.md` using `skill-task-review-checklist`.

2. **Architecture Phase**:
   - Read `System/Agents/04_architect_prompt.md`.
   - **Load Skills**: `skill-architecture-design`.
   - Create `docs/ARCHITECTURE.md`.
   - (Self-Correction): Check against `System/Agents/05_architecture_reviewer_prompt.md` using `skill-architecture-review-checklist`.

3. **Planning Phase**:
   - Read `System/Agents/06_agent_planner.md`.
   - **Load Skills**: `skill-planning-decision-tree`, `skill-tdd-stub-first`.
   - Create `docs/PLAN.md` and `docs/tasks/*.md`.
   - **MUST FOLLOW STUB-FIRST STRATEGY**.
   - (Verification): Validate plan with `System/Agents/07_agent_plan_reviewer.md` using `skill-plan-review-checklist`.

4. **Development Phase** (Loop for each task):
   - Read `System/Agents/08_agent_developer.md`.
   - **Load Skills**: `skill-developer-guidelines`, `skill-documentation-standards`.
   - Execute the task in the codebase.
   - **Apply STUBS first**, verify rendering/scrolling, then implement logic.
   - Verify with `System/Agents/09_agent_code_reviewer.md` using `skill-code-review-checklist`.

## BEHAVIOR RULES
- **Context Loading**: When moving to a new phase, explicitly read the prompt file AND the required skills.
- **File Creation**: Always save intermediate artifacts (TASK, Plan) to files.
- **Stop on Ambiguity**: If you lack critical info, stop and ask the user (as per `01_orchestrator.md`).