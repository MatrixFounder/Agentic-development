---
name: skill-update-memory
description: "Auto-update .AGENTS.md files based on code changes from git diff."
version: 1.0
---
# Update Memory Skill

## Purpose
Analyze code changes and propose updates to `.AGENTS.md` files to prevent "agent amnesia" in subsequent sessions.

## When to Use
- After code changes before commit
- As part of `09_agent_code_reviewer` verification
- In `04-update-docs` workflow

## Input
- `git diff --staged` output OR
- List of changed files from VCS

## Protocol

### Step 1: Filter Changes

**IGNORE these patterns (no action needed):**
```
*.lock                 # Package locks (package-lock.json, yarn.lock, etc.)
*.min.js, *.min.css    # Minified bundles
dist/, build/, out/    # Build outputs
node_modules/          # Dependencies
migrations/            # DB migrations (schema documented elsewhere)
*.md                   # Documentation (not source code)
*.json, *.yaml, *.toml # Config files (unless in src/)
__pycache__/, *.pyc    # Python cache
.git/                  # Git internals
tests/, __tests__/     # Test files (optional: can include if significant)
```

**FOCUS on these patterns:**
```
src/                   # Main source code
lib/                   # Library code
app/                   # Application code
packages/*/src/        # Monorepo packages
*.py, *.ts, *.js       # Source files (not in ignored dirs)
```

### Step 2: Identify Target .AGENTS.md

For each changed source file:
1. Look for `.AGENTS.md` in the **same directory**
2. If not found, traverse **up** to parent directories
3. If still not found, use **project root** `.AGENTS.md`

```
Changed: src/services/auth/login.py
Target:  src/services/auth/.AGENTS.md  (if exists)
         OR src/services/.AGENTS.md
         OR src/.AGENTS.md
         OR .AGENTS.md (root)
```

### Step 3: Classify Change Type

| Change Type | Action |
|-------------|--------|
| **New file** | Add new entry to `.AGENTS.md` |
| **Deleted file** | Mark as `(Deleted)` or remove entry |
| **Logic change** | Update function/class description |
| **Rename** | Update file reference |
| **Refactor (no logic change)** | Update structure, keep purpose |

### Step 4: Generate Update

**For new files:**
```markdown
### [new_file.py]
**Purpose:** [Infer from code/filename]
**Classes/Functions:**
- `ClassName` — [Brief description]
```

**For deleted files:**
```markdown
### [deleted_file.py] (Deleted)
*Removed in [task-ID/date]*
```

**For logic changes:**
```markdown
### [modified_file.py]
**Purpose:** [Updated purpose if changed]
**Classes/Functions:**
- `ClassName` — [Updated description]
  - `new_method()` — [New method added]
```

### Step 5: Preserve Human Knowledge

> [!IMPORTANT]
> **NEVER delete or modify sections marked as:**
> - `[Human Knowledge]`
> - `<!-- PRESERVE -->`
> - `**Note:**` blocks with architectural rationale

**Append-only mode** for manual annotations:
```markdown
### [file.py]
**Purpose:** Auto-generated description

**[Human Knowledge]:**
This uses a weird pattern because of legacy API constraints.
<!-- Agent: DO NOT MODIFY THIS SECTION -->
```

## Integration

### In Code Reviewer (09_agent_code_reviewer)
```
Before approving PR:
1. Run skill-update-memory
2. Check if .AGENTS.md updates are proposed
3. If yes, Developer MUST apply updates before merge
```

### In Update Docs Workflow (04-update-docs)
```
As part of documentation update:
1. Run git diff against last documented state
2. Apply skill-update-memory
3. Commit .AGENTS.md updates
```

## Example Session

```
Developer: "I added a new AuthService class"

Agent applies skill-update-memory:
1. git diff --staged shows:
   - A src/services/auth/auth_service.py
2. Filter: src/services → INCLUDE
3. Target: src/services/auth/.AGENTS.md (create if not exists)
4. Type: New file
5. Generate:
   ### auth_service.py
   **Purpose:** Authentication service handling login/logout
   **Classes:**
   - `AuthService` — Main authentication handler
     - `login(credentials)` — Validate user credentials
     - `logout(session)` — Invalidate session
6. Check: No [Human Knowledge] to preserve (new file)
7. Output: Proposed .AGENTS.md update
```

## Anti-Patterns

❌ **Don't** update .AGENTS.md for config changes  
❌ **Don't** delete manual annotations  
❌ **Don't** generate entries for test files (unless explicitly configured)  
❌ **Don't** process files in node_modules or dist
