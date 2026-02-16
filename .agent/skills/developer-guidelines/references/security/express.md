# Express.js Security Quick-Reference

> Condensed from `References/security-best-practices/references/javascript-express-web-server-security.md`.
> Load this when generating or reviewing Express code.

## LLM Anti-Patterns (DO NOT recommend these)

- ❌ Using `app.use(helmet())` without understanding its defaults — Helmet ≥5 sets sensible defaults but may need tuning (CSP is not set by default in some versions).
  - ✅ Use `helmet()` AND verify CSP is explicitly configured for your app.
- ❌ Trusting `req.query` / `req.body` values as strings — Express parses `?foo[]=bar` as an array, `?foo[x]=1` as an object. Type coercion bugs → logic flaws.
  - ✅ Always validate/cast: `String(req.query.foo)` or use a validation library (Joi, Zod).
- ❌ Setting `trust proxy = true` globally without understanding implications — makes `req.ip`, `req.protocol`, `req.hostname` trust ALL proxies.
  - ✅ Set `trust proxy` to exact proxy count or IP range: `app.set('trust proxy', 1)`.
- ❌ Recommending `cookie.secure = true` unconditionally — breaks local HTTP dev.
  - ✅ Conditional: `secure: process.env.NODE_ENV === 'production'`
- ❌ Using `res.redirect(req.query.next)` without validation — open redirect.

## Critical Grep Patterns

```
# XSS / Template injection
res.send(             # If sending user input as HTML — XSS risk
innerHTML             # Client-side DOM XSS (if SSR context)
<%- (unescaped)       # EJS unescaped output — verify trusted source
!{                    # Pug unescaped — verify trusted source
{{{ (triple)          # Handlebars unescaped — verify trusted source

# Input validation
req.query             # Always validate types — may be object/array
req.params            # Path params — validate format
req.body              # Verify body parser limits and validation
express.json(         # Check { limit: '...' } is set
express.urlencoded(   # Check { limit: '...' , extended: false }

# Auth & Session
express-session       # Verify secret rotation, secure cookie flags
cookie.secure         # Must be conditional on environment
cookie.httpOnly       # Must be true for session cookies
cookie.sameSite       # Should be 'lax' or 'strict'
passport              # Verify session serialization is minimal

# CSRF
csurf                 # Deprecated — use csrf-csrf, lusca, or custom
csrf                  # Verify present on all state-changing routes

# File handling
express.static(       # Verify directory is constrained, no dotfiles
multer                # Verify limits: { fileSize, files, fieldSize }
res.sendFile(         # Verify path is not user-controlled
res.download(         # Verify path validation
path.join(            # Verify no user input in path construction

# Injection
child_process         # OS command injection risk
exec(                 # Shell execution — never with user input
spawn(                # Safer than exec, but validate args
eval(                 # Code injection — never with user input

# Deployment
NODE_ENV              # Must be 'production' in production
app.listen(           # Verify not exposed directly (use proxy)
```

## Framework-Specific Edge Cases

1. **`req.query` type coercion** — `?admin=true` gives string `"true"`, but `?items[]=a&items[]=b` gives array. `?obj[key]=val` gives object. Always validate.
2. **`trust proxy` settings** — `true` trusts all hops. Use numeric value (hop count) or specific subnet: `app.set('trust proxy', 'loopback')`.
3. **`express-session` secret** — Supports array for rotation: `secret: [newSecret, oldSecret]`. Old sessions remain valid until they expire.
4. **`express.static` dotfiles** — By default serves dotfiles. Set `dotfiles: 'deny'` to prevent `.env`, `.git` exposure.
5. **`multer` without limits** — Defaults allow unlimited file size. Always set `limits: { fileSize: N, files: M }`.
6. **`res.redirect()` status code** — Default is 302. For POST→GET, use 303. For permanent, use 301. Input validation on URL is critical regardless.
7. **Body parser `extended`** — `express.urlencoded({ extended: true })` uses `qs` library which allows nested objects. Use `extended: false` unless needed.
8. **Error handler signature** — Express error handlers MUST have 4 params `(err, req, res, next)`. Missing `next` makes Express treat it as regular middleware.

## Recommended Audit Order

1. Helmet.js presence and CSP configuration
2. `trust proxy` setting — verify matches actual deployment
3. Input validation on `req.query`/`req.body`/`req.params` (type coercion)
4. Session configuration: secret strength, cookie flags, store type
5. CSRF protection on all state-changing routes
6. File upload limits (`multer`) and static file serving (`express.static`)
7. Template engine unescaped outputs (`<%-`, `!{`, `{{{`)
8. `child_process` / `exec` usage with user input
9. Open redirect via `res.redirect()` with user-controlled URLs
10. Error handling: no stack traces in production, proper error middleware
