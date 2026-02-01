# Example: Trivial Task (Fast Path)

**User Request**: "Add a standard logger to the `PaymentService` class."

**Agent Thinking** (Internal):
*   **Complexity**: TRIVIAL. Clear requirement, standard pattern.
*   **Action**: Fast Path. No deep research needed. Confirm and go.

**Agent**:
"I'll add the standard logger to `PaymentService`.

Just to confirm the pattern:
```python
import logging
logger = logging.getLogger(__name__)
```
Is this the correct standard for your project?"

**User**:
"Yes."

**Agent**:
"Great. Proceeding with implementation."
