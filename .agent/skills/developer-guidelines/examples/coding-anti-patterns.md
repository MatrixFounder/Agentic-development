# Coding Anti-Patterns: Before/After Examples

Real-world examples of common LLM mistakes during development. Each shows what goes wrong and the correct approach.

---

## 1. Drive-By Refactoring (Surgical Changes)

**Task:** "Fix the bug where empty emails crash the validator"

**Anti-Pattern:** Fixes the bug but also "improves" unrelated code

```diff
  def validate_user(user_data):
-     # Check email format
-     if not user_data.get('email'):
+     """Validate user data."""
+     email = user_data.get('email', '').strip()
+     
+     # Validate email
+     if not email:
          raise ValueError("Email required")
-     
-     # Basic email validation
-     if '@' not in user_data['email']:
+     if '@' not in email or '.' not in email.split('@')[1]:
          raise ValueError("Invalid email")
      
-     # Check username
-     if not user_data.get('username'):
+     # Validate username
+     username = user_data.get('username', '').strip()
+     if not username:
          raise ValueError("Username required")
+     if len(username) < 3:
+         raise ValueError("Username too short")
      
      return True
```

**Problems:** Improved email validation beyond the bug, added username validation nobody asked for, changed comments, added docstring.

**Correct:** Only fix the empty email crash.

```diff
  def validate_user(user_data):
      # Check email format
-     if not user_data.get('email'):
+     email = user_data.get('email', '')
+     if not email or not email.strip():
          raise ValueError("Email required")
      
      # Basic email validation
-     if '@' not in user_data['email']:
+     if '@' not in email:
          raise ValueError("Invalid email")
      
      # Check username
      if not user_data.get('username'):
          raise ValueError("Username required")
      
      return True
```

---

## 2. Speculative Features (Implementation Discipline)

**Task (from PLAN.md):** "Save user preferences to database"

**Anti-Pattern:** Adds caching, validation, merging, and notifications not in the plan.

```python
class PreferenceManager:
    def __init__(self, db, cache=None, validator=None):
        self.db = db
        self.cache = cache or InMemoryCache()
        self.validator = validator or DefaultValidator()
    
    def save(self, user_id: int, prefs: dict, 
             merge: bool = True, 
             validate: bool = True,
             notify: bool = False) -> bool:
        if validate:
            errors = self.validator.validate(prefs)
            if errors:
                raise ValidationError(errors)
        existing = self.get(user_id) if merge else {}
        if merge:
            existing.update(prefs)
            prefs = existing
        self.db.execute(
            "UPDATE users SET preferences = ? WHERE id = ?",
            (json.dumps(prefs), user_id)
        )
        if self.cache:
            self.cache.set(f"prefs:{user_id}", prefs)
        if notify:
            self.notify_preference_change(user_id, prefs)
        return True
```

**Problem:** PLAN.md says "save preferences". Developer added caching, validation, merge logic, and notifications — none of which are in the plan. This is speculative complexity.

**Correct:** Implement what the plan requires. If caching/validation are needed, they should be in the plan.

```python
def save_preferences(db, user_id: int, preferences: dict):
    """Save user preferences to database."""
    db.execute(
        "UPDATE users SET preferences = ? WHERE id = ?",
        (json.dumps(preferences), user_id)
    )
```

**Note:** If the ARCHITECTURE.md specifies a service layer with caching and validation, then implementing `PreferenceManager` with those features IS correct — the distinction is plan-driven vs. speculative.

---

## 3. Silent Interpretation (Think Before Implementing)

**Task:** "Make the search faster"

**Anti-Pattern:** Silently picks one interpretation and implements 200 lines.

```python
@lru_cache(maxsize=1000)
async def search(query: str) -> List[Result]:
    # 200 lines of caching + indexing + async optimization
    ...
```

**Correct:** Surface the ambiguity, present options with effort estimates.

```
"Make the search faster" could mean several things:

1. **Faster response time** (< 100ms instead of 500ms)
   - Add database indexes + cache frequent queries
   - Effort: ~2h

2. **Handle more concurrent searches** (throughput)
   - Async/await + connection pooling
   - Effort: ~4h

3. **Faster perceived speed** (UX)
   - Partial results + progressive loading
   - Effort: ~3h

Current: ~500ms for typical queries. 
Which aspect matters most?
```

**When to ask vs. decide:** This is a *critical ambiguity* (affects architecture and user-facing behavior). For implementation-level decisions (which caching library to use), apply professional judgment and document the choice.
