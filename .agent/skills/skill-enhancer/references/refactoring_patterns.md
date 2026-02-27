# Deep Refactoring Patterns

Turn "Passive Reference" into "Motivated Algorithms" using the graduated approach.

## Pattern 1: The "Suggested" Trap → Graduated Fix

**Bad (Passive):**
> It is suggested that you check the file for errors before proceeding.

**Okay (Imperative-Only, missing motivation):**
> You MUST check the file for errors.

**Good (Graduated — imperative + why):**
> You MUST check the file for errors before proceeding — undetected errors
> compound silently and cause hard-to-debug failures downstream.

## Pattern 2: The "Ambiguous Can" → Context-Dependent Fix

**Bad (Passive):**
> You can use the `--force` flag if needed.

**Good (Graduated):**
> **IF** the command fails with `EEXIST`:
>    Run with `--force` — this is safe because the file will be overwritten with the correct version.
> **ELSE**:
>    Do not use `--force` — it bypasses safety checks that prevent data loss.

## Pattern 3: The "Hidden Decision"

**Bad (Passive):**
> Ensure the configuration is correct.

**Good (Imperative):**
> Verify `config.yaml`:
> *   `version` MUST be `2`
> *   `debug` MUST be `false`

## Pattern 4: The "Text Logic" Trap (Script-First)

**Bad (Text Algorithm):**
> 1. Scan the directory for files.
> 2. For each file, read line 1.
> 3. If line 1 starts with "#", move it to /done.

**Good (Script Tool):**
> Run the organizer script:
> `python3 scripts/organize_files.py --target ./`

**Why?**
*   Text loops > 5 lines satisfy the "Laziness Threshold". Agents give up.
*   Scripts are deterministic.

## Pattern 5: Prompt-Only -> Hybrid Contract

**Bad (Unbounded Prompt):**
> Analyze the repo, modify everything needed, and validate.

**Good (Hybrid):**
> 1. Use prompt reasoning to define the change plan and scope.
> 2. Run deterministic scripts for file mutation and checks.
> 3. Summarize script evidence and decide follow-up actions.

**Why?**
*   Keeps reasoning flexible while making execution reproducible.
*   Produces machine-verifiable evidence.

## Pattern 6: Ad-Hoc Script -> Governed Script

**Bad (Ad-Hoc):**
> Run `python scripts/tool.py`.

**Good (Governed Contract):**
> - Command: `python3 scripts/tool.py --target <path> --dry-run`
> - Inputs: explicit args only.
> - Outputs: deterministic report + exit code.
> - Failures: non-zero exit with actionable error.

**Why?**
*   Makes behavior testable and CI-compatible.
*   Reduces hidden side effects.

## Pattern 7: Unsafe Mutation -> Scoped Mutation

**Bad (Wide Scope):**
> Rename files across the project.

**Good (Scoped):**
> 1. Require explicit scope (`--path`, `--module`, or target list).
> 2. Exclude non-target/system directories by default.
> 3. Require explicit opt-in for destructive operations.

**Why?**
*   Prevents accidental framework or infrastructure changes.
*   Makes rollback and review practical.

## Pattern 8: Passive Description → Pushy Description

**Bad (Passive):**
> description: Guide for building dashboards.

**Good (Pushy):**
> description: Use when building dashboards, data visualization, metrics display, or showing structured data. Apply even if the user doesn't explicitly ask for a 'dashboard'.
