---
description: Start a feature using the standard Stub-First pipeline
---
# Workflow: Base Stub-First Development

**Description:**  
Core pipeline with Stub-First and TDD. Used as foundation for others.

**Steps:**

1. Call /analyst-tz               # Technical Specification
2. Call /tz-review
3. Call /architect-design
4. Call /architecture-review
5. Call /planner-stub-first      # Enforce Stub → Impl pairs
6. Call /plan-review
7. For each task pair:
   - Call /developer-stub
   - Call /code-review-stub
   - Call /developer-impl
   - Call /code-review-final
8. Final validation and commit preparation
