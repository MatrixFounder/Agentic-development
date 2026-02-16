# Django Security Quick-Reference

> Condensed from `References/security-best-practices/references/python-django-web-server-security.md`.
> Load this when generating or reviewing Django code.

## LLM Anti-Patterns (DO NOT recommend these)

- ❌ Using `mark_safe()` on user-derived content — direct XSS vector.
  - ✅ Let Django's auto-escaping handle it; use `mark_safe()` only on developer-controlled strings.
- ❌ Using `|safe` template filter on variables that may contain user input.
- ❌ Setting `DEBUG = True` in production — exposes settings, SQL queries, tracebacks.
- ❌ Setting `ALLOWED_HOSTS = ['*']` in production — enables Host header attacks.
- ❌ Using `.extra()` or `.raw()` with string formatting for user input — SQL injection.
  - ✅ Use ORM queries, or `params=[]` with `.raw()` / `.extra()`.
- ❌ Recommending `SESSION_COOKIE_SECURE = True` unconditionally — breaks local HTTP dev.
  - ✅ Make conditional: `SESSION_COOKIE_SECURE = not DEBUG`
- ❌ Adding random domains to `CSRF_TRUSTED_ORIGINS` — weakens CSRF protection.

## Critical Grep Patterns

```
# XSS
mark_safe(            # Raw HTML — verify not user-derived
|safe                 # Template filter — verify trusted source
{% autoescape off %}  # Disables escaping block — very dangerous
format_html(          # Safe alternative to mark_safe with interpolation

# SQL Injection
.extra(               # Raw SQL fragments — must use params=[]
.raw(                 # Raw SQL — must use params=[]
RawSQL(               # Raw SQL expression — must parameterize
cursor.execute(       # Direct SQL — must use %s placeholders + params
connection.cursor()   # Direct DB access — verify parameterized

# Auth & Session
@login_required       # Verify all protected views
@permission_required  # Verify correct permission strings
LoginRequiredMixin    # CBV equivalent — verify ordering
AUTHENTICATION_BACKENDS  # Custom backends — audit carefully

# CSRF
@csrf_exempt          # Intentional bypass — verify justified
CSRF_TRUSTED_ORIGINS  # Must be minimal allowlist
csrf_token            # Verify present in all POST forms

# Configuration
DEBUG =               # Must be False in production
ALLOWED_HOSTS         # Must not be ['*'] in production
SECRET_KEY            # Must not be hardcoded / committed
SECURE_PROXY_SSL_HEADER  # Must match actual proxy header exactly

# File handling
FileSystemStorage     # Verify upload path is outside webroot
handle_uploaded_file  # Verify size/type validation
MEDIA_ROOT            # Verify not served with directory listing
```

## Framework-Specific Edge Cases

1. **`SECURE_PROXY_SSL_HEADER`** — Must exactly match what your proxy sends. Wrong header name = attacker can spoof HTTPS detection.
2. **`mark_safe()` + `format_html()`** — `format_html()` is the safe alternative; it escapes arguments before marking result safe. Always prefer it.
3. **`{% autoescape off %}` blocks** — Disable Django's auto-escaping entirely. Every variable inside becomes XSS-capable.
4. **`.extra()` deprecation path** — Still functional but dangerous; ORM expressions (`F()`, `Q()`, `Subquery()`) are safer alternatives.
5. **Middleware ordering matters** — `SecurityMiddleware` must be first; `SessionMiddleware` must come before `AuthenticationMiddleware` (auth reads from session).
6. **`CSRF_TRUSTED_ORIGINS`** (Django 4.0+) — Required when frontend and backend are on different origins. Must be exact scheme+host, not wildcards.
7. **Admin site exposure** — `/admin/` is auto-registered. In production, restrict access by IP or use non-obvious URL prefix.
8. **`JsonResponse` with user data** — Safe for body XSS (JSON-encoded), but verify `Content-Type: application/json` is set (it is by default).

## Recommended Audit Order

1. `DEBUG`/`ALLOWED_HOSTS`/`SECRET_KEY` settings in production
2. `mark_safe()` / `|safe` / `{% autoescape off %}` with user input
3. `.extra()` / `.raw()` / `cursor.execute()` SQL injection
4. CSRF coverage (`@csrf_exempt` minimized, tokens in forms)
5. Auth decorators on all protected views
6. File upload validation and storage location
7. Cookie flags (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`)
8. Middleware ordering and security middleware presence
9. Admin site access restrictions
