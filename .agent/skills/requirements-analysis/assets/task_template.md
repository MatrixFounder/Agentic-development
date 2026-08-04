
<!--
  REGISTER. Write in whichever language the project uses; nothing in this pipeline changes that
  choice. In that language, apply the authoring contract BEFORE the first sentence:
  `.agent/skills/artifact-formalizer/references/authoring-contract.md` — six per-sentence tests and
  the licensed statement forms. It is the single source for them, so this template does not restate
  the rules. Audit with `artifact-formalizer/scripts/scan_register.py`.
-->

### 0. Meta Information (MANDATORY)
- **Task ID:** Extract from existing tasks (e.g. 002 if 001 exists) or use 001 for new project. **REQUIRED.**
- **Slug:** Short kebab-case name (e.g. `user-auth`). **REQUIRED.**
- **WARNING:** Do not skip this section. Archiving reads the Task ID and Slug from here; without them `skill-archive-task` cannot name the archive file.

### 1. General Description
- Brief description of the task based on the general statement from the user
- Goal of development
- Connection with existing system (if applicable)

### 2. List of Use Cases

Create a list of Use Cases. Highlight which are new and which are modifications of existing ones.

For each use case indicate:

#### 2.1. Use Case Name
Short, clear name (e.g., "New User Registration")

#### 2.2. Actors
Who participates in this use case:
- User (specifying role if important)
- System
- External systems (if any)

#### 2.3. Preconditions
What must be fulfilled before the use case starts

#### 2.4. Main Scenario
Step-by-step description of successful execution. If modifying an existing Use Case, indicate which steps exist, which are added, changed, or deleted:
1. Actor performs action X
2. System responds Y
3. ...

#### 2.5. Alternative Scenarios
Description of deviations from the main scenario:
- **Alternative 1:** What happens if...
  1. Step
  2. Step
- **Alternative 2:** ...

#### 2.6. Postconditions
What must be achieved after successful execution

#### 2.7. Acceptance Criteria
Specific, verifiable criteria. One line each, no severity glyph:
- Criterion 1
- Criterion 2
- Criterion 3

### 3. Non-functional Requirements (if applicable)
- Performance
- Security
- Scalability
- Compatibility

### 4. Constraints and Assumptions
- Technical constraints
- Business constraints
- Assumptions made during TASK creation

### 5. Open Questions
List of questions requiring clarification from the user
