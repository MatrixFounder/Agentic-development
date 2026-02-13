---
name: hooks-creator
description: Use when the user wants to customize Gemini CLI behavior using hooks (events, blockers, loggers).
tier: 2
version: 1.0
---
# Hooks Creator

**Purpose**: Create robust, secure, and compliant Gemini CLI hooks that intercept and customize the agent's lifecycle (e.g., blocking tools, injecting context, logging).

> [!WARNING]
> **SECURITY CRITICAL:** 
> *   **Strict JSON**: Printing to `stdout` breaks the CLI. Use `stderr` for logs.
> *   **Injection Risks**: BASH hooks MUST use `jq`. Never use `grep` on raw input.
> *   **Dependency Checks**: Scripts MUST fail gracefully (exit 2) if deps like `jq` are missing.

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I'll use `grep` to parse JSON in Bash because it's faster" -> **WRONG**. This is a security vulnerability. You **MUST** use `jq`.
- "I'll just print a debug message to stdout" -> **WRONG**. This breaks JSON parsing. **ALL** logs must go to `stderr`.
- "I can skip the dependency check" -> **WRONG**. Scripts will fail silently. functionality. Always check for `jq` or node modules.
- "I'll use `exit 1` for a denial" -> **WRONG**. Use `exit 0` with `{"decision": "deny"}` for structured feedback, or `exit 2` for system errors.

## 2. Capabilities
- Generate **Bash** hooks for simple logic (using `jq`).
- Generate **Node.js** hooks for complex logic or heavy JSON processing.
- Configure `settings.json` with correct matchers and event types.
- Validate security and performance best practices.

## 3. Instruction Protocol

### Phase 1: Analyze & Clarify
1.  **Identify the Event**: Map user intent to the correct Life Cycle Event.
    - *Example*: "Stop me from committing secrets" -> `BeforeTool` (triggered on `write_file`).
    - *Example*: "Add git history to context" -> `BeforeAgent` (or `SessionStart`).
    - *Example*: "Add git history to context" -> `BeforeAgent` (or `SessionStart`).
2.  **Analyize Clarity (Fast Path)**:
    - **Clear Request**: If the user provides specific intent (e.g., "Block 'rm' commands"), **SKIP clarification** and proceed to implementation.
    - **Ambiguous Request**: If vague (e.g., "Make it safer"), ask **ONE** clarifying question: "Do you want to block specific tools or scan content?"
3.  **Select Implementation**:
    - **Bash**: For simple checks (grepping specific patterns, file existence).
    - **Node.js**: For logic requiring array manipulation, complex JSON, or async calls.

### Phase 2: Implementation (The Golden Rules)
1.  **Strict JSON Output**:
    - The script **MUST NOT** echo anything to `stdout` except the final JSON object.
    - Redirect all intermediate logs to `stderr` (e.g., `echo "Debug" >&2`).
    - Redirect all intermediate logs to `stderr` (e.g., `echo "Debug" >&2`).
2.  **Dependency Checks (MANDATORY)**:
    - **Bash**: Verify `jq` availability AND functionality. 
        - Pattern: `command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 2; }`
3.  **Security Sanitization**:
    - Never pass raw `input` to `eval` or `exec`.
    - Use `jq` to extract fields safely before processing.

### Phase 3: Configuration & Verification
1.  **Generate `settings.json` snippet**:
    - Use specific **matchers** (e.g., `write_file|replace_...`) instead of `*` to optimize performance.
    - Ensure `type` is `"command"`.
2.  **Verification Recommendations**:
    - Tell the user to run `chmod +x <script>`.
    - Advise testing with piped JSON: `cat test.json | ./hook.sh`.

## 4. Canonical Resources (Source of Truth)
You **MUST** read these files for API details:
- `references/Gemini CLI Hooks.md` (Core Concepts)
- `references/reference.md` (JSON Schema & Exit Codes)
- `references/best-practices.md` (Security)

## 5. Examples (Few-Shot)

### 1. Security Gate (Bash)
*See `examples/security_gate.sh` for full implementation.*
**Use when**: Blocking unsafe content or tools.
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

## 6. Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "I'll skip the `jq` check" | Systems without `jq` will crash unpredictably. |
| "Users know not to `echo`" | No they don't. You must enforce it in the code. |
| "I'll use Python" | Node.js/Bash are preferred for minimal runtime deps, but Python is allowed if requested. |
