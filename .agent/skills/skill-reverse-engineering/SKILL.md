---
name: skill-reverse-engineering
description: "Regenerate architecture documentation from codebase analysis."
version: 1.0
---
# Reverse Engineering Skill

## Purpose
Recover the mental model of a project from its codebase when documentation is outdated or missing.

## When to Use
- Documentation-code mismatch detected
- New team member onboarding
- Post-"quick fix" marathon cleanup
- Legacy code takeover

## Strategy: Iterative Analysis

> [!IMPORTANT]
> **Context Overflow Mitigation**: Never try to analyze entire codebase at once.
> Use folder-by-folder approach with local summaries.

### Phase 1: Directory Scan
```
1. List top-level source directories
2. For each directory:
   a. Count files and estimate complexity
   b. Identify dominant language/framework
   c. Note any existing .AGENTS.md
```

### Phase 2: Local Summaries (Per-Directory)
```
For each significant directory:
1. Read existing .AGENTS.md (if any)
2. List files and their approximate sizes
3. Sample 2-3 representative files
4. Generate LOCAL summary:
   - Purpose of this directory
   - Key classes/modules
   - Dependencies (imports from other dirs)
   - External integrations
```

**Output format:**
```markdown
## src/services/auth/
**Purpose:** Authentication and authorization layer
**Key Files:**
- `auth_service.py` — Main service class
- `jwt_handler.py` — Token management
**Dependencies:** `src/models/user`, `src/utils/crypto`
**External:** Firebase Auth SDK
```

### Phase 3: Global Synthesis
```
1. Collect all local summaries
2. Identify cross-cutting concerns
3. Map dependency graph
4. Generate/update docs/ARCHITECTURE.md
```

## Output Artifacts

### 1. ARCHITECTURE.md Update

Generate or update these sections:
```markdown
## Directory Structure
[Tree with purpose annotations]

## Component Map
[Which directories form logical components]

## Data Flow
[How data moves between components]

## External Dependencies
[Third-party services and libraries]
```

### 2. KNOWN_ISSUES.md Updates

Identify and document:
```markdown
## Hidden Knowledge Discovered

### [Issue Title]
**Location:** `src/services/auth/legacy_adapter.py`
**Discovery:** Found during reverse engineering
**Description:** Uses deprecated API due to compatibility constraints
**Impact:** Cannot upgrade to v2 auth without migration
```

**Look for these patterns:**
- `TODO:`, `FIXME:`, `HACK:`, `XXX:` comments
- Unusual code patterns with no explanation
- Disabled tests or `@skip` decorators
- Environment-specific conditionals
- Magic numbers without constants

## Protocol

### Step 1: Assess Scope
```
What needs reverse engineering?
- [ ] Single directory
- [ ] Full project
- [ ] Specific component
```

### Step 2: Gather Existing Context
```
1. Read docs/ARCHITECTURE.md (current state)
2. Read docs/KNOWN_ISSUES.md
3. Read root .AGENTS.md
4. Check git log for recent major changes
```

### Step 3: Execute Iterative Analysis
```
For each directory (depth-first):
1. Generate local summary
2. Store in working memory
3. Move to next directory
4. After all dirs: synthesize global view
```

### Step 4: Diff Against Documentation
```
Compare generated architecture with existing docs:
- New components not documented?
- Documented components that no longer exist?
- Structural changes?
```

### Step 5: Propose Updates
```
Output:
1. Proposed ARCHITECTURE.md changes (diff format)
2. New KNOWN_ISSUES.md entries
3. Suggested .AGENTS.md creations
```

## Human Knowledge Preservation

> [!CAUTION]
> **Never overwrite architectural rationale written by humans.**

**Protected patterns:**
```markdown
<!-- HUMAN KNOWLEDGE -->
...
<!-- END HUMAN KNOWLEDGE -->

> **Design Decision:** [rationale]

**Historical Context:** [explanation]
```

**Merge strategy:**
```
IF section exists with human annotation:
  APPEND new information below
  PRESERVE human section intact
ELSE:
  REPLACE with generated content
```

## Example Session

```
User: "The ARCHITECTURE.md is outdated, please reverse-engineer from code"

Agent applies skill-reverse-engineering:

Phase 1: Directory Scan
- src/: 4 subdirs, ~50 files
- lib/: 2 subdirs, utilities
- tests/: skip (not source)

Phase 2: Local Summaries
- src/api/: REST endpoints, Express.js
- src/services/: Business logic, 3 services
- src/models/: Data models, TypeORM entities
- src/utils/: Shared utilities

Phase 3: Synthesis
- Layered architecture: API → Services → Models
- External: PostgreSQL, Redis, S3
- Hidden: Legacy auth adapter (HACK comment found)

Output:
1. ARCHITECTURE.md diff showing new structure
2. KNOWN_ISSUES.md: "Legacy auth adapter needs migration"
3. Recommend .AGENTS.md for src/services/auth/
```

## Integration

### With skill-update-memory
After reverse engineering:
1. Generate missing `.AGENTS.md` files
2. Use `skill-update-memory` format for entries

### With 04-update-docs Workflow
```
If docs drift detected:
1. Run skill-reverse-engineering
2. Generate proposed updates
3. Request human review before applying
```

## Anti-Patterns

❌ **Don't** read all files into context at once  
❌ **Don't** delete human-written architectural decisions  
❌ **Don't** generate architecture from test files  
❌ **Don't** ignore existing documentation completely  
❌ **Don't** assume all code is intentional (look for TODOs)
