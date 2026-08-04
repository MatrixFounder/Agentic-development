---
name: skill-task-model
description: Standards for Technical Specifications (TASK) and Use Cases.
tier: 1
version: 1.1
---

# TASK Model & Examples

**Purpose**: Defines the structure and quality standards for Technical Specifications to ensure unambiguous implementation.

## 1. Red Flags (Anti-Rationalization)
**STOP if you are thinking:**
- "I'll figure out the edge cases while coding" -> **WRONG**. define Alternative Scenarios NOW.
- "Acceptance Criteria: 'It works'" -> **WRONG**. Criteria must be binary (Pass/Fail) and specific.
- "I don't need actors, it's just a backend job" -> **WRONG**. "System" is an actor. "Cron Job" is an actor.

## 2. TASK Structure Rules
- **Meta Information:** Section 0 MUST include Task ID and Slug.
- **Use Cases:** Must be structured with Actors, Preconditions, Main Scenario, Alternative Scenarios, Postconditions, and Acceptance Criteria.
- **Validation:** Criteria must be verifiable.

## 3. Examples

### Example of a Good Use Case
> [!TIP]
> See `examples/good_use_case.md` for a complete, structured example. Its acceptance
> criteria are plain bullets: severity is a named value, never a glyph
> (`documentation-standards` §5.5 rule 5).

### Example of a Bad Use Case
> [!TIP]
> See `examples/bad_use_case.md` for what NOT to do.

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "Writing scenarios takes too long" | Rewriting code because of missed edge cases takes 3x longer. |
| "It's obvious what happens" | Not to the Code Reviewer, and not to you in two weeks. |

## 4. Resources
- `examples/`: Reference use cases.
