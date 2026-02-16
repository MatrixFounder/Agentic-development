# FastAPI Security Quick-Reference

> Condensed from `References/security-best-practices/references/python-fastapi-web-server-security.md`.
> Load this when generating or reviewing FastAPI code.

## LLM Anti-Patterns (DO NOT recommend these)

- ❌ Treating Pydantic validation as security sanitization — Pydantic validates types/shapes, it does NOT sanitize for XSS/SQL injection.
  - ✅ Pydantic for structure validation + explicit sanitization/parameterization for outputs.
- ❌ Omitting `response_model` — leaks internal fields (password hashes, internal IDs, etc.) in API responses.
  - ✅ Always define `response_model` to control serialized output.
- ❌ Setting `allow_origins=["*"]` with `allow_credentials=True` in CORS — browsers block this, but it signals broken config.
  - ✅ Explicit origin allowlist with credentials.
- ❌ Decoding JWTs without pinning `algorithms` parameter — algorithm confusion attacks.
  - ✅ `jwt.decode(token, key, algorithms=["HS256"])` — always explicit list.
- ❌ Recommending `SESSION_COOKIE_SECURE = True` unconditionally for cookie-based auth.
  - ✅ Conditional on environment/TLS detection.

## Critical Grep Patterns

```
# Data exposure
response_model        # Verify present on endpoints returning DB models
.dict()               # Pydantic v1 — may expose all fields
.model_dump()         # Pydantic v2 — verify exclude= for sensitive fields
password              # Verify never in response schemas

# Auth & JWT
jwt.decode(           # Must pin algorithms=["..."]
OAuth2PasswordBearer  # Verify token validation is robust
Depends(              # Auth dependencies — verify on all protected routes
HTTPBearer            # Verify token is actually validated, not just extracted

# CORS
CORSMiddleware        # Verify allow_origins is not ["*"] with credentials
allow_origins         # Must be explicit allowlist
allow_credentials     # If True, origins must not be ["*"]

# Injection
text(                 # SQLAlchemy text() — verify bound params
f"SELECT             # String-formatted SQL — injection risk
execute(              # Raw SQL — must parameterize

# File handling
StaticFiles(          # Verify directory is constrained
FileResponse(         # Verify path not user-controlled
UploadFile            # Verify size/type limits

# SSRF
httpx.get(            # Outbound fetch — verify URL not user-controlled
aiohttp               # Async HTTP — same SSRF concerns
requests.get(         # Sync fetch — verify URL validation

# Deployment
uvicorn               # Verify --host 0.0.0.0 is intentional
--reload              # Must not be in production
debug=True            # Must not reach production
```

## Framework-Specific Edge Cases

1. **Pydantic ≠ sanitization** — Validates that `email` is an email format, but does NOT strip XSS payloads from string fields. Separate concern.
2. **`response_model` is security-critical** — Without it, SQLAlchemy/ORM objects serialize ALL columns including `password_hash`, internal flags, etc.
3. **`Depends()` chain** — If auth dependency raises `HTTPException`, downstream dependencies don't run — but verify auth is first in the chain.
4. **Background tasks** — `BackgroundTasks` run after response. Secrets logged in background tasks still leak. Errors in background tasks are silent by default.
5. **`StaticFiles` path traversal** — Starlette's `StaticFiles` follows symlinks. Verify the served directory doesn't contain symlinks to sensitive locations.
6. **Async resource exhaustion** — Unbounded `asyncio.gather()` on user-controlled lists can exhaust memory/connections. Always limit concurrency.
7. **CORS + cookies** — FastAPI's CORS middleware doesn't handle CSRF. If using cookies for auth, add CSRF protection separately.
8. **Middleware ordering** — Middleware executes in reverse order of addition. Auth middleware must execute before route handlers.

## Recommended Audit Order

1. `response_model` present on all endpoints (data leakage prevention)
2. Auth dependencies (`Depends()`) on all protected routes
3. JWT validation: `algorithms` pinned, expiry checked, issuer verified
4. CORS configuration: origins explicit, credentials handled correctly
5. SQL injection: parameterized queries, no f-string SQL
6. File uploads: size limits, type validation, safe storage
7. SSRF: outbound HTTP with user-controlled URLs
8. Deployment: no `--reload`, no `debug=True`, proper ASGI server
