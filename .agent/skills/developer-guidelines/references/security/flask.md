# Flask Security Quick-Reference

> Condensed from `References/security-best-practices/references/python-flask-web-server-security.md`.
> Load this when generating or reviewing Flask code.

## LLM Anti-Patterns (DO NOT recommend these)

- ❌ Setting `SESSION_COOKIE_SECURE = True` unconditionally — breaks local dev over HTTP.
  - ✅ Use env-conditional: `app.config['SESSION_COOKIE_SECURE'] = not app.debug` (or check explicit `PROD` env var).
- ❌ Recommending HSTS in app code — breaks non-TLS setups; belongs at reverse proxy/edge.
- ❌ Using `safe_join()` without considering edge cases — it rejects `..` traversal correctly, but CVE-2025-66221 shows it can be bypassed via Windows device names (`CON`, `NUL`, etc.).
  - ✅ Use `safe_join()` + update Werkzeug to patched version. For defense-in-depth, verify `os.path.realpath(result).startswith(os.path.realpath(base_dir))`.
- ❌ Storing secrets in `app.config` from env without fail-closed check.
  - ✅ `SECRET_KEY = os.environ['SECRET_KEY']` (KeyError on missing) not `.get()` with fallback.
- ❌ Using `SECRET_KEY_FALLBACKS` for routine rotation — it keeps old keys valid indefinitely.

## Critical Grep Patterns

```
# XSS / Template injection
Markup(              # Raw HTML bypass — trace input source
|safe                # Jinja2 safe filter — verify trusted source
render_template_string(  # SSTI if user input reaches template

# Auth & Session
@login_required      # Verify ALL sensitive routes have this
SESSION_COOKIE_SECURE # Must be conditional on environment
SECRET_KEY           # Must not be hardcoded or weak

# CSRF
CSRFProtect          # flask-wtf — verify it's initialized
csrf.exempt          # Intentional bypass — verify justified
WTF_CSRF_ENABLED     # Must be True in production

# File handling
send_file(           # Verify path is not user-controlled
send_from_directory( # Verify directory is constrained
safe_join(           # NOT sufficient alone — see anti-patterns

# Injection
subprocess           # OS command injection risk
os.system(           # Never with user input
db.engine.execute(   # Raw SQL — must use parameterized queries
text(                # SQLAlchemy text() — verify bound params

# Deployment
app.run(debug=True   # Must not reach production
FLASK_DEBUG=1        # Must not be set in production env
```

## Framework-Specific Edge Cases

1. **`safe_join` edge cases** — It correctly prevents `..` traversal, but CVE-2025-66221 found a bypass via Windows device names. Always update Werkzeug and consider `os.path.realpath` containment check as defense-in-depth.
2. **`SECRET_KEY_FALLBACKS`** (Flask 2.3+) — Keeps old signing keys valid. Do NOT use for routine rotation; use only during migration windows.
3. **`Markup()` class** — Marks strings as "safe" HTML. If user input flows into `Markup()`, it's XSS.
4. **`flask-wtf` CSRF** — Must call `CSRFProtect(app)` AND include `{{ csrf_token() }}` in forms. AJAX needs `X-CSRFToken` header.
5. **`send_file` with `as_attachment=False`** — Serves inline; user-uploaded HTML/SVG becomes stored XSS if not content-typed correctly.
6. **`@login_required` placement** — Must be the outermost decorator (closest to `@app.route`), otherwise bypassed.
7. **Session cookies** — Flask uses client-side signed cookies by default. Sensitive data in session is visible (base64) even if tamper-proof.

## Recommended Audit Order

1. `SECRET_KEY` hardcoded/weak → `debug=True` in prod
2. CSRF protection present (`flask-wtf`) → all state-changing routes covered
3. `Markup()` / `|safe` / `render_template_string` with user input
4. File serving (`send_file`, `send_from_directory`, `safe_join`)
5. SQL injection (`text()`, raw queries, string formatting in queries)
6. Auth decorator coverage (`@login_required` on all protected routes)
7. Cookie flags (`SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`)
8. Deployment config (debug off, proper WSGI server, no `app.run()` in prod)
