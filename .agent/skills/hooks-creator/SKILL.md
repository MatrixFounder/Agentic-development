---
name: hooks-creator
description: Use when the user wants to customize Gemini CLI behavior using hooks (events, blockers, loggers).
tier: 2
version: 1.1
---
# Hooks Creator

**Purpose**: Create robust, secure, and compliant Gemini CLI hooks that intercept and customize the agent's lifecycle (e.g., blocking tools, injecting context, logging).

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I'll use `grep` to parse JSON in Bash because it's faster" -> **WRONG**. This is a security vulnerability. You **MUST** use `jq`.
- "I'll just print a debug message to stdout" -> **WRONG**. This breaks JSON parsing. **ALL** logs must go to `stderr`.
- "I can skip the dependency check" -> **WRONG**. Scripts will fail silently. Always check for `jq` or node modules.
- "I'll use `exit 1` for a denial" -> **WRONG**. Use `exit 0` with `{"decision": "deny"}` for structured feedback, or `exit 2` for system errors.

## 2. Capabilities
- Generate **Bash** hooks for simple logic (using `jq`).
- Generate **Node.js** hooks for complex logic or heavy JSON processing.
- Configure `settings.json` with correct matchers and event types.
- Validate security and performance best practices.

## 3. Execution Mode
- **Mode**: `prompt-first`
- **Why this mode**: the skill ships no `scripts/` of its own — it authors hook scripts for the user's project. Choosing the event, the language (Bash vs Node.js) and the matcher is judgement over the request plus `references/`; the deterministic work lives in the generated hook, not here.
- **Script Contract**: none of its own. The contract the *generated* hook must meet is §5 Phase 2: strict JSON on `stdout`, logs on `stderr`, a `jq` dependency check, exit `2` on system failure. The I/O schemas and the exit-code table are in `references/reference.md`.

## 4. Safety Boundaries (SECURITY CRITICAL)

> [!WARNING]
> **SECURITY CRITICAL:** 
> *   **Strict JSON**: Printing to `stdout` breaks the CLI. Use `stderr` for logs.
> *   **Injection Risks**: BASH hooks MUST use `jq`. Never use `grep` on raw input.
> *   **Dependency Checks**: Scripts MUST fail gracefully (exit 2) if deps like `jq` are missing.

- **Scope**: this skill authors hook scripts and a `settings.json` snippet; enabling them is the user's step — Phase 3 hands over `chmod +x` and the pipe test instead of running them.
- **Blast radius**: a generated hook runs on every matching event, so prefer a specific `matcher` over `*` (Phase 3.1). Exit `2` aborts the tool or the turn, so reserve it for a missing dependency or a parse failure and express a policy denial as exit `0` plus `{"decision": "deny"}` (`references/reference.md` § Global hook mechanics).

## 5. Instruction Protocol

### Phase 1: Analyze & Clarify
1.  **Identify the Event**: Map user intent to the correct Life Cycle Event.
    - *Example*: "Stop me from committing secrets" -> `BeforeTool` (triggered on `write_file`).
    - *Example*: "Add git history to context" -> `BeforeAgent` (or `SessionStart`).
2.  **Analyze Clarity (Fast Path)**:
    - **Clear Request**: If the user provides specific intent (e.g., "Block 'rm' commands"), **SKIP clarification** and proceed to implementation.
    - **Ambiguous Request**: If vague (e.g., "Make it safer"), ask **ONE** clarifying question: "Do you want to block specific tools or scan content?"
3.  **Select Implementation**:
    - **Bash**: For simple checks (grepping specific patterns, file existence).
    - **Node.js**: For logic requiring array manipulation, complex JSON, or async calls.

### Phase 2: Implementation (The Golden Rules)
1.  **Strict JSON Output**:
    - The script **MUST NOT** echo anything to `stdout` except the final JSON object.
    - Redirect all intermediate logs to `stderr` (e.g., `echo "Debug" >&2`).
2.  **Dependency Checks (MANDATORY)**:
    - **Bash**: Verify `jq` availability AND functionality. 
        - Pattern: `command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 2; }`
3.  **Security Sanitization**:
    - Never pass raw `input` to `eval` or `exec`.
    - Use `jq` to extract fields safely before processing.

### Phase 3: Configuration & Validation Evidence
1.  **Generate `settings.json` snippet**:
    - Use specific **matchers** (e.g., `write_file|replace_...`) instead of `*` to optimize performance.
    - Ensure `type` is `"command"`.
2.  **Verification Recommendations**:
    - Tell the user to run `chmod +x <script>`.
    - Advise testing with piped JSON: `cat test.json | ./hook.sh`.
    - **Pass criteria**: `out=$(mktemp); ./hook.sh < test.json > "$out"; echo "exit=$?"` — `0` on every normal path, `2` only on the system-block path (missing dependency, unparseable input). On each exit-0 run, `jq -se 'length == 1 and (.[0] | type == "object")' "$out" >/dev/null` proves that `stdout` carries exactly one JSON object; on the exit-2 path `stdout` is empty by design. (`jq -e .` or `jq -e 'type == "object"'` would not: `-e` judges only the last output, so both exit 0 on two concatenated objects.) A `mktemp` file, not a fixed `/tmp` name, keeps another user's link out of the path.
    - **Worked example**: `in=$(mktemp); out=$(mktemp); printf '{"tool_input":{"content":"API_TOKEN=abc"}}' > "$in"; bash examples/security_gate.sh < "$in" > "$out"; echo "exit=$?"` — `exit=0`, `"decision": "deny"` in `$out`, `Blocked secret commitment` on `stderr`.

## 6. Canonical Resources (Source of Truth)
You **MUST** read these files for API details:
- `references/Gemini CLI Hooks.md` (Core Concepts)
- `references/reference.md` (JSON Schema & Exit Codes)
- `references/best-practices.md` (Security)

## 7. Examples (Few-Shot)

### 1. Security Gate (Bash)
*See `examples/security_gate.sh` for full implementation.*
**Use when**: Blocking unsafe content or tools.

### 2. Tool Filtering (Node.js)
*See `examples/tool_filter.js` for full implementation.*
**Use when**: Restricting tools based on user prompt/intent.

### 3. Settings Configuration
*See `examples/settings_snippet.json`.*

### 4. Simple Logger (Bash)
*See `examples/log_tools.sh`.*
**Use when**: Debugging or auditing tool usage.

### 5. Context Injection (Bash)
*See `examples/inject_context.sh`.*
**Use when**: Adding environment data (Git, DB) to agent context.

### 6. Response Validation (Node.js)
*See `examples/validate_response.js`.*
**Use when**: Enforcing quality checks (e.g., "Must include Summary:") before showing output.

## 8. Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "I'll skip the `jq` check" | Systems without `jq` will crash unpredictably. |
| "Users know not to `echo`" | No they don't. You must enforce it in the code. |
| "I'll use Python" | Node.js/Bash are preferred for minimal runtime deps, but Python is allowed if requested. |
