# Example: Trivial Task (Fast Path)

**User Request**: "Add a standard logger to the `PaymentService` class."

---

**Agent Thinking** (Internal):
- **Complexity**: TRIVIAL. Clear requirement, standard pattern, single component.
- **Action**: Fast Path. Skip ideation. Confirm pattern and go.

---

**Agent**:
"I'll add the standard logger to `PaymentService`.

Quick confirm — I see your project uses Python's built-in `logging`:
```python
import logging
logger = logging.getLogger(__name__)
```
Is this the correct pattern, or do you use a custom logger?"

**User**:
"Yes, that's right."

**Agent**:
"Got it. Adding logger to `PaymentService` with `__name__` scope. Proceeding to implementation."

---

**Why this works**:
- No ideation phase needed — requirement is unambiguous
- One confirmation question to verify the project convention
- No Design Doc — chat confirmation is sufficient for TRIVIAL
- Moves to implementation in 2 exchanges
